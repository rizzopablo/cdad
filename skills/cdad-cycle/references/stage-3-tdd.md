# Etapa 3 — TDD anti-trampa con sesiones aisladas

La etapa más larga y donde la disciplina importa más. La trampa principal: que un solo agente escriba test e implementación en la misma sesión. Eso colapsa el oráculo independiente.

## Sub-fases

| Sub-fase | Nombre | Quién actúa | Output |
|----------|--------|-------------|--------|
| 3.1 | RED | test-writer (sesión aislada) | Test que falla por la razón correcta |
| 3.2 | GREEN | implementer (sesión aislada) | Código mínimo que hace pasar el test |
| 3.3 | REFACTOR | refactorer (opcional) | Código más limpio, suite verde |
| 3.4 | PROPERTIES | test-writer | Property tests para invariantes |
| 3.5 | INTEGRATION/E2E | test-writer | Tests de flujo cross-componente |

Las cinco no siempre aplican. RED-GREEN es obligatorio. REFACTOR cuando aporta. PROPERTIES si el spec marca invariantes. INTEGRATION/E2E si los criterios de aceptación lo piden.

## Estrategia de aislamiento

**Antes de empezar la etapa, decidí cómo materializar las sesiones aisladas** según tu entorno. Cargá `references/sub-agent-strategies.md` y aplicá la estrategia correspondiente.

Resumen rápido:

- **Sub-agentes nativos** (OpenCode, Claude Code, Zed Agent Panel): usá sub-agentes con permisos por glob. `test-writer` solo edita `tests/`, `implementer` solo edita código de implementación.
- **Single-session** (chat común, fallback): el LLM cambia de "modo" explícitamente entre fases, y para fases sucesivas el usuario puede abrir un chat nuevo pegando solo el contexto requerido.

## Sub-fase 3.1 — RED

### Setup

Apertura de sesión `test-writer`. Le pasás:

- El spec aprobado (`docs/specs/<feat>/spec.md`).
- La interface o firma del módulo (lo que el spec define como contrato).
- Las convenciones de testing del proyecto (`docs/systemPatterns.md`).

**No le pasás el código de implementación**. Si el código aún no existe, perfecto. Si existe (caso de extender feature), aislarlo del contexto del test-writer.

### Tarea del test-writer

Escribir un test que verifique **una postcondición específica** del spec. La postcondición se elige así:

- Empezá por la primera postcondición que el spec marca como base.
- Si hay postcondiciones **ortogonales** (paths de código independientes que no se pisan), agruplas en un mismo ciclo RED-GREEN-REFACTOR para acelerar. Si están acopladas, una por ciclo.

El test debe:

1. **Tener un nombre claro** que describe qué postcondición verifica: `test_postcondition_3_invalid_input_raises_error`.
2. **Fallar** al ejecutarse, porque no hay implementación.
3. **Fallar por la razón correcta**: el assertion falla, no porque el módulo no existe ni porque hay un syntax error.

### Verificación de "falla por razón correcta"

Si tenés bash, corré el test y leé el error. Si no, pedile al usuario:

> *"Corré el test y pegame el error que da. Tiene que ser un AssertionError o equivalente, no un ImportError ni un syntax error. Si es ImportError, el test está incompleto y volvemos al test-writer."*

Si el test falla por motivo equivocado, **no avances**: volvé al test-writer para corregir.

### Cierre de la sub-fase RED

Commit con mensaje del estilo `test: add failing test for postcondition N`.

Actualizá state file:
```json
"tdd_substage": "green",
"postconditions_status": { "<N>": "red" }
```

## Sub-fase 3.2 — GREEN

### Setup

Sesión `implementer`. Le pasás:

- El spec aprobado.
- El test que tiene que hacer pasar (los nuevos commiteados en RED).
- La interface.
- `docs/systemPatterns.md`.

**No le pasás el razonamiento del test-writer** (cómo decidió escribir el test). Solo el test ya escrito.

### Tarea del implementer

Hacer pasar el test con código **mínimo**. No agregar features no pedidas. No optimizar prematuramente. La regla es la del TDD clásico: la implementación más simple que hace pasar el test.

Si el implementer propone agregar tres cosas más "porque van a hacer falta después", frenalo:

> *"Esas las dejamos para cuando haya un test que las pida. Por ahora, mínimo viable para este test."*

### Verificación

Corré la suite completa (no solo el nuevo test). Todo verde, incluyendo los tests previos. Si un test previo se rompió, volvés al implementer para arreglarlo sin romper la postcondición nueva.

### Cierre de la sub-fase GREEN

Commit `feat: implement <postcondición>`.

State file:
```json
"tdd_substage": "refactor",
"postconditions_status": { "<N>": "green" }
```

## Sub-fase 3.3 — REFACTOR (opcional)

### Cuándo aplicarla

Solo si el código que salió de GREEN tiene fricción evidente: duplicación, nombres pobres, complejidad accidental. Si está limpio, **saltala**. Refactorizar por ritualismo no aporta.

### Setup

Sesión `refactorer`. Permisos: edit en código de implementación, NO en tests. Le pasás:

- El código actual.
- La suite completa.

### Regla absoluta

Suite debe seguir verde **en todo momento**. Si un cambio del refactorer rompe un test, lo revierte y prueba otro approach.

### Cierre

Commit `refactor: <qué se mejoró>`. State file no cambia (sigue siendo `green` en la postcondición).

## Sub-fase 3.4 — PROPERTIES

### Cuándo aplicarla

Solo si el spec marca **Invariantes verificables**. Aplica especialmente bien para:

- Algoritmos puros (parsers, encoders/decoders, transformaciones).
- Componentes con invariantes claras (round-trip, idempotencia, asociatividad).

No aplica bien para:

- Código con muchos side effects.
- Lógica de negocio con muchas condiciones específicas.
- UI.

Si no aplica, saltá a 3.5 (o cerrá la etapa si tampoco aplica).

### Setup

Sesión `test-writer` de nuevo, con permisos solo en `tests/`. Le pasás:

- El spec con la sección "Invariantes verificables".
- La interface.
- La librería de property testing del proyecto (Hypothesis para Python, fast-check para JS, QuickCheck para Haskell, etc.).

### Tarea

Escribir property tests que generen inputs aleatorios y verifiquen que las invariantes se cumplen. Si el property test falla con un input específico, ese input es un bug.

### Verificación

Property tests verdes con un volumen razonable (típicamente 100-1000 inputs por property). Si fallan, el implementer arregla el código (sub-fase mini-GREEN).

### Cierre

Commit `test: add property tests for invariants`. State file:
```json
"tdd_substage": "integration"
```

## Sub-fase 3.5 — INTEGRATION / E2E

### Cuándo aplicarla

Si el spec marca **criterios de aceptación E2E** o si la feature toca múltiples capas (DB, lógica, API, UI). Si la feature es puramente algorítmica sin side effects, no aplica.

### Modalidades

- **Modalidad A — outside-in**: el test E2E se escribe **antes** que cualquier unit test. Queda rojo durante todo el ciclo y va pasando a medida que las piezas se conectan. Bueno para features con flujo central claro y para tener métrica continua de progreso.
- **Modalidad B — cierre**: el test E2E se escribe **al final**, después de que las unidades están verdes, antes del merge. Más simple operativamente, perdés la métrica continua.

Decidilo con el usuario al inicio de la etapa 3. Para features de flujo central, A. Para agregados a flujos existentes, B.

### Tarea

El test-writer (en sesión aislada del implementer) traduce los criterios de aceptación a tests E2E. Setup con fixtures completas, llamadas a la API pública, asserts sobre los efectos observables.

### Verificación

E2E verde. Si está rojo en modalidad B (debería estar verde porque las unidades están verdes), hay un problema de ensamblaje: vuelta al implementer.

### Cierre

Commit `test: add E2E tests`. State file:
```json
"tdd_substage": "review-pending"
```

## Loop entre postcondiciones

Cuando una postcondición está verde, volvés a 3.1 con la siguiente. El ciclo es:

```
RED (post 1) → GREEN (post 1) → [REFACTOR] → RED (post 2) → ...
```

Hasta cubrir todas las postcondiciones del spec. Después PROPERTIES y INTEGRATION (si aplican).

## Gate de salida (Etapa 3 → Etapa 4)

- [ ] Toda postcondición del spec tiene al menos un test que la verifica.
- [ ] Toda la suite está verde (verificado empíricamente, no asumido).
- [ ] Si el spec marca invariantes → property tests verdes.
- [ ] Si el spec marca criterios E2E → tests de integración/E2E verdes.
- [ ] Commits granulares (RED, GREEN, REFACTOR separados, no un solo commit con todo).
- [ ] Cobertura cumple el criterio del spec, si lo había.

## Anti-patrones a vigilar

Cargá `references/anti-patterns.md` si detectás:

- Una sola sesión escribió test e implementación.
- El implementer modificó tests para hacerlos pasar.
- Tests escritos después del código.
- Test "verde" sin verificación empírica.
- Saltarse property tests cuando el spec los pedía.

## Cierre de la etapa

State file:
```json
{
  "current_stage": "review",
  "tdd_substage": null,
  "stage_history": [..., {"stage": "tdd", "completed_at": "..."}]
}
```

Cargá `references/stage-4-review.md`.
