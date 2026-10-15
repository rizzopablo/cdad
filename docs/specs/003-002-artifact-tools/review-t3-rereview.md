# Re-review final T3 — 003-002-artifact-tools (ronda 3, calibrada)

> Materializado por el orquestador desde el TEXTO FINAL del reviewer (ADR-003).
> Modelo: `mofgw/glm-5.3-flash`. Sesión: `<ses-54>`.
> Paquete: `003-002-artifact-tools-reviewer-review-008`. Remedio evaluado: `5c76fee`.
> **Dictamen: CLOSED — T3 cierra. 0 bloqueantes; deudas ponderadas por uso real.**

**Calibración aplicada:** `docs/owner-decision-review-calibration-2026-10-05.md`
(proporcionalidad, cierre por clase, usabilidad como criterio).

## (a) El remedio de clase fail-closed CIERRA la familia — verificado por dos vías

**Vía 1 — tests** (`tests/test_003_002_t3_reviewfix3.py`, 7 tests): R-F1a (×2), R-F1b (×2),
R-F1c (opción no invariante **con selección correcta** → degrada igual) y el lock del caso
canónico. Cada vector con control positivo interno.

**Vía 2 — ejercicio directo de `_argv_test_roots` / `_rel_within`** (independiente de los
tests del autor):

| Forma | Binding | Dictamen |
|---|---|---|
| `unittest -v tests.test_fixture` (R-F1a) | BOUND `['tests']`; con selección sesgada ⇒ `unknown` | **Cerrado** — la posición de la opción ya no importa |
| `unittest tests` paquete 1 segmento (R-F1b) | BOUND `['tests']`; no resoluble ⇒ `None` ⇒ `unknown` | **Cerrado** |
| `discover -s tests -k green_ok` (R-F1c) | **UNKNOWN** (2 razones) aun con selección correcta | **Cerrado** — `-k` no está en `RUN_INVARIANT_FLAGS` |
| `discover -s tests` (canónico §8) | BOUND, declarado ⇒ `valid-current` | **Caso bueno intacto** |

**Por qué es de clase y no enumeración:** (1) whitelist **cerrada** de opciones — toda
opción no listada degrada; (2) `discover` **sin `-s` explícito degrada**; (3) todo objetivo
que no resuelva a árbol contenedor degrada. Las tres fallan hacia `unknown`, nunca hacia
verde.

**Usabilidad (regla 4):** `discover -s tests -v` y `--buffer` siguen aprobando; las
selecciones correctas no son rechazadas. El mecanismo no quedó inusable.

## (b) No-regresión verificada
- Batería de la feature (8 archivos): **69 tests OK**.
- Suite completa: **433 tests OK** — reproduce la cifra del commit.

## Deuda (ponderada por efecto real, NO bloqueante — calibración reglas 1 y 3)
- **[Optional · l] Whitelist más estricta que lo necesario:** flags invariantes no listados
  (`--locals`, `-c`) degradan a `unknown`. Efecto real ≈ nulo (el fallo es del lado
  conservador: nunca un falso verde). Agregar solo si un uso real lo pide.
- **[FYI · l] Doble motivo en `discover -s tests -k X`** (opción y su valor): diagnóstico
  verboso, inofensivo.
- **[FYI · l] `_module_tree` sobre un nombre imposible (`tests..x`)**: sin camino realista
  (el módulo no importa ⇒ no hay exit 0 ⇒ no hay `valid-current`).

## Abstenciones
1. No dictaminó la corrección semántica del texto de la spec ni de la calibración (contrato
   aprobado; su vigencia es del orquestador).
2. No dispuso de observación de dispatch para la corrida r3; la verificación se apoya en
   **reproducción directa**, no en atestados de sesión.
3. Formas de argv fuera del eje T3: la calibración prohíbe abrirlas aquí.

## Veredicto
**CLOSED.** El remedio es genuinamente de clase, cierra R-F1a/R-F1b/R-F1c junto con R1/F1,
mantiene el caso canónico verde y no introduce regresiones. **T3 cierra.**
