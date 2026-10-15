# Cierre de 005-012-transition-registration

**Feature:** 005-012-transition-registration · **Epic:** `epic-005-real-operation` (fila 12, decimotercera y
**última** unidad) · **Cerrada:** 2026-10-14 · **Contrato:** `spec.md` sha256
`9e34750f4c238c337d4d56be7e1edab5749329c4b9bbed3ee3c34a25b37e7cc9` (draft-004) · **Plan:** `plan.md` sha256
`9abfb89408c94ef25e14e2fea68b5ca1015718f09d1d5b2936e404db33dba10d` · **Aprobación:** orquestador OpenCode
bajo la HITL delegada del epic-005 (`docs/epics/epic-005-real-operation/execution.md:8-23`).

## 1. Qué entrega la unidad

**Una operación del CLI que registra la decisión explícita del orquestador sobre una transición** —recepción
de una entrega, aprobación de un gate, avance de etapa, cierre de feature, entrega tardía y **disposición de
un despacho sin recibo**—, **comprueba sus requisitos mecánicos** y la aplica **sin edición manual del
state**, con: (a) la **evidencia referenciada** exigida (recibo durable o artefacto materializado) y el gate
aprobado por la **autoridad vigente**; (b) **recibir nunca aprueba**; (c) repetirla **no duplica efectos**; y
(d) la **contabilidad automatizada** con el **juicio en el orquestador** (fila 12, `plan.md:45`).

Superficie: `cdad_packet.py register-transition` con seis clases (vocabulario cerrado), el **escritor único**
existente (`_ProjectLock` + publicación atómica + una sola serialización) y la **forma aditiva** del registro.
El **cierre comprueba ANTES de aplicar**: entregas requeridas (recibo durable **o** disposición) y la
aprobación vigente, falla cerrado **nombrando** y ofrece las dos salidas legítimas. Decisión registrada en
**ADR-029** (`docs/adr/ADR-029-registro-de-transiciones-identidad-por-contenido-vigencia-por-el-pin.md`).

## 2. Gates de la etapa 3 (verificación propia del orquestador, no aceptación de la prosa)

| Tarea | Focal (RED → GREEN) | Regresiones declaradas | Otros |
|---|---|---|---|
| T1 superficie + identidad + digests derivados + forma mínima | 15 rojos por **aserción** (`878091b`) → **15 passed** (`401f966`) | **56** | — |
| T2 `gate`: pin por bytes + autoridad en tres casos | 14 → **14** (`21bada6`) | **33** | T1 15 |
| T5 vigencia estructural (`supersedes` + lector) | 5 → **5** (`c164b30`) | **42** | T1+T2 29 |
| T3 `closure` + `disposition` (B1) | 8 → 7/8 **con bloqueo declarado** (`0057a50`) → testfix (`016405f`) → **8** | **20** | T1+T2+T5 34 · `test_packet_prepare` 19 |
| T4 `receive --late` + `late-delivery` | 7 → **7** (`f5e0fc2`) | **25** | T1..T5 42 · proporcionales 61 |
| T6 guard del contexto abierto y sin uso | 3 (1 rojo de contrato + 2 controles) → **3** (`721990f`) | **42** | T1..T5 49 · uso legítimo 15 |
| T7 documentación por referencia (docs-only) | comprobaciones observables (`7b10325`) | — | sentido del texto: review |
| review-fix B1 (PD-6 en `closure`) | 3 → **11** (`724ca3c`) | **20** | T2 sin cambio |
| review-fix B2 (identidad con los insumos con efecto) | 5 → **21** (`64a32d3`) | **56** | T1 previos intactos |
| review-fix B3 (vigencia por el pin) | 3 → **8** (`ffb7abd`) | **42** | T2+T3+T5 33 · T1+T4+T6 31 |

Todos los RED fallaron **por aserción** (0 `ImportError`, `SyntaxError` o errores de colección) y ningún GREEN
tocó `tests/` (verificado en cada uno con `git diff --name-only <base>..<green> -- tests/` **vacío**).

## 3. Review formal (etapa 4) — 2 bloqueantes / 7 opcionales / 3 abstenciones

`review.md`, diff `74b0f4e..HEAD` (25 archivos, +7448/−20), reviewer `mofgw/glm-5.3-flash` — **familia
distinta** a la del implementer `mofgw/deepseek-v4.1-flash` — en sesión aislada y de sólo lectura. Auditoría
test↔postcondición: **52 tests, 0 superfluos, 0 mocks sobre el cableado**.

- **B1 — la comprobación de autoridad de PD-6 no se aplicaba a `closure`** (una sola call-site de
  `_gate_authority`, en la rama `gate`): un cierre bajo delegación **revocada o vencida** prosperaba
  escribiendo `approved_by` y marcando `done`. **Corregido ya** con RED primero (`331566c` → `724ca3c`).
- **B2 — `transition_key` omitía los insumos con efecto** y el no-op corría antes de toda escritura: N
  `delivery` del mismo paquete con la misma etiqueta (el uso natural para registrar las postcondiciones de un
  GREEN, porque `--postcondition` es singular por invocación) devolvían rc=0 «no-op» **sin registrar y sin
  fallar**, contra PD-12. **Corregido con enmienda del contrato** (draft-003: PD-10 con el payload canónico,
  PD-11 con el no-op honesto) y después RED/GREEN (`f7fcbcc` → `64a32d3`).
- **B3 — la reaprobación tras una enmienda estaba obligada al registro manual:** el control de exclusión de
  PD-14 exigía `--supersedes`, que **sólo puede citar entradas con `transition_key`**, y las aprobaciones
  registradas a mano son **keyless**. Hallazgo del orquestador OpenCode al reaprobar la enmienda de B2
  (**medido**: la nota de esa entrada transcribe las dos respuestas del CLI), declarado **bloqueante para el
  uso previsto** por el orquestador Claude. **Corregido con enmienda del contrato** (draft-004: la vigencia la
  decide **el pin que nombra los bytes actuales**, el criterio que PD-8(b) ya usaba) y después RED/GREEN
  (`dc13903` → `ffb7abd`).
- **Opciónales:** O1..O4 (texto de AC-4/ficha T3, §2.1, la «tabla» inexistente, el mecanismo del control de
  fecha) corregidos en las enmiendas; **O5/O6/O7 → deuda D-13..D-15**. **Abstenciones (3):** la evidencia de
  T8 (resuelta corriéndolo), la suite completa (resuelta en el cierre) y la auditoría recibo-por-recibo de las
  transiciones registradas (material del audit del orquestador).
- El reviewer juzgó **correcta** la divergencia de `gate` frente a `validate-state`/`prepare` ante delegación
  vencida **por fecha** (PD-6 lo exige; `_validate_v2_vigency` no lee `expires_on`) y verificó que la
  limitación de `tdd_substage` **no obliga a editar el state a mano** (ningún validador lo lee; `open-unit` lo
  limpia), por lo que no bloquea AC-1.

## 4. Aceptación (T8) — APROBADA y repetida sobre el commit final

`acceptance.md` (sha256 `da6e3d59227da1ed9f27fbb172d3869c926a1617ffeed14c27cb3f5f9fb480c2`): el **CLI real del
repo** como subproceso sobre **proyectos descartables en `<tmp>`** con el `HOME` del subproceso en un tempdir
**vacío**. **AC-1** (ciclo representativo registrado **sólo** con la operación, en la **forma mínima sin pasar
ningún digest**): **8 invocaciones, todas rc=0**; **7 entradas** de la operación (`advance`, `gate` de etapa 2,
`delivery` RED, `delivery` GREEN, `delivery` del Memory Bank, `gate` de T4, `closure`); feature `done` /
`active_feature: null` / `idle`, con los digests **derivados** por el CLI y **cero** ediciones manuales del
state. **AC-2** `receive` normal sigue fallando cerrado; `receive --late` rc=0 con recibo durable y
`semantic_status: pending`; `late-delivery` rc=0; la feature **no se reabre** y no aprueba nada. **AC-3**
idéntica → no-op **byte-idéntico** nombrando la entrada; distinta → entrada nueva; estructuralmente excluyente
→ rc=2 `state incoherent` sin efectos. **AC-4** cierre sin aprobación → `approval pending`; con un despacho
**sin recibo** → `evidence missing` **nombrando el paquete**, state intacto, **ofreciendo las dos salidas y ya
no `late-delivery`**; con la disposición registrada, el cierre **avanza**. T8 se **repitió sobre `6fd515d`**
(después de B3) con los mismos resultados (`closure-suite.md`), y ese gate quedó registrado con la operación.

## 5. Suite de cierre (una vez, por quien cierra)

`closure-suite.md`: worktree fijado a **`6fd515d`** (T1–T7 + los review-fix B1, B2 y B3 + la evidencia de T8).
`python3 -m pytest tests -q -p no:cacheprovider` → **1024 passed / 4 skipped, sin fallos**. `make validate` →
**155 PASS / 1 FAIL**, el fallo **F011 preexistente** (D-6 de 005-011). Entre `6fd515d` y este cierre sólo
cambia documentación.

## 6. El dato de la unidad: el trabajo manual bajó, medido

Esta es la **primera feature que se cierra con la operación que ella misma entrega**. El `stage_history` de la
feature tiene **32 entradas**: **26 registradas con la operación** (21 `delivery` + 5 `gate`) y **6 a mano**,
cada una con su motivo declarado en su nota:

1. el **discovery** y las **cuatro aprobaciones `specification`** (draft-001 inicial, draft-002, draft-003 y
   draft-004): el procedimiento propio del orquestador —la spec y el plan se aprueban y se registran **antes**
   de que la operación exista para la feature, y esas entradas son **keyless**—;
2. el **RED de T1** — la operación **todavía no existía**: la introduce su propio GREEN;
3. y, dentro de las reaprobaciones, **dos casos que la operación no pudo registrar**: la de la **enmienda B2**
   (respondió `state incoherent` nombrando `transition_key None`, y `--supersedes` con cualquier clave falló
   `does not name an existing specification approval`) —**ése es el defecto B3, medido con la operación
   rechazando su propia transición**— y la de la **enmienda B3** (el arreglo **todavía no estaba
   implementado**, así que la operación la habría rechazado igual; quedó declarada como la **última transición
   manual por esa causa**).

Los **6 scripts de registro propios** del ciclo anterior (005-013, `debt.md:65-69`) dejan de ser necesarios: el
ciclo de esta feature se registró con el CLI, y los cuatro casos manuales restantes son **de apertura/contrato**
(anteriores a que la operación exista para la feature) o **el defecto que la propia operación ahora corrige**.

## 7. Desviaciones e incidentes (todas declaradas en su momento)

1. **T3: fixture defectuoso en el RED, detectado en el GREEN.** De 8 focales, uno citaba un documento de
   cierre que su fixture **nunca escribía**. El implementer **se detuvo** (no editó el test, no fabricó
   digests) y probó la implementación aparte; el test-writer corrigió **sólo la precondición** del fixture
   (`016405f`, +14 líneas, **0 aserciones tocadas**) y el gate se aprobó **después** de la entrega: la
   separación **entrega ≠ gate** (PD-4) se ejerció de verdad.
2. **Dos digests escritos mal a mano y corregidos** (evidencia de por qué existe esta unidad; ver `debt.md` §5).
3. **El commit externo `da3612a`** (`state: sync .cdad-state.json checkpoint (HB 14 Oct)`) escribió el state
   **fuera del flujo del ciclo**. El state quedó válido y la transición se registró después; queda como
   evidencia de la clase de escritura que la unidad reemplaza.
4. **El ADR no tiene `artifact_kind` en la tabla cerrada del producto** (los kinds del scribe son
   projectbrief/systemPatterns/activeContext/progress): la entrega del scribe se recibió por partes para los
   dos documentos admitidos y **el ADR se materializó aparte**, declarado (misma práctica que en 005-013).
5. **`review_status` no se escribió a mano:** es el campo derivado sin dueño de la **deuda D-2**; el veredicto
   queda durable en `review.md` y en la entrada `review` del state.
6. **Un error de recepción** en el discovery (un `artifact_kind` fuera de la tabla cerrada): el recibo inválido
   **no aprobó nada**, se preservó en `.cdad/local/` y se rehizo la recepción con el descriptor correcto sobre
   **los mismos bytes**.
7. **Serialización del review-fix:** el `active_packet` es único, así que los dos RED del review-fix fueron
   secuenciales (no paralelos); el GREEN de T1 precedió al RED de T2 por la misma razón.

## 8. Criterio de aceptación de la feature

Un ciclo representativo registrado **sólo** con la operación nueva, **sin editar el state a mano**, con el CLI
real sobre un proyecto descartable (**AC-1** ✅), más el caso de la **entrega tardía** (**AC-2** ✅) y el de la
**repetición tras una interrupción** (**AC-3** ✅), y el cierre que **comprueba entregas y aprobación antes de
aplicar** y tiene salida cuando el despacho no vuelve (**AC-4** ✅). El único control nuevo es la comprobación
del cierre, y es el que **elimina** el `completed` fabricado. **La meta numérica es orientación, no umbral.**

## 9. Estado del epic y límites declarados

`epic-005-real-operation` sigue **abierto** (`features-loop`) con **13/13 unidades cerradas** y **ninguna en
cola**. **No se cierra el epic acá:** quedan el **gate de saneamiento antes de publicar**
(`execution.md:65-73`: rutas personales absolutas e ids crudos en archivos versionados), el **despliegue** de
005-013 y 005-012 (reservado al dueño) y la decisión del dueño. **El proyecto queda en reposo.**

**Límites declarados (no verificados, no presentados como verificados):** la operación **no existe en la
versión instalada** hasta el despliegue (deuda D-4); la mitad «árbol» de INV-7 (snapshot completo del árbol,
más allá del state byte a byte idéntico) no se asertó; la consecuencia de D-12 no es reproducible en un
fixture nuevo; el número de invocaciones de un ciclo **real** (no de fixture) sigue desconocido; y el ahorro
de trabajo manual se mide por los scripts que dejan de necesitarse (§6), no por una cifra de tiempo.
