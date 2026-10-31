# Aprobación del AUDIT T1 — 2026-10-30

- **Aprobador:** orquestador CDAD, en nombre del dueño, bajo mandato HITL
  `owner-mandate-hitl-2026-10-30.md` (instrucción literal del dueño registrada
  allí). El AUDIT no traía aprobación: recibirlo no aprobaba nada.
- **Artefacto aprobado:** `docs/specs/010-004-packet-dispatch-ergonomics/test-audit.md`
- **Digest aprobado:** `fb0fa81f75b17b2249ba9b37183ec30200239382b75cf59ecf19431c2e65a941`
  (`fb0fa81f…`, derivado de los bytes del artefacto al aprobar).
- **Recibo de la entrega:** `5acf26667e67553827e815c8cd950260797287044b0725563427ddb0a1dc13d8`
  (`semantic_status: pending`; el recibo acredita la entrega, no la aprobación).
- **Paquete:** `010-004-packet-dispatch-ergonomics-test-writer-audit-001`;
  **ejecución:** `exec-010-004-packet-dispatch-ergonomics-001`.
- **Producto:** `test-audit.md` (informe AUDIT, materializado por el orquestador,
  ADR-003), sin ediciones del rol.

## Fundamento de la aprobación

1. **Cumple el alcance de T1** (`plan.md:40-55`): inventario test↔promesa/PC con
   expectativas vigentes y sustituidas (§1), traza expectativa anterior →
   `004-002` PD-12 → decisión owner → `010-004` §7/PC-04 sin modificar la spec
   histórica (§2), separación PC-08a/PC-08b (§3), selección focal con regresiones,
   controles positivos, comandos y límites de evidencia (§4), ambigüedades
   escaladas en vez de resueltas por su cuenta (§5) y evidencia de ejecución (§6).
2. **Respeta el contrato del rol:** subfase AUDIT read-only; cero archivos
   modificados y cero commits, con la desviación del campo `commit` declarada en
   vez de fabricar un commit inexistente; implementación no leída, según declara y
   según el alcance del paquete.
3. **La sustitución histórica queda trazada al contrato vigente**, no a una
   interpretación: `spec.md` §7 (sustitución N-3) y PC-04, con la spec `004-002`
   intacta como fuente histórica.
4. **R4 registrada para cada prueba seleccionada** (§ siguiente). Ninguna prueba
   entra como requisito ordinario sin consecuencia de usuario, y ninguna se
   promueve sin motivo registrado.

## R4 — qué se rompe para el usuario sin cada prueba seleccionada

| Selección (AUDIT §4) | Consecuencia de usuario registrada | Origen |
|---|---|---|
| 1. PC-04-a: legacy sin policy + v1 presente | El proyecto legacy seguiría recibiendo encargos v1 **sin policy**: el usuario recibiría trabajo preparado sobre una autoridad que nadie puede verificar, y el despacho se rompería al validar (INV-08/INV-12). | AUDIT §1.1-r1 (consecuencia ya registrada allí) |
| 2. PC-04-b: `prepare` sin flags, contexto v2 en copia no canónica | Una preparación nueva declararía el contexto en una ubicación sin autoridad, o lo resolvería por convenio de ruta: el usuario ejecutaría un encargo con un contexto distinto del registrado. | AUDIT §1.1-r2 (lado EXEC) |
| 3. PC-04-c: preparación nueva exitosa (control positivo) | Sin el control, el endurecimiento podría volverse un rechazo universal y el usuario no podría preparar **ningún** encargo nuevo. La spec lo exige expresamente (§7.1: «un rechazo universal no satisface el contrato»). | Orquestador, al aprobar (control positivo derivado de §7.1) |
| 4. PC-05 fila 1: request con localizador, sin `--execution-context` | El localizador del request no resolvería: el consumidor volvería a transcribir rutas a mano, que es exactamente el defecto que motiva la feature (transcripción manual del contexto). | Orquestador, al aprobar (promesa B, PC-05) |
| 5. PC-06: localizador fuera de dominio o discordante | Un localizador absoluto, vacío o con escapes podría resolver **otra** ejecución: el usuario despacharía contra un contrato que no es el aprobado para esa feature. | Orquestador, al aprobar (PC-06/INV-03/INV-04) |
| 6. PC-07: raíz explícita con directorio de invocación distinto | Los paquetes dejarían de resolver al operar desde un worktree o subdirectorio: caso real de uso del repo, hoy resuelto por transcripción manual. | Orquestador, al aprobar (promesa B, PC-07) |
| 7. PC-02/PC-01 (tanda T3): emisión C | La identificación C podría emitirse sobre contexto v1 o sobre un paquete divergente: se despacharía trabajo con un paquete que no es el validado. | Orquestador, al aprobar (promesa A; se detalla al preparar T3) |

Las pruebas de la tanda T3 se seleccionan al preparar su paquete; esta tabla fija
la consecuencia de usuario de la selección ya auditada y no autoriza ampliarla sin
registro.

## Resolución A1 — frontera de preámbulo de §4.4 para `validate-packet`

- **Recomendación técnica que se adopta** (AUDIT §5-A1): añadir cobertura de la
  frontera de preámbulo en T3 como **regresión faltante, no deuda silenciosa**.
- **Decisión:** se aprueba añadir un RED de PC-08a para la frontera de preámbulo
  **en la tanda T3**, dentro del dispatch RED de T3 (separado, como todo RED).
- **Fundamento:** `spec.md` PC-08a exige «se conserva la diferencia de preámbulo de
  §4.4» y el plan (`plan.md:31`) asigna a T3 cuatro garantías de PC-08a
  reutilizables; solo tres tienen cobertura. La garantía no está «ya verde»: está
  **sin cubrir**, así que no se fabrica un RED para algo verde (lo que la spec
  prohíbe) sino que se cubre una frontera comprometida. Diferirlo habría dejado
  una promesa aprobada sin verificación, contra el criterio de cierre.
- **Límite:** no se convierte en una batería de variantes de preámbulo ni en una
  cuota; un caso por lado (aceptación con preámbulo legítimo y rechazo del
  divergente) basta, con control positivo para no producir un rechazo universal.

## Resolución A2 — lado OUT del test reescrito de `prepare`

- **Recomendación técnica que se adopta** (AUDIT §5-A2): conservar el lado OUT
  (default `.cdad/packets`) en el test reescrito, con contexto canónico explícito.
- **Decisión:** el test `tests/test_packet_prepare.py::test_p2_default_execution_context_and_out_dir_under_project_cdad`
  se reescribe conservando el lado OUT, con un contexto v2 canónico explícito y
  una sola promesa (P2). No se crea un test aparte para el OUT.
- **Fundamento:** PC-04 sustituye el lado **EXEC** (la copia en
  `.cdad/execution.json` deja de ser localizador admisible); el default de salida
  `.cdad/packets` **no** está gobernado por §4.1, así que la sustitución no lo
  alcanza. Conservarlo en el mismo test mantiene la promesa P2 completa sin
  duplicar fixture ni introducir una segunda promesa en un test nuevo.
- **Límite:** la reescritura pertenece al POST-AUDIT aprobado (cambio auditado con
  trazabilidad), no al implementer ni al cierre; el RED nuevo va en su dispatch.

## Consecuencias registradas

- `audit_status` pasa a `approved` con este documento como referencia de
  aprobación; el recibo permanece `pending` (no se reescribe la recepción).
- Habilita **POST-AUDIT**, precedido por el paso habilitante V2-1
  (`owner-decision-plan-v2-1.md`): sin él, el paquete POST-AUDIT renderizaría la
  combinación POST-AUDIT+RED que INV-01 prohíbe.
- RED sigue en un dispatch separado, con fallo por `AssertionError`.
- Esta aprobación **no** aprueba el plan (ya aprobado, pin `2ae8ada3…`), no edita
  `spec.md` (pin `fc6b2ccc…`) y no modifica la spec histórica `004-002`.
