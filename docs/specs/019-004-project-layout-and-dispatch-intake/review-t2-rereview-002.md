# Re-review T2 — 019-004

**Resultado: T2 no puede considerarse cerrado bajo la especificación aprobada; no recomiendo iniciar T3 todavía.** La búsqueda de gap-report y el rechazo de layouts ambiguos en los comandos de continuity examinados corrigen los dos caminos señalados en la revisión anterior. Sin embargo, la nueva definición de evidencia insuficiente deja una excepción material frente al contrato.

## Hallazgo

### Los registros de continuity y guards quedan excluidos de la evidencia de ejecución

**Severidad: Required · Verdict: BLOCKING · Bucket: h**

La especificación aprobada, §4.2, indica que los **registros de ejecución o paquetes bajo `.cdad/`**, sin layout admitido, producen un diagnóstico de ambigüedad. En cambio, `_execution_record_evidence()` en `skills/cdad-cycle/scripts/cdad_layout.py` excluye por nombre los directorios `continuity` y `guards` bajo `.cdad/executions/<id>/`, sin examinar sus registros.

Por tanto, un proyecto que solo contiene esos registros se considera no inicializado: puede continuar operando y, en el camino de bootstrap, proponerse como nuevo en vez de requerir aclaración. La decisión registrada explica por qué se desea conservar ese comportamiento, pero no cambia la especificación aprobada ni concilia su texto con la excepción.

**Cierre verificable:** hacer que esos registros produzcan ambigüedad conforme a §4.2 y ajustar las expectativas afectadas, **o** elevar al titular una modificación explícita del contrato que excluya esos registros y defina sus consecuencias para bootstrap y continuity. Después, verificar ambos comportamientos con fixtures que contengan únicamente cada tipo de registro.

## Cierre de los hallazgos anteriores

- **Continuity:** las correcciones incorporan la comprobación previa para `checkpoint-receipt`, `reanchor`, `resume` y `trigger`, además de los comandos ya cubiertos. La evidencia focal ejercita rechazo sin escritura y controles legacy y registrado para receipt/reanchor. El hallazgo anterior queda **parcialmente cerrado**, sujeto a la excepción de clasificación anterior.
- **Gap-report:** la revisión del cambio y los tests focales respaldan que ya no selecciona `docs/` ante evidencia insuficiente. **Cerrado en el alcance examinado.**
- **Decisiones sobre continuity y guards:** coherentes con las necesidades expresadas por los fixtures, pero no acreditadas como compatibles con la redacción vigente de §4.2.

## Evidencia

- Route C: `validate-request` y `validate-packet` finalizaron con código 0; la identificación renderizada coincidió con la recibida.
- Comando ejecutado:

  ```text
  PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider tests/test_019_004_receipt_reanchor_ambiguity.py tests/test_003_004_t2_reviewfix.py tests/test_016_002_gap_report.py tests/test_003_004_t3_trigger.py
  ```

  Salida: `21 passed in 35.26s`.

- Commits examinados: `86f70fe1`, `9afb0cd1`, `a3ca8c0a` y `b3646afe`.
- No modifiqué archivos ni creé commits. Al comenzar, `docs/.cdad-state.json` ya figuraba modificado.
- No ejecuté la suite completa; el resultado anterior corresponde únicamente a la selección indicada.

## Abstentions

- No acredito exhaustivamente todos los consumidores del layout ni todos los caminos de materialización.
- No acredito la reconciliación integral de la tabla de decisiones vigentes con los ADR.
- No evalúo el cierre integral de intake ni de las instrucciones instaladas fuera de este re-review focal.