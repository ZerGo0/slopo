func transform(values: [Int], factor: Int) -> [Int] {
    let scaled = values.map { value in
        let boosted = value * factor
        return boosted + 1
    }

    let positives = scaled.filter { $0 > 0 }

    let combine: (Int, Int) -> Int = { left, right in
        let merged = left + right
        return merged * 2
    }

    let applied = apply(positives, using: { item in
        let shifted = item - factor
        return shifted
    })

    let reduced = applied.reduce(0) { acc, item in
        return combine(acc, item)
    }

    return [reduced]
}
