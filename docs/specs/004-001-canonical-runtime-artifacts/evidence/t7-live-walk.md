# T7 — recorrido vivo de capacidad (PD-11/12, criterio 6) — evidencia de RUNTIME

Fecha: 2026-09-29 19:35–19:47. Orquestador: Claude. Evidencia de permisos
efectivos en un runtime real, separada de la evidencia estática/instalada de
`tests/test_004_001_t7_capacity.py` (plan del epic: "no atribuir a una prueba
estática lo que no ejecutó").

## Alcance de lo que prueba (precisión de la review de GPT)

Este recorrido usa el **camino legacy sin paquete** y dice al agente que no
hace falta cargar skills. Demuestra la **capacidad operativa de los agentes
instalados** (permisos efectivos, herramientas, ciclo mínimo con commits) y
nada más. **No** demuestra el recorrido CDAD completo con paquetes y
contexto reducido: eso se comprueba en el próximo desarrollo real (004-002),
sin repetir este ejercicio sintético.

## Condiciones

- Runtime: OpenCode v2.0.16 (`~/.opencode/bin/opencode run --auto`), agentes
  `cdad-*` de la **instalación real** (`~/.config/opencode/agents`), idéntica a
  staging (`install.sh --check` rc=0). No se usó una raíz aislada para el
  runtime vivo: `OPENCODE_CONFIG_DIR` suma la config global en lugar de
  reemplazarla (probado: mofgw sigue visible con config aislada), así que un
  recorrido "aislado" no lo sería de verdad. El aislamiento de instalación se
  prueba en la parte estática.
- Proyecto consumidor sintético fuera del checkout
  (`~/.cache/cdad-verify-tmp/walk-repo`: `src/calc`, `tests/test_calc.py`,
  `docs/specs/sub/spec.md` con P1 `sub(a,b) = a-b`), sin el repo CDAD en el
  path. Camino legacy (sin paquete).
- Modelos: escritores `mofgw/glm-5.3-flash`; architect, reviewer y scribe
  `mofgw/deepseek-v4.1-flash` (familia distinta de los escritores).
- Script: una ejecución secuencial por rol, `timeout 900`; salida completa en
  `t7-live-walk.log`.

## Resultado por rol

| Rol | Modelo | Duración | Resultado |
|---|---|---|---|
| architect | deepseek-v4.1-flash | 42 s | midió con `rtk wc -l` (Σ=7 del propio comando, correcto), `git log`, spec verificable; sin ediciones |
| test-writer | glm-5.3-flash | 3 min 41 s | test de `sub` agregado, RED por la razón correcta, commit `4929170` |
| implementer | glm-5.3-flash | 5 min 9 s | `sub` implementado, suite 2 passed, commit `3dd73b6` |
| reviewer | deepseek-v4.1-flash | 1 min 3 s | RED reproducido, GREEN real, dictamen APTO sin bloqueantes (3 opcionales) |
| scribe | deepseek-v4.1-flash | 26 s | borrador de progreso como texto, sin escribir archivos |

## Permisos efectivos (escáner `opencode-session-scan.py`, 5 sesiones)

```
per tool  [ok, denied]: {'shell': (23, 0), 'read': (11, 0), 'edit': (3, 0), 'glob': (2, 0)}
per agent [ok, denied]: architect (7,0) test-writer (7,0) implementer (11,0) reviewer (8,0) scribe (6,0)
shell verbs: git 7, echo 5, python3 5, rtk 3, pwd 1, cat 1, set 1 — denied=0
```

**Cero rechazos de operación legítima** (criterio 4). Los lectores no editaron;
los escritores editaron solo su ámbito (test-writer → `tests/`, implementer →
`src/`). Las fronteras negativas (lector edita, test-writer lee `src/`,
implementer edita `tests/`) no se provocaron en vivo; su prueba es la parte
estática (evaluador sobre bytes instalados + ejecución real del path-guard CC).

## Fricción medida (insumo para 003-003)

- **F-W1 — `rtk wc -l <directorio>` falla en silencio semántico**: `rtk wc -l
  src/ tests/` imprime `0 src/`, `0 tests/`, `Σ 0` y sale con rc=1. El
  architect lo detectó, lo reportó como medición inválida y midió con archivos
  explícitos (Σ 7). Es la misma familia que F6 de T1 (fallos semánticos
  silenciosos de rtk). No es un rechazo de permisos; el costo fue ~4 llamadas
  extra.
- Aviso de `rtk` "No hook installed" en cada llamada: ruido de contexto, sin efecto.
- Sin bucles ni reintentos por permisos; ningún rol se acercó al techo de 300 pasos.
- Log saneado: identidad git del dueño y rutas de home redactadas (control A3).

## Fe de erratas (2026-09-29, review de GPT)

- El registro de cierre de T7 decía "45 llamadas". Lo correcto son **39**:
  7+7+11+8+6 por agente, igual que 23+11+3+2 por herramienta. Error de suma
  del orquestador, corregido en `c0-dispatch-record.md`.
- La primera anonimización del log fue incompleta: quedaban usuario y grupo
  en los listados `ls -la`. Ahora aparecen como `<user> <group>`.
