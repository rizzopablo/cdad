# SPEC — cdad-001-validate-subagents

> Spec-first. Estado: DRAFT (bootstrap 03 Ago 2026).
> Postcondición + formato mínimo + tests ANTES del build.
> El build del script se hace con el ciclo CDAD (task_plan Phase 4, task 4).

## 1. Contexto

Phase 4 del repo cdad: validar que la delegación vía sub-agentes nativos
(`subagent_type: cdad-<rol>`) funciona end-to-end. Para eso se construye una
mini-feature de validación recursiva: el propio repo cdad se valida a sí mismo
con su ciclo CDAD (CDAD recursivo).

**Trigger resuelto (03 Ago 22:47):** opencode server corriendo desde 13:11
(post-install agents 05:20) — `/config` del server vivo muestra 5/5 cdad agents
cargados. `install.sh --check` 11/11 PASS. Byte-compare 5/5 agentes IDENTICAL.

## 2. Postcondición (definición de done)

Después de ejecutar el ciclo CDAD para esta mini-feature, DEBE existir:

```text
scripts/validate-subagents.sh
```

Y al ejecutar:

```bash
bash scripts/validate-subagents.sh
```

DEBE:

1. **Retornar exit 0** si y solo si todas las verificaciones pasan
   (exit != 0 ante cualquier falla, con mensaje claro de qué falló).
2. **Leer los agentes de los directorios de instalación runtime**
   (no del repo): `$HOME/.config/opencode/agents/cdad-*.md` —
   fallback documentado si el path runtime no existe.
3. **Cross-checkar contra el repo** reutilizando `install.sh --check`
   (repo es la única fuente de verdad).
4. **Producir/enumerar artefactos por etapa** en
   `docs/specs/cdad-001-validate-subagents/artifacts/`:
   - `spec.md` — la spec de la etapa (architect)
   - `tests/` — tests de la etapa (test-writer)
   - `impl.diff` — diff de implementación (implementer)
   - `review.md` — review con **declaración de modelo del reviewer**
   - `memory-bank.md` — entry de memory bank (scribe)
5. **Imprimir un resumen por etapa** en stdout:
   `[etapa] artefacto -> OK/FAIL`.

## 3. Formato mínimo de artefactos

### 3.1 `spec.md`
- `# SPEC — <nombre>` en la primera línea
- Sección `## 2. Postcondición` con criterios verificables
- Sin secciones vacías

### 3.2 `tests/`
- Al menos 1 archivo de test por criterio de la postcondición
- Los tests corren sin red (offline, stdlib o pytest)

### 3.3 `impl.diff`
- Formato unified diff (`diff -u` o `git diff`)
- Debe ser aplicable: `git apply --check --reverse` (ya aplicado) o `git apply --check` (aún aplicable) exit 0
- **Nota (05 Ago, review cdad-001):** divergencia documentada con el criterio literal `patch -p1 --dry-run`: `patch --dry-run` falla con diffs de creación ya aplicados (el archivo ya existe en el working tree), mientras `git apply --check --reverse` distingue correctamente "ya aplicado" de "aún aplicable". T4 usa el criterio robusto de `git apply` para ser consistente con el validator.

### 3.4 `review.md`
- DEBE contener la línea exacta:
  `Reviewer model: <modelo>` (declaración de modelo del reviewer)
- Secciones: `## Hallazgos`, `## Veredicto: PASS|FAIL`

### 3.5 `memory-bank.md`
- Entry con: fecha, qué se validó, resultado, fricciones (si hubo)

## 4. Criterios de aceptación (tests, escritos antes del build)

Los siguientes tests DEBEN pasar contra el script construido.
Viven en `tests/` de esta spec (bootstrap) y se ejecutan con:

```bash
cd docs/specs/cdad-001-validate-subagents && bash tests/run_all.sh
```

### T1 — exit 0 con entorno válido
- Setup: agentes runtime presentes (los 5 cdad-*), install.sh --check OK.
- Assert: `bash scripts/validate-subagents.sh; echo $?` → `0`.

### T2 — exit != 0 si falta un agente runtime
- Setup: mover temporalmente `cdad-reviewer.md` fuera del dir runtime.
- Assert: exit != 0 Y stdout menciona `cdad-reviewer`.

### T3 — cross-check contra repo
- Setup: entorno válido.
- Assert: el output incluye el resultado de `install.sh --check`
  (se reusa; no se duplica lógica).

### T4 — artefactos por etapa
- Setup: entorno válido.
- Assert: existen los 5 artefactos en `artifacts/` con formato mínimo
  (spec.md con `## 2. Postcondición`, tests/ no vacío, impl.diff
  aplicable, review.md con línea `Reviewer model:`, memory-bank.md con fecha).

### T5 — idempotencia
- Setup: correr 2 veces seguidas.
- Assert: exit 0 en ambas, sin errores de "ya existe" (overwrite o skip limpio).

## 5. Anti-scope (NO entra en esta iteración)

- ❌ No es un framework genérico de validación de sub-agentes.
- ❌ No toca config de modelos (bailian/opencode.jsonc).
- ❌ No modifica los 5 agentes ni sus permisos.
- ❌ No hace deploy ni toca infraestructura externa.

## 6. Riesgos

| Riesgo | Mitigación |
|--------|-----------|
| opencode server no disponible al correr el ciclo | validate-subagents.sh valida config estática (frontmatter en Etapa 1 + byte-compare vía `install.sh --check` en Etapa 2), no requiere server vivo para T1-T5 |
| Paths runtime varían por máquina | `$HOME/.config/opencode/agents/` con fallback a `$(dirname install.sh)/agents/` |
| El ciclo CDAD real (task 4) depende de modelos bailian | Los tests T1-T5 son offline; la dependencia de red queda solo en el ciclo de build |

## 7. Decisión

- **Apuesta:** BET (Phase 4 del repo, appetite ~2-3 ciclos del orquestador).
- **Status:** spec bootstrap ✅ — esperando ciclo CDAD (task 4).
