# Active Context — CDAD-CLI

## Estado Actual (2026-05-01)

**Phase 1 MVP completado.** El CLI tiene 4 comandos funcionales y 2 agentes implementados. 88 tests pasando con 78% de cobertura.

### Qué funciona ahora

| Comando | Estado | Agente | Descripción |
|---|---|---|---|
| `cdad init` | ✅ Completo | — | Inicializa proyecto CDAD, detecta framework |
| `cdad spec` | ✅ Completo | ArchitectAgent | Genera specs con postcondiciones verificables |
| `cdad architect` | ✅ Completo | ArchitectAgent | Analiza código y recomienda mejoras |
| `cdad test` | ✅ Completo | TestWriterAgent | Genera tests pytest desde spec validada |
| `cdad red` | ⚠️ Scaffolding | — | Valida specs y ejecuta tests |
| `cdad green` | ⚠️ Scaffolding | — | Ejecuta tests y verifica GREEN |
| `cdad review` | 🚧 Placeholder | — | Pendiente: ReviewerAgent |
| `cdad merge` | 🚧 Placeholder | — | Pendiente: ScribeAgent |

### Presets activos

- **generic**: proyectos Python genéricos (detecta `pyproject.toml` / `setup.py`)
- **odoo**: addons de Odoo (detecta `__manifest__.py` / `__openerp__.py`)
- **django**: proyectos Django (detecta `manage.py`)

### Métricas

- Tests: **88 passing**
- Cobertura: **78%**
- Archivos de código fuente: ~25 archivos Python
- Agentes: 2 de 5 implementados
- Comandos: 4 completos, 4 scaffolding

### Próximo paso inmediato

Desarrollar `ImplementerAgent` y completar el ciclo RED→GREEN usando el propio CDAD-CLI (dogfooding).

### Riesgos actuales

1. **API Anthropic**: todos los agentes que usan LLM requieren `ANTHROPIC_API_KEY`. Sin ella, los comandos fallan silenciosamente.
2. **Validación de specs**: el SpecValidator es estricto pero puede rechazar specs válidas con formato ligeramente diferente.
3. **Cobertura al 78%**: faltan tests para comandos `red`/`green`/`review`/`merge` y para `PhaseManager`.

### Decisiones recientes

- Se eligió **context narrowing** sobre sandboxing para aislamiento de agentes (ADR-003)
- Se priorizó **ArchitectAgent + TestWriterAgent** como primer par de agentes (ciclo descubrimiento → spec → tests)
- Se estableció **pytest como validador de tests** (RED/GREEN se detecta por código de salida de pytest)
