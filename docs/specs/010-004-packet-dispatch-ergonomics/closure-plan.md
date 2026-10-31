# Plan de cierre — 010-004-packet-dispatch-ergonomics

**Autor:** orquestador CDAD (mandato HITL vigente: `docs/epics/epic-010-documentary-specialization/execution.md`).
**Estado:** plan preparado, **nada de esto ejecutado todavía** por este documento.
**Contrato:** `spec.md` SHA-256 `fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64`.
**Base de la decisión:** reverificación T6 (`review-verification.md`, intento 34): **B1–B4 CERRADOS**, sin bloqueantes nuevos, cierre declarable **cuando se cumplan 7 condiciones**.

Este plan ordena esas condiciones y no las sustituye. Nada de aquí publica, instala ni aprueba: la declaración de cierre y el Memory Bank los aprueba el owner, y publicar es una decisión separada (R1).

## 0. Precondiciones (antes de medir nada)

1. **El fix R-A/R-B tiene que estar dentro del árbol medido.** El packet `010-004-packet-dispatch-ergonomics-implementer-review-fix-003` (implementer/review-fix, `write_scope`: `skills/cdad-cycle/{scripts,references}`) está **preparado y sin despachar**. Mientras no se despache, se reciba y deje sus dos commits, el árbol no es el árbol final y la suite no se corre.
2. **El archivo no rastreado `docs/specs/010-000-continuity-relative-root/discovery.md` (138 líneas) aparece en `dirty` del intento de cierre.** Decisión del owner o del orquestador: incorporarlo (evidencia de una unidad ya cerrada) o declararlo como preexistente ajeno a esta unidad. No se borra.
3. **Un solo paquete activo.** `prepare` de Stage 5 no puede convivir con el packet del fix sin resolverlo (PD-4).

## 1. Orden exacto de ejecución

| # | Paso | Resultado esperado | Quién |
|---|---|---|---|
| 1 | Despachar y recibir `...-implementer-review-fix-003` | dos commits (`fix(010-004)` / `docs(010-004)`) + recibo `pending` | orquestador (begin → verify-begin → transporte → record → receive) |
| 2 | Cerrar el packet del fix en state | `active_packet.status: completed`, sin paquete activo | orquestador |
| 3 | **(a)** Suite completa **una sola vez** sobre el árbol final | intento de cierre con evidencia durable | quien cierra |
| 4 | **(b)** Escribir `closure.md` con la evidencia de (a) | declaración de cierre + límites | orquestador |
| 5 | **(c)** Preparar y despachar el packet del scribe | borradores del Memory Bank | orquestador + scribe |
| 6 | Aprobación del owner del Memory Bank | aprobación registrada | **owner** |
| 7 | Commit `docs(memory):` | Memory Bank actualizado | orquestador |
| 8 | Decisión de publicación | sí/no, con su propio alcance | **owner** |

## 2. (a) Suite completa — un intento, sobre el árbol final

```sh
mkdir -p .cdad/evidence/010-004-closure
git status --short            # vacío, salvo lo declarado en §0.2
python3 scripts/cdad-suite.py close --all --evidence-root .cdad/evidence/010-004-closure
```

Qué acredita el intento, y nada más:

- `attempt.json`: `selection.kind: all`, `commit`, `dirty`, `rc`, `pytest_summary`, `canary.delta_lines`.
- `stdout.log` / `stderr.log` y `canary-before/after.txt` en el mismo directorio de intento.
- **Una sola corrida.** Si falla, se repara y se declara un intento nuevo nombrando el motivo; no se repite la suite sobre un árbol equivalente (re-entry, equivalencia de corridas).

Condición de cierre: `rc=0` y `pytest_summary` sin fallos. El intento es el techo de medición del feature: ninguna otra corrida posterior puede presentarse como evidencia de aceptación.

## 3. (b) `closure.md` — contenido obligatorio

1. **Alcance** (spec §3) y contrato (`spec.md` `fc6b2ccc…`), más el `commit` medido por el intento de cierre.
2. **Las 12 postcondiciones con su evidencia**, sin reescribir la traza ya corregida de `t4-closure.md` §3:

| PC | Evidencia principal |
|---|---|
| PC-01, PC-02 | `t3-closure.md`, `properties-t5.md`, `e2e-t5.md` |
| PC-03 | `t4-closure.md` §3 + B1 cerrado en `review-verification.md` (intake A+C y C/v2 en `sources/roles/architect.md`, 20 derivados, guarda `tests/test_010_004_t6_b1_guard.py`) |
| PC-04, PC-05, PC-06, PC-07 | `t2-closure.md`; PC-04/PC-05 además `e2e-t5.md` |
| PC-07b | `t4-closure.md` §3 + B2 cerrado (`review-verification.md`: helper en `prepare()`, prueba del caso `dispatched`, salvedad documental R-B) |
| PC-08a, PC-08b | `t2-closure.md` / `t3-closure.md`; PC-08a además `properties-t5.md` |
| PC-09 | `t3-closure.md` |
| PC-10, PC-11 | `t4-closure.md` §3 + B3 cerrado (`review-verification.md`: `re-entry.md` «Integrity, observability and fidelity», I-4 e I-5) |
| PC-12 | `t3-closure.md`, `properties-t5.md`, `e2e-t5.md` (recorrido del consumidor instalado aislado) |

3. **Incidentes I-1..I-8** (`docs/epics/epic-010-documentary-specialization/observations-packet-dispatch.md`) con su disposición: resuelto en esta unidad, declarado como límite, o encolado en el backlog.
4. **Límites, en su formulación literal:**
   - **R1:** «La unidad queda cerrada en el repositorio, NO vigente en la instalación.» Con la tabla de hashes **re-medida** (la de `closure-conditions.md` §1 es previa al fix):
     - repo `skills/cdad-cycle/scripts/cdad_packet.py` = `3c0aca3226b3f93f7e2b0a3d8bba5637c86c688b0d83139a8a53e25c18d334df` (medido 2026-10-31, HEAD `c91ff58b`, árbol con el fix R-A **no** incluido todavía)
     - instalación `~/.config/opencode`, `~/.agents`, `~/.claude` = `171fcd1413ec8446272564388fe2165716569e6c3c070f02f4dca8008960e679` (las tres coinciden)
   - **F011:** `make validate` seguirá en FAIL al cierre (`Assert PASS: 182 / Assert FAIL: 1`, rc=2). La condición es **declarado, medido y no oculto**, no PASS.
   - **R3:** las guardas documentales acreditan un token, no obediencia; no se «arreglan» congelando prosa.
   - **Fidelidad del intento 32:** el recibo acredita 2.811 B de confirmación, no el informe sustantivo; `review-fix-t6-report.md:9` lo declara y debe seguir visible.
5. **Estado de los tests del feature:** los 7 archivos, qué cubre cada uno y el resultado del intento de cierre:

| Archivo | Cobertura |
|---|---|
| `tests/test_010_004_t2_red.py` | PC-04, PC-05, PC-06, PC-07, PC-08a |
| `tests/test_010_004_t3_red.py` | PC-01, PC-02, PC-08b, PC-09, PC-12 |
| `tests/test_010_004_t4_red.py` | guarda documental (token `--route C`), PC-12 |
| `tests/test_010_004_t5_properties.py` | PC-01, PC-02, PC-03, PC-08a, PC-12 |
| `tests/test_010_004_t5_e2e.py` | PC-01, PC-02, PC-05, PC-12 |
| `tests/test_010_004_t6_red.py` | B2 (v1 activo) y B4 (localizador del sucesor) |
| `tests/test_010_004_t6_b1_guard.py` | B1 (intake C/v2 y rechazo A+C en fuente y derivados) |

6. **Lo que el cierre NO declara:** vigencia en la instalación, aprobación del owner, F011 en PASS, ni que las guardas acrediten obediencia.

## 4. (c) Stage 5 — packet del scribe (después de `closure.md`)

Se prepara **cuando el packet del fix esté cerrado y `closure.md` exista** (una sola unidad activa, PD-4), y `--input` exige archivos existentes:

```sh
python3 scripts/cdad_packet.py prepare --project-root . \
  --role scribe --substage memory \
  --objective "<entrada de activeContext fechada + transición de progress + ADR solo si hubo decisión arquitectónica>" \
  --input docs/specs/010-004-packet-dispatch-ergonomics/spec.md=contrato aprobado \
  --input docs/specs/010-004-packet-dispatch-ergonomics/review.md=review de Stage 4 (B1-B4) \
  --input docs/specs/010-004-packet-dispatch-ergonomics/review-verification.md=reverificación T6 \
  --input docs/specs/010-004-packet-dispatch-ergonomics/closure.md=declaración de cierre y límites \
  --input docs/activeContext.md=Memory Bank vigente \
  --input docs/progress.md=Memory Bank vigente
```

El scribe escribe **borradores** (`scribe-activeContext`, `scribe-progress`, y `role-report` para un eventual ADR); no aprueba ni commitea. La materialización de `docs/activeContext.md` y `docs/progress.md` va por `cdad_result.py materialize` con su autorización (create-only/CAS contra la base). Un ADR, si corresponde, lo materializa el orquestador bajo ADR-003 en `docs/adr/` —no hay `artifact_kind` para ADR en la tabla cerrada §7.

## 5. Qué aprueba el owner, en este orden

1. **El informe de reverificación** (`review-verification.md`, intento 34): aprobar el dictamen B1–B4 cerrado y la lista de 7 condiciones.
2. **La declaración de cierre** (`closure.md`): alcance, 12 postcondiciones con evidencia, incidentes y límites — incluida la formulación literal de R1.
3. **El Memory Bank** (borradores del scribe). Es no delegable y es lo único que autoriza el commit `docs(memory):`.
4. **La publicación / instalación** (R1). Decisión separada y posterior: hasta que el owner la tome, `make validate` (F011) seguirá en FAIL por diseño y ninguna afirmación de vigencia en el CLI instalado puede sostener un cierre.

**Nada se publica ni se instala antes del punto 4.** El orquestador no publica, no instala y no convierte estos pasos en una aprobación tácita.

## 6. Riesgos y desvíos ya conocidos

- **Un intento de suite, no tres.** El árbol cambia solo con los commits del fix; los commits documentales posteriores no habilitan una corrida nueva.
- **El paquete del fix no puede reutilizarse** para Stage 5: packet distinto, rol distinto, sin mezclar unidades.
- **El `dirty` del intento** incluye cualquier archivo no rastreado que quede vivo (§0.2): se decide antes de medir, no después.
- **La tabla de hashes de R1 se re-mide después del fix** (este documento ya da la medición previa al fix y la de la instalación; `closure.md` debe llevar la posterior).
