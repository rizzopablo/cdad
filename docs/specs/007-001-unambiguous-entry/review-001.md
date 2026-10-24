# Review de etapa 4 — 007-001-unambiguous-entry

Dictamen: NO APTO. 3 BLOCKING reproducidos por CLI sobre fixtures temporales.

## BLOCKING 1 — fuentes malformadas se clasifican como aprobación ausente
Proveniencia: `skills/cdad-cycle/scripts/cdad_packet.py:7065-7073,7095-7125`; selectores `:1815-1824,1863-1865`. Incumple §2.3 S1/A1 e INV-4.
- `stage_history="corrupt"` → `approval_reference.status="ausente"`.
- `epic_history="corrupt"` → `approval_reference.status="ausente"`.
Remedio: comprobar interpretabilidad de las fuentes antes de S2/A2, sin cambiar predicados de autorización; emitir `desconocida` con diagnóstico.

## BLOCKING 2 — se pierden diagnósticos nuevos exigidos por el contrato
Proveniencia: `cdad_packet.py:7108-7118,7311-7319`; examen de pendientes `:6758-6765`. Incumple §2.1, §2.3 C2 y §2.4.
- Contrato eliminado: `desconocida` pero `unknowns` sólo trae el diagnóstico previo de versión.
- Sin `active_packet`, candidato con `REQUEST.json` = `{`: devuelve `execution-active` sin informar la ilegibilidad.
Remedio: recoger diagnósticos de resolución independientemente de la clasificación y agregarlos preservando los anteriores; no convertir un candidato ilegible en pendiente probado.

## BLOCKING 3 — el identificador seguro no garantiza confinamiento del request
Proveniencia: `cdad_packet.py:6812-6816,6854-6857`. Incumple §2.1 requisito 3.
Reproducción: request movido fuera del proyecto y reemplazado por symlink a los mismos bytes → `{"situation":"packet-prepared","approval":"vigente"}`.
Remedio: verificar confinamiento de la ruta resuelta antes de leer; rechazar escapes con diagnóstico de pertenencia, sin fallback.

## Evidencia
`pytest -q` sobre test_007_001 + 005-013 t1 + 005-011 t3 + 005-012 t5: 70 passed. La suite verde no cubre estas divergencias.

No identificados otros hallazgos materiales. No se modificó ningún archivo. No se ejecutó la suite completa.
