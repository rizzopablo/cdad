# Decisión del orquestador sobre review-t2 (2026-10-06)

**F1** (`allow` fabricado ante un objetivo no evaluable) afecta un criterio central y se corrige en una ronda, con un remedio de clase que cubre las cuatro condiciones de cierre del reviewer:
1. ~~deny fuera de raíz~~ **Enmendado por el dueño (2026-10-06): salir de la raíz del proyecto está habilitado por defecto.** Una operación fuera de la raíz ⇒ `allow`, con motivo honesto `outside project root: not governed by project policy`; nunca «within the declared scope». Solo se deniega lo que la política declara explícitamente.
2. Herramienta sin destino resoluble (bash y cualquier herramienta que no escribe) ⇒ `decision:"unknown"`, con un motivo honesto que nunca diga «within the declared scope». **No** es un deny: un rechazo no se fabrica, y un bash legítimo sigue siendo posible.
3. `read_scope` se consulta para las lecturas.
4. `path_policy` o `private_paths` con un tipo inválido ⇒ rc≠0 «policy invalid» (falla de forma explícita); si falta, se toma como vacía declarada.
5. `--role` distinto de `exec_context.role` ⇒ rc≠0, con un diagnóstico de inconsistencia.

Se incluye **O-B** (docstring con el tiempo verbal de la fase RED; es trivial). **O-A, O-C y O-D** pasan a deuda baja; O-D se declara como limitación en el contrato `preflight-v1`, dentro de esta misma ronda.

## Enmienda del dueño (2026-10-06)

«Sospecho que los permisos quedarán muy estrictos. En general salir de la raíz del proyecto lo habilito por defecto.» Se aplica a todo el preflight: es **consultivo**, informa al orquestador y no impide trabajo legítimo. `deny` solo cuando una regla explícita de la política o del scope del rol lo dice; en lo demás, `allow` honesto o `unknown`.

## Calibración posterior (dueño, 2026-10-06)
La severidad de `read_scope` y del preflight en general se ajusta con uso real, una vez integrada la feature completa (T5 y uso posterior). Queda como deuda de calibración y no bloquea.
