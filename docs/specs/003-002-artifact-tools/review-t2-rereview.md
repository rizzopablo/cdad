# Re-review focal T2 — 003-002-artifact-tools

> Materializado por el orquestador desde el TEXTO FINAL del reviewer (ADR-003).
> Modelo: `mofgw/glm-5.3-flash`. Sesión: `<ses-41>`.
> Paquete: `003-002-artifact-tools-reviewer-review-004`. Alcance focal (PD-5).
> **Dictamen: R1/R2/R3 CERRADOS; 0 bloqueos nuevos; 2 FYI + O1–O3 a deuda. T2 cierra.**

**Contrato:** `sha256sum …/spec.md` → `ba73e645…f37` = el del paquete ✓ · **Objeto:** `6886f27..7703658` (5 archivos, +157/−126).

## Evidencia ejecutada por el reviewer

| # | Comando | Resultado |
|---|---|---|
| E1 | `sha256sum spec.md` | coincide ✓ |
| E2 | `git show --stat 92b60cf` | 2 archivos, +41/−1 |
| E3 | `git diff --stat 6886f27..7703658` | 5 files, +157/−126 |
| E4 | `unittest discover -p "test_003_002_t2_reviewfix.py"` | **12 OK** (R1/R2/R3 + R4a/R4b + 7 locks R5) |
| E5 | `unittest discover -p "test_003_002_t2_materialize.py"` | **11 OK** |
| E6 | `unittest discover -p "test_003_002_t1*.py"` | **14 OK** |
| E7 | grep `test-writer-audit` | **0 referencias activas** en código/política (solo históricas) ✓ |
| E8/E9 | Lectura de `materialize` + `_validate_v2_vigency` | state cargado y `validate_state` **antes** de cualquier escritura; `revoked_at`/`status != active` → rechazo ✓ |
| E10 | grep `ROLE_SUBSTAGES['reviewer']` | `{plan-review, review}` = exactamente lo que `_allowed_kinds` admite ✓ |

## Cierres

### R1 — Vigencia de la delegación aplicada · CERRADO · bucket m
`materialize` lee el state real del disco en el instante de la materialización y ejecuta `validate_state` antes de todo efecto durable. El test reproduce el escape exacto de la review (revocación **post-receipt**) y observa la oracle: rc≠0 sin traceback, sin stdout, copia no aplicada, state/receipt/context intactos. **Cierre empírico, no solo por lectura.**

### R2 — Un solo kind de auditoría · CERRADO · bucket m
`artifact-policy.json` ya no define `test-writer-audit`; el universo queda en 11 kinds con **una** fila de auditoría (`test-audit`).

### R3 — Cierre rol↔kind aplicado · CERRADO · bucket m
`_allowed_kinds(role, substage)` implementa la tabla de §7 y se aplica **por copia en el pre-flight**. Cobertura nombre por nombre: los 11 kinds, cada uno en exactamente una fila; roles/substages fuera de tabla → `frozenset()` (fail-closed). También cierra la dirección restringida (un reviewer read-only no puede materializar role-reports ajenos).

## Locks
R4a (journal real, ahora determinista), R4b (journal divergente) y los 7 locks de la matriz §7 siguen verdes; sin regresión en T1/T2.

## Hallazgos nuevos
- **FYI-1 (l):** `validate_state` en su rama **v1** con `model_policy="ordinary"` no consulta `hitl_delegation`. El fix reutiliza el validador exactamente igual que las recepciones (contrato declarado del remedio) y la superficie de la feature es v2 → no es divergencia nueva; deuda preexistente compartida con `receive`.
- **FYI-2 (l):** `docs/specs/003-001-role-packets/spec.md:42` menciona `test-writer-audit.md` en su árbol de docs (otra feature; limpieza editorial).

## Abstenciones
1. Suite completa no re-corrida en este paquete (solo las suites T1/T2); el GREEN del implementer citó 401 passed.
2. FYI-1 verificado por lectura, no por suite (no hay fixture v1-ordinary).
3. Concurrencia de dos `materialize` sobre el mismo journal: §7 no la especifica.
4. FYI-2: editorial de otra feature.

## Dictamen
**Los tres bloqueantes verificables quedan cerrados, sin bloqueos nuevos.** T2 cierra; O1–O3 y los FYI a deuda priorizada.
