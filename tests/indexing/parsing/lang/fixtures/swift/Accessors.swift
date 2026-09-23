struct Vault {
    var stored: Int = 0
    var multiplier: Int = 1

    var scaled: Int {
        get {
            let base = stored * multiplier
            return base + 1
        }
        set {
            stored = newValue / multiplier
        }
    }

    var summary: Int {
        let doubled = stored * 2
        return doubled + multiplier
    }

    var tracked: Int = 0 {
        willSet {
            log(newValue - tracked)
        }
        didSet {
            log(tracked - oldValue)
        }
    }

    subscript(index: Int) -> Int {
        get {
            let shifted = index + stored
            return shifted * multiplier
        }
        set {
            stored = newValue - index
        }
    }
}
