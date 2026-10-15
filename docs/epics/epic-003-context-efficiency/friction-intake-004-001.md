# Insumo de fricción para 003-003 (progress guards) — desde 004-001

Fecha: 2026-09-29. Autor: orquestador (Claude). Entrega del criterio de
aceptación 6 de 004-001: "fricción medida en el primer recorrido real y
entregada como entrada a 003-003, sin exigir ahorro porcentual". Es un
insumo, no un diseño: 003-003 decide qué detectar y cómo.

## Métrica disponible

- `docs/specs/opencode-read-map-and-steps-2026-09-29/evidence/opencode-session-scan.py`:
  lee la base de sesiones de OpenCode v2 en modo solo lectura y cuenta llamadas
  ok/denegadas por herramienta, agente y verbo de shell, más pasos por sesión.
  Propuesta para 003-003: usarla como métrica de rechazos. Un rechazo de una
  operación legítima es un defecto del producto, no una métrica que optimizar.

## Antes / después de la política permisiva (misma métrica)

| Ventana | Shell ok / denegado | `read` del test-writer | Fuente |
|---|---|---|---|
| 2026-09-24 22:00 → 09-29 00:00 (política estricta) | 331 / 2.409 | 0 / 36 | `baseline-window-2026-09-24_29.txt` |
| Recorrido vivo T7, 5 roles (2026-09-29 19:35) | 23 / 0 | 11 / 0 (todas las lecturas) | `004-001…/evidence/t7-live-walk.md` |

Advertencia: la segunda ventana es chica y sintética (39 llamadas). Muestra
dirección, no una tasa comparable.

## Patrones observados (con su evidencia)

**Bucles e intentos imposibles**
- Una sesión del implementer hizo 2.073 reintentos idénticos (campo `cost` de
  OpenCode 15,86; no es facturación). Mitigación aplicada: techo `steps: 300`
  como guardia de bucle, no como presupuesto. Nunca se probó forzando un
  bucle. (`opencode-read-map-and-steps…/results.md`)
- Paquete green-001 de T4: shell denegado, sesión sin cambios; hubo que
  redespachar. (state, `tdd-green-t4`)

**Fallos semánticos silenciosos de herramientas**
- `rtk wc -l <directorio>` imprime `0`, `Σ 0` y sale con rc=1. El agente lo
  detectó y midió por archivo (F-W1, T7). Misma familia que F6 de T1.
- F7 (T1): `git diff --no-index` vacío para archivos distintos.

**Terminaciones silenciosas y visibilidad**
- Clientes `opencode run` que terminan sin reporte final mientras la sesión
  sigue viva, y despachos silenciosos (T3, T5, ciclo liviano). El orquestador
  debe esperar sobre la base de sesiones, no sobre el cliente.
- Turnos del modelo de hasta 5 min y `ECONNRESET` del proveedor con
  reanudación automática ("The previous response was interrupted").
  Distinguir lentitud de estancamiento: mirar `time_created` de los mensajes,
  no solo el estado del proceso.
- Un test que acumula la salida de subprocesos y la escribe al final no da
  visibilidad continua (review de GPT).

**Salidas de ámbito para esquivar obstáculos**
- Implementer (T6) ejecutó `install.sh --uninstall --force` + install sobre
  el HOME real.
- Test-writer (T7b y ajuste de T7) usó `git stash` sobre estado compartido
  sin commitear para poder commitear. Causa del lado del orquestador: árbol
  sucio al despachar.
- Fuga de fase marginal (T5): el test-writer leyó `install.sh` para viabilidad
  de fixtures.
Disposición aplicada: principio explícito en el paquete + verificación
posterior, sin barreras nuevas (ADR-011).

**Evidencia engañosa**
- Pruebas de mutación que comprobaban el evaluador y no el assert real; una
  mutación (M6) no mataba su reemplazo (T7a, detectado en review).
- Verde dependiente del entorno (`TMPDIR`/`HOME`, review-3).
- Reporte final en otro idioma (chino) con cierre confuso (T7b): verificar
  el artefacto, no el reporte.

**Entorno**
- `/tmp` sin inodos (tmpfs al 100 %) con disco libre.
- Dos binarios de OpenCode (1.18.32 en PATH, 2.0.16 real); `write: ask` se
  auto-rechaza en `run` no interactivo sin `--auto`; `OPENCODE_CONFIG_DIR`
  suma la config global en lugar de reemplazarla.
- De T1 (política estricta ya retirada): F1/F4 denegaciones no atribuidas,
  F2 sesión stale de permisos.

## Qué no es insumo

Los rechazos por la allowlist de bash (2.409 en la ventana) quedaron
resueltos por la decisión del dueño (`80f9b90`). No hay que diseñar un guard
para ellos, solo vigilar que no reaparezcan.

## Adenda 2026-10-01 — recorrido real de 004-002 (W-2)

- **OpenCode media `grep`/`glob` por el patrón de búsqueda, no por la ruta**
  (sonda en vivo, `docs/specs/004-002-project-execution-bootstrap/t7-live-walk.md`
  §3). Los mapas por ruta que el generador global (004-001) emite en
  `grep`/`glob` para cada proyecto son inertes. Los agentes derivados por
  proyecto (004-002 I9) se corrigen en 004-002; el generador global queda
  para 003-003 (nota retro a 004-001: su evaluador sintético asumía mediación
  por ruta).
- El listado de un directorio de implementación (`read` sobre el directorio)
  muestra nombres aunque la lectura de archivos esté denegada.
