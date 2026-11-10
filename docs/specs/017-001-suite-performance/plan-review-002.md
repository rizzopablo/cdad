# Revisión focal del borrador 017-001 v2

**Dictamen: recomiendo corregir un bloqueante antes de presentar el borrador para aprobación.** La decisión corresponde al dueño; esta revisión no aprueba la spec ni autoriza la implementación.

Documentos efectivamente leídos:

- `docs/specs/017-001-suite-performance/spec.md` — SHA-256 `581f96b2a84f1bc383171ced289bf741621c1ceea68a8c387b7f8579cfb1273b`
- `docs/specs/017-001-suite-performance/plan.md` — SHA-256 `93ca1cb3280bb4a0f8abc713f9f51e04d989985e8fdee3b03d0e9d7c1ff11e47`

## Hallazgo

### El plan exige cumplir el objetivo serial antes de poder considerar el paralelismo

**Severidad: Required · Verdict: BLOCKING · Bucket: m**

**Ubicación:** `spec.md:350-361,400`; `plan.md:133-176,341-382`. Contrato de referencia: `docs/epics/epic-017-suite-performance/plan.md:29-35,59-64` y `discovery-decisions-2026-11-07.md:9-12`.

PC-8 exige que la preparación serial satisfaga por sí sola el objetivo que el dueño fijará después de la base. T5 debe demostrar ese resultado antes de entregar su producto; T6, que decide si explorar paralelismo, depende de T5. El plan incluso declara que decidir «sin paralelismo» no dispensa del objetivo serial.

La decisión registrada pide **optimización serial primero** y permite considerar paralelismo si el costo residual lo justifica y se demuestra seguridad. No exige que el objetivo final ya esté alcanzado antes de considerar esa alternativa. Si el dueño fija un objetivo razonable que la mejora serial no alcanza, pero queda costo residual susceptible de paralelización segura, el plan se detiene en T5 y nunca permite evaluar T6. La restricción introduce una condición de aceptación más fuerte que la decisión registrada y puede impedir alcanzar el resultado previsto por el epic.

**Corrección propuesta y cierre verificable:** separar la obligación de ejecutar y medir primero la optimización serial de la obligación de alcanzar el objetivo final. Permitir que T6 reciba el resultado serial medido, incluso si aún no alcanza el objetivo, y evalúe la alternativa condicionada por utilidad y seguridad. La aceptación debe seguir exigiendo el objetivo acordado y todas las garantías; si el dueño desea que sea obligatoriamente serial, debe registrar expresamente esa decisión. Verificar que un resultado serial insuficiente pero medido pueda llegar a la decisión de T6 sin autorizar paralelismo inseguro.

## Comprobación de los hallazgos anteriores

1. **Medición antes de la base: cerrado en el borrador.** La spec exige registrar operaciones comprometidas, observar preparación real dentro de `call`, calibrar todos los intervalos comprometidos y declarar desconocidos y su regla de decisión antes de consumir la base (`spec.md:195-237,297-319`). T2 y T3 producen la calibración y la comprobación de entrada.
2. **Primera tarea despachable: cerrado en el borrador.** T1 identifica resultado y consumidor, responsables, rutas, comprobaciones observables, focales, regresiones y gate (`plan.md:29-62,210-277`). T1–T3 separan fases, operaciones y contabilidad en entregas rechazables por separado.
3. **Identidad de ambos documentos: lectura identificada.** Esta revisión nombra ambos hashes. El despacho fija contractualmente el de la spec; el orquestador debe verificar que el gate fije **ambos hashes aquí informados** antes de presentar la pareja para aprobación.
4. **ADR-040 ausente del índice: continúa como opcional previamente registrado.** No observé que altere este borrador; corresponde al mantenimiento del índice, no bloquea esta corrección.

## Evidencia y límites

- Ruta C: `validate-request` y `validate-packet` finalizaron sin errores; `render --route C` produjo la identificación recibida.
- Comprobaciones ejecutadas: `sha256sum docs/specs/017-001-suite-performance/{spec,plan}.md`, `git status --short`, `git diff --name-only` y `git rev-parse HEAD`.
- HEAD observado: `1abb717232ab3d0a9cbdf096f08ec9d1a9d84854`. El estado mostraba `docs/.cdad-state.json` modificado.
- No ejecuté tests ni suite completa: esta es una revisión de borrador, no una acreditación de implementación o rendimiento.
- Archivos modificados por esta revisión: **ninguno**. Commit creado: **ninguno**.

## Abstentions

- No puedo determinar qué preparación dominará el costo, qué reducción será alcanzable ni si el paralelismo será útil y seguro: faltan la base y la evidencia correspondientes.
- La fijación de ambos documentos en el gate y su aprobación posterior corresponden al orquestador y al dueño; esta revisión no acredita que ya hayan ocurrido.
