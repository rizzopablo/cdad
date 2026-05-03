---
feature_id: 003-implementer-agent
stage: 4-review
layer: 1-code-correctness
reviewed_by: reviewer
reviewed_at: 2026-05-03
---

# Code Review: ImplementerAgent + `cdad green`

## BLOQUEANTES

### 1. Divergencia: error string para max_iterations (PC-003-3)

**Ubicación**: `src/cdad/agents/implementer.py:426`

**Problema**:
El spec (línea 75, PC-003-3) especifica:
> "Si tras `max_iterations` iteraciones la suite sigue RED, retorna `success=False` con `error="max_iterations_reached"`"

Pero el código retorna:
```python
error=f"Failed to reach GREEN after {max_iterations} iterations"
```

Esta es una violación del contrato verificable. El error string debe ser exactamente `"max_iterations_reached"` como postcondición verificable.

**Sugerencia de fix**:
```python
# Línea 426, cambiar de:
error=f"Failed to reach GREEN after {max_iterations} iterations",
# A:
error="max_iterations_reached",
```

**Prioridad**: Bloqueante — El spec numera esta postcondición como PC-003-3 y es verificable.

---

### 2. Active feature hardcodeado en _scan_for_obsolete_references

**Ubicación**: `src/cdad/agents/implementer.py:162`

**Problema**:
La función de detección de obsolescencia tiene un parámetro default hardcodeado a "003":
```python
def _scan_for_obsolete_references(self, test_output: str, active_feature: str = "003") -> list[ObsolescenceSuspicion]:
```

Esto significa que solo funciona correctamente para features 003. Si hay otras features con specs cerrados (002, 001, 004, etc.), la heurística fallará porque solo buscará referencias a `PC-NNN donde NNN != "003"`.

**Sugerencia de fix**:
Pasar `active_feature` desde `implement()` leyéndolo del spec_path o del estado del proyecto:
```python
def implement(self, spec_path: Path, ...) -> ImplementResult:
    # Extraer feature ID del path (e.g., "003" de "docs/specs/003-implementer-agent/spec.md")
    feature_id = spec_path.parent.name.split("-")[0]
    ...
    suspicions = self._scan_for_obsolete_references(combined_output, active_feature=feature_id)
```

**Prioridad**: Bloqueante — La heurística de obsolescencia es parte del contrato (PC-003-5), y está hardcodeada a un valor específico que no es genérico.

---

## OPCIONALES

### 3. Búsqueda de spec por active_feature incompleta en CLI

**Ubicación**: `src/cdad/cli/main.py:388-401`

**Problema**:
El comando intenta buscar specs como:
```python
spec_path = project_root / "docs" / "specs" / f"{active_feature}.md"
```

Pero el spec actual está en `docs/specs/003-implementer-agent/spec.md`, no `docs/specs/003.md`. El fallback (líneas 397-401) intenta buscar el primer `.md` en `specs_dir`, pero fallará porque es una estructura de subdirectorios.

En un proyecto real con la estructura correcta, el comando no encontrará la spec.

**Sugerencia de fix**:
```python
# Línea 388-389, cambiar búsqueda a:
spec_dir = project_root / "docs" / "specs" / active_feature
if spec_dir.exists():
    spec_path = spec_dir / "spec.md"
    if spec_path.exists():
        pass
else:
    # Fallback a búsqueda más inteligente
    for subdir in sorted((project_root / "docs" / "specs").glob("*-*")):
        if subdir.is_dir() and subdir.name.startswith(active_feature):
            spec_path = subdir / "spec.md"
            if spec_path.exists():
                break
```

**Impacto**: Sin esto, el comando `cdad green` sin `--spec` fallará en proyectos reales.

**Prioridad**: Opcional pero importante — afecta usabilidad del comando en la CLI.

---

### 4. Captura de Exception demasiado genérica en ACPProvider

**Ubicación**: `src/cdad/llm/providers/acp.py:114-119`

**Problema**:
```python
try:
    await conn.close_session(session_id)
except Exception:
    # Some ACP agents (e.g. qwen) don't support the session/close method.
    # Swallow the error so it doesn't mask the actual response.
    pass
```

Capturar `Exception` es demasiado genérico. Puede ocultar bugs legítimos como:
- `AttributeError` si la API cambió
- `RuntimeError` por timeout o desconexión
- Otros errores inesperados

**Sugerencia de fix**:
```python
except (AttributeError, NotImplementedError):
    # Some ACP agents (e.g. qwen) don't support the session/close method.
    pass
```

**Prioridad**: Opcional — Es un edge case, pero buena práctica es ser específico con excepciones.

---

### 5. Duplicación de output en comando green

**Ubicación**: `src/cdad/cli/main.py:473-481` y `src/cdad/agents/implementer.py:367, 393, 417`

**Problema**:
El agente imprime progreso en cada iteración:
```python
print(f"[Iteration {i}] Suite RED — {passed} passed, {failed} failed")
print(f"Modified: {', '.join(str(p) for p in written)}")
```

Luego, el comando también imprime el resultado:
```python
typer.echo(f"success: {result.success}")
typer.echo(f"iterations_used: {result.iterations_used}")
```

Hay potencial duplicación de información en stdout.

**Sugerencia de fix**:
Usar un flag `verbose: bool` para controlar si el agente debe imprimir, o separar output del agente de output del CLI.

**Prioridad**: Opcional — El output es funcional, solo un poco redundante.

---

## CHECKLIST DE VALIDACIÓN

- ✅ Spec identificado y accesible (`docs/specs/003-implementer-agent/spec.md`)
- ✅ 13 postcondiciones especificadas
- ✅ ImplementResult dataclass implementado con todos los campos
- ✅ Método `implement()` tiene firma correcta
- ✅ Tests unitarios cubren postcondiciones
- ✅ Property test para invariante "no toca tests/" (1283 líneas)
- ✅ Cambio de default `acp/qwen` implementado
- ✅ Parámetro `override` en `resolve_provider()` agregado
- ✅ Comando `cdad green` registrado e implementado
- ✅ Exit codes mapping (0, 1, 2) implementado
- ⚠️ **Error string para max_iterations NO coincide con spec** (BLOQUEANTE)
- ⚠️ **Active feature hardcodeado en heurística** (BLOQUEANTE)

---

## RESUMEN

**Bloqueantes a resolver**: 2
- Error string mismatch para max_iterations (PC-003-3)
- Active feature hardcodeado en _scan_for_obsolete_references (PC-003-5)

**Opcionales a considerar**: 3
- Búsqueda de spec mejora usabilidad
- Exception handling más específico en ACP
- Consolidación de output del agente vs CLI

**Recomendación**: Resolver los 2 bloqueantes antes del merge. Los opcionales pueden ir en Phase 2.

---

Status: **Requires Changes** (bloqueantes identificados)  
Date: 2026-05-03
