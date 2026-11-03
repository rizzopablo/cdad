# test-audit — 013-003-redundancy-pilot

## 2. Lote auditado

* A: `tests/test_005_013_t1_unit_projection.py::test_b1_collision_with_published_projection_fails_closed_and_keeps_bytes`
* B: `tests/test_005_013_t1_unit_projection.py::test_b1_collision_leaves_the_old_packet_valid_and_receivable`
* C (control vecino): `tests/test_005_013_t1_unit_projection.py::test_b1_no_collision_with_custom_out_dir_still_publishes`
* Verificador histórico 013-002: `tests/test_013_002_live_inventory.py::test_013_002_C_mapa_inicial_B1_identificado_por_entrada` (+ `::test_013_002_C_conserva_origen_y_metadatos_historicos` como contraste).

## 3. Comparación PC-2 (estados / acciones / comprobaciones)

| Recorrido | Estado inicial | Acciones del fixture | Comprobaciones actuales |
|---|---|---|---|
| A, sin despacho previo | 1× `prepare architect/discovery` OK publicado en dir por defecto; `UNIT-CONTRACT.md` + `REQUEST.json` con pin | `edit_active_unit_scope` (cambia fila activa para que la regeneración no sea byte-idéntica); `complete_active_packet` (transición orquestador `prepared→completed` para que la 2ª corrida llegue a publicar); `--out-dir` custom VACÍO (re-acuña `-001`) + 2º `prepare discovery --out-dir custom` | `rc!=0`; `packet_id` nombrado en `stderr`; `sha256(proyección) antes==después`; `REQUEST.json` viejo byte-idéntico. Protege INV-3/PD-4: rechazo + diagnóstico + conservación. No despacha, no hace `receive`. |
| B, con despacho previo | Igual que A + `record-dispatch` OK; guarda `active_packet` dispatched (`active_before`) | Mismas 3 acciones que A + 2º `prepare` (sin asertar rc) + `restore_active_packet(active_before)` + `receive` | `contract.sha256 == sha256(archivo)`; `receive rc==0`, `packet_validation==passed`, `identity_validation==passed`, `semantic_status==pending`. Protege INV-3/PD-4/PD-6: pin coherente + recevabilidad posterior. No aserta `rc!=0` ni nombre en `stderr`. |
| C, sin colisión | 1× `prepare draft` OK (otra subetapa, deja `.cdad` existente) + `complete_active_packet`; el `-001` de `discovery` NO existe en dir por defecto | `--out-dir` custom VACÍO + `prepare discovery --out-dir custom` | `rc==0`; proyección en ruta canónica con `unit_block()`; `sha256(archivo)==contract.sha256==active_packet.contract_sha256`; `PACKET.md+REQUEST.json` quedan en custom. Protege PD-4/PD-5 camino feliz. |

Diferencias no internas (no se descartan):
* Completar el binding es precondición de llegada a publicación (sin ella el CLI responde `rc=2 active packet … is 'prepared'`); no es detalle de implementación, es transición declarada del orquestador que el propio fixture documenta.
* Restaurar el binding en B es lo que permite observar "el paquete viejo sigue siendo el registrado y utilizable" (PC-2: efecto de completar/restaurar en B). A no puede observar recevabilidad porque nunca despacha; B no puede observar rechazo porque no lo aserta.
* Compartir `rc`, preparación (`edit_active_unit_scope`, `complete_active_packet`, `make_custom_out_dir`) o cobertura no basta para consolidar (PC-2, último párrafo).

## 4. Disposición única por test (013-001) + contribución diferencial

**A — Mantener.** Promesa: colisión contra proyección publicada falla cerrada y conserva bytes. Obls: INV-3, PD-4 (docstring `test_pd1…:71-77`, B1 `1117-1129`). Contribución diferencial: único que exige `rc!=0` + nombre del paquete en `stderr` + `REQUEST.json` intacto. Sin A se pierde la obligación de diagnóstico accionable; B ejecuta la colisión sin asertarla. Evidencia: verde focal (ver §6); docstring RED-hoy medido (reescritura `2237d30d…→cec98be9…`, `rc=0` sin nombrar).

**B — Mantener.** Promesa: tras la colisión el paquete viejo sigue válido y recebible. Obls: INV-3/PD-4/PD-6 (B1 `1169-1187`). Contribución diferencial: único que exige `contract.sha256==digest` tras colisión + `receive passed/pending` con binding restituido. Sin B, una regresión que conserve bytes pero rompa `receive` (p. ej. validar contra plan vivo en vez de proyección durable — RED-hoy `rc=2 contract sha256 does not match exact content`) pasaría A y C. Evidencia: verde focal; RED-hoy medido documentado.

**C — Mantener (control intacto).** Promesa: sin colisión el `--out-dir` custom publica bien. Obls: PD-4/PD-5 control. Contribución: evita que la corrección CREATE-ONLY rompa el camino sin colisión (RED-hoy `rc=2 cannot write prepared packet … extra-000`). Sin C, un fix de A que bloquee todo custom-out pasaría A+B. No se toca por alcance ("el control C permanece intacto"). Evidencia: verde focal.

Ningún test Retira (la spec §3 PC-1: no elimina obligaciones de 005-013). Ningún Sustituir/Consolidar/Extender/Añadir acreditado en este AUDIT. Ante duda, Mantener — aquí además con evidencia positiva de diferencia.

## 5. Mapa de conservación PC-6

* `pc-map.json:446-475`: dos registros B1, ambos `VERIFY`, `task: 013-002-live-inventory`, `decision: mantener`: PD-4→A (variante rechazo+bytes), PD-6→B (variante pin+receive pending). `target_nodeid` cadena en ambos. OK.
* Examen INV-3 y PD-4 en B (pedido 013-003 PC-6): el docstring de B declara INV-3/PD-4/PD-6 pero la entrada de mapa de B solo tipifica `contract.id: PD-6` (fuente cita PD-6). La variante observable sí menciona pin (`contract.sha256 sigue coincidiendo`), luego la diferencia está conservada en texto aunque el `id` sea PD-6. No se propone cambio de mapa en este AUDIT porque el resultado es Mantener y la obligación histórica (destino actual = test actual antes de sustitución acreditada) ya se cumple; cualquier enriquecimiento del `id` sería cambio de asignación y pertenece a POST-AUDIT con aprobación, no a este delta vacío.
* Verificador 013-002 C1: exige que A/B pertenezcan al lote identificado por entrada (`task` o `decision_note` con `013-002-live-inventory`) y que `target_nodeid` sea el test actual. Se cumple (2 passed, ver §6). Si ambos se mantienen y no cambia esa expectativa, permanece intacto (spec 013-003 PC-7).

## 6. Resultado antes atribuible PC-3 (revisión inicial, selección focal exacta)

Comando (sin suite completa, sin gate CI):
```sh
python3 -m pytest -q -p no:cacheprovider \
  tests/test_005_013_t1_unit_projection.py::test_b1_collision_with_published_projection_fails_closed_and_keeps_bytes \
  tests/test_005_013_t1_unit_projection.py::test_b1_collision_leaves_the_old_packet_valid_and_receivable \
  tests/test_005_013_t1_unit_projection.py::test_b1_no_collision_with_custom_out_dir_still_publishes
```
Salida: `3 passed in 3.10s`, `RC=0`. Revisión `06fe83ce`, árbol limpio.

Contraste histórico:
```sh
python3 -m pytest -q -p no:cacheprovider \
  tests/test_013_002_live_inventory.py::test_013_002_C_mapa_inicial_B1_identificado_por_entrada \
  tests/test_013_002_live_inventory.py::test_013_002_C_conserva_origen_y_metadatos_historicos
```
Salida: `2 passed`, `RC=0`.

Configuración: `HOME` aislado por fixture (tempdir, nunca real); ids `999-…` sintéticos; `CLI_TIMEOUT_S=120`. Sin fallo inicial que declarar. El verde posterior (destinos finales, si los hubiere) queda pendiente de POST-AUDIT; al decidir Mantener, los tests quedan intactos y este verde acredita conservación.

Suite completa no realizada (sin autorización expresa; full-suite policy del packet). No se afirma verde global.

## 7. Viabilidad mutación / control negativo PC-5

Estado: **no realizado en AUDIT; no exigible para Mantener.** Fundamento:
* La mutación de implementación requeriría encargo separado sobre copia declarada; no autoriza al test-writer a leer/modificar implementación (spec PC-5 §121, invariante rol). No se intentó.
* El control negativo (verificador candidato + fallo pertinente atribuible, sin contar errores preparación/importación ni aserciones falseadas) solo es obligatorio antes de eliminar orígenes (PC-4). Al conservarse ambos, no bloquea.
* Viabilidad a futuro: acotada y honesta. Dos defectos propuestos (sobrescritura al colisionar; pérdida de recevabilidad) son ejercitables como controles negativos negro-caja vía los propios fixtures (2º `prepare --out-dir` + `receive`), con operador = corrida focal, selección = A/B, presupuesto = segundos, alcance al CLI vía `PACKET_CLI` en tempdir. Un mutante que no alcance el subproceso no acreditaría sensibilidad. Si POST-AUDIT pretendiera Sustituir/Consolidar, deberá declarar operador/ubicación/selección/presupuesto y producir fallo pertinente observado antes de eliminar.

## 8. Deltas documentales como texto (PC-6/PC-7, para materializar el orquestador)

Delta de tests: vacío (Mantener A/B/C; verificador 013-002 intacto).

```text
--- delta-mapa-013-003-audit: VACÍO ---
razón: decisión Mantener A/B/C; sin cambios de orígenes/destinos;
  entradas pc-map.json PD-4→A y PD-6→B (task 013-002-live-inventory) conservadas;
  target_nodeid siguen cadenas a tests actuales; registros/deudas ajenas intactas.
```

Delta de altas inventario (RED/properties/E2E): no aplica en AUDIT.

`python3 scripts/cdad-suite.py validate` no ejecutado en este AUDIT (medición de integridad sobre revisión con deltas materializados corresponde a re-entry/Review/cierre por el orquestador; no se convierte su ausencia en verde ni en bloqueo de AUDIT).

## 9. Decisión y límites PC-8

* Decisión: **Mantener A, Mantener B, Mantener C.** Justificación: contribuciones disjuntas (diagnóstico de rechazo vs. recevabilidad posterior vs. control camino feliz); consolidar exigiría localizar todas las comprobaciones y recorridos en un destino (PC-2) y demostrar sensibilidad (PC-4) — no acreditado ni necesario; Mantener es resultado válido.
* Incertidumbre declarada: cobertura INV-3/PD-4 en la entrada de mapa de B tipificada solo como PD-6 (variante sí la describe). No se resuelve eliminando tests (invariante 2).
* Cierre separa: (1) estructural pendiente del orquestador, (2) focal 3/3 + histórico 2/2 aquí, (3) revisión semántica pendiente, (4) experimento no realizado/no exigible, (5) suite completa no realizada. Sin extrapolación a ahorro/tiempo/rendimiento.

Evidencia requerida del rol: ficheros modificados: ninguno; comandos exactos + salidas + RC: §6; commit: ninguno (AUDIT no commitea; materializa el orquestador).

## Resolución (delegado del dueño, 2026-11-02)

AUDIT aprobado: Mantener A, B y C; delta de tests y de mapa vacíos con su razón; sin POST-AUDIT, RED ni GREEN (no hay cambio de comportamiento ni sustituto). El experimento de mutación queda **no realizado y no exigible** al no haber sustitución; su viabilidad como control negativo caja negra queda registrada. Siguiente paso: revisión independiente del resultado.

## Nota de corrección (orquestador, tras la review, 2026-11-02)

Corrige §7 y la Resolución. El estado del experimento de mutación (PC-5) es **«no realizado»**; la viabilidad por fixtures queda **inconclusa**. La afirmación «alcance al CLI vía `PACKET_CLI` en tempdir / control caja negra» es incorrecta: `PACKET_CLI` apunta a `REPO_ROOT/skills/...` (`tests/test_005_013_t1_unit_projection.py:124,127`) y solo el proyecto fixture está en tempdir; los fixtures ejercitan el CLI real pero no inyectan defecto. Inyectar un defecto exige una copia mutada de la implementación bajo encargo separado (PC-5). Un futuro Sustituir/Consolidar no puede heredar «viabilidad ya evaluada». Además, «contribuciones disjuntas» (§9) debe leerse «distintas con solape en la conservación del pin y los bytes».
