# Tarea 3 RED — consumidores e instalación

Fecha: 2026-09-17. Test-writer en sesión separada, modelo solicitado
`gpt-5.6-sol`. Gate reproducido por el orquestador.

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_role_packet_consumers
Ran 5 tests
FAILED (failures=6)
```

No hubo errores ni casos `BLOCKED`. La preservación de permisos críticos en la
instalación aislada ya pasa. Los seis fallos contractuales cubren consumidores
que todavía recargan el ciclo completo, ausencia del entrypoint instalado
exacto, falta de paridad desde un proyecto consumidor y dependencia Python 3
no publicada en README/ayuda del instalador.

La prueba realizó una instalación bajo una raíz temporal explícita, sin cambiar
`HOME` ni tocar la instalación real. No ejecutó OpenCode ni proveedores.

Archivo: `tests/test_role_packet_consumers.py`. Mapeo: P3 preservación y consumo
por paquete; P6 instalación, paridad y dependencia pública.

Status: RED verified by Codex (agent-delegated) on 2026-09-17.
