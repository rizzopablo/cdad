# Review de Fixes — 004-provider-aware-cli

## Bloqueantes originales (1-6)
### 1. send_message con firma incorrecta: ✅ Resuelto
La función `send_message` en `config_auto` ahora tiene la firma correcta: `(system_prompt, history[], model, max_tokens)`. Se puede ver en la línea 740-745 de `src/cdad/cli/main.py` donde se llama a `provider_instance.send_message("", [...], model=provider_instance._model_id, max_tokens=2048)`.

### 2. green violaba Invariante 10: ✅ Resuelto
La función `green` ahora usa `_resolve_config()` como se puede ver en la línea 578 de `src/cdad/cli/main.py`: `config = _resolve_config(project_root)`. Esto cumple con el Invariante 10 que indica cómo deben leerse las configuraciones.

### 3. Hardcoded ANTHROPIC_API_KEY en main.py: ✅ Resuelto
Se ha eliminado el uso hardcoded de ANTHROPIC_API_KEY y ahora se utiliza `get_available_providers()` del registry como se ve en la línea 697 de `src/cdad/cli/main.py`: `from cdad.llm.registry import get_available_providers`.

### 4. Backup destructivo en config_auto: ✅ Resuelto
El backup ahora se realiza DESPUÉS de la validación exitosa, como se puede ver en la línea 765 de `src/cdad/cli/main.py` donde primero se valida que haya un `validated_provider_string` y luego se hace el backup en la línea 770.

### 5. Validación falsa de stubs: ✅ Resuelto
Ahora se verifica que la respuesta sea una instancia de string con `isinstance(response, str)` en la línea 756 de `src/cdad/cli/main.py`, lo que evita que los stubs (como MagicMock) pasen la validación falsamente.

### 6. Timeout frágil con signal.alarm: ✅ Resuelto
Se ha reemplazado por `ThreadPoolExecutor` con timeout de 30s como se ve en la línea 736 de `src/cdad/cli/main.py`, lo cual es compatible con diferentes versiones de Python.

## Fixes ACP (A-C)
### A. Race condition: ✅ Resuelto
Se implementó `asyncio.Event` + `wait_for(timeout=120)` después de `prompt()` como se puede ver en la línea 833 de `src/cdad/llm/providers/acp.py` donde se usa `await asyncio.wait_for(collector._done.wait(), timeout=120.0)`.

### B. Extracción de texto: ✅ Resuelto
Ahora se usa `update.content.text` en vez de `update.text` como se puede ver en la línea 807 de `src/cdad/llm/providers/acp.py` donde se manejan ambos casos (con `update.content.text` y con `update.text` directamente).

### C. Stubs de protocolo: ✅ Resuelto
Se implementaron métodos de protocolo como `read_text_file`, `write_text_file`, `create_terminal`, etc., y devuelven `NotImplementedError` como se puede ver en las líneas 733-771 de `src/cdad/llm/providers/acp.py`. Esta es la implementación correcta para indicar que CDAD no soporta estas operaciones.

## Nuevos hallazgos
### 1. Manejo de excepciones en close_session opcional
Ubicación: src/cdad/llm/providers/acp.py:l850
Problema: En algunos agentes ACP (como qwen), el método close_session no está soportado, por lo que se ignora el error. Aunque se maneja apropiadamente, esto podría dejar recursos sin limpiar en ciertos agentes.
Sugerencia: Considerar agregar logging de debug para estos casos para facilitar troubleshooting futuro.
Severidad: Opcional

## Veredicto
Aprobado para merge — Todos los bloqueantes originales han sido resueltos correctamente y los fixes ACP son robustos. El único hallazgo menor es opcional y no afecta la funcionalidad crítica.