# ADR-003: Aislamiento de Sesiones por Context Narrowing

**Fecha**: 2026-02-01  
**Estado**: Aceptado  
**Contexto**: CDAD-CLI §2.5, Aislamiento de Agentes

## Contexto

En CDAD, cada agente (Architect, TestWriter, Implementer, Reviewer, Scribe) debe operar de forma aislada para evitar:
- **Contaminación de contexto**: que un agente vea información que no le corresponde
- **Leakage de conocimiento**: que el TestWriter vea la implementación y escriba tests que "hacen trampa"
- **Acoplamiento implícito**: que agentes tomen decisiones basadas en información fuera de su rol

Se evaluaron dos enfoques:
1. **Sandboxing**: aislamiento a nivel de SO (contenedores, namespaces, chroot)
2. **Context narrowing**: limitar los archivos que cada agente puede leer

## Decisión

Implementar aislamiento por **context narrowing** (limitación de archivos accesibles), no por sandboxing a nivel de SO.

## Racional

1. **Simplicidad**: no requiere herramientas externas (Docker, namespaces, etc.)
2. **Epistémico vs técnico**: el aislamiento es epistémico (el agente no *sabe* lo que no ve) más que técnico (no *puede* acceder). Confiamos en que las instrucciones del sistema sean respetadas.
3. **Transparencia**: los usuarios pueden inspeccionar qué archivos ve cada agente (`get_accessible_files()`)
4. **Validación de contratos**: si un agente "hace trampa", los validadores (`SpecValidator`, `TestValidator`) detectan violaciones de contrato
5. **Performance**: sin overhead de contenedores o procesos aislados

## Implementación

Cada agente implementa `get_accessible_files()`:

```python
# ArchitectAgent ve: README, docs/, specs
# TestWriterAgent ve: specs, tests existentes, pyproject.toml
# ImplementerAgent verá: specs, tests, src/ (pendiente)
# ReviewerAgent verá: specs, tests, src/ (pendiente)
```

`BaseAgent.get_context()` lee solo los archivos devueltos por `get_accessible_files()`.

## Alternativas Rechazadas

### Sandboxing con contenedores (Docker)
- **Pro**: aislamiento real a nivel de SO; imposible que un agente acceda fuera de su sandbox
- **Contra**: overhead significativo; complejidad de infraestructura; requiere Docker instalado; ralentiza desarrollo iterativo

### Procesos separados con permisos de filesystem
- **Pro**: aislamiento real; auditable
- **Contra**: complejo de implementar en Python cross-platform; permisos varían entre OS; difícil de debuggear

## Mitigaciones contra "cheating"

1. **SpecValidator**: rechaza specs sin postcondiciones verificables
2. **TestValidator**: detecta si tests pasan sin implementación (RED phase fallida)
3. **System prompts**: instruyen explícitamente al agente sobre qué NO hacer
4. **Review phase**: ReviewerAgent compara implementación contra spec (pendiente)

## Consecuencias

- **Positivas**: implementación simple, transparente, sin dependencias externas, fácil de debuggear
- **Negativas**: aislamiento epistémico no es garantía técnica; un agente malicioso (o con instrucciones corruptas) podría acceder a archivos fuera de su rol
- **Mitigación**: los validadores actúan como última línea de defensa; si un test pasa sin implementación correcta, el TestValidator lo detecta
