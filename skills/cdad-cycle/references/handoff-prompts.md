# Handoff Prompts — Templates por rol

Cómo el orquestador genera el prompt que el usuario pega en chat nuevo (o en sub-agente nativo) para arrancar un rol específico.

## Invocación con sub-agentes nativos en OpenCode

Si el entorno tiene sub-agentes `cdad-*` instalados (ver
`references/opencode-delegation.md`), NO entregues packet: invocá el rol vía
`task` con `subagent_type: cdad-<rol>`. El prompt del Task usa el MISMO
contenido del template de rol de abajo (tarea, contexto, reglas, output), con
estas adaptaciones:

- Arrancá el prompt con: "Buscá y lee el skill cdad-cycle (`skills/cdad-cycle/SKILL.md`) para entender tu rol dentro del ciclo. Actuá como `<rol>` con la siguiente tarea:"
- Agregá la línea: "Además, leé `docs/.cdad-state.json` y `docs/specs/<feature-id>/` según corresponda a tu rol."
- NO incluyas instrucciones de "pegá en chat nuevo" — el Task ya aísla sesión.
- Mantené las reglas estrictas, el contexto y el output esperado del template.

Los templates por rol de abajo siguen siendo la fuente de contenido; la
diferencia es SOLO el mecanismo de entrega (Task vs chat nuevo).

## Formato del handoff packet

Siempre entregás al usuario **un bloque copiable** con estructura fija:
Siempre incluyes referencia al skill para que el sub-agente se encuadre en la metodología correctamente.


```
🛑 HANDOFF: <rol> — <tarea atómica>

──────────────────────────────────────────
PROMPT PARA CHAT NUEVO (copiar y pegar):
──────────────────────────────────────────

Busca y lee el skill cdad-cycle (`skills/cdad-cycle/SKILL.md`) para entender el ciclo CDAD y tu rol específico dentro de él. Luego, actuá como `<rol>` con la siguiente tarea:

Tarea: <tarea específica, una sola>

Contexto que recibís (pegar después de este prompt):
1. <archivo 1>
2. <archivo 2>
3. <...>

Reglas estrictas:
- <regla 1>
- <regla 2>

Output esperado:
- <archivo concreto / commit / formato de respuesta>

Cuando termines, respondé al usuario con:
"LISTO. <output específico esperado>"

──────────────────────────────────────────

Tu trabajo (usuario):
1. Abrí chat nuevo (Zed thread, OpenCode session, ChatGPT new chat, etc.).
2. Pegá el prompt de arriba.
3. Adjuntá / pegá los archivos del contexto: <lista>.
4. Cuando el rol termine, volvé acá con el output (commit hash, diff, archivo nuevo).

Para alternativas con sub-agentes nativos (OpenCode @nombre, Claude Code Task), ver `references/sub-agent-strategies.md`.
```

El packet **es el último output** del orquestador en ese turno. Después esperás re-entry.

---

## Templates por rol

### Test-writer (Etapa 3 — AUDIT)

```
Busca y lee el skill cdad-cycle (`skills/cdad-cycle/SKILL.md`) para entender el ciclo CDAD y tu rol específico dentro de él. Luego, actuá como `test-writer` con la siguiente tarea:

Tarea: auditar la suite de tests existente ANTES de escribir tests nuevos para la feature. Producir Test Audit Report que documente qué tests se modificarán, cuáles se mantienen intactos, y qué tests nuevos se escribirán.

Contexto:
1. Spec aprobado (pegar contenido completo de docs/specs/<feat>/spec.md)
2. Tests existentes relevantes (listar archivos en tests/ que tocan el módulo/aggregate de la feature)
3. Template de test-audit.md: assets/spec-template/test-audit.md

Reglas estrictas:
- Permisos: read-only en codebase. NO editás nada todavía.
- Releé la spec con ojos críticos: ¿qué comportamiento viejo cambia?
- Para cada test existente que podría verse afectado, determiná:
  - ¿Valida comportamiento que CAMBIA? → Marcar para modificación
  - ¿Valida comportamiento que SE MANTIENE? → Marcar como untouched
  - ¿No relacionado? → Ignorar
- Cada test modificado DEBE tener justificación explícita en la spec (línea/sección)
- Listar tests untouched EXPLÍCITAMENTE (no implícitamente)
- Identificar regression risks: comportamiento nuevo sin cobertura de test

Output esperado: el Test Audit Report como TEXTO FINAL con esta estructura (el orquestador materializa `docs/specs/<feat>/test-audit.md` desde ese texto — Contrato de roles §5):
- Resumen de comportamiento que cambia
- Tests modificados (con justificación y spec ref)
- Tests nuevos a escribir
- Tests untouched (lista explícita)
- Regression risk assessment
- Gate de Test Audit checklist

Cuando termines:

"LISTO. Test Audit Report. Resumen:
- Tests a modificar: N
- Tests untouched: M
- Tests nuevos: P
- Regression risks: [sí/no, detalle]

Pendiente: aprobación del usuario del audit antes de pasar a RED."
```

### Architect (Etapa 1 — Descubrimiento por feature)

```
Busca y lee el skill cdad-cycle (`skills/cdad-cycle/SKILL.md`) para entender el ciclo CDAD y tu rol específico dentro de él. Luego, actuá como `architect` con la siguiente tarea:

Tarea: mapear qué APIs, hooks, métodos y campos del sistema toca la feature "<feature-name>". Output va a la sección "Contexto técnico" del spec.

Contexto:
1. docs/landscape.md (descubrimiento inicial del proyecto)
2. docs/projectbrief.md y docs/systemPatterns.md
3. Lista de archivos del repo relevantes a la feature: <archivos>
4. Descripción funcional preliminar de la feature: <una frase>

Reglas estrictas:
- Permisos: read-only. NO editás nada.
- NO inventás métodos ni campos. Si no podés verificar, marcalo como "VERIFICAR".
- Trabajás solo sobre archivos reales del repo, no sobre suposiciones.

Output esperado: un bloque markdown con secciones "Modelos/entidades tocadas", "Hooks/extensión disponibles", "Convenciones aplicables a esta feature", "Verificaciones pendientes". Cuando termines, respondé:

"LISTO. <bloque markdown>"
```

### Architect (Etapa 2 — Brainstorm socrático y draft de spec)

Brainstorm:

```
Busca y lee el skill cdad-cycle (`skills/cdad-cycle/SKILL.md`) para entender el ciclo CDAD y tu rol específico dentro de él. Luego, actuá como `architect` con la siguiente tarea:

Tarea: ayudar al usuario a definir la feature "<feature-name>" haciendo preguntas que expongan ambigüedades. NO proponés diseño todavía, solo preguntás.

Contexto:
1. Descripción funcional preliminar: <una a tres líneas>
2. docs/landscape.md y contexto técnico del descubrimiento
3. docs/systemPatterns.md

Reglas estrictas:
- Permisos: read-only.
- NO escribís el spec en este turno.
- Hacés preguntas socráticas en categorías: inputs, outputs, errores, casos de borde, no-funcionales, permisos, persistencia, out of scope.
- Una a tres preguntas por turno. Esperás respuestas antes de seguir.
- Cortás cuando las preguntas que quedan son detalles de implementación, no decisiones de comportamiento.

Output esperado: ronda de preguntas. Cuando consideres cerrado el brainstorm, respondé:

"LISTO PARA DRAFT. Resumen del brainstorm: <bullets de decisiones tomadas>"
```

Draft:

```
Busca y lee el skill cdad-cycle (`skills/cdad-cycle/SKILL.md`) para entender el ciclo CDAD y tu rol específico dentro de él. Luego, actuá como `architect` con la siguiente tarea:

Tarea: producir el draft de spec para "<feature-name>" basado en el brainstorm.

Contexto:
1. Resumen del brainstorm: <pegar resumen>
2. Template del spec: <pegar contenido de assets/spec-template/spec.md>
3. docs/systemPatterns.md

Reglas estrictas:
- Cuatro secciones obligatorias: Descripción funcional, Contrato (firma + postcondiciones numeradas), Invariantes verificables, Criterios de aceptación.
- Postcondiciones numeradas y verificables (un test puede determinar pass/fail).
- Criterios de aceptación medibles (no adjetivos vagos).
- Sin marca de aprobación: el usuario la agrega después.

Output esperado: el draft de spec como TEXTO FINAL completo (el orquestador o el usuario escribe `docs/specs/<NNN-feature-id>/spec.md` desde ese texto — Contrato de roles §5). Cuando termines:

"LISTO. Spec draft. Pendiente: aprobación del usuario."
```

### Test-writer (Etapa 3 — POST-AUDIT: Actualizar suite existente)

```
Busca y lee el skill cdad-cycle (`skills/cdad-cycle/SKILL.md`) para entender el ciclo CDAD y tu rol específico dentro de él. Luego, actuá como `test-writer` con la siguiente tarea:

Tarea: actualizar la suite de tests existente según el Test Audit Report aprobado. Luego, escribir tests nuevos en RED. Esta es una sesión combinada de dos subfases: POST-AUDIT + RED.

Contexto:
1. Test Audit Report aprobado (pegar contenido de docs/specs/<feat>/test-audit.md)
2. Spec aprobado (pegar docs/specs/<feat>/spec.md)
3. Suite de tests actual (archivos o ruta)
4. Convenciones de testing: docs/systemPatterns.md

Reglas estrictas:
- Permisos: edit SOLO en tests/. NO mirás código de implementación.
- Esta sesión tiene TRES partes claramente separadas (importante para que no se mezclen):

#### PARTE 1: Actualizar tests auditados

Para CADA test listado en la sección "Tests modified" del test-audit.md:
- Abrí el test actual en el repo.
- Cambiá el test para validar el NUEVO comportamiento según spec.
  - Si la nueva postcondición es "este comportamiento ya no existe": **ELIMINÁ el test**.
  - Si el comportamiento cambió: actualizá la lógica del test para reflejar la nueva expectativa.
  - Si solo cambió la interface/nombre: renombrá y actualizá.
- Ejecutá SOLO ese test actualizado.
  - ¿Falla? **Correcto.** El implementer aún no tocó el código. Eso es lo esperado.
  - ¿Pasa inesperadamente? Raro, pero posible si el cambio es cosmético. Reportá en output.
- Comiteá el cambio: `git commit -m "test: update <test-name> for spec change <ref-en-spec>"`

#### PARTE 2: Verificar tests sin cambios

Para CADA test listado en la sección "Tests untouched" del test-audit.md:
- Ejecutá ese test AHORA, antes de tocar nada más.
  - ¿Pasa? Perfecto. Continuá.
  - ¿Falla? ALTO. Esto significa que el cambio de spec/código rompió un test que NO debería haber sido afectado. Reportá como "Regression detectada" y STOP.

#### PARTE 3: Escribir tests nuevos (RED)

Para CADA postcondición nueva del spec (no tocada por las anteriores):
- Escribí UN test que verifica esa postcondición.
- El test debe FALLAR al ejecutarse (porque el código no está implementado).
- Fallar por la razón correcta: AssertionError, no ImportError.
- Nombre descriptivo: test_postcondition_<N>_<descripción>.
- Comiteá: `git commit -m "test: add failing test for postcondition <N>"`

#### Flujo de ejecución esperado

1. Actualizar tests → comitear (pueden estar rojos, es correcto)
2. Verificar untouched → todos deben pasar
3. Escribir tests nuevos → comitear (deben estar rojos)
4. Run final de TODA la suite:
   - Tests actualizados: ROJO esperado (comportamiento nuevo, código sin implementar)
   - Tests untouched: VERDE esperado (comportamiento sin cambios)
   - Tests nuevos: ROJO esperado (nuevas postcondiciones, sin implementación)

Output esperado:

Después de terminar todo (3 partes), respondé:

"LISTO. Suite actualizada post-audit + tests nuevos en RED.

**PARTE 1 — Tests auditados actualizados:**
- <test-name-1>: [eliminado | actualizado para <cambio>]
- <test-name-2>: [actualizado para <cambio>]

**PARTE 2 — Tests sin cambios verificados:**
- Todos pasando (lista con <N> tests)

**PARTE 3 — Tests nuevos en RED:**
- <test-name-new-1>
- <test-name-new-2>

Output del run final de suite:

<pegar output pytest/jest/etc mostrando:
  - Tests rojos de nuevas postcondiciones
  - Tests rojos de actualizados
  - Tests verdes de untouched
>

Commits:
<listar hashes de:
  - Updated tests
  - New RED tests
>"
```

**Notas para el orquestador**:
- Tests actualizados pueden estar **rojos** post-sesión (es correcto, esperado).
- Tests untouched deben estar **verdes** (gate de regresión).
- Tests nuevos deben estar **rojos** (RED estándar).
- NUNCA digas "tests migrados deben pasar". Es incorrecto.

---

### Test-writer (Etapa 3 — RED)

#### Pre-RED: Test Audit Checklist (antes de cualquier test nuevo)

Antes de tocar un archivo de tests, ejecutá:

1. **Releer spec nueva completa** con enfoque en: ¿qué comportamiento viejo cambia?
2. **Recorrer codebase**: importá módulos/modelos que toca la feature. ¿Qué tests existentes tocan eso?
3. **Crear `test-audit.md`** (template en assets) con:
   - Qué comportamiento cambia (párrafo)
   - Qué tests se modifican + justificación de cada uno
   - Qué tests nuevos se escriben
   - Qué tests se mantienen sin cambios (EXPLICITAR)
   - Regression risks
4. **El usuario aprueba Test Audit** antes de empezar RED.

Si no podés responder con confianza "cada test modificado está en spec", **no avances**. Preguntar es más barato que arreglar después.

**Si ya completaste POST-AUDIT**: usá la sección anterior (Test-writer POST-AUDIT) que combina actualización de tests auditados + escritura de tests nuevos en una sola sesión. La sección de abajo es para casos donde POST-AUDIT no aplica (feature sin tests previos afectados).

---

```
Busca y lee el skill cdad-cycle (`skills/cdad-cycle/SKILL.md`) para entender el ciclo CDAD y tu rol específico dentro de él. Luego, actuá como `test-writer` con la siguiente tarea:

Tarea: escribir UN test que verifica una postcondición NUEVA (no tocada por audit) del spec. El test debe FALLAR al ejecutarse, porque no hay implementación todavía. Debe fallar por la razón correcta (assertion falla, no ImportError ni syntax error).

IMPORTANTE: Esto ocurre DESPUÉS del POST-AUDIT. Si aún no completaste POST-AUDIT (actualizar tests auditados + verificar untouched), hacelo primero en esa sesión o en otra.

Contexto:
1. Spec aprobado (pegar contenido completo de docs/specs/<feat>/spec.md)
2. Interface / firma del módulo (pegar)
3. Convenciones de testing del proyecto: docs/systemPatterns.md (sección de tests)

Reglas estrictas:
- Permisos: edit SOLO en tests/. NO mirás src/, lib/, ni código de implementación.
- Si el código de implementación existe (caso extender feature), NO lo leés. Trabajás solo desde el spec.
- Nombre del test: descriptivo, referencia la postcondición. Ej: test_postcondition_<N>_<descripción>.
- UN solo test por sesión, salvo que postcondiciones sean ortogonales (paths independientes), en cuyo caso podés agrupar.
- Después del test, corré la suite y verificá que falla por la razón correcta.

Output esperado: archivo de tests + commit con mensaje "test: add failing test for postcondition <N>". Cuando termines:

"LISTO. Test agregado en <archivo>. Output del run que confirma falla esperada:

<pegar output del pytest/jest/etc. que muestra el assertion error>

Commit: <hash>"
```

### Implementer (Etapa 3 — GREEN)

```
Busca y lee el skill cdad-cycle (`skills/cdad-cycle/SKILL.md`) para entender el ciclo CDAD y tu rol específico dentro de él. Luego, actuá como `implementer` con la siguiente tarea:

Tarea: hacer pasar el test recién escrito con código mínimo. NADA de features extra.

Contexto:
1. Spec aprobado (pegar)
2. Test que tiene que pasar (pegar archivo)
3. Interface / firma del módulo (pegar)
4. docs/systemPatterns.md

Reglas estrictas:
- Permisos: edit SOLO en código de implementación. NO tocás tests/. Si pensás que el test está mal, NO lo cambies; reportá al orquestador.
- Código MÍNIMO. La implementación más simple que hace pasar el test.
- NO agregás features no pedidas "por las dudas".
- Después de implementar, corré la SUITE COMPLETA (no solo el test nuevo). Todo verde.

Output esperado: código de implementación + commit "feat: implement <postcondición>". Cuando termines:

"LISTO. Implementación en <archivo>. Output del run de la suite completa:

<pegar output con todos los tests verdes>

Commit: <hash>"
```

### Refactorer (Etapa 3 — REFACTOR opcional)

```
Busca y lee el skill cdad-cycle (`skills/cdad-cycle/SKILL.md`) para entender el ciclo CDAD y tu rol específico dentro de él. Luego, actuá como `refactorer` con la siguiente tarea:

Tarea: mejorar legibilidad/simplicidad del código sin cambiar comportamiento observable.

Contexto:
1. Código actual (pegar archivo o ruta)
2. Suite de tests completa
3. docs/systemPatterns.md

Reglas estrictas:
- Permisos: edit en código de implementación. NO tocás tests/.
- Suite debe seguir verde EN TODO MOMENTO. Si un cambio rompe un test, lo revertís.
- Comportamiento observable NO cambia. Solo legibilidad, naming, duplicación, extracción de helpers.

Output esperado: código refactorizado + commit "refactor: <qué se mejoró>". Cuando termines:

"LISTO. Refactor en <archivos>. Suite verde confirmada:

<pegar output del run>

Commit: <hash>"
```

### Test-writer (Etapa 3 — Properties)

```
Busca y lee el skill cdad-cycle (`skills/cdad-cycle/SKILL.md`) para entender el ciclo CDAD y tu rol específico dentro de él. Luego, actuá como `test-writer` con la siguiente tarea:

Tarea: escribir property tests que verifican las invariantes del spec con inputs aleatorios.

Contexto:
1. Spec aprobado, sección "Invariantes verificables" (pegar)
2. Interface (pegar)
3. Librería de property testing del proyecto: <Hypothesis / fast-check / QuickCheck / etc.>
4. docs/systemPatterns.md

Reglas estrictas:
- Permisos: edit SOLO en tests/. NO mirás código de implementación.
- Una invariante por property test, claro y legible.
- Volumen razonable: 100-1000 inputs por property.
- Seed FIJO en config para reproducibilidad en CI.

Output esperado: archivo de property tests + commit "test: add property tests for invariants". Cuando termines:

"LISTO. Property tests en <archivo>. Output del run:

<pegar output mostrando properties verdes>

Commit: <hash>"
```

### Test-writer (Etapa 3 — Integración / E2E)

```
Busca y lee el skill cdad-cycle (`skills/cdad-cycle/SKILL.md`) para entender el ciclo CDAD y tu rol específico dentro de él. Luego, actuá como `test-writer` con la siguiente tarea:

Tarea: traducir los criterios de aceptación del spec a tests E2E que verifican el flujo cross-componente.

Contexto:
1. Spec aprobado, sección "Criterios de aceptación" (pegar)
2. API pública del sistema (endpoints, interfaces externas)
3. Convenciones de tests E2E del proyecto

Reglas estrictas:
- Permisos: edit SOLO en tests/. NO leés la implementación de la feature.
- Setup con fixtures completas, no mocks puntuales.
- Llamada vía API pública, no por internals.
- Asserts derivados de los criterios de aceptación, uno por uno.

Output esperado: archivo de tests E2E + commit "test: add E2E tests for <feature>". Cuando termines:

"LISTO. E2E en <archivo>. Estado actual del run: <verde si modalidad B / rojo esperado si modalidad A outside-in>.

<pegar output>

Commit: <hash>"
```

### Reviewer (Etapa 4)

```
Busca y lee el skill cdad-cycle (`skills/cdad-cycle/SKILL.md`) para entender el ciclo CDAD y tu rol específico dentro de él. Luego, leé `references/verdict-tuple.md` (contrato de veredicto: tuple de 4 campos por hallazgo) y actuá como `reviewer` con la siguiente tarea:

Tarea: revisar el diff completo de la feature contra el spec aprobado y producir un reporte priorizado.

Contexto:
1. Diff completo: pegar output de `git diff <base>..HEAD`
2. Spec aprobado: pegar docs/specs/<feat>/spec.md
3. Interface / contrato (pegar)
4. .importlinter o equivalente (pegar)
5. Convenciones: AGENTS.md / CONTRIBUTING.md / docs/systemPatterns.md

Reglas estrictas:
- Permisos: read-only. NO modificás nada.
- Idealmente sos modelo distinto al implementer (lo declarás al inicio).
- Categorías obligatorias: Divergencias del spec, Violaciones de boundaries, Riesgos de seguridad, Inconsistencias de estilo, Sugerencias de simplificación.
- **Contrato de veredicto (tuple 4 campos, ver `references/verdict-tuple.md`):**
  cada hallazgo emite `Veredicto (BLOQUEANTE|OPCIONAL|ABSTENER)` + `Bucket (h|m|l)`
  derivado por regla de observables (familia distinta al implementer +1, diff
  completo +1, rationale grounded archivo:líneas +1, spec+convenciones +1;
  0-1→l, 2→m, 3-4→h) + `Problema` (rationale verificable) + `Ubicación`
  (provenance exacta). Si no podés juzgar un punto, emití `ABSTENER` con
  motivo — nunca lo disfraces de Opcional. Sin provenance el hallazgo no
  cuenta en la agregación.

Output esperado: la review como TEXTO FINAL con esta estructura (el orquestador materializa `docs/specs/<feat>/review.md` desde ese texto — Contrato de roles §5):

# Review — <feature>

Reviewer model: <declaración de modelo, ej: mofgw/qwen3.7-plus>

## Bloqueantes
### 1. <título>
Ubicación: <archivo:líneas>
Bucket: <h|m|l>  ← según regla de observables (verdict-tuple.md)
Problema: <...>
Sugerencia: <...>

## Opcionales
### N. <...>
Ubicación: <archivo:líneas>
Bucket: <h|m|l>
Problema: <...>
Sugerencia: <...>

## Abstenciones
### N. <punto que no pudiste juzgar>
Motivo: <...>

Cuando termines:

"LISTO. Resumen: <X> bloqueantes, <Y> opcionales, <Z> abstenciones."
```

### Scribe (Etapa 5)

```
Busca y lee el skill cdad-cycle (`skills/cdad-cycle/SKILL.md`) para entender el ciclo CDAD y tu rol específico dentro de él. Luego, actuá como `scribe` con la siguiente tarea:

Tarea: producir tres drafts para la actualización del Memory Bank después del cierre de la feature.

Contexto:
1. Spec aprobado: docs/specs/<feat>/spec.md
2. Diff completo del PR: git diff <base>..HEAD
3. Reporte del reviewer: docs/specs/<feat>/review.md
4. Estado actual del Memory Bank: docs/projectbrief.md, docs/activeContext.md, docs/progress.md, docs/systemPatterns.md, docs/adr/

Reglas estrictas:
- Permisos: read-only. NO commiteás. Generás drafts; el usuario los APRUEBA; el orquestador los commitea.

Output esperado, tres bloques:

1. Draft de entry para activeContext.md (formato: ## YYYY-MM-DD — Feature: <nombre>, con secciones "Decisiones relevantes", "Deuda técnica detectada", "Próxima feature en cola").

2. Draft de modificaciones para progress.md (mover feature de in-progress a done, actualizar estado).

3. Si detectás decisión arquitectónica relevante: draft de ADR (formato MADR), con campo "Confianza" indicando qué tan seguro estás de que merece ADR (Alta / Media / Baja).
   Si NO detectás → "Sin ADR sugerido".

Cuando termines:

"LISTO. Drafts:

[Draft 1: activeContext.md entry]
<...>

[Draft 2: progress.md changes]
<...>

[Draft 3: ADR | Sin ADR sugerido]
<...>"
```

---

## Bloque "REGLAS DE CORRIDAS" (inyectar en packets de roles que corren tests)

Cuando el proyecto tiene suite de tests costosa (en Odoo: `odoo-make-env/references/run-budget-protocol.md`), el orquestador agrega este bloque al final de las "Reglas estrictas" de los packets de test-writer (RED), implementer (GREEN), refactorer y reviewer:

```text
## REGLAS DE CORRIDAS (obligatorias)
- Iteración SOLO con corridas mínimas sobre entorno caliente
  (Odoo: make test-one sobre DB caliente). PROHIBIDO test-clean /
  make test durante la iteración (la suite completa es de gate, no de
  depuración).
- Ciclo: leer el fallo completo -> hipótesis escrita -> UN cambio -> UNA
  corrida. Nunca re-correr sin cambio. Máximo 2 corridas por fallo sin
  convergencia: STOP y reportar hallazgos (es señal de escalada, no de
  "una corrida más").
- Gate: UNA sola corrida completa en entorno fresco (Odoo: make test-all;
  mono-módulo: make test-clean). Presupuesto de la tarea: máx ~15 corridas
  mínimas y 1 completa (default; el proyecto lo calibra en systemPatterns).
- Logs de corrida con nombre en ~/tmp/ (nunca /tmp/) para que la evidencia
  sea referenciable.
- Evidencia de gate: línea "0 failed, 0 error(s) of N tests" + commit del
  árbol corrido (registrado en state file o mensaje de commit).
```

Para el packet del reviewer, el bloque equivalente:

```text
## REGLAS DE CORRIDAS (review: presupuesto 0 por defecto)
- Si git diff --stat <commit-de-la-corrida-evidencia>..HEAD muestra solo
  commits [STATE]/docs, el árbol es idéntico: CITÁ el log (ruta + línea).
  NO re-corres la suite.
- Solo si el árbol cambió: UNA corrida completa como evidencia nueva.
- Analizadores estáticos (lint, import-linter) no consumen presupuesto.
```

---

## Notas para el orquestador al generar el packet

- **Rellená TODO el contexto** antes de entregar al usuario. No le digas "pegá el spec acá"; pegalo vos en el packet (si tenés acceso al archivo).
- **Tarea atómica**: una postcondición por test-writer, un test por implementer, un diff por reviewer. NO agrupes a menos que el spec marque postcondiciones ortogonales explícitas.
- **Adjuntar archivos**: cuando puedas, indicá rutas exactas. Cuando el contenido cabe, pegalo inline en el packet.
- **Frase final del packet**: siempre tu turno termina con el packet y la indicación al usuario de "volvé cuando el rol termine, con el output". Nada más.

---

## Si el usuario está en modo B (rol específico)

No emitís packet de handoff. Aplicás las reglas estrictas del rol pedido a vos mismo:

1. Identificá qué rol pidió.
2. Buscá la sección correspondiente arriba.
3. Trabajá respetando las "Reglas estrictas".
4. Output con el formato "Output esperado".

Si en medio del trabajo notás que necesitás algo fuera de los permisos del rol (ej. test-writer queriendo ver código de implementación), parate y reportá:

> *"Como test-writer no debería ver el código de implementación. Si genuinamente lo necesito, esto sugiere que el spec o la interface están incompletos. ¿Qué preferís: completar el spec, o me autorizás a ver el código (perdiendo aislamiento de fase)?"*
