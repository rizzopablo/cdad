# GREEN de bloqueantes de review — 003-001-role-packets

Fecha: 2026-09-17  
Base: `ab0e5cc`  
Ejecución: tres implementadores `gpt-5.6-sol` sobre archivos disjuntos.

## Cambios

- CLI: restringe ADR-010 al epic 003, clasifica paths por destino resuelto,
  admite cwd como `project-root`, valida paquetes por bytes y exige identidad
  activa para métricas.
- Instalador: una raíz explícita ya no depende de `HOME`, se canonicaliza y
  rechaza solapamientos con el source; uninstall deriva de un manifest único.
- Agentes: los cinco receptores distinguen paquete canónico validado de flujo
  legacy; el paquete no recarga skills completos y legacy conserva las cargas.

Los implementadores no modificaron tests. Cada segmento pasó sus regresiones
asignadas y validaciones sintácticas/diff.

## Evidencia integrada

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  tests.test_role_packets \
  tests.test_role_packet_render \
  tests.test_role_packet_consumers \
  tests.test_role_packet_review_regressions

Ran 33 tests in 136.283s

OK
```

Resultado: 33/33, cero errores, skips o `BLOCKED`; los 25 tests anteriores y
las ocho regresiones de review pasaron juntos.

