# Aceptación funcional y aprobación del Memory Bank — 010-002 — 2026-10-31

Registro de la aceptación funcional del entregable de
`010-002-documentary-role-integration` y de la aprobación de los borradores de
Memory Bank, **ejercidas por el orquestador en nombre de Pablo** bajo el mandato
HITL del 2026-10-30
(`docs/specs/010-004-packet-dispatch-ergonomics/owner-mandate-hitl-2026-10-30.md`
§1 y §3: aprobar los gates operativos del ciclo y continuar el epic completo sin
detener el ciclo por aprobaciones rutinarias de gate, mientras se implemente la
descomposición y el alcance ya aprobados).

## Objeto aceptado

- Contrato: `docs/specs/010-002-documentary-role-integration/spec.md`, SHA-256
  `0d630c49cfd4c8b0f671026437000617b96bf1bc44b2383dd2914bc7e5581abc` (v4).
- Plan: `docs/specs/010-002-documentary-role-integration/plan.md`, SHA-256
  `3ead624c39a2436d6629afa11883f9cbffde885b548bbecff14f8c9500671190` (v4).
- Producto: el procedimiento documental en
  `skills/cdad-cycle/references/handoff-prompts.md`; la matriz Odoo de
  aplicabilidad por rol en las seis fuentes de rol, en las cinco skills Odoo y en
  las cuatro referencias del inventario; la doctrina de selección en
  `SKILL.md`, los dos adaptadores y `sub-agent-strategies.md`; la derivación
  canónica, los dos contrastes y la regla de presencia en `cdad_packet.py`; el
  esquema `packet-request.schema.json`; y los 22 agentes derivados de ambos
  runtimes.
- Verificadores: `tests/test_010_002_documentary_role_integration.py` (29 tests,
  incluidos los dos controles de B1 y B2) y
  `tests/test_010_002_documentary_role_properties.py` (7 tests); los cinco
  fixtures adaptados de T5.
- Evidencia de cierre: `docs/specs/010-002-documentary-role-integration/closure.md`
  y la medición de suite del intento de cierre.

## Con qué criterio se acepta

1. **La promesa del epic se cumple en el resultado, no en la etiqueta.** Un
   encargo documental encuentra su procedimiento, su alcance, sus fuentes y sus
   verificadores en los campos que ya existían; no hizo falta ningún agente,
   campo ni selector nuevo, y el dominio del proyecto se conserva.
2. **La excepción documental no es una puerta.** Un diff de addon no puede
   cobijarse bajo la etiqueta documental: la regla del diff prevalente está en
   las fuentes de rol, en las skills y en los agentes, y el reviewer la aplica.
3. **El encargo llega a quien debe.** Un agente de otro rol no valida; un
   destinatario incoherente con el dominio vigente no se publica ni se registra
   como intento nuevo; un cambio de `stack` durante la ejecución no invalida un
   trabajo ya lanzado ni su recibo.
4. **Lo que se promete es lo que el mecanismo hace.** La vía nativa declara una
   obligación procedimental y la guarda mecánica se atribuye solo al adaptador
   externo; el esquema describe forma y no se presenta como validador
   contextual.
5. **Nada de esta unidad se presenta como publicado.** La publicación vigente de
   la instalación es la de `010-004` (`2026-10-31`); tras los cambios de
   `010-001`, `010-002` y su corrección la copia instalada está por detrás, y
   volver a publicar es decisión del dueño.

## Lo que esta aceptación NO acredita

- **No acredita fidelidad semántica de un documento real.** Los 36 tests son
  control estructural; la acreditación de fidelidad corresponde al piloto
  `010-003`.
- **No acredita conducta efectiva de modelos.** Ninguna comprobación de esta
  unidad observa qué hace un modelo con la instrucción nueva.
- **No publica ni habilita push.** Esta unidad no actualiza la instalación
  global: la publicación vigente es la de `010-004` (`2026-10-31`) y, tras los
  cambios de `010-001`, `010-002` y su corrección, la copia instalada está por
  detrás (`install.sh --check` rc=1, drift 22/22). Republicar es decisión del dueño.
- **No cierra el epic.** `010-003-documentary-pilot` sigue pendiente.

## Aprobación de los borradores de Memory Bank

Se aprueban los cuatro borradores producidos por el scribe para esta unidad
(`docs/projectbrief.md`, `docs/systemPatterns.md`, `docs/activeContext.md`,
`docs/progress.md`) con el mismo criterio: fidelidad a la evidencia de la unidad,
sin hechos nuevos, con los pendientes y la deriva declarados como tales y sin
presentar nada como publicado. La materialización la ejecuta el orquestador.

## Contexto de la decisión

El review de T8 encontró tres bloqueantes y los tres se cerraron con evidencia
independiente (`review-002.md`: sin bloqueantes nuevos). El defecto **I-10** del
mecanismo de admisión se declara en
`deviation-green-accreditation-2026-10-31.md` con su secuencia exacta y su
estatus de excepción no reutilizable, y queda en el backlog con dos correcciones
posibles. Nada de eso se oculta en este registro.
