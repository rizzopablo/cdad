# Closure — 013-001-criterion-coherence

**Epic:** `epic-013-test-criterion` — orden 1/4. **Cerrada:** 2026-11-02.
**Contrato:** `docs/specs/013-001-criterion-coherence/spec.md`, sha256
`79b9c12b481efe1f240e09465c7687607c599c0aac8054c996950bf00e3bfd00`, aprobado por Pablo
(HITL delegada, `docs/epics/epic-013-test-criterion/execution.md`) el 2026-11-02.
**Estado:** cerrada en el repositorio; **no publicada ni desplegada**.

## 1. Resultado

El criterio de selección y mantenimiento de tests es uno solo y aplicable por las dos vías
(legacy y paquetes): protección existente antes de añadir, contribución declarada, sustitución
ordinaria acreditable, presupuesto de propiedades declarado y suite completa sólo con
autorización expresa. Producto: `ef56a39d..4adc1e46` (48 archivos, +952/−244), RED `96ad443f`,
sustituto de POST-AUDIT `e19983fc`, ADR-041 `b7125a47`.

## 2. Evidencia

- Focal: `pytest tests/test_013_001_criterion_coherence.py
  tests/test_004_003_t5_reentry_equivalence.py tests/test_005_003_t6_packet_contract.py
  tests/test_cdad_generate.py -q` → **30 passed in 7.01s**.
- **Suite completa no realizada** (directiva del dueño); no se declara verde ni gate de CI verde.
- Regeneración: `make agents` sin deriva (14 agentes, 7 por runtime).
- Revisión independiente: `review.md` — 6 bloqueantes (B1–B6) y 3 (R1–R3) cerrados; **no hubo
  tercera revisión independiente**: verificación del orquestador sobre los criterios de cierre
  exactos del reviewer, declarada.

## 3. `deferred-hardening` de la spec §8 — conservado con su disposición

| Ítem de §8 | Disposición registrada |
|---|---|
| Acreditación semántica exhaustiva de la suite | **Fuera del compromiso** de esta unidad; la carga se reparte con la revisión semántica independiente (no se acredita por test). |
| Poda y mutación del piloto | **013-003-redundancy-pilot.** La sensibilidad exigida a un sustituto (PC-6) no impone herramienta ni campaña universal de mutación. |
| Rendimiento, fixtures, paralelismo y selección dinámica | **013-004-suite-performance**, que **sólo se abre por decisión del dueño**; requieren medición previa. |
| Detector automático de equivalencias | **No necesario**, declarado: no acredita conservación semántica. Sin unidad destino. |
| Retirada de `cdad-spec-and-test` | **Aplazada expresamente por el dueño** (decisión del 2026-11-02, posterior al alcance del epic). Se corrigió lo contradictorio; la skill sigue disponible y cargable. |
| Nuevo workflow, selector o permiso automático para el gate | **No necesario** para distinguir herramienta disponible de ejecución autorizada. Sin unidad destino. |
| Prueba universal de obediencia de agentes | **No prometida**: se verifica norma distribuida y revisión independiente. Sin unidad destino. |

Ninguna exclusión aplace una postcondición de la spec.

## 4. Deuda declarada (fuera de §8)

- **O1** — los 5 tests de promesa y el sustituto no detectan regresión **semántica** en
  superficies Odoo (sobrevivieron «ALWAYS runs at closure» junto al token de autorización y
  `8-10` en `odoo-test-writer`). Destino: deuda declarada, cubierta por diseño por la revisión
  semántica.
- **O2** — ADR-020 y ADR-039 no enlazan a ADR-041; hoy sólo el índice de `systemPatterns.md`.
- **O4** — «suite green» sin precisar en `stage-4-review.md:180,188`, `cdad-cycle/SKILL.md:73,541`,
  `sub-agent-strategies.md:36,138`.
- **O5** — «every postcondition has at least one test» (`SKILL.md:315,356`) y POST-AUDIT ausente
  del diagrama de `SKILL.md:303`.
- **O6** — justificación en la spec de cada test modificado conviviendo con el mapa PC-5.
- **O7** — «Whole suite green» en `state-detection.md:69,71` (enruta estado, no es gate).
- **Tests `007_00*`** sin agotar en la regresión del POST-AUDIT 2.
- **Suite completa no realizada.**
- **Despliegue pendiente (reserva del dueño):** el árbol instalado en ambos runtimes **no** lleva
  la norma (0 apariciones de `autorización expresa` en `stage-3-tdd.md` y `packets/common.md`
  instalados, contra 6 y 1 en el repo).
- **CLI instalada en HOME emite paquetes con instrucciones obsoletas** tras cambiar las fuentes
  (`02f7ae49`); **hasta desplegar, preparar paquetes con `scripts/cdad_packet.py` del repo**.

## 5. Límites de esta evidencia

Focal, no completa; sin tercera revisión independiente (declarado); el despliegue se verificó por
grep sobre los dos árboles instalados y no reinstalando; no se re-ejecutaron las mutaciones de la
primera review (O1 es deuda declarada); no se evaluó conducta real de agentes, que la spec excluye
explícitamente.
