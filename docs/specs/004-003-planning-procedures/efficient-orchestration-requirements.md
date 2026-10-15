# Orquestación y validación proporcionales — requisitos para 004-003

Fecha: 2026-10-05. Decisión del usuario: incorporar la propuesta de eficiencia
a la planificación de 004-003. Este documento precisa el encargo; no aprueba
una spec aún no escrita ni sustituye por sí solo los gates instalados.

## Intención y alcance

Reducir tiempo, tokens y contexto gastados en trabajo repetido, conservando
contratos, aislamiento de roles, revisión independiente y evidencia verificable.
El orquestador responde por el resultado útil y por justificar el trabajo
adicional según la información o garantía que aporta. Debe poder sostener una
ejecución prolongada dentro de su mandato sin exigir intervención por cada paso.

Se incorpora como procedimiento de los roles existentes en 004-003. No requiere
otro agente, epic, plataforma de métricas, caché universal ni nuevas restricciones
por comando. La automatización posterior no es requisito para usarlo.

## Requisitos del procedimiento

1. **Tests proporcionados al contrato y al riesgo.** Verificar comportamiento
   observable, invariantes y fallos relevantes. Evitar pruebas de detalles
   internos y variantes redundantes sin capacidad de detección adicional.
   No imponer una cuota de tests ni limitarse al camino feliz. Si se descubre
   un requisito importante ausente, elevar la corrección del contrato; no
   descartarlo para ahorrar ni ampliar unilateralmente el alcance.
2. **Plan de validación breve por unidad de trabajo.** Indicar pruebas focales,
   regresiones afectadas, gate de integración y responsable de ejecutar cada
   comprobación. Puede referenciar una estrategia común del proyecto. Para
   trabajo sin código, definir comprobaciones observables adecuadas al artefacto,
   sin inventar una suite de software.
3. **Iteración focalizada.** Durante construcción y correcciones, ejecutar lo
   necesario para resolver la hipótesis actual. Ampliar al cambiar contratos
   compartidos o ante incertidumbre sobre impacto. Ejecutar la suite completa
   acordada en el gate correspondiente; no hacerla obligatoria en toda etapa
   ni prohibir una ejecución temprana que tenga una razón concreta.
4. **Reutilización explícita de evidencia vigente.** Un cambio de rol o de etapa
   no invalida por sí mismo una ejecución. Comprobar versión del producto y
   tests (incluidos cambios sin commit), selección ejecutada, comando, resultado,
   entorno/configuración/dependencias relevantes y disponibilidad del original.
   El mismo commit no prueba equivalencia del entorno. Si no se puede establecer
   equivalencia, declarar la incertidumbre y ejecutar lo necesario. No exigir
   una nueva infraestructura de huellas para aplicar esta regla inicialmente.
5. **Re-entry con responsabilidad, sin duplicación rutinaria.** El orquestador
   comprueba identidad, alcance, vigencia y suficiencia de la evidencia y los
   cambios permitidos. Puede usar resultados ejecutados por un rol o CI: una
   afirmación de éxito sin evidencia no alcanza. Ante inconsistencias, riesgos
   concretos o fallos, profundiza o reproduce la comprobación pertinente. No
   repite automáticamente la suite ni hace una segunda review completa.
6. **Delegación por unidades coherentes.** Delegar trabajo sustancial y tareas
   que requieren aislamiento; conservar decisiones, coordinación y controles
   breves en el orquestador. No maximizar cantidad de agentes ni abrir una sesión
   por operación pequeña. Agrupar objetivos relacionados dentro del mismo rol
   cuando compartan contexto y tengan un cierre verificable, preservando la
   separación RED/GREEN y la revisión independiente. Paralelizar solo con
   dependencias y alcances compatibles.
7. **Encargos suficientes, no exhaustivos.** Incluir objetivo útil, contrato y
   versión, entradas pertinentes, alcance, decisiones autónomas, estrategia de
   validación, salida esperada y motivos para volver al orquestador. Referenciar
   fuentes precisas y permitir lecturas pertinentes dentro del rol; no copiar
   el historial ni cargar toda la metodología. Los logs completos permanecen
   consultables fuera del contexto activo.
8. **Intervención por falta de progreso.** Un reintento debe responder a una
   hipótesis o información nueva. Repetición idéntica, ausencia de avance,
   obstáculo del entorno o costo desproporcionado disparan revisión de estrategia.
   Reconciliar la actual regla general de dos intentos con este criterio, sin
   reemplazarla por reintentos ilimitados. Presupuestos concretos autorizados
   y límites reales del runtime siguen aplicando. Un límite no concede permiso
   para saltar controles ni para declarar éxito sin evidencia.
9. **Utilidad desde el plan.** Nombrar el recorrido del consumidor y quién produce
   cada entrada. Comprobar el resultado instalado cuando sea pertinente. Conservar
   trabajo válido ante desvíos y corregir solo lo invalidado.

## Integración sin nuevas copias de reglas

El architect debe identificar la fuente canónica de cada regla y armonizar sus
consumidores: planificación y templates, gates, re-entry, instrucciones de
orquestación y paquetes de roles/subfases. Revisar especialmente:

- `skills/cdad-cycle/references/stage-3-tdd.md`: presupuesto de ejecución y gates.
- `skills/cdad-cycle/references/re-entry.md` y `skills/cdad-cycle/SKILL.md`:
  diferencia entre exigir evidencia y exigir una ejecución nueva.
- `sources/roles/orchestrator.md` y paquetes: tamaño del encargo y contexto.
- Procedimientos especializados, incluido Odoo: preservar requisitos reales
  de entorno limpio, instalación e integración; definir cuándo una ejecución
  anterior los satisface y cuándo requiere otra ejecución.

No editar salidas generadas a mano. Este encargo es entrada de diseño; el
procedimiento operativo final tendrá su fuente canónica, no otra copia aquí.
La spec deberá hacer explícitos los cambios de gates para su aprobación.

## Aceptación a derivar en la spec

- Un resultado completo verificable puede satisfacer controles consecutivos
  de implementer, orquestador y reviewer sin tres ejecuciones equivalentes.
- Un cambio relevante posterior o evidencia de entorno insuficiente exige
  revisar la vigencia y ejecutar las comprobaciones afectadas antes del cierre.
- Una corrección local usa pruebas focales; un cambio transversal justifica
  ampliación. El procedimiento no trata ambos casos como idénticos.
- Un encargo permite trabajar sin reconstruir toda la conversación y mantiene
  las fronteras de rol. La delegación no elimina responsabilidad del orquestador.
- El procedimiento llega a la instalación y se aplica a la planificación del
  trabajo pendiente de 003-002. Separar evidencia de instrucciones distribuidas
  de evidencia de mejora observada durante ejecución real.

Usar casos pequeños para comprobar reglas y distribución. Evitar suites que
solo busquen frases del prompt o intenten probar determinísticamente que un
modelo siempre seguirá las instrucciones. La mejora operativa necesita uso real.

## Continuidad hacia epic 003 y medición mínima

- **004-003:** procedimiento, estrategia de validación en planes, revisión del
  plan y re-entry proporcional. Primer uso sobre el trabajo pendiente de 003-002.
- **003-002:** facilitar recepción y referencia de evidencia original; no
  confundir recibo mecánico con aprobación de calidad ni implementar aquí ese
  subsistema para poder empezar.
- **003-003:** detectar repeticiones improductivas y registrar sus causas;
  distinguir una repetición justificada de un bucle sin progreso.
- **003-004:** conservar decisiones, pendientes y referencias al renovar contexto,
  sin volver a cargar logs completos ni repetir trabajo por perder su rastro.

Registrar en los artefactos existentes, con esfuerzo proporcionado: tiempo de
pruebas, cantidad y motivo de ejecuciones completas, reutilización de evidencia,
retrabajo y defectos detectados después. Tokens solo si hay datos disponibles;
lo desconocido se declara. No repetir desarrollos para comparar ni atribuir
causalmente ahorros entre features distintas. Menor tiempo no basta si aumenta
el retrabajo o se pierde cobertura de requisitos.

## Próximo paso y handoff

Incorporar estos requisitos al discovery/spec/plan de 004-003 y a su revisión
independiente. Si el primer encargo del architect ya fue ejecutado, entregar un
delta acotado conservando lo válido; no reiniciar Discovery. No cambia el state
ni activa construcción por la mera existencia de este documento.
