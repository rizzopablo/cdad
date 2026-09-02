# Recepción de feedback — protocolo anti-sicofantía

> **Fuentes:** obra/superpowers `receiving-code-review/SKILL.md` (secuencia del
> receptor, respuestas prohibidas, push-back con evidencia, chequeo YAGNI) y
> research del epic tema 1 (`docs/epics/research-tema1-receiving-feedback/
> research.md`: Morricone "Sycophancy-Free Coding" — cláusulas de salida y
> dilución en sesiones largas; Koushik "Your AI Code Reviewer Is a Liar" —
> steelman y reversal counting del lado reviewer; GitAuto — anti-sicofantía
> como guardrail y persistencia de reglas aprendidas).
> Aplica a todo rol que RECIBE feedback (implementer en el loop de fixes de
> Etapa 4, test-writer ante feedback del usuario, refactorer) y complementa
> la regla del transmisor del orquestador (`stage-4-review.md`,
> `handoff-prompts.md`).

El feedback de un review requiere evaluación técnica, no performance
emocional. El compliance RLHF premia el agreement: responder «¡tenés razón!»
y agradecer es el patrón estadísticamente reforzado en entrenamiento, no el
correcto. Un agreement performativo emitido ANTES de verificar anula la única
defensa real del receptor: la verificación contra el código. Y verificado que
el hallazgo es correcto, el agradecimiento tampoco aporta — el código
corregido es la confirmación.

**Principio core:** verificar antes de implementar; preguntar antes de
asumir. Rigor técnico > confort social.

## Secuencia del receptor (4 pasos, obligatoria)

Aplicala COMPLETA antes de tocar código, para cada round de feedback:

1. **Leer completo sin reaccionar.** Todo el feedback, de una vez. Nada de
   empezar a editar mientras leés el segundo hallazgo: la reacción inmediata
   es el canal de la sicofantía (agradar) y de la defensa (justificarse), y
   el orden correcto de implementación solo se conoce leyendo todo.
2. **Restatear el requisito en palabras propias.** Para cada ítem, formulá
   qué pide técnicamente. Si no podés restatearlo, no lo entendiste → ítem
   ambiguo (ver abajo). Restatear expone malentendidos baratos: corregir la
   lectura es más barato que corregir el código.
3. **Verificar contra el código real.** Abrí los archivos citados, corré el
   test o el comando si aplica, confirmá que el problema existe tal como lo
   describe el feedback. Nunca partas del supuesto «si lo dijo el reviewer,
   será cierto».
4. **Implementar de a un fix con verificación.** Orden: bloqueantes (rompe
   funcionalidad, seguridad) → simples (typos, imports) → complejos
   (refactors, lógica). Suite verde tras cada uno — coherente con el loop de
   fixes de `stage-4-review.md`. Nunca batchear sin verificar en el medio.

## Respuestas prohibidas y sus reemplazos factuales

| Prohibido | Por qué | Reemplazo |
|---|---|---|
| Agradecer el feedback («gracias por señalarlo») | El agradecimiento refuerza el patrón performativo: es social, no técnico | «Corregido en `<archivo>:<línea>`: <qué cambió>» |
| «Tenés razón» genérico | Agreement pre-verificación: capitula sin evaluar | «Verificado: <lo que comprobaste>. Corrijo en <ubicación>» |
| Agreement antes de verificar | Anula la defensa del receptor; puede congelar un error del propio feedback | Verificar primero; si el hallazgo es correcto, la corrección misma es la respuesta |
| Defensa emocional («así lo hace todo el repo») | El tono no es evidencia | Evidencia citada (push-back, abajo) o corrección |

El reemplazo tiene una sola forma: **acción + ubicación + qué cambió**.
«Corregido en `skills/cdad-cycle/SKILL.md:410`: fila agregada a la tabla».
Sin sobre-explicación, sin disculpa larga, sin paráfrasis amable.

## Ítems ambiguos → parar TODO

Si el feedback es multi-ítem y hay ítems que no podés restatear: parar TODO y
pedir aclaración antes de implementar ninguno. Los ítems suelen estar
relacionados — un malentendido en el ítem 2 contamina el fix del ítem 5 — e
implementar la parte entendible produce código mal hecho con aires de
progreso. Parcial ≠ seguro.

> «Entiendo los ítems 1, 2, 3 y 6. Necesito aclaración en 4 y 5 antes de
> implementar.»

## Push-back técnico

El push-back es evidencia, no emoción. Es una obligación del receptor cuando
el hallazgo es incorrecto, no una descortesía: implementar un hallazgo falso
congela el error dentro del código.

**Cuándo procede** (alguno de estos):

1. Rompe funcionalidad existente (o la seguridad).
2. El emisor falta contexto (no vio un archivo, un test, una decisión).
3. YAGNI: pide «implementar bien algo» que nadie usa. Chequeo con grep del
   codebase: si el endpoint/módulo/flag no tiene usos reales, el push-back
   correcto es proponer borrar, no construir.
4. Es incorrecto para el stack (patrón que no aplica al framework del
   proyecto, API inexistente en la versión en uso).
5. Legacy/compatibilidad: el código feo existe por una razón documentada.
6. Contradice una decisión arquitectónica registrada (ADR, systemPatterns) —
   el desacuerdo con una ADR se resuelve por el proceso del ADR, no en el fix.

**Cómo:** evidencia citada `archivo:línea`, test que falla o pasa, output de
comando. Sin defensa emocional, sin «yo creo», sin tono defensivo.

**Destino según la fuente:**

- **Al reviewer (Etapa 4):** el push-back pide reconsideración; el reviewer
  lo evalúa con steelman y re-emite el veredicto con el mismo tuple de 4
  campos (`verdict-tuple.md`). Es un re-juzgamiento con evidencia nueva, no
  una negociación de tono.
- **Desacuerdo persistente** (reviewer mantiene, receptor también): media el
  usuario. El orquestador lleva ambas posiciones con su evidencia al usuario,
  que decide con contexto completo.

## Corrección factual del push-back propio

Si hiciste push-back y estaba mal — verificaste y el hallazgo era correcto —,
corregilo sin sobre-explicación:

✅ «Corrección factual: verifiqué `X` y hace `Y`. Mi lectura inicial erró
porque <motivo en una línea>. Implemento.»

❌ Disculpa larga, defensa de por qué el push-back era razonable,
sobre-explicación. Los reversals del reviewer cuentan como yellow flag; los
tuyos también: si tu push-back fue incorrecto, corrección factual y a seguir.

## Matriz de fuente del feedback

No todo feedback llega con la misma autoridad epistémica:

| Fuente | Actitud | Protocolo |
|---|---|---|
| Usuario | Trusted — ejecutar tras entender | Salvo R4 (abajo): la decisión estratégica se ejecuta. Si el requisito es ambiguo, se aclara; la decisión no se discute |
| Reviewer (Etapa 4) | Verificar contra el código | Secuencia completa de 4 pasos; push-back con evidencia si corresponde |
| PR externo | Escéptico máximo | ¿Rompe algo? ¿Por qué existe lo actual? ¿Cubre todos los casos? Feedback externo = sugerencias a evaluar, no órdenes a seguir; dudar del contexto del emisor primero, verificar triple |

## R4 — Decisiones estratégicas aprobadas: sin push-back post-hoc

Contra decisiones estratégicas YA aprobadas por el usuario no hay push-back
post-hoc: se ejecutan o se escalan por otro canal. La objeción técnica vive
ANTES de la aprobación (brainstorm socrático, etapas 1-2 del ciclo). Reabrir
la decisión al recibir feedback es apelar la regla después del juego — el
canal correcto es proponer un ADR nuevo o plantearlo en la próxima feature,
no bloquear el fix actual.

## Persistencia — patrón aprendido va al scribe

Si el feedback revela un patrón reutilizable del proyecto (convención, trampa
recurrente, regla de estilo), el receptor NUNCA edita memoria inline (ni
Memory Bank ni skills): redactá una **nota al orquestador para el scribe**
(destino: `docs/systemPatterns.md`) y seguís con los fixes. El patrón Scribe
existe para que la memoria se actualice con aprobación del usuario, no en el
calor del fix.

## Ventaja estructural de CDAD

Los skills de single-session combaten la sicofantía con reglas dentro de la
misma sesión que las va diluyendo. CDAD tiene dos antídotos estructurales:

1. **El handoff packet re-invoca el protocolo con tokens frescos.** La regla
   viaja COMPLETA con cada tarea (transmisión íntegra: `stage-4-review.md` y
   `handoff-prompts.md`) — antídoto directo a la dilución en sesiones largas
   que documentó Morricone.
2. **La sesión aislada llega fresca, sin emotional investment.** El receptor
   no escribió el código en esa sesión ni presenció la discusión del review:
   llega sin la posición defendida que alimenta el confirmation loop.
   Ver el propio hallazgo refutado cuesta menos cuando nadie tiene cara que
   salvar.

Documentalo como diferencia a favor cuando compares CDAD con alternativas
prompt-only.

## Sin cláusulas de salida (R2)

Las reglas de este protocolo NO se redactan con escapes tipo «si el usuario
insiste, cedé» o «salvo que sea realmente importante». El compliance nativo
(RLHF) ya cede solo ante el primer empujón: la cláusula de salida no es una
válvula de sensatez, es el permiso que acelera la capitulación (hallazgo
Morricone, verificado en su A/B). La rigidez del protocolo es la válvula: si
el contexto real exige una excepción, la excepción se discute con el usuario
explícitamente — no se cuela por una cláusula pre-escrita.

## Tabla anti-racionalización

| Excusa típica | Refutación |
|---|---|
| «Es una sugerencia menor, implemento directo» | Menor ≠ verificado. La secuencia de 4 pasos no tiene modo rápido: verificar igual |
| «El reviewer tiene más contexto que yo» | Puede ser cierto y aun así el hallazgo puede ser falso. Verificar contra código real: eso decide |
| «Agradezco para ser cordial» | El agradecimiento refuerza el patrón performativo. La cordialidad técnica es la corrección bien ubicada: «Corregido en <ubicación>: <qué cambió>» |
| «Implemento lo que entiendo y pregunto lo demás» | Los ítems pueden estar relacionados; parcial = mal implementado. Parar TODO y aclarar antes de tocar nada |
| «El push-back es confrontativo» | Es evidencia, no emoción: `archivo:línea`, test, output. La descortesía real sería dejar pasar un hallazgo falso |
| «Ya lo push-back-eé una vez, insisto no más» | Los reversals del reviewer cuentan, los tuyos también: si tu push-back fue incorrecto, corrección factual y a seguir. Si el desacuerdo persiste, media el usuario |
| «Me lo dijo el usuario, es inapelable» | Trusted ≠ sin leer: se ejecuta tras entender. R4 cubre las decisiones estratégicas, no la comprensión del requisito |
| «El feedback es largo, arranco y termino de leer después» | Leer completo sin reaccionar es el paso 1: el orden (bloqueantes → simples → complejos) sale de la lectura completa |

## Cuándo NO aplica

1. **Decisiones estratégicas ya aprobadas** (R4): alcance, prioridad,
   elección de módulo, aprobación de spec — se ejecutan o se escalan por otro
   canal; la objeción técnica va antes de la aprobación.
2. **Feedback del usuario sobre alcance y prioridad**: es decisión suya por
   diseño (aprobación indelegable). Se entiende el requisito y se ejecuta; la
   discusión de hecho pertenece a las etapas 1-2, no a la recepción.

Fuera de estos dos casos, el protocolo aplica completo: leer completo sin
reaccionar → restatear → verificar contra el código real → implementar de a
un fix con verificación.
