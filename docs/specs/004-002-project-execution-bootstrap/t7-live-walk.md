# Recorrido real de 004-002 en v2 (PD-13, C1, C2) — 2026-10-01

Evidencia del tramo v2. El corte y la publicación están en `cut-c.md`.

## 1. Primer encargo v2 (T7, matriz integral de aceptación)

- Paquete `004-002-project-execution-bootstrap-test-writer-red-019`, ejecución
  `exec-004-002-project-execution-bootstrap-001`. Despacho: OpenCode 2.0.16
  `--standalone`, agente de proyecto `cdad-test-writer` (derivado), modelo
  `mofgw/glm-5.3-flash`, sesión `<ses-290>`.
- Registro I8: `prepare --record-dispatch … --attempt-id a1` → rc 0;
  `.cdad/executions/<id>/dispatches/a1.json`; el paquete pasó de `prepared` a
  `dispatched`.
- Resultado: `7e7a3a9` (`tests/test_004_002_t7_acceptance.py`): tabla de
  trazabilidad PD-1..PD-13 y criterios 1–8; tres tests nuevos (resume entre
  sesiones, matriz 4 layouts × 4 consumidores desde el producto instalado,
  cita anclada de los cinco puntos de PD-11), en verde; 166 passed en los
  suites citados. El rol no recibió denegaciones: nunca intentó leer
  implementación.

## 2. Verificación en vivo de C1 (sondas del orquestador)

Como el encargo no ejercitó la barrera, el orquestador hizo una sonda
explícita: el mismo prompt (read de `scripts/cdad-generate.py`, grep `"def "`
en `scripts`, glob `*.py` en `skills`, read de un test) con el mismo modelo,
en dos proyectos:

| Llamada | Agente de proyecto (este repo, v2) | Agente global (copia sin `.opencode/`) |
|---|---|---|
| read `scripts/cdad-generate.py` | **denegada** (`permission.rejected`) | ejecutada |
| grep `"def "` en `scripts` | ejecutada (31 coincidencias) | ejecutada |
| glob `*.py` en `skills` | ejecutada | ejecutada |
| read de un test | ejecutada | ejecutada |

`read` y su contraste prueban que la barrera por ruta de lectura depende del
agente de proyecto y funciona en vivo. `grep` y `glob` no se bloquearon.

## 3. Hallazgo W-2: en OpenCode, grep/glob se median por el patrón de búsqueda

Sonda de semántica con un agente de prueba (`grep: {"*": allow, "def*":
deny}`, `glob: {"*": allow, "*.py": deny}`):

| Llamada | Resultado |
|---|---|
| grep `"def "` en `scripts` | denegada |
| grep `"import"` en `scripts` | ejecutada |
| glob `*.py` en `skills` | denegada |
| glob `**/*.md` en `docs` | ejecutada |

OpenCode evalúa los permisos de `grep` y `glob` contra el **patrón de
búsqueda** (regex o glob), no contra la ruta. Los mapas por ruta que I9
deriva para `grep`/`glob` son inertes en OpenCode. Los tests de T5 usaban un
evaluador sintético, y las reviews se habían abstenido sobre la semántica
real; el recorrido real lo encontró.

**Disposición del orquestador** (criterio 3 de la spec: "si no funciona, se
declara la limitación y se usa el modo verificado"):

- Los derivados dejan de emitir entradas por ruta en `grep`/`glob`: no deben
  declarar una barrera que no existe. `read` y `edit` conservan sus mapas
  (verificados en vivo).
- Limitación declarada en la guía, de la misma clase que `bash` permisivo: en
  OpenCode, las búsquedas no están acotadas por ruta. Negar `grep`/`glob`
  por completo no aporta, porque `bash` es permisivo por decisión del dueño.
- En Claude Code, el guard sí media `Grep`/`Glob` por `path`/`pattern` (C2);
  queda la prueba en una sesión real.

## 4. Robustez de la barrera de lectura y servicio de fondo

Sondas adicionales con el agente de proyecto `cdad-test-writer`:

| Llamada | Resultado |
|---|---|
| read con ruta absoluta del repo a `scripts/cdad-generate.py` | denegada |
| read `./scripts/cdad-generate.py` | denegada |
| read `scripts/../scripts/cdad-generate.py` | denegada |
| read `skills/cdad-cycle/SKILL.md` | denegada |
| listado del directorio `scripts` | ejecutado (solo nombres) |

La barrera de lectura resiste las variantes de ruta. El listado de un
directorio de implementación muestra nombres pero no contenido: se acepta y
se declara como limitación.

**Servicio de fondo (criterio 3):** `opencode run` sin `--standalone`, desde
la raíz del repo → read de `scripts/` denegado y read de un test ejecutado.
El servicio carga los agentes de proyecto `.opencode/agents/`; retomar
sesiones sin `--standalone` conserva las barreras v2.

**C1:** verificada para lectura (con contraste, variantes de ruta y servicio
de fondo). Búsquedas: ver W-2.

## 5. C2 en una sesión real de Claude Code

Claude Code 2.1.285, `claude -p` (modelo haiku), en una copia del repo con
`docs/cdad-policy.json` y un hook `PreToolUse` de proyecto que invoca el guard
de la instalación aislada (`path-guard.sh test-writer-read`, con
`CDAD_PACKET_CLI` apuntando a su CLI). Entrada real de las herramientas
(Claude Code envía `Read` con ruta absoluta):

| Llamada real | Resultado del guard |
|---|---|
| `Read {file_path: <abs>/scripts/cdad-generate.py}` | bloqueada: "test-writer may not read implementation (scripts/cdad-generate.py)" |
| `Grep {pattern: "def ", path: "scripts"}` | bloqueada (implementación) |
| `Glob {pattern: "*.py", path: "skills"}` | bloqueada (implementación) |
| `Grep {pattern: "def "}` (sin `path`) | bloqueada: pide acotar a tests/docs |
| `Read {file_path: <abs>/tests/test_004_002_t7_acceptance.py}` | permitida |

**C2:** verificada con la forma real de entrada y en una sesión real. La
instalación global de Claude Code no se tocó (decisión del dueño): el hook de
la prueba es de proyecto y apunta a la instalación aislada.

## 6. Ruta privada (P-1) en vivo, con la revisión de política `9ffb7d16` (2026-10-02)

Sondas del orquestador después de reconciliar la política. Los derivados se
regeneraron y los 11 contienen la ruta privada y la regla L-1.

| Runtime | Rol | Operación | Resultado |
|---|---|---|---|
| OpenCode 2.0.16 (`--standalone`, agente de proyecto) | cdad-reviewer | `read` de `tests/.sensitive-patterns.local` | `Permission denied: read` |
| OpenCode 2.0.16 (`--standalone`, agente de proyecto) | cdad-test-writer | `read` de `tests/.sensitive-patterns.local` | `Permission denied: read` |
| Guard de Claude Code (invocación directa, rama v2, CLI de la raíz aislada) | test-writer-read / implementer | `Read` de la ruta privada (absoluta) | rc=2, "private project path is denied to every role" |
| ídem | test-writer-read / implementer | `Read` de `tests/test_004_002_t7_w2.py` (control) | rc=0 |

**Limitación observada.** En Claude Code, el guard media solo a los roles que
escriben o leen con alcance (implementer y test-writer). Architect, reviewer y
scribe no tienen guard, así que para ellos la ruta privada queda cubierta por
la instrucción y la auditoría. En OpenCode sí se deniega a todos los roles.
La sonda de OpenCode también cierra la falta de re-sonda tras el fix F-P1 que
señaló el review-014 (F-SET-2).
