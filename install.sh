#!/usr/bin/env bash
# install.sh — CDAD skills & agents installer
#
# Deploys the CDAD skills and the STAGED agent set into the REAL runtime
# directories (~/.config/opencode, ~/.agents, ~/.claude) under an explicit
# install root. Since 004-001 T6 (PD-9) the public layout (<root>/agents and
# <root>/skills) is NO LONGER an install destination: installs land only at
# real runtime destinations. Since 004-001 T5 the AGENTS come exclusively from
# the staging tree declared by build/staging/manifest.json (PD-18: the
# installer never reads sources/; generation-time profile/stack resolution is
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
# manifest <install root>/.cdad-install-manifest.json — runtime/stack/profile
# resolved by staging (R3-O2) plus per-file sha256+source provenance for
# everything the installer deployed. Installs report conflicts (a locally
# modified owned file — agents, skills and the guard share the SAME
# conflict-and-preserve policy, review-5 B2 — or a symlink at a destination)
# and preserve the local bytes; files owned by a previous install that this
# install no longer deploys stay registered as pending_removal (visible to
# --check, retired by --uninstall; review-5 B3 — a reinstall never forgets).
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
# EXPECTED_CDAD_AGENTS counts OpenCode agents. Base = 6 generic (architect,
# implementer, orchestrator, reviewer, scribe, test-writer) + 5 Odoo variants
# (agents/cdad-*-odoo.md: architect/test-writer/implementer/reviewer/scribe).
# The cdad-.*-odoo variants are captured by the same cdad-*.md glob in
# install_agents() (now the staged set from build/staging) and carry a fixed
# model per role (generation-time, recorded in the staging manifest); they are
# counted here so the "N of N cdad agents present" verification is correct.
EXPECTED_CDAD_AGENTS=11
# NOTE: EXPECTED_CDAD_AGENTS counts OpenCode agents. Claude Code agents are
# staged under agents/claude-code/ and deployed to .claude/agents by the same
# staging-driven pass. EXPECTED_CDAD_AGENTS_CLAUDE_CODE=11 is their count.
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
# contract). The staging manifest also records the resolved runtime/stack/
# profile — published verbatim in the ownership manifest (R3-O2: the stack is
# an explicit recorded input, not a hidden effect of the machine).
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
PROFILE_FLAG=""
MODEL_PROFILE=""
PROFILE_MARKER="$OPENCODE_AGENTS_DIR/.cdad-models-profile"
OWNERSHIP_MANIFEST="$INSTALL_ROOT/$INSTALL_MANIFEST_NAME"
# Owned files recorded during THIS install: "rel<TAB>sha256<TAB>source".
OWNED=()
# Conflicts detected during THIS run: "rel<TAB>reason".
CONFLICTS=()
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
# Bash allowlists — derivation via the single policy source (004-001 T4)
# ---------------------------------------------------------------------------
# The bash POLICY lives only in the canonical role sources (sources/roles/)
# and is derived by scripts/cdad-generate.py (PD-1/PD-4). The adapter emitters
# (`scripts/cdad-bash-allowlist.sh`) compose that SAME policy and install.sh
# injects the derived block into the INSTALLED copies of the OpenCode agents
# only (same pattern as the model: line). The installed copy is derived
# output; the canonical sources are the truth for the policy.
ALLOWLIST_SH="$SCRIPT_DIR/scripts/cdad-bash-allowlist.sh"
if [ ! -f "$ALLOWLIST_SH" ]; then
  die "Bash allowlist generator missing: $ALLOWLIST_SH"
fi

# Roles whose bash block is derived (P5). The orchestrator is not task-spawned
# and keeps the handwritten block from the repo.
ALLOWLIST_ROLES="architect test-writer implementer reviewer scribe"

role_is_generated() {
  case " $ALLOWLIST_ROLES " in
    *" $1 "*) return 0 ;;
    *) return 1 ;;
  esac
}

# cdad_bash_allowlist <role> — prints the derived bash block for the role on
# this machine (the generator detects the stack; fail fast). Invoked via
# `bash` (same criterion as validate-subagents.sh with install.sh): only the
# file's existence matters; the +x bit is enforced by the separate A7 check.
cdad_bash_allowlist() {
  bash "$ALLOWLIST_SH" "$1"
}

# apply_bash_block <src> <role> — prints the file content with the bash section
# rules replaced by the derived allowlist. Pure function of (file, this
# machine's stack): that purity is what lets --check compare against the
# DERIVED expectation and not against repo bytes.
apply_bash_block() {
  local src="$1" role="$2" block
  block="$(cdad_bash_allowlist "$role")"
  awk -v block="$block" '
    /^---[[:space:]]*$/ { fm++; print; next }
    fm == 1 && /^[[:space:]]{2}bash:[[:space:]]*$/ {
      print
      printf "%s\n", block
      skip = 1
      next
    }
    fm == 1 && skip && /^[[:space:]]{2}[A-Za-z_-]+:/ { skip = 0 }
    skip { next }
    { print }
  ' "$src"
}

# rewrite_bash_section — RETIRED in 004-001 T5: the bash policy is derived at
# GENERATION time (scripts/cdad-generate.py, PD-1) and the installer deploys
# the staged bytes as-is. Kept only as a documentation anchor; the derivation
# used by the legacy --check path lives in apply_bash_block above.

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
  # When the source agents/ directory exists (a full checkout) the count keeps
  # the historical repo-manifest semantics. In an isolated product (PD-12:
  # agents/ absent) it falls back to the STAGED opencode set, which is the
  # single deployment input.
  local dir="$1"
  local f base name count=0
  if [ ! -d "$dir" ]; then
    printf '0'
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
  if [ ! -f "$STAGING_MANIFEST" ]; then
    printf '0'
    return 0
  fi
  while IFS= read -r name; do
    [ -n "$name" ] || continue
    if [ -f "$dir/$name" ]; then
      count=$((count + 1))
    fi
  done < <(python3 - "$STAGING_MANIFEST" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
for entry in data.get("artifacts", []):
    rel = entry.get("file", "")
    if rel.startswith("agents/opencode/"):
        print(rel.split("/", 2)[2])
PY
)
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

CDAD installer — deploys the CDAD skills and the STAGED agent set
(build/staging/manifest.json, produced by `make staging`) into the runtime
directories (~/.config/opencode, ~/.agents, ~/.claude and the public layout).
The agent artifacts come EXCLUSIVELY from staging (PD-18: sources/ is never
read); the deployed bytes are the staged bytes, which carry the generation-time
profile, stack and derived bash policy. Every successful install publishes the
ownership manifest <install root>/.cdad-install-manifest.json (runtime/stack/
profile resolved by staging + per-file sha256/source provenance).

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
               back to the legacy repo comparison (profile- and
               allowlist-aware against the derived expectation).
   --economical Install the economical profile marker (execution roles
                 deepseek-v4-flash; architect deepseek-v4-pro, reviewer
                 minimax-m3 — family different from the implementer; ADR-007).
  --optimus    Install the optimus profile marker (design default).
               The per-runtime model map is RETIRED (006-003 PD-1c): no profile
               resolves models any more, and the deployed agent bytes (the
               STAGING bytes, recorded in the staging manifest) carry no
               `model:` line.
  --premium    Install the premium profile marker (top-tier, configurable via
               env CDAD_PREMIUM_MODEL_<ROLE>). The profile flags are mutually
               exclusive.
  --basic      Install the basic profile marker: NO fixed models — agents
               inherit the runtime's default model. Like --optimus: the
               deployed agent bytes carry the STAGING profile resolved at
               GENERATION time (R3-O2; recorded in build/staging/manifest.json),
               so to deploy basic models regenerate the staging with that
               profile first. With a staging of another profile the flag
               only persists the marker: the disagreement is reported
               (PROFILE MISMATCH) and the STAGED profile prevails — no
               contradictory label is published. There is NO automatic
               portability across providers: rc and re-staging behavior
               under a mismatched staging is deferred to epic-004 T6
               (decision registered, review-6 R6-B1).
               Trade-off (ADR-007): the reviewer≠implementer anti-bias
               invariant is NOT enforced by the installer in this profile —
               configure models manually if you need it.
  --help       Show this help and exit.

Exit codes: rc=1 from install/--uninstall/--check means PENDING work —
 conflicts preserved on re-install (CONFLICT ... PRESERVED), staged
 removals not yet retired (PENDING-REMOVAL), or drift (DRIFT) — NOT a
 broken install: the rest is deployed and coherent; resolve the reported
 conflicts first.

No flags = install (safe default). The profile is STATEFUL: the last profile
installed persists via .cdad-models-profile, so a later install without flag
or env reuses it instead of falling back to optimus. Precedence is the same
everywhere (install, --check, --dry-run):
    flag > env CDAD_MODEL_PROFILE > marker .cdad-models-profile > optimus
Fresh installs (no marker yet) default to optimus (the repo's design default);
switch profiles at any time with `install.sh --<profile>` — the new choice is
installed AND persisted as the marker.

Environment — premium overrides (top-tier multi-provider; no forced mofgw
prefix; the target provider must be configured in the runtime, e.g.
opencode.jsonc):
  CDAD_PREMIUM_MODEL_ARCHITECT    top-tier architect (default mofgw/qwen3.7-max)
  CDAD_PREMIUM_MODEL_TEST_WRITER  top-tier test-writer (default mofgw/glm-5.2)
  CDAD_PREMIUM_MODEL_IMPLEMENTER  top-tier implementer (default mofgw/deepseek-v4-pro)
  CDAD_PREMIUM_MODEL_REVIEWER     top-tier reviewer (default mofgw/qwen3.7-max)
  CDAD_PREMIUM_MODEL_SCRIBE       top-tier scribe (default mofgw/qwen3.7-max)
  Example: CDAD_PREMIUM_MODEL_REVIEWER=anthropic/claude-sonnet-4-5 \
           bash install.sh --premium
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
      The staged bytes already carry the generation-time profile (model: line)
      and the derived bash: policy — the installer transforms nothing.
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
      (runtime/stack/profile resolved by staging — R3-O2 — plus per-file
       sha256 + source provenance of everything deployed; conflicts listed
       separately until explicitly resolved)

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
      --basic)     normalized+=(-b) ;;
      --help)      normalized+=(-h) ;;
      --*)         die "Unknown option: $arg (see --help)" ;;
      *)           normalized+=("$arg") ;;
    esac
  done
  set -- "${normalized[@]}"

  local opt profile_count=0
  while getopts "dfuceboph" opt; do
    case "$opt" in
      d) DRY_RUN=1 ;;
      f) FORCE=1 ;;
      u) UNINSTALL=1 ;;
      c) CHECK=1 ;;
      e) PROFILE_FLAG=economical; profile_count=$((profile_count + 1)) ;;
      o) PROFILE_FLAG=optimus;    profile_count=$((profile_count + 1)) ;;
      p) PROFILE_FLAG=premium;    profile_count=$((profile_count + 1)) ;;
      b) PROFILE_FLAG=basic;      profile_count=$((profile_count + 1)) ;;
      h) usage; exit 0 ;;
      *) usage; exit 1 ;;
    esac
  done
  shift $((OPTIND - 1))
  if [ $# -gt 0 ]; then
    die "Unexpected arguments: $* (see --help)"
  fi
  if [ "$profile_count" -gt 1 ]; then
    die "Profile flags are mutually exclusive: use only one of --economical | --optimus | --premium | --basic"
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
  PROFILE_MARKER="$OPENCODE_AGENTS_DIR/.cdad-models-profile"
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

record_owned() {  # abs_path source — register an owned file for the ownership manifest
  [ "$DRY_RUN" -eq 1 ] && return 0
  local abs="$1" source="$2" sha rel
  sha="$(sha256_of "$abs")"
  rel="${abs#"$INSTALL_ROOT"/}"
  OWNED+=("$rel"$'\t'"$sha"$'\t'"$source")
}

add_conflict() {  # rel reason — report and preserve (PD-7: never overwrite/delete)
  local rel="$1" reason="$2"
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

# previous_artifact_sha <rel> — the sha256 registered by the LAST successful
# install (empty when the file is not owned yet). Load once per run, BEFORE
# any deploy: the shared stage_owned_file semantics (review-5 B2) need it for
# the skills/guard passes too, not only for the staged agents.
declare -A PREV_SHA=()
declare -A PREV_SRC=()
load_previous_ownership() {
  local prev="$OWNERSHIP_MANIFEST"
  [ -f "$prev" ] || return 0
  local rel sha source
  while IFS=$'\t' read -r rel sha source; do
    [ -n "$rel" ] || continue
    PREV_SHA[$rel]="$sha"
    PREV_SRC[$rel]="$source"
  done < <(python3 - "$prev" <<'PY'
import json, sys
try:
    data = json.load(open(sys.argv[1], encoding="utf-8"))
except (OSError, ValueError):
    raise SystemExit(0)
artifacts = data.get("artifacts")
if not isinstance(artifacts, dict):
    raise SystemExit(0)
for rel, record in sorted(artifacts.items()):
    if isinstance(record, dict):
        print("%s\t%s\t%s" % (rel, record.get("sha256", ""), record.get("source", "")))
PY
)
}

# stage_one_destination <staging-rel> <staged-sha> <abs-destination>
# PD-6/7 conflict semantics at ONE destination, then deploy or record:
#   symlink/non-regular at destination      -> conflict, preserved, NOT owned
#   owned file modified since last install  -> conflict, preserved, NOT owned
#   installed bytes == staged bytes         -> in sync (or adopted), owned
#   registered + staging regenerated        -> redeploy the STAGED bytes
#   unowned bytes differ from staging       -> conflict, preserved, NOT owned
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
      add_conflict "$rel" "unowned content at an owned destination differs from staging"
      return 0
    fi
    if [ "$DRY_RUN" -eq 1 ]; then
      log "DRY-RUN COPY $srel -> $dst"
      log "DRY-RUN STAGED-UPDATE $rel staging moved on; would redeploy the staged bytes"
    else
      do_run "COPY (staging regenerated) $srel -> $dst" cp -p "$STAGING_DIR/$srel" "$dst"
      record_owned "$dst" "$srel"
    fi
    return 0
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    log "DRY-RUN COPY $srel -> $dst"
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
# runtime/stack/profile (R3-O2); artifacts map install-root-relative paths to
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
  python3 - "$STAGING_MANIFEST" "$OWNERSHIP_MANIFEST" "$stream_file" "$INSTALL_VERSION" <<'PY' || status=$?
import json, os, sys
staging_path, out_path, stream_path, install_version = (
    sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
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
    if rel in artifacts or rel in conflict_paths:
        continue
    pending[rel] = {"sha256": record.get("sha256", ""), "source": record.get("source", "")}
for rel, record in sorted(previous_pending.items()):
    if rel in artifacts or rel in conflict_paths:
        continue  # re-adopted or conflicted this run
    pending[rel] = {"sha256": record.get("sha256", ""), "source": record.get("source", "")}
staging = json.load(open(staging_path, encoding="utf-8"))
manifest = {
    "manifest_version": 1,
    "installer": "install.sh",
    # PD-14/INV-7: the installation declares its own version/commit so the
    # version a session loaded is verifiable from the published artifact.
    "source_version": install_version,
    "runtime": staging.get("runtime", ""),
    "stack": staging.get("stack", ""),
    "profile": staging.get("profile", ""),
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
  if [ "$status" -ne 0 ]; then
    die "Cannot write the ownership manifest: $OWNERSHIP_MANIFEST (stream reader exit $status)"
  fi
  log "OWNERSHIP manifest: $OWNERSHIP_MANIFEST"
  log "OWNERSHIP summary: ${#OWNED[@]} owned file(s), ${#CONFLICTS[@]} conflict(s) (pending_removal carried in the manifest)"
}

# ---------------------------------------------------------------------------
# Profile resolution (fail fast on invalid profile)
# ---------------------------------------------------------------------------
# resolve_profile — assigns MODEL_PROFILE (active profile). Consistent
# precedence across install, --check and --dry-run:
#     flag > env CDAD_MODEL_PROFILE > marker .cdad-models-profile > optimus
# The marker makes the install STATEFUL: the last installed profile persists
# (an install without flag or env respects it); a fresh install without a
# marker uses optimus (repo's design). --check already read the marker;
# now install does too.
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

# 006-003 PD-1c/PD-1f: the per-profile model map is RETIRED, so there is no
# map left to validate a profile against (`validate_profile` and its
# `cdad_valid_profile` lookup are gone). The profile surface itself (flag
# rejection, marker retirement) belongs to the installer unit of 006-003.

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

write_profile_marker() {  # <profile> — persists the EFFECTIVE profile (B4:
                          # marker == manifest.profile == staging.profile)
  local persist_profile="$1"
  ensure_dir "$OPENCODE_AGENTS_DIR"
  if [ "$DRY_RUN" -eq 1 ]; then
    log "DRY-RUN MARKER $PROFILE_MARKER = $persist_profile"
  else
    printf '%s\n' "$persist_profile" > "$PROFILE_MARKER"
    record_owned "$PROFILE_MARKER" "install.sh (model profile state)"
    log "PROFILE marker: $PROFILE_MARKER = $persist_profile"
  fi
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
# D4 conflict semantics. The staged bytes carry the generation-time profile,
# stack and derived bash policy: the installer transforms nothing (R3-O2: the
# resolution was recorded in the staging manifest, never recomputed here).
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
  printf '%s\n' "$PROFILE_MARKER"
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
# resolution (its record stays in the manifest).
# No confirmation prompt: the manifest IS the explicit resolution of what is ours.
uninstall_by_manifest() {
  local reg_path keep_file status=0 total=0 removed=0 preserved=0
  local key rel sha source path actual
  local -a keep_artifacts=() keep_pending=()
  reg_path="$(mktemp)" || die "Cannot create the uninstall registration temp file"
  python3 - "$OWNERSHIP_MANIFEST" "$reg_path" <<'PY' || { rm -f "$reg_path"; die "Cannot read the ownership manifest: $OWNERSHIP_MANIFEST"; }
import json, sys
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
            out.write("%s\t%s\t%s\t%s\n" % (key, rel, record.get("sha256", ""), record.get("source", "")))
out.close()
PY
  log "Uninstalling per ownership manifest (artifacts + pending_removal); foreign files are never touched"
  while IFS=$'\t' read -r key rel sha source; do
    [ -n "$rel" ] || continue
    total=$((total + 1))
    case "$rel" in
      /*) path="$rel" ;;
      *)  path="$INSTALL_ROOT/$rel" ;;
    esac
    if [ -L "$path" ]; then
      do_run "UNINSTALL $path" rm -f -- "$path"
      removed=$((removed + 1))
      continue
    fi
    if [ ! -f "$path" ]; then
      log "UNINSTALL (absent, idempotent) $path"
      continue
    fi
    # E1 (review-5): historical ownership is not authorization to discard
    # later local changes — a modified owned file is reported and PRESERVED.
    actual="$(sha256_of "$path")"
    if [ -n "$sha" ] && [ "$actual" != "$sha" ]; then
      preserved=$((preserved + 1))
      if [ "$key" = "artifacts" ]; then
        keep_artifacts+=("$rel"$'\t'"$sha"$'\t'"$source")
      else
        keep_pending+=("$rel"$'\t'"$sha"$'\t'"$source")
      fi
      log "CONFLICT: $rel — modified locally since the recorded install; PRESERVED for explicit resolution (--uninstall did not remove it)"
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
  log "Uninstall complete: $removed of $total registered file(s) removed, $preserved preserved (locally modified — explicit resolution needed)"
}

# ---------------------------------------------------------------------------
# Verification & summary
# ---------------------------------------------------------------------------
check_agent_file() {  # src dst role expected — profile-aware + allowlist-derived compare; 0 = identical
  local src="$1" dst="$2" role="$3" expected="$4"
  if [ ! -f "$dst" ]; then
    printf 'DRIFT: missing %s\n' "$dst"
    return 1
  fi
  # Byte-compare of the content WITHOUT the model: line — the deploy may drift
  # from the repo ONLY on that line (profile applied to the copy) and on the
  # bash block (allowlist derived from THIS machine's stack, P5 cdad-010). The
  # expectation is DERIVED: the repo goes through the same replacement as the
  # installation — it is not compared against repo bytes.
  if role_is_generated "$role"; then
    if ! cmp -s <(apply_bash_block "$src" "$role" | grep -v '^model:') <(grep -v '^model:' "$dst"); then
      printf 'DRIFT: differs %s\n' "$dst"
      return 1
    fi
  else
    if ! cmp -s <(grep -v '^model:' "$src") <(grep -v '^model:' "$dst"); then
      printf 'DRIFT: differs %s\n' "$dst"
      return 1
    fi
  fi
  # The runtime's model: line must be EXACTLY the active profile's model.
  local actual
  actual="$(sed -n 's/^model:[[:space:]]*//p' "$dst" | head -1)"
  if [ -z "$expected" ]; then
    if [ -n "$actual" ]; then
      printf '❌ %s: declares model: %s but role %s carries no model in profile %s\n' "$dst" "$actual" "$role" "$MODEL_PROFILE"
      return 1
    fi
  elif [ "$actual" != "$expected" ]; then
    printf '❌ %s: expected model (profile %s) = %s, found: %s\n' "$dst" "$MODEL_PROFILE" "$expected" "${actual:-<none>}"
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
  # LEGACY path: roots installed BEFORE the ownership manifest existed. Those
  # roots carried the public layout (<root>/agents|skills), so it is still
  # checked/installed-referenced here for THEM; PD-9 installs (manifest-owned)
  # never reach this function (main dispatches to check_installed_staging).
  local f base s role want_model
  local total=0 expected_total=0 drifted=0
  local extra_total=0 extra_expected=0
  local -a drifted_paths=()
  expected_total=$(( $(count_flat_files "$SOURCE_AGENTS_DIR" 'cdad-*.md') * 2 + ${#SKILLS[@]} * 3 ))
  for f in "$SOURCE_AGENTS_DIR"/cdad-*.md; do
    [ -e "$f" ] || continue
    total=$((total + 1))
    base=$(basename "$f")
    role=${base#cdad-}
    role=${role%.md}
    # 006-003 PD-1e/INV-3: no agent fixes a model, so nothing is expected here
    # (the retired map used to answer this) — the installed bytes must carry
    # no `model:` line either.
    want_model=""
    if ! check_agent_file "$f" "$OPENCODE_AGENTS_DIR/$base" "$role" "$want_model"; then
      drifted_paths+=("$OPENCODE_AGENTS_DIR/$base")
      drifted=1
    fi
    if cmp -s "$f" "$PUBLIC_AGENTS_DIR/$base"; then
      total=$((total + 1))
      printf 'OK: %s\n' "$PUBLIC_AGENTS_DIR/$base"
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
      log "Check: PASS ($total/$expected_total in sync + $extra_total/$extra_expected extra dirs, profile $MODEL_PROFILE)"
    else
      log "Check: PASS ($total/$expected_total in sync, profile $MODEL_PROFILE)"
    fi
    return 0
  fi
  log "Check: FAIL — ${drifted_paths[*]} (profile $MODEL_PROFILE)"
  return 1
}

# check_installed_staging — PD-5 semantic check of an OWNED install (the
# ownership manifest exists) against the staging tree as the single truth:
#   - STAGING-DRIVEN owned artifacts (source = the staging-relative agents/*
#     path, by construction of the ownership manifest): drift vs the CURRENT
#     staged bytes, and OBSOLETE when the staged source disappeared upstream
#     (renamed/removed — case3/case10 semantics).
#   - LEGACY-PROVENANCE owned files (skills mirrored per file, the guard
#     script, the profile marker — sources "skills/…", "scripts/…",
#     "install.sh …"): the OBSOLETE staging-membership rule does NOT apply
#     (the staging manifest only declares agents); existence is the check,
#     skill trees get their own byte comparison below (green-003 fix-loop 3).
#   - every staged artifact must be owned (regenerated upstream, reinstall
#     needed).
# No profile logic here: the installer deploys the staged bytes as-is (R3-O2).
# Owned entries OUTSIDE the install root (CDAD_SKILL_EXTRA_DIRS targets) are
# recorded with their absolute path as the key and addressed as-is.
check_installed_staging() {
  local rel source installed staged owned_sha staged_sha installed_sha
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

  while IFS=$'\t' read -r rel owned_sha source; do
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
          staged_sha="$(sha256_of "$staged")"
          # Review-5 B1: hash the INSTALLED bytes — the manifest sha256 is
          # historical; only the bytes actually under this root can drift
          # after the install (or after a staging regeneration).
          installed_sha="$(sha256_of "$installed")"
          if [ "$installed_sha" != "$staged_sha" ]; then
            printf 'DRIFT: differs %s (installed copy differs from the current staged bytes)\n' "$installed"
            problems+=("drift $rel")
            drift=1
          else
            printf 'OK: %s\n' "$installed"
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
data = json.load(open(sys.argv[1], encoding="utf-8"))
artifacts = data.get("artifacts")
if isinstance(artifacts, dict):
    for rel, record in sorted(artifacts.items()):
        if isinstance(record, dict):
            print("%s\t%s\t%s" % (rel, record.get("sha256", ""), record.get("source", "")))
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
      printf 'MISSING (staged but not installed): %s\n' "$STAGING_DIR/$srel"
      problems+=("missing staged $srel")
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
  log "Check: FAIL — ${problems[*]}"
  return 1
}

print_summary() {  # mode: install | uninstall
  local mode="$1"
  local cdad_agents non_cdad total
  cdad_agents=$(count_manifest_agents_installed "$OPENCODE_AGENTS_DIR")
  total=$(count_flat_files "$OPENCODE_AGENTS_DIR" '*.md')
  non_cdad=$((total - cdad_agents))
  log "=== Summary ($mode) ==="
  log "Agents: $cdad_agents of $EXPECTED_CDAD_AGENTS staged cdad-*.md present in $OPENCODE_AGENTS_DIR"
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
    local item_count
    item_count=$(uninstall_items | awk 'END { print NR + 0 }')
    log "=== Summary (dry-run uninstall) ==="
    log "Would remove $item_count managed item(s) (see DRY-RUN lines above)"
    return 0
  fi
  local staged_count conflicts_preview srel dst destinations
  staged_count=$(staged_artifact_list | awk 'END { print NR + 0 }')
  log "=== Summary (dry-run) ==="
  log "Model profile: requested $MODEL_PROFILE, effective ${effective_profile:-$MODEL_PROFILE} (the deployed agent bytes are the STAGED ones)"
  log "Staging: $STAGING_MANIFEST (runtime $(staged_header runtime), stack $(staged_header stack), profile $(staged_header profile))"
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
      guard_staging
      if check_installed_staging; then
        return 0
      fi
      return 1
    fi
    # Legacy check for roots installed before the ownership manifest existed.
    resolve_profile
    if check_installed; then
      return 0
    fi
    return 1
  fi

  if [ "$UNINSTALL" -eq 1 ]; then
    if [ -f "$OWNERSHIP_MANIFEST" ]; then
      # PD-8: manifest-scoped uninstall (no prompt; the manifest is the
      # explicit record of what this installer owns). Idempotent.
      guard_python3
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
  guard_sources
  guard_staging
  # Review-5 B2: the per-file ownership semantics (stage_owned_file) compare
  # the installed bytes against the LAST install's register — needed for the
  # skills pass too, so load it once here, before anything is deployed.
  load_previous_ownership
  resolve_profile
  # Review-5 B4 (profile invariant / R3-O2): the effective profile must be
  # unambiguous BEFORE anything is deployed or labelled. The staged bytes
  # carry the generation-time profile recorded in the staging manifest; a
  # requested profile that differs is informed HERE (dry-run included) and
  # never published as a contradictory label: the persisted marker records
  # the STAGED profile, so marker == install manifest == staging (a refusal
  # would also be a valid resolution; informing + coherent labels is chosen).
  # R3-O2: the staged bytes are the deployed bytes — the flag alone no longer
  # changes what is installed, so it must not silently change the label.
  local staged_profile=""
  local effective_profile="$MODEL_PROFILE"
  staged_profile="$(staged_header profile)"
  if [ -n "$staged_profile" ] && [ "$MODEL_PROFILE" != "$staged_profile" ]; then
    log "PROFILE MISMATCH: requested profile '$MODEL_PROFILE' differs from the staged profile '$staged_profile' (no coincide — the staged agent bytes were generated with '$staged_profile', R3-O2)"
    log "PROFILE MISMATCH: the effective profile follows staging; the persisted marker records '$staged_profile' (no contradictory labels are published)"
    effective_profile="$staged_profile"
  fi
  install_skills
  install_skills_extra
  install_agents
  # Claude Code targets (guard script; CC agents/skills come from the staged set)
  install_guard_script
  write_profile_marker "$effective_profile"
  INSTALL_VERSION="$(installation_version)"
  write_version_marker "$INSTALL_VERSION"
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
