class Conditionals {

    fun describe(score: Int): String {
        var tier: String
        if (score >= 90) {
            tier = "gold"
            return tier + score
        } else if (score >= 50) {
            tier = "silver"
        } else {
            tier = "bronze"
            tier = tier + "!"
        }
        return tier
    }

    fun settle(value: Int, min: Int, max: Int): Int {
        var adjusted = value
        if (value < min) {
            val deficit = min - value
            adjusted = min + deficit / 2
        }
        if (value > max) {
            adjusted = max
            return adjusted - 1
        }
        return adjusted
    }
}
