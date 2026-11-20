**I withdraw the safe-boundary recommendation.** Migration must preserve open work; finishing, withdrawing or retiring it is not a prerequisite.

## Recommend B: preserve identities, translate physical access

Use one deterministic mapping after migration:

- Historical `.cdad/...` → physical `.cdad-execution/...`.
- Historical `.cdad/project-layout.json` → physical `cdad/project-layout.json`.
- New publications use the new spelling.

Neither mapping probes for an alternative store. `.cdad/` must be absent; hashes continue covering the original persisted bytes.

**A is substantially more invasive:** changing requests requires matching packet re-rendering; changing receipts invalidates authorization hashes; changing checkpoint references requires rehashing bodies and repairing chain links; suspended `resume_checks` then need reconciliation. This is interconnected evidence rewriting, not just updating mutable state. B avoids that cascade.

### Manual steps

Beyond the owner’s three steps:

- Move versioned methodology state/documents into `cdad/` where they currently live elsewhere.
- Update the placement declaration and explicitly declare the finite methodology moves described below.
- Preserve requests, packets, execution contexts, receipts, authorizations, journals, checkpoint bodies and suspension records **without editing their bytes**.
- Prevent concurrent filesystem writes during the physical moves—not completion of the development work. Pending deliveries remain pending and are received afterward.

No new execution, approval or checkpoint is needed merely because a physical location changed.

## Minimum adaptations

Paths below are under `skills/cdad-cycle/scripts/`.

| Area | Physical translation suffices | Additional identity adaptation |
|---|---|---|
| Execution contexts | Shared project-path resolution opens the renamed file. | `_request_locator_path` and canonical-location checks must accept historical spelling resolving to the same execution, with unchanged ID/containment checks (`cdad_packet.py:1670–1700,3366–3385`). New preparation emits only the new spelling. |
| Contracts and approvals | Read contract bytes through the mapping. | Accept the historical packet-local `UNIT-CONTRACT.md` pair; compare admitted contract locations through the mapping. Preserve contract digests and approval-path ownership checks (`2050–2073,3074–3088`). |
| Packet rendering | Keep the request and context dictionaries unchanged. | **Do not normalize them before rendering.** Render already emits their declared locator, contract, scopes, policy and execution values; retain the exact-byte comparison (`2147–2225,2328–2346`). |
| Policy and authority | Read moved policy/authority files through the mapping. | Compare mapped locations for `policy.path` versus selected policy and for equivalent authority locations. Keep execution/state bindings and snapshot/digest checks intact (`1353–1382`). |
| Inbox and materialization | Map `staged_path`, copy targets and allowed destinations before containment checks. | Preserve authorization/journal identity strings and journal keys. `_apply_copy` uses the original `target_rel`; changing it would lose replay recognition (`cdad_result.py:275–305,1005–1018,1116–1137`). |
| Receipts | Existing durable verification already reconstructs payload paths from the physical result directory. | Leave `stored_ref` and receipt bytes unchanged. Authorization and journal hashes remain valid (`cdad_result.py:428–452,742–744,949–962,1054–1066`). |
| Continuity and suspension | Resolve stored reference paths and `resume_checks` keys through the mapper. | Retain stored hashes, checkpoint filenames and links. Missing/changed contract references must still fail (`cdad_continuity.py:1955–1990,2353–2382`; `cdad_packet.py:797–825,1099–1101`). |

This cannot be implemented solely by modifying `_project_path`: continuity also directly joins `root / rel` in `_field_digest`, `_digest_references` and `_reference_digest` (`cdad_continuity.py:518–522,545–562,2297–2304`). Those should call the **same mapping**, not implement separate rules. Result’s `_project_path` and root-relative continuity `_resolve` can compose it. Explicit cwd-relative file arguments must retain their cwd semantics.

## Methodology relocation needs one explicit declaration

Operational-prefix translation is unambiguous. **Arbitrary `docs/` translation is not:** it could redirect unrelated product documents.

Recommend a finite, manually declared old→new methodology move list in the existing placement declaration, with strict validation—not a second store selector or discovery mechanism. It covers moved state/policy/Memory Bank files and explicitly identified methodology-only subtrees. Its exact schema is not proposed here.

This declaration also supports existing custom methodology directories without silently exempting them from the owner’s `cdad/` requirement.

Two important consequences:

- Historical policy scopes need equivalent interpretation over the moved regions. Mapping individual file access alone does not make a frozen `documentation_roots: ["docs"]` classify physical `cdad/...` correctly. Classification and exact-file checks must use the same declared aliases while preserving unrelated `docs/` coverage (`cdad_packet.py:1435–1480`). This is the largest additional adaptation.
- Preserve policy bytes during relocation. Rewriting roots merely to match physical paths would change the accepted policy digest. New policies/publications can use new identities; historical snapshots remain historical.

Thus B is a **bounded but cross-cutting compatibility patch**, not a three-step rename. The methodology relocation requirement—not the operational rename—creates most of its complexity.

## Precise remaining limits

**Instruction snapshots:** requests carrying `instruction_sources` already render from verified frozen bytes. Older requests without snapshots render against live instruction files (`cdad_packet.py:1780–1786,1884–1895`). If this change alters those instruction assets, filesystem mapping cannot guarantee their old packet render remains identical. A finite producer-supplied historical instruction bundle is the alternative; accepting packet text as its own oracle is not.

**Permissions:** generated path guards/agent permissions must recognize mapped physical scopes without widening them. Python filesystem translation alone does not update an already-running worker’s permissions. Supporting old CLI processes that keep writing old physical paths is likewise beyond an upgraded resolver; outstanding results can retain old identities, but their subsequent processing must use the upgraded toolchain.

Recommend one migration guide and a brief shared pre-write diagnostic for an unmigrated `.cdad/`; no converter or new verb. Adapt existing packet, policy, receipt, continuity, suspension and permission tests. Reserve at most two genuinely new migration scenarios; existing integrity protections remain, but do not already prove alias interpretation.

No migration, edits or tests were performed. This is a proposal, not approval.