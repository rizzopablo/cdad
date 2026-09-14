# Active Context

Estado actual del proyecto. Cada feature cerrada agrega una entry. Las entries más recientes arriba.

---

## 2026-09-13 — Feature: cdad-010-opencode-permissions

Cerrada la feature que reparó la delegación a los sub-agentes `cdad-*` en
OpenCode (rota por interacción de 3 capas: clasificador del plugin que ignora
allows específicas, huecos de allowlist + wrapper rtk, y el hack `write: ask`
top-level inerte). 10 agentes task-ables (5 base + 5 odoo), bloques de
permisos autocontenidos (catch-all primero, específicas después — semántica
findLast), cero `ask` en runtime (fail-fast deny), allowlists bash por rol con
pares `X*`/`rtk X*` derivadas del stack detectado (`scripts/cdad-bash-allowlist.sh`
+ `install.sh`, P5), docs de delegación corregidos (P6) y ADR-009. Copia
huérfana `cdad-test-writer-local.md` (fuera del repo, filtraba a `src/`)
eliminada.

Decisiones clave:
- **Palanca anidada, no top-level (enmienda P1):** `permission.write: ask`
  dentro del bloque `permission:` — el KNOWN_KEYS del clasificador no incluye
  `write` top-level (probe: palanca top-level inerte, agente colapsa a
  read-only y `task` lo rechaza); anidada, el clasificador la lee y el runtime
  NO la evalúa (cero `permission=write` en 124MB de logs). La enmienda nace de
  una desviación registrada: el commit `5f9f4d2` mezcló el fix de agentes con
  la edición del assert A1 de run-checks.sh fuera de rol (AP-4) — bajo la
  política del dueño queda como precedente: violación así futura = tarea NO
  cumplida.
- **Eliminación de `"find *": allow` (H3):** vector directo de
  escritura/ejecución (`find -delete`, `-exec sh`) en los 6 roles read-only
  cuya allowlist declara "solo lectura". Navegación preservada (`ls *`, `wc *`,
  `pwd`, `cd *`, pares `rtk find*` en lectores).
- **Política de enforcement del dueño (Capa 2, Pablo):** bloquear vectores
  directos y evidentes, no bypasses hipotéticos; la expectativa se documenta en
  skills/procedimientos; agente que cumple violando el protocolo sin motivo
  válido = tarea NO cumplida. Definición operativa (N3): "vector directo y
  evidente" = demostrable con un probe de una sola invocación con output
  pegado (Regla de Oro) — el episodio N1 lo demostró: dos sesiones dieron
  veredictos opuestos sobre el mismo matcher y el que tenía probes pegados
  tenía razón.

Estado final: run-checks.sh 217 PASS / 0 FAIL (RED 42/132 → 174/0 → 184/31 →
215/0 → 217/0 con assert de orden findLast N2), 3 validadores en PASS
simultáneo, matriz de probes G1-G16 ejecutada post-restart desde sesión
primaria con evidencia pegada (G9 con enmienda justificada: `go version`
DENEGADO es diseño correcto; G14 con re-test tras misreport del modelo), cero
prompts `ask` y cero `permission=write` en logs, review APROBADO-COMENTARIOS
(2 pasadas). Commits: rango `b352bf6..a1d37a7` (27 commits; highlights:
`f36f8c7` P1-P4, `b0027bd` P5, `5f9f4d2` palanca anidada, `a45219c` fixes
H3/H4, `a1d37a7` N2).

Pendiente (bucket de hardening, NO fixeado acá):
- Re-evaluación de matching de comandos compuestos con la premisa corregida
  (N1: el matcher evalúa por segmento — `cd X && <arbitrario>` NO bypassa; el
  "hardening de matching" original probablemente ya no es necesario).
- `"find *": allow` en la config global del usuario (`opencode.jsonc`) —
  misma clase que H3, fuera de alcance por invariante de no-modificación (N4).
- Solape de globs de dominio Odoo (intersección entre globs odoo y globs
  genéricos de tests colocados en las variantes) — revisar en hardening.

---

## 2026-09-04 — Fix: path-guard reconoce tests colocados (sin ciclo formal)

Fix en `scripts/claude-code-path-guard.sh` (commit `0fd023f`), detectado en
un proyecto cliente (backend Go + extensión JS) y reportado por Pablo. El
guard asumía tests en
`tests/**` dedicado, pero Go EXIGE tests en el mismo paquete/directorio
(`*_test.go`, requisito del compilador) y JS/TS coloca `*.test.{js,ts}`
junto al módulo. Consecuencias corregidas en AMBOS lados:

- **test-writer-write / test-writer-odoo-write**: la allowlist de escritura
  ahora acepta tests colocados (`**/*_test.go`, `**/*.test.{js,ts,mjs,cjs}`,
  `**/*.spec.{ts,js}`, `**/test_*.py`), además de `tests/**` y `**/tests/**`.
  Sin esto, el rol quedaba sin NINGÚN path escribible en un repo Go.
- **implementer / implementer-odoo** (lado inverso, no reportado — detectado
  en revisión): la blocklist ahora incluye los mismos patrones. Sin esto, el
  implementer podía editar tests colocados y romper silenciosamente el gate
  anti-trampa.
- **test-writer-read**: excepción de lectura para tests colocados bajo
  `src/**`/`lib/**` (el test-writer debe poder leer la suite que edita).
- **Factorización**: array `TEST_FILE_GLOBS` + `is_test_file()` como fuente
  única usada por ambos lados.

Verificación: batería de 19 casos por rol (bloqueos/permisos, ambos layouts,
variantes Odoo) — 19/19 PASS. Copia instalada (`~/.claude/cdad-scripts/`)
redesplegada e idéntica a la canónica.

**Deuda de proceso (documentada, no oculta):** el fix se aplicó inline y
antes del spec — bypass del ciclo CDAD (Pablo pidió ciclo light a mitad de
camino; se decidió no retroactivar y solo documentar). La batería de 19
casos no vive como test permanente en `tests/` — si el guard vuelve a
tocarse, incorporarla como RED formal de esa feature.

## 2026-09-02 — Epic: epic-002-cdad-audit-fixes (12 features, cerrado)

Cerrado el epic que corrige los hallazgos de
`findings/audit-consistencia-2026-09-02.md` (auditoría completa de
metodología, agentes OpenCode/Claude Code y skills, pedida por Pablo).
Delegación HITL explícita para todo el epic (spec approval, priorización,
Memory Bank) — ver `docs/.cdad-state.json` campo `hitl_delegation`.

Decisiones relevantes:
- **B1 (bash como fuga del aislamiento)**: calibrado como defensa en
  profundidad, no reescritura estricta — decisión explícita de Pablo antes
  de ejecutar: *"la combinación de barrera estructural parcial + conductual
  está funcionando bastante bien"*. La allowlist de bash cierra la fuga de
  contenido (cat/head/tail/rg) preservando TODO lo legítimo (tests, lint,
  git commit propio, navegación) — ningún rol perdió capacidad real.
- **Perfil `basic`**: es el más usado por Pablo (costo de tokens) y su
  comportamiento NO cambió — el fix fue puramente documental (dejar de
  afirmar el anti-bias como garantizado ahí, cuando ADR-007 ya documentaba
  la excepción).
- **RED verifica requerimiento, no cobertura**: refuerzo explícito pedido
  por Pablo — un test-writer no debe sobre-especificar más allá del spec
  (tests carísimos/imposibles de satisfacer, tiempo y tokens perdidos).
  Agregado a SKILL.md, stage-3-tdd.md, y a los 4 agentes test-writer.

Deuda técnica detectada:
- Esta misma entry es la primera desde cdad-004 (2026-09-02) —
  activeContext.md no tenía entries para cdad-005..009 pese a estar `done`
  en progress.md. No se backfillea acá (fuera del scope de este epic); si
  hace falta detalle de esas 5 features, está en sus commits y en
  `docs/epics/epic-001-superpowers-gaps/closure.md`.
- Deuda ya registrada sin cambios: CI del repo, dogfood pendiente de varias
  features (ver progress.md Queued).

Próxima feature en cola: ninguna decidida — Pablo define.

## 2026-09-02 — Feature: cdad-004-lint-gate

Cerrada feature que incorpora `make lint` (pre-commit-vauxoo) como 4º target
del contrato odoo-make-env y como evidencia obligatoria en review/gates Odoo.

Decisiones relevantes:
- Lint con `uvx pre-commit-vauxoo==8.3.18`, SIEMPRE `--no-overwrite` (la
  bootstrap de configs es del proyecto, nunca del agente), corre en host,
  autofixes deshabilitados.
- El lint es evidencia mandatory en review Odoo; los hallazgos W/C siguen
  advisory (split mandatory/advisory intacto).
- Fix colateral: assert stale de cdad-003 (odoo-dev-methodology retirado en
  d9dc599, test nunca actualizado) → `assert_file_not_has`.

Deuda técnica detectada:
- CI inexistente en este repo (suite bash local hace de gate) — registrar en
  progress.
- H3/dogfood: `make lint` sin validar end-to-end contra un addon Odoo real.
- Runtime `delegate` (read-only) falló 8/8 por timeout en esta sesión —
  revisar infraestructura antes del próximo epic.

Próxima feature en cola: epic `superpowers-gaps` (5 features, orden
propuesto: G1 recepción de feedback → G5 git safety → G3 debugging → G4
planning → G2 despacho paralelo).

## 2026-09-02 — Bootstrap del proyecto

Memory Bank inicializado durante el cierre de cdad-004-lint-gate (primera
feature del repo con ciclo CDAD completo: spec → RED 10/10 → GREEN → review
two-layer → merge).

Pendientes para completar manualmente:
- CI del repo (GitHub Actions) — deuda registrada en progress.md.
