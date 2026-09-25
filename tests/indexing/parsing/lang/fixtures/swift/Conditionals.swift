func classify(score: Int, bonus: Int) -> String {
    if score >= 90 {
        let total = score + bonus
        return "top \(total)"
    }

    if score >= 50 {
        return "pass"
    } else if score >= 30 {
        let gap = 50 - score
        return "near \(gap)"
    } else {
        return "fail"
    }
}

func firstPositive(values: [Int]) -> Int {
    guard let head = values.first else {
        let fallback = values.count
        return -fallback
    }

    if head > 0 {
        return head
    }
    return -head
}

func describe(value: Int?) -> String {
    if let value = value {
        let doubled = value * 2
        return "some \(doubled)"
    } else {
        return "none"
    }
}
