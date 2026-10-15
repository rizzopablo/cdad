# RED correctivo posterior al POST-AUDIT

Fecha: 2026-09-17. Test-writer en sesión nueva `gpt-5.6-sol`; sólo modificó los
tres tests de la feature.

Suite focal: **20 métodos, 16 fallos, cero skips y cero `BLOCKED`**, 79.382 s.

- 13 fallos, uno por pareja rol/subfase: falta metadata pública
  `instruction_sources`.
- 3 fallos P5: el validator acepta `outcome="unknown"` y timestamps no RFC3339.
- Las matrices ampliadas P2/P4 pasan.
- La paridad P6 ahora exige éxito real y también paridad de error inválido.
- Se retiraron todos los retornos exitosos `BLOCKED`.

Los tests agregan oráculo semántico por rol sin congelar el texto completo,
matriz de autoridad/vencimiento/basic, paths/scopes faltantes, estado/métricas y
paridad instalada. El test-writer no leyó implementación.

Status: RED verified; GREEN required.
