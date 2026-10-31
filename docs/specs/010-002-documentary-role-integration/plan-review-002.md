# Dictamen de plan-review (segunda pasada): 010-002-documentary-role-integration

**Recomendación: la versión 2 está lista para someterse a aprobación.** No encontré bloqueantes: B1 y B2 están cerrados y O1..O6 adoptados. Quedan cuatro hallazgos no bloqueantes. N1 conviene incorporarlo antes de aprobar, porque se corrige con una línea y evita un reencauce seguro en T2. Este dictamen no aprueba nada ni autoriza implementar; decide el dueño.

**Objeto revisado**
- `plan.md` v2: `6f3ebc481bbade9a4cee69f753737adbb33401a1d142f7134c75732f48258662`
- `spec.md` v2: `8a18d186ebc968e23442eef33f449e454c406ad1da7cfd63f43c1669ee91ac42`

**Intake:** ruta C válida.
- Los metadatos coinciden con `REQUEST.json` y `PACKET.md`, y los dos hashes coinciden con los del contrato.
- El contexto de ejecución es v2.
- `validate-request` y `validate-packet` dieron rc=0, y `render` es idéntico a `PACKET.md` (`cmp` rc=0).

## Hallazgos bloqueantes

Ninguno.

## Hallazgos no bloqueantes

### N1. Ya se conocen fixtures afectados fuera de la lista de T5
- **Severidad:** Consider
- **Verdict:** OPTIONAL
- **Bucket:** h
- **Ubicación:** `plan.md:188-191`, `:255-262`, `:476`, `:511-518`; `spec.md:279`; `tests/test_006_005_u1b_dispatch_entry.py:826-834`; `tests/test_006_005_u2_opencode_module.py:943`.
- **Fundamento:**
  - Ambos fixtures parten de requests generados por `prepare` y eliminan solo `agent`, conservando `execution_context`. Con la regla de D3 pasan a ser requests inválidos.
  - El comentario de `u1b` remite a ese mismo mecanismo de simulación de históricos.
  - T5 solo autoriza adaptar `u1c`.
  - `u1b` no figura en ninguna regresión de T4 ni de T6. `u2` sí está en T6, pero T5 no puede editarlo.
- **Consecuencia:** T2 debería detectarlo, y `plan.md:87` ordena detenerse y reautorizar el alcance, así que el proceso no se rompe. Sin embargo, el reencauce es seguro y evitable. Si la medición fallara, `u1b` solo aparecería en la suite de cierre de T9, cuando GREEN ya no puede tocar tests.
- **Condición de cierre:** añadir ambos archivos a T5 en prosa y `plan-tasks`, y `u1b` a las regresiones de T6 en las tres superficies. Esto no sustituye la medición de T2.

### N2. Registrar un despacho nuevo no está delimitado frente a la repetición y al cierre del write-ahead
- **Severidad:** Consider
- **Verdict:** OPTIONAL
- **Bucket:** m
- **Ubicación:** `spec.md:94,102`; PC-08 (`:207-213`); `plan.md:241`; `cdad_packet.py:4238-4254`; `cdad_delegate_opencode.py:3000-3032`.
- **Fundamento:**
  - El adaptador registra un write-ahead antes de lanzar y completa ese registro al terminar, por la misma entrada `--record-dispatch`.
  - Una repetición idéntica también pasa por esa vía.
  - Una implementación directa del chequeo dentro de `_record_dispatch` rechazaría la observación final si `stack` cambió mientras corría el trabajo.
- **Consecuencia:** un despacho ya lanzado podría quedar con su registro provisional, contra la intención de `spec.md:102`. La ventana es estrecha, porque exige un cambio de `stack` durante la ejecución.
- **Condición de cierre:** declarar que el contraste aplica a un intento nuevo, no a la repetición idempotente ni a la finalización de su write-ahead, y añadir esa transición a T5.

### N3. La discordancia de rol ya no impide un render válido, a diferencia de D-3
- **Severidad:** Consider
- **Verdict:** OPTIONAL
- **Bucket:** m
- **Ubicación:** `spec.md:98,100`; `discovery-decisions-2026-10-31.md`, D-3 («no producir un render válido», «en `prepare`/validación del request»).
- **Fundamento:**
  - La v2 limita el contraste a publicar y despachar, y ese es el alcance que declara este paquete para O1.
  - El argumento de O1 solo afecta a la parte temporal, es decir, a `stack`. La discordancia de rol no depende del tiempo.
  - Un `agent` de otro rol seguirá pasando `validate-request` y `render`, y solo se rechazará al registrar el despacho.
  - La sonda sobre los requests reales dio **274 con `agent` y prefijo de rol correcto, 0 discordantes**. Una comprobación estática de rol no afectaría a ningún request publicado.
- **Consecuencia:** es una diferencia literal con una decisión que no se reabre. El efecto real es limitado, porque el registro sigue cortando antes de despachar. Queda una diferencia sin registrar entre el texto de la decisión y el contrato.
- **Condición de cierre:** elegir una de dos opciones:
  - añadir a la validación compartida el contraste estático agente↔rol, sin mirar `stack`; o
  - registrar en las decisiones que D-3 queda precisada por O1.

### N4. El rechazo en la publicación no se puede provocar desde la interfaz pública
- **Severidad:** Consider
- **Verdict:** OPTIONAL
- **Bucket:** m
- **Ubicación:** PC-07 (`spec.md:206`); `plan.md:41,203`; `cdad_packet.py:6412-6425,6666`.
- **Fundamento:** `prepare` deriva `agent` del mismo `role` y `state` contra los que se contrastaría. No acepta un agente del llamador, así que la rama de rechazo es inalcanzable por CLI.
- **Consecuencia:** esa mitad de PC-07 será un control verde o exigirá simular una interfaz interna, lo que `plan.md:41` excluye. La garantía real es que `prepare` construye el agente coherente; la mitad del despacho sí se puede probar.
- **Condición de cierre:** que T2 clasifique esa mitad como garantía por construcción, verificando el agente publicado, y que EV-03 lo declare así.

### FYI
- Las cláusulas Odoo siguen sin llegar a la instalación global mientras persista la deriva. `spec.md:281` y T9 lo declaran.
- `bootstrap.md:60` («`stack` absent → generic») es correcta y no necesita cambios.

## Verificación por hallazgo y objetivo

| # | Punto | Resultado | Evidencia |
|---|---|---|---|
| 1 | **B1** | Cerrado | `spec.md:51-63` define la frontera y el régimen de la documentación del módulo. `:67-74` fija la base por rol, y el verificador documental queda en `:61`. Reviewer y orquestador deciden por diff real, y el architect conserva conocimiento, con inventario solo antes de modificar un addon (`:78`). PC-04/05 cubren los seis roles en los tres casos. |
| 2 | **B2** | Cerrado | `SKILL.md` figura en las citas (`spec.md:324`), en T4 (`plan.md:128,433`) y en PC-09. `plan.md:115,411` cubre «otro valor» en ambas superficies, y las dos frases existen en `SKILL.md:137` y `sub-agent-strategies.md:157`. |
| 3 | **O1** | Adoptado | `spec.md:91-102` y `plan.md:208-209,241-242`. Matiz en N2 y N3. |
| 4 | **O2** | Adoptado | `spec.md:104-112`, PC-08 y `plan.md:205-206`. El censo actual da 45 requests con contexto y agente. |
| 5 | **O3** | Adoptado | `spec.md:123-128`, PC-08 y `plan.md:210`. El rechazo mecánico existe en `cdad_delegate_opencode.py:_check_derived_agent_published`, y el fallo del write-ahead bloquea el lanzamiento. |
| 6 | **O4** | Adoptado | `spec.md:237-239` y `plan.md:43,116,182,253`. |
| 7 | **O5** | Adoptado | `spec.md:13`, PC-12 y EV-04. |
| 8 | **O6** | Adoptado | La prosa de T4 y T6, la tabla de regresiones y `plan-tasks` coinciden entre sí. La omisión de N1 es común a las tres. |
| 9 | AUDIT de T2 | Cumple | `plan.md:73-91,391-392`. Mide fixtures discordantes y resuelve las adaptaciones antes de RED, y T6 no edita tests (`:264`). |
| 10 | Inventario de cuatro referencias | Cumple | `plan.md:133-150`: son candidatas, con `write_scope` confirmado antes de editar, y coinciden con `plan-tasks`. |
| 11 | Contradicciones | Sin bloqueantes | D-1, D-2, D-4 y D-5 se respetan. Los criterios del epic quedan trazados por O5. La única diferencia con las decisiones es N3. |

## Abstentions
- **Medición completa de fixtures:** hice un grep de los patrones `pop("agent")` y reasignación de `agent`, no una ejecución simulada. Pueden existir otros fixtures afectados entre los 41 archivos de test que usan `record-dispatch`; esa medición corresponde a T2.
- **Validador de `plan-tasks`:** no lo ejecuté contra este plan. Revisé el bloque a mano en dependencias, archivos y coherencia con la prosa.
- **Tamaño de agentes generados:** el test del techo estático pasa hoy (2 passed), y ese techo gobierna el paquete. No busqué un límite propio de los agentes generados ni medí cuánto crecerán con T4.
- **Suficiencia real de la matriz Odoo:** depende de la redacción de T4 y se juzga en T8.

## Evidencia
- **Archivos modificados:** ninguno.
- **Commit:** ninguno. `HEAD` es `3bea7a8d356e35ccb93d22d010632f1d7e7406bf`.
- **Comandos:**
  - `python3 -B scripts/cdad_packet.py validate-request|validate-packet|render --request <REQUEST.json>`, con `--packet <PACKET.md>` en `validate-packet`.
  - `cmp` del render contra `PACKET.md`, y `sha256sum` de `plan.md` y `spec.md`.
  - `python3 -B -m pytest -q tests/test_static_block_ceiling.py`.
  - `python3 -I` en memoria para el censo de `.cdad/packets/*/REQUEST.json`.
  - `grep`, `sed` y `wc` sobre las rutas citadas.
- **Salidas:**
  - `vr=0`, `vp=0`, `rr=0`, `cmp=0`.
  - Test del techo: `2 passed`.
  - Censo: `Counter({'noagent': 592, 'roleok': 274, 'ctx_gen': 45})`.
  - `stack` vigente en el estado: `None`.
- **Suite completa:** no ejecutada; este paquete no la pide.
