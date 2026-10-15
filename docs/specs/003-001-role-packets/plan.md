---
feature_id: 003-001-role-packets
created_at: 2026-09-17
status: approved
---

# Plan — 003-001 Role packets

## Restricciones globales

- Contrato observable definido por `spec.md`; no anticipar implementación.
- Python 3 stdlib, sin dependencias descargadas.
- Un único renderer/policy compartido; no duplicar el guard entre comandos.
- Modelo único no relaja scopes, sesiones, evidencia, gates ni aprobaciones.
- No recibir ni persistir resultados: eso pertenece a `003-002`.
- Tests existentes sólo cambian bajo la justificación explícita del spec.
- Fixtures usan project/install roots temporales; nunca modifican instalación
  real ni reutilizan `HOME` como variable de tarea.

## Tarea 1 — Estado, path policy y guard compartido

**Postcondiciones:** P4 y base estructural de P5/P6.

**Archivos**

- Create: schemas/fixtures públicos bajo `skills/cdad-cycle/assets/` y `tests/`.
- Create: política compartida en `skills/cdad-cycle/scripts/`, junto al
  entrypoint canónico inicial `cdad_packet.py` para `validate-state` y el
  wrapper fino `scripts/cdad_packet.py`. Los comandos de Tarea 2 lo amplían.
- Modify: `skills/cdad-cycle/assets/state-template.json`.
- Modify: `scripts/validate-subagents.sh`.
- Modify: `install.sh` para CDAD_INSTALL_ROOT; es prerrequisito del fixture
  del guard y se implementa aquí, no se posterga a Tarea 3.
- Test: runner black-box de estado, paths, autoridad y excepción.

**Consume**

```text
--project-root ROOT
EXECUTION.json
ROOT/docs/.cdad-state.json
CDAD_INSTALL_ROOT opcional
```

**Produce**

```text
validate-state(execution context, project state) -> exit status + diagnostic
classify_path(path, path policy) -> one mechanical class or rejection
validate_model_policy(execution, state) -> ordinary | scoped exception | rejection
```

La política valida igualdad exacta de execution/state, membresía de feature,
etapa activa, autoridad estructurada, vigencia y pares runtime/scope. Una
excepción inválida falla antes de compatibilidad `basic`.

**TDD**

1. RED de comportamiento sobre el dry-run existente de instalación aislada. La ausencia
   de la futura CLI se prueba aparte como disponibilidad, no como fallo del
   contrato.
2. GREEN mínimo para matriz de binding, paths seguros, active packet nullable y
   fixture roots.
3. Evidencia focalizada de P4 y parte de P5/P6; no declarar suite integrada.

## Tarea 2 — Contrato canónico y renderer

**Dependencia:** Tarea 1 verde en su subconjunto público.

**Postcondiciones:** P1, P2, P3 y métricas de P5.

**Archivos**

- Create: `skills/cdad-cycle/packets/common.md`.
- Create: `skills/cdad-cycle/packets/roles/*.md`.
- Create: `skills/cdad-cycle/packets/substages/*.md`.
- Create: schemas de request, packet y metric bajo
  `skills/cdad-cycle/assets/`.
- Modify: `skills/cdad-cycle/scripts/cdad_packet.py` como implementación
  canónica instalable.
- Modify: `scripts/cdad_packet.py` como wrapper fino del repo.
- Test: fixtures por pareja rol/subfase, manipulación y scopes.

**Consume**

```text
EXECUTION.json
REQUEST.json
estado validado por Tarea 1
contrato aprobado y templates canónicos
```

**Produce**

```text
python3 scripts/cdad_packet.py render ... -> paquete Markdown por stdout
python3 scripts/cdad_packet.py validate-request ...
python3 scripts/cdad_packet.py validate-packet ...
python3 scripts/cdad_packet.py validate-state ...
python3 scripts/cdad_packet.py validate-metric ...
```

El renderer invoca la política única de Tarea 1. Discovery consume
`approved-epic-plan`; no fabrica un feature spec aprobado. `validate-packet`
re-renderiza y compara bytes.

**TDD**

1. RED: determinismo, JSON canónico, tampering, hash, combinaciones inválidas,
   path/scope e identidad de métricas.
2. GREEN: composición mínima y validación suficiente para P1/P2/P3/P5.
3. Verificar todos los roles/subfases y que no aparezcan reglas cruzadas.

## Tarea 3 — Consumidores y entorno aislado

**Dependencias:** Tareas 1 y 2 verdes en sus contratos públicos.

**Postcondiciones:** integración de P3/P6 y compatibilidad completa de P4.

**Archivos**

- Modify: `agents/cdad-orchestrator.md`.
- Modify: agentes base `agents/cdad-*.md` aplicables.
- Modify: `skills/cdad-cycle/SKILL.md`.
- Modify: `skills/cdad-cycle/references/handoff-prompts.md`.
- Modify: `skills/cdad-cycle/references/opencode-delegation.md`.
- Modify: `install.sh`, README y validator para dependencia Python,
  `--project-root` y `CDAD_INSTALL_ROOT`.
- Modify: assertions textuales existentes sólo bajo la justificación del spec.
- Test: paridad Task/chat, instalación aislada y no regresión de permisos.

**Consume**

```text
renderer y policy de Tareas 1-2
agentes/templates vigentes
project root e install root aislados
```

**Produce**

```text
consumidores que seleccionan common + role + substage
Task y chat nuevo con el mismo contrato funcional
dependencia Python visible
install-check y validator ejecutables contra fixtures aislados
entrypoint instalado que resuelve assets relativos a la skill instalada
```

La CLI sólo valida declaraciones. El orquestador conserva la comprobación
obligatoria de archivos modificados en re-entry; no se atribuye esa capacidad
al renderer.

**TDD**

1. RED sobre consumidores existentes y referencias duplicadas; assertions de
   disponibilidad separadas.
2. GREEN para migrar consumidores sin alterar permisos ni gates.
3. Verificar P3/P6, matriz completa P4 y compatibilidad `basic` ordinaria.
4. Smoke instalado desde un proyecto sin wrapper del repo; exigir mismos bytes,
   códigos y diagnósticos que la interfaz fuente.

## Integración final

Sólo después de las tres tareas:

1. Ejecutar matriz black-box P1-P6 con cero skips/bloqueados.
2. Ejecutar `tests/validate-consistency.sh` y comparar contra baseline conocido
   123 PASS / 1 FAIL, aislando F011 de copia instalada.
3. Ejecutar `tests/validate-odoo-specialization.sh`.
4. Ejecutar `validate-subagents.sh` e `install.sh --check` contra project/install
   roots temporales.
5. Ejecutar el smoke del CLI instalado desde un proyecto consumidor sin árbol
   `scripts/` del repo y comprobar paridad.
6. Verificar que la instalación real no cambió.
7. Registrar que existe un ejecutable OpenCode fuera de PATH y que la
   aceptación runtime automática completa queda para integración 003/004.
8. Registrar la deuda CI ya existente; usar el gate local permitido.

## Auto-revisión

- Cobertura: Tarea 1 → P4/P5/P6; Tarea 2 → P1/P2/P3/P5; Tarea 3 → integración
  P3/P4/P6. Todas las postcondiciones tienen tarea y ninguna tarea carece de
  postcondición.
- Sin placeholders de comportamiento.
- Firmas consistentes: `--project-root`, `--execution-context`, `--request`,
  `--packet`, `--record` y `CDAD_INSTALL_ROOT` conservan el mismo significado.
- No se declara suite global verde antes de Integration final.

---

Status: Approved by Codex (agent-delegated, pedido explícito del usuario el 2026-09-17) on 2026-09-17
