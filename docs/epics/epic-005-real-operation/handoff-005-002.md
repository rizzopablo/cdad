# Handoff — 005-009 cerrada; continuación con 005-002-session-context-meter

Fecha: 2026-10-11. **Snapshot del cierre de 005-009, no estado vivo.**
Estado del epic en ese cierre: `epic-005-real-operation`, `epic_stage: features-loop`,
`active_feature: null`, `current_stage: idle` (reposo legítimo, `validate-state` VALID).

## 0. Actualización de entrada — 2026-10-11

El plan vigente intercala **005-010-real-opencode-delegation** antes de 005-002.
Al registrar esta actualización, 005-010 está en construcción. Consultar el
state y su cierre antes de actuar; no usar el snapshot anterior para abrir otra
ejecución. Sus hallazgos sobre carga y señal durable sustituyen las premisas
pendientes de la fotografía de 005-009, sin reescribir ese informe histórico.

Cuando corresponda retomar 005-002, conservar su discovery y añadir al paquete
del architect el [delta de entrada al draft](../../specs/005-002-session-context-meter/draft-inputs-2026-10-11.md).
No repetir el relevamiento ni cargar toda la conversación. La dirección del
dueño y los límites de investigación están en
[el registro estratégico](../../../findings/agent-operation-strategy-2026-10-11.md)
y en la sección «Ajuste de los ciclos pendientes» del [plan](plan.md).

Más adelante, 005-003 consume su `discovery-inputs.md` y 005-007 consume el
[encargo de planificación y aceptación de uso](../../specs/005-007-progressive-planning/discovery-inputs.md).
La ejecución autónoma general queda después de planificación y paralelismo/recursos;
no se habilita auto-continuación sin validación y presupuesto por esta actualización.

## 1. Qué se cerró en esta sesión

**005-008-project-path-capabilities** (cuarta feature) y **005-009-cli-delegation** (quinta),
ambas aprobadas y conducidas bajo la delegación HITL de epic-005 (`execution.md`).

- **005-008:** `skills/cdad-cycle/scripts/cdad_packet.py` (+19/−2): el `read` del test-writer
  reabre el árbol de tests anidado antes de `private`; `_test_patterns` incluye `test_files`; el
  diagnóstico del esquema de política nombra el campo ofensor. ADR-022. Suite de cierre
  **701 passed / 0 failed**.
- **005-009:** interfaz común de delegación con **un adaptador por destino** (OpenCode) que
  **reutiliza** `prepare`/I8/ledger/`receive`/`reconcile` sin crear otro state; verificación del
  modo de carga **fail-closed** sin fallback genérico; espera sobre **señal durable**; vocabulario
  de terminación con **entrega ≠ gate**; reconciliación del SPAWN GUARD. ADR-023. Suite de cierre
  **734 passed / 1 skipped** (el skip es PD-10, declarado).

**Despliegue:** sucesora `6f4d5db` (incluye ambas), perfil `basic`, tres bases, respaldo previo,
0 conflictos, 11/11 agentes, `cdad-version-check.py` **COHERENT**. Ejecutado por instrucción
directa del dueño.

## 2. Qué queda abierto (del dueño)

1. **PD-10 / recorrido real:** una sesión de **Claude coordinador** despachando a un **worker
   OpenCode** real sobre la instalación elegida, con su re-entry registrado. Aporta la **R2
   pendiente de 005-006** y la aceptación de interoperabilidad del plan.
2. **VERIFY-3:** confirmar la entry soportada (`mode: all`) contra la versión de OpenCode vigente.
3. **Aceptación conjunta (plan §5):** una sesión nueva inicia el consumidor Perl/Webmin con una
   instrucción breve y realiza la primera delegación útil.

**Deuda priorizada** (opcionales de la review de 005-009): cota de espera ausente → invocación sin
cota si falta `wait.timeout_seconds`; falso positivo del barrido A3 en la prosa de un fixture;
presupuesto nulo si la cota ≤ reserva; «no polling loop» frente al sondeo acotado; `--packet-id` sin
validar en el adaptador. Más: `install.sh --check` sensible a `__pycache__`; A3 preexistente.

## 3. Continuación: 005-002-session-context-meter

**Pausada desde el 2026-10-10 con su discovery COMPLETO e intacto** (no repetirlo, no modificar sus
contratos). Su próxima unidad es la **subetapa `draft`** (spec + plan) por el architect.

Insumos disponibles: `docs/specs/005-002-session-context-meter/discovery.md` (esquema de
`opencode.db` mapeado, tipos de mensaje, formas de las partes `tool`, y las tres magnitudes pedidas;
línea base del plan reproducida sobre la primera sesión de 005-001: ~12,55 min, 101 llamadas,
51.243 caracteres de salida máxima, ~203.276 tokens de entrada del último paso con caché; 12 VERIFY
abiertos) y la fila de 005-002 del plan del epic, con el delta de §0.

**Nota de dependencia:** el plan declaraba que 005-002 depende de la adopción de la versión de
005-005; esa versión (y las sucesoras) ya están desplegadas, así que la dependencia está satisfecha.
El plan §5 recuerda que su medición **no se presupone**: se mide.

**Orden vigente tras la actualización de §0:** completar 005-010; después 005-002,
luego `005-003-orientation-reduction`, `005-007-progressive-planning`
y `005-004-claude-code-roles`, según el plan vigente y sus dependencias.

## 4. Restricciones vigentes (recordatorio)

Sin push; sin cambios en HOME salvo instrucción directa del dueño; sin reiniciar servidores
compartidos; sin operaciones de producción. Cada sesión de rol arranca fresca: el paquete debe
llevar todo el contexto. Para una corrida de cierre en worktree, ejecutar `make staging` **dentro**
del worktree antes de la suite (`build/` está gitignoreado).
