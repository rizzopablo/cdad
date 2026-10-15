# Review stage 4 — 005-001-idle-and-v7-bootstrap (T1..T4 + T-CORR)

**Contrato revisado:** `docs/specs/005-001-idle-and-v7-bootstrap/spec.md` — sha256 `9b92b8f4c873a79b9660231a891e2e94de3eed882e12a008f7ecfff1e854c99c` **verificado contra los bytes reales** (coincide; entrada pineada vigente en `stage_history`, `contract_path` correcto; la entrada superada del 2026-10-08/hash `a793522a…` no otorga autoridad — comportamiento correcto).
**Diff:** `git diff c78a0e4..HEAD` (rama `codex/epic-005-real-operation`). Commits de producto `c885f02, 0e77e49, 11e1454, bfe8edb, 70df141 (+ fix 70df141)`; de tests `e49a1ce, 7941007, 66b880a, d7355b7, 3b5c5ec, bd65cd6, ec8bd48` — todos presentes en el log (verificado).

## Veredicto

La feature cumple el contrato en su totalidad observable: autorización por rol C1 (PD-1..PD-6, PD-18, INV-8), reemplazo con conservación y corrección C2 (PD-7..PD-11, PD-16, PD-19..PD-24, INV-3/INV-7), reposo legítimo (PD-13..PD-15), marcadores distinguibles (PD-12), prueba decisiva conforme al ajuste declarado. Verificación ejecutada por mí: **suite completa 629 passed** (0 fallos, en tres segmentos), focales 30 passed, `make validate` con **exactamente los 2 FAIL F011 preexistentes declarados en R4**, mismo motivo. La única falta de cierre es **bloqueante y de gran importancia documental**: la sección «Reemplazo» de `project-execution.md` declarada en el plan (T2 y T-CORR) nunca fue escrita: al margen del componente runtime/CLI, es el desvío documental más grueso.

## Bloqueantes

### B1 — Falta la sección «Reemplazo» (`--replace-packet`) en la referencia operativa
- **Ubicación:** `skills/cdad-cycle/references/project-execution.md` (el diff sólo tocó el fragmento de §2 Autoridad, +21/−4); declarada en `docs/specs/005-001-idle-and-v7-bootstrap/plan.md` :39 (T2 «Files: … references/project-execution.md (Modify: nueva sección "Reemplazo")») y :55 (T-CORR: «§«Reemplazo» — conservación y corrección»).
- **Problema:** Sub-modo verificado en `cdad_packet.py` (en particular el de producto), de acuerdo con la simulación ejecutada: `grep -n "Reemplazo|replace-packet" skills/cdad-cycle/references/project-execution.md` → rc=1 (cero menciones); `grep -rln "replace-packet" skills/cdad-cycle/ --include=*.md` → cero archivos (ningún artefacto lo menciona).
- **Consecuencia:** El comportamiento de la superficie del CLI no queda documentado; el operador/rol no puede descubrir `--replace-packet` y reusa el scaffolding por defecto, inválido para ese fin; la superficie queda con aplicación incompleta; NOTA ABIERTA: **esto NO descuenta ninguna postcondición de runtime (todas verificadas)**, pero es un artefacto declarado por el plan aprobado (dos tareas) y roto — inseparable del no cierre (re-registrar o contar la violación del plan).
- **Cierre verificable:** Antes del commit de cierre: agregar una sección «Reemplazo» en `project-execution.md` (nuevos: selector `--replace-packet` + `--reason`; detecta obsolescencia PD-8; opciones de corrección PD-20 exactas); centinela `-`; pisos obligatorios; diagnósticos `packet obsolete`/`approval pending`; `.superseded.json` con traza PD-24) → commit en `skills/` y grep de la comprobación. **Costo:** doc-only, bajo riesgo (no toca el comportamiento del bloque estático: aplica a `packets/`, no a `references/`).

## Opcionales / Considerar (no bloqueantes)

### B2 — La prueba decisiva ejecuta los pasos 4–5 con otro objeto (declaración en el ledger): el reemplazo del paquete del architect tras editar el plan del epic no se prueba
- **Ubicación:** `tests/test_005_001_t4_decisive.py` S5 (comentario «Elección del paquete (declarada)», :644-651 aprox.); PD-17 de la spec.
- **Problema:** PD-17 letra: se edita el **plan del epic** y se reemplaza el **paquete del architect**. El test edita la **spec** y reemplaza el paquete **P1 (test-writer)**; el paquete del architect quedó `completed` en S2. El ajuste está declarado al orquestador en el propio ledger (fila 13, «escenario PD-17 ajustado…») y verificado, pero no está enmendado en spec/plan.
- **Consecuencia:** La semántica específicamente architect (reemplazo con contrato `approved-epic-plan` **sin pin de hash**, D2: la deriva del plan invalida el paquete pero NO exige re-registro de aprobación) no tiene test focal; comparte no obstante el mismo code path (`_contract_for` + `_contract_approval_for` architect), riesgo de comportamiento bajo.
- **Sugerencia:** Registrar la sustitución como enmienda menor (comentario en spec §PD-17 o adaptar el test con un bloque adicional S5-arch: `--resume-packet` del architect → `packet obsolete` + reemplazo con sha nuevo del plan). No extiende criterios del epic.
- **Verdict:** OPTIONAL · **Bucket:** m

### B3 — La raíz v7 adoptada (y HOME) quedó fuera de sync para `cdad_packet.py` tras el commit T-CORR
- **Ubicación:** versión operativa: `sha256(repo)=2809c094…` ≠ `sha256($HOME/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py)=c75ccc64…` ≠ los del `$HOME/.cache/cdad-adopted-ce09ed0/…` (1115 líneas de diff con el repo; `replace-packet` ausente: 0 ocurrencias).
- **Problema:** La verificación "byte a byte iguales, una sola versión del CLI, sin MIX-V6V7" declarada en el encabezado del `dispatch-ledger.md` ya **no vale** para `cdad_packet.py` (sí para `cdad_continuity/cdad_result/cdad_guard`). Es la misma clase de hallazgo MIX-V6V7 ya registrado en el propio ledger (corregido para agentes, no para scripts tras T-CORR). La activación está **reservada al dueño** (spec §5, R3): no es defecto de producto de la feature, y el gate de paridad (R3/test_p5) se verifica en un instalador temporal (tempdir), no en la raíz viva.
- **Riesgo real:** el próximo `prepare` despachado por sesión v7 usaría un CLI **sin** la corrección C1 (pin de submit re-registrado) y **sin** `--replace-packet`, re-introduciendo la circularidad I2 corregida — escenario emparejado con el punto (e) del plan.
- **Cierre verificable:** En stage 5/cierre, registro explícito en el ledger con los dos shas y orden de re-sincronización al dueño (o re-verificación `sha256` después de que re-instale). **Verdict:** OPTIONAL · **Bucket:** m

### B4 — Contrato con la ruta pin registrada pero archivo DELETED → diagnóstico genérico, no `approval pending`
- **Ubicación:** `cdad_packet.py:1436-1440` (`_reject_absent_contract_without_approval` cae al «ordinary read diagnostic»), :1950-1952 (replace), PD-11.
- **Problema:** Si un pin registra el `contract_path` correcto pero la spec fue borrada, replace/prepare emiten "cannot read contract …" (rc=2, sin efectos; invariantes intactos). Es un caso límite no ejercitado y el mensaje no nombra la corrección (`re-register`). El helper T4 se definió sin cubrir el caso «entry nombrando path → fall-through».
- **Cierre verificable:** Extender el guard: entrada sin archivo (sha no verificable) → `approval pending` nombrando el pin registrado. **Verdict:** OPTIONAL · **Bucket:** l

### B5 — Cobertura parcial del argv mezclado de PD-23 (7/15 flags enumerados)
- **Ubicación:** `tests/test_005_001_tcorr.py` `FORBIDDEN_FLAGS` (:833-841): no prueba `--contract-path`, `--plan-version`, `--reconcile-policy`/`--decision-ref`, `--record-dispatch`/`--attempt-id`, `--propose-policy`.
- **Problema:** El mecanismo `_reject_mode_mix` es un único punto común (funcional para los 15: verificado por lectura), pero su test solo estresó 7; detectaría idiosincrasias por flag futuras. **Verdict:** OPTIONAL · **Bucket:** l

### B6 — Oráculo débil del motivo de política (PD-22, write-scope)
- **Ubicación:** `tests/test_005_001_tcorr.py:796-800` (regex `politic|policy|no admite|not permitido|invalid`).
- **Problema:** El wrapper `_validate_corrections` siempre escribe "--write-scope is invalid: …", por lo que el regex queda satisfecho **por el texto propio del wrapper aunque el motivo subyacente desapareciera**. Corrección barata: asertar un token del motivo real (p. ej. `not allowed|not permitted|cannot use`).
- **Verdict:** OPTIONAL · **Bucket:** l

### B7 — Mensajes de test heredados de la época RED
- **Ubicación:** `tests/test_005_001_tcorr.py:376/857` ("hoy el sub-modo rechaza las correcciones"), `tests/test_005_001_t4_decisive.py:560-566` ("hoy emite el error genérico… (defecto reportado)") — hoy verdes por el fix.
- **Problema:** Mensajes de fallo que relatan un defecto ya corregido confunden futuras depuraciones. Archivo de issues de sustentación del histórico. **Verdict:** OPTIONAL · **Bucket:** l

### Considerado y descartado
- **T3 «state-detection.md» sin modificar:** desviación **declarada** en el ledger fila 9 y correcta: :27-30 ya documentaba la invariante activa ⟺ idle (verificado por lectura).
- **`_validate_idle_coherence` no valida `state.version`/epic_features del reposo:** tolerancias congruentes con PD-13; FYI sin acción.
- T-CORR afectó `test_role_packets.py`/`test_004_002_*`: migraciones additivas del pin D3 (diff leído: no debilita aserciones).
- Suite completa serial ≈10,5 min (más allá de 10 min por segmento encogido en 3): FYI performance, sin impacto en contrato (no hay CI).

## Auditoría test ↔ postcondición (AP-13/AP-14)

| PD | Test | Camino verificado |
|---|---|---|
| PD-1/PD-2/PD-5/PD-6 | `t1` TestPd1/Pd2/Pd5/Pd6 | CLI subprocess en tempdir sintético (caja negra, 0 mocks de producto); migraciones D3 additivas |
| PD-3/PD-4/PD-12(ap) | `t1` TestPd3/Pd4/Pd12 | marcador + tokens + sin efectos (árbol+state byte-a-byte) |
| PD-7/8/9/10/11/16/12(ob) | `t2` exactamente 1 clase por PD | `.superseded.json` base, INV-2/3/5 asserts, dispatched→reconciliación |
| PD-13/14/15/12(si) | `t3` (4 variantes de reposo + 4 incoherencias) | `VALID: idle` rc=0 y marcadores sin mezcla |
| PD-18/19/20/21/22/23/24 | `tcorr` | centinela `-`/ambigüedad, pisos, trazas de dif, argv mezclado (7/15), diagnóstico campo/motivo/opción |
| PD-17 | `t4` S1–S6 secuencial | e2e con `record-dispatch`+`receive`+`validate-receipt` reales; ver B2 |

Anti-mocks ✓ (todo subprocess/ramdisk, sin stub del producto). Constatación de RED legítima: 3 ciclos RED→GREEN interrumpidos por defectos del TEST (no del producto) con derivación al test-writer y re-RED verificado (`git stash`) — higiene verificada en el ledger (filas 6/9/14).

## INV-1..INV-8

INV-1 ✓ (gates de validación antes de `_publish_generation`; replace valida sucesor en :2034) · INV-2 ✓ (tests PD-7/T4 comparan stage/epic_history pre/post; CLI no escribe aprobaciones) · INV-3 ✓ (byte-compare del anterior + snapshot-diff) · INV-4 ✓ · INV-5 ✓ (stdout==PACKET.md determinista) · INV-6 ✓ (PD-6 + gates de pin) · INV-7 ✓ (PD-19..21) · INV-8 ✓ (PD-18 con control positivo).

## Abstentions

1. **No corroboré el test de la revisión completa de `docs/.cdad-state.json` (177 líneas de diff de registro) ni de los handoffs del epic:** son registros narrativos del orquestador fuera del producto auditable; verifiqué por muestreo el pin de especificación y el `active_packet` vigente. Cualquier aserción narrativa del ledger que no cité queda sin verificación.
2. **No verifiqué los 2 FAIL F011 como idénticos en estado c78a0e4 con pruebas de ejecución de época:** la identidad de ambos motivos con lo declarado en R4 (y evidencias de las filas 4/7 del ledger) habilita la inferencia de preexistencia; el comprobador A3 nombra además archivos de 004-003 y `__pycache__` no tocados por este diff — reviso el FAIL "every" de F011-2 como PREEXISTENTE por composición del conjunto, no como afirmación histórica ejecutada.
3. **No ejecuté la regresión de focales fuera de los tres segmentos** (la suite total se dividió en 3 por >10 min serial de caché bajo limitación time-out); los tres segmentos completan el catálogo de `tests/test_*.py` (84 archivos), con pass total 629.

## Evidencia (comandos y salidas)

- `sha256sum docs/specs/005-001-…/spec.md` → `9b92b8f4c873a79b9660231a891e2e94de3eed882e12a008f7ecfff1e854c99c` ✓ (= contrato del paquete).
- `python3 -m pytest tests/test_005_001_t{1,t2,t3idle,tcorr,t4}_*.py -q` → **30 passed** (28.39s).
- Suite completa por segmentos (`pytest tests/ -q -p no:randomly`): part_aa **186 passed/158s**, part_ab **269 passed/226s**, part_ac **174 passed/354s** → **629 passed, 0 failed**.
- `make validate` → **Assert PASS: 141 · Assert FAIL: 2 (rc=2)**, ambos F011: `scripts/validate-subagents.sh` (install.sh --check: drift de $HOME vs repo) y `tests/validate-odoo-specialization.sh` (A3) — los 2 preexistentes declarados en R4; los archivos citados por A3 (docs/specs/004-003/*, `__pycache__`) no fueron tocados por este diff.
- Manifiesto v7: `.opencode/agents/.cdad-derived.json` `source_dir` = raíz v7 `cdad-adopted-ce09ed0`; 11/11 derivados OK ("manifest OK") — ver contra B3 para scripts.
- `sha256sum` comparativo del CLI repo vs instalado → divergencia de `cdad_packet.py` (evidencia B3).
- Lectura completa: spec (188 l.), plan (146 l.), `cdad_packet.py` secciones `_contract_approval_for`(:1342), `_reject_absent_contract_without_approval`(:1418), `_validate_idle_coherence`(:476), `validate_request`(:723), `_replace_packet`(:1888), `_sentinel_list/_with_role_floor/_validate_corrections`(:1815-1886), `_resume_packet`(:1735), parser/_reject_mode_mix/main(:3315-3590); los 5 archivos de tests de la feature (7,359 l. del derivado + focos); diffs de refs y migraciones de tests.

---

**Resumen ejecutivo:** 1 bloqueante (B1, declarado por el plan, cierre barato y guiado: escribir la sección «Reemplazo» como lo especifica el código ya validado). 6 opcionales catalogados (B2..B7) — de ellos B3 es el que merece decisión del dueño antes de la siguiente feature: la raíz v7 viva ya no corre el CLI de esta feature. No recomendaría fusionar sin cerrar B1 y registrar B3; el resto no extiende el ciclo.
