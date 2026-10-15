# Review — 005-011-common-entry (etapa 4, T1..T3)

**Rol:** reviewer · **Paquete:** `005-011-common-entry-reviewer-review-001` · **Fecha:** 2026-10-13
**Contrato:** `docs/specs/005-011-common-entry/spec.md` — sha256 verificado con mi propia ejecución:

```
$ sha256sum docs/specs/005-011-common-entry/spec.md
37cd45931ad7a4c6d28e5491556d81c283b2aa7b346c6a53b3852b6ac5c610bc
```

Coincide con el del paquete. Plan verificado: `edcee01503c…fbbf833`. Alcance: diff de producto de
T1..T3 contra PD-1..PD-6 y AC-1..AC-5; T4 (AC-6/AC-7/AC-8) fuera de esta review. Sesión propia de
review; este informe se escribe fuera del repo en `<transport>/005-011-review-report.md`; el árbol
compartido quedó intacto (solo `git worktree add/remove` con `--force` del worktree propio; nunca
`git stash`).

## Evidencia base (comandos y salida, primera persona)

Commits encadenados T1..T3 — `git log --oneline`/`git show --stat`:

```
00dd36e test(005-011): T1 RED — 3 archivos, todos en tests/            (00dd36e…61ee)
61d100e docs: RED de T1 registrado                                     (padre del GREEN)
53413b3 feat: T1 GREEN — cdad_packet.py(−30 líneas: C4 retirado), orientation.md, project-execution.md
6dcf0f3 docs: GREEN de T1 con bloqueo parcial declarado
4ea82ea test: T1 testfix del oráculo PD-2 — SOLO tests/test_005_011_t1_relative_root.py
4713882 docs · 13c68b9 feat: T2 GREEN — SOLO skills/cdad-cycle/SKILL.md + skills/cdad-epic/SKILL.md
c9040bf docs · 1c207d9 test(005-011): T3 RED — SOLO tests/test_005_011_t3_view_action.py
c4f8adb docs · 860a611 feat: T3 GREEN — cdad_packet.py + orientation.md
```

`(b) ningún GREEN tocó tests/`: `git show --name-only` de 53413b3, 13c68b9 y 860a611 no lista ningún
archivo bajo `tests/` (salida arriba). ✔

`(b) focales sin relajar tras el RED`:

```
$ git diff 00dd36e HEAD -- tests/test_005_011_t1_relative_root.py   → solo el testfix autorizado 4ea82ea
$ git diff 4ea82ea HEAD -- tests/test_005_011_t1_relative_root.py   → vacío
$ git diff 1c207d9 HEAD -- tests/test_005_011_t3_view_action.py     → vacío
$ git diff 00dd36e HEAD -- tests/test_005_003_t1_compact_view.py tests/test_005_003_t2_examples_execute.py
  → vacío
```

El testfix (4ea82ea) no debilita: agrega setup (`fx.prepare()` con aserción de éxito), un control más
estricto (`validate-state` raíz absoluta debe dar rc=0) y cambia la aserción a la equivalencia
EQUIVALENTE `rc(relativo) == rc(absoluto)` que no acepta el fallo por binding; `validate-policy`
conservado tal cual. No hay aserción eliminada.

### Corridas de verificación (primera persona)

```
$ python3 -m pytest tests/test_005_011_t1_relative_root.py -q        → 5 passed
$ python3 -m pytest tests/test_005_011_t3_view_action.py -q          → 5 passed
$ python3 -m pytest tests/test_005_003_t1_compact_view.py tests/test_005_003_t2_examples_execute.py -q
                                                                     → 21 passed
$ python3 -m pytest tests/test_005_001_t3_idle.py -q                 → 4 passed
$ python3 -m pytest tests/test_005_006_t1_start_procedure.py tests/test_005_006_t6_owner_reviewfix.py \
    tests/test_005_010_t3_references.py tests/test_005_010_reviewfix.py \
    tests/test_005_009_t3_spawn_reconciliation.py tests/test_005_005_t2_docs_policy.py -q
                                                                     → 61 passed
```

### Falsificación del testfix corregido contra el CLI pre-fix (worktree, ítem 1 de los insumos)

```
$ git worktree add --detach /tmp/opencode/wt-review-t1prefix 61d100e
$ cp tests/test_005_011_t1_relative_root.py tests/test_005_003_t1_compact_view.py <worktree>/tests/
$ python3 -m pytest tests/test_005_011_t1_relative_root.py -q -k relative_root_consistent
E   AssertionError: PD-2 violada: `validate-state --project-root .` debe resolver la raíz relativa
    contra el cwd y dar el MISMO veredicto que la raíz absoluta; hoy rc=2 != 0;
    stderr='ERROR: --project-root must be an absolute existing directory: .'
1 failed, 4 deselected in 0.72s
$ python3 -m pytest tests/test_005_003_t1_compact_view.py -q -k relative_root_accepted
E   AssertionError: PD-1 violada: la vista `status` debe emitir la proyección (rc=0); hoy rc=2 …
1 failed, 10 deselected in 0.30s
$ git worktree remove --force /tmp/opencode/wt-review-t1prefix
```

En HEAD ambos pasan (5/5 y 21/21 arriba). El oráculo corregido **discrimina el comportamiento**: falla
pre-fix por el motivo correcto (rechazo de raíz relativa, no por binding ni setup) y pasa con el
producto. Y el rechazo de `validate-state` por binding ausente está fijado por el oráculo verde
preexistente `tests/test_005_001_t3_idle.py` (4 passed en primera persona).

## (c) Los dos oráculos declarados de PD-3 corresponden al comportamiento NUEVO

- **C4 reemplazado** (`tests/test_005_003_t1_compact_view.py`, `test_pd5_relative_root_accepted_projects_view`):
  el diff de 00dd36e sustituye `test_pd5_relative_root_asymmetry_diagnosed_in_view` (afirmaba rc≠0 +
  diagnóstico) por: `status --project-root .` → rc=0 con proyección y `entry` del mapa declarado. El
  docstring declara la autoridad (fila 11, 005-011 PD-3). Verifiqué que discrimina: falla sobre el CLI
  pre-fix (salida arriba) y pasa en HEAD.
- **Fixture de PD-5** (`tests/test_005_003_t2_examples_execute.py:545+`): el diff cambia SOLO la
  invocación que falla (`--project-root .` → raíz inexistente) y la aserción de recuperación
  (`absolut` → `existing directory`); el oráculo de captura del rc se conserva íntegro — rc real del
  CLI sin enmascarar ≠ 0, patrón `PIPESTATUS`/`RC_PIPE`/`RC_REAL`, formato `ERROR: …`, prohibiciones
  de atajo, sin máscara del rc. Verde en HEAD (10/10 del archivo).

## (d) Textos corregidos de verdad; sin segunda copia ni afirmación vieja predominantemente

- `orientation.md` §3: la sección «Root-relative asymmetry (diagnosed in the view)» fue reescrita
  (diff de 53413b3) a «Project root resolution» con referencia a `project-execution.md` §1; la
  historización («the former root-relative asymmetry … is gone») no es una afirmación vieja.
- `project-execution.md:49` ya no dice «must be an absolute existing directory»; dice «resolved
  against the current working directory and must be an existing directory».
- Sin documento nuevo y sin segunda copia de la regla de la vista: `git show --name-only` de los tres
  GREEN no crea archivo; la regla «view first» la poseen `orientation.md` §1 y `project-start.md` §11,
  y los Step 1/tablas la **citan con sus dueños** (verifico por lectura, no por lista de palabras).
- INV-1 (read-only) sigue cobertizada por el oráculo preexistente
  `test_inv1_status_is_read_only_state_byte_identical` (incluido en los 21 passed).
- **EXCEPTO la hallada abajo (OP-1)**: quedó una afirmación vieja (una sola, hallada con grep) fuera
  de los dos sitios de corrección declarados.

## (e) Guardas de texto de los otros references/skills

`test_005_006_t1_start_procedure`, `test_005_006_t6_owner_reviewfix`, `test_005_010_t3_references`,
`test_005_010_reviewfix`, `test_005_009_t3_spawn_reconciliation` (INV-8), `test_005_005_t2_docs_policy`:
**61 passed** en primera persona (comando arriba).

## (f) Anonimización de los documentos versionados de la feature

```
$ grep -rn -E "/home/[a-z]+|/root/|ofap|ses-[a-zA-Z0-9]{6,}|<ip>" docs/specs/005-011-common-entry/
→ sin coincidencias (salvo magnitudes ya publicadas: 304.054, 105 mil)
$ grep -rn -E "/home/|/tmp/opencode|ofap|51\.83" skills/cdad-cycle/SKILL.md skills/cdad-epic/SKILL.md \
    skills/cdad-cycle/references/orientation.md skills/cdad-cycle/references/project-execution.md \
    skills/cdad-cycle/scripts/cdad_packet.py
→ sin coincidencias
```

## (a) PD/AC del alcance: cobertura

| PD/AC | Verificación | Primera persona |
|---|---|---|
| PD-1 / AC-1 | T2: observable_checks + guardas verdes + review por sentido (Step 1 de las dos skills leyendo el diff de 13c68b9: la primera acción prescripta es la vista, con dueños citados; `state-detection.md` a ampliación condicional con gatillo y motivo en las dos tablas; fila `orientation.md` nueva en la tabla de `cdad-cycle`; `resume` y la fila `project-start.md` intactas) | guardas 61 passed; lectura hecha |
| PD-2 / AC-2 | Focal T1 5/5 (subproceso, caja negra): proyección con raíz relativa, equivalencia de subcomandos, raíz inexistente falla cerrado nombrando `existing directory` sin proyección parcial, cwd sin bandera, otras validaciones sin cambio (salida idéntica relativa vs absoluta) | 5 passed |
| PD-3 / AC-3 | Los dos oráculos declarados actualizados y verificados como nuevo comportamiento | 21 passed + falsificación pre-fix |
| PD-4 / AC-4 | Focal T3 pata que diverge leída (token por estructura excluyendo `verdict`), resolución sólo con `["project"]`, ausencia sin resolución y con forma distinta | 5 passed |
| PD-5 / AC-5 | Focal T3 ruta de `prepared` nombra el despacho con `--replace-packet` condicional, `entry` intacto, `dispatched` conserva su ruta y difiere | 5 passed |
| PD-6 | Sin documento nuevo; extensiones aditivas (`verdict`/`verified`/`cause` conservados; `divergent_legs`/`resolution` nuevos); `entry` sin cambio | diff leído + focales |

Ningún focal depende de estructura interna ni de mocks sobre plumbing: los dos focales operan el CLI
como subproceso (caja negra) sobre fixtures sintéticos en tempdirs con HOME aislado; el caso de versión
copia el árbol `skills/` a un tempdir e invoca el CLI copiado (nunca el repo); las aserciones de T3 son
estructurales sobre la salida JSON (INV-5: el sentido lo juzga la review — lo hago abajo).

---

# BLOQUEANTES

**Ninguno.** El diff de producto implementa lo declarado por el contrato; focales rojo→verde
verificados, oráculos autorizados declarados y discriminantes, textos corregidos salvo un resto
(OP-1), guardas verdes.

# OPCIONALES (deuda con condición de cierre; criterio vigente 2026-10-12)

**OP-1 — Afirmación vieja remanente: `orientation.md:69` (tabla de operaciones, fila `open-unit`).**
- **Ubicación:** `skills/cdad-cycle/references/orientation.md:69`, columna de notas de la fila
  «Open the next unit»: «absolute `--project-root`».
- **Problema (medido):** bajo la resolución unificada (commit `53413b3`), TODOS los subcomandos
  aceptan la raíz relativa; `-i` `open-unit` pasa por la misma rama de `main` (diff leído). La fila
  quedó fuera del alcance de corrección declarado por la spec (`§2.2` nombraba `orientation.md:68-75`
  = el §3 de asimetría, y `project-execution.md:49`) y sigue afirmando el rechazo que se retiró.
- **Consecuencia:** el documento canónico de orientación contradice el comportamiento nuevo y sigue
  enviando al coordinador a montar rutas absolutas innecesarias; es exactamente el género de
  «afirmación vieja» que el encargo manda verificar al cierre (d).
- **Verdict: OPTIONAL · Severidad: Required · Bucket: m** (información declarada del producto;
  no rompe el uso previsto porque la lectura es conservadora). Procedencia: **leído** (grep propio con
  salida; diff del GREEN).
- **Condición de cierre verificable:** quitar «absolute» de la fila (o referenciar la regla única de
  `project-execution.md` §1, como hizo el §3) y verificar con
  `grep -rn -iE "absolute.{0,20}--project-root" skills/**/*.md` → sin restos de la afirmación vieja,
  con las guardas de texto en verde.

**OP-2 — Compiten los dos «first» en el Step 1 de `cdad-cycle` (`SKILL.md:251`).**
- **Ubicación:** el párrafo del Step 1 tiene dos «**first**»: «Consult **first** the read-only compact
  view …» y «When you start a new session, rebuild the carried context **first** with `resume`».
- **Problema:** sí compiten léxicamente: la segunda frase se auto-describe con la situación exacta
  de un coordinador nuevo («When you start a new session») y alega «first», con el mismo adverbio que
  la primera acción prescripta de la fila 11. Un coordinador nuevo podría leer `resume` como lo
  primero.
- **Consecuencia (acotada, verificada):** si ganara ese «first», la primera acción no sería la vista y
  AC-6/AC-7 medirían el incumplimiento en T4. Pero el daño queda acotado por tres backstops: (i) la
  guarda inmediata «**without an active execution, do not run `resume`**» y su ventana del 005-006;
  (ii) backstop mecánico — `resume` exige `--execution-context` requerida
  (`skills/cdad-cycle/scripts/cdad_continuity.py:1320-1321`, `required=True`), así que un «resume
  primero» a ciegas falla cerrado en argparse (rc≠0) y fuerza a consultar la vista; (iii) la
  aceptación real lo mide en T4 antes de cerrar. Por eso NO bloquea el resultado bajo el criterio
  vigente, pero es deuda del texto del producto de PD-1.
- **Verdict: OPTIONAL · Severidad: Required · Bucket: m** (prosa vigilada del Step 1, producto
  principal de PD-1; no compromete el resultado por los backstops). Procedencia: **leído** (texto
  vigente y sinopsis del CLI con línea citada).
- **Condición de cierre verificable:** reescribir la cláusula de `resume` sin el segundo «first» p.
  ej. «if the view shows an active execution, rebuild the carried context with `resume`; without one,
  do not run `resume`» — conservando la negación literal que fijan las guardas del 005-006
  (`tests/test_005_006_t1_start_procedure.py:535-569`) — y verificar que la guarda queda verde y que
  queda un único «first» asociado a la vista en el Step 1.

**OP-3 — `cdad-epic` Step 1 nombra `cdad_packet.py` SIN RUTA (`skills/cdad-epic/SKILL.md:58`).**
- **Juicio:** la ruta SÍ es alcanzable sin explorar: el Step 1 atribuye expresamente al dueño
  («the `cdad-cycle` reference `references/orientation.md` §1») y la §1 de esa referencia trae la
  invocación literal (`python3 "<skill-dir>/scripts/cdad_packet.py" status --project-root ROOT`,
  `orientation.md:25-35`); leer una referencia prescripta no es explorar versiones/manifiestos/código.
  La apelación al skill dueño desambigua `<skill-dir>`. Declara: **ALCANZA** para la fila 11.
- **Verdict: OPTIONAL · Severidad: Nit · Bucket: l.** Procedencia: **leído** (texto actual de ambos
  archivos con líneas citadas).
- **Condición de cierre (opcional):** por simetría y robustez, incluir la invocación o `<skill-dir>`
  explícitos también en el Step 1 del epic (p. ej. «`<cdad-cycle-skill-dir>/scripts/cdad_packet.py
  status`»), sin tocar las guardas de cableado existentes.

**OP-4 — Cobertura focal de PD-2: subcomandos no sondados.**
- **Ubicación:** `tests/test_005_011_t1_relative_root.py` (testfix 4ea82ea, HEAD).
- **Problema:** la spec §2.2/PD-2 enuncia «todos» los subcomandos (`status`, `validate-state`,
  `validate-policy`, `render`, `validate-request`, `validate-packet`, `prepare`, `open-unit`,
  `validate-metric`); el focal sondea 5 (los 4 validadores + estado/paquete) y el de raíz inexistente
  sondea 3. `render`, `open-unit`, `validate-metric` y `prepare` con raíz **relativa** no tienen
  aserción directa (prepare corre con raíz absoluta en los fixtures), aunque todos van por la misma
  única rama unificada de `main` (diff de 53413b3) — riesgo real bajo, no cero.
- **Verdict: OPTIONAL · Severidad: Nit · Bucket: l.** Procedencia: **leído** (corrida del focal +
  lectura del diff de main y del focal).
- **Condición de cierre (opcional):** agregar las sondas restantes con raíz relativa al foco o
  test de control, o declarar en el plan por qué el subconjunto representativo basta.

**OP-5 — Fallback de `_divergent_legs` con desempate no determinista.**
- **Ubicación:** `skills/cdad-cycle/scripts/cdad_packet.py:3817-3827` — cuando la pata `CLI` no está,
  elige `max(set(present), key=present.count)`; con empate el `max` sobre un `set` es
  no determinista.
- **Problema:** bajo `DRIFT` la pata `CLI` siempre está presente (el chequeo exige
  `agents_version`/`cli_version` no None para llegar a `DRIFT`, `cdad-version-check.py:231-235`), así
  que la rama es inalcanzable hoy; queda como complejidad muerta con un desempate no determinista si
  algo lo alcanzara en el futuro.
- **Verdict: OPTIONAL · Severidad: Nit · Bucket: l.** Procedencia: **leído** (código del chequeo y
  del diff del GREEN).
- **Condición de cierre (opcional):** retirar el fallback o hacerlo determinista (orden de
  `VERSION_LEGS`), con los focales de T3 en verde.

**FYI (no cuenta como hallazgo):** los encabezados DRAFT de spec y plan citan
`mofgw/deepseek-v4.1-flash` como registro de rol (procedencia anti-sesgo, patrón preexistente
aprobado en la revisión de etapa 2); el PRODUCTO de T1..T3 está limpio (grep sin coincidencias).
INV-6 en la letra («proveedor/modelo concreto … en spec, plan») convive con ese patrón de cabecera;
lo señalo como ambigüedad del contrato vigente, no como defecto del diff.

---

## Procedencia de los tres insumos (juicio solicitado)

1. **Testfix del oráculo de T1 (bloqueo parcial del GREEN): DISPOSICIÓN CORRECTA.** El diagnóstico del
   implementer es exacto (el focal pedía rc=0 de `validate-state` por un motivo que no depende de la
   raíz: la ausencia de binding, rechazo fijado por el oráculo verde preexistente
   `tests/test_005_001_t3_idle.py` — 4 passed en mi corrida) y verdaderamente "insatisfacible" sin
   violar PD-2. La corrección acotada (4ea82ea) al test-writer respetó sesiones y alcances: un solo
   archivo de tests, no debilita (agrega setup y un control de equivalencia más exigente), conserva la
   cobertura de `validate-state` y `validate-policy`, y el oráculo resulta discriminante: lo
   falsifiqué yo mismo contra el CLI pre-fix en un worktree (61d100e) — falla por el motivo correcto
   (rc=2 vs 0 por la raíz) y pasa 5/5 en HEAD. El partial-blockage declarado en el GREEN y el envío al
   test-writer fueron conducta conforme al contrato.
2. **Los dos «first» del Step 1: SÍ compiten → OP-2** (opcional/deuda con backstops y condición de
   cierre; no bloqueante bajo el criterio vigente).
3. **`cdad-epic` Step 1 sin ruta: ALCANZA por referencia** (prescripta, con el skill dueño nombrado y
   la invocación literal en `orientation.md` §1); queda OP-3 como mejora de simetría opcional.

## ABSTENCIONES

- **AB-1 (fuera de alcance del paquete):** no juzgo AC-6, AC-7 ni AC-8 (T4: aceptación de uso con
  sesiones reales nuevas y suite completa al cierre). El paquete excluye T4 de esta review; el
  comportamiento real de una sesión nueva queda a la medición del gate, con `resume`-requiere-
  `--execution-context` como backstop mecánico del riesgo OP-2.
- **AB-2 (no observable en mi alcance):** cuál «first» gana en la lectura real de un coordinador nuevo
  (la frecuencia del misreading de OP-2). No hay instrumento en mi paquete para medirla; por eso
  OP-2 cierra con condición textual verificable + verificación por el gate de T4, no con confianza
  subjetiva.

---

**Resumen: 0 bloqueantes, 5 opcionales, 2 abstenciones.**
