# Informe T2b — 005-011-common-entry (implementer · subetapa GREEN)

- Paquete: `005-011-common-entry-implementer-green-004` (packet_version 1)
- Contrato: `docs/specs/005-011-common-entry/spec.md` (sha256 `a6d05d9d…e39a`), enmienda 4; plan `docs/specs/005-011-common-entry/plan.md` ficha T2b
- Rol: implementer. Invariante «no editar tests»: **cumplida** (no se tocó `tests/**`).
- Tipo de trabajo: SOLO documentación (una palanca, por referencia) + regeneración de derivados.
- Commit: `68044cb` — `68044cba8fb935a4bdbe99abae9b3e2fe39c8261`

## 1. Cambio (archivo:línea)

**`sources/roles/orchestrator.md:107-112`** — nuevo bullet **Session entry (every new session)** al frente del bloque *Continuity wiring*: la **primera acción de toda sesión** es cargar la skill `cdad-cycle` y consultar su vista compacta `status`, **por referencia** a `orientation.md` §1 (la regla «view first, expand on a concrete need» se compone en `project-start.md` §11; se **cita, nunca se reescribe**). El **state completo** pasa a **ampliación condicional**: se carga solo ante una necesidad concreta que afecte al siguiente despacho, con el motivo registrado. No se copia la regla ni la invocación completa del CLI.

**`sources/roles/orchestrator.md:116-117`** — `resume` deja de ser «the first step of every new session that resumes work» y pasa a ser **el paso siguiente a la vista**, y solo con una ejecución activa.

**`sources/roles/orchestrator.md:118-122`** — se **conserva intacta** la rama `**Start from rest:** never resume without an active execution …` (guarda por ventana de 005-003/005-006).

**Derivados regenerados** (ventana idéntica a la fuente):
- `agents/cdad-orchestrator.md:101-115` (OpenCode)
- `agents/claude-code/cdad-orchestrator.md:106-120` (Claude Code)

No se tocó ningún otro rol, ni el mecanismo de despacho, ni el resto del prompt.

## 2. Tabla observable_check → resultado

| observable_check (desglosado) | Resultado | Evidencia |
|---|---|---|
| El prompt generado del orquestador (**OpenCode** y **Claude Code**) nombra la vista `status` como primera acción | ✅ | `agents/cdad-orchestrator.md:101` y `agents/claude-code/cdad-orchestrator.md:106` («Session entry … the first action is to load the `cdad-cycle` skill and consult its read-only compact view `status`»); paridad con `sources/roles/orchestrator.md:107` |
| Conserva la rama «sin ejecución activa → no resume» (`resume` como paso siguiente, no primero) | ✅ | `sources/roles/orchestrator.md:116-122` y derivados; guardas 005-006 verdes |
| `make agents` **idempotente** | ✅ | 2ª corrida sin cambio de bytes (sha256 A == B, §4) |
| Las **guardas de texto** existentes siguen verdes | ✅ | §4: 148 passed + 28 passed, 2 skipped |
| Regla por **referencia**, sin copia ni documento nuevo | ✅ | cita `orientation.md` §1 + `project-start.md` §11; sin invocación CLI; sin archivo nuevo |
| **NO** se tocaron otros roles / despacho / resto del prompt | ✅ | `git diff --stat` acotado a 3 archivos (§5) |
| Invariante «no editar tests» | ✅ | `git status` no muestra cambios en `tests/**` |

## 3. Sentido del cambio (lo juzga la review, INV-5)

La entrada del orquestador quedó así, **por sentido**:
1. **`status` primero.** La primera acción de toda sesión es orientar por la vista compacta `status` de la skill `cdad-cycle` — la misma ruta breve y común que el Step 1 de las skills (T2) — citando a sus dueños (`orientation.md` §1, `project-start.md` §11) en vez de duplicar la regla.
2. **`resume` solo con ejecución activa.** `resume` ya no se presenta como el primer paso de toda sesión: queda como el paso **siguiente a la vista** y **solo** cuando hay una ejecución activa. Se conserva literal la rama «start from rest» / «never resume without an active execution».
3. **State completo solo ante una necesidad concreta.** Leer el state completo (o `state-detection.md`) deja de ser el primer paso y pasa a ser una ampliación condicional, gatillada por una necesidad concreta que afecte al siguiente despacho, con el motivo registrado.

## 4. Comandos y salida

**Baseline (antes del cambio), regresiones declaradas + guardas de texto:**
```
env -u TMPDIR python3 -m pytest -q \
  tests/test_005_006_t1_start_procedure.py \
  tests/test_005_009_t3_spawn_reconciliation.py \
  tests/test_005_010_t3_references.py \
  tests/test_cdad_generate.py \
  tests/test_packet_prepare.py \
  tests/test_005_006_t6_owner_reviewfix.py \
  tests/test_005_010_reviewfix.py \
  tests/test_003_007_t4_atomic_unit_rule.py < /dev/null
→ 94 passed in 38.25s
```

**Regeneración de derivados + idempotencia:**
```
make agents            # 1ª corrida (tras el cambio)
sha256sum agents/cdad-orchestrator.md agents/claude-code/cdad-orchestrator.md
  bd44dbf93734834860e9b4ca897ce23e5ed8f90e3108bca57f009130f97e0721  agents/cdad-orchestrator.md
  aac4269ce8df4b9b6dcf4250da80e158ab122f2a2f0a1929e46d3dbf365dfc55  agents/claude-code/cdad-orchestrator.md
make agents            # 2ª corrida
sha256sum agents/cdad-orchestrator.md agents/claude-code/cdad-orchestrator.md
  bd44dbf93734834860e9b4ca897ce23e5ed8f90e3108bca57f009130f97e0721  agents/cdad-orchestrator.md
  aac4269ce8df4b9b6dcf4250da80e158ab122f2a2f0a1929e46d3dbf365dfc55  agents/claude-code/cdad-orchestrator.md
diff A B → sin diferencias ⇒ IDEMPOTENTE (la 2ª corrida NO cambia bytes)
```

**Regresiones declaradas + guardas de texto que leen `sources/roles/orchestrator.md` o los derivados (tras el cambio):**
```
env -u TMPDIR python3 -m pytest -q \
  tests/test_005_006_t1_start_procedure.py \
  tests/test_005_009_t3_spawn_reconciliation.py \
  tests/test_005_010_t3_references.py \
  tests/test_cdad_generate.py \
  tests/test_packet_prepare.py \
  tests/test_005_006_t6_owner_reviewfix.py \
  tests/test_005_010_reviewfix.py \
  tests/test_003_007_t4_atomic_unit_rule.py \
  tests/test_003_006_t3_receive_wiring.py \
  tests/test_005_006_t2_intake.py \
  tests/test_005_004_t1_dispatch_tool_name.py \
  tests/test_005_004_t4_cc_guard_decisions.py \
  tests/test_004_002_t7_private_paths.py \
  tests/test_role_packet_consumers.py \
  tests/test_opencode_read_map_and_steps.py < /dev/null
→ 148 passed in 58.31s
```

**Regresión proporcional extra (procedencia / paridad de derivados, leen `agents/*.md`):**
```
env -u TMPDIR python3 -m pytest -q \
  tests/test_005_005_t3_provenance.py \
  tests/test_004_001_t7_pd10.py \
  tests/test_005_005_t2_docs_policy.py \
  tests/test_005_002_t4_acceptance.py < /dev/null
→ 28 passed, 2 skipped in 7.43s
```

Nota: una primera ubicación del bullet (entre `reconcile` y `resume`) rompió `tests/test_005_006_t2_intake.py::test_inv4_intake_never_resume_without_active_…` (INV-4(a): toda mención de `resume` en la ventana del intake debe quedar cualificada por la rama «sin ejecución activa → no resume» dentro de ±5 líneas; la línea de `reconcile` menciona «resume»). Se resolvió moviendo el bullet **Session entry** al frente del bloque (queda a ≤5 líneas de `reconcile`), sin duplicar la regla ni debilitar la guarda.

## 5. `git diff --stat` acotado (incluye derivados regenerados)

```
 agents/cdad-orchestrator.md             | 9 ++++++++-
 agents/claude-code/cdad-orchestrator.md | 9 ++++++++-
 sources/roles/orchestrator.md           | 9 ++++++++-
 3 files changed, 24 insertions(+), 3 deletions(-)
```

`docs/.cdad-state.json` aparece modificado en el working tree pero **NO** se commiteó: es el binding de despacho escrito por el orquestador (fuera del write_scope del implementer).

## 6. Commit

```
68044cb feat(005-011): T2b — la entrada comun del orquestador empieza por la vista status; resume como paso siguiente
3 files changed, 24 insertions(+), 3 deletions(-)
hash: 68044cba8fb935a4bdbe99abae9b3e2fe39c8261
```

Sin `--no-verify`; sin `git stash`; sin push; sin desplegar.
