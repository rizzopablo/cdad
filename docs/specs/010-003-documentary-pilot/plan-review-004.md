# Dictamen plan-review (cuarta vuelta, acotada al delta): 010-003-documentary-pilot

**Objeto:** `plan.md` v5, sha256 `b7d396ca6849db32d1468f214ae794a7d71bc62d8e4f18ec7a51f3d987754a82`, y `spec.md` v4, sha256 `eca095280aeaa887208d2e93a4935c536da507f1c4720cda35cbfe9bf9868c1b`. Los digests coinciden con los bytes en disco.

**Intake:** ruta C con contexto v2. `validate-request` dio rc=0, `validate-packet` rc=0 y `render | cmp PACKET.md` rc=0. La identificación coincide con `render --route C`.

**Veredicto: aprobable con cambios.** BN-2 y O-9..O-12 están bien resueltos y nada de lo cerrado se movió. Queda **un bloqueante nuevo (BN-3)**, de corrección local: el límite declarado en el cierre de BN-2 es falso para el comando declarado. Este dictamen no aprueba nada.

## Bloqueante

### BN-3: el comando focal muestra código del verificador, y el contrato dice que no
**Required · Verdict: BLOCKING · Bucket: h**

- **Ubicación:**
  - Promesa: `spec.md:185`, `plan.md:196`, `plan.md:533` (T4 en `plan-tasks`), con el mismo límite por remisión en T7 (`plan.md:353`).
  - Gate y cobertura: `plan.md:541`, `plan.md:437`.
  - Comando: `focal_tests` de T4 y T7, `python3 -B -m pytest -q tests/test_010_003_documentary_pilot.py`.
- **Evidencia:** ejecuté un test mínimo que falla con ese mismo formato de comando. La salida incluyó el cuerpo de la función de test y el valor esperado (`assert 'doc' == 'CLAVE-SECRETA'`). `-q` no suprime el traceback. Con `--tb=no` desaparece el código, pero la línea `FAILED` conserva el mensaje de la aserción y ese valor.
- **Consecuencia:**
  - **Código:** es seguro que se muestra. Al empezar T4 `relevamiento.md` no existe, así que las pruebas de producto fallan en la primera ejecución, salvo que el verificador esté escrito de otro modo.
  - **Contrato:** «no ve el código del test» resulta falso sin ninguna infracción del implementer, porque el plan le ordena trabajar con esa salida.
  - **Fundamento de BN-2:** se debilita el punto 4 de la resolución («un oráculo que el productor no lee no se puede moldear»).
  - **Clave:** ninguna regla impide que una aserción o un mensaje impriman contenido de la clave o de las muestras. La fuga real depende de cómo se escriba el verificador, que aún no existe. Si ocurre, recae en el riesgo de PC-11 que NB-5 quería cerrar. La auditoría de T5/T6 no lo detectaría, porque esa salida es una lectura autorizada.
- **Condición de cierre:** spec y plan hacen ambas cosas:
  1. Fijan un comando focal para T4 y T7 con salida acotada, por ejemplo `--tb=no`, en los tres sitios: spec, prosa del plan y `plan-tasks`.
  2. Añaden a T3 una exigencia comprobable en la inspección previa a GREEN: los mensajes y valores de aserción del verificador no reproducen contenido de `oracle/` ni de `structural/`.

  Si la autoridad prefiere no tocar el comando, la alternativa mínima es conservar el punto 2 y reescribir el límite: «puede ver fragmentos del test en los tracebacks; no se le entrega el archivo». Esa opción es honesta, pero cede parte del fundamento de BN-2.

## Veredicto del delta

| # | Veredicto | Ubicación | Fundamento |
|---|---|---|---|
| BN-2 | **Cerrado**, salvo el límite tratado en BN-3 | `spec.md:51,181-185`; `plan.md:35,174-196`; bloque `plan.md:532-534` | El verificador sale de insumos y lectura y se ejecuta como `focal_test`. Los tres lugares son coherentes. `oracle/` y `structural/` siguen fuera y la justificación del recorte se conserva. Se exige rc=0 en `validate-request` y `validate-packet`. |
| Construible | **Sí, por raíces** | `cdad_packet.py:1419-1499` | Ver la tabla siguiente. |
| O-9 | **Cerrado** | `spec.md:75,126,232`; `plan.md:135,184,266,512` | El request cita el commit de preparación y el del producto desciende de él. Las dos identidades se conservan, así que un tercero puede comprobarlo. |
| O-10 | **Cerrado** | `spec.md:157-166`; `plan.md:282-291,554` | Tablas de cuatro filas equivalentes, criterio único, las referencias de método se registran sin invalidar y registrar no autoriza. Es fiel a la resolución. |
| O-11 | **Cerrado** | `spec.md:181`; `plan.md:176,532` | `stage-3-tdd.md` queda declarada con la advertencia sobre el selector. |
| O-12 | **Cerrado** | `spec.md:189`; `plan.md:351-353,593,602` | `read_scope` acotado, sin `oracle/`, `structural/` ni `challenge-review.md`. |

**Resultado de `_validate_scope` (rol implementer, política real):**

| Scope | Resultado |
|---|---|
| Contrato por ruta | Aceptado |
| `product-review.md` como `contract` por ruta | Aceptado |
| `sources/` y `challenge/` como `tests` por raíz | Aceptado |
| `skills/cdad-cycle/references` como `implementation` por raíz | Aceptado |
| `product/` como `docs`, lectura y escritura | Aceptado |
| `product/` como `contract` por raíz | Aceptado |
| `inventory.md` y `negative.md` por ruta exacta | **Rechazado** |
| `stage-3-tdd.md` por ruta exacta | **Rechazado** |

`_scope_contains` confirma que el conjunto aceptado no contiene `oracle/contrast-key.md` ni el verificador.

## No bloqueantes nuevos

| # | Tupla | Ubicación | Hallazgo y remedio |
|---|---|---|---|
| O-13 | Nit · OPTIONAL · h | `plan.md:176,351`; `spec.md:181,189` | **Texto más preciso que el mecanismo.** Se habla de lecturas «exactas», pero el selector admisible es la raíz `references/`, que alcanza `handoff-prompts.md` y otras. La advertencia del selector cubre esto. Además, inventario, candidato y normas solo se pueden declarar por raíz. **Remedio:** nombrar las raíces en el request o eliminar «exactas». |
| O-14 | Consider · OPTIONAL · h | `plan.md:351` | **Clase de `product/` como insumo.** Un `--input` bajo `product/` con scope `docs` queda fuera del `read_scope`: `_scope_contains` lo clasifica como `contract`. `prepare` lo rechaza de forma visible. **Remedio:** en T7 añadir `contract` root `product/` a la lectura, o no declarar el producto como input. |

## No regresión

- **PC:** las quince coinciden byte a byte con la spec v3 (`c23f07ac`). PC-15 conserva el límite de NB-2.
- **`plan-tasks`:** bloque único, JSON válido, T1..T8. T1, T2 y T5 no tienen archivos y usan `observable_checks`. T3, T4 y T7 declaran rutas.
- **Presentes y sin debilitar:**
  - BN-1: `spec.md:151`.
  - NB-1: `spec.md:75-86`.
  - NB-3: `spec.md:155`.
  - NB-4: tabla de `spec.md:161`.
  - Orden T3 → T4 → T5 → T6: `plan.md:23`.
  - D-4: `spec.md:241`.
  - Límites de `spec.md` §7.
- **Contradicciones nuevas entre spec y plan, o entre prosa y bloque:** ninguna fuera de BN-3.

## Límites declarados, no deuda oculta

- El recorte de lectura, la exclusión de T5 y la precedencia de BN-1 son contractuales y auditables. No son aislamiento técnico.
- La salida del verificador informa la corrección y no acredita fidelidad semántica.
- El ensayo acredita detección sobre un desafío declarado, sembrado y sintético, sin generalización.
- Sin transcripción recuperable no se acredita independencia.
- Las fechas de git no prueban el orden.
- La comparación de bytes no prueba la ausencia de escrituras transitorias.
- O-13: el selector de referencias es más amplio que lo autorizado.

## Abstentions

- No ejecuté `prepare`, porque escribe. Quedan sin comprobar de punta a punta el paquete real de T4 y si los gates admiten `reviewer/review` en T5–T7. El plan exige rc=0 antes de despachar, lo que cubre el primero. La construibilidad se comprobó con `_validate_scope` y `_scope_contains`.
- No evalué el verificador real, que no existe. La fuga de clave de BN-3 es una posibilidad condicionada; la exposición de código no.
- Sigue sin verificarse la legibilidad práctica del store del runtime y el enforcement del guard de lectura. El plan no presume ninguno de los dos.
- No apliqué la tabla de decisiones vigentes frente a `docs/adr/`: el delta no toca decisiones de código.
- No consulté al asesor.

## Evidencia

- **Archivos modificados:** ninguno en el repositorio; solo auxiliares en `/tmp/` (`/tmp/opencode_scope.py`, `/tmp/opencode/pt/test_x.py`).
- **Commit:** ninguno. **Tests del repositorio:** no ejecutados.
- **Comandos:**
  - `cdad_packet.py validate-request`, `validate-packet`, `render` y `render --route C` sobre este encargo.
  - `sha256sum` de plan y spec.
  - Script `json.loads` del bloque `plan-tasks`.
  - `diff` de las líneas PC contra `c23f07ac`.
  - Script `/tmp/opencode_scope.py`, que invoca `_validate_scope` y `_scope_contains` con la política real.
  - `python3 -B -m pytest -q test_x.py`, con y sin `--tb=no`.
- **Salida relevante:**
  - `vr=0`, `vp=0`, `cmp=0`.
  - Un bloque con T1..T8.
  - `pcdiff=0`.
  - `REJ ... exact tests path is not declared by path_policy` para las rutas exactas.
  - `oracle/contrast-key.md []` y `tests/test_010_003_documentary_pilot.py []` en contención.
  - La salida de pytest con `def test_prod():` y `'CLAVE-SECRETA'`.
