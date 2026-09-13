class Account(initial: Int) {

    var balance: Int = initial
        get() {
            return field
        }
        set(value) {
            field = value.coerceAtLeast(0)
        }

    init {
        balance = balance + initial
    }

    constructor(initial: Int, bonus: Int) : this(initial) {
        balance = balance + bonus
    }
}
