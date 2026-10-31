---

# INFORME GREEN — T4 de 010-002-documentary-role-integration

**Rol:** implementer · **Subfase:** green · **Ruta C (respaldo explícito por archivo)** · **Plan task:** T4

## 0. Intake (ruta C) — validación previa

| Comprobación | Comando | Resultado |
|---|---|---|
| Contrato pineado | `sha256sum docs/specs/010-002-documentary-role-integration/spec.md` | `0d630c49…81abc` = bloque de identificación ✅ |
| Render canónico | `python3 scripts/cdad_packet.py render --request .cdad/packets/010-002-…-implementer-green-001/REQUEST.json > /tmp/opencode/rendered-packet.md` | rc=0 |
| PACKET == render | `diff -u /tmp/opencode/rendered-packet.md …/PACKET.md` | sin diferencias ✅ |
| Paquete validado | `python3 scripts/cdad_packet.py validate-packet --request … --packet …` | rc=0 ✅ |
| Contexto de ejecución | `.cdad/executions/exec-010-002-documentary-role-integration-001/execution.json` | `schema_version: 2` ✅ |

Identificación recibida (packet_id, contract+sha256, execution_id) coincide con REQUEST.json/PACKET.md; sin cuerpo inline (admissible en C), sin mezcla de rutas.

## 1. Estado inicial y final

- RED de partida (medido antes de tocar producto): `10 failed, 3 passed`.
- GREEN final (comando focal declarado):

```
$ python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py \
    -k 'TestEngagement or TestOdooApplicability or TestDispatchDoctrine or TestDistribution'
13 passed in 12.70s
```

Los trece tests: `TestEngagement` 3, `TestOdooApplicability` 5, `TestDispatchDoctrine` 2, `TestDistribution` 3. Ningún test fue modificado: `git diff HEAD~1 --stat -- tests/` → 0 líneas.

## 2. Archivos modificados (44 en el commit)

- **`sources/roles/`** (6): `architect.md`, `test-writer.md`, `implementer.md`, `reviewer.md`, `orchestrator.md`, `scribe.md` — matriz de aplicabilidad PC-04/PC-05 (documental / addon / mixto) en la sección `directive` (se compone en el agente genérico **y** en la variante odoo), declaración de fronteras/seis roles sin variante documental, y delimitación de obligaciones de addon que eran incondicionales.
- **`sources/agents/adapters/`** (2): `opencode.md`, `claude-code.md` — derivación canónica del destinatario, rechazo mecánico de variante no publicada antes de lanzar, sin fallback silencioso.
- **`skills/cdad-cycle/SKILL.md`** — §3.1: doctrina de selección coherente con el mecanismo.
- **`skills/cdad-cycle/references/handoff-prompts.md`** — nuevo `## Documentary engagement — operating procedure`: siete declaraciones por los campos existentes, pasos de preparación/aceptación, fronteras y parada ante superposición con insumos protegidos; remite a `documentary-contracts.md` sin reproducir la norma.
- **`skills/cdad-cycle/references/sub-agent-strategies.md`** — eliminada «stack ausente u otro valor → genérico»; regla de sufijo, variante ausente y sin sustitución silenciosa.
- **`skills/cdad-cycle/packets/roles/*.md`** (5) — una línea de conservación de fronteras y ausencia de variante documental (techo intacto).
- **`skills/odoo-expert/SKILL.md`** — casa única de la frontera de addon (`## Addon work vs. module documentation`).
- **`skills/odoo-architect/SKILL.md`** — inventario/entorno exigibles solo antes de modificar un addon; frontera y régimen documental.
- **`skills/odoo-test-writer/SKILL.md`** — verificador documental ≠ test de addon; tests de addon verifican producto de addon bajo `tests/`.
- **`skills/odoo-reviewer/SKILL.md`** — diff documental vs diff de addon; addon oculto bajo etiqueta se informa y bloquea; sin permiso retroactivo.
- **`skills/odoo-make-env/SKILL.md`** y **`references/run-budget-protocol.md`** — aplicabilidad del contrato de suite/presupuesto: sin addon modificado no hay corrida ni presupuesto.
- **`agents/**`** (22): regenerados con `make agents`, nunca editados a mano; `build/staging` regenerado.

## 3. Reproducibilidad y techo

```
$ make agents  &&  make agents      # dos generaciones, comparación de bytes
generation diff: []                 # agentes + staging + manifests idénticos
promoted != staging: []             # 22 agentes promovidos == staging
manifest entries: 22 (sha256 + sources por artefacto)
```

```
$ python3 -B -m pytest -q tests/test_006_004_u3_principle_single_source.py -k TestPd13StaticBlockCeiling -s
PD-13/V-4: máximo 3864 bytes (reviewer/plan-review), techo declarado 12000 bytes
1 passed
$ python3 -B -m pytest -q tests/test_static_block_ceiling.py   → passed
```

Techo **no elevado** (3864/12000; +1 línea por bloque de rol).

## 4. Regresiones declaradas

| Comando | Resultado |
|---|---|
| `pytest -q tests/test_cdad_generate.py tests/test_static_block_ceiling.py` | 12 passed in 4.35s |
| `pytest -q tests/test_cdad_generate.py tests/test_004_001_t6.py` | 19 passed in 75.91s |
| `pytest -q tests/test_010_001_documentary_contracts.py` | 11 passed in 11.23s (incluye INV-06: ningún consumidor copia frases de la norma) |
| `pytest -q tests/test_006_004_u3_principle_single_source.py` | 15 passed in 5.04s |
| `pytest -q tests/test_install_ownership.py tests/test_install_review5_regressions.py tests/test_007_006_withdraw_and_republish.py` | 78 passed in 343.94s (entornos y destinos aislados de los propios tests) |
| `bash tests/validate-odoo-specialization.sh` | PASS 68 · FAIL 0 |

## 5. Inventario de las cuatro referencias candidatas (decisión por archivo)

| Archivo | Decisión | Acción |
|---|---|---|
| `skills/odoo-expert/references/evidence-and-quality.md` | Regla **ya contextualizada** a trabajo de addon (habla del módulo listo con evidencia: lint, OCA, tests, instalación) | No editado |
| `skills/odoo-make-env/references/run-budget-protocol.md` | Aplicabilidad **incondicional a delimitar** (presupuesto de suite por etapa) | Añadida nota de aplicabilidad: presupuesto 0 si no se modifica addon; presupuestos/recetas intactos |
| `skills/odoo-make-env/references/odoo-sh.md` | Referencia **técnica sin conflicto** (implementación del make contract en odoo.sh) | No editado |
| `skills/odoo-make-env/references/odoo-19-traps.md` | Referencia **técnica sin conflicto** (traps de API Odoo 19) | No editado |

## 6. Decisiones de diseño declaradas

- **Casa única de la frontera de addon:** el enunciado completo vive en `odoo-expert`; las otras cuatro skills declaran su aplicabilidad y la lista de directorios en sus propias palabras (patrón PC-14 de 010-001) sin duplicar recetas ni normas ajenas.
- **Matriz en `directive`** (no en `odoo`): PC-04/05 exige que los **artefactos distribuidos** la lleven, incluidos los agentes genéricos de ambos runtimes.
- **Sin tocar generador, instalador, guardas ni permisos.** No hubo necesidad de detener ninguna parte.
- **`build/staging` y `.cdad/`** permanecen ignorados por git; `docs/.cdad-state.json` (modificado antes de esta tarea) y los `docs/` no rastreados quedaron **fuera** del commit.

## 7. Commit

```
c0126040 feat: implement documentary engagement procedure, Odoo applicability and recipient doctrine
44 files changed, 586 insertions(+), 51 deletions(-)
```

Ninguna escritura fuera de `write_scope` (`sources/roles`, `sources/agents`, `skills`, `agents`, `build`).

## 8. Límites honestos (PD-15)

Verificación estructural: un verde aquí no acredita fidelidad semántica, suficiencia de una exclusión ni conducta efectiva de modelos. La frontera de addon en una sola casa con consumidores por referencia es una decisión de diseño declarada, revisable por el reviewer contra el contrato; la matriz se distribuye también en los agentes genéricos por exigencia de PC-04/05.
