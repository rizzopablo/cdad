"""Default configuration and constants for CDAD CLI."""

# LLM Model Configuration
DEFAULT_LLM_MODELS = {
    "architect": "claude-opus-4-7",
    "test_writer": "claude-sonnet-4-6",
    "implementer": "claude-sonnet-4-6",
    "reviewer": "claude-sonnet-4-6",
    "scribe": "claude-sonnet-4-6",
}

# Supported Frameworks
SUPPORTED_FRAMEWORKS = ["generic", "odoo", "django"]

# Phase definitions and valid transitions
PHASES = {
    "none": {"next": "discovery", "command": "discover"},
    "discovery": {"next": "spec", "command": "spec"},
    "spec": {"next": "red", "command": "red"},
    "red": {"next": "green", "command": "green"},
    "green": {"next": "review", "command": "review"},
    "review": {"next": "merge", "command": "merge"},
    "merge": {"next": None, "command": None},
}

# Validation rules
ALLOWED_VERIFICATION_METHODS = ["test", "query", "visual", "integration"]

# Vague keywords that should not appear in postcondition descriptions
VAGUE_KEYWORDS = [
    "properly",
    "correctly",
    "appropriate",
    "suitable",
    "good",
    "bad",
]

# File patterns
SPEC_FILES_PATTERN = "docs/specs/*.md"
TEST_FILES_PATTERN = "tests/test_*.py"
MEMORY_BANK_FILE = "AGENTS.md"
DISCOVERY_FILE = "docs/discovery.md"
REVIEW_FILE = ".cdad-review.md"
MERGED_FLAG_FILE = ".cdad-merged"

# Framework detection files
FRAMEWORK_DETECTION = {
    "odoo": ["__manifest__.py", "__openerp__.py"],
    "django": ["manage.py"],
    "generic": ["setup.py", "pyproject.toml"],
}
