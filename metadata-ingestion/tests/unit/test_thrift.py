import json
import pathlib
from typing import Callable, List

from _pytest.config import Config
from freezegun import freeze_time

from datahub.ingestion.api.common import PipelineContext
from datahub.ingestion.source.thrift.thrift import ThriftSource

FROZEN_TIME = "2020-04-14 07:00:00"


def gen_thrift_mcps_and_verify(
    input_file: str,
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
            func(mcp_objects)

        return wrapper

    return decorator


@gen_thrift_mcps_and_verify(
    "./tests/unit/thrift_files/primitive_types.thrift",
)
def test_primitive(mcp_objects: List[dict]) -> None:
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    aspect = json.loads(obj["aspect"]["value"])
    thrift_schema = aspect["platformSchema"]["com.linkedin.schema.ThriftSchema"]
    fields = aspect["fields"]
    tfs = thrift_schema["fields"]
    assert len(fields) == len(tfs) == 7
    expected = [  # type: ignore [var-annotated]
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
    for field, tf, exp in zip(
        fields,
        tfs,
        expected,
    ):
        index, name, type_, native_type, hyper_type = exp
        assert field["fieldPath"] == tf["name"] == name
        assert field["type"] == type_
        assert field["nativeDataType"] == native_type
        assert tf["index"] == index
        assert tf["hyperType"] == hyper_type


@gen_thrift_mcps_and_verify(
    "./tests/unit/thrift_files/namespace_star.thrift",
)
def test_namespace_star(mcp_objects: List[dict]) -> None:
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    assert (
        obj["entityUrn"]
        == "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.Foo1,PROD)"
    )


@gen_thrift_mcps_and_verify(
    "./tests/unit/thrift_files/namespace_literal.thrift",
)
def test_namespace_literal(mcp_objects: List[dict]) -> None:
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    assert (
        obj["entityUrn"]
        == "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.Foo4,PROD)"
    )


@gen_thrift_mcps_and_verify(
    "./tests/unit/thrift_files/namespace_explicit.thrift",
)
def test_namespace_explicit(mcp_objects: List[dict]) -> None:
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    assert (
        obj["entityUrn"]
        == "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.Foo5,PROD)"
    )


@gen_thrift_mcps_and_verify(
    "./tests/unit/thrift_files/namespace_py.thrift",
)
def test_namespace_py(mcp_objects: List[dict]) -> None:
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    assert obj["entityUrn"] == "urn:li:dataset:(urn:li:dataPlatform:thrift,Foo2,PROD)"


@gen_thrift_mcps_and_verify(
    "./tests/unit/thrift_files/namespace_multiple.thrift",
)
def test_namespace_multiple(mcp_objects: List[dict]) -> None:
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    assert (
        obj["entityUrn"]
        == "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.Foo3,PROD)"
    )


@gen_thrift_mcps_and_verify(
    "./tests/unit/thrift_files/enum_types.thrift",
)
def test_enum_types(mcp_objects: List[dict]) -> None:
    assert len(mcp_objects) == 2
    key = mcp_objects[0]
    properties = mcp_objects[1]
    assert (
        key["entityUrn"]
        == properties["entityUrn"]
        == "urn:li:thriftEnum:com.company.TweetType"
    )
    assert key["aspectName"] == "thriftEnumKey"
    assert properties["aspectName"] == "thriftEnumProperties"
    aspect = json.loads(properties["aspect"]["value"])
    assert aspect["items"] == [
        {"key": "TWEET"},
        {"key": "RETWEET", "value": {"int": 2}},
        {"key": "DM", "value": {"int": 10}},
        {"key": "REPLY"},
    ]


@gen_thrift_mcps_and_verify(
    "./tests/unit/thrift_files/union_types.thrift",
)
def test_union_types(mcp_objects: List[dict]) -> None:
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    obj[
        "entityUrn"
    ] = "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.Foo6,PROD)"


@gen_thrift_mcps_and_verify(
    "./tests/unit/thrift_files/exception_types.thrift",
)
def test_exception_types(mcp_objects: List[dict]) -> None:
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    obj[
        "entityUrn"
    ] = "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.Foo6,PROD)"


@gen_thrift_mcps_and_verify(
    "./tests/unit/thrift_files/typedef.thrift",
)
def test_typedef(mcp_objects: List[dict]) -> None:
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


@gen_thrift_mcps_and_verify(
    "./tests/unit/thrift_files/nested_types.thrift",
)
def test_nested_types(mcp_objects: List[dict]) -> None:
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
                "urn": "urn:li:thriftEnum:com.company.E1",
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


@gen_thrift_mcps_and_verify(
    "./tests/unit/thrift_files/include_1.thrift",
)
def test_include(mcp_objects: List[dict]) -> None:
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    aspect = json.loads(obj["aspect"]["value"])
    field = aspect["fields"][0]
    assert field["type"] == {
        "type": {"com.linkedin.schema.ArrayType": {"nestedType": ["i64"]}}
    }
    assert field["nativeDataType"] == "list<i64>"


@gen_thrift_mcps_and_verify(
    "./tests/unit/thrift_files/composite_types.thrift",
)
def test_composite_types(mcp_objects: List[dict]) -> None:
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
                        "urn": "urn:li:thriftEnum:com.company.TweetType",
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
    for field, tf, exp in zip(
        fields,
        tfs,
        expected,
    ):
        index, name, type_, native_type, hyper_type = exp
        assert field["fieldPath"] == tf["name"] == name
        assert field["type"] == type_
        assert field["nativeDataType"] == native_type
        assert tf["index"] == index
        assert tf["hyperType"] == hyper_type


@gen_thrift_mcps_and_verify(
    "./tests/unit/thrift_files/field_metadata.thrift",
)
def test_field_metadata(mcp_objects: List[dict]) -> None:
    assert len(mcp_objects) == 1
    obj = mcp_objects[0]
    aspect = json.loads(obj["aspect"]["value"])
    thrift_schema = aspect["platformSchema"]["com.linkedin.schema.ThriftSchema"]
    fields = aspect["fields"]
    tfs = thrift_schema["fields"]
    assert len(fields) == len(tfs) == 4
    expected = [  # type: ignore [var-annotated]
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

    for field, tf, exp in zip(
        fields,
        tfs,
        expected,
    ):
        index, name, type_, native_type, hyper_type, default, annotations = exp
        assert field["fieldPath"] == tf["name"] == name
        assert field["type"] == type_
        assert field["nativeDataType"] == native_type
        assert tf["index"] == index
        assert tf["hyperType"] == hyper_type
        assert tf["default"] == default
        assert tf.get("annotations", []) == annotations


@gen_thrift_mcps_and_verify(
    "./tests/unit/thrift_files/const_composite_types.thrift",
)
def test_const_composite_types(mcp_objects: List[dict]) -> None:
    assert len(mcp_objects) == 3
    obj = mcp_objects[2]
    aspect = json.loads(obj["aspect"]["value"])
    thrift_schema = aspect["platformSchema"]["com.linkedin.schema.ThriftSchema"]
    fields = aspect["fields"]
    tfs = thrift_schema["fields"]
    assert len(fields) == len(tfs) == 12
    expected = [
        (
            1,
            "color",
            {"type": {"com.linkedin.schema.EnumType": {}}},
            "Color",
            [
                {
                    "com.linkedin.schema.HyperTypeUrnToken": {
                        "text": "Color",
                        "urn": "urn:li:thriftEnum:com.company.Color",
                    }
                }
            ],
            {"string": "Color.RED"},
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
            {"string": "[[1, 2, 3], [1, 2, 3], [1, 2, 3]]"},
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
            None,
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
            {"string": "{a:1, b:2}"},
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
            None,
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
                        "urn": "urn:li:thriftEnum:com.company.TweetType",
                    }
                },
                {"com.linkedin.schema.HyperTypeTextToken": {"text": ">"}},
            ],
            None,
        ),
        (
            7,
            "l1",
            {"type": {"com.linkedin.schema.ArrayType": {"nestedType": ["i64"]}}},
            "list<i64>",
            [
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "list<"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": "i64"}},
                {"com.linkedin.schema.HyperTypeTextToken": {"text": ">"}},
            ],
            {"string": "[1, 2, 3]"},
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
            None,
        ),
        (
            9,
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
            {"string": "{1:[11, 111], 2:[22, 222]}"},
        ),
        (
            10,
            "color2",
            {"type": {"com.linkedin.schema.EnumType": {}}},
            "TweetType",
            [
                {
                    "com.linkedin.schema.HyperTypeUrnToken": {
                        "text": "TweetType",
                        "urn": "urn:li:thriftEnum:com.company.TweetType",
                    }
                }
            ],
            {"string": "TweetType.RETWEET"},
        ),
        (
            11,
            "s3",
            {"type": {"com.linkedin.schema.RecordType": {}}},
            "S1",
            [
                {
                    "com.linkedin.schema.HyperTypeUrnToken": {
                        "text": "S1",
                        "urn": "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.S1,PROD)",
                    }
                }
            ],
            {"string": "{'S3':'structValue'}"},
        ),
        (
            12,
            "U2",
            {"type": {"com.linkedin.schema.UnionType": {"nestedTypes": ["E1", "S2"]}}},
            "U1",
            [
                {
                    "com.linkedin.schema.HyperTypeUrnToken": {
                        "text": "U1",
                        "urn": "urn:li:dataset:(urn:li:dataPlatform:thrift,com.company.U1,PROD)",
                    }
                }
            ],
            {"string": '{"E1":"enumValue","S2":"structValue"}'},
        ),
    ]
    for field, tf, exp in zip(
        fields,
        tfs,
        expected,
    ):
        index, name, type_, native_type, hyper_type, default = exp
        assert field["fieldPath"] == tf["name"] == name
        assert field["type"] == type_
        assert field["nativeDataType"] == native_type
        assert tf["index"] == index
        assert tf["hyperType"] == hyper_type
        if "default" in tf.keys():
            assert tf["default"] == default


@gen_thrift_mcps_and_verify(
    "./tests/unit/thrift_files/annotations.thrift",
)
def test_annotations(mcp_objects: List[dict]) -> None:
    assert len(mcp_objects) == 4
    obj = mcp_objects[0]
    aspect = json.loads(obj["aspect"]["value"])
    general_annotations = aspect["platformSchema"]["com.linkedin.schema.ThriftSchema"][
        "annotations"
    ]
    thrift_schema = aspect["platformSchema"]["com.linkedin.schema.ThriftSchema"]
    fields = aspect["fields"]
    tfs = thrift_schema["fields"]
    assert len(fields) == len(tfs) == 1
    expected = [  # type: ignore [var-annotated]
        (
            1,
            "bar",
            {"type": {"com.linkedin.schema.NumberType": {}}},
            "i64",
            [{"com.linkedin.schema.HyperTypeTextToken": {"text": "i64"}}],
            {"float": 1},
            [
                {"key": "datahub.terms", "value": {"string": "term1,term2"}},
                {"key": "size", "value": {"int": 12}},
            ],
            [
                {"urn": "urn:li:glossaryTerm:term1"},
                {"urn": "urn:li:glossaryTerm:term2"},
            ],
        ),
    ]
    expect_annotations = [
        {"key": "datahub.terms", "value": {"string": "term3,term4"}},
        {"key": "case", "value": {"string": "case1"}},
    ]
    for field, tf, exp in zip(
        fields,
        tfs,
        expected,
    ):
        (
            index,
            name,
            type_,
            native_type,
            hyper_type,
            default,
            annotations,
            terms,
        ) = exp

        assert field["fieldPath"] == tf["name"] == name
        assert field["type"] == type_
        assert field["nativeDataType"] == native_type
        assert tf["index"] == index
        assert tf["hyperType"] == hyper_type
        assert tf["default"] == default
        assert tf.get("annotations", []) == annotations
        assert field["glossaryTerms"]["terms"] == terms
    assert expect_annotations == general_annotations

    obj = mcp_objects[2]
    aspect = json.loads(obj["aspect"]["value"])
    general_annotations = aspect["platformSchema"]["com.linkedin.schema.ThriftSchema"][
        "annotations"
    ]
    thrift_schema = aspect["platformSchema"]["com.linkedin.schema.ThriftSchema"]
    fields = aspect["fields"]
    tfs = thrift_schema["fields"]
    assert len(fields) == len(tfs) == 1
    expected = [  # type: ignore [var-annotated]
        (
            1,
            "bar1",
            {"type": {"com.linkedin.schema.NumberType": {}}},
            "i64",
            [{"com.linkedin.schema.HyperTypeTextToken": {"text": "i64"}}],
            {"float": 2},
            [
                {"key": "datahub.terms", "value": {"string": "term5,term6"}},
                {"key": "size", "value": {"int": 11}},
            ],
            [
                {"urn": "urn:li:glossaryTerm:term5"},
                {"urn": "urn:li:glossaryTerm:term6"},
            ],
        ),
    ]
    expect_annotations = [
        {"key": "datahub.terms", "value": {"string": "term7,term8"}},
        {"key": "case", "value": {"string": "case2"}},
    ]
    for field, tf, exp in zip(
        fields,
        tfs,
        expected,
    ):
        (
            index,
            name,
            type_,
            native_type,
            hyper_type,
            default,
            annotations,
            terms,
        ) = exp
        assert field["fieldPath"] == tf["name"] == name
        assert field["type"] == type_
        assert field["nativeDataType"] == native_type
        assert tf["index"] == index
        assert tf["hyperType"] == hyper_type
        assert tf["default"] == default
        assert tf.get("annotations", []) == annotations
        assert field["glossaryTerms"]["terms"] == terms
    assert expect_annotations == general_annotations

    obj = mcp_objects[1]
    aspect = json.loads(obj["aspect"]["value"])
    assert aspect["terms"] == [
        {"urn": "urn:li:glossaryTerm:term3"},
        {"urn": "urn:li:glossaryTerm:term4"},
    ]

    obj = mcp_objects[3]
    aspect = json.loads(obj["aspect"]["value"])
    assert aspect["terms"] == [
        {"urn": "urn:li:glossaryTerm:term7"},
        {"urn": "urn:li:glossaryTerm:term8"},
    ]
