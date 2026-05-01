"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary CDAD project structure."""
    (tmp_path / "docs" / "specs").mkdir(parents=True)
    (tmp_path / "tests").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src").mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def spec_with_postconditions(tmp_path):
    """Create a valid spec file with postconditions."""
    spec_file = tmp_path / "spec.md"
    content = """---
title: Test Feature
description: A test feature for CDAD
---

# Feature Spec

## Discovery
This feature does X, Y, Z.

## Postconditions

### Postcondition 1
**Name**: User can login
**Description**: Users should be able to authenticate with valid credentials
**Verification**: test

### Postcondition 2
**Name**: Data is persisted
**Description**: User data must be saved to database after creation
**Verification**: query
"""
    spec_file.write_text(content)
    return spec_file


@pytest.fixture
def spec_without_postconditions(tmp_path):
    """Create an invalid spec file without postconditions section."""
    spec_file = tmp_path / "spec.md"
    content = """---
title: Test Feature
description: A test feature without postconditions
---

# Feature Spec

## Discovery
This feature does X, Y, Z.
"""
    spec_file.write_text(content)
    return spec_file


@pytest.fixture
def spec_with_vague_postcondition(tmp_path):
    """Create an invalid spec with vague postcondition description."""
    spec_file = tmp_path / "spec.md"
    content = """---
title: Test Feature
---

# Feature Spec

## Postconditions

### Postcondition 1
**Name**: Feature works
**Description**: The feature should work properly
**Verification**: test
"""
    spec_file.write_text(content)
    return spec_file


@pytest.fixture
def spec_without_verification_method(tmp_path):
    """Create spec with postcondition missing verification method."""
    spec_file = tmp_path / "spec.md"
    content = """---
title: Test Feature
---

# Feature Spec

## Postconditions

### Postcondition 1
**Name**: User login
**Description**: Users can authenticate with valid credentials
"""
    spec_file.write_text(content)
    return spec_file
