# Review — 004-003 T1: contract-kind de plan borrador (PD-1)

> Materializado por el orquestador desde el TEXTO FINAL del reviewer (ADR-003).
> Modelo: `mofgw/glm-5.3-flash` (familia ≠ implementer). Sesión:
> `<ses-4>`. Paquete:
> `004-003-planning-procedures-reviewer-review-001`. Dictamen:
> **changes-required** (2 bloqueantes, 3 opcionales).

**Contrato:** `docs/specs/004-003-planning-procedures/spec.md` (sha256 verificado: `ba395fedf46b…bf766` ✓) · **Diff:** `1f51f03..b61f1a2` (implementación `b61f1a2`; RED `1f51f03` revisado aparte porque el rango lo excluye) · **Modo:** read-only, sesión independiente del implementer ✓ anti-sesgo.

## Verificación del autor (re-ejecutada por el reviewer)

| Comando | Resultado |
|---|---|
| `python3 -m unittest tests.test_004_003_t1_draft_contract -v` | `Ran 2 tests in 0.974s — OK` |
| `python3 -m pytest tests/test_packet_prepare.py tests/test_role_packet_render.py tests/test_role_packets.py tests/test_role_packet_consumers.py tests/test_role_packet_review_regressions.py tests/test_static_block_ceiling.py -q` | `54 passed in 145s` |
| `python3 -m pytest tests/test_004_002_*.py -q` | `95 + 61 + 43 passed` |
| `python3 -m pytest tests/test_004_001_*.py tests/test_install_ownership.py tests/test_install_review5_regressions.py tests/test_bash_policy_selection.py tests/test_cdad_generate.py -q` | `71 passed` |
| `python3 -m pytest tests/test_cdad_adapters_opencode.py -q` | `3 passed` |

**~326 tests OK, 0 fallos.** La implementación no rompe ninguna regresión existente y el GREEN cumple los 2 tests RED.

## Archivos modificados en el diff

1. `skills/cdad-cycle/scripts/cdad_packet.py` (+67/−10) — `b61f1a2`
2. `skills/cdad-cycle/assets/active-packet.schema.json` (+1/−1) — `b61f1a2`
3. `docs/.cdad-state.json`, `dispatch-ledger.md`, `supervision-record.md` — `cddbe96`, `d2a11b2` (registro del orquestador; declara la desviación del oráculo)

## Hallazgos

### F1 — CRITICAL · BLOCKING · Bucket: h — La superficie `draft-plan` está abierta a TODOS los roles: un paquete `implementer green` puede despacharse contra un plan NO aprobado (bypass de gate)

**Ubicación:** `cdad_packet.py`, `prepare()` ~2288–2297 (el bloque de flags aplica a cualquier `role/substage`); `validate_request()` no restringe `draft-plan` por rol (~709+).

**Evidencia reproducida** (fixture aislado, mismos helpers de `tests/test_packet_prepare.py`):

```
$ prepare --role implementer --substage green --contract-kind draft-plan \
    --contract-path docs/planning-contract-draft.md --plan-version draft-001
rc: 0
published contract: {"kind": "draft-plan", ..., "plan_version": "draft-001"}
write_scope: [{"class": "implementation", "root": "src"}, {"class": "implementation", "root": "lib"}, {"class": "implementation", "path": "install.sh"}]
```

**Racional:** el spec aprueba la superficie para **revisión** (PD-1: "prepare puede renderizar un paquete de **reviewer**"; §2 tabla). El invariante 4 (§3): *"la revisión de plan **no** concede permiso de implementación"* — y aquí un contrato borrador vincula directamente a un implementer con write scope de implementación. Ni el spec ni el supervision-record declaran esa apertura como decisión. Confianza ≥95%.

**Remedio estructural:** restringir la triple flag (o `draft-plan` en `validate_request`) a `role == "reviewer"` y añadir el caso negativo al suite T1.

### F2 — Required · BLOCKING · Bucket: h — La emisión del paquete borrador lleva una marca de aprobación (`"purpose": "approved contract"`)

**Ubicación:** `cdad_packet.py:2316`: `"inputs": [{"path": contract_path, "purpose": "approved contract"}]` — hardcodeado para todo kind.

**Evidencia reproducida** (REQUEST.json y PACKET.md del paquete draft-plan):

```
P1 contract: {"kind": "draft-plan", "path": "docs/planning-contract-draft.md", "plan_version": "draft-001", ...}
P1 inputs:   [{"path": "docs/planning-contract-draft.md", "purpose": "approved contract"}]
PACKET.md:   - docs/planning-contract-draft.md: approved contract
```

**Racional:** PD-1 exige que la emisión del borrador lleve el sha/versión *"no una aprobación"* y que el borrador *"sin marcarlo approved"*. El propio docstring-oráculo del test T1 declara *"never an approval marking"*. El test positivo no aserta el campo `inputs`, por eso pasó. Confianza ≥95%.

**Remedio:** `purpose` no aprobatorio cuando el kind es `draft-plan`; extender el test positivo para asertar la ausencia de marca de aprobación.

### F3 — Nit · OPTIONAL · Bucket: m — `validate_request` acepta un contrato `approved-*` con `plan_version: null`

`cdad_packet.py:713` (`elif plan_version is not None:`) distingue por **valor**, no por **presencia de clave**, aunque el chequeo de esquema sí distingue por presencia. Sin ganancia de capacidad. **Remedio:** rechazar por presencia de clave.

### F4 — Nit · OPTIONAL · Bucket: l — Validación de path duplicada en la rama draft

`validate_request` llama `_project_path(..., "contract.path")` en la rama `is_draft` (~721) y de nuevo incondicionalmente (~733). Redundante.

### F5 — Optional-Consider · Bucket: m — Huecos de cobertura negativa en el suite T1

Sin test: (a) `draft-plan` sin `plan_version`; (b) forja con `approved-epic-plan`; (c) kind desconocido vía flags; (d) **implementer green + draft-plan** — el hueco que dejó pasar F1. Nota cosmética: `--plan-version ""` da "requires … together" en vez de "non-empty plan_version".

## Aspectos correctos (verificados)

- El guard de forja `approved-*` + `plan_version` funciona: rc≠0 con diagnóstico explícito, sin publicación (rc=2 antes de cualquier escritura).
- Flags parciales y versión vacía rechazadas; `resume` y `propose-policy` blindados contra las 3 flags nuevas.
- Esquema y validador de estado consistentes con `VALID_CONTRACT_KINDS`.
- Tests black-box por subprocess, mapeo explícito a PD-1, sin leer implementación; desviación de oráculo honestamente declarada.
- Sin N+1 ni cambios de hot paths.

## Abstenciones

- **No ejecutó la suite completa con `unittest discover`**: excede >10 min y el runner del proyecto es `pytest`; bajo unittest bare 3 módulos 004-002 fallan por imports relativos (preexistente y ajeno a este diff, confirmado: pasan bajo pytest).
- **No ejecutó `validate-consistency.sh` / `validate-odoo-specialization.sh`**: regresiones declaradas de **T2**, no de T1.
- **No verificó los pasos de gate de dispatch de los commits de docs** (`cddbe96`, `d2a11b2`): los lee como evidencia declarada.
- **No constató si algún consumidor externo de `REQUEST.json` asume `purpose == "approved contract"`**: F2 es defecto observable por sí mismo; la búsqueda de consumidores dependientes queda fuera del alcance del paquete.

**Resumen:** 2 BLOCKING (F1, F2), 3 no-bloqueantes (F3–F5). Ambos bloqueantes tienen remedio localizado en `cdad_packet.py` (<10 líneas) más extensiones del suite T1; ninguno invalida el diseño del guard de forja, que es correcto.
