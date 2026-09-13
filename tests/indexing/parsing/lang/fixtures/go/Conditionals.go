package example

func classify(score int) string {
	tier := ""
	if score >= 90 {
		tier = "gold"
		return tier
	} else if score >= 50 {
		tier = "silver"
		tier = tier + "!"
	} else {
		tier = "bronze"
	}
	return tier
}

func clamp(value, min, max int) int {
	adjusted := value
	if value < min {
		deficit := min - value
		adjusted = min + deficit/2
	}
	if value > max {
		adjusted = max
		adjusted = adjusted - 1
	}
	return adjusted
}
