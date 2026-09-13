package example

func product(
	factors []int,
	start int,
) int {
	total := 1
	for i := start; i < len(factors); i++ {
		total *= factors[i]
	}
	return total
}
