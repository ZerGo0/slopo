package example

func process(xs []int, threshold int) int {
	total := 0
	for _, x := range xs {
		if x > threshold {
			switch {
			case x > 100:
				total = total + 100
				total = total - 1
			default:
				total = total + x
			}
		}
	}
	return total
}
