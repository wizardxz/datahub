import json
import pathlib
from typing import Callable, Dict, List, Tuple

from _pytest.config import Config
from freezegun import freeze_time

from datahub.ingestion.api.common import PipelineContext
from datahub.ingestion.source.thrift.thrift import ThriftSource
from tests.test_helpers import mce_helpers

FROZEN_TIME = "2020-04-14 07:00:00"


def check_golden_file(
    input_file: str, actual_output_file: str, golden_file: str
) -> Callable[[Callable[[List[dict]], None]], Callable[[pathlib.Path, Config], None]]:
    def decorator(
        func: Callable[[List[dict]], None]
    ) -> Callable[[pathlib.Path, Config], None]:
        @freeze_time(FROZEN_TIME)
        def wrapper(tmp_path: pathlib.Path, pytestconfig: Config) -> None:
            source = ThriftSource.create(
                {"filename": input_file},
                PipelineContext(run_id="test_run_id"),
            )
            mcp_objects = [wu.metadata.to_obj() for wu in source.get_workunits()]

            with open(str(tmp_path / actual_output_file), "w") as f:
                json.dump(mcp_objects, f, indent=2)

            # Verify the output.
            test_resources_dir = pytestconfig.rootpath / "tests/unit"
            mce_helpers.check_golden_file(
                pytestconfig,
                output_path=tmp_path / actual_output_file,
                golden_path=test_resources_dir / golden_file,
            )
            func(mcp_objects)

        return wrapper

    return decorator


@check_golden_file(
    "./tests/unit/thrift_files/primitive_types.thrift",
    "primitive_types.json",
    "./thrift_golden/primitive_types_golden.json",
)
def test_primitive(mcp_objects: List[dict]) -> None:
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    aspect = json.loads(obj["aspect"]["value"])
    fields = aspect["fields"]
    assert len(fields) == 7
    expecteds = [
        (
            1,
            "boolValue",
            {"type": {"com.linkedin.schema.BooleanType": {}}},
            "bool",
            [{"com.linkedin.schema.HyperTypeTextToken": {"text": "bool"}}],
        ),
        (
            2,
            "byteValue",
            {"type": {"com.linkedin.schema.NumberType": {}}},
            "byte",
            [{"com.linkedin.schema.HyperTypeTextToken": {"text": "byte"}}],
        ),
        (
            3,
            "i16Value",
            {"type": {"com.linkedin.schema.NumberType": {}}},
            "i16",
            [{"com.linkedin.schema.HyperTypeTextToken": {"text": "i16"}}],
        ),
        (
            4,
            "i32Value",
            {"type": {"com.linkedin.schema.NumberType": {}}},
            "i32",
            [{"com.linkedin.schema.HyperTypeTextToken": {"text": "i32"}}],
        ),
        (
            5,
            "i64Value",
            {"type": {"com.linkedin.schema.NumberType": {}}},
            "i64",
            [{"com.linkedin.schema.HyperTypeTextToken": {"text": "i64"}}],
        ),
        (
            6,
            "doubleValue",
            {"type": {"com.linkedin.schema.NumberType": {}}},
            "double",
            [{"com.linkedin.schema.HyperTypeTextToken": {"text": "double"}}],
        ),
        (
            7,
            "stringValue",
            {"type": {"com.linkedin.schema.StringType": {}}},
            "string",
            [{"com.linkedin.schema.HyperTypeTextToken": {"text": "string"}}],
        ),
    ]  # type: List[Tuple[int, str, Dict[str, Dict[str, Dict[str, str]]], str, List[Dict[str, Dict[str, str]]]]]
    for field, expected in zip(
        fields,
        expecteds,
    ):
        index, name, type_, native_type, hyper_type = expected
        assert field["fieldPath"] == name
        assert field["type"] == type_
        assert field["nativeDataType"] == native_type
