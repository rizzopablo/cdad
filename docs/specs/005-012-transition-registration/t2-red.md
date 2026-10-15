# Informe RED — 005-012 T2 (`test-writer`, subetapa `red`)

**Paquete:** `005-012-transition-registration-test-writer-red-002` · **Ejecución:** `exec-005-012-transition-registration-001` · **Feature:** `005-012-transition-registration` · **Tarea:** T2
**Contrato (oráculo):** `docs/specs/005-012-transition-registration/spec.md` (sha256 `6504e655…c6abe`) — **derivado de la spec, no de la implementación**.
**Plan:** `docs/specs/005-012-transition-registration/plan.md` §4 ficha T2 + bloque canónico `plan-tasks` (rendido por el paquete).
**Archivo creado (único):** `tests/test_005_012_t2_gate_authority.py` (nuevo, 667 líneas).
**Commit:** `112ce91` — `test: 005-012 T2 RED — gate (pin derivado de contrato/plan + autoridad en tres casos, PD-5/PD-6/PD-10/PD-20)` (1 archivo, +667; `git diff` acotado al alcance declarado `tests/`).

*Nota de anonimización:* las salidas de pytest traen rutas absolutas del repo; en este informe la raíz del repo se sustituye por `<repo>`. El archivo de test no contiene rutas absolutas del dueño (la raíz se deriva de `__file__`), ni ids crudos de sesión, ni nombres de otros proyectos: los ids del fixture son inventados (`epic-demo-100-fixture`, `demo-100-transition-fixture`).

## (a) Casos y PD que verifica cada uno

La clase `gate` **ya no existe** todavía en el árbol: T1 GREEN introdujo sólo `delivery` y `advance`. El CLI de hoy responde a `--transition gate` con un **error de uso** (`rc=2`, `invalid choice: 'gate' (choose from delivery, advance)`) y sin efecto alguno.

Fixture: proyecto descartable en un tempdir, `HOME` del subproceso en un tempdir **vacío**, ids sintéticos. La capa previa se produce por el **camino legítimo del CLI** (`prepare` → paquete `prepared`, ejecución v2, delegación HITL con `source` existente); las mutaciones de autoridad se aplican después sobre el state, con formas **ya declaradas por la suite** (`test_004_002_t2_bootstrap.py`, `test_003_004_t2_reviewfix.py`) — **ningún campo inventado**.

| Test | PD | Verifica |
|---|---|---|
| `test_pd5_gate_registered_with_non_empty_approver` | PD-5 (+§2.2, +PD-17) | `gate --stage <token> --approve-by <texto>` → rc=0; **+1** entrada con `transition: "gate"`, la etiqueta declarada y `approved_by` **NO vacío** (= aprobador declarado); `validate-state` rc=0 **antes y después** |
| `test_pd5_pd20_stage2_gate_derives_contract_and_plan_digests` | PD-5 + PD-20 | Gate de etapa 2 (`--stage specification`) con `--contract-path`/`--plan-path` **sin afirmar ningún digest** → rc=0; el CLI **DERIVA** el sha256 de los bytes, lo **escribe** en la entrada (`contract_sha256`/`plan_sha256`) y lo **imprime** en la salida |
| `test_pd20_asserted_contract_digest_that_matches_is_verified` | PD-20 | Un `--contract-sha256` afirmado que **coincide** se verifica y se **acepta** (rc=0) y queda escrito (la aserción opcional no puede rechazar por defecto) |
| `test_pd5_asserted_contract_digest_divergent_fails_closed` | PD-5 / INV-7 | `--contract-sha256` afirmado **divergente** → rc=2 `evidence missing`, **sin efectos** (state byte a byte idéntico) |
| `test_pd5_absent_contract_file_fails_closed` | PD-5 / INV-7 | `--contract-path` con el archivo **ausente** → rc=2 `evidence missing`, sin efectos |
| `test_pd5_asserted_plan_digest_divergent_fails_closed` | PD-5 / INV-7 | `--plan-sha256` afirmado **divergente** (contrato válido) → rc=2 `evidence missing`, sin efectos |
| `test_pd5_absent_plan_file_fails_closed` | PD-5 / INV-7 | `--plan-path` con el archivo **ausente** (contrato válido) → rc=2 `evidence missing`, sin efectos |
| `test_pd6_case_a_gate_accepted_with_active_delegation` | PD-6 (caso A) | Con delegación registrada y **vigente** (`status: active`, `source` resoluble) se verifica su vigencia y el `gate` **se acepta** (rc=0) escribiendo el aprobador declarado |
| `test_pd6_case_b_revoked_delegation_fails_closed_approval_pending` | PD-6 (caso B, revocada) | Delegación **revocada** (`status: "revoked"` + `revoked_at`) → rc=2, marcador **`approval pending`**, nombrando el registro, **sin efectos** (byte a byte idéntico) |
| `test_pd6_case_b_expired_delegation_fails_closed_approval_pending` | PD-6 (caso B, vencida) | Delegación **vencida** por su `expires_on` (`2020-01-01`) → rc=2, marcador **`approval pending`**, nombrando el registro, sin efectos |
| `test_pd6_case_c_without_delegation_registers_declared_approver` | PD-6 (caso C, **P2**) | **SIN** registro `hitl_delegation` → rc=0, `approved_by` = aprobador declarado en la entrada, y la salida **declara que no hubo delegación que verificar** (el dueño no se bloquea) |
| `test_pd6_case_c_active_epic_null_registers_declared_approver` | PD-6 (caso C, `active_epic: null`) | Igual que el anterior: sin autoridad que verificar → rc=0 y aprobador declarado escrito |
| `test_pd10_gate_entry_carries_transition_key` | PD-10 (forma `gate`) | La entrada de `gate` lleva `transition_key` (clave nueva y aditiva, forma sha256 de 64 hex) |
| `test_pd11_identical_gate_repetition_is_noop_byte_identical` | PD-11 (clase `gate`) | Repetición idéntica → rc=0, **sin** segunda entrada, state **byte a byte idéntico** y salida que **nombra** la entrada existente (su `transition_key`) |

Cobertura de los 6 casos mínimos del paquete: (1) PD-5/pin → filas 1-5; (2) PD-6 A → fila 8; (3) PD-6 B (revocada **y** vencida) → filas 9-10; (4) PD-6 C (P2) → filas 11-12; (5) PD-20 afirmado coincidente → fila 3; (6) aditividad/forma (`validate-state` rc=0 antes/después, `transition_key`, no-op) → filas 1, 13, 14.

Convenciones cumplidas: **caja negra sobre el CLI real como subproceso**; **ningún mock** del cableado interno; ningún test de cobertura no derivado de un PD; cada test cita su PD en el docstring y en el mensaje de aserción. Ninguna aserción sobre porcentajes ni conteos del state vivo.

## (b) Corrida focal: comando exacto y salida real

```
$ python3 -m pytest tests/test_005_012_t2_gate_authority.py -q
```

Salida real (`14 failed in 7.23s`; rutas del repo sustituidas por `<repo>`):

```
FAILED tests/test_005_012_t2_gate_authority.py::test_pd5_gate_registered_with_non_empty_approver
FAILED tests/test_005_012_t2_gate_authority.py::test_pd5_pd20_stage2_gate_derives_contract_and_plan_digests
FAILED tests/test_005_012_t2_gate_authority.py::test_pd20_asserted_contract_digest_that_matches_is_verified
FAILED tests/test_005_012_t2_gate_authority.py::test_pd5_asserted_contract_digest_divergent_fails_closed
FAILED tests/test_005_012_t2_gate_authority.py::test_pd5_absent_contract_file_fails_closed
FAILED tests/test_005_012_t2_gate_authority.py::test_pd5_asserted_plan_digest_divergent_fails_closed
FAILED tests/test_005_012_t2_gate_authority.py::test_pd5_absent_plan_file_fails_closed
FAILED tests/test_005_012_t2_gate_authority.py::test_pd6_case_a_gate_accepted_with_active_delegation
FAILED tests/test_005_012_t2_gate_authority.py::test_pd6_case_b_revoked_delegation_fails_closed_approval_pending
FAILED tests/test_005_012_t2_gate_authority.py::test_pd6_case_b_expired_delegation_fails_closed_approval_pending
FAILED tests/test_005_012_t2_gate_authority.py::test_pd6_case_c_without_delegation_registers_declared_approver
FAILED tests/test_005_012_t2_gate_authority.py::test_pd6_case_c_active_epic_null_registers_declared_approver
FAILED tests/test_005_012_t2_gate_authority.py::test_pd10_gate_entry_carries_transition_key
FAILED tests/test_005_012_t2_gate_authority.py::test_pd11_identical_gate_repetition_is_noop_byte_identical
14 failed in 7.23s
```

**Motivo del fallo, caso por caso** — corrida con traza en una línea (misma sesión, mismo archivo), comando exacto:

```
$ python3 -m pytest tests/test_005_012_t2_gate_authority.py -q --tb=line
```

| Test | Línea | Aserción que falla | Tipo |
|---|---|---|---|
| `test_pd5_gate_registered_…` | `:228` | `PD-5 violada: gate con --approve-by debe registrarse (rc=0); hoy rc=2` | AssertionError (contrato) |
| `test_pd5_pd20_stage2_gate_derives_…` | `:272` | `PD-5 violada: … sin afirmar ningún digest debe aceptarse (rc=0); hoy rc=2` | AssertionError |
| `test_pd20_asserted_contract_digest_that_matches_…` | `:320` | `PD-20 violada: un --contract-sha256 afirmado que coincide … (rc=0); rc=2` | AssertionError |
| `test_pd5_asserted_contract_digest_divergent_…` | `:357` | `PD-5 violada: el rechazo debe llevar el marcador «evidence missing»` | AssertionError |
| `test_pd5_absent_contract_file_…` | `:382` | `PD-5 violada: el archivo ausente debe fallar con el marcador «evidence missing»` | AssertionError |
| `test_pd5_asserted_plan_digest_divergent_…` | `:411` | `PD-5 violada: el rechazo debe llevar el marcador «evidence missing»` | AssertionError |
| `test_pd5_absent_plan_file_…` | `:437` | `PD-5 violada: el plan ausente debe fallar con el marcador «evidence missing»` | AssertionError |
| `test_pd6_case_a_…` | `:468` | `PD-6 violada (caso A): con la delegación vigente el gate debe aceptarse (rc=0); rc=2` | AssertionError |
| `test_pd6_case_b_revoked_…` | `:500` | `PD-6 violada (caso B, revocada): … marcador «approval pending»` | AssertionError |
| `test_pd6_case_b_expired_…` | `:528` | `PD-6 violada (caso B, vencida): … marcador «approval pending»` | AssertionError |
| `test_pd6_case_c_without_delegation_…` | `:557` | `PD-6 violada (caso C, sin delegación — P2): … NO debe bloquearse (rc=0); rc=2` | AssertionError |
| `test_pd6_case_c_active_epic_null_…` | `:590` | `PD-6 violada (caso C — active_epic: null): … no debe bloquearse (rc=0); rc=2` | AssertionError |
| `test_pd10_gate_entry_carries_transition_key` | `:613` | `PD-10 violada: el gate debe registrarse (rc=0) para llevar su clave de identidad; hoy rc=2` | AssertionError |
| `test_pd11_identical_gate_repetition_…` | `:640` | `PD-11 violada: la primera invocación del gate debe registrar la transición (rc=0); hoy rc=2` | AssertionError |

Diagnóstico observado del CLI (idéntico en los 14, es la salida real del subproceso):

```
ERROR: cdad_packet.py register-transition: argument --transition: invalid choice: 'gate'
(choose from delivery, advance)
```

**Los 14 son AssertionError** (fallos por aserción de contrato): ningún `ImportError`, `SyntaxError`, `JSONDecodeError`, traceback ni fallo de precondición de fixture (la capa `prepare` y los `validate-state` previos dieron rc=0; no aparece ningún fallo con el prefijo `precondición (fixture…`).

Declaración honesta de un matiz del RED (heredado de T1): en los **cuatro casos negativos de pin** y en los **dos de autoridad** la primera aserción es `rc == 2`, y hoy argparse también sale con rc=2, así que esa aserción pasa por coincidencia y el test cae en la **siguiente** aserción (el marcador del contrato). El rojo sigue siendo por aserción de contrato: el test distingue el rechazo de dominio por el **marcador** (`evidence missing` / `approval pending`), no por el rc.

**Evidencia extra (motivo concreto: el archivo nuevo se suma a la suite e importa un módulo de test existente; se verifican las regresiones declaradas por el paquete):**

```
$ python3 -m pytest tests/test_005_001_t1_role_approval.py tests/test_005_001_t4_decisive.py \
    tests/test_005_007_t3_open_unit.py tests/test_packet_prepare.py -q
33 passed in 28.34s
```

La suite completa **no** se corrió (política del paquete: la corre quien cierra).

## (c) El archivo NO importa el módulo de implementación

Importaciones del archivo (grep real sobre el archivo):

```
 92: import hashlib
 93: import subprocess
 94: from pathlib import Path
 96: import pytest
 98: from test_005_012_t1_register_transition_base import (
       APPROVER, AUTHORITY_REF, EPIC_ID, FEATURE_ID, TRANSITION_DIGEST_RE,
       _Fixture as _BaseFixture, assert_unchanged, entries, last_entry_with)
```

- **Ninguna** importación de `cdad_packet` ni `cdad_result` (ni por nombre ni por ruta): las únicas apariciones de `cdad_packet.py` en el archivo están en el **docstring** que declara la superficie de invocación. Los CLIs se invocan **solo como subproceso** (`subprocess.run([sys.executable, <CLI>, …])`, heredado del runner del focal T1), tal como exige la spec §4 y la ficha T2.
- El único import no estándar es `test_005_012_t1_register_transition_base`, un **módulo de test** ya existente (patrón declarado por el paquete: «reutilizá el patrón y los helpers que ya usó el focal de T1»), del que se reutilizan el runner de subproceso, el constructor de proyecto descartable y tres helpers de observación (`assert_unchanged`, `entries`, `last_entry_with`); **no** se importa lógica de producto.
- No se leyó código de implementación. La forma de `hitl_delegation` (activa/revocada/vencida) y la resolución de `--contract-path` relativa a la raíz del proyecto se derivaron de **tests** existentes dentro del alcance de lectura (`test_004_002_t2_bootstrap.py`, `test_003_004_t2_reviewfix.py`, `test_004_003_t1_draft_contract.py`) y se validaron corriendo el CLI como subproceso sobre proyectos descartables.

## (d) Commit

```
$ git log --oneline -1
112ce91 test: 005-012 T2 RED — gate (pin derivado de contrato/plan + autoridad en tres casos, PD-5/PD-6/PD-10/PD-20)

$ git show --stat --oneline HEAD | tail -3
112ce91 test: 005-012 T2 RED — gate (pin derivado de contrato/plan + autoridad en tres casos, PD-5/PD-6/PD-10/PD-20)
 tests/test_005_012_t2_gate_authority.py | 667 ++++++++++++++++++++++++++++++++
 1 file changed, 667 insertions(+)
```

Estado del árbol tras el commit: `M docs/.cdad-state.json`. **No es un cambio mío**: es el registro del despacho de este mismo paquete, hecho por el orquestador; no lo toqué ni lo commiteé. Mi único archivo escrito y commiteado es el test focal.

## Ambigüedades / límites declarados (no inventé oráculo ni debilité tests)

Nada me bloqueó: el contrato fue verificable. Declaro estos puntos de interpretación y límites, con la decisión tomada y su fundamento:

1. **PD-6 caso C / PD-6 caso B(revocada) — el estado del fixture no es «coherente» para `validate-state`.** Verifiqué empíricamente (sonda en tempdir) que el `validate-state` del CLI rechaza tanto `hitl_delegation` ausente con epic activo («an active epic requires a delegation record») como la delegación revocada («hitl_delegation is revoked»). Es exactamente el **límite del estado** que la spec declara como **deuda D-10** (la vigencia del *estado* sigue exigiendo delegación; el recurso P2 es que **la operación no bloquee**). Por eso los casos C no asertan `validate-state`; su oráculo es el comportamiento de la **operación** (rc=0 + aprobador declarado), tal como fija PD-6. Los casos A (vigente), vencida y de pin sí operan sobre un estado `validate-state` rc=0 (y el caso de la forma mínima lo asertá antes/después).
2. **La variante `active_epic: null` con una ejecución activa es incoherente para `validate-state`** («active_epic None does not match the execution epic»). La incluyo igual porque el contrato la declara explícitamente («con `active_epic: null`: idéntico al anterior») y su oráculo es sólo el de la operación; no asertá coherencia del estado.
3. **«La salida declara que no hubo delegación que verificar».** Lo verifico con una comprobación estructural mínima (aparece «delegation» en la salida), sin decidir el significado de un párrafo por listas de palabras —precedente declarado: `test_obs2_declared_dependencies_verified_or_declared` usa `"dependenc" in salida`—. **El sentido del texto lo juzga la review** (criterio del dueño, `plan.md:26`); si el orquestador prefiere una frase canónica distinta, es un cambio de contrato, no del test.
4. **Base de resolución de `--contract-path`/`--plan-path`.** Los paso **relativos a la raíz del proyecto** (y aserto que la entrada registra ese mismo string), que es la convención ya establecida del propio CLI para `--contract-path` —confirmada en negro corriendo `tests/test_004_003_t1_draft_contract.py` (2 passed): escribe el archivo bajo `project.root / <relpath>` y pasa el relpath—. No es una invención: es la semántica existente de la bandera.
5. **Pin del gate de etapa 2 sobre una ruta de contrato NUEVA** (`docs/specs/<feature>/spec-t2-gate.md`, distinta de la que el fixture ya tiene pinneada). Es deliberado: la exclusión estructural de PD-14 («ya existe una entrada vigente para `(feature, contract_path)` sin `--supersedes`») es **T5**, fuera del alcance de T2; usar una ruta sin entrada previa mantiene el focal de T2 válido también cuando T5 esté implementado (la suite completa se corre al cierre).
6. **Forma de la delegación vencida.** Uso `expires_on: "2020-01-01"` (fecha en el pasado), forma ya presente en la suite (`test_003_004_t2_reviewfix.py:562`, `test_003_004_t2_writeahead.py:513`) y sancionada por el paquete («vencida por su `expires_on`»). No inventé campos.
7. **INV-7 — mitad «árbol».** Aserto el **state byte a byte idéntico** en todo rechazo y **no** el snapshot completo del árbol, por el mismo motivo que el RED de T1 declaró (no es verificable qué artefactos toca el escritor fuera del state; la mitad «árbol» queda para el gate de aceptación T8).
8. **Casos negativos: marcador por condición.** En los rechazos, la aserción discriminante es el **marcador** del contrato (`evidence missing` / `approval pending`), no el rc (matiz declarado en (b)). En los dos casos de marca «nombrando el registro» uso una tolerancia mínima (`"delegation"` en la salida **o** el id del epic), porque la spec no fija literalmente la palabra del diagnóstico; el fuerte es el marcador.
