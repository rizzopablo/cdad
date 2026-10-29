# Spec — 009-002: el generador emite frontmatter V2 de OpenCode

- **Feature:** `009-002-opencode-v2-frontmatter` (epic-009-installer-updates)
- **Modo:** light, decidido por el dueño el 2026-10-28. **Desvío declarado:** la spec la redacta el
  orquestador (no el architect) porque el diseño está determinado por una referencia que funciona en el
  runtime (los 11 agentes convertidos y verificados) y por el emisor V1 actual; el riesgo de diseño es bajo.
- **Origen:** reporte de la instalación del 2026-10-28. Un agente con `permission:` (mapa, V1) se lee como V1
  y **el runtime ignora `model:`**; con `permissions:` (lista, V2) el modelo resuelve.

## Problema

CDAD genera agentes OpenCode en **V1** (`permission:` mapa, `temperature:` top-level, `edit: deny` inerte).
Con ese formato el `model:` que el usuario configura **no tiene efecto**, y `install.sh --check` compara V1
del repo contra V2 instalado → drift permanente en los 11 agentes y conversión manual en cada actualización.

## Decisión

El generador (`scripts/cdad-generate.py::oc_frontmatter`) emite **V2 nativo**. La instalación no transforma
bytes (T5: despliega el staging tal cual).

## Postcondiciones

- **PC-1.** Todo agente OpenCode generado (`agents/opencode/*.md`, `build/staging/agents/opencode/*.md`) tiene
  `permissions:` como **lista** de entradas `{action, resource, effect}`; no contiene `permission:`,
  `temperature:` top-level ni `edit: deny` inerte.
- **PC-2.** Cada regla del mapa V1 aparece **exactamente una vez** en la lista V2, con el mismo `action`
  (`read`/`edit`/`grep`/`shell`), el mismo `resource` y el mismo `effect`, **en el mismo orden**.
  El bloque de bash pasa a entradas `action: shell`.
- **PC-3.** Sólo el reviewer lleva `request: body: temperature: 0.1`; los demás roles no llevan `request`.
- **PC-4.** El orquestador conserva `mode: all` y su política permisiva en forma V2 válida (YAML parseable),
  sin claves sin comillas que rompan el parseo.
- **PC-5.** Los agentes de Claude Code (`agents/claude-code/*.md`) **no cambian** (esquema propio, `tools:`).
- **PC-6.** `make agents` es **idempotente** (dos corridas → bytes idénticos) y, tras regenerar, una
  instalación limpia deja `install.sh --check` **PASS** (los bytes comparados son V2 a ambos lados).
- **PC-7.** La ruta legacy de `--check` (`apply_bash_block`) entiende la forma V2 o se retira con motivo
  declarado; no puede quedar comparando una forma que ya no se emite.

## Invariantes

1. **Semántica de permisos intacta:** mismos globs, mismos efectos, mismo orden de evaluación; el cambio es de
   **forma**, no de política. Un rol de sólo lectura sigue sin poder editar; el test-writer sigue sin ver la
   implementación.
2. **Nada de modelos en el texto instalable** (INV-3 de 006-003): el generador no emite `model:`.
3. **Un solo emisor:** no se agrega un conversor posterior; el formato se decide en el generador.

## Unidades

| U | Contenido | Aceptación |
|---|---|---|
| U1 | Tests de forma y equivalencia sobre los agentes generados (PC-1…PC-5) | fallan hoy (V1) por `AssertionError` |
| U2 | `oc_frontmatter` V2 + regeneración (`make agents`) + `apply_bash_block` V2 o retiro declarado | PC-1…PC-7; `make agents` idempotente |

## Límites declarados

- No se valida la semántica del runtime desde el repo (requiere el binario): se acredita con la referencia
  convertida que ya funciona y con un test estático de forma.
- No se toca la política de permisos ni el contenido de los roles.
- `install.sh --check` sobre un HOME ya convertido a V2 seguirá marcando drift hasta reinstalar: es esperado.
