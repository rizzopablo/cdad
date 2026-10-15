# Architect draft 001 — 004-002 (Codex gpt-6-astra, 2026-09-29)

> Materializado por el orquestador, verbatim salvo links absolutos → relativos al repo. Borrador **no aprobado**.

**Contrato verificado. Entrega de solo lectura; spec y plan sin aprobar.** El borrador adopta las opciones recomendadas de D1–D4, separadas al final para decisión explícita del dueño. Las interfaces nuevas se identifican como propuestas, no como capacidades existentes.

**A. Discovery**

El problema es separar tres cosas hoy mezcladas: política del proyecto, identidad durable de ejecución y observaciones de cada despacho. El alcance aprobado exige hacerlo extendiendo `prepare`, con permisos coherentes y recuperación segura ([plan.md:199](docs/epics/epic-004-single-source-planning/plan.md:199)).

| Evidencia verificada | Consecuencia |
|---|---|
| `prepare` carga obligatoriamente un contexto previo, deriva el contrato y produce request, paquete y binding del state ([cdad_packet.py:575](skills/cdad-cycle/scripts/cdad_packet.py:575)). | Extender este productor; eliminar la preparación manual de identidad cuando los datos ya existen. |
| `execution` liga `runtime` a la identidad; contiene un único par de modelos ([cdad_packet.py:23](skills/cdad-cycle/scripts/cdad_packet.py:23), [cdad_packet.py:160](skills/cdad-cycle/scripts/cdad_packet.py:160)). | Un cambio de runtime por rol no debe cambiar la ejecución lógica. |
| El contexto real declara `multi-runtime` y modelos `null`; el ledger documenta la operación por rol ([execution.json:3](.cdad/execution.json:3), [dispatch-ledger.md:3](docs/specs/004-002-project-execution-bootstrap/dispatch-ledger.md:3)). | El consumidor multiruntime ya existe; no es un caso hipotético. |
| `path_policy` acepta raíces, archivos exactos y convenciones de tests co-ubicados. El clasificador resuelve por prioridad: tests, co-ubicados, implementación, documentación ([cdad_packet.py:111](skills/cdad-cycle/scripts/cdad_packet.py:111)). | Hay una base reutilizable, pero falta detectar conflictos de clasificación. |
| Los scopes predeterminados del test-writer incluyen únicamente `test_roots`; omiten archivos exactos y tests co-ubicados ([cdad_packet.py:550](skills/cdad-cycle/scripts/cdad_packet.py:550)). | Corregir defaults además de adaptar permisos. |
| OpenCode usa raíces de implementación prefijadas; Claude Code también mantiene globs propios ([cdad-generate.py:404](scripts/cdad-generate.py:404), [claude-code-path-guard.sh:165](scripts/claude-code-path-guard.sh:165)). | Los permisos deben consumir la misma clasificación efectiva que el paquete. |
| `prepare` reemplaza `active_packet`; escribe archivos y usa un `.tmp` fijo para state. Hay rollback ante `OSError`, sin exclusión ni recuperación durable de interrupciones en ese camino ([cdad_packet.py:613](skills/cdad-cycle/scripts/cdad_packet.py:613)). | Conservar un único paquete activo requiere exclusión y publicación recuperable. |
| La validación `ordinary` retorna antes de comprobar autoridad y feature activa; esas comprobaciones aparecen en la excepción de epic-003 ([cdad_packet.py:214](skills/cdad-cycle/scripts/cdad_packet.py:214)). | El bootstrap necesita validación de autoridad independiente de la política de modelos. Un hash de contrato no prueba aprobación. |
| El instalador exige `agents/` aunque despliega agentes desde staging ([install.sh:540](install.sh:540)). | Retirar esa precondición residual y probar la distribución real. |

Los consumidores verificados son el orquestador generado, el CLI instalable, los adaptadores OpenCode/Claude Code y los validadores de paquetes/métricas. El orquestador activa el camino de paquetes solamente si encuentra `execution.json` ([orchestrator.md:21](sources/roles/orchestrator.md:21)). La documentación exige construirlo manualmente y deja al architect standalone en legacy ([handoff-prompts.md:15](skills/cdad-cycle/references/handoff-prompts.md:15)).

La métrica existente ya identifica rol, paquete, runtime y modelo; debe conservarse su interoperabilidad sin convertir esta feature en recepción automática ([packet-metric.schema.json:6](skills/cdad-cycle/assets/packet-metric.schema.json:6)).

**VERIFY delimitado:** esta inspección no demuestra cómo una configuración de proyecto queda efectivamente activada en cada runtime instalado, ni demuestra controles por rol en Codex. La aceptación exige evidencia de activación o una limitación explícita antes del despacho. No se presupone una API nueva del runtime.

La fricción existente justifica diagnosticar capacidad y verificar resultados; no reconstruir allowlists. El recorrido vivo anterior fue legacy, no un ciclo con paquetes ([closure.md:15](docs/specs/004-001-canonical-runtime-artifacts/closure.md:15), [friction-intake:80](docs/epics/epic-003-context-efficiency/friction-intake-004-001.md:80)).

**B. Borrador de spec — 004-002-project-execution-bootstrap**

**Feature ID:** `004-002-project-execution-bootstrap` · **Epic:** `epic-004-single-source-planning`  
**Estado:** borrador no aprobado. ADR-011 gobierna autoridad, capacidades y límites.

**1. Descripción funcional**

Una política versionada del proyecto define la clasificación de archivos y los espacios temporales permitidos. El `prepare` existente utiliza esa política y la autoridad vigente para iniciar o reanudar una ejecución durable y preparar encargos.

La identidad lógica permanece estable entre roles, runtimes, sesiones y reintentos. Cada intento de despacho registra sus propias observaciones. Los scopes y adaptadores derivan de la misma política efectiva; sus límites se declaran antes del despacho.

Quedan fuera: recepción automática de resultados de 003-002, budgets, detección de estancamiento de 003-003, planificación de 004-003 y un sandbox general.

**2. Contrato**

Se conserva la entrada existente:

```text
cdad_packet.py prepare --project-root <raíz>
  --role <rol> --substage <subfase> --objective <encargo>
  [opciones existentes]
```

Extensiones propuestas, dentro del mismo CLI:

- `prepare --propose-policy`: imprime una propuesta determinista y termina sin modificar política, ejecución, state ni paquetes. No requiere rol/subfase/objetivo.
- `prepare --resume-packet <id>`: recupera el paquete activo compatible, conservando sus bytes e identidad; rechaza opciones que pretendan modificarlo.
- `prepare --reconcile-policy <sha256> --decision-ref <ruta>`: acepta una nueva revisión únicamente con decisión vigente y sin paquete pendiente.
- `prepare --migrate-execution`: migración explícita del contexto v1 conforme a PD-10.
- `prepare --record-dispatch <packet-id> --attempt-id <id>`: registra un intento con runtime/modelos/sesión observados; no genera otro paquete ni recibe su resultado. Repetir el mismo registro es idempotente; datos contradictorios fallan.

Los nombres anteriores son interfaces **propuestas para implementar**. Sus combinaciones incompatibles terminan con diagnóstico y código distinto de cero.

Artefactos propuestos:

| Artefacto | Contrato |
|---|---|
| `docs/cdad-policy.json` | Única política editable: versión de esquema, `path_policy` existente y raíces temporales relativas al proyecto. No contiene selección de modelos ni aprobación implícita. |
| `.cdad/execution.json`, v2 | Identidad, feature, epic nullable para standalone, alcance, autoridad verificable, política de modelos y snapshot/hash de política. |
| `.cdad/packets/<id>/` | Request, paquete y evidencia de capacidades efectiva para ese encargo, ligados al hash de política. |
| `.cdad/executions/<execution-id>/dispatches/<attempt-id>.json` | Registro por intento: ejecución, paquete, rol/subfase, runtime, modelo configurado/reportado, sesión, fecha y procedencia de observaciones. |
| `state.execution` | Referencia coherente a la ejecución durable; no otra definición editable de política ni un runtime global. |

La autoridad se verifica mediante una referencia a una decisión explícita del usuario o delegación vigente: identidad/alcance afectados, estado, evidencia y vencimiento. Se conserva la delegación existente cuando corresponda. Si falta información verificable, `prepare` informa exactamente qué decisión falta; no interpreta nombres de archivos o una cadena “Approved” como autorización suficiente.

**Postcondiciones**

1. **PD-1 — Política única y propuesta sin autoridad.** La búsqueda usa exclusivamente `docs/cdad-policy.json`, relativa a `--project-root`. Una propuesta idéntica sobre el mismo layout produce los mismos bytes y ninguna escritura. Una política ausente o inválida impide producir un paquete autorizado; no activa defaults silenciosos.

2. **PD-2 — Clasificación inequívoca.** Se validan rutas normalizadas, archivos exactos, raíces y convenciones de co-ubicación. Se rechazan escapes por `..`, rutas absolutas, symlinks fuera del proyecto y asignaciones incompatibles.  
   Se permiten únicamente estas excepciones explícitas dentro de implementación: raíces/archivos declarados como tests y nombres de tests bajo `colocated_test_roots`; se sustraen de implementación. Solapamientos redundantes de la misma clase son válidos. Documentación contra tests o implementación es conflicto. Un nombre de test fuera de las ubicaciones declaradas no concede permisos. Un path sin clasificar no puede incluirse en un scope de producto que requiera clasificación.

3. **PD-3 — Bootstrap autorizado.** Sin contexto previo, con state, contrato, política y autoridad válidos, `prepare` crea una sola identidad y publica contexto, binding y paquete coherentes. Autoridad ausente, revocada, vencida o fuera de alcance; contrato no aprobado; feature incompatible o cerrada: error específico y ninguna publicación.

4. **PD-4 — Identidad y reanudación.** Nuevos roles, runtimes, modelos o sesiones conservan `execution_id` para la misma ejecución activa. Reanudar un paquete conserva `packet_id` y bytes. Otro encargo crea otro paquete únicamente si el anterior está `completed` o `failed`; `prepared` y `dispatched` impiden reemplazo. Cambiar feature o autoridad incompatible exige resolver explícitamente la ejecución anterior.

5. **PD-5 — Política congelada y reconciliación.** Contexto y paquete conservan snapshot y hash verificables. Cualquier cambio de bytes en la política se detecta antes de preparar o reanudar. La reconciliación requiere referencia de decisión, hash esperado y ningún paquete pendiente; conserva historial y paquetes anteriores. Nunca actualiza silenciosamente permisos de un encargo activo.

6. **PD-6 — Observaciones por intento.** Dos roles en runtimes distintos y dos reintentos del mismo rol quedan registrados por separado bajo la misma ejecución. Valores no conocidos son `null`, con procedencia explícita cuando se conocen. `multi-runtime` no se usa como runtime observado de un intento. Preparar un paquete no afirma que fue ejecutado; registrar el intento no afirma que terminó. Cambiar de modelo no concede autoridad.

7. **PD-7 — Scopes completos desde política.** Defaults y opciones explícitas respetan clasificación y contrato del rol. Test-writer recibe tests dedicados, archivos exactos y co-ubicados autorizados, sin implementación; implementer puede editar implementación autorizada, excluyendo todos los tests; roles lectores no reciben escritura de producto. Los scopes del encargo pueden restringir la política, nunca ampliarla.

8. **PD-8 — Permisos y capacidades trazables.** Los adaptadores OpenCode y Claude Code consumen la política efectiva, incluidas raíces `scripts`, `agents`, `skills`, archivos exactos y layouts Odoo. La evidencia previa al despacho identifica hash de política, configuración activada, herramientas mediadas y límites. Cada barrera retenida tiene prueba positiva y negativa. Si un runtime no puede representar o activar una restricción, declara la diferencia antes del despacho; no informa coherencia inexistente.

9. **PD-9 — Temporales y acciones externas.** El paquete diferencia escritura de producto, temporales autorizados y acciones externas con autoridad referenciada. Una raíz temporal no puede superponerse al producto ni escapar del proyecto. No declarar temporales significa que no se autorizan. Falta de capacidad devuelve operación, causa y limitación al coordinador. No se agregan allowlists de Bash ni autorizaciones externas implícitas.

10. **PD-10 — Compatibilidad explícita.** Contextos v1 y paquetes históricos siguen siendo inspeccionables/validables según su versión. Para preparar trabajo nuevo desde v1 se exige migración explícita: conserva identidad y evidencia histórica, contrasta el `path_policy` anterior con la política aprobada y no inventa observaciones por rol. Una discrepancia exige reconciliación. No migra con paquete pendiente. `--execution-context` conserva su función de ubicación, pero no introduce otra política editable.

11. **PD-11 — Exclusión y recuperación.** Un único escritor por proyecto protege lectura del estado, reserva de identificadores y publicación. Dos preparaciones simultáneas no sobrescriben paquetes ni state: una obtiene resultado y la otra recibe diagnóstico de ocupación o paquete pendiente.  
    Se prueba interrupción tras reservar identidad, escribir contexto provisional, escribir paquete y antes/después de publicar state. La siguiente invocación recupera una generación coherente o conserva la anterior, sin borrar archivos ajenos. No imprime un paquete despachable antes de completar su publicación. No se promete despacho paralelo ni tolerancia a pérdida física de almacenamiento.

12. **PD-12 — Consumidor instalado y standalone.** Desde una instalación aislada, sin checkout como ruta de ejecución, funcionan propuesta, validación, bootstrap, preparación y reanudación. Instalar agentes requiere staging válido, no `agents/` fuente; permanecen las dependencias reales de skills/scripts. Standalone con spec aprobada prepara roles posteriores al architect sin epic ficticio. Architect standalone conserva el camino legacy documentado mientras no exista contrato de entrada aprobado para ese caso.

13. **PD-13 — Recorrido real y evidencia.** Se completa un ciclo real desde proyecto consumidor con paquetes para architect, test-writer, implementer, reviewer y scribe, sesiones separadas y contexto reducido; los roles lectores entregan texto para materialización. Se registra continuidad de identidad, runtime/modelo por intento, configuración efectiva, comandos/resultados, gates, desviaciones y fricción. No se presenta una prueba estática o fixture como ejecución real.

**3. Invariantes verificables**

1. Un único productor de paquetes: `prepare` y su renderizado canónico; sin paquetes reparados manualmente.
2. Autoridad y aprobación nunca se deducen de clasificación, detección de layout, runtime o modelo.
3. Test-writer no inspecciona implementación; implementer no modifica tests aprobados; architect/reviewer/scribe no materializan producto.
4. Bash conserva la política permisiva vigente. Los controles por herramienta no se describen como sandbox ni como mediación de los procesos que Bash ejecuta.
5. Política editable única; snapshots históricos inmutables y verificables.
6. Un solo paquete activo y un solo epic activo; standalone no fabrica un epic.
7. Archivos ajenos, autoridad previa y campos de state no afectados sobreviven a preparación, migración y recuperación.
8. La selección de modelos conserva su fuente existente; las observaciones registradas no sustituyen ese mapa.

**4. Criterios de aceptación**

1. PD-1–PD-12 cubiertas por tests de comportamiento con trazabilidad; casos negativos verifican ausencia de publicación o conservación del estado anterior.
2. Matriz de layouts: repo CDAD, convencional, tests co-ubicados y Odoo. Matriz de consumidores: v1 migrado, v2 reanudado y standalone.
3. OpenCode y Claude Code: pruebas de configuración derivada más evidencia de activación y fronteras en runtime. Codex: limitación concreta declarada, sin atribuirle controles no demostrados.
4. Recuperación verificada en los cinco puntos de PD-11 y prueba concurrente sin sobrescrituras.
5. Validadores existentes en PASS, o sustitución de assertions con trazabilidad y garantía equivalente.
6. Recorrido PD-13 terminado, sin denegaciones legítimas pendientes de disposición y sin incidentes materiales sin resolver. Métricas desconocidas permanecen desconocidas; no se exige ahorro porcentual.
7. Documentación mínima reproducible de instalación, aprobación de política, primer `prepare`, reanudación, migración y resolución de cambio de política.

**Status: Draft — pendiente de decisión explícita del usuario sobre D1–D4 y aprobación de spec/plan.**

**C. Plan de tareas internas**

Cada tarea implementable sigue RED → GREEN en sesiones separadas → revisión del delta → verificación del orquestador. El cierre registra contrato, archivos realmente cambiados, snapshot probado y disposición de desviaciones.

| Tarea | Alcance RED → GREEN | Dependencias |
|---|---|---|
| T1 | Política, propuesta, clasificación y excepciones explícitas; fixtures de cuatro layouts. PD-1/2. | D1 y spec aprobadas. |
| T2 | Bootstrap, autoridad y compatibilidad standalone; identidad v2 y migración v1. PD-3/4/10/12 parcial. | T1, D2/D4. |
| T3 | Snapshot, reconciliación, exclusión y recuperación ante interrupciones. PD-5/11. | T2. |
| T4 | Registro por intento, unknown explícito y compatibilidad con métricas; sin recepción automática. PD-6. | T3, D3. |
| T5 | Scopes completos y adaptación de permisos desde política; temporales y declaración de capacidades. PD-7/8/9. | T1–T4. |
| T6 | Instalación aislada sin `agents/` fuente, consumidores instalados, documentación y regresiones. PD-10/12. | T5. |
| T7 | Recorrido real completo, observación por intento, supervisión y cierre. PD-13 y aceptación. | T6. |

T7 es validación operativa: no se fabrica un RED artificial. Los defectos descubiertos abren correcciones acotadas con RED propio. El recorrido debe usar una tarea real autorizada del consumidor; sus tests y artefactos sintéticos no sustituyen esa evidencia.

**D. DECISIONES DEL DUEÑO**

| Decisión | Opción recomendada, usada en el borrador | Alternativas y costo |
|---|---|---|
| **D1. Ruta de política** | `docs/cdad-policy.json`, versionada; `.cdad/` conserva ejecución y derivados. | `.cdad/project-policy.json` exige excepción al ignore y revisar el contrato actual que excluye `.cdad/` de Git. Múltiples ubicaciones/overrides agregan precedencia y riesgo de fuentes competidoras. |
| **D2. Compatibilidad** | Lectura/validación histórica v1; migración explícita a v2 antes de preparar trabajo nuevo, conservando ID. | Migración automática reduce pasos pero oculta una decisión sobre política. Corte completo v1 simplifica código y rompe consumidores/fixtures existentes. Soporte de escritura v1 indefinido mantiene dos modelos operativos. |
| **D3. Registro por rol** | Registro durable por **intento de despacho**, ligado a paquete y ejecución; campos desconocidos `null`. El ledger Markdown interino queda como evidencia histórica. | Un registro por rol pierde reintentos/cambios de modelo. Solo Markdown evita esquema nuevo, pero deja validación y correlación manuales. Ampliar métricas puede reutilizar estructura, pero acopla preparación con recepción de 003-002. |
| **D4. Architect standalone** | Mantener entrada legacy del architect; bootstrap por paquetes para roles con spec aprobada, sin epic ficticio. | Agregar un nuevo contrato de intake standalone permite paquetes desde Discovery, pero amplía contratos, aprobación y validadores más allá del camino existente. |

Estas son decisiones pendientes sobre el diseño propuesto, no una solicitud de repetir autorizaciones ya vigentes.

**Evidencia del rol**

- Archivos modificados: **ninguno**. Commits creados: **ninguno**.
- HEAD inspeccionado: `bcaf2965c93c36c16579f3687fb24c05587c71cf`.
- `git status --short` inicial y `git status --porcelain` final: salida vacía.
- `sha256sum docs/epics/epic-004-single-source-planning/plan.md`: `e8546c5b69c44f0cb1dbd1061b4e499adbb260be08b548802cfe446afcbcf126`.
- `sha256sum skills/cdad-cycle/packets/common.md skills/cdad-cycle/packets/roles/architect.md skills/cdad-cycle/packets/substages/architect-draft.md`: los tres hashes coinciden exactamente con el paquete.
- Exploración mediante `rg`, `nl -ba`, `sed`, `cat` y comandos Git de lectura; comandos exactos y salidas conservados en el transcript. La búsqueda inicial en el wrapper no encontró definiciones; se inspeccionó después la implementación canónica instalable. Dos lecturas truncadas mediante `head` produjeron `Broken pipe`, sin efecto sobre archivos.
- No ejecuté `prepare`, instaladores ni tests: esta entrega verifica evidencia y propone contratos; no acredita implementación ni aceptación operativa.