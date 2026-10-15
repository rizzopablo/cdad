## Evidencia de verificación (comandos y salidas)

| # | Comando | Resultado |
|---|---|---|
| V1 | `sha256sum docs/specs/003-004-context-continuity/spec.md` | `31cffdb0…1984d78` = contract ✓ |
| V2 | `python3 -m pytest tests/test_003_004_t1_checkpoint.py tests/test_003_004_t1_resume.py -v` | **7 passed in 5.86s** (focales T1; suite no corrida, fuera de instrucción) |
| V3 | Probe A: `begin` con update sin `packet_id`/`attempt` | rc 0; head persiste `packet_id: null`, `attempt: null` → **invalida contra el schema propio** (`None is not of type 'string'`) |
| V4 | Probe B: `resume --json` validado contra `continuity-checkpoint.schema.json` | **NO valida**: `projection` no permitido (`additionalProperties:false`) y `no_op` ausente del required |
| V5 | Probe C: `begin` divergente con misma clave `(exec, pk-1, 1)` y cuerpo distinto | **rc 0**, head sobrescrito, cadena crece (`seq 2`, `prev=body1`) |
| V6 | Probe D: `resume --role test-writer` con referencia `docs/impl-decisiones.md` (en `documentation_roots`) | **Ocultada** pese a ser documentación según la política |
| V7 | `grep -n "token\|impl-" tests/test_003_004_t1_resume.py` | El RED **nunca declara** la convención del token `impl` (solo el fixture `fixture/impl-note.md`, líneas 92/416) |

Alcance del diff: exactamente los 4 archivos del plan T1 (CLI 509 l., wrapper 11 l., 2 schemas) + bookkeeping de orquestador (c6c42ee: state/ledger, dominio del orquestador). El wrapper replica la convención existente de `scripts/cdad_guard.py`. Sin escrituras fuera de `path_policy`.

---

## Hallazgos bloqueantes

### B1 — El render de `resume` declara `continuity-checkpoint-v1` pero no lo satisface
- **Verdict: BLOCKING · Bucket: m · Ejes: correctness/contract**
- **Dónde:** `skills/cdad-cycle/scripts/cdad_continuity.py:446-463` vs `skills/cdad-cycle/assets/continuity-checkpoint.schema.json:8-21`.
- **Evidencia (probe B):** el render emite `"checkpoint": "continuity-checkpoint-v1"` con `projection` extra y sin `no_op`; el schema (`additionalProperties:false`, `no_op` required) lo rechaza. La spec §3 define el contrato como «checkpoint + cuerpo + **render de resume**», así que el schema del diff sub-entrega el contrato aprobado. RED y GREEN son consistentes entre sí; el artefacto schema es el que contradice a ambos.
- **Consecuencia:** T2 (`reconcile-v1`) consume `continuity-checkpoint-v1`; cualquier consumidor que valide el render contra el contrato nombrado fallará. En una metodología contract-driven, un contrato que rechaza su propio render es ambigüedad de contrato, no detalle cosmético.
- **Cierre verificable:** alinear los tres: o el render usa un id de contrato propio (`active-record` ya existe como schema para la proyección), o el schema cubre el render (`no_op` opcional / `oneOf` envelope|render). Condición: `jsonschema.validate(render_de_resume, schema)` pasa (o el render declara otro id con su schema).

### B2 — El filtro P5 por token `impl` es una heurística acoplada al test, no declarada en política ni en RED
- **Verdict: BLOCKING? No — Verdict: OPTIONAL · Bucket: m · Ejes: architecture/contract** *(ver nota de proporcionalidad)*
- **Dónde:** `cdad_continuity.py:72-74, 332-336`; test RED `test_003_004_t1_resume.py:92,415-419`.
- **Evidencia:** el RED exige ocultar `fixture/impl-note.md`, que la política **no** clasifica como implementación, y su docstring declara solo `implementation_roots` — ninguna convención de token. El docstring GREEN (líneas 35-39) atribuye la regla a «the RED contract's convention (V6)»: atribución **falsa** (V7). El GREEN inventó la regla para hacer pasar el test. Probe D: falso positivo real — `docs/impl-decisiones.md` (documentación declarada) se oculta a test-writer.
- **Por qué no bloquea T1:** la dirección del fallo es fail-closed (nunca filtra información hacia roles no privilegiados; roles desconocidos también se filtran, `:341-345`), el regex es acotado (`(^|[-_.])impl(?:[-_.]|$)`), y el efecto práctico hoy es bajo. Pero es un escape de contrato: una regla de clasificación de rutas nace en GREEN fuera de la política, que es la fuente declarada de verdad (`path_policy` del propio packet).
- **Cierre verificable:** promover la convención a la política (`path_policy.implementation_name_tokens: ["impl"]`) o a la spec (§V6), y corregir la atribución del docstring; o mover el fixture del test bajo un root de implementación declarado. Elegir UNA fuente de verdad.

*(Calibración: B2 es deuda declarable, no defecto observable bloqueante de las postcondiciones P1/P2/P5/P7 de T1 — el comportamiento observable pedido por P5 se cumple. Lo escalo a blocker solo si el orquestador rechaza reglas fuera de política por principio.)*

---

## Hallazgos opcionales / deuda

### O1 — `begin` divergente con la misma clave hoy sobrescribe el head en silencio (rc 0)
- **Verdict: OPTIONAL · Bucket: m · Eje: correctness**
- **Dónde:** `cdad_continuity.py:277-296` (el no-op exige cuerpo idéntico; el resto cae al append).
- **Evidencia (probe C):** mismo `(execution_id, packet_id, attempt)`, cuerpo distinto → rc 0, head sobrescrito, cadena crece. El criterio 3 de la spec exige «conflicto/escalado (no sobrescribe)».
- **Atenuante:** el RED (`test_003_004_t1_checkpoint.py:65-66`) y el plan (T2 focales) **declaran esta faceta para T2** — no es omisión del implementer. El orden del plan protege la adopción real (T4 depende de T2/T3). **Riesgo residual:** en la ventana T1→T2, el mecanismo write-ahead de D6 se comporta al revés de su propósito si alguien re-comienza con cuerpo divergente. T2 **debe** cerrarlo antes de T4; sugerencia barata: fail-closed con `ContinuityError` en begin divergente por clave, ya en T2.

### O2 — Update sin campos de contrato produce head schema-inválido en silencio
- **Verdict: OPTIONAL · Bucket: m · Eje: correctness**
- **Dónde:** `cdad_continuity.py:197-210, 254-296` (sin validación de `packet_id`/`attempt`).
- **Evidencia (probe A):** `begin` rc 0 con `packet_id: null` → head inválido contra el schema propio; además la clave de idempotencia `(execution_id, None, None)` pierde discriminación. La postura del módulo (`ContinuityError` = «designed, deterministic failure») pide fail-closed; aquí falla abierto.
- **Cierre:** validar en `_canonical_body` que `packet_id` es string no vacío y `attempt` entero; rc≠0 con delta nombrado. Natural incluirlo en el RED de T2.

### N1 (Nit) — `--json` se acepta y se ignora
- **Dónde:** `:480, 490` (el flag nunca se lee; la salida es siempre JSON). La firma §3 lo declara opcional — el modo no-JSON queda indefinido. Sin efecto en los focales (siempre pasan `--json`). O eliminar el flag o documentar que JSON es el único modo.

### F1 (FYI) — Límites del modelo de tamper, para declarar en T2/T3
1. **Rollback/replay:** restaurar un head más viejo + sus bodies pasa toda la verificación de `resume` (`seq` no se contrasta contra nada persistido; solo head + bodies content-addressed sobreviven, `:216-251`). Es la familia split-brain/cabezas divergentes → T2 (D7). No bloquea T1: los cuatro negativos de P1 (criterio 2) están cubiertos y cada uno falla rc≠0 con delta nombrado (verificado por test + lectura de `:351-404`).
2. **Tamper auto-consistente** (reescribir head+body+refs): indetectable por diseño — no hay firma; el digest solo prueba consistencia interna. `_verify_references` usa `root / str(rel)` crudo (`:397`), alcanzable solo vía ese tamper fuera de modelo. Declarar el límite en `references/continuity.md` (T3) en vez de darlo por resuelto.
3. **`_write_synced` sin `fsync`** (`:110-116`): durabilidad write-ahead contra crash de proceso, no contra pérdida de energía. Aceptable MVP; no llamar «inmutable» más allá de lo que prueba.

---

## Verificación positiva de los focales (lo que sí probé)

- **P1:** round-trip determinista (mismo input, dos proyectos → mismo `body_sha256`; cuerpo sin paths absolutos ni timestamps), cadena `seq/prev` con digest real de referencias, y los 4 negativos de tamper vía `resume` con delta nombrado — 7/7 focales en verde (5.86s).
- **Invariante 1/D3:** escritura confinada a `.cdad/executions/<id>/continuity/**`, `docs/.cdad-state.json` intacto (aserción de test + probes). El CLI nunca aprueba ni escribe state.
- **P2:** render frío reconstruye goal/decisions-con-rationale/authority/uncertainties/next_action con stdin cerrado, rc 0.
- **P7:** exceso de `--max-bytes` (explícito y default 16 KiB) → rc≠0 sin truncar y **sin persistir nada** (aserción byte-a-byte del store vacío).

---

## Abstentions

1. **Suite completa + validadores (criterio 10):** no la corrí — la instrucción del orquestador acota a focales T1. La evidencia del gate (494 passed) en ledger #6 corresponde al árbol pre-commit, no a `9705aec` exactamente: el orquestador decidirá si exige re-corrida sobre el commit.
2. **V5 (¿`resume` genera `packet-metric` de reconstrucción en 001?):** la spec dice «a fijar en RED», pero ni el RED ni el plan T1 lo abordan. Sin evidencia para juzgar si fue resuelta u olvidada — potencial incertidumbre huérfana; escalar al orquestador antes de T2.
3. **Comportamiento de `install.sh` con el nuevo wrapper:** fuera del diff y del packet; el wrapper sigue la convención existente, pero no verifiqué el flujo de instalación.

**Commit revisado:** `9705aec` (implementer) + `c6c42ee` (bookkeeping orquestador, en rango). Ningún archivo modificado por esta revisión (write_scope vacío).
