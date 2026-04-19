package main

import "fmt"

func greet(name string) string {
	return fmt.Sprintf("Hello, %s", name)
}

type Calculator struct {
	result int
}

func (c *Calculator) Add(a, b int) int {
	return a + b
}

func main() {
	msg := greet("world")
	fmt.Println(msg)
}
