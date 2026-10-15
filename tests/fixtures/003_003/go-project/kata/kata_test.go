// Test co-ubicado del fixture de generalidad T4 (P8): vive junto a kata.go
// (misma carpeta/package), convención Go de tests co-ubicados.
package kata

import "testing"

func TestSnapInvierte(t *testing.T) {
	cases := map[string]string{
		"":      "",
		"hola":  "aloh",
		"ab":    "ba",
		"ñandú": "údnañ",
	}
	for in, want := range cases {
		if got := Snap(in); got != want {
			t.Fatalf("Snap(%q) = %q, want %q", in, got, want)
		}
	}
}
