package calc

import "testing"

// TestAdd_basic verifies that Add(2, 3) returns 5 (P2: observable postcondition)
func TestAdd_basic(t *testing.T) {
	result := Add(2, 3)
	if result != 5 {
		t.Errorf("Add(2, 3) = %d, want 5", result)
	}
}

// TestAdd_no_panic verifies Add does not panic on valid inputs (P4)
func TestAdd_no_panic(t *testing.T) {
	defer func() {
		if r := recover(); r != nil {
			t.Errorf("Add(2, 3) panicked: %v", r)
		}
	}()
	result := Add(2, 3)
	if result != 5 {
		t.Errorf("Add(2, 3) = %d, want 5", result)
	}
}

// TestAdd_negative verifies Add works with negative numbers
func TestAdd_negative(t *testing.T) {
	result := Add(-2, 3)
	if result != 1 {
		t.Errorf("Add(-2, 3) = %d, want 1", result)
	}
}

// TestAdd_zero verifies Add works with zero
func TestAdd_zero(t *testing.T) {
	result := Add(0, 0)
	if result != 0 {
		t.Errorf("Add(0, 0) = %d, want 0", result)
	}
}
