# Deuda y observaciones — 005-001-idle-and-v7-bootstrap

Registrada al cierre de la review formal (stage 4, `review.md`), 2026-10-09.
Los hallazgos opcionales no prolongan el ciclo (calibración de la review,
`references/stage-4-review.md`); se registran aquí con su disposición.

## Opcionales de la review

- **B2 (OPTIONAL, m) — PD-17 literal vs. escenario ajustado.** La prueba decisiva
  edita la spec y reemplaza el paquete P1 (test-writer); el texto literal de
  PD-17 declara editar el plan del epic y reemplazar el paquete del architect.
  El ajuste fue **instruido por el dueño** (2026-10-09: «el paquete del architect
  se recibe y se completa antes de preparar al test-writer, y el reemplazo se
  prueba con un paquete todavía preparado y no despachado») y queda registrado
  aquí y en el `dispatch-ledger.md` (fila 13). Queda sin test la semántica
  específica del architect (contrato `approved-epic-plan` **sin pin de hash**,
  D2). Disposición: **deuda**; si el dueño quiere cerrarla, la vía es un bloque
  S5-arch en `test_005_001_t4_decisive.py` o una enmienda de PD-17.
- **B4 (OPTIONAL, l) — Contrato con pin de path correcto pero archivo borrado.**
  `cdad_packet.py` cae al diagnóstico genérico «cannot read contract» en vez de
  `approval pending` (rc=2 sin efectos; invariantes intactos). Cierre: extender
  `_reject_absent_contract_without_approval` a «la entrada nombra el path y el
  archivo falta».
- **B5 (OPTIONAL, l) — PD-23 cubre 7/15 flags foráneos** en el test; el
  mecanismo `_reject_mode_mix` es una familia única y en runtime cubre los 15
  (verificado por lectura). Cierre: ampliar la tabla del test.
- **B6 (OPTIONAL, l) — Oráculo débil en PD-22:** la regex de motivo se satisface
  con el texto propio del wrapper. Cierre: asertar un token real del motivo.
- **B7 (OPTIONAL, l) — Mensajes de test heredados de la época RED** («hoy emite
  el error genérico… (defecto reportado)») que hoy describen un defecto ya
  corregido. Cierre: reescribir esos mensajes.

## Observación de gate — raíz v7 viva vs. repo (B3, decisión del dueño)

`sha256(skills/cdad-cycle/scripts/cdad_packet.py)` del repo ≠ el de la copia de
la raíz v7 adoptada (`$HOME/.cache/cdad-adopted-ce09ed0/.config/opencode/…`): la
raíz viva **no** corre C1 ni `--replace-packet`. Los demás scripts
(`cdad_continuity`, `cdad_result`, `cdad_guard`) sí coinciden, y el manifiesto de
agentes v7 está OK (11/11). Re-sincronizar/activar la raíz es **reservado al
dueño** (spec §5, R3): el próximo despacho por la raíz v7 usaría un CLI sin la
feature. Cierre propuesto: registrar los dos shas en el ledger (hecho) y
re-sincronizar antes de 005-002.

## Observación — agentes de proyecto derivados de una fuente no-v7 (2026-10-09)

Al retomar, el manifiesto `.opencode/agents/.cdad-derived.json` apuntaba a
`~/.config/opencode/agents` (instalación de HOME, otra versión) en vez de la raíz
v7 adoptada: algún `prepare` anterior corrió sin `CDAD_OPENCODE_AGENTS_DIR`. El
CLI no fuerza la raíz adoptada registrada en `.cdad/activation.json`; un
orquestador que omita la variable publica agentes de otra versión **sin avisar**
(criterio 2 del epic). Disposición: corregido en esta sesión (todos los
`prepare` con la variable; el manifiesto volvió a la raíz v7). Queda como
candidato a mejora de producto (que `prepare` resuelva la raíz adoptada sola).
