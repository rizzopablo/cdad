# Decisión del orquestador — review T4 (003-007)

Informe: `review-t4.md`, recibido con `cdad_result receive` (receipt `824a575d…`) y
materializado sin cambios. Sin bloqueantes. El RED se reprodujo (7/3), una mutación del texto
derriba 4 tests y `make agents` es idempotente.

| Hallazgo | Decisión |
|---|---|
| F-1: `continuity.md` perdió la mención del no-op del checkpoint idéntico (P6) | **Se corrige ahora** con un review-fix de una línea (implementer). Es solo documentación, no se regenera nada, no corre gate. **T4 queda cerrada** con ese commit. |
| F-2: señal `r"plan"` no discrimina | Deuda baja (`T4-F2`). Solo la usa el test de coherencia, que es simétrico. |
| F-3: F011/A3 | Preexistentes (deuda ANON-1 de 003-006 y copias de HOME). |
