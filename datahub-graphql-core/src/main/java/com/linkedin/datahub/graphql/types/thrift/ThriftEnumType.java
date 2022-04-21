package com.linkedin.datahub.graphql.types.thrift;

import static com.linkedin.metadata.Constants.*;

import com.linkedin.common.urn.Urn;
import com.linkedin.common.urn.UrnUtils;
import com.linkedin.datahub.graphql.QueryContext;
import com.linkedin.datahub.graphql.generated.AutoCompleteResults;
import com.linkedin.datahub.graphql.generated.EntityType;
import com.linkedin.datahub.graphql.generated.FacetFilterInput;
import com.linkedin.datahub.graphql.generated.SearchResults;
import com.linkedin.datahub.graphql.generated.ThriftEnum;
import com.linkedin.datahub.graphql.resolvers.ResolverUtils;
import com.linkedin.datahub.graphql.types.SearchableEntityType;
import com.linkedin.datahub.graphql.types.mappers.AutoCompleteResultsMapper;
import com.linkedin.datahub.graphql.types.mappers.UrnSearchResultsMapper;
import com.linkedin.datahub.graphql.types.thrift.mapper.ThriftEnumMapper;
import com.linkedin.entity.EntityResponse;
import com.linkedin.entity.client.EntityClient;
import com.linkedin.metadata.Constants;
import com.linkedin.metadata.query.AutoCompleteResult;
import com.linkedin.metadata.search.SearchResult;

import graphql.com.google.common.collect.ImmutableSet;
import graphql.execution.DataFetcherResult;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import javax.annotation.Nonnull;
import javax.annotation.Nullable;

public class ThriftEnumType implements SearchableEntityType<ThriftEnum> {

  private static final Set<String> ASPECTS_TO_RESOLVE = ImmutableSet.of(
    THRIFT_ENUM_KEY_ASPECT_NAME,
    THRIFT_ENUM_PROPERTIES_ASPECT_NAME
  );

  private static final Set<String> FACET_FIELDS = ImmutableSet.of("name");

  private static final String ENTITY_NAME = "thriftEnum";

  private final EntityClient _entityClient;

  public ThriftEnumType(final EntityClient entityClient) {
    _entityClient = entityClient;
  }

  @Override
  public EntityType type() {
    return EntityType.THRIFT_ENUM;
  }

  @Override
  public Class<ThriftEnum> objectClass() {
    return ThriftEnum.class;
  }

  @Override
  public List<DataFetcherResult<ThriftEnum>> batchLoad(
    List<String> urnStrs,
    QueryContext context
  ) {
    final List<Urn> urns = urnStrs
      .stream()
      .map(UrnUtils::getUrn)
      .collect(Collectors.toList());
    try {
      final Map<Urn, EntityResponse> pinterestThriftEnumItemMap = _entityClient.batchGetV2(
        Constants.THRIFT_ENUM_ENTITY_NAME,
        new HashSet<>(urns),
        ASPECTS_TO_RESOLVE,
        context.getAuthentication()
      );

      final List<EntityResponse> gmsResults = new ArrayList<>();
      for (Urn urn : urns) {
        gmsResults.add(pinterestThriftEnumItemMap.getOrDefault(urn, null));
      }
      return gmsResults
        .stream()
        .map(
          gmsThriftEnum ->
            gmsThriftEnum == null
              ? null
              : DataFetcherResult
                .<ThriftEnum>newResult()
                .data(ThriftEnumMapper.map(gmsThriftEnum))
                .build()
        )
        .collect(Collectors.toList());
    } catch (Exception e) {
      throw new RuntimeException(
        "Failed to batch load PinterestThriftEnumItems",
        e
      );
    }
  }

  @Override
  public SearchResults search(
    @Nonnull String query,
    @Nullable List<FacetFilterInput> filters,
    int start,
    int count,
    @Nonnull final QueryContext context
  )
    throws Exception {
    final Map<String, String> facetFilters = ResolverUtils.buildFacetFilters(
      filters,
      FACET_FIELDS
    );
    final SearchResult searchResult = _entityClient.search(
      ENTITY_NAME,
      query,
      facetFilters,
      start,
      count,
      context.getAuthentication()
    );
    return UrnSearchResultsMapper.map(searchResult);
  }

  @Override
  public AutoCompleteResults autoComplete(
    @Nonnull String query,
    @Nullable String field,
    @Nullable List<FacetFilterInput> filters,
    int limit,
    @Nonnull final QueryContext context
  )
    throws Exception {
    final Map<String, String> facetFilters = ResolverUtils.buildFacetFilters(
      filters,
      FACET_FIELDS
    );
    final AutoCompleteResult result = _entityClient.autoComplete(
      ENTITY_NAME,
      query,
      facetFilters,
      limit,
      context.getAuthentication()
    );
    return AutoCompleteResultsMapper.map(result);
  }
}
