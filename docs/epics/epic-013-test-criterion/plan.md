---
epic_id: epic-013-test-criterion
epic_name: Criterio y mantenimiento de la suite de tests
created_at: 2026-11-02
approved_by: Pablo
approved_at: 2026-11-02
---

<!-- cdad:plan-anchors
{"history": ["Cambios al plan"], "authorization": ["Autoridad"]}
-->

# Epic 013: Criterio y mantenimiento de la suite de tests

## Resumen

Cerrar el circuito entre generar y mantener tests: buscar la protección existente
antes de añadir, acreditar qué aporta cada test y poder sustituir redundancias sin
perder obligaciones. R2, R4 y R7 ya contienen la base; faltan coherencia operativa
y una disposición ordinaria de sustitución. El objetivo primario es el criterio;
el tamaño y la duración de la suite son síntoma y medida.

Insumos: `docs/specs/013-test-criterion-suite-review/discovery.md` y
`discovery-research.md`, y `docs/research/testing-practices-2026-10-25.md`.

## Alcance

Entra:
- Coherencia del criterio en sus fuentes y consumidores.
- Inventario de la suite al día y trazabilidad suficiente para el lote piloto.
- Disposición de redundancias y una poda piloto acotada.
- Mutación únicamente como experimento acotado de esa poda.
- Diagnóstico de rendimiento, condicionado a una decisión posterior del dueño.

No entra:
- Retirar `cdad-spec-and-test` (decisión del dueño, 2026-11-02: después). Sus
  contradicciones quedan registradas en el Discovery.
- Acreditación semántica de los 1937 tests, gate universal de mutación, clasificador
  automático de equivalencias, migración masiva a ejecución en proceso.
- Reescribir los contratos cerrados 008-002 y 008-006.

## Features

| # | Feature | Resultado | Depende de |
|---|---|---|---|
| 1 | `013-001-criterion-coherence` | Selección por promesa, contribución respecto de la suite existente y sustitución en AUDIT/POST-AUDIT; instrucciones operativas alineadas; presupuesto de propiedades resuelto; contradicción sobre la suite completa de cierre resuelta en la norma | — |
| 2 | `013-002-live-inventory` | Inventario sin la brecha actual (`cdad-suite.py validate` rc=1, 158 nodeids en 18 archivos), clasificación separada de acreditación, mapa del lote piloto | — |
| 3 | `013-003-redundancy-pilot` | Lote revisable con decisión de mantener, extender, sustituir o consolidar; sustitutos y obligaciones conservadas; evidencia antes/después; experimento de mutación si resulta viable | 1, 2 |
| 4 | `013-004-suite-performance` | Línea base, atribución de costos y optimización de la preparación; paralelismo solo si hace falta y se demuestra seguro | 2; **se abre solo por decisión del dueño** |

## Contratos entre features

- **Vocabulario:** 013-001 fija los términos de disposición; 013-002 y 013-003 los consumen sin redefinirlos.
- **Inventario:** 013-002 es el dueño de los datos; 013-003 actualiza el inventario con cada sustitución.
- **Genealogía:** toda obligación sustituida conserva su rastro hasta el test que la protege.
- **Poda y velocidad son promesas separadas:** una no se presenta como prueba de la otra.

## Criterios de aceptación del epic

- Rutas legacy y por paquetes transmiten el mismo criterio aplicable.
- `cdad-suite.py validate` termina con rc=0.
- El piloto concluye con decisiones acreditadas por revisión independiente; «mantener» es un resultado válido.
- Ninguna promesa comprometida pierde verificación (R7). No hay cuota de tests, bytes ni minutos.
- Los cambios van a `sources/` y regeneración, nunca a los agentes generados.

## Evidencia y suite completa

Directiva del dueño: la suite completa no es gate por defecto; cada feature cierra
con evidencia focal. Las normas vigentes (`stage-3-tdd.md`, gate E3→E4) dicen otra
cosa; 013-001 resuelve esa contradicción. Corrida completa solo con autorización
expresa. Sin ella, la integración del epic la declara como no realizada.

## Riesgos

- Confundir igual resultado o cobertura con igual protección.
- Consolidar hasta crear tests enormes difíciles de diagnosticar.
- Justificaciones genéricas de contribución.
- Mutantes que no alcanzan el subproceso probado: una campaña inconclusa no acredita nada.

## Autoridad

Aprueba el dueño. Decisiones ya tomadas el 2026-11-02: cuatro unidades con estas
dependencias; poda por obligaciones conservadas, sin cuota; mutación solo como
experimento acotado; retiro de la skill y línea base aplazados.

## Cambios al plan

Ninguno todavía.
