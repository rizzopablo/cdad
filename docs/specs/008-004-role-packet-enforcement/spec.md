# 008-004 — Exigencia de paquete en los despachos de rol

Status: Aprobada por el orquestador (HITL delegada del dueño) el 2026-10-27, con D1/D2/D3 fijadas.
Epic: epic-008-suite-coherence
Dependencia: 008-003

## Autoridad y objetivo

Autoridad: plan aprobado del epic y su UNIT-CONTRACT.
Base técnica: discovery.md de esta feature.

Cerrar la admisión y acreditación de encomiendas CDAD inválidas mediante
validación del paquete completo, sin cambiar el harness ni crear otro
registro de ejecución.

Decisiones HITL recibidas:
- D1: opción A como ruta principal; C como respaldo explícito; B fuera.
- D2: el marcador canónico identifica la encomienda CDAD, no las palabras
  del objetivo ni el nombre del rol.
- D3: rechazar un nuevo begin cuya referencia contract esté cubierta por
  el write_scope del paquete, reutilizando _scope_contains.

## Alcance y límites

Dentro:
- Intake compartido de los roles y sus agentes generados/instalados.
- Preflight del orquestador y fronteras existentes de despacho,
  delegación, registro y recepción.
- Comprobación temprana de referencias al publicar un nuevo begin.
- Documentación y adaptadores que actualmente exigen paquete sin prefijos.

Fuera:
- Cambiar el harness o exigirle que suprima su preámbulo.
- Interceptar herramientas nativas, imponer un sandbox o impedir
  físicamente lecturas/escrituras fuera de scope.
- Selección de modelos, registros adicionales, nuevos recibos o rc nuevos.
- Prohibir consultas legacy legítimas.

La ausencia de marcador no constituye una encomienda CDAD para el intake
del rol. No demuestra que un orquestador no haya omitido indebidamente
el paquete al delegar: el preflight sigue siendo obligatorio para una
operación CDAD iniciada por el orquestador.

La validación de PACKET.md en disco no acredita por sí sola los bytes
que recibió una sesión nativa. La garantía del intake depende de que el
rol aplique sus instrucciones; no existe interceptación del transporte
nativo por esta feature.

## Contrato de admisión

### Identificación

Se identifica el marcador por la línea exacta ---cdad-packet-json,
independientemente de su posición después de un preámbulo.

- Cero marcadores: consulta legacy; no se acredita como despacho CDAD.
- Uno: debe delimitar un bloque canónico válido, terminado por
  ---end-cdad-packet-json, y superar la validación de la ruta elegida.
- Más de uno, bloque incompleto, metadatos inválidos o identidad
  discordante: rechazo; nunca fallback automático a legacy.

El preámbulo no modifica objetivo, contrato, instrucciones ni scopes.
No se eligen paquetes mediante heurísticas sobre texto libre.

### A — Paquete inline, ruta principal

Resolver el REQUEST.json y el contexto de ejecución del paquete
identificado; validar el request con las reglas existentes.

Comparar el paquete completo recibido, desde el marcador hasta el final
del render canónico, con render_packet del request validado. El preámbulo
anterior al marcador no participa de esa comparación ni autoriza trabajo.

La igualdad abarca objetivo, instrucciones, contrato, entradas, scopes,
invariantes y evidencia; validar únicamente el JSON del encabezado no basta.
No normalizar ni reconstruir texto alterado para hacerlo coincidir.

REQUEST.json no declara actualmente un digest del paquete completo.
La prueba es request validado → render canónico → igualdad de bytes,
no un supuesto campo de digest inexistente.

### C — Respaldo explícito por archivos

El despacho declara explícitamente esta ruta e identifica un único paquete
publicado. Conserva un único bloque canónico de identificación en el prompt;
la falta del cuerpo inline es admisible sólo en esta ruta explícita.

Antes de trabajar, el rol lee REQUEST.json y PACKET.md del paquete señalado,
valida el request y compara todo PACKET.md con el render canónico.
Los metadatos recibidos deben coincidir con los del paquete validado.
No buscar otro paquete si falla el identificado.

La lectura mínima de control-plane necesaria para esta validación se
declara en el contrato/instrucciones correspondientes. No amplía el scope
de producto del test-writer ni autoriza leer implementación.

Un paquete inline alterado no se rescata silenciosamente mediante C.

### Orden y efectos

La admisión debe preceder a los nuevos efectos de la encomienda:
nuevo begin, lanzamiento por las fronteras administradas, observación,
staging, recepción y cambios de estado correspondientes.

El orquestador realiza el preflight antes de begin y del transporte nativo.
Las entradas CLI directamente invocables verifican sus propias
precondiciones antes de sus efectos; no confían sólo en el preflight.

No se acredita una entrega nueva cuyo paquete no supere la validación.
No se añaden registros o recibos para duplicar los existentes.

Los replays durables conservan su precedencia actual: reconocer una
repetición ya acreditada no equivale a autorizar un despacho nuevo.

### Errores

Diagnóstico accionable que identifique la causa y el paquete o referencia,
cuando estén disponibles.

Se conserva cli-delegation.md:
- Error de invocación sin envoltura: rc no cero existente.
- Si se produce envoltura válida de bloqueo: termination=blocked,
  delivery=none y delivery_ref=null; rc=0 significa envoltura producida.

No se define un nuevo código de salida.

## Referencias y nuevo begin

Para un nuevo begin asociado a un paquete, resolver las referencias con
las clases actuales y verificar cada referencia contract contra todos los
selectores de write_scope mediante _scope_contains, usando el contrato,
política y raíz correspondientes al paquete validado.

Si queda cubierta, rechazar antes de persistir: diagnosticar la referencia
y el selector incompatibles. No reclasificar automáticamente.

Una referencia living explícita conserva su semántica: su divergencia no
se convierte por sí sola en P1. Las restantes validaciones siguen vigentes.

La regla se aplica a nuevos begin; no invalida retroactivamente registros
durables ni adelanta el rechazo por delante del reconocimiento de replay.

## Postcondiciones verificables

### PC-01 — Admisión antes de efectos nuevos

Un despacho CDAD iniciado por el orquestador o solicitado mediante las
fronteras CLI sin paquete verificable se rechaza con diagnóstico antes
de publicar nuevo begin, observación, entrega o cambio de estado.
El intake con un bloque canónico inválido tampoco autoriza trabajo.
Un prompt sin marcador conserva la ruta legacy y no acredita despacho CDAD.

### PC-02 — Preámbulo transparente

El mismo paquete inline íntegro, con o sin preámbulo, admite la misma
encomienda con idéntico objetivo, identidad y scopes. El preámbulo no
otorga permisos ni altera el trabajo autorizado.

### PC-03 — Integridad completa y selección inequívoca

Una alteración del objetivo, instrucciones, contrato o scopes respecto
del render validado, aunque conserve el encabezado, impide trabajar y
acreditar una entrega nueva. Un bloque mal formado o más de un marcador
produce rechazo, sin elección heurística ni fallback legacy.

### PC-04 — Respaldo explícito y vinculado

La ruta C sólo admite el paquete único identificado cuyos REQUEST.json
y PACKET.md superen la validación completa y coincidan con la identidad
recibida. Archivo ausente, identidad discordante o selección ambigua
bloquean antes del trabajo. La lectura de control-plane no amplía el
scope de producto del rol.

### PC-05 — Compatibilidad de operaciones no despachantes

capabilities, migrate y las operaciones internas legítimas conservan sus
contratos sin exigir un despacho ficticio. Una consulta legacy sin
marcador sigue disponible, pero no produce acreditación CDAD.

### PC-06 — Coherencia entre referencias y escritura

Un nuevo begin con referencia contract cubierta por write_scope se rechaza
con diagnóstico antes de persistir. La referencia living explícita puede
divergir sin que ese cambio por sí solo produzca P1. No hay reclasificación
automática ni debilitamiento de la protección de referencias contract.

### PC-07 — Preservación durable e idempotencia

El rechazo no modifica registros durables previos. Las repeticiones válidas
de begin y recepción conservan la idempotencia existente y no crean enlaces,
observaciones o recibos duplicados por esta feature.

### PC-08 — Intake coherente entre distribución y roles

Las definiciones canónicas, los agentes generados para ambos adaptadores
y los agentes desplegados mediante la instalación soportada expresan la
misma selección A/C/legacy y los mismos rechazos. Ninguna copia conserva
la primera línea como condición necesaria ni permite fallback legacy
ante un bloque inválido.

## Decisiones de diseño

- Regla compartida por familia de roles frente a parches por incidente:
  actualizar intake-core y su composición; evita divergencia entre roles.
- Validación canónica existente frente a protocolo de hashes adicional:
  reutilizar validate_request/render_packet y la comparación completa.
  No crear un segundo criterio de integridad.
- A frente a exigir cambios del runtime: tolerar exclusivamente el
  preámbulo; la integridad del paquete no se flexibiliza. C es una
  alternativa explícita, no una recuperación silenciosa.
- Cobertura de scope frente a comparar strings de rutas: reutilizar
  _scope_contains para conservar clases, raíces y política existentes.
- Replay frente a revalidación retroactiva: conservar el orden vigente;
  la nueva restricción gobierna nuevos efectos.

## Superficie técnica verificada

- sources/roles/architect.md:15–32: propietario de intake-core.
- scripts/cdad-generate.py:70,602–603: composición compartida.
- skills/cdad-cycle/scripts/cdad_packet.py:1409–1430:
  _scope_contains.
- skills/cdad-cycle/scripts/cdad_packet.py:1569,1782–1858:
  validate_request y render_packet.
- skills/cdad-cycle/scripts/cdad_dispatch.py:491–542:
  resolución del paquete y frontera dispatch.
- skills/cdad-cycle/scripts/cdad_delegate.py:536–581:
  frontera de transporte y bytes enviados al adaptador.
- skills/cdad-cycle/scripts/cdad_continuity.py:428–509,1041–1139:
  clases de referencia, planificación y replay de begin.
- skills/cdad-cycle/scripts/cdad_result.py:635–679:
  replay durable anterior a validación de recepción nueva.
- skills/cdad-cycle/references/cli-delegation.md:101–134:
  envoltura y semántica de rc.

## Verificación y deferred-hardening

Cada PC requiere evidencia de su consecuencia observable; reutilizar la
cobertura por capacidad existente antes de añadir pruebas. No se exige
una batería, cantidad de tests, cobertura porcentual o benchmark.

Diferido, no bloqueante:
- Fuzzing amplio del parser y combinatoria exhaustiva de transportes.
- Pruebas de carga, rendimiento y tamaños extremos sin consecuencia
  contractual identificada.
- Matriz exhaustiva de versiones de runtime.
- Interceptación nativa y resistencia frente a un agente que ignore sus
  instrucciones: exigirían otro alcance/harness, no se prometen aquí.

Toda ampliación del QA necesita una postcondición adicional aprobada o una
tarea posterior; no se incorpora como gate implícito.
