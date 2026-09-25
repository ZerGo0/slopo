func within(
    values: [Int],
    lower: Int,
    upper: Int
) -> [Int] {
    var kept: [Int] = []
    for value in values {
        if value >= lower
            && value <= upper {
            kept.append(value)
        }
    }
    return kept
}

func categorize(code: Int) -> String {
    switch code {
    case 1,
        2,
        3:
        let mapped = code * 10
        return "low \(mapped)"
    default:
        return "high"
    }
}
