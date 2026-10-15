# Review T1 (004-002) — Codex gpt-6-astra, 2026-09-30

> Materializado por el orquestador, verbatim salvo rutas del worktree. Sesión `01a0f09f-97cc-7342-9025-f75852cfdead`. Primer intento falló por límite de uso de Codex; reintento tras el reset (01:43).

**Dictamen: changes-required.** El delta pasa las 42 pruebas focales con staging generado, pero las sondas reproducen defectos fuera de su cobertura.

Revisé `84adc55..49d2ebf`. El SHA-256 de la spec coincide con el contrato. No modifiqué archivos del repositorio ni hice commits; `git status --porcelain` quedó vacío.

## Hallazgos BLOCKING

**B1 — Los conflictos omiten los tests co-ubicados. Severidad: Required.**

- **Verdict:** BLOCKING
- **Bucket:** h
- **Rationale:** ambos validadores de solapamientos omiten `colocated_test_roots` y sus convenciones. Una política con documentación en `pkg` y tests co-ubicados `pkg/test_*.py` valida con rc=0. Con esos mismos tests y `temporary_roots=["pkg"]`, también valida y clasifica `pkg/test_a.py` como `temporary`. Se aceptan asignaciones incompatibles y producto como temporal.
- **Provenance:** `skills/cdad-cycle/scripts/cdad_packet.py:201` y `:235`; PD-2 y PD-9.

**Remedio:** comprobar intersecciones incluyendo las convenciones co-ubicadas, conservando la distinción entre raíz, archivo exacto y selección por nombre. Agregar ambos negativos.

**B2 — La política enlazada fuera del proyecto valida, pero no permite clasificar. Severidad: Required.**

- **Verdict:** BLOCKING
- **Bucket:** h
- **Rationale:** `validate-policy` abre directamente la ruta de política, sin comprobar su resolución. Con `docs/cdad-policy.json` como symlink hacia un JSON externo válido:
  - Sin `--classify`: rc=0, `VALID: policy docs/cdad-policy.json`.
  - Con `--classify tests/test_a.py`: rc=2, `ERROR: policy path escapes project root: 'docs/cdad-policy.json'`.

  El mismo documento se declara válido o inválido según se solicite clasificación.
- **Provenance:** `skills/cdad-cycle/scripts/cdad_packet.py:823`, frente a `:182`; PD-1, PD-2 e I1.

**Remedio:** resolver y comprobar la ubicación de la política antes de cargarla, independientemente de `--classify`.

**B3 — La propuesta ignora opciones incompatibles. Severidad: Required.**

- **Verdict:** BLOCKING
- **Bucket:** h
- **Rationale:** `prepare --propose-policy --role reviewer --objective x` devuelve rc=0 y una propuesta; ignora las opciones de preparación ordinaria. El contrato exige diagnóstico y rc≠0 ante opciones incompatibles.
- **Provenance:** `skills/cdad-cycle/scripts/cdad_packet.py:831`; spec §2, exclusividad de modos.

**Remedio:** validar las combinaciones antes de ejecutar el modo elegido y probar que la mezcla falla sin escrituras.

## Hallazgos OPTIONAL

**O1 — La propuesta tiene cobertura limitada de layouts.**

- **Verdict:** OPTIONAL
- **Bucket:** h
- **Rationale:** sobre Odoo propone `implementation_roots=["addons"]`, sin tests: `addons/m1/tests/test_a.py` queda como `implementation`. Sobre `mypkg/{mod.py,mod_test.py}` propone listas vacías y ambos quedan `unclassified`. Además, un `src` enlazado fuera produce una propuesta rc=0 que luego falla en `validate-policy`. La determinación de layouts debería ampliar su cobertura y validar la propuesta antes de emitirla.
- **Provenance:** `skills/cdad-cycle/scripts/cdad_packet.py:677`; PD-1 y matriz de layouts de T1. No considero obligatorio inferir automáticamente convenciones que el contrato no define.

**O2 — Los validadores pierden la semántica de archivo exacto.**

- **Verdict:** OPTIONAL
- **Bucket:** h
- **Rationale:** mezclan archivos y raíces y comparan ambos por ascendencia. La política abstracta `documentation_files=["pkg"]`, `implementation_roots=["pkg/src"]` falla; también `implementation_files=["pkg"]`, `temporary_roots=["pkg/tmp"]`. El clasificador, en cambio, limita los archivos exactos a igualdad. Conviene preservar esa distinción también al validar; las sondas usan rutas inexistentes, sin afirmar que esos árboles puedan materializarse con `pkg` como archivo regular.
- **Provenance:** `skills/cdad-cycle/scripts/cdad_packet.py:199–207` y `:235–244`; PD-2.

**O3 — El test de temporales vacíos acepta ausencia de respuesta.**

- **Verdict:** OPTIONAL
- **Bucket:** h
- **Rationale:** una mutación que omite la línea de clasificación de `scratch/anything.txt` deja el test verde. `assertNotIn("temporary", classes.values())` acepta un mapa vacío. Debe exigir explícitamente `scratch/anything.txt → unclassified`.
- **Provenance:** `tests/test_004_002_t1_policy.py:491–494`; PD-9 e I1.

**O4 — Acoplamiento nominal y diagnósticos poco precisos.**

- **Verdict:** OPTIONAL
- **Bucket:** h
- **Rationale:** `classify_path_i1` e `I1_CLASS_BY_TOKEN` incorporan un identificador del plan al código permanente. Los validadores duplican enumeraciones de clases —duplicación que contribuye a B1— y el error de documentación no identifica las rutas enfrentadas. Conviene usar nombres del dominio y una representación compartida de reglas.
- **Provenance:** `skills/cdad-cycle/scripts/cdad_packet.py:71`, `:174`, `:198` y `:230`; legibilidad, arquitectura y errores explícitos.

## Evidencia de pruebas y sondas

Ejecuté en el worktree:

```sh
env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_004_002_t1_policy.py tests/test_packet_prepare.py -q -p no:cacheprovider
```

Resultado: **36 passed, 6 failed**. Los seis fallaron en preparación del fixture instalado por:

```text
ERROR: Staging manifest missing: …/build/staging/manifest.json
```

Después exporté **`49d2ebf`** a `/tmp/review-t1-staging-y6vwrvu2`, ejecuté `make staging` y repetí exclusivamente las dos suites focales, con `TMPDIR` eliminado y cachés desactivadas:

```text
make staging: rc=0
42 passed in 39.94s
```

No ejecuté la suite completa. `git diff --check 84adc55..49d2ebf` terminó sin salida, rc=0.

Sondas adicionales:

| Caso | Resultado observado |
|---|---|
| Symlink interno `alias → src` | Ambas rutas clasifican el mismo test; rc=0 |
| Documentación mediante alias de raíz de implementación | Rechazo, rc=2 |
| Raíces y archivos con barra final | Se normalizan; clasificación equivalente, rc=0 |
| Mismo archivo exacto declarado test e implementación | Clase `test`; su descendiente queda `unclassified` |
| `src/../lib` | Rechazo explícito, rc=2 |
| Convención `../test_` | Aceptada, pero no coincide con el nombre consultado |

Las sondas principales y el procedimiento de copia están en [review_t1_probes.py](/tmp/review_t1_probes.py) y [review_t1_copycheck.py](/tmp/review_t1_copycheck.py). Comandos ejecutados:

```sh
env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 /tmp/review_t1_probes.py
env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 /tmp/review_t1_copycheck.py
```

## Mutaciones del oráculo

Ejecuté:

```sh
env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 /tmp/review_t1_mutations.py
```

Cada mutación se aplicó a una copia temporal del código; ejecuté los **23 tests de T1** contra ella.

| Garantía alterada | Fallos detectados |
|---|---:|
| Admitir campos extra | 3 |
| Cambiar ubicación de política | 13 |
| Introducir escritura durante propuesta | 2 |
| Romper determinismo | 2 |
| Quitar prioridad de política | 1 |
| Permitir escape por symlink | 1 |
| Omitir conflictos de documentación | 2 |
| Quitar extracción de tests | 4 |
| Quitar clasificación co-ubicada | 1 |
| Conceder clase por nombre fuera de ubicación | 1 |
| Omitir validación de temporales | 3 |
| Conceder temporales con lista vacía | 4 |
| Quitar clasificación temporal | 2 |
| Ignorar archivos exactos de implementación | 1 |

**Las 14 mutaciones fueron detectadas, sin errores de ejecución del test.** La mutación adicional de ausencia de respuesta sobrevivió al test específico, como documenta O3. Estos resultados no cubren los huecos reproducidos en B1–B3.

## Compatibilidad de `prepare`

Comparé el código base y el actual con cero flags obligatorias, solo `--role`, y `--role` más `--substage`.

En todos los casos: **rc=2 y stdout vacío**. Cambió el diagnóstico:

```text
Base: ERROR: cdad_packet.py prepare: the following arguments are required: --objective
Actual: ERROR: prepare requires --role, --substage and --objective
```

El actual enumera también opciones ya proporcionadas. Con raíz inexistente cambió además la precedencia: antes diagnosticaba flags faltantes; ahora diagnostica `--project-root`. Por tanto, se conserva el rechazo, **no el comportamiento textual exacto**.

## Abstentions

Ninguna sobre los defectos reproducidos de T1. No atribuyo a este delta cumplimiento de scopes v2, publicación o activación runtime: corresponden a tareas posteriores del plan. Los buckets `h` se sustentan en diff completo, contrato y citas verificables; no presuponen haber corroborado el modelo efectivo del implementer.
## Disposición del orquestador

- **Corregir ahora:** B1, B2 y B3. Se suman O2 (mismo validador que B1), O3
  (test que acepta ausencia de respuesta), O4 (nombres del dominio) y que la
  propuesta se valide a sí misma antes de emitirse (parte de O1).
- **Diferido a T6:** la inferencia de layouts de O1 (tests de Odoo,
  co-ubicados sin raíz). La propuesta es orientativa y el contrato no define
  esa inferencia.
- **Hallazgo lateral para T6 (PD-12):** en un checkout limpio fallan 6 tests
  porque dependen de `build/staging/manifest.json`, que está ignorado por git.
- **Suite completa reproducida por el orquestador** en `49d2ebf`: 155 passed
  (`env -u TMPDIR`, 582 s).

## Re-review (misma sesión Codex, `01a0f09f-97cc-7342-9025-f75852cfdead`)

**Dictamen: changes-required.** B1 y B2 están cerrados; B3 conserva un caso reproducible con valores vacíos. Las **50 pruebas focales pasan** después de generar staging en una copia temporal de `a62ab68`.

## BLOCKING

**B3 residual — Opciones ordinarias explícitas con valor vacío eluden la exclusividad. Severidad: Required.**

- **Verdict:** BLOCKING
- **Bucket:** h
- **Rationale:** el guard usa `any(ordinary)`, que confunde una opción ausente con una opción escalar proporcionada como `""`. Esta invocación devuelve **rc=0, propuesta por stdout y stderr vacío**:

  ```sh
  python3 scripts/cdad_packet.py prepare --project-root /tmp/proyecto \
    --propose-policy --role ""
  ```

  Reproduje lo mismo con `--execution-context`, `--substage`, `--objective`, `--expected-output` y `--out-dir`. Las variantes con valores no vacíos sí fallan con rc=2. No hubo escrituras, pero sigue incumpliéndose el rechazo de combinaciones incompatibles.
- **Provenance:** `skills/cdad-cycle/scripts/cdad_packet.py:874–877`; spec §2 y disposición B3. Los tests de `tests/test_004_002_t1_reviewfix.py:164–166` solo cubren valores no vacíos.

**Remedio:** distinguir presencia de opciones escalares mediante `is not None`, separándolas de las listas; agregar casos con cadena vacía.

## Verificación de las correcciones

| Hallazgo | Evidencia propia | Estado |
|---|---|---|
| B1 | Documentación y temporales sobre tests co-ubicados: rc=2, stdout vacío y diagnóstico con ambas rutas | Cerrado |
| B2 | Política enlazada fuera: mismo rechazo rc=2 con y sin `--classify` | Cerrado |
| B3 | Las 11 opciones ordinarias comprobadas se rechazan con valores no vacíos; seis escalares aceptan `""` | Parcial |
| O2 | Los dos casos abstractos originales ahora validan; igualdad de archivos y archivo contenido por raíz incompatible siguen rechazándose | Cerrado |
| O3 | El test nuevo exige `unclassified`; detecta la mutación que suprime la respuesta | Cerrado |
| O4 | Eliminados los nombres ligados a I1; validadores comparten regiones y diagnósticos identifican rutas | Cerrado |
| Propuesta validada | `src` enlazado fuera: rc=2, stdout vacío y error de escape | Cerrado |

También repetí symlinks internos, barras finales, colisión test/implementación en archivo exacto y clasificación de descendientes: mantienen los resultados anteriores. Un archivo documental que no coincide con la convención co-ubicada valida; uno que coincide se rechaza.

La inferencia Odoo/co-ubicada permanece limitada, conforme a su **disposición explícita para T6**. El diagnóstico de `prepare` sin flags obligatorias sigue igual que en `49d2ebf`: rc=2 y stdout vacío.

## Mutaciones

Ejecutadas sobre copias temporales, contra los tests nuevos:

| Mutación | Fallos detectados |
|---|---:|
| Omitir co-ubicados del conflicto documental | 1 |
| Omitir co-ubicados del conflicto temporal | 1 |
| Eliminar resolución segura de la política al cargarla | 1 |
| Eliminar guard de exclusividad | 3 subtests |
| Restaurar comparación por ascendencia para archivos exactos | 2 |
| Suprimir clasificación de `scratch/anything.txt` | 1 |
| Eliminar validación previa de propuesta | 1 |

**Las siete mutaciones fueron detectadas, sin errores de ejecución.** Además, ejecuté los ocho tests nuevos contra una copia de `49d2ebf`: siete métodos fallan —nueve fallos contando subtests— y O3 pasa, como corresponde a una corrección del oráculo.

Comandos reproducibles:

```sh
env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 /tmp/review_t1_probes.py
env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 /tmp/review_t1_recheck.py
env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 /tmp/review_t1_fixmutations.py
```

## Pruebas focales y estado

En el worktree ejecuté:

```sh
env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 -m pytest \
  tests/test_004_002_t1_policy.py \
  tests/test_004_002_t1_reviewfix.py \
  tests/test_packet_prepare.py -q -p no:cacheprovider
```

Resultado: **44 passed, 6 failed**, todos los fallos por ausencia de `build/staging/manifest.json`.

Exporté `a62ab68` a `/tmp/review-t1-staging-yfdx0bhw`, ejecuté `make staging` y repetí las tres suites:

```text
make staging: rc=0
50 passed in 63.30s
```

Procedimiento conservado en [review_t1_fixcopy.py](/tmp/review_t1_fixcopy.py). No ejecuté la suite completa ni utilicé sus resultados reportados como evidencia propia.

El diff de código/tests pasa `git diff --check`; el diff completo señala únicamente whitespace final en `docs/specs/004-002-project-execution-bootstrap/review-t1.md:27`.

**Archivos del repositorio modificados: ninguno. Commits creados: ninguno.** HEAD verificado: `a62ab68ddc123aa716e358f12162fcd6c64fda17`; worktree limpio.

## OPTIONAL

Sin nuevos hallazgos materiales.

## Abstentions

Ninguna en el alcance focal revisado. La inferencia de layouts diferida a T6 no se considera un bloqueo de esta revisión.
**Disposición:** B3 residual con un micro-ciclo RED/GREEN en las mismas sesiones.
