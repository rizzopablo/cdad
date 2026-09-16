# CDAD: primer relevamiento de sesiones reales

Fecha: 2026-09-16. Investigación de solo lectura; no es una review del código
del cliente ni una certificación de gates. Prioridad del usuario: tiempo,
contexto necesario, costo. No se ejecutaron agentes ni tests en el servidor.

## Resultado principal

La primera mejora a evaluar es detectar ejecución sin progreso. Una review
repitió 1.194 veces el mismo comando, con salida idéntica y exitosa, durante
50,9 minutos y terminó abortada. Acortar instrucciones por sí solo no aborda
este fallo. También hay crecimiento considerable de contexto en el orquestador,
rechazos de permisos y uso de la misma familia de modelo en implementación y
review.

La hipótesis de recarga de `cdad-cycle` en cada turno **no se confirmó**:
se observaron 65 cargas mediante la herramienta `skill`, en 65 sesiones distintas.

## Fuente y alcance

Se consultó SQLite con `mode=ro`, `query_only=ON` y transacciones de lectura.
Tablas: `session`, `message`, `part`; se inspeccionó el esquema y se comprobó
que `session_message` no contiene filas para la selección. No se leyeron datos
de tablas de cuentas, credenciales o enlaces compartidos.

Selección por directorio del proyecto documental y repositorio enlazado,
extendida a descendientes por `parent_id`: 85 sesiones, 6 raíces, 5.575 mensajes
y 22.390 partes. Los datos encontrados tienen el directorio documental como
directorio de sesión aunque las herramientas trabajen en otros repositorios.
Se contaron mensajes una sola vez, sin sumar nuevamente los totales de sesión.

OpenCode instalado: 1.18.30. Las sesiones registran versiones 1.18.23 y 1.18.30.
El modelo observado es `glm-5.3-flash`, no `glm-3.5-flash`, con proveedores
`mofgw` y OpenRouter; también aparecen otros modelos en algunos mensajes.

Los metadatos completos permanecen en almacenamiento temporal privado fuera
del repositorio. Este informe omite host, usuario, cuentas y rutas privadas.
Los IDs de eventos permiten contrastarlo nuevamente contra la base original.

## Muestra principal: desarrollo del módulo de camiones

Raíz: `ses_fa96be182ffe8Kb37m9ylm5AUs`. Abarca varias features y correcciones,
no una sola feature aceptada; por eso no se calcula todavía costo por feature.

| Indicador | Registro observado |
|---|---:|
| Sesiones de la familia | 79: raíz + 78 hijas |
| Mensajes de asistente | 4.869 |
| Llamadas de herramientas | 6.256 |
| Herramientas con estado `error` | 290 (4,6 %) |
| Tokens `input`, sumados entre mensajes | 51.191.140 |
| Tokens `cache.read`, sumados entre mensajes | 726.106.698 |
| Tokens `output` | 1.126.353 |
| Tokens `reasoning` | 1.683.864 |
| Unión de intervalos de mensajes de asistente | 59,96 h |
| Suma de duración de llamadas `task` | 47,35 h, incluida en otros intervalos |

Las 78 hijas se distribuyen en 30 test-writer, 25 implementer, 11 reviewer,
7 scribe y 5 architect. El período de mensajes ocupa aproximadamente 9,77 días
desde el inicio de la raíz. Eso no equivale a 9,77 días de trabajo activo.

La unión temporal evita contar dos veces intervalos solapados padre/hijo.
No mide inferencia pura: los mensajes incluyen esperas de herramientas y de
subagentes. **No sumar las 47,35 h a las 59,96 h.** Los tiempos fuera de estos
intervalos no se clasifican automáticamente como espera humana.

El campo `cost` suma 18,5752 para esta familia (6,3229 vía `mofgw` y 12,2523
vía OpenRouter). Es un contador de OpenCode sin conciliación con facturación,
moneda ni tarifas del gateway: no se presenta como costo monetario real.

## Hallazgos con evidencia

### 1. Bucle de review sin progreso confirmado

Sesión `ses_fa57cfcc3ffecoJf8lsRCIImS4`, review de feature `001-002`:

- 1.204 llamadas `bash`; 1.194 repiten exactamente una búsqueda de `sudo`
  sobre los mismos dos módulos, sin cambiar argumentos.
- Esas 1.194 llamadas abarcan 597 mensajes, todas `completed`, salida de
  405 bytes idéntica por SHA-256 y código de salida 0.
- Desde `prt_05a83484c0016aRhFwtM6VUT5i` hasta
  `prt_05ab1e51b001YrN4s6E75zu1q2`: 50,91495 minutos, el 2026-09-01 UTC.
- Último mensaje `msg_05ab1e606001N1IBk4brEoRj87`:
  `MessageAbortedError`. La delegación correspondiente terminó
  `Tool execution aborted`; no hubo veredicto final en esa sesión.
- La repetición representa el 19,1 % de todas las llamadas de herramientas de
  la familia. No representa ese porcentaje de tiempo ni de costo total.

Propuesta para especificar: detectar repetición de acción y resultado sin nueva
evidencia ni cambio de estado, detener el bucle con diagnóstico y devolver
control al orquestador. Distinguir polling legítimo y repeticiones justificadas.
El umbral requiere calibración. No atribuir todavía la causa a contexto, modelo
o instrucciones; el síntoma está probado, la causa raíz no.

### 2. Contexto elevado concentrado en la raíz

Proxy de entrada por mensaje: `tokens.input + tokens.cache.read +
tokens.cache.write`, excluyendo registros de entrada nula. Para la raíz:
mediana 332.693 y máximo 904.206 tokens reportados. Para toda la familia:
mediana 103.176. Son contadores reportados por el proveedor/runtime, no una
medición independiente del texto ni una prueba de capacidad efectiva del modelo.

El máximo corresponde a `msg_088192b65001OVDM3ymdH88K3E`: input 270,
cache.read 903.936. Se contrastó contra su único `step-finish`, con cifras
idénticas; no es una suma de varios pasos de ese mensaje.

La raíz registra 28.540.697 tokens `input` y 345.255.242 de lectura de caché
a través de sus mensajes. Caché puede abaratar reutilización, pero no convierte
el contexto lógico en pequeño. Se observaron dos partes `compaction` consecutivas
el 2 de septiembre; no prueban dos recuperaciones satisfactorias ni permiten
reconstruir por sí solas la política de compactación.

Propuesta: medir checkpoints por feature, handoffs acotados y reconstrucción
de sesión; conservar decisiones, permisos y referencias a evidencia.

### 3. Fricción de permisos y fallos del proveedor

En las 85 sesiones se clasificaron 236 errores `bash` cuyo texto indica
restricciones de permisos. La clasificación se basa en el mensaje de error,
no en inferencias por código de salida. No son 236 fallos de tests.

Las siete delegaciones con error de la familia principal incluyen tres
ejecuciones abortadas, una cancelación, un reset de conexión, un error upstream
y un límite de crédito/salida máxima. Deben separarse de retrabajo funcional.

Propuesta: verificar capacidades y comandos legítimos por rol antes del piloto,
manteniendo las restricciones de edición/lectura. No abrir permisos globales
para eliminar los rechazos. No se cuantifica todavía el tiempo perdido por ellos.

### 4. Misma familia de modelo en implementer y reviewer

Los 1.785 mensajes de implementer y los 854 de reviewer de la muestra usan
GLM-5.3-flash. Cambiar entre `mofgw` y OpenRouter no cambia la familia del modelo.
Por ejemplo, la review `ses_fa57cfcc3ffecoJf8lsRCIImS4` y la implementación
`ses_fa522e331ffea3X7Z9Ivc4zbpX` pertenecen a la feature `001-002`.

Esto no satisface el invariante de diversidad de familias de la metodología
cargada actualmente. No equivale a demostrar que el código sea incorrecto.
La línea base del piloto debe verificar garantías, además de medir velocidad;
no considerar equivalente una variante rápida que relaje esos controles.

### 5. Corregir la hipótesis de recargas y dimensionar tests

`cdad-cycle`: 65 cargas explícitas en 65 sesiones, cero repeticiones dentro de
la misma sesión por la herramienta `skill`. Sus respuestas suman 2.156.894
bytes distribuidos entre sesiones; no son tokens ni contexto simultáneo.
Esto no descarta cargas por otros mecanismos, pero no respalda «recarga por
turno» como prioridad empírica para esta muestra.

Se detectaron 26 repeticiones adicionales de `read` con mismos argumentos y
misma salida dentro de una sesión, agrupadas en 16 grupos. Pueden ser legítimas
tras pérdida de contexto; la mera repetición no demuestra desperdicio.

Una búsqueda heurística de comandos de tests encuentra 339 candidatos y 5,75 h
de duración acumulada. **No son 339 suites completas**: incluye comandos que
mencionan tests, diagnósticos y ejecuciones rechazadas. Hace falta clasificarlos
y vincular selección, resultados, revisión y entorno antes de proponer ahorro
por reutilización de evidencia.

## Diferencia de versiones: requisito previo para el piloto

El checkout de CDAD encontrado en el VPS está en `main`, revisión `4aa2b02`
del 2026-08-30. La skill instalada en las dos ubicaciones consultadas tiene
SHA-256 `d3074b7a7ddc48530a7229d1896aa8314b19302184dd1f3ad68d55cb37ddf5fc`.
Difiere de la skill local de `translation-en` (`eb3a511`), cuyo hash es
`a75990c8639592eaea7d2236f2531875c1de43cc8e05f40dcf7a62b056664e5f`.

Esto confirma divergencia actual, pero no identifica automáticamente la revisión
de cada archivo instalado ni la que estaba cargada en cada sesión histórica.
El repositorio local contiene correcciones posteriores de permisos/delegación
(`cdad-010`); no atribuir a la versión actual todos los incidentes de septiembre.
No se actualizó ni reinstaló CDAD en el servidor durante este relevamiento.

## Consecuencia para el epic

Mantener la línea base como primera entrega, ampliada con este análisis
retrospectivo. Antes de fijar el resto del alcance:

1. Fijar revisión e instrucciones efectivas y comprobar compatibilidad de roles
   en el VPS; separar incidencia histórica de comportamiento actual.
2. Especificar detección/recuperación de bucles sin progreso con este caso como
   regresión y con casos de polling legítimo para evitar cortes incorrectos.
3. Evaluar continuidad/checkpoints del orquestador y paquetes por rol.
4. Clasificar ejecuciones de tests y correcciones por feature para obtener
   tiempo hasta aceptación y evidencia reutilizable.
5. Medir simplificación de instrucciones; no usar recarga por turno como
   justificación demostrada. Conciliar costo solo después de los dos objetivos
   prioritarios y con tarifas/contadores verificables.

El plan sigue siendo un borrador. Este estudio no ejecuta las optimizaciones,
no modifica la política vigente y no demuestra todavía un porcentaje de ahorro.
