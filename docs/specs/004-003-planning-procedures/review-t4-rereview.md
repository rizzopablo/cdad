# Re-review focal T4 — 004-003

> Materializado por el orquestador desde el TEXTO FINAL del reviewer (ADR-003).
> Modelo: `mofgw/glm-5.3-flash`. Sesión: `<ses-22>`.
> Paquete: `004-003-planning-procedures-reviewer-review-007`. Alcance focal (PD-5).
> **Dictamen: F-A y F-B CLOSED y verificados; sin debilitamiento; suite completa
> verificada por el reviewer (356/356). 1 bloqueante de evidencia (R1).**

**Contrato:** `spec.md` sha256 `ba395fed…bf766` ✓.

## Cierres verificados

### F-A — CLOSED ✓
`afbb776` (+1 línea, `skills/cdad-cycle/references/stage-2-specification.md:112`): declara el "Validation plan" por tarea y referencia `planning-contract-draft.md` §4.1 *referenciando, nunca copiando* (PD-12/invariante 6).
Verificación objetiva: conteo de `planning-contract-draft.md` en el consumidor = **exactamente 1**; la línea única nombra "§4.1"; no hay fence `plan-tasks` (sin segundo manual). Test `TestFAConsumerReferencesCanonicalHomeS41Once` **pasa**. Distribución: los mirrors instalados en los 3 hosts reportan `stage-2-specification.md` **OK** tras `install.sh --check`.

### F-B — CLOSED ✓
`899ff30` (+32/−11 en `planning-contract-draft.md`): §4.1 lista literalmente todos los nombres que el esquema consume — `tasks`, `validation_strategy`, `id`, `produce`, `consume`, `depends_on`, `parallel`, `files`, `focal_tests`, `observable_checks`, `regressions`, `integration_gate`, `owner` — y el literal `@validation_strategy` en `focal_tests`, `observable_checks`, `regressions` o `integration_gate`.
Paridad semántica (más allá del test): la lista coincide **nombre por nombre con las claves que realmente consumen** `_plan_tasks_from_contract` / `_check_plan_tasks` / `_check_plan_validation_plan` (`cdad_packet.py:2262,2271-2520`). Ni un nombre que el esquema ignore, ni una clave consumida sin documentar.
Ejemplo honesto: el reviewer extrajo el bloque literal de §4.1 y ejecutó el **validador real** contra él: `token count: 1`, parsea T0/T1 + estrategia, ambos checks pasan → la afirmación "es estructuralmente válido si se ejecuta por el validador" es **verdadera y verificada**. Fence count en el documento = **1**.

### Sin debilitamiento de F2 ni del lock ✓
- `4def0de`: `147/0` (numstat) — adición pura. Los 8 tests previos quedan intactos (8 `def test_` antes → 11 ahora: +f2b/+fa/+fc).
- F2 original intacto (fence en §4, tokens de prosa PD-8, rol mecánico, `count("```plan-tasks")==1`).
- F-C: el lock `TestFCStrategyReferenceAcceptedInRegressions` es un positivo adicional y pasa — la deuda opcional quedó retirada a nivel de test sin costo.
- **Suite: 27/27 (`-k 004_003`) y suite completa independiente: 356 passed / 479 s** — ahora verificada por el reviewer, no aceptada como prueba.

## Hallazgos

**R1 — Falta la compilación de `review-t4.md` (cadena de evidencia rota).** El state (`7083b64`) cita `docs/specs/004-003-planning-procedures/review-t4.md` como evidencia de `review-1-t4`, pero el archivo **no existe** (ni en el worktree ni en el historial); las reviews t1/t2/t3 sí, la t4 no. Además `899ff30` referencia un "F-D de review-t4" que no está definido en ninguna sección. Consecuencia: no se puede leer la review original y la identidad de F-D no es auditable.
**Verdict: BLOCKING para cerrar la etapa T4** (gate de evidencia: una referencia de evidencia apunta a un artefacto inexistente). Bucket m. No es un defecto de código del fix.

**N1 (FYI) — F011 / drift de install preexistente.** `validate-consistency.sh`: 141 PASS / 2 FAIL, ambos de `install.sh --check` con drift en `agents/*.md` de `.claude` y `.config/opencode`. Origen: `sources/roles/*` modificados en `80f9b90` (2026-09-29), nunca reinstalados. Las superficies del fix están en sync. Remedio: `install.sh` fuera de este ciclo.

**N2 (FYI)** — `docs/.cdad-state.json` sin commitear: es el binding del propio paquete en vuelo; mecánica esperada (PD-11), dominio del orquestador.

## Abstenciones

- **F-D:** la definición original del hallazgo no es verificable (review-t4.md no se compiló); se verifica su efecto práctico (§4.1 con nombres de parámetro + ejemplo válido por el validador real), pero la identidad/redacción original de F-D queda **abstención**.
- F-C como *discusión original de la review t4*: no se re-adjudica (PD-5); solo se verifica que el lock existe y pasa.
- Calidad global del texto agregado en stage-2 más allá del contrato: abstención (fuera del alcance focal).

## Evidencia requerida

| Comando (cd `cdad`) | Resultado |
|---|---|
| `sha256sum docs/specs/004-003-planning-procedures/spec.md` | `ba395fed…bf766` ✓ |
| `pytest tests/test_004_003_t4_validation_fields.py -q` | **11 passed** |
| `pytest tests/ -k "004_003" -q` | **27 passed** |
| `pytest tests/ -q -p no:cacheprovider` | **356 passed** in 479.05s |
| Validador real vs. ejemplo §4.1 | `token count: 1` → **schema-VALID** |
| `bash tests/validate-consistency.sh` | 141 PASS / 2 FAIL (F011, preexistente) |
| `bash install.sh --check` | stage-2-specification.md OK ×3 |
| `git show 4def0de --numstat` | tests: **147 / 0** (adición pura) |

**Commits del review-fix:** `afbb776` (F-A), `899ff30` (F-B), `4def0de` (RED del cierre), `7083b64` (registro).

**Veredicto:** F-A y F-B cerrados genuinamente y ninguna garantía debilitada; suite completa verde verificada (356/356). **La etapa T4 no puede cerrar formalmente hasta que `review-t4.md` esté materializado** (R1), con este re-review, antes de pasar a T5/AUDIT.
