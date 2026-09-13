class Loops {

    fun join(parts: List<String>): String {
        val out = StringBuilder()
        for (part in parts) {
            out.append(part)
            out.append(",")
        }
        return out.toString()
    }

    fun fib(n: Int): Long {
        var a = 0L
        var b = 1L
        var count = n
        while (count > 0) {
            val next = a + b
            a = b
            b = next
            count -= 1
        }
        return a
    }

    fun digits(n: Int): Int {
        var value = n
        var count = 0
        do {
            value /= 10
            count += 1
        } while (value != 0)
        return count
    }
}
