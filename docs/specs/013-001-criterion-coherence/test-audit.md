# Test Audit Report — 013-001-criterion-coherence

**Feature**: 013-001-criterion-coherence (norma operativa: selección por contribución, mantenimiento acreditable, instrucciones coherentes, propiedades presupuestadas, evidencia proporcional autorizada)
**Spec version**: `docs/specs/013-001-criterion-coherence/spec.md` — sha256 `79b9c12b481efe1f240e09465c7687607c599c0aac8054c996950bf00e3bfd00` (validada: `validate-request rc=0`, `validate-packet rc=0`, `render --route C` idéntico al dispatch; contexto de ejecución v2 `schema_version: 2`)
**Test Writer**: test-writer (subfase AUDIT)
**Audit completed**: 2026-11-02

**Régimen**: AUDIT — no se modifica ningún test en esta subfase. No se ejecutó suite completa (política focal: el que cierra corre la suite una vez; este encargo ordena expresamente "Sin suite completa"). Comandos ejecutados: sólo lecturas (`sha256sum`, `grep`, `sed`, `validate-request`, `validate-packet`, `render --route C`) sobre `docs/specs/013-001-criterion-coherence/` y `tests/`. No se leyó implementación (`sources/`, `skills/`, `scripts/`, `agents/`, `build/` no fueron leídos como producto; sólo se cita la tabla de superficies de la spec como dato del contrato). Archivos modificados: ninguno. Commit: ninguno (el informe se entrega como FINAL TEXT; lo materializa el orquestador en `test-audit.md`).

## Behavior that changes (summary)

La spec (PC-1–PC-14, §3–§6) cambia la norma, no la interpreta como compatible con la anterior:

- **Promesa A (PC-1–PC-3)**: AUDIT distingue protección existente/faltante por referencias recuperables; cada incorporación declara su diferencia ("sin este test, el usuario…"); un test puede cubrir varias PCs y una promesa varios tests; postcondiciones/simetrías/cobertura no son cuotas (se conservan promociones R4).
- **Promesa B (PC-4–PC-7)**: vocabulario de **disposición única** (Mantener/Extender/Sustituir/Consolidar/Añadir/Retirar, §PC-4 tabla + mapeo a secciones de `test-audit.md`); sustitución/consolidación exige mapa de conservación PC-5; **POST-AUDIT admite sustitutos nuevos de comportamiento vigente** con verde + sensibilidad ante defecto contractual concreto (PC-6, sin RED, sin retirar originales hasta tener destino + evidencia); revisión independiente contrasta antes de aceptar (PC-7).
- **Promesa C (PC-8–PC-9)**: AUDIT/POST-AUDIT/RED/re-entry seleccionan por promesa; pre-RED no ordena leer implementación; se distingue sustituto vigente (PC-6) de test pendiente; `cdad-spec-and-test` se corrige sin retirarse; ninguna referencia concede permiso de lectura.
- **Promesa D (PC-10–PC-11)**: se sustituyen las cuotas rivales (100–1000, mínimo 100, valores Odoo 8–10) por **presupuesto finito y positivo declarado y justificado** + evidencia reproducible (invariante, declarado vs ejecutado, semilla, versión/config del generador, contraejemplo).
- **Promesa E (PC-12–PC-14)**: `stage-3-tdd.md` (Test evidence policy) es el único hogar canónico: evidencia focal + regresión proporcional; **suite completa sólo con autorización expresa** (también en cierre/integración/merge/transversal); se conserva instalación limpia de addon (`test-clean` o equivalente) como dimensión distinta; `packets/common.md` deja de ordenar cierre-con-suite-completa; `cdad-ci-gate.py` es herramienta de corrida completa sólo bajo autorización (mantiene `close --all` + verde atribuible cuando se autoriza; su omisión nunca es "verde"); sin autorización se registra "suite completa no realizada"; relaciones explícitas con ADR-020 (se sustituye exigencia automática), ADR-039 (se conserva recorrido para invocaciones autorizadas, sin obligatoriedad ni autorización automática) y Odoo.

## Test selection by promise (R2)

R2 es la única definición editable de selección (promesa observable; un test puede proteger varias PCs de su promesa; nada de cuotas por postcondición/simetría/cobertura). Lo registrado aquí es, por test, promesa + PCs + consecuencia.

| Test | Promise | Postconditions protected | Without this test, the user... |
|---|---|---|---|
| `tests/test_005_003_t6_packet_contract.py::test_pd10_instruction_declares_full_suite_policy` | E | PC-12, PC-13 | …no detecta que el bloque de instrucción siga ordenando "la corre quien cierra" como mandato incondicional, y un cierre futuro ejecuta (u omite silenciosamente) la suite completa sin autorización trazable |
| `tests/test_008_005_ci_gate.py::test_pc1_un_comando_orden_fijo_y_una_sola_corrida_de_pytest`, `test_pc3_rojo_nombra_fallos_y_skips_completos_sin_repetir_suite`, `test_pc4_cambio_solo_documentacion_no_ejecuta_superficie`, `test_pc4_cambio_de_producto_sin_superficie_es_rojo_y_nombra_ruta` (+ resto del archivo, 12 tests) | E | PC-12, PC-13 | …pierde el contrato funcional conservado del gate (recorrido completo, orden fijo, atribución fail-closed); una refactorización que rompa `close --all` o la atribución pasa verde y la herramienta autorizada deja de ser fiable |
| `tests/test_008_002_suite_evidence.py` (6 tests: `test_sequential_attempts_preserve_first_bytes`, `test_simultaneous_attempts_are_independent`, `test_attempt_records_selection_result_and_skip_reason`, `test_interrupted_attempt_is_never_success`, `test_measure_does_not_modify_tree` + guarda CLI) | E | PC-12 | …pierde evidencia focal/preservación de intentos; un cierre futuro confunde interrupción con éxito o sobrescribe evidencia anterior sin detección |
| `tests/test_008_002_suite_selection.py` (PC-1/PC-2/PC-3-estructural/PC-5/PC-7 de 008-002) | A, E | PC-1, PC-2, PC-3 | …pierde selección exacta/inventario/validación contra baseline; una poda futura elimina obligaciones acreditadas sin que `validate` lo rechace |
| `tests/test_005_012_t3_closure_dispatch_resolution.py`, `test_005_012_t4_late_delivery.py`, `test_005_012_t2_gate_authority.py` | E | PC-12, PC-13 | …un cierre sin despacho recepcionado, sin pin de spec vigente o sin autoridad pasa como éxito; el usuario fusiona/cierra sin la evidencia que el gate exige |
| `tests/test_006_003_u8_acceptance.py` | E | PC-12 (instalación limpia) | …una regresión que elimina la verificación de instalación desde cero pasa verde; el addon se publica sin probar instalación limpia (una corrida caliente la sustituye en silencio) |
| `tests/test_010_004_t5_properties.py::test_inv05_complete_equality_rejects_every_seeded_byte_divergence`, `test_inv04_failed_admission_rejects_every_seeded_family` (SEED=20261030, CASES_PER_PROPERTY=100) | D | PC-10, PC-11 | …pierde el patrón de propiedades sembradas reproducibles (semilla fija, invariante, familias, conteo ejecutado); un generador no reproducible o una muestra vacía pasa como "propiedad verde" |
| `tests/test_010_004_t4_red.py` (2 tests de superficies de despacho ruta C) | C | PC-8, PC-9 | …una edición que borra `--route C` de las superficies de despacho deja el despacho sin camino publicado con todos los gates verdes; el paquete ejecutado no es el publicado |
| `tests/test_004_003_t4_validation_fields.py`, `test_004_003_t3_plan_checks.py`, `test_005_007_t2_progressive_plan_validator.py` | A, C | PC-1, PC-8 | …planes sin bloque de validación/checks observables o sin referencia al hogar canónico pasan la planificación; el AUDIT posterior no tiene contra qué contrastar |
| `tests/test_004_003_t5_reentry_equivalence.py` | B, C | PC-5, PC-7, PC-8 | …una re-entrada que sustituye evidencia sin equivalencia acreditada pasa verde; se pierde conservación de obligaciones en reingresos |
| `tests/test_006_001_t1_selection.py`, `test_003_003_t3_budget.py` | A, D | PC-2, PC-10 | …selección/presupuesto sin justificación pasan; se reintroducen cuotas implícitas o selecciones sin diferencia declarada |
| *(inexistente)* `test_013_001_<promesa>_<disposiciones-y-sustitutos>` — ver "New tests to write" | B | PC-4, PC-5, PC-6, PC-7 | …las seis disposiciones, el mapa PC-5 y el recorrido POST-AUDIT-verde+sensibilidad de PC-6 quedan sin verificador focal; ver fila correspondiente |

Cada fila con consecuencia nombrada es requisito ordinario. Las filas marcadas `deferred-hardening` en Riesgos no generan test en el ciclo actual, por razón registrada.

## Modified tests

Ningún test se modifica en AUDIT (la subfase propone; POST-AUDIT/RED ejecutan lo aprobado). Disposición propuesta por test existente afectado (vocabulario PC-4; exactamente una por test):

### test_pd10_instruction_declares_full_suite_policy
- **Change**: Sustituir la aserción "la corre quien cierra" por "suite completa sólo con autorización expresa; sin autorización se registra no realizada" (remite al hogar canónico `stage-3-tdd.md` Test evidence policy)
- **Spec ref**: PC-12, PC-13; §5 fila `packets/common.md`
- **Promise**: E
- **Postconditions protected**: PC-12, PC-13
- **Without this test, the user**: cierra con (o sin) suite completa sin autorización trazable
- **New expectation**: el bloque común declara autorización expresa + registro de no-realizada; ningún asset de rol/subetapa afirma gate-de-cierre-completo
- **Why**: la norma anterior ("siempre la corre quien cierra") es exactamente lo que PC-13 ordena eliminar
- **Disposición propuesta**: **Sustituir** (origen: test actual; destino: test actualizado que conserva la obligación de declarar política + añade la de autorización)

### test_008_005_ci_gate.py (12 tests del gate como caja negra)
- **Change**: Conservar contrato funcional (`close --all`, orden, atribución fail-closed); alinear documentación/uso con "sólo bajo autorización expresa"; no convertir en gate focal; no añadir selector/CLI
- **Spec ref**: PC-13 (párrafos gate); §5 fila `scripts/cdad-ci-gate.py` + `docs/ci-gate.md`
- **Promise**: E
- **Postconditions protected**: PC-13
- **Without this test, the user**: usa una herramienta de corrida completa rota creyéndola atribuible
- **New expectation**: mismo recorrido + exigencia de verde atribuible cuando se invoca autorizado; su omisión nunca es "gate verde"
- **Why**: PC-13 conserva el contrato funcional y cambia sólo la condición de invocación
- **Disposición propuesta**: **Mantener** (contrato funcional) + **Extender** puntual donde el test fije texto de uso ("siempre/cierre/push" → "bajo autorización"); si el texto vive en `docs/ci-gate.md` y no en el CLI, el test no cambia

### test_008_002_suite_evidence.py + test_008_002_suite_selection.py
- **Change**: Ningún cambio de expectativa funcional; verificar compatibilidad con evidencia focal + autorización (no exigir suite completa por cerrar)
- **Spec ref**: PC-1, PC-3, PC-12; §6 (criterio 6)
- **Promise**: A + E
- **Postconditions protected**: PC-1, PC-3, PC-12
- **Without this test, the user**: pierde preservación de evidencia y selección exacta
- **Why**: son la base de "regresión proporcional" que PC-12 conserva
- **Disposición propuesta**: **Mantener**

### test_005_012_t3/t4/t2 (closure), test_006_003_u8 (instalación limpia)
- **Change**: Cierre: añadir "autorizada o no realizada" a la evidencia de suite completa; instalación limpia: conservar intacta y distinguirla de suite completa
- **Spec ref**: PC-12 (instalación limpia como dimensión distinta; bloqueo si el runner une ambas), PC-13, PC-14 (Odoo)
- **Promise**: E
- **Postconditions protected**: PC-12, PC-13, PC-14
- **Without this test, the user**: omite instalación limpia o infiere suite completa del nombre `test-clean`
- **Why**: PC-12 ordena conservar instalación limpia y prohibir la inferencia
- **Disposición propuesta**: **Extender** (cierre: caso "sin autorización → registra no realizada"); **Mantener** (instalación limpia)

### test_010_004_t5_properties.py (2 propiedades, SEED 100 casos)
- **Change**: Conservar invariantes/patrón reproducible; sustituir la lectura "100 = mínimo universal" por "presupuesto declarado y justificado por campaña; evidencia: declarado vs ejecutado + semilla + versión/config + contraejemplo"
- **Spec ref**: PC-10, PC-11; §2 punto 5 (cuotas incompatibles); §6 evidencia estructural
- **Promise**: D
- **Postconditions protected**: PC-10, PC-11
- **Without this test, the user**: acepta propiedades no reproducibles o confunde muestra con suficiencia contractual
- **New expectation**: cada campaña declara presupuesto antes de correr; cambiarlo exige justificación + comprobar no-eliminación de obligaciones
- **Why**: el valor 100 es dato de esa campaña, no cuota universal; PC-10 prohíbe mínimos/máximos universales
- **Disposición propuesta**: **Extender** (parametrizar presupuesto declarado + aserción declarado-vs-ejecutado); **Mantener** en todo lo demás. No se reduce muestra ni se toca el invariante.

### test_010_004_t4_red.py + test_004_003_t4/t3 + test_005_007_t2 + test_004_003_t5
- **Change**: Añadir al oráculo la distinción PC-6 (sustituto vigente → POST-AUDIT, no RED) y la prohibición de importar/inspeccionar implementación en pre-RED; conservar todo lo demás
- **Spec ref**: PC-6 (secuencia reconciliada), PC-8, PC-9
- **Promise**: B + C
- **Postconditions protected**: PC-5, PC-6, PC-8, PC-9
- **Without this test, the user**: envía sustitutos vigentes a RED (rojo artificial) o disfraza lecturas de implementación como "búsqueda"
- **Why**: las instrucciones actuales afirman universalmente "todo test nuevo pertenece a RED"; PC-6/PC-8 lo prohíben
- **Disposición propuesta**: **Extender**

## New tests to write

Cada uno protege una promesa con PCs y consecuencia; ninguno duplica un resultado observable equivalente:

- `test_013_001_A_audit_distinguishes_existing_and_missing` — promesa A; PC-1, PC-2, PC-3; sin este test, el usuario aprueba incorporaciones sin saber qué ya protege la suite y duplica verificadores equivalentes (o deja huecos creyéndolos cubiertos). Verifica: AUDIT con referencias recuperables, declaración de diferencia por incorporación, y ausencia de cuota numérica postcondición→test (incluidas promociones R4 justificadas que sí avanzan).
- `test_013_001_B_single_disposition_per_test` — promesa B; PC-4; sin este test, el usuario acumula tests sin disposición o con dos disposiciones y nadie sabe qué se puede retirar/sustituir. Verifica: exactamente una disposición de las seis por test auditado; mapeo a secciones de plantilla sin duplicar disposición por referencia; Mantener ante incertidumbre sin certificar suficiencia; Retirar sólo con referencia a obligación eliminada en spec aprobada.
- `test_013_001_B_substitution_conservation_map` — promesa B; PC-5; sin este test, el usuario acepta sustituciones por "mismo resultado/cobertura/menor duración" y pierde obligaciones vigentes. Verifica los cinco elementos del mapa (orígenes/destinos, obligaciones vigentes, estados/acciones/efectos diferenciales, ubicación por comprobación, evidencia+límites).
- `test_013_001_B_post_audit_substitute_green_plus_sensitivity` — promesa B; PC-6; sin este test, el usuario retira originales sin destino ejecutable o acepta "sensibilidad" falsa (import-error, fallo de setup, aserción falseada, control fuera del recorrido). Verifica: sustituto nuevo de comportamiento vigente en POST-AUDIT (no RED), verde + control negativo de defecto contractual concreto, mapa conservado, originales intactos hasta la evidencia, bloqueo declarado si no hay sensibilidad en alcance. Es el cambio de recorrido central de la feature.
- `test_013_001_B_independent_review_contrasts_before_accepting` — promesa B; PC-7; sin este test, el usuario acredita sustituciones sin contraste independiente y declara suites acreditadas a partir de un lote. Verifica: revisión de disposiciones + mapa + evidencia; veredicto Mantener posible; genealogía conservada.
- `test_013_001_C_no_quota_no_implementation_read` — promesa C; PC-8; sin este test, el usuario vuelve a exigir un test por postcondición o a ordenar inspección de implementación en pre-RED. Verifica ambas prohibiciones + distinción sustituto-vigente vs pendiente.
- `test_013_001_C_homes_and_auxiliary_skill` — promesa C; PC-9; sin este test, el usuario reedita doctrinas paralelas y `cdad-spec-and-test` vuelve a declarar duración-<30s universal / verde→merge como sustituto del ciclo. Verifica: R2/R4/R7 como hogares referenciados (no paralelos) y corrección mínima de la skill sin retirarla.
- `test_013_001_D_budget_declared_before_campaign` — promesa D; PC-10; sin este test, el usuario reintroduce cuotas universales rivales. Verifica: presupuesto finito/positivo declarado antes de cada campaña con justificación (invariante/dominio/coste); variantes contractuales obligatorias siempre verificadas (no sustituidas por muestreo).
- `test_013_001_D_reproducible_evidence` — promesa D; PC-11; sin este test, el usuario no puede reproducir ni calibrar una campaña. Verifica los cinco campos recuperables + regla de cambio de presupuesto.
- `test_013_001_E_canonical_home_and_authorized_only` — promesa E; PC-12; sin este test, el usuario dispersa la política en hogares paralelos o ejecuta `test-clean`+suite inseparables en silencio. Verifica: hogar único, autorización expresa incluso en cierre/integración/merge/transversal, comandos por proyecto, instalación limpia conservada como dimensión distinta, bloqueo declarado cuando el runner une ambas.
- `test_013_001_E_consumers_stop_defaulting_full_suite` — promesa E; PC-13; sin este test, `common.md`/consumidores/gates vuelven a exigir suite completa por defecto/cierre/push. Verifica remisión al hogar, gate sólo autorizado (conserva `close --all` + verde atribuible), sin workflow/trigger/opción nuevos, y registro "no realizada" (nunca "verde" sin evidencia).
- `test_013_001_E_posterior_decision_record` — promesa E; PC-14; sin este test, el usuario pierde la trazabilidad ADR-020 (sustituida) / ADR-039 (conservada para autorizadas, sin obligatoriedad ni autorización automática) / Odoo, o inventa vigencia de ADR-039. Verifica relaciones explícitas + antecedentes preservados + `systemPatterns.md` reconciliado por su responsable.

Nota de ubicación: son verificadores de norma documental (régimen documentary: oráculo desde contrato + entradas autorizadas, nunca desde el producto bajo verificación); viven bajo `tests/` como el resto de la suite de este repo, sin `TransactionCase`/`@tagged` (no es addon).

## Unchanged tests (untouched)

Quedan EXACTAMENTE intactos (disposición **Mantener**; citarlos desde una sustitución no les añade otra):

- `tests/test_008_005_ci_gate.py` en su contrato funcional (orden, una sola corrida pytest, atribución fail-closed, canario no decisorio, hermeticidad, exit-2 de uso) — la herramienta no cambia.
- `tests/test_008_002_suite_evidence.py` y `tests/test_008_002_suite_selection.py` en selección exacta, inventario y preservación de evidencia.
- `tests/test_010_004_t3_red.py` y oráculos de ruta C reutilizados por propiedades (verificación publicada de C).
- `tests/test_006_004_u7_seed_verification.py` (patrón de semilla) en lo que no fije cuota universal.
- Toda la suite ajena a las superficies del §5 (features 003/004/005/006/007/010 no enumeradas arriba): no la toca esta unidad; su alcance explícito (§5, invariante 8) no elimina tests del piloto ni acredita redundancias de toda la suite — eso pertenece a 013-002/013-003.

## Regression Risk Assessment

- ⚠️ Riesgo 1 (B, PC-6): sin los tests nuevos `*_post_audit_substitute_*` no hay verificador focal del recorrido sustituto-vigente; el riesgo se cubre con los tests propuestos, no con silencio.
- ⚠️ Riesgo 2 (E, PC-12/PC-13): `test_pd10_instruction_declares_full_suite_policy` y consumidores пошагово fijan la norma anterior; hasta su sustitución aprobada, la suite exige lo contrario de la spec. Bloqueo transitorio conocido y acotado (no se ejecuta suite completa para "comprobarlo").
- ⚠️ Riesgo 3 (D, PC-10): valores históricos 100/1000/8–10 dispersos en especializaciones Odoo (`odoo-test-writer`, `odoo-make-env/run-budget-protocol`) pueden leerse como cuotas tras el cambio genérico; la auditoría los señala para corrección en implementación, sin inventar inventario core/OCA (esta unidad no modifica addon, §6).
- ⚠️ Riesgo 4 (alcance): superficies fuera de `tests/` (§5: `sources/`, `references/`, `packets/`, `assets/`, `skills/`, `scripts/`, `docs/`, `agents/`, `build/`) no son tocadas por el test-writer; su cambio pertenece al implementer con regeneración (`make agents`) y validación canónica de paquetes. Ningún test del ciclo actual acredita esas ediciones; lo hará la revisión independiente (PC-7 + §6).
- `deferred-hardening` (con razón, sin test en este ciclo): acreditación semántica exhaustiva de la suite; poda/mutación del piloto (013-003); rendimiento/fixtures/paralelismo/selección dinámica; detector automático de equivalencias; retirada de `cdad-spec-and-test`; workflow/selector/permiso automático para el gate; prueba universal de obediencia de agentes — todos en §8 de la spec, ninguno difiere una PC.

## Test Audit Gate

- [ ] Cada test modificado tiene justificación en spec.md con referencia explícita (tabla anterior)
- [ ] Cada test nombra promesa + postcondiciones + consecuencia ("sin este test, el usuario...")
- [ ] Ningún test añadido duplica un resultado observable equivalente
- [ ] Ningún test modificado carece de justificación documentada
- [ ] Tests intactos listados explícitamente
- [ ] Riesgos evaluados; cada diferimiento va a `deferred-hardening` con su razón (§8 spec, sin diferir PCs)
- [ ] El usuario (humano o agente de jerarquía superior) aprueba este informe antes de POST-AUDIT/RED

---
*Evidencia del encargo: `validate-request rc=0`, `validate-packet rc=0`, `render --route C` idéntico al dispatch, `sha256(spec.md)=79b9c12b…e3bfd00`, contexto v2. Sin archivos modificados, sin suite completa, sin lecturas de implementación.*

## Resolución del delegado del dueño (2026-11-02)

Aprobado con dos correcciones obligatorias:
1. **Sin cuota encubierta.** Los 12 tests nuevos propuestos replican casi uno a uno las postcondiciones, justo lo que esta feature prohíbe. RED escribe a lo sumo un módulo con un test por promesa (A-E); dentro de cada uno, las comprobaciones son estructurales sobre artefactos reales. Lo semántico queda para la revisión independiente (spec §6).
2. **Disposición única.** Los «Mantener + Extender» del ci-gate y de closure se resuelven en POST-AUDIT test por test, con exactamente una disposición.

Las casillas del gate quedan aprobadas con esas condiciones.
