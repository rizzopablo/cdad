# Review — 004-003 T1 review-fix (re-review focal F1/F2)

> Materializado por el orquestador desde el TEXTO FINAL del reviewer (ADR-003).
> Modelo: `mofgw/glm-5.3-flash`. Sesión: `<ses-7>`.
> Paquete: `004-003-planning-procedures-reviewer-review-002`. Alcance: focal
> (PD-5: sin segunda review completa). **Dictamen: F1 y F2 CERRADOS, sin
> regresiones, 0 bloqueantes.**

**Contrato:** `spec.md` — sha256 re-calculado `ba395fedf46b…bf766` ✓ · **Diff:** `ef81a8a..0c729a3` (implementación `b0acb03`, +13/−1; RED `1d4a062`; registro del orquestador `0c729a3`) · **Modo:** read-only, sesión independiente del implementer ✓.

## Verificación del autor (re-ejecutada por el reviewer)

| Comando | Resultado |
|---|---|
| `sha256sum docs/specs/004-003-planning-procedures/spec.md` | `ba395fed…bf766` ✓ |
| `python3 -m pytest tests/test_004_003_t1_reviewfix.py tests/test_004_003_t1_draft_contract.py -q` | `4 passed in 2.33s` |
| `python3 -m pytest tests/test_packet_prepare.py tests/test_role_packet_render.py tests/test_role_packets.py tests/test_role_packet_consumers.py tests/test_role_packet_review_regressions.py -q` | `52 passed in 147.50s` |

## Cierre de F1 — VERIFICADO ✓ (`cdad_packet.py:2299-2305`)

El guard `if is_declared_draft and role != "reviewer": raise PolicyError(...)` se ejecuta **antes de cualquier publicación**. Verificación estructural adicional: `_contract_for()` (línea 892) **nunca** devuelve `draft-plan` — la triple flag explícita es la única ruta a un contrato borrador, y esa ruta ahora está blindada por rol. **No existe bypass alternativo.** El test RED cubre el caso reproducido (`implementer/green` — rc≠0, ERROR, stdout vacío, sin publicación, estado y árbol sin cambios) más `test-writer/red` como pin de la regla, con control honesto de que `reviewer/review` **sí** tiene éxito (la denegación es por rol, no por flag).

## Cierre de F2 — VERIFICADO ✓ (`cdad_packet.py:2326-2328`)

El `purpose` del input del borrador es `"draft plan for review"` (sin substring "approv"); el flujo no-borrador conserva `"approved contract"`. Fuente única confirmada: el render de PACKET.md (`cdad_packet.py:818`) deriva de `request["inputs"]` — sin copia hardcodeada del wording aprobatorio en la ruta borrador. Grep de `"approved contract"` en el repo: solo la rama no-borrador (2328), el test RED y un fixture preexistente (`test_role_packet_render.py:157`, no-borrador).

## Regresiones en el mismo diff

**Ninguna.** El diff toca solo `prepare()` en `cdad_packet.py`: (a) `is_declared_draft` defaults a `False`, la rama honesta (sin flags) no cambia; (b) ningún consumidor hace branching sobre el **valor** de `purpose` (grep: solo validación de forma, línea 745); (c) `VALID_CONTRACT_KINDS` y el esquema no cambian. Los 52 tests de paquete/roles + los 4 de T1 pasan. La restricción por rol es completa: `ROLE_SUBSTAGES["reviewer"] = {"review"}`.

## Hallazgos

- **Ningún bloqueante nuevo.** F1 y F2 cerrados con sus remedios estructurales exactos, tal como los prescribió la review original.
- **FYI · OPTIONAL · Bucket: l** — F3–F5 de la review original siguen sin abordar (el fix no toca `validate_request`); consistente con sus veredictos no-bloqueantes. Ubicación: `cdad_packet.py:709-733`. No re-emitidos como hallazgos (PD-5: re-review focal; ya registrados en `review-t1.md`).

## Abstenciones

- **No re-ejecutó la suite completa (333 tests)**: ~10 min; la re-verificación se acotó a los 4 tests del review-fix más el subset de regresión de paquetes (52) que ejercita todo consumidor de `prepare()`/REQUEST.json del diff. La cifra "333 passed" se lee como evidencia declarada.
- **No re-verificó los gates de dispatch de los commits de docs** (`ef81a8a`, `0c729a3`): registro declarado.
- **No verificó consumidores externos fuera del repo** que pudieran parsear `purpose`; cubierto parcialmente por `test_role_packet_consumers.py`.

**Dictamen del re-review focal: F1 y F2 CERRADOS, sin regresiones. 0 bloqueantes.**
