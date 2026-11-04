# review.md — 016-002-gap-report, revisión del stage 4

**Paquete:** route C, `016-002-gap-report-reviewer-review-001`. Antes de empezar comprobé el paquete:
- `validate-request` y `validate-packet` terminaron con rc=0.
- `render` reproduce PACKET.md byte a byte.
- `render --route C` coincide con el bloque de identificación recibido.
- El sha256 de la spec es `315fad2c…54bc7c4b` y coincide con el declarado.

No toca código Odoo ni addons, así que no cargué skills de dominio.

**Objeto revisado:** el diff declarado `cf11fa15..HEAD` contiene solo estado, registro e inventario. La implementación (`d2996e7e`) y la referencia (`733d7afb`) quedan fuera de ese rango. Revisé `66304deb..HEAD`, que sí incluye las piezas que nombra el objetivo. Lo registro en Abstenciones.

**Comandos ejecutados:**
- `python3 -m pytest -q tests/test_016_002_gap_report.py tests/test_016_001*.py` → 16 pasados (5 de gap-report y 11 de 016-001).
- `/tmp/rv016/exp.py`: experimentos con fixtures autocontenidos.
- Degradaciones sobre copias en `/tmp/rv016/m` (16 en total).
- No modifiqué el producto, los tests ni el repositorio.

## Hallazgos bloqueantes

### B1 — Una exclusión duplicada oculta el hueco (incumple PC-6). Required
- **Dónde:** `skills/cdad-cycle/scripts/cdad_contract_links.py:1676-1698`.
- **Evidencia:** dos entradas idénticas para `unit-a` y la promesa B dan rc=1 y `status: invalid`, pero `gaps: []` y `excluded: ['B']`. La primera entrada se aplica y solo la segunda genera el diagnóstico.
- **Consecuencia:** la spec dice que una exclusión con identidad ambigua «no suprime el hueco que habría sin ella», y también lo dice §5 («No se admiten varias…»). Aquí el hueco PC-2 desaparece. Además, si los motivos son distintos, el resultado depende del orden de las entradas.
- **Corrección:** acumular las entradas por `(unit, promise)` y, cuando hay más de una, no aplicar ninguna y marcarlas todas inválidas.
- **Cierre verificable:** con la exclusión duplicada, PC-2 aparece en `gaps` y no en `excluded`.
- Verdict: BLOCKING · Bucket: h

### B2 — R-C no detecta una exclusión inválida que suprime el hueco (verificación de PC-6). Required
- **Dónde:** `tests/test_016_002_gap_report.py:419`.
- **Evidencia:** introduje una degradación que aplica la exclusión aunque el motivo esté vacío (y además emite el diagnóstico). Los 5 tests siguen pasando. El oráculo `assertIn("PC-2", pb.stdout)` se cumple igual, porque PC-2 aparece en `excluded` y en `obligations`.
- **Consecuencia para el usuario:** sin este control, un informe con una exclusión inválida puede borrar huecos accionables sin que ningún test lo detecte. B1 es justo ese defecto y pasa en verde.
- **Corrección:** comprobar `PC-2` dentro de `payload["gaps"]` y su ausencia en `payload["excluded"]`. Añadir el caso duplicado y el de contrato o hash que no coincide. Es tarea del test-writer.
- Verdict: BLOCKING · Bucket: h

### B3 — La referencia no nombra al orquestador como materializador (PC-10, mitad documental). Required
- **Dónde:** `skills/cdad-cycle/references/contract-test-links.md` §«Informe de huecos».
- **Evidencia:** en esa sección no hay ninguna mención a «orquestador» ni a «fotografía». Las menciones de las líneas 13, 108 y 146 son de 016-001 y tratan los deltas de registro, no las exclusiones ni las fotografías.
- **Consecuencia:** PC-10 exige que la documentación identifique al orquestador como quien materializa las exclusiones y las fotografías opcionales. Hoy no queda claro quién escribe `EXCLUSIONS.json`, y puede acabar haciéndolo GREEN, que §5 prohíbe.
- **Corrección:** añadir dos frases. La primera: el orquestador materializa las exclusiones autorizadas. La segunda: stdout es el producto, y una fotografía versionada la conserva el orquestador junto con su comando y su revisión, sin que la CLI la escriba.
- Verdict: BLOCKING · Bucket: h

### B4 — Las unidades no cerradas desaparecen del informe y R-A lo exige (§3 y §6 frente al test). Required
- **Dónde:** el código en `cdad_contract_links.py:972-973` y el test en `test_016_002_gap_report.py:271`.
- **Evidencia:** la fila actual `unit-c` en estado `in-progress` no aparece en ninguna parte del JSON. `out_of_universe` solo recoge unidades `done` sin spec, y R-A afirma `assertNotIn("unit-c", flat)`.
- **Contraste con la spec:**
  - §3: «Las demás filas quedan fuera del universo, con su estado recuperable».
  - §6 pide como mínimo «cierres no registrados y unidades fuera del universo».
  - PC-1 solo prohíbe que la unidad se reincorpore *al universo*.
- **Consecuencia:** el usuario no puede distinguir una unidad en curso de una que no está en el estado (promesa A). Además, el oráculo rechaza una implementación que cumpla la spec.
- **Corrección:** listar las filas no `done` en `out_of_universe` con su `status`. Cambiar R-A para que compruebe que `unit-c` no está en `universe` y sí está en `out_of_universe` con `in-progress`.
- Si la lectura que se quiere es «recuperable desde el archivo de estado», debe quedar escrita como decisión, y entonces este punto deja de bloquear. Esa interpretación la decide el usuario.
- Verdict: BLOCKING · Bucket: m

## Hallazgos no bloqueantes

### N1 — Huecos de verificación que dejan pasar degradaciones
Todas estas degradaciones sobreviven con 5/5 en verde:
- **Verificador compartido entre obligaciones** (solo acredita el primer pc_id; R-B solo mira PC-1, `test:326`). Consecuencia: una regresión que exija un test por obligación pasa en verde. Debería comprobar también PC-2.
- **No indexada contada como hueco** (R-E solo busca la cadena `"unit-b"`, `test:513`). Debería comprobar `unit-b ∈ not_indexed` y su ausencia en `gaps` y `obligations`.
- **Modo legacy y su etiqueta de cobertura:** no hay ningún fixture legacy. Probé a mano que funciona (`mode: legacy`, etiqueta correcta, hueco L-2).
- **Mezcla de marcadores e índice legacy:** sin test.
- **Ambigüedad histórica y deduplicación:** sin test. Probé a mano que funcionan (`ambiguous_closure` da rc=1; las copias equivalentes se deduplican).
- **Recuperación de la evidencia de cierre (PC-1):** no se comprueba.
- **Reordenar bindings:** sin test.

Las degradaciones que sí se detectaron, una por promesa:
- A: la copia histórica reincorpora la unidad; se ignora el hash del cierre.
- B: el review no cuenta como verificador.
- C: el motivo vacío se acepta; lo excluido se presenta como declarado.
- D: hora en la salida; mutación de entradas.
- E: se exige colección; se eliminan los límites.

Es decir, cada promesa A–E tiene al menos un verificador que falsifica, aunque la cobertura interna es parcial. Lo marco como opcional porque solo B2 tiene una consecuencia de usuario demostrada (B1).
- Verdict: OPTIONAL · Bucket: h

### N2 — Rutas absolutas del host en los informes con error (§6). Required
- **Dónde:** `cdad_contract_links.py:874-875, 1086, 1174-1175, 1581-1582`, donde se repiten `args.*` y `given` tal como llegaron.
- **Evidencia:** con `--state` absoluto inexistente, la salida contiene `str(root)`. Lo mismo pasa con un registro absoluto que no existe.
- **Consecuencia:** un informe rc=1 no es reproducible entre máquinas, y §6 lo prohíbe sin distinguir éxito de error. La degradación «estado como ruta absoluta» tampoco la detecta ningún test.
- **Corrección:** mostrar en los mensajes la ruta relativa a ROOT cuando sea posible, o un marcador `<fuera del proyecto>`.
- Verdict: OPTIONAL · Bucket: h

### N3 — Reordenar bindings cambia la salida cuando dos archivos tienen el mismo contenido (PC-7). Nit
- **Dónde:** `cdad_contract_links.py:1192-1211`.
- **Evidencia:** `unit-a=r1.json unit-a=r2.json` (mismo sha) da `inputs.registries.unit-a.path = r1.json`; con el orden invertido da `r2.json`.
- **Consecuencia:** es un caso raro, pero contradice tanto PC-7 como la frase de la referencia («Reordenar los vínculos no altera el resultado»).
- **Corrección:** elegir la ruta menor en orden lexicográfico, o rechazar la duplicación.
- Verdict: OPTIONAL · Bucket: h

### N4 — Filas actuales duplicadas: gana la primera sin aviso. Nit
- **Dónde:** `cdad_contract_links.py:909`.
- **Evidencia:** con `[done, in-progress]` para la misma unidad, la unidad entra en el universo; con `[in-progress, done]`, no entra.
- **Corrección:** tratarlo como ambigüedad, igual que el caso histórico.
- Verdict: OPTIONAL · Bucket: h

### N5 — Un registro inválido hace desaparecer los huecos conocidos por marcadores. FYI
- **Evidencia:** si `unit-a` tiene un nodeid ausente de la colección, sale rc=1 con `gaps: []` y `index.mode: markers`.
- La spec lo admite, porque el resultado es explícitamente incompleto y no presenta una clasificación como válida. Aun así, el lector pierde los huecos que se conocían solo por los marcadores.
- Verdict: OPTIONAL · Bucket: m

## Comprobaciones conformes, con evidencia

- **Doble corrida:** la salida es idéntica byte a byte (R-D y degradación de hora detectada).
- **Efectos:** las entradas no cambian y la herramienta no ejecuta tests; en el código no hay subprocess.
- **Códigos 0/1/2:** se respetan.
- **Código 0 con huecos:** es coherente con §2. El informe separa «informe producido» (campo `status` y el límite `GAP_LIMIT_NO_PROTECTION`) de «cobertura», y `declared` no implica ejecución.
- **`validate`:** sigue intacto; sus 11 tests pasan y su firma no cambió.
- **Proyectos sin registros:** el informe se produce sin colección e incluye `registry_note` «sin registro de vínculos declarado».
- **Referencia:** remite al formato de colección de 016-001 sin copiarlo, y declara que no crea gates. Sus punteros a `handoff-prompts.md`, `stage-3-tdd.md` y `re-entry.md` no mencionan gap-report, pero solo apuntan al contexto general y no prometen nada.
- **Registro materializado:** cinco links que cubren PC-1..PC-10, con nodeids que apuntan a los tests reales.

## Abstenciones

- **Rango del diff:** el diff declarado `cf11fa15..HEAD` no contiene la implementación ni la referencia. Las revisé en `66304deb..HEAD`. Si el orquestador quería revisar solo ese rango, el objetivo del paquete se contradice; le toca resolverlo.
- **Tabla de decisiones vigentes frente a `docs/adr/`:** no la contrasté en profundidad. No vi ningún ADR afectado de forma evidente.
- **Validación del registro de 016-002 con `validate`:** no corrí la validación completa con una colección real (rc=2 por falta de `--collection`). No afirmo nada sobre su verde estructural.
- **Suite completa:** no la ejecuté. Según la política por momento, corresponde al cierre del epic.

Archivos modificados: ninguno. Commit: ninguno, porque el rol es de solo lectura.
