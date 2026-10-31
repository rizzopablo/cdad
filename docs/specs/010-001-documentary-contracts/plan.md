# Plan — 010-001 Contratos documentales compartidos

**Estado:** borrador; pendiente de aprobación de Pablo.  
**Contrato:** `docs/specs/010-001-documentary-contracts/spec.md`.

## Objetivo y fronteras

Publicar la referencia compartida y transportar obligaciones breves por los consumidores existentes, conservando roles, aislamiento, dominio y autoridad.

No se implementa el selector de 010-002 ni el piloto de 010-003.

Cada despacho corresponde a un único rol y subfase. Las tareas siguientes son secuenciales; RED y GREEN se despachan por separado.

## Pasos

- [ ] T1. Aprobar y materializar el contrato.
- [ ] T2. Construir verificadores independientes y demostrar RED.
- [ ] T3. Implementar la referencia y las obligaciones de rol.
- [ ] T4. Completar transporte y distribución canónica.
- [ ] T5. Revisar independientemente y resolver hallazgos.
- [ ] T6. Cerrar con aceptación y borradores de Memory Bank.

```plan-tasks
{
  "validation_strategy": "Cada responsable ejecuta las comprobaciones declaradas de su tarea. Las tareas sin ejecución de software se verifican por observable_checks, sin suite ficticia. T2 demuestra RED; T3 acredita contenido normativo; T4 acredita transporte y regresiones focalizadas. T5 contrasta semánticamente el contrato y las fuentes. La suite completa se ejecuta una sola vez por quien cierre en T6. Ningún control estructural acredita fidelidad semántica ni aceptación funcional.",
  "tasks": [
    {
      "id": "T1",
      "detail": "next",
      "depends_on": [],
      "parallel": [],
      "files": [
        "docs/specs/010-001-documentary-contracts/spec.md",
        "docs/specs/010-001-documentary-contracts/plan.md"
      ],
      "focal_tests": "@validation_strategy",
      "observable_checks": [
        "Aprobación recuperable de Pablo de spec, plan y D1-D4; materialización fiel sin registrar aprobación inexistente.",
        "Preparación y validación únicamente del encargo de T2, con fuentes, producto editable, oráculos protegidos y evidencia, sin permisos amplios sobre docs/**. T3 y todos los encargos siguientes se preparan y validan justo antes de su despacho, tras cerrar el encargo anterior."
      ],
      "regressions": [],
      "integration_gate": "Pablo aprueba; el orquestador materializa y prepara y valida únicamente el encargo de T2. T3 y todos los encargos siguientes se preparan y validan justo antes de su despacho, tras cerrar el encargo anterior.",
      "owner": "Pablo: aprobación; orquestador: materialización y validación de paquetes."
    },
    {
      "id": "T2",
      "detail": "next",
      "depends_on": [
        "T1"
      ],
      "parallel": [],
      "files": [
        "tests/test_010_001_documentary_contracts.py"
      ],
      "focal_tests": [
        "python3 -B -m unittest tests.test_010_001_documentary_contracts"
      ],
      "observable_checks": [
        "Grupos A-D trazados a PC-01-16, con una clase pública por grupo: TestPromiseA, TestPromiseB, TestPromiseC y TestPromiseD; oráculo derivado del contrato, sin inspeccionar el producto documental.",
        "RED por aserciones de comportamiento ausente; separar controles ya verdes y proteger tests/fixtures de GREEN."
      ],
      "regressions": [],
      "integration_gate": "El orquestador verifica evidencia RED y aislamiento antes de despachar GREEN; fixtures adicionales solo bajo tests/ y declarados en el paquete.",
      "owner": "Test-writer: verificadores y ejecución RED; orquestador: gate."
    },
    {
      "id": "T3",
      "detail": "next",
      "depends_on": [
        "T2"
      ],
      "parallel": [],
      "files": [
        "skills/cdad-cycle/references/documentary-contracts.md",
        "skills/cdad-cycle/SKILL.md",
        "sources/roles/architect.md",
        "sources/roles/implementer.md",
        "sources/roles/test-writer.md",
        "sources/roles/reviewer.md",
        "sources/roles/scribe.md",
        "sources/roles/orchestrator.md"
      ],
      "focal_tests": [
        "python3 -B -m unittest tests.test_010_001_documentary_contracts.TestPromiseA tests.test_010_001_documentary_contracts.TestPromiseB tests.test_010_001_documentary_contracts.TestPromiseC"
      ],
      "observable_checks": [
        "Referencia conforme a D1-D4 y PC-01-12, obligaciones breves y punteros por rol.",
        "Diff limitado al paquete; sin editar tests, contrato ni insumos protegidos; sin campos, agentes, skills o permisos nuevos."
      ],
      "regressions": [
        "Comprobar en el diff conservación de independencia del test-writer, función del scribe y autoridad de aprobación."
      ],
      "integration_gate": "Grupos normativos verdes y diff conforme; distribución explícitamente pendiente de T4.",
      "owner": "Implementer: contenido, comprobaciones focalizadas y diff; orquestador: gate."
    },
    {
      "id": "T4",
      "detail": "next",
      "depends_on": [
        "T3"
      ],
      "parallel": [],
      "files": [
        "skills/cdad-cycle/packets/roles/architect.md",
        "skills/cdad-cycle/packets/roles/implementer.md",
        "skills/cdad-cycle/packets/roles/test-writer.md",
        "skills/cdad-cycle/packets/roles/reviewer.md",
        "skills/cdad-cycle/packets/roles/scribe.md",
        "build/staging/",
        "agents/"
      ],
      "focal_tests": [
        "python3 -B -m unittest tests.test_010_001_documentary_contracts",
        "make staging",
        "make agents",
        "make validate"
      ],
      "observable_checks": [
        "PC-13-16: punteros y obligaciones en paquetes, ambos runtimes y variantes genéricas/Odoo; techo estático vigente.",
        "Generación repetible y render real; instalación aislada con bytes de referencia y staging, sin modificar instalación global ni derivados manualmente. Los paquetes publicados antes del cambio de bloques de T4 quedan obsoletos y no se reutilizan para despachos posteriores."
      ],
      "regressions": [
        "tests/test_cdad_generate.py",
        "tests/test_role_packet_render.py",
        "tests/test_role_packet_consumers.py",
        "tests/test_install_ownership.py",
        "tests/test_install_review5_regressions.py",
        "tests/test_006_004_u3_principle_single_source.py"
      ],
      "integration_gate": "Distribución y regresiones focalizadas verdes; destinos aislados y rutas derivadas concretas delimitados en el paquete. Necesidad de editar renderer, instalador o esquema exige detener y replantear. Un hallazgo del grupo D atribuible a sources/ o a skills/cdad-cycle/SKILL.md vuelve a un despacho GREEN acotado de T3; no se corrige desde T4.",
      "owner": "Implementer: generación, render, instalación y regresiones; orquestador: gate."
    },
    {
      "id": "T5",
      "detail": "next",
      "depends_on": [
        "T4"
      ],
      "parallel": [],
      "files": [],
      "observable_checks": [
        "Reviewer independiente contrasta PC-01-16 con evidencia y examina semánticamente D1-D4 contra fuentes; verifica expresamente PC-10/INV-08 sobre sandbox y escrituras transitorias.",
        "Revisar fronteras de escritura, oráculo, fuente única, punteros y distribución; no equiparar estructura con fidelidad.",
        "Hallazgos localizados con consecuencia y condición de cierre; declarar abstenciones y acreditar resolución por el rol competente."
      ],
      "regressions": [
        "Reexaminar las comprobaciones afectadas por cada corrección; discrepancias contractuales vuelven a especificación/aprobación."
      ],
      "integration_gate": "Informe independiente y evidencia de resolución, sin autoaprobación ni edición del reviewer.",
      "owner": "Reviewer: revisión read-only; roles competentes: correcciones y sus comprobaciones; orquestador: gate."
    },
    {
      "id": "T6",
      "detail": "next",
      "depends_on": [
        "T5"
      ],
      "parallel": [],
      "files": [],
      "observable_checks": [
        "Suite completa y comandos/resultados registrados por quien cierra; PC-01-16 acreditadas y pendientes admisibles visibles.",
        "Registros automático y semántico separados; aceptación funcional recuperable de Pablo.",
        "Scribe devuelve borradores de Memory Bank conservando deferred-hardening; materialización solo tras aprobación; sin push ni publicación."
      ],
      "regressions": [
        "@validation_strategy"
      ],
      "integration_gate": "Pablo acepta funcionalmente y aprueba borradores de Memory Bank antes de su incorporación; el orquestador registra solo aprobaciones obtenidas.",
      "owner": "Quien cierra: suite y evidencia; reviewer: evidencia semántica; Pablo: aceptación/aprobación; scribe: borradores; orquestador: materialización y registro."
    }
  ]
}
```

## T1 — Aprobación y materialización

**Responsables:** Pablo y orquestador.

1. Solicitar aprobación explícita de spec y plan, incluidas D1–D4.
2. Materializar los documentos sin registrar aprobación inexistente.
3. Preparar y validar únicamente el encargo de T2 con fuentes, producto editable, oráculos protegidos y evidencia esperada. T3 y todos los encargos siguientes se preparan y validan justo antes de su despacho, tras cerrar el encargo anterior; no se publican anticipadamente en T1.

**Verificación:**

- Aprobación recuperable de Pablo.
- Contrato materializado coherente con el texto aprobado.
- Paquetes válidos y alcances delimitados.
- Ningún permiso amplio sobre `docs/**` sustituye la identificación del producto.

**Salida:** contrato autorizado para RED.

## T2 — Verificadores independientes y RED

**Rol:** test-writer, en sesión independiente.

**Producto propuesto:** `tests/test_010_001_documentary_contracts.py` y fixtures necesarios bajo `tests/`.

Derivar las comprobaciones de la spec aprobada, sin inspeccionar la implementación documental para construir el oráculo. Los procesos bajo prueba pueden observar las superficies públicas declaradas; no se importan internos del generador o renderer como sustituto de su comportamiento.

| Grupo | Postcondiciones | Verificación |
|---|---|---|
| A. Criterios compartidos | PC-01–04 | Referencia presente; conceptos, localizadores y reglas de pendientes identificables. Revisión semántica complementaria registrada. |
| B. Frontera de producción | PC-05–08 | Declaraciones del encargo y obligaciones por rol, incluida la protección de fuentes/oráculos y la independencia del test-writer. |
| C. Aceptación honesta | PC-09–12 | Separación de registros, límites estructurales, revisión contra fuentes y autoridad de aceptación. |
| D. Distribución | PC-13–16 | Unicidad por frases normativas derivadas de la referencia, con espacios normalizados, sobre `skills/`, `sources/` y `agents/`, siguiendo `tests/test_006_004_u3_principle_single_source.py`; punteros, fuentes y paquetes; generación real; agentes promovidos; instalación aislada; conservación de restricciones. |

T2 expone una clase pública por grupo: A → `TestPromiseA`, B → `TestPromiseB`, C → `TestPromiseC`, D → `TestPromiseD`. Son nombres comprometidos para el módulo nuevo, no clases existentes. Su informe publica los selectores; el paquete de T3 se prepara y valida justo antes de su despacho, tras cerrar el encargo de T2, y fija los comandos exactos de A–C. El grupo D puede seguir rojo hasta T4.

Las comprobaciones de contenido no congelan párrafos completos. Comprueban obligaciones y referencias; la revisión independiente juzga suficiencia y coherencia.

**Verificación:**

- Cada prueba identifica la promesa y postcondiciones protegidas.
- RED falla mediante aserciones por comportamiento ausente, no por errores de importación o fixtures.
- El informe diferencia controles ya verdes de las carencias que motivan RED.
- Tests y fixtures quedan fuera del alcance editable de GREEN.

**Comando focalizado propuesto, una vez creado el módulo:**

```bash
python3 -B -m unittest tests.test_010_001_documentary_contracts
```

## T3 — Referencia y obligaciones de rol

**Rol:** implementer, subfase GREEN.

**Superficies previstas:**

- Nuevo `skills/cdad-cycle/references/documentary-contracts.md`.
- `skills/cdad-cycle/SKILL.md`: entrada breve en la tabla de referencias.
- `sources/roles/architect.md`.
- `sources/roles/implementer.md`.
- `sources/roles/test-writer.md`.
- `sources/roles/reviewer.md`.
- `sources/roles/scribe.md`.
- `sources/roles/orchestrator.md`.

**Trabajo:**

1. Implementar la referencia conforme a D1–D4 y PC-01–12.
2. Incorporar obligaciones breves y punteros por rol.
3. Ajustar el contrato del implementer para admitir únicamente producto documental expresamente autorizado, sin ampliar defaults.
4. Mantener la independencia del test-writer también cuando el producto es un documento.
5. Conservar la función del scribe y la autoridad de aprobación.

**Verificación:**

- Grupos A–C verdes mediante el comando exacto fijado en el paquete, usando las clases públicas expuestas por T2:

  ```bash
  python3 -B -m unittest tests.test_010_001_documentary_contracts.TestPromiseA tests.test_010_001_documentary_contracts.TestPromiseB tests.test_010_001_documentary_contracts.TestPromiseC
  ```
- Revisión del diff limitada a las rutas del paquete.
- Ninguna edición de tests, contrato de aceptación ni insumos protegidos.
- Ningún campo, agente, skill o permiso nuevo.

**Salida:** contenido normativo implementado; distribución pendiente de T4.

## T4 — Transporte y distribución

**Rol:** implementer, subfase GREEN, mediante despacho separado.

**Superficies previstas:**

- `skills/cdad-cycle/packets/roles/{architect,implementer,test-writer,reviewer,scribe}.md`.
- Artefactos derivados de agentes y staging, exclusivamente mediante generación.

No se prevé modificar el renderer, instalador ni esquema. Si aparece una necesidad real fuera de este alcance, se informa y se replantea; no se amplía silenciosamente.

**Trabajo:**

1. Transportar las obligaciones y el puntero en los cinco bloques existentes. Los paquetes publicados antes de este cambio quedan obsoletos para despachos posteriores; preparar y validar los nuevos contra las instrucciones vigentes justo antes de despacharlos.
2. Regenerar mediante `make agents`; no editar agentes manualmente.
3. Verificar generación repetible.
4. Renderizar paquetes representativos mediante la CLI existente.
5. Instalar y comprobar los artefactos en destinos aislados declarados por el paquete.

La instalación utiliza `CDAD_INSTALL_ROOT` con una raíz absoluta existente. Las variables de destinos adicionales se controlan para no tocar instalaciones reales.

**Verificación:**

- PC-13–16 acreditadas.
- Referencia instalada con los bytes de origen.
- Agentes instalados con los bytes de staging.
- Obligaciones presentes en variantes genéricas y Odoo existentes.
- Bloques estáticos bajo el techo vigente.
- Regresiones focalizadas de generación, paquetes e instalación.
- Sin cambios de instalación global ni modificaciones manuales de derivados.

Un hallazgo del grupo D atribuible a `sources/` o a `skills/cdad-cycle/SKILL.md` vuelve a un despacho GREEN acotado de T3; no se corrige desde T4. Se cierra el encargo activo antes de preparar y validar el despacho de corrección. Tras la corrección se reejecutan las comprobaciones afectadas y se retoma T4 mediante un nuevo encargo preparado y validado antes de su despacho.

**Entrypoints existentes:**

```bash
make staging
make agents
make validate
```

Las pruebas destructivas o de instalación se ejecutan en copias/destinos descartables dentro del workspace autorizado, no contra el entorno personal.

## T5 — Revisión independiente y correcciones

**Rol:** reviewer, sesión distinta del autor, read-only.

**Entradas:** contrato aprobado, diff completo, tests, resultados y artefactos distribuidos.

**Verificación:**

1. Comprobar la correspondencia PC-01–16 → evidencia.
2. Examinar semánticamente D1–D4: categorías, localizadores, pendientes e integración mínima con fuente única.
3. Buscar escapes de escritura, ampliaciones de permisos y contaminación del oráculo.
4. Contrastar fuente única, punteros, paquetes y artefactos generados.
5. Comprobar que ninguna prueba estructural se presenta como fidelidad semántica y verificar expresamente PC-10/INV-08: ninguna obligación textual o paquete se presenta como sandbox ni como prueba de ausencia de escrituras transitorias.
6. Registrar hallazgos con ubicación, consecuencia y condición de cierre; declarar abstenciones.

Las correcciones vuelven al rol competente. El implementer no modifica verificadores; una discrepancia contractual vuelve a especificación/aprobación cuando corresponda.

**Salida:** informe independiente y evidencia de resolución, sin autoaprobación.

## T6 — Cierre y Memory Bank

**Responsables:** quien cierre la tarea, Pablo, scribe y orquestador, cada uno dentro de su función.

1. Ejecutar una vez la suite completa declarada para el cierre, conforme a la política vigente.
2. Consolidar evidencia automática y revisión independiente por separado.
3. Solicitar aceptación funcional de Pablo.
4. Despachar al scribe para los borradores de Memory Bank, conservando `deferred-hardening`.
5. Materializar y registrar únicamente conforme a las aprobaciones obtenidas.

**Verificación:**

- Suite completa y comandos/resultados registrados.
- Ninguna postcondición comprometida sin acreditar.
- Pendientes admisibles visibles y justificados.
- Aceptación recuperable de Pablo.
- Borradores de Memory Bank aprobados antes de su incorporación.
- Sin push ni publicación externa.

## Referencias del plan

- Secuencia y dependencias: `docs/epics/epic-010-documentary-specialization/plan.md:41-51`.
- Gates y autoridad: `docs/epics/epic-010-documentary-specialization/plan.md:53-106`.
- Separación y materialización: `sources/roles/orchestrator.md:118-153`.
- Pruebas por promesa: `sources/roles/test-writer.md:66-92`.
- Generación canónica: `Makefile:1-23`.
- Instalación aislada: `install.sh:327-347`.
- Precedente de procesos reales: `tests/test_006_004_u3_principle_single_source.py:17-37,76-81`.

---

## Evidencia de este encargo

*Registro conservado del borrador original `architect-draft-001`; la evidencia de esta corrección figura en el apartado siguiente.*

**Intake:** ruta C válida; contexto v2; `PACKET.md` idéntico al render canónico completo: **6721 bytes**. SHA-256 del contrato y del plan aprobado coincidentes.

Comandos de validación ejecutados desde la raíz:

```bash
python3 scripts/cdad_packet.py validate-request --project-root . --execution-context .cdad/executions/exec-010-001-documentary-contracts-002/execution.json --request .cdad/packets/010-001-documentary-contracts-architect-draft-001/REQUEST.json

python3 scripts/cdad_packet.py validate-packet --project-root . --execution-context .cdad/executions/exec-010-001-documentary-contracts-002/execution.json --request .cdad/packets/010-001-documentary-contracts-architect-draft-001/REQUEST.json --packet .cdad/packets/010-001-documentary-contracts-architect-draft-001/PACKET.md

python3 scripts/cdad_packet.py render --project-root . --execution-context .cdad/executions/exec-010-001-documentary-contracts-002/execution.json --request .cdad/packets/010-001-documentary-contracts-architect-draft-001/REQUEST.json --route C
```

Los dos validadores terminaron con **rc=0**, sin salida. El render de ruta C coincidió con la identificación recibida. La comparación completa se realizó en memoria mediante `subprocess.check_output`, `Path.read_bytes()` y `assert`; hashes con `hashlib.sha256`, usando Python **3.13.5**.

Estado observado al inicio y al final:

```text
 M docs/.cdad-state.json
?? docs/specs/010-000-continuity-relative-root/discovery.md
?? docs/specs/010-001-documentary-contracts/
```

Comandos de estado ejecutados:

```bash
git status --short
git diff --stat
git rev-parse HEAD
```

HEAD observado:

```text
bd69977694d3eea936f905c348ce4350e4c127d4
```

**Archivos editados por este encargo: ninguno. Commit creado: ninguno.** No ejecuté implementación, generación, instalación ni suite. El estado preexistente no se atribuye a este trabajo ni demuestra ausencia de escrituras transitorias.

## Evidencia de la corrección — `architect-draft-002`

**Intake:** ruta C validada; identificación coincidente, contexto v2, SHA-256 contractual coincidente y comparación binaria completa de `PACKET.md` contra su render canónico: **6214 bytes idénticos**.

Comandos ejecutados desde la raíz:

```bash
python3 scripts/cdad_packet.py validate-request --project-root <repo> --request .cdad/packets/010-001-documentary-contracts-architect-draft-002/REQUEST.json

python3 scripts/cdad_packet.py validate-packet --project-root <repo> --request .cdad/packets/010-001-documentary-contracts-architect-draft-002/REQUEST.json --packet .cdad/packets/010-001-documentary-contracts-architect-draft-002/PACKET.md

python3 --version
git status --short
git diff --stat
git rev-parse HEAD
```

Ambos validadores finalizaron con **rc=0**, sin salida. La comparación del render completo y de la identificación de ruta C se realizó en memoria mediante `subprocess.check_output`; el contrato se contrastó mediante `hashlib.sha256`.

El bloque propuesto se validó en memoria con Python **3.13.5**, usando `python3 -B`, `runpy.run_path` y estas comprobaciones existentes:

```python
m = runpy.run_path(
    "skills/cdad-cycle/scripts/cdad_packet.py",
    run_name="cdad_packet_validation_only"
)
parsed, strategy = m["_plan_tasks_from_contract"](proposed)
m["_check_plan_tasks"](parsed)
m["_check_plan_validation_plan"](parsed, strategy)
```

Resultado:

```text
VALIDATION: canonical parse, dependency/parallel checks, per-task validation: PASS; T1-T6 only; one LF fence; original plan retained.
SPEC unchanged; input SHA256: 3cf014dd82c8f264d3555e74bd7dea997bf6921227f8740042f19ed1d75c8fb0
```

La comprobación se aplicó al plan original con la inserción del bloque, sin escribir archivos. La anotación histórica y este apartado únicamente distinguen la evidencia de ambos encargos.

El estado final mostró las mismas rutas preexistentes indicadas arriba. `git diff --stat` informó:

```text
 docs/.cdad-state.json | 190 +++++++++++++++++++++++++++++---------------------
 1 file changed, 112 insertions(+), 78 deletions(-)
```

HEAD permaneció en `bd69977694d3eea936f905c348ce4350e4c127d4`.

**Archivos modificados por esta corrección: ninguno. Commit creado: ninguno.** No ejecuté implementación, generación, instalación ni suite. Ambos documentos siguen siendo borradores pendientes de aprobación de Pablo.

## Evidencia de la corrección — `architect-draft-003`

**Objeto:** aplicar F1–F6 de `docs/specs/010-001-documentary-contracts/plan-review.md:11-65`, conservando el resto del borrador y sus registros históricos.

**Intake:** ruta C válida, contexto de ejecución v2. Identificación completa coincidente con su render de ruta C; `PACKET.md` idéntico al render canónico completo: **6610 bytes**. SHA-256 del contrato coincidente.

Comandos principales ejecutados desde la raíz:

```bash
python3 skills/cdad-cycle/scripts/cdad_packet.py validate-request --project-root . --request .cdad/packets/010-001-documentary-contracts-architect-draft-003/REQUEST.json

python3 skills/cdad-cycle/scripts/cdad_packet.py validate-packet --project-root . --request .cdad/packets/010-001-documentary-contracts-architect-draft-003/REQUEST.json --packet .cdad/packets/010-001-documentary-contracts-architect-draft-003/PACKET.md

python3 skills/cdad-cycle/scripts/cdad_packet.py render --project-root . --request .cdad/packets/010-001-documentary-contracts-architect-draft-003/REQUEST.json --route C

git status --short
git diff --stat
git rev-parse HEAD
```

Los validadores terminaron con **rc=0**, sin salida. Las comparaciones completas se efectuaron en memoria mediante `subprocess.check_output`, `Path.read_bytes()` y `assert`; el contrato se contrastó mediante `hashlib.sha256`.

La propuesta corregida se construyó únicamente en memoria con Python **3.13.5**, mediante `python3 -B -`. Se verificó la presencia única de cada fragmento sustituido y se examinó su diff mediante `difflib.unified_diff`. El bloque corregido se comprobó con las funciones existentes:

```python
m = runpy.run_path(
    "skills/cdad-cycle/scripts/cdad_packet.py",
    run_name="cdad_packet_validation_only"
)
tasks, strategy = m["_plan_tasks_from_contract"](plan.encode())
m["_check_plan_tasks"](tasks)
m["_check_plan_validation_plan"](tasks, strategy)
assert [x["id"] for x in tasks] == ["T1", "T2", "T3", "T4", "T5", "T6"]
```

Salidas relevantes:

```text
Complete canonical PACKET.md comparison: identical (6610 bytes). Contract SHA256: matches.
Full route C identification comparison: identical.
VALIDATION: canonical parse, dependency/parallel checks, per-task validation: PASS; T1-T6 only; one canonical block.
Python: 3.13.5
No files written; historical evidence retained unchanged.
```

**Trazabilidad de las correcciones:**

- **F1:** PC-12 e INV-07 usan autoridad genérica para la norma distribuible; el nombre concreto queda en los documentos de autoridad de esta unidad bajo `docs/`.
- **F2:** T1 prepara únicamente T2/T3; los encargos posteriores se preparan justo antes de su despacho. T4 declara obsoletos los paquetes anteriores al cambio de bloques.
- **F3:** PC-13 y el grupo D fijan unicidad por frases normativas con espacios normalizados sobre `skills/`, `sources/` y `agents/`, conforme al precedente verificado en `tests/test_006_004_u3_principle_single_source.py:52-57`.
- **F4:** T2 declara una clase pública por grupo y T3 dispone de un comando exacto para A–C.
- **F5:** PC-10 incorpora INV-08 y T5 lo verifica expresamente.
- **F6:** T5 examina D1–D4.

Estado final observado:

```text
 M docs/.cdad-state.json
?? docs/specs/010-000-continuity-relative-root/discovery.md
?? docs/specs/010-001-documentary-contracts/
```

`git diff --stat` informó:

```text
 docs/.cdad-state.json | 282 ++++++++++++++++++++++++++++++++++++--------------
 1 file changed, 204 insertions(+), 78 deletions(-)
```

HEAD observado al inicio y al cierre:

```text
bd69977694d3eea936f905c348ce4350e4c127d4
```

**Archivos modificados por este encargo: ninguno. Commit creado: ninguno.** Las rutas de estado ya estaban presentes al iniciar; no atribuyo sus cambios a este trabajo ni uso esa observación como prueba de ausencia de escrituras transitorias. No ejecuté implementación, generación, instalación ni suite. Ambos documentos permanecen pendientes de aprobación.

## Evidencia de la corrección — `architect-draft-004`

**Objeto:** corregir N1 y N2 de `docs/specs/010-001-documentary-contracts/plan-review-002.md:22-48`. La spec permanece sin cambios; los registros anteriores se conservan como evidencia histórica, no como instrucciones operativas vigentes.

**Intake:** ruta C validada; contexto de ejecución v2; contrato SHA-256 coincidente. Comparación binaria completa de `PACKET.md` contra el render canónico: **6332 bytes idénticos**. Identificación completa de ruta C coincidente.

**Correcciones propuestas:**

- **N1:** las tres apariciones operativas de T1 preparan y validan únicamente T2. T3 y todos los encargos siguientes se preparan y validan justo antes de su despacho, tras cerrar el encargo anterior. La declaración de T2 sobre el paquete de T3 queda sincronizada.
- **N2:** T4 y su `integration_gate` devuelven los hallazgos del grupo D atribuibles a `sources/` o `skills/cdad-cycle/SKILL.md` a un despacho GREEN acotado de T3, sin corregirlos desde T4. La vuelta respeta el cierre del encargo activo y la preparación secuencial de los nuevos.

Se conserva la distribución de tareas y sus alcances: frente a ampliar T4 o cambiar los selectores de T3, se elige el retorno explícito al despacho competente. El criterio es reparar el defecto sin ampliar permisos ni modificar las demás obligaciones.

**Fundamento verificado:** `skills/cdad-cycle/scripts/cdad_packet.py:6465-6489` rechaza preparar otro paquete mientras exista uno publicado activo sin cierre admisible. Las comprobaciones estructurales del plan están en `:5124-5165`, `:5168` y `:5286-5307`.

Comandos principales ejecutados desde la raíz:

```bash
python3 scripts/cdad_packet.py --help

python3 scripts/cdad_packet.py validate-request --help
python3 scripts/cdad_packet.py render --help
python3 scripts/cdad_packet.py validate-packet --help

python3 scripts/cdad_packet.py validate-request --project-root . --execution-context .cdad/executions/exec-010-001-documentary-contracts-002/execution.json --request .cdad/packets/010-001-documentary-contracts-architect-draft-004/REQUEST.json

python3 scripts/cdad_packet.py validate-packet --project-root . --execution-context .cdad/executions/exec-010-001-documentary-contracts-002/execution.json --request .cdad/packets/010-001-documentary-contracts-architect-draft-004/REQUEST.json --packet .cdad/packets/010-001-documentary-contracts-architect-draft-004/PACKET.md

python3 scripts/cdad_packet.py render --project-root . --execution-context .cdad/executions/exec-010-001-documentary-contracts-002/execution.json --request .cdad/packets/010-001-documentary-contracts-architect-draft-004/REQUEST.json --route C

git status --short
git diff --stat
git rev-parse HEAD
```

Los validadores terminaron con **rc=0**, sin salida. Las comparaciones completas de paquete e identificación se ejecutaron en memoria mediante `subprocess.check_output` y `assert`; el contrato y los documentos de entrada se contrastaron mediante `hashlib.sha256`.

La propuesta se construyó y verificó en memoria mediante `python3 -B -`, Python **3.13.5**. Se comprobaron seis sustituciones únicas y se imprimió su diff con `difflib.unified_diff`. La validación estructural ejecutada fue:

```python
m = runpy.run_path(
    "skills/cdad-cycle/scripts/cdad_packet.py",
    run_name="cdad_packet_validation_only"
)
tasks, strategy = m["_plan_tasks_from_contract"](plan.encode())
m["_check_plan_tasks"](tasks)
m["_check_plan_validation_plan"](tasks, strategy)
old_tasks, old_strategy = m["_plan_tasks_from_contract"](original.encode())
assert strategy == old_strategy
assert [t["id"] for t in tasks] == ["T1", "T2", "T3", "T4", "T5", "T6"]
assert all(
    t == o
    for t, o in zip(tasks, old_tasks)
    if t["id"] not in ("T1", "T4")
)
```

Salidas:

```text
INTAKE PASS: complete canonical packet (6332 bytes); complete route C identification matches.
PLAN PASS: canonical parse, dependencies, per-task validation; T1-T6 retained; only T1/T4 machine-readable entries changed; 6 unique replacements; no files written.
SPEC unchanged: a01969d7f51da614c6e502d8660bafea17ad5ae8bb7caf5aea624f43927d94ac
Python: 3.13.5
```

Hashes de los documentos de entrada:

```text
spec.md: a01969d7f51da614c6e502d8660bafea17ad5ae8bb7caf5aea624f43927d94ac
plan.md: 9fee79a36dccb0faf6dbe9372f7d946e9aebf4886844b80162eb399fd506a478
```

Estado observado al inicio y al final:

```text
 M docs/.cdad-state.json
?? docs/specs/010-000-continuity-relative-root/discovery.md
?? docs/specs/010-001-documentary-contracts/
```

Salida final de `git diff --stat`:

```text
 docs/.cdad-state.json | 374 +++++++++++++++++++++++++++++++++++++++-----------
 1 file changed, 296 insertions(+), 78 deletions(-)
```

HEAD observado al inicio y al final:

```text
bd69977694d3eea936f905c348ce4350e4c127d4
```

**Archivos modificados por este encargo: ninguno. Commit creado: ninguno.** La propuesta se devuelve como texto, sin materializar archivos. No ejecuté implementación, generación, instalación ni suite. El estado preexistente no se atribuye a este trabajo ni demuestra ausencia de escrituras transitorias. Ambos documentos permanecen pendientes de aprobación de Pablo.

## Aprobación

Plan aprobado por Pablo el 2026-10-31 con la spec, mediante el mismo mandato HITL delegado. Versión aprobada: 4, con el bloque `plan-tasks` de T1–T6. Observaciones O1 y O2 del plan-review-003 no bloqueantes, diferidas con motivo en `owner-approval-2026-10-31.md`.

Status: Approved by Pablo on 2026-10-31
