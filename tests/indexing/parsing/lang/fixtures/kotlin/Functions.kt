class Catalog(private val prefix: String) {

    fun greet(name: String) = "$prefix, $name!"

    fun classify(n: Int): String = when {
        n < 0 -> "negative"
        n == 0 -> "zero"
        else -> "positive"
    }

    fun normalize(values: List<Double>): List<Double> {
        val total = values.sum()
        val scaled = mutableListOf<Double>()
        for (value in values) {
            scaled.add(value / total)
        }
        return scaled
    }
}

fun List<Int>.sumEvens(): Int =
    filter { it % 2 == 0 }.sum()

@Deprecated("prefer greet")
fun salute(name: String): String {
    val trimmed = name.trim()
    return "Hi, $trimmed"
}
