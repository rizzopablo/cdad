# Evidencia — aceptación PD-10 (paso a: antes del despliegue)

Fecha: 2026-10-11. Corrida por el orquestador Claude (coordinador real, sesión de Claude Code).
Cubre PD-9(a) de 005-010 y PD-10 de 005-009. El paso b (confirmación desde la instalación
global, después del despliegue del dueño) queda pendiente.

Rutas abreviadas: `<tmp>` es un directorio temporal del workspace y `<home>` el HOME del dueño.

## 1. Versión e instalación aislada

- Versión: commit `3c9d3ee` (HEAD de `codex/epic-005-real-operation` al correr).
- Worktree fijado a ese commit en `<tmp>/src`; `make staging PROFILE=basic`;
  `CDAD_INSTALL_ROOT=<tmp>/root ./install.sh --basic --force` → rc 0,
  «Verify: PASS — 11 cdad agents present after install»; `<tmp>/root/version.txt` = `3c9d3ee…`.
- HOME del dueño sin tocar: la instalación global sigue en `6f4d5db`.

## 2. Proyecto temporal

- `git clone` del repo en `<tmp>/proj` (rama `codex/epic-005-real-operation`, mismo commit).
- `prepare` con el CLI de la instalación aislada y
  `CDAD_OPENCODE_AGENTS_DIR=<tmp>/root/.config/opencode/agents`:
  `--role architect --substage discovery --new-execution`, encargo mínimo de solo lectura
  (informar el sha256 de la spec de 005-010 y sus ids PD-n). Paquete
  `005-010-real-opencode-delegation-architect-discovery-001`; agente derivado `mode: subagent`.
- `cdad-version-check.py --project-root <tmp>/proj` → `COHERENT` (proyecto, agentes y CLI en
  `3c9d3ee`).

## 3. Recorrido

Coordinador: esta sesión de Claude Code, con `PWD` = `<workspace>/projects/cdad`, distinto del
proyecto (prueba de PD-3 de 005-009 y del arreglo de `PWD`).

```
python3 <tmp>/root/.claude/skills/cdad-cycle/scripts/cdad_delegate.py \
  --project-root <tmp>/proj \
  --packet 005-010-real-opencode-delegation-architect-discovery-001 \
  --destination opencode --exec-config <tmp>/exec-config.json
```

`exec-config.json`: runtime `opencode`, binario de OpenCode v2.0.26, base de sesiones del
runtime, modelo y `wait.timeout_seconds` (valores locales, fuera del repo).

Salida (rc 0, 36 s):

```json
{"attempt": "delegate-opencode-b5264bfa7864",
 "delivery_ref": "<tmp>/proj/.cdad/runtime/results/exec-005-010-real-opencode-delegation-001/005-010-real-opencode-delegation-architect-discovery-001/receipt.json",
 "diagnosis": null, "session": "<ses-141>", "termination": "completed"}
```

## 4. Verificación

- Fila durable (lectura `mode=ro`): `agent = cdad-architect`, `directory = <tmp>/proj`,
  `idle_outcome = succeeded`, modelo del proveedor configurado.
- Recibo: `semantic_status: pending`, `identity_validation: passed`,
  `packet_validation: passed`, `role: architect`, `substage: discovery`.
- Entrega: el sha256 informado (`baf195a3…891b`) coincide con `sha256sum` de la spec; los ids
  informados (PD-1..PD-10) coinciden con la spec.
- Ledger I8: dos registros, el de la interfaz (`delegate-opencode-…`, `model_reported: null`) y
  el del worker (`opencode-…`, `session` y `model_reported` desde la fila durable).
- `cdad_continuity.py reconcile` → `classification: received`, `repeat_effect: false`.

## 5. Re-entry del coordinador

En el state del proyecto temporal: `active_packet.status` `dispatched` → `completed` y entrada
`pd10-acceptance-reentry` en `stage_history` con la referencia al recibo;
`validate-state` → `VALID`. La interfaz, el adaptador y el worker no escribieron el state.

## 6. Hallazgos durante la aceptación

- **Corregido en el ciclo:** `opencode run` toma el directorio del proyecto de la variable
  `PWD`, no del cwd del proceso. La primera corrida de la integración (T4) ejecutó el rol en el
  directorio del coordinador. Arreglo: el adaptador fija `PWD` = raíz del proyecto (`3c9d3ee`);
  test en `tests/test_005_010_t2_load_mode_invocation.py::TestPd4PwdProjectDirectory`.
- **Menor, para la review:** `model_reported` del registro del worker guarda el objeto de modelo
  de la fila como texto JSON (`{"id":…,"providerID":…}`) y no como `proveedor/modelo`.

## 7. Paso b — confirmación desde la instalación global (2026-10-11)

- Despliegue del dueño («Despliegalo y aprueba»): `.cdad/local/deploy-005-010-home.sh c9f4810`;
  `<home>/version.txt` = `c9f4810…`. `install.sh --check` informó DRIFT solo por el
  `__pycache__` de `cdad-cycle/scripts` (76 archivos del producto contra 77 instalados, deuda
  conocida).
- Proyecto temporal de la aceptación: `prepare` con el CLI global republicó los agentes desde la
  instalación global (diagnóstico de cambio de origen, sin cambio silencioso);
  `cdad-version-check` → `COHERENT` en `c9f4810`.
- `cdad_delegate.py` global → `termination: completed`, sesión
  `<ses-146>` (`agent = cdad-architect`, directorio del proyecto
  temporal, `idle_outcome = succeeded`); recibo `pending`, identidad y paquete `passed`; entrega
  con el sha256 correcto de la spec y 10 ids PD; `reconcile` → `received`; re-entry `VALID`.

## 8. Paso b con B1 desplegada (2026-10-13)

- Despliegue autorizado por el dueño con el otro proyecto activo en reposo: `.cdad/local/deploy-005-003-home.sh 0650655`.
  Incluye B1 (005-010), 005-002 y 005-003 con F2. `<home>/version.txt` = `0650655…`. El chequeo dio
  DRIFT solo por `__pycache__` de `cdad-cycle/scripts` (82 archivos del producto contra 84
  instalados; la diferencia son dos `.pyc`). Los scripts son idénticos al repo en las tres
  instalaciones. El respaldo completo de los artefactos del manifiesto quedó fuera del repo.
- Proyecto temporal de la aceptación: `prepare` con el CLI global y `cdad-version-check` →
  `COHERENT`.
- `cdad_delegate.py` global → `termination: completed`, recibo `pending`, identidad y paquete
  `passed`. La entrega trae el sha256 correcto de la spec (`baf195a3…891b`) y sus 10 PD-n.
  `reconcile` → `received`, `repeat_effect: false`.
