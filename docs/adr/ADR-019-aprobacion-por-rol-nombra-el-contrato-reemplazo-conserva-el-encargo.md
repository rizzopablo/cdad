# ADR-019 — La aprobación de contrato por rol nombra el contrato; el reemplazo de paquete conserva y corrige el encargo anterior

* Estado: **Aceptado** (2026-10-09; orquestador bajo delegación HITL de epic-005)
* Fecha: 2026-10-09
* Decisores: dueño (Pablo, instrucción del 2026-10-09); orquestador bajo delegación HITL de epic-005
* Confianza: **Media**

## Contexto y enunciado del problema

El arranque de una feature tenía una **circularidad I2**: el **architect** —que redacta la
spec— necesitaba una spec aprobada para que `prepare` lo habilitara, y la spec no existía
todavía. El orquestador la esquivó con una entrada provisional `specification` que también
habilitaba a test-writer/implementer: un atajo que otorgaba autoridad a roles que no debían
tenerla. Al corregirlo (T1), el registro de aprobación de spec se **pineó** con
`contract_sha256`; pero quedaron dos huecos que el dueño mandó cerrar antes del cierre
(**enmienda T-CORR**, 2026-10-09):

1. **C1 — la ruta de la aprobación.** Un `sha256` correcto con otro `contract_path` (o sin
   `contract_path`) seguía habilitando: una aprobación copiada de otra feature cuyo contenido
   coincidía por casualidad, o una entrada sin pin de ruta, autorizaban un contrato que **no
   nombraban**. El pin de hash no bastaba para decir **qué** se aprobó.
2. **C2 — la conservación en el reemplazo.** `--replace-packet` (T2) conservaba solo
   identidad/subetapa/objetivo y **recomputaba** los defaults de scopes/invariantes/entrega,
   de modo que un paquete obsoleto no se podía **corregir** al reemplazarlo: el encargo
   anterior se perdía. Un paquete preparado y nunca despachado cuyo contrato cambió quedaba
   sin salida útil.

## Impulsores de la decisión

- Que la autoridad de un rol sea **la del contrato correcto**: hash **y** ruta.
- Que un paquete obsoleto y no despachado pueda **reemplazarse** conservando el encargo
  anterior y corrigiéndolo de forma explícita, sin reabrir identidad ni contrato.
- Que ninguna operación **invente** autorización: el reemplazo publica solo con la aprobación
  vigente del contrato del día.
- Que el reemplazo siga siendo **atómico y auditable**: el paquete anterior byte a byte, una
  traza durable de qué se conservó, qué cambió y por qué.
- Que la disciplina de rol no se degrade: los pisos obligatorios del rol no se pueden quitar.

## Opciones consideradas

1. **C1 — seguir exigiendo solo `contract_sha256`.** Rechazada: un hash coincidente con otra
   ruta habilita autoridad indebida; el pin no nombra lo aprobado.
2. **C1 — exigir `contract_path` sin pin de hash.** Rechazada: pierde la protección de PD-4
   (editar la spec invalidaría la aprobación sin que el pin lo note).
3. **C2 — recomputar defaults y aceptar solo rol/subetapa/objetivo (versión previa de D4).**
   Rechazada: no permite corregir el encargo de un paquete obsoleto; el encargo anterior se
   descarta.
4. **C2 — conservar el `REQUEST.json` anterior campo a campo y aplicar correcciones explícitas
   sobre él** (elegida): mantiene el encargo atómico pero corregible; el centinela `-`
   distingue «opción no dada» (conserva) de «lista vacía» (reemplaza por vacío); los pisos
   obligatorios del rol se re-agregan siempre.

## Decisión

1. **La aprobación de spec nombra el contrato (C1/PD-18/INV-8).** Una entrada `stage_history`
   `specification` habilita a los roles de construcción **solo** si su pin nombra el contrato
   verificado: `contract_path == contract["path"]` **y** `contract_sha256 == sha256`. Un
   `contract_sha256` correcto con `contract_path` distinto (o ausente) → `approval pending`,
   nombrando el path **registrado** y el **esperado**, sin efectos. El enforcement vive en
   `validate_request`; el architect sigue habilitándose por `epic_history` `stage: "epic-plan"`
   **sin** pin (D2).
2. **El reemplazo conserva y corrige el encargo (C2/PD-19..PD-24/INV-7; D4 enmendada/D7).**
   `--replace-packet <id> --reason` sobre el `active_packet` `prepared` con obsolescencia
   verificable re-resuelve el contrato del día y publica el sucesor **solo** con la aprobación
   vigente (PD-11). Sin opciones de corrección, conserva campo a campo el `REQUEST.json`
   anterior (`execution_id, role, substage, objective, inputs, read_scope, write_scope,
   invariants, expected_output, evidence_required`) y **no** recomputa defaults. Las opciones
   `--input/--read-scope/--write-scope/--invariant/--expected-output/--evidence` reemplazan la
   lista/campo **entero** (centinela `-` como único valor → vacío; `-` mezclado → rc=2); los
   pisos obligatorios del rol se re-agregan siempre (PD-21). Las correcciones pasan las mismas
   validaciones que un `prepare` normal (PD-22); el argv mezclado se rechaza (PD-23). El
   paquete anterior queda byte a byte idéntico (INV-3) y `.superseded.json` conserva
   `conserved_fields`/`changed_fields` disjuntos y exhaustivos (PD-24). Ninguna operación
   escribe aprobaciones (INV-2).
3. **Los bloqueos son distinguibles y accionables (PD-12):** `approval pending`,
   `packet obsolete` y `state incoherent`, mutuamente excluyentes por condición, con el
   registro/falta concreto y la acción siguiente.

## Consecuencias

- **Positivas:** la autoridad de rol queda atada al contrato correcto (hash **y** ruta); el
  paquete obsoleto y no despachado se recupera conservando y corrigiendo el encargo; la
  recuperación es auditable (dos `REQUEST.json` + traza de conservación/cambio + `reason`); el
  CLI sigue determinista, read-only sobre el producto y nunca aprueba (ADR-003 intacto).
- **Negativas / límites declarados:** pinear la spec obliga a **re-registrar** la aprobación
  cuando sus bytes cambian (pasó con la enmienda T-CORR: el sha derivó y la entrada previa
  quedó superada, PD-4); la superficie de corrección agrega casos de validación. **B3 (media,
  decisión del dueño):** la raíz v7 viva quedó fuera de sync para `cdad_packet.py` (sin C1 ni
  `--replace-packet`) → un `prepare` despachado por ella reintroduciría la circularidad I2;
  re-sincronizar es reservado al dueño. **B2:** PD-17 literal (reemplazo del paquete del
  architect tras editar el plan del epic) se ejecuta ajustado sobre el paquete del test-writer;
  la semántica del architect (contrato sin pin) queda sin test focal (mismo code path).
  **B4/B5/B6/B7** (opcionales, ver `debt.md`).

## Alternativas y trabajo futuro

Cerrar B2 (bloque S5-arch o enmienda de PD-17); extender `_reject_absent_contract_without_approval`
a «la entrada nombra el path y el archivo falta» (B4); ampliar la tabla de flags foráneos del
test de PD-23 (B5); asertar un token real del motivo en PD-22 (B6); reescribir los mensajes de
test heredados del RED (B7); re-sincronizar la raíz v7 (B3, dueño); que `prepare` resuelva la
raíz adoptada sola.

## Confianza

**Media.** C1 y C2 están verificadas por tests focales (30 passed) y por la **prueba decisiva
PD-17** end-to-end, con control positivo interno en cada negativo y suite completa 629 passed.
La confianza no es alta porque el reemplazo del paquete del **architect** no tiene test focal
(B2), la raíz v7 viva no corre la corrección (B3, decisión del dueño) y el gate es una suite
local sin CI.

## Enlaces

- Spec/plan: `docs/specs/005-001-idle-and-v7-bootstrap/{spec,plan}.md` (PD-18..PD-24; D4
  enmendada, D7; enmienda T-CORR 2026-10-09)
- Evidencia: `docs/specs/005-001-idle-and-v7-bootstrap/{review,debt,dispatch-ledger}.md`
- Referencia operativa: `skills/cdad-cycle/references/project-execution.md` §2 y §8
- ADR relacionados: ADR-003 (el orquestador materializa artefactos), ADR-011 (autonomía
  supervisada), ADR-012 (política de límites por proyecto), ADR-013 (contrato de plan borrador
  que no aprueba), ADR-014 (recepción/materialización/aprobación separadas)
