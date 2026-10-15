#!/usr/bin/env python3
"""RED tests for 004-001 T3 PD-19: the static-block byte ceiling becomes policy.

The 12,000-byte ceiling of the packet's static-instruction block
(`skills/cdad-cycle/scripts/cdad_packet.py:411-412`, hardcoded `12_000`) must
become a declared policy parameter — environment variable
`CDAD_STATIC_BLOCK_LIMIT`, default 12000 — and exceeding it must produce an
explicit error with a short diagnostic and NO mixed output.

Uses the existing public packet fixtures (tests.test_role_packet_render).
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from tests.test_role_packet_render import PacketFixture

CEILING_ENV = "CDAD_STATIC_BLOCK_LIMIT"
DEFAULT_CEILING_BYTES = 12000
LOWER_CEILING = "512"  # safely below every static block measured in baseline.json
CEILING_TOKENS = ("static", "limit", "ceiling", "byte")


class TestStaticBlockCeilingParameterized(unittest.TestCase):
    def test_postcondition_19_default_ceiling_renders_normally(self) -> None:
        """PD-19 (a): without the env var the behavior is unchanged (renders)."""
        self.assertNotIn(
            CEILING_ENV,
            os.environ,
            "test hygiene: %s leaked into the environment and voids the default-path check" % CEILING_ENV,
        )
        with tempfile.TemporaryDirectory(prefix="cdad-t3-ceiling-default-") as tmp:
            fixture = PacketFixture(Path(tmp), "test-writer", "red")
            fixture.write()
            result = fixture.render()
            self.assertEqual(
                result.returncode,
                0,
                "PD-19: the default ceiling (12000) must keep rendering normally: %s" % result.stderr,
            )
            self.assertTrue(
                result.stdout.startswith("---cdad-packet-json\n"),
                "PD-19: a render under the default ceiling lost the packet delimiters",
            )

    def test_postcondition_19_lowered_ceiling_fails_explicitly_without_mixed_output(self) -> None:
        """PD-19 (b): a lowered ceiling + a block over it → explicit error, no mixing."""
        with tempfile.TemporaryDirectory(prefix="cdad-t3-ceiling-lowered-") as tmp:
            fixture = PacketFixture(Path(tmp), "test-writer", "red")
            fixture.write()
            os.environ[CEILING_ENV] = LOWER_CEILING
            try:
                result = fixture.render()
            finally:
                os.environ.pop(CEILING_ENV, None)
            self.assertNotEqual(
                result.returncode,
                0,
                "PD-19: the ceiling was ignored — %s is not respected as a policy parameter" % CEILING_ENV,
            )
            self.assertTrue(
                result.stderr.strip(),
                "PD-19: exceeding the lowered ceiling lacked a diagnostic",
            )
            self.assertTrue(
                any(token in result.stderr.lower() for token in ("static", "limit", "ceiling", "byte")),
                "PD-19: the diagnostic does not name the ceiling problem",
            )
            self.assertEqual(
                result.stdout,
                "",
                "PD-19: exceeding the ceiling produced mixed output (stdout must stay empty)",
            )


if __name__ == "__main__":
    unittest.main()
