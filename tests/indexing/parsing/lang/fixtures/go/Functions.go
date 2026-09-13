package example

import "strings"

type Greeter struct {
	prefix string
}

func (g Greeter) Greet(name string, loud bool) string {
	greeting := g.prefix + ", " + name
	if loud {
		greeting = strings.ToUpper(greeting)
		greeting = greeting + "!"
	}
	return greeting
}

func SumEvens(nums []int) int {
	total := 0
	for _, n := range nums {
		if n%2 == 0 {
			total += n
		}
	}
	return total
}

func Normalize(s string) string {
	trimmed := strings.TrimSpace(s)
	return strings.ToLower(trimmed)
}
