# Versión operativa adoptada de CDAD (dogfooding)

Registro de la versión de CDAD que usan los agentes mientras se desarrolla CDAD en
este mismo proyecto. Mantenido por el orquestador.

## Versión vigente

| Campo | Valor |
|---|---|
| Commit | `29a4805` (005-012, 005-013, 005-014 y el saneamiento de contenido), desplegado el 2026-10-14 |
| Fecha de adopción | 2026-10-14 |
| Activación | **La hizo el dueño**: instalación global en HOME desde un worktree fijo al commit; `install.sh --check` PASS. Declara la versión en el artefacto: `~/version.txt` + `source_version` en el manifiesto de propiedad (PD-14/INV-7 de 005-005). Registro del despliegue en `docs/epics/epic-005-real-operation/execution.md` §Pendientes para el cierre |
| Raíz de instalación | `$HOME` (global): `~/.config/opencode/skills` (+ `.agents/skills`, `.claude/skills`); manifiesto `~/.cdad-install-manifest.json`; marcador `~/version.txt` |
| Agentes de proyecto | `prepare` los publica desde la instalación global **sin** variable de entorno (005-005 T3: variable > registro de activación `.cdad/activation.json` > global). Al cerrar el epic-005 los derivados de este repo todavía declaran la versión anterior y el chequeo da `DRIFT` (pierna `project`, rc=1): republicarlos con el primer `prepare` legítimo del próximo ciclo y comprobar la versión antes de despachar; no editar derivados a mano (deuda RD-a de 005-011) |
| Regla de versión del CLI | Una sola versión de `cdad_continuity` por ejecución. La v6 no entiende las referencias con `fields` que escribe la v7 y falla cerrado (deuda `MIX-V6V7` de 003-007) |
| Checkpoints de legado | Un body sin `record` (anterior a 003-007) se lee sin bloquear: informa los cambios, también en archivos que hoy serían `contract`. "Se pudo leer" no es "sigue aprobado": el orquestador evalúa esos cambios antes de actuar y luego escribe un checkpoint nuevo con clases explícitas |

**Nota de reconciliación (2026-10-14):** la versión vigente de este registro era `35062b0`
(2026-10-10) y no reflejaba los despliegues posteriores del epic-005. Se actualiza a `29a4805`, el
commit instalado al cierre del epic. El despliegue global y la publicación de los derivados de cada
proyecto son operaciones distintas: la instalación nueva está disponible, pero no cambia las
instrucciones que una sesión ya tiene cargadas ni reinicia el servidor.

*Nota histórica (v1, `8cb6580`):* esa versión correspondía al cierre de epic-004 (las tres features
cerradas). Es la primera versión que contiene el contrato de plan borrador
(ADR-013), la subfase `plan-review`, el plan de validación por unidad y la regla de
equivalencia/re-entry.

## Verificación posterior al despliegue de 005-006 — 2026-10-10

Comprobación independiente de archivos instalados: marcador `version.txt` y
`source_version` del manifiesto = `35062b0cf1842c5fc4a09bd68c18084f78e7c8f5`,
perfil `basic`, cero conflictos. **334/334 artefactos** del manifiesto coinciden
con sus hashes, sin ausencias. Los archivos clave de arranque y comprobación
de versión de las tres bases de skills coinciden byte a byte con ese commit.
El orquestador global de OpenCode tiene la entrada de arranque desde reposo y
`<skill-dir>`, sin `$CDAD_INSTALL_ROOT`.

Esto confirma el producto instalado; no comprueba qué cargó una sesión o
servidor ya abierto. Los derivados locales del repo siguen en la versión
anterior. La R2 real de 005-006 permanece como verificación pendiente aceptada
por el dueño, según `docs/specs/005-006-guided-project-start/closure.md` §6.
El despliegue global y el refresh de esos derivados son operaciones distintas.

## Cómo se adopta (mecanismo soportado)

El bloque siguiente describe la adopción **opcional** por proyecto usada antes
del despliegue global. No es un requisito del próximo ciclo: con la instalación
global vigente y sin overrides locales, `prepare` toma esa fuente por defecto.
No introducir una raíz aislada, activación ni variable de entorno solo para
resolver derivados anteriores; republicarlos mediante el flujo normal.

1. **Raíz aislada** (nunca HOME):
   `CDAD_INSTALL_ROOT=<home>/.cache/cdad-adopted-2ec12a7 bash install.sh --force`.
2. **Ámbito de proyecto** — OpenCode descubre `.opencode/opencode.jsonc` y las
   skills de `.opencode/skills/`, con **precedencia sobre `~/.config/opencode/skills`**
   (orden documentado de fuentes). Este proyecto usa la entrada `skills` de su
   config de proyecto:
   ```jsonc
   // .opencode/opencode.jsonc  (ignorado por git: adopción local)
   { "$schema": "https://opencode.ai/config.json",
     "skills": ["<home>/.cache/cdad-adopted-2ec12a7/.config/opencode/skills"] }
   ```
3. **Agentes de proyecto** — `prepare` publica `.opencode/agents/cdad-*.md` (I9)
   desde `$CDAD_OPENCODE_AGENTS_DIR` + la política del proyecto, con el manifiesto
   `.opencode/agents/.cdad-derived.json` (que registra `source_dir` y el sha256 de
   cada derivado).

## Verificación de que el runtime carga la instalación

Verificado empíricamente el 2026-10-05, con la sesión en la raíz del repo:

1. **Skills.** Un subagente nuevo cargó `cdad-cycle` y el runtime devolvió como
   base `<home>/.cache/cdad-adopted-8cb6580/.config/opencode/skills/cdad-cycle`
   (la raíz adoptada, no el global). El cuerpo cargado contiene la oración
   `A retry (attempt) must respond to a new hypothesis or new information; …`
   (regla G3 de 004-003) — marcador ausente en la copia global. `references/re-entry.md`
   contiene `## Equivalence of a registered run (canonical rule)` (T5 de 004-003).
2. **Agentes.** `opencode debug agents` desde el repo muestra los agentes
   `cdad-implementer`, `cdad-implementer-odoo`, `cdad-orchestrator`,
   `cdad-test-writer` y `cdad-test-writer-odoo` con los mapas de permiso
   derivados (`.opencode/agents/**` deny), es decir los agentes de proyecto
   publicados por I9, no los globales.
3. **Config.** `opencode debug config` desde el repo lista
   `.opencode/opencode.jsonc` con la entrada `skills` apuntando a la raíz adoptada.
4. **Contraprueba (previa a la corrección de L1).** Desde el directorio externo,
   el mismo subagente cargó la copia global desactualizada
   (`~/.config/opencode/skills/cdad-cycle`, sin la regla G3). Es la evidencia de
   que el mecanismo de precedencia funciona y de que L1 era real.

## Enmienda declarada vigente (retirada en la adopción de `2ec12a7`)

La calibración de la review (proporcionalidad, cierre por clase, **condición verificable
de cierre**, usabilidad) se incorporó al producto en `675c18e`/`64362f8` **después** de
`8cb6580`, por lo que durante T4 de 003-002 viajó como **entrada declarada del encargo**
del reviewer (registrada en el `dispatch-ledger.md` de la feature).

**Estado: retirada.** La versión adoptada `2ec12a7` incluye la regla (verificado en el
consumidor, tabla de arriba), así que ya no hay enmienda que transportar aparte: los
agentes cargan la calibración desde su propia instalación.

*Nota de honestidad:* la calibración **no tuvo una review independiente del texto**; las
reglas las dictó el dueño, el implementer las transcribió, el orquestador verificó la
fidelidad por inspección del diff y el reviewer de T4 las **aplicó** en uso. La adopción
se hizo en el límite de feature, con esa base declarada.

## Limitaciones declaradas

**L1 — La adopción de proyecto exige que la sesión corra dentro del repo.**
OpenCode descubre `.opencode/` desde el directorio de trabajo hacia la raíz del
proyecto. La sesión del orquestador se inició en `<repo-parent>`
(el repo contenedor, que trata `cdad/` como gitlink), así que **no** veía el
`.opencode/` del repo y cargaba la copia global desactualizada de
`~/.config/opencode/skills`. Verificado empíricamente (un subagente reportó
`<home>/.config/opencode/skills/cdad-cycle` sin la sección de equivalencia de
004-003).
*Alternativa mínima aplicada:* mover la sesión al repo
(`<repo>`), que es donde ocurre el trabajo. No se
requiere maquinaria nueva ni tocar HOME.

**L2 — El instalador rechaza destinos dentro del repo.**
`CDAD_SKILL_EXTRA_DIRS=<repo>/.opencode/skills` falla con
`Managed install destination overlaps the source repository`. Por eso la adopción
de proyecto usa la entrada `skills` de la config (apuntando a la raíz aislada) en
lugar de copiar las skills dentro del repo. Ventaja adicional: **una sola copia**
(la raíz adoptada), sin duplicados que puedan divergir.

**L3 — Situación histórica: mirrors de HOME anteriores al despliegue global.**
Durante la adopción aislada no se reinstalaban y explicaban el FAIL `F011-A`.
El despliegue autorizado de 005-006 los actualizó: no usar esa explicación
histórica para descartar un drift actual. Distinguir derivados de proyecto
anteriores y cachés de Python del producto instalado.

## Política de cambio de versión

- Se adopta una versión nueva **solo entre ciclos**, y **después**
  de su revisión independiente.
- Mientras haya tareas activas, la versión adoptada **no cambia** ni se editan sus
  archivos: el árbol de trabajo evoluciona aparte (por eso la raíz adoptada es una
  copia y no un enlace al árbol).
- La versión anterior se conserva: su raíz aislada no se borra, y la tabla de
  historial de abajo mantiene la referencia.

## Historial de versiones adoptadas

| Versión | Commit | Fecha | Motivo del cambio | Referencia anterior |
|---|---|---|---|---|
| v1 | `8cb6580` | 2026-10-05 | Primera adopción: cierre de epic-004 | — |
| v2 | `2ec12a7` | 2026-10-06 | Cierre de `003-002-artifact-tools`: el producto de la feature (CLI de artefactos) y la calibración de la review entran en la versión operativa; se retira la enmienda declarada | `8cb6580` (conservada) |
| v3 | `939f501` | 2026-10-07 | Límite de tarea T4→T5 de 003-003: el guard entra en la versión operativa. Consumo verificado: un agente nuevo cargó `cdad-cycle` desde la raíz `939f501` y vio `scripts/cdad_guard.py`. Install `--check` PASS (342 grupos). | `2ec12a7` (conservada) |
| v4 | `818f12a` | 2026-10-07 | Cierre de `003-004-context-continuity`: `cdad_continuity` y `references/continuity.md` entran en la versión operativa. Install `--check` PASS (348 grupos). | `939f501` (conservada) |
| v5 | `d958672` | 2026-10-08 | Cierre de T1–T3 de `003-006-runtime-adoption` (cableado en SKILL/orquestador, `cdad-activate.py`). Install `--check` PASS (363 grupos). Recorrido por runtime de T4 en un worktree desechable (`docs/specs/003-006-runtime-adoption/adoption-ledger.md`). | `818f12a` (conservada) |
| v6 (activada por el dueño el 2026-10-08; reemplazada por v7) | `abcd4d3` | 2026-10-08 | Agrega RU-1 (`CDAD_PACKET_CLI` en el hook emitido) y RU-2 (rechazo todo o nada en `cdad_continuity`). Install `--check` PASS (363 grupos). El clasificador de permisos no dejó activarla al orquestador; **la activó el dueño** el 2026-10-08 con `cdad-activate.py` (OpenCode + Codex), y el `prepare` de 003-007 publicó sus agentes. | `d958672` (conservada) |
| v7 (instalada, no activada) | `2ed4c8d` | 2026-10-08 | T1–T2 de `003-007-living-continuity`: clases de referencia `contract`/`living`, `record`, append de checkpoint. Install `--check` PASS (363 grupos). Usada por ruta explícita en la aceptación T3 (rotación real). | `abcd4d3` (vigente) |
| v7 final (vigente; activada por el dueño el 2026-10-08) | `ce09ed0` | 2026-10-08 | Agrega T4 de 003-007: unidad despachable, clases en el cableado del orquestador, `resume` como primer paso. Install `--check` PASS (363 grupos). La sonda 2 corrió en un worktree activado con esta raíz. Activada por el dueño; los agentes de proyecto se publican en el próximo `prepare` con `CDAD_OPENCODE_AGENTS_DIR`. | `abcd4d3` (conservada) |
| v8 (desplegada en la instalación global el 2026-10-09, perfil `basic`; Check PASS) | `9396394` | 2026-10-09 | Cierre de `005-001-idle-and-v7-bootstrap`: aprobación por rol (corrige el I2 circular), `--replace-packet` con conservación y corrección del encargo, reposo legítimo en `validate-state`. Producto idéntico a `ec86ca8` (suite de cierre 629 passed, reproducida por la revisión). Install `--check` PASS (351 grupos; la diferencia con 363 son los `__pycache__` que la v7 generó al usarse). Brechas conocidas, se corrigen en 005-005: los insumos conservados en un reemplazo no se revalidan; `prepare` toma los agentes de `CDAD_OPENCODE_AGENTS_DIR` o de HOME, no del registro de activación; procedimiento y paquetes piden suite completa por GREEN. | `ce09ed0` (vigente) |
| v9 (reemplazada por el despliegue de 005-006) | `7f66619` | 2026-10-10 | Cierre de `005-005-adoption-coherence`: el reemplazo valida el encargo resultante completo (conservado + corregido), política única de evidencia, y procedencia de la instalación (variable > registro de activación > global) con la versión verificable en el artefacto publicado (`version.txt` + `source_version`). Verificado tras el despliegue por el orquestador: `source_version` del manifiesto == `~/version.txt` == `7f66619f7d928b9ef17de3c846fd8ff8cd0df4f8`, `conflicts: 0`, y el CLI instalado contiene los marcadores de 005-005 (`_activation_registry`, `_installation_version`, `_describe_installation`). Desbloquea **005-002** (dependía de la adopción de esta versión). Cierra O5 de `docs/specs/005-005-adoption-coherence/debt.md`. | `9396394` (conservada) |
| Cierre de 005-006 (reemplazada por el despliegue de 005-008) | `35062b0` | 2026-10-10 | Desplegado por instrucción directa del dueño: arranque guiado, rutas `<skill-dir>` y comprobación única de versión. Verificación independiente: marcador/manifiesto coincidentes, 334/334 hashes correctos, cero conflictos y archivos clave coincidentes en las tres bases. Derivados de proyecto anteriores y R2 real todavía pendientes; no confundir instalación con sesión cargada. | `7f66619` (respaldada por el despliegue) |

| Cierre de 005-008 (vigente, global, perfil `basic`) | `10507e5` | 2026-10-10 | Desplegado por instruccion directa del dueno («si, quiero desplegar 008»): capacidades de rutas coherentes con el clasificador (el test-writer lee y edita su arbol de tests anidado; `_test_patterns` incluye `test_files`) y diagnostico del esquema de politica que nombra el campo ofensor. Verificado: marcador/manifiesto = `10507e5…`, conflicts 0, el CLI instalado contiene el arreglo; el FAIL de `--check` es la deuda conocida de `__pycache__`. Derivados del proyecto republicados por el primer `prepare` (COHERENT rc=0). | `35062b0` (respaldada por el despliegue) |
## Despliegue global — 2026-10-09

La v8 `9396394` se desplegó en la instalación global del usuario (OpenCode, `.agents` y Claude
Code), perfil `basic` (agentes sin modelo fijo; el modelo lo elige el runtime o la delegación).
Lo ejecutó el dueño con un script local; antes se respaldaron los agentes de OpenCode
modificados a mano. Verificado: `install.sh --check` PASS (351 grupos), cero conflictos, el
`cdad_packet.py` de las tres bases de skills es el de la v8. Regla desde esta fecha: los ciclos
corren con la versión instalada al empezar; el cierre entrega la versión nueva en el repo y el
despliegue es una tarea aparte. La activación por proyecto y las raíces aisladas quedan para
pruebas. Este repo todavía tiene la activación de la v7 y agentes de proyecto propios, que tapan
la instalación global: retirarlos o alinearlos antes de 005-005.

## Despliegue global — 2026-10-10 (v9, cierre de 005-005)

La versión que produjo 005-005 (commit de cierre `7f66619`) se desplegó en la misma instalación
global, perfil `basic`, con el mismo procedimiento (worktree fijo al commit + `make staging
PROFILE=basic` + `install.sh --basic --force`); lo ejecutó el dueño con
`.cdad/local/deploy-005-005-home.sh`, que respalda lo previo en
`<workspace>/archive/20261010-opencode-agents-pre-005-005/`. **Verificación del orquestador tras el
despliegue:** `source_version` del manifiesto == `~/version.txt` ==
`7f66619f7d928b9ef17de3c846fd8ff8cd0df4f8`, `conflicts: 0`, y el CLI instalado ya contiene los
marcadores de 005-005. Con esto se cumple la dependencia declarada de 005-002 («005-005 y la
adopción de su versión»), que queda habilitada para abrirse.
