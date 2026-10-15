# Cierre — 005-001-idle-and-v7-bootstrap

**Feature:** `005-001-idle-and-v7-bootstrap` · **Epic:** `epic-005-real-operation`
**Cerrada:** 2026-10-09 · **Aprobada por:** orquestador OpenCode (HITL delegada epic-005)
**Contrato:** `spec.md` sha256 `9b92b8f4c873a79b9660231a891e2e94de3eed882e12a008f7ecfff1e854c99c`
(incluye la enmienda T-CORR del 2026-10-09) · **Plan:** `plan.md` (T1–T4 + T-CORR)

## 1. Resultado

La feature corrige la **circularidad I2** del arranque de una feature y habilita la
**operación real con v7**:

- **(b) Aprobación de contrato por rol.** El **architect** se habilita con la aprobación
  del **plan del epic** (`epic_history` `stage: "epic-plan"`, `approved_by`, **sin** pin de
  hash — D2). **test-writer, implementer y reviewer** exigen una entrada `stage_history`
  `specification` que **nombre el contrato**: `contract_path` **y** `contract_sha256`
  coincidentes con el contrato verificado (D3; C1/PD-18/INV-8). Editar la spec deriva el
  sha y la aprobación deja de coincidir (PD-4).
- **(c) Reemplazo de un paquete preparado y no despachado.** `prepare --replace-packet
  <id> --reason <texto>` re-resuelve el contrato del día y publica un sucesor **solo** con
  la aprobación vigente (PD-11); exige obsolescencia verificable (PD-8) y un `--reason` no
  vacío (PD-9); un paquete `dispatched` sigue exigiendo **reconciliación** (PD-10). El
  paquete anterior queda **byte a byte idéntico** (INV-3) y se escribe `.superseded.json`
  durable. **C2 (enmienda T-CORR):** el reemplazo **conserva** campo a campo el encargo
  anterior (`inputs`, `read_scope`, `write_scope`, `invariants`, `expected_output`,
  `evidence_required`) y admite las opciones de corrección `--input/--read-scope/
  --write-scope/--invariant/--expected-output/--evidence` (cada una reemplaza esa lista
  entera; centinela `-` para vaciarla cuando la spec lo permite; PD-19..PD-24/INV-7),
  con los pisos obligatorios del rol imposibles de quitar (PD-21) y la traza
  `conserved_fields`/`changed_fields` en `.superseded.json` (PD-24).
- **(d) Marcadores distinguibles y accionables** (PD-12): `approval pending` /
  `packet obsolete` / `state incoherent`, mutuamente excluyentes por condición, con el
  registro/falta concreto y la acción legítima siguiente, sin efectos.
- **(e) Reposo legítimo.** `validate-state` acepta un state en reposo
  (`active_feature == null` ⟺ `current_stage == "idle"`, con `execution` remanente y/o
  `active_packet` terminal) → `VALID: idle`; rechaza el incoherente y el reposo con un
  paquete en vuelo (PD-13..PD-15).
- **(a) Publicación de los agentes de proyecto v7** (ya cumplida el 2026-10-08): el primer
  `prepare` del epic publicó `source_dir` + 11/11 hashes de la raíz v7 adoptada.

## 2. Prueba decisiva (PD-17)

Un único escenario secuencial end-to-end, caja negra sobre el CLI
(`tests/test_005_001_t4_decisive.py`): discovery del architect autorizado **sin** spec;
construcción bloqueada (`approval pending`) hasta la aprobación pineada; `--resume-packet`
de un paquete obsoleto → `packet obsolete`; `--replace-packet` con la autorización vigente
→ sucesor publicado, paquete anterior intacto, `.superseded.json` con el motivo, sin tocar
`stage_history`/`epic_history`; negativos sin efectos. **Verde end-to-end** (commit
`70df141`).

Escenario **ajustado** (instrucción del dueño, 2026-10-09): el paquete del architect se
**recibe y completa** (flujo real `record-dispatch` → staging → `receive` →
`validate-receipt` → transición) antes de preparar al test-writer, y el reemplazo se prueba
con un paquete **todavía `prepared` y no despachado** (P1). El ajuste está registrado en
`dispatch-ledger.md` (fila 13) y en `debt.md` (B2: PD-17 literal edita el plan del epic y
reemplaza el paquete del architect; queda sin test focal la semántica del architect —
contrato sin pin de hash, mismo code path).

El RED de T4 **destapó un defecto real**: sin el archivo de la spec y sin aprobación,
`prepare` daba el error genérico «cannot read contract» en vez de `approval pending`
(PD-3/PD-12); se corrigió con `_reject_absent_contract_without_approval` (commit
`70df141`).

## 3. Gate de cierre

- **Suite completa:** `python3 -m pytest tests/ -q` — **629 passed, 0 failed** en
  `ec86ca8` (los commits posteriores son solo `docs/`: Memory Bank, ADR y state; la
  equivalencia del árbol de producto está declarada — ningún test lee esos archivos).
- **Focales de la feature:** 30 passed (t1 7, t2 8, t3 4, tcorr 10, t4 1).
- **`make validate`:** 141 PASS / 2 FAIL **F011 preexistentes** (drift de mirrors de HOME;
  patrón sensible A3), verificados por `git stash` como ajenos al diff (R4 del plan).
- **Sin CI** (gate local, deuda declarada).
- **Auditoría test↔postcondición:** un test por postcondición (PD-1..PD-24), caja negra sin
  mocks del producto, control positivo interno en cada negativo, marcadores mutuamente
  excluyentes. Tres ciclos RED→GREEN interrumpidos por defectos del **test** (no del
  producto), con derivación al test-writer y RED re-verificado con `git stash`.

## 4. Review formal (stage 4)

Una **única** review formal (`review.md`), que cubre T1–T4 y las correcciones T-CORR:
veredicto `changes-required` con **1 bloqueante B1** y 6 opcionales.

- **B1 (doc, bucket m) — CERRADO:** la sección «Reemplazo» de
  `skills/cdad-cycle/references/project-execution.md`, declarada por el plan (T2/T-CORR),
  nunca se había escrito. Cerrada con el commit `9468027` (+75/−1) y su **familia**
  (`1faef04`: el índice de `SKILL.md` menciona `replacement`). Cierre verificado por el
  orquestador según la condición del reviewer: `grep` de la referencia pasa de rc=1 a rc=0.
- **Opcionales B2..B7 → deuda** (`debt.md`). **B3** (la raíz v7 viva quedó fuera de sync
  para `cdad_packet.py`: no corre C1 ni `--replace-packet`) es **decisión del dueño**
  (activar/re-sincronizar versiones está reservado al dueño).

## 5. Registro y trazabilidad

- Paquetes y sesiones: `dispatch-ledger.md` (filas 1–15).
- Commits de producto: T1 `c885f02`, T2 `0e77e49`, T3 `11e1454`, T-CORR `bfe8edb`, T4
  `70df141`; review-fix B1 `9468027` + familia `1faef04`.
- Commits de tests: `e49a1ce`, `7941007`, `66b880a`, `d7355b7`, `3b5c5ec`, `bd65cd6`,
  `ec8bd48`.
- Spec/plan `71520dd`; enmienda T-CORR `d1b36c2`; review `952bc72`; Memory Bank `eb2a288`.
- `stage_history`: entradas `specification` (con pin re-registrado), `tdd-red/green-t1..t4`,
  `tdd-red/green-tcorr`, `review-1`, `review-fix-b1(-familia)`, `merge-memory-bank`.
- Receipts durables: `architect-draft-001`, `reviewer-review-001`, `scribe-memory-001`.

## 6. Limitaciones y deuda

- **B3 (media, dueño):** la raíz v7 viva y el repo divergen en `cdad_packet.py`; el próximo
  despacho por la raíz v7 usaría un CLI sin la feature (reintroduce la circularidad I2).
  Re-sincronizar antes de 005-002.
- **B2, B4, B5, B6, B7** (opcionales) — detalle en `debt.md`.
- **Observación de gate:** los agentes de proyecto derivados apuntaban a la instalación de
  HOME (otra versión) por un `prepare` sin `CDAD_OPENCODE_AGENTS_DIR`; corregido en la
  sesión (el CLI no fuerza la raíz adoptada — candidato de mejora de producto).
- **Sin CI**; `make validate` con 2 FAIL preexistentes (F011/A3).
- El texto literal de **PD-17** no coincide con el escenario ejecutado (B2); la autoridad
  del ajuste es la instrucción del dueño del 2026-10-09.

## 7. Estado al cerrar

`epic_features[005-001].status = "done"`; la ejecución queda en reposo legítimo
(`active_feature: null`, `current_stage: "idle"`, binding `execution` conservado) —
`validate-state` → `VALID: idle`. El epic-005 sigue activo (`features-loop`) con
`005-002-session-context-meter` en cola; **no se abre por anticipado**.
