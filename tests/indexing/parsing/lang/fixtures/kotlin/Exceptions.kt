class Exceptions {

    fun parseOrZero(text: String): Int {
        var value: Int
        try {
            value = text.toInt()
            value = value * 2
        } catch (e: NumberFormatException) {
            value = 0
            value = value - 1
        } finally {
            value = value + 1
        }
        return value
    }

    fun elementAt(xs: IntArray, i: Int, fallback: Int): Int {
        var result: Int
        try {
            result = xs[i]
        } catch (e: IndexOutOfBoundsException) {
            result = fallback
            result = result - 1
        } catch (e: NullPointerException) {
            result = 0
        }
        return result
    }
}
