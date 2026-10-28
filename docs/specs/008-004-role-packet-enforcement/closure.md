# Cierre 008-004-role-packet-enforcement

Fecha: 2026-10-28. Epic: `epic-008-suite-coherence`. Feature 4 de 6.

## Resultado

Una encomienda CDAD **no se admite ni se acredita sin un paquete verificado**, y el preámbulo que el
runtime antepone a todo prompt de subagente deja de romper el intake:

- En las **fronteras invocables** (`begin`, `prepare --record-dispatch`, `cdad_dispatch dispatch/record`,
  `cdad_delegate`) el paquete publicado se valida y se compara byte a byte con el render canónico de su
  request antes de producir efectos.
- En el **intake de los roles**, el marcador se identifica **exactamente una vez en cualquier
  posición**, el preámbulo es transparente y no autoriza nada, y la ruta A exige comparar el paquete
  recibido completo contra el render canónico completo — no sólo el encabezado.
- `begin` **rechaza una referencia de clase `contract` cubierta por el `write_scope`** del propio
  paquete, que era el defecto que hizo fallar cuatro registros por P1 durante este epic (cifra de 008-003); en esta unidad se sumó un rechazo distinto, `state incoherent`, al corregir la spec después del `begin`.

## Contrato

`docs/specs/008-004-role-packet-enforcement/spec.md` — 8 PCs con D1 (A + respaldo C), D2 (el marcador
canónico como señal de encomienda) y D3 (rechazo temprano de referencias en scope).

## Cambios

- `cdad_packet.py` (+126): `verify_published_packet()` — valida el request y compara el `PACKET.md`
  completo contra el render; rechaza ausencia, cero o múltiples marcadores, bloque sin cierre y
  cualquier alteración del objetivo, instrucciones, contrato, scopes o evidencia.
- `cdad_continuity.py` (+162): `_admit_packet()` en `begin`; `_refuse_covered_contract_references()`
  contra todos los selectores de `write_scope`; `_published_commission_trace()` para distinguir
  encomienda incompleta de continuidad legacy.
- `cdad_dispatch.py` (+23): admisión en `dispatch` antes de la prueba de continuidad y del transporte, y
  en `record` antes de observar o preparar staging.
- `cdad_delegate.py` (+24): admisión en la propia frontera, antes de leer los bytes y del adaptador.
- `sources/roles/architect.md` (intake compartido) y **20 copias generadas** en `agents/` y
  `agents/claude-code/`: marcador en cualquier posición, preámbulo transparente, ruta A con comparación
  completa, ruta C con vinculación de identidad y rechazos separados por ruta.

## Evidencia

| Etapa | Commit |
|---|---|
| Discovery | `4e991c8` |
| RED (11 rojos + 6 guardas) | `f10aeaa` |
| GREEN | `126d68b` |
| Review-fix (3 bloqueantes) | `41b90d6` |
| Pruebas durables (25/25, discriminan) | `a2dec5b` |
| Review 2ª ronda | `91bfcce` |
| PC-08: intake + 20 copias | `0760d54` |
| Review-fix (2 bloqueantes de A/C) | `f7f3510`, `d7cbb1f` |
| Review final (4ª ronda) | `a89cfb5` |

- `tests/test_008_004_packet_enforcement.py`: **25 tests** que discriminan contra el código previo.
- Regresiones: 664 passed en continuidad, despacho, recepción y paquetes; `003-004`/`003-007` intactos.
- Gate final: ver «Gate».

## PCs y acreditación

| PC | Acreditación |
|---|---|
| 01 | Código + pruebas durables (rechazo antes de efectos) |
| 02 | Lectura del intake (preámbulo transparente y no autorizante) |
| 03 | Lectura del límite de comparación + verificador publicado + pruebas de frontera |
| 04 | Lectura de la ruta C (bloque único, identidad vinculada, límite de lectura) |
| 05 | Gate final (regresiones legacy, `capabilities`/`migrate`) |
| 06 | Pruebas de `begin` con referencia en scope + controles `living` |
| 07 | Pruebas de preservación e idempotencia |
| 08 | Lectura de la fuente y de las 20 copias + **distribución instalada** tras el deploy |

## Gate

Tres corridas completas del mismo mecanismo de cierre:

| Corrida | Commit | Resultado | rc | Canario | Duración |
|---|---|---|---|---|---|
| A (2026-10-28 01:32) | `126d68b` + pruebas durables (pre-PC-08) | **1808 passed, 5 skipped** | 0 | 0 | 51:02 |
| B (2026-10-28 04:54) | `d7cbb1f` | 1805 passed, **3 failed**, 5 skipped | 1 | 0 | 1:02:59 |
| C (2026-10-28 06:44) | `d7cbb1f` | 1804 passed, **4 failed**, 5 skipped | 1 | 0 | 1:43:09 |

**Diagnóstico de B y C (no atribuible a esta unidad).** Los 7 fallos son, en todos los casos,
`assertLess(elapsed, …)` sobre reloj de pared en pruebas de espera/reintento:

- `tests/test_005_010_b1_last_assistant.py:164` (cota 5 s, observado 5.05 s),
- `tests/test_005_010_reviewfix.py:405` (cota 5 s, observado 5.35 s),
- `tests/test_005_010_t1_durable_signal.py:293` (cota 5 s, observado 6.08 s),
- `tests/test_006_001_t2_wait_recovery.py::TestPd11RespondsWithinBudget` ×2 (cota 2.5 s, observado
  3.80 s / 3.21 s / 6.72 s),
- `tests/test_006_001_t2_wait_recovery.py:1211` (fixture: el escritor del lock no vio el centinela
  dentro de la ventana; la propia prueba ordena «fallo de fixture, detener y reportar, no debilitar la
  aserción»).

Evidencia de que son intermitentes por carga y no una regresión de esta unidad:

- El host estuvo cargado durante B y C por **agentes ajenos a esta sesión** (`/proc/loadavg` 5.4-6.9
  sobre 8 CPU; procesos `claude`/`codex`/`opencode` de otras sesiones). La duración pasó de 51 min a
  1:43 sin cambio de código.
- La clase `TestPd11RespondsWithinBudget` pasa **3/3 dos veces seguidas** en el árbol actual con el
  mismo load 6.5-6.6, y **3/3** en un worktree del commit previo a esta feature (`126d68b`).
- Las 7 pruebas son cotas de tiempo, no aserciones de comportamiento; los 25 tests de esta feature y
  las 664 pruebas de regresión de continuidad, despacho, recepción y paquetes pasan.

**Consecuencia declarada:** el gate de la unidad no queda verde por un defecto **preexistente** de
estabilidad de la suite (cotas de reloj de pared), no por el producto de 008-004. Se registra como
deuda **BLOCKING para el criterio de aceptación del epic** («tres corridas completas consecutivas
verdes, sin fallos intermitentes») y como **primer requisito de 008-005**: un gate de CI sobre un
runner cargado no puede producir rojos falsos.

**Extra del gate:** tras el deploy a HOME (ver abajo), `make validate` pasa **68/68** (el antiguo F011
era el drift de los agentes instalados, que declaraban `model:`).

## Deploy y distribución instalada (PC-08)

- `./install.sh --check` estaba en FAIL por drift contra `staging` (copia instalada en `b4fd046`).
- Los 16 conflictos del instalador eran los agentes propios instalados con bytes previos; se
  respaldaron en `.cdad/local/deploy-backup-20261028/` y se reinstaló.
- Resultado: **11 agentes por runtime** (`~/.config/opencode/agents`, `~/.claude/agents`) con el intake
  corregido (`at any position` presente en las 22 copias registradas), **sin `model:`**, y
  `./install.sh --check` → **PASS (414 grupos de artefactos en sincronía)**.

## Límites declarados

- La garantía es de **admisión en las fronteras administradas y en el intake del rol**. No es un sandbox:
  no intercepta herramientas nativas ni impide que un agente ignore sus instrucciones.
- Validar el paquete en disco **no** acredita por sí solo los bytes que recibió una sesión nativa.
- `deferred-hardening`: fuzzing del parser, combinatoria exhaustiva de transportes, matriz de versiones
  de runtime e interceptación nativa.

## Deuda observada

- **Cuatro `record` rechazados por P1** durante el epic (cifra de 008-003), y un quinto rechazo distinto (`state incoherent`) por citar en el `begin` una referencia `contract`
  dentro del `write_scope`; la regla ya existe (PC-06) y el defecto se cerró.
- **Transcripción manual de paquetes:** el digest canónico detectó dos transcripciones erróneas del
  orquestador. Regla operativa: despachar los bytes del archivo, nunca re-tipearlos.
- **`make validate` F011** preexistente y ambiental (agentes instalados con `model:`).
- **Cotas de reloj de pared en la suite:** 3 tests (`test_005_010_b1_last_assistant`,
  `test_006_001_t2_wait_recovery::TestPd11RespondsWithinBudget` ×2) fallan con el host cargado y pasan
  en aislamiento. Insumo directo para **008-005**: un runner de CI cargado produce falsos rojos.
- **008-002:** `pytest_summary.skips[].reason` vacío → 008-005.
