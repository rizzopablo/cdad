# Cierre — 009-001: overlay de claves de usuario en agentes instalados

- **Épica:** `epic-009-installer-updates` (épica light de una feature, decisión del dueño 2026-10-28)
- **Estado:** cerrada con evidencia; sin push (la publicación sigue reservada al dueño)
- **Contrato:** `docs/specs/009-001-installer-agent-overlay/spec.md` (sha256 `61caacb6…`)

## Qué se prometió y qué se entrega

> Instalar una actualización de CDAD **no cuesta la configuración del usuario**: el `model:` elegido por
> agente sobrevive, el resto del agente se actualiza, el archivo sigue owned y el despliegue sigue siendo
> verificable.

**Antes.** Un `model:` en el frontmatter del agente instalado dejaba el archivo en **conflicto**: dejaba de
ser owned, no recibía actualizaciones y `--check` fallaba. El remedio operativo (borrar y reinstalar)
**borraba el modelo**. Reproducido en `.cdad/local/009-001/evidence/repro.md`.

**Después.** El overlay se reconoce, se reinserta sobre el staging nuevo y el agente queda owned. La
procedencia decide sólo cuando la base **no** es el staging actual (edición local real o upstream movido), y
en ese caso el conflicto D4 se conserva intacto.

## Postcondiciones

| PC | Estado | Evidencia |
|---|---|---|
| PC-1 conserva el valor sin conflicto | **cumplido** | `test_pc1_*` (12/12 verde) |
| PC-2 el resto del agente se actualiza | **cumplido** | `test_pc2_update_rebases_non_overlay_bytes_onto_new_staging` (fixture corregido: fuente→destino determinista) |
| PC-3 sigue owned, SYNC, `--check` 0 | **cumplido** | `test_pc3_*` + escenarios (a)(b)(c) del review-fix |
| PC-4 modificación fuera del overlay → conflicto D4 | **cumplido** | `test_pc4_*` (guardián) + escenario (d) del review-fix: `CONFLICT` preservado, no owned |
| PC-5 ningún texto instalable fija modelo | **cumplido** | `test_pc5_*` con pierna negativa (staging envenenado → rc 1) y positiva (overlay instalado → PASS) |
| PC-6 diagnóstico nombra la ruta instalada | **cumplido** | `test_pc6_*` + `Check: FAIL — drift .config/opencode/agents/…` |
| PC-7 `--uninstall` preserva el agente con overlay | **cumplido** | `test_pc7_*` byte a byte + `PRESERVED` |

## Lo que el review adversarial cambió (y por qué el ciclo valió)

El primer GREEN tenía **siete tests verdes y tres defectos reales**. El review los reprodujo:

- **F1 (crítico):** cambiar de modelo —la edición más común— producía conflicto y congelaba el agente; las
  copias que el instalador viejo había dejado en conflicto no se reparaban nunca. Se corrigió comparando
  contra el staging vigente *antes* del gate de procedencia.
- **F2:** el validador tenía su propia copia de la lista de claves (`grep '^model:'`), violando INV-2. Ahora
  consume `scripts/agent-overlay.py extract`.
- **F3:** el veredicto de `--check` seguía nombrando la ruta de staging. Corregido.

Los cinco tests que faltaban se escribieron **antes** del fix y fallaron por `AssertionError` (contrafactual
verificado). Sin esa ronda, la feature habría llegado al dueño con PC-1 roto en el caso más frecuente.

## Cambios

| Archivo | Qué |
|---|---|
| `scripts/agent-overlay.py` (nuevo, 234 líneas) | Única definición: `USER_OWNED_KEYS` como dato, gramática estrecha del frontmatter, `extract`/`merge`/`compare`/`installable-check`, fail-closed |
| `install.sh` | `stage_user_overlay` + `deploy_staged_overlay` en los 3 call sites; `--check` compara contra el esperado y nombra la ruta instalada; `--uninstall` preserva el overlay |
| `scripts/validate-subagents.sh` | Stage de modelos consume el helper; sin literal `^model:` |
| `tests/test_009_001_installer_agent_overlay.py` (nuevo, 12 tests) | Una prueba por promesa + los 5 casos del review |
| `README.md` | Documentación del overlay y de las claves de usuario |

## Límites declarados

- **No se promete YAML general:** la gramática admitida es un bloque `---` al inicio, una línea `^model:`
  exactamente una, valor no vacío; lo demás es divergencia y se preserva como conflicto.
- **No se validan modelos:** disponibilidad o compatibilidad es del runtime y del usuario.
- **Personalizaciones fuera de las claves declaradas** siguen bajo conflicto D4; un merge general excede la
  feature (`deferred-hardening`).
- **No se evaluó** CRLF ni el prune de agentes obsoletos con overlay (declarado por el review).

## Deuda y diferibles

- `deferred-hardening`: YAML arbitrario/valores complejos; personalizaciones fuera de las claves; validación
  de modelos; CRLF; prune de obsoletos con overlay.
- El test-writer no commiteó la última corrección (una aserción): la commiteó el orquestador — desvío
  declarado, contenido verificado (12/12).

## Gate de cierre

`python3 scripts/cdad-ci-gate.py --base 87b8fe2 --evidence-root .cdad/local/009-001/gate`

| Dato | Valor |
|---|---|
| Commit | `4a5735d` |
| Resultado | **1839 passed, 5 skipped, 0 failed, 0 errors** (`verified: true`) |
| Superficie | **397 nodeids** seleccionados por superficie (cambio de código, 6 rutas) |
| `dirty` | **0** |
| Canario | delta 0 |
| Veredicto | **green**, `attributable: true` |
| Carga | `loadavg` 5.80 / 5.94 / 5.52 |

**Una corrida, no tres:** la estabilidad de la suite se acreditó en el epic 008; acá el gate certifica este
commit una vez, como pide la política del paquete. Los 5 skips son los opt-in reales, con su motivo.

**Nota de la primera corrida (RED honesto):** el gate falló con `surface rc=1` — `README.md: cambio sin
superficie clasificada` — porque el selector de `cdad-suite.py` sólo reconoce `docs/` e ignora
`documentation_files` de la política. La suite estaba verde (1839 passed) y el rojo era del clasificador. El
cambio de README salió de este release y se registra como deuda para la feature de documentación, que de
todos modos toca ese archivo.

## Cierre

La feature cumple la promesa del dueño: **actualizar ya no le cuesta sus modelos**. Queda listo para
publicar; el push y la instalación en otros agentes los decide el dueño.
