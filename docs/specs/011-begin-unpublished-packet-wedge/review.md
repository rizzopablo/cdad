# review.md — 011-begin-unpublished-packet-wedge

## Veredicto (4 campos)
| Campo | Valor |
|---|---|
| Blocking | 0 |
| Optional | 2 |
| Abstentions | 1 |
| Resultado | Sin hallazgos bloqueantes. PC-1..PC-5 verificadas. La decision de aceptar es del dueno. |

## Verificacion por PC
| PC | Evidencia | Resultado |
|---|---|---|
| PC-1 | test_011_begin_en_v2_sin_request_ni_rastro_se_rechaza_sin_efectos: rc, diagnostico, inventario y bytes de cabeza. En fb743245 falla por asercion de contrato (rc=0), no por entorno. | Cumple |
| PC-2 | test_011_tras_rechazo_prepare_begin_y_verify_begin_ok: rechazo, prepare, begin y verify-begin por CLIs publicos. | Cumple |
| PC-3 | test_begin_legado_sin_arbol_de_paquetes_se_acepta sobre 87a16432. | Cumple |
| PC-4 | test_pc07_begin_identico_repetido_es_replay_sin_efectos cubre rc y ausencia de efectos, no no_op. Sonda desechable en v2: no_op True, cabeza e inventario intactos. | Cumple; cobertura parcial (F1) |
| PC-5 | test_begin_con_request_ausente_y_rastro_de_publicacion_se_rechaza. Sonda en v2 con rastro y sin REQUEST: rc!=0, diagnostico de rama incomplete, arbol intacto. | Cumple |
| INV-1 | Discriminador exec_context.get("schema_version") == 2 (cdad_continuity.py:1258), del documento. _load_execution_context lo conserva. | Cumple |
| INV-2 | _admit_packet corre en _plan_write antes del enlace y de la escritura, despues del replay (cdad_continuity.py:1113). | Cumple |

Criterio 3: regresion focal verde, 116 passed incluidos los dos casos nuevos.
Barrido adicional (no exigido): 17 archivos con begin, 194 passed. No sustituye la suite completa.

## Hallazgos
### F1 — PC-4 no fija no_op en un test permanente (Optional, bucket m)
tests/test_008_004_packet_enforcement.py:524. El test del replay de begin comprueba rc y ausencia de efectos, no no_op == true. Comportamiento correcto segun sonda; si no_op regresara, el llamador recibiria un replay sin marcar, sin efecto duplicado en disco. Cierre: anadir asercion o registrar deuda.

### F2 — PC-5 sin caso v2 explicito (FYI/Optional, bucket l)
tests/test_008_004_packet_enforcement.py:692. La rama es independiente de version y la sonda en v2 paso. Sin consecuencia de usuario nombrada: deferred-hardening.

## Abstenciones
- A1: suite completa no corrida (deuda declarada de la spec). El barrido cubre solo archivos que emiten begin.
- No se contrasto la tabla de decisiones contra docs/adr/ (fuera del read_scope). El diff no introduce decisiones nuevas.
- Discrepancia con el audit: test-audit.md afirma que _RecoveryProject es v1, pero en ejecucion es v2 (la asercion de precondicion de _v2_execution_context pasa). Los tests corren en v2, como PC-1 exige; la afirmacion del audit es incorrecta.

## Comandos
render rc=0; cmp con PACKET.md identico; sha256sum de spec coincide; git show 87a16432 y fb743245; pytest 6 archivos focales 116 passed; pytest 17 archivos con begin 194 passed; git archive fb743245 pytest -k test_011 2 failed por asercion; sonda replay v2 y PC-5 v2 2 passed; git status sin cambios propios.
