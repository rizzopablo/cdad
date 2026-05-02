"""ContractValidator - validates contract postconditions."""

from dataclasses import dataclass
from typing import List

from cdad.validators.spec_validator import SpecValidationResult


@dataclass
class ContractValidationResult:
    """Result of contract validation."""

    satisfied: List[str]
    unsatisfied: List[str]


class ContractValidator:
    """Validates that postconditions are satisfied by implementation."""

    def validate(self, spec: SpecValidationResult, test_results: dict) -> ContractValidationResult:
        """Validate that postconditions are satisfied.

        Phase 1 (MVP) scope: this is a deliberately trivial mapping —
        if the project's test suite passes, every postcondition is reported
        as satisfied; otherwise all are reported as unsatisfied. Real
        per-postcondition contract verification (parameterized property-based
        checks against multiple implementations) is Phase 2 work and will
        replace this body without changing the public signature.

        Args:
            spec: SpecValidationResult with postconditions.
            test_results: Dictionary with test pass/fail status.

        Returns:
            ContractValidationResult with satisfied/unsatisfied postconditions.
        """
        satisfied = []
        unsatisfied = []

        # If tests pass, assume postconditions are met
        if test_results.get("tests_passed", False):
            satisfied = [pc.name for pc in spec.postconditions]
        else:
            # If tests fail, postconditions are not met
            unsatisfied = [pc.name for pc in spec.postconditions]

        return ContractValidationResult(satisfied=satisfied, unsatisfied=unsatisfied)
