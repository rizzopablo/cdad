# Discovery — 010-001-documentary-contracts

**Resultado:** existe una base compatible para incorporar criterios documentales sin crear etapas ni acumular permisos. La brecha principal es contractual: distinguir el documento producido de sus fuentes y verificadores, y separar la comprobación estructural del juicio semántico. **Este informe no es una spec ni una aprobación.**

## 1. Landscape documental verificado

### Fuentes y distribución

| Superficie | Comportamiento verificado | Consecuencia |
|---|---|---|
| `sources/roles/*.md` | Son las fuentes editables de los roles; el generador compone sus contratos en el orquestador. `sources/roles/architect.md:1-11`; `scripts/cdad-generate.py:740-745`. | Las obligaciones documentales deben nacer en fuentes, no mediante edición manual de agentes. |
| `skills/cdad-cycle/references/` | Existe el patrón de una referencia normativa única y obligaciones de rol que apuntan a ella. `skills/cdad-cycle/references/design-principles.md:3-5`; `docs/systemPatterns.md:137-150`. | Es un precedente reutilizable para compartir criterios sin duplicarlos. |
| Paquetes | El renderer compone exclusivamente `common.md`, el bloque del rol y el de su subfase; registra sus hashes. `skills/cdad-cycle/scripts/cdad_packet.py:1947-1953,1991-1994`. | Cambiar solamente las fuentes de agentes no basta para transportar una nueva obligación por paquete. |
| Generación | `make staging` genera ambos runtimes; `make agents` promueve sus salidas. `Makefile:10-18`. | La validación futura debe cubrir fuentes y artefactos distribuidos. |
| Instalación | El instalador recorre todos los archivos de cada skill seleccionado y conserva modificaciones locales como conflictos; los agentes proceden de staging. `install.sh:1261-1286,1302-1307`. | Una referencia dentro de un skill ya distribuido tiene una vía existente de instalación. |
| Estado y dominio | La plantilla contiene `stack`; el agente del paquete se deriva del rol más ese valor. El generador produce variantes genéricas y Odoo. `skills/cdad-cycle/assets/state-template.json:1-8`; `skills/cdad-cycle/scripts/cdad_packet.py:6412-6425`; `scripts/cdad-generate.py:834-837`. | No hay fundamento para decidir aquí un nuevo selector documental ni para sustituir Odoo por documentación. Esa decisión corresponde a 010-002. `docs/epics/epic-010-documentary-specialization/plan.md:92-94`. |

### Responsabilidades que deben conservarse

- **Architect:** explora y devuelve borradores; no modifica ni aprueba el producto. `sources/roles/architect.md:68-76,87-92`.
- **Test-writer:** construye el oráculo desde el contrato, sin inspeccionar la implementación; edita únicamente tests autorizados. `sources/roles/test-writer.md:18-24,33-40`.
- **Implementer:** implementa el comportamiento aprobado y no modifica sus tests. Su contrato está expresado actualmente en términos de código. `sources/roles/implementer.md:18-24,38-44`.
- **Reviewer:** examina artefacto y contrato en una sesión independiente, sin editar ni aprobar. Los hallazgos requieren fundamento y ubicación; debe declarar abstenciones. `sources/roles/reviewer.md:21-43,63-68`.
- **Scribe:** produce borradores de Memory Bank; explícitamente no es el agente general de documentación. `sources/roles/scribe.md:15-28,37-42`.
- **Orquestador:** coordina y materializa los resultados read-only, pero no ejecuta trabajo de rol inline. `sources/roles/orchestrator.md:118-142`.

El plan aprobado conserva esta separación y reserva las aprobaciones a Pablo. `docs/epics/epic-010-documentary-specialization/plan.md:55-69,99-106`.

### Capacidades existentes de alcance y verificación

**La escritura documental ya es admisible, pero no es el default del implementer.** El validador permite clases `implementation` y `docs` para ese rol; sus alcances predeterminados incluyen solamente implementación. Para selectores de archivo documental exacto, exige declararlos en `documentation_files`. `skills/cdad-cycle/scripts/cdad_packet.py:1461-1474,2266-2276`.

**Los insumos no tienen protección individual declarada por hash.** Cada entrada de `inputs` tiene exactamente `path` y `purpose`; la validación comprueba su pertenencia al alcance de lectura. El conjunto de campos del request es cerrado. `skills/cdad-cycle/scripts/cdad_packet.py:1743-1764,1922-1928`.

**La recepción no acredita fidelidad semántica.** El recibo mantiene `semantic_status: pending`. La comprobación de alcance puede quedar `unknown` sin una observación confiable; con ella, contrasta las rutas modificadas contra `write_scope`. `skills/cdad-cycle/scripts/cdad_result.py:364-400,745-751`.

**Existe un precedente explícito para no confundir presencia con verdad.** El comprobador doctrinal verifica marcadores y ausencias, pero declara que no demuestra integridad, suficiencia del razonamiento ni equivalencia de una regeneración. `scripts/cdad-doctrine-check.py:29-35`.

## 2. Mapa de brechas

| Brecha | Evidencia y riesgo | Cambio mínimo propuesto |
|---|---|---|
| **Criterio documental compartido** | El plan exige distinguir evidencia, propuesta, contradicción y pendiente; los contratos actuales contienen obligaciones de evidencia por rol, pero no desarrollan conjuntamente esas categorías. `plan.md:61-66`; `sources/roles/architect.md:71-72`; `sources/roles/reviewer.md:31-43`. | Una casa normativa compartida y obligaciones breves por rol que remitan a ella. |
| **Código frente a producto autorizado** | El contrato del implementer dice “ONLY implementation code”, aunque el validador admite escritura `docs`. `sources/roles/implementer.md:18,40`; `cdad_packet.py:1469-1470`. | Explicitar la producción documental autorizada sin convertir al implementer en escritor general de `docs/**`. |
| **Documento, fuente y oráculo pueden compartir clase** | `docs` es una clasificación de rutas; no expresa si un archivo es producto, fuente o plantilla protegida. El implementer puede recibir escritura documental y el test-writer lectura documental. `cdad_packet.py:1466-1474`; `docs/cdad-policy.json:2-5`. | Declarar esas funciones en el encargo y mantener las fuentes/oráculos fuera del alcance editable de GREEN. |
| **Independencia del verificador documental** | La regla actual prohíbe al test-writer leer implementación; los mapas genéricos deniegan `src/**` y `lib/**`, no identifican un documento producido como implementación. `sources/roles/test-writer.md:19-24`; `scripts/cdad-generate.py:396-408`. | Explicitar que tampoco deriva su oráculo leyendo el resultado documental que debe verificar. La concreción de selección/permisos queda para 010-002. |
| **Verde estructural frente a aceptación semántica** | La recepción ya mantiene el juicio pendiente, pero falta el contrato específico para revisar afirmaciones contra fuentes. El plan exige esa separación. `cdad_result.py:745-751`; `plan.md:64-66,79-84`. | Registrar por separado controles automáticos y revisión semántica, cada uno con resultado, referencias y limitaciones. |
| **Distribución incompleta de nuevas reglas** | Agentes y bloques estáticos de paquete son superficies distintas. Existe un precedente que verifica ambas y su distribución generada. `scripts/cdad-generate.py:631-668`; `tests/test_006_004_u3_principle_single_source.py:23-37,58-79`. | Verificar que los consumidores reciban el criterio por la ruta aprobada, sin copiar íntegramente la norma en cada superficie. |

## 3. Propuesta mínima para discutir en brainstorm

### Contenido común propuesto

Sin fijar todavía sintaxis ni nombres de archivos:

- **Evidencia:** afirmación respaldada por una fuente localizable, sin atribuirle más de lo que demuestra.
- **Propuesta:** alternativa planteada por el autor, distinguida del hecho observado y de una decisión aprobada.
- **Contradicción:** afirmaciones incompatibles conservadas con sus respectivas fuentes; sin inventar consenso.
- **Pendiente:** información no acreditada o decisión abierta, con la condición necesaria para resolverla.

Esta propuesta desarrolla el compromiso aprobado de trazabilidad y tratamiento de incertidumbre; no agrega aprobación autónoma. `docs/epics/epic-010-documentary-specialization/plan.md:61-66,99-106`.

### Límite de escritura propuesto

Cada encargo documental debería identificar:

1. Fuentes autorizadas.
2. Producto editable.
3. Verificadores e insumos de aceptación protegidos.
4. Evidencia esperada y limitaciones.

GREEN modificaría únicamente el producto autorizado. El test-writer conservaría los verificadores; reviewer y architect seguirían read-only. Los demás roles devolverían observaciones para Memory Bank, sin actualizarlo directamente. Es la separación ya exigida por el plan. `plan.md:55-69,85-86`.

**Aplicación compatible:** preferir un subárbol dedicado del producto sobre permisos amplios a `docs`; si se elige un archivo exacto, respetar su declaración en la política. No hace falta inventar un campo nuevo de request para comenzar a expresar el contrato, porque ya existen `inputs`, `write_scope`, `invariants` y `evidence_required`. Esto no equivale a protección mecánica por archivo. `cdad_packet.py:1461-1464,1743-1764`.

### Alternativas y criterio

**Referencia dentro del ciclo existente frente a skill nuevo:** recomiendo explorar primero una referencia instalable en `skills/cdad-cycle/references/`, cuyo nombre se decidiría en Specification. Reutiliza el precedente de fuente única y la distribución existente, sin ampliar ahora el catálogo del instalador. Un skill separado quedaría justificado si 010-002 demuestra una necesidad de carga independiente. `design-principles.md:9-18`; `install.sh:66,1261-1286`.

**Regla general frente a excepción documental:** conviene expresar la frontera como *quien produce no modifica su oráculo*, aplicable a código y documentación, y concretar después los límites de cada producto. No recomiendo una excepción que autorice al implementer a editar documentación indiscriminadamente. El plan exige especialización sin permisos acumulados. `plan.md:25-27,55-60`.

## 4. Verificación futura: alcance y límites

**Automatizable:** presencia de las categorías y obligaciones acordadas, referencias localizables, separación declarada de rutas, consistencia de fuentes/paquetes/agentes y distribución instalable. El repositorio ya tiene comprobaciones documentales y precedentes de pruebas sobre procesos reales en copias descartables. `scripts/cdad-doctrine-check.py:7-21`; `tests/test_006_004_u3_principle_single_source.py:17-37`.

**Revisión semántica independiente:** contrastar afirmaciones con las fuentes, detectar respaldo insuficiente, contradicciones omitidas y referencias que existen pero no sostienen la afirmación. Un enlace existente no prueba fidelidad. Estos defectos están comprometidos expresamente para el piloto, sin promesa de detección infalible. `plan.md:79-84,95-96`.

**No propuesto aquí:** un motor genérico de verdad, puntajes semánticos automáticos, formatos binarios, corpus real, nuevos agentes o nuevos campos de estado. Son exclusiones o decisiones diferidas por el plan. `plan.md:32-37,49-51,92-97`.

## 5. Preguntas abiertas para Pablo

1. **¿Las categorías deben tener una representación Markdown obligatoria o basta una distinción explícita y localizable?** La primera simplifica controles estructurales; la segunda evita imponer un formato innecesario.
2. **¿Qué localizador mínimo debe exigirse según la fuente?** Para el piloto Markdown puede acordarse archivo más línea/sección; versiones y documentos cambiantes requieren decidir cómo conservar la referencia.
3. **¿Qué pendientes impiden aceptar un entregable y cuáles pueden permanecer visibles?** Debe fijarlo el contrato funcional; ninguna ausencia de evidencia debería convertirse silenciosamente en hecho.

La elección del perfil documental combinado con Odoo permanece en 010-002; no la doy por resuelta. `plan.md:46,92-94`.

## 6. Evidencia de ejecución

### Intake

Ruta C validada para el único paquete identificado:

- `validate-request`: **rc=0**, sin stdout ni stderr.
- `validate-packet`: **rc=0**, sin stdout ni stderr.
- Comparación binaria de `PACKET.md` con el render completo: **idénticos**.
- Contexto de ejecución: **schema 2**.
- SHA-256 del contrato: `d041da0a01c5ae5e097442c3ee87ab99e7f0fd1fe3f1dadd5913779cca6c6cf7`.
- Render completo: **5647 bytes**, SHA-256 `57e6b04ffecdd50e8047eb31310b8ba769381181415a4698b115536d888972ae`.

Comandos ejecutados, desde la raíz del proyecto:

```bash
python3 -B skills/cdad-cycle/scripts/cdad_packet.py validate-request --project-root . --request .cdad/packets/010-001-documentary-contracts-architect-discovery-002/REQUEST.json

python3 -B skills/cdad-cycle/scripts/cdad_packet.py validate-packet --project-root . --request .cdad/packets/010-001-documentary-contracts-architect-discovery-002/REQUEST.json --packet .cdad/packets/010-001-documentary-contracts-architect-discovery-002/PACKET.md

python3 -B skills/cdad-cycle/scripts/cdad_packet.py render --project-root . --request .cdad/packets/010-001-documentary-contracts-architect-discovery-002/REQUEST.json --route C
```

La igualdad completa se comprobó mediante Python `subprocess.check_output`, `Path.read_bytes()` y `assert`; hashes mediante `hashlib.sha256`. Entorno observado: **Python 3.13.5**, con `-B`.

### Cambios y commit

**Archivos modificados por este encargo: ninguno. Commit creado: ninguno.**

Al inicio y al cierre, `git status --short` mostró las mismas rutas preexistentes:

```text
 M docs/.cdad-state.json
?? docs/specs/010-000-continuity-relative-root/discovery.md
```

`git rev-parse HEAD` permaneció en:

```text
bd69977694d3eea936f905c348ce4350e4c127d4
```

No atribuyo esos cambios previos al encargo ni presento el estado final como prueba de ausencia de escrituras transitorias. No ejecuté suite, generación ni instalación: este paquete autoriza Discovery read-only, no cierre de implementación. `sources/roles/architect.md:165-176`; `skills/cdad-cycle/packets/common.md:3`.
