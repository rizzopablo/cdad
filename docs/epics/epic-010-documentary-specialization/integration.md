# Epic 010 — Integración

**Etapa E3.** Verificación de que las cinco features funcionan juntas, no sólo
cada una por separado. La auditoría se hizo con la directiva vigente del owner:
**primero se inventaría la cobertura existente y sólo lo no cubierto produce
tests nuevos.** Conclusión: no hubo tests nuevos.

## 1. Criterios del epic → cobertura

| # | Criterio (plan §Criterios de aceptación) | Estado | Evidencia decisiva |
|---|---|---|---|
| 1 | Las cinco features cierran individualmente con evidencia de sus contratos | **evidencia, no test** | los cinco `closure.md` (010-000, 010-004, 010-001, 010-002, 010-003) con sus revisiones y recibos; un test que compruebe que los archivos existen no acredita el cierre |
| 2 | 010-000: raíces relativas/absolutas, rechazo de escapes, revisión independiente y artefacto instalable; sin tocar la instalación global como sustituto | **parcial (test + evidencia)** | `test_010_000_continuity_relative_root.py::test_A_relative_root_begin_and_checkpoint_match_absolute` (`record`/`seq` relativos == absolutos), `::test_C_existing_controls_hold_under_relative_root` (paquete alterado rc≠0; `../fuera.txt`, `/etc/passwd` y symlink exterior rechazados; testigo exterior intacto), `::test_D_installed_consumer_reproduces_relative_equivalence` (`CDAD_INSTALL_ROOT` aislado, efecto instalado relativo == absoluto, traversal rehusado, árbol sin publicaciones). La revisión independiente es evidencia (`review.md`, `isolated-validation.md`) |
| 3 | El flujo canónico genera, instala y resuelve los perfiles documentales; restricciones por rol conservadas | **cubierto (test)** | `test_010_002_documentary_role_integration.py::TestDistribution` (staging publica los 11 agentes; promovido == staging byte a byte; skills instaladas == fuente; agente resuelto presente en ambos runtimes; `write_scope` documental); `test_010_002_documentary_role_properties.py::TestFinalIsolatedDistribution` (CLI y esquema instalados == fuente; agente esperado por rol/stack; `validate-request` rc=0; paquete `dispatched`; rol de lectura con `write_scope` vacío) |
| 4 | Agentes genéricos y Odoo conservan su comportamiento; combinación documental/Odoo según 010-002 | **cubierto (test + regresión)** | `::test_ordinary_publication_publishes_derived_agent_and_context` (`null`/vacío/ausente → `cdad-test-writer`; `odoo` → `cdad-test-writer-odoo`); propiedad de derivación sobre 100 combinaciones; `TestEngagement::test_six_role_boundaries_and_no_documentary_variant` (exactamente 11 agentes por runtime); `::test_documentary_odoo_journey_keeps_domain_and_write_frontier` (agente Odoo resuelto, frontera de escritura `docs`, instalado == staging); `test_packet_prepare.py::test_p6_claude_barriers_are_unchanged` (guardas de Claude idénticas) |
| 5 | El piloto identifica un defecto estructural mediante un control automático | **cubierto (test)** | `test_010_003_documentary_pilot.py::test_broken_locator_is_rejected_with_document_reference_and_cause` (veredicto negativo, `cause == missing_fragment`, documento y referencia) y `::test_the_product_cites_only_inventoried_fragments_and_at_least_one` |
| 6 | La revisión independiente identifica afirmación sin respaldo, contradicción omitida y referencia incorrecta, con ubicación y evidencia | **parcial (evidencia + fracción test)** | evidencia: `challenge-review.md` (F-1/F-2/F-3 del ensayo), `challenge-contrast.md` (3/3, cero omisiones), `semantic-evidence.md` §2; la fracción testable —que un script no decida verdad semántica— la fija `::test_semantically_defective_candidate_is_structurally_accepted` |
| 7 | El entregable corregido conserva trazabilidad; límites y pendientes visibles; aceptación funcional del usuario | **parcial (test + evidencia)** | trazabilidad: `::test_the_product_cites_only_inventoried_fragments_and_at_least_one` y `::test_inventory_accounts_for_every_source_with_matching_digest_and_declares_synthetic_origin`; límites, pendientes y aceptación: `functional-acceptance.md` y `closure.md` §3-§4 |
| 8 | No se modifican verificadores ni insumos protegidos desde GREEN; cambios vuelven al rol competente y, si alteran contrato, a aprobación | **evidencia de proceso** | `review.md`/`review-002.md`, `deviation-green-accreditation-2026-10-31.md` (I-10 declarado y restituido); el test de inventario detecta deriva **actual** de las fuentes (digest == registrado), no la historia del diff |
| 9 | Validación y regresión pasan; sin datos privados ni modelos concretos en el producto instalable; sin push ni publicación | **parcial (test + evidencia)** | modelos: `test_006_002_u2_neutral_skill.py::test_pd1_no_concrete_model_in_delegation_context` (todo `.md` de las skills, `offenders == []`), `test_cdad_generate.py::test_pd_1e_generated_agents_carry_no_model_line` (11 agentes × 2 runtimes) y `::test_pd_7a_generated_orchestrators_name_no_model`; datos privados: `test_010_001_documentary_contracts.py::TestPromiseC::test_the_norm_requires_contrast_with_sources_and_owner_acceptance` (nombre del aprobador ausente en `skills/`, `sources/`, `agents/`, con controles de vacuidad); bytes instalados: `TestPromiseD::test_isolated_install_distributes_the_reference_with_source_bytes`; la suite completa y la ausencia de push son evidencia de los cierres |

## 2. Medición

Selección decisiva (no la suite completa), sobre el estado de cierre:

```
python3 -m pytest -q <26 nodos decisivos de 010-000, 010-001, 010-002,
                        010-003, 006-002 y test_cdad_generate>
..........................                                               [100%]
26 passed in 140.91s (0:02:20)
rc=0
```

La suite completa ya estaba verde sobre la versión del cierre de 010-003
(`c229a671`: **1926 passed, 5 skipped, rc=0**, canario delta 0). Desde ese commit
sólo cambiaron documentos y el estado: ningún archivo de `tests/`, `skills/`,
`scripts/` ni `src/` se modificó después. La verificación de esa afirmación está
en el commit de cierre del epic.

## 3. Hallazgos de la integración

1. **No faltaba ningún test de integración.** El flujo completo —generar,
   instalar en un HOME aislado, resolver el agente por rol y stack, conservar la
   frontera de escritura y los límites de rol— ya estaba ejercitado de punta a
   punta por `TestDistribution` y `TestFinalIsolatedDistribution` de 010-002, más
   las regresiones de 010-000 y los controles de 010-003. Añadir un E2E nuevo
   habría duplicado esos oráculos y creado una segunda definición de la misma
   promesa.
2. **Seis de los nueve criterios no son materia de test.** Cierres individuales,
   revisión semántica independiente, aceptación funcional, no modificación de
   verificadores desde GREEN y ausencia de push son **evidencia de sesiones y de
   proceso**. Un test de repositorio sólo podría comprobar que un archivo existe,
   que es tautológico. Se declaran como evidencia con su ubicación.
3. **La cobertura actual es de contrato, no de cobertura.** La auditoría se hizo
   con la directiva del owner del 2026-10-31: mapa de cobertura existente primero
   y tests nuevos sólo para lo no cubierto. Confirmó que la suite no necesita
   crecer para esta integración.
4. **Límite conocido y no resuelto acá:** la instalación global está por detrás de
   la publicación de 010-004 (`install.sh --check` rc=1 en el HOME real). La
   verificación de instalación se hizo sobre HOMEs aislados, que es lo que el
   contrato promete; publicar es decisión del dueño y no se hizo.

## 4. Deuda que la integración deja declarada

- **I-8, I-9, I-10, I-11, I-12, I-13, I-14, I-15** y el canario de agentes:
  registrados en `backlog.md`, cada uno con su condición de cierre.
- **Deriva de la instalación global** (`010-001/closure.md` §5): mientras no se
  publique, los roles reciben la obligación documental por el paquete y la
  toolchain del repositorio, no por el agente instalado.
- **La suite y el tiempo de cierre:** 1764 funciones / 1918 casos y ~1 h de
  suite. La directiva del owner del 2026-10-31 ataca la causa en el AUDIT; la
  reducción de tests existentes exige su propia unidad con mapa test→promesa.
- **Selección de tests por cobertura existente:** formalizar la directiva en las
  fuentes del skill (siete hogares y agentes generados) es la unidad siguiente.

## 5. Veredicto

**La integración del epic se acredita con la suite existente y la evidencia de
proceso.** No se agregó ningún test porque no faltaba cobertura testable; no se
modificó ningún test existente. El gate E3 queda cumplido en lo que puede
cumplirse sin push (la CI de `main` no se ejecuta sin publicar).
