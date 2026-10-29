#!/usr/bin/env bash
# install.sh — CDAD skills & agents installer
#
# Deploys the CDAD skills and the STAGED agent set into the REAL runtime
# directories (~/.config/opencode, ~/.agents, ~/.claude) under an explicit
# install root. Since 004-001 T6 (PD-9) the public layout (<root>/agents and
# <root>/skills) is NO LONGER an install destination: installs land only at
# real runtime destinations. Since 004-001 T5 the AGENTS come exclusively from
# the staging tree declared by build/staging/manifest.json (PD-18: the
# installer never reads sources/; generation-time stack resolution is
# recorded in the staging manifest). Copies are independent (per-file owned
# cp -p), never symlinks. Only cdad-owned paths are touched; the 7 non-cdad
# agents and ~/.agents/.skill-lock.json are left alone. The 4 loose top-level
# skills/*.md files (re-entry.md, feature-handoff.md, handoff-prompts.md,
# epic-planning.md) are reference docs, NOT valid runtime skill dirs (bare
# .md != skill dir), and are intentionally never installed.
# When CDAD_SKILL_EXTRA_DIRS is set (colon-separated), the 3 skills are also
# installed into each extra dir (e.g. the OpenClaw skills dir).
#
# Ownership (D4, 004-001 T5): every successful install publishes the ownership
# manifest <install root>/.cdad-install-manifest.json — runtime/stack resolved
# by staging (R3-O2) plus per-file sha256+source provenance for
# everything the installer deployed. Installs report conflicts (a locally
# modified owned file — agents, skills and the guard share the SAME
# conflict-and-preserve policy, review-5 B2 — or a symlink at a destination)
# and preserve the local bytes; files owned by a previous install that this
# install no longer deploys are RETIRED when their bytes still match the
# recorded sha256 (006-003 U7/D6: the install retires its own obsoletes) and
# stay registered as pending_removal when they were modified locally — or when
# their record carries no digest to compare against (B-1: with no digest there
# is no proof the bytes are still ours) — visible to --check, retired by
# --uninstall; review-5 B3 — a reinstall never forgets.
# This is how a pre-T6 root's public-layout copies surface after a PD-9
# reinstall: pending_removal, retired by --uninstall. --uninstall removes
# exactly the manifest entries (artifacts + pending records), preserving a
# locally modified file for explicit resolution.

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Canonical (pwd -P): guard_source_overlap compares against this path; a logical
# path would let a symlinked repo invocation target the source tree (B4).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SOURCE_SKILLS_DIR="$SCRIPT_DIR/skills"
SOURCE_AGENTS_DIR="$SCRIPT_DIR/agents"

INSTALL_ROOT="${CDAD_INSTALL_ROOT:-${HOME:-}}"

OPENCODE_AGENTS_DIR="$INSTALL_ROOT/.config/opencode/agents"
OPENCODE_SKILLS_DIR="$INSTALL_ROOT/.config/opencode/skills"
AGENTS_SKILLS_DIR="$INSTALL_ROOT/.agents/skills"

CLAUDE_CODE_AGENTS_DIR="$INSTALL_ROOT/.claude/agents"
CLAUDE_CODE_SKILLS_DIR="$INSTALL_ROOT/.claude/skills"
CLAUDE_CODE_SCRIPTS_DIR="$INSTALL_ROOT/.claude/cdad-scripts"
# PD-9 (004-001 T6): the public layout (<root>/agents, <root>/skills) is NOT
# an install destination. The two vars below are LEGACY-REMOVAL ONLY: they
# keep pre-T6 roots uninstallable (--uninstall / uninstall_items) and let the
# legacy --check path (check_installed, manifest-less roots) report their
# historical copies. Nothing in the install path deploys there anymore.
PUBLIC_AGENTS_DIR="$INSTALL_ROOT/agents"
PUBLIC_SKILLS_DIR="$INSTALL_ROOT/skills"

SKILLS=(cdad-cycle cdad-epic cdad-spec-and-test odoo-architect odoo-test-writer odoo-reviewer odoo-make-env odoo-expert)
# EXPECTED_CDAD_AGENTS* are the FALLBACK totals of the post-install Verify, used
# only when the staged set cannot be read (plan amendment A-6: the expected count
# now comes FROM the staging manifest, per runtime — `staged_agent_count`). Kept
# as the declared last resort so a manifest-less root (legacy --uninstall path)
# keeps its historical summary instead of printing an empty expectation.
# EXPECTED_CDAD_AGENTS counts OpenCode agents. Base = 6 generic (architect,
# implementer, orchestrator, reviewer, scribe, test-writer) + 5 Odoo variants
# (agents/cdad-*-odoo.md: architect/test-writer/implementer/reviewer/scribe).
# The cdad-.*-odoo variants are captured by the same cdad-*.md glob in
# install_agents() (now the staged set from build/staging) and fix NO model per
# role (006-003 D1/INV-3: no installable surface pins a model).
EXPECTED_CDAD_AGENTS=11
# NOTE: EXPECTED_CDAD_AGENTS counts OpenCode agents. Claude Code agents are
# staged under agents/claude-code/ and deployed to .claude/agents by the same
# staging-driven pass. EXPECTED_CDAD_AGENTS_CLAUDE_CODE=11 is their fallback count.
EXPECTED_CDAD_AGENTS_CLAUDE_CODE=11

# Extra skill target dirs (colon-separated) via CDAD_SKILL_EXTRA_DIRS, e.g. the
# OpenClaw skills dir. Empty by default: only the default runtimes are used.
# Not hardcoded here: this repo is public, each deployer sets their own value.
EXTRA_SKILLS_DIRS="${CDAD_SKILL_EXTRA_DIRS:-}"

# ---------------------------------------------------------------------------
# Staging (004-001 T5/PD-18): the ONLY input for agent deployment
# ---------------------------------------------------------------------------
# The installer deploys the agents declared by build/staging/manifest.json
# (produced by scripts/cdad-generate.py via `make staging`) and the STAGED
# bytes, never the canonical sources (sources/ is unread to this installer by
# contract). The staging manifest also records the resolved runtime/stack —
# published verbatim in the ownership manifest (R3-O2: the stack is an explicit
# recorded input, not a hidden effect of the machine).
STAGING_DIR="$SCRIPT_DIR/build/staging"
STAGING_MANIFEST="$STAGING_DIR/manifest.json"
INSTALL_MANIFEST_NAME=".cdad-install-manifest.json"

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
DRY_RUN=0
FORCE=0
UNINSTALL=0
CHECK=0
OWNERSHIP_MANIFEST="$INSTALL_ROOT/$INSTALL_MANIFEST_NAME"
# Owned files recorded during THIS install: "rel<TAB>sha256<TAB>source".
OWNED=()
# Conflicts detected during THIS run: "rel<TAB>reason".
CONFLICTS=()
# 006-003 U7/D6: the obsolete prune needs to know which DESTINATIONS this run
# deploys (in BOTH modes: --dry-run must preview the same bajas) and which ones
# it already disclosed as conflicts. Keyed by absolute path, so a manifest that
# recorded absolute paths and one that recorded install-root-relative paths
# describe the SAME destination.
declare -A OWNED_ABS=()
declare -A CONFLICT_ABS=()
# Obsolete-retirement plan of this run (PD-6a/D6): keys retired from disk and
# from the manifest, and entries preserved (locally modified) that must stay
# REGISTERED. Consumed by write_ownership_manifest; "" until the prune runs.
PRUNED=()
KEPT=()
PRUNE_PLAN_FILE=""
# PD-14/INV-7: deterministic identifier of what this install deployed, resolved
# once per run (installation_version) and published at the install root.
INSTALL_VERSION=""

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
# Bash allowlists — RETIRED in 009-002 (PC-7), documentation anchor
# ---------------------------------------------------------------------------
# The OpenCode frontmatter is V2 (`permissions:` list of {action, resource,
# effect}), so the `  bash:` sub-map the derivation used to substitute no
# longer exists in any emitted form; and since 004-001 T5 the policy is
# derived at GENERATION time (scripts/cdad-generate.py, PD-1) and the installer
# deploys the staged bytes as-is. Keeping a second, check-time derivation would
# be the duplicated mechanism the epic forbids (criterio 4) and would compare
# against a shape nobody emits (PC-7). `--check` compares the repo artifacts as
# they are, with the ONE overlay semantics (scripts/agent-overlay.py, 009-001).
# Evidence: tests/test_009_002_opencode_v2_frontmatter.py (PC-1..PC-7).
# scripts/cdad-bash-allowlist.sh stays as the standalone emitter of the
# derived policy (rule lines), consumed by its own test; it no longer feeds the
# installer.

# 009-001: the user-owned overlay helper. The frontmatter keys the USER owns
# (today `model:` — the list is DATA inside the helper) are the user's
# configuration, not local drift: an install brings the rest of the agent from
# staging and reinserts them. This is the ONE definition of that semantics —
# install, --check (both paths) and scripts/validate-subagents.sh consume it,
# and no bash filter redefines "overlay" (009-001 INV-2).
AGENT_OVERLAY_PY="$SCRIPT_DIR/scripts/agent-overlay.py"

# rewrite_bash_section — RETIRED in 004-001 T5: the bash policy is derived at
# GENERATION time (scripts/cdad-generate.py, PD-1) and the installer deploys
# the staged bytes as-is.

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

count_manifest_agents_installed() {  # dir -> how many declared agent names are present there
  # The STAGED set is the declared single deployment input (PD-18) and the same
  # basis plan amendment A-6 uses for the expected total, so both sides of the
  # "N of N" presence check agree by construction: a staging-only fixture agent
  # counts on both sides and a retired staged agent disappears from both. The
  # repo agents/ directory is only the LEGACY fallback for a root with no
  # staging manifest (pre-T5 install, legacy --uninstall summary).
  local dir="$1"
  local f base name count=0
  if [ ! -d "$dir" ]; then
    printf '0'
    return 0
  fi
  if [ -f "$STAGING_MANIFEST" ]; then
    while IFS= read -r name; do
      [ -n "$name" ] || continue
      if [ -f "$dir/$name" ]; then
        count=$((count + 1))
      fi
    done < <(staged_agent_names opencode)
    printf '%s' "$count"
    return 0
  fi
  if [ -d "$SOURCE_AGENTS_DIR" ]; then
    for f in "$SOURCE_AGENTS_DIR"/cdad-*.md; do
      [ -e "$f" ] || continue
      base=$(basename "$f")
      if [ -f "$dir/$base" ]; then
        count=$((count + 1))
      fi
    done
    printf '%s' "$count"
    return 0
  fi
  printf '0'
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

CDAD installer — deploys the CDAD skills and the STAGED agent set
(build/staging/manifest.json, produced by `make staging`) into the runtime
directories (~/.config/opencode, ~/.agents, ~/.claude and the public layout).
The agent artifacts come EXCLUSIVELY from staging (PD-18: sources/ is never
read); the deployed bytes are the staged bytes, which carry the generation-time
stack and derived bash policy (no installable surface pins a model: 006-003
D1/INV-3). Every successful install publishes the
ownership manifest <install root>/.cdad-install-manifest.json (runtime/stack
resolved by staging + per-file sha256/source provenance).

The packet renderer requires Python 3 and uses only the Python standard
library (stdlib); the installer never downloads Python dependencies.

Options:
  --dry-run    Show what would be done without changing anything (the staged
               set is announced exactly; conflicts are previewed).
  --force      Skip confirmation prompts (matters for the legacy --uninstall,
               which without it asks for confirmation first).
  --uninstall  Remove ONLY the entries recorded in the ownership manifest
               (foreign files survive; idempotent). Without an ownership
               manifest it falls back to the legacy cdad-manifest removal and
               asks for confirmation unless --force is given.
  --check      Verify an owned install against STAGING (exit 1 on drift):
               installed bytes vs current staged bytes, obsolete staged
               sources (renamed/removed upstream), staged artifacts not yet
               installed, and the installed skill trees vs the repo.
               --status is an alias. Without an ownership manifest it falls
               back to the legacy repo comparison (repo artifacts as emitted,
               compared with the user-owned overlay semantics).
  --basic      DEPRECATED, no effect (006-003 D1): accepted only so the
               existing recipes keep working; it resolves no profile and
               writes no marker. The installer has no profiles: the model is
               chosen in the delegation config (delegation.json), never by an
               installer flag.
  --help       Show this help and exit.

Exit codes: rc=1 from install/--uninstall/--check means PENDING work —
 conflicts preserved on re-install (CONFLICT ... PRESERVED), staged
 removals not yet retired (PENDING-REMOVAL), or drift (DRIFT) — NOT a
 broken install: the rest is deployed and coherent; resolve the reported
 conflicts first.

No flags = install (safe default). The model is NOT an installer concern: no
installable surface pins a model, so no flag, env or marker selects one. The
model of the external delegation is read from the delegation config
(delegation.json) by the delegation layer.

Environment:
  CDAD_MODEL_PROFILE  DEPRECATED and ignored (006-003 A-1): accepted only so
               local recipes keep working; it resolves no profile and writes
               no marker (the model lives in the delegation config).
  CDAD_SKILL_EXTRA_DIRS  colon-separated list of ADDITIONAL directories where
               the 3 cdad skills are also installed (e.g. the OpenClaw skills
               dir). Empty by default: only the default runtimes are used.
               Applied to install, --check, --uninstall and --dry-run.
  CDAD_INSTALL_ROOT  absolute, existing root that replaces the usual HOME
               prefix for every managed runtime destination. HOME itself is
               left unchanged. Applied to install, --check, --uninstall and
               --dry-run.

What gets installed (from build/staging — the single agent input, PD-18):
  build/staging/agents/opencode/cdad-*.md
      -> ~/.config/opencode/agents/           (cp -p of the STAGED bytes)
  build/staging/agents/claude-code/cdad-*.md
      -> ~/.claude/agents/                    (cp -p of the STAGED bytes)
      The staged bytes already carry the generation-time bash: policy (no
      `model:` line) — the installer transforms nothing.
  skills/cdad-{cycle,epic,spec-and-test}/ + skills/odoo-*/
      -> ~/.config/opencode/skills/<skill>/   (per-file owned copy, NEVER --delete)
      -> ~/.agents/skills/<skill>/            (per-file owned copy, NEVER --delete)
      -> ~/.claude/skills/<skill>/            (per-file owned copy) [Claude Code]
      -> <dir>/<skill>/ for each dir in $CDAD_SKILL_EXTRA_DIRS when set
                                           (per-file owned copy, NEVER --delete)
      The cdad-cycle tree travels complete (packets, references and
      scripts/cdad_packet.py): an isolated consumer runs the CLI and the CC
      guard resolves it installed, without the checkout (PD-12).
  scripts/claude-code-path-guard.sh
      -> ~/.claude/cdad-scripts/path-guard.sh (cp -p, chmod +x)
  Ownership manifest:
      <install root>/.cdad-install-manifest.json
      (runtime/stack resolved by staging — R3-O2 — plus per-file
       sha256 + source provenance of everything deployed; conflicts listed
       separately until explicitly resolved)

User-owned overlay (009-001) — your configuration survives every install:
  The frontmatter keys the USER owns in an installed agent are data, declared
  once in scripts/agent-overlay.py (USER_OWNED_KEYS: today only `model`). You
  may set them in the installed copy, e.g. `model: your/model-id`; install,
  `--check` and scripts/validate-subagents.sh all read that one definition.
    - install / reinstall: the value is preserved verbatim and everything else
      comes from the current staging bytes, so updates do arrive. The agent
      stays owned: the next run reports SYNC and `--check` passes.
    - `--check` names the installed agent and the overlay it keeps.
    - `--uninstall` keeps an agent that carries your overlay byte for byte:
      it is your configuration, not the installer's to delete.
    - Anything else you change, and any ambiguous overlay (no frontmatter, a
      duplicated key, an empty value, a key in the body), is a CONFLICT:
      preserved untouched, reported, and never adopted as owned.
  There is no flag: preserving your configuration is the behaviour, never an
  option. The product keeps pinning no model anywhere installable — the
  validator fails if agents/ or build/staging declares `model:`.

PD-9 (004-001 T6): the public layout (<root>/agents and <root>/skills) is NOT
installed anymore — only real runtime destinations. A root that still carries
the pre-T6 public copies sees them reported as pending_removal by --check and
freed by --uninstall.

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
# warn_basic_deprecated — D1 (006-003): `--basic` is accepted only as a
# DEPRECATED, EFFECT-FREE alias (>=6 test recipes pass it). The notice is ONE
# line; nothing about a profile is resolved or persisted (INV-7: nothing
# silent).
warn_basic_deprecated() {
  log "DEPRECATED: --basic is obsolete and has no effect (006-003 D1) — the installer has no profiles; the model is chosen in the delegation config (delegation.json)"
}

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
      --basic)     normalized+=(-b) ;;
      --help)      normalized+=(-h) ;;
      --*)
        # 006-003 D1/PD-1a: the installer has no profiles. A retired profile
        # flag (and any other unknown option) is refused HERE, before anything
        # is deployed, with a diagnostic pointing at the delegation config — the
        # single place where the model is chosen. The retired spellings are
        # deliberately NOT listed: the source names none of them (PD-1a).
        die "Unknown option: $arg — the installer has no profiles; the model is chosen in the delegation config (delegation.json), not by an installer flag (see --help)"
        ;;
      *)           normalized+=("$arg") ;;
    esac
  done
  set -- "${normalized[@]}"

  local opt
  while getopts "dfucbh" opt; do
    case "$opt" in
      d) DRY_RUN=1 ;;
      f) FORCE=1 ;;
      u) UNINSTALL=1 ;;
      c) CHECK=1 ;;
      b) warn_basic_deprecated ;;
      h) usage; exit 0 ;;
      *) usage; exit 1 ;;
    esac
  done
  shift $((OPTIND - 1))
  if [ $# -gt 0 ]; then
    die "Unexpected arguments: $* (see --help)"
  fi
  # A-1 (006-003): CDAD_MODEL_PROFILE is accepted and IGNORED with the same
  # one-line deprecation notice as `--basic` (INV-7: nothing silent).
  if [ -n "${CDAD_MODEL_PROFILE:-}" ]; then
    log "DEPRECATED: CDAD_MODEL_PROFILE is obsolete and ignored (006-003 A-1) — the installer has no profiles; the model is chosen in the delegation config (delegation.json)"
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

set_install_paths() {
  OPENCODE_AGENTS_DIR="$INSTALL_ROOT/.config/opencode/agents"
  OPENCODE_SKILLS_DIR="$INSTALL_ROOT/.config/opencode/skills"
  AGENTS_SKILLS_DIR="$INSTALL_ROOT/.agents/skills"
  CLAUDE_CODE_AGENTS_DIR="$INSTALL_ROOT/.claude/agents"
  CLAUDE_CODE_SKILLS_DIR="$INSTALL_ROOT/.claude/skills"
  CLAUDE_CODE_SCRIPTS_DIR="$INSTALL_ROOT/.claude/cdad-scripts"
  # PD-9: legacy-removal-only destinations (see comment at the top of the file).
  PUBLIC_AGENTS_DIR="$INSTALL_ROOT/agents"
  PUBLIC_SKILLS_DIR="$INSTALL_ROOT/skills"
  OWNERSHIP_MANIFEST="$INSTALL_ROOT/$INSTALL_MANIFEST_NAME"
}

canonical_path() {
  local path="$1" existing suffix=""
  existing="$path"
  while [ ! -e "$existing" ] && [ ! -L "$existing" ]; do
    suffix="/$(basename "$existing")$suffix"
    existing=$(dirname "$existing")
  done
  if [ ! -d "$existing" ]; then
    die "Managed install destination has a non-directory ancestor: $path"
  fi
  existing="$(cd -P -- "$existing" && pwd)"
  printf '%s%s\n' "$existing" "$suffix"
}

paths_overlap() {
  local left="${1%/}" right="${2%/}"
  [ -n "$left" ] || left="/"
  [ -n "$right" ] || right="/"
  [ "$left" = "$right" ] || [[ "$left" == "$right/"* ]] || [[ "$right" == "$left/"* ]]
}

guard_source_overlap() {
  local destination canonical_destination extra_dir skill
  local -a destinations=(
    "$OPENCODE_AGENTS_DIR"
    "$OPENCODE_SKILLS_DIR"
    "$AGENTS_SKILLS_DIR"
    "$CLAUDE_CODE_AGENTS_DIR"
    "$CLAUDE_CODE_SKILLS_DIR"
    "$CLAUDE_CODE_SCRIPTS_DIR"
  )
  # PD-9 (004-001 T6): the public layout is not an install destination, so it
  # is not part of the managed-overlap guard either.
  while IFS= read -r extra_dir; do
    [ -n "$extra_dir" ] || continue
    for skill in "${SKILLS[@]}"; do
      destinations+=("$extra_dir/$skill")
    done
  done < <(extra_skills_dirs)
  for destination in "${destinations[@]}"; do
    canonical_destination="$(canonical_path "$destination")"
    if paths_overlap "$canonical_destination" "$SCRIPT_DIR"; then
      die "Managed install destination overlaps the source repository: $canonical_destination"
    fi
  done
}

guard_install_root() {
  local requested_root
  if [ -n "${CDAD_INSTALL_ROOT+x}" ]; then
    requested_root="$CDAD_INSTALL_ROOT"
    case "$requested_root" in
      /*) ;;
      *) die "CDAD_INSTALL_ROOT must be an absolute existing directory: $requested_root" ;;
    esac
    if [ ! -d "$requested_root" ]; then
      die "CDAD_INSTALL_ROOT must be an absolute existing directory: $requested_root"
    fi
  else
    guard_home
    requested_root="$HOME"
  fi
  INSTALL_ROOT="$(cd -P -- "$requested_root" && pwd)"
  set_install_paths
  guard_source_overlap
}

guard_python3() {
  if ! command -v python3 >/dev/null 2>&1; then
    die "Python 3 is required for the CDAD packet renderer (standard library only); install python3 before continuing"
  fi
}

guard_sources() {
  if [ ! -d "$SOURCE_SKILLS_DIR" ]; then
    die "Source skills directory missing: $SOURCE_SKILLS_DIR"
  fi
  # PD-12 (004-002 T6): the AGENTS are deployed exclusively from build/staging
  # (guard_staging); the installer no longer requires a source agents/
  # directory next to install.sh. sources/ stays unread.
  local s
  for s in "${SKILLS[@]}"; do
    if [ ! -d "$SOURCE_SKILLS_DIR/$s" ]; then
      die "Source skill missing: $SOURCE_SKILLS_DIR/$s"
    fi
  done
}

# ---------------------------------------------------------------------------
# Staging guards & provenance helpers (004-001 T5 / PD-18 / D4)
# ---------------------------------------------------------------------------
guard_staging() {  # the staging manifest is the declared single input: fail fast
  if [ ! -f "$STAGING_MANIFEST" ]; then
    die "Staging manifest missing: $STAGING_MANIFEST (regenerate it with \`make staging\` — the installer deploys the staged set exclusively and never reads sources/)"
  fi
  python3 - "$STAGING_MANIFEST" <<'PY' || die "Staging manifest is not valid JSON with a non-empty artifacts list: $STAGING_MANIFEST"
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
artifacts = data.get("artifacts")
assert isinstance(artifacts, list) and artifacts
for entry in artifacts:
    rel = entry.get("file")
    assert isinstance(entry, dict) and isinstance(rel, str)
    # Runtime membership is encoded in the path (staging merge, T5): an
    # artifact outside the known runtime dirs or nested deeper is a staging
    # defect — fail HERE (main shell), never silently inside a subshell.
    assert rel.startswith(("agents/opencode/", "agents/claude-code/")), rel
    name = rel.split("/", 2)[2]
    assert name and "/" not in name, rel
PY
}

sha256_of() {  # file -> hex digest (fail fast on read errors)
  sha256sum "$1" | awk '{print $1}'
}

# installation_version — deterministic, reproducible identifier of the version
# this install deployed (PD-14/INV-7). Prefers the generation commit when the
# product tree IS a git checkout; otherwise falls back to the content id of the
# staging manifest the installer already consumes (the portable/isolated case:
# a product copy need not be a git repo). Never an invented value.
installation_version() {
  local toplevel commit
  toplevel="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
  if [ "$toplevel" = "$SCRIPT_DIR" ]; then
    commit="$(git -C "$SCRIPT_DIR" rev-parse HEAD 2>/dev/null || true)"
    if [[ "$commit" =~ ^[0-9a-f]{7,64}$ ]]; then
      printf '%s\n' "$commit"
      return 0
    fi
  fi
  sha256_of "$STAGING_MANIFEST"
}

# write_version_marker — declares the installed version/commit AT THE INSTALL
# ROOT (PD-14/INV-7): a one-line `version.txt` the packet renderer reads
# (`_installation_version`) to publish `source_version` in the derived-agents
# manifest, so the version a session loaded is verifiable from the artifact.
# Recorded as an owned artifact so --uninstall retires it too.
write_version_marker() {
  local version="$1" marker="$INSTALL_ROOT/version.txt"
  if [ "$DRY_RUN" -eq 1 ]; then
    log "DRY-RUN VERSION $marker = $version"
    return 0
  fi
  printf '%s\n' "$version" > "$marker"
  record_owned "$marker" "install.sh (installation version)"
  log "VERSION marker: $marker = $version"
}

# install_root_abs <recorded-path> — resolve a path RECORDED in the ownership
# manifest against the install root (PD-6e): an absolute path is already
# resolved, a relative one resolves under the — possibly redirected — root.
install_root_abs() {
  case "$1" in
    /*) printf '%s' "$1" ;;
    *)  printf '%s/%s' "$INSTALL_ROOT" "$1" ;;
  esac
}

# owned_removal_state <path> <recorded-sha256> — the ONE rule that decides what a
# registered own path is entitled to right now. Shared by --uninstall
# (review-5 E1) and the obsolete prune (006-003 U7/D6) instead of duplicating it:
#   removable    — a symlink, or a regular file whose bytes match a RECORDED
#                  sha256: the digest was compared and the bytes are still the
#                  ones we deployed.
#   absent       — nothing at that path (idempotent).
#   modified     — a regular file whose bytes differ from a RECORDED digest: the
#                  user changed it after the install, so it is never discarded.
#   unverifiable — the record carries NO usable digest (empty or null, B-1): with
#                  nothing to compare against there is no evidence that the bytes
#                  are still ours, and INV-2 only authorizes retiring OWN bytes
#                  proven unchanged. Preserved and reported, never removed —
#                  neither on a re-install nor on --uninstall. (Before B-1 the
#                  empty digest fell into `removable` and the file was deleted.)
# A symlink is not the bytes we deployed (unlinking it destroys nothing of the
# user's), so it keeps the historical removable verdict.
owned_removal_state() {
  local path="$1" recorded="$2" actual
  if [ ! -L "$path" ] && [ ! -e "$path" ]; then printf 'absent'; return 0; fi
  if [ -z "$recorded" ]; then printf 'unverifiable'; return 0; fi
  if [ -L "$path" ]; then printf 'removable'; return 0; fi
  if [ ! -f "$path" ]; then printf 'absent'; return 0; fi
  actual="$(sha256_of "$path")"
  if [ "$actual" = "$recorded" ]; then printf 'removable'; return 0; fi
  printf 'modified'
}

record_owned() {  # abs_path source — register an owned file for the ownership manifest
  local abs="$1" source="$2" sha rel
  rel="${abs#"$INSTALL_ROOT"/}"
  # Tracked in BOTH modes (the manifest itself is not): the obsolete prune needs
  # to know which destinations this run deploys, and --dry-run has to preview the
  # same bajas it would perform.
  OWNED_ABS["$abs"]=1
  [ "$DRY_RUN" -eq 1 ] && return 0
  sha="$(sha256_of "$abs")"
  OWNED+=("$rel"$'\t'"$sha"$'\t'"$source")
}

# ---------------------------------------------------------------------------
# User-owned agent overlay (009-001) — consumed, never reimplemented
# ---------------------------------------------------------------------------
guard_agent_overlay() {
  if [ ! -f "$AGENT_OVERLAY_PY" ]; then
    die "User-owned overlay helper missing: $AGENT_OVERLAY_PY"
  fi
}

# agent_overlay_extract <file> — one `key=value` line per user-owned key present
# (nothing when the copy carries none). An ambiguous copy fails with its
# diagnostic on the captured output, so the caller preserves it (D3) instead of
# guessing.
agent_overlay_extract() {
  python3 "$AGENT_OVERLAY_PY" extract "$1"
}

# agent_overlay_base_sha <file> — sha256 of the copy WITHOUT its user-owned keys:
# the base this install compares its recorded provenance against (§2).
agent_overlay_base_sha() {
  python3 "$AGENT_OVERLAY_PY" base-sha "$1"
}

# agent_overlay_merge <staged> <installed> <out> — writes the staged bytes with
# the installed copy's user-owned values reinserted. The bytes go to a FILE: a
# shell variable would drop trailing newlines and corrupt the agent.
agent_overlay_merge() {
  python3 "$AGENT_OVERLAY_PY" merge "$1" "$2" --out "$3"
}

# agent_overlay_compare <installed> <expected> — sets OVERLAY_VERDICT
# (identical | overlay-only | divergent | error) and OVERLAY_DETAIL (the
# preserved keys, or the reason). Returns 0 when the installed bytes differ from
# the expectation at most by the user-owned overlay.
OVERLAY_VERDICT=""
OVERLAY_DETAIL=""
agent_overlay_compare() {
  local line status=0
  line="$(python3 "$AGENT_OVERLAY_PY" compare "$1" "$2" 2>&1)" || status=$?
  OVERLAY_VERDICT="${line%%:*}"
  if [ "$OVERLAY_VERDICT" = "$line" ]; then
    OVERLAY_DETAIL=""
  else
    OVERLAY_DETAIL="${line#*: }"
  fi
  [ "$status" -eq 0 ]
}

# print_ok_agent <path> — the OK line of an in-sync agent, disclosing the
# preserved user overlay (PC-6) when the last compare found one.
print_ok_agent() {
  if [ "$OVERLAY_VERDICT" = identical ]; then
    printf 'OK: %s\n' "$1"
  else
    printf 'OK: %s (user overlay preserved: %s)\n' "$1" "$OVERLAY_DETAIL"
  fi
}

# agent_removal_preserves_overlay <recorded-source> <path> — prints the retained
# user-owned overlay of an installed AGENT and returns 0 when the path carries
# one: user configuration is never deleted by ownership alone (§2, PC-7).
agent_removal_preserves_overlay() {
  local source="$1" path="$2" keys
  case "$source" in
    agents/*) ;;
    *) return 1 ;;
  esac
  keys="$(agent_overlay_extract "$path" 2>/dev/null)" || return 1
  [ -n "$keys" ] || return 1
  printf '%s' "$keys"
}

add_conflict() {  # rel reason — report and preserve (PD-7: never overwrite/delete)
  local rel="$1" reason="$2"
  CONFLICT_ABS["$(install_root_abs "$rel")"]=1
  CONFLICTS+=("$rel"$'\t'"$reason")
  if [ "$DRY_RUN" -eq 1 ]; then
    log "DRY-RUN CONFLICT: $rel — preserved ($reason)"
  else
    log "CONFLICT: $rel — preserved ($reason)"
  fi
}

staged_artifact_list() {  # prints "staging-rel<TAB>manifest-sha256" per staged artifact
  python3 - "$STAGING_MANIFEST" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
for entry in data.get("artifacts", []):
    rel = entry.get("file", "")
    if rel:
        print("%s\t%s" % (rel, entry.get("sha256", "")))
PY
}

staged_header() {  # key — prints the staging manifest header value (R3-O2)
  python3 - "$STAGING_MANIFEST" "$1" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
print(data.get(sys.argv[2], ""))
PY
}

staged_destinations() {  # staging-rel — prints the absolute destination(s); validated by guard_staging
  local srel="$1" name
  case "$srel" in
    agents/opencode/*)
      name="${srel#agents/opencode/}"
      case "$name" in */*) die "Unexpected nested staged artifact: $srel" ;; esac
      # PD-9 (004-001 T6): the public layout (<root>/agents|skills) is NOT an
      # install destination anymore — real runtime destinations only.
      printf '%s\n' "$OPENCODE_AGENTS_DIR/$name"
      ;;
    agents/claude-code/*)
      name="${srel#agents/claude-code/}"
      case "$name" in */*) die "Unexpected nested staged artifact: $srel" ;; esac
      printf '%s\n' "$CLAUDE_CODE_AGENTS_DIR/$name"
      ;;
  esac
}

# staged_agent_names <runtime> — the agent FILENAMES the STAGING manifest deploys
# to that runtime (one per line; nothing when there is no readable staging).
# PD-18: staging is the single deployment input, so it is also the single basis
# the post-install presence check can honestly compare against.
staged_agent_names() {  # runtime
  [ -f "$STAGING_MANIFEST" ] || return 0
  python3 - "$STAGING_MANIFEST" "$1" <<'PY'
import json, sys
path, runtime = sys.argv[1], sys.argv[2]
try:
    data = json.load(open(path, encoding="utf-8"))
except (OSError, ValueError):
    raise SystemExit(0)
prefix = "agents/%s/" % runtime
for entry in data.get("artifacts", []):
    rel = str(entry.get("file", ""))
    if rel.startswith(prefix):
        print(rel[len(prefix):])
PY
}

# staged_agent_count <runtime> — how many agents the staging manifest deploys to
# that runtime (plan amendment A-6). The expected agent count of the post-install
# Verify is DERIVED from the staged set, not a frozen constant: a staged agent the
# install no longer deploys (retired by D6/PD-6a) lowers the expectation with it,
# so the retirement cannot collide with a stale hardcoded total. Prints "" when
# there is no readable staging manifest (the caller falls back to the historical
# constant, e.g. the legacy --uninstall path over a manifest-less root).
staged_agent_count() {  # runtime — prints the count (empty if unresolvable)
  [ -f "$STAGING_MANIFEST" ] || return 0
  local count
  count="$(staged_agent_names "$1" | awk 'END { print NR + 0 }')"
  printf '%s' "$count"
}

# previous_artifact_sha <rel> — the sha256 registered by the LAST successful
# install (empty when the file is not owned yet). Load once per run, BEFORE
# any deploy: the shared stage_owned_file semantics (review-5 B2) need it for
# the skills/guard passes too, not only for the staged agents.
# B-1: the records are exchanged NUL-framed (never a TSV read with `IFS=$'\t'
# read`): tab is IFS whitespace, so consecutive tabs are ONE delimiter and an
# EMPTY field would silently shift the remaining columns into the wrong slots.
declare -A PREV_SHA=()
declare -A PREV_SRC=()
load_previous_ownership() {
  local prev="$OWNERSHIP_MANIFEST"
  [ -f "$prev" ] || return 0
  local rel sha source
  while IFS= read -r -d '' rel \
     && IFS= read -r -d '' sha \
     && IFS= read -r -d '' source; do
    [ -n "$rel" ] || continue
    PREV_SHA[$rel]="$sha"
    PREV_SRC[$rel]="$source"
  done < <(python3 - "$prev" <<'PY'
import json, sys

def field(value):
    # B-1: a `null` digest is published as EMPTY, never as the Python repr
    # `None`, so no record field can carry a non-string token.
    return value if isinstance(value, str) else ""

try:
    data = json.load(open(sys.argv[1], encoding="utf-8"))
except (OSError, ValueError):
    raise SystemExit(0)
artifacts = data.get("artifacts")
if not isinstance(artifacts, dict):
    raise SystemExit(0)
for rel, record in sorted(artifacts.items()):
    if isinstance(record, dict):
        sys.stdout.write("%s\0%s\0%s\0" % (
            rel, field(record.get("sha256")), field(record.get("source"))))
PY
)
}

# deploy_staged_overlay <staging-rel> <dst> <installed-rel> <keys>
# 009-001 D2: writes the STAGED bytes with the installed user-owned values
# reinserted — never the old file — or reports SYNC when the copy already is
# exactly that. The bytes that end up installed are recorded as owned, so the
# digest describes what the user now has (PC-3) and a second run is a no-op.
deploy_staged_overlay() {
  local srel="$1" dst="$2" rel="$3" keys="$4"
  local expected_file synced copy
  if [ -n "$keys" ]; then
    synced="staging + user overlay ($keys)"
    copy="staged bytes + user overlay $keys"
  else
    # The user removed their overlay: staging IS the expected result.
    synced="staging"
    copy="staging regenerated"
  fi
  expected_file="$(mktemp)" || die "Cannot create the user-overlay merge temp file"
  if ! agent_overlay_merge "$STAGING_DIR/$srel" "$dst" "$expected_file"; then
    rm -f "$expected_file"
    add_conflict "$rel" "the staged bytes cannot receive the user-owned overlay ($keys); PRESERVED for explicit resolution"
    return 0
  fi
  if cmp -s "$expected_file" "$dst"; then
    if [ "$DRY_RUN" -eq 1 ]; then
      log "DRY-RUN SYNC $rel already in sync with $synced"
    else
      log "SYNC $rel already in sync with $synced"
    fi
    record_owned "$dst" "$srel"
  else
    do_run "COPY ($copy) $srel -> $dst" overlay_write "$expected_file" "$dst"
    record_owned "$dst" "$srel"
  fi
  rm -f "$expected_file"
  return 0
}

# stage_user_overlay <staging-rel> <dst> <installed-sha> <recorded-sha>
# 009-001: the user-owned keys of the INSTALLED copy are the user's
# configuration, not local drift. Returns 0 when the copy can be brought to
# (staging + overlay) — in sync, redeployed, or preserved as a conflict — and 1
# when the difference is not an overlay at all, so the historical D4 path runs
# untouched.
# Order matters (§2). The comparison against the CURRENT staging decides sync
# FIRST: when the bytes outside the overlay ARE the staged bytes, nothing foreign
# is adopted — the result is staging plus the user's own values — so provenance
# has no remaining difference to judge. That is what makes changing the model,
# deleting it, and a copy an older installer left unowned an UPDATE instead of a
# conflict (review 009-001 F1). Provenance is consulted only when the base is NOT
# the current staging: there the difference left over is either the upstream
# update the record accredits (the base we recorded, with or without the overlay
# already applied) or a local edit, which stays preserved (PC-4).
# The referent is the STAGED FILE this run would deploy (the same bytes `cp`
# puts at a destination and `--check` compares against), not the digest the
# staging manifest declares: the decision is about bytes, and the manifest's
# value describes the tree as it was generated.
stage_user_overlay() {
  local srel="$1" dst="$2" installed_sha="$3" recorded="$4"
  local rel keys base_sha staged_sha
  # Agents are the only installable text with a user-owned overlay (§1). Every
  # other destination keeps the historical D4 diagnostic untouched, so a local
  # edit of a skill or a script is never reported as an overlay problem.
  case "$srel" in
    agents/*) ;;
    *) return 1 ;;
  esac
  rel="${dst#"$INSTALL_ROOT"/}"
  if ! keys="$(agent_overlay_extract "$dst" 2>&1)"; then
    add_conflict "$rel" "user-owned overlay cannot be recognized ($keys); PRESERVED for explicit resolution"
    return 0
  fi
  keys="${keys//$'\n'/, }"
  base_sha="$(agent_overlay_base_sha "$dst")" || die "Cannot read the user-owned overlay of: $dst"
  staged_sha="$(sha256_of "$STAGING_DIR/$srel")"
  if [ "$base_sha" != "$staged_sha" ]; then
    # Bytes outside the overlay differ from the current staging: an overlay never
    # authorizes adopting foreign bytes, and never hides a D4 conflict (PC-4).
    [ -n "$keys" ] || return 1
    if [ -z "$recorded" ]; then
      add_conflict "$rel" "an unowned copy carries a user-owned overlay ($keys); PRESERVED — an overlay does not authorize adopting foreign bytes"
      return 0
    fi
    if [ "$base_sha" != "$recorded" ] && [ "$installed_sha" != "$recorded" ]; then
      add_conflict "$rel" "modified outside the user-owned overlay ($keys: the bytes around it are not the ones recorded by the last install, $recorded); PRESERVED for explicit resolution"
      return 0
    fi
  fi
  deploy_staged_overlay "$srel" "$dst" "$rel" "$keys"
}

# overlay_write <merged-file> <dst> — replace the installed bytes IN PLACE so the
# destination keeps its mode and ownership (the merged copy lives in a temp).
overlay_write() {
  cat "$1" > "$2"
}

# stage_one_destination <staging-rel> <staged-sha> <abs-destination>
# PD-6/7 conflict semantics at ONE destination, then deploy or record:
#   symlink/non-regular at destination      -> conflict, preserved, NOT owned
#   owned file modified since last install  -> conflict, preserved, NOT owned
#   bytes differing only by the USER's       -> redeploy (staged + overlay), owned
#     overlay (009-001: base == staging)        (SYNC when it already is that)
#   installed bytes == staged bytes         -> in sync (or adopted), owned
#   registered + staging regenerated        -> redeploy the STAGED bytes
#   unowned bytes differ from staging        -> conflict, preserved, NOT owned
#                                              (unless only the overlay differs:
#                                               then the copy is repaired)
#   missing                                 -> deploy the STAGED bytes
stage_one_destination() {
  local srel="$1" staged_sha="$2" dst="$3"
  local rel installed_sha prev dst_dir
  rel="${dst#"$INSTALL_ROOT"/}"
  if [ -L "$dst" ] || { [ -e "$dst" ] && [ ! -f "$dst" ]; }; then
    add_conflict "$rel" "symlink or non-regular file at destination; never written through"
    return 0
  fi
  if [ -f "$dst" ]; then
    installed_sha="$(sha256_of "$dst")"
    prev="${PREV_SHA[$rel]:-}"
    if [ -n "$prev" ] && [ "$prev" != "$installed_sha" ]; then
      # The copy changed since the last install: the ONE sanctioned change is the
      # user-owned overlay on the bytes we recorded.
      if stage_user_overlay "$srel" "$dst" "$installed_sha" "$prev"; then
        return 0
      fi
      add_conflict "$rel" "modified locally since the last install (registered $prev, found $installed_sha)"
      return 0
    fi
    if [ "$installed_sha" = "$staged_sha" ]; then
      if [ "$DRY_RUN" -eq 1 ]; then
        log "DRY-RUN COPY $srel -> $dst"
        log "DRY-RUN SYNC $rel already in sync with staging"
      else
        log "SYNC $rel already in sync with staging"
      fi
      record_owned "$dst" "$srel"
      return 0
    fi
    if [ -z "$prev" ]; then
      # No record of this destination, yet the staged bytes are the only ones it
      # may carry outside an overlay: an overlay copy left unowned by an older
      # installer is repaired by the same comparison (review 009-001 F1c), while
      # any other foreign byte stays a preserved conflict.
      if stage_user_overlay "$srel" "$dst" "$installed_sha" "$prev"; then
        return 0
      fi
      add_conflict "$rel" "unowned content at an owned destination differs from staging"
      return 0
    fi
    # Owned and unchanged since the last install while staging moved on: the
    # copy can still carry the user's overlay (it was registered WITH it), so the
    # expected bytes are the new staging plus that overlay.
    if stage_user_overlay "$srel" "$dst" "$installed_sha" "$prev"; then
      return 0
    fi
    if [ "$DRY_RUN" -eq 1 ]; then
      log "DRY-RUN COPY $srel -> $dst"
      log "DRY-RUN STAGED-UPDATE $rel staging moved on; would redeploy the staged bytes"
      record_owned "$dst" "$srel"
    else
      do_run "COPY (staging regenerated) $srel -> $dst" cp -p "$STAGING_DIR/$srel" "$dst"
      record_owned "$dst" "$srel"
    fi
    return 0
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    log "DRY-RUN COPY $srel -> $dst"
    record_owned "$dst" "$srel"
    return 0
  fi
  dst_dir="$(dirname "$dst")"
  ensure_dir "$dst_dir"
  do_run "COPY $srel -> $dst" cp -p "$STAGING_DIR/$srel" "$dst"
  record_owned "$dst" "$srel"
}

# stage_owned_file <src> <dest> <source-label> [chmod-mode]
# Review-5 B2: SKILLS and the GUARD get the SAME ownership semantics as the
# staged agents (one shared policy, not per-file-type criteria). For ONE
# destination file:
#   symlink/non-regular at destination      -> conflict, preserved, NOT owned
#   owned file modified since last install  -> conflict, preserved, NOT owned
#   installed bytes == source bytes         -> in sync, owned
#   unowned bytes differ from source        -> conflict, preserved, NOT owned
#   owned file, source moved on             -> redeploy the source bytes
#   missing                                 -> deploy the source bytes
# [chmod-mode] is applied ONLY when bytes are actually (re)deployed — a
# preserved file is never touched in any way (D4/PD-7).
stage_owned_file() {
  local src="$1" dst="$2" source_label="$3" chmod_mode="${4:-}"
  local rel installed_sha src_sha prev dst_dir
  if [ ! -f "$src" ]; then
    add_conflict "$dst" "source missing; nothing overwritten"
    return 0
  fi
  rel="${dst#"$INSTALL_ROOT"/}"
  if [ -L "$dst" ] || { [ -e "$dst" ] && [ ! -f "$dst" ]; }; then
    add_conflict "$rel" "symlink or non-regular file at destination; never written through"
    return 0
  fi
  src_sha="$(sha256_of "$src")"
  if [ -f "$dst" ]; then
    installed_sha="$(sha256_of "$dst")"
    prev="${PREV_SHA[$rel]:-}"
    if [ -n "$prev" ] && [ "$prev" != "$installed_sha" ]; then
      add_conflict "$rel" "modified locally since the last install (registered $prev, found $installed_sha)"
      return 0
    fi
    if [ "$installed_sha" = "$src_sha" ]; then
      if [ "$DRY_RUN" -eq 1 ]; then
        log "DRY-RUN SYNC $rel already in sync"
      else
        log "SYNC $rel already in sync"
      fi
      record_owned "$dst" "$source_label"
      return 0
    fi
    if [ -z "$prev" ]; then
      add_conflict "$rel" "unowned content at an owned destination differs from the source; preserved for explicit resolution"
      return 0
    fi
    if [ "$DRY_RUN" -eq 1 ]; then
      log "DRY-RUN COPY $source_label -> $dst"
      log "DRY-RUN UPDATE $rel source moved on; would redeploy the source bytes"
      record_owned "$dst" "$source_label"
    else
      do_run "COPY (source moved on) $source_label -> $dst" cp -p "$src" "$dst"
      record_owned "$dst" "$source_label"
      if [ -n "$chmod_mode" ]; then
        chmod "$chmod_mode" "$dst"
      fi
    fi
    return 0
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    log "DRY-RUN COPY $source_label -> $dst"
    record_owned "$dst" "$source_label"
    return 0
  fi
  dst_dir="$(dirname "$dst")"
  ensure_dir "$dst_dir"
  do_run "COPY $source_label -> $dst" cp -p "$src" "$dst"
  record_owned "$dst" "$source_label"
  if [ -n "$chmod_mode" ]; then
    chmod "$chmod_mode" "$dst"
  fi
}

deploy_staged_agents() {  # deploy the manifest-declared staged set (D4)
  local srel staged_sha dst
  while IFS=$'\t' read -r srel staged_sha; do
    [ -n "$srel" ] || continue
    if [ ! -f "$STAGING_DIR/$srel" ]; then
      die "Staged artifact missing from the staging tree: $STAGING_DIR/$srel"
    fi
    while IFS= read -r dst; do
      [ -n "$dst" ] || continue
      stage_one_destination "$srel" "$staged_sha" "$dst"
    done < <(staged_destinations "$srel")
  done < <(staged_artifact_list)
}

# write_ownership_manifest — publish <root>/.cdad-install-manifest.json ATOMICALLY
# and ONLY after every deployment succeeded (no half state: a failed install
# never publishes ownership). Header = the staging manifest's resolved
# runtime/stack (R3-O2); artifacts map install-root-relative paths to
# sha256+source provenance of the installed bytes; conflicts lists what was
# preserved (unowned until resolved).
#
# The owned/conflict records CANNOT ride on stdin: `python3 - <<'PY'` reads the
# SCRIPT from stdin, so the heredoc wins over any pipe and the data never
# arrives (the green-003 fix-loop-2 crash). The records stream through a temp
# file instead: mktemp honors TMPDIR when set and falls back to /tmp without
# it — it never assumes HOME (review-3 P6 lesson), and the file is removed on
# every path, success or failure.
write_ownership_manifest() {
  [ "$DRY_RUN" -eq 1 ] && return 0
  local stream_file status=0
  stream_file="$(mktemp)" || die "Cannot create the ownership-manifest stream temp file"
  if ! {
    printf '%s\n' "${OWNED[@]}"
    printf '%s\n' '%%CONFLICTS%%'
    printf '%s\n' "${CONFLICTS[@]}"
  } > "$stream_file"; then
    rm -f "$stream_file"
    die "Cannot write the ownership-manifest stream temp file: $stream_file"
  fi
  python3 - "$STAGING_MANIFEST" "$OWNERSHIP_MANIFEST" "$stream_file" "$INSTALL_VERSION" "$PRUNE_PLAN_FILE" <<'PY' || status=$?
import json, os, sys
staging_path, out_path, stream_path, install_version = (
    sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
# 006-003 U7/D6: the obsolete-retirement plan of the prune pass ("" when it did
# not run, i.e. there was no previous manifest): the keys retired from disk (they
# must leave the manifest) and the entries preserved because they were modified
# locally (they must STAY registered — PD-6b/INV-2).
prune_path = sys.argv[5] if len(sys.argv) > 5 else ""
pruned, kept = set(), {}
if prune_path and os.path.exists(prune_path):
    blob = open(prune_path, encoding="utf-8").read()
    pruned_blob, _, kept_blob = blob.partition("%%KEPT%%")
    pruned = {line for line in pruned_blob.splitlines() if line.strip()}
    for line in kept_blob.splitlines():
        if not line.strip():
            continue
        rel, sha, source = line.split("\t", 2)
        kept[rel] = {"sha256": sha, "source": source}
stream = open(stream_path, encoding="utf-8").read().split("%%CONFLICTS%%", 1)
artifacts = {}
for line in stream[0].splitlines():
    if not line.strip():
        continue
    rel, sha, source = line.split("\t", 2)
    artifacts[rel] = {"sha256": sha, "source": source}
conflicts = []
for line in stream[1].splitlines():
    if not line.strip():
        continue
    rel, reason = line.split("\t", 1)
    conflicts.append({"path": rel, "reason": reason})
conflict_paths = {entry["path"] for entry in conflicts}
# Review-5 B3: a reinstall must never FORGET an installed file it has stopped
# deploying. Every previously registered file (last artifacts or last
# pending_removal) that was neither re-deployed nor conflicted this run stays
# REGISTERED as pending_removal — visible to --check, retired by --uninstall.
previous = {}
previous_pending = {}
if os.path.exists(out_path):
    try:
        pdata = json.load(open(out_path, encoding="utf-8"))
    except (OSError, ValueError):
        pdata = {}
    pa = pdata.get("artifacts")
    if isinstance(pa, dict):
        for rel, record in pa.items():
            if isinstance(record, dict):
                previous[rel] = record
    pp = pdata.get("pending_removal")
    if isinstance(pp, dict):
        for rel, record in pp.items():
            if isinstance(record, dict):
                previous_pending[rel] = record
pending = {}
for rel, record in sorted(previous.items()):
    if rel in artifacts or rel in conflict_paths or rel in pruned:
        continue
    pending[rel] = {"sha256": record.get("sha256", ""), "source": record.get("source", "")}
for rel, record in sorted(previous_pending.items()):
    if rel in artifacts or rel in conflict_paths or rel in pruned:
        continue  # re-adopted, conflicted or retired this run
    pending[rel] = {"sha256": record.get("sha256", ""), "source": record.get("source", "")}
# PD-6b: an obsolete own file the prune PRESERVED (modified locally) stays
# registered — a conflict disclosure never unregisters a file.
pending.update(kept)
staging = json.load(open(staging_path, encoding="utf-8"))
manifest = {
    "manifest_version": 1,
    "installer": "install.sh",
    # PD-14/INV-7: the installation declares its own version/commit so the
    # version a session loaded is verifiable from the published artifact.
    "source_version": install_version,
    "runtime": staging.get("runtime", ""),
    "stack": staging.get("stack", ""),
    "artifacts": dict(sorted(artifacts.items())),
    "pending_removal": dict(sorted(pending.items())),
    "conflicts": sorted(conflicts, key=lambda c: c["path"]),
}
tmp_path = out_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8") as fh:
    json.dump(manifest, fh, indent=2, sort_keys=True)
    fh.write("\n")
os.replace(tmp_path, out_path)
PY
  rm -f "$stream_file"
  if [ -n "$PRUNE_PLAN_FILE" ]; then
    rm -f "$PRUNE_PLAN_FILE"
    PRUNE_PLAN_FILE=""
  fi
  if [ "$status" -ne 0 ]; then
    die "Cannot write the ownership manifest: $OWNERSHIP_MANIFEST (stream reader exit $status)"
  fi
  log "OWNERSHIP manifest: $OWNERSHIP_MANIFEST"
  # 009-001 PC-1: an update whose only difference is the user's overlay must not
  # DECLARE a conflict — a "0 conflict(s)" line still reads as one, and the
  # dry-run summary already reports the count only when there is something to
  # report. So the preserved set is disclosed only when it is non-empty.
  if [ "${#CONFLICTS[@]}" -gt 0 ]; then
    log "OWNERSHIP summary: ${#OWNED[@]} owned file(s), ${#CONFLICTS[@]} conflict(s) (pending_removal carried in the manifest)"
  else
    log "OWNERSHIP summary: ${#OWNED[@]} owned file(s) (pending_removal carried in the manifest)"
  fi
}

# ---------------------------------------------------------------------------
# Install operations (staging-driven agents; ownership recorded per file)
# ---------------------------------------------------------------------------
sync_skill_to() {  # skill_name target_base_dir — per-file owned copy (review-5
                   # B2: same conflict-and-preserve policy as agents), never --delete
  local skill="$1" base="$2"
  local src="$SOURCE_SKILLS_DIR/$skill"
  local dst="$base/$skill"
  local src_file
  ensure_dir "$dst"
  # Every file gets the D4/PD-7 semantics via stage_owned_file: a locally
  # modified owned skill file is reported as a conflict and preserved byte
  # for byte, never overwritten. Files present in the destination but NOT in
  # the source are left alone (never --delete); if they were owned by a
  # previous install they surface as pending_removal (review-5 B3).
  while IFS= read -r -d '' src_file; do
    stage_owned_file "$src_file" "$dst/${src_file#"$src/"}" "skills/$skill/${src_file#"$src/"}"
  done < <(find "$src" -type f -print0)
}

install_skills() {
  local s
  for s in "${SKILLS[@]}"; do
    sync_skill_to "$s" "$OPENCODE_SKILLS_DIR"
    sync_skill_to "$s" "$AGENTS_SKILLS_DIR"
    # PD-9 (004-001 T6): no public-layout copy — <root>/skills is not a
    # runtime destination; the real runtimes above are the only bases.
    sync_skill_to "$s" "$CLAUDE_CODE_SKILLS_DIR"
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

# install_agents — deploys the STAGED agent set (build/staging, PD-18) with the
# D4 conflict semantics. The staged bytes carry the generation-time stack and
# derived bash policy: the installer transforms nothing (R3-O2: the resolution
# was recorded in the staging manifest, never recomputed here).
install_agents() {
  deploy_staged_agents
}

install_guard_script() {
  local src="$SCRIPT_DIR/scripts/claude-code-path-guard.sh"
  local dst="$CLAUDE_CODE_SCRIPTS_DIR/path-guard.sh"
  if [ ! -f "$src" ]; then
    log "WARN: Guard script not found: $src (Claude Code agents may fail to enforce path-scoping)"
    return 0
  fi
  # Review-5 B2: the guard is an owned artifact too — the SAME
  # conflict-and-preserve policy as agents and skills (a locally modified
  # guard is reported and preserved byte for byte, never overwritten).
  stage_owned_file "$src" "$dst" "scripts/claude-code-path-guard.sh" +x
}

# ---------------------------------------------------------------------------
# User configuration (006-003 U4/D3/D5, A-3/A-4)
# ---------------------------------------------------------------------------
# The delegation config and the server credential example are USER DATA, not
# install artifacts: created only when missing (never overwritten), never
# registered in the ownership manifest, and therefore never removed by
# --uninstall nor by the obsolete-retirement step. Location (spec §2.2/§2.3):
# $XDG_CONFIG_HOME/cdad/ when XDG_CONFIG_HOME is defined, otherwise
# <install-root>/.config/cdad/ (INV-6: a redirected root confines every write).
user_config_dir() {
  printf '%s/cdad' "${XDG_CONFIG_HOME:-$INSTALL_ROOT/.config}"
}

write_delegation_template() {  # path — v1 template, only when missing
  local path="$1"
  if [ -e "$path" ] || [ -L "$path" ]; then
    log "User config: $path already exists — preserved untouched (user data; never overwritten, never owned, never removed)"
    return 0
  fi
  cat > "$path" <<'JSON' || die "Cannot write the delegation config: $path"
{
  "version": 1,
  "models": {
    "opencode": {}
  }
}
JSON
  log "User config: $path (delegation config v1 template — set models.<destination-id>.<role> to choose the delegated model)"
}

# PD-9 (§2.6): the execution configuration per runtime. The entry resolves the
# runtime explicitly and reads its section of `runtimes.json` — the retired
# exec-config is no longer user configuration. Like the delegation config, this
# is USER DATA: created only when missing, never registered in the manifest,
# never overwritten. The delegated model and the credential do NOT live here
# (delegation.json, ADR-033 D3/point 6).
write_runtimes_template() {  # path — v1 template, only when missing
  local path="$1"
  if [ -e "$path" ] || [ -L "$path" ]; then
    log "User config: $path already exists — preserved untouched (user data; never overwritten, never owned, never removed)"
    return 0
  fi
  cat > "$path" <<'JSON' || die "Cannot write the runtimes config: $path"
{
  "version": 1,
  "runtimes": {}
}
JSON
  log "User config: $path (execution configuration v1 template — one section per runtime id; the model stays in delegation.json, never here)"
}

write_server_env_example() {  # path — credential template with no value
  local path="$1"
  if [ -e "$path" ] || [ -L "$path" ]; then
    log "User config: $path already exists — preserved untouched (user data; never overwritten, never owned, never removed)"
    return 0
  fi
  cat > "$path" <<'ENV' || die "Cannot write the server credential example: $path"
# CDAD OpenCode server credential — TEMPLATE ONLY: it carries no value.
#
# Copy it next to this file and keep the copy private (mode 600):
#   cp opencode-server.env.example opencode-server.env
#   chmod 600 opencode-server.env
#
# The password is the one of the `opencode serve` instance you dispatch
# against (with OpenChamber, the password configured there). The adapter
# reads the environment first and this file second; an empty value means
# "absent". Never commit the filled file.
OPENCODE_PASSWORD=
OPENCODE_SERVER_PASSWORD=
ENV
  log "User config: $path (credential template with no value; copy it to opencode-server.env with mode 600)"
}

install_user_config() {
  local config_dir
  config_dir="$(user_config_dir)"
  if [ "$DRY_RUN" -eq 1 ]; then
    log "DRY-RUN user config: $config_dir/delegation.json + runtimes.json + opencode-server.env.example (templates, written only when missing)"
    return 0
  fi
  ensure_dir "$config_dir"
  write_delegation_template "$config_dir/delegation.json"
  write_runtimes_template "$config_dir/runtimes.json"
  write_server_env_example "$config_dir/opencode-server.env.example"
}

# ---------------------------------------------------------------------------
# Obsolete own files (006-003 U7/D6: PD-6a..e)
# ---------------------------------------------------------------------------
# The installer retires ITS OWN obsolete files. Candidate = every entry a
# previous install registered (artifacts or pending_removal) that this run
# neither redeploys nor discloses as a conflict; --uninstall's rule decides
# (owned_removal_state, shared — never duplicated):
#   removable (bytes match the recorded sha256) -> retired from DISK and from the
#       manifest: the install no longer deploys it, so keeping it registered
#       forever would leave --check reporting a PENDING-REMOVAL nobody resolves;
#   modified -> PRESERVED, disclosed as CONFLICT and kept REGISTERED (PD-6b):
#       a local change is never discarded by an install (INV-2);
#   unverifiable (record with NO digest, B-1) -> PRESERVED exactly like a local
#       change, disclosed as CONFLICT and kept REGISTERED: without a digest there
#       is no proof the bytes are still ours, so INV-2 forbids retiring them;
#   absent -> nothing to do (idempotent; the registered entry is left as it is).
# A file the manifest does NOT register is never read nor written, so it cannot
# be touched even while the prune is active (PD-6c/INV-2), and the user config
# files are not registered either (A-3). --dry-run announces every baja through
# do_run and performs none.
prune_owned_obsolete() {
  local prev="$OWNERSHIP_MANIFEST"
  [ -f "$prev" ] || return 0
  local reg_path
  reg_path="$(mktemp)" || die "Cannot create the obsolete-prune registration temp file"
  # PD-6e: the manifest-reading python receives INSTALL_ROOT and resolves every
  # RECORDED path against it — absolute paths stay as they are, relative ones
  # resolve under the (possibly redirected) root. The hash compares the bytes on
  # DISK, and `owned_removal_state` decides with the recorded digest.
  # B-1: the records travel NUL-framed. A 4-column TSV read by bash
  # (`IFS=$'\t' read`) collapses consecutive tabs — tab is IFS whitespace, so
  # tab TAB is ONE delimiter — and an EMPTY recorded digest made the source land
  # in the digest slot (or the record look digest-less). NUL cannot appear in a
  # value, so every field arrives exactly as published, empty ones included.
  python3 - "$prev" "$INSTALL_ROOT" "$reg_path" <<'PY' || { rm -f "$reg_path"; die "Cannot read the ownership manifest: $prev"; }
import json, os, sys


def field(value):
    """A record field as text (B-1): a `null` digest is published as EMPTY, never
    as the Python repr `None`."""
    return value if isinstance(value, str) else ""


manifest_path, root, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    data = json.load(open(manifest_path, encoding="utf-8"))
except (OSError, ValueError):
    raise SystemExit(0)
records = {}
for section_name in ("artifacts", "pending_removal"):
    section = data.get(section_name)
    if not isinstance(section, dict):
        continue
    for rel, record in sorted(section.items()):
        if isinstance(record, dict) and rel not in records:
            records[rel] = record
with open(out_path, "w", encoding="utf-8") as out:
    for rel, record in sorted(records.items()):
        absolute = rel if os.path.isabs(rel) else os.path.join(root, rel)
        out.write("%s\0%s\0%s\0%s\0" % (
            absolute, rel, field(record.get("sha256")), field(record.get("source"))))
PY
  local abs rel sha source state preserved=0 plan_path overlay_keys
  local -A pruned_abs=()
  while IFS= read -r -d '' abs \
     && IFS= read -r -d '' rel \
     && IFS= read -r -d '' sha \
     && IFS= read -r -d '' source; do
    [ -n "$rel" ] || continue
    [ -n "${OWNED_ABS[$abs]:-}" ] && continue     # this run deploys it: not obsolete
    [ -n "${CONFLICT_ABS[$abs]:-}" ] && continue  # already reported and preserved
    if [ -n "${pruned_abs[$abs]:-}" ]; then
      PRUNED+=("$rel")                            # same destination, another key
      continue
    fi
    state="$(owned_removal_state "$abs" "$sha")"
    case "$state" in
      absent) continue ;;
      removable)
        # 009-001 §2: an installed agent that carries the user's overlay holds
        # user data — it is preserved and stays registered even though its bytes
        # still match their recorded digest.
        if overlay_keys="$(agent_removal_preserves_overlay "$source" "$abs")"; then
          preserved=$((preserved + 1))
          KEPT+=("$rel"$'\t'"$sha"$'\t'"$source")
          add_conflict "$rel" "no longer deployed by this install but carries the user-owned overlay ($overlay_keys); PRESERVED and kept registered"
          continue
        fi
        do_run "REMOVE (own obsolete: no longer deployed, bytes match the recorded sha256) $abs" rm -f -- "$abs"
        pruned_abs["$abs"]=1
        PRUNED+=("$rel")
        ;;
      modified|unverifiable)
        # `modified` (a local change) and `unverifiable` (a record with no
        # digest to compare against, B-1) share ONE outcome: the file is never
        # discarded by an install — it is disclosed and stays registered (PD-6b).
        preserved=$((preserved + 1))
        KEPT+=("$rel"$'\t'"$sha"$'\t'"$source")
        if [ "$state" = unverifiable ]; then
          add_conflict "$rel" "obsolete own file with no recorded sha256 to compare its bytes against; PRESERVED and kept registered (explicit resolution needed)"
        else
          add_conflict "$rel" "obsolete own file modified locally since the recorded install (registered $sha); PRESERVED and kept registered"
        fi
        ;;
      *) die "Unexpected removal state $state for $abs" ;;
    esac
  done < "$reg_path"
  rm -f "$reg_path"
  log "Obsolete prune: ${#PRUNED[@]} own file(s) retired, $preserved preserved (locally modified, or with no recorded digest — explicit resolution needed)"
  [ "$DRY_RUN" -eq 1 ] && return 0
  # The plan for write_ownership_manifest: keys to drop, then the entries that
  # must stay REGISTERED (PD-6b). Read by PYTHON (`split("\t", maxsplit=2)`,
  # which preserves empty fields) — never by a bash `read` (B-1).
  plan_path="$(mktemp)" || die "Cannot create the obsolete-prune plan temp file"
  if ! {
    printf '%s\n' "${PRUNED[@]}"
    printf '%s\n' '%%KEPT%%'
    printf '%s\n' "${KEPT[@]}"
  } > "$plan_path"; then
    rm -f "$plan_path"
    die "Cannot write the obsolete-prune plan: $plan_path"
  fi
  PRUNE_PLAN_FILE="$plan_path"
}

# ---------------------------------------------------------------------------
# Uninstall operations (cdad-owned paths only)
# ---------------------------------------------------------------------------
# uninstall_items — prints the paths uninstall would remove. Agents come from
# the SOURCE repo manifest (never a target-dir glob: a user-created cdad-*.md
# that was never in the repo must survive). Skills come from the hardcoded
# SKILLS array (same-input-same-output: uninstall removes what install
# installs, plus the public-layout copies that pre-T6 installs owned — PD-9:
# a legacy uninstall still frees the whole historical footprint).
uninstall_items() {
  local f base
  for f in "$SOURCE_AGENTS_DIR"/cdad-*.md; do
    [ -e "$f" ] || continue
    base=$(basename "$f")
    printf '%s\n' "$OPENCODE_AGENTS_DIR/$base"
    printf '%s\n' "$PUBLIC_AGENTS_DIR/$base"
  done
  for f in "$SOURCE_AGENTS_DIR"/claude-code/cdad-*.md; do
    [ -e "$f" ] || continue
    printf '%s\n' "$CLAUDE_CODE_AGENTS_DIR/$(basename "$f")"
  done
  printf '%s\n' "$CLAUDE_CODE_SCRIPTS_DIR/path-guard.sh"
  local s d
  for s in "${SKILLS[@]}"; do
    printf '%s\n' "$OPENCODE_SKILLS_DIR/$s"
    printf '%s\n' "$AGENTS_SKILLS_DIR/$s"
    printf '%s\n' "$CLAUDE_CODE_SKILLS_DIR/$s"
    printf '%s\n' "$PUBLIC_SKILLS_DIR/$s"
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
  local item
  while IFS= read -r item; do
    [ -n "$item" ] || continue
    do_run "UNINSTALL $item" rm -rf -- "$item"
  done < <(uninstall_items)
}

# uninstall_by_manifest — PD-8: remove EXACTLY the ownership manifest entries
# (per file: a foreign file inside an owned directory survives). Idempotent:
# already-removed entries are reported and skipped. Review-5 B3: pending_removal
# entries are retired too (a reinstall that no longer deploys a file keeps it
# registered until uninstall). Review-5 E1: a locally modified owned file is
# NEVER removed by ownership alone — it is reported and preserved for explicit
# resolution (its record stays in the manifest). B-1: a record with NO recorded
# digest is preserved the same way — without a digest there is no proof the bytes
# are still ours, and INV-2 only authorizes retiring own bytes proven unchanged.
# No confirmation prompt: the manifest IS the explicit resolution of what is ours.
uninstall_by_manifest() {
  local reg_path keep_file status=0 total=0 removed=0 preserved=0
  local key rel sha source path state overlay_keys
  local -a keep_artifacts=() keep_pending=()
  reg_path="$(mktemp)" || die "Cannot create the uninstall registration temp file"
  # B-1: NUL-framed records (never a 4-column TSV read by bash `read`, which
  # collapses consecutive tabs and shifted an empty digest's columns).
  python3 - "$OWNERSHIP_MANIFEST" "$reg_path" <<'PY' || { rm -f "$reg_path"; die "Cannot read the ownership manifest: $OWNERSHIP_MANIFEST"; }
import json, sys


def field(value):
    return value if isinstance(value, str) else ""


try:
    data = json.load(open(sys.argv[1], encoding="utf-8"))
except (OSError, ValueError):
    raise SystemExit(0)
out = open(sys.argv[2], "w", encoding="utf-8")
for key in ("artifacts", "pending_removal"):
    section = data.get(key)
    if not isinstance(section, dict):
        continue
    for rel, record in sorted(section.items()):
        if isinstance(record, dict):
            out.write("%s\0%s\0%s\0%s\0" % (
                key, rel, field(record.get("sha256")), field(record.get("source"))))
out.close()
PY
  log "Uninstalling per ownership manifest (artifacts + pending_removal); foreign files are never touched"
  while IFS= read -r -d '' key \
     && IFS= read -r -d '' rel \
     && IFS= read -r -d '' sha \
     && IFS= read -r -d '' source; do
    [ -n "$rel" ] || continue
    total=$((total + 1))
    path="$(install_root_abs "$rel")"
    # E1 (review-5) / 006-003 U7: historical ownership is not authorization to
    # discard later local changes — a modified owned file is reported and
    # PRESERVED. owned_removal_state is the ONE rule (also used by the obsolete
    # prune); a symlink or an absent path is handled exactly as before.
    state="$(owned_removal_state "$path" "$sha")"
    case "$state" in
      absent)
        log "UNINSTALL (absent, idempotent) $path"
        continue
        ;;
      modified|unverifiable)
        # `modified` (a local change) and `unverifiable` (no recorded digest,
        # B-1) share ONE outcome: PRESERVED for explicit resolution.
        preserved=$((preserved + 1))
        if [ "$key" = "artifacts" ]; then
          keep_artifacts+=("$rel"$'\t'"$sha"$'\t'"$source")
        else
          keep_pending+=("$rel"$'\t'"$sha"$'\t'"$source")
        fi
        if [ "$state" = unverifiable ]; then
          log "CONFLICT: $rel — the recorded install carries no sha256 to compare the bytes against; PRESERVED for explicit resolution (--uninstall did not remove it)"
        else
          log "CONFLICT: $rel — modified locally since the recorded install; PRESERVED for explicit resolution (--uninstall did not remove it)"
        fi
        continue
        ;;
      removable) ;;   # own bytes, unchanged: retired below
      *) die "Unexpected removal state $state for $path" ;;
    esac
    # 009-001 §2/PC-7: an installed agent that carries the user's overlay is user
    # configuration — ownership is not authorization to delete it, even when its
    # digest matches the manifest. It is preserved byte for byte and keeps its
    # record (a reinstall or a later --uninstall keeps reporting it).
    if overlay_keys="$(agent_removal_preserves_overlay "$source" "$path")"; then
      preserved=$((preserved + 1))
      if [ "$key" = "artifacts" ]; then
        keep_artifacts+=("$rel"$'\t'"$sha"$'\t'"$source")
      else
        keep_pending+=("$rel"$'\t'"$sha"$'\t'"$source")
      fi
      log "PRESERVED: $rel — carries the user-owned overlay ($overlay_keys); --uninstall keeps user configuration (delete the file explicitly to drop it)"
      continue
    fi
    do_run "UNINSTALL $path" rm -f -- "$path"
    removed=$((removed + 1))
  done < "$reg_path"
  rm -f "$reg_path"
  if [ "$DRY_RUN" -eq 0 ]; then
    keep_file="$(mktemp)" || die "Cannot create the uninstall preservation temp file"
    if ! {
      printf '%s\n' "${keep_artifacts[@]}"
      printf '%s\n' '%%PENDING%%'
      printf '%s\n' "${keep_pending[@]}"
    } > "$keep_file"; then
      rm -f "$keep_file"
      die "Cannot write the uninstall preservation temp file: $keep_file"
    fi
    python3 - "$OWNERSHIP_MANIFEST" "$keep_file" <<'PY' || status=$?
import json, os, sys
path, keep_path = sys.argv[1], sys.argv[2]
data = json.load(open(path, encoding="utf-8"))
stream = open(keep_path, encoding="utf-8").read()

def parse(blob):
    # PYTHON-side parse (B-1): `split("\t", maxsplit=2)` keeps EMPTY fields,
    # unlike a bash `read`. The hash never rides on bash column splitting.
    out = {}
    for line in blob.splitlines():
        if not line.strip():
            continue
        rel, sha, source = line.split("\t", 2)
        out[rel] = {"sha256": sha, "source": source}
    return out

try:
    kept_a, kept_p = stream.split("%%PENDING%%", 1)
except ValueError:
    kept_a, kept_p = stream, ""
data["artifacts"] = dict(sorted(parse(kept_a).items()))
data["pending_removal"] = dict(sorted(parse(kept_p).items()))
tmp = path + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(data, fh, indent=2, sort_keys=True)
    fh.write("\n")
os.replace(tmp, path)
PY
    rm -f "$keep_file"
    if [ "$status" -ne 0 ]; then
      die "Cannot update the ownership manifest after uninstall: $OWNERSHIP_MANIFEST (exit $status)"
    fi
  fi
  log "Uninstall complete: $removed of $total registered file(s) removed, $preserved preserved (locally modified, or with no recorded digest — explicit resolution needed)"
}

# ---------------------------------------------------------------------------
# Verification & summary
# ---------------------------------------------------------------------------
check_agent_file() {  # src dst — overlay-aware compare; 0 = in sync
  local src="$1" dst="$2" expected
  if [ ! -f "$dst" ]; then
    printf 'DRIFT: missing %s\n' "$dst"
    return 1
  fi
  # 009-002 PC-7: the expectation is the repo artifact AS EMITTED (V2
  # frontmatter; the bash policy is baked at generation time, 004-001 T5).
  # The comparison then applies the ONE definition of the user-owned overlay
  # (scripts/agent-overlay.py) — no second bash filter decides what an overlay
  # is (009-001 INV-2).
  expected="$(mktemp)" || die "Cannot create the agent check temp file"
  cat "$src" > "$expected"
  if agent_overlay_compare "$dst" "$expected"; then
    print_ok_agent "$dst"
    rm -f "$expected"
    return 0
  fi
  rm -f "$expected"
  printf 'DRIFT: differs %s (%s)\n' "$dst" "$OVERLAY_DETAIL"
  return 1
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
  # LEGACY path: roots installed BEFORE the ownership manifest existed. Those
  # roots carried the public layout (<root>/agents|skills), so it is still
  # checked/installed-referenced here for THEM; PD-9 installs (manifest-owned)
  # never reach this function (main dispatches to check_installed_staging).
  local f base s
  local total=0 expected_total=0 drifted=0
  local extra_total=0 extra_expected=0
  local -a drifted_paths=()
  expected_total=$(( $(count_flat_files "$SOURCE_AGENTS_DIR" 'cdad-*.md') * 2 + ${#SKILLS[@]} * 3 ))
  for f in "$SOURCE_AGENTS_DIR"/cdad-*.md; do
    [ -e "$f" ] || continue
    total=$((total + 1))
    base=$(basename "$f")
    if ! check_agent_file "$f" "$OPENCODE_AGENTS_DIR/$base"; then
      drifted_paths+=("$OPENCODE_AGENTS_DIR/$base")
      drifted=1
    fi
    if agent_overlay_compare "$PUBLIC_AGENTS_DIR/$base" "$f"; then
      total=$((total + 1))
      print_ok_agent "$PUBLIC_AGENTS_DIR/$base"
    else
      printf 'DRIFT: missing or differs %s\n' "$PUBLIC_AGENTS_DIR/$base"
      drifted_paths+=("$PUBLIC_AGENTS_DIR/$base")
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
    if check_skill_tree "$SOURCE_SKILLS_DIR/$s" "$PUBLIC_SKILLS_DIR/$s"; then
      total=$((total + 1))
    else
      drifted_paths+=("$PUBLIC_SKILLS_DIR/$s")
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
      log "Check: PASS ($total/$expected_total in sync + $extra_total/$extra_expected extra dirs)"
    else
      log "Check: PASS ($total/$expected_total in sync)"
    fi
    return 0
  fi
  log "Check: FAIL — ${drifted_paths[*]}"
  return 1
}

# check_installed_staging — PD-5 semantic check of an OWNED install (the
# ownership manifest exists) against the staging tree as the single truth:
#   - STAGING-DRIVEN owned artifacts (source = the staging-relative agents/*
#     path, by construction of the ownership manifest): drift vs the CURRENT
#     staged bytes, and OBSOLETE when the staged source disappeared upstream
#     (renamed/removed — case3/case10 semantics).
#   - LEGACY-PROVENANCE owned files (skills mirrored per file, the guard
#     script — sources "skills/…", "scripts/…", "install.sh …"): the OBSOLETE
#     staging-membership rule does NOT apply (the staging manifest only declares
#     agents); existence is the check, skill trees get their own byte comparison
#     below (green-003 fix-loop 3).
#   - every staged artifact must be owned (regenerated upstream, reinstall
#     needed).
# No profile logic here (006-003 D1): the installer deploys the staged bytes
# as-is (R3-O2).
# Owned entries OUTSIDE the install root (CDAD_SKILL_EXTRA_DIRS targets) are
# recorded with their absolute path as the key and addressed as-is.
check_installed_staging() {
  local rel source installed staged owned_sha
  local drift=0 total=0
  local -a problems=()
  declare -A STAGED_LISTED=()
  declare -A CHECK_OWNED=()

  while IFS= read -r srel; do
    [ -n "$srel" ] || continue
    STAGED_LISTED[$srel]=1
  done < <(python3 - "$STAGING_MANIFEST" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
for entry in data.get("artifacts", []):
    rel = entry.get("file", "")
    if rel:
        print(rel)
PY
)

  while IFS= read -r -d '' rel \
     && IFS= read -r -d '' owned_sha \
     && IFS= read -r -d '' source; do
    [ -n "$rel" ] || continue
    total=$((total + 1))
    CHECK_OWNED[$rel]=1
    case "$rel" in
      /*) installed="$rel" ;;
      *)  installed="$INSTALL_ROOT/$rel" ;;
    esac
    case "$source" in
      agents/*)
        # Staging-driven artifact: full PD-5 semantics vs the staged tree.
        staged="$STAGING_DIR/$source"
        if [ -z "${STAGED_LISTED[$source]:-}" ] || [ ! -f "$staged" ]; then
          printf 'OBSOLETE: %s (staged source %s is no longer in the staging manifest/tree)\n' "$installed" "$source"
          problems+=("OBSOLETE $rel")
          drift=1
        elif [ ! -f "$installed" ]; then
          printf 'DRIFT: missing %s\n' "$installed"
          problems+=("missing $rel")
          drift=1
        else
          # The installed copy is compared against the STAGED bytes through the
          # ONE overlay definition: a user-owned key is a disclosure, not drift
          # (009-001 PC-3/PC-6), and anything else still is drift. The diagnostic
          # names the INSTALLED path — never the staging file the user cannot act
          # on (D5).
          if agent_overlay_compare "$installed" "$staged"; then
            print_ok_agent "$installed"
          else
            printf 'DRIFT: differs %s (installed copy vs the current staged bytes: %s)\n' \
              "$installed" "$OVERLAY_DETAIL"
            problems+=("drift $rel")
            drift=1
          fi
        fi
        ;;
      *)
        # Legacy-provenance owned file: existence only (no staging membership).
        if [ ! -f "$installed" ]; then
          printf 'DRIFT: missing %s\n' "$installed"
          problems+=("missing $rel")
          drift=1
        else
          printf 'OK: %s\n' "$installed"
        fi
        ;;
    esac
  done < <(python3 - "$OWNERSHIP_MANIFEST" <<'PY'
import json, sys


def field(value):
    # B-1: NUL-framed fields, so an empty digest cannot shift the source column.
    return value if isinstance(value, str) else ""


data = json.load(open(sys.argv[1], encoding="utf-8"))
artifacts = data.get("artifacts")
if isinstance(artifacts, dict):
    for rel, record in sorted(artifacts.items()):
        if isinstance(record, dict):
            sys.stdout.write("%s\0%s\0%s\0" % (
                rel, field(record.get("sha256")), field(record.get("source"))))
PY
)

  # Review-5 B3: files registered as PENDING REMOVAL by a previous install
  # (owned once, no longer deployed by the current staging) stay VISIBLE here
  # until --uninstall retires them — a forgotten obsolete install must never
  # pass --check silently.
  local prel psha ppath
  while IFS=$'\t' read -r prel psha; do
    [ -n "$prel" ] || continue
    case "$prel" in
      /*) ppath="$prel" ;;
      *)  ppath="$INSTALL_ROOT/$prel" ;;
    esac
    if [ -f "$ppath" ] || [ -L "$ppath" ]; then
      printf 'PENDING-REMOVAL: %s (installed but no longer maintained by this install; retired by --uninstall)\n' "$ppath"
      problems+=("pending-removal $prel")
      drift=1
    fi
    # Already gone: silently idempotent (no rewrite here; --uninstall clears).
  done < <(python3 - "$OWNERSHIP_MANIFEST" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
pending = data.get("pending_removal")
if isinstance(pending, dict):
    for rel in sorted(pending):
        rec = pending[rel]
        if isinstance(rec, dict):
            print("%s\t%s" % (rel, rec.get("sha256", "")))
PY
)

  # Staged artifacts with no owned destination: upstream regenerated something
  # this install root never received (reinstall propagates it — PD-5).
  local srel covered dst drel
  local -a missing_destinations=()
  for srel in "${!STAGED_LISTED[@]}"; do
    covered=0
    while IFS= read -r dst; do
      [ -n "$dst" ] || continue
      drel="${dst#"$INSTALL_ROOT"/}"
      if [ -n "${CHECK_OWNED[$drel]:-}" ]; then
        covered=1
        break
      fi
    done < <(staged_destinations "$srel")
    if [ "$covered" -eq 0 ]; then
      # D5 (009-001): the diagnostic names the INSTALLED destination — the path
      # the user can act on — never the staging file, which is not theirs to fix.
      # Review F3: the SUMMARY entry has to name it too, or the last line of a
      # failed --check still sends the user to build/staging.
      missing_destinations=()
      while IFS= read -r dst; do
        [ -n "$dst" ] || continue
        printf 'MISSING (staged but not installed): %s\n' "$dst"
        missing_destinations+=("${dst#"$INSTALL_ROOT"/}")
      done < <(staged_destinations "$srel")
      if [ "${#missing_destinations[@]}" -gt 0 ]; then
        problems+=("missing ${missing_destinations[*]}")
      else
        problems+=("missing $srel (no installed destination resolves from staging)")
      fi
      drift=1
    fi
  done

  local s d
  for s in "${SKILLS[@]}"; do
    if check_skill_tree "$SOURCE_SKILLS_DIR/$s" "$OPENCODE_SKILLS_DIR/$s"; then
      total=$((total + 1))
    else
      problems+=("skills $OPENCODE_SKILLS_DIR/$s")
      drift=1
    fi
    if check_skill_tree "$SOURCE_SKILLS_DIR/$s" "$AGENTS_SKILLS_DIR/$s"; then
      total=$((total + 1))
    else
      problems+=("skills $AGENTS_SKILLS_DIR/$s")
      drift=1
    fi
    # PD-9 (004-001 T6): the public layout is no longer installed nor checked
    # here; the per-file ownership manifest still reports any pending_removal
    # entry left by a pre-T6 install that deployed it.
    if check_skill_tree "$SOURCE_SKILLS_DIR/$s" "$CLAUDE_CODE_SKILLS_DIR/$s"; then
      total=$((total + 1))
    else
      problems+=("skills $CLAUDE_CODE_SKILLS_DIR/$s")
      drift=1
    fi
  done
  local d
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    for s in "${SKILLS[@]}"; do
      if check_skill_tree "$SOURCE_SKILLS_DIR/$s" "$d/$s"; then
        total=$((total + 1))
      else
        problems+=("extra $d/$s")
        drift=1
      fi
    done
  done < <(extra_skills_dirs)

  if [ "$drift" -eq 0 ]; then
    log "Check: PASS ($total artifact groups in sync with staging/skills)"
    return 0
  fi
  # The verdict is the last line of the run and is emitted WITHOUT the log
  # timestamp so it can be grepped verbatim. Its entries name the INSTALLED
  # destinations (D5/PC-6): a summary that lists staging paths leaves the user
  # with nothing they can repair.
  printf 'Check: FAIL — %s\n' "${problems[*]}"
  return 1
}

print_summary() {  # mode: install | uninstall
  local mode="$1"
  local cdad_agents non_cdad total expected_agents
  cdad_agents=$(count_manifest_agents_installed "$OPENCODE_AGENTS_DIR")
  total=$(count_flat_files "$OPENCODE_AGENTS_DIR" '*.md')
  non_cdad=$((total - cdad_agents))
  # 006-003 plan amendment A-6: the expected agent count is DERIVED from the
  # staged set for this runtime — a staged agent retired by this same run
  # (PD-6a/D6) lowers the expectation instead of failing the Verify against a
  # frozen total. The historical constant is only the declared last resort when
  # the staged set is unreadable (e.g. legacy --uninstall over a root with no
  # staging), so unrelated summaries keep their previous wording.
  expected_agents="$(staged_agent_count opencode)"
  [ -n "$expected_agents" ] || expected_agents="$EXPECTED_CDAD_AGENTS"
  log "=== Summary ($mode) ==="
  log "Agents: $cdad_agents of $expected_agents staged cdad-*.md present in $OPENCODE_AGENTS_DIR"
  log "Agents dir: $non_cdad unmanaged .md files present (untouched)"
  local s d
  for s in "${SKILLS[@]}"; do
    log "  $s: $(count_tree_files "$OPENCODE_SKILLS_DIR/$s") files @ config, $(count_tree_files "$AGENTS_SKILLS_DIR/$s") files @ agents, $(count_tree_files "$CLAUDE_CODE_SKILLS_DIR/$s") files @ claude-code"
  done
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    for s in "${SKILLS[@]}"; do
      log "  $s: $(count_tree_files "$d/$s") files @ extra: $d"
    done
  done < <(extra_skills_dirs)
  if [ "$mode" = "install" ] && [ "$DRY_RUN" -eq 0 ] && [ "$cdad_agents" -ne "$expected_agents" ]; then
    log "Verify: FAIL — expected $expected_agents cdad agents, found $cdad_agents"
    return 1
  fi
  if [ "$mode" = "install" ]; then
    log "Verify: PASS — $cdad_agents cdad agents present after install"
  fi
}

print_dry_run_summary() {
  if [ "$UNINSTALL" -eq 1 ]; then
    local item_count
    item_count=$(uninstall_items | awk 'END { print NR + 0 }')
    log "=== Summary (dry-run uninstall) ==="
    log "Would remove $item_count managed item(s) (see DRY-RUN lines above)"
    return 0
  fi
  local staged_count conflicts_preview srel dst destinations
  staged_count=$(staged_artifact_list | awk 'END { print NR + 0 }')
  log "=== Summary (dry-run) ==="
  log "Staging: $STAGING_MANIFEST (runtime $(staged_header runtime), stack $(staged_header stack))"
  log "Staged set: $staged_count artifact(s) -> destinations below (R3-O2: the staging resolution is recorded, never recomputed)"
  while IFS=$'\t' read -r srel _; do
    [ -n "$srel" ] || continue
    destinations=""
    while IFS= read -r dst; do
      [ -n "$dst" ] || continue
      destinations+="${destinations:+, }$dst"
    done < <(staged_destinations "$srel")
    log "  $srel -> $destinations"
  done < <(staged_artifact_list)
  log "Skills: ${#SKILLS[@]} skills x 3 runtime bases + extra dirs, mirrored from $SOURCE_SKILLS_DIR (PD-9: no public layout)"
  conflicts_preview="${#CONFLICTS[@]}"
  if [ "$conflicts_preview" -gt 0 ]; then
    log "Conflicts (preserved, need explicit resolution): $conflicts_preview — see CONFLICT lines above"
  fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  parse_options "$@"
  guard_install_root

  if [ "$CHECK" -eq 1 ]; then
    guard_sources
    if [ -f "$OWNERSHIP_MANIFEST" ]; then
      # Owned install (004-001 T5): semantic check against staging (PD-5).
      guard_python3
      guard_agent_overlay
      guard_staging
      if check_installed_staging; then
        return 0
      fi
      return 1
    fi
    # Legacy check for roots installed before the ownership manifest existed.
    # Its comparisons also fold in the user-owned overlay (009-001), so it needs
    # the helper and, like every other path, the interpreter.
    guard_python3
    guard_agent_overlay
    if check_installed; then
      return 0
    fi
    return 1
  fi

  if [ "$UNINSTALL" -eq 1 ]; then
    if [ -f "$OWNERSHIP_MANIFEST" ]; then
      # PD-8: manifest-scoped uninstall (no prompt; the manifest is the
      # explicit record of what this installer owns). Idempotent. 009-001: an
      # installed agent with a user-owned overlay is preserved, never deleted.
      guard_python3
      guard_agent_overlay
      uninstall_by_manifest
      return 0
    fi
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

  guard_python3
  guard_agent_overlay
  guard_sources
  guard_staging
  # Review-5 B2: the per-file ownership semantics (stage_owned_file) compare
  # the installed bytes against the LAST install's register — needed for the
  # skills pass too, so load it once here, before anything is deployed.
  load_previous_ownership
  install_skills
  install_skills_extra
  install_agents
  # Claude Code targets (guard script; CC agents/skills come from the staged set)
  install_guard_script
  # 006-003 U4 (A-3/A-4): user data, created only when missing and never owned.
  install_user_config
  INSTALL_VERSION="$(installation_version)"
  write_version_marker "$INSTALL_VERSION"
  # 006-003 U7/D6 (PD-6a..e): retire the own obsolete files this run no longer
  # deploys (byte-identical only; modified ones are preserved and reported).
  prune_owned_obsolete
  write_ownership_manifest
  if [ "$DRY_RUN" -eq 1 ]; then
    print_dry_run_summary
  else
    print_summary install
  fi
  if [ "${#CONFLICTS[@]}" -gt 0 ]; then
    exit 1
  fi
}

main "$@"
