# RED report — 003-001-role-packets / Tarea 1

Fecha: 2026-09-17  
Rol: test-writer RED, aislado de implementación  
Resultado: **RED válido**

## Resultado focal

Comando:

```text
python3 -m unittest -v tests.test_role_packets
```

Resultado: 2 tests ejecutados, 1 fallo, exit code 1.

Rerun final tras la corrección autorizada del fixture: `epic_features.status`
usa `in-progress`; `current_stage` permanece `tdd`. El resultado no cambió.

- El test P6 ejecutó exclusivamente `bash install.sh --dry-run --basic`, con
  `CDAD_INSTALL_ROOT` igual a un directorio temporal absoluto existente y
  `CDAD_SKILL_EXTRA_DIRS` vacío. No alteró `HOME`.
- Falló por `AssertionError` contractual: los 48 destinos publicados por los
  registros `DRY-RUN COPY ... -> DEST` y `DRY-RUN MARKER DEST = ...` quedaron
  fuera de `CDAD_INSTALL_ROOT`.
- La disponibilidad de `scripts/cdad_packet.py` se informó separadamente como
  `BLOCKED (not semantic RED)`. Ese test terminó `ok`; la ausencia de CLI no es
  la causa del RED.
- No se ejecutó `install.sh` sin `--dry-run`, ni `--check`, ni
  `validate-subagents.sh`.

Log original privado: transporte temporal. Evidencia verificada y anonimizada: `evidence/t1-red.log`.

## Mapeo test → contrato

| Test | Postcondición | Contrato observable |
|---|---|---|
| `TestInstallRootDryRun.test_p6_dry_run_confines_every_destination_to_explicit_install_root` | P6 | Todo destino publicado por dry-run queda bajo la raíz absoluta de `CDAD_INSTALL_ROOT`; además aparecen los seis prefijos documentados: `.config/opencode/agents`, `.config/opencode/skills`, `.agents/skills`, `.claude/agents`, `.claude/skills`, `.claude/cdad-scripts`. |
| `TestStateBindingMatrixWhenCliAvailable.test_p4_p5_state_binding_matrix_or_report_interface_blocked` | P4/P5 | Cuando exista la CLI pública, acepta los pares autorizados OpenCode/Codex, rechaza bindings discordantes, cierre/revocación y autoridad discordante; acepta `active_packet=null` y rechaza un paquete activo incompleto. Mientras no exista, informa BLOCKED sin skip ni falso RED. |

La prueba P6 analiza sólo destinos declarados por el output público. No exige
ausencia de `/home` en rutas fuente, no congela timestamps ni texto auxiliar y
no lee la implementación del instalador.

## Fixtures reutilizables

`tests/test_role_packets.py` incluye:

- `execution_document()` para los pares runtime/scope autorizados;
- `state_document()` con binding de ejecución, autoridad HITL y
  `active_packet` configurable; el estado de la feature dentro del epic es
  `in-progress`, separado de `current_stage: tdd`;
- `StateFixture` para crear un project root temporal autocontenido;
- `invoke_validate_state()` para la firma pública de §4;
- una matriz P4 de ID, epic, feature, runtime, scope, autoridad, epic activo,
  feature activa, cierre, revocación y fuente de delegación discordantes;
- los dos casos P5 iniciales de `active_packet` nulo/incompleto.

No se escribieron tests de Tarea 2 o Tarea 3. La matriz se activa
automáticamente cuando el entrypoint de Tarea 1 exista.

## Archivo modificado

- `tests/test_role_packets.py` — nuevo runner unittest black-box.

No se modificó ningún otro archivo del repositorio y no se realizaron
operaciones git o de estado CDAD.

## Archivos leídos

- `docs/specs/003-001-role-packets/spec.md`
- `docs/specs/003-001-role-packets/plan.md`
- `docs/specs/003-001-role-packets/test-audit.md`
- listado de `tests/**`; antes de este cambio sólo contenía
  `tests/validate-consistency.sh` y `tests/validate-odoo-specialization.sh`.

No se leyó `scripts/**`, `install.sh`, `agents/**`, `skills/**`, `src/**`,
`lib/**` ni un diff de implementación.

## Comandos ejecutados

1. Lectura de spec, plan y audit aprobados; inventario de `tests/**`.
2. Probe seguro: `mktemp -d /tmp/cdad-install-red-probe.XXXXXX`.
3. Probe black-box: `env CDAD_INSTALL_ROOT=<tmp> CDAD_SKILL_EXTRA_DIRS= bash install.sh --dry-run --basic`.
4. Focal RED: `python3 -m unittest -v tests.test_role_packets`.

## Gate RED

Cumplido: el fallo demuestra comportamiento actual contrario a P6 mediante
una assertion, no mediante import error, command-not-found o ausencia de CLI.
El siguiente paso corresponde al implementer GREEN de Tarea 1. Antes de una
instalación real, debe verificarse que este test queda verde y que todos los
destinos del dry-run están confinados; esa autorización no forma parte de este
handoff.

Validado por Codex (HITL delegado): reproducción independiente del fallo
contractual P6. P4/P5 siguen pendientes de ejecutar, no se cuentan como verdes.
Se autoriza corregir únicamente el enum de fixture `epic_features.status`
de `tdd` a `in-progress`; no cambia las expectativas del contrato.
