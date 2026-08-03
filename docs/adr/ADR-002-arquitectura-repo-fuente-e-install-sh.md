# ADR-002: Repo fuente como única fuente de verdad + install.sh para propagación

- **Status**: Accepted
- **Date**: 2026-08-03
- **Deciders**: Pablo Rizzo + Ofap

## Contexto

El skill `cdad-cycle` y los skills `cdad-epic`/`cdad-spec-and-test` existían en 3 copias: el repo fuente `cdad/cdad/`, `~/.config/opencode/skills/` y `~/.agents/skills/`. Editar una instalación directamente generaba drift garantizado entre las copias. Además, los 5 sub-agentes CDAD (ADR-001) recién creados existían solo en `~/.config/opencode/agents/` — no viajaban con el framework al clonar en otra máquina.

## Opciones consideradas

### Opción A: Editar las instalaciones directamente (status quo)
- Pros: inmediato, cero setup.
- Contras: drift entre repo/config/.agents; los agentes no viajan con el framework; imposible de reproducir en otra máquina.

### Opción B: Repo fuente como fuente de verdad + script install.sh que copia a runtimes
- Pros: el repo es la única fuente; instalaciones regenerables; los agentes viajan con el framework; workflow claro (editar repo → install.sh → propagar).
- Cons: hay que re-correr install.sh tras cada cambio del repo (aceptado, con `--check` para detectar drift).

### Opción C: Symlinks del repo a las instalaciones
- Pros: cambios propagan automáticamente.
- Contras: VERIFICADO que las instalaciones actuales son copias independientes (no symlinks) con mtime preservado; cambiar a symlinks sería un cambio de comportamiento silencioso; los runtimes pueden escribir/borrar (riesgo de corrupción del repo).

## Decisión

Desarrollo SIEMPRE en el repo fuente `cdad/cdad/`. Los agentes viven versionados en `cdad/agents/` (formato opencode, runtime de referencia) y los skills en `cdad/skills/`. Un script `install.sh` (idempotente, flags `--dry-run/--force/--uninstall/--check/--help`) copia skills + agentes a los runtimes.

## Razones

1. Pablo explícito: "hace todo el desarrollo en el dir de fuentes, luego los instalas (un script install.sh puede ser útil)".
2. Verificado: instalaciones actuales son copias independientes byte-idénticas (firma cp -p/rsync -a), no symlinks.
3. `cdad-spec-and-test` existía SOLO en `.config` — el repo debe ser fuente completa.
4. install.sh nunca usa `--delete` (targets tienen contenido no-cdad) y nunca toca `.agents/.skill-lock.json` ni los 7 agentes no-Cdad.

## Consecuencias

**Positivas:**
- Repo = fuente única de verdad. Instalaciones regenerables con `install.sh`.
- Los agentes viajan con el framework (clonar repo → install.sh → listo).
- `--check` detecta drift (comparación byte-a-byte de los 11 artefactos).

**Negativas / trade-offs:**
- Requiere re-correr install.sh tras cada cambio del repo (mitigado con `--check` + mensaje "re-run after git pull").
- Los 4 `.md` sueltos en `skills/` (re-entry, feature-handoff, handoff-prompts, epic-planning) no se instalan (bare .md != skill dir) — documentado como intencional.

**Neutrales:**
- La instalación de `.config` y `.agents` son regenerables; no hay estado único irremplazable.

## Notas

Decisión de ubicación: `cdad/agents/` SIN subdir `opencode/` — los agentes son roles CDAD multi-runtime; probar en opencode ≠ pertenecer a opencode. Formato de archivo = sintaxis opencode (runtime de referencia) por ahora.
