# Propuesta: evidencia de suite, trazabilidad contrato→test y medición de redundancia

**Fecha:** 2026-11-02. **Estado:** borrador para discusión (dueño + architect). No aprobado.
**Origen:** conversación de cierre del epic 013 entre el dueño y el orquestador.
**Insumos:** `docs/epics/epic-013-test-criterion/closure.md`, `integration.md`; cierres de 013-001/002/003;
`docs/adr/ADR-041-evidencia-autorizada-y-criterio-de-contribucion.md`; `docs/suite-maintenance.md`;
`skills/cdad-cycle/references/stage-3-tdd.md` (Test evidence policy).

## 1. Hechos de partida (verificados)

- Suite: 1949 nodeids en 226 módulos `tests/test_*.py`; `cdad-suite.py validate` rc=0 (013-002).
  Duración documentada 46–103 min (`docs/ci-gate.md:64-66`).
- Epic 013 cerrado **sin suite completa** por directiva del dueño; ADR-041 convirtió esa directiva en norma
  del producto: «suite completa solo con autorización expresa», también en cierre de ciclo y de epic.
- Piloto 013-003: 2 tests + 1 control, elegidos por diferencias conocidas; resultado Mantener; mutación
  «no realizada», viabilidad inconclusa. **No es extrapolable.**
- Trazabilidad actual:
  - `suite-inventory.json`: cada nodeid → capacidad + contrato (clasificación, no acreditación).
  - `pc-map.json`: 31 registros a nivel obligación/variante, varios `VERIFY`.
  - 192 de 226 módulos de test citan `PC-n`/`PD-n` en su texto (grep, no verificado semánticamente).
  - Formato de postcondiciones en las specs no uniforme (un grep simple las detecta en 20 de 63 specs; la cifra
    real es mayor, el dato solo muestra que no hay formato extraíble común).
- La norma nueva de 013 **no está desplegada**; se aplicó una sola vez, con paquetes preparados desde el repo.

## 2. Problemas identificados

1. **Política de evidencia mal generalizada.** La exclusión de la suite completa respondía al costo de CDAD
   (proyecto con muchos epics). Como default del producto perjudica a proyectos jóvenes o grandes que añaden
   tests imprescindibles, y deja sin detección la regresión de contratos antiguos.
2. **Hueco de cobertura invisible.** La suite completa detecta regresión, no ausencia de test: un contrato sin
   verificador vinculado pasa en verde.
3. **Vínculo ≠ sensibilidad.** Un test vinculado a una PC puede no fallar si la PC se viola (013-001/002: los
   tests de presencia de texto dejan sobrevivir mutaciones semánticas).
4. **Redundancia sin medir.** No sabemos si la suite es optimizable; el piloto no lo responde.
5. **Criterio 013 sin validación operativa.** Nunca ejercitado con agentes instalados ni por el camino
   Sustituir (POST-AUDIT con sensibilidad).

## 3. Propuestas

### A. Corregir la política de evidencia (prioritaria, antes de desplegar 013)

| Momento | Default propuesto |
|---|---|
| Durante el ciclo (RED/GREEN/POST-AUDIT/review-fix) | Focal + regresión proporcional; sin suite completa |
| Cierre de ciclo (feature) | **Recomendada**; si no se corre, registrar «suite completa no realizada» + motivo |
| Cierre de epic | **Obligatoria por defecto**; omitir solo con dispensa expresa del dueño, registrada con motivo, por ese cierre |

- El costo se declara por proyecto (duración, alternativa: CI, worktree aparte, selección por dependencias);
  el default no depende de CDAD.
- Sustituye la parte correspondiente de ADR-041 (nuevo ADR posterior), alinea `stage-3-tdd.md` y consumidores
  (los mismos que tocó 013-001), con regeneración.
- Consecuencia: el cierre del epic 013 queda como dispensa pendiente; correr la suite una vez (autorizada) para
  regularizarlo.

### B. Trazabilidad contrato → tests

- **Hacia adelante:** cada test nuevo declara su vínculo (spec, PC/obligación) en formato verificable; el
  cierre de unidad comprueba que cada postcondición aprobada tiene ≥1 test vinculado (o exclusión declarada).
- **Chequeo de huecos:** listar postcondiciones de specs cerradas sin test vinculado. Requiere un formato de
  postcondición extraíble (hoy no uniforme).
- **Hacia atrás:** relleno por demanda (zonas a optimizar o de riesgo), no masivo: un relleno de 1949 tests
  por agente produciría vínculos nominales.
- Dónde vive: extender `pc-map.json`/inventario o un registro nuevo — **decisión abierta**.

### C. Medición de redundancia (muestreo calibrado)

1. Preregistro: definición de «asimilable», métricas, umbrales, presupuesto, parada.
2. Muestra estratificada (~60–80) por familia de capacidad y por antigüedad; el estrato «más nuevos» se
   sobremuestrea (hipótesis del dueño: más probabilidad de redundancia), tomado de varias features, no 100
   consecutivos (agrupamiento por feature reduce la precisión).
3. «Preexistente» = árbol en el commit padre de cada test.
4. Oráculo: mutación sobre copia de la implementación (encargo separado); redundante = ningún defecto detectado
   por el test escapa a la suite previa.
5. Auditoría ciega con disposiciones de 013-001; contraste con la mutación → proporción asimilable por estrato,
   falsos positivos del juez, costo por test.
6. Informe de extrapolación con intervalo; decide si abrir 013-004 (poda/rendimiento).

### D. Validar el criterio de 013 en operación

- Desplegar (decisión del dueño) tras A.
- Un ciclo real pequeño con agentes instalados, observando si los roles aplican el criterio.
- Un caso de Sustituir real o sintético que ejercite POST-AUDIT y la exigencia de sensibilidad.
- Cerrar las mutaciones semánticas que sobreviven en los tests de 013-001/002 (O1/O3).

## 3bis. Revisión del orquestador (correcciones a lo dicho en la conversación)

1. **B reabre parcialmente 013-001.** «Cada postcondición aprobada tiene ≥1 test vinculado» se acerca a la
   redacción que 013-001 retiró como cuota (deuda O5: «every postcondition has at least one test») y choca con
   «la postcondición no es cuota» (PC-1..3 de 013-001). Reformulación propuesta: **cada postcondición tiene un
   verificador declarado** — un test vinculado, o revisión/evidencia con exclusión declarada. La tensión queda
   explícita para que la decidan el architect y el dueño.
2. **C mezcla dos preguntas con oráculos distintos.**
   - Histórica (la del dueño): ¿el test era asimilable cuando se añadió? → contra el commit padre; valida el
     criterio de contribución.
   - De poda: ¿se puede quitar hoy? → leave-one-out contra la suite actual; es la que decide 013-004.
   C debe declarar cuál responde, o separarse en dos mediciones.
3. **El costo de C, tal como está escrito, probablemente es inviable.** «Ningún defecto escapa a la suite
   previa» exige correr la suite previa contra cada mutante (46–103 min por corrida × 60–80 tests × varios
   mutantes). El conjunto de comparación debe acotarse (p. ej. por capacidad vía `suite-inventory.json`), y esa
   cota es un supuesto que debilita la garantía. Se pide estimación de costo antes de preregistrar.
4. **A:** la corrida completa de cierre de epic usa el gate atribuible existente (`scripts/cdad-ci-gate.py
   close --all`, ADR-039), no un mecanismo nuevo.
5. La cifra «20 de 63 specs» de §1 viene de una regex débil: no usarla como dato; se pide medirla.

## 3ter. Opinión del architect (2026-11-02, sesión `<ses-329>`, solo lectura, sobre `ad7565d4`)

Materializada por el orquestador (ADR-003); resumen fiel, el texto completo queda en la sesión.

1. **A correcta.** La aprobación de la política debe autorizar por sí misma la corrida de cierre de epic (pedir
   permiso individual reproduce la contradicción de `stage-3-tdd.md:69-75`). Inestables: no reintentar hasta
   verde; suite lenta: presupuesto/entorno, no dispensa implícita; sin CI: ejecución local atribuible; la
   instalación limpia Odoo sigue como dimensión independiente. Nuevo ADR que supersede solo la cláusula de
   autorización/defaults de ADR-041 (contribución y obligaciones Odoo se conservan). Consumidores: `stage-3-tdd.md`
   (hogar), `SKILL.md`, `handoff-prompts`, `re-entry`, `anti-patterns`, `stage-4-review`, `stage-5-merge`,
   `state-detection`, `assets/feature-plan-template.md`, `packets/common.md`, `sources/roles/{implementer,reviewer,
   orchestrator,test-writer}.md`, `skills/cdad-epic/{SKILL.md,epic-integration.md,epic-closure.md}`,
   `skills/{odoo-make-env,odoo-test-writer,odoo-reviewer}` + `run-budget-protocol.md`, `docs/{ci-gate,
   suite-maintenance,systemPatterns}.md`.
   - **Corrección a §3bis.4:** el gate no tiene `close --all`; su paso `close` invoca `cdad-suite.py close
     --evidence-root … --all` (`scripts/cdad-ci-gate.py:311-313`, verificado).
   - **Corrección a §3.A:** no «regularizar» el 013: cerró bajo una directiva registrada; una corrida posterior es
     evidencia adicional, no reparación.
2. **B:** registro pequeño por unidad, separado del inventario (clasifica) y de `pc-map` (genealogía):
   `contrato+revisión → PC → verificador recuperable → comprobación protegida → evidencia/límites`, muchos-a-muchos,
   admite tests existentes. Mecánico: referencias, nodeids recolectables, PC sin verificador; la pertinencia la
   acredita revisión independiente. «Verificador declarado» mejora, pero declarado ≠ ejecutado ≠ pertinente; una
   exclusión no dispensa una promesa comprometida. No exigir test nuevo por PC (R2/R7) → resuelve O5 sin cuota.
3. **No normalizar retroactivamente.** IDs estables hacia adelante; contratos viejos por demanda. Medición propia:
   **62/63** specs tienen al menos un candidato de ID en posición declarativa (regex anclada; no mide extracción
   completa ni unicidad). La cifra 20/63 de §1 queda refutada.
4. **C:** separar historia y poda es imprescindible. 60–80 sin justificar: fijar precisión y presupuesto,
   aleatorio con probabilidades registradas y ponderación. Historia = incorporación de la protección, no del
   nodeid. Poda = leave-one-out; retiradas individualmente admisibles pueden ser incompatibles juntas. Mutantes
   finitos = sensibilidad acotada, nunca «ningún defecto»; clasificar equivalentes/no aplicados/inconclusos.
   Medir costo primero. Sesgos extra: mutantes favorables al juez, supervivencia, renombrados, parametrización,
   fixtures compartidos, inestabilidad. Hacer C **después de B mínimo**, como factibilidad, sin extrapolación ni
   poda prometidas.
5. **Orden:** A separada y urgente → B mínimo ejercitado mediante D → C independiente y opcional. No agrupar A–D.
   Sobra: regularización retroactiva y normalización masiva. Falta: tratamiento de rojos/skips en la corrida de
   cierre, responsable de `validate` en Mantener, criterio de suficiencia del mapa.
6. **Recomendación:** aprobar A; contraste independiente de coherencia legacy/paquetes/Odoo; desplegar con
   autorización; B sin backfill masivo; D como validación acotada; presupuestar C después. Esta propuesta no es
   aún un contrato.

## 4. Orden tentativo

A (corrección + suite completa del 013) → despliegue → D → B (adelante + chequeo de huecos) → C → 013-004 si C lo justifica.

## 5. Decisiones del dueño

1. ¿Aprueba los defaults de A?
2. ¿Acepta el costo de mutación sobre copia de implementación (C.4)? Sin él, C se limita a opinión de revisores.
3. ¿Umbral de redundancia que justificaría podar? ¿Tope de tiempo para C?
4. ¿Un epic con A–D o separar A como corrección urgente?

## 6. Preguntas abiertas para el architect

- ¿Es correcta la tabla de defaults de A? ¿Riesgos (tests inestables, costo en proyectos Odoo, CI ausente)?
- ¿Qué forma mínima de vínculo contrato→test es verificable sin gold-plating, y dónde debe vivir?
- ¿Es viable normalizar el formato de postcondiciones de las specs para el chequeo de huecos, o hay una vía menor?
- ¿El diseño de C es metodológicamente válido? ¿Tamaño de muestra, estratos, oráculo, sesgos no contemplados?
- ¿Orden y corte en unidades/epics? ¿Algo que sobre o falte?
