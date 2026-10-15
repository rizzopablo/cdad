# Tarea 2 GREEN — renderer de paquetes

Fecha: 2026-09-17. Implementer en sesión separada, modelo solicitado
`gpt-5.6-sol`. Gate verificado independientemente por el orquestador.

Resultado focal:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_role_packet_render
Ran 11 tests in 75.019s
OK
```

Se ejecutaron las 100 entradas generadas con seed fijo y no apareció ningún
`BLOCKED`. T1 permaneció verde en la corrida del implementer: 2/2 pruebas.

Se implementaron `render`, `validate-request`, `validate-packet` y
`validate-metric`, junto con schemas y las instrucciones pequeñas common + rol
+ subfase. El máximo estático observado fue 1.095 bytes, debajo del límite de
12.000. La validación comprueba identidad, hash del contrato, canonicalización,
scopes por rol, paths seguros, alteraciones y métricas con desconocidos
explícitos.

Límites: todavía faltan consumidores, empaquetado/instalación del entrypoint,
documentación y paridad Task/chat (T3). No se ejecutó OpenCode E2E ni una
instalación global.

Status: GREEN verified by Codex (agent-delegated) on 2026-09-17.
