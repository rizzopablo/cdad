"""Tests for ContractValidator (Phase 1: trivial implementation)."""

from cdad.validators.contract_validator import (
    ContractValidator,
    ContractValidationResult,
)
from cdad.validators.spec_validator import Postcondition, SpecValidationResult


def _make_spec(*names: str) -> SpecValidationResult:
    return SpecValidationResult(
        is_valid=True,
        postconditions=[
            Postcondition(name=n, description=f"desc {n}", verification_method="test")
            for n in names
        ],
        errors=[],
    )


class TestContractValidator:
    def test_tests_passed_marks_all_postconditions_satisfied(self):
        spec = _make_spec("returns_sum", "rejects_negatives")
        result = ContractValidator().validate(spec, {"tests_passed": True})

        assert isinstance(result, ContractValidationResult)
        assert result.satisfied == ["returns_sum", "rejects_negatives"]
        assert result.unsatisfied == []

    def test_tests_failed_marks_all_postconditions_unsatisfied(self):
        spec = _make_spec("returns_sum", "rejects_negatives")
        result = ContractValidator().validate(spec, {"tests_passed": False})

        assert result.satisfied == []
        assert result.unsatisfied == ["returns_sum", "rejects_negatives"]

    def test_missing_tests_passed_key_treated_as_failure(self):
        spec = _make_spec("returns_sum")
        result = ContractValidator().validate(spec, {})

        assert result.satisfied == []
        assert result.unsatisfied == ["returns_sum"]

    def test_empty_postconditions_yields_empty_lists(self):
        spec = _make_spec()
        result = ContractValidator().validate(spec, {"tests_passed": True})

        assert result.satisfied == []
        assert result.unsatisfied == []
