# SPEC draft — 010-004: ergonomía del despacho de paquetes

**Estado:** borrador v3, revisado conforme a `owner-decision-v2-new-assignments.md`; pendiente de revisión y aprobación explícita de Pablo.
**Base:** Discovery y plan-review de esta unidad.  
**Autoridad:** plan aprobado de `epic-010-documentary-specialization` y UNIT-CONTRACT del encargo. Este borrador no modifica ninguno de ellos.

## 1. Objetivo funcional

Permitir que el orquestador despache un encargo sin retranscribir su cuerpo y que el rol encuentre el contexto de ejecución sin inferirlo. Ante un rechazo, ofrecer una causa accionable sin divulgar el contenido del encargo.

La propuesta reutiliza el renderer, la ruta C y los validadores existentes. No incorpora otro protocolo de encargos ni promete una conexión mecánica con herramientas nativas que el repositorio no demuestra.

Se mantienen separados:

1. Integridad del paquete publicado.
2. Observabilidad de la entrega.
3. Fidelidad del resultado al contrato y las fuentes.

## 2. Decisiones contractuales pendientes

### 2.1. Tensión entre plan y observaciones

El plan aprobado menciona contexto explícito y emisión de ruta C por el renderer (`docs/epics/epic-010-documentary-specialization/plan.md:123-130`). Las observaciones piden no fijar el mecanismo antes de Discovery (`observations-packet-dispatch.md:36-46`).

Se propone:

- Confirmar la emisión de C como solución de esta unidad.
- Entender «sin retranscripción» como **cargar el cuerpo desde el paquete publicado**, no como prueba de conexión mecánica renderer→herramienta nativa.
- Preferir C para nuevos despachos nativos.
- Conservar A como alternativa explícita y el render completo como salida predeterminada.
- No exigir una prueba independiente del mensaje recibido sin capacidad demostrada del runtime.

La aprobación y su trazabilidad deben resolver expresamente esta tensión; no se modifica ni reinterpreta silenciosamente el plan.

### 2.2. I-4: falta de observabilidad

Se conserva la disposición acordada (`observations-packet-dispatch.md:48-72`):

- Una evidencia insuficiente de entrega no demuestra corrupción.
- Por sí sola no obliga a repetir todo el trabajo.
- Debe registrarse la limitación y contrastarse el resultado con contrato y fuentes.
- No permite ignorar divergencias conocidas, autoridad inválida ni contenido infiel.

### 2.3. I-5: divergencia comprobada

El despacho reviewer rechazado perdió backticks durante la transcripción, aunque los archivos publicados eran íntegros (`observations-packet-dispatch.md:74-90`).

Ese rechazo se conserva. No es un caso de mera noobservabilidad ni se rescata cambiando retrospectivamente a C. La recuperación requiere un **nuevo encargo válido**, con los gates correspondientes.

### 2.4. Decisión del owner: encargos nuevos v2

`owner-decision-v2-new-assignments.md:3-15` resuelve N-1: la nueva emisión C es v2-only y **toda preparación o encargo nuevo utiliza ejecución v2**, también al continuar un proyecto viejo. No basta con restringir C.

v1 se conserva para reconocer, validar y retomar lo histórico bajo las condiciones existentes. No se reescriben sus archivos, se elimina su soporte ni se convierte su replay en permiso para preparar nuevos encargos v1.

Esta decisión no aprueba la spec completa, no resuelve §2.1 y no aporta por sí sola autoridad, aprobación ni pin para cada proyecto viejo. La frontera operativa se especifica en §4.1.

## 3. Alcance

### Dentro

- Contexto explícito en request y cabecera de toda nueva publicación.
- Ejecución v2 para toda preparación nueva, incluidos sucesores y recuperaciones que publiquen una nueva generación.
- Eliminación de la selección implícita v1 para preparación nueva cuando falta policy.
- Resolución compartida en `render`, `validate-request` y `validate-packet`.
- Emisión C v2-only desde `render`.
- Comprobaciones compartidas de dominio, identidad y schema del localizador; comprobaciones de ruta en las superficies expresamente indicadas en §4.1.
- Conservación de reconocimiento, validación, render y reentrada históricos bajo sus condiciones existentes.
- Instrucciones de intake, despacho, handoff, preparación y re-entry pertinentes.
- Fuentes y agentes derivados de OpenCode y Claude Code.
- Verificación de un consumidor instalado aislado.

Superficies principales:

- `skills/cdad-cycle/scripts/cdad_packet.py` y su wrapper.
- Intake compartido en `sources/roles/architect.md`.
- Despacho en `sources/roles/orchestrator.md`.
- `sources/agents/adapters/{opencode,claude-code}.md`.
- `skills/cdad-cycle/references/handoff-prompts.md`.
- `skills/cdad-cycle/references/project-execution.md`, para expresar consistentemente la frontera entre preparación nueva y recuperación histórica.
- Instrucciones de re-entry que describan las evidencias comprometidas.
- Salidas generadas correspondientes.

### Fuera

- Cambiar las opciones o la resolución de contexto de `cdad_result.py receive/run/validate-run`.
- Rediseñar la selección de ejecución de `prepare`, salvo impedir toda publicación nueva v1 y declarar/comprobar el localizador v2 antes de publicar.
- Ampliar a v1 el resolvedor por identidad o los consumidores que actualmente requieren v2.
- Cambiar el transporte externo, sus registros o sus recibos.
- Conectores o interceptores nativos.
- Nuevos ledgers, recibos o protocolos de entrega o migración.
- Certificación automática de fidelidad semántica.
- Cambios de modelos, permisos, separación de roles o autoridad.
- Migración automática v1→v2; reescritura, renombrado o destrucción de archivos históricos.
- Actualización de la instalación global, push o publicación.

Los consumidores que ya llaman validadores comunes seguirán comprobando el request extendido en los términos de §4.1. Esto no convierte sus opciones de contexto en opcionales ni les añade una comparación entre la ruta de su argumento y el localizador.

## 4. Contrato propuesto

Las interfaces y campos nuevos de esta sección son propuestas, no capacidades ya implementadas.

Actualmente, los tres comandos afectados exigen `--execution-context` y cargan su ruta relativa al directorio de invocación (`cdad_packet.py:9485-9491,9900-9914`). El request tiene un conjunto cerrado de campos opcionales (`:1595-1612`).

### 4.1. Localizador del contexto y frontera histórica

Se añade `execution_context` como propiedad opcional del esquema del request para conservar la admisión de requests históricos. Toda nueva publicación canónica debe declararla.

«Nuevo» significa una nueva preparación/publicación del encargo, no simplemente la presencia del campo. Omitirlo no habilita a un productor a publicar un nuevo encargo v1.

La versión del contexto de ejecución es independiente de `schema_version: 1` del request y de `packet_version: 1`; esta unidad no cambia esas versiones.

#### Dominio del localizador

Cuando está presente, `execution_context` debe ser una cadena project-relative segura con la forma exacta:

`.cdad/executions/<execution_id>/execution.json`

`<execution_id>` coincide con el del request y cumple el dominio de nombre plano ya utilizado por `_load_execution_context` (`cdad_packet.py:2945-2955`).

Se rechazan localizadores absolutos, vacíos, con escapes, componentes alternativos o ubicaciones diferentes. Se conserva la comprobación de pertenencia real al proyecto, incluida la resolución de enlaces (`:295-310`).

El documento cargado debe tener schema v2 e identidad de ejecución y feature concordantes. Una copia en otra ubicación no es un localizador admitido aunque contenga la misma identidad.

`.cdad/execution.json` no pertenece al dominio del campo nuevo. Su uso explícito para un request histórico v1 sin campo se conserva por la vía histórica descrita abajo; no se convierte en preparación nueva.

`execution.authority_ref` continúa identificando la fuente de autoridad, no la ubicación del contexto.

#### Responsabilidad de cada capa

- **Validación compartida del request:** cuando existe el campo, comprueba dominio seguro, concordancia con `execution_id`, schema v2 del documento suministrado y las identidades correspondientes. Conserva las comprobaciones vigentes de estado, política, contrato, aprobación y binding.
- **Resolución de los tres CLI:** `render`, `validate-request` y `validate-packet` cargan el contexto según la matriz siguiente. Cuando hay localizador y argumento explícito, comparan ambos archivos canónicos.
- **Emisión C:** añade las restricciones publicadas y de contexto canónico v2 de §4.2, incluso para requests históricos sin campo.
- **Preparación/publicación nueva:** comprueba contexto v2 y su ubicación canónica antes de publicar e incorpora el localizador en request y cabecera.

`validate_request` recibe el documento de contexto, no la ruta desde la que el consumidor lo cargó (`cdad_packet.py:1582-1595`). No se le atribuye una comparación que su interfaz no puede realizar.

En particular, esta unidad no añade a `cdad_result` un rechazo por haber recibido su documento mediante una copia byte-idéntica en otra ruta: mantiene su resolución y controles existentes, más los checks compartidos del campo cuando aparece. La aceptación sigue dependiendo de los demás controles; no se promete aceptación universal de copias.

#### Raíz y argumentos

- El localizador del request se interpreta respecto de la raíz canónica del proyecto.
- Sin `--project-root`, la raíz continúa siendo el directorio actual.
- La independencia respecto del directorio de invocación exige declarar la misma raíz, normalmente mediante una ruta absoluta.
- Las rutas CLI de `--request`, `--packet` y el argumento explícito `--execution-context` mantienen su interpretación histórica: las relativas lo son al directorio de invocación.
- Desde otro directorio deben proporcionarse argumentos de archivo válidos allí, por ejemplo absolutos.

Una raíz explícita no cambia automáticamente la interpretación histórica de todos los argumentos.

#### Matriz de resolución

La tabla rige por igual para `render`, `validate-request` y `validate-packet`:

| Request | `--execution-context` | Resultado |
|---|---|---|
| Con localizador | Ausente | Resolver exclusivamente el localizador v2 y validar. |
| Con localizador | Presente | Validar el localizador y exigir que el argumento resuelva al mismo archivo canónico. Si discrepan, rechazar. |
| Histórico, sin localizador | Presente | Conservar la carga explícita y la validación existentes, incluidas las condiciones v1/v2 aplicables. |
| Histórico, sin localizador | Ausente | Rechazar por contexto no proporcionado. No añadir fallback por `execution_id`. |

«Resolver» no implica aceptar: los demás controles siguen siendo obligatorios. No se prueba otra ubicación cuando falla el localizador.

Las restricciones nuevas del localizador no se aplican retrospectivamente a las rutas explícitas admitidas para requests históricos sin campo.

El resolvedor v2 por identidad existente puede reutilizarse donde corresponda. Su uso en `verify_published_packet` no autoriza añadir un fallback a estos tres CLI (`:1974-1980,2945-2955`).

#### Toda preparación nueva utiliza v2

La regla incluye preparación ordinaria, sucesores de reemplazo y recuperaciones que publiquen una nueva generación, aunque el trabajo proceda de un proyecto viejo o conserve el objetivo de un encargo anterior.

- Toda nueva publicación declara en request y cabecera el localizador del contexto v2 realmente seleccionado.
- Antes de publicar se comprueban schema v2, identidad y ubicación canónica.
- Se rechaza una selección v1 tanto explícita como implícita, también cuando falta `docs/cdad-policy.json`. No se publica ni se copia, convierte o reubica el contexto para hacerla pasar.
- Se conserva la selección/reutilización v2 y sus gates existentes.
- Un sucesor nuevo incorpora el localizador aunque su predecesor v2 histórico no lo tuviera. No se añade retrospectivamente al predecesor.
- Una recuperación que solo verifica o reemite bytes históricos no constituye una preparación nueva. Si publica una nueva generación, sí queda sujeta a esta regla.
- No se amplía a v1 ninguna vía de reemplazo o recuperación que actualmente requiere v2.

**Delta comprobado:** hoy `_select_execution` devuelve un contexto v1 cuando no existe policy (`cdad_packet.py:2928-2942`); `prepare` consume esa selección (`:6202`) y permite binding v1 (`:6433-6441`). Esta spec elimina esa posibilidad para nuevas publicaciones. El rechazo de v1 explícito ya existe (`:2898-2911`); conservarlo no basta para cerrar la vía implícita.

#### Reentrada y replay históricos

Reconocer o validar un contexto v1 no autoriza su adopción hacia adelante. Se mantienen `validate_state` y `validate_request` con sus condiciones existentes, sin declarar todo legado automáticamente válido (`:1181-1233,1582-1788`).

Para un request histórico sin localizador:

- Los tres CLI conservan la vía de contexto explícito de la matriz.
- La ausencia del campo no añade metadatos al render.
- El render completo y el intake A pueden utilizarse para contrastar/reemitir lo histórico cuando satisfagan íntegramente las condiciones vigentes.
- No se reescriben request, paquete o contexto para adecuarlos al renderer actualizado. Si el cotejo falla, se conserva el archivo y se diagnostica el rechazo.
- No se restaura automáticamente un binding anterior ni se rebajan autoridad, aprobación, contrato o vigencia para conseguir el replay.

`prepare --resume-packet` es la vía existente de reemisión byte-identical, no de creación de encargos. No admite opciones ordinarias de preparación (`project-execution.md:121-129`).

**Límite real:** su implementación actual carga el contexto por identidad v2 y exige los controles de revisión de policy y contrato (`cdad_packet.py:3017-3087`). Por tanto, esta spec no promete que ese submodo funcione para un paquete exclusivamente v1, ni lo amplía a v1. La reentrada v1 conserva sus vías explícitas existentes; no se la bloquea silenciosamente presentándole ese submodo como solución universal.

#### Nuevo trabajo v2 al retomar un proyecto viejo

Se utiliza el procedimiento existente, no un protocolo de migración nuevo:

1. Reconocer lo existente y distinguir recuperación histórica de preparación nueva.
2. Comprobar la policy owner-owned y la autoridad del rol conforme a `project-execution.md` §§1–2. `--propose-policy` puede producir una propuesta sin escritura; corresponde al owner decidir y materializar la policy.
3. Para abrir una ejecución nueva cuando existe contexto previo, usar el bootstrap existente de §3 con `prepare --new-execution`, una vez satisfechos sus requisitos. No pasar el documento v1 como contexto de trabajo.
4. Si ya existe una ejecución v2 coherente que debe reutilizarse, usarla conforme a la selección vigente; no crear otra innecesariamente. Se conserva el rechazo `state incoherent` ante un contexto abierto y sin usar (`cdad_packet.py:2912-2927`).
5. Resolver previamente los bloqueos de paquete activo y los gates aplicables solo cuando exista un mecanismo aplicable. Para un paquete v1 activo no terminal, incluido `prepared`, no hay una ruta CLI terminal existente: se diagnostica esa causa y se escala al owner, sin modificar state ni preparar v1. Se acepta explícitamente esta laguna y su escalación conforme a `owner-decision-v2-new-assignments.md:7,13`; no se promete un procedimiento inexistente. `--new-execution` no elude el bloqueo.

La autoridad no se deduce de esta decisión general de producto:

- Para architect con épica activa, se exige la aprobación del plan en `epic_history`; no se inventa un pin de spec para habilitar arquitectura.
- Para los demás roles sobre contrato aprobado, se conserva la aprobación específica vigente con `contract_path` y `contract_sha256` concordantes.
- Se conserva la excepción existente del objeto `draft-plan` de revisión: revisarlo no equivale a aprobarlo ni requiere fingir una aprobación.
- La delegación y su vigencia se comprueban cuando corresponde a una épica activa; no se fabrica una épica para un proyecto standalone.

Referencias: `project-execution.md:52-119`; `_contract_approval_for`, `_validate_v2_vigency` y `_bootstrap_v2_execution` (`cdad_packet.py:2560-2805`).

Si faltan requisitos, se informa la causa y la continuación concreta:

| Situación | Continuación |
|---|---|
| Legado sin policy para trabajo nuevo | Identificar la configuración faltante; proponer la policy y pedir decisión/materialización al owner antes del bootstrap v2. No preparar v1. |
| Aprobación o pin ausente/desactualizado | `approval pending`: indicar el contrato y el registro que corresponde obtener o corregir mediante la autoridad competente. |
| Paquete v1 activo no terminal, incluido `prepared` | Diagnosticar el bloqueo y la ausencia de una ruta CLI terminal existente; escalar al owner, dejando state intacto y sin preparar v1. No indicar «completar o fallar» como procedimiento disponible ni añadir migración o withdraw v1. |
| Otros estados/bindings, unidades o paquetes activos incompatibles | Diagnóstico de incoherencia con el registro implicado; usar el procedimiento existente solo si es aplicable. Si no existe, declarar la laguna y escalar al owner sin modificar state ni preparar v1. No borrar bindings ni decisiones para desbloquear. |
| Architect standalone sin mandato de épica | Conservar el diagnóstico legacy existente de `_contract_for` (`:2060-2072`); orientar reconocimiento y aclaración del mandato. No fabricar un contrato de épica ni emitir un nuevo paquete v1. |
| Replay no admitido por su vía actual | Identificar el límite y las vías históricas explícitas aplicables; si se requiere otro encargo, aplicar los requisitos de preparación v2. |

No existe aquí una garantía de conversión de cualquier estado viejo en estado v2 ejecutable. Cuando la evidencia o el mecanismo existente no basten, se declara la laguna y se escala la decisión al responsable; no se inventa autoridad, una migración automática ni una aceptación retrospectiva.

El bootstrap puede publicar el nuevo contexto y actualizar el binding conforme al procedimiento autorizado. No convierte ni destruye los archivos v1 y no reescribe paquetes históricos.

### 4.2. Emisión de ruta C — solo ejecución v2

Interfaz propuesta:

```text
cdad_packet.py render --project-root <raíz> --request <REQUEST.json> --route C
```

Se admite `--execution-context` conforme a la matriz de §4.1. Sin `--route C`, `render` sigue emitiendo el paquete completo.

C puede representar un paquete v2 histórico sin localizador si se suministra el contexto explícito exigido por la matriz. Emitir una identificación para ese paquete existente no es preparar un encargo nuevo ni añade campos a sus archivos.

#### Binding con el request publicado

Para emitir C:

1. `--request` debe designar el propio archivo publicado en `.cdad/packets/<packet_id>/REQUEST.json`, dentro de la raíz indicada.
2. No basta una copia fuera de esa ubicación, aunque sea byte-idéntica.
3. El contexto seleccionado debe tener schema v2 y resolver al archivo canónico `.cdad/executions/<execution_id>/execution.json`. Esto también se exige si el request histórico no declara localizador.
4. Un contexto v1 se rechaza con diagnóstico explícito: C requiere v2. No se intenta buscar un contexto v2 inexistente como si fuera un error incidental ni se convierte el legado.
5. Se valida el request con el contexto seleccionado.
6. Se verifica el `PACKET.md` publicado completo mediante `verify_published_packet`, que carga el contexto por identidad v2. La identidad y el archivo deben concordar con los ya seleccionados.
7. Solo después se emite la identificación.

El verificador publicado conserva su resolución v2 y su frontera de comparación. No se amplía para aceptar v1 ni se cambia la resolución de sus otros consumidores.

Una copia o request alternativo no puede generar una identificación para el paquete publicado. Estas restricciones adicionales pertenecen a la nueva salida C; no modifican la interfaz histórica del render completo.

#### Representación

La salida utiliza la identificación de la ruta C existente:

- Una línea literal `Route C — explicit file backup`.
- Un único bloque Markdown delimitado por una línea de apertura de tres backticks seguida de `json` y una línea de cierre de tres backticks.
- Un objeto con:
  - `project_root`;
  - `packet_id`;
  - `execution_id`;
  - `execution_context`;
  - `request`;
  - `packet`;
  - `contract`, conservando todos sus campos declarados y su digest.

`project_root` identifica la raíz absoluta canónica utilizable por el receptor. Las referencias a request, paquete y contexto son project-relative; el receptor las resuelve contra esa raíz.

La identificación no utiliza el marcador de cabecera de A. No reproduce instrucciones, objetivo, entradas, scopes ni cuerpo del encargo.

Para iguales archivos, raíz y configuración relevantes, la salida es determinista. No modifica `REQUEST.json`, `PACKET.md` ni el estado. Si falla una comprobación, no emite una identificación utilizable.

Es una vista del paquete existente, no otro contrato. Su tamaño depende de los metadatos, no de la longitud del cuerpo.

### 4.3. Admisión del rol y precedencia

Las instrucciones comunes deben expresar sin ambigüedad:

#### Ruta A

- Se cuentan primero las líneas de marcador A.
- Exactamente una apertura y su cierre de cabecera son necesarios.
- **El cierre JSON termina la cabecera, no el paquete.**
- La comparación comprende desde el marcador inicial hasta el final del paquete recibido, incluido todo el cuerpo.
- Una divergencia no se reconstruye ni normaliza para admitirla.

#### Ruta C

- Requiere contexto v2 canónico conforme a §4.2. Un contexto v1 recibe diagnóstico explícito; no se cambia silenciosamente a A ni se prepara otro encargo.

- Requiere declaración explícita y una sola identificación del paquete publicado.
- El rol contrasta todos sus metadatos con los archivos nombrados y el contexto validado.
- Valida el request y compara el paquete publicado completo contra el render canónico antes de trabajar.
- No necesita cuerpo inline.
- No busca otro paquete si el nombrado falla.
- Las lecturas de control-plane no amplían el scope de producto.

#### Mezcla y fallback

Para eliminar la ambigüedad, las dos formas se usan de manera exclusiva:

- Un dispatch que contiene identificación C **y** paquete inline A se rechaza por mezcla de rutas, aunque el inline coincida.
- La presencia de un inline divergente nunca permite seleccionar C para rescatarlo.
- Un cuerpo parcial tampoco sustituye la identificación C.
- Los marcadores A duplicados no se resuelven eligiendo uno.
- Un prompt que afirma ser un paquete pero no satisface su admisión se rechaza; no pasa silenciosamente a legacy.

Esta regla se comprueba en las instrucciones de intake y despacho. No se promete un parser nuevo que intercepte todos los prompts nativos.

Un preámbulo del runtime no autoriza ni modifica el encargo. Las palabras del objetivo o referencias incidentales a una ruta no sustituyen su identificación explícita.

### 4.4. Fronteras de comparación y preámbulo

Se conservan las diferencias actuales:

| Superficie | Comparación |
|---|---|
| `validate-packet --packet` | Archivo suministrado completo contra el render. No elimina preámbulo. |
| Verificación publicada utilizada para C | Contexto canónico v2 cargado por identidad mediante `verify_published_packet`; comparación desde el único marcador A del archivo publicado hasta su final. No admite contexto v1. |
| Intake A del rol | Desde el marcador A del mensaje hasta el final del paquete recibido. |

El preámbulo anterior al marcador puede ser transparente en las dos últimas superficies sin serlo en la primera.

Por tanto, `validate-packet` no se presenta como un validador de un mensaje completo con envoltura del runtime. Un archivo canónico sin envoltura debe pasar por las superficies aplicables.

No se unifica esta diferencia en esta unidad: no es necesario para emitir C y hacerlo ampliaría el cambio. Nunca se ignora contenido posterior al marcador.

Base: `cdad_packet.py:1885-1932,1981-1985,9911-9914`.

### 4.5. Diagnósticos seguros

En las superficies afectadas se distinguen:

- Identificación ausente, malformada, ambigua o mezcla de rutas.
- Contexto no proporcionado, inválido o discordante.
- Localizador fuera del dominio o distinto de la ubicación canónica.
- Request no publicado en la ubicación requerida para C.
- Autoridad, aprobación, contrato o binding inválidos.
- Divergencia del paquete completo.

Cada diagnóstico ofrece causa y siguiente acción pertinente: proporcionar el argumento exigido, obtener la identificación generada, utilizar el contexto canónico conocido o volver al responsable de autoridad/publicación.

C con contexto v1 informa que C requiere v2; distingue el uso histórico del paquete de la preparación de otro encargo. No recomienda convertir el archivo ni sugiere que cambiar de ruta rescate una entrega divergente.

La preparación nueva sobre legado informa los requisitos faltantes de §4.1: policy, autoridad/aprobación/pin o coherencia de estado. La continuación identifica al responsable y un procedimiento existente solo cuando sea aplicable. Para un paquete v1 activo no terminal, incluido `prepared`, el resultado observable único es diagnosticar el bloqueo y la ausencia de ruta CLI terminal existente y escalar al owner, sin modificar state ni preparar v1; no se promete una salida operativa inexistente. Un diagnóstico legacy no autoriza preparación v1 ni acredita una consulta como dispatch CDAD.

Cuando se conoce la referencia esperada, se presenta de manera segura y project-relative. No se imprimen fragmentos del cuerpo, diffs textuales del encargo ni valores arbitrarios potencialmente sensibles.

Se conservan los códigos de salida y las envolturas existentes. Un rechazo no publica archivos, registra intentos, recibe resultados ni cambia estado.

Las instrucciones del rol describen su diagnóstico requerido; no se presentan como enforcement mecánico de su conducta.

### 4.6. Distribución y despacho

Las instrucciones de orquestación, ambos adaptadores, `handoff-prompts.md` y las referencias de preparación/reentrada pertinentes deben concordar:

- Todo encargo nuevo se prepara sobre ejecución v2, también al continuar un proyecto viejo.
- El legado se reconoce y recupera conforme a §4.1; su mera presencia no habilita preparación nueva v1.
- Para C, obtener la identificación del renderer y trasladar esa salida, sin recomponer su objeto ni adjuntar el cuerpo.
- Para A, trasladar el render completo sin alterarlo.
- A no es una excepción que permita preparar encargos nuevos v1.
- No presentar `.cdad/execution.json` como entrada universal.
- No presentar `--resume-packet` como una vía universal de replay v1.
- No modificar las reglas de transporte externo ni sustituir el transporte nativo por el CLI dentro del mismo runtime.
- Mantener registro, recepción, separación de roles y gates vigentes.
- No tratar un rechazo como habilitación para pasar a legacy.
- Ante requisitos ausentes, diagnosticar y orientar hacia el procedimiento existente sin fabricar autoridad ni cambiar la versión silenciosamente.

Los agentes derivados se regeneran desde fuentes, conforme a `Makefile:1-18`; no se parchean manualmente.

La compatibilidad histórica se comprueba con el consumidor actualizado. No se promete que una instalación anterior, cuyo esquema cerrado desconoce el campo, admita requests nuevos.

### 4.7. Evidencia y proporcionalidad

| Evidencia | Acredita | No acredita |
|---|---|---|
| Request validado y archivo igual al render | Integridad publicada | Mensaje recibido por el runtime |
| Bytes enviados a stdin externo | Entrega a esa frontera | Recepción o persistencia final |
| Literal reconstruido por el modelo | Comparación de ese literal | Exportación independiente del mensaje |
| Contraste del resultado con contrato y fuentes | Fidelidad examinada, con límites | Integridad del transporte |
| Recibo del resultado | Recepción según su contrato | Aprobación semántica o integridad del prompt |

Si no hay acceso independiente al mensaje recibido, se declara esa limitación. No se certifica igualdad mecánica de entrega mediante autoatestación.

El orquestador puede contrastar el resultado sin repetirlo automáticamente **por esa sola carencia de evidencia**, conservando revisión y aprobación aplicables. Un transporte correcto tampoco justifica aceptar un resultado infiel.

## 5. Postcondiciones observables

### Promesa A — Despachar sin retranscribir el cuerpo

**PC-01.** Para un paquete publicado válido con contexto canónico v2, `render --route C` emite únicamente la declaración e identificación de §4.2, deterministas y concordantes. No modifica archivos ni estado. Un request v2 histórico sin localizador conserva el requisito de argumento explícito de §4.1.

**PC-02.** La emisión C rechaza un contexto v1 con diagnóstico explícito de C v2-only. También rechaza un request que no designa el archivo publicado requerido, un contexto no canónico o un paquete publicado inválido/divergente. No emite una identificación utilizable ni produce efectos persistentes.

**PC-03.** El intake y despacho documentados exigen contexto v2 para C y validación íntegra del paquete nombrado antes de trabajar; admiten C sin cuerpo inline y rechazan mezcla A+C, identificación ambigua y cuerpo parcial. No permiten cambiar de paquete, ruta o scope para rescatar un rechazo.

### Promesa B — Preparar trabajo nuevo en v2 y utilizar el contexto sin adivinarlo

**PC-04.** Toda preparación nueva que publica un encargo —ordinaria, sucesora o de recuperación— utiliza contexto v2 y declara en request y cabecera su localizador canónico. Se rechazan selecciones v1 explícitas o implícitas, incluida la selección histórica sin policy, y ubicaciones v2 incompatibles antes de publicar, sin efectos persistentes. Un sucesor nuevo declara el campo aunque el predecesor no lo tuviera.

**PC-05.** `render`, `validate-request` y `validate-packet` cumplen la matriz completa de §4.1. Un request histórico sin argumento explícito se rechaza, sin fallback por identidad.

**PC-06.** Los checks compartidos rechazan localizadores fuera de dominio o discordantes con identidad/schema. Los tres CLI, C y la preparación nueva aplican además sus comprobaciones de ubicación de §4.1–4.2. Un argumento explícito de los tres CLI que discrepa del localizador se rechaza con diagnóstico de contexto y sin efectos persistentes; no se prueba otra ubicación. No se introduce esa comparación de ruta en las interfaces de otros consumidores.

**PC-07.** Con raíz explícita y argumentos de archivo válidos desde el directorio de invocación, los requests con localizador resuelven el mismo contexto desde otro directorio. Los requests históricos sin campo conservan su uso explícito v1/v2 y las condiciones de validación existentes; la ausencia del campo no añade metadatos al render ni provoca reescritura o migración.

**PC-07b.** El procedimiento para retomar un proyecto v1 distingue recuperación histórica de encargo nuevo, remite al bootstrap v2 existente y explicita policy, autoridad y aprobación/pin según el rol. Si faltan, identifica causa, responsable y continuación conforme a §4.1, sin preparar v1 ni fabricar autoridad. Ante un paquete v1 activo no terminal, incluido `prepared`, compromete un único resultado observable: diagnosticar el bloqueo y la ausencia de ruta CLI terminal existente y escalar al owner, dejando state intacto y sin preparar v1; no promete un procedimiento inexistente ni incorpora migración o withdraw v1. Distingue el replay byte-identical de `--resume-packet`, sujeto a sus condiciones v2 actuales, de las vías explícitas históricas v1 y de una nueva publicación. Su revisión no se presenta como garantía de que todo estado viejo sea automáticamente ejecutable.

### Promesa C — Comparar el paquete completo y explicar el rechazo

**PC-08a — Regresión mecánica existente.** Los verificadores mantienen aceptación del paquete canónico completo y rechazo de divergencia del cuerpo con cabecera intacta, sin normalizar bytes. Se conserva la diferencia de preámbulo de §4.4.

**PC-08b — Instrucción revisable.** El intake común y sus salidas generadas afirman que el cierre JSON no termina el paquete y que la comparación abarca también instrucciones y cuerpo. Su revisión no acredita conducta real de un modelo.

**PC-09.** Los diagnósticos afectados distinguen las causas de §4.5, ofrecen siguiente acción y referencia esperada segura cuando se conoce, sin divulgar el cuerpo ni cambiar semánticas de salida.

### Promesa D — No confundir observabilidad con validez

**PC-10.** El procedimiento de reporte/re-entry distingue integridad publicada, observabilidad de entrega y fidelidad del resultado. No presenta archivo, stdin, literal reconstruido ni recibo como prueba independiente del prompt recibido.

**PC-11.** El procedimiento conserva I-4 e I-5: no exige repetición automática únicamente por falta de observabilidad; sí mantiene rechazo ante divergencia comprobada o autoridad inválida y hallazgo ante resultado infiel. No rescata mediante C un dispatch inline alterado. Su recuperación mediante un nuevo encargo cumple la regla v2 y los gates vigentes.

### Promesa E — Entregar la mejora distribuible

**PC-12.** Fuentes, agentes regenerados, ambos adaptadores, handoff y referencias de preparación/reentrada describen consistentemente las interfaces y fronteras anteriores. Un consumidor instalado aislado puede preparar un paquete nuevo v2, emitir C y resolver/validar su contexto, sin modificar la instalación global.

## 6. Invariantes verificables

- **INV-01:** un paquete corresponde a un rol y una subfase; no acumula permisos.
- **INV-02:** identidad, estado, contrato, aprobación, política y binding siguen validándose.
- **INV-03:** el localizador no crea una fuente de autoridad alternativa al contexto canónico.
- **INV-04:** ninguna ruta permite elegir otro paquete tras fallar la admisión.
- **INV-05:** igualdad completa no se sustituye por igualdad de cabecera o semejanza semántica.
- **INV-06:** las lecturas de control-plane no amplían acceso al producto.
- **INV-07:** no se añaden protocolos de entrega, registros, recibos o conectores paralelos.
- **INV-08:** no hay conversión, reescritura ni adopción silenciosa de contextos históricos; su reconocimiento o replay no habilita preparación nueva v1.
- **INV-09:** recepción o evidencia de transporte no implican aprobación semántica.
- **INV-10:** los derivados se regeneran desde fuentes.
- **INV-11:** los rechazos nuevos ocurren antes de publicación o efectos persistentes.
- **INV-12:** toda nueva publicación de un encargo utiliza ejecución v2 y declara su localizador; C solo representa paquetes con contexto canónico v2.

## 7. Aceptación proporcional

La aceptación requiere evidencia trazada a las postcondiciones:

**Sustitución contractual trazable (N-3).** Para preparación nueva, esta spec sustituye explícitamente la garantía de `docs/specs/004-002-project-execution-bootstrap/spec.md:115` (PD-12: el proyecto legacy «conserva su intake») en cuanto permitía preparar implícitamente un encargo v1 sin policy. La autoridad del cambio es `owner-decision-v2-new-assignments.md:3-13`: todo encargo nuevo utiliza v2. Se conserva el reconocimiento, validación y reentrada históricos de §4.1; la spec histórica permanece intacta.

Expectativas verificadas por lectura que deben actualizarse para PC-04:

- `tests/test_004_002_t6_landing.py::test_pd12_legacy_without_policy_keeps_legacy_intake` (`:606-642`): espera publicación implícita v1 sin policy.
- `tests/test_packet_prepare.py::test_p2_default_execution_context_and_out_dir_under_project_cdad` (`:402-424`): espera preparación exitosa usando por defecto `.cdad/execution.json`.

En su etapa, el test-writer audita la lista completa de tests afectados y actualiza las expectativas con trazabilidad por test al requisito anterior, a esta sustitución y a la decisión owner, conservando las garantías aún vigentes. Los dos tests nombrados no constituyen una lista exhaustiva ni evidencia de ejecución. El implementer no edita tests; no se difiere esta actualización al cierre ni se altera la spec histórica.

1. **Pruebas previas a GREEN del comportamiento nuevo:** emisión C v2-only y su rechazo explícito de v1; binding publicado; campo/localizador; matriz de los tres CLI; incompatibilidades; diagnósticos; preparación nueva exclusivamente v2. Debe comprobarse el cierre de la vía implícita v1 sin policy y la incorporación del campo en las nuevas generaciones afectadas. Deben existir controles válidos; un rechazo universal no satisface el contrato.
2. **Compatibilidad histórica:** verificar requests sin campo con argumento explícito, rechazo de su ausencia y condiciones v1/v2 pertinentes. La ausencia del campo no añade metadatos ni reescribe archivos. El replay se verifica solo en las vías que realmente lo admiten; no se exige ni se atribuye soporte v1 a `--resume-packet`.
3. **Frontera de consumidores:** comprobar los checks compartidos de dominio/identidad/schema y las comparaciones de ubicación en las superficies comprometidas. No ampliar opciones ni resolución de `cdad_result`.
4. **Regresión mecánica:** reutilizar la cobertura de paquete completo, cuerpo alterado y diferencias de bytes —incluido CRLF ya cubierto—. PC-08a puede estar verde antes del cambio; no se fabrica un RED para una capacidad existente.
5. **Revisión independiente de instrucciones:** examinar intake, mezcla de rutas, orquestación, adaptadores, handoff, preparación/reentrada y tratamiento I-4/I-5. Para PC-07b comprobar la referencia al procedimiento existente, los requisitos por rol y la continuación ante carencias; no exigir una migración automática ni un protocolo nuevo. Pruebas de texto no acreditan obediencia de un modelo ni recepción nativa.
6. **Consumidor instalado aislado:** comprobar el recorrido de PC-12 y la preservación de restricciones, sin actualizar la instalación global.
7. **Cierre:** cumplir la política de suite declarada en el paquete y los gates de revisión y aprobación correspondientes.

No se exige benchmark, cuota de escenarios, porcentaje de cobertura, variantes equivalentes adicionales ni exportación real del prompt no comprometida.

## 8. Decisiones de diseño

| Propuesta | Alternativa | Criterio |
|---|---|---|
| C emitida por el renderer común | Conector específico o nuevo protocolo | Reutiliza la ruta existente y evita retranscribir el cuerpo sin inventar capacidades del runtime. |
| Resolución compartida con localizador restringido | Corregir ejemplos o admitir rutas arbitrarias | Resuelve la familia de consumidores afectados sin añadir otra fuente de autoridad. |
| Requests anteriores mantienen argumento obligatorio | Nuevo fallback por identidad en los tres comandos | Conserva el comportamiento real y evita ampliar compatibilidad implícitamente. |
| Identificación C exclusiva, sin marcador A | Mezclar ambas formas o añadir marcadores de otro protocolo | Reutiliza el bloque de identificación existente y elimina precedencia ambigua. |
| C ligada al propio request publicado | Aceptar copias equivalentes | Impide que una copia seleccione o represente otro encargo publicado. |
| Conservar las fronteras actuales de preámbulo | Unificar todos los comparadores | La unificación no es necesaria para la promesa de esta unidad. |
| Diagnóstico por causa | Mostrar diffs del encargo | Acción útil sin divulgar contenido. |
| Separar evidencia de fidelidad | Repetir por ausencia de prueba de entrega | Conserva I-4 sin debilitar I-5 ni los gates. |
| Regla general: toda nueva publicación usa v2; C también es v2-only | Restringir solo C y conservar preparación v1 por A o por ausencia de policy | Aplica la decisión del owner a toda la familia de preparaciones y cierra la vía implícita real. |
| Checks compartidos de dominio/identidad/schema y comparación de ruta en las superficies que conocen esa ruta | Atribuir comparación de archivos a `validate_request` o ampliar todas las CLI | Conserva las interfaces y separa validación del documento de resolución del archivo. |
| Reutilizar bootstrap y autoridad vigentes para nuevo trabajo sobre legado | Convertir v1 automáticamente o tratar la decisión general como aprobación del proyecto | Preserva autoridad, pins y archivos históricos sin crear otro protocolo. |
| Replay condicionado por las capacidades históricas reales | Prometer `--resume-packet` para cualquier v1 | Evita inventar soporte; ofrece vías explícitas y diagnóstico sin bloquear silenciosamente la reentrada. |

Base técnica verificada: `cdad_packet.py:295-310,1182-1233,1582-1788,1795-1993,2893-2955,9485-9491,9797-9803,9900-9922`; `sources/roles/architect.md:15-57`; `sources/roles/orchestrator.md:45-99`; adaptadores OpenCode `:66-100` y Claude Code `:80-114`; `handoff-prompts.md:5-47`. Frontera de preparación y reentrada contrastada además con `cdad_packet.py:2060-2072,2560-2805,2893-2955,2958-3087,3374-3599,5933-5956,6172-6230,6433-6470`; `project-execution.md:39-45,52-129`; `project-start.md:160-182`; decisión owner `:3-15`.

## 9. Trazabilidad del plan-review

| Hallazgo | Tratamiento en este borrador |
|---|---|
| **B-1** | Se conserva cerrado: matriz única para los tres CLI; histórico sin argumento rechazado, sin fallback; condiciones de validación conservadas. PC-05 y PC-07. |
| **B-2** | Se conserva el cierre: dominio seguro, vínculo identidad/schema y rechazo sin efectos. La decisión posterior restringe el campo nuevo a v2; el v1 histórico permanece sin campo por contexto explícito. PC-04 y PC-06–07. |
| **O-1** | Declaración literal, bloque JSON distinto del marcador A y rechazo de mezcla incluso coincidente. PC-03. |
| **O-2** | C exige el propio request publicado; las copias no bastan. PC-02. |
| **O-3** | Independencia de cwd condicionada a raíz y argumentos adecuados. PC-07. |
| **O-4** | Regresión mecánica existente PC-08a separada de instrucción revisable PC-08b; no se exige RED artificial. |
| **O-5** | Consumidores delimitados; `cdad_result` sin ampliación CLI; handoff explícito; diferencia de preámbulo conservada. |
| **N-1** | Corregido conforme a la decisión del owner: C v2-only usa el verificador existente sin ampliarlo. Toda preparación nueva es v2, incluida la vía implícita que antes permitía v1 sin policy. PC-01–04. |
| **O-A** | Checks compartidos de dominio/identidad/schema separados de igualdad de ruta en los tres CLI y C; la preparación comprueba su propia publicación. No se amplían las interfaces de otros consumidores. §4.1 y PC-06. |
| **O-B** | Evidencia del encargo anterior etiquetada como histórica y no normativa, conservando sus hechos originales. |
| **N-2** | §4.1, §4.5 y PC-07b explicitan la laguna para v1 activo no terminal, incluido `prepared`: diagnóstico y escalación al owner, sin modificar state ni preparar v1 y sin prometer una ruta CLI terminal inexistente. |
| **N-3** | §7 declara la sustitución de 004-002 PD-12:115 por la decisión owner, identifica los dos tests verificados y asigna al test-writer la auditoría y actualización trazable; implementer no edita tests y la spec histórica queda intacta. |
| **O-C** | §8 conserva una sola tabla Markdown, sin línea vacía entre sus filas. |

N-1 queda atendido en esta propuesta, no aprobado por el architect. La pregunta histórica de `orchestration-review-v2-decision-pending.md` se conserva y se referencia como resuelta por `owner-decision-v2-new-assignments.md`; no se borra ni reescribe su registro.

I-4, I-5, el incidente y las revisiones anteriores se conservan. La tensión de §2.1 sigue pendiente de decisión explícita de Pablo. Este borrador no autoriza implementación.

## 10. deferred-hardening

- **Exportación independiente del mensaje recibido por cada runtime:** capacidad pendiente de verificar. No se promete ni sustituye por autoatestación.
- **Conexión mecánica renderer→herramienta nativa:** requiere una superficie demostrada; C evita retranscribir el cuerpo, pero no prueba recepción.
- **Atomicidad entre validación y lectura/transmisión posterior:** el recorrido existente contiene operaciones separadas. No se promete eliminar esa ventana.
- **Unificación del tratamiento de preámbulos:** se conserva expresamente la diferencia de §4.4; no es necesaria para emitir C.
- **Endurecimiento exhaustivo de diagnósticos ajenos al cambio:** fuera de alcance; los nuevos diagnósticos sí deben satisfacer §4.5.
- **Nuevas restricciones generales sobre enlaces internos o rutas explícitas históricas:** se conservan controles existentes; no se amplía este trabajo a una política general del filesystem.
- **Interoperabilidad entre versiones instaladas distintas:** una instalación antigua puede desconocer el campo nuevo. PC-12 compromete el consumidor actualizado aislado, no un protocolo de negociación de versiones.
- **Rendimiento y variantes equivalentes adicionales:** no existe una promesa de rendimiento ni necesidad evidenciada que las justifique.

Ninguna exclusión aplaza una promesa comprometida.

## 11. Decisión pendiente de Pablo

Quedan pendientes la aprobación estratégica de §2.1 y la aprobación explícita de esta spec corregida, tras la revisión correspondiente.

No se solicita elegir detalles técnicos todavía en borrador. Este texto no autoriza implementación ni altera el plan aprobado.

---

## Anexo no normativo — evidencia histórica del encargo architect draft-002

El contenido siguiente conserva el informe original de ese encargo. Sus comandos, mediciones, hashes y referencias a HEAD describen aquella ejecución, no capacidades del producto ni evidencia de esta revisión v3. No forma parte de las promesas, postcondiciones o criterios de aceptación.

- **Ruta C:** identificación contrastada con el request validado; digest del contrato verificado y `PACKET.md` completo comparado contra stdout canónico.
- **Salida de comparación:**

```text
Route C metadata, contract SHA256 and COMPLETE PACKET.md canonical comparison: PASS (6577 bytes)
```

- **Validaciones CLI ejecutadas**, con `R=<repo>`, `E=.cdad/executions/exec-010-004-packet-dispatch-ergonomics-001/execution.json` y `P=.cdad/packets/010-004-packet-dispatch-ergonomics-architect-draft-002`:

```bash
python3 scripts/cdad_packet.py validate-request --project-root "$R" --execution-context "$E" --request "$P/REQUEST.json"
python3 scripts/cdad_packet.py render --project-root "$R" --execution-context "$E" --request "$P/REQUEST.json"
python3 scripts/cdad_packet.py validate-packet --project-root "$R" --execution-context "$E" --request "$P/REQUEST.json" --packet "$P/PACKET.md"
```

Los argumentos se suministraron expandidos; los comandos exactos y el comparador Python en memoria constan en las llamadas de herramientas. Las validaciones finalizaron satisfactoriamente, sin salida; el render se comparó íntegramente, sin normalización.

- **Medición:** Python `3.13.5`; comparación de bytes en memoria, sin temporales.
- **Archivos modificados:** ninguno.
- **Commit creado:** ninguno.
- **HEAD inicial y final:** `fd3afba7cf549f98ce449df0f46a5811bd1cd7c5`.
- `git diff --exit-code` y `git diff --cached --exit-code`: satisfactorios, sin salida.
- `git status --short`, inicial y final:

```text
?? docs/specs/010-000-continuity-relative-root/discovery.md
```

El archivo preexistente no se modificó. No se ejecutaron tests, suite, generación, instalación, implementación ni push.

La comparación acredita el paquete publicado, no una exportación independiente del mensaje recibido por el runtime.

**Borrador pendiente de aprobación.**

## Registro de aprobación (metadatos posteriores al borrador)

Pablo aprobó explícitamente el borrador exacto SHA-256 `054d4657b5dae096114a9e41beaad3c356234fe8fd5c60236752c24c89212008` con «aprobado, adelante», tras abrir esta especificación. Registro: 2026-10-30. Incluye §2.1 (C emitida por renderer preferente para nuevos despachos nativos, sin prometer conexión mecánica), encargos nuevos v2 y reentrada histórica sin migración automática. Los textos de aprobación pendiente anteriores se conservan como historia del borrador y quedan superados únicamente por este registro. No se modifica contenido funcional.

N-4, N-5 y N-6 siguen OPTIONAL abiertos/postergados conforme a `plan-review.md`; no se declaran resueltos ni se introduce precedencia o interpretación legacy nueva. Si el AUDIT evidencia afectación funcional de N-4/N-5 se consulta al owner, sin elegir silenciosamente un contrato incompatible. La aprobación no sustituye los demás gates.

Status: Approved by Pablo on 2026-10-30
