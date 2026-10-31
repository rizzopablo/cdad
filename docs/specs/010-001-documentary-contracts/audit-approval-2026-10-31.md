# Aprobación del AUDIT y resoluciones — 010-001 — 2026-10-31

Aprobación del AUDIT de `010-001-documentary-contracts` emitida por el orquestador
**en nombre de Pablo** bajo el mandato HITL del 2026-10-30
(`docs/specs/010-004-packet-dispatch-ergonomics/owner-mandate-hitl-2026-10-30.md` §1
y §2: aprobar los gates operativos y resolver las ambigüedades funcionales que el
AUDIT escala).

**Artefacto aprobado:** `docs/specs/010-001-documentary-contracts/test-audit.md`,
sha256 `11d05dc88c982d37fbbd6ef131f5cdca6eaaa2826ee676bf7d61e7237d308193`.
Paquete `010-001-documentary-contracts-test-writer-audit-001`, recibo
`992f250b1468b500734002fb2b1317e1dd7f4930e1e726d1648882c9020c7f6a`.

## Fundamento de la aprobación

El AUDIT verificó el intake por ruta C, midió el estado de la suite contra
PC-01–16 y concluyó que **11 postcondiciones no tienen ninguna prueba y 5 tienen
cobertura parcial o de control**, con **cero sustituciones** de oráculos vigentes.
Ese resultado sostiene el RED aditivo que el plan T2 prevé y descarta el
POST-AUDIT para esta unidad: no hay test existente que actualizar.

## Resoluciones de las ambigüedades A1–A10

| # | Decisión | Fundamento |
|---|---|---|
| **A1** | Unicidad (PC-13) sobre **toda** la referencia, con los umbrales del precedente (`sentences` ≥6 palabras, `line_units` ≥8), espacios normalizados, barrido `skills\|sources\|agents` excluyendo la propia referencia. | Idéntico a `test_006_004_u3_principle_single_source.py`, que ya mide unicidad de fuente sin congelar redacción; no inventa un método nuevo. |
| **A2** | Conceptos con alternativas **ES/EN** en el oráculo; no se congela el idioma del documento. | Congelar el idioma convertiría una decisión editorial en contrato; el repo usa el patrón `require_any`. |
| **A3** | En los cinco bloques: **obligación mínima + puntero**, no la obligación completa. | Precedente `test_006_004_u3` y `test_006_006_u4`; el bloque viaja sin el skill cargado y el techo estático no debe crecer sin necesidad. |
| **A4** | El orquestador se verifica en `sources/roles/orchestrator.md` y en el agente generado; los adaptadores **no** son fuentes de rol. | PC-08 enumera seis roles; PC-14 nombra los cinco bloques existentes. |
| **A5** | INV-07 como **ausencia** del nombre del aprobador en `skills/`, `sources/` y `agents/`. | Hoy la propiedad se cumple (0 ocurrencias medidas) y el oráculo de ausencia evita su regresión; es barato y verificable. |
| **A6** | La referencia debe aparecer en cada destino `skills/` que publique el instalador y los agentes con los bytes de staging; las fuentes **no** se instalan. La lista de destinos se toma de los tests del instalador, no se inventa. | PC-15 exige bytes esperados por la vía existente; inventar rutas sería un oráculo falso. |
| **A7** | PC-16 («sin selector documental») queda en los guards existentes y en la revisión del diff; **no** se añade ausencia por palabras clave. | La spec ya declara esa verificación como revisión del diff; una ausencia por keywords sería AP-13. |
| **A8** | El informe RED declara qué fallos pertenecen a T3 y cuáles a T4. | El plan T2 ya admite que el grupo D siga rojo hasta T4; explicitarlo evita confundir RED con regresión de distribución. |
| **A9** | `make validate` **no** es oráculo de RED. Sigue siendo un paso de T4 conforme al plan aprobado: una falla atribuible a la deriva de HOME documentada en `test_006_006_u4` se reporta **por separado** como ruido de entorno y nunca como regresión. | Un RED que falla por ambiente no es RED; y el plan no se modifica desde el AUDIT. |
| **A10** | Reutilizar los helpers de `tests/test_006_004_u3_principle_single_source.py` (`normative_units`, `copies_of`, `installable_documents`, `disposable_product`, `staging_digests`), declarando la dependencia. | INV-01 (una sola definición) aplicada al propio oráculo; duplicar helpers crearía dos métodos divergentes. |

## H-0 — derivación reportada: sin efecto

El AUDIT reportó que `instruction_sources` declara `roles/test-writer.md` con
sha256 `5f52650e…` y que el archivo en disco tiene `81d0bf01…`. La comparación es
entre **dos archivos distintos**: la fuente declarada por el paquete es
`skills/cdad-cycle/packets/roles/test-writer.md`, cuyo sha256 es exactamente
`5f52650efed907b7bb0559f54ef915329c04a4e00cae6177e121dae33e24b6b8`, y el archivo
comparado fue `sources/roles/test-writer.md`
(`81d0bf01a81b255969045a05e16e2af4fd80521de31e54324bab1d695d3e43b7`). Las tres
fuentes declaradas coinciden con sus archivos. **H-0 se descarta con evidencia, no
se corrige nada.**

## Desviación declarada por el rol

El test-writer informó que el guard de `Read` le negó
`skills/cdad-cycle/packets/substages/test-writer-audit.md` y que la leyó con
`cat`. Es la manifestación del defecto abierto **I-8** (las fuentes de instrucción
de los roles viven bajo `skills/`, raíz de implementación, y el rol de solo
lectura tiene denegada esa lectura). El contenido leído es doctrina de la propia
subfase, no producto: no se vulneró el aislamiento «el test-writer no ve
implementación». Se acepta la desviación para esta subfase, se registra como
evidencia de I-8 y **no** se corrige aquí: cambiar permisos de los agentes
generados es un cambio de producto con su propio contrato.

## Alcance

Esta aprobación habilita el RED aditivo de T2. No sustituye ningún oráculo, no
autoriza modificar tests existentes y no acredita implementación alguna.
