# Aprobación de spec y plan — 2026-10-31

Aprobación de los documentos de `010-001-documentary-contracts`, emitida por el
orquestador **en nombre de Pablo** al amparo del mandato HITL explícito registrado
en `docs/specs/010-004-packet-dispatch-ergonomics/owner-mandate-hitl-2026-10-30.md`
§3, que autoriza al orquestador a resolver «las aprobaciones que el plan del epic
exige para specs y planes de esas features **en tanto implementen la
descomposición y el alcance ya aprobados** en `plan.md`».

## Objeto aprobado

| Documento | Versión revisada | SHA-256 revisado (antes del marcador) | SHA-256 tras el marcador de aprobación |
|---|---|---|---|
| `spec.md` | draft-3 (sin cambios en draft-4) | `a01969d7f51da614c6e502d8660bafea17ad5ae8bb7caf5aea624f43927d94ac` | `9bf17a398b55384e271815c8a6c2910563f75a5d2475ec291c31d4f4d26c94da` |
| `plan.md` | versión 4 | `5fe898b6d9128a3bfe4397c984f339a2e85eac56e236919f9b1aa9cdf5187fca` | `cb3c25a8ba6b420baab8ec495620560c122ca17fbe749c95cb171e5867ab0265` |

El único cambio en los bytes posteriores al marcador es el bloque de aprobación
agregado al final de cada documento. El contenido revisado es el que llevan los
digests de la tercera columna.

## Revisión independiente previa

1. `plan-review.md` (primera pasada): un bloqueante F1 (nombre del dueño en
   producto instalable) y cinco observaciones F2–F6.
2. `architect-draft-003.md`: corrección de F1–F6.
3. `plan-review-002.md` (segunda pasada): F1, F3, F4, F5 y F6 cerrados; F2
   cerrado con reparo; bloqueante nuevo N1 (un solo paquete activo: T1 no podía
   preparar T2 y T3 a la vez) y observación N2.
4. `architect-draft-004.md`: corrección de N1 y N2.
5. `plan-review-003.md` (tercera pasada): N1 y N2 cerrados, sin bloqueantes
   nuevos.

Las tres pasadas las realizó `cdad-reviewer`, en sesión nativa distinta de la del
architect y con otro modelo configurado por el runtime (arquitecto:
`openai/gpt-6.1-sol`; reviewer: `claude-code/claude-opus-5-5`). Ninguna revisión
fue ejecutada por su autor.

## Alcance de la aprobación

- Implementa la descomposición y el alcance ya aprobados del epic-010
  (`plan.md` §Descomposición, fila 2: «los roles disponen de criterios
  documentales compartidos…»). No agrega features, no cambia el orden, no
  modifica criterios de aceptación del epic.
- No modifica contratos ya aprobados: `010-004` conserva sus pins.
- No relaja gates, severidades ni aislamiento de roles.

## Observaciones no bloqueantes diferidas, con motivo

- **O1 (plan-review-003, nit de redacción).** La verificación de T1 dice
  «Paquetes válidos» en plural aunque T1 prepara un solo encargo. Se acepta como
  redacción imprecisa: el paso 3 y el `integration_gate` de T1 son inequívocos
  sobre «únicamente el encargo de T2», y ninguna conclusión del proceso depende
  del plural.
- **O2 (plan-review-003, ruta de retorno del grupo D).** La ruta de retorno de
  T4 hacia un GREEN acotado de T3 nombra `sources/` y
  `skills/cdad-cycle/SKILL.md`, no la referencia nueva. Un hallazgo atribuible a
  la referencia cae en la regla general ya declarada en T4 («si aparece una
  necesidad real fuera de este alcance, se informa y se replantea»), que produce
  el mismo efecto —volver a T3— con un paso de decisión adicional. Se difiere sin
  ampliar alcance; si el defecto apareciera en la práctica, se corrige el plan
  por enmienda.

## Límites de esta aprobación

No acredita trabajo de rol alguno, no sustituye los gates de TDD, review y
cierre, no convierte una recepción en aprobación y no autoriza push, publicación
ni instalación global. La aceptación funcional del entregable y la aprobación del
Memory Bank al cierre se registran por separado cuando correspondan.
