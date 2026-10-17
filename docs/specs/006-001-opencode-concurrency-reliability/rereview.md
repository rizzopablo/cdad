Comienzo con la RE-REVIEW acotada. Primero localizo los artefactos déclarados: la review formal (hallazgos y condiciones de cierre), la spec v2, el diff y los informes de rol.
Continúo la RE-REVIEW. Leo la review formal (hallazgos y condiciones de cierre) y la spec v2:
Tengo los hallazgos y sus condiciones de cierre. Ahora obtengo el diff declarado y los informes de rol del review-fix:
El diff es acotado (3 archivos). Verifico qué tocó cada commit y leo los informes de rol:
Ahora examino el diff GREEN del adaptador en detalle:
La fórmula coincide con la condición de cierre propuesta por la review. Ahora verifico la aritmética real contra el código (cómo se fijan `wait_deadline`, la cota de la interfaz, `grace` y `budget`):
La implementación de B1 coincide textualmente con la fórmula de cierre propuesta (`E + bound + g + ε ≤ T` acotado por el slack de la reserva). Verifico aritméticamente la banda crítica y reviso el archivo de tests RED:
Los tests son de contrato observable (origen del envelope, sesión, diagnóstico, sin `run`). Ahora verifico el orden de los guardas en `delegate()` (bloqueo antes de cualquier invocación del binario) y contexto completo:
El guarda B2 está ubicado correctamente (después del bloqueo por fila `no-idle`, antes de preflight). Reviso ahora que la rama que B3a pina sea la de `!standalone` (lerle: cierre B3a real) y corro el foca para evidencia directa:
La aserción de B3a pincha efectivamente la cláusula `== "standalone"` de `_settle_decides`. Corro ahora el foca completo para evidencia directa:
Foca verde (4 passed). verifico además que el oráculo aprobado de 005-009 (que despacha dos veces con store aún no creado — la razón del distinction `no existe` en B2) siga verde:
Oráculos aprobados intactos. Última barrida de invariantes sobre el diff exacto (argv prohibidos, secretos, paths sensibles):
Un punto fino: ¿el B3b ejercita realmente el tope «por presupuesto restante» del preflight de servicio, o solo el configurado? Leo la región de preflight y el test PD-11 de servidor para comparar:
B3b replica la estructura del focal de servidor aceptado por la review (:1337). Me falta verificar la coherencia de O1 en la documentación de referencia (`cli-delegation.md`) — la tabla de claves no debe seguir prometiendo `logs_dir`:
Chequeo dónde alimenta `prior_check_reads_value` (por el `reads += 1` que ahora ocurre antes del descarte de store inexistente):
La mecánica de `reads` quedó sin distorsión (cuenta registros con sesión, no lecturas de store — semántica intacta). Cierro con la verificación de árbol limpio y armo el informe final:
# Informe del reviewer — RE-REVIEW 006-001-opencode-concurrency-reliability (etapa 4, cierre de hallazgos)

**Contrato:** spec v2 aprobada (`docs/specs/006-001-opencode-concurrency-reliability/spec.md`, sha256 `dac418b9…`). **Objeto:** el diff acotado de la review-fix, `6fae723..HEAD -- skills/ tests/` (RED `17a7ca1` solo en `tests/test_006_001_reviewfix.py`; GREEN `161c9ff` en `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` + `skills/cdad-cycle/assets/opencode-exec-config.example.json`). Sesión independiente; el informe del implementer no se usó como prueba: mecanismos y aserciones verificados contra el código y corridas propias.

---

## Evidencia (obligatoria del packet)

| Comando | Salida |
|---|---|
| `git diff --stat 6fae723..HEAD -- skills/ tests/` | 3 files, +886/−14: asset (−1 `"logs_dir"`), adaptador (+92 −14), `tests/test_006_001_reviewfix.py` (+807) |
| `git show --stat 17a7ca1` / `161c9ff` | RED tocó **solo tests/**; GREEN tocó **solo los 2 archivos de producto** (tests/ intacto ✓) |
| `git rev-parse HEAD` | `524a5d66…` (estado doc; último commit de producto es `161c9ff`) |
| `timeout 280 python3 -m pytest tests/test_006_001_reviewfix.py -q` | `4 passed in 16.50s` |
| `timeout 280 python3 -m pytest tests/test_005_009_t2_opencode_adapter.py tests/test_006_001_t2_wait_recovery.py -q` | `20 passed in 45.35s` (oráculos aprobados que consumen `_prior_attempt_check`, intactos) |
| `grep -rn logs_dir skills/` | sin coincidencias (el docstring FALSO quedó sin resto) |
| `git status --short` | vacío (sin modificaciones del reviewer) |

Barrida de invariante sobre el diff: ningún `serve`, `service start|stop|restart|get|set|unset` ni `reload` añadido al producto (los `service status`/`token` del grep son del *fake* de fixture del test — protocolo legítimo del binario falso); ningún cambio en construcción de argv, fallback `service → standalone`, ni re-despacho; D-11 intacto (el lector del registro no se tocó; el diagnóstico nuevo de B2 transporta solo el id de sesión previa, ya público en el diagnose de bloqueo existente — ninguna url/contraseña).

**Suite completa:** no corrida — policy del packet (la corre quien cierra). Suite de la review-fix declarada verde en rf-green.md:61-66.

---

## Tabla de cierre por hallazgo

| Hallazgo | Condición de cierre (review) | Veredicto | Provenance |
|---|---|---|---|
| **B1** piso `CLIENT_MIN_BUDGET_SHARE` rompe PD-11 en cota media | Acotar el piso: `E + bound_cliente + g + ε ≤ T` siempre; fórmula sugerida `max(remaining, min(0.75·budget, remaining + max(0, RESERVA − g − margen)))`; focal cota ~10 s, preflight > 25 % del budget, cliente colgado → envelope del ADAPTADOR | **CERRADO** | Fórmula implementada tal como la propuso la review: `<repo>/skills/cdad-cycle/scripts/cdad_delegate_opencode.py:1959-1962` con `COMPLETION_MARGIN_SECONDS = 0.8` (`:201`); aritmética verificada: con gracia ≥ 0,2 el tope da 0 extra (PD-11 manda, declarado en rf-green.md:40); con gracia chica, el piso solo gasta el slack de la reserva → el adaptador SIEMPRE responde dentro de su cota (con el margen cubriendo ε de post-despacho); el camino feliz no pierde presupuesto (`max` con `remaining` ⇒ el cliente nunca recibe menos que `remaining`). Focal: `tests/test_006_001_reviewfix.py:477-560` (cota 10 s, `/api/info` retardado 4 s > 25 % de B=8,8, cliente `hangs`; aserta origen del envelope + sesión elegida + `did not answer within` ausente en diagnosis **y** stdout). RED demostrado en rf-red.md:36 (fallaba por el envelope de la interfaz, `session: None`). Verde en mi corrida |
| **B2** prior-check falla ABIERTO ante store busy/ilegible → segundo worker vivo | Un registro previo con sesión cuya fila NO puede afirmarse → `blocked_before_dispatch` con diagnóstico «no se puede afirmar … intento previo», sin invocar `run`; focal con escritor persistente | **CERRADO** (con nuance declarada, ver Abstentions 1 y Nota de cierre) | `<repo>/skills/cdad-cycle/scripts/cdad_delegate_opencode.py:778-791`: store **existente** ilegible/ocupado (`_StoreBusy`/`AdapterError`) → `unaffirmable_session`; el llamador bloquea `:1876-1890` — ubicado DESPUÉS del bloqueo por fila no-idle y ANTES de cualquier preflight ⇒ cero invocaciones del binario en ese camino. El docstring «fail open» fue reemplazado por el fail-closed espejo de §2.3b (`:736-748`). Focal `tests/test_006_001_reviewfix.py:566-674`: registro previo del mismo paquete con fila previa **IDLE** (anti-vacuo: legible ⇒ seguiría despachando, PD-9 control), escritor `BEGIN EXCLUSIVE` persistente, precondición probe verificada (`:628-642`), aserta `blocked` + sin `run` + `session` null + diagnóstico «no se puede afirmar»/«intento previo». RED demostrado en rf-red.md:37 (`'completed' != 'blocked'`) |
| **B3a** sin focal «fila no idle en modo servicio → timeout» | Focal T2: modo `service`, fila no idle, settle chico → `timeout` al vencer la cota, settle ignorado, sin recibo → FIN TERMINACIÓN | **CERRADO** (cobertura; pasaba en RED, declarado — sin ocultamiento) | `tests/test_006_001_reviewfix.py:693-748`: servicio vivo (scenario_running + registro versión compatible `:705`), variante `exit-row-not-idle`, settle 0,3 s / cota 2 s → aserta `timeout` (no `unknown`), `elapsed > 3×settle` (el asentamiento no decidió) y `elapsed < 3,5` (acotado), PD-8 sesión, sin `--server`/`--standalone` (`:737-746`, §2.3b/INV-10), `service status` exactamente UNA vez, sin recibo. Pincha de verdad el refactor temido: `_settle_decides` devuelve `mode_effective == "standalone"` (`cdad_delegate_opencode.py:662`; un `== "server"` lo dejaría en rojo). Verde en mi corrida |
| **B3b** sin focal «preflight de servicio acotado por presupuesto restante» | Focal PD-11 de preflight de servicio dentro del presupuesto | **CERRADO** (cobertura), con observación opcional nueva O5-RF ↓ | `tests/test_006_001_reviewfix.py:750-803`: `service status` retardado 1,2 s (`:760-762`), `completed` dentro de la cota 10 s, precondición de retardo verificada `:785-790`, `service status` exactamente una vez `:802`, `assert_receipt_no_gate`. El clamped `min(configured, remaining)` existe para servicio en `cdad_delegate_opencode.py:1922-1924` |
| **O1** `logs_dir` muerto en el asset, docstring falso | Quitar `logs_dir` del asset (o consumirlo) y corregir el docstring | **CERRADO** | Diff: `skills/cdad-cycle/assets/opencode-exec-config.example.json` pierde la línea `"logs_dir": "<log>"`; `grep -rn logs_dir skills/` → 0 coincidencias (docstring corregido en `<repo>/skills/cdad-cycle/scripts/cdad_delegate_opencode.py:15`). La clave que queda en la config del *fixture* del foca (`test_006_001_reviewfix.py:422`) es extra en un config de prueba, no el asset publicado — PD-12 sin violación |

---

## Hallazgos NUEVOS introducidos por el fix

**O5-RF — El oráculo nuevo B3b no discrimina el tope «por presupuesto restante» del preflight de servicio frente al tope configurado.**
- *Severidad:* Optional-Consider · *Verdict: OPTIONAL* · *Bucket: l*
- *Provenance:* `tests/test_006_001_reviewfix.py:765-772` (cota 10, `preflight_timeout_seconds: 2`, retardo 1,2 s): configured (2 s) < remaining (≈8,8 s), así que `min(preflight_timeout_configured, remaining)` queda determinado por el valor **configurado**; el refactor que eliminará el clamped por `remaining` en la rama de servicio (`cdad_delegate_opencode.py:1922-1924`) dejaría B3b en verde. Es espeja del echo que la propia review récord como el focal de servidor aceptado (`t2` `:1337`, que tampoco ejercita el clamped activando su ramificación), de modo que la fidelidad del oráculo ya está en línea con el estándar de la review — por eso no es un Hallazgo bloqueante.
- *CONDICIÓN DE CIERRE VERIFICABLE:* una variante (o focal futuro) con configured ≥ remaining — p. ej. cota 3 / configured 20 / retardo > remaining — que aserte el resultado del acotamiento por `remaining`; o registrarlo como deuda de sharpness cobertura de la banda del clamped en servicio.

Sin más hallazgos nuevos: ni B1/B2 introducen regresión — los oráculos aprobados que consumían el `except (_StoreBusy, AdapterError): continue` original siguen verdes (mi corrida de tests/test_005_009… + t2_wait_recovery: `20 passed`), y el `reads` de `_prior_attempt_check` mantiene su semántica original (cuenta registros previos inspeccionados, no lecturas de store: `<repo>/skills/cdad-cycle/scripts/cdad_delegate_opencode.py:777`), así que nada fabricante-of-diagnóstico nueva entró por ese lado.

---

## Abstentions

1. **Necesidad de la nuance store-inexistente de B2 (contradifusión de rf-green.md:13,42):** verifiqué **positivamente** que los oráculos aprobados de 005-009 y T2 pasan con la encrucijada existente; el «contradifusión» (que romperían SIN la encrucijada) proviene del informe GREEN — no puedo verificarlo negativamente desde la etapa read-only. La encrucijada en sí es coherente con §2.7 («fila ausente no bloquea»: un store SQLite no creado no puede sostener escritor) y está declarada en el cade del docstring (`:779-783`); no la reviso en el sentido negativo. Corredor residual: la ventana TOCTOU `is_file()` → `_store_state()` cae por construcción hacia direcciones seguras (o lectura → fila ausente ⇒ no bloquea, o busy → `unaffirmable` ⇒ bloquea).
2. **Corrida del foca bajo carga real DT-9:** mi corrida estuvo sin la carga declarada del host (~9); el fragilidad de ragged buffers de cota de 2 s del fixtures és deuda ya declarada del packet/epic (DT-9) — repetí el foca + oráculos en estado de host moderadamente descargado.
3. **Mediciones instrumentadas del GREEN** (respuesta del adaptador a ≈9,33–9,39 s de cota 10 — rf-green.md:40): mi evidencia de margen propio es la corrida limpia (`4 passed in 16.50s`); la instrumentación fue temporal y removida antes del commit — mencionado como tal, no verifico residuos de esa instrumentación en el código (barrida del diff: no hay artefactos de debug en archivos alterados).
4. **Suite completa:** no corri el conjunto completo el conjuto completo (policy del packet: la corre quien cierra).

---

## Resumen

**5 hallazgos cerrados (B1, B2, B3a, B3b, O1), 0 bloqueantes, 1 opcional nuevo, 4 abstenciones.**

- **B1 CERRADO** — el piso queda acotado por la reserva menos gracia menos margen de completación (formula declarada literales); el vínculo de happy path no pierde presupuesto; el foca de cota media con preflight lento y cliente colgado es RED→GREEN verificado por mí.
- **B2 CERRADO** — intención anterior innegociable: store existente no afirmable → `blocked` antes del despacho, sin invocar binario, diagnóstico §2.3b; encrucijada declarada store-inexistente con oráculos aprobados intactos y verificados.
- **B3a/B3b CERRADOS** — cobertura de las cláusulas de la enmienda en modo servicio (petering del `!standalone` / preflight de servicio acotado), declarados desde RED, sin ocultar.
- **O1 CERRADO** — `logs_dir` fuera del asset y del docstring, grep sin rezagos.
- Invariante central intacto y secretos D-11 sin regresión; GREEN no tocó `tests/` (verificado por `git show --stat`).

**Read-only:** no aprobé ni edité; `git status --short` vacío. La suite completa queda para quien cierre, conforme a la policy del packet.
