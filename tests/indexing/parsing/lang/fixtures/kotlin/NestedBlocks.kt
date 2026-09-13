class Nesting {

    fun process(xs: IntArray, threshold: Int): Int {
        var total = 0
        for (x in xs) {
            if (x > threshold) {
                try {
                    total = total + 100 / x
                } catch (e: ArithmeticException) {
                    total = total - 1
                }
            }
        }
        return total
    }
}
