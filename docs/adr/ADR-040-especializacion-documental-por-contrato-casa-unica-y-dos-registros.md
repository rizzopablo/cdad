# ADR-040 — Especialización documental por contrato: una casa normativa y dos registros de cierre

- **Estado:** Accepted (adoptado el 2026-10-31 en el cierre del epic 010 por el orquestador
  en nombre del dueño, bajo el mandato HITL del 2026-10-30, §1 y §3; documenta decisiones ya
  ejercidas por las cinco unidades, no crea alcance nuevo).
- **Fecha:** 2026-10-31.
- **Decisores:** dueño del repo (aprobación); orquestador (materialización bajo ADR-003).
- **Roles afectados:** `orchestrator`, `architect`, `test-writer`, `implementer`,
  `reviewer`, `scribe` y sus variantes Odoo.
- **Confidence:** **Media** (ver §Confianza).

## Contexto y problema

El ciclo CDAD produce también entregables cuyo producto es un documento —relevamiento,
mapa de proceso, historia de usuario—. Hasta `010-001`, cada encargo inventaba sus
criterios: qué cuenta como evidencia, cómo se cita una fuente, cuándo un pendiente impide
aceptar, hasta dónde puede escribir el rol que produce y quién revisa. El riesgo no era
la falta de capacidad de los roles, sino que **cada encargo definiera su propia vara**, y
que un verde de control se leyera como corrección documental.

La pregunta de diseño era de forma: ¿un agente o skill documental con sus propios
permisos, campos nuevos del estado y una etapa nueva del ciclo, o una especialización
declarada con el transporte que ya existe? Un agente nuevo acumularía resolución,
clasificación de rutas y distribución, y un campo nuevo del estado obligaría a migrar
identidad y compatibilidad histórica.

## Decisión

1. **La especialización documental es de contrato, no de identidad.** Un encargo
   documental se declara con los campos que el encargo ya lleva: `objective` y promesas,
   `expected_output`, `inputs`/`read_scope`, `write_scope`, `invariants` y alcances, y
   `evidence_required` con límites y pendientes. **No se crea** rol, agente, etapa,
   subfase, campo del estado ni selector documental, y `stack` conserva su significado de
   dominio (la variante Odoo sigue siendo de dominio, no de tipo de producto).
2. **Una sola casa normativa.** `skills/cdad-cycle/references/documentary-contracts.md`
   fija las cuatro categorías obligatorias (evidencia, propuesta, contradicción,
   pendiente) como **criterio y no como formato**, el localizador mínimo por tipo de
   fuente, la clasificación de pendientes por su efecto sobre el contrato, las cuatro
   declaraciones de todo encargo documental, las fronteras por rol, los dos registros y
   sus límites. Los consumidores la **citan por puntero** —seis fuentes de rol, cinco
   bloques estáticos de `packets/roles/` y los agentes derivados de ambos runtimes— y no
   la re-enuncian. Se elige esta forma porque la distribución de referencias y la
   obligación por puntero ya existen (precedente: ADR-034 y
   `design-principles.md`).
3. **Dos registros de cierre que no se sustituyen.** El control automático/estructural
   acredita qué se ejecutó, con qué resultado, alcance y límites; la revisión semántica
   independiente acredita qué afirmaciones y fuentes se examinaron, con hallazgos y
   abstenciones. Un verde estructural **no** acredita fidelidad a las fuentes, un recibo
   de transporte **no** acredita revisión semántica y la aceptación estructural de un
   paquete no es aprobación.
4. **Quien produce no modifica su oráculo.** Fuentes, verificadores, contrato de
   aceptación y plantillas usadas como oráculo quedan fuera del GREEN; una superposición
   o una ambigüedad sobre qué papel juega un archivo **detiene** esa parte, y un cambio
   legítimo del oráculo vuelve al rol competente y, si altera el contrato, a aprobación.
5. **La norma aplica condicionalmente y no amplía autoridad.** Gobierna cuando el encargo
   declara producto documental; no cambia la clasificación de rutas de la política, los
   permisos ni los alcances admitidos, no reemplaza el Memory Bank y no convierte al
   scribe en productor documental general.

## Consecuencias

**Positivas.** El ciclo gana capacidad documental sin multiplicar mecanismos: la
generación, la instalación y la resolución del perfil se acreditan con los agentes
existentes y un encargo bien declarado (`010-002`: 11 agentes por runtime, derivación
sobre 100 combinaciones, frontera de escritura conservada, guardas de Claude idénticas).
La norma tiene un solo dueño editable y un techo medido (3709 / 12000 bytes en los bloques
estáticos). El reparto de evidencia resistió su propia prueba: en `010-001` los 11 tests
estaban verdes y la norma omitía dos reglas de la decisión (B1), lo que demuestra
operativamente que un verde estructural no cubre la suficiencia semántica.

**Negativas y límites declarados.** (a) La obligación vive en **dos superficies** —fuentes
de rol y bloques estáticos— más la regeneración de agentes, y ninguna sustituye a la otra;
dejar sólo las fuentes produjo dos contratos publicados que se contradecían (B2 de
`010-001`), y el generador **no** compone la tabla §2 de `SKILL.md`, que se corrige a mano.
(b) La especialización es **disciplina de despacho, no guarda mecánica**: el despachador
puede omitir una cláusula de forma (I-15: el request del ensayo no citó los commits de
fijación) o mandar leer una norma fuera del alcance del rol (I-14); ambas están en el
backlog con condición de cierre. (c) La fidelidad semántica se acredita **por revisión
humana/sesión separada**, sobre un desafío declarado: el piloto `010-003` demostró
detección 3/3 sobre una muestra **sembrada y sintética**, sin detección a ciegas y sin
garantía de conducta de modelos. (d) Mientras no se publique, la obligación llega por el
paquete y por la toolchain del repositorio, no por el agente instalado.

**Límites que este ADR no promete.** Parser o linter universal de documentos, formatos
binarios, corpus reales de clientes, detección automática de contradicciones o verdad
semántica, protección mecánica por hash de cada insumo, paridad total entre esquema y
validador, ni verificación de conducta de modelos.

## Alternativas consideradas

- **Un agente o skill documental nuevo, con etapa propia.** Rechazada: acumula permisos y
  multiplica resolución, clasificación y distribución; contradice el invariante de no
  crear mecanismos por defecto y el contrato de roles vigente.
- **Campos nuevos del estado o un selector documental.** Rechazada: obliga a migrar
  identidad y compatibilidad histórica para expresar algo que el transporte ya expresa
  (`010-002` D1).
- **Criterios documentales por encargo, sin casa normativa.** Rechazada: es el estado
  previo; cada encargo define su vara y ninguna obligación es contrastable entre encargos.
- **Formato documental obligatorio (cuatro secciones fijas o una tabla universal).**
  Rechazada: fabrica instancias ficticias; las categorías se exigen como distinción
  verificable, y el encargo puede fijar una forma más específica cuando forma parte de su
  promesa observable.
- **Puntaje de un LLM como verificación semántica.** Rechazada: no acredita contraste con
  fuentes ni trazabilidad del hallazgo; se exige revisión independiente con localizador y
  evidencia, y aceptación del usuario.

## Referencias

- `docs/specs/010-001-documentary-contracts/spec.md` (PC-01..PC-16), `closure.md`,
  `review.md`, `review-002.md`.
- `docs/specs/010-002-documentary-role-integration/spec.md` (PC-01..PC-13, D1..D5).
- `docs/specs/010-003-documentary-pilot/{semantic-evidence.md, functional-acceptance.md,
  closure.md}` y `docs/epics/epic-010-documentary-specialization/{plan.md, integration.md}`.
- `docs/systemPatterns.md` §«Contratos documentales — una casa, punteros y dos registros»
  y §«Especialización documental por contrato y destinatario coherente».
- Precedentes: ADR-003 (materialización), ADR-014 (recepción/materialización/aprobación
  separadas), ADR-034 (principio con casa única y deberes de rol), ADR-036 (verificador
  del productor importado por consumidores).
- Propuesta antecedente conservada en `docs/specs/010-001-documentary-contracts/scribe-report.md`
  §«Propuesta de ADR» (Medium, no adoptada por la unidad).

## Confianza

**Media.** A favor: la decisión se ejerció de punta a punta en las cinco unidades, con
revisión independiente en cada una, detección semántica acreditada 3/3 sobre el desafío
sembrado y los dos registros funcionando como límite operativo (B1 de `010-001` es la
prueba de que el reparto hace falta). En contra: la obligación **no está vigente en
ninguna instalación real** (deriva de 52 archivos), su cumplimiento depende de la
disciplina de despacho y no de una guarda mecánica —I-8, I-10, I-14 e I-15 son defectos
abiertos del transporte— y la suficiencia semántica sólo está acreditada sobre una muestra
sintética y declarada. Esas tres razones son las que impiden proponerlo como `Accepted`
hoy; el contenido de la decisión no está en duda, su vigencia y su enforcement sí.
