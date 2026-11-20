I'll start by reading the approved contract and the declared inputs.
Now I have the full picture. Let me write the acceptance test file.
Now the reformulation of the opt-in 005-010 T4 integration test (declaring the D3/U4 replacement):
Now the exec-config builder and the delegation document:
Now the call site and the assertion message:
Now the assertion itself and its message:
Trabajo terminado y commiteado. Reporte:

## 1. Archivos modificados (solo `tests/`)

| Archivo | Estado | Qué |
|---|---|---|
| `tests/test_006_003_u8_acceptance.py` | **nuevo** (797 líneas) | U8: aceptación end-to-end con `CDAD_INSTALL_ROOT`, `HOME` falso y `XDG_CONFIG_HOME` propios |
| `tests/test_005_010_t4_integration.py` | reformulado (+107/−25) | Oráculo `model_configured` movido de la exec-config a `delegation.json` (D3/U4), declarado; sigue opt-in y sin activar |

Commit: `1bc7645 test: 006-003 U8 aceptación — recorrido end-to-end en raíz redirigida (PD-8a/PD-8b, PD-6a, INV-1/INV-3/INV-6) y T4 reformulada por D3/U4 (modelo desde delegation.json)` (2 files, 889 insertions, 25 deletions). Sin `--no-verify`, sin stash, sin push. Los untracked `docs/planning/` y `findings/…-2026-10-17.md` quedaron sin tocar.

## 2. Mapa test → PD/INV

| Test | Postcondición | Qué observa |
|---|---|---|
| `test_pd_8a_install_passes_check_without_models_and_with_empty_config` | **PD-8a** (+PD-1e/PD-2a/PD-2b, **INV-3**) | generador sin `--profile` sobre copia → install → `--check` rc=0 + «PASS», sin PENDING-REMOVAL; ningún agente instalado con `^model:`; orquestadores instalados sin modelos concretos; `delegation.json` v1 con destino `opencode` y `.example` con líneas `KEY=` vacías |
| `test_pd_3b_pd_5c_server_dispatch_uses_installed_config_and_no_leak` | **PD-3b + PD-5c + INV-1 + INV-7** | se completa el `delegation.json` del instalador (rol `test-writer`) y un `opencode-server.env` 0600 con centinela; despacho `mode: server` contra fixture loopback con Basic auth → `completed`; argv lleva el modelo de delegación y **no** el `model` heredado de la exec-config (presente a propósito); centinela ausente de stdout/stderr/diagnóstico/argv/I8/entrega/delegation.json (y el fixture **sí** lo recibió: oráculo no vacuo) |
| `test_pd_8b_make_validate_passes_on_the_acceptance_install` | **PD-8b** | `tests/validate-consistency.sh` (cuerpo de `make validate`) con root/HOME/XDG redirigidos a la instalación de aceptación → rc=0, `Assert FAIL: 0`, cero líneas `FAIL:` |
| `test_pd_6a_reinstall_retires_own_obsolete_and_check_still_passes` | **PD-6a** (puente U7) + PD-8a | fuente propia retirada del producto → reinstalación retira los despliegues registrados, los saca del manifiesto y `--check` sigue PASS |
| `test_inv_6_full_walk_never_touches_the_fake_home` | **INV-6** | install → check → reinstalación → despacho server: HOME falso byte a byte vacío, nada nuevo al lado de root/config dir, `xdg/` solo contiene `cdad/` |
| T4 (reformulado) | 005-010 PD-8 (e) + **006-003 D3/U4** | `model_configured` se compara contra el modelo de `delegation.json` escrito en el temporal, con `XDG_CONFIG_HOME` redirigido; la exec-config ya no declara `model` |

**PD-8c** (suite completa) no se corre aquí: política del paquete → la corre quien cierra.

## 3. Comandos y salida

```bash
# línea base antes de escribir (árbol post-U7 GREEN)
python3 -m pytest tests/test_006_003_u4_delegation_config.py tests/test_006_003_u6_server_credential.py tests/test_006_003_u7_prune_obsolete.py -q
→ 20 passed in 141.01s

# módulo nuevo + T4 reformulada
python3 -m pytest tests/test_006_003_u8_acceptance.py tests/test_005_010_t4_integration.py -q
→ 5 passed, 1 skipped in 69.22s          (T4 sigue omitida por defecto)

# focal completa 006-003
python3 -m pytest tests/test_006_003_u{1,2,3,4,5p,6,7,8}*.py -q   # invocado por lista explícita
→ 55 passed in 223.37s

# herencia de T4 (T3 importa sus helpers)
python3 -m pytest tests/test_006_001_t3_integration.py -q
→ 1 skipped in 0.07s

python3 -m py_compile tests/test_005_010_t4_integration.py tests/test_006_003_u8_acceptance.py → compile OK
```

## 4. Hallazgo (no forzado)

**F-1 — PD-8b no PASSa hoy en este host sin redirigir: `make validate` → 168 PASS / 1 FAIL.**

```
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
[repo] cross-check: install.sh --check
DRIFT: differs <home>/.claude/skills/cdad-cycle/SKILL.md
DRIFT: … (11 agentes × .claude/agents, .config/opencode/agents; + skills cdad-cycle, agents, exec-config example)
❌ install.sh --check failed (rc=1)
```
Causa: F011 corre `install.sh --check` contra la instalación **del dueño** (`~/.claude`, `~/.config/opencode`, `~/.agents`), que quedó stale tras U1/U3/U4 (artefactos instalables cambiados); no es un assert de producto. Evidencia de que el validador es verde sobre una instalación al día: **redirigido a la instalación de aceptación → `Assert PASS: 169 / Assert FAIL: 0`** (mismo script, misma suite de asserts). Por eso PD-8b se assertea redirigido (declarado en el docstring del test y en la frontera), y el `make validate` sin redirigir queda como decisión del orquestador para el cierre: reinstalar el host o registrar la deriva como ambiental.

Desviación declarada (honesta): ejecuté `make validate` y `scripts/validate-subagents.sh` en modo caja negra para producir esta evidencia; su salida nombró rutas del host y la lista de drift (nombres, ningún contenido, ninguna credencial). No leí código de implementación ni `~/.config/cdad/*` ni `tests/.sensitive-patterns.local`.

## 5. Notas de diseño (declaradas)
- Reuso por import (sin duplicar fixtures ni tests ajenos): `AdapterCase`/`Pd600T1Case` vía `ServerCredentialCase` (U6), `FakeInfoServer`+`basic_auth_header` (006-001 T1), helpers de manifiesto/árbol (U7).
- «`make staging` o equivalente sobre una copia»: `scripts/cdad-generate.py --runtime <r> --stack odoo --out build/staging` **sin** `--profile` dentro de la copia de producto (nunca el repo, nunca el HOME real).
- Cotas holgadas: el fixture usa los defaults de U6/T1 (`FAST_WAIT`, `TEST_WAIT_TIMEOUT_SECONDS`) sin apretarlos; el archivo nuevo tarda ~65 s.
