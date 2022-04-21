import json
from dataclasses import dataclass, field
from typing import Generator, Iterable, Iterator, Union

from datahub.configuration.common import ConfigModel
from datahub.ingestion.api.source import Source, SourceReport
from datahub.ingestion.api.workunit import MetadataWorkUnit, UsageStatsWorkUnit
from datahub.metadata.com.linkedin.pegasus2avro.metadata.snapshot import DatasetSnapshot
from datahub.metadata.com.linkedin.pegasus2avro.mxe import (
    MetadataChangeEvent,
    MetadataChangeProposal,
)
from datahub.metadata.com.linkedin.pegasus2avro.schema import (
    ArrayType,
    NullType,
    NumberType,
    OtherSchema,
    SchemaField,
    SchemaFieldDataType,
    SchemaMetadata,
    StringType,
)
from datahub.metadata.schema_classes import DatasetSnapshotClass, UsageAggregationClass


from antlr4 import *
from .dist.ThriftGrammerLexer import ThriftGrammerLexer
from .dist.ThriftGrammerParser import ThriftGrammerParser
from .dist.ThriftGrammerVisitor import ThriftGrammerVisitor
from typing import Union, overload, List


class ThriftSourceConfig(ConfigModel):
    filename: str


class ThriftVisitor(ThriftGrammerVisitor):
    def visitDocument(
        self, ctx: ThriftGrammerParser.DocumentContext
    ) -> Generator[MetadataChangeEvent, None, None]:
        for definition in ctx.definition():
            yield self.visit(definition)

    def visitDefinition(
        self, ctx: ThriftGrammerParser.DefinitionContext
    ) -> MetadataChangeEvent:
        if ctx.struct_():
            return self.visit(ctx.struct_())
        else:
            raise NotImplementedError()

    def visitStruct_(
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
                        fields=[self.visit(field) for field in ctx.field()],
                    )
                ],
            )
        )

    

    def visitField(self, ctx: ThriftGrammerParser.FieldContext) -> SchemaField:
        return SchemaField(

            fieldPath=ctx.IDENTIFIER().getText(),
            type=self.visit(ctx.field_type()),
            nativeDataType=ctx.field_type().getText(),
        )

    def visitField_type(
        self, ctx: ThriftGrammerParser.Field_typeContext
    ) -> SchemaFieldDataType:
        if ctx.base_type():
            raise NotImplementedError()

    def visitBase_type(
        self, ctx: ThriftGrammerParser.Base_typeContext
    ) -> SchemaFieldDataType:
        return self.visit(ctx.real_base_type())

    def visitReal_base_type(
        self, ctx: ThriftGrammerParser.Real_base_typeContext
    ) -> SchemaFieldDataType:
        if ctx.TYPE_I32():
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
            visitor = ThriftVisitor()

            yield from visitor.visit(tree)

    def get_workunits(self) -> Iterable[Union[MetadataWorkUnit, UsageStatsWorkUnit]]:
        for i, obj in enumerate(self.parse(self.config.filename)):
            wu = MetadataWorkUnit(f"file://{self.config.filename}:{i}", mce=obj)
            self.report.report_workunit(wu)
            yield wu

    def get_report(self):
        return self.report

    def close(self):
        pass
