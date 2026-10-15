---
feature_id: 003-005-claude-code-packets
feature_name: Paquetes utilizables en Claude Code (port + prepare)
created_at: 2026-09-18
approved_by: Pablo
approved_at: 2026-09-18
---

# Spec: Paquetes utilizables en Claude Code

## Motivo

003-001 dejó el renderer y el camino de paquete en los agentes OpenCode, pero:
(a) ningún comando prepara `REQUEST.json` ni el binding del state, así que
`render` nunca corrió contra un state real (`validate-state` falla con
`state.execution must be an object` en este mismo repo); (b) los agentes de
Claude Code (`agents/claude-code/`) no conocen el camino de paquete. Esta
feature los resuelve sin ampliar el alcance de 002 (sin receipts, journal ni
idempotencia).

## Contrato

### 1. Subcomando `prepare`

```text
python3 cdad_packet.py prepare \
  --project-root ROOT \
  [--execution-context EXEC.json]        # default: ROOT/.cdad/execution.json
  --role ROLE --substage SUBSTAGE \
  --objective TEXT \
  [--input PATH=PURPOSE]...              # se agregan después del contrato
  [--read-scope CLASS=SELECTOR]...       # reemplazan el default de lectura
  [--write-scope CLASS=SELECTOR]...      # reemplazan el default de escritura
  [--invariant TEXT]...                  # se agregan a los defaults del rol
  [--expected-output TEXT] \
  [--evidence TEXT]...                   # reemplazan el default
  [--out-dir DIR]                        # default: ROOT/.cdad/packets
```

`SELECTOR` es un directorio (se emite como `root`) o un archivo existente (se
emite como `path`). La clase `repository-read` se escribe sin selector:
`--read-scope repository-read`.

Derivaciones deterministas (sin flags):

- `packet_id`: `<feature_id>-<role>-<substage>-NNN`, donde NNN (3 dígitos,
  desde 001) es el primer número libre en `--out-dir`.
- `contract`: kind y path según la regla de 003-001 (`approved-epic-plan` y
  `docs/epics/<epic_id>/plan.md` para architect; `approved-feature-spec` y
  `docs/specs/<feature_id>/spec.md` para los demás). `sha256` es el del
  contenido actual; `commit` es `null`.
- `inputs`: primero `{path: <contract.path>, purpose: "approved contract"}` y
  después cada `--input`, en orden.
- Scopes por defecto:
  - test-writer: lectura = `contract` sobre el directorio del contrato + `tests`
    sobre cada `test_roots`; escritura = `tests` sobre cada `test_roots`.
  - implementer: lectura = `repository-read`; escritura = `implementation`
    sobre cada `implementation_roots` + `implementation` (path) por cada
    `implementation_files`.
  - architect, reviewer, scribe: lectura = `repository-read`; escritura = `[]`.
- `invariants` por defecto: test-writer `["Do not read implementation code",
  "Each test maps to a postcondition"]`; implementer `["Do not edit tests"]`;
  los demás `[]`. Los `--invariant` se agregan al final.
- `expected_output` por defecto: `"Role report with the required evidence"`.
- `evidence_required` por defecto: `["modified files", "exact commands",
  "command output", "commit"]`.

### 2. Efectos

Si todo valida, `prepare` hace exactamente tres escrituras:

1. `OUT/<packet_id>/REQUEST.json`.
2. `OUT/<packet_id>/PACKET.md`.
3. `ROOT/docs/.cdad-state.json`: `execution` pasa a ser exactamente los 7
   campos de binding del execution context (`id, epic_id, feature_id, runtime,
   scope, model_policy, authority_ref`, sin `model`) y `active_packet` pasa a
   `{id, role, substage, status: "prepared", packet_version: 1, contract_kind,
   contract_sha256}`. Las demás claves del state quedan iguales (igualdad JSON).
   El archivo se escribe con indentación de 2, UTF-8 y newline final.

stdout es exactamente el paquete: los mismos bytes que `PACKET.md` y que
`render` produce después con el mismo execution, el REQUEST escrito y el state
resultante. `validate-packet` sobre esos tres archivos pasa. Exit 0.

### 3. Fallo sin efectos

Cualquier error (role/substage inválido, contrato ausente, scope fuera de
política, execution inválido, flag mal formado, validación del state
resultante) termina con exit 2, `ERROR: ...` en stderr, stdout vacío, y sin
crear archivos: `OUT` no gana entradas y el state queda igual byte a byte.

Enmienda (review 1, 2026-09-18): esto incluye los fallos durante la
escritura (choque de packet_id, state no serializable): se serializa todo
antes de escribir y el rollback solo borra lo que creó la propia invocación.
`feature_id` y el `packet_id` derivado deben ser nombres planos
(`[A-Za-z0-9._-]+`, sin `..`); si no lo son, es un error de validación.

### 4. Port a Claude Code

- Los 10 agentes de rol de `agents/claude-code/` (5 base + 5 odoo) incorporan
  la misma directiva de dos caminos que los agentes OpenCode de 003-001: con un
  paquete validado (primera línea `---cdad-packet-json`) lo siguen sin cargar
  `cdad-cycle`; sin paquete cargan la skill como antes; si dice ser un paquete
  pero es inválido, se detienen y lo reportan. Los agentes odoo conservan la
  carga de sus skills de dominio también en el camino de paquete.
- `agents/claude-code/cdad-orchestrator.md`, `agents/cdad-orchestrator.md` y
  `skills/cdad-cycle/references/handoff-prompts.md` indican `prepare` como la
  forma de producir el paquete y que su stdout se pasa sin cambios como prompt
  de Task.
- Las barreras existentes de Claude Code (hooks `path-guard`, tools) no cambian.

## Postcondiciones

- P1: `prepare` válido produce las tres escrituras de §2 y stdout == PACKET.md
  == `render` posterior; `validate-packet` pasa.
- P2: las derivaciones por defecto de §1 (packet_id incremental, contrato,
  inputs, scopes, invariants, output, evidence) son las observadas en REQUEST.json.
- P3: los flags explícitos reemplazan o se agregan según §1.
- P4: cualquier fallo cumple §3 (sin archivos, state byte a byte igual).
- P5: instalado en una raíz aislada, el `cdad_packet.py` instalado ejecuta
  `prepare` contra un proyecto fixture y produce el mismo paquete que el del repo.
- P6: los agentes Claude Code instalados cumplen §4 y conservan sus hooks.

## Fuera de alcance

Transiciones de `active_packet` después de `prepared` (dispatched/completed),
receipts, journal, creación automática de `execution.json` y packets de
architect sin plan de epic. Registrado como limitación: una feature suelta sin
epic no puede generar un paquete de architect (va por el flujo de siempre).
