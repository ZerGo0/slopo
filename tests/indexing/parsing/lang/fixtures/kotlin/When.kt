class Grades {

    fun points(grade: String): Int {
        var score = 0
        when (grade) {
            "A" -> {
                score = 4
                score = score * 10
            }
            "B" -> {
                score = 3
                score = score + 1
            }
            else -> {
                score = 0
            }
        }
        return score
    }

    fun summarize(values: List<Int>): String {
        val label = when {
            values.isEmpty() -> "empty"
            values.sum() > 100 -> {
                val total = values.sum()
                "big:$total"
            }
            else -> values
                .max()
                .toString()
        }
        return label
    }
}
