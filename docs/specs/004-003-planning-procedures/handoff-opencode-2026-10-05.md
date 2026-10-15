# Traspaso a OpenCode — 004-003 (2026-10-05)

El orquestador pasa a una sesión OpenCode (`cdad-orchestrator`). Claude solo
revisa entre ciclos, a pedido del dueño.

## Estado
- 004-002 cerrada (2026-10-03). Deuda priorizada en
  `../004-002-project-execution-bootstrap/debt-second-look.md` (F4 alta).
- 004-003 activa, etapa `discovery`. `active_packet` red-027 = `failed` (cerrado).
- Architect cortado dos veces por errores de transporte (sin crédito); pausa
  registrada en `dispatch-ledger.md`. Sesión previa: `<ses-313>`.
- Hay cambios sin commitear ajenos a este traspaso (`plan.md`,
  `planning-contract-draft.md`, `handoff-architect-001.md`,
  `efficient-orchestration-requirements.md`): revisarlos con el dueño antes
  de commitear.

## Modelos
- `mofgw/deepseek-v4.1-flash`: architect, implementer, scribe.
- `mofgw/glm-5.3-flash`: test-writer, reviewer (familia distinta al implementer).

## Próximos pasos
1. Delegar al subagente `cdad-architect` (deepseek) la discovery con
   `handoff-architect-001.md` (+ `efficient-orchestration-requirements.md`).
   Entregable: borrador de spec/plan; read-only.
2. Revisar el borrador contra el código; llevar las decisiones abiertas al dueño.
3. Materializar spec y plan aprobados; avanzar estado a spec→ciclos.
4. Por tarea: RED (test-writer GLM) → GREEN (implementer deepseek) → review
   (GLM) → review-fix → registro PD-17 (resultados/alcance/desvíos) en
   `supervision-record.md` y fila en `dispatch-ledger.md`.
5. Cierre de feature: suite completa en worktree fijado
   (`make staging` y luego `env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests -q -p no:cacheprovider`),
   segunda mirada, Memory Bank (scribe, aprobación del dueño).
6. Planificar la deuda de 004-002 (F4 primero) dentro de 004-003 o como feature propia.

## Reglas
- Paquetes v2: `cdad_packet.py prepare` desde la raíz aislada
  `<home>/.cache/cdad-004-002-v2/root` (`CDAD_OPENCODE_AGENTS_DIR=$R/.config/opencode/agents`).
  Despachar solo si `prepare` da rc=0 y el rol del paquete coincide.
  Marcar `active_packet.status` completed/failed antes del siguiente `prepare` (PD-4).
- Gates: los roles iteran con tests focales; el implementer corre la suite
  completa una vez por tarea; el orquestador solo al cierre; sin gate si el
  diff no toca código ni tests.
- MVP: hallazgos que no rompen el camino feliz van a deuda priorizada; se avanza.
- Límites: mecánicos solo si son obvios y no sobre-restrictivos; la base son
  instrucciones claras por rol (cómo actuar, por qué saltar un límite no
  sirve, detenerse y reportar si bloqueado) + auditoría del orquestador.
  Los paquetes no deben pedir lecturas que la política niega.
- Nunca instalar CDAD en HOME real (`~/.claude`, `~/.config/opencode`): solo
  raíces aisladas (`CDAD_INSTALL_ROOT=...`).
- No leer ni pedir leer `tests/.sensitive-patterns.local`. Sin `--no-verify`,
  sin push automático; commits con pathspec.
- Generalidad: CDAD debe servir a Go (tests junto al código) y a ciclos sin código.
