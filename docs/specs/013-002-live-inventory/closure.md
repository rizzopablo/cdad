# Closure — 013-002-live-inventory

**Epic:** `epic-013-test-criterion` — orden 2/4. **Cerrada:** 2026-11-02.
**Contrato:** `docs/specs/013-002-live-inventory/spec.md`, sha256
`31a6ddbdd1eef65b358b51356c0dc100c92d1001a429d095a3fdc2258c1727e1`, aprobado por Pablo
(HITL delegada, `docs/epics/epic-013-test-criterion/execution.md`) el 2026-11-02.
**Estado:** cerrada en el repositorio; **no publicada ni desplegada**.

## 1. Resultado

El inventario de la suite es completo sobre la colección efectiva, distingue clasificación de
acreditación, entrega la semilla mapeada del lote piloto con su procedimiento de sustitución y
declara en un documento de proyecto el comando de integridad y los momentos en que se exige.
Producto: `54a667b9..dd5196df` (10 archivos, +1042/−14), RED `54a667b9`, review-fix `dd5196df`,
cierre de B1-B4 registrado en `review.md` (`645f2bd2`).

## 2. Evidencia

- Estructural: `python3 scripts/cdad-suite.py validate` → **rc=0**, `status: ok`, **1949
  nodeids, 232 módulos inventariados, 31 registros de mapa**, 0 pendientes estructurales
  (3 `placeholder_targets` preexistentes). Punto de partida: **rc=1 con 19 módulos y 163
  nodeids** sin asignar, colección 1942.
- Colección: `python3 -m pytest tests --collect-only -q` → **1949 tests collected**.
- Focal: `python3 -m pytest tests/test_013_002_live_inventory.py -q` → **7 passed**; **7 de 9
  mutaciones** murieron (A×2, B, C×2, D×2 — una promesa por test).
- Regeneración: `make agents` en copia `git archive` → **rc=0, sin deriva** (2 agentes).
- **Suite completa no realizada** (directiva del dueño); no se declara verde completo ni gate
  de CI verde.
- Revisión independiente: `review.md` — **4 bloqueantes (B1–B4) cerrados** en `dd5196df` (con O1
  y O2); O3 y O4 a deuda declarada. **No hubo segunda revisión independiente**: el orquestador
  verificó los criterios de cierre exactos del reviewer, declarada.
- Intake por ruta C válido en las dos revisiones (render canónico == `PACKET.md`).

## 3. `deferred-hardening` de la spec §8 — conservado con su disposición

| Ítem de §8 | Disposición registrada |
|---|---|
| Acreditación semántica exhaustiva de la suite | **Fuera del compromiso** de esta unidad por el contrato del epic; la carga se reparte con la revisión semántica independiente. |
| Poda, controles de sensibilidad y mutación del piloto | **013-003-redundancy-pilot.** Aquí no se retira ningún test. |
| Clasificador automático de equivalencias | **No necesario**, declarado: no acredita conservación. Sin unidad destino. |
| Rediseño del chequeo histórico de conservación | **No prometido**: la conservación comprometida se verifica contra una revisión anterior válida (PC-6), no por garantía automática nueva. |
| Resolución del contrato del helper `tests/_rf2_open_pause.py` | **Deuda explícita y visible** (contrato literal `VERIFY`, confianza baja) en `docs/suite-maintenance.md` y en la evidencia de PC-3; su resolución requiere identificar y contrastar un contrato real y **no se acredita por `validate rc=0`**. Sin unidad asignada. |
| Resolución de deuda temporal de 008-002 | **No pertenece a esta unidad**; su disposición se conserva. |
| Rendimiento, fixtures y paralelismo | **013-004-suite-performance**, que **sólo se abre por decisión del dueño**. |
| Obediencia infalible de agentes | **No prometida**: se verifica la norma distribuida (orquestador, handoffs, re-entry) y se exige evidencia por los gates existentes. |

Ninguna exclusión aplace una postcondición PC-1–PC-8.

## 4. Deuda declarada (fuera de §8)

- **O3** — dos mutaciones sobreviven: invertir el gate a «bloquea en RED» deja los 7 focales en
  verde (el test D1 no verifica la semántica de los momentos en los handoffs) y eliminar los 2
  `VERIFY` históricos también; el test A1 no ejecuta `validate` pese a su nombre y comprueba
  nodeids sólo por archivo (el `validate` del gate cubre esa parte). Corresponde a test-writer si
  se promueve.
- **O4** — `test_b1_collision_leaves_the_old_packet_valid_and_receivable` se mapea sólo a PD-6,
  aunque su docstring cubre también INV-3 y PD-4.
- **Correspondencia semántica de 16 de las 21 asignaciones nuevas o corregidas** sin examinar a
  fondo: el reviewer contrastó ruta, recuento real y nombres, y sólo miró nombres de tests en 5
  módulos. Deuda declarada, no acreditación.
- **Contrato literal `VERIFY` del helper `tests/_rf2_open_pause.py`** (confianza baja), separado
  de pendientes estructurales y de acreditación semántica.
- **3 `placeholder_targets`** preexistentes del mapa y **~30 módulos** con
  `static_test_nodeids` distinto de la colección real: declarados como históricos/estáticos en
  `docs/suite-maintenance.md`, **no** corregidos por esta unidad.
- **Abstenciones del reviewer sin cerrar:** `tests/test_008_002_suite_selection.py` no ejecutado
  (orden y deduplicación de `list` no verificados más allá del caso SELF); tabla de decisiones
  vigentes no contrastada contra `docs/adr/`; ejemplo `surface --base HEAD` no verificado sobre
  el repo real.
- **Hallazgo de tooling al preparar paquetes de esta feature:** un `--write-scope`/`scope.root`
  que apunta a un **archivo existente** se rechaza con `scope root must designate a directory`
  (`skills/cdad-cycle/scripts/cdad_packet.py:1436-1437`); hay que usar el selector `path`. Y
  `docs=docs` como selector de escritura **choca con las referencias `contract` en `begin`**:
  `_refuse_covered_contract_references` (`cdad_continuity.py:1277-1326`, 008-004 PC-06) rechaza
  antes de persistir cualquier referencia `contract` alcanzada por el `write_scope` —correcto
  como fail-closed, pero los paquetes que documentan bajo `docs/` y citan un contrato que vive
  ahí necesitan selectores más estrechos—. No se corrigió el producto; queda declarado.
- **Suite completa no realizada.**
- **Sin segunda revisión independiente** (verificación del orquestador sobre los criterios de
  cierre del reviewer, declarada).
- **Despliegue pendiente (reserva del dueño):** el producto no está en el árbol instalado, así
  que los runtimes instalados no transmiten la regla de inventario vivo; y sigue vigente la
  deuda de 013-001 —la CLI de HOME emite paquetes con instrucciones obsoletas, de modo que
  **hasta desplegar, los paquetes se preparan con `scripts/cdad_packet.py` del repo**.

## 5. Límites de esta evidencia

Verde **estructural** sobre la revisión con los deltas materializados, no acreditación semántica;
evidencia **focal** (7 tests) más colección, no suite completa; `make agents` verificado en copia
`git archive`, no sobre el árbol instalado; no se re-ejecutaron las mutaciones de la review (O3 es
deuda declarada); el contraste decisión-vigente/`docs/adr/` no se realizó; no se evaluó conducta
real de agentes, que la spec excluye explícitamente.
