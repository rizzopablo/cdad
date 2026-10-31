# Revisión v2 recibida — decisión de compatibilidad pendiente

Registro de supervisión, no normativa ni aprobación del contrato.

La revisión independiente de `spec.md` v2 (SHA-256 `8d2b948e2fd596ce1298c036423e5c8b91d905396bba26e8dc6a8df6571a4517`) está en `plan-review.md`; la revisión anterior se conserva íntegra en `plan-review-v1.md` (SHA-256 `2c38d9dcc28e084986e7bc5258f58f3732258400bb7b609d10bd2cda27babbd5`).

Fuente: FINAL TEXT de sesión `<session>`, mensaje `msg_18afba2ad001kvVav26f27NPjU`, obtenido mediante `session.messages`. Registro del transporte ya realizado: packet `010-004-packet-dispatch-ergonomics-reviewer-plan-review-003`, continuidad intento entero 6. No se repitió begin ni dispatch. El runtime no acreditó la sesión: faltaban parent/moment; no se inventaron esos datos. La recepción valida identidad/paquete, pero no demuestra por sí misma procedencia de sesión ni aprueba contenido.

Dictamen: B-1/B-2 cerrados; N-1 BLOCKING; O-A/O-B OPTIONAL. N-1 identifica una incompatibilidad de la promesa C/v1 con el verificador publicado, que solo carga v2.

## Decisión que corresponde a Pablo

¿Debe C admitir contextos v1?

- (a) C v2-only, rechazando v1 con diagnóstico explícito de contexto y preservando A para v1. Recomendación acotada de supervisión: simplifica y reutiliza el verificador existente sin ampliar sus consumidores; implica recortar la promesa de C y requiere decisión del owner.
- (b) Mantener C/v1 mediante comparación canónica del paquete contra el contexto seleccionado, sin cambiar el verificador compartido. Alternativa si Pablo necesita esa compatibilidad.

No se elige ninguna alternativa. No preparar otro architect antes de la decisión; tampoco implementar ni abrir TDD. La tensión plan/observaciones de §2.1 sigue pendiente para aprobación del owner.

O-A sugiere aclarar dominio/identidad/schema en `validate_request`, distinguiendo igualdad de ruta en los tres CLI y C. O-B sugiere etiquetar o separar evidencia de encargo como no normativa. Son opcionales, no autorización para ampliar alcance.

## Evidencia de recepción

- Recibo: `.cdad/runtime/results/exec-010-004-packet-dispatch-ergonomics-001/010-004-packet-dispatch-ergonomics-reviewer-plan-review-003/receipt.json`.
- SHA-256 del recibo: `d23433dcf9f0d01ef8bd984abbadaa6cacf5281ad5e2ca1a95ef8b534b21c011`.
- SHA-256 FINAL TEXT: `7a1f0e90f8c12605153fdce587937e2199424f36a3c3c23ebb5fd83efc0f1e13`.
- `semantic_status: pending`; `approval_effect: false`. Spec no aprobada; etapa specification retenida.

Sin implementación, tests, push ni nuevos spawns. El discovery 010-000 ajeno permanece intacto y fuera de este commit.
