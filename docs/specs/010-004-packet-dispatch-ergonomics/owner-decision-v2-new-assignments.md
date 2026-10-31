# Decisión owner: encargos nuevos v2; v1 para retomar lo viejo

2026-10-30. Fuente: instrucción explícita de Pablo, transmitida por el orquestador supervisor a esta sesión: «V1 solo debe conocerlo cdad para retomar un proyecto viejo, pero todo lo nuevo va sobre v2».

Resuelve la elección N-1 de `plan-review.md` v2 y la pregunta de `orchestration-review-v2-decision-pending.md`: C será v2-only. Todo encargo NUEVO y toda preparación nueva serán v2, también al continuar un proyecto viejo. No es aprobación de la spec completa, de implementación ni de la tensión plan/observations de §2.1. Etapa specification; spec no aprobada. No autoriza migración automática, eliminación de soporte de reentrada ni reescritura/renombrado/destrucción del legado v1.

La compatibilidad v1 queda estrictamente en reconocimiento, validación y reentrada de proyectos viejos bajo las condiciones existentes; render/validación/replay históricos no son permiso para preparar encargos nuevos v1. El architect precisará esa frontera con evidencia, sin bloquear silenciosamente la reentrada. Si se necesita un encargo nuevo v2, citará el procedimiento existente y los requisitos de autoridad/pin explícitos; si faltan, diagnosticará legacy/approval pending/state incoherent con la continuación accionable que corresponda, sin fabricar autoridad ni inventar un protocolo de migración.

## Delta que debe precisar el architect (no implementación)

El canon actual sí permite prepare v1: `skills/cdad-cycle/scripts/cdad_packet.py`, `_select_execution` (2928–2942), devuelve contexto v1 cuando no existe policy; `prepare` lo consume (6202) y publica binding v1 (6433). El borrador v2 conserva esa posibilidad. La decisión cambia esa regla para TODA preparación nueva; no basta con recortar C. Contrastar también argumentos explícitos y vías de recuperación, sin convertir replay byte-identical en preparación nueva.

El procedimiento existente `references/project-execution.md` §§2–4 exige autoridad y bootstrap v2, contempla `--new-execution` ante contexto previo y `--resume-packet` para reemisión byte-identical; prohíbe adoptar v1 hacia adelante mediante contexto explícito. Identificar sus condiciones y cualquier laguna real: una decisión general de producto no constituye por sí sola el pin/autoridad de cada proyecto viejo. No se ejecuta transición de autoridad aquí.

Encargo acotado: corregir N-1, promesas/PCs/matriz y wording que permitía prepare v1; mantener cierres B-1/B-2, I-4/I-5 y gates. O-A: aclarar checks compartidos de dominio/identidad/schema frente a igualdad de ruta en los tres CLI y C, sin ampliar consumidores. O-B: separar o etiquetar evidencia del encargo como no normativa conservando los hechos originales. Ningún hardening ni alcance nuevo.

## Trazabilidad y conservación

Revisión v2: `plan-review.md`, N-1 BLOCKING; O-A/O-B OPTIONAL. Recibo terminado del reviewer `010-004-packet-dispatch-ergonomics-reviewer-plan-review-003`; continuidad intento 6, head seq 12 cerrado, reconcile `already-closed`, sin repetir transporte. Se conservan todos los registros anteriores, incluida la pregunta histórica pendiente (resuelta ahora, no borrada), revisión v1 e incidente. La recepción de una futura revisión no aprobará la spec.

Expansión de estado: necesaria para localizar el contexto activo y registrar esta decisión sin alterar autoridad. Se preparará solamente un nuevo packet architect draft sobre la ejecución v2 actual; sin begin ni dispatch por esta sesión subagente. Próximo intento esperado 7, que el supervisor debe congelar y verificar inmediatamente antes del transporte.
