Both clean final runs captured. This completes the GREEN task.

---

## Role report — 006-001 T1 GREEN

**Modified files**
- `<repo>/skills/cdad-cycle/scripts/cdad_delegate_opencode.py` (only file touched)
- `cdad_delegate.py`, `OUTPUT_KEYS`, termination vocabulary and the I8 schema are untouched: `git diff 8ec3046..HEAD -- skills/cdad-cycle/scripts/cdad_delegate.py` is empty; `git diff --stat 8ec3046..HEAD` shows only the adapter (8ec3046 = the commit right after the RED commit's state-doc updates, i.e. before this role's work).

**Commits**
- `4bc8934` feat: 006-001 T1 GREEN selección de modo, preflight, procedencia y secretos
- `a96c2d8` feat: 006-001 T1 GREEN compara la versión observada del cliente (§2.3 filas 4-5) — a follow-up fix after a self-review caught two defects no oracle exercised (see below)

**Summary by PD**
- **PD-1/§2.1-§2.2** — `mode` (server|standalone|undeclared) and the five new `wait.*` keys are validated before `REQUEST.json` is even loaded (invalid → `blocked`, nothing invoked, no registration possible). The mode-selection table resolves `mode_effective` (server/standalone/none) with no silent fallback (INV-2): a `server` key present (even syntactically invalid) with `mode` undeclared is treated as an intended server mode, not a silent standalone fallback — an extension of the table beyond its literal rows, driven by INV-2.
- **PD-2/§2.3** — Preflight only in the server effective mode (D-2): `binary --version` (bounded, stdin closed) then `GET /api/info` with Basic auth (password from `OPENCODE_PASSWORD`, else `OPENCODE_SERVER_PASSWORD`, first-present wins even if wrong, never logged), both bounded by `min(preflight_timeout_seconds, remaining budget)`. Maps every row of the table: connection failure → `transport-error`; 401/403 → `blocked` naming both env vars; 404/non-JSON/missing `version` → `blocked`; unparseable observed/server version → `blocked`; version mismatch → `blocked` naming both; an additional mismatch against `binary_version` (when configured and parseable) also blocks, naming both — this is the comparison I initially collapsed into `configured or observed` (a bug: it would have let the real `--version` mismatch pass silently whenever `binary_version` was configured, since all current fixtures declare `binary_version=1.0.0` and no oracle distinguishes the two paths). Fixed in `a96c2d8`: observed-vs-server is always checked first; the `binary_version` check is additional, never a substitute.
- **PD-3/§2.6** — The worker's own attempt is registered in the I8 ledger (`_register_dispatch`, same ledger as the interface's own record) in every termination after `REQUEST.json` loads, not only `completed`. Provenance carries the new pairs in free text: `provenance.runtime` gets `mode_requested=`, `mode_effective=`, `client_version=`, `server_version=`; `provenance.session` gets the literal session-base alternative (`durable session row...` | `chosen by adapter` | `not dispatched`) plus `store=`, `row=` (`present`/`absent`/`unknown`), `store_reads=unknown`, `prior_check_reads=unknown` (exact counting is T2 scope; the test only requires the literal `unknown` or a digit string, INV-9). A registration failure appends `worker record not written: <cause>` to the diagnosis without changing the termination (D-5) — never raises.
- **PD-4** — Unaffected: same-errand assertions (sha256 stdin, `--agent/--session/--model/--auto`, PWD, durable identity, completed→receive pending) hold in server mode too, reusing the untouched dispatch path.
- **PD-5** — URL redaction: a client stderr mentioning the configured server URL is rewritten to the literal `servidor configurado` before entering the `transport-error` diagnosis (exact-substring replacement only — a differently-formatted mention of the same host would not be caught). Password is only ever used to build the Basic header, never logged or placed in argv; URL appears exactly once, in `run`'s argv.

**Four tests the RED commit already reported as able to pass today (declared, not hidden)**: `test_pd1_mode_server_with_valid_url_dispatches_server_flag_only`, `test_pd2_password_order_prefers_first_env_var_when_valid`, `test_pd4_same_errand_in_server_mode`, `test_pd5_no_secrets_in_successful_dispatch_outputs`.

**Other declarations**
- §2.1's minimum-bound check (`timeout_seconds` must exceed `WAIT_RESERVE_SECONDS`) is not implemented here — it's PD-11, assigned to T2.
- An unparseable `binary_version` only skips the extra server-vs-binary_version check (per "y es parseable"); it never blocks by itself.
- In standalone, `client_version` records the raw configured `binary_version` text (not re-parsed), per D-2.
- With an exhausted wait budget, the preflight timeout becomes `0`, which currently surfaces as `transport-error`; this edge belongs to PD-11 (T2).
- Two pre-existing raises (`request has no role`, empty stdin) still exit through `main()` as `blocked` without a worker record — the "every termination after REQUEST.json" scope doesn't reach these two since they raise rather than return.
- The full suite was **not** run (per the full-suite policy: the closer runs it once at T3).

**Exact commands, final lines**
```
$ python3 -m pytest tests/test_006_001_t1_selection.py -q -p no:cacheprovider
..................                                                       [100%]
18 passed in 30.42s

$ python3 -m pytest tests/test_005_009_t1_interface.py tests/test_005_009_t2_opencode_adapter.py tests/test_005_010_t1_durable_signal.py tests/test_005_010_t2_load_mode_invocation.py tests/test_005_010_reviewfix.py tests/test_005_010_b1_last_assistant.py -q -p no:cacheprovider
....................................                                     [100%]
36 passed in 72.57s (0:01:12)
```

**A known timing race surfaced once, reproduced and measured (not fixed, out of T1/T2-scope boundary)**: during one full regression run, `test_005_010_reviewfix.py::TestR3IdleOutcomeEdgeVariants::test_r3_succeeded_without_final_text_is_blocked_without_receipt` failed on its own elapsed-time guard (`2.61s not less than 2`), distinct from the race the packet pre-documented (that one is in `test_005_009_t2`, a different test). Isolated reruns passed 3/3 at ~1.4s each; two subsequent full-suite runs passed 36/36. I measured the cause with a disposable worktree at `8ec3046` (pre-T1): this specific test's `succeeded-no-text` path went from ~1.05-1.09s (no registration call, pre-T1) to ~1.35-1.47s at HEAD (now runs one `prepare --record-dispatch` subprocess, per D-5's "registro en toda terminación"). That is real added latency this task introduces, consistent with spec intent, eating into this test's margin under the shared 2s fixture bound; it only tipped over once, under load. Per the packet's instruction I reported this diagnostically rather than touching `WAIT_RESERVE_SECONDS` or any T2-owned timing (D-3). Flagging for whoever closes T2: its regression list already includes `test_005_010_reviewfix.py`, so it inherits this margin and may want to revisit the 2s fixture bound there.