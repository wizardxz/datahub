namespace java com.company

include "constants.thrift"

struct Foo10 {
    1: i64 bar = 1 (datahub.terms="term1,term2", size=12)
}(
    datahub.terms="term3,term4"
    case="case1"
)

union Foo6 {
    1: i64 bar1 = 2 (datahub.terms="term5,term6", size=11)
}(
    datahub.terms="term7,term8"
    case="case2"
)