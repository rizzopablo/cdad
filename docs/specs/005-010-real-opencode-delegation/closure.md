# Cierre — 005-010-real-opencode-delegation

Fecha: 2026-10-11. Orquestada por Claude (excepción de `execution.md`, «ok: a» del dueño), con
los roles en OpenCode. Corrió entera con la versión instalada al empezar (`6f4d5db`). La versión
nueva queda en el repo; desplegarla es decisión del dueño.

## 1. Resultado

El adaptador OpenCode de 005-009 completa un recorrido real Claude → OpenCode → `receive` →
re-entry. Contra el runtime instalado (v2.0.26) era inoperable: exigía `mode: all`, esperaba una
señal que solo escribía el doble de los tests y hacía correr al rol en el directorio del
coordinador.

## 2. Criterios de aceptación (spec §4)

| Criterio | Estado | Evidencia |
|---|---|---|
| PD-1/INV-3/INV-4 señal durable, solo lectura, correlación, espera acotada | cumplido | T1; `tests/test_005_010_t1_durable_signal.py` |
| PD-2 fallo cerrado ante esquema o archivo inválido | cumplido | T1; variantes `unknown-schema`, `not-sqlite` |
| PD-3/INV-6 `mode: subagent` despacha; identidad desde la fila; sin fallback | cumplido | T2; `tests/test_005_010_t2_load_mode_invocation.py` |
| PD-4/INV-7 `--standalone`, `--server`, `--auto`, stdin; `PWD` = proyecto | cumplido | T2 y T2b; `TestPd4PwdProjectDirectory` |
| PD-5/INV-5 clasificación por `idle_outcome`; recibo `pending` | cumplido | T1 y review-fix R1/R3 |
| PD-6 I8 del worker desde la fila | cumplido | T1 y review-fix R2 (`proveedor/modelo`) |
| PD-7 doble SQLite fiel | cumplido | `tests/test_005_009_t2_opencode_adapter.py` |
| PD-8 integración opcional contra el binario real | cumplido | `tests/test_005_010_t4_integration.py`: omitida por defecto; habilitada, 1 passed |
| PD-9 aceptación en dos pasos | **paso a cumplido**; paso b pendiente del despliegue | `evidence/pd10-acceptance.md` |
| PD-10/INV-7 referencias actualizadas, sin valores del host | cumplido | T3; `tests/test_005_010_t3_references.py` |
| Suite completa y validadores | cumplido | 763 passed / 2 skipped en un worktree fijado a `3e556a8`; `validate-consistency` con los 2 FAIL preexistentes (F011, A3) |

## 3. Gates

- Review formal única (reviewer de otra familia que el implementer): 1 bloqueante (R1) y 6
  opcionales. R1–R4 corregidos; R5–R7 a deuda (`review.md`).
- La suite de cierre corrió sobre `3e556a8`. Los commits posteriores (`890ece2`, `bc056d7`) solo
  tocan la prueba de integración, que se omite por defecto; esa prueba se corrió habilitada contra
  OpenCode real después de `bc056d7`: 1 passed.
- Recorrido PD-10 repetido con una instalación aislada de `3e556a8`: `completed`
  (`<ses-143>`), `model_reported` `proveedor/modelo`,
  `reconcile: received`, re-entry `VALID`.

## 4. Deuda y pendientes

- R5–R7 de la review (memoria de `fetchall`, numeración del docstring, encoding del URI SQLite).
- Paso b de PD-9: confirmación corta desde la instalación global después del despliegue.
- Plan del epic: el dueño y Codex lo editaron durante este ciclo (sección «Ajuste de los ciclos
  pendientes», fuera de 005-010). La última aprobación registrada en `epic_history` fija
  `996dd7e0…`; la próxima feature necesita registrar la aprobación de la versión vigente antes del
  `prepare` de su architect.
- Patrón repetido: un rol cerró su turno esperando la suite en segundo plano, sin commitear.

## 5. Despliegue (tarea del dueño)

Script `.cdad/local/deploy-005-010-home.sh <commit>` (respaldo, worktree fijo, perfil `basic`,
instalación y chequeo). Después hay que reiniciar o recargar el servidor de OpenCode y avisar al
orquestador para el paso b.

## 6. Reapertura por B1 (2026-10-11)

La verificación posterior de Codex (`review-codex-2026-10-11.md`) encontró B1: si el último
mensaje `assistant` no tenía texto, `_last_assistant_text` tomaba el de un mensaje anterior y
clasificaba `completed` en vez de `blocked` (PD-1/PD-5). El dueño aprobó corregirla con el mismo
esquema; la orquestó Claude con HITL delegada.

- RED `1b62f5d` (test-writer): `tests/test_005_010_b1_last_assistant.py`, con un caso que falla
  por comportamiento y una regresión multi-texto. El oráculo `durable_last_assistant_text` del
  doble queda alineado al último mensaje.
- GREEN `7a2ed0a` (implementer): `ORDER BY seq DESC LIMIT 1` y `None` sin texto. De paso resuelve
  R5 (`fetchall`). Gate: 39 passed / 1 skipped.
- La review es la de Codex; el orquestador revisó el diff (1 archivo, +9/−7). No hubo otra review
  formal, por proporcionalidad.
- Integración real habilitada sobre `7a2ed0a`: 4 corridas, 2 passed. En las otras 2, el modelo se
  negó a repetir el token fijo (lo tomó como inyección); la tubería y la entrega funcionaron.
  Deuda: el oráculo de T4 depende de que el modelo obedezca.
- Barrido de solo lectura de 400 sesiones `succeeded` de la base: solo 1 termina con un último
  `assistant` sin texto (sesión interactiva, no un rol). Su texto anterior era un avance
  intermedio, justo el caso de B1, así que `blocked` es lo correcto.
- Suite completa en un worktree fijado a `7a2ed0a`: 765 passed / 2 skipped (15 min).
- Despliegue pendiente: espera a que el otro proyecto activo esté en reposo (decisión del dueño); después, la
  confirmación corta de PD-9(b) con la versión nueva.
