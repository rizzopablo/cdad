# Auditoría 019-002: cinco fallos de la suite del epic

**Paquete (ruta C):** válido. `REQUEST.json` y `PACKET.md` coinciden byte a byte con `cdad_packet.py render`, y `validate-packet` devolvió rc=0. La spec tiene el sha256 declarado (`dc0800fa…`).

**Archivos modificados:** ninguno. No hay commit, porque en la auditoría no se editan tests.

**Qué leí y qué no:**
- No leí código de implementación. Leí la spec, los tests y los mensajes de aserción al ejecutarlos.
- No leí `.cdad/orchestration/epic-019/019-epic-tests-suite.log`, porque queda fuera de mi alcance de lectura. Reproduje yo los cinco fallos.
- Usé `git show … | grep -c` para contar patrones en commits del README. Con `git worktree` (en `/tmp`, ya removido) corrí tests sobre el commit anterior a 019-002 (`3322aaf3^`).
- No leí `docs/suite-maintenance.md`, por el mismo motivo. Un grep de estos nodeids sobre ese archivo no devolvió nada, así que el delta de inventario queda para el orquestador.

**Comandos y resultado:**
- `python3 -m pytest -q <5 nodeids>`: los 5 fallan, todos con `AssertionError` (el de INV-6 es un `pytest.fail` explícito dentro del test).
- Mismos tests sobre `3322aaf3^` (justo antes de 019-002), junto con los demás de `t4_readme` y `t6_owner_reviewfix`: 4 fallan y 4 pasan. `test_pd10…` pasa en esa base.

## Hallazgo central

Los cinco fallos tienen **dos causas distintas**. Solo una es de 019-002.

| Nodeid | Causa | ¿La introdujo 019-002? |
|---|---|---|
| `t2_intake::test_pd10_intake_wiring_uses_installed_cli` | La línea 157 de `sources/roles/orchestrator.md` nombra `re-entry.md` sin `<skill-dir>` (fragmento: «`re-entry.md`), also when no consultation was warranted — readiness is…»). Esa línea apareció con 019-002 (PC-3, readiness sin consulta). | **Sí.** Pasa en la base anterior. |
| `t4_readme::test_pd11…` y `::test_inv6…` | El README no tiene sección de arranque guiado. INV-6 no se puede evaluar sin esa sección. | **No.** Ya fallaban antes de 019-002. |
| `t6_owner_reviewfix::test_hallazgo_a1…` | `README.md:91` usa `CDAD_INSTALL_ROOT`. | **No.** Ya fallaba antes de 019-002. |
| `t6_owner_reviewfix::test_hallazgo_a2…` | `README.md:127` invoca `cdad_packet.py status` sin `<skill-dir>/scripts/`. | **No.** Ya fallaba antes de 019-002. |

Origen de los cuatro fallos del README: el commit `3b62d552` («docs: orientar README a personas…», 13-nov, anterior a 019-002) los introdujo.
- En `3b62d552^` el README no tenía `CDAD_INSTALL_ROOT` ni la invocación sin marcador.
- Desde `3b62d552` los tiene, y sigue sin sección de arranque guiado.
- Los commits de 019-002 sobre el README (`baf2874f` y `b38e3c26`) no los cambiaron.

## Disposición por test

Cada test recibe una sola disposición. Ninguno requiere cambiar el oráculo, porque la spec de 019-002 no toca las promesas de 005-006. Por eso la disposición es **Mantener** en los cinco. El producto es el que debe corregirse.

| Test | Disposición | Promesa y postcondiciones | Consecuencia para el usuario |
|---|---|---|---|
| `test_pd10_intake_wiring_uses_installed_cli` | Mantener | El intake del orquestador usa las referencias de la skill instalada, no rutas relativas al proyecto. Protege PD-10 e INV-5 de 005-006. | Sin este test, en un proyecto que no es el de CDAD el orquestador seguiría un `re-entry.md` que no existe en esa ruta. |
| `test_pd11_readme_guided_start…` | Mantener | El README debe decir que una instrucción breve basta y remitir a `project-start.md` (PD-11). | Sin este test, quien empieza no se entera de que no hace falta un prompt largo. |
| `test_inv6_no_long_prompt_block…` | Mantener | El arranque es un puntero corto, sin bloque de prompt largo ni plantilla (INV-6). | Sin este test, el README podría volver a copiar el prompt largo. |
| `test_hallazgo_a1_no_install_root…` | Mantener | El README no cita `CDAD_INSTALL_ROOT`, que es una variable del instalador y no del runtime. | Sin este test, con instalación global la ruta del CLI resuelve a una carpeta inexistente. |
| `test_hallazgo_a2_cli_invocations…` | Mantener | Toda invocación del CLI usa `<skill-dir>/scripts/…`. | Sin este test, quien sigue el README copia un comando que falla fuera del repo de CDAD. |

Ninguno requiere Extender, Sustituir, Consolidar, Añadir ni Retirar. No hay nodeids nuevos, así que no hace falta delta textual. No cambia el mapeo test→postcondición, así que no hace falta map delta.

## Relación con la spec 019-002

- **PD-10:** es una regresión de 019-002. Su PC-9 pide conservar la protección de entrega que ya existe, y el test sigue siendo válido. La spec admite cambiar solo la expectativa de `test_006_005_u7…:699–709` (PC-5), y ese cambio no aplica aquí. La corrección es de producto: marcar la referencia con `<skill-dir>` en la fuente y regenerar los agentes. Los agentes son salidas declaradas y no se editan a mano.
- **Los cuatro del README:** vienen de antes de 019-002 y 019-002 no los tocó. PC-8 solo pide guía liviana en el README y no menciona arranque guiado ni `CDAD_INSTALL_ROOT`. Corregirlos mezclaría una deuda ajena con esta feature.

## Próximos pasos proporcionados

1. **PD-10:** el implementer arregla la línea 157 de la fuente del orquestador con `<skill-dir>` y regenera. Verificar con `pytest tests/test_005_006_t2_intake.py`. Alcance mínimo: no se permite editar el test.
2. **Cuatro del README:** decisión del orquestador y del dueño. Hay dos opciones:
   - **(a)** Abrir una corrección separada de documentación 005-006: una sección corta de arranque en el README, quitar `CDAD_INSTALL_ROOT` de la línea 91 y marcar con `<skill-dir>` la línea 127. Por ser de README, no entra en el write_scope de tests y necesita su propio paquete.
   - **(b)** Registrarlos como regresión preexistente de `3b62d552`, con motivo, y no atribuirlos a 019-002 en el cierre del epic.
   
   Recomiendo (a). Son baratos de arreglar y las promesas siguen vigentes.
3. **Cierre del epic:** la suite completa quedó interrumpida. **Suite completa no realizada.** Ejecuté solo los 5 nodeids, más `t4_readme` y `t6_owner_reviewfix` en la base anterior. No afirmo suite completa verde ni cerrada. Tras las correcciones hay que correr la suite entera con evidencia real, según la política de cierre de epic.