(names U6-1, §«sonda V-7», §«006-005 U6: recorrido real»). No implementation code was read; the entry was exercised as a process.

### Modified files (write scope `tests/` only)

- `tests/test_006_005_u6fix1_capabilities_entry.py` — new, 574 lines.

### Test → PD map (one test per numbered postcondition, docstrings name it)

| Test | PD | What it observes |
|---|---|---|
| `TestPd10EntryCapabilities.test_pd10_entry_capabilities_observes_the_declared_runtime_section` | **PD-10** (§2.2/§2.3, O-3) | `capabilities --runtime u6fix` through the ENTRY with a `runtimes.json` section declaring a fake binary (version) and a disposable SQLite store with the V-7 installed schema: answer declares the **observed** version (`u6fix-runtime 7.7.7`, not `unknown`), `session_correlation` true with the store columns, no missing-configuration `reason`, `native_observation` true. |
| `TestPd25MigrationVerification.test_pd25_migrated_section_is_verified_by_entry_capabilities` | **PD-25** (§2.6.1) + PD-10 | E5 walk: `migrate` from a fixture exec-config (`runtime`/`model`/`credential_env_file` + section keys) writes the section, then `capabilities` through the entry verifies what was migrated (observed version + columns). |
| `TestPd9MissingSection.test_pd9_capabilities_without_section_names_the_single_source` | **PD-9** (§2.6, one source) | Without a section `capabilities` fails closed naming `runtimes.json`, the runtime section and the key-by-key correspondence (`binary`, `sessions_db`); and does not write the section (INV-7). |

Fixture interface declared in the file: runtime `u6fix`, module `cdad_delegate_u6fix.py` staged next to the entry; its `--capabilities` **observes** the configuration it receives on the channel the external dispatch already uses (`--exec-config`, an equivalent carrier, or `CDAD_EXEC_CONFIG`), runs `<binary> --version` and reads `PRAGMA table_info(session_v2)`; without configuration it reproduces the U6-1 answer (`version: unknown` + the `sessions_db`/`binary` reason). The store columns are carried inside the five declared keys (§2.2), since the entry validates the document as exactly `native_observation, external_transport, session_correlation, version, reason`.

Why the U1b fixture is not reused (declared in the docstring): its `--capabilities` is a **constant** document that reads no configuration and observes no binary/store — precisely why U1b could not see U6-1; reusing it would hide the defect again.

### Exact commands and output

**Focal (new RED), `python3 -m unittest -v tests.test_006_005_u6fix1_capabilities_entry`** → rc=1, 3 failures, all `AssertionError` (no ImportError/SyntaxError/fixture error):

```
FAIL: test_pd10_entry_capabilities_observes_the_declared_runtime_section
AssertionError: 'unknown' != 'u6fix-runtime 7.7.7'
 : PD-10 (U6-1): `version` no es la versión OBSERVADA del binario configurado
   (se espera 'u6fix-runtime 7.7.7'; `unknown` es el defecto U6-1): 'unknown'

FAIL: test_pd25_migrated_section_is_verified_by_entry_capabilities
AssertionError: 'unknown' != 'u6fix-runtime 7.7.7'
 : PD-25 (U6-1, sección migrada): … (misma causa)

FAIL: test_pd9_capabilities_without_section_names_the_single_source
AssertionError: 0 == 0 : PD-9/§2.6: sin sección del runtime, `capabilities` debe fallar cerrado (rc=0):
{"external_transport": true, "native_observation": false, "reason": "the execution configuration declares no durable
 session store (`sessions_db`) and no destination binary (`binary`)", "session_correlation": false, "version": "unknown"}
Ran 3 tests in 3.295s — FAILED (failures=3)
```

The RFed failure is the right one: the entry never delivers the section to the module, so the fixture observes no binary/store and the entry relays `unknown` + missing-configuration reason — exactly the U6-1 defect. The PD-9 case shows the same defect from the other side: with no section the entry still answers rc=0 instead of the single-source diagnostic.

**Feature focals `tests/test_006_005_*.py` (per file, `python3 -m pytest -q`):**

```
u1a_runtime_config                rc=0  19 passed in 34.53s
u1b_dispatch_entry                rc=0  13 passed in 19.18s
u1c_packet_agent                  rc=0   5 passed in  3.94s
u2_opencode_module                rc=0  19 passed in 25.28s
u3b_derived_temporary_permission  rc=0   6 passed in  3.56s
u3_temporary_scope                rc=0   8 passed in  4.08s
u4_single_entry                   rc=0   7 passed in  2.35s
u5_disposition_failed             rc=0   6 passed in  7.26s
u6fix1_capabilities_entry         rc=1   3 failed in  2.02s   <-- the new RED
u7_scribe_role_report             rc=0   6 passed in 18.50s
```

**Commit (only `tests/`):**

```
$ git add tests/test_006_005_u6fix1_capabilities_entry.py
$ git commit -m "test: 006-005 U6-1 RED — capabilities por la entrada observa la seccion del runtime"
[main ed64092] test: 006-005 U6-1 RED — capabilities por la entrada observa la seccion del runtime
 1 file changed, 574 insertions(+)
 create mode 100644 tests/test_006_005_u6fix1_capabilities_entry.py
HEAD = ed640926ae0fb8e94a57b51928052a37dc29c6a7
```

After the commit `git status --porcelain` shows only the untracked, not-mine paths (`docs/planning/`, `findings/incremental-construction-and-reproducible-validation-2026-10-17.md`). No `--no-verify`, no stash, no push. `tests/.sensitive-patterns.local` was not read; no host values are used (binary, version and store are per-test temporaries).

### Honest limitations / declared deviations

- **Black-box behavior probe (declared).** To learn the shape the entry accepts for a runtime module's capability document, I ran the entry as a process against throwaway fixture modules in `/tmp/opencode` (`nested`, `reason`, `bool`, five-key variants). This is entry behavior, not implementation reading: it showed the document must carry **exactly** the five §2.2 keys, so the observed columns travel inside `session_correlation` (which the contract defines as declaring the keys the observed version exposes and whether the threshold is reached). No product source file was opened.
- **Full suite not run**, per the packet's declared full-suite policy (the closer runs it once at closure). I ran the new focal and the feature's `test_006_005_*.py` set requested by the objective; the listed regressions of the ficha (`test_005_*`, `test_004_002_t4`, `test_006_00*`) were not run in this RED.
- The PD-9 case is a **guard that fails today for the same defect** (capabilities never consults the section); if the intended fix only delivers the section when present and leaves the absent case as `unknown`, that test is the one to re-scope — it is included because the objective explicitly requires the negative PD-9 case through the entry.
- **Expected RED today is complete and behavioral**: the entry exists (U1a), so no failure is a missing verb, an import error or a fixture precondition.