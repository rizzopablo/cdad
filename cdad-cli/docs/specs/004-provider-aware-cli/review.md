# Review — 004-provider-aware-cli

## Resumen
- **Modelo usado**: Gemini 2.0 Flash (Reviewer sub-agent)
- **Archivos revisados**: `src/cdad/cli/main.py`, `src/cdad/llm/client.py`, `src/cdad/llm/registry.py`, `src/cdad/llm/providers/anthropic.py`
- **Alcance**: Revisión completa del diff contra Spec 004 v2 y análisis del fallo en PC-004-16.

Se han detectado **6 hallazgos bloqueantes** que incluyen regresiones funcionales, violaciones de invariantes de diseño y riesgos de estabilidad. La implementación de `config auto` fallará con proveedores reales debido a una discrepancia en la firma de métodos internos.

## Bloqueantes

### 1. Inconsistencia crítica de API en `config_auto`
**Ubicación**: `src/cdad/cli/main.py:663-667`
**Problema**: El comando llama a `provider_instance.send_message` pasando un `str` como segundo argumento y omitiendo `max_tokens`. Sin embargo, `AnthropicProvider` (y otros) esperan `history: list[Message]` y el keyword-only argument `max_tokens`.
**Impacto**: `config auto` fallará con un `TypeError` al intentar validar cualquier proveedor real (Anthropic/OpenAI), descartándolos erróneamente. Los tests no detectaron esto porque usan mocks con firmas laxas (`*args, **kwargs`).
**Sugerencia**: Ajustar la llamada para pasar una lista de mensajes: `provider_instance.send_message("", [{"role": "user", "content": "..."}], model=..., max_tokens=2048)`.

### 2. Violación de Invariante 10 en comando `green`
**Ubicación**: `src/cdad/cli/main.py:494-504`
**Problema**: El comando `green` mantiene su propia lógica de carga de configuración que solo lee `./cdad.toml`. No utiliza la función `_resolve_config` implementada para esta feature.
**Impacto**: Ignora la configuración global (`~/.config/cdad/cdad.toml`), rompiendo el soporte de scopes unificado definido en el spec.
**Sugerencia**: Reemplazar la carga manual por `config = _resolve_config(project_root)`.

### 3. Violación de Criterios de Aceptación (Hardcoded Keys)
**Ubicación**: `src/cdad/cli/main.py:608, 610`
**Problema**: El comando `config auto` accede directamente a `os.environ.get("ANTHROPIC_API_KEY")`. El criterio de aceptación prohíbe explícitamente matches de esta cadena en `src/cdad/cli/`.
**Impacto**: Incumplimiento del contrato de aislamiento (la CLI no debe conocer nombres específicos de keys de proveedores).
**Sugerencia**: Mover la lógica de detección de candidatos al `registry.py` o usar una abstracción en los proveedores.

### 4. Backup Destructivo en `config_auto`
**Ubicación**: `src/cdad/cli/main.py:623-630`
**Problema**: El backup (`os.rename`) se realiza *antes* de iniciar la validación de proveedores. Si ningún proveedor resulta válido, el comando aborta (exit 2) pero deja el archivo original renombrado a `.bak`, dejando al usuario sin configuración activa.
**Impacto**: Pérdida de configuración funcional ante fallos temporales de red o credenciales.
**Sugerencia**: Realizar el backup solo inmediatamente antes de escribir el nuevo archivo (después de tener un `validated_provider_string`).

### 5. Validación Falsa de Stubs
**Ubicación**: `src/cdad/llm/registry.py:211` y `src/cdad/cli/main.py:663`
**Problema**: Si `resolve_provider` devuelve un stub (`MagicMock`), la llamada a `send_message()` devuelve otro `MagicMock`. En `main.py:674`, `if response and response.strip():` evalúa como verdadero para un Mock.
**Impacto**: `config auto` podría dar por válido un proveedor cuyas credenciales fallaron (stub), escribiendo una configuración inservible.
**Sugerencia**: Verificar `if not _check_stub_provider(provider_instance): continue` dentro del loop de `config auto`.

### 6. Implementación frágil de Timeout (PC-004-16)
**Ubicación**: `src/cdad/cli/main.py:657-674`
**Problema**: 
1. Usa `signal.alarm`, que es incompatible con hilos y puede ser interferido por el test runner.
2. Usa `TimeoutError` como builtin, lo cual lanza `NameError` en Python 3.10 (requerido por el proyecto) ya que fue añadido en 3.11.
3. No garantiza la limpieza del alarm/handler ante excepciones genéricas (falta `finally`).
**Impacto**: Inestabilidad en la fase de validación y causa probable del "hang" reportado en tests.
**Sugerencia**: Usar un decorador de timeout basado en hilos o, si se mantiene `signal`, capturar `NameError` y usar `finally` para `signal.alarm(0)`.

## Opcionales

### 7. Colisión de Backups
**Ubicación**: `src/cdad/cli/main.py:624`
**Problema**: El timestamp tiene precisión de minutos (`%Y%m%d%H%M`). Dos ejecuciones en el mismo minuto colisionarán.
**Sugerencia**: Añadir segundos (`%Y%m%d%H%M%S`).

### 8. Código muerto / Helpers redundantes
**Ubicación**: `src/cdad/cli/main.py:56, 103`
**Problema**: `_load_cdad_toml_config` y `_find_project_root` parecen no tener usos tras la refactorización.
**Sugerencia**: Eliminar si se confirma su obsolescencia.

## Nota sobre PC-004-16
El test `test_timeout_rejects_provider` se cuelga probablemente porque:
1. El signal no se entrega al estar en un sub-proceso/hilo del runner.
2. Al lanzar `NameError` (por `TimeoutError` inexistente en 3.10) dentro del handler, si esto ocurre en un entorno de test mal configurado, el flujo de interrupción de `time.sleep` puede comportarse de forma errática.
3. **Recomendación**: Migrar la validación de `config auto` a un modelo no bloqueante o usar un timeout que no dependa de `SIGALRM` si se desea máxima compatibilidad cross-platform.

---
LISTO. Review finalizada.
Resumen: 6 bloqueantes, 2 opcionales.
