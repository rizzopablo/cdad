# Encargo 2 para el orquestador OpenCode — epic-005 / 005-001

Fecha: 2026-10-08. Reemplaza a [handoff-opencode.md](handoff-opencode.md), que queda como historia.
Este encargo trae el diagnóstico hecho: no hace falta reconstruirlo.

## 1. Identidad

- **Proyecto:** el repo git `<proyecto>`, sin importar desde dónde abras la
  sesión. Su directorio contenedor es otro repo que solo guarda el gitlink: no trabajes ahí.
  Usá rutas absolutas o `git -C <proyecto>`.
- **Rama:** `codex/epic-005-real-operation`. Sin push.
- **Versión operativa:** v7 `ce09ed0`. Skills y config: `.cdad/activation.json`. Agentes de
  proyecto: publicados desde la v7 y verificados (11/11 hashes, `source_dir` en
  `<raíz adoptada>/.config/opencode/agents`). Usá los scripts del proyecto con esa
  misma versión; no mezcles v6.
- **Autoridad:** plan aprobado por Pablo y delegación en [execution.md](execution.md). La ampliación
  de 005-001 también está aprobada (ver «Cambios al plan»).

## 2. Estado comprobado (al escribir este encargo)

- `docs/.cdad-state.json`: `active_epic` epic-005, `features-loop`, `active_feature`
  005-001, `current_stage: discovery`, ejecución `exec-005-001-idle-and-v7-bootstrap-001`.
- `stage_history[161]`: entrada con `stage: specification` y `approved_by: Pablo` para 005-001,
  con el plan como evidencia. **No es una aprobación de spec**: la spec no existe. Se registró para
  pasar el control I2 del primer `prepare`.
- `active_packet`: `005-001-idle-and-v7-bootstrap-architect-discovery-001`, `prepared`, nunca
  despachado. **Está obsoleto**: el plan cambió después de prepararlo y `prepare --resume-packet`
  devuelve `contract sha256 does not match exact content`. Ese rechazo es correcto.
- La ejecución 005-001 no tiene checkpoint de continuidad todavía. `cdad_continuity.py resume`
  (contexto del orquestador) y `cdad_packet.py prepare --resume-packet` (re-emitir los bytes de un
  paquete) son operaciones distintas; ninguna de las dos aplica ahora.

## 3. Obstáculos conocidos (defectos del producto, se corrigen en 005-001)

- **I2 circular:** `_approved_stage_entry` (`skills/cdad-cycle/scripts/cdad_packet.py`) se aplica a
  todos los roles y exige una entrada `feature` + `stage: specification` + `approved_by` no vacío.
  El architect, que redacta la spec, no puede prepararse sin ella. Solo mira esas tres claves: toma
  la primera entrada que coincida.
- **Sin reemplazo de paquetes:** no hay camino en el CLI para retirar un paquete preparado cuyo
  contrato cambió.

## 4. Siguiente acción, en orden

1. **Rectificar `stage_history[161]`** en una forma que el control actual excluya, conservando la
   historia: cambiá `stage` a `discovery-authorization` y renombrá `approved_by` a `authorized_by`;
   agregá `rectified_at: 2026-10-08` y una nota: «Registrada para pasar I2 en el primer prepare; no
   es una aprobación de spec. Rectificada por la revisión del dueño.» No la borres.
2. **Retirar el paquete obsoleto:** `active_packet` a `null`. No lo marques `completed` ni `failed`
   y no borres `.cdad/packets/005-001-idle-and-v7-bootstrap-architect-discovery-001/`. Registrá en
   `docs/specs/005-001-idle-and-v7-bootstrap/dispatch-ledger.md`: id, `contract_sha256`, motivo
   (plan editado después de prepararlo) y que nunca se despachó.
3. Commit del state y del ledger; árbol limpio.
4. **Consecuencia esperada:** hasta que la corrección exista, `cdad_packet.py prepare`,
   `validate-state` y `--resume-packet` van a fallar por I2 para esta ejecución. Es correcto: no
   hay spec aprobada. No lo esquives con otro registro.
5. **Discovery por el camino temporal fuera del CLI:** escribí
   `docs/specs/005-001-idle-and-v7-bootstrap/handoff-architect-001.md` y despachá al architect
   (`cdad-architect`, `mofgw/deepseek-v4.1-flash`, solo lectura) con ese archivo. Registralo en el
   ledger como «camino temporal fuera del CLI por I2 circular; autoridad: plan aprobado +
   execution.md». No es una aprobación de spec.
   - Insumos: `plan.md` (fila 005-001, puntos a–e, y «Cambios al plan»), este encargo §2–3, la
     deuda VALIDATE-IDLE de `docs/specs/003-007-living-continuity/debt.md`, y el código de
     `_approved_stage_entry`, `_validate_v2_vigency`, `_contract_for` y `--resume-packet`.
   - Pedido: spec con postcondiciones verificables y plan de tareas para (b) aprobación por rol,
     (c) reemplazo de paquetes preparados no despachados, (d) mensajes que distinguen aprobación
     pendiente / paquete obsoleto / estado incoherente y dicen cómo seguir, (e) reposo legítimo.
     Debe incluir la prueba decisiva del plan y qué pasa con una entrada rectificada como la del
     paso 1 (no habilita nada).
6. Aprobá la spec y el plan bajo la delegación. Registrá la aprobación real en `stage_history`
   (`stage: specification`, `approved_by` del delegado, evidencia `spec.md` y su sha256). Desde
   ahí el ciclo sigue por el CLI.

## 5. Límites

- No instales CDAD en HOME ni actives versiones; eso es del dueño.
- Sin `--no-verify` ni push. No leas `tests/.sensitive-patterns.local`.
- Gates de tests según el plan. Las suites largas, en primer plano con `timeout` holgado,
  esperando `EXIT=`.
- No vuelques salidas enormes al contexto: filtrá o resumí (una sola salida de la sesión anterior
  pasó de 51 mil caracteres).
- Ante un obstáculo fuera de tu ámbito, entregá el diagnóstico; no fabriques registros ni alteres
  cambios ajenos para esquivarlo.
