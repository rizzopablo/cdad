# ADR-018 — Las clases de referencia de la continuidad (contrato/vivo) las declara el escritor, nunca la ruta

* Estado: **Aceptado** (2026-10-08; orquestador bajo delegación HITL de epic-003)
* Fecha: 2026-10-08
* Decisores: dueño (Pablo); orquestador bajo delegación HITL de epic-003
* Confianza: **Media**

## Contexto y enunciado del problema

`cdad_continuity` (003-004, ADR-016) sellaba **todas** las referencias de un checkpoint por
digest y fallaba cerrado ante cualquier deriva. El trabajo real escribe ledgers, deuda y
Memory Bank **después** de cada checkpoint, así que la reanudación se bloqueaba por progreso
legítimo (**T4-REF**, deuda alta de 003-006) y un checkpoint de límite se confundía con un
`begin` duplicado (**T4-CKPT**). Hacía falta distinguir **qué cambio invalida una evidencia**
(contrato/autoridad) de **cuál es progreso** (documentos vivos), sin introducir un servicio,
un agente permanente ni un controlador LLM, y sin clasificar por rutas fijas.

## Impulsores de la decisión

- Que la evolución normal del trabajo (ledgers, deuda, Memory Bank) no impida reanudar.
- Que la deriva de un contrato/autoridad **sí** bloquee, con path y delta exactos.
- Que el CLI siga siendo determinista y read-only sobre el producto, y nunca apruebe.
- Que la integridad no baje en silencio (nada de digests constantes ni proyecciones vacías).

## Opciones consideradas

1. **Clasificar por rutas fijas dentro del CLI.** Rechazada: mezcla contrato y progreso, produce
   bloqueos espurios y no cubre excepciones; además contradice "no hay clasificación por rutas".
2. **Clases por defecto declaradas en la política** (`docs/cdad-policy.json`). Diferida a deuda:
   el esquema es estricto (`cdad_packet.py:406` exige `set(document) == POLICY_KEYS`) y requiere
   coordinar con el renderer.
3. **Clases declaradas por el escritor en la referencia** (elegida): `{"path", "class", "fields"?}`
   con ausencia/desconocido → `contract` (falla cerrado).

## Decisión

1. Una referencia de continuidad lleva `class ∈ {contract, living}` **declarada por el
   escritor**; el CLI **no** deriva la clase de la ruta. Ausente o desconocida → `contract`
   (falla cerrado). La clase resuelta se **estampa** en el body del checkpoint.
2. **`contract` bloquea** (`rc≠0` con `path` y delta); **`living` informa y nunca calla en
   silencio** (`state ∈ unchanged|changed|missing`, `current_sha256`). El sobre de
   `resume`/`reconcile`/`trigger` reporta cada referencia visible.
3. **`fields`** proyecta un JSON a un subconjunto de claves top-level (autoridad del state:
   `hitl_delegation`, `approver`, `execution`); `fields` sobre no-JSON o con proyección vacía
   → `rc≠0` **al escribir** (el digest se congela en el body).
4. **El body del checkpoint gana `record`** (`begin`|`checkpoint`): un `checkpoint` con la clave
   del head **apendea** un eslabón (`seq+1`, `prev`), un `begin` divergente con la misma clave
   sigue cerrado, un checkpoint idéntico es no-op; `_detect_split_brain` = ≥2 bodies con
   `record != "checkpoint"` por clave.
5. **Legado por comparación (P7):** un cuerpo pre-003-007 sin `class`, si difiere, se reporta
   `changed` con `legacy: true` y **no bloquea**; su clase **no está congelada**.
6. **Unidad despachable en el orquestador:** el encargo es una tarea del plan o una subfase TDD
   (RED/GREEN como despachos separados la satisfacen), con postcondiciones trazadas a ≥1 test y
   un diff acotado; el "Continuity wiring" declara las clases `living`/`contract`.

## Consecuencias

- **Positivas:** la evolución normal deja de bloquear sin perder integridad; `contract` sigue
  fail-closed con delta exacto; la distinción es explícita, auditable y verificable; el CLI
  permanece read-only y nunca aprueba (ADR-003/ADR-016 intactos).
- **Negativas / límites declarados:** el legado se resuelve por comparación y su clase **no está
  congelada**, de modo que **informa** cualquier documento cambiado —incluida una decisión que
  en un checkpoint nuevo sería `contract`— en lugar de bloquearlo; **MIX-V6V7** obliga a usar
  una sola versión del CLI por ejecución (la v6 con un checkpoint v7 con `fields` falla
  cerrado); **T2-R1** (un `begin` idéntico tras un append de su clave da `rc≠0` en lugar de
  no-op); sin detección de forks de checkpoint mismo-key; `stage_history` (R2-STAGE) y las
  clases por policy (POLICY-CLASS) quedan fuera de todo digest/por defecto.

## Alternativas y trabajo futuro

Clases por defecto en la política (bloqueado por el esquema estricto; coordinar con el
renderer); detección de forks de checkpoint mismo-key; integridad de `stage_history`;
remedio de T2-R1 (reconocer el body idéntico en `bodies/`); documentar MIX-V6V7 en la adopción
de la v7; lector de sesiones, medición de contexto y CI (deuda del epic).

## Confianza

**Media.** La decisión y sus postcondiciones (P1–P10) están verificadas por tests focales y por
**uso real** (rotación v7 sobre los tres stores; bloqueos de contrato/autoridad en copia; sonda
2 que descubre `resume`/`reconcile` sin indicación). La confianza no es alta porque el legado
por comparación **no congela la clase** (informa en vez de bloquear), hay límites declarados
(MIX-V6V7, T2-R1, sin detección de forks) y el gate es una suite local sin CI.

## Enlaces

- Spec/plan: `docs/specs/003-007-living-continuity/{spec,plan}.md`
- Evidencia: `docs/specs/003-007-living-continuity/{dispatch-ledger,continuity-ledger,debt}.md`,
  `evidence/t3/`, `evidence/discovery-probe-2.md`, `review-t1..t4*.md`
- ADR relacionados: ADR-003 (el orquestador materializa), ADR-014
  (recepción/materialización/aprobación separadas), ADR-016 (continuidad checkpoint
  content-addressed), ADR-017 (activación por proyecto hacia raíz aislada)
- Cierre pendiente: `docs/specs/003-007-living-continuity/closure.md` (a redactar) y
  `docs/epics/epic-003-context-efficiency/closure-amendment-draft.md`
