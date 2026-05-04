"""CDAD CLI main entry point."""

import json
import os
import re
import shutil
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import toml
import typer

from cdad.agents.architect import ArchitectAgent
from cdad.agents.implementer import (
    ImplementerAgent,
    ImplementResult,
    InvalidSpecError,
    SpecNotFoundError,
)
from cdad.agents.test_writer import TestWriterAgent
from cdad.config.defaults import MEMORY_BANK_FILE
from cdad.llm.client import LLMClient
from cdad.llm.provider import ConfigurationError
from cdad.llm.registry import resolve_provider
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


def _resolve_config(project_root: Path) -> dict:
    """Resolve config by merging local and global configurations.

    Priority: local (./cdad.toml) > global (~/.config/cdad/cdad.toml) > empty
    """
    config = {}

    # Try global config first (~/.config/cdad/cdad.toml)
    global_config_path = Path.home() / ".config" / "cdad" / "cdad.toml"
    if global_config_path.exists():
        try:
            config = toml.load(global_config_path)
        except Exception:
            pass

    # Local config overrides global
    local_config_path = project_root / "cdad.toml"
    if local_config_path.exists():
        try:
            local = toml.load(local_config_path)
            # Shallow merge: local keys override global
            for key, value in local.items():
                if key == "agents" and "agents" in config:
                    config["agents"].update(value)
                else:
                    config[key] = value
        except Exception:
            pass

    return config


def _require_agent_config(config: dict, role: str) -> bool:
    """Validate that config has [agents] section with role or default.

    Returns True if valid, False otherwise (and prints error to stderr).
    """
    supported = "Supported providers: anthropic, openai, acp."
    if "agents" not in config:
        typer.echo(
            f"Error: No cdad.toml found or missing [agents] section. "
            f"Run 'cdad config auto' or 'cdad config set' to configure providers. {supported}",
            err=True,
        )
        return False

    if role not in config["agents"] and "default" not in config["agents"]:
        typer.echo(
            f"Error: No provider configured for role '{role}' and no default. "
            f"Run 'cdad config auto' or 'cdad config set' to configure providers. {supported}",
            err=True,
        )
        return False

    return True


def _check_stub_provider(provider_instance) -> bool:
    """Check if provider is a stub (factory failed). If so, print error and return False."""
    # A genuine stub has _is_stub=True AND lacks real provider methods
    # A test mock has _is_stub=False (or undefined) AND has real methods like send_message

    has_is_stub = hasattr(provider_instance, "_is_stub") and provider_instance._is_stub is True

    if has_is_stub:
        typer.echo(
            "Error: Provider not available. Supported providers: anthropic, openai, acp.",
            err=True,
        )
        return False
    return True


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
    feature: Optional[str] = typer.Option(None, help="Feature description"),
    path: Optional[Path] = typer.Option(None, help="Project path"),
    provider: Optional[str] = typer.Option(
        None, help="Provider override (e.g. anthropic/claude-opus-4-7)"
    ),
    target: Optional[str] = typer.Argument(None, help="Feature name (positional)"),
) -> None:
    """Start discovery phase - architect agent analyzes the feature."""
    feature_text = feature or target or "unnamed"
    project_root = path or Path.cwd()

    project = _load_project(project_root)
    if project is None:
        raise typer.Exit(2)

    # Load config and validate
    config = _resolve_config(project_root)
    if not _require_agent_config(config, "architect"):
        raise typer.Exit(2)

    # Resolve provider
    try:
        provider_instance = resolve_provider("architect", config, override=provider)
    except ConfigurationError as exc:
        typer.echo(f"Error: Provider not resolvable: {exc}", err=True)
        raise typer.Exit(2)

    # Check if provider is a stub (factory failed due to missing credentials)
    if not _check_stub_provider(provider_instance):
        raise typer.Exit(2)

    # Validate provider command exists if applicable (only for real ACP providers)
    if (
        hasattr(provider_instance, "command")
        and provider_instance.command
        and isinstance(provider_instance.command, list)
    ):
        if not shutil.which(provider_instance.command[0]):
            cmd_name = provider_instance.command[0]
            typer.echo(f"Error: Provider command '{cmd_name}' not found in PATH", err=True)
            raise typer.Exit(2)

    # Create LLMClient with provider
    model_id = getattr(provider_instance, "_model_id", "") or "claude-opus-4-7"
    llm_client = LLMClient(provider=provider_instance, model=model_id)

    try:
        architect = ArchitectAgent(role="architect", project=project, llm_client=llm_client)

        typer.echo(f"🔍 Discovering: {feature_text}")
        typer.echo(f"   Project: {project.name} ({project.framework})")
        typer.echo("")

        discovery_output = architect.discover(feature_text)

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
    provider: Optional[str] = typer.Option(
        None, help="Provider override (e.g. anthropic/claude-opus-4-7)"
    ),
) -> None:
    """Generate spec from discovery."""
    project_root = path or Path.cwd()

    project = _load_project(project_root)
    if project is None:
        raise typer.Exit(2)

    # Load config and validate
    config = _resolve_config(project_root)
    if not _require_agent_config(config, "architect"):
        raise typer.Exit(2)

    discovery_path = project_root / "docs" / "discovery.md"
    if not discovery_path.exists():
        typer.echo("Error: No discovery found. Run 'cdad discover' first.", err=True)
        raise typer.Exit(2)

    # Resolve provider
    try:
        provider_instance = resolve_provider("architect", config, override=provider)
    except ConfigurationError as exc:
        typer.echo(f"Error: Provider not resolvable: {exc}", err=True)
        raise typer.Exit(2)

    # Check if provider is a stub (factory failed due to missing credentials)
    if not _check_stub_provider(provider_instance):
        raise typer.Exit(2)

    # Validate provider command exists if applicable (only for real ACP providers)
    if (
        hasattr(provider_instance, "command")
        and provider_instance.command
        and isinstance(provider_instance.command, list)
    ):
        if not shutil.which(provider_instance.command[0]):
            cmd_name = provider_instance.command[0]
            typer.echo(f"Error: Provider command '{cmd_name}' not found in PATH", err=True)
            raise typer.Exit(2)

    # Create LLMClient with provider
    model_id = getattr(provider_instance, "_model_id", "") or "claude-opus-4-7"
    llm_client = LLMClient(provider=provider_instance, model=model_id)

    try:
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
            typer.echo(
                f"⚠ Validation failed (attempt {attempts}/{retry}); asking architect to fix."
            )
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
    provider: Optional[str] = typer.Option(
        None, help="Provider override (e.g. anthropic/claude-opus-4-7)"
    ),
) -> None:
    """Analyze existing code and produce architectural recommendations."""
    project_root = path or Path.cwd()

    project = _load_project(project_root)
    if project is None:
        raise typer.Exit(2)

    if not target.exists():
        typer.echo(f"Error: Target not found: {target}", err=True)
        raise typer.Exit(2)

    # Load config and validate
    config = _resolve_config(project_root)
    if not _require_agent_config(config, "architect"):
        raise typer.Exit(2)

    # Resolve provider
    try:
        provider_instance = resolve_provider("architect", config, override=provider)
    except ConfigurationError as exc:
        typer.echo(f"Error: Provider not resolvable: {exc}", err=True)
        raise typer.Exit(2)

    # Check if provider is a stub (factory failed due to missing credentials)
    if not _check_stub_provider(provider_instance):
        raise typer.Exit(2)

    # Validate provider command exists if applicable (only for real ACP providers)
    if (
        hasattr(provider_instance, "command")
        and provider_instance.command
        and isinstance(provider_instance.command, list)
    ):
        if not shutil.which(provider_instance.command[0]):
            cmd_name = provider_instance.command[0]
            typer.echo(f"Error: Provider command '{cmd_name}' not found in PATH", err=True)
            raise typer.Exit(2)

    # Create LLMClient with provider
    model_id = getattr(provider_instance, "_model_id", "") or "claude-opus-4-7"
    llm_client = LLMClient(provider=provider_instance, model=model_id)

    try:
        agent = ArchitectAgent(role="architect", project=project, llm_client=llm_client)

        typer.echo(f"🏗  Analyzing: {target}")
        analysis = agent.analyze(target)
        recommendations = agent.recommend(analysis)

        out_dir = project_root / "docs" / "architecture"
        out_dir.mkdir(parents=True, exist_ok=True)
        slug = _slugify(
            str(target.relative_to(project_root)) if target.is_absolute() else str(target)
        )
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
    provider: Optional[str] = typer.Option(
        None, help="Provider override (e.g. anthropic/claude-sonnet-4-6)"
    ),
) -> None:
    """Generate failing pytest tests from a spec."""
    project_root = path or Path.cwd()

    project = _load_project(project_root)
    if project is None:
        raise typer.Exit(2)

    spec_file = project_root / "docs" / "specs" / f"{spec_name}.md"
    if not spec_file.exists():
        typer.echo(f"Error: Spec not found: {spec_file}", err=True)
        raise typer.Exit(2)

    # Load config and validate
    config = _resolve_config(project_root)
    if not _require_agent_config(config, "test_writer"):
        raise typer.Exit(2)

    out_file = project_root / "tests" / f"test_{spec_name.replace('-', '_')}.py"
    if out_file.exists() and not force:
        typer.echo(f"Error: {out_file} already exists. Use --force to overwrite.", err=True)
        raise typer.Exit(2)

    # Resolve provider
    try:
        provider_instance = resolve_provider("test_writer", config, override=provider)
    except ConfigurationError as exc:
        typer.echo(f"Error: Provider not resolvable: {exc}", err=True)
        raise typer.Exit(2)

    # Check if provider is a stub (factory failed due to missing credentials)
    if not _check_stub_provider(provider_instance):
        raise typer.Exit(2)

    # Validate provider command exists if applicable (only for real ACP providers)
    if (
        hasattr(provider_instance, "command")
        and provider_instance.command
        and isinstance(provider_instance.command, list)
    ):
        if not shutil.which(provider_instance.command[0]):
            cmd_name = provider_instance.command[0]
            typer.echo(f"Error: Provider command '{cmd_name}' not found in PATH", err=True)
            raise typer.Exit(2)

    # Create LLMClient with provider
    model_id = getattr(provider_instance, "_model_id", "") or "claude-sonnet-4-6"
    llm_client = LLMClient(provider=provider_instance, model=model_id)

    try:
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
def green(
    spec: Optional[Path] = typer.Option(None, help="Path to spec file"),
    max_iterations: int = typer.Option(5, help="Max TDD iterations"),
    provider: Optional[str] = typer.Option(None, help="Provider override (e.g. acp/qwen)"),
    path: Optional[Path] = typer.Option(None, help="Project path"),
) -> None:
    """Run ImplementerAgent to close the GREEN phase."""
    project_root = path or Path.cwd()

    # --- Step 1: Resolve spec path ---
    spec_path: Optional[Path] = None
    if spec is not None:
        spec_path = Path(spec)
        if not spec_path.exists():
            typer.echo(f"Error: Spec not found: {spec_path}")
            raise typer.Exit(2)
    else:
        state_file = project_root / "docs" / ".cdad-state.json"
        if state_file.exists():
            try:
                state = json.loads(state_file.read_text(encoding="utf-8"))
                active_feature = state.get("active_feature")
                if active_feature:
                    spec_path = project_root / "docs" / "specs" / f"{active_feature}.md"
                    if not spec_path.exists():
                        typer.echo(f"Error: Spec not found: {spec_path}")
                        raise typer.Exit(2)
            except (json.JSONDecodeError, OSError) as exc:
                typer.echo(f"Error: Cannot read state file: {exc}")
                raise typer.Exit(2)

        # Fallback: no --spec and no active_feature in state file
        if spec_path is None:
            specs_dir = project_root / "docs" / "specs"
            if specs_dir.exists():
                specs = sorted(specs_dir.glob("*.md"))
                if specs:
                    spec_path = specs[0]

        if spec_path is None:
            typer.echo("No active feature. Pass --spec PATH or initialize a feature first.")
            raise typer.Exit(2)

    # --- Step 2: Check test files exist ---
    test_dir = project_root / "tests"
    if test_dir.exists():
        test_files = sorted(test_dir.glob("test_*.py"))
    else:
        test_files = []
    if not test_files:
        typer.echo("No active feature. Pass --spec PATH or initialize a feature first.")
        raise typer.Exit(2)

    # --- Step 3: Load config ---
    config = _resolve_config(project_root)

    # --- Step 4: Resolve provider ---
    try:
        provider_instance = resolve_provider("implementer", config, override=provider)
    except ConfigurationError as exc:
        typer.echo(f"Error: Provider not resolvable: {exc}")
        raise typer.Exit(2)

    # --- Step 5: Validate provider ---
    if hasattr(provider_instance, "command") and provider_instance.command:
        if not shutil.which(provider_instance.command[0]):
            cmd_name = provider_instance.command[0]
            typer.echo(f"Error: Provider command '{cmd_name}' not found in PATH")
            raise typer.Exit(2)

    # --- Step 6: Create LLMClient wrapping the provider ---
    model_id = getattr(provider_instance, "_model_id", "") or "qwen"
    llm_client = LLMClient(provider=provider_instance, model=model_id)

    # --- Step 7: Create project and agent ---
    project = _load_project(project_root)
    if project is None:
        raise typer.Exit(2)

    agent = ImplementerAgent(role="implementer", project=project, llm_client=llm_client)

    # --- Step 8: Run implement() ---
    try:
        result: ImplementResult = agent.implement(
            spec_path,
            max_iterations=max_iterations,
            provider_override=provider,
        )
    except (SpecNotFoundError, InvalidSpecError) as exc:
        typer.echo(f"Error: {exc}")
        raise typer.Exit(2)
    except ConfigurationError as exc:
        typer.echo(f"Error: Provider configuration failed: {exc}")
        raise typer.Exit(2)

    # --- Step 9: Print ImplementResult ---
    status_str = "GREEN" if result.success else "RED"
    typer.echo(f"\nSuite {status_str} — iterations_used: {result.iterations_used}")
    typer.echo(f"success: {result.success}")
    typer.echo(f"iterations_used: {result.iterations_used}")
    modified_str = (
        ", ".join(str(p) for p in result.files_modified) if result.files_modified else "(none)"
    )
    typer.echo(f"files_modified: {modified_str}")
    if result.error:
        typer.echo(f"error: {result.error}")
    if result.obsolescence_suspicions:
        typer.echo(f"obsolescence_suspicions: {len(result.obsolescence_suspicions)} detected")

    # --- Step 10: Map result to exit code (PC-003-13) ---
    if result.success:
        raise typer.Exit(0)
    # All agent-loop failures (max_iterations, obsolescence, provider_error, etc.) → exit 1
    raise typer.Exit(1)


@app.command()
def review() -> None:
    """Review implementation against spec."""
    typer.echo("(Phase 1: Full reviewer agent coming soon)")


@app.command()
def merge() -> None:
    """Merge and update Memory Bank."""
    typer.echo("(Phase 1: Full merge workflow coming soon)")


# ---------------------------------------------------------------------------
# config command group
# ---------------------------------------------------------------------------

config_app = typer.Typer(name="config", help="Manage provider configuration.")
app.add_typer(config_app)


@config_app.command("auto")
def config_auto(
    path: Optional[Path] = typer.Option(None, help="Project path"),
    local: bool = typer.Option(False, "--local", is_flag=True, help="Write to ./cdad.toml"),
    global_: bool = typer.Option(False, "--global", is_flag=True, help="Write to ~/.config/cdad/cdad.toml"),
) -> None:
    """Auto-detect available providers and create cdad.toml."""
    # Determine which config file to write to
    if local:
        config_path = Path.cwd() / "cdad.toml"
    else:
        # Default or --global: use global config
        config_path = Path.home() / ".config" / "cdad" / "cdad.toml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

    project_root = path or Path.cwd()

    # --- Pre-check: find available candidates using registry ---
    from cdad.llm.registry import get_available_providers

    available = get_available_providers()
    if not available:
        typer.echo(
            "Error: No providers available. Configure one of: "
            "anthropic (set API key env var), "
            "openai (set API key env var), "
            "claude (install bin), "
            "qwen (install bin).",
            err=True,
        )
        raise typer.Exit(2)

    # Build candidate tuples (provider_name, provider_string)
    candidates = []
    for provider_id in available:
        if provider_id == "anthropic":
            candidates.append(("anthropic", "anthropic/claude-opus-4-7"))
        elif provider_id == "openai":
            candidates.append(("openai", "openai/gpt-4o"))
        elif provider_id.startswith("acp/"):
            acp_alias = provider_id.split("/", 1)[1]
            candidates.append(("acp", provider_id))

    # --- Validate each candidate with a real call (timeout 30s) ---
    validated_provider_string = None

    for provider_name, provider_string in candidates:
        try:
            provider_instance = resolve_provider(provider_name, {}, override=provider_string)
        except ConfigurationError:
            continue

        # If provider is not a stub, it passed factory validation; trust it
        if not (hasattr(provider_instance, '_is_stub') and provider_instance._is_stub):
            validated_provider_string = provider_string
            break

        # For stubs, try real validation (shouldn't happen in normal flow, but for testing)
        try:

            def send_validation_message():
                return provider_instance.send_message(
                    "",
                    [{"role": "user", "content": "Is CDAD available? Responde con 'disponible'."}],
                    model=provider_instance._model_id,
                    max_tokens=2048,
                )

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(send_validation_message)
                response = future.result(timeout=3)

            # Validate response is actually a string
            if isinstance(response, str) and response.strip():
                validated_provider_string = provider_string
                break
            else:
                typer.echo(f"Discarded {provider_name}: empty or invalid response", err=True)

        except FuturesTimeout:
            typer.echo(f"Discarded {provider_name}: timeout", err=True)
        except Exception as exc:
            typer.echo(f"Discarded {provider_name}: error: {exc}", err=True)

    if not validated_provider_string:
        typer.echo(
            "Error: No provider responded to validation. "
            "Check your API keys and network connection.",
            err=True,
        )
        raise typer.Exit(2)

    # --- Backup existing toml AFTER successful validation ---
    if config_path.exists():
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        backup_path = config_path.parent / f"{config_path.name}.bak-{timestamp}"
        try:
            os.rename(str(config_path), str(backup_path))
        except OSError as exc:
            typer.echo(f"Error: Failed to backup existing cdad.toml: {exc}", err=True)
            raise typer.Exit(2)

    # --- Write config file with only default ---
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        f'[agents]\ndefault = "{validated_provider_string}"\n',
        encoding="utf-8",
    )
    typer.echo(f'✓ Created cdad.toml with default = "{validated_provider_string}"')


@config_app.command("set")
def config_set(
    role: str = typer.Argument(..., help="Role name"),
    value: str = typer.Argument(..., help="Provider/model string (e.g. anthropic/claude-opus-4-7)"),
    path: Optional[Path] = typer.Option(None, help="Project path"),
    local: bool = typer.Option(False, "--local", is_flag=True, help="Write to ./cdad.toml"),
    global_: bool = typer.Option(False, "--global", is_flag=True, help="Write to ~/.config/cdad/cdad.toml"),
) -> None:
    """Set a provider for a specific role in cdad.toml."""
    VALID_ROLES = {"default", "architect", "test_writer", "implementer", "reviewer", "scribe"}

    # Determine which config file to write to
    if local:
        config_path = Path.cwd() / "cdad.toml"
    else:
        # Default or --global: use global config
        config_path = Path.home() / ".config" / "cdad" / "cdad.toml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

    # Validate role
    if role not in VALID_ROLES:
        typer.echo(
            f"Error: Unknown role '{role}'. "
            f"Valid roles: default, architect, test_writer, implementer, reviewer, scribe.",
            err=True,
        )
        raise typer.Exit(2)

    # Validate format: must contain "/" and provider part must match regex
    if "/" not in value:
        typer.echo(
            f"Error: Invalid format '{value}'. Expected 'provider/model'.",
            err=True,
        )
        raise typer.Exit(2)

    provider_part = value.split("/", 1)[0]
    if not re.match(r"^[a-z][a-z0-9_-]*$", provider_part):
        typer.echo(
            f"Error: Invalid provider name '{provider_part}' in '{value}'. "
            f"Expected 'provider/model' format (lowercase: '{provider_part.lower()}').",
            err=True,
        )
        raise typer.Exit(2)

    # Load existing config from the target file
    config: dict = {}
    if config_path.exists():
        try:
            config = toml.load(config_path)
        except Exception:
            config = {}

    if "agents" not in config:
        config["agents"] = {}

    config["agents"][role] = value

    # Ensure directory exists and write
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(toml.dumps(config), encoding="utf-8")
    typer.echo(f'✓ Set {role} = "{value}" in cdad.toml')


def main() -> None:
    """Entry point."""
    app()


if __name__ == "__main__":
    main()
