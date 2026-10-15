
Commits: `aee7107` (RED) + `2204bab` (GREEN). Alcance de archivos **exactamente** los 2 declarados por plan T2 (verify: `git diff --name-only`). No hay toques fuera de scope. `docs/.cdad-state.json` aparece como `M` en el árbol de trabajo — modificación pre-existente del orquestador, no producida por esta review (no toqué ese archivo; verificar por el log del orquestador).

**Comandos ejecutados (read-only + sondas en `/tmp/opencode/guard-rev-probe`, workspace temporal aprobado):**
- `env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_003_003_t2_preflight.py -q` → `4 passed in 1.10s` (suite completa no repetida: 453 passed en `2204bab` según orquestador).
- 8 sondas `preflight` sobre proyecto sintético con política/ctx propios (fixtures propios, sin incidente real — P6 respetada; ninguno dentro del repo).

**Lo que el T2 sí cumple (verificado, no por confianza):** P3 literal — prevalidación acotada (misma operación denegada N veces ⇒ rc y bytes idénticos), decisión función pura sin contador ni deriva; O2 — política leída y byte-a-byte idéntica tras deny+allow (test lo afirma con `read_bytes`); invariante 1 — árbol read-only (`tree_snapshot` before/after); rc≠0 + diagnóstico stderr + envolvente completa stdout en deny, sin traceback; `denied_by` distingue `policy` vs `role-scope`; traversal `tests/../secrets/…` normalizado y denegado por política (probe G ✓); fallback correcto con contexto no-dict (rc=2 ✓).

---

## Hallazgos bloqueantes

### F1 — `allow` fabricado ante objetivo no resoluble / fuera de raíz (familia única; P5, D6, «unknown no se fabrica»)

**Evidencia (probes, todos rc=0/allow):**

| # | Operación | Resultado | Defecto |
|---|---|---|---|
| A | `{"tool":"read","path":"../outside/x.txt"}` | allow, rc=0 | escape `..` → `rel=None` → la política (private_paths) y el rol no se consultan; allow con justificación «within the declared scope» |
| D | `{"tool":"read","path":"/tmp/opencode/…/other/secrets.txt"}` (abs fuera de raíz) | allow, rc=0 | ídem |
| B | `{"tool":"bash","command":"rm -rf /tmp/x"}` | allow, rc=0, reason «operation 'bash' **on None** is within the declared scope» | herramienta que muta, fuera de `WRITE_TOOLS` y sin path resoluble ⇒ allow total |
| G' | `{"tool":"read","path":"skills/lib.py"}` con `read_scope` de solo `docs`+`tests` | allow, rc=0 | `read_scope` **nunca** se consulta: `_scope_targets` se aplica solo a `write_scope` (línea ~327) |
| E | `private_paths: "secrets/secret.local"` (string, no lista) | allow, rc=0 sobre la ruta privada | `_private_paths` devuelve `[]` ante shape inválido ⇒ **fail-open**; contradice el propio docstring «Fail loud on a missing or malformed input» |
| C | `--role reviewer` con ctx de `test-writer` | allow, rc=0, «within the declared scope of role 'reviewer'» | `--role` no se contrasta con `exec_context["role"]`: identidad no verificable, justificación fabricada |

**Por qué bloquea:** D6 declara detectar «una operación declarada denegada **o fuera de raíz**» *antes de llamarla*. Para targets no resolubles (`rel=None`) y para toda herramienta no-write, el guard emite `allow` con reason que **afirma** «is within the declared scope» — una afirmación de éxito sobre nada evaluado. Eso viola exactamente el eje que el orquestador pidió verificar («unknown no se fabrica», spec §2 sin-señal-fiable, P5) y el docstring de `_root_relative`, que promete fail-closed («fails closed to "outside"») — en la rama read falla *open*. El RED de T2 lo dejó declarado («variantes de ruta mediadas por patrón… se fija en review»): esta revisión es el lugar de fijarlo, y lo que quedó fijado fabrica allow.

**Consecuencia:** el preflight es consumible como evidencia de «la operación es legítima» cuando la ubicación/intención no pudo verificarse; en el caso B una operación destructiva recibe rc=0. Un denegado legítimo por read-scope (C4: deny de operación legítima = defecto del producto) no se detecta pre-flight y el guard lo habría endosado como allow.

**Condición verificable de cierre (un focale, un run):**
1. `read` con `../`-escape o path absoluto fuera de raíz ⇒ rc≠0 (`deny` por fuera-de-raíz, D6) o envelope `decision:"unknown"` con reason honesto; `allow` = fallo.
2. Herramienta sin target resoluble (bash y todo lo no-write) ⇒ `decision:"unknown"` (o `deny` declarado en contrato); prohibido reason «within the declared scope».
3. `path_policy` no-objeto o `private_paths` presente con tipo ≠ lista ⇒ rc≠0 «policy invalid» (fail-loud); ausente ⇒ vacía declarada.
4. `--role` ≠ `exec_context["role"]` ⇒ rc≠0 o `unknown` con diagnóstico de inconsistencia.

Verdict: **BLOCKING** · Bucket: **h** · Ubicación: `skills/cdad-cycle/scripts/cdad_guard.py` — `_root_relative` + `evaluate_preflight` (rama private-check y rama no-write), `_private_paths`, `_cmd_preflight` (contraste de rol).

---

## Opcionales (sin prolongar)

- **O-A** `--json` es inerte: se emite JSON siempre, con o sin flag (docstring del test dice «con --json»). Alinear: flag elimina o envelope textual sin flag. Verdict: OPTIONAL · Bucket: l · `cdad_guard.py` `_build_parser`/`_cmd_preflight`.
- **O-B** Docstring del test quedó en tiempo-RED: «RED hoy: el subcomando `preflight` NO existe aún» — falso post-GREEN; confunde futuras auditorías del mapping test↔postcondición. Actualizar. Verdict: OPTIONAL · Bucket: l · `tests/test_003_003_t2_preflight.py:69`.
- **O-C** `tree_snapshot` importado de `tests/test_004_002_t2_bootstrap.py`: acoplamiento cross-feature entre tests (mover a helper compartido). Verdict: OPTIONAL · Bucket: l · `tests/test_003_003_t2_preflight.py:51`.
- **O-D** D6 declara consumo de «mapa de rol»: hoy `WRITE_TOOLS` es una lista genérica sin diferenciación por rol (todas las mutaciones vía herramientas patrimonialmente write; bash excluido por diseño declarado). Aceptable como MVP si F1 introduce `unknown`; registrar la limitación en el contrato `preflight-v1`. Verdict: OPTIONAL · Bucket: m · `cdad_guard.py` (constante `WRITE_TOOLS`).

## Verificaciones positivas (precondición de F1, no lo debilitan)

Lo acotado de P3 y el O2 están bien construidos: determinismo byte-a-byte, árbol y política intocados, `denied_by` honesto en la vía deny, y fallo cerrado correcto en la rama de **escrituras** (out-of-root write ⇒ deny; `bash`+path no-write es el hueco F1-B). Los cuatro focales pasan en local (`4 passed in 1.10s`) y no reproducen ninguno de los casos A/B/C/D/E — ahí está el gap de cobertura, no en lo que cubren.

## Deuda T1 (no reabierta)

F1 (traceback no-UTF-8), F2 (token vacío), O2/O3 de T1: confirmado que siguen en `review-t1-decision.md:15-17`; este diff no los agrava ni los corrige — correcto, es T2.

## Abstenciones

- **Equivalencia causal deny→mala conducta:** no puedo juzgar la fricción de integración real (T5) — fuera de este diff; nada en el código trata el rechazo como conducta.
- **Comportamiento con `--project-root` relativo:** no lo probé (todas las sondas usan root absoluto, como los fixtures del test); si el runner lo invoca relativo, `_root_relative` cambia de comportamiento — lo dejo como abstención, no como hallazgo.
- **Rendimiento:** O(n·m) trivial sobre listas pequeñas de política; no hay hot path observable — sin medición, no afirmo.

**Dictamen:** 1 familia bloqueante (F1, 6 sub-casos con sondas reproducibles) + 4 opcionales. La familia F1 es la que el orquestador marcó como eje prioritario; la corrección es acotada (fail-closed → `unknown`/deny en la rama no-resoluble, fail-loud en shape de política, contraste de rol) y no reabre decisiones de T1.
