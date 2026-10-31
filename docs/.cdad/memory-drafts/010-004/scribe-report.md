# Reporte del scribe — 010-004 (Stage 5, Memory Bank) — PENDIENTE DE APROBACIÓN

Procedencia (declarada, no inferida):

| Campo | Valor |
|---|---|
| Rol | scribe |
| Runtime / agente | opencode / `cdad-scribe` |
| Sesión | `<session>` |
| Sesión padre (despacho) | `<session>` |
| Modelo reportado por el runtime | `opencode-go/deepseek-v4.1-flash` (variante low) |
| Paquete | `010-004-packet-dispatch-ergonomics-scribe-memory-001` |
| Ejecución | `exec-010-004-packet-dispatch-ergonomics-001` |
| Intento de continuidad | 36 (`begin` → `verify-begin` → despacho → `record` → `receive` → `checkpoint-receipt`) |
| Intento de despacho (ledger) | `010-004-scribe-memory-attempt36` |
| Recibo durable | `.cdad/runtime/results/exec-010-004-packet-dispatch-ergonomics-001/010-004-packet-dispatch-ergonomics-scribe-memory-001/receipt.json` |
| sha256 del recibo | `b839fbebbdd49a44cc37f8b8a12d1075f270cd417850a5dab04e5d60d8c96cb9` |
| Transición registrada | `delivery` / `t6-scribe-memory-received` key `7d9ab90703113ddf16bc9dd485a78a202b13a8051e03ed879861d2dfdb1812b7` |
| FINAL TEXT — bytes | **25481** |
| FINAL TEXT — sha256 | **`d6c1ccd977477cd614a0074e529dd3992f9dd9af4fda6ac7206daf7da7b516a7`** |
| `semantic_status` del recibo | `pending` — recibir no aprueba ningún gate |

Borradores extraídos de este FINAL TEXT (materializados como borrador, **no aplicados**):

| Archivo | bytes | sha256 |
|---|---|---|
| `projectbrief.draft.md` | 5597 | `888c196a9c484dbb1d5c95f96be9c1112c5fb8fefc4a916ca8839d45ea7b3989` |
| `activeContext.draft.md` | 8725 | `80d5ada492c0141daa53801e8770c35580bfdeee89c0210a8b6b6c22424a9f01` |
| `systemPatterns.draft.md` | 6759 | `4b3af75464cc3ffacda12ca70121473b52aa93108397dd592f6ee9da2c80692b` |

Ranura ADR (tercera decisión del rol): **ningún ADR propuesto**, con motivo declarado
dentro del FINAL TEXT (`# Draft 3 (ADR) — No ADR suggested`): la decisión ya está
fijada por el contrato aprobado (pin `fc6b2ccc…5d64`) y queda como convención en
`systemPatterns.md`.

Estado de aplicación: los tres borradores **no** se aplicaron a `docs/projectbrief.md`,
`docs/activeContext.md` ni `docs/systemPatterns.md`. Requieren aprobación del dueño;
el orquestador ejecuta el git de la materialización. Este archivo y los `.draft.md`
son evidencia de borrador, no fuente de verdad.

Límite de fidelidad: este reporte acredita la entrega y su identidad; el cuerpo
bajo el marcador es byte-idéntico al FINAL TEXT recibido (sha `d6c1ccd977477cd614a0074e529dd3992f9dd9af4fda6ac7206daf7da7b516a7`), y esa
identidad se verifica separando el cuerpo, no leyendo el archivo completo.

<!-- FINAL-TEXT-BEGIN -->
Validation complete. Both files reconcile with the canonical render, so I'm proceeding under the validated packet.

## Validación de admisión (evidencia)

```
$ R=<repo>
$ P=.cdad/packets/010-004-packet-dispatch-ergonomics-scribe-memory-001
$ python3 skills/cdad-cycle/scripts/cdad_packet.py validate-request --project-root $R --request $P/REQUEST.json   → exit=0
$ python3 skills/cdad-cycle/scripts/cdad_packet.py validate-packet  --project-root $R --request $P/REQUEST.json --packet $P/PACKET.md → exit=0
$ python3 skills/cdad-cycle/scripts/cdad_packet.py render --project-root $R --request $P/REQUEST.json > /tmp/opencode/render-full.md
$ cmp /tmp/opencode/render-full.md $P/PACKET.md → IDENTICAL
  sha256 render = sha256 PACKET.md = 855a40c3865be8aa06cccf2615ac3d08d6391f1bad30f95e55b223423d8ae222
$ render --route C  == bloque de identificación recibido (mismos 8 campos, mismos valores)
$ sha256sum docs/specs/010-004-packet-dispatch-ergonomics/spec.md → fc6b2ccc5cfda3215f83e4610b17b042064ebfda72f0d5377b0a6f0dca515d64 (pin OK)
$ validate-state → VALID: execution=exec-010-004-…-001 feature=010-004-… model_policy=ordinary
```
Sin discrepancias. Roll: **scribe**, write_scope `[]`, read_scope `repository-read`, invariantes `[]`. Drafts only; nothing written, committed or approved.

---

# BORRADOR 1 — `docs/projectbrief.md` (FINAL TEXT, reemplaza el archivo completo)

```markdown
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
- **Frontera con la instalación (R1).** La unidad `010-004` queda **cerrada en el
  repositorio y NO vigente en la instalación**: el despacho real usa la toolchain del
  repo (`skills/cdad-cycle/scripts/…` y sus envoltorios `scripts/`) hasta que el dueño
  decida publicar. La copia instalada conserva el comportamiento anterior (sin
  `--route`, esquema cerrado que desconoce el campo, preparación v1 implícita sin
  policy). Publicar es decisión del dueño, no del orquestador. Detalle y hashes
  medidos en `docs/specs/010-004-packet-dispatch-ergonomics/closure.md` §7.

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
orientación acotada del orquestador y despacho de encargos por paquete
publicado (rutas A y C). Fuera de scope: runtimes específicos de
CI, adaptadores privados de entornos Odoo (viven en repos privados),
conectores o interceptores nativos de transporte, y certificación automática
de fidelidad semántica.

## Recursos externos

- Repo: https://github.com/rizzopablo/cdad
- Referencia de skills externos: obra/superpowers (comparación documentada en
  el epic superpowers-gaps)

---

Última actualización: 2026-10-31
```

---

# BORRADOR 2 — `docs/activeContext.md` (FINAL TEXT, entrada a insertar al inicio del cuerpo, después del encabezado y la línea `---`)

```markdown
## 2026-10-31 — Feature: 010-004-packet-dispatch-ergonomics (epic 010, unidad 2/5)

**Cierre técnico declarado; NO aprobado.** `closure.md` declara el cierre de la
unidad con su evidencia de suite completa; la aprobación del cierre y del Memory
Bank es del dueño y publicar es una decisión separada. Contrato:
`docs/specs/010-004-packet-dispatch-ergonomics/spec.md`, pin
`fc6b2ccc…5d64`, aprobado por Pablo el 2026-10-30.

**Qué se cerró.** El encargo dejó de depender de retranscribir su cuerpo y el rol
dejó de inferir su contexto de ejecución: `render --route C` emite solo una
identificación (declaración + bloque JSON de 8 campos) que no reproduce
instrucciones, objetivo, entradas, scopes ni cuerpo, y exige request publicado,
contexto v2 canónico y `PACKET.md` completo verificado antes de emitir; toda
preparación nueva usa v2 y declara el localizador
`.cdad/executions/<execution_id>/execution.json` en request y cabecera; la vía
implícita v1 sin policy quedó cerrada. El intake de rol ahora declara que el
cierre JSON no termina el paquete, que la comparación va del marcador al final, y
rechaza la mezcla A+C. Doce postcondiciones (PC-01..PC-12), cuatro promesas de
problema y la de distribución.

**Decisiones relevantes.**

- **C emitida por el renderer común, no un conector nuevo.** Reutiliza la ruta C
  existente y evita inventar capacidades del runtime; se acepta explícitamente que
  C evita retranscribir pero **no prueba recepción** (spec §2.1, §4.7).
- **C es v2-only y ligada al request publicado.** El contexto v1 recibe diagnóstico
  explícito; una copia byte-idéntica fuera de `.cdad/packets/<packet_id>/` no puede
  emitir identificación. Trade-off: se conserva la diferencia de preámbulo entre
  `validate-packet` (archivo completo, sin prefacio) y las otras dos superficies, en
  vez de unificar comparadores (§4.4).
- **Localizador restringido y compartido, no rutas arbitrarias.** El campo es
  opcional en el esquema (admite histórico) pero obligatorio en toda publicación
  nueva; la matriz de §4.1 rige igual para `render`, `validate-request` y
  `validate-packet`, con rechazo del histórico sin argumento explícito y sin
  fallback por identidad. Trade-off: desde otro directorio hay que declarar la raíz
  y pasar argumentos válidos allí; una raíz explícita no reinterpreta los argumentos.
- **Laguna v1 activo no terminal: diagnóstico y escalación al dueño.** No hay ruta
  CLI terminal existente (incluido `prepared`); se declara la laguna en vez de
  prometer un procedimiento o inventar migración/withdraw v1 (§4.1, §4.5, PC-07b,
  N-2).
- **Precedencia de diagnósticos de configuración** (decisión del dueño,
  `decision-diagnostic-precedence.md`): cuando coexisten policy/autoridad/aprobación
  inválida y contexto v1, se emite primero la causa accionable de configuración; el
  rechazo por contexto v1 se conserva íntegro (rc≠0, sin efectos, sin conversión).
  No crea jerarquía general ni reabre la spec; N-4/N-5/N-6 siguen postergados.

**Evidencia.** Review independiente inicial: 4 bloqueantes (B1 intake A+C/v2, B2
paquete v1 activo con "complete or fail", B3 PC-10/11 sin procedimiento, B4 sin test
del localizador del sucesor), 3 requeridos no bloqueantes (R1/R2/R3) y 4 opcionales;
reverificación T6 (attempt 34) los declara **B1–B4 CERRADOS**, sin bloqueantes
nuevos; R-A y R-B resueltos en `review-fix-rar-b.md` (attempt 35, commits
`28991b4a` —comentario de `prepare()`, 8 líneas— y `6869301f` —una línea en
`project-start.md`—). Tests del feature: 7 archivos, **22 tests**; focales
**30 passed in 43.62s** (selección de 6 archivos + `test_cdad_generate.py`; excluye
a propósito `t5_properties`, 2 tests verdes en su propio gate). Gate de cierre
(quien cierra corre la suite, un solo intento completado): `--all` 1876 nodeids,
commit `daace667`, **rc=0**, `1871 passed, 5 skipped in 3668.03s`, `dirty 1`,
`canary_delta_lines=0`; los 5 skips son integraciones preexistentes por variables
de entorno, ninguna cubre una PC de esta unidad. Un intento previo quedó
interrumpido por el límite de tiempo de la herramienta (63 % de la selección, sin
`rc`): no se usa como medición de aceptación. Todo recibo de la unidad quedó
`semantic_status: pending`: recibir no aprobó ningún gate. Fuentes:
`docs/specs/010-004-packet-dispatch-ergonomics/{closure.md,review.md,review-verification.md,review-fix-rar-b.md}`.

**Deuda técnica detectada.**

- **D-1 / publicación (R1):** «La unidad queda cerrada en el repositorio, NO vigente
  en la instalación». La copia instalada conserva el comportamiento anterior y
  rechaza estos paquetes por esquema cerrado; hashes medidos tras el fix R-A: repo
  `d62278a1…` vs. instalación `171fcd14…` en `~/.config/opencode`, `~/.agents` y
  `~/.claude`. Publicar es decisión del dueño; ninguna afirmación de vigencia en el
  CLI instalado puede sostener un cierre o un despacho.
- **R-A endurecimiento diferido:** `--replace-packet` y `--resume-packet` no pasan
  por `_reject_active_v1_packet`; con un paquete v1 activo rechazan con el
  diagnóstico de contexto inexistente en vez de nombrar el bloqueo y escalar. Es
  seguro (rc=2, sin efectos) pero no accionable; requiere unidad propia con su test
  (backlog de la épica).
- **I-8:** el test-writer no puede leer sus propios `instruction_sources` (`skills`
  es `implementation_root` y el `read_scope` del rol no lo incluye); el rol se
  detiene y reporta —correcto— pero la instrucción sigue inaccesible. Fuera de
  alcance; tres salidas registradas, sin unidad asignada.
- **R2 (clase I-6 abierta):** la fila 3 de la matriz no distingue un request
  histórico de uno nuevo sin localizador; un paquete nuevo publicado por la copia
  instalada pasa con `--execution-context` y C puede emitir identificación con
  `execution_context` aunque el request no lo declare. El caso quedó corregido;
  cerrar la clase exige un gate del orquestador con su propio contrato.
- **`deferred-hardening` de la spec §10 (ocho ítems, ninguno aplaza una promesa
  comprometida):** exportación independiente del mensaje recibido por cada runtime
  (capacidad pendiente de verificar); conexión mecánica renderer→herramienta nativa
  (requiere superficie demostrada); atomicidad entre validación y
  lectura/transmisión posterior (ventana conservada); unificación del tratamiento de
  preámbulos (diferencia de §4.4 conservada a propósito); endurecimiento exhaustivo
  de diagnósticos ajenos al cambio; nuevas restricciones generales sobre enlaces
  internos o rutas explícitas históricas (controles existentes conservados);
  interoperabilidad entre versiones instaladas distintas (PC-12 compromete el
  consumidor actualizado aislado, no un protocolo de negociación); rendimiento y
  variantes equivalentes adicionales (sin promesa ni necesidad evidenciada).
- **Límites declarados que no se convierten en garantías:** R3 — las guardas
  documentales comprueban tokens estables y su supervivencia en los derivados, no
  acreditan obediencia de un modelo (la mutación por inversión semántica de B1 siguió
  en verde); **F011 medido y no oculto** — `make validate` sigue en 182 PASS / 1 FAIL
  (`rc=2`), FAIL único en F011, drift preexistente y ambiental: la condición de
  cierre es «declarado», no PASS; **fidelidad del recibo del attempt 32** — el recibo
  (`5c5293e8…`, 2.811 B) acredita la entrega y la identidad del intento, **no el
  informe íntegro**, restituido aparte en `review-fix-t6-report.md` con procedencia
  declarada.
- **Desviaciones de proceso registradas (no ocultas):** el AUDIT submidió el universo
  de fixtures (2 expectativas nombradas vs. 105 archivos y 64 fallos en 15 archivos,
  `fixture-impact-inventory.md` §0); un encargo del POST-AUDIT correctivo acotó los
  cambios a una sola celda y dejó tres oráculos residuales (defecto del orquestador
  que redactó el encargo, corregido en `scope-correction-residual-oracles.md`); dos
  `record` sin sesión acreditada, sin inventar datos de procedencia.
- **Archivo no rastreado ajeno:** `docs/specs/010-000-continuity-relative-root/discovery.md`
  sigue `untracked`; es preexistente y ajeno a esta unidad, no se borró ni se movió.

**Next feature in queue.** `010-001-documentary-contracts` (epic 010, orden 2;
`depends_on: 010-004`, ya satisfecha por esta unidad). Al cerrarse el Memory Bank y
aprobarse el cierre, `010-004` pasa a `done` y `010-001` queda desbloqueada: su
Discovery debe abrirse desde el estado coherente de la épica. Publicar la
instalación **no** es requisito de arranque, pero mientras no se publique, todo
despacho real sigue necesitando la toolchain del repo (R1).
```

---

# BORRADOR 3 — `docs/systemPatterns.md` (FINAL TEXT, sección nueva a insertar inmediatamente después de la sección «Cotas de reloj de pared…» y antes de `## Palanca write: ask`; es decir, al final del bloque de patrones de epic 008)

```markdown
### Despacho por ruta C y contexto de ejecución declarado (epic 010, 2026-10-31)

- **El contexto de ejecución se declara, no se infiere.** Toda publicación nueva de un
  encargo incorpora `execution_context` en `REQUEST.json` **y** en la cabecera de
  `PACKET.md`, con la forma exacta `.cdad/executions/<execution_id>/execution.json`,
  donde `<execution_id>` coincide con el del request y cumple el dominio de nombre
  plano ya usado por `_load_execution_context`. Se rechazan localizadores absolutos,
  vacíos, con escapes, con componentes alternativos o en otra ubicación, incluida una
  copia byte-idéntica: la ubicación canónica es parte del contrato, no una convención.
  El campo es opcional en el esquema para conservar la admisión de requests
  históricos, pero omitirlo **no** habilita a nadie a publicar un encargo nuevo v1.
  `.cdad/execution.json` no pertenece al dominio del campo: su uso explícito queda
  solo en la vía histórica. Base: `010-004` §4.1, PC-04..PC-07, INV-12.
- **Toda preparación nueva usa v2; la selección implícita v1 sin policy quedó
  cerrada.** La regla cubre preparación ordinaria, sucesores de reemplazo y
  recuperaciones que publiquen generación nueva, aunque el trabajo venga de un
  proyecto viejo o conservase el objetivo de un encargo anterior; un sucesor nuevo
  declara el campo aunque su predecesor histórico no lo tuviera, y no se añade
  retrospectivamente al predecesor. El delta medido: `_select_execution` devolvía v1
  sin policy y `prepare` consumía esa selección; ahora se rechaza la v1 explícita y la
  implícita antes de publicar. Reconocer, validar o reemitir lo histórico **no**
  autoriza adopción hacia adelante. Base: `010-004` §4.1, PC-04, PC-07b.
- **Ruta C es el vehículo de despacho que no retranscribe el cuerpo.** `render
  --project-root <raíz> --request <REQUEST.json> --route C` emite una línea literal
  `Route C — explicit file backup` y un único bloque JSON con `project_root`,
  `packet_id`, `execution_id`, `execution_context`, `request`, `packet` y `contract`
  (con todos sus campos y su digest); no reproduce instrucciones, objetivo, entradas,
  scopes, invariantes ni cuerpo, no usa el marcador de cabecera de A y no modifica
  archivos ni estado. Antes de emitir exige: request designando el archivo **publicado**
  en `.cdad/packets/<packet_id>/REQUEST.json` dentro de la raíz; contexto **v2**
  canónico (un v1 recibe diagnóstico explícito, sin intentar buscar uno v2 ni
  convertirlo); request validado contra ese contexto; y `PACKET.md` publicado completo
  verificado con `verify_published_packet`. El receptor resuelve las referencias
  project-relative contra `project_root`; para iguales archivos, raíz y configuración
  la salida es determinista. Base: `010-004` §4.2, PC-01/PC-02.
- **El intake del rol es exclusivo y completo, y esa exclusividad está escrita en la
  fuente y en los derivados.** Se cuentan primero los marcadores A: exactamente una
  apertura y su cierre son necesarios, y **el cierre JSON termina la cabecera, no el
  paquete**; la comparación comprende del marcador inicial al final del paquete
  recibido, incluido todo el cuerpo, sin reconstruir ni normalizar. Un dispatch con
  identificación C **y** paquete inline A se rechaza por mezcla aunque el inline
  coincida; C no requiere cuerpo inline, no busca otro paquete si el nombrado falla y
  exige contexto v2; un cuerpo parcial no sustituye la identificación; marcadores
  duplicados no se resuelven eligiendo uno; y un prompt que afirma ser paquete sin
  satisfacer su admisión se rechaza sin pasar a legacy. Las lecturas de control-plane
  no amplían el scope de producto. Base: `010-004` §4.3, PC-03/PC-08b.
- **Paquete v1 activo no terminal: diagnóstico que nombra el bloqueo y escala, sin
  ruta CLI terminal.** Con un paquete v1 activo, incluido `prepared`, el resultado
  observable único es diagnosticar el bloqueo **y** la ausencia de una ruta CLI
  terminal existente, y escalar al dueño, dejando state intacto y sin preparar v1;
  no se indica «completar o fallar» como procedimiento disponible y no se añade
  migración ni withdraw v1. `--resume-packet` conserva su función de reemisión
  byte-identical bajo sus condiciones v2 actuales y no se presenta como vía universal
  de replay v1. Límite declarado y aceptado: es una **laguna** de la spec, no un
  procedimiento inexistente disfrazado. Base: `010-004` §4.1/§4.5, PC-07b, N-2.
- **Precedencia de diagnósticos de configuración sobre el rechazo de contexto.** Cuando
  una preparación nueva encuentra a la vez (a) policy ausente, mal formada o existente
  pero no-archivo, o autoridad/aprobación/pin inválidos y (b) un contexto v1 explícito
  o implícito, **primero se emite (a)**. El rechazo de (b) se conserva completo: la
  operación falla igual, sin efectos persistentes, sin publicar, sin binding v2, sin
  copiar/convertir/reubicar el contexto y sin fallback legacy. La precedencia no se
  aplica a la inversa ni crea una jerarquía general de diagnósticos: solo impide que
  la causa accionable quede inalcanzable detrás del rechazo de versión/ubicación. No
  reabre la spec ni edita el plan; N-4/N-5/N-6 siguen postergados. Normativo en
  `docs/specs/010-004-packet-dispatch-ergonomics/decision-diagnostic-precedence.md`.
- **Integridad, observabilidad y fidelidad son tres hechos distintos.** Un request
  validado igual al render acredita integridad publicada, no el mensaje recibido por el
  runtime; bytes escritos a stdin acreditan entrega a esa frontera, no recepción;
  contrastar el resultado con contrato y fuentes acredita fidelidad examinada, con
  límites; un recibo acredita recepción según su contrato, no aprobación semántica. La
  falta de observabilidad de entrega, por sí sola, no demuestra corrupción ni obliga a
  repetir el trabajo; sí se mantiene el rechazo ante divergencia comprobada o
  autoridad inválida. Base: `010-004` §2.2/§2.3/§4.7, PC-10/PC-11.
- **Lo que esta convención NO promete.** No intercepta prompts nativos ni herramientas:
  es admisión documental. Las guardas de intake comprueban tokens estables y su
  supervivencia en los derivados, no conducta de un modelo (R3: la inversión semántica
  de la regla A+C siguió en verde). No hay exportación independiente del mensaje
  recibido ni conexión mecánica renderer→herramienta: C evita retranscribir, no prueba
  recepción. La unidad está cerrada en el repositorio y **no vigente en la instalación**
  (R1): el despacho real usa la toolchain del repo y publicar es decisión del dueño.
  Normativo en `docs/specs/010-004-packet-dispatch-ergonomics/spec.md` (PC-01..PC-12);
  este archivo no re-enuncia las postcondiciones.
```

---

# Draft 3 (ADR) — **No ADR suggested**

No propongo ADR en esta unidad. La decisión arquitectónica que la unidad materializa (ruta C como vehículo de despacho, contexto de ejecución declarado y v2-only para publicación nueva) ya está fijada por el **contrato aprobado** con pin `fc6b2ccc…5d64` y queda registrada como convención en `systemPatterns.md`; proponer un ADR agregaría una fuente normativa paralela al contrato y excede los tres borradores que este paquete declara. Si el dueño quiere además una fila en «Decisiones vigentes», es una decisión suya y requiere su propia unidad/encargo, no este borrador. (Precedente relevante ya vigente: ADR-038 y ADR-036 cubren admisión por bytes y verificador canónico; esta unidad no las modifica.)

---

# Observaciones para el orquestador (no silenciadas)

1. **El paquete reemplazó el trío por defecto del rol.** Los tres borradores declarados son `projectbrief` / `activeContext` / `systemPatterns`; no se pidió `progress.md`. Verifiqué que `docs/progress.md` **no tiene fila para `010-004`** (ni para 010-001..003): `grep -n "010-00" docs/progress.md` devuelve solo `010-000` (líneas 14 y 22), y `.cdad-state.json` mantiene la unidad en `in-progress`. La transición «in-progress → done» queda **sin borrador** por no estar en el objetivo del paquete: si el dueño la quiere, hace falta el texto y su encargo, o aprobar que el orquestador la materialice como parte de la materialización, no como producto de este rol.
2. **Cifras citadas y su origen**: todas provienen de `closure.md` §2/§4/§8, `review.md`, `review-verification.md` o `spec.md`; no medí ninguna por mi cuenta y no re-derivé hashes. Las cifras de suite (`1871 passed / 5 skipped / rc=0 / 3668.03s`) son del intento `attempt-20261031T035714924428Z-3385202-2939fdeb` sobre `daace667`, tal como la closure las declara.
3. **`deferred-hardening` conservado (R6)**: los ocho ítems de `spec.md` §10 están en el borrador de `activeContext` con su disposición («postergado, ninguno aplaza una promesa comprometida»), más las cuatro deudas que el objetivo nombra. No hay deuda omitida.
4. **Nada materializado**: no escribí archivos, no commiteé, no instalé, no publiqué. `git status --short` sigue mostrando solo el `untracked` preexistente `docs/specs/010-000-continuity-relative-root/discovery.md`.

**Estado:** tres borradores en FINAL TEXT, listos para aprobación del dueño y materialización por el orquestador (ADR-003/ADR-011:101). No aprobados, no aplicados.