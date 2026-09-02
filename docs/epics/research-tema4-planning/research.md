# Tema 4: Planning granular spec→TDD — investigación (02 Sep 2026)

## Fuentes revisadas

| Fuente | Qué aporta |
|---|---|
| obra/superpowers `writing-plans/SKILL.md` (171 líneas, leído completo; 4 mirrors idénticos — onei, skillrepo, openai/plugins, ericgandrade) | Task right-sizing ("la unidad más chica con su propio ciclo de test que vale un gate de reviewer fresco; fold setup/config en la tarea que los necesita; split solo donde un reviewer podría rechazar una y aprobar la vecina"), Consumes/Produces con firmas exactas (el implementer de una tarea solo ve su tarea), No Placeholders (lista explícita de frases prohibidas = fallas del PLAN), auto-revisión (cobertura del spec / escaneo placeholders / consistencia de firmas), Global Constraints verbatim del spec |
| **existential-birds/beagle `write-plan`** — la más valiosa | **"Tests are the contract; impls are the contract's satisfaction"**: en el plan NO se escribe código de implementación especulativo (el planner adivina con firmas/vecindad que el executor verá y él no — "writing the impl twice reverses TDD"); en su lugar: files touched + **behavior contract de 3-5 bullets observables** + referencia al análogo existente (la especificidad es el DELTA respecto al análogo, no el estado completo). Paralelo: >5 bullets = re-derivar la implementación en markdown. **Parallel-implementation gate**: si el plan agrega un 2º backend detrás de una interfaz, debe haber task final que corra la suite canónica contra AMBAS y afirme comportamiento idéntico |
| beagle hard gate | Plan sin spec = planes que hornean supuestos no examinados — el plan planifica CONTRA el spec, nunca lo re-inventa |

## Lo que CDAD YA tiene (verificado)

- `stage-2-specification.md:90`: "Compleja: dividir en spec.md, plan.md, tasks.md" — una línea, sin metodología.
- `cdad-epic/SKILL.md`: planning light deliberado a nivel epic (sin descomposición exhaustiva — distinto nivel, no duplica).
- `agents/cdad-architect.md`: scope = brainstorm socrático + draft de spec (no planifica).
- Regla §6 state-passing (handoff autocontenido) — el plan será su fuente natural.
- Aislamiento test-writer (no ve código de implementación).

## Gap real

Sin criterio de tamaño de tarea, sin contrato de interfaz entre tareas, sin
regla anti-placeholder, sin auto-revisión — y con un riesgo propio de CDAD:
un bloque "firmas exactas" sin cuidado filtraría implementación al
test-writer.

## Propuesta adaptada (síntesis CDAD)

**Extensión de `stage-2-specification.md`** (sección nueva "Planning de
features complejas" reemplazando la línea 90) + extensión del rol architect:

1. **Disparador**: spec complejo (múltiples componentes) → el architect
   produce `plan.md` (además del spec) antes de cerrar Etapa 2; el gate
   2→3 incluye plan aprobado si existe.
2. **Tamaño de tarea CDAD**: la unidad más chica que cierra en su propio
   mini-ciclo TDD (RED→GREEN propio) y que un reviewer podría rechazar sin
   rechazar la vecina. Setup/scaffolding se pliega en la tarea que los
   necesita.
3. **Estructura de tarea**: Files (paths exactos) + **Consumes/Produces**
   (contrato público, firmas exactas — apto para test-writer) + pasos TDD.
4. **La síntesis beagle/CDAD**: el plan define el CONTRATO (tests con
   aserciones reales, comandos exactos, mensajes de commit) y el
   **comportamiento observable** (3-5 bullets verificables contra el test),
   NO el código de implementación ("escribir la impl dos veces revierte
   TDD"). El implementer ve: comportamiento + referencia al análogo. Esto
   resuelve la tensión del aislamiento: el plan entero puede verlo el
   test-writer porque no contiene implementación especulativa.
5. **No placeholders**: lista de frases prohibidas (TBD/TODO/"manejar edge
   cases"/"similar a la Tarea N") = falla del plan; y la variante beagle:
   la vagueza con contrato NO es placeholder (el patrón prohibido es vagueza
   sin contrato).
6. **Auto-revisión** del architect: cobertura del spec (cada postcondición →
   ≥1 tarea), escaneo de placeholders, consistencia de firmas entre tareas
   (clearLayers vs clearFullLayers).
7. **AP-19 — Plan placeholder**: plan con tareas que no cierran en un ciclo
   TDD propio o con frases prohibidas.
8. Global constraints del spec copiadas verbatim en el header del plan.

**Formato: cycle light** (cdad-008; toca stage-2-specification.md +
cdad-architect.md + quizá SKILL.md/handoff-prompts mínimo).
