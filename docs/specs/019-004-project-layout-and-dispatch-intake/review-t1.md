## Review: T1 project-layout resolution

**Result:** no blocking finding established for the reviewed T1 scope. The additional realpath-equals-root guard is a contract mismatch worth resolving, but I do not have evidence of a realistic affected project that warrants making it blocking.

### Optional — root-resolving symlink is rejected beyond the stated contract

**Verdict: OPTIONAL · Bucket: l**  
**Location:** `skills/cdad-cycle/scripts/cdad_layout.py:136–137`

A normalized relative locator such as `alias`, where `alias` is a symlink to the repository root, passes the specification’s listed path restrictions: it does not escape the root, is not under `.cdad/`, and resolves to an existing directory. The implementation nevertheless rejects it.

The guard is defensible as a design precaution, but it adds a restriction not stated in §4.1. **Remedy:** either remove it, or explicitly decide that methodology placement at the repository root is unsupported and amend the contract accordingly. Add a focused test for whichever behavior is decided.

## Closure evidence

- **PC-01, PC-02, PC-04:** Supported within the exercised limits, except for the additional restriction noted above. The tests cover registered-layout precedence, exact legacy signals, ambiguity, ordinary documentation, and representative invalid locators without writes.
- **PC-08, resolution:** Supported within the exercised limits for explicit roots, invocation directories, repository names and a symlinked root.
- **PC-09, resolution:** Supported within the exercised limits; broader file-argument and dispatch-declaration behavior is outside this T1 review.
- **Placement versus operational validation:** Supported within the exercised limits: missing or invalid operational artifacts do not prevent placement resolution.
- **Read-only behavior:** Supported for the tested filesystem scenarios; this is not a proof for every filesystem failure mode.

## Verification and scope

- Reviewed implementation commit **`22b75b87`**: `skills/cdad-cycle/scripts/cdad_layout.py` and `skills/cdad-cycle/scripts/cdad_packet.py`. The focused test file was introduced separately in **`03246f47`**.
- Ran `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_019_004_layout -v`: **7 tests passed**.
- Validated the named Route C request and published packet and compared the rendered identification with the dispatch.
- No product files were modified by this review. The pre-existing working-tree change was `docs/.cdad-state.json`.
- The complete suite was not run; this was a focused T1 review.

## Abstentions

- The current-decisions table references existing ADR files, but several ADR files are absent from the table. I did not establish their current status or whether each omission is inconsistent; that requires a separate comparison of those ADRs’ statuses.
- I did not verify the implementer’s original test-run output or independently establish sensitivity/RED evidence. The passing run above is this review’s own verification.