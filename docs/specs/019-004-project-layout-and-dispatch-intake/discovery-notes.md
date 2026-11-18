# Discovery — project layout and dispatch intake

Status: scope approved by Pablo on 2026-11-16; specification not drafted or
approved. Planned next cycle of epic-019-discovery-dialogue, after closure of
019-002. This note opens discovery only, not an execution or implementation.

## Owner decisions

The owner requests `cdad/` as the default home of methodology documents, leaving
`docs/` for end-user documentation; product-repository-relative paths independent
of the coordinator's current directory; and analysis of a single-command role
intake replacing repeated manual validation steps. Repository directory names
are arbitrary. The owner explicitly approved adding this cycle to the same epic.

## Attributed technical observations

The orchestrator inspected current product code and actual role-session tool
records before this amendment:

- `skills/cdad-cycle/scripts/cdad_packet.py` defines `STATE_RELPATH_TEXT` as
  `docs/.cdad-state.json`, and its render/validation CLI also loads that path
  directly. This is executable behavior, not only a documentation convention.
- `validate-packet` resolves execution context, calls `validate_request`
  (which calls `validate_state`), renders canonically, and compares packet bytes.
  Separate calls to those validators repeat part of the same work.
- Review sessions for packets reviewer-review-014 and reviewer-review-015 in
  019-002 read metadata, discovered the CLI/help, invoked validate-request and
  validate-packet, then rendered Route C identification. The scribe-memory-002
  session similarly rediscovered the command and rendered identification.
  Source: read-only inspection of those native session transcripts.
- A valid file on disk does not establish that the role received that file or
  identification unchanged. Simplification must retain that distinction.
- The nested-root example now documented in `sub-agent-strategies.md` moves only
  an initialization-only native child before delivering the canonical packet.
  It depends on the runtime's relocation capability and is not a sandbox.

## Owner clarification — existing projects (2026-11-16)

Pablo explicitly confirmed that existing projects must not be moved or changed:
the orchestrator must use the directories registered in project metadata.
`cdad/` replaces `docs/` only as the default for new projects. No automatic
migration is commissioned. Continue development under the existing epic mandate.
Pablo also confirmed that the methodology directory is a per-project configured
value, not a global fixed constant, resolved relative to the product repository
root. Existing metadata compatibility and any absence of a registered value must
be determined from the actual product.

## Proposals requiring specification, not inferred owner decisions

- Prefer a shared path resolver rather than replacing scattered hardcoded paths.
- Preserve existing projects' registered directories, including historical
  references and hashes. Determine the current metadata source and the minimum
  resolution needed; no migration feature is commissioned.
- Preserve `.cdad/` operational storage unless a separate need is demonstrated.
- Compose existing validators behind an intake command; do not create parallel
  validation logic. Resolve the installed command without requiring roles to
  search the product checkout or rediscover CLI help.
- Determine how exact received bytes/identification reach the command, what it
  returns, and how admitted legacy cases are handled. Do not promise that a
  boolean validating stored files proves delivery, semantic acceptance or
  effective filesystem permissions.
- Distinguish methodology artifacts of a project from end-user documentation of
  CDAD itself; do not indiscriminately move all repository `docs/` content.

## Next boundary

Close 019-002 with its completed suite evidence before opening the new execution.
Then obtain targeted architect analysis and a reviewed specification/plan under
the existing epic mandate. No product, tests, historical packets or active state
paths are changed by these notes. No fixed test quota, additional role or new
approval gate is proposed.
