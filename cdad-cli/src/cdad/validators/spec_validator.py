"""Validator for spec files - ensures specs meet CDAD standards."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import frontmatter
import re

from cdad.config import ALLOWED_VERIFICATION_METHODS, VAGUE_KEYWORDS


@dataclass
class Postcondition:
    """Represents a validated postcondition from a spec."""

    name: str
    description: str
    verification_method: str


@dataclass
class SpecValidationResult:
    """Result of spec validation."""

    is_valid: bool
    postconditions: List[Postcondition]
    errors: List[str]


class SpecValidationError(Exception):
    """Raised when spec validation fails."""

    pass


class SpecValidator:
    """Validates that specs conform to CDAD standards."""

    def validate_file(self, path: Path) -> SpecValidationResult:
        """Validate a spec file.

        Args:
            path: Path to the spec markdown file.

        Returns:
            SpecValidationResult with validation status and postconditions.

        Raises:
            FileNotFoundError: If spec file doesn't exist.
        """
        if not path.exists():
            raise FileNotFoundError(f"Spec file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        errors = []
        postconditions = []

        # Check for Postconditions section
        postconditions_section = self._extract_postconditions_section(post.content)
        if postconditions_section is None:
            errors.append("Missing required '## Postconditions' section in spec")
            return SpecValidationResult(is_valid=False, postconditions=[], errors=errors)

        # Extract and validate postconditions
        postconditions, extraction_errors = self._extract_postconditions(postconditions_section)
        errors.extend(extraction_errors)

        # Ensure at least one postcondition was parsed
        if len(postconditions) == 0 and len(extraction_errors) == 0:
            errors.append(
                "No postconditions found in '## Postconditions' section. "
                "Must define at least one '### Postcondition ...' block"
            )

        is_valid = len(errors) == 0
        return SpecValidationResult(is_valid=is_valid, postconditions=postconditions, errors=errors)

    def _extract_postconditions_section(self, content: str) -> Optional[str]:
        """Extract the Postconditions section from markdown content.

        Args:
            content: Markdown content without frontmatter.

        Returns:
            Content of Postconditions section, or None if not found.
        """
        # Match ## Postconditions section - need \n## to avoid false positives
        pattern = r"## Postconditions(.*?)(?=\n## |\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def _extract_postconditions(
        self, section_content: str
    ) -> tuple[List[Postcondition], List[str]]:
        """Extract individual postconditions from section content.

        Args:
            section_content: Content of the Postconditions section.

        Returns:
            Tuple of (list of Postcondition objects, list of errors).
        """
        postconditions = []
        errors = []

        # Split by ### Postcondition lines
        postcondition_blocks = re.split(r"### Postcondition \d+", section_content)
        postcondition_blocks = [block.strip() for block in postcondition_blocks if block.strip()]

        for block in postcondition_blocks:
            pc, pc_errors = self._parse_postcondition_block(block)
            if pc_errors:
                errors.extend(pc_errors)
            elif pc:
                postconditions.append(pc)

        return postconditions, errors

    def _parse_postcondition_block(self, block: str) -> tuple[Optional[Postcondition], List[str]]:
        """Parse a single postcondition block.

        Args:
            block: Content of a single postcondition block.

        Returns:
            Tuple of (Postcondition object or None, list of errors).
        """
        errors = []

        # Extract name
        name_match = re.search(r"\*\*Name\*\*:\s*(.+?)(?:\n|$)", block)
        if not name_match:
            errors.append("Postcondition missing **Name** field")
            return None, errors

        name = name_match.group(1).strip()

        # Extract description
        desc_match = re.search(r"\*\*Description\*\*:\s*(.+?)(?=\*\*|$)", block, re.DOTALL)
        if not desc_match:
            errors.append(f"Postcondition '{name}' missing **Description** field")
            return None, errors

        description = desc_match.group(1).strip()

        # Check for vague descriptions
        if self._is_vague_description(description):
            errors.append(
                f"Postcondition '{name}' has vague description: '{description}'. "
                "Use specific, testable descriptions (e.g., 'User can login with valid credentials')"
            )

        # Extract verification method
        verif_match = re.search(r"\*\*Verification\*\*:\s*(.+?)(?:\n|$)", block)
        if not verif_match:
            errors.append(
                f"Postcondition '{name}' missing **Verification** field. "
                f"Must be one of: {', '.join(ALLOWED_VERIFICATION_METHODS)}"
            )
            return None, errors

        verification_method = verif_match.group(1).strip().lower()

        # Validate verification method
        if verification_method not in ALLOWED_VERIFICATION_METHODS:
            errors.append(
                f"Postcondition '{name}' has invalid verification method '{verification_method}'. "
                f"Must be one of: {', '.join(ALLOWED_VERIFICATION_METHODS)}"
            )

        if errors:
            return None, errors

        return (
            Postcondition(
                name=name, description=description, verification_method=verification_method
            ),
            [],
        )

    def _is_vague_description(self, description: str) -> bool:
        """Check if description uses vague language.

        Args:
            description: Description text to check.

        Returns:
            True if description is vague, False otherwise.
        """
        description_lower = description.lower()
        words = description.split()

        # Pattern 1: Very short descriptions with vague keywords (2-3 words total)
        # e.g., "works properly", "is correct"
        if len(words) <= 3:
            for keyword in VAGUE_KEYWORDS:
                if keyword in description_lower:
                    return True

        # Pattern 2: Vague verb combinations anywhere in description
        # Matches patterns like "works properly", "should work properly", etc.
        vague_patterns = [
            r"(work|function|operate|run)s?\s+\w*\s*(properly|correctly|well|fine)",
            r"should\s+(work|function|operate)(\s+\w+)*\s+(properly|correctly|well|fine)",
            r"^should\s+(work|function|operate)",
        ]
        for pattern in vague_patterns:
            if re.search(pattern, description_lower):
                return True

        return False
