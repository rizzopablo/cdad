# Verification and closure (PC-12)

Locators are at revision `64aa4670`. Status: procedure. No review has been run; no result is recorded here.

## 1. The protected checklist

- **Path:** `docs/specs/019-001-discovery-dialogue-contract/review-checklist.md`
- **SHA-256:** `41161a34802e0a4945de042f03b2e65f146c827342d0433079924f3d94a9a83f` (recomputed for this product; the checklist's own recorded discovery digest `6d77f4ba…` matches `discovery.md` as recomputed)
- **Materialization record:** `docs/epics/epic-019-discovery-dialogue/checklist-001-materialize.json`, receipt SHA-256 `c1eca5d4f4f89addc5ca9ab4297b86f6462b1f923102f40e1d978a6146956ab1`. It is kept outside the product directory.
- **Rule:** the producer does not edit the checklist. A necessary correction returns to the independent reviewer. A change to the contract returns to the approval in force (`spec.md`, operating-design declaration).

## 2. The closure handoff

The orchestrator closes verification in this order:

1. Confirms that the product directory contains only the files listed under "Files" in `README.md`, and that the protected inputs are unchanged (by digest).
2. Dispatches an **independent reviewer**: a read-only session that is neither the producer, nor the architect of this design, nor the implementer.
3. Gives the reviewer the product, the protected checklist and the admitted sources, and nothing else that would substitute for the sources.
4. Receives the reviewer's report, materializes it **outside** the product directory, and routes any findings.

The reviewer's independence is the same standard `documentary-contracts.md` §5 sets for the
reviewer role: the reviewer contrasts the product with its contract and its sources, and never
treats the presence of a structure as proof.

## 3. The per-PC result

For **each** of PC-1 to PC-12 the report records:

| Field | Content |
|---|---|
| Result | satisfied / not satisfied / not evidenced |
| Evidence | product locators (`<file>#<section>`) and source locators (`<path>:Lx-Ly` at the examined revision) |
| Examined versions | the product revision, the source revision, and the digests of checklist and spec |
| Findings | what the reviewer found wrong or unclear |
| Missing evidence | what would be needed for the result to be satisfied |
| Limitations and abstentions | what the reviewer did not examine |

**A missing or failed postcondition cannot establish acceptance.** A result of
"not evidenced" blocks acceptance exactly as "not satisfied" does.

## 4. Two records, kept apart

`documentary-contracts.md` §6 requires two separate records. This product keeps them apart:

- **Structural control:** which validation ran (for example `validate-request`, `validate-packet`, `validate-state`, `validate-policy`, `render --route C`), its exit result, the scope it covers and its limits. These checks do not show fidelity.
- **Independent semantic review:** the per-PC result of §3, from the reviewer.

Both records live outside the product directory (`operating-design/`). The orchestrator
chooses their location when it materializes them; this product does not name one.
The checklist's own materialization record, `docs/epics/epic-019-discovery-dialogue/checklist-001-materialize.json`,
is the existing example of a record kept there.

## 5. Acceptance

Acceptance requires **all** of the following:

1. Every PC has result "satisfied" with cited evidence (§3).
2. No unresolved contradiction blocks an unambiguous operating proposal. Contradictions are resolved, not marked pending (`activation-map.md` R4 and R8).
3. The acceptance is **explicit and names its authority**. Either the authorized approver accepts the reviewed design, or the orchestrator accepts it under the sole delegation exception of `roles-and-dialogue.md` §1. That acceptance is valid only when it cites the explicit delegation and falls within its limits. For epic 019 the delegation is `docs/epics/epic-019-discovery-dialogue/execution.md:8-14`, and its limits are: inside `epic-019-discovery-dialogue`, before closure, cancellation or revocation, and without publication or deployment. A reviewer's verdict never approves. An acceptance that names no authority is not accepted.
4. D1–D5 are accepted or amended by the approver (`README.md`, "Proposed decisions").

**Review is not approval.** A "satisfied" result for every PC does not approve the design.

## 6. Failure and change rules

- A failed or missing postcondition is a failure of acceptance, not a limitation to be carried.
- A structural check that passes does not replace a semantic result.
- The producer never reviews its own product.
- A reviewer's abstention is recorded as such, and it does not count as satisfied.

## 7. Limits of this verification

Verification of this product establishes documentary fidelity, internal consistency and an actionable
activation contract. It does **not** establish:

- deployment, or that any instruction is active,
- universal runtime compatibility,
- observed agent compliance (that belongs to `acceptance-protocol-019-002.md`), or
- that 019-002's executable corrections are delivered.

The reviewer's scope is what the reviewer examined. Anything it did not examine is listed as an
abstention.
