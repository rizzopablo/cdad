#!/usr/bin/env python3
"""005-012 T5 RED — vigencia estructural de la aprobación: el campo
`supersedes` y el **lector aditivo** (PD-14, PD-15).

Contract:
- docs/specs/005-012-transition-registration/spec.md §2.1 (`--supersedes` en la
  superficie del subcomando), §2.3 (PD-14: vigencia estructural; PD-15: prohibido
  que la única traza de una sustitución sea prosa), §2.2 (forma aditiva: la clave
  `supersedes` de la entrada), §2.4 (INV-3 append-only, INV-7 sin efectos),
  §5 D-8 (la vigencia se marca en la entrada NUEVA, aditiva sobre D3/PD-18 de
  005-001), §3 (frontera del juicio: el CLI no decide el significado de un texto).
- Postcondiciones soporte que el encargo declara para estos flujos: PD-10/PD-11
  (la entrada lleva `transition_key`; repetir la invocación idéntica es no-op) y
  PD-17 (aditividad: `validate-state` rc=0 antes y después; ninguna entrada
  histórica se invalida ni se reescribe).
- docs/specs/005-012-transition-registration/plan.md §4 ficha T5 (test focal
  declarado `tests/test_005_012_t5_approval_vigency.py`).

Superficie observable bajo prueba (caja negra: SOLO subprocess sobre el CLI del
repo; el módulo de implementación NUNCA se importa y su código NUNCA se lee):

    python3 skills/cdad-cycle/scripts/cdad_packet.py register-transition \\
        --project-root <ABS> --transition gate --stage specification \\
        --approve-by <texto> --contract-path <p> [--substage <sub>] \\
        [--supersedes <transition-key>]
    python3 skills/cdad-cycle/scripts/cdad_packet.py prepare \\
        --project-root <ABS> --role test-writer --substage red --objective <t>
    python3 skills/cdad-cycle/scripts/cdad_packet.py validate-state \
        --project-root <ABS>

El **lector** es el que usa el propio CLI para autorizar a los roles de
construcción (`_approved_spec_entries`/`_contract_approval_for`), y se observa
en negro por su efecto: un `prepare --role test-writer --substage red` que se
HABILITA (rc=0) o se BLOQUEA con el marcador `approval pending` (rc=2). HOY el
lector ignora el campo `supersedes`: una entrada reemplazada (con el pin todavía
coincidente) sigue habilitando. Por eso cada test falla en la ASERCIÓN sobre el
comportamiento del contrato (rc esperado, marcador, efecto sobre la vigencia,
bytes del state), nunca en la invocación ni en una precondición de fixture: los
fallos RED son AssertionError de contrato, jamás ImportError, SyntaxError,
JSONDecodeError ni error de setup.

Fixture: proyecto descartable en un tempdir (política válida, delegación HITL
vigente con `source` resoluble, ejecución v2, paquete real `dispatched` con
recibo durable) construido por el camino legítimo del CLI (`prepare` →
`prepare --record-dispatch` → `cdad_result.py receive`), con el `HOME` del
subproceso en un tempdir VACÍO (nunca el HOME real, nunca este repo). Los ids del
fixture son sintéticos y anónimos. El paquete se deja terminal con una
`--transition delivery` legítima (PD-2, T1) para que el lector pueda correr
(`prepare` exige un paquete activo terminal). Las mutaciones de `stage_history`
que arman el escenario de vigencia se aplican sobre el state del fixture con la
forma declarada por §2.2 (misma práctica que el focal de T2 con la delegación);
ningún campo inventado. Se reutilizan el patrón y los helpers del focal T1
(fixture base, `entries`/`last_entry_with`/`assert_unchanged`) y de T2 (subclase
de fixture con helper `gate`).

Mapeo test → postcondición (y caso mínimo del encargo):

  test_pd14_second_vigente_without_supersedes_fails_closed
      -> PD-14 (registro) + INV-7. Caso 1: con un `(feature, contract_path)` que
         YA tiene una entrada vigente, un segundo `gate --stage specification`
         para el MISMO `contract_path` SIN `--supersedes` → rc=2, marcador
         `state incoherent`, nombrando la entrada vigente y el campo
         `supersedes`, y SIN efectos (state byte a byte idéntico).
  test_pd14_supersedes_replaces_the_vigent_entry_for_the_reader
      -> PD-14 (registro + lector). Casos 2 y 3: con `--supersedes` que nombra
         una entrada existente de la misma feature y el mismo `contract_path` →
         rc=0, la entrada nueva lleva `transition_key` y `supersedes`; a partir
         de ahí el lector sólo habilita por la nueva: presentando el contrato de
         la aprobación SUSTITUIDA el rol NO se habilita (rc=2 `approval pending`,
         sin efectos), y con el contrato VIGENTE sí (rc=0).
  test_pd15_prose_note_is_not_the_control_and_the_structural_field_is
      -> PD-15. Caso 4 (control negativo): dos entradas con el pin correcto y una
         nota en prosa «reemplaza a la anterior» pero SIN `supersedes` → ambas
         siguen habilitando (comportamiento de hoy, declarado); con el campo
         `supersedes` → sólo la nueva habilita. Se verifican los dos lados.
  test_pd17_operation_keeps_validate_state_green_and_history_append_only
      -> PD-17 + INV-3. Caso 5: `validate-state` rc=0 antes y después; ninguna
         entrada histórica sin `supersedes` se invalida ni se reescribe
         (append-only): las entradas previas quedan intactas, no ganan el campo
         nuevo, y la entrada histórica sigue habilitando. Sin porcentajes ni
         conteos del state vivo del repo.
  test_pd10_pd11_gate_with_supersedes_carries_key_and_repeat_is_noop
      -> PD-10/PD-11 + PD-14 (el no-op no deshace el reemplazo). Caso 6: la
         entrada del gate con `--supersedes` lleva `transition_key`, y repetir la
         invocación idéntica es no-op (rc=0, sin segunda entrada, state byte a
         byte idéntico, salida que nombra la entrada existente).

Interpretaciones declaradas (no se inventó oráculo ni se debilitó un test):

1. **La segunda vigente es una transición DISTINTA.** PD-10 fija los campos de
   `transition_key` y `supersedes` NO está entre ellos; PD-11 hace que una
   invocación idéntica sea no-op. Por eso, para que exista una segunda ENTRADA
   vigente del mismo par, la invocación difiere en un campo de la clave
   (`--substage`). Si no, PD-11 (no-op) y PD-14 (rc=2) se contradirían.
2. **Cómo se observa que la sustituida deja de habilitar.** El par comparte el
   `contract_path`; lo que cambia entre dos aprobaciones es el contenido del
   archivo (el caso real de una re-aprobación: el contrato se corrige). El test
   presenta los bytes de la aprobación sustituida (hoy habilitan porque su pin
   coincide) y los de la vigente: sólo los segundos deben habilitar tras PD-14.
3. **El control negativo de PD-15 se arma con el state del fixture** (dos
   entradas con el pin correcto y una nota en prosa), porque registrar una
   segunda vigente sin `--supersedes` es justamente lo que PD-14 rechaza. La
   nota es dato del fixture; el test NO decide su significado (frontera del
   juicio, §3): sólo comprueba que no cambia qué entrada habilita.
4. **El lector se corre tras una `delivery` legítima** (única forma de que el
   paquete activo quede terminal y `prepare` llegue a la comprobación del pin).
   En cada test hay a lo sumo UNA invocación habilitante del lector, para no
   confundir el bloqueo del lector con el bloqueo por paquete activo.

REVIEW-FIX B3 (paquete `005-012-transition-registration-test-writer-red-010`).
La spec vigente fue ENMENDADA otra vez (spec §0.1, PD-14/D-8): el **predicado de
vigencia** del control de exclusión pasa a ser el que el cierre ya usaba en
PD-8(b) —**la entrada debe NOMBRAR los bytes actuales** (`contract_path` + el
`contract_sha256` derivado)—, de modo que una aprobación cuyo pin **ya no
nombra** los bytes actuales **no compite** como vigente (y ya no habilitaba: el
lector exige el pin). Los casos anteriores **no** se tocan ni se debilitan (con
los MISMOS bytes su lectura no cambia). Los casos nuevos son el RED de esa
corrección:

  test_b3_pd14_reapproval_with_new_bytes_over_keyless_approval_needs_no_supersedes
      -> PD-14 (consecuencia 1) + D-8. Caso 1 (el defecto B3): una aprobación
         `specification` **sin `transition_key`** (registrada a mano, `--supersedes`
         no puede citarla) cuyo pin **ya no nombra** los bytes actuales (el
         contrato se enmendó) **no compite**: `gate --stage specification
         --contract-path <spec>` **sin** `--supersedes` → rc=0, con una entrada
         NUEVA (su `transition_key` y el pin derivado de los bytes actuales) que
         habilita a los roles de construcción; la vieja no habilita (su pin no
         coincide) y no se reescribe.
  test_b3_pd14_same_bytes_still_requires_supersedes_and_the_amendment_does_not
      -> PD-14 (consecuencias 2 y 3) + PD-20. Casos 2 y 3: con la entrada
         vigente **con clave** cuyo pin NOMBRA los bytes actuales, reaprobar los
         MISMOS bytes sigue exigiendo el campo estructural (sin `--supersedes` →
         rc=2 `state incoherent` nombrando la entrada vigente y el campo; state
         byte a byte idéntico = caso 3) y **con** `--supersedes <transition-key>`
         → rc=0. Este comportamiento no cambia. Mitad discriminante del mismo
         flujo (consecuencia 1, «tenga o no clave la entrada vieja»): enmendados
         los bytes, esa misma vigente ya no compite → un `gate` posterior **sin**
         `--supersedes` → rc=0.
  test_b3_pd17_amendment_keeps_validate_state_green_and_history_untouched
      -> PD-17 + INV-3. Caso 4 (aditividad): sobre el flujo del caso 1,
         `validate-state` rc=0 ANTES y DESPUÉS; ninguna entrada histórica sin
         `transition_key` se invalida ni se reescribe (append-only) y la
         operación sólo anexa. Sin porcentajes ni conteos del state vivo del
         repo.

Mismo instrumento y mismas convenciones que los casos anteriores (caja negra
sobre el CLI como subproceso; proyecto descartable con el HOME del subproceso en
un tempdir vacío; fixture sintético y anónimo; cada test corre y falla por
ASERCIÓN, nunca por import, sintaxis o error de fixture).
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from test_004_002_t2_bootstrap import prepare_args
from test_005_012_t1_register_transition_base import (
    APPROVER,
    CONTRACT_BYTES,
    CONTRACT_FILE,
    FEATURE_ID,
    STATE_INCOHERENT,
    APPROVAL_PENDING,
    TRANSITION_DIGEST_RE,
    _Fixture as _BaseFixture,
    assert_unchanged,
    entries,
    last_entry_with,
)

# La clase `gate` es la DECISIÓN; `--stage` es la etiqueta. La vigencia
# estructural de PD-14 es la del gate de ETAPA 2: `--stage specification` con el
# pin del contrato.
SPEC_STAGE = "specification"
# Rol de construcción cuyo `prepare` consume el pin (PD-14: el lector aditivo).
READER_ROLE = "test-writer"
READER_SUBSTAGE = "red"
# Segunda invocación del MISMO par (feature, contract_path): difiere en un campo
# de `transition_key` (`--substage`) y por eso es una transición distinta
# (interpretación 1 del docstring).
SECOND_SUBSTAGE = "green"
DISTINCT_SUBSTAGE_NO_SUPERSEDES = "red"

# Bytes del contrato pineado. `CONTRACT_BYTES` (A) es el que el fixture escribe
# en `CONTRACT_FILE`; B son los bytes CORREGIDOS de la re-aprobación (el caso
# real: el contrato cambia entre dos aprobaciones del mismo `contract_path`).
CONTRACT_BYTES_A = CONTRACT_BYTES
CONTRACT_BYTES_B = (
    b"# Spec fixture (demo-100 transition registration, corrected)\n")

# Claves de identidad de las entradas que el fixture escribe a mano (forma de
# §2.2: clave nueva y aditiva, derivada como sha256). No se afirma el algoritmo
# de la implementación: se afirma la FORMA declarada por el contrato.
KEY_PRIOR = hashlib.sha256(b"demo-100-t5-prior-approval").hexdigest()
KEY_SECOND = hashlib.sha256(b"demo-100-t5-second-approval").hexdigest()

PROSE_NOTE = "reemplaza a la anterior (prosa del fixture; PD-15)"

# Review-fix B3: aprobaciones registradas A MANO (sin `transition_key`): son el
# caso real del defecto —`--supersedes` sólo puede citar entradas CON clave— y
# su aprobación `specification` vive con el pin del contrato de su momento.
MANUAL_APPROVAL_NOTE = "entrada keyless del fixture demo-100 (B3)"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class _VigencyFixture(_BaseFixture):
    """Proyecto descartable (capa legítima del CLI) para la vigencia de PD-14.

    Modo `ready`: paquete `dispatched` con recibo durable real, de modo que una
    `--transition delivery` legítima (PD-2, T1) deja el paquete activo terminal y
    el lector (`prepare`) puede correr.
    """

    def __init__(self, base: Path) -> None:
        super().__init__(base, mode="ready")

    # -- invocación (caja negra) ------------------------------------------

    def gate(self, *extra: str) -> subprocess.CompletedProcess:
        return self.register_transition(
            "--transition", "gate", "--stage", SPEC_STAGE,
            "--approve-by", APPROVER, *extra)

    def reader(self) -> subprocess.CompletedProcess:
        """El lector, observado en negro por su efecto sobre el rol de
        construcción (rc=0 habilitado / rc=2 `approval pending`)."""
        return self.run_packet(*prepare_args(
            self.root, role=READER_ROLE, substage=READER_SUBSTAGE,
            objective="sonda de vigencia de la aprobación (fixture demo-100)"))

    def deliver(self) -> subprocess.CompletedProcess:
        """Deja el paquete activo terminal por el camino legítimo (PD-2/T1)."""
        return self.delivery()

    # -- escenario de vigencia sobre el state del fixture -----------------

    def reset_history(self, stage_history: list[dict]) -> None:
        state = self.read_state()
        state["stage_history"] = list(stage_history)
        self.write_state(state)

    def historical_entry(self) -> dict:
        """Entrada histórica SIN `transition_key` y SIN `supersedes` (la forma
        real de la historia: PD-10/PD-17 declaran la clave como aditiva)."""
        return {
            "feature": FEATURE_ID,
            "stage": "discovery",
            "approved_by": APPROVER,
            "approved_at": "2026-10-14T00:00:00Z",
            "note": "entrada histórica del fixture demo-100",
        }

    def spec_entry(self, *, contract_sha256: str, transition_key: str,
                   **extra) -> dict:
        """Entrada `specification` con el pin del contrato (D3/PD-18 de 005-001,
        la regla que PD-14 EXTIENDE) y la forma aditiva de §2.2."""
        entry = {
            "feature": FEATURE_ID,
            "stage": SPEC_STAGE,
            "transition": "gate",
            "approved_by": APPROVER,
            "approved_at": "2026-10-14T01:00:00Z",
            "contract_path": CONTRACT_FILE,
            "contract_sha256": contract_sha256,
            "transition_key": transition_key,
        }
        entry.update(extra)
        return entry

    def keyless_spec_entry(self, *, contract_sha256: str, **extra) -> dict:
        """Aprobación `specification` **SIN `transition_key`**: la forma de las
        aprobaciones registradas **a mano** (el caso B3). `--supersedes` sólo
        puede citar entradas con clave, así que ésta no es sustituible por el
        campo estructural; su pin es el de los bytes que estaban vigentes
        cuando se registró."""
        entry = {
            "feature": FEATURE_ID,
            "stage": SPEC_STAGE,
            "approved_by": APPROVER,
            "approved_at": "2026-10-14T01:00:00Z",
            "contract_path": CONTRACT_FILE,
            "contract_sha256": contract_sha256,
            "note": MANUAL_APPROVAL_NOTE,
        }
        entry.update(extra)
        return entry

    def prose_pair(self) -> list[dict]:
        """Dos entradas con el pin correcto (una por cada juego de bytes) y una
        nota en prosa en la segunda, SIN el campo `supersedes` (PD-15)."""
        return [
            self.historical_entry(),
            self.spec_entry(contract_sha256=_sha256(CONTRACT_BYTES_A),
                            transition_key=KEY_PRIOR),
            self.spec_entry(contract_sha256=_sha256(CONTRACT_BYTES_B),
                            transition_key=KEY_SECOND, note=PROSE_NOTE),
        ]

    def structural_pair(self) -> list[dict]:
        """El mismo par, con el campo ESTRUCTURAL: la segunda entrada nombra la
        primera en `supersedes` (PD-14/PD-15)."""
        return [
            self.historical_entry(),
            self.spec_entry(contract_sha256=_sha256(CONTRACT_BYTES_A),
                            transition_key=KEY_PRIOR),
            self.spec_entry(contract_sha256=_sha256(CONTRACT_BYTES_B),
                            transition_key=KEY_SECOND, supersedes=KEY_PRIOR),
        ]

    def write_contract(self, data: bytes) -> None:
        (self.root / CONTRACT_FILE).write_bytes(data)

    def gate_entries(self) -> list[dict]:
        return [e for e in entries(self.read_state())
                if e.get("transition") == "gate"]

    def contract_spec_entries(self) -> list[dict]:
        """Todas las entradas `specification` del par (feature, `contract_path`),
        en el orden del `stage_history` (append-only): las registradas por el CLI
        y las keyless que el fixture escribió a mano."""
        return [e for e in entries(self.read_state())
                if e.get("stage") == SPEC_STAGE
                and e.get("contract_path") == CONTRACT_FILE]


@pytest.fixture
def vigency_fx(tmp_path: Path) -> _VigencyFixture:
    return _VigencyFixture(tmp_path)


# ---------------------------------------------------------------- PD-14 (1)


def test_pd14_second_vigente_without_supersedes_fails_closed(
        vigency_fx: _VigencyFixture) -> None:
    """PD-14 (registro), caso 1: con un `(feature, contract_path)` que YA tiene
    una entrada `specification` vigente, registrar un segundo `gate --stage
    specification` para el MISMO `contract_path` SIN `--supersedes` → rc=2,
    marcador `state incoherent`, nombrando la entrada vigente y el campo
    `supersedes`; y SIN efectos (state byte a byte idéntico, INV-7).

    RED hoy: el CLI registra la segunda vigente (rc=0) → falla la aserción del
    rechazo; el state sí cambia (agrega una entrada).
    """
    vigency_fx.reset_history([vigency_fx.historical_entry()])
    first = vigency_fx.gate("--contract-path", CONTRACT_FILE)
    assert first.returncode == 0, (
        "precondición (comportamiento existente): el PRIMER gate de etapa 2 del "
        "par (feature, contract_path) se registra (rc=0); rc="
        f"{first.returncode}: {first.stdout!r} {first.stderr!r}")
    entry_prior = last_entry_with(vigency_fx.read_state(), transition="gate")
    assert entry_prior is not None, (
        "precondición (fixture): el primer gate debe dejar su entrada en "
        "`stage_history`")
    key_prior = entry_prior.get("transition_key")
    assert isinstance(key_prior, str) and TRANSITION_DIGEST_RE.match(key_prior), (
        f"precondición (fixture): la entrada vigente debe llevar su "
        f"`transition_key` (forma de §2.2/PD-10): {key_prior!r}")
    assert vigency_fx.validate_state().returncode == 0, (
        "precondición (fixture): el state con la aprobación vigente es "
        "coherente hoy (`validate-state` rc=0)")
    before = vigency_fx.state_bytes()

    second = vigency_fx.gate("--contract-path", CONTRACT_FILE,
                             "--substage", DISTINCT_SUBSTAGE_NO_SUPERSEDES)
    out = second.stdout + second.stderr

    assert second.returncode == 2, (
        "PD-14 violada: registrar un segundo gate de `--stage specification` "
        "para el MISMO `(feature, contract_path)` que ya tiene una entrada "
        "vigente, SIN `--supersedes`, debe fallar cerrado (rc=2); hoy rc="
        f"{second.returncode} (se registra la segunda vigente): {out!r}")
    assert STATE_INCOHERENT in out.lower(), (
        "PD-14 violada: el rechazo debe llevar el marcador "
        f"«{STATE_INCOHERENT}»: {out!r}")
    assert "supersedes" in out, (
        "PD-14 violada: el diagnóstico debe NOMBRAR el campo `supersedes` "
        f"(la marca estructural de la sustitución): {out!r}")
    assert (key_prior in out) or (CONTRACT_FILE in out), (
        "PD-14 violada: el diagnóstico debe NOMBRAR la entrada vigente (su "
        f"`transition_key` {key_prior!r} o el `contract_path` "
        f"{CONTRACT_FILE!r}): {out!r}")
    assert_unchanged(vigency_fx, before, "PD-14",
                     "segunda vigente sin `--supersedes` (INV-7)")


# ---------------------------------------------------------------- PD-14 (2-3)


def test_pd14_supersedes_replaces_the_vigent_entry_for_the_reader(
        vigency_fx: _VigencyFixture) -> None:
    """PD-14 (registro + lector), casos 2 y 3: con `--supersedes
    <transition-key>` que nombra una entrada EXISTENTE de la misma feature y el
    mismo `contract_path` → rc=0; la entrada nueva lleva `transition_key` y el
    campo `supersedes`. A partir de ahí el lector SÓLO habilita por la nueva:
    presentando el contrato de la aprobación SUSTITUIDA el rol de construcción
    ya NO se habilita (rc=2 `approval pending`, sin efectos) mientras que con el
    contrato VIGENTE sí (rc=0).

    RED hoy: el registro con `--supersedes` es rc=0 y queda escrito, pero el
    lector ignora el campo → el contrato de la aprobación sustituida SIGUE
    habilitando (rc=0) y falla la aserción del bloqueo.
    """
    vigency_fx.reset_history([vigency_fx.historical_entry()])
    first = vigency_fx.gate("--contract-path", CONTRACT_FILE)
    assert first.returncode == 0, (
        "precondición (fixture): la primera aprobación del par se registra "
        f"(rc=0); rc={first.returncode}: {first.stdout!r} {first.stderr!r}")
    key_prior = last_entry_with(vigency_fx.read_state(), transition="gate")
    assert key_prior is not None, (
        "precondición (fixture): el primer gate debe dejar su entrada")
    key_prior = key_prior.get("transition_key")
    assert isinstance(key_prior, str) and TRANSITION_DIGEST_RE.match(key_prior), (
        f"precondición (fixture): la entrada a sustituir lleva su "
        f"`transition_key`: {key_prior!r}")

    vigency_fx.write_contract(CONTRACT_BYTES_B)
    second = vigency_fx.gate("--contract-path", CONTRACT_FILE,
                             "--substage", SECOND_SUBSTAGE,
                             "--supersedes", key_prior)
    out = second.stdout + second.stderr

    assert second.returncode == 0, (
        "PD-14 violada: con `--supersedes` que nombra una entrada existente de "
        "la misma feature y el mismo `contract_path` el segundo gate debe "
        f"aceptarse (rc=0); rc={second.returncode}: {out!r}")
    entry_new = vigency_fx.gate_entries()[-1]
    key_new = entry_new.get("transition_key")
    assert isinstance(key_new, str) and TRANSITION_DIGEST_RE.match(key_new), (
        "PD-14 violada: la entrada nueva debe llevar su `transition_key` (clave "
        f"nueva y aditiva de §2.2/PD-10): {key_new!r}")
    assert entry_new.get("supersedes") == key_prior, (
        "PD-14 violada: la entrada NUEVA debe llevar el campo estructural "
        f"`supersedes` nombrando la sustituida ({key_prior!r}): "
        f"{entry_new.get('supersedes')!r}")
    assert len(vigency_fx.gate_entries()) == 2, (
        "PD-14 violada: el par queda con DOS entradas de gate (la sustituida y "
        f"la vigente) y ninguna se reescribe: {vigency_fx.gate_entries()!r}")

    delivered = vigency_fx.deliver()
    assert delivered.returncode == 0, (
        "precondición (fixture, comportamiento existente): la entrega deja el "
        f"paquete activo terminal para poder correr el lector (rc=0); rc="
        f"{delivered.returncode}: {delivered.stdout!r} {delivered.stderr!r}")

    # PD-14 (lector) — caso 3: el contrato de la aprobación SUSTITUIDA.
    vigency_fx.write_contract(CONTRACT_BYTES_A)
    state_before_reader = vigency_fx.state_bytes()
    blocked = vigency_fx.reader()
    out_blocked = blocked.stdout + blocked.stderr

    assert blocked.returncode == 2, (
        "PD-14 violada (lector): presentando el contrato de la aprobación "
        "SUSTITUIDA el rol de construcción ya NO se habilita (rc=2): el lector "
        "debe ignorar la entrada reemplazada por `supersedes`; hoy rc="
        f"{blocked.returncode}: {out_blocked!r}")
    assert APPROVAL_PENDING in out_blocked.lower(), (
        "PD-14 violada (lector): el bloqueo debe llevar el marcador "
        f"«{APPROVAL_PENDING}»: {out_blocked!r}")
    assert vigency_fx.state_bytes() == state_before_reader, (
        "PD-14/INV-7 violada (lector): el bloqueo del lector no debe modificar "
        "el state")

    # PD-14 (lector) — caso 2: el contrato VIGENTE habilita.
    vigency_fx.write_contract(CONTRACT_BYTES_B)
    enabled = vigency_fx.reader()
    assert enabled.returncode == 0, (
        "PD-14 violada (lector): con el contrato VIGENTE (el que la entrada "
        "nueva pinnea) el rol de construcción debe habilitarse (rc=0); rc="
        f"{enabled.returncode}: {enabled.stdout!r} {enabled.stderr!r}")


# ---------------------------------------------------------------- PD-15 (4)


def test_pd15_prose_note_is_not_the_control_and_the_structural_field_is(
        tmp_path: Path) -> None:
    """PD-15, caso 4 (control negativo): dos entradas con el pin correcto y una
    nota en prosa «reemplaza a la anterior» pero SIN `supersedes` → AMBAS siguen
    habilitando (el comportamiento de hoy, declarado). Con el campo estructural
    `supersedes` → sólo la nueva habilita: presentando el contrato de la primera
    el rol NO se habilita, y con el de la nueva sí.

    RED hoy: el lado de la prosa se comporta como está declarado (rc=0 en ambos
    juegos de bytes), pero el lado del campo NO: sin la marca estructural el
    reemplazo no existe y la entrada reemplazada sigue habilitando (rc=0) cuando
    el contrato exige el bloqueo (rc=2).
    """
    # (a) Prosa, bytes de la PRIMERA entrada: la prosa no invalida nada.
    prose_a = _VigencyFixture(tmp_path / "prose-a")
    prose_a.reset_history(prose_a.prose_pair())
    prose_a.write_contract(CONTRACT_BYTES_A)
    delivered = prose_a.deliver()
    assert delivered.returncode == 0, (
        "precondición (fixture): la entrega deja el paquete terminal "
        f"(rc=0); rc={delivered.returncode}: {delivered.stderr!r}")
    proc_a = prose_a.reader()
    assert proc_a.returncode == 0, (
        "PD-15 violada (control negativo, prosa): una nota en prosa que dice "
        "«reemplaza a la anterior» NO cambia qué entrada habilita; la entrada "
        "con el pin correcto sigue habilitando (rc=0); rc="
        f"{proc_a.returncode}: {proc_a.stdout!r} {proc_a.stderr!r}")

    # (b) Prosa, bytes de la SEGUNDA entrada: también habilita ("ambas siguen
    # habilitando" — la prosa no deshabilita a ninguna).
    prose_b = _VigencyFixture(tmp_path / "prose-b")
    prose_b.reset_history(prose_b.prose_pair())
    prose_b.write_contract(CONTRACT_BYTES_B)
    assert prose_b.deliver().returncode == 0, (
        "precondición (fixture): la entrega deja el paquete terminal (rc=0)")
    proc_b = prose_b.reader()
    assert proc_b.returncode == 0, (
        "PD-15 violada (control negativo, prosa): la segunda entrada (la que "
        "dice «reemplaza» en prosa) también sigue habilitando (rc=0): "
        f"rc={proc_b.returncode}: {proc_b.stdout!r} {proc_b.stderr!r}")

    # (c) Campo estructural: sólo la nueva habilita (el mismo escenario, la
    # misma presentación de bytes; lo único que cambia es `supersedes`).
    structural = _VigencyFixture(tmp_path / "structural")
    structural.reset_history(structural.structural_pair())
    structural.write_contract(CONTRACT_BYTES_A)
    assert structural.deliver().returncode == 0, (
        "precondición (fixture): la entrega deja el paquete terminal (rc=0)")
    state_before_reader = structural.state_bytes()
    blocked = structural.reader()
    out_blocked = blocked.stdout + blocked.stderr
    assert blocked.returncode == 2, (
        "PD-15 violada (el campo SÍ es el control): con `supersedes` la entrada "
        "nombrada deja de habilitar; presentando su contrato el rol de "
        f"construcción no se habilita (rc=2); hoy rc={blocked.returncode}: "
        f"{out_blocked!r}")
    assert APPROVAL_PENDING in out_blocked.lower(), (
        "PD-15 violada: el bloqueo por la aprobación reemplazada debe llevar el "
        f"marcador «{APPROVAL_PENDING}»: {out_blocked!r}")
    assert structural.state_bytes() == state_before_reader, (
        "PD-15/INV-7 violada: el bloqueo del lector no debe modificar el state")

    structural.write_contract(CONTRACT_BYTES_B)
    enabled = structural.reader()
    assert enabled.returncode == 0, (
        "PD-15 violada (el campo SÍ es el control): con `supersedes`, sólo la "
        "entrada nueva habilita; su contrato debe habilitar el rol (rc=0); rc="
        f"{enabled.returncode}: {enabled.stdout!r} {enabled.stderr!r}")


# ---------------------------------------------------------------- PD-17 (5)


def test_pd17_operation_keeps_validate_state_green_and_history_append_only(
        vigency_fx: _VigencyFixture) -> None:
    """PD-17 (+ INV-3), caso 5: el oráculo es `validate-state` rc=0 ANTES y
    DESPUÉS; ninguna entrada histórica sin `supersedes` se invalida ni se
    reescribe (append-only). Sin porcentajes ni conteos del state vivo del repo:
    las cifras se leen del fixture y sólo se comparan consigo mismas.

    RED hoy: la operación que PD-14 debe rechazar (la segunda vigente sin
    `--supersedes`) se registra (rc=0) y agrega una entrada → falla la aserción
    del rechazo (y con ella la de «sin efectos»).
    """
    vigency_fx.reset_history([vigency_fx.historical_entry()])
    first = vigency_fx.gate("--contract-path", CONTRACT_FILE)
    assert first.returncode == 0, (
        "precondición (fixture): la primera aprobación se registra (rc=0); "
        f"rc={first.returncode}: {first.stderr!r}")
    assert vigency_fx.deliver().returncode == 0, (
        "precondición (fixture): la entrega deja el paquete terminal (rc=0)")
    assert vigency_fx.validate_state().returncode == 0, (
        "PD-17 violada: `validate-state` debe dar rc=0 ANTES de la operación "
        "sobre el state con historia sin `transition_key` y sin `supersedes`")

    before_bytes = vigency_fx.state_bytes()
    before_entries = entries(vigency_fx.read_state())
    historical_before = [e for e in before_entries if "transition_key" not in e]
    assert historical_before, (
        "precondición (fixture): debe haber al menos una entrada histórica sin "
        "la clave nueva (PD-10/PD-17: la clave es aditiva)")
    assert all("supersedes" not in e for e in historical_before), (
        "precondición (fixture): la historia del fixture no tiene "
        f"`supersedes`: {historical_before!r}")

    second = vigency_fx.gate("--contract-path", CONTRACT_FILE,
                             "--substage", DISTINCT_SUBSTAGE_NO_SUPERSEDES)
    out = second.stdout + second.stderr

    assert second.returncode == 2, (
        "PD-17 violada (por PD-14): la segunda vigente sin `--supersedes` debe "
        f"rechazarse (rc=2) sin tocar la historia; hoy rc={second.returncode}: "
        f"{out!r}")
    assert STATE_INCOHERENT in out.lower(), (
        f"PD-17 violada: el rechazo debe llevar «{STATE_INCOHERENT}»: {out!r}")
    assert vigency_fx.state_bytes() == before_bytes, (
        "PD-17/INV-3 violada: la operación rechazada NO debe reescribir ni "
        "invalidar ninguna entrada de `stage_history` (append-only); el state "
        "debe quedar byte a byte idéntico")

    assert vigency_fx.validate_state().returncode == 0, (
        "PD-17 violada: `validate-state` debe dar rc=0 DESPUÉS de la operación "
        "(ninguna validación nueva se aplica a las entradas existentes)")
    after_entries = entries(vigency_fx.read_state())
    historical_after = [e for e in after_entries if "transition_key" not in e]
    assert historical_after == historical_before, (
        "PD-17/INV-3 violada: las entradas históricas sin la clave nueva deben "
        f"quedar intactas: {historical_after!r} != {historical_before!r}")

    probe = vigency_fx.reader()
    assert probe.returncode == 0, (
        "PD-17 violada: una entrada histórica sin `supersedes` NO se invalida: "
        "su pin sigue habilitando al rol de construcción (rc=0); rc="
        f"{probe.returncode}: {probe.stdout!r} {probe.stderr!r}")


# ---------------------------------------------------------------- PD-10/11 (6)


def test_pd10_pd11_gate_with_supersedes_carries_key_and_repeat_is_noop(
        vigency_fx: _VigencyFixture) -> None:
    """PD-10/PD-11 (clase `gate` con `--supersedes`), caso 6: la entrada lleva
    `transition_key` y repetir la invocación IDÉNTICA es no-op (rc=0, sin
    segunda entrada, state byte a byte idéntico, salida que nombra la entrada
    existente). El no-op no tiene efectos: tampoco deshace el reemplazo (la
    entrada sustituida sigue sin habilitar, PD-14).

    RED hoy: el registro con `--supersedes` es rc=0 y queda escrito, la
    repetición es no-op (forma aditiva de T1), pero la mitad discriminante falla:
    el lector ignora el reemplazo y el contrato de la entrada sustituida sigue
    habilitando (rc=0 en vez del bloqueo).
    """
    vigency_fx.reset_history([vigency_fx.historical_entry()])
    first = vigency_fx.gate("--contract-path", CONTRACT_FILE)
    assert first.returncode == 0, (
        "precondición (fixture): la primera aprobación se registra (rc=0); "
        f"rc={first.returncode}: {first.stderr!r}")
    entry_prior = last_entry_with(vigency_fx.read_state(), transition="gate")
    assert entry_prior is not None, (
        "precondición (fixture): el primer gate debe dejar su entrada")
    key_prior = entry_prior.get("transition_key")
    assert isinstance(key_prior, str) and TRANSITION_DIGEST_RE.match(key_prior), (
        f"precondición (fixture): la entrada a sustituir lleva su clave: "
        f"{key_prior!r}")

    vigency_fx.write_contract(CONTRACT_BYTES_B)
    extra = ("--substage", SECOND_SUBSTAGE, "--supersedes", key_prior)
    second = vigency_fx.gate("--contract-path", CONTRACT_FILE, *extra)
    out = second.stdout + second.stderr

    assert second.returncode == 0, (
        "PD-10 violada: el gate de etapa 2 con `--supersedes` debe registrarse "
        f"(rc=0) para llevar su clave de identidad; rc={second.returncode}: "
        f"{out!r}")
    entry_new = vigency_fx.gate_entries()[-1]
    key_new = entry_new.get("transition_key")
    assert isinstance(key_new, str) and TRANSITION_DIGEST_RE.match(key_new), (
        "PD-10 violada: la entrada del gate con `--supersedes` debe llevar "
        f"`transition_key`: {key_new!r}")
    assert entry_new.get("supersedes") == key_prior, (
        "PD-10 violada: la entrada nueva debe llevar el campo estructural "
        f"`supersedes` nombrando la sustituida ({key_prior!r}): "
        f"{entry_new.get('supersedes')!r}")

    state_after_second = vigency_fx.state_bytes()
    count_after_second = len(entries(vigency_fx.read_state()))

    repeat = vigency_fx.gate("--contract-path", CONTRACT_FILE, *extra)

    assert repeat.returncode == 0, (
        "PD-11 violada: repetir la invocación idéntica del gate con "
        f"`--supersedes` debe ser un no-op exitoso (rc=0); rc="
        f"{repeat.returncode}: {repeat.stdout!r} {repeat.stderr!r}")
    assert len(entries(vigency_fx.read_state())) == count_after_second, (
        "PD-11 violada: la repetición idéntica NO debe agregar una segunda "
        f"entrada de `stage_history` (sigue habiendo {count_after_second})")
    assert vigency_fx.state_bytes() == state_after_second, (
        "PD-11 violada: el state tras la repetición idéntica debe ser byte a "
        "byte idéntico al de la primera invocación")
    repeat_out = repeat.stdout + repeat.stderr
    assert key_new and key_new in repeat_out, (
        "PD-11 violada: la salida del no-op debe nombrar la entrada existente "
        f"(su `transition_key` {key_new!r}): {repeat_out!r}")

    # PD-11 (sin efectos) + PD-14: la repetición no deshace el reemplazo.
    assert vigency_fx.deliver().returncode == 0, (
        "precondición (fixture): la entrega deja el paquete terminal (rc=0)")
    vigency_fx.write_contract(CONTRACT_BYTES_A)
    blocked = vigency_fx.reader()
    out_blocked = blocked.stdout + blocked.stderr
    assert blocked.returncode == 2, (
        "PD-11/PD-14 violadas: la repetición idéntica no debe tener efectos "
        "sobre la vigencia: el contrato de la entrada reemplazada sigue sin "
        f"habilitar (rc=2); hoy rc={blocked.returncode}: {out_blocked!r}")
    assert APPROVAL_PENDING in out_blocked.lower(), (
        "PD-11/PD-14 violadas: el bloqueo debe llevar el marcador "
        f"«{APPROVAL_PENDING}»: {out_blocked!r}")


# ------------------------------------------------- Review-fix B3 — PD-14 (1)
# El predicado de vigencia de PD-14/D-8 es «el pin que NOMBRA los bytes
# actuales»: una aprobación cuyo pin ya no los nombra NO compite. El caso real
# (B3): la aprobación previa está registrada A MANO, sin `transition_key`, y
# `--supersedes` no puede citarla.


def test_b3_pd14_reapproval_with_new_bytes_over_keyless_approval_needs_no_supersedes(
        vigency_fx: _VigencyFixture) -> None:
    """PD-14 (consecuencia 1) + D-8 — caso 1 del encargo (el defecto B3): una
    aprobación `specification` **sin `transition_key`** (registrada a mano;
    `--supersedes` no puede citarla, no tiene clave) cuyo pin **ya no nombra**
    los bytes actuales (el contrato se enmendó después de esa aprobación) **no
    compite** como vigente. Entonces `gate --stage specification --contract-path
    <spec>` **sin** `--supersedes` → **rc=0**, con una entrada **NUEVA** (su
    `transition_key` y el pin derivado de los bytes actuales, PD-20) que habilita
    a los roles de construcción; la entrada vieja **no** habilita (su pin no
    nombra estos bytes) y **no** se reescribe (INV-3).

    RED hoy (defecto B3): el control de exclusión decide por `contract_path`, así
    que la entrada keyless compite aunque su pin no nombre los bytes → rc=2
    `state incoherent` pidiendo `--supersedes`, que no puede satisfacerse: la
    reaprobación obligaría a editar el state a mano. Falla por ASERCIÓN (rc=2 en
    vez de 0), nunca por import, sintaxis o fixture.
    """
    old_pin = _sha256(CONTRACT_BYTES_A)
    vigency_fx.reset_history([
        vigency_fx.historical_entry(),
        vigency_fx.keyless_spec_entry(contract_sha256=old_pin),
    ])
    # La enmienda: el contrato se corrige DESPUÉS de esa aprobación; la entrada
    # vieja conserva su pin (el «caso real» de §0.1).
    vigency_fx.write_contract(CONTRACT_BYTES_B)
    current_pin = _sha256(CONTRACT_BYTES_B)
    assert current_pin != old_pin, (
        "precondición (fixture): los bytes actuales difieren de los que la "
        "entrada keyless pinneó (su pin ya no los nombra)")

    manual = vigency_fx.contract_spec_entries()
    assert len(manual) == 1 and "transition_key" not in manual[0], (
        "precondición (fixture): la aprobación previa es `specification`, del "
        f"mismo `contract_path`, y SIN `transition_key`: {manual!r}")
    assert manual[0].get("contract_sha256") == old_pin, (
        "precondición (fixture): la entrada keyless conserva el pin de los "
        f"bytes que aprobó: {manual[0].get('contract_sha256')!r}")
    assert "supersedes" not in manual[0], (
        "precondición (fixture): la entrada keyless no sustituye a ninguna otra")
    assert vigency_fx.validate_state().returncode == 0, (
        "precondición (fixture): el state con la aprobación keyless y el "
        "contrato enmendado es coherente hoy (`validate-state` rc=0)")

    proc = vigency_fx.gate("--contract-path", CONTRACT_FILE)
    out = proc.stdout + proc.stderr

    assert proc.returncode == 0, (
        "PD-14 violada (consecuencia 1 / B3): reaprobar tras la enmienda de los "
        "bytes del contrato NO necesita `--supersedes` —la entrada vieja no "
        "compite porque su pin ya no nombra los bytes actuales—; hoy rc="
        f"{proc.returncode}: {out!r}")
    assert STATE_INCOHERENT not in out.lower(), (
        "PD-14 violada (consecuencia 1 / B3): el registro no debe pedir el "
        f"campo estructural `--supersedes`: {out!r}")

    spec_entries = vigency_fx.contract_spec_entries()
    assert len(spec_entries) == 2, (
        "PD-14 violada (B3): la reaprobación agrega UNA entrada nueva del par "
        f"(append-only): {spec_entries!r}")
    entry_new = spec_entries[-1]
    key_new = entry_new.get("transition_key")
    assert isinstance(key_new, str) and TRANSITION_DIGEST_RE.match(key_new), (
        "PD-14 violada (B3): la entrada nueva debe llevar su `transition_key` "
        f"(clave nueva y aditiva de §2.2/PD-10): {key_new!r}")
    assert entry_new.get("contract_sha256") == current_pin, (
        "PD-20 violada (B3): la aprobación nueva debe llevar el pin DERIVADO de "
        "los bytes actuales (el pin es lo que la hace la vigente): esperado "
        f"{current_pin!r}, entrada {entry_new.get('contract_sha256')!r}")
    assert entry_new.get("supersedes") is None, (
        "PD-14 violada (B3): la entrada vieja NO compite, así que la nueva no "
        "lleva ninguna sustitución (no hay clave vieja que citar): "
        f"{entry_new.get('supersedes')!r}")
    assert spec_entries[:-1] == manual, (
        "PD-14/INV-3 violada (B3): la entrada keyless queda INTACTA (no se "
        "reescribe ni pierde su pin): "
        f"{spec_entries[:-1]!r} != {manual!r}")
    assert vigency_fx.validate_state().returncode == 0, (
        "PD-14 violada (B3): el state con la reaprobación debe seguir coherente")

    # La entrada nueva es la que habilita a los roles de construcción; la vieja
    # no puede serlo (su pin no nombra los bytes actuales).
    assert vigency_fx.deliver().returncode == 0, (
        "precondición (fixture, comportamiento existente): la entrega deja el "
        "paquete activo terminal para poder correr el lector (rc=0)")
    enabled = vigency_fx.reader()
    assert enabled.returncode == 0, (
        "PD-14 violada (B3): la entrada nueva (pin de los bytes actuales) debe "
        "habilitar al rol de construcción (rc=0); la vieja no habilita porque "
        f"su pin NO nombra estos bytes; rc={enabled.returncode}: "
        f"{enabled.stdout!r} {enabled.stderr!r}")


# ------------------------------------------------- Review-fix B3 — PD-14 (2-3)
# Los MISMOS bytes siguen exigiendo el campo estructural (consecuencia 2) y el
# rechazo no tiene efectos (consecuencia 3, INV-7).


def test_b3_pd14_same_bytes_still_requires_supersedes_and_the_amendment_does_not(
        vigency_fx: _VigencyFixture) -> None:
    """PD-14 (consecuencias 2 y 3) + PD-20 — casos 2 y 3 del encargo: con la
    entrada vigente **CON clave** cuyo pin **nombra los bytes actuales**,
    reaprobar los **MISMOS** bytes sigue exigiendo el campo estructural: sin
    `--supersedes` → **rc=2**, marcador `state incoherent`, nombrando la entrada
    vigente y el campo `supersedes`, y el state queda **byte a byte idéntico**
    (INV-7, caso 3); **con** `--supersedes <transition-key>` que nombra esa
    entrada → **rc=0**, con el campo escrito en la entrada nueva. Este
    comportamiento **no cambia** (los casos anteriores del focal ya lo fijan con
    otros flujos; acá se lo ejerce sobre el predicado nuevo).

    Mitad discriminante del mismo flujo (PD-14 consecuencia 1: «tenga o no clave
    la entrada vieja»): **enmendados** los bytes, esa misma entrada vigente ya
    **no** compite → un `gate` posterior del mismo `contract_path` **sin**
    `--supersedes` → **rc=0**. RED hoy en esa mitad: el control sigue comparando
    `contract_path` y rechaza (rc=2) aunque el pin de la vigente ya no nombre los
    bytes.
    """
    vigency_fx.reset_history([vigency_fx.historical_entry()])
    first = vigency_fx.gate("--contract-path", CONTRACT_FILE)
    assert first.returncode == 0, (
        "precondición (comportamiento existente): el primer gate de etapa 2 del "
        f"par (feature, contract_path) se registra (rc=0); rc={first.returncode}: "
        f"{first.stdout!r} {first.stderr!r}")
    entry_prior = vigency_fx.gate_entries()[-1]
    key_prior = entry_prior.get("transition_key")
    assert isinstance(key_prior, str) and TRANSITION_DIGEST_RE.match(key_prior), (
        f"precondición (fixture): la entrada vigente lleva su clave: {key_prior!r}")
    same_pin = _sha256(CONTRACT_BYTES_A)
    assert entry_prior.get("contract_sha256") == same_pin, (
        "precondición (fixture): la entrada vigente NOMBRA los bytes actuales "
        "(sin enmienda, su pin coincide con el contrato del fixture): "
        f"{entry_prior.get('contract_sha256')!r} != {same_pin!r}")

    # Caso 2 (rechazo) y caso 3 (sin efectos): MISMOS bytes, sin el campo.
    before = vigency_fx.state_bytes()
    second = vigency_fx.gate("--contract-path", CONTRACT_FILE,
                             "--substage", DISTINCT_SUBSTAGE_NO_SUPERSEDES)
    out = second.stdout + second.stderr

    assert second.returncode == 2, (
        "PD-14 violada (consecuencia 2): con una entrada `specification` "
        "vigente que NOMBRA los bytes actuales, reaprobar los MISMOS bytes sin "
        f"`--supersedes` debe fallar cerrado (rc=2); hoy rc="
        f"{second.returncode}: {out!r}")
    assert STATE_INCOHERENT in out.lower(), (
        "PD-14 violada (consecuencia 2): el rechazo debe llevar el marcador "
        f"«{STATE_INCOHERENT}»: {out!r}")
    assert "supersedes" in out, (
        "PD-14 violada (consecuencia 2): el diagnóstico debe NOMBRAR el campo "
        f"estructural `supersedes`: {out!r}")
    assert (key_prior in out) or (CONTRACT_FILE in out), (
        "PD-14 violada (consecuencia 2): el diagnóstico debe NOMBRAR la entrada "
        f"vigente (su `transition_key` {key_prior!r} o el `contract_path` "
        f"{CONTRACT_FILE!r}): {out!r}")
    assert_unchanged(vigency_fx, before, "PD-14",
                     "los MISMOS bytes sin `--supersedes` (consecuencia 3, "
                     "INV-7)")

    # Caso 2 (aceptación con el campo): mismo bytes, `--supersedes` citando la
    # entrada vigente.
    third = vigency_fx.gate("--contract-path", CONTRACT_FILE,
                            "--substage", DISTINCT_SUBSTAGE_NO_SUPERSEDES,
                            "--supersedes", key_prior)
    out_third = third.stdout + third.stderr
    assert third.returncode == 0, (
        "PD-14 violada (consecuencia 2): con `--supersedes <transition-key>` que "
        "nombra una entrada existente de la misma feature y el mismo "
        f"`contract_path` el registro debe aceptarse (rc=0); rc="
        f"{third.returncode}: {out_third!r}")
    entry_new = vigency_fx.gate_entries()[-1]
    key_new = entry_new.get("transition_key")
    assert isinstance(key_new, str) and TRANSITION_DIGEST_RE.match(key_new), (
        "PD-14 violada: la entrada nueva debe llevar su `transition_key`: "
        f"{key_new!r}")
    assert entry_new.get("transition_key") != key_prior, (
        "PD-14 violada: la aprobación nueva es una transición distinta de la "
        f"sustituida ({key_prior!r}): {key_new!r}")
    assert entry_new.get("supersedes") == key_prior, (
        "PD-14 violada: la entrada NUEVA debe llevar el campo estructural "
        f"`supersedes` nombrando la sustituida ({key_prior!r}): "
        f"{entry_new.get('supersedes')!r}")
    assert entry_new.get("contract_sha256") == same_pin, (
        "PD-20 violada: el pin de la entrada nueva se DERIVA de los bytes "
        f"actuales: {entry_new.get('contract_sha256')!r} != {same_pin!r}")
    assert vigency_fx.gate_entries()[:2] == [entry_prior, entry_new] and len(
        vigency_fx.gate_entries()) == 2, (
        "PD-14/INV-3 violada: el par queda con DOS entradas y ninguna se "
        f"reescribe: {vigency_fx.gate_entries()!r}")
    assert vigency_fx.validate_state().returncode == 0, (
        "PD-14 violada: el state con la sustitución de los MISMOS bytes debe "
        "seguir coherente")

    # Mitad discriminante (consecuencia 1, «tenga o no clave la entrada vieja»):
    # enmendados los bytes, la vigente ya no compite → no hace falta el campo.
    vigency_fx.write_contract(CONTRACT_BYTES_B)
    amended_pin = _sha256(CONTRACT_BYTES_B)
    assert amended_pin != same_pin, (
        "precondición (fixture): el contrato enmendado tiene otros bytes")

    fourth = vigency_fx.gate("--contract-path", CONTRACT_FILE,
                             "--substage", SECOND_SUBSTAGE)
    out_fourth = fourth.stdout + fourth.stderr
    assert fourth.returncode == 0, (
        "PD-14 violada (consecuencia 1): tras la enmienda ninguna entrada "
        "vigente NOMBRA los bytes actuales, así que un `gate` posterior del "
        "mismo `contract_path` NO necesita `--supersedes` (rc=0); hoy rc="
        f"{fourth.returncode}: {out_fourth!r}")
    entry_amended = vigency_fx.gate_entries()[-1]
    assert entry_amended.get("contract_sha256") == amended_pin, (
        "PD-20 violada (consecuencia 1): la aprobación de los bytes enmendados "
        "debe llevar el pin DERIVADO de los bytes actuales: "
        f"{entry_amended.get('contract_sha256')!r} != {amended_pin!r}")
    assert vigency_fx.validate_state().returncode == 0, (
        "PD-14 violada: el state tras la reaprobación de los bytes enmendados "
        "debe seguir coherente")


# ------------------------------------------------- Review-fix B3 — PD-17 (4)


def test_b3_pd17_amendment_keeps_validate_state_green_and_history_untouched(
        vigency_fx: _VigencyFixture) -> None:
    """PD-17 (+ INV-3) — caso 4 del encargo (aditividad): el oráculo es
    `validate-state` **rc=0 ANTES y DESPUÉS** de la operación; ninguna entrada
    histórica **sin `transition_key`** se invalida ni se reescribe. Se ejerce
    sobre el flujo del caso 1 (la reaprobación tras la enmienda, con la
    aprobación previa keyless): la entrada keyless queda **intacta** (no pierde su
    pin, no gana la clave nueva y no se le exige ningún campo) y la operación
    **sólo anexa** (append-only). Sin porcentajes ni conteos del state vivo del
    repo: las cifras se leen del fixture y sólo se comparan consigo mismas.

    RED hoy (por la mitad B3): la reaprobación tras la enmienda se rechaza con
    rc=2, así que la operación no se registra y la foto de la historia posterior
    no se alcanza. Falla por ASERCIÓN de contrato.
    """
    old_pin = _sha256(CONTRACT_BYTES_A)
    vigency_fx.reset_history([
        vigency_fx.historical_entry(),
        vigency_fx.keyless_spec_entry(contract_sha256=old_pin),
    ])
    vigency_fx.write_contract(CONTRACT_BYTES_B)

    assert vigency_fx.validate_state().returncode == 0, (
        "PD-17 violada: `validate-state` debe dar rc=0 ANTES de la operación "
        "sobre el state con la aprobación keyless y el contrato enmendado")

    before_entries = entries(vigency_fx.read_state())
    historical_before = [e for e in before_entries if "transition_key" not in e]
    assert len(historical_before) >= 2, (
        "precondición (fixture): hay entradas históricas SIN la clave nueva "
        f"(PD-10/PD-17: la clave es aditiva): {historical_before!r}")
    assert all("supersedes" not in e for e in historical_before), (
        "precondición (fixture): la historia del fixture no tiene "
        f"`supersedes`: {historical_before!r}")

    proc = vigency_fx.gate("--contract-path", CONTRACT_FILE)
    out = proc.stdout + proc.stderr

    assert proc.returncode == 0, (
        "PD-17 violada (por PD-14/B3): la reaprobación tras la enmienda debe "
        f"registrarse (rc=0) para poder evaluar la aditividad; hoy rc="
        f"{proc.returncode}: {out!r}")
    assert vigency_fx.validate_state().returncode == 0, (
        "PD-17 violada: `validate-state` debe dar rc=0 DESPUÉS de la operación "
        "(ninguna validación nueva se aplica a las entradas existentes)")

    after_entries = entries(vigency_fx.read_state())
    historical_after = [e for e in after_entries if "transition_key" not in e]
    assert historical_after == historical_before, (
        "PD-17/INV-3 violada: las entradas históricas sin `transition_key` "
        "deben quedar intactas (no se invalidan, no se reescriben y no se les "
        f"exige la clave nueva): {historical_after!r} != {historical_before!r}")
    assert after_entries[:len(before_entries)] == before_entries, (
        "PD-17/INV-3 violada: la operación es append-only (las entradas "
        f"previas no cambian): {after_entries[:len(before_entries)]!r} != "
        f"{before_entries!r}")
    assert len(after_entries) == len(before_entries) + 1, (
        "PD-17 violada: la transición registrada deja UNA entrada nueva "
        f"({len(before_entries)} → {len(after_entries)})")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
