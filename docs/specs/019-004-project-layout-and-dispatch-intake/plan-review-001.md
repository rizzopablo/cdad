# Revisión del borrador: 019-004

**Dictamen: requiere correcciones antes de solicitar aprobación.** La revisión no aprueba el plan ni autoriza su implementación.

Objeto revisado:

- Plan `draft-001`: SHA-256 `723a3ad7f25a53866043c41838d1634c67ea1b6bf9efdb0f4fee18641c13fa56`
- Especificación `draft-001`: SHA-256 `733e7ea270af05563af1efec0f15b9188888fa7ad996ed22440dc975e29a8937`

## Hallazgos

### 1. La detección de proyectos existentes no tiene una regla suficientemente precisa

**Required · Verdict: BLOCKING · Bucket: m**

**Ubicación:** `spec.md:109–122`, `349–352`; `plan.md:57–61`.

La especificación enumera como posibles señales heredadas el estado, la política, el Memory Bank y las ubicaciones de specs y epics, pero no define qué archivos concretos o combinaciones constituyen una señal reconocible. Esto importa para nombres compartidos con documentación ordinaria, como `docs/adr/`, `docs/specs/` o `docs/progress.md`.

Dos implementaciones compatibles con la redacción pueden clasificar el mismo repositorio de manera distinta: una podría tratar documentación del producto como un proyecto CDAD existente; otra podría proponer inicializar un proyecto que sí contenía artefactos CDAD incompletos. En ambos casos se compromete la selección determinista y no migratoria prometida por PC-02–PC-04.

**Corrección y cierre verificable:** definir las señales fijas y su precedencia, incluidos los casos incompletos y ambiguos. Contrastar mediante fixtures al menos documentación ordinaria con nombres coincidentes, una instalación heredada reconocible y restos CDAD insuficientes para una clasificación segura.

### 2. La protección de una ejecución no queda ligada de forma inequívoca a la ubicación seleccionada

**Required · Verdict: BLOCKING · Bucket: m**

**Ubicación:** `spec.md:111–118`, `160–167`, `366–376`; `plan.md:72–95`.

El contrato exige que una continuación conserve la ubicación y el snapshot de política, pero no define cómo se aplica ese vínculo cuando falta el locator o cuando el estado seleccionado ya no contiene la ejecución activa. El estado se busca dentro del directorio seleccionado: por tanto, una selección diferente puede hacer que la operación consulte otro estado antes de llegar a comparar la política de la ejecución anterior.

La limitación declarada sobre reemplazo coherente externo no resuelve por sí sola este caso: la propia especificación promete que una continuación conflictiva será rechazada y que no existe repointing admitido. La verificación propuesta menciona conflictos de continuación, pero no fija qué identidad de ejecución debe recuperarse y contrastarse cuando cambia o desaparece el locator.

**Corrección y cierre verificable:** especificar cómo se determina la ejecución cuyo vínculo debe verificarse, sin búsqueda especulativa ni fallback que seleccione otro proyecto. Incorporar evidencia de continuación con locator ausente o alterado y estado alternativo: debe rechazarse el conflicto sin modificar ninguno de los artefactos.

### 3. La ubicación configurable puede entrar en conflicto con la política que el contrato prohíbe modificar

**Required · Verdict: BLOCKING · Bucket: m**

**Ubicación:** `spec.md:80–90`, `158–165`, `337–339`, `364–376`; `skills/cdad-cycle/scripts/cdad_packet.py:365–385`; `plan.md:82–95`.

Se admite cualquier directorio relativo válido, incluidos directorios anidados, pero el locator expresamente **no** clasifica rutas y una política aceptada no puede reescribirse. El clasificador actual da precedencia a implementación y tests sobre documentación. Por ejemplo, una ubicación metodológica bajo una raíz ya clasificada como implementación no pasa a ser documentación por el mero hecho de seleccionar el locator.

El contrato exige simultáneamente materializar artefactos metodológicos allí, respetar la política existente y no ampliar permisos, sin definir qué ocurre cuando esas obligaciones son incompatibles. Un proyecto configurado puede resolver correctamente el layout y, sin embargo, quedar imposibilitado de completar el ciclo o inducir una excepción de permisos no autorizada.

**Corrección y cierre verificable:** definir la validación de compatibilidad entre layout, política y destinos antes de operar, y el diagnóstico cuando no sean compatibles; cualquier cambio de política debe volver a la autoridad competente. Verificar una ubicación compatible y otra solapada con una raíz de implementación o tests, sin reescritura automática ni ampliación silenciosa.

### 4. El contrato de Route C es más restrictivo que la admisión que pretende preservar

**Required · Verdict: BLOCKING · Bucket: m**

**Ubicación:** `spec.md:217–224`, `244–266`; `architect-consultation-001.md:89–91`.

La gramática propuesta exige una declaración literal seguida de un bloque JSON cercado y solo espacios después. La consulta técnica advierte expresamente que las instrucciones vigentes exigen coincidencia de metadatos, pero no justifican restricciones adicionales de formato. Sin una decisión explícita sobre compatibilidad, una representación que el rol actual puede identificar y contrastar correctamente podría ser rechazada por el nuevo comando.

Esto afecta el objetivo de simplificar la admisión sin debilitar ni alterar sus límites. No sostengo que toda envoltura adicional deba aceptarse; el problema es que el borrador convierte una elección nueva de transporte en requisito de admisión sin demostrar su compatibilidad con los despachos existentes.

**Corrección y cierre verificable:** contrastar la gramática con las representaciones efectivamente admitidas y decidir explícitamente qué envolturas se conservan o dejan de admitir. Los controles deben incluir una identificación canónica, una representación histórica legítima documentada y los casos mixtos o parciales que deben seguir rechazándose.

### 5. La tabla de decisiones omite ADR presentes; la revisión de su estado requiere reconciliación

**Optional/Consider · Verdict: OPTIONAL · Bucket: m**

**Ubicación:** `docs/systemPatterns.md:5–48`; `docs/adr/ADR-037-suspension-registro-de-unidades-en-reposo.md:1–7`, `ADR-038-admision-en-cada-frontera-invocable-y-comparacion-por-bytes.md:1–7`, `ADR-039-verde-atribuible-o-no-es-verde.md:1–9`.

La tabla referencia archivos existentes, pero no incluye ADR-037, ADR-038 ni ADR-039. Los tres archivos se presentan como `Proposed`; además, ADR-037 registra una aprobación y ADR-039 dice que su decisión rige localmente. La nota de exclusiones de la tabla tampoco los menciona.

No atribuyo esta divergencia al borrador ni concluyo qué estado debe tener cada decisión. Conviene que el mantenedor reconcilie el índice y los registros; para este encargo no identifiqué una contradicción demostrada con una decisión vigente del reviewer.

## Suficiencia de verificación y límites

Se contrastaron las estrategias A–E con `skills/cdad-cycle/references/stage-2-specification.md` § “Verification strategy per promise”. El problema principal de A y B es que, antes de escribir el oráculo, deben resolverse las ambigüedades señaladas arriba. C declara una estrategia ejecutable apropiada para el comportamiento descrito. D necesita resolver la compatibilidad de Route C. E combina ejercicio instalado y revisión contextual, con la limitación de adquisición nativa declarada.

Como se revisan **borradores**, no productos implementados, las categorías de cierre de las promesas A–E son **unable to verify**: no se han ejecutado sus verificaciones de aceptación. Esto no equivale a declarar fallidas las implementaciones futuras ni a acreditar las promesas.

## Evidencia de esta revisión

- Ruta C: `validate-request` y `validate-packet` terminaron sin salida; el render de identificación coincidió con la identificación recibida. El contexto declarado es v2.
- `sha256sum` confirmó los dos digests indicados al inicio.
- Se examinaron los borradores, la consulta y notas de discovery, tests existentes del límite de comparación, fuentes de clasificación y guard, y la tabla de decisiones frente a `docs/adr/`.
- **Tests de producto:** no ejecutados; esta es una revisión de un plan no aprobado.
- **Archivos modificados por esta revisión:** ninguno. `git status --short` mostró `M docs/.cdad-state.json`, ya presente al examinar el árbol.
- **Commit creado:** ninguno. El HEAD examinado fue `977f8474e4fd396f91b2e95c3691f61d0656e40c`.

## Abstentions

- No se acreditó que ningún runtime pueda exportar fielmente el mensaje nativo recibido; el propio borrador mantiene esa capacidad pendiente.
- No se verificó una implementación, instalación, ciclo completo ni evidencia de regresión: todavía no forman parte del objeto entregado.
- No se decidió el estado normativo de ADR-037–039; corresponde reconciliarlo con su autoridad y sus registros.