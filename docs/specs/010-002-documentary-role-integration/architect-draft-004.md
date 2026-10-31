## Cambios de v4

- **B1:** adoptada la rederivación. La garantía por construcción cubre preparación ordinaria y `prepare --replace-packet`. El sucesor deriva su agente del rol y stack vigente, también ante un predecesor histórico sin agente. Se incorporan las transiciones a D3, PC-06/07, EV-03, T5, T6 y `plan-tasks`.
- **N5:** T5 ejecuta el módulo nuevo, los tres archivos adaptados y `test_007_002_dispatch_recovery.py`, con resultado esperado y observado por archivo.
- **N6:** un histórico admitido sin contexto ni agente puede registrar un intento nuevo sin contraste contextual del destinatario y sin derivación o sustitución silenciosa.

Los textos siguientes son **borradores completos, no aprobados**. No se han materializado archivos.

---

## Evidencia de esta entrega

**Ruta:** C válida; identificación coincidente; contexto v2; contrato SHA256 comprobado; `PACKET.md` completo idéntico al render canónico.

**Comandos de comprobación ejecutados:**

```sh
R=.cdad/packets/010-002-documentary-role-integration-architect-draft-004
E=.cdad/executions/exec-010-002-documentary-role-integration-001/execution.json

python3 -B scripts/cdad_packet.py validate-request \
  --request "$R/REQUEST.json" --execution-context "$E"

python3 -B scripts/cdad_packet.py validate-packet \
  --request "$R/REQUEST.json" --packet "$R/PACKET.md" \
  --execution-context "$E"

python3 -B scripts/cdad_packet.py render \
  --request "$R/REQUEST.json" | cmp - "$R/PACKET.md"

python3 -B -c 'import json; p=".cdad/executions/exec-010-002-documentary-role-integration-001/execution.json"; print("execution schema:",json.load(open(p))["schema_version"])'

git diff --name-only -- agents skills scripts sources build install.sh tests
git rev-parse HEAD
```

**Salida:**

```text
validate-request: rc=0
validate-packet: rc=0
canonical full render: IDENTICAL
execution schema: 2
product/test tracked diff: empty
3bea7a8d356e35ccb93d22d010632f1d7e7406bf
```

- **Archivos modificados por este rol:** ninguno. Se observaron cambios documentales y de estado preexistentes; no se alteraron.
- **Commit:** ninguno.
- **Tests de producto y suite completa:** no ejecutados; este encargo entrega borradores read-only.
- **Pendiente:** revisión y aprobación explícitas; implementación y acreditación de las postcondiciones mediante el plan.
</subagent>
