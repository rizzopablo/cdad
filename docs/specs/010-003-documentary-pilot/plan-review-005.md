# Dictamen plan-review (quinta vuelta, acotada al delta): 010-003-documentary-pilot

**Objeto:** `plan.md` v6, sha256 `49ce6f813aeb4e0bea0ff4f44d541a48deef29dc42f2af5aa6e05e5bf3352b04`, y `spec.md` v5, sha256 `f2dce9e0d1eb35d94d67ed3dfb4e756551d3b236f9513f7aee2ad50d0ff1d5e5`. Los digests coinciden con los bytes en disco.

**Intake:** ruta C con contexto v2. `validate-request` dio rc=0, `validate-packet` rc=0 y `render | cmp PACKET.md` rc=0. La identificación coincide con `render --route C`.

**Veredicto: aprobable.** No quedan bloqueantes. BN-3, O-13 y O-14 están cerrados, los scopes de T4 y T7 son construibles y no hay regresión. Los dos hallazgos siguientes son opcionales y no condicionan el veredicto. Este dictamen no aprueba nada: eso corresponde a la autoridad.

## Verificación del delta

| # | Veredicto | Ubicación | Fundamento |
|---|---|---|---|
| 1. BN-3, comando | **Cerrado** | `spec.md:186`; `plan.md:158,205,339,369,512,533,573,594` | El comando focal es idéntico en spec, prosa y bloque, también en T3 y T6. Los únicos `pytest` sin `--tb=no` son las regresiones de 010-001 y 010-002 (`plan.md:211,375`), que no ejecutan el verificador. |
| 2. BN-3, inspección en T3 | **Cerrado** | `spec.md:82`; `plan.md:126,187,516` | T3 comprueba que el verificador no lee `oracle/` y que sus mensajes y valores no reproducen la clave. La comparación contra la clave se atribuye al contraste del orquestador, y T4 la confirma antes del despacho. El resultado queda en `preparation-record.md`. |
| 3. BN-3, límite | **Cerrado** | `spec.md:52,186,254`; `plan.md:37,198,537,597` | El texto dice que ve nombres de casos, mensajes y valores, no el cuerpo; que no recibe clave ni muestras estructurales como insumo; y que `pytest` no es un sandbox. No queda ninguna promesa de que no vea el test en absoluto: «sin leer» se refiere siempre al archivo. |
| 4. O-13 | **Cerrado** | `spec.md:182,190`; `plan.md:178,353,464,536,597` | El mapa coincide con `_validate_scope`. «Exacta» aplicada a selectores queda solo en el contrato. También aparece en las frases que declaran el rechazo de la ruta exacta de `tests`, que son correctas. |
| 5. O-14 | **Cerrado** | `spec.md:190`; `plan.md:353,597` | T7 declara `product/` como raíz `contract`, y `_scope_contains` incluye `product/relevamiento.md`. |
| 6. Construibilidad | **Sí** | `cdad_packet.py:1419-1499` | Ver tabla siguiente. |

**Resultado de `_validate_scope` y `_scope_contains` (rol implementer, política real):**

| Comprobación | Resultado |
|---|---|
| Contrato por ruta, `contract` | Aceptado |
| `sources/` y `challenge/` por raíz, `tests` | Aceptado |
| `skills/cdad-cycle/references` por raíz, `implementation` | Aceptado |
| `product/` por raíz, `contract` (lectura) | Aceptado |
| `product-review.md` por ruta, `contract` | Aceptado |
| `product/` por raíz, `docs` (escritura) | Aceptado |
| Contención de `oracle/contrast-key.md`, `structural/x.md`, el verificador y `challenge-review.md` | `[]` en los cuatro |
| Contención de inventario, candidato, producto, informe de T6 y `stage-3-tdd.md` | Cada uno dentro de su selector |

## No regresión

- **PC:** son quince e idénticas byte a byte a las de la spec v3 (`c23f07ac`). PC-15 conserva su límite.
- **`plan-tasks`:** bloque único. `_plan_tasks_from_contract` lo acepta con T1..T8.
- **Presentes y sin debilitar:**
  - Precedencia de BN-1: `spec.md:152`.
  - Fijación de NB-1: `spec.md:76-87`.
  - Transcripción y git de NB-3: `spec.md:156`.
  - Discovery invalidante de NB-4 y tabla de O-10: `spec.md:160-167`, `plan.md:282-291`.
  - Recorte de T4 y T7.
  - Orden T3 → T4 → T5 → T6: `plan.md:23`.
  - D-4: `spec.md:242`.
  - Límites de §7.
- **Contradicciones nuevas entre spec y plan, o entre prosa y bloque:** ninguna.

## No bloqueantes

| # | Tupla | Ubicación | Hallazgo y remedio |
|---|---|---|---|
| O-15 | Consider · OPTIONAL · m | `spec.md:188,190`; `plan.md:353` | **Vía indirecta de la clave en T7.** T6 lee la clave y `challenge-contrast.md`, y su informe entra como insumo de T7. Ningún texto impide que `product-review.md` copie la clave. Eso reabriría de forma atenuada el riesgo de «corrección como copia», aunque `oracle/` esté fuera del scope. No afecta a T5. **Remedio:** añadir a T6 que sus hallazgos fundamentan contra fuentes e inventario sin transcribir la clave. |
| O-16 | Nit · OPTIONAL · m | `plan.md:126`; `plan-review-004.md:26` | **La inspección cubre `oracle/`, no `structural/`.** El dictamen anterior pedía ambas y la resolución adoptó solo la clave. El verificador debe leer `structural/` para PC-04–PC-06, así que sus diagnósticos pueden mostrar esas muestras. El límite sigue siendo verdadero, porque dice «como insumo», y el daño es bajo: son muestras de localizador, no respuestas. **Remedio:** ninguno obligatorio; basta tratarlo como límite aceptado. |

## Límites declarados, no deuda oculta

- El recorte de lectura, la exclusión de T5 y la precedencia de BN-1 son contractuales y auditables. No son aislamiento técnico.
- La raíz `skills/cdad-cycle/references` es más amplia que lo autorizado, y solo la restricción contractual la acota.
- `pytest` no es un sandbox. La salida focal muestra nombres, mensajes y valores, y no acredita fidelidad semántica.
- El ensayo acredita detección sobre un desafío declarado, sembrado y sintético, no a ciegas y sin generalización.
- Sin transcripción recuperable no se acredita independencia.
- Las fechas de git no prueban el orden.
- La comparación de bytes no prueba la ausencia de escrituras transitorias.
- Una lectura registrada no queda autorizada por ese registro.

## Abstentions

- No ejecuté `prepare`, porque escribe. El paquete real de T4 y los gates de `reviewer/review` en T5–T7 quedan sin comprobar de punta a punta. El plan exige rc=0 antes de despachar T4, pero no lo exige igual para T5–T7.
- No evalué el verificador real, que no existe. Si cumple la inspección de T3, solo se comprobará en ese momento.
- Sigue sin verificarse la legibilidad práctica del store del runtime y el enforcement del guard de lectura. El plan no presume ninguno de los dos.
- No apliqué la tabla de decisiones vigentes frente a `docs/adr/`: el delta no toca decisiones de código.
- No volví a medir el comportamiento de `--tb=no`. Me apoyo en la medición ya registrada en `plan-review-004.md:18` y en la cuarta resolución.
- `scripts/cdad_packet.py` difiere de `skills/cdad-cycle/scripts/cdad_packet.py`. Validé el paquete con el primero, y los scopes y el bloque con el segundo, que es el citado por la spec. No analicé esa diferencia.
- No consulté al asesor.

## Evidencia

- **Archivos modificados:** ninguno. **Commit:** ninguno. **Tests del repositorio:** no ejecutados.
- **Comandos:**
  - `python3 -B scripts/cdad_packet.py validate-request --request <REQUEST>`
  - `python3 -B scripts/cdad_packet.py validate-packet --request <REQUEST> --packet <PACKET>`
  - `python3 -B scripts/cdad_packet.py render --request <REQUEST> | cmp - <PACKET>`
  - `python3 -B scripts/cdad_packet.py render --request <REQUEST> --route C`
  - `sha256sum` de plan y spec.
  - `grep -n pytest` y `grep -n -i 'exact\|no ve \|sin leer\|no lee'` sobre spec y plan.
  - `diff` de las líneas PC contra `c23f07ac:spec.md`.
  - Script en línea con `cdad_packet._validate_scope`, `_scope_contains` y `_plan_tasks_from_contract`.
- **Salida relevante:**
  - `vr=0`, `vp=0`, `rc2=0`.
  - `pc-same-v3`, 15 PC.
  - `parsed ['T1', ..., 'T8']`.
  - Contención `[]` para clave, muestra estructural, verificador y `challenge-review.md`.
