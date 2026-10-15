# Continuación de CDAD con GLM

Fecha: 2026-09-23. Base inspeccionada: `4a821a0`, rama
`codex/epic-003-context-efficiency`. Documento de encargo y continuidad;
no constituye aprobación de las nuevas specs ni evidencia de ejecución.

## Actualización vigente — 2026-09-24

El usuario pidió ajustar CDAD hacia autonomía supervisada. La decisión está
aceptada en [ADR-011](../adr/ADR-011-autonomia-supervisada-limites-proporcionales.md).
El próximo encargo es la [enmienda C0](../epics/epic-004-single-source-planning/c0-amendment-supervised-autonomy-2026-09-24.md):
GLM prepara spec/plan de 004-001 simplificando capacidades y controles **antes**
de generar agentes. Incorpora las correcciones de C0; no repetir el inventario
completo ni pedir de nuevo la decisión metodológica del usuario.
El nuevo epic sigue sin activar; política instalada sin cambios. El reparto
GLM desarrolla / GPT o Claude analiza y revisa permanece.

## 1. Leer esto primero

El usuario quiere que **GLM desarrolle las mejoras**, reservando GPT y Claude
para análisis profundo y revisión. La prioridad es mejorar contratos,
procedimientos, descomposición y gestión del contexto. No se solicita elegir
el mejor modelo ni comparar proveedores. La versión concreta de GLM y el
runtime de continuación todavía no se han fijado en este encargo: registrar
los efectivos al comenzar; no inventarlos ni cambiar perfiles globales.

La decisión más reciente es explorar **mejores skills/procedimientos de
planificación antes de crear un agente planner**. El plan inicial de este
handoff no añade ese agente. La responsabilidad de planificar existe; la
necesidad de otro tipo de agente queda diferida y requiere justificación.

Este encargo documenta y prepara la continuación. No activa hoy otro epic,
no inicia implementación, no instala en el home y no publica cambios.

### Lectura por etapas, sin cargar todo el repositorio

1. Leer este documento y comprobar estado, rama y cambios locales.
2. Leer el [plan propuesto del epic 004](../epics/epic-004-single-source-planning/plan.md).
3. Para preparar/revisar la planificación, leer su
   [contrato de procedimiento](../epics/epic-004-single-source-planning/planning-contract-draft.md).
4. Consultar las fuentes concretas enlazadas para el siguiente trabajo.
5. Al retomar 003, leer su [handoff actual](../epics/epic-003-context-efficiency/handoff.md)
   y solo el apartado correspondiente de
   [remaining-features-handoff.md](../epics/epic-003-context-efficiency/remaining-features-handoff.md).

No entregar los cuatro documentos completos a todos los ejecutores. El
coordinador extrae un encargo por rol con contratos y restricciones completos,
referencias precisas y contexto permitido. No copiar la conversación histórica.

## 2. Intención que debe sobrevivir a cada cambio de sesión

- Mantener un orquestador lógico capaz de trabajar durante muchas horas,
  decidir dentro de la autoridad delegada y conservar el objetivo global.
- Reducir el contexto necesario por tarea y por llamada. El epic 003 tiene
  objetivo 200k; menos de 100k es una aspiración posterior, no una garantía
  alcanzada ni una condición nueva para cerrar el MVP.
- Automatizar lo mecánico con código. No introducir un administrador LLM que
  consulte otro LLM estratégico en cada vuelta.
- Mantener contratos verificables, separación de sesiones, permisos por rol,
  test-writer sin implementación, auditoría independiente y review.
- Mejorar sobre desarrollos pendientes. No repetir features terminadas para
  comparar resultados, modelos o estrategias.
- Reducir carga de mantenimiento: una fuente editable de cada regla;
  derivaciones generadas por runtime cuando sean necesarias.
- Hacer que el producto instalado sea utilizable desde un proyecto real.
  Que las piezas internas pasen tests no basta.
- Guardar estado antes de cada handoff o transición para poder continuar con
  otro modelo sin depender de esta sesión ni del crédito disponible.

La descomposición tiene que reducir complejidad y contexto total, no solo el
tamaño de cada mensaje. No convertir cada tarea interna en un ciclo completo.
La paralelización es opcional: necesita contratos estables, ámbitos disjuntos
y una integración definida; no es un objetivo por sí misma.

### Vocabulario que se debe mantener estable

| Término | Significado en este encargo |
|---|---|
| Epic | Objetivo global que coordina varias features y su integración. |
| Feature / ciclo | Capacidad verificable que atraviesa las etapas CDAD. |
| Tarea | Unidad interna de una feature con contrato y verificación propios; no implica otra ceremonia completa. |
| Rol / modo | Responsabilidad e instrucciones del ejecutor; un modo nuevo no exige otro tipo de agente. |
| Sesión | Contexto concreto de una instancia del runtime; se puede sustituir al reanudar. |
| Ejecución lógica | Identidad durable del trabajo autorizado; puede abarcar varias sesiones y paquetes. |
| Paquete | Encargo canónico para rol/subfase, con contrato, entradas y límites; no es todo el contexto que se consumirá. |
| Receipt / recibo | Constancia mecánica de recepción/verificaciones; no aprobación semántica. |
| Gate | Condición de transición comprobada con evidencia y, donde corresponda, aprobación autorizada. |
| C0 | Revisión inicial de la propuesta estructural, antes de construir sus ciclos. |

## 3. Estado comprobado y límites de la evidencia

| Elemento | Estado al preparar este handoff |
|---|---|
| Repositorio de trabajo | Repositorio anidado `cdad/`; el padre contiene un gitlink. Operar dentro del repositorio anidado. |
| HEAD inspeccionado | `4a821a0`; árbol limpio antes de estos cambios documentales. |
| Epic activo en state | `epic-003-context-efficiency`, `features-loop`, sin feature activa. |
| 003-001-role-packets | Cerrada: paquetes canónicos, validadores, métricas e instalación aislada. |
| 003-005-claude-code-packets | Cerrada: `prepare`, binding de state y consumidores Claude Code. |
| 003-002-artifact-tools | En cola; discovery/spec/plan en archivos `*-draft.md`, no aprobados. |
| 003-003 / 003-004 | En cola; briefs, sin specs individuales aprobadas ni implementación. |
| Epic 004 de este handoff | Propuesta nueva; no activo, no aprobado, IDs de features provisionales. |
| Contexto <200k durante ejecución prolongada | No demostrado todavía. |

En una comprobación anterior de esta misma conversación, sobre `4a821a0`,
`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests -q -p no:cacheprovider`
terminó con **52 passed en 149.23s**. No se reejecutó para producir este
handoff, que solo cambia documentación. Es una observación de continuidad,
no evidencia vigente para aprobar futuros cambios. Los cierres de 001/005
registran validadores en PASS con instalación aislada; este handoff no afirma
haber repetido esos validadores ni comprobado la instalación real actual.

Fuentes del estado: [state](../.cdad-state.json),
[activeContext](../activeContext.md), [execution](../epics/epic-003-context-efficiency/execution.md),
[spec de 005](../specs/003-005-claude-code-packets/spec.md).

### Hechos importantes para no partir de un diagnóstico falso

1. Hay planificación en tres niveles; no hay que inventarla desde cero.
   Ver `skills/cdad-epic/references/epic-planning.md` y
   `skills/cdad-cycle/references/stage-2-specification.md`.
2. Las tres tablas de roles tienen un control de igualdad en
   `tests/validate-consistency.sh`. La igualdad puede propagar contenido
   incorrecto para un runtime. No describir todos los validadores como simples
   comprobaciones de frases ni afirmar que esas tablas difieren byte a byte.
3. Existen 11 agentes OpenCode y 11 Claude Code, incluyendo orquestadores y
   variantes Odoo. La duplicación manual sí crea mantenimiento y omisiones.
4. El epic 002 ya discutió fuente única. Su
   [cierre](../epics/epic-002-cdad-audit-fixes/closure.md) explica por qué se
   conservaron prompts autocontenidos. Generar esos prompts desde una fuente
   permite mantener esa propiedad; no sustituirlos por enlaces que nadie carga.
5. `prepare` existe. No volver a construirlo como si faltara. Actualmente
   requiere el execution context, prepara archivos y deja `active_packet` en
   `prepared`; no implementa recepción, despacho persistente ni continuidad.
6. La política de paths del paquete no equivale por sí sola a los permisos
   efectivos del runtime. Hay que conectar o contrastar ambos controles.
7. El esquema de métricas valida registros; no prueba que haya captura
   automática de todo el contexto de una sesión.

## 4. Autoridad, modelos y revisión

### Reparto operativo propuesto

| Función | Responsable y límite |
|---|---|
| Coordinación cotidiana y construcción | GLM: prepara encargos, conduce ciclos, ejecuta roles en sesiones separadas y resuelve decisiones rutinarias dentro de contratos aprobados. |
| Diseño inicial de specs y planes | GLM en modo architect; devuelve propuestas concretas y dudas acotadas. |
| Análisis profundo | GPT o Claude: arquitectura compartida, límites de confianza, descomposición y decisiones que afecten otros ciclos. |
| Review independiente | GPT o Claude en sesión distinta del autor/implementer; evidencia y contrato como entradas, sin aceptar conclusiones del autor como prueba. |
| Aprobación estratégica | Usuario o agente expresamente autorizado para ese alcance. Un dictamen técnico de review no concede por sí solo esa autoridad. |

El usuario ya eligió GLM para el desarrollo y GPT/Claude para análisis y
revisión. No volver a pedir permiso por esa asignación. La anterior selección
de Sol es histórica y no determina los próximos encargos.

La delegación de HITL a Codex del epic 003 **no debe copiarse como si nombrara
a GLM ni como aprobación del nuevo epic 004**. Preparar primero el plan y la
política de ejecución concretos; en el checkpoint C0 registrar alcance,
responsable, decisiones delegadas y vencimiento. Una vez autorizados, no
reconsultar cada acción rutinaria. Si no existe autorización para aprobar una
spec, GLM puede prepararla y hacer el discovery, pero no autoaprobarla.

La construcción GLM + revisión GPT/Claude es distinta del recorrido de
validación de modelo único que aún exige el plan aprobado de 003. No afirmar
que son equivalentes. Antes del recorrido final, conservar ese requisito o
presentar una modificación explícita para revisión/aprobación; no comprar
ejecuciones duplicadas para satisfacer dos interpretaciones.

[ADR-010](../adr/ADR-010-modelo-unico-mvp-epic-003.md) es una excepción
limitada, con runtime/epic/vencimiento. No heredarlo en 004 ni desactivar un
guard para poder avanzar. Identificar la política aplicable a la ejecución
real y revisar únicamente la ampliación que de verdad resulte necesaria.

### Checkpoints de revisión, sin consulta por cada iteración

- **C0, antes de construir 004:** inventario, descomposición, fuentes canónicas,
  contratos compartidos, recorrido consumidor y autoridad. Una revisión
  conjunta GPT o Claude; no hacen falta ambos ni un comité.
- **Por ciclo:** spec y plan concretos antes de RED cuando introducen nuevos
  contratos o riesgos; agrupar su examen en un único paquete de revisión.
  Las tareas internas no reciben todas otro ciclo ni otra aprobación global.
- **Antes de cierre de cada feature:** revisión independiente del diff,
  tests y evidencia, conforme a CDAD. Correcciones focales se reevalúan con
  el alcance necesario; no reconstruir toda la discusión por cada ajuste.
- **Antes de reanudar 003-002:** revisar su draft contra los nuevos contratos.
- **Antes de integrar/cerrar 003:** revisar continuidad, presupuesto real y
  recorrido de aceptación completo.

Si GPT/Claude no están disponibles, guardar el paquete de revisión y continuar
solo trabajo independiente autorizado. No fingir una aprobación, reemplazar
silenciosamente al reviewer ni dejar una llamada de pago repitiéndose en espera.

## 5. Secuencia de trabajo

1. **Reconciliar y preparar C0.** Verificar HEAD/state, inventariar fuentes y
   confirmar capacidades del runtime real. Usar el procedimiento propuesto de
   planificación para preparar 004; no exigir que esté automatizado antes de
   poder usarlo como guía documental.
2. **Epic 004 propuesto: fuente única, bootstrap y planificación.** Tres
   ciclos candidatos, detallados en su plan. Resolver la estructura antes de
   extenderla con 003-002. No abrir una reescritura general de CDAD.
3. **Retomar epic 003:** adaptar drafts de 002; completar 002, 003 y 004 en
   ese orden, salvo un cambio de dependencias revisado y documentado.
4. **Validación real e integración:** completar un desarrollo pendiente con
   la continuidad implementada y medición suficiente; cerrar con evidencia.

El número 004 identifica un epic nuevo; no implica ejecutarlo después de
terminar 003. Es una dependencia correctiva intercalada. Como el state actual
solo representa un epic activo, no crear dos `active_epic`. En C0 elegir y
documentar una suspensión/reanudación explícita que preserve el registro de
003. No inventar una extensión de state incompatible ni un gestor multi-epic.
Hasta esa decisión, el state conserva 003 activo, como en esta actualización documental.

## 6. Contrato mínimo de cada handoff

Actualizar un documento durable **antes de despachar** y al recibir el
resultado. No depender de `/tmp`, el historial de chat o un agente vivo.

```text
Fecha, epic/feature/tarea, HEAD y cambios sin commit relevantes
Objetivo observable y postcondiciones asignadas
Rol, subfase, runtime y modelo solicitado/reportado (desconocido si falta)
Autoridad aplicable, decisiones aprobadas y pendientes
Contrato/versiones y entradas permitidas con propósito
Archivos que puede editar; archivos que no puede leer/tocar
Dependencias satisfechas; agentes/trabajo en curso e identidad de sesión
Resultado esperado, destino durable y cómo comprobarlo
Evidencia ya obtenida: comando, resultado, alcance, revisión y log
Presupuesto/reintentos consumidos; bloqueo o próxima acción exacta
Condiciones para detener, pedir contexto o devolver al architect
```

El informe original del rol se conserva íntegro; el coordinador puede añadir
un resumen, pero no sustituirlo. Antes de implementar 002, usar la captura
disponible del runtime y materialización fiel; no afirmar recepción atómica
o idempotente que todavía no existe. No afirmar hash comprobado sin calcularlo.

El handoff debe estar guardado en el repositorio antes del despacho. Hacer
commits documentales coherentes cuando corresponda, sin incluir cambios ajenos
ni forzar un commit ceremonial por cada mensaje. No hacer push automático.

### Paquete que GLM entrega a GPT/Claude

Un único índice con: objetivo; base/revisión exacta; spec/plan; diff o archivos
precisos; evidencia íntegra localizable; dudas concretas; decisiones que pide.
Separar hechos, hipótesis y opciones. Declarar limitaciones y checks no
ejecutados. El reviewer registra hallazgos, severidad, evidencia y dictamen;
el proceso registra quién resuelve los bloqueantes.

## 7. Reglas para construir sin ampliar el problema

- Usar `cdad-epic` y `cdad-cycle` vigentes. Registrar enmiendas explícitas
  cuando cambie una regla; este handoff no es una implementación de la skill.
- El coordinador no escribe tests e implementación en una misma sesión.
  El test-writer no recibe código de implementación mediante un plan, memoria
  o resumen. Review y auditoría de tests conservan sesiones independientes.
- Empezar por un RED observable sobre el contrato, GREEN mínimo y revisión.
  Ajustar pruebas existentes cuando cambie un requisito aprobado; no preservar
  un bug para que un fixture quede verde ni borrar su garantía sin reemplazo.
- Evitar tests que solo buscan frases cuando lo importante es comportamiento,
  permisos efectivos, instalación o recuperación. También evitar comparar dos
  salidas incorrectas del mismo generador como único oráculo de corrección.
- Instalar y probar primero en raíces temporales aisladas, usando
  `CDAD_INSTALL_ROOT`; no reutilizar `HOME` como variable de la tarea ni tocar
  la configuración real para ocultar un fallo del test.
- Respetar los guards de paths/symlinks, permisos y propiedad de archivos.
  No usar borrado recursivo ni sincronización destructiva sobre directorios
  generales del usuario para resolver archivos CDAD obsoletos.
- No ejecutar los validadores que instalan sin revisar antes sus destinos y
  preparar una raíz aislada. Registrar comandos exactos después de confirmarlos.
- No emitir prompts pagos desde probes de infraestructura salvo que pertenezcan
  al trabajo real autorizado. El probe OpenCode anterior no demostró aislamiento
  completo; ver [runtime-discovery](../epics/epic-003-context-efficiency/runtime-discovery.md).
- No insertar rutas personales, credenciales, IDs de sesiones reales ni logs
  privados en documentación distribuible, fixtures o commits. Usar rutas
  relativas, datos sintéticos y evidencias depuradas; preservar solo lo necesario.

## 8. Primer encargo exacto para GLM

El encargo inicial siguiente ya produjo el informe C0. Para continuar, usar
el checklist de la enmienda del 2026-09-24: spec/plan con capacidades, controles
mínimos y supervisión proporcional. Se conserva esta lista como trazabilidad
de los entregables que deben actualizarse, no rehacerse.

Verificar el estado actual y conservar/actualizar:

1. Inventario de fuentes por responsabilidad con divergencias concretas,
   consumidores y origen canónico propuesto.
2. Delta sobre el plan candidato de 004: conservar lo válido, resolver las
   decisiones abiertas y justificar cualquier división adicional.
3. Recorrido consumidor con productor de cada entrada y responsables de
   integración; capacidades/permisos comprobados del runtime elegido.
4. Contrato de autoridad y modelos propuesto para esta ejecución, sin inventar
   delegaciones ni modificar perfiles compartidos.
5. Un delta focal C0 y la spec/plan inicial de 004-001 para GPT o Claude, con la política de ADR-011 ya incorporada.

No reabrir 001/005 como si siguieran incompletas. Corregir sus limitaciones
mediante los nuevos ciclos. No comenzar 003-002 sobre las copias manuales antes
de resolver C0. Mantener progreso independiente mientras la revisión esté
pendiente, y terminar el handoff con una próxima acción inequívoca.
