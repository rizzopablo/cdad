package calc

// Add returns the sum of two integers.
// Postcondition P1: Add function exists in pkg/calc.
// Postcondition P2: Add(2, 3) returns 5.
// Postcondition P3: Add is a public function (capitalized).
// Postcondition P4: No panics on valid inputs.
func Add(a, b int) int {
	return a + b
}
