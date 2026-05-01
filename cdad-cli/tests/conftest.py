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


@pytest.fixture
def temp_odoo_project(tmp_path):
    """Create a temporary Odoo addon project."""
    (tmp_path / "docs" / "specs").mkdir(parents=True)
    (tmp_path / "tests").mkdir(parents=True, exist_ok=True)
    (tmp_path / "models").mkdir(parents=True)
    (tmp_path / "views").mkdir(parents=True)
    # Create __manifest__.py to identify as Odoo addon
    manifest = tmp_path / "__manifest__.py"
    manifest.write_text("""{'name': 'Test Addon', 'version': '14.0.1.0.0', 'depends': ['base']}""")
    return tmp_path


@pytest.fixture
def temp_django_project(tmp_path):
    """Create a temporary Django project."""
    (tmp_path / "docs" / "specs").mkdir(parents=True)
    (tmp_path / "tests").mkdir(parents=True, exist_ok=True)
    (tmp_path / "myapp").mkdir(parents=True)
    # Create manage.py to identify as Django project
    manage_py = tmp_path / "manage.py"
    manage_py.write_text(
        "#!/usr/bin/env python\nfrom django.core.management import execute_from_command_line\n"
    )
    return tmp_path


@pytest.fixture
def temp_generic_project(tmp_path):
    """Create a temporary generic Python project."""
    (tmp_path / "docs" / "specs").mkdir(parents=True)
    (tmp_path / "tests").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src").mkdir(parents=True, exist_ok=True)
    # Create pyproject.toml to identify as generic Python project
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "test-project"\n')
    return tmp_path


@pytest.fixture
def temp_discovery_project(temp_generic_project):
    """Create a temporary project in discovery phase."""
    (temp_generic_project / "docs" / "discovery.md").write_text("# Discovery\nFeature exploration")
    return temp_generic_project


@pytest.fixture
def temp_spec_project(temp_generic_project):
    """Create a temporary project in spec phase."""
    (temp_generic_project / "docs" / "specs" / "feature.md").write_text("""---
title: Test Spec
---

# Spec

## Postconditions

### Postcondition 1
**Name**: Test
**Description**: Test postcondition for feature
**Verification**: test
""")
    return temp_generic_project


@pytest.fixture
def temp_red_project(temp_generic_project):
    """Create a temporary project in red phase (failing tests)."""
    (temp_generic_project / "docs" / "specs" / "feature.md").write_text("""---
title: Test Spec
---

# Spec

## Postconditions

### Postcondition 1
**Name**: Test
**Description**: Test postcondition for feature
**Verification**: test
""")
    # Create a failing test
    (temp_generic_project / "tests" / "test_feature.py").write_text("""
import pytest

def test_feature():
    assert False, "Test not implemented"
""")
    return temp_generic_project


@pytest.fixture
def temp_green_project(temp_generic_project):
    """Create a temporary project in green phase (passing tests)."""
    (temp_generic_project / "docs" / "specs" / "feature.md").write_text("""---
title: Test Spec
---

# Spec

## Postconditions

### Postcondition 1
**Name**: Test
**Description**: Test postcondition for feature
**Verification**: test
""")
    # Create a passing test
    (temp_generic_project / "tests" / "test_feature.py").write_text("""
def test_feature():
    assert True
""")
    return temp_generic_project


@pytest.fixture
def temp_review_project(temp_generic_project):
    """Create a temporary project in review phase."""
    (temp_generic_project / "docs" / "specs" / "feature.md").write_text("""---
title: Test Spec
---

# Spec

## Postconditions

### Postcondition 1
**Name**: Test
**Description**: Test postcondition for feature
**Verification**: test
""")
    (temp_generic_project / ".cdad-review.md").write_text("# Review Report")
    return temp_generic_project


@pytest.fixture
def temp_merge_project(temp_generic_project):
    """Create a temporary project in merge phase."""
    (temp_generic_project / ".cdad-merged").write_text("")
    return temp_generic_project
