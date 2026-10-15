# Revisión de la spec y el plan — 005-007 (orquestador Claude, entre tramos)

Fecha: 2026-10-13. Objeto: spec `54877103…` y plan `1f636260…` (commit `e1b792a`).

## Dictamen

**Conforme; sin enmiendas.** El núcleo está bien planteado:
- detalle progresivo con un campo cerrado `detail`, sin debilitar el fallo cerrado del validador;
- tamaño de unidad por condiciones verificables, sin números inventados;
- plantillas que parten del recorrido de uso;
- fuente única para cada regla.

Los tres puntos del delta entraron como alcance (PD-7, PD-8 y PD-9), y la aceptación mide la misma
sesión de 005-003 §9. Bien medida la decisión de despachar el draft por sesión aislada en vez de
`cdad_delegate.py`.

## Observaciones para la etapa 3 (sin cambiar el contrato)

1. **PD-8 y el draft por la interfaz común.** La interfaz emite una sola parte `role-report`, y el
   draft del architect produce dos artefactos (spec y plan). PD-8 resuelve el informe de discovery,
   pero un draft recibido por `cdad_delegate.py` sigue sin poder materializarse en dos archivos. Si
   T4 no lo cubre, va a `debt.md` con su condición de cierre, sin hacer pasar la parte única como
   spec.
2. **`open-unit` y las dependencias.** Abrir «la primera `queued`» confía en el orden del plan. Si
   el plan declara dependencias entre features, `open-unit` las verifica o declara que no las
   verifica. No debe abrir en silencio una unidad cuya dependencia no está `done`.
3. **Simetría al cerrar.** Cerrar una feature también se hace hoy editando el state a mano. No entra
   en esta feature, pero conviene medirlo en la aceptación (comandos sobre el state al cerrar) y
   dejarlo como deuda si pesa.

## Verificación del cierre (orquestador Claude, 2026-10-13 07:00)

- Suite completa propia en un worktree fijado a `93e6d89`, **con `make staging`**: 887 passed /
  1 failed / 4 skipped. El fallo es la cota de 2,0 s del doble de OpenCode
  (`test_pd4_auto_false_omits_auto_flag`), inestabilidad ya conocida bajo carga. Aislado pasa 3 de 3.
- Los «4 failed + 6 errors» del cierre del orquestador no se reproducen. Los mismos tres módulos
  (`test_opencode_read_map_and_steps`, `test_role_packet_review_regressions`,
  `test_004_001_t7_capacity`) dan 18 passed, con `TMPDIR` y sin él. La causa más probable es que
  su worktree de cierre no corrió `make staging` (hay tests que dependen de `build/staging`, hallazgo
  ya registrado en 004-002). No es la familia F011/HOME que declaró. No son regresiones, pero la
  explicación del cierre está mal atribuida.
- **Deuda de proceso:** el procedimiento de la suite de cierre debe incluir `make staging` en el
  worktree fijado, o los tests deben declarar esa precondición en vez de fallar.
- En reposo, `status` da `next-unit` y nombra `open-unit`.
