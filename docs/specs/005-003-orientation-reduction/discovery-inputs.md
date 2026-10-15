# Insumos de discovery — 005-003-orientation-reduction

Fecha: 2026-10-10. Preparado por instrucción del dueño: conservar los análisis
de Codex y Claude para que 005-003 los contemple al llegar su turno.
**No es una spec aprobada, no activa la feature y no modifica el ciclo en curso.**

## Resultado que debe orientar el discovery

El orquestador debe llegar al siguiente despacho legítimo con contexto acotado,
sin reconstruir preventivamente la implementación del CLI ni cargar toda la
historia del proyecto. Debe conservar autoridad, contratos, evidencia y
capacidad de orquestar durante horas. Menos preparación no significa omitir
gates, ocultar bloqueos o delegar una tarea insuficientemente definida.

El plan vigente mide orientación al retomar (`resume`). Este insumo aporta
además **arranque desde reposo después de una enmienda autorizada**. Al preparar
la spec de 005-003, reconciliar esa frontera con 005-006: usar el procedimiento
existente de reconocimiento/arranque, no crear otro bootstrap. Si se necesita
enmendar la fila del epic, hacerlo entonces con la autoridad pertinente y sin
invalidar paquetes activos. No editar ahora el plan por esta nota.

## Caso nuevo: S-BOOT-04

Sesión real OpenCode 2.0.26. Encargo: incorporar una ampliación aprobada al plan,
sincronizar el state, conservar otra feature pausada e iniciar el discovery de
005-008 con subagente architect. La identidad exacta de la sesión y el método
de reproducción quedan en `.cdad/local/orientation-analysis-005-003-2026-10-10.json`
(archivo local ignorado por Git). No publicar ese registro ni los logs crudos.

| Medida observada antes del primer despacho | Valor |
|---|---:|
| Petición del usuario → inicio efectivo de la herramienta de delegación | 526,661 s; aproximadamente 8 min 47 s |
| Llamadas a herramientas | 72: 50 shell, 11 read, 10 edit, 1 skill |
| Salidas textuales de herramientas | 418.841 caracteres |
| Lecturas del state | 4 fragmentos consecutivos, líneas 1–2068; no cuatro relecturas completas |
| Salidas textuales de esos fragmentos | 215.292 caracteres; aproximadamente 51,4 % del total |
| Consultas de código operativo mediante búsquedas/extractos | 21 llamadas, aproximadamente 70.138 caracteres |
| Máximo proxy de entrada reportada en mensajes previos | 200.076 tokens, input + cache-read + cache-write |

Los caracteres incluyen envoltorios/numeración devueltos por las herramientas;
no son bytes originales de archivos. El proxy de tokens no es consumo acumulado,
costo ni una medición independiente de la ventana real del modelo. Las salidas
no incluyen la skill inyectada con el mensaje inicial: esa carga adicional fue
de 37.667 caracteres, según el registro. No inferir ahorro ya demostrado.

### Método y diferencias entre los dos análisis

La medida de Codex corta antes del primer evento `subagent`, usando el tiempo
del mensaje de usuario y `time.ran` de la herramienta. El nacimiento de la
sesión hija confirma el despacho unos 57 ms después. Se cuentan invocaciones
de herramientas, no comandos individuales dentro de una invocación de shell.
El máximo de tokens usa mensajes previos completados; no un mensaje todavía
en ejecución con contadores vacíos. La identificación de consultas de código
incluye búsqueda/extractos de `cdad_packet.py` y `cdad_continuity.py`.

Claude aportó una clasificación aproximada: 73 llamadas, 8,3 minutos y unas 19
lecturas de código. Los análisis coinciden en la dinámica, pero esos números
no se promedian ni se declaran idénticos. 005-002 debe reproducir la medida con
un criterio de corte explícito y explicar diferencias si compara ambos.

### Trabajo legítimo y orientación evitable

**Legítimo:** leer el encargo, incorporar la aprobación al plan, sincronizar
features/autoridad, preparar el paquete, republicar derivados anteriores y
comprobar versión, binding y validez. La sesión incluía una enmienda real:
no compararla sin matices con un arranque que ya tenía todo preparado.

**Evitable en este recorrido:** leer toda la historia del state e inspeccionar
el código del CLI para deducir autorización por rol, efectos de `prepare`,
defaults de alcance/evidencia, formato de continuidad y observaciones de
despacho. El primer `prepare` finalmente funcionó sin un bloqueo que exigiera
esa investigación previa. No se observaron denegaciones de permisos en el
tramo analizado; hubo errores de interfaz, rutas y formato.

La sesión usó inicialmente el comprobador de versión del checkout, que
correctamente devolvió `UNKNOWN`; luego el instalado devolvió `COHERENT` tras
republicar. También probó una raíz relativa que el CLI no admite, validadores
sin sus argumentos requeridos, un texto y después Markdown donde `begin`
esperaba JSON, y un registro de despacho sin el archivo de observaciones.
Algunos comandos imprimieron `rc=0` por consultar el retorno de una tubería,
aunque el CLI había emitido un error. Esto no es evidencia fiable del retorno
del CLI ni prueba que el agente haya declarado esos errores como éxito.

## Diagnóstico consolidado y corrección de atribución

**La instalación ya incluía 005-006, commit `35062b0`.** Claude corrigió su
hipótesis inicial de que la sesión corría con v9. La skill cargada reportó la
base instalada y el despliegue precedió al inicio de la sesión. No atribuir
este caso a ausencia de la receta nueva ni a un despliegue pendiente.

La información operativa existía, pero no fue consultada en el momento útil:
no aparecen lecturas de `project-start.md`, `project-execution.md` o
`continuity.md` antes de delegar. La sesión cargó las skills generales y luego
reconstruyó esa información desde el código.

La situación era «reposo → enmienda → nueva feature», aunque el encargo no
usaba literalmente «inicializar». La selección de la entrada no puede depender
de esa palabra. A la vez, la receta de arranque enumera comandos pero delega
los formatos JSON a otras referencias: descubrir la receta correcta no elimina
por sí solo toda la fricción de interfaz.

No reducir el diagnóstico a obediencia del modelo. Una interfaz que exige
encontrar varias referencias entre instrucciones extensas sigue siendo un
problema del producto. Tampoco resolverlo añadiendo todas las referencias al
contexto inicial: eso conserva el problema con más tokens.

## Cambios a evaluar en 005-003, por impacto

1. **Vista compacta del estado operativo.** Generada por código desde las
   fuentes existentes: proyecto reconocido, epic/feature, ejecución vigente,
   paquete y estado, autoridad/aprobación relevante, versión y ruta operativa
   siguiente. El historial se consulta selectivamente cuando existe una duda
   concreta. No crear otra memoria de estado que deba sincronizarse a mano.
2. **Selección explícita de entrada.** Ejecución activa → continuidad y
   reconciliación; reposo sin trabajo pendiente → apertura de siguiente unidad;
   bootstrap/configuración incompleta → procedimiento existente y diagnóstico.
   Un paquete preparado o trabajo pendiente se atiende, no se pierde por una
   inferencia simplista de `current_stage`. La salida compacta debe señalar la
   referencia operativa pertinente, sin sustituir decisiones estratégicas.
3. **Interfaz operativa suficiente.** Exponer para las operaciones frecuentes
   cuándo usarlas, argumentos necesarios, defaults relevantes, efectos y un
   ejemplo mínimo válido de sus archivos de entrada. Priorizar `prepare`,
   validación, `begin` y registro de despacho. Reusar esquemas/constantes ya
   existentes; evitar otro manual extenso mantenido a mano. Puede ser ayuda
   ejecutable, ejemplos generados o una referencia corta: decidir por utilidad
   y costo, no obligar a construir un generador de documentación completo.
4. **Comprobación de versión única y correctamente situada.** Reusar
   `cdad-version-check.py` instalado. Distinguir ausencia de derivados de
   incoherencia, republicar por el camino legítimo y verificar después. No
   duplicar inspecciones de manifiestos/marcadores sin una contradicción nueva.
   La coincidencia de archivos no demuestra lo cargado por una sesión abierta.
5. **Evidencia mecánica fiable.** Capturar el retorno del CLI real, sin ocultarlo
   con `head`/`tail`; salida acotada para el contexto y evidencia completa
   disponible. Errores accionables con formato esperado y recuperación legítima.
   No ampliar alcances, fabricar aprobaciones o borrar registros para continuar.
6. **Criterio de preparación suficiente.** Investigar más cuando hay un bloqueo
   o una incertidumbre que afecta al siguiente despacho. Una investigación
   técnica del producto pertenece al architect; el orquestador no debe repetirla
   preventivamente. No prohibir inspección de código cuando sí es necesaria.

**Historial separado:** Claude propuso moverlo fuera del state. No es requisito
inicial: una proyección puede reducir contexto manteniendo el formato actual.
Evaluar separación solo si aporta beneficio adicional medible, incluyendo
compatibilidad de consumidores, referencias, hashes y migración. No convertir
esta optimización en una reescritura obligatoria del sistema de estado.

## Aceptación que debe concretar el architect

- Una sesión nueva en reposo llega al primer despacho legítimo sin leer toda
  la historia ni reconstruir el CLI desde su código para el recorrido normal.
- Una reanudación con trabajo activo preserva autoridad, aprobaciones y efectos;
  una ausencia/incoherencia devuelve el bloqueo y cómo resolverlo. Un resumen
  corto no oculta un paquete pendiente ni declara válido un contrato cambiado.
- Los ejemplos operativos se ejecutan contra la versión correspondiente. No
  verificar utilidad solamente buscando frases en Markdown.
- El uso real siguiente reduce orientación y contexto con evidencia de
  005-002: tiempo hasta despacho, herramientas, volumen de salidas y proxy de
  entrada cuando esté disponible. Los datos ausentes permanecen desconocidos.
- La meta numérica se fija después de la medición, atendiendo a trabajo legítimo
  distinto entre casos. No imponer un límite universal de minutos/llamadas ni
  afirmar operación bajo 100k/200k sin evidencia de las sesiones pertinentes.
- La reducción no traslada trabajo innecesario al primer worker. Observar
  también si el encargo quedó completo, si hubo bloqueos/retrabajo y si las
  responsabilidades permanecen claras.

Probar hacia adelante con la próxima unidad real. No repetir desarrollos
completos para comparar: reutilizar estas trazas históricas como línea base y
usar pruebas deterministas pequeñas solo para el comportamiento necesario.

## Consumo al llegar el turno de 005-003

### Ampliación de criterio — 2026-10-11

El dueño pidió integrar la
[dirección estratégica](../../../findings/agent-operation-strategy-2026-10-11.md).
La orientación debe dar estado, autoridad, siguiente paso y capacidades reales
del entorno en una superficie breve, con referencias a la versión/configuración
efectivas. No reconstruir esa información desde código en cada arranque ni
inyectar toda la documentación para evitarlo.

Evaluar cómo el orquestador encuentra capacidades ya existentes para presentar
planes, archivos, previews y diffs. OpenChamber es un consumidor concreto: sus
capacidades visibles no se presuponen accesibles al agente. Verificar la instalación
y el mecanismo de acceso antes de prometer automatización; conservar fallback
portable por archivos/enlaces. Una integración compleja de UI queda como propuesta
posterior; no implementar OnlyOffice ni otra fuente de estado en 005-003.

Un primer despacho más rápido es una señal, no una aceptación suficiente:
comprobar que tiene insumos/capacidades adecuados y lleva a un resultado útil sin
trasladar la orientación al worker. La evidencia de 005-002 distingue eventos
observados de juicios del orquestador; no se atribuye utilidad por un timestamp.
La aceptación usa una próxima sesión real y registra ayudas extraordinarias,
bloqueos y resultado; una sonda técnica no demuestra por sí sola usabilidad humana.

### Paquete de discovery

El orquestador debe añadir **este archivo como insumo explícito** del paquete
de discovery del architect, junto con la salida de 005-002 y los hallazgos
previos enlazados abajo. El architect decide alcance y plan detallado; este
insumo no preaprueba una implementación ni fija sus funciones internas.

Reutilizar el transporte/recepción entregado por 005-009 y su corrección 005-010
según la versión instalada y su aceptación real. 005-007
recibe lo referido a tamaño de unidades y preparación de encargos; 005-003
sigue siendo dueño de orientación y acceso compacto a información operativa.
No duplicar bootstrap de 005-006 ni abrir un epic nuevo por este caso.

- [Casos anteriores de arranque](../../../findings/session-guided-start-friction-2026-10-10.md).
- [Plan del epic](../../epics/epic-005-real-operation/plan.md).
- [Discovery de medición 005-002](../005-002-session-context-meter/discovery.md).
- [Receta de arranque existente](../../../skills/cdad-cycle/references/project-start.md).
- [Interfaz de ejecución existente](../../../skills/cdad-cycle/references/project-execution.md).
- [Continuidad y ejemplos existentes](../../../skills/cdad-cycle/references/continuity.md).
