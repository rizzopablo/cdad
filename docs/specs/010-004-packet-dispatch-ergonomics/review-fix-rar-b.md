Both findings applied, verified, and committed. Final report:

## Validación del packet (Route C — respaldo explícito de archivos)

Scripts del **repositorio** (`skills/cdad-cycle/scripts/`), con `--project-root <repo>`:

| Control | Comando | Resultado |
|---|---|---|
| Request | `cdad_packet.py validate-request --request <P>/REQUEST.json` | `EXIT=0` |
| Packet publicado | `cdad_packet.py validate-packet --request <P>/REQUEST.json --packet <P>/PACKET.md` | `VALIDATE_PACKET_EXIT=0` |
| Render canónico completo | `cdad_packet.py render --request …` vs `PACKET.md` | `FULL_PACKET_IDENTICAL=yes` (byte a byte) |
| Identificación Route C | `cdad_packet.py render --route C --request …` | idéntico al bloque de identificación del dispatch |
| Contrato | `sha256sum docs/specs/010-004-packet-dispatch-ergonomics/spec.md` | `fc6b2ccc…5d64` = declarado |
| Policy | `sha256sum docs/cdad-policy.json` | `f508ab1e…2711` = declarado y en `execution.json` |

Ninguna diferencia → packet válido; no se buscó otro packet ni se usó la copia global.

## Hallazgos verificados contra la evidencia original (review-verification.md:55-71)

- **R-A** confirmado: `_replace_packet` (l.3611) y `_resume_packet` (l.3266) no pasan por `prepare()` ni por `_reject_active_v1_packet`; el comentario en l.6458-6460 afirmaba «EVERY preparation path». Corregido **solo el comentario**.
- **R-B** confirmado: `project-start.md:93-95` decía «Add --new-execution…» sin salvedad. Añadida **una** línea.

## Cambios (sin tocar tests)

- `skills/cdad-cycle/scripts/cdad_packet.py:6458-6462` — comentario de `prepare()` ahora declara: bloqueo PC-07b en rutas de preparación nueva/ordinaria y `--new-execution`; `_replace_packet`/`_resume_packet` no pasan por el helper y conservan su propio rechazo. Chequeo mecánico del diff: `ONLY_COMMENTS=yes`; `ast.parse` → `AST_OK=yes`.
- `skills/cdad-cycle/references/project-start.md:96` — línea añadida: `#    A published v1 packet still active: no terminal CLI route; escalate to the owner (project-execution.md §3).` Sin headings, sin filas de tabla, resto del párrafo intacto.

```
 skills/cdad-cycle/references/project-start.md | 1 +
 skills/cdad-cycle/scripts/cdad_packet.py      | 8 +++++---
 2 files changed, 6 insertions(+), 3 deletions(-)
```

## Verificación focal (árbol final)

1. `python3 -m pytest tests/test_010_004_t6_red.py tests/test_010_004_t6_b1_guard.py tests/test_010_004_t2_red.py tests/test_010_004_t3_red.py tests/test_010_004_t4_red.py tests/test_010_004_t5_e2e.py tests/test_cdad_generate.py -q`
   → **`30 passed in 68.95s (0:01:08)`** (igual a la medición de la reverificación T6)
2. `python3 -m pytest tests/test_005_006_t1_start_procedure.py tests/test_005_006_t2_intake.py tests/test_005_006_t6_owner_reviewfix.py -q`
   → **`26 passed in 0.55s`**

Suite completa **no** ejecutada (política declarada: la corre quien cierra).

## Commits (uno por hallazgo)

- `28991b4a` `fix(010-004): R-A — el comentario de prepare() dice la verdad sobre el bloqueo v1`
- `6869301f` `fix(010-004): R-B — puntero a project-execution.md §3 en project-start.md`

`git status` limpio salvo `?? docs/specs/010-000-continuity-relative-root/discovery.md`, preexistente y ajeno a esta unidad. No se tocó la copia instalada, ni `tests/**`, ni spec/plan, ni derivados generados. Endurecer `--replace-packet`/`--resume-packet` quedó fuera, como deuda anotada.