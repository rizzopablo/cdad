# Revisión final — 017-001

**Resultado: no puedo recomendar todavía la aceptación al dueño.** La revisión quedó incompleta: no identifico un defecto del producto con confianza suficiente para declararlo bloqueante, pero tampoco tengo evidencia revisada suficiente para acreditar las postcondiciones y la conservación de tests exigidas por el encargo.

## Comprobaciones realizadas

- **Entrada a Review:** `python3 scripts/cdad-suite.py validate` devolvió `status: ok` y **2055 nodeids**. El resultado también informa tres entradas `placeholder_targets` y una medición temporal `pending`; no las interpreté como fallos sin contrastar sus contratos.
- **Resultados crudos:** conté los casos en los XML. Tanto la corrida serial como los dos workers paralelos suman **2055 casos: 2050 passed y 5 skipped**. La comparación de pares `(classname, name)` de los XML no mostró identidades exclusivas ni diferencias de resultado. Esto no sustituye la comprobación de correspondencia XML–nodeid exigida por la spec.
- **Revisión de las corridas:** `attempt.json` y `parallel.json` registran el mismo commit, `83674246098c19a94fc6887506c056ad0d5124d1`, y `dirty: 0`. El HEAD revisado es `1eb8a65d02ae30500f0a52b68cfc6f6b4ff15841`; entre ambos hay un commit documental de resultados.
- **Reducción:** con los valores publicados, `(4235 − 2925.336183793843) / 4235` da **30,9248 %**. El contrato de T7 define para el paralelo la ventana de ejecución, excluyendo el barrido de canario, y reporta aparte la pared total del comando. La comparación debe interpretarse con esa diferencia de fronteras.
- Los archivos de canario de configuración anterior y posterior son idénticos en ambas corridas. El JSON paralelo registra **20 procesos transitorios encontrados y cero restantes**; no verifiqué independientemente la cobertura del mecanismo.
- La identificación **Route C** coincidió con el render; `validate-request` y `validate-packet` terminaron sin error.

## Hallazgos

No presento hallazgos de producto con ≥80 % de confianza a partir de las comprobaciones realizadas. **La ausencia de hallazgos no equivale a una revisión completa ni a una aprobación.**

## Abstentions

- No completé el contraste **PC-1 a PC-12**, el plan aprobado ni la comprobación independiente de la autoridad y secuencia de la decisión PC-4.
- No completé la auditoría anti-gaming archivo por archivo de las adaptaciones a tests preexistentes. Revisé los cambios visibles en `_RecoveryProject` y `_Project`: agregan intervalos alrededor de la construcción y preparación y conservan las aserciones mostradas; esto no acredita el resto del diff.
- No recalculé íntegramente la conciliación, la preparación duplicada, la correspondencia nodeid–XML ni las condiciones y hashes de todos los artefactos crudos.
- No verifiqué las correcciones de los nueve bloqueantes anteriores de T6, ni los invariantes sobre producto instalable, separación de roles y trabajo inline del orquestador.
- No ejecuté focales ni suite completa. Quedan como límites declarados la **carga externa del host**, la dependencia de **Linux** para la gestión de familia de procesos y el **resto de tiempo no desglosado**.

No modifiqué archivos ni hice commits. La revisión debe completarse antes de que el dueño decida la aceptación.
