import json
from datahub.ingestion.source.thrift import ThriftSource

from freezegun import freeze_time

from datahub.ingestion.api.common import PipelineContext
from tests.test_helpers import mce_helpers

FROZEN_TIME = "2020-04-14 07:00:00"


@freeze_time(FROZEN_TIME)
def test_thrift(
    tmp_path,
    pytestconfig,
):

    source = ThriftSource.create(
        {"filename": "./examples/thrift_files/example.thrift"}, PipelineContext(run_id="test_run_id")
    )

    mce_objects = [wu.metadata.to_obj() for wu in source.get_workunits()]

    with open(str(tmp_path / "thrift_mces.json"), "w") as f:
        json.dump(mce_objects, f, indent=2)

    # Verify the output.
    test_resources_dir = pytestconfig.rootpath / "tests/unit/thrift"
    mce_helpers.check_golden_file(
        pytestconfig,
        output_path=tmp_path / "thrift_mces.json",
        golden_path=test_resources_dir / "thrift_mces_golden.json",
    )
