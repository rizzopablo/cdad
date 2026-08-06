# ADR-004: "Usuario" = humano o agente autónomo de mayor jerarquía dueño del proceso

- **Status**: Accepted
- **Date**: 2026-08-05
- **Deciders**: Pablo (dueño del proyecto) + Ofap

## Contexto

El framework decía "aprobación humana indelegable": aprobar spec, priorizar
review, commitear Memory Bank, aprobar plan de epic, editar drafts. Pero la
metodología también se usa para orquestar otros agentes en forma completamente
autónoma (p.ej. desde un proceso orquestador externo), donde el dueño del proceso es un agente de
mayor jerarquía, no un humano. Decir "humano" excluía ese modo de uso y
obligaba a reinterpretar cada ocurrencia ("where CDAD says 'human approval',
read 'validación del usuario'"). El insight ya estaba en MEMORY.md: la
aprobación es async y non-blocking cuando la hace un agente dueño del proceso.

## Opciones consideradas

### Opción A: Mantener "humano" y reinterpretar en cada uso
- Pros: cero cambios de texto.
- Contras: ambigüedad permanente; cada lector re-deriva la regla; el modo
  autónomo (proceso orquestador externo orquestando agentes) queda como excepción tácita.

### Opción B: Renombrar el rol a "usuario" con definición canónica
- Pros: una definición única y visible; el modo autónomo queda explícito; el
  orquestador del ciclo sigue sin auto-aprobarse (se aclara en la misma
  definición).
- Contras: hay que tocar muchos archivos (skill, references, agents,
  templates); riesgo de relajar accidentalmente los guardrails anti-bias.

### Opción C: Dos roles distintos ("humano" y "agente dueño")
- Pros: precisión nominal máxima.
- Contras: duplica el texto de las reglas; en la práctica el comportamiento es
  el mismo (mismos criterios, mismos guardrails); más superficie de
  inconsistencia.

## Decisión

"usuario" = un humano O un agente autónomo de mayor jerarquía que es dueño del
proceso y orquesta este ciclo (p.ej. desde un proceso orquestador externo). Las decisiones
estratégicas —aprobar spec, priorizar review, commitear Memory Bank, aprobar
plan de epic— son del **usuario**, nunca del orquestador del ciclo. Cuando el
usuario es un agente, aplica los mismos criterios que un humano: guardrails
innegociables (matriz de severidad: seguridad y bug funcional = bloqueante sin
excepciones) y, ante la duda, se escala igual — no se baja la severidad por
ser agente.

Definición canónica en el bloque "Contrato de roles" de `cdad-cycle/SKILL.md`
y `agents/cdad-orchestrator.md` (ambas copias byte-idénticas). Sweep de las
ocurrencias de "humano" en rol de aprobador/dueño en el resto del framework:
references, agents, templates y copias sueltas. No se tocan las ocurrencias
idiomáticas/no-autoridad (ej. "error humano").

## Razones

1. La metodología se usa para orquestar agentes de forma autónoma; el dueño
   del proceso en ese modo es un agente de mayor jerarquía, no un humano.
2. La decisión estratégica sigue siendo del usuario — nunca del orquestador
   del ciclo (el orquestador no se auto-aprueba). Esto no cambia: solo se
   redefine quién puede ocupar el rol de usuario.
3. Mantener los guardrails (matriz de severidad innegociable, escalar ante la
   duda) evita que la autonomía relaje el anti-bias.

## Consecuencias

**Positivas:**
- Autonomía sin relajar anti-bias: el orquestador sigue sin auto-aprobarse;
  la matriz de severidad es innegociable para cualquier usuario, humano o
  agente.
- Una sola definición canónica en lugar de reinterpretación ad-hoc por
  lector.

**Negativas / trade-offs:**
- El criterio "quién es el usuario" queda a cargo del entorno que invoca el
  ciclo: quien lo orquesta desde afuera (proceso orquestador externo, humano) define si el
  dueño es un humano o un agente de mayor jerarquía.

**Neutrales:**
- La marca de aprobación en spec/state sigue el formato `Approved by <X>`
  donde X puede ser humano o agente; la trazabilidad de quién aprobó queda
  explícita (mismo estándar que AP-6).

## Notas

Formaliza el insight de MEMORY.md: "Where CDAD says 'human approval', read
'validación del usuario'... approval es async, non-blocking." `CDAD_metodologia.md`
(153KB) se revisa aparte; este ADR aplica a skills/, agents/ y templates.
