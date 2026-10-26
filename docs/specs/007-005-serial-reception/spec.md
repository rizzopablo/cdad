# 007-005 — Recepción serial real

**Feature:** `007-005-serial-reception`  
**Epic:** `epic-007-reliable-cycle-operation`  
**Estado:** borrador para review  
**Contrato:** `.cdad/packets/007-005-serial-reception-architect-draft-001/UNIT-CONTRACT.md`  
**Aprobación:** orquestador (HITL delegada del dueño) tras review APTO CON AJUSTES; los ajustes AJ1–AJ4 están al final y prevalecen. **PC-03 enmendada el 2026-10-26** (`amendment-pc03.md`): la moneda del `begin` se acredita por encadenamiento, no por cercanía temporal no registrada.

## 1. Contexto y alcance

La unidad verifica un recorrido serial real en **el consumidor activo**, utilizando la versión adoptada `538ec57` y los mecanismos existentes de orientación, preparación, despacho, recepción y continuidad.

No añade comportamiento al producto. Su resultado es evidencia reproducible de una recepción real y una declaración explícita de sus límites.

### Dentro

- Comprobar adopción, procedencia y autoridad vigentes.
- Identificar una pregunta diferencial legítimamente pendiente.
- Preparar y despachar una sola unidad read-only.
- Consumir la entrega por la ruta indicada en `delivery`.
- Validar recibo, bytes y cierre de continuidad.
- Registrar evidencia privada en el consumidor y un manifiesto anonimizado en CDAD.

### Fuera

- Implementación, reparación o modificación del producto.
- Nuevos tests de producto, recibos, registros de intentos o almacenes de continuidad.
- Cambios en specs cerradas.
- Activación global, modificación de HOME, servicios o runtime.
- Selección o sustitución de modelo.
- Fabricación de trabajo o de fallos para acreditar capacidades del epic.

Se utiliza el procedimiento general publicado frente a ampliar un lanzador privado: el objetivo es observar la integración existente, no mantener una segunda ruta de orquestación. Un envoltorio que sólo lance trabajo no acredita recepción y queda fuera del recorrido de aceptación.

## 2. Precondiciones

Antes de preparar el tramo, el orquestador del consumidor debe demostrar:

1. **Adopción autorizada:** existe autorización vigente del dueño para la instalación adoptada en HOME correspondiente a `538ec57`.
2. **Procedencia comprobable:** los agentes y las CLI realmente utilizados corresponden a esa instalación. El chequeo del consumidor declara coherencia contra ella.
3. **Autoridad vigente:** la ejecución y el contrato del consumidor siguen autorizados; el operador que actúa bajo esa autoridad queda identificado en su `stage_history`, mediante el procedimiento canónico, sin edición manual.
4. **Unidad elegible:** la unidad del consumidor está activa, no suspendida y habilitada para el tramo. Si requiere reanudación, ésta debe completarse por `resume-unit` antes de comenzar.
5. **Pregunta pendiente real:** el último dictamen recibido y la continuidad vigente dejan abierta la verificación diferencial definida en §3.
6. **Presupuesto operativo:** un paquete, una sesión y un despacho; sin reintentos automáticos ni cambio de modelo ante cuota o fallo del runtime.

**Precisión de interfaz:** el chequeo existente imprime `verdict: COHERENT` y devuelve `rc=0`; aquí «COHERENTE» designa ese resultado. El código cero aislado no prueba que la instalación sea `538ec57`: deben conservarse también versión y procedencia.

Si falta alguna precondición, se registra su causa y la recepción permanece pendiente. No se sustituye por pruebas controladas.

## 3. Definición del tramo y contrato

### Objetivo diferencial

Determinar, respecto del último dictamen entregado:

- qué ejecutable y contexto utiliza realmente el observable **E3-T02**;
- cuál es el observable exacto bajo la composición conservada.

El paquete debe referenciar privadamente el dictamen antecedente y distinguir lo ya resuelto de la pregunta restante. No vuelve a encargar una decisión amplia sobre alternativas ni presume el resultado de la comparación.

### Responsabilidades

**Rol despachado:** examina evidencia autorizada y devuelve un informe breve como FINAL TEXT. No escribe archivos, modifica producto, decide alcance ni aprueba propuestas.

**Orquestador del consumidor:** prepara, registra, recibe y ejecuta únicamente los efectos mecánicos autorizados mediante las CLI existentes.

**Orquestador de CDAD:** conserva el manifiesto anonimizado, contrasta las postcondiciones y propone el cierre. La recepción mecánica no aprueba el informe ni cierra por sí misma un gate.

### Identidades

Se mantienen correlacionados:

- ejecución `E`;
- paquete `P`;
- intento entero de continuidad `N`;
- intento textual del transporte;
- sesión del despacho;
- descriptor, recibo y checkpoint.

`N` no se deduce del identificador textual del intento.

Estas identidades completas permanecen en el consumidor. Los documentos de CDAD utilizan alias, sin IDs de sesión, rutas internas absolutas ni configuración local.

## 4. Postcondiciones verificables

| PC | Resultado observable | Comprobación |
|---|---|---|
| **PC-01** | Adopción autorizada de `538ec57`, procedencia, coherencia y autoridad vigente están acreditadas; el operador figura en `stage_history`. | Salida íntegra del chequeo, referencias con digest y registro canónico de historial. |
| **PC-02** | La vista compacta orientó el tramo y `prepare` produjo un paquete para la pregunta diferencial pendiente, con rol read-only y sin permisos de escritura. | Captura de `status`, `PACKET.md`, `REQUEST.json` y antecedente recibido; comparación del objetivo y scopes. |
| **PC-03** | Existe un `begin` para `E/P/N` y `verify-begin` lo validó inmediatamente antes del único despacho, sin escritura de continuidad intermedia. | Salidas y secuencia temporal privada; coincidencia de identidades y digest del cuerpo. |
| **PC-04** | Se produjo un despacho real y su registro conserva la correlación con `E/P/N`, intento textual y sesión, con observaciones honestas del runtime y sin override contrario a la política. | Registro canónico, salida del transporte y `record` con el mismo `--continuity-attempt N`. Los valores desconocidos siguen declarados como desconocidos. |
| **PC-05** | El sobre declara una entrega válida y el consumidor aplicó exactamente la ruta de `delivery`. | Sobre completo y comandos: `staged` conduce a `receive`; `received` a validación del recibo existente, sin recibir otra vez. |
| **PC-06** | El recibo valida los bytes originales del informe y mantiene `semantic_status=pending`. | `validate-receipt`, hashes de partes y comparación con los bytes recibidos; sin reescritura, resumen o regeneración del payload. |
| **PC-07** | Existe un cierre de continuidad demostrable para `E/P/N`, con `receipt_checkpoint` que referencia el recibo y su digest. | Validación de recibo, `reconcile`, `resume` y verificación de la cadena; no basta un cuerpo aislado o un `begin` histórico. |
| **PC-08** | El `status` final es coherente, muestra la siguiente acción y no exige repetir efectos; el manifiesto permite reproducir PC-01…07 y declara lo no observado. | Captura final, comprobación del manifiesto y registro de los efectos pendientes o ya realizados. |

Una postcondición sin evidencia queda **pendiente**, no satisfecha por inferencia. Registrar un bloqueo cumple la contingencia, pero no equivale a recepción aceptada.

## 5. Procedimiento

Los pasos operativos corresponden al orquestador autorizado del consumidor, no al rol read-only despachado.

1. **Verificar precondiciones.** Conservar autorización, versión/procedencia, chequeo de coherencia y registro del operador.
2. **Consultar la vista compacta.** Seguir la operación y referencias que indique. Una incoherencia bloqueante se registra; no se corrige editando el estado.
3. **Confirmar el delta.** Contrastar el último dictamen con la continuidad vigente. Si la pregunta ya está resuelta, detener: no hay tramo elegible.
4. **Preparar el paquete con `prepare`.** Un objetivo diferencial, una sesión, scopes read-only y presupuesto explícito.
5. **Publicar `begin`.** El UPDATE declara `E/P/N`, objetivo, antecedentes, incertidumbres, presupuesto y siguiente acción.
6. **Ejecutar `verify-begin` inmediatamente antes del transporte.** Conservar su salida exitosa. Entre esa comprobación y el despacho no se escribe continuidad.
7. **Despachar una sola vez.** Conservar la correlación privada y las observaciones reales del runtime.
8. **Registrar con el mismo `N`.** En transporte nativo, ejecutar `record --continuity-attempt N`, que prepara mecánicamente los bytes y emite el sobre. En transporte externo, conservar el registro canónico y el sobre del recorrido existente; no ejecutar un segundo `record` para duplicarlo.
9. **Consumir por `delivery`:**
   - `staged`: ejecutar `receive` sobre el descriptor indicado, propagando `N`; no volver a preparar las partes.
   - `received`: validar el recibo indicado; no ejecutar otra recepción ni volver a staging.
   - `none`, contradicción o artefacto inválido: no avanzar como recepción exitosa; registrar el bloqueo y reconciliar únicamente cuando corresponda.
10. **Validar recibo y continuidad.** Confirmar `semantic_status=pending` y el cierre enlazado. Si falta el cierre, recuperar sólo ese efecto con el mecanismo existente, sin repetir transporte o recepción.
11. **Aplicar sólo efectos pendientes y autorizados.** Cualquier materialización utiliza la autorización y el mecanismo canónicos; ninguna transición concede aprobación implícita.
12. **Capturar salida y manifiesto.** Registrar `status` final, PC satisfechas, pendientes y límites. El cierre requiere decisión explícita de la autoridad competente.

`checkpoint-receipt` puede quedar ejecutado por la recepción o validación con cierre. No se exige repetirlo si ya existe el cierre correcto: se verifica su identidad.

### Comandos reproducibles de comprobación

Variables privadas del operador:

- `C`: raíz del consumidor.
- `S`: scripts de la instalación adoptada.
- `X`: contexto de ejecución.
- `P`: paquete.
- `N`: intento entero.
- `R`: recibo durable.

```sh
python3 "$S/cdad-version-check.py" --project-root "$C"

python3 "$S/cdad_packet.py" status --project-root "$C"

python3 "$S/cdad_continuity.py" verify-begin \
  --project-root "$C" --execution-context "$X" \
  --packet "$P" --attempt "$N" --json

python3 "$S/cdad_result.py" validate-receipt \
  --project-root "$C" --receipt "$R"

python3 "$S/cdad_continuity.py" reconcile \
  --project-root "$C" --execution-context "$X" \
  --packet "$P" --json

python3 "$S/cdad_continuity.py" resume \
  --project-root "$C" --execution-context "$X" --json

sha256sum "$C/.cdad/packets/$P/PACKET.md" \
  "$C/.cdad/packets/$P/REQUEST.json" "$R"
```

La comprobación `verify-begin` acredita el instante previo al despacho; no se exige que vuelva a aprobar después de avanzar la cabeza.

Las opciones completas de preparación, transporte, registro y recepción se toman de las CLI instaladas y sus referencias canónicas. No se inventan opciones ni se introduce un wrapper.

## 6. Evidencia y manifiesto

### Conservación privada

Permanecen en el consumidor:

- autorización, identidad del operador y registro de historial;
- versión, procedencia y salida de coherencia;
- vistas compactas inicial y final;
- contexto, paquete, request y antecedente del objetivo diferencial;
- UPDATE, salidas de `begin` y `verify-begin`;
- evidencia del despacho y registro;
- sobre completo y descriptor, cuando corresponda;
- informe original, recibo y salidas de validación;
- cabeza y cuerpos necesarios para demostrar el cierre;
- comandos exactos, códigos de salida y orden de ejecución.

### Manifiesto en CDAD

El manifiesto es documentación de evidencia, no un nuevo ledger operativo ni otra autoridad sobre intentos.

Cada entrada contiene:

| Campo | Contenido exigido |
|---|---|
| Alias | Identificador neutro del artefacto. |
| Ruta | Ruta parametrizada respecto de una raíz privada, sin identidad interna. |
| SHA-256 | Digest de los bytes originales privados. |
| Rol | Productor o responsable de la evidencia. |
| Comando reproducible | Comando con variables que permita localizar, hashear o validar el artefacto. |
| Resultado | Código de salida y conclusión comprobable, sin filtrar datos privados. |
| Cobertura | PC y borde que acredita. |
| Límite | Qué no demuestra o qué permanece sin observar. |

La correspondencia entre variables, alias y rutas reales se conserva privadamente y debe estar disponible al verificador autorizado. Sin esa resolución, el manifiesto no acredita reproducibilidad.

No se atribuye al texto anonimizado el digest de los bytes originales. Si se publica un extracto sanitizado, se distingue explícitamente de su fuente privada.

## 7. Invariantes y aceptación

### Invariantes

- Un paquete, una sesión y un despacho; sin reintentos automáticos.
- Ninguna escritura del rol despachado.
- Estado, intentos, disposición y continuidad se modifican sólo mediante sus mecanismos canónicos.
- Recibir y materializar no aprueban.
- La continuidad conserva `E/P/N` y no se rebobina para forzar un cierre.
- Una unidad suspendida no avanza.
- Los documentos CDAD no contienen identidad privada del consumidor.
- La evidencia ausente, inconclusa o invalidada no se convierte en acreditación.

### Criterio de aceptación

La recepción puede proponerse como aceptada únicamente cuando:

1. PC-01…PC-08 tienen evidencia reproducible.
2. El informe responde a la pregunta diferencial o declara fundadamente sus incógnitas; su recepción no sustituye la revisión semántica.
3. No se repitieron efectos ni se editaron manualmente estado o encargos.
4. El manifiesto distingue evidencia real, controlada y no observada.
5. La autoridad competente revisó la evidencia y decidió explícitamente.

No se requieren tests de producto nuevos: esta unidad observa comportamiento existente y no modifica su contrato. Una brecha nueva demostrada se registra para decisión y alcance propios; no habilita una reparación improvisada ni duplicar pruebas de 007-001/003/004/006/007.

La suite completa se rige exclusivamente por la política común del paquete; no sustituye ninguna PC de recepción real.

## 8. Qué NO se declara y tabla de límites

| Capacidad o situación | Declaración admisible |
|---|---|
| Entrada, despacho, recepción y continuidad recorridos realmente | Observado en el consumidor, limitado al tramo y evidencia identificados. |
| Reparación o recuperación que no ocurrió naturalmente | «Verificado en entorno controlado, no observado en consumidor», sólo con referencia a esa evidencia; en otro caso, «no observado». |
| Retiro y republicación no ejercidos en este tramo | No observados en este tramo; las pruebas anteriores no se presentan como uso real aquí. |
| Suspensión y reanudación no ejercidas | No observadas en este tramo. |
| Fallos, timeout, cuota o interrupciones no ocurridos | No observados; no se provocan para acreditar el epic. |
| Otros consumidores o transportes no utilizados | No observados. |
| Corrección semántica del informe | Requiere revisión separada; el recibo no la acredita. |
| Aprobación o ampliación de alcance del consumidor | No otorgada por esta unidad. |
| Concurrencia, atomicidad global o interceptación universal del runtime | Fuera de alcance. |
| Falta de autorización, trabajo pendiente o llegada | Recepción pendiente y feature sin cierre. |

**Observación de alcance:** recorrer la integración no implica ejercitar todos sus ramales. En particular, el recorrido feliz no acredita recuperación de fallo, retiro ni suspensión si éstos no ocurrieron. Tampoco modifica los criterios de cierre del epic.

## 9. Riesgos y contingencia

| Riesgo | Respuesta obligatoria |
|---|---|
| Coherencia de una instalación distinta de la adoptada | Verificar versión y procedencia además del veredicto. |
| Repetir trabajo ya entregado | Comprobar el delta antes de preparar. Sin delta, detener. |
| Confundir rc o terminación con recepción | Validar `delivery`, su artefacto y el recibo. |
| Recibo durable con continuidad pendiente | Recuperar sólo el cierre existente; no volver a despachar. |
| Cuota, fallo de runtime o despacho sin llegada | Registrar causa y efectos conocidos; sin cambio de modelo ni reintento automático. |
| Fuga de identidad en evidencia | Mantener originales privados y revisar el manifiesto antes de materializarlo en CDAD. |
| Necesidad de diagnóstico externo para completar el recorrido | Registrarla como límite o brecha; no ocultarla para declarar satisfecho el recorrido feliz. |

Si el tramo no puede ejecutarse o completarse, el registro de bloqueo identifica el borde alcanzado, evidencia disponible, efectos conocidos, incertidumbres y condición necesaria para retomar. La feature permanece abierta y la recepción pendiente.

## 10. Base y evidencia de este borrador

Fuentes:

- `discovery.md`, secciones «Recomendación y autoridad», «Cadena de evidencia y verificación» y «Verificación, límites y postcondiciones candidatas».
- Plan del epic, secciones «Contratos entre features», «Criterios de aceptación del epic» y «Autoridad».
- Spec 007-003, §2.1–2.4: intento entero, comprobación pretransporte y cierre común.
- Spec 007-004, §4 y §6: contrato del sobre y consumo por `delivery`.
- Spec 007-007, «Interacción con operaciones existentes»: prohibición de avance de suspendidas.
- `skills/cdad-cycle/references/re-entry.md:104-136`: consumo por entrega y recuperación de continuidad.
- `skills/cdad-cycle/references/continuity.md:16-25`: superficies de comprobación y cierre.
- `skills/cdad-cycle/scripts/cdad-version-check.py:34-39,229-235`: veredicto de coherencia y códigos.

**Trabajo del architect:** lectura de archivos mediante `read`, `cat`, `sed` y búsquedas acotadas `rg`; consultas:

```sh
git status --short
git rev-parse HEAD
sha256sum \
  .cdad/packets/007-005-serial-reception-architect-draft-001/UNIT-CONTRACT.md \
  docs/cdad-policy.json
```

Resultados:

- HEAD observado: `3b284bb2184bb8e5fe7aa3a3ac889c0d4b1d06ec`.
- Contrato: `44b44b11efd97df22c5c33fa8e7f25915af5ae43ab67a581608f7d188c3ae862`.
- Política: `f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711`.
- Ambos digests coinciden con el paquete.
- Estado observado: ` M docs/.cdad-state.json`; no se atribuye ese cambio a esta tarea.
- Una búsqueda de `references/version*` no encontró esa ruta; la interfaz se verificó directamente en `cdad-version-check.py`.

**Archivos modificados por el architect:** ninguno.  
**Tests, despachos y operaciones mutantes ejecutados:** ninguno.  
**Commit creado:** ninguno.  
**Recepción real en esta tarea:** no observada.  
**Aprobación del borrador:** pendiente.


## Ajustes del orquestador (review 2026-10-26)

**AJ1 — Predicados mecánicos y decisiones semánticas separados (bloqueante resuelto).** PC-01, PC-02 y PC-08 se reescriben así:
- **PC-01 (mecánica):** el `status` del consumidor declara `hitl_delegation.status == "active"` y `authority_ref` con digest igual al contrato citado; el chequeo de versión devuelve `verdict == "COHERENT"` con `rc == 0` **y** la versión/procedencia observada igual a la adoptada; el despacho registra `runtime` y `session`. La *vigencia* es un juicio de la autoridad y se conserva como decisión registrada, no se infiere del digest.
- **PC-02 (mecánica + decisión):** existe una **decisión registrada del delta** que (a) cita el antecedente por `sha256`, (b) enumera lo ya resuelto, (c) formula la pregunta restante, y (d) nombra el rol/substage del encargo. Sus bytes acreditan que la decisión existe; la corrección del juicio corresponde al gate humano/delegado, no a la PC.
- **PC-08 (mecánica):** `status` final devuelve un `entry` de la tabla cerrada y un `next.operation.verb` explícito, `reconcile` no reporta el intento como irresoluble, y el manifiesto valida (abajo). «No exige repetir efectos» se acredita por esos campos, no por lectura libre.

**AJ2 — Par rol/substage declarado (bloqueante resuelto).** El tramo se prepara con `--role architect --substage draft` (subfases válidas del rol: `discovery`, `brainstorm`, `draft`; `draft` es la que produce el informe que se encarga). La plantilla de `prepare` conserva `--role`, `--substage`, `--objective`, `--input` del antecedente y scopes read-only; `REQUEST.json` debe coincidir por igualdad con esos valores.

**AJ3 — Recuperación del cierre (menor).** Si la recepción dejó el recibo validado y falta el cierre, la recuperación usa la interfaz existente, **mutante y condicionada**, con el mismo N entero: `cdad_result.py validate-receipt --receipt R --close-continuity --continuity-attempt N`. No se repite transporte ni recepción.

**AJ4 — Verificación mecánica del manifiesto sin CLI nueva.** No se añade comportamiento al producto ni tests de producto: la unidad no cambia contrato. La aceptación exige un **comando reproducible declarado en el manifiesto** que compruebe, contra los originales privados: campos obligatorios, existencia, `sha256` de cada fuente, cobertura de PC-01..PC-08 y ausencia de identidad del consumidor en el texto materializado. Su salida íntegra se conserva en `closure.md`; un manifiesto que no valide deja la PC pendiente. Si en el futuro hiciera falta un validador reutilizable, será una unidad propia con sus tests.
