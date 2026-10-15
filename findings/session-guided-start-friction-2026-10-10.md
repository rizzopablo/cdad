# Intento de continuar un epic: orientación sin despacho

Fecha: 2026-10-10. Caso anonimizado S-BOOT-02, OpenCode 2.0.26.
Análisis de lectura de la sesión y de sus resultados de herramientas; no se
ejecutó un nuevo ciclo ni se modificó la metodología.

## Resultado observado

La solicitud fue retomar el epic con la siguiente feature del plan actualizado.
La sesión llegó a identificar 005-006, pero terminó por una orden explícita
de parar, antes de modificar el state, preparar un paquete o delegar. No hubo
sesiones hijas. No fue una caída técnica ni un bloqueo por permisos.

| Medida | Observación |
|---|---|
| Duración creada → respuesta completada | Aproximadamente 7 min 18 s |
| Llamadas a herramientas | 41: 35 shell, 4 read, 2 skill |
| Turnos del asistente | 22 |
| Mayor salida individual | 55.027 caracteres: lectura parcial del state histórico |
| Carga de las dos skills | 50.401 caracteres, incluyendo envoltorios y listado de recursos |
| Mayor proxy de entrada por llamada | 109.212 tokens: input + cache-read + cache-write reportados |
| Entrada acumulada reportada | 265.005 input y 1.370.368 cache-read |
| Despachos / cambios | 0 / 0 según sesión y reporte final |

El acumulado cuenta procesamiento repetido entre llamadas; no representa la
ventana de contexto. El proxy máximo no es una medición independiente del
prompt completo. Esta sesión no demuestra ahorro en un desarrollo terminado.

## Hallazgos

1. **Reconocimiento del proyecto posible, pero innecesariamente ruidoso.** La
   sesión abrió desde un repositorio contenedor y encontró pronto el repo de
   desarrollo anidado. Ese layout es legítimo; no hay razón para imponer que
   el directorio inicial sea la raíz del proyecto. Fallaron consultas que
   asumían inicialmente que los documentos estaban en el directorio de sesión.

2. **Continuación de epic confundida con reanudación de ejecución.** El state
   indicaba reposo legítimo y la última feature cerrada. Aun así se intentó
   `resume` sobre esa ejecución histórica. Su checkpoint referenciaba el plan
   anterior y el control rechazó el hash cambiado. El rechazo es correcto para
   esa reanudación; no prueba que iniciar la feature siguiente esté bloqueado.
   `sources/roles/orchestrator.md` y `skills/cdad-cycle/SKILL.md` prescriben
   `resume` al empezar una sesión sin expresar suficientemente esta distinción.

3. **CLI y evidencia de errores.** Hubo llamadas sin los argumentos requeridos
   y una ruta relativa rechazada. Los comandos canalizaron salidas a `tail`
   y luego imprimieron `$?`: apareció `RC=0` aunque el programa había fallado.
   El agente sí leyó los errores y no declaró esos pasos exitosos, pero ese
   patrón no produce evidencia fiable del código de retorno del programa.

4. **Carga tardía y voluminosa del procedimiento.** Las skills se invocaron
   después de que el usuario preguntara por ellas, unos 4 min 30 s después de
   iniciar. Antes se investigaron ayuda, estructuras e historial de ejecuciones.
   La carga completa agregó unos 50 mil caracteres. Esto requiere una entrada
   operativa clara y proporcional, no simplemente exigir más lecturas.

5. **Una incógnita de aceptación se convirtió en investigación global previa.**
   El plan leído en la sesión nombraba un proyecto consumidor por abreviatura.
   La búsqueda ya mostró una carpeta coincidente, pero el agente investigó
   otros proyectos y memorias generales y terminó declarando la identidad
   desconocida. Incorporó datos privados de infraestructura sin necesidad
   para el encargo. No se observó su publicación, pero sí entrada al contexto.
   Identificar el consumidor era útil para la aceptación; no era necesario
   resolverlo por completo antes de delegar el discovery del producto genérico.

6. **Reconocimiento correcto sin ejecución consecuente.** El agente detectó
   que faltaban las nuevas features en `epic_features`, que había autoridad
   delegada y que el usuario había ordenado avanzar. Al parar volvió a pedir
   confirmación del orden ya establecido. Respetar el stop fue correcto;
   convertir un orden vigente en una nueva aprobación no aporta control.

## Qué funcionó

- Se identificaron el plan nuevo y la próxima feature; se detectó el desfase
  del state sin fabricar aprobaciones ni alterar contratos.
- Se verificó el marcador de la instalación v9 y la igualdad de la skill
  de ciclo instalada con la del repo. No hay evidencia en esta sesión de que
  una instalación vieja haya sido la causa del resultado.
- No se encontraron rechazos de permisos en las 41 llamadas. Los fallos
  visibles fueron de ruta, argumentos y vigencia de un checkpoint histórico.
- Se respetó la orden de parar y se informó que no hubo cambios.

## Cambios de diseño a considerar

**Reconocimiento único y salida compacta.** Identificar proyecto y versión,
estado resumido, autoridad, unidad siguiente y obligaciones pendientes. Separar
hechos actuales de historial. El directorio de sesión es una pista, no una
norma sobre el layout del usuario.

**Ramas explícitas de continuación.** Con una ejecución activa se reconstruye
y reconcilia su trabajo cuando corresponde. Entre features se confirma el
cierre anterior y se abre la siguiente desde el plan vigente, sin reanudar
por defecto la ejecución cerrada. Sin contexto inicial se hace bootstrap.

**Criterio para delegar.** Cuando existen objetivo, autoridad, contrato aplicable
y entradas suficientes, despachar el discovery. Trasladar al encargo las dudas
que ese rol debe resolver. Preguntar tempranamente por una decisión realmente
indispensable; no investigar el espacio global para evitar una pregunta breve.

**Distribución propuesta dentro del plan existente:** 005-006 cubre arranque,
reconocimiento y encargos suficientes; 005-003, lectura compacta y selección
del camino de continuidad; 005-002 reproduce estas medidas. Su primer adaptador
debe contemplar que esta sesión está en `session_v2`/`session_message`, no en las
tablas legacy `session`/`message`/`part`; un esquema no soportado se diagnostica.
No crear un ciclo nuevo por cada síntoma ni imponer un tope arbitrario de llamadas.

## Cambios posteriores y límites

Al revisar el repositorio, la fila actual de 005-006 ya describe un proyecto
consumidor elegido por el dueño e identificado localmente, sin la abreviatura
del encargo original. Esa corrección evita una ambigüedad del caso; no reemplaza
la distinción entre continuar el epic y reanudar una ejecución.

No se reprodujeron los comandos ni se auditó toda la instalación. La ausencia
de cambios está respaldada por el reporte y las operaciones observadas, no por
una comparación independiente de todos los archivos del servidor. Se omiten
identificadores de sesión, rutas personales, proyectos externos y datos de
infraestructura. Las secuencias relevantes del registro fueron 36 (state),
101–127 (CLI/continuidad), 142 (skills), 198–272 (búsqueda del consumidor) y
287 (reporte después del stop).

## Segundo intento: despacho después de orientación excesiva

Caso anonimizado S-BOOT-03, misma fecha y versión de OpenCode. La solicitud
nombró explícitamente 005-006, pidió cargar las dos skills y pasar al architect
la evidencia del primer intento. Corte del análisis: primera delegación;
no se evalúa aquí el discovery posterior ni el cierre de la feature.

| Medida hasta el despacho | Observación |
|---|---|
| Pedido → inicio efectivo de la herramienta de delegación | 10 min 8,6 s |
| Herramientas antes de delegar | 61 |
| Distribución | 44 shell, 12 read, 2 skill, 2 write, 1 glob |
| Lecturas directas del state histórico | 3 fragmentos, 161.857 caracteres de salida |
| Total de texto devuelto por herramientas antes del despacho | 377.958 caracteres, incluidos envoltorios |
| Máximo proxy de entrada reportado antes del despacho | 174.758 tokens, incluido cache-read |
| Resultado en ese corte | Ejecución nueva y paquete preparados, validadores verdes, `begin` escrito, architect iniciado |

Tiempo calculado con el mensaje del usuario y `time.ran` de la herramienta de
delegación; no con la hora inicial del mensaje que anunció el despacho. Las
cifras describen esta muestra, no un promedio ni un presupuesto obligatorio.

### Dinámica observada

- Encontró el proyecto anidado en unos 16 segundos. La búsqueda de raíz no
  explica los diez minutos posteriores ni justifica imponer otro layout.
- Cargó las skills en el primer minuto, pero antes leyó state y otros archivos.
  Luego continuó leyendo los fragmentos históricos del state hasta que empleó
  una proyección compacta de sus campos. La carga temprana de skills no bastó.
- Verificó correctamente que el CLI instalado coincidía con la versión esperada.
  Antes probó buscar un repositorio Git en la instalación y ejecutar el archivo
  Python directamente; esos fallos no fueron denegaciones del arnés.
- Entre aproximadamente los minutos 2 y 5 investigó código interno: parsing
  de inputs, construcción del request, defaults, identificadores de ejecución,
  serialización del state, registros de despacho y estructuras de continuidad.
  También reconstruyó el orden operativo a partir de archivos y fechas de una
  ejecución anterior. El usuario había pedido operar, no auditar el CLI.
- Interpretó inicialmente que los agentes derivados eran viejos porque diferían
  de los globales. Después comprobó que el manifest ligaba correctamente fuente
  y derivado y que otras diferencias provenían del perfil de instalación.
  Un diff bruto y el mtime no prueban incoherencia: la derivación transforma
  precisamente esos archivos.
- Sincronizó el state alrededor del minuto 7, preparó el paquete y realizó las
  comprobaciones y el checkpoint previos al despacho. Llegó a un resultado
  operativo sin fabricar aprobaciones; la demora no fue toda improductiva.

### Interpretación y siguiente acción propuesta

Se repite el patrón incluso con un encargo más preciso y la evidencia previa
como insumo. Hay errores de criterio del agente y una entrada operativa que
no logra evitar que éste reconstruya los detalles del producto para usarlo.
La investigación del CLI compensa un recorrido poco claro; las verificaciones
de versión y derivación, razonables en principio, se expanden sin una pregunta
material pendiente ni un criterio explícito para darlas por suficientes.

Priorizar dentro de 005-006 el recorrido de esta misma continuación: reconocer
proyecto, obtener solo los hechos actuales, distinguir reposo de reanudación,
confirmar la procedencia con el mecanismo previsto y despachar discovery con
el encargo suficiente. Si el procedimiento documentado no permite hacerlo,
registrar la duda precisa y resolverla o delegarla; no estudiar por defecto la
implementación completa del arnés.

Ofrecer ejemplos operativos comprobados de inicio de feature y continuidad,
con sintaxis y resultados suficientes para ejecutarlos desde la instalación.
Los mecanismos existentes deberían exponer la proyección y referencias que
necesita el orquestador, sin imponer otro controlador ni duplicar estado.

No convertir estas cifras en una prohibición de superar cierto número de
lecturas. El criterio es funcional: cada comprobación debe resolver una duda
que afecte el próximo despacho. Una vez satisfecha, el proceso avanza. Medir
el tiempo hasta delegar junto con la suficiencia del encargo y el retrabajo
posterior, para no obtener un arranque veloz a costa de trabajo mal definido.
