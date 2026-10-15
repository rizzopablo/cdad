> Materializado por el orquestador desde `architect-draft-002` (Codex gpt-6-astra), verbatim salvo links relativos. Ver `spec-gate-claude-002.md` para las condiciones de aprobación.

## Spec — 004-002-project-execution-bootstrap

**Feature ID:** `004-002-project-execution-bootstrap` · **Epic:** `epic-004-single-source-planning` · **Estado:** Draft. ADR-011 gobierna autoridad, capacidades y límites.

### 1. Descripción funcional

Una política versionada del proyecto define la clasificación de archivos y los espacios temporales autorizables. El `prepare` existente utiliza esa política, el state y la autoridad vigente para iniciar o reanudar una ejecución durable y producir paquetes.

La identidad lógica de ejecución permanece estable entre roles, runtimes, sesiones y reintentos. Runtime, modelos y sesión son observaciones de cada intento de despacho, no componentes de esa identidad.

OpenCode aplica la política mediante agentes generados en `.opencode/agents/` del proyecto. Claude Code la consulta al ejecutar su guard de paths. Los scopes, los permisos representables y la evidencia de capacidades derivan de la misma política; las diferencias se declaran antes del despacho.

La adopción es exclusivamente hacia adelante. Los contextos y paquetes v1 no se convierten ni se reescriben. Los proyectos legacy conservan su funcionamiento y adoptan la política al iniciar una feature nueva. En este repositorio, 004-002 se construye con el contexto actual hasta el único corte definido en el plan; después continúa con una ejecución v2 nueva.

El recorrido real de aceptación es **la propia ejecución de 004-002 en este repositorio**, con evidencia diferenciada antes y después del corte.

Quedan fuera: migración o validación histórica v1 mediante la herramienta nueva, recepción automática de resultados de 003-002, budgets y detección de estancamiento de 003-003, procedimientos de planificación de 004-003 y un sandbox general.

### 2. Contrato

**Entrada conservada:**

```text
cdad_packet.py prepare --project-root <raíz>
  --role <rol> --substage <subfase> --objective <encargo>
  [opciones existentes compatibles]
```

**Extensiones propuestas para implementar, no interfaces existentes:**

| Modo de `prepare` | Resultado |
|---|---|
| `--propose-policy` | Imprime una propuesta determinista, sin escrituras ni aprobación. No requiere rol/subfase/objetivo. |
| Preparación ordinaria | Resuelve o inicia ejecución v2 y publica request, paquete y binding coherentes. |
| `--resume-packet <id>` | Recupera el paquete compatible sin cambiar identidad ni bytes. |
| `--reconcile-policy <sha256> --decision-ref <ruta>` | Acepta para la ejecución la revisión materializada por decisión del dueño; exige ausencia de paquete pendiente. No edita la política. |
| `--record-dispatch <packet-id> --attempt-id <id> --input <ruta>` | Registra un intento desde un documento de observaciones. En este modo, `--input` admite exactamente ese documento; no representa inputs del encargo. |

Los modos son excluyentes. Opciones incompatibles, documentos inválidos o autoridad insuficiente producen diagnóstico y salida distinta de cero, sin publicación parcial. El modo de registro no acepta resultados del trabajo ni decisiones de gates.

**Artefactos y contenido:**

| Artefacto | Contenido y propiedad |
|---|---|
| `docs/cdad-policy.json` | Única política editable. Contiene exclusivamente `schema_version`, `path_policy` y `temporary_roots`. Ningún rol CDAD recibe permiso para editarla. |
| Contexto de ejecución v2 | Identidad, feature, epic nullable, alcance, referencia verificable de autoridad, política de modelos y snapshot/hash de política. No contiene runtime/modelo global como identidad. |
| `state.execution` | Binding y referencia al contexto activo; no otra política editable. |
| `.cdad/packets/<id>/` | Request y paquete canónico, ligados a ejecución, contrato y revisión de política. |
| `.cdad/executions/<execution-id>/dispatches/<attempt-id>.json` | Intento, paquete, ejecución, rol/subfase, runtime, modelos configurado/reportado, sesión, fecha y procedencia de observaciones. Unknown explícito como `null`. |
| `.opencode/agents/` | Agentes derivados de las fuentes canónicas y la política, con manifest de hashes y procedencia. No son otra fuente editable. |

Para proyectos nuevos puede utilizarse `.cdad/execution.json`. Si esa ruta contiene evidencia v1, se conserva intacta y el nuevo contexto se crea en `.cdad/executions/<nuevo-id>/execution.json`. El binding activo permite resolverlo automáticamente; `--execution-context` conserva su función de ubicación y no introduce otra política.

La aprobación y autoridad se resuelven desde los registros del proyecto y sus referencias de decisión. El hash del contrato demuestra contenido, no aprobación. La implementación debe reconocer los registros vigentes sin exigirles retrospectivamente campos exclusivos de otro epic. Si no puede verificar una decisión necesaria, identifica la referencia o dato faltante y no publica.

**Postcondiciones:**

1. **PD-1 — Política única, propuesta y propiedad.**  
   La búsqueda utiliza únicamente `docs/cdad-policy.json`, relativa al proyecto. Una propuesta sobre entradas iguales produce bytes iguales y ninguna escritura. En el camino v2, política ausente o inválida impide preparar paquetes; no activa defaults silenciosos. La política queda excluida de todos los scopes de escritura de roles, incluso bajo un scope amplio de documentación. Su contenido no incorpora modelos, autoridad, aprobaciones ni reglas de Bash.

2. **PD-2 — Clasificación inequívoca.**  
   Se validan raíces, archivos exactos y convenciones de tests co-ubicados. Se rechazan rutas absolutas, escapes por `..`, symlinks fuera del proyecto y asignaciones incompatibles. Los tests expresamente declarados dentro de implementación se sustraen de ella; solapamientos redundantes de una misma clase son válidos. Documentación contra implementación o tests es conflicto. Un nombre de test fuera de las ubicaciones declaradas no concede permisos. Una ruta sin clasificación necesaria no puede ampliar un scope.

3. **PD-3 — Bootstrap autorizado.**  
   Con state, contrato, política y autoridad válidos, `prepare` crea una identidad v2 sin exigir que el usuario construya manualmente el contexto. Publica contexto, binding y paquete coherentes. Autoridad ausente, revocada, vencida o fuera de alcance; contrato sin aprobación verificable; feature incompatible o cerrada: error específico y ninguna publicación. Estas comprobaciones también se aplican a `model_policy: ordinary`.

4. **PD-4 — Identidad y reanudación.**  
   Dentro de una ejecución v2, cambiar rol, runtime, modelo o sesión conserva `execution_id`. Reanudar conserva `packet_id` y bytes. Un encargo nuevo solo sustituye el paquete activo cuando el anterior está `completed` o `failed`; `prepared` y `dispatched` impiden reemplazo. Cambiar feature o autoridad incompatible requiere resolver explícitamente la ejecución anterior. El corte v1→v2 de PD-10 crea otra ejecución; no se presenta como reanudación.

5. **PD-5 — Snapshot y reconciliación.**  
   Contexto y paquetes conservan snapshot/hash verificables de la política. Cambiar sus bytes bloquea nueva preparación, reanudación o registro de despacho hasta reconciliar. La reconciliación exige hash esperado, decisión del dueño y ningún paquete pendiente; conserva las revisiones históricas y no altera paquetes existentes. Los derivados de permisos deben corresponder a la revisión aceptada antes del próximo despacho. La operación no concede a un rol permiso para editar la política.

6. **PD-6 — Observaciones por intento, sin recepción.**  
   Dos roles en runtimes distintos y dos intentos del mismo paquete quedan diferenciados bajo una ejecución. Repetir un registro idéntico es idempotente; reutilizar el identificador con datos contradictorios falla sin sobrescribir. Runtime desconocido es `null`; `multi-runtime` no representa un runtime observado. Preparar no afirma despacho y registrar despacho no afirma finalización. El registro no recibe entregables, resuelve gates ni marca paquetes `completed` o `failed`. Los tests verifican expresamente esta frontera con 003-002.

7. **PD-7 — Scopes derivados completos.**  
   Defaults y scopes explícitos respetan clasificación y contrato del rol. Test-writer recibe tests dedicados, archivos exactos y co-ubicados autorizados, sin lectura de implementación ni escritura fuera de tests. Implementer puede escribir implementación autorizada, excluyendo todos los tests. Architect, reviewer y scribe no reciben escritura de producto. Los scopes pueden restringir la política, nunca ampliarla. La exclusión de `docs/cdad-policy.json` prevalece sobre cualquier permiso por clase.

8. **PD-8 — Mecanismo concreto y activación comprobada.**  
   OpenCode utiliza agentes generados en `.opencode/agents/` del proyecto, con los mismos nombres que sus equivalentes globales. Su contenido procede de las fuentes canónicas, la política y el perfil existente; no se mantienen copias editables paralelas. La publicación conserva archivos ajenos y rechaza sobrescribir derivados modificados sin resolución explícita.

   Claude Code utiliza el hook `PreToolUse` ya generado hacia `~/.claude/cdad-scripts/path-guard.sh`; el guard instalado carga la política del proyecto al ejecutarse y aplica su clasificación. En el camino v2, una política inválida no provoca fallback silencioso a globs globales.

   La verificación distingue:

   - **Derivación:** igualdad semántica entre clasificación, scopes y reglas generadas para layout CDAD —incluidos `scripts`, `agents`, `skills` y archivos exactos—, convencional, co-ubicado y Odoo.
   - **Activación OpenCode:** desde el proyecto, una sesión con agente local permite una lectura legítima de test y deniega una lectura de implementación. Un control aislado sin agente local demuestra qué configuración produjo el cambio.
   - **Activación Claude Code:** una sesión real invoca el guard instalado y demuestra una operación permitida y otra denegada según una clasificación de proyecto que difiera del mapa global. Ejecutar el script directamente no sustituye esta prueba.
   - **Fronteras:** cada barrera declarada efectiva tiene prueba positiva y negativa por las herramientas que realmente media. Se registran runtime/versión, modo de lanzamiento, raíz del proyecto, hashes de política y derivados, comandos y resultados.

   El spike de OpenCode 2.0.16 solo acredita el caso con `--standalone`. Se debe verificar separadamente el servicio de fondo con timeout explícito de 300 segundos y registrar sesión, resultado o bloqueo. Si vuelve a fallar, el recorrido usa `--standalone` y el servicio de fondo queda declarado no verificado; no se atribuye una causa no aislada.

   Cualquier diferencia entre scopes y restricciones representables se declara antes del despacho. No se atribuyen controles por rol a Codex sin evidencia.

9. **PD-9 — Temporales y acciones externas.**  
   El encargo distingue producto, temporales y acciones externas. `temporary_roots` contiene rutas relativas sin escape ni solapamiento con producto; los temporales de un encargo son un subconjunto explícito. La lista vacía no autoriza temporales. Las acciones externas requieren referencia de autoridad en el encargo, no en la política. Un fallo de capacidad identifica operación, causa conocida y limitación para el coordinador. No se agrega un ejecutor de acciones externas ni filtros de Bash.

10. **PD-10 — Adopción hacia adelante.**  
    No existe `--migrate-execution`. La herramienta nueva no convierte ni reescribe contextos o paquetes v1 y no promete validarlos: su reproducción histórica utiliza la revisión de herramienta conservada en Git. Encontrar un contexto v1 como candidato para trabajo nuevo produce diagnóstico, sin conversión ni sobrescritura.

    Los proyectos legacy conservan su camino vigente durante su feature actual. Adoptan v2 al iniciar una nueva feature, con política y autoridad válidas. En este repo se aplica exclusivamente el corte del plan.

    Cada test con fixture v1 se transforma para verificar su garantía vigente sobre v2 o se retira con una entrada de trazabilidad que identifica test, requisito anterior y razón de retiro. Eliminar una garantía todavía exigida sin reemplazo en verde no es válido.

11. **PD-11 — Exclusión y recuperación.**  
    Un único escritor por proyecto protege resolución de ejecución, reserva de identificadores y publicación. Dos preparaciones concurrentes no sobrescriben contexto, paquetes, derivados ni state: una obtiene resultado y la otra recibe diagnóstico de ocupación o paquete pendiente.

    Se inyectan interrupciones: después de reservar identidad, después de escribir contexto provisional, después de escribir paquete/derivados, antes de publicar state y después de publicarlo. La siguiente invocación recupera una generación coherente o conserva la anterior, sin borrar archivos ajenos. No se imprime un paquete despachable antes de completar su publicación. El alcance no incluye despacho paralelo ni pérdida física del almacenamiento.

12. **PD-12 — Consumidor instalado y legacy/standalone.**  
    Desde una instalación aislada, sin usar el checkout como ruta de ejecución, funcionan propuesta, bootstrap, preparación, registro y reanudación, incluida la generación local OpenCode y las dependencias del guard. La instalación consume staging para agentes y deja de exigir el directorio fuente `agents/`; mantiene las dependencias reales de skills/scripts y no lee `sources/`.

    Un caso representativo de proyecto legacy sin contexto conserva su intake. Architect standalone sigue ese camino. Con spec aprobada, los roles posteriores pueden usar bootstrap sin fabricar un epic. La documentación explica configuración, autoridad, primera preparación, reanudación y reconciliación.

13. **PD-13 — Recorrido real de 004-002.**  
    La evidencia corresponde al desarrollo de `004-002-project-execution-bootstrap` en este repositorio: architect, test-writer, implementer, reviewer y scribe trabajan por paquetes y en sesiones separadas; los lectores entregan texto para materialización.

    El ledger distingue el tramo v1 previo al corte y el tramo v2 posterior. Después del corte se completa trabajo real pendiente de aceptación, revisión y cierre mediante v2, incluyendo test-writer, implementer, reviewer y scribe. No se repite artificialmente el architect ni se atribuyen al tramo histórico capacidades nuevas.

    Se registran contratos, IDs, intentos, runtimes/modelos conocidos, configuración efectiva, comandos/resultados, gates y disposición de fricción. La continuidad de identidad se demuestra dentro de v2; la relación con el tramo v1 queda documentada como sucesión, sin inventar observaciones retrospectivas.

### 3. Invariantes verificables

1. `prepare` continúa siendo el único productor de paquetes; no se reparan manualmente ni se incorpora un productor alternativo.
2. Clasificación, runtime, modelo y detección de layout no conceden autoridad.
3. Ningún rol modifica su política de límites. Los derivados no son fuentes editables; su publicación pertenece al mecanismo de preparación/configuración supervisado.
4. Test-writer no inspecciona implementación; implementer no modifica tests aprobados; los roles lectores no materializan producto.
5. Bash conserva la política permisiva. Los mapas y hooks no se describen como sandbox ni como mediación de los procesos lanzados por Bash.
6. Una sola política editable, snapshots históricos inmutables, un solo paquete activo y un solo epic activo.
7. Preparación, reconciliación y recuperación conservan archivos ajenos y campos de state no afectados. El corte preserva los bytes de los contextos y paquetes v1.
8. `cdad-models.sh` conserva la selección de modelos. Los registros de intento son observaciones y no amplían permisos.
9. Registrar un intento no recibe resultados ni acredita cumplimiento o cierre.

### 4. Criterios de aceptación

1. PD-1–PD-12 tienen tests de comportamiento trazados. Los casos negativos verifican ausencia de publicación o conservación del estado anterior.
2. La matriz incluye layout CDAD, convencional, co-ubicado y Odoo; consumidores v2 nuevo/reanudado, legacy sin contexto y standalone con spec aprobada. No incluye migración v1.
3. OpenCode y Claude Code tienen evidencia de derivación y activación real según PD-8. El servicio de fondo OpenCode tiene resultado documentado; si no funciona, se declara la limitación y se usa el modo verificado.
4. Pasan los cinco puntos de interrupción y el caso concurrente de PD-11.
5. Los validadores vigentes pasan; toda sustitución o retiro de assertions/fixtures v1 tiene trazabilidad y conserva las garantías aplicables.
6. El corte tiene revisión instalada identificada, hashes históricos preservados y primer paquete v2 válido. Ningún paquete pendiente se abandona para efectuarlo.
7. El recorrido PD-13 termina con evidencia de ambos tramos y sin defectos materiales pendientes. Las limitaciones aceptadas quedan explícitas; unknown permanece unknown.
8. La guía mínima es reproducible desde producto instalado. No se exige ahorro porcentual ni un framework adicional de métricas.

---

**Status: Aprobada por Pablo (2026-09-29) con las condiciones C1–C2 del plan.**

## Cambios respecto de draft-001

| Elemento | Cambio | Motivo |
|---|---|---|
| D1–D6 | Se retira la sección de decisiones pendientes y sus alternativas. | Son vinculantes. |
| Política | Se fija contenido de exactamente tres campos y exclusión de escritura para todos los roles. | D1 y O1. |
| PD-8 | Se concreta `.opencode/agents/` local y guard CC que carga política al ejecutarse. | D5 y G1. |
| Activación | Se separan pruebas de derivación, script y runtime real; se incorpora control OpenCode y verificación del servicio de fondo. | El spike solo acredita `--standalone`. |
| PD-10 | Se elimina `--migrate-execution`, conversión v1 y validación histórica por la herramienta nueva. | D2; reduce implementación y matriz de compatibilidad. |
| Contexto nuevo | Se añade ubicación alternativa resuelta por binding cuando la ruta habitual contiene v1. | Crear v2 sin sobrescribir evidencia histórica. |
| Fixtures v1 | Se exige conversión del test a garantías v2 o retiro trazado. | D2 sin mantener soporte operativo v1. |
| G3 | Se conserva el caso legacy representativo; se descarta la recomendación de migración del gate. | Los datos del gate informan el diseño; D2 decide su tratamiento. |
| PD-13 | Se identifica este repo y 004-002, con evidencia anterior/posterior al corte. | D6 y G2. |
| Plan | Se agrega un único corte entre aterrizaje utilizable y aceptación integral. | Evita construir con capacidades todavía inexistentes. |
| Registro | Se concreta entrada del intento y se excluyen recepción, resultados y cierre mediante tests. | D3 y O2. |
| Métricas | Se retira la integración adicional con métricas como tarea propia. | No es necesaria para registrar intentos; evita extenderse hacia 003-002. |
| Acciones externas | Se conserva distinción y autoridad referenciada, sin diseñar un ejecutor. | Alcance observable del epic. |
| Autoridad | Se exige verificar los registros vigentes sin copiar requisitos exclusivos de epic-003. | El código actual separa indebidamente esas verificaciones por política de modelos. |
| Productor e identidad | Se mantienen un solo `prepare` e identidad lógica separada de observaciones. | Aspectos valorados por el gate y exigidos por el epic. |

Se conservan trece postcondiciones para facilitar trazabilidad; se reduce contenido operativo, especialmente migración, compatibilidad histórica e integración de métricas.

## Tensiones

- **D2 frente a continuidad de identidad y PD-13.** La feature tendrá dos ejecuciones lógicas, una histórica v1 y otra nueva v2. La continuidad se exige dentro de cada ejecución; el recorrido de la feature enlaza ambas. Exigir el mismo ID a través del corte equivaldría a la migración descartada.

- **D1/O1 frente a `--reconcile-policy`.** Ningún rol edita la política. El dueño materializa su decisión; `prepare` acepta esa revisión para la ejecución y regenera derivados. La reconciliación no es una autorización para que implementer u orquestador cambien sus propios límites.

- **D5 frente a evidencia disponible.** El agente local OpenCode tiene evidencia acotada con `--standalone`. El guard CC dinámico y el modo de servicio de fondo siguen **VERIFY**. La spec exige verificarlos y declarar sus límites; no los presenta como existentes.

- **Autoridad vigente frente al validador actual.** El registro de epic-004 utiliza `scope`, `expires` y `source`; la rama especial de epic-003 exige otros campos. Debe implementarse resolución de la evidencia vigente sin inventar que esos campos ya existen ni alterar la delegación. Una referencia insuficiente se diagnostica, no se completa por inferencia.
