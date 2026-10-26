# Discovery — 007-008-receipt-next-action (epic 007)

**Contrato:** plan aprobado proyectado en `UNIT-CONTRACT.md`; no existe aquí una spec aprobada de esta feature.

## Superficie y decisión pendiente

- **Origen del arrastre:** `skills/cdad-cycle/scripts/cdad_continuity.py:1414-1447` construye `_closing_body`: copia literalmente `head_body.next_action` (1434), aunque añade decisión de recepción mecánica y `receipt_checkpoint`. El contrato 007-003 exige conservar objetivo, decisiones, incertidumbres, presupuesto y evidencia, **no** la acción previa (`docs/specs/007-003-continuity-at-edges/spec.md:65-70`). Es un arrastre de implementación, no una obligación declarada. El incidente está documentado en `docs/specs/007-005-serial-reception/closure.md:68-71`.
- **Consumidores:** `cdad_continuity.py:2654-2669,2716-2743` proyecta `next_action` sin corregirla en `resume`: **esa proyección también queda obsoleta**. No debe confundirse con la orientación compacta de `cdad_packet.py`: sus rutas dependen del estado del paquete/ejecución, no de ese texto (`:8343-8358`; `status_view`, `:8897`). `reconcile` clasifica por recibo/journal y prohíbe duplicar el efecto (`cdad_continuity.py:2345-2358`); `trigger` calcula señal y presupuesto, sin consumir la acción (`:2571-2634`). La búsqueda literal no encontró lectores adicionales de `next_action` en `agents/`, `sources/` ni `build/`; el orquestador remite al mecanismo común (`sources/roles/orchestrator.md:151-180`).
- **`null` frente a texto:** ambos son admisibles (`cdad_continuity.py:563-566`). `null` elimina la orden obsoleta pero pierde orientación; además, suspensión/reanudación transforma una acción ausente en `"Continue the preserved assignment"` (`cdad_packet.py:1033-1037,1079-1097`). Recomiendo **texto canónico**, limitado a «recibo recibido mecánicamente; no repetir despacho/recepción; revisar resultado sin presumir aprobación». Resolverlo en el cierre común cubre toda la familia de entradas sin inventar una siguiente etapa ni modificar cada consumidor. Antecedente coherente: retirada reemplaza la acción, preservando el contexto (`references/continuity.md:81-89`). **VERIFY/decisión de spec:** literal definitivo y tratamiento explícito de `null`.

## Garantías y cobertura

Preservar goal, authority, decisiones anteriores, incertidumbres, referencias, budget, changes y evidence; añadir sólo decisión mecánica, marcador de recibo y enlace `prev` correcto (`cdad_continuity.py:1414-1447`). No modificar identidad ni reconocimiento: clave ejecución/paquete/intento y contenido ruta normalizada/digest; replay devuelve el cierre histórico **antes** de construir otro (`:1450-1542`). No migrar cierres antiguos: conservar bytes y digest, aunque contengan acción obsoleta.

Extender cobertura existente, sin replicar fixtures: 007-003 recepción/replay (`tests/test_007_003_continuity_at_edges.py:1608`), entrada externa (`:1828`) y recuperación (`:1958`); 007-004 recuperación sin nueva recepción (`tests/test_007_004_termination_not_success.py:499`); 007-007 suspensión/reanudación tras recepción (`tests/test_007_007_suspend_resume_units.py:557`). Su prueba de restauración de acción (`:198-238`) sigue válida para contextos **no recibidos**.

## Postcondiciones candidatas

1. Un cierre nuevo por CLI contiene la acción canónica, nunca la orden previa de re-despacho.
2. `resume` proyecta exactamente esa acción; `reconcile` conserva la señal de recibido.
3. El cierre conserva los campos anteriores y añade exactamente un enlace coherente, decisión mecánica y referencia verificable al recibo.
4. Recepción ordinaria, externa y recuperación convergen al mismo comportamiento; `semantic_status` continúa `pending`.
5. Replay inmediato/histórico conserva todos los bytes, digest y secuencia, incluidos cierres legados; conflicto de recibo sigue rechazándose.
6. Suspender/reanudar una unidad recibida conserva la acción posterior al recibo y no repite efectos.

**Riesgos:** interpretar recepción como aprobación; perder orientación con `null`; rehabilitar acción antigua al reanudar; migrar historia accidentalmente; texto adicional que exceda `max_bytes`.

**Evidencia:** lecturas con `read`, `sed -n`, búsquedas acotadas `rg -n`, validación con `sha256sum` (contrato y política coinciden), `git status --short`, `git diff --stat`, `git rev-parse HEAD`. Salida: único cambio preexistente `M docs/.cdad-state.json` (15 inserciones/6 eliminaciones), igual al finalizar. **Archivos modificados por este rol: ninguno. Tests no ejecutados. Commit creado: ninguno; HEAD observado: `5396d327c87bdb32ffa1e7b046ebcdbbbe9359f3`.**
