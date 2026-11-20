**Corrección completada** en la ronda de resultado **2/2**, sin ampliar el límite. El cleanup de PD4 ahora restaura permisos solo si el archivo todavía existe; permanece ilegible durante las comprobaciones. No se modificaron assertions ni se añadieron tests.

La validación estructural Route C de `intake` terminó correctamente usando el archivo de captura indicado. Esa validación no acredita por sí sola el origen de la captura.

**Verificación focal:** `python3 -m pytest -q tests/test_006_005_u1b_dispatch_entry.py tests/test_006_005_u1a_runtime_config.py` → **36 passed**, rc 0. La salida y el código están guardados en `tests/.native-record-evidence/cleanup-002-u1b-u1a.{txt,rc}`, sin sobrescribir la evidencia RED. No se ejecutó la suite completa; la evidencia se limita a esos dos módulos.

**Commit:** `2140c64aba80232063ed137f3f3761ac92524cd6`. Incluye únicamente el test corregido y los dos archivos de evidencia. No leí código de implementación.

**Delta de inventario para el orquestador:** no hay nodeids nuevos ni cambios de mapa. Los dos helpers preexistentes no listados tienen cero nodeids propios:

- `tests/install_backup_oracle.py`: helper de oráculos de respaldo del instalador; capacidad propuesta `generation-install-permissions`. Su docstring atribuye el contrato a una decisión del propietario del 2026-11-19; falta identificar un contrato documental recuperable antes de acreditarlo.
- `tests/install_harness.py`: helper de fixtures mínimos para tests del instalador; capacidad propuesta `generation-install-permissions`. La asignación se basa en su docstring y consumidores; el contrato recuperable sigue por confirmar.

Estas propuestas son metadatos para materialización, no acreditación semántica.
