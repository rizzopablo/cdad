<!-- materializado desde .cdad/runtime/results/exec-007-001-unambiguous-entry-001/007-001-unambiguous-entry-architect-discovery-001/parts (sesión ses_65324cdc…, cdad-architect, gpt-6.1-sol), recibo VALID -->
## Discovery — 007-001

**Contrato validado:** SHA-256 del `UNIT-CONTRACT.md`, plan y política coinciden con sus referencias. No presupongo una spec de feature aprobada.

### Superficie técnica verificada

| Superficie | Hallazgo |
|---|---|
| `skills/cdad-cycle/scripts/cdad_packet.py:6709-6751` | `entry=continuity-reconcile` agrupa despacho pendiente, paquete preparado y ejecución para retomar. `next.route` los distingue mediante prosa, sin identificar sistemáticamente el script. |
| `…/cdad_packet.py:6837-6849` | `authority.approval` muestra referencia de autoridad y digest del paquete, **no el registro verificable de aprobación vigente**. |
| `…/cdad_packet.py:1772-1904` | Ya existen selectores y validación de autoridad: mandato del architect desde `epic_history`; aprobación de spec desde `stage_history`, excluyendo registros sustituidos y comprobando ruta/digest. No corresponde crear otra autoridad. |
| `…/cdad_packet.py:6643-6658` | La ejecución histórica ya se distingue de la activa. Conservarlo. |
| `…/cdad_packet.py:6767-6891` | La vista es una proyección acotada, con diagnóstico al superar el límite. Ampliarla no debe volcar el historial. |
| `sources/roles/orchestrator.md:28-48,137-176` | El cuerpo contiene el árbol de entrada y verbos operativos, pero el mapeo verbo→script es parcial. Debe alinearse con la vista sin duplicar interfaces completas. |
| `scripts/cdad_packet.py` | Es un wrapper; la implementación canónica es la instalada dentro del skill. |
| `skills/cdad-cycle/references/orientation.md:14-38,65-74` | Ya hay propietario de orientación y tabla de operaciones. Conviene ampliar por referencias, no construir otra fachada. |

Los hallazgos corresponden a AC-7.2, .5 y .7 (`docs/epics/epic-006-opencode-concurrency/closure.md:39-44`).

### Decisiones que requieren consulta antes del draft

Hay una discrepancia de procedimiento: el paquete declara **`architect/discovery`**, pero el objetivo pide además un **spec draft**. Mi contrato de rol exige preguntar primero y no redactar la spec durante el brainstorm.

Propongo resolver estas dos decisiones:

1. **Compatibilidad de la vista.** Recomiendo conservar `entry` y los campos actuales, añadiendo una situación inequívoca y una operación estructurada con script y referencia de procedimiento. Alternativa: reemplazar los valores de `entry`. Prefiero la ampliación porque existen consumidores y pruebas que fijan esos valores (`tests/test_005_011_t3_view_action.py:470-510`).  
   **¿Confirmas esa evolución aditiva como interfaz estable para 002-004?**

2. **Referencia de aprobación.** Recomiendo proyectar el registro aplicable según rol/objeto, con localizador verificable y resultado de comprobación; distinguir aprobación vigente, ausente, sustituida o contrato cambiado, sin convertir la vista en un nuevo gate. Para el architect, mostrar el mandato del epic, no una supuesta spec aprobada.  
   **¿Confirmas ese alcance, incluyendo el caso `draft-plan`, que actualmente no exige aprobación (`cdad_packet.py:1850-1855`)?**

**VERIFY pendiente:** fijar con estas respuestas los nombres y valores exactos de los campos y el tratamiento de situaciones que producirán 002-004. No presento interfaces propuestas como existentes.

## Evidencia de ejecución

- **Archivos modificados por mí:** ninguno.
- **Estado inicial y final:** `git status --short` devolvió ` M docs/.cdad-state.json`; cambio preexistente, no intervenido.
- **Commit observado:** `git rev-parse HEAD` → `afee23fc47f8028ab2ec423f7fbf497572fd8622`.
- **Comprobaciones exactas:** `sha256sum` sobre contrato, plan y política; `git status --short`; `git rev-parse HEAD`; lecturas mediante `cat`, `nl -ba … | sed -n …` y búsquedas acotadas con `rg -n`. Comandos completos y salidas quedan en las llamadas de esta sesión.
- **Tests:** no ejecutados; no se solicitó suite para este discovery.
- **Commit creado:** ninguno.

Queda pendiente el draft, tras responder la consulta y autorizar el paso a especificación.
## Decisiones del orquestador (HITL delegada, 2026-10-23)

1. **Evolución aditiva: confirmada.** Se conservan `entry` y los campos actuales; se agregan una situación inequívoca y una operación estructurada (script + referencia de procedimiento). Es la interfaz estable que consumen 002-004.
2. **Referencia de aprobación: confirmada** con el alcance propuesto: proyectar el registro aplicable según rol/objeto con localizador verificable y resultado de comprobación (vigente / ausente / sustituida / contrato cambiado), sin convertir la vista en gate. Para el architect, el mandato del epic. En `draft-plan` la vista declara que no se exige aprobación (borrador), sin inventarla.

Se autoriza el paso a especificación.
