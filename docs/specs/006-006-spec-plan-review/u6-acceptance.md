# 006-006 U6 — recorrido de aceptación real (PD-13)

Status: recorrido del orquestador bajo la delegación HITL amplia del owner (2026-10-20). Producto: la copia de HOME desplegada desde HEAD `a276531` (U1–U5 incluidas), excepto en E7, que usa la copia del producto dentro del proyecto descartable. Runtime: OpenCode v2.0.32 en modo server, por el adaptador instalado. Proyecto **descartable**: un worktree del repo con `.cdad` copiado y un estado propio. Nunca HOME como proyecto ni el proyecto activo. Las rutas del host se reemplazaron por `<walk>`.

## Resultado por escenario

| Escenario | Resultado | Evidencia (salida real) |
|---|---|---|
| **E1** spec sin plan | Cumple | `prepare ... --object-kind spec` ⇒ rc=0. Paquete 005 con `form: spec` y `purpose` «draft spec for review», contrato `f5dfaa44…`. Despacho real ⇒ recibo con `semantic_status: pending`. `materialize` ⇒ `docs/specs/006-006-spec-plan-review/plan-review.md`, sha `1ab12d0c…` igual al del part. El dictamen nombra el objeto y el digest `f5dfaa44…` («verified»). |
| **E2** spec + plan | Cumple | La forma `plan` aplica sus checks al plan: sin `plan-tasks` ⇒ rc=2 «missing the required plan-tasks block»; luego, sin `integration_gate` ni `owner` ⇒ rc=2, uno por campo. Con el plan completo ⇒ rc=0, paquete 007. El contrato fija `sha256 030d6286…` (plan) y `spec_sha256 f5dfaa44…` (spec), ambos iguales a `sha256sum`. `inputs` trae los dos documentos, cada uno con su `purpose`. El dictamen materializado (sha `8e5a3c03…`, igual al part) nombra los dos digests. |
| **E3** borrador de otra feature | Cumple | Con la ejecución de A y el contrato `docs/specs/999-draft-b/spec.md` ⇒ rc=0, `feature_id` = A, `contract.path` = B. Un target en `docs/specs/999-draft-b/` ⇒ rc=2, «outside the allowed root for artifact_kind 'plan-review' ('docs/specs/006-006-spec-plan-review/')», y la carpeta de B queda solo con `spec.md`. Un target en la carpeta de A ⇒ sha `63057e32…`, igual al part. El dictamen nombra `docs/specs/999-draft-b/spec.md` y `fca9954b…`. |
| **E4** re-review por digest | Cumple; hallazgo **W-1** | Tras editar el borrador: `REQUEST.contract.sha256` = `f5dfaa44…` y `sha256sum` = `95671114…`, distintos ⇒ la revisión preparada no cubre los bytes nuevos. Con bytes sin cambiar (el borrador restaurado) el digest coincide (`f5dfaa44…`). **W-1:** el paquete viejo (preparado, nunca despachado) no se puede sustituir. `prepare` ⇒ rc=2 PD-4 «active packet … is 'prepared'». `disposition` ⇒ rechazo «only a dispatched packet can be dispositioned». `prepare --replace-packet` ⇒ rechazo PD-2 «plan-review subphase requires a draft-plan contract: an approved contract is not the object this procedure reviews». Rodeo del recorrido: restaurar los bytes y despachar el paquete vigente. **Corregido** (RED `4f755ac`, GREEN `de629b8`): `--replace-packet` ahora reemplaza un paquete de borrador preparado, y la re-review se prepara con el digest nuevo. Verificado con `tests/test_006_006_w1_replace_draft_packet.py` y en el recorrido real tras el despliegue del cierre (ver abajo). |
| **E5** el dictamen no aprueba | Cumple | El estado no tiene ninguna entrada con `approved_by` que nombre el borrador. El recibo queda `pending`. `prepare --role test-writer` con el borrador como contrato ⇒ rc=2 «draft-plan contract is reviewer-only». La autorización de `materialize` lleva `approval_effect: false`. |
| **E6** coherente que no alcanza la intención | Cumple (juicio semántico) | Borrador B: la intención exige mantener `--out` como alias durante una versión, y PD-2 lo quita. El dictamen dice «BLOCKING · Bucket: h, `spec.md:11`, conflicting with lines 4 and 7» y propone un remedio estructural. La evidencia es el texto del dictamen (`plan-review-b.md`). |
| **E7** compatibilidad entre revisiones | Cumple | (i) `prepare` con la copia del producto del proyecto descartable ⇒ rc=0, paquete 008, substage `9a2311d2…`. (ii) El substage vuelve a su forma previa a U2 (`af0b1144…`). (iii) Despacho real y recepción con la copia ya cambiada ⇒ `termination: blocked`, «the receive flow failed: ERROR: packet differs from its canonical rendering (validate-packet)». (iv) Salida declarada en `re-entry.md` (U3): terminarlo bajo la revisión con la que se publicó, o preparar uno nuevo bajo la vigente. No se ejecuta: el producto no la ofrece. |
| **U5** dos revisiones y A→B→A (PD-9) | Cumple (por tests) | Los recorridos los ejecuta el CLI real en proyectos sintéticos, dentro de `tests/test_006_006_u5_exemption_record.py`: 5 casos de recorrido verdes, y el focal completo da 14 passed. No se repitieron a mano. La selección de vigencia B/C de la errata B-5 la verificó la review de etapa 4 con las transiciones reales (`review.md` O-1: «selected_only_B= True excludes_A= True … selected_only_C= True excludes_A_and_B= True»); su automatización queda como deuda. |

## Hallazgos

| Id | Clase | Estado |
|---|---|---|
| W-1 | un paquete `plan-review` preparado y no despachado no se puede reemplazar: `--replace-packet` valida contra el contrato aprobado y rechaza el `draft-plan` (PD-2), y `disposition` solo admite paquetes despachados; tras editar el borrador, el usuario queda sin salida para la re-review (E4) | corregido (`4f755ac`/`de629b8`); informes `w1-red.md`/`w1-green.md` |
| W-2 | el adaptador termina con rc=0 incluso con `termination: blocked` (E7); el diagnóstico va en la salida JSON | observación, no se cambia |

## W-1 tras el despliegue del cierre

CLI desplegado en HOME (`86cb942`), en el mismo proyecto descartable:

```text
prepare e1-w1a rc=0
006-006-spec-plan-review-reviewer-plan-review-009
aa83c8a854d41a6980786f6202efd9656d06bb4e1997ab4ceab449bf9bc517db  docs/specs/006-006-spec-plan-review/draft-e1.md
replace rc=0
prepare e1-w1b rc=2
ERROR: active packet '006-006-spec-plan-review-reviewer-plan-review-010' is 'prepared': complete or fail it before preparing a new packet (PD-4)
006-006-spec-plan-review-reviewer-plan-review-009 f5dfaa449a35492e63d62164ab8653c4c313bc5ade87cf3f6d5d658ea6857153
010 aa83c8a854d41a6980786f6202efd9656d06bb4e1997ab4ceab449bf9bc517db spec reviewer plan-review
```

Se prepara el paquete 009 sobre el borrador (`f5dfaa44…`) y se edita el borrador (`aa83c8a8…`). `--replace-packet` da rc=0 y publica el reemplazo 010, que fija el digest nuevo `aa83c8a8…` con forma `spec`. El `prepare` siguiente da rc=2 por PD-4, porque 010 ya es el paquete activo: es lo esperado.
