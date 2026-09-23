func outer(values: [Int]) -> Int {
    func increment(n: Int) -> Int {
        let bumped = n + 1
        return bumped
    }

    return increment(n: values.count)
}
