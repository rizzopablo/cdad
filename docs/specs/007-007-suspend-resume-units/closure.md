# Cierre 007-007-suspend-resume-units

Fecha: 2026-10-25. Epic: `epic-007-reliable-cycle-operation`. Colección de features: 4/7.

## Resultado

Una unidad se suspende en un borde seguro, se ejecuta otra y la primera se reanuda explícitamente, sin perder estado, identidad ni trazabilidad y sin repetir efectos.

- `suspend-unit --feature ID --reason TEXT` / `resume-unit --feature ID` (feature obligatoria; rc 2 con diagnóstico para entrada, coherencia, vigencia, seguridad o lock).
- `suspended_units` preserva valor y presencia/ausencia del estado de unidad; es una sola unidad ejecutable (no pila, no concurrencia).
- Borde seguro sobre los intentos de la ejecución, no sólo sobre `active_packet`.
- Reanudación verificada contra identidad, autoridad, política/versión, pins, aprobación y cadena.
- Checkpoints de suspensión/reanudación enlazados, sin `begin`, recibo ni ejecución nuevos.
- Matriz A2: ninguna entrada mutante avanza una suspendida; lecturas y validación de recibos siguen disponibles.
- `status`: `units-suspended`, `select-unit` (instrucción) y `next.alternatives` sólo con unidades elegibles.

## Evidencia

- Contrato: `spec.md` con ajustes A1–A5.
- Tests: `tests/test_007_007_suspend_resume_units.py` (19 casos; 16 en la versión aprobada por review).
- Review: 4 rondas, sesión `ses_e8ad5f723ffenb7IaCoN0egiCv`; final APTO CON AJUSTES, sin bloqueantes en el alcance MVP.
- Gate por superficie (`819ebe5`): 947 passed / 0 failed (antes del último fix); tras los fixes, conjuntos focales 19+52 verdes.
- Suite completa: 1582 passed, 38 failed — todos del RED de 007-004 (esperados).
- **Uso real (esta sesión):** `suspend-unit 007-004` rc 0 → `status` = `units-suspended`; `open-unit --feature 007-007` rc 0 con dependencia 007-003 verificada. Es la primera aplicación real de la capacidad.

## Excepción de arranque

La feature se desarrolló con despachos nativos sin `begin`/`record` ni recibo, porque el ciclo no permitía cambiar de unidad (carencia que la propia feature cierra). Sustituyen al recibo la spec aprobada, los commits y esta evidencia. La excepción queda **extinguida** con este cierre: la siguiente unidad (007-006) se abre por el ciclo normal.

## Deudas declaradas (no bloqueantes)

1. La clasificación gestionado/standalone de la continuidad se elude retirando además el registro canónico; no es frontera de seguridad y no habilita despacho.
2. Los escritores de continuidad no comparten el lock del proyecto (preexistente).
3. No se re-verifica la aprobación si el historial se borra a mano.
4. La identidad de la unidad la suministra el llamador (B1 de la ronda 1).
5. Contaminación entre tests en corridas grandes (HOME/XDG no aislados): pendiente de auditoría por capacidad.
