## Discovery 010-000 — diagnóstico confirmado

**El defecto está en comparar una ruta resuelta absoluta contra un `project_root` todavía relativo. No es un escape real.**

Packet validado: REQUEST y PACKET canónicos; comparación íntegra del contenido recibido: **5241 bytes idénticos**, SHA-256 `c00e6e8900eccb40075387e15ef7d7233d07979c21006bdb717a8a79da916e87`.

### 1. Causa y superficie afectada

En `skills/cdad-cycle/scripts/cdad_packet.py:279–293`, `_project_path` ejecuta:

```python
resolved = candidate.resolve(strict=False)
resolved.relative_to(project_root)
```

Si `project_root == Path(".")`, `resolved` es absoluto y la base sigue relativa: `relative_to` falla y se emite un falso «escapes project root».

La entrada CLI de packet **ya normaliza correctamente** la raíz mediante `_absolute_existing_directory` (`:1297–1301`, `:9778–9784`). El problema aparece cuando otra función llama directamente al módulo sin pasar por ese CLI.

| Entrada | Evidencia |
|---|---|
| Continuity CLI `begin` | `_run_write` reconstruye la raíz sin resolver (`cdad_continuity.py:1154–1164`). El control previo de `main` usa otra variable resuelta, pero no la transmite al handler (`:3175–3197`). |
| API `plan_write` | Recibe y propaga la raíz sin normalizar (`:1012–1038`). |
| Admisión de un nuevo `begin` | `_plan_write → _admit_packet → cdad_packet.verify_published_packet` (`:1109–1114`, `:1222–1253`). Esta última conserva la raíz recibida (`cdad_packet.py:1917–1974`). |
| Clasificación programática | `classify_path_observable` también falla con raíz relativa. Además contiene otra conversión `candidate.relative_to(project_root)` (`:407–427`). |

**No todos los comandos están rotos:** en el estado examinado, `verify-begin`, `reconcile`, `resume` y `trigger` produjeron resultados idénticos con raíz relativa y absoluta. `close_durable_receipt`, `continuity_state` y reanchor ya resuelven la raíz (`cdad_continuity.py:1651`, `:1407`, `:2092`).

### 2. Reproducción read-only

Entorno: **Python 3.13.5**.

Las sondas ejecutadas muestran:

```text
_project_path .:
  PolicyError policy path escapes project root: 'docs/cdad-policy.json'

verify_published_packet .:
  PolicyError path_policy.documentation_files escapes project root: 'README.md'

plan_write .:
  ContinuityError the begin is refused:
  path_policy.documentation_files escapes project root: 'README.md'
```

Con raíz absoluta:

```text
_project_path: OK
verify_published_packet: OK
plan_write: OK planned_writes: 2 published: 0
```

`plan_write` calculó un **nuevo begin**, aumentando el intento del cuerpo vigente; no publicó el plan ni modificó la cadena.

También se ejecutó exactamente:

```bash
python3 -B scripts/cdad_packet.py validate-request \
  --project-root <repo> \
  --execution-context .cdad/executions/exec-010-000-continuity-relative-root-001/execution.json \
  --request .cdad/packets/010-000-continuity-relative-root-architect-discovery-002/REQUEST.json
```

Resultado: **rc=0, sin diagnóstico**. La misma validación mediante el CLI instalable pasó con estas combinaciones:

| CWD | `--project-root` | Resultado |
|---|---|---|
| Checkout | `.` | rc=0 |
| Contenedor | `cdad` | rc=0 |
| `skills/` | `..` | rc=0 |
| Checkout | Ruta absoluta | rc=0 |

Los comandos y scripts completos de las sondas, incluyendo argumentos y salidas, quedan registrados en las llamadas de herramientas de esta ejecución.

### 3. Solución mínima recomendada

**Normalizar la raíz antes de operar y conservar los controles de pertenencia.**

- En continuity, establecer una raíz canónica que llegue efectivamente a los handlers; resolverla únicamente en una variable local de `main` no basta.
- Cubrir también el borde programático `plan_write`, que no atraviesa `main`.
- En packet, asegurar que el borde programático de verificación y el guard de rutas comparen candidato y raíz en el mismo espacio canónico.
- Revisar las conversiones asociadas a `relative_to(project_root)`: corregir solo `_project_path` puede dejar fallos posteriores en clasificación o presentación (`cdad_packet.py:420`, `:475`, `:1422`).

**Criterio de diseño:** prefiero una regla general —raíz canónica en los bordes relevantes— frente a excepciones para `"."`, instrucciones de usar siempre rutas absolutas o eliminación del containment. No hace falta crear un nuevo subsistema de rutas ni refactorizar consumidores ajenos a este defecto.

No debe cambiarse indiscriminadamente la semántica de los argumentos: continuity resuelve contexto/update relativos al proyecto (`cdad_continuity.py:232–234`), mientras packet tiene entradas relativas al CWD (`cdad_packet.py:2156–2158`, `:9881–9886`).

### 4. Regresión necesaria

Para Specification posterior, recomiendo comprometer estas promesas observables:

- Un nuevo `begin` válido y su entrada programática funcionan con raíces equivalentes relativas y absolutas.
- El resultado durable conserva identidad, referencias, digests, secuencia y comportamiento de replay; la normalización no introduce rutas absolutas en el cuerpo portable.
- Continúan rechazándose traversal y escapes por symlink, con ausencia de publicaciones ante rechazo.
- El consumidor instalado reproduce el comportamiento del código fuente sin depender del wrapper del checkout.

Las sondas actuales confirmaron rechazo de `../outside`, `docs/../../outside` y una ruta absoluta suministrada como referencia project-relative. **VERIFY:** escapes mediante symlinks y escrituras reales en fixtures aislados; no se ejecutaron aquí.

Fixtures reutilizables verificadas:

- `tests/test_007_003_continuity_at_edges.py:535–575`: preparación de paquetes y nuevos `begin`.
- `tests/test_008_003_lifecycle_decisions.py`: guardas de entradas programáticas, autoridad y replay.
- `tests/test_008_004_packet_enforcement.py`: admisión canónica y protección de contratos.
- `tests/test_role_packet_consumers.py:31–148`: instalación aislada y paridad con consumidor sin wrapper.

### 5. Vía distribuible

La fuente corregible está en **`skills/cdad-cycle/scripts/`**, no en una instalación global. `scripts/cdad_packet.py` es solamente un wrapper (`:1–11`).

La vía existente es:

1. Generar staging con `make staging` (`Makefile:10–13`).
2. Instalar bajo una raíz aislada mediante `CDAD_INSTALL_ROOT`, con `CDAD_SKILL_EXTRA_DIRS` vacío.
3. Comprobar instalación y ejecutar los CLI instalados contra un proyecto consumidor sintético.
4. Comparar comportamiento con la fuente.

El instalador copia el árbol completo del skill, incluidos sus scripts (`install.sh:1261–1285`). Por tanto, **generar agentes no sustituye verificar los scripts instalados**.

**Pendiente de ejecución autorizada:** generación, instalación aislada, regresiones de escritura y revisión independiente. No se realizaron en este Discovery.

### Evidencia de cierre

```bash
git diff --exit-code
git diff --cached --exit-code
git status --porcelain=v1
git rev-parse HEAD
```

Resultados: ambos diffs y status sin salida; HEAD:

```text
b109abf0df7895ea66d18b1927737a25cd96e491
```

**Archivos modificados: ninguno. Commit creado: ninguno.** Sin spec, implementación, instalación global, publicación ni ejecución de la suite completa.
