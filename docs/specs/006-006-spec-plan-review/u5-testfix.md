TESTFIX complete and committed.

# CDAD — test-writer TESTFIX, U5 (006-006-spec-plan-review)

**Packet**: `006-006-spec-plan-review-test-writer-red-003` · exec `exec-006-006-spec-plan-review-001` · substage `red` · rol `test-writer`
**Contrato**: `docs/specs/006-006-spec-plan-review/spec.md` (sha256 `4d029a11…d298`)

## 1. Fichero modificado (único)

| Fichero | Cambio |
|---|---|
| `tests/test_006_006_u5_exemption_record.py` | +19 / −3 (fixture de cierre + docstrings) |

`git diff --stat -- tests/` → 1 fichero. Nada fuera de `tests/`. **No toqué ninguna aserción** del contrato: el diff es íntegramente de la fixture (`_ExemptionClosureFixture.__init__`) y de los docstrings que la declaran.

## 2. El cambio (testfix, no oráculo)

`_ExemptionClosureFixture.__init__` registraba el proyecto en modo `ready` **sin** la transición `delivery`: el paquete activo quedaba `dispatched`, y el LECTOR (`prepare`) rechazaba por PD-4 — oráculo vigente (`tests/test_004_002_t2_bootstrap.py:522`) — **antes** de mirar la aprobación. La aserción de vigencia (V-4) medía el estado del paquete, no la exención.

El arreglo, por el **mismo camino** que `_ExemptionFixture` (`_VigencyFixture.deliver()` → `self.delivery()` → `register-transition --transition delivery`), con la misma precondición de fixture (`rc=0`) y el diagnóstico equivalente:

```python
    testfix: la fixture deja el paquete terminal (PD-4) — la entrega legítima
    se registra por el MISMO camino que `_ExemptionFixture` (`delivery`:
    `register-transition --transition delivery`), sin lo cual el paquete
    activo queda `dispatched` y el LECTOR (`prepare`) rechaza por PD-4
    ANTES de mirar la aprobación: la aserción de vigencia (V-4) mediría el
    estado del paquete activo, no la vigencia de la exención.
    """
    def __init__(self, base: Path) -> None:
        super().__init__(base, mode="ready")
        delivered = self.delivery()
        assert delivered.returncode == 0, (...)
```

Docstring de módulo actualizado en la misma línea (una frase): la fixture de cierre registra además la entrega legítima ⇒ paquete terminal (PD-4) ⇒ el LECTOR puede llegar a la comprobación del pin.

**Por qué la fixture `gate` ya lo hacía y la de cierre no**: `_ExemptionFixture` (hereda de `_VigencyFixture`) llama `self.deliver()`; `_ExemptionClosureFixture` (hereda de `_ClosureFixture`) no lo hacía — `_ClosureFixture` sólo entrega en modo `double`. Consecuencia: la stage del `delivery` es `tdd-green-t1` (no `specification`), con lo que `drop_approval()` sigue quitando exactamente la aprobación y nada más.

## 3. Comandos y salida

```
$ python3 -m pytest tests/test_006_006_u5_exemption_record.py -q
..............                                                           [100%]
14 passed in 20.98s
```
(antes del testfix: `13 passed, 1 failed` — el que fallaba era `…_approval_with_exemption_stays_vigente_for_the_closure`, por PD-4)

```
$ python3 -m pytest tests/test_006_006_u5_exemption_record.py::test_pd9_approval_with_exemption_stays_vigente_for_the_closure -q
.                                                                        [100%]
1 passed in 5.27s
```

Regresiones declaradas de la ficha U5 (todas verdes):

```
$ python3 -m pytest -q tests/test_005_012_t1_register_transition_base.py tests/test_005_012_t2_gate_authority.py \
    tests/test_005_012_t3_closure_dispatch_resolution.py tests/test_005_012_t4_late_delivery.py \
    tests/test_005_012_t5_approval_vigency.py tests/test_005_014_closure_replay.py \
    tests/test_006_005_u5_disposition_failed.py
71 passed in 96.97s (0:01:36)

$ python3 -m pytest -q tests/test_005_001_t2_replace_packet.py tests/test_005_001_t3_idle.py \
    tests/test_006_003_rf_review_fixes.py tests/test_006_003_rf2_review_fixes.py tests/test_packet_prepare.py
41 passed in 122.39s (0:02:02)
```

**Suite completa**: NO la ejecuto (política declarada en el paquete: la corre una vez quien cierra).

## 4. Mapeo test → postcondición (sin cambios)

El test #5 sigue mapeando a **PD-9 + V-4** y ahora mide lo que dice medir: la aprobación con exención sigue vigente para el cierre (lector `rc=0`, segunda aprobación sin `--supersedes` rechazada con `state incoherent` + `supersedes`, cierre `rc=0`). Ningún oráculo vigente se reemplazó (A-1 intacto); `PD-4` sigue sin tocarse.

## 5. Commit

```
$ git add tests/test_006_006_u5_exemption_record.py
$ git commit -m "test: 006-006 U5 testfix — fixture de cierre con paquete terminal"
[main b597c55] test: 006-006 U5 testfix — fixture de cierre con paquete terminal
 1 file changed, 19 insertions(+), 3 deletions(-)
```

`b597c55` · sin `--no-verify` · sin `git stash` · sin `push` · **un solo fichero** en el commit.

Estado del repo tras el commit: ` M docs/.cdad-state.json` (del orquestador) y los sin trackear `docs/planning/` + `findings/*.md` — **no míos**, sin tocar.

## 6. Nota de alcance

- No leí código de implementación (`skills/cdad-cycle/scripts/cdad_packet.py`): el diagnóstico vino del informe GREEN (`docs/specs/006-006-spec-plan-review/u5-green.md` §5) y de los oráculos de `tests/`.
- El diff es un **arreglo local de fixture** (una clase, en un fichero): no toca `_ClosureFixture`, `_VigencyFixture` ni `_Fixture`, de modo que el impacto fuera del focal es estructuralmente nulo — aun así corrí las 12 regresiones declaradas como evidencia.