namespace java com.company

include "constants.thrift"

struct Foo10 {
    1: i64 bar = 1 (order=2)
    2: i64 constBar = constants.threshold (stage="prod")
    3: double floatBar = 3.0
    4: string stringBar = "hello"
}