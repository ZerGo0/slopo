interface BodySizes {

    fun emptyBody() {}

    @Deprecated("use takeFirst instead")
    fun annotatedWithLogic(items: List<Int>, limit: Int): List<Int> {
        val result = mutableListOf<Int>()
        for (item in items) {
            if (result.size >= limit) {
                break
            }
            result.add(item)
        }
        return result
    }
}
