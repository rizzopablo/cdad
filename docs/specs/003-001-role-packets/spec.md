---
feature_id: 003-001-role-packets
feature_name: Paquetes mínimos por rol y subfase
created_at: 2026-09-17
approved_by: Codex (agent-delegated)
approved_at: 2026-09-17
---

# Spec: Paquetes mínimos por rol y subfase

## Descripción funcional

CDAD debe entregar a cada sesión de rol sólo las instrucciones y el contexto
necesarios para su tarea y subfase, conservando identidad de ejecución, contrato
de entrada, restricciones del rol, evidencia esperada y formato de salida.

La composición y validación del paquete serán deterministas y utilizables desde
línea de comandos. Esta feature también define el estado y la medición mínimos
que consumirán las siguientes features del epic, y aplica la excepción temporal
de modelo único de ADR-010 sin relajar permisos, separación de sesiones, gates
ni evidencia.

## Contrato

### 1. Fuentes canónicas de instrucciones

Las instrucciones se organizan como Markdown pequeño:

```text
skills/cdad-cycle/packets/
├── common.md
├── roles/
│   ├── architect.md
│   ├── test-writer.md
│   ├── implementer.md
│   ├── reviewer.md
│   └── scribe.md
└── substages/
    ├── architect-discovery.md
    ├── architect-brainstorm.md
    ├── architect-draft.md
    ├── test-writer-audit.md
    ├── test-writer-post-audit.md
    ├── test-writer-red.md
    ├── test-writer-properties.md
    ├── test-writer-e2e.md
    ├── implementer-green.md
    ├── implementer-refactor.md
    ├── implementer-review-fix.md
    ├── reviewer-review.md
    └── scribe-memory.md
```

Cada paquete combina exactamente `common.md`, una instrucción de rol, un delta
de subfase y los datos de la solicitud. No se mantienen templates completos
duplicados por cada combinación. La suma de common + rol + delta no supera
12.000 bytes UTF-8 por combinación. Es un límite del texto de instrucciones,
no una estimación de tokens ni un límite de contexto del runtime.

Los agentes pueden recibir estas instrucciones directamente. No se exige que
una sesión ejecutora cargue `skills/cdad-cycle/SKILL.md` completo. El
orquestador conserva el ciclo, las transiciones y los gates.

Las restricciones de lectura y edición incluidas en el paquete son obligaciones
de comportamiento. Los permisos nativos existentes siguen siendo la barrera
mecánica cuando el runtime los ofrece; esta feature no afirma aislamiento de
filesystem ni auditoría completa de lecturas en runtimes que no lo demuestren.

### 2. Contexto de ejecución

`EXECUTION.json` tiene esta forma exacta:

```json
{
  "schema_version": 1,
  "execution": {
    "id": "exec-003-001-0001",
    "epic_id": "epic-003-context-efficiency",
    "feature_id": "003-001-role-packets",
    "runtime": "opencode",
    "scope": "opencode-mvp",
    "model_policy": "epic-003-single-model",
    "authority_ref": "docs/epics/epic-003-context-efficiency/execution.md",
    "model": {
      "configured": "provider/model",
      "reported": null
    }
  },
  "path_policy": {
    "implementation_roots": ["src", "lib"],
    "test_roots": ["tests"],
    "colocated_test_roots": ["src", "lib"],
    "documentation_roots": ["docs"],
    "colocated_test_suffixes": [
      "_test.go",
      ".test.js",
      ".test.ts",
      ".test.mjs",
      ".test.cjs",
      ".spec.js",
      ".spec.ts"
    ],
    "colocated_test_prefixes": ["test_"]
  }
}
```

`execution.model.configured` y `reported` son observaciones distintas;
cualquiera puede ser `null`. Ningún comando infiere modelo efectivo.

### 3. Solicitud de paquete

`REQUEST.json` tiene esta forma exacta:

```json
{
  "schema_version": 1,
  "packet_id": "packet-003-001-0001",
  "execution_id": "exec-003-001-0001",
  "feature_id": "003-001-role-packets",
  "role": "test-writer",
  "substage": "red",
  "objective": "Verificar P1 mediante comportamiento observable",
  "contract": {
    "kind": "approved-feature-spec",
    "path": "docs/specs/003-001-role-packets/spec.md",
    "sha256": "<64 lowercase hex>",
    "commit": null
  },
  "inputs": [
    {
      "path": "docs/specs/003-001-role-packets/spec.md",
      "purpose": "contrato aprobado"
    }
  ],
  "read_scope": [
    {"class": "contract", "root": "docs/specs/003-001-role-packets"},
    {"class": "tests", "root": "tests"}
  ],
  "write_scope": [
    {"class": "tests", "root": "tests"}
  ],
  "invariants": [
    "No leer código de implementación",
    "Cada test debe mapear a una postcondición"
  ],
  "expected_output": "Test rojo y evidencia de fallo por assertion",
  "evidence_required": [
    "archivos modificados",
    "comando",
    "salida",
    "commit"
  ]
}
```

`REQUEST.json.execution_id` referencia `EXECUTION.json.execution.id`; no
contiene una segunda copia del contexto. `feature_id` debe coincidir en request,
execution y estado.

Campos obligatorios: todos salvo `contract.commit` y los dos campos de modelo,
que pueden ser `null`; `inputs`, `read_scope` y `write_scope` pueden ser listas
vacías cuando el contrato del rol lo permita.

Roles y parejas válidas:

```text
architect: discovery | brainstorm | draft
test-writer: audit | post-audit | red | properties | e2e
implementer: green | refactor | review-fix
reviewer: review
scribe: memory
```

`contract.kind` admite:

- `approved-epic-plan` para `architect/discovery`, `architect/brainstorm` y
  `architect/draft` antes de existir un spec aprobado;
- `approved-feature-spec` para las subfases posteriores a la aprobación.

Los paths de contrato válidos son exactamente
`docs/epics/<epic_id>/plan.md` para `approved-epic-plan` y
`docs/specs/<feature_id>/spec.md` para `approved-feature-spec`. El kind y el
path deben corresponder. Otros documentos necesarios se declaran como inputs.

El discovery usa el plan aprobado del epic. El paquete lo identifica como
`approved-epic-plan`; no puede presentarlo como feature spec ni afirmar que la
feature ya fue aprobada.

`contract.sha256` es el SHA-256 en minúsculas del contenido exacto.
`contract.commit` es opcional.

### 4. Interfaz pública

La implementación usa Python 3 estándar, sin dependencias de terceros. La
implementación canónica instalable vive en
`skills/cdad-cycle/scripts/cdad_packet.py`; `scripts/cdad_packet.py` es un
wrapper fino para uso y tests desde el repo. La copia instalada resuelve
templates y schemas relativos al directorio de la skill instalada, no al repo
fuente:

```text
python3 scripts/cdad_packet.py render \
  --project-root ROOT \
  --execution-context EXECUTION.json \
  --request REQUEST.json

python3 scripts/cdad_packet.py validate-request \
  --project-root ROOT \
  --execution-context EXECUTION.json \
  --request REQUEST.json

python3 scripts/cdad_packet.py validate-packet \
  --project-root ROOT \
  --execution-context EXECUTION.json \
  --request REQUEST.json \
  --packet PACKET.md

python3 scripts/cdad_packet.py validate-state \
  --project-root ROOT \
  --execution-context EXECUTION.json

python3 scripts/cdad_packet.py validate-metric \
  --project-root ROOT \
  --record METRIC.json

bash scripts/validate-subagents.sh \
  --project-root ROOT \
  --execution-context EXECUTION.json
```

`--project-root` es opcional en todos los comandos y por defecto es el
directorio de trabajo actual. El estado siempre se resuelve como
`ROOT/docs/.cdad-state.json`. Esto permite fixtures completos bajo una raíz
temporal.

`CDAD_INSTALL_ROOT` sigue siendo la raíz explícita y opcional de instalación
para `install.sh --check` y `validate-subagents.sh`. No reemplaza
`--project-root`, `HOME` ni la raíz del proyecto.

Layout público de `CDAD_INSTALL_ROOT`: sustituye el prefijo habitual de
instalación, conservando `.config/opencode/agents`, `.config/opencode/skills`,
`.agents/skills`, `.claude/agents`, `.claude/skills` y `.claude/cdad-scripts`
debajo de esa raíz. Debe ser un directorio absoluto existente. Aplica a
instalación, `--dry-run`, `--check` y validator; una raíz explícita inválida
falla antes de tocar otros destinos. Los directorios extra explícitos conservan
su significado; los fixtures pasan `CDAD_SKILL_EXTRA_DIRS` vacío.

Fixture público reproducible de Tarea 1:

```text
CDAD_INSTALL_ROOT=ROOT_INSTALADO bash install.sh --dry-run --basic
CDAD_INSTALL_ROOT=ROOT_INSTALADO bash install.sh --basic
CDAD_INSTALL_ROOT=ROOT_INSTALADO bash install.sh --check
CDAD_INSTALL_ROOT=ROOT_INSTALADO bash scripts/validate-subagents.sh \
  --project-root ROOT --execution-context EXECUTION.json
```

Antes de implementar la raíz, sólo se ejecuta el primer comando (sin
escrituras): una assertion de destinos fuera de ROOT_INSTALADO demuestra el
RED contractual P6. No se ejecuta una instalación hasta verificar su soporte
y confinamiento. La matriz P4/P5 usa el CLI tras existir, con tests previamente
escritos; disponibilidad y casos bloqueados se informan por separado.

Éxito devuelve `0`. Una violación devuelve código distinto de `0`, diagnóstico
por stderr y ninguna salida parcial por stdout. `render` escribe únicamente el
paquete completo por stdout y valida request, state y excepción antes de emitir.

Python 3 pasa a ser dependencia declarada del renderer/validator. README e
instalador deben hacerla visible y fallar con diagnóstico concreto si no está
disponible; no descargan dependencias.

El instalador expone un entrypoint documentado equivalente a la interfaz
anterior. Desde un proyecto consumidor sin `scripts/cdad_packet.py` del repo,
ese entrypoint debe renderizar y validar los mismos fixtures con los mismos
bytes y códigos de salida. Esta obligación no introduce un framework genérico
de packaging.

La ruta instalada exacta es
`CDAD_INSTALL_ROOT/skills/cdad-cycle/scripts/cdad_packet.py`, donde
`CDAD_INSTALL_ROOT` es la raíz explícita que contiene `agents/` y `skills/`;
no reemplaza ni modifica `HOME`. El script instalado resuelve templates y
schemas relativos a su propia skill y funciona desde cualquier proyecto
consumidor, sin depender del wrapper o layout del repositorio fuente.

Consumir un paquete significa: el orquestador captura los bytes completos de
`render` y los entrega sin cambios como prompt de Task o cuerpo del handoff; el
rol sigue ese paquete y sus inputs declarados sin recargar
`cdad-cycle/SKILL.md`. Esta feature garantiza contenido portable y paridad de
los dos canales. Interceptar automáticamente Task, renderizar dentro del runtime
o probar que un cliente de chat preservó el clipboard pertenece a integración
posterior.

### 5. Formato canónico del paquete

Cada paquete empieza con metadata JSON delimitada, seguida por Markdown:

```text
---cdad-packet-json
{"contract":{"commit":null,"kind":"approved-feature-spec","path":"docs/specs/003-001-role-packets/spec.md","sha256":"..."},"execution_id":"exec-003-001-0001","feature_id":"003-001-role-packets","packet_id":"packet-003-001-0001","packet_version":1,"read_scope":[...],"role":"test-writer","substage":"red","write_scope":[...]}
---end-cdad-packet-json
# CDAD task
...
```

La metadata usa JSON UTF-8 en una sola línea, claves ordenadas
lexicográficamente, separadores `,` y `:` sin espacios, escaping JSON estándar
y terminadores LF. No requiere YAML. Además de los campos del ejemplo,
la metadata incluye `execution` (el objeto completo del contexto, con modelos
configurado/reportado) y `path_policy`, para que el consumidor conozca las
clasificaciones de archivos y el alcance de la excepción.

La metadata incluye además `instruction_sources`, una lista ordenada de tres
objetos `{path, sha256}`:

```json
[
  {"path":"common.md","sha256":"<64 lowercase hex>"},
  {"path":"roles/<role>.md","sha256":"<64 lowercase hex>"},
  {"path":"substages/<role>-<substage>.md","sha256":"<64 lowercase hex>"}
]
```

Cada digest corresponde a los bytes UTF-8 exactos del archivo indicado. El
orden es el orden de composición. Los bytes delimitados del bloque estático son
la concatenación de esas tres fuentes, con un único LF entre fuentes y sin otra
instrucción insertada. `validate-packet` recalcula digests, procedencia y bloque;
una fuente, orden, digest o cuerpo discordante invalida el paquete.

El cuerpo tiene orden canónico:

1. instrucción común;
2. instrucción del rol;
3. delta de subfase;
4. objetivo;
5. referencia del contrato;
6. referencias de inputs;
7. scopes e invariantes;
8. salida y evidencia esperadas.

El bloque de instrucciones estáticas se delimita públicamente con
`<!-- cdad-instructions:start -->` y `<!-- cdad-instructions:end -->`, cada
marcador en su propia línea. Los bytes UTF-8 entre esas dos líneas son la
medida verificable del límite de 12.000 bytes. El objetivo y los demás datos
dinámicos aparecen después del marcador final. La selección de instrucciones
por rol/subfase se verifica mecánicamente y su pertinencia semántica forma
parte del review independiente.

Los inputs son referencias `path` + `purpose`; el renderer no inserta su
contenido arbitrario. Las instrucciones canónicas sí forman parte del cuerpo.

`validate-packet` parsea y valida metadata, exige coincidencia exacta con
request, execution y state, recalcula el hash del contrato, vuelve a renderizar
el paquete y exige igualdad byte a byte. Así detecta alteración de metadata,
instrucciones, scopes, objetivo, referencias o cuerpo.

### 6. Gramática y validación de paths y scopes

Todo path debe ser relativo a `--project-root`, usar `/`, estar normalizado y no
ser vacío, absoluto ni contener segmentos `.` o `..`.

Los scopes admiten sólo objetos `{class, root}`, salvo `repository-read`, cuya
forma exacta es `{"class":"repository-read"}` y no admite `root`.

Clases válidas:

- `contract`
- `docs`
- `tests`
- `colocated-tests`
- `implementation`
- `repository-read`

Además de `root`, un scope puede usar `path` para conceder acceso a un único
archivo. Son excluyentes: `{class, root}` o `{class, path}`. La path policy
admite listas opcionales `implementation_files`, `documentation_files` y
`test_files` (por defecto vacías); cada selector exacto debe figurar en la
lista correspondiente. Ejemplo: `implementation_files: ["install.sh"]` permite
`{"class":"implementation","path":"install.sh"}` sin habilitar el directorio
entero. `documentation_files: ["README.md"]` permite su edición al implementer.
Un selector `path` no admite directorios; `root` no admite archivos. Se aplican
los mismos controles de traversal, symlinks, pertenencia y precedencia de tests.
Los tests exactos nunca pasan a ser editables por el implementer.

Ausencia de permisos se expresa con `[]`; no existe clase `none`.

Los roots son directorios existentes o nuevos dentro del proyecto, no pueden
ser `.` y deben pertenecer a la categoría declarada en `path_policy`. Los aliases
`docs` y `contract` no pueden relabelar paths clasificados como implementación.

Clasificación mecánica:

- `tests`: descendientes de `test_roots`;
- `colocated-tests`: descendientes de `colocated_test_roots` cuyo nombre cumple
  uno de los prefijos o sufijos declarados;
- `implementation`: descendientes de `implementation_roots` que no clasifican
  como `colocated-tests`;
- `contract`: descendientes del directorio del contrato exacto;
- `docs`: descendientes de `documentation_roots`, salvo paths que también
  clasifiquen como implementación;
- `repository-read`: lectura de cualquier path dentro del proyecto.

Restricciones por rol:

- test-writer sólo puede leer `contract`, `docs`, `tests` y
  `colocated-tests`; no puede usar `repository-read` ni `implementation`;
- test-writer sólo puede escribir `tests` y `colocated-tests`;
- implementer puede leer `repository-read`, `contract`, `docs`, `tests`,
  `colocated-tests` e `implementation`, pero no escribir `tests` ni
  `colocated-tests`;
- architect, reviewer y scribe pueden usar `repository-read` para lectura y no
  tienen escritura;
- ningún rol puede declarar una raíz de escritura que cubra el proyecto.

Validación obligatoria:

- rechazar traversal;
- para paths existentes, resolver symlinks y rechazar destino fuera de la raíz
  del proyecto o de scope;
- para paths nuevos, resolver el ancestro existente más cercano y aplicar la
  misma regla;
- rechazar inputs fuera de `read_scope`;
- rechazar roots que solapen una raíz de implementación cuando la clase no sea
  `implementation`, salvo scopes `tests` y `colocated-tests`, que sólo conceden acceso a los
  archivos clasificados como tests. La clasificación de tests tiene precedencia
  sobre implementación; un scope `implementation` nunca concede edición de
  esos archivos, aunque comparta directorio;
- rechazar cualquier scope incompatible con el rol.

El CLI valida declaraciones, no una traza completa de lecturas. El orquestador
debe comprobar los archivos modificados al re-entry con las herramientas del
repositorio/runtime. Esta obligación permanece documentada, pero no se presenta
como capacidad de `cdad_packet.py`. Tampoco se afirma inspección de imports
indirectos no observables.

### 7. Estado mínimo y binding de autoridad

`docs/.cdad-state.json` incorpora:

```json
{
  "execution": {
    "id": "exec-003-001-0001",
    "epic_id": "epic-003-context-efficiency",
    "feature_id": "003-001-role-packets",
    "runtime": "opencode",
    "scope": "opencode-mvp",
    "model_policy": "epic-003-single-model",
    "authority_ref": "docs/epics/epic-003-context-efficiency/execution.md"
  },
  "active_packet": {
    "id": "packet-003-001-0001",
    "role": "test-writer",
    "substage": "red",
    "status": "prepared",
    "packet_version": 1,
    "contract_kind": "approved-feature-spec",
    "contract_sha256": "<64 lowercase hex>"
  },
  "hitl_delegation": {
    "status": "active",
    "epic_id": "epic-003-context-efficiency",
    "source": "docs/epics/epic-003-context-efficiency/execution.md",
    "expires_on": [
      "epic-closed",
      "epic-cancelled",
      "user-revoked"
    ]
  }
}
```

`active_packet` puede ser `null` antes de preparar un paquete. Si está presente,
`validate-state` verifica todos sus campos, enums, versión y hash. `render`
requiere que coincida exactamente con `request.packet_id`, rol, subfase,
contract kind y hash.

Estados válidos de paquete en 001: `prepared`, `dispatched`, `completed` y
`failed`. Esta feature valida el snapshot; no recibe resultados, no ofrece
idempotencia de recepción y no reconstruye sesiones.

La política compartida por `validate-state`, `render` y
`validate-subagents.sh` exige igualdad exacta entre `EXECUTION.json.execution`
y `state.execution` para `id`, `epic_id`, `feature_id`, `runtime`, `scope`,
`model_policy` y `authority_ref`.

Además exige:

- `active_epic == execution.epic_id`;
- `active_feature == execution.feature_id`;
- la feature pertenece a `epic_features` y no está `done` ni `cancelled`;
- `epic_stage` es `features-loop`, `epic-integration` o `epic-closure`;
- `hitl_delegation.status == "active"`;
- `hitl_delegation.epic_id == execution.epic_id`;
- `hitl_delegation.source == execution.authority_ref`;
- el archivo `authority_ref` existe dentro del proyecto;
- `expires_on` contiene los tres eventos definidos y ninguno ocurrió según el
  estado estructurado.

No se parsea la prosa del archivo de autoridad. La autorización mecánica
proviene de los campos estructurados; el archivo es referencia auditable.

Un `epic_stage` `done`, `cancelled` o `null`, delegación `revoked`/`expired`,
epic discordante o cualquier binding discordante invalida la excepción.

Si `model_policy == "epic-003-single-model"`, primero se valida toda la
excepción. Un fallo termina la validación aunque el perfil sea `basic`. Sólo
cuando no se solicita excepción se aplica la compatibilidad histórica de
`basic`.

Pares autorizados:

- `runtime=opencode`, `scope=opencode-mvp`: puede compartir modelo entre todos
  los roles, incluidos reviewer e implementer;
- `runtime=codex`, `scope=codex-construction`: puede compartir modelo entre los
  roles delegados; no afirma qué modelo usa el orquestador padre.

Toda aceptación identifica ejecución, runtime, scope, autoridad y modelos
configurado/reportado disponibles, y declara que la diversidad no se exige ni
se acredita por esa excepción. No infiere igualdad efectiva si el runtime no
la reporta ni afirma independencia estadística.

Los consumidores existentes sin contexto de ejecución preparado conservan su
flujo vigente. No deben solicitar un paquete incompleto ni inventar un mandato.
Con paquete válido, el ejecutor carga exclusivamente sus instrucciones y los
inputs autorizados; no vuelve a cargar el ciclo completo.

### 8. Medición mínima separada

Cada medición es un JSON independiente:

```json
{
  "schema_version": 1,
  "execution_id": "exec-003-001-0001",
  "packet_id": "packet-003-001-0001",
  "epic_id": "epic-003-context-efficiency",
  "feature_id": "003-001-role-packets",
  "role": "test-writer",
  "substage": "red",
  "runtime": "opencode",
  "model": {
    "configured": "provider/model",
    "reported": null
  },
  "started_at": "2026-09-17T00:00:00Z",
  "ended_at": null,
  "input_tokens": null,
  "output_tokens": null,
  "context_limit": null,
  "retry_count": 0,
  "outcome": "dispatched"
}
```

`validate-metric` usa `--project-root` para comparar identidad contra
`docs/.cdad-state.json`: execution, epic, feature, role/substage y, cuando
`active_packet` no es `null`, packet. No recibe execution context separado.

Campos desconocidos permanecen `null`. Tokens, límite y reintentos, cuando no
son `null`, son enteros no negativos. El esquema no convierte bytes en tokens,
no calcula facturación y no afirma captura automática del runtime.

`started_at` y `ended_at` usan RFC 3339 con offset explícito; `ended_at` puede
ser `null` mientras la llamada no terminó y, cuando existe, no precede a
`started_at`. `outcome` pertenece a `prepared`, `dispatched`, `completed` o
`failed`; texto libre como `unknown` es inválido. Un hecho no observado se
representa en su campo nullable, no inventando un outcome.

## Postcondiciones

**P1. Composición mínima y determinista.** Para toda solicitud válida,
`render` devuelve código `0` y un paquete formado por exactamente el bloque
común, el rol solicitado, el delta solicitado y los datos de la solicitud. Dos
ejecuciones con entradas idénticas producen bytes idénticos. No aparecen
instrucciones exclusivas de otro rol o subfase; la instrucción estática
combinada no supera los 12.000 bytes UTF-8 definidos arriba.

**P2. Integridad canónica del paquete.** Una solicitud válida produce metadata
JSON canónica con packet, execution, feature, contrato, rol, subfase y scopes
exactos. `validate-packet` acepta únicamente el resultado byte a byte del
renderer y rechaza alteraciones, hash discordante, pareja inválida, input fuera
de read scope, path inseguro o scope incompatible.

**P3. Restricciones críticas preservadas.** Todo paquete declara las
restricciones mínimas de su rol. Test-writer no recibe scope de implementación
ni repository-read y sólo escribe tests; implementer no escribe tests;
architect, reviewer y scribe son read-only. La política de modelo único no
elimina ni contradice estas restricciones.

**P4. Excepción estrecha y con vencimiento.** La política compartida acepta
igualdad reviewer/implementer sólo cuando execution context, state, epic,
feature, etapa, delegación, autoridad y runtime/scope coinciden. Rechaza IDs
discordantes, autoridad ausente, vencimiento, revocación, cierre, herencia o
scope no autorizado. Una excepción inválida falla antes de considerar `basic`;
`basic` sin excepción conserva su comportamiento previo.

**P5. Estado y métricas honestos.** `validate-state` admite `active_packet=null`
antes de preparar trabajo y, si existe, valida todos sus campos. `render` exige
match exacto con el paquete activo. `validate-metric` compara identidad con el
estado, mantiene separado modelo configurado/reportado, acepta `null` para
hechos desconocidos y rechaza tipos o números inválidos. Ninguna salida equipara
bytes con tokens, deriva facturación o afirma captura automática.

**P6. Portabilidad verificable sin sobreafirmar aislamiento.** Task y chat
nuevo se renderizan desde el mismo contrato funcional. El CLI valida scopes
declarados; la comprobación de archivos modificados queda como gate obligatorio
del orquestador. `--project-root` y `CDAD_INSTALL_ROOT` permiten fixtures
aislados sin cambiar `HOME` ni la instalación real. El entrypoint instalado
funciona desde un proyecto consumidor y produce los mismos bytes y resultados
que el wrapper del repo.

## Invariantes verificables

- Para toda solicitud válida, el SHA-256 declarado equivale al contenido
  exacto del contrato.
- Para cada pareja rol/subfase existe una única composición canónica.
- Ningún modo de modelo cambia scopes, evidencia, aprobación o gates.
- Una ejecución no hereda autoridad por compartir repo, perfil, instalación o
  modelo.
- `null` significa desconocido; nunca equivale a cero.
- Recepción idempotente, detección de bucles y continuidad automática quedan
  fuera de esta feature.

## Criterios de aceptación

- [ ] Tests black-box cubren P1-P6 usando sólo las interfaces públicas.
- [ ] Un fixture de cada pareja rol/subfase renderiza y valida; discovery usa
      `approved-epic-plan` y las subfases posteriores usan el contrato válido
      para su etapa.
- [ ] Los fixtures prueban ausencia de reglas exclusivas de otra subfase.
- [ ] La matriz ADR-010 incluye OpenCode autorizado, Codex construction
      autorizado, epic/runtime/scope/feature/ejecución discordantes, autoridad
      ausente, vencimiento, revocación y `basic` con excepción inválida.
- [ ] Traversal, symlink escape, relabel de implementación, inputs fuera de
      read scope y write scopes amplios/incompatibles son rechazados.
- [ ] Antes de existir la CLI, RED se demuestra sobre consumidores existentes;
      assertions de disponibilidad de interfaz están separadas. `command not
      found`, import failure o ausencia del script no cuentan como RED
      contractual.
- [ ] Tests futuros de CLI pueden estar temporalmente bloqueados mientras la
      interfaz no existe; el gate final exige cero skips/bloqueados.
- [ ] `bash tests/validate-consistency.sh` no introduce regresiones respecto del
      baseline conocido de 123 PASS / 1 FAIL; F011 corresponde a drift de copia
      instalada y se evalúa separadamente.
- [ ] `bash tests/validate-odoo-specialization.sh` pasa.
- [ ] `bash scripts/validate-subagents.sh` y `bash install.sh --check` pasan
      contra raíces de proyecto/instalación aisladas.
- [ ] El ejecutable OpenCode 1.18.31 existe fuera de PATH. La aceptación
      automática completa sobre runtime real permanece diferida para la
      integración de 003/004; no se afirma ausencia del binario.
- [ ] Python 3 stdlib está documentado y su ausencia produce diagnóstico claro.
- [ ] Un smoke test invoca el CLI instalado desde un proyecto fixture que no
      contiene el wrapper del repo y comprueba paridad byte a byte con el CLI
      ejecutado desde el repo.
- [ ] La ausencia de CI permanece como deuda explícita; el gate local está
      permitido por `docs/projectbrief.md`.

## Justificación de tests existentes modificados

Se permite modificar assertions textuales existentes únicamente cuando apuntan
a una frase movida desde `SKILL.md`, agentes o `handoff-prompts.md` hacia la
nueva fuente canónica. El reemplazo debe comprobar el mismo contrato en la
ubicación canónica o que el consumidor referencia esa fuente; no puede eliminar
ni debilitar el requisito.

## Fuera de alcance

- Recepción, persistencia o deduplicación de resultados (`003-002`).
- Detección de bucles, reintentos o recuperación (`003-003`).
- Checkpoints y reconstrucción automática (`003-004`).
- Motor general de workflows o templates arbitrarios.
- Captura automática de tokens/modelo desde runtimes.
- Cambios globales de perfiles o eliminación del guard de diversidad.
- Automatización completa de runtimes distintos del primer camino OpenCode.
- Afirmar aislamiento mecánico o trazas de lectura no observadas.
- Corregir el drift de una instalación real ajena al fixture aislado.

## Contexto técnico

Superficies principales:

- `skills/cdad-cycle/references/handoff-prompts.md`
- `skills/cdad-cycle/references/opencode-delegation.md`
- `skills/cdad-cycle/assets/state-template.json`
- `skills/cdad-cycle/SKILL.md`
- `agents/cdad-orchestrator.md`
- `agents/cdad-{architect,test-writer,implementer,reviewer,scribe}.md`
- `scripts/cdad-models.sh`
- `scripts/validate-subagents.sh`
- `install.sh`
- `tests/validate-consistency.sh`
- `tests/validate-odoo-specialization.sh`
- `docs/adr/ADR-010-modelo-unico-mvp-epic-003.md`
- `docs/epics/epic-003-context-efficiency/execution.md`

No existe CI del repositorio detectada; los runners locales constituyen la
evidencia disponible y la deuda está registrada.

---

Status: Approved by Codex (agent-delegated, pedido explícito del usuario el 2026-09-17) on 2026-09-17
