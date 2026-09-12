# VALIDATION — cdad-010-opencode-permissions

> Fecha: 2026-09-12 · Evidencia empírica pegada, no descrita (Regla de Oro).

## Baseline RED (pre-implementación)

### 1. Probes de runtime del 2026-09-12 (sesión primaria, pre-fix)

Estos probes SON el RED de la capa empírica (fallas verificadas del estado
actual). Output pegado de la sesión:

```
task → cdad-test-writer:
❌ Agent 'cdad-test-writer' is read-only and should use the delegate tool
   for async background execution.

task → cdad-test-writer-local (probe de permisos):
PROBE-1 go version: DENEGADO permiso
PROBE-2 gofmt --help: PERMITIDO con output
PROBE-3 rtk go version: DENEGADO permiso
PROBE-4 pwd: PERMITIDO con output
PROBE-5 write tests/__cdad_probe__.md: PERMITIDO
PROBE-6 write src/__cdad_probe__.ts: PERMITIDO   ← FUGA (P2 violada hoy)

task → cdad-implementer (probe de permisos):
PROBE-A write tests/__cdad_probe2__.md: DENEGADO  (correcto — regla del agente gana)
PROBE-B go version: DENEGADO permiso              (allowlist sin go)
PROBE-C pytest --version: DENEGADO permiso        (el modelo corrió 'rtk pytest --version')
```

Evidencia de log (runtime, `~/.local/share/opencode/log/opencode.log`):
- `evaluated permission=edit pattern=src/__cdad_probe__.ts action.pattern=* action.action=allow`
  → el hueco lo llenó el `edit: {"*": "allow"}` GLOBAL de `opencode.jsonc`.
- `evaluated permission=edit pattern=tests/__cdad_probe2__.md action.pattern=tests/** action.action=deny`
  → la regla del agente GANA sobre el global (findLast, merge [global..., agente...]).
- `evaluated permission=bash pattern="rtk pytest --version" action.pattern=* action.action=deny`
  → el wrapper rtk no matchea `pytest*` (P4 violada hoy).
- Cero evaluaciones `permission=write` en 124MB de logs → la clave `write:`
  es solo de clasificación (base de la palanca P1).

### 2. Capa estática: run-checks.sh en RED

```
$ bash docs/specs/cdad-010-opencode-permissions/run-checks.sh
RESULTADO: 42 PASS, 132 FAIL
```

Fallas esperadas: A1 (write: ask ausente), A2 (catch-all ausente/ask),
A3/A4/A5/A6 (pares rtk, denies, globs), A7 (generador inexistente),
A8 (docs sin actualizar), A10 (2 validadores en FAIL preexistente).

### 3. Fallas PREEXISTENTES (no de cdad-010, corregidas post-audit)

- `scripts/validate-subagents.sh` → FAIL: `install.sh --check` rechaza
  `~/.config/opencode/agents/cdad-architect.md` — las copias instaladas
  driftaron del repo (enmiendas 02-09/09-08 aplicadas a mano en las copias).
- `tests/validate-consistency.sh` → 1 FAIL (F011, hereda del anterior).
- Corrección registrada en test-audit.md §"Corrección post-RED".
- Implicancia: GREEN debe dejar ambos en PASS (criterio de aceptación 4).

## Matriz de probes GREEN (a ejecutar tras implementar + RESTART de opencode)

Ejecución: SOLO sesión primaria (guardia anti-spawn). Cada celda = comando →
resultado esperado. Evidencia: output pegado abajo de cada fila al ejecutar.

| # | Agente (task) | Probe | Esperado | Postcond |
|---|---------------|-------|----------|----------|
| G1 | cdad-test-writer | `task` aceptado | sin rechazo "read-only" | P1 |
| G2 | cdad-test-writer | write `tests/__probe_g2__.md` | PERMITIDO | P2 |
| G3 | cdad-test-writer | write `src/__probe_g3__.ts` | DENEGADO | P2 |
| G4 | cdad-test-writer | bash `rtk pytest --version` (si pytest en stack) | PERMITIDO | P4 |
| G5 | cdad-test-writer | bash `rtk read docs/x.md` | DENEGADO | P4 |
| G6 | cdad-test-writer | bash `python3 -c "print(1)"` | DENEGADO sin prompt | P3 |
| G7 | cdad-implementer | write `tests/__probe_g7__.md` | DENEGADO | P2 |
| G8 | cdad-implementer | write `src/__probe_g8__.ts` | PERMITIDO | P2 |
| G9 | cdad-implementer | bash `go version` (si go en stack) | PERMITIDO | P4 |
| G10 | cdad-architect | `task` aceptado + write cualquiera | task OK, write DENEGADO | P1/P2 |
| G11 | cdad-reviewer | bash `rtk read docs/x.md` | PERMITIDO | P4 |
| G12 | cdad-reviewer | bash `rtk err ls` | DENEGADO | P4 |
| G13 | cdad-scribe | `task` aceptado | sin rechazo | P1 |
| G14 | cdad-test-writer-odoo | write `tests/__probe_g14__.py` | PERMITIDO | P2 |
| G15 | cdad-implementer-odoo | bash `pylint --version` | PERMITIDO | P4 |
| G16 | todos | grep logs durante la batería | cero `action.action=ask`, cero `permission=write` | P3 |

### Resultados GREEN

_(pendiente — se completa tras implementación + restart)_

## Checklist de criterios de aceptación

1. [ ] run-checks.sh todo PASS (RED definido antes de editar)
2. [ ] Matriz G1-G16 con output pegado
3. [ ] Cero prompts ask / cero `permission=write` en logs (grep pegado)
4. [ ] 3 validadores en PASS simultáneo
5. [ ] install.sh --dry-run / --check / idempotencia
6. [ ] Cero diff agents/claude-code/
7. [ ] Docs P6 + ADR-009 completos
