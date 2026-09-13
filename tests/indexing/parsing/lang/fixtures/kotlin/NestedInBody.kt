fun outerFunction(items: List<Int>): Int {
    fun localFunction(x: Int): Int {
        return x + 1
    }
    return items.get(0)
}
