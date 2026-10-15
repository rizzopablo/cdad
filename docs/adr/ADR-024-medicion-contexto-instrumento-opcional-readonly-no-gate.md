# ADR-024: La medición de contexto es un instrumento opcional, read-only y no-gate

- **Status**: Accepted
- **Date**: 2026-10-11
- **Deciders**: orquestador OpenCode (HITL delegada epic-005) + architect
- **Confidence**: Media
- **Aprobación**: orquestador OpenCode bajo la delegación HITL del epic-005 (`docs/epics/epic-005-real-operation/execution.md`), con evidencia (spec aprobada, review formal, suite de cierre). El architect no aprueba su propia propuesta.

## Contexto y problema

El epic-005 necesita medir el contexto que consume cada rol para reducir la orientación del
orquestador con datos, no con supuestos. La medición debe servir a features posteriores (005-003,
005-006) sin convertirse en un motor de evaluación de sesiones ni en un nuevo gate del ciclo, y sin
acoplar el contrato de medición a un runtime concreto: el esquema de la fuente **no es un contrato
público** y la deriva ya ocurrió. ¿Dónde vive la medición y cuánto puede decidir?

## Opciones consideradas

### Opción A: instrumento opcional, read-only, no-gate, con registro neutral y adaptador que traduce
- Pros: neutralidad respecto del runtime; el ciclo sigue aunque el entorno no exponga tokens; el
  medidor no puede auto-validar ni aprobar nada; el contrato neutral (asset) y el traductor
  (adaptador) evolucionan por separado.
- Contras: el registro neutral y el adaptador deben mantenerse coherentes; exige disciplina de cubos
  (observado/estimado/desconocido) para no fabricar métricas.

### Opción B: gate de medición obligatorio del ciclo
- Pros: garantiza que toda feature quede medida.
- Contras: acopla la metodología a la disponibilidad de tokens del runtime; convierte un instrumento
  de observación en una precondición; contradice «opcional para la metodología» (plan fila 7).

### Opción C: motor de evaluación de sesiones con veredicto propio
- Pros: un único lugar que clasifique el resultado.
- Contras: exige juicio semántico (calidad, fricción, repeticiones de suites), fuera del alcance
  declarado; el instrumento determinista no puede emitir veredictos honestos.

## Decisión

La medición se implementa como **instrumento opcional**: un **registro neutral**
(`context-meter-v1`) en un **schema asset** + **reference** de la skill, **no enganchado en ningún
gate**, y un **adaptador read-only** (lector SQLite `?mode=ro`, `stdlib`, JSON único y determinista)
que **solo traduce**. El registro distingue **observado / estimado / desconocido** (desconocido
**nunca** es cero) y el medidor **nunca aprueba nada**: el informe de aplicación es una **anotación
referenciada** cuyo límite deriva de hechos observables, no del juicio del lector.

## Razones

1. La medición es **opcional para la metodología** (plan fila 7): el desarrollo no puede depender de
   que el runtime exponga tokens.
2. Neutralidad: el registro no contiene nombres de tablas/columnas del runtime; el adaptador es el
   único traductor (R6), de modo que el contrato sobrevive a cambios de runtime.
3. El esquema del store no es contrato público (deriva ya ocurrida): el adaptador **falla cerrado**
   por columnas/tabla requeridas, con diagnóstico que nombra el faltante y sin fabricar métricas.
4. Separar observación de decisión: el medidor no cierra gates ni aprueba resultados; el juicio
   semántico queda fuera del instrumento.

## Consecuencias

**Positivas:**
- El ciclo sigue funcionando sin datos de tokens; la medición se invoca a demanda.
- El contrato neutral es reutilizable por otros adaptadores (p. ej. otros runtimes) sin tocar la
  metodología.
- Un despacho registrado no se confunde con una entrega aceptada.

**Negativas / trade-offs:**
- El registro neutral y el adaptador deben mantenerse coherentes (el asset es el contrato; el
  adaptador traduce).
- La salida compacta (límite normativo de 16384 bytes por documento de sesión) debe respetarse para
  no inyectar el transcript al contexto del consumidor.
- El detector de hitos reconoce un conjunto acotado de herramientas (riesgo de falso `absent`
  declarado), registrado como deuda.

**Neutrales:**
- La anotación de aplicación es opcional; su ausencia no afecta el registro.

## Notas

- Contrato normativo: `docs/specs/005-002-session-context-meter/spec.md` (PD-1..PD-16,
  INV-1..INV-10); procedimiento: `skills/cdad-cycle/references/context-meter.md`; contrato neutral:
  `skills/cdad-cycle/assets/context-meter.schema.json`.
- Análogo a ADR-015 (analizador read-only, juicio en el orquestador) y ADR-014 (recepción,
  materialización y aprobación separadas).
- Deuda priorizada asociada: `docs/specs/005-002-session-context-meter/debt.md` (10 OPTIONAL; D1 =
  el `time_relative: 0.0` fabricado).
