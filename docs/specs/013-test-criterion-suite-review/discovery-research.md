# Addendum de investigación — 013-test-criterion-suite-review

**Borrador para decisión del dueño. No es una spec ni aprueba el epic.**

**Convención:** **[F]** identifica evidencia verificada y citada; **[R]** identifica interpretación o recomendación propia. Los identificadores S1–S19 remiten a las fuentes de la sección **(b)**.

**Alcance:** investigación externa e inspección de las fuentes del repositorio. Se leyó completa `docs/research/testing-practices-2026-10-25.md`. Este addendum amplía y corrige sus recomendaciones; no reproduce su catálogo.

**Revisión local:** `211e3d170ff23be5cd49519f1840d1d915f5c889`. Las mediciones reutilizadas proceden del Discovery, realizado en `0eab565c0f262a3411489c5a822466c86d1ed8e8`; **no son nuevas mediciones sobre HEAD**. Rutas relativas al repositorio anidado `cdad/`.

---

## (a) Resumen ejecutivo

**[R] El problema merece un epic, pero no una nueva plataforma de testing.** La prioridad es cerrar el circuito entre generación y mantenimiento: buscar la protección existente antes de añadir tests, acreditar su contribución y permitir sustituir redundancias sin perder obligaciones. R2/R4/R7 ya contienen la base; faltan coherencia operativa y una disposición ordinaria de sustitución.

**[F] La literatura respalda desconfiar de tres equivalencias:** más tests no significa necesariamente mejor detección; igual cobertura no significa igual protección; igual resultado superficial no significa equivalencia de comportamientos. La reducción basada en mutantes conserva mejor la detección que la basada en cobertura en el experimento de Chen et al., pero no ofrece garantía universal. Los resultados recientes sobre tests generados por LLM refuerzan la dependencia del contexto y del oráculo utilizado [S3, S4, S8].

**[R] Recomiendo empezar por lo simple:** criterio coherente → inventario actualizado → mapa suficiente del lote → poda piloto con sustitutos y revisión independiente. No hace falta acreditar semánticamente los 1937 tests antes de obtener una mejora acotada.

**[R] La mutación puede aportar evidencia objetiva de sensibilidad conservada, no demostrar por sí sola «garantía conservada».** Debe complementar el mapa de obligaciones. Para una poda que solo cambia tests, mutar exclusivamente «líneas de producto cambiadas» produce un ámbito vacío: hay que fijar previamente una porción de producto y el mismo conjunto de mutantes antes y después. Comparar únicamente porcentajes tampoco basta; pueden ocultar la pérdida de mutantes antes detectados.

**[F] Coverage.py no tiene una imposibilidad general con subprocesos.** Su documentación contempla `patch = subprocess`, datos paralelos y combinación. Siguen pendientes la atribución por test, la propagación de configuración y las terminaciones abruptas. Además, testmon declara que no sigue cambios de archivos estáticos: una limitación especialmente relevante para CDAD, cuyo producto incluye instrucciones Markdown y plantillas [S12, S13].

**[R] No recomiendo reescribir masivamente la suite para ejecutar todo en proceso.** Esa opción puede abaratar determinadas verificaciones, pero también dejar de comprobar arranque, entorno, rutas, señales y efectos del proceso real. Debe justificarse por superficie y medición, no adoptarse para acomodar una herramienta.

**[R] Recomiendo fusionar el contenido útil de `cdad-spec-and-test` en los hogares existentes y retirar después la skill autónoma.** La afirmación del orquestador es sustancialmente correcta, pero incompleta: paquetes v2 no la carga; legacy sí la exige, también en variantes generadas, y dos módulos de tests protegen literalmente esa carga. Retirarla requiere migrar fuentes, expectativas, generación e instalación, no borrar un directorio.

**[R] Mantengo las cuatro features propuestas**, con dos ajustes: 013-001 incluye esa migración y la resolución del presupuesto de propiedades; 013-004 empieza por medición y optimización mecánica, dejando el paralelismo condicionado a necesidad y seguridad demostradas.

**Límites:** no se ejecutaron nuevos tests, suite completa, `make validate` ni instalador. No hay ahorro acreditado, proporción global de redundancias ni viabilidad local medida de mutación, testmon o xdist.

---

## (b) Fuentes, calidad y aplicabilidad

Consulta externa realizada el **2 de noviembre de 2026**. Las citas siguientes identifican el contenido utilizado, no solo páginas que mencionan el tema.

### Evidencia empírica y experiencia de ingeniería

| ID | Fuente y contenido verificado [F] | Calidad, contexto y límite para CDAD |
|---|---|---|
| **S1** | Google, *Software Engineering at Google*, [cap. 11](https://abseil.io/resources/swe-book/html/ch11.html) y [cap. 12](https://abseil.io/resources/swe-book/html/ch12.html): tamaño frente a alcance; estabilidad ante refactor; cobertura como información incompleta; legibilidad y tests sin lógica innecesaria. | Experiencia primaria de ingeniería a gran escala. Fundamenta criterios, no demuestra qué tests concretos sobran aquí. Sus proporciones orientativas no son cuotas transferibles. |
| **S2** | Google, [*Change-Detector Tests Considered Harmful*](https://testing.googleblog.com/2015/01/testing-on-toilet-change-detector-tests.html) y [*Code Coverage Best Practices*](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html): copiar información de la implementación puede generar tests que solo detectan cambios; cobertura no acredita calidad suficiente. | Consejos primarios de practicantes, no experimentos controlados. Aplicables al riesgo de congelar detalles, pero no justifican eliminar toda comprobación textual. |
| **S3** | Chen et al., ASE 2020, [*Revisiting the Relationship Between Fault Detection, Test Adequacy Criteria, and Test Set Size*](https://homes.cs.washington.edu/~rjust/publ/mutants_faults_revisited_ase_2020.pdf), especialmente experimento de reducción y figura de p. 9: «most test sets reduced based on mutants maintain their fault-detection capability», frente a pérdida sustancial al reducir por cobertura. | Estudio empírico primario con fallas reales de Defects4J y tests de desarrolladores. Es la evidencia más directa encontrada para la poda. Java, no CLI Python ni tests escritos bajo aislamiento CDAD; «most» no significa «todos». |
| **S4** | Petrović et al., [*Practical Mutation Testing at Scale*](https://homes.cs.washington.edu/~rjust/publ/practical_mutation_testing_tse_2021.pdf), TSE: líneas cambiadas, supresión de mutantes improductivos, selección dirigida y **como máximo un mutante por línea**. [*Does mutation testing improve testing practices?*](https://arxiv.org/abs/2103.07189), ICSE 2021: análisis de casi 15 millones de mutantes y evidencia de acoplamiento con fallas reales. | Evidencia industrial primaria y amplia. Respalda viabilidad con reducción de ruido e infraestructura; no un gate universal de cero supervivientes ni su rentabilidad en CDAD. |
| **S5** | Meta, [*Automated Unit Test Improvement using Large Language Models*](https://arxiv.org/abs/2402.09171), FSE 2024: filtros de compilación, ejecución fiable y aumento de cobertura; aceptación de recomendaciones por ingenieros. | Despliegue industrial primario. Mejora tests humanos existentes y dispone de infraestructura propia. Aceptación y cobertura no equivalen a cumplimiento contractual. |
| **S6** | Meta, [*Mutation-Guided LLM-based Test Generation*](https://arxiv.org/abs/2501.12862), 2025: ACH genera pocos mutantes orientados a una preocupación; 9095 mutantes y 571 tests; aceptación del 73 % en sus test-a-thons. | Informe industrial primario sobre Kotlin/Android y preocupaciones de privacidad. Respalda orientar la generación a defectos concretos, no copiar sus resultados ni introducir otro agente aquí. |
| **S7** | Konstantinou et al., [*Can we find bugs using LLM-generated oracles?*](https://arxiv.org/html/2410.21136), versión v2, octubre de 2026: en sus sujetos Java los oráculos capturan principalmente comportamiento actual; los autores concluyen que las sugerencias requieren inspección humana. | Experimento controlado primario. Generación con información de implementación: difiere del test-writer CDAD, que no debe verla. La advertencia sobre el origen del oráculo sí resulta pertinente. |
| **S8** | Zhao et al., [*Do Coverage and Mutation Scores of LLM-Generated Test Suites Correlate with Their Effectiveness?*](https://arxiv.org/html/2607.22880v1), ISSTA 2026, §§4–8: utilidad dependiente del contexto; relaciones distintas entre comparación de modelos y comparación de suites dentro de un modelo; limitaciones con código de entrada defectuoso. | Replicación empírica primaria, Java/Defects4J, generación predominantemente de caja blanca. Impide tratar mutation score o cobertura como indicadores universales de valor para un test particular. |
| **S9** | Ouédraogo et al., [*On the Diffusion of Test Smells in LLM-Generated Unit Tests*](https://arxiv.org/abs/2410.10628), v3, aceptado en TOSEM en 2026: compara suites LLM, humanas y EvoSuite; encuentra smells persistentes y dependientes del contexto de generación. | Estudio primario amplio, pero sobre Java y detectores de smells. No mide la prevalencia ni el impacto de esos smells en CDAD. |
| **S10** | [SWT-Bench](https://arxiv.org/abs/2406.12952): tests generados por agentes para validar reparaciones reales. [*Predictive Test Selection*](https://arxiv.org/html/1810.05286): selección industrial en Facebook que reduce costo conservando gran parte de la detección, no toda. | Evidencia primaria de utilidad de generación y selección. Un benchmark de reparaciones y un sistema industrial predictivo no acreditan mantenimiento sostenible ni selección segura aquí. |
| **S11** | Parry et al., [*Test flimsiness: characterizing flakiness induced by mutation to the code under test*](https://eprints.whiterose.ac.uk/id/eprint/236716/), ICSE 2026: estudia inestabilidad que aparece al mutar el producto. | Evidencia empírica primaria. Advierte que el resultado de mutación también puede contaminarse con inestabilidad; no diagnostica flakiness local. |

### Documentación, estándares y criterios

| ID | Fuente y contenido verificado [F] | Calidad, contexto y límite para CDAD |
|---|---|---|
| **S12** | Coverage.py, [gestión de procesos](https://coverage.readthedocs.io/en/latest/subprocess.html); pytest-cov, [soporte de subprocesos](https://pytest-cov.readthedocs.io/en/latest/subprocess-support.html). Coverage requiere intervenir al inicio y final; pytest-cov 7 trasladó ese soporte a Coverage.py. | Documentación oficial: alta autoridad sobre funcionamiento previsto. No sustituye una prueba con los wrappers, entornos y terminaciones reales de CDAD. |
| **S13** | [testmon](https://www.testmon.org/) y [su implementación](https://raw.githubusercontent.com/tarpas/pytest-testmon/main/testmon/testmon_core.py): dependencias mediante Coverage.py, construcción previa de datos, coordinación con `COVERAGE_PROCESS_START`; declara que no sigue «static files» ni servicios externos. | Documentación y código primarios. La exclusión de archivos estáticos afecta directamente a Markdown, plantillas y otros insumos relevantes del repo. |
| **S14** | [mutmut, README](https://raw.githubusercontent.com/boxed/mutmut/main/README.rst): filtrado por cobertura, selección, profundidad de pila, ejecución con `fork`/`forkserver` y riesgos de estado heredado. [Cosmic Ray, tutorial](https://cosmic-ray.readthedocs.io/en/latest/tutorials/intro/index.html): código mutado, comando de tests, baseline y timeout. | Documentación oficial: acredita capacidades declaradas, no compatibilidad local. El mecanismo de ejecución importa especialmente cuando el test lanza otro intérprete. |
| **S15** | pytest-xdist, [how-to](https://pytest-xdist.readthedocs.io/en/stable/how-to.html): cada worker ejecuta sus fixtures de sesión; no existe garantía incorporada de ejecución única global; muestra coordinación mediante bloqueo. | Documentación oficial directamente aplicable a la evaluación de workers y staging compartido. No demuestra aceleración ni seguridad. |
| **S16** | Hypothesis, [referencia](https://hypothesis.readthedocs.io/en/latest/reference/api.html): generación, configuración y reproducibilidad. pytest, [flaky tests](https://docs.pytest.org/en/stable/explanation/flaky.html): estado no controlado, aislamiento y paralelismo como factores. | Documentación oficial. Los valores de configuración son controles operativos, no evidencia de suficiencia contractual. |
| **S17** | Jest, [snapshot testing](https://jestjs.io/docs/snapshot-testing): referencia almacenada, revisión de actualizaciones y determinismo. Fowler, [Contract Test](https://martinfowler.com/bliki/ContractTest.html): comprobar que el doble sigue representando al servicio. | Documentación oficial y criterio experto primario. Las ideas son transferibles; no hay motivo acreditado para incorporar Jest o infraestructura de microservicios. |
| **S18** | Beck/Sutton, [Test Desiderata](https://kentbeck.github.io/TestDesiderata/); [catálogo de test smells](https://testsmells.org/pages/testsmells.html): propiedades deseables y patrones como General Fixture, Assertion Roulette y Eager Test. | Criterios expertos y catálogo especializado. Útiles para inspección; un smell es señal para investigar, no sentencia de eliminación. |
| **S19** | Fichas oficiales IEC de ISO/IEC/IEEE 29119 [parte 2: procesos](https://webstore.iec.ch/en/publication/71833), [parte 3: documentación](https://webstore.iec.ch/en/publication/71834) y [parte 4: técnicas](https://webstore.iec.ch/en/publication/71836), ediciones 2021. | Se verificaron **metadatos y abstracts**, no el texto normativo completo. No se atribuyen a estas normas cuotas, umbrales de poda ni obligaciones detalladas no consultadas. |

### Método y carencias

**[F]** Se usaron búsqueda web, lectura de fuentes y Context7 para documentación de Coverage.py, xdist e Hypothesis. Algunos fetch fallaron: ISO devolvió 403 y el lector web no admitió determinados PDF. Los abstracts ISO se consultaron en IEC; los PDF utilizados se extrajeron con `pypdf` en memoria porque `pdftotext` no estaba disponible. No se instalaron herramientas.

**[F]** El entorno inspeccionado tenía Python 3.13.5, pytest 8.3.5, coverage 7.15.0 y pytest-cov 7.1.0. No estaban instalados pytest-testmon, pytest-xdist, Hypothesis, mutmut ni Cosmic Ray. Por tanto, las propuestas sobre ellos son evaluaciones documentales, **no pruebas locales**.

**[R]** La aceptación de este addendum debería contrastar las afirmaciones con las fuentes y comprobar que cada requerimiento y hallazgo recibe respuesta. No corresponde aceptarlo por presencia de secciones ni por mi propio veredicto.

---

## (c) Conocimiento por tema: consecuencias para generación y mantenimiento

### 1. Valor: contribución, no cantidad

**[F]** Google y Test Desiderata combinan detección, estabilidad ante cambios legítimos, velocidad, aislamiento y legibilidad. No reducen valor a duración o cobertura [S1, S18].

**[R]** Para CDAD conviene separar dos preguntas:

- **Pertinencia:** ¿qué promesa o promoción justificada sirve?
- **Contribución:** considerando los tests existentes, ¿qué protección adicional aporta?

Un test puede ser pertinente y redundante. La frase «sin este test, el usuario…» resulta insuficiente si describe el riesgo genérico de una capacidad que otros tests ya protegen.

**[R] Práctica recomendada:** reutilizar, extender, consolidar o añadir según la diferencia observable que falta. Registrar la decisión en el AUDIT existente.

**Ventaja:** frena acumulación sin imponer cuotas.  
**Costo/riesgo:** exige inspeccionar la protección existente; una descripción genérica puede aparentar una contribución inexistente.

### 2. Poda: preservar obligaciones y sensibilidad

**[F]** Chen et al. encontraron que la reducción preservando adecuación por mutación mantenía la detección de fallas en la mayoría de los conjuntos estudiados, mientras la reducción por cobertura sufría pérdidas sustanciales [S3].

**[R]** Esto respalda preferir evidencia de detección a igualdad de cobertura. **No respalda** eliminar automáticamente un test porque otro cubre sus líneas, porque es más lento o porque ambos terminan con el mismo exit code.

Para una sustitución acotada recomiendo:

1. Identificar obligaciones, estados previos y efectos protegidos.
2. Señalar el sustituto y dónde quedan verificadas esas protecciones.
3. Contrastar por separado preparación, acción y oráculo.
4. Obtener revisión independiente y evidencia de ejecución proporcional.
5. Añadir mutación solo cuando aporte información y sea viable.

**[R]** «Garantía conservada» debe significar conservación acreditada de las obligaciones comprometidas dentro del ámbito revisado, no promesa de detectar cualquier defecto futuro.

**Carencia:** no se encontró una regla empírica universal que permita certificar poda segura con un número, porcentaje o relación entre tamaños.

### 3. Mutación acotada: prometedora, pero con un ámbito correcto

**[F]** Google consigue utilidad limitando generación y ruido: líneas cambiadas, supresión de mutantes improductivos y selección dirigida. El propio estudio explica que algunos mutantes detectables inducirían tests de valor negativo, por fijar detalles de implementación [S4].

**[R]** Por ello, «cero mutantes vivos sin justificar» **no se deriva** como gate necesario de esa experiencia.

Hay dos usos distintos:

| Uso | Ámbito razonable [R] |
|---|---|
| Evaluar un cambio de producto | Código cambiado relevante para el contrato. |
| Evaluar poda de tests sin cambiar producto | Porción de producto protegida por el lote, fijada antes de podar. |

**[R]** Para el segundo uso, definir un conjunto fijo \(M\) de mutantes y comparar:

> Mutantes detectados antes ⊆ mutantes detectados después.

La comparación debe conservar producto, operadores, configuración, exclusiones y condiciones relevantes. **Igual mutation score no basta** si desaparecen unas detecciones y aparecen otras.

**Ventajas:** detecta pérdidas concretas que un mapa nominal o cobertura igual pueden ocultar.  
**Contras:** mutantes equivalentes o improductivos, costo de ejecución, fallos de infraestructura, inestabilidad y alcance limitado de los operadores.

**[R]** Timeouts o errores de infraestructura deben quedar distinguidos de una detección atribuible al oráculo. Una campaña inconclusa no acredita conservación.

**[R]** La mutación será inicialmente una medida experimental de **sensibilidad conservada**, complementaria a la revisión de obligaciones. No un gate general ni un reemplazo de R7.

### 4. Viabilidad por subproceso

**[F]** mutmut documenta ejecución de pytest y workers derivados mediante `fork` o `forkserver`; Cosmic Ray admite un comando de tests sobre el producto mutado [S14].

**[R]** Cuando el test arranca un intérprete nuevo, hay que demostrar que ese intérprete ejecuta el mutante y no otra copia del producto o un staging anterior. Esto es distinto de demostrar que se recogió cobertura.

**[R]** Un piloto autorizado debería comprobar primero un defecto canario con resultado observable conocido. Si no llega al proceso probado, no tiene sentido interpretar sus puntuaciones. La documentación hace de Cosmic Ray un candidato plausible para ese ensayo, **no una elección acreditada**.

**[R]** Tampoco debe enviarse implementación mutada al test-writer vulnerando su aislamiento. Un superviviente relevante puede traducirse, mediante el rol competente, en una diferencia conductual y un contrato suficiente para ese writer.

### 5. Test smells y consolidación

**[F]** Los catálogos y estudios de tests LLM encuentran problemas de legibilidad y mantenimiento, pero no convierten automáticamente cada patrón en un defecto funcional [S9, S18].

**[R]** Prioridades de inspección para CDAD:

- preparación general y costosa que muchos casos no necesitan;
- dependencias ocultas de HOME, rutas, cachés o estado;
- duplicación del mismo recorrido sin protección adicional;
- oráculos amplios difíciles de diagnosticar;
- lógica en el test que reconstruye la decisión del producto.

**[F]** Google favorece tests legibles y desaconseja lógica innecesaria; también acepta repetición que haga el test comprensible [S1].

**[R]** No propongo prohibiciones sintácticas absolutas de `if`/`for`, detectores nuevos ni un gate de smells. Consolidar hasta crear un test enorme puede empeorar diagnóstico y mantenimiento aunque reduzca nodeids.

### 6. Tests escritos por LLM y agentes

**[F]** TestGen-LLM filtra candidatos por mejoras comprobables; ACH orienta generación hacia fallas concretas. SWT-Bench muestra utilidad para validar reparaciones. Ninguno demuestra que cualquier test generado aporte valor marginal [S5, S6, S10].

**[F]** Los estudios de oráculos y métricas advierten que el comportamiento actual puede confundirse con el esperado y que los indicadores dependen del contexto [S7, S8].

**[R]** CDAD evita una vía de copia al impedir que el test-writer vea implementación. No elimina ambigüedad de la spec, repetición histórica ni sobreespecificación.

**[R]** La adaptación apropiada es reforzar el origen contractual del oráculo y la comparación con verificadores existentes, manteniendo auditoría independiente. No adoptar un ciclo automático de «generar hasta subir cobertura o matar todo».

### 7. Prosa, change-detectors y producto documental

**[F]** El change-detector de Google critica tests que replican información de implementación sin verificar un comportamiento independiente [S2]. CDAD, por su parte, exige separar control estructural y revisión semántica (`documentary-contracts.md:151-171`).

**[R]** Una cadena literal puede ser:

- un detalle accidental que no conviene congelar;
- una interfaz textual comprometida;
- contenido normativo que debe distribuirse fielmente.

La decisión depende del contrato, no del tipo `str`.

**[R]** Para CLI, conviene comprobar decisiones, estado, preservación y salida estructurada cuando esas superficies ya existan y estén comprometidas. No corresponde inventar una API JSON solo para facilitar tests.

**[R]** Para prosa normativa, presencia, distribución o igualdad de bytes pueden ser promesas válidas. No prueban que la regla sea suficiente, coherente o verdadera. Más sinónimos o ventanas de proximidad no resuelven ese límite.

### 8. Golden y snapshot

**[F]** Jest presenta snapshots como referencias revisables y exige atención al determinismo y a las actualizaciones [S17].

**[R]** Encajan en artefactos deliberadamente estables, siempre que se revise el diff y el productor no actualice su propio oráculo para obtener verde.

**Ventajas:** comparación completa y visible de una representación.  
**Riesgos:** aceptar regeneraciones mecánicamente, congelar detalles accidentales o normalizar precisamente los bytes cuya conservación importa.

**[R]** No recomiendo snapshots globales de toda la prosa. Deben reservarse para una promesa concreta de representación o distribución.

### 9. Contract testing

**[F]** Fowler usa contract tests para comprobar que un doble de un servicio continúa representándolo [S17].

**[R]** En CDAD hay dos asuntos que no deben confundirse:

- tests de promesas contractuales del producto, ya propios del ciclo;
- comprobación de fidelidad de dobles de adaptadores o herramientas externas.

El segundo puede aportar valor donde exista un doble y riesgo de divergencia. No reemplaza pruebas de comportamiento CLI ni revisión de instrucciones. No hay evidencia que justifique introducir infraestructura adicional de contratos.

### 10. Tamaño, perfiles rápidos y selección por impacto

**[F]** Google distingue recursos consumidos de alcance funcional. Un test que lanza procesos no se vuelve pequeño por tener pocas líneas [S1].

**[R]** Un perfil rápido útil combina costo con capacidad/obligación; «fast» por sí solo no informa qué deja fuera. Debe servir a iteración, sin sustituir la evidencia de cierre.

**[F]** Coverage.py puede medir subprocesos con configuración adicional y coordinación del guardado [S12]. testmon requiere datos previos y no sigue cambios de archivos estáticos ni servicios externos [S13].

**[R]** Hay que acreditar tres cosas separadas:

1. Se mide el proceso hijo correcto.
2. La ejecución queda asociada al test correcto.
3. Un cambio relevante selecciona el test que debe reaccionar.

Un informe combinado de cobertura solo responde parcialmente a la primera.

**[R]** Para CDAD, selección explícita por capacidades y dependencias declaradas es el punto de partida más sencillo. testmon podría complementar Python, pero no debería excluir silenciosamente tests afectados por Markdown, plantillas, shell o staging.

**[R]** La migración a invocación en proceso es una alternativa posterior, únicamente para superficies públicas verificadas y conservando pruebas de las diferencias propias del proceso. Su superioridad económica no está medida.

### 11. Paralelismo y fixtures compartidas

**[F]** xdist ejecuta fixtures de sesión por worker; compartir su resultado requiere coordinación explícita. Sus documentos muestran una técnica con bloqueo [S15].

**[R]** Para CDAD, evaluar por separado:

- staging inmutable compartido y copiado por test;
- estado mutable exclusivo del test o worker;
- recursos que deban permanecer seriales.

**Ventaja:** puede reducir espera sin eliminar garantías.  
**Riesgos:** multiplicar generación por worker, introducir carreras, heredar estado y aumentar presión de CPU/I/O.

**[R]** Compartir preparación no es válido si evita precisamente la transición cuya corrección se prueba. El aislamiento existente es una base, no una certificación de seguridad paralela.

### 12. Flakiness y presupuestos de propiedades

**[F]** pytest vincula flakiness con estado no controlado e insuficiente aislamiento; el paralelismo puede exponerlo. La investigación de flimsiness advierte además sobre inestabilidad bajo mutación [S11, S16].

**[R]** Un rerun que pasa no debería transformar un fallo en evidencia limpia. Registrar y distinguir fallo conductual, timeout, infraestructura e inestabilidad resulta más informativo que añadir reintentos.

**[F]** Hypothesis permite configurar generación y reproducibilidad. Sus parámetros no constituyen una demostración de suficiencia [S16].

**[R]** El presupuesto de propiedades debe responder al invariante, dominio y costo por ejecución. No hay fundamento externo encontrado para imponer universalmente ni **8–10** ni **100–1000** entradas.

**[R]** Eso no autoriza a reducir hoy el mínimo vigente: la contradicción requiere una decisión y migración de la norma canónica. Tampoco corresponde posponer una variante contractual obligatoria alegando presupuesto. Para reproducibilidad deben registrarse semilla, versión, configuración y contraejemplo pertinente.

### Correcciones expresas a la investigación anterior

| Recomendación anterior | Actualización [R], sustentada arriba |
|---|---|
| «Un test por postcondición». | Retirar como cuota: contradice la selección por promesa y la trazabilidad muchos-a-uno de R2/R7. |
| Uno o dos tests CLI por superficie. | No hay cuota respaldada. Los comportamientos propios del proceso determinan cuáles hacen falta. |
| testmon válido solo en proceso. | Demasiado absoluto: existe soporte de cobertura de hijos; falta acreditar atribución y selección. Los archivos estáticos siguen siendo un límite expreso. |
| Migrar la mayoría a `main(argv)` como opción más rentable. | Rentabilidad no medida; `main(argv)` no se presupone como interfaz disponible ni pública. |
| Gate por diff con cero supervivientes injustificados. | Propuesta propia, no conclusión necesaria de Google. No adoptarla ahora. |
| Comparar solo mutation score antes/después. | Usar identidades sobre un conjunto fijo; el porcentaje aislado puede ocultar pérdidas. |
| Propiedades solo en funciones puras. | Es una simplificación operativa, no un límite general de la técnica. Cualquier ampliación en CDAD debe respetar su contrato vigente. |
| Noche completa, mutación y orden aleatorio por defecto. | No introducir esa operación recurrente sin necesidad, costo y autorización. |

---

## (d) Cruce con los hallazgos A1–A8

| Hallazgo del Discovery | Contraste externo | Consecuencia y pregunta todavía abierta |
|---|---|---|
| **A1 — R2 ya rechaza acumulación.** | **[F]** S1/S2/S8 respaldan no usar cantidad o cobertura como aceptación suficiente. | **[R] Confirma.** Aplicar contribución respecto de la suite, no inventar otra doctrina. Sigue sin saberse cuántos tests carecen de contribución. |
| **A2 — Instrucciones postcondición→test.** | **[F]** S1/S18 privilegian comportamiento y legibilidad; no establecen una correspondencia numérica. **[F]** Persisten el paquete RED, `SKILL.md:204`, handoff y re-entry citados por A2. | **[R] Confirma la incoherencia local.** Alinear ejemplos y despachos; no fusionar por decreto todas las verificaciones de una promesa. |
| **A3 — Falta retiro ordinario por redundancia.** | **[F]** S3 aporta evidencia sobre reducción y riesgos de preservar solo cobertura. | **[R] Confirma y precisa.** Añadir sustitución al AUDIT/POST-AUDIT existente. La equivalencia de cada lote sigue pendiente de acreditar. |
| **A4 — Skills y presupuestos contradictorios.** | **[F]** S1/S16 no sustentan el umbral de utilidad de 30 s ni una cuota universal de entradas. | **[R] Confirma.** Resolver hogares normativos y retirar reglas rivales. La literatura no elige el presupuesto concreto de CDAD. |
| **A5 — Inventario incompleto y mapa limitado.** | **[F]** S12/S13 muestran que cobertura/dependencias no cubren por sí solas todas las superficies relevantes. | **[R] Confirma.** Corregir los 158 nodeids/18 archivos informados por Discovery; no presentarlos como «tests sin promesa». El mapa de 29 registros tampoco acredita toda la suite. |
| **A6 — Preparación CLI repetida.** | **[F]** S15 explica costos por worker y coordinación de fixtures. | **[R] Abre una alternativa mecánica, no prueba redundancia.** Los 21 flags costaron 21,879 s en la muestra; eso no acredita que sus obligaciones sean equivalentes ni cuánto se ahorraría. |
| **A7 — Candidatos, no lote eliminable.** | **[F]** S3/S4 aconsejan contrastar detección y evitar simplificaciones por cobertura o cantidad. | **[R] Confirma la cautela.** El par B1 protege estados distintos; 1,919 s es costo conjunto observado, no ahorro. Falta acreditar el recorrido sustituto. |
| **A8 — Prosa frente a conducta.** | **[F]** S2/S7/S17 distinguen cambio, oráculo y representación; la norma documental local exige revisión semántica separada. | **[R] Confirma con matiz.** Conservar verificaciones textuales pertinentes, declarar su límite y no presentarlas como conducta de un agente. La suficiencia semántica sigue requiriendo contraste independiente. |

**[R]** Ninguna fuente externa determina la proporción de redundancia local, la distribución temporal completa o la seguridad de xdist. Esas preguntas siguen siendo empíricas del proyecto.

---

## (e) Alternativas comparadas para CDAD

Todos los costos y riesgos siguientes son **valoraciones cualitativas [R]**, no estimaciones medidas. R2 selecciona; R4 justifica entrada/promociones; R7 protege todas las promesas comprometidas.

| Alternativa | Pros | Contras / costo / riesgo | Encaje R2/R4/R7 | Recomendación |
|---|---|---|---|---|
| **Criterio + AUDIT por contribución** | Aprovecha controles existentes; previene acumulación. | Inspección manual; posible justificación vacía. Costo bajo–medio. | Directo; explicitar diferencia y sustituto. | **Primero**, sin gate nuevo. |
| **Mapa del lote + poda sin mutación** | Conserva obligaciones y permite actuar sin herramientas nuevas. | Puede pasar por alto diferencias sutiles de detección. Costo medio; revisión independiente necesaria. | Compatible si acredita obligaciones, estados y efectos. | **Base del piloto.** |
| **Mapa + mutación acotada** | Añade evidencia de sensibilidad antes/después. | Integración y costo desconocidos; equivalencia, ruido y subprocess/staging. | Complemento de R7; no sustituye el mapa ni habilita tests ajenos a R2. | **Experimento opcional**, ámbito fijo; no gate general. |
| **Poda por cobertura o recuentos** | Barata de automatizar. | Igual cobertura o menos tests no acreditan protección. Riesgo alto. | Insuficiente para R7. | **No usar como criterio de retiro.** |
| **Selección explícita por capacidad/impacto** | Comprensible; aprovecha inventario. | Depende de datos actualizados y dependencias conocidas. | Apoya regresión proporcional; no reemplaza cierre. | **Preferida inicialmente.** |
| **testmon** | Selección dinámica de Python; reduce trabajo repetido si funciona. | Datos previos; hijos y atribución por verificar; no sigue archivos estáticos. Costo medio. | Complementario, con fallback conservador. | Diferir hasta comprobar selección real. |
| **Fixtures inmutables + xdist** | Puede reducir preparación y espera sin podar. | Carreras, multiplicación de staging y recursos. Costo medio; ahorro desconocido. | Debe conservar comportamientos y atribución del resultado. | Medir preparación primero; paralelismo después. |
| **Invocación en proceso** | Puede abaratar arranques y facilitar instrumentación. | Puede dejar de observar entorno y ciclo de proceso; migración potencialmente alta. | Solo con interfaz pública real y garantías CLI restantes. | No migración masiva; decidir por superficie. |
| **Perfil rápido por tamaño y capacidad** | Feedback frecuente y explícito. | Puede ocultar garantías si se confunde con aceptación completa. Costo bajo–medio. | Compatible con evidencia proporcional y cierre vigente. | Usar selección existente antes de más clasificación. |
| **Presupuesto de propiedades por invariante** | Costo explícito y reproducible. | Un presupuesto escaso puede dejar variantes obligatorias sin comprobar. | Requiere resolver norma actual; nunca diferir promesas. | Incluir decisión en 013-001; optimizar tras medir. |
| **Contract tests de dobles** | Detectan divergencia del sustituto frente a la interfaz real. | Otra verificación que mantener; no reemplazan integración. | Válidos para una obligación concreta. | Solo donde haya doble y riesgo acreditado. |
| **Golden/snapshot selectivo** | Hace visibles cambios de representación. | Actualización mecánica y fragilidad por detalles accidentales. | Válido si representación/bytes son promesa. | Selectivo, no snapshot global de prosa. |

### Decisión recomendada sobre «garantía conservada»

**[R]** Adoptar como base **mapa de obligaciones del lote + sustitutos + revisión independiente + evidencia proporcional**. Ensayar mutación cuando pueda mejorar esa evidencia con costo acotado.

**[R]** Si el ensayo no funciona, no se declara éxito ni se convierte automáticamente en un proyecto de infraestructura. Se conserva la incertidumbre, se mantiene el test dudoso o se reduce el lote. Lo simple primero no significa aceptar una poda no acreditada.

---

## (f) Veredicto sobre `cdad-spec-and-test`

### Verificación de la afirmación del orquestador

| Afirmación | Resultado |
|---|---|
| Es residual. | **[F]** Conserva una carga obligatoria legacy, aunque no participa como skill en paquetes v2. **[R]** «Residual» describe su posición, no significa «sin consumidores». |
| Solo aparece en dos legacy-loads. | **[F]** Son los dos hogares fuente: `sources/roles/architect.md:65` y `test-writer.md:17`. Se propagan a agentes generados, incluidas variantes Odoo. El intake también la nombra para prohibir recargarla en ruta de paquetes (`architect.md:26-29`). |
| La instala `install.sh`. | **[F]** Figura en `SKILLS`, línea 66; la copia por archivo se aplica a esas entradas (`:1272-1314`). |
| Tiene reglas contradictorias. | **[F]** Descarta tests de ≥30 s (`SKILL.md:80-85`), resume «todos pasan → Merge» (`:65-78`) y presenta otro formato/numeración de gates (`:95-102`). Esto diverge del ciclo vigente. |
| Paquetes v2 la usa. | **[F] No como carga de instrucciones.** `cdad_packet.py:1995-2000` compone `packets/common.md`, rol y subfase. El intake prohíbe cargar skills completas de ciclo/spec. No se infiere que las obligaciones de los agentes desaparezcan. |

### Qué se perdería al retirarla

**[F]** Su contenido útil no es exclusivamente de código: declara aplicación a documentación, infraestructura y research, y admite verificaciones por comandos, archivos y pasos manuales con resultado esperado (`SKILL.md:9-14,52-60`).

**[F]** El ciclo actual ya dispone de contratos documentales y contempla verificación y aceptación diferenciadas (`documentary-contracts.md:89-175`).

**[R]** Debe conservarse la idea útil —definir qué significa terminado y cómo se verifica, sin limitar «test» a pytest—, **no** sus gates paralelos, su postcondición única ni el atajo verde→Merge. Fusionar significa completar o enlazar hogares existentes, no copiar íntegramente la skill.

### Qué puede romper una retirada incompleta

- **[F] Roles y generación:** los legacy-loads seguirían ordenando cargar algo ausente. Los cambios pertenecen a `sources/` y luego a regeneración.
- **[F] Tests:** `tests/test_cdad_generate.py:458-499` y `tests/test_cdad_adapters_opencode.py:230-271` exigen literalmente la carga. **[R]** Quitarla sin migrar esas expectativas produciría incompatibilidad; esta conclusión es estática, no resultado de una corrida.
- **[F] Instalador:** `guard_sources`, `install.sh:553-566`, exige los directorios de `SKILLS`. Borrar el directorio manteniendo la entrada no es una retirada válida.
- **[F] Validadores:** no se encontraron referencias directas en `cdad-doctrine-check.py` ni en los `tests/validate-*.sh` inspeccionados. **[R]** Eso no acredita que sus resultados sigan verdes después de un cambio.
- **[F] ADR-002:** menciona la skill en el contexto histórico y como parte de la fuente completa (`:9,33`). **[R]** Registrar la decisión posterior; no borrar el antecedente como si nunca hubiera existido.
- **[F] Manifiesto generado:** `cdad-generate.py:948-970` enumera artefactos de agentes, no árboles de skills. Cambiar las fuentes modifica agentes y sus hashes; no hay una entrada de skill que simplemente quitar de ese manifiesto.
- **[F] Ownership instalado:** la poda de obsoletos depende del manifiesto previo y del estado de los bytes (`install.sh:1424-1544`). Archivos modificados o no verificables se preservan; la copia no usa `--delete`. **[R]** Sacarla de `SKILLS` no garantiza borrar todas las copias antiguas.

### Recomendación

**[R] Fusionar lo útil y retirar la skill autónoma como parte de 013-001.**

Conservarla corregida mantendría una superficie completa que architect/test-writer legacy cargan además del ciclo. Conservarla como documento no cargado exige igualmente decidir ubicación y descubrimiento. La fusión resulta más simple porque los hogares de aceptación, formatos y producto documental ya existen.

**[R]** La retirada requiere migración conjunta de fuentes, referencias, tests afectados, generación y distribución. No propongo borrar ahora ni ejecutar el instalador dentro de esta investigación.

---

## (g) Epic revisado

**[R] Confirmo el corte en cuatro features**, con entregas observables y sin convertir el epic en una auditoría exhaustiva previa.

| Feature | Resultado propuesto [R] | Dependencias y límites |
|---|---|---|
| **013-001 — Coherencia del criterio y sus consumidores** | Alinear selección por promesa, contribución respecto de lo existente y sustitución en AUDIT/POST-AUDIT; corregir instrucciones operativas; resolver presupuestos de propiedades; fusionar y retirar `cdad-spec-and-test`. | Hogares canónicos antes que consumidores. Fuentes + regeneración, no edición manual de agentes. No poda masiva. |
| **013-002 — Inventario vivo y trazabilidad suficiente** | Resolver la brecha de inventario informada; mantener separadas clasificación y acreditación semántica; preparar el mapa del lote piloto y el mantenimiento de sus datos. | La reparación mecánica puede empezar independientemente; el criterio final se alinea con 013-001. No exige mapear semánticamente los 1937 tests. |
| **013-003 — Disposición de redundancias y poda piloto** | Lote revisable con decisiones de mantener, extender, sustituir o consolidar; sustitutos y obligaciones conservadas; evidencia antes/después; mutación opcional si se autoriza. | Depende de 013-001 y del inventario/mapa pertinente de 013-002. No cuota de tests eliminados, bytes o minutos. |
| **013-004 — Rendimiento sin pérdida de garantías** | Línea base autorizada; atribución de costos; optimización de preparación; evaluación posterior de paralelismo y perfiles. | Medición puede prepararse antes; comparar sobre un conjunto estable. xdist no es resultado obligatorio ni debe introducirse sin necesidad. |

Dependencia principal:

```text
013-001 ─┐
         ├──→ 013-003 ──→ evaluación final de rendimiento en 013-004
013-002 ─┘

013-004: preparación de medición y diagnóstico pueden adelantarse.
```

### Ajustes de alcance importantes

**[R]** No separaría la retirada de la skill como quinta feature por defecto: es parte de corregir fuentes de criterio rivales. Solo justificaría separarla una necesidad real de compatibilidad o despliegue gradual.

**[R]** No mezclaría poda y velocidad en la misma promesa. Una consolidación puede mejorar mantenimiento sin acelerar; una fixture puede acelerar conservando todos los casos. El epic debe informar ambos resultados sin presentar uno como prueba del otro.

**[F]** La muestra existente fue deliberada: 205 tests en 252,25 s, no una línea base estadísticamente representativa (`discovery.md:172-202`). **[R]** No permite fijar ahorro global ni objetivos de paralelismo.

### Integración entre features

**[R]** El cierre debe contrastar, usando los mecanismos ya existentes:

- que legacy y paquetes transmiten el mismo criterio aplicable;
- que el inventario refleja los tests resultantes;
- que las sustituciones conservan genealogía y obligaciones;
- que el perfil optimizado no obtiene velocidad omitiendo garantías.

**[F]** La política actual exige suite completa al cierre de feature y contempla anticiparla ante cambios en instalador, staging o renderer (`stage-3-tdd.md:61-79`). **[R]** El epic deberá obtener las autorizaciones correspondientes; este addendum no rebaja esa política ni autoriza corridas.

### Trabajo diferido propuesto

**[R]** Dejar fuera inicialmente:

- acreditación semántica exhaustiva de toda la suite;
- mutación global, gate universal y detector LLM de equivalencias;
- migración masiva a ejecución en proceso;
- reorganización general de archivos;
- nuevos clasificadores, dashboards y operaciones nocturnas;
- instalación de herramientas antes de decidir qué experimento necesitan.

**Motivo:** ninguna de esas ampliaciones es necesaria para acreditar la primera mejora. No se difiere una obligación de un lote que sí se comprometa.

**[R]** Se preservan las specs cerradas de 008-002 y 008-006. Actualizar datos vivos o abrir capacidades nuevas no requiere reescribir retrospectivamente sus contratos.

---

## (h) Preguntas actualizadas para el dueño

1. **¿Confirmas el epic de cuatro features y estas dependencias?** Recomiendo mantener separadas coherencia, inventario, poda y rendimiento.

2. **¿Apruebas fusionar lo útil y retirar `cdad-spec-and-test` dentro de 013-001?** La alternativa es conservarla corregida, asumiendo otra superficie que mantener.

3. **¿Aceptas como criterio del piloto conservar obligaciones y protecciones acreditadas, sin cuota de poda?** La revisión independiente debe poder concluir «mantener» cuando no haya sustitución suficiente.

4. **¿Autorizas evaluar mutación únicamente como experimento acotado?** Ámbito fijo, canario de subprocess/staging y presupuesto previo; sin gate universal ni obligación de construir infraestructura si no resulta viable.

5. **¿Autorizas una corrida completa de línea base y, más adelante, las verificaciones exigidas por los cambios aprobados?** Hasta ahora no existe esa autorización. El presupuesto de propiedades y cualquier objetivo de velocidad quedan para una decisión fundamentada, no se fijan aquí.

---

**[F] Estado de entrega:** sin modificaciones del asistente en el repositorio ni corridas nuevas de tests. La comprobación final mantuvo únicamente el archivo no versionado preexistente `docs/specs/010-000-continuity-relative-root/discovery.md`; el diff de `sources`, `skills`, `tests`, `scripts`, `agents`, `build` e `install.sh` estaba vacío.

**[R] Conclusión:** primero coherencia y mantenimiento de garantías; después optimización medida. La mutación puede fortalecer la evidencia del piloto, pero no debe convertirse en una nueva cuota que vuelva a premiar acumulación.
