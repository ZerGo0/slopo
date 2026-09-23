func distance(x: Double, y: Double) -> Double {
    let squared = x * x + y * y
    return squared.squareRoot()
}

func loadAll(ids: [Int]) async throws -> [Int] {
    let head = try await fetch(ids[0])
    let rest = try await fetchMany(ids)
    return [head] + rest
}

class Counter {
    var value: Int

    init(start: Int) {
        value = start * 2
    }

    init?(label: String) {
        guard let parsed = Int(label) else {
            return nil
        }
        value = parsed
    }

    deinit {
        value = 0
        log(value)
    }

    static func zero() -> Counter {
        let created = Counter(start: 0)
        return created
    }

    func advance(by step: Int) -> Int {
        value += step
        return value
    }
}
