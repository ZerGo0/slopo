package example

func join(parts []string) string {
	out := ""
	for _, part := range parts {
		out = out + part
		out = out + ","
	}
	return out
}

func fib(count int) int {
	a, b := 0, 1
	for i := 0; i < count; i++ {
		next := a + b
		a = b
		b = next
	}
	return a
}

func drain(value int) int {
	steps := 0
	for value > 0 {
		value = value / 10
		steps = steps + 1
	}
	return steps
}
