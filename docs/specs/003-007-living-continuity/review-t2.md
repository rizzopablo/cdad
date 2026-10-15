# Informe de revisión — T2 de `003-007-living-continuity` (P5, P6, O-1)

**Packet:** `003-007-living-continuity-reviewer-review-002` · **Rol:** reviewer (stage 4, `review`) · **Modelo:** mofgw/glm-5.3-flash
**Objeto de revisión:** diff `4417b49..f466ed9` (RED `1d43ac7` + GREEN `f466ed9`)
**Contrato:** `docs/specs/003-007-living-continuity/spec.md` — hash verificado: `3b4e8c4a…afa07c` ✔ (coincide con el packet)
**Inputs adicionales cargados:** `plan.md`, `t2-record-decision.md` (rectifica D5), `review-t1-decision.md` (O-1)

---

## Dictamen

**Sin defectos bloqueantes.** La implementación del GREEN cumple P5, P6, O-1 y las decisiones de contrato en los flujos observables previstos; el RED está bien especificado y el gate pasa íntegro. Quedan **1 hallazgo Required no bloqueante** (contradicción de texto de decisión/`continuity.md` con el comportamiento observable en un estado nuevo alcanzable — verificación propia por sonda), **2 opcionales** y 1 FYI preexistente fuera del alcance. El hallazgo Required queda a adjudicación del orquestador: ajuste de comportamiento **o** enmienda de la decisión/docs con test que fije el resultado nuevo.

---

## Respuestas a las preguntas del orquestador (con evidencia de sondas propias)

1. **¿Un checkpoint con la clave del head siempre encadena al head vigente (prev = body del head)?** Sí. Solidez propia (begin→ckpt→ckpt, misma clave): `seq` 1→2→3; tras el segundo append, `prev_checkpoint_sha256 == body_sha256` del head anterior == `True` (sonda `probe1_chain`).
2. **¿Fork silencioso en uso normal de un único orquestador?** No vía CLI: el append usa siempre `prev = head.body_sha256` y `seq = head.seq+1`; la cadena es lineal. Con h2 en caché local no hay comparación contra un head desactualizado (se recarga en cada invocación). Residual: (a) sin lock, dos invocaciones concurrentes sobre el mismo head apendarían con igual `seq`/`prev` (fuera de "un único orquestador"; nunca estuvo en contrato); (b) ejecutar un comando de un attempt viejo tras avanzar el head se apendea — **preexistente en `4417b49`** (código histórico verificado), no introducido por T2 (FYI-1).
3. **Begin divergente misma clave tras append: rc≠0 y cero escrituras (RU-2)?** Sí, verificado por sonda: rc 1, mensaje `split-brain… diverges from the head`, árbol byte-a-byte intacto; además `reconcile` posterior rc 0 sin escalar (sonda P2a/O4). La faceta `begin` de `test_003_006_t4_ru2_refused_write.py` está intacta (`git show 1d43ac7 --stat`: sólo la clase de la faceta `checkpoint` fue sustituida).
4. **O-1: ¿queda camino para que un body nuevo sea legado?** No. `legacy = ("record" not in body) and declared not in REFERENCE_CLASSES` (cdad_continuity.py:856-859): todo body nuevo lleva `record` (estampado en `_canonical_body:549`, sin default de omisión), y quitar `record`/campos del body rompe el digest en `_verify_body` (fail closed). **Y el body legado real sigue resolviendo por comparación:** resp implementado sobre `tests/fixtures/003-007-legacy-store/` — nota intacta → rc 0, `legacy: true`, `state: "unchanged"`; nota divergida → rc 0 (no bloquea), `legacy: true`, `state: "changed"` (sonda P4a/P4b).
5. **Split-brain tras P5:** sigue detectando ≥2 bodies `record != "checkpoint"` bajo una clave (sondas: begin+huérfano sin record → rc 1 citando el digest; begin+huérfano `record:"begin"` → rc 1). Ya no detecta divergencias entre bodies `record:"checkpoint"` — deuda declarada en spec §6 y documentada en `continuity.md` ("Same-key checkpoint forks are NOT detected"). La reespecificación de la faceta `checkpoint` de `test_003_006_t4_ru2_refused_write.py` es legítima (BL-2, trazado a P5/D5 en su docstring) y no debilita el todo-o-nada: la variante `begin` y el all-or-nothing quedaron intactos (sonda O4 + tests de 003-004 en el gate).
6. **reconcile y resume sobre begin→ckpt→ckpt misma clave:** ambos rc 0; `reconcile` clasifica sin escalar (`escalate: False`, sin `divergent checkpoint heads`); rinde sin split-brain (sonda probe1; abstención de clasificación exacta fue aceptada en `review-draft-001-decision.md`).
7. **`continuity.md` vs código:** coherente en append, `record` (body y sobre), discriminador de legado y límites de detección — salvo la línea del no-op que estructura el hallazgo R-1 (abajo).

---

## Hallazgos

### R-1 · Re-ejecución de un `begin` idéntico después de un append con su misma clave ya no es no-op
- **Severidad:** Required · **Verdict:** OPTIONAL (no bloqueante; queda a adjudicación) · **Bucket:** h (verificado por sonda)
- **Locación:** `skills/cdad-cycle/scripts/cdad_continuity.py:641-655` (`_run_write`: el no-op compara el body solo contra el **head**; la rama `begin` divergente eleva antes de consultar el resto del store) · `skills/cdad-cycle/references/continuity.md:52-54` ("An identical write … is a successful no-op") · `docs/specs/003-007-living-continuity/t2-record-decision.md:16` ("El no-op de `begin` sigue valiendo para un `begin` repetido con el mismo body").
- **Evidencia (sonda propia, proyecto sintético en tmp):** `begin(K1)` → `checkpoint(K1)` (append legítimo P5, head queda en el eslabón checkpoint) → re-ejecutar el **mismo `begin` byte-idéntico** ⇒ **rc 1** con mensaje `split-brain: a begin … diverges from the head`, **cero escrituras** (byte-a-byte), mientras que sin append la misma re-ejecución es no-op `no_op:true` (rc 0). Sólo es alcanzable cuando el head se movió por el append de P5 — estado nuevo que este diff introduce y que ningún test fija ni aprueba.
- **Consecuencia:** viola el enunciado de `t2-record-decision.md` y de `continuity.md`; un retrazado/reintento del begin dentro de su propio flujo de paquete produce una falsa alarma `split-brain` (etiquetado incorrecto de un conflicto que no existe) y degrada la idempotencia que P3 de 003-004 garantiza. Dirección segura (fail-closed, sin escritura, RU-2 preservado) y no alcanzable en la disciplina normal del orquestador (tras el checkpoint existe receipt; un begin re-ejecutado no forma parte del flujo sancionado), por eso no bloqueante — pero requiere adjudicación explícita, no silencio.
- **Cierre verificable (una de dos):** (a) comportamiento — test que demuestre re-ejecución de `begin` idéntico tras append de su misma clave ⇒ rc 0 no-op sin escrituras (p. ej. reconociendo el body idéntico content-addressed de la misma clave en `bodies/`); o (b) de decisión — enmienda de `t2-record-decision.md` y `continuity.md:52-54` que delimite el no-op al estado head=begin y un test que fije rc≠0 como comportamiento deseado. Adjudica el orquestador.

### O-1c · Huérfanos `record:"checkpoint"` quedan invisibles para `_detect_split_brain` y la excepción de orphanos está escrita como "pre-RU-2"
- **Severidad:** Optional-Consider · **Verdict:** OPTIONAL · **Bucket:** h (comportamiento confirmado por sonda O3; la ventana es lectura de código)
- **Locación:** `cdad_continuity.py:894-896` (los bodies `record=="checkpoint"` se saltan la detección) · la ventana `_write_synced(body)` → `_write_synced(head)` en `cdad_continuity.py:665-670` (caída intermedia deja un body huérfano con record checkpoint) · `continuity.md` ("Orphan bodies are not detected … limit of pre-RU-2 orphan bodies").
- **Consecuencia:** un crash entre los dos `fsync` deja un huérfano `record:"checkpoint"` que ninguna detección cubre (los huérfanos descritos en la deudan eran "pre-RU-2"; esta sub-clase es nueva). Deuda ya declarada en spec §6 (forks mismo-key) y límite documentado; el único desajuste es la atribución cronológica del origen de los huérfanos en la frase de `continuity.md`.
- **Cierre:** precisar la frase para cubrir huérfanos del escritor actual (crash entre syncs) — quede dentro de la deuda de forks, ya documentada.

### Nit-1 · `_canonical_body` mapea todo command ≠ `begin` a `record:"checkpoint"`
- **Severidad:** Nit · **Verdict:** OPTIONAL · **Bucket:** m
- **Locación:** `cdad_continuity.py:635-637` (`"begin" if command == "begin" else "checkpoint"`). Hoy el argparse limita a `begin`/`checkpoint`; si mañana entra un tercer comando en `_run_write`, su body se etiquetaría checkpoint en silencio (inversión del principio fail-closed de legado). Sugerencia: enum whitelisted explícito con `else: raise ContinuityError(...)`.

### FYI-1 · Re-ejecución de attempt viejo tras avance del head — preexistente, fuera del alcance
- **Verdict:** no aplica · **Bucket:** m
- Ejecutar un `begin`/`checkpoint` con attempt viejo cuando el head avanzó (`attempt` distinto ⇒ `_same_key` falso) **apendea** un eslabón; el begin duplicado re-ejecutado asi luego dispara `_detect_split_brain` (≥2 bodies por clave). Este flujo preexistía en `4417b49` (mismo fall-through en el código histórico) y ya dependía de la disciplina RU-2 del orquestador (N-3 de `review-t1-decision.md` es deuda por familia análoga). No lo introdujo T2; registrado para trazabilidad, sin acción pedida en este ciclo.

---

## Verificación del autor

- **Ledger (`dispatch-ledger.md` filas 10-11):** RED `1d43ac7` — 5 RED por la razón correcta + 5 guardas verdes, regresión 50/50, V5 medido; reproducido por el orquestador. GREEN `f466ed9` — gate acotado **60/60 (antes 55/5)**, sin suite completa (gate vigente), reproducido por el orquestador en 42 s.
- **Reproducción del reviewer del mismo gate exacto:** `env -u TMPDIR python3 -m pytest -q tests/test_003_007_t*.py tests/test_003_004_*.py tests/test_003_006_t4_*.py < /dev/null` → **`60 passed in 40.71s`**. El árbol actual es idéntico al del run del gate salvo docs/state (`git diff --stat f466ed9..HEAD` = sólo `docs/.cdad-state.json` + `dispatch-ledger.md`), por lo que la evidencia del run aplica al código revisado.
- **RED autenticado sin re-ejecutarlo** (rol read-only; re-corrida histórica exigiría worktree_OUT de write_scope): `1d43ac7` sólo toca tests (`git show 1d43ac7 --stat` = 2 archivos de tests); el fuente vigente en ese commit es el pre-T2 (`4417b49`), que verifiqué textualmente: sin `record` en `_canonical_body`, y el checkpoint misma-key divergente **incondicionalmente** eleva split-brain rc≠0. Las 5 afirmaciones nuevas (append rc 0/seq+1/prev, `record` en body y sobre, no-escalamiento tras append, bloqueo O-1 con rc≠0, faceta P5 de RU-2 exigendo rc 0) **necesariamente rojas** contra ese fuente, con mensajes que nombran la postcondición. Coherente con lo registrado en el ledger.

---

## Cumplimiento de contrato (eje 6)

- **Archivos tocados = plan T2:** RED: create `tests/test_003_007_t2_checkpoint_vs_begin.py` (964 líneas), modify `tests/test_003_006_t4_ru2_refused_write.py` (sólo faceta checkpoint re-especificada, con trazabilidad BL-2 en docstring; variante begin y all-or-nothing intactos — verificado por diff y sonda O4). GREEN: modify `cdad_continuity.py`, `continuity-checkpoint.schema.json`, `continuity.md`. Editados los 3 archivos declarados; **los tests no fueron tocados por el implementer** (`git diff 1d43ac7..f466ed9 -- tests/` vacío).
- **Bookkeeping en el rango** (`t2-record-decision.md`, `docs/.cdad-state.json`, `dispatch-ledger.md`): obra del orquestador en sus commits chore (`d69a7c7`, `718ac9d`, `c921f35`, `3c210ff`), dentro de su autoridad; no toca write_scope del implementer ni del reviewer.
- **Esquema:** `record` declara enum `begin|checkpoint` **sin añadirse a `required`** — coincide con spec §3 ("opcional en el esquema; los escritores nuevos lo emiten").
- **Invariancia 2 (no fabricar digest/límite):** sin digest inventado; `missing`/`unreadable` se respetan (N-1/N-2 de T1 quedan en deuda, reconocidas).
- **P1-P4, P7, P8:** sin regresión — 003-004 y 003-006-T4 en el gate pasan íntegros; el fixture legado versionado no cambió; `resume --role` intacto (fuera del diff).
- **Tests-first/convención:** cada test nombra su postcondición (S1-S8 ancladas a P5/P6/O-1/V5 y a la abstención aceptada); sembrados como datos con convención content-addressed (precedente citado); nunca stores reales; progenitor sintético en tmp; foreground con stdin cerrado y timeout explícito. Respeta el `path_policy` del packet (tmp es espacio temporal).

---

## Evidencia (archivos, comandos, salidas, commits)

**Commits revisados:** `4417b49` → `1d43ac7` (RED: tests) → `f466ed9` (GREEN: 3 archivos impl) · rango Sylphbook: `git diff --stat 4417b49..f466ed9` = 8 archivos, +1187/−71.
**Comandos executas (toda lectura/sólo son дебtimas):**
1. `sha256sum docs/specs/003-007-living-continuity/spec.md` → `3b4e8c4a…afa07c` ✔
2. `git diff 4417b49..f466ed9 -- skills/cdad-cycle/scripts/cdad_continuity.py` (96 líneas), `-- tests/test_003_006_t4_ru2_refused_write.py`, `-- assets/continuity-checkpoint.schema.json references/continuity.md`
3. **Gate:** `env -u TMPDIR python3 -m pytest -q tests/test_003_007_t*.py tests/test_003_004_*.py tests/test_003_006_t4_*.py < /dev/null` → **`60 passed in 40.71s`** (nunca suite completa, nunca background ✔)
4. **6 sondas propias en `/tmp/opencode/rev-003-007-t2/`** (proyectos sintéticos + copias del fixture legado; read-only sobre el repo): cadena begin→ckpt→ckpt misma clave; begin divergente/identico tras append con snapshot byte-a-byte del store; fixture legado intacto y divergido vía `resume`; 4 variantes de `_detect_split_brain` (2 sin-record escalan citando digest; 2 con record=checkpoint no escalan — deuda declarada; huérfano record=begin + begin escalan; begin divergente sin append no escribe y reconcile rc 0). Scripts: `probe_base.py`, `probe1_chain.py`, `probe2b.py`, `probe3.py`, `probe4.py`.

**Escri ORDER:** ninguna (rol read-only; tmp sondeas en `/tmp/opencode/`).

---

## Abstenciones

- **A1 — Re-ejecución independiente del RED en `1d43ac7`:** no re-corrida como ejecución (la reprodución histórica exigería worktree, una escritura fuera de mi write_scope); sustituida por autenticación analítica del motivo de RED (commit sólo-tests + código pre-T2 verificado textualmente + afirmaciones nuevas necesariamente fallas) y por la reproducción ya registrada del orquestador (ledger fila 10). Impacto si estuviera falseado: bajo; el GREEN reproduce el gate 60/60 con idéntico mando.
- **A2 — P9 (aceptación con rotación real) y render sobre los stores reales:** fuera del alcance de esta revisión; owner T3 (orquestador) según plan y spec §5.8 — no se emitirá juicio sobre cumplimiento de P9 hasta esa instancia.
- **A3 — Comportamiento bajo escritores concurrentes (sin lock):** fuera del "un único orquestador" del contrato de uso; no juzgado.

---

**Estado de gate Stage 4 (informativo, no aprueba):** se cumple reporte + evidencia + clasificación; el orquestador debe decidir sobre R-1 (comportamiento vs enmienda de decisión/docs con test que fije el resultado elegido) antes de declarar el cierre. Todo hallazgo viajero completo al paquete de feedback, sin suavizado.
