// Package kata — fixture de generalidad T4 (P8): proyecto Go mínimo con
// tests CO-UBICADOS (el test vive junto al código que verifica, convención
// Go para ubicación de tests; el repo CDAD en cambio usa tests/ plano).
// Este paquete existe para probar que la capacidad del guard generaliza a
// proyectos Go; no es producto y no se usa fuera de los fixtures 003_003.
// La traza go-project-trace.json registra el ciclo TDD (rojo -> verde) sobre
// este par código+test co-ubicado; el estado del fixture es el final (verde).
package kata

// Snap devuelve los caracteres de s en orden inverso (por rune, no por byte,
// para que los casos con caracteres multibyte del test co-ubicado pasen).
func Snap(s string) string {
	r := []rune(s)
	out := make([]rune, len(r))
	for i, c := range r {
		out[len(r)-1-i] = c
	}
	return string(out)
}
