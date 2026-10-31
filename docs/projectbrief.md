# Project Brief

## Propósito del proyecto

CDAD (Contract-Driven AI Development): metodología + framework de agentes para
desarrollar software con IA bajo disciplina de contratos — spec aprobado, TDD
anti-trampa con sesiones aisladas por rol, review two-layer y Memory Bank.
Para equipos (humanos + agentes) que quieren calidad verificable, no teatro.

## Stack técnico

- **Formato**: markdown (skills + agents frontmatter opencode) + bash + Python 3 (stdlib).
- **CLI canónicos del ciclo** (familia `skills/cdad-cycle/scripts/`, con wrapper fino en
  `scripts/`): paquetes/estado (`cdad_packet.py`), recepción/materialización/evidencia
  (`cdad_result.py`), continuidad (`cdad_continuity.py`), guards (`cdad_guard.py`),
  medición de contexto (`cdad_context_meter.py`), versión (`cdad-version-check.py`);
  generador/activación en `scripts/` (`cdad-generate.py`, `cdad-activate.py`).
- **Instalación**: `install.sh` (copia a `~/.config/opencode/` y `~/.agents/`,
  flags `--check/--force/--uninstall`); agentes generados desde `sources/` a staging
  (nunca editados a mano) e instalados solo desde staging.
- **Tooling de tests**: suite **pytest** (Python) por feature (`tests/test_<feature>_t*.py`,
  RED/GREEN por tarea) + validadores **bash** de consistencia (`tests/validate-*.sh`,
  `make validate`); checks por feature en `docs/specs/<id>/VALIDATION.md`.
- **Lint / type check**: para proyectos Odoo gestionados con CDAD:
  `make lint` (pre-commit-vauxoo) + `make test*` (contrato odoo-make-env).
- **CI**: pendiente (deuda registrada; la suite local hace de gate, ver progress).

## Despacho de encargos y frontera con la instalación

- **El paquete es un artefacto publicado, no un mensaje.** Un encargo CDAD se
  prepara con `cdad_packet.py prepare` y queda en `.cdad/packets/<packet_id>/`
  (`REQUEST.json` + `PACKET.md` canónico). El rol lo admite por una de dos rutas
  exclusivas: **ruta A** (paquete inline completo, comparado byte a byte contra el
  render) o **ruta C** (bloque de identificación + lectura del paquete publicado).
- **Ruta C es la vía de despacho sin retranscribir el cuerpo.** `render --route C`
  emite solo la declaración y un bloque JSON con `project_root`, `packet_id`,
  `execution_id`, `execution_context`, `request`, `packet` y `contract`; no reproduce
  instrucciones, objetivo, entradas, scopes ni cuerpo. Exige el request **publicado**
  en su ubicación canónica, contexto v2 canónico y el `PACKET.md` completo verificado
  contra el render antes de emitir. No modifica archivos ni estado. Base: `010-004`
  (`docs/specs/010-004-packet-dispatch-ergonomics/spec.md` §4.2, PC-01/PC-02).
- **El contexto de ejecución se declara, no se infiere.** Toda publicación nueva
  declara `execution_context` con la forma exacta
  `.cdad/executions/<execution_id>/execution.json` en `REQUEST.json` y en la cabecera
  de `PACKET.md`; toda preparación nueva —ordinaria, sucesora o de recuperación que
  publique generación nueva— usa ejecución **v2**, incluso al continuar un proyecto
  viejo. Los requests históricos v1 se reconocen, validan y reemiten por sus vías
  explícitas; ninguno de esos usos habilita preparación nueva v1.
- **El destinatario del encargo se comprueba en dos niveles, en momentos distintos**
  (`010-002` D3, PC-06..PC-08). **Estático** agente↔rol en la validación compartida:
  `cdad-<role>` exacto o prefijo completo `cdad-<role>-` con sufijo no vacío; un agente de
  otro rol no valida ni produce render válido, y el contraste **no** consulta el stack ni
  acredita que la variante esté publicada. **Contextual** rol/stack/agente solo al publicar
  un request nuevo —ordinario o `prepare --replace-packet`— y al registrar un **intento
  nuevo** de despacho con agente declarado. Toda publicación nueva deriva el agente del rol
  y del stack vigente; el reemplazo **rederiva** y deja de copiar el del predecesor (cubre
  predecesor histórico sin agente y stack cambiado, sin reescribir bytes históricos). La
  recepción de un paquete ya despachado, la repetición idempotente de un registro idéntico
  y la finalización válida del write-ahead **no** se reevalúan contra el stack vigente; un
  intento nuevo con agente declarado sí. `execution_context` exige `agent`, y `agent` sigue
  excluido del render.
- **Mecánico y procedimental se atribuyen donde existen.** Una variante requerida y no
  publicada es **deber procedimental** del orquestador en la vía nativa (comprobar
  publicación, detener y reportar, nunca sustituir en silencio); el rechazo mecánico antes
  de lanzar pertenece **solo** al adaptador externo.
- **El esquema del request describe forma, no autoridad.** `packet-request.schema.json`
  declara `agent` y `execution_context`, conserva el conjunto cerrado y exige la
  dependencia `execution_context` → `agent`. No sustituye las comprobaciones del CLI sobre
  coherencia de rol, rutas, archivos, estado, autoridad, hashes ni momento de publicación.
- **Frontera con la instalación (R1).** La unidad `010-004` queda **cerrada en el
  repositorio y NO vigente en la instalación**: el despacho real usa la toolchain del
  repo (`skills/cdad-cycle/scripts/…` y sus envoltorios `scripts/`) hasta que el dueño
  decida publicar. La copia instalada conserva el comportamiento anterior (sin
  `--route`, esquema cerrado que desconoce el campo, preparación v1 implícita sin
  policy). Publicar es decisión del dueño, no del orquestador. Detalle y hashes
  medidos en `docs/specs/010-004-packet-dispatch-ergonomics/closure.md` §7. **Publicada el 2026-10-31** con aprobación del dueño: `install.sh --check` rc=0 y hashes
  repo = instalado; ver `closure.md` §10.

## Producto documental — norma única y frontera de escritura

- **Una sola casa normativa.** Los criterios para encargos cuyo producto es un documento
  (relevamiento, mapa de proceso, historia de usuario) viven en
  `skills/cdad-cycle/references/documentary-contracts.md`, localizable desde la tabla de
  referencias de `skills/cdad-cycle/SKILL.md`. Los consumidores —las seis fuentes de rol,
  los cinco bloques estáticos de `skills/cdad-cycle/packets/roles/` y los agentes
  derivados de ambos runtimes— declaran su obligación en sus propias palabras y nombran
  el archivo; nadie reproduce sus frases normativas. Base: `010-001`, PC-13/PC-14.
- **Cuatro categorías, no un formato.** Evidencia, propuesta, contradicción y pendiente
  son distinciones obligatorias y localizables; no se exigen secciones vacías ni
  instancias ficticias. Toda afirmación factual identifica la fuente que la sostiene y
  dónde examinarla, con un **localizador mínimo por tipo de fuente** (archivo del repo,
  insumo recibido, mensaje o decisión, minuta, fuente mutable).
- **Pendientes clasificados por su efecto sobre el contrato.** Bloquea el pendiente que
  impide verificar una postcondición o un criterio de aceptación, y también el de
  impacto todavía desconocido. El productor no rebaja una obligación a «no bloqueante»
  por decisión unilateral: si hay que renunciar a una promesa, cambia el contrato por el
  procedimiento de aprobación vigente.
- **Frontera producto autorizado / fuentes / verificadores.** Todo encargo documental
  declara fuentes autorizadas, producto editable por rutas, verificadores e insumos de
  aceptación protegidos, evidencia esperada y límites de verificación. Compartir la
  clasificación `docs` **no** vuelve editable un archivo. Rige **«quien produce no
  modifica su oráculo»**, para código y para documento.
- **Dos registros en el cierre.** Control automático/estructural (qué se ejecutó,
  resultado, alcance, límites) y revisión semántica independiente (qué se contrastó,
  hallazgos, abstenciones). La presencia de secciones, etiquetas, archivos o referencias
  resolubles **no** demuestra fidelidad, suficiencia ni verdad semántica; un recibo de
  transporte o la aceptación estructural de un paquete tampoco acreditan revisión
  semántica. La aceptación funcional es del usuario/dueño que aprueba.
- **El perfil documental es una especialización por contrato, no una identidad**
  (`010-002` D1, PC-01..PC-03). Un encargo documental se declara con los campos que ya
  existen: objetivo y promesas en el contrato/`objective`, producto en `expected_output`,
  fuentes en `inputs`/`read_scope`, producto editable en `write_scope`, separación y
  verificadores en `invariants` y alcances, comprobaciones y límites en
  `evidence_required`. **No** hay agente, rol, etapa, subfase, campo del estado ni selector
  documental nuevos, y `stack` sigue significando dominio. El **procedimiento operativo** de
  preparación y aceptación vive en `skills/cdad-cycle/references/handoff-prompts.md`
  (`## Documentary engagement — operating procedure`) y remite a la norma, sin repetirla.
  La producción documental exige alcance editable explícito; los defaults de rol no se
  amplían.
- **Aplicabilidad Odoo por rol y por producto o diff real** (`010-002` D2, PC-04/PC-05).
  Las obligaciones de addon rigen cuando el encargo modifica o verifica el addon; un
  producto exclusivamente documental conserva el conocimiento funcional de dominio y **no**
  exige una batería de addon que no modifica. La frontera de addon —código, vistas,
  controladores, asistentes, seguridad, datos, estáticos, `__manifest__.py` y equivalentes
  funcionales— tiene casa única en `skills/odoo-expert/SKILL.md`; la documentación del
  módulo es producto documental salvo declaración en contrario. La base de decisión es por
  rol: contrato para architect y test-writer, producto aprobado para implementer, y
  **diff real** —que prevalece sobre la etiqueta— para reviewer y orquestador. Un addon
  oculto bajo etiqueta documental se informa y bloquea su aceptación como documental puro.
  La frontera **no** cambia la clasificación de rutas ni los permisos.
- **Un verificador documental no es un test de addon.** No exige `TransactionCase` ni
  `@tagged`; corre por el runner declarado del proyecto y, si ese runner no lo cubre, el
  encargo declara el límite de evidencia sin comandos crudos ni permisos nuevos.
- **Límite de vigencia.** La norma está en el repositorio; la instalación global no la
  distribuye todavía (`install.sh --check` en deriva, `010-001/closure.md` §5). Hasta que
  el dueño decida publicar, la obligación llega **por el paquete** y no por el agente
  instalado, y el despacho real usa la toolchain del repo.

## Stakeholders y roles

- **Aprobador de specs / dueño**: el dueño del repo (humano, HITL).
- **Orquestador de referencia**: `cdad-orchestrator` (agente); en epic-005 la HITL está
  delegada al orquestador OpenCode (`docs/epics/epic-005-real-operation/execution.md`).
- **Runtimes soportados**: OpenCode (nativo, ADR-008 para Claude Code), Zed.

## Restricciones conocidas

- Español rioplatense (vos) en toda la documentación.
- En OpenCode: TODOS los roles cdad son task-ables y se delegan vía `task`
  (palanca `write: ask`, cdad-010/ADR-009; el canal `delegate` está muerto en
  deploys con default global sin crédito). En otros runtimes, Agent/handoff
  manual.
- Los modelos por rol viven en el frontmatter de `agents/*.md` (perfiles
  optimus/economical/premium via install.sh).
- La admisión del rol es **documental**: las guardas verifican tokens estables y su
  supervivencia en los derivados, no la conducta de un modelo ni los bytes que recibió
  una sesión nativa. Toda afirmación de cumplimiento se lee con ese límite (R3).

## Scope general

Cubre: ciclo de 5 etapas, roles especializados (+variantes Odoo), epic
coordinado, bootstrap de Memory Bank, ejecución por proyecto v2 (política
única + agentes derivados + guard), continuidad, medición de contexto,
orientación acotada del orquestador, despacho de encargos por paquete
publicado (rutas A y C), los contratos documentales compartidos (categorías,
localizadores, pendientes y frontera producto/fuentes/verificadores) y la
especialización documental por contrato (procedimiento operativo, aplicabilidad Odoo
por rol y diff, coherencia del destinatario y esquema del request). Fuera de scope: runtimes específicos de
CI, adaptadores privados de entornos Odoo (viven en repos privados),
conectores o interceptores nativos de transporte, y certificación automática
de fidelidad semántica.

## Recursos externos

- Repo: https://github.com/rizzopablo/cdad
- Referencia de skills externos: obra/superpowers (comparación documentada en
  el epic superpowers-gaps)

---

Última actualización: 2026-10-31
