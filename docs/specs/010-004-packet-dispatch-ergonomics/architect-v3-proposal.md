## Resultado

Ruta C validada: identificación concordante, contrato verificado y `PACKET.md` completo idéntico al render canónico.

Devuelvo **patch textual del borrador, no aprobación**. No modifiqué archivos.

## Patch listo para materializar

**Archivo:** `docs/specs/010-004-packet-dispatch-ergonomics/spec.md`  
**Base exacta SHA-256:** `8d2b948e2fd596ce1298c036423e5c8b91d905396bba26e8dc6a8df6571a4517`

Aplicar las sustituciones siguientes sobre esa base. Los bloques no indicados permanecen intactos. No modificar las revisiones, decisiones ni registros históricos.

### 1. Estado

Sustituir la línea de estado por:

> **Estado:** borrador v3, revisado conforme a `owner-decision-v2-new-assignments.md`; pendiente de revisión y aprobación explícita de Pablo.

### 2. Añadir §2.4, inmediatamente antes de §3

```markdown
### 2.4. Decisión del owner: encargos nuevos v2

`owner-decision-v2-new-assignments.md:3-15` resuelve N-1: la nueva emisión C es v2-only y **toda preparación o encargo nuevo utiliza ejecución v2**, también al continuar un proyecto viejo. No basta con restringir C.

v1 se conserva para reconocer, validar y retomar lo histórico bajo las condiciones existentes. No se reescriben sus archivos, se elimina su soporte ni se convierte su replay en permiso para preparar nuevos encargos v1.

Esta decisión no aprueba la spec completa, no resuelve §2.1 y no aporta por sí sola autoridad, aprobación ni pin para cada proyecto viejo. La frontera operativa se especifica en §4.1.
```

### 3. Sustituir §3 completo

```markdown
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
```

### 4. Sustituir §4.1 completo

```markdown
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
5. Resolver previamente los bloqueos de paquete activo y los gates aplicables por los mecanismos existentes. `--new-execution` no los elude.

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
| Estado/binding, unidad o paquete activo incompatibles | Diagnóstico de incoherencia con el registro implicado; resolverlo por el procedimiento existente aplicable antes de preparar. No borrar bindings ni decisiones para desbloquear. |
| Architect standalone sin mandato de épica | Conservar el diagnóstico legacy existente de `_contract_for` (`:2060-2072`); orientar reconocimiento y aclaración del mandato. No fabricar un contrato de épica ni emitir un nuevo paquete v1. |
| Replay no admitido por su vía actual | Identificar el límite y las vías históricas explícitas aplicables; si se requiere otro encargo, aplicar los requisitos de preparación v2. |

No existe aquí una garantía de conversión de cualquier estado viejo en estado v2 ejecutable. Cuando la evidencia o el mecanismo existente no basten, se declara la laguna y se escala la decisión al responsable; no se inventa autoridad, una migración automática ni una aceptación retrospectiva.

El bootstrap puede publicar el nuevo contexto y actualizar el binding conforme al procedimiento autorizado. No convierte ni destruye los archivos v1 y no reescribe paquetes históricos.
```

### 5. Sustituir §4.2 completo

```markdown
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
```

### 6. Precisiones de intake, comparación y diagnósticos

En §4.3, bajo `#### Ruta C`, añadir como primer punto:

> - Requiere contexto v2 canónico conforme a §4.2. Un contexto v1 recibe diagnóstico explícito; no se cambia silenciosamente a A ni se prepara otro encargo.

En la tabla de §4.4, sustituir exclusivamente la fila de verificación publicada por:

```markdown
| Verificación publicada utilizada para C | Contexto canónico v2 cargado por identidad mediante `verify_published_packet`; comparación desde el único marcador A del archivo publicado hasta su final. No admite contexto v1. |
```

En §4.5, añadir después del párrafo que empieza «Cada diagnóstico ofrece»:

```markdown
C con contexto v1 informa que C requiere v2; distingue el uso histórico del paquete de la preparación de otro encargo. No recomienda convertir el archivo ni sugiere que cambiar de ruta rescate una entrega divergente.

La preparación nueva sobre legado informa los requisitos faltantes de §4.1: policy, autoridad/aprobación/pin o coherencia de estado. La continuación identifica al responsable y el procedimiento existente pertinente. Un diagnóstico legacy no autoriza preparación v1 ni acredita una consulta como dispatch CDAD.
```

### 7. Sustituir §4.6 completo

```markdown
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
```

### 8. Sustituir §5 completo

```markdown
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

**PC-07b.** El procedimiento para retomar un proyecto v1 distingue recuperación histórica de encargo nuevo, remite al bootstrap v2 existente y explicita policy, autoridad y aprobación/pin según el rol. Si faltan, identifica causa, responsable y continuación conforme a §4.1, sin preparar v1 ni fabricar autoridad. Distingue el replay byte-identical de `--resume-packet`, sujeto a sus condiciones v2 actuales, de las vías explícitas históricas v1 y de una nueva publicación. Su revisión no se presenta como garantía de que todo estado viejo sea automáticamente ejecutable.

### Promesa C — Comparar el paquete completo y explicar el rechazo

**PC-08a — Regresión mecánica existente.** Los verificadores mantienen aceptación del paquete canónico completo y rechazo de divergencia del cuerpo con cabecera intacta, sin normalizar bytes. Se conserva la diferencia de preámbulo de §4.4.

**PC-08b — Instrucción revisable.** El intake común y sus salidas generadas afirman que el cierre JSON no termina el paquete y que la comparación abarca también instrucciones y cuerpo. Su revisión no acredita conducta real de un modelo.

**PC-09.** Los diagnósticos afectados distinguen las causas de §4.5, ofrecen siguiente acción y referencia esperada segura cuando se conoce, sin divulgar el cuerpo ni cambiar semánticas de salida.

### Promesa D — No confundir observabilidad con validez

**PC-10.** El procedimiento de reporte/re-entry distingue integridad publicada, observabilidad de entrega y fidelidad del resultado. No presenta archivo, stdin, literal reconstruido ni recibo como prueba independiente del prompt recibido.

**PC-11.** El procedimiento conserva I-4 e I-5: no exige repetición automática únicamente por falta de observabilidad; sí mantiene rechazo ante divergencia comprobada o autoridad inválida y hallazgo ante resultado infiel. No rescata mediante C un dispatch inline alterado. Su recuperación mediante un nuevo encargo cumple la regla v2 y los gates vigentes.

### Promesa E — Entregar la mejora distribuible

**PC-12.** Fuentes, agentes regenerados, ambos adaptadores, handoff y referencias de preparación/reentrada describen consistentemente las interfaces y fronteras anteriores. Un consumidor instalado aislado puede preparar un paquete nuevo v2, emitir C y resolver/validar su contexto, sin modificar la instalación global.
```

### 9. Invariantes

Sustituir INV-08 por:

> - **INV-08:** no hay conversión, reescritura ni adopción silenciosa de contextos históricos; su reconocimiento o replay no habilita preparación nueva v1.

Añadir después de INV-11:

> - **INV-12:** toda nueva publicación de un encargo utiliza ejecución v2 y declara su localizador; C solo representa paquetes con contexto canónico v2.

### 10. Sustituir §7 completo

```markdown
## 7. Aceptación proporcional

La aceptación requiere evidencia trazada a las postcondiciones:

1. **Pruebas previas a GREEN del comportamiento nuevo:** emisión C v2-only y su rechazo explícito de v1; binding publicado; campo/localizador; matriz de los tres CLI; incompatibilidades; diagnósticos; preparación nueva exclusivamente v2. Debe comprobarse el cierre de la vía implícita v1 sin policy y la incorporación del campo en las nuevas generaciones afectadas. Deben existir controles válidos; un rechazo universal no satisface el contrato.
2. **Compatibilidad histórica:** verificar requests sin campo con argumento explícito, rechazo de su ausencia y condiciones v1/v2 pertinentes. La ausencia del campo no añade metadatos ni reescribe archivos. El replay se verifica solo en las vías que realmente lo admiten; no se exige ni se atribuye soporte v1 a `--resume-packet`.
3. **Frontera de consumidores:** comprobar los checks compartidos de dominio/identidad/schema y las comparaciones de ubicación en las superficies comprometidas. No ampliar opciones ni resolución de `cdad_result`.
4. **Regresión mecánica:** reutilizar la cobertura de paquete completo, cuerpo alterado y diferencias de bytes —incluido CRLF ya cubierto—. PC-08a puede estar verde antes del cambio; no se fabrica un RED para una capacidad existente.
5. **Revisión independiente de instrucciones:** examinar intake, mezcla de rutas, orquestación, adaptadores, handoff, preparación/reentrada y tratamiento I-4/I-5. Para PC-07b comprobar la referencia al procedimiento existente, los requisitos por rol y la continuación ante carencias; no exigir una migración automática ni un protocolo nuevo. Pruebas de texto no acreditan obediencia de un modelo ni recepción nativa.
6. **Consumidor instalado aislado:** comprobar el recorrido de PC-12 y la preservación de restricciones, sin actualizar la instalación global.
7. **Cierre:** cumplir la política de suite declarada en el paquete y los gates de revisión y aprobación correspondientes.

No se exige benchmark, cuota de escenarios, porcentaje de cobertura, variantes equivalentes adicionales ni exportación real del prompt no comprometida.
```

### 11. Decisiones de diseño

En la tabla de §8, añadir estas filas:

```markdown
| Regla general: toda nueva publicación usa v2; C también es v2-only | Restringir solo C y conservar preparación v1 por A o por ausencia de policy | Aplica la decisión del owner a toda la familia de preparaciones y cierra la vía implícita real. |
| Checks compartidos de dominio/identidad/schema y comparación de ruta en las superficies que conocen esa ruta | Atribuir comparación de archivos a `validate_request` o ampliar todas las CLI | Conserva las interfaces y separa validación del documento de resolución del archivo. |
| Reutilizar bootstrap y autoridad vigentes para nuevo trabajo sobre legado | Convertir v1 automáticamente o tratar la decisión general como aprobación del proyecto | Preserva autoridad, pins y archivos históricos sin crear otro protocolo. |
| Replay condicionado por las capacidades históricas reales | Prometer `--resume-packet` para cualquier v1 | Evita inventar soporte; ofrece vías explícitas y diagnóstico sin bloquear silenciosamente la reentrada. |
```

Añadir al párrafo de base técnica:

> Frontera de preparación y reentrada contrastada además con `cdad_packet.py:2060-2072,2560-2805,2893-2955,2958-3087,3374-3599,5933-5956,6172-6230,6433-6470`; `project-execution.md:39-45,52-129`; `project-start.md:160-182`; decisión owner `:3-15`.

### 12. Sustituir §9 completo

```markdown
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

N-1 queda atendido en esta propuesta, no aprobado por el architect. La pregunta histórica de `orchestration-review-v2-decision-pending.md` se conserva y se referencia como resuelta por `owner-decision-v2-new-assignments.md`; no se borra ni reescribe su registro.

I-4, I-5, el incidente y las revisiones anteriores se conservan. La tensión de §2.1 sigue pendiente de decisión explícita de Pablo. Este borrador no autoriza implementación.
```

### 13. Etiquetar la evidencia histórica sin alterar sus hechos

Sustituir únicamente el encabezado `## Evidencia de este encargo` por:

```markdown
## Anexo no normativo — evidencia histórica del encargo architect draft-002

El contenido siguiente conserva el informe original de ese encargo. Sus comandos, mediciones, hashes y referencias a HEAD describen aquella ejecución, no capacidades del producto ni evidencia de esta revisión v3. No forma parte de las promesas, postcondiciones o criterios de aceptación.
```

Conservar íntegro todo el contenido posterior del anexo. §10 y §11 permanecen intactos.

## Evidencia de frontera y delta

- **Vía v1 real, no supuesta:** `_select_execution` retorna v1 sin policy en `skills/cdad-cycle/scripts/cdad_packet.py:2928-2942`; `prepare` consume la selección en `:6202` y publica binding según versión en `:6433-6441`. Restringir solamente C dejaba abierta esa preparación.
- **Replay no equivale a preparar:** `_resume_packet` rechaza opciones ordinarias y devuelve los bytes comprobados, pero carga mediante `_load_execution_context`, v2 por identidad (`:2958-3087`). No corresponde prometer ese submodo para v1.
- **C sin ampliar consumidores:** `verify_published_packet` ya carga por identidad v2 y compara el cuerpo completo (`:1935-1993`). La propuesta restringe C a esa capacidad.
- **Autoridad existente:** `project-execution.md:52-119` y `_contract_approval_for` (`:2560-2633`) distinguen mandato de arquitectura, aprobación con pin y revisión de borradores. La decisión general no sustituye ninguno.

## Evidencia de esta invocación — no normativa

Comandos de validación ejecutados con los argumentos expandidos que constan en las llamadas:

```text
/usr/bin/python3 scripts/cdad_packet.py validate-request --project-root <repo> --execution-context .cdad/executions/exec-010-004-packet-dispatch-ergonomics-001/execution.json --request .cdad/packets/010-004-packet-dispatch-ergonomics-architect-draft-003/REQUEST.json

/usr/bin/python3 scripts/cdad_packet.py render --project-root <repo> --execution-context .cdad/executions/exec-010-004-packet-dispatch-ergonomics-001/execution.json --request .cdad/packets/010-004-packet-dispatch-ergonomics-architect-draft-003/REQUEST.json

/usr/bin/python3 scripts/cdad_packet.py validate-packet --project-root <repo> --execution-context .cdad/executions/exec-010-004-packet-dispatch-ergonomics-001/execution.json --request .cdad/packets/010-004-packet-dispatch-ergonomics-architect-draft-003/REQUEST.json --packet .cdad/packets/010-004-packet-dispatch-ergonomics-architect-draft-003/PACKET.md
```

Resultados:

```text
validate-request: rc=0; stdout/stderr vacíos
render: rc=0; stdout completo idéntico a PACKET.md; 6271 bytes
validate-packet: rc=0; stdout/stderr vacíos
identification context/root + canonical metadata: MATCH
```

Comparación en memoria mediante Python `3.13.5`, sin temporales ni normalización:

```text
PACKET.md SHA-256:
c78b2512a67846e8dc4e5e273fddadfb2904e3b5a7c82c7eda3d89bd6d6d2c7f

UNIT-CONTRACT.md SHA-256:
af0708d59354efdd06f8771e1deebc52dac5d8bd7c2dd7f532fb25091a60578b
```

Auditoría final:

```text
git rev-parse HEAD
f50875ad199f450a1f71cee47e94c68dba2ea00f

git diff --exit-code
git diff --cached --exit-code
Ambos satisfactorios, sin salida.

git status --short
?? docs/specs/010-000-continuity-relative-root/discovery.md
```

El archivo no trackeado ya estaba presente al inicio y no se modificó. **Archivos modificados: ninguno. Commit: ninguno.** Sin tests, implementación, generación, instalación, push ni spawns.

La comparación acredita el paquete publicado; no constituye una exportación independiente del mensaje recibido por el runtime. **Spec pendiente de revisión y aprobación.**