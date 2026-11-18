# Revisión del borrador 004

**Objeto:** `docs/specs/019-002-effective-discovery-instructions/verification-strategy-draft-004.md`  
**SHA-256:** `5ccfc69e58667907a0db2b37f9df2c6628c16472602cc95c8ceb1315d12b94f5`

## Hallazgos bloqueantes

No identifiqué hallazgos bloqueantes con la evidencia examinada.

La propuesta distingue verificación ejecutable y semántica, contempla compromisos mixtos y preserva la exención explícita de revisión. La autoaplicación requiere autorización expresa y no presenta el borrador como dispensa de las obligaciones actuales.

## Hallazgo no bloqueante

### La tabla de decisiones vigentes no refleja todos los ADR presentes

**Verdict: OPTIONAL · Bucket: h · Severity: Optional/Consider**

La comparación de `docs/systemPatterns.md:5` con `docs/adr/` encontró once archivos ADR sin fila en la tabla: 012, 016, 025–030 y 037–039. No encontré filas que apunten a archivos ausentes.

Esto es una desalineación preexistente del índice, no una contradicción demostrada introducida por el borrador. **Acción propuesta:** reconciliar la tabla con los ADR y sus estados, sin agregarla como alcance incidental de 019-003.

## Dictamen y límites

No identifiqué una necesidad de reintroducir lectores de comprensión, ejercicios de contexto mínimo, checklists previos a producción ni cuotas de pruebas. La secuencia propuesta reconoce que debe actualizar los pines después del reingreso y detenerse ante un rechazo; **no queda acreditado que las transiciones futuras vayan a tener éxito**.

Esta revisión no aprueba el borrador ni autoriza implementación. La decisión corresponde a la autoridad aplicable.

## Abstentions

- **Secuencia operativa:** no ejecuté `validate-unit-contract`, suspensión, apertura ni reanudación; sus resultados futuros dependen del estado y los pines al momento de ejecutarlos.
- **Cobertura de consumidores:** no hice un inventario exhaustivo de consumidores efectivos ni certifico que los controles de distribución seleccionados en el futuro sean suficientes.
- **Decisiones vigentes:** comprobé la correspondencia de nombres entre la tabla y el directorio, pero no contrasté íntegramente el contenido de todos los ADR con el borrador.
- **Tests:** no ejecuté pruebas ni suite completa; se trata de una revisión de un borrador documental.

## Evidencia

- Ruta C: `validate-request` y `validate-packet` finalizaron sin diagnóstico; `render --route C` reprodujo la identificación recibida.
- `sha256sum docs/specs/019-002-effective-discovery-instructions/verification-strategy-draft-004.md` produjo el digest indicado.
- `git rev-parse HEAD` produjo `5da46516c1736a30ef19df65a7e8a7a5691f4959`.
- `git status --short` mostró la modificación preexistente `docs/.cdad-state.json`.
- **Archivos modificados por esta revisión:** ninguno. **Commit creado:** ninguno.