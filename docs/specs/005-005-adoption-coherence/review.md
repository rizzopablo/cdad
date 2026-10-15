# Review stage 4 — 005-005-adoption-coherence (T1..T4)

**Contrato revisado:** `docs/specs/005-005-adoption-coherence/spec.md` — sha256 `9349b0c1468de48b4223798e4209a1f16959ff5f0869a39c101ca039f7fe4d22` **verificado contra los bytes reales** (`sha256sum` coincide; entrada pineada vigente en `stage_history` con `contract_path` correcto).
**Diff:** `git diff f148304..HEAD` (vida completa de la feature en `codex/epic-005-real-operation`): 27 commits, 30 archivos, +3774/−107. Commits de producto `65e887f` (T1 GREEN), `4b990bb` (T2 GREEN + enmienda), `6f7363c` (T3a GREEN), `b4ce4d9`+`1f1cc63` (T3b), `9e5215f` (T4 GREEN version.txt); de tests `dc66cb2, 3d9e854, fd1aaa3, 012ccac, eda293c` (+ RED-FIX del oráculo de versión).
**Producto:** `skills/cdad-cycle/scripts/cdad_packet.py`, `skills/cdad-cycle/references/**`, `skills/cdad-cycle/packets/**` y `SKILL.md`, `install.sh`, `docs/specs/005-001-idle-and-v7-bootstrap/{spec.md,review.md}`, `docs/epics/epic-005-real-operation/handoff-opencode*.md`. Tests: `tests/test_005_005_t{1,2,3,4}*`.

## Veredicto

**`changes-approved` — sin bloqueantes.** La feature cumple lo observable del contrato (PD-1..PD-18, INV-1..INV-8) y **confirma el pedido del encargo §4: elimina contradicciones y trabajo manual SIN sumar restricciones al camino normal de `prepare`** (PD-5/INV-4 con test focal; la validación completa del encargo resultante queda confinada al sub-modo `--replace-packet`, coherente con D1/PD-22). Verificación propia: **suite completa canónica 649 passed / 0 fallos** (pytest, 16:41), focales y regresiones OK (62 + 11 tests), `make validate` con exactamente los **2 FAIL F011 preexistentes declarados en R6** (mismo motivo: `install.sh --check` y A3 de odoo-specialization), como prometido en R6.

Si se confirma el veredicto: el orquestador pasa a stage 5 (cierre: registro de evidencia + Memory Bank + los VERIFY del dueño abiertos), con los opcionales listados que NO prolongan el ciclo.

## Bloqueantes

Ninguno.

## Opcionales (no bloqueantes; no extienden el ciclo)

### O1 — Camino silencioso cuando el registro de activación existe pero es ilegible · OPTIONAL · Bucket: l
- **Ubicación:** `cdad_packet.py` `_activation_registry` (≈:2461-2470) + `_derived_source_dir` (≈:2477-2481).
- **Problema:** Si `.cdad/activation.json` existe pero el JSON es corrupto o `adopted_root` falta/inválido, el resolver retorna None y `_derived_source_dir` cae silenciosamente al camino global/HOME sin diagnóstico que nombre el registro — hueco delgado del INV-7 «cambio de origen nunca silencioso» (la otra rama, con registro legible + manifiesto previo, sí diagnostica el brazo b de PD-13; sin manifiesto previo quedaría sin aviso).
- **Consecuencia:** Un proyecto con el registro corrupto cambia de instalación silenciosamente — la misma clase del caso MIX-V6V7 real.
- **Cierre verificable:** una rama de una línea: si `path.is_file()` pero el parseo falla → `PolicyError rc=2` que nombre el registro corrupto (re-activar), o warning stderr que nombre el registro y el motivo. Coste bajo, código pequeño.

### O2 — Diagnóstico de contradicción sin marcador de versión no explicita «versión desconocida» · OPTIONAL · Bucket: l
- **Ubicación:** `_describe_installation` (≈:2521-2527).
- **Problema:** Si el `version.txt` del origen no existe, el diagnóstico de contradicción nombra el registro y las **rutas** pero no dice que una de las versiones es desconocida (p. ej. en instalaciones anteriores al marcador).
- **Cierre verificable:** cuando `_installation_version` es None, el texto del aviso añade "(version unknown — no marker at <root>)". Barato (el nombre de version es honesto, nunca inventado — esta mejora lo explicita).

### O3 — PD-1 sin test dedicado para sus rebanadas no-input · OPTIONAL · Bucket: l
- **Ubicación:** `tests/test_005_005_t1_replace_conserved.py`.
- **Problema:** PD-1 también exige "`invariants`/`evidence_required` strings no vacíos, `expected_output` no vacío" en el encargo resultante. No hay test del reemplazo con esos campos conservados en vacío; el comportamiento se cubre vía `validate_request` (≈`:795-796`, preexistente y probado en 005-001), pero la trazabilidad PD-1→test en T1 invoca el reuso sin ejercitarlo de front.
- **Cierre verificable:** un subtest que intente el reemplazo con `--expected-output ''`→ rc=2, sin efectos.

### O4 — `CDAD_OPENCODE_AGENTS_DIR` puede filtrarse al CLI de los tests T1 · OPTIONAL · Bucket: l
- **Ubicación:** `run_cli` de `tests/test_005_005_t1_replace_conserved.py` (el `env` del subproceso no se esteriliza; T3/T4 sí lo hacen en `run_prepare`/`run_packet`).
- **Problema:** En una máquina con esa variable seteada, el `prepare` de los tests T1 puede derivar agentes desde una carpeta ajena. Aquí corre con ella ausente y los asserts del reemplazo no dependen del origen → riesgo de flakiness en el entorno del dueño, no un defecto actual.
- **Cierre verificable:** limpiar `CDAD_OPENCODE_AGENTS_DIR` (y `CDAD_PREMIUM_MODEL_`) en `run_cli` (una línea).

### O5 — La instalación REAL vigente (v8) sigue con `source_version: null` · FYI (observación del orquestador; no defecto del diff)
- El manifiesto vigente proviene de una instalación **anterior** al marcador que 005-005 introduce; la versión nueva del repo sí lo declara (verificado in situ por `test_t4_pd14_*` con la instalación aislada). El despliegue de la versión nueva es **tarea aparte del dueño** (encargo). Cierre verificable post-despliegue: `source_version` de `.opencode/agents/.cdad-derived.json` == contenido del `version.txt` de la raíz del despliegue.

## Auditoría test ↔ postcondición (AP-13/AP-14)

| PD | Test | Camino verificado |
|---|---|---|
| PD-1 (encargo completo) | `test_pd02` + `test_pd03` (conservados invalidados) + `validate_request` preexistente (no-vacíos y contención de inputs) | Dominio de validación = encargo resultante completo (conservado + corregido) |
| PD-2 | `test_pd02` | input CONSERVADO inexistente → rc=2 con campo/motivo/opción; sin publicar; paquete anterior byte-idéntico; state intacto; control positivo interno rc=0 |
| PD-3 | `test_pd03` | alcance conservado fuera de política (selector no clasificado, read+write) → rc=2 campo/motivo/opción; control positivo interno rc=0; el arco «clase no admitida» es inalcanzable como conservado (el argv equivalente es rechazado por el `prepare` normal mismo — probe del paquete) |
| PD-4 | `test_pd04` | reemplazo repetido con la corrección → rc=0, sucesor con insumo existente; `.superseded.json`; sin entradas nuevas en stage_history/epic_history (INV-2) |
| PD-5 | `test_pd05` | camino normal acepta un input declarado inexistente (INV-4: sin restricción nueva) |
| PD-6 | `test_pd06` | `--input -` (lista vacía) sigue valido en el reemplazo |
| PD-7 | `test_pd07` | pisos del rol intactos en el sucesor tras correcciones (INV-5, PD-21 no relajado) |
| PD-8 | `test_pd8` | sección ÚNICA «Test evidence policy» con título exacto y los 5 puntos; la equivalencia remite a re-entry.md sin copiarla (INV-6) |
| PD-9 | `test_pd9` + `test_t4_pd09` (in situ) | barrido sin afirmaciones de frecuencia por GREEN; los 13 consumidores declarados remiten a la política |
| PD-10 | `test_pd10` + `test_t4_pd10` (in situ) | GREEN/refactor/review-fix alineados (sin «required full regression suite», con remisión explícita) |
| PD-11 | `test_pd11` | enmienda fechada 2026-10-09 en la spec de 005-001 con el recorrido ejecutado (record-dispatch/receive/validate-receipt/orden pre-test-writer; paquete prepared no despachado) y decisión explícita sobre el pin; **re-registro del pin verificado por esta review**: `stage_history` con `specification / amendment: PD-17 (T2 de 005-005)` y `contract_sha256=8ba37ce2…` == sha256 real del archivo enmendado |
| PD-12 | `test_pd12` | orden variable > registro > global; con registro y sin variable → `source_dir` = `<adopted_root>/.config/opencode/agents` registrada, no HOME; control positivo del orden 1 |
| PD-13 | `test_pd13` | brazo (a) variable vs registro y brazo (b) resuelto vs manifiesto previo (análogo sintético MIX-V6V7): diagnóstico stderr nombra `.cdad/activation.json` y las DOS versiones en juego; control de coherencia no dispara el aviso |
| PD-14 | `test_pd14` + `test_t4_pd14` (in situ) | manifiesto publicado declara `source_version` == `version.txt` de la raíz de la instalación (oráculo acepta hex 7-64, versión con puntos, etiqueta v<N>); la versión cargada es verificable desde el artefacto |
| PD-15 | documental, sin test (declarado en plan T3) | `opencode-delegation.md` §Reload: dato del dueño como dato; comprobación aislada registrada (CLI instalado 1.18.32, HOME/XDG temporales, agente de proyecto sombrea al global en proceso nuevo); **`opencode reload` NO se afirma** (sin sub-comando en 1.18.32; `serve` con 401 sin token) |
| PD-16 | documental | review.md de 005-001: barrido de glitches sin resultados; PD-27→PD-20 corregido; veredicto changes-required, B1 bloqueante, B2..B7, tabla PD↔test, INV y 3 abstenciones preservados sin re-evaluar |
| PD-17 | documental | `grep -rn -E "/home/|/Users/|ofap|cdad-adopted-[0-9a-f]" docs/epics/epic-005-real-operation/` → rc=1; originales preservados en `.cdad/local/handoff-opencode{,-2}.original.md` (git-ignorado); `~/.claude`/`~/.agents`/`~/.config/opencode` permanecen por criterio D7 |
| PD-18 | `test_t4_pd18_walkthrough` | end-to-end con el CLI INSTALADO en raíz aislada (nunca HOME): prepare → replace con validación completa T1 (insumo conservado inexistente rc=2 campo/motivo/opción, sin efectos; corrección explícita rc=0) → `record-dispatch` rc=0, paquete despachado; sin rodeos manuales |

Anti-mocks ✓ (todo subprocess contra el CLI real; instalación real vía `cdad-generate.py` + `install.sh` con `CDAD_INSTALL_ROOT` en tempdirs; HOME de cada subproceso aislado, con guard estructural INV-8 que rechaza cualquier corrida cuyo HOME sea el real). RED legítima registrada en el ledger; el T4 RED destapó el defecto de declaración de versión (PD-14) que se cerró en T4 GREEN (`9e5215f`), y el RED-FIX del oráculo (_is_versionish) fue de test, no de producto. INV-1..INV-5, INV-8 revisados contra el código: sin cambios de comportamiento en `prepare` normal (único call-site de `_validate_corrections` es el reemplazo, :2022).

## Separación (pedido del encargo §4)

- **(a) Principio de CDAD**: una sola política de evidencia con dueño canónico y consumidores que remiten sin copiar (INV-6); pisos del rol intactos (INV-5); el encargo activo debe dejar de ser válido para que exista una corrección — el reemplazo valida el encargo resultante completo (PD-1, heredero de PD-22); cambio de instalación nunca silencioso (INV-7); tests de integración aislados del entorno del dueño (INV-8).
- **(b) Decisión del proyecto**: confinar la validación completa del encargo al sub-modo `--replace-packet` y conservar el camino normal intacto (D1/PD-5 — exactamente lo que pedía el dueño); orden de origen variable > registro de activación > global (D4); versión declarada por el instalador (`version.txt` + `source_version` en el manifiesto de derivados, D5); cierre como test de integración en raíz aislada, sin desplegar en HOME (D8); enmienda documental fechada de PD-17 de 005-001 con re-registro del pin (PD-11). La metodología define la evidencia; los comandos concretos quedan del proyecto (punto 4 del PD-8).
- **(c) Particularidad del entorno**: (i) el guard del test-writer deniega `instruction_sources` que viven bajo `packets/` (path_policy las clasifica como implementation_roots; los paquetes ejecutaron con el cuerpo de PACKET.md por declaración del orquestador — hecho, no desvío del rol); (ii) la instalación v8 vigente no declara `source_version` por ser anterior al marcador (despliegue reservado al dueño, O5); (iii) `opencode reload` no comprobable en el entorno del dueño (2.0.22, GUI, servidor permanente) ni en este sandbox (1.18.32 sin sub-comando, serve con 401) — el adaptador lo declara NO verificado, honesto; (iv) sin CI: `make validate` mantiene los 2 FAIL F011 previos (R6), misma causa, no atribuibles a este diff.

## Evidencia (comandos exactos y salidas)

```
sha256sum docs/specs/005-005-adoption-coherence/spec.md
  → 9349b0c1468de48b4223798e4209a1f16959ff5f0869a39c101ca039f7fe4d22 (== pin del state)

git log --oneline f148304..HEAD | head -30   → 27 commits
git diff --stat f148304..HEAD | tail -30     → 30 archivos, +3774/−107

grep -rn -iE "once per GREEN|full suite per GREEN|required full regression suite" \
     skills/cdad-cycle/references/ skills/cdad-cycle/packets/ skills/cdad-cycle/SKILL.md
  → rc=1 (cero resultados)                                            [PD-9]
grep -rn -E "/home/|/Users/|ofap|cdad-adopted-[0-9a-f]" docs/epics/epic-005-real-operation/
  → rc=1 (cero resultados)                                            [PD-17]
grep -c "## Test evidence policy" skills/cdad-cycle/references/stage-3-tdd.md → 1      [PD-8]
grep -rln "Test evidence policy" .../references + .../packets + SKILL.md → 13 archivos  [PD-9]
sha256sum docs/specs/005-001-idle-and-v7-bootstrap/spec.md
  → 8ba37ce2cce72607c4182c432e380019cc07cc5f69c48b2491cdfc481ca91170
     == contract_sha256 re-registrado en stage_history                  [PD-11]

cd tests && python3 -m unittest test_005_005_t2_docs_policy test_005_005_t3_provenance -v
  → OK (3 tests: pd12, pd13, pd14)
cd tests && python3 -m unittest test_005_005_t1_replace_conserved test_005_005_t2_docs_policy test_005_005_t4_integration
  → OK (11 tests, 13.171s)
cd tests && python3 -m unittest test_005_001_tcorr test_005_001_t2_replace_packet \
     test_004_002_t7_l1_derived test_003_006_t2_activation test_role_packet_render test_packet_prepare
  → OK (62 tests, 89.758s)   [regresiones del plan T1/T3]

SUITE COMPLETA canónica (runner del repo según tests/conftest.py):
python3 -m pytest tests/ -q   →  649 passed, 0 fallos, 16:41  [criterio «suite completa verde» ✓]
  nota: con `python3 -m unittest discover` el MISMO suite da 584 tests / 6 errors —
  todos ModuleNotFoundError: No module named 'tests' (artefacto del runner; los módulos
  del suite se importan mutuamente vía `from tests.<module> import ...`, que solo resuelve
  bajo pytest/conftest). No es defecto del diff ni del producto.

make validate
  → Assert PASS: 141 · Assert FAIL: 2 (F011 scripts/validate-subagents.sh;
    F011 tests/validate-odoo-specialization.sh) — exactamente los 2 preexistentes (R6)
```

## Abstenciones

1. **No reproduje localmente el caso MIX-V6V7 real de producción** (instalaciones sin marcador pre-T4): se verificó con el análogo sintético del test T3 (brazo b) y el walk-through aislado del T4; el estado real queda compilado al despliegue del dueño (O5).
2. **No verifiqué `opencode reload` en la versión 2.0.22 del dueño** (no alcanzable desde este sandbox): el adaptador declara auditablemente lo verificado (1.18.32 en aislamiento) y lo NO verificado; el comportamiento del servidor del dueño queda sin evidencia y el documento no lo afirma.
3. **D7 — VERIFY del dueño abierto** (`~/.claude`, `~/.agents`, `~/.config/opencode` en `handoff-opencode.md:63` y `execution.md:21`): la spec §8 lo registra explícitamente como VERIFY (dueño); lo respeté — el criterio aprobado los conserva y el grep PD-17 no los señala como personas-instalación.
4. **O1 no ejecutado por caso** (registro activación corrupto): hallazgo por lectura de código con razonamiento de familia INV-7/PD-13; el cierre exigido es ejecutable (rc=2 o warning observable), no añadí el test yo misma (rol read-only).
5. **Las 6 errors de la corrida suplementaria unittest-discover**:174 clasificadas como artefacto del runner por identidad del error (6/6 `No module named 'tests'`) + la ausencia del problema bajo pytest (649/649); no re-ejecuté cada módulo ofendido aislado con stub de sys.path.
