#!/bin/bash
# CDAD Claude Code Path Guard — reconstruye path-scoping via PreToolUse hook
#
# Uso: lee JSON por stdin (tool_name, tool_input.file_path o
# tool_input.command según la herramienta).
# Invoke: command: "~/.claude/cdad-scripts/path-guard.sh <rol>"
#
# Roles basados en file_path (Read/Grep/Glob/Edit/Write):
#   implementer         → bloquea Edit/Write a tests/**
#   test-writer-read   → bloquea Read/Grep/Glob a src/** y lib/**
#   test-writer-write  → bloquea Edit/Write a todo excepto tests/**
#   implementer-odoo   → alias de implementer (bloquea Edit/Write a **/tests/**)
#   test-writer-odoo-read  → bloquea Read/Grep/Glob a models/views/controllers/wizards
#   test-writer-odoo-write → bloquea Edit/Write a todo excepto **/tests/**
#
# Roles basados en command (Bash) — ver findings/audit-consistencia-2026-09-02.md
# B1: el matcher de arriba solo cubre Read/Grep/Glob/Edit/Write; Bash quedaba
# sin cubrir y era la fuga real (cat src/x.py, sed -i tests/x.py, etc.). No
# intenta parsear qué PATH toca el comando (frágil, bash es Turing-completo);
# en cambio bloquea comandos de lectura/escritura de CONTENIDO por nombre —
# el mismo diseño que la allowlist bash de los agentes OpenCode: Bash sirve
# para CORRER cosas (tests, git, navegación), no para leer/escribir contenido
# (para eso están Read/Edit, correctamente scopeados por el matcher de arriba):
#   test-writer-bash | implementer-bash | test-writer-odoo-bash | implementer-odoo-bash
#     → bloquea comandos de lectura de contenido (cat/head/tail/sed/awk/grep/
#       rg/less/more/intérpretes) y de escritura por redirección (>, >>, tee,
#       sed -i). NO bloquea git/make/pytest/ls/find/wc/pwd — esa es la
#       allowlist legítima, calibrada para no forzar al agente a buscar
#       rodeos.

set -e

ROL="${1:-unknown}"

# Lee el JSON del hook desde stdin
INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')

# ── Guarda de contenido vía Bash (comandos, no paths) ───────────────────────
BASH_CONTENT_GUARD_ROLES="test-writer-bash implementer-bash test-writer-odoo-bash implementer-odoo-bash"
if [[ "$TOOL_NAME" == "Bash" ]] && [[ " $BASH_CONTENT_GUARD_ROLES " == *" $ROL "* ]]; then
  COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
  if [[ -z "$COMMAND" ]]; then
    exit 0
  fi
  # Primer token del comando (nombre del binario), ignorando espacio inicial.
  first_word() { printf '%s' "$1" | sed -E 's/^[[:space:]]+//' | awk '{print $1}'; }
  CMD_NAME="$(first_word "$COMMAND")"
  CMD_NAME="${CMD_NAME##*/}"  # sin path (/usr/bin/cat -> cat)

  DENY_CONTENT_READ="cat head tail less more sed awk grep egrep fgrep rg ag python python3 node perl ruby php xxd od strings view vim vi nano emacs"
  for bad in $DENY_CONTENT_READ; do
    if [[ "$CMD_NAME" == "$bad" ]]; then
      exit 2  # Bloquea: comando de lectura de contenido
    fi
  done
  # Escritura por redirección o tee/sed-i, en cualquier parte del comando
  # (incluye pipelines: "foo | tee bar", "echo x >> tests/y").
  if [[ "$COMMAND" == *">"* ]] || [[ "$COMMAND" == *"tee "* ]] || [[ "$COMMAND" =~ sed[[:space:]]+-i ]]; then
    exit 2  # Bloquea: escritura de contenido vía shell
  fi
  exit 0  # Todo lo demás (make, pytest, git, ls, find, wc, pwd, ...) pasa
fi

FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Si no hay file_path (p.ej. Bash en un rol sin bash-content-guard, o una
# tool sin path), permite — el guard de esta sección es por path, no aplica.
if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Normaliza file_path a RELATIVO al proyecto (PWD) para que los globs relativos
# (tests/**, src/**, lib/**) matcheen tanto rutas relativas como absolutas.
# Fix B: sin esto, un sub-agente podía pasar una ruta absoluta (/abs/.../tests/x)
# y evadir el guard (la ruta absoluta no matchea el glob relativo).
#
# Fix C (B1): una ruta absoluta que NO cae bajo $PWD (otro root distinto,
# symlink, etc.) se marcaba ABS_OUTSIDE_PWD=0 antes y se relativizaba a ciegas
# (quitaba el "/" inicial y listo) — "/home/otro/src/x.py" quedaba como
# "home/otro/src/x.py", que NO matchea el glob "src/**" y pasaba sin bloqueo.
# Ahora se marca explícitamente; matches_glob() prueba también el glob con
# prefijo "**/" para ese caso, así "algo/.../src/x.py" sigue matcheando
# "src/**" sin importar cuántos directorios haya antes.
ABS_OUTSIDE_PWD=0
# Calculado ACÁ (shell principal), no dentro de relativize(): esa función se
# invoca vía "$(...)" (subshell) más abajo, así que cualquier asignación de
# variable hecha adentro se pierde al volver — hay que decidirlo antes.
EXPANDED_FILE_PATH="${FILE_PATH/#\~\//$HOME\/}"
if [[ "$EXPANDED_FILE_PATH" == /* && "$EXPANDED_FILE_PATH" != "$PWD"* ]]; then
  ABS_OUTSIDE_PWD=1
fi
relativize() {
  local p="$1"
  # expande ~/ si viene
  p="${p/#\~\//$HOME\/}"
  # si es absoluta bajo $PWD, la relativiza
  if [[ "$p" == "$PWD"* ]]; then
    p="${p#$PWD}"
    p="${p#/}"
  elif [[ "$p" == /* ]]; then
    # absoluta fuera del proyecto: no hay forma fiable de saber si "es la
    # misma carpeta con otro root" — se trata como potencialmente peligrosa
    # (ABS_OUTSIDE_PWD ya quedó en 1, calculado arriba en el shell padre).
    p="${p#/}"
  fi
  # quita ./, duplicados /, y trailing /
  p="${p#./}"
  p="${p//\/\//\/}"
  p="${p%/}"
  printf '%s' "$p"
}
FILE_PATH="$(relativize "$FILE_PATH")"

# Función helper: ¿matchea un glob?
matches_glob() {
  local path="$1"
  local glob="$2"

  # Base exacta (tests, tests/) también matchea tests/** — evita bypass por dir sin contenido
  local base="${glob%/**}"
  if [[ "$path" == "$base" || "$path" == "$base/" ]]; then
    return 0
  fi

  # Sustituye ** por un patrón regex que matchea cualquier profundidad
  local pattern="${glob//\*\*/.+}"
  pattern="${pattern//\*/[^/]*}"
  pattern="^${pattern}$"

  if [[ "$path" =~ $pattern ]]; then
    return 0
  fi

  # Fix C: si la ruta original era absoluta y de fuera de $PWD, probá
  # también el glob con "**/" al frente — cubre "cualquier root, después
  # <glob>" en vez de exigir que el glob matchee desde la raíz relativizada.
  if [[ "$ABS_OUTSIDE_PWD" == "1" && "$glob" != "**/"* ]]; then
    local wide_pattern=".+/${pattern#^}"
    [[ "$path" =~ $wide_pattern ]] && return 0
  fi

  return 1
}

# Lógica por rol
case "$ROL" in
  implementer)
    # Bloquea Edit/Write a tests/**
    if [[ "$TOOL_NAME" =~ ^(Edit|Write)$ ]]; then
      if matches_glob "$FILE_PATH" "tests/**"; then
        exit 2  # Bloquea
      fi
    fi
    exit 0  # Permite todo lo demás
    ;;

  implementer-odoo)
    # Alias de implementer, variante Odoo: bloquea Edit/Write a **/tests/**.
    if [[ "$TOOL_NAME" =~ ^(Edit|Write)$ ]]; then
      if matches_glob "$FILE_PATH" "**/tests/**"; then
        exit 2  # Bloquea
      fi
    fi
    exit 0  # Permite todo lo demás
    ;;

  test-writer-read)
    # Bloquea Read/Grep/Glob a src/** y lib/**
    if [[ "$TOOL_NAME" =~ ^(Read|Grep|Glob)$ ]]; then
      if matches_glob "$FILE_PATH" "src/**" || matches_glob "$FILE_PATH" "lib/**"; then
        exit 2  # Bloquea
      fi
    fi
    exit 0  # Permite todo lo demás
    ;;

  test-writer-odoo-read)
    # Bloquea Read/Grep/Glob a la implementación Odoo (models/views/controllers/wizards).
    if [[ "$TOOL_NAME" =~ ^(Read|Grep|Glob)$ ]]; then
      if matches_glob "$FILE_PATH" "**/models/**" \
        || matches_glob "$FILE_PATH" "**/views/**" \
        || matches_glob "$FILE_PATH" "**/controllers/**" \
        || matches_glob "$FILE_PATH" "**/wizards/**"; then
        exit 2  # Bloquea
      fi
    fi
    exit 0  # Permite todo lo demás
    ;;

  test-writer-write)
    # Bloquea Edit/Write a todo excepto tests/**
    if [[ "$TOOL_NAME" =~ ^(Edit|Write)$ ]]; then
      if ! matches_glob "$FILE_PATH" "tests/**"; then
        exit 2  # Bloquea
      fi
    fi
    exit 0  # Permite todo lo demás
    ;;

  test-writer-odoo-write)
    # Bloquea Edit/Write a todo excepto **/tests/**
    if [[ "$TOOL_NAME" =~ ^(Edit|Write)$ ]]; then
      if ! matches_glob "$FILE_PATH" "**/tests/**"; then
        exit 2  # Bloquea
      fi
    fi
    exit 0  # Permite todo lo demás
    ;;

  *)
    # Rol desconocido → permite (fail-open)
    exit 0
    ;;
esac
