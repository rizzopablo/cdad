# review.md — borrador spec/plan 003-006-runtime-adoption

**Alcance:** `docs/specs/003-006-runtime-adoption/architect-draft-001.md` vs `handoff-architect-001.md`, rama `codex/epic-003-context-efficiency` @ `cf03962`. Solo lectura; nada corrido que escriba (ni `install.sh`).

## Verificación de las observaciones del orquestador

- **O-A — CONFIRMADA.** `scripts/cdad-generate.py` (función `cc_frontmatter`) emite literales `command: ~/.claude/cdad-scripts/path-guard.sh <rol>`; verificadas en los agentes adoptados (`<home>/.cache/cdad-adopted-818f12a/.claude/agents/cdad-implementer.md:11`). Copiar/enlazar esos agentes a `.claude/agents/` de un proyecto ejecutaría el guard **global viejo** (sha `18197266…` ≠ repo/adoptado `e5ab39f4…`). El borrador D4/P5 declara el outcome ("resueltos a `A/.claude/cdad-scripts/path-guard.sh`") pero **no declara el mecanismo** → R-1.
- **O-B — CONFIRMADA.** Los hooks de CC viven en el frontmatter de cada agente (generados por `cc_frontmatter`, scripts/cdad-generate.py:495–505); **no** en `settings.json`. El borrador (spec §2.2, D4) emite `.claude/settings.json` **sin definir su contenido** → BL-2. Nota: la raíz adoptada no tiene `settings.json` (verificado: `.claude/` contiene solo `agents/`, `skills/`, `cdad-scripts/`), lo que sugiere que sobra.
- **O-C — CONFIRMADA (resuelta).** `docs/runtime-adopted-version.md:123`: fila `v4 (vigente)` = `818f12a`, actualizada en `b186329`. El V6 del borrador quedó caduco (Nit N-1).
- **O-D — PARCIALMENTE.** No puedo ejecutar `claude -p`/`codex exec` (prohibido por el encargo); el juicio es análisis estático → R-2 y Abstenciones. El guion §1.4 en su estado actual No es ejecutable tal cual: faltan flags de modo no-interactivo y la frontera de escritura bajo HOME de los propios runtimes.

---

## Respondiendo las 4 preguntas del encargo

**Q1 — Cubre el objetivo sin funcionalidad nueva.** En esencia sí: D7 reutiliza `cdad_result.py` (verificado: `skills/cdad-cycle/scripts/cdad_result.py:1460-1496`, `receive`/`validate-receipt`/`materialize` existen; sin CLI nuevo); D8 acota `classify` fuera. Riesgos de creep acotables: el "chequeo de identidad de versión" (D9) no tiene mecanismo definido — puede derivar en una herramienta nueva (R-4); el generador que sobreescribe configs existentes de usuario puede volverse resolución de conflictos (R-5).

**Q2 — Postcondiciones verificables.** P1/P2/P3 son test de unidad válidos (grep de docs; determinismo byte-a-byte; `git check-ignore` — confirmé que hoy `.claude/` y `.agents/` No están ignorados, `git check-ignore` exit=1, `.gitignore:13` solo `.opencode/`). P7/P8 No requieren runtimes reales: `cdad_continuity.py` clasifica `received` por presencia de receipt legible (`_classify`, skills/cdad-cycle/scripts/cdad_continuity.py:794–814) → testable en pytest con staging sintético. **Correctamente** las que exigen runtime real (P4, P5-observado, P6, P9 "sin re-preguntar") están en T4 sin RED. Descubrimiento botado: el borrador No revela que v4 adoptada YA contiene los 4 scripts (línea 15 del borrador) — P4 puede evidenciarse aunque el resto falle; bien.

**Q3 — Restricciones del dueño.** Nunca HOME: respetado por D2/I1 «salvo» un matiz (R-6): la raíz adoptada vive bajo `$HOME/.cache` y la **re-adopción** (ausente del plan, BL-1) escribe allí — compatible con el precedente (`818f12a`, `939f501` conservadas), pero debe declararse el límite exacto. "No afectar la sesión orquestadora": el plan **no cubre** que el orquestador que ejecuta T4 tiene cargadas las reglas viejas (R-7). Configs no commiteadas: cubierto (P3/I3, `.gitignore` a commitear) — pero el ledger de T4 no declara anonimización de rutas locales (R-3-net: ver R-3/R-5).

**Q4 — Riesgos no cubiertos:** ver BL-1, BL-2, R-5 (clobber de configs de usuario existentes), R-6, R-7.

---

## Bloqueantes (BL-n)

**BL-1 — El plan no incluye la re-adopción de la nueva versión; P1 nunca llega a los runtimes.**
El wiring (T1/T3) modifica `skills/cdad-cycle/SKILL.md` y `sources/roles/orchestrator.md` en el repo, pero cada runtime carga el SKILL/orquestador desde la raíz adoptada `818f12a` (v4), cuyo `SKILL.md` No menciona `cdad_result`/`cdad_guard`/`cdad_continuity` (verificado: `grep -c` = 0 en `.agents/skills/.../SKILL.md` y `.config/opencode/skills/.../SKILL.md` y adoptadas). En Claude Code el cuerpo del orquestador solo existe en `A/.claude/agents/` (v4, sin `receive`). Sin task que ejecute `install.sh` hacia una **nueva raíz versionada del commit de cierre**, registre v5 en `docs/runtime-adopted-version.md` (predicado: filas :10, :122–123) y repunte `A` en el generador, T4 No puede evidenciar el objetivo #2 del encargo ("cada runtime carga **una misma** versión operativa") y D9/I2 quedan violados por diseño.
*Cierre:* añadir tarea (o primer paso de T4): re-adopción a nueva raíz `~/.cache/cdad-adopted-<rev>` + fila v5 en `runtime-adopted-version.md` + verificación de consumidor + repunte de A en T2/T4. Declarar el límite: escribe bajo `~/.cache`, **no** en las configs de HOME (`~/.claude`, `~/.agents`, `~/.config/opencode`) — precedente establecido por 3 adoptadas previas.

**BL-2 — `.claude/settings.json` aparece en el contrato con contenido indefinido (O-B).**
Spec §2.2 y D4 emiten `.claude/settings.json` sin definir qué contiene; P2 (determinismo byte-a-byte) hace indefinible un artefacto que no tiene contenido especificado. Además, `settings.json` de proyecto afecta a **toda** sesión abierta en el directorio — contradice la restricción del dueño ("no afectar la sesión orquestadora ni otros proyectos"). Los CDAD hooks viven en frontmatter (verificado, O-B) → no hace falta.
*Cierre:* quitar `.claude/settings.json` de §2.2/D4/P5 (mínimo), o definir su contenido exacto y por qué (solo si V1 lo exige).

---

## Recomendaciones (R-n)

- **R-1 (Required — O-A, mecanismo mínimo del guard).** El mínimo No requiere tocar `cdad-generate.py`: **reescritura determinista** en la activación de la línea `command: ~/.claude/cdad-scripts/path-guard.sh <rol>` → `command: <A>/.claude/cdad-scripts/path-guard.sh <rol>` (el guard existe en `A/.claude/cdad-scripts/path-guard.sh`, verificado). Los comentarios del frontmatter que citan `~/.claude` (scripts/cdad-generate.py:504–507) pueden quedar; el test de T2 debe afirmar que **ningún `command:` emitido contiene literal `~/.claude`**. Alternativa (regenerar con path parametrizado) es más superficie: no es lo mínimo. Razón: sin esto, un implementer copia byte-a-byte y el outcome de P5 fuerza el fix tarde.
- **R-2 (Required — O-D, guion §1.4 no ejecutable tal cual).** Especificar: (a) `claude -p` con flags no interactivos (`--permission-mode` u omisión de permisos ya que los hooks de frontmatter corren sin approval; `--max-turns`; el reconocimiento de `.claude/agents` de proyecto **es V1**); (b) `codex exec` con sandbox/permisos y el descubrimiento `.agents/skills` (es V2); (c) declarar la frontera de escritura bajo HOME: `claude`/`codex` escriben sus propios logs/sesiones bajo `$HOME` — eso No instala ni modifica CDAD, pero debe quedar escrito en el guion/ledger para no contradecir la restricción del dueño. Razón: T4 (owner orquestador) tendría que improvisarlos en frío.
- **R-3 (Required — Makefile arrastrará diffs ajenos).** `make agents` copia **todos** los `cdad-*.md` de staging a `agents/` y `agents/claude-code/` (Makefile:17–19). T3 declara solo 3 archivos; si staging tiene salida pendiente de otros roles, el GREEN puede commitear diffs no pedidos. Cierre: staging limpio antes del `make agents` o listar los archivos realmente tocados.
- **R-4 (Required — acotar D9 al manifest existente).** "Chequeo de identidad de versión" sin mecanismo = riesgo de funcionalidad nueva (contra D1). Mínimo: comparar los archivos emitidos contra los sha del manifest que **ya existe** en `A` (`.cdad-install-manifest.json`); el "la sesión reporta qué cargó" del recorrido es prompt-level, gratis. Sin herramienta nueva.
- **R-5 (Required — no clobber configs de usuario).** El generador no detecta choque con configuración existente No propia (ej. un `opencode.jsonc` con `model`/`permission` del dueño). Un overwrite silencioso afectaría otros proyectos — restricción del dueño. Cierre: si el target existe y difiere de lo que el generador emitiría, falla con error (dry-run la muestra), nunca sobreescribe en silencio.
- **R-6 (Consider — ambigüedad de I1).** I1 ("ninguna activación escribe bajo HOME") es correcto para el generador, pero leído a la letra prohíbe la re-adopción (BL-1) porque la raíz adoptada vive bajo `$HOME/.cache`. Reescribir I1: "no escribe en las configuraciones del HOME real (`~/.claude`, `~/.agents`, `~/.config/opencode`); la raíz adoptada versionada bajo `~/.cache` es la excepción declarada".
- **R-7 (Consider — reglas vigentes de T4).** El orquestador que ejecuta T4 tiene cargado el cuerpo del agente **viejo** (publicado por `prepare` I9); un recargado a mitad de sesión es incierto. Declarar en el plan: durante T4 las reglas nuevas se leen ad hoc del repo (o `resume` en sesión nueva de orquestador tras re-adopción), y eso queda en el ledger.
- **R-8 (Consider — ledger anónimo).** El formato del ledger (`runtime | base cargada (file:line) | …`) no declara anonimización; el repo es potencialmente público. Fijar: rutas relativas o marcadores (`<adopted-root>/<sha>/…`), ninguna ruta absoluta local commiteada (precedente contrario ya en `docs/runtime-adopted-version.md:14` — no replicarlo en el ledger).
- **N-1 (Nit).** V6 del borrador ya está resuelto (v4 = `818f12a` vigente, `runtime-adopted-version.md:123`, commit `b186329`); actualizar la mención para no reintroducir la duda del dueño.
- **N-2 (Nit).** En el bloque `plan-tasks`, T3 `consume` el artefacto de T1 con `depends_on: []`: coherencia formal a validar contra el validador del plan (si `consume` implica dependencia, añadir `depends_on`).
- **N-3 (Nit — P5 bifurcada).** La mitad unit-testable de P5 (bytes emitidos, ruta del hook, shape) está en T2; la mita "un hook ausente No bloquea herramientas" es comportamiento de runtime CC (exit 127 ≠ 2 ya es fail-open estructural) → solo evidenciable en el rehearsal de T4; no forzar esa cláusula al test RED de T2.

---

## Qué pasa a deuda (proporcionalidad — No rompen el camino feliz)

Confirmo las ya declaradas por el borrador (1.6 / Vacunas), y añado solo:
1. **Guard parametrizado en origen:** si algún día `cdad-generate.py` debe emitir rutas relativas al proyecto (vs. reescritura en activación), a deuda — la reescritura en activación (R-1) basta para MVP.
2. **Settings.json de CC de proyecto:** si V1 revela que algo de settings es imprescindible, queda como deuda del endurecimiento, no del MVP.
3. `reconcile` clasifica `received` solo vía receipt (verificado en `_classify`) — el caso "dispatch recorded, no receipt" sigue siendo `dispatched` genérico; aceptable, sin deuda nueva.

## Abstenciones

- **No verifiqué V1** (descubrimiento/merge-trust de `.claude/` de proyecto y precedencia vs `~/.claude`) ni **V2** (descubrimiento de skills de Codex por proyecto), ni V3 re-confirmado: exigen ejecutar los runtimes reales, prohibido por el encargo ("sin `opencode run`/`claude`/`codex` anidados"). P5/P6 en su mitad observable dependen íntegramente de la evidencia T4 — así debe quedarse.
- **No ejecuté `claude -p`/`codex exec`** para O-D: el juicio de ejecutabilidad (R-2) es análisis estático del guion, no una corrida.
- **No corrí `install.sh`** (ni `--dry-run`) — análisis del manifest/os archivos adoptados existentes únicamente.

## Veredicto

**Aprobable con cambios.** El esqueleto discovery → D1–D10 → P1–P10 → T1–T4 es correcto, proporcional y honesto (los VERIFY están bien etiquetados; el reuso de 002/004 es real — comprobado en los CLIs). Los dos bloqueantes son de **plan**, no de idea: (BL-1) la re-adopción de la nueva versión operativa que da sentido a todo el epic, y (BL-2) el artefacto indefinido `.claude/settings.json`. Ambos se corrigen editando el borrador sin tocar código.
