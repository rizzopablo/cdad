"""CDAD CLI main entry point."""

import typer
from pathlib import Path
from typing import Optional

app = typer.Typer(
    name="cdad",
    help="Contract-Driven AI Development CLI",
    no_args_is_help=True,
)


@app.command()
def init(
    name: str = typer.Option(..., help="Project name"),
    framework: str = typer.Option("generic", help="Framework (generic, odoo, django)"),
) -> None:
    """Initialize a new CDAD project."""
    typer.echo(f"Initializing CDAD project: {name}")
    typer.echo(f"Framework: {framework}")
    typer.echo("✓ Project initialized")


@app.command()
def status(path: Optional[Path] = typer.Option(None, help="Project path")) -> None:
    """Show current CDAD phase and next steps."""
    project_root = path or Path.cwd()
    typer.echo(f"Project root: {project_root}")
    typer.echo("Status command - to be implemented")


@app.command()
def discover(feature: str = typer.Option(..., help="Feature description")) -> None:
    """Start discovery phase."""
    typer.echo(f"Discovering: {feature}")
    typer.echo("Discover command - to be implemented")


@app.command()
def spec() -> None:
    """Generate spec from discovery."""
    typer.echo("Generating spec from discovery...")
    typer.echo("Spec command - to be implemented")


@app.command()
def red() -> None:
    """Write tests (RED phase)."""
    typer.echo("Entering RED phase...")
    typer.echo("Red command - to be implemented")


@app.command()
def green() -> None:
    """Implement code to pass tests (GREEN phase)."""
    typer.echo("Entering GREEN phase...")
    typer.echo("Green command - to be implemented")


@app.command()
def review() -> None:
    """Review implementation against spec."""
    typer.echo("Reviewing implementation...")
    typer.echo("Review command - to be implemented")


@app.command()
def merge() -> None:
    """Merge and update Memory Bank."""
    typer.echo("Merging changes...")
    typer.echo("Merge command - to be implemented")


def main() -> None:
    """Entry point."""
    app()


if __name__ == "__main__":
    main()
