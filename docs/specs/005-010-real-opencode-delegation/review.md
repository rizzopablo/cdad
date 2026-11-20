<!-- Materializado por el orquestador Claude desde la entrega del reviewer (paquete 005-010-real-opencode-delegation-reviewer-review-001, mofgw/glm-5.3-flash). -->

# Review formal — 005-010-real-opencode-delegation (etapa 4)

**Reviewer:** cdad-reviewer (GLM, sesión independiente del implementador — anti-bias)
**Packet:** `005-010-real-opencode-delegation-reviewer-review-001` (v1, validado; write_scope=[], repository-read)
**Contrato verificado:** `sha256sum docs/specs/005-010-real-opencode-delegation/spec.md` → `baf195a3…891b` = pin del packet ✓

## Errores y comandos

**Objeto revisado:** rango `06d0e98..ea4b915` (25 commits, HEAD actual = `ea4b915`) tocado solo en el scope declarado:

```
skills/cdad-cycle/scripts/cdad_delegate_opencode.py | 540 +/-
skills/cdad-cycle/references/cli-delegation.md      |  61 +/-
skills/cdad-cycle/references/opencode-delegation.md |  61 +/-
tests/test_005_009_t2_opencode_adapter.py           | 881 +/-
tests/test_005_009_t4_acceptance.py                 |  21 +/-
tests/test_005_010_t{1,2,3,4}_*.py                  | nuevos (533/505/361/455)
```

**Comando(s):** verificado `git log --oneline -5 ea4b915`, `git log --oneline -1 HEAD`, lectura de los 9 archivos del rango, `git log --oneline -1 HEAD`, y del diff `e6479b5`; lectura de los 4 tests nuevos + fixture migrada + admisión PD-10 (docs/specs/005-010-real-opencode-delegation/evidence/pd10-acceptance.md) + stage_history de 005-010 en `docs/.cdad-state.json`.

**Verificación que corrió el revisor (repositorios-read only):**

- `cd tests && python3 -m unittest test_005_010_t1_durable_signal test_005_010_t2_load_mode_invocation test_005_010_t3_references test_005_010_t4_integration` → `Ran 19 tests ... OK (skipped=1)` (el skip es T4, omitido por diseño PD-8).
- `cd tests && python3 -m unittest test_005_009_t1_interface test_005_009_t2_opencode_adapter test_005_009_t4_acceptance test_005_009_t3_spawn_reconciliation` → `Ran 15 tests ... OK (skipped=1)` (regresión de 005-009 sobre la fixture migrada).
- `make validate` en el repo raíz → `Assert PASS: 141 / Assert FAIL: 2` (los 2 FAIL están fuera del alcance de este diff: ver el hallazgo F1).
- Instalación: correr `unittest` necesita `cd tests/` (imports módulos hermanos, `test_005_009_t1_interface`); desde la raíz falla con `ModuleNotFoundError` (no es defecto del producto, es convención de corrida; documentada porque la reproducibilidad lo exige).

**Commit evidence:** `ea4b915` (HEAD) = `docs(005-010): aceptacion PD-10 paso a...`.
**Postcondición contract compliance:** `git diff 06d0e98..ea4b915 -- skills/cdad-cycle/scripts/cdad_delegate.py scripts/cdad-generate.py sources/agents/adapters/opencode.md` → 0 bytes: INV-2 se cumple (la interfaz común, el generador y la fuente canónica de agentes están intactos). Ningún archivo tocado está fuera de los scopes del packet.

---

## Hallazgos BLOCKING

**R1 (Vocabulary: TimeoutExpired del destino clasificado como `transport-error`, hecho material falso)**
- `Verdict: BLOCKING` · `Bucket: m` · `docs/specs/005-010-real-opencode-delegation/spec.md` PD-5 (vocabulario), PD-2 (sin materiales falseados), R-E de §9 (binario legacy que cuelga).
- **Ubicación exacta:** `skills/cdad-cycle/scripts/cdad_delegate_opencode.py:255-258` (TimeoutExpired → AdapterError) y `:782-784` (AdapterError de la invocación → `termination="transport-error"`, diagnosis `"the destination client failed in transport (rc=…)"`).
- **Comportamiento actual:** si el binario/destino cuelga y nunca retorna rc, `subprocess.run` levanta `TimeoutExpired` cuando expira el budget, el adaptador lo convierte a `AdapterError`, y ese error cae en el mismo `except` que los errores reales de arranque (`OSError`), reportando `transport-error` con diagnosis «failed in transport (rc=N)» — **un hecho que NO se verificó**: no hay rc (el cliente no retornó; el adaptador lo mató), no hay fila durable en la base... En realidad: no hay fila correlacionada y el budget expiró → **per la spec, ese escenario material (sin fila / sin idle dentro del budget / cliente sin terminar) es `timeout`, no `transport-error`**. `transport-error` es, por PD-5, «un cliente que **falla en el transporte antes de cualquier fila (`rc ≠ 0` sin señal)**» — un hecho que el adaptador observa, no uno que fabrica. Un binario legacy que cuelga es el riesgo R-E nombrado en la spec: el adaptador, tal en el código, reportaría un hecho falso (`rc=…` inexistente) y una clase que asevera una terminación conocida del transporte cuando el hecho observado es solo ausencia-de-señal-en-la-cota.
- **Consecuencia:** el responsable/coordinador recibe una clase que afirma una falacia de transporte (afecta la reconciliación y la interpretación de reintentos: `transport-error` se lee como «no hubo sesión / fallar antes de sesión», `timeout` como «espera consumida sin señal, la sesión pudo existir»); contradice PD-5 literalmente.
- **Cierre verífico:** distinguir en `_invoke_destination` (`:255-258`) el `TimeoutExpired` del `OSError`, devolviendo `termination="timeout"` con diagnosis honesta («bounded wait exhausted while the destination invocation had not returned; no durable row observed»), y mantener `OSError` (binario no arranca) como `transport-error` con rc/nombre del error real. Igual limpieza para el caso `budget=0.0` (timeout ≤ `WAIT_RESERVE_SECONDS=1.0`, `_wait_budget:440-443` → `subprocess.run(timeout=0.0)`) que hoy también cae en `transport-error`. El hecho debe salir del argv/fixture, no del diagnóstico: añadir una variante del doble cuya invocación supere el budget (por ejemplo, sleep > `TEST_WAIT_TIMEOUT_SECONDS`) para que el test de PD-5 fije la clase esperada.

## Mejoras (verde fuerte)

**R2 (Hallazgo de la evidencia, confirmado: `model_reported` guarda el objeto de modelo de la fila como texto JSON)**
- `Verdict: BLOCKING?` no → `Verdict: OPTIONAL` · `Bucket: m`.
- **Ubicación:** `cdad_delegate_opencode.py:836` (`model_reported=_as_text(row.get("model"))`) y `:462`.
- **Detalle:** cumple PD-6 al pie de la letra (proviene de `session_v2.model`, collectado con provenance), PERO si la fila trae el modelo serializado como objeto JSON (`{"id":…,"providerID":…}`), el I8 queda con texto JSON de baja utilidad para la observabilidad («configured / observed»), ya lo señala la evidencia propia (`docs/specs/005-010-real-opencode-delegation/evidence/pd10-acceptance.md:75-76`). **Cierre:** normalizar (`proveedor/modelo` si la fila lo permite) o, si se conserva verbatim, anotar la provenance para decir que es la representación cruda de la fila (evita que la review de I8 lea `{…}` como modelo). No es falla del contrato; es deuda de calidad de dato.

**R3 (PD-5: dos ramas de `classify` sin cobertura en el doble)**
- `Verdict: OPTIONAL` · `Bucket: m`.
- **Ubicación:** `cdad_delegate_opencode.py:663-668` (succeeded **sin texto final** → `blocked`) y `:680-682` (`idle_outcome` desconocido → `unknown`); fixture `tests/test_005_009_t2_opencode_adapter.py` (`FAKE_VARIANTS`, no incluye variantes `succeeded-no-text` ni `unknown-outcome`).
- **Detalle:** PD-5 declara «succeeded → completed (con texto final presente; **si falta, blocked con diagnóstico**)» y el vocabulario incluye `unknown`; el producto tiene ambas ramas correctas, pero ningún test las fija (el fixture «succeeded» siempre escribe texto final y ninguna variante escribe un `idle_outcome` no declarado). Es la gamma R-C de la spec (el rol que usa herramientas queda sin texto) — el comportamiento real confirmado solo en T4 habilitada. **Cierre:** añadir las dos variantes al doble (PD-7 las espera).

**R4 (Fail-open con `wait.timeout_seconds` ausente)**
- `Verdict: OPTIONAL` · `Bucket: m`.
- **Ubicación:** `cdad_delegate_opencode.py:729-733` (timeout `None` si la config no trae la clave) + `:770-771` (`wait_deadline = now + (None or 0)`) + `_invoke_destination` recibe `budget=None` → `subprocess.run(timeout=None)`.
- **Detalle:** sin `wait.timeout_seconds`, la invocación al destino queda **sin cota** (INV-4 dice «la espera es acotada por `wait.timeout_seconds`»: si la clave falta, hoy esa espera es infinita en la invocación; una config mal hecha o parcial deja desacotado el recurso en la ruta de cuelgue No; también `budget=0.0` con `timeout_seconds ≤ 1.0` produce el dopple de R1). **Cierre:** fail-closed pre-despacho con diagnóstico accionable si la config de ejecución no declara una espera acotada positiva (la spec la exige como campo de la configuración).

**R5 (`_last_assistant_text` carga TODOS los mensajes `assistant` con `fetchall()`)**
- `Verdict: OPTIONAL` · `Bucket: m`.
- **Ubicación:** `cdad_delegate_opencode.py:352-357`.
- **Detalle:** la consulta ordena `seq DESC` pero materializa la lista entera de mensajes `assistant` (cada uno con `data.content[]` que puede contener payloads de herramientas grandes) antes de quedarse con el primero no vacío. Para la corrida real de acá es irrelevante; para sesiones largas es memoria no acotada. **Cierre:** iterar el cursor sin `fetchall()` (lazy, se corta en el primer texto) o `LIMIT 1` cuando la variante synthetic de R-C/#2 lo permita.

**R6 (Docstring del adaptador mezcla numeración de postcondiciones de 005-009 con 005-010)**
- `Verdict: OPTIONAL` · `Bucket: l`.
- **Ubicación:** `cdad_delegate_opencode.py:1-57` (p. ej. «(005-009 T2; PD-4, PD-5, PD-6, PD-7)», «(PD-8/INV-7)», «PD-3» en el punto 2 = modo de carga de 005-009, hoy PD-3 de 005-010).
- **Detalle:** tras 005-010, los mismos IDs (PD-1..PD-10) apuntan a postcondiciones distintas en las dos specs; el docstring ya no es ambiguiguo sin contexto (invitación a recomendar explícito «PD-3 de 005-009» vs «PD-3 de 005-010» para el lector futuro, o referirse por contrato no por postcondición de otra feature). Nit de readability, no de corrección.

**R7 (Path de `sessions_db` sin encoding en el URI SQLite)**
- `Verdict: OPTIONAL` · `Bucket: l`.
- **Ubicación:** `cdad_delegate_opencode.py:381` (`f"file:{store_path}?mode=ro", uri=True`).
- **Detalle:** caracteres `?#` en el path de la config romperían el parse del URI (path truncado → fallo cerrado en el peor caso; `mode=ro` permanece literal, no hay vector de escritura porque el modo queda fijo). La ruta viene de config del dueño (trusted), riesgo real bajo. Si se arregla, `urllib.parse.quote(str(store_path))`.

## FYI (deuda no atribuible a este diff)

**F1 (make validate: 2 FAIL preexistentes, no atribuidos).** `bash tests/validate-consistency.sh` marca F011 «drift de HOME» y `validate-odoo-specialization.sh` marca A3 «sensitive patterns». Verificado: los archivos que matchean (`docs/specs/004-003-planning-procedures/supervision-record.md:165`, `review-t5.md:38`, `tests/test_role_packets.py:50`, `tests/test_005_009_t1_interface.py:30`) **no aparecen en `git diff --name-only 06d0e98..ea4b915`** (grep sobre el rango → 0 coincidencias); son falsos positivos del patrón local NO acotado (el patrón matchea `PROPONE`/`TOPOLOGÍA` case-insensitive), ya registrados como deuda del check en `docs/specs/004-003-planning-procedures/review-t5.md:38` («Remedio: acotar el patrón… — deuda del check, no de T5»). Cumple el criterio de aceptación «los FAIL preexistentes, si los hay, no se atribuyen a este diff».

**Nota de laboratorio de tests (no atribuible):** el `__pycache__` del árbol work se regenera al correr los tests (visto en `git status`); no constituye escritura de producto.

---

## Verificaciones planteadas (todas superadas o fechadas en evidencia)

| # | Verificación | Resultado | Evidencia (comando / archivo:línea) |
|---|---|---|---|
| V1 | Correlación `--session <id>` con id elegido por el adaptador (PD-1) | ✓ | `cdad_delegate_opencode.py:235,769`; test T1 `TestPd1SessionCorrelation`; test T2b; la fixture usa el id recibido (`tests/test_005_009_t2_opencode_adapter.py`, `session_id_written`) |
| V2 | Lectura mode=ro, nunca immutable, nunca escritura (PD-2/INV-3) | ✓ | `cdad_delegate_opencode.py:381` (`file:…?mode=ro`, sin `immutable`); el adaptador no abre tx de write; tests también leen mode=ro (`tests/test_005_009_t2_opencode_adapter.py:721,733`; `tests/test_005_010_t4_integration.py:132`) |
| V3 | Esquema desconocido / no-SQLite / JSON corrupto → `blocked` con diagnóstico que NOMBEA el esquema/columna, sin recibo y SIN esperar de más (PD-2) | ✓ | `:289-312,404-407`; tests T1 `TestPd2FailClosedStoreDiagnostics` (asserts `elapsed < TEST_WAIT_TIMEOUT_SECONDS`); fixture variantes `unknown-schema`, `not-sqlite` |
| V4 | Modo de carga: `subagent` ya no bloque; exigencia = derivado publicado + identidad `session_v2.agent == "cdad-<rol>"` desde la fila durable; SIN fallback genérico (PD-3/INV-6) | ✓ | `:169-211,821-824`; tests T2 `TestPd3SubagentEntryDispatches` (SEED `mode:subagent` → `completed`), `TestPd3UnpublishedDerivedFailsClosed` (pre-despacho, sin invocación), `TestPd3DurableIdentityMismatch` (variante `wrong-agent` con fila foránea `general` → `blocked`, 1 solo argv, sin genérico); registro argv verbatim conservado por fixture (`_argv_record`, `e6479b5`) |
| V5 | `--standalone` por defecto, `--server` por config (exclusivo), `--auto` activada por defecto (PD-4/INV-7/INV-8) | ✓ | `:235-243,727-728`; tests T2 `TestPd4InvocationArgvMatrix` (3 subunits sobre argv observable del binario falso) |
| V6 | PWD del destino == raíz del proyecto explícito, nunca la del coordinador; el hecho viene del runtime real (corrección del orquestador, commit `3c9d3ee`) | ✓ | `:244-254` (env PWD + cwd codifican project_root); test T2 `TestPd4PwdProjectDirectory` (coordinador con PWD ajeno; fila durable → `directory` correcto); el hallazgo real está documentado en `pd10-acceptance.md:71-74` y `stage_history` tdd-t4-integration-test/tdd-green-t2b-pwd |
| V7 | Clasificación desde `idle_outcome`, nunca del rc; recibo `pending`; solo `completed` persiste entrega (PD-5/INV-5) | ✓ | `_classify:652-682` + `delegate:826-830`; tests T1 `TestPd5IdleOutcomeClassification`; fixture variantes → terminaciones (`VARIANT_TERMINATION`) |
| V8 | rc=0 temprano sin fila idle → `timeout`, no `completed` (PD-1)` | ✓ | tests T1 `test_pd1_rc0_before_idle_is_not_completed` (fixture rc=0 + stdout con texto + fila nunca idle) |
| V9 | Observación I8 del worker desde la fila durable con provenance; registro de la interfaz honesto (`model_reported: null`) (PD-6/D6) | ✓ | `:449-478,598-600,836`; tests T1 `TestPd6WorkerI8FromDurableRow` (ROW_MODEL ≠ FAKE_MODEL para discriminar fuente por comportamiento) |
| V10 | La espera es acotada (PD-1/INV-4); el fallo cerrado no se degrada a timeout por esperar de más | ✓ (con la excepción R4) | `_wait_budget/_await_durable_outcome:412-443`; tests T1 asserts de tiempo;_polling `POLL_INTERVAL_SECONDS=0.05` `sleep(min(0.05, remaining))` |
| V11 | Ningún valor del VPS en producto/referencias (INV-7/PD-10) | ✓ | tests T3 `TestInv7ReferencesWithoutVpsValues`; fixture usa `fixture.invalid` (TLD reservado); `exec-config.json` con valores locales, fuera del repo (`pd10-acceptance.md:40-41`) |
| V12 | Referencias: contrato durable SQLite, modo de carga, tabla de modelos obsoleta eliminada y con single-puntero (PD-10) | ✓ | diff de `cli-delegation.md` (secciones nuevas PD-1/2/5 + server/permissions) y `opencode-delegation.md` (dog: `mode:subagent` + fila durable + tabla sin nombres de modelo, puntero a `scripts/cdad-models.sh` + perfil activo) |
| T4 (PD-8) omitida por defecto, habilitada por variable, con diagnóstico en skip; sin valores por defecto del host | ✓ (corrida foco y skip) | `tests/test_005_010_t4_integration.py:154-201` (skip con diagnosis que nombra la variable); suite revisa la omisión (1 skipped en todas las corridas); la corrida habilitada real quedó en `stage_history` (tdd-green-t2b-pwd, sesión `ses_6fb2…` en proyecto temporal) |
| Tests no debilitados en el testfix (`ae600eb`, `e6479b5`) | ✓ | diffs analizados: `ae600eb` reemplaza aserciones (`out['session']==SESSION_ID` constante, contradice PD-1) por correlación real (fila + `session_id_written`) y alias del registro del worker — **fortalece**; `e6479b5` conserva basename de rutas existentes (mismo scrub del tmpdir) y deja verbatim los valores de opciones — no debilita, repara aserción imposible sin producto; `test_005_009_t4_acceptance.py` también refuerza la precondición (antes `!sessions.json.is_file()`, ahora `[None]` sobre `durable_session_rows` del store SQLite) |

---

## Abstenciones

- **Suite COMPLETA (todos los 74 módulos) — no corrida por completo en esta revisión.** intento agotó el time budget (los testsets de 003/004 corren flujos reales largos); verifiqué los 19 tests de 005-010 + los 15 de regresión 005-009 (34 tests, OK con 1 skip por diseño), y la suite focuses (T1/T2/T3 + regresiones de 005-009) que el plan exige para el cierre de cada sub-tarea T (state `stage_history` registra verificación del orquestador por GREEN). No puedo confirmar directamente el postcondición «suite completa verde al cierre» fuera de lo corrido; quedó como assertion del orquestador, no duplicada acá.
- **Corrida T4 habilitada (PD-8)** — no la re-ejecuto (toque el HOME del dueño y credenciales reales presentes en la base: corresponde al dueño/orquestador; la corrida habilitada real está registrada en `stage_history` con `sessions ses_d4b…/ses_6fb…` y la corrección PWD derivada de ella).
- **Valores del runtime real** (modelo real qué modelo exacto quedó en `session_v2.model`; shape JSON exacto que OpenCode v2.0.x serializa): solo la evidencia de aceptación lo reporta; no re-verifiquables sin la base real → abstención (la observación de R2 es sobre el shape reportado por el propio registro de I8, no sobre el modelo real).

**Sin hallazgos que el permiso de leer pruebas/implementación no cubra; read-only compliance: write_scope `[]` respetado (0 escrituras; solo lectura de repo + corridas de tests que escriben SOLO bajo `tmp/` depytest y `.cdad/` de fixtures de tempdir).**

---

## Índice resumido

| ID | Veredicto | Severidad | Bucket | Resumen |
|----|-----------|-----------|--------|---------|
| R1 | BLOCKING | Requerido | m | TimeoutExpired del destino → `transport-error` con hecho material falso (rc inexistente, «failed in transport»); PD-5 exige `timeout` (sin fila/sin idle/truncado en la cota). R-E legacy-hang e impacto en reconciliación |
| R2 | OPTIONAL | Mejora | m | `model_reported` = objeto JSON verbatim de la fila (evidencia §6) |
| R3 | OPTIONAL | Mejora | m | Ramas `succeeded-sin-texto → blocked` e `idle_outcome desconocido → unknown` sin variante que las fije en el doble |
| R4 | OPTIONAL | Mejora | m | Config sin `wait.timeout_seconds` → timeout=None: invocación DESACOTADA (INV-4 fail-open) |
| R5 | OPTIONAL | Mejora | m | `_last_assistant_text` con `fetchall()` no acotado |
| R6 | OPTIONAL | Nit | l | Docstring del adaptador REFERENCIA postcondiciones de 005-009 sin desambiguación |
| R7 | OPTIONAL | Nit | l | URI SQLite sin encoding de path (`?#`) |
| F1 | FYI | — | — | 2 FAILs de `make validate` preexistentes, fuera del diff (deuda documentada del check A3) |

**Dictamento:** el diff implements fielmente PD-1..PD-10 e INV-1..INV-10 (verificado contrato, producto, tests y referencias), con un caso de clasificación PD-5 (R1) que necesita corrección antes de cerrar la review (es implementación de vocabulario, no de funcionalidad: NO afecta la entrega durable ni el gate). Mejoras y deuda quedan trazadas sin hito. El cierre de PD-9 requiere paso b (post-despliegue del dueño), pendiente por diseño y bien registrado en el state.

---

## Decisión del orquestador (2026-10-11)

- **R1 (bloqueante): se corrige.** Un `TimeoutExpired` del destino es `timeout`, no `transport-error`.
- **R4: se corrige en la misma ronda.** Una espera sin cota viola INV-4: sin `wait.timeout_seconds` positivo, fallo cerrado antes del despacho.
- **R3: se corrige.** Variantes del doble para `succeeded` sin texto y `idle_outcome` desconocido.
- **R2: se corrige.** `model_reported` se normaliza a `proveedor/modelo` cuando la fila lo permite.
- **R5, R6, R7: deuda** (memoria en sesiones largas, numeración del docstring, encoding del URI), sin efecto en el camino feliz.
- **Suite completa:** la corrió el orquestador en el worktree fijado a `3c9d3ee`: 753 passed / 1 failed / 2 skipped. La falla es de preparación del orquestador (staging armado con `basic` para la instalación aislada); con el staging por defecto ese archivo pasa (5 passed). Se repite al cierre.
