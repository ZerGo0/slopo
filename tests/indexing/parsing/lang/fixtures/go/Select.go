package example

func pump(ch chan int, done chan bool) int {
	total := 0
	select {
	case v := <-ch:
		total = total + v
		total = total * 2
	case <-done:
		total = -1
		return total
	default:
		total = 0
	}
	return total
}
