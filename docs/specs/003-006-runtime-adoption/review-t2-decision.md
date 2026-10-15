# Decisión sobre review-t2 — 003-006 (orquestador, delegación HITL)

- **B-1 (aceptado como bloqueante):** contención de ruta. Si `R/.claude` es un enlace a
  `~/.claude`, la activación escribiría y podaría en la configuración del HOME real. Es justo
  lo que prohíbe I1. Cierre: antes de escribir o podar, cada destino (y cada componente
  intermedio) se resuelve con `realpath` y debe quedar estrictamente bajo
  `realpath(project_root)`. Si no, el conflicto se nombra, rc≠0 y no se escribe nada (todo o
  nada). Lo mismo para la poda. Se cubre con un review-fix RED → GREEN.
- **O-4 (se absorbe en el cierre de B-1):** resolver `realpath` de `--project-root` y
  `--adopted-root` al validar los argumentos.
- **O-1, O-2, O-3, O-5:** a deuda (`debt.md`).
