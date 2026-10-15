# Review — 003-001-role-packets

Reviewer model: `gpt-5.6-sol` (misma familia que el implementer por la excepción aprobada en ADR-010; no suma el observable de diversidad de familia).

Veredicto final: **CHANGES_REQUESTED**.

## Alcance y evidencia

- Rama revisada: `codex/epic-003-context-efficiency`.
- HEAD revisado: `87b6386e5587e637299a242b2623551d4e294b7b`.
- Base de la rama/epic: `39b48fd`, registrada en `docs/epics/epic-003-context-efficiency/execution.md:22`.
- Parent de la feature: `d6ae7f9`; es el padre de `0efff3b`, primer commit de `003-001-role-packets`. El diff de feature revisado fue `d6ae7f9..87b6386`. El tramo `39b48fd..d6ae7f9` se usó como contexto normativo de mandato y ADR-010.
- Se revisaron spec, plan, aprobación, ADR-010, handoff, estado, implementación, instalador, consumidores, schemas y los tres archivos de tests del diff completo.
- Se reutilizó la evidencia vigente de `docs/specs/003-001-role-packets/auditfix2-green.md:28-42`: `Ran 25 tests in 109.655s` / `OK`. El producto probado es `10b0f9b`; entre ese commit y HEAD no cambian producto ni tests. No se repitió la suite.
- Se ejecutaron sólo probes black-box focales para dudas materiales descubiertas durante el review. Todos fueron efímeros y no modificaron el árbol.

## Bloqueantes

### 1. El canal Task vuelve a cargar el skill completo y anula el paquete mínimo

Veredicto: **BLOQUEANTE**  
Bucket: **h**  
Severidad: **Required — divergencia funcional de P1/P3/P6**  
Problema: El paquete común ordena no cargar el ciclo completo y la spec exige que el rol consuma exclusivamente el paquete y sus inputs. Sin embargo, los cinco agentes OpenCode que reciben el Task conservan una directiva incondicional de cargar `cdad-cycle` (y algunos también `cdad-spec-and-test`). Esa directiva forma parte del prompt del agente y se ejecuta además del stdout renderizado. Por tanto, el canal Task no logra la reducción de contexto aprobada y no es funcionalmente equivalente al handoff de chat. El test de consumidores sólo inspecciona el orquestador y `handoff-prompts.md`, no los agentes receptores reales.
Ubicación: `agents/cdad-architect.md:62`; `agents/cdad-test-writer.md:119`; `agents/cdad-implementer.md:91`; `agents/cdad-reviewer.md:69`; `agents/cdad-scribe.md:68`; contradice `skills/cdad-cycle/packets/common.md:1` y `docs/specs/003-001-role-packets/spec.md:286-290`.  
Sugerencia: Hacer condicional la carga del skill en cada agente base: un Task con metadata válida `---cdad-packet-json` sigue directamente el paquete; el flujo legacy conserva la carga actual. Agregar un test instalado que inspeccione a los cinco receptores y pruebe ambos caminos.

### 2. La excepción `epic-003-single-model` se puede heredar coherentemente a otro epic

Veredicto: **BLOQUEANTE**  
Bucket: **h**  
Severidad: **Critical — boundary/autorización ADR-010**  
Problema: `validate_state` activa la excepción por el string `model_policy`, pero nunca exige `execution.epic_id == "epic-003-context-efficiency"`. Si execution, state, `active_epic`, `epic_features`, delegación y un archivo de autoridad se cambian de manera coherente a `epic-004-other`, la validación devuelve `0` y `model_policy=scoped-exception`. Esto viola el vencimiento/no-herencia de ADR-010 y P4. El test existente sólo muta un lado de cada binding; no prueba una identidad cross-epic autoconsistente.
Ubicación: `skills/cdad-cycle/scripts/cdad_packet.py:199-236`; contrato en `docs/adr/ADR-010-modelo-unico-mvp-epic-003.md:31-59` y `docs/specs/003-001-role-packets/spec.md:591-596`.  
Sugerencia: Fijar explícitamente el epic autorizado para esa policy, o cargar una policy registrada cuya identidad incluya epic/runtime/scope/authority. Añadir el caso negativo autoconsistente de otro epic.

Evidencia focal:

```text
returncode=0
VALID: execution=exec-003-001-t1 runtime=opencode scope=opencode-mvp authority=docs/epics/epic-004-other/execution.md ... model_policy=scoped-exception
```

### 3. Un symlink interno permite relabelar implementación como docs/tests

Veredicto: **BLOQUEANTE**  
Bucket: **h**  
Severidad: **Critical — seguridad y aislamiento de scopes**  
Problema: `_project_path` resuelve el destino sólo para comprobar que permanece dentro del proyecto, pero devuelve el path sin resolver. `classify_path` y `_scope_contains` clasifican luego el texto original. Un symlink `docs/impl-link -> ../src` permite que un test-writer declare `docs/impl-link/secret.py` como input bajo scope `docs`; `validate-request` lo acepta con código `0`. La spec exige resolver symlinks y rechazar destinos fuera del scope, no sólo fuera del proyecto.
Ubicación: `skills/cdad-cycle/scripts/cdad_packet.py:76-87`, `skills/cdad-cycle/scripts/cdad_packet.py:108-131`, `skills/cdad-cycle/scripts/cdad_packet.py:253-280`, `skills/cdad-cycle/scripts/cdad_packet.py:297-308`; contrato en `docs/specs/003-001-role-packets/spec.md:415-428`.  
Sugerencia: Clasificar y comprobar containment sobre el path resuelto relativo al project root, conservando por separado el spelling canónico que se publica. Probar escapes externos e internos entre cada clase sensible.

Evidencia focal:

```text
docs/impl-link -> ../src
input: docs/impl-link/secret.py
validate-request returncode=0
```

### 4. Una raíz válida que coincide con el repo convierte uninstall en borrado del source

Veredicto: **BLOQUEANTE**  
Bucket: **h**  
Severidad: **Critical — operación destructiva fuera del scope esperado**  
Problema: `CDAD_INSTALL_ROOT` sólo se valida como directorio absoluto existente. Los nuevos destinos públicos son `$INSTALL_ROOT/agents` y `$INSTALL_ROOT/skills`. Si la raíz es el propio repo (válida según el contrato actual), esos destinos coinciden con `SOURCE_AGENTS_DIR` y `SOURCE_SKILLS_DIR`; `--uninstall --force` elimina los agentes y skills fuente. El dry-run lo demuestra explícitamente. Además, `uninstall_items` no incluye los nuevos public skills aunque `uninstall_cdad` sí los borra, así que la confirmación no enumera todos los targets reales.
Ubicación: `install.sh:19-35`, `install.sh:391-402`, `install.sh:532-560`, `install.sh:632-651`, `install.sh:675-713`.  
Sugerencia: Canonicalizar la raíz y rechazar cualquier solapamiento entre destinos gestionados y el repo/source antes de toda operación, incluida uninstall/check/dry-run. Hacer que instalación, check, confirmación, dry-run, resumen y uninstall deriven de un único manifest de destinos.

Evidencia focal del dry-run con `CDAD_INSTALL_ROOT=<repo>`:

```text
DRY-RUN UNINSTALL .../cdad/agents/cdad-architect.md
DRY-RUN UNINSTALL skills/cdad-cycle -> .../cdad/skills/cdad-cycle
...
Would remove 11 cdad agents + 8 skills x 2 runtimes
```

El resumen también subcuenta los destinos realmente listados.

### 5. El default documentado de `--project-root` siempre falla

Veredicto: **BLOQUEANTE**  
Bucket: **h**  
Severidad: **Required — bug de interfaz pública P6**  
Problema: argparse usa `default="."`, pero `_absolute_existing_directory` rechaza todo path no absoluto. Por eso omitir `--project-root` no usa el cwd como promete la spec; falla antes de leer execution/state en todos los subcomandos.
Ubicación: `skills/cdad-cycle/scripts/cdad_packet.py:239-243`, `skills/cdad-cycle/scripts/cdad_packet.py:465-480`, `skills/cdad-cycle/scripts/cdad_packet.py:484-496`; contrato en `docs/specs/003-001-role-packets/spec.md:232-235`.  
Sugerencia: Resolver paths relativos contra `Path.cwd()` antes de validar existencia, y cubrir la omisión del flag desde un fixture cuyo cwd sea el project root.

Evidencia focal:

```text
python3 scripts/cdad_packet.py validate-state --execution-context /tmp/does-not-exist.json
ERROR: --project-root must be an absolute existing directory: .
```

### 6. `validate-packet` acepta bytes distintos tras normalizar CRLF

Veredicto: **BLOQUEANTE**  
Bucket: **h**  
Severidad: **Required — integridad canónica P2**  
Problema: El validador lee el paquete con `Path.read_text()`, que aplica universal-newline translation. Un paquete canónico con todos los LF reemplazados por CRLF se normaliza al leer y es aceptado con código `0`, aunque P2 exige igualdad byte a byte y terminadores LF.
Ubicación: `skills/cdad-cycle/scripts/cdad_packet.py:503-509`; contrato en `docs/specs/003-001-role-packets/spec.md:306-328` y `docs/specs/003-001-role-packets/spec.md:579-583`.  
Sugerencia: Leer bytes y comparar con `rendered.encode("utf-8")`; emitir render por `sys.stdout.buffer` si se quiere garantizar LF independientemente de text I/O. Agregar un negativo CRLF.

Evidencia focal:

```text
render_rc=0
validate_crlf_rc=0
```

### 7. Métricas sin `active_packet` aceptan packet/rol/subfase inventados

Veredicto: **BLOQUEANTE**  
Bucket: **h**  
Severidad: **Required — honestidad de métricas P5**  
Problema: Cuando `state.active_packet` es `null`, `validate_metric` omite toda validación de `packet_id`, `role` y `substage`, incluso el enum y la pareja rol/subfase. Un registro con `packet_id="invented"`, `role="operator"` y `substage="deploy"` devuelve `0`. El contrato exige comparar la identidad de la medición con el estado; no hay paquete al cual vincular ese registro.
Ubicación: `skills/cdad-cycle/scripts/cdad_packet.py:415-444`; contrato en `docs/specs/003-001-role-packets/spec.md:556-568` y `docs/specs/003-001-role-packets/spec.md:598-603`.  
Sugerencia: Validar siempre enums y pareja; para la semántica actual, rechazar una métrica si no hay `active_packet`, o definir y aprobar otra fuente estructurada de identidad histórica antes de permitirla.

Evidencia focal:

```text
active_packet=null
packet_id=invented role=operator substage=deploy
validate-metric returncode=0
```

### 8. `CDAD_INSTALL_ROOT` explícito todavía requiere un `HOME` válido

Veredicto: **BLOQUEANTE**  
Bucket: **h**  
Severidad: **Required — aislamiento/portabilidad P6**  
Problema: `main` llama incondicionalmente a `guard_home` antes de `guard_install_root`. Con una raíz absoluta existente y `HOME` ausente, incluso `--dry-run` falla. Esto contradice que la raíz explícita sustituye el prefijo habitual de instalación y hace que el fixture dependa de estado externo que no necesita.
Ubicación: `install.sh:23-33`, `install.sh:385-402`, `install.sh:939-943`; contrato en `docs/specs/003-001-role-packets/spec.md:241-247` y `docs/specs/003-001-role-packets/spec.md:605-611`.  
Sugerencia: Exigir `HOME` sólo cuando `CDAD_INSTALL_ROOT` no está definido; validar/canonicalizar primero la raíz efectiva.

Evidencia focal:

```text
env -u HOME CDAD_INSTALL_ROOT=/tmp ... install.sh --dry-run --basic
ERROR: Cannot resolve home directory ($HOME is empty or not a directory)
```

## Opcionales

### 9. Los schemas públicos son bastante más permisivos que la CLI

Veredicto: **OPCIONAL**  
Bucket: **h**  
Severidad: **Optional — consistencia arquitectónica**  
Problema: `execution-context.schema.json` acepta cualquier objeto como `path_policy`; `rendered-packet.schema.json` acepta cualquier string para role/substage; `packet-request.schema.json` no expresa la correlación rol/subfase ni la forma cerrada de contract/scopes. La CLI corrige esto en runtime, pero un consumidor que use los schemas públicos recibe falsos positivos.
Ubicación: `skills/cdad-cycle/assets/execution-context.schema.json:32`, `skills/cdad-cycle/assets/packet-request.schema.json:12-21`, `skills/cdad-cycle/assets/rendered-packet.schema.json:12-18`.  
Sugerencia: Alinear schemas con las formas cerradas ya implementadas, o documentarlos explícitamente como descriptores parciales que no sustituyen la CLI.

### 10. La dependencia publicada no expresa la versión mínima de Python

Veredicto: **OPCIONAL**  
Bucket: **h**  
Severidad: **Optional — portabilidad**  
Problema: README e instalador dicen sólo “Python 3”, pero la implementación requiere al menos Python 3.7 (`from __future__ import annotations` y `datetime.fromisoformat`). `guard_python3` sólo comprueba que exista un binario, por lo que una instalación con Python 3.6 pasa el guard y el entrypoint falla al arrancar.
Ubicación: `README.md:3-7`, `install.sh:404-407`, `skills/cdad-cycle/scripts/cdad_packet.py:4-7`, `skills/cdad-cycle/scripts/cdad_packet.py:452-459`.  
Sugerencia: Declarar y comprobar la versión mínima, o reescribir las pocas construcciones incompatibles si se pretende soportar todo Python 3 histórico.

## Abstenciones

### 11. Integración automática con un runtime OpenCode real

Veredicto: **ABSTENER**  
Bucket: **h**  
Severidad: **N/A**  
Problema: La propia spec difiere la interceptación/runtime E2E a la integración 003/004 y el entorno disponible no aporta una corrida OpenCode real. No se afirma ni aprobación ni defecto adicional sobre esa integración.
Ubicación: `docs/specs/003-001-role-packets/spec.md:286-292`, `docs/specs/003-001-role-packets/spec.md:649-651`.  
Sugerencia: Mantener esta limitación explícita hasta el gate de integración previsto.

## Resultado por eje

- Correctness: bloqueado por Task que recarga el skill, default roto de project root, normalización CRLF y métricas no vinculadas.
- Readability: la implementación es compacta y legible; los destinos de instalación deberían salir de un manifest único para evitar drift entre install/check/confirm/uninstall/resúmenes.
- Architecture: bloqueado por el alcance cross-epic de ADR-010 y la contradicción entre packet y agente receptor.
- Security: bloqueado por relabel vía symlink y por uninstall sobre el source cuando la raíz colisiona.
- Performance: no se observan regresiones materiales en el diff. El renderer opera sobre tres archivos pequeños y JSON local; la suite 25/25 existente es evidencia suficiente para este review.

Resumen: **8 bloqueantes, 2 opcionales, 1 abstención. CHANGES_REQUESTED.**
