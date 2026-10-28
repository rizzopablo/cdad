# Plan — 009-001: el instalador preserva la configuración de modelos del usuario a través de las actualizaciones

Ciclo **light** (decisión del dueño, 2026-10-28): un plan corto, una spec compacta, una fase RED, un GREEN
de tres unidades, una review y cierre. Vive en `epic-009-installer-updates` (épica de una sola feature): el
estado de CDAD no admite features huérfanas.

## 1. Promesa al usuario

> Instalo una actualización de CDAD y **mis modelos por agente siguen ahí**, el resto del agente queda
> actualizado, y el despliegue sigue pudiendo verificarse (`--check` verde).

Hoy no se cumple, y no por un `cp`: el archivo con `model:` del usuario queda **en conflicto** y **congelado**
en la versión vieja, y `--check` falla; el remedio operativo (borrar y reinstalar) **borra el modelo**.
Evidencia reproducida en `.cdad/local/009-001/evidence/repro.md`.

## 2. Alcance

**Entra:**
- Las **claves de usuario** del frontmatter de los agentes instalados — hoy sólo `model:` — se preservan a
  través de install/update, en las dos copias vivas: `.config/opencode/agents/` y `.claude/agents/`.
- El archivo sigue **owned**: next run `SYNC`, `--check` PASS, y el resto del contenido sí se actualiza.
- `validate-subagents.sh` distingue **texto instalable** (repo/staging: `model:` prohibido) de **copia
  instalada** (overlay del usuario: permitido y reportado).
- Mensaje de `--check` que hoy imprime la ruta de staging (`MISSING (staged but not installed): <staging>`)
  pasa a imprimir la ruta instalada.

**No entra:**
- Elegir, sugerir o puntuar modelos (INV-3/006-003 intacto: ningún texto instalable fija un modelo).
- Preservar otras personalizaciones libres del usuario (siguen siendo conflicto D4, como hoy).
- `opencode.json` / configuración del runtime fuera de las copias de agentes: el instalador no lo toca y
  debe seguir sin tocarlo.

## 3. Diseño (pensado para mantenimiento)

**Una casa, una lista, tres consumidores.**

- `scripts/agent-overlay.py` — único hogar de la semántica:
  - `USER_OWNED_KEYS = ("model",)` — **dato**, no código: agregar una clave es una entrada acá + un fixture.
  - `extract(installed_bytes)` → valores de las claves de usuario presentes en el frontmatter.
  - `merge(staged_bytes, extracted)` → bytes esperados (staged + overlay reinsertado en el frontmatter).
  - `compare(installed_bytes, staged_bytes)` → `identical | overlay-only | divergent` (con detalle).
  - Falla cerrado: frontmatter ausente, clave duplicada, clave en el cuerpo o valor vacío → `divergent` con
    motivo (nunca se adivina, nunca se descarta en silencio).
- `install.sh` — **consume** el helper, no reimplementa:
  - `stage_one_destination`: `expected = merge(staged, extract(installed))`; si `installed == expected` →
    SYNC; si difiere sólo por overlay → redeploy del **esperado** y sigue owned; si difiere en otra cosa →
    conflicto D4 (sin cambios); log `OVERLAY model: <valor> (preserved)`.
  - `check_installed_staging`: compara contra el **esperado** y reporta `SYNC (model override preserved: …)`;
    el resto de los drift siguen siendo drift.
  - `check_agent_file` (legacy): se pliega al mismo helper; no queda una segunda definición de «qué es
    overlay».
- `scripts/validate-subagents.sh`: Stage 4 verifica el **texto instalable** (`agents/`, `build/staging`,
  copias generadas) y reporta, sin fallar, los overrides de la copia instalada.

**Regla de mantenimiento:** si mañana el usuario también configura `temperature`, `steps` o `tools`, se
agrega la clave a `USER_OWNED_KEYS` y el comportamiento sale solo en install, `--check`, validator y tests.

## 4. Contrato (la spec lo formaliza)

| PC | Promesa observable |
|---|---|
| PC-1 | Instalar sobre una copia con `model:` del usuario **conserva el valor exacto** y no reporta conflicto. |
| PC-2 | El resto del archivo queda **igual al staging nuevo** (una actualización real llega). |
| PC-3 | El archivo **sigue owned**: la segunda corrida es `SYNC` y `--check` PASS. |
| PC-4 | Una modificación **fuera** del overlay sigue siendo conflicto D4: preservada, no-owned, reportada. |
| PC-5 | Ningún texto instalable (repo/staging) declara `model:`; el validador falla si aparece. |
| PC-6 | La copia instalada con overlay se **reporta** (install y `--check`), nunca se acepta en silencio. |
| PC-7 | `--uninstall` no borra un agente con overlay: lo preserva (es dato del usuario). |

## 5. Unidades

| U | Contenido | Aceptación |
|---|---|---|
| U1 | `scripts/agent-overlay.py` + tests de la semántica (extract/merge/compare, fail-closed, clave nueva por dato) | tests verdes; `model` en cuerpo o duplicado → `divergent` con motivo |
| U2 | Wiring de `install.sh` (install, `--check`, legacy) + mensaje de ruta corregido | PC-1..PC-4, PC-6 en root de arena; D4 existente intacto |
| U3 | `validate-subagents.sh` re-scopeado + `docs` (README/`--help` de `USER_OWNED_KEYS`) + aserción de `make validate` | PC-5/PC-7; `make validate` 100 % |

## 6. Decisiones

- **D1.** Las claves de usuario son **sólo frontmatter** y se declaran como dato (`USER_OWNED_KEYS`).
- **D2.** El overlay se **reinserta** en el frontmatter del staging (no se conserva el archivo viejo): así la
  actualización llega.
- **D3.** Ambigüedad = **conflicto D4** (comportamiento actual), nunca pérdida silenciosa.
- **D4.** El validador se re-scopea a texto instalable; la copia instalada no se prohíbe.
- **D5.** `--check` imprime la ruta **instalada** en sus drift (hoy imprime staging).
- **D6.** Sin flag nuevo en el instalador: la preservación es el comportamiento, no una opción.

## 7. Riesgos

| Riesgo | Mitigación |
|---|---|
| Un merge mal hecho rompe el frontmatter y el agente no carga | U1 con parseo estricto + fail-closed; tests con frontmatter malformado |
| El overlay tapa una actualización real | PC-2 lo exige explícitamente; test con staging cambiado |
| Duplicar la semántica en bash y en Python | Un solo helper; el legacy se pliega (drift check AP-13) |
| El validator deja pasar un `model:` en repo | PC-5 con test negativo sobre `agents/` |

## 8. Cierre esperado

`closure.md` con: evidencia de PC-1..PC-7, `make validate`, `./install.sh --check` PASS, y entrada de Memory
Bank. **No publica**: el push sigue reservado al dueño.
