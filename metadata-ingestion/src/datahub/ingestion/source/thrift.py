import os
import re
from abc import ABC
from dataclasses import dataclass, field, replace
from functools import lru_cache, reduce
from types import TracebackType
from typing import Dict, Generator, Iterable, List, Optional, Tuple, Type, Union, cast

from antlr4 import CommonTokenStream, InputStream

from datahub.configuration.common import ConfigModel
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.ingestion.api.source import Source, SourceReport
from datahub.ingestion.api.workunit import MetadataWorkUnit, UsageStatsWorkUnit
from datahub.ingestion.source.dist.ThriftLexer import ThriftLexer  # type: ignore
from datahub.ingestion.source.dist.ThriftParser import ThriftParser  # type: ignore
from datahub.ingestion.source.dist.ThriftVisitor import ThriftVisitor  # type: ignore
from datahub.metadata.com.linkedin.pegasus2avro.events.metadata import ChangeType
from datahub.metadata.com.linkedin.pegasus2avro.schema import (
    Annotation,
    ArrayType,
    BooleanType,
    BytesType,
    EnumType,
    HyperTypeTextToken,
    HyperTypeUrnToken,
    MapType,
    NumberType,
    RecordType,
    SchemaField,
    SchemaFieldDataType,
    SchemaMetadata,
    StringType,
    ThriftEnumItem,
    ThriftEnumTypeKey,
    ThriftEnumTypeProperties,
    ThriftField,
    ThriftSchema,
    UnionType,
)


def get_enum_urn(java_namespace: Optional[str], name: str) -> str:
    return f"urn:li:thriftEnumType:{get_qualified_name(name, java_namespace)}"


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


def get_literal_text(ctx: ThriftParser.LITERAL) -> str:
    literal = ctx.getText()
    m = re.match(r"(\".*\")|(\'.*\')", literal)
    if m is None:
        raise ValueError(f"{literal} is not a valid include")
    return literal[1:-1]


class ThriftSourceConfig(ConfigModel):
    filename: str
    thrift_paths: Optional[Tuple[str, ...]] = None


@lru_cache
def parse(filename: str) -> ThriftParser.DocumentContext:
    with open(filename) as text_file:
        # lexer

        lexer = ThriftLexer(InputStream(text_file.read()))
        stream = CommonTokenStream(lexer)
        # parser
        parser = ThriftParser(stream)

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
class ResolvedUnion(Resolved):
    subtypes: List[str]


@dataclass(frozen=True)
class ResolvedException(Resolved):
    pass


@dataclass(frozen=True)
class ResolvedConstValue(Resolved):
    type_: Type
    value: Union[int, str, bool, float, None]


@dataclass(frozen=True)
class Unresolved(ResolveResult):
    pass


@dataclass(frozen=True)
class Redirect(Unresolved):
    filename: str
    thrift_path: Optional[Tuple[str, ...]]
    qualified_name: str


@dataclass(frozen=True)
class UnresolvedFieldType(Unresolved):
    ctx: ThriftParser.Field_typeContext


@dataclass(frozen=True)
class UnresolvedConstValue(Unresolved):
    ctx: ThriftParser.Const_valueContext


@dataclass(frozen=True)
class NameResolver:
    namespaces: Dict[str, str] = field(default_factory=dict)
    data: Dict[str, ResolveResult] = field(default_factory=dict)
    includes: Dict[str, str] = field(default_factory=dict)

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
            includes={**self.includes, **other.includes},
        )

    def add_enum(self, name: str) -> "NameResolver":
        return replace(
            self,
            data={
                **self.data,
                name: ResolvedEnum(
                    get_enum_urn(self.java_namespace, name), name, self.namespaces
                ),
            },
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

    def add_union(self, name: str, subtypes: List[str]) -> "NameResolver":
        return replace(
            self,
            data={
                **self.data,
                name: ResolvedUnion(
                    get_dataset_urn(self.java_namespace, name),
                    name,
                    self.namespaces,
                    subtypes,
                ),
            },
        )

    def add_typedef(
        self,
        name: str,
        ctx: ThriftParser.Field_typeContext,
    ) -> "NameResolver":
        return replace(
            self,
            data={**self.data, name: UnresolvedFieldType(ctx)},
        )

    def add_const_value(
        self,
        name: str,
        ctx: ThriftParser.Const_valueContext,
    ) -> "NameResolver":
        return replace(
            self,
            data={**self.data, name: UnresolvedConstValue(ctx)},
        )

    def add_include(self, qualifier: str, filename: str) -> "NameResolver":
        return replace(self, includes={**self.includes, qualifier: filename})

    def add_namespace(self, language: str, namespace: str) -> "NameResolver":
        return replace(self, namespaces={**self.namespaces, language: namespace})

    def get(self, name: str) -> Optional[ResolveResult]:
        return self.data.get(name)


@dataclass(frozen=True)
class GetHeader(ThriftVisitor):
    filename: str
    thrift_paths: List[str] = field(default_factory=list)

    def visitDocument(self, ctx: ThriftParser.DocumentContext) -> NameResolver:
        return reduce(
            lambda result, current: result.merge(self.visitHeader(current)),
            ctx.header(),
            NameResolver(),
        )

    def visitHeader(self, ctx: ThriftParser.HeaderContext) -> NameResolver:
        if ctx.include_():
            return self.visitInclude_(ctx.include_())
        elif ctx.namespace_():
            return self.visitNamespace_(ctx.namespace_())
        else:
            return NameResolver()

    def visitNamespace_(self, ctx: ThriftParser.Namespace_Context) -> NameResolver:
        func = {
            ThriftParser.StarNamespaceContext: self.visitStarNamespace,
            ThriftParser.ExplicitNamespaceContext: self.visitExplicitNamespace,
            ThriftParser.CppNamespaceContext: self.visitCppNamespace,
            ThriftParser.PhpNamespaceContext: self.visitPhpNamespace,
        }.get(type(ctx), None)
        if func is not None:
            return func(ctx)
        else:
            return NameResolver()

    def visitStarNamespace(
        self, ctx: ThriftParser.StarNamespaceContext
    ) -> NameResolver:
        if ctx.IDENTIFIER():
            return NameResolver().add_namespace("*", ctx.IDENTIFIER().getText())
        elif ctx.LITERAL():
            return NameResolver().add_namespace("*", get_literal_text(ctx.LITERAL()))
        else:
            raise NotImplementedError()

    def visitExplicitNamespace(
        self, ctx: ThriftParser.ExplicitNamespaceContext
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
            raise NotImplementedError()

    def visitCppNamespace(self, ctx: ThriftParser.CppNamespaceContext) -> NameResolver:
        return NameResolver().add_namespace("cpp", ctx.IDENTIFIER().getText())

    def visitPhpNamespace(self, ctx: ThriftParser.PhpNamespaceContext) -> NameResolver:
        return NameResolver().add_namespace("php", ctx.IDENTIFIER().getText())

    def visitInclude_(self, ctx: ThriftParser.Include_Context) -> NameResolver:
        filepath = os.path.dirname(self.filename)
        include_filename = get_literal_text(ctx.LITERAL())

        qualifier = os.path.splitext(os.path.split(include_filename)[1])[0]
        potential_include_file_fullnames = [
            os.path.join(filepath, include_filename)
        ] + [
            os.path.join(thrift_path, include_filename)
            for thrift_path in self.thrift_paths or []
        ]
        for potential_include_file_fullname in potential_include_file_fullnames:
            if os.path.isfile(potential_include_file_fullname):
                return NameResolver().add_include(
                    qualifier, potential_include_file_fullname
                )
        else:
            raise RuntimeError(f"Cannot find {include_filename}")


@lru_cache
def get_header(filename: str, thrift_paths: List[str]) -> NameResolver:
    return GetHeader(filename, thrift_paths).visit(parse(filename))


@dataclass(frozen=True)
class GetNameResolver(ThriftVisitor):
    header: NameResolver

    def visitDocument(self, ctx: ThriftParser.DocumentContext) -> NameResolver:
        return reduce(
            lambda result, current: result.merge(self.visitDefinition(current)),
            ctx.definition(),
            self.header,
        )

    def visitDefinition(self, ctx: ThriftParser.DefinitionContext) -> NameResolver:
        if ctx.enum_rule():
            return self.visitEnum_rule(ctx.enum_rule())
        elif ctx.struct_():
            return self.visitStruct_(ctx.struct_())
        elif ctx.union_():
            return self.visitUnion_(ctx.union_())
        elif ctx.service():
            return self.header
        elif ctx.exception_():
            return self.visitException_(ctx.exception_())
        elif ctx.typedef_():
            return self.visitTypedef_(ctx.typedef_())
        elif ctx.const_rule():
            return self.visitConst_rule(ctx.const_rule())
        else:
            raise NotImplementedError()

    def visitConst_rule(self, ctx: ThriftParser.Const_ruleContext) -> NameResolver:
        return self.header.add_const_value(
            ctx.IDENTIFIER().getText(), ctx.const_value()
        )

    def visitException_(self, ctx: ThriftParser.Exception_Context) -> NameResolver:
        return self.header.add_struct(ctx.IDENTIFIER().getText())

    def visitTypedef_(self, ctx: ThriftParser.Typedef_Context) -> NameResolver:
        return self.header.add_typedef(ctx.IDENTIFIER().getText(), ctx.field_type())

    def visitEnum_rule(self, ctx: ThriftParser.Enum_ruleContext) -> NameResolver:
        return self.header.add_enum(ctx.IDENTIFIER().getText())

    def visitStruct_(self, ctx: ThriftParser.Struct_Context) -> NameResolver:
        return self.header.add_struct(ctx.IDENTIFIER().getText())

    def visitUnion_(self, ctx: ThriftParser.Union_Context) -> NameResolver:
        subtypes = [field.field_type().getText() for field in ctx.field()]
        return self.header.add_union(ctx.IDENTIFIER().getText(), subtypes)


@lru_cache
def get_name_resolver(filename: str, thrift_paths: Tuple[str, ...]) -> NameResolver:
    tree = parse(filename)
    header = GetHeader(filename, thrift_paths).visit(tree)
    return GetNameResolver(header).visit(tree)


@dataclass(frozen=True)
class BindingContext(ABC):
    parent: "Optional[BindingContext]"

    def _resolve(self, qualified_name: str) -> Optional[ResolveResult]:
        return None

    def resolve(self, qualified_name: str) -> Optional[ResolveResult]:
        current: Optional[BindingContext] = self
        while current is not None:
            result = current._resolve(qualified_name)
            if result is not None:
                return result
            current = current.parent
        # TODO
        # raise RuntimeError(f"{qualified_name} cannot be resolved.")
        return None

    def _get_filename(self) -> Optional[str]:
        return None

    def get_filename(self) -> str:
        current: Optional[BindingContext] = self
        while current is not None:
            result = current._get_filename()
            if result is not None:
                return result
            current = current.parent
        raise RuntimeError("Cannot get filename")


@dataclass
class BindingContextPusher:
    binder: "Binder"
    new_context: BindingContext
    old_context: Optional[BindingContext] = None

    def __enter__(self) -> None:
        self.old_context = self.binder.context
        self.binder.context = self.new_context

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        assert self.old_context is not None
        self.binder.context = self.old_context
        return True


@dataclass(frozen=True)
class NamingBindingContext(BindingContext):
    filename: str
    thrift_paths: Optional[Tuple[str, ...]] = None

    def _resolve(self, qualified_name: str) -> Optional[ResolveResult]:
        name_resolver = get_name_resolver(self.filename, self.thrift_paths)
        qualifier, name = split_qualified_name(qualified_name)
        if qualifier is None:
            return name_resolver.get(name)
        else:
            if qualifier in name_resolver.includes:
                filename = name_resolver.includes[qualifier]
                return Redirect(filename, self.thrift_paths, name)
            elif isinstance(name_resolver.get(qualifier), ResolvedEnum):
                return None  # TODO 1: order = SortOrder.DESC
            else:
                raise RuntimeError(
                    f"The qualifier of {qualified_name} is not included."
                )

    def _get_filename(self) -> Optional[str]:
        return self.filename


@dataclass
class Binder:
    context: BindingContext

    def bind_MCPs_from_Document(
        self, ctx: ThriftParser.DocumentContext
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        for definition in ctx.definition():
            yield from self.bind_MCPs_from_Definition(definition)

    def bind_MCPs_from_Definition(
        self, ctx: ThriftParser.DefinitionContext
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        if ctx.struct_():
            yield from self.bind_MCPs_from_struct_(ctx.struct_())
        elif ctx.union_():
            yield from self.bind_MCPs_from_union_(ctx.union_())
        elif ctx.enum_rule():
            yield from self.bind_MCPs_from_enum_rule(ctx.enum_rule())
        elif ctx.service():
            pass
        elif ctx.exception_():
            yield from self.bind_MCPs_from_exception_(ctx.exception_())
        elif ctx.typedef_():
            pass
        elif ctx.const_rule():
            pass
        else:
            raise NotImplementedError()

    def bind_MCPs_from_exception_(
        self, ctx: ThriftParser.Exception_Context
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        if ctx.type_annotations():
            annotations = [
                self.bind_Annotation_from_type_annotation(type_annotation)
                for type_annotation in ctx.type_annotations().type_annotation()
            ]
        else:
            annotations = None

        name = ctx.IDENTIFIER().getText()
        result = cast(Resolved, self.context.resolve(name))
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
                platformSchema=ThriftSchema(
                    filename=self.context.get_filename(),
                    rawSchema=ctx.getText(),
                    fields=[
                        self.bind_ThriftField_from_field(field) for field in ctx.field()
                    ],
                    annotations=annotations,
                    namespace_=result.namespaces,
                ),
                fields=[
                    self.bind_SchemaField_from_field(field) for field in ctx.field()
                ],
            ),
        )

    def bind_MCPs_from_struct_(
        self, ctx: ThriftParser.Struct_Context
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        if ctx.type_annotations():
            annotations = [
                self.bind_Annotation_from_type_annotation(type_annotation)
                for type_annotation in ctx.type_annotations().type_annotation()
            ]
        else:
            annotations = None

        name = ctx.IDENTIFIER().getText()
        result = cast(Resolved, self.context.resolve(name))
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
                platformSchema=ThriftSchema(
                    filename=self.context.get_filename(),
                    rawSchema=ctx.getText(),
                    fields=[
                        self.bind_ThriftField_from_field(field) for field in ctx.field()
                    ],
                    annotations=annotations,
                    namespace_=result.namespaces,
                ),
                fields=[
                    self.bind_SchemaField_from_field(field) for field in ctx.field()
                ],
            ),
        )

    def bind_MCPs_from_union_(
        self, ctx: ThriftParser.Union_Context
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        if ctx.type_annotations():
            annotations = [
                self.bind_Annotation_from_type_annotation(type_annotation)
                for type_annotation in ctx.type_annotations().type_annotation()
            ]
        else:
            annotations = None

        name = ctx.IDENTIFIER().getText()
        result = cast(Resolved, self.context.resolve(name))
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
                platformSchema=ThriftSchema(
                    filename=self.context.get_filename(),
                    rawSchema=ctx.getText(),
                    fields=[
                        self.bind_ThriftField_from_field(field) for field in ctx.field()
                    ],
                    annotations=annotations,
                    namespace_=result.namespaces,
                ),
                fields=[
                    self.bind_SchemaField_from_field(field) for field in ctx.field()
                ],
            ),
        )

    def bind_MCPs_from_enum_rule(
        self, ctx: ThriftParser.Enum_ruleContext
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        if ctx.type_annotations():
            annotations = [
                self.bind_Annotation_from_type_annotation(type_annotation)
                for type_annotation in ctx.type_annotations().type_annotation()
            ]
        else:
            annotations = None

        name = ctx.IDENTIFIER().getText()
        result = cast(Resolved, self.context.resolve(name))
        yield MetadataChangeProposalWrapper(
            entityType="thriftEnumType",
            changeType=ChangeType.UPSERT,
            aspectName="thriftEnumTypeKey",
            entityUrn=result.urn,
            aspect=ThriftEnumTypeKey(name=name),
        )
        yield MetadataChangeProposalWrapper(
            entityType="thriftEnumType",
            changeType=ChangeType.UPSERT,
            aspectName="thriftEnumTypeProperties",
            entityUrn=result.urn,
            aspect=ThriftEnumTypeProperties(
                items=[
                    self.bind_ThriftEnumItem_from_enum_field(enum_field)
                    for enum_field in ctx.enum_field()
                ],
                annotations=annotations,
                namespace_=result.namespaces,
            ),
        )

    def bind_ThriftEnumItem_from_enum_field(
        self, ctx: ThriftParser.Enum_fieldContext
    ) -> ThriftEnumItem:
        if ctx.type_annotations():
            annotations = [
                self.bind_Annotation_from_type_annotation(type_annotation)
                for type_annotation in ctx.type_annotations().type_annotation()
            ]
        else:
            annotations = None
        return ThriftEnumItem(
            key=ctx.IDENTIFIER().getText(),
            value=cast(int, self.bind_value_from_integer(ctx.integer(), int))
            if ctx.integer()
            else None,
            annotations=annotations,
        )

    def bind_Annotation_from_type_annotation(
        self, ctx: ThriftParser.Type_annotationContext
    ) -> Annotation:
        key = ctx.IDENTIFIER().getText()
        if not ctx.annotation_value():
            value = None
        else:
            value = self.bind_annotation_value_from_annotation_value(
                ctx.annotation_value()
            )

        return Annotation(key=key, value=value)

    def bind_annotation_value_from_annotation_value(
        self, ctx: ThriftParser.Annotation_valueContext
    ) -> Union[int, str]:
        if ctx.integer():
            return int(ctx.integer().getText())
        elif ctx.LITERAL():
            return get_literal_text(ctx.LITERAL())
        else:
            raise NotImplementedError()

    def bind_SchemaField_from_field(
        self, ctx: ThriftParser.FieldContext
    ) -> SchemaField:
        return SchemaField(
            fieldPath=ctx.IDENTIFIER().getText(),
            type=self.bind_SchemaFieldDataType_from_field_type(ctx.field_type()),
            nativeDataType=self.bind_native_data_type_from_field_type(ctx.field_type()),
        )

    def bind_native_data_type_from_field_type(
        self, ctx: ThriftParser.Field_typeContext
    ) -> str:
        if ctx.base_type():
            return self.bind_native_data_type_from_base_type(ctx.base_type())
        elif ctx.IDENTIFIER():
            return self.bind_native_data_type_from_IDENTIFIER(ctx.IDENTIFIER())
        elif ctx.container_type():
            return self.bind_native_data_type_from_container_type(ctx.container_type())
        else:
            raise NotImplementedError()

    def bind_native_data_type_from_base_type(
        self, ctx: ThriftParser.Base_typeContext
    ) -> str:
        return ctx.real_base_type().getText()

    def bind_native_data_type_from_IDENTIFIER(
        self, ctx: ThriftParser.IDENTIFIER
    ) -> str:
        qualified_name = ctx.getText()
        return self.bind_native_data_type_from_qualified_name(qualified_name)

    def bind_native_data_type_from_qualified_name(self, qualified_name: str) -> str:
        result = self.context.resolve(qualified_name)

        func = {
            ResolvedEnum: self.bind_native_data_type_from_Resolved,
            ResolvedStruct: self.bind_native_data_type_from_Resolved,
            ResolvedUnion: self.bind_native_data_type_from_Resolved,
            ResolvedException: self.bind_native_data_type_from_Resolved,
            Redirect: self.bind_native_data_type_from_Redirect,
            UnresolvedFieldType: self.bind_native_data_type_from_UnresolvedFieldType,
        }.get(type(result))
        if func is None:
            raise NotImplementedError()

        return func(result)  # type: ignore [operator, Cannot call function of unknown type]

    def bind_native_data_type_from_Resolved(self, result: Resolved) -> str:
        return result.native_data_type

    def bind_native_data_type_from_Redirect(self, result: Redirect) -> str:  # type: ignore [return, Missing return statement]
        with BindingContextPusher(
            self,
            NamingBindingContext(
                self.context, filename=result.filename, thrift_paths=result.thrift_path
            ),
        ):
            return self.bind_native_data_type_from_qualified_name(result.qualified_name)

    def bind_native_data_type_from_UnresolvedFieldType(
        self, result: UnresolvedFieldType
    ) -> str:
        return self.bind_native_data_type_from_field_type(result.ctx)

    def bind_native_data_type_from_container_type(
        self, ctx: ThriftParser.Container_typeContext
    ) -> str:
        if ctx.list_type():
            return self.bind_native_data_type_from_list_type(ctx.list_type())
        elif ctx.map_type():
            return self.bind_native_data_type_from_map_type(ctx.map_type())
        elif ctx.set_type():
            return self.bind_native_data_type_from_set_type(ctx.set_type())
        else:
            raise NotImplementedError()

    def bind_native_data_type_from_list_type(
        self, ctx: ThriftParser.List_typeContext
    ) -> str:
        return f"list<{self.bind_native_data_type_from_field_type(ctx.field_type())}>"

    def bind_native_data_type_from_set_type(
        self, ctx: ThriftParser.Set_typeContext
    ) -> str:
        return f"set<{self.bind_native_data_type_from_field_type(ctx.field_type())}>"

    def bind_native_data_type_from_map_type(
        self, ctx: ThriftParser.Map_typeContext
    ) -> str:
        return f"map<{self.bind_native_data_type_from_field_type(ctx.field_type()[0])},{self.bind_native_data_type_from_field_type(ctx.field_type()[1])}>"

    def bind_Type_from_field_type(
        self, ctx: ThriftParser.Field_typeContext
    ) -> Optional[Type]:
        if ctx.base_type():
            return self.bind_Type_from_base_type(ctx.base_type())
        elif ctx.IDENTIFIER():
            return self.bind_Type_from_IDENTIFIER(ctx.IDENTIFIER())
        elif ctx.container_type():
            return self.bind_Type_from_container_type(ctx.container_type())
        else:
            raise NotImplementedError()

    def bind_Type_from_base_type(self, ctx: ThriftParser.Base_typeContext) -> Type:
        return {
            "bool": bool,
            "byte": int,
            "i16": int,
            "i32": int,
            "i64": int,
            "double": float,
            "string": str,
        }[ctx.real_base_type().getText()]

    def bind_Type_from_IDENTIFIER(self, ctx: ThriftParser.IDENTIFIER) -> Type:
        qualified_name = ctx.getText()
        return self.bind_Type_from_qualified_name(qualified_name)

    def bind_Type_from_qualified_name(self, qualified_name: str) -> Type:
        result = self.context.resolve(qualified_name)

        func = {
            ResolvedEnum: lambda _: int,
            ResolvedUnion: lambda _: None,  # TODO 29: Container container = { "mesos": {} }
            ResolvedStruct: lambda _: None,  # TODO 4: optional AdditionalParams additionalParams = {};
            Redirect: self.bind_Type_from_Redirect,
            UnresolvedFieldType: self.bind_Type_from_UnresolvedFieldType,
        }.get(type(result))
        if func is None:
            raise NotImplementedError()

        return func(result)  # type: ignore [operator, Cannot call function of unknown type]

    def bind_Type_from_Redirect(self, result: Redirect) -> Type:  # type: ignore [return, Missing return statement]
        with BindingContextPusher(
            self,
            NamingBindingContext(
                self.context, filename=result.filename, thrift_paths=result.thrift_path
            ),
        ):
            return self.bind_Type_from_qualified_name(result.qualified_name)

    def bind_Type_from_UnresolvedFieldType(
        self, result: UnresolvedFieldType
    ) -> Optional[Type]:
        return self.bind_Type_from_field_type(result.ctx)

    def bind_Type_from_container_type(
        self, ctx: ThriftParser.Container_typeContext
    ) -> Type:
        if ctx.list_type():
            return list
        elif ctx.map_type():
            return dict
        elif ctx.set_type():
            return set
        else:
            raise NotImplementedError()

    def bind_value_from_const_value(
        self, ctx: ThriftParser.Const_valueContext, type_: Type
    ) -> Union[int, str, bool, float, None]:
        if ctx.integer() and type_ in {int, bool, float}:
            return self.bind_value_from_integer(ctx.integer(), type_)
        elif ctx.DOUBLE() and type_ == float:
            return self.bind_value_from_DOUBLE(ctx.DOUBLE())
        elif ctx.LITERAL() and type_ == str:
            return self.bind_value_from_LITERAL(ctx.LITERAL())
        elif ctx.IDENTIFIER():
            return self.bind_value_from_IDENTIFIER(ctx.IDENTIFIER(), type_)
        elif ctx.const_list():
            # TODO 1: list<i64> my_list = [1,2,3]
            return None
        elif ctx.const_map():
            # TODO
            return None
        else:
            raise NotImplementedError()

    def bind_value_from_DOUBLE(self, ctx: ThriftParser.IDENTIFIER) -> float:
        return float(ctx.getText())

    def bind_value_from_LITERAL(self, ctx: ThriftParser.LITERAL) -> str:
        return get_literal_text(ctx)

    def bind_value_from_IDENTIFIER(
        self, ctx: ThriftParser.IDENTIFIER, type_: Type
    ) -> Union[int, str, bool, float, None]:
        qualified_name = ctx.getText()
        return self.bind_value_from_qualified_name(qualified_name, type_)

    def bind_value_from_qualified_name(
        self, qualified_name: str, type_: Type
    ) -> Union[int, str, bool, float, None]:
        result = self.context.resolve(qualified_name)

        func = {
            ResolvedConstValue: lambda x, _: cast(ResolvedConstValue, x).value,
            Redirect: self.bind_value_from_Redirect,  # type: ignore [dict-item]
            UnresolvedConstValue: self.bind_value_from_UnresolvedConstValue,
        }.get(type(result), None)
        if func is not None and result is not None:
            return func(result, type_)  # type: ignore [arg-type]
        else:
            # TODO failed to resolve
            return None

    def bind_value_from_Redirect(  # type: ignore [return, Missing return statement]
        self, result: Redirect, type_: Type
    ) -> Union[int, str, bool, float, None]:
        assert isinstance(result, Redirect)
        with BindingContextPusher(
            self,
            NamingBindingContext(
                self.context, filename=result.filename, thrift_paths=result.thrift_path
            ),
        ):
            return self.bind_value_from_qualified_name(result.qualified_name, type_)

    def bind_value_from_UnresolvedConstValue(
        self, result: UnresolvedConstValue, type_: Type
    ) -> Union[int, str, bool, float, None]:
        return self.bind_value_from_const_value(result.ctx, type_)

    def bind_value_from_integer(
        self, ctx: ThriftParser.IntegerContext, type_: Type
    ) -> Union[int, bool, float]:
        if ctx.INTEGER():
            result = int(ctx.INTEGER().getText())
        elif ctx.HEX_INTEGER():
            result = int(ctx.HEX_INTEGER().getText(), 16)
        else:
            raise NotImplementedError()
        return {int: int, bool: bool, float: float}[type_](result)

    def bind_ThriftField_from_field(
        self, ctx: ThriftParser.FieldContext
    ) -> ThriftField:
        if ctx.type_annotations():
            annotations = [
                self.bind_Annotation_from_type_annotation(type_annotation)
                for type_annotation in ctx.type_annotations().type_annotation()
            ]
        else:
            annotations = None
        if ctx.const_value():
            type_ = self.bind_Type_from_field_type(ctx.field_type())
            # TODO type_ could be union, not implemented yet.
            if type_ is not None:
                default = self.bind_value_from_const_value(ctx.const_value(), type_)
            else:
                default = None
        else:
            default = None
        m = re.match(r"(\d+)\:", ctx.field_id().getText())
        if m is None:
            raise ValueError()
        else:
            index = int(m.group(1))

        return ThriftField(
            name=ctx.IDENTIFIER().getText(),
            index=index,
            hyperType=list(self.bind_HyperType_from_field_type(ctx.field_type())),
            default=default,
            annotations=annotations,
        )

    def bind_HyperType_from_field_type(
        self, ctx: ThriftParser.Field_typeContext
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        if ctx.base_type():
            yield from self.bind_HyperType_from_base_type(ctx.base_type())
        elif ctx.container_type():
            yield from self.bind_HyperType_from_container_type(ctx.container_type())
        elif ctx.IDENTIFIER():
            yield from self.bind_HyperType_from_IDENTIFIER(ctx.IDENTIFIER())

    def bind_HyperType_from_base_type(
        self, ctx: ThriftParser.Base_typeContext
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        yield HyperTypeTextToken(text=ctx.real_base_type().getText())

    def bind_HyperType_from_IDENTIFIER(
        self, ctx: ThriftParser.IDENTIFIER
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        qualified_name = ctx.getText()
        yield from self.bind_HyperType_from_qualified_name(qualified_name)

    def bind_HyperType_from_qualified_name(
        self, qualified_name: str
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        result = self.context.resolve(qualified_name)

        func = {
            ResolvedEnum: self.bind_HyperType_from_Resolved,
            ResolvedStruct: self.bind_HyperType_from_Resolved,
            ResolvedUnion: self.bind_HyperType_from_Resolved,
            ResolvedException: self.bind_HyperType_from_Resolved,
            Redirect: self.bind_HyperType_from_Redirect,
            UnresolvedFieldType: self.bind_HyperType_from_UnresolvedFieldType,
        }.get(type(result))
        if func is None:
            raise NotImplementedError()

        yield from func(result)  # type: ignore [operator, Cannot call function of unknown type]

    def bind_HyperType_from_Redirect(
        self, result: Redirect
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        with BindingContextPusher(
            self,
            NamingBindingContext(
                self.context, filename=result.filename, thrift_paths=result.thrift_path
            ),
        ):
            yield from self.bind_HyperType_from_qualified_name(result.qualified_name)

    def bind_HyperType_from_UnresolvedFieldType(
        self, result: UnresolvedFieldType
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        yield from self.bind_HyperType_from_field_type(result.ctx)

    def bind_HyperType_from_Resolved(
        self, result: Resolved
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        yield HyperTypeUrnToken(result.native_data_type, result.urn)

    def bind_HyperType_from_container_type(
        self, ctx: ThriftParser.Container_typeContext
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        if ctx.list_type():
            return self.bind_HyperType_from_list_type(ctx.list_type())
        elif ctx.map_type():
            return self.bind_HyperType_from_map_type(ctx.map_type())
        elif ctx.set_type():
            return self.bind_HyperType_from_set_type(ctx.set_type())
        else:
            raise NotImplementedError()

    def bind_HyperType_from_list_type(
        self, ctx: ThriftParser.List_typeContext
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        yield HyperTypeTextToken("list<")
        yield from self.bind_HyperType_from_field_type(ctx.field_type())
        yield HyperTypeTextToken(">")

    def bind_HyperType_from_set_type(
        self, ctx: ThriftParser.Set_typeContext
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        yield HyperTypeTextToken("set<")
        yield from self.bind_HyperType_from_field_type(ctx.field_type())
        yield HyperTypeTextToken(">")

    def bind_HyperType_from_map_type(
        self, ctx: ThriftParser.Map_typeContext
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        yield HyperTypeTextToken("map<")
        yield from self.bind_HyperType_from_field_type(ctx.field_type()[0])
        yield HyperTypeTextToken(",")
        yield from self.bind_HyperType_from_field_type(ctx.field_type()[1])
        yield HyperTypeTextToken(">")

    def bind_SchemaFieldDataType_from_field_type(
        self, ctx: ThriftParser.Field_typeContext
    ) -> SchemaFieldDataType:
        if ctx.base_type():
            return self.bind_SchemaFieldDataType_from_base_type(ctx.base_type())
        elif ctx.container_type():
            return self.bind_SchemaFieldDataType_from_container_type(
                ctx.container_type()
            )
        elif ctx.IDENTIFIER():
            return self.bind_SchemaFieldDataType_from_IDENTIFIER(ctx.IDENTIFIER())

        else:
            raise ValueError()

    def bind_SchemaFieldDataType_from_IDENTIFIER(
        self, ctx: ThriftParser.IDENTIFIER
    ) -> SchemaFieldDataType:
        qualified_name = ctx.getText()
        return self.bind_SchemaFieldDataType_from_qualified_name(qualified_name)

    def bind_SchemaFieldDataType_from_qualified_name(
        self, qualified_name: str
    ) -> SchemaFieldDataType:
        result = self.context.resolve(qualified_name)
        assert result is not None

        func = {
            ResolvedEnum: lambda _: SchemaFieldDataType(EnumType()),
            ResolvedStruct: lambda _: SchemaFieldDataType(RecordType()),
            ResolvedUnion: self.bind_SchemaFieldDataType_from_ResolvedUnion,  # type: ignore [dict-item]
            ResolvedException: lambda _: SchemaFieldDataType(RecordType()),
            Redirect: self.bind_SchemaFieldDataType_from_Redirect,  # type: ignore [dict-item]
            UnresolvedFieldType: self.bind_SchemaFieldDataType_from_UnresolvedFieldType,
        }.get(type(result))
        if func is None:
            raise NotImplementedError()

        return func(result)  # type: ignore [arg-type]

    def bind_SchemaFieldDataType_from_ResolvedUnion(
        self, result: ResolvedUnion
    ) -> SchemaFieldDataType:
        return SchemaFieldDataType(UnionType(result.subtypes))

    def bind_SchemaFieldDataType_from_Redirect(  # type: ignore [return, Missing return statement]
        self, result: Redirect
    ) -> SchemaFieldDataType:
        with BindingContextPusher(
            self,
            NamingBindingContext(
                self.context, filename=result.filename, thrift_paths=result.thrift_path
            ),
        ):
            return self.bind_SchemaFieldDataType_from_qualified_name(
                result.qualified_name
            )

    def bind_SchemaFieldDataType_from_UnresolvedFieldType(
        self, result: UnresolvedFieldType
    ) -> SchemaFieldDataType:
        return self.bind_SchemaFieldDataType_from_field_type(result.ctx)

    def bind_SchemaFieldDataType_from_base_type(
        self, ctx: ThriftParser.Base_typeContext
    ) -> SchemaFieldDataType:
        return self.bind_SchemaFieldDataType_from_real_base_type(ctx.real_base_type())

    def bind_SchemaFieldDataType_from_container_type(
        self, ctx: ThriftParser.Container_typeContext
    ) -> SchemaFieldDataType:
        if ctx.list_type():
            return self.bind_SchemaFieldDataType_from_list_type(ctx.list_type())
        elif ctx.map_type():
            return self.bind_SchemaFieldDataType_from_map_type(ctx.map_type())
        elif ctx.set_type():
            return self.bind_SchemaFieldDataType_from_set_type(ctx.set_type())
        else:
            raise NotImplementedError()

    def bind_SchemaFieldDataType_from_map_type(
        self, ctx: ThriftParser.Map_typeContext
    ) -> SchemaFieldDataType:

        return SchemaFieldDataType(
            MapType(
                self.bind_native_data_type_from_field_type(ctx.field_type()[0]),
                self.bind_native_data_type_from_field_type(ctx.field_type()[1]),
            )
        )

    def bind_SchemaFieldDataType_from_list_type(
        self, ctx: ThriftParser.List_typeContext
    ) -> SchemaFieldDataType:
        return SchemaFieldDataType(
            ArrayType([self.bind_native_data_type_from_field_type(ctx.field_type())])
        )

    def bind_SchemaFieldDataType_from_set_type(
        self, ctx: ThriftParser.Set_typeContext
    ) -> SchemaFieldDataType:
        return SchemaFieldDataType(
            ArrayType([self.bind_native_data_type_from_field_type(ctx.field_type())])
        )

    def bind_SchemaFieldDataType_from_real_base_type(
        self, ctx: ThriftParser.Real_base_typeContext
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
            raise NotImplementedError()


@dataclass
class ThriftSource(Source):
    config: ThriftSourceConfig
    report: SourceReport = field(default_factory=SourceReport)

    @classmethod
    def create(cls, config_dict, ctx):
        config = ThriftSourceConfig.parse_obj(config_dict)
        return cls(ctx, config)

    def parse(
        self, filename: str, thrift_paths: Optional[Tuple[str, ...]]
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        if os.path.isfile(filename) and os.path.splitext(filename)[1] == ".thrift":
            print(f"Processing {filename}")
            tree = parse(filename)
            context = NamingBindingContext(None, filename, thrift_paths=thrift_paths)
            # evaluator
            yield from Binder(context).bind_MCPs_from_Document(tree)
        elif os.path.isdir(filename):
            for f in os.listdir(filename):
                yield from self.parse(os.path.join(filename, f), thrift_paths)

    def get_workunits(self) -> Iterable[Union[MetadataWorkUnit, UsageStatsWorkUnit]]:
        for i, obj in enumerate(
            self.parse(self.config.filename, self.config.thrift_paths)
        ):
            wu = MetadataWorkUnit(f"file://{self.config.filename}:{i}", mcp=obj)
            self.report.report_workunit(wu)
            yield wu

    def get_report(self):
        return self.report

    def close(self):
        pass
