# Adopción de CDAD por proyecto (`runtime-adoption`)

Procedimiento corto para cablear las herramientas CDAD en un proyecto sin tocar
las configuraciones del HOME real. Complementa la spec 003-006 §2.2. Los
contratos de cada comando viven en `references/continuity.md`,
`references/progress-guards.md` y `references/re-entry.md`; esta referencia solo
describe la activación.

## Comando

```sh
python3 scripts/cdad-activate.py \
  --project-root <project-root> \
  --adopted-root <adopted-root> \
  [--runtime opencode|claude-code|codex]... [--dry-run]
```

Sin `--runtime` se activan los tres. `<adopted-root>` es una raíz aislada
producida por `install.sh`; debe contener `.cdad-install-manifest.json`.

## Qué emite por runtime (siempre bajo `<project-root>`, git-ignorado)

- **opencode:** `.opencode/opencode.jsonc` con `skills` →
  `<adopted-root>/.config/opencode/skills`. Los agentes de `.opencode/agents/`
  los publica `prepare`; la activación no los toca.
- **claude-code:** `.claude/agents/<n>.md` copiados desde
  `<adopted-root>/.claude/agents/` con el `command:` del hook reescrito
  determinísticamente de `~/.claude/cdad-scripts/path-guard.sh <rol>` a
  `CDAD_PACKET_CLI=<adopted-root>/.claude/skills/cdad-cycle/scripts/cdad_packet.py <adopted-root>/.claude/cdad-scripts/path-guard.sh <rol>`
  (RU-1: el guard recibe el clasificador de la raíz adoptada vía
  `CDAD_PACKET_CLI` y deja de resolverlo desde `$HOME`), y
  `.claude/skills/<s>` como enlace simbólico a
  `<adopted-root>/.claude/skills/<s>`. **No** se emite `settings.json`.
- **codex:** `.agents/skills/<s>` como enlace simbólico a
  `<adopted-root>/.agents/skills/<s>`.

Registro: `.cdad/activation.json` con `adopted_root`, el sha256 del manifest de
`<adopted-root>` y, por cada ruta emitida, su sha256 (archivo) o su destino
(enlace). Orden determinista.

## Procedencia de los agentes de proyecto (005-005 PD-12..PD-14)

`prepare` publica los agentes de proyecto en `.opencode/agents/` y resuelve su
origen en este orden: (1) `CDAD_OPENCODE_AGENTS_DIR`; (2) la raíz adoptada
**registrada** en `.cdad/activation.json` → `<adopted_root>/.config/opencode/agents`;
(3) sin activación, la instalación global (`$HOME/.config/opencode/agents`). El
manifiesto publicado `.opencode/agents/.cdad-derived.json` declara `source_dir` y
`source_version` (versión/commit del origen), de modo que es verificable qué
versión cargó una sesión. Si el origen resuelto difiere del registro o del
`source_dir` del manifiesto anterior, `prepare` emite en **stderr** un
diagnóstico que nombra `.cdad/activation.json` y las versiones en juego: nunca
cambia de versión en silencio (INV-7). La recarga de una sesión ya iniciada y la
versión cargada se conservan como evidencia histórica **no instalable** bajo
`docs/` (006-002 PD-9: esa referencia por runtime salió del árbol instalable).

## Re-apuntar a otra raíz adoptada

Ejecutar de nuevo con el nuevo `--adopted-root`: los destinos propios se
reemplazan y las rutas propias que ya no se emiten se quitan. Un destino ajeno
que difiera de lo que se emitiría es un **conflicto**: el comando falla (rc≠0)
sin escribir nada y el mensaje nombra la ruta; `--dry-run` lo muestra sin
escribir.

## Garantías y límites

- Determinista: mismo `(project_root, adopted_root)` → bytes y enlaces idénticos.
- **Nunca** escribe en `~/.claude`, `~/.agents` ni `~/.config/opencode`: solo bajo
  `<project-root>`. La raíz adoptada versionada bajo `~/.cache` la escribe la
  re-adopción, no este comando.
- Identidad de versión (R-4): cada archivo fuente consumido de `<adopted-root>` se
  compara con el sha256 de su entrada en `.cdad-install-manifest.json`; si falta
  la entrada o el sha difiere, falla (rc≠0) y no escribe nada.
- No-clobber con propiedad (R-5): un destino existente se reemplaza solo si lo
  emitió el generador (está en `.cdad/activation.json` y su contenido coincide
  con lo registrado); cualquier otro destino divergente es conflicto
  (todo o nada).
- Contención de ruta (B-1): antes de escribir o podar, el directorio contenedor
  de cada destino (componentes intermedios incluidos) se resuelve con
  `realpath` y debe quedar bajo `realpath(<project-root>)`; un symlink que
  escape de R es conflicto nombrado (rc≠0, todo o nada).
- Python stdlib solamente.
