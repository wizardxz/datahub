package com.linkedin.datahub.graphql.types.dataset.mappers;

import com.linkedin.datahub.graphql.generated.HyperTypeTextToken;
import com.linkedin.datahub.graphql.generated.HyperTypeToken;
import com.linkedin.datahub.graphql.generated.HyperTypeUrnToken;
import com.linkedin.datahub.graphql.generated.KeyValueSchema;
import com.linkedin.datahub.graphql.generated.PlatformSchema;
import com.linkedin.datahub.graphql.generated.TableSchema;
import com.linkedin.datahub.graphql.generated.ThriftAnnotation;
import com.linkedin.datahub.graphql.generated.ThriftAnnotationValue;
import com.linkedin.datahub.graphql.generated.ThriftDefaultValue;
import com.linkedin.datahub.graphql.generated.ThriftField;
import com.linkedin.datahub.graphql.generated.ThriftNamespace;
import com.linkedin.datahub.graphql.generated.ThriftSchema;
import com.linkedin.datahub.graphql.types.mappers.ModelMapper;
import com.linkedin.schema.SchemaMetadata;
import com.linkedin.schema.ThriftField.HyperType;
import java.util.stream.Collectors;
import javax.annotation.Nonnull;

public class PlatformSchemaMapper implements ModelMapper<SchemaMetadata.PlatformSchema, PlatformSchema> {

  public static final PlatformSchemaMapper INSTANCE = new PlatformSchemaMapper();

  public static PlatformSchema map(@Nonnull final SchemaMetadata.PlatformSchema metadata) {
      return INSTANCE.apply(metadata);
  }

  @Override
  public PlatformSchema apply(@Nonnull final SchemaMetadata.PlatformSchema input) {
      Object result;
      if (input.isSchemaless()) {
          return null;
      } else if (input.isPrestoDDL()) {
          final TableSchema prestoSchema = new TableSchema();
          prestoSchema.setSchema(input.getPrestoDDL().getRawSchema());
          result = prestoSchema;
      } else if (input.isOracleDDL()) {
          final TableSchema oracleSchema = new TableSchema();
          oracleSchema.setSchema(input.getOracleDDL().getTableSchema());
          result = oracleSchema;
      } else if (input.isMySqlDDL()) {
          final TableSchema mySqlSchema = new TableSchema();
          mySqlSchema.setSchema(input.getMySqlDDL().getTableSchema());
          result = mySqlSchema;
      } else if (input.isKafkaSchema()) {
          final TableSchema kafkaSchema = new TableSchema();
          kafkaSchema.setSchema(input.getKafkaSchema().getDocumentSchema());
          result = kafkaSchema;
      } else if (input.isOrcSchema()) {
          final TableSchema orcSchema = new TableSchema();
          orcSchema.setSchema(input.getOrcSchema().getSchema());
          result = orcSchema;
      } else if (input.isBinaryJsonSchema()) {
          final TableSchema binaryJsonSchema = new TableSchema();
          binaryJsonSchema.setSchema(input.getBinaryJsonSchema().getSchema());
          result = binaryJsonSchema;
      } else if (input.isEspressoSchema()) {
          final KeyValueSchema espressoSchema = new KeyValueSchema();
          espressoSchema.setKeySchema(input.getEspressoSchema().getTableSchema());
          espressoSchema.setValueSchema(input.getEspressoSchema().getDocumentSchema());
          result = espressoSchema;
      } else if (input.isKeyValueSchema()) {
          final KeyValueSchema otherKeyValueSchema = new KeyValueSchema();
          otherKeyValueSchema.setKeySchema(input.getKeyValueSchema().getKeySchema());
          otherKeyValueSchema.setValueSchema(input.getKeyValueSchema().getValueSchema());
          result = otherKeyValueSchema;
      } else if (input.isOtherSchema()) {
          final TableSchema otherTableSchema = new TableSchema();
          otherTableSchema.setSchema(input.getOtherSchema().getRawSchema());
          result = otherTableSchema;
    } else if (input.isThriftSchema()) {
      final ThriftSchema thriftSchema = new ThriftSchema();
      thriftSchema.setRawSchema(input.getThriftSchema().getRawSchema());
      thriftSchema.setFilename(input.getThriftSchema().getFilename());
      thriftSchema.setFields(
        input
          .getThriftSchema()
          .getFields()
          .stream()
          .map(this::mapThriftField)
          .collect(Collectors.toList())
      );
      if (input.getThriftSchema().getAnnotations() != null) {
        thriftSchema.setAnnotations(
          input
            .getThriftSchema()
            .getAnnotations()
            .stream()
            .map(this::mapAnnotation)
            .collect(Collectors.toList())
        );
      }
      thriftSchema.setNamespaces(
        input
          .getThriftSchema()
          .getNamespace_()
          .entrySet()
          .stream()
          .map(e -> new ThriftNamespace(e.getKey(), e.getValue()))
          .collect(Collectors.toList())
      );
      result = thriftSchema;
    } else {
      throw new RuntimeException(
        String.format(
          "Unrecognized platform schema type %s provided",
          input.memberType().getType().name()
        )
      );
    }
    return (PlatformSchema) result;
  }

  private ThriftAnnotation mapAnnotation(
    @Nonnull com.linkedin.schema.ThriftAnnotation gmsAnnotation
  ) {
    ThriftAnnotation annotation = new ThriftAnnotation();
    annotation.setKey(gmsAnnotation.getKey());
    annotation.setValue(
      gmsAnnotation.getValue().isInt()
        ? new ThriftAnnotationValue(gmsAnnotation.getValue().getInt(), null)
        : new ThriftAnnotationValue(null, gmsAnnotation.getValue().getString())
    );
    return annotation;
  }

  private ThriftDefaultValue mapDefault(
    @Nonnull com.linkedin.schema.ThriftField.Default gmsDefault
  ) {
    if (gmsDefault.isBoolean()) {
      return new ThriftDefaultValue.Builder()
        .setBooleanValue(gmsDefault.getBoolean())
        .build();
    } else if (gmsDefault.isInt()) {
      return new ThriftDefaultValue.Builder()
        .setIntValue(gmsDefault.getInt())
        .build();
    } else if (gmsDefault.isFloat()) {
      return new ThriftDefaultValue.Builder()
        .setFloatValue(gmsDefault.getFloat())
        .build();
    } else if (gmsDefault.isString()) {
      return new ThriftDefaultValue.Builder()
        .setStringValue(gmsDefault.getString())
        .build();
    }
    return null;
  }

  private HyperTypeToken mapHyperTypeToken(@Nonnull HyperType gmsHyperType) {
    if (gmsHyperType.isHyperTypeTextToken()) {
      return new HyperTypeTextToken(
        gmsHyperType.getHyperTypeTextToken().getText()
      );
    } else if (gmsHyperType.isHyperTypeUrnToken()) {
      com.linkedin.schema.HyperTypeUrnToken gmsToken = gmsHyperType.getHyperTypeUrnToken();
      return new HyperTypeUrnToken(gmsToken.getText(), gmsToken.getUrn());
    } else {
      return null;
    }
  }

  private ThriftField mapThriftField(
    @Nonnull com.linkedin.schema.ThriftField gmsField
  ) {
    ThriftField field = new ThriftField();
    field.setName(gmsField.getName());
    field.setIndex(gmsField.getIndex());
    field.setHyperType(
      gmsField
        .getHyperType()
        .stream()
        .map(this::mapHyperTypeToken)
        .collect(Collectors.toList())
    );
    if (gmsField.getDefault() != null) {
      field.setDefault(mapDefault(gmsField.getDefault()));
    }
    if (gmsField.getAnnotations() != null) {
      field.setAnnotations(
        gmsField
          .getAnnotations()
          .stream()
          .map(this::mapAnnotation)
          .collect(Collectors.toList())
      );
    }
    return field;
  }
}
