import os
import re
from dataclasses import dataclass, field, replace
from functools import lru_cache, reduce
from typing import Dict, Generator, Iterable, List, Optional, Tuple, Type, Union, cast

from antlr4 import CommonTokenStream, InputStream

from datahub.configuration.common import ConfigModel
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.ingestion.api.common import WorkUnit
from datahub.ingestion.api.source import Source, SourceReport
from datahub.ingestion.api.workunit import MetadataWorkUnit, UsageStatsWorkUnit
from datahub.ingestion.source.thrift.dist.thriftLexer import thriftLexer  # type: ignore
from datahub.ingestion.source.thrift.dist.thriftParser import thriftParser  # type: ignore
from datahub.ingestion.source.thrift.dist.thriftVisitor import thriftVisitor  # type: ignore
from datahub.metadata.com.linkedin.pegasus2avro.events.metadata import ChangeType
from datahub.metadata.com.linkedin.pegasus2avro.schema import (
    BooleanType,
    BytesType,
    NumberType,
    OtherSchema,
    SchemaField,
    SchemaFieldDataType,
    SchemaMetadata,
    StringType,
)


def get_dataset_urn(java_namespace: Optional[str], name: str) -> str:
    return f"urn:li:dataset:(urn:li:dataPlatform:thrift,{get_qualified_name(name, java_namespace)},PROD)"


def get_qualified_name(name: str, qualifier: Optional[str]) -> str:
    if qualifier is None:
        return name
    else:
        return f"{qualifier}.{name}"


def split_qualified_name(qualified_name: str) -> Tuple[Optional[str], str]:
    parts = qualified_name.split(".", maxsplit=1)
    if len(parts) == 1:
        qualifier = None
        name = qualified_name
    elif len(parts) == 2:
        qualifier, name = parts
    else:
        raise ValueError()
    return qualifier, name


def get_literal_text(ctx: thriftParser.LITERAL) -> str:
    literal = ctx.getText()
    m = re.match(r"(\".*\")|(\'.*\')", literal)
    if m is None:
        raise ValueError(f"{literal} is not a valid include")
    return literal[1:-1]


class ThriftSourceConfig(ConfigModel):
    filename: str


@lru_cache
def parsefile(filename: str) -> thriftParser.DocumentContext:
    with open(filename) as text_file:
        # lexer

        lexer = thriftLexer(InputStream(text_file.read()))
        stream = CommonTokenStream(lexer)
        # parser
        parser = thriftParser(stream)

        tree = parser.document()
        return tree


@dataclass(frozen=True)
class ResolveResult:
    pass


@dataclass(frozen=True)
class Resolved(ResolveResult):
    urn: str
    native_data_type: str
    namespaces: Dict[str, str]


@dataclass(frozen=True)
class ResolvedEnum(Resolved):
    pass


@dataclass(frozen=True)
class ResolvedStruct(Resolved):
    pass


@dataclass(frozen=True)
class ResolvedConstValue(Resolved):
    type_: Type
    value: Union[int, str, bool, float, None]


@dataclass(frozen=True)
class Unresolved(ResolveResult):
    pass


@dataclass(frozen=True)
class UnresolvedFieldType(Unresolved):
    ctx: thriftParser.Field_typeContext


@dataclass(frozen=True)
class UnresolvedConstValue(Unresolved):
    ctx: thriftParser.Const_valueContext


@dataclass(frozen=True)
class NameResolver:
    namespaces: Dict[str, str] = field(default_factory=dict)
    data: Dict[str, ResolveResult] = field(default_factory=dict)

    @property
    def java_namespace(self) -> Optional[str]:
        if "java" in self.namespaces:
            return self.namespaces["java"]
        elif "*" in self.namespaces:
            return self.namespaces["*"]
        else:
            return None

    def merge(self, other: "NameResolver") -> "NameResolver":
        return replace(
            self,
            namespaces={**self.namespaces, **other.namespaces},
            data={**self.data, **other.data},
        )

    def add_struct(self, name: str) -> "NameResolver":
        return replace(
            self,
            data={
                **self.data,
                name: ResolvedStruct(
                    get_dataset_urn(self.java_namespace, name), name, self.namespaces
                ),
            },
        )

    def add_const_value(
        self,
        name: str,
        ctx: thriftParser.Const_valueContext,
    ) -> "NameResolver":
        return replace(
            self,
            data={**self.data, name: UnresolvedConstValue(ctx)},
        )

    def add_namespace(self, language: str, namespace: str) -> "NameResolver":
        return replace(self, namespaces={**self.namespaces, language: namespace})

    def get(self, name: str) -> Optional[ResolveResult]:
        return self.data.get(name)


@dataclass(frozen=True)
class GetHeader(thriftVisitor):
    filename: str

    def visitDocument(self, ctx: thriftParser.DocumentContext) -> NameResolver:
        return reduce(
            lambda result, current: result.merge(self.visitHeader(current)),
            ctx.header(),
            NameResolver(),
        )

    def visitHeader(self, ctx: thriftParser.HeaderContext) -> NameResolver:
        if ctx.namespace_():
            return self.visitNamespace_(ctx.namespace_())
        else:
            return NameResolver()

    def getNamespaceType(self, ctx: thriftParser.Namespace_Context) -> str:
        if ctx.getText()[0:3] == "cpp":
            return "cpp"
        elif ctx.getText()[0:3] == "php":
            return "php"
        elif ctx.getText()[9:10] == "*":
            return "star"
        else:
            return "explicit"

    def visitNamespace_(self, ctx: thriftParser.Namespace_Context) -> NameResolver:
        func = {
            "star": self.visitStarNamespace,
            "explicit": self.visitExplicitNamespace,
            "cpp": self.visitCppNamespace,
            "php": self.visitPhpNamespace,
        }.get(self.getNamespaceType(ctx), None)
        if func is not None:
            return func(ctx)
        else:
            return NameResolver()

    def visitStarNamespace(self, ctx: thriftParser.Namespace_Context) -> NameResolver:
        if ctx.IDENTIFIER():
            return NameResolver().add_namespace("*", ctx.IDENTIFIER()[0].getText())
        elif ctx.LITERAL():
            return NameResolver().add_namespace("*", get_literal_text(ctx.LITERAL()))
        else:
            raise NotImplementedError("only support IDENTIFIER OR LITERAL as namespace name")

    def visitExplicitNamespace(
        self, ctx: thriftParser.Namespace_Context
    ) -> NameResolver:
        identifiers = ctx.IDENTIFIER()
        language = identifiers[0].getText()
        if len(identifiers) == 2:
            return NameResolver().add_namespace(language, identifiers[1].getText())
        elif ctx.LITERAL():
            return NameResolver().add_namespace(
                language, get_literal_text(ctx.LITERAL())
            )
        else:
            raise NotImplementedError("only support IDENTIFIER OR LITERAL as namespace name")

    def visitCppNamespace(self, ctx: thriftParser.Namespace_Context) -> NameResolver:
        return NameResolver().add_namespace("cpp", ctx.IDENTIFIER()[0].getText())

    def visitPhpNamespace(self, ctx: thriftParser.Namespace_Context) -> NameResolver:
        return NameResolver().add_namespace("php", ctx.IDENTIFIER()[0].getText())


@lru_cache
def get_header(filename: str) -> NameResolver:
    return GetHeader(filename)


@dataclass(frozen=True)
class GetNameResolver(thriftVisitor):
    header: NameResolver

    def visitDocument(self, ctx: thriftParser.DocumentContext) -> NameResolver:
        return reduce(
            lambda result, current: result.merge(self.visitDefinition(current)),
            ctx.definition(),
            self.header,
        )

    def visitDefinition(self, ctx: thriftParser.DefinitionContext) -> NameResolver:
        if ctx.struct_():
            return self.visitStruct_(ctx.struct_())
        else:
            raise NotImplementedError("can only process struct")


    def visitStruct_(self, ctx: thriftParser.Struct_Context) -> NameResolver:
        return self.header.add_struct(ctx.IDENTIFIER().getText())


@lru_cache
def get_name_resolver(filename: str) -> NameResolver:
    tree = parsefile(filename)
    header = GetHeader(filename).visit(tree)
    return GetNameResolver(header).visit(tree)


@dataclass(frozen=True)
class Binder:
    filename: str
    name_resolver: NameResolver

    def resolve(self, qualified_name: str) -> Optional[ResolveResult]:
        qualifier, name = split_qualified_name(qualified_name)
        if qualifier is None:
            return self.name_resolver.get(name)
        else:
            raise NotImplementedError("Cannot process include yet")

    def bind_MCPs_from_Document(
        self, ctx: thriftParser.DocumentContext
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        for definition in ctx.definition():
            yield from self.bind_MCPs_from_Definition(definition)

    def bind_MCPs_from_Definition(
        self, ctx: thriftParser.DefinitionContext
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        if ctx.struct_():
            yield from self.bind_MCPs_from_struct_(ctx.struct_())
        else:
            raise NotImplementedError("can only process struct and const value")

    def bind_MCPs_from_struct_(
        self, ctx: thriftParser.Struct_Context
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:

        name = ctx.IDENTIFIER().getText()
        result = cast(Resolved, self.resolve(name))
        yield MetadataChangeProposalWrapper(
            entityType="dataset",
            changeType=ChangeType.UPSERT,
            aspectName="schemaMetadata",
            entityUrn=result.urn,
            aspect=SchemaMetadata(
                schemaName=name,
                platform="urn:li:dataPlatform:thrift",
                version=0,
                hash="",
                platformSchema=OtherSchema(
                    rawSchema=ctx.getText(),
                ),
                fields=[
                    self.bind_SchemaField_from_field(field) for field in ctx.field()
                ],
            ),
        )

    def bind_SchemaField_from_field(
        self, ctx: thriftParser.FieldContext
    ) -> SchemaField:
        return SchemaField(
            fieldPath=ctx.IDENTIFIER().getText(),
            type=self.bind_SchemaFieldDataType_from_field_type(ctx.field_type()),
            nativeDataType=self.bind_native_data_type_from_field_type(ctx.field_type()),
        )

    def bind_native_data_type_from_field_type(
        self, ctx: thriftParser.Field_typeContext
    ) -> str:
        if ctx.base_type():
            return self.bind_native_data_type_from_base_type(ctx.base_type())
        else:
            raise NotImplementedError("can only process base type")

    def bind_native_data_type_from_base_type(
        self, ctx: thriftParser.Base_typeContext
    ) -> str:
        return ctx.real_base_type().getText()

    def bind_Type_from_field_type(
        self, ctx: thriftParser.Field_typeContext
    ) -> Optional[Type]:
        if ctx.base_type():
            return self.bind_Type_from_base_type(ctx.base_type())
        else:
            raise NotImplementedError("can only process base type")

    def bind_Type_from_base_type(self, ctx: thriftParser.Base_typeContext) -> Type:
        return {
            "bool": bool,
            "byte": int,
            "i16": int,
            "i32": int,
            "i64": int,
            "double": float,
            "string": str,
        }[ctx.real_base_type().getText()]

    def bind_value_from_const_value(
        self, ctx: thriftParser.Const_valueContext, type_: Type
    ) -> Union[int, str, bool, float, None]:
        if ctx.integer() and type_ in {int, bool, float}:
            return self.bind_value_from_integer(ctx.integer(), type_)
        elif ctx.DOUBLE() and type_ == float:
            return self.bind_value_from_DOUBLE(ctx.DOUBLE())
        elif ctx.LITERAL() and type_ == str:
            return self.bind_value_from_LITERAL(ctx.LITERAL())
        else:
            raise NotImplementedError("can only process base type")

    def bind_value_from_DOUBLE(self, ctx: thriftParser.IDENTIFIER) -> float:
        return float(ctx.getText())

    def bind_value_from_LITERAL(self, ctx: thriftParser.LITERAL) -> str:
        return get_literal_text(ctx)

    def bind_value_from_integer(
        self, ctx: thriftParser.IntegerContext, type_: Type
    ) -> Union[int, bool, float]:
        if ctx.INTEGER():
            result = int(ctx.INTEGER().getText())
        elif ctx.HEX_INTEGER():
            result = int(ctx.HEX_INTEGER().getText(), 16)
        else:
            raise NotImplementedError("only support INTEGER and HEX INTEGER")
        return {int: int, bool: bool, float: float}[type_](result)

    def bind_SchemaFieldDataType_from_field_type(
        self, ctx: thriftParser.Field_typeContext
    ) -> SchemaFieldDataType:
        if ctx.base_type():
            return self.bind_SchemaFieldDataType_from_base_type(ctx.base_type())

        else:
            raise NotImplementedError("can only process base types")

    def bind_SchemaFieldDataType_from_base_type(
        self, ctx: thriftParser.Base_typeContext
    ) -> SchemaFieldDataType:
        return self.bind_SchemaFieldDataType_from_real_base_type(ctx.real_base_type())

    def bind_SchemaFieldDataType_from_real_base_type(
        self, ctx: thriftParser.Real_base_typeContext
    ) -> SchemaFieldDataType:
        if (
            ctx.TYPE_BYTE()
            or ctx.TYPE_I16()
            or ctx.TYPE_I32()
            or ctx.TYPE_I64()
            or ctx.TYPE_DOUBLE()
        ):
            return SchemaFieldDataType(NumberType())
        elif ctx.TYPE_STRING():
            return SchemaFieldDataType(StringType())
        elif ctx.TYPE_BINARY():
            return SchemaFieldDataType(BytesType())
        elif ctx.TYPE_BOOL():
            return SchemaFieldDataType(BooleanType())
        else:
            raise NotImplementedError("can only process base type")


@lru_cache
def get_binder(filename: str) -> Binder:
    name_resolver = get_name_resolver(filename)
    return Binder(filename, name_resolver)


@dataclass
class ThriftReport(SourceReport):
    errors: List[str] = field(default_factory=list)

    def report_workunit(self, wu: WorkUnit) -> None:
        self.workunits_produced += 1
        self.workunit_ids.append(wu.id)


@dataclass
class ThriftSource(Source):
    config: ThriftSourceConfig
    report: ThriftReport = field(default_factory=ThriftReport)

    @classmethod
    def create(cls, config_dict, ctx):
        config = ThriftSourceConfig.parse_obj(config_dict)
        return cls(ctx, config)

    def parse(
        self, filename: str
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        try:
            if os.path.isfile(filename) and os.path.splitext(filename)[1] == ".thrift":
                print(f"Processing {filename}")
                tree = parsefile(filename)
                # evaluator
                yield from get_binder(
                    filename
                ).bind_MCPs_from_Document(tree)
            elif os.path.isdir(filename):
                for f in os.listdir(filename):
                    yield from self.parse(os.path.join(filename, f))
        except Exception as e:
            self.report.errors.append(f"Error: {e}")

    def get_workunits(self) -> Iterable[Union[MetadataWorkUnit, UsageStatsWorkUnit]]:
        for i, obj in enumerate(
            self.parse(self.config.filename)
        ):
            wu = MetadataWorkUnit(f"file://{self.config.filename}:{i}", mcp=obj)
            self.report.report_workunit(wu)
            yield wu

    def get_report(self):
        return self.report

    def close(self):
        pass
