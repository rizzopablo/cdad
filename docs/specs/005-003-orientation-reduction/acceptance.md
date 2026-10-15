# Aceptación de T5 — 005-003-orientation-reduction

Fecha: 2026-10-12. **Artefacto del orquestador** (la ficha de T5 asigna la medición al orquestador;
el architect solo lee). Verifica el **gate de aceptación** de la feature y **observa** (no garantiza)
lo que la fila 8 enmendada y los criterios A1-A11 piden.

> **Estado: PARCIAL, con un bloqueo declarado.** La parte de unidad está satisfecha y verificada. La
> **aceptación con una sesión real nueva** (A1/A2/A6 y la observación de A8/A9) **requiere desplegar la
> versión nueva**, acción **reservada al dueño** y **prohibida en este tramo**: se declara como
> **BLOQUEO**, no como fallo ni como éxito.

## 1. Precondiciones del gate (INV-8): D11 y R4 cerrados

| Precondición | Estado | Evidencia |
|---|---|---|
| **D11** (chequeo de no-escritura de la integración real, inestable con la base viva) | **CERRADA en T3** | Condición causal aplicada en sus cuatro partes: (1) ausencia de escrituras sobre **base temporal controlada** y (2) **concurrencia con otro escritor activo** viven en el focal `tests/test_005_003_t3_set_summary.py` (`test_d11_1_*`, `test_d11_2_*`); (3) la aserción de `(tamaño, mtime)` de la base **viva** se retiró de `tests/test_005_002_t4_acceptance.py` (commit `8b5673d`), que ahora afirma **solo la lectura y los resultados**; (4) la regla «la base real **nunca** se escribe, ni para demostrarlo» está declarada en `context-meter.md:326`. Focal: **9 passed** (corrida propia del orquestador). |
| **R4** (documento multiplexado) | **CERRADA en T3** | `skills/cdad-cycle/references/context-meter.md:306-318` declara los **dos elementos**: el total del conjunto es **≤ N × el límite por sesión** y el límite normativo es **por documento de sesión**. Focal: verde. |
| Medición con el **artefacto del repo** en solo lectura | **Disponible** | El medidor del repo corre read-only sobre la base de sesiones; la versión instalada **no** lo contiene (sigue siendo *ausencia*, no incoherencia: la vista `status` devuelve `version.verdict = UNKNOWN` con causa). |

## 2. Uso real observado en este tramo (evidencia propia)

**La vista compacta (T1) en el proyecto real** — `python3 skills/cdad-cycle/scripts/cdad_packet.py status --project-root <ABS>`:

| Observado | Valor |
|---|---|
| Documento emitido | **1.679 B** (límite normativo: 16.384 B; margen ~10×) |
| Claves emitidas | `authority`, `entry`, `epic`, `execution`, `feature`, `next`, `packet`, `project`, `unknowns`, `version` — exactamente el conjunto declarado, sin `stage_history` |
| `entry` | `continuity-reconcile` (con paquete `completed` y ejecución activa: coherente con el mapa de §2.2) |
| `version` | `UNKNOWN` con causa explícita («any non-zero rc reads as not verified») — **ausencia**, no `DRIFT` |
| Read-only | el estado quedó intacto (INV-1; verificado por los focales y por la invariante de la vista) |

**Contraste con la línea base medida**: la lectura del estado completo en el caso S-BOOT-04 fue de
**215.292 caracteres** (4 fragmentos, líneas 1-2068); la proyección medida acá es de **1.679 B** —
dos órdenes de magnitud, sin emitir el historial.

## 3. Observación de la reorientación de cada rol (A8 — proxy declarado, NO garantía)

Medición read-only con el medidor del repo sobre las **12 sesiones de rol** de este tramo
(6 del test-writer, 6 del implementer; documento de la corrida: 96.552 B, media 8.046 B por sesión).
El proxy es de **tramo completo** (`session_reads`, `total_output`, `tool_calls`) y **no** un corte
pre-acción: en toda sesión de rol `previous_*` y `time_to_first_*` salen `unknown` con causa.

| Rol | Sesiones | Llamadas | Salida total (car.) | Lecturas de la sesión |
|---|---:|---:|---:|---:|
| `cdad-implementer` | 6 | 246 | 1.532.782 | 19 · 5 · 9 · 7 · 19 · 13 |
| `cdad-test-writer` | 6 | 150 | 1.454.923 | 18 · 7 · 11 · 2 · 8 · 6 |

**Pregunta de aceptación (A5/A8), respondida con lo observado y no con un umbral:** los 12 encargos se
**empezaron y completaron** (11 con commit del rol; el restante bloqueó legítimamente y se completó en
un re-despacho que commiteó — §5), **sin trasladarle trabajo al rol** (cada paquete llevó su tarea, su
contrato aplicable y sus comandos de validación) y **sin quitarle información necesaria** (el RED de
cada unidad se escribió desde el contrato aprobado, y el GREEN desde el oráculo). **No** se afirma
«sin aumento» de lecturas: se **observa y se registra**. La extensión del medidor con un hito de
«primera acción del encargo» sigue siendo **PROPUESTA** al dueño, no asumida.

## 4. Metas numéricas: orientación, no demostración automática (A6)

Las bandas (llamadas ≈45-55 antes del primer despacho; salida ≈120-180 KB; `time_to_first_dispatch`
≤ la banda de C; entre despachos con reducción y criterio declarado) son **orientación derivada** de la
línea base medida, declarada como **derivada y no medida**. **No** son umbrales que acepten o rechacen
por sí solos, y **no** se aplican aquí: la comparación like-for-like corresponde a la **próxima sesión
real**, que está bloqueada (§7).

## 5. Commit por rol (A2-d y la fila 8 enmendada)

| Unidad | Rol | Commit del rol |
|---|---|---|
| T1 RED / GREEN | test-writer / implementer | `2bdf314b` / `2bc159a3` |
| T2 RED / testfix / GREEN | test-writer / test-writer / implementer | `350aa58` / `5e628de2` / `1810370` |
| T3 RED / GREEN | test-writer / implementer | `8b5673d` / `48d47f7` |
| T4 RED / GREEN | test-writer / implementer | `afd7fd4` / `b6e567b` |
| T6 RED / GREEN | test-writer / implementer | `d805876` / `d45e627` |

**11 de 12 sesiones de rol commitearon su producto.** La única excepción es el **GREEN de T2 en su
primer intento** (`sha256:1934e5517e6087c4…` — referencia **hasheada** de la sesión, §2.9): **bloqueó legítimamente** por un oráculo
mutuamente insatisfacible, **paró sin tocar tests ni commitear** (como manda el encargo) y dejó su
trabajo en el árbol; el orquestador resolvió el bloqueo con un **testfix firmado** por el test-writer
(`5e628de2`) y **re-despachó** el GREEN, que completó y commiteó (`1810370`). **Dato de aceptación: el
único rol que no commiteó lo hizo por un bloqueo declarado, no por omisión** — y quedó registrado.

## 6. Ejecuciones redundantes y evidencia equivalente (A10 — por justificación, sin «0» rígido)

| Corrida | Motivo |
|---|---|
| Focal de cada unidad, por el orquestador | **Verificación en dos niveles**: procedencia, diff, alcance y focales (segundos) en cada gate |
| Regresión del área (selector) en T1 GREEN, T2 RED y T6 GREEN | **Motivo concreto**: el cambio toca el CLI de paquetes / los assets de paquete, que consumen muchos tests |
| Regresión del área **citada** del rol en T2 GREEN, T3 GREEN y T6 GREEN | **Evidencia equivalente con procedencia verificada**: mismo árbol, mismo commit, baseline declarado por el rol; el orquestador verificó por sí mismo los focales y las regresiones críticas de cada unidad |
| **Suite completa** | **NO corrida todavía**: se corre **una sola vez** al cierre, en un worktree fijado al commit de cierre |

## 7. Bloqueo declarado: la aceptación con una sesión real nueva

Los criterios **A1** (una sesión nueva en reposo llega al primer despacho legítimo sin leer toda la
historia ni reconstruir el CLI, **sin que nadie le explique el recorrido**), **A2** (reanudación que
preserva autoridad y devuelve bloqueo ante ausencia/incoherencia), **A6** (señal ≠ aceptación) y la
observación de **A9** (tiempo del orquestador entre despachos) exigen **una sesión real nueva con la
versión nueva cargada**. Eso requiere **desplegar** la versión, acción **reservada al dueño** y
**prohibida** en este tramo.

**No se simula ni se declara satisfecho por proximidad.** Lo que sí se aporta: la evidencia de uso real
de §2 (la vista `status` sobre el proyecto real), la observación de §3 y el cumplimiento del gate de
§1. La aceptación de uso real queda **pendiente del despliegue**, con estos elementos ya listos para
observarse:

1. si la **primera acción de orientación** de la sesión nueva fue la vista `status`;
2. las **ampliaciones** realizadas y su **motivo** (bloqueo o duda concreta);
3. el **resultado** (primer despacho legítimo alcanzado, o bloqueo declarado);
4. las magnitudes del medidor con los mismos cuts (tiempo hasta el despacho, herramientas, volumen de
   salida y proxy de entrada cuando esté disponible), con lo ausente en `unknown` con causa.

## 8. Verificación de T5

- `python3 -m pytest tests/test_005_003_t3_set_summary.py -q` → **9 passed** (D11 y R4 cerrados).
- `python3 skills/cdad-cycle/scripts/cdad_packet.py status --project-root <ABS>` → **rc=0**, documento de **1.679 B** con las claves declaradas.
- Medidor del repo en solo lectura sobre 12 sesiones de rol → **rc=0**, documento de 96.552 B.
- **La suite completa se corre una sola vez, al cierre** (no en esta unidad).

## 9. Aceptación real con la versión desplegada (2026-10-13, orquestador Claude)

Sesión nueva del orquestador OpenCode con la instalación `0650655`, en este repo y en reposo. El
prompt fue mínimo («Continuá el epic. Detenete después de recibir y registrar el primer resultado
delegado») y no explicaba el recorrido. Lectura de solo lectura sobre la base de sesiones; el
id crudo está en `.cdad/local/accept-005-003.session`.

**Resultado de uso (A1, A2, A6).** Hubo un primer despacho legítimo sin ayuda:
- consultó `status`, eligió la siguiente unidad del plan (005-007), abrió la feature, preparó y
  validó el paquete;
- delegó con `cdad_delegate.py --destination opencode`, recibió, verificó por muestreo y registró
  (`7ce766b`, `8cbb23c`, `aef3c72`);
- declaró dos desviaciones: una fe de erratas de un registro manual retirado, y la brecha de
  materialización del informe de discovery.
- Duración total: 11,9 min.

**Medidas hasta el primer despacho** (cálculo propio sobre las partes `tool`; el medidor no detecta
este despacho, ver abajo):

| Medida | Línea base C (S-BOOT-04) | Esta sesión |
|---|---:|---:|
| Llamadas previas | 72 | 74 (55 shell, 5 read, 5 write, 4 edit, 2 glob, 2 skill, 1 execute) |
| Salida previa | 418.841 car. | 399.082 car. |
| Tiempo hasta el despacho | 8,29 min | 5,02 min |
| Lecturas del código del CLI | 21 llamadas, ≈70 KB | 0 |
| Consultas a `status` | — | 1 |
| Comandos sobre `docs/.cdad-state.json` | 4 fragmentos, 215 KB | 15; la mayor, una lectura de 55 KB |

**Lectura.** No es una comparación exacta: esta sesión abrió una feature nueva (escrituras del
state, ejecución nueva), y la línea base no lo hacía.
- **Mejoró:**
  - desapareció la reconstrucción del CLI desde su código;
  - el tiempo bajó un 39 %;
  - la entrada fue correcta sin explicación.
- **No mejoró:** las llamadas (74) y la salida (399 mil car.) quedan lejos de las bandas de
  orientación (45–55 y 120–180 KB).
- **Causa principal.** El orquestador consultó `status` y aun así leyó y editó el state completo
  para abrir la feature: 15 comandos sobre el state, el mayor de 55 KB. Abrir una feature exige hoy
  editar el state a mano.
- **Candidato de mejora:** una operación del CLI que abra la feature, o la siguiente unidad, sin
  leer ni reescribir el state entero.

**Brechas declaradas.**
1. El medidor no detecta el despacho por `cdad_delegate.py` (shell): lo declara como «no
   detectado por este lector», como manda D4. Conviene reconocer la invocación de la interfaz
   común de delegación como despacho.
2. `cdad_result.py` no materializa el informe de discovery del architect; el orquestador lo copió
   mecánicamente, con sha idéntico.

**Dictamen.** A1, A2 y A6 se cumplen en lo cualitativo: hubo un primer despacho legítimo sin
ayuda, se preservó la autoridad, y la aceptación usó una sesión real. Las metas numéricas, que son
orientación, no se alcanzan, y la causa medida apunta a cómo se abre una feature, no a la
orientación de lectura.
