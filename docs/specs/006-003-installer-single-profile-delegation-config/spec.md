# spec.md — `006-003-installer-single-profile-delegation-config` (APROBADA con enmiendas A-1..A-4)

> Estado: **borrador**. Lo aprueba el usuario explícitamente; el architect no aprueba su propia propuesta.
> Léase junto a `docs/specs/006-003-installer-single-profile-delegation-config/discovery.md` (evidencia) y `docs/epics/epic-006-opencode-concurrency/plan.md` §9.

## 1. Descripción funcional

Cinco resultados, todos observables desde fuera del código:

1. **El instalador y el generador no tienen perfiles ni mapa de modelos.** `install.sh` y `make staging` producen agentes sin `model:`; ninguna superficie instalable fija ni nombra modelos. La elección de modelo deja de ser una decisión de orquestación (plan §9, principio).
2. **La delegación externa toma el modelo solo de un archivo de configuración** (`delegation.json`), por destino y rol. Una clave `model` heredada en la exec-config se ignora con un aviso de deprecación.
3. **El invariante del reviewer de otra familia pasa a ser una verificación de configuración**: un script compara los modelos efectivos de reviewer e implementer y el gate de review declara «invariante no garantizado» cuando no es verificable.
4. **El instalador deja la config de delegación y un ejemplo de credencial del servidor OpenCode** (`opencode-server.env.example`, sin valor), y el adaptador carga la credencial de un archivo con permisos verificados.
5. **La instalación retira sus propios archivos obsoletos** (`pending_removal`) cuando los bytes siguen intactos, y nunca borra lo modificado ni lo ajeno.

## 2. Contrato

### 2.1 Instalador (CLI) — D1

- Flags de perfil `--economical`, `--optimus`, `--premium` → **rechazados**: rc≠0 con diagnóstico que nombra la config de delegación como el lugar donde se elige el modelo. Ningún despliegue ocurre.
- `--basic` → **aceptado, deprecado, sin efecto** (no escribe marcador, no lee ni resuelve perfil). Al usarlo, aviso de deprecación de una línea. Motivo: ≥6 recetas de test usan `install.sh --basic` (discovery §1.6).
- `CDAD_MODEL_PROFILE` y el marcador `.cdad-models-profile` dejan de leerse/escribirse. Derivado de D1: la env se acepta e ignora con el mismo aviso, para no romper recetas locales; alternativa (ignorarla en silencio) marcada al dueño.
- `PROFILE_FLAG`/`MODEL_PROFILE` (`install.sh:101-103`), `resolve_profile`/`validate_profile` (`:978-1001`), `write_profile_marker` (`:1023-1034`), `source scripts/cdad-models.sh` (`:126-133`) y el bloque `PROFILE MISMATCH` (`:1722-1735`) se retiran.
- El manifiesto de staging pierde la clave `profile`; el manifiesto de ownership la conserva solo si ya existía (la clave `profile` del manifiesto de ownership viene de staging, `install.sh:954`).

### 2.2 `delegation.json` (versión 1) — D3

Ruta: `$XDG_CONFIG_HOME/cdad/delegation.json`, o `<INSTALL_ROOT>/.config/cdad/delegation.json` si `XDG_CONFIG_HOME` no está definida. Contenido:

```json
{
  "version": 1,
  "models": { "<destination-id>": { "<role>": "<provider>/<model>" } },
  "credential_env_file": "<path>"
}
```

- `models` por **destino y rol** (roles: `architect`, `test-writer`, `implementer`, `reviewer`, `scribe`).
- `credential_env_file` opcional; default `<config-dir>/cdad/opencode-server.env`.
- El archivo es la **única** fuente de modelo de la delegación externa; sin fallback.

### 2.3 Archivo de credencial — D5

- Formato: subconjunto `KEY=value` + líneas de comentario que empiezan con `#`. Claves `OPENCODE_PASSWORD` y `OPENCODE_SERVER_PASSWORD`. Valor vacío ⇒ tratado como ausente (nunca se manda header vacío; criterio vigente, `cdad_delegate_opencode.py:939-941`).
- Orden: variables de entorno primero; si no hay, el archivo (`credential_env_file` o el default).
- Solo en modo `server` (único punto que usa la credencial: `_preflight_server`, `cdad_delegate_opencode.py:1026-1067`).
- Permisos: se verifica sobre el **fd abierto** (`os.fstat`), patrón TOCTOU de `cdad_packet.py:1275-1320`; se rechaza si `S_IMODE(st_mode) & 0o077` (acepta 600 y 400).
- Diagnóstico 401/403 (reescritura del de `:1056-1060`) autosuficiente: nombres de variables, ruta resuelta, procedencia del valor, y —si aplica— ruta+modo encontrado. Nunca el valor.

### 2.4 Script de verificación de familia — D4

- Nuevo script en `skills/cdad-cycle/scripts/` (nombre propuesto: `cdad_model_family.py`), independiente del runtime y del SO del consumidor. Entradas: los dos modelos efectivos (config de delegación y/o fila durable) y su procedencia.
- Salidas declaradas: `same-family` (igualdad exacta de strings), `guaranteed-by-configuration` (stems distintos), `not-verifiable` (alias de Claude Code / stem no interpretable), `invariant-not-guaranteed` (falta un modelo). Siempre rc=0 (aviso, no gate bloqueante).
- La declaración se escribe en `review.md` (artefacto del reviewer, materializado por el orquestador — ADR-003) y el intento se registra con los campos I8 existentes (`cdad_delegate.py:183-193`), sin inventar campos nuevos.

## 3. Postcondiciones (observables y testeables)

**PD-1 — Instalador y generador sin perfiles** (← AC-1)
- PD-1a. `grep -nE -- '--(economical|optimus|premium)' install.sh` → sin salida.
- PD-1b. `grep -n 'PROFILE' Makefile` → sin la definición `PROFILE ?= optimus`; la receta `staging` (`Makefile:13-14`) invoca `cdad-generate.py` **sin** `--profile`.
- PD-1c. `scripts/cdad-models.sh` no existe y ningún archivo de producto lo referencia (`grep -rn 'cdad-models.sh' install.sh scripts/` → sin salida).
- PD-1d. `build/staging/manifest.json` no contiene la clave `profile`.
- PD-1e. `grep -rc '^model:' agents/cdad-*.md agents/claude-code/*.md` → 0 (hoy 21).
- PD-1f. `python3 scripts/cdad-generate.py --runtime opencode --stack odoo --out <tmp>` sin `--profile` → rc=0; con `--profile X` → rc≠0 con diagnóstico.
- PD-1g. Control negativo: `install.sh --check` sobre una raíz recién instalada → PASS.

**PD-2 — Config de delegación creada por el instalador** (← AC-2)
- PD-2a. Instalación en raíz redirigida sin `XDG_CONFIG_HOME`: se crean `<root>/.config/cdad/delegation.json` (JSON válido, `version: 1`) y `<root>/.config/cdad/opencode-server.env.example`.
- PD-2b. `opencode-server.env.example`: toda línea no-comentario tiene la forma `KEY=` con valor **vacío**; no contiene ningún secreto.
- PD-2c. Con `XDG_CONFIG_HOME=C` definida, los dos archivos se crean bajo `C/cdad/` y **no** bajo la raíz.
- PD-2d. Segunda instalación sobre un `delegation.json` editado por el usuario: bytes **idénticos** (no se pisa); se reporta de acuerdo a la política de conflicto existente (`install.sh:790-857`).

**PD-3 — Fuente única del modelo en la delegación externa** (← AC-3)
- PD-3a. `skills/cdad-cycle/assets/opencode-exec-config.example.json` no contiene la clave `model`.
- PD-3b. Con una exec-config que declara `model: X` y `delegation.json` con `<dest>/<role> → Y`: el argv del destino lleva `--model Y` (el `model` declarado no cambia el efectivo) y aparece un diagnóstico de deprecación de una línea que nombra la ruta de `delegation.json` y cómo migrar.
- PD-3c. Rol sin entrada en `delegation.json`: el argv del destino **no** contiene `--model`; la observación I8 registra `model_configured: null` y `provenance.model_configured` apunta a la config de delegación (no a la exec-config).
- PD-3d. `skills/cdad-cycle/references/cli-delegation.md` § *Configuration* (prosa `:269-270`) deja de listar el modelo como clave de la exec-config.

**PD-4 — Verificación de familia** (← AC-4)
- PD-4a. Reviewer e implementer con el **mismo** modelo efectivo → salida `same-family` (aviso).
- PD-4b. Modelos distintos con stems conocidos (`deepseek-v4-pro` vs `glm-5.2`) → `guaranteed-by-configuration`.
- PD-4c. Falta un modelo, o alias de Claude Code (`sonnet` vs `opus`) → `not-verifiable` / `invariant-not-guaranteed`; **nunca** «garantizada».
- PD-4d. En el caso (c), el texto de `review.md` registra la declaración («invariante no garantizado») y el intento lleva los campos I8.
- PD-4e. El script siempre rc=0 (no bloquea el gate).

**PD-5 — Credencial del servidor** (← AC-5)
- PD-5a. Con fixture de servidor que exige credencial y sin credencial: el diagnóstico nombra `OPENCODE_PASSWORD`, `OPENCODE_SERVER_PASSWORD`, la ruta resuelta, la procedencia del valor y (si aplica) el modo; permite resolverlo **sin otra documentación**.
- PD-5b. `.env` con modo `0644` → **rechazado** con diagnóstico que nombra la ruta y el modo encontrado; no se envía header.
- PD-5c. `.env` con modo `0600` y valor → la credencial se usa; el valor **nunca** aparece en stdout/stderr/argv/registro (oráculo de ausencia con centinela).
- PD-5d. Variable de entorno presente y archivo presente: gana la variable de entorno.
- PD-5e. Línea `KEY=` (valor vacío) ⇒ credencial ausente.

**PD-6 — Retiro de obsoletos propios en la instalación** (← AC-8, D6)
- PD-6a. Instalar sobre una raíz cuyo manifiesto registra `pending_removal` con sha256 igual a los bytes actuales, no redesplegado y no en conflicto → el archivo se **retira** y deja de figurar en el manifiesto; `install.sh --check` no lo reporta como PENDING-REMOVAL.
- PD-6b. `pending_removal` **modificado localmente**: se preserva, se reporta como CONFLICT y sigue registrado (misma regla que `uninstall_by_manifest`, `install.sh:1196-1207`).
- PD-6c. Archivo **no registrado** en el manifiesto: no se toca.
- PD-6d. `--dry-run` lista las bajas sin borrar.
- PD-6e. El python del manifiesto recibe `INSTALL_ROOT` (hoy `install.sh:899` pasa 4 args sin él) y resuelve rutas absolutas y relativas.

**PD-7 — Textos instalables sin perfiles ni modelos** (← AC-7, D7)
- PD-7a. `grep -rE 'deepseek|glm-|qwen|minimax|sonnet|haiku|opus|mofgw/' skills/ agents/cdad-orchestrator.md agents/claude-code/cdad-orchestrator.md` → sin salida (hoy matchean los dos orquestadores: `agents/cdad-orchestrator.md:163-167,176`; `agents/claude-code/cdad-orchestrator.md:5,168-173,181`).
- PD-7b. §2 de `skills/cdad-cycle/SKILL.md` (hoy `:77-82`) y la sección `delegation` de los adaptadores (hoy `sources/agents/adapters/opencode.md:76-83`, `claude-code.md:98-105`) ya no hablan de «perfil»; la familia del reviewer se describe como verificación de configuración declarada cuando no es verificable.

**PD-8 — Aceptación global** (← AC-6)
- PD-8a. `bash install.sh --check` → PASS (salvo DT-8 declarada).
- PD-8b. `make validate` → PASS.
- PD-8c. Suite completa verde, corrida **una vez** por quien cierra (política del paquete).

## 4. Invariantes (verificables)

- **INV-1.** El valor de la credencial nunca aparece en stdout, stderr, argv, `delegation.json`, `review.md` ni en el registro I8; solo centinelas en tests.
- **INV-2.** El instalador nunca borra un archivo modificado localmente ni uno no registrado; solo retira lo propio con sha256 sin cambios.
- **INV-3.** Ningún texto instalable fija modelos (ni `model:` en agentes, ni celdas de modelo en §2 de los orquestadores).
- **INV-4.** Ningún texto instalable nombra `/tmp` (invariante del plan §8 punto 4). Hoy se cumple en `skills/` (grep sin salida); el test lo fija como no-regresión.
- **INV-5.** La familia distinta del reviewer es un invariante: garantizado por configuración o **declarado**; nunca silencio.
- **INV-6.** Con raíz redirigida (`CDAD_INSTALL_ROOT`), la instalación no toca HOME ni `~/.config`.
- **INV-7.** Sin fallback silencioso: ni de modelo (exec-config → default del destino se declara), ni de perfil.

## 5. Decisiones

- **D1** — instalador y generador sin perfiles ni mapa; `--basic` alias deprecado sin efecto; `--economical|--optimus|--premium` rechazados con diagnóstico. `cdad-models.sh` se retira; `Makefile` sin `PROFILE`; `cdad-generate.py` sin `--profile`; manifiesto de staging sin `profile`. (Derivada D1b: `CDAD_MODEL_PROFILE` se acepta e ignora con aviso — marcada.)
- **D2** — ruta nativa: CDAD no fija ni adivina el modelo; consume el configurado si es legible y el observado (fila durable) post-hoc; si no, «no verificable».
- **D3 (DUEÑO)** — estricto: `delegation.json` es la única fuente de modelo de la delegación externa; `model` en la exec-config se ignora con aviso de deprecación de una línea; sin fallback; rol sin entrada → sin `--model`, `model_configured: null`.
- **D4** — familia: igualdad exacta (aviso duro) + token de stem (aviso); alias CC → «no verificable»; faltante → «invariante no garantizado»; script nuevo en `skills/cdad-cycle/scripts/`, aviso no bloqueante; declaración en `review.md` + campos I8.
- **D5** — credencial: env primero; si no, `credential_env_file` o default `<config-dir>/cdad/opencode-server.env`; solo modo `server`; `KEY=value` + `#`; permisos sobre el fd abierto (rechaza bits 077); diagnóstico 401/403 autosuficiente sin el valor; instalador crea plantilla y `.example` sin valor, nunca pisa; ubicación `$XDG_CONFIG_HOME/cdad/` o `<install-root>/.config/cdad/`.
- **D6 (DUEÑO)** — retiro de `pending_removal` propios en la instalación, como unidad propia; preserva y reporta modificados; no toca no registrados; `--dry-run` muestra las bajas; pasa `INSTALL_ROOT` al python del manifiesto. DT-8 queda fuera.
- **D7** — §2 de `SKILL.md` y sección `delegation` de los adaptadores reescritas sin perfiles; los tests acoplados se **reformulan declarando el reemplazo**, no se borran asserts sin declararlo.
- **D8 (cierre, fuera de esta etapa)** — ADR nuevo que reemplaza ADR-007 y la parte de perfiles de ADR-008; lo redacta el cierre.

## 6. Desconocidos y cómo se resuelven

1. **¿El runtime OpenCode honra `agent.<name>.model` sobre el frontmatter de un agente custom?** No verificable desde el repo (`execution.md:200`, observación no investigada). Resolución: CDAD no depende de ello; el modelo efectivo se **declara no verificable** cuando no se observa, y se registra el observado post-hoc (PD-4c).
2. **Relación exacta de contraseña OpenChamber ↔ `opencode serve`** (`plan.md` §9.5; no verificable en repo). Resolución: la afirma el dueño; el texto del diagnóstico cita la procedencia de forma genérica (plan §9.5) y nunca el valor.
3. **¿Puede el manifiesto de staging quedar sin `profile` sin romper consumidores no auditados?** Resolución: grep auditado de consumidores + `test_install_ownership.py:281-308` reformulado; si apareciera un consumidor no auditado, DT nueva.

## 7. Fuera de alcance

- DT-8 (`__pycache__` en staging) — sigue aparte; el retiro de PD-6 no promete árbol «limpio».
- Config de agentes del runtime del dueño (OpenChamber) y del consumidor.
- Redacción del ADR nuevo (D8) — cierre.
- Handoff del consumidor, runtimes nuevos, push/despliegue.

---

## 8. Enmiendas del orquestador al aprobar (HITL delegada, 2026-10-18)

- **A-1 (D1b resuelta).** `CDAD_MODEL_PROFILE` se acepta e ignora con el mismo aviso de deprecación de una línea que `--basic` (coherente con INV-7: nada silencioso).
- **A-2 (`destination-id`).** El id de destino es el identificador del runtime de destino del adaptador (`opencode` para el adaptador OpenCode); la spec y `cli-delegation.md` lo definen así y la plantilla lo usa.
- **A-3 (archivos de config = datos del usuario).** `delegation.json` y `opencode-server.env.example` se crean solo si no existen y **no** se registran en el manifiesto de ownership: ni `--uninstall` ni el retiro de PD-6 los borran nunca. PD-2d se lee así: segunda instalación → bytes idénticos y aviso de que ya existe; no es CONFLICT.
- **A-4 (unidad única para el `.env.example`).** La creación de los dos archivos de config la hace U4; U6 no toca `install.sh`.

Status: Approved by orquestador Claude (HITL delegada por Pablo, epic-006) on 2026-10-18
