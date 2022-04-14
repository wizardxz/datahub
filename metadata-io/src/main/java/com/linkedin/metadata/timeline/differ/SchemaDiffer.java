package com.linkedin.metadata.timeline.differ;

import com.datahub.util.RecordUtils;
import com.github.fge.jsonpatch.JsonPatch;
import com.linkedin.common.urn.DatasetUrn;
import com.linkedin.common.urn.Urn;
import com.linkedin.metadata.entity.ebean.EbeanAspectV2;
import com.linkedin.metadata.timeline.data.ChangeCategory;
import com.linkedin.metadata.timeline.data.ChangeEvent;
import com.linkedin.metadata.timeline.data.ChangeOperation;
import com.linkedin.metadata.timeline.data.ChangeTransaction;
import com.linkedin.metadata.timeline.data.SemanticChangeType;
import com.linkedin.schema.SchemaField;
import com.linkedin.schema.SchemaFieldArray;
import com.linkedin.schema.SchemaMetadata;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import javax.annotation.Nonnull;


public class SchemaDiffer implements Differ {
  private static final String SCHEMA_METADATA_ASPECT_NAME = "schemaMetadata";
  private static final String BACKWARDS_INCOMPATIBLE_DESC = "A backwards incompatible change due to ";
  private static final String FORWARDS_COMPATIBLE_DESC = "A forwards compatible change due to ";
  private static final String BACK_AND_FORWARD_COMPATIBLE_DESC = "A forwards & backwards compatible change due to ";
  private static final String FIELD_DESCRIPTION_ADDED_FORMAT =
      "The description '%s' for the field '%s' has been added.";
  private static final String FIELD_DESCRIPTION_REMOVED_FORMAT =
      "The description '%s' for the field '%s' has been removed.";
  private static final String FIELD_DESCRIPTION_MODIFIED_FORMAT =
      "The description for the field '%s' has been changed from '%s' to '%s'.";

  private static String getFieldPathV1(@Nonnull SchemaField field) {
    String[] v1PathTokens = Arrays.stream(field.getFieldPath().split("\\."))
        .filter(x -> !(x.startsWith("[") || x.endsWith("]")))
        .toArray(String[]::new);
    return String.join(".", v1PathTokens);
  }

  private static String getSchemaFieldUrn(@Nonnull Urn datasetUrn, @Nonnull SchemaField schemaField) {
    return String.format("urn:li:schemaField:(%s,%s)", datasetUrn, getFieldPathV1(schemaField));
  }

  private static String getSchemaFieldUrn(@Nonnull Urn datasetUrn, @Nonnull String schemaFieldPath) {
    return String.format("urn:li:schemaField:(%s,%s)", datasetUrn, schemaFieldPath);
  }

  private static ChangeEvent getDescriptionChange(SchemaField baseField, SchemaField targetField,
      String datasetFieldUrn) {
    String baseDesciption = (baseField != null) ? baseField.getDescription() : null;
    String targetDescription = (targetField != null) ? targetField.getDescription() : null;
    if (baseDesciption == null && targetDescription != null) {
      // Description got added.
      return ChangeEvent.builder()
          .changeType(ChangeOperation.ADD)
          .semVerChange(SemanticChangeType.MINOR)
          .category(ChangeCategory.DOCUMENTATION)
          .target(datasetFieldUrn)
          .description(String.format(FIELD_DESCRIPTION_ADDED_FORMAT, targetDescription, targetField.getFieldPath()))
          .build();
    }
    if (baseDesciption != null && targetDescription == null) {
      // Description removed.
      return ChangeEvent.builder()
          .changeType(ChangeOperation.REMOVE)
          .semVerChange(SemanticChangeType.MINOR)
          .category(ChangeCategory.DOCUMENTATION)
          .target(datasetFieldUrn)
          .description(String.format(FIELD_DESCRIPTION_REMOVED_FORMAT, baseDesciption, baseField.getFieldPath()))
          .build();
    }
    if (baseDesciption != null && !baseDesciption.equals(targetDescription)) {
      // Description Change
      return ChangeEvent.builder()
          .changeType(ChangeOperation.MODIFY)
          .semVerChange(SemanticChangeType.PATCH)
          .category(ChangeCategory.DOCUMENTATION)
          .target(datasetFieldUrn)
          .description(String.format(FIELD_DESCRIPTION_MODIFIED_FORMAT, baseField.getFieldPath(), baseDesciption,
              targetDescription))
          .build();
    }
    return null;
  }

  private static List<ChangeEvent> getGlobalTagChangeEvents(SchemaField baseField, SchemaField targetField,
      String datasetFieldUrn) {
    return GlobalTagsDiffer.computeDiffs(baseField != null ? baseField.getGlobalTags() : null,
        targetField != null ? targetField.getGlobalTags() : null, datasetFieldUrn);
  }

  private static List<ChangeEvent> getGlossaryTermsChangeEvents(SchemaField baseField, SchemaField targetField,
      String datasetFieldUrn) {
    return GlossaryTermsDiffer.computeDiffs(baseField != null ? baseField.getGlossaryTerms() : null,
        targetField != null ? targetField.getGlossaryTerms() : null, datasetFieldUrn);
  }

  private static List<ChangeEvent> getFieldPropertyChangeEvents(SchemaField baseField, SchemaField targetField,
      Urn datasetUrn, ChangeCategory changeCategory) {
    List<ChangeEvent> propChangeEvents = new ArrayList<>();
    String datasetFieldUrn;
    if (targetField != null) {
      datasetFieldUrn = getSchemaFieldUrn(datasetUrn, targetField);
    } else {
      datasetFieldUrn = getSchemaFieldUrn(datasetUrn, baseField);
    }

    // Description Change.
    if (ChangeCategory.DOCUMENTATION.equals(changeCategory)) {
      ChangeEvent descriptionChangeEvent = getDescriptionChange(baseField, targetField, datasetFieldUrn);
      if (descriptionChangeEvent != null) {
        propChangeEvents.add(descriptionChangeEvent);
      }
    }

    // Global Tags
    if (ChangeCategory.TAG.equals(changeCategory)) {
      propChangeEvents.addAll(getGlobalTagChangeEvents(baseField, targetField, datasetFieldUrn));
    }

    // Glossary terms.
    if (ChangeCategory.GLOSSARY_TERM.equals(changeCategory)) {
      propChangeEvents.addAll(getGlossaryTermsChangeEvents(baseField, targetField, datasetFieldUrn));
    }

    return propChangeEvents;
  }

  // TODO: This could use some cleanup, lots of repeated logic and tenuous conditionals
  private static List<ChangeEvent> computeDiffs(SchemaMetadata baseSchema, SchemaMetadata targetSchema,
      Urn datasetUrn, ChangeCategory changeCategory) {
    boolean isOrdinalBasedSchema = isSchemaOrdinalBased(targetSchema);
    if (!isOrdinalBasedSchema) {
      // Sort the fields by their field path.
      if (baseSchema != null) {
        sortFieldsByPath(baseSchema);
      }
      sortFieldsByPath(targetSchema);
    }

    // Performs ordinal based diff, primarily based on fixed field ordinals and their types.
    SchemaFieldArray baseFields = (baseSchema != null ? baseSchema.getFields() : new SchemaFieldArray());
    SchemaFieldArray targetFields = targetSchema.getFields();
    int baseFieldIdx = 0;
    int targetFieldIdx = 0;
    List<ChangeEvent> changeEvents = new ArrayList<>();
    while (baseFieldIdx < baseFields.size() && targetFieldIdx < targetFields.size()) {
      SchemaField curBaseField = baseFields.get(baseFieldIdx);
      SchemaField curTargetField = targetFields.get(targetFieldIdx);
      if (isOrdinalBasedSchema) {
        if (!curBaseField.getNativeDataType().equals(curTargetField.getNativeDataType())) {
          // Non-backward compatible change + Major version bump
          if (ChangeCategory.TECHNICAL_SCHEMA.equals(changeCategory)) {
            changeEvents.add(ChangeEvent.builder()
                .category(ChangeCategory.TECHNICAL_SCHEMA)
                .elementId(getSchemaFieldUrn(datasetUrn, curBaseField))
                .target(datasetUrn.toString())
                .changeType(ChangeOperation.MODIFY)
                .semVerChange(SemanticChangeType.MAJOR)
                .description(String.format("%s native datatype of the field '%s' changed from '%s' to '%s'.",
                    BACKWARDS_INCOMPATIBLE_DESC, getFieldPathV1(curTargetField), curBaseField.getNativeDataType(),
                    curTargetField.getNativeDataType()))
                .build());
          }
          List<ChangeEvent> propChangeEvents = getFieldPropertyChangeEvents(curBaseField, curTargetField, datasetUrn,
              changeCategory);
          changeEvents.addAll(propChangeEvents);
          ++baseFieldIdx;
          ++targetFieldIdx;
          continue;
        }
        if (baseFieldIdx == targetFieldIdx && !curBaseField.getFieldPath().equals(curTargetField.getFieldPath())
            && ChangeCategory.TECHNICAL_SCHEMA.equals(changeCategory)) {
          // The field got renamed. Forward compatible + Minor version bump.
          changeEvents.add(ChangeEvent.builder()
              .category(ChangeCategory.TECHNICAL_SCHEMA)
              .elementId(getSchemaFieldUrn(datasetUrn, curBaseField))
              .target(datasetUrn.toString())
              .changeType(ChangeOperation.MODIFY)
              .semVerChange(SemanticChangeType.MINOR)
              .description(
                  FORWARDS_COMPATIBLE_DESC + "field name changed from '" + getFieldPathV1(curBaseField) + "' to '"
                      + getFieldPathV1(curTargetField) + "'")
              .build());
        }
        // Generate change events from property changes
        List<ChangeEvent> propChangeEvents = getFieldPropertyChangeEvents(curBaseField, curTargetField, datasetUrn,
            changeCategory);
        changeEvents.addAll(propChangeEvents);
        ++baseFieldIdx;
        ++targetFieldIdx;
      } else {
        // Non-ordinal based schemas are pre-sorted by ascending order of fieldPaths.
        int comparison = curBaseField.getFieldPath().compareTo(curTargetField.getFieldPath());
        if (comparison == 0) {
          // This is the same field. Check for change events from property changes.
          List<ChangeEvent> propChangeEvents = getFieldPropertyChangeEvents(curBaseField, curTargetField, datasetUrn,
              changeCategory);
          changeEvents.addAll(propChangeEvents);
          ++baseFieldIdx;
          ++targetFieldIdx;
        } else if (comparison < 0) {
          // BaseFiled got removed. Non-backward compatible change + Major version bump
          if (ChangeCategory.TECHNICAL_SCHEMA.equals(changeCategory)) {
            changeEvents.add(ChangeEvent.builder()
                .category(ChangeCategory.TECHNICAL_SCHEMA)
                .elementId(getSchemaFieldUrn(datasetUrn, curBaseField))
                .target(datasetUrn.toString())
                .changeType(ChangeOperation.REMOVE)
                .semVerChange(SemanticChangeType.MAJOR)
                .description(BACKWARDS_INCOMPATIBLE_DESC + "removal of the field'" + getFieldPathV1(curBaseField) + "'.")
                .build());
          }
          List<ChangeEvent> propChangeEvents = getFieldPropertyChangeEvents(curBaseField, curTargetField, datasetUrn,
              changeCategory);
          changeEvents.addAll(propChangeEvents);
          ++baseFieldIdx;
        } else {
          // The targetField got added. Forward & backwards compatible change + minor version bump.
          if (ChangeCategory.TECHNICAL_SCHEMA.equals(changeCategory)) {
            changeEvents.add(ChangeEvent.builder()
                .category(ChangeCategory.TECHNICAL_SCHEMA)
                .elementId(getSchemaFieldUrn(datasetUrn, curTargetField))
                .target(datasetUrn.toString())
                .changeType(ChangeOperation.ADD)
                .semVerChange(SemanticChangeType.MINOR)
                .description(
                    BACK_AND_FORWARD_COMPATIBLE_DESC + "the newly added field '" + getFieldPathV1(curTargetField) + "'.")
                .build());
          }
          List<ChangeEvent> propChangeEvents = getFieldPropertyChangeEvents(curBaseField, curTargetField, datasetUrn,
              changeCategory);
          changeEvents.addAll(propChangeEvents);
          ++targetFieldIdx;
        }
      }
    }
    while (baseFieldIdx < baseFields.size()) {
      // Handle removed fields. Non-backward compatible change + major version bump
      SchemaField baseField = baseFields.get(baseFieldIdx);
      if (ChangeCategory.TECHNICAL_SCHEMA.equals(changeCategory)) {
        changeEvents.add(ChangeEvent.builder()
            .elementId(getSchemaFieldUrn(datasetUrn, baseField))
            .target(datasetUrn.toString())
            .category(ChangeCategory.TECHNICAL_SCHEMA)
            .changeType(ChangeOperation.REMOVE)
            .semVerChange(SemanticChangeType.MAJOR)
            .description(BACKWARDS_INCOMPATIBLE_DESC + "removal of field: '" + getFieldPathV1(baseField) + "'.")
            .build());
      }
      List<ChangeEvent> propChangeEvents = getFieldPropertyChangeEvents(baseField, null, datasetUrn,
          changeCategory);
      changeEvents.addAll(propChangeEvents);
      ++baseFieldIdx;
    }
    while (targetFieldIdx < targetFields.size()) {
      // Newly added fields. Forwards & backwards compatible change + minor version bump.
      SchemaField targetField = targetFields.get(targetFieldIdx);
      if (ChangeCategory.TECHNICAL_SCHEMA.equals(changeCategory)) {
        changeEvents.add(ChangeEvent.builder()
            .elementId(getSchemaFieldUrn(datasetUrn, targetField))
            .target(datasetUrn.toString())
            .category(ChangeCategory.TECHNICAL_SCHEMA)
            .changeType(ChangeOperation.ADD)
            .semVerChange(SemanticChangeType.MINOR)
            .description(BACK_AND_FORWARD_COMPATIBLE_DESC + "the newly added field '" + getFieldPathV1(targetField) + "'.")
            .build());
      }
      List<ChangeEvent> propChangeEvents = getFieldPropertyChangeEvents(null, targetField, datasetUrn,
          changeCategory);
      changeEvents.addAll(propChangeEvents);
      ++targetFieldIdx;
    }

    // Handle primary key constraint change events.
    List<ChangeEvent> primaryKeyChangeEvents = getPrimaryKeyChangeEvents(baseSchema, targetSchema, datasetUrn);
    changeEvents.addAll(primaryKeyChangeEvents);

    // Handle foreign key constraint change events.
    List<ChangeEvent> foreignKeyChangeEvents = getForeignKeyChangeEvents(baseSchema, targetSchema);
    changeEvents.addAll(foreignKeyChangeEvents);

    return changeEvents;
  }

  private static boolean isSchemaOrdinalBased(SchemaMetadata schemaMetadata) {
    if (schemaMetadata == null) {
      return false;
    }
    SchemaMetadata.PlatformSchema platformSchema = schemaMetadata.getPlatformSchema();
    return platformSchema.isOracleDDL() || platformSchema.isMySqlDDL() || platformSchema.isPrestoDDL();
  }

  private static void sortFieldsByPath(SchemaMetadata schemaMetadata) {
    assert (schemaMetadata != null);
    List<SchemaField> schemaFields = new ArrayList<>(schemaMetadata.getFields());
    schemaFields.sort(Comparator.comparing(SchemaField::getFieldPath));
    schemaMetadata.setFields(new SchemaFieldArray(schemaFields));
  }

  private static ChangeEvent getIncompatibleChangeEvent(SchemaMetadata baseSchema, SchemaMetadata targetSchema) {
    if (baseSchema != null && targetSchema != null) {
      if (!baseSchema.getPlatform().equals(targetSchema.getPlatform())) {
        return ChangeEvent.builder()
            .semVerChange(SemanticChangeType.EXCEPTIONAL)
            .description("Incompatible schema types," + baseSchema.getPlatform() + ", " + targetSchema.getPlatform())
            .build();
      }
      if (!baseSchema.getSchemaName().equals(targetSchema.getSchemaName())) {
        return ChangeEvent.builder()
            .semVerChange(SemanticChangeType.EXCEPTIONAL)
            .description(
                "Schema names are not same," + baseSchema.getSchemaName() + ", " + targetSchema.getSchemaName())
            .build();
      }
    }
    return null;
  }

  @SuppressWarnings("ConstantConditions")
  private static SchemaMetadata getSchemaMetadataFromAspect(EbeanAspectV2 ebeanAspectV2) {
    if (ebeanAspectV2 != null && ebeanAspectV2.getMetadata() != null) {
      return RecordUtils.toRecordTemplate(SchemaMetadata.class, ebeanAspectV2.getMetadata());
    }
    return null;
  }

  @SuppressWarnings("UnnecessaryLocalVariable")
  private static List<ChangeEvent> getForeignKeyChangeEvents(SchemaMetadata baseSchema, SchemaMetadata targetSchema) {
    List<ChangeEvent> foreignKeyChangeEvents = new ArrayList<>();
    // TODO: Implement the diffing logic.
    return foreignKeyChangeEvents;
  }

  private static List<ChangeEvent> getPrimaryKeyChangeEvents(SchemaMetadata baseSchema, SchemaMetadata targetSchema,
      Urn datasetUrn) {
    List<ChangeEvent> primaryKeyChangeEvents = new ArrayList<>();
    Set<String> basePrimaryKeys =
        (baseSchema != null && baseSchema.getPrimaryKeys() != null) ? new HashSet<>(baseSchema.getPrimaryKeys())
            : new HashSet<>();
    Set<String> targetPrimaryKeys =
        (targetSchema.getPrimaryKeys() != null) ? new HashSet<>(targetSchema.getPrimaryKeys()) : new HashSet<>();
    Set<String> removedBaseKeys =
        basePrimaryKeys.stream().filter(key -> !targetPrimaryKeys.contains(key)).collect(Collectors.toSet());
    for (String removedBaseKeyField : removedBaseKeys) {
      primaryKeyChangeEvents.add(ChangeEvent.builder()
          .category(ChangeCategory.TECHNICAL_SCHEMA)
          .elementId(getSchemaFieldUrn(datasetUrn, removedBaseKeyField))
          .target(datasetUrn.toString())
          .changeType(ChangeOperation.MODIFY)
          .semVerChange(SemanticChangeType.MAJOR)
          .description(BACKWARDS_INCOMPATIBLE_DESC + "removal of the primary key field '" + removedBaseKeyField + "'")
          .build());
    }

    Set<String> addedTargetKeys =
        targetPrimaryKeys.stream().filter(key -> !basePrimaryKeys.contains(key)).collect(Collectors.toSet());
    for (String addedTargetKeyField : addedTargetKeys) {
      primaryKeyChangeEvents.add(ChangeEvent.builder()
          .category(ChangeCategory.TECHNICAL_SCHEMA)
          .elementId(getSchemaFieldUrn(datasetUrn, addedTargetKeyField))
          .target(datasetUrn.toString())
          .changeType(ChangeOperation.MODIFY)
          .semVerChange(SemanticChangeType.MAJOR)
          .description(BACKWARDS_INCOMPATIBLE_DESC + "addition of the primary key field '" + addedTargetKeyField + "'")
          .build());
    }
    return primaryKeyChangeEvents;
  }

  @Override
  public ChangeTransaction getSemanticDiff(EbeanAspectV2 previousValue, EbeanAspectV2 currentValue,
      ChangeCategory changeCategory, JsonPatch rawDiff, boolean rawDiffRequested) {
    if (!previousValue.getAspect().equals(SCHEMA_METADATA_ASPECT_NAME) || !currentValue.getAspect()
        .equals(SCHEMA_METADATA_ASPECT_NAME)) {
      throw new IllegalArgumentException("Aspect is not " + SCHEMA_METADATA_ASPECT_NAME);
    }

    SchemaMetadata baseSchema = getSchemaMetadataFromAspect(previousValue);
    SchemaMetadata targetSchema = getSchemaMetadataFromAspect(currentValue);
    assert (targetSchema != null);
    List<ChangeEvent> changeEvents = new ArrayList<>();
    ChangeEvent incompatibleChangeEvent = getIncompatibleChangeEvent(baseSchema, targetSchema);
    if (incompatibleChangeEvent != null) {
      changeEvents.add(incompatibleChangeEvent);
    } else {
      try {
        changeEvents.addAll(
            computeDiffs(baseSchema, targetSchema, DatasetUrn.createFromString(currentValue.getUrn()), changeCategory));
      } catch (URISyntaxException e) {
        throw new IllegalArgumentException("Malformed DatasetUrn " + currentValue.getUrn());
      }
    }

    // Assess the highest change at the transaction(schema) level.
    SemanticChangeType highestSematicChange = SemanticChangeType.NONE;
    changeEvents =
        changeEvents.stream().filter(changeEvent -> changeEvent.getCategory() == changeCategory).collect(Collectors.toList());
    ChangeEvent highestChangeEvent =
        changeEvents.stream().max(Comparator.comparing(ChangeEvent::getSemVerChange)).orElse(null);
    if (highestChangeEvent != null) {
      highestSematicChange = highestChangeEvent.getSemVerChange();
    }
    return ChangeTransaction.builder()
        .changeEvents(changeEvents)
        .timestamp(currentValue.getCreatedOn().getTime())
        .rawDiff(rawDiffRequested ? rawDiff : null)
        .semVerChange(highestSematicChange)
        .actor(currentValue.getCreatedBy())
        .build();
  }
}
