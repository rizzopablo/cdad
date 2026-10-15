# Review formal (etapa 4) — 005-008-project-path-capabilities

**Paquete:** 005-008-project-path-capabilities-reviewer-review-001 · **Rol:** reviewer (read-only)
**Contrato aprobado:** docs/specs/005-008-project-path-capabilities/spec.md (sha256 849c6201…62 ✓ verificado contra el archivo materializado)
**Diff revisado:** `git diff 3fb1e91..HEAD` — 5 archivos: skills/cdad-cycle/scripts/cdad_packet.py (commits 17e6184 +9, 8500bf4 +10/−2), tests/test_005_008_t1_nested_tests.py (17d5f9c), test_005_008_t2_language_commands.py (aff3a20), test_005_008_t3_acceptance.py (54fb376), docs/.cdad-state.json.
**Modelo reviewer:** mofgw/glm-5.3-flash (≠ familia/variante del implementer deepseek — anti-bias).

---

## Veredicto

**PASS (sin bloqueantes).** La implementación satisface las postcondiciones PD-1..PD-11 de la spec aprobada por comportamiento observable; los tests están mapeados 1-a-1 sin superfluos, el RED es genuino y verificado por corrida propia, no hay regresiones ni cambios de paridad. Se listan hallazgos opcionales y abstenciones declaradas abajo.

## Evidencia de verificación (comandos propios, read-only)

| Verificación | Comando | Resultado |
|---|---|---|
| Spec pin | sha256sum docs/specs/…/spec.md | 849c6201…62 == packet ✓ |
| Suite completa (primer plano) | `python3 -m pytest tests/ -q` | **1 failed, 700 passed in 925.82s** (única falla: preexistente/ambiental, ver abajo) |
| make validate | `make validate` | 141 PASS / **2 FAIL** (ambas preexistentes/ambientales, ver abajo) |
| Focal 005-008 en HEAD | `pytest tests/test_005_008_t{1,2,3}*.py -q` | **16 passed in 60.87s** |
| RED T1 genuino | worktree 17d5f9c + focal | **3 failed / 6 passed**; las 3 fallas son `AssertionError: 'deny' != 'allow'` de comportamiento (PD-1, PD-5, PD-6 control-hermano). 0 ImportError/Syntax |
| RED T2 genuino | worktree aff3a20 + focal | **1 failed / 1 passed**; AssertionError `'commands' not found in 'ERROR: policy fields do not match schema…'` (diagnóstico genérico = defecto) |
| Tests no debilitados | diff test-files RED→HEAD | **byte idénticos** (0 diff) en los tres archivos |
| Paridad guard CC | `git diff 3fb1e91..HEAD -- scripts/claude-code-path-guard.sh` | **0 líneas** (sin cambios) |
| Paridad resto de skills | `git diff 3fb1e91..HEAD -- skills/ (excl. cdad_packet.py)` | **0 líneas**; clasificador `classify_path` sin hunks (diff solo toca `_validate_policy_document`, `_test_patterns`, `_derived_maps` rama read) |
| HOME intocado (INV-9) | cat ~/version.txt | `35062b0…` (mtime 11:13, anterior al ciclo) |
| Atribución falla suite | worktree 3fb1e91 + build/staging local | misma falla `review5_b4` reproduce en base → preexistente |
| Atribución validate odoo | worktree 3fb1e91 + .sensitive-patterns.local copiado | A3 falla igual en base → preexistente |

## Fidelidad PD-1..PD-11 / INV-1..INV-9

**Producto (cdad_packet.py, 3 hunks únicos):**
- D1: `_test_patterns` ahora incluye `path_policy["test_files"]` literales (PD-5, PD-4-paridad) — cdad_packet.py:2602-2607.
- D2: rama `read` del test-writer: deny de implementación → allow de `_test_patterns` → allow de co-ubicados → `private` al final (PD-1, PD-6/INV-2, findLast) — :2656-2662. `edit` del implementer consume la misma fuente (PD-4).
- PD-10(b): `_validate_policy_document` nombra `unknown field(s): X` / `missing field(s): Y` conservando el fail-closed (`PolicyError`, schema exacto de 3 campos) — :417-428 (INV-5, D4).

**Cobertura tests↔postcondiciones (sin superfluos, sin frases de prompt, sin nombres internos, sin mocks de plumbing):** T1 = 9 tests ↔ PD-1..PD-9 uno a uno; todo por subprocess sobre `prepare` + derivados publicados + oráculo findLast único (`pd10_permission_semantics.verdict` reutilizado por import) + guard CC forma-real como control. T2 = 2 tests ↔ PD-10(a) Makefile-lock y PD-10(b) diagnóstico nombrado (+ control de política exacta y no-cambio silencioso byte-a-byte). T3 = 5 tests ↔ PD-11 (positivas/negativas sobre el PRODUCTO INSTALADO, `install.sh --basic` con `CDAD_INSTALL_ROOT` en tempdir, skip limpio honesto) + W-2. La prosa PD-10(c/d) verificada por review: (c) el puntero existe en `stage-3-tdd.md` §«Test evidence policy» punto 4 («el proyecto declara los comandos», sin duplicación); (d) nada se instaló ni operó en producción (HOME intacto, sin intérprete/runner instalados).

**INV-3/PD-7:** se reabren solo árboles/archivos declarados (nunca `**/t/**`, `**/*.t`); sondas de convención global barridas por `undeclared_convention_rules` en todos los derivados. **INV-4/PD-9:** grep/glob sin entradas por ruta en todos los derivados (helper W-2 de T5). **INV-6:** declarado honestamente en T3 (grep/shell/sesión separada no son sandbox); sin allowlists por comando. **INV-7:** no se implementó el consumidor Perl ni agentes manuales. **INV-8:** clasificador, guard CC, esquema de manifiesto y publicación atómica sin cambios (diff lo confirma). **INV-9:** epic-005 plan/execution sin cambios en el rango; HOME/producción reservados y intocados.

## Preexistentes no atribuibles al diff (evidencia)

1. **Suite: `test_review5_b4_basic_request_vs_staging_profile_labels_coherent` FAIL (1/701).** La precondición exige staging con perfil ≠ `basic`; `product_root()` reutiliza el `build/staging/` real (gitignored; `manifest.json` con `profile=basic`, mtime 2026-10-10 **11:14**, anterior a todos los commits del diff 12:1x+). La falla idéntica reproduce en el worktree de la base con el mismo build/staging. El diff no toca install.sh ni staging ni esta test-suite.
2. **make validate: F011 `validate-subagents.sh` FAIL** → `install.sh --check` reporta DRIFT de `__pycache__/*.pyc` ausentes en `~/.claude/skills/...` (deriva del HOME del dueño; falla también en base). **F011 `validate-odoo-specialization.sh` FAIL (A3)** → patrones sensibles en docs/specs/004-003-planning-procedures/*, tests/test_role_packets.py (+ un .pyc regenerado por corridas); reproduce igual en base con el mismo entorno; archivos ajenos al diff.

## Opcionales (NO prolongan el ciclo)

- **O-1 — Registro del dueño pendiente (spec §10 / criterio §4):** VERIFY 1, 3, 5 y 6 del discovery «se cierran o se declaran en la aceptación (T3) con el dueño». La entrada de state `tdd-t3-acceptance` registra el recorrido aislado (5/5) con límites honestos, pero no la declaración/cierre con el dueño (layout/política real del consumidor, mediación viva, dominio, comandos Perl del consumidor). Cierre verificable: en stage 5, registrar en state la declaración/cierre o la no-cierre con el dueño de los VERIFY 1/3/5/6.
- **O-2 — Inventario de superficie incompleto (trazabilidad):** spec §2 y plan T1 «Files» no listan `_validate_policy_document`, y el plan T2 «files» no incluye cdad_packet.py, aunque PD-10(b) exige el diagnóstico nombrado (cambio de producto necesario e implementado en 8500bf4). Cierre: errata/nota en Memory Bank (spec-errata) declarando la superficie real de T2; sin cambio de código.
- **O-3 — Estado local de staging:** `build/staging` (gitignored) quedó con `profile=basic`, lo que mantiene en rojo el 1 test de instalación y (con el A3)ική parte de validate. Cierre: regenerar staging con el perfil por defecto (`make staging`) o aislar `product_root()` del estado del checkout — decisión del dueño, fuera de este diff.
- **FYI:** el commit T3 se llama «T3 RED» aunque sus tests pasan de inmediato (plan T3: «GREEN es de los cambios de T1») — registrado honestamente en el state como LOCK.

## Abstenciones declaradas

- **A-1:** No verifiqué la mediación en vivo de un proceso OpenCode real (VERIFY 3): los tests declaran honestamente ese límite; la evidencia viva con el dueño es ítem de cierre (O-1).
- **A-2:** No leí `tests/.sensitive-patterns.local` (ruta privada prohibida por el plan); la reproducción A3 usó el validador que sí lo lee — no su contenido.
- **A-3:** No releí el paquete `implementer-green-003` (fuera de mis inputs declarados); el hallazgo O-2 se basa solo en plan aprobado vs diff.
- **A-4:** La suite total tomó 925.82s en esta ventana (dos corridas totales con la misma única falla) — la cifra reportada es de la corrida completa en primer plano de esta revisión, no estimación.
