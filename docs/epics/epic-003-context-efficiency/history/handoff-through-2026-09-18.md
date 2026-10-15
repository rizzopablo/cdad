> Archivo histórico conservado el 2026-09-23, con el nombre personal sustituido
> por «el usuario». Contiene estados intermedios
> contradictorios; no usar como instrucción de continuación. Ver [handoff actual](../handoff.md).

# Handoff operativo — epic 003

Última actualización: 2026-09-17
Branch: `codex/epic-003-context-efficiency`
Último commit estable: `1e83534`
Publicación: no hacer push automático.

## Mandato vigente

El usuario delegó a Codex el HITL completo del epic: alcance, aprobación de
specs, priorización de review, Memory Bank y gates, con evidencia. La delegación
vence al cerrar, cancelar o revocar el epic. Para los subagentes se usa
`gpt-5.6-sol`. ADR-010 permite modelo único dentro del alcance del epic sin
relajar sesiones, permisos, TDD, review o evidencia.

Usar `cdad-epic` para coordinación y `cdad-cycle` para cada feature. El
orquestador no escribe tests ni implementación. El usuario exige que **cada
handoff futuro actualice este archivo antes de delegar**, porque puede continuar
el trabajo con Claude sin acceso a la conversación actual.

## Estado del epic

Plan aprobado: `docs/epics/epic-003-context-efficiency/plan.md`.

| Feature | Estado |
|---|---|
| `003-001-role-packets` | Review B4 rechazado por invocación symlink; RED pendiente |
| `003-002-artifact-tools` | En cola; discovery/drafts temporales existen, no aprobados ni materializados |
| `003-003-progress-guards` | En cola |
| `003-004-context-continuity` | En cola |

`docs/.cdad-state.json` es la fuente del estado de máquina. Actualmente:
feature `003-001-role-packets`, etapa `tdd`, subfase `red`, audit `approved`,
review `changes-required`.

## 003-001: trabajo cerrado

- Discovery, spec y plan aprobados bajo HITL delegado.
- T1 RED `631b1b3`; T1 GREEN `413cb0d`:
  instalación aislada, binding de ejecución/autoridad, excepción ADR-010 y
  `validate-state`. Evidencia focal 2/2 y check aislado 27/27.
- T2 RED `c5c89a1`; T2 GREEN `e06089f`:
  renderer/validator canónico, 13 parejas rol/subfase, schemas, métricas y
  100 propiedades deterministas. Evidencia 11/11, cero `BLOCKED`, máximo de
  instrucciones estáticas 1.095 bytes frente al límite 12.000.
- T3 RED `eb7e6ce`; T3 GREEN `ddc5f4a`:
  consumidores Task/chat, CLI instalada portable, Python 3 stdlib documentado.
  Evidencia 5/5; T1+T2 13/13; instalación/check aislado 46/46; Odoo 141/141.
- La instalación real no fue modificada. `validate-consistency.sh` conserva
  baseline preexistente 123 PASS / 1 FAIL F011 por drift de copia instalada.
- Los commits GREEN no editaron `tests/**`; tests existentes no fueron
  debilitados.

Artefactos clave:

- `docs/specs/003-001-role-packets/spec.md`
- `docs/specs/003-001-role-packets/plan.md`
- `docs/specs/003-001-role-packets/test-audit.md`
- `docs/specs/003-001-role-packets/t1-red.md`, `t1-green.md`
- `docs/specs/003-001-role-packets/t2-red.md`, `t2-green.md`
- `docs/specs/003-001-role-packets/t3-red.md`, `t3-green.md`
- `docs/specs/003-001-role-packets/post-audit.md`

## POST-AUDIT rechazado y RED correctivo cerrado

Commit `63594af` registra el rechazo. Los tests pasan, pero la cobertura no es
suficiente:

1. PA-1 alto: composición semántica common + rol + subfase y restricciones P3
   no tienen oráculo independiente; `validate-packet` usa el mismo renderer.
2. PA-2 alto: matriz P4 incompleta (autoridad ausente, expiración, feature
   terminada/cancelada/fuera del epic, pares no autorizados, herencia,
   excepción inválida antes de `basic`, `basic` ordinario).
3. PA-3 alto: paridad source/installed podía aprobar dos fallos idénticos.
4. PA-4/PA-5 medios: matrices negativas P2 y estado/métricas P5 incompletas.
5. PA-6 medio: antiguos guards `BLOCKED` retornan éxito; deben fallar después
   de GREEN y el gate final exige cero bloqueos.

El test-writer correctivo cerró esas matrices en `0bc4e4d`: 20 métodos,
16 fallos esperados, cero skips/BLOCKED. Trece fallos exigen procedencia pública
de instrucciones; tres rechazan outcome/timestamps inválidos. P2/P4 ampliados y
P6 endurecido ya pasan. La enmienda aprobada agrega `instruction_sources`
ordenado con SHA-256 y fija RFC3339/outcomes cerrados en P5.

## GREEN correctivo cerrado

Commit `96972c1`. La suite focal integrada pasó 20/20 en 76,830 s, sin skips
ni `BLOCKED`. El implementer no modificó tests. El renderer ahora publica y
valida las tres fuentes ordenadas con hashes ligados a los bytes estáticos; las
métricas validan outcomes cerrados y timestamps RFC 3339 con orden temporal.
Evidencia: `docs/specs/003-001-role-packets/auditfix-green.md`.

## Segundo POST-AUDIT

Commit `edb564a` registra el informe canónico
`docs/specs/003-001-role-packets/post-audit-2.md`. Veredicto: cambios
requeridos. PA-2, PA-3, PA-4 y PA-6 están cerrados. Persisten:

- PA-1 alto: el test no recalcula hashes desde las fuentes ni compara el bloque
  estático byte a byte; faltan exclusiones cruzadas representativas.
- PA-5 medio: falta matriz de `active_packet`, rechazo de pareja rol/subfase
  inválida, orden temporal y aceptación de los cuatro outcomes.

## Segundo RED correctivo

Commit `56bc846`; evidencia canónica
`docs/specs/003-001-role-packets/auditfix2-red.md`. El oráculo PA-1 ahora
recalcula hashes y compara los bytes públicos exactos; P5 cubre todos los
campos, mismatches, orden temporal y cuatro outcomes. Queda un único RED de
producto: `validate-state` acepta la pareja inválida `reviewer/green`. Hay 25
métodos, cero skips/BLOCKED. El test-writer no leyó implementación ni schemas.

## Segundo GREEN correctivo

Commit `10b0f9b`; evidencia canónica
`docs/specs/003-001-role-packets/auditfix2-green.md`. La validación reutiliza
`ROLE_SUBSTAGES` y rechaza `reviewer/green`. Suite focal 25/25 en 109,655 s,
cero skips/BLOCKED. El implementer modificó sólo `cdad_packet.py`, nunca tests.

## POST-AUDIT final aprobado

Commit `00338e0`; informe
`docs/specs/003-001-role-packets/post-audit-3.md`. PA-1..PA-6 cerrados,
25 tests mapeados al contrato, independencia RED/GREEN confirmada y cero
skips/BLOCKED. No se repitió la suite: se reutilizó evidencia 25/25.

## Stage 4 rechazado

Commit `ac7b283`; informe canónico
`docs/specs/003-001-role-packets/review.md`. Ocho bloqueantes:

1. Los cinco agentes Task cargan el skill completo aun con paquete válido.
2. ADR-010 puede heredarse a otro epic autoconsistente.
3. Symlink interno permite relabelar implementación como docs/tests.
4. `CDAD_INSTALL_ROOT=<repo>` hace que uninstall apunte al source.
5. El default relativo de `--project-root` siempre falla.
6. `validate-packet` acepta CRLF por normalización de texto.
7. Métricas sin `active_packet` aceptan identidad inventada.
8. Una raíz explícita sigue requiriendo `HOME`.

Opcionales no incluidos en el gate inmediato: schemas más estrictos y versión
mínima Python. Abstención aceptada: integración OpenCode real queda para
003-003/003-004.

## RED de review cerrado

Commit `e6a007a`; evidencia
`docs/specs/003-001-role-packets/reviewfix-red.md`. Suite ampliada: 33 tests,
25 verdes y ocho RED exactos, cero errores/skips/BLOCKED. El test-writer no leyó
`cdad_packet.py` ni el cuerpo de `install.sh`.

## GREEN de review consolidado

Commit `bea0338`; evidencia
`docs/specs/003-001-role-packets/reviewfix-green.md`. Tres implementadores Sol
trabajaron en archivos disjuntos:

- CLI cerró bloqueantes 2, 3, 5, 6 y 7.
- Instalador cerró bloqueantes 4 y 8.
- Cinco agentes receptores cerraron bloqueante 1.

Suite integrada: 33/33 en 136,283 s, cero errores/skips/BLOCKED; los
implementadores no modificaron tests.

## Segundo review

Commit `cc54141`; informe `docs/specs/003-001-role-packets/review-2.md`.
Veredicto changes-required: 7/8 bloqueantes cerrados. B4 queda parcial porque
`guard_source_overlap` no incluye destinos de `CDAD_SKILL_EXTRA_DIRS`, aunque
uninstall sí los incorpora y ejecuta con `rm -rf`; un extra dir `<repo>/skills`
se acepta y enumera borrado del source.

## RED residual B4

Commit `a9c615a`; evidencia
`docs/specs/003-001-role-packets/extradir-red.md`. Un método B4 produce un RED
con 12 observaciones: extra directo `<repo>/skills` y symlink al mismo source se
aceptan en install dry-run, check y uninstall dry-run. El control positivo con
extra aislado pasa y enumera destinos. Cero errores/skips/BLOCKED.

## GREEN residual B4

Commit `cc81e95`; evidencia
`docs/specs/003-001-role-packets/extradir-green.md`. El guard incorpora todos
los destinos efectivos `<extra>/<skill>` usando el mismo parser del manifest,
resuelve symlinks y rechaza solapamiento antes de acciones. Método B4 verde;
suite integrada 33/33 en 107,105 s; cero errores/skips/BLOCKED. Implementer no
modificó tests.

## Tercer review

Commit `1e83534`; informe `docs/specs/003-001-role-packets/review-3.md`.
Changes-required: al invocar el instalador mediante un symlink externo,
`SCRIPT_DIR` conserva una ruta lógica mientras destinos se canonicalizan; una
raíz igual al repo físico se acepta y publica acciones contra source. Los otros
casos B4 y B1-B3/B5-B8 permanecen cerrados.

## Cierre de 003-001 (sesión Claude Code, 2026-09-18)

- RED symlink del instalador: `da48f3c`. GREEN `641f3b8` (`pwd -P` en SCRIPT_DIR).
- Suite 33/33; 3 validadores en PASS con `CDAD_INSTALL_ROOT` aislado.
- Review-4: APROBADO-COMENTARIOS (`docs/specs/003-001-role-packets/review-4.md`).
- Memory Bank actualizado (activeContext, progress). State: 001 en `done`, sin feature activa.
- Los roles pasan de Codex/`gpt-5.6-sol` a Claude Code (sub-agentes `cdad-*`) por decisión del usuario.

## Próximo paso

Abrir `003-002-artifact-tools` con `cdad-cycle`: el architect audita los tres
drafts de `docs/specs/003-002-artifact-tools/` contra el producto final de 001 y
resuelve las seis decisiones de `remaining-features-handoff.md`. Queda sujeto a
crédito disponible.

## 003-002 preparado pero no iniciado

Existen drafts temporales no canónicos en `/tmp` para spec/plan de
`003-002-artifact-tools`; no asumirlos aprobados. El diseño propuesto recibe
bytes originales, persiste recibos idempotentes, materializa por autorización y
separa evidencia mecánica de aprobación semántica. Antes de usarlo, revisar las
correcciones pedidas al architect y repetir discovery/spec bajo `cdad-cycle`.

## Reglas de continuidad

- No hacer push salvo pedido explícito.
- No reparar la instalación real para ocultar F011; usar raíces aisladas.
- No afirmar sandbox de archivos en subagentes Codex: hay contexto nuevo y
  restricciones conductuales auditables, filesystem compartido.
- No repetir desarrollos ni hacer A/B de modelos. Validar hacia adelante.
- Mantener desconocidos como `null`; bytes no son tokens.
- Antes de cada handoff: actualizar último commit, estado, agente/rol, alcance,
  evidencia pendiente y siguiente comando en este archivo; commitearlo junto al
  handoff o antes de la delegación.
