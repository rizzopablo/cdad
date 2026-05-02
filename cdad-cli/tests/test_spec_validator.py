"""Tests for SpecValidator - validates specs meet CDAD standards."""

import pytest
from cdad.validators.spec_validator import SpecValidator, Postcondition


class TestSpecValidator:
    """Test SpecValidator validates specs per CDAD standards."""

    def test_accepts_valid_spec_with_postconditions(self, spec_with_postconditions):
        """SpecValidator accepts specs with valid postconditions section."""
        validator = SpecValidator()
        result = validator.validate_file(spec_with_postconditions)

        assert result.is_valid is True
        assert len(result.postconditions) == 2
        assert result.errors == []

    def test_rejects_spec_without_postconditions_section(self, spec_without_postconditions):
        """SpecValidator rejects specs without Postconditions section."""
        validator = SpecValidator()
        result = validator.validate_file(spec_without_postconditions)

        assert result.is_valid is False
        assert "Postconditions" in result.errors[0]

    def test_rejects_spec_with_vague_postcondition(self, spec_with_vague_postcondition):
        """SpecValidator rejects postconditions with vague descriptions."""
        validator = SpecValidator()
        result = validator.validate_file(spec_with_vague_postcondition)

        assert result.is_valid is False
        assert any("vague" in err.lower() for err in result.errors)

    def test_rejects_spec_with_missing_verification_method(self, spec_without_verification_method):
        """SpecValidator rejects postconditions without verification method."""
        validator = SpecValidator()
        result = validator.validate_file(spec_without_verification_method)

        assert result.is_valid is False
        assert any("verification" in err.lower() for err in result.errors)

    def test_extracts_postconditions_into_structured_objects(self, spec_with_postconditions):
        """SpecValidator extracts postconditions into Postcondition objects."""
        validator = SpecValidator()
        result = validator.validate_file(spec_with_postconditions)

        assert len(result.postconditions) == 2

        pc1 = result.postconditions[0]
        assert isinstance(pc1, Postcondition)
        assert pc1.name == "User can login"
        assert pc1.description == "Users should be able to authenticate with valid credentials"
        assert pc1.verification_method == "test"

        pc2 = result.postconditions[1]
        assert pc2.name == "Data is persisted"
        assert pc2.verification_method == "query"

    def test_validates_verification_method_is_allowed_type(self, tmp_path):
        """SpecValidator validates that verification method is one of allowed types."""
        spec_file = tmp_path / "spec.md"
        content = """---
title: Test
---

# Feature Spec

## Postconditions

### Postcondition 1
**Name**: Test postcondition
**Description**: This is a testable postcondition description
**Verification**: invalid_method
"""
        spec_file.write_text(content)

        validator = SpecValidator()
        result = validator.validate_file(spec_file)

        assert result.is_valid is False
        assert any("verification" in err.lower() for err in result.errors)

    def test_handles_yaml_frontmatter(self, tmp_path):
        """SpecValidator correctly parses YAML frontmatter in spec files."""
        spec_file = tmp_path / "spec.md"
        content = """---
title: Feature with frontmatter
author: test
tags:
  - important
  - urgent
---

# Spec

## Postconditions

### Postcondition 1
**Name**: Frontmatter test
**Description**: Test that YAML frontmatter is parsed correctly
**Verification**: test
"""
        spec_file.write_text(content)

        validator = SpecValidator()
        result = validator.validate_file(spec_file)

        assert result.is_valid is True
        assert len(result.postconditions) == 1

    def test_raises_error_on_nonexistent_file(self, tmp_path):
        """SpecValidator raises error when spec file doesn't exist."""
        validator = SpecValidator()
        nonexistent = tmp_path / "nonexistent.md"

        with pytest.raises(FileNotFoundError):
            validator.validate_file(nonexistent)

    def test_validation_result_has_correct_structure(self, spec_with_postconditions):
        """SpecValidator returns SpecValidationResult with expected fields."""
        validator = SpecValidator()
        result = validator.validate_file(spec_with_postconditions)

        assert hasattr(result, "is_valid")
        assert hasattr(result, "postconditions")
        assert hasattr(result, "errors")
        assert isinstance(result.postconditions, list)
        assert isinstance(result.errors, list)
