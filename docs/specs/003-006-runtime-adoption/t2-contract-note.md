# Nota de contrato para T2 — `scripts/cdad-activate.py` (orquestador)

Precisa la spec §2.2 sin ampliarla. Rige el RED y el GREEN de T2.

## Entrada
`--project-root R --adopted-root A [--runtime opencode|claude-code|codex]... [--dry-run]`.
Sin `--runtime` se activan los tres. `A` es una raíz aislada producida por `install.sh`
con `A/.cdad-install-manifest.json` (`artifacts: {<ruta relativa a A>: {sha256, source}}`).

## Identidad de versión (R-4)
Antes de escribir, cada archivo fuente que se va a usar de `A` se compara con el
`sha256` de su entrada en el manifest. Si falta la entrada o el sha difiere: error
(rc≠0) y no se escribe nada.

## Salidas por runtime (todas bajo `R`)
- **opencode:** `.opencode/opencode.jsonc` = JSON con `"$schema": "https://opencode.ai/config.json"`
  y `"skills": ["<A>/.config/opencode/skills"]`. Los agentes de `.opencode/agents/` los publica `prepare`; no se tocan.
- **claude-code:** `.claude/agents/<n>.md` = copia de cada `A/.claude/agents/<n>.md` con la
  reescritura de toda línea `command: ~/.claude/cdad-scripts/path-guard.sh <rol>` a
  `command: <A>/.claude/cdad-scripts/path-guard.sh <rol>`. Ningún `command:` emitido contiene `~/.claude`.
  `.claude/skills/<s>` = enlace simbólico a `A/.claude/skills/<s>` por cada skill. **No** se emite `settings.json`.
- **codex:** `.agents/skills/<s>` = enlace simbólico a `A/.agents/skills/<s>` por cada skill.
- **registro:** `.cdad/activation.json` con `adopted_root`, sha256 del manifest de `A` y, por cada
  ruta emitida, su sha256 (archivo) o su destino (enlace). Orden de claves y listas determinista.

## No-clobber con propiedad (R-5)
Una ruta destino que ya existe se puede reemplazar **solo si** está en el
`.cdad/activation.json` previo y su contenido actual coincide con lo registrado (la emitió
el generador y nadie la tocó). Cualquier otro destino existente que difiera de lo que se
emitiría → error (rc≠0), no se escribe nada (todo o nada) y el mensaje nombra la ruta.
Si el destino existe y es idéntico a lo que se emitiría, no es conflicto.
Re-apuntar a otra `A` reemplaza lo propio y quita las rutas propias que ya no se emiten.

## Garantías
- Determinista: dos corridas con la misma entrada dejan bytes y enlaces idénticos.
- `--dry-run`: lista las rutas que escribiría y los conflictos; no escribe nada.
- Nunca escribe fuera de `R` (en particular nada bajo `$HOME` salvo que `R` esté allí).
- `.gitignore` del repo cubre `.claude/` y `.agents/` (además de `.opencode/` y `.cdad/`).
- stdlib solamente.
