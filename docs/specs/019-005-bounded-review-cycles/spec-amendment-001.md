# Specification amendment 001 — self-contained dispatch

Status: proposed amendment to the approved 019-005 specification, prepared by the
orchestrator under Pablo's instruction of 2026-11-17 that this correction belongs
to the current methodology cycle rather than a new one. Independent review is
required before it replaces anything.

## Problem observed in use

Three consecutive review dispatches of this very feature were blocked at intake.
The shared instruction told the role to locate the installed CLI from the installer
ownership manifest when the runtime reports only the skill id. The manifest lives in
the user's home, outside the product repository, and a confined role cannot read it.
The instruction demanded something the role's own scope denies.

The same family of mistake appeared elsewhere: a relocated child session does not
inherit instruction files loaded from the other directory, and a role cannot read
what the packet does not describe when its scope excludes it.

## Added promise

### Promise E — the dispatch carries everything the role needs

**Property:** a role never has to discover, inherit or guess a resource its unit
requires.

- **PC-11:** the dispatch names every external executable the unit requires, with an
  explicit locator line, together with the product root. A role uses the named path
  and does not resolve it from installation metadata.
- **PC-12:** every required read and write lies within the declared scopes. When a
  required resource falls outside them, the correct outcome is a reported gap, never
  a search, an out-of-scope read or an improvised substitute.
- **PC-13:** the dispatch does not depend on instructions that a runtime loads
  automatically from a directory. Anything required from such a file is carried in
  the packet or in a reference the packet names inside the scopes.
- **PC-14:** when the role session runs in a different directory from the
  orchestrator, the dispatch states the context that is not available, instead of
  letting the role assume it.
- **PC-15:** packaged instructions state the same rule at the sender and receiver
  boundaries: senders include the locator and the scope; receivers report a missing
  required resource and stop.

**Method:** combined. Contextual review of the sender and receiver instructions, plus
a bounded fresh-session check in which a role resolves and uses the required CLI from
the packet alone, with no access to the orchestrator's conversation and no out-of-scope
read.

**Acceptance:** the reviewer finds the rule stated once, consumed at the boundaries
and free of contradictory operational text; the bounded check shows the role invoking
the named CLI and reporting a gap, not improvising, when a required resource is placed
outside its scope.

**Evidence:** cited instruction locations, the dispatch under test, the role's actual
response and any failure preserved.

**Limits:** this does not make a runtime export information the packet omits, does not
create a sandbox and does not prove universal compliance across runtimes.

## Consequence for the plan

The amendment stays inside T1: it touches the same instruction surface already being
changed, adding the sender boundary in the orchestrator source and handoff guidance
and the receiver boundary in the shared role block. No new task, CLI flag, schema
field or counter is introduced.

## Deferred-hardening

- **Automatic verification that a packet names every needed resource:** deferred; it
  would require simulating each role's environment, and the bounded check plus review
  is the declared evidence.
- **Runtime-specific relocation adapters:** unchanged from the base specification.
