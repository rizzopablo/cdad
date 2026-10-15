# Re-review focal T1 — 003-002-artifact-tools

> Materializado por el orquestador desde el TEXTO FINAL del reviewer (ADR-003).
> Modelo: `mofgw/glm-5.3-flash`. Sesión: `<ses-35>`.
> Paquete: `003-002-artifact-tools-reviewer-review-002`. Alcance focal (PD-5):
> cierre de R1 + locks R2/R3/R5. **Dictamen: R1 CERRADO y verificado
> empíricamente; sin bloqueantes activos. T1 cierra.**

**Contrato:** `spec.md` sha256 `ba73e645…f37` verificado ✓ · **Delta:** `980940d..2106766`.

## Evidencia medida por el reviewer

| Chequeo | Resultado |
|---|---|
| `git diff 2106766 -- cdad_result.py` | vacío — el árbol == el commit del fix ✅ |
| `git diff 980940d..2106766 --stat` | solo `cdad_result.py` +8/−3 ✅ |
| **RED empírico (pre-fix)** | el reviewer extrajo el script de `980940d` a un espejo en `/tmp` y corrió la suite review-fix contra él: **R1 FAIL** con la firma exacta del defecto (`rc=0 stdout='VALID: receipt'`; el archivo de escape fuera del root se leyó) y los 6 locks pasan → **RED no vacuo, reproducido por el reviewer, no citado** |
| GREEN focales | `unittest discover -p "test_003_002_t1*.py"` → **14/14 OK** |
| Suite completa | `unittest discover -s tests` → **378 OK (514.7 s)** — cierra la abstención PD-5 de la review anterior |

## R1 — CERRADO · bucket m

El fix (`2106766`, `_verify_durable`) implementa exactamente el remedio: `_segment(part.get("name"), …)` antes de la junction, en la función compartida por **ambos** call sites (retry y `validate-receipt`). `_segment` hace `fullmatch` de `[A-Za-z0-9][A-Za-z0-9._-]{0,127}` sobre todo el string + rechazo explícito de `..`.

**Sin debilitamiento:** el cambio *estrecha* la validación; los receipts legítimos siempre llevan nombres validados como segmento en la creación (`:202`), y toda la regresión es verde.

## Locks R2/R3/R5 — verdes

R2a (kill-pre-publish + retry), R2b (concurrencia idéntica), R3 (manifest trusted in-scope + `renamed`/`previous_path`), R5 (validate-receipt positivo/negativo): todos OK, y **también contra el código pre-fix** → locks genuinos, no tests acoplados al fix.

## Otros

- **FYI (bucket l, OPTIONAL):** `_verify_durable` no re-verifica unicidad de `parts[i].name` en un recibo forjado; sin impacto observable (un duplicado solo relee el mismo archivo) y §3 la exige y la enforcea a nivel descriptor (`:204-205`).
- **R4 y R6 a deuda** (opcionales), como declaró el ledger con justificación; fuera del alcance focal.

## Abstenciones

1. Las abstenciones de la review anterior quedan **disueltas**: la suite completa (378) la corrió el reviewer sobre el estado exacto del fix, y R2b/kill corren en vivo.
2. No repitió la auditoría línea a línea de P1–P6 fuera de `_verify_durable` (focal PD-5).

## Dictamen

R1 cerrado y verificado empíricamente; locks verdes; el fix no debilitó nada observable. **T1 sin bloqueantes pendientes.**
