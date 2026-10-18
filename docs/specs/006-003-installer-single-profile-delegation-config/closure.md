# Cierre de 006-003-installer-single-profile-delegation-config

**Feature:** 006-003-installer-single-profile-delegation-config · **Epic:** `epic-006-opencode-concurrency` (tercera feature) · **Cerrada:** 2026-10-18 · **Contrato:** `spec.md` con §8 (A-1..A-4) y §9 (A-5, del dueño) · **Plan:** `plan.md` con A-6 · **Aprobación:** orquestador Claude bajo la HITL delegada del epic-006; A-5, Memory Bank, ADR-033 y despliegue aprobados por Pablo.

## 1. Qué entrega

Instalador y generador sin perfiles ni mapa de modelos (ADR-033, que reemplaza ADR-007 y la parte de perfiles de ADR-008). El modelo de la delegación interna lo fija la configuración del runtime; el de la externa, `delegation.json` por destino y rol. CDAD no elige ni verifica la familia del reviewer (A-5). La credencial del servidor se carga desde un `.env` 0600, con un diagnóstico 401/403 autosuficiente. El instalador retira sus obsoletos propios intactos, preserva lo modificado y deja fuera de su manifiesto la configuración del usuario.

## 2. Gates

| Etapa | Evidencia |
|---|---|
| Construcción U1–U8 | RED→GREEN por unidad (`u*-red.md`, `u*-green.md`, testfixes); U5 abandonada por A-5 y reemplazada por U5'; GREEN de U7 detenido por B3 y resuelto con A-6; aceptación U8 en raíz redirigida (`u8-acceptance.md`) |
| Review | 0 bloqueantes, 7 opcionales, 3 abstenciones (`review.md`) |
| Review-fix 1 | O-1, O-2, O-4 (`rf-red.md`, `rf-green.md`); la afirmación sobre O-5 quedó refutada |
| Re-review focal 1 | B-1: el TSV leído con bash colapsaba columnas vacías (`rereview.md`) |
| Review-fix 2 | B-1 con registros separados por NUL + OPT-1 (`rf2-red.md`, `rf2-green.md`) |
| Re-review focal 2 | 0 bloqueantes; OPT-2 a deuda (`rereview2.md`) |
| Suite de cierre | 1177 passed, 5 skipped, 0 failed (`8638d06`) |
| Memory Bank | `activeContext.md`, `progress.md`, `systemPatterns.md`, ADR-033 y las marcas de reemplazo en ADR-007 y ADR-008 |

## 3. Abierto al cerrar

- **Deuda:** O-3 (precedencia de `XDG_CONFIG_HOME` del host frente a la raíz redirigida; decide el dueño), O-6 (XDG relativo), OPT-2 (comentario de symlinks en `install.sh`), DT-8.
- **Para 006-005:** abandonar un paquete despachado no lo libera; se pasó a `failed` a mano (`execution.md`).
- **Consumidor:** sus exec-configs con `model` cambian de modelo efectivo hasta que lo migre a `delegation.json` (D3).
