# Decisión del orquestador — review T2 (003-007)

Informe: `review-t2.md`, recibido con `cdad_result receive` (receipt `b223c23a…`) y
materializado sin cambios. **T2 cerrada**: sin bloqueantes; gate acotado 60/60, reproducido
por el reviewer (40,7 s); seis sondas propias.

| Hallazgo | Decisión |
|---|---|
| R-1: un `begin` idéntico re-ejecutado tras un append de su misma clave da rc≠0 | **Opción (b): se enmienda la decisión, más deuda.** Falla cerrado, sin escrituras, y no es alcanzable en el flujo sancionado: tras el checkpoint hay receipt, y `begin` solo se emite antes de despachar. El no-op de `begin` vale cuando el head es ese mismo `begin`. `t2-record-decision.md` queda enmendada abajo. La redacción de `continuity.md` se corrige en T4 (mismo despacho del implementer). Deuda `T2-R1`: reconocer el body idéntico de la misma clave en `bodies/` para no-op. |
| O-1c: huérfanos con `record: "checkpoint"` (caída entre los dos fsync) invisibles | La frase de `continuity.md` se corrige en T4 para cubrir huérfanos del escritor actual. Dentro de la deuda `CKPT-FORK`. |
| Nit-1: un comando ≠ `begin` se etiqueta como `checkpoint` | Deuda baja (`T2-N1`): enum explícito con error. Hoy argparse solo admite dos comandos. |
| FYI-1: un `attempt` viejo apendea | Preexistente, sin acción; queda bajo la familia T1-N3. |
