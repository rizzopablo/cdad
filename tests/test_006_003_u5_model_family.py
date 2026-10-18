#!/usr/bin/env python3
"""RED tests for 006-003 U5: reviewer/implementer model-family verification.

Contract: docs/specs/006-003-installer-single-profile-delegation-config/spec.md
(approved 2026-10-18) — §2.4 (script de verificación de familia), PD-4a..PD-4e,
INV-5 ("la familia distinta del reviewer … garantizado por configuración o
declarado; nunca silencio"), D2 (no adivinar el modelo) and D4 (aviso, no gate).

Unit: U5 of the approved plan (ficha U5) — the new script
`skills/cdad-cycle/scripts/cdad_model_family.py`, black-box over its CLI.

Fixed minimal interface (the packet authorises pinning exactly this much: "dos
modelos de entrada con su procedencia y una salida legible por máquina con el
veredicto y un texto de declaración"):

    python3 skills/cdad-cycle/scripts/cdad_model_family.py \\
        --implementer <model> [--implementer-provenance <text>] \\
        [--reviewer <model>] [--reviewer-provenance <text>]

stdout is a single JSON object carrying at least:
  "verdict"      -> one of the four declared values:
                    "same-family", "guaranteed-by-configuration",
                    "not-verifiable", "invariant-not-guaranteed"
  "declaration"  -> the statement a reviewer copies into review.md

Omitted `--reviewer` (or an empty value) means "the model is missing".
Exit code is 0 for every comparison outcome (a warning, never a blocking gate);
non-zero is reserved for invalid usage.

Black-box discipline: the script is executed as a subprocess; only its stdout,
its exit code and (for the runtime-independence clause) its own bytes are
inspected as the postcondition's subject. No implementation module is imported
and no implementation source is read as guidance. Provider identifiers used
here are fictitious (`prov/`); the model ids are the spec's own examples.

Mapping (one test per numbered postcondition):

- test_pd_4a_*  -> PD-4a  (same effective model -> "same-family")
- test_pd_4b_*  -> PD-4b  (distinct stems -> "guaranteed-by-configuration";
                            same stem, different ids -> same-family warning,
                            never "guaranteed")
- test_pd_4c_*  -> PD-4c  (missing model -> "invariant-not-guaranteed";
                            Claude Code aliases -> "not-verifiable"; neither
                            case claims the invariant is guaranteed)
- test_pd_4d_*  -> PD-4d  (non-guaranteed cases carry a declaration usable in
                            review.md; the review-gate reference tells the
                            reviewer to run the script and record it)
- test_pd_4e_*  -> PD-4e  (rc=0 in every comparison case; rc!=0 only for
                            invalid usage)
- extra          -> §2.4 runtime independence (no provider names, no model
                            table inside the script)

Expected RED against the current tree (declared, not accidental): the script
`skills/cdad-cycle/scripts/cdad_model_family.py` does not exist yet, so every
test fails on an explicit assertion about the missing behaviour (the script
file, or the declaration text in the review-gate reference); none fails as an
ImportError or a syntax error.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

SCRIPT = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_model_family.py"
SCRIPT_REF = "skills/cdad-cycle/scripts/cdad_model_family.py"

# PD-4d: the review gate reference that must order the check and its
# declaration. "The one the text already uses" — the test accepts either.
REVIEW_REFERENCES = (
    REPO_ROOT / "skills" / "cdad-cycle" / "references" / "stage-4-review.md",
    REPO_ROOT / "skills" / "cdad-cycle" / "references" / "re-entry.md",
)

# The four declared verdicts (§2.4). Anything else is not a declared output.
DECLARED_VERDICTS = {
    "same-family",
    "guaranteed-by-configuration",
    "not-verifiable",
    "invariant-not-guaranteed",
}

# PD-4d: "invariante no garantizado" or its English equivalent.
INVARIANT_NOT_GUARANTEED_RE = re.compile(
    r"invariante\s+no\s+garantizad|invariant\s+not\s+guaranteed",
    re.IGNORECASE,
)

# PD-4b/PD-4c: the *claim* that the invariant is warranted. A statement such as
# "invariante no garantizado" is not a claim; "garantizada por configuración"
# is. The machine verdict is the primary oracle; this is the text-level guard.
GUARANTEE_CLAIM_RE = re.compile(
    r"garantizad[ao]\s+por\s+configurac|guaranteed\s+by\s+configuration",
    re.IGNORECASE,
)

# PD-4b (same stem branch): the output must speak of the *same family*.
SAME_FAMILY_TEXT_RE = re.compile(r"misma\s+familia|same\s+family", re.IGNORECASE)

# §2.4 runtime independence: the script must not embed provider names, and
# therefore no concrete model table either. Claude Code's bare aliases are NOT
# in this list: recognising them (or treating any bare alias as uninterpretable)
# is legitimate behaviour.
PROVIDER_NAMES = (
    "deepseek",
    "glm",
    "qwen",
    "minimax",
    "mofgw",
    "openrouter",
    "anthropic",
    "openai",
    "gemini",
    "mistral",
)

TIMEOUT_S = 30


def _run(args: list[str]) -> subprocess.CompletedProcess:
    """Execute the family script black-box. Missing script = clear assertion."""
    assert SCRIPT.is_file(), (
        f"falta el script de verificación de familia: {SCRIPT_REF} "
        "(§2.4/PD-4a..e)"
    )
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=TIMEOUT_S,
        cwd=str(REPO_ROOT),
    )


def _machine_output(args: list[str]) -> tuple[dict, subprocess.CompletedProcess]:
    """Run the script and return its machine-readable verdict payload.

    Asserts rc=0 (PD-4e: a warning never blocks the gate) and that stdout is a
    single JSON object carrying `verdict` + `declaration`.
    """
    proc = _run(args)
    assert proc.returncode == 0, (
        f"el script debe salir con rc=0 ante un resultado de comparación "
        f"(PD-4e); rc={proc.returncode}; stderr={proc.stderr!r}"
    )
    raw = proc.stdout.strip()
    assert raw, (
        "el script no escribió salida legible por máquina en stdout (§2.4); "
        f"stderr={proc.stderr!r}"
    )
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:  # pragma: no cover - RED path reports it
        raise AssertionError(
            "stdout no es un objeto JSON legible por máquina (§2.4): "
            f"{exc}; salida={raw!r}"
        ) from None
    assert isinstance(payload, dict), (
        f"la salida legible por máquina debe ser un objeto JSON; es {type(payload).__name__}"
    )
    assert "verdict" in payload, (
        f"la salida no trae el veredicto en la clave 'verdict'; claves={sorted(payload)}"
    )
    assert "declaration" in payload, (
        f"la salida no trae el texto de declaración en la clave 'declaration'; "
        f"claves={sorted(payload)}"
    )
    assert isinstance(payload["declaration"], str) and payload["declaration"].strip(), (
        f"el texto de declaración está vacío: {payload['declaration']!r}"
    )
    return payload, proc


def _text(proc: subprocess.CompletedProcess, payload: dict) -> str:
    """Everything a reviewer could read: stdout + stderr."""
    return f"{proc.stdout}\n{proc.stderr}"


class TestPd4aSameEffectiveModel(unittest.TestCase):
    """PD-4a — reviewer and implementer share the same effective model."""

    def test_pd_4a_same_effective_model_is_same_family(self) -> None:
        """PD-4a: same effective model on both sides -> `same-family`."""
        payload, proc = _machine_output(
            [
                "--implementer",
                "prov/fixture-family-alpha",
                "--implementer-provenance",
                "delegation.json:opencode/implementer",
                "--reviewer",
                "prov/fixture-family-alpha",
                "--reviewer-provenance",
                "durable-row:reviewer-model",
            ]
        )
        self.assertEqual(
            payload["verdict"],
            "same-family",
            f"PD-4a: igualdad exacta de strings => 'same-family'; "
            f"salida={payload!r}",
        )
        rendered = _text(proc, payload).lower()
        self.assertIn(
            "delegation.json:opencode/implementer",
            rendered,
            "la procedencia del modelo del implementer debe llegar a la salida (§2.4)",
        )
        self.assertIn(
            "durable-row:reviewer-model",
            rendered,
            "la procedencia del modelo del reviewer debe llegar a la salida (§2.4)",
        )


class TestPd4bDistinctStemsAreGuaranteed(unittest.TestCase):
    """PD-4b — distinct known stems guarantee the invariant by configuration."""

    def test_pd_4b_distinct_stems_are_guaranteed_by_configuration(self) -> None:
        """PD-4b: `deepseek-v4-pro` vs `glm-5.2` -> `guaranteed-by-configuration`."""
        payload, _proc = _machine_output(
            [
                "--implementer",
                "prov/deepseek-v4-pro",
                "--implementer-provenance",
                "delegation.json:opencode/implementer",
                "--reviewer",
                "prov/glm-5.2",
                "--reviewer-provenance",
                "delegation.json:opencode/reviewer",
            ]
        )
        self.assertEqual(
            payload["verdict"],
            "guaranteed-by-configuration",
            f"PD-4b: stems distintos => 'guaranteed-by-configuration'; "
            f"salida={payload!r}",
        )
        self.assertNotRegex(
            payload["declaration"],
            INVARIANT_NOT_GUARANTEED_RE,
            "PD-4b: el caso garantizado no debe declarar el invariante como no garantizado",
        )


class TestPd4bSameStemDifferentIdsWarns(unittest.TestCase):
    """PD-4b (second branch) — same stem with different ids is NOT guaranteed."""

    def test_pd_4b_same_stem_different_ids_warns_same_family(self) -> None:
        """PD-4b: `deepseek-v4-pro` vs `deepseek-v4-flash` -> same-family warning, never guaranteed."""
        payload, proc = _machine_output(
            [
                "--implementer",
                "prov/deepseek-v4-pro",
                "--implementer-provenance",
                "delegation.json:opencode/implementer",
                "--reviewer",
                "prov/deepseek-v4-flash",
                "--reviewer-provenance",
                "delegation.json:opencode/reviewer",
            ]
        )
        verdict = payload["verdict"]
        self.assertIn(
            verdict,
            DECLARED_VERDICTS,
            f"PD-4b: veredicto fuera del conjunto declarado en §2.4: {verdict!r}",
        )
        self.assertNotEqual(
            verdict,
            "guaranteed-by-configuration",
            "PD-4b: el mismo stem con ids distintos NUNCA es 'guaranteed-by-configuration'; "
            f"salida={payload!r}",
        )
        self.assertRegex(
            _text(proc, payload),
            SAME_FAMILY_TEXT_RE,
            "PD-4b: mismo stem => aviso de misma familia en la salida; "
            f"salida={payload!r}",
        )
        self.assertNotRegex(
            _text(proc, payload),
            GUARANTEE_CLAIM_RE,
            "PD-4b: el aviso no puede afirmar que el invariante está garantizado",
        )


class TestPd4cMissingModelIsNotGuaranteed(unittest.TestCase):
    """PD-4c — a missing model means the invariant is not guaranteed."""

    def test_pd_4c_missing_model_is_invariant_not_guaranteed(self) -> None:
        """PD-4c: no reviewer model (omitted or empty) -> `invariant-not-guaranteed`, never "garantizada"."""
        for label, extra in (
            ("flag omitida", []),
            ("valor vacío", ["--reviewer", ""]),
        ):
            with self.subTest(caso=label):
                payload, proc = _machine_output(
                    [
                        "--implementer",
                        "prov/fixture-family-alpha",
                        "--implementer-provenance",
                        "delegation.json:opencode/implementer",
                        *extra,
                    ]
                )
                self.assertEqual(
                    payload["verdict"],
                    "invariant-not-guaranteed",
                    f"PD-4c ({label}): falta un modelo => "
                    f"'invariant-not-guaranteed'; salida={payload!r}",
                )
                text = _text(proc, payload)
                self.assertNotIn(
                    "garantizada",
                    text.lower(),
                    f"PD-4c ({label}): el caso no puede decir «garantizada»; salida={text!r}",
                )
                self.assertNotRegex(
                    text,
                    GUARANTEE_CLAIM_RE,
                    f"PD-4c ({label}): el caso no puede afirmar que el invariante está "
                    "garantizado por configuración",
                )
                self.assertRegex(
                    payload["declaration"],
                    INVARIANT_NOT_GUARANTEED_RE,
                    "PD-4d: la declaración de un caso no garantizado debe decir "
                    "«invariante no garantizado» (o su equivalente inglés); "
                    f"declaración={payload['declaration']!r}",
                )


class TestPd4cClaudeCodeAliasesAreNotVerifiable(unittest.TestCase):
    """PD-4c — bare Claude Code aliases cannot be interpreted."""

    def test_pd_4c_claude_code_aliases_are_not_verifiable(self) -> None:
        """PD-4c: `sonnet` vs `opus` -> `not-verifiable`, never "garantizada"."""
        payload, proc = _machine_output(
            [
                "--implementer",
                "sonnet",
                "--implementer-provenance",
                "claude-code alias",
                "--reviewer",
                "opus",
                "--reviewer-provenance",
                "claude-code alias",
            ]
        )
        self.assertEqual(
            payload["verdict"],
            "not-verifiable",
            f"PD-4c: alias de Claude Code => 'not-verifiable'; salida={payload!r}",
        )
        text = _text(proc, payload).lower()
        self.assertNotIn(
            "garantizada",
            text,
            f"PD-4c: el caso de alias no puede decir «garantizada»; salida={text!r}",
        )
        self.assertNotRegex(
            _text(proc, payload),
            GUARANTEE_CLAIM_RE,
            "PD-4c: el caso de alias no puede afirmar que el invariante está garantizado",
        )
        self.assertRegex(
            payload["declaration"],
            INVARIANT_NOT_GUARANTEED_RE,
            "PD-4d: la declaración del caso no verificable debe decir "
            "«invariante no garantizado» (o su equivalente inglés); "
            f"declaración={payload['declaration']!r}",
        )


class TestPd4dDeclarationIsCopyableIntoReviewMd(unittest.TestCase):
    """PD-4d — the non-guaranteed cases emit a declaration fit for review.md."""

    def test_pd_4d_non_guaranteed_cases_emit_a_single_line_declaration(self) -> None:
        """PD-4d: same-family / not-verifiable / missing model each carry one copyable declaration line."""
        cases = {
            "same-family (igualdad exacta)": [
                "--implementer",
                "prov/fixture-family-alpha",
                "--reviewer",
                "prov/fixture-family-alpha",
            ],
            "not-verifiable (alias)": [
                "--implementer",
                "sonnet",
                "--reviewer",
                "opus",
            ],
            "invariant-not-guaranteed (faltante)": [
                "--implementer",
                "prov/fixture-family-alpha",
            ],
        }
        for label, args in cases.items():
            with self.subTest(caso=label):
                payload, _proc = _machine_output(args)
                declaration = payload["declaration"]
                self.assertNotIn(
                    "\n",
                    declaration.strip(),
                    f"PD-4d ({label}): la declaración debe ser una línea copiable "
                    f"en review.md; declaración={declaration!r}",
                )
                self.assertRegex(
                    declaration,
                    re.compile(r"invariante|invariant", re.IGNORECASE),
                    f"PD-4d ({label}): la declaración debe nombrar el invariante; "
                    f"declaración={declaration!r}",
                )


class TestPd4dReviewGateReferenceMandatesTheCheck(unittest.TestCase):
    """PD-4d — the review-gate reference orders the check and its declaration."""

    def test_pd_4d_review_reference_tells_the_reviewer_to_run_the_script(self) -> None:
        """PD-4d: a review-gate reference names the script, the invariant and review.md (concept oracle)."""
        script_concept = re.compile(
            r"cdad_model_family|model_family|familia del reviewer|reviewer family",
            re.IGNORECASE,
        )
        declaration_concept = re.compile(r"declaraci[oó]n|declaration", re.IGNORECASE)
        invariant_concept = re.compile(r"invariante|invariant", re.IGNORECASE)
        review_md_concept = re.compile(r"review\.md", re.IGNORECASE)

        checked: list[str] = []
        reasons: list[str] = []
        for reference in REVIEW_REFERENCES:
            checked.append(reference.name)
            if not reference.is_file():
                reasons.append(f"{reference.name}: no existe")
                continue
            text = reference.read_text(encoding="utf-8", errors="replace")
            missing = [
                name
                for name, pattern in (
                    ("script de familia", script_concept),
                    ("declaración", declaration_concept),
                    ("invariante", invariant_concept),
                    ("review.md", review_md_concept),
                )
                if not pattern.search(text)
            ]
            if not missing:
                return
            reasons.append(f"{reference.name}: falta {', '.join(missing)}")

        self.fail(
            "PD-4d: ninguna referencia del gate de review indica correr el script "
            f"de familia y registrar la declaración en review.md; revisado={checked}; "
            f"detalle={reasons}"
        )


class TestPd4eWarningNeverBlocksTheGate(unittest.TestCase):
    """PD-4e — every comparison outcome is rc=0; only invalid usage is rc!=0."""

    def test_pd_4e_every_comparison_outcome_exits_zero(self) -> None:
        """PD-4e: five comparison scenarios (all four verdicts) exit 0."""
        scenarios = {
            "same-family": [
                "--implementer",
                "prov/fixture-family-alpha",
                "--reviewer",
                "prov/fixture-family-alpha",
            ],
            "guaranteed-by-configuration": [
                "--implementer",
                "prov/deepseek-v4-pro",
                "--reviewer",
                "prov/glm-5.2",
            ],
            "same stem (aviso)": [
                "--implementer",
                "prov/deepseek-v4-pro",
                "--reviewer",
                "prov/deepseek-v4-flash",
            ],
            "not-verifiable": [
                "--implementer",
                "sonnet",
                "--reviewer",
                "opus",
            ],
            "invariant-not-guaranteed": [
                "--implementer",
                "prov/fixture-family-alpha",
            ],
        }
        for label, args in scenarios.items():
            with self.subTest(escenario=label):
                proc = _run(args)
                self.assertEqual(
                    proc.returncode,
                    0,
                    f"PD-4e ({label}): el resultado es un aviso, no un gate "
                    f"bloqueante; rc={proc.returncode}; stderr={proc.stderr!r}",
                )

    def test_pd_4e_invalid_usage_exits_nonzero(self) -> None:
        """PD-4e: rc!=0 is reserved for invalid usage (unknown option)."""
        proc = _run(["--definitely-not-a-cdad-flag"])
        self.assertNotEqual(
            proc.returncode,
            0,
            "PD-4e: el uso inválido debe salir con rc!=0; "
            f"salida={proc.stdout!r} stderr={proc.stderr!r}",
        )


class TestScriptIsRuntimeIndependent(unittest.TestCase):
    """§2.4 — the script names no provider and embeds no concrete model table."""

    def test_script_names_no_provider_and_has_no_model_table(self) -> None:
        """§2.4: the family script is runtime-independent (no provider names, no model table)."""
        assert SCRIPT.is_file(), (
            f"falta el script de verificación de familia: {SCRIPT_REF} "
            "(§2.4, independiente del runtime)"
        )
        source = SCRIPT.read_text(encoding="utf-8", errors="replace").lower()
        found = sorted({name for name in PROVIDER_NAMES if name in source})
        self.assertEqual(
            found,
            [],
            "§2.4: el script no debe nombrar proveedores ni contener una tabla de "
            f"modelos concretos (es independiente del runtime); encontrado={found}",
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
