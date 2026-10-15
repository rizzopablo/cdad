# Delegación interoperable entre agentes CLI y políticas de proyecto

Fecha: 2026-10-10. Propuesta para reconciliar después del cierre de 005-006.
No es una spec aprobada ni modifica el plan, el state o el ciclo activo.

Prioridad del dueño: habilitar el consumidor Perl y la orquestación entre
agentes. El diseño general no debe retrasar ese primer uso real.

## Resultado buscado

Un agente autorizado, desde cualquier CLI compatible, puede preparar un encargo
CDAD, delegarlo a otro CLI compatible con el rol y proyecto correctos y recibir
un resultado verificable. El protocolo es común; las particularidades de cada
CLI viven en su adaptador. No se reconstruyen scripts por proyecto ni por cada
pareja de herramientas.

OpenCode, Claude Code, Codex y Pi son destinos posibles del diseño, no una
declaración de compatibilidad ya comprobada. El usuario puede elegirlos como
coordinador o ejecutor cuando sus capacidades requeridas estén verificadas.
Cambiar de CLI no cambia el contrato, el rol, el alcance ni la autoridad.

Primer recorrido consumidor: proyecto Perl/Webmin, con implementación bajo
`webmin-module/<module>/` y tests en su subdirectorio `t/`. Es un caso de uso,
no una nueva convención obligatoria de CDAD. Claude → OpenCode es el primer
recorrido consumidor. OpenCode → otro CLI debe usar el mismo contrato y sirve
para comprobar que el diseño no quedó atado a un coordinador particular.

## Arquitectura propuesta: contrato común y adaptadores

Separar cuatro decisiones: **rol CDAD**, **CLI ejecutor**, **modelo** y
**mecanismo de delegación**. Un reviewer sigue siendo reviewer aunque se
ejecute en otro CLI. Dos CLI distintos pueden usar la misma familia de modelo;
el cambio de herramienta no demuestra independencia de modelos ni aislamiento
de información.

El recorrido común es:

`agente autorizado → encargo canónico → adaptador del CLI destino → sesión de rol → resultado durable → re-entry del responsable`

Se implementa un adaptador por CLI destino, invocable desde los coordinadores
compatibles; no un script para Claude→OpenCode, otro para OpenCode→Claude y
otros para cada combinación. El coordinador necesita un mecanismo soportado
para lanzar el adaptador y recibir su resultado. Si no dispone de ejecución,
el handoff manual conserva el contrato sin fingir automatización.

### Encargo y entrega

Reutilizar el paquete, el registro de despacho y el recibo existentes. Los
datos siguientes son responsabilidades del contrato de interoperabilidad;
antes de añadir campos hay que ubicar los que ya existen en CDAD:

| Entrada común | Salida común |
|---|---|
| Identidad de encargo/intento y responsable de recibirlo | Identidad del intento y referencia de sesión/proceso cuando exista |
| Proyecto explícito y paquete canónico con sus insumos y alcances | Entrega final del rol y referencias a artefactos/evidencia |
| Rol y autoridad delegada | Terminación: completado, bloqueado, error, timeout o cancelación |
| CLI destino y configuración solicitada | Configuración efectiva observada, o desconocida explícitamente |
| Ubicación local de resultados y política de espera/cancelación | Logs durables y diagnóstico con siguiente acción legítima |

La terminación del proceso y la suficiencia de la entrega son hechos distintos:
«completado» no equivale a «gate aprobado». El responsable del ciclo hace el
re-entry. Un fallo de transporte tampoco prueba que el worker no haya escrito
nada: antes de repetir, reconciliar sesión, artefactos y efectos disponibles.

El adaptador adapta invocación, carga de rol y transporte, sin reescribir el
contrato para cada herramienta. Puede usar un envoltorio específico del CLI,
separado del paquete canónico y sin ampliar su alcance. Si el destino no puede
respetar una capacidad necesaria, debe declararlo antes del despacho y ofrecer
un camino soportado; no caer silenciosamente a un agente genérico.

### Autoridad y posibles delegaciones sucesivas

«Cualquier agente puede delegar» describe una capacidad disponible, no una
autorización universal para cualquier rol. El worker puede solicitar ayuda;
solo puede despacharla si el encargo le delega esa decisión y el entorno la
soporta. Una delegación hija no obtiene más acceso, escritura o autoridad que
lo autorizado para la tarea. Si requiere información incompatible con su rol
—por ejemplo, implementación durante RED—, vuelve al responsable del ciclo.

La fuente vigente incluye una prohibición de spawn desde subagentes ligada a
un incidente y un mecanismo concreto. Este diseño requiere reconciliar esa
regla: conservar la prohibición donde el runtime no lo soporta, y distinguirla
de una delegación externa autorizada. No reemplazarla por recursión ilimitada
ni mantenerla como veto universal que contradiga el nuevo recorrido legítimo.

Para el primer aterrizaje basta coordinador→worker, con devolución al
coordinador y sin delegación recursiva automática. La misma herramienta puede
ser coordinador en un encargo y worker en otro. Si más adelante se permiten
cadenas, registrar padre/responsable y acotar su profundidad, coste o tiempo
según el mandato, con diagnóstico útil cuando se alcance el límite. Los valores
no son constantes universales de la metodología.

El orquestador del ciclo conserva la propiedad del state y la decisión sobre
gates. No compartir esa escritura entre todos los CLI ni habilitar múltiples
paquetes activos mediante un dispatcher: cualquier paralelismo futuro debe
reconciliar primero el modelo de estado existente.

### Capacidades y contexto

Un adaptador declara qué soporta: sesión nueva de rol, carga de política del
proyecto, selección de modelo, salida final capturable, identificación de
sesión, espera, cancelación y recuperación. Distinguir lo documentado de lo
probado desde la instalación real. Una capacidad opcional ausente no bloquea
otros recorridos legítimos: sin callback, por ejemplo, puede usarse una espera
soportada. No construir un catálogo exhaustivo de comandos ni repetir un probe
completo en cada delegación; reutilizar verificaciones vigentes hasta que cambie
la instalación o la configuración relevante.

Cada sesión recibe el paquete y sus insumos suficientes, no la conversación
completa del coordinador. La entrega al coordinador incluye resumen útil y
referencias a evidencia completa local, sin volcar logs enormes al contexto.
El sistema adapta el modo de cargar el rol a cada CLI y declara los límites de
aislamiento; un proceso separado por sí solo no impide acceso al repositorio.

## Hechos comprobados y límites

1. Los agentes globales instalados contienen defaults de `src/`, `lib/`,
   `tests/` y ciertas convenciones de nombres. No describen por sí solos
   el layout Perl del consumidor. CDAD **ya tiene** clasificación por
   `path_policy` y publicación de agentes derivados: no hace falta mantener
   agentes Perl manuales ni añadir otro catálogo global de extensiones.
2. Se ejecutó una sonda contra el CLI **instalado**, sin tocar el consumidor:
   `implementation_roots: [webmin-module/module]` y
   `test_roots: [webmin-module/module/t]`. Clasificó `.pl`/`.cgi` como
   implementación y `t/basic.t` como tests; el implementer obtuvo deny de
   edición sobre `t/**` y el test-writer allow de edición sobre ese árbol.
   **Brecha real:** el mapa de lectura del test-writer solo emitió deny para
   la raíz de implementación, sin excepción para `test_roots` anidada. Puede
   impedir que el test-writer lea sus propios tests. El remedio debe respetar
   la prioridad del clasificador y conservar los denies de rutas privadas.
3. La sonda anterior comprueba clasificación y reglas generadas, **no**
   la mediación efectiva de un proceso OpenCode. Las lecturas por shell/grep
   tampoco quedan aisladas por una regla de `read`. No se promete sandbox.
4. El consumidor carece de `docs/cdad-policy.json` y sus exclusiones Git
   actuales no cubren los derivados y metadatos locales de CDAD.
5. La instalación operativa consultada es v9, `7f66619`, con artefactos
   declarativos de formato V1. OpenCode V2 documenta normalización de sintaxis
   V1 soportada: **el formato antiguo no prueba que esté ignorado**. Hay que
   comprobar configuración efectiva, advertencias y operaciones reales.
   Fuente: [migración oficial](https://opencode.ai/v2/docs/migrate-v1/).
6. OpenCode documenta servidor compartido y `--standalone` con servidor privado.
   Esa opción es una elección del adaptador; no reemplaza verificar versión,
   agente, modelo y contexto de proyecto cargados.
   Fuente: [CLI oficial](https://opencode.ai/v2/docs/cli).
7. No se comprobó aquí el script previo, su callback ni el estado de los
   servidores permanentes. El ejecutable no estaba disponible en el PATH de
   esta sesión de análisis. No se lanzaron workers ni se usaron credenciales.

## Qué pertenece a cada nivel

| Nivel | Responsabilidad |
|---|---|
| Metodología | Separación de roles, contrato suficiente, autorización, evidencia proporcional, re-entry y decisiones ante obstáculos. |
| Proyecto | Layout de código/tests/docs, privacidad, comandos de validación, autorizaciones de entorno y ubicación permitida de artefactos locales. |
| Runtime/adaptador | Carga y precedencia de agentes, formato de permisos, selección efectiva de rol/modelo, transporte del paquete y recepción del resultado. |
| Instalación/ejecución local | Binario, rutas absolutas, proveedor concreto, servidor utilizado, callback disponible y valores iniciales de timeout. |

La restricción de no comunicar agentes mediante `/tmp` es del proyecto. No
debe convertirse en una prohibición global de CDAD. Los tiempos y modelos
concretos tampoco son requisitos universales de la metodología.

## Unidad propuesta

Propuesta reconciliada en dos entregas: **005-008-project-path-capabilities**
y **005-009-cli-delegation**, en ese orden. La delegación ya no usa el ID
provisional 005-008 de la primera versión de este finding.
Plan de continuación: [prioridades Perl y CLI](../docs/epics/epic-005-real-operation/priority-perl-cli-plan-2026-10-10.md).
Aplicar al epic aprobado y al state mediante el orquestador, tras la aprobación
del dueño contenida en el encargo de continuación; no activar desde este finding.
No confundirla con 005-004, que contempla roles usados desde Claude Code.
La interoperabilidad con un CLI como worker es distinta de soportar toda la
metodología de forma nativa en él. Compartir componentes y evidencia con
005-004, sin duplicar bootstrap de 005-006 ni dar soporte nativo por supuesto.

### A. Política y permisos derivados

- La política versionada declara raíces concretas, incluida una raíz de tests
  anidada en implementación. No autorizar indiscriminadamente cualquier `t/`
  o archivo `.t` del repositorio por ser Perl.
- Corregir la excepción de lectura coherentemente con clasificación/edición.
  Verificar también auxiliares legítimos del árbol de tests y rutas privadas.
- El producto instalado debe demostrar que el test-writer puede leer/escribir
  tests y no leer implementación mediante las herramientas mediadas; que el
  implementer puede editar código y no tests; y que lectura/medición/validación
  legítimas siguen disponibles.
- Declarar límites de shell, búsqueda y otras herramientas. Mantener la política
  de autonomía supervisada, sin reintroducir allowlists extensas por comando.

### B. Despacho externo y recepción

Reutilizar primero el mecanismo existente que funcione. Si falta un adaptador,
darle una interfaz mínima: proyecto, paquete, rol y configuración de ejecución;
resultado final, identificación de intento/sesión y causa de terminación.
Mantener la interfaz común independiente del coordinador; el primer adaptador
implementa el destino OpenCode y el segundo demuestra la dirección inversa
desde OpenCode hacia un CLI disponible. Elegir ese segundo destino después de
verificar sus capacidades y coste; no exigir implementar todos a la vez.

- Usar `prepare` y paquetes canónicos. Transportar el paquete íntegro, sin
  añadir por fuera otra plantilla de procedimiento o las reglas del proyecto.
- Un proceso externo debe poder seleccionar efectivamente el rol CDAD. No
  asumir que un perfil `mode: subagent` puede elegirse como agente principal
  del CLI; verificarlo o usar el camino soportado. Ningún fallback silencioso
  a un agente genérico.
- Proyecto explícito e independiente de dónde esté la sesión del coordinador.
  Evidencia de los agentes/configuración cargados, no solo de archivos presentes.
- Modelo configurable por ejecución o rol, sin fijar un proveedor en CDAD.
  Registrar configurado y observado, o desconocido. Aplicar la independencia
  que exija el mandato del proyecto; no relanzar aquí el debate de tiering.
- Separar éxito del proceso, entrega del rol y aprobación del gate. `rc=0`
  sin resultado final suficiente no cierra la tarea; una entrega bloqueada
  puede ser correcta y útil sin ser una implementación completada.
- Si se usa background, probar que el proceso sobrevive a la devolución de
  control y que la finalización realmente llega al coordinador. Callback,
  timeout, cancelación y reconexión deben tener recuperación documentada.
  Sin callback probado, usar una espera soportada o comprobaciones espaciadas;
  nunca prometer una notificación que no existe.
- Reusar el ledger, receipts y reconciliación existentes para evitar efectos
  duplicados; no construir otra base de estado del ciclo dentro del dispatcher.

### C. Privacidad y configuración portable

- `docs/cdad-policy.json` y contratos canónicos permanecen versionados y
  publicables. Manifests con paths absolutos, logs crudos y conexiones privadas
  son locales. Proponer exclusiones antes de generar esos artefactos.
- No ignorar automáticamente toda `.opencode/` si contiene configuración
  compartida legítima. Excluir derivados/metadatos locales y conservar lo que
  el proyecto decida versionar. Evaluar `.cdad/` y el directorio de ejecución
  local según su contenido; trasladar al handoff público solo evidencia
  necesaria y anonimizada.
- Resolver el directorio de paquetes/logs desde la organización declarada por
  el proyecto. Ni `var/logs/` ni un directorio temporal concreto son universales.
- Las instrucciones privadas de un entorno externo no se copian a contratos
  públicos. El paquete contiene la restricción y referencias autorizadas
  suficientes, sin datos de acceso ni nombres privados.

## Entrega urgente para iniciar el consumidor

Dos resultados, entregables por separado si eso facilita su construcción y
review. Mantenerlos juntos solo si el discovery confirma un ciclo pequeño.
La cantidad de features no es una condición de aceptación.

### 1. Soporte efectivo del proyecto Perl/Webmin

- Preparar la política desde el layout existente: implementación `.pl`/`.cgi`,
  tests `.t` y auxiliares en el árbol de tests declarado. Conservar las
  convenciones del consumidor, sin imponer `src/` o `tests/`.
- Corregir la brecha de lectura de tests anidados y comprobar desde el producto
  instalado que test-writer y implementer tienen las capacidades necesarias y
  las barreras de lectura/edición mediadas que corresponden a sus roles.
- Declarar en el proyecto cómo se comprueba sintaxis y cómo se ejecutan tests
  focales y regresión. No basta con autorizar extensiones: el entorno necesita
  intérprete, runner y dependencias adecuados. Si faltan, reportar la capacidad
  ausente y su resolución legítima, sin operar producción para obtenerla.
- Dar a los roles las convenciones y referencias Perl/Webmin pertinentes al
  encargo. Reutilizar especialización existente cuando sirva; no crear agentes
  manuales por lenguaje ni cargar documentación de dominio entera por defecto.
- Verificar el recorrido con una tarea pequeña autorizada y evidencia útil;
  mantener proporcionalidad de tests y revisión. El smoke no autoriza por sí
  mismo la implementación del producto consumidor.

### 2. Primera orquestación entre CLI operativa

- Habilitar Claude como coordinador y OpenCode como worker mediante la interfaz
  común propuesta, reutilizando el dispatcher existente si satisface el
  contrato. Proyecto, paquete y rol explícitos; ninguna ruta de este servidor
  ni proveedor concreto pasa a ser requisito del producto.
- Comprobar una entrega real en sesión separada: configuración efectiva del
  rol, resultado final durable y recepción/re-entry del coordinador. Un worker
  bloqueado debe devolver un reporte útil, sin silencio ni reintento infinito.
- Usar una espera soportada y recuperación mínima comprobada. Callback,
  ejecución en background y notificación automática solo si ya son fiables o
  necesarios para ese recorrido; no construir un scheduler para arrancar.
- Mantener límites y clasificación de evidencia honestos: cambiar de CLI no
  garantiza otra familia de modelo ni un sandbox. El coordinador conserva
  state, autoridad y aprobación de gates.

**Criterio de disponibilidad para el consumidor:** ambos resultados funcionan
desde la versión instalada que se usará durante el ciclo. El proyecto puede
continuar con una instrucción breve y sus datos registrados, sin un nuevo
prompt extenso de excepciones ni parches particulares a agentes globales.

La dirección inversa OpenCode→otro CLI, más adaptadores, callbacks avanzados y
mayor concurrencia son ampliaciones posteriores. La interfaz debe admitirlos
desde el diseño, pero no bloquean este primer uso. Se conserva la intención
bidireccional sin exigir una implementación universal en la entrega urgente.

## Aceptación de la interoperabilidad ampliada y tamaño de los ciclos

1. Fixture Perl/Webmin y otro layout distinto se clasifican y derivan sin
   cambiar los agentes globales ni escribir variantes manuales.
2. Pruebas reales focales de capacidades positivas y barreras relevantes
   desde el producto instalado, con límites honestamente declarados.
3. Dos encargos pequeños usan la misma interfaz: Claude → OpenCode y
   OpenCode → un segundo CLI verificado. Cada uno llega al rol correcto y
   vuelve por `receive` con evidencia durable, sin scripts específicos por
   pareja. Se verifica la configuración efectiva, no se presume por el YAML.
4. Un fallo/interrupción se distingue del éxito y puede retomarse sin repetir
   efectos ni fabricar entrega. No simular un callback y declararlo real.
5. El consumidor puede iniciar discovery documental con su política y mandato;
   el primer RED usa el aislamiento de rutas corregido. Producción y desarrollo
   no autorizado siguen fuera de alcance.
6. Una revisión del diff destinado a publicación no incluye datos privados ni
   metadatos absolutos de la instalación. La evidencia sensible queda local.

7. La delegación no amplía alcances ni modifica state desde el worker. Ausencia
   de una capacidad necesaria devuelve un diagnóstico accionable; no dispara
   reintentos sin cambio de condiciones ni un fallback silencioso.

Primero medir lo ya resuelto por 005-006 y lo que ofrece el dispatcher existente.
Si solo quedan el defecto de raíces anidadas y una verificación de recorrido,
hacer un ciclo correctivo pequeño. Si hay que construir transporte, callback
y recuperación nuevos, separar ese adaptador de la corrección de permisos:
no acumular una plataforma de jobs en una feature preparatoria. Diseñar la
interfaz general ahora y aterrizar adaptadores gradualmente. Una verificación
bidireccional pequeña prueba la generalidad sin exigir una matriz completa de
todas las parejas de CLI ni repetir desarrollos enteros.

## Secuencia y restricciones

- Revisar la entrega final de 005-006 antes de planificar. En la consulta
  inicial había trabajo activo; al ajustar esta prioridad el state declara
  `active_feature: null`, `current_stage: idle` y el último paquete completado.
  Eso permite preparar la siguiente propuesta, sin presumir por el state que
  la entrega esté instalada ni que toda su aceptación haya sido revisada.
- Reconciliar el orden con el trabajo ya abierto de 005-002 y la feature
  005-004 pendiente. No asumir una cola antigua como vigente.
- Proponer el siguiente ciclo y resolver únicamente las brechas restantes.
  Ejecutarlo con la versión estable elegida; entregar/instalar la sucesora al
  límite del ciclo, sin cambiar la propia versión operativa a mitad de trabajo.
- Discovery documental del consumidor no tiene por qué esperar todo el
  adaptador. No abrir RED/implementación hasta contar con autorización real,
  contrato y aislamiento aplicable verificados.
- Fuera: plataforma universal de jobs, migración masiva de todos los runtimes,
  sandbox nuevo, recursión automática, scheduler paralelo nuevo, operación de
  producción, cambio de proveedor/modelo como
  optimización, instalaciones globales o publicación no autorizadas.

Esta propuesta conserva lo útil del diagnóstico recibido, pero trata el
bootstrap y las reglas del consumidor como configuración normal, y concentra
el desarrollo de CDAD en capacidad efectiva, interoperabilidad y recepción.
