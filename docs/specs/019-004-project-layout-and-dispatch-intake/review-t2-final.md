# Revisión focal T2 — 019-004

**T2 no debería considerarse cerrado ni iniciarse T3 todavía.** La enumeración ampliada funciona en los casos focales examinados, pero queda una incompatibilidad con la sección 4.2 para un directorio `.cdad/packets/` vacío.

## Hallazgo

### Un directorio `packets` vacío se trata como evidencia de ambigüedad

**Severidad: Required · Verdict: BLOCKING · Bucket: h**

La especificación aprobada enumera como evidencia «cualquier entrada **bajo** `.cdad/packets/`» (§4.2). Sin embargo, `skills/cdad-cycle/scripts/cdad_layout.py:229` comprueba la existencia del directorio mismo, aunque esté vacío.

La consecuencia es que un proyecto sin entrada alguna en `packets` puede rechazarse como ambiguo y no recibir la propuesta de bootstrap prevista para un proyecto sin inicializar. No considero aceptable mantenerlo solo como comportamiento conservador: la enumeración aprobada es cerrada y distingue las entradas de sus directorios contenedores.

**Cierre verificable:** comprobar las entradas de `.cdad/packets/`, no solo la existencia del directorio, y verificar que un directorio vacío no cause ambigüedad mientras que una entrada real sí la cause. Si se quiere conservar la interpretación más restrictiva, requiere una modificación explícita del contrato.

## Resultado de la comprobación focal

- Las tres ubicaciones añadidas —`inbox`, `runtime/results` y `publication`— producen ambigüedad cuando contienen entradas. Los tests focales también cubren paquetes y registros de ejecución no operativos.
- Los registros de `continuity` y `guards` por sí solos resuelven como proyecto sin inicializar.
- Los ejemplos probados de contenido no nombrado no producen ambigüedad.
- La precedencia de ambos marcadores legacy exactos y del locator registrado se mantiene en los casos probados.
- Los tests comprueban ausencia de escrituras en los rechazos focales. Esto no acredita exhaustivamente todos los comandos o caminos posibles.
- El hallazgo anterior sobre la exclusión de `continuity` y `guards` queda cerrado frente al **contrato enmendado**.

## Evidencia

- Route C: `validate-request` y `validate-packet` finalizaron sin error; la identificación generada mediante `render --route C` coincidió con la recibida.
- Commit de implementación revisado: `593a213cda3b99ff321fbadaae2471660c362a13`. HEAD observado: `89bfe0167ff13ec558c7432e36b81551f16e66f8`.
- Verificación ejecutada:

  ```text
  PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider tests/test_019_004_ambiguity_enumeration.py tests/test_019_004_receipt_reanchor_ambiguity.py tests/test_019_004_continuity_gap_ambiguity.py tests/test_019_004_layout.py
  ```

  Resultado: `68 passed in 93.69s`.

- No modifiqué archivos ni creé commits. `docs/.cdad-state.json` ya aparecía modificado al comenzar y seguía así al terminar.
- Suite completa no realizada: se ejecutó la selección focal indicada; sus resultados no acreditan toda la suite.

## Abstentions

- No acredito exhaustivamente todos los consumidores del layout ni todos los caminos de materialización y rechazo.
- No acredito la reconciliación integral de la tabla de decisiones con los ADR.
- No evalúo el cierre integral de intake ni las instrucciones instaladas fuera del alcance T2 solicitado.