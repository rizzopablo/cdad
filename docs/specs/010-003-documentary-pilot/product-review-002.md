# Re-verificación T7 (reviewer/review): 010-003-documentary-pilot

**Dictamen: aprobado para cierre. Sin bloqueantes; quedan 2 observaciones opcionales (N-2 y N-3).**

La ruta C es válida: `validate-request` rc=0, `validate-packet` rc=0, el render canónico coincide byte a byte con `PACKET.md` (`cmp` rc=0) y el sha256 de `spec.md` coincide con el contrato. El contexto de ejecución es v2.

## 1. Diff y ascendencia

- **Ascendencia:** `git merge-base --is-ancestor 7fcca219 6596e804` da rc=0. El padre directo de `6596e804` es `d2307c42`, que desciende de `7fcca219`.
- **Commit:** `6596e804` toca solo `product/relevamiento.md` (+5/−3), y coincide con lo declarado.
- **Diferencia con la formulación del encargo:** `git diff --stat 7fcca219 6596e804` sin filtro de ruta muestra 5 archivos, porque el rango incluye `d2307c42` (documentos y estado).
  - Ese commit no toca el producto: el único commit del rango sobre `relevamiento.md` es `6596e804`.
  - El rango tampoco cambia `tests`, `skills` ni `scripts`.
- **HEAD:** es igual a `6596e804`, y el producto y los fixtures están limpios.
- **Informe del implementer:** coincide con el diff. Están declarados los cambios en Plazo, Archivo, P-01 y P-02; no hay cambios silenciosos.

## 2. F-1: cerrado

Ubicación: `relevamiento.md:26` y `:40`. Las cinco condiciones de cierre de `product-review.md` se cumplen:

| Condición | Resultado | Evidencia |
|---|---|---|
| Atribuir cada inicio a su fuente | Cumple | `s1-f03`: desde el registro. `s2-f04`: desde la recepción completa. `s1-f05`: en la incompleta, desde la recepción completa y no desde la primera presentación |
| Declarar la diferencia y el vacío del corpus | Cumple | «Los inicios difieren…» y «El corpus no aclara…» |
| Agregar un pendiente completo | Cumple | P-02 (`:40`) |
| No elegir regla | Cumple | Declaración explícita, sin conciliación |
| Re-verificar todo el diff | Cumple | Este informe |

La declaración es verdadera contra el corpus: ni `s1` ni `s2` regulan el registro de una solicitud completada después. `s1-f01` solo fija el registro el día de la recepción, y `s2-f02` trata la vía de recepción y la numeración.

## 3. Pendientes y opcionales

- **P-02 (`:40`):** tiene todos los campos de PC-12.
  - Información faltante, condición de cierre y «designación pendiente» como responsable.
  - Ubicación: sección Plazo de respuesta.
  - Clasificación no bloqueante, justificada por `spec.md:18`, que promete presentar las divergencias y no resolverlas. También lo respalda `documentary-contracts.md` §3.
  - No usa esa admisión para eludir otra postcondición: PC-10 y PC-11 siguen cumplidas.
- **P-01 (`:38`):** sigue completo y conserva su clasificación.
- **O-1:** adoptada. La cita de `s2-f01` niega expresamente cualquier prelación.
- **O-2:** adoptada (`:30`). La diferencia queda sin dirimir.
- **N-1:** adoptada. Las secciones nombradas existen y las citas siguen intactas.

## 4. No regresión

Contrasté con la clave sin transcribirla.

- **Defecto 1 (afirmación sin respaldo):** no reaparece. La búsqueda de sus términos da 0 coincidencias y no existe la sección correspondiente.
- **Defecto 2 (contradicción omitida):** ambas posiciones se conservan en `:21-22` y `:34`.
- **Defecto 3 (referencia que no sostiene):** la afirmación sobre el archivo cita `s1-f04` (`:30`).
- **Citas:**
  - Antes había 12 enlaces y ahora hay 14; los dos nuevos son `s1-f01` y `s2-f01`.
  - Las 9 anclas originales se conservan y `s2-f01` es la décima.
  - Un script comprobó que los 14 enlaces resuelven a una fuente real con su ancla.
  - Los sha256 de `s1` y `s2` coinciden con el inventario.
- **Declaración de documento sintético:** se conserva (`:3`).

## 5. Afirmaciones contrastadas

Comparé todas las afirmaciones factuales de las líneas 11-40 con su fragmento; las nuevas fueron estas:

| Línea | Afirmación | Fragmento | Resultado |
|---|---|---|---|
| 26 | `s1` fija 15 días hábiles para una solicitud completa, desde el registro | `s1-f03` | Sostenida |
| 26 | El registro se hace el día de la recepción | `s1-f01` | Sostenida |
| 26 | `s2` fija 15 días hábiles desde la recepción completa | `s2-f04` | Sostenida |
| 26 | En la incompleta corre desde la recepción completa | `s1-f05` | Sostenida; el «cuando» agrupa las dos oraciones del fragmento de forma razonable |
| 26, 40 | El corpus no aclara el registro posterior | Corpus completo | Verdadera |
| 30 | Diferencia en la organización del legajo | `s1-f04`, `s2-f05` | Sostenida |
| 38 | `s2` se aplica junto con el procedimiento de Registro y no lo reemplaza | `s2-f01` | Sostenida; ver N-2 |

## 6. Comandos

| Comando | Salida | rc |
|---|---|---|
| `python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py` | `8 passed in 0.14s` | 0 |
| `python3 -B -m pytest -q tests/test_010_001_documentary_contracts.py tests/test_010_002_documentary_role_integration.py` | `40 passed in 48.40s` | 0 |
| `git show --stat --format='%H %P' 6596e804` | 1 archivo, 5+/3− | 0 |
| `git diff 7fcca219 6596e804 -- docs/specs/010-003-documentary-pilot/product/relevamiento.md` | Revisado completo | 0 |
| `git log --format=%h 7fcca219..6596e804 -- docs/specs/010-003-documentary-pilot/product/relevamiento.md` | `6596e804` | 0 |

**Límite del control:** el verde acredita estructura y resolubilidad de citas, no fidelidad semántica. La fidelidad la cubre la sección 5 de este informe.

**Archivos modificados:** ninguno. El estado local de la feature (`docs/.cdad-state.json` y los dos informes sin versionar) ya existía.

## 7. Hallazgos

**N-2 (Nit). Verdict: OPTIONAL · Bucket: l · Ubicación: `relevamiento.md:38`.**
«su procedimiento se aplica junto con el del Área de Registro» es menos exacto que `s2-f01`, donde lo que se aplica es «esta nota». El sentido no cambia. Remedio: escribir «la nota de `s2` se aplica junto con el procedimiento del Área de Registro…».

**N-3 (Nit). Verdict: OPTIONAL · Bucket: l · Ubicación: `relevamiento.md:26`.**
«Los inicios difieren» es exacto como comparación textual, pero para una solicitud completa desde su llegada los inicios pueden coincidir. El mismo párrafo ya acota lo no dirimido a «ese caso», así que no induce a error. Remedio: escribir «las formulaciones del inicio difieren».

Ningún hallazgo bloquea, y la calibración indica que los opcionales no prolongan el ciclo.

## 8. Alcance y abstenciones

**Examiné:**
- Producto completo y diff.
- `spec.md`: línea 18 y líneas 165-190, incluida la promesa D. No lo leí entero.
- `product-review.md`: F-1 y fragmentos de otras secciones, no todo el informe.
- `tdd-t7-review-fix.md`, inventario, `s1`, `s2`, `negative.md`, clave, `challenge-contrast.md`, `stage-4-review.md` y `documentary-contracts.md`.

**Lecturas fuera del alcance declarado, registradas:**
- `docs/systemPatterns.md`: un `grep` que mostró 3 líneas (encabezados y una fila de ADR). No revela nada sobre el producto.
- Un `find` listó rutas de `cdad_packet.py` bajo `.cdad/evidence/`, sin abrir contenido.
- `scripts/cdad_packet.py` se ejecutó, pero no lo leí.
- `REQUEST.json`, `PACKET.md` y `execution.json` son el plano de control de este encargo.

**No leí:** `structural/`, el verificador ni el plan.

**Abstenciones:**
- **Contradicción estricta o no:** no califico si el contraste del plazo lo es. El corpus no alcanza para decidirlo, y el producto tampoco lo afirma.
- **Tabla de decisiones vigentes:** no la comparé con `docs/adr/`, porque queda fuera del alcance de lectura. Esa parte del deber del revisor no se cumplió en este encargo; este producto documental no toca esas decisiones.
- **Independencia:** es procedimental, no técnica. Este informe no demuestra que no haya habido accesos sin registrar.

## 9. Recomendación final

**Aprobado para cierre por parte del revisor.** F-1 está cerrado, no hay regresiones y las pruebas están verdes. N-2 y N-3 quedan a criterio de la autoridad. P-01 y P-02 deben seguir visibles en el registro de cierre. La aceptación funcional y la suite completa corresponden a quien cierra.
