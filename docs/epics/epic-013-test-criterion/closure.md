# Closure — epic-013-test-criterion

**Cerrado:** 2026-11-02. **Estado:** cerrado en el repositorio; **no publicado ni desplegado** (reserva del dueño).
**Autoridad:** HITL delegada de Pablo (`execution.md`).

## 1. Resultado

El criterio de selección y mantenimiento de tests es uno solo y aplicable por las rutas legacy y por paquetes: selección por promesa, contribución respecto de la protección existente, disposición única, sustitución de comportamiento vigente en POST-AUDIT con verde y sensibilidad, presupuesto de propiedades declarado y **suite completa solo con autorización expresa** (ADR-041). El inventario está al día (`validate` rc=1 → rc=0) con declaración de proyecto y procedimiento de sustitución. El piloto concluyó **Mantener** el lote B1 sin podar: la hipótesis de ahorro no se confirmó en ese lote; se demostró el procedimiento.

| Unidad | Cierre | Resultado |
|---|---|---|
| 013-001-criterion-coherence | `docs/specs/013-001-criterion-coherence/closure.md` | criterio coherente; ADR-041 |
| 013-002-live-inventory | `docs/specs/013-002-live-inventory/closure.md` | `validate` rc=0; `docs/suite-maintenance.md` |
| 013-003-redundancy-pilot | `docs/specs/013-003-redundancy-pilot/closure.md` | Mantener A/B/C; sin cambios de tests |
| 013-004-suite-performance | — | **No abierta**: se abre solo por decisión del dueño |

## 2. Evidencia

Ver `integration.md`. 40 focales verdes, `validate` rc=0, `make agents` sin deriva, doctrina OK. **Suite completa no realizada** (directiva del dueño).

## 3. Retrospectiva breve

- Las plan-reviews y reviews encontraron bloqueantes reales en 3 de 3 unidades (13-001: 6+3; 13-002: 2+4; 13-003: 1 documental). Omitir la plan-review de 013-003 no ocultó defectos, pero no hay contraste.
- Los tests (8 por unidad en promedio) no detectan los defectos semánticos que halla la review; esa carga la asume el reviewer, como las specs declaran.
- Tooling: paquetes con CLI instalada quedan obsoletos tras cambiar fuentes (usar CLI del repo hasta desplegar); `--write-scope` a archivo existente falla; `docs=docs` choca con referencias `contract` en `begin`; la clase de la referencia en `begin` tuvo que ser `living`.

## 4. Deuda declarada

Las de cada cierre (O1–O7 de 013-001, O3/O4 y 16/21 asignaciones sin examinar de 013-002, PC-5 inconclusa y solape A/B de 013-003); suite completa no realizada; sin tercera revisión de 013-001, ni segunda de 013-002 y 013-003; 013-004 no abierta; **despliegue pendiente: la instalación no tiene la norma**. Sin ADR nuevo del epic más allá de ADR-041.

## 5. Siguiente

Decisión del dueño: publicar y desplegar; abrir o no 013-004. Antes de abrir 013-004, `suite-maintenance.md` debe asignar quién registra `validate` cuando el resultado es Mantener.
