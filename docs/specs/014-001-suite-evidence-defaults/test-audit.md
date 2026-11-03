# test-audit.md — 014-001-suite-evidence-defaults (AUDIT, TEXTO FINAL)

**Feature:** 014-001-suite-evidence-defaults · **Subfase:** AUDIT (test-writer, sesión `<ses-338>`)
**Contrato:** `docs/specs/014-001-suite-evidence-defaults/spec.md` (sha256 `6403397f4d57abee961d59c69a4d8d7403f7a306b2fdbc2e4785622208b0c2f0` verificado) · **Packet:** `014-001-suite-evidence-defaults-test-writer-audit-001` (route C)
**Método:** lectura de spec aprobada + los dos rangos ordenados + barridos focales en `tests/` (`autorización expresa|suite completa`, `una vez por GREEN|gate de cierre|closure gate|al cierre de la feature|SOLO con autoriz`). Sin lectura de implementación. Sin edición de tests.

**Regla de selección (R2):** un verificador por promesa observable del usuario (A–D), no por PC ni por archivo.

**Vocabulario de disposiciones:** Mantener · Extender · Sustituir · Consolidar · Añadir · Retirar. `Sustituir/Consolidar` se materializan en archivos nuevos de POST-AUDIT (verde + sensibilidad); `Añadir` son archivos nuevos de RED. Ninguna disposición reescribe contratos cerrados (INV-2).

## 1. Verificadores existentes que codifican la política sustituida

| # | Verificador existente | Disposición | Promesa / PC | Motivo | Operación |
|---|---|---|---|---|---|
| 1 | `tests/test_005_003_t6_packet_contract.py:648-755` (`test_pd10_instruction_declares_full_suite_policy`) + docstring `:79-84` | **Sustituir** (POST-AUDIT) | A/C · PC-3, PC-10 | Exige que la parte común declare "suite completa SOLO con autorización expresa"; falso bajo PC-3 para el cierre ordinario de epic. Conserva valor como detector de doctrina paralela. | Archivo nuevo POST-AUDIT: autorización-por-política + remisión al hogar + ausencia de doctrina paralela. |
| 2 | `tests/test_013_001_criterion_coherence.py:199-230` (`test_E_authorized_only_with_clean_install`) | **Sustituir** (POST-AUDIT) | A/D · PC-3, PC-13, PC-14 | Hogar "exige autorización expresa" y `docs/ci-gate.md` "condiciona el gate a autorización expresa". El tramo `test-clean` se conserva pero pertenece a PC-14. | Archivo nuevo POST-AUDIT: hogar + gate con interfaz real + instalación limpia como dimensión distinta. |
| 3 | `tests/test_004_003_t5_reentry_equivalence.py:367-391` (`TestG2Stage3GateGainsEquivalenceClause`) + docstring `:13-15` | **Sustituir** (POST-AUDIT) | B/C · PC-3, PC-5, PC-8 | Marco "una vez por GREEN" incompatible; la cláusula de equivalencia es rescatable. | Destino que conserve equivalencia y cambie frecuencia a defaults por momento. |
| 4 | `tests/test_005_005_t2_docs_policy.py:76-117` (PD-8(ii) "suite completa al cierre de la feature") | **Extender** (POST-AUDIT) | A/B · PC-2, PC-5 | Parcialmente vigente; falta feature vs epic y autorización por política. | Extender con los tres defaults. |
| 5 | `tests/test_005_005_t2_docs_policy.py:148-168` (veto "por GREEN") + `:184-198` (PD-10 "gate de cierre") | **Mantener** veto + **Extender** polo positivo | C · PC-4, PC-9 | Veto sigue válido; "gate de cierre" debe precisarse feature/epic. | Extender aserción positiva. |
| 6 | Fixtures `integration_gate = "suite completa una vez por GREEN"`: `test_004_003_t1_draft_contract.py:72,84`, `test_004_003_t3_plan_checks.py:90`, `test_004_003_t4_validation_fields.py:157,238`, `test_005_007_t2_progressive_plan_validator.py:154` | **Mantener** | — (INV-2) | Fixtures de contratos cerrados, no oráculos de esta política. | Ninguna. |
| 7 | `tests/test_006_003_u8_acceptance.py:45`, `tests/test_008_005_ci_gate.py:464-467` | **Mantener** | B · PC-5, PC-13 | Coherentes: cierre corre la completa por el gate existente. | Ninguna. |
| 8 | `test_003_007_t1…:111`, `test_003_007_t2…:116`, `test_003_007_t4…:48`, `tests/fixtures/003_003/background-suite-death.json:6` | **Mantener** | — | Prohíben completa como rutina de iteración; compatibles con PC-4. | Ninguna. |

Grep exhaustivo sobre `tests/`: 47 + 18 matches, todos clasificados arriba.

## 2. Mapeo promesa → verificadores propuestos para RED

- **Promesa A (PC-1–PC-4):** A1 hogar único con tres defaults y autorización por política (PC-2/3/4); A2 ADR de supersesión parcial (PC-1); A3 recomendación/obligación/dispensa distinguibles (PC-2/5).
- **Promesa B (PC-5–PC-8):** B1 omisión registrada con régimen correcto; B2 fallo/no atribuible impide verde; B3 skips/xfail visibles con efecto; B4 inestables sin reintentar hasta verde.
- **Promesa C (PC-9–PC-11):** C1 consumidores de §5 sin contradicciones (barrido negativo de órdenes incompatibles + referencia al hogar); C2 paquetes nuevos coherentes, históricos intactos; C3 `make agents` reproducible.
- **Promesa D (PC-12–PC-14):** D1 declaración por proyecto sin dispensa implícita; D2 gate con interfaz real; D3 Odoo instalación limpia ≠ amplitud.

En cada uno: parte mecánica (estructura/regex) vs parte semántica para el reviewer (spec §7). Destino propuesto: 3–4 archivos nuevos de RED; 2 archivos nuevos de POST-AUDIT para Sustituir #1–#3 + extensiones #4–#5.

deferred-hardening: backfill de trazabilidad, mutación/poda, enforcement automático de dispensa/skips, campañas de costo en otros proyectos (§8 de la spec).

## 3. Evidencia

Archivos modificados: ninguno. Commit: ninguno. Suite completa: no realizada (selección = lecturas y greps focales; no se corrió pytest). sha256 de spec verificado.

## 4. Decisión del orquestador (HITL delegada, 2026-11-02)

Aprobadas las disposiciones §1 (#1–#3 Sustituir a POST-AUDIT; #4–#5 Extender en POST-AUDIT; #6–#8 Mantener).

Ajuste al mapeo §2 (R2: un verificador por promesa observable, no por sub-ítem): **RED = 4 verificadores**, uno por
promesa A, B, C, D, cada uno con las aserciones mecánicas que hoy listan A1–A3, B1–B4, C1–C3, D1–D3. La parte
semántica de cada ítem queda para el reviewer (spec §7). Motivo: 13 tests de presencia de texto para un cambio
normativo inflan la suite con oráculos frágiles (lección 013-001/002: mutaciones semánticas sobreviven a tests de
texto); la cobertura de las 14 PC se mantiene por trazabilidad dentro de cada verificador.

Orden: RED (Añadir A–D) → GREEN (implementer; #1–#5 quedarán rojos al cambiar la norma, previsto) → POST-AUDIT
(Sustituir/Extender #1–#5, archivos nuevos, sensibilidad) → review.

¿Qué rompe para el usuario sin estos tests? (R4): A — cierra el epic esperando un permiso que la política ya da, o
itera con suites completas; B — etiqueta como verde una omisión, una corrida roja o una inestable reintentada;
C — un handoff/paquete le transmite la orden vieja; D — usa «suite lenta» como dispensa tácita o pierde `test-clean`.

## 5. Replanificación tras GREEN (orquestador, 2026-11-02)

La premisa de §4 («#1–#5 quedarán rojos al cambiar la norma») quedó refutada: tras GREEN (`bda98739..fbd8a675`)
los cinco pasan, porque sus oráculos admiten la redacción nueva (p. ej. `_AUTH_EXPRESS` acepta «autorización
suficiente», `tests/test_005_003_t6_packet_contract.py:653-656`). Disposición revisada: **#1–#5 Mantener**; no se
abre POST-AUDIT. La promesa nueva la protegen los 4 verificadores de 014-001. Deuda declarada: docstrings de #1–#3
describen el marco anterior («SOLO con autorización expresa», «una vez por GREEN»); son descripción histórica de
contratos cerrados (INV-2), no oráculo vigente. El reviewer lo contrasta.

Alta de inventario materializada: `tests/test_014_001_suite_evidence_defaults.py` → `orientation-planning`,
contrato 014-001; `cdad-suite.py validate` rc=0.
