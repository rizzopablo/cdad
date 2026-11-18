# Revisión independiente del plan de recuperación

**Dictamen: un hallazgo bloqueante.** Los dos hallazgos de la revisión anterior quedan cerrados **en el borrador**. La ejecución y aceptación del producto siguen pendientes. Esta revisión no aprueba los documentos ni autoriza implementación.

Objetos revisados:

- `recovery-plan.md` — SHA-256 `7d4fcec1604d1d8f5dd7421dd93def4cd7b82ae253c0bff49f786245e6f46cc8`
- `recovery-spec.md` — SHA-256 `55a4e571731607d258b56c10d3d84acf29ddf86fb52aa145cde23a5fe733ba45`

## Hallazgo

### Required — La ruta para ejecutar las instrucciones candidatas sigue sin resolverse

**Verdict: BLOCKING · Bucket: m**

- **Evidencia:** `recovery-spec.md:81–95` exige una sesión real con instrucciones candidatas, publicaciones nuevas, versiones efectivas recuperables y una evaluación independiente. El plan asigna esa ejecución a T8 (`recovery-plan.md:273–302`), pero no identifica cómo el runtime consumirá las instrucciones candidatas sin instalarlas. La incertidumbre ya estaba documentada explícitamente en el plan anterior (`plan.md:60–66`); el nuevo contrato continúa excluyendo instalación y despliegue (`recovery-spec.md:138`).
- **Consecuencia:** Se puede terminar la producción y llegar a T8 sin una vía autorizada para ejecutar el candidato. Una sesión que cargue instrucciones instaladas distintas no demostraría PC-7, aunque produzca una transcripción aparentemente satisfactoria.
- **Cierre verificable:** Antes de comprometer la ejecución de T8, identificar y contrastar una ruta concreta que cargue los artefactos candidatos y permita recuperar sus versiones efectivas sin instalación no autorizada; o declarar expresamente esta incertidumbre, su responsable y la condición de resolución previa a T8. Si la única ruta viable requiere instalación, detener esa parte y solicitar autoridad separada. La suficiencia de la verificación se juzga conforme a `stage-2-specification.md` §“Verification strategy per promise”.

## Disposición de los hallazgos anteriores

1. **PC-4, cardinalidad:** cerrado en el borrador. `recovery-spec.md:53–61` limita la promesa a la clase de artefacto y a la entrega normal de un informe por cada adaptador; ya no promete rechazar globalmente múltiples partes. Los adaptadores inspeccionados construyen normalmente una parte y derivan su clase de la tabla compartida. La implementación y sus pruebas aún deben demostrar el resultado comprometido.

2. **PC-3, corrección formal:** cerrado en el borrador. `recovery-spec.md:39–47` separa la presentación corregida del original recibido y del destino canónico registrado, conserva la atribución y exige contrastar la repetición de la materialización. La ruta propuesta concuerda con el comportamiento inspeccionado en `cdad_result.py:967–1002`; no se ejecutó una repetición real.

## Evidencia y límites

- **Categorías de cierre del producto:** PC-1 a PC-7, **unable to verify / no ejecutados**. Se revisó la suficiencia del borrador, no un producto implementado.
- El contraste de la tabla de decisiones vigentes con `docs/adr/` no encontró rutas de ADR inexistentes; los ADR no listados inspeccionados están propuestos.
- **Validación de ingreso:** `validate-request` y `validate-packet` finalizaron sin salida ni error; `render --route C` coincidió con la identificación recibida y la comparación completa de `render` con `PACKET.md` dio `render_cmp=0`. Contexto de ejecución: esquema v2.
- **Comandos principales:** `python3 scripts/cdad_packet.py validate-request …`, `validate-packet …`, `render … | cmp - …`, `sha256sum` sobre ambos borradores, `git status --short`, `git rev-parse HEAD`, `git diff --quiet bc922c04 -- sources agents skills scripts tests install.sh build`, y búsquedas y lecturas acotadas. HEAD: `c29ef97cea79ebd603491f62dae99bed0bcf05f9`; comparación de superficies nombradas con la base: salida `0`.
- **Tests ejecutados:** ninguno; revisión previa a producción. No se acredita una suite completa.
- **Archivos modificados y commits creados por esta revisión:** ninguno. El estado observado ya contenía una modificación del archivo de estado y documentos de recuperación no rastreados.

## Abstentions

- No establecí qué runtime concreto puede cargar todas las instrucciones candidatas sin instalación; esa incertidumbre fundamenta el hallazgo.
- No ejecuté la entrega multiparte, la repetición de materialización ni el ejercicio con agentes reales.