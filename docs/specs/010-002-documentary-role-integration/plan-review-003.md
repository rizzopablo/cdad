# Dictamen de plan-review (tercera pasada): 010-002-documentary-role-integration

**Recomendación: no aprobar todavía la versión 3.** N1..N4 están cerrados, pero el cambio de v3 deja un bloqueante nuevo (B1). `prepare --replace-packet` es una vía pública de publicación que copia el agente del predecesor, y eso contradice la garantía por construcción y PC-06. La corrección es acotada: una decisión del dueño y unas líneas en spec y plan. Cerrado B1, la v3 sería aprobable sin otra ronda amplia. Este dictamen no aprueba nada ni autoriza implementar.

**Objeto revisado**
- `plan.md` v3: `4025d22f7988f735f8a780fdd85e3f698e7974349095128a1631bd2a3fbbad2c`
- `spec.md` v3: `1a94dbc04477d82e02b5bfa4843167e4c7cdf339697ac5ed46f398b88809d80d`

**Intake:** ruta C válida.
- Los metadatos de la identificación coinciden con `REQUEST.json` y `PACKET.md`, y los dos hashes coinciden con el contrato.
- El contexto de ejecución es v2.
- `validate-request` y `validate-packet` dieron rc=0, y `render` es idéntico a `PACKET.md`.

## Hallazgos bloqueantes

### B1. El reemplazo de paquete publica un request nuevo con el agente copiado, sin derivarlo
- **Severidad:** Required
- **Verdict:** BLOCKING
- **Bucket:** h
- **Ubicación:** `spec.md:117,232,234,298`; `plan.md:45,217,265`; `skills/cdad-cycle/scripts/cdad_packet.py:3611,3800-3801,3807,3827,9782,10306`.
- **Fundamento:**
  - `_replace_packet` se alcanza con `prepare --replace-packet`, y el propio código llama al sucesor «a NEW publication».
  - Copia `agent` del predecesor si existe (`:3800-3801`) y escribe siempre `execution_context` (`:3807`).
  - Spec y plan afirman que `prepare` deriva el agente por construcción y no aceptan otro. Eso solo es cierto para la vía ordinaria (`:6666`).
  - Ni el spec, ni T5, ni T6, ni EV-03 mencionan esta vía.
- **Consecuencia, en dos casos:**
  - **Predecesor sin `agent`:** el sucesor lleva contexto y no agente. Con la regla nueva de D3, un reemplazo que hoy funciona pasa a fallar. El censo da 592 requests sin agente de un total de 868. Ningún test comprometido protege este caso, y el rechazo no tiene diagnóstico propio.
  - **`stack` cambiado:** el sucesor conserva el agente anterior. Según cómo se implemente, o se publica un destinatario discordante que incumple PC-06 y solo se corta en `record-dispatch`, o falla sin regla contractual.
  - En ambos casos falla cerrado y no llega trabajo a un rol equivocado. El defecto es que el contrato afirma una garantía falsa y deja sin definir una transición pública. Además, el test-writer no lee la implementación, así que T2 no puede detectarlo por sí solo.
- **Condición de cierre:** el dueño decide una de estas dos opciones, y spec y plan la declaran.
  - **Rederivar (recomendada):** el sucesor toma el agente del rol y `stack` vigente, igual que una preparación nueva. Cubre los dos casos y mantiene PC-06 sin excepciones.
  - **Rechazar:** el reemplazo falla cerrado con diagnóstico propio cuando no hay agente coherente que conservar, y la salida es una preparación nueva.
  - En ambos casos hay que limitar la garantía por construcción a lo que quede cierto, y añadir la transición a D3, PC-06/07, EV-03, T5, T6 y `plan-tasks`. `tests/test_007_002_dispatch_recovery.py` usa `--replace-packet`; si el contrato cambia sus oráculos, debe entrar en T5, y como mínimo en las regresiones de T6.

## Hallazgos no bloqueantes

### N5. Los tests adaptados en T5 no se ejecutan en su gate
- **Severidad:** Consider
- **Verdict:** OPTIONAL
- **Bucket:** h
- **Ubicación:** `plan.md:210-213,250,518-520,536`.
- **Fundamento:** T5 edita `u1c`, `u1b` y `u2`, pero su comando solo corre el módulo nuevo y `regressions` está vacío.
- **Consecuencia:** un error de fixture se descubre en T6, donde el implementer no puede corregir tests, y obliga a volver al test-writer. El proceso no se rompe.
- **Condición de cierre:** añadir esos tres archivos a la verificación de T5, registrando el RED esperado de cada uno.

### N6. No se declara qué pasa con un intento nuevo sobre un request sin `agent`
- **Severidad:** Consider
- **Verdict:** OPTIONAL
- **Bucket:** m
- **Ubicación:** `spec.md:132,236`; `plan.md:220`.
- **Fundamento:** PC-07 trata el agente discordante, y D3 admite históricos sin ambos campos. No dice si un histórico sin agente puede registrar un intento nuevo.
- **Consecuencia:** el `drop_optional_agent` de `u1b` queda con contexto y sin agente, así que al adaptarlo hay que decidir el caso. Sin declaración, la decisión queda implícita en T6.
- **Condición de cierre:** una línea en D3 y un caso en T5. La lectura compatible es admitirlo sin contraste contextual y sin fallback.

### FYI
- D-3 pide que el mensaje nombre rol, stack y agente esperado. El diagnóstico estático nombra rol, agente recibido y familia, y declara que no evalúa stack. La diferencia está justificada en `spec.md:104-106`, pero `discovery-decisions-2026-10-31.md` no registra esa precisión.
- `spec.md:13` y el epic (`plan.md:77-78` del epic) siguen trazados: la combinación documental/Odoo se acredita en PC-12.

## Verificación N1..N4

| # | Resultado | Evidencia |
|---|---|---|
| **N1** | Cerrado | `u1b` y `u2` figuran en T5 en prosa (`plan.md:203-204`) y en `plan-tasks` (`:515-516`). `u1b` figura en las regresiones de T6 en prosa (`:284`), en la tabla (`:385`) y en `plan-tasks` (`:564`). Las listas no sustituyen la medición de T2 (`:96,206,290,389,429,532,559`; `spec.md:312`). |
| **N2** | Cerrado | D3 (`spec.md:119-121`) y PC-08 (`:243-245`) declaran la excepción sin relajar identidad, idempotencia ni transacciones. T5 la compromete por efectos durables (`plan.md:226-229,234`, `:528-530`). Es implementable: `_record_dispatch` ya separa `identical_replay` y `completion` antes de publicar, y `_completion_rejection` conserva el rechazo de datos distintos. Un `attempt_id` nuevo no tiene registro previo, así que no entra en la excepción. |
| **N3** | Cerrado | La regla está en `spec.md:95-104` y en PC-07 (`:235`). El contraste contextual queda limitado a publicación e intento nuevo (`:110-115`). `plan.md:263` lo lleva a la validación compartida; `validate_request` cubre `render`, `verify_published_packet` y recepción. El censo da 276 requests con agente, todos del rol correcto, y 0 discordantes, de modo que no invalida históricos reales. |
| **N4** | Cerrado en el texto | PC-07 (`spec.md:233-236`) y EV-03 (`:298`) separan las tres vías y clasifican `prepare` como garantía por construcción; T2 y T8 lo recogen (`plan.md:70-71,340`). La afirmación es exacta para la vía ordinaria, pero no para `--replace-packet`: ver B1. |

## Otras verificaciones

| Punto | Resultado | Evidencia |
|---|---|---|
| Contradicciones entre spec, plan, decisiones y epic | Una, B1 | D-1, D-2, D-4 y D-5 se respetan. D-3 queda precisada según lo descrito en el FYI. |
| Alcance | Sin ampliación | Sin agentes, campos, etapas, selectores ni permisos nuevos (`spec.md:318-319`; `plan.md:272`). |
| Esquema (PC-10) | Viable | Con ambas propiedades y `dependentRequired` aplicados en memoria sobre el asset, los 868 requests reales validan con jsonschema 4.19.2. Hay 47 con contexto y agente, y 0 con contexto sin agente. |
| Rutas de T6 | Correctas | `scripts/cdad_packet.py` es un wrapper de 330 bytes; la lógica vive en la ruta de T6. |
| `plan-tasks` | Válido | JSON correcto con 9 tareas; `_check_plan_tasks` no objetó nada, dentro del alcance de esa función. |

## Abstentions
- **Medición completa de fixtures:** no la hice, corresponde a T2. Con búsqueda directa, `pop("agent")` solo aparece en los tres archivos de T5.
- **Fixtures con `"stack": "generic"`:** aparecen en `test_003_006_t2_activation.py:112` y `test_005_005_t3_provenance.py:184`. No determiné si llegan al contraste contextual.
- **Comportamiento de B1:** lo establecí por lectura de código, sin ejecutar un reemplazo tras cambiar `stack`.
- **`test_007_002_dispatch_recovery.py`:** no determiné cuántos oráculos dependen de la copia del agente.
- **Suficiencia real de la matriz Odoo:** depende de la redacción de T4 y se juzga en T8.

## Evidencia
- **Archivos modificados:** ninguno.
- **Commit:** ninguno. `HEAD` es `3bea7a8d356e35ccb93d22d010632f1d7e7406bf`.
- **Comandos:**
  - `python3 -B scripts/cdad_packet.py validate-request --request <REQUEST.json>`
  - `python3 -B scripts/cdad_packet.py validate-packet --request <REQUEST.json> --packet <PACKET.md>`
  - `python3 scripts/cdad_packet.py render --request <REQUEST.json> | cmp - <PACKET.md>`
  - `sha256sum` de `plan.md` y `spec.md`
  - `python3 -I` en memoria para el censo y para el esquema, y `_check_plan_tasks` sobre el bloque
  - `grep`, `git grep` y `sed` sobre las rutas citadas
- **Salidas:**
  - `vr=0`, `vp=0`, render `IDENTICAL`.
  - Censo por rol del agente: `Counter({'none': 592, True: 276})`.
  - Esquema: `Counter({False: 868, 'ctx_agent': 47, 'ctx_noagent': 0})`; `False` indica requests sin errores.
  - `_check_plan_tasks`: `None`, rc=0.
- **Suite completa:** no ejecutada; este paquete no la pide.
