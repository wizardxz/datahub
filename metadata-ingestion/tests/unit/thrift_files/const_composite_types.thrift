namespace java com.company

include "enum_types.thrift"
include "include_2.thrift"
include "nested_types.thrift"

enum Color {
  RED = 1,
  GREEN = 2
}

struct CompositeTypes {
    1: Color color = Color.RED
    2: list<list<i64>> l2 =[[1, 2, 3], [1, 2, 3], [1, 2, 3]]
    3: set<i64> s1
    4: map<string, i64> m1 = {"a":1, "b":2}
    5: map<string, set<i64>> m2
    6: list<enum_types.TweetType> l3
    7: list<i64> l1 =[1, 2, 3]
    8: set<nested_types.S1> s2
    9: map<i64, include_2.UserIDs> m3 = {1:[11,111], 2:[22,222]}
    10: enum_types.TweetType color2 = enum_types.TweetType.RETWEET
    11: nested_types.S1 s3 = {'S3':'structValue'}
    12: nested_types.U1 U2 = {"E1":"enumValue", "S2":"structValue"}
}

