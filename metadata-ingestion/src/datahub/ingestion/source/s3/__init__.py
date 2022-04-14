import dataclasses
import logging
import os
import re
from collections import OrderedDict
from datetime import datetime
from math import log10
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pydeequ
from pydeequ.analyzers import AnalyzerContext
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import (
    ArrayType,
    BinaryType,
    BooleanType,
    ByteType,
    DateType,
    DecimalType,
    DoubleType,
    FloatType,
    IntegerType,
    LongType,
    MapType,
    NullType,
    ShortType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)
from pyspark.sql.utils import AnalysisException
from smart_open import open as smart_open

from datahub.emitter.mce_builder import (
    make_data_platform_urn,
    make_dataset_urn_with_platform_instance,
)
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.mcp_builder import (
    FolderKey,
    KeyType,
    PlatformKey,
    S3BucketKey,
    add_dataset_to_container,
    gen_containers,
)
from datahub.ingestion.api.common import PipelineContext
from datahub.ingestion.api.source import Source, SourceReport
from datahub.ingestion.api.workunit import MetadataWorkUnit
from datahub.ingestion.source.aws.s3_util import (
    get_bucket_name,
    get_bucket_relative_path,
    strip_s3_prefix,
)
from datahub.ingestion.source.s3.config import DataLakeSourceConfig
from datahub.ingestion.source.s3.profiling import _SingleTableProfiler
from datahub.ingestion.source.s3.report import DataLakeSourceReport
from datahub.ingestion.source.schema_inference import avro, csv_tsv, json, parquet
from datahub.ingestion.transformer.add_dataset_browse_path import (
    AddDatasetBrowsePathConfig,
    AddDatasetBrowsePathTransformer,
)
from datahub.metadata.com.linkedin.pegasus2avro.metadata.snapshot import DatasetSnapshot
from datahub.metadata.com.linkedin.pegasus2avro.mxe import MetadataChangeEvent
from datahub.metadata.com.linkedin.pegasus2avro.schema import (
    BooleanTypeClass,
    BytesTypeClass,
    DateTypeClass,
    NullTypeClass,
    NumberTypeClass,
    RecordTypeClass,
    SchemaFieldDataType,
    SchemaMetadata,
    StringTypeClass,
    TimeTypeClass,
)
from datahub.metadata.schema_classes import (
    ChangeTypeClass,
    DatasetPropertiesClass,
    MapTypeClass,
    OtherSchemaClass,
)
from datahub.telemetry import stats, telemetry
from datahub.utilities.perf_timer import PerfTimer

# hide annoying debug errors from py4j
logging.getLogger("py4j").setLevel(logging.ERROR)
logger: logging.Logger = logging.getLogger(__name__)

# for a list of all types, see https://spark.apache.org/docs/3.0.3/api/python/_modules/pyspark/sql/types.html
_field_type_mapping = {
    NullType: NullTypeClass,
    StringType: StringTypeClass,
    BinaryType: BytesTypeClass,
    BooleanType: BooleanTypeClass,
    DateType: DateTypeClass,
    TimestampType: TimeTypeClass,
    DecimalType: NumberTypeClass,
    DoubleType: NumberTypeClass,
    FloatType: NumberTypeClass,
    ByteType: BytesTypeClass,
    IntegerType: NumberTypeClass,
    LongType: NumberTypeClass,
    ShortType: NumberTypeClass,
    ArrayType: NullTypeClass,
    MapType: MapTypeClass,
    StructField: RecordTypeClass,
    StructType: RecordTypeClass,
}


def get_column_type(
    report: SourceReport, dataset_name: str, column_type: str
) -> SchemaFieldDataType:
    """
    Maps known Spark types to datahub types
    """
    TypeClass: Any = None

    for field_type, type_class in _field_type_mapping.items():
        if isinstance(column_type, field_type):
            TypeClass = type_class
            break

    # if still not found, report the warning
    if TypeClass is None:
        report.report_warning(
            dataset_name, f"unable to map type {column_type} to metadata schema"
        )
        TypeClass = NullTypeClass

    return SchemaFieldDataType(type=TypeClass())


# config flags to emit telemetry for
config_options_to_report = [
    "platform",
    "use_relative_path",
    "ignore_dotfiles",
]

# profiling flags to emit telemetry for
profiling_flags_to_report = [
    "profile_table_level_only",
    "include_field_null_count",
    "include_field_min_value",
    "include_field_max_value",
    "include_field_mean_value",
    "include_field_median_value",
    "include_field_stddev_value",
    "include_field_quantiles",
    "include_field_distinct_value_frequencies",
    "include_field_histogram",
    "include_field_sample_values",
]

S3_PREFIXES = ("s3://", "s3n://", "s3a://")


# LOCAL_BROWSE_PATH_TRANSFORMER_CONFIG = AddDatasetBrowsePathConfig(
#     path_templates=["/ENV/PLATFORMDATASET_PARTS"], replace_existing=True
# )
#
# LOCAL_BROWSE_PATH_TRANSFORMER = AddDatasetBrowsePathTransformer(
#     ctx=None, config=LOCAL_BROWSE_PATH_TRANSFORMER_CONFIG
# )


@dataclasses.dataclass
class TableData:
    disaply_name: str
    is_s3: bool
    full_path: str
    partitions: Optional[OrderedDict]
    timestamp: datetime
    table_path: str


class S3Source(Source):
    source_config: DataLakeSourceConfig
    report: DataLakeSourceReport
    profiling_times_taken: List[float]
    processed_containers: List[str]

    def __init__(self, config: DataLakeSourceConfig, ctx: PipelineContext):
        super().__init__(ctx)
        self.source_config = config
        self.report = DataLakeSourceReport()
        self.profiling_times_taken = []

        config_report = {
            config_option: config.dict().get(config_option)
            for config_option in config_options_to_report
        }
        config_report = {**config_report, "profiling_enabled": config.profiling.enabled}

        telemetry.telemetry_instance.ping(
            "data_lake_config",
            config_report,
        )

        if config.profiling.enabled:
            telemetry.telemetry_instance.ping(
                "data_lake_profiling_config",
                {
                    config_flag: config.profiling.dict().get(config_flag)
                    for config_flag in profiling_flags_to_report
                },
            )
            self.init_spark()

    def init_spark(self):

        conf = SparkConf()

        conf.set(
            "spark.jars.packages",
            ",".join(
                [
                    "org.apache.hadoop:hadoop-aws:3.0.3",
                    "org.apache.spark:spark-avro_2.12:3.0.3",
                    pydeequ.deequ_maven_coord,
                ]
            ),
        )

        if self.source_config.aws_config is not None:

            aws_access_key_id = self.source_config.aws_config.aws_access_key_id
            aws_secret_access_key = self.source_config.aws_config.aws_secret_access_key
            aws_session_token = self.source_config.aws_config.aws_session_token

            aws_provided_credentials = [
                aws_access_key_id,
                aws_secret_access_key,
                aws_session_token,
            ]

            if any(x is not None for x in aws_provided_credentials):

                # see https://hadoop.apache.org/docs/r3.0.3/hadoop-aws/tools/hadoop-aws/index.html#Changing_Authentication_Providers
                if all(x is not None for x in aws_provided_credentials):
                    conf.set(
                        "spark.hadoop.fs.s3a.aws.credentials.provider",
                        "org.apache.hadoop.fs.s3a.TemporaryAWSCredentialsProvider",
                    )

                else:
                    conf.set(
                        "spark.hadoop.fs.s3a.aws.credentials.provider",
                        "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
                    )

                if aws_access_key_id is not None:
                    conf.set("spark.hadoop.fs.s3a.access.key", aws_access_key_id)
                if aws_secret_access_key is not None:
                    conf.set(
                        "spark.hadoop.fs.s3a.secret.key",
                        aws_secret_access_key,
                    )
                if aws_session_token is not None:
                    conf.set(
                        "spark.hadoop.fs.s3a.session.token",
                        aws_session_token,
                    )
            else:
                # if no explicit AWS config is provided, use a default AWS credentials provider
                conf.set(
                    "spark.hadoop.fs.s3a.aws.credentials.provider",
                    "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider",
                )

        conf.set("spark.jars.excludes", pydeequ.f2j_maven_coord)
        conf.set("spark.driver.memory", self.source_config.spark_driver_memory)

        self.spark = SparkSession.builder.config(conf=conf).getOrCreate()

    @classmethod
    def create(cls, config_dict, ctx):
        config = DataLakeSourceConfig.parse_obj(config_dict)

        return cls(config, ctx)

    def read_file_spark(self, file: str, ext: str) -> Optional[DataFrame]:

        logger.debug(f"Opening file {file} for profiling in spark")
        file = file.replace("s3://", "s3a://")

        telemetry.telemetry_instance.ping("data_lake_file", {"extension": ext})

        if ext.endswith(".parquet"):
            df = self.spark.read.parquet(file)
        elif ext.endswith(".csv"):
            # see https://sparkbyexamples.com/pyspark/pyspark-read-csv-file-into-dataframe
            df = self.spark.read.csv(
                file,
                header="True",
                inferSchema="True",
                sep=",",
                ignoreLeadingWhiteSpace=True,
                ignoreTrailingWhiteSpace=True,
            )
        elif ext.endswith(".tsv"):
            df = self.spark.read.csv(
                file,
                header="True",
                inferSchema="True",
                sep="\t",
                ignoreLeadingWhiteSpace=True,
                ignoreTrailingWhiteSpace=True,
            )
        elif ext.endswith(".json"):
            df = self.spark.read.json(file)
        elif ext.endswith(".avro"):
            try:
                df = self.spark.read.format("avro").load(file)
            except AnalysisException:
                self.report.report_warning(
                    file,
                    "To ingest avro files, please install the spark-avro package: https://mvnrepository.com/artifact/org.apache.spark/spark-avro_2.12/3.0.3",
                )
                return None

        # TODO: add support for more file types
        # elif file.endswith(".orc"):
        # df = self.spark.read.orc(file)
        else:
            self.report.report_warning(file, f"file {file} has unsupported extension")
            return None
        logger.debug(f"dataframe read for file {file} with row count {df.count()}")
        # replace periods in names because they break PyDeequ
        # see https://mungingdata.com/pyspark/avoid-dots-periods-column-names/
        return df.toDF(*(c.replace(".", "_") for c in df.columns))

    def create_emit_containers(
        self,
        container_key: KeyType,
        name: str,
        sub_types: List[str],
        parent_container_key: Optional[PlatformKey] = None,
        domain_urn: Optional[str] = None,
    ) -> Iterable[MetadataWorkUnit]:
        if container_key.guid() not in self.processed_containers:
            container_wus = gen_containers(
                container_key=container_key,
                name=name,
                sub_types=sub_types,
                parent_container_key=parent_container_key,
                domain_urn=domain_urn,
            )
            self.processed_containers.append(container_key.guid())
            logger.debug(f"Creating container with key: {container_key}")
            for wu in container_wus:
                self.report.report_workunit(wu)
                yield wu

    def create_container_hierarchy(
        self, table_data: TableData, dataset_urn: str
    ) -> Iterable[MetadataWorkUnit]:
        logger.debug(f"Creating containers for {dataset_urn}")
        base_full_path = table_data.table_path
        parent_key = None
        if table_data.is_s3:
            bucket_name = get_bucket_name(table_data.full_path)
            bucket_key = self.gen_bucket_key(bucket_name)
            yield from self.create_emit_containers(
                container_key=bucket_key,
                name=bucket_name,
                sub_types=["S3 bucket"],
                parent_container_key=None,
            )
            parent_key = bucket_key
            base_full_path = get_bucket_relative_path(table_data.table_path)

        for folder in base_full_path[: base_full_path.rfind("/")].split("/"):
            abs_path = folder
            if parent_key:
                if isinstance(parent_key, S3BucketKey):
                    prefix = parent_key.bucket_name
                elif isinstance(parent_key, FolderKey):
                    prefix = parent_key.folder_abs_path
                abs_path = prefix + "/" + folder
            folder_key = self.gen_folder_key(abs_path)
            yield from self.create_emit_containers(
                container_key=folder_key,
                name=folder,
                sub_types=["Folder"],
                parent_container_key=parent_key,
            )
            parent_key = folder_key
        if parent_key is None:
            logger.warning(
                f"Failed to associate Dataset ({dataset_urn}) with container"
            )
            return
        yield from add_dataset_to_container(parent_key, dataset_urn)

    def get_fields(self, table_data: TableData) -> List:
        if table_data.is_s3:
            if self.source_config.aws_config is None:
                raise ValueError("AWS config is required for S3 file sources")

            s3_client = self.source_config.aws_config.get_s3_client()

            file = smart_open(
                table_data.full_path, "rb", transport_params={"client": s3_client}
            )
        else:

            file = open(table_data.full_path, "rb")

        fields = []

        try:
            if table_data.full_path.endswith(".parquet"):
                fields = parquet.ParquetInferrer().infer_schema(file)
            elif table_data.full_path.endswith(".csv"):
                fields = csv_tsv.CsvInferrer(
                    max_rows=self.source_config.max_rows
                ).infer_schema(file)
            elif table_data.full_path.endswith(".tsv"):
                fields = csv_tsv.TsvInferrer(
                    max_rows=self.source_config.max_rows
                ).infer_schema(file)
            elif table_data.full_path.endswith(".json"):
                fields = json.JsonInferrer().infer_schema(file)
            elif table_data.full_path.endswith(".avro"):
                fields = avro.AvroInferrer().infer_schema(file)
            else:
                self.report.report_warning(
                    table_data.full_path,
                    f"file {table_data.full_path} has unsupported extension",
                )
            file.close()
        except Exception as e:
            self.report.report_warning(
                table_data.full_path,
                f"could not infer schema for file {table_data.full_path}: {e}",
            )
            file.close()
        logger.debug(f"Extracted fields in schema: {fields}")
        fields = sorted(fields, key=lambda f: f.fieldPath)

        return fields

    def get_table_profile(
        self, table_data: TableData, dataset_urn: str
    ) -> Iterable[MetadataWorkUnit]:
        # read in the whole table with Spark for profiling
        table = self.read_file_spark(
            table_data.table_path, os.path.splitext(table_data.full_path)[1]
        )

        # if table is not readable, skip
        if table is None:
            self.report.report_warning(
                table_data.disaply_name,
                f"unable to read table {table_data.disaply_name} from file {table_data.full_path}",
            )
            return

        with PerfTimer() as timer:
            # init PySpark analysis object
            logger.debug(
                f"Profiling {table_data.full_path}: reading file and computing nulls+uniqueness {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
            table_profiler = _SingleTableProfiler(
                table,
                self.spark,
                self.source_config.profiling,
                self.report,
                table_data.full_path,
            )

            logger.debug(
                f"Profiling {table_data.full_path}: preparing profilers to run {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
            # instead of computing each profile individually, we run them all in a single analyzer.run() call
            # we use a single call because the analyzer optimizes the number of calls to the underlying profiler
            # since multiple profiles reuse computations, this saves a lot of time
            table_profiler.prepare_table_profiles()

            # compute the profiles
            logger.debug(
                f"Profiling {table_data.full_path}: computing profiles {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
            analysis_result = table_profiler.analyzer.run()
            analysis_metrics = AnalyzerContext.successMetricsAsDataFrame(
                self.spark, analysis_result
            )

            logger.debug(
                f"Profiling {table_data.full_path}: extracting profiles {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
            table_profiler.extract_table_profiles(analysis_metrics)

            time_taken = timer.elapsed_seconds()

            logger.info(
                f"Finished profiling {table_data.full_path}; took {time_taken:.3f} seconds"
            )

            self.profiling_times_taken.append(time_taken)

        mcp = MetadataChangeProposalWrapper(
            entityType="dataset",
            entityUrn=dataset_urn,
            changeType=ChangeTypeClass.UPSERT,
            aspectName="datasetProfile",
            aspect=table_profiler.profile,
        )
        wu = MetadataWorkUnit(
            id=f"profile-{self.source_config.platform}-{table_data.table_path}", mcp=mcp
        )
        self.report.report_workunit(wu)
        yield wu

    def ingest_table(self, table_data: TableData) -> Iterable[MetadataWorkUnit]:

        logger.info(f"Extracting table schema from file: {table_data.full_path}")
        browse_path: str = (
            strip_s3_prefix(table_data.table_path)
            if table_data.is_s3
            else table_data.table_path.strip("/")
        )

        data_platform_urn = make_data_platform_urn(self.source_config.platform)
        logger.info(f"Creating dataset urn with name: {browse_path}")
        dataset_urn = make_dataset_urn_with_platform_instance(
            self.source_config.platform,
            browse_path,
            self.source_config.platform_instance,
            self.source_config.env,
        )

        dataset_snapshot = DatasetSnapshot(
            urn=dataset_urn,
            aspects=[],
        )

        dataset_properties = DatasetPropertiesClass(
            description="",
            name=table_data.disaply_name,
            customProperties={},
        )
        dataset_snapshot.aspects.append(dataset_properties)

        fields = self.get_fields(table_data)
        schema_metadata = SchemaMetadata(
            schemaName=table_data.disaply_name,
            platform=data_platform_urn,
            version=0,
            hash="",
            fields=fields,
            platformSchema=OtherSchemaClass(rawSchema=""),
        )
        dataset_snapshot.aspects.append(schema_metadata)

        mce = MetadataChangeEvent(proposedSnapshot=dataset_snapshot)
        wu = MetadataWorkUnit(id=table_data.table_path, mce=mce)
        self.report.report_workunit(wu)
        yield wu

        yield from self.create_container_hierarchy(table_data, dataset_urn)

        if self.source_config.profiling.enabled:
            yield from self.get_table_profile(table_data, dataset_urn)

    def gen_bucket_key(self, name):
        return S3BucketKey(
            platform="s3",
            instance=self.source_config.env
            if self.source_config.platform_instance is None
            else self.source_config.platform_instance,
            bucket_name=name,
        )

    def gen_folder_key(self, abs_path):
        return FolderKey(
            platform=self.source_config.platform,
            instance=self.source_config.env
            if self.source_config.platform_instance is None
            else self.source_config.platform_instance,
            folder_abs_path=abs_path,
        )

    def get_prefix(self, relative_path: str) -> str:
        index = re.search("[\*|\{]", relative_path)  # noqa: W605
        if index:
            return relative_path[: index.start()]
        else:
            return relative_path

    def extract_table_name(self, named_vars: dict) -> str:
        if self.source_config.path_spec.table_name is None:
            raise ValueError("path_spec.table_name is not set")
        return self.source_config.path_spec.table_name.format_map(named_vars)

    def extract_table_data(self, path: str, timestamp: datetime) -> TableData:

        logger.debug(f"Getting table data for path: {path}")
        parsed_vars = self.source_config.path_spec.get_named_vars(path)
        table_data = None
        if parsed_vars is None or "table" not in parsed_vars.named:
            table_data = TableData(
                disaply_name=os.path.basename(path),
                is_s3=self.source_config.path_spec.is_s3(),
                full_path=path,
                partitions=None,
                timestamp=timestamp,
                table_path=path,
            )
        else:
            include = self.source_config.path_spec.include
            depth = include.count("/", 0, include.find("{table}"))
            table_path = (
                "/".join(path.split("/")[:depth]) + "/" + parsed_vars.named["table"]
            )
            table_data = TableData(
                disaply_name=self.extract_table_name(parsed_vars.named),
                is_s3=self.source_config.path_spec.is_s3(),
                full_path=path,
                partitions=None,
                timestamp=timestamp,
                table_path=table_path,
            )
        return table_data

    def s3_browser(self) -> Iterable[tuple]:
        if self.source_config.aws_config is None:
            raise ValueError("aws_config not set. Cannot browse s3")
        s3 = self.source_config.aws_config.get_s3_resource()
        bucket_name = get_bucket_name(self.source_config.path_spec.include)
        logger.debug(f"Scanning bucket : {bucket_name}")
        bucket = s3.Bucket(bucket_name)
        prefix = self.get_prefix(
            get_bucket_relative_path(self.source_config.path_spec.include)
        )
        logger.debug(f"Scanning objects with prefix:{prefix}")
        for obj in bucket.objects.filter(Prefix=prefix).page_size(1000):
            s3_path = f"s3://{obj.bucket_name}/{obj.key}"
            yield s3_path, obj.last_modified

    def local_browser(self) -> Iterable[tuple]:
        prefix = self.get_prefix(self.source_config.path_spec.include)
        if os.path.isfile(prefix):
            logger.debug(f"Scanning single local file: {prefix}")
            yield prefix, os.path.getmtime(prefix)
        else:
            logger.debug(f"Scanning files under local folder: {prefix}")
            for root, dirs, files in os.walk(prefix):
                for file in sorted(files):
                    full_path = os.path.join(root, file)
                    yield full_path, os.path.getmtime(full_path)

    def get_workunits(self) -> Iterable[MetadataWorkUnit]:
        self.processed_containers = []
        with PerfTimer() as timer:

            file_browser = (
                self.s3_browser()
                if self.source_config.path_spec.is_s3()
                else self.local_browser()
            )
            table_dict: Dict[str, TableData] = {}
            for file, timestamp in file_browser:
                if not self.source_config.path_spec.allowed(file):
                    continue
                table_data = self.extract_table_data(file, timestamp)
                d_table_data = table_dict.setdefault(table_data.table_path, table_data)
                if d_table_data.timestamp < table_data.timestamp:
                    table_dict[table_data.table_path] = table_data
            for guid, table_data in table_dict.items():
                yield from self.ingest_table(table_data)

            if not self.source_config.profiling.enabled:
                return

            total_time_taken = timer.elapsed_seconds()

            logger.info(
                f"Profiling {len(self.profiling_times_taken)} table(s) finished in {total_time_taken:.3f} seconds"
            )

            time_percentiles: Dict[str, float] = {}

            if len(self.profiling_times_taken) > 0:
                percentiles = [50, 75, 95, 99]
                percentile_values = stats.calculate_percentiles(
                    self.profiling_times_taken, percentiles
                )

                time_percentiles = {
                    f"table_time_taken_p{percentile}": 10
                    ** int(log10(percentile_values[percentile] + 1))
                    for percentile in percentiles
                }

            telemetry.telemetry_instance.ping(
                "data_lake_profiling_summary",
                # bucket by taking floor of log of time taken
                {
                    "total_time_taken": 10 ** int(log10(total_time_taken + 1)),
                    "count": 10 ** int(log10(len(self.profiling_times_taken) + 1)),
                    "platform": self.source_config.platform,
                    **time_percentiles,
                },
            )

    def get_report(self):
        return self.report

    def close(self):
        pass
