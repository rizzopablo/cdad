# Informe de corrección — review-fix T5 (010-001)

## Intake (ruta C)

`validate-request` rc=0, `validate-packet` rc=0, contexto v2, sin cuerpo inline; el bloque de identificación coincide con `render --route C`. Contrato `spec.md` con sha256 `9bf17a39…c94da` verificado.

## Hallazgos cerrados

**B1 (bloqueante) — `skills/cdad-cycle/references/documentary-contracts.md` §3**
- Regla 1 incorporada (L74-75): un pendiente cuyo efecto sobre una obligación del contrato aún se desconoce **es bloqueante**; «no conocer el efecto no es evidencia de que ninguna obligación se toque».
- Regla 2 incorporada (L81-83): una contradicción solo permanece si la promesa es documentar posiciones divergentes; debe resolverse si lo prometido es una definición operativa inequívoca que depende de ella.
- Ejemplos de D3 que faltaban (L70-73): hecho del que depende el resultado comprometido sin respaldo; decisión necesaria para delimitar el producto o proteger sus insumos; verificación comprometida que no se puede ejecutar. Redacción propia, sin copiar frases del contrato.

**B2 (bloqueante) — contrato del implementer alineado en las tres superficies**
- `SKILL.md:72` (tabla §2): «May edit: implementation product (code, or a documentary deliverable the engagement expressly commissions)», conservando **NOT `tests/**`**.
- `references/handoff-prompts.md:372`: «edit ONLY the implementation product: code, or the documentary deliverable the engagement expressly commissions», conservando la prohibición de tests.
- `references/sub-agent-strategies.md:35,137`: misma admisión en la lista de sub-agentes y en la tabla de permisos.
- Fila del refactorer (`SKILL.md:73`, `sub-agent-strategies.md:138`) intacta; defaults sin ampliar (la admisión queda condicionada al encargo expreso); `sources/`, `agents/` y `build/` sin tocar, por lo que no hubo regeneración.

**O2 (aceptada) — `documentary-contracts.md` §4 (L98-101)**: el producto editable se expresa con un directorio propio declarado en el alcance; una ruta documental exacta exige estar declarada en la política de rutas; las declaraciones usan los campos existentes, sin campos nuevos.

**O3 (aceptada) — `documentary-contracts.md` §4 (L105-111)**: la norma se detiene también ante ambigüedad sobre qué parte juega un archivo —producto, fuente, verificador o insumo de aceptación— y nombra el contrato de aceptación, no solo la superposición.

**O4**: diferida según el encargo; sin cambios.

## Diff acotado

```
 skills/cdad-cycle/SKILL.md                         |  2 +-
 .../cdad-cycle/references/documentary-contracts.md | 29 +++++++++++++++++-----
 skills/cdad-cycle/references/handoff-prompts.md    |  2 +-
 skills/cdad-cycle/references/sub-agent-strategies.md | 4 +--
 4 files changed, 27 insertions(+), 10 deletions(-)
```

Sin cambios en `tests/**`, spec, plan, `sources/`, `agents/`, `build/`, `scripts/`, `install.sh` ni `Makefile`.

## Comandos y salida

```bash
python3 -B -m unittest tests.test_010_001_documentary_contracts
# ...........
# Ran 11 tests in 8.075s — OK

python3 -B -m unittest tests.test_006_004_u3_principle_single_source
# ...............
# Ran 15 tests in 2.543s — OK
# PD-13/V-4: bloque estático de los 14 pares — máximo 3709 bytes (reviewer/plan-review), techo 12000

python3 -B -m unittest tests.test_006_003_u3_texts_without_profiles
# ..........
# Ran 10 tests in 0.112s — OK

python3 -B -m unittest tests.test_004_001_t6
# .........
# Ran 9 tests in 43.786s — OK
```

La regresión de instalación (`test_004_001_t6`, 9 tests) se ejecutó porque B2 modifica referencias distribuidas; el test de instalación aislada que compara los bytes de la referencia corrió dentro del módulo de 11. Unicidad (PC-13) y vocabulario prohibido de §2 quedaron verdes en sus módulos respectivos.

## Commit

```
71c2a7e2 refactor: close B1 and B2 of the T5 review
```

Estado del árbol posterior: solo `docs/.cdad-state.json` modificado y un `discovery.md` no rastreado, ambos previos a mi trabajo y ajenos al encargo; no fueron incluidos en el commit. No edité tests ni verificadores; la resolución de B1/B2 queda acreditada para la re-examinación semántica del reviewer.
