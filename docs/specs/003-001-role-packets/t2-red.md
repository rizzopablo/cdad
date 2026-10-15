# Tarea 2 RED — renderer de paquetes

Fecha: 2026-09-17. Rol: test-writer en sesión separada, modelo solicitado
`gpt-5.6-sol`. Gate validado por el orquestador.

Comando focal:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_role_packet_render
```

Resultado reproducido: **11 métodos, 16 fallos, exit 1**. Los fallos son
contractuales: la CLI pública existe, pero `render`, `validate-request` y
`validate-metric` responden `invalid choice`. No son errores de importación ni
ausencia del ejecutable.

La batería agrega 136 casos: las 13 parejas rol/subfase, determinismo,
delimitación y límite de 12.000 bytes de instrucciones, metadata canónica,
tampering, hashes, traversal/symlink, scopes por rol y archivo exacto, métricas
e identidades. Incluye 100 requests generados con seed fijo; se ejecutarán
cuando exista un render válido. Los casos dependientes informan `BLOCKED after
primary RED`; el gate final exige cero bloqueados.

Archivo de test: `tests/test_role_packet_render.py`. El test-writer no leyó ni
modificó implementación, agentes, skills o instalación. No hubo instalación
global. Log original de transporte: `/tmp/cdad-003-001-t2-red.log`.

Mapeo: P1 composición/determinismo/tamaño; P2 integridad, paths y alteraciones;
P3 permisos por rol; P5 métricas. P4 ya tiene GREEN parcial en Tarea 1. P6 y la
integración completa permanecen pendientes de Tarea 3.

Status: RED verified by Codex (agent-delegated) on 2026-09-17.
