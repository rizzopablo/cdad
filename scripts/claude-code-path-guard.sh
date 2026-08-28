#!/bin/bash
# CDAD Claude Code Path Guard — reconstruye path-scoping via PreToolUse hook
#
# Uso: lee JSON por stdin (tool_name, tool_input.file_path, etc.)
# Invoke: command: "~/.claude/cdad-scripts/path-guard.sh <rol>"
#
# Roles:
#   implementer         → bloquea Edit/Write a tests/**
#   test-writer-read   → bloquea Read/Grep/Glob a src/** y lib/**
#   test-writer-write  → bloquea Edit/Write a todo excepto tests/**
#   implementer-odoo   → alias de implementer (bloquea Edit/Write a **/tests/**)
#   test-writer-odoo-read  → bloquea Read/Grep/Glob a models/views/controllers/wizards
#   test-writer-odoo-write → bloquea Edit/Write a todo excepto **/tests/**

set -e

ROL="${1:-unknown}"

# Lee el JSON del hook desde stdin
INPUT=$(cat)

# Extrae tool_name y file_path con jq
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Si no hay file_path (e.g., Bash sin --file-path), permite
if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Normaliza file_path a RELATIVO al proyecto (PWD) para que los globs relativos
# (tests/**, src/**, lib/**) matcheen tanto rutas relativas como absolutas.
# Fix B: sin esto, un sub-agente podía pasar una ruta absoluta (/abs/.../tests/x)
# y evadir el guard (la ruta absoluta no matchea el glob relativo).
relativize() {
  local p="$1"
  # expande ~/ si viene
  p="${p/#\~\//$HOME\/}"
  # si es absoluta bajo $PWD, la relativiza
  if [[ "$p" == "$PWD"* ]]; then
    p="${p#$PWD}"
    p="${p#/}"
  else
    # absoluta fuera del proyecto: quita el root para comparación relativa
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

  [[ "$path" =~ $pattern ]] && return 0 || return 1
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
