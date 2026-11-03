# Review 013-002-live-inventory: no aceptable todavía

**Objeto:** `git diff 54a667b9~1..HEAD`, con HEAD en `797f2055`. No modifiqué nada del repo; las mutaciones y `make agents` corrieron en una copia temporal de `git archive`.
**Intake por ruta C:** válido. `cdad_packet.py render` reproduce `PACKET.md` byte a byte, la identificación coincide, el contexto es v2 y el sha de la spec es correcto.

Hay 4 hallazgos bloqueantes. La deuda queda en las opcionales.

## Bloqueantes

### B1 — Required: falta el procedimiento de sustitución de PC-6
- **Verdict:** BLOCKING | **Bucket:** h
- **Ubicación:** `docs/suite-maintenance.md:67`
- **Evidencia:** el documento solo dice «delta del mapa de PC-6», sin definirlo. `grep -i "read_scope|revisión anterior|destino"` en `docs/suite-maintenance.md`, `handoff-prompts.md` y `orchestrator.md` no encuentra el procedimiento:
  - Faltan los pasos AUDIT → delta → POST-AUDIT → materialización → contraste.
  - Falta la declaración expresa del mapa en `read_scope`, junto con la revisión anterior.
  - Falta la cadena de re-sustitución y la identidad por contrato, id y variante.
  - Falta el tratamiento de varios destinos sin usar una lista en `target_nodeid`.
- **Consecuencia:** 013-003 no recibe el procedimiento que PC-6 le promete. Puede perder genealogía o despachar al test-writer sin lectura del mapa.
- **Cierre:** añadir ese procedimiento bajo `## Inventario vivo`.

### B2 — Required: la norma distribuida fija un comando de este proyecto
- **Verdict:** BLOCKING | **Bucket:** h
- **Ubicación:** `sources/roles/orchestrator.md:231-239` (y sus agentes generados), `handoff-prompts.md:717-727`, `re-entry.md:426-437`
- **Evidencia:** los tres textos nombran `python3 scripts/cdad-suite.py validate`, aunque la spec §5 reserva rutas y comandos a la documentación del proyecto. PC-7 dice además «No presume rutas ni comandos». `cdad-suite.py` no está entre los scripts de `skills/cdad-cycle/scripts`.
- **Consecuencia:** en otro proyecto, el orquestador puede exigir rc=0 de un comando inexistente, o de uno distinto al declarado, justo en los gates que bloquean Review y cierre.
- **Cierre:** sustituirlo por «el comando de integridad declarado» y regenerar con `make agents`.

### B3 — Required: PC-3 sin registro y contadores auxiliares sin identificar
- **Verdict:** BLOCKING | **Bucket:** m
- **Evidencia:**
  - 30 módulos preexistentes tienen `static_test_nodeids` distinto de la colección real. Por ejemplo, `test_007_004_termination_not_success.py` declara 18 y tiene 69, y el módulo B1 declara 14 y tiene 18.
  - Ese campo no se actualizó ni se identifica como histórico: `grep -i "static_test|contador"` en `suite-maintenance.md` no devuelve nada.
  - La cabecera del inventario sigue diciendo `draft T1 … sin pc-map`.
  - No encontré el registro de PC-3 (revisión, comando de colección, cantidades, diferencias y deuda del helper) en el diff del estado, ni en `docs/specs/013-002-live-inventory/`, ni con búsqueda de `1949`/`evidence` en los paquetes del implementer.
- **Consecuencia:** el dato auxiliar puede leerse como colección efectiva, justo lo que PC-3 prohíbe, y la entrega no es comparable.
- **Cierre:** declarar el carácter estático del campo y registrar PC-3 con los valores medidos: 1949 nodeids, 232 entradas en el inventario, 31 registros en el mapa, 0 pendientes estructurales y la deuda del helper aparte.

### B4 — Required: módulos mixtos clasificados con una sola capacidad
- **Verdict:** BLOCKING | **Bucket:** m
- **Ubicación:** entradas de `tests/test_008_003_lifecycle_decisions.py` y `tests/test_010_002_documentary_role_integration.py` en `suite-inventory.json`
- **Evidencia:**
  - `test_008_003` tiene `scope: module` en `continuity`, pero incluye `test_pc02_suspension_follows_the_accredited_owner` y `test_pc02_direct_plan_write_respects_suspension`. La capacidad `suspension` existe.
  - `test_010_002` tiene `scope: module` en `packets-authority-identity`, pero incluye `test_distributed_artifacts_carry_the_matrix`, que corresponde a generación y distribución.
- **Consecuencia:** `list --capability suspension` omite esos tests. Según PC-2 y §7, la correspondencia final de las asignaciones bloquea su aceptación.
- **Cierre:** añadir asignaciones por nodeids, sin particionar, o justificar en `rationale` por qué el módulo pertenece íntegramente a una capacidad.

## Opcionales y deuda

- **O1 — Required menor (OPTIONAL | m): transmisión de PC-7 incompleta.** `orchestrator.md` y `handoff-prompts.md` omiten el delta de POST-AUDIT y el del mapa. Además, ninguno de los tres textos dice que rc=0 se mide sobre la revisión con los deltas materializados. No bloquea porque el orquestador lee `## Inventario vivo`, que sí lo contiene.
- **O2 — Nit (OPTIONAL | m): GREEN queda fuera en `re-entry.md`.** Dice «GREEN con cambios de tests», pero GREEN no cambia tests. La comprobación de GREEN no se aplicaría, en contra de la tabla de PC-7.
- **O3 — Consider (OPTIONAL | m): dos mutaciones sobreviven a los tests.**
  - Si se invierte el gate a «bloquea en RED», los 7 tests siguen en verde. El test D1 no verifica la semántica de los momentos en los handoffs. Sin él, un cambio así no se detecta y el usuario podría bloquear RED por datos que su autor no puede editar. Eso contradice «verificación focal… pasos no bloqueantes».
  - Si se eliminan los 2 `VERIFY` históricos, también sigue en verde, porque las 2 entradas nuevas satisfacen la aserción `legacy_verify`.
  - El test A1 tampoco ejecuta `validate`, pese a su nombre, y comprueba los nodeids solo por archivo. El `validate` del gate cubre esa parte.
  - Corresponde a test-writer y queda en deferred-hardening salvo que se pida promoverlo.
- **O4 — Nit (OPTIONAL | l):** el mapa asigna `test_b1_collision_leaves_…` solo a PD-6, pero su docstring también cubre INV-3 y PD-4.

## Verificación con evidencia propia

| Punto | Resultado |
|---|---|
| (a) Contratos de las altas | Los 21 existen, incluido `spec.yaml` corregido. El único no recuperable es el helper `VERIFY`, ya declarado como deuda. |
| (a) SELF | Correctamente detallado por 7 nodeids; `list --capability suite-isolation` devuelve los 7. |
| (b) Entradas B1 | Las 2 entradas tienen `task`, destino actual y `status: VERIFY` justificado. El diff del mapa es solo aditivo: los 29 registros anteriores y `pilot_*` quedan intactos. Las variantes coinciden con los tests. |
| (c) `suite-maintenance.md` | Separación clasificación/acreditación, tabla de momentos, límites de PC-8, advertencia sobre `surface` y deuda del helper presentes. Falta lo señalado en B1 y B3. |
| (d) Regla PC-7 | Condicional, sin gate ni fase nuevos y sin exigir suite completa. No detecté contradicción con 013-001/R2, aunque el contraste fue por `grep` y lectura del diff. |
| (e) `make agents` | rc=0 en copia `git archive`, 0 archivos con deriva. |
| (f) Tests | Los 7 pasan y ninguno es vacío: cada uno cae con al menos una mutación. Fallaron 7 de 9 mutaciones. |
| `validate` | rc=0, 1949 nodeids, 232 módulos, 31 registros, 3 `placeholder_targets` preexistentes. |

## Evidencia exigida

- **Commit revisado:** `797f2055`.
- **Archivos modificados por esta revisión:** ninguno.
- **Archivos del diff:** los 10 del `--stat`: inventario, mapa, `suite-maintenance.md`, tres instrucciones, dos agentes, el test y el estado.
- **Comandos ejecutados:**
  - `python3 scripts/cdad_packet.py render --project-root . --request … --execution-context …` seguido de `cmp`, resultado SAME
  - `python3 scripts/cdad-suite.py validate`, rc=0
  - `python3 -m pytest tests/test_013_002_live_inventory.py -q`, 7 passed
  - `python3 -m pytest tests --collect-only -q`, 1949 collected
  - `make agents` en copia temporal, rc=0, sin deriva
  - `python3 scripts/cdad-suite.py surface --base 54a667b9~1 --collect-only`, solo colección
  - `python3 scripts/cdad-suite.py list --capability suite-isolation`, incluye los 7 nodeids de SELF
- **Suite completa no realizada:** solo se corrió la colección y los 7 focales.

## Abstenciones

- **Lectura de las 21 asignaciones:** las contrasté con ruta, recuento real y nombres de los tests. Solo examiné los nombres de tests en 5 módulos y ninguno a fondo. No acredito la correspondencia de los otros 16 más allá de eso.
- **`tests/test_008_002_suite_selection.py`:** no lo ejecuté, así que no verifico orden y deduplicación de `list` más allá del caso SELF.
- **Tabla de decisiones vigentes frente a `docs/adr/`:** no hice ese contraste.
- **`surface --base HEAD` en el ejemplo de la documentación:** no lo verifiqué sobre el repo real. Sí corrí la variante con `HEAD~1`, que dio selección vacía, y la de `54a667b9~1`.

## Priorización del delegado del dueño (2026-11-02)

B1-B4 BLOQUEANTES (se corrigen). O1 y O2 se corrigen junto (triviales). O3 (mutaciones que sobreviven) y O4 a deuda declarada.


## Cierre de B1-B4 (verificación del orquestador, 2026-11-02)

Tras `dd5196df`: `validate` rc=0 (1949/232/31); el comando literal ya no figura en la norma distribuida (0 apariciones en los tres textos); procedimiento PC-6 y registro PC-3 en `docs/suite-maintenance.md`; mixtos de 008_003 y 010_002 asignados por nodeids; focales verdes. **No hubo segunda revisión independiente**: verificación del orquestador sobre los criterios de cierre del reviewer, declarada.

Deuda declarada: O3 (los tests no detectan la inversión del gate a «bloquea en RED» ni la eliminación de los 2 VERIFY históricos; A1 no ejecuta `validate`), O4 (INV-3/PD-4 de un registro B1), correspondencia semántica de 16 de las 21 asignaciones no examinada a fondo, suite completa no realizada, despliegue pendiente (reserva del dueño).
