# Informe — test-writer RED (review-fix B1)

**Feature:** `005-012-transition-registration` · **Ejecución:** `exec-005-012-transition-registration-001`
**Paquete:** `005-012-transition-registration-test-writer-red-009` · **Tarea:** T3 (review-fix del bloqueante B1)
**Contrato:** `docs/specs/005-012-transition-registration/spec.md` (sha256 `56d0be4b…edd5`) — PD-6, PD-8, PD-9, PD-21, PD-12, PD-17; `review.md` §1 B1 (condición de cierre); `plan.md` ficha T3. Raíz del repo: `<repo>`.

## 1. Archivos y alcance

- **Modificado (único):** `tests/test_005_012_t3_closure_dispatch_resolution.py` (+241/−2).
- Alcance respetado: sólo `tests/**`. **No** se leyó ni editó implementación; caja negra por subproceso sobre el CLI del repo. **No** se tocó el focal de T1 (B2 va en otro paquete) ni `docs/.cdad-state.json` (ya estaba modificado por el orquestador).
- Cambios **aditivos**: ningún caso existente se modificó ni debilitó (las 2 líneas reemplazadas son del docstring/mapeo, no de aserciones existentes).

## 2. (a) Casos agregados y postcondición que verifica cada uno

| Test nuevo | PD que verifica | Qué fija |
|---|---|---|
| `test_b1_pd6_revoked_delegation_fails_closed_approval_pending` | **PD-6 (B1)** + INV-7 | Con el fixture **listo para cerrar** (PD-8(a) y PD-8(b) verdes) y la delegación **REVOCADA** (`status: "revoked"` + `revoked_at`, forma del focal de T2) → `closure` **rc=2**, marcador **`approval pending`**, **nombrando** el registro, y state **byte a byte idéntico** (nada de `epic_features[].status: "done"` ni `active_feature: null`). |
| `test_b1_pd6_expired_delegation_fails_closed_approval_pending` | **PD-6 (B1)** + INV-7 | Ídem con la delegación **VENCIDA por fecha** (`expires_on` ISO en el pasado — `"2020-01-01"`, la forma de `test_pd6_case_b_expired_delegation_fails_closed_approval_pending`): rc=2 `approval pending`, nombrando el registro, sin efectos. |
| `test_pd6_case_c_closure_without_delegation_keeps_the_owner_unblocked` | **PD-6 (caso C, P2/D-10)** + PD-9 | **Control positivo** que la review exige conservar: **sin** registro `hitl_delegation` —y en la variante que PD-6 declara idéntica, además `active_epic: null`— el `closure` sigue **rc=0**, la entrada registra el **aprobador declarado** (`--approve-by`) y la salida **declara que no hubo delegación que verificar**. El dueño no se bloquea. |

Casos 1 y 2 = **RED** del defecto (hoy el cierre **prospera**). Caso 3 = guarda de no-regresión de P2/D-10 (hoy también rojo: la salida no declara la ausencia de delegación porque el cierre no pasa por el control).

Caso 4 del encargo (**el closure legítimo sigue funcionando**) → ya cubierto por el caso existente `test_pd9_closure_applied_records_evidence_and_rests` (delegación vigente + PD-8 verde → rc=0 con el efecto completo). **No** se tocó; sigue verde.

**Aislamiento de causas.** Para que la ÚNICA causa del rechazo de los casos 1/2 sea la autoridad, el fixture deja **PD-8 verde** (un paquete `dispatched` **con** recibo durable + la aprobación `specification` vigente pinneando el contrato).

**Añadidos de fixture (aditivos, sin alterar `single`/`double`):** modo nuevo `ready` en `_ClosureFixture` (PD-8 verde) y mutaciones declaradas de la delegación `revoke_delegation()` / `expire_delegation()` / `remove_delegation(epic_null=…)`, con las **mismas formas** del focal de T2. Fixture `authority_fx` nuevo.

## 3. (b) Comando exacto y salida real

### 3.1 Rojo de los casos nuevos + existentes verdes (focal T3)

```
$ python3 -m pytest tests/test_005_012_t3_closure_dispatch_resolution.py -q -rf
E       AssertionError: PD-6 violada (B1, revocada): con la delegación revocada el cierre debe fallar cerrado (rc=2); rc=0: "registered transition closure stage 'feature-closure' for demo-100-transition-fixture … approved_by: Demo Approver … stage_history: 2 entries (+1)"
E       assert 0 == 2
E       AssertionError: PD-6 violada (B1, vencida): con la delegación vencida por fecha el cierre debe fallar cerrado (rc=2); rc=0: "registered transition closure … approved_by: Demo Approver …"
E       assert 0 == 2
E       AssertionError: PD-6 violada (caso C, sin delegación): la salida debe DECLARAR que no hubo delegación que verificar: "registered transition closure … approved_by: Demo Approver …"
E           assert 'delegation' in "registered transition closure stage 'feature-closure' for demo-100-transition-fixture …"
FAILED tests/test_005_012_t3_closure_dispatch_resolution.py::test_b1_pd6_revoked_delegation_fails_closed_approval_pending
FAILED tests/test_005_012_t3_closure_dispatch_resolution.py::test_b1_pd6_expired_delegation_fails_closed_approval_pending
FAILED tests/test_005_012_t3_closure_dispatch_resolution.py::test_pd6_case_c_closure_without_delegation_keeps_the_owner_unblocked
3 failed, 8 passed in 18.57s
```

**Lectura del rojo (el defecto B1 reproducido por caja negra):** con delegación **revocada** o **vencida por fecha** el cierre **prospera (rc=0)**: aplica la aprobación de cierre, escribe `approved_by` y marca la feature `done`. Falla la **aserción del rc** (`assert 0 == 2`) — `AssertionError` de contrato, **no** `ImportError` ni `SyntaxError`. El caso C falla por la aserción del **texto del diagnóstico** (la salida no declara la ausencia de delegación, porque el cierre no pasa por el control de autoridad).

### 3.2 Regresiones declaradas de T3

```
$ python3 -m pytest tests/test_005_001_t3_idle.py tests/test_005_003_f2_idle_history.py tests/test_005_007_t3_open_unit.py tests/test_003_002_t1_receive.py -q
....................                                                     [100%]
20 passed in 23.38s
```

La suite completa **no** se corre acá (política: la corre quien cierra). PD-17 sin conteos ni porcentajes del state vivo. En el caso C **no** se asertó `validate-state` (límite D-10 declarado por PD-6: la vigencia del *estado* con epic activo y sin delegación es deuda). INV-7 se asevera como en los RED de T1/T2/T5: state byte a byte idéntico.

## 4. (c) Commit

```
$ git show --stat --oneline HEAD
331566c test: 005-012 review-fix B1 RED — PD-6 aplicada a closure (delegacion revocada/vencida falla cerrado approval pending, sin efectos) + control positivo del dueno sin delegacion
 tests/test_005_012_t3_closure_dispatch_resolution.py | 243 ++++++++++++++++++++-
 1 file changed, 241 insertions(+), 2 deletions(-)
```

## 5. Interpretaciones declaradas (el contrato fue verificable; no hubo detención)

1. **`closure` legítimo (caso 4 del encargo).** El focal ya lo cubre con delegación vigente y PD-8 verde (`test_pd9_…`); sigue verde. No se duplicó.
2. **Caso C en dos variantes.** PD-6 declara idénticos «sin delegación» y «`active_epic: null`»; el test cubre ambas (la segunda, tras el GREEN, debe comportarse igual).
3. **La nota del caso C es exigible a `closure`.** PD-6 abre con «`gate` **y `closure`** exigen `--approve-by`… La comprobación de la autoridad tiene tres casos», así que el caso C aplica a `closure`; la aserción es la misma que el focal de T2 usa para `gate`.
4. **Marcador del caso B.** «revocada o vencida → rc=2, marcador `approval pending`, nombrando el registro» (PD-6); el «nombrado» se asevera con el mismo criterio del focal de T2 (`"delegation"` en la salida **o** el `EPIC_ID`).
5. **Sin efectos:** se asevera por INV-7 (state byte a byte idéntico), lo que cubre «nada de `epic_features[].status: "done"`, nada de `active_feature: null`».

**Anonimización:** sin rutas absolutas del dueño, sin ids crudos de sesión, sin nombres de otros proyectos; fixture sintético y anónimo (`demo-100-…`, `epic-demo-100-fixture`), `HOME` del subproceso en tempdir vacío, proyecto descartable en `<tmp>`.
