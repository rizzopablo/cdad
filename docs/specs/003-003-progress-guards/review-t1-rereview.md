
**Condiciones de sesión (verdict-tuple):** familia de modelo distinta del implementador ✔ · diff completo en contexto ✔ · citas file:line verificables ✔ · spec + review-t1 + decision en contexto ✔ → bucket base **h**. No acepté la conclusión del autor como prueba: leí el código GREEN completo, los 4 focales RED y ejecuté 2 sondas propias en `/tmp/opencode/`.

## Verificado: cierre de los hallazgos de review-t1

- **B1 — CERRADO ✔.** `cdad_guard.py:106-112`: token ausente o no-string ⇒ `flush()` + `run = []` ⇒ no agrupa, no fabrica incidente. Correcto y semánticamente limpio: `flush()` preserva el incidente de una corrida *observada* previa (≥3 entradas con token string), y la señal desconocida rompe la equivalencia en vez de agrupar por `None == None`. Focal cubre token ausente y no-string (`tests/test_003_003_t1_reviewfix.py:214-230`).
- **B2 — CERRADO CON RESIDUO ✘ (ver hallazgo F1).** `validate_trace` (`cdad_guard.py:198-214`) chequea las tres invariantes declaradas en la decisión; CLI las aplica antes de clasificar (`:250-254`, rc=2, stderr, stdout vacío); `OSError` e `JSONDecodeError` capturados con diagnóstico diseñado (`:236-249`). **Pero** queda un camino de "archivo ilegible" con traceback crudo (sonda en vivo, abajo).
- **B3b (opción b) — CERRADO ✔.** La regla emitida ya no afirma canonicalizar (`REPETITION_RULE`, `cdad_guard.py:50-54`: "args as recorded"); la responsabilidad del grabador queda declarada en el contrato `trace-v1` (nota en `guard-trace.schema.json:4`) y en docstring (`cdad_guard.py:63-68`). Focal aserta `"canonical" not in rule.lower()` (`test_003_003_t1_reviewfix.py:305-310`). Coherente con la decisión del orquestador.
- **O1 — CERRADO ✔.** Poll injustificado ⇒ `decision: "unknown"` (`cdad_guard.py:163-166`); focal lo cubre (`test_003_003_t1_reviewfix.py:317-359`). Además está alineado con el spec, que ya lo exigía: "Ausencia de señal fiable ⇒ `unknown` explícito" (`spec.md:126`). No re-abro.
- **Regresiones:** no encontré ninguna. Los fixtures de la suite T1 usan tokens string siempre (grep: `test_003_003_t1_repetition.py:123,141,147`); el GREEN solo rompe el agrupado por señal no-observada, que ningún test previo ejercitaba. Suite 449 passed en `37f9132` tomada como dada (instrucción del orquestador; no repetida). Alcance limpio: RED `2aed630` toca solo `tests/` (1 archivo); GREEN `37f9132` toca solo los 2 archivos de implementación declarados (schema + guard); los docs del rango son bookkeeping del orquestador (0b74d8e/124ea55). Wrapper `scripts/cdad_guard.py` propaga rc=2 intacto (runpy + `SystemExit`).

---

## Hallazgos BLOCKING

### F1 — Residuo de B2: trace existente con bytes no-UTF-8 ⇒ traceback crudo (el cierre de B2 no cubre todo "archivo ilegible")

- **Verdict:** `BLOCKING` · **Bucket:** `h` (sonda en vivo propia) · **Severidad:** Required
- **Evidencia (file:line + sonda):** `skills/cdad-cycle/scripts/cdad_guard.py:236-243`: el `try` del `read_text` captura solo `OSError`. `UnicodeDecodeError` es subclase de `ValueError`, no de `OSError`, y el segundo `except ValueError` (`:246`) está alrededor de `json.loads`, no de la lectura. Sonda (archivo con bytes `\xff\xfe…` dentro de contrato de nombre): `rc=1`, `stdout_bytes=0`, stderr arranca con `Traceback (most recent call last): … cdad_guard.py, line 269`. El resto del error-path sí está diseñado (sondas B1/B2 de la review previa y focales B2 pasan).
- **Consecuencia:** la condición de cierre de la decisión es explícita: "archivo/JSON ilegible ⇒ rc≠0 con diagnóstico, **sin traceback**" (`review-t1-decision.md:6`). Un trace grabado con encoding corrupto (uso real del grabador de T3) produce el diagnóstico no diseñado que B2 mandó eliminar — rc≠0 y sin salida parcial, pero el eje "diagnóstico determinista, no traceback" queda abierto.
- **Cierre verificable:** capturar `UnicodeDecodeError` (o `ValueError`) en la lectura (`:236-243`) con el mismo patrón rc=2 + stderr diseñado; focal nuevo: trace binaria no-UTF-8 → rc≠0, stderr con mensaje diseñado sin "Traceback", stdout vacío.

---

## Hallazgos OPTIONAL

- **F2 — Token `""` (string vacío) se trata como progreso observado y fabrica `changed: false`.** `cdad_guard.py:106` solo exige `isinstance(str)`: con `progress_token: ""` en 5 entradas equivalentes, mi sonda da `rc=0`, 1 incidente, `evidence.progress.changed: false` — la misma fabricación que B1, vía un valor degenerado que el schema no impide. La letra de la decisión ("no-string") se cumple; el espíritu (P5: señal no fiable no es dato) no. **Verdict:** `OPTIONAL` · **Bucket:** `m`. Cierre: una línea (`not isinstance(pt, str) or not pt.strip()` ⇒ desconocido) o exigir token no-vacío en la nota del schema.
- **F3 — Validación solo en el CLI; `classify_trace` conserva el swallow fail-open.** `cdad_guard.py:182-184` sigue tragando `entries` no-lista, y `classify_trace` no llama a `validate_trace`; hoy no hay ningún consumidor por import (grep: tests y wrapper van todos por CLI), así que el escape es latente, no activo. **Verdict:** `OPTIONAL` · **Bucket:** `l`. Cierre: `validate_trace` dentro de `classify_trace` o eliminar el swallow muerto.
- **F4 — Drift de nombres tras B3b.** (a) `canonical_fingerprint` (`cdad_guard.py:62`) ya no canonicaliza nada: el nombre contradice el docstring que lo acompaña; (b) el docstring de interfaz en `tests/test_003_003_t1_polling.py:25` documenta `"decision": "wait" | "escalate"` sin el `unknown` que la implementación ahora emite. **Verdict:** `OPTIONAL` · **Bucket:** `l` (nits; el (b) importa antes de que T3/T4 consuman la interfaz).

## FYI (deuda declarada, no re-abierta por instrucción del orquestador)

- `spec.md:217` (D2) sigue definiendo la huella con "argumentos canonicalizados"; el guard hashea args tal como fueron grabados. La consistencia spec↔código descansa íntegramente en la nota del schema, que nada valida (O2, a deuda). Constato el encadenamiento, no lo re-abro.

## Abstentions

- **Clase de resultado real y tokens reales de la DB (V1):** `observe` no existe; no emito juicio sobre señales que el grabador futuro produzca (afecta el bucket de F2).
- **Frecuencia real de traces no-UTF-8 / token `""` en producción:** depende del grabador (T3); la sonda prueba el camino, no su frecuencia.
- **Re-ejecución de la suite completa:** instrucción explícita del orquestador; 449 passed en `37f9132` tomado como evidencia dada, no verificada por mí en esta pasada.

## Evidencia (comandos y salidas exactas)

| # | Comando | Resultado |
|---|---|---|
| C1 | `git diff --stat 4933ed0..37f9132` | 8 archivos: guard (+89), schema (+1), reviewfix tests (+363), docs de review/estado |
| C2 | `git show --stat 2aed630` / `git show --stat 37f9132` | RED: solo `tests/test_003_003_t1_reviewfix.py`; GREEN: solo guard + schema (alcance limpio) |
| P1 | `python3 skills/cdad-cycle/scripts/cdad_guard.py classify --project-root /tmp/opencode/rr-probe/proj --trace fixture/binary.json` | **`rc=1`, stdout 0 bytes, stderr: `Traceback (most recent call last)`** (F1) |
| P2 | `… classify … --trace fixture/emptytok.json` | `rc=0`, 1 incidente `repetition-without-progress`, `"changed": false` con token `""` (F2) |
| L1 | `grep -rn "cdad_guard\|classify" --include="*.py" …` | sin consumidores por import de `classify_trace` (F3 latente, no activo) |

**Archivos modificados por mí:** ninguno (write_scope `[]`; sondas en `/tmp/opencode/rr-probe/`).
**Commit evaluado:** `37f9132` (GREEN) sobre `2aed630` (RED, tests-only) — trazabilidad RED→GREEN íntegra en el rango; HEAD actual `108b433` no altera los archivos del rango evaluado.

**Resumen:** **1 blocking (F1, residuo de B2) · 3 optional · 3 abstentions.** B1, B3b y O1 están correctamente cerrados; B2 está cerrado en sus tres desvíos de contrato y sus dos sondas originales, pero la familia "archivo ilegible" conserva un escape (no-UTF-8 → traceback crudo, sonda en vivo) que incumple literalmente la condición de cierre de la decisión. Es un fix acotado (un `except` + un focal).
