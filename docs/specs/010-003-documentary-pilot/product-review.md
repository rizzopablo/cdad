# Revisión del producto: 010-003-documentary-pilot (T6, reviewer/review)

**Dictamen:** el producto corrige los tres defectos conocidos, pero queda **1 hallazgo bloqueante (F-1)** sobre el inicio del plazo de respuesta y debe pasar por T7.

**Validación del encargo (ruta C):** la metadata coincide con `REQUEST.json`. `cdad_packet.py render` dio rc=0 y `cmp` contra `PACKET.md` dio 0, sin diferencias en 13453 bytes. El contexto de ejecución es v2 y el sha256 del contrato coincide.

## 1. Diff y ascendencia

| Comprobación | Resultado |
|---|---|
| Commit del producto | `7fcca219e119ea72f29d68f406642afa5b2e1483` |
| Diff | `A docs/specs/010-003-documentary-pilot/product/relevamiento.md`, 38 inserciones, **ningún otro archivo** |
| Desciende de `cd2d57b3…` | Sí: `git merge-base --is-ancestor` rc=0 |
| Registro versionado en `4c822805` | Sí: el commit contiene `preparation-record.md`, y también desciende de él el commit del producto (rc=0) |
| Producto desde `7fcca219` hasta HEAD | Sin cambios; tampoco hay cambios pendientes en el árbol de trabajo |
| `tests/` desde `cd2d57b3` hasta HEAD | 0 archivos cambiados |
| Hashes de fuentes, inventario, candidato, clave y verificador | Coinciden con `preparation-record.md:24-33` |

Comandos: `git show --stat/--name-status`, `git merge-base --is-ancestor`, `git diff --name-only`, `git log -- <rutas>`, `sha256sum`.

## 2. Afirmaciones contrastadas

Ruta del producto: `docs/specs/010-003-documentary-pilot/product/relevamiento.md`. Todas las citas resuelven a una fuente inventariada y a un ancla registrada, por lectura propia y por el control.

| Línea | Afirmación | Cita | ¿La sostiene? |
|---|---|---|---|
| 3 | Documento sintético, sin datos reales | — (metadato) | Compatible con `inventory.md:6` |
| 5 | Describe la corrección del candidato | — (metadato) | Exacto frente a `negative.md` |
| 7 | Inventario y herencia de versión | — (metadato) | Sí: `inventory.md:3,31,36` |
| 11 | Registro del día, número correlativo, datos consignados | `s1-f01` | Sí, casi textual |
| 13 | La vía no altera la numeración ni el orden | `s2-f02` | Sí, textual |
| 15 | Solicitud incompleta: se observa y se pide completarla | `s1-f05` | Sí |
| 19 | Las fuentes no coinciden; no hay decisión acreditada | apoyada en 21-22 | Sí en lo que examina el corpus; ver O-1 sobre `s2-f01` |
| 21 | Definición de caso límite; Jefe de Registro con visto bueno previo | `s1-f02` | Sí |
| 22 | Solo la Dirección de Operaciones, sin visto bueno | `s2-f03` | Sí |
| 26 (1) | 15 días hábiles desde el registro | `s1-f03` | Sí, pero omite el calificativo operativo; ver F-1 |
| 26 (2) | `s2`: el mismo máximo, desde la recepción completa | `s2-f04` | Sí en el número y el inicio; «mismo» solo vale para los 15 días; ver F-1 |
| 26 (3) | Corre desde la recepción completa, no desde la primera presentación | `s1-f05` | Sí, textual; sin atribución y sin conciliar; ver F-1 |
| 30 (1) | Legajo anual, cinco años, por correlativo de recepción | `s1-f04` | Sí |
| 30 (2) | `s2`: por correlativo y fecha de resolución, cinco años | `s2-f05` | Sí; diferencia no calificada, ver O-2 |
| 34 | Contradicción sobre quién aprueba y sobre el visto bueno | `s1-f02`, `s2-f03` | Sí |
| 38 | P-01 | referencia a 34 | Sí |

## 3. Los tres defectos conocidos

Ubicaciones en `tests/fixtures/010_003_documentary_pilot/challenge/negative.md`, sin reproducir la clave.

| Defecto | Ubicación en el candidato | Estado en el producto | Traza |
|---|---|---|---|
| (a) Sin respaldo | `negative.md:23-25` | **Corregido.** La sección se eliminó; ningún fragmento la sostiene. | Ninguna (`grep` sin coincidencias) |
| (b) Contradicción omitida | `negative.md:13` | **Corregido.** La afirmación de criterio único desaparece y `s1-f02` y `s2-f03` quedan en las líneas 21-22 y 34. | Ninguna; `s1-f02` ya está citada |
| (c) Referencia insuficiente | `negative.md:21` | **Corregido.** La afirmación sobre el archivo cita `s1-f04` en la línea 30; `s1-f03` solo sostiene el plazo en la línea 26. | Ninguna |

`challenge-contrast.md` no contradice este dictamen. Sus observaciones O-1 y O-2 sobre el legajo y el inicio del plazo sí siguen vivas en el producto: ver F-1 y O-2.

## 4. Posiciones y pendientes

- **Posiciones:** ambas se conservan con localizador (líneas 21, 22 y 34). No hay consenso inventado ni elección de una posición.
- **P-01 (línea 38):** indica lo que falta, la condición de cierre, «designación pendiente» y la clasificación. Lo clasifica como no bloqueante, con respaldo en `spec.md:18` y `documentary-contracts.md:77-83`.
- **Pendientes faltantes:** el documento tiene solo P-01. La incertidumbre sobre el inicio del plazo no está declarada (F-1).
- **Propuestas:** no hay; PC-12 no aplica en ese punto.

## 5. Control estructural

```
$ python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py
........                                                                 [100%]
8 passed in 0.13s
rc=0
```

**Límites:** acredita la resolubilidad estructural de citas, inventario y anclas. **No** acredita fidelidad semántica ni que el documento sea correcto. El candidato negativo también pasa este control por diseño (PC-06).

## 6. Hallazgos

### F-1 (Required): divergencia sobre el inicio del plazo sin declarar

**Verdict: BLOCKING · Bucket: m**

- **Ubicación:** `relevamiento.md:26`, y ausencia en las líneas 32-38.
- **Evidencia:**
  - `s1-f03` cuenta «desde el registro de la solicitud».
  - `s1-f01` registra toda solicitud «el día de su recepción».
  - `s1-f05` y `s2-f04` cuentan desde la recepción completa; `s1-f05` excluye además la primera presentación.
  - Ninguna fuente dice si la solicitud completada se registra de nuevo.
- **Consecuencia:** tomemos una solicitud presentada incompleta el día D1 y completada el día D5. Según `s1-f03` y `s1-f01` podría contarse desde D1; según `s1-f05` y `s2-f04`, desde D5.
  - La línea 26 yuxtapone ambas reglas, usa «el mismo plazo» y cierra con una regla sin atribuir, lo que sugiere un punto resuelto.
  - La línea 34 habla de una sola contradicción y el documento declara solo P-01, así que el lector concluye que no hay otra incertidumbre.
  - Esto incumple «las divergencias existentes» (`spec.md:18`), PC-12 y `documentary-contracts.md:30-32`.
- **Salvedad:** el calificativo «solicitud completa» de `s1-f03` admite una lectura conciliadora. Por eso no afirmo que sea una contradicción cerrada, sino una incertidumbre que el corpus no resuelve y que el producto no declara. Es la razón del bucket m.
- **Condición de cierre:**
  - Atribuir cada inicio del plazo a su fuente.
  - Declarar la diferencia y que el corpus no aclara el registro de una solicitud completada después.
  - Agregar un pendiente con todos los campos de PC-12 y una clasificación justificada.
  - No elegir una regla sin decisión acreditada.
  - Re-verificar todo el diff en T7.

### O-1 (Consider): `s2-f01` sin usar

**Verdict: OPTIONAL · Bucket: m**

`relevamiento.md:19,34` sostiene que no hay decisión acreditada, y nunca cita `s2-f01`: la nota «se aplica junto con» el procedimiento del Área de Registro «y no lo reemplaza». Ese fragmento no resuelve el conflicto, pero es relevante para quien quiera dar prevalencia a `s2`. Propuesta: citarlo en P-01 como contexto, sin extraer de él una prelación que la fuente no fija.

### O-2 (Consider): diferencia en la organización del legajo sin calificar

**Verdict: OPTIONAL · Bucket: m**

`relevamiento.md:30` presenta `s1-f04` (correlativo de recepción) y `s2-f05` (correlativo y fecha de resolución), ambas atribuidas. Pueden ser compatibles, porque `s2-f05` no excluye a `s1-f04`, y por eso no bloquea. Propuesta: una frase breve que indique que la diferencia queda sin dirimir.

### N-1 (Nit): referencia frágil en P-01

**Verdict: OPTIONAL · Bucket: l**

`relevamiento.md:38` usa «sección anterior» y «la sección». Al agregar el pendiente de F-1 conviene nombrar «Divergencia registrada» y «Aprobación de casos límite».

## 7. Alcance y abstenciones

**Examiné:**
- Producto, contrato y `documentary-contracts.md`.
- `stage-4-review.md`, solo por búsqueda dirigida.
- Inventario, `s1`, `s2`, candidato y clave.
- `challenge-contrast.md` y el registro de preparación.
- `REQUEST.json`, `PACKET.md`, `execution.json` y `scripts/cdad_packet.py` (ejecutado, no leído).

**No leí:** `structural/`, el verificador, el plan ni otros documentos de la feature. Un `find` listó nombres de rutas bajo `.cdad/evidence/`, sin abrir contenido. No leí `verdict-tuple.md`: apliqué el formato de veredicto tal como lo fija mi rol.

**Archivos modificados:** ninguno en el repositorio. Usé un render temporal en `/tmp` y lo borré. El cambio en `docs/.cdad-state.json` ya existía al iniciar la sesión.

**Tabla de decisiones vigentes:** no comparada con `docs/adr/`, porque está fuera del alcance de lectura de este encargo.

**Abstenciones:**
- Si el contraste de `s1-f03` con `s1-f05` y `s2-f04` es una contradicción estricta: el corpus no alcanza para decidirlo y dejo esa calificación a la autoridad.
- La calidad de la auditoría de T5: solo vi su resultado en el contraste.
- La evidencia posterior de PC-13 y PC-14, que corresponde a T7 y al cierre.

**Límite:** esta revisión cubre este corpus sintético y no promete detección infalible.

## 8. Recomendación

No solicitar aceptación todavía. Enviar **F-1** a T7, con O-1, O-2 y N-1 a criterio de la autoridad. Después re-verificar todo el diff del producto y repetir el control focal.
