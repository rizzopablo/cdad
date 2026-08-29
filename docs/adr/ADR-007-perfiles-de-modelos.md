# ADR-007: Perfiles de modelos CDAD (economical | optimus | premium)

- **Status**: Accepted
- **Date**: 2026-08-05
- **Deciders**: el usuario (dueño del proyecto) + el orquestador

## Contexto

El dueño quiere poder correr el ciclo con un perfil económico ahora (costo
bajo, velocidad alta) sin renunciar a que el diseño del framework proponga
modelos selectivos por rol (ADR-001/005: architect/scribe razonador fuerte,
test-writer riguroso, implementer productivo barato, reviewer en familia
distinta al implementer). El repo es la fuente de verdad de diseño (ADR-002:
todo desarrollo vive en `cdad/cdad/` y se propaga con `install.sh`), pero el
deploy necesita elegir el perfil sin tocar el repo: hoy el runtime debe ser
byte-idéntico al repo (instalación por copia, `--check` byte-a-byte), así que
cualquier desviación en la línea `model:` rompería el check.

## Opciones consideradas

### Opción A: Un solo mapa de modelos fijo (status quo)
- Pros: cero cambios; un único mapa en ADR-001/005 + tabla §2 del Contrato de
  roles.
- Contras: el deploy no puede elegir; correr económico exige editar el repo o
  los agentes instalados (drift garantizado, el check lo detecta y falla).

### Opción B: Perfiles en `scripts/cdad-models.sh` + switch vía `install.sh`
- Pros: el repo queda con el diseño (optimus); el deploy elige el perfil en la
  instalación; el check y el validator son profile-aware (saben que la única
  desviación legítima del repo es la línea `model:`); el antebias
  reviewer ≠ implementer se preserva en los 3 perfiles.
- Contras: dos fuentes del mapa (script + ADR-001/005 + tabla §2) — mitigado
  porque optimus espeja exactamente el diseño y el script es la fuente de
  verdad operativa; el check pierde el byte-compare estricto de la línea
  `model:` (la reemplaza por una validación semántica contra el perfil activo).

### Opción C: Reemplazar el mapa fijo por un solo mapa "económico" en el repo
- Pros: costo mínimo de mantenimiento.
- Contras: el diseño perdería la propuesta de modelos selectivos; el repo ya
  no mostraría lo que el dueño aprobó como diseño (ADR-001/005).

## Decisión

Crear `scripts/cdad-models.sh` como fuente única del mapa de perfiles
(`cdad_model <perfil> <rol>`), con tres perfiles:

- **economical** — mínimo costo: todos los roles `deepseek-v4-flash`;
  el reviewer queda en `qwen3.7-plus` (default).
- **optimus** — perfil de diseño, default del repo: architect/scribe
  `deepseek-v4-pro`, test-writer `glm-5.2`, implementer `deepseek-v4-flash`,
  reviewer `qwen3.7-plus`. Espeja la tabla §2 del Contrato de roles y
  ADR-001/005.
- **premium** — top-tier **configurable por env**: cada rol es overrideable vía
  `CDAD_PREMIUM_MODEL_<ROL>` (architect/test-writer/implementer/reviewer/
  scribe) en formato `provider/model` de CUALQUIER provider (p.ej.
  `anthropic/claude-opus-4-5`, `openai/gpt-5.2-codex`); sin env, usa el
  default top-tier de los providers configurados (mofgw): architect/reviewer/
  scribe `qwen3.7-max`, test-writer `glm-5.2`, implementer `deepseek-v4-pro`.
  Requisito para el override: el provider de destino debe estar configurado en
  el runtime (p.ej. añadir anthropic/openai a `opencode.jsonc`).

Premium es multi-provider por diseño: los valores de env NO llevan prefijo
`mofgw` forzado — el override se usa tal cual. Los perfiles economical y
optimus quedan fijos (mofgw, este deploy).

El switch es vía CLI de `install.sh`: `bash install.sh --economical | --optimus
| --premium` (mutuamente excluyentes; default optimus). Al instalar, el perfil
aplicado se persiste en `~/.config/opencode/agents/.cdad-models-profile`
(una línea: el nombre del perfil; el uninstall lo borra). `install.sh` (modos
install, `--check` y `--dry-run`) y `scripts/validate-subagents.sh` son
profile-aware: resuelven el perfil activo como flag/env `CDAD_MODEL_PROFILE` >
marker `.cdad-models-profile` > optimus.

**Nota (stateful, 2026-08-06):** el último perfil instalado persiste vía
`.cdad-models-profile`; un `install.sh` posterior sin flag ni env respeta el
marker en vez de volver a optimus. Para cambiar de perfil usá
`install.sh --<perfil>` (instala Y persiste el nuevo). El default del repo para
installs frescos (sin marker) sigue siendo optimus.

## Razones

1. El repo es la fuente de verdad de diseño (ADR-002): los agentes del repo
   quedan siempre con optimus; la elección de perfil es responsabilidad del
   deploy (opt-in), no del diseño.
2. El antebias no-negociable se preserva y se VALIDA: en los 3 perfiles el
   reviewer corre en un modelo distinto al implementer (defaults: qwen3.7-plus/
   max vs deepseek/glm) y `validate-subagents.sh` aplica el guard de
   desigualdad reviewer≠implementer (comparación de strings exacta) en todos
   los perfiles — cubre envs mal configuradas sin inferir familia de modelo.
   El orquestador sigue sin `model:` (el modelo lo elige el usuario al
   seleccionarlo, ADR-001/005).
3. El check y el validator siguen siendo guards de drift: el byte-compare del
   resto del contenido es estricto; la única desviación legítima del repo es
   la línea `model:` y se valida contra el perfil activo.

## Consecuencias

**Positivas:**
- El deploy elige el perfil sin tocar el repo: `install.sh --economical` baja
  el costo de corrida; `--premium` sube calidad; optimus es el default.
- Premium es top-tier multi-provider configurable: con
  `CDAD_PREMIUM_MODEL_REVIEWER=anthropic/claude-sonnet-4-5 bash install.sh
  --premium` el deploy usa el top-tier de anthropic sin tocar el repo ni el
  mapa de modelos.
- El repo siempre muestra el diseño (optimus); el runtime puede desviarse
  intencionalmente del repo SOLO en la línea `model:` (el check lo sabe).
- El perfil activo queda persistido y verificable (marker + validator).

**Negativas / trade-offs:**
- Riesgo de dos fuentes del mapa (script + ADR-001/005 + tabla §2) → mitigado
  porque optimus espeja exactamente el diseño y el script es la fuente de
  verdad operativa (install/check/validator lo leen, no duplican el mapa).
- El check ya no es byte-compare puro para agentes: ignora `^model:` en la
  comparación y valida esa línea semánticamente contra el perfil activo.
- Un override de env mal configurado (reviewer == implementer) rompe el
  invariante anti-bias → el validator lo detecta y FALLA con mensaje
  descriptivo (guard reviewer≠implementer).
- El override premium exige que el provider de destino esté configurado en el
  runtime (p.ej. anthropic/openai en `opencode.jsonc`); si no, el modelo
  elegido no está disponible y el runtime falla al seleccionarlo.

**Neutrales:**
- Con perfil optimus (default) el resultado de `install.sh --check` y de
  `validate-subagents.sh` es exactamente el actual (los tests de cdad-001
  siguen PASS).
- Los perfiles economical/premium son opt-in del deploy; el diseño propone
  optimus y el deploy lo acepta o lo overridea por perfil.

## Verificación (realizada 2026-08-05)

El ciclo completo de perfiles se verificó en el orden: baseline `--check`
PASS (optimus) → `--economical` (marker = economical) → `--check` PASS →
validator PASS → `--optimus` (restaura diseño) → `--check` PASS → validator
PASS → `--premium` → `--check` PASS → validator PASS → `--optimus` final
(runtime en diseño) → `--check` PASS → validator PASS → tests cdad-001 PASS.
La identidad del bloque §2 (SKILL ↔ orquestador) con la nota de perfiles se
verificó byte-idéntica.

### Verificación del override premium (realizada 2026-08-06)

- `--premium` sin envs → defaults premium instalados (architect/reviewer/scribe
  `qwen3.7-max`, test-writer `glm-5.2`, implementer `deepseek-v4-pro`);
  `--check` PASS; validator PASS.
- Env override: `CDAD_PREMIUM_MODEL_ARCHITECT=anthropic/claude-opus-4-5
  CDAD_PREMIUM_MODEL_REVIEWER=anthropic/claude-sonnet-4-5 bash install.sh
  --premium` → architect y reviewer en anthropic/...; `--check` con las mismas
  envs PASS; validator PASS (guard anti-bias: reviewer≠implementer).
- Guard anti-bias: `CDAD_PREMIUM_MODEL_REVIEWER=mofgw/deepseek-v4-pro
  CDAD_PREMIUM_MODEL_IMPLEMENTER=mofgw/deepseek-v4-pro bash install.sh
  --premium` → el validator FALLA con "reviewer e implementer comparten modelo"
  (después se reinstaló `--premium` sin envs).
- Final: runtime restaurado a optimus (perfil de diseño).

## Enmienda (2026-08-24): ajuste del perfil economical

- **Status**: Accepted (supera la definición economical original de este ADR)
- **Deciders**: el usuario (dueño del proyecto) + el orquestador

### Contexto

1. Reporte del dueño: `qwen3.7-plus` (reviewer economical por default) fallando
   de forma recurrente en corridas recientes (causa raíz no auditada en logs;
   el síntoma motivó el cambio).
2. Propuesta inicial del dueño: mover architect y reviewer economical a
   `deepseek-v4-pro`. **Rechazada para el reviewer**: deepseek-v4-pro y el
   implementer economical (`deepseek-v4-flash`) son la MISMA familia — el guard
   del validator (comparación de strings) la dejaría pasar, pero violaría el
   invariante de diseño "familia DISTINTA" (anti-confirmation-bias).

### Decisión

- **economical|architect → `mofgw/deepseek-v4-pro`**: sin invariante de familia;
   la precisión del spec es la carga crítica del ciclo (spec ambiguo → tests
   ambiguos → AP-13 Garbage Cascade).
- **economical|reviewer → `mofgw/minimax-m3`**: familia distinta al implementer
   (antibias preservado en strings Y en familia); según `opencode.jsonc` cuesta
   0.30/1.20 vs 0.40/1.60 de qwen3.7-plus (−25%) con 1M contexto / 512k output
   (vs 131k de qwen) — mejor para reviews de diffs grandes.
- Roles de ejecución (test-writer, implementer, scribe) sin cambios:
   `deepseek-v4-flash`.
- **optimus y premium quedan sin cambios** (siguen con qwen3.7-plus/max en
   reviewer). Nota: si las fallas de qwen se confirman como del modelo y no de
   provisión puntual, evaluar extender el reemplazo a los otros perfiles.

### Verificación (realizada 2026-08-24)

`install.sh --economical` → `--check` PASS → `validate-subagents.sh` PASS
(guard anti-bias: minimax-m3 ≠ deepseek-v4-flash). Detalle en la corrida de
instalación de esa fecha.

## Enmienda 2026-08-29 — Perfil `basic` (portabilidad entre providers)

### Contexto

Cuando las cuentas del provider principal se agotan, el usuario switchea a un
provider de fallback (p.ej. openrouter). Los perfiles existentes fijan
`model: mofgw/<id>` que no existen en el provider destino → los subagentes
quedan trabados. Se necesita un perfil portable que no dependa de IDs de
modelo específicos.

### Decisión

Perfil **`basic`**: `install.sh --basic` **elimina la línea `model:`** de las
copias instaladas (nunca del repo). Los agentes heredan el modelo por default
del runtime, en cualquier provider.

- `cdad_model` / `cdad_model_claude` devuelven vacío para todos los roles en
  basic (incluidas las variantes `*-odoo`, cuyo modelo fijo por rol queda
  suspendido en este perfil).
- `--check` ya era profile-aware: con basic espera que las copias NO declaren
  `model:`.

### Trade-off (aceptado, documentado)

El invariante anti-bias (reviewer en modelo distinto al implementer) NO es
garantizado por el instalador en basic: todos los roles heredan el mismo
modelo default. El usuario con varios modelos disponibles puede configurar
modelos por agente a mano; con un solo modelo disponible, el sistema de
agentes funciona igual. La protección estructural (sesiones aisladas,
read-only, permisos por rol) no cambia con el perfil.

### Cuándo usar cada perfil

| Perfil   | Cuándo                                                                 |
| -------- | ---------------------------------------------------------------------- |
| basic    | provider único/agotado, switch a fallback, o setup minimalista          |
| economical | ejecución barata con calidad en spec/review (mofgw)                  |
| optimus  | diseño default, balance costo/calidad (mofgw)                          |
| premium  | top-tier multi-provider con overrides por env                          |

### Verificación (realizada 2026-08-29)

`install.sh --basic` en sandbox (HOME aislado) → `model:` stripped en las 11
copias (5 base + 5 odoo + orquestador sin modelo) → `--check` PASS → marker
`.cdad-models-profile = basic`. Runtime real re-verificado con economical.

## Enmienda 2 (2026-08-29) — Fallback de proveedor: qué soporta OpenCode y receta

### Investigación (docs oficiales opencode.ai, 2026-08-29)

- **NO existe fallback de modelo nativo por agente**: ni `opencode.json` ni el
  frontmatter aceptan una cadena de fallback (`fallback: [m1, m2]`). Cada
  agente resuelve UN modelo (frontmatter `model:` o config); si el ID no
  existe en el provider activo → `ProviderModelNotFoundError` → subagente
  trabado (síntoma observado).
- **Lo que sí existe**:
  1. `model` + `small_model` globales (una primaria, una económica — no es
     cadena de fallback).
  2. Override por agente en config: `agent.<nombre>.model` en `opencode.json`
     (documentado para agentes built-in; para agentes custom markdown la
     precedencia config>frontmatter es el patrón documentado — verificar en
     runtime con `opencode run --agent <nombre>` y revisar `modelID` en el
     log si se depende de ello).
  3. Vercel AI Gateway: `provider.vercel.models.<model>.options.order` permite
     fallback real del MISMO model ID entre providers (requiere gateway; no
     aplica a IDs distintos por provider).

### Receta operativa (con el perfil `basic` de la enmienda 1)

1. **Switch de provider = 1 línea**: en `opencode.jsonc`, `"model":
   "<provider>/<model-id>"` del provider activo. Con perfil basic, TODOS los
   agentes CDAD heredan esa primaria — cero ediciones por agente.
2. **Anti-bias opcional en fallback**: si el provider de fallback tiene ≥2
   modelos, agregar en `opencode.jsonc` un override puntual:
   `"agent": { "cdad-reviewer": { "model": "<provider>/<otro-modelo>" } }` →
   reviewer en modelo distinto sin tocar el repo ni el perfil.
3. **Volver al principal**: restaurar `"model"` y `install.sh --economical`
   (o el perfil que corresponda) — el switch es stateful y reversible.

### Alternativa estructural (futura)

La solución definitiva al problema de portabilidad es un gateway que exponga
IDs estables por rol (patrón mofgw, ADR-005) con routing multi-provider y
fallback en el gateway — no en el cliente. OpenCode no lo resuelve a nivel
agente; quedará como ADR separado si se implementa.
