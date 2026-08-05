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

SKILLS=(cdad-cycle cdad-epic cdad-spec-and-test)
EXPECTED_CDAD_AGENTS=6

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
DRY_RUN=0
FORCE=0
UNINSTALL=0
CHECK=0

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
               --status is an alias.
  --help       Show this help and exit.

No flags = install (safe default).

What gets installed:
  skills/cdad-{cycle,epic,spec-and-test}/
      -> ~/.config/opencode/skills/<skill>/   (rsync -a, NEVER --delete; or cp -rp)
      -> ~/.agents/skills/<skill>/            (rsync -a, NEVER --delete; or cp -rp)
  agents/cdad-*.md
      -> ~/.config/opencode/agents/           (cp -p, NEVER --delete)

Note: the 4 loose top-level skills/*.md files (re-entry.md, feature-handoff.md,
handoff-prompts.md, epic-planning.md) are reference docs, not valid skill dirs
(bare .md != skill dir), and are intentionally NOT installed.

Never touched: non-cdad agents in ~/.config/opencode/agents,
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
      --help)      normalized+=(-h) ;;
      --*)         die "Unknown option: $arg (see --help)" ;;
      *)           normalized+=("$arg") ;;
    esac
  done
  set -- "${normalized[@]}"

  local opt
  while getopts "dfuch" opt; do
    case "$opt" in
      d) DRY_RUN=1 ;;
      f) FORCE=1 ;;
      u) UNINSTALL=1 ;;
      c) CHECK=1 ;;
      h) usage; exit 0 ;;
      *) usage; exit 1 ;;
    esac
  done
  shift $((OPTIND - 1))
  if [ $# -gt 0 ]; then
    die "Unexpected arguments: $* (see --help)"
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

copy_agent_file() {  # filename — copies one cdad agent into the agents dir
  local fname="$1"
  local src="$SOURCE_AGENTS_DIR/$fname"
  local dst="$OPENCODE_AGENTS_DIR/$fname"
  ensure_dir "$OPENCODE_AGENTS_DIR"
  do_run "COPY agents/$fname -> $dst" cp -p "$src" "$dst"
}

install_skills() {
  local s
  for s in "${SKILLS[@]}"; do
    sync_skill_to "$s" "$OPENCODE_SKILLS_DIR"
    sync_skill_to "$s" "$AGENTS_SKILLS_DIR"
  done
}

install_agents() {
  local f
  for f in "$SOURCE_AGENTS_DIR"/cdad-*.md; do
    [ -e "$f" ] || continue
    copy_agent_file "$(basename "$f")"
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
  local s
  for s in "${SKILLS[@]}"; do
    printf '%s\n' "$OPENCODE_SKILLS_DIR/$s"
    printf '%s\n' "$AGENTS_SKILLS_DIR/$s"
  done
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
  if [ -d "$OPENCODE_AGENTS_DIR" ]; then
    local f base
    for f in "$SOURCE_AGENTS_DIR"/cdad-*.md; do
      [ -e "$f" ] || continue
      base=$(basename "$f")
      do_run "UNINSTALL $OPENCODE_AGENTS_DIR/$base" rm -f -- "$OPENCODE_AGENTS_DIR/$base"
    done
  fi
  local s
  for s in "${SKILLS[@]}"; do
    do_run "UNINSTALL skills/$s -> $OPENCODE_SKILLS_DIR/$s" rm -rf -- "$OPENCODE_SKILLS_DIR/$s"
    do_run "UNINSTALL skills/$s -> $AGENTS_SKILLS_DIR/$s" rm -rf -- "$AGENTS_SKILLS_DIR/$s"
  done
}

# ---------------------------------------------------------------------------
# Verification & summary
# ---------------------------------------------------------------------------
check_one_file() {  # src dst — prints DRIFT if missing/different; 0 = identical
  local src="$1" dst="$2"
  if [ ! -f "$dst" ]; then
    printf 'DRIFT: missing %s\n' "$dst"
    return 1
  fi
  if ! cmp -s "$src" "$dst"; then
    printf 'DRIFT: differs %s\n' "$dst"
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

check_installed() {  # exit 0 if all installed artifacts match the repo, 1 on drift
  local f base s
  local total=0 expected=0 drifted=0
  local -a drifted_paths=()
  expected=$(( $(count_flat_files "$SOURCE_AGENTS_DIR" 'cdad-*.md') + ${#SKILLS[@]} * 2 ))
  for f in "$SOURCE_AGENTS_DIR"/cdad-*.md; do
    [ -e "$f" ] || continue
    total=$((total + 1))
    base=$(basename "$f")
    if ! check_one_file "$f" "$OPENCODE_AGENTS_DIR/$base"; then
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
  if [ "$drifted" -eq 0 ]; then
    log "Check: PASS ($total/$expected in sync)"
    return 0
  fi
  log "Check: FAIL — ${drifted_paths[*]}"
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
  local s
  for s in "${SKILLS[@]}"; do
    log "  $s: $(count_tree_files "$OPENCODE_SKILLS_DIR/$s") files @ config, $(count_tree_files "$AGENTS_SKILLS_DIR/$s") files @ agents"
  done
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
    log "=== Summary (dry-run uninstall) ==="
    log "Would remove $(count_flat_files "$SOURCE_AGENTS_DIR" 'cdad-*.md') cdad agents + ${#SKILLS[@]} skills x 2 runtimes (see DRY-RUN lines above)"
    return 0
  fi
  local src_agents cur_agents
  src_agents=$(count_flat_files "$SOURCE_AGENTS_DIR" 'cdad-*.md')
  cur_agents=$(count_flat_files "$OPENCODE_AGENTS_DIR" 'cdad-*.md')
  log "=== Summary (dry-run) ==="
  log "Would install: ${#SKILLS[@]} skills x 2 runtimes + $src_agents cdad agents"
  log "Agents dir currently has $cur_agents cdad-*.md; would copy $src_agents from source"
  local s
  for s in "${SKILLS[@]}"; do
    log "  $s: source has $(count_tree_files "$SOURCE_SKILLS_DIR/$s") files; would mirror to both runtimes"
  done
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  parse_options "$@"
  guard_home

  if [ "$CHECK" -eq 1 ]; then
    guard_sources
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
  install_skills
  install_agents
  if [ "$DRY_RUN" -eq 1 ]; then
    print_dry_run_summary
  else
    print_summary install
  fi
}

main "$@"
