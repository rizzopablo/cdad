# Test Audit — cdad-010-opencode-permissions

> Fecha: 2026-09-12 · Rol: test-writer (AUDIT) · Ejecutado INLINE por el
> orquestador (desviación documentada: cdad-test-writer clasificado read-only
> por el bug que esta feature arregla — chicken-and-egg; delegate muerto con
> evidencia de timeouts. Riesgo de contaminación nulo: no existe
> implementación que ver). Aprobado por Pablo vía delegación HITL
> (2026-09-12, alcance: feature cdad-010).

## 1. Inventario de la suite existente

| Archivo | Qué assertiona | Relevantes a cdad-010 |
|---|---|---|
| `tests/validate-consistency.sh` (F002-F012) | asserts estáticos grep/awk sobre `agents/`, `skills/`, `scripts/` | **F009** (bash allowlists: sin `"*": allow` en write-capables, sin `cat/head/tail *`, git commit/add preservado, sin `git *` sin acotar en odoo read-only, sin `go test*` en genéricos, `make *` presente) — es el prior art directo |
| `tests/validate-odoo-specialization.sh` (sección P1) | allowlists de las 5 variantes odoo: `pylint *` presente, sin `"*": allow`, `git diff` presente, FORBIDDEN_BASH_ALL = `odoo-bin, psql, createdb, dropdb, "go ", python, curl, wget, "git *"` | Directamente afectado por P1/P4/P5 en variantes odoo |
| `scripts/validate-subagents.sh` | valida formato de agentes + impl.diff (F011 lo integra) | Indirecto |
| `scripts/cdad-models.sh` | fuente única del mapa de modelos (patrón a imitar) | Patrón para el generador P5 |
| `install.sh` | `copy_agent_file()` aplica perfil de modelo SOLO en la copia; `--check` ignora línea `model:` | P5 extiende este patrón a allowlists |

Nota menor al spec: `validate-subagents.sh` vive en `scripts/`, no en
`tests/` (el criterio de aceptación 4 lo lista mal). No bloquea.

## 2. Mapeo test↔postcondición

| Postcondición | Cobertura hoy | Gap |
|---|---|---|
| P1 (write: ask → task-able) | NINGUNA (ningún check mira la clave `write:`) | run-checks.sh: assert por agente |
| P2 (bloques autocontenidos + tests colocados) | Parcial: F009 mira orden en bash de write-capables; NADA mira `edit:` ni globs de tests colocados en OpenCode (path-guard es Claude Code only) | run-checks.sh: asserts de orden catch-all→específicas por clave + globs expandidos |
| P3 (cero ask en runtime) | NINGUNA | run-checks.sh: grep de `ask` en bash/edit/read de los 10 |
| P4 (pares rtk + denies) | NINGUNA (rtk no existe en ningún check) | run-checks.sh: pares presentes, denies presentes |
| P5 (install.sh deriva) | NINGUNA | run-checks.sh: generador existe + invocado + dry-run |
| P6 (docs) | F004 toca tabla de references de SKILL.md, no el contenido task/delegate | run-checks.sh: greps por sección en los 4 archivos |

## 3. Asserts existentes que ROMPERÍAN / hole nuevos (clasificación a/b)

1. **(b — extender F009 y odoo-P1, justificado)**: `rtk git *` es el análogo
   exacto de AP-17 para read-onlys (`rtk git push` = commit/push mutante vía
   proxy). Los asserts actuales buscan el literal `"git *": allow` y NO
   matchean `"rtk git *": allow` (la comilla previa no está junto a `git`).
   El spec P4 no lo prohibía explícitamente para read-onlys → se agrega a
   RED: `"rtk git *": allow` prohibido en TODOS los roles (git siempre
   acotado a subcomandos, directo o vía rtk).
2. **(b — odoo-P1, justificado)**: `FORBIDDEN_BASH_ALL` incluye `"go "` y
   `python` para variantes odoo → el generador P5 NO puede dar a variantes
   odoo allows de `go*`/`python*` (el stack odoo testea vía `make`/pylint).
   El generador debe ser rol×stack con set de prohibidos por stack. El spec
   P5 dice "toolchains disponibles en la máquina destino" sin esta
   excepción → registrada acá como restricción del generador (regla AUDIT).
3. **(a — spec ajustado en RED, menor)**: P2 decía globs con braces
   (`**/*.test.{js,ts,mjs,cjs}`). VERIFICADO en código (`wildcard.ts:4-7`):
   el matcher ESCAPA `{}` y `}` literalmente → braces NO funcionan. El
   generador debe expandir variantes (`**/*.test.js`, `**/*.test.ts`, ...).
   Esto resuelve el "VERIFICAR con probe" del spec por vía estática; el
   probe de confirmación queda como evidencia complementaria en GREEN.
4. **Sin roturas directas**: F009 no assertiona `edit:` ni `write:` → P1/P2
   no rompen asserts existentes; los asserts de bash de F009 siguen pasando
   con el diseño P4/P5 (catch-all deny + pares; `make *` se conserva como
   default agnóstico del repo).

## 4. Beneficio de duda / fragilidad

- `bash_section` descarta comentarios (bien), pero un valor `allow` citado
  en prosa sin `#` sería falso-positivo — mantener comentarios YAML.
- F009 valida el REPO, no las copias instaladas → drift instalado invisible;
  P5 (--check contra expectativa derivada) lo mitiga; el gap se cierra con
  criterio 5.
- `validate-odoo-specialization.sh` P1 exige `pylint *` presente en las 5
  variantes → el generador debe conservar pylint para stack odoo.

## 5. Gaps → esqueleto de asserts RED (run-checks.sh de la feature)

- A1: los 10 agentes tienen línea `write: ask` exacta.
- A2: en cada clave con reglas (edit/bash/read), el catch-all es la PRIMERA
  regla y no existe acción `ask` en bash/edit/read (verificación line-order
  con awk).
- A3: prohibido `"rtk *": allow` en los 10; presentes `"rtk err*": deny` y
  `"rtk summary*": deny` en los 10; prohibido `"rtk git *": allow` (hallazgo
  3.1).
- A4: test-writer (+odoo): denies `"rtk read*"`, `"rtk grep*"`, `"rtk
  find*"`, `"rtk diff*"` presentes; edit incluye globs de tests colocados
  EXPANDIDOS (sin braces); read incluye excepciones de lectura colocada.
- A5: implementer (+odoo): edit = catch-all propio + `tests/**` deny + tests
  colocados deny.
- A6: read-onlys (+odoo): `edit: deny` simple; sin `sed`/`tee` en bash;
  `rtk read*`/`rtk grep*`/`rtk find*` presentes.
- A7: `scripts/cdad-bash-allowlist.sh` existe, ejecutable, invocado por
  install.sh; respeta FORBIDDEN de odoo (hallazgo 3.2) y conserva `pylint *`
  en odoo.
- A8: docs P6: greps por sección (opencode-delegation.md, SKILL.md §4,
  cdad-orchestrator.md, projectbrief.md, systemPatterns.md con "write: ask"
  + "vigilancia").
- A9: cero diff en `agents/claude-code/` (git diff, criterio 6).
- A10: los 3 validadores existentes siguen en PASS (se invocan al final).

## Veredicto

AUDIT: **PASS con ajustes** — 2 extensiones de asserts justificadas (3.1,
3.2), 1 ajuste menor al spec registrado (3.3: braces → expansión), sin
roturas de asserts existentes. Suite existente sana; RED puede abrirse.

## Corrección post-RED (2026-09-12, evidencia de corrida)

El punto "suite existente sana" era INCORRECTO en un aspecto: al abrir RED,
`scripts/validate-subagents.sh` y `tests/validate-consistency.sh` (F011)
están en FAIL **preexistente** — causa: las copias instaladas en
`~/.config/opencode/agents/` driftaron del repo (las enmiendas del 02-09 y
09-08 se aplicaron a mano en las copias, violando "repo = fuente de verdad";
`install.sh --check` compara contra bytes del repo y falla). No es regresión
de cdad-010. Implicancia: el GREEN de cdad-010 (instalar desde repo con
allowlists derivadas + `--check` contra expectativa derivada, P5) debe dejar
ambos validadores en PASS — es criterio de aceptación 4. Registrado como
baseline en VALIDATION.md.
