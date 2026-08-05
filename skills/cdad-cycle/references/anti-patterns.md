# Anti-patrones documentados

Patrones a detectar y corregir cuando aparecen en cualquier etapa del ciclo.

## AP-1 — Single session para todo

**Síntoma**: el usuario dice "ya está, le pedí al LLM que escriba el test y el código en una sola pasada".

**Por qué es malo**: el agente alinea test e implementación entre sí. El test pasa porque fue escrito para el código que el agente iba a escribir, no porque verifique el spec. Pierdes el oráculo independiente.

**Corrección**: pedí al usuario que retomemos. Aunque el código "funcione", los tests no son confiables. Volvé a Etapa 3 con sesión `test-writer` aislada y reescribí los tests sin mirar el código actual. Después corré los tests contra el código existente: si pasan, está bien; si fallan, hay bug que el primer test no detectó.

## AP-2 — Test escrito después del código

**Síntoma**: el usuario implementa primero "para ver si funciona" y después escribe el test.

**Por qué es malo**: el test que escribís después del código tiende a verificar **lo que el código hace**, no **lo que el spec pide**. Es la trampa más sutil.

**Corrección**: si ya pasó, no podés deshacerlo, pero podés mitigarlo: pedile al usuario que revise el test contra el spec, **sin mirar el código**, y se pregunte "si el código fuera completamente distinto, ¿este test seguiría siendo válido?". Si la respuesta es "no estoy seguro", reescribilo desde el spec.

Para próximas postcondiciones, reforzá la disciplina: test primero, sí o sí.

## AP-3 — Test "verde" sin verificación empírica

**Síntoma**: alguien dice "el test pasa" pero no se corrió la suite.

**Por qué es malo**: la confianza no es evidencia. El test puede tener un bug que lo hace siempre pasar. La implementación puede tener side effects que rompen otros tests.

**Corrección**: corré la suite. Si tu entorno no permite ejecución, pedile al usuario el output exacto:

> *"Necesito el output de la suite. Pegame las últimas 20 líneas del run, incluyendo la línea de resumen final."*

No avances de fase con "yo creo que pasa".

## AP-4 — Implementer modifica tests

**Síntoma**: durante GREEN, el implementer encuentra que el test "está mal" y lo cambia para que pase.

**Por qué es malo**: la regla del implementer es **hacer pasar el test, no cambiarlo**. Si el test está mal, hay que volver al test-writer en una sesión aislada para corregirlo, no permitirle al implementer "ajustarlo".

**Corrección**: revertí el cambio del test. Si el test genuinamente está mal:

1. Cerrá la sesión del implementer.
2. Abrí sesión de test-writer.
3. Pasale: el spec, el test problemático, el motivo por el que parece estar mal.
4. El test-writer corrige (o explica por qué estaba bien y el implementer se confundió).
5. Volvé al implementer con el test corregido.

## AP-5 — Saltar el spec porque "es simple"

**Síntoma**: "es solo agregar un campo, no necesita spec".

**Por qué es malo**: las features que parecen simples al inicio son las que más frecuentemente revelan ambigüedades en implementación. Y "simple" para vos puede no ser simple para el LLM.

**Corrección**: aceptá la **variante mínima del spec**: un párrafo de descripción + un test que falla. No es overkill — es el mínimo que mantiene la disciplina.

> *"OK, no necesitamos los seis bloques. Pero un párrafo describiendo qué hace, un assertion concreto, y aprobación tuya. Tres minutos."*

## AP-6 — Spec aprobado en silencio

**Síntoma**: el spec existe pero no tiene marca de aprobación inequívoca; el usuario "asume que está aprobado".

**Por qué es malo**: en Etapa 4, cuando el reviewer detecta una divergencia, no vamos a saber si la divergencia es contra el spec original aprobado o contra una versión que cambió.

**Corrección**: agregar la marca explícita ahora. Línea final `Status: Approved by <X> on <fecha>` o frontmatter. Después seguimos.

## AP-7 — Memory Bank desactualizado

**Síntoma**: la feature se mergea, pero `activeContext.md` y `progress.md` no se tocaron.

**Por qué es malo**: la próxima sesión arranca sin contexto de lo que se acaba de hacer. El LLM no sabe que ya tenemos parser de fechas, propone reimplementarlo desde cero.

**Corrección**: bloqueá el cierre de Etapa 5. Aplicá patrón Scribe (drafteás vos, el usuario edita y commitea). 5 minutos, no se negocia.

## AP-8 — ADRs especulativos o ausentes

**Dos extremos malos**:

- **Especulativos**: ADR-001 "Vamos a usar PostgreSQL en algún momento". No hay decisión real, es expectativa. Ruido.
- **Ausentes**: se tomó decisión arquitectónica grande (ej. cambio de DB, nuevo bounded context) y no hay ADR.

**Corrección**: ADR cuando hay decisión real con consecuencias y trade-offs documentables. Si dudás, preguntá: *"¿alguien dentro de 6 meses podría preguntar 'por qué hicimos X así'?"* Si sí → ADR. Si no → no.

## AP-9 — CI skipeado

**Síntoma**: "el linter falla pero es cosa menor, mergeamos y arreglamos después".

**Por qué es malo**: "después" no llega. Las violaciones se acumulan. Cada PR que pasa con CI skipeado erosiona la confianza en CI.

**Corrección**: lo arreglás antes. Si genuinamente es trivial, son 2 minutos. Si es real, había una razón para que CI lo bloqueara.

## AP-10 — "Pasa por mí"

**Síntoma**: el usuario empieza a delegar al LLM, en el momento y sin pedido explícito previo, cosas que son indelegables por defecto (aprobación de spec, priorización del review, contenido del Memory Bank update).

**Por qué es malo**: erosiona el principio de aprobación del usuario en momentos clave. La calidad sostenible viene de la combinación dueño-del-proceso (humano o agente de mayor jerarquía) + LLM, no del LLM solo.

**Corrección**: señalá la indelegabilidad amablemente.

> *"Esto requiere tu juicio sobre <dominio/cliente/producto>. Yo puedo draftearlo o darte opciones, pero la decisión es tuya. ¿Te paso un draft para que lo edites?"*

**Excepción — no confundir con delegación legítima**: aprobación de spec (Etapa 2) y priorización de review (Etapa 4) admiten delegación a un agente experto **solo si el usuario lo pidió explícitamente para esa feature o etapa puntual**, no como default del proyecto. Ver "Excepción: delegación explícita a agente experto" en `stage-2-specification.md` y `stage-4-review.md`. Un pedido casual dentro de la conversación ("aprobalo vos, dale") sin ese contexto previo sigue siendo AP-10 — la diferencia es que el pedido explícito tiene que preceder al momento de aprobar, no coincidir con él.

## AP-15 — Autoaprobación no solicitada

**Síntoma**: el orquestador (u otro agente) asume por su cuenta que puede aprobar spec o priorizar review porque "se siente con suficiente contexto", sin que el usuario lo haya pedido explícitamente para esa feature.

**Por qué es malo**: la delegación de aprobación existe para casos donde el usuario, con su propio juicio, decide que confía el criterio a un agente. Si el agente se autootorga esa autoridad, no hay ninguna decisión del usuario detrás — es AP-10 con un paso extra de justificación.

**Corrección**: si no hubo pedido explícito previo, aprobación del usuario por defecto, sin excepciones. Si el orquestador está tentado a aprobar porque "esto es obvio" o "no vale la pena molestar al usuario", esa tentación es la señal de que hay que pasarlo al usuario, no la justificación para saltearlo.

## AP-11 — Refactor que rompe tests

**Síntoma**: el refactorer hace cambios y "ahora tres tests fallan, pero son menores, los arreglamos".

**Por qué es malo**: la regla del refactor es "comportamiento observable no cambia". Si tests fallan, cambió comportamiento. No es refactor; es modificación funcional sin spec.

**Corrección**: revertí el refactor. Si era genuinamente refactor y los tests estaban mal, eso es problema de los tests (volvé a test-writer). Si era modificación funcional, eso requiere actualizar el spec primero (volvé a Etapa 2).

## AP-12 — Property tests con seed aleatorio

**Síntoma**: property tests verdes localmente, rojos en CI a veces.

**Por qué es malo**: tests no determinísticos rompen la confianza en la suite.

**Corrección**: configurá seed fijo para property tests en CI. Hypothesis, fast-check y libs similares lo soportan. El seed se commitea junto con el test.

## AP-13 — Garbage Cascade (spec ambiguo con tests no exhaustivos)

**Síntoma**: la etapa de feature no usa cobertura exhaustiva (por diseño — ver "Convención de tests" en `stage-3-tdd.md`), pero el spec tiene postcondiciones vagas o sin numerar.

**Por qué es malo**: sin exhaustividad de tests, toda la carga de precisión recae en el spec. Un spec ambiguo produce tests de contrato que verifican una interpretación posible pero no la correcta, y una implementación que pasa la suite sin ser lo que el usuario necesitaba. El error se propaga en cascada desde Etapa 2 sin que nada en Etapa 3 lo detecte.

**Corrección**: no se abre RED con postcondiciones no numeradas o no testeables. Si aparece ambigüedad durante RED o GREEN, no se resuelve "a criterio" del test-writer o implementer — se vuelve a Etapa 2 a precisar el spec y se reaprueba.

## AP-14 — Mock sobre plumbing

**Síntoma**: el test-writer verifica orden de llamadas de middleware, nombres de funciones internas, o mockea colaboradores internos en vez de verificar el efecto observable.

**Por qué es malo**: fija una decisión de implementación en la etapa RED, antes de que exista implementación. Le quita al implementer la libertad de diseño que GREEN necesita, y acopla el test a una estructura interna que puede cambiar sin que el comportamiento cambie — el test se vuelve frágil y deja de ser un oráculo confiable del contrato.

**Corrección**: revertí el test. Reescribilo verificando el efecto que un consumidor externo del sistema (otro proceso, otro servicio, el usuario) puede observar — mensaje wire, resultado de command, evento emitido hacia afuera, auth rechazada. Si el efecto que querés verificar es puramente interno entre módulos, probablemente no corresponde a una postcondición del spec; revisá si el spec necesita precisión.

## Cómo usar este archivo

Cargalo cuando detectes señales de cualquiera de estos patrones. No lo cargues preventivamente; es ruido si todo va bien. Cuando intervenís contra un anti-patrón, citá el código (AP-N) en tu mensaje al usuario para que pueda buscarlo:

> *"Estamos cayendo en AP-2 (test después del código). Vamos a corregir antes de seguir."*
