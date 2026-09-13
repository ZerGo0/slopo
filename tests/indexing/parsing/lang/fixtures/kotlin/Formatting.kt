class Formatting {

    fun product(
        factors: IntArray,
        start: Int
    ): Long {
        var total = 1L
        for (i in
             start until factors.size) {
            total *= factors[i]
        }
        return total
    }

    fun tier(score: Int): String
    {
        val label: String
        if (score >= 90)
        {
            label = "gold"
            label.uppercase()
        }
        else
        {
            label = "bronze"
            label.lowercase()
        }
        return label
    }
}
