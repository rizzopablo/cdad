# 010-001 — Contratos documentales compartidos

**Estado:** borrador para aprobación de Pablo.  
**Épica:** `epic-010-documentary-specialization`.  
**Dependencias:** `010-000`, `010-004`.

## 1. Descripción

Incorporar criterios documentales compartidos al ciclo CDAD existente para producir relevamientos, procesos e historias de usuario trazables.

Esta feature entrega **la norma compartida y las obligaciones de sus consumidores**. No entrega todavía la selección del perfil documental —010-002— ni acredita el piloto funcional —010-003—.

La casa normativa propuesta es:

`skills/cdad-cycle/references/documentary-contracts.md`

Los roles remiten a ella mediante obligaciones breves. No se crea otro skill, agente, etapa ni mecanismo de aprobación.

La documentación funcional es producto bajo contrato; no sustituye al Memory Bank ni convierte al scribe en productor documental general.

## 2. Decisiones de diseño propuestas

Estas decisiones resuelven las preguntas del discovery, pero **no constituyen aprobación**.

### D1. Categorías obligatorias; formato flexible

**Alternativas consideradas:**

- Imponer cuatro secciones o una tabla Markdown universal.
- Exigir distinciones explícitas y localizables, sin imponer un contenedor.

**Decisión:** adoptar la segunda alternativa. Las cuatro categorías son obligatorias como criterio; no es obligatorio crear cuatro secciones vacías.

Se permite distinguirlas mediante encabezados, etiquetas, columnas o formulaciones inequívocas. El encargo puede imponer un formato más específico cuando forme parte de su promesa observable.

| Categoría | Compromiso |
|---|---|
| **Evidencia** | Una afirmación respaldada identifica qué fuente la sostiene y dónde localizarla. No atribuye a la fuente más de lo que demuestra. |
| **Propuesta** | Una alternativa del autor aparece como propuesta, no como hecho observado ni decisión aprobada. |
| **Contradicción** | Las afirmaciones incompatibles conservan sus respectivas referencias. No se inventa consenso ni se elimina una posición sin decisión acreditada. |
| **Pendiente** | La información no acreditada o decisión abierta identifica qué falta y qué permitiría resolverla. No se convierte silenciosamente en hecho. |

Las categorías describen afirmaciones o cuestiones, no necesariamente documentos completos. Una contradicción puede originar un pendiente; distinguirlos no obliga a duplicar su contenido.

**Criterio:** mantener una distinción verificable sin introducir un formato que el resultado funcional no necesita. La comprobación automática de etiquetas no demuestra que la clasificación sea correcta.

### D2. Localizador mínimo según la fuente

**Alternativas consideradas:**

- Aceptar cualquier enlace o nombre de archivo.
- Exigir siempre líneas y hashes individuales.
- Exigir identidad, ubicación interna y una versión recuperable, adaptadas a cada fuente.

**Decisión:** adoptar la tercera alternativa.

Todo respaldo debe permitir recuperar **la fuente examinada y el fragmento utilizado**:

| Tipo de fuente | Localizador mínimo |
|---|---|
| Archivo del repositorio | Ruta relativa + líneas, sección o identificador interno inequívoco + revisión o snapshot identificado. |
| Documento Markdown/texto recibido como insumo | Ruta o identificador del insumo + sección, líneas o fragmento inequívoco + versión/snapshot examinado. |
| Mensaje o decisión del usuario | Identificador recuperable del mensaje o transcripción autorizada + fecha/contexto suficiente para distinguirlo + fragmento o apartado pertinente. |
| Minuta o transcripción | Identificador y versión del insumo + sección, intervención o marca temporal pertinente. |
| Página web u otra fuente mutable | URL/identificador original + ubicación interna + versión o captura autorizada recuperable y fecha de consulta/captura. Una URL viva y una fecha, sin forma de recuperar el contenido examinado, no bastan. |

La versión puede declararse una vez en un inventario de fuentes y reutilizarse mediante identificadores. No se exige repetirla en cada cita.

No se agregan campos al esquema JSON de `inputs`. Las declaraciones se expresan mediante el contrato y los campos existentes del encargo. Una fuente externa necesita una representación accesible dentro del alcance autorizado; esta norma no concede acceso adicional.

Si la fuente no puede recuperarse o no sostiene la afirmación, el respaldo no se acredita: corresponde corregir la referencia, reformular o declarar un pendiente.

**Criterio:** asegurar reproducibilidad práctica sin inventar una protección mecánica por hash para cada entrada del request.

### D3. Pendientes bloqueantes según la promesa comprometida

**Alternativas consideradas:**

- Prohibir cualquier pendiente al aceptar.
- Permitir todos los pendientes si están visibles.
- Clasificarlos según su efecto sobre el contrato aprobado.

**Decisión:** adoptar la tercera alternativa.

Un pendiente **bloquea** cuando impide verificar una postcondición o un criterio de aceptación, por ejemplo:

- Falta el respaldo de un hecho necesario para el resultado comprometido.
- Una contradicción impide establecer el proceso que se prometió definir.
- Falta una decisión necesaria para delimitar el producto o proteger sus insumos.
- No se puede ejecutar una verificación comprometida.
- No se conoce todavía su impacto sobre una obligación del contrato.

Puede permanecer **no bloqueante** cuando:

- Está fuera del alcance comprometido; o
- El contrato promete identificar y presentar la incertidumbre, no resolverla.

Cada pendiente registra: cuestión, ubicación afectada, información o decisión necesaria para resolverlo, condición de cierre y clasificación justificada. Identifica al decisor/responsable cuando se conoce; en caso contrario declara que falta designarlo.

Una contradicción puede permanecer si la promesa es documentar posiciones divergentes. No puede permanecer sin resolver si se prometió entregar una definición operativa inequívoca que depende de ella.

El productor no rebaja unilateralmente una obligación a “no bloqueante”. Si se necesita renunciar a una promesa, se cambia el contrato mediante el procedimiento de aprobación vigente.

**Criterio:** permitir entregables honestos sin convertir la visibilidad de una carencia en sustituto de cumplimiento.

### D4. Integración mínima y fuente única

Se prefiere una referencia dentro de `cdad-cycle` frente a un skill nuevo porque ya existen distribución de referencias y obligaciones de rol por puntero.

Las fuentes de roles y los bloques estáticos de paquetes son superficies distintas: ambas deben transportar la obligación pertinente. Los agentes se regeneran; no se editan manualmente.

La aplicación es condicional: los criterios documentales se usan cuando el encargo tiene producto documental. La regla general **«quien produce no modifica su oráculo»** conserva también la separación vigente para código.

La selección del perfil documental y su combinación con Odoo permanecen en 010-002.

## 3. Contrato

### Promesa A — Los roles disponen de criterios documentales inequívocos

- **PC-01.** La referencia canónica define evidencia, propuesta, contradicción y pendiente con las distinciones de D1, sin exigir instancias ficticias ni secciones vacías.
- **PC-02.** Prescribe respaldo localizable para las afirmaciones factuales, identificación explícita de propuestas y conservación de contradicciones con sus fuentes.
- **PC-03.** Establece el localizador mínimo por tipo de fuente de D2 y el tratamiento de fuentes inaccesibles, mutables o insuficientes.
- **PC-04.** Establece la clasificación de pendientes de D3, sus datos mínimos y la prohibición de aceptar una promesa incumplida mediante reclasificación unilateral.

**Verificación:** comprobaciones estructurales de presencia y revisión independiente del contenido normativo contra estas decisiones.

### Promesa B — El encargo separa producto, fuentes y oráculo

- **PC-05.** La norma exige que cada encargo documental identifique:
  1. Fuentes autorizadas.
  2. Producto editable, mediante rutas delimitadas.
  3. Verificadores e insumos de aceptación protegidos.
  4. Evidencia esperada y limitaciones de verificación.

- **PC-06.** Prescribe que fuentes, contrato de aceptación, verificadores y plantillas usadas como oráculo queden fuera del alcance editable de GREEN. Compartir la clasificación `docs` no los convierte en producto editable. Una superposición o ambigüedad requiere detener esa parte y corregir el encargo.

- **PC-07.** Declara la regla «quien produce no modifica su oráculo». Un cambio legítimo del oráculo vuelve al rol competente y, si altera el contrato, a aprobación; no se realiza desde GREEN para obtener un resultado favorable.

- **PC-08.** Las obligaciones por rol conservan estas fronteras:

| Rol | Obligación documental |
|---|---|
| Orquestador | Preparar las cuatro declaraciones de PC-05, delimitar los alcances y comprobar evidencia y pendientes en los gates existentes. |
| Architect | Especificar promesas documentales verificables, fuentes, límites y aceptación; devolver borradores sin escribir ni aprobar. |
| Test-writer | Derivar el verificador del contrato y de los insumos autorizados, no del documento producido que debe verificar; editar únicamente tests autorizados. |
| Implementer | Producir únicamente el producto documental expresamente autorizado; no editar fuentes, verificadores ni insumos protegidos. |
| Reviewer | Contrastar producto y contrato con las fuentes en sesión independiente y read-only; registrar hallazgos, límites y abstenciones. |
| Scribe | Conservar su función de Memory Bank; producir sus borradores desde evidencia, sin asumir la producción documental general ni aprobarla. |

La modificación del contrato del implementer sustituye la restricción exclusivamente nominal a “código” por producto de implementación autorizado —código o documentación expresamente encargada—, sin ampliar sus permisos por defecto.

**Verificación:** revisión de la norma y de las obligaciones publicadas en las fuentes y superficies distribuidas.

### Promesa C — Un verde estructural no se presenta como aceptación semántica

- **PC-09.** La norma separa dos registros:
  - **Control automático/estructural:** control ejecutado, resultado, alcance y limitaciones.
  - **Revisión semántica independiente:** afirmaciones y fuentes examinadas, resultado, hallazgos y limitaciones/abstenciones.

- **PC-10.** Declara que presencia de secciones, etiquetas, archivos o referencias resolubles no demuestra fidelidad, suficiencia ni verdad semántica. Tampoco acredita revisión semántica un recibo de transporte o aceptación estructural del paquete. Una obligación textual o un paquete no constituye un sandbox ni demuestra ausencia de escrituras transitorias.

- **PC-11.** Prescribe contrastar afirmaciones con sus fuentes, buscando respaldo insuficiente, contradicciones omitidas y referencias que existen pero no sostienen lo afirmado. La revisión declara su alcance real; no promete detección infalible.

- **PC-12.** Prescribe que la aceptación funcional corresponda al usuario/dueño que aprueba, con las verificaciones comprometidas realizadas y sin pendientes que impidan acreditar el contrato. Los pendientes admisibles permanecen visibles.

**Verificación:** revisión independiente de las obligaciones y de sus límites explícitos. Esta feature no sustituye el ensayo semántico del piloto.

### Promesa D — Los criterios llegan por las vías existentes sin ampliar autoridad

- **PC-13.** Existe una única casa normativa en `skills/cdad-cycle/references/documentary-contracts.md`, localizable desde la tabla de referencias de `skills/cdad-cycle/SKILL.md`. Los consumidores remiten a ella sin reproducir sus frases normativas. La unicidad se mide por frases normativas derivadas de la referencia, con espacios normalizados, sobre `skills/`, `sources/` y `agents/`, siguiendo el precedente de `tests/test_006_004_u3_principle_single_source.py`; la redacción de las obligaciones breves de rol no duplica esas frases.

- **PC-14.** Las seis fuentes de rol de PC-08 contienen su obligación y el puntero pertinente. Los cinco bloques de rol existentes en `skills/cdad-cycle/packets/roles/` transportan las obligaciones de los roles delegados. Los agentes generados y promovidos de ambos runtimes conservan esas obligaciones, incluidas sus variantes Odoo existentes.

- **PC-15.** La instalación aislada mediante el instalador existente distribuye la referencia y los consumidores con los bytes esperados. La generación continúa siendo reproducible y los bloques estáticos respetan el techo vigente.

- **PC-16.** El cambio no introduce nuevos agentes, skills, etapas, campos del request/estado, selector documental ni ampliaciones de permisos por defecto. Conserva las cargas de dominio y restricciones existentes.

**Verificación:** pruebas de artefactos públicos y procesos reales de generación, render e instalación aislada, más revisión del diff.

## 4. Invariantes

- **INV-01:** una sola definición normativa; consumidores por referencia.
- **INV-02:** quien produce no modifica su oráculo.
- **INV-03:** un encargo corresponde a un rol y una subfase; no acumula permisos.
- **INV-04:** architect y reviewer siguen read-only; el test-writer no deriva su oráculo del producto producido.
- **INV-05:** una propuesta, contradicción o ausencia de evidencia no se transforma silenciosamente en hecho.
- **INV-06:** estructura válida no equivale a fidelidad semántica ni a aceptación funcional.
- **INV-07:** las aprobaciones y la aceptación funcional permanecen en el usuario/dueño que aprueba; la materialización conserva el contrato vigente. El nombre concreto del aprobador de esta unidad queda únicamente en sus documentos de autoridad bajo `docs/`, no en la norma distribuible.
- **INV-08:** una obligación textual o un paquete no se presenta como sandbox ni como prueba de ausencia de escrituras transitorias.

## 5. Criterios de aceptación medibles

1. PC-01 a PC-16 tienen trazabilidad a comprobaciones automáticas o revisión independiente, identificando cuál corresponde.
2. Las cuatro categorías, los localizadores de D2 y las reglas de pendientes de D3 están presentes y no contienen decisiones contradictorias.
3. Las seis fuentes de rol y los cinco bloques existentes transportan sus obligaciones; sus punteros resuelven a la referencia distribuida.
4. Los artefactos generados/promovidos coinciden con sus fuentes mediante la vía canónica; dos generaciones equivalentes producen los mismos bytes.
5. La instalación en destinos aislados distribuye la referencia y los agentes previstos, sin usar la instalación global como sustituto de la corrección.
6. Los bloques estáticos cumplen el techo vigente, sin elevarlo para acomodar este cambio.
7. Las pruebas focalizadas y regresiones pertinentes pasan. La suite completa se ejecuta una vez por quien cierre la tarea, conforme a la política vigente.
8. La revisión independiente informa hallazgos y abstenciones; las discrepancias que impidan cumplir el contrato se resuelven antes de solicitar aceptación.
9. Pablo aprueba explícitamente spec y plan antes de implementación, y decide la aceptación funcional al cierre.

Las pruebas se agrupan por promesa observable. No se exige una prueba por postcondición ni una cuota de variantes equivalentes.

## 6. Exclusiones

- Selección o resolución del perfil documental y combinación documental/Odoo.
- Nuevos campos, esquemas, agentes o mecanismos de permisos.
- Validador universal de documentos o motor de verdad semántica.
- Protección mecánica individual por hash de todos los insumos.
- Ejecución del piloto o acreditación anticipada de sus resultados.
- Edición general de formatos binarios, corpus real de clientes o publicación externa.
- Sustitución del scribe, nuevas etapas o aprobación autónoma.

## 7. `deferred-hardening`

| Elemento no comprometido aquí | Motivo |
|---|---|
| Parser/linter general para cualquier formato documental | Esta feature publica el contrato compartido; no existe una promesa de interpretación automática universal. |
| Detección automática de verdad o contradicciones semánticas | No es acreditable mediante presencia estructural ni puntajes; se conserva la revisión independiente. |
| Protección mecánica adicional por insumo | Requeriría diseño de integración/esquema no autorizado aquí. La separación contractual sí queda comprometida. |
| Formatos binarios y captura genérica de fuentes externas | El alcance inicial es Markdown pequeño e insumos autorizados; no se necesita un sistema de ingestión general. |
| Cobertura exhaustiva, rendimiento y combinatoria sin consecuencia contractual | No protegen una promesa adicional de esta unidad. |

010-002 y 010-003 son unidades posteriores del plan aprobado, no mecanismos para posponer una obligación comprometida en esta spec.

## 8. Referencias verificadas

- Alcance, separación y autoridad: `docs/epics/epic-010-documentary-specialization/plan.md:15-37,41-69,79-106`.
- Brechas y preguntas: `docs/specs/010-001-documentary-contracts/discovery.md:39-96`.
- Criterio de diseño: `skills/cdad-cycle/references/design-principles.md:3-23`.
- Architect: `sources/roles/architect.md:68-94`.
- Implementer y frontera actual: `sources/roles/implementer.md:18-24,38-44`.
- Independencia del test-writer: `sources/roles/test-writer.md:18-24,38-40`.
- Convención de pruebas: `sources/roles/test-writer.md:66-92`.
- Reviewer: `sources/roles/reviewer.md:21-43,63-68`.
- Scribe: `sources/roles/scribe.md:15-33,37-42`.
- Orquestación y materialización: `sources/roles/orchestrator.md:118-153`.
- Alcances documentales y esquema existente: `skills/cdad-cycle/scripts/cdad_packet.py:1461-1474,1743-1764,1922-1928,2266-2276`.
- Composición y techo de paquetes: `skills/cdad-cycle/scripts/cdad_packet.py:1947-1994`.
- Recepción sin acreditación semántica: `skills/cdad-cycle/scripts/cdad_result.py:745-751`.
- Límites de comprobación por presencia: `scripts/cdad-doctrine-check.py:29-35`.
- Generación: `Makefile:1-23`; `scripts/cdad-generate.py:631-668`.
- Instalación y aislamiento del destino: `install.sh:327-347,1261-1286,1302-1307`.
- Precedente de verificación distribuida: `tests/test_006_004_u3_principle_single_source.py:17-37,47-81`.

## 9. Aprobación

Aprobada por Pablo el 2026-10-31 mediante el mandato HITL del 2026-10-30 delegado al orquestador (`docs/specs/010-004-packet-dispatch-ergonomics/owner-mandate-hitl-2026-10-30.md` §3), que cubre las aprobaciones de spec y plan de las features del epic-010 mientras implementen la descomposición y el alcance ya aprobados en `docs/epics/epic-010-documentary-specialization/plan.md`. Registro de la decisión, revisión independiente y observaciones no bloqueantes: `docs/specs/010-001-documentary-contracts/owner-approval-2026-10-31.md`.

Status: Approved by Pablo on 2026-10-31
