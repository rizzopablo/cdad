**Paquete:** `003-004-context-continuity-reviewer-review-003` · **Rol:** reviewer · **Sesión:** independiente del implementador (`green-t2-003-004-a1`)
**Rango evaluado:** `071b61b..02bc021` (RED `d14d80d` → GREEN `02bc021`, más bookkeeping `dc91122`/`1641859`; HEAD actual `502a01f`)
**Contrato:** `docs/specs/003-004-context-continuity/spec.md` sha256 `31cffdb0…84d78` — **verificado con `sha256sum`: coincide** ✓

**Focos del orquestador: (1) forma reconcile-v1, (2) expired-authority dominante, (3) reconcile sin escritura ni repetición, (4) split-brain, (5) cierre O1/R-B1/R-B2** — todos evaluados abajo.

## Verificación del autor (lo que corridé yo)

| Comando (stdin cerrado, foreground) | Resultado |
|---|---|
| `sha256sum docs/specs/003-004-context-continuity/spec.md` | `31cffdb0…` = contrato ✓ |
| `python3 -m pytest tests/test_003_004_t1_checkpoint.py tests/test_003_004_t1_resume.py tests/test_003_004_t1_reviewfix.py tests/test_003_004_t2_writeahead.py tests/test_003_004_t2_reconcile.py -q < /dev/null` | **21 passed** (11.76 s) |
| `bash tests/validate-consistency.sh < /dev/null` | 141 PASS / **2 FAIL** (`F011` subagents+odoo, preexistentes: en los worktrees pre-rango `fc184c1`/`6cea734` ya falla el F011 de subagents; la A3 de odoo apunta a contenido de 004-003 — `287f6c7`, ancestro de `071b61b` — y `__pycache__` sin trackear, no a archivos de 003-004) |
| `git diff d14d80d..02bc021 -- tests/` | **vacío → el implementer NO tocó tests en GREEN** ✓ |
| Probes propios (`/tmp/opencode/rev-t2-probes/probe.py`, 4 tempdir sintéticos, stdin cerrado) | ver hallazgos A, C |

**Disciplina RED/GREEN:** RED `d14d80d` verificada solo vía ledger #13 («11 focales, todos AssertionError, re-verificado»); no la re-corro porque el árbol ya es post-GREEN. Mitigado por: GREEN sin ediciones de tests (diff vacío) y 21/21 en verde actual.

---

## Hallazgos (orden por leverage)

### A — `expired-authority` borra la señal de receipt/materialización (foco 2) — Required · **Verdict: OPTIONAL** · Bucket: **m**
**Dónde:** `skills/cdad-cycle/scripts/cdad_continuity.py:642-667` (`_classify`, primer `if`), `:715` (`unknowns` descartados salvo clasificación `unknown`).
**Riesgo P3 real (respondiendo la pregunta del orquestador):** sí oculta el efecto, no arriesga duplicarlo por sí solo. Probe: autoridad vencida + receipt válido + journal de materialización → clasificación `expired-authority` con `reasons` que solo hablan de D4; **ni el receipt ni la materialización aparecen en el envelope** (sin `unknowns`, sin mención). El orquestador no puede distinguir «expiró y el trabajo ya está cerrado» de «expiró sin ningún efecto». `repeat_effect: false` es constante global, así que el CLI nunca ofrece repetir (foco 3 ✓), y tras renovar autoridad un reconcile posterior muestra `received`/`already-closed` — el riesgo de duplicación queda acotado a quien viole D6 (reconciliar antes de todo reintento). Pero es pérdida observable de señal fiable que §2 exige reportar caso por caso, y el caso co-ocurrente (vencido ∧ recibido/cerrado/unknown) **no está en los tests** (el subtest expired-authority no siembra receipt) ni declarado en el RED.
**Remedio estructural:** mantener `expired-authority` como clasificación dominante, pero (i) preservar `unknowns` siempre que existan (no solo con clasificación `unknown`), y (ii) añadir a `reasons` (o un objeto `signals`) los hechos receipt/materialization/dispatch.
**Cierre verificable:** probe vencido+receipt+mat → el envelope menciona el estado del receipt; rc 0.

### B — `resume` en frío (sin head) declara `continuity-checkpoint-v1` violándolo · **Verdict: OPTIONAL**\* · Bucket: **m**
\*Escala a BLOCKING si el orquestador interpreta el tag `checkpoint:` como reclamo de conformancia (así se trató B1 en review-t1).
**Dónde:** `02bc021`, `_run_resume` rama `head is None` (`cdad_continuity.py:745-773`). **Es cambio del rango**: en `071b61b` `resume` sin head era `ContinuityError` (rc≠0); GREEN lo cambió a envelope con `packet_id/attempt/seq/body_sha256 = null`.
**Evidencia:** `continuity-checkpoint.schema.json` exige `seq` integer ≥1, `packet_id` string, `body_sha256` 64-hex — los nulls violan el esquema que el propio envelope declara. Además el render de resume (también preexistente) porta `record`/`projection`/`role` no previstos (`additionalProperties: false`) y omite el `no_op` requerido — no conforma nunca al esquema que su tag nombra.
**Contexto:** el RED (criterio 4) exigió `resume rc 0` en proyecto **sin head** — una extensión de la letra de §2 (que solo garantiza no-error por ausencia de `ACTIVE.json`); la forma de ese envelope de frío no fue fijada en RED (V6) y el GREEN la eligió solo.
**Cierre verificable:** declarar el formulario de arranque en frío en el RED (o tag de contrato distinto / enmienda de schema con variante null), con `jsonschema.validate(envelope_frio, continuity-checkpoint.schema.json)` donde o conforma o ya no reclama el contrato.

### C — `--packet` sin validar: traversal y oráculo alimentable desde fuera del store · **Verdict: OPTIONAL** · Bucket: **m**
**Dónde:** `_run_reconcile` (`:671-690`): `args.packet` se usa directo en `_results_dir`/`_materialization_dir`; a diferencia de `execution_id` (`_safe_segment`, `:195`) no hay validación.
**Evidencia (probe):** `reconcile --packet "../../fixture"` → **rc 0**. La lectura de `receipt.json` escapa del proyecto; un receipt colocado fuera del store (o una errata del operador) puede fabricar la clasificación (`received` para un packet nunca despachado — viola «no se fabrica éxito»).
**Cierre verificable:** `_safe_segment(packet_id, "packet")` en `reconcile` (y extender `_require_key_fields` al segmento de `update.packet_id`); probe `--packet "../../x"` → rc≠0. Cerrar **antes de T3** (`trigger` heredará `--packet`).

### D — `_write_synced` sin `os.fsync` (write-ahead menos durable que 002) · **Verdict: OPTIONAL** · Bucket: **m**
**Dónde:** `cdad_continuity.py:123-129` (flush sin fsync; sin fsync de directorio). Contrasta con el estándar del propio repo: `cdad_result.py:376-389` hace fsync+dir-fsync. El write-ahead (D6) es la garantía contra duplicación en crash: head reportado rc 0 pero bytes no volcados = ventana donde un crash posterior degrada a `not-started` antes del dispatch. MVP-proporcionado, pero cerrear **antes de T4** (adopción real es donde la ventana importa).

### E — Nits (Verdict: OPTIONAL · Bucket: l)
1. `_require_content_fields` (`:279-282`) admite `decision: ""` mientras exige `rationale` no vacía — inconsistencia menor (D11 query «decision+razón»).
2. Criterio 2: de los 4 negativos de P1, solo *body tamper* está testeado vía `reconcile` (`TestP1StaleTamperReconcile`); cadena rota/referencia inexistente/digest de referencia alterado corren el mismo `_verify_*` desde `reconcile:678-682` pero solo se testean vía `resume` (T1). Argumento de equivalencia aceptable en MVP; un focal barato en T3 cerraría la letra del criterio.
3. Estado procesal: `02bc021` (commit de feature GREEN) incluye una edición de `docs/.cdad-state.json` que registra `test-writer-red-003 completed` — out-of-phase dentro del commit del implementer; `502a01f` lo corrigió. Toda la serie actualiza state en `chore` commit; mantener esa pauta.

### F — FYI (sin acción exigida)
1. `begin`/`checkpoint` no consultan `_detect_split_brain`: persiste la divergencia pendiente de un packet hermano mientras se encadenan checkpoints nuevos en el mismo execution. Coherente con «el CLI nunca aprueba» y con el alcance por-packet de reconcile, pero la disciplina de escalado (D7) descansa en el orquestador.
2. `_detect_split_brain` ignora silenciosamente cuerpos no-JSON o con clave alterada (`:572-579` continue) — tamper de cuerpos huérfanos queda sin detección (fuera de la letra de P1, que cubre head+cadena+referencias).
3. **Foco 1/3/4/5 — cobertura confirmada:** forma `reconcile-v1` declarada en RED (`test_003_004_t2_writeahead.py:28-43`) y respetada por GREEN campo a campo (incluye `unknowns[]` no vacío solo en `unknown` — el RED lo fijó así, por lo que el descarte del hallazgo A es fiel al RED pero no a §2); reconcile **nunca escribe y nunca ofrece repetir** (`_emit` constante `repeat_effect: False`, read-only verificado por snapshot byte-a-byte en cada rama + mi lectura de `_run_reconcile`: `_write_synced` inalcanzable); split-brain por misma clave escala rc≠0 nombrando el digest, sin elegir ganador y preservando la evidencia (`test_d7` + `test_o1`); fixtures SIMULACIÓN sin incidente real (receipt 002 escrito atómicamente por `cdad_result.py` — verificado, por lo que «readable ⇒ received» es un oráculo bien fundado).

## Cierre de residuos T1 (foco 5) — **todos cerrados**
- **O1:** divergente con misma clave → rc≠0, head byte-intacto, seq intacta, cuerpo divergente conservado como evidencia (`test_o1` GREEN) ✓
- **R-B1:** 4 cuerpos malformados → rc≠0 en `begin` **y** `checkpoint`, campo nombrado, cero persistencia (`test_rb1`) ✓
- **R-B2:** `--role` sin política → rc≠0 nombrando la política, control positivo rc 0 (`test_rb2` + `_require_policy_for_role:442-453`) ✓

## Abstentions
1. **Suite completa (508) no re-corrida** — el paquete acota a focales T1+T2. Evidencia: ledger #14 (implementer, stdin cerrado). Los validadores sí corridé (2 F011 preexistentes, no causados por el diff; la A3 de odoo apunta a contenido de 004-003 que **no adjudiqué** — fuera del contrato de esta feature).
2. **Disciplina RED de T2**: acepto la doble verificación del ledger #13 sin poder re-producirla sobre el árbol RED.
3. **Instalación (`install.sh --check`, drift F011)**: el drift de las copias instaladas en `$HOME` (`~/.config/opencode/...`) preexiste el rango (worktrees `fc184c1`/`6cea734` fallan igual); no diagnosticé qué copias están stale ni si el drift de `cdad_continuity.py` instalado oculta el GREEN actual.
4. **Semántica del tag `checkpoint:`** en renders de `resume` (¿reclamo de conformancia o marcador de derivación?): ambigüedad de interpretación que la serie no ha fijado por test; queda resuelta condicionalmente en el hallazgo B, no como abstención ciega.

**Archivos modificados por esta revisión:** ninguno (write_scope `[]`; probes en `/tmp/opencode/rev-t2-probes/`, fuera del repo).
**Commits:** evaluados `d14d80d`, `dc91122`, `02bc021`, `502a01f` (rango completo `071b61b..02bc021`); ningún commit emitido.
**Dictamen:** sin bloqueantes duros; 3 Required con verdict OPTIONAL (A, B condicional, C) que recommend cerrar **antes de T3/T4**; nits D/E; focos 1-5 del orquestador resueltos salvo la pérdida de señal de A.
