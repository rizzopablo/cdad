# Plan: Rendimiento de la suite

Borrador v3 no aprobado. Descompone una sola feature en tareas dependientes; no crea nuevas unidades ni amplía permisos.

## Steps

- [ ] Entregar XML y fases de `close`, conservando el cierre existente.
- [ ] Observar y calibrar las operaciones comprometidas antes de la base.
- [ ] Entregar atribución reproducible y comprobar la entrada a la base.
- [ ] Capturar la línea base completa y acordar el objetivo.
- [ ] Optimizar preparación serial y medir antes/después.
- [ ] Resolver el paralelismo condicionado.
- [ ] Revisar conservación y acreditar la corrida final.

## Organización y fronteras

Solo T1 es el siguiente lote despachable (`detail: next`).

T2–T7 son tareas `planned`: tienen objetivo, dependencias, responsable e incertidumbre con condición de resolución. El orquestador concreta su contrato, archivos y validación antes de despacharlas, sin modificar silenciosamente una tarea ya publicada.

La instrumentación se divide por resultados consumibles:

- T1 entrega resultados y fases recuperables sin cambiar el cierre.
- T2 entrega intervalos de operaciones con fidelidad demostrada.
- T3 entrega contabilidad reproducible y comprobación de suficiencia para iniciar la base.

Se puede rechazar T2 sin negar la utilidad del XML y las fases de T1; se puede rechazar la contabilidad de T3 sin negar que T2 capturó intervalos reales. Ninguna de esas entregas parciales autoriza por sí sola la base.

T5 entrega a T6 la optimización serial ejecutada y medida, incluido su balance frente al objetivo, aunque este todavía no se alcance. La dependencia exige precedencia y evidencia, no éxito serial suficiente para aceptar la feature. El objetivo final se acredita en T7 conforme a la spec §7.

```plan-tasks
{
  "validation_strategy": "Durante el desarrollo: focales y regresión proporcional, sin suite completa rutinaria. El reviewer registra validate a la entrada de Review; el orquestador lo registra al cierre, sobre las revisiones pertinentes. Base y final instrumentadas según autorización del dueño. La integración temprana no ejecuta el gate completo de CI.",
  "tasks": [
    {
      "id": "T1",
      "detail": "next",
      "objective": "Entregar XML y fases recuperables de close sin cambiar su semántica.",
      "consume": [],
      "produce": [
        {
          "artifact": "pytest.xml y profile.json por intento",
          "contract": "phase-profile-v1: spec §§4.2–4.3; entrega parcial sin acreditación de base"
        }
      ],
      "depends_on": [],
      "parallel": [],
      "files": [
        "Modify: scripts/cdad-suite.py",
        "Create: scripts/cdad_suite_observer.py",
        "Create/Test: tests/test_017_001_suite_profile.py",
        "Test: tests/test_008_002_suite_evidence.py",
        "Test: tests/test_008_002_suite_selection.py",
        "Test: tests/test_008_005_ci_gate.py"
      ],
      "focal_tests": [
        "test-writer RED y ejecutor GREEN: python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py"
      ],
      "regressions": [
        "ejecutor GREEN: python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py"
      ],
      "integration_gate": "Reviewer independiente: contrastar artefactos y preservación de §4.3, revisar evidencia focal y regresión, y ejecutar python3 scripts/cdad-suite.py validate sobre revisión con deltas materializados. Orquestador: comprobar alcance, evidencia y hallazgos antes de integrar. No ejecutar cdad-ci-gate.py como comprobación rutinaria de T1.",
      "owner": "test-writer: AUDIT acotado y RED; implementer: scripts y GREEN; reviewer independiente: Review; orquestador: materialización e integración"
    },
    {
      "id": "T2",
      "detail": "planned",
      "objective": "Fijar el alcance de operaciones y demostrar captura fiel de sus intervalos, incluida preparación real dentro de call.",
      "consume": [
        {
          "artifact": "pytest.xml y profile.json por intento",
          "contract": "phase-profile-v1: spec §§4.2–4.3; entrega parcial sin acreditación de base",
          "producer": "T1"
        }
      ],
      "produce": [
        {
          "artifact": "registro de operaciones y calibración focal recuperable",
          "contract": "spec §4.2"
        }
      ],
      "depends_on": ["T1"],
      "parallel": [],
      "owner": "arquitecto: mapeo; test-writer: oráculo y cambios autorizados bajo tests; implementer: observador fuera de tests; orquestador: integración",
      "uncertainty": "Fronteras concretas, mecanismo compatible, selección focal y necesidad de adaptar helpers sin alterar acciones contractuales.",
      "resolves_when": "Al concretar T2, el mapeo identifica los recorridos candidatos, intervalos comprometidos, desconocidos con regla de decisión, archivos por rol y selección capaz de ejercitar cada intervalo comprometido."
    },
    {
      "id": "T3",
      "detail": "planned",
      "objective": "Entregar agregación reproducible sin doble conteo y comprobar la condición de entrada a la base.",
      "consume": [
        {
          "artifact": "registro de operaciones y calibración focal recuperable",
          "contract": "spec §4.2",
          "producer": "T2"
        }
      ],
      "produce": [
        {
          "artifact": "método versionado de atribución y comprobación de entrada a la base",
          "contract": "spec §4.4"
        }
      ],
      "depends_on": ["T2"],
      "parallel": [],
      "owner": "test-writer: verificación contable; implementer: método autorizado; reviewer: contraste; orquestador: decisión de entrada",
      "uncertainty": "Forma final de los eventos capturados y ubicación exacta del agregador y sus verificadores.",
      "resolves_when": "T2 entrega evidencia calibrada; antes de despachar T3 se fijan el contrato del agregador, archivos, casos contables y comprobaciones de intervalos faltantes, compartidos y anidados."
    },
    {
      "id": "T4",
      "detail": "planned",
      "objective": "Conservar una base completa instrumentada y obtener del dueño el objetivo evaluable de reducción.",
      "consume": [
        {
          "artifact": "método versionado de atribución y comprobación de entrada a la base",
          "contract": "spec §4.4",
          "producer": "T3"
        }
      ],
      "produce": [
        {
          "artifact": "base, atribución y objetivo del dueño",
          "contract": "spec PC-3–PC-6"
        }
      ],
      "depends_on": ["T3"],
      "parallel": [],
      "owner": "orquestador: corrida y registro; dueño: objetivo",
      "uncertainty": "Revisión, colección efectiva, condiciones del host, costos observados y objetivo posterior.",
      "resolves_when": "Antes de ejecutar la base se acredita §4.4 y se fijan revisión, selección y condiciones; tras examinarla, el dueño registra magnitud, selección, método y regla de evaluación."
    },
    {
      "id": "T5",
      "detail": "planned",
      "objective": "Reducir preparación serial por costo observado, conservar las comprobaciones y entregar el resultado medido y su balance frente al objetivo, aunque todavía no lo alcance.",
      "consume": [
        {
          "artifact": "base, atribución y objetivo del dueño",
          "contract": "spec PC-3–PC-6",
          "producer": "T4"
        }
      ],
      "produce": [
        {
          "artifact": "optimización serial, comparación focal y balance frente al objetivo",
          "contract": "spec PC-7–PC-8 y PC-11; no exige alcanzar el objetivo final"
        }
      ],
      "depends_on": ["T4"],
      "parallel": [],
      "owner": "test-writer: preparación bajo tests; implementer: producto autorizado fuera de tests; reviewer: conservación",
      "uncertainty": "Qué preparación es reducible y qué consumidores, transiciones y archivos resultan afectados.",
      "resolves_when": "La base y el objetivo permiten elegir un cambio por costo observado; el siguiente lote fija entradas de caché, recursos mutables, selección antes/después y regresión de consumidores. El resultado serial medido se entrega a T6 aunque no alcance el objetivo."
    },
    {
      "id": "T6",
      "detail": "planned",
      "objective": "Evaluar el paralelismo después del resultado serial medido, aunque sea insuficiente para el objetivo; aplicarlo solo si el costo residual lo justifica y se demuestra seguridad.",
      "consume": [
        {
          "artifact": "optimización serial, comparación focal y balance frente al objetivo",
          "contract": "spec PC-7–PC-8 y PC-11; no exige alcanzar el objetivo final",
          "producer": "T5"
        }
      ],
      "produce": [
        {
          "artifact": "decisión de paralelismo y evidencia pertinente",
          "contract": "spec PC-9–PC-10"
        }
      ],
      "depends_on": ["T5"],
      "parallel": [],
      "owner": "orquestador y reviewer independiente; ejecución solo mediante paquetes delimitados; dueño para una restricción expresa de mantener toda la solución serial",
      "uncertainty": "Costo residual, utilidad neta y recursos efectivamente compartidos.",
      "resolves_when": "El contraste serial permite decidir si explorar concurrencia sin exigir que ya alcance el objetivo; si procede, antes de implementarla se fijan procesos, aislamiento, recursos, cachés, costo por worker y comprobaciones concurrentes. Una restricción de mantener toda la solución serial requiere decisión expresa del dueño."
    },
    {
      "id": "T7",
      "detail": "planned",
      "objective": "Confirmar conservación, integridad y cumplimiento del objetivo final conforme a spec §7, mediante la evidencia comparativa y la corrida completa instrumentada autorizada.",
      "consume": [
        {
          "artifact": "optimización serial, comparación focal y balance frente al objetivo",
          "contract": "spec PC-7–PC-8 y PC-11; no exige alcanzar el objetivo final",
          "producer": "T5"
        },
        {
          "artifact": "decisión de paralelismo y evidencia pertinente",
          "contract": "spec PC-9–PC-10",
          "producer": "T6"
        }
      ],
      "produce": [
        {
          "artifact": "review, intento final e informe de cierre",
          "contract": "spec PC-11–PC-12 y aceptación de §7"
        }
      ],
      "depends_on": ["T5", "T6"],
      "parallel": [],
      "owner": "reviewer independiente: revisión; orquestador: corrida, integridad final y materialización; dueño: aceptación",
      "uncertainty": "Candidata estabilizada, comparabilidad efectiva y selección vigente.",
      "resolves_when": "Antes de consumir la final se fijan candidata, base honesta del gate, colección y evaluación del objetivo; cualquier incompatibilidad que afecte esa evaluación vuelve al dueño."
    }
  ]
}
```

## T1 — XML y fases sin cambiar el cierre

### Resultado y consumidor

Resultado consumible: cada intento de `close` conserva sus artefactos actuales y agrega XML y perfil con argv, tiempo del hijo y fases identificadas, conforme a la parte de §4.2 aplicable.

Consumidores: T2 utiliza esos registros para añadir operaciones; el responsable de la suite puede recuperar resultados y fases desde los intentos.

Esta tarea aporta la parte de resultados/fases de PC-1 y la conservación de PC-2. No completa PC-1 ni habilita PC-3.

### Entrada y condiciones para arrancar

- Spec y plan v3 aprobados por el dueño.
- Paquetes con alcance exacto por rol y workspace de evidencia.
- Para el test-writer: contrato aprobado y tests pertinentes; no implementación.
- Para el implementer: contrato y verificadores publicados de T1.
- Referencias contractuales: spec §§4.2–4.3, PC-1, PC-2 e INV-1, INV-6 e INV-7.
- Referencias de regresión: los tres módulos existentes declarados en el bloque.

El AUDIT de T1 se limita a reutilización y carencias de los verificadores del cierre y de los nuevos artefactos. No audita todavía todas las cachés ni las doce postcondiciones.

### Archivos y separación

- Modify: `scripts/cdad-suite.py`, solo implementer.
- Create: `scripts/cdad_suite_observer.py`, solo implementer; ruta propuesta para la observación, no API ya existente.
- Create/Test: `tests/test_017_001_suite_profile.py`, solo test-writer.
- Test, sin modificaciones previstas en T1:
  - `tests/test_008_002_suite_evidence.py`.
  - `tests/test_008_002_suite_selection.py`.
  - `tests/test_008_005_ci_gate.py`.

Si el AUDIT demuestra que debe modificarse un verificador existente, se declara y delimita antes de hacerlo; no se amplía el paquete por conveniencia.

Los deltas documentales de altas los entrega el test-writer como texto. El orquestador los materializa antes de la siguiente transición.

### Comprobaciones observables

1. Una selección sintética conocida ejecutada por el CLI produce XML y fases correspondientes a los nodeids y resultados realmente emitidos. Una fase ausente no aparece como una fase de duración cero.
2. Los artefactos y el argv se recuperan desde el intento reservado; sucesivos intentos no sobrescriben evidencia anterior.
3. La instrumentación conserva el resultado y los registros del cierre de §4.3, incluidos fallos, skips e interrupciones, según la protección existente y sus carencias declaradas.
4. Una entrega solo de fases no acredita operaciones calibradas ni base completa. El diagnóstico distingue medición incompleta de resultado contractual de pytest.
5. El recorrido del gate sigue invocando una sola corrida de pytest; la regresión usa el entorno sintético del verificador existente, no una suite completa real.

No se exige una cuota de variantes equivalentes. El test-writer reutiliza verificadores existentes y añade solo protección faltante de estas promesas.

### Validación y responsables

- Test-writer: AUDIT acotado, selección de verificadores y RED pertinente del nuevo módulo.
- Implementer: GREEN focal y regresión proporcional con los comandos del bloque.
- Reviewer independiente: contrasta contrato, evidencia cruda, diff y resultados; registra `python3 scripts/cdad-suite.py validate` sobre la revisión con deltas materializados, conforme a `docs/suite-maintenance.md`.
- Orquestador: comprueba separación de roles, alcance y evidencia; materializa informes y resuelve el gate existente de integración.

El gate de T1 exige focales y regresiones satisfactorias, ausencia de bloqueantes pertinentes, y la integridad exigida a la entrada de Review. No es una corrida completa de `scripts/cdad-ci-gate.py`.

### TDD y evidencia de salida

AUDIT → RED de la protección nueva → GREEN → regresión proporcional → revisión independiente.

Se conservan:

- Auditoría y contribución de cada verificador.
- Comandos, selección, revisión y configuración efectiva.
- Resultado RED pertinente y GREEN.
- Intentos focales con XML, perfil, logs y diagnóstico.
- Regresión y comprobación del gate de una sola corrida.
- Diff por rol, deltas documentales, informe de revisión y commits.

La compatibilidad del observador con pytest es VERIFY que debe resolver T1 en focal. Una incompatibilidad o una necesidad de cambiar selección, parser o resultado contractual detiene esa parte y vuelve al orquestador.

Estimación: alcance técnico acotado, con incertidumbre concentrada en observación y compatibilidad. No se dispone de una duración medida del desarrollo; no se usa el costo histórico de la suite para estimarla.

## T2 — Operaciones comprometidas y calibración previa

**Detail:** planned.

**Objetivo:** completar el alcance de §4.2 y demostrar intervalos reales, correctamente atribuidos, antes de consumir la base.

**Depende de:** T1.

**Responsables:** arquitecto para mapeo técnico; test-writer para oráculo y modificaciones autorizadas bajo `tests/`; implementer para observación fuera de `tests/`; orquestador para materialización e integración.

El siguiente lote resolverá:

- Fronteras de construcción y preparación inicial dentro de `call`.
- Copias, generación, reutilización y regeneraciones contractuales.
- Operaciones compartidas, anidadas y esperas relevantes.
- Qué se compromete medir y qué queda desconocido con su regla de decisión.
- Selección conocida que ejercite cada intervalo comprometido.

La observación de preparación real dentro de `call` es obligatoria. Una selección sintética puede ayudar a comprobar el transporte, pero no sustituye la calibración de los recorridos candidatos.

**Produce:** `operation-scope.json`, evidencia focal y `calibration.md`, con selección, revisión y contraste esperado/observado.

**Incertidumbre y resolución:** mecanismo, fronteras y archivos concretos se fijan con el mapeo antes de despachar la implementación de T2. Si observar requiere alterar la transición contractual, se detiene esa alternativa y se declara el desconocimiento admisible o el bloqueo pertinente.

## T3 — Atribución y condición de entrada a la base

**Detail:** planned.

**Objetivo:** conservar el método versionado y ejecutable de agregación y conciliación de §4.4, comprobado sobre evidencia focal calibrada.

**Depende de:** T2.

**Responsables:** test-writer para el oráculo contable; implementer para el método autorizado; reviewer para contraste; orquestador para comprobar la entrada a la base.

**Produce:** método reproducible, atribución focal y registro de la comprobación de entrada.

**Incertidumbre y resolución:** el formato real de los eventos de T2 determina los archivos y detalles del agregador. Antes del despacho se fijan sus entradas, salidas y verificadores, sin tomar el informe producido como oráculo.

La entrada a la base debe comprobar todos los requisitos de spec §4.4. Un perfil con fases completas y sin los intervalos comprometidos no permite pasar.

## T4 — Línea base completa y objetivo

**Detail:** planned.

**Objetivo:** obtener la base completa recuperable, su atribución y el objetivo posterior del dueño.

**Depende de:** T3 y condición de entrada satisfecha.

**Responsables:** orquestador; dueño para el objetivo.

**Produce:** intento base, `baseline.json`, atribución, informe y `target.md`.

**Incertidumbre y resolución:** revisión, selección efectiva y condiciones se fijan antes de ejecutar. El objetivo se resuelve con el dueño después de examinar la base.

La corrida debe conservar revisión, orden, configuración, staging, cachés, recursos, carga, volumen auxiliar y evidencia cruda. La captura se contrasta con el alcance comprometido; una omisión esperada no se convierte en desconocimiento retrospectivo.

Antes de optimizar se registra magnitud, selección, condiciones y regla de evaluación. También se resuelve cómo mantener comparabilidad si se agregan verificadores después de la base.

No se inventa ahorro esperado ni se adopta un porcentaje sin esa decisión.

## T5 — Optimización serial

**Detail:** planned.

**Objetivo:** aplicar cambios elegidos por costo observado, conservar las garantías y entregar el resultado serial medido con su balance frente al objetivo. No es condición de salida alcanzar ya el objetivo final.

**Depende de:** T4.

**Responsables:** test-writer para preparación bajo `tests/`; implementer solo para producto autorizado fuera de `tests/`; reviewer independiente para conservación.

**Produce:** optimización serial, comparación focal y balance frente al objetivo: diff por responsable, matriz cambio→costo→garantía conservada, contraste antes/después, costo residual observado y reducción pendiente cuando corresponda.

**Incertidumbre y resolución:** la base determina candidatos, consumidores y archivos. Antes del despacho se fijan selección y orden equivalentes, entradas y vida útil de cachés, recursos mutables y regresiones afectadas.

Las operaciones necesarias para decidir ya deben estar medidas. Si una decisión depende de una operación desconocida, se aplica spec §4.4 antes del cambio: focal calibrada sobre revisión base recuperable, sin reconstruir ficticiamente la base completa.

Se conserva:

- Estado mutable independiente.
- Fixtures y estado `.cdad` necesarios.
- Regeneraciones y procesos CLI contractuales.
- Valores absolutos, diferencias, residuales y regresiones observadas.

T5 satisface su salida cuando la optimización serial se ha ejecutado y medido conforme a PC-7–PC-8 y se conserva PC-11. Entrega ese resultado a T6 aunque el balance muestre que el objetivo aún no se alcanza. Esto no permite omitir mediciones, aceptar una regresión contractual ni declarar aceptada la feature.

Si el cambio requiere modificar el contrato o un verificador fuera de lo aprobado, se detiene esa parte y vuelve al responsable competente.

## T6 — Decisión sobre paralelismo

**Detail:** planned.

**Objetivo:** evaluar la alternativa paralela según el resultado serial medido, el objetivo pendiente y la seguridad demostrable; aplicarla solo si se justifica y se acredita su seguridad.

**Depende de:** T5 ejecutada y medida. No requiere que el resultado serial alcance ya el objetivo final.

**Responsables:** orquestador y reviewer independiente; ejecución solo mediante paquetes delimitados. Corresponde al dueño registrar una restricción expresa de mantener toda la solución serial.

**Produce:** `parallelism.md` y evidencia pertinente.

**Incertidumbre y resolución:** el contraste serial determina si hay utilidad pendiente. Si procede explorar concurrencia, se concreta el contrato del siguiente lote antes de ejecutarlo: procesos, recursos compartidos, cachés, temporales, finalización de hijos y costo por worker.

Un resultado serial insuficiente, pero medido y con garantías conservadas, llega a esta evaluación. La insuficiencia no autoriza por sí sola el paralelismo: siguen siendo necesarias la justificación por costo residual y la evidencia de seguridad de PC-9–PC-10.

Si no se justifica, no se demuestra seguro o excede el mandato, se registra «no aplicado» y se conserva serie. Mantener obligatoriamente toda la solución serial por elección del dueño requiere registrar expresamente esa decisión; no es una consecuencia impuesta por T5 ni por la dependencia T5→T6.

No se habilita concurrencia solo porque exista aislamiento HOME/XDG. La decisión sin paralelismo no dispensa del objetivo final. Si este sigue sin alcanzarse, queda bloqueada la aceptación y se solicita decisión del dueño, sin rebajarlo unilateralmente.

## T7 — Revisión y corrida final

**Detail:** planned.

**Objetivo:** acreditar conservación, integridad y cumplimiento del objetivo final conforme a spec §7, sin otra corrida completa redundante.

**Depende de:** T5–T6 y candidata estabilizada.

**Responsables:** reviewer independiente; orquestador para cierre y materialización; dueño para aceptación.

**Produce:** review, intento final, atribución final, comparación y registro de aceptación.

**Incertidumbre y resolución:** antes de consumir la corrida final se fijan candidata, base honesta del gate, selección vigente, condiciones y evaluación del objetivo. Si una incompatibilidad de selección impide esa evaluación, se resuelve con el dueño antes de correr.

La solución final, serial o con paralelismo justificado y seguro, debe satisfacer el objetivo registrado en PC-4 sobre su selección, condiciones y regla de evaluación aprobadas. La entrega medida de T5 y la decisión de T6 no sustituyen esa acreditación ni dispensan ninguna garantía.

La final instrumentada autorizada debe aportar verde atribuible, skips declarados, canario examinado y perfil íntegro. El reviewer registra `validate` a la entrada de Review; el orquestador confirma integridad sobre la candidata final al cierre.

Un fallo, cambio incompatible o perfil incompleto permanece declarado. Una repetición completa exige autorización suficiente conforme a la política vigente; no se reintenta para esconder un rojo.

## Cobertura de postcondiciones

- PC-1: T1 aporta resultados/fases; T2 completa intervalos y calibración.
- PC-2: T1 y conservación posterior.
- PC-3: T2–T4.
- PC-4: T4.
- PC-5–PC-6: T2–T4; actualización final en T7.
- PC-7–PC-8: T5.
- PC-9–PC-10: T6.
- PC-11: revisión de T5–T7.
- PC-12: T7.
- Objetivo final registrado en PC-4 y aceptación de spec §7: balance serial en T5, decisión condicionada en T6 y acreditación final en T7.

## Producto documental y evidencia

Propuesta de materialización bajo:

`docs/specs/017-001-suite-performance/performance/`

- `operation-scope.json`: operaciones comprometidas y desconocidas, fronteras y reglas de decisión.
- `calibration.md`: evidencia focal, selección y contraste esperado/observado.
- `baseline.json`: identidad, condiciones y referencias a evidencia base.
- `attribution.json` y `report.md`: datos derivados y explicación.
- `target.md`: decisión del dueño posterior a la base.
- `comparison.json`: antes/después, condiciones de comparabilidad y balance frente al objetivo.
- `parallelism.md`: decisión y evidencia pertinente.

Los artefactos crudos permanecen en sus intentos originales, con referencias y hashes. El método de agregación queda conservado con versión y comando ejecutable.

Los paquetes delimitan qué rol produce o materializa cada archivo. Este plan no concede permisos de escritura por sí mismo.
