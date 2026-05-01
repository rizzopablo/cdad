"""CDAD CLI main entry point."""

import typer
from pathlib import Path
from typing import Optional

from cdad.project.model import ProjectModel
from cdad.orchestrator.phase_manager import PhaseManager
from cdad.validators.spec_validator import SpecValidator
from cdad.validators.test_validator import TestValidator

app = typer.Typer(
    name="cdad",
    help="Contract-Driven AI Development CLI - orchestrator for CDAD workflow",
    no_args_is_help=True,
)


@app.command()
def init(
    name: str = typer.Option(..., help="Project name"),
    framework: str = typer.Option("generic", help="Framework (generic, odoo, django)"),
) -> None:
    """Initialize a new CDAD project."""
    project_root = Path.cwd() / name
    project_root.mkdir(exist_ok=True)

    # Create project structure
    (project_root / "docs" / "specs").mkdir(parents=True, exist_ok=True)
    (project_root / "tests").mkdir(exist_ok=True)
    (project_root / "src").mkdir(exist_ok=True)

    typer.echo(f"✓ Initialized CDAD project: {name}")
    typer.echo(f"  Framework: {framework}")
    typer.echo(f"  Location: {project_root}")


@app.command()
def status(path: Optional[Path] = typer.Option(None, help="Project path")) -> None:
    """Show current CDAD phase and next steps."""
    project_root = path or Path.cwd()

    try:
        project = ProjectModel(project_root)
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
    except FileNotFoundError:
        typer.echo("Error: Not a CDAD project", err=True)


@app.command()
def discover(feature: str = typer.Option(..., help="Feature description")) -> None:
    """Start discovery phase."""
    typer.echo(f"Discovering: {feature}")
    typer.echo("(Phase 1: Full architect agent coming soon)")


@app.command()
def spec() -> None:
    """Generate spec from discovery."""
    project_root = Path.cwd()
    try:
        project = ProjectModel(project_root)
        specs = project.list_spec_files()
        typer.echo(f"Specs: {len(specs)} found")
        for spec in specs:
            typer.echo(f"  - {spec.name}")
    except FileNotFoundError:
        typer.echo("Error: Not a CDAD project", err=True)


@app.command()
def red(path: Optional[Path] = typer.Option(None, help="Project path")) -> None:
    """Validate spec and check tests (RED phase)."""
    project_root = path or Path.cwd()

    try:
        project = ProjectModel(project_root)
        specs = project.list_spec_files()

        if not specs:
            typer.echo("No specs found. Run 'cdad spec' first.")
            return

        validator = SpecValidator()
        for spec_file in specs:
            result = validator.validate_file(spec_file)
            if result.is_valid:
                typer.echo(f"✓ {spec_file.name} is valid")
            else:
                typer.echo(f"✗ {spec_file.name} has errors:")
                for error in result.errors:
                    typer.echo(f"  - {error}")
    except FileNotFoundError:
        typer.echo("Error: Not a CDAD project", err=True)


@app.command()
def green(path: Optional[Path] = typer.Option(None, help="Project path")) -> None:
    """Run tests and check status (GREEN phase)."""
    project_root = path or Path.cwd()

    try:
        test_dir = project_root / "tests"

        if not test_dir.exists():
            typer.echo("No tests directory found.")
            return

        validator = TestValidator()
        result = validator.validate(test_dir)

        typer.echo(f"Passed: {result.passed}")
        typer.echo(f"Failed: {result.failed}")
        if result.errors:
            for error in result.errors:
                typer.echo(f"Error: {error}")
    except FileNotFoundError:
        typer.echo("Error: Not a CDAD project", err=True)


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
