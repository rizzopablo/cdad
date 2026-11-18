# Revisión independiente — 019-002

**Resultado: 3 hallazgos bloqueantes.** La decisión sobre su priorización corresponde al aprobador. La revisión se hizo contra `bc922c04..d415cc1b`; no aprueba la feature.

## Hallazgos

### 1. El cierre instruye producir el estado que acaba de declarar incoherente

**Required · Verdict: BLOCKING · Bucket: m**  
**Ubicación:** `skills/cdad-cycle/references/stage-5-merge.md:187`  
**Contrato:** PC-5, `spec.md:67–75`.

La misma instrucción dice primero “update state” a `done`/`null` y después que el reposo legítimo es `idle`/`null` y que `done`/`null` requiere diagnóstico. Un orquestador que siga literalmente el primer mandato deja el siguiente inicio en diagnóstico, en lugar de permitir abrir la unidad siguiente.

**Cierre verificable:** sustituir la instrucción de cierre por la transición existente que deja `idle`/`null`, sin conservar un mandato contradictorio; revisar la guía de cierre y el handoff de epic contra el comportamiento real.

### 2. La consulta opcional se vuelve obligatoria en instrucciones operativas

**Required · Verdict: BLOCKING · Bucket: m**  
**Ubicaciones:** `skills/cdad-cycle/references/stage-1-discovery.md:71`; `skills/cdad-cycle/references/stage-2-specification.md:9,17–25,29,33–36`; `skills/cdad-cycle/references/re-entry.md:230–239`.  
**Contrato:** PC-1 y PC-6, `spec.md:33,81`.

La regla principal hace condicional la consulta: cuando la incertidumbre o el juicio independiente la justifiquen. Sin embargo, la salida de Stage 1 ordena despachar *brainstorm*, Stage 2 vuelve a ordenar generar y entregar el paquete, y el handoff del borrador pide un resumen de esa consulta. Para una necesidad sencilla sin incertidumbre consecuente, la ruta detallada impone una consulta que el contrato no requiere y no ofrece una ruta clara de diálogo directo a borrador.

**Cierre verificable:** hacer condicionales las instrucciones de transición, reentrada y preparación del borrador de la misma familia; comprobar contextualmente tanto la ruta con consulta como la ruta sin consulta, manteniendo las decisiones recuperables y la revisión independiente existente.

### 3. Persiste una cuota por mensaje en la guía efectiva

**Required · Verdict: BLOCKING · Bucket: m**  
**Ubicación:** `skills/cdad-cycle/references/stage-1-discovery.md:18–20`.  
**Contrato:** PC-6, `spec.md:81`; dirección del encargo: sin cuota por mensaje.

La guía de descubrimiento inicial todavía ordena hacer “one to three” preguntas por turno. Es una regla aplicable al diálogo real del orquestador, no un ejemplo, y reinstala una cuota que la recuperación pidió evitar. Puede obligar a dividir artificialmente una consulta que el usuario podría contestar de una vez.

**Cierre verificable:** eliminar el límite obligatorio y revisar las superficies efectivas de descubrimiento para que orienten la cantidad de preguntas por utilidad y contexto, sin introducir otra cuota.

## Estado de las promesas y evidencia

- **PC-1/PC-2: Failed.** La responsabilidad y la preservación de decisiones están expresadas, pero la ruta obligatoria del hallazgo 2 contradice la consulta condicional.
- **PC-3: Supported within declared limits**, para la revisión contextual del ejemplo. `_apply_copy` (`skills/cdad-cycle/scripts/cdad_result.py:972–1005`) omite la reescritura si el destino registrado conserva los bytes y rechaza la divergencia. Ejecuté los dos tests existentes de reintento y divergencia: **2 passed in 17.69s**. No ejecuté una sesión de agente que produzca la presentación corregida; PC-7 sigue pendiente.
- **PC-4: Supported within declared limits.** Los cuatro tests nuevos corresponden a derivación nativa, entrega OpenCode, materialización y rechazo de borradores; la expectativa retirada es la específicamente autorizada. La evidencia registrada es **17 passed** (`recovery-delivery-green.md:7–13`). No establece fidelidad del diálogo.
- **PC-5: Failed.** La evidencia ejecutable registrada es **105 passed** (`recovery-orientation-green.md:12–16`), pero la guía contradice el resultado por el hallazgo 1. Los dos tests nuevos corresponden a cierre→status→apertura y diagnóstico de `done`/`null`; no sustituyen la revisión semántica de la guía. El informe GREEN declara que su sesión no validó el paquete antes de trabajar: es un límite procedimental que corresponde evaluar al orquestador.
- **PC-6: Failed.** Hallazgos 2 y 3. Revisé las fuentes canónicas afectadas, salidas generadas, instrucciones de paquete, ruta legacy, guía Odoo y metodología. La evidencia declarada de generación y recepción congelada está en `recovery-semantic-production.md:22–26`; esos checks no cierran contradicciones semánticas.
- **PC-7: Missing, pendiente por secuencia.** El ejercicio real es la tarea siguiente; su ausencia no es un nuevo defecto de diseño ni evidencia de éxito.

La auditoría del mapeo no identificó tests nuevos superfluos ni mocks sobre plumbing en los dos archivos revisados. Los controles usan CLI y fixtures descartables. La suite completa no se ejecutó en esta revisión.

La tabla de decisiones apunta a archivos existentes; los ADR no listados que examiné están marcados *Proposed*. No identifiqué una contradicción nueva con las decisiones aplicables a esta revisión.

## Comandos y alcance

- Validación de ruta C: `validate-request`, `validate-packet`, render de identificación y comparación del render completo con `PACKET.md`: sin error; `cmp` devolvió `0`.
- `git diff --quiet d415cc1b HEAD -- sources agents skills scripts tests install.sh build`: `0`; el producto y los tests examinados coinciden con el candidato. `HEAD` es `6dd025355b259556db079318b7616564fe2d8569`.
- Reintentos: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider` sobre `TestT4IdempotentIntegration::test_t4_materialize_retry_idempotent_targets_unchanged` y `TestR4RealJournalObserve::test_r4b_journal_divergent_retry_refuses_without_overwrite`: **2 passed**. Una primera selección con nombres de clase incorrectos no ejecutó tests (`exit 4`); luego se corrigió.
- No modifiqué archivos ni creé commits. El estado preexistente mostraba `M docs/.cdad-state.json`.

## Abstentions

- No acredito el recorrido real de PC-7 ni cumplimiento universal de agentes: aún faltan sesiones, transcripciones y evaluación independiente del candidato.
- No verifiqué con una ejecución nueva las selecciones completas de GREEN ni la suite completa; cité los informes registrados y sus límites.
- No verifico que los modelos de autor y revisor sean de familias distintas; los buckets se asignaron sin ese punto.