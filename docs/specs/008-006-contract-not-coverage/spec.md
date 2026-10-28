---
feature_id: 008-006-contract-not-coverage
feature_name: Tests por contrato, no por cobertura
created_at: 2026-10-27
approved_by: pending
approved_at: pending
---

# Spec: Tests por contrato, no por cobertura

## User journey

- **Actor:** dueño de una feature y roles CDAD que la especifican, verifican y cierran.
- **Objetivo:** obtener garantías del comportamiento comprometido sin pagar tests redundantes ni ocultar verificaciones diferidas.
- **Inicio legítimo:** una feature con contrato aprobado y roles aislados.
- **Primer resultado útil:** una propuesta RED justificable por promesas de usuario, con diferimientos explícitos y sin limitar la robustez del código.

La doctrina selecciona tests por promesas observables, conserva la trazabilidad
a postcondiciones y registra lo diferido. No incorpora un nuevo mecanismo de
recepción ni pretende automatizar el juicio sobre la pertinencia de un test.

## Acceptance criteria

- Las fuentes asignan cada regla a un único hogar; los consumidores la citan
  o reciben por composición, sin otra definición editable.
- Todas las promesas comprometidas siguen sujetas a verificación por comportamiento.
- Las plantillas permiten identificar promesas, postcondiciones y diferimientos.
- Ambos runtimes reciben la doctrina regenerada sin alterar la política de modelos.

## Contract

### Promesa A — Especificar garantías sin multiplicar escenarios equivalentes

**PC-1.** La fuente del architect exige postcondiciones numeradas y verificables
agrupadas por promesa observable, prohíbe exigir N variantes con idéntico resultado
y exige `deferred-hardening`. La plantilla de spec permite identificar esa
agrupación y contiene la sección, incluso cuando su contenido es `None`.
La plantilla de plan referencia esas promesas y diferimientos sin cambiar su
esquema ni exigir un test por tarea.

### Promesa B — Recibir tests necesarios y trazables, no cuotas de cobertura

**PC-2.** La convención compartida del test-writer establece un test por promesa,
no por postcondición ni camino interno; exige trazabilidad a las postcondiciones
protegidas y la declaración «sin este test, el usuario…». El detalle de stage 3
y la plantilla de auditoría aplican esa selección sin reconstruir cuotas por
postcondición, simetría o cobertura. Se conservan la auditoría independiente
y las propiedades derivadas de invariantes contractuales.

### Promesa C — Revisar y decidir sin bloquear por QA especulativo

**PC-3.** El reviewer exige consecuencia de usuario para un hallazgo por falta
de test; sin ella, lo registra como diferido no bloqueante, sujeto al gate.
El orquestador exige y registra antes de aprobar RED la respuesta a
«¿qué se rompe para el usuario sin este test?». Sin respuesta, el test no entra
como exigencia ordinaria. Puede promover un hallazgo por seguridad,
integridad/pérdida silenciosa de datos o regresión evidente y cara de descubrir
tarde; registra expresamente el motivo. Son instrucciones a los roles,
no validaciones nuevas del receptor de informes.

### Promesa D — Conservar robustez y diferimientos al entregar

**PC-4.** La fuente del implementer y su fila contractual sustituyen la exigencia
de limitarse al mínimo que pasa el test por implementación simple del
comportamiento aprobado con robustez razonable, incluidas validaciones,
guardas y manejo de errores necesarios aunque ningún test los exija.
La fuente del scribe exige incluir `deferred-hardening` y sus disposiciones
registradas en el borrador de closure, sin ampliar sus permisos de edición
ni aprobación.

### Promesa E — No perder garantías por aplicar la reducción de redundancia

**PC-5.** El detalle canónico de stage 3 contiene el contrapeso explícito:
cada promesa comprometida debe verificarse por comportamiento antes de aceptar
la feature; un test puede verificar varias postcondiciones. Diferir hardening
no permite diferir una promesa comprometida ni relajar seguridad, integridad
o conservación de datos. Los consumidores remiten a ese contrapeso.
Las excepciones de promoción se definen únicamente en el hogar del gate.

### Promesa F — Recibir la misma doctrina en los agentes distribuidos

**PC-6.** `make agents` regenera OpenCode y Claude Code desde las fuentes.
Los agentes resultantes contienen las reglas o punteros correspondientes a su
rol, y la tabla compuesta no conserva «one test per postcondition» ni la
restricción contradictoria del implementer. La convención compartida mantiene
un único host editable. Se preserva la política existente de modelos:
los artefactos generados no incorporan `model:`; un agente instalado modificado
localmente, incluido su `model:`, no se sobrescribe mediante esta feature.

## Siete reglas, siete hogares

El siguiente texto mínimo es contractual; puede traducirse sin perder ninguna
obligación. Las plantillas son consumidores, no nuevos dueños.

| Regla | Único hogar editable | Texto mínimo |
|---|---|---|
| R1 — Especificación | `sources/roles/architect.md` | Agrupa postcondiciones numeradas y verificables por promesa observable; no exijas variantes con el mismo resultado. Toda spec incluye `deferred-hardening`. |
| R2 — Selección y justificación | `sources/roles/test-writer.md`, bloque `cdad-shared:convention-rule` | Un test por promesa observable, no por postcondición, simetría, cobertura ni variante interna equivalente. Traza cada test a sus postcondiciones y declara «sin este test, el usuario…». |
| R3 — Hallazgos de tests | `sources/roles/reviewer.md` | Un hallazgo por falta de test nombra la consecuencia de usuario; sin ella va a `deferred-hardening` y no bloquea, salvo promoción según el gate del orquestador. |
| R4 — Gate y promociones | `sources/roles/orchestrator.md` | Antes de aprobar RED pregunta y registra «¿qué se rompe para el usuario sin este test?». Sin respuesta no se exige. Una promoción por seguridad, integridad/pérdida silenciosa de datos o regresión evidente y cara de descubrir tarde requiere motivo registrado. |
| R5 — Robustez del código | `sources/roles/implementer.md` | Implementa simplemente el comportamiento aprobado, sin funcionalidades especulativas. La selección de tests no limita validaciones, guardas ni manejo razonable de errores necesarios. |
| R6 — Persistencia del diferimiento | `sources/roles/scribe.md` | Incluye el `deferred-hardening` de la spec y sus disposiciones registradas en el borrador de closure para materialización por el orquestador; no lo omitas silenciosamente. |
| R7 — Contrapeso de aceptación | `skills/cdad-cycle/references/stage-3-tdd.md` | Reducir redundancia no reduce garantías: toda promesa comprometida se verifica por comportamiento antes de aceptar. Un test puede verificar varias postcondiciones. El diferimiento no permite posponer promesas comprometidas ni relajar seguridad, integridad o conservación de datos. |

Las filas contractuales describen las responsabilidades de su dueño sin crear
una segunda regla. Stage 3 cita R2 para selección y R4 para promociones.
La convención compartida cita R7. Los demás roles citan los hogares aplicables.
La reproducción generada no constituye duplicación editable.

## Límite verificable

Los tests de esta feature son estáticos: verifican presencia del contenido
contractual, ausencia de contradicciones identificadas y composición en fuentes,
plantillas y agentes generados.

No determinan si una consecuencia de usuario es verdadera o suficiente.
Ese juicio pertenece a la revisión y al gate con evidencia registrada.

Queda resuelto el VERIFY del discovery: no se añade rechazo operativo de informes
sin declaración, nuevo formato de recepción ni cambio en `cdad_result`.
Eso requeriría otro contrato.

## Verificación proporcionada

- Lectura de las siete reglas en sus hogares y de sus referencias consumidoras.
- Grep contextual para detectar formulaciones contradictorias señaladas en discovery.
- Tests estáticos agrupados por las promesas anteriores; no un test por archivo,
  frase, rol o variante.
- Regresiones focales existentes de composición, generación y plantillas.
- Regeneración de ambos runtimes mediante `make agents`.

La literalidad sólo es necesaria para identificadores y marcadores contractuales;
los tests no deben congelar párrafos completos ni convertir su redacción en API.

## deferred-hardening

- Juicio automatizado sobre relevancia, veracidad o suficiencia de la consecuencia
  declarada: no se implementa; el juicio permanece humano/agéntico con revisión.
- Rechazo operativo de informes incompletos: fuera de esta unidad; necesita
  contrato propio de formato y recepción.
- QA intensivo de variantes equivalentes, carga y rendimiento no comprometidos:
  diferido, sin convertirlo en requisito de aceptación.

Ningún elemento anterior permite diferir una promesa comprometida.
R7 gobierna la aceptación y R4 las promociones excepcionales.

## Out of scope

- Reorganizar o eliminar tests históricos.
- Cambiar protocolos, schemas, recepción de resultados o transiciones del ciclo.
- Cambiar selección de modelos, instalar agentes en destinos reales o activar servicios.
- Limitar la robustez razonable del implementer.

## Technical context

- `sources/roles/test-writer.md:35,65-83`: fila contractual y convención compartida.
- `sources/roles/orchestrator.md:273-278`: aplicación de la convención al gate.
- `skills/cdad-cycle/references/stage-3-tdd.md:17-27,101-110,238-245`:
  selección, auditoría y aceptación que deben alinearse.
- `skills/cdad-cycle/assets/spec-template/spec.md`: postcondiciones y sección
  nueva de diferimiento.
- `skills/cdad-cycle/assets/spec-template/test-audit.md`: trazabilidad y justificación.
- `skills/cdad-cycle/assets/feature-plan-template.md`: referencias sin cambiar schema.
- `Makefile:10-18`: staging y promoción para ambos runtimes.
- `scripts/cdad-generate.py:840-900`: unicidad del bloque y composición.

## Decisión de diseño

Se elige una regla general por promesa, con trazabilidad muchos-a-uno,
frente a cuotas específicas por archivo, postcondición o camino interno.
El criterio es conservar garantías sin multiplicar verificaciones equivalentes.
Los riesgos excepcionales tienen un único decisor y motivo registrado.

**AJ4 — La verificación de esta unidad no puede ser un RED del test-writer, y se declara por qué.** La política de alcance (`cdad_packet.py`, allowlist por rol) prohíbe al test-writer **leer** `sources/` y `agents/` (clase `implementation`), que es exactamente el objeto bajo prueba. Se verificó intentándolo: el paquete se rechaza. Por lo tanto:
- la verificación de PC-1..PC-6 es (a) **inspección estática del reviewer** con archivo:línea sobre fuentes, plantillas y agentes generados; (b) un **verificador ejecutable** `scripts/cdad-doctrine-check.py` que el closer y 008-005 corren, escrito por el implementer y revisado por el reviewer; (c) las regresiones existentes de generación y plantillas.
- **No hay RED de test-writer** en esta unidad. Es una desviación declarada, no un hueco: la independencia la da el reviewer, que no escribió el cambio.
- Va a `deferred-hardening`: convertir la doctrina en tests bajo `tests/` exige que la política de alcance permita al test-writer leer el texto fuente, o que el verificador se instale como producto; hoy ninguna de las dos existe.

## Ajustes del orquestador (review del borrador, 2026-10-27)

**AJ1 — El generador es un consumidor más, y estaba contradiciendo la regla.** `scripts/cdad-generate.py:523-531` inyecta en el agente del test-writer un fragmento RED que exige «one test per numbered postcondition». Actualizar sólo los siete hogares y la tabla compuesta habría distribuido **las dos reglas a la vez**. Ese fragmento se alinea con R2 (o se sustituye por un puntero al hogar canónico) y PC-6 comprueba en ambos runtimes que la cuota no sobrevive. No es un octavo hogar: es un consumidor del hogar de R2.

**AJ2 — «Un test por promesa» no es un techo.** R2 y PC-2 se leen como: **no se multiplican tests para resultados observables equivalentes**, y sí se escriben los necesarios para **comportamientos comprometidos distintos** y los que R4 promueva con motivo. La unidad de selección es la promesa; el límite es la equivalencia observable, no el número.

**AJ3 — `deferred-hardening` registra lo que se decide no probar, con motivo.** La obligación no es que la sección exista: es que **cada diferimiento decidido quede ahí con su motivo**, y que `None` signifique «no hay ninguno», no «no lo pensamos». La selección y el gate lo registran; el scribe lo traslada al `closure.md`.

Status: Pending approval
