namespace * "com.company"

struct S1 {
    1: S3 structValue
}

union U1 {
    1: E1 enumValue
    2: S2 structValue
}

enum E1 {
    APPLE = 1
    ORANGE = 2
}

struct S2 {
    1: i64 i64Value
}

typedef S2 S3