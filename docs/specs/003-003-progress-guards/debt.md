# Deuda priorizada — 003-003

## Alta
- (ninguna tras la corrección del dueño; ver guards-ledger.md, Corrección)

## Media (antes alta)
- **G1 Grabador de producto desde la DB de OpenCode:** hoy es un script desechable. Debe cubrir tres puntos:
  - marcar los lanzamientos desacoplados (`&`, `nohup`, redirección a log) como `unknown`;
  - emitir una señal de fin de sesión sin entrega;
  - usar un digest de progreso por contenido.
  Ver `guards-ledger.md`, causas 1–4.
- ~~G2~~ retirada: el seguimiento por PID es del modo de despacho del orquestador, no del producto.

## Media
- T1 F1: traceback ante un archivo que no es UTF-8, aunque falla cerrado.
- Calibración de la severidad del preflight y de `read_scope`, con uso real (decisión del dueño).

## Baja
- T1: F2, O2, O3a/b/c.
- T2: O-A, O-C, O-D (declarada).
- T3: O3, O4; `budget` con un id absoluto (solo lectura).
- T4: O1–O3, N1–N3.
- Validadores: 2 FAIL preexistentes y ajenos a esta feature.
