#!/usr/bin/env bash
# install.sh — CDAD skills & agents installer
#
# Copies CDAD skills and agents from this repo into the runtime directories
# (~/.config/opencode and ~/.agents). Copies are independent (cp -rp / rsync -a,
# cp -p for files), never symlinks. Only cdad-owned paths are touched; the
# 7 non-cdad agents and ~/.agents/.skill-lock.json are left alone. The 4 loose
# top-level skills/*.md files (re-entry.md, feature-handoff.md,
# handoff-prompts.md, epic-planning.md) are reference docs, NOT valid runtime
# skill dirs (bare .md != skill dir), and are intentionally never installed.
# When CDAD_SKILL_EXTRA_DIRS is set (colon-separated), the 3 skills are also
# installed into each extra dir (e.g. the OpenClaw skills dir).

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SKILLS_DIR="$SCRIPT_DIR/skills"
SOURCE_AGENTS_DIR="$SCRIPT_DIR/agents"

OPENCODE_AGENTS_DIR="${HOME:-}/.config/opencode/agents"
OPENCODE_SKILLS_DIR="${HOME:-}/.config/opencode/skills"
AGENTS_SKILLS_DIR="${HOME:-}/.agents/skills"

CLAUDE_CODE_AGENTS_DIR="${HOME:-}/.claude/agents"
CLAUDE_CODE_SKILLS_DIR="${HOME:-}/.claude/skills"
CLAUDE_CODE_SCRIPTS_DIR="${HOME:-}/.claude/cdad-scripts"

SKILLS=(cdad-cycle cdad-epic cdad-spec-and-test)
EXPECTED_CDAD_AGENTS=6
# NOTE: EXPECTED_CDAD_AGENTS counts OpenCode agents. Claude Code has the same 5 roles
# in agents/claude-code/ subdirectory; install_claude_code_agents() handles that separately.
EXPECTED_CDAD_AGENTS_CLAUDE_CODE=5

# Extra skill target dirs (colon-separated) via CDAD_SKILL_EXTRA_DIRS, e.g. the
# OpenClaw skills dir. Empty by default: only the default runtimes are used.
# Not hardcoded here: this repo is public, each deployer sets their own value.
EXTRA_SKILLS_DIRS="${CDAD_SKILL_EXTRA_DIRS:-}"

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
DRY_RUN=0
FORCE=0
UNINSTALL=0
CHECK=0
PROFILE_FLAG=""
MODEL_PROFILE=""
PROFILE_MARKER="$OPENCODE_AGENTS_DIR/.cdad-models-profile"

if command -v rsync >/dev/null 2>&1; then
  HAS_RSYNC=1
else
  HAS_RSYNC=0
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

# ---------------------------------------------------------------------------
# Model profiles — fuente única del mapa (scripts/cdad-models.sh)
# ---------------------------------------------------------------------------
MODELS_SH="$SCRIPT_DIR/scripts/cdad-models.sh"
if [ ! -f "$MODELS_SH" ]; then
  die "Model profiles script missing: $MODELS_SH"
fi
# shellcheck source=scripts/cdad-models.sh
source "$MODELS_SH"

# do_run desc cmd [args...] — log the action, then execute (or skip in dry-run)
do_run() {
  local desc="$1"
  shift
  if [ "$DRY_RUN" -eq 1 ]; then
    log "DRY-RUN $desc"
  else
    log "$desc"
    "$@"
  fi
}

ensure_dir() {  # dir — creates it; halts loudly if impossible
  if [ ! -d "$1" ]; then
    if [ "$DRY_RUN" -eq 1 ]; then
      log "DRY-RUN MKDIR $1"
    else
      mkdir -p "$1" || die "Cannot create directory: $1"
    fi
  fi
}

count_flat_files() {  # dir pattern -> number of matching files (0 if dir missing)
  local dir="$1" pattern="$2"
  if [ -d "$dir" ]; then
    find "$dir" -maxdepth 1 -type f -name "$pattern" 2>/dev/null | wc -l | tr -d ' '
  else
    printf '0'
  fi
}

count_tree_files() {  # dir -> number of files recursively (0 if dir missing)
  local dir="$1"
  if [ -d "$dir" ]; then
    find "$dir" -type f 2>/dev/null | wc -l | tr -d ' '
  else
    printf '0'
  fi
}

count_manifest_agents_installed() {  # dir -> how many repo-manifest agent names are present there
  local dir="$1"
  local f base count=0
  if [ ! -d "$dir" ]; then
    printf '0'
    return 0
  fi
  for f in "$SOURCE_AGENTS_DIR"/cdad-*.md; do
    [ -e "$f" ] || continue
    base=$(basename "$f")
    if [ -f "$dir/$base" ]; then
      count=$((count + 1))
    fi
  done
  printf '%s' "$count"
}

# extra_skills_dirs — prints each configured extra skill target dir on its own
# line (safe to iterate with `while read`). Empty output when CDAD_SKILL_EXTRA_DIRS
# is unset, so every caller keeps the default behavior untouched.
extra_skills_dirs() {
  local dir
  local -a dirs=()
  if [ -z "$EXTRA_SKILLS_DIRS" ]; then
    return 0
  fi
  IFS=: read -r -a dirs <<< "$EXTRA_SKILLS_DIRS" || true
  for dir in "${dirs[@]}"; do
    if [ -n "$dir" ]; then
      printf '%s\n' "$dir"
    fi
  done
}

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------
usage() {
  cat <<'EOF'
usage: install.sh [options]

CDAD installer — copies CDAD skills and agents from this repo into the
runtime directories (~/.config/opencode and ~/.agents).

Options:
  --dry-run    Show what would be done without changing anything.
  --force      Skip confirmation prompts and overwrite read-only targets.
               The default install is already idempotent (it overwrites in
               place and shows no prompt), so --force mainly matters for
               --uninstall, which without it asks for confirmation first.
  --uninstall  Remove ONLY the cdad-*.md agents (from the repo manifest) in
               ~/.config/opencode/agents and the 3 cdad skill dirs from both
               runtimes. Asks for confirmation unless --force is given.
  --check      Verify installed files match the repo (exit 1 on drift).
               --status is an alias. Agents are compared profile-aware: the
               model: line must match the ACTIVE profile (flag/env
               CDAD_MODEL_PROFILE > marker .cdad-models-profile > optimus).
   --economical Install the economical profile (execution roles deepseek-v4-flash;
                architect deepseek-v4-pro, reviewer minimax-m3 — familia
                distinta al implementer). Cheap run, spec/review quality kept
                (enmienda 2026-08-24, ADR-007).
  --optimus    Install the optimus profile (design default): architect/scribe
               deepseek-v4-pro, test-writer glm-5.2, implementer flash,
               reviewer qwen3.7-plus. Balanced cost/quality.
  --premium    Install the premium profile (top-tier configurable por env):
               por default architect/reviewer/scribe qwen3.7-max, implementer
               deepseek-v4-pro, test-writer glm-5.2. Cada rol es overrideable
               con una env CDAD_PREMIUM_MODEL_<ROL> en formato provider/model
               de CUALQUIER provider (p.ej. anthropic/openai); el provider de
               destino debe estar configurado en el runtime.
               The profile flags are mutually exclusive.
  --help       Show this help and exit.

No flags = install (safe default). The profile is STATEFUL: the last profile
installed persists via .cdad-models-profile, so a later install without flag
or env reuses it instead of falling back to optimus. Precedence is the same
everywhere (install, --check, --dry-run):
    flag > env CDAD_MODEL_PROFILE > marker .cdad-models-profile > optimus
Fresh installs (no marker yet) default to optimus (the repo's design default);
switch profiles at any time with `install.sh --<perfil>` — the new choice is
installed AND persisted as the marker.

Environment — premium overrides (top-tier multi-provider; sin prefijo mofgw
forzado; el provider de destino debe estar configurado en el runtime, p.ej.
opencode.jsonc):
  CDAD_PREMIUM_MODEL_ARCHITECT    top-tier architect (default mofgw/qwen3.7-max)
  CDAD_PREMIUM_MODEL_TEST_WRITER  top-tier test-writer (default mofgw/glm-5.2)
  CDAD_PREMIUM_MODEL_IMPLEMENTER  top-tier implementer (default mofgw/deepseek-v4-pro)
  CDAD_PREMIUM_MODEL_REVIEWER     top-tier reviewer (default mofgw/qwen3.7-max)
  CDAD_PREMIUM_MODEL_SCRIBE       top-tier scribe (default mofgw/qwen3.7-max)
  Ejemplo: CDAD_PREMIUM_MODEL_REVIEWER=anthropic/claude-sonnet-4-5 \
           bash install.sh --premium
  CDAD_SKILL_EXTRA_DIRS  colon-separated list of ADDITIONAL directories where
               the 3 cdad skills are also installed (e.g. the OpenClaw skills
               dir). Empty by default: only the default runtimes are used.
               Applied to install, --check, --uninstall and --dry-run.

What gets installed:
  skills/cdad-{cycle,epic,spec-and-test}/
      -> ~/.config/opencode/skills/<skill>/   (rsync -a, NEVER --delete; or cp -rp)
      -> ~/.agents/skills/<skill>/            (rsync -a, NEVER --delete; or cp -rp)
      -> ~/.claude/skills/<skill>/            (rsync -a, NEVER --delete; or cp -rp) [Claude Code]
      -> <dir>/<skill>/ for each dir in $CDAD_SKILL_EXTRA_DIRS when set
                                           (rsync -a, NEVER --delete; or cp -rp)
  agents/cdad-*.md (OpenCode format)
      -> ~/.config/opencode/agents/           (cp -p, NEVER --delete)
  agents/claude-code/cdad-*.md (Claude Code format)
      -> ~/.claude/agents/                    (cp -p, NEVER --delete)
  scripts/claude-code-path-guard.sh
      -> ~/.claude/cdad-scripts/path-guard.sh (cp -p, chmod +x)

Note: the 4 loose top-level skills/*.md files (re-entry.md, feature-handoff.md,
handoff-prompts.md, epic-planning.md) are reference docs, not valid skill dirs
(bare .md != skill dir), and are intentionally NOT installed.

Never touched: non-cdad agents in ~/.config/opencode/agents or ~/.claude/agents,
~/.agents/.skill-lock.json, or anything outside the cdad paths above.
EOF
}

# ---------------------------------------------------------------------------
# Option parsing (getopts, with long-option normalization)
# ---------------------------------------------------------------------------
parse_options() {
  local normalized=()
  local arg
  for arg in "$@"; do
    case "$arg" in
      --dry-run)   normalized+=(-d) ;;
      --force)     normalized+=(-f) ;;
      --uninstall) normalized+=(-u) ;;
      --check)     normalized+=(-c) ;;
      --status)    normalized+=(-c) ;;
      --economical) normalized+=(-e) ;;
      --optimus)   normalized+=(-o) ;;
      --premium)   normalized+=(-p) ;;
      --help)      normalized+=(-h) ;;
      --*)         die "Unknown option: $arg (see --help)" ;;
      *)           normalized+=("$arg") ;;
    esac
  done
  set -- "${normalized[@]}"

  local opt profile_count=0
  while getopts "dfuceoph" opt; do
    case "$opt" in
      d) DRY_RUN=1 ;;
      f) FORCE=1 ;;
      u) UNINSTALL=1 ;;
      c) CHECK=1 ;;
      e) PROFILE_FLAG=economical; profile_count=$((profile_count + 1)) ;;
      o) PROFILE_FLAG=optimus;    profile_count=$((profile_count + 1)) ;;
      p) PROFILE_FLAG=premium;    profile_count=$((profile_count + 1)) ;;
      h) usage; exit 0 ;;
      *) usage; exit 1 ;;
    esac
  done
  shift $((OPTIND - 1))
  if [ $# -gt 0 ]; then
    die "Unexpected arguments: $* (see --help)"
  fi
  if [ "$profile_count" -gt 1 ]; then
    die "Profile flags are mutually exclusive: use only one of --economical | --optimus | --premium"
  fi
}

# ---------------------------------------------------------------------------
# Guards (fail fast, early exit)
# ---------------------------------------------------------------------------
guard_home() {
  if [ -z "${HOME:-}" ] || [ ! -d "$HOME" ]; then
    die "Cannot resolve home directory (\$HOME is empty or not a directory)"
  fi
}

guard_sources() {
  if [ ! -d "$SOURCE_SKILLS_DIR" ]; then
    die "Source skills directory missing: $SOURCE_SKILLS_DIR"
  fi
  if [ ! -d "$SOURCE_AGENTS_DIR" ]; then
    die "Source agents directory missing: $SOURCE_AGENTS_DIR"
  fi
  local s
  for s in "${SKILLS[@]}"; do
    if [ ! -d "$SOURCE_SKILLS_DIR/$s" ]; then
      die "Source skill missing: $SOURCE_SKILLS_DIR/$s"
    fi
  done
  if [ "$(count_flat_files "$SOURCE_AGENTS_DIR" 'cdad-*.md')" -lt 1 ]; then
    die "No cdad-*.md agent files found in $SOURCE_AGENTS_DIR"
  fi
}

# ---------------------------------------------------------------------------
# Profile resolution (fail fast on invalid profile)
# ---------------------------------------------------------------------------
# resolve_profile — asigna MODEL_PROFILE (perfil activo). Precedencia
# consistente en install, --check y --dry-run:
#     flag > env CDAD_MODEL_PROFILE > marker .cdad-models-profile > optimus
# El marker hace STATEFUL la instalación: el último perfil instalado persiste
# (un install sin flag ni env lo respeta); un install fresco sin marker usa
# optimus (diseño del repo). --check ya leía el marker; ahora install también.
resolve_profile() {
  if [ -n "$PROFILE_FLAG" ]; then
    MODEL_PROFILE="$PROFILE_FLAG"
  elif [ -n "${CDAD_MODEL_PROFILE:-}" ]; then
    MODEL_PROFILE="$CDAD_MODEL_PROFILE"
  elif [ -f "$PROFILE_MARKER" ]; then
    MODEL_PROFILE="$(cat "$PROFILE_MARKER")"
  else
    MODEL_PROFILE="optimus"
  fi
}

validate_profile() {  # aborta si el perfil activo no es soportado
  if ! cdad_valid_profile "$MODEL_PROFILE"; then
    die "Invalid model profile: '$MODEL_PROFILE' (esperado: economical | optimus | premium)"
  fi
}

# ---------------------------------------------------------------------------
# Install operations
# ---------------------------------------------------------------------------
sync_skill_to() {  # skill_name target_base_dir — mirrors the skill dir (never --delete)
  local skill="$1" base="$2"
  local src="$SOURCE_SKILLS_DIR/$skill"
  local dst="$base/$skill"
  ensure_dir "$base"
  if [ "$HAS_RSYNC" -eq 1 ]; then
    # NO --delete here, EVER: target dirs contain non-cdad content (8 skills in
    # config, memento in .agents, 7 non-cdad agents). A future "optimization"
    # that raises this flag's level deletes unmanaged data. Use --check (below)
    # for drift detection instead.
    do_run "COPY skills/$skill -> $dst" rsync -a "$src/" "$dst/"
  else
    log "WARN: rsync not found; using cp -rp (no --delete, no drift detection via rsync)"
    do_run "COPY skills/$skill -> $dst" cp -rp "$src/." "$dst/"
  fi
}

copy_agent_file() {  # filename — copies one cdad agent, applying the profile's model to the COPY
  local fname="$1"
  local src="$SOURCE_AGENTS_DIR/$fname"
  local dst="$OPENCODE_AGENTS_DIR/$fname"
  local role model
  role=${fname#cdad-}
  role=${role%.md}
  model=$(cdad_model "$MODEL_PROFILE" "$role")
  ensure_dir "$OPENCODE_AGENTS_DIR"
  do_run "COPY agents/$fname -> $dst" cp -p "$src" "$dst"
  if [ "$DRY_RUN" -eq 1 ]; then
    if [ -n "$model" ]; then
      log "DRY-RUN PROFILE $fname: model: $model (perfil $MODEL_PROFILE)"
    fi
    return 0
  fi
  # Perfil aplicado SOLO en la copia; el repo (diseño optimus) nunca cambia.
  # Si la copia ya tiene ese modelo (install idempotente), no se toca nada.
  if [ -n "$model" ] && [ -f "$dst" ] && ! grep -q "^model:[[:space:]]*$model" "$dst"; then
    log "PROFILE $fname: model: -> $model"
    sed -i "s|^model:.*|model: $model|" "$dst"
  fi
}

write_profile_marker() {  # persiste el perfil activo para --check y el validator
  ensure_dir "$OPENCODE_AGENTS_DIR"
  if [ "$DRY_RUN" -eq 1 ]; then
    log "DRY-RUN MARKER $PROFILE_MARKER = $MODEL_PROFILE"
  else
    printf '%s\n' "$MODEL_PROFILE" > "$PROFILE_MARKER"
    log "PROFILE marker: $PROFILE_MARKER = $MODEL_PROFILE"
  fi
}

install_skills() {
  local s
  for s in "${SKILLS[@]}"; do
    sync_skill_to "$s" "$OPENCODE_SKILLS_DIR"
    sync_skill_to "$s" "$AGENTS_SKILLS_DIR"
  done
}

# install_skills_extra — mirrors the skills into each CDAD_SKILL_EXTRA_DIRS
# target using the exact same sync_skill_to semantics (never --delete, honors
# --dry-run). No-op when the env var is unset.
install_skills_extra() {
  local d s
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    for s in "${SKILLS[@]}"; do
      sync_skill_to "$s" "$d"
    done
  done < <(extra_skills_dirs)
}

install_agents() {
  local f
  for f in "$SOURCE_AGENTS_DIR"/cdad-*.md; do
    [ -e "$f" ] || continue
    copy_agent_file "$(basename "$f")"
  done
}

install_guard_script() {
  local src="$SCRIPT_DIR/scripts/claude-code-path-guard.sh"
  local dst="$CLAUDE_CODE_SCRIPTS_DIR/path-guard.sh"
  if [ ! -f "$src" ]; then
    log "WARN: Guard script not found: $src (Claude Code agents may fail to enforce path-scoping)"
    return 0
  fi
  ensure_dir "$CLAUDE_CODE_SCRIPTS_DIR"
  do_run "COPY scripts/claude-code-path-guard.sh -> $dst" cp -p "$src" "$dst"
  if [ "$DRY_RUN" -eq 0 ] && [ -f "$dst" ]; then
    do_run "CHMOD +x $dst" chmod +x "$dst"
  fi
}

install_claude_code_agents() {
  local f src dst role model
  local cc_agents_subdir="$SOURCE_AGENTS_DIR/claude-code"
  if [ ! -d "$cc_agents_subdir" ]; then
    log "Claude Code agents subdirectory not found: $cc_agents_subdir (skipping)"
    return 0
  fi
  ensure_dir "$CLAUDE_CODE_AGENTS_DIR"
  for f in "$cc_agents_subdir"/cdad-*.md; do
    [ -e "$f" ] || continue
    src="$f"
    dst="$CLAUDE_CODE_AGENTS_DIR/$(basename "$f")"
    role=$(basename "$f")
    role=${role#cdad-}
    role=${role%.md}
    # Claude Code agents use cdad_model_claude (from extended cdad-models.sh)
    model=$(cdad_model_claude "$MODEL_PROFILE" "$role")
    do_run "COPY agents/claude-code/$(basename "$f") -> $dst" cp -p "$src" "$dst"
    if [ "$DRY_RUN" -eq 1 ]; then
      if [ -n "$model" ]; then
        log "DRY-RUN PROFILE $(basename "$f"): model: $model (perfil $MODEL_PROFILE)"
      fi
      continue
    fi
    # Apply profile's model to the copied agent (if the function exists and model is set)
    if [ -n "$model" ] && [ -f "$dst" ]; then
      # Only modify if model line is different (idempotent)
      if ! grep -q "^model:[[:space:]]*$model" "$dst"; then
        log "PROFILE $(basename "$f"): model: -> $model"
        sed -i "s|^model:.*|model: $model|" "$dst"
      fi
    fi
  done
}

install_claude_code_skills() {
  local s
  for s in "${SKILLS[@]}"; do
    sync_skill_to "$s" "$CLAUDE_CODE_SKILLS_DIR"
  done
}

# ---------------------------------------------------------------------------
# Uninstall operations (cdad-owned paths only)
# ---------------------------------------------------------------------------
# uninstall_items — prints the paths uninstall would remove. Agents come from
# the SOURCE repo manifest (never a target-dir glob: a user-created cdad-*.md
# that was never in the repo must survive). Skills come from the hardcoded
# SKILLS array (same-input-same-output: uninstall removes what install installs).
uninstall_items() {
  local f base
  for f in "$SOURCE_AGENTS_DIR"/cdad-*.md; do
    [ -e "$f" ] || continue
    base=$(basename "$f")
    printf '%s\n' "$OPENCODE_AGENTS_DIR/$base"
  done
  local s d
  for s in "${SKILLS[@]}"; do
    printf '%s\n' "$OPENCODE_SKILLS_DIR/$s"
    printf '%s\n' "$AGENTS_SKILLS_DIR/$s"
  done
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    for s in "${SKILLS[@]}"; do
      printf '%s\n' "$d/$s"
    done
  done < <(extra_skills_dirs)
}

confirm_uninstall() {  # lists the exact removals and asks y/N; 0 = proceed, 1 = abort
  local item
  local -a items=()
  while IFS= read -r item; do
    items+=("$item")
  done < <(uninstall_items)
  printf 'Will remove %d item(s):\n' "${#items[@]}"
  for item in "${items[@]}"; do
    printf '  %s\n' "$item"
  done
  printf 'Remove these %d items? [y/N] ' "${#items[@]}"
  local ans
  if ! read -r ans; then
    printf '\n'   # EOF (e.g. piped stdin) counts as "no"
    return 1
  fi
  case "$ans" in
    y|Y) return 0 ;;
    *)   return 1 ;;
  esac
}

uninstall_cdad() {
  log "Uninstalling cdad artifacts (non-cdad files are never touched)"
  # OpenCode agents
  if [ -d "$OPENCODE_AGENTS_DIR" ]; then
    local f base
    for f in "$SOURCE_AGENTS_DIR"/cdad-*.md; do
      [ -e "$f" ] || continue
      base=$(basename "$f")
      do_run "UNINSTALL $OPENCODE_AGENTS_DIR/$base" rm -f -- "$OPENCODE_AGENTS_DIR/$base"
    done
    do_run "UNINSTALL $PROFILE_MARKER" rm -f -- "$PROFILE_MARKER"
  fi
  # Claude Code agents
  if [ -d "$CLAUDE_CODE_AGENTS_DIR" ]; then
    local f base
    for f in "$SOURCE_AGENTS_DIR"/claude-code/cdad-*.md; do
      [ -e "$f" ] || continue
      base=$(basename "$f")
      do_run "UNINSTALL $CLAUDE_CODE_AGENTS_DIR/$base" rm -f -- "$CLAUDE_CODE_AGENTS_DIR/$base"
    done
  fi
  # Guard script
  do_run "UNINSTALL $CLAUDE_CODE_SCRIPTS_DIR/path-guard.sh" rm -f -- "$CLAUDE_CODE_SCRIPTS_DIR/path-guard.sh"
  # Skills (both runtimes)
  local s d
  for s in "${SKILLS[@]}"; do
    do_run "UNINSTALL skills/$s -> $OPENCODE_SKILLS_DIR/$s" rm -rf -- "$OPENCODE_SKILLS_DIR/$s"
    do_run "UNINSTALL skills/$s -> $AGENTS_SKILLS_DIR/$s" rm -rf -- "$AGENTS_SKILLS_DIR/$s"
    do_run "UNINSTALL skills/$s -> $CLAUDE_CODE_SKILLS_DIR/$s" rm -rf -- "$CLAUDE_CODE_SKILLS_DIR/$s"
  done
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    for s in "${SKILLS[@]}"; do
      do_run "UNINSTALL skills/$s -> $d/$s" rm -rf -- "$d/$s"
    done
  done < <(extra_skills_dirs)
}

# ---------------------------------------------------------------------------
# Verification & summary
# ---------------------------------------------------------------------------
check_agent_file() {  # src dst role expected — profile-aware compare; 0 = identical
  local src="$1" dst="$2" role="$3" expected="$4"
  if [ ! -f "$dst" ]; then
    printf 'DRIFT: missing %s\n' "$dst"
    return 1
  fi
  # Byte-compare del contenido SIN la línea model: — el deploy puede desviarse
  # del repo SOLO en esa línea (perfil aplicado en la copia).
  if ! cmp -s <(grep -v '^model:' "$src") <(grep -v '^model:' "$dst"); then
    printf 'DRIFT: differs %s\n' "$dst"
    return 1
  fi
  # La línea model: del runtime debe ser EXACTA al modelo del perfil activo.
  local actual
  actual="$(sed -n 's/^model:[[:space:]]*//p' "$dst" | head -1)"
  if [ -z "$expected" ]; then
    if [ -n "$actual" ]; then
      printf '❌ %s: declara model: %s pero el rol %s no lleva modelo en el perfil %s\n' "$dst" "$actual" "$role" "$MODEL_PROFILE"
      return 1
    fi
  elif [ "$actual" != "$expected" ]; then
    printf '❌ %s: model esperado (perfil %s) = %s, encontrado: %s\n' "$dst" "$MODEL_PROFILE" "$expected" "${actual:-<ninguno>}"
    return 1
  fi
  printf 'OK: %s\n' "$dst"
  return 0
}

check_skill_tree() {  # src_dir dst_dir — cmps every source file vs dst; 0 = identical
  local src_dir="$1" dst_dir="$2"
  local src_count dst_count
  local drift=0
  local src_file rel dst_file
  src_count=$(count_tree_files "$src_dir")
  if [ ! -d "$dst_dir" ]; then
    printf 'DRIFT: missing dir %s\n' "$dst_dir"
    return 1
  fi
  dst_count=$(count_tree_files "$dst_dir")
  if [ "$src_count" -ne "$dst_count" ]; then
    printf 'DRIFT: %s has %s file(s), installed has %s\n' "$src_dir" "$src_count" "$dst_count"
    drift=1
  fi
  while IFS= read -r -d '' src_file; do
    rel=${src_file#"$src_dir"/}
    dst_file="$dst_dir/$rel"
    if [ ! -f "$dst_file" ]; then
      printf 'DRIFT: missing %s\n' "$dst_file"
      drift=1
    elif ! cmp -s "$src_file" "$dst_file"; then
      printf 'DRIFT: differs %s\n' "$dst_file"
      drift=1
    fi
  done < <(find "$src_dir" -type f -print0)
  return "$drift"
}

check_installed() {  # exit 0 if all installed artifacts match the repo (agents profile-aware), 1 on drift
  local f base s role want_model
  local total=0 expected_total=0 drifted=0
  local extra_total=0 extra_expected=0
  local -a drifted_paths=()
  expected_total=$(( $(count_flat_files "$SOURCE_AGENTS_DIR" 'cdad-*.md') + ${#SKILLS[@]} * 2 ))
  for f in "$SOURCE_AGENTS_DIR"/cdad-*.md; do
    [ -e "$f" ] || continue
    total=$((total + 1))
    base=$(basename "$f")
    role=${base#cdad-}
    role=${role%.md}
    want_model=$(cdad_model "$MODEL_PROFILE" "$role")
    if ! check_agent_file "$f" "$OPENCODE_AGENTS_DIR/$base" "$role" "$want_model"; then
      drifted_paths+=("$OPENCODE_AGENTS_DIR/$base")
      drifted=1
    fi
  done
  for s in "${SKILLS[@]}"; do
    if check_skill_tree "$SOURCE_SKILLS_DIR/$s" "$OPENCODE_SKILLS_DIR/$s"; then
      total=$((total + 1))
    else
      drifted_paths+=("$OPENCODE_SKILLS_DIR/$s")
      drifted=1
    fi
    if check_skill_tree "$SOURCE_SKILLS_DIR/$s" "$AGENTS_SKILLS_DIR/$s"; then
      total=$((total + 1))
    else
      drifted_paths+=("$AGENTS_SKILLS_DIR/$s")
      drifted=1
    fi
  done
  # Extra skill target dirs: validated ONLY when CDAD_SKILL_EXTRA_DIRS is set.
  # When unset, extra_skills_dirs emits nothing and the default behavior (and
  # its PASS message) stays byte-identical.
  local d
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    extra_expected=$((extra_expected + ${#SKILLS[@]}))
    for s in "${SKILLS[@]}"; do
      if check_skill_tree "$SOURCE_SKILLS_DIR/$s" "$d/$s"; then
        extra_total=$((extra_total + 1))
      else
        drifted_paths+=("$d/$s")
        drifted=1
      fi
    done
  done < <(extra_skills_dirs)
  if [ "$drifted" -eq 0 ]; then
    if [ "$extra_expected" -gt 0 ]; then
      log "Check: PASS ($total/$expected_total in sync + $extra_total/$extra_expected extra dirs, perfil $MODEL_PROFILE)"
    else
      log "Check: PASS ($total/$expected_total in sync, perfil $MODEL_PROFILE)"
    fi
    return 0
  fi
  log "Check: FAIL — ${drifted_paths[*]} (perfil $MODEL_PROFILE)"
  return 1
}

print_summary() {  # mode: install | uninstall
  local mode="$1"
  local cdad_agents non_cdad total
  cdad_agents=$(count_manifest_agents_installed "$OPENCODE_AGENTS_DIR")
  total=$(count_flat_files "$OPENCODE_AGENTS_DIR" '*.md')
  non_cdad=$((total - cdad_agents))
  log "=== Summary ($mode) ==="
  log "Agents: $cdad_agents of $EXPECTED_CDAD_AGENTS repo cdad-*.md present in $OPENCODE_AGENTS_DIR"
  log "Agents dir: $non_cdad unmanaged .md files present (untouched)"
  local s d
  for s in "${SKILLS[@]}"; do
    log "  $s: $(count_tree_files "$OPENCODE_SKILLS_DIR/$s") files @ config, $(count_tree_files "$AGENTS_SKILLS_DIR/$s") files @ agents"
  done
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    for s in "${SKILLS[@]}"; do
      log "  $s: $(count_tree_files "$d/$s") files @ extra: $d"
    done
  done < <(extra_skills_dirs)
  if [ "$mode" = "install" ] && [ "$DRY_RUN" -eq 0 ] && [ "$cdad_agents" -ne "$EXPECTED_CDAD_AGENTS" ]; then
    log "Verify: FAIL — expected $EXPECTED_CDAD_AGENTS cdad agents, found $cdad_agents"
    return 1
  fi
  if [ "$mode" = "install" ]; then
    log "Verify: PASS — $cdad_agents cdad agents present after install"
  fi
}

print_dry_run_summary() {
  if [ "$UNINSTALL" -eq 1 ]; then
    local extra_count=0 d
    while IFS= read -r d; do
      [ -n "$d" ] || continue
      extra_count=$((extra_count + 1))
    done < <(extra_skills_dirs)
    log "=== Summary (dry-run uninstall) ==="
    log "Would remove $(count_flat_files "$SOURCE_AGENTS_DIR" 'cdad-*.md') cdad agents + ${#SKILLS[@]} skills x 2 runtimes + ${#SKILLS[@]} x $extra_count extra dir(s) (see DRY-RUN lines above)"
    return 0
  fi
  local src_agents cur_agents
  src_agents=$(count_flat_files "$SOURCE_AGENTS_DIR" 'cdad-*.md')
  cur_agents=$(count_flat_files "$OPENCODE_AGENTS_DIR" 'cdad-*.md')
  log "=== Summary (dry-run) ==="
  log "Perfil de modelos: $MODEL_PROFILE"
  local f base role m
  for f in "$SOURCE_AGENTS_DIR"/cdad-*.md; do
    [ -e "$f" ] || continue
    base=$(basename "$f")
    role=${base#cdad-}
    role=${role%.md}
    m=$(cdad_model "$MODEL_PROFILE" "$role")
    if [ -n "$m" ]; then
      log "  $base -> model: $m"
    else
      log "  $base -> (sin model:)"
    fi
  done
  log "Would install: ${#SKILLS[@]} skills x 2 runtimes + $src_agents cdad agents"
  log "Agents dir currently has $cur_agents cdad-*.md; would copy $src_agents from source"
  local s
  for s in "${SKILLS[@]}"; do
    log "  $s: source has $(count_tree_files "$SOURCE_SKILLS_DIR/$s") files; would mirror to both runtimes"
  done
  local d
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    log "  + extra dir $d: would install ${#SKILLS[@]} skills"
  done < <(extra_skills_dirs)
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  parse_options "$@"
  guard_home

  if [ "$CHECK" -eq 1 ]; then
    guard_sources
    resolve_profile
    validate_profile
    if check_installed; then
      return 0
    fi
    return 1
  fi

  if [ "$UNINSTALL" -eq 1 ]; then
    if [ ! -d "$SOURCE_AGENTS_DIR" ]; then
      die "Cannot uninstall: source agent manifest missing ($SOURCE_AGENTS_DIR)"
    fi
    if [ "$DRY_RUN" -eq 0 ] && [ "$FORCE" -eq 0 ]; then
      if ! confirm_uninstall; then
        log "Aborted."
        return 0
      fi
    fi
    uninstall_cdad
    if [ "$DRY_RUN" -eq 1 ]; then
      print_dry_run_summary
    else
      print_summary uninstall
    fi
    return 0
  fi

  guard_sources
  resolve_profile
  validate_profile
  install_skills
  install_skills_extra
  install_agents
  # Claude Code targets (new in ADR-008)
  install_guard_script
  install_claude_code_agents
  install_claude_code_skills
  write_profile_marker
  if [ "$DRY_RUN" -eq 1 ]; then
    print_dry_run_summary
  else
    print_summary install
  fi
}

main "$@"
