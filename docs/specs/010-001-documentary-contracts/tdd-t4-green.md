## FINAL TEXT — Informe GREEN · 010-001 contratos documentales (T4)

### 1. Intake (ruta C) — validado antes de trabajar

| Comprobación | Resultado |
|---|---|
| Identificación recibida vs. `render --route C` | **idéntica** |
| `validate-packet` (REQUEST + PACKET) | **rc=0**, sin salida |
| `validate-request` (REQUEST + execution) | **rc=0**, sin salida |
| `sha256` del contrato vs. `docs/specs/.../spec.md` | `9bf17a39…c94da` — **coincide** |
| `execution.json` | `schema_version: 2` (v2, admisible en ruta C) |
| Cuerpo inline junto a la identificación | no hay → sin mezcla de rutas |

```bash
python3 scripts/cdad_packet.py validate-packet --request .cdad/packets/010-001-documentary-contracts-implementer-green-002/REQUEST.json --packet .cdad/packets/010-001-documentary-contracts-implementer-green-002/PACKET.md   # rc=0
python3 scripts/cdad_packet.py validate-request --request .cdad/packets/010-001-documentary-contracts-implementer-green-002/REQUEST.json                                                                              # rc=0
python3 scripts/cdad_packet.py render --request .../REQUEST.json --route C   # salida idéntica a la identificación recibida
```

### 2. Archivos modificados y commit

**Cinco bloques estáticos** (`skills/cdad-cycle/packets/roles/`), una frase parafraseada de obligación mínima + puntero verbatim `documentary-contracts.md` por rol; sin copiar frases normativas de la referencia ni de `design-principles.md`; sin ninguna mención a sandbox:

| Bloque | bytes | sha256 |
|---|---|---|
| architect.md | 873 | `668b9df2…82e3d5` |
| implementer.md | 829 | `d93b44e4…964fbe` |
| reviewer.md | 1039 | `bbc4b6f2…d16bd6` |
| scribe.md | 473 | `9afe0f3e…c1ba63a` |
| test-writer.md | 626 | `a211e9cf…2f470c` |

**22 agentes promovidos** (`agents/` y `agents/claude-code/`, 11 × 2 runtimes) regenerados exclusivamente por `make agents`; sin edición manual. El diff incorpora además la propagación de los cambios de `sources/roles/` de T3 (p. ej. la directiva del implementer «implementation product (code, or a documentary product expressly commissioned)»), que estaba pendiente de promoción.

**Commit:** `2a918b72775a04e277114bb0696af10e5967fc80` — `feat: transport documentary obligations to role packets and regenerate agents` (27 archivos, +137/−10). Solo los 5 bloques y los 22 agentes. `docs/.cdad-state.json` (binding ajeno, ya modificado al intake) y el `discovery.md` no trackeado de 010-000 quedaron **fuera** del commit; no toqué tests, docs, `sources/roles/`, `SKILL.md`, la referencia, `scripts/`, `install.sh` ni el esquema.

### 3. `make staging` dos veces — bytes idénticos

```bash
make staging        # rc=0
find build/staging -type f ... sha256sum por archivo > run1.sha
make staging        # rc=0
... > run2.sha
diff run1.sha run2.sha   # sin salida → STAGING_IDENTICAL_ACROSS_TWO_RUNS
sha256sum run1.sha run2.sha  # 9f556681a8d90feb1a2e2253ab583302942753a714453d99098d2f6edd07b17c (ambos)
```

23 archivos por corrida (11 agentes × 2 runtimes + `manifest.json`). Tras el tercer `make staging` implícito de `make agents`, el árbol de staging seguía coincidiendo con `run2.sha`.

### 4. `make agents` y promoción

```bash
make agents   # rc=0; cp build/staging/agents/{opencode,claude-code}/cdad-*.md → agents/ y agents/claude-code/
```
22 archivos promovidos; los agentes genéricos y las variantes Odoo de ambos runtimes llevan el puntero y la obligación heredada de `sources/roles/`.

### 5. Render representativo — los bloques viajan

En una copia descartable (`/tmp/opencode/t4-render/product`, `active_packet` saneado solo en la copia) se prepararon paquetes frescos con la CLI y se renderizaron con `render` para los cinco roles delegados:

```text
architect:     rc=0  duty=1  pointer=1   (render de paquete publicado, binding de unidad)
test-writer:   rc=0  duty=1  pointer=1
implementer:   rc=0  duty=1  pointer=1
reviewer:      rc=0  duty=1  pointer=1
scribe:        rc=0  duty=1  pointer=1
```

El `instruction_sources` del header renderizado fija el sha256 exacto del bloque vigente (p. ej. `roles/implementer.md … d93b44e4…964fbe`), es decir el paquete transporta los bytes actuales del bloque, no una copia. Nota: el único par que no admitió preparación nueva fue `architect/discovery` (proyección de unidad ya publicada, INV-3/PD-4); para architect se renderizó un paquete publicado en la copia, que ya lee el bloque nuevo.

### 6. Instalación aislada con bytes verificados

`CDAD_INSTALL_ROOT` **dentro del repo** (`build/t4-install-check`) fue **rechazado por el propio instalador**: `ERROR: Managed install destination overlaps the source repository` — guarda de install.sh, no un fallo mío. Usé entonces una raíz absoluta existente y descartable en el workspace del proyecto, hermana del repo: `<workspace>/projects/cdad/t4-install-check-010-001` (nunca HOME real, `~/.claude` ni `~/.config/opencode`).

```bash
CDAD_INSTALL_ROOT=<workspace>/projects/cdad/t4-install-check-010-001 CDAD_SKILL_EXTRA_DIRS="" bash install.sh
# rc=0 · "Verify: PASS — 11 cdad agents present after install"
```

```text
REF_BYTES_OK .config/opencode/skills/cdad-cycle    (cmp contra la fuente: idénticos)
REF_BYTES_OK .claude/skills/cdad-cycle             (cmp contra la fuente: idénticos)
AGENT_BYTES_OK opencode    (11 archivos == build/staging/agents/opencode)
AGENT_BYTES_OK claude-code (11 archivos == build/staging/agents/claude-code)
POINTER_COUNT instalado: 22 / 22
```

Raíz de instalación eliminada después. Sin cambios en la instalación global.

### 7. Módulo completo y regresiones

```bash
python3 -B -m unittest tests.test_010_001_documentary_contracts
# ...........  Ran 11 tests in 8.945s  OK   (grupo D incluido)
```

```bash
python3 -B -m unittest tests.test_cdad_generate tests.test_role_packet_render \
  tests.test_role_packet_consumers tests.test_install_ownership \
  tests.test_install_review5_regressions tests.test_006_004_u3_principle_single_source
# Ran 64 tests in 418.296s  OK
```

Techo estático vigente sin elevar: máximo **3709 bytes** (reviewer/plan-review) sobre 12000.

### 8. `make validate`

```bash
make validate   # rc=2 · Assert PASS: 182 · Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
```

Único fallo: **deriva de instalación global** (`install.sh --check`): falta `~/.claude/skills/cdad-cycle/references/documentary-contracts.md`, difiere `SKILL.md` y difieren los 22 agentes instalados en `~/.claude/agents` y `~/.config/opencode/agents`. Es la deriva de entorno esperada por no haber publicado los cambios globalmente, **no una regresión**; no instalé nada global, conforme al encargo.

### 9. Límites honestos (PD-15 / INV-06 / INV-08)

- El verde es **estructural**: no acredita fidelidad ni suficiencia semántica; eso es T5 y el dueño.
- El paquete despachado queda **obsoleto** por diseño tras cambiar los bloques (su header fija los sha256 anteriores); no se reutiliza para despachos posteriores.
- Una obligación textual o un paquete **no es un sandbox** ni prueba ausencia de escrituras transitorias.
- Suite completa **no ejecutada**: la política del paquete la corre una sola vez quien cierra (T6).
