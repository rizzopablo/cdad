# plan-review 003 — 010-000 Raíces equivalentes en continuidad

**Dictamen: no encontré bloqueantes. B1 está cerrado, y O1–O4 están resueltos o ya no aplican.** Esto es una revisión y no una aprobación: no marco el borrador como aprobado ni autorizo la implementación. La decisión es tuya.

- **Objeto revisado:** `docs/specs/010-000-continuity-relative-root/spec.md`
- **sha256:** `97b1c65258a87f13b850acd54d3773bcffad80b027e73fb73ccb6526ccc7ea82`. Lo calculé y coincide con el contrato.
- **Forma:** spec, kind `draft-plan`, commit null. HEAD observado: `fa4e6bc`.

## Validación del paquete (ruta A)

Comparé por bytes todo el prompt recibido, desde el marcador hasta el final, contra el render canónico.

| Comprobación | Resultado |
|---|---|
| `validate-request` (contexto `.cdad/executions/exec-010-000-continuity-relative-root-001/execution.json`) | rc=0 |
| `validate-packet` (REQUEST.json + PACKET.md) | rc=0 |
| sha256 del render canónico | `488164701ec9855b2ffafdfcd2c4c57655505275c1fa078f371bf018c60a72e3` (6982 bytes) |
| `cmp` del render contra `PACKET.md` | idénticos |
| `cmp` del prompt recibido contra el render | **BYTE-IDENTICAL**, mismo sha256 `4881647…72e3` |

Límite de esta comprobación: el lado "recibido" es mi transcripción literal del prompt a un archivo mediante heredoc. No es una captura cruda del canal. La hice antes de ver el render completo; solo había visto sus primeros 300 bytes y el `od` de los últimos 200. Por eso es poco probable que haya acercado mi copia al texto canónico. Usé los archivos temporales `/tmp/recv003.md` y `/tmp/render003.md`, y ya los borré.

## Cierre de la revisión anterior

- **B1 (PC-07 prometía un rechazo por symlink en `update.references` que no existe): CERRADO.**
  - `spec.md:69–74` enumera las entradas que se controlan por resolución.
  - `:78` declara que `update.references` solo tiene control léxico y que no se promete rechazar symlinks exteriores.
  - `:31`, `:108`, `:130` y `:136` lo dejan registrado en `deferred-hardening`, sin contradicciones con el resto de la spec.
  - Cada entrada de la lista pasa realmente por `_project_path`, y lo comprobé en `cdad_packet.py`:
    - `policy.path`: `:1254`
    - `path_policy`: `:330`, `:313`, `:512`
    - `temporary_roots`: `:424`, `:528`, `:1377`
    - `raw_path` y selectores de clasificación: `:345–356`, `:416–417`
    - scopes: `:1361`
    - directorio contractual: `:1370`, `:1423`
    - `contract.path`: `:1695/1698`
    - `contract.spec_path`: `:1719`
    - `inputs[].path`: `:1756`
    - `authority_ref`: `:575`, `:1210`
  - El control léxico que describe `:78` corresponde al código: `_normalize_reference`, `cdad_continuity.py:238–247`.
  - **Conclusión:** la promesa se puede verificar y ya no obliga a GREEN a añadir un containment nuevo.
- **O1 (`checkpoint` no estaba cubierto): RESUELTO.** Ahora lo cubren `:21–22`, PC-01 `:43`, PC-02 `:47`, PC-04 `:57` y la aceptación §5.3.
- **O2 (`--basic` obsoleto): RESUELTO.** `:91–92` ya no lo incluye. `CDAD_INSTALL_ROOT` y `CDAD_SKILL_EXTRA_DIRS` existen en `install.sh:49,87,518–525`.
- **O3 (raíz expresada mediante symlink): RESUELTO.**
  - `:15` dice que la equivalencia se decide por resolución, y §5.5 lo hace exigible.
  - Eso concuerda con el código: `_project_path` compara un candidato ya resuelto (`resolve()`) contra `project_root` (`cdad_packet.py:288–289`).
  - El CLI del paquete ya sigue ese criterio (`:1297–1301`), y el de continuidad también (`cdad_continuity.py:3175`).
  - Lo que hoy rompe es `_run_write`: reconstruye `Path(args.project_root)` sin resolver (`:1157`), y `plan_write` recibe la raíz tal cual (`:1012–1038`). Esa es la superficie que la spec cubre.
- **O4 (el informe del autor estaba dentro del contrato): RESUELTO.** Ese bloque ya no está. §7 (`:138–153`) solo contiene referencias de código y una nota explícita: "pendiente de ejecución, no presentado como resultado".

## Hallazgos

Ninguno con confianza ≥80% que deba registrarse, ni bloqueante ni opcional. No añado hallazgos para llenar una cuota.

## Comprobaciones sin hallazgo (riesgo examinado)

- **Abstención anterior sobre `render_packet` y la raíz:** la única dependencia de la raíz es `_plan_task_sections`, que lee el plan mediante `_project_path` (`cdad_packet.py:5165`).
  - Con una raíz relativa sin resolver, ahí también aparece el falso escape. Eso entra en la corrección de la raíz que exige PC-02.
  - El render no incrusta rutas de la raíz en los bytes, así que PC-02 (`verify_published_packet`) es alcanzable.
  - `verify_published_packet` devuelve los JSON cargados (`:1917–1974`), que no contienen la raíz.
- **PC-04:** `_replay_envelope` (`cdad_continuity.py:985–1004`) y la ruta de publicación (`:1120–1150`) no incorporan la raíz absoluta a campos portables. La raíz solo aparece en los destinos físicos `_body_path` y `_head_path`, que PC-02 trata como "destinos físicos equivalentes".
- **PC-08:** la vía `make staging` (`Makefile:10–13`) más el instalador con raíz aislada existe. Tiene un precedente en `tests/test_role_packet_consumers.py:40–58`.
- **Tabla de decisiones / ADRs:** ninguna decisión vigente entra en conflicto. ADR-038 (admisión en cada frontera invocable y comparación por bytes) es coherente con PC-06. ADR-002 y ADR-017 hablan de symlinks y raíces de activación en otro ámbito.

## Abstentions

- No ejecuté `begin`/`checkpoint` con una raíz relativa para reproducir el RED de §5.2. Doy por buena su viabilidad solo por la lectura del código (`:1157` frente a `_project_path`). La reproducción corresponde a la etapa 3.
- No ejecuté staging ni la instalación aislada.
- No juzgo si el límite de la comparación del prompt recibido (transcripción mía, no captura cruda del canal) es suficiente para el control que pide el objetivo. Lo dejo declarado arriba para que lo decidas tú.

## Evidencia requerida

- **Archivos modificados:** ninguno en el repo. Solo los dos temporales en `/tmp`, ya borrados.
- **Commit:** ninguno.
- **Comandos:**
  - `sha256sum` sobre la spec.
  - `cdad_packet.py validate-request|validate-packet|render --project-root . --execution-context <execution.json> --request <REQUEST.json> [--packet <PACKET.md>]`.
  - `cmp` del render contra `PACKET.md` y del prompt recibido contra el render.
  - Lecturas con `sed`/`grep` de `cdad_packet.py`, `cdad_continuity.py`, `install.sh`, `Makefile`, `tests/test_role_packet_consumers.py` y `docs/adr/`.
  - `git status --short` al final: sin cambios respecto al inicio (`?? …/discovery.md`).
- **Suite completa:** no la ejecuté, conforme a la política común.
