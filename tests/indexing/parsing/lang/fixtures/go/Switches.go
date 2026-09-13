package example

func label(n int) string {
	switch n {
	case 0:
		out := "zero"
		return out
	case 1, 2:
		out := "small"
		return out + "!"
	default:
		out := "many"
		return out
	}
}

func describe(v interface{}) string {
	switch x := v.(type) {
	case int:
		doubled := x * 2
		return itoa(doubled)
	case string:
		trimmed := x + "!"
		return trimmed
	default:
		return "unknown"
	}
}
