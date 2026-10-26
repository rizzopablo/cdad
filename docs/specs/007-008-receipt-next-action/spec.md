# 007-008 — Acción posterior al cierre de recibo

**Estado:** aprobada por el orquestador (HITL delegada) tras review sin bloqueantes; ajustes AJ1–AJ3 al final.  
**Epic:** `epic-007-reliable-cycle-operation`.  
**Dependencias:** 007-003 y 007-005.

## 1. Descripción funcional

Un cierre nuevo de recepción debe orientar al operador hacia la revisión del resultado, sin conservar una instrucción previa de despacho ni confundir recepción mecánica con aprobación.

Actualmente `_closing_body` hereda `head_body.next_action`, aunque el cuerpo ya acredita recepción. `resume` proyecta ese mismo valor. La corrección se realiza en el productor común del cierre, no reinterpretando la acción en cada consumidor.

Referencias verificadas:

- `skills/cdad-cycle/scripts/cdad_continuity.py:1414-1447`: construcción del cierre.
- `skills/cdad-cycle/scripts/cdad_continuity.py:1450-1542`: reconocimiento del cierre existente antes de construir otro.
- `skills/cdad-cycle/scripts/cdad_continuity.py:2654-2669,2716-2743`: proyección de continuidad.
- `docs/specs/007-003-continuity-at-edges/spec.md:65-100`: preservación del contexto, referencia al recibo, encadenamiento y compatibilidad histórica.
- `docs/specs/007-008-receipt-next-action/discovery.md`: descubrimiento de esta unidad.

## 2. Alcance y decisiones

### Dentro

- Sustituir la herencia de `next_action` exclusivamente al construir un cierre nuevo de recepción.
- Verificar el comportamiento por recepción ordinaria, entrada externa y recuperación del cierre pendiente.
- Preservar replay, continuidad, suspensión/reanudación y señales de recepción.
- Extender los fixtures existentes de 007-003, 007-004 y 007-007.

### Fuera

- Migrar, corregir o reinterpretar cierres históricos.
- Cambiar esquemas, identidad del cierre, almacenamiento, transportes, aprobaciones o disposición.
- Cambiar la forma de `status`.
- Introducir selección automática de una etapa posterior.
- Despliegue, activación global o publicación.

### Criterio de diseño

Se elige el cierre común frente a correcciones específicas en `resume`, recepción externa o recuperación: el hecho que invalida la acción previa es el mismo en todas las entradas y ya existe un productor compartido.

Se elige texto canónico frente a `null`: mantiene orientación explícita y evita que la reanudación sustituya una acción ausente por una instrucción genérica.

La compatibilidad histórica es deliberada: un cierre antiguo puede seguir mostrando una acción obsoleta. Esta unidad no autoriza reescribirlo ni cambiar su proyección.

## 3. Contrato

### 3.1 Precondiciones

Se conservan las precondiciones vigentes de `close_durable_receipt` y sus entradas públicas:

- Recibo durable válido e identidad compatible.
- Intento entero positivo declarado explícitamente.
- Integridad y cadena demostrable.
- Para publicar un cierre nuevo: contexto y autoridad exigidos por el mecanismo existente.
- Para reconocer uno existente: orden de reconocimiento e idempotencia vigentes.

Esta unidad no agrega requisitos al replay.

### 3.2 Acción canónica

Todo cierre **nuevo** producido por `_closing_body` contiene exactamente este valor JSON de `next_action`, sin comillas tipográficas ni puntuación adicional:

```text
recibo recibido mecánicamente; no repetir despacho/recepción; revisar el resultado sin presumir aprobación
```

El valor es independiente de la acción anterior, incluida su ausencia o `null`. No se concatena con ella.

### 3.3 Preservación del cierre

Respecto del comportamiento vigente, el único cambio funcional del cuerpo es el valor de `next_action`.

Se conservan:

- `goal` y `authority`.
- Decisiones previas, en su orden, seguidas de exactamente una incorporación de la decisión mecánica existente `RECEIPT_DECISION`.
- `uncertainties` y `references`.
- Presencia y valor de `budget`, `changes` y `evidence`, conforme al contrato vigente.
- Construcción de `receipt_checkpoint`: ruta normalizada y digest del recibo.
- Construcción de `prev`: digest y secuencia de la cabeza inmediatamente anterior.
- Identificadores y `record="checkpoint"`.

**Precisión:** preservar `prev` y `receipt_checkpoint` significa no cambiar sus reglas de construcción. No significa copiar los valores de esos campos desde el cuerpo anterior.

### 3.4 Identidad, replay e historia

La clave continúa siendo ejecución/paquete/intento. El contenido que identifica el recibo continúa siendo ruta normalizada/digest.

Un cierre existente demostrable se reconoce antes de construir otro. Si el recibo coincide, se devuelve el cierre existente sin escritura, aunque su acción sea histórica y obsoleta. Si no coincide, se conserva el rechazo vigente sin crear un segundo cierre.

No se recalculan ni sustituyen cuerpos históricos para imponer la acción nueva.

### 3.5 Lecturas y reanudación

- `cdad_continuity.py resume` proyecta literalmente la acción de la cabeza: para un cierre nuevo, la acción canónica.
- `reconcile` conserva su clasificación basada en recibo y journal, sin deducir aprobación del texto.
- En un contexto con recibo válido, autoridad vigente y sin materialización, conserva la señal `received` y `repeat_effect=false`.
- Suspender y luego reanudar una unidad con cierre nuevo restaura la acción canónica, sin repetir despacho ni recepción.
- No se exige esa acción durante la suspensión: ese checkpoint conserva su orientación específica de unidad suspendida.
- La forma de la vista compacta `status` no cambia.

## 4. Postcondiciones verificables

### PC-01 — Acción de todo cierre nuevo

Dado un contexto válido sin cierre previo, al cerrar el recibo por CLI, el cuerpo durable contiene `next_action` exactamente igual al literal de §3.2.

Variantes parametrizadas de acción previa: orden de re-despacho, otro texto válido y `null`.

**Oráculo:** JSON del cuerpo durable, no búsqueda de palabras en mensajes de consola.

### PC-02 — Contexto y enlace preservados

Al crear ese cierre:

- Los campos preservados de §3.3 mantienen sus valores y las ausencias opcionales previstas.
- `decisions` equivale a las decisiones anteriores más una sola `RECEIPT_DECISION`.
- `receipt_checkpoint` identifica el recibo durable por ruta normalizada y SHA-256.
- `prev` apunta a la cabeza anterior y la secuencia avanza exactamente un enlace.
- Los cuerpos anteriores no cambian de bytes.

**Oráculo:** comparación estructural de JSON, lectura de cabeza y digests calculados sobre los bytes almacenados.

### PC-03 — Convergencia de entradas sin aprobación

Las siguientes entradas producen un cierre nuevo con la misma regla de acción y preservación:

1. Recepción ordinaria con intento de continuidad.
2. Validación de recibo externo con cierre explícito.
3. Recuperación mediante `checkpoint-receipt` después de recibo durable, con o sin transición ya registrada.

En todos los casos, `semantic_status` permanece `pending`. Las rutas de cierre de un recibo ya durable no vuelven a recibirlo ni alteran sus bytes.

**Oráculo:** cuerpo y recibo JSON, snapshots de archivos y efectos existentes. Convergencia significa igualdad de comportamiento contractual, no igualdad de digests entre ejecuciones distintas.

### PC-04 — Replay y conflicto conservan historia

Repetir el cierre con igual identidad y recibo:

- Devuelve éxito con reconocimiento de no operación.
- Mantiene byte a byte cabeza, cuerpos y recibo.
- Conserva digest, secuencia y cantidad de enlaces.

Variantes: cierre nuevo inmediato; cierre histórico alcanzable tras enlaces posteriores; cierre histórico con acción previa obsoleta.

Para la misma clave con recibo de contenido distinto, se rechaza sin escritura ni segundo cierre.

**Oráculo:** snapshots de bytes y JSON del resultado. La variante histórica usa una cadena íntegra y demostrable; no modifica un cuerpo sin reconstruir correctamente su integridad en el fixture.

### PC-05 — Suspensión/reanudación conserva la orientación recibida

Después de un cierre nuevo, suspender la unidad, trabajar en otra unidad y reanudar la primera restaura la acción canónica.

Variantes: la otra unidad se cierra o se suspende.

El recibo original permanece byte-idéntico; no aparece otro despacho ni otra recepción del intento recibido. No cambia la restauración de acciones de contextos que todavía no fueron recibidos.

**Oráculo:** proyección de continuidad tras reanudar y snapshots de recibo, despachos y efectos.

### PC-06 — Lecturas coherentes y sin aprobación implícita

Inmediatamente después de un cierre nuevo, con autoridad vigente y sin materialización:

- `resume.projection.next_action` coincide exactamente con §3.2.
- `reconcile` informa `received` y `repeat_effect=false`.
- El recibo continúa con `semantic_status=pending`.
- No se agrega aprobación, disposición ni materialización.
- `status` conserva su forma contractual existente.

**Oráculo:** salidas JSON y comparación del estado durable antes y después de las lecturas.

## 5. Invariantes

1. Recepción mecánica no implica aprobación semántica.
2. No cambia la identidad ejecución/paquete/intento ni ruta normalizada/digest.
3. Reconocer un replay precede a construir un cierre nuevo.
4. Ningún cuerpo histórico se migra o reescribe.
5. No se repiten efectos por cierre, recuperación, lectura o reanudación.
6. No se introduce otro escritor, registro o almacenamiento de continuidad.
7. Se mantienen validación, integridad y límites de bytes existentes; no se trunca el literal para ajustarlo a un límite.
8. Fuera de cierres nuevos de recepción, esta unidad no redefine `next_action`.

## 6. Estrategia de pruebas

Un test por postcondición, con variantes parametrizadas. Reutilizar y extender antes de crear otro módulo:

- `tests/test_007_003_continuity_at_edges.py:1608`: recepción y replay.
- `tests/test_007_003_continuity_at_edges.py:1828`: recibo externo.
- `tests/test_007_003_continuity_at_edges.py:1958`: recuperación.
- `tests/test_007_004_termination_not_success.py:499`: recuperación sin nueva recepción.
- `tests/test_007_007_suspend_resume_units.py:557`: suspensión/reanudación tras recepción.

No duplicar fixtures ni convertir detalles internos de implementación en el oráculo principal. El literal esperado se declara de manera independiente en los tests; no se importa del productor.

La ejecución de suite completa se rige por la política común del paquete.

## 7. Criterios de aceptación

- Las seis postcondiciones tienen evidencia automatizada con las variantes indicadas.
- RED demuestra el arrastre previo mediante resultados observables, no errores del fixture.
- GREEN satisface la acción literal y las garantías de preservación, replay y ausencia de efectos repetidos.
- Las pruebas focalizadas existentes de 007-003, 007-004 y 007-007 conservan sus garantías.
- No cambian esquemas ni forma de `status`, ni aparecen migraciones o aprobaciones implícitas.
- Review verifica que el cambio se concentra en el productor común y no corrige artificialmente lectores o historia.
- La aprobación de esta especificación permanece pendiente de decisión explícita.

## 8. Evidencia de elaboración

**Rol:** architect, draft, read-only.  
**Archivos modificados por el rol:** ninguno.  
**Tests ejecutados:** ninguno.  
**Commit creado:** ninguno.  
**HEAD observado:** `5396d327c87bdb32ffa1e7b046ebcdbbbe9359f3`.

Comandos ejecutados desde la raíz del repositorio:

```bash
cat .cdad/packets/007-008-receipt-next-action-architect-draft-001/PACKET.md
sha256sum .cdad/packets/007-008-receipt-next-action-architect-draft-001/UNIT-CONTRACT.md
cat .cdad/packets/007-008-receipt-next-action-architect-draft-001/UNIT-CONTRACT.md docs/specs/007-008-receipt-next-action/discovery.md skills/cdad-cycle/references/design-principles.md
git status --short
git diff --stat
git rev-parse HEAD
sha256sum docs/cdad-policy.json
sed -n '45,100p' docs/specs/007-003-continuity-at-edges/spec.md
sed -n '60,76p' docs/specs/007-005-serial-reception/closure.md
sed -n '1400,1550p' skills/cdad-cycle/scripts/cdad_continuity.py
sed -n '2330,2370p' skills/cdad-cycle/scripts/cdad_continuity.py
sed -n '2640,2750p' skills/cdad-cycle/scripts/cdad_continuity.py
sed -n '1015,1105p' skills/cdad-cycle/scripts/cdad_packet.py
sed -n '1608,1668p' tests/test_007_003_continuity_at_edges.py
sed -n '1820,1848p' tests/test_007_003_continuity_at_edges.py
sed -n '1950,1985p' tests/test_007_003_continuity_at_edges.py
sed -n '490,530p' tests/test_007_004_termination_not_success.py
sed -n '550,615p' tests/test_007_007_suspend_resume_units.py
rg -n 'semantic_status|repeat_effect|def test_' tests/test_007_003_continuity_at_edges.py | tail -25
git status --short
git diff --stat
```

Resultados relevantes:

- Digest del contrato: `343243000cbbadd3deaf6239abd028791f697db0a2437ae15808a337b72c0642`; coincide con el paquete.
- Digest de política: `f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711`; coincide con el paquete.
- Las lecturas confirman herencia de `next_action`, reconocimiento previo del replay y proyección literal en `resume`.
- Estado observado al inicio y al final, sin diferencias entre ambas comprobaciones:

```text
 M docs/.cdad-state.json
?? docs/specs/007-008-receipt-next-action/
 docs/.cdad-state.json | 139 +++++++++++++++++++++++++++++++++++++++++++++++---
 1 file changed, 132 insertions(+), 7 deletions(-)
```

Estos cambios eran preexistentes a la intervención del rol.

## Ajustes del orquestador (review 2026-10-26)

**AJ1 — PC-01 incluye la acción ausente (MINOR).** Las variantes parametrizadas son: orden de re-despacho, otro texto válido, `null` y **clave `next_action` ausente** (se elimina la clave del input válido, no se sustituye por `null`). En las cuatro, el cuerpo durable contiene el literal exacto de §3.2.

**AJ2 — Cobertura mapeada, no «un test por PC» (MINOR).** Cada PC tiene cobertura explícitamente mapeada; una prueba puede cubrir varias PCs y una PC puede verificarse extendiendo varias pruebas existentes. Las variantes se mantienen parametrizadas; no se crean agregadores para satisfacer una restricción de organización.

**AJ3 — Precisión de las variantes.** (a) En PC-05, la aserción de la acción restaurada se ejecuta **inmediatamente después de `resume-unit`**, antes de cualquier `prepare → begin` posterior. (b) En PC-04, el conflicto usa un **recibo alternativo válido** (no un recibo corrupto): así se prueba conflicto de identidad/contenido y no validación.

**AJ4 — Decisión mecánica contractual (respuesta al test-writer).** El cierre nuevo añade exactamente este objeto a `decisions`, después de las previas y en este orden de claves:

```json
{"decision": "recepción mecánica del recibo durable (checkpoint-receipt)",
 "rationale": "el recibo existe y valida contra su payload durable: se registra la recepción MECÁNICA del efecto — no es aprobación semántica, no materializa, no dispone y no repite transporte ni recepción (§2.3)"}
```

PC-02 compara el objeto completo, no una subcadena. El valor se declara en el test de forma independiente; no se importa del productor.
