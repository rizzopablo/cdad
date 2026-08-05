# Etapa E3 — Integración del epic

Verificar que las features del epic funcionan **juntas**, no solo cada una por su lado. Output: tests E2E cross-feature verdes + `integration.md` documentando qué se integró y qué se aprendió.

## Por qué esta etapa existe

Cada feature pasó su propio ciclo CDAD con tests E2E individuales. Pero los tests E2E individuales solo cubren el flujo de UNA feature. La integración del epic verifica que las features compuestas dan el resultado prometido en los criterios de aceptación del epic.

Ejemplo: epic facturación AFIP. Features individuales tienen tests:
- 001 valida CUIT.
- 002 genera XML.
- 003 envía al WS.
- 004 maneja cola de reintentos.
- 005 parsea respuestas.

Pero ningún test individual verifica el flujo completo: factura entra → CUIT validado → XML generado → enviado al WS → respuesta parseada → estado persistido. Eso es trabajo de E3.

## Tu rol

Coordinás. Identificás los flujos cross-feature que hay que testear (los que están en los criterios de aceptación del epic), emitís handoff a **test-writer modo E2E cross-feature**, validás resultado.

## Pasos

### Paso 1 — Identificar flujos a testear

Releé los **Criterios de aceptación del epic** del `plan.md`. Cada criterio que requiere flujo cross-feature es un test E2E del epic.

Ejemplo:

| Criterio | Test E2E cross-feature |
|----------|------------------------|
| "Dado factura válida, se genera XML, se envía, se persiste estado" | Test que ejerce 001 + 002 + 003 + 005 |
| "Dado envío fallido, cola reintenta hasta éxito o timeout" | Test que ejerce 003 + 004 con WS mock que falla N veces |

### Paso 2 — Handoff a test-writer modo E2E cross-feature

Es una variante del E2E que `cdad-cycle` ya tiene, pero con scope ampliado: cubre múltiples features.

Cargá `cdad-cycle/references/handoff-prompts.md` (sí, del otro skill — el patrón es el mismo) y adaptá la sección "Test-writer (Etapa 3 — Integración / E2E)" para cross-feature:

```
Sos un sub-agente test-writer en CDAD modo E2E cross-feature del epic.

Tarea: traducir UN criterio de aceptación del epic a test E2E que ejerce 
múltiples features juntas.

Contexto:
1. Plan del epic: pegar docs/epics/<id>/plan.md
2. Criterio específico a verificar: <pegar>
3. Specs de las features involucradas: pegar docs/specs/<feat-i>/spec.md por cada una
4. API pública de cada feature (las interfaces que se usan desde afuera)
5. Convenciones de tests E2E del proyecto

Reglas estrictas:
- Permisos: edit SOLO en tests/ (en una carpeta tests/integration/ o tests/epic/)
- Llamada vía API pública de las features. NO accedés a internals.
- Setup con fixtures realistas, no mocks que conviertan el test en unit.
- Mocks SOLO para sistemas externos del epic (servicios de terceros, APIs externas).
- Asserts derivados del criterio del epic, uno por uno.

Output esperado: archivo de test E2E + commit "test(epic): add E2E for <criterio>".
Cuando termines:
"LISTO. E2E en <archivo>. Output del run:
<pegar output mostrando E2E verde>
Commit: <hash>"
```

Generá el packet con todo el contexto inline. Entregá al usuario, terminá turno.

### Paso 3 — Re-entry

Validá:

- [ ] Test E2E existe en `tests/integration/` o equivalente del proyecto.
- [ ] Output del run pegado por el usuario muestra verde.
- [ ] Suite completa sigue verde (incluyendo tests previos de cada feature).
- [ ] Commit con prefijo `test(epic):` o similar consistente.

Si pasa: marcá ese criterio como cubierto. Si quedan más criterios cross-feature, emití siguiente handoff. Si no, avanzás.

### Paso 4 — Documentar `integration.md`

Cuando todos los criterios cross-feature tienen E2E verde, draftéa `docs/epics/<id>/integration.md`:

```markdown
# Epic <id> — Integration

## Tests E2E cross-feature

| Criterio | Test | Estado |
|----------|------|--------|
| <criterio 1> | tests/integration/test_epic_<id>_flow.py::test_full_flow | ✅ verde |
| <criterio 2> | tests/integration/test_epic_<id>_retry.py::test_retry_until_success | ✅ verde |

## Hallazgos durante integración

<Cualquier cosa aprendida durante la fase de integración: bugs cross-feature 
que emergieron, ajustes a contratos, refactors que se hicieron a features ya 
done para que jueguen bien juntas, etc.>

## Deuda técnica detectada

<Si la integración reveló deuda que no se resolvió en este epic, documentarla 
para futuros epics o features standalone.>
```

Pasale el draft al usuario para aprobación final del archivo (no es indelegable, pero conviene que el usuario (humano o agente de mayor jerarquía) lo revise antes de commitear).

## 🛑 Gate de salida (E3 → E4)

- [ ] Cada criterio de aceptación cross-feature del epic tiene su test E2E.
- [ ] Todos los E2E cross-feature pasan.
- [ ] Suite completa verde (E2E individuales + cross-feature + unit + properties + linter + type checker).
- [ ] CI verde en main / branch del epic.
- [ ] `docs/epics/<id>/integration.md` existe y está commiteado.

Cuando todos OK: actualizá state (`epic_stage: epic-closure`). Anunciá transición. Cargá `epic-closure.md`.

## Anti-patrón principal (EAP-4)

**Saltar E3 porque "cada feature pasó sus E2E"**. Tests individuales NO sustituyen tests cross-feature. Bugs típicos que solo aparecen en integración:

- Feature A genera output que feature B espera con formato ligeramente distinto.
- Timing entre features (race conditions).
- Recursos compartidos (DB, archivos, locks) que individualmente funcionan pero juntos chocan.
- Errores que en feature A son "manejados" tirando una excepción que feature B no contempla.

Si el usuario intenta saltar:

> *"Las features individuales pasaron sus E2E pero ninguno verifica el flujo completo del epic. La integración cross-feature es justamente donde aparecen los bugs que ningún test individual detecta. ¿Cuántos criterios cross-feature te quedan? Si son pocos, salimos rápido."*

## Si E3 falla — bug cross-feature

Si un test cross-feature falla, identificá qué feature(s) tienen el bug. Es probable que el bug esté en una feature ya `done`, lo cual significa:

1. La feature que tiene el bug vuelve a `in-progress` en el state.
2. Se aplica el fix con disciplina CDAD (test rojo primero, etc.) — sí, requiere otro mini-ciclo.
3. Si el bug revela que el spec de la feature estaba incompleto, se actualiza el spec y se reaprueba.

NO mergeás un fix cross-feature como "patch en el test E2E" sin ir a la feature responsable. Eso ensucia los specs y los rompe a futuro.
