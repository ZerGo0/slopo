package example

func OuterFunction(x int) int {
	increment := func(n int) int {
		doubled := n * 2
		return doubled + 1
	}
	return increment(x)
}
