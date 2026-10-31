# Informe del implementer — 010-002 T8, subfase REVIEW-FIX

## Intake (ruta C) — validado antes de trabajar

| Comprobación | Resultado |
|---|---|
| Bloque de identificación único, sin paquete inline ni mezcla A+C | OK |
| `packet_id`, `contract.path`, `contract.sha256`, `execution_id` contra `REQUEST.json` y `PACKET.md` | Coinciden |
| `execution.json` | `schema_version: 2` (v2, ruta C admisible) |
| `cdad_packet.py validate-request` | `rc=0` |
| `cdad_packet.py validate-packet` | `rc=0` |
| `cdad_packet.py render` completo vs `PACKET.md` | `diff -u` vacío, sha256 `2f174c9c…3aace` en ambos |
| SHA-256 del contrato `spec.md` | `0d630c49…81abc` — coincide |

No se cargaron skills de ciclo completo; solo se leyó el producto y los tests que hacen de oráculo.

## Hallazgos verificados contra su evidencia original

- **B1**: confirmado en las cuatro superficies que lista el RED (`sources/agents/adapters/{opencode,claude-code}.md` y los dos `cdad-orchestrator.md` generados). La cláusula literal estaba dentro de «Mechanism (native)». La sección equivalente de `sources/roles/orchestrator.md:79-83`, `skills/cdad-cycle/SKILL.md:142-148` y `references/sub-agent-strategies.md:163-167` ya decía lo correcto → la corrección se alineó a esa formulación.
- **B2**: confirmado en las nueve superficies (tres fuentes + seis agentes `-odoo`). La matriz de aplicabilidad vive en `cdad-section:directive`, en otra sección, y no subordinaba el delta.

## Archivos modificados (5 ubicaciones + 8 generados)

### B1 — 1/2 `sources/agents/adapters/opencode.md` (delegation)

**Antes:**
> `…required variant that is not published is rejected mechanically before launching the role work: fail closed, never substitute it silently by the generic agent.`

**Después:**
> `…required variant that is not published is a procedural duty, not a mechanical guard: the orchestrator checks that the derived agent is published and, when it is not, stops that part of the engagement and reports the block to the user — or to the owner, as the case requires — never substituting the generic agent silently. The mechanical rejection before launching the role work belongs to the external adapter alone; no new mechanical guard is promised for this native path or attributed to the module.`

### B1 — 2/2 `sources/agents/adapters/claude-code.md` (delegation)

Texto idéntico al anterior (misma sección, `Agent` tool en la línea previa, no tocada).

### B2 — 3/5 `sources/roles/reviewer.md` (`cdad-section:odoo`)

**Antes:**
> `- Evidence required: green make test-clean + pasted output; oca-checks with 0 findings; pylint-odoo with no blocking E/W; make lint --all with 0 blocking issues (…)`

**Después:**
> `- Evidence required only when the real diff touches addon code, views, security or data of the addon: green make test-clean + pasted output; oca-checks with 0 findings; pylint-odoo with no blocking E/W; make lint --all with 0 blocking issues (…)`
> `- The real diff decides. A documentary-pure diff keeps the domain judgment and demands no addon battery for an addon it does not modify; a mixed engagement keeps both families and both evidences. A documentary label never exempts code, views, security or data that the diff modifies.`

### B2 — 4/5 `sources/roles/implementer.md` (`cdad-section:odoo`)

**Antes:**
> `- GREEN evidence: green make test, installation gate make test-clean if the spec marks it, and clean lint (make lint --all, 0 blocking issues, pasted).`

**Después:**
> `- Addon evidence, only when the product or the diff touches addon code: green make test, installation gate make test-clean when the spec marks it, and clean lint (make lint --all, 0 blocking issues, pasted).`
> `- A documentary-pure product keeps the domain knowledge and demands no addon tests, installation or lint for an addon it does not modify; a mixed engagement keeps both families on its respective products, and the real diff prevails over the label.`

### B2 — 5/5 + P-5 `sources/roles/test-writer.md` (`cdad-section:odoo`)

**Antes:** solo la batería incondicional (`TransactionCase, mandatory @tagged … RED with make test-one, AUDIT with make test`).

**Después (añadido, sin tocar la batería ni la prohibición de comandos crudos):**
> `- Addon test obligations, only when the product or the diff touches addon code: addon tests keep the framework, tags, fixtures and Odoo runner above; a documentary-pure engagement builds its committed documentary verifier and demands no TransactionCase, @tagged or addon runner just because the project domain is Odoo; a mixed engagement separates both regimes.`
> `- A documentary verifier is not an addon test: it requires neither TransactionCase nor @tagged. Its execution uses the project's declared runner; when that runner does not cover it, the engagement declares the evidence limit and no raw command outside the make contract is emitted, nor is any permission widened.`

### Generados (8, por `make agents`, nunca a mano)

`agents/cdad-orchestrator.md`, `agents/claude-code/cdad-orchestrator.md` (B1 compone la sección de delegación del adaptador), y los seis `agents[/claude-code]/cdad-{reviewer,implementer,test-writer}-odoo.md` (B2 copia la sección Odoo).

## Comandos exactos y salidas

| Comando | rc | Salida |
|---|---|---|
| `python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py -k 'mechanical or odoo_applicability or delta'` | 0 | `3 passed, 26 deselected in 1.10s` (antes: `2 failed, 1 passed`) |
| `python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py` | 0 | `29 passed in 39.15s` |
| `python3 -B -m pytest -q tests/test_010_002_documentary_role_properties.py` | 0 | `7 passed in 185.57s (0:03:05)` |
| `python3 -B -m pytest -q tests/test_cdad_generate.py` | 0 | `10 passed in 2.92s` |
| `python3 -B -m pytest -q tests/test_010_001_documentary_contracts.py` | 0 | `11 passed in 9.05s` |
| `python3 -B -m pytest -q tests/test_006_004_u3_principle_single_source.py::TestPd13StaticBlockCeiling` | 0 | `1 passed in 1.65s` — techo estático sin cambios (`packets/` intacto) |
| `make agents` ×2, `sha256sum` de `agents/` + `build/staging` | 0 | 47 archivos, `diff -u` vacío entre generaciones; agregado `d4812217…` |
| `git archive HEAD \| tar -x` + `make agents` en descartable, `diff -rq` contra `agents/` | 0 | **NO DIFFERENCES** (agregado `ab3f1032…`) |

Suite completa: **no ejecutada** — política del paquete (la corre quien cierra).

## Verificación de los detectores (no de la prosa)

Ejecutando los helpers del propio test sobre las fuentes corregidas:

- `native_mechanism_region` localiza la región en ambos adaptadores (1022/1023 chars); `claims_new_mechanical_guard(region)` → `[]`; obligación procedimental y «sin sustitución silenciosa» → sin faltantes; la descripción del adaptador externo conserva `UNPUBLISHED_VARIANT + MECHANICAL_REJECTION + BEFORE_LAUNCH`.
- `unconditional_addon_battery(odoo_section(...), role)` → `[]` en reviewer, implementer y test-writer, conservando cada batería (`make test-clean/oca-checks/pylint-odoo`, `make test/clean lint`, `@tagged/make test-one/make test`).

## Invariantes y alcance

- **Tests intactos:** `git status -- tests` vacío; `git diff --stat HEAD~1 HEAD -- tests` vacío.
- No se tocó generador, instalador, guardas, permisos, defaults, esquema ni CLI. Sin archivos fuera de `sources/roles`, `sources/agents/adapters`, `agents` y `build/staging` (ignorado por git).
- Los cambios preexistentes en `docs/.cdad-state.json`, la desviación I-10 y los evidencia untracked ajenos quedaron fuera del commit.
- Calidad (5 checks aplicados al producto documental): obligación con salida temprana explícita (detener y reportar), estado ilegal imposible (nativa ya no declara guarda mecánica que no existe), regla única por sección sin duplicar la matriz, fail-loud (el bloqueo se reporta, nunca se sustituye en silencio), naming intencional («procedural duty» vs «mechanical rejection»).

## Commit

- **`735d977c9e1a7816d56ca65fdfd1865c986d0841`** — `fix(010-002): review-fix de B1 y B2 (via nativa procedimental y deltas Odoo condicionados)`
- Alcance: 13 archivos, +106/−30 (5 fuentes + 8 agentes declarados).

## Límites honestos

- La corrección es de instrucciones: los controles acreditan presencia y polaridad estructurales, no conducta efectiva de modelos (PC-13).
- B3 (registro de I-10) y N1 (evidencia untracked) **no** formaban parte de este encargo y siguen abiertos: la re-revisión limitada que pide el dictamen debe cubrirlos.
