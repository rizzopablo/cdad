# Dictamen de plan-review (cuarta pasada): 010-002-documentary-role-integration

**Recomendación: la versión 4 es aprobable.** No encontré bloqueantes. B1, N5 y N6 están cerrados y los cambios no introducen contradicciones. El único punto que el dueño debería conocer antes de aprobar es N7, un callejón sin salida estrecho y fail-closed. Este dictamen no aprueba nada ni autoriza implementar.

**Objeto revisado**
- `plan.md` v4: `3ead624c39a2436d6629afa11883f9cbffde885b548bbecff14f8c9500671190`
- `spec.md` v4: `0d630c49cfd4c8b0f671026437000617b96bf1bc44b2383dd2914bc7e5581abc`

**Intake:** ruta C válida.
- La identificación coincide con `REQUEST.json` y `PACKET.md`, y ambos hashes coinciden con el contrato.
- El contexto de ejecución es v2.
- `validate-request` y `validate-packet` dieron rc=0, y `render` es idéntico a `PACKET.md`.

## Hallazgos bloqueantes

Ninguno.

## Hallazgos no bloqueantes

### N7. Un cambio de `stack` sin otra obsolescencia deja el paquete `prepared` sin salida directa
- **Severidad:** Consider
- **Verdict:** OPTIONAL
- **Bucket:** m
- **Ubicación:** `spec.md:123,139,325`; `plan.md:241-242`; `skills/cdad-cycle/scripts/cdad_packet.py:3707-3713,6467-6487`.
- **Fundamento:**
  - El reemplazo exige que hayan cambiado el contrato, su documento complementario o la política, o que exista una disposición.
  - Un cambio de `stack` no cuenta como obsolescencia.
  - Tras ese cambio, y solo con ese cambio, el intento nuevo se rechaza por la regla nueva.
  - `--replace-packet` se rechaza por PD-8, y `prepare` ordinario queda bloqueado por el paquete activo publicado.
  - La disposición no sirve, porque exige un despacho previo.
- **Consecuencia:**
  - Falla cerrado y ningún trabajo llega a un rol equivocado.
  - La spec es honesta: condiciona el reemplazo a «si satisface sus precondiciones» (`:139`).
  - `spec.md:325` dice que el orquestador «registra y resuelve», pero no indica cómo. Las salidas reales son restaurar el `stack` o hacer un cambio legítimo de contrato o política.
  - El caso es raro, y el reemplazo tras cambio de `stack` queda cubierto cuando también hay obsolescencia.
- **Condición de cierre:** una línea en `spec.md:325` o en el procedimiento que nombre esas salidas. No hay que relajar PD-8.

### FYI
- **Traza de `.superseded.json`:** `agent` queda fuera de `ASSIGNMENT_UNIVERSE` (`cdad_packet.py:3340-3343`), así que un cambio de agente no aparecerá en `changed_fields`. Se observa comparando ambos `REQUEST.json`. Es coherente con el contrato: no se añaden campos y PC-06 se verifica sobre el valor publicado.
- **ADR-019:** se titula «el reemplazo conserva el encargo», pero su lista de campos conservados (`:65-67`) no incluye `agent`. La rederivación no lo contradice. El comentario de `cdad_packet.py:3797-3799`, que justifica la copia, cae dentro del cambio de T6.
- **Adaptador externo:** en históricos sin `agent` usa `cdad-<role>` como fallback declarado, con nota explícita de ausencia (`cdad_delegate_opencode.py:419-437`). Esto no contradice P-3 ni `spec.md:133,171`, que separan el tratamiento histórico declarado del fallback silencioso. T5 debe verificar el registro y no leer ese lanzamiento como derivación silenciosa.

## Verificación B1, N5 y N6

| # | Resultado | Evidencia |
|---|---|---|
| **B1** | Cerrado | Ver el detalle bajo esta tabla. |
| **N5** | Cerrado | Cinco comandos, sin omitir ninguno porque otro falle (`plan.md:218-231`, `:555-559`). RED esperado y observado por archivo (`:233`, `:562`). Sin fabricar fallos ni aceptar fallos de fixture (`:235`, `:563`). Gate y evidencia alineados (`:276,376`; `spec.md:312`). |
| **N6** | Cerrado | D3 (`spec.md:133`), PC-07 (`:251`), PC-08 (`:254`), INV-04 (`:299`), EV-03 (`:313`), T5 (`plan.md:249,267,571`) y T6 (`:294,603`). Es implementable: `_record_dispatch` no exige `agent` y `execution_context` es condicional (`cdad_packet.py:1740`). Coincide con P-3. |

**Detalle de B1**

- **Declaración:** el reemplazo es publicación nueva y el sucesor rederiva el agente sin copiarlo (`spec.md:113,118-127`).
- **Las dos vías públicas:** cubiertas en `spec.md:118-125`.
- **Predecesor sin `agent`:** `spec.md:122,245`.
- **`stack` cambiado:** `spec.md:123,246`.
- **Bytes históricos y precondiciones:** conservados en `spec.md:127,139,247`.
- **Transición incorporada:**
  - PC-06 y PC-07: `spec.md:244-249`.
  - EV-03: `spec.md:313`.
  - T5: `plan.md:240-242,565-566,577`.
  - T6: `plan.md:291-292,600-601`.
- **`tests/test_007_002_dispatch_recovery.py`:**
  - T5 en prosa: `plan.md:210`.
  - T5 en tabla: `:417`.
  - T5 en `plan-tasks`: `:552,559`.
  - T6 en prosa: `:318`.
  - T6 en tabla: `:418`.
  - T6 en `plan-tasks`: `:618`.
- **Implementabilidad:** `_replace_packet` ya tiene `state` y publica por el mismo punto, y `_packet_agent(role, state)` (`cdad_packet.py:6412`) es reutilizable.
- **Tests existentes:** ninguno de los cinco archivos de reemplazo que revisé fija la copia del agente. Son `test_005_005_t1`, `test_005_001_t2`, `test_006_006_w1`, `test_010_004_t6_red` y `test_005_001_tcorr`. T2 hace la medición completa.

## Otras verificaciones

| Punto | Resultado | Evidencia |
|---|---|---|
| P-1..P-4 frente a spec y plan | Sin contradicción | P-1 en `spec.md:96-105`, P-2 en `:129-131`, P-3 en `:133`, P-4 en `:118-127`. El FYI de `plan-review-003` sobre P-1 queda resuelto: la precisión ya está registrada. |
| Dictámenes previos | N1..N4 conservados | Las listas de T5/T6 siguen sin sustituir la medición de T2 (`plan.md:101,320,422`). |
| Epic | Sin contradicción | La combinación documental/Odoo sigue en PC-12 (`spec.md:286-287`). |
| Current decisions | Sin conflicto | ADR-019 vigente; ver FYI. |
| Alcance | Sin ampliación | Sin agentes, campos, etapas, selectores ni permisos nuevos (`spec.md:334-335`; `plan.md:301`). |
| Referencias de spec §10 | Correctas | Los hashes de `plan-review-003.md` y de `discovery-decisions-2026-10-31.md` coinciden. Los localizadores P-1..P-4 (`147-183`) y `3796-3801` también. |
| `plan-tasks` | JSON válido | 9 tareas. No volví a ejecutar `_check_plan_tasks`. |

## Abstentions
- **N7, por lectura de código:** no reproduje la secuencia completa de cambio de `stack` y rechazo en un proyecto descartable.
- **Fixtures con `"stack": "generic"`:** sigue sin determinar si alcanzan el contraste contextual. Corresponde a T2.
- **Medición completa de fixtures:** corresponde a T2.
- **Suficiencia de la matriz Odoo:** se juzga en T8.

## Evidencia
- **Archivos modificados:** ninguno. El diff de producto y tests está vacío (0 rutas).
- **Commit:** ninguno. `HEAD` es `3bea7a8d356e35ccb93d22d010632f1d7e7406bf`.
- **Comandos:**
  - `python3 -B scripts/cdad_packet.py validate-request --request <REQUEST.json> --execution-context <execution.json>`
  - `python3 -B scripts/cdad_packet.py validate-packet --request <REQUEST.json> --packet <PACKET.md> --execution-context <execution.json>`
  - `python3 -B scripts/cdad_packet.py render --request <REQUEST.json> | cmp - <PACKET.md>`
  - `sha256sum` de los documentos citados
  - `python3 -I` para parsear el bloque `plan-tasks`
  - `git diff --name-only -- agents skills scripts sources build install.sh tests`
  - `rg` y `sed` sobre las rutas citadas
- **Salidas:** `vr=0`, `vp=0`, `cmp=0`, hashes coincidentes con el contrato, `plan-tasks` con 9 tareas.
- **Suite completa:** no ejecutada; este paquete no la pide.
