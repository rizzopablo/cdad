## Dictamen

Objeto: `docs/specs/999-int-draft/spec.md`  
SHA-256 verificado: `3527d8f820a602d7cbe2effc66cd611fea7bb5b4d75af6dd2d7fad1a58060d88`.

**1 BLOCKING · 1 OPTIONAL.** El borrador requiere resolver el contrato observable indicado abajo antes del RED. Este dictamen no constituye aprobación.

### 1. Required — El único resultado conservado tiene semántica incompleta

**Verdict: BLOCKING · Bucket: m**

**Procedencia:** `docs/specs/999-int-draft/spec.md:4-7`; `skills/cdad-cycle/scripts/cdad_packet.py:6781-6791,6851-6854,7203-7205`.

La intención elimina la salida y conserva únicamente el código de retorno, pero PD-1 no define qué significa «estado válido», ni el resultado para estados inválidos o información desconocida.

Esto importa porque actualmente `status` puede registrar problemas en `unknowns` y devolver rc=0. No equivale a `validate-state`. Silenciar esa proyección sin resolver la semántica del código puede hacer indistinguibles, para un consumidor automatizado, un estado operativo y uno con información faltante. Tampoco queda decidido si «no imprime nada» incluye stderr ante errores.

**Movimiento propuesto:** fijar una matriz mínima de comportamiento para éxito, información incompleta y errores: criterio aplicable, rc y contenido permitido en stdout/stderr. Puede preservar el comportamiento existente o cambiarlo; esa elección corresponde al dueño, no al test-writer.

**Condición de cierre:** el contrato permite derivar expectativas inequívocas para esos casos, incluido el comportamiento sin `--quiet`, sin inventar qué valida `status`.

### 2. Nit — La tabla de decisiones no está alineada con los ADR disponibles

**Verdict: OPTIONAL · Bucket: m**

**Procedencia:** `docs/systemPatterns.md:9-38`; regla de contraste en `skills/cdad-cycle/references/stage-4-review.md:64-68`.

La fila de `docs/systemPatterns.md:38` declara vigente `docs/adr/ADR-901-no-existe.md`, pero el archivo no existe. El contraste también detectó ocho ADR sin fila: ADR-012, 016 y 025–030.

Es una inconsistencia documental comprobada; no demuestra por sí misma un defecto funcional de `--quiet`, por lo que no bloquea este borrador.

**Condición de cierre:** reconciliar las filas con los archivos existentes, sin inventar decisiones ni estados. ADR-034 se aplicó como criterio; no hay evidencia de que este cambio necesite una abstracción adicional.

## Abstentions

- No se juzga el funcionamiento de una implementación de `--quiet`: el objeto revisado es una especificación anterior al RED.
- No se acredita independencia de familia respecto del autor: el paquete no identifica su modelo.

## Evidencia

Comandos de identidad ejecutados:
```sh
sha256sum docs/specs/999-int-draft/spec.md docs/cdad-policy.json
git status --short
git rev-parse HEAD
```

Resultados:
- Digest del borrador: coincide con el contrato.
- Digest de política: `f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711`.
- HEAD observado: `0dc28f2038d5af89105767d2021348c61efaedf0`.
- Estado inicial y final: ` M docs/.cdad-state.json`; cambio preexistente, no modificado por esta revisión.
- Contraste read-only mediante Python entre filas de la tabla y `docs/adr/*.md`: un archivo referenciado ausente y ocho archivos sin fila.
- Lecturas y búsquedas focales: borrador completo, decisiones, referencias canónicas, tests existentes y código de `status`. Sin ejecución de tests ni suite completa.

**Archivos modificados:** ninguno. **Commit creado:** ninguno.