# Decisión del orquestador sobre review-t1 (2026-10-06)

Familia única: el guard trata «no observado» como dato. Remedio de clase, una sola ronda.

- **B1** (token ausente ⇒ incidente fabricado): token ausente/no-string ⇒ señal desconocida ⇒ sin incidente (o marcador `unknown`). Se corrige.
- **B2** (entrada fuera de contrato con rc=0): `classify` valida `trace=="trace-v1"`, `schema_version==1`, `entries` lista; archivo/JSON ilegible ⇒ rc≠0 con diagnóstico, sin traceback ni salida parcial. Se corrige.
- **B3** (huella sin canonicalizar): se elige la **opción (b)**, la proporcional al MVP. La canonicalización es responsabilidad del grabador y queda declarada en el contrato `trace-v1` (nota en el schema y docstring). `REPETITION_RULE` deja de afirmar que canonicaliza.
- **O1** (poll sin condición ⇒ `wait`): misma familia. Se incluye: decisión `unknown` / `justified: false`.
- **O2, O3a, O3b, O3c:** a deuda priorizada, baja.

## Re-review (2026-10-06) y cierre de T1

B1, B3b y O1 quedaron cerrados. B2 se cerró en su contrato, con un residuo F1: un archivo que no es UTF-8 produce un traceback crudo. Aun así falla cerrado (rc=1, stdout vacío, sin salida parcial). Decisión del orquestador, según el criterio MVP: no rompe el camino feliz ni fabrica un resultado, así que **pasa a deuda (media)** y se agrupa con O2/O3 para una pasada de endurecimiento de entrada al cierre de la feature. Lo mismo para F2 (token `""` tratado como observado: baja). **T1 cerrada.**

## Deuda T1
- Media: F1, traceback ante un archivo no UTF-8 (agregar `UnicodeDecodeError` al `except` + un focal).
- Baja: F2 (token vacío), O2 (validar los fixtures contra el schema), O3a/b/c (nits y nombres).
