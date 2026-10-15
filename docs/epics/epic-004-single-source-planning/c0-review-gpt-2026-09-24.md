# Dictamen técnico C0 — revisión GPT

Fecha: 2026-09-24. Receptor: orquestador GLM.
Objeto: propuesta de preparación C0 del architect, materializada en
`c0-architect-report-2026-09-24.md`, y decisiones D1–D10.
Base de revisión: HEAD `9edda07`; código sin cambios respecto de `4a821a0`.

## Dictamen y siguiente paso

**CHANGES REQUIRED — corrección focal de C0, sin rediseño general.**

La dirección y las tres features son técnicamente razonables: fuente única y
distribución → bootstrap → procedimientos de planificación, antes de 003-002.
El inventario justifica el trabajo. Mantener roles existentes, separación de
generación/instalación, compatibilidad Odoo/legacy y revisión de planes.

Antes de declarar C0 conforme, corregir tres decisiones: D9 (estado al activar
004), D2 (criterio de mantenimiento) y las afirmaciones de runtime de §3.2/§5.
Los cambios solicitados son documentales; no requieren repetir el discovery
completo, ejecutar un desarrollo ni convocar otro comité de revisión.

GLM puede preparar las correcciones y la spec/plan de 004-001. No iniciar
construcción ni cambiar el state hasta resolver el dictamen y registrar la
aprobación estratégica aplicable. Esta revisión no activa el epic ni concede
a GLM una delegación HITL. El usuario ya eligió GLM para desarrollar: esa
selección no necesita otra confirmación.

## Alcance de la revisión y evidencia

Revisión estática del informe completo, dispatch record, documentos base y
fuentes relevantes de roles, state, renderer, instalador y consumidores de
tests. Se reprodujo el conteo de archivos/líneas/bytes. No se ejecutaron suite,
instalación, validadores completos, llamadas a proveedores ni probes runtime.
No se presenta la corrida histórica de 52 tests como evidencia nueva.

Los tres documentos base siguen sin trackear en el árbol inspeccionado. Para
identificar exactamente la propuesta revisada, SHA-256 calculados en esta revisión:

| Documento | SHA-256 |
|---|---|
| `plan.md` | `5582700515052c5ddfc65669bb33cde8a237c02a9b35843945d748478eaee5ac` |
| `planning-contract-draft.md` | `aced513dd54f513bbda29ba9d38859828bfc4087f388f833fe782086993742b6` |
| `../../handoffs/2026-09-23-glm-continuation.md` | `d359787bda321a72ebc74dffeb5eea877667a0561f1d6257a1141871e4a367a4` |

Estos hashes identifican los bytes leídos; no sustituyen guardar los documentos
en el commit del paquete aprobado antes de construir o trasladar el trabajo.

## Correcciones requeridas para C0

### C0-R1 — D9 mantiene un epic distinto del trabajo ejecutado

Prioridad: alta. Evidencia: informe `:167`, §6 VERIFY 6; detección del ciclo
en `skills/cdad-cycle/references/state-detection.md:27-38`; detección de epic
en `skills/cdad-epic/references/state-detection.md:9-17,39-45`.

Mantener 003 activo es correcto **mientras 004 es una propuesta**. No constituye
una solución para ejecutar los ciclos 004-001/002/003: la siguiente sesión
leerá 003 como contexto activo, puede cargar su plan y retomar su cola. Eso
contradice el objetivo de continuidad sin depender de la memoria del chat.

Precisión importante: `cdad_packet.py:219-221` retorna `ordinary` sin exigir
igualdad con `active_epic/active_feature`; por tanto no afirmo que el CLI vaya
a rechazar automáticamente esa configuración. Que la acepte no demuestra
coherencia del proceso. `prepare` además actualiza `state.execution` y
`active_packet` (`:590-595`), por lo que "cero churn del state" tampoco describe
la ejecución real de paquetes.

**Cambio pedido:** D9 debe distinguir preparación de activación. Antes de
activar 004, conservar snapshot/handoff de 003 con su progreso, decisiones y
autoridad, registrar suspensión documental y hacer que el único state activo
represente 004. Al retomar 003, reconciliar el progreso conservado con el estado
actual; no restaurar ciegamente un JSON antiguo que borre nueva historia.
Proponer los pasos exactos y los campos afectados en la activación; no añadir
un motor multi-epic ni un nuevo valor de etapa sin soporte.

**Criterio de resolución:** una sesión nueva identifica el epic/feature correctos
durante 004, y la reanudación posterior encuentra 003-001/005 done y las demás
pendientes, sin heredar una delegación a otro agente/epic.

### C0-R2 — D2 confunde longitud con mantenimiento y usa una suma incorrecta

Prioridad: media. Evidencia: informe `:29`, `:160-161`, `:174`, §6 VERIFY 5.

Las cifras por archivo del informe son reproducibles, pero su suma no lo es:

| Grupo | Archivos | Líneas (LF) | Bytes UTF-8 de archivos completos |
|---|---:|---:|---:|
| OpenCode | 11 | 1.572 | 79.127 |
| Claude Code | 11 | 1.125 | 61.034 |
| Total | 22 | **2.697** | **140.161** |

Las diferencias con los subtotales informados son 97 y 46 líneas: coinciden
con ambos scribe-odoo, listados pero aparentemente omitidos de la suma.
Verificación: `rg -c '' agents/cdad-*.md agents/claude-code/cdad-*.md`, sumado
por directorio, y lectura binaria independiente (`count(b'\n')`, `len(bytes)`).
Estos bytes incluyen frontmatter: **no son contexto cargado ni tokens**.

Aunque la suma se corrigiera, fuentes + generador + manifest ≤ líneas de las
copias no demuestra menor mantenimiento. Puede penalizar validaciones claras
y premiar comprimir código o prosa sin eliminar una dependencia manual.

**Cambio pedido:** mantener conteos como diagnóstico y aceptar como requisitos:
salidas declaradas generadas sin edición manual; cada regla compartida tiene
una única fuente editable; un cambio de regla se propaga con una regeneración
reproducible; adaptadores contienen diferencias justificadas; no se agrega un
framework general. Informar tamaño y costo de mantenimiento, explicar aumentos
y revisar complejidad si aparecen, sin un veto automático por líneas.

Medir la línea base de instrucciones antes del refactor es útil y barato;
conservar método, versión y configuración. No afirmar que es imposible
recuperarla después: el source está versionado. La configuración efectiva sí
debe capturarse si puede cambiar. En packet-path contar agente + instrucciones
del paquete + lecturas aplicables, no solo su bloque estático. Separar entradas
sintéticas de componentes estáticos y no llamar a esa suma consumo observado.

**Criterio de resolución:** reemplazar D2 y su condición de cierre, corregir
sumas en la propuesta operativa y precisar el alcance de T1. El informe
original puede conservarse con errata enlazada, sin fingir que dijo otra cosa.

### C0-R3 — Las garantías de Codex se trasladaron a OpenCode

Prioridad: alta. Evidencia: informe R5 `:86`, §3.2 `:202-213`, §5 hecho runtime
`:278`; dispatch record `:52-60`; `runtime-discovery.md:7-12,20-28,53-68`.

La afirmación sobre filesystem compartido y ausencia de política configurable
por hijo pertenece a **Codex nativo** en la fuente citada. El fallo observado
del smoke **OpenCode** fue la lectura de configuración heredada fuera de las
raíces temporales. Ni eso ni compartir filesystem prueban ausencia de controles
de acceso mediados por herramientas/hooks en OpenCode.

Además, el informe llama "confirmadas" a capacidades expuestas por ayuda/tipos
y presenta versiones históricas bajo un título de runtime comprobado hoy,
aunque sus propias limitaciones reconocen que no verificó la versión actual.
El smoke documentó un subconjunto de endpoints de sesiones vacías; no ejercitó
llamadas a modelos, routing ni aislamiento de roles.

**Cambio pedido:** separar runtime, fecha y tipo de evidencia: observado en
Codex; expuesto por ayuda/tipos OpenCode; probado en sesiones vacías; pendiente
de comprobación efectiva. Reemplazar "sin sandbox" por la garantía concreta
no demostrada cuando corresponda. Mantener la restricción de no repetir el
probe sin resolver su contaminación de configuración, pero permitir una
comprobación acotada y segura de la capacidad de la que dependa el contrato.

**Criterio de resolución:** §3.2 y el paquete C0 no atribuyen al runtime elegido
propiedades de otro runtime ni convierten desconocidos en ausencia comprobada.
No hace falta ejecutar ahora un probe para corregir esa clasificación.

## Decisiones aceptables y precisiones para las specs

- **D1:** Markdown + generador Python stdlib es una opción razonable. Corregir
  la justificación: JSON tiene parser en stdlib y no impide generar prompts
  autocontenidos; ese argumento no permite descartar JSON. Elegir por facilidad
  de autoría/composición. La spec fija ubicaciones, delimitadores y errores
  de fuente incompleta/duplicada antes de implementar. 400–700 líneas es una
  estimación, no un requisito ni evidencia de costo.
- **D4:** manifest + dry-run es razonable. La spec debe proteger un archivo
  instalado que el usuario modificó después: propiedad histórica no autoriza
  borrarlo silenciosamente. Comparar contra la versión registrada, informar
  conflicto y resolver antes del borrado. Definir también primera instalación
  sin manifest, rutas fuera de destino/symlinks, fallo parcial y uninstall.
- **D5:** congelar edición de salidas generadas, con origen/comando de
  regeneración visibles. No prohibir editar fuentes legítimas por llamarse agente.
- **D6:** retirar layout público del default. Dependencia de fixtures confirmada
  en `tests/test_role_packet_consumers.py:39-46,61-67` y
  `tests/test_role_packet_review_regressions.py:231-335`. Migrar sus garantías a
  destinos runtime reales. Mantener un opt-in solo si hay consumidor/contrato
  de compatibilidad que lo justifique, no únicamente para conservar el fixture.
- **D7:** conservar garantía F001 hasta sustituirla en el mismo cambio coherente.
- **D8:** representar explícitamente la revisión de borradores, sin aprobación
  falsa. El mecanismo final pertenece a 004-003; hoy puede usarse handoff legacy
  identificado para planificar/revisar el propio 004.
- **D10:** mantener tres features. La medición T1 es preparación/evidencia, no
  una feature ni una ceremonia TDD obligatoria por sí misma. Arquitectura,
  adaptadores e instalación sí requieren sus verificaciones contractuales.
- **Política de modelos:** GLM construye y GPT/Claude revisan conforme a la
  elección del usuario. Recomiendo proponer una enmienda del criterio final de
  003 que refleje ese reparto, con medición de todas las llamadas gestionadas,
  evitando una segunda construcción solo para demostrar modelo único. No se
  aprueba ni aplica aquí esa enmienda.

## Observaciones de entrega que GLM debe corregir

1. El reporte conserva un identificador real de sesión en su envoltorio XML
   (`c0-architect-report-2026-09-24.md:5`). Para el paquete distribuible, extraer
   el cuerpo del resultado y conservar trazabilidad local fuera del artefacto
   público. No altera el contenido del informe. No afirmar anonimización total
   por haber eliminado rutas. No reescribir historia Git ni hacer force-push;
   corregir la copia vigente y registrar la sanitización.
2. Antes de construir, versionar los documentos base y el delta aceptado para
   que otra máquina pueda revisar/ejecutar los mismos contratos. Referenciar
   solo el commit del informe mientras las fuentes quedan sin trackear no basta.
3. La divergencia de property tests es real, pero ya estaba señalada en el
   diagnóstico anterior; no presentarla como hallazgo nuevo necesario para
   justificar más alcance. La omisión de `cdad-spec-and-test` en el legacy del
   architect genérico Claude Code también está comprobada (`:17`), respecto de
   su equivalente OpenCode (`:65`); mantenerla en la corrección de intake.

## Re-entry exacto para GLM

1. Conservar el informe original como evidencia; producir un delta C0 breve que
   resuelva R1–R3 y enlace este dictamen desde el registro de despacho.
2. Corregir/sanitizar el envoltorio distribuible y versionar los documentos
   necesarios sin mezclar cambios ajenos. Mantener privacidad y sin push automático.
3. Presentar el delta, el procedimiento de activación y la spec/plan inicial de
   004-001. Una relectura focal de R1–R3 basta; no repetir el informe completo.
4. Tras dictamen conforme y aprobación estratégica registrada, activar 004 con
   state coherente y ejecutar el ciclo con los roles separados. Mientras tanto,
   sigue válido el trabajo independiente de §4.2 del informe.

Esta revisión no cambia state, código, agentes, instalación ni las decisiones
aprobadas del epic 003. El original del architect no se editó en este turno.

## Adenda — causa del error de agregación

La inspección posterior del registro real confirma seis llamadas de medición
rechazadas y una salida alternativa con los 22 conteos correctos, antes de
publicar la suma incorrecta. Hay una omisión comprobada del par `rtk wc` en
la allowlist; el rechazo de llamadas registradas como `wc` simple requiere
atribución adicional. Ver [análisis de fricción de permisos](../../../findings/permission-friction-c0-2026-09-24.md).

R2 conserva su corrección de números y del criterio de mantenimiento. La causa
del incidente no debe reducirse a aritmética de GLM: la fricción del entorno
contribuyó a reemplazar la operación determinista directa por una agregación
no verificada. Incorporar el hallazgo al diseño de capacidades de 004 sin
desactivar globalmente los controles ni ampliar el número de epics.


## Evolución de la propuesta — 2026-09-24

El usuario pidió cambiar el enfoque de control hacia autonomía supervisada.
La [enmienda de C0](c0-amendment-supervised-autonomy-2026-09-24.md) incorpora
las correcciones R1–R3 al plan y agrega ADR-011 como decisión metodológica
vigente. Los hashes de este dictamen identifican la versión anterior revisada;
no describen los documentos actualizados. La siguiente revisión es focal sobre
la spec/plan de 004-001 y el procedimiento de activación. No reabrir la elección
metodológica ya autorizada ni declarar esta implementación como terminada.
