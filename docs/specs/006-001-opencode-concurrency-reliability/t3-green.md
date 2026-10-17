I'll start by reading the declared inputs and understanding the current state.
Now let me look at the current state of the files to modify and the focal tests.
Let me establish the baseline by running the focal and reference tests before changes.
Now I'll write the updated reference document. Let me compose it carefully, preserving all guard-required concepts while adding the service mode.
The F011 failure looks like pre-existing HOME/install drift. Let me prove it isn't introduced by my change.
Confirmed pre-existing (F011 fails at pristine HEAD too). Now running the declared regressions for the packet.
All green. Now let me review the diff and commit only the two intended files.
# Reporte del rol — implementer GREEN T3 (006-001-opencode-concurrency-reliability)

## Archivos modificados (write scope: `skills/`)

| Archivo | Cambio |
|---|---|
| `skills/cdad-cycle/references/cli-delegation.md` | +170/−19: modos, preflight de servicio, fallback, `service.require`, límites, receta de aislamiento, responsable, delegación nativa vs entre CLIs, declaración de contención no demostrada |
| `skills/cdad-cycle/assets/opencode-exec-config.example.json` | **nuevo** (22 líneas): config de ejemplo portable con `mode: "service"` y `service.require` |

**El adaptador NO necesitó cambios** (`skills/cdad-cycle/scripts/cdad_delegate_opencode.py` sin tocar): los tests focales T3 ya pasaban por el GREEN previo de T1/T1b/T2 (`ddba831`). No edité `tests/`.

## Resumen por PD

- **PD-12** (config de ejemplo ejecutable y portable, AC-8): se creó `assets/opencode-exec-config.example.json` con **cada clave que el adaptador lee** (`runtime`, `binary`, `binary_version`, `model`, `logs_dir`, `sessions_db`, `server`, `auto`, `mode`, `service.require`, `wait.*`), la fila `mode: "service"` y `service.require: false` (default de §2.1), **solo placeholders `<...>` y defaults**, sin rutas/puertos/proveedor/modelo del host. JSON válido (parseado).
- **PD-6** (concurrencia útil, AC-3): `cli-delegation.md` documenta la concurrencia con fixture (dos proyectos, mismo store/servidor → dos `completed`, sesión/`directory`/nonce propios) y los **dos recorridos reales** (servidor descartable y servicio vivo), con la receta de aislamiento. **Se declara que la eliminación de bloqueos del store NO se demuestra** (observación empírica, AC-7). Los recorridos reales los corre el orquestador/dueño (integración), no este paquete.
- **PD-1/PD-13/PD-14/INV-2/INV-10** (referencia): tabla de selección `server|service|standalone`, compatibilidad sin `mode` (D-9), preflight de servidor y de servicio (`service status` **una vez**, interpretación cerrada, gate de versión **D-11** proyectando solo la clave `version`), fallback `service`→`standalone` **declarado y contable** solo con el servicio detenido (`service-unavailable`), `service.require` (D-10), y límites: **nunca** arrancar/reiniciar/reconfigurar el servicio ni servidores; **nunca** escribir ni mantener el store (solo lectura). Responsable del servidor y del servicio: **dueño/operador, CDAD no**.
- **INV-6/INV-7**: sin valores del host; la guarda `test_005_010_t3_references.py` (patrones prohibidos + hosts de URL neutrales) queda verde.
- **PD-8/D-7/D-8** (terminaciones/recorrido): se conserva y refuerza la clasificación y la delegación nativa con `task` dentro de OpenCode (sesiones hijas en el mismo servidor) frente a la delegación **entre CLIs** (el adaptador).

## Comandos con líneas finales

```
python3 -c "json.load(open('skills/cdad-cycle/assets/opencode-exec-config.example.json'))"
  → JSON OK

python3 -m pytest tests/test_006_001_t3_concurrency.py tests/test_005_010_t3_references.py -q -p no:cacheprovider
  → 7 passed in 4.81s

# Regresiones declaradas del packet T3:
python3 -m pytest tests/test_005_010_t3_references.py tests/test_006_001_t1_selection.py \
  tests/test_006_001_t1b_service_mode.py tests/test_006_001_t2_wait_recovery.py \
  tests/test_005_009_t4_acceptance.py -q -p no:cacheprovider
  → 53 passed, 1 skipped in 88.52s   (el skip es el opt-in preexistente de 005-009 T4)

make validate
  → Assert PASS: 155
    Assert FAIL: 1
    FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
```

**Sobre el FAIL de `make validate`:** es **preexistente, no introducido** por este cambio. Verificado revirtiendo temporalmente mis dos archivos al estado de `HEAD` y corriendo `bash tests/validate-consistency.sh`: **el mismo único FAIL (F011, `Assert FAIL: 1`)** persiste — proviene del *drift* entre el repo y las copias instaladas en `HOME` (`~/.config/opencode/agents`, `~/.claude/skills`), que por regla **no se reinstala ni se toca**. Mi cambio sólo suma entradas de drift del mismo assert (el doc modificado y el asset nuevo ausente en la copia instalada), sin crear ningún assert fallido nuevo (155 PASS / 1 FAIL idénticos).

`tests/test_006_001_t3_integration.py` (recorrido real, opt-in por entorno) queda omitido por defecto; lo corre el orquestador con la credencial del operador — no es este paquete.

## Commit

```
d0a7963 feat: 006-001 T3 GREEN referencia de delegacion CLI (modos server|service|standalone,
        preflight de servicio, config de ejemplo)
 2 files changed, 192 insertions(+), 19 deletions(-)
```

Sin `--no-verify`, sin `git stash`, sin push; `git status --short` limpio tras el commit (solo los dos archivos del write scope). No toqué `HOME`, el runtime real ni el servicio.

## Declaraciones honestas

1. **El adaptador no requirió cambios** y no lo toqué: los focales T3 ya pasaban por T1/T1b/T2; el RED de T3 probó la sensibilidad del oráculo por mutación (informe `t3-red.md`). Este GREEN entrega la **referencia y la config de ejemplo** (PD-12 + documentación de PD-6/PD-13/PD-14 que juzga la review).
2. **PD-12 no tiene test en la suite** (lo declara `t3-red.md`): su verificación es de implementer/review (leer el asset) y del gate de cierre; verifiqué que el JSON es válido, que cada clave es una que el adaptador lee y que no hay valores del host.
3. **La eliminación de bloqueos del store no está demostrada**: queda documentada como observación empírica (AC-7), no como propiedad probada.
4. Los recorridos **reales** (servidor y servicio vivo) y la **suite completa** corresponden a quien cierra (gate de integración), no a este paquete.
