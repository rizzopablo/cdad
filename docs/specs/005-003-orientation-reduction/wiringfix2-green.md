## Reporte del encargo (implementer · GREEN de continuación, 005-003-orientation-reduction)

### 1. Diff exacto

Commit `a13576f` — un solo archivo, `skills/cdad-cycle/references/orientation.md` (1 file changed, 6 insertions, 5 deletions). Sólo se re-envolvió el mismo párrafo (mismas palabras y puntuación) para prefijar los dos CLIs con el marcador:

```diff
diff --git a/skills/cdad-cycle/references/orientation.md b/skills/cdad-cycle/references/orientation.md
index becd5e2..0c60608 100644
--- a/skills/cdad-cycle/references/orientation.md
+++ b/skills/cdad-cycle/references/orientation.md
@@ -66,11 +66,12 @@ to the context; the **complete** evidence stays available **by reference**.
 
 ### Root-relative asymmetry (diagnosed in the view)
 
-`cdad_packet.py` requires an **absolute** `--project-root` and rejects a relative
-one (`ERROR: --project-root must be an absolute existing directory: .`), while
-`cdad_continuity.py resume --project-root .` resolves the relative root against
-the cwd (rc 0). The `status` view **diagnoses** this asymmetry in its output and
-names the recovery path: pass an **absolute** `--project-root`.
+`<skill-dir>/scripts/cdad_packet.py` requires an **absolute** `--project-root`
+and rejects a relative one (`ERROR: --project-root must be an absolute existing
+directory: .`), while `<skill-dir>/scripts/cdad_continuity.py resume
+--project-root .` resolves the relative root against the cwd (rc 0). The
+`status` view **diagnoses** this asymmetry in its output and names the recovery
+path: pass an **absolute** `--project-root`.
 
 ### Dispatch-attempt input (`docs/attempt.json`)
```

Sentido conservado intacto: la **asimetría** (el CLI de paquetes rechaza la raíz relativa; el de continuidad la resuelve contra el cwd, rc 0) y el **camino de recuperación** (pasar `--project-root` absoluto). No se tocó nada más de la sección ni del archivo. Los dos `<skill-dir>/scripts/cdad_*.py` quedan enteros en su línea (el grep de la clase los ve con el marcador en la misma línea).

### 2. Comandos y salidas

```
$ python3 -m pytest tests/test_005_006_t6_owner_reviewfix.py -q
.....                                                                    [100%]
5 passed in 0.06s

$ python3 -m pytest tests/test_005_003_t2_examples_execute.py -q
..........                                                               [100%]
10 passed in 1.81s

$ grep -n "cdad_[a-z_]*\.py" skills/cdad-cycle/references/orientation.md | grep -v "<skill-dir>"
(sin salida; rc=1)   →  VACÍO
```

Las 12 líneas con `cdad_*.py` del archivo quedan todas con `<skill-dir>` (líneas 17, 25, 44, 47, 51, 61, 62, 63, 64, 65, 69, 71). La suite completa **no** se corrió (la corre el orquestador al cierre). No se tocaron tests, HOME, ni se desplegó/pusheó.

### 3. Hash del commit

`a13576f26deba706cb887f542ee4fb5bdf1f9874` — `fix(005-003): completa el marcador <skill-dir> en la referencia operativa`

### 4. Otros ofensores de la clase (declarados)

- **En el conjunto de cableado del oráculo A2** (`sources/roles/orchestrator.md`, `skills/cdad-cycle/SKILL.md`, `references/continuity.md`, `references/project-start.md`, `README.md`, los dos agentes generados) y en `orientation.md`: **cero**. El oráculo A2 queda verde y el grep de la clase en `orientation.md` vacío.
- **Fuera de ese conjunto** (documentos de referencia que **no** están en la lista de cableado de A2, no modificados por este encargo): hay menciones de CLIs con un marcador **distinto** (`<skill>/scripts/...`) o en prosa, p. ej. `references/project-execution.md` (usa `<skill>/scripts/cdad_packet.py`), `references/handoff-prompts.md` y `references/progress-guards.md` (usan `skills/cdad-cycle/scripts/...`), `references/cli-delegation.md`, `references/re-entry.md:19`, `references/opencode-delegation.md:71`, `references/runtime-adoption.md:29`, y descripciones de `assets/*.schema.json`. No pertenecen a la clase tal como la fija el oráculo A2 ni al alcance declarado de este encargo (los dos ofensores de `orientation.md`); quedan **sin tocar** y los declaro por si el orquestador quiere plegarlos a una corrección de la misma familia.

Nota de estado: `docs/.cdad-state.json` ya figuraba modificado por el orquestador antes de este encargo; no lo toqué ni lo incluí en el commit (el commit tiene pathspec acotado a `orientation.md`).