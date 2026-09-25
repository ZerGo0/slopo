func aggregate(rows: [[Int]], limit: Int) -> Int {
    var total = 0

    for row in rows {
        let head = row[0]
        total += head * 2
    }

    while total > limit {
        total -= limit
        total /= 2
    }

    var countdown = total
    repeat {
        countdown -= 1
        total += countdown
    } while countdown > 0

    return total
}

func drain(values: [Int]) -> Int {
    var stack = values
    var total = 0

    while let top = stack.popLast() {
        total += top
    }

    for value in values where value > 0 {
        total += value
    }
    return total
}
