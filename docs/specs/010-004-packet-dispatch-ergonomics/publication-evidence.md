# Evidencia de la publicación — 010-004-packet-dispatch-ergonomics

**Fecha:** 2026-10-31. **Autor:** orquestador CDAD (materialización de una medición propia, ADR-003).
**Estado:** documento **posterior** al cierre. No re-aprueba nada ni modifica el contrato: `closure.md`
(§7, §9, §10) está pineado por el cierre registrado en `docs/.cdad-state.json`
(`closure_evidence.sha256 = 820b1a31…`) y **no se reescribe**. Este archivo conserva las corridas
crudas que sostienen §10, para que cualquiera pueda reproducirlas.

## 1. Antes de publicar

```sh
bash install.sh --check    # rc=1
```

`Check: FAIL`. `DRIFT` en los **22 agentes instalados** (11 por runtime), en los cinco archivos de
referencia de `skills/cdad-cycle` (`re-entry.md`, `project-execution.md`, `handoff-prompts.md`,
`project-start.md`, `packets/substages/test-writer-post-audit.md`), en `cdad_packet.py` y
`cdad_continuity.py`, y en los `__pycache__` de los tres árboles. Ningún agente instalado portaba el
intake nuevo (`Route A and route C are exclusive` → 0 coincidencias).

## 2. Publicación

```sh
bash install.sh            # rc=0 — 390 owned file(s), 0 conflict(s)
bash install.sh --check    # rc=0 — Check: PASS (414 artifact groups in sync with staging/skills)
```

- Staging verificado idéntico a una generación fresca: `cdad-generate.py --runtime opencode|claude-code
  --stack odoo --out <tmp>` + `diff -r` contra `build/staging/agents` → sin diferencias.
- `install.sh` **no** se modificó; no hizo falta `--force` (no interviene en conflictos).
- 12 destinos incoherentes respecto del manifiesto previo (`source_version 6de69b6dd09c`, que declaraba
  0 conflictos): 9 agentes de `~/.config/opencode/agents` con el `model:` del usuario sobre un cuerpo
  anterior, y 3 `__pycache__/*.pyc` recompilados localmente. El instalador los reportó
  `CONFLICT … PRESERVED` (política 009-001). Resueltos con el mecanismo del propio instalador:
  `scripts/agent-overlay.py merge <staged> <instalado> --out` (bytes de staging + el `model:` del usuario
  verbatim) y retiro de los tres directorios `__pycache__` (caché derivada). Segunda corrida: 0
  conflictos, 0 `pending_removal`.
- Respaldo de los bytes instalados y del manifiesto previo: `.cdad/local/deploy-backup-20261031/`.
- Manifiesto resultante: 390 artefactos, 0 conflictos, 0 `pending_removal`, `runtime claude-code`,
  `stack odoo`, `source_version` = commit de la publicación.

## 3. Hashes (repo vs instalado)

| Archivo | Repo | `~/.config/opencode` | `~/.agents` | `~/.claude` |
|---|---|---|---|---|
| `cdad-cycle/scripts/cdad_packet.py` | `d62278a15f93…2167df` | idem | idem | idem |

Un único sha256 distinto entre las cuatro copias (`sort -u` → 1). `references/re-entry.md`:
`2e506000a017…`, idéntico en repo y `~/.config/opencode`.

## 4. Capacidad nueva en la copia instalada

```sh
~/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py render --help
#   --route {C}     emit the route C explicit file backup identification

~/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py render \
  --project-root . \
  --request .cdad/packets/010-004-packet-dispatch-ergonomics-scribe-memory-001/REQUEST.json \
  --route C
# rc=0 — "Route C — explicit file backup" + bloque JSON de 8 campos
```

**Alcance de esa medición (importante para reproducirla).** Se tomó con la unidad **activa**
(`state.active_feature = 010-004`). Una vez registrado el cierre, la misma invocación devuelve **rc=2**:

```
ERROR: active_feature None does not match the execution feature '010-004-packet-dispatch-ergonomics'
```

No es una regresión: es el control de identidad que impide emitir la identificación de un paquete cuya
unidad ya no está activa (el state descansa en `idle`; la ejecución de 010-004 conserva su vínculo). Para
re-medir `--route C` hace falta una unidad activa con su paquete publicado.

Los 10 agentes de rol instalados por runtime portan el token de intake; el orquestador instalado, en
ambos runtimes, cita `--route C` dos veces.

## 5. `make validate`

```sh
make validate    # rc=0
# tests/validate-consistency.sh:          Assert PASS: 183  Assert FAIL: 0
# tests/validate-odoo-specialization.sh:  Assert PASS: 68   Assert FAIL: 0
# PASS: F011: scripts/validate-subagents.sh (active profile) → PASS
# PASS: F011: tests/validate-odoo-specialization.sh → PASS (zero regression)
```

El FAIL de `closure.md` §7 era el drift de la instalación; publicado, la medición cambia sin tocar la
aserción. **D-1 resuelto.**
