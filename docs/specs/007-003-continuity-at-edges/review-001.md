# Review de etapa 4 — 007-003-continuity-at-edges (2026-10-24)

Dictamen: **NO APTO**. Tres BLOCKING reproducidos por CLI.

## BLOCKING 1 — se autoriza transporte sobre historia no demostrable
`cdad_continuity.py:1012-1033`. `verify_begin()` obtiene `chain` pero ignora `chain["demonstrable"]`; un ancestro legado sin `prev` interrumpe la demostración sin excepción. Reproducido: cuerpo legado sin `prev` → `begin(attempt=2)` → `verify-begin --attempt 2` devuelve rc=0 y `seq=2`. Incumple §2.1 y §2.3.1, y permite transportar algo cuyo cierre posterior rechazará por no demostrable.
**Cierre:** exigir demostración completa antes de acreditar el `begin`, conservando la lectura compatible de legados; rechazo sin efectos con diagnóstico.

## BLOCKING 2 — la actualización de evidencia sustituye identidad sin conservar antecedente
`cdad_continuity.py:784-796`. El merge comprueba que el antecedente exista, no que corresponda a la identidad invalidada ni que conserve su referencia; tampoco exige antecedente al sustituir una entrada vigente. Dos reproducciones rc=0: invalidar `a` (referencia A) con referencia B y antecedente de A; sobrescribir `a` vigente con referencia B sin antecedente. Incumple §2.5, PC-06 e INV-7.
**Cierre:** validar la transición contra la entrada antecedente; conservar la identidad de la evidencia invalidada; exigir trazabilidad en sustituciones (identificador nuevo y antecedente).

## BLOCKING 3 — abrir continuidad rompe el replay de un registro durable anterior
`cdad_packet.py:3357-3398`. `provenance.continuity="absent"` se recalcula desde la presencia actual. Reproducido: registrar sin continuidad (rc=0) → `begin` (rc=0) → repetir el registro idéntico ⇒ rc=2 «already exists with different observation data». Incumple la excepción de replay durable (§2.2, PC-02).
**Cierre:** conservar el diagnóstico histórico al reconocer una repetición, sin recalcularlo; una observación realmente distinta sigue rechazándose.

## Resto
`d531839` no relaja oráculos. Suite específica 6 passed; los hallazgos son variantes no cubiertas. No se certificó la suite completa.

## Re-review (2026-10-24): 3 BLOCKING cerrados, 1 subsistente

- Cerrados: historia no demostrable en `verify-begin`; identidad de la evidencia; replay durable.
- **BLOCKING subsistente:** `_evidence_history()` incorpora entradas de `chain["links"]` sin comprobar `chain["demonstrable"]` (`cdad_continuity.py:724-750,808-815`). Reproducido: `begin` con evidencia → convertir el cuerpo en legado sin `prev` → `checkpoint` que invalida con antecedente sobre ese cuerpo ⇒ rc=0, publica `seq=2`. Una invalidación cuyo antecedente es inadmisible no debe acreditarse.
- Regresión: 140 passed.
