**Dictamen: 6 hallazgos Required / BLOCKING. No recomiendo cerrar todavía 004-002.**

Revisión independiente, familia Codex frente a implementers DeepSeek. Rango: `d57d678ec4b653bda86d72fca07918f0f1f1c9f9..94032c36985b95eef1224881f1d136785e183805`. La spec coincide con `f72e6540…b57c`. No reabro las limitaciones aceptadas por el dueño.

**F1 — Required · Verdict: BLOCKING · Bucket: h — Reconciliación con publicación parcial.**  
Ubicación: [cdad_packet.py:1675](<repo>/skills/cdad-cycle/scripts/cdad_packet.py:1675). PD-5/PD-11, invariante 7.
`_publish_owned_atomically` reemplaza primero el contexto y después el state. Si falla el segundo `os.replace`, elimina temporales pero no revierte el primero; `committed` nunca se utiliza para recuperación.
Sonda en memoria del helper real, inyectando `OSError` únicamente al reemplazar state: `cannot publish reconciliation` y resultado **`context=NEW, state=OLD`**.
La operación informa fracaso dejando aceptada parcialmente la revisión. Los cinco puntos actuales de interrupción no ejercitan esta ventana.
**Remedio:** publicación recuperable de ambas generaciones, con journal y recuperación o rollback; verificar también error y muerte entre renombrados.

**F2 — Required · Verdict: BLOCKING · Bucket: h — El contexto admite otra política bajo el hash aceptado.**  
Ubicación: [cdad_packet.py:560](<repo>/skills/cdad-cycle/scripts/cdad_packet.py:560). PD-1/PD-5/PD-7.
El validador comprueba que el snapshot sea base64, pero no su digest ni su correspondencia con `path_policy`; el historial tiene la misma debilidad.
Sondas independientes conservando el hash de la política real: sustituir el snapshot por base64 de `not policy JSON`, o sustituir `path_policy` por `{"test_roots":["scripts"]}`. **Ambas pasan `_validate_v2_execution_document` y `_ensure_policy_reconciled`.**
Así, un contexto inconsistente puede producir scopes y derivados ajenos a la política cuyo hash acredita.
**Remedio:** validar digest, esquema y clasificación desde los bytes del snapshot; contrastarlos con los campos redundantes y verificar cada revisión histórica.

**F3 — Required · Verdict: BLOCKING · Bucket: h — Normalización desigual permite eludir exclusiones concretas.**  
Ubicaciones: [cdad_packet.py:248](<repo>/skills/cdad-cycle/scripts/cdad_packet.py:248), [claude-code-path-guard.sh:177](<repo>/scripts/claude-code-path-guard.sh:177). PD-2/PD-8, P-1 e invariante 3.
Dos reproducciones:
- Políticas con `private_paths=["./tests/private"]` o `["tests//private"]` son válidas, pero clasificar `tests/private` devuelve **`test`**. Con `["tests/private"]` devuelve **`private`**. Son rutas simples, no globs de mejor esfuerzo.
- Guard real, rol implementer, herramienta Write: `.opencode/agents/cdad-implementer.md` → **rc=2**; `.opencode//agents/cdad-implementer.md` → **rc=0**. Solo invoqué el guard: no ejecuté ninguna escritura.
El clasificador normaliza el candidato, mientras esas exclusiones comparan otra representación.
**Remedio:** canonicalizar entradas y candidatos consistentemente, o rechazar representaciones no canónicas; aplicar también al veto de derivados.

**F4 — Required · Verdict: BLOCKING · Bucket: h — Scopes incompletos para tests exactos y co-ubicados.**  
Ubicaciones: [cdad_packet.py:905](<repo>/skills/cdad-cycle/scripts/cdad_packet.py:905), [cdad_packet.py:646](<repo>/skills/cdad-cycle/scripts/cdad_packet.py:646). PD-7/PD-12; criterio 2.
`_default_scopes` del test-writer solo contempla `test_roots`:
- Política válida con únicamente `test_files=["check.py"]` → **`KeyError: 'test_roots'`**.
- `test_roots=[]`, tests co-ubicados bajo `src` con sufijo `_test.go` → **write_scope vacío**.
- Intentar scope explícito `{"class":"colocated-tests","root":"src"}` → **`scope selector is not classified as colocated-tests`**: clasifica el directorio como implementación, aunque contiene tests autorizados.
La matriz de layouts no demuestra que el paquete permita trabajar sobre esos tests.
**Remedio:** derivar todos los tipos declarados y validar scopes co-ubicados como conjuntos filtrados, sin conceder implementación.

**F5 — Required · Verdict: BLOCKING · Bucket: h — Reconciliar habilita sobrescribir derivados modificados.**  
Ubicación: [cdad_packet.py:2128](<repo>/skills/cdad-cycle/scripts/cdad_packet.py:2128). PD-8/I9.
El control de modificaciones retorna inmediatamente cuando el manifiesto corresponde a otra revisión de política, precisamente el caso posterior a reconciliar.
Sonda del helper real con manifiesto y archivo en memoria: mismo derivado modificado → **REJECTED** con política anterior; **ACCEPTED** con política nueva. La preparación posterior reemplaza ese archivo sin resolución explícita.
**Remedio:** comprobar integridad contra el manifiesto anterior antes de regenerar; separar integridad del derivado y vigencia de su política.

**F6 — Required · Verdict: BLOCKING · Bucket: h — I8 registra identidades sin validar el paquete.**  
Ubicación: [cdad_packet.py:1856](<repo>/skills/cdad-cycle/scripts/cdad_packet.py:1856). PD-6/I8 y rechazo de documentos inválidos.
Registro verifica `request.execution_id`, pero no `request.packet_id`, rol/subfase ni correspondencia con `PACKET.md`.
Sonda sobre el flujo real, sustituyendo únicamente el REQUEST leído por una copia en memoria con `packet_id="different-packet"` y `role="NOT-A-CDAD-ROLE"`: llega a publicación un registro para **review-015 con `NOT-A-CDAD-ROLE`**. Lock y publicación fueron sustituidos por destinos inertes; no hubo escrituras.
**Remedio:** validar identidad y metadatos canónicos antes de registrar, preservando los reintentos históricos legítimos. No equiparar registro de observaciones con autorización para despachar.

**Optional · Verdict: OPTIONAL · Bucket: h — Precisar dos afirmaciones documentales.**  
[project-execution.md:131](<repo>/skills/cdad-cycle/references/project-execution.md:131) incluye “listing” en la barrera verificada, mientras `t7-live-walk.md §4` registra listado permitido.  
[ADR-012:28](<repo>/docs/adr/ADR-012-politica-limites-por-proyecto.md:28) no delimita claramente por runtime la ausencia de barreras edit/write/grep/glob. La guía sí distingue esas limitaciones. Corregir la descripción, sin ampliar mecanismos.

**Cobertura del contrato y riesgos para 004-003**

| Garantía | Resultado de esta revisión |
|---|---|
| PD-1/2/5/6/7/8 | Contradicciones F1–F6. |
| PD-3/4/9/10 | Evidencia documental/tests inspeccionados; sin nuevo defecto confirmado aquí. |
| PD-11 | F1 muestra una ventana no cubierta por los cinco puntos declarados. |
| PD-12 | F4 limita consumidores válidos; instalación no reproducida aquí. |
| PD-13 | Cierre integral aún no acreditado: el ledger termina con un intento de scribe anulado. |
| Criterios 1/2/7 | Insuficientes para cierre por los defectos y la cobertura indicada. |
| Criterios 3/4/5 | Evidencia histórica disponible; no reejecutada integralmente. |
| Criterio 6 | **138 hashes históricos OK; 0 ausentes; 0 distintos.** |
| Criterio 8 | Guía inspeccionada; flujo instalado no reproducido. |

Para 004-003: no asumir que hash y scopes concuerdan, que los defaults habilitan todos los layouts, ni que un registro I8 acredita la identidad íntegra del encargo. Los cambios de política requieren resolver F1/F5 antes de depender de recuperación y regeneración.

**Evidencia de ejecución**

- `git log --oneline -- docs/specs/004-002-project-execution-bootstrap/`: primer commit `bcaf296`; base su padre `d57d678`.
- `sha256sum docs/specs/004-002-project-execution-bootstrap/spec.md`: coincide íntegramente.
- `bash -n scripts/claude-code-path-guard.sh install.sh`: rc=0.
- Sondas `python3 -B` con heredocs completos registrados en las llamadas: resultados detallados arriba; AST de **32 Python modificados OK**.
- `git status --porcelain`: vacío antes y después. **Archivos modificados: ninguno. Commits creados: ninguno.**

## Abstentions

- **Verdict: ABSTAIN · Bucket: h:** no ejecuté pytest, staging ni instalación: sus fixtures escriben archivos y este encargo lo prohíbe expresamente. Los **329 passed** corresponden al registro histórico en `5b14f0e`, no a una corrida mía.
- **Verdict: ABSTAIN · Bucket: h:** no repetí sesiones runtime, concurrencia real ni mediciones de rendimiento. Las sondas transaccionales en memoria no equivalen a pruebas de integración con procesos.
- No leí el archivo privado ni accedí a las instalaciones globales.