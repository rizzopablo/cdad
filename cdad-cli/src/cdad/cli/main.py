"""CDAD CLI main entry point."""

import os
import re
from pathlib import Path
from typing import Optional

import typer

from cdad.agents.architect import ArchitectAgent
from cdad.agents.test_writer import TestWriterAgent
from cdad.config.defaults import DISCOVERY_FILE, MEMORY_BANK_FILE
from cdad.llm.client import LLMClient
from cdad.orchestrator.phase_manager import PhaseManager
from cdad.project.model import ProjectModel
from cdad.validators.spec_validator import (
    SpecValidationError,
    SpecValidator,
)
from cdad.validators.test_validator import TestValidator

app = typer.Typer(
    name="cdad",
    help="Contract-Driven AI Development CLI - orchestrator for CDAD workflow",
    no_args_is_help=True,
)


def _make_llm_client(api_key: str) -> LLMClient:
    """Factory for LLMClient. Monkey-patched in tests."""
    return LLMClient(api_key=api_key)


def _require_api_key() -> Optional[str]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        typer.echo(
            "Error: ANTHROPIC_API_KEY not set. Set it with: export ANTHROPIC_API_KEY=sk-ant-...",
            err=True,
        )
        return None
    return api_key


def _load_project(project_root: Path) -> Optional[ProjectModel]:
    try:
        return ProjectModel(project_root)
    except FileNotFoundError:
        typer.echo("Error: Not a CDAD project", err=True)
        return None


def _slugify(value: str) -> str:
    value = re.sub(r"[^\w\-]+", "-", value.strip())
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "target"


@app.command()
def init(
    name: str = typer.Option(..., help="Project name"),
    framework: Optional[str] = typer.Option(
        None, help="Framework (generic, odoo, django). Auto-detected if omitted."
    ),
) -> None:
    """Initialize a new CDAD project."""
    project_root = Path.cwd() / name
    project_root.mkdir(exist_ok=True)

    (project_root / "docs" / "specs").mkdir(parents=True, exist_ok=True)
    (project_root / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
    (project_root / "tests").mkdir(exist_ok=True)
    (project_root / "src").mkdir(exist_ok=True)

    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        pyproject.write_text(
            f'[project]\nname = "{name}"\nversion = "0.0.1"\nrequires-python = ">=3.10"\n',
            encoding="utf-8",
        )

    agents_md = project_root / MEMORY_BANK_FILE
    if not agents_md.exists():
        agents_md.write_text(
            f"# {name} - Agent Memory Bank\n\nProject-wide context for CDAD agents.\n",
            encoding="utf-8",
        )

    detected = ProjectModel(project_root).framework
    used = framework or detected

    typer.echo(f"✓ Initialized CDAD project: {name}")
    typer.echo(f"  Framework: {used} (detected: {detected})")
    typer.echo(f"  Location: {project_root}")


@app.command()
def status(path: Optional[Path] = typer.Option(None, help="Project path")) -> None:
    """Show current CDAD phase and next steps."""
    project_root = path or Path.cwd()

    project = _load_project(project_root)
    if project is None:
        return

    manager = PhaseManager(project)
    current = manager.current_phase
    next_cmd = manager.suggest_next_command()

    typer.echo(f"Project: {project.name}")
    typer.echo(f"Framework: {project.framework}")
    typer.echo(f"Phase: {current}")
    if next_cmd:
        typer.echo(f"Next step: cdad {next_cmd}")
    else:
        typer.echo("✓ Workflow complete!")


@app.command()
def discover(
    feature: str = typer.Option(..., help="Feature description"),
    path: Optional[Path] = typer.Option(None, help="Project path"),
) -> None:
    """Start discovery phase - architect agent analyzes the feature."""
    project_root = path or Path.cwd()

    project = _load_project(project_root)
    if project is None:
        return

    api_key = _require_api_key()
    if not api_key:
        return

    try:
        llm_client = _make_llm_client(api_key)
        architect = ArchitectAgent(role="architect", project=project, llm_client=llm_client)

        typer.echo(f"🔍 Discovering: {feature}")
        typer.echo(f"   Project: {project.name} ({project.framework})")
        typer.echo("")

        discovery_output = architect.discover(feature)

        docs_dir = project_root / "docs"
        docs_dir.mkdir(exist_ok=True)
        discovery_path = docs_dir / "discovery.md"
        discovery_path.write_text(discovery_output, encoding="utf-8")

        typer.echo(f"✓ Discovery saved to {discovery_path}")
    except Exception as e:
        typer.echo(f"Error during discovery: {e}", err=True)


@app.command()
def spec(
    name: str = typer.Option(..., help="Spec name (e.g., 'user-auth')"),
    path: Optional[Path] = typer.Option(None, help="Project path"),
    retry: int = typer.Option(1, help="Retries if spec validation fails"),
) -> None:
    """Generate spec from discovery."""
    project_root = path or Path.cwd()

    project = _load_project(project_root)
    if project is None:
        return

    api_key = _require_api_key()
    if not api_key:
        return

    discovery_path = project_root / "docs" / "discovery.md"
    if not discovery_path.exists():
        typer.echo("Error: No discovery found. Run 'cdad discover' first.", err=True)
        return

    try:
        llm_client = _make_llm_client(api_key)
        architect = ArchitectAgent(role="architect", project=project, llm_client=llm_client)

        discovery_content = discovery_path.read_text(encoding="utf-8")
        typer.echo(f"📋 Generating spec: {name}")

        specs_dir = project_root / "docs" / "specs"
        specs_dir.mkdir(parents=True, exist_ok=True)
        spec_file = specs_dir / f"{name}.md"
        validator = SpecValidator()

        spec_output = architect.draft_spec(discovery_content)
        spec_file.write_text(spec_output, encoding="utf-8")
        result = validator.validate_file(spec_file)

        attempts = 0
        while not result.is_valid and attempts < retry:
            attempts += 1
            typer.echo(f"⚠ Validation failed (attempt {attempts}/{retry}); asking architect to fix.")
            fix_msg = (
                "The spec you produced has these validation errors:\n"
                + "\n".join(f"- {e}" for e in result.errors)
                + "\n\nReturn a corrected full spec in markdown."
            )
            spec_output = architect.invoke(fix_msg)
            spec_file.write_text(spec_output, encoding="utf-8")
            result = validator.validate_file(spec_file)

        if result.is_valid:
            typer.echo(f"✓ Spec saved to {spec_file}")
            typer.echo(f"✓ Spec is valid ({len(result.postconditions)} postconditions)")
        else:
            typer.echo(f"⚠ Spec saved to {spec_file} but has validation errors:")
            for error in result.errors:
                typer.echo(f"  - {error}")
    except Exception as e:
        typer.echo(f"Error generating spec: {e}", err=True)


@app.command()
def architect(
    target: Path = typer.Argument(..., help="File or directory to analyze"),
    path: Optional[Path] = typer.Option(None, help="Project path"),
) -> None:
    """Analyze existing code and produce architectural recommendations."""
    project_root = path or Path.cwd()

    project = _load_project(project_root)
    if project is None:
        return

    if not target.exists():
        typer.echo(f"Error: Target not found: {target}", err=True)
        return

    api_key = _require_api_key()
    if not api_key:
        return

    try:
        llm_client = _make_llm_client(api_key)
        agent = ArchitectAgent(role="architect", project=project, llm_client=llm_client)

        typer.echo(f"🏗  Analyzing: {target}")
        analysis = agent.analyze(target)
        recommendations = agent.recommend(analysis)

        out_dir = project_root / "docs" / "architecture"
        out_dir.mkdir(parents=True, exist_ok=True)
        slug = _slugify(str(target.relative_to(project_root)) if target.is_absolute() else str(target))
        out_file = out_dir / f"{slug}.md"
        out_file.write_text(
            f"# Architecture review: {target}\n\n"
            f"## Analysis\n\n{analysis}\n\n"
            f"## Recommendations\n\n{recommendations}\n",
            encoding="utf-8",
        )
        typer.echo(f"✓ Recommendations saved to {out_file}")
    except Exception as e:
        typer.echo(f"Error during analysis: {e}", err=True)


@app.command()
def test(
    spec_name: str = typer.Argument(..., help="Spec name (without .md)"),
    path: Optional[Path] = typer.Option(None, help="Project path"),
    force: bool = typer.Option(False, help="Overwrite existing test file"),
) -> None:
    """Generate failing pytest tests from a spec."""
    project_root = path or Path.cwd()

    project = _load_project(project_root)
    if project is None:
        return

    spec_file = project_root / "docs" / "specs" / f"{spec_name}.md"
    if not spec_file.exists():
        typer.echo(f"Error: Spec not found: {spec_file}", err=True)
        return

    api_key = _require_api_key()
    if not api_key:
        return

    out_file = project_root / "tests" / f"test_{spec_name.replace('-', '_')}.py"
    if out_file.exists() and not force:
        typer.echo(f"Error: {out_file} already exists. Use --force to overwrite.", err=True)
        return

    try:
        llm_client = _make_llm_client(api_key)
        agent = TestWriterAgent(role="test_writer", project=project, llm_client=llm_client)

        typer.echo(f"🧪 Generating tests for spec: {spec_name}")
        source = agent.write_tests(spec_file)

        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(source, encoding="utf-8")
        typer.echo(f"✓ Tests saved to {out_file}")
    except SpecValidationError as e:
        typer.echo(f"Error: {e}", err=True)
    except Exception as e:
        typer.echo(f"Error generating tests: {e}", err=True)


@app.command()
def red(path: Optional[Path] = typer.Option(None, help="Project path")) -> None:
    """Validate spec and check tests (RED phase)."""
    project_root = path or Path.cwd()

    project = _load_project(project_root)
    if project is None:
        return

    specs = project.list_spec_files()
    if not specs:
        typer.echo("No specs found. Run 'cdad spec' first.")
        return

    validator = SpecValidator()
    all_valid = True
    for spec_file in specs:
        result = validator.validate_file(spec_file)
        if result.is_valid:
            typer.echo(f"✓ {spec_file.name} is valid ({len(result.postconditions)} postconditions)")
        else:
            all_valid = False
            typer.echo(f"✗ {spec_file.name} has errors:")
            for error in result.errors:
                typer.echo(f"  - {error}")

    if not all_valid:
        typer.echo("\nFix spec errors before proceeding to RED phase.")
        return

    test_files = project.list_test_files()
    if test_files:
        typer.echo(f"\n🧪 Found {len(test_files)} test file(s). Running tests...")
        test_validator = TestValidator()
        result = test_validator.validate(project_root / "tests")
        typer.echo(f"   Passed: {result.passed}")
        typer.echo(f"   Failed: {result.failed}")
        for error in result.errors:
            typer.echo(f"   Error: {error}")
        if result.failed > 0:
            typer.echo("\n✓ RED phase: Tests are failing as expected.")
        else:
            typer.echo("\n⚠ Warning: No failing tests found.")
    else:
        typer.echo("\nNo test files found. Write failing tests first.")


@app.command()
def green(path: Optional[Path] = typer.Option(None, help="Project path")) -> None:
    """Run tests and check status (GREEN phase)."""
    project_root = path or Path.cwd()

    project = _load_project(project_root)
    if project is None:
        return

    test_dir = project_root / "tests"
    if not test_dir.exists():
        typer.echo("No tests directory found.")
        return

    typer.echo("🧪 Running tests...")
    validator = TestValidator()
    result = validator.validate(test_dir)

    typer.echo(f"   Passed: {result.passed}")
    typer.echo(f"   Failed: {result.failed}")
    for error in result.errors:
        typer.echo(f"   Error: {error}")

    if result.failed == 0 and result.passed > 0:
        typer.echo("\n✓ GREEN phase: All tests pass!")
    elif result.failed > 0:
        typer.echo(f"\n⚠ {result.failed} test(s) still failing.")
    else:
        typer.echo("\n⚠ No tests found. Write tests first (RED phase).")


@app.command()
def review() -> None:
    """Review implementation against spec."""
    typer.echo("(Phase 1: Full reviewer agent coming soon)")


@app.command()
def merge() -> None:
    """Merge and update Memory Bank."""
    typer.echo("(Phase 1: Full merge workflow coming soon)")


def main() -> None:
    """Entry point."""
    app()


if __name__ == "__main__":
    main()
