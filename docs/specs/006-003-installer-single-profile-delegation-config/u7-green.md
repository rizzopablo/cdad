I'll start by reading the contract, tests, and the current installer.
Patch applies clean. Let me apply it and then add the A-6 change (Verify count derived from staging).
## Role report — implementer / GREEN (2º intento) · `006-003-installer-single-profile-delegation-config` U7

### 0. Resultado — **GREEN. Commit `516149b`. Tests intactos.**

Contrato verificado (`docs/specs/006-003-…/spec.md` sha256 `c25ebf0e…d18890`). Solo `install.sh` modificado; `tests/` intacto; nunca se instaló en HOME (todas las corridas de test usan raíces/con `CDAD_INSTALL_ROOT` temporales); `docs/planning/` y `findings/…` (untracked, ajenos) sin tocar; sin `--no-verify`, sin stash, sin push.

### 1. Archivos modificados

```
 install.sh | 265 ++++++++++++++++++++++++++++++++++++++++++++---------
 1 file changed, 265 insertions(+), 64 deletions(-)
```

- Reutilicé `/tmp/opencode/u7-prune.diff`: `git apply --check` → **APPLIES CLEAN**, aplicado (`+194/−34` del intento anterior).
- **Delta nuevo (A-6)** sobre ese parche: `staged_agent_names`/`staged_agent_count` y `print_summary`/`count_manifest_agents_installed` derivando **ambos lados** del `Verify` del conjunto en staging (el parche no traía A-6).

### 2. Qué implementa

- **PD-6a/b/c (prune):** `prune_owned_obsolete` recorre `artifacts`+`pending_removal` previos; candidato = no redesplegado (`OWNED_ABS`, trackeado también en `--dry-run`) ni ya conflictuado (`CONFLICT_ABS`). La decisión es la **regla única** `owned_removal_state` (extraída de `uninstall_by_manifest`, sin duplicar): `removable` (sha256 intacto) → borra de disco y del manifiesto; `modified` → preserva, `CONFLICT` y **sigue registrado** (`KEPT`); `absent` → no-op. Archivos no registrados nunca se leen (PD-6c/A-3).
- **PD-6d:** `--dry-run` lista las bajas vía `do_run` y no escribe manifiesto ni plan.
- **PD-6e:** el python que lee el manifiesto recibe `INSTALL_ROOT` y resuelve claves absolutas y relativas.
- **A-6:** la cuenta esperada del `Verify` sale del staging por runtime, **y la observada también** (`count_manifest_agents_installed` prefiere el set staged, PD-18); las constantes quedan solo como fallback declarado para una raíz sin staging (path legacy de `--uninstall`).

### 3. Tabla test → resultado

| Módulos | Resultado |
|---|---|
| `test_006_003_u7_prune_obsolete.py` (focal, 6) | **6 passed** |
| `test_install_review5_regressions.py` (B3 reformulada, 6) | **6 passed** |
| `test_install_ownership.py` + `test_005_004_t2_installer_claims.py` + `test_006_003_u1/u2/u4/u6/u7` (52) | **52 passed** |
| 8 módulos `003_*` + `004_001_*` (52) | **52 passed** |
| 9 módulos `004_002_*` / `004_003_*` / `005_001` (86) | **86 passed** |
| 5 módulos `005_005_*` / `005_006` / `005_008` (24) | **24 passed** |
| 7 módulos adapters/packet/role_packet (59) | **59 passed** |
| **37 módulos que invocan `install.sh` (279 tests)** | **279 passed, 0 failed** |
| `bash tests/validate-consistency.sh` | 168 PASS / **1 FAIL = F011** (drift de HOME, declarado) |

Interacción detectada y corregida en el camino (honesta): mi primer corte de A-6 derivaba solo el **esperado** del staging mientras el **observado** seguía contando el manifiesto repo `agents/`; `test_install_ownership.py::test_t5_case9` (fixture staged-only `cdad-zz-t5-extra.md`) falló `Verify: FAIL — expected 12, found 11` (batch: 1 failed/51 passed). Corregido derivando ambos lados del staging (batch posterior: **52 passed**).

### 4. Comandos exactos y salida

```
$ git apply /tmp/opencode/u7-prune.diff          → APPLIED (install.sh | 194 ++--)
$ bash -n install.sh                             → OK
$ python3 -m pytest tests/test_006_003_u7_prune_obsolete.py -q
6 passed in 85.96s
$ python3 -m pytest tests/test_install_review5_regressions.py -q
6 passed in 81.65s
$ python3 -m pytest tests/test_install_ownership.py tests/test_005_004_t2_installer_claims.py \
    tests/test_006_003_u1_… tests/test_006_003_u2_… tests/test_006_003_u4_… \
    tests/test_006_003_u6_… tests/test_006_003_u7_… -q
52 passed in 307.28s
$ python3 -m pytest tests/test_003_002_t4_integration.py … tests/test_004_001_t7_capacity.py -q
52 passed in 122.52s
$ python3 -m pytest tests/test_004_002_t1_policy.py … tests/test_005_001_tcorr.py -q
86 passed in 113.84s
$ python3 -m pytest tests/test_005_005_t1_replace_conserved.py … tests/test_005_008_t3_acceptance.py -q
24 passed in 51.71s
$ python3 -m pytest tests/test_cdad_adapters_opencode.py … tests/test_role_packets.py -q
59 passed in 165.41s
$ bash tests/validate-consistency.sh
Assert PASS: 168 · Assert FAIL: 1 → FAIL: F011 (scripts/validate-subagents.sh → drift …/HOME)
$ bash scripts/validate-subagents.sh
Check: FAIL — drift .claude/agents/… .config/opencode/agents/… (HOME)  ❌ install.sh --check failed
```

F011 reproducido: el drift es de la instalación real en `<home>/.config|.claude` (path `active profile`), no de este cambio.

### 5. Commit

```
516149b feat: 006-003 U7 GREEN — el instalador retira sus obsoletos propios (PD-6a..e/INV-2)
        y deriva la cuenta del Verify del staging (A-6)
 1 file changed, 265 insertions(+), 64 deletions(-)
```
Sin `--no-verify` (no hay hooks activos), sin stash, sin push. `git status --short`: solo `M install.sh` commiteado; quedan los dos untracked ajenos sin tocar.

### 6. Límites honestos
- No corrí la suite completa (política del paquete: la corre quien cierra); corrí el universo de 37 módulos que invocan `install.sh` + la consistencia.
- `--check` legacy sobre raíces sin staging conserva la constante como fallback declarado (comportamiento previo); en modo install, staging siempre existe (`guard_staging`) y la cuenta sale del staging.
