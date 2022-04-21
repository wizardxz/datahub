from __future__ import annotations
import json
from typing import Callable, List

from freezegun import freeze_time

from datahub.ingestion.api.common import PipelineContext
from datahub.ingestion.source.thrift import ThriftSource
from tests.test_helpers import mce_helpers

FROZEN_TIME = "2020-04-14 07:00:00"


def check_golden_file(
    input_file: str, actual_output_file: str, golden_file: str
) -> bool:
    def decorator(func: Callable[[List[dict]], None]):
        @freeze_time(FROZEN_TIME)
        def wrapper(tmp_path, pytestconfig):
            source = ThriftSource.create(
                {"filename": input_file},
                PipelineContext(run_id="test_run_id"),
            )
            mcp_objects = [wu.metadata.to_obj() for wu in source.get_workunits()]

            with open(str(tmp_path / actual_output_file), "w") as f:
                json.dump(mcp_objects, f, indent=2)

            # Verify the output.
            test_resources_dir = pytestconfig.rootpath / "tests/unit/thrift_golden"
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
    "primitive_types_golden.json",
)
def test_primitive(mcp_objects: List[dict]):
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    aspect = json.loads(obj["aspect"]["value"])
    thrift_schema = aspect["platformSchema"]["com.linkedin.schema.ThriftSchema"]
    fields = aspect["fields"]
    tfs = thrift_schema["fields"]
    assert len(fields) == len(tfs) == 7
    expected = [
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
    ]
    for field, tf, expected in zip(
        fields,
        tfs,
        expected,
    ):
        index, name, type_, native_type, hyper_type = expected
        assert field["fieldPath"] == tf["name"] == name
        assert field["type"] == type_
        assert field["nativeDataType"] == native_type
        assert tf["index"] == index
        assert tf["hyperType"] == hyper_type


@check_golden_file(
    "./tests/unit/thrift_files/namespace_star.thrift",
    "namespace_star.json",
    "namespace_star_golden.json",
)
def test_namespace_star(mcp_objects: List[dict]):
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    assert (
        obj["entityUrn"]
        == "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.Foo1,PROD)"
    )


@check_golden_file(
    "./tests/unit/thrift_files/namespace_literal.thrift",
    "namespace_literal.json",
    "namespace_literal_golden.json",
)
def test_namespace_literal(mcp_objects: List[dict]):
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    assert (
        obj["entityUrn"]
        == "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.Foo4,PROD)"
    )


@check_golden_file(
    "./tests/unit/thrift_files/namespace_explicit.thrift",
    "namespace_explicit.json",
    "namespace_explicit_golden.json",
)
def test_namespace_explicit(mcp_objects: List[dict]):
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    assert (
        obj["entityUrn"]
        == "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.Foo5,PROD)"
    )


@check_golden_file(
    "./tests/unit/thrift_files/namespace_py.thrift",
    "namespace_py.json",
    "namespace_py_golden.json",
)
def test_namespace_py(mcp_objects: List[dict]):
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    assert obj["entityUrn"] == "urn:li:dataset:(urn:li:dataPlatform:thrift,Foo2,PROD)"


@check_golden_file(
    "./tests/unit/thrift_files/namespace_multiple.thrift",
    "namespace_multiple.json",
    "namespace_multiple_golden.json",
)
def test_namespace_multiple(mcp_objects: List[dict]):
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    assert (
        obj["entityUrn"]
        == "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.Foo3,PROD)"
    )


@check_golden_file(
    "./tests/unit/thrift_files/enum_types.thrift",
    "enum_types.json",
    "enum_types_golden.json",
)
def test_enum_types(mcp_objects: List[dict]):
    assert len(mcp_objects) == 2
    key = mcp_objects[0]
    properties = mcp_objects[1]
    assert (
        key["entityUrn"]
        == properties["entityUrn"]
        == "urn:li:thriftEnumType:com.company.TweetType"
    )
    assert key["aspectName"] == "thriftEnumTypeKey"
    assert properties["aspectName"] == "thriftEnumTypeProperties"
    aspect = json.loads(properties["aspect"]["value"])
    assert aspect["items"] == [
        {"key": "TWEET"},
        {"key": "RETWEET", "value": {"int": 2}},
        {"key": "DM", "value": {"int": 10}},
        {"key": "REPLY"},
    ]


@check_golden_file(
    "./tests/unit/thrift_files/union_types.thrift",
    "union_types.json",
    "union_types_golden.json",
)
def test_union_types(mcp_objects: List[dict]):
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    obj[
        "entityUrn"
    ] = "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.Foo6,PROD)"


@check_golden_file(
    "./tests/unit/thrift_files/exception_types.thrift",
    "exception_types.json",
    "exception_types_golden.json",
)
def test_exception_types(mcp_objects: List[dict]):
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    obj[
        "entityUrn"
    ] = "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.Foo6,PROD)"


@check_golden_file(
    "./tests/unit/thrift_files/typedef.thrift",
    "typedef.json",
    "typedef_golden.json",
)
def test_typedef(mcp_objects: List[dict]):
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    aspect = json.loads(obj["aspect"]["value"])
    thrift_schema = aspect["platformSchema"]["com.linkedin.schema.ThriftSchema"]
    field = aspect["fields"][0]
    tf = thrift_schema["fields"][0]
    assert field["fieldPath"] == tf["name"] == "bar"
    assert field["type"] == {"type": {"com.linkedin.schema.NumberType": {}}}
    assert field["nativeDataType"] == "i64"
    assert tf["hyperType"] == [
        {"com.linkedin.schema.HyperTypeTextToken": {"text": "i64"}}
    ]


@check_golden_file(
    "./tests/unit/thrift_files/nested_types.thrift",
    "nested_types.json",
    "nested_types_golden.json",
)
def test_nested_types(mcp_objects: List[dict]):
    assert len(mcp_objects) == 5
    s1 = mcp_objects[0]
    aspect = json.loads(s1["aspect"]["value"])
    thrift_schema = aspect["platformSchema"]["com.linkedin.schema.ThriftSchema"]
    field = aspect["fields"][0]
    tf = thrift_schema["fields"][0]
    assert field["fieldPath"] == tf["name"] == "structValue"
    assert field["type"] == {"type": {"com.linkedin.schema.RecordType": {}}}
    assert field["nativeDataType"] == "S2"
    assert tf["hyperType"] == [
        {
            "com.linkedin.schema.HyperTypeUrnToken": {
                "text": "S2",
                "urn": "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.S2,PROD)",
            }
        }
    ]

    u1 = mcp_objects[1]
    aspect = json.loads(u1["aspect"]["value"])
    thrift_schema = aspect["platformSchema"]["com.linkedin.schema.ThriftSchema"]
    field = aspect["fields"][0]
    tf = thrift_schema["fields"][0]
    assert field["fieldPath"] == tf["name"] == "enumValue"
    assert field["type"] == {"type": {"com.linkedin.schema.EnumType": {}}}
    assert field["nativeDataType"] == "E1"
    assert tf["hyperType"] == [
        {
            "com.linkedin.schema.HyperTypeUrnToken": {
                "text": "E1",
                "urn": "urn:li:thriftEnumType:com.company.E1",
            }
        }
    ]

    field = aspect["fields"][1]
    tf = thrift_schema["fields"][1]
    assert field["fieldPath"] == tf["name"] == "structValue"
    assert field["type"] == {"type": {"com.linkedin.schema.RecordType": {}}}
    assert field["nativeDataType"] == "S2"
    assert tf["hyperType"] == [
        {
            "com.linkedin.schema.HyperTypeUrnToken": {
                "text": "S2",
                "urn": "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.S2,PROD)",
            }
        }
    ]


@check_golden_file(
    "./tests/unit/thrift_files/include_1.thrift",
    "include_1.json",
    "include_1_golden.json",
)
def test_include(mcp_objects: List[dict]):
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    aspect = json.loads(obj["aspect"]["value"])
    field = aspect["fields"][0]
    assert field["type"] == {
        "type": {"com.linkedin.schema.ArrayType": {"nestedType": ["i64"]}}
    }
    assert field["nativeDataType"] == "list<i64>"


@check_golden_file(
    "./tests/unit/thrift_files/composite_types.thrift",
    "composite_types.json",
    "composite_types_golden.json",
)
def test_composite_types(mcp_objects: List[dict]):
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    aspect = json.loads(obj["aspect"]["value"])
    thrift_schema = aspect["platformSchema"]["com.linkedin.schema.ThriftSchema"]
    fields = aspect["fields"]
    tfs = thrift_schema["fields"]
    assert len(fields) == len(tfs) == 8
    expected = [
        (
            1,
            "l1",
            {"type": {"com.linkedin.schema.ArrayType": {"nestedType": ["i64"]}}},
            "list<i64>",
            [
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "list<"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "i64"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": ">"}},
            ],
        ),
        (
            2,
            "l2",
            {"type": {"com.linkedin.schema.ArrayType": {"nestedType": ["list<i64>"]}}},
            "list<list<i64>>",
            [
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "list<"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "list<"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "i64"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": ">"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": ">"}},
            ],
        ),
        (
            3,
            "s1",
            {"type": {"com.linkedin.schema.ArrayType": {"nestedType": ["i64"]}}},
            "set<i64>",
            [
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "set<"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "i64"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": ">"}},
            ],
        ),
        (
            4,
            "m1",
            {
                "type": {
                    "com.linkedin.schema.MapType": {
                        "keyType": "string",
                        "valueType": "i64",
                    }
                }
            },
            "map<string,i64>",
            [
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "map<"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "string"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": ","}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "i64"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": ">"}},
            ],
        ),
        (
            5,
            "m2",
            {
                "type": {
                    "com.linkedin.schema.MapType": {
                        "keyType": "string",
                        "valueType": "set<i64>",
                    }
                }
            },
            "map<string,set<i64>>",
            [
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "map<"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "string"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": ","}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "set<"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "i64"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": ">"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": ">"}},
            ],
        ),
        (
            6,
            "l3",
            {"type": {"com.linkedin.schema.ArrayType": {"nestedType": ["TweetType"]}}},
            "list<TweetType>",
            [
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "list<"}},
                {
                    "com.linkedin.schema.HyperTypeUrnToken": {
                        "text": "TweetType",
                        "urn": "urn:li:thriftEnumType:com.company.TweetType",
                    }
                },
                {"com.linkedin.schema.HyperTypeTextToken": {"text": ">"}},
            ],
        ),
        (
            7,
            "m3",
            {
                "type": {
                    "com.linkedin.schema.MapType": {
                        "keyType": "i64",
                        "valueType": "list<i64>",
                    }
                }
            },
            "map<i64,list<i64>>",
            [
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "map<"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "i64"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": ","}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "list<"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "i64"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": ">"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": ">"}},
            ],
        ),
        (
            8,
            "s2",
            {"type": {"com.linkedin.schema.ArrayType": {"nestedType": ["S1"]}}},
            "set<S1>",
            [
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "set<"}},
                {
                    "com.linkedin.schema.HyperTypeUrnToken": {
                        "text": "S1",
                        "urn": "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.S1,PROD)",
                    }
                },
                {"com.linkedin.schema.HyperTypeTextToken": {"text": ">"}},
            ],
        ),
    ]
    for field, tf, expected in zip(
        fields,
        tfs,
        expected,
    ):
        index, name, type_, native_type, hyper_type = expected
        assert field["fieldPath"] == tf["name"] == name
        assert field["type"] == type_
        assert field["nativeDataType"] == native_type
        assert tf["index"] == index
        assert tf["hyperType"] == hyper_type


@check_golden_file(
    "./tests/unit/thrift_files/field_metadata.thrift",
    "field_metadata.json",
    "field_metadata_golden.json",
)
def test_field_metadata(mcp_objects: List[dict]):
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    aspect = json.loads(obj["aspect"]["value"])
    thrift_schema = aspect["platformSchema"]["com.linkedin.schema.ThriftSchema"]
    fields = aspect["fields"]
    tfs = thrift_schema["fields"]
    assert len(fields) == len(tfs) == 4
    expected = [
        (
            1,
            "bar",
            {"type": {"com.linkedin.schema.NumberType": {}}},
            "i64",
            [{"com.linkedin.schema.HyperTypeTextToken": {"text": "i64"}}],
            {"float": 1},
            [{"key": "order", "value": {"int": 2}}],
        ),
        (
            2,
            "constBar",
            {"type": {"com.linkedin.schema.NumberType": {}}},
            "i64",
            [{"com.linkedin.schema.HyperTypeTextToken": {"text": "i64"}}],
            {"float": -100},
            [{"key": "stage", "value": {"string": "prod"}}],
        ),
        (
            3,
            "floatBar",
            {"type": {"com.linkedin.schema.NumberType": {}}},
            "double",
            [{"com.linkedin.schema.HyperTypeTextToken": {"text": "double"}}],
            {"float": 3.0},
            [],
        ),
        (
            4,
            "stringBar",
            {"type": {"com.linkedin.schema.StringType": {}}},
            "string",
            [{"com.linkedin.schema.HyperTypeTextToken": {"text": "string"}}],
            {"string": "hello"},
            [],
        ),
    ]

    for field, tf, expected in zip(
        fields,
        tfs,
        expected,
    ):
        index, name, type_, native_type, hyper_type, default, annotations = expected
        assert field["fieldPath"] == tf["name"] == name
        assert field["type"] == type_
        assert field["nativeDataType"] == native_type
        assert tf["index"] == index
        assert tf["hyperType"] == hyper_type
        assert tf["default"] == default
        assert tf.get("annotations", []) == annotations
