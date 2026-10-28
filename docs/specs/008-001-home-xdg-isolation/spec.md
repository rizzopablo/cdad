# 008-001 — Aislamiento HOME/XDG por test

**Estado:** aprobada por el orquestador (HITL delegada) con AJ1–AJ5; PC-7 y PC-8 agregadas el 2026-10-27 a partir del gate (borde de cota).  
**Epic:** `epic-008-suite-coherence`.  
**Base:** `docs/specs/008-001-home-xdg-isolation/discovery.md` y contrato aprobado de la unidad.

## 1. Objetivo

Cada test ejecutado por pytest dispone de HOME, directorios XDG y temporales propios. Sus subprocess heredan ese entorno, salvo overrides explícitos del test. La ejecución no depende incidentalmente de la configuración personal del operador.

La exposición actual está verificada; que explique todos los fallos intermitentes sigue siendo una hipótesis. Esta unidad no promete corregir causas ajenas al aislamiento.

## 2. Evidencia y decisiones

- `tests/conftest.py:11-16` solo configura `sys.path`: no hay aislamiento transversal.
- `skills/cdad-cycle/scripts/cdad_packet.py:140` captura `Path.home()` durante importación. `_derived_source_dir`, en `:4071-4084`, consume ese valor después de comprobar override explícito y activación.
- `tests/test_005_002_t4_acceptance.py:993-1014,1049-1066` exige variables explícitas para las aceptaciones contra store real.

### Decisiones

1. **Fixture autouse de alcance function**, compartida por toda la suite, en lugar de parches por familia: la regla pertenece a cada test, no a su procedencia histórica.
2. **Resolución lazy del origen global de agentes**, en lugar de recargar módulos o parchear constantes desde tests: el producto debe consultar el entorno vigente cuando resuelve la ruta.
3. **Overrides locales preservados**: un fixture puede construir un HOME/XDG sintético distinto del predeterminado. No se reemplazan archivos, SQLite ni servidores de fixture por mocks.
4. **Canario basado en entorno y escrituras**, no en una promesa de observación universal de lecturas.
5. **Tres corridas completas en cierre**, como excepción explícita del objetivo específico frente a la regla común de una corrida. Deben autorizarse así en el paquete del closer; este draft no ejecuta ninguna.

## 3. Alcance

### Dentro

- Aislamiento transversal en `tests/conftest.py`.
- Adaptaciones mínimas de fixtures afectados, preservando sus aserciones.
- Corrección lazy de la captura identificada en `cdad_packet.py`.
- Revisión acotada de otras capturas HOME/XDG durante importación en los scripts utilizados por la suite; corrección equivalente cuando se demuestre el mismo defecto.
- Canarios y regresiones, extendiendo módulos existentes antes de crear otros.
- Evidencia de teardown y del gate de cierre.

### Fuera

Red, puertos, servicios externos vivos, presión temporal, paralelismo, reorganización por capacidad —008-002— y cambios de orden para ocultar contaminación. No se modifican contratos funcionales, formato de `status`, recibos ni almacenamiento de continuidad.

## 4. Contrato funcional

### Preparación

Antes de ejecutar fixtures funcionales y el cuerpo de cada test:

- Crear una raíz temporal exclusiva y directorios existentes para:
  - `HOME`;
  - `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_STATE_HOME`;
  - `XDG_CACHE_HOME`, `XDG_RUNTIME_DIR`;
  - `TMPDIR`, `TMP`, `TEMP`.
- Todas esas rutas son absolutas y descendientes de la raíz del test. Las tres variables temporales pueden compartir directorio.
- `XDG_RUNTIME_DIR` es privado al usuario ejecutor.
- Invalidar la caché `tempfile.tempdir` para que la resolución temporal use el entorno del test.
- Neutralizar overrides CDAD heredados que desvíen configuración, instalación o agentes hacia ubicaciones externas, mediante una lista explícita justificada por sus consumidores reales. No se permite borrar indiscriminadamente `CDAD_*`.
- No fabricar variables de habilitación de aceptaciones reales.

La asignación de la raíz no puede depender de una caché temporal contaminada por el test anterior.

### Ejecución

Los subprocess sin entorno explícito heredan las rutas aisladas. Los helpers que construyen `env` deben preservar ese aislamiento, salvo overrides sintéticos deliberados o entradas reales expresamente habilitadas.

La fixture autouse no cubre código ejecutado durante colección. Las capturas dependientes de HOME/XDG identificadas durante importación deben eliminarse o resolverse en el momento de uso; no se oculta este límite mediante recargas de módulos.

### Resolución de agentes

Se mantiene exactamente esta precedencia:

1. `CDAD_OPENCODE_AGENTS_DIR` no vacío;
2. instalación registrada en `.cdad/activation.json`;
3. `HOME` vigente seguido de `.config/opencode/agents`.

El fallback global no cambia a `XDG_CONFIG_HOME` como efecto incidental de esta unidad.

### Finalización

Después de finalizar los procesos, servidores y demás recursos creados por el test:

- Restaurar presencia y valor anteriores de las variables gestionadas.
- Restaurar el valor anterior de `tempfile.tempdir`, incluido `None`.
- Retirar la raíz descartable.

La secuencia debe mantenerse también cuando el test falla. El teardown no termina procesos ajenos ni utiliza un barrido global como sustituto de la propiedad de recursos.

## 5. Postcondiciones verificables

### PC-1 — Raíces exclusivas y herencia

Dos tests ejecutados en una misma invocación observan raíces distintas. Cada uno y su subprocess verifican que las nueve variables gestionadas apuntan a sus descendientes y que un temporal creado mediante `tempfile` queda dentro.

**Variantes:** caché temporal previamente poblada; override sintético local de HOME/XDG; subprocess con entorno copiado por un helper existente.

**Oráculo:** rutas reportadas por CLI, existencia de archivos y bytes de marcadores exclusivos; ningún test encuentra el marcador del otro.

### PC-2 — Resolución lazy y precedencias conservadas

Un módulo importado antes de cambiar HOME resuelve después el origen global desde el HOME vigente. Cambiar nuevamente HOME cambia ese fallback, sin reimportar.

**Variantes:** override explícito vence a activación y HOME; activación vence a HOME; sin ambos se usa el fallback; origen ausente conserva el comportamiento contractual existente.

**Oráculo:** ruta resuelta y consumo de agentes sintéticos reales diferenciados por sus bytes. No basta con comprobar que existe una función nueva.

### PC-3 — Configuración y stores sin habilitación accidental

Los recorridos existentes de configuración, registro de servicio y SQLite consumen los recursos sintéticos elegidos por sus fixtures, no señuelos externos.

Sin las variables explícitas requeridas, las aceptaciones reales conservan su resultado **skip** y diagnóstico. La fixture no convierte un skip en pass ni inventa IDs o stores.

**Variantes:** entorno padre con overrides CDAD desviantes; configuración ausente; override local legítimo; variables reales ausentes.

**Oráculo:** resultados funcionales existentes, bytes o registros sintéticos inequívocos y resumen de omisiones. No se exige acceder a un store real para acreditar esta PC.

### PC-4 — Escrituras confinadas y canario sensible

Una corrida controlada escribe marcadores desde un test y su subprocess: aparecen exclusivamente bajo las raíces aisladas.

Se compara el inventario y `mtime_ns` del HOME real antes y después, incluyendo creación, eliminación y cambios de entradas, sin seguir enlaces simbólicos fuera de él. La prueba de sensibilidad usa un HOME externo sintético controlado: una escritura deliberada fuera de la raíz aislada debe ser detectada.

**Oráculo:** marcadores con bytes conocidos y diferencia de inventarios vacía en la corrida válida; diferencia detectada en el control negativo.

El inventario excluye únicamente los artefactos de evidencia identificados previamente si deben residir bajo ese HOME. No se excluyen ubicaciones para ocultar escrituras del producto. Fallos de acceso o cambios concurrentes vuelven la evidencia inconclusa: se investigan, no se presentan como ausencia de contaminación.

Esta comprobación **no demuestra ausencia universal de lecturas**, ni detecta necesariamente escrituras transitorias revertidas entre snapshots.

### PC-5 — Restauración y cierre de recursos

Al terminar el test, incluso con fallo deliberado, se restauran entorno y `tempfile.tempdir`; los procesos y servidores creados por el fixture han terminado antes de retirar su raíz.

**Variantes:** variable originalmente ausente o presente; caché temporal originalmente `None` o fijada; ejecución satisfactoria y ejecución fallida.

**Oráculo:** comparación exacta antes/después desde un controlador de corrida anidada, códigos de salida y comprobación de terminación de los recursos identificados por el fixture. No se declara terminación basándose solo en que desapareció su directorio.

### PC-6 — Gate completo reproducible

El closer registra tres ejecuciones completas consecutivas de:

```bash
python3 -m pytest tests -q
```

Cada una termina con `rc=0`, sin failures ni errors y sin contaminación detectada. Se conservan las omisiones legítimas, explicadas en la evidencia.

Por corrida se registra: comando, revisión y estado del árbol, resultado, resumen de pytest y resultado del canario. No se modifica el orden, selección ni aserciones entre esas tres corridas.

Un fallo interrumpe la secuencia. Se investiga su causa; después de una corrección, la secuencia de tres comienza de nuevo. Si la causa queda fuera del alcance, la unidad queda bloqueada, sin afirmar suite estable.

## 6. Invariantes

- No se eliminan aserciones, cobertura contractual ni tests para obtener verde.
- No se añaden skips, xfails o reintentos para ocultar fallos.
- Las entradas reales siguen siendo explícitas y opt-in.
- Los overrides sintéticos locales conservan efecto.
- No cambia la precedencia de agentes ni la semántica funcional existente.
- No se sustituyen recorridos reales sintéticos por mocks.
- No se incorporan rutas, identidades, credenciales ni datos del consumidor a código, fixtures o evidencia publicada.
- HOME/XDG por entorno no constituye una sandbox: rutas absolutas y entornos explícitos pueden escapar.

## 7. Aceptación y evidencia

La unidad es aceptable únicamente con:

1. Mapeo PC-1…PC-6 a tests o evidencia de cierre.
2. Regresiones focales verdes antes del gate completo.
3. Tres corridas consecutivas acreditadas según PC-6.
4. Inventarios sin cambios atribuibles a los tests y controles negativos sensibles.
5. Cambios de producto limitados a las capturas dependientes del entorno demostradas.
6. Revisión que confirme preservación de aserciones, precedencias y omisiones.

**Pendientes de verificación en implementación:** lista exacta de overrides heredados a neutralizar; posibles capturas adicionales no cubiertas por la búsqueda inicial; orden efectivo de teardown de los fixtures que mantienen procesos. Son obligaciones de investigación acotada, no autorización para ampliar el alcance.

## 8. Evidencia del draft

- Archivos modificados por este rol: ninguno.
- Tests ejecutados: ninguno.
- Commit creado: ninguno.
- HEAD observado: `e12564f`.
- Cambio preexistente observado: `docs/.cdad-state.json`, 3 inserciones y 3 eliminaciones.

Comandos ejecutados desde la raíz del repositorio:

```bash
cat .cdad/packets/008-001-home-xdg-isolation-architect-draft-001/PACKET.md
cat .cdad/packets/008-001-home-xdg-isolation-architect-draft-001/UNIT-CONTRACT.md
cat docs/specs/008-001-home-xdg-isolation/discovery.md
cat docs/epics/epic-008-suite-coherence/plan.md
cat skills/cdad-cycle/references/design-principles.md
git status --short
sha256sum .cdad/packets/008-001-home-xdg-isolation-architect-draft-001/UNIT-CONTRACT.md docs/cdad-policy.json
nl -ba tests/conftest.py
sed -n '125,146p;4060,4095p' skills/cdad-cycle/scripts/cdad_packet.py
sed -n '975,1075p' tests/test_005_002_t4_acceptance.py
rg -n 'Path.home\(|expanduser\(|tempfile.tempdir|CDAD_.*(DIR|ROOT)|pytest' tests/conftest.py pyproject.toml pytest.ini Makefile skills/cdad-cycle/scripts/cdad_packet.py
rg -n '^[A-Z_]+.*(Path.home\(|expanduser\(|getenv\(.?(HOME|XDG)|environ.*(HOME|XDG))' skills/cdad-cycle/scripts --glob '*.py'
git rev-parse --short HEAD
git diff --stat
```

Resultados relevantes: hashes del contrato y política coincidentes con el paquete; única captura encontrada por la búsqueda acotada: `cdad_packet.py:140`. `pyproject.toml` y `pytest.ini` no existen; esa búsqueda emitió diagnóstico, por lo que no constituye una auditoría exhaustiva de capturas.

## Ajustes del orquestador (review 2026-10-26)

**AJ1 — El aislamiento por defecto no impide las pruebas de fallback (bloqueante resuelto).** Las nueve rutas de PC-1 aplican al **entorno predeterminado**. Un test puede **quitar o vaciar** deliberadamente una variable gestionada para ejercer una precedencia (p. ej. `XDG_CONFIG_HOME` ausente → `CDAD_INSTALL_ROOT` → HOME), siempre con recursos sintéticos propios y sin cambiar la precedencia del producto. PC-1 se verifica en el caso por defecto; las variantes se verifican por bytes de configuración diferenciada en cada nivel.

**AJ2 — Overrides heredados: tabla contractual (bloqueante resuelto).**

| Variable | Consumidor | Tratamiento de un valor heredado | Override local |
|---|---|---|---|
| `HOME`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_STATE_HOME`, `XDG_CACHE_HOME`, `XDG_RUNTIME_DIR`, `TMPDIR`, `TMP`, `TEMP` | producto y subprocess | se **fijan** a la raíz del test | permitido; el test puede quitarlos/vaciarlos para ejercer un fallback |
| `CDAD_INSTALL_ROOT` | `cdad_config_dir` (fallback de configuración) | se **retira** del entorno heredado | permitido con raíz sintética |
| `CDAD_OPENCODE_AGENTS_DIR` | `_derived_source_dir` (origen de agentes) | se **retira** del entorno heredado | permitido con agentes sintéticos |
| `CDAD_CONTEXT_METER_STORE` | almacén del medidor de contexto | se **retira** del entorno heredado | permitido con ruta sintética |
| `CDAD_DELEGATE_DESTINATION`, `CDAD_STATIC_BLOCK_LIMIT`, `CDAD_TEST_*` | destino, límite y controles de test | **se conservan** (no son rutas de usuario) | permitido |

No se fabrican ni se retiran variables de habilitación de aceptaciones reales. PC-3 prueba cada fila con un señuelo sintético.

**AJ3 — Evidencia del gate (menor).** Cada corrida de PC-6 conserva log completo en `.cdad/local/008-001/run-{1,2,3}.log`, el `rc` **de pytest**, el commit y estado del árbol, el resumen y el resultado del canario. Los intentos interrumpidos se guardan como `attempt-<n>.log` y se distinguen de la secuencia válida; la secuencia de tres se reinicia tras cualquier corrección.

**AJ4 / PC-7 — El wrapper no preempta la cota del adaptador (agregado 2026-10-27).** La corrida 1 del gate falló en `test_006_001_reviewfix.py` B1: `cdad_delegate.py` espera al adaptador el **mismo** `timeout_seconds` que el adaptador administra, así que bajo carga lo mata antes de que emita su sobre y el usuario recibe `did not answer within` con `session: null` — exactamente lo que PD-11/PD-8 prohíben. La cota es del adaptador; el wrapper es una red de seguridad y debe esperar un **margen declarado** más.

- **PC-7:** con un adaptador que responde un sobre `timeout` válido dentro de `cota + margen` pero después de la cota, el wrapper devuelve **ese sobre** (sesión conservada), no su diagnóstico genérico. Un adaptador que no responde dentro de `cota + margen` sigue produciendo el `timeout` del wrapper. El margen es una constante declarada del producto y el diagnóstico del wrapper nombra el límite efectivo (`cota + margen`).
- Test determinista con adaptador falso (sin depender de carga): responde a `cota + ε` → sobre del adaptador; no responde → timeout del wrapper.

**AJ5 / PC-8 — El adaptador no despacha sin presupuesto útil (agregado 2026-10-27).** El gate expuso que el adaptador OpenCode calcula la espera como `cota - preflight_consumido`; bajo carga el preflight consume la cota y la espera queda en `0.0s`, devolviendo un timeout falso aunque el cliente respondiera. Diseño (dictamen del architect, 2026-10-27): la cota es **total** del adaptador; el preflight tiene un **deadline agregado** y debe reservar presupuesto positivo para el cliente y la observación durable **antes** de ejecutarlo; si la preparación agota el presupuesto, **no se lanza el cliente**.

- **PC-8a:** con una preparación que cruza su deadline (p.ej. `/api/info` demora más que el presupuesto preparatorio), el adaptador **no ejecuta** el cliente, no fabrica sesión/recibo, y el diagnóstico identifica el **agotamiento preparatorio** (no un `bounded wait (0.0 seconds)`).
- **PC-8b:** con preparación admisible, queda presupuesto positivo reservado para el cliente y la observación durable, sin ampliar la cota total.
- Test determinista con binario OpenCode falso y servidor loopback controlado: registrar `--version`/`run`; variante que cruza el deadline (no `run`) y variante dentro del presupuesto (fila durable `idle` → resultado).
