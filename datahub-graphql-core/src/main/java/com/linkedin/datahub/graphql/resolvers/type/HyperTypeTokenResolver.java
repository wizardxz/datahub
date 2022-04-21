package com.linkedin.datahub.graphql.resolvers.type;

import com.linkedin.datahub.graphql.generated.HyperTypeTextToken;
import com.linkedin.datahub.graphql.generated.HyperTypeUrnToken;
import graphql.TypeResolutionEnvironment;
import graphql.schema.GraphQLObjectType;
import graphql.schema.TypeResolver;

public class HyperTypeTokenResolver implements TypeResolver {

  private static final String TEXT_TOKEN = "HyperTypeTextToken";
  private static final String URN_TOKEN = "HyperTypeUrnToken";

  @Override
  public GraphQLObjectType getType(TypeResolutionEnvironment env) {
    if (env.getObject() instanceof HyperTypeTextToken) {
      return env.getSchema().getObjectType(TEXT_TOKEN);
    } else if (env.getObject() instanceof HyperTypeUrnToken) {
      return env.getSchema().getObjectType(URN_TOKEN);
    } else {
      throw new RuntimeException(
        "Unrecognized object type provided to type resolver"
      );
    }
  }
}
