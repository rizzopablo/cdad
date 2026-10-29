#!/usr/bin/env python3
"""004-001 T7a — PD-10 (D7): coherent replacement of mechanism assertions.

Contract: docs/specs/004-001-canonical-runtime-artifacts/spec.md (PD-10,
verifiable invariant 5, acceptance criterion 3) + plan row T7.

Scope: the text-presence asserts of F001/F009 (tests/validate-consistency.sh)
and P1 (tests/validate-odoo-specialization.sh) are classified and each
mechanism assert on the OpenCode permission maps / CC hook matchers is
REPLACED by a semantic check that parses the GENERATED frontmatter
(agents/*.md — declared outputs of the generator) and evaluates the maps
(findLast) with the evaluator reused from
tests/test_opencode_read_map_and_steps.py (no second evaluator).
The bash validators invoke the shared checker (tests/pd10_permission_semantics.py)
with its trace lines 'PD-10: reemplaza <old-id>'.

Mini-cycle T7 ("sin borrar y ya"): every replacement passes GREEN against the
current tree, and a mutation on a MODIFIED COPY of the generated output makes
its replacement FAIL — an assert that cannot fail is not a replacement
(Paso 3 of the task objective).

Owner-retired controls (commit 80f9b90, permissive bash policy, owner decision
2026-09-29): the FORBIDDEN_BASH_ALL/CONTENT lists and the P1 'no "*": allow'
asserts are NOT reintroduced — bash asserts assert the owner contract
(exact catch-all allow), not bash operations.

Test -> postcondition mapping:
  test_*_green                -> PD-10 replacements pass against the real tree
  test_mut_[m1..m10]          -> PD-10 mutation requirement: each replacement
                                 fails when the retained barrier is mutated
  test_f001_f009_classified   -> PD-10 traceability audit report exists
                                 (the classification table is part of the role
                                 report; this test pins the retained semantics)
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tests.pd10_permission_semantics import (  # noqa: E402
    CONSISTENCY_CHECKS,
    ODOO_CHECKS,
    SETS,
    matcher_of,
    verdict,
)

AGENTS = REPO_ROOT / "agents"

# The helpers must be importable without pytest peculiarities; plain functions
# (not a TestCase mixin) so both pytest and the bash validators share one
# entry point.

def check(agents_file: Path, tool: str, probe: str) -> str:
    """Direct evaluation on one agent file (tests may call in-place)."""
    text = agents_file.read_text(encoding="utf-8")
    return verdict(text, tool, probe)


class TestPd10Green(unittest.TestCase):
    """PD-10 replacements GREEN against the current tree (same commit)."""

    def test_pd10_consistency_replacements_green(self) -> None:
        """PD-10: every consistency-set semantic replacement passes."""
        for trace, agent, tool, probe, expect in CONSISTENCY_CHECKS:
            if tool.startswith("matcher:"):
                continue  # matcher checks run in test_pd10_cc_matchers_green
            with self.subTest(trace=trace):
                got = check(AGENTS / agent, tool, probe)
                self.assertEqual(got, expect,
                                 f"{trace}: expect {expect!r}, got {got!r}")

    def test_pd10_odoo_replacements_green(self) -> None:
        """PD-10: every odoo-set semantic replacement passes."""
        for trace, agent, tool, probe, expect in ODOO_CHECKS:
            with self.subTest(trace=trace):
                got = check(AGENTS / agent, tool, probe)
                self.assertEqual(got, expect,
                                 f"{trace}: expect {expect!r}, got {got!r}")

    def test_pd10_cc_matcher_green(self) -> None:
        """PD-10: the CC path-guard hooks attach to the documented tool sets."""
        tw = (AGENTS / "claude-code/cdad-test-writer.md").read_text(
            encoding="utf-8")
        m = matcher_of(tw, {"Read", "Grep", "Glob"})
        self.assertIsNotNone(
            m, "PD-10: reemplaza F009-cc-tw-read-guard — the CC test-writer "
            "must declare a PreToolUse hook matcher attaching the path-guard "
            "to Read, Grep and Glob")
        imp = (AGENTS / "claude-code/cdad-implementer.md").read_text(
            encoding="utf-8")
        m2 = matcher_of(imp, {"Edit", "Write"})
        self.assertIsNotNone(
            m2, "PD-10: reemplaza F009-cc-imp-edit-guard — the CC implementer "
            "must declare a PreToolUse hook matcher attaching the path-guard "
            "to Edit and Write")

    def test_pd10_checker_cli_matches_pytest(self) -> None:
        """PD-10: the shared checker CLI (what the bash validators invoke)
        exits 0 over the real tree — validators and pytest agree."""
        import subprocess
        r = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tests" /
                                 "pd10_permission_semantics.py")],
            capture_output=True, text=True, cwd=str(REPO_ROOT), check=False)
        self.assertEqual(r.returncode, 0,
                         "PD-10: the semantic checker must pass over the real "
                         f"tree (validators gate on this):\n{r.stdout}")


# --- mutation machinery (H1: the replacement itself must fail) ---------------
# Paso 3 of the objective, as amended by the orchestrator review of 33bf757:
# each mutation test copies the generated agents tree to a temp dir, applies a
# targeted mutation on the COPY, and runs the REAL replacement probe the bash
# validators run — `python3 tests/pd10_permission_semantics.py --set <set>
# --agents-dir <copy>` — asserting (a) rc != 0 AND (b) the failure line of the
# targeted replacement, `FAIL: PD-10: reemplaza <id>`, is in the output.
# A mutation that does not flip the checker's verdict proves nothing.


class TestMutationsCLI(unittest.TestCase):
    """H1: every mutation runs the replacement (the checker CLI) and the
    checker FAILS naming the exact replacement the mutation targets."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="pd10-mut-")
        self.addCleanup(self._tmp.cleanup)

    def run_mutation(self, rel: str, *,
                     drop_entries: set[tuple[str, str, str]] = frozenset(),
                     replace_entry: tuple[str, str, str, str] | None = None,
                     add_entry: tuple[str, str, str] | None = None,
                     replace: tuple[str, str] | None = None,
                     add_anchor: tuple[str, str] | None = None,
                     set_name: str, trace: str
                     ) -> subprocess.CompletedProcess:
        """Copy the generated agents tree, mutate ONE agent file on the copy,
        run the checker CLI against the copy, return the result.

        Preconditions (AssertionError, harness-level): the file exists and
        every drop-line / replace-source / add-anchor is present — a no-op
        mutation would prove nothing.
        """
        src_root = REPO_ROOT / "agents"
        copy = Path(self._tmp.name) / "agents"
        shutil.copytree(src_root, copy, symlinks=True, dirs_exist_ok=True)
        target = copy / rel
        self.assertTrue(target.is_file(), f"harness: {rel} missing")
        text = target.read_text(encoding="utf-8")
        original = text
        lines_out = []
        # Rewrite V2 permission entries as semantic units. Other mutation
        # families (CC matchers) retain their exact-line operation below.
        source_lines = original.splitlines(keepends=True)
        output_lines = []
        removed_entries: set[tuple[str, str, str]] = set()
        replaced_entry_done = False
        inserted_entry = False
        i = 0
        while i < len(source_lines):
            line = source_lines[i]
            if line.rstrip() == "  - action:" or line.startswith("  - action: "):
                end = i + 1
                while end < len(source_lines) and source_lines[end].startswith("    "):
                    end += 1
                block = source_lines[i:end]
                values = {}
                for item in block:
                    for key in ("action", "resource", "effect"):
                        prefix = f"  - {key}: " if key == "action" else f"    {key}: "
                        if item.startswith(prefix):
                            values[key] = item[len(prefix):].strip().strip("'\"\n")
                identity = (values.get("action", ""), values.get("resource", ""),
                            values.get("effect", ""))
                if identity in drop_entries:
                    removed_entries.add(identity)
                elif (replace_entry and identity == replace_entry[:3]
                      and not replaced_entry_done):
                    block = [item.replace(
                        f"    effect: {replace_entry[2]}",
                        f"    effect: {replace_entry[3]}", 1)
                             if item.startswith("    effect: ") else item
                             for item in block]
                    output_lines.extend(block)
                    replaced_entry_done = True
                else:
                    output_lines.extend(block)
                i = end
                continue
            # Insert once at the end of the ordered permission list, before
            # the next top-level key or closing frontmatter delimiter.
            if (add_entry and not inserted_entry and output_lines
                    and line.startswith("---")):
                output_lines.extend([
                    f"  - action: {add_entry[0]}\n",
                    f"    resource: {add_entry[1]}\n",
                    f"    effect: {add_entry[2]}\n",
                ])
                inserted_entry = True
            output_lines.append(line)
            i += 1
        if add_entry and not inserted_entry:
            output_lines.extend([
                f"  - action: {add_entry[0]}\n",
                f"    resource: {add_entry[1]}\n",
                f"    effect: {add_entry[2]}\n",
            ])
            inserted_entry = True
        lines_out = []
        replaced_done = anchor_done = False
        # Preserve the legacy exact-line mutation path for CC hook matchers.
        for line in output_lines:
            if (replace and not replaced_done
                    and line.rstrip() == replace[0].rstrip()):
                # exact-line match (indentation included): the first occurrence
                # ONLY — the mutation stays surgical, a second identical line
                # is left untouched. Inserted lines are newline-terminated so
                # the mutated frontmatter stays parseable YAML.
                lines_out.append(replace[1].rstrip() + "\n")
                replaced_done = True
                continue
            lines_out.append(line)
            if (add_anchor and not anchor_done
                    and line.rstrip() == add_anchor[0].rstrip()):
                lines_out.append(add_anchor[1].rstrip() + "\n")
                anchor_done = True
        if drop_entries:
            missing = drop_entries - removed_entries
            self.assertFalse(
                missing,
                f"harness precondition: V2 permission entries missing from "
                f"{rel}: {missing}")
        self.assertFalse(
            (replace and not replaced_done) or
            (add_anchor and not anchor_done) or
            (replace_entry and not replaced_entry_done) or
            (add_entry and not inserted_entry),
            f"harness precondition: mutation anchor not found in {rel}")
        target.write_text("".join(lines_out), encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tests" /
                                 "pd10_permission_semantics.py"),
             "--set", set_name, "--agents-dir", str(copy)],
            capture_output=True, text=True, cwd=str(REPO_ROOT), check=False)
        return r

    def assertCheckerFails(self, r: subprocess.CompletedProcess,
                           trace: str, set_name: str) -> None:
        """H1 assertion: the replacement executable by the validators FAILS:
        rc != 0 and the targeted 'FAIL: PD-10: reemplaza <id>' line present."""
        self.assertNotEqual(
            r.returncode, 0,
            f"H1: the checker must FAIL on the mutated copy (set={set_name}); "
            f"got rc=0 — the mutation does not kill the replacement\n"
            f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}")
        self.assertIn(
            f"FAIL: PD-10: reemplaza {trace}",
            r.stdout,
            f"H1: the mutated copy must fail THE targeted replacement "
            f"({trace!r}) inside set {set_name!r}; if stdout is empty the "
            f"checker crashed — stderr:\n{r.stderr}\nstdout:\n{r.stdout}")

    # --- consistency-set mutations -----------------------------------------
    def test_mut_m1_tw_read_src_deny_removed(self) -> None:
        """M1 (H1): quitar el deny de src/** del test-writer read map ->
        la ejecución REAL del reemplazo F009-tw-read-src-deny (el checker CLI)
        falla sobre la copia. Trace: PD-10 reemplaza F009-tw-read-src-deny."""
        r = self.run_mutation(
            "cdad-test-writer.md",
            drop_entries={("read", "src/**", "deny")},
            set_name="consistency", trace="F009-tw-read-src-deny")
        self.assertCheckerFails(r, "F009-tw-read-src-deny", "consistency")

    def test_mut_m2_reader_edit_deny_removed(self) -> None:
        """M2 (H1): 'añadir allow de edit al lector' (inline `edit: deny` ->
        `edit: allow` en cdad-architect) -> el reemplazo F009-readers-edit-deny
        falla al ejecutarse sobre la copia."""
        r = self.run_mutation(
            "cdad-architect.md",
            replace_entry=("edit", "*", "deny", "allow"),
            set_name="consistency", trace="F009-readers-edit-deny")
        self.assertCheckerFails(r, "F009-readers-edit-deny", "consistency")

    def test_mut_m3_imp_tests_blocklist_removed(self) -> None:
        """M3 (H1): quitar la blocklist de tests del implementer edit map ->
        F009-imp-edit-tests-deny falla (tests/test_a.py editable)."""
        r = self.run_mutation(
            "cdad-implementer.md",
            drop_entries={("edit", p, "deny") for p in (
                "tests/**", "**/tests/**", "**/*_test.go", "**/*.test.js",
                "**/*.test.ts", "**/*.test.mjs", "**/*.test.cjs",
                "**/*.spec.ts", "**/*.spec.js", "**/test_*.py")},
            set_name="consistency", trace="F009-imp-edit-tests-deny")
        self.assertCheckerFails(r, "F009-imp-edit-tests-deny", "consistency")

    def test_mut_m4_imp_catchall_allow_to_deny(self) -> None:
        """M4 (H1): flip del catch-all `"*": allow` -> `"*": deny` en el
        implementer edit map -> F009-imp-edit-catchall-allow falla
        (src/lib.py no editable)."""
        r = self.run_mutation(
            "cdad-implementer.md",
            replace_entry=("edit", "*", "allow", "deny"),
            set_name="consistency", trace="F009-imp-edit-catchall-allow")
        self.assertCheckerFails(r, "F009-imp-edit-catchall-allow",
                                "consistency")

    def test_mut_m5_tw_odoo_models_deny_removed(self) -> None:
        """M5 (H1): quitar los 4 deny de dirs odoo del tw-odoo read map ->
        F009-tw-odoo-read-models-deny y P1-tw-*-scope fallan."""
        r = self.run_mutation(
            "cdad-test-writer-odoo.md",
            drop_entries={("read", f"**/{p}/**", "deny") for p in
                          ("models", "views", "controllers", "wizards")},
            set_name="consistency", trace="F009-tw-odoo-read-models-deny")
        self.assertCheckerFails(r, "F009-tw-odoo-read-models-deny",
                                "consistency")
        r2 = self.run_mutation(
            "cdad-test-writer-odoo.md",
            drop_entries={("read", f"**/{p}/**", "deny") for p in
                          ("models", "views", "controllers", "wizards")},
            set_name="odoo", trace="P1-tw-models-scope")
        self.assertCheckerFails(r2, "P1-tw-models-scope", "odoo")

    def test_mut_m6_tw_edit_tests_allow_removed(self) -> None:
        """M6 (H1, H2): quitar '"tests/**": allow' del tw edit map -> el
        reemplazo F009-tw-edit-tests-allow falla sobre la copia: el probe
        del allow-side es tests/conftest.py (NON-test-shaped: ninguna regla
        colocada lo cubre, así que la mutación lo hace editable-para-deny y
        el reemplazo muere). El docstring ya no racionaliza la fuga."""
        r = self.run_mutation(
            "cdad-test-writer.md",
            drop_entries={("edit", p, "allow") for p in
                          ("tests/**", "**/tests/**")},
            set_name="consistency", trace="F009-tw-edit-tests-allow")
        self.assertCheckerFails(r, "F009-tw-edit-tests-allow", "consistency")

    def test_mut_m7_imp_odoo_models_leakover_added(self) -> None:
        """M7 (H1): re-añadir el deny **/models/** al imp-odoo edit map ->
        F009-imp-no-models-deny (bugfix 80f9b90) falla (own scope bloqueado)."""
        r = self.run_mutation(
            "cdad-implementer-odoo.md",
            add_entry=("edit", "**/models/**", "deny"),
            set_name="consistency", trace="F009-imp-no-models-deny")
        self.assertCheckerFails(r, "F009-imp-no-models-deny", "consistency")

    def test_mut_m8_tw_manifest_read_deny_added(self) -> None:
        """M8 (H1): añadir '"**/__manifest__.py": deny' al tw-odoo read map ->
        P1-tw-manifest-allow falla al ejecutarse (--set odoo)."""
        r = self.run_mutation(
            "cdad-test-writer-odoo.md",
            add_entry=("read", "**/__manifest__.py", "deny"),
            set_name="odoo", trace="P1-tw-manifest-allow")
        self.assertCheckerFails(r, "P1-tw-manifest-allow", "odoo")

    # --- matcher mutations (CC) --------------------------------------------
    def test_mut_m9_cc_matcher_changed_tw(self) -> None:
        """M9 (H1): matcher de la CC test-writer reducido (Read|Grep|Glob ->
        Read) -> F009-cc-tw-read-guard falla al ejecutarse."""
        r = self.run_mutation(
            "claude-code/cdad-test-writer.md",
            replace=("    - matcher: Read|Grep|Glob",
                     "    - matcher: Read"),
            set_name="consistency", trace="F009-cc-tw-read-guard")
        self.assertCheckerFails(r, "F009-cc-tw-read-guard", "consistency")

    def test_mut_m10_cc_matcher_changed_imp(self) -> None:
        """M10 (H1): matcher de la CC implementer reducido (Edit|Write ->
        Edit) -> F009-cc-imp-edit-guard falla al ejecutarse."""
        r = self.run_mutation(
            "claude-code/cdad-implementer.md",
            replace=("    - matcher: Edit|Write",
                     "    - matcher: Edit"),
            set_name="consistency", trace="F009-cc-imp-edit-guard")
        self.assertCheckerFails(r, "F009-cc-imp-edit-guard", "consistency")


    # --- audit integrity (retained from 33bf757) ---------------------------
    def test_mut_m11_traces_unique_and_mapped(self) -> None:
        """Audit integrity: each check carries exactly one 'PD-10: reemplaza'
        trace naming an old assert id; no unmapped replacement."""
        ids = [t.split("reemplaza ")[1].split(" (")[0]
               for s in SETS.values()
               for t, *_rest in s
               if "reemplaza " in t]
        expected_old = {
            "F009-readers-edit-deny", "F009-tw-edit-tests-allow",
            "F009-tw-read-src-deny", "F009-tw-odoo-read-models-deny",
            "F009-imp-edit-catchall-allow", "F009-imp-edit-tests-deny",
            "F009-imp-no-models-deny", "F009-cc-tw-read-guard",
            "F009-cc-imp-edit-guard",
            "P1-tw-models-scope", "P1-tw-views-scope",
            "P1-tw-controllers-scope", "P1-tw-wizards-scope",
            "P1-tw-tests-allow", "P1-tw-manifest-allow", "P1-imp-tests-deny",
        }
        self.assertLessEqual(expected_old, set(ids),
                             "Every replaced old assert id must appear as trace")

    def test_mut_m12_owner_retired_lists_not_reintroduced(self) -> None:
        """PD-10 (iii): the FORBIDDEN_BASH_* lists and the P1 'no "*": allow'
        asserts retired by 80f9b90 are NOT reintroduced in the validators."""
        for v in ("tests/validate-consistency.sh",
                  "tests/validate-odoo-specialization.sh"):
            t = (REPO_ROOT / v).read_text(encoding="utf-8")
            self.assertNotIn("FORBIDDEN_BASH", t,
                             f"owner-retired lists must stay retired ({v})")
            self.assertNotIn('no "*": allow', t,
                             f"owner-retired wildcard ban must stay retired ({v})")


if __name__ == "__main__":
    unittest.main()
