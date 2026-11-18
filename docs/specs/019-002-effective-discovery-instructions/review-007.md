# Revisión focal — corrección de «CDAD light»

**Resultado:** no encontré hallazgos bloqueantes en la corrección examinada. El bloqueo de `review-006` queda resuelto **en las dos páginas revisadas**, con los límites indicados abajo. Esto no constituye aprobación ni aceptación final de la feature.

## Resultado de la revisión

El glosario ya no presenta la revisión como opcional ni limita el aislamiento a componentes críticos. Para una feature del ciclo normal conserva la revisión del borrador —o la exención registrada del dueño—, la aprobación y la separación de roles. También distingue el trabajo acotado fuera del ciclo (`CDAD_metodologia.md:2937`).

Contrasté esa definición con la matriz (`:114`), las demás apariciones pertinentes del documento (`:195`, `:2832`, `:2955`), el consejo para trabajo acotado en `README.md:21–25`, PC-8 (`spec.md:111–113`) y las fuentes de R8 (`operating-design/lightweight-paths.md` y `activation-map.md`). No encontré una orientación que siga autorizando, para el ciclo normal, revisión opcional o aislamiento parcial. La fila de la matriz apunta a las referencias autoritativas.

No hay hallazgos adicionales que reportar en esta revisión focal.

## Categorías de evidencia

| Compromiso examinado | Categoría | Alcance |
|---|---|---|
| Bloqueo de `review-006`, PC-8/R8 en `CDAD_metodologia.md` y `README.md` | **Supported within declared limits** | Revisión semántica de las dos páginas, no de todos los consumidores de la feature. |
| Alcance persistido de `89038416` | **Supported within declared limits** | El commit modifica únicamente `CDAD_metodologia.md`; no contiene cambios en tests. No prueba ausencia de escrituras transitorias. |
| Observaciones PC-4 y PC-11 | **Missing** | Siguen pendientes las ejecuciones y registros recuperables requeridos; esta revisión no los acredita. |
| Aprobación y procedencia del contrato | **Contradictory / unresolved** | Se conserva la discrepancia previamente registrada entre la clasificación del encargo y la procedencia de aprobación pendiente. No se declara subsanada. |
| Resto de las promesas de la feature | **Unable to verify** | Fuera del alcance de esta revisión focal. |

## Evidencia y comprobaciones

- **Intake Route C:** `validate-request` y `validate-packet` devolvieron `0`; `render | cmp - PACKET.md` devolvió `canonical_cmp=0`. La identificación recibida coincide con `render --route C`; el contexto de ejecución es v2.
- **Contrato:** `sha256sum docs/specs/019-002-effective-discovery-instructions/spec.md` devolvió `5cca6fa6d0cde92cadab961c8218126a741432b575bc169df24c7901eef34eb0`.
- **Cambio:** `git show --format= --name-only 89038416` mostró solo `CDAD_metodologia.md`. `git diff --check 89038416^ 89038416` devolvió `0`.
- **Estado de las páginas:** `git diff --quiet 89038416 HEAD -- README.md CDAD_metodologia.md` devolvió `0`: sus contenidos no cambiaron después del commit revisado.
- **Tests:** examiné primero las referencias pertinentes. El reporte del implementador declara que no ejecutó tests; no ejecuté una suite para esta corrección documental semántica. La revisión contextual es la evidencia para el texto, no una prueba de ejecución de la feature.
- **Decisiones vigentes:** la comparación con `docs/adr/` encontró 32 rutas indexadas y ninguna ausente. Los ADR no indexados se presentan como propuestos; no identifiqué una contradicción del cambio con las decisiones aplicables al reviewer.
- **Suite completa:** no realizada; esta no es una revisión de cierre de feature ni de epic.
- **Archivos modificados por esta revisión:** ninguno. **Commit de esta revisión:** ninguno. `docs/.cdad-state.json` ya aparecía modificado en el árbol de trabajo.

## Abstentions

- No acredito la aprobación de la especificación ni la validez histórica de los despachos anteriores.
- No acredito la activación instalada, las observaciones PC-4/PC-11 ni la aceptación final de la feature.
- Los commits examinados no permiten demostrar que no existieron escrituras transitorias fuera de alcance.