# plan.md — `006-003-installer-single-profile-delegation-config` (APROBADO)

> **Regla A-1 (transversal):** los tests acoplados a perfiles/modelos (discovery §1.6) se cambian **solo en el subfase RED**, declarando el reemplazo del oráculo (no se borran asserts sin declararlo; convención ya usada en `tests/validate-consistency.sh:293-309`). El implementer no edita tests.
> **Política de suite:** regresión focal por unidad; suite completa **una vez**, la corre quien cierra este paquete.

## Unidades

### U1 — Generador sin perfiles ni mapa
- **Depende de:** —
- **Archivos:** `scripts/cdad-generate.py`, `Makefile`, `scripts/cdad-models.sh` (retirado), `sources/agents/adapters/opencode.md` + `claude-code.md` (bullet de frontmatter `:15-18` / `:98-105`), `agents/**` regenerado (`make agents`), `scripts/validate-subagents.sh` (quita el bloque de mapa `:185-242`).
- **RED que la fija:** `test_cdad_generate.py` (flag `--profile` y PD-14), `test_004_001_acceptance_matrix.py` (matriz 4 perfiles), `validate-consistency.sh` F008 (`:463-471`), `test_opencode_read_map_and_steps.py`. Mapea **PD-1a,c,d,e,f** y parte de PD-7a.
- **Regresiones:** `validate-consistency.sh`, `make validate`, `test_004_001_t6.py`, cualquier test que lea agentes generados.
- **Gate:** focal verde + `make agents` reproducible + `validate-consistency.sh` PASS.

### U2 — Instalador sin perfiles
- **Depende de:** U1 (manifiesto sin `profile`).
- **Archivos:** `install.sh` (vars `:101-103`, carga `:126-133`, ayuda `:329-380`, parseo `:441-472`, `resolve_profile`/`validate_profile` `:978-1001`, marcador `:1023-1034`, checks `:1283-1294`, `:1344`, `:1442-1526`, mismatch `:1722-1735`).
- **RED:** `test_install_review5_regressions.py:401-480` (B4 pierde objeto → reformular declarándolo), `test_install_ownership.py:281-308` (campo `profile`), `test_005_004_t2_installer_claims.py:105,438`. Mapea **PD-1a,b,g**.
- **Regresiones:** recetas `install.sh --basic` (`test_003_002_t4_integration.py:64`, `test_004_001_t7_capacity.py:166`, `test_004_002_t6_landing.py:257`, `test_004_003_t2_plan_review.py:268`, `test_005_005_t4_integration.py:88`, `test_005_008_t3_acceptance.py:167`), `test_005_004_t1_dispatch_tool_name.py`, `test_005_006_t2_intake.py`.
- **Gate:** focal + `install.sh --check` PASS en raíz redirigida.

### U3 — §2 de `SKILL.md` y sección `delegation` de los adaptadores
- **Depende de:** U1 (orquestadores regenerados).
- **Archivos:** `skills/cdad-cycle/SKILL.md:77-82,165-170`, `sources/agents/adapters/opencode.md:76-83`, `claude-code.md:98-105`, orquestadores regenerados.
- **RED:** `test_006_002_u4_skill_without_models.py:153-180` (conceptos 6/7/8 «perfil»), `test_006_002_u1_delegation_section.py:121-127,437-450`. Mapea **PD-7a,b**.
- **Regresiones:** `validate-consistency.sh` F001 (`:303-361`), tests que leen orquestadores generados (`test_role_packet*.py`, `test_packet_prepare.py`).
- **Gate:** focal + oracle AC-7 vacío.

### U4 — Config de delegación (fuente única)
- **Depende de:** U2 (ubicación `<root>/.config`).
- **Archivos:** `install.sh` (crea `delegation.json` + `.env.example`), `skills/cdad-cycle/scripts/cdad_delegate.py:264-267` + `:177-193` (provenance), `cdad_delegate_opencode.py:1678,404-405`, `assets/opencode-exec-config.example.json`, `references/cli-delegation.md:267-276`.
- **RED:** nuevo test de delegación externa. Mapea **PD-2a-d, PD-3a-d**.
- **Regresiones:** tests del adaptador de 006-001/006-002 que leen I8 y argv.
- **Gate:** focal + `install.sh --check` PASS.

### U5 — Verificación de familia
- **Depende de:** U4 (modelo configurado).
- **Archivos:** nuevo `skills/cdad-cycle/scripts/cdad_model_family.py`.
- **RED:** test del script con fixtures (a/b/c) y de la declaración. Mapea **PD-4a-e**.
- **Regresiones:** `scripts/validate-subagents.sh` (su guard pasa vacuo con `basic` — `:226,240,252`; declararlo, no confiar en él).
- **Gate:** focal verde; restricción «aviso, no gate».

### U6 — Credencial del servidor
- **Depende de:** U4 (`credential_env_file`).
- **Archivos:** `cdad_delegate_opencode.py:935-945,1026-1067`; `install.sh` (`.env.example`); `cli-delegation.md`.
- **RED:** fixture de servidor que exige credencial + oráculo de ausencia con centinela. Mapea **PD-5a-e, INV-1**.
- **Regresiones:** `test_pd5_no_secrets_in_successful_dispatch_outputs` (vigilar DT-9, margen 2 s).
- **Gate:** focal + PD-2b (el `.example` sin valor).

### U7 — Retiro de obsoletos propios en la instalación
- **Depende de:** U2.
- **Archivos:** `install.sh` (manifiesto python `:899`, cálculo `pending_removal` `:917-946`, nuevo paso de retiro, `--check` `:1499-1526`, `--dry-run`).
- **RED:** test con manifiesto sintético (intacto / modificado / ajeno / dry-run). Mapea **PD-6a-e, INV-2**.
- **Regresiones:** `test_install_ownership.py`, tests de `--uninstall` (misma regla de sha256).
- **Gate:** focal + `install.sh --check` PASS.

### U8 — Aceptación (raíz redirigida, nunca HOME)
- **Depende de:** U1–U7.
- **Archivos:** test de aceptación.
- **RED/E2E:** `CDAD_INSTALL_ROOT=<tmp>` + `XDG_CONFIG_HOME=<tmp>`; instalación end-to-end; fixture de servidor que exige credencial; verificación de PD-8a,b,c y de INV-6 (HOME intacto). Mapea **PD-8a-c, INV-6**.
- **Regresiones:** módulos acoplados de §1.6 completos + `validate-consistency.sh`.
- **Gate:** `install.sh --check` PASS + `make validate` PASS; suite completa una vez al cierre.

## Dependencias (resumen)

```
U1 ──▶ U2 ──▶ U4 ──▶ U5
 │      │      └───▶ U6
 │      └───▶ U7
 └───▶ U3
U1..U7 ──▶ U8
```

## Riesgos heredados (de discovery §6)

R1 (tests acoplados → A-1), R2 (recetas `--basic` → PD-1b), R3 (exec-configs con `model` → PD-3b), R4 (diff en `agents/` → declarado), R5 (staging divergente → PD-1d), R6 (DT-8 fuera), R7 (fail-open de familia → PD-4c), R8 (nueva superficie de lectura de credencial → PD-5b,c), R9 (`model_reported` vs `model_configured` se registra, no se interpreta como éxito).

---

Status: Approved by orquestador Claude (HITL delegada por Pablo, epic-006) on 2026-10-18
