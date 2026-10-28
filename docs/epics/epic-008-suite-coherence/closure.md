# Cierre — Epic 008 «Coherencia y sostenibilidad de la suite»

Fecha: 2026-10-28. Features: **6/6 cerradas**, cada una con su `closure.md`. El plan declaraba cinco;
`008-006-contract-not-coverage` se agregó el 2026-10-27 por decisión del dueño y se ejecutó después de
`008-002` y antes de `003/004/005`, para que rigiera en las tres unidades restantes.

## Resultado

El epic no agregó capacidad al producto: **devolvió a la suite la condición de gate** y puso **una sola
decisión donde había varias**. Lo que el epic 007 dejó como sospecha —tests verdes en aislamiento y rojos en
corridas grandes— quedó medido, aislado y corregido; y lo que dejó como práctica —despachos de rol sin
paquete— pasó a ser una frontera que rechaza antes de producir efectos.

El criterio que el epic se puso y que `008-004` no pudo cumplir —«Suite estable»— se verifica con **tres
corridas consecutivas del gate real sobre el mismo commit y árbol limpio**: **1827 passed, 5 skipped,
`verdict green`, `attributable true`, canario 0**, con el host cargado (`loadavg` 5.26–6.43) — el mismo
escenario que en `008-004` produjo siete falsos rojos.

## Features entregadas

| # | Feature | Resultado consumible | Cierre |
|---|---|---|---|
| 1 | `008-001-home-xdg-isolation` | Cada test corre con HOME, XDG y temporales propios; el producto resuelve el origen de agentes con el HOME vigente; la cota de despacho tiene dueño | `docs/specs/008-001-home-xdg-isolation/closure.md` |
| 2 | `008-002-suite-by-capability` | Selector canónico por capacidad (`scripts/cdad-suite.py`), inventario de **210 módulos**, mapa de **29 obligaciones** y `close` que reserva un intento exclusivo y conserva su evidencia | `docs/specs/008-002-suite-by-capability/closure.md` |
| 3 | `008-003-lifecycle-decision-model` | Identidad, autoridad, replay y conflicto en un núcleo compartido (`cdad_lifecycle.py`); **15 ramas decisorias locales** retiradas | `docs/specs/008-003-lifecycle-decision-model/closure.md` |
| 4 | `008-004-role-packet-enforcement` | Una encomienda no se admite ni se acredita sin paquete verificado: **5 fronteras invocables** comparan el paquete completo contra el render canónico antes de efectos; el intake identifica el marcador **una vez en cualquier posición** | `docs/specs/008-004-role-packet-enforcement/closure.md` |
| 5 | `008-005-ci-gate` | `scripts/cdad-ci-gate.py` + `docs/ci-gate.md`: 5 pasos en orden fijo, **una sola corrida de pytest**, verde **atribuible** o salida distinta de cero que nombra la causa | `docs/specs/008-005-ci-gate/closure.md` |
| 6 | `008-006-contract-not-coverage` | Doctrina «test por contrato, no por cobertura» en **7 hogares** editables y los **22 agentes** generados, con verificador ejecutable que falla cerrado | `docs/specs/008-006-contract-not-coverage/closure.md` |

## Gate del epic — tres corridas consecutivas

`python3 scripts/cdad-ci-gate.py --base HEAD~1`, sobre `443a43d` (base `0dd044f`), árbol limpio en las tres.

| Corrida | Raíz de evidencia | Resultado | Veredicto |
|---|---|---|---|
| 1 | `.cdad/local/008-005/epic-runs/gate-20261028T094851568108Z-2703548-ff3e9885/` | **1827 passed, 5 skipped, 0 failed, 0 errors** | `green`, `attributable: true` |
| 2 | `.cdad/local/008-005/epic-runs/gate-20261028T103800000601Z-3242412-e1ea0883/` | **1827 passed, 5 skipped, 0 failed, 0 errors** | `green`, `attributable: true` |
| 3 | `.cdad/local/008-005/epic-runs/gate-20261028T112759810567Z-3781147-9d15c9ef/` | **1827 passed, 5 skipped, 0 failed, 0 errors** | `green`, `attributable: true` |

En las tres: `dirty 0`, canario `delta_lines 0`, `pytest_summary.verified: true` y `loadavg` 5.26 / 5.60 /
6.31 (1 min). Los 5 skips son los opt-in reales, con su motivo completo en `gate.json` (el `COLUMNS` fijado
en el hijo de `run_pytest_to_logs` es lo que los completa).

**Límite declarado de esta secuencia.** El commit es el cierre documental de `008-005` (cambio
sólo-documentación, 2 rutas), así que en las tres corridas el paso de **superficie** se declaró *no aplica*
(`D9`/`PC-4`) y la suite corrió igual. La secuencia acredita **estabilidad de la suite y atribución del
verde**, no la clasificación por superficie sobre un cambio de producto: eso lo acreditan los tests del
gate (PC-4) y `python3 scripts/cdad-suite.py surface --base 84631f3 --collect-only` (rc 0 con selección
real de nodeids). Tres corridas verdes son evidencia **acotada** de estabilidad, no prueba de ausencia
universal de flakiness.

**Certificación del commit de cierre.** Sobre `0cda2d8` (los tres commits posteriores a la secuencia son
sólo documentación: 7 rutas, todas `documentation`), con `--base 443a43d`: **`verdict green`,
`attributable: true`, `dirty 0`, `1827 passed, 5 skipped`, canario 0, `loadavg` 6.53** —
`.cdad/local/008-005/epic-runs/gate-20261028T123027017263Z-144767-3c1ffcdd/`. `make validate` **68/68** y
`./install.sh --check` **PASS (414 grupos)** tras re-desplegar los 4 agentes `test-writer` regenerados en
008-005.

## Criterios de aceptación

| Criterio del plan | Estado | Verificación / límite |
|---|---|---|
| Las features cerradas, cada una con su `closure.md` | **Cumplido** | **6/6**; el plan decía 5 y `008-006` se agregó por decisión del dueño. |
| **Suite estable** | **Cumplido, con alcance declarado** | Tres corridas consecutivas del gate real sobre el mismo commit y árbol limpio: 1827 passed / 5 skipped, `green` + `attributable`, `dirty 0`, canario 0, `loadavg` 5.26–6.43. Límite: la secuencia no ejerce el paso de superficie y la clase «esperó por encima de la cota» perdió su test (F1). |
| **Suite coherente** | **Cumplido en coherencia y trazabilidad; la reducción literal no se cumple y se declara sustituida** | Selector canónico, inventario de 210 módulos, mapa de 29 obligaciones y `close` con evidencia preservada. La medición del piloto dio **+3.317 bytes / +81 LF** y se publica tal como salió: la directiva **AJ6** del dueño sustituyó «test por cobertura» por «test por contrato». No se presenta una reducción que no hubo. |
| **Un solo decisor** | **Cumplido, con deudas declaradas** | `cdad_lifecycle.py` (408 líneas, sin I/O, sin reloj) y 15 ramas locales retiradas. `SUSP-IDENTITY` cerrada **condicionada**; `SUSP-GUARD` **parcial**; `SUSP-LOCK` y `SUSP-APPROVAL` **no cierran**. |
| **Paquete obligatorio** | **Cumplido, con el límite de admisión** | 5 fronteras + intake de roles; 25 tests que discriminan contra el código previo. Límite: **admite, no intercepta**. |
| **Test por contrato** | **Cumplido, con el límite de la verificación** | 7 hogares + 22 agentes + verificador que falla cerrado. Límite: acredita presencia de marcadores, no integridad semántica. |
| **CI verde en cada push** | **Cumplido a nivel mecanismo; activación pendiente del dueño** | El gate existe, corre los 5 pasos, no publica, no usa red ni credenciales y falla cerrado. **No hay workflow versionado**: `.github/**` y `Makefile` son `unclassified`; exige enmienda de política. |
| Sin mecanismos duplicados nuevos | **Cumplido, con dos excepciones declaradas** | El gate **invoca**; la admisión reutiliza el verificador del productor (ADR-036); `close` es el mecanismo único de cierre. Excepciones: la tabla `termination/delivery` (008-003) y `resume_unit` con ramas locales de vigencia. |

## Retrospectiva

**Funcionó.**

- **Un gate que no miente.** La atribución fail-closed convirtió «verde» en un hecho verificable —commit,
  árbol, intento, resumen, rc— y permitió declarar el caso incómodo: en `008-004` la corrida verde era
  **anterior** a PC-08, así que el commit final no tuvo corrida verde.
- **Cerrar preservando la evidencia.** El `close` de `008-002` —intento exclusivo, `attempt.json` atómico,
  logs, canario con alcance— hizo posible la secuencia de tres corridas.
- **Reviews que reproducen.** Los defectos que importaron se reprodujeron, no se leyeron: `PYTEST_ADDOPTS`
  produciendo «cero aprobados con rc 0»; un encabezado válido con objetivo alterado que pasaba el intake; y
  `cdad_delegate` lanzando un worker con el paquete alterado tras un `begin` válido.
- **Declarar la pérdida en vez de cubrirla.** En `008-005` la clase «acotada por encima de la cota» dejó de
  ser observable al re-anclar los techos; se declaró (F1) y se corrigieron los textos.
- **Una casa y sus copias.** El intake y la doctrina se corrigieron en la fuente y se regeneraron las copias
  (22 agentes), con verificador que falla cerrado.

**No funcionó.**

- **Las cotas de reloj de pared se descubrieron un epic tarde.** El costo: un commit de producto
  (`d7cbb1f`) sin corrida verde y una unidad que no pudo declarar su gate.
- **La doctrina y el método crecieron más rápido que su mecanismo.** La exigencia de paquete existía en
  prosa desde el epic 007 y recién en `008-004` tuvo frontera que la hiciera cumplir.

**Incidentes operativos (declarados).**

1. **El preámbulo del runtime rompió el intake de «primera línea»** hasta `008-004`; la corrección fue que la
   identidad la diera el marcador canónico en cualquier posición.
2. **Tres transcripciones manuales erróneas de paquetes** (dos documentadas en los cierres de 008-002/008-004
   y una en el GREEN de 008-005); el digest canónico las detectó. Regla: **despachar los bytes del archivo,
   nunca re-tipearlos**.
3. **Contratos enmendados después del `begin`**: el `record` se niega. Cuatro rechazos por P1 en `008-004`
   (más uno por `state incoherent`) y uno en `008-005`. Regla: **registrar antes de enmendar**.
4. **Split-brain de continuidad**: dos `begin` del mismo intento y un archivo de actualización mal nombrado
   dejaron dos cabezas divergentes; el CLI no elige ganador por diseño. Reparado a mano, con respaldo en
   `.cdad/executions/exec-008-005-ci-gate-001/continuity/head.json.split-brain-20261028.bak`.

## Deuda que se lleva

| Deuda | Origen | Disposición |
|---|---|---|
| **Cotas de reloj de pared — F1:** la clase «acotada por encima de la cota» no es observable | `008-005` (review F1) | `deferred-hardening`; restituirla exige un observable de duración en el producto |
| `SUSP-LOCK`, `SUSP-APPROVAL` abiertas; `SUSP-GUARD` parcial; `SUSP-IDENTITY` condicionada | `008-003` | Se arrastran con su límite declarado |
| **`HOME-LEAK-DERIVED-AGENTS`:** 6 líneas de delta en el HOME real durante el gate | `008-006` | Deuda media: reproducir el write y aislarlo |
| **CI no activado:** workflow no versionado; `make validate` fuera del gate | `008-005` | Exige **enmienda de política del dueño** |
| Fuzzing del parser, combinatoria de transportes, matriz de runtimes, interceptación nativa | `008-004` | `deferred-hardening`; ninguno permite diferir un PC comprometido |
| F011 (`make validate`) | heredada | **Ya no bloquea**: era el drift de los agentes instalados y pasa **68/68** tras el deploy del 2026-10-28 |

**`deferred-hardening` consolidado (R6).** Se arrastra con su motivo y su dueño; ninguno permite diferir una
promesa comprometida: 008-002 (variantes de PC-5, `measure` como contrato, etiquetas `[ghost]`, preservación
semántica fuera del piloto, atomicidad de `close`); 008-003 (estrés concurrente, manipulación de múltiples
archivos, combinatoria sin consecuencia, benchmarks); 008-004 (fuzzing, combinatoria de transportes,
carga/rendimiento, matriz de runtimes, interceptación nativa); 008-005 (F1, reloj inyectable, tope de la
suite, `make validate` dentro del gate, superficie en vez de suite, enmienda de política); 008-006 (rechazo
operativo de informes sin la declaración, juicio automatizado de la consecuencia, doctrina como tests, QA
intensivo).

## Cierre

El epic cierra **6/6** y **no implica publicar**: el push sigue reservado al dueño. Lo que queda abierto no
es una feature del plan, sino tres decisiones suyas: la enmienda de política que activa CI en el push, la
prioridad de la deuda de arriba y la publicación.
