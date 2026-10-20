## Reporte del rol — test-writer (substage RED, TESTFIX)

### Qué estaba roto

El lock PD-12 de 005-006 localizaba las dos regiones de enforcement **por número de línea** (`LOCK_REGION_1 = (480, 640)`, `LOCK_REGION_2 = (1400, 1580)`). Los cambios de 006-005 desplazaron el segundo sitio, que cayó fuera de la ventana → `AssertionError` aunque el enforcement **no había cambiado**.

### Evidencia: el segundo sitio SÍ existe como región separada

```
$ grep -n "epic_features" skills/cdad-cycle/scripts/cdad_packet.py
598:    features = state.get("epic_features")
600:        raise PolicyError("epic_features must be a list")
603:        raise PolicyError("execution feature must occur exactly once in epic_features")
1696:    features = state.get("epic_features")
1698:        raise PolicyError("epic_features record missing: state.epic_features must be a list")
1704:            f"epic_features entry"
1709:        f"active feature {feature_id!r} is closed: epic_features status {status!r} "
```

Los dos enforcement viven hoy en **`validate_state`** (def línea 570; enforcement 598-605) y **`_active_feature_entry`** (def línea 1695; enforcement 1696-1711). Verificado contra la revisión previa a 006-005 (`81ee8d3`), donde los **mismos símbolos** alojaban el enforcement (574-579 y 1551-1564): el ancla por símbolo es la de la spec, el número de línea sólo era del HEAD medido.

### Qué reformulé (sin debilitar)

Las regiones se localizan por **símbolo** (la función que las contiene), y en cada sitio se exige lo mismo que antes:
(a) la entrada se **exige** (raise vivo que nombra `epic_features`), (b) ocurre **exactamente una vez**, (c) la entrada **no está cerrada**. Cada sitio se evalúa por separado → el lock sigue siendo de las **dos** regiones, no de un punto.

**No se debilitó el lock** — prueba por mutación sobre copias (el archivo real nunca se tocó): 10/10 mutaciones detectadas (eliminación total/parcial de cada enforcement, borrado de la cardinalidad, borrado de la exigencia de "no cerrada", enforcement comentado = raise muerto, enforcement mudado de función, cardinalidad movida de un sitio al otro); control: pasa. Y **aguanta el desplazamiento** (+37/+250/+900 líneas, función nueva insertada): 5/5 sigue pasando — el modo de falla que se está arreglando.

### Archivos modificados

- `tests/test_005_006_t3_epic_features.py` (único archivo; el `docs/.cdad-state.json` modificado y los untracked de `docs/planning/` y `findings/` **no son míos**, no los toqué)

### Comandos y salidas

```
$ python3 -m pytest tests/test_005_006_t3_epic_features.py -v
test_pd12_epic_planning_assigns_epic_features_sync_owner        PASSED
test_pd12_project_start_names_drift_and_routes_sync_to_cdad_epic PASSED
test_pd12_enforcement_lock_cdad_packet_epic_features              PASSED
test_inv3_sole_state_writer_remains_orchestrator_in_sync_section PASSED
4 passed in 0.08s
```
```
$ python3 -m pytest tests/test_005_006_t{1,2,3,4,5,6}_*.py
36 passed in 1.77s

$ python3 -m pytest tests/test_006_005_u1b_dispatch_entry.py      # focal de la ficha
17 passed in 18.62s

$ python3 -m pytest <las 15 regresiones declaradas de la ficha>
118 passed, 2 skipped in 241.31s
```

### Commit

```
b2395a2 test: 005-006 lock PD-12 anclado por simbolo, no por linea
 tests/test_005_006_t3_epic_features.py | 189 +++++++++++++++-----
 1 file changed, 163 insertions(+), 26 deletions(-)
```
(sin `--no-verify`, sin stash, sin push)

### Declaración de alcance

- **Implementación leída**: sí, y de forma acotada — `grep` del símbolo `epic_features` en `skills/cdad-cycle/scripts/cdad_packet.py` más el contexto mínimo de los dos cuerpos, **explícitamente autorizado por la tarea** (el lock es un oráculo sobre el código por diseño de 005-006). No la edité. El grep de la revisión vieja (`git show 81ee8d3:… | grep -n "^def "`) se usó sólo para confirmar los nombres de función.
- No se corrió la suite completa (política del paquete: la corre quien cierra, una vez, al cierre).
- No leí `tests/.sensitive-patterns.local`.