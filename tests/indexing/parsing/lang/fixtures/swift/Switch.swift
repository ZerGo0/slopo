func label(code: Int) -> String {
    switch code {
    case 0:
        return "zero"
    case 1, 2, 3:
        let doubled = code * 2
        return "small \(doubled)"
    case let n where n < 0:
        return "negative \(n)"
    default:
        let capped = min(code, 100)
        return "big \(capped)"
    }
}

func route(event: Event) -> Int {
    switch event {
    case .tap(let x, let y):
        let sum = x + y
        return sum
    case .scroll:
        return -1
    }
}
