from dataclasses import dataclass, field
from typing import Generator, Iterable, Union

from antlr4 import CommonTokenStream, InputStream

from datahub.configuration.common import ConfigModel
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.ingestion.api.source import Source, SourceReport
from datahub.ingestion.api.workunit import MetadataWorkUnit, UsageStatsWorkUnit
from datahub.ingestion.source.dist.ThriftLexer import ThriftLexer  # type: ignore
from datahub.ingestion.source.dist.ThriftParser import ThriftParser  # type: ignore
from datahub.metadata.com.linkedin.pegasus2avro.events.metadata import ChangeType
from datahub.metadata.com.linkedin.pegasus2avro.schema import (
    ArrayType,
    NumberType,
    OtherSchema,
    SchemaField,
    SchemaFieldDataType,
    SchemaMetadata,
    StringType,
    MapType,
)


class ThriftSourceConfig(ConfigModel):
    filename: str


class Binder:
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
        else:
            raise NotImplementedError()

    def bind_MCPs_from_struct_(
        self, ctx: ThriftParser.Struct_Context
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:

        name = ctx.IDENTIFIER().getText()
        urn = f"urn:li:dataset:(urn:li:dataPlatform:thrift,{name},PROD)"
        yield MetadataChangeProposalWrapper(
            entityType="dataset",
            changeType=ChangeType.UPSERT,
            aspectName="schemaMetadata",
            entityUrn=urn,
            aspect=SchemaMetadata(
                schemaName=name,
                platform="urn:li:dataPlatform:thrift",
                version=0,
                hash="",
                platformSchema=OtherSchema(""),
                fields=[
                    self.bind_SchemaField_from_field(field) for field in ctx.field()
                ],
            ),
        )

    def bind_SchemaField_from_field(
        self, ctx: ThriftParser.FieldContext
    ) -> SchemaField:
        return SchemaField(
            fieldPath=ctx.IDENTIFIER().getText(),
            type=self.bind_SchemaFieldDataType_from_field_type(ctx.field_type()),
            nativeDataType=self.bind_str_from_field_type(ctx.field_type()),
        )


    def bind_SchemaFieldDataType_from_field_type(
        self, ctx: ThriftParser.Field_typeContext
    ) -> SchemaFieldDataType:
        if ctx.base_type():
            return self.bind_SchemaFieldDataType_from_base_type(ctx.base_type())
        elif ctx.container_type():
            return self.bind_SchemaFieldDataType_from_container_type(
                ctx.container_type()
            )
        
        else:
            raise NotImplementedError()

    def bind_SchemaFieldDataType_from_base_type(
        self, ctx: ThriftParser.Base_typeContext
    ) -> SchemaFieldDataType:
        return self.bind_SchemaFieldDataType_from_Real_base_type(ctx.real_base_type())

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
                self.bind_str_from_field_type(ctx.field_type()[0]),
                self.bind_str_from_field_type(ctx.field_type()[1])
                )
        )

    def bind_SchemaFieldDataType_from_list_type(
        self, ctx: ThriftParser.List_typeContext
    ) -> SchemaFieldDataType:

        return SchemaFieldDataType(
            ArrayType([self.bind_str_from_field_type(ctx.field_type())])
        )

    def bind_SchemaFieldDataType_from_set_type(
        self, ctx: ThriftParser.Set_typeContext
    ) -> SchemaFieldDataType:

        return SchemaFieldDataType(
            ArrayType([self.bind_str_from_field_type(ctx.field_type())])
        )

    def bind_str_from_field_type(
        self, ctx: ThriftParser.Field_typeContext
    ) -> str:
        if ctx.base_type():
            return self.bind_str_from_base_type(ctx.base_type())
        elif ctx.container_type():
            return self.bind_str_from_container_type(ctx.container_type())
        else:
            raise NotImplementedError()

    def bind_str_from_container_type(
        self, ctx: ThriftParser.Container_typeContext
    ) -> str:
        if ctx.list_type():
            return self.bind_str_from_list_type(ctx.list_type())
        elif ctx.map_type():
            return self.bind_str_from_map_type(ctx.map_type())
        elif ctx.set_type():
            return self.bind_str_from_set_type(ctx.set_type())
        else:
            raise NotImplementedError()

    def bind_str_from_list_type(self, ctx: ThriftParser.List_typeContext) -> str:
        return f"list<{self.bind_str_from_field_type(ctx.field_type())}>"

    def bind_str_from_set_type(self, ctx: ThriftParser.Set_typeContext) -> str:
        return f"set<{self.bind_str_from_field_type(ctx.field_type())}>"

    def bind_str_from_map_type(self, ctx: ThriftParser.Map_typeContext) -> str:
        return f"map<{self.bind_str_from_field_type(ctx.field_type()[0])},{self.bind_str_from_field_type(ctx.field_type()[1])}>"

    def bind_str_from_base_type(self, ctx: ThriftParser.Base_typeContext) -> str:
        return ctx.real_base_type().getText()

    def bind_SchemaFieldDataType_from_Real_base_type(
        self, ctx: ThriftParser.Real_base_typeContext
    ) -> SchemaFieldDataType:
        if ctx.TYPE_I32() or ctx.TYPE_I64() or ctx.TYPE_DOUBLE():
            return SchemaFieldDataType(NumberType())
        elif ctx.TYPE_STRING:
            return SchemaFieldDataType(StringType())
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
        self, filename: str
    ) -> Generator[MetadataChangeProposalWrapper, None, None]:
        with open(filename) as text_file:
            # lexer

            lexer = ThriftLexer(InputStream(text_file.read()))
            stream = CommonTokenStream(lexer)
            # parser
            parser = ThriftParser(stream)

            tree = parser.document()
            # evaluator
            yield from Binder().bind_MCPs_from_Document(tree)

    def get_workunits(self) -> Iterable[Union[MetadataWorkUnit, UsageStatsWorkUnit]]:
        for i, obj in enumerate(self.parse(self.config.filename)):
            wu = MetadataWorkUnit(f"file://{self.config.filename}:{i}", mcp=obj)
            self.report.report_workunit(wu)
            yield wu

    def get_report(self):
        return self.report

    def close(self):
        pass
