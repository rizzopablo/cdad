# Etapa 3 — TDD anti-trampa con sesiones aisladas

La etapa más larga. La trampa principal: que un solo agente escriba test e implementación en la misma sesión. Tu rol como orquestador es justamente prevenir eso emitiendo handoffs separados.

## Tu rol como orquestador

NO escribís tests, NO implementás, NO refactorizás. Coordinás:

1. Identificás qué postcondición toca (la primera pendiente, o agrupación ortogonal si el spec lo permite).
2. Emitís handoff a **test-writer** (RED).
3. Validás test rojo en re-entry.
4. Emitís handoff a **implementer** (GREEN).
5. Validás suite verde en re-entry.
6. Opcionalmente: handoff a **refactorer** si hay fricción evidente.
7. Loop hasta cubrir todas las postcondiciones.
8. Si spec marca invariantes: handoff a **test-writer modo properties**.
9. Si spec marca criterios E2E: handoff a **test-writer modo E2E**.
10. Cierre de etapa cuando todos los gates pasan.

## Sub-fases

| Sub-fase | Rol | Cuándo |
|----------|-----|--------|
| RED | test-writer | Postcondición pendiente |
| GREEN | implementer | Tras RED válido |
| REFACTOR | refactorer | Opcional, si hay fricción |
| PROPERTIES | test-writer modo properties | Spec marca invariantes |
| INTEGRATION/E2E | test-writer modo E2E | Spec marca criterios E2E |

## Sub-fase 3.1 — RED

Cargá `references/handoff-prompts.md` sección "Test-writer (Etapa 3 — RED)".

Antes de generar el packet, decidí qué postcondición tocar:

- La primera pendiente del spec.
- O agrupación de postcondiciones **ortogonales** (paths de código independientes que no se pisan). Si están acopladas, una por ciclo.

Generá packet con:
- Spec aprobado completo.
- Interface / firma del módulo.
- Convenciones de testing (`docs/systemPatterns.md`).
- Postcondición específica a verificar.

Entregás packet, terminás turno.

### Re-entry

Cargá `references/re-entry.md` sección "Test-writer — RED". Verificación crítica: el test falla por **AssertionError**, no por ImportError ni syntax error.

Si pasa: actualizá state, emití handoff a implementer.
Si falla por razón equivocada: handoff de vuelta al test-writer con info del fallo.

## Sub-fase 3.2 — GREEN

Handoff a implementer con: spec, test que tiene que pasar, interface, systemPatterns.

### Re-entry

Cargá `re-entry.md` sección "Implementer — GREEN". Verificaciones críticas:

- Suite **completa** verde (no solo el test nuevo).
- Implementer NO modificó tests/.

Si modificó tests: AP-4. Pedí revertir.

Si pasa: actualizá `postconditions_status: { "<N>": "green" }`. Preguntá si refactor o siguiente.

## Sub-fase 3.3 — REFACTOR (opcional)

**Solo si hay fricción evidente** (duplicación, naming pobre, complejidad accidental). Si código limpio, saltá. Refactor por ritualismo no aporta.

Handoff a refactorer.

### Re-entry

Suite verde EN TODO MOMENTO. Si rojo: AP-11.

## Sub-fase 3.4 — PROPERTIES

Solo si spec marca invariantes verificables. No aplica para código con muchos side effects ni UI.

Handoff a test-writer modo properties.

### Re-entry

Properties verdes con seed fijo, ≥100 inputs.

Si una property falla con input específico: ese input es bug. Handoff a implementer con contraejemplo.

## Sub-fase 3.5 — INTEGRATION / E2E

Solo si spec marca criterios de aceptación E2E o feature toca múltiples capas.

### Modalidades

- **A — outside-in**: E2E primero, queda rojo durante todo el ciclo, va pasando a medida que las piezas se conectan.
- **B — cierre**: E2E al final, después de unidades verdes.

Decidilo con el usuario al inicio de Etapa 3. Para flujo central claro: A. Para agregados a flujos existentes: B.

Handoff a test-writer modo E2E.

### Re-entry

Si modalidad B y E2E rojo: problema de ensamblaje. Handoff a implementer.

## Loop entre postcondiciones

Cada vez que cierra GREEN (+ REFACTOR opcional) de una postcondición, decidís:

- ¿Quedan postcondiciones pendientes? → handoff a test-writer (RED) con la siguiente.
- ¿Todas verdes y spec marca invariantes? → handoff a properties.
- ¿Properties verdes y spec marca E2E? → handoff a E2E (modalidad B) o verificar E2E que ya estaba (modalidad A).
- ¿Todo verde? → cierre de etapa.

## 🛑 Gate de salida (Etapa 3 → Etapa 4)

- [ ] Toda postcondición del spec tiene al menos un test que la verifica.
- [ ] Suite verde (verificado empíricamente con output del run pegado por usuario).
- [ ] Si spec marca invariantes → property tests verdes.
- [ ] Si spec marca criterios E2E → tests E2E verdes.
- [ ] Commits granulares (RED, GREEN, REFACTOR separados).

Cuando todos OK: actualizá state (`current_stage: review`, `tdd_substage: null`). Anunciá transición. Emití handoff a reviewer.

## Anti-patrones a vigilar

- **AP-1**: single session para test + implementación.
- **AP-2**: test escrito después del código.
- **AP-3**: test "verde" sin verificación empírica.
- **AP-4**: implementer modifica tests.
- **AP-11**: refactor que rompe tests.
- **AP-12**: property tests con seed aleatorio.

Cargá `references/anti-patterns.md` si detectás señales.
