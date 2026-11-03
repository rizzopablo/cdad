# ADR-042: Defaults de evidencia por momento (supersesión parcial de ADR-041)

- **Status**: Accepted (decisión delegada del dueño, epic-014, 2026-11-02).
- **Origen**: `docs/specs/014-001-suite-evidence-defaults/spec.md` (PC-1..PC-14) y `docs/epics/epic-014-suite-evidence-policy/plan.md`.
- **Supersede**: sustituye únicamente la cláusula de autorización/defaults de ADR-041 (decisión 1: «Suite completa solo con autorización expresa del dueño, también en cierre, integración, merge o cambio transversal»), y sus consecuencias incompatibles. No reescribe la decisión de ADR-041: su texto se conserva y su vigencia queda anotada con puntero a este ADR. Esta sustitución es una supersesión parcial, no una derogación total.

## Contexto

ADR-041 fijó «suite completa solo con autorización expresa» como regla uniforme, incluso en cierre de epic. El plan aprobado de epic-014 autoriza por política la corrida ordinaria de cierre de epic y exige distinguir tres momentos (durante el ciclo, cierre de feature, cierre de epic). Mantener la exigencia uniforme obligaba a pedir un permiso individual que la política ya otorga, o a omitir la corrida de cierre por simple ausencia de ese permiso.

## Decisión

1. **Defaults por momento.** El hogar canónico (`skills/cdad-cycle/references/stage-3-tdd.md` §«Test evidence policy») declara:
   - Durante el ciclo: tests focales y regresión proporcional; sin suite completa como rutina de iteración o depuración.
   - Cierre de feature: suite completa recomendada. Si se omite se registra «suite completa no realizada», motivo, selección ejecutada y límites.
   - Cierre de epic: suite completa obligatoria por defecto. Omitirla requiere dispensa expresa del dueño, registrada con motivo para ese cierre.
2. **Autorización suficiente.** La aprobación de esta política autoriza la corrida ordinaria de cierre de epic. Ninguna instrucción operativa exige autorización adicional para esa corrida ni permite omitirla por simple ausencia de permiso individual.
3. **Alcance de la sustitución.** Se sustituye la cláusula de autorización/defaults de ADR-041 y las órdenes operativas incompatibles (frecuencia por GREEN, regresión completa exigida por cambio de árbol o review-fix como automatismo). Se conservan de ADR-041: la exigencia de contribución por disposición única, las propiedades con presupuesto declarado, la instalación limpia de addon como dimensión distinta, y la atribución de corridas.
4. **Lo que no cambia.** ADR-039 conserva su estado y su recorrido; este ADR no lo presenta como ratificado ni impone su herramienta a todos los proyectos. No se crea runner, flag, workflow, campo de estado ni mecanismo de autorización nuevos. La autorización no equivale a evidencia, ni autoriza publicación, despliegue o reintentos indiscriminados.

## Consecuencias

- Los consumidores referencian el hogar y aplican su consecuencia local sin reproducir doctrina paralela.
- Los cierres honestos registran omisión, fallo o dispensa sin etiquetarlas como verde.
- El costo y el entorno se declaran por proyecto; la lentitud no constituye dispensa implícita.
- La instalación limpia (`test-clean` cuando sea exigible) y la amplitud de la selección son dimensiones distintas.

## Contribución, propiedades e instalación limpia (preservadas de ADR-041)

- **Contribución**: cada test auditado conserva su disposición única (Mantener, Extender, Sustituir, Consolidar, Añadir, Retirar).
- **Propiedades**: presupuesto finito y positivo declarado y justificado por campaña; sin cuotas universales.
- **Instalación limpia**: cuando el producto o el diff tocan addon, `test-clean` (o el mecanismo declarado del proyecto) sigue vigente como evidencia específica y no se confunde con la amplitud de la suite.
