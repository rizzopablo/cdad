# 005-011 — T4: aceptación de uso con la versión desplegada (`c2c04b4`), 2026-10-13

La corrió el orquestador Claude en clones descartables. La instalación global se desplegó en `c2c04b4`. Su huella quedó igual antes y después (`14f78503…`).

## AC-7 — Claude Code: cumplido en el orden de entrada, mejora parcial

**Escenario:**
- **Proyecto:** un clon de HEAD con un paquete de reviewer de solo lectura preparado. Es el mismo escenario que `005-004/t5-acceptance.md`.
- **Coordinador:** `claude -p` nuevo, lanzado desde un directorio confiable que no carga la memoria del proyecto, con la instrucción breve habitual.
- **Medición:** conteo propio sobre el transcript.

| Hasta el primer despacho | Línea base (005-004 T5) | Ahora |
|---|---:|---:|
| Primera acción después de la skill | leer el state completo (llamada 2) | `status` (llamada 2) |
| Llamada del primer `Agent` | 23 | 22 |
| Salida previa | 105 mil car. | 80 mil car. (−24 %) |
| Tiempo y costo de toda la sesión | 8,7 min, 3,88 USD | 3,9 min, 1,69 USD |

**Lo que sigue pendiente:**
- leyó el plan, la spec y `orientation.md`;
- corrió aparte el chequeo de versión, que repite lo que ya dice `status`;
- falló dos veces `--record-dispatch` por uso: faltaba `--attempt-id` y el `attempt.json` llevaba campos de más.

El rol respondió bien los tres ítems del oráculo.

## AC-6 — OpenCode: NO cumplido

**Escenario:**
- **Proyecto:** un clon en el reposo real de `d16708e`, con 005-011 en cola, el producto de `c2c04b4` como fixture y sin artefactos de 005-011. Es la misma situación que la línea base.
- **Coordinador:** el mismo prompt mínimo y el mismo agente que la línea base.
- **Medición:** el medidor de 005-002, más conteo propio por llamada.

Una primera corrida no es válida: mezcló artefactos actuales de 005-011 con un reposo anterior y dejó los archivos del lanzador en la carpeta de al lado. El error es del lanzador, y se descarta.

| Hasta el primer despacho | Línea base (005-007 §7) | Ahora |
|---|---:|---:|
| Primera acción | leer el state | leer el state (llamadas 2–6, cuatro lecturas, unos 186 mil car.) |
| Carga de la skill | llamadas 1–2 | llamada 10 |
| `status` | llamada 21 | llamada 13 |
| Llamada del primer despacho (medidor) | 71 | 77 |
| Salida previa | 304 mil car. | 400 mil car. |
| Tiempo hasta el despacho | 5,8 min | 13,8 min |

**Causas:**
1. **La entrada real de OpenCode es el prompt del agente `cdad-orchestrator`, no la skill.**
   - Ese prompt (`sources/roles/orchestrator.md:110`) dice que `resume` es «the first step of every new session» y no menciona `status`.
   - T2 excluyó el agente de forma explícita, porque no es el texto común entre runtimes. Por eso la corrección no llegó a OpenCode.
   - En Claude Code la skill se cargó primero; por eso ahí mejoró.
2. **Duda sobre el medio de despacho** (llamadas 50–77):
   - el orquestador registró un intento por subagente;
   - lo retiró porque el paquete no se puede tipear byte a byte dentro del prompt;
   - terminó despachando por `cdad_delegate.py` y lo declaró en un erratum.

   Es la misma fricción que RD-9 de 005-004.

**Disposición:** compromete el resultado de la feature, así que bloquea según el criterio vigente. Se abre la corrección T2b: el prompt del orquestador entra por `status`. Después se redespliega y se repite AC-6.

## Repetición con `7212ead` (T2b desplegada), 2026-10-14

La huella de la instalación global quedó igual antes y después (`2202423d…`).

**Claude Code:** mismo escenario que la corrida anterior, con una sesión nueva y conteo propio.

| Hasta el primer despacho | Línea base | 1.ª corrida | Esta corrida |
|---|---:|---:|---:|
| Primera acción después de la skill | state completo | `status` | `status` (llamada 2) |
| Llamada del primer `Agent` | 23 | 22 | 14 |
| Salida previa | 105 mil car. | 80 mil | 54 mil (−49 %) |
| Duración total | 8,7 min | 3,9 min | 3,0 min |

**OpenCode, corrida 2: no mide T2b.**
- En OpenCode, el agente derivado del proyecto (`.opencode/agents/cdad-orchestrator.md`) tiene prioridad sobre el global.
- El que había en el clon venía del despliegue anterior, sin T2b. Se republicó recién con el `prepare` de la propia sesión, a mitad de la corrida.
- **Hallazgo de producto (RD nuevo):** después de un despliegue, la primera sesión de cada proyecto arranca con el orquestador derivado viejo. El DRIFT de la pata `project` lo anuncia, y la vista dice que el próximo `prepare` lo resuelve, pero la entrada ya ocurrió antes de ese `prepare`.
- Datos de esta corrida, solo como referencia: despacho en la llamada 50, 287 mil car., 6,5 min.

**OpenCode, corrida 3: agentes del proyecto ya republicados en `7212ead`.** Medidor más conteo propio.

| Hasta el primer despacho | Línea base (005-007 §7) | 1.ª corrida (`c2c04b4`) | Corrida 3 (`7212ead`) |
|---|---:|---:|---:|
| Carga de la skill | llamadas 1–2 | llamada 10 | llamada 1 |
| Primera lectura del state completo | llamada 3 | llamada 2 | llamada 2 (53 mil car.) |
| `status` | llamada 21 | llamada 13 | llamada 3 |
| Llamada del primer despacho | 71 | 77 | 59 (−17 %) |
| Salida previa | 304 mil car. | 400 mil | 296 mil (−3 %) |
| Tiempo hasta el despacho | 5,8 min | 13,8 min | 4,7 min (−20 %) |

## Decisión del gate T4 (orquestador Claude, con la HITL delegada)

- **AC-7 (Claude Code): cumplido.** `status` es la primera acción. El despacho baja de la llamada 23 a la 14, y la salida previa a la mitad.
- **AC-6 (OpenCode): cumplido en parte, y se declara así.**
  - La skill se carga primero y `status` llega en la llamada 3, en vez de la 21. Bajan las llamadas y el tiempo.
  - No se cumple el orden estricto «`status` antes del state completo»: el modelo hace `cat` del state en la llamada 2, inmediatamente antes.
  - Lo que queda es una lectura de 53 mil caracteres que precede a la vista aun con el agente actualizado; el costo lo pone el tamaño del state (unos 490 KB, la mayor parte historia). Que sea un hábito del modelo, o que otro ajuste del prompt rinda poco, son hipótesis no demostradas (precisión del 2026-10-14).
  - **Deuda estructural:** compactar el state, por ejemplo archivando la historia cerrada, para que leerlo no sea caro. Queda como candidata para el plan.
- **El gate se aprueba con AC-6 parcial declarado.** El resultado de la feature (que la entrada pase por `status` en los dos runtimes y reduzca la exploración) está demostrado en Claude Code y logrado en su mayor parte en OpenCode. La brecha restante tiene costo medido, causa no demostrada y deuda con condición de cierre.

**RD nuevos:**
- **RD-a — agentes derivados viejos tras un despliegue.** Condición de cierre: que la primera sesión después de un despliegue use el orquestador nuevo. Por ejemplo, que el despliegue republique los derivados de los proyectos registrados, o que el orquestador no se derive al proyecto.
- **RD-b — compactación del state.** Condición de cierre: que leer el state completo cueste un orden de magnitud menos, sin perder la historia (archivada y referenciada).
