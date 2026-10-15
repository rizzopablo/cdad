# Deuda registrada: segunda mirada de 004-002 (2026-10-03)

Fuente: `review-second-look.md` (Codex gpt-6-astra, review-015).

**Decisión del dueño (Pablo):** se registran como deuda y se continúa hasta un
MVP; con estos defectos, el camino feliz sigue siendo viable. Prioridades de
la evaluación del orquestador:

| # | Defecto | Afecta el camino feliz | Prioridad |
|---|---|---|---|
| F4 | `_default_scopes` del test-writer solo contempla `test_roots`: con solo `test_files` da KeyError; los tests co-ubicados (p. ej. Go `_test.go`) quedan con write_scope vacío y el scope explícito se rechaza | **Sí**, en layouts sin `tests/` separado (Go). No afecta a este repo | **Alta**: resolver antes de usar v2 en un proyecto Go o co-ubicado |
| F3 | Normalización desigual: las entradas privadas no canónicas (`./x`, `x//y`) se aceptan pero no clasifican como privadas, y el guard deja pasar `.opencode//agents/...` (rc=0; el orquestador lo reprodujo) | No (es un rodeo; lo detecta la auditoría con `git diff`) | Media: rechazar o canonicalizar de forma consistente |
| F2 | El contexto v2 no valida que el snapshot de la política corresponda a su `policy_sha256` ni al `path_policy` redundante | No (requiere un contexto alterado a mano) | Media |
| F6 | `--record-dispatch` no valida `packet_id`, rol ni subfase contra el paquete | No (requiere un request inconsistente) | Media |
| F5 | Tras reconciliar, el control de integridad de los derivados se saltea y un derivado editado a mano se sobrescribe | No (requiere una edición manual más una reconciliación) | Baja |
| F1 | `_publish_owned_atomically` no revierte el contexto si falla el reemplazo del state, y la reconciliación queda publicada a medias | No (requiere un error de disco entre dos renombrados) | Baja |
| Doc | La guía §7 incluye "listing" en la barrera verificada (t7-live-walk §4 registra el listado como permitido); ADR-012:28 no delimita por runtime | No | Baja |

Destino: backlog de endurecimiento de la ejecución v2, a planificar con
004-003 o en una feature propia. F4 se vincula con el principio de
generalidad (Go, ciclos sin código).
