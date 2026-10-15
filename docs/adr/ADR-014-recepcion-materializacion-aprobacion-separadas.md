# ADR-014 — Recepción, materialización y aprobación son hechos distintos; el recibo nunca aprueba

## Estado
Aceptado (2026-10-06) — origen: feature `003-002-artifact-tools` (epic
`epic-003-context-efficiency`). Aprobado por el dueño (HITL delegada al
orquestador OpenCode). Borrador del scribe materializado por el orquestador
(ADR-003).

## Contexto
ADR-003 establece que el orquestador materializa los artefactos de los roles
read-only transcribiendo su output. En la práctica ese patrón mezclaba tres
hechos distintos: (a) la **persistencia exacta** de los bytes que produjo un rol,
(b) la **copia autorizada** de esos bytes a destinos canónicos, y (c) la
**aprobación semántica** del artefacto (spec, review, audit, Memory Bank), que es
indelegable al LLM. Sin una separación mecánica, un "recibo" o una copia podía
leerse como aprobación, y el estado del ciclo podía ser mutado por la herramienta
que persistía el output. El runtime v2 (execution context, paquete renderizado,
binding de autoridad, observación de dispatch I8) ya aportaba la identidad y la
vigencia sobre las que construir.

## Opciones consideradas

### Opción A: herramientas de artefactos con recibo mecánico que no aprueba
- **Pros:** persiste bytes originales de forma atómica e idempotente; separa
  recepción/materialización/aprobación; un solo escritor del state; scopes y
  targets explícitos; evidencia de runner no auto-elegida.
- **Contras:** superficie nueva (CLI, store, schemas, política de artefactos) que
  reconciliar; la aprobación sigue siendo un acto externo.

### Opción B: mantener la materialización manual del orquestador (ADR-003) y
dejar la recepción/evidencia fuera del producto
- **Pros:** cero superficie nueva.
- **Contras:** no persiste bytes originales de forma verificable ni idempotente;
  la transcripción puede resumir o regenerar; no hay recibo mecánico ni evidencia
  de suite reutilizable con equivalencia comprobada. **Descartada.**

### Opción C: un harness que además apruebe automáticamente
- **Pros:** menos pasos humanos.
- **Contras:** viola el invariante "la aprobación no es delegable al LLM";
  convierte una comprobación mecánica en un gate semántico que no puede
  sostener. **Descartada.**

## Decisión
`receive`, `materialize` y `run-evidence` son operaciones separadas de un CLI
(`skills/cdad-cycle/scripts/cdad_result.py` + entrypoint instalado), construidas
sobre el runtime v2. Reglas fijadas:

1. El recibo es **mecánico e inmutable**: `semantic_status` siempre `pending`,
   `approval_effect` siempre `false`; ningún recibo aprueba ni cierra un gate.
2. **Un solo escritor del state:** `docs/.cdad-state.json` lo cambia solo el
   orquestador; `state_transition_requested=received` es lógico y el orquestador
   lo mapea al estado de paquete `completed`.
3. **Persistencia atómica e idempotente** (temp + fsync + rename), una sola
   finalización durable por `(execution_id, packet_id)`; el retry idéntico devuelve
   el mismo receipt byte a byte.
4. **Política de artefactos:** la tabla cerrada fija la **raíz permitida** por
   `artifact_kind`; el **target exacto** se declara en la autorización
   (create-only/CAS). El cierre rol↔kind es fail-closed.
5. **Evidencia de runner** limitada a `python3 -m unittest`, con snapshots
   before/after calculados por la herramienta y ligadura `argv`↔selecciones
   fail-closed (lo no demostrable degrada a `unknown`, nunca a verde).

## Razones
1. Preserva el aislamiento/anti-bias de ADR-001/ADR-003: el rol sigue read-only y
   el artefacto lo materializa el orquestador, ahora con bytes verificables.
2. Mantiene la aprobación semántica donde corresponde (dueño/orquestador según
   delegación), separada de la mecánica.
3. La idempotencia y la atomicidad hacen el flujo reconciliable al re-entry.

## Consecuencias
- **(+)** Recepción verificable byte a byte, retry idempotente, evidencia de suite
  reutilizable con equivalencia comprobada; primer uso real en este repo
  (`receive`+`materialize`, bytes idénticos).
- **(+)** El state conserva un único escritor (el orquestador); ninguna herramienta
  muta el ciclo.
- **(−)** Superficie nueva que reconciliar en instalación y consumidores (hecho).
- **(−)** Los ADR no están cubiertos por la tabla de artefactos: su materialización
  sigue siendo del orquestador (ADR-003).
- **(−)** La whitelist de `argv` quedó más estricta que lo necesario (`--locals`,
  `-c` degradan a `unknown`); efecto real ≈ nulo (falla del lado conservador).
- **Neutral:** `observation_status=unknown` y el CAS de Memory Bank quedaron sin
  ejercitar (el primer uso fue create-only).

## Confianza
**Alta** para el núcleo (recibo que nunca aprueba, un solo escritor del state,
persistencia exacta/idempotente): verificado en uso real y en cuatro reviews
cerradas (T1–T4), con `materialize` aplicando la vigencia de la delegación tras
R1 de T2 (reproducido y cerrado empíricamente). **Media** para la cobertura de la
política de artefactos: `observation_status=unknown` y el CAS de Memory Bank no se
ejercitaron todavía; los ADR quedan fuera de la tabla.
