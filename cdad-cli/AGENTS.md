# CDAD-CLI: Agent Memory Bank (CDAD §10.3)

> **Última actualización**: 2026-05-01  
> **Fase**: Phase 1 MVP completada  
> **Versión**: 0.1.0

---

## Tech Stack

| Capa | Tecnología | Versión |
|---|---|---|
| CLI | Typer (sobre Click) | 0.9.0 / <8.2 |
| LLM | Anthropic SDK | ≥ 0.40.0 |
| Modelos | claude-opus-4-7, claude-sonnet-4-6 | — |
| Tests | pytest + pytest-cov | 7.4.0 / 4.1.0 |
| Linting | black, ruff, mypy | 23.7.0 / 0.1.0 / 1.4.0 |
| Config | PyYAML, python-frontmatter, toml | ≥ 6.0 / 1.0.0 / 0.10.2 |
| Python | ≥ 3.9 | — |

## Comandos Importantes

### Instalación
```bash
pip install -e ".[dev]"
pre-commit install
```

### Desarrollo
```bash
pytest                          # Ejecutar todos los tests
pytest --cov=src/cdad           # Con coverage
black src/ tests/               # Formatear código
ruff check src/ tests/          # Linting
mypy src/                       # Type checking
```

### CLI (comandos operativos)
```bash
cdad init --name my-project     # Inicializar proyecto CDAD
cdad discover --feature "..."   # Discovery (ArchitectAgent)
cdad spec --name feature-name   # Generar spec (ArchitectAgent + SpecValidator)
cdad architect src/module.py    # Analizar código (ArchitectAgent)
cdad test feature-name          # Generar tests (TestWriterAgent)
cdad red                        # Validar specs + tests (scaffolding)
cdad green                      # Verificar tests pasan (scaffolding)
cdad status                     # Estado actual del proyecto
```

### Variables de entorno
```bash
export ANTHROPIC_API_KEY=sk-ant-...  # Requerida para comandos con LLM
```

## Coding Standards

### Estilo
- **Line length**: 100 caracteres (black + ruff)
- **Target Python**: 3.9+
- **Imports**: ordenados — stdlib, third-party, local
- **Nomenclatura**: `snake_case` para funciones/variables, `PascalCase` para clases

### Type Hints
- Obligatorio en firmas de funciones públicas
- `typing.List`, `typing.Optional` preferidos sobre `list[]`, `X | None` (compatibilidad Python 3.9)
- mypy con `warn_return_any = true`, `disallow_untyped_defs = false` (tolerante en código legacy)

### Docstrings
- Google style en todas las clases y métodos públicos
- Incluir Args, Returns, Raises cuando aplique

### Tests
- pytest fixtures para setup compartido
- `tmp_path` para operaciones de archivos (no mockear filesystem)
- Monkey-patch `_make_llm_client()` para evitar llamadas reales a API
- Tests unitarios para validadores y modelos; tests de integración para CLI (con CliRunner)

### Commits
- Mensajes en inglés (convención de código)
- Formato: `type(scope): description`
- Tipos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Ejemplo: `feat(agent): add ArchitectAgent.analyze() method`

## Don't Touch

### No modificar directamente
- `src/cdad/agents/base.py` — interfaz abstracta, cambios requieren ADR
- `src/cdad/config/defaults.py` — constantes de configuración centralizadas
- `src/cdad/presets/__init__.py` — orden del registry afecta detección de frameworks
- `pyproject.toml` version — seguir semver, actualizar solo en releases
- `AGENTS.md` (este archivo) — actualizar solo en checkpoints de fase

### No hacer
- No hardcodear `ANTHROPIC_API_KEY` (usar variable de entorno)
- No modificar validadores sin actualizar tests correspondientes
- No saltar la fase RED (generar tests que pasan sin implementación)
- No usar `print()` — usar `typer.echo()` para output de CLI
- No llamar a LLM fuera de `LLMClient` (centralizado para logging/retry)

## Boundaries Arquitectónicos

```
┌─────────────────────────────────────────────┐
│  CLI Layer (src/cdad/cli/)                   │
│  Typer commands → Orchestrator               │
├─────────────────────────────────────────────┤
│  Orchestrator (src/cdad/orchestrator/)       │
│  PhaseManager → detect state, suggest next   │
├─────────────────────────────────────────────┤
│  Agents (src/cdad/agents/)                   │
│  BaseAgent → ArchitectAgent, TestWriterAgent │
│  (context narrowing via get_accessible_files)│
├─────────────────────────────────────────────┤
│  Validators (src/cdad/validators/)           │
│  SpecValidator, TestValidator               │
├─────────────────────────────────────────────┤
│  Domain (src/cdad/project/, src/cdad/llm/)   │
│  ProjectModel, LLMClient                     │
├─────────────────────────────────────────────┤
│  Presets (src/cdad/presets/)                 │
│  generic, django, odoo (framework detection) │
└─────────────────────────────────────────────┘
```

**Regla de flujo**: CLI → Orchestrator → Agent → LLMClient → ProjectModel → Validators → File I/O

**Aislamiento**: cada agente solo accede a archivos definidos en `get_accessible_files()`. Los validadores verifican contratos independientemente del agente.

## Workflow de Agentes

### Flujo CDAD completo
```
discover → spec → test → red → green → review → merge
   │          │        │       │        │        │
   Architect  Architect  Test   Valid   Implem   Review
   Agent      Agent     Writer  ators   ent      Agent
                        Agent          Agent    + Scribe
```

### Agente actual: ArchitectAgent
- **Ve**: README, docs/, specs existentes
- **Hace**: discover(), draft_spec(), analyze(), recommend()
- **Modelo**: claude-opus-4-7 (más potente para razonamiento arquitectónico)

### Agente actual: TestWriterAgent
- **Ve**: specs, tests existentes, pyproject.toml
- **Hace**: write_tests() — genera pytest desde spec validada
- **Modelo**: claude-sonnet-4-6
- **Valida**: SpecValidator antes de generar tests

### Agentes pendientes
- **ImplementerAgent**: escribir código para pasar tests (GREEN)
- **ReviewerAgent**: comparar implementación contra spec
- **ScribeAgent**: actualizar Memory Bank después de merge

## Convenciones de Commits

| Prefix | Cuándo usar | Ejemplo |
|---|---|---|
| `feat` | Nueva funcionalidad | `feat(agent): add TestWriterAgent.write_tests()` |
| `fix` | Corrección de bug | `fix(cli): handle missing ANTHROPIC_API_KEY gracefully` |
| `docs` | Documentación | `docs: add ADR-003 for context narrowing` |
| `refactor` | Cambio sin alterar comportamiento | `refactor(validator): extract postcondition parsing` |
| `test` | Tests nuevos o correcciones | `test(cli): add integration tests for cdad spec` |
| `chore` | Mantenimiento | `chore: bump pytest-cov to 4.1.0` |

### Branch naming
- `feat/agent-implementer` — nueva feature
- `fix/spec-validator-regex` — corrección
- `refactor/agent-base-abc` — refactor

### Pull Request checklist
- [ ] Tests pasan (`pytest`)
- [ ] Coverage no baja significativamente
- [ ] Linting limpio (`ruff check`, `black`, `mypy`)
- [ ] ADR creado si cambia arquitectura
- [ ] Memory Bank actualizado si cambia contexto
