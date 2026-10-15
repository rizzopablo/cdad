# Deuda declarada — 005-007-progressive-planning

Fecha: 2026-10-13. Cada entrada con **condición de cierre**. Lo que no cierra la feature va aquí como **deuda
declarada**, nunca como omitido (documented debt ≠ hidden debt). Esta lista complementa la deuda de la spec (§8)
y la medición de `acceptance.md`.

| # | Deuda | Origen | Condición de cierre |
|---|---|---|---|
| D-1 | **Medición de uso con la VERSIÓN DESPLEGADA** en una sesión nueva (like-for-like de `005-003/acceptance.md` §9). | spec §8 D-1; `acceptance.md` §4 | Autorización de despliegue del dueño + una sesión real nueva en reposo medida con el medidor del repo. **BLOQUEO declarado** mientras no se despliegue (acción reservada al dueño). |
| D-2 | Detección de despacho del medidor con **prefijos de envoltura** (`time`, `env`, `nohup`, `nice`, `sudo`, `bash -c`): la invocación real envuelta NO se detecta (falso negativo observado en la traza real del orquestador). | `acceptance.md` §2; evidencia: ledger `dispatches/delegate-opencode-2ac2addcb404.json` + medidor `first_dispatch: absent` | Extender el detector a los prefijos de envoltura y cubrirlo con un oráculo focal. **Exigible ya** por una traza real (la práctica del repo envuelve despachos con `nohup bash -c`). |
| D-3 | **El cierre de una unidad sigue siendo manual** (simetría de `open-unit`, observación 3 de la revisión Claude): 19 operaciones de estado en el cierre de esta feature, ninguna del CLI. | `acceptance.md` §2; `review-claude-spec-2026-10-13.md` obs. 3 | Un subcomando que cierre la unidad con el mismo esquema que `open-unit` (escritor único, escritura atómica, sin edición manual) y su oráculo de comportamiento. |
| D-4 | **Un draft del architect entregado por `cdad_delegate.py` llega como UNA sola parte** (`role-report`) y no puede materializarse como `spec.md` + `plan.md`; PD-8 hace materializable el informe, no la partición. | `review-claude-spec-2026-10-13.md` obs. 1; informe de T4 | Que la entrega declare partes por artefacto (o que la interfaz soporte multi-parte) sin hacer pasar la parte única como spec. |
| D-5 | **Refuerzo material de la detección de despacho** por corroboración con el ledger durable (`dispatches/<attempt>.json`), manteniendo el medidor como lector de sesiones. | spec §8 D-4 | Solo si se observa un falso negativo que el refuerzo por invocación no cubra (ver D-2). |
| D-6 | **Formato del bloque como asset** (`plan-tasks.schema.json`) en lugar de la declaración única en `planning-contract-draft.md` §4.1. | spec §8 D-5 (alternativa de D1) | Decisión del dueño; hoy el formato vive en un solo lugar correcto. |
| D-7 | **VERIFY 6/7 del discovery** (sesión de cierre de 005-001 `unknown` en el medidor; ruta del CLI en Claude Code para 005-004). | spec §8 D-2/D-3 | Por su feature/owner; se citan, no se reabren aquí. |
| D-8 | **Datos del proceso**: tres defectos de oráculo detectados por el gate del orquestador (fixture de T2 que no omitía el campo; helper de T5 que recibía el documento; y la bandera `--delegation-dispatch` fijada por el oráculo y no nombrada literalmente en la spec). | `acceptance.md` §6; registros `tdd-*` del state | Que el reviewer juzgue si la práctica del oráculo necesita refuerzo (p. ej. exigir al test-writer que todo caso negativo pruebe que el fixture cambia el hecho) y que el contrato nombre los campos que el oráculo va a fijar. |

**Pre-existente, NO de esta feature** (declarado para que no se confunda con una regresión): `make validate`
141 PASS / 2 FAIL (F011: `scripts/validate-subagents.sh` y `tests/validate-odoo-specialization.sh`); suite completa
871 passed / 9 skipped / 4 failed + 6 errors idénticos al commit base `99e2f2e` (familia F011/instalados).
