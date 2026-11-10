# review-T2-004 — Revisión focal de T2

**Revisión examinada:** `d28b62ac95eb2f5644b8c5bc868da47dcb74083d`  
**Dictamen:** el bloqueante de `review-T2-003` **cierra**. Con el alcance focal de esta revisión, **T2 pasa el gate**; la decisión corresponde al usuario u orquestador.

## Hallazgos

No encontré hallazgos bloqueantes ni opcionales dentro del alcance encargado.

## Evidencia del cierre

- `operation-scope.json:554-560` describe C-P-cold como copia *slim* sin `.cdad`, `build`, `.git` ni cachés, y C-P-present como una ruta sin copia de `product_root`. El verificador primero prepara una fuente descartable con esos filtros y, para C-P-present, repone el manifiesto; después `product_root` utiliza la rama de manifiesto existente sin copiar (`tests/test_017_001_suite_operations.py:792-824`, `tests/product_staging.py:88-100`).
- La regla del registro y `calibration.md:102` distinguen C-U1/C-U4, cuyos filtros no excluyen `.cdad`, de C-U3/C-D, que utilizan la copia U3 y sí la excluyen. C-D llama a `disposable_product()` (`tests/test_010_002_documentary_role_integration.py:1170-1180`).
- Ambos documentos mantienen desconocido el tiempo aislado de `.cdad`: no lo infieren del volumen y requieren medición adicional si una decisión de exclusión depende de ese costo.
- El diff de `d28b62ac` modifica solamente la regla documental y la atribución de volumen. No altera las ocho selecciones, sus conteos registrados ni la declaración de C-W como no requerida.

## Verificación independiente

| Comando | Resultado |
|---|---|
| `python3 -m json.tool docs/specs/017-001-suite-performance/performance/operation-scope.json >/dev/null` | rc 0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 scripts/cdad-suite.py validate` | rc 0; `status: ok`, 2022 nodeids |
| `git diff d28b62ac^ d28b62ac --stat` | Solo `calibration.md` y `operation-scope.json` |
| `git rev-parse HEAD` | `d28b62ac95eb2f5644b8c5bc868da47dcb74083d` |

No ejecuté de nuevo las ocho selecciones ni la suite completa. No modifiqué archivos ni generé commits; `docs/.cdad-state.json` ya aparecía modificado al iniciar la revisión.

## Abstentions

- No contrasté los perfiles crudos externos al repositorio ni los manifiestos de volumen; por tanto, no acredito independientemente la cifra de archivos o bytes de `.cdad`.
- Esta revisión no reabre la auditoría exhaustiva de la instrumentación ni la conciliación completa de ADR: su alcance es el cierre del bloqueante identificado.
