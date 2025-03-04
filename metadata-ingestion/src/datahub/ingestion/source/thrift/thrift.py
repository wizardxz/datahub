import os
import re
import time
from dataclasses import dataclass, field, replace
from functools import lru_cache, reduce
from typing import (
    Dict,
    Generator,
    Iterable,
    List,
    NewType,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)

from antlr4 import CommonTokenStream, InputStream, TerminalNode

from datahub.configuration.common import ConfigModel
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.ingestion.api.common import WorkUnit
from datahub.ingestion.api.source import Source, SourceReport
from datahub.ingestion.api.workunit import MetadataWorkUnit, UsageStatsWorkUnit
from datahub.ingestion.source.thrift.parse_tools import (  # type: ignore
    thriftLexer,
    thriftParser,
    thriftVisitor,
)
from datahub.metadata.com.linkedin.pegasus2avro.common import (
    AuditStamp,
    GlossaryTermAssociation,
    GlossaryTerms,
)
from datahub.metadata.com.linkedin.pegasus2avro.events.metadata import ChangeType
from datahub.metadata.com.linkedin.pegasus2avro.schema import (
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
    ThriftAnnotation,
    ThriftEnumItem,
    ThriftEnumKey,
    ThriftEnumProperties,
    ThriftField,
    ThriftSchema,
    UnionType,
)


def get_list_item_type(type_: Type) -> Type:
    return type_.__args__[0]


def get_map_key_type(type_: Type) -> Type:
    return type_.__args__[0]


def get_map_value_type(type_: Type) -> Type:
    return type_.__args__[1]


def get_enum_urn(java_namespace: Optional[str], name: str) -> str:
    return f"urn:li:thriftEnum:{get_qualified_name(name, java_namespace)}"


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


def get_literal_text(ctx: TerminalNode) -> str:
    literal = ctx.getText()
    m = re.match(r"(\".*\")|(\'.*\')", literal)
    if m is None:
        raise ValueError(f"{literal} is not a valid include")
    return literal[1:-1]


class ThriftSourceConfig(ConfigModel):
    filename: str
    thrift_paths: Optional[Tuple[str, ...]] = None
    explicit: bool = False


@lru_cache()
def parse(filename: str) -> thriftParser.DocumentContext:
    with open(filename) as text_file:
        # lexer

        lexer = thriftLexer(InputStream(text_file.read()))
        stream = CommonTokenStream(lexer)
        # parser
        parser = thriftParser(stream)

        tree = parser.document()
        return tree


@dataclass(frozen=True)
class TypeResolveResult:
    pass


@dataclass(frozen=True)
class TypeResolved(TypeResolveResult):
    urn: str
    native_data_type: str
    namespaces: Dict[str, str]


@dataclass(frozen=True)
class ResolvedEnum(TypeResolved):
    pass


@dataclass(frozen=True)
class ResolvedStruct(TypeResolved):
    pass


@dataclass(frozen=True)
class ResolvedUnion(TypeResolved):
    subtypes: List[str]


@dataclass(frozen=True)
class ResolvedException(TypeResolved):
    pass


@dataclass(frozen=True)
class TypeUnresolved(TypeResolveResult):
    pass


@dataclass(frozen=True)
class RedirectForType(TypeUnresolved):
    filename: str
    thrift_path: Optional[Tuple[str, ...]]
    qualified_name: str


@dataclass(frozen=True)
class ValueResolveResult:
    pass


@dataclass(frozen=True)
class UnresolvedFieldType(TypeUnresolved):
    ctx: thriftParser.Field_typeContext


@dataclass(frozen=True)
class ValueUnresolved(ValueResolveResult):
    pass


@dataclass(frozen=True)
class RedirectForValue(ValueUnresolved):
    filename: str
    thrift_path: Optional[Tuple[str, ...]]
    qualified_name: str


@dataclass(frozen=True)
class UnresolvedConstValue(ValueUnresolved):
    ctx: thriftParser.Const_valueContext


@dataclass(frozen=True)
class ValueResolved(ValueResolveResult):
    type_: Type
    value: Union[int, str, bool, float]


@dataclass(frozen=True)
class NameResolver:
    namespaces: Dict[str, str] = field(default_factory=dict)
    type_data: Dict[str, TypeResolveResult] = field(default_factory=dict)
    value_data: Dict[str, ValueResolveResult] = field(default_factory=dict)
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
            type_data={**self.type_data, **other.type_data},
            value_data={**self.value_data, **other.value_data},
            includes={**self.includes, **other.includes},
        )

    def add_enum(self, name: str) -> "NameResolver":
        return replace(
            self,
            type_data={
                **self.type_data,
                name: ResolvedEnum(
                    get_enum_urn(self.java_namespace, name), name, self.namespaces
                ),
            },
        )

    def add_struct(self, name: str) -> "NameResolver":
        return replace(
            self,
            type_data={
                **self.type_data,
                name: ResolvedStruct(
                    get_dataset_urn(self.java_namespace, name), name, self.namespaces
                ),
            },
        )

    def add_union(self, name: str, subtypes: List[str]) -> "NameResolver":
        return replace(
            self,
            type_data={
                **self.type_data,
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
        ctx: thriftParser.Field_typeContext,
    ) -> "NameResolver":
        return replace(
            self,
            type_data={**self.type_data, name: UnresolvedFieldType(ctx)},
        )

    def add_const_value(
        self,
        name: str,
        ctx: thriftParser.Const_valueContext,
    ) -> "NameResolver":
        return replace(
            self,
            value_data={**self.value_data, name: UnresolvedConstValue(ctx)},
        )

    def add_include(self, qualifier: str, filename: str) -> "NameResolver":
        return replace(self, includes={**self.includes, qualifier: filename})

    def add_namespace(self, language: str, namespace: str) -> "NameResolver":
        return replace(self, namespaces={**self.namespaces, language: namespace})

    def get_type(self, name: str) -> Optional[TypeResolveResult]:
        return self.type_data.get(name)

    def get_value(self, name: str) -> Optional[ValueResolveResult]:
        return self.value_data.get(name)


@dataclass(frozen=True)
class GetHeader(thriftVisitor):
    filename: str
    thrift_paths: Tuple[str, ...] = field(default_factory=tuple)

    def visitDocument(self, ctx: thriftParser.DocumentContext) -> NameResolver:
        return reduce(
            lambda result, current: result.merge(self.visitHeader(current)),
            ctx.header(),
            NameResolver(),
        )

    def visitHeader(self, ctx: thriftParser.HeaderContext) -> NameResolver:
        if ctx.include_():
            return self.visitInclude_(ctx.include_())
        elif ctx.namespace_():
            return self.visitNamespace_(ctx.namespace_())
        else:
            return NameResolver()

    def visitNamespace_(self, ctx: thriftParser.Namespace_Context) -> NameResolver:
        func = {
            thriftParser.StarNamespaceContext: self.visitStarNamespace,  # type: ignore [dict-item, incompatible type]
            thriftParser.ExplicitNamespaceContext: self.visitExplicitNamespace,  # type: ignore [dict-item, incompatible type]
            thriftParser.CppNamespaceContext: self.visitCppNamespace,  # type: ignore [dict-item, incompatible type]
            thriftParser.PhpNamespaceContext: self.visitPhpNamespace,  # type: ignore [dict-item, incompatible type]
        }.get(type(ctx), None)
        if func is not None:
            return func(ctx)
        else:
            return NameResolver()

    def visitStarNamespace(
        self, ctx: thriftParser.StarNamespaceContext
    ) -> NameResolver:
        if ctx.IDENTIFIER():
            return NameResolver().add_namespace("*", ctx.IDENTIFIER().getText())
        elif ctx.LITERAL():
            return NameResolver().add_namespace("*", get_literal_text(ctx.LITERAL()))
        else:
            raise NotImplementedError()

    def visitExplicitNamespace(
        self, ctx: thriftParser.ExplicitNamespaceContext
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

    def visitCppNamespace(self, ctx: thriftParser.CppNamespaceContext) -> NameResolver:
        return NameResolver().add_namespace("cpp", ctx.IDENTIFIER().getText())

    def visitPhpNamespace(self, ctx: thriftParser.PhpNamespaceContext) -> NameResolver:
        return NameResolver().add_namespace("php", ctx.IDENTIFIER().getText())

    def visitInclude_(self, ctx: thriftParser.Include_Context) -> NameResolver:
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


@lru_cache()
def get_header(filename: str, thrift_paths: List[str]) -> NameResolver:
    return GetHeader(filename, thrift_paths).visit(parse(filename))


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
            raise NotImplementedError(f"not support {ctx.getText()} yet.")

    def visitConst_rule(self, ctx: thriftParser.Const_ruleContext) -> NameResolver:
        return self.header.add_const_value(
            ctx.IDENTIFIER().getText(), ctx.const_value()
        )

    def visitException_(self, ctx: thriftParser.Exception_Context) -> NameResolver:
        return self.header.add_struct(ctx.IDENTIFIER().getText())

    def visitTypedef_(self, ctx: thriftParser.Typedef_Context) -> NameResolver:
        return self.header.add_typedef(ctx.IDENTIFIER().getText(), ctx.field_type())

    def visitEnum_rule(self, ctx: thriftParser.Enum_ruleContext) -> NameResolver:
        return self.header.add_enum(ctx.IDENTIFIER().getText())

    def visitStruct_(self, ctx: thriftParser.Struct_Context) -> NameResolver:
        return self.header.add_struct(ctx.IDENTIFIER().getText())

    def visitUnion_(self, ctx: thriftParser.Union_Context) -> NameResolver:
        subtypes = [field.field_type().getText() for field in ctx.field()]
        return self.header.add_union(ctx.IDENTIFIER().getText(), subtypes)


@lru_cache()
def get_name_resolver(filename: str, thrift_paths: Tuple[str, ...]) -> NameResolver:
    tree = parse(filename)
    header = GetHeader(filename, thrift_paths).visit(tree)
    return GetNameResolver(header).visit(tree)


SkipValidationType = NewType("SkipValidationType", str)


@dataclass(frozen=True)
class Binder:
    filename: str
    thrift_paths: Tuple[str, ...]
    name_resolver: NameResolver

    def resolve_type(self, qualified_name: str) -> Optional[TypeResolveResult]:
        qualifier, name = split_qualified_name(qualified_name)
        if qualifier is None:
            return self.name_resolver.get_type(name)
        else:
            if qualifier in self.name_resolver.includes:
                filename = self.name_resolver.includes[qualifier]
                return RedirectForType(filename, self.thrift_paths, name)
            else:
                raise RuntimeError(
                    f"The qualifier of {qualified_name} is not included."
                )

    def resolve_value(self, qualified_name: str) -> Optional[ValueResolveResult]:
        qualifier, name = split_qualified_name(qualified_name)
        if qualifier is None:
            return self.name_resolver.get_value(name)
        else:
            if qualifier in self.name_resolver.includes:
                filename = self.name_resolver.includes[qualifier]
                return RedirectForValue(filename, self.thrift_paths, name)
            elif isinstance(self.name_resolver.get_type(qualifier), ResolvedEnum):
                resolved_enum = cast(
                    ResolvedEnum, self.name_resolver.get_type(qualifier)
                )
                return ValueResolved(
                    type_=str,
                    value=qualified_name,
                )
            else:
                raise RuntimeError(
                    f"The qualifier of {qualified_name} is not included."
                )

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
            raise NotImplementedError(f"not support {ctx.getText()} yet")

    def bind_MCPs_from_exception_(
        self, ctx: thriftParser.Exception_Context
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        if ctx.type_annotations():
            annotations = [
                self.bind_Annotation_from_type_annotation(type_annotation)
                for type_annotation in ctx.type_annotations().type_annotation()
            ]
        else:
            annotations = None

        name = ctx.IDENTIFIER().getText()
        result = cast(TypeResolved, self.resolve_type(name))
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
                    filename=self.filename,
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

    def bind_MCPs_from_type_annotations(
        self, ctx: Optional[thriftParser.Type_annotationsContext], urn: str
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        if ctx is not None:
            for annotation in ctx.type_annotation():
                mcp = self.bind_MCP_from_annotation(annotation, urn)
                if mcp is not None:
                    yield mcp

    def bind_MCP_from_annotation(
        self, ctx: thriftParser.Type_annotationContext, urn: str
    ) -> Optional[MetadataChangeProposalWrapper]:
        key = ctx.IDENTIFIER().getText()
        if key == "datahub.terms":

            return MetadataChangeProposalWrapper(
                entityType="dataset",
                changeType=ChangeType.UPSERT,
                aspectName="glossaryTerms",
                entityUrn=urn,
                aspect=self.bind_GlossaryTerms_from_annotation_value(
                    ctx.annotation_value()
                ),
            )
        return None

    def bind_GlossaryTerms_from_annotation_value(
        self, ctx: thriftParser.Annotation_valueContext
    ) -> GlossaryTerms:

        terms = get_literal_text(ctx.LITERAL()).split(",")
        return GlossaryTerms(
            terms=[
                GlossaryTermAssociation(urn=f"urn:li:glossaryTerm:{term.strip()}")
                for term in terms
            ],
            auditStamp=AuditStamp(
                time=int(time.time() * 1000), actor="urn:li:corpuser:datahub"
            ),
        )

    def bind_MCPs_from_struct_(
        self, ctx: thriftParser.Struct_Context
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        if ctx.type_annotations():
            annotations = [
                self.bind_Annotation_from_type_annotation(type_annotation)
                for type_annotation in ctx.type_annotations().type_annotation()
            ]
        else:
            annotations = None

        name = ctx.IDENTIFIER().getText()
        result = cast(TypeResolved, self.resolve_type(name))
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
                    filename=self.filename,
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
        yield from self.bind_MCPs_from_type_annotations(
            ctx.type_annotations(), result.urn
        )

    def bind_MCPs_from_union_(
        self, ctx: thriftParser.Union_Context
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        if ctx.type_annotations():
            annotations = [
                self.bind_Annotation_from_type_annotation(type_annotation)
                for type_annotation in ctx.type_annotations().type_annotation()
            ]
        else:
            annotations = None

        name = ctx.IDENTIFIER().getText()
        result = cast(TypeResolved, self.resolve_type(name))
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
                    filename=self.filename,
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
        yield from self.bind_MCPs_from_type_annotations(
            ctx.type_annotations(), result.urn
        )

    def bind_MCPs_from_enum_rule(
        self, ctx: thriftParser.Enum_ruleContext
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        if ctx.type_annotations():
            annotations = [
                self.bind_Annotation_from_type_annotation(type_annotation)
                for type_annotation in ctx.type_annotations().type_annotation()
            ]
        else:
            annotations = None

        name = ctx.IDENTIFIER().getText()
        result = cast(TypeResolved, self.resolve_type(name))
        yield MetadataChangeProposalWrapper(
            entityType="thriftEnum",
            changeType=ChangeType.UPSERT,
            aspectName="thriftEnumKey",
            entityUrn=result.urn,
            aspect=ThriftEnumKey(name=name),
        )
        yield MetadataChangeProposalWrapper(
            entityType="thriftEnum",
            changeType=ChangeType.UPSERT,
            aspectName="thriftEnumProperties",
            entityUrn=result.urn,
            aspect=ThriftEnumProperties(
                items=[
                    self.bind_ThriftEnumItem_from_enum_field(enum_field)
                    for enum_field in ctx.enum_field()
                ],
                annotations=annotations,
                namespace_=result.namespaces,
            ),
        )

    def bind_ThriftEnumItem_from_enum_field(
        self, ctx: thriftParser.Enum_fieldContext
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
        self, ctx: thriftParser.Type_annotationContext
    ) -> ThriftAnnotation:
        key = ctx.IDENTIFIER().getText()
        if not ctx.annotation_value():
            value = None
        else:
            value = self.bind_annotation_value_from_annotation_value(
                ctx.annotation_value()
            )

        return ThriftAnnotation(key=key, value=value)

    def bind_annotation_value_from_annotation_value(
        self, ctx: thriftParser.Annotation_valueContext
    ) -> Union[int, str]:
        if ctx.integer():
            return int(ctx.integer().getText())
        elif ctx.LITERAL():
            return get_literal_text(ctx.LITERAL())
        else:
            raise NotImplementedError(f"not support {ctx.getText()} yet.")

    def bind_SchemaField_from_field(
        self, ctx: thriftParser.FieldContext
    ) -> SchemaField:
        return SchemaField(
            fieldPath=ctx.IDENTIFIER().getText(),
            type=self.bind_SchemaFieldDataType_from_field_type(ctx.field_type()),
            nativeDataType=self.bind_native_data_type_from_field_type(ctx.field_type()),
            glossaryTerms=self.bind_GlossaryTerms_from_annotations(
                ctx.type_annotations()
            ),
        )

    def bind_GlossaryTerms_from_annotations(
        self, ctx: thriftParser.Type_annotationsContext
    ) -> Optional[GlossaryTerms]:
        if ctx is None:
            return None
        else:
            for annotation in ctx.type_annotation():

                if annotation.IDENTIFIER().getText() == "datahub.terms":

                    return self.bind_GlossaryTerms_from_annotation_value(
                        annotation.annotation_value()
                    )
            return None

    def bind_native_data_type_from_field_type(
        self, ctx: thriftParser.Field_typeContext
    ) -> str:
        if ctx.base_type():
            return self.bind_native_data_type_from_base_type(ctx.base_type())
        elif ctx.IDENTIFIER():
            return self.bind_native_data_type_from_IDENTIFIER(ctx.IDENTIFIER())
        elif ctx.container_type():
            return self.bind_native_data_type_from_container_type(ctx.container_type())
        else:
            raise NotImplementedError(f"not support {ctx.getText()} yet.")

    def bind_native_data_type_from_base_type(
        self, ctx: thriftParser.Base_typeContext
    ) -> str:
        return ctx.real_base_type().getText()

    def bind_native_data_type_from_IDENTIFIER(self, ctx: TerminalNode) -> str:
        qualified_name = ctx.getText()
        return self.bind_native_data_type_from_qualified_name(qualified_name)

    def bind_native_data_type_from_qualified_name(self, qualified_name: str) -> str:
        result = self.resolve_type(qualified_name)

        func = {
            ResolvedEnum: self.bind_native_data_type_from_Resolved,
            ResolvedStruct: self.bind_native_data_type_from_Resolved,
            ResolvedUnion: self.bind_native_data_type_from_Resolved,
            ResolvedException: self.bind_native_data_type_from_Resolved,
            RedirectForType: self.bind_native_data_type_from_Redirect,
            UnresolvedFieldType: self.bind_native_data_type_from_UnresolvedFieldType,
        }.get(type(result))
        if func is None:
            raise NotImplementedError(f"not support {type(result)} yet.")

        return func(result)  # type: ignore [operator, Cannot call function of unknown type]

    def bind_native_data_type_from_Resolved(self, result: TypeResolved) -> str:
        return result.native_data_type

    def bind_native_data_type_from_Redirect(self, result: RedirectForType) -> str:  # type: ignore [return, Missing return statement]
        binder = get_binder(result.filename, self.thrift_paths)
        return binder.bind_native_data_type_from_qualified_name(result.qualified_name)

    def bind_native_data_type_from_UnresolvedFieldType(
        self, result: UnresolvedFieldType
    ) -> str:
        return self.bind_native_data_type_from_field_type(result.ctx)

    def bind_native_data_type_from_container_type(
        self, ctx: thriftParser.Container_typeContext
    ) -> str:
        if ctx.list_type():
            return self.bind_native_data_type_from_list_type(ctx.list_type())
        elif ctx.map_type():
            return self.bind_native_data_type_from_map_type(ctx.map_type())
        elif ctx.set_type():
            return self.bind_native_data_type_from_set_type(ctx.set_type())
        else:
            raise NotImplementedError(f"not support {ctx.getText()} yet.")

    def bind_native_data_type_from_list_type(
        self, ctx: thriftParser.List_typeContext
    ) -> str:
        return f"list<{self.bind_native_data_type_from_field_type(ctx.field_type())}>"

    def bind_native_data_type_from_set_type(
        self, ctx: thriftParser.Set_typeContext
    ) -> str:
        return f"set<{self.bind_native_data_type_from_field_type(ctx.field_type())}>"

    def bind_native_data_type_from_map_type(
        self, ctx: thriftParser.Map_typeContext
    ) -> str:
        return f"map<{self.bind_native_data_type_from_field_type(ctx.field_type()[0])},{self.bind_native_data_type_from_field_type(ctx.field_type()[1])}>"

    def bind_Type_from_field_type(self, ctx: thriftParser.Field_typeContext) -> Type:
        if ctx.base_type():
            return self.bind_Type_from_base_type(ctx.base_type())
        elif ctx.IDENTIFIER():
            return self.bind_Type_from_IDENTIFIER(ctx.IDENTIFIER())
        elif ctx.container_type():
            return self.bind_Type_from_container_type(ctx.container_type())
        else:
            raise NotImplementedError(f"not support {ctx.getText()} yet.")

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

    def bind_Type_from_IDENTIFIER(self, ctx: TerminalNode) -> Type:
        qualified_name = ctx.getText()
        return self.bind_Type_from_qualified_name(qualified_name)

    def bind_Type_from_qualified_name(self, qualified_name: str) -> Type:
        result = self.resolve_type(qualified_name)

        func = {
            ResolvedEnum: lambda _: int,
            ResolvedUnion: lambda _: SkipValidationType,
            ResolvedStruct: lambda _: SkipValidationType,
            RedirectForType: self.bind_Type_from_Redirect,  # type: ignore
            UnresolvedFieldType: self.bind_Type_from_UnresolvedFieldType,
        }.get(type(result))
        if func is None:
            raise NotImplementedError(f"not support {type(result)} yet.")

        return func(result)  # type: ignore [operator, Cannot call function of unknown type, arg-type]

    def bind_Type_from_Redirect(self, result: RedirectForType) -> Type:  # type: ignore [return, Missing return statement]
        binder = get_binder(result.filename, self.thrift_paths)
        return binder.bind_Type_from_qualified_name(result.qualified_name)

    def bind_Type_from_UnresolvedFieldType(self, result: UnresolvedFieldType) -> Type:
        return self.bind_Type_from_field_type(result.ctx)

    def bind_Type_from_container_type(
        self, ctx: thriftParser.Container_typeContext
    ) -> Type:
        if ctx.list_type():
            return List[self.bind_Type_from_field_type(ctx.list_type().field_type())]  # type: ignore
        elif ctx.map_type():
            return Dict[  # type: ignore
                self.bind_Type_from_field_type(ctx.map_type().field_type()[0]),
                self.bind_Type_from_field_type(ctx.map_type().field_type()[1]),
            ]
        elif ctx.set_type():
            return Set[self.bind_Type_from_field_type(ctx.set_type().field_type())]  # type: ignore
        else:
            raise NotImplementedError(f"not support {ctx.getText()} yet.")

    def bind_value_from_const_value(
        self, ctx: thriftParser.Const_valueContext, type_: Type
    ) -> Union[int, str, bool, float]:
        if type_ == SkipValidationType:
            return ctx.getText()
        elif ctx.integer() and type_ in {int, bool, float}:
            return self.bind_value_from_integer(ctx.integer(), type_)
        elif ctx.DOUBLE() and type_ == float:
            return self.bind_value_from_DOUBLE(ctx.DOUBLE())
        elif ctx.LITERAL() and type_ == str:
            return self.bind_value_from_LITERAL(ctx.LITERAL())
        elif ctx.IDENTIFIER():
            return self.bind_value_from_IDENTIFIER(ctx.IDENTIFIER(), type_)
        elif ctx.const_list():
            return "".join(self.bind_value_from_const_list(ctx.const_list(), type_))
        elif ctx.const_map():
            return "".join(self.bind_value_from_const_map(ctx.const_map(), type_))
        else:
            raise NotImplementedError(f"not support {ctx.getText()} yet.")

    def _string_join(
        self, delimiter: str, parts: Iterable[str]
    ) -> Generator[str, None, None]:
        if delimiter == "":
            yield from parts
        else:
            first = True
            for part in parts:
                if first:
                    first = False
                else:
                    yield delimiter
                yield part

    def bind_value_from_const_list(
        self, ctx: thriftParser.Const_listContext, type_: Type
    ) -> Generator[str, None, None]:
        item_type = get_list_item_type(type_)
        yield "["
        yield from self._string_join(
            ", ",
            map(
                lambda value: str(self.bind_value_from_const_value(value, item_type)),
                ctx.const_value(),
            ),
        )
        yield "]"

    def bind_value_from_const_map(
        self, ctx: thriftParser.Const_mapContext, type_: Type
    ) -> Generator[str, None, None]:
        yield "{"
        yield from self._string_join(
            ", ",
            map(
                lambda entry: f"{self.bind_value_from_const_value(entry.const_value()[0], get_map_key_type(type_))}"
                ":"
                f"{self.bind_value_from_const_value(entry.const_value()[1], get_map_value_type(type_))}",
                ctx.const_map_entry(),
            ),
        )
        yield "}"

    def bind_value_from_DOUBLE(self, ctx: TerminalNode) -> float:
        return float(ctx.getText())

    def bind_value_from_LITERAL(self, ctx: TerminalNode) -> str:
        return get_literal_text(ctx)

    def bind_value_from_IDENTIFIER(
        self, ctx: TerminalNode, type_: Type
    ) -> Union[int, str, bool, float]:
        qualified_name = ctx.getText()
        return self.bind_value_from_qualified_name(qualified_name, type_)

    def bind_value_from_qualified_name(
        self, qualified_name: str, type_: Type
    ) -> Union[int, str, bool, float]:
        result = self.resolve_value(qualified_name)

        func = {
            ValueResolved: lambda x, _: cast(ValueResolved, x).value,
            RedirectForValue: self.bind_value_from_Redirect,  # type: ignore [dict-item]
            UnresolvedConstValue: self.bind_value_from_UnresolvedConstValue,
        }.get(type(result), None)
        if func is not None:
            return func(result, type_)  # type: ignore [operator]
        else:
            raise ValueError(f"{type(result)} is not handled.")

    def bind_value_from_Redirect(  # type: ignore [return, Missing return statement]
        self, result: RedirectForType, type_: Type
    ) -> Union[int, str, bool, float, None]:
        binder = get_binder(result.filename, self.thrift_paths)
        return binder.bind_value_from_qualified_name(result.qualified_name, type_)

    def bind_value_from_UnresolvedConstValue(
        self, result: UnresolvedConstValue, type_: Type
    ) -> Union[int, str, bool, float, None]:
        return self.bind_value_from_const_value(result.ctx, type_)

    def bind_value_from_integer(
        self, ctx: thriftParser.IntegerContext, type_: Type
    ) -> Union[int, bool, float]:
        if ctx.INTEGER():
            result = int(ctx.INTEGER().getText())
        elif ctx.HEX_INTEGER():
            result = int(ctx.HEX_INTEGER().getText(), 16)
        else:
            raise NotImplementedError(f"not support {ctx.getText()} yet.")
        return {int: int, bool: bool, float: float}[type_](result)

    def bind_ThriftField_from_field(
        self, ctx: thriftParser.FieldContext
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
        self, ctx: thriftParser.Field_typeContext
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        if ctx.base_type():
            yield from self.bind_HyperType_from_base_type(ctx.base_type())
        elif ctx.container_type():
            yield from self.bind_HyperType_from_container_type(ctx.container_type())
        elif ctx.IDENTIFIER():
            yield from self.bind_HyperType_from_IDENTIFIER(ctx.IDENTIFIER())

    def bind_HyperType_from_base_type(
        self, ctx: thriftParser.Base_typeContext
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        yield HyperTypeTextToken(text=ctx.real_base_type().getText())

    def bind_HyperType_from_IDENTIFIER(
        self, ctx: TerminalNode
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        qualified_name = ctx.getText()
        yield from self.bind_HyperType_from_qualified_name(qualified_name)

    def bind_HyperType_from_qualified_name(
        self, qualified_name: str
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        result = self.resolve_type(qualified_name)

        func = {
            ResolvedEnum: self.bind_HyperType_from_Resolved,
            ResolvedStruct: self.bind_HyperType_from_Resolved,
            ResolvedUnion: self.bind_HyperType_from_Resolved,
            ResolvedException: self.bind_HyperType_from_Resolved,
            RedirectForType: self.bind_HyperType_from_Redirect,
            UnresolvedFieldType: self.bind_HyperType_from_UnresolvedFieldType,
        }.get(type(result))
        if func is None:
            raise NotImplementedError(f"not support {type(result)} yet.")

        yield from func(result)  # type: ignore [operator, Cannot call function of unknown type]

    def bind_HyperType_from_Redirect(
        self, result: RedirectForType
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        binder = get_binder(result.filename, self.thrift_paths)
        yield from binder.bind_HyperType_from_qualified_name(result.qualified_name)

    def bind_HyperType_from_UnresolvedFieldType(
        self, result: UnresolvedFieldType
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        yield from self.bind_HyperType_from_field_type(result.ctx)

    def bind_HyperType_from_Resolved(
        self, result: TypeResolved
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        yield HyperTypeUrnToken(result.native_data_type, result.urn)

    def bind_HyperType_from_container_type(
        self, ctx: thriftParser.Container_typeContext
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        if ctx.list_type():
            return self.bind_HyperType_from_list_type(ctx.list_type())
        elif ctx.map_type():
            return self.bind_HyperType_from_map_type(ctx.map_type())
        elif ctx.set_type():
            return self.bind_HyperType_from_set_type(ctx.set_type())
        else:
            raise NotImplementedError(f"not support {ctx.getText()} yet.")

    def bind_HyperType_from_list_type(
        self, ctx: thriftParser.List_typeContext
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        yield HyperTypeTextToken("list<")
        yield from self.bind_HyperType_from_field_type(ctx.field_type())
        yield HyperTypeTextToken(">")

    def bind_HyperType_from_set_type(
        self, ctx: thriftParser.Set_typeContext
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        yield HyperTypeTextToken("set<")
        yield from self.bind_HyperType_from_field_type(ctx.field_type())
        yield HyperTypeTextToken(">")

    def bind_HyperType_from_map_type(
        self, ctx: thriftParser.Map_typeContext
    ) -> Generator[Union[HyperTypeTextToken, HyperTypeUrnToken], None, None]:
        yield HyperTypeTextToken("map<")
        yield from self.bind_HyperType_from_field_type(ctx.field_type()[0])
        yield HyperTypeTextToken(",")
        yield from self.bind_HyperType_from_field_type(ctx.field_type()[1])
        yield HyperTypeTextToken(">")

    def bind_SchemaFieldDataType_from_field_type(
        self, ctx: thriftParser.Field_typeContext
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
            raise NotImplementedError(f"not support {ctx.getText()} yet.")

    def bind_SchemaFieldDataType_from_IDENTIFIER(
        self, ctx: TerminalNode
    ) -> SchemaFieldDataType:
        qualified_name = ctx.getText()
        return self.bind_SchemaFieldDataType_from_qualified_name(qualified_name)

    def bind_SchemaFieldDataType_from_qualified_name(
        self, qualified_name: str
    ) -> SchemaFieldDataType:
        result = self.resolve_type(qualified_name)
        assert result is not None

        func = {
            ResolvedEnum: lambda _: SchemaFieldDataType(EnumType()),
            ResolvedStruct: lambda _: SchemaFieldDataType(RecordType()),
            ResolvedUnion: self.bind_SchemaFieldDataType_from_ResolvedUnion,  # type: ignore [dict-item]
            ResolvedException: lambda _: SchemaFieldDataType(RecordType()),
            RedirectForType: self.bind_SchemaFieldDataType_from_Redirect,  # type: ignore [dict-item]
            UnresolvedFieldType: self.bind_SchemaFieldDataType_from_UnresolvedFieldType,
        }.get(type(result))
        if func is None:
            raise NotImplementedError(f"not support {type(result)} yet.")

        return func(result)  # type: ignore [arg-type]

    def bind_SchemaFieldDataType_from_ResolvedUnion(
        self, result: ResolvedUnion
    ) -> SchemaFieldDataType:
        return SchemaFieldDataType(UnionType(result.subtypes))

    def bind_SchemaFieldDataType_from_Redirect(  # type: ignore [return, Missing return statement]
        self, result: RedirectForType
    ) -> SchemaFieldDataType:
        binder = get_binder(result.filename, self.thrift_paths)
        return binder.bind_SchemaFieldDataType_from_qualified_name(
            result.qualified_name
        )

    def bind_SchemaFieldDataType_from_UnresolvedFieldType(
        self, result: UnresolvedFieldType
    ) -> SchemaFieldDataType:
        return self.bind_SchemaFieldDataType_from_field_type(result.ctx)

    def bind_SchemaFieldDataType_from_base_type(
        self, ctx: thriftParser.Base_typeContext
    ) -> SchemaFieldDataType:
        return self.bind_SchemaFieldDataType_from_real_base_type(ctx.real_base_type())

    def bind_SchemaFieldDataType_from_container_type(
        self, ctx: thriftParser.Container_typeContext
    ) -> SchemaFieldDataType:
        if ctx.list_type():
            return self.bind_SchemaFieldDataType_from_list_type(ctx.list_type())
        elif ctx.map_type():
            return self.bind_SchemaFieldDataType_from_map_type(ctx.map_type())
        elif ctx.set_type():
            return self.bind_SchemaFieldDataType_from_set_type(ctx.set_type())
        else:
            raise NotImplementedError(f"not support {ctx.getText()} yet.")

    def bind_SchemaFieldDataType_from_map_type(
        self, ctx: thriftParser.Map_typeContext
    ) -> SchemaFieldDataType:

        return SchemaFieldDataType(
            MapType(
                self.bind_native_data_type_from_field_type(ctx.field_type()[0]),
                self.bind_native_data_type_from_field_type(ctx.field_type()[1]),
            )
        )

    def bind_SchemaFieldDataType_from_list_type(
        self, ctx: thriftParser.List_typeContext
    ) -> SchemaFieldDataType:
        return SchemaFieldDataType(
            ArrayType([self.bind_native_data_type_from_field_type(ctx.field_type())])
        )

    def bind_SchemaFieldDataType_from_set_type(
        self, ctx: thriftParser.Set_typeContext
    ) -> SchemaFieldDataType:
        return SchemaFieldDataType(
            ArrayType([self.bind_native_data_type_from_field_type(ctx.field_type())])
        )

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
            raise NotImplementedError(f"not support {ctx.getText()} yet.")


@lru_cache()
def get_binder(filename: str, thrift_paths: Tuple[str, ...]) -> Binder:
    name_resolver = get_name_resolver(filename, thrift_paths)
    return Binder(filename, thrift_paths, name_resolver)


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
        self, filename: str, thrift_paths: Optional[Tuple[str, ...]]
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        if os.path.isfile(filename) and os.path.splitext(filename)[1] == ".thrift":
            try:
                print(f"Processing {filename}")
                tree = parse(filename)
                # evaluator
                yield from get_binder(
                    filename, thrift_paths or tuple()
                ).bind_MCPs_from_Document(tree)
            except Exception as e:
                if self.config.explicit:
                    raise e
                self.report.errors.append(f"Error: {e}")
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
