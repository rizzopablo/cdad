# RED de review — 003-001-role-packets

Fecha: 2026-09-17  
Rol: test-writer independiente  
Alcance: ocho bloqueantes de `docs/specs/003-001-role-packets/review.md`

## Resultado

Se agregó `tests/test_role_packet_review_regressions.py` con ocho métodos
black-box, uno por bloqueante. No se modificaron producto, documentación,
estado, schemas, assets ni git.

Suite focal ejecutada una sola vez:

```text
python3 -m unittest -v \
  tests.test_role_packets \
  tests.test_role_packet_render \
  tests.test_role_packet_consumers \
  tests.test_role_packet_review_regressions
```

Resultado exacto:

```text
Ran 33 tests in 136.010s

FAILED (failures=8)
```

- Tests vigentes verdes: 25/25.
- Tests nuevos RED: 8/8.
- Errores: 0.
- Skips: 0.
- `BLOCKED`: 0.

## REDs esperados y observados

1. `test_p1_p3_p6_all_task_agents_branch_valid_packet_from_legacy`
   - Contrato: P1/P3/P6.
   - Oráculo: inspecciona los cinco agentes Task instalados y exige una rama
     para metadata válida `---cdad-packet-json` que no recargue `cdad-cycle`,
     más una rama legacy que conserve la carga.
   - RED observado: architect, test-writer, implementer, reviewer y scribe no
     reconocen el marcador canónico; mantienen sólo la directiva incondicional.

2. `test_p4_scoped_exception_rejects_self_consistent_other_epic`
   - Contrato: P4 y ADR-010.
   - Oráculo: crea otro epic, feature, authority, execution, state y delegación
     mutuamente coherentes, conservando `epic-003-single-model`.
   - RED observado: `validate-state` devuelve 0 y hereda la excepción fuera de
     `epic-003-context-efficiency`.

3. `test_p2_internal_symlink_cannot_relabel_implementation_as_docs_or_tests`
   - Contrato: P2, clasificación y resolución de symlinks.
   - Oráculo: apunta `docs/impl-link` y `tests/impl-link` a `../src` e intenta
     declarar `src/secret.py` mediante ambas clases permitidas al test-writer.
   - RED observado: `validate-request` acepta ambos relabels (`docs`, `tests`).

4. `test_p6_install_and_uninstall_reject_source_overlap_and_list_public_targets`
   - Contrato: P6, confinamiento de `CDAD_INSTALL_ROOT` y manifest público de
     destinos.
   - Oráculo: install y uninstall dry-run deben rechazar la raíz fuente antes
     de publicar acciones; en una raíz aislada, uninstall debe enumerar todos
     los agentes y skills públicos instalados.
   - RED observado: install y uninstall aceptan `CDAD_INSTALL_ROOT` igual al
     repo fuente. La comprobación de enumeración aislada también se ejecutó y
     no agregó un fallo independiente al método.

5. `test_p6_omitted_project_root_uses_current_working_directory`
   - Contrato: P6 e interfaz pública del CLI.
   - Oráculo: ejecuta `validate-state` desde el project fixture sin pasar
     `--project-root`.
   - RED observado: código 2 con
     `ERROR: --project-root must be an absolute existing directory: .`.

6. `test_p2_validate_packet_rejects_crlf_byte_variant`
   - Contrato: P2, igualdad byte a byte y terminadores LF.
   - Oráculo: renderiza bytes canónicos, sustituye cada LF por CRLF y valida el
     archivo alterado.
   - RED observado: `validate-packet` devuelve 0 para bytes distintos.

7. `test_p5_metric_without_active_packet_rejects_unbound_identity`
   - Contrato: P5, identidad honesta de métricas.
   - Oráculo: con `active_packet=null`, prueba un packet inventado manteniendo
     rol/subfase válidos y una segunda identidad con rol/subfase inexistentes.
   - RED observado: ambas métricas son aceptadas.

8. `test_p6_explicit_install_root_works_without_home`
   - Contrato: P6, fixture de instalación aislado.
   - Oráculo: ejecuta install dry-run con raíz absoluta existente y elimina
     `HOME` del entorno.
   - RED observado: código 1 con
     `ERROR: Cannot resolve home directory ($HOME is empty or not a directory)`.

## Aclaraciones contractuales aplicadas

- El párrafo de métricas dice que `packet_id` se compara cuando
  `active_packet` existe, mientras P5 exige identidad vinculada al estado. El
  handoff de review resuelve la tensión para este fix: sin `active_packet` no
  existe una fuente estructurada para aceptar una identidad de paquete, por lo
  que la métrica se rechaza.
- La descripción inicial de `CDAD_INSTALL_ROOT` dice que no reemplaza `HOME`,
  pero P6, el review y el handoff exigen que una raíz explícita permita el
  fixture sin depender de `HOME`. El test fija esa conducta explícita.
- Para los agentes Task no se prescribe un formato interno de secciones. El
  test verifica semántica pública: marcador canónico, validez, no recarga en
  el camino packet y carga preservada en el camino legacy.

## Límites respetados

- No se leyó `cdad_packet.py`.
- No se leyó el cuerpo de `install.sh`; sólo se invocó su CLI pública mediante
  instalación/dry-run aislados.
- De los agentes sólo se consultaron las directivas públicas necesarias para
  construir el oráculo y luego las copias instaladas como superficie de
  consumo.
- No se hicieron commits ni operaciones git.
