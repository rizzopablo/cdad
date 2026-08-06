# ADR-007: Perfiles de modelos CDAD (economical | optimus | premium)

- **Status**: Accepted
- **Date**: 2026-08-05
- **Deciders**: Pablo (dueño del proyecto) + Ofap

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
(una línea: el nombre del perfil; el uninstall lo borra). `install.sh --check`
y `scripts/validate-subagents.sh` son profile-aware: resuelven el perfil activo
como flag/env `CDAD_MODEL_PROFILE` > marker `.cdad-models-profile` > optimus.

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
