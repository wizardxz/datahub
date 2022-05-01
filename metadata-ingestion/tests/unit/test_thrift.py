import json

from freezegun import freeze_time

from datahub.ingestion.api.common import PipelineContext
from datahub.ingestion.source.thrift import ThriftSource
from tests.test_helpers import mce_helpers

FROZEN_TIME = "2020-04-14 07:00:00"


@freeze_time(FROZEN_TIME)
def test_thrift(
    tmp_path,
    pytestconfig,
):
    for input_file, actual_output_file, golden_file in [
        (
            "./examples/thrift_files/example.thrift",
            "thrift_mcps.json",
            "thrift_mcps_golden.json",
        ),
        (
            "./examples/thrift_files/compositetypes.thrift",
            "thrift_mcps_compositetypes.json",
            "thrift_mcps_compositetypes_golden.json",
        ),
    ]:
        source = ThriftSource.create(
            {"filename": input_file},
            PipelineContext(run_id="test_run_id"),
        )
        mcp_objects = [wu.metadata.to_obj() for wu in source.get_workunits()]

        with open(str(tmp_path / actual_output_file), "w") as f:
            json.dump(mcp_objects, f, indent=2)

        # Verify the output.
        test_resources_dir = pytestconfig.rootpath / "tests/unit/thrift"
        mce_helpers.check_golden_file(
            pytestconfig,
            output_path=tmp_path / actual_output_file,
            golden_path=test_resources_dir / golden_file,
        )
