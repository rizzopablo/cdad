# Plan de 016-003-suite-review-tranche-1

- [ ] **Selector y método:** aprobar spec, escribir verificadores independientes e implementar únicamente las superficies bajo `skills/`.
- [ ] **Congelación y auditoría:** materializar colección/selección; auditar los 398 nodeids y materializar deltas de vínculo por unidad.
- [ ] **Experimentos:** registrar presupuesto; contrastar candidatos en copias autorizadas y conservar todos los resultados.
- [ ] **Evaluación y cierre:** medir costo, revisar independientemente, registrar decisión de continuación y aportar evidencia de cierre atribuible.

## Evidencia de esta consulta

**Comandos principales ejecutados:**

```sh
python3 <home>/.agents/skills/cdad-cycle/scripts/cdad_packet.py \
  validate-request --project-root . \
  --request .cdad/packets/016-003-suite-review-tranche-1-architect-draft-001/REQUEST.json

python3 <home>/.agents/skills/cdad-cycle/scripts/cdad_packet.py \
  validate-packet --project-root . \
  --request .cdad/packets/016-003-suite-review-tranche-1-architect-draft-001/REQUEST.json \
  --packet .cdad/packets/016-003-suite-review-tranche-1-architect-draft-001/PACKET.md
```

Además se compararon en memoria los bytes completos de `render` con `PACKET.md` y el SHA256 del contrato: coincidieron.

Colección ejecutada dos veces, **sin ejecutar tests**:

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTEST_ADDOPTS='' \
python3 -m pytest tests --collect-only -q -p no:cacheprovider
```

Resultado: `rc=0`; **1988 tests recolectados**. Primera colección: `4.10s`. Python `3.13.5`, pytest `8.3.5`, Git `2.47.3`; repositorio no superficial. El orden y los hashes del tramo se calcularon con la regla exacta del §4.

**Archivos modificados por mí:** ninguno.  
**Tests ejecutados:** ninguno; sólo colección.  
**Commit creado:** ninguno.  
**Estado observado al entrar y salir:** modificación preexistente de `docs/.cdad-state.json`; sin cambios de producto observados.  
**Costo de auditar el tramo:** todavía no medido; no se deduce del tiempo de colección.
