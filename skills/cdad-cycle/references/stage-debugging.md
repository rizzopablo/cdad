# Debugging sistemático — protocolo de diagnóstico

> **Fuentes:** obra/superpowers `systematic-debugging/SKILL.md` (ley de hierro,
> 4 fases, regla 3+ fixes → arquitectura, red flags) y sus auxiliares
> `root-cause-tracing.md` (fix en la fuente, no donde aparece el síntoma),
> `condition-based-waiting.md` (polling de condición, nunca sleep arbitrario) y
> `defense-in-depth.md` (validación por capas); adaptación Hermes Agent —
> "The Feedback Loop Rule": adivinar sin loop rojo-capable ES el failure mode;
> arjenschwarz `systematic-debugger` — inspección Fagan modificada + Five Whys
> para bugs stubborn (post-múltiples-fallos); research del epic
> (`docs/epics/research-tema3-debugging/research.md`).
> Notación canónica de búsqueda: `defense.?in.?depth` y
> `condition.?based.?waiting` — los términos matchean con o sin guiones
> ("defense-in-depth", "defense in depth").
>
> **Se invoca cuando:** un GREEN falla en Etapa 3 y hay que diagnosticar antes
> de re-delegar (`stage-3-tdd.md` §3.2), o CI está roto en Etapa 5
> (`stage-5-merge.md` §5.1).

**Principio core:** SIN CAUSA RAÍZ VERIFICADA NO HAY FIX. El síntoma es dato,
no diagnóstico. Un fix que no sale de una causa raíz verificada es una apuesta
disfrazada de corrección — y las apuestas apiladas son thrashing (AP-18).

## El loop rojo ES la sub-fase RED

Esta es la síntesis central del protocolo en CDAD: el debugging no es otra
metodología, es RED con disciplina de diagnóstico. El *tight feedback loop* de
Superpowers/Hermes — un comando que reproduce el bug — **es la sub-fase RED**
de `stage-3-tdd.md` aplicada al bug:

- Un comando **tight**: rápido, determinista, agent-runnable, que va **rojo con
  el síntoma exacto** y verde **solo con el fix**.
- El assert verifica el síntoma observado, no "que no crashea". Un test que
  pasa sin el fix no es un loop rojo: no falsa nada.
- **Antes de leer código para armar teorías, el loop rojo tiene que existir.**
  Adivinar sin loop rojo-capable es EL failure mode del debugging.
- Si el bug es flaky: el primer trabajo es **subir la tasa de repro** — correr
  el test 100 veces, paralelizar, estrechar la ventana de timing. NUNCA sleep
  arbitrario ni "re-intento y veamos": `condition-based-waiting` — polling de
  la condición real (el recurso está, el evento llegó, el estado cambió) en
  lugar de esperar un tiempo inventado.

## Fase 1 — Diagnóstico (recolectar evidencia)

1. **Leer el error completo.** Stack traces enteros, line numbers, primer
   error del output (no el último). Recortar el error es recortar la evidencia.
2. **Armar el loop rojo** (ver arriba). Sin repro no hay diagnóstico: hay
   adivinanza.
3. **Cambios recientes:** `git diff` / `git log` del área afectada. La mayoría
   de los bugs llegó con un commit reciente.
4. **Sistemas multi-componente:** instrumentar cada boundary (qué entra, qué
   sale en cada frontera de servicio/módulo/proceso) **antes** de proponer
   nada. La evidencia en boundaries reemplaza teorías sobre "a qué hora se
   rompe el pipeline".
5. Llevá la evidencia acumulada como registro (qué probaste, qué observaste).
   En la regla 3+, esa evidencia es lo que escala.

## Fase 2 — Minimizar + comparar

- **Repro mínimo (cut-one-thing):** quitá de a un elemento del repro (datos,
  pasos, componentes). El criterio de done: quitar cualquiera de los elementos
  restantes lo pone verde. Cada elemento que sobra en el repro es ruido que
  puede apuntar la hipótesis mal.
- **Comparar contra código que sí funciona** (mismo codebase, mismo mecanismo
  en otro lugar) **listando TODAS las diferencias** — no solo la que ya
  sospechás. La diferencia que no miraste es la que causa el bug.

## Fase 3 — Hipótesis rankeadas

No elijas una teoría y la defiendas: generá **3-5 hipótesis falsables**,
ordenadas por verosimilitud × baratura de falsar. Cada una lleva una
predicción explícita: "si X es la causa, Y debería pasar Z".

- Testeá con la **sonda más chica** (un log, un breakpoint, un assert extra) —
  nunca un cambio grande "para ver si se arregla".
- **UNA variable por vez.** Cambiar dos cosas juntos destruye la información:
  aunque se arregle, no sabés cuál fue, y el otro cambio puede haber
  introducido un bug nuevo.
- **Verificá antes de seguir.** Si la predicción no se cumple, la hipótesis
  está muerta: anotala y pasá a la siguiente, no la retuerzas.
- "No entiendo X" es una respuesta válida y útil — mejor que una teoría
  conveniente no falsada.

## Fase 4 — Fix

- **Un solo fix, sobre la causa raíz** — no sobre el síntoma. Tracing hacia
  atrás por la call chain: el fix va en la **fuente**, no donde aparece el
  síntoma.
- **Sin "while I'm here":** sin fixes empaquetados con refactor ni limpieza de
  al lado. Si el vecino necesita refactor, es otra tarea (y otro ciclo RED).
- **Test de regresión primero.** Si la causa raíz es una postcondición nueva,
  el test de regresión lo escribe el test-writer (RED); si el test que falló
  estaba mal (verificaba otra cosa), el fix es del test. El fix de código entra
  después, y ese test es lo que impide que el bug vuelva.
- **Defense-in-depth DESPUÉS del fix:** validación por capas (borde de datos,
  entrada de módulo, invariantes internos) para que la clase de bug sea
  imposible, no solo ausente. Nunca en lugar del fix de causa raíz.

## Regla del 3+ → STOP → ADR

**3 fixes fallidos o más = STOP.** No intentes el cuarto: el cuarto intento
sobre la misma teoría no es persistencia, es ignorar evidencia.

1. Cuestioná la arquitectura, no tu suerte: 3+ fixes sin resultado es señal de
   que el diseño, no el detalle, está en la causa.
2. **Escala al usuario** con la evidencia acumulada (loop rojo, hipótesis
   testeadas y sus resultados, qué aprendiste en cada fallo).
3. El desenlace es un **ADR** (`docs/adr/`) que decide: bug puntual dentro de
   un diseño razonable, o diseño equivocado → posible vuelta a Descubrimiento
   (la excepción ya existente del ciclo, "spec entero mal → Etapa 1").
4. Cada fix que arregla acá pero rompe allá **ES la señal**: el problema nuevo
   en otro lugar es el dato de que el corte de responsabilidades está mal.

## Roles en el ciclo CDAD

- **Diagnóstico = implementer.** Lee la suite y el código (puede leer tests),
  pero NO toca `tests/` (AP-4 sigue aplicando). El loop rojo puede ser el test
  rojo existente o un comando de repro desechable fuera de `tests/`.
- **Test de regresión = test-writer.** Si la causa raíz implica postcondición
  nueva, el test entra por RED (test-writer); el implementer no lo escribe.
- **Bugs stubborn (3+ fallos ya acumulados):** inspección **Fagan** modificada
  (clarificar el problema → lectura línea a línea del código involucrado SIN
  arreglar nada en el recorrido) + **Five Whys** (3-5 whys, escribiendo los
  supuestos de cada salto) como técnica de las fases 1-2. Se disparan CUANDO
  ya hubo 3+ fallos, no antes.

## Tabla anti-racionalización

| Excusa típica | Refutación |
|---|---|
| «Es simple, lo arreglo directo» | Simple ≠ diagnosticado. Sin causa raíz verificada no hay fix — ni para bugs "obvios" |
| «Solo pruebo un cambio y veo» | Probar sin loop rojo es adivinar con steps extra. Primero el comando que va rojo con el síntoma exacto |
| «Corro 2 cambios juntos para ir más rápido» | Dos variables a la vez destruyen la información: si se arregla, no sabés cuál fue; y una puede introducir un bug nuevo. UNA por vez |
| «Ya intenté 3, uno más no molesta» | 3+ es STOP, no "otra ronda": escala al usuario con evidencia y ADR. El cuarto intento quema contexto y confianza |
| «Es flaky, re-intento» | Re-intentar es rezar. Subí la tasa de repro (correr 100x, paralelizar, estrechar ventana) y usá condition-based-waiting, nunca sleep arbitrario |
| «No hay repro, voy por intuición» | Sin loop rojo no hay teoría que valga: toda teoría sin repro es infalsable. Invertí primero en reproducir |
| «Aprovecho y refactorizo lo de al lado» | While-I'm-here apila un cambio de diseño encima de un fix sin diagnóstico: si algo rompe, no sabés qué. El fix es único y enfocado |
| «El ADR es burocracia, pruebo otro fix» | El ADR es el único registro de por qué el cuarto fix también fallaría. Sin ADR, el próximo ciclo vuelve a empezar de cero |

## Cuándo NO aplica

1. **Infra pura documentada:** caída de proveedor externo, cuota agotada,
   incidente de plataforma — no es código que arreglar: escalar al usuario +
   monitoreo, y esperar al proveedor. El protocolo no fabrica fixes de código
   para problemas que no son de código.
2. **Flaky crónico con plan de monitoreo explícito y deuda registrada:** si la
   inestabilidad ya está documentada como deuda con plan de monitoreo y quota
   acordada con el usuario, no se re-diagnostica en cada sesión — se consulta
   el plan.

Fuera de estos dos casos, el protocolo aplica completo: loop rojo primero →
diagnóstico → minimizar + comparar → hipótesis rankeadas → fix único sobre
causa raíz.
