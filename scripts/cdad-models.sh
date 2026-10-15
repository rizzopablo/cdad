#!/usr/bin/env bash
# CDAD model profiles — single source of the map (duplicates ADR-001/005 and
# the §2 table of the Roles Contract for the optimus profile; the
# economical/premium profiles are deploy opt-in). Sourced by install.sh and
# validate-subagents.sh.
#
# Usage: bash install.sh --economical | --optimus | --premium

# Profiles: economical | optimus | premium
# (anti-bias non-negotiable in all 3: reviewer on a different model from the implementer)
#
# Premium — top-tier configurable via env (multi-provider by design). Each role
# is overridable with an env; without the env, it uses the configured providers'
# top-tier default (mofgw). The env value accepts ANY provider/model format
# (e.g. anthropic/claude-opus-4-5, openai/gpt-5.2-codex) and does NOT carry a
# forced mofgw prefix. Requirement for the override: the target provider must
# be configured in the runtime (e.g. opencode.jsonc).
#
#   CDAD_PREMIUM_MODEL_ARCHITECT    default mofgw/qwen3.7-max
#   CDAD_PREMIUM_MODEL_TEST_WRITER  default mofgw/glm-5.2
#   CDAD_PREMIUM_MODEL_IMPLEMENTER  default mofgw/deepseek-v4-pro
#   CDAD_PREMIUM_MODEL_REVIEWER     default mofgw/qwen3.7-max
#   CDAD_PREMIUM_MODEL_SCRIBE       default mofgw/qwen3.7-max
#
# Example: CDAD_PREMIUM_MODEL_REVIEWER=anthropic/claude-sonnet-4-5
#   (requires having the anthropic provider configured in the runtime).

# cdad_model <profile> <role> → prints "provider/model" (role without match → empty).
# The orchestrator NEVER carries model: → cdad_model returns empty for that role.
# Note: in case patterns, "|" is OR — the literal profile|role separator is escaped
# as "\|" (each alternative is an explicit (profile, role) pair).
cdad_model() {
  local perfil="$1" rol="$2"
  # basic: NO fixed models — agents inherit the runtime's default model
  # (portable across providers; useful when the primary provider is exhausted
  # and you switch to another, or with a single model available). Trade-off
  # documented in ADR-007: the reviewer≠implementer anti-bias is NOT guaranteed
  # by the installer in this profile (manual configuration if needed).
  [ "$perfil" = "basic" ] && return 0
  case "$perfil|$rol" in
    # --- Odoo variants (*-odoo): FIXED models per role (ADR-007), the same in
    # any profile (stack="odoo" in docs/.cdad-state.json delegates to these
    # variants). Placed FIRST on purpose: they are the most specific patterns
    # (exact "-odoo" suffix) and profile-independent, so the order of the
    # generic blocks below is NOT load-bearing — no generic pattern
    # (e.g. *\|reviewer) can shadow them even if the case is reordered.
    *\|architect-odoo)
      echo "mofgw/deepseek-v4-pro";;
    *\|test-writer-odoo)
      echo "mofgw/glm-5.2";;
    *\|implementer-odoo)
      echo "mofgw/deepseek-v4-flash";;
    *\|reviewer-odoo)
      echo "mofgw/qwen3.7-plus";;
    *\|scribe-odoo)
      echo "mofgw/deepseek-v4-pro";;

    # --- economical (2026-08-24 amendment): cheap execution with quality at
    # the critical points — architect moves up to deepseek-v4-pro (spec
    # precision is the cycle's critical load), execution roles on
    # deepseek-v4-flash, reviewer on minimax-m3 (family DIFFERENT from
    # deepseek; replaces qwen3.7-plus — owner's report: recurring failures;
    # minimax-m3 also 25% cheaper: 0.30/1.20 vs 0.40/1.60).
    economical\|architect)
      echo "mofgw/deepseek-v4-pro";;
    economical\|reviewer)
      echo "mofgw/minimax-m3";;
    economical\|test-writer|economical\|implementer|economical\|scribe)
      echo "mofgw/deepseek-v4-flash";;

    # --- optimus (design profile, repo default): mirrors the §2 table of the
    # Roles Contract and ADR-001/005 — architect+scribe deepseek-v4-pro,
    # test-writer glm-5.2, implementer deepseek-v4-flash; reviewer default.
    optimus\|architect|optimus\|scribe)
      echo "mofgw/deepseek-v4-pro";;
    optimus\|test-writer)
      echo "mofgw/glm-5.2";;
    optimus\|implementer)
      echo "mofgw/deepseek-v4-flash";;

    # --- premium: top-tier configurable via env — each role is overridable
    # via CDAD_PREMIUM_MODEL_<ROLE> (any provider/model, e.g.
    # anthropic/openai); without the env, it uses the configured providers'
    # top-tier default (mofgw).
    premium\|architect)
      echo "${CDAD_PREMIUM_MODEL_ARCHITECT:-mofgw/qwen3.7-max}";;
    premium\|test-writer)
      echo "${CDAD_PREMIUM_MODEL_TEST_WRITER:-mofgw/glm-5.2}";;
    premium\|implementer)
      echo "${CDAD_PREMIUM_MODEL_IMPLEMENTER:-mofgw/deepseek-v4-pro}";;
    premium\|reviewer)
      echo "${CDAD_PREMIUM_MODEL_REVIEWER:-mofgw/qwen3.7-max}";;
    premium\|scribe)
      echo "${CDAD_PREMIUM_MODEL_SCRIBE:-mofgw/qwen3.7-max}";;

    # --- reviewer default: qwen3.7-plus in any profile (model different from
    # that profile's implementer; an env override that makes them equal is
    # rejected by the validator's anti-bias guard). Due to the case's
    # first-match rule, placed AFTER the -odoo variants and the explicit
    # profiles: it does not produce a false default for reviewer-odoo (the
    # pattern *\|reviewer does not fully match "…reviewer-odoo").
    *\|reviewer)
      echo "mofgw/qwen3.7-plus";;
  esac
}

# cdad_model_claude <profile> <role> → prints "alias or model-id" for Claude Code.
# Claude Code has no mofgw gateway (only Anthropic-native models), so we
# return aliases (haiku/sonnet/opus/fable).
# Invariant: reviewer ≠ implementer (weakened compared to OpenCode but
# still enforced).
cdad_model_claude() {
  local perfil="$1" rol="$2"
  # basic: NO fixed models — same trade-offs as cdad_model (ADR-007).
  [ "$perfil" = "basic" ] && return 0
  case "$perfil|$rol" in
    # --- Odoo variants (*-odoo) and orchestrator: FIXED models per role, the
    # same in any profile (same criterion as ADR-007 for OpenCode). They go
    # FIRST because the generic patterns below (*\|reviewer, etc.) do NOT
    # fully match "...-odoo", but the explicit order avoids relying on
    # that subtlety.
    *\|architect-odoo|*\|scribe-odoo|*\|test-writer-odoo)
      echo "sonnet";;
    *\|implementer-odoo)
      echo "haiku";;
    *\|reviewer-odoo)
      echo "opus";;
    # The orchestrator coordinates, validates gates and decides: the role that
    # costs the most to be wrong in, and the one that spends the fewest tokens per turn.
    *\|orchestrator)
      echo "opus";;

    # --- economical: haiku for everything except reviewer (which moves up to
    # opus for family diversity). NOTE: in Claude Code, economical|reviewer=haiku breaks
    # the "different family" invariant if combined with economical|implementer=haiku
    # (both are Anthropic models). ADR-008 documents this as an accepted limitation.
    economical\|architect|economical\|test-writer|economical\|implementer|economical\|scribe)
      echo "haiku";;

    # --- optimus (design profile for Claude Code): sonnet architect/scribe
    # (analogous to deepseek-v4-pro, cost-balanced), sonnet test-writer (analogous
    # to specialized glm-5.2), haiku implementer (fast/cheap), opus reviewer
    # (different family, analogous to qwen3.7-plus).
    optimus\|architect|optimus\|scribe|optimus\|test-writer)
      echo "sonnet";;
    optimus\|implementer)
      echo "haiku";;

    # --- premium: opus architect/scribe/reviewer/test-writer (maximum quality
    # in the roles that benefit the most: spec, synthesis, adversarial review,
    # contract tests). implementer on sonnet — NOT opus (bug B2, findings
    # 2026-09-02: opus==opus with the reviewer violated the anti-bias invariant
    # reviewer≠implementer, and the validate-subagents.sh guard did not see it
    # because it only evaluated OpenCode's cdad_model, never cdad_model_claude).
    # sonnet remains top-tier for the role that needs the most expensive model
    # the least (minimal code that makes an already-written test pass).
    premium\|architect|premium\|scribe|premium\|reviewer)
      echo "opus";;
    premium\|implementer)
      echo "sonnet";;
    premium\|test-writer)
      echo "opus";;  # improvement over optimus

    # --- reviewer default: opus (different from implementer in any profile).
    *\|reviewer)
      echo "opus";;
  esac
}

# cdad_valid_profile <profile> → 0 if supported, 1 if not (fail fast at the
# boundary: flag/env/marker). Prints nothing; the caller gives the descriptive message.
cdad_valid_profile() {
  case "$1" in
    economical|optimus|premium|basic) return 0 ;;
    *) return 1 ;;
  esac
}
