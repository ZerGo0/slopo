class Outer {
    class Inner {
        func inside(a: Int) -> Int {
            return a + 1
        }
    }

    struct Point {
        func norm() -> Int {
            return 0
        }
    }

    func outerMethod() -> Int {
        return 42
    }
}
