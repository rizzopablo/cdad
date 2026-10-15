# Tercera review final — 003-001-role-packets

Reviewer model: `GPT-6 (Codex)`; familia distinta de los implementadores
`gpt-5.6-sol` declarados en `reviewfix-green.md` y `extradir-green.md`.

Veredicto Stage 4: **CHANGES_REQUESTED**.

## Alcance y evidencia

- HEAD revisado: `393e952`; producto: `cc81e95`. El tramo posterior al producto
  sólo modifica `docs/epics/epic-003-context-efficiency/handoff.md`.
- Se inspeccionaron el handoff vigente, `review.md`, `review-2.md`,
  `extradir-red.md`, `extradir-green.md`, el método B4, el diff correctivo y el
  `install.sh` resultante.
- Se reutilizó la evidencia vigente de
  `docs/specs/003-001-role-packets/extradir-green.md:13-23`: método B4 verde,
  `Ran 33 tests in 107.105s` / `OK`, sin errores, skips ni `BLOCKED`. No se
  repitió la suite.
- Separación TDD preservada: `a9c615a` agregó/amplió el RED en
  `tests/test_role_packet_review_regressions.py`; `cc81e95` modificó
  `install.sh` y no tocó `tests/**`. Ambos commits también materializaron su
  evidencia/estado documental, sin mezclar tests con implementación.
- Ante una duda material descubierta por inspección se ejecutó un único probe
  black-box con `--dry-run`, mediante un symlink temporal fuera del repo. El
  árbol permaneció limpio y no se ejecutó uninstall real.

## Estado focal de B4

Los casos escritos por el RED residual sí están cerrados en la invocación física
normal del repo:

- `guard_source_overlap` agrega los ocho destinos de `CDAD_INSTALL_ROOT` y cada
  destino efectivo `<extra>/<skill>` producido por el mismo
  `extra_skills_dirs`; luego canonicaliza cada destino antes de compararlo con
  el source (`install.sh:424-447`).
- `guard_install_root` llama ese guard desde la entrada común y `main` lo ejecuta
  antes de las ramas de check, uninstall e install, incluidos sus modos dry-run
  (`install.sh:450-467,972-1009`).
- Install, check, manifest de uninstall, resumen y guard recorren el mismo parser
  de extras (`install.sh:211-226,436-441,610-617,698-724,828-899,930-966`).
- B4 prueba raíz física solapada, extra directo `<repo>/skills`, extra symlink al
  mismo source y extra temporal aislado; para el control aislado comprueba
  install real, install dry-run, check, uninstall dry-run y enumeración de todos
  los destinos extra en ambos dry-runs
  (`tests/test_role_packet_review_regressions.py:230-360`).

El cierre no es completo porque la identidad del source usada en la comparación
no está canonicalizada.

## Bloqueantes

### 1. Un alias symlink del repo elude el guard de solapamiento y vuelve a exponer el source

Veredicto: **BLOQUEANTE**  
Bucket: **h**  
Severidad: **Critical — riesgo destructivo verificable**  
Problema: `SCRIPT_DIR` se obtiene con `pwd` lógico, por lo que conserva el
spelling de un directorio symlink (`install.sh:19-21`). En cambio, cada destino
gestionado se convierte a ruta física mediante `cd -P` antes de compararlo
(`install.sh:403-445`). Si el instalador se invoca como
`/tmp/.../repo-link/install.sh`, donde `repo-link` apunta al repo, el lado fuente
de `paths_overlap` queda como el alias `/tmp/.../repo-link` y el destino como la
ruta física del repo. La comparación textual no detecta que son el mismo árbol.

El probe focal usó `CDAD_INSTALL_ROOT=<repo físico>`, invocó el instalador por
ese alias y obtuvo:

```text
status=0
DRY-RUN COPY skills/cdad-cycle -> <repo físico>/.config/opencode/skills/cdad-cycle
DRY-RUN COPY skills/cdad-cycle -> <repo físico>/.agents/skills/cdad-cycle
DRY-RUN COPY skills/cdad-cycle -> <repo físico>/skills/cdad-cycle
```

Por tanto falla el requisito de rechazar antes de publicar acciones. La misma
comparación se ejecuta una vez antes de todas las ramas (`install.sh:972-1009`),
así que check y uninstall comparten la evasión. En uninstall, el manifest incluye
los skills públicos/extra y `uninstall_cdad` entrega cada entrada a `rm -rf`
(`install.sh:698-724,749-755`); no se ejecutó esa variante destructiva.

El test no cubre esta identidad porque `REPO_ROOT` se resuelve físicamente y
`INSTALLER` deriva de esa ruta (`tests/test_role_packets.py:17-18`); todas las
invocaciones B4 llaman esa ruta física (`tests/test_role_packet_review_regressions.py:33-53`).

Ubicación: `install.sh:19-21,403-445,698-724,749-755,972-1009`;
`tests/test_role_packets.py:17-18`;
`tests/test_role_packet_review_regressions.py:33-53,230-360`;
remediación exigida originalmente en
`docs/specs/003-001-role-packets/review.md:61-68`.

Sugerencia: fijar una identidad física del source desde el inicio, por ejemplo
obteniendo `SCRIPT_DIR` con `pwd -P`, y usarla para `SOURCE_*` y todas las
comparaciones. Agregar a B4 una invocación del instalador a través de un symlink
al directorio del repo, con `CDAD_INSTALL_ROOT=<repo físico>`, y exigir rechazo
sin ninguna línea de acción para install dry-run, check y uninstall dry-run.

## No regresión de los otros siete bloqueantes

**Confirmada por inspección.** Entre el GREEN consolidado `bea0338` y el producto
`cc81e95`, fuera de tests/docs sólo cambian diez líneas de `install.sh` dentro de
`guard_source_overlap`; no cambian los cinco agentes receptores ni
`skills/cdad-cycle/scripts/cdad_packet.py`.

| Bloqueante original | Estado | Evidencia |
|---|---|---|
| B1 packet/legacy en cinco receptores | **CERRADO, sin regresión** | Los agentes no cambiaron desde `bea0338`; conservan las ramas mutuamente excluyentes registradas en `review-2.md:19`. |
| B2 ADR-010 limitado al epic | **CERRADO, sin regresión** | La CLI no cambió; conserva `AUTHORIZED_SINGLE_MODEL_EPIC` y el rechazo cross-epic de `review-2.md:20`. |
| B3 relabel por symlink interno | **CERRADO, sin regresión** | La CLI no cambió; conserva clasificación y containment sobre paths resueltos de `review-2.md:21`. |
| B5 default cwd | **CERRADO, sin regresión** | La CLI no cambió; conserva `Path.cwd().resolve()` cuando se omite el flag, según `review-2.md:23`. |
| B6 igualdad de bytes/CRLF | **CERRADO, sin regresión** | La CLI no cambió; conserva render binario y comparación de `read_bytes()`, según `review-2.md:24`. |
| B7 métrica sin `active_packet` | **CERRADO, sin regresión** | La CLI no cambió; conserva el binding obligatorio registrado en `review-2.md:25`. |
| B8 raíz explícita sin `HOME` | **CERRADO, sin regresión** | `guard_install_root` sigue llamando `guard_home` sólo cuando `CDAD_INSTALL_ROOT` no está definido (`install.sh:450-467`); el nuevo recorrido de extras no lee `HOME`. |

## Opcionales retenidos

### 2. Schemas públicos más permisivos que la CLI

Veredicto: **OPCIONAL**  
Bucket: **h**  
Problema: permanece el hallazgo de `review-2.md:58-63`; el correctivo B4 no toca
schemas. No bloquea este gate.

Ubicación: `skills/cdad-cycle/assets/execution-context.schema.json:32`;
`skills/cdad-cycle/assets/packet-request.schema.json:12-21`;
`skills/cdad-cycle/assets/rendered-packet.schema.json:12-18`.

### 3. Versión mínima de Python no publicada

Veredicto: **OPCIONAL**  
Bucket: **h**  
Problema: permanece el hallazgo de `review-2.md:65-70`; queda fuera del gate
inmediato.

Ubicación: `README.md:3-7`; `install.sh:470-473`;
`skills/cdad-cycle/scripts/cdad_packet.py:4-7,479-486`.

## Abstenciones

### 4. E2E con runtime OpenCode real

Veredicto: **ABSTENER**  
Bucket: **h**  
Motivo: la aceptación automática completa continúa diferida por contrato; no se
usa para aprobar ni bloquear este cierre.

Ubicación: `docs/specs/003-001-role-packets/spec.md:649-651`;
`docs/specs/003-001-role-packets/review-2.md:72-79`.

## Resultado

**1 bloqueante · 2 opcionales · 1 abstención. CHANGES_REQUESTED.**

Los casos B4 explícitos añadidos en `a9c615a` están verdes, el extra aislado
mantiene instalación/check/listado/manifest coherentes y B1-B3/B5-B8 no
regresionan. Stage 4 no puede aprobarse mientras una invocación por alias del
repo permita que destinos físicos solapados pasen el guard y publiquen acciones
contra el source.
