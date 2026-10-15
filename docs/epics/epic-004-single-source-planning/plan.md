---
epic_id: epic-004-single-source-planning
created_at: 2026-09-23
status: active
activated_at: 2026-09-24
---

# Epic 004 propuesto: autonomía supervisada, fuente única y planificación

> **Estado vigente (reconciliado 2026-09-29 con `docs/.cdad-state.json`):**
> epic **activo** desde 2026-09-24 (activación aprobada por Pablo según el
> procedimiento §6; registro en `epic_history` y en
> [execution.md](execution.md)). 004-001 tiene T1–T7 cerrados y su cierre de
> feature está pendiente; 004-002 y 004-003 están en cola. Las secciones
> "Actualización 2026-09-24" y "Estado y función de este documento" que siguen
> describen el estado **previo** a la activación y se conservan como historia.
> Ante una divergencia, la fuente de verdad del estado es el state file.

Actualización 2026-09-24: la dirección metodológica de
[ADR-011](../../adr/ADR-011-autonomia-supervisada-limites-proporcionales.md)
está decidida por el usuario. La activación/specs del epic siguen pendientes.
La [enmienda C0 vigente](c0-amendment-supervised-autonomy-2026-09-24.md)
incorpora R1–R3, sustituye D2/D9 del informe histórico y contiene el encargo
inmediato para GLM. **Simplificar la política antes de generar sus copias.**

## Estado y función de este documento

Propuesta para revisión C0; no epic activo ni plan aprobado. Los tres IDs de
features son candidatos. No crear todavía entradas `done`, specs aprobadas ni
evidencia ficticia. El detalle adicional de este plan busca un handoff preciso;
no obliga a reproducir esta extensión en todos los planes de CDAD.

Mandato, reparto GLM/GPT/Claude y secuencia completa:
[handoff de continuación](../../handoffs/2026-09-23-glm-continuation.md).
Procedimiento que se pretende incorporar:
[planning-contract-draft.md](planning-contract-draft.md).

## Resultado buscado

Que cada rol pueda completar su encargo con autonomía supervisada y límites
proporcionales; que una regla de CDAD se mantenga en una única fuente editable y llegue de
manera coherente a sus runtimes; que un proyecto consumidor pueda preparar
un encargo sin fabricar a mano su identidad de ejecución; y que los planes
se revisen por cobertura, contexto, dependencias y recorrido completo antes
de construir. Esto habilita la continuación del epic 003, sin sustituirla.

## Alcance y exclusiones

Incluye agentes OpenCode/Claude Code, variantes base/Odoo, paquetes, contratos
de orquestación, instalación y bootstrap de la política del proyecto. Reutiliza
los perfiles de modelos; revisa y simplifica allowlists/hooks existentes
según ADR-011, sin convertir sus mecanismos históricos en invariantes. Añade procedimientos de planificación y
revisión de planes con roles existentes.

No incluye un agente planner permanente, otro orquestador, un controlador LLM,
un motor general de workflows, nuevo proveedor, benchmarks de modelos, RAG,
integración completa de todos los runtimes ni implementar 003-002/003/004 dentro
de este epic. Tampoco rediseñar la metodología Odoo. Los permisos se ajustan para hacer
viable el encargo según ADR-011, no para facilitar el trabajo del generador. Las instrucciones de dominio conservan sus fuentes.

## Diagnóstico de partida que debe validar el inventario

- Contrato de roles repetido en skill y dos orquestadores: igualdad parcial
  automatizada, pero el contenido de modelos corresponde al diseño OpenCode
  y resulta confuso en Claude Code.
- Procedimientos repartidos entre cuerpos de agentes, referencias de etapas
  y paquetes. Hay divergencias semánticas fuera de las tablas verificadas;
  revisar, por ejemplo, el tratamiento de properties.
- 22 agentes mantenidos manualmente. El port de paquetes omitió inicialmente
  Claude Code y se completó en 003-005.
- El instalador copia a `agents/` y `skills/` bajo la raíz de instalación
  además de destinos runtime. Con raíz HOME esto genera carpetas no usadas
  por los runtimes. Los renombrados dejan archivos obsoletos.
- `execution.json` combina identidad de ejecución y política de paths del
  proyecto; `prepare` ya existe pero necesita ese archivo.
- La planificación existe; sus controles no exigen todavía revisión técnica
  independiente de la división, contexto previsto ni productor de cada entrada.

El inventario debe usar una tabla por **regla/responsabilidad**, no solo contar
líneas similares: fuente actual, consumidores, divergencia, fuente futura,
salidas derivadas, compatibilidad y verificación. Incluir referencias sueltas
en `skills/` para comprobar si son shims; no eliminarlas por parecer duplicadas.

## Arquitectura propuesta y contratos compartidos

| Responsabilidad | Fuente editable propuesta | Consumidores / restricciones |
|---|---|---|
| Identidad y límites de cada rol | Definición canónica del rol | Agente, paquetes y adaptador de permisos; sin tres listas manuales. |
| Procedimiento por rol/subfase | Paquetes/procedimientos canónicos | Ejecutor y referencia de orquestación pertinente; composición determinista. |
| Secuencia, gates y decisiones del ciclo | Contrato canónico de orquestación | Skill, orquestador y referencias generadas o resumidas desde la misma fuente. |
| Modelos configurados | `scripts/cdad-models.sh` y configuración explícita de ejecución | Adaptación por runtime/perfil; distinguir configurado y reportado. |
| Capacidades y permisos runtime | Contrato por rol de ADR-011 + adaptador por runtime | Libertad dentro del encargo y barreras justificadas; retirar restricciones sin garantía útil. |
| Especialización Odoo | Fuentes de dominio existentes y delta de rol | No clonar todo el procedimiento base ni suprimir reglas Odoo. |
| Clasificación de paths | Política versionada del proyecto | Scopes de paquetes y controles efectivos del runtime. |
| Identidad de ejecución | Registro durable resuelto al iniciar/reanudar | Estado, paquetes y futuros receipts/checkpoints; estable entre llamadas. |

La ubicación exacta y el formato de las nuevas fuentes se deciden en C0.
Evitar introducir un lenguaje de configuración general: usar el mecanismo
más simple que exprese estos contratos y se distribuya con el proyecto.

**Una fuente no significa una sola aparición en el prompt.** Puede ser
necesario generar invariantes breves en más de un consumidor. La propiedad
requerida es que se editen una vez y se deriven coherentemente. Los agentes
deben seguir funcionando sin acceso al repo fuente, con la instalación real.

Separar generación de instalación: entradas explícitas → artefactos reproducibles
en staging; luego despliegue controlado en destinos del runtime. Si el resultado
depende del stack/perfil, esa configuración es una entrada identificada, no
un efecto oculto de la máquina que ejecuta el generador.

## Descomposición candidata

| Orden | Feature candidata | Resultado completo | Dependencias |
|---|---|---|---|
| 1 | `004-001-canonical-runtime-artifacts` | Política simplificada por capacidades; fuentes canónicas y agentes derivados utilizables en ambos runtimes, con instalación controlada y detección de drift. | Inventario y C0 aprobados. |
| 2 | `004-002-project-execution-bootstrap` | Política del proyecto revisable y preparación orgánica de ejecuciones/paquetes con identidad estable y permisos coherentes. | Contratos y adaptadores de 001. |
| 3 | `004-003-planning-procedures` | Planificación y revisión de planes como procedimientos de roles existentes, consumibles desde instalación, con inputs y evidencia propios. | Fuentes de 001, bootstrap de 002. |

Usar desde C0 el procedimiento documental de planificación; 003 lo incorpora
al producto. No hay dependencia circular entre usar una guía y automatizarla.
El architect puede revisar esta división en C0 si demuestra una frontera mejor.
No crear más ciclos por cada archivo, runtime o test. Dentro de cada ciclo sí
hay tareas RED→GREEN acotadas.

## Ciclo 004-001: fuentes canónicas y artefactos por runtime

### Entregable y tareas internas candidatas

1. Formalizar capacidades, autonomía e invariantes por rol según ADR-011;
   decidir qué controles conservar/simplificar/retirar. La medición inicial
   es preparación, sin ciclo propio. Probar el trabajo legítimo con la política
   simplificada antes de consolidar la generación, empezando por OpenCode.
   Definir la fuente común y las diferencias legítimas de runtime/dominio.
2. Generar los agentes y las secciones derivadas. Contrato común estable antes
   de trabajar en adaptadores OpenCode y Claude Code.
3. Conectar instalación/check con salidas generadas y una política de propiedad
   de archivos. Integrar el recorrido instalado de ambos runtimes.

Adaptadores podrían construirse en paralelo si no editan las mismas fuentes
compartidas. El integrador es único y verifica ambos contra el mismo contrato.
No paralelizar cambios concurrentes a `install.sh` o al state sin protocolo.

### Requisitos observables

- Cada rol dispone de lectura/medición/cálculo/ejecución necesarios dentro de
  su alcance. Pruebas de capacidades positivas acompañan las fronteras retenidas.
- Permisos se justifican por efectos/recursos, no por una lista de nombres
  mantenida por inercia. Read-only del producto permite scratch/logs declarados.
- Generar la política simplificada, no replicar las restricciones históricas.
  Sesiones, paquetes y worktrees no se describen como sandbox por sí solos.
- Baseline verificable y mantenimiento: una fuente por regla, cambios propagados
  sin edición de salidas. Informar líneas/bytes y complejidad, sin techo de líneas
  como criterio de aceptación. No confundir bytes con contexto efectivo.
- Las denegaciones inesperadas producen diagnóstico útil para el orquestador;
  alternativas no soportadas y salidas abreviadas no cuentan como evidencia exacta.
- Misma entrada explícita produce la misma salida; generación falla ante
  combinaciones no soportadas o fuentes incompletas, sin publicar una mezcla.
- Una modificación de un invariante canónico llega a todos sus consumidores.
  Pruebas independientes comprueban el significado, no solo igualdad de bytes.
- Tabla/modelo configurado corresponde al runtime y perfil; `basic` conserva
  su semántica de herencia. Nunca mostrar un modelo de diseño como modelo
  efectivo observado. No cambiar la selección de modelos como parte del refactor.
- Los agentes de rol cargan su procedimiento pertinente sin sumar skill completa
  en el camino de paquete. Legacy sigue utilizable o tiene migración explícita
  revisada; no retirar ese fallback silenciosamente.
- Invariantes anti-trampa y especializaciones Odoo se preservan. Validar la
  semántica de permisos/orden de reglas de cada runtime, no homogeneizarlos a ojo.
- Instalar en destinos reales de los runtimes bajo una raíz aislada. Los fixtures
  consumen ese layout. Si se conserva un layout de exportación, es opt-in y no
  se mezcla con la instalación normal.
- No crear por defecto `HOME/agents` y `HOME/skills`. No borrar carpetas ajenas
  ya existentes para ocultar el problema.
- Actualización elimina solo archivos obsoletos demostrablemente propiedad de
  CDAD, con tratamiento explícito de modificaciones locales y dry-run. No
  aplicar borrado global a una carpeta compartida. Un manifest de propiedad es
  una opción; C0/spec debe fijar el contrato elegido.
- Mantener protección frente a source/destination overlap, symlinks, extra dirs
  y rollback que afecte únicamente archivos propios de la operación.
- `--check` detecta desvíos entre configuración/fuentes y producto instalado.
  Los cambios de tests de igualdad F001 deben reemplazarse por controles de
  generación + semántica por runtime, no simplemente eliminarse.

### Pruebas y aceptación del ciclo

Recorridos de tareas legítimas (medición/suma, lecturas permitidas, runner y
entrega de evidencia) más casos de fronteras retenidas. Verificar raw/wrapper
solo donde se soporten y con salida apropiada; no multiplicar excepciones
por cada comando. La spec define qué se controla antes y qué se verifica al
re-entry. No omitir pruebas útiles para satisfacer un presupuesto de líneas.

Matriz base/Odoo × OpenCode/Claude Code × perfiles soportados, usando datos
sintéticos y configuración explícita; no llamadas a proveedores para cada celda.
Casos negativos de permisos y destinos; actualización con archivo CDAD
renombrado y archivo ajeno conservado; generación repetida; smoke instalado
desde un proyecto consumidor sin depender del checkout como ruta de ejecución.
Separar evidencia de archivos generados de evidencia de permisos efectivos
en un runtime: no atribuir a una prueba estática lo que no ejecutó.

## Ciclo 004-002: política del proyecto y bootstrap de ejecución

### Entregable y tareas internas candidatas

1. Política versionada del proyecto: clasificación, carga, propuesta inicial y
   validación. Detectar layout puede proponer una política, no otorgar autoridad.
2. Resolver/iniciar/reanudar ejecución durable desde state + runtime + autoridad;
   extender el `prepare` existente, sin crear un productor paralelo.
3. Adaptar scopes/permisos a esa misma política y verificar el recorrido desde
   proyecto consumidor. Documentar instalación/configuración mínima real.

### Requisitos observables

- Tests, implementación y documentación se clasifican sin ambigüedad, incluyendo
  proyectos con tests colocados junto al source y Odoo. Política inválida,
  ausencia de clasificación necesaria o solapamiento no amplían permisos.
- La política es versionada/revisable en el proyecto. Su ruta exacta se fija en
  spec y se descubre de forma determinista; evitar configuraciones competidoras.
- El bootstrap utiliza autoridad ya existente o presenta la decisión faltante;
  no deduce aprobaciones de nombres de carpeta, texto de un resultado o defaults.
- La identidad lógica se crea una vez y persiste al preparar otros paquetes,
  reintentar o reanudar. Un proceso/sesión runtime nuevo no significa otra
  ejecución lógica; los futuros budgets y receipts dependen de esto.
- Registrar feature/epic, runtime observado, modelo configurado/reportado,
  política y autoridad aplicables. Unknown permanece explícito, sin falsos datos.
- Conservar snapshot/referencia verificable de la política efectiva. Si cambia
  durante una ejecución, detectar el cambio y reconciliarlo explícitamente;
  no cambiar permisos de un trabajo en curso silenciosamente.
- Dejar de exigir al usuario construir manualmente el archivo de identidad
  cuando los datos se pueden resolver. Esto no implica eliminar el registro
  durable de ejecución. Compatibilidad con execution contexts anteriores se
  decide por consumidores reales y se prueba.
- Política/encargo distingue archivos del producto, temporales autorizados y
  acciones externas. Los fallos de capacidad devuelven al coordinador la razón
  concreta, sin transformarse en incumplimiento del agente por recibir un deny.
- Los permisos efectivos y scopes del paquete concuerdan o el runtime declara
  una limitación concreta antes de despachar. No declarar sandbox por rol si
  solo existen restricciones conductuales.
- Preparaciones concurrentes no pisan estado ni asignan la misma identidad
  indebidamente. Definir exclusión/rechazo seguro si se conserva un solo
  `active_packet`; no prometer despacho paralelo con un estado que no lo soporta.
- Un fallo no deja identidad/state/paquete contradictorios ni borra trabajo
  ajeno. Verificar recuperación ante interrupciones en puntos definidos.

### Pruebas y aceptación del ciclo

Desde proyecto sintético representativo: descubrir/revisar política → resolver
ejecución → preparar paquete → comprobar agente/alcance instalado. Repetir
prepare/reanudar conservando identidad; fallos de autoridad, paths y política
cambiada; concurrencia o rechazo explícito; proyectos legacy y standalone.
No se exige recepción automática: es responsabilidad de 003-002.

## Ciclo 004-003: procedimientos de planificación y revisión

Enmienda de alcance acordada con el usuario el 2026-10-05:
[orquestación y validación proporcionales](../../specs/004-003-planning-procedures/efficient-orchestration-requirements.md).
Incorporar al discovery/spec/plan: estrategia de validación por tarea,
reutilización de evidencia vigente, delegación por unidades coherentes y
supervisión sin duplicación rutinaria. No crea una feature adicional ni cambia
por sí sola los gates operativos; su armonización forma parte de 004-003.

### Entregable y tareas internas candidatas

1. Incorporar el contrato de planificación y el re-entry proporcional de ADR-011:
   encargo breve con razones, decisiones autónomas, evidencia y respuesta a
   desviaciones; conservar trabajo válido y repetir solo lo invalidado.
   Integrar en la fuente correcta, los templates
   y los gates pertinentes, sin duplicar otro manual de roles.
2. Incorporar modo de revisión de planes en reviewer, con inputs distintos de
   la revisión de código, sesión independiente y contrato de salida acotado.
3. Probar distribución/consumo y usarlo para replanificar el trabajo pendiente
   de 003-002; guardar dictamen y cambios concretos, sin reimplementar 002.

### Requisitos observables

- Epic: cobertura de intención, recorrido completo, dependencias e invariantes.
  Feature: tareas verificables y contexto suficiente. Detalle fino solo para
  la próxima tanda; tareas futuras pueden declarar incertidumbre con dueño y
  condición de resolución, sin entrar así a construcción.
- El reviewer recibe intención original + restricciones + plan, no solo spec.
  Revisa omisiones y supuesta independencia, no solo consistencia interna.
- La revisión no autoaprueba alcance. El responsable autorizado resuelve los
  hallazgos; un cambio de frontera/permiso/contrato compartido revisa dependencias.
- El procedimiento no crea planner permanente ni obliga a revisión extensa
  por cada tarea menor. Define disparadores y alcance de revisión incremental.
- Importante: hoy el renderer solo soporta `reviewer/review` contra
  `approved-feature-spec`; architect consume `approved-epic-plan`. Revisar
  un **plan borrador** antes de aprobación no cabe honestamente en ese contrato.
  La spec debe definir soporte explícito para objeto borrador, versión y
  autoridad de revisión, o un handoff legacy identificado mientras se migra.
  No falsificar `approved` ni reutilizar un tipo incompatible para pasar el guard.
- Una propuesta de plan no concede permisos de implementación. Mantener separados
  artefacto revisado, referencia de autorización y estado de aprobación.
- El orquestador verifica en límites de tarea/subfase y ante señales relevantes,
  sin microgestionar herramientas. Distingue decisión válida, obstáculo del
  entorno, desvío aceptable e incumplimiento material. No cerrar gates afectados
  por evidencia inválida; no repetir automáticamente la tarea completa.
- Vincular estimación/observación a tarea y versión del plan sin exigir un
  sistema general de telemetría. Métricas ausentes no se fabrican.

### Pruebas y aceptación del ciclo

Fixtures de plan con entrada sin productor, dependencia circular, contrato
incompatible y paralelismo inválido prueban los checks mecánicos que realmente
se implementen. Un esquema no decide la calidad semántica: el reviewer debe
probar el procedimiento sobre el próximo plan real y registrar hallazgos.
La comprobación instalada incluye el nuevo modo de revisión y no requiere
leer todo el repo fuente ni convertir el borrador en aprobado para invocarlo.

## Recorrido consumidor que debe cerrar el epic

| Paso | Productor de la entrada | Consumidor y comprobación |
|---|---|---|
| Fuentes y configuración de runtime | Repo canónico + configuración explícita | Generador, con validación de combinaciones. |
| Agentes/skills derivados | Generador | Instalador, con propiedad/destinos y check. |
| Política del proyecto | Bootstrap propone; responsable autorizado resuelve ambigüedad | Preparación y adaptadores de permisos. |
| Identidad y autoridad de ejecución | Bootstrap resuelve datos durables y autoridad existente | State/prepare, sin inventar aprobaciones. |
| Objetivo y plan | Usuario/discovery y architect/coordinador | Reviewer de plan en otra sesión. |
| Contrato aprobado para construir | Responsable autorizado tras resolver hallazgos | Prepare y rol correspondiente. |
| REQUEST/PACKET | Prepare existente extendido | Agente instalado, inputs y scopes comprobados. |
| Resultado del rol | Canal real del runtime | Coordinador conserva original; recepción automatizada llegará en 003-002. |

El responsable de integración es el coordinador del epic; cada ciclo verifica
su tramo y la integración final verifica todos. Los smokes mecánicos pueden
usar resultados sintéticos, etiquetados como tales. Al menos un encargo útil
pendiente debe comprobar el consumo real del paquete por el agente; aprovechar
la revisión/planificación de 003-002 para no repetir un desarrollo terminado.

## Cierre y entrega a epic 003

Cerrar solo con: ciclos aprobados/cerrados, fuentes sin edición manual
competidora, ambos runtimes con compatibilidad y límites documentados, proyecto
consumidor funcionando, plan real revisado y handoff a 003 actualizado.

La suite Python de base y los tres validadores conocidos se ejecutan según su
alcance, en raíces aisladas; añadir las nuevas comprobaciones significativas.
No obligar a una cantidad fija de tests. Resolver explícitamente el gate de CI
si sigue sin existir; no declarar CI verde por ejecutar tests locales.

Conservar las garantías ya aprobadas de 001/005, revisando contratos mediante
enmiendas cuando corresponda. No cerrar 003 junto con 004: recepción, guards,
continuidad y presupuesto 200k siguen pendientes hasta su propia evidencia.

## Decisiones que debe resolver C0

0. Aplicar ADR-011 ya decidido; concretar capacidades y controles mínimos,
   sin reabrir la elección metodológica ni tratarla como una lista de comandos.
1. Aprobar o ajustar los tres límites de feature y las fuentes canónicas.
2. Formato/ubicación de fuentes y salidas generadas, compatibilidad legacy y
   propiedad de archivos instalados. No precisar toda la implementación.
3. Seleccionar runtime/versiones de construcción y política de modelos real.
4. Registrar autoridad GLM/GPT/Claude y suspensión/reanudación de epic 003 sin
   perder su state, decisiones o historial.
5. Confirmar cómo se revisarán borradores mientras se incorpora el modo nativo,
   y quién puede aprobar los contratos resultantes.

---

Status: Draft — pendiente de revisión C0 y aprobación del responsable autorizado.
