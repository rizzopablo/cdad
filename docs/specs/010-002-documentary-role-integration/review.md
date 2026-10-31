# Dictamen T8 — 010-002-documentary-role-integration

**La unidad no puede cerrarse todavía.** Hay tres bloqueantes, y los tres son de instrucciones o de registro. La lógica del CLI y el esquema no presentan defectos dentro de lo revisado.

**Intake (ruta C):** válido.
- `validate-request` dio rc=0.
- El render es igual byte a byte a `PACKET.md` y la identificación coincide.
- El sha256 del contrato coincide (`0d630c49…`).

**Mediciones propias en HEAD:**

| Comprobación | Resultado |
|---|---|
| Tests de integración, propiedades y 010-001 | 45 passed, rc=0 |
| `make agents` dos veces sobre `git archive HEAD` | rc=0 y hash idéntico sobre `agents` + `build` (`594fbd6d…`) |
| `diff -rq` contra `agents/` del repo | Sin diferencias |

No modifiqué nada del repo. Los temporales están fuera, en `~/clawd/tmp/rv8`.

## Bloqueantes

### B1 — Los adaptadores nativos prometen un rechazo mecánico inexistente
- **Severidad:** Required. **Verdict:** BLOCKING. **Bucket:** h.
- **Ubicación:** `sources/agents/adapters/opencode.md:76`, `sources/agents/adapters/claude-code.md:90`, `agents/cdad-orchestrator.md:311`, `agents/claude-code/cdad-orchestrator.md:312`.
- **Fundamento:** dentro de «Mechanism (native)» se lee «A required variant that is not published is rejected mechanically before launching the role work». D4 y PC-08 dicen que en la vía nativa es una detención procedimental y que la guarda mecánica corresponde solo al adaptador externo. El mismo agente orquestador lo dice bien en otra sección («no new mechanical guard is promised»).
- **Consecuencia:** el orquestador nativo puede omitir la comprobación de publicación porque confía en una guarda que no existe. La instrucción queda además autocontradictoria. Se viola PC-09 y el test está verde igualmente (ver punto 8).
- **Cierre:**
  - Corregir ambos adaptadores a la obligación procedimental y regenerar con `make agents`.
  - Reforzar el detector con esta frase literal como caso positivo.

### B2 — Los deltas Odoo de rol conservan batería incondicional
- **Severidad:** Required. **Verdict:** BLOCKING. **Bucket:** h.
- **Ubicación:** sección `cdad-section:odoo` de `sources/roles/reviewer.md`, `sources/roles/implementer.md` y `sources/roles/test-writer.md`, y sus seis agentes generados (tres por runtime). Las tres líneas de `sources/roles/*.md` que la spec §10 citaba como «Obligaciones Odoo de rol» quedaron sin tocar.
- **Fundamento:**
  - Reviewer: «Evidence required: green `make test-clean` + pasted output; `oca-checks` with 0 findings…».
  - Implementer: «GREEN evidence: green `make test`… clean lint».
  - Test-writer: «mandatory `@tagged`… Suites via make».
  - Las tablas de aplicabilidad nuevas viven en otra sección y dicen lo contrario. Nada subordina el delta a ellas, a diferencia de architect y orchestrator, que sí se corrigieron.
- **Consecuencia:** `cdad-reviewer-odoo` o `cdad-implementer-odoo` pueden exigir o fabricar evidencia de addon sobre un diff puramente documental. Ese es el fallo que la Promesa B prohíbe. Las skills lo atenúan, pero el agente sigue dando dos órdenes opuestas.
- **Cierre:** condicionar los tres deltas al diff o producto de addon, regenerar y añadir un control que falle con el texto incondicional actual. El test-writer conserva su régimen para los tests de addon. Decidir también cómo corre un verificador documental, ya que «raw python/pytest never emitted» sigue vigente; esto no puede ampliar permisos.

### B3 — El registro de I-10 omite que el registro del despacho pasó la guarda con el árbol alterado
- **Severidad:** Required. **Verdict:** BLOCKING. **Bucket:** m (inferencia temporal, no observación directa).
- **Ubicación:** `docs/specs/010-002-documentary-role-integration/deviation-green-accreditation-2026-10-31.md` §2, §3 y §7; `docs/epics/epic-010-documentary-specialization/execution.md:97-105`.
- **Fundamento:**
  - §2 dice que `record-dispatch` rechazó, y §7 que el despacho «queda registrado».
  - §3 solo describe comparaciones. Nada dice cómo se levantó el rechazo.
  - `dispatches/green-001-attempt01.json` tiene mtime 09:45:32.
  - `packets/roles/implementer.md`, que el registro lee, tiene mtime 09:45:48, ya restaurado.
  - La entrega en `stage_history` es de 09:45:58.
  - Con `verify_published_packet` previo a todo efecto, el registro casi con certeza pasó durante la restitución temporal, o con otra copia del CLI. La desviación descarta expresamente esta segunda vía.
- **Consecuencia:** la operación real fue satisfacer una guarda fail-closed reescribiendo temporalmente la fuente que lee. Quedó descrita como simple comparación, así que el defecto y su maniobra pueden repetirse en silencio.
- **Cierre:** añadir a la desviación la secuencia exacta de comandos, rc y horarios de `record-dispatch` y `receive`, declararlo como excepción a la guarda y fijar si es repetible o requiere al dueño.

## No bloqueantes

- **N1 — Evidencia sin commit (OPTIONAL, h):** `red-t5.md`, `tdd-t6-green.md` y `tdd-t7-properties.md` siguen untracked. Sin ellos EV-02 no es recuperable. Debe resolverse antes de EV-07.
- **N2 — Estado de la spec (Nit, h):** el encabezado de `spec.md` sigue diciendo «borrador… pendiente de aprobación» y `commit` es null. La aprobación está en otro archivo. Es confuso, pero el hash del contrato coincide.
- **N3 — Duplicación de la frontera (Consider, m):** las skills dicen que `odoo-expert` es dueño de la frontera, pero la repiten casi literal en cuatro lugares (`odoo-architect`, `odoo-make-env`, `odoo-reviewer`, `odoo-test-writer`), aunque afirman no repetirla. Puede divergir. Remedio: dejar el puntero y las consecuencias de cada rol.
- **N4 — Duplicación del párrafo de roles (Nit, m):** el mismo párrafo se repite en las seis fuentes de rol. Es consecuencia de la matriz y no genera defecto hoy.

## Verificación punto por punto

### 1. Postcondiciones e invariantes

| Ítem | Estado | Nota |
|---|---|---|
| PC-01, PC-02 | Acreditada | `handoff-prompts.md`, por campos existentes y sin variantes. |
| PC-03 | Acreditada | Control estructural, más doctrina de detención. |
| PC-04 | Parcial | B2 (implementer y test-writer). |
| PC-05 | Parcial | B2 (reviewer). Scribe y orquestador correctos. |
| PC-06, PC-07, PC-08 | Acreditadas salvo una cláusula | Lectura del código y tests verdes. La cláusula procedimental de variante ausente en vía nativa cae por B1. |
| PC-09 | **No acreditada** | B1. |
| PC-10 | Acreditada | `jsonschema` real con draft 2020-12, donde `dependentRequired` tiene efecto. |
| PC-11 | Acreditada | Medición propia. |
| PC-12.a | Acreditada por informe | Sin re-ejecución propia del recorrido T4. |
| PC-12.b | Acreditada | Tests verdes en HEAD. |
| PC-13 | Sostenible | Este dictamen separa estructura de juicio. Queda pendiente la aceptación. |
| INV-01, INV-02, INV-03, INV-04, INV-06, INV-07 | Acreditadas | INV-03 sin vigilancia exhaustiva, como admite la spec. |
| INV-05 | Parcial | B2 no exime addon, pero desordena la excepción documental. La cláusula del diff prevalente está presente. |
| INV-08 | Parcial | B3 mezcla una maniobra de admisión con una comparación. |

### 2. Decisiones D-1..D-5 y precisiones P-1..P-4

D-1, D-2 (salvo B2), D-3, D-5 y las cuatro precisiones se conservan. D-4 está incumplida en los adaptadores (B1). No hay agentes, campos ni selectores nuevos. `agents/` sigue con 22 archivos.

### 3. Aplicabilidad Odoo

- **(a) Liberación del documental:** sí en skills y referencias, no limpia en los deltas (B2).
- **(b) Addon bajo etiqueta:** no puede cobijarse. La regla del diff prevalente está en reviewer, orchestrator y `odoo-reviewer`.
- **(c) Mezcla:** operativa.
- **(d) Documentación dentro del módulo:** bien clasificada.
- **Referencias:** `evidence-and-quality.md` habla de un módulo que se declara listo, así que no contradice la matriz. En `odoo-sh.md` y `odoo-19-traps.md` solo hice búsqueda de palabras clave, sin lectura completa, y no apareció ninguna contradicción.

### 4. Destinatario

- La precedencia es correcta: el contraste estático va en la validación compartida y el contextual solo si no hay registro almacenado.
- El tipo de `agent` se valida antes del contraste (`cdad_packet.py:1814`).
- La repetición y la finalización no se reevalúan contra el stack vigente.
- Un `attempt_id` existente con otros datos sigue cayendo en `_completion_rejection`, así que no encontré esa vía de elusión.
- El histórico sin agente no recibe derivación.
- `agent` no entra en el render.
- Los registros pasan por `--record-dispatch`, y tanto `cdad_dispatch.py` como el adaptador externo lo invocan.

### 5. Defaults y permisos

No hay cambios en defaults, generadores ni guardas en el diff. El test-writer conserva escritura solo en tests y los roles de lectura no ganan escritura.

### 6. Procedencia

Los agentes son idénticos a la salida de `make agents` desde HEAD, y dos generaciones coinciden. Por lectura del informe de T7, las comparaciones de bytes de la instalación se hacen contra la fuente y no contra `build/staging`; no lo audité línea a línea (ver abstenciones).

### 7. Desviación I-10

- **(a) Parcialmente legítima.** La acreditación de la autenticidad del paquete es legítima en sustancia. Su verificabilidad por un tercero es solo parcial. Reproduje `e49f4b06`, `198ac0e6`, `d93b44e4` y `ef3dab65`. En cambio, `render` hoy falla con `active_packet mismatch`, así que la igualdad completa no se reproduce sin reconstruir el estado.
- **(b) Auténtico respecto del hash de rol declarado.** El archivo no cambió desde 08:59:55, antes del commit de T4. Mi comprobación cubrió ese hash, no el render completo.
- **(c) No suficiente.** Ver B3. El defecto en sí sí está bien registrado (`backlog.md:12`).

### 8. Riesgos de oráculo

- **Detector de guarda:** `claims_new_mechanical_guard` queda verde con B1 presente. Su ventana de negación de 300 caracteres alcanza previsiblemente el «never» de la frase vecina. La causa exacta es inferencia mía, aunque el verde junto al texto es un hecho.
- **Deltas Odoo:** los tests de aplicabilidad ven las tablas nuevas pero no la contradicción con los deltas. Presencia de texto no es coherencia.
- **Propiedades:** T7 no prueba transiciones de reemplazo. Están en T5, como se declara.

### 9. PC-13

La separación es real en esta unidad: los verdes no acreditan fidelidad y este informe llega a conclusiones que los tests no detectaron. Es recepción, no aprobación.

## Abstenciones

- **Suite completa y `tests/validate-odoo-specialization.sh`:** no los ejecuté. Corresponden al cierre.
- **Igualdad byte a byte del paquete T4 con su render:** no verificable sin reconstruir el estado de aquel momento.
- **Secuencia real de `receive` en I-10:** solo tengo horarios (entrega 10 s después de la restitución). Hace falta el log de comandos.
- **Ausencia total de `build/staging` como oráculo en los tests:** no la audité línea a línea. Me apoyo en el informe de T7 y en que los tests pasan.
- **Techo estático:** no lo re-medí.
- **Conducta real de modelos y fidelidad de un documento real:** fuera del alcance de esta unidad.

## Recomendación

No cerrar. Corregir B1 y B2 con un encargo acotado, regenerar y volver a ejecutar los tests afectados. Completar B3 en la desviación, incorporar la evidencia de N1 y hacer una re-revisión limitada a esos puntos antes de EV-07.

**Evidencia de este informe:**
- Archivos modificados: ninguno.
- Commit: ninguno.
- Comandos ejecutados:
  - `cdad_packet.py validate-request` y `render`
  - `pytest` sobre los tres módulos indicados
  - `make agents` dos veces en una copia descartable
  - `diff -rq`, `git diff 3bea7a8d..HEAD` y `sha256sum`
