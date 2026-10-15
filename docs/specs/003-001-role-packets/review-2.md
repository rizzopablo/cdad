# Re-review — 003-001-role-packets

Reviewer model: `GPT-6 (Codex)`; familia distinta de los implementadores `gpt-5.6-sol` declarados en `reviewfix-green.md`.

Veredicto final: **CHANGES_REQUESTED**.

## Alcance y evidencia

- HEAD revisado: `d31c915`; producto: `bea0338`. El único cambio posterior al producto es el handoff documental en `docs/epics/epic-003-context-efficiency/handoff.md`.
- Se inspeccionaron el handoff, spec, review original, RED/GREEN de review, tests y el diff completo de corrección `e6a007a..bea0338`, además del código resultante.
- Se reutilizó la evidencia de `docs/specs/003-001-role-packets/reviewfix-green.md:20-35`: `Ran 33 tests in 136.283s` / `OK`. No se repitió la suite porque `git diff --stat bea0338..d31c915` sólo contiene documentación.
- Se ejecutó un único probe focal, read-only (`--dry-run`), ante una duda material sobre el alcance del guard de solapamiento.
- Separación TDD preservada: `e6a007a` introdujo los ocho tests RED; `bea0338` no modificó `tests/**`. Los tres informes de implementer registran archivos disjuntos (`cdad_packet.py`, `install.sh`, cinco agentes receptores).

## Cierre explícito de los ocho bloqueantes originales

| # | Estado | Evidencia de conducta y código |
|---|---|---|
| 1. Agentes packet/legacy | **CERRADO** | Los cinco receptores seleccionan exactamente una ruta: paquete canónico validado sin recarga de skills completos, o legacy con las cargas anteriores; un paquete declarado pero inválido se detiene. Código: `agents/cdad-architect.md:62-67`, `agents/cdad-test-writer.md:119-124`, `agents/cdad-implementer.md:91-96`, `agents/cdad-reviewer.md:69-74`, `agents/cdad-scribe.md:68-73`. Conducta: regresión 1 verde dentro de 33/33. |
| 2. ADR-010 limitado al epic | **CERRADO** | `AUTHORIZED_SINGLE_MODEL_EPIC` fija `epic-003-context-efficiency` y `validate_state` rechaza otra identidad antes del resto de bindings. Código: `skills/cdad-cycle/scripts/cdad_packet.py:29-31,216-225`. Conducta: el fixture autoconsistente de otro epic queda rechazado; regresión 2 verde. |
| 3. Symlink interno | **CERRADO** | `_project_path` devuelve el destino resuelto; clasificación, roots exactos y containment comparan `Path` resueltos. Código: `skills/cdad-cycle/scripts/cdad_packet.py:77-99,120-148,272-330`. Conducta: relabels `docs -> src` y `tests -> src` quedan rechazados; regresión 3 verde. |
| 4. Solapamiento/manifest uninstall | **PARCIAL — BLOQUEANTE** | El trigger exacto `CDAD_INSTALL_ROOT=<repo>` queda rechazado y confirmación, ejecución y resumen de uninstall consumen `uninstall_items`. Sin embargo, los destinos extra que el mismo manifest elimina no pasan por `guard_source_overlap`; la misma clase de borrado del source sigue disponible. Ver hallazgo 1. |
| 5. Default cwd | **CERRADO** | `--project-root` queda en `None` al omitirse y `main` usa `Path.cwd().resolve()`; un valor explícito conserva validación absoluta. Código: `skills/cdad-cycle/scripts/cdad_packet.py:492-515`. Conducta: `validate-state` desde el fixture sin flag pasa; regresión 5 verde. |
| 6. CRLF / igualdad de bytes | **CERRADO** | `render` escribe UTF-8 binario y `validate-packet` compara `read_bytes()` con los bytes canónicos. Código: `skills/cdad-cycle/scripts/cdad_packet.py:265-269,527-534`. Conducta: la variante CRLF se rechaza; regresión 6 verde. |
| 7. Métrica sin active_packet | **CERRADO** | Toda métrica valida pareja rol/subfase, exige `active_packet`, valida su forma y liga `packet_id/role/substage`. Código: `skills/cdad-cycle/scripts/cdad_packet.py:437-457`. Conducta: identidad inventada con `active_packet=null` se rechaza; regresión 7 verde. |
| 8. Raíz explícita sin HOME | **CERRADO** | `guard_install_root` sólo llama `guard_home` cuando no existe `CDAD_INSTALL_ROOT`; la raíz explícita se valida y canonicaliza primero. Código: `install.sh:385-461`. Conducta: dry-run aislado sin `HOME` pasa; regresión 8 verde. |

## Bloqueantes

### 1. El manifest de uninstall puede borrar los skills fuente mediante `CDAD_SKILL_EXTRA_DIRS`

Veredicto: **BLOQUEANTE**  
Bucket: **h**  
Severidad: **Critical — riesgo destructivo verificable**  
Problema: `guard_source_overlap` canonicaliza y comprueba sólo los ocho destinos derivados de `INSTALL_ROOT`. `extra_skills_dirs` se incorpora después a `uninstall_items`, y `uninstall_cdad` ejecuta cada entrada con `rm -rf`. Por eso una raíz principal segura no protege un destino extra que coincide con `SOURCE_SKILLS_DIR` o que resuelve por symlink hacia él. Esto conserva la causa de seguridad del bloqueante original 4 y contradice su remediación requerida: rechazar cualquier solapamiento entre destinos gestionados y el source antes de publicar o ejecutar acciones.

Ubicación: `install.sh:211-226`, `install.sh:424-442`, `install.sh:688-718`, `install.sh:743-749`; requisito de remediación en `docs/specs/003-001-role-packets/review.md:61-68`; superficie pública en `docs/specs/003-001-role-packets/spec.md:241-247`.

Evidencia focal, una sola invocación:

```text
CDAD_INSTALL_ROOT=/tmp \
CDAD_SKILL_EXTRA_DIRS=<repo>/skills \
bash install.sh --uninstall --force --dry-run

DRY-RUN UNINSTALL <repo>/skills/cdad-cycle
...
DRY-RUN UNINSTALL <repo>/skills/odoo-expert
Would remove 75 managed item(s)
```

El comando devuelve `0` y publica acciones contra el source. Sin `--dry-run`, las mismas entradas llegan a `rm -rf`.

Sugerencia: incorporar todos los directorios extra canonicalizados al mismo conjunto que valida `guard_source_overlap`, exigir que sean absolutos/directorios válidos, y hacer que guard, install, check y uninstall consuman una única enumeración de destinos. Ampliar la regresión 4 con extra igual a source y extra symlink a source, exigiendo rechazo antes de cualquier línea `DRY-RUN`.

## Opcionales retenidos

### 2. Schemas públicos más permisivos que la CLI

Veredicto: **OPCIONAL**  
Bucket: **h**  
Problema: sigue vigente el hallazgo original; el diff correctivo no toca schemas y la CLI continúa siendo la autoridad estricta. No bloquea este gate.
Ubicación: `skills/cdad-cycle/assets/execution-context.schema.json:32`, `skills/cdad-cycle/assets/packet-request.schema.json:12-21`, `skills/cdad-cycle/assets/rendered-packet.schema.json:12-18`; review original `docs/specs/003-001-role-packets/review.md:148-155`.

### 3. Versión mínima de Python no publicada

Veredicto: **OPCIONAL**  
Bucket: **h**  
Problema: sigue vigente el hallazgo original y queda fuera del gate inmediato, según el handoff.
Ubicación: `README.md:3-7`, `install.sh:464-467`, `skills/cdad-cycle/scripts/cdad_packet.py:4-7,479-486`; review original `docs/specs/003-001-role-packets/review.md:157-164`.

## Abstenciones

### 4. E2E con runtime OpenCode real

Veredicto: **ABSTENER**  
Bucket: **h**  
Motivo: la spec y el handoff difieren explícitamente la interceptación/runtime E2E a integración posterior. No se usa esta ausencia para aprobar ni bloquear el resto.
Ubicación: `docs/specs/003-001-role-packets/spec.md:286-292,649-651`; `docs/epics/epic-003-context-efficiency/handoff.md:165-172`.

## Resultado por eje

- **Correctness:** los cierres 1-3 y 5-8 implementan la conducta pedida y están cubiertos por la evidencia 33/33. El cierre 4 es incompleto para un destino que el propio manifest considera gestionado.
- **Readability:** los helpers nuevos son legibles, pero existen dos fuentes de destinos: el array privado de `guard_source_overlap` y `uninstall_items`. Esa duplicación causó la omisión comprobada.
- **Architecture:** la ejecución/confirmación/resumen de uninstall ya comparten manifest; el guard todavía no consume esa fuente ni una fuente común equivalente.
- **Security:** bloqueado por el vector destructivo de `CDAD_SKILL_EXTRA_DIRS` hacia el repositorio fuente.
- **Performance:** no se observan regresiones materiales; la resolución de pocos destinos y paths locales es acotada.

Resumen: **1 bloqueante, 2 opcionales, 1 abstención. CHANGES_REQUESTED.**
