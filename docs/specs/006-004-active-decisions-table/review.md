# Review — 006-004-active-decisions-table

**2 BLOCKING · 5 OPTIONAL · 1 abstención.** No constituye aprobación.

Base revisada: `4f72f92~1..abe05ce91c45bc693e6cf1f5486711a700d68c37`. Spec y política coinciden con los SHA-256 del paquete.

## Bloqueantes

### B-1 — El bootstrap introduce una decisión ficticia en proyectos sin ADR

**Required · Verdict: BLOCKING · Bucket: m**

**Ubicación:** `skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md:11-13`.

La plantilla contiene una fila `vigente` que apunta a `docs/adr/ADR-NNN-<slug>.md`. El bootstrap copia esa plantilla (`references/bootstrap.md:68`), por lo que un proyecto sin decisiones nace con una fila que aparenta declararlas.

**Evidencia independiente:** copié la plantilla a un proyecto descartable sin ADR y ejecuté el mismo comprobador U7:

```text
TEMPLATE_COPIED_WITHOUT_ADRS rc=1 failed=['PD-11-FILE']
FAIL: ... file that does not exist: docs/adr/ADR-NNN-<slug>.md
```

Esto contradice **PD-7/E5**: la sección inicial debe estar vacía, no declarar un archivo inexistente. Además alimenta una falsa desalineación al reviewer.

**Remedio:** dejar únicamente encabezado y separador; explicar el ejemplo fuera de las filas de datos.

**Cierre verificable:** copiar literalmente la plantilla a un proyecto sin ADR, comprobar que no contiene decisiones declaradas y que el comprobador acepta esa tabla vacía. Mantener el `prepare` sin filas verde.

### B-2 — El GREEN de U7 conserva una escritura fuera del alcance autorizado

**Required · Verdict: BLOCKING · Bucket: m**

**Ubicación:** `docs/specs/006-004-active-decisions-table/u7-green.md:37-41`; cambio efectivo en `docs/systemPatterns.md:17`, commit `8f41160`.

Contrasté el informe con el commit y con `.cdad/packets/006-004-active-decisions-table-implementer-green-005/REQUEST.json:27-51`: el paquete autoriza únicamente implementación, no `docs/**`. El implementer modificó y commiteó precisamente ese documento. El receipt declara `scope_validation: unknown`, no una comprobación favorable.

La corrección de contenido es razonable, pero su entrega no satisface el contrato de alcance. El plan asigna esta materialización al orquestador; la regla general exige invalidar y rehacer resultados fuera de alcance. La recepción registrada no sustituye esa resolución.

**Remedio:** el orquestador debe resolver expresamente la entrega inválida y rehacer/materializar la corrección por el canal autorizado. No hace falta reescribir historia ni cambiar el oráculo.

**Cierre verificable:** disposición registrada, corrección realizada bajo autoridad y alcance adecuados, auditoría del diff y comprobador U7 verde.

## Opcionales / deuda

### O-1 — La pertenencia a `docs/adr/` sólo se comprueba por prefijo

**Verdict: OPTIONAL · Bucket: m**

**Ubicación:** `tests/validate-consistency.sh:896-902`; **PD-11**.

Una fila con `docs/adr/../outside.md`, apuntando a un archivo existente en `docs/`, obtiene:

```text
OUTSIDE_ADR_DIR rc=0 failed=[]
PASS: ... existing file under docs/adr/
```

El comprobador certifica una pertenencia que no verificó. No afecta las filas sembradas ni abre el CLI, que utiliza resolución de rutas; queda como deuda del comprobador.

**Cierre:** comprobar contención sobre la ruta resuelta y añadir el negativo correspondiente.

### O-2 — ADR-034 conserva marcas contradictorias de borrador

**Verdict: OPTIONAL · Bucket: m**

**Ubicación:** `docs/adr/ADR-034-principio-general-antes-especifico.md:3,7-8,75`; **INV-14**.

El encabezado dice `Accepted`, pero también declara aprobación pendiente, se describe como borrador y termina en `Status: Proposed`. La aprobación separada sí está registrada en `execution.md:417-419`; por eso no concluyo que falte aprobación.

**Cierre:** actualizar las marcas residuales y describir el borrador como fase histórica.

### O-3 — Falta el bloque U3 solicitado en el validador bash

**Verdict: OPTIONAL · Bucket: m**

**Ubicación:** `tests/test_006_004_u3_principle_single_source.py:92-96`; contrato en `plan.md`, ficha U3, y **PD-10**.

El RED declara que omitió el bloque de `validate-consistency.sh` exigido por el plan. Los tests Python sí comprueban fuente única, obligaciones y límite: es una discrepancia de superficie de validación, no ausencia total del oráculo.

**Cierre:** incorporar una comprobación equivalente o registrar una enmienda explícita que adopte el oráculo Python.

## Juicio sobre W-U6-1..3

| Hallazgo | Dictamen |
|---|---|
| **W-U6-1** — cambios no pedidos del scribe (`u6-acceptance.md:34-45,51`) | **OPTIONAL · Bucket: m.** El diff acredita la desviación; no invalida la demostración de concurrencia del CAS. Cierre: registrar la deuda de fidelidad y conservar la revisión del diff antes de aprobar materializaciones. |
| **W-U6-3** — descriptor adicional para Memory Bank (`u6-acceptance.md:53`) | **OPTIONAL · Bucket: m.** La cadena utilizó el materializador real y una clase existente; el paso manual es deuda de ergonomía. Cierre: documentar la receta o mejorar el adaptador en su alcance propio. |

## Abstentions

- **W-U6-2 — Verdict: ABSTAIN · Bucket: m.** `u6-acceptance.md:52` atribuye el redespliegue al script, pero declara que la causa no fue investigada. No puedo distinguir fallo del adaptador, del llamador o de ambos con ese resumen. Cierre: reproducción descartable con argumentos, estado previo, receipt y registro del nuevo despacho; sin tocar las sesiones activas.

## Evidencia de verificación

Comandos ejecutados, sin suite completa:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/opencode python3 -m pytest -p no:cacheprovider tests/test_006_004_u1_decisions_field.py tests/test_006_004_u2_decisions_section.py tests/test_006_004_u3_principle_single_source.py tests/test_006_004_u4_decisions_table.py tests/test_006_004_u7_seed_verification.py -q
```

```text
53 passed in 38.77s
```

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/opencode python3 -m pytest -p no:cacheprovider tests/test_006_003_u8_acceptance.py::TestPd8bMakeValidate::test_pd_8b_make_validate_passes_on_the_acceptance_install -q
bash tests/validate-odoo-specialization.sh
```

```text
1 passed in 16.80s
Assert PASS: 68
Assert FAIL: 0
```

Las sondas Python —comandos completos en el transcript— ejecutaron el bloque U7 sobre copias descartables y verificaron adicionalmente una instalación aislada:

```text
install --basic rc=0
installed principle exists=True
installed principle byte-identical=True
```

Los focales cubren PD-1..11 y las comprobaciones de PD-13 mediante CLI/procesos reales; no encontré mocks sobre plumbing. U6 sigue siendo evidencia registrada del recorrido, no una ejecución que yo haya repetido.

**Archivos modificados por esta revisión:** ninguno. **Commit creado:** ninguno. Estado y archivos ajenos conservados.