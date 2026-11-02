# 011 — Begin sobre paquete no publicado (wedge)

**Estado:** Approved by Pablo on 2026-11-01.

## 1. Descripcion

El orquestador, desde una ejecucion CDAD v2 valida con continuidad sana, intenta emitir un `begin` para un paquete aun no publicado. El sistema debe rechazarlo sin alterar la continuidad e indicar como preparar el paquete. Tras corregir la preparacion, el orquestador puede emitir un `begin` legitimo y acreditarlo con `verify-begin`.

Alcance: solo el arreglo preventivo 1. No repara ejecuciones ya bloqueadas ni elimina todas las causas de split-brain.

## 2. Contrato

**Definiciones**

- **Ejecucion v2:** el documento de ejecucion declara `schema_version == 2`.
- **Begin nuevo:** no es replay exacto acreditado en la cadena demostrable.
- **REQUEST publicado:** archivo `.cdad/packets/<packet_id>/REQUEST.json`. Su existencia no sustituye la verificacion canonica vigente.

**Promesa A — Rechazo preventivo sin bloquear lo legitimo**

- **PC-1.** En ejecucion v2, un `begin` nuevo cuyo `packet_id` no tiene REQUEST publicado se rechaza con `rc != 0`, aun sin rastro en el arbol de paquetes. El diagnostico nombra el `packet_id`, senala la ausencia de `REQUEST.json` e indica preparar con `prepare`. No crea ni modifica cuerpos y conserva los bytes de la cabeza (o su ausencia).
- **PC-2.** Tras el rechazo de PC-1, con la preparacion corregida, un `begin` legitimo da `rc == 0` y su `verify-begin` da `rc == 0`, sin reparacion manual.

**Promesa B — Compatibilidad**

- **PC-3.** Ejecucion no-v2 sin arbol de paquetes y precondiciones validas sigue admitiendo `begin` (`rc == 0`).
- **PC-4.** Replay exacto acreditado conserva exito (`rc == 0`, `no_op == true`), sin cuerpos nuevos ni cambio de cabeza.
- **PC-5.** Paquete con rastro pero sin `REQUEST.json` sigue rechazado antes de persistir, sin cuerpos nuevos ni cambio de cabeza.

Los paquetes publicados conservan la admision canonica vigente (REQUEST, texto del paquete, referencias protegidas).

## 3. Invariantes

- **INV-1 — Discriminador:** la exigencia v2 sale del documento de ejecucion (`schema_version == 2`), nunca del rastro del `packet_id`. La comprobacion de publicacion incompleta sigue aplicando.
- **INV-2 — Fail-closed:** ningun efecto persistente de un `begin` nuevo ocurre antes de su admision.

## 4. Criterios de aceptacion

1. Cada PC-1..PC-5 vinculada a evidencia automatizada. El caso nuevo de PC-1 falla antes del fix por asercion del contrato, no por entorno.
2. La evidencia compara inventario y bytes de cuerpos/cabeza antes/despues del rechazo y del replay; verifica rc, diagnostico y acreditacion posterior.
3. Verdes los casos nuevos y la regresion focal: `test_008_004_packet_enforcement.py`, `test_003_004_t2_writeahead.py`, `test_003_007_t2_checkpoint_vs_begin.py`, `test_003_004_t2_reconcile.py`, `test_007_006_withdraw_and_republish.py`, `test_008_003_lifecycle_decisions.py`.
4. Se conserva salida con comando, revision y resumen final. Por directiva del dueno, la suite completa **no es gate** de esta feature.

## Contexto tecnico

`C = skills/cdad-cycle/scripts/cdad_continuity.py`, `L = cdad_lifecycle.py`. Hueco en `C:1228-1259`; llamador con contexto en `C:1054-1055`, `C:1113-1118`; replay antes de admision `C:1090-1104`, orden en `L:433-460`; version conservada `C:359-379`, esquema v2 en `cdad_packet.py:2996-3015`; split-brain intacto `C:2297-2343`.

## Deuda declarada

- Suite completa no corrida (directiva del dueno); evidencia comprometida: regresion focal.
- Seguimiento 2 (unicidad por clave + reanudacion), 3-5 (recuperacion, autoridad, reanchor), ejecuciones ya bloqueadas y hash editorial: fuera.

Status: Approved by Pablo on 2026-11-01.
