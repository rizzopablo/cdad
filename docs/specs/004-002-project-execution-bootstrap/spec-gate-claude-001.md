# Gate de spec — revisión de architect-draft-001 (004-002)

Fecha: 2026-09-29. Revisor: Claude (orquestador; familia distinta del
architect, Codex gpt-6-astra). Verificaciones propias y un spike en runtime.
Sin modificar código.

## Dictamen

```
dictamen: changes-required antes de aprobar (el borrador es sólido)
blocking: 2  (G1 mecanismo de PD-8; G2 recorrido real de PD-13 sin nombrar)
data:     1  (G3 consumidores reales para D2)
optional: 2
```

Lo que el borrador hace bien: el discovery cita código real (verifiqué el
HEAD `bcaf296`; coincide). Separa la identidad lógica de las observaciones
por intento, lo que resuelve la limitación runtime/modelo sin inventar datos.
Mantiene un solo productor (`prepare`). Deja explícitas D1–D4 con alternativas
y costo.

## G1 — PD-8 promete un mecanismo que hoy no existe (bloqueante)

PD-8 dice que los adaptadores "consumen la política efectiva". Hoy los 11
agentes CDAD se instalan de forma **global** (`~/.config/opencode/agents`),
el repo no tiene configuración `.opencode/` ni `.claude/` propia, y
`claude-code-path-guard.sh` no lee ninguna política. El propio architect lo
marcó como VERIFY, pero lo redactó como postcondición cumplible.

**Spike del orquestador (2026-09-29, OpenCode 2.0.16, glm-5.3-flash):**
proyecto sintético con `.opencode/agents/cdad-test-writer.md`, copia del
global más `"scripts/**": deny` en `read`.

| Corrida | `read scripts/tool.sh` | `read tests/test_x.py` |
|---|---|---|
| Con agente de proyecto (`--standalone`) | **denegada** (`Permission denied: read`) | permitida |
| Control sin `.opencode/` (`--standalone`) | **permitida** (leyó el contenido) | — |

Conclusiones:
- En OpenCode, un agente de proyecto reemplaza al global del mismo nombre y
  `opencode run` lo aplica. Existe un mecanismo verificable.
- El control confirma en vivo la fuga que 004-001 dejó pendiente: con los
  agentes globales, el test-writer lee `scripts/` (implementación de este
  repo).
- Salvedad: con el servicio de fondo (sin `--standalone`) la primera corrida
  se colgó sin crear sesión (timeout 300 s). No se aisló la causa.
- Claude Code: el guard es un script, así que podría leer la política en
  tiempo de ejecución. Es plausible, **no está probado**.

Pedido: PD-8 debe elegir un mecanismo concreto (decisión del dueño **D5**) y
decir cómo se verifica su activación:
- (a) generación por proyecto de agentes OpenCode en `.opencode/agents/`
  desde la política, más guard CC que lea la política en tiempo de ejecución;
- (b) mapas globales genéricos con una limitación declarada, donde los scopes
  del paquete y un guard CC dinámico llevan la política.

## G2 — PD-13 no nombra el recorrido real (bloqueante; decisión D6)

"Una tarea real autorizada del consumidor" no identifica ni proyecto ni
tarea. Recomendación: que el recorrido real sea **la propia ejecución de
004-002**, que ya corre por paquetes (este architect se despachó con
`prepare` a Codex) y seguirá así con test-writer e implementer. Coincide con
la review de GPT: no repetir un ejercicio sintético. La alternativa es que el
dueño nombre otro proyecto y tarea.

## G3 — D2 debe decidirse con datos de consumidores reales

Comprobación acotada del orquestador (`projects/*/.cdad/execution.json` y
`projects/*/docs/.cdad-state.json`, dos niveles):
- `execution.json` v1: **solo este repo**.
- Proyectos con CDAD por camino legacy (state sin contexto de ejecución):
  ocho proyectos del dueño (nombres omitidos).

Consecuencias: para D2 alcanza una **migración única y explícita** de este
repo; mantener v1 legible solo para paquetes históricos. El modo
**standalone/legacy** (PD-12, D4) tiene 8 consumidores reales: su camino no
debe romperse y merece un caso de prueba representativo.

## Opcionales

- O1 — Invariante nuevo: el archivo de política queda fuera del ámbito de
  escritura de todos los roles y solo cambia con `--reconcile-policy` y una
  decisión del dueño. Quien construye no edita sus propios límites (la regla
  anti-trampa de CDAD, aplicada al artefacto nuevo).
- O2 — `--record-dispatch` debe quedarse del lado de `prepare` (registro del
  intento) y no deslizarse a la recepción de resultados de 003-002. Los tests
  deben sostenerlo.

## Nota de orquestación

El architect se despachó con `--ephemeral`, así que su sesión no se puede
retomar. La revisión será un despacho nuevo con `architect-draft-001.md` y
este gate como entradas. Los roles iterativos de Codex se despacharán sin
`--ephemeral`.
