# Closure — 016-003-suite-review-tranche-1

**Epic:** `epic-016-traceability-and-suite-review` — orden 3/3. **Cerrada:** 2026-11-04. No publicada ni desplegada.
**Contrato:** `docs/specs/016-003-suite-review-tranche-1/spec.md`, sha256 `b3f91691e9cd44e32b60f5fa9aa98b42fffa9e363757a4ec28592622d069f9c4`.

## Resultado

Existe la revisión del primer tramo del 20 % de la suite, con control estructural automático y revisión semántica
independiente: el selector produce una selección congelada y reproducible (398 nodeids de 1 988, revisión
`120fa8b9`), el validador exige una fila por nodeid con comprobación, consecuencia, evidencia y disposición R2, y
resuelve las obligaciones tanto por marcadores reales como por el índice legacy de 016-001 (extensión con
`--registry`, nacida de un defecto real detectado a mitad del tramo). Las 398 filas están auditadas, con 0
candidatos, 25 unidades con registro de vínculo validado y el costo medido con proyección y decisión autorizada.

Lo que la feature **no** promete: no acredita que la suite no tenga redundancia, no autoriza poda y no sustituye la
revisión semántica. La ausencia de candidatos deja el costo experimental sin calibrar, y así queda declarado.

Commits principales: RED `39d54116`, GREEN `a2321a66`/`7568db1f`; defecto del validador RED `37af51dc`, fixture
`34e628f4`, GREEN `81c6d0fd`; lotes `4a8cce87` (B1a), `b5cc2467` (B1b), `9cf0d6c9` (B2a), `3e283a39` (B2b),
`70ce4865`+`45f99492` (B3/B4), `82264fcc` (B5), `56faf334` (B6), `310cb2ed` (B7), `ab39889f` (B8), `3dddebd5` (B9),
`04240f5f` (B10), `5771cace` (B11), `f92aaca1` (B12); cierre del tramo `77717c1e`; fixes de la revisión `0b6046a9`
(H1), `6bdbb854` (H2/B1/B2/O1/O2), `afbb4c2e` (O3/O4), `8805eaff` (N1/N2/N3); POST-AUDIT `94c86e80`.

## Evidencia

- `tranche-1/selection.json` + `collection.json`: 398 de 1 988 nodeids; `select` reproducible byte a byte.
- `tranche-1/audit.json`: 398 filas, una por nodeid, 398 `Mantener`, 0 candidatos, 12 filas con incertidumbre
  declarada, 36 módulos y 25 contratos.
- `cdad_suite_review.py validate` sobre el tramo real con los 26 registros: `ok`, 398 filas, 0 candidatos, 0 errores.
- `cdad_contract_links.py validate`: 26/26 registros rc 0; el registro de la propia unidad con `--baseline` contra la
  colección viva (1 994 nodeids) rc 0, con los 6 verificadores R-A..R-F vinculados a PC-1..PC-10.
- `pytest tests/test_016_003_suite_review_tranche_1.py`: 6 passed; con 016-001/016-002: 22 passed.
- `python3 scripts/cdad-suite.py validate`: `ok` (1 994 nodeids, 238 módulos, 31 entradas de mapa); el módulo queda
  inventariado con sus 6 verificadores en `suite-review-tranche`.
- `tranche-1/costs.json`: 17 actividades de auditoría, revisión independiente, cierre con 31 comandos medidos y 3
  bloques de preparación compartida; 22 sesiones; 7 081,8 s de auditoría (17,79 s por test), 8 692,5 s agregados por
  unión de intervalos, 9 643,7 s de reloj; 2 716 861 tokens de entrada, 702 509 de salida y 92 903 503 de lectura de
  caché; proyección del resto (1 590 nodeids) 29 986,6 s ≈ 8,3 h, declarada como cota alta.
- `tranche-1/decision.md`: decisión autorizada de continuar con el tramo 2 con cambios explícitos de método, con
  responsable, autoridad (delegación HITL del dueño, 2026-11-02), motivo, evidencia y alcance; sin autorizar poda,
  backfill ni reescritura de contratos cerrados.
- `tranche-1/experiments/`: `candidates.json` vacío, `manifest.json` declarando ausencia de copia y workspace,
  bitácora de ausencia de experimentos y `suspicions.json` con S1, S2 y S3 (examinadas, no promovidas, con la
  evidencia que faltaría).
- Revisión independiente en tres pasadas: `review.md` (rechazado: H1 bloqueante, H2 mayor, H3–H5 menores), `review-r2.md`
  (rechazado: H1/H3/H4 cerrados; B1/B2 abiertos sobre el costo) y `review-r3.md` (**aprobado con observaciones**:
  seis cierres verificados contra los archivos y la aritmética de costo al decimal; N1 corregido, N2/N3 declarados).
- Suite completa de la feature: **no realizada** (recomendada al cerrar feature); la exige el gate de cierre del epic.

## Deuda

- **O2 del review:** el volumen de lectura de caché (92,9 M tokens) ya está en `costs.json` y en el informe; falta
  decidir si entra en la noción de costo que el dueño quiere gobernar.
- **N3 del review:** seis filas citan fragmentos que viven en un test hermano que no ejecutan (declaradas con sus
  nodeids en el informe §2). Sustituirlos por aserciones propias requiere otra pasada de auditoría.
- **N2:** el bloque de cierre usa el rótulo `ses_orquestador_cierre`, sin id de sesión del runtime; sus tokens se
  declaran «no disponibles», no cero.
- **S1/S2/S3:** sospechas registradas sin experimento; el costo experimental por candidato sigue sin calibrar.
- La proyección es lineal y por cota alta: no descuenta el ahorro esperado de los cambios de método del tramo 2.
- El tramo es el 20 % más nuevo **por construcción**: no es muestra aleatoria y no autoriza extrapolación.

## Siguiente

Cierre del epic 016 con la suite completa por el gate atribuible; publicación y despliegue quedan reservados al dueño.
