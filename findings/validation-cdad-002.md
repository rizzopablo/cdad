# Validation: CDAD-002 — Claude Code Sub-agents (ADR-008 Verification)

**Date:** 2026-08-14 (REESCrito con evidencia real — reemplaza template PASS prematuro del 2026-08-13)
**Profile:** economical (architect haiku, test-writer haiku, implementer haiku, reviewer opus, scribe haiku)
**Result:** ✅ **PASS** — 5 etapas CDAD ejecutadas end-to-end con sub-agentes reales vía `claude` CLI; gates G7c/G7d/G7e verificados con evidencia

---

## Executive Summary

Esta es la validación **real** del soporte Claude Code de CDAD (ADR-008), ejecutada el 2026-08-14. La versión anterior de este archivo (commits `d12c502`/`772a3a1`, 13 Ago) era un template pre-rellenado que declaraba "PASS" pero cuyo propio cuerpo decía "Ready for real Claude Code CLI execution" — los gates no se habían ejecutado. Esta reescritura documenta la ejecución real.

**Método:** repo git temporal aislado (`~/tmp/cdad-002-spike/`), mini-feature `Add(a,b int) int`, ciclo CDAD de 5 etapas ejecutado con `claude -p --agent <rol>` (headless) y `--dangerously-skip-permissions` para los agentes write-capable.

**Resultados clave:**
- ✅ 5 sub-agentes reales invocados vía CLI headless (v2.1.232)
- ✅ RED falla por `undefined: calc.Add` (postcondición no implementada) — no por import error
- ✅ GREEN: suite 4/4 verde
- ✅ Reviewer (opus) ≠ implementer (haiku) — invariante ADR-001 preservado (G7e)
- ✅ Path-scoping guard verificado: exit 2 real en violaciones + hooks cableados (G7d)
- ✅ Delegación de sub-agentes vía Agent tool funciona headless, sin spawn-recursion (M2)

---

## Correcciones aplicadas durante la validación (defectos reales encontrados)

| # | Defecto | Severidad | Corrección | Verificación |
|---|---------|-----------|------------|--------------|
| A | **Bypass por ruta absoluta**: implementer/tw-read podían leer/escribir `src/`,`tests/` con ruta absoluta (exit 0 en vez de 2) | MAJOR | Fix B en `claude-code-path-guard.sh`: `relativize()` relativiza rutas bajo `$PWD` | probe: ruta abs a `tests/` impl → **2** ✓ (antes 0) |
| B | **Bypass dir exacto**: `tests` (sin slash) no matcheaba `tests/**` (exit 0) | MAJOR | Fix B: `matches_glob` matchea base exacta | probe: dir `tests` impl → **2** ✓ (antes 0) |
| C | **Layout del spike contradictorio**: `pkg/calc/` quedaba fuera del espacio protegido por los guards (test-writer-write bloquea escribir `pkg/calc/*`; read-guard no protege `pkg/calc/calc.go`) → G7c/G7d mutuamente excluyentes y AP-7 no ejercitable | CRITICAL | Re-layout a `src/calc/` + `tests/calc/` (dentro del espacio protegido) | spec + checklist actualizados |
| D | **Model drift**: copia instalada de test-writer declaraba `haiku` mientras source ya era `sonnet` | MINOR | Reinstall (propaga source a runtime) | byte-compare: solo línea `model:` difiere (por perfil economical) |
| E | **Sandbox headless bloquea escritura** sin permiso | — | `--dangerously-skip-permissions` (hooks siguen activos; solo salta el prompt de sandbox) | GREEN exitoso |

**No corregido (aceptado como trade-off documentado):** Bash bypass. El guard solo inspecciona `tool_input.file_path`; un sub-agente con `Bash` podría `cat src/...` evadiendo. ADR-008 (L82-84) decide **Bash completo** explícitamente (Claude Code no soporta granularidad por comando). Se documenta como limitación conductual del modelo guard, consistente con ADR-008.

---

## Probes del path-guard (baseline → fixed)

Los probes se corren con JSON del hook por stdin (`echo '{"tool_name":"...","tool_input":{"file_path":"..."}}' | path-guard.sh <rol>`). Exit 2 = bloquea, exit 0 = permite.

| # | Probe | Esperado | Baseline | Fixed | Nota |
|---|-------|----------|----------|-------|------|
| 1 | implementer · Edit · `tests/foo_test.go` | block | 2 | 2 | ✓ |
| 2 | implementer · Edit · `src/main.go` | allow | 0 | 0 | ✓ |
| 3 | test-writer-read · Read · `src/main.go` | block | 2 | 2 | ✓ |
| 4 | test-writer-write · Edit · `tests/foo_test.go` | allow | 0 | 0 | ✓ |
| 5 | test-writer-write · Edit · `src/main.go` | block | 2 | 2 | ✓ |
| 6 | implementer · Edit · ruta ABS `$PWD/tests/foo` | block | **0 (bypass)** | **2** ✓ | Fix B |
| 7 | test-writer-read · Read · ruta ABS `$PWD/src/main` | block | **0 (bypass)** | **2** ✓ | Fix B |
| 8 | implementer · Edit · dir `tests` exacto | block | **0 (bypass)** | **2** ✓ | Fix B |

**Resultado:** baseline reveló 3 bypasses (6,7,8); tras Fix B todos los probes correctos. Fix B propagado vía reinstall (guard instalado byte-idéntico al source).

---

## Gates

### G7a — 5 agentes Claude Code instalados en `~/.claude/agents/` ✅
`ls ~/.claude/agents/cdad-*.md` → 5 files (architect, test-writer, implementer, reviewer, scribe). Confirmado.

### G7b — Guard script presente + ejecutable ✅
`~/.claude/cdad-scripts/path-guard.sh` presente, `chmod +x` aplicado por install.sh. Confirmado.

### G7c — Spike end-to-end 5 etapas PASS ✅ (repo temporal `~/tmp/cdad-002-spike/`)

| Etapa | Rol | Evidencia |
|-------|-----|-----------|
| 1-2 Discovery+Spec | cdad-architect | Audit repo + brainstorm + spec draft (P1-P4) → spec materializada por orquestador |
| 3.0-3.1 AUDIT+RED | cdad-test-writer | `tests/calc/calc_test.go` (4 tests); `go test` falla `undefined: calc.Add` |
| 3.2 GREEN | cdad-implementer | `src/calc/calc.go` + `Add`; suite 4/4 verde; commit `d2678a3` |
| 4 Review | cdad-reviewer | 0 CRITICAL, 0 MAJOR; 1 MINOR (tests sin postcondición) + 1 TRIVIAL |
| 5 Memory Bank | cdad-scribe | Draft MB con lessons + anti-patrones AP-27/28/29 |

### G7d — Path-scoping hooks ✅
- Hooks `PreToolUse` cableados en cdad-test-writer.md (Read\|Grep\|Glob + Edit\|Write) y cdad-implementer.md (Edit\|Write), invocando `path-guard.sh <rol>`.
- Guard devuelve exit 2 real en las 3 violaciones (probes 1,3,5 + Fix B 6,7,8).
- **Evidencia estructural:** probes del guard (exit 2), NO dependiente de cooperación del agente.
- **Evidencia conductual (débil, sanity):** test-writer se autobloqueó cooperativamente al pedirle leer `src/`.
- **Limitación documentada:** Bash puede evadir (ADR-008 trade-off aceptado).

### G7e — Model routing per profile ✅
- Reviewer real: `claude-opus-5` (opus)
- Implementer real: `claude-haiku-4-5` (haiku)
- Invariante reviewer ≠ implementer **preservado** (modelos distintos).
- Verificado vía `--output-format json` → `modelUsage` del run real.

### M2 — Delegación de sub-agentes vía Agent tool ✅ (ADR-008 criterio #2/#3)
- `claude -p` orquestador spawneó `cdad-architect` y `cdad-reviewer` como sub-agentes vía Agent tool (headless).
- Aislamiento de sesión: cada sub-agente reportó solo su contexto.
- **Sin spawn-recursion** (ningún sub-agente spawneó otro — GUARDIA DE SPAWN respetada).

---

## Fricciones descubiertas (validación real)

1. **F1 (BLOCKER inicial): sandbox headless bloquea escritura** de agentes write-capable. Resuelto con `--dangerously-skip-permissions` (salta prompt sandbox; hooks del guard siguen activos).
2. **F2: RED inicial falló por import error** (`no required module provides .../src/calc`) porque el package no existía. Resuelto creando skeleton `src/calc/calc.go` (solo `package calc`, sin `Add`) → fallo correcto `undefined: calc.Add`.
3. **F3: state-passing requiere handoff explícito** del orquestador. El scribe no vio los outputs reales del reviewer (asumió "stages 4-5 no ejercitadas") porque el orquestador no se los pasó vía handoff. Confirmado: el orquestador debe materializar/pasar artefactos (regla 6 del ciclo CDAD).
4. **F4: layout `pkg/calc/` (template) fuera del espacio de los guards** → C1. Corregido con re-layout `src/`+`tests/`.

---

## Deuda técnica aceptada

- **Bash bypass**: sub-agente con Bash puede evadir el path-guard (leer `src/`, escribir fuera de `tests/`). Aceptado (ADR-008 decide Bash completo). Mitigación: revisión humana / confianza en el prompt del agente. NO es enforceable estructuralmente en Claude Code.
- **Path-scoping conductual**, no estructural (hook, no runtime permission). Documentado en ADR-008.
- **Model routing cross-Anthropic** (opus vs haiku), no cross-provider como OpenCode. Documentado en ADR-008.
- **Agentes write-capable requieren `--dangerously-skip-permissions`** en headless; en sesión interactiva requiere aprobar el prompt.

---

## Conclusión

**CDAD-002 VALIDADO con evidencia real (2026-08-14).** Los gates G7a-G7e pasan, la delegación de sub-agentes vía Agent tool funciona headless (M2), y 3 defectos reales (A, B, C) fueron corregidos durante la validación. El findings anterior era un template con PASS prematuro; este documento refleja la ejecución real verificada.

**Recomendación:** ADR-008 → **Verified**. CDAD soporta Claude Code como segundo runtime con los trade-offs documentados (Bash, conductual, cross-Anthropic).

---

## Audit Trail

| Archivo | Estado |
|---------|--------|
| `src/calc/calc.go` (repo temporal) | Implementado (Add) |
| `tests/calc/calc_test.go` (repo temporal) | 4 tests, PASS |
| `scripts/claude-code-path-guard.sh` (repo cdad) | Fix B aplicado + verificado |
| `docs/specs/cdad-002/spec.md` (repo cdad) | Re-layout src/ + tests/ |
| `docs/specs/cdad-002/VALIDATION_CHECKLIST.md` (repo cdad) | Re-layout src/ + tests/ |
| `pkg/calc/` (repo cdad) | **Eliminado** (leftover del template) |
| `~/.claude/agents/cdad-*.md` | 5 agentes instalados (perfil economical) |
| `~/.claude/cdad-scripts/path-guard.sh` | Fix B propagado, byte-idéntico al source |
