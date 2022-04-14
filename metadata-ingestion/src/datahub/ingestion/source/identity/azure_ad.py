import json
import logging
import re
import urllib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, Iterable, List

import click
import requests

from datahub.configuration import ConfigModel
from datahub.configuration.common import AllowDenyPattern
from datahub.emitter.mce_builder import make_group_urn, make_user_urn
from datahub.ingestion.api.common import PipelineContext
from datahub.ingestion.api.source import Source, SourceReport
from datahub.ingestion.api.workunit import MetadataWorkUnit
from datahub.metadata.com.linkedin.pegasus2avro.metadata.snapshot import (
    CorpGroupSnapshot,
    CorpUserSnapshot,
)
from datahub.metadata.com.linkedin.pegasus2avro.mxe import MetadataChangeEvent
from datahub.metadata.schema_classes import (
    CorpGroupInfoClass,
    CorpUserInfoClass,
    GroupMembershipClass,
)

logger = logging.getLogger(__name__)


class AzureADConfig(ConfigModel):
    """Config to create a token and connect to Azure AD instance"""

    # Required
    client_id: str
    tenant_id: str
    client_secret: str
    redirect: str
    authority: str
    token_url: str
    graph_url: str

    # Optional: Customize the mapping to DataHub Username from an attribute in the REST API response
    # Reference: https://docs.microsoft.com/en-us/graph/api/user-list?view=graph-rest-1.0&tabs=http#response-1
    azure_ad_response_to_username_attr: str = "userPrincipalName"
    azure_ad_response_to_username_regex: str = "(.*)"

    # Optional: Customize the mapping to DataHub Groupname from an attribute in the REST API response
    # Reference: https://docs.microsoft.com/en-us/graph/api/group-list?view=graph-rest-1.0&tabs=http#response-1
    azure_ad_response_to_groupname_attr: str = "displayName"
    azure_ad_response_to_groupname_regex: str = "(.*)"

    # Optional: to ingest users, groups or both
    ingest_users: bool = True
    ingest_groups: bool = True
    ingest_group_membership: bool = True

    ingest_groups_users: bool = True
    users_pattern: AllowDenyPattern = AllowDenyPattern.allow_all()
    groups_pattern: AllowDenyPattern = AllowDenyPattern.allow_all()

    # If enabled, report will contain names of filtered users and groups.
    filtered_tracking: bool = True


@dataclass
class AzureADSourceReport(SourceReport):
    filtered: List[str] = field(default_factory=list)
    filtered_tracking: bool = field(default=True, repr=False)
    filtered_count: int = field(default=0)

    def report_filtered(self, name: str) -> None:
        self.filtered_count += 1
        if self.filtered_tracking:
            self.filtered.append(name)


# Source that extracts Azure AD users, groups and group memberships using Microsoft Graph REST API


class AzureADSource(Source):
    """Ingest Azure AD Users and Groups into DataHub"""

    @classmethod
    def create(cls, config_dict, ctx):
        config = AzureADConfig.parse_obj(config_dict)
        return cls(config, ctx)

    def __init__(self, config: AzureADConfig, ctx: PipelineContext):
        super().__init__(ctx)
        self.config = config
        self.report = AzureADSourceReport(
            filtered_tracking=self.config.filtered_tracking
        )
        self.token_data = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "tenant_id": self.config.tenant_id,
            "client_secret": self.config.client_secret,
            "resource": "https://graph.microsoft.com",
            "scope": "https://graph.microsoft.com/.default",
        }
        self.token = self.get_token()
        self.selected_azure_ad_groups: list = []
        self.azure_ad_groups_users: list = []

    def get_token(self):
        token_response = requests.post(self.config.token_url, data=self.token_data)
        if token_response.status_code == 200:
            token = token_response.json().get("access_token")
            return token
        else:
            error_str = (
                f"Token response status code: {str(token_response.status_code)}. "
                f"Token response content: {str(token_response.content)}"
            )
            logger.error(error_str)
            self.report.report_failure("get_token", error_str)
            click.echo("Error: Token response invalid")
            exit()

    def get_workunits(self) -> Iterable[MetadataWorkUnit]:
        # for future developers: The actual logic of this ingestion wants to be executed, in order:
        # 1) the groups
        # 2) the groups' memberships
        # 3) the users

        # Create MetadataWorkUnits for CorpGroups
        if self.config.ingest_groups:
            # 1) the groups
            for azure_ad_groups in self._get_azure_ad_groups():
                logger.info("Processing another groups batch...")
                datahub_corp_group_snapshots = self._map_azure_ad_groups(
                    azure_ad_groups
                )
                for datahub_corp_group_snapshot in datahub_corp_group_snapshots:
                    mce = MetadataChangeEvent(
                        proposedSnapshot=datahub_corp_group_snapshot
                    )
                    wu = MetadataWorkUnit(id=datahub_corp_group_snapshot.urn, mce=mce)
                    self.report.report_workunit(wu)
                    yield wu

        # Populate GroupMembership Aspects for CorpUsers
        datahub_corp_user_urn_to_group_membership: Dict[
            str, GroupMembershipClass
        ] = defaultdict(lambda: GroupMembershipClass(groups=[]))
        if (
            self.config.ingest_group_membership
            and len(self.selected_azure_ad_groups) > 0
        ):
            # 2) the groups' membership
            for azure_ad_group in self.selected_azure_ad_groups:
                # Azure supports nested groups, but not DataHub.  We need to explode the nested groups into a flat list.
                datahub_corp_group_urn = self._map_azure_ad_group_to_urn(azure_ad_group)
                if not datahub_corp_group_urn:
                    error_str = f"Failed to extract DataHub Group Name from Azure AD Group named {azure_ad_group.get('displayName')}. Skipping..."
                    self.report.report_failure("azure_ad_group_mapping", error_str)
                    continue
                self._add_group_members_to_group_membership(
                    datahub_corp_group_urn,
                    azure_ad_group,
                    datahub_corp_user_urn_to_group_membership,
                )

        if (
            self.config.ingest_groups_users
            and self.config.ingest_group_membership
            and not self.config.ingest_users
        ):
            # 3) the users
            # getting infos about the users belonging to the found groups
            datahub_corp_user_snapshots = self._map_azure_ad_users(
                self.azure_ad_groups_users
            )
            yield from self.ingest_ad_users(
                datahub_corp_user_snapshots, datahub_corp_user_urn_to_group_membership
            )

        # Create MetadataWorkUnits for CorpUsers
        if self.config.ingest_users:
            # 3) the users
            for azure_ad_users in self._get_azure_ad_users():
                # azure_ad_users = next(self._get_azure_ad_users())
                datahub_corp_user_snapshots = self._map_azure_ad_users(azure_ad_users)
                yield from self.ingest_ad_users(
                    datahub_corp_user_snapshots,
                    datahub_corp_user_urn_to_group_membership,
                )

    def _add_group_members_to_group_membership(
        self,
        parent_corp_group_urn: str,
        azure_ad_group: dict,
        user_urn_to_group_membership: Dict[str, GroupMembershipClass],
    ) -> None:
        # Extract and map members for each group
        for azure_ad_group_members in self._get_azure_ad_group_members(azure_ad_group):
            # if group doesn't have any members, continue
            if not azure_ad_group_members:
                continue
            for azure_ad_member in azure_ad_group_members:
                odata_type = azure_ad_member.get("@odata.type")
                if odata_type == "#microsoft.graph.user":
                    self._add_user_to_group_membership(
                        parent_corp_group_urn,
                        azure_ad_member,
                        user_urn_to_group_membership,
                    )
                elif odata_type == "#microsoft.graph.group":
                    # Since DataHub does not support nested group, we add the members to the parent group and not the nested one.
                    self._add_group_members_to_group_membership(
                        parent_corp_group_urn,
                        azure_ad_member,
                        user_urn_to_group_membership,
                    )
                else:
                    raise ValueError(
                        f"Unsupported @odata.type '{odata_type}' found in Azure group member"
                    )

    def _add_user_to_group_membership(
        self,
        group_urn: str,
        azure_ad_user: dict,
        user_urn_to_group_membership: Dict[str, GroupMembershipClass],
    ) -> None:
        user_urn = self._map_azure_ad_user_to_urn(azure_ad_user)
        if not user_urn:
            error_str = f"Failed to extract DataHub Username from Azure ADUser {azure_ad_user.get('displayName')}. Skipping..."
            self.report.report_failure("azure_ad_user_mapping", error_str)
        else:
            self.azure_ad_groups_users.append(azure_ad_user)
            # update/create the GroupMembership aspect for this group member.
            if group_urn not in user_urn_to_group_membership[user_urn].groups:
                user_urn_to_group_membership[user_urn].groups.append(group_urn)

    def ingest_ad_users(
        self,
        datahub_corp_user_snapshots: Generator[CorpUserSnapshot, Any, None],
        datahub_corp_user_urn_to_group_membership: dict,
    ) -> Generator[MetadataWorkUnit, Any, None]:
        for datahub_corp_user_snapshot in datahub_corp_user_snapshots:
            # Add GroupMembership if applicable
            if (
                datahub_corp_user_snapshot.urn
                in datahub_corp_user_urn_to_group_membership.keys()
            ):
                datahub_group_membership = (
                    datahub_corp_user_urn_to_group_membership.get(
                        datahub_corp_user_snapshot.urn
                    )
                )
                assert datahub_group_membership
                datahub_corp_user_snapshot.aspects.append(datahub_group_membership)
            mce = MetadataChangeEvent(proposedSnapshot=datahub_corp_user_snapshot)
            wu = MetadataWorkUnit(id=datahub_corp_user_snapshot.urn, mce=mce)
            self.report.report_workunit(wu)
            yield wu

    def get_report(self) -> SourceReport:
        return self.report

    def close(self) -> None:
        pass

    def _get_azure_ad_groups(self) -> Iterable[List]:
        yield from self._get_azure_ad_data(kind="/groups")

    def _get_azure_ad_users(self) -> Iterable[List]:
        yield from self._get_azure_ad_data(kind="/users")

    def _get_azure_ad_group_members(self, azure_ad_group: dict) -> Iterable[List]:
        group_id = azure_ad_group.get("id")
        kind = f"/groups/{group_id}/members"
        yield from self._get_azure_ad_data(kind=kind)

    def _get_azure_ad_data(self, kind: str) -> Iterable[List]:
        headers = {"Authorization": "Bearer {}".format(self.token)}
        #           'ConsistencyLevel': 'eventual'}
        url = self.config.graph_url + kind
        while True:
            if not url:
                break
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                try:
                    url = json_data["@odata.nextLink"]
                except KeyError:
                    # no more data will follow
                    url = False  # type: ignore
                yield json_data["value"]
            else:
                error_str = (
                    f"Response status code: {str(response.status_code)}. "
                    f"Response content: {str(response.content)}"
                )
                logger.error(error_str)
                self.report.report_failure("_get_azure_ad_data_", error_str)
                continue

    def _map_identity_to_urn(self, func, id_to_extract, mapping_identifier, id_type):
        result, error_str = None, None
        try:
            result = func(id_to_extract)
        except Exception as e:
            error_str = "Failed to extract DataHub {} from Azure AD {} with name {} due to '{}'".format(
                id_type, id_type, id_to_extract.get("displayName"), repr(e)
            )
        if not result:
            error_str = "Failed to extract DataHub {} from Azure AD {} with name {} due to unknown reason".format(
                id_type, id_type, id_to_extract.get("displayName")
            )
        if error_str is not None:
            logger.error(error_str)
            self.report.report_failure(mapping_identifier, error_str)
        return result, error_str

    def _map_azure_ad_groups(self, azure_ad_groups):
        for azure_ad_group in azure_ad_groups:
            corp_group_urn, error_str = self._map_identity_to_urn(
                self._map_azure_ad_group_to_urn,
                azure_ad_group,
                "azure_ad_group_mapping",
                "group",
            )
            if error_str is not None:
                continue
            group_name = self._extract_regex_match_from_dict_value(
                azure_ad_group,
                self.config.azure_ad_response_to_groupname_attr,
                self.config.azure_ad_response_to_groupname_regex,
            )
            if not self.config.groups_pattern.allowed(group_name):
                self.report.report_filtered(f"{corp_group_urn}")
                continue
            self.selected_azure_ad_groups.append(azure_ad_group)
            corp_group_snapshot = CorpGroupSnapshot(
                urn=corp_group_urn,
                aspects=[],
            )
            corp_group_info = self._map_azure_ad_group_to_corp_group(azure_ad_group)
            corp_group_snapshot.aspects.append(corp_group_info)
            yield corp_group_snapshot

    # Converts Azure group profile into DataHub CorpGroupInfoClass Aspect
    def _map_azure_ad_group_to_corp_group(self, group):
        return CorpGroupInfoClass(
            displayName=self._map_azure_ad_group_to_group_name(group),
            description=group.get("description"),
            email=group.get("mail"),
            members=[],
            groups=[],
            admins=[],
        )

    # Creates Datahub CorpGroup Urn from Azure AD Group object
    def _map_azure_ad_group_to_urn(self, azure_ad_group):
        group_name = self._map_azure_ad_group_to_group_name(azure_ad_group)
        if not group_name:
            return None
        # decode the group name to deal with URL encoding, and replace spaces with '_'
        url_encoded_group_name = urllib.parse.quote(group_name)
        return make_group_urn(url_encoded_group_name)

    def _map_azure_ad_group_to_group_name(self, azure_ad_group):
        return self._extract_regex_match_from_dict_value(
            azure_ad_group,
            self.config.azure_ad_response_to_groupname_attr,
            self.config.azure_ad_response_to_groupname_regex,
        )

    def _map_azure_ad_users(self, azure_ad_users):
        for user in azure_ad_users:
            corp_user_urn, error_str = self._map_identity_to_urn(
                self._map_azure_ad_user_to_urn, user, "azure_ad_user_mapping", "user"
            )
            if error_str is not None:
                continue
            if not self.config.users_pattern.allowed(corp_user_urn):
                self.report.report_filtered(f"{corp_user_urn}.*")
                continue
            corp_user_snapshot = CorpUserSnapshot(
                urn=corp_user_urn,
                aspects=[],
            )
            corp_user_info = self._map_azure_ad_user_to_corp_user(user)
            corp_user_snapshot.aspects.append(corp_user_info)
            yield corp_user_snapshot

    def _map_azure_ad_user_to_user_name(self, azure_ad_user):
        return self._extract_regex_match_from_dict_value(
            azure_ad_user,
            self.config.azure_ad_response_to_username_attr,
            self.config.azure_ad_response_to_username_regex,
        )

    # Creates DataHub CorpUser Urn from Azure AD User object
    def _map_azure_ad_user_to_urn(self, azure_ad_user):
        user_name = self._map_azure_ad_user_to_user_name(azure_ad_user)
        if not user_name:
            return None
        return make_user_urn(user_name)

    def _map_azure_ad_user_to_corp_user(self, azure_ad_user):
        full_name = (
            str(azure_ad_user.get("givenName", ""))
            + " "
            + str(azure_ad_user.get("surname", ""))
        )
        return CorpUserInfoClass(
            active=True,
            displayName=azure_ad_user.get("displayName", full_name),
            firstName=azure_ad_user.get("givenName", None),
            lastName=azure_ad_user.get("surname", None),
            fullName=full_name,
            email=azure_ad_user.get("mail"),
            title=azure_ad_user.get("jobTitle", None),
            countryCode=azure_ad_user.get("mobilePhone", None),
        )

    def _extract_regex_match_from_dict_value(
        self, str_dict: Dict[str, str], key: str, pattern: str
    ) -> str:
        raw_value = str_dict.get(key)
        if raw_value is None:
            raise ValueError(f"Unable to find the key {key} in Group. Is it wrong?")
        match = re.search(pattern, raw_value)
        if match is None:
            raise ValueError(
                f"Unable to extract a name from {raw_value} with the pattern {pattern}"
            )
        return match.group()
