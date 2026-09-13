package pipeline

class Processor {
    private var onComplete: (() -> Unit)? = null

    fun transform(values: List<Int>): List<Int> {
        val doubler = fun(x: Int): Int { return x * 2 }
        return values
            .filter { it > 0 }
            .map(fun(v: Int): Int {
                val scaled = doubler(v)
                return scaled + 1
            })
    }

    fun configure() {
        this.onComplete = fun() {
            println("done")
        }
    }

    fun summarize(values: List<Int>): Int {
        val total = values.fold(0) { acc, v ->
            acc + v
        }
        return total
    }
}
