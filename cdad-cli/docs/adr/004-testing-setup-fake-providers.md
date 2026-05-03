# ADR 004: Testing Setup — Fake Providers y Environment Variables

**Date**: 2026-05-03  
**Status**: Accepted  
**Deciders**: Test-Writer, Implementer, Architect

## Context

Feature 003 (ImplementerAgent) y futuras features requieren testing de agentes que invocan `LLMProvider` (Anthropic, OpenAI, ACP, etc.). Los tests no deben:
- Consumir API keys reales.
- Hacer requests de red (falla en CI, lento en local).
- Depender de disponibilidad de servicios terceros.

Necesitamos una convención clara para:
1. **Cómo configurar el entorno de testing** (venv, env vars).
2. **Qué fake providers usar** en tests unitarios.
3. **Cuándo usar tests de integración** con providers reales.

## Decision

### 1. Fake Providers para Unit Tests

Cada provider (`AnthropicProvider`, `OpenAIProvider`, `ACPProvider`) tendrá un fake correspondiente en `tests/fakes/`:

```
tests/fakes/
├── __init__.py
├── fake_anthropic_provider.py
├── fake_openai_provider.py
└── fake_acp_provider.py
```

Cada fake:
- Implementa la misma interfaz que el provider real (`LLMProvider` Protocol).
- Devuelve respuestas configurables/deterministas (inyectadas en el constructor).
- **NUNCA hace requests de red** ni accede a env vars de API keys.
- Es síncrono (compatible con el flujo actual).

Ejemplo:

```python
class FakeACPProvider(LLMProvider):
    def __init__(self, scripted_responses: list[str]):
        self.responses = scripted_responses
        self.call_count = 0
    
    def complete(self, messages: list[dict], ...) -> str:
        if self.call_count >= len(self.responses):
            raise IndexError("scripted_responses exhausted")
        resp = self.responses[self.call_count]
        self.call_count += 1
        return resp
```

### 2. Environment Variables de Testing

Durante tests unitarios, el `resolve_provider()` debe usar fakes, no providers reales. Estrategia:

**En `conftest.py` (fixture scope=session)**:

```python
@pytest.fixture(autouse=True)
def mock_env_for_tests(monkeypatch):
    # Dummy API keys para que resolve_provider() no falle por "missing key"
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-dummy-anthropic")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-dummy-openai")
    # ACP no necesita key, pero puede ser útil para otros flags
```

**Registro de fakes en el registry** (en conftest o en los tests que los necesitan):

```python
from cdad.llm.registry import register
from tests.fakes import FakeACPProvider

register("acp_fake", lambda *args, **kwargs: FakeACPProvider(...))
```

### 3. Tests de Integración con Providers Reales

Para testing real con `qwen --acp` (dogfooding), usar marker `@pytest.mark.integration`:

```python
@pytest.mark.integration
def test_implementer_with_real_qwen():
    # Corre contra qwen real vía ACP
    # Skipea si qwen no está instalado o CDAD_RUN_INTEGRATION=false
    ...
```

Skipeos:
- Si `qwen` CLI no está disponible → skip automático.
- Si env var `CDAD_SKIP_INTEGRATION=true` → skip.
- CI/default: skippear tests de integración (correr solo unit tests con fakes).

### 4. Cómo Correr Tests en el Venv

#### Unit tests (default, rápido, sin network):

```bash
cd cdad-cli
source venv/bin/activate
pytest tests/ -v
```

No requiere API keys reales ni `qwen` instalado.

#### Tests de integración (opcional, requiere qwen):

```bash
source venv/bin/activate
pytest tests/ -v -m integration
```

Requiere `qwen --acp` disponible y funcionando.

#### Con cobertura:

```bash
pytest tests/ --cov=src/cdad --cov-report=html
```

## Consequences

- ✅ Tests unitarios rápidos y reproducibles.
- ✅ No dependen de API keys externas ni network.
- ✅ CI puede correr sin configurar secrets.
- ✅ Developers pueden iterar sin costo de API.
- ⚠️ Los fakes deben mantenerse en sync con los providers reales (responsabilidad de quien modifique `LLMProvider`).
- ⚠️ Tests de integración requieren setup local (`qwen`) — no corren en todos los entornos.

## Implementation Notes

- Los fakes se crean en `tests/fakes/` al inicio de feature 003.
- La fixture de env vars dummy se agrega a `tests/conftest.py`.
- Documentar en `docs/systemPatterns.md` sección "Testing" cómo escribir tests que usen providers.
