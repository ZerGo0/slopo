func square(x: Int) -> Int {
    return x * x
}

func sum(values: [Int]) -> Int {
    var total = 0
    for value in values {
        total += value
    }
    return total
}

func countHits(rows: [[Int]], limit: Int) -> Int {
    var hits = 0
    for row in rows {
        for cell in row {
            if cell > limit {
                hits += 1
            }
        }
    }
    return hits
}
