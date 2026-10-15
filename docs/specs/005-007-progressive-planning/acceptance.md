# Aceptación de la feature — 005-007-progressive-planning (gate T8)

Fecha: 2026-10-13. Ejecución: `exec-005-007-progressive-planning-001`. Medición y dictamen: **orquestador OpenCode**
bajo la HITL delegada del epic-005 (`docs/epics/epic-005-real-operation/execution.md`), con el criterio de review
vigente del 2026-10-12. Contrato verificado: `spec.md` (`54877103…`, con marca de aprobación) y `plan.md` (`1f636260…`).

El gate de la feature **es** este documento: se declara **BLOQUEO PARCIAL** — todo lo verificable en el repo está
verificado y verde; la medición con la **versión desplegada** es una acción reservada al dueño y queda como
**BLOQUEO declarado**, nunca como verde por proximidad (spec PD-10/PD-11, plan §6).

## 1. AC-1..AC-6 (contrato) — verificados

Oraculos congelados, re-corridos por el orquestador en el árbol al cerrar T7: **37 passed** en 22.51s
(`tests/test_005_007_t1..t7_*.py`). Regresiones del área registradas por unidad en `docs/.cdad-state.json`.

| AC | Unidad | Oráculo | Commit del rol | Resultado (orquestador) |
|---|---|---|---|---|
| AC-1 | T1 | `tests/test_005_007_t1_progressive_detail_rule.py` | `7ff19c1` | 5 passed (RED `16a89ad`: 5 failed) |
| AC-2 | T3 | `tests/test_005_007_t3_open_unit.py` | `54eeed6` | 6 passed (RED `47cd7cc`: 6 failed) + regresión 34 passed |
| AC-3 | T4 | `tests/test_005_007_t4_architect_report_materialization.py` | `512d913` | 7 passed (RED `852d3be`: 1 failed + 6 controles) + regresión 18 passed |
| AC-4 | T5 | `tests/test_005_007_t5_delegation_dispatch.py` | `8ac41d6` | 5 passed (RED `b3044b1`: 4 failed) + regresión 20 passed / 2 skipped |
| AC-5 | T6 | `tests/test_005_007_t6_templates.py` | `594da73` | 4 passed (RED `95516ef`: 4 failed) |
| AC-6 | T7 | `tests/test_005_007_t7_unit_size_and_retries.py` | `a59101d` | 4 passed (RED `4462a9a`: 4 failed) |
| (base) | T2 | `tests/test_005_007_t2_progressive_plan_validator.py` | `09567cd` | 6 passed + regresión 22 passed (RED `07abeb2`; testfix `7d683c9`) |

Cadena RED→GREEN por unidad: cada tarea tuvo su RED por `AssertionError` (commit `test:`), su GREEN por el
implementer (commit `feat:`) y su regresión proporcional. **Tres unidades** requirieron una vuelta extra porque el
gate del orquestador encontró defectos **del oráculo** (no de la implementación), registrados como tales:
T2 (fixture que no omitía el campo), T5 (helper que recibía el documento en vez de la sesión). En ambos casos el
implementer no commiteó un GREEN no validado y el test-writer corrigió el oráculo en sesión aislada; el par
RED/GREEN se verificó en un **worktree fijado al HEAD sin la implementación**.

## 2. AC-7 — meta de aceptación (orientación, no umbral)

**Instrumento y procedencia.** (a) El medidor del repo, en solo lectura:
`python3 skills/cdad-cycle/scripts/cdad_context_meter.py --store ~/.local/share/opencode/opencode.db
--session <sesión real> --delegation-dispatch` (la base de sesiones se abre `mode=ro`; nunca se escribe);
(b) conteo propio sobre las partes `tool` de la sesión. Sesiones medidas: la del orquestador de esta feature
(`<ses-orq-005-007>`, `store_ref sha256:0674cab5…`) y la de un tramo anterior
(`<ses-orq-005-007-previa>`). Los ids reales están en `.cdad/local/session-ids.md`, fuera del repo.

**Apertura (delta 1).** Antes (esta sesión, con la versión instalada que no tiene la mejora): abrir la unidad
exigió **3 escrituras manuales del estado** (2 ediciones + 1 escritura por script) y **1 lectura completa** del
`docs/.cdad-state.json` (397 KB, ~3.200 líneas); referencia de la línea base: 15 comandos sobre el state, el mayor
de ~55 KB (`005-003/acceptance.md` §9). Después (oráculo AC-2, T3): **1 operación del CLI** (`open-unit`) y **0
ediciones manuales**, con el estado coherente (`validate-state` verde) y el rechazo explícito de una segunda
apertura o de una unidad no `queued`.

**Cierre (observación 3 de la revisión Claude).** El cierre **sigue siendo manual**: en esta sesión se usaron
**19 operaciones de estado** (el script de registro del orquestador, una por transición) más un commit por
transición. No hay todavía una operación de CLI de cierre simétrica a `open-unit`: se registra como **deuda**
(condición de cierre: un subcomando que cierre la unidad con el mismo esquema y sin edición manual).

**Detección del despacho por el medidor (PD-9).** En la traza real de esta sesión el medidor reporta
`first_dispatch: absent` con causa declarada. El orquestador verificó el hecho material: la invocación real de la
interfaz **existió** (ledger `dispatches/delegate-opencode-2ac2addcb404.json`) pero iba envuelta en un prefijo
(`time python3 …/cdad_delegate.py …`), y el detector resuelve el **programa** del segmento (`time`), no el
argumento. **Falso negativo declarado**, clase: invocaciones envueltas por prefijos (`time`, `env`, `nohup`,
`nice`, `sudo`, `bash -c`). No lo cubre el oráculo congelado (que sí pasa en sus 5 casos). **Condición de cierre:**
extender el detector a los prefijos de envoltura si una traza real lo exige — lo hace exigible **esta** traza
(la práctica del repo envuelve despachos con `nohup bash -c`). Queda a juicio del reviewer si bloquea el uso
previsto; el resultado principal de la feature no depende de esa detección.

## 3. AC-8 — suite completa una sola vez, en worktree fijado

Corrida **una** vez por el orquestador en un worktree fijado al commit `a5cd0c8` (el commit de cierre de la etapa 3):

```
env -u TMPDIR python3 -m pytest tests -q
4 failed, 871 passed, 9 skipped, 6 errors in 906.18s (0:15:06)
```

Los 4 fallos y los 6 errores son **IDÉNTICOS** a los que produce el mismo conjunto de pruebas en el commit **base**
`99e2f2e` (antes de cualquier código de esta feature), verificado por el orquestador en un worktree separado:
`tests/test_opencode_read_map_and_steps.py::TestP4InstallPreservesSteps`,
`tests/test_role_packet_review_regressions.py` (3 casos) y `tests/test_004_001_t7_capacity.py` (6 casos, dependientes
de bytes instalados/HOME). Son pre-existentes (familia F011/instalados), **no regresiones de 005-007**.

## 4. Fuera de lo verificado aquí (BLOQUEO declarado)

- **Medición like-for-like con la versión desplegada en una sesión nueva** (PD-11/AC-7): requiere **desplegar**
  (acción reservada al dueño). **BLOQUEO declarado**; responsable: el dueño. Mientras no se despliegue, la
  medición de esta feature usa el **artefacto del repo en solo lectura**.
- **Confirmación del consumidor** (usar la mejora en el arranque de la próxima unidad, 005-004): depende del
  despliegue previo.

## 5. Desconocidos conservados (con causa)

- `cache.write`, costo facturado y atención humana: no observables con el instrumento actual (005-002).
- `first_dispatch` de la traza real: falso negativo declarado (§2) con su condición de cierre.
- La comparación de llamadas/salida previas al primer despacho **con la versión desplegada** queda pendiente del
  despliegue (§4).

## 6. Datos del proceso (para la review y el cierre)

- Tres defectos de oráculo detectados por el gate del orquestador (T2 fixture, T5 helper; y un tercer caso menor:
  la bandera `--delegation-dispatch` que el oráculo fija y la spec no nombra literalmente).
- El implementer no commiteó un GREEN no validado en los dos casos en que el gate falló (criterio correcto,
  declarado en su informe), y el orquestador lo resolvió con testfix + fix-loop.
- Los despachos se registran en el ledger I8 por `prepare --record-dispatch` (o por la interfaz común, en el
  tramo de discovery/draft).

**Dictamen del orquestador:** la feature **no cierra** hasta que la review formal (stage 4) se pronuncie y el
Memory Bank se apruebe; este documento es el gate de la unidad de aceptación (T8) con la parte desplegada en
**BLOQUEO declarado**.

## 7. Medición de uso con la versión desplegada (D-1, 2026-10-13, orquestador Claude)

Sesión nueva del orquestador OpenCode con la instalación `9d89a4b`, en este repo y en reposo, con
el mismo prompt mínimo que `005-003/acceptance.md` §9. El id está en
`.cdad/local/accept-005-007.session`. Se leyó en solo lectura.

**Recorrido:** consultó `status`, que apuntaba a `open-unit`, y abrió 005-004 con `open-unit` sin
editar el state a mano (declaró que la entrada no tiene `depends_on`). Después hizo `prepare`, las
validaciones, `begin` y `--record-dispatch`, y despachó al architect por subagente. Recibió la
entrega con `receive` y `materialize`, sin `cp`, y la registró en el commit `1f0b0fe`.

| Medida hasta el primer despacho | 005-003 §9 (`0650655`) | Esta sesión (`9d89a4b`) |
|---|---:|---:|
| Llamadas previas | 74 | 70 |
| Salida previa | 399.082 car. | 304.054 car. (−24 %) |
| Comandos sobre `docs/.cdad-state.json` | 15 | 7 |
| Ediciones manuales del state para abrir | sí | 0 (`open-unit`) |
| Tiempo hasta el despacho | 5,02 min | 5,82 min (medidor) / 6,02 min (conteo propio) |
| Despacho detectado por el medidor | no | sí (`observed`, llamada 71) |

**Lectura:**
- **Se cumple:** una sola operación del CLI para abrir la unidad, sin edición manual; el medidor
  detecta el despacho por sí solo; el informe se materializa por el camino legítimo.
- **Mejora parcial:** la salida y los comandos sobre el state bajan, pero las llamadas casi no.
- **No mejora:** el tiempo es similar.
- ~~**Causa visible:** lectura del state y registro manual posterior a la recepción.~~ Atribución
  corregida el mismo día (abajo): el registro manual ocurre después del despacho y no explica el
  gasto previo.
- **Causa del gasto previo (conteo por llamada, 2026-10-13):** la entrada al proceso.
  - Llamadas 1–2: las dos skills (≈54 mil car.).
  - Llamada 3: el state completo (59 mil car., truncado), antes de cualquier operación del CLI.
  - Llamadas 4–19: exploración manual del state, el plan, la ejecución y los paquetes.
  - Llamada 20: `status --project-root .` rechazado. `cdad_packet.py` exige una ruta absoluta y
    `cdad_continuity.py` no.
  - Llamada 21: `status` válido. Señalaba `open-unit`, pero también informaba `unknowns: version
    DRIFT` (proyecto en `0650655`, instalación en `9d89a4b`) sin una acción concreta.
  - Llamadas 22–30: el orquestador investigó versiones, manifiestos y el código del comprobador de
    versión, guiado por ese DRIFT.
  - Lo empuja el texto de las skills: `cdad-epic` Step 1 y `cdad-cycle` Step 1 mandan leer
    `state-detection.md`, que lee campos del archivo. La ruta compacta existe, pero compite con las
    anteriores.
- **Siguiente palanca:** una entrada común breve que todas las skills usen primero (`status`), que
  acepte una raíz relativa y que, ante un DRIFT, dé una acción concreta. Solo después de eso conviene
  automatizar el registro de transiciones; esa automatización ayuda durante el ciclo, pero no reduce
  el arranque.
