# Auditoría de consistencia CDAD — 2026-09-02

Revisión completa de metodología (`CDAD_metodologia.md`), skills
(`cdad-cycle`, `cdad-epic`, familia `odoo-*`), agentes (OpenCode +
Claude Code, base + variantes Odoo), ADRs, scripts e instalador.

**Método:** lectura lineal de la metodología + *diff pass* sistemático sobre
cada bloque normativo que está duplicado en más de un archivo, + ejecución de
los validadores del repo y pruebas empíricas del path-guard.

**Diagnóstico de fondo:** el repo no tiene bugs dispersos; tiene **un solo
modo de falla repetido** — texto normativo copiado en N lugares sin generador
ni test de consistencia, que drifteó. Los 11 bloqueantes de abajo son
instancias de eso. La sección final propone el remedio estructural.

---

## Bloqueantes — cambian lo que un agente hace en runtime

### B1 — `bash` es la puerta trasera que anula el aislamiento anti-trampa (los dos runtimes)

El Principio 3 (sesiones aisladas con permisos granulares) es la razón de ser
de CDAD: la barrera es *estructural*, no conductual. Hoy es conductual en
ambos runtimes, por la misma vía.

**OpenCode** (`agents/cdad-test-writer.md`, `agents/cdad-implementer.md`):

```yaml
# cdad-test-writer
read:  { "src/**": deny, "lib/**": deny }
grep:  { "src/**": deny, "lib/**": deny }
bash:  { "*": allow }          # ← cat src/impl.py
```
```yaml
# cdad-implementer
edit:  { "tests/**": deny }
write: { "tests/**": deny }
bash:  { "*": allow }          # ← sed -i 's/…/…/' tests/test_x.py
```

**Claude Code** (`scripts/claude-code-path-guard.sh` + frontmatter): los
matchers del hook son `Read|Grep|Glob` y `Edit|Write`. `Bash` no está en
ningún matcher, y el script además hace `exit 0` cuando no hay `file_path`
(comentado en el propio script: *"Si no hay file_path (e.g., Bash sin
--file-path), permite"*). Verificado empíricamente:

```
Edit tests/x.py  como implementer      → exit 2  (bloquea, OK)
Bash sed -i tests/x.py como implementer → exit 0  (pasa)
Bash cat src/impl.py como test-writer   → exit 0  (pasa)
Read src/impl.py como test-writer       → exit 2  (bloquea, OK)
```

Bonus del mismo script: `relativize()` deja pasar rutas absolutas fuera de
`$PWD` (`/otro/repo/src/x.py` → `otro/repo/src/x.py`, no matchea `src/**`) →
`Read` de una ruta absoluta externa también hace exit 0.

**El repo tiene media solución escrita.** Las cinco variantes `-odoo` usan
`bash: {"*": deny}` + allowlist, que es la forma correcta — pero la allowlist
sigue filtrando: `cdad-test-writer-odoo` deniega `read`/`grep` sobre
`**/models/**` y a la vez permite `cat *` y `git *`, así que `cat models/x.py`
y `git show HEAD:models/x.py` leen la implementación igual. Las variantes
Odoo **estrecharon** el agujero; no lo cerraron.

Fix, en tres partes (portar el patrón sin arrastrar la fuga):
1. `bash: {"*": deny}` + allowlist en `cdad-test-writer` y `cdad-implementer`;
2. en esa allowlist, `cat`/`head`/`tail`/`rg` acotados a los paths que el rol
   ya puede leer, y `git` acotado a `git diff|log|status` (nunca `git show`
   ni `git *` genérico — ver también M4);
3. en Claude Code, agregar al hook un matcher `Bash` que inspeccione
   `tool_input.command` en vez de `file_path`, y cerrar el fail-open de
   `relativize()` para rutas absolutas fuera de `$PWD`.

Mientras esto no esté, el gate 3→4 y AP-1/AP-2/AP-4 dependen de que el
sub-agente se autolimite — exactamente lo que el capítulo 1 de la metodología
dice que no hay que hacer.

### B2 — El perfil `premium` en Claude Code viola el invariante anti-bias, y el guard no lo ve

`scripts/cdad-models.sh`, `cdad_model_claude`:

```bash
premium\|architect|premium\|scribe|premium\|reviewer|premium\|implementer)
  echo "opus";;
```

Verificado: `premium` → implementer `opus`, reviewer `opus`. **Mismo modelo**,
no ya misma familia. La función lleva encima el comentario
*"Invariante: reviewer ≠ implementer … igualmente exigido"*.

El guard de `scripts/validate-subagents.sh` sólo evalúa `cdad_model`
(OpenCode); `cdad_model_claude` nunca entra en `MODEL_EXPECTED`, así que
nadie lo detecta.

Segundo problema del mismo guard: compara **strings exactos**, y el
invariante escrito es de **familia**. Un
`CDAD_PREMIUM_MODEL_REVIEWER=mofgw/deepseek-v4-flash` con implementer
`deepseek-v4-pro` pasa el guard y viola el invariante. La enmienda 2026-08-24
de ADR-007 identifica exactamente este agujero (*"el guard del validator
(comparación de strings) la dejaría pasar, pero violaría el invariante de
diseño"*) y lo resuelve por elección manual de modelo, no en código.

Fix: extender el guard a `cdad_model_claude`, y agregar una tabla
`modelo → familia` para que la comparación sea por familia.

Defectos menores en el mismo archivo (comentario contradice el código):
- bloque premium claude dice *"sonnet test-writer"*, el código emite `opus`;
- bloque economical claude dice *"reviewer sube a opus"* y acto seguido
  discute `economical|reviewer=haiku`, que el código nunca produce.

### B3 — El contrato de veredicto vive en el packet pero contradice el system prompt del agente reviewer

`references/re-entry.md:130` ordena rechazar la review que no traiga
`Bucket: <h|m|l>` y sección "Abstenciones" (*"Sin bucket/provenance → pedir
corrección"*). `stage-4-review.md:21` y el template de reviewer de
`handoff-prompts.md:451,466-496` sí lo llevan: el packet arranca con
*"leé `references/verdict-tuple.md` … actuá como `reviewer`"* y trae el
formato con `Veredicto`/`Bucket`/`Abstenciones`.

El problema es el **conflicto**: los cuatro archivos de agente reviewer
(`agents/cdad-reviewer.md`, `agents/claude-code/cdad-reviewer.md` y sus dos
variantes `-odoo`) tienen **cero** ocurrencias de `Bucket`, `ABSTENER` o
`verdict-tuple`, y prescriben en su propio *"Formato de output"* un reporte
Bloqueantes/Opcionales sin esos campos.

Cuando el orquestador delega —que es la ruta que SKILL.md §4 marca como
**preferida**— el sub-agente recibe dos especificaciones de formato
incompatibles: la del packet y la de su propio system prompt. El system prompt
del sub-agente pesa más, así que lo esperable es una review sin `Bucket` ni
`Abstenciones`, que `re-entry.md` está obligado a rechazar. Por la ruta de
handoff manual a chat nuevo el conflicto no existe (no hay system prompt de
agente), lo que produce el resultado invertido: la ruta *menos* recomendada es
la que cumple el gate.

El fix es unidireccional y barato: agregar el tuple de 4 campos al bloque
"Formato de output" de los cuatro agentes reviewer, para que las dos
superficies digan lo mismo.

### B4 — Tres taxonomías incompatibles para el mismo artefacto, sin regla de traducción

| Fuente | Vocabulario |
|---|---|
| `agents/cdad-reviewer.md` (+ `-odoo`, + skill `odoo-reviewer`) | ejes Correctness / **Readability** / **Architecture** / Security / Performance · severidad Critical / Required / Optional / Nit / FYI |
| `agents/claude-code/cdad-reviewer.md` | ejes Correctness / **Robustness** / **Maintainability** / **Testability** / Performance · severidad CRITICAL / MAJOR / MINOR / TRIVIAL |
| `stage-4-review.md` Capa 2 + `verdict-tuple.md` | BLOQUEANTE / OPCIONAL / ABSTENER (+ bucket h/m/l) |

El gate 4→5 cuenta "bloqueantes resueltos". Nada dice si `MAJOR` es
bloqueante, ni cómo mapear `Nit`/`FYI`. Y las descripciones de los agentes
que el runtime muestra al usuario prometen "5 ejes" sin decir cuáles, así que
el mismo diff revisado en OpenCode y en Claude Code produce dos reportes que
no se pueden comparar.

### B5 — Property tests y E2E: excluidos y exigidos en el mismo archivo

`SKILL.md` §3 y `stage-3-tdd.md` (mismas palabras, dos veces):

> *"La cobertura exhaustiva, **property tests**, load/perf y edge cases NO
> pertenecen al ciclo de feature. Son responsabilidad de una etapa/epic de
> hardening separada, posterior."*

Y a ~200 líneas de distancia, en esos mismos dos archivos:

- diagrama del ciclo: `3.4 PROPERTIES` y `3.5 E2E` con sus gates;
- `## Sub-fase 3.4 — PROPERTIES` con procedimiento y criterio (`seed fijo, ≥100 inputs`);
- Gate 3→4: *"Si spec marca invariantes → property tests verdes"*;
- tabla §2: `test-writer (RED/props/E2E) | 3.1, 3.4, 3.5`;
- AP-12 existe sólo para property tests.

`CDAD_metodologia.md` §7.5/§7.6, el cheatsheet §13.1 y el README los ponen
firmemente **dentro** de la etapa 3.

Un orquestador que lee §3 concluye que están fuera de alcance y después choca
con un gate que bloquea por ellos. Hay que decidir cuál gana y borrar la otra
mitad (mi lectura: la exclusión apunta a *cobertura exhaustiva y load/perf*,
no a property tests derivados de invariantes del spec — entonces sacar
"property tests" de la frase de exclusión).

### B6 — El orquestador de Claude Code está mal portado

`agents/claude-code/cdad-orchestrator.md` es copia casi verbatim del de
OpenCode. Tres consecuencias:

1. **Modelos que no existen en ese runtime.** Su tabla §2 y su nota de
   perfiles llevan `deepseek-v4-pro`, `glm-5.2`, `qwen3.7-plus`,
   `minimax-m3`. En Claude Code los modelos son `haiku|sonnet|opus`
   (`cdad_model_claude`). El orquestador cree que el reviewer corre en
   minimax-m3 cuando corre en opus.
2. **Nombres de herramienta equivocados.** Instruye *"roles read-only vía
   `delegate`; write-capable vía `task`"* — ambas son de OpenCode. Su propio
   frontmatter declara `tools: … Task`, y `claude-code-delegation.md` dice
   que el mecanismo es la herramienta `Agent`.
3. **Perdió la resolución de sufijo por stack.** El de OpenCode tiene:
   *"Primero resolvé el sufijo de stack: `docs/.cdad-state.json.stack` — si
   tiene valor y existe `cdad-<rol>-<stack>`, usá esa variante"*. El de
   Claude Code **no lo tiene**. Resultado: con `stack: odoo` en Claude Code,
   el orquestador nunca delega a las variantes `-odoo` aunque `install.sh`
   las instaló en `~/.claude/agents/`. SKILL.md §3.1 promete lo contrario.

### B7 — `basic` es el perfil realmente instalado y ningún documento operativo lo menciona

El bloque §2 está triplicado **idéntico** en `SKILL.md:77`,
`agents/cdad-orchestrator.md:69` y `agents/claude-code/cdad-orchestrator.md:70`:

> `Switch: install.sh --economical|--optimus|--premium.`

`install.sh` acepta `--basic` desde la enmienda 2026-08-29 de ADR-007, y ese
es el perfil activo hoy. En `basic` el instalador **borra la línea `model:`**
y, en palabras del propio ADR, *"el invariante anti-bias … NO es garantizado
por el instalador"*. Las tres copias del bloque §2, tres líneas más abajo,
siguen afirmando:

> **Invariantes anti-bias (no negociables):** reviewer usa familia de modelo
> distinta al implementer.

El ADR documenta el trade-off correctamente; la capa que el agente
efectivamente lee, no. Fix: agregar `--basic` a la nota de perfiles y
condicionar el invariante (*"garantizado por el instalador en
economical/optimus/premium; en basic requiere override manual en
`opencode.jsonc`"*, que es la receta que ya está en la enmienda 2).

### B8 — El validador propio del repo está en FAIL, por una aserción que ya no puede ponerse verde

```
$ bash scripts/validate-subagents.sh
✅ 10/10 agentes runtime presentes
✅ install.sh --check PASS (27/27 in sync, perfil basic)
❌ implementer -> FAIL (impl.diff)
[modelos] perfil basic: … el anti-bias reviewer≠implementer NO es verificado
== RESULTADO: FAIL ==
```

(`tests/validate-odoo-specialization.sh` sí está en PASS, 121/121.)

**Causa raíz.** El único `❌` no es un guard estructural roto: es la Etapa 3 de
artefactos del spike cdad-001, que verifica que
`docs/specs/cdad-001-validate-subagents/artifacts/impl.diff` (congelado el
2026-08-05) siga aplicando sobre el árbol actual, en reverse (ya aplicado) o
forward (aún aplicable). Ese diff toca `scripts/validate-subagents.sh`, y ese
archivo fue reescrito después por cdad-003 y ADR-007 (profile-awareness, guard
anti-bias). Verificado: fallan las dos direcciones —
`patch failed: scripts/validate-subagents.sh:33` en reverse,
`:18` en forward.

O sea: es una aserción auto-invalidante. Ninguna corrección de código la va a
poner verde, porque el "fallo" es que el repo evolucionó legítimamente encima
del archivo que el artefacto histórico congela. Y como está en rojo permanente
y nadie puede arreglarla, quedó normalizada — que es el mecanismo exacto por el
que AP-9 dice que se erosiona la confianza en CI.

Dos salidas, ambas de minutos:
- retirar esa aserción (el spike cdad-001 ya cumplió su función; su valor
  probatorio está en `findings/validation-cdad-001.md`, no en que el diff
  siga aplicando), o
- regenerar `impl.diff` contra el estado actual y aceptar que hay que
  regenerarlo cada vez que alguien toque el validador.

En cualquier caso el hallazgo de proceso queda: **`progress.md` no registra
esto como deuda aceptada**, y `SKILL.md` §Verification regla 5 dice
*"deuda documentada ≠ deuda oculta"*. Hoy es deuda oculta detrás de un exit
code que nadie mira.

### B9 — El schema del state file tiene cinco versiones divergentes

| Fuente | `stack` | `audit_status` | `active_epic` + `epic_*` |
|---|---|---|---|
| `SKILL.md` (ejemplo) | ✅ | ❌ | ❌ |
| `state-detection.md` Paso 1 ("estructura mínima") | ❌ | ❌ | ❌ (lo menciona en prosa, no en el schema) |
| `assets/state-template.json` | ✅ | ✅ | ❌ |
| `bootstrap.md` Paso 4 | ❌ | ❌ | ❌ |
| `cdad-epic/SKILL.md` | ❌ | ❌ | ✅ (+ `epic_stage`, `epic_features`, `epic_history`) |

`bootstrap.md` Paso 2b manda escribir `stack` en un JSON que su propio Paso 4
no declara. Y el state real del repo usa `"current_stage": "idle"`, valor que
ningún enum lista (`discovery|specification|tdd|review|merge|done`): un
orquestador que aplique `state-detection.md` a este repo no sabe dónde está.

Fix: `assets/state-template.json` como fuente única; todas las demás
referencias apuntan a él en vez de reproducirlo, y se agrega `idle` al enum
(o se normaliza el state a `done`).

### B10 — Gates duplicados en `SKILL.md` y en las stage refs, drifteados

| Gate | Sólo en SKILL.md | Sólo en la stage ref |
|---|---|---|
| 2→3 | formatos de aprobación aceptados (`Status: Approved by…` / frontmatter) | *"si el spec es complejo: `plan.md` existe, pasó auto-revisión y está aprobado"* |
| 3→4 | *"Test Audit completado y aprobado"* · *"cada test modificado tiene justificación explícita en spec.md"* | — |
| 5→done | carve-out *"si NO hay CI configurado: suite local + deuda registrada"* | *"Feature mergeada"* (y "CI verde completo" sin carve-out) |

El item de `plan.md` es el que más duele: cdad-008 lo agregó a `stage-2` y no a
`SKILL.md`, así que un orquestador que valide el gate desde el contrato
principal (que es lo que SKILL.md dice tener *"siempre cargado"*) deja pasar
una feature compleja sin plan aprobado.

### B11 — El gate 4→5 contradice la excepción de delegación documentada en su propio archivo

`stage-4-review.md` dedica dos secciones a la delegación legítima de la Capa 2
(usuario-agente autónomo, y excepción por pedido explícito), con trazabilidad
en `review.md` y `stage_history`. Cuarenta líneas más abajo, su propio gate:

> - [ ] Usuario aprobó priorización (**no delegado al LLM**).

Idéntico en `SKILL.md`. Un ciclo que usó la delegación explícita —el camino
que el mismo archivo bendice— no puede cerrar el gate. `AP-10` en
`stage-2-specification.md` tiene el mismo problema en versión corta
(*"delegar la aprobación al LLM. Indelegable."*, sin la excepción que
`anti-patterns.md` sí documenta).

Fix: redactar el item como *"priorización validada por el usuario, o
agente-delegada con pedido explícito registrado en `stage_history`"*.

---

## Medios — costo de mantenimiento y calidad del output

### M1 — Los cinco agentes base divergieron fuerte entre runtimes

Líneas de cuerpo divergentes (sin frontmatter):

| Agente | OpenCode | Claude Code | divergentes |
|---|---|---|---|
| cdad-reviewer | 90 | 122 | **156** |
| cdad-scribe | 36 | 89 | 87 |
| cdad-architect | 61 | 61 | 76 |
| cdad-test-writer | 82 | 146 | 76 |
| cdad-implementer | 59 | 92 | 39 |
| cdad-orchestrator | 195 | 191 | 12 |
| **las 5 variantes `-odoo`** | — | — | **4-6** |

Las mejoras se aplicaron de un solo lado: los checklists GREEN y REFACTOR
existen sólo en el implementer de Claude Code; la postura adversarial y las
anti-rationalizations sólo en el reviewer de OpenCode. Las variantes `-odoo`
están sincronizadas (4-6 líneas) — otra vez, el patrón sano ya existe en el
repo y no se aplicó donde importa.

### M2 — El scribe de Claude Code apunta a un archivo que no existe en la convención

`agents/claude-code/cdad-scribe.md:18,80` manda materializar en
`docs/memory-bank.md`. El Memory Bank de CDAD es
`activeContext.md` + `progress.md` + `adr/`; no hay `memory-bank.md`. El
scribe de OpenCode lo dice bien (*"los tres drafts … el orquestador los
materializa en los archivos del Memory Bank"*).

### M3 — Los allowlists de `bash` de los roles read-only genéricos son Go-only

`cdad-architect`, `cdad-reviewer` y `cdad-scribe` permiten `go test*`,
`go vet*`, `go build*`, `gofmt *` — herencia literal del spike Go de cdad-002.
No hay `pytest`, `make`, `npm`, `cargo`. En cualquier proyecto que no sea Go,
el reviewer no puede correr nada, mientras `stage-5-merge.md` §5.1 y la tabla
de evidencia de `SKILL.md` le exigen output de suite. (Las variantes `-odoo`
lo resolvieron con `make *` / `pylint *` / `pre-commit *`.)

Sugerencia: allowlist mínima agnóstica (`make *`, `git diff|log|show|blame`,
`ls|cat|head|tail|wc|find|rg|pwd`) + un hueco documentado para el comando de
test del proyecto, tomado de `systemPatterns.md`.

### M4 — Los roles read-only de la familia Odoo pueden escribir git

`cdad-architect-odoo`, `cdad-reviewer-odoo` y `cdad-scribe-odoo` traen
`"git *": allow` → `git commit`, `git push`, `git reset`, `git checkout`
habilitados para roles cuyo contrato dice *"Puede editar: nada"*. Es
exactamente la superficie que AP-17 (integración destructiva) existe para
cerrar, y el incidente citado en AP-17 fue un `git reset` sobre trabajo sin
commitear. Las variantes genéricas lo hacen bien
(`git diff*|log*|show*|blame*`).

### M5 — Dos references quedaron fuera de la tabla de carga

`verdict-tuple.md` y `claude-code-delegation.md` no están en *"Cómo leer las
references"* de `SKILL.md`. En un skill construido sobre progressive
disclosure —cuya propia instrucción es *"cargá una a la vez, no mantengas todo
el árbol en contexto"*— una reference ausente de la tabla es una reference que
no se carga nunca. `verdict-tuple.md` es justamente el contrato que B3 dice
que falta.

### M6 — `claude-code-delegation.md`: API inventada y cita de AP equivocada

```python
from Agent import agent
result = agent(subagent_type="cdad-test-writer", prompt="…")
```
No existe. Claude Code no expone un módulo Python `Agent`.

Y más abajo: *"el invariante 'test-writer nunca ve `src/`' es crítico
(**AP-7**, anti-trampa)"*. AP-7 es "Memory Bank desactualizado". Los correctos
son AP-1/AP-2. En un corpus donde la instrucción es *"citá el código (AP-N)
para que el usuario pueda buscarlo"*, una cita cruzada mal apuntada envía al
lector al anti-patrón equivocado.

### M7 — Cuatro archivos huérfanos en `skills/*.md`, stale

| Archivo | vs. su reference canónica | líneas de diff |
|---|---|---|
| `skills/handoff-prompts.md` | `cdad-cycle/references/` | **319** — le falta toda la sección de invocación con sub-agentes y el template completo de Test-writer AUDIT |
| `skills/re-entry.md` | `cdad-cycle/references/` | 3 — le falta el contrato de veredicto |
| `skills/feature-handoff.md` | `cdad-epic/references/` | 11 — le falta la nota de independencia del arnés |
| `skills/epic-planning.md` | `cdad-epic/references/` | 0 — duplicado exacto |

`install.sh` los declara *"reference docs, intentionally never installed"*.
Nadie los enlaza y nada los sincroniza: son trampas para quien lea el repo.
Sugerencia: borrarlos, o dejar un stub de una línea apuntando al canónico.

### M8 — `verdict-tuple.md` filtra contexto privado en un skill distribuible

Sección *"Aplicación actual"*: *"Deep-read reviews (**mi pipeline arXiv**)"*,
*"**fb-012 lesson**"*, *"**guard-event-log (G1)**"*, y en Anti-scope
*"NO toca cdad-epic (**gated por aprobación de Pablo**)"*. Nada de eso es
resoluble para un consumidor externo del skill, y `tests/…-odoo…sh` ya corre
un check A3 de sanitización sobre `skills/`. Mover ese contexto al ADR o a
`activeContext.md` y dejar en la reference sólo el contrato.

### M9 — El dogfooding del propio repo no cumple sus convenciones de epic (corregido 2026-09-02, más acotado de lo que decía la primera versión)

**Corrección sobre el hallazgo original:** la primera versión de este ítem
decía *"`docs/epics/` está vacío"*, basada en `ls -d docs/epics` (que sólo
imprime el nombre del directorio, no su contenido — error de comando, no de
lectura). `docs/epics/epic-001-superpowers-gaps/plan.md` existe, está
completo (resumen, scope, 5 features con dependencias y orden de ejecución,
contratos cross-feature, criterios de aceptación, riesgos) y tiene
`Status: Approved by Pablo on 2026-09-02`. El Gate E2 de `cdad-epic` **sí**
está cumplido. Retiro esa afirmación.

Lo que sí queda en pie, más acotado:
- faltan `epic_stage`, `epic_features`, `epic_history` en
  `docs/.cdad-state.json` (los campos que `cdad-epic` lee para saber dónde
  está — el epic quedó `done` de hecho pero sin que el state file lo declare
  en su propio vocabulario);
- las features se llaman `cdad-005…cdad-009`, no
  `<epic-num>-<feat-num>-<slug>` como manda la convención de IDs de
  `cdad-epic/SKILL.md` (`epic-001-superpowers-gaps` no colapsa a un
  `<epic-num>` numérico limpio, así que la convención tal como está escrita
  no tiene una traducción obvia — vale precisarla para epics con id
  no-numérico);
- no existe `docs/epics/epic-001-superpowers-gaps/closure.md` pese a que las
  5 features están `done` en `progress.md` — el Gate E4→done de `cdad-epic`
  nunca se ejecutó formalmente aunque el trabajo sí cerró;
- se encontraron además 4 directorios vacíos y huérfanos
  (`docs/epics/epic-002-git-safety`, `epic-003-systematic-debugging`,
  `epic-004-granular-planning`, `epic-005-parallel-dispatch` — sin
  referencias en ningún `.md`/`.json` del repo, aparentemente un intento
  temprano de un epic por tema antes de consolidar en `epic-001` con 5
  features).

Invocar `cdad-epic` sobre este repo hoy detecta plan aprobado y todas las
features done, pero no puede cerrar el epic formalmente (falta closure.md) ni
reportar el estado con su propio vocabulario (faltan los campos de state).

### M10 — `cdad-epic` no tiene ruta de sub-agentes

`cdad-cycle` §4 establece un orden de preferencia explícito (sub-agentes →
handoff packet → inline). `cdad-epic` sólo ofrece *"Abrí chat nuevo"*, sin
mencionar delegación nativa, y no existe un agente `cdad-epic-*`. La
asimetría no está justificada en ningún lado; o se documenta como decisión, o
se le da la misma regla de decisión que a `cdad-cycle`.

---

## Cosméticos

- **`SKILL.md`**: el encabezado *"## Anti-rationalization table"* queda
  separado de su tabla por la sección *"Validación externa del modelo
  (addyosmani)"*, cuyo texto dice *"la refutación ya está escrita **arriba**"*
  apuntando hacia abajo.
- **`anti-patterns.md`**: AP-15 está intercalado entre AP-10 y AP-11; la
  sección *"Cómo usar este archivo"* quedó a mitad de archivo, con AP-18 y
  AP-19 colgando después. Señal de append sin integrar.
- **`opencode-delegation.md`**: frase rota (*"apuntando el modelo del
  sub-agente a la vía el gateway local"*) y *"se mantiene en los 3 perfiles"*
  (son cuatro desde `basic`).
- **`state-detection.md`**: Paso 1 dice que el state file es *"la fuente de
  verdad"*; Paso 5 dice que *"el archivo gana"*. Se resuelve con el
  sanity-check, pero conviene una sola formulación.
- **`cdad-epic/references/anti-patterns.md:69`** referencia
  `references/coordination-with-cdad-cycle.md`, que no existe.
- **`claude-code-delegation.md`**: calcos del inglés (*"se preserve"*,
  *"respecta"*, *"la garantía es conductual, no structural"*).
- **`handoff-prompts.md`**: la sección de invocación con sub-agentes dice
  explícitamente *"en OpenCode"*; no hay equivalente para Claude Code pese a
  ADR-008.

---

## Remedio estructural (la sugerencia principal)

Los once bloqueantes son la misma falla: **bloques normativos copiados sin
generador ni test de consistencia**. Corregirlos uno por uno los reintroduce
en la próxima feature. Tres movimientos, en orden de retorno:

**1. Fuente única para los cuatro bloques que hoy están duplicados.**

| Bloque | Copias hoy | Debería vivir en |
|---|---|---|
| Contrato de roles §2 + nota de perfiles | `SKILL.md` + 2 orquestadores | un `references/role-contract.md` que los tres incluyan por referencia |
| Checklists de gates | `SKILL.md` + 5 stage refs | sólo en las stage refs; `SKILL.md` enlaza |
| Schema del state file | 5 lugares | `assets/state-template.json`; el resto apunta |
| Taxonomía de severidad/veredicto | 3 vocabularios | `verdict-tuple.md`, y los 4 agentes reviewer lo citan |

**2. Un `tests/validate-consistency.sh` con el mismo estilo assert de
`validate-odoo-specialization.sh`** (que ya corre 121 asserts en verde). Los
asserts que habrían atrapado todo lo de arriba son baratos:

- el bloque §2 es byte-idéntico en las 3 copias (ADR-007 ya afirma esta
  propiedad — hoy no está testeada);
- cada gate de `SKILL.md` tiene item por item su contraparte en la stage ref;
- `cdad_model_claude` cumple reviewer ≠ implementer en los 4 perfiles;
- ningún agente reviewer omite `Bucket` / `ABSTENER`;
- todo `references/*.md` aparece en la tabla de carga;
- toda ruta citada entre backticks existe;
- las claves de `assets/state-template.json` son superset de las que aparecen
  en los ejemplos de `SKILL.md`, `state-detection.md`, `bootstrap.md` y
  `cdad-epic/SKILL.md`;
- ningún agente base tiene `bash: {"*": allow}`.

**3. Regla de paridad de runtime.** Todo cambio a un agente base toca las dos
variantes en el mismo commit, o el archivo declara arriba por qué diverge. Las
variantes `-odoo` ya cumplen esto (4-6 líneas de diff): el repo sabe hacerlo,
sólo no lo hizo donde el drift era más caro.

---

## Lo que está bien y conviene no tocar

Para no leer esto como una lista de desastres: la arquitectura conceptual es
sólida y varias piezas son mejores que el promedio del rubro.

- La separación **contrato de roles (siempre cargado) / references
  (profundización)** es el diseño correcto para progressive disclosure, y la
  tabla §2 es una pieza de ingeniería de prompt de calidad.
- La **tabla anti-racionalización** con refutación pre-escrita por excusa es
  la mejor defensa práctica contra el skip de gates que vi implementada en un
  skill.
- **§5.6 (git safety)**, con detección de entorno, guard de submodule, menú
  fijo, confirmación por palabra literal y limpieza por provenance, es
  material de referencia. AP-17 y AP-18 (thrashing) son anti-patrones reales,
  bien caracterizados por síntoma.
- El **presupuesto de corridas** y la **reutilización de evidencia del gate**
  (presupuesto 0 para el reviewer si el árbol no cambió) atacan un costo real
  que casi nadie modela.
- Las **variantes `-odoo`** son el ejemplo de cómo debería verse el resto en
  disciplina de mantenimiento: sincronizadas entre runtimes (4-6 líneas de
  diff), `bash` con allowlist en vez de `*: allow`, contrato de make
  explícito, y con su propio test en verde. La allowlist todavía filtra
  (B1, M4), pero la forma es la correcta.
- El **ADR-007 con sus tres enmiendas** documenta honestamente los trade-offs,
  incluida la suspensión del anti-bias en `basic`. El problema no es el ADR:
  es que la capa operativa no lo siguió.
