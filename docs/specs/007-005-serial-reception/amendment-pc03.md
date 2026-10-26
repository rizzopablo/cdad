# Enmienda 2026-10-26 — PC-03: sustitución contractual retrospectiva autorizada

## Motivo

PC-03 exigía que `verify-begin` se ejecutara «inmediatamente antes del único despacho». Esa
redacción supone que verificación y transporte ocurren en la misma sesión. En un despacho entre
proyectos no lo hacen: el orquestador verifica en su sesión y el transporte lo ejecuta una sesión
raíz en el proyecto consumidor. Los registros del producto no capturan el intervalo de reloj entre
ambos, así que el requisito, tal como estaba escrito, **no es observable** y deja la PC pendiente
aunque la moneda esté demostrada.

## Sustitución (no dispensa)

El `begin` verificado es el `begin` vigente en el despacho si y sólo si:

1. `verify-begin` devuelve el `seq` y el `body_sha256` del `begin`;
2. el cierre de recibo (`checkpoint-receipt`) tiene `prev.seq = seq` y
   `prev.checkpoint_sha256 = body_sha256`;
3. no existe otro checkpoint entre ambos.

Esta condición **no es equivalente ni más estricta** que el texto original. Conserva la garantía de
**identidad y adyacencia lógica** (el cuerpo verificado es el predecesor inmediato del cierre) y
**elimina la garantía temporal** (que la verificación haya ocurrido poco antes del transporte). Una
verificación antigua seguida mucho después por el despacho y el cierre, sin checkpoints intermedios,
satisface esta condición y no el texto original.

Por eso se registra como **sustitución contractual retrospectiva autorizada**, no como cumplimiento
del requisito original. La autoridad delegada acepta la sustitución; el requisito temporal no se
cumple y se declara **no observado**.

## Evidencia de la unidad

- `06-verify-begin.json`: `seq 16`, `body_sha256 dedb50df…`.
- `05-begin.json`: `seq 16`, el mismo `body_sha256`.
- Cuerpo del cierre (seq 17): `prev.seq 16`, `prev.checkpoint_sha256 dedb50df…`.
- No hay cuerpos intermedios: la cadena va de 16 a 17.

## Efecto

PC-03 se lee, desde esta enmienda, con la condición 1–3, y **sólo bajo el contrato enmendado**: el
requisito original de inmediatez temporal no se cumple. La captura temporal pasa a límite declarado
del expediente. **No se repite el recorrido** para fabricar la captura.

**Aprobada por:** Orquestador CDAD (HITL delegada del dueño), 2026-10-26.
