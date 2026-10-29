# Cierre — epic-009-installer-updates

Fecha: 2026-10-29 UTC. Resultado: **2/2 features cerradas**.

## Entrega

- **009-001-installer-agent-overlay:** conserva el `model:` del usuario al actualizar agentes; mantiene propiedad y verificación cuando la base es acreditable, y preserva como conflicto las modificaciones restantes. Cierre individual: `docs/specs/009-001-installer-agent-overlay/closure.md`.
- **009-002-opencode-v2-frontmatter:** generador y agentes derivados emiten V2 nativo; las reglas y su orden se conservan. OpenCode 2.2.0 real reconoció modelo y variante en los 11 agentes, y una actualización V1→V2 preservó el modelo. Cierre individual: `docs/specs/009-002-opencode-v2-frontmatter/closure.md`.

## Criterios del plan

1. **Cierres individuales:** ambos con evidencia PC-1…PC-7 y revisiones independientes.
2. **Validación:** instalación y `--check` en arena externa, rc 0; `make validate` 68/68. Gate completo sobre `1772563`: GREEN, **1844 passed, 5 skipped, 0 failed**, árbol limpio, resumen verificado y atribución verdadera. Evidencia: `.cdad/local/009-002/gate-final/gate-20261029T011218177492Z-2292973-b28d0e32/`.
3. **Sin modelo distribuido:** el generador no selecciona modelo; éste pertenece al usuario. Claude Code no cambia en 009-002.
4. **Sin semántica duplicada:** el helper de overlay es único; los oráculos de permisos comparten lector V1/V2. El instalador no agrega un conversor posterior al generador.
5. **Publicación:** 009-001 fue publicada por instrucción expresa del dueño en `9fc90b1`; este cierre no publica 009-002 ni instala sobre el HOME real.

## Retrospectiva

El fix de representación alcanzó dos productores: agentes estáticos y derivados por proyecto. Actualizar sólo el primero producía YAML híbrido en el segundo. Las revisiones independientes detectaron además helpers compartidos incompatibles y mutaciones PD-10 que seguían ancladas a V1; se repararon sin retirar las barreras.

La primera corrida completa de 009-002 fue roja por dos oráculos V1 restantes; se conservó esa evidencia, se corrigieron con controles negativos y se verificó el commit nuevo. No se promediaron intentos ni se trató un skip como pase. La espera se hizo mediante finalización nativa de la tarea en segundo plano, sin sleeps de sondeo.

## Deuda y siguiente trabajo

Se conservan los límites de ambos cierres: inventario histórico incompleto, temperatura del reviewer derivado desde una fuente V1 antigua hasta reinstalar, overlay limitado a `model:` y formatos admitidos, conflictos por modificaciones externas y los diferibles del instalador. La premisa de que todo agente V1 ignora modelos no se generaliza: la revisión encontró un caso V1 de proyecto que sí resolvía modelo.

Documentación pública y eficiencia de selección/ejecución de tests fueron solicitadas para después de esta entrega; no se implementaron en este fix. No hay nueva ADR: la representación cambió, la política se conservó.
