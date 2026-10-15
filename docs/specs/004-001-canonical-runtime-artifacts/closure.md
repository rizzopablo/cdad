# Cierre de 004-001 — canonical-runtime-artifacts

Fecha: 2026-09-29. Orquestador: Claude, con construcción delegada a los roles
CDAD de OpenCode. Verificación propia del orquestador en cada punto
("reproducido" = corrido por el orquestador, no tomado de un reporte).
Pendiente: aprobación del dueño para el merge y el Memory Bank.

## Criterios de aceptación (spec §4)

| # | Criterio | Estado | Evidencia |
|---|---|---|---|
| 1 | Matriz smoke runtime × rol (11 por runtime) × perfil soportado, desde instalación aislada, sin proveedor | ✅ reproducido | `tests/test_004_001_acceptance_matrix.py` (`5e12c0f`): 4 perfiles × 2 runtimes × 11 agentes = 88 celdas; frontmatter coherente con `cdad-models.sh`; `--check` rc=0 por perfil. 12/12 en mi corrida. Complementa la matriz base/odoo de T6. |
| 2 | Cero agentes editados a mano tras el generador (22 salidas declaradas); `install.sh` sin cambios de comportamiento al cierre del aterrizaje A | ✅ reproducido | Regenerar con `cdad-generate.py` (optimus, odoo, ambos runtimes) da salidas idénticas a los 22 archivos de `agents/`. Aterrizaje A cerrado con review-4 *approved*. |
| 3 | Los tres validadores en PASS o sus assertions migradas con trazabilidad (PD-10) | ✅ reproducido | consistency, odoo-specialization y subagents en PASS. T7a (`33bf757`, `c9f1448`) con tabla de trazabilidad; listas FORBIDDEN retiradas por decisión del dueño (`80f9b90`). |
| 4 | Recorrido de capacidad (PD-11) completo, cero rechazos injustificados | ✅ | Estático: `test_004_001_t7_capacity.py` (`881830e`, `c230d99`). Vivo: `evidence/t7-live-walk.md`, 5 roles, 39 llamadas, 0 denegaciones. Alcance: capacidad operativa por camino legacy; el ciclo con paquetes y contexto reducido se comprueba en 004-002. |
| 5 | Baseline PD-13 antes de la primera generación, con `rtk wc *` aterrizado, totales mecánicos y techo registrado | ✅ con desviación dispuesta | `evidence/baseline.json` (T1). `rtk wc` estaba bloqueado en esa sesión: se midió con `rtk rg -c` (mecánico, totales del comando) y el contraste externo coincidió dígito a dígito. Dispuesto en el PD-17 de T1. Techo PD-19 registrado (12.000). |
| 6 | Fricción medida en el primer recorrido real, entregada a 003-003 | ✅ | `docs/epics/epic-003-context-efficiency/friction-intake-004-001.md` (`95a5a62`), enlazado desde el handoff de 003-003. |
| 7 | PD-17 completo en T1–T7; la instalación no lee `sources/` (PD-18); exceso del techo produce error claro (PD-19) | ✅ | `c0-dispatch-record.md`: T1, T2, T3, T6, T7 y T4/T5 consolidados. PD-18: `tests/test_install_ownership.py`. PD-19: `tests/test_static_block_ceiling.py`. Ambos dentro de la suite. |

**Suite completa**: 132 passed (test-writer, `env -u TMPDIR`, 858 s) tras
`5e12c0f`; mi última corrida completa fue 120/120 antes de agregar la matriz
y el ajuste del log. Los archivos nuevos los corrí por separado: 12/12 y 22/22.

## Revisiones

review-1..6 (GPT/Codex), review-7 (Claude, T6) y la review externa de GPT
del 2026-09-29 sobre T7. Todos los bloqueantes cerrados.

## Desviaciones relevantes (detalle en PD-17)

- Salidas de ámbito de los agentes para esquivar obstáculos (install en el
  HOME real en T6; `git stash` sobre estado compartido en T7). Sin pérdida.
  Disposición: principio explícito en el paquete + árbol limpio antes de
  despachar + verificación posterior. Sin barreras nuevas.
- Durante la matriz, un intento de instalación sin `CDAD_INSTALL_ROOT` falló
  en una precondición antes de escribir. El HOME real se verificó intacto.
- Errores del orquestador corregidos: log con identidad del dueño (A3), 45 →
  39 llamadas, anonimización incompleta, criterios contados como 6.

## Observaciones para después (no bloquean el cierre)

- `install.sh` exige un directorio `agents/` junto al script aunque despliega
  solo desde staging (PD-18 intacto: los bytes vienen de staging). Candidato
  a limpieza en 004-002.
- 004-002: derivar las raíces de implementación desde `path_policy` (hoy
  read/grep del test-writer solo ocultan `src/**` y `lib/**`).
- `steps: 300` no se probó forzando un bucle.
- Verificar en 004-002 el recorrido CDAD completo con paquetes y contexto
  reducido, sobre trabajo real.

## Hallazgo posterior al cierre (2026-09-29, gate 002 de 004-002)

La prueba estática PD-12 de Claude Code (`test_004_001_t7_capacity.py`)
bloqueó `Grep`/`Glob` con un JSON sintético que traía `file_path`, una forma
que las herramientas reales no envían. `claude-code-path-guard.sh` deja pasar
toda llamada sin `file_path`. Por eso, en uso real, **Grep y Glob no están
mediados** en Claude Code: el negativo de esas dos herramientas estaba
sobredeclarado. `Read` sí quedó probado con su forma real. Corrección y
prueba: 004-002, T5 (`spec-gate-claude-002.md`, C2). No se reabre 004-001.
