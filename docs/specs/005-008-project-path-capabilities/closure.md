# Cierre — 005-008-project-path-capabilities

**Feature:** `005-008-project-path-capabilities` · **Epic:** `epic-005-real-operation`
**Fecha:** 2026-10-10 · **Estado:** cerrada (etapa 5 cumplida)
**Aprobación:** orquestador OpenCode bajo la delegación HITL de epic-005
(`docs/epics/epic-005-real-operation/execution.md`).

## 1. Resultado

Una política válida del proyecto con **tests anidados dentro de la implementación**
(caso real: Perl/Webmin, implementación `webmin-module/module/` y tests en
`webmin-module/module/t/`) ahora produce **mapas de permisos coherentes con el
clasificador**: el test-writer **lee y edita** sus tests y auxiliares declarados,
conserva el **deny mediado de lectura** sobre la implementación, y el implementer
**edita implementación y no tests**. Se cubre además el caso focal de `test_files`
bajo implementación y la precedencia de las rutas privadas.

- **PD-1/PD-3:** el `read`/`edit` del test-writer reabre el árbol de tests declarado
  (antes solo lo hacía `edit`: se podía editar un test que no se podía leer).
- **PD-2/PD-4:** la barrera de lectura de implementación se conserva; el implementer
  edita implementación y no tests.
- **PD-5:** `_test_patterns` incluye `test_files` (antes se ignoraba: el clasificador
  decía `tests` y los permisos derivados lo denegaban).
- **PD-6:** una excepción de tests nunca reabre una ruta privada (el allow de tests va
  **antes** de `private`; findLast conserva la barrera).
- **PD-7/INV-3:** sin convenciones globales `**/t/**` ni `**/*.t`; solo árboles/archivos
  declarados. **PD-9/W-2:** sin entradas por ruta en `grep`/`glob`.
- **PD-8:** el layout convencional no regresiona.
- **PD-10:** los comandos de sintaxis/tests del consumidor viven en su lugar canónico
  (Makefile/systemPatterns); el esquema de `docs/cdad-policy.json` sigue de exactamente
  tres campos y ahora **rechaza un campo extra nombrándolo** en el diagnóstico.
- **PD-11:** el **producto instalado** en una raíz aislada demuestra las capacidades
  positivas y negativas, con los límites honestos declarados.

No se implementó el producto consumidor, no se crearon agentes Perl manuales ni otro
sistema de políticas, no se cambió HOME y no se operó producción (INV-7/INV-9).

## 2. Gate de etapa 5

| Comprobación | Resultado |
|---|---|
| Suite completa (worktree fijo al commit de cierre) | **701 passed / 0 failed** (875.64s, exit 0) |
| Focales de la feature | 16/16 (T1 9, T2 2, T3 5) |
| `make validate` | 141 PASS / 2 FAIL **preexistentes/ambientales**, ajenos al diff |
| Review formal | **PASS, 0 bloqueantes** (ver §6) |
| Memory Bank | borradores del scribe, revisados y aprobados bajo la delegación HITL |

## 3. Decisiones aprobadas (D1–D7, tal como se propusieron)

D1 fuente única de patrones incluyendo `test_files`; D2 orden del mapa `read`
(deny de implementación → allow de tests declarados → `private` al final); D3 sin
convenciones globales; D4 comandos del proyecto en su lugar canónico, nunca en la
política; D5 aceptación por comportamiento observable + recorrido del producto
instalado; D6 T1 es el único cambio de producto, T2 reusa 005-006 sin duplicar el
bootstrap, T3 es la aceptación; D7 frontera explícita.

## 4. Desviaciones y hallazgos de proceso

1. **Error del orquestador (sin efecto):** el objetivo del primer paquete de GREEN de
   T1 (`-green-001`) perdió las palabras entre backticks porque el shell las interpretó
   como sustitución de comando al construir el comando. El paquete se marcó `failed`
   **sin despacharse** y se preparó `-green-002` con el texto correcto. El objetivo no
   es corregible por `--replace-packet` (conserva el encargo anterior y solo admite
   insumos/alcances/invariantes/entrega/evidencia).
2. **Reviewer con suite en background:** el primer turno del reviewer devolvió control
   mientras la suite completa corría en background y el proceso murió con la sesión
   (patrón ya visto en 004-001/004-003/005-006). Se **reanudó la misma sesión** y
   entregó el informe completo en primer plano.
3. **Superficie de T2 (O-2 de la review):** el plan no listaba
   `_validate_policy_document` en los `files` de T2, pero PD-10(b) —aprobada como parte
   del contrato— exige el diagnóstico nombrado. El cambio implementa exactamente la
   postcondición aprobada y la suite aprobada la verifica. Errata declarada aquí.
4. **RED de T3 (honesto):** T3 no tiene producto nuevo (el plan lo declara); sus tests
   pasan de inmediato contra el producto instalado. Es un **lock** del recorrido, con
   el RED de sus postcondiciones registrado en T1. No se fabricó ninguna falla.
5. **Artefacto ajeno observado:** apareció sin rastrear
   `docs/specs/005-003-orientation-reduction/discovery-inputs.md` (12:14), preparado por
   otra sesión (caso S-BOOT-04). No pertenece a este ciclo, no se commiteó y no se tocó.

## 5. Evidencia

**Commits de la feature** (base `3fb1e91`):

| Commit | Unidad |
|---|---|
| `17d5f9c` | T1 RED — 9 tests (uno por PD-1..PD-9) |
| `17e6184` | T1 GREEN — `+9` en `skills/cdad-cycle/scripts/cdad_packet.py` |
| `aff3a20` | T2 RED — PD-10(a)/(b) |
| `8500bf4` | T2 GREEN — `+10/-2` (diagnóstico nombrado) |
| `54fb376` | T3 — aceptación desde el producto instalado |
| `7928650` | review formal materializada |

**Suite completa** (worktree fijo en el commit de cierre, corrida del orquestador):
**701 passed / 0 failed** en `875.64s` (exit 0). El primer intento en ese worktree dio
700 passed / 1 failed porque el `build/staging` se había construido con `PROFILE=basic` y
`test_install_review5_regressions.py::TestReview5ProfileAgreement::test_review5_b4_basic_request_vs_staging_profile_labels_coherent`
exige un staging con perfil distinto; reconstruido con el perfil por defecto (`make staging`), el test
pasa y la suite queda **verde completa**. Registro: `/tmp/opencode/close-suite-005-008*.log`.

**Hallazgo de entorno (nuevo, verificado):** un worktree limpio **no** reproduce el entorno de la suite —
`build/` está gitignoreado y los tests de instalación dependen del build de staging; sin él dan 4F/6E que
**no** son regresiones (los mismos 15 tests pasan en el árbol con staging). Una corrida de cierre en
worktree exige ejecutar `make staging` **dentro** del worktree antes de la suite.

**Recorrido del producto instalado (gate de integración PD-11):** los 5 tests de T3
construyen una instalación aislada (`install.sh --basic` con `CDAD_INSTALL_ROOT` en un
tempdir) y ejercitan el CLI instalado; corridos por el orquestador: 5 passed.
**HOME intacto** (marcador `~/version.txt` = `35062b0`, anterior al ciclo).

## 6. Review

Una sola review formal (`review.md`), read-only, con **modelo de familia distinta** a la
del implementer. **Veredicto: PASS, sin bloqueantes.** Verificó por sí misma: suite
completa 700 passed / 1 falla **preexistente/ambiental** (un test exige un
`build/staging` con perfil distinto de `basic`; reproduce igual en la base), `make
validate` 141/2 preexistentes, focos 16/16, RED genuino por worktrees en los commits de
RED y tests **byte-idénticos** entre RED y HEAD (no debilitados), paridad del guard CC y
del clasificador, y auditoría test↔postcondición (16 tests, 0 superfluos, sin nombres
internos ni mocks de plumbing).

**Opcionales** (no prolongan el ciclo): O-1 (registro con el dueño de los VERIFY
1/3/5/6, ver §7), O-2 (errata de superficie de T2, ver §4.3), O-3 (`build/staging` local
en rojo, fuera del diff). **Abstenciones:** mediación en vivo de un proceso OpenCode
real, lectura de la ruta privada, relectura del paquete de GREEN, y la cifra de suite
(corrida completa real, no estimada).

## 7. VERIFY abiertos del dueño y aceptación conjunta

El cierre de la feature **no** cierra estos puntos: pertenecen al dueño del consumidor y
a la aceptación conjunta con 005-009 (plan §5, spec §8).

1. **VERIFY 1** — layout/política reales del consumidor Perl/Webmin (vive fuera de este
   repo; el layout del plan es caso de uso, no política confirmada).
2. **VERIFY 3** — mediación en vivo de un proceso de runtime real (los tests declaran
   ese límite; `grep`, el shell y una sesión separada no son sandbox).
3. **VERIFY 5** — entrega de convenciones/referencias de dominio al consumidor no-odoo
   (el paquete no inyecta fuentes de dominio; se resuelve por objetivo+insumos o por el
   mecanismo de stack, sin agentes manuales).
4. **VERIFY 6** — registro real de los comandos Perl del consumidor en su lugar canónico.
5. **Aceptación conjunta (plan §5):** una sesión nueva inicia el consumidor con una
   instrucción breve, conserva sus IDs y organización, registra lo faltante y realiza la
   primera delegación útil. Aporta la aceptación pendiente **R2 de 005-006** y la de
   interoperabilidad cuando ejerza ambas. **No** se ejecutó en este ciclo.

## 8. Deuda

- **O-1/O-2/O-3** de la review (arriba), ponderadas por efecto real.
- `install.sh --check` sigue siendo sensible a los `__pycache__` que Python escribe
  junto al CLI instalado (señal del verificador, no requisito del consumidor).
- El paquete de CDAD no inyecta fuentes de dominio por encargo (VERIFY 5).

## 9. Versión sucesora y despliegue (instrucciones; **no ejecutado**)

La versión sucesora de este ciclo es el commit de cierre de esta feature. El despliegue
**es una acción del dueño** y **no** se ejecutó aquí: no se cambió HOME, no se
reinstalaron las bases globales y no se publicó nada.

Para desplegar la sucesora (cuando el dueño lo decida, **entre ciclos**):

1. Congelar un worktree en el commit de cierre de la feature.
2. `make staging PROFILE=basic` y luego `install.sh --basic --force` con el
   `INSTALL_ROOT` que corresponda (HOME solo si el dueño lo autoriza).
3. Verificar: `version.txt` y `source_version` del manifiesto iguales al commit;
   `install.sh --check` sin conflictos; los archivos clave presentes en las tres bases.
4. Republicar los agentes derivados de cada proyecto consumidor con su primer
   `prepare` legítimo (nunca a mano) y comprobar la coherencia de versión.
5. La R2 real y la aceptación conjunta del consumidor (§7) se registran entonces.

## 10. Próxima unidad del epic

**005-009-cli-delegation** (orden 5), que depende de 005-008 para la aceptación conjunta
del consumidor. Después: 005-002 (pausada, discovery intacto), 005-003, 005-007 y
005-004, según el plan vigente.
