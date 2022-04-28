from ast import Return
from dataclasses import dataclass, field
from typing import Generator, Iterable, Union

from antlr4 import InputStream, CommonTokenStream

from datahub.configuration.common import ConfigModel
from datahub.ingestion.api.source import Source, SourceReport
from datahub.ingestion.api.workunit import MetadataWorkUnit, UsageStatsWorkUnit
from datahub.metadata.com.linkedin.pegasus2avro.metadata.snapshot import DatasetSnapshot
from datahub.metadata.com.linkedin.pegasus2avro.mxe import (
    MetadataChangeEvent,
)
from datahub.metadata.com.linkedin.pegasus2avro.schema import (
    NumberType,
    OtherSchema,
    SchemaField,
    SchemaFieldDataType,
    SchemaMetadata,
    StringType,
)

from datahub.ingestion.source.dist.ThriftGrammerLexer import ThriftGrammerLexer
from datahub.ingestion.source.dist.ThriftGrammerParser import ThriftGrammerParser
from datahub.ingestion.source.dist.ThriftGrammerVisitor import ThriftGrammerVisitor


class ThriftSourceConfig(ConfigModel):
    filename: str


class Binder:
    def bind_MCEs_from_Document(
        self, ctx: ThriftGrammerParser.DocumentContext
    ) -> Generator[MetadataChangeEvent, None, None]:
        for definition in ctx.definition():
            yield self.bind_MCE_from_Definition(definition)

    def bind_MCE_from_Definition(
        self, ctx: ThriftGrammerParser.DefinitionContext
    ) -> MetadataChangeEvent:
        if ctx.struct_():
            return self.bind_MCE_from_struct_(ctx.struct_())
        else:
            raise NotImplementedError()

    def bind_MCE_from_struct_(
        self, ctx: ThriftGrammerParser.Struct_Context
    ) -> MetadataChangeEvent:
        name = ctx.IDENTIFIER().getText()
        urn = f"urn:li:dataset:(urn:li:dataPlatform:thrift,{name},PROD)"
        return MetadataChangeEvent(
            DatasetSnapshot(
                urn=urn,
                aspects=[
                    SchemaMetadata(
                        schemaName=name,
                        platform="urn:li:dataPlatform:thrift",
                        version=0,
                        hash="",
                        platformSchema=OtherSchema(""),
                        fields=[self.bind_SchemaField_from_field(field) for field in ctx.field()],
                    )
                ],
            )
        )

    def bind_SchemaField_from_field(self, ctx: ThriftGrammerParser.FieldContext) -> SchemaField:
        return SchemaField(
            fieldPath=ctx.IDENTIFIER().getText(),
            type=self.bind_SchemaFieldDataType_from_field_type(ctx.field_type()),
            nativeDataType=self.bind_nativeDataType_from_field_type(ctx.field_type())
        )

    def bind_nativeDataType_from_field_type(self, ctx: ThriftGrammerParser.Field_typeContext) -> SchemaField:
        if ctx.base_type():
            return ctx.getText()
        else:
            raise NotImplementedError()

    def bind_SchemaFieldDataType_from_field_type(
        self, ctx: ThriftGrammerParser.Field_typeContext
    ) -> SchemaFieldDataType:
        if ctx.base_type():
            return self.bind_SchemaFieldDataType_from_base_type(ctx.base_type())
        else:
            raise NotImplementedError()

    def bind_SchemaFieldDataType_from_base_type(
        self, ctx: ThriftGrammerParser.Base_typeContext
    ) -> SchemaFieldDataType:
        return self.bind_SchemaFieldDataType_from_Real_base_type(ctx.real_base_type())

    def bind_SchemaFieldDataType_from_Real_base_type(
        self, ctx: ThriftGrammerParser.Real_base_typeContext
    ) -> SchemaFieldDataType:
        if ctx.TYPE_I32() or ctx.TYPE_I64()or ctx.TYPE_DOUBLE():
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

    def parse(self, filename) -> Generator[MetadataChangeEvent, None, None]:
        with open(filename) as text_file:
            # lexer

            lexer = ThriftGrammerLexer(InputStream(text_file.read()))
            stream = CommonTokenStream(lexer)
            # parser
            parser = ThriftGrammerParser(stream)

            tree = parser.document()
            # evaluator
            yield from Binder().bind_MCEs_from_Document(tree)


    def get_workunits(self) -> Iterable[Union[MetadataWorkUnit, UsageStatsWorkUnit]]:
        for i, obj in enumerate(self.parse(self.config.filename)):
            wu = MetadataWorkUnit(f"file://{self.config.filename}:{i}", mce=obj)
            self.report.report_workunit(wu)
            yield wu

    def get_report(self):
        return self.report

    def close(self):
        pass
