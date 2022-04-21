namespace java com.company

include "enum_types.thrift"
include "include_2.thrift"
include "nested_types.thrift"

struct CompositeTypes {
    1: list<i64> l1
    2: list<list<i64>> l2
    3: set<i64> s1
    4: map<string, i64> m1
    5: map<string, set<i64>> m2
    6: list<enum_types.TweetType> l3
    7: map<i64, include_2.UserIDs> m3
    8: set<nested_types.S1> s2
}

