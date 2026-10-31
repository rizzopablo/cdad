## FINAL TEXT — Informe GREEN · 010-001 contratos documentales (T3)

### 1. Intake (ruta C) — validado antes de trabajar

| Comprobación | Resultado |
|---|---|
| Identificación recibida vs. `render --route C` | **idéntica** (comparación byte a byte) |
| `PACKET.md` vs. render canónico completo | **idéntico** (`diff` sin salida, 9935 bytes) |
| `validate-request` (REQUEST + execution) | **rc=0**, sin salida |
| `execution.json` `schema_version` | **2** (v2, admisible en ruta C) |
| sha256 del contrato vs. `spec.md` en disco | `9bf17a39…c94da` — **coincide** |
| Cuerpo inline junto a la identificación | **no hay** → sin mezcla de rutas |

Comandos (desde la raíz):

```bash
python3 -B skills/cdad-cycle/scripts/cdad_packet.py render --project-root . \
  --execution-context .cdad/executions/exec-010-001-documentary-contracts-002/execution.json \
  --request .cdad/packets/010-001-documentary-contracts-implementer-green-001/REQUEST.json --route C

diff -u .cdad/packets/010-001-documentary-contracts-implementer-green-001/PACKET.md /tmp/opencode/render-A.md
# → PACKET_MATCHES_RENDER

python3 -B skills/cdad-cycle/scripts/cdad_packet.py validate-request --project-root . \
  --execution-context .cdad/executions/exec-010-001-documentary-contracts-002/execution.json \
  --request .cdad/packets/010-001-documentary-contracts-implementer-green-001/REQUEST.json
# → rc=0, sin salida
```

### 2. Archivos modificados y commit

- **Nuevo:** `skills/cdad-cycle/references/documentary-contracts.md` (171 líneas) — la casa normativa única: cuatro categorías con sus distinciones (D1), localizador mínimo por tipo de fuente y tratamiento de fuentes inaccesibles/mutables/insuficientes (D2), clasificación bloqueante/no bloqueante con sus datos mínimos y prohibición de rebaja unilateral (D3), las cuatro declaraciones del encargo, la protección del oráculo, las fronteras de los seis roles (PC-05…PC-08), los dos registros de cierre con sus límites (PC-09…PC-11) y la aceptación funcional del usuario/dueño (PC-12). Sin ningún nombre propio.
- **Modificados:** `skills/cdad-cycle/SKILL.md` (+1 fila en «How to read the references»); `sources/roles/{architect,implementer,test-writer,reviewer,scribe,orchestrator}.md` (+4…+11 cada uno: obligación documental parafraseada + puntero verbatim `documentary-contracts.md`).
- **Implementer:** el contrato admite ahora «implementation code, or the documentary product an engagement expressly commissions» (directiva y columna *May edit*), **sin ampliar defaults**; «You do NOT touch test files.» y «You CANNOT edit them.» quedan **literales**.
- **Commit:** `3344526edbe0e191b1c979411eb80b241315d039` — `feat: implement shared documentary contracts and role obligations (PC-01..PC-12)` (8 archivos, +207/−2).
- **Ningún test, contrato aprobado, agente, `build/`, `scripts/`, `install.sh` ni `docs/` modificado.** `docs/.cdad-state.json` sigue modificado por el binding del orquestador (diff ajeno: `active_packet`), no por este encargo.

### 3. Comando focal (A–C) y salida

```bash
python3 -B -m unittest tests.test_010_001_documentary_contracts.TestPromiseA tests.test_010_001_documentary_contracts.TestPromiseB tests.test_010_001_documentary_contracts.TestPromiseC
```
```text
......
----------------------------------------------------------------------
Ran 6 tests in 0.348s

OK
```

### 4. Estado del grupo D — rojo por diseño (T4)

```bash
python3 -B -m unittest tests.test_010_001_documentary_contracts
# Ran 11 tests ... FAILED (failures=27)
```
Los 27 fallos son **exclusivamente** `task='T4'`:
- `test_the_six_role_sources_and_five_blocks_carry_their_obligation_and_pointer`: **5 subtest T4** (los cinco bloques `packets/roles/` sin puntero). La mitad **T3 (6 fuentes) está verde.**
- `test_generated_and_promoted_agents_of_both_runtimes_carry_the_obligations`: **22 subtest** (11 agentes × 2 runtimes sin regenerar).

**Ya verdes** (no estaban en el RED declarado para T3 pero quedaron acreditadas): `test_the_norm_lives_in_one_house_listed_in_the_reference_table`, `test_no_installable_surface_copies_the_normative_phrases` (unicidad PC-13/INV-01: ninguna frase de la referencia se reproduce en `skills/`, `sources/`, `agents/`) y `test_isolated_install_distributes_the_reference_with_source_bytes`.

Generación verificada como proceso (copia descartable en `/tmp/opencode/gen-check`, sin tocar el árbol): `opencode`/`claude-code` × `generic`/`odoo` → **rc=0**, y los 6 agentes genéricos y los 11 de la variante Odoo de cada runtime llevan el puntero.

### 5. Regresión proporcional ejecutada

```text
tests.test_006_004_u3_principle_single_source + test_006_003_u5p_no_family_requirement + test_004_002_t7_limits_rule  → Ran 25 tests, OK
tests.test_005_006_t2_intake + test_003_006_t3_receive_wiring + test_003_007_t4_atomic_unit_rule + test_006_002_u6_context_discipline → Ran 31 tests, OK
tests.test_cdad_generate + test_role_packet_render + test_role_packet_consumers → Ran 32 tests, OK
```
Techo estático intacto: máximo **3397 bytes** (reviewer/plan-review) sobre 12000.

### 6. Límites honestos (PD-15 / INV-06 / INV-08)

- **Un verde A–C es estructural.** No acredita fidelidad semántica, suficiencia ni aceptación funcional: eso es T5 y el dueño. El módulo no es un sandbox ni prueba ausencia de escrituras transitorias.
- **`scripts/validate-subagents.sh` (invocado por `tests/validate-consistency.sh`) ahora reporta FAIL** en `install.sh --check`: `DRIFT: missing ~/.claude/skills/cdad-cycle/references/documentary-contracts.md` y `differs .../SKILL.md`. Es exactamente la distribución diferida a T4 (instalación aislada); **no instalé nada global** ni toqué el HOME. El resto del validador: 182 PASS.
- **Suite completa no ejecutada**: la política del paquete la corre una sola vez quien cierra (T6).
- El grupo D sigue rojo por diseño; no lo declaré verde.
