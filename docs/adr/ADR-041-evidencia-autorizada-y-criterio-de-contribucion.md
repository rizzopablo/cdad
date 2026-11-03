# ADR-041: Suite completa solo con autorización; los tests se mantienen por contribución

- **Status**: Accepted (decisión delegada del dueño, epic-013, 2026-11-02).
- **Origen**: `docs/specs/013-001-criterion-coherence/spec.md` (PC-4..PC-14) y `docs/epics/epic-013-test-criterion/`.

## Contexto

> **Nota de vigencia (2026-11-02, epic-014):** la cláusula de autorización/defaults de la Decisión 1 queda
> sustituida por `docs/adr/ADR-042-defaults-de-evidencia-por-momento.md` (supersesión parcial). El resto de
> esta decisión (contribución, propiedades, instalación limpia y atribución) sigue vigente. Este aviso no
> reescribe la decisión histórica.

La política de evidencia exigía la suite completa al cierre (ADR-020, decisión 1) y el gate de CI la corría
siempre (ADR-039, decisión 6). La suite tarda 46–103 min; el dueño dispuso que la suite completa no es gate por
defecto. Además, las normas empujaban a acumular tests por postcondición y no ofrecían una salida ordinaria
para sustituir redundancias.

## Decisión

1. **Suite completa solo con autorización expresa del dueño**, también en cierre, integración, merge o cambio
   transversal. Sin ella se registra «suite completa no realizada» y la selección ejecutada; nunca «verde».
2. **ADR-020**: se sustituye únicamente su exigencia de suite completa automática. Se mantienen el hogar
   canónico (`stage-3-tdd.md`, Test evidence policy), la regresión proporcional, la equivalencia y los comandos
   declarados por proyecto.
3. **ADR-039**: se conservan su recorrido y atribución para invocaciones autorizadas. No hace obligatoria la
   herramienta en cada cierre ni en cada push, y no se ratifica aquí su estado `Proposed`.
4. **Odoo**: la instalación limpia de addon (`test-clean`) sigue vigente como evidencia específica y no se
   confunde con la suite completa.
5. **Tests**: cada test auditado recibe una disposición única (Mantener, Extender, Sustituir, Consolidar,
   Añadir, Retirar). Un sustituto de comportamiento vigente se prepara en POST-AUDIT con verde más
   sensibilidad demostrada, no en RED.
6. **Propiedades**: presupuesto declarado y justificado por campaña; se retiran las cuotas universales.

## Consecuencias

- Los cierres dependen de evidencia focal; la integración del epic declara lo que no corrió.
- La suite completa sigue siendo posible y atribuible cuando el dueño la autoriza.
- Los antecedentes de ADR-020 y ADR-039 se conservan; esta decisión es posterior.
