# Review — re-review focal RU-1 (003-006-runtime-adoption)

**Packet:** `003-006-runtime-adoption-reviewer-review-005` · **Rol:** reviewer · **Contrato:** `docs/specs/003-006-runtime-adoption/spec.md` (sha256 verificado: `dc485e80…7cb7` ✓) · **Política:** `docs/cdad-policy.json` (sha256 `f508ab1e…7111` ✓)

## Evidencia de ejecución (read-only)

- **Archivos modificados por mí:** ninguno (write_scope vacío; solo lecturas del repo + raíces temporales propias bajo `/tmp/opencode/`, todas eliminadas al final).
- **Commit bajo review:** `5c09770` `feat: fijar CDAD_PACKET_CLI a la raíz adoptada en el hook de activación (RU-1)` — diff `7a480f4..5c09770` = 2 archivos: `scripts/cdad-activate.py` (+8/−1), `skills/cdad-cycle/references/runtime-adoption.md` (+4/−1... neto +3/−1).

## Verificación de la verificación del autor

| Comando | Resultado |
|---|---|
| `python3 -m pytest tests/test_003_006_t2_activation.py -k "ru1 or p5_hook" -q` | **3 passed** (GREEN ✓) |
| Tests RU-1 en commit RED `1703790` (worktree temporal `/tmp/opencode/ru1-red-wt`, luego removido) | **2 failed** — RED real, no test que ya pasaba ✓ |
| Reproducción Paso 3 (raíces temporales propias, ver abajo) | coincide con `adoption-ledger.md` Paso 3 ✓ |

Secuencia RED→GREEN correcta: `1703790` (RED) → `7a480f4` (ledger) → `5c09770` (GREEN).

## Reproducción del Paso 3 del orquestador

Raíces temporales propias: `A` (guard real `scripts/claude-code-path-guard.sh` + CLI canónico `skills/cdad-cycle/scripts/cdad_packet.py`) y `wt` (política real `docs/cdad-policy.json`), bajo `/tmp/opencode/`. Línea emitida exacta pasada por `bash -c` con `CLAUDE_PROJECT_DIR=<wt>`:

```
CDAD path-guard: implementer may not edit tests (tests/zz.txt is test)
rc=2 -> tests/zz.txt        ✓ bloquea
rc=0 -> scripts/zz.py       ✓ permite
```

Control (sin `CDAD_PACKET_CLI`, HOME sin clasificador): `rc=2 — "policy present but the classifier was not found … blocking without fallback"` → fail-closed confirmado, coincide con la corrección de redacción de P5 en la decisión. **Cerrado.**

## Hallazgos

### H1 — La línea emitida coincide exactamente con t4-ru1-decision.md — **cerrado** (m)
- **Evidencia:** `cdad-activate.py:141` emite `f"CDAD_PACKET_CLI={packet_cli} {guard}"` con `PACKET_CLI_REL=".claude/skills/cdad-cycle/scripts/cdad_packet.py"` (línea 31) y `GUARD_SOURCE_REL=".claude/cdad-scripts/path-guard.sh"`. Archivo emitido real (fixture sintético del propio test, corrido por mí):
  ```
  command: CDAD_PACKET_CLI=<T>/A/.claude/skills/cdad-cycle/scripts/cdad_packet.py <T>/A/.claude/cdad-scripts/path-guard.sh implementer
  ```
  Coincide carácter a carácter con la línea de cierre de `t4-ru1-decision.md:10`. El rol final (`implementer`, `test-writer-odoo-read/write`, etc.) se preserva porque el replace solo intercambia el tramo `~/.claude/...path-guard.sh`.

### H2 — Ningún `command:` emitido depende de HOME — **cerrado** (m)
- **Evidencia:** la línea emitida no contiene `~` ni `$HOME` ni expansión; `test_t4_ru1_no_command_depends_on_home` (tests:700-724) lo aserta por línea y pasa. Los usos restantes de `$HOME` en el guard (`claude-code-path-guard.sh:105-111, 263, 270`) son normalización de rutas `~/…` del *input de herramienta*, no dependencia del comando emitido; `:134` es el fallback que RU-1 corta al fijar la var. **Residuo menor:** si la raíz adoptada vive bajo el HOME real (como v5: `~/.cache/cdad-adopted-d958672`), la ruta fijada está *bajo* HOME pero explícitamente resuelta — la decisión exige no *resolver desde* HOME, y eso se cumple. No blocking.

### H3 — Ajuste del test p5 legítimo — **cerrado** (m)
- **Evidencia:** el ajuste está declarado en el docstring del test (`tests:17-22`), autorizado por la decisión; la aserción nueva es *estricta* (formato exacto de línea completa, no solo substring), y se añadieron 2 tests RED nuevos. La aserción original de que el guard resuelve a `<A>` y que no hay `settings.json` se conserva. No es debilitamiento.

### H4 (Nit, opcional) — `replace()` no anclado reescribe también la prosa del template — **residuo** (l)
- **Evidencia:** simulando el rewrite sobre el template real `build/staging/agents/claude-code/cdad-implementer.md`, la segunda ocurrencia reescrita es el comentario `# Path-scoping is enforced by ~/.claude/cdad-scripts/path-guard.sh (the` → queda `# Path-scoping is enforced by CDAD_PACKET_CLI=… path-guard.sh (the`. Cosmético, sin efecto funcional (no es un `command:`). Remedio estructural: anclar el replace a `command: ` + HOOK_TILDE o reemplazar solo la primera ocurrencia por línea de comando.

### H5 (Optional-Consider) — la activación no valida la existencia del clasificador en A — **residuo** (l)
- **Evidencia:** la activación valida `GUARD_SOURCE_REL` contra el manifest (`cdad-activate.py:147-152`) pero no exige que `PACKET_CLI_REL` exista en A ni esté en el manifest. Un adopt defectuoso se descubriría recién en la primera escritura mediada (fail-closed, rc=2 con diagnóstico). Remedio: mismo chequeo temprano que el guard. No es hueco de seguridad: falla cerrado.

### H6 (FYI, fuera de alcance de este diff) — rutas de adopción con espacios romperían la línea
- Pre-existente (ya rompía `<A>/.../path-guard.sh`); el prefijo de env no lo agrava. No introducido por RU-1.

## Veredicto global de la re-review focal RU-1

**Sin hallazgos blocking.** RU-1 está **cerrado**: formato exacto ✓, sin dependencia de HOME en los `command:` ✓, verificación Paso 3 reproducible con raíces propias ✓, p5 ajustado legítimamente ✓, RED→GREEN real ✓, doc `runtime-adoption.md` consistente con el código ✓. Residuos H4/H5 son Nits opcionales, no bloquean.

## Abstenciones

- **Ejecución del hook dentro de Claude Code real:** el ledger declara que la ejecución en runtime depende de que el dueño marque la carpeta como de confianza (Paso 2); eso es decisión del dueño fuera de este diff y de mi capacidad de verificación — no lo avaló ni lo refutó.
- **Review completa del feature (no focal):** el orquestador delimitó esta review a RU-1; no revisé el resto del diff acumulado del feature ni otros RU.