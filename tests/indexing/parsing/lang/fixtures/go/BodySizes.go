package example

func emptyBody() {}

func withLogic(items []int) (int, error) {
	if len(items) == 0 {
		return 0, nil
	}
	max := items[0]
	for _, item := range items[1:] {
		if item > max {
			max = item
		}
	}
	return max, nil
}
