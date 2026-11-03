# Spec — 013-001-criterion-coherence

**Estado:** borrador revisado, pendiente de aprobación. Sustituye como propuesta al borrador materializado; esta revisión se entrega como texto, sin editar el repositorio.  
**Fecha:** 2026-11-02.  
**Autoridad:** contrato de unidad aprobado y decisiones transmitidas por el delegado del dueño en el paquete `013-001-criterion-coherence-architect-draft-002`.

## 1. Descripción funcional

### Recorrido del usuario

- **Actor:** quien coordina una feature y los roles que preparan, modifican y revisan sus tests.
- **Objetivo:** verificar lo comprometido sin acumular verificadores equivalentes ni retirar protecciones necesarias.
- **Punto de partida:** existen una spec aprobada, tests previos y las subfases AUDIT, POST-AUDIT, RED y revisión independiente.
- **Primer resultado útil:** un AUDIT distingue protección existente, protección faltante y cambios de verificadores que pueden aprobarse sin perder obligaciones.

La feature alinea las instrucciones recibidas por rutas legacy y por paquetes. Explicita la contribución respecto de la suite existente, incorpora la sustitución al mantenimiento ordinario y resuelve las contradicciones sobre presupuestos de propiedades y suite completa.

Un sustituto nuevo de **comportamiento vigente** se prepara en **POST-AUDIT**, no en RED. Su evidencia es ejecución verde más sensibilidad demostrada frente a un defecto contractual concreto, conservando el mapa de obligaciones y la revisión independiente.

El producto es la **norma operativa distribuida**, no una garantía de obediencia infalible de los agentes. Su aceptación combina controles estructurales con revisión semántica independiente.

## 2. Fuentes y autoridad

### Fuentes admitidas y snapshot

Se admite el repositorio dentro del alcance `repository-read` del paquete.

Snapshot inspeccionado: `ca9f6f9f79ed638f29a3c6a57c312b7496627f28`. El árbol tenía cambios ajenos en `docs/.cdad-state.json` y un discovery sin versionar; no se presenta como árbol limpio.

Las rutas abreviadas `references/`, `packets/` y `assets/` siguientes pertenecen a `skills/cdad-cycle/`.

| Fuente | Localizador y función |
|---|---|
| Contrato aprobado | `.cdad/packets/013-001-criterion-coherence-architect-draft-002/UNIT-CONTRACT.md`, secciones Unit y Shared |
| Decisiones para esta revisión | `REQUEST.json` del mismo paquete, campo `objective`; identificación y cuerpo validados canónicamente |
| Plan del epic | `docs/epics/epic-013-test-criterion/plan.md`, Alcance, Features, Contratos entre features, Evidencia y suite completa |
| Borrador revisado | `docs/specs/013-001-criterion-coherence/spec.md`, hash `65a48f9280eadb090966bc34615e9463be3f6e76657a65d81733bab5c493e1fa` |
| Review | `docs/specs/013-001-criterion-coherence/plan-review.md`, hallazgos 1–5 |
| Discovery | `docs/specs/013-test-criterion-suite-review/discovery.md`, §A, apartados 1–8, y §D |
| Addendum | `docs/specs/013-test-criterion-suite-review/discovery-research.md`, §(c).2 y §(e)–(f) |
| R2 | `sources/roles/test-writer.md:80-118`, selección, justificación y propiedades |
| R4 | `sources/roles/orchestrator.md:312-325`, gate y promociones |
| R7 y evidencia | `references/stage-3-tdd.md`, Counterweight, Test evidence policy y subfases |
| AUDIT, POST-AUDIT y RED | `references/handoff-prompts.md:171-210,285-406`; bloques de paquetes correspondientes |
| Plantilla de AUDIT | `assets/spec-template/test-audit.md`, selección, modificados, nuevos e intactos |
| Propiedades | `references/handoff-prompts.md:478-503`; `references/re-entry.md:337-345`; `skills/odoo-test-writer/SKILL.md:141-147`; `skills/odoo-make-env/references/run-budget-protocol.md`, propiedades |
| Política anterior | ADR-020, decisión 1; `references/stage-5-merge.md`; `skills/cdad-epic/SKILL.md:119`; `skills/cdad-epic/references/epic-integration.md:76,109-115` |
| Gate mecanizado | `scripts/cdad-ci-gate.py:302-314`; `docs/ci-gate.md`, Qué corre y Costo; ADR-039, decisiones 1 y 6 y Consecuencias |
| Especialización Odoo | `skills/odoo-make-env/SKILL.md`, contrato y reglas; `references/run-budget-protocol.md`; `skills/odoo-test-writer/SKILL.md:120-147`; `skills/odoo-reviewer/SKILL.md:80-103`; deltas Odoo de implementer y reviewer |
| Índice y resúmenes de decisiones | `docs/systemPatterns.md`, Decisiones vigentes y resúmenes de políticas de evidencia |

### Evidencia, contradicciones y decisiones

1. **Suite completa.** El plan aprobado exige autorización expresa y evidencia focal por defecto. La norma vigente exige suite completa al cierre. Esta feature cambia esa norma; no interpreta ambos textos como compatibles.
2. **Gate de CI.** La herramienta invoca `close --all`. La decisión transmitida establece que **solo se ejecuta cuando se autoriza**. No se convierte en cierre obligatorio ni en disparador automático por push.
3. **ADR-020 y ADR-039.** ADR-020 está aceptado. ADR-039 se declara `Proposed`, con aplicación local descrita y extensión al push pendiente; no aparece en la tabla actual de decisiones vigentes. Debe registrarse la relación con ambos sin atribuir a ADR-039 una ratificación que no consta.
4. **Instalación limpia de addon.** Sigue vigente como evidencia específica aplicable. No se confunde con ejecutar todos los tests del proyecto.
5. **Propiedades.** Hay cuotas incompatibles: 100–1000, mínimo 100 y valores Odoo 8–10. Se propone sustituirlas por presupuesto declarado y justificado.
6. **Skill auxiliar.** `cdad-spec-and-test` **no se retira**. Se corrigen sus prescripciones incompatibles, manteniendo existencia, cargas e instalación.

Las recomendaciones del addendum no sustituyen decisiones del dueño. No se vuelven a acreditar sus fuentes externas.

## 3. Contrato

### Promesas observables

| Promesa | Resultado | Postcondiciones |
|---|---|---|
| A — Selección por contribución | AUDIT distingue protección existente y faltante | PC-1–PC-3 |
| B — Mantenimiento acreditable | Cada test recibe una disposición y las sustituciones conservan obligaciones | PC-4–PC-7 |
| C — Instrucciones coherentes | Legacy y paquetes transmiten el mismo criterio aplicable | PC-8–PC-9 |
| D — Propiedades presupuestadas | Presupuesto explícito y reproducible, sin cuotas rivales | PC-10–PC-11 |
| E — Evidencia proporcional autorizada | El cierre no exige una suite completa no autorizada y conserva la evidencia específica de addon | PC-12–PC-14 |

### A. Selección por contribución

**PC-1.** Antes de proponer tests nuevos, AUDIT identifica mediante referencias recuperables los verificadores existentes relevantes y contrasta qué postcondiciones protegen.

La falta de acreditación se declara; no se presenta automáticamente como ausencia de protección.

**PC-2.** Cada incorporación o extensión propuesta declara qué protección falta respecto de los verificadores considerados. La consecuencia «sin este test, el usuario…» expresa esa diferencia, no únicamente el riesgo genérico de la capacidad.

Si no se identifica una diferencia, el informe registra reutilización o incertidumbre. No prescribe otro test equivalente por defecto.

**PC-3.** La selección permite que un test proteja varias postcondiciones y que una promesa necesite varios tests cuando haya comportamientos comprometidos distintos.

Postcondiciones, simetrías, cobertura y variantes no constituyen cuotas. Se conservan las promociones justificadas cuyo procedimiento pertenece a R4.

### B. Mantenimiento acreditable

**PC-4.** Todo test incluido en el AUDIT —existente o propuesto— recibe **exactamente una** disposición:

| Disposición | Significado |
|---|---|
| **Mantener** | Conservar exactamente el verificador existente; puede reutilizarse como protección acreditada |
| **Extender** | Modificar un verificador existente para cubrir una protección faltante identificada |
| **Sustituir** | Reemplazar un verificador por otro u otros que conservan sus obligaciones vigentes |
| **Consolidar** | Reunir las protecciones de varios verificadores en un recorrido sustituto, conservando sus obligaciones |
| **Añadir** | Crear un verificador para protección faltante; no es el mero destino de una sustitución |
| **Retirar** | Eliminar un verificador porque la spec aprobada elimina la obligación que protegía |

Una obligación que sigue vigente no permite usar **Retirar** como atajo: corresponde acreditar su conservación mediante sustitución o consolidación.

La disposición se relaciona con las secciones existentes de la plantilla así:

| Sección de `test-audit.md` | Relación |
|---|---|
| **Test selection by promise** | Registro único por test: disposición, promesa, postcondiciones y contribución; referencias a operaciones de sustitución cuando correspondan |
| **Modified tests** | Tests existentes cuyo contenido o existencia cambia: Extender, Sustituir, Consolidar o Retirar |
| **New tests to write** | Tests físicamente nuevos: Añadir o destinos nuevos de Sustituir/Consolidar; estos últimos se identifican como POST-AUDIT |
| **Unchanged tests (untouched)** | Tests existentes que quedan exactamente intactos, con disposición Mantener; pueden ser destinos de conservación mediante referencia |
| **Regression Risk Assessment** | Obligaciones sin protección acreditada, incertidumbres y bloqueos |
| **Test Audit Gate** | Comprueba disposición única, justificación, destinos y aprobación del informe |

Un destino existente que permanece intacto sigue siendo **Mantener**; citarlo desde una sustitución no le añade otra disposición. Un destino nuevo o modificado que únicamente conserva obligaciones se registra como **Sustituir** o **Consolidar**, no como Añadir o Extender. Consolidar identifica la reunión de varios orígenes en un recorrido.

Las referencias entre secciones no duplican la disposición. Una operación que también introduce obligaciones nuevas debe distinguirlas expresamente; no puede ocultarlas bajo el recorrido de sustitución de comportamiento vigente.

Ante incertidumbre se conserva el test con disposición Mantener y se registra lo pendiente, sin certificar por ello su suficiencia.

Este vocabulario lo consumen 013-002 y 013-003 sin redefinirlo. No modifica por sí solo formatos o valores de inventarios existentes.

**PC-5.** Toda sustitución o consolidación identifica:

- verificadores de origen y destino;
- obligaciones comprometidas que permanecen vigentes;
- estados iniciales, acciones y efectos cuya diferencia pueda importar;
- ubicación de cada comprobación en el destino;
- evidencia de ejecución, sensibilidad y límites de la comparación.

Compartir resultado superficial, cobertura o menor duración no acredita equivalencia.

Retirar exige una referencia explícita a la eliminación de la obligación en la spec aprobada; no exige inventar un destino para una obligación que legítimamente desaparece.

**PC-6.** **POST-AUDIT** ejecuta los cambios aprobados de mantenimiento. Además de modificar tests existentes, puede crear un test físicamente nuevo **solo cuando sea un sustituto o consolidación de comportamiento vigente identificado en el AUDIT aprobado**.

Para ese sustituto:

1. No se exige RED ni se envía a RED por ser un archivo o test nuevo.
2. Se acredita ejecución **verde** sobre el comportamiento vigente.
3. Se demuestra **sensibilidad** mediante un control negativo autorizado que represente un defecto contractual concreto: debe observarse el fallo pertinente del verificador y atribuirlo a la protección declarada.
4. Se conserva el mapa de obligaciones de PC-5. Verde y sensibilidad no acreditan por sí solos equivalencia universal.
5. No se retiran los originales hasta disponer del destino ejecutable y de esa evidencia.
6. Si la sensibilidad no puede demostrarse dentro del alcance autorizado, se informa el bloqueo y se mantienen los originales.

No cuentan como sensibilidad un error de importación, fallo de preparación, aserción arbitrariamente falseada o control que no alcance el recorrido relevante. No se exige una herramienta de mutación ni se autoriza al test-writer a leer o modificar implementación.

POST-AUDIT conserva exactamente los tests declarados intactos y separa sus resultados de los de tests modificados y sustitutos.

La secuencia operativa queda reconciliada:

- **Mantenimiento de comportamiento vigente:** AUDIT aprobado → POST-AUDIT, incluidos sustitutos y retiros acreditados → revisión independiente. No se despacha GREEN si no hay implementación que cambiar.
- **Comportamiento pendiente:** AUDIT aprobado → POST-AUDIT cuando corresponda → RED separado → GREEN separado → revisión.
- Un mantenimiento posterior se despacha como otro POST-AUDIT aislado y aprobado; no queda implícito dentro de RED o GREEN.

Las instrucciones dejan de afirmar universalmente «todo test nuevo pertenece a RED» y «siempre hay tres despachos». RED conserva su fallo por la razón correcta para el comportamiento pendiente; no se fuerza un rojo artificial para comportamiento vigente.

**PC-7.** La revisión independiente contrasta las disposiciones, el mapa de conservación y la evidencia antes de aceptar la sustitución.

Puede concluir **Mantener** cuando no esté acreditada. El informe conserva la genealogía de las obligaciones y no declara acreditada toda la suite a partir de un lote.

### C. Instrucciones coherentes

**PC-8.** AUDIT, POST-AUDIT, RED y re-entry seleccionan por promesa y protección pendiente. No convierten una postcondición en obligación de crear un test nuevo ni condicionan el avance a una correspondencia numérica entre ambos.

Pre-RED busca en tests, contratos y entradas autorizadas. No ordena importar o inspeccionar implementación para descubrir qué debe verificar el test-writer.

Las instrucciones distinguen el sustituto de comportamiento vigente de PC-6 del test para comportamiento pendiente.

**PC-9.** Fuentes de roles, referencias, plantillas, bloques de paquetes y agentes regenerados transmiten un criterio compatible:

- R2 conserva el hogar de selección y justificación.
- R4 conserva el procedimiento de promociones.
- R7 conserva la aceptación sin pérdida de garantías.
- Los consumidores aplican o referencian esos hogares sin doctrinas paralelas.

`cdad-spec-and-test` permanece disponible y cargable. Deja de declarar una duración inferior a 30 segundos como condición universal de utilidad y de presentar verde→merge o sus gates/formato propios como sustitutos del ciclo vigente.

Una referencia no concede permiso de lectura. Si una instrucción necesaria no está accesible dentro del encargo, se informa la insuficiencia en vez de ampliar el alcance.

### D. Propiedades presupuestadas

**PC-10.** La norma genérica establece un presupuesto finito y positivo declarado antes de cada campaña de propiedades. Su justificación considera el invariante, dominio y coste del recorrido.

No impone mínimos o máximos universales de entradas ni permite cuotas rivales en especializaciones.

Las variantes contractuales obligatorias permanecen verificadas; no se sustituyen por la expectativa de que el muestreo las alcance.

**PC-11.** La evidencia permite recuperar:

- invariante;
- presupuesto declarado y cantidad realmente ejecutada;
- semilla;
- versión y configuración relevante del generador;
- contraejemplo pertinente cuando falle.

Cambiar el presupuesto exige justificar la calibración y comprobar que no elimina obligaciones comprometidas. Aumentarlo no pertenece automáticamente a hardening cuando es necesario para verificar el compromiso actual.

### E. Evidencia proporcional autorizada

**PC-12.** `stage-3-tdd.md`, sección **Test evidence policy**, sigue siendo el único hogar canónico de la política y establece:

- evidencia focal y regresión proporcional al cambio;
- suite completa únicamente con autorización expresa del dueño, también en cierre de feature, integración de sesiones, merge, integración de epic o cambios transversales;
- comandos concretos declarados por el proyecto;
- reutilización de evidencia conforme al hogar existente de equivalencia;
- condiciones locales registradas como datos, no como requisitos nuevos.

Autorizar una modificación, cerrar una tarea o disponer de un comando no autoriza por sí solo toda la suite.

**Instalación limpia de addon:** se mantiene la obligación aplicable de demostrar instalación desde cero mediante `test-clean` o el mecanismo equivalente ya declarado por el proyecto. Su evidencia incluye la verificación pertinente del addon; una corrida caliente no la sustituye.

La instalación limpia y la amplitud de la selección son dimensiones distintas. No se ejecuta toda la suite del proyecto por inferencia del nombre `test-clean` o `test-all`.

Si el runner disponible une inseparablemente la instalación limpia requerida con una suite completa no autorizada, se informa el bloqueo y se solicita autorización o resolución del entorno. No se omite silenciosamente la instalación ni se inventan flags o targets.

Los encargos sin cambios de addon no adquieren obligaciones de instalación por el dominio del proyecto.

**PC-13.** Los consumidores enumerados en §5 dejan de exigir una suite completa por defecto, por cierre o por push. Los gates mantienen evidencia empírica de todas las promesas comprometidas.

En particular:

- `packets/common.md` remite al hogar canónico y deja de ordenar que quien cierra ejecute siempre la suite completa.
- `scripts/cdad-ci-gate.py` es una **herramienta de corrida completa** que solo se invoca con autorización expresa suficiente para esa corrida.
- Una invocación autorizada del gate mantiene su recorrido `close --all` y su exigencia de verde atribuible. No se convierte en un gate focal ni se presenta su omisión como resultado verde.
- Esta unidad no crea un workflow, disparador por push, autorización implícita ni opción CLI nueva.

Sin autorización se registra **suite completa no realizada**, junto con selección efectivamente ejecutada y límites. Nunca se declara «suite completa verde» ni «gate de CI verde» sin evidencia correspondiente.

Si la evidencia autorizada no basta para una obligación comprometida, esa parte se bloquea y se solicita la decisión necesaria.

**PC-14.** La decisión posterior queda registrada mediante los responsables y mecanismos existentes, con estas relaciones explícitas:

- **ADR-020:** se sustituye su exigencia de suite completa automática al cierre o por superficies transversales. Se mantienen el hogar canónico, regresión proporcional, equivalencia y declaración de comandos por proyecto.
- **ADR-039:** su recorrido y atribución se conservan para invocaciones autorizadas. Su aplicación local descrita y la propuesta de corrida en cada push no hacen obligatoria la herramienta en todos los cierres ni la autorizan automáticamente.
- **Odoo:** se conserva la evidencia específica de instalación limpia y se elimina su confusión con una suite completa incondicional.

Se preservan los antecedentes históricos, indicando qué parte recibe una decisión posterior. Registrar esta relación no ratifica por sí solo todo ADR-039 ni reescribe specs cerradas.

`docs/systemPatterns.md` actualiza sus resúmenes y el índice correspondiente a la decisión efectivamente aprobada. No se inventa una vigencia previa de ADR-039.

### Firma o interfaz

No se incorpora API, comando, campo JSON, rol, subfase ni gate nuevo.

Se amplía el contenido admitido de **POST-AUDIT** y del informe `test-audit.md`. Se emplean los mecanismos existentes de generación y render de paquetes.

La autorización de corridas se transmite mediante la autoridad y los encargos existentes; no se añade un sistema automático de permisos.

## 4. Invariantes verificables

1. **Conservación:** toda obligación vigente de un test sustituido tiene destino acreditado; una referencia nominal no basta.
2. **Disposición única:** cada test del AUDIT recibe una sola disposición; las referencias entre operaciones no crean otra.
3. **Aislamiento:** el test-writer no deriva su oráculo leyendo implementación.
4. **Responsabilidad:** GREEN no modifica tests ni entradas protegidas de aceptación; architect y reviewer no aprueban su propio producto.
5. **Autoridad:** incertidumbre de verificación no se convierte en éxito ni autoriza una suite completa.
6. **Instalación:** la política de autorización no elimina evidencia aplicable de instalación limpia de addon.
7. **Derivación:** los agentes se regeneran desde fuentes; no se corrigen manualmente.
8. **Alcance:** esta unidad no elimina tests del piloto ni acredita redundancias de toda la suite.

Son invariantes de la norma y su distribución. Su presencia textual no demuestra fidelidad semántica ni conducta infalible de agentes.

## 5. Superficies afectadas

Las rutas abreviadas conservan el significado indicado en §2. Esta tabla identifica consumidores concretos; no concede por sí misma alcance de escritura a un despacho.

| Superficie | Cambio o comprobación exigida |
|---|---|
| `sources/roles/test-writer.md` | Contribución respecto de lo existente; disposiciones; POST-AUDIT para sustitutos vigentes; presupuesto de propiedades |
| `sources/roles/orchestrator.md` | Aplicación en AUDIT y re-entry; secuencias diferenciadas; conservar procedimiento de promociones |
| `sources/roles/implementer.md` | Retirar mandato `FULL suite` tras implementar; alinear delta Odoo sin eliminar instalación limpia |
| `sources/roles/reviewer.md` | Contraste independiente de conservación; distinguir `test-clean` de suite completa |
| `references/stage-3-tdd.md` | Hogar de evidencia; mantenimiento; recorrido POST-AUDIT; propiedades; integración paralela y gate E3→E4 |
| `references/handoff-prompts.md` | AUDIT, POST-AUDIT, RED, notas de secuencia, GREEN, propiedades y selección por promesa |
| `references/re-entry.md` | Validación de mantenimiento y sustitutos; avance por promesa; evidencia y presupuestos, conservando hogar de equivalencia |
| `skills/cdad-cycle/SKILL.md` | Resumen del ciclo, contratos y gates compatibles con ambos recorridos y la política autorizada |
| `references/anti-patterns.md` | Quitar suite completa automática de cierre; remitir a hogares existentes y distinguir control textual de suficiencia |
| `references/stage-4-review.md` | Revisión y re-ejecución proporcional; conservar independencia y reutilización de evidencia |
| `references/stage-5-merge.md` | Cierre, CI y comprobación tras merge conforme a autorización; no exigir suite completa por cerrar o fusionar |
| `packets/common.md` | Referencia al hogar canónico; eliminar mandato incondicional al responsable del cierre |
| `packets/roles/test-writer.md` | Mantener aislamiento y distinguir evidencia RED de sustitución vigente |
| `packets/roles/implementer.md` | Referencia compatible a evidencia proporcional y autorización |
| `packets/substages/test-writer-audit.md` | Disposiciones, contribución y operaciones aprobables |
| `packets/substages/test-writer-post-audit.md` | Admitir sustitutos nuevos aprobados; verde y sensibilidad antes del retiro |
| `packets/substages/test-writer-red.md` | Promesa pendiente, sin cuota por postcondición ni envío de sustitutos vigentes a RED |
| `packets/substages/test-writer-properties.md` | Presupuesto declarado y evidencia reproducible por referencia a R2 |
| `packets/substages/implementer-green.md`, `implementer-refactor.md`, `implementer-review-fix.md` | Mantener referencias compatibles, sin introducir obligación completa |
| `assets/spec-template/test-audit.md` | Disposición única, relación con secciones, contribución, destinos y obligaciones |
| `assets/feature-plan-template.md` | Corregir `validation_strategy` que prescribe suite completa al cierre |
| `skills/cdad-epic/SKILL.md` | Corregir gate de suite completa incondicional |
| `skills/cdad-epic/references/epic-integration.md` | Corregir exigencias de suite completa tanto intermedias como de salida |
| `skills/odoo-make-env/SKILL.md` | Alinear usos de `test`, `test-clean`, `test-all` y presupuesto; conservar semántica de instalación desde cero |
| `skills/odoo-make-env/references/run-budget-protocol.md` | Quitar corridas completas automáticas en cierre/review/fix; conservar anti-loop e instalación limpia; alinear propiedades |
| `skills/odoo-test-writer/SKILL.md` | Alinear AUDIT, instalación, recorridos RED/POST-AUDIT y propiedades |
| `skills/odoo-reviewer/SKILL.md` | Conservar evidencia de instalación limpia sin convertirla en autorización de toda la suite |
| `skills/cdad-spec-and-test/SKILL.md` | Corrección mínima de duración, formato y gates contradictorios; sin retirada |
| `scripts/cdad-ci-gate.py` | Mantener recorrido completo y atribución; alinear su documentación de uso con invocación autorizada, sin nuevo selector ni cambio de contrato funcional |
| `docs/ci-gate.md` | Explicar autorización previa, coste y ausencia de obligatoriedad automática por push/cierre |
| ADR-020 y ADR-039 en `docs/adr/` | Registrar relación con decisión posterior, preservando antecedentes y estado real |
| `docs/systemPatterns.md` | Reconciliar resúmenes operativos e índice de decisiones mediante su responsable |
| `scripts/cdad-doctrine-check.py` | Solo ajustes estructurales justificados, si hacen falta; no juez automático de equivalencia |
| `agents/` y `build/` | Exclusivamente regeneración |

Los cambios en verificadores pertenecen al test-writer. Aprobaciones, decisiones y Memory Bank conservan sus responsables actuales.

No se modifica el contrato funcional cerrado de `cdad-ci-gate.py`, ni las specs cerradas 008-002 y 008-006. Los paquetes históricos publicados no se reescriben retrospectivamente; se cambian sus fuentes para futuras emisiones.

## 6. Verificación y aceptación

### Entradas protegidas

La spec aprobada, contrato de unidad y plan aprobado son entradas de aceptación. GREEN no los modifica ni cambia verificadores para obtener verde.

El test-writer recibe contrato y entradas autorizadas suficientes para construir su oráculo. La tabla de superficies no le autoriza a leer el producto normativo bajo verificación.

Esta unidad modifica metodología, no un addon. No exige inventario core/OCA ni entorno de instalación de un addon que no modifica.

### Evidencia requerida

**Control estructural o automático**

- AUDIT identifica protección existente, diferencias y expectativas históricas que deben cambiar.
- Verificadores focales cubren las promesas estructurales y de distribución comprometidas.
- La plantilla permite clasificar sin duplicidad los seis tipos de disposición y distinguir test nuevo de disposición Añadir.
- Se comprueba que legacy y paquetes transmiten el recorrido de sustitución de PC-6, sin un mandato contradictorio de RED.
- Se regeneran agentes mediante `make agents`, sin edición manual.
- Se renderizan y validan canónicamente paquetes relevantes.
- Se aplica regresión proporcional de generación, paquetes, política y superficies afectadas.
- Se conservan comando, selección, revisión, configuración, salida y código de retorno.

Comprobar el contrato conservado del gate mediante verificadores focales no autoriza ejecutar el gate real sobre toda la suite.

**Revisión semántica independiente**

Contrasta las superficies contra PC-1–PC-14, especialmente:

- cuotas indirectas por postcondición;
- consecuencias genéricas sin contribución diferencial;
- tests sin disposición o con disposiciones incompatibles;
- sustitutos sin destino ejecutable, sensibilidad o conservación acreditada;
- instrucciones que aún obliguen a llevar sustitutos vigentes a RED;
- lecturas de implementación disfrazadas de búsqueda;
- presupuestos rivales;
- cierres o pushes que todavía impongan suite completa;
- supresión accidental de instalación limpia de addon;
- uso del gate completo sin autorización;
- relaciones incompletas o estados inventados respecto de ADR-020 y ADR-039.

Declara fuentes, hallazgos, límites y abstenciones. Un validador textual no sustituye este contraste.

### Criterio de aceptación

La feature es aceptable cuando:

1. Todas sus postcondiciones tienen evidencia pertinente y revisión independiente.
2. No quedan contradicciones operativas que impidan aplicar sus recorridos.
3. Fuentes, distribución regenerada y paquetes relevantes son compatibles.
4. Cada consumidor enumerado tiene resultado registrado: cambio realizado o comprobación fundada de compatibilidad.
5. Las obligaciones históricas modificadas tienen una decisión posterior trazable.
6. El cierre distingue evidencia focal, instalación limpia cuando aplique y suite completa autorizada o no realizada.
7. El dueño aprueba el resultado.

No se exige `cdad-suite.py validate rc=0` como resultado de esta unidad: reparar el inventario pertenece a 013-002. Tampoco se exige reducción de tests, bytes o minutos.

## 7. Decisiones de diseño

- **Criterio general frente a excepciones por feature:** aplicar R2/R4/R7 a protección existente evita reglas por prefijo y clasificadores nuevos. El criterio es conservar obligaciones, no disminuir un contador.
- **POST-AUDIT frente a RED artificial o subfase nueva:** el mantenimiento de comportamiento vigente no necesita implementación pendiente. Ampliar POST-AUDIT conserva roles y exige evidencia adecuada: verde y sensibilidad, no un rojo fingido.
- **Disposición frente a ubicación física:** un test nuevo puede ser sustituto, y un test intacto puede conservar obligaciones de otro. Separar decisión de sección evita que «nuevo» determine automáticamente RED.
- **Presupuesto declarado frente a cuota universal:** permite calibrar coste sin confundir muestra con suficiencia contractual.
- **Corregir frente a retirar la skill auxiliar:** respeta el aplazamiento aprobado y elimina contradicciones actuales.
- **Autorizar la invocación frente a rediseñar el gate:** conserva el contrato completo y atribuible de la herramienta; la decisión pendiente es cuándo usarla, no convertirla en otro runner.
- **Instalación limpia frente a batería indiscriminada:** conserva la garantía específica del addon sin inferir permiso para ejecutar toda la suite.

## 8. deferred-hardening

- **Acreditación semántica exhaustiva de la suite:** fuera del compromiso; esta unidad define el criterio.
- **Poda y mutación del piloto:** corresponden a 013-003. La sensibilidad exigida a un sustituto no impone una herramienta ni campaña universal de mutación.
- **Rendimiento, fixtures, paralelismo y selección dinámica:** requieren medición y decisión posterior; no prueban pertinencia.
- **Detector automático de equivalencias:** no acredita conservación semántica y no resulta necesario.
- **Retirada de `cdad-spec-and-test`:** aplazada expresamente.
- **Nuevo workflow, selector o permiso automático para el gate:** no necesario para distinguir herramienta disponible de ejecución autorizada.
- **Prueba universal de obediencia de agentes:** no se promete; se verifica norma distribuida y revisión independiente.

Ninguna exclusión permite diferir una postcondición de esta spec.

Status: Approved by Pablo (HITL delegado, docs/epics/epic-013-test-criterion/execution.md) on 2026-11-02
