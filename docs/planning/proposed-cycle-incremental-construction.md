# Ciclo propuesto — Construcción incremental y validación reproducible

Fecha: 2026-10-17.
Estado: **planificación diferida; no activado; spec y aprobación pendientes**.
Identificador: se asignará al incorporarlo al backlog vigente, sin reservar ahora
un número de feature ni crear otra épica.

Origen: [caso S-ITER-01 y análisis](../../findings/incremental-construction-and-reproducible-validation-2026-10-17.md).
El dueño solicita preparar este ciclo mientras hay otros trabajos en marcha.
No concede por ello HITL de ejecución, aprobación del futuro contrato ni despliegue.

**Relación necesaria, 2026-10-21:** consumir también [S-SYS-01](../../findings/system-capability-planning-evidence-2026-10-21.md)
y la [continuación surgida de Superlite](superlite-followups-2026-10-19/plan.md).
El caso amplía la evidencia desde conservar preparación y aprendizaje hacia
integrar capacidades operativas y transferir hallazgos a sus consumidores.
Antes de activar esta propuesta, resolver si sus resultados se reciben dentro
de A/B; no ejecutar iniciativas duplicadas ni fusionar alcances en silencio.
El marco es contratos, garantías y evidencia; las pruebas de código son un
instrumento posible y no equivalen a la garantía exigida.

## 1. Resultado útil

Que CDAD ayude a construir y depurar acumulando avance y aprendizaje, con encargos
que permitan las correcciones autorizadas y con una validación que demuestre lo
que realmente exige el contrato. Evitar tanto la reconstrucción ritual como la
aceptación de un resultado dependiente de reparaciones no registradas.

Una unidad coherente: **evaluar el principio, resolver su incorporación y alinear
sus consumidores operativos**. No presupone desarrollar maquinaria nueva.

## 2. Entrada y ubicación en el trabajo vigente

- Se ejecutará en un borde seguro de ciclo, después del trabajo actualmente en
  marcha. No se insertan tareas ni cambios de contrato en un paquete despachado.
- Al iniciar, el orquestador consulta la vista compacta, identifica versión
  instalada y trabajo activo y reconcilia lo ya incorporado. La fotografía al
  documentar mostraba `006-002-delegation-by-layer` en curso; no es una condición
  que la próxima sesión deba reproducir.
- Si sigue abierto epic-006, el dueño podrá incorporarlo mediante una enmienda
  acotada cuando corresponda. Si ya cerró, se ubica en la planificación siguiente.
  No reabrir un epic cerrado sólo para conservar esta propuesta.
- Considerar lo que haya aterrizado sobre separación de capas, delegación nativa,
  decisiones vigentes, evidencias y planificación. No duplicarlo ni sustituirlo
  sin un conflicto concreto.
- Autoridad y aprobación de spec/plan siguen el mecanismo vigente y el mandato
  que exista entonces. No se heredan delegaciones de epics anteriores.

## 3. Alcance y restricciones

**Dentro:** investigación acotada de la evidencia y reglas, decisión metodológica,
modificaciones mínimas en procedimientos/encargos/re-entry/review, trazabilidad a
su dueño canónico y una recepción sobre trabajo pendiente apropiado.

**Fuera:** reparar el consumidor; modificar su host; diseñar su laboratorio;
repetir sus ventanas; imponer contenedores, carpetas, SO o runtime; crear un rol,
sandbox, motor de workflows, esquema de checkpoints o formato de recibo nuevo
sin una necesidad concreta descubierta y aprobada. Tampoco comparar modelos.

Conservar independencia de roles, contratos aprobados, límites de escritura y
autoridad sobre efectos externos. «Explorar» no habilita al implementer a alterar
los tests ni al test-writer a inspeccionar implementación. El orquestador delega
la construcción y la depuración sustancial; no absorbe todos sus detalles.

No introducir una fase universal «investigar todo antes» ni una secuencia fija
«explorar → limpiar → repetir». La eficacia prima sobre un límite de contexto;
la carga metodológica debe ser proporcional al trabajo que habilita.

## 4. Preguntas de discovery y decisiones requeridas

1. ¿Qué parte del caso está comprobada y qué parte sólo fue relatada? Conservar
   esa clasificación; no transformar duración relatada en benchmark.
2. ¿Qué está ya resuelto por ADR-011, evidencia proporcional, equivalencia y
   replanteo? Identificar el delta, con referencias actuales, antes de editar.
3. ¿Dónde reside el principio y qué consumidores deben referenciarlo? Proponer
   un único dueño operativo; un ADR puede registrar la razón, pero no sustituye
   instrucciones instalables. Reutilizar la estructura vigente.
4. ¿Cómo expresa un encargo su propósito, el estado de partida, el margen para
   corregir y la evidencia esperada usando sus campos actuales? Evitar nuevos
   campos obligatorios si el formato existente es suficiente.
5. ¿Cuándo una intervención conserva resultados y cuándo invalida comprobaciones
   dependientes? Distinguir estado construido de evidencia acreditada. No exigir
   demostrar otra vez todo el sistema por un cambio local.
6. ¿Cómo separar fallos del entregable evaluado y del instrumento de evaluación,
   dando una salida legítima cuando el agente necesita cambiar de alcance?
7. ¿Qué trabajo real próximo permite observar la mejora sin reejecutar desarrollos
   ya terminados ni crear fallos artificiales en un sistema compartido?

Salida: diagnóstico breve, decisiones recomendadas, mapa fuente→consumidor y
spec/plan proporcionales. Puede concluir que parte de la propuesta ya está cubierta
y no necesita cambios. La incorporación de lo restante debe quedar explícita.

## 5. Construcción propuesta, después de aprobar spec y plan

| Unidad | Resultado y responsable | Dependencias / comprobación |
|---|---|---|
| U1 — Evaluación y contrato | Architect: discovery, alcance mínimo, criterios de aceptación y plan. La aprobación corresponde a quien tenga autoridad vigente. | Fuentes del caso y versión actual. Contrastar el despacho con el propósito, no sólo resumir el ADR. |
| U2 — Incorporación operativa | Roles correspondientes: principio canónico y alineación de los consumidores necesarios. | U1 aprobado. Reusar formatos y generación existentes; aislamiento test-writer/implementer cuando haya cambios ejecutables. |
| U3 — Review y recepción | Reviewer independiente: coherencia de reglas y utilidad. Orquestador: evidencia instalada/real pertinente y cierre honesto. | Cambios de U2 y trabajo pendiente elegido. Una review formal al final; re-review focal si aparecen bloqueantes. |

U2 no es una batería de tareas por archivo. El plan concreto agrupa cambios por
responsabilidad y efecto, limitando rondas y reorientación. Si no hace falta código,
no inventar un RED de búsqueda de frases para simular una feature ejecutable.
Si surge código necesario, usar el ciclo TDD vigente sobre comportamiento observable.

La recepción real puede requerir esperar al consumidor. En ese caso distinguir
incorporación disponible y eficacia observada; no fabricar aceptación ni detener
todo trabajo independiente. Decidir con la autoridad vigente cómo registrar lo pendiente.

## 6. Criterios de aceptación que debe precisar la spec

| Criterio | Evidencia esperada |
|---|---|
| CA-1 — Principio con razones | Existe un dueño canónico instalable. Distingue exploración y validación sin imponer limpiar, continuar o reiniciar siempre. |
| CA-2 — Encargo coherente | En un encargo real se entiende qué se quiere aprender/demostrar, qué puede corregir el rol y qué debe devolver. No exige pedir permiso por cada arreglo dentro de autoridad ni resolver fuera de ella. |
| CA-3 — Re-entry honesto | Se identifica qué se observó, qué se modificó, qué queda incorporado y qué resultado es reproducible. La evidencia previa sólo se reutiliza donde sigue aplicando. |
| CA-4 — Sin garantías debilitadas | No se alteran contratos, tests o autoridad para conseguir un verde. «Sin errores nuevos» no sustituye la aceptación; fallos conocidos relevantes no desaparecen del reporte. |
| CA-5 — Elección contextual | La revisión evalúa ejemplos donde conviene continuar, aislar y reconstruir. Una validación puede detenerse si se invalida su fundamento o continuar con controles independientes; la razón queda comprensible. |
| CA-6 — Capas y distribución | Las reglas generales permanecen únicas; agentes y paquetes remiten a ellas según su función. Verificar la ruta instalada afectada, no sólo el repositorio fuente. |
| CA-7 — Utilidad hacia adelante | Un trabajo pendiente apropiado registra la pregunta, decisión de alcance, evidencia y resultado. Informar retrabajo/repeticiones evitables observados; desconocidos como desconocidos. No exigir una mejora porcentual ni comparaciones causales que los datos no sostengan. |
| CA-8 — Proporcionalidad | No nace un formulario largo, una etapa universal o un bloqueo extra. Una tarea simple conserva un camino simple; una integración compleja puede requerir más contexto y comprobaciones. |

CA-5 puede contrastarse con ejemplos breves de decisiones revisadas, sin introducir
errores en infraestructura real ni obligar al consumidor a recorrer las tres opciones.
CA-7 no se acredita sólo porque un texto mencione el principio o una suite esté verde.

## 7. Política de comprobación y recepción

- Aplicar la política vigente de pruebas proporcionales y equivalencia. Durante
  cambios ejecutables, focales y módulos afectados; suite de cierre según la
  política y el impacto real. No duplicar evidencia equivalente entre roles.
- En modificaciones de texto, revisar contradicciones, referencias y el encargo
  que producirán. Los chequeos de frases no prueban que un agente sepa aplicarlo.
- Probar generación/instalación aislada si se afectan esos caminos. El ciclo usa
  la instalación estable; su candidato no sustituye esa instalación a mitad de trabajo.
- Recibir la mejora en un uso posterior autorizado y apropiado. Separar tiempos
  de preparación, corrección y validación cuando estén disponibles y sean útiles;
  no imponer telemetría nueva para poder avanzar ni estimar tokens ausentes.
- Si faltan datos para comparar, describir el resultado y la limitación. No repetir
  el desarrollo anterior como experimento de control.
- El despliegue global, los servicios y el host del consumidor conservan sus
  reservas de autoridad. La propuesta no los autoriza.

## 8. Cierre y continuidad

El cierre deja: decisiones adoptadas o descartadas con motivo; fuentes canónicas
y consumidores alineados; evidencias con sus límites; resultado de la recepción
o pendiente explícito; deuda acotada, sin llamar completo a lo no observado.

Si se registra un ADR de CDAD, su estado refleja la aprobación real y su regla
aparece en el producto instalable. No copiar como aceptado el ADR propuesto del
consumidor. Referenciar su origen anonimizado y mantener la distinción de niveles.

En cada handoff basta un estado breve: versión/contrato aplicable, cambios hechos,
estado y conocimiento reutilizables, evidencia válida, incertidumbres y siguiente
acción. No volver a cargar la conversación completa ni convertirla en otro contrato.

**Acción siguiente, cuando llegue el turno:** reconciliar esta propuesta con la
planificación vigente, asignar la feature y realizar U1. Este documento no activa
el ciclo, no cambia el state y no necesita un prompt que repita todo su contenido.
