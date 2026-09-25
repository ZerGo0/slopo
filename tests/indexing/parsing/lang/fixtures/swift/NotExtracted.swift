protocol Service {
    func handle(request: Int) -> Int
    var name: String { get }
    subscript(key: Int) -> Int { get }
}

func placeholder() {}

let noop: () -> Void = {}

func anchor(values: [Int]) -> Int {
    if values.isEmpty {}

    let first = values.first ?? 0
    let last = values.last ?? 0
    return first + last
}
