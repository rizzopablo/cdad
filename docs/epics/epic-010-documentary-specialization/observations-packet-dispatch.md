# Observaciones para 010-004 — despacho de paquetes

Evidencia recogida por el orquestador durante `010-000` (2026-10-29). No es
Discovery ni un contrato: son incidentes verificables para que la unidad
`010-004-packet-dispatch-ergonomics` los convierta en postcondiciones.

## I-1 — Transporte manual y divergencia de bytes

El paquete se copia a mano en el prompt del subagente. En el primer review de
spec, dos pares de backticks se perdieron en la copia; el reviewer rechazó
correctamente el paquete. La ruta A exige comparación byte a byte; no existe un
paso mecánico de transporte ni una ruta C emitida por el renderer.

Consecuencia: cualquier transcripción —humana o de modelo— puede invalidar el
encargo sin que el trabajo haya empezado.

## I-2 — El cierre del bloque JSON se lee como fin del paquete

El render canónico abre `---cdad-packet-json`, lo cierra con
`---end-cdad-packet-json` y continúa con el cuerpo. Un test-writer interpretó
ese cierre como "paquete parcial" y se detuvo sin ejecutar la comparación
canónica.

Consecuencia: el formato no explicita que el bloque es una cabecera y que la
comparación cubre desde el marcador hasta el final.

## I-3 — El contexto de ejecución se infiere

La cabecera declara `execution_id`, pero no la ruta del contexto v2. Dos
subagentes usaron `docs/.cdad-state.json` y `.cdad/execution.json` como contexto
y fallaron con "execution context fields do not match schema". La ruta correcta
es `.cdad/executions/<execution_id>/execution.json`.

Consecuencia: el rol debe deducir una ruta que la cabecera puede declarar.

## Criterio de cierre sugerido para 010-004

- La cabecera del paquete declara el contexto de ejecución utilizable sin
  inferencia.
- Existe una forma de despacho que no dependa de retranscribir bytes.
- El intake distingue explícitamente cabecera y cuerpo.
- Regresión de los tres incidentes: paquete divergente rechazado con diagnóstico
  accionable; cabecera+y cuerpo aceptados; contexto declarado aceptado y
  contexto ajeno rechazado nombrando el esperado.

No fijar mecanismo (ruta C, archivo, otro) antes del Discovery de la unidad.

## I-4 — Verificación de entrega no observable y bloqueo desproporcionado

En el resultado de `scribe-memory-002`, el rol informó `cmp` entre render y
PACKET.md, pero describió el cotejo del prompt recibido como «campo por campo».
Eso no acredita igualdad byte a byte de la entrega; tampoco demuestra corrupción
del paquete ni invalida por sí solo el borrador. El orquestador lo convirtió en
bloqueo automático y luego rectificó ese criterio a petición del usuario.

Problema a investigar: el transporte nativo puede no exponer los bytes recibidos
como artefacto verificable. Exigir al modelo que los reconstruya y certifique
puede producir una declaración no comprobable, en lugar de garantía mecánica.
No se afirma todavía que todos los runtimes tengan esta limitación.

Separar en Discovery tres evidencias: integridad del paquete publicado, integridad
de la entrega y fidelidad del resultado al encargo. Un `cmp` de render contra
PACKET.md prueba solo la primera; una comparación semántica no prueba la segunda.
Investigar cómo acreditar la entrega sin retranscripción ni autoatestación del
modelo y cómo diagnosticar honestamente lo no observable.

Disposición acordada con el usuario: registrar la limitación y contrastar el
borrador con las fuentes, sin repetir automáticamente todo el trabajo ni tratar
una declaración insuficiente como prueba de corrupción. Esto no elimina las
reglas vigentes ni autoriza ignorar divergencias reales, autoridad inválida o
contenido infiel. La mejora del protocolo corresponde a 010-004; este registro
no modifica por sí solo su contrato ni aprueba el cierre de 010-000.

## I-5 — Divergencia real en despacho reviewer de 010-004

El reviewer de la sesión `<session>` rechazó el packet
`010-004-packet-dispatch-ergonomics-reviewer-plan-review-001` antes de revisar.
El padre confirmó la causa: al copiar el prompt eliminó los backticks de
`"planned"` y `"next"` en el bloque de instrucciones. El render y los archivos
publicados eran íntegros; la entrega inline divergía. No es la incertidumbre
de observabilidad I-4, ni se descarta por trivialidad: el rechazo se conserva.

El FINAL TEXT original se conserva como `incident-reviewer-packet-001.md`
en `docs/specs/010-004-packet-dispatch-ergonomics/`, recibido mecánicamente con
`semantic_status: pending`. No constituye plan-review sustantivo: la spec
`3a52522f285e42756d7240f84b5b76338837c7642169970ae8893e708961a038`
sigue sin dictamen ni aprobación. No se rescata la entrega inline alterada
mediante ruta C. La recuperación es un nuevo encargo reviewer canónico,
sin cambiar la spec, con ruta C explícita si el intake vigente la permite;
no un renderer de ruta C aún no implementado. No se baja ningún gate.

## I-6 — Paquete nuevo publicado sin localizador PC-04 y rechazado en el gate del padre

El 2026-10-30 el orquestador publicó
`010-004-packet-dispatch-ergonomics-test-writer-red-005`
(`REQUEST.json` sha256 `b13f83cd130772501fcf2f9d7015386d34d650f0754b802f3a8ff96a4773f4de`,
`PACKET.md` sha256 `aa4863266deb94a123950eb20a66f75e8ee13b959e9ac5d7b873c6f14d55c90f`)
y su handoff de ruta C. El gate del orquestador supervisor lo rechazó **antes de
despachar**, y el rechazo es correcto:

```sh
python3 scripts/cdad_packet.py validate-packet --project-root . \
  --request .cdad/packets/010-004-packet-dispatch-ergonomics-test-writer-red-005/REQUEST.json \
  --packet  .cdad/packets/010-004-packet-dispatch-ergonomics-test-writer-red-005/PACKET.md
# ERROR: execution context not provided: the request declares no
# request.execution_context (a historical request) and --execution-context was
# not given. Pass the canonical v2 context explicitly
# (--execution-context .cdad/executions/<execution_id>/execution.json), or use
# a packet whose request declares its locator   [rc=2]
```

No hubo efectos: ni `begin`, ni despacho, ni recibo. La cabeza de continuidad
sigue en `seq 49` (`implementer-green-003`, cerrada): nada se anexó ni se fabricó.

**Causa medida.** El `REQUEST.json` no contiene `execution_context` (0
coincidencias) y la cabecera canónica del `PACKET.md` tampoco lo declara. La
copia del repo en el commit de preparación (`c1652c75`) escribe el localizador
**incondicionalmente** al publicar (`request[REQUEST_LOCATOR_FIELD] =
_canonical_execution_locator(...)`, dos rutas de `prepare`, ya presentes desde
`a273042e`): no puede producir ese request. La copia **instalada**
(`~/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py`, sha256
`171fcd1413ec8446272564388fe2165716569e6c3c070f02f4dca8008960e679`, stale D-1,
cero apariciones de `REQUEST_LOCATOR_FIELD`) sí publica requests sin el campo;
la ausencia simultánea de `current_decisions` es coherente con esa copia. La
edición manual del request después de publicarlo es una alternativa que los
bytes no excluyen, pero nada en el árbol la exige.

**Por qué la auto-validación no lo detectó (circularidad).** La matriz de §4.1
admite `request` sin localizador **más** `--execution-context` explícito como
«historical explicit load». Medido en este árbol: con el flag, `validate-packet`
devuelve rc=0 tanto con la copia del repo como con la instalada, y `render`
reproduce `PACKET.md` byte a byte; sin el flag, `render` falla con el mismo
error (rc=2). La sesión que publicó validó con el **mismo** artefacto que
publicó y con el fallback puesto: el `rc=0` acreditaba coherencia
request↔packet, no cumplimiento de PC-04. El handoff C
(`.cdad/010-004-t4-red-005-route-c.txt`, sha256
`79fac7a1134ed07f1e9744f3246f5d13e36f742e941113b0f58e413004651426`) se emitió
por la misma rama histórica: declara el localizador en la identificación
mientras el request publicado no lo declara. La afirmación de
`decision-t4-mechanical-guard.md` §10 («`validate-*` rc=0; `render` por
defecto == `PACKET.md`») no se sostiene para este paquete.

**Lección.** (1) Validar siempre con `scripts/cdad_packet.py` del repo —nunca la
copia instalada— y sin el fallback cuando el paquete es nuevo; (2) comprobar
explícitamente que `REQUEST.json` declara `execution_context` con el valor
canónico `.cdad/executions/<execution_id>/execution.json` **y** que la cabecera
canónica del `PACKET.md` lo declara igual; (3) un `render` byte-idéntico prueba
coherencia interna, no PC-04; (4) un handoff C emitido desde un request inválido
hereda el defecto. Es exactamente la clase de inferencia que I-3 y PC-04
prohíben: el localizador se declara, no se deduce del argumento.

**Addendum — segundo defecto de I-6, propio y detectado en la misma sesión.** El primer
sustituto, `…-test-writer-red-006`, quedó publicado con el contrato **duplicado**
en `inputs`: `prepare` inyecta el contrato principal y el orquestador volvió a
pasarlo por `--input` (la misma clase que obligó a retirar `-red-004`). Lo
detectó la lectura del `PACKET.md` publicado, no un validador: `validate-request`
y `validate-packet` daban rc=0 con el input repetido. Se retiró con `withdraw`
(`transition_key:
dbbda8c4bf178e05e70dd3baf09a0867d666df87df32660fa4c37aa43cc7f727`) y se
publicó `…-test-writer-red-007`, cuyos cuatro `inputs` son
`spec.md` (principal), `plan.md`, `decision-t4-mechanical-guard.md` y
`t3-closure.md`. Lección añadida: además de validar con el CLI del repo, **leer
el contenido publicado** (inputs, objetivo, decisiones) antes de entregar el
handoff; los validadores acreditan forma y binding, no que el encargo sea el
que se quiso preparar.

## I-7 — Despacho con `request_sha256` fabricado por el orquestador (paquete válido, metadato corrupto)

El 2026-10-30 el orquestador despachó
`010-004-packet-dispatch-ergonomics-implementer-green-005` y añadió a mano, en el
bloque de metadatos del despacho, un `request_sha256` **inexistente**:

```text
declarado (fabricado): 1dd89940b0a2ad1f0c0d5ec3b0c26c1c5cc4c4dd7b8e5e5f7d0e6b0eb3e4f3d3
real sha256sum .cdad/packets/…-green-005/REQUEST.json:
                       1dd89940c15298078f76495f8e869937735e5024cafbfc00456c65c95960e112
sha256sum .cdad/packets/…-green-005/PACKET.md:
                       2b4a32be23f6f242b463b62f464929e651cab070e3f8874c372d8293726c89d8  (13115 bytes)
```

Ambos valores tienen 64 hex: comparten los primeros 8 (`1dd89940`) y divergen
después. No es otra convención de serialización ni un digest de otro objeto: es
una copia corrompida del digest real, escrita de memoria en la prosa del
despacho.

**Clase distinta de I-6, no una repetición.** En I-6 el defecto estaba en el
artefacto publicado (request sin localizador PC-04, contrato duplicado en
`inputs`): el paquete mismo era inválido. Aquí el paquete es **válido e
íntegro** y lo corrupto es un **metadato del despacho que no pertenece al
paquete**: `REQUEST.json`, `PACKET.md` y los cuatro `inputs` son correctos, y los
validadores lo acreditan. Por eso ningún validador del paquete podía detectarlo:
la corrupción ocurrió aguas abajo de la publicación, en el vehículo.

**Medida del rol (fail-closed, sin efectos).** El implementer
(`<session>`) se detuvo en intake. Lo que sí validó, medido:
`validate-request` rc=0; `validate-packet` rc=0; `render` completo byte-idéntico
al `PACKET.md` publicado (`cmp` vacío, 13115 bytes); los 7 campos canónicos de
`render --route C` coinciden sin diferencias; `contract.sha256`
`fc6b2ccc…5d64` y `plan.sha256` `2ae8ada3…6685` coinciden. Descartó las
explicaciones benignas midiendo **siete digests candidatos** del mismo request:

```text
raw                                1dd89940c15298078f76495f8e869937735e5024cafbfc00456c65c95960e112  (= real)
raw + "\n"                         6399bd144427c6729e7cbbae5a2ff4892adc17c923d9841ac58ff5b178a4791e
json sort_keys compact             0b6cb9298470586caa2c69a0de5a84f02f00fc6d4aca486ddf8735ed61dc37f4
json sort_keys compact + "\n"      4db3c80536594cbaf83300cb2238b9a3bf61769218500f71ca00737ee465345b
json sort_keys indent=2            106c9fa8ce4a63fc85caaa0e715f274ba8a2a733b6c25f58a5b492815696e1de
json compact (orden original)      d82d12f7c7ec9ede7f3e11a1c786909fa5dda19be58969d761855949bde21584
json indent=2 (orden original)     c0320e31d74569134d3c880df86babb993bca0063ef0a08fe4536ab14468128b
```

**Ninguno** coincide con el valor declarado: no hay lectura del request —raw,
canónica o re-serializada— que produzca el digest despachado. Confirmado
también por el orquestador supervisor con los mismos siete caminos.

**Consecuencia: cero efectos.** La asignación no se ejecutó: sin `make`, sin
`pytest`, sin edición, sin commit. `reconcile` del paquete lo acredita:
`classification: not-started`, `signals.dispatch: none`, `receipt.state: absent`,
`repeat_effect: false`. No hubo despacho registrado ni recibo que retirar. El
retiro se registró como `withdraw` (007-006), `transition_key`
`5fda92b055ed077d4a0b21182c03c7aa8fda265baacb4341c075e436cad7fd1a`, y la cabeza
de continuidad del intento 26 (`begin`, seq 52, body `1a99ffe5…`) se cerró con
un checkpoint de retiro (seq 53, body `5b7dabb6…`) conservando paquete, intento,
autoridad y contexto, y declarando `next_action` de no despacho. Sin recibo.

**Origen del metadato.** `.cdad/010-004-implementer-green-005-route-c.txt` (736
bytes) contiene la identificación canónica de 7 campos **sin ningún hash
anotado**; el `request_sha256` no venía del renderer ni de `sha256sum`: lo
agregó el orquestador al redactar el despacho. Es la misma familia que I-1, I-5
y el addendum de I-6 —transcripción humana o de modelo— pero con un agravante
propio: no se perdió un carácter, se **inventó** un valor con la forma correcta
(64 hex, prefijo correcto), que es más difícil de detectar que un byte faltante.

**Lección operativa.** (1) Construir el bloque de despacho con
`python3 scripts/cdad_packet.py render --project-root <raíz> --request
.cdad/packets/<packet_id>/REQUEST.json --route C` y **copiar su salida
verbatim**: es exactamente el fallo que la ruta C existe para evitar, porque esa
salida solo lleva los 7 campos canónicos y ningún hash anotado que pueda
derivar; (2) si el despacho exige metadatos adicionales (`packet_sha256`,
`request_sha256`, `plan`), esos valores se producen **pegando la salida de
`sha256sum`**, nunca re-tipeando un digest de memoria ni completando un prefijo
conocido; (3) un metadato fabricado no se detecta con ningún validador del
paquete: `validate-request`/`validate-packet`/`render` dan rc=0 con el bloque
corrupto, así que la verificación del despacho debe ser mecánica por
construcción, no por relectura; (4) el rol hizo bien en detenerse: fail-closed
ante un metadato discordante, sin buscar otro paquete ni caer a legacy.

**Sustituto publicado.** `…-implementer-green-007`
(`REQUEST.json` `e23b9c18…f6c0`, `PACKET.md` `35d6e82e…f766`), idéntico a
`-green-005` salvo `packet_id` (verificado por diferencia de campos en el
request y por `diff` del `PACKET.md`: solo cambia el identificador). El primer
sustituto, `…-green-006`, se retiró antes de despacharlo (`transition_key`
`af44235a510b410142479226a8051dc2e02c1a1f8d1763788a7c17f2a213240e`) porque la
preparación volvió a pasar `Do not edit tests`, que `prepare` ya inyecta como
piso del rol: el invariante quedaba duplicado y eso ya no era «el mismo encargo
salvo el identificador». Misma clase que el addendum de I-6 —`prepare` inyecta
contrato e invariantes de rol, y el llamador no debe repetirlos—, ahora medida
también sobre `invariants`.

## I-8 — El test-writer no puede leer sus propios `instruction_sources` (raíz de implementación vs. rol de lectura acotada)

**Medido el 2026-10-30** en el dispatch PROPERTIES de T5
(`010-004-packet-dispatch-ergonomics-test-writer-properties-001`, sesión
`<session>`, intento 28). El FINAL TEXT del rol declara el
bloqueo, con dos intentos de lectura uno por archivo y **sin workaround** (no
`cat`, no copia, no otra vía); la traza de la sesión conserva el razonamiento y
la decisión de detener esa parte y reportarla (regla de límites de PD-15), en
lugar de rodearla con bash.

**Evidencia.** El bloque canónico del paquete declara
`instruction_sources` con `common.md` sha256 `37609c56…7110`,
`roles/test-writer.md` `5f52650e…b6b8` y
`substages/test-writer-properties.md` `44722aa6…ca32`; los tres digests
coinciden con `sha256sum` de los archivos reales. La policy del proyecto
(`docs/cdad-policy.json`, sha256 `f508ab1e…2711`) declara `skills` entre sus
`implementation_roots`, y el `read_scope` del paquete es
`docs/specs/010-004-packet-dispatch-ergonomics` + `tests`, sin `skills/**`:
el guard de lectura del runtime denegó los dos archivos
(`Permission denied: read`) por quedar fuera del scope de rol y bajo una raíz
de implementación. El paquete **no** es inválido: `validate-request`,
`validate-packet` y el render canónico dieron rc=0; el defecto es de
**ergonomía de despacho**, no de integridad del encargo.

**Consecuencia.** El rol no puede auditar el texto de su propia instrucción:
solo ve el bloque `cdad-instructions` que el render embebe en el `PACKET.md`
(una síntesis), no los archivos fuente que ese bloque condensa. Si el bloque
estático cambia, el rol lo detecta por el **digest** declarado —y solo si el
digest cambia—, nunca por lectura; una divergencia semántica que el render no
refleje, o que el rol no pueda cotejar contra la fuente, no es observable desde
el rol. La instrucción ejecutada sigue siendo la del paquete validado, así que
la garantía mecánica no se pierde; lo que se pierde es la capacidad del rol de
verificar por sí mismo que el texto que recibió es el que su fuente declara.

**Corrección propuesta (unidad futura; no se aplica en T5, fuera de alcance).**
Tres salidas posibles, a decidir con contrato: (a) declarar los
`instruction_sources` bajo una clase de lectura admitida para el rol (p. ej.
`instruction`/`documentation`, separada de `implementation_roots`), o (b)
exceptuar `skills/cdad-cycle/packets/**` de la denegación de lectura de
implementación conservando la prohibición sobre el resto de `skills/**`, o (c)
incluir los archivos fuente como `inputs` declarados del paquete y tratarlos
como contrato. Cualquiera cambia el contrato de scopes o el de preparación; no
se elige ni se implementa acá.
