---
epic_id: epic-005-real-operation
epic_name: Operación real y medición de contexto
created_at: 2026-10-08
status: approved
approved_by: Pablo
approved_at: 2026-10-08
---

# Epic 005: Operación real y medición de contexto

## Resultado buscado

El epic-003 dejó probado el mecanismo de continuidad (v7, `ce09ed0`). Falta la
evidencia de que un orquestador opera con menos contexto. Este epic pone en uso real
la versión instalada, hace que un proyecto arranque con una instrucción breve, mide el contexto que consume cada rol y recorta la orientación
del orquestador con esos datos. Al final, los roles quedan activos también en
Claude Code. Las cifras de ahorro no se presuponen: se miden.

## Alcance

- Dentro: publicación coherente de skills, agentes y CLI de la versión instalada; arranque guiado de proyectos; capacidades de rutas de proyecto para un consumidor con tests anidados (caso de uso: Perl/Webmin); delegación externa interoperable entre CLI (interfaz común y primer adaptador OpenCode); planificación progresiva; validador en
  reposo; lector de sesiones de OpenCode y medición de contexto por rol;
  reducción de las lecturas de orientación; activación de los roles en Claude Code.
- Fuera: CI, ANON-1, R2-STAGE, POLICY-CLASS, sandbox, plataforma universal de
  jobs y el resto de la deuda de 003-007 (siguen priorizadas para después).
  Cambios en instalaciones globales de HOME salvo decisión explícita del dueño
  (005-004 y las entregas entre ciclos). Comparaciones entre modelos.

## Entregas

| Orden | Feature | Resultado verificable | Dependencias |
|---|---|---|---|
| 1 | 005-001-idle-and-v7-bootstrap | Arrancar y continuar una feature legítimamente, sin registros ficticios ni encargos obsoletos. (a) El primer `prepare` publica los agentes de proyecto desde la raíz v7 (`source_dir` y hashes verificados; hecho el 2026-10-08). (b) Aprobación por rol: el architect se habilita con la aprobación del plan del epic; test-writer, implementer y reviewer exigen la aprobación de esa spec concreta (ruta y hash). (c) Reemplazo de un paquete preparado y no despachado cuyo contrato cambió: registra el motivo, conserva el anterior y prepara uno nuevo con la autorización vigente, sin aprobar el contrato nuevo; un paquete despachado sigue requiriendo reconciliación. (d) Mensajes de bloqueo que distinguen aprobación pendiente, paquete obsoleto y estado incoherente, y dicen qué falta y cómo seguir, sin habilitar atajos. (e) `validate-state` acepta un state en reposo legítimo y sigue rechazando uno incoherente (VALIDATE-IDLE). Prueba decisiva: discovery autorizado sin spec, construcción bloqueada hasta su aprobación y recuperación de un paquete obsoleto sin inventar evidencia; en uso real, el primer `prepare` de 005-002 sale sin atajos. | — |
| 2 | 005-005-adoption-coherence | Continuación correctiva de 005-001: preparar, corregir y despachar un encargo con la versión esperada y la validación proporcional, sin rodeos manuales. (a) El reemplazo valida también los insumos conservados y dice cómo ajustarlos. (b) Una sola política de tests en procedimiento, paquetes canónicos y encargos: la metodología define la evidencia (regresión proporcional, suite completa al cierre, reutilización de evidencia equivalente) y el proyecto declara los comandos; las condiciones locales se registran en la evidencia sin volverse requisito. (c) Procedencia de la instalación: el registro de activación es la fuente por defecto cuando existe, con camino explícito para proyectos sin activación o con otra instalación legítima; una contradicción se diagnostica, nunca cambia de versión en silencio. Documentación de 005-001 dentro de la tarea que corresponda: PD-17 enmendada, `review.md` normalizada, rutas personales fuera de los documentos del repo (originales en un registro local). Cierre: validación de integración desde una instalación aislada. Después: instalación nueva ligada a commit y manifiesto, activación del dueño y verificación de lo que carga una sesión nueva. | 005-001 |
| 3 | 005-006-guided-project-start | Una instrucción breve («usá CDAD para inicializar este proyecto y comenzar su análisis preliminar») basta para llegar a una primera delegación útil. El orquestador reconoce o inicializa el proyecto conservando lo existente (documentación, planes y convenciones propias, como los nombres de épicas y features); descubre requisitos y restricciones (stack, organización, privacidad, entorno de pruebas, límites operativos, autoridad) y los registra en su lugar canónico, creando solo lo que falte; distingue lo inferible de lo que decide el usuario y pregunta solo esto último; prepara encargos completos. El discovery parte de recorridos concretos de uso (de la petición inicial a la primera entrega), y el contrato obliga en las dos direcciones: el arnés da al rol insumos, capacidades y una salida legítima ante un bloqueo. No traslada el prompt largo a una plantilla. Aceptación: el arranque real de un proyecto existente parcialmente inicializado, elegido por el dueño (identificado en el registro local de la instalación, no en este repo) más comprobaciones pequeñas de proyecto nuevo y de configuración incompleta, sin depender de nombres, carpetas ni entorno de ese proyecto. Frontera con 005-003: 005-006 resuelve el arranque; 005-003, la orientación al retomar; comparten el mismo procedimiento de reconocimiento del proyecto. | 005-005 |
| 4 | 005-008-project-path-capabilities | Capacidades de lectura, edición y validación coherentes con la política del proyecto para un consumidor con tests anidados en implementación (primer caso real: Perl/Webmin). (a) Una política válida con tests anidados permite al test-writer leer y editar sus tests y auxiliares declarados, conservando el deny de lectura mediada sobre la implementación; el implementer edita implementación y no tests. (b) Clasificación y permisos derivados concuerdan con la prioridad vigente de `test_roots`/`test_files`, implementación y rutas privadas; incluye un caso focal de `test_files` bajo implementación y una excepción de tests nunca reabre una ruta privada. (c) Un segundo layout convencional funciona sin regresión; sin reglas globales `**/t/**` ni `**/*.t`. (d) El proyecto registra los comandos de sintaxis y tests Perl en su lugar canónico, con regresión proporcional y suite al cierre; los roles reciben las convenciones y referencias de dominio del encargo; una ausencia de intérprete, runner o dependencias produce diagnóstico útil, no cambios no autorizados en máquinas productivas. (e) El producto instalado demuestra las capacidades positivas y negativas mediante operaciones reales del runtime, sin presentar grep, shell o sesión separada como sandbox ni volver a allowlists por comando. No crea agentes Perl manuales ni otro sistema de políticas. | 005-006 cerrada y desplegada |
| 5 | 005-009-cli-delegation | Interfaz común de delegación externa y primer recorrido real Claude → OpenCode, con rol, proyecto, entrega y re-entry verificables. Un adaptador por destino (no un script por pareja de herramientas); rol CDAD, CLI y modelo son decisiones independientes; diseñada para otros CLI en cualquiera de las dos posiciones, sin exigir implementarlos todos. (a) Reutiliza paquetes, observaciones de despacho, ledger, receipts y reconciliación existentes; no crea otro state del ciclo ni reescribe las reglas del paquete. (b) El proyecto es explícito e independiente del directorio del coordinador; el worker usa el rol, la configuración y la versión esperados; se comprueba el modo de carga soportado, sin fallback silencioso a un agente genérico. (c) El worker recibe contexto suficiente y acotado, y devuelve su texto final y evidencia referenciada sin encadenar sesiones fuera de su mandato. (d) Distingue entrega completada, bloqueo del rol, error de transporte, timeout y cancelación; `rc=0` no aprueba un gate; timeout no prueba ausencia de cambios; tras una interrupción se reconcilian los efectos antes de repetir. (e) Ofrece espera o finalización realmente soportada y probada; no inventa señales de finalización ni sondea en bucle. (f) Configuración portable: selección de modelo, binarios, logs, servidores y tiempos en el nivel correcto; registra configurado/observado o desconocido, sin valores de este VPS en producto o contratos públicos. (g) Encargo pequeño real Claude → OpenCode → recepción CDAD desde la instalación elegida para la aceptación. Reconciliar la prohibición heredada de spawn desde subagentes: se conserva donde el runtime no la soporte y se distingue de la delegación externa autorizada; una delegación no amplía autoridad ni permite al worker escribir el state. | 005-008 para la aceptación conjunta del consumidor |
| 6 | 005-010-real-opencode-delegation | Continuación correctiva de 005-009: el adaptador OpenCode completa un recorrido real, no solo contra un doble de test. (a) La señal durable es una superficie que OpenCode realmente produce en la versión instalada (su base de sesiones en solo lectura, un export de la sesión o la salida estructurada del cliente), identificada sin ambigüedad con la sesión despachada; un esquema desconocido falla cerrado. (b) El modo de carga del rol como entrada no interactiva se resuelve con evidencia en la versión instalada, sin fallback a un agente genérico. (c) El transporte del paquete y la elección de servidor (privado o servicio de fondo) y de permisos son los que el CLI soporta de verdad, configurables en el nivel correcto. (d) Los tests usan un doble que reproduce el comportamiento observado de OpenCode, y una prueba de integración opcional corre contra el binario real. Aceptación: PD-10 de 005-009 — recorrido real Claude → OpenCode → `receive` → re-entry desde una instalación aislada de la versión nueva antes del despliegue, y confirmación corta desde la instalación global después del despliegue. Orquestada por Claude (ver `execution.md`). | 005-009 |
| 7 | 005-002-session-context-meter | Formato de medición neutral respecto del runtime y opcional para la metodología, que distingue datos observados, estimados y desconocidos; el desarrollo sigue aunque el entorno no exponga tokens. Primer adaptador: lector de solo lectura de las sesiones de OpenCode, que informa por sesión y por rol: tokens de entrada/salida, lecturas de archivos, llamadas a herramientas y momento del primer `resume`. Distingue contexto cargado por paso, procesamiento acumulado y costo. Aplicada a las sesiones de 005-001 y a la sonda 2 de 003-007, con salida reproducible. Muestras: la primera sesión de 005-001 y la sesión de cierre de 005-001 (unas 4 h, 13 subagentes, máximo de input informado por llamada del orquestador de unas 310 mil, caché incluida; medido por Codex). Línea base a reproducir (medida por Codex sobre la primera sesión de 005-001): unos 12,5 minutos, 101 llamadas a herramientas, una salida de más de 51 mil caracteres y unas 203 mil de entrada reportada en el último paso, caché incluida (carga de contexto de ese paso, no tokens consumidos). | 005-005 y la adopción de su versión (va después de 005-006 por prioridad, no por dependencia técnica: puede analizar sesiones históricas y luego las del arranque real de 005-006) |
| 8 | 005-003-orientation-reduction | Orientación al retomar y arranque desde reposo con contexto acotado, sobre todo el proceso de delegación. Contenido: una vista compacta del estado operativo generada por código desde las fuentes existentes (`status`); una selección explícita de entrada que atiende primero un paquete pendiente; una interfaz operativa suficiente con ejemplos que se ejecutan; la disposición de versión y del medidor (el medidor no instalado es ausencia, no incoherencia); y el resumen del conjunto para corridas multi-sesión (R4). El procedimiento canónico de arranque y reentrada consulta primero la vista compacta y amplía solo ante una necesidad concreta. Cada encargo trae los comandos de validación de su tarea, cuándo ampliarla, y las postcondiciones, invariantes y decisiones aplicables, con referencias al contrato completo. El arranque reutiliza el procedimiento de 005-006; el tamaño de unidad es de 005-007. Aceptación, con trabajo real y el medidor de 005-002 (artefacto del repo mientras no esté instalado): (1) una sesión nueva en reposo llega al primer despacho legítimo sin leer toda la historia ni reconstruir el CLI y sin que nadie le explique el recorrido; (2) una reanudación preserva autoridad, aprobaciones y efectos, y una ausencia o incoherencia devuelve el bloqueo y cómo resolverlo; (3) los ejemplos se ejecutan; (4) los roles empiezan y completan su encargo, commit incluido, con menos reconstrucción innecesaria, sin corridas completas innecesarias ni repetición de evidencia equivalente. D11 y R4 se cierran dentro de la feature, antes de usar la integración real y las corridas multi-sesión como gate. La meta numérica sale de la línea base medida, como orientación y no como demostración automática. | 005-002 |
| 9 | 005-007-progressive-planning | Contratos claros y tareas ejecutables con contexto suficiente, evitando tanto la especificación excesiva como la fragmentación: planificación progresiva (objetivo y dependencias completos; detalle solo para la tanda próxima) y tamaño de unidad que no pague planificación, sesiones y revisión sin avance suficiente. Las plantillas acompañan ese resultado: la spec parte del recorrido de uso en vez de una firma de función y su aceptación es el comportamiento, no un porcentaje de cobertura. La regla de reintentos permite continuar con una hipótesis nueva y avance verificable, y pide diagnóstico o replanteamiento ante repetición sin progreso; el número de intentos es una señal, no el criterio. | 005-006 |
| 10 | 005-004-claude-code-roles | Roles CDAD activos en Claude Code para este proyecto, sin tocar HOME salvo decisión del dueño (confianza de carpeta, copias viejas). Un ciclo corto real despachado desde Claude Code con la versión instalada al empezar el ciclo. | 005-005 (puede ir en paralelo con 005-002 y 005-003) |
| 11 | 005-011-common-entry | Continuación correctiva de 005-003: una sesión nueva entra al proceso por una ruta breve y común antes de leer el state o explorar. (a) Todas las skills (`cdad-epic`, `cdad-cycle` y las de rol que orientan) empiezan por `status`; `state-detection.md` y la documentación extensa quedan como ampliación ante una necesidad concreta, no como primer paso. (b) `status` acepta una raíz relativa igual que los demás CLI. (c) `status` informa versión y siguiente acción claras: un DRIFT legítimo (por ejemplo, agentes de proyecto anteriores a la instalación, que el próximo `prepare` republica) dice qué lo resuelve, en vez de invitar a investigar. Aceptación con el medidor de 005-002: una sesión nueva en reposo consulta `status` antes de leer el state completo y llega al primer despacho sin explorar versiones, manifiestos ni código del CLI; la meta numérica sale de `005-007/acceptance.md` §7 (70 llamadas, 304 mil caracteres) como orientación. | 005-003, 005-007 |
| 12 | 005-012-transition-registration | Operación del CLI que registra una decisión explícita del orquestador sobre una transición (recepción de una entrega, aprobación de un gate, avance de etapa, cierre de feature), comprueba sus requisitos y la aplica de forma consistente, sin edición manual del state. (a) Exige la evidencia referenciada (recibo, artefacto materializado) y que el gate lo apruebe quien tiene la autoridad vigente. (b) Recibir una entrega nunca aprueba un gate. (c) Repetirla tras una interrupción no duplica efectos. (d) Automatiza la contabilidad y conserva el juicio del orquestador. Cubre D-3 de 005-007. | 005-011 |
| 13 | 005-013-unit-contract | El hash identifica el contrato que recibió el agente y deja de bloquear globalmente la planificación del proyecto. (a) El contrato de una unidad es una proyección generada del plan, sin otra copia mantenida a mano: objetivo, alcance y aceptación de la unidad; restricciones compartidas que le aplican (incluidas secciones que prevalecen sobre las filas, como «Ajuste de los ciclos pendientes»); contratos o decisiones de otras unidades de las que depende; aprobación y versión de origen. El hash se calcula sobre esa proyección. (b) Consecuencias según el cambio: agregar una unidad futura independiente o modificar otra sin dependencias compartidas no afecta el encargo; un cambio en el alcance o en una dependencia relevante de la unidad activa registra el impacto y el orquestador decide cómo reconciliarlo; retirar una autorización o cambiar una restricción de aplicación inmediata impide las acciones afectadas. (c) Un paquete ya despachado se recibe contra el contrato que efectivamente recibió el agente; recibirlo no lo aprueba bajo el contrato nuevo, y la decisión de si sirve, se adapta o quedó superado es del orquestador. Fuera de alcance: varias unidades ejecutándose a la vez sobre el mismo state (`active_packet` único). Prueba decisiva: despachar un architect, agregar una feature independiente al plan y recibir su entrega normalmente; después comprobar que un cambio relevante sí exige reconciliación. | 005-011 |
| 14 | 005-014-closure-replay | Repetir un cierre ya aplicado no falla ni sugiere abrir la unidad. (a) Con `--transition closure` y sin feature activa, el CLI busca la clave de identidad en el historial de la feature nombrada (`--feature`): si existe con el mismo payload, es un no-op exitoso que lo dice en su salida y no escribe el state; si no existe, o es un cierre distinto (otro payload u otra feature), rechaza cerrado con un mensaje que no sugiere abrir la unidad cuando la feature ya está cerrada. (b) El mismo orden de chequeos ante una repetición después de un cambio de feature activa se revisa en las demás clases dentro de la spec: se corrige en esta unidad sólo si es el mismo arreglo; si no, va a deuda priorizada. Fuera de alcance: cualquier otro cambio de `register-transition`. Prueba decisiva: cerrar una feature y repetir la misma orden de cierre (rc=0, no-op, state byte a byte igual); una repetición con otro payload rechaza; y un escenario de reanudación con el CLI real sobre un proyecto descartable (cierre aplicado, «interrupción», la misma orden otra vez → no-op). | 005-012 |

## Ajuste de los ciclos pendientes — decisión del dueño, 2026-10-11

Dirección y backlog de investigación:
[operación, planificación y aceptación de uso](../../../findings/agent-operation-strategy-2026-10-11.md).
El dueño confirmó el orden de prioridad: interoperabilidad real → medición y
orientación → planificación → paralelismo/recursos → ejecución autónoma durable.
Los dos últimos son líneas posteriores por investigar, no features nuevas de
este epic. La secuencia de la tabla se conserva; 005-010 mantiene su contrato.

Estos ajustes forman parte del encargo de los próximos architect y prevalecen
sobre una lectura más estrecha de las filas de entrega:

- **005-002:** conservar el discovery y llevar al draft el
  [delta de medición](../../specs/005-002-session-context-meter/draft-inputs-2026-10-11.md).
  Distinguir primer `resume` y primer despacho observado; relacionar las métricas
  con resultado/evidencia sin construir un juez semántico de sesiones. Orientación,
  volumen de salidas y atención humana no se reducen a contar tokens; declarar lo
  no observable. No repetir desarrollos para comparar.
- **005-003:** consumir la
  [entrada de discovery](../../specs/005-003-orientation-reduction/discovery-inputs.md),
  incluidos estado compacto, siguiente acción y capacidades efectivas ligadas a
  versión/configuración. Evaluar aprovechamiento de interfaces existentes;
  OpenChamber es un caso, no una dependencia de la metodología ni un dashboard
  nuevo dentro de esta feature. La mejora debe llevar a un encargo útil, no solo
  a una invocación temprana de `resume`.
- **005-007:** el
  [encargo de investigación](../../specs/005-007-progressive-planning/discovery-inputs.md)
  amplía la profundidad del discovery: descomposición por resultado, dependencias,
  incertidumbre, contexto y costo de integración; aplicación a trabajo real y
  aceptación de uso diferenciada de TDD/E2E técnico. Seleccionar una mejora acotada;
  cambios de templates por sí solos no demuestran el resultado. Una solución que
  requiera scheduler, integración UI o plataforma de usabilidad se propone aparte.
- **005-004:** conservar su ciclo real y su alcance, teniendo presentes capacidades
  efectivas y acceso a las entregas. No convertirlo en una integración de WebUI.

El consumo continuo observado por el dueño en pruebas de Project Management
motiva una restricción transversal: mayor autonomía/concurrencia debe ir acompañada
de validación de resultados y presupuesto autorizado. Una sesión terminada o una
suite verde no habilitan automáticamente trabajo dependiente. La validación es
proporcional, con evidencia equivalente reutilizable y sin otra aprobación por
cada acción. No se añade ahora una plataforma de ejecución automática.

## Criterios de aceptación del epic

1. Todas las features del plan cerradas, cada una con su gate de etapa 5.
2. Cada ciclo corre de punta a punta con una versión instalada estable (agentes,
   skills y CLI de la misma versión, sin mezclas); la versión nueva se entrega en el
   repo al cierre y se despliega entre ciclos. Verificado en cada `prepare` por
   `source_dir`, hashes y la versión declarada por la instalación.
3. Informe de medición de contexto antes y después de 005-003, producido por
   la herramienta de 005-002 sobre sesiones reales.
4. Suite completa verde al cierre, corrida por el orquestador en un worktree
   fijado al commit de cierre; validadores sin fallos nuevos.
5. Aceptación conjunta del consumidor: después de entregar y desplegar las
   correcciones **entre ciclos**, una sesión nueva inicia el consumidor
   Perl/Webmin con una instrucción breve, conserva sus IDs y organización,
   registra lo faltante y realiza la primera delegación útil. Antes del primer
   RED del consumidor están verificadas su política, las capacidades de los
   roles, los comandos de validación y la autorización de su spec; el discovery
   documental permitido no espera toda la maquinaria. El recorrido real aporta
   la aceptación pendiente R2 de 005-006 y la de interoperabilidad cuando
   efectivamente ejerce ambas, reutilizando evidencia equivalente y
   anonimizando la evidencia publicable. Una capacidad nueva no equivale a una
   cifra de ahorro demostrada.

## Riesgos

- El esquema de `opencode.db` no es un contrato público: puede cambiar con
  versiones de OpenCode. 005-002 debe fallar cerrado ante un esquema desconocido.
- Con una sola sonda por variante, la medición es indicativa, no estadística.

## Operación

- Orquestación en OpenCode (`cdad-orchestrator`); Claude revisa entre ciclos.
- Modelos como en 003-007: `mofgw/deepseek-v4.1-flash` para architect,
  implementer y scribe; `mofgw/glm-5.3-flash` para test-writer y reviewer.
- Gates de tests: el implementer corre focales y módulos tocados; suite
  completa al cierre de cada feature o si se toca instalador, staging o renderer.
- Rama `codex/epic-005-real-operation`. Sin push automático.

## Autoridad (decisión del dueño)

Propuesta: misma forma que epic-003. El orquestador OpenCode actúa como HITL
delegado para specs, planes, gates y Memory Bank de este epic; vence al
cerrar, cancelar o revocar el epic; no se hereda; sin push. Quedan siempre del
dueño: activar versiones en el repo real, cambios en HOME y la confianza de
carpeta de Claude Code.

## Aprobación

- Aprobador del plan: Pablo
- Estado: Aprobado por Pablo el 2026-10-08 («ok», en respuesta a la solicitud de aprobar el plan y confirmar la delegación). Delegación en [execution.md](execution.md).

## Cambios al plan

- 2026-10-14: se suma la fila 14 (005-014, cierre repetible), unidad correctiva pequeña pedida por el
  dueño sobre un defecto del uso previsto de 005-012: con la feature cerrada `active_feature` es `null`
  y el chequeo de feature activa corre **antes** de la búsqueda idempotente por `transition_key`
  (PD-11), así que un orquestador interrumpido justo después del cierre no puede reanudar con la
  misma orden y recibe un error que sugiere abrir la unidad; la vía análoga que `late-delivery` ya
  resuelve (`--feature` cuando no hay feature activa) fija la forma del arreglo. Alcance y prueba
  decisiva en la fila. No cambia las filas 1–13 ni los criterios del epic. Se aplica con el proyecto
  en reposo (sin unidad activa ni paquete despachado) y no invalida trabajo en curso: verificado
  comparando la proyección de las unidades anteriores antes y después de la edición, la única línea
  que difiere es la procedencia `plan_sha256` del bloque de origen, que el veredicto de cambio no
  compara como parte (el origen es procedencia); las partes `unit` y `shared` quedan byte a byte
  iguales, porque la fila entra en la tabla de entregas —cuyas líneas quedan fuera de la proyección—
  y «Cambios al plan» es una sección de historia declarada por el producto. Aprobada por el dueño en
  la instrucción de continuación, bajo la HITL delegada vigente (`execution.md`).

- 2026-10-13: se suman las filas 11 (005-011, entrada común) y 12 (005-012, registro de
  transiciones) como unidades correctivas después de 005-004. Motivo: la medición D-1 de 005-007
  (`acceptance.md` §7) atribuye el gasto previo al primer despacho a la entrada al proceso (skills
  que mandan leer el state, `status` tardío y un DRIFT sin acción), no al registro posterior; la
  revisión de Codex lo confirmó y fijó las restricciones de la fila 12. Aprobada por Pablo («si,
  ok»). No cambia las filas 1–10 ni los criterios del epic; 005-004 conserva su alcance.
- 2026-10-13 (segunda): se suma la fila 13 (005-013, contrato por unidad). Motivo: el pin del
  architect es el sha del plan completo, y agregar planificación futura invalida encargos que no
  cambiaron, lo que impide planificar en paralelo. El dueño lo planteó y aprobó corregirlo («si,
  continúa»); la revisión de Codex fijó el contrato como proyección generada, la tabla de
  consecuencias y la recepción contra el contrato recibido, como unidad con aceptación propia y no
  como inciso de 005-012. Orden de ejecución: 005-011, 005-013, 005-012.

- 2026-10-12: la fila 8 (005-003) se reescribe con la enmienda que propuso su discovery
  (`docs/specs/005-003-orientation-reduction/discovery.md` §3), con los ajustes de las
  revisiones de Claude y Codex: la entrada habitual del orquestador pasa por la vista
  compacta; cada encargo trae su validación concreta y su contrato aplicable; los roles
  commitean; D11 y R4 se cierran dentro de la feature. Aprobada por Pablo («De acuerdo»).
  No cambia la lista de features ni su secuencia. En el criterio 3 del epic, el medidor
  se invoca desde el repo mientras no esté instalado.

- 2026-10-11: a pedido del dueño, se documenta la prioridad estratégica confirmada
  y se ajustan las entradas de 005-002/003/007 y el handoff. Se conserva la lista
  de features, su secuencia y los criterios de aceptación del epic. La investigación
  de planificación debe producir una mejora aplicada, y la aceptación distingue
  contrato, integración y usabilidad. OpenChamber y OnlyOffice quedan registrados
  con sus diferentes grados de evidencia; no se autorizan integraciones ni servicios
  nuevos. Al editar, el paquete activo de 005-010 y su checkpoint referenciaban su
  propia spec/plan, no este plan del epic; esos contratos se mantienen intactos.

- 2026-10-08: 005-001 suma la corrección del control de aprobación (I2). El
  primer `prepare` del epic falló porque el architect, que redacta la spec,
  necesitaba una spec aprobada; el orquestador lo esquivó con un registro
  provisional que habilita también a test-writer e implementer. No cambia el
  alcance ni los criterios del epic.
- 2026-10-08: 005-001 se amplía (fila 1, puntos c y d): reemplazo de paquetes
  obsoletos y mensajes de recuperación. Motivos: el paquete del architect quedó
  obsoleto cuando se editó este plan después de prepararlo, y el CLI no ofrece
  cómo reemplazarlo. Es una ampliación del alcance de la feature, aprobada por
  Pablo el 2026-10-08 («Estoy de acuerdo con la propuesta de Claude»); no
  cambia el alcance ni los criterios del epic. 005-002 suma la línea base de la
  primera sesión.
- Esta edición vuelve a cambiar el hash del plan: el paquete
  `005-001-idle-and-v7-bootstrap-architect-discovery-001` ya estaba obsoleto y
  se retira según `handoff-opencode-2.md`.

- 2026-10-09: 005-001 suma dos **correcciones acotadas de T1/T2**, instruidas
  por el dueño antes del cierre de la feature (no cambian el alcance ni los
  criterios del epic, sí la forma de la autorización y del reemplazo):
  (1) **Ruta de la aprobación.** El registro de aprobación de spec debe exigir
  que su `contract_path` coincida con el contrato, además del
  `contract_sha256`; una entrada con el hash correcto pero otro path (o sin
  path) no habilita nada.
  (2) **Conservación en el reemplazo.** `--replace-packet` conserva el encargo
  anterior (insumos, alcances, invariantes, entrega esperada y evidencia) y
  permite corregirlo con `--input`, `--read-scope`, `--write-scope`,
  `--invariant`, `--expected-output` y `--evidence` (cada una, si se da,
  reemplaza esa lista entera; la spec define cómo dejar una lista vacía cuando
  esté permitido). No acepta rol, subetapa, objetivo ni opciones de ejecución.
  Los invariantes obligatorios del rol se mantienen siempre. Las correcciones
  pasan las mismas validaciones que un `prepare` normal: si algo no es válido,
  falla nombrando el campo, el motivo y la opción para corregirlo, sin publicar
  nada y dejando intacto el paquete anterior. El registro de reemplazo, junto
  con los dos encargos guardados, debe permitir ver qué se conservó, qué cambió
  y por qué.
  Se ejecutan como tarea **T-CORR** (antes de T4), con **tests focales de
  regresión**, y se cubren en la única review formal del cierre. Gate de tests
  durante los ajustes: focales + módulos tocados; la suite completa queda para
  el cierre de la feature.
- 2026-10-09: se agrega 005-005-adoption-coherence (orden 2), continuación
  correctiva de 005-001, y 005-002 pasa a depender de 005-005 y de la adopción
  de su versión. 005-002 suma el formato de medición neutral y opcional y una
  segunda muestra. Las dependencias pasan a nombrar features en vez de números
  de orden. Cambia la descomposición del plan; aprobado por Pablo el
  2026-10-09 («si», sobre la propuesta de agregar 005-005). El criterio 1
  pasa de «las cuatro features» a «todas las features del plan»; los demás
  criterios no cambian.
- 2026-10-10: se agregan 005-006-guided-project-start (orden 3) y
  005-007-progressive-planning (orden 6); 005-002 pasa detrás de 005-006 por
  prioridad. El criterio 2 pasa de «la misma versión durante todo el epic» a
  «una versión estable durante cada ciclo, con entregas entre ciclos», según la
  regla del dueño del 2026-10-09 (desarrollar y desplegar son tareas distintas).
  Se quitan del título y del alcance las referencias a la v7. Aprobado por
  Pablo el 2026-10-10 («continúa como dices», sobre la propuesta de registrar
  005-006 y 005-007 con ese orden y las precisiones de Codex). No cambia el
  objetivo del epic.
- 2026-10-10: la fila de 005-006 nombraba por su nombre interno el proyecto
  de aceptación sin definirlo; el primer intento de arranque lo buscó por todo
  el workspace. Se reemplaza por una referencia al registro local (también
  evita publicar un nombre interno). Sin cambio de alcance.
- 2026-10-10: se agregan 005-008-project-path-capabilities (orden 4) y
  005-009-cli-delegation (orden 5), después de 005-006 y antes de 005-002, y se
  amplía el alcance con capacidades de rutas de proyecto y delegación externa
  interoperable. El dueño aprueba la propuesta
  `priority-perl-cli-plan-2026-10-10.md` en el encargo de continuación
  («Apruebo la ampliación y prioridades documentadas en
  …/priority-perl-cli-plan-2026-10-10.md», Pablo, 2026-10-10). El orden restante
  pasa a 005-002, 005-003, 005-007 y 005-004, según el plan vigente y sus
  dependencias; 005-002 no se cancela y no repite su discovery. Se agrega el
  criterio 5 (aceptación conjunta del consumidor); los criterios 1-4 no cambian.
  Quedan explícitamente fuera: POLICY-CLASS completa, CI, sandbox y una
  plataforma universal de jobs. La corrección focal de coherencia
  clasificador→permisos **sí** entra (005-008). Los valores de modelos y rutas
  de instalación son configuración local, no constantes de la metodología. No
  cambia el objetivo del epic.
- 2026-10-11: se agrega 005-010-real-opencode-delegation (orden 6), continuación
  correctiva de 005-009, antes de 005-002. 005-009 cerró con PD-10 sin evidencia
  y, al intentar el recorrido real, el adaptador instalado (`6f4d5db`) resultó
  inoperable contra OpenCode real: los roles son `mode: subagent` (falla cerrado),
  la señal durable es un JSON que solo escribe el doble de los tests y el
  transporte por stdin no está verificado en la versión instalada (v2.0.26). La
  orquesta Claude, porque el lado coordinador del recorrido es Claude
  (`execution.md`, sección 2026-10-11). Aprobada por el dueño («ok: a», Pablo,
  2026-10-11, sobre la propuesta de ciclo correctivo orquestado por Claude con
  roles en OpenCode). No cambia el objetivo ni los criterios del epic.
