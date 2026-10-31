## Evidencia de esta intervención

- **Ruta C válida:** contexto v2; identificación coincidente; request y paquete validados; `PACKET.md` idéntico byte a byte al render canónico completo; SHA-256 del contrato coincidente.
- **Comprobación en memoria:** proyección revisada de ocho hitos aceptada por `_check_plan_tasks`; selector de lectura normativa de T5 aceptado por `_validate_scope`. No se validó un paquete futuro completo de T5.
- **Archivos modificados por este rol:** ninguno. **Commit creado:** ninguno.
- **Tests y suite:** no ejecutados.
- **Base observada:** `3bc0c212185821f506e4c12f2d2789d8ff2b604a`.
- **Estado preexistente conservado:** modificación de `docs/.cdad-state.json` y directorio no versionado de la feature.

Comandos principales ejecutados:

```bash
python3 scripts/cdad_packet.py validate-request \
  --project-root <repo> \
  --request .cdad/packets/010-003-documentary-pilot-architect-draft-004/REQUEST.json

python3 scripts/cdad_packet.py validate-packet \
  --project-root <repo> \
  --request .cdad/packets/010-003-documentary-pilot-architect-draft-004/REQUEST.json \
  --packet .cdad/packets/010-003-documentary-pilot-architect-draft-004/PACKET.md

python3 scripts/cdad_packet.py render \
  --project-root <repo> \
  --request .cdad/packets/010-003-documentary-pilot-architect-draft-004/REQUEST.json \
  --route C

git status --short
git diff --stat
git rev-parse HEAD
sha256sum docs/specs/010-003-documentary-pilot/spec.md \
  docs/specs/010-003-documentary-pilot/plan.md
```

Salidas relevantes:

```text
FULL canonical render: byte-identical; contract SHA256: matches

PASS: revised task projection (8 milestones, existing fields/dependencies) accepted by _check_plan_tasks; T5 norm read-root accepted. Exact authorized norm is contractually limited to documentary-contracts.md.

ea71cb5f6c2a28d8b24a2f8966f81a594869b45f9d58768527fd9fcda17f3510  docs/specs/010-003-documentary-pilot/spec.md
342cb14f9a6d4a8c13c9edaf87ea30a2f6508d5d8f078c8edbb5434b880d7ae6  docs/specs/010-003-documentary-pilot/plan.md
```

Los hashes corresponden a los documentos originales en disco, no a estos borradores todavía sin materializar.
