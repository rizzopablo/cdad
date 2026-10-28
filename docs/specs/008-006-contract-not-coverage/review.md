# Revisión de 008-006

## Hallazgos

### 1. Required — R4 tiene una segunda definición editable

**Verdict: BLOCKING · Bucket: h**

`sources/roles/reviewer.md:85-88` enumera las categorías de promoción excepcionales, aunque `sources/roles/orchestrator.md:274-280` es el hogar exclusivo de R4. La propia instrucción del reviewer dice «never restate it here» después de reproducirlas.

Esto incumple PC-5 y la regla de hogar único: si cambia el gate, el reviewer puede seguir aplicando categorías desactualizadas. **Cierre verificable:** sustituir la enumeración del reviewer por una referencia a R4, regenerar ambos runtimes y comprobar que solo el hogar del gate define las categorías.

### 2. Required — Stage 3 reproduce la regla de selección que dice no redefinir

**Verdict: BLOCKING · Bucket: h**

`skills/cdad-cycle/references/stage-3-tdd.md:17-19` vuelve a formular la selección por promesa, la trazabilidad, la declaración de consecuencia y la aclaración de que no es un techo. R2 tiene su hogar editable en `sources/roles/test-writer.md`, según la spec, líneas 95-107.

La duplicación crea dos textos editables que pueden divergir, precisamente en la interpretación de AJ2. **Cierre verificable:** mantener en stage 3 la aplicación y el enlace a R2, sin volver a definir sus obligaciones; conservar allí R7 como contrapeso propio y revisar los demás consumidores por el mismo patrón.

### 3. Required — El verificador acepta la ausencia de agentes generados

**Verdict: BLOCKING · Bucket: h**

`scripts/cdad-doctrine-check.py:275-306` solo comprueba los archivos encontrados por `glob("cdad-*.md")`; no exige que exista ningún agente ni que estén presentes todos los roles y variantes. Si se elimina un agente —o todos los archivos de uno de los dos directorios, dejando el directorio— esa comprobación no informa la ausencia y el programa puede declarar éxito.

Esto debilita la verificación ejecutable prevista en AJ4 para PC-6: no demuestra que ambos runtimes reciban la doctrina. **Cierre verificable:** exigir el conjunto esperado de artefactos por runtime y demostrar, con una comprobación focal aislada, que eliminar cualquiera produce salida no cero.

### 4. Optional/Consider — El mensaje de éxito excede lo que comprueban los marcadores

**Verdict: OPTIONAL · Bucket: m**

`scripts/cdad-doctrine-check.py:57-106,176-201,239-270,300-304` comprueba fragmentos textuales, no todas las obligaciones ni la equivalencia de los agentes con sus fuentes. Por ejemplo, contar un bloque `plan-tasks` no valida su contenido; detectar un marcador en un agente no prueba que esté actualizado. Sin embargo, las líneas 335-348 presentan el resultado como «the doctrine is not intact» / «OK».

El encabezado sí limita el alcance al juicio sobre consecuencias, pero debería distinguir también **presencia de marcadores** de integridad completa. **Cierre verificable:** ajustar diagnóstico y documentación al alcance real y mantener como verificaciones separadas la composición y el schema.

## Evidencia de verificación

- Contrato: SHA-256 calculado `6f288cb6194f913f245a89c34e20f44eda977054abcb3365f04c7963cfac94b3`, coincide con el paquete.
- Commit revisado: `1e2811d`, 36 archivos. No modifiqué archivos. Ya existía una modificación en `docs/.cdad-state.json`.
- `python3 scripts/cdad-doctrine-check.py` → `OK — 7 homes, 83 files scanned, 22 generated agents`.
- `python3 -m unittest discover -s tests -p 'test_cdad_generate.py' -q` → 10 tests, **OK**.
- `python3 -m unittest discover -s tests -p 'test_005_007_t2_progressive_plan_validator.py' -q` → 6 tests, **OK**.
- `git diff 1e2811d^ 1e2811d -- skills/cdad-cycle/assets/feature-plan-template.md` muestra adiciones fuera del bloque `plan-tasks`; la regresión focal anterior pasó.
- No ejecuté la suite completa: el paquete la reserva para el cierre.

## Abstentions

- No verifiqué mediante regeneración comparativa que **cada byte** de los agentes distribuidos coincida con una generación nueva desde las fuentes; los tests focales de generación pasaron, pero los marcadores del verificador no prueban esa equivalencia.
- No verifiqué las disposiciones de instalación sobre un agente local modificado con `model:` en un destino real; el contrato excluye instalar agentes en destinos reales.
