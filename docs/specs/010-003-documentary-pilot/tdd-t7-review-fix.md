Route C validated (`validate-request` rc=0, `validate-packet` rc=0; contract sha256 `f2dce9e0…` matches; execution v2). Work complete. FINAL TEXT:

# T7 implementer/review-fix — reporte final (010-003-documentary-pilot)

## 1. Diff conceptual de lo cambiado

**Agregado:**
- **P-02 (nuevo pendiente, sección Pendientes):** declara la incertidumbre sobre el inicio exacto del plazo cuando la solicitud llega incompleta y se completa después (sección Plazo de respuesta), con todos los campos de PC-12: información faltante (si la solicitud completada se registra de nuevo), condición de cierre (incorporar la regla/decisión acreditada con localizador y precisar el inicio), responsable (designación pendiente) y clasificación justificada (no bloqueante, porque el contrato promete documentar las divergencias en lugar de resolverlas).
- **Frase de cierre en Plazo de respuesta:** declara que el corpus no aclara el registro posterior y que el inicio exacto queda sin dirimir, sin elegir regla ni proponer conciliación.
- **Contexto `s2-f01` en P-01** (O-1): cita la nota de que el procedimiento de `s2` se aplica junto con el del Área de Registro y no lo reemplaza, sin extraer prelación.
- **Frase en Archivo** (O-2): la diferencia de organización del legajo (`s1-f04` vs `s2-f05`) queda sin dirimir, sin presentarla como contradicción cerrada ni como consenso.
- **Repetición de la cita `s1-f01` en Plazo de respuesta** para atribuir el inicio de `s1-f03` (registro el día de la recepción).

**Precisado (F-1):** la sección Plazo de respuesta ya no yuxtapone reglas ni usa "el mismo plazo" como si el punto estuviera resuelto: cada inicio queda atribuido a su fuente (`s1-f03` desde el registro + `s1-f01`; `s2-f04` desde la recepción completa; `s1-f05` recepción completa, no primera presentación) y la diferencia de inicio se hace explícita.

**Precisado (N-1):** "divergencia de la sección anterior" → "divergencia de la sección Divergencia registrada, relativa a la sección Aprobación de casos límite"; "reformular la sección" → "reformular la sección Aprobación de casos límite".

**Dejado igual:** estructura por secciones; las nueve citas existentes (conservadas todas); ambas posiciones sobre aprobación de casos límite con sus localizadores; declaración de documento sintético; declaración de corrección del candidato; sección Divergencia registrada; campos y clasificación de P-01. Ningún dato, persona u organización real agregados.

## 2. Nueva sección "Plazo de respuesta" (completa)

> La fuente `s1` fija un plazo máximo de quince días hábiles para responder una solicitud completa, contados desde el registro de la solicitud ([Plazo de respuesta](…s1.md#s1-f03)); ese registro se realiza el día de la recepción ([Registro de la solicitud](…s1.md#s1-f01)). La fuente `s2` fija un plazo máximo de quince días hábiles contados desde la recepción completa de la solicitud ([Plazo según Operaciones](…s2.md#s2-f04)). La fuente `s1` indica además que, cuando la solicitud llega incompleta, el plazo de respuesta corre desde la recepción completa y no desde la primera presentación ([Recepción incompleta](…s1.md#s1-f05)). Los inicios difieren: `s1-f03` cuenta desde el registro —que `s1-f01` sitúa el día de la recepción—, mientras que `s1-f05` y `s2-f04` cuentan desde la recepción completa. El corpus no aclara si una solicitud completada después se registra de nuevo, por lo que el inicio exacto del plazo en ese caso queda sin dirimir; este relevamiento no elige una regla ni propone conciliación (ver el pendiente P-02 de la sección Pendientes).

## 3. Nuevo P-02 (completo)

> - **P-02 (no bloqueante).** Falta la información que permita fijar el inicio exacto del plazo de respuesta cuando la solicitud llega incompleta y se completa después (sección Plazo de respuesta). Información faltante: si una solicitud completada después se registra de nuevo, dado que `s1-f03` cuenta desde el registro —que `s1-f01` sitúa el día de la recepción— mientras que `s1-f05` y `s2-f04` cuentan desde la recepción completa, sin que ninguna fuente aclare ese registro posterior. Condición de cierre: incorporar la regla o decisión acreditada sobre el registro de las solicitudes completadas, con su localizador, y precisar en consecuencia el inicio aplicable en la sección Plazo de respuesta. Responsable: designación pendiente. Clasificación: no bloqueante, porque el contrato del piloto promete documentar las divergencias existentes en lugar de resolverlas.

## 4. Tabla de comandos (salida y rc)

| Comando | Salida | rc |
|---|---|---|
| `python3 scripts/cdad_packet.py validate-request --project-root … --execution-context … --request …/REQUEST.json` | (sin salida) | 0 |
| `python3 scripts/cdad_packet.py validate-packet … --request … --packet …/PACKET.md` | (sin salida) | 0 |
| `python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py` | `8 passed in 0.14s` | 0 |
| `python3 -B -m pytest -q --tb=no tests/test_010_001_documentary_contracts.py tests/test_010_002_documentary_role_integration.py` | `40 passed in 58.16s` | 0 |
| `git merge-base --is-ancestor 7fcca219… HEAD` (pre y post commit) | (sin salida) | 0 |
| `git add …/product/relevamiento.md && git commit -m "fix(010-003): declara la divergencia del inicio del plazo y clasifica los pendientes (T7)"` | `1 file changed, 5 insertions(+), 3 deletions(-)` | 0 |

Verificador no leído ni modificado; `oracle/`, `structural/` y todo otro documento de la feature no leídos. Nota honesta: para confirmar el stat del commit propio ejecuté `git show --stat --oneline HEAD` (solo stat —1 archivo, 5+/3-—, sin mostrar contenido de ningún archivo); si la autoridad lo considera alcance excedido, queda registrado aquí.

## 5. Commit y ascendencia

- **Nuevo commit:** `6596e804654f9b76d3e7710c2011b312350fe75d` — `fix(010-003): declara la divergencia del inicio del plazo y clasifica los pendientes (T7)`
- **Desciende de** `7fcca219e119ea72f29d68f406642afa5b2e1483` (commit del producto de T4): `merge-base --is-ancestor` rc=0.
- **Toca solo** `docs/specs/010-003-documentary-pilot/product/relevamiento.md`. Preexistentes sin tocar: `M docs/.cdad-state.json`, `?? …/product-review.md`.

## 6. Archivos modificados

- `docs/specs/010-003-documentary-pilot/product/relevamiento.md` (único).
