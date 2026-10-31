# Directiva del owner — reutilizar la cobertura existente antes de crear tests

**Vigente desde:** 2026-10-31, por decisión del dueño (Pablo).
**Alcance:** la selección de pruebas de todo encargo CDAD a partir de la próxima
unidad que edite las fuentes; se registra acá mientras no esté formalizada.
**Estado:** directiva vigente en uso; su formalización en las fuentes es una
unidad propia, todavía sin abrir.

## Texto de la regla

> **Antes de pedir tests nuevos, el AUDIT debe verificar si los tests existentes
> ya cubren las condiciones del contrato. Sólo las condiciones que quedan sin
> cubrir producen tests nuevos, y esos tests son los mínimos necesarios para
> cubrir únicamente lo que falta. No se pide un test por condición, ni por
> postcondición, ni por simetría: se pide cobertura de contrato, y la que ya
> existe no se duplica.**

La regla se apoya en la doctrina vigente «test por contrato, no por cobertura»
(`docs/epics/epic-008-suite-coherence/owner-rule-tests-contract.md`, 008-006) y la
extiende en un punto que aquella no fijaba: **el inventario de cobertura
existente precede a la creación de pruebas**.

## Cláusulas operativas

1. **AUDIT — mapa de cobertura, no sólo de selección.** Para cada condición del
   contrato, el AUDIT declara: `covered` / `partially covered` / `uncovered`, y
   nombra el test existente y la aserción concreta que la cubre. «Hay tests del
   módulo» no es cobertura; la aserción tiene que proteger esa condición.
2. **Sólo lo no cubierto entra a RED.** Un test nuevo se justifica únicamente por
   una condición `uncovered` o por la parte faltante de una `partially covered`.
   Si la condición ya está cubierta, no se agrega un test equivalente: se cita el
   existente.
3. **Mínimo necesario, no mínimo conveniente.** Un solo test puede cubrir varias
   condiciones si su resultado observable es el mismo. La regla 2 de la doctrina
   (variantes internas con el mismo resultado observable = un test) sigue
   mandando. «Mínimo» se mide contra las condiciones del contrato, no contra el
   esfuerzo del rol.
4. **Cada test nuevo declara su hueco.** Una línea con: condición que cubre, por
   qué ningún test existente la protege, y qué se rompe para el usuario sin él
   (R4). Sin las tres, el test no entra.
5. **El POST-AUDIT audita la afirmación de cobertura**, no sólo la aplicación de
   cambios: en una sesión distinta verifica que los tests citados realmente
   cubren lo que el AUDIT dice, y que lo declarado `uncovered` no esté ya
   protegido en otro archivo.
6. **El gate del orquestador** comprueba dos cosas antes de aprobar RED: que el
   mapa de cobertura exista con ubicaciones, y que todo test nuevo tenga su hueco
   declarado. Un test nuevo sin hueco se devuelve.
7. **No se relaja nada de seguridad, integridad o pérdida silenciosa de datos:**
   la facultad de promoción de la cláusula 9 de la doctrina 008-006 sigue
   intacta, y un test promovido por esa vía declara su motivo, no se disfraza de
   cobertura faltante.

## Dónde se aplica cuando se formalice

- `skills/cdad-cycle/packets/roles/test-writer.md` (deber de AUDIT y RED).
- `skills/cdad-cycle/packets/substages/test-writer-audit.md`,
  `test-writer-post-audit.md` y `test-writer-red.md`.
- `skills/cdad-cycle/references/stage-3-tdd.md` (detalle de la selección).
- `skills/cdad-cycle/sources/roles/test-writer.md` y la regla de gate en
  `sources/roles/orchestrator.md`.
- Los agentes generados que correspondan, con su verificador ejecutable.

No se edita nada de esto desde una unidad en curso: son contratos del skill y
exigen su propia spec, su plan, su revisión y su gate.

## Cómo se acredita que la regla funciona

Una feature de prueba donde el AUDIT demuestre, con ubicaciones, que K condiciones
ya están cubiertas por tests existentes; que se agreguen sólo los tests de las
condiciones `uncovered`/`partially covered`; y que el RED resultante falle
únicamente por comportamiento realmente ausente. El control de la unidad debe
fallar cerrado si un test nuevo no declara su hueco o si el mapa de cobertura
nombra un test que no contiene la aserción.

## Riesgo que la regla debe controlar

El atajo peligroso es declarar `covered` de más para no escribir tests. Por eso la
cobertura se declara **con nombre de test y aserción**, y la audita una sesión
distinta (cláusula 5). Un `covered` sin aserción identificable se trata como
`uncovered`.

## Medición que la motiva

- Suite del repositorio: **1764 funciones de test / 1918 casos**, con un cierre
  que tarda alrededor de una hora porque buena parte lanza el CLI como subproceso.
- La suite creció por historia de features y no por capacidad, como ya diagnosticó
  el epic 008; esta directiva ataca la causa en el punto donde se decide: el
  AUDIT de cada unidad.

## Lo que esta directiva no hace

- No autoriza borrar tests existentes: reducirlos exige su propia unidad, con
  mapa test→promesa y decisión de la autoridad.
- No cambia el significado de las postcondiciones ni el gate de aceptación.
- No convierte «ya está cubierto» en una excusa: la cobertura se prueba, no se
  supone.
