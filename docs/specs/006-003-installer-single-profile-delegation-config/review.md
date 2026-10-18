Tengo la especificación aprobada. Ahora voy a revisar la implementación. Comenzando con las comprobaciones observables de la especificación (PD-1, PD-3, PD-7) y los artefactos principales.
Las comprobaciones observables de la spec (PD-1, PD-3a, PD-7a) se han aprobado. Ahora revisaré la implementación principal — install.sh.
install.sh leído por completo. Ahora los scripts de delegación (fuente única de modelo, ruta de credenciales).
Ahora las pruebas de eliminación/aceptación y las pruebas acopladas reformuladas (regla A-1).
# Review — 006-003-installer-single-profile-delegation-config (etapa 4)

**Objeto juzgado:** diff `2b43516..HEAD` (HEAD = `401d951`) contra la spec aprobada `docs/specs/006-003-installer-single-profile-delegation-config/spec.md` (PD-1..PD-8, INV-1..7, D1..D7, enmiendas A-1..A-4 §8, A-5 §9 — que retira la verificación de familia y PD-4) y el plan con A-6. **Read-only: no edité ni aprobé nada; write_scope respetado (vacío).**

**Verificación del autor (qué corrió, según reports):** RED/GREEN/testfix por unidad U1..U8 con commits trazables; suite completa por quien despacha (`deb8320`): `pytest tests/` → **1166 passed / 1 failed / 5 skipped** (el failed es de 006-001, corre 3/3 en aislamiento, carrera de fixtures documentada en `execution.md` última sección); `make validate` 168/1 (F011 = drift de la instalación del dueño, anterior a este diff) y 169/0 redirigido a la instalación de aceptación de U8.

**Comandos de verificación propios (todos en `<repo>`, salida de los PD observables):**

```
git log --oneline 2b43516..HEAD ; git diff --stat 2b43516..HEAD
grep -nE -- '--(economical|optimus|premium)' install.sh                  → sin salida (PD-1a ✓)
grep -n 'PROFILE' Makefile                                              → sin salida (PD-1b ✓)
grep -rn 'cdad-models.sh' install.sh scripts/ skills/ sources/ agents/   → sin salida (PD-1c ✓)
grep -n '"profile"' build/staging/manifest.json                         → sin salida (PD-1d ✓)
grep -rc '^model:' agents/cdad-*.md agents/claude-code/*.md             → todo 0 (PD-1e ✓)
grep -n 'model' skills/cdad-cycle/assets/opencode-exec-config.example.json → sin salida (PD-3a ✓)
grep -rEn 'deepseek|glm-|qwen|minimax|sonnet|haiku|opus|mofgw/' skills/ agents/*orchestrator* → sin salida (PD-7a ✓)
ls skills/cdad-cycle/scripts/  → cdad_model_family.py NO existe (A-5 ✓)
git show --stat 797b935 / df90b41 / 516149b  → A-4: U6 no toca install.sh ✓
```
Lecturas completas: `install.sh` (1908 líneas), `cdad_delegate.py`, secciones de credencial/despacho de `cdad_delegate_opencode.py`, diffs de tests reformulados. No leí `tests/.sensitive-patterns.local` ni `~/.config/cdad/*`.

---

## Blockings

**Ninguno.** Todas las postcondiciones observables que pude verificar por grep/oráculo pasan; no encontré camino que comprometa el resultado, la evidencia o el uso previsto.

## Optionals

**O-1 · Required · Bucket: h · Verdict: OPTIONAL (deuda) — credencial de entorno vacía envía un header Basic vacío, contra el criterio declarado en §2.3.**
Provenance: `skills/cdad-cycle/scripts/cdad_delegate_opencode.py:957-960` (`os.environ.get` sin chequear vacío) + `:1158-1161` (`if password is not None` → header). Spec §2.3 (`spec.md:44`): «Valor vacío ⇒ tratado como ausente (nunca se manda header vacío; criterio vigente, `cdad_delegate_opencode.py:939-941`)» — la cita del criterio apunta justo a `_preflight_password`, y con `OPENCODE_PASSWORD=""` exportado el valor llega como `""` (no `None`) y se manda `Basic b64("opencode:")`. El caso `KEY=` del **archivo** sí está bien implementado (`:996-998`, PD-5e ✓). Consecuencia: fail-closed (401 → blocked con diagnóstico), pero la distinción ausente/rechazada se corrompe y el diagnóstico orienta al archivo cuando el problema está en la env. No es regresión del diff (el código viejo tenía el mismo hueco; la spec lo codificó como criterio). **Cierre verificable:** tratar `""` de entorno como ausente (o declarar la excepción en `cli-delegation.md`) + oráculo PD-5 con env vacía en `tests/test_006_003_u6_server_credential.py`.

**O-2 · Required · Bucket: m · Verdict: OPTIONAL (deuda) — el lector de `delegation.json` resuelve por HOME, no por INSTALL_ROOT; divergencia silenciosa en raíz redirigida.**
Provenance: `skills/cdad-cycle/scripts/cdad_delegate.py:100-106` (`Path.home()/.config` si XDG unset) vs `install.sh:1123-1125` (instala en `<INSTALL_ROOT>/.config/cdad`). Spec §2.2 (`spec.md:28`): «`<INSTALL_ROOT>/.config/cdad/delegation.json` si XDG no está definida». Mecanismo: instalación con `CDAD_INSTALL_ROOT=<root>` + XDG unset (config soportada, INV-6) → el usuario configura el modelo en `<root>/.config/cdad/delegation.json` (único lugar que el instalador le nombró), el despacho lee `<HOME>/.config/cdad/delegation.json`, no existe → «missing file = empty configuration» (`cdad_delegate.py:156-157`) → sin `--model`, sin aviso. El modelo configurado se ignora en silencio — escape observable de D3 en esa configuración. En el uso primario (root == HOME, y en todos los tests U4/U8, que redirigen HOME y XDG juntos) coincide y pasa. Es una tensión interna de la spec (el lector no tiene entrada de INSTALL_ROOT). **Cierre verificable:** decisión del dueño registrada (que el lector honre `CDAD_INSTALL_ROOT`, o declarar HOME como base del lector en §2.2 y `cli-delegation.md`) + test del escenario raíz-redirigida-con-HOME-real.

**O-3 · Optional-Consider · Bucket: m — tensión INV-6 ↔ PD-2c cuando XDG_CONFIG_HOME está definido en el host.**
Provenance: `install.sh:1123-1125` + `spec.md:116` (INV-6) y `spec.md:70` (PD-2c). Mecanismo: instalación con raíz redirigida y `XDG_CONFIG_HOME` del host definido → los dos archivos de config se crean en el XDG real (típicamente bajo `~/.config`), fuera de la raíz: INV-6 al pie de la letra se rompe en esa configuración. La implementación sigue PD-2c fielmente; los tests evitan el caso redirigiendo XDG al tempdir (`test_006_003_u8_acceptance.py:271-277`), así que la combinación no está fijada. **Cierre:** el dueño declara la precedencia (PD-2c gana por diseño, o XDG se ignora con aviso cuando hay raíz redirigida) y un test la fija.

**O-4 · Nit · Bucket: h — diagnóstico 401 imprime «credential file None» cuando la credencial vino del entorno.**
Provenance: `cdad_delegate_opencode.py:1069` (`path: None` en la rama environment) + `:1088-1098` (interpolación directa de `credential["path"]`). Mecanismo: password en env (incorrecta) → 401 → el texto dice «or in the credential file None». PD-5a sigue cumplido para el caso ausente (la ruta siempre se resuelve cuando se consultó el archivo). **Cierre:** omitir la cláusula del archivo cuando `path is None`, o nombrar la fuente usada.

**O-5 · Nit · Bucket: h — `owned_removal_state` retira sin comparar bytes cuando el sha registrado está vacío.**
Provenance: `install.sh:654` (`[ -z "$recorded" ] → removable`). El instalador siempre registra sha (`record_owned`, `:666`), así que solo es alcanzable con un manifiesto editado a mano; INV-2 al pie de la letra («solo retira lo propio con sha256 sin cambios», `spec.md:112`) no se satisface para ese registro degenerado, ahora heredado por el prune nuevo de U7. **Cierre:** exigir sha no vacío para `removable` (vacío → `modified`/conservar) o declarar la regla histórica explícitamente.

**O-6 · Optional-Consider · Bucket: l — XDG_CONFIG_HOME relativo.**
Provenance: `install.sh:1124` y `cdad_delegate.py:105`. Un XDG relativo (inválido por la spec XDG) crea/resuelve rutas relativas al cwd de cada proceso; ambos lados solo coinciden si el cwd coincide. **Cierre:** validar absolutidad con diagnóstico (patrón ya usado para `CDAD_INSTALL_ROOT`, `install.sh:531-536`).

**O-7 · FYI · Bucket: m — suite con 1 failed y `make validate` con F011 en este checkout.**
Provenance: `execution.md` última sección (`deb8320`): el failed es `test_006_001_t1_selection.py::test_pd2_connection_refused_is_transport_error` (3/3 en aislamiento, carrera de fixtures conocida, no es regresión de 006-003); F011 es drift ambiental previo (169/0 redirigido). PD-8c es obligación del **cierre**: quien cierre debe correr la suite una vez y resolver el 1 failed (re-corrida o arreglo de fixtures) para declarar «suite verde».

---

## Abstentions

1. **Honra el runtime `agent.<name>.model` sobre el frontmatter de un agente custom OpenCode** (spec §6.1): declarado no-verificable desde el repo por la propia spec; CDAD no depende de ello. No juzgable aquí.
2. **Consumidores externos no auditados del manifiesto de staging sin clave `profile`** (spec §6.3): la resolución de la spec fue grep auditado + reformulación de `test_install_ownership.py:281-308`; no puedo afirmar la inexistencia de un consumidor fuera del repo. La DT declarada por la spec cubre el caso.
3. **Re-derivar la suite completa (30 min) o `make validate` completo**: política del paquete — la suite la corre una vez quien cierra, y no corresponde re-correrla en review; los resultados citados provienen de los reports y `execution.md` declarados, que no re-verifiqué por ejecución.

---

## Resumen: 0 bloqueantes, 7 opcionales, 3 abstenciones

## Juicios por punto pedido

1. **Credencial (INV-1, PD-5):** ✓ sin hallazgo bloqueante. La credencial viaja solo por header `Authorization` de `urllib` (`:1158-1161`), nunca por argv ni shell; el diagnóstico 401/403 nunca interpola el valor (solo ruta, modo, procedencia genérica — genérica porque lo permite §6.2); el detalle de error de lectura es `strerror` sin contenido (`:1051-1053`); el I8 no lleva credencial (oráculo U8 con centinela sobre argv/stdout/stderr/diagnosis/I8/delivery/`delegation.json`, `test_006_003_u8_acceptance.py:558-618`, con no-vacuidad). Permisos verificados sobre el fd abierto (`os.fstat`, `:1029-1034`, acepta 600/400, rechaza bits 077, PD-5b ✓). El diagnóstico 401/403 es autosuficiente (nombra ambas variables en orden, ruta resuelta, procedencia y `chmod 600` si aplica) — deudas cosméticas: O-1 y O-4.
2. **Retiro de obsoletos (INV-2, PD-6, A-3, A-6):** ✓. El prune solo itera registros del manifiesto previo (`:1205-1224`); un archivo no registrado jamás se lee ni toca (PD-6c ✓); modificado → preservado + CONFLICT + sigue registrado vía KEPT (`:1243-1247`, `pending.update(kept)` `:1017`; PD-6b ✓); `--dry-run` anuncia las bajas sin borrar (PD-6d ✓); el python del manifiesto recibe INSTALL_ROOT y resuelve absolutas y relativas (PD-6e ✓); los archivos de config de usuario nunca se registran (A-3 ✓, test dedicado `test_a_3_config_files_are_never_owned_removed_nor_registered`), así que ni prune ni `--uninstall` pueden borrarlos. La cuenta del Verify se deriva del staging **en ambos lados** (esperado `staged_agent_count`, observado `count_manifest_agents_installed`, `:240-275, :1768-1775`) — conservó su poder de detectar instalación incompleta, y el hueco inicial del lado observado fue detectado y corregido en el GREEN (u7-green.md:40). Residual menor: O-5.
3. **Fuente única del modelo (D3, PD-3):** ✓. El adaptador resuelve el modelo solo vía `cdad_delegate.delegation_model` (`:1965-1973`); el `model` de la exec-config se ignora con aviso de una línea que nombra la ruta y cómo migrar (`cdad_delegate.py:174-185`, disparado en `:373-374` antes de despachar); un `delegation.json` inválido (JSON malformado, versión ≠ 1, sin `models`) falla ANTES de despachar con diagnóstico claro — `DelegateError` rc=2 en la interfaz (`:372` antes de `:378`, `:399-401`) y `blocked_before_dispatch` en el adaptador (`:1969-1973`). Rol sin entrada → sin `--model`, `model_configured: null` con provenance de la config de delegación (PD-3c ✓, `:148-171, :278-292`). Deuda: O-2 (divergencia silenciosa en el escenario raíz redirigida + HOME real).
4. **Sin perfiles ni modelos (PD-1, PD-7, INV-3, A-5):** ✓. Todos los greps de PD-1a..e, PD-3a y PD-7a limpios; `cdad_model_family.py` no existe; los requisitos de familia retirados de `SKILL.md`, `sources/roles/*`, adaptadores y agentes generados (verificado por grep y por el oráculo U5' con exclusiones declaradas una por una). La observación I8 se conserva (`model_configured`/`model_reported` + provenance) y los demás invariantes anti-sesgo quedan intactos (`sources/roles/orchestrator.md` diff, test 6 de U5'). Las exclusiones declaradas (`verdict-tuple.md` +1 por familia, `handoff-prompts.md:499,501`) son puntaje de confianza/preferencia («ideally»), no exigencia de despacho — defendible bajo A-5, registrado aquí como revisado y aceptado.
5. **Reformulación de tests acoplados (A-1):** ✓ sin pérdida silenciosa de cobertura. Revisados U1 (constantes PROFILE retiradas con declaración), U2/U3, U4, U5' (testfix del falso positivo documentado con barrido auditado), U7 testfix (B3 reformulada por D6/A-6 conservando el recorrido completo y agregando la variante modificada), T4 (`003-002`, `005-005`, `005-004`), `006-001 t1_selection` (assert de `--model` invertido con config de delegación redirigida), `validate-odoo-specialization.sh` P1.reviewer (invertido con reemplazo declarado por A-5), `validate-consistency.sh` F001/F008 (presencias invertidas a ausencias) y `test_004_001_acceptance_matrix.py` (que incluso **gana** cobertura: ausencia de `model:` en los 11 agentes × 2 runtimes). Todos declaran qué afirmaban y por qué el contrato lo reemplaza; ningún assert cayó sin declaración.
6. **Uso previsto:** ✓. Con solo los artefactos instalados, un usuario nuevo tiene: el mensaje del instalador al crear la config (`install.sh:1141,1164`), el `--help` (delegation.json como único lugar del modelo, `:330-355`), `opencode-server.env.example` con instrucciones cp/chmod 600 y procedencia de la contraseña (`:1150-1163`), `cli-delegation.md` § Configuration completa (ruta, formato v1, roles, orden env→archivo, modos, `credential_env_file`, `destination-id` por A-2) y el § «Model choice» del orquestador instalado (`agents/cdad-orchestrator.md:179`). Residual: O-2 (escenario raíz redirigida).

**Deuda para el cierre (no bloquea la review):** O-1, O-2, O-3 requieren decisión del dueño o test; O-7 se resuelve corriendo la suite en el cierre. Ninguno compromete el resultado observable declarado por PD-1..PD-8 en la configuración primaria de uso.

---

## Disposición del orquestador (HITL delegada, 2026-10-18)

0 bloqueantes. Por el criterio vigente (MVP: se bloquea solo lo que compromete el resultado, la evidencia o el uso previsto), se corrigen en **una sola ronda de review-fix** los opcionales baratos que contradicen la letra de la spec o confunden el diagnóstico:
- **O-1:** una credencial de entorno vacía se trata como ausente (§2.3).
- **O-2:** el lector de `delegation.json` y de la credencial resuelve la misma base que el instalador (honra `CDAD_INSTALL_ROOT` cuando está definida, como §2.2). Es la solución general: una sola regla de ubicación para el que escribe y el que lee.
- **O-4:** el diagnóstico no imprime «credential file None»; nombra la fuente usada.
- **O-5:** un registro con sha vacío no se retira; se conserva.

Pasan a deuda: **O-3** (precedencia XDG del host frente a la raíz redirigida; caso raro, la decide el dueño) y **O-6** (XDG relativo). **O-7** se cierra con la suite del cierre.
