# Revisión focal — redo documental 019-002

**Resultado: un hallazgo bloqueante.** La restauración y el redo son verificables en los commits examinados, pero el producto conserva una contradicción material con PC-8 y R8. Esta revisión no aprueba la feature ni acredita su aceptación final.

## Hallazgo bloqueante

### La definición de «CDAD light» conserva la revisión opcional y el aislamiento parcial

**Required · Verdict: BLOCKING · Bucket: h**

**Ubicación:** `CDAD_metodologia.md:114,2937`.  
**Contrato y fuente:** `docs/specs/019-002-effective-discovery-instructions/spec.md:111–113`; diseño aceptado `docs/specs/019-001-discovery-dialogue-contract/operating-design/lightweight-paths.md:37–49`, `activation-map.md:80–85` y `acceptance-record.md:7–12`.

La fila corregida de la matriz (`:114`) dice que una feature del ciclo normal conserva la revisión del borrador —o la exención registrada— y la separación de roles. Sin embargo, el glosario del mismo documento (`:2937`) sigue definiendo «CDAD light» como una variante con **revisión opcional** y sesiones aisladas solo para componentes críticos.

Un lector que consulte el glosario puede seguir eligiendo precisamente las excepciones que PC-8 ordena retirar para el ciclo normal. La referencia correcta en la matriz no elimina esa instrucción contradictoria en otra entrada de consulta ordinaria.

**Remedio estructural:** reconciliar la definición del glosario con la fila y con las referencias autoritativas, manteniendo «CDAD light» como etiqueta explicativa, no como tercer protocolo.

**Cierre verificable:** una revisión contextual del documento comprueba que sus definiciones y orientaciones sobre «CDAD light» ya no presentan la revisión ni la separación de roles como opcionales para el ciclo normal, y que distinguen el trabajo acotado fuera del ciclo.

## Redo, alcance y procedencia

- El `write_scope` del packet `implementer-review-fix-005` declara exactamente `README.md` y `CDAD_metodologia.md` (`REQUEST.json:31–39`) y prohíbe editar tests (`:41–43`).
- `baf2874f` restaura ambos archivos al contenido de `3322aaf3^`; `b38e3c26` vuelve a modificarlos. Cada commit contiene exclusivamente esos dos archivos.
- El resultado de `b38e3c26` es idéntico en esos archivos al de `3322aaf3`. La igualdad prueba contenido, **no** convierte en válida retroactivamente la modificación original.
- No observé cambios posteriores en esos dos archivos hasta `42ec1344`. La comprobación de commits no demuestra la ausencia de escrituras transitorias fuera de alcance.
- El packet del implementador ya no era el packet activo al intentar revalidarlo en esta sesión: el validador devolvió `active_packet mismatch: id`. Por tanto, no presento esa comprobación actual como validación histórica de su dispatch.
- La contradicción entre la clasificación del encargo como contrato aprobado y las etiquetas y procedencia de aprobación pendientes permanece sin resolver. No se cambió el hash ni se declara la aprobación subsanada.

## Categorías de evidencia

| Compromiso examinado | Categoría | Alcance |
|---|---|---|
| PC-8 / R8, en las dos páginas revisadas | **Failed** | Persiste la contradicción del glosario. No se extrapola este resultado a todas las superficies de dominio. |
| Restauración y redo dentro de los archivos declarados | **Supported within declared limits** | Los commits y comparaciones sostienen el alcance y los contenidos persistidos; no prueban ausencia de escrituras transitorias. |
| PC-4 y PC-11, rutas observadas | **Missing** | El encargo indica expresamente que no se acrediten como observadas. Siguen pendientes de ejecuciones y registros recuperables. |
| Resto de las promesas de la feature | **Unable to verify** | Esta fue una revisión focal del redo documental, no una nueva revisión integral ni aceptación de la feature. |

## Comprobaciones y evidencia

- Intake de esta revisión: `validate-request` y `validate-packet` terminaron con `rc=0`; `render | cmp` produjo `cmp_exit=0`. La identificación Route C coincidió con el render y el contexto es v2.
- `git diff --quiet 3322aaf3^ baf2874f -- README.md CDAD_metodologia.md` → `baseline_restored_exit=0`.
- `git diff --quiet 3322aaf3 b38e3c26 -- README.md CDAD_metodologia.md` → `original_bytes_repeated_exit=0`.
- `git diff --quiet b38e3c26 HEAD -- README.md CDAD_metodologia.md` → `unchanged_since_redo_exit=0`.
- `git diff --check 3322aaf3^..b38e3c26 -- README.md CDAD_metodologia.md` → `diff_check_exit=0`.
- `sha256sum docs/specs/019-002-effective-discovery-instructions/spec.md` → `5cca6fa6d0cde92cadab961c8218126a741432b575bc169df24c7901eef34eb0`.
- Examiné primero las referencias de tests pertinentes: no encontré un test que establezca la coherencia semántica de estas dos páginas. El reporte del redo declara que no ejecutó tests; no sustituí esa declaración por una corrida propia. La revisión contextual detectó el defecto anterior.
- La comparación de la tabla de decisiones con `docs/adr/` encontró **32 rutas indexadas, ninguna ausente**; los ADR no indexados examinados figuran como propuestos.
- **Suite completa:** no realizada; revisión focal documental, no cierre de feature ni de epic.
- **Archivos modificados por esta revisión:** ninguno. **Commit:** ninguno. `docs/.cdad-state.json` ya aparecía modificado en el árbol de trabajo.

## Abstentions

- No puedo acreditar la validez histórica del dispatch del implementador con la validación actual bloqueada por el cambio de packet activo, ni verificar ausencia de escrituras transitorias.
- No acredito la aprobación de la especificación, la activación instalada, las rutas observadas PC-4/PC-11 ni la aceptación final.
- No verifiqué la familia de modelo del implementador; el bucket no incorpora ese punto.