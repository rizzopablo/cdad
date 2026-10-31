# Scribe role report — 010-001-documentary-contracts

Entrega del paquete `010-001-documentary-contracts-scribe-memory-002` (transporte
nativo, ruta C, attempt 1). Materializada por el orquestador bajo ADR-003: los
cuatro borradores de Memory Bank viajan como partes separadas con sus kinds
(`scribe-projectbrief`, `scribe-systemPatterns`, `scribe-activeContext`,
`scribe-progress`) y este informe conserva la propuesta de ADR y el reporte del rol.

## Intake declarado por el rol

| Comprobación | Resultado |
|---|---|
| `sha256` del contrato en disco vs. identificación | coincide (`9bf17a39…d4f4d26c94da`) |
| `validate-request` | rc=0, sin salida |
| Paquete completo vs. render canónico | `diff` sin diferencias → IDENTICAL |
| `validate-packet` | rc=0 |
| Identificación recibida vs. `render --route C` | idéntica |
| `validate-state` del contexto de ejecución | `VALID`, `schema_version: 2` |
| Cuerpo inline | no hay → sin mezcla A+C |

## Propuesta de ADR (NO adoptada por la unidad)

**Estado de la decisión:** existe una decisión arquitectónica durable, pero la unidad
no adoptó ningún ADR: el diff no toca `docs/adr/`, la tabla «Decisiones vigentes» de
`systemPatterns.md` no recibe fila, y el reviewer se abstuvo de cotejar esa tabla. El
ADR va como **propuesta** (no vigente) y su número queda a cargo del orquestador/dueño.

**Destino propuesto:** `docs/adr/ADR-040-contratos-documentales-casa-unica-y-dos-registros.md`

```markdown
# ADR-040 — Contratos documentales: una casa normativa única y dos registros de cierre

- **Estado:** Proposed (borrador de scribe; no adoptado por la unidad `010-001`).
- **Fecha:** 2026-10-31.
- **Decisores:** dueño del repo (aprobación); orquestador (materialización).
- **Roles afectados:** `orchestrator`, `architect`, `test-writer`, `implementer`,
  `reviewer`, `scribe` y sus variantes Odoo.
- **Confidence:** **Medium** (ver §Confianza).

## Contexto y problema

El ciclo CDAD produce también entregables documentales —relevamientos, mapas de
proceso, historias de usuario— y hasta `010-001` cada encargo inventaba sus criterios:
qué cuenta como evidencia, cómo se cita una fuente, cuándo un pendiente impide aceptar,
y hasta dónde puede escribir el rol que produce. Los roles ya se obligaban por puntero
a referencias compartidas (`design-principles.md` es el precedente), y las superficies
instalables se generan desde `sources/` hacia staging y de ahí a los agentes.

La pregunta abierta era de forma, no de capacidad: ¿un skill nuevo con su propio
mecanismo, o una referencia dentro del ciclo existente con obligaciones breves en los
consumidores?

## Decisión

1. **Una sola casa normativa:** `skills/cdad-cycle/references/documentary-contracts.md`,
   localizable desde la tabla de referencias de `skills/cdad-cycle/SKILL.md`. Los
   consumidores —seis fuentes de rol, cinco bloques estáticos de paquete y los agentes
   derivados de ambos runtimes— declaran su obligación en sus propias palabras y
   nombran el archivo. Ninguna superficie instalable reproduce sus frases normativas.
   La unicidad se mide por frases normativas derivadas de la referencia, con espacios
   normalizados, sobre `skills/`, `sources/` y `agents/`.
2. **Aplicación condicional:** la norma gobierna cuando el encargo declara producto
   documental; el trabajo de código conserva las reglas de su rol.
3. **Categorías como criterio, no como formato:** evidencia, propuesta, contradicción y
   pendiente son distinciones obligatorias y localizables, no secciones vacías.
4. **Frontera de escritura:** fuentes autorizadas, producto editable delimitado por
   rutas, verificadores e insumos de aceptación protegidos, evidencia esperada y límites
   de verificación se declaran antes de empezar. Compartir la clasificación `docs` no
   vuelve editable un archivo. **Quien produce no modifica su oráculo.**
5. **Dos registros que nunca se sustituyen:** control estructural (qué se ejecutó,
   resultado, alcance, límites) y revisión semántica independiente (qué se contrastó,
   hallazgos, abstenciones). La aceptación funcional es del usuario/dueño que aprueba.
6. **Sin autoridad nueva:** no crea roles, etapas, campos del request/estado ni
   permisos por defecto, no reemplaza el Memory Bank y no convierte al scribe en
   productor documental general.

## Alternativas consideradas

- **Skill o agente nuevo dedicado a documentación.** Descartada: duplicaría el
  mecanismo de distribución y obligaciones ya existente y agregaría superficie
  aprobatoria sin promesa adicional.
- **Formato universal impuesto (cuatro secciones o tabla Markdown fija).** Descartada:
  obliga a instancias ficticias y no mejora la verificabilidad.
- **Protección mecánica por hash de cada insumo.** Descartada para esta unidad: exige
  diseño de esquema no autorizado; se conserva la separación contractual y queda como
  `deferred-hardening`.
- **Validador automático de fidelidad semántica.** Descartada: no es acreditable por
  presencia estructural ni por puntajes.

## Consecuencias

### Positivas

- Un encargo documental encuentra criterios explícitos donde su paquete lo señala; no
  hay que inventarlos por encargo.
- La obligación viaja por la vía de distribución ya auditada (staging determinista,
  instalador, techo de bloques estáticos), sin mecanismo paralelo.
- La frontera producto/fuentes/verificadores impide que el rol que produce ajuste su
  propio oráculo para obtener un resultado favorable.
- El cierre declara por separado estructura y fidelidad: un verde de tests no se puede
  presentar como aceptación semántica.

### Negativas y costos

- **Dos superficies que mantener en fase:** fuentes de rol y bloques estáticos; el
  generador no compone la tabla §2 de `SKILL.md`, así que una corrección de contrato
  puede quedar dividida entre superficies (fue exactamente el bloqueante B2).
- **La obligación no viaja por conducta:** es admisión documental; las guardas
  comprueban tokens estables y su supervivencia en los derivados, no la obediencia de
  un modelo.
- **Deriva de publicación:** mientras la instalación global no se actualice, los
  agentes instalados no llevan la obligación y el CLI instalado compone paquetes desde
  su copia vieja; el trabajo depende de la toolchain del repo.
- **Redacción no estabilizada:** quedaron un «only» más estricto que la decisión
  (N1), un residuo de descripción de salida (N2) y solapamiento de 6-gramas (O4),
  diferidos al piloto.

## Referencias

- `docs/specs/010-001-documentary-contracts/spec.md` (PC-01..PC-16, D1..D4, INV-01..INV-08).
- `skills/cdad-cycle/references/documentary-contracts.md` (la casa normativa).
- `docs/specs/010-001-documentary-contracts/closure.md` (§2 postcondiciones y clase de
  evidencia, §4 desviaciones, §5 deriva, §6 diferidos).
- `docs/specs/010-001-documentary-contracts/{review.md, review-002.md}`.
- Precedente de forma: `docs/adr/ADR-034-principio-general-antes-especifico.md`.

## Confianza

**Medium.** A favor: la decisión está ejercida y medida en la unidad —transporte a seis
fuentes, cinco bloques y 22 agentes, unicidad por frases normalizadas, techo 3709/12000,
generación reproducible e instalación aislada con bytes verificados— y su necesidad
surgió de una brecha real del ciclo. En contra: la revisión independiente encontró dos
bloqueantes en la primera pasada (la norma omitía reglas de la propia decisión y el
contrato del implementer quedaba dividido), la redacción tiene dos nits abiertos, y la
**suficiencia semántica para un documento real no está acreditada**: corresponde al
piloto `010-003`. Por eso no se propone como `Accepted`.
```

## Reporte del rol (verbatim)

**Archivos modificados en el repositorio:** ninguno. `write_scope` vacío, respetado.

**Comandos ejecutados y salida (exacta):**

```bash
# intake
sha256sum docs/specs/010-001-documentary-contracts/spec.md
# 9bf17a398b55384e271815c8a6c2910563f75a5d2475ec291c31d4f4d26c94da  docs/specs/010-001-documentary-contracts/spec.md

python3 scripts/cdad_packet.py validate-request --request .cdad/packets/010-001-documentary-contracts-scribe-memory-002/REQUEST.json
# rc=0, sin salida

python3 scripts/cdad_packet.py validate-packet --request .cdad/packets/010-001-documentary-contracts-scribe-memory-002/REQUEST.json \
  --packet .cdad/packets/010-001-documentary-contracts-scribe-memory-002/PACKET.md
# rc=0

python3 scripts/cdad_packet.py render --request .cdad/packets/010-001-documentary-contracts-scribe-memory-002/REQUEST.json \
  --execution-context .cdad/executions/exec-010-001-documentary-contracts-002/execution.json > /tmp/opencode/render.md
diff /tmp/opencode/render.md .cdad/packets/010-001-documentary-contracts-scribe-memory-002/PACKET.md
# sin salida -> IDENTICAL

python3 scripts/cdad_packet.py render --route C --request .cdad/packets/010-001-documentary-contracts-scribe-memory-002/REQUEST.json
# bloque identico al recibido (comparado campo a campo y byte a byte)

python3 scripts/cdad_packet.py validate-state --execution-context .cdad/executions/exec-010-001-documentary-contracts-002/execution.json --project-root .
# VALID: execution=exec-010-001-documentary-contracts-002 feature=010-001-documentary-contracts model_policy=ordinary   (rc=0)

# medicion propia citada en los borradores
python3 -B -m unittest tests.test_010_001_documentary_contracts
# ........... / Ran 11 tests in 10.409s / OK
python3 -B -m unittest tests.test_006_004_u3_principle_single_source.TestPd13StaticBlockCeiling
# . / Ran 1 test in 1.376s / OK
# maximo 3709 bytes (reviewer/plan-review), techo declarado 12000 bytes

# estado del arbol al redactar (sin cambios por mi trabajo)
git status --porcelain
#  M docs/.cdad-state.json
# ?? docs/specs/010-000-continuity-relative-root/discovery.md
# ?? docs/specs/010-001-documentary-contracts/closure.md
# ?? docs/specs/010-001-documentary-contracts/owner-acceptance-2026-10-31.md
```

**Commit:** ninguno. No aprueba ni materializa: los cinco borradores quedan como FINAL
TEXT para que el usuario apruebe y el orquestador los materialice y commitee (ADR-003).

**Límites de esta entrega.** Los borradores son fieles a los documentos declarados como
entradas; no verificó la suite completa ni `install.sh --check` (política: la corre
quien cierra, y el dato del cierre §5 se cita como medición del autor, no propia).
`closure.md` y `owner-acceptance-2026-10-31.md` estaban sin commitear en el árbol al
redactar; si cambian antes de materializar, estos borradores deben revalidarse.
`make validate` rc=2 por deriva (F011) se registra como fallo conocido, no como verde.
