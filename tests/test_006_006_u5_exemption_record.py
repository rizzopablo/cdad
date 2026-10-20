#!/usr/bin/env python3
"""006-006 U5 RED — la exención del owner, registrada e incluida en la
identidad de la transición, SÓLO cuando se declara.

Contract:
- docs/specs/006-006-spec-plan-review/spec.md §2.7 (R-11..R-14, PD-9,
  INV-12, INV-13, D-13, D-14, D-15, V-4, V-7, V-8) y §3 (PD-9, PD-14).
- docs/specs/006-006-spec-plan-review/plan.md §3 ficha U5 (el RED, sus
  controles y sus regresiones) y §4 (A-1).

Superficie observable bajo prueba (caja negra: SOLO subprocess sobre el CLI;
el módulo de implementación NUNCA se importa y su código NUNCA se lee — el
mismo patrón que los focales de 005-012/005-014/006-005):

    python3 skills/cdad-cycle/scripts/cdad_packet.py register-transition \\
        --project-root <ABS> --transition gate --stage specification \\
        --approve-by <texto> --contract-path <p> \\
        [--exempted-by <t>] [--exemption-reason <t>] [--requested-by <t>] \\
        [--delegated] [--supersedes <transition-key>]
    python3 skills/cdad-cycle/scripts/cdad_packet.py prepare --project-root <ABS> ...
    python3 skills/cdad-cycle/scripts/cdad_packet.py validate-state --project-root <ABS>

Fixture: proyecto descartable en un tempdir (política válida, contrato
pineado, delegación HITL vigente, ejecución v2 y paquete reales) construido
por el camino legítimo del CLI (`prepare` → `--record-dispatch` → `receive`),
con el `HOME` del subproceso en un tempdir VACÍO (nunca el HOME real, nunca
este repo). Los ids del fixture son sintéticos y anónimos. Ninguna mutación
toca el state de este repo. No hay mocks sobre el plumbing.

ORÁCULES DECLARADOS (interfaces que fija este RED, derivadas del contrato):

1. Las cuatro banderas de la exención son `--exempted-by`,
   `--exemption-reason`, `--requested-by` y `--delegated` (interruptor), y
   son admisibles SÓLO con `--transition gate` (spec §2.7, plan U5 zona 1).
   La ENTRADA de `stage_history` suma entonces los campos planos
   `exempted_by`, `reason`, `requested_by` y `delegated` (spec §2.7, plan U5
   zona 2). Sin las banderas, la entrada NO lleva esos campos.
2. El bloque `exemption` del payload de identidad lleva EXACTAMENTE los campos
   declarados (R-12) y sólo existe cuando la invocación declara la exención
   (R-11). Sin exención declarada, el payload NO lleva bloque y es byte a byte
   idéntico al del producto ANTERIOR (R-13, D-14): las identidades históricas
   se conservan y NO hay enmienda de 005-014 PD-23 ni de 006-005 PD-19(b).
3. La `transition_key` se RECOMPUTA desde el payload escrito (mismo oráculo
   vigente de 005-012 PD-10: `sha256` de la serialización canónica
   `json.dumps(payload, ensure_ascii=False, sort_keys=True,
   separators=(",", ":"))` sobre UTF-8).
4. La REPETICIÓN idéntica (misma exención) es un no-op: rc=0, sin segunda
   entrada, state byte a byte idéntico y salida que nombra la entrada
   existente (PD-11, R-14(a)).
5. La repetición que CAMBIA la exención NO es un no-op: o se registra por
   `--supersedes` (la entrada previa sigue en el historial y la nueva la
   marca) o se RECHAZA explícitamente nombrando la entrada vigente y la vía
   permitida; nunca rc=0 sin registrar (PD-9, INV-12, D-13).
6. El recorrido A→B→A (A: aprobación sin exención; B: aprobación con
   exención registrada con `--supersedes A`; la tercera invocación vuelve al
   payload de A) NO puede ser un no-op que deje B vigente (R-14(b), D-15):
   - sin `--supersedes` ⇒ el rechazo vigente de una sola aprobación (que
     nombra la entrada vigente y la vía `--supersedes`);
   - con `--supersedes` ⇒ el RECHAZO DE COLISIÓN: rc≠0, marcador
     `state incoherent`, nombrando la clave que colisiona y que NO es la
     vigente, la clave de la vigente y las DOS salidas (registrar con un
     valor distinguible, o reconciliar);
   - en ambos casos el state queda byte a byte idéntico y la aprobación
     vigente sigue en vigor, comprobado CON EL LECTOR (el `prepare` de un rol
     de construcción: habilitado por la entrada vigente, bloqueado por la
     sustituida), no sólo con el conteo de entradas.
7. La SALIDA que el rechazo de colisión declara existe: la retirada de la
   exención se registra con un VALOR DISTINGUIBLE (evidencia citada con
   `--artifact`, que entra en la identidad), con lo que la entrada nueva tiene
   clave propia, queda vigente y NO lleva bloque `exemption`.

CONTROLES DECLARADOS (verdes con el producto en vigor; NO son aserciones que
deban fallar al abrir el RED — plan §3 U5 y §4 A-1):

- El recorrido de DOS REVISIONES (B-3, R-13, V-7) en `gate`, `closure` y
  `disposition`: el producto ANTERIOR (la revisión del producto vigente
  cuando se abrió este RED, materializada con `git archive` en un directorio
  temporal) registra la orden y el producto vigente la registra sobre una
  COPIA byte a byte idéntica del mismo proyecto; el `transition_key_payload`
  escrito por el vigente es BYTE-IDÉNTICO al del anterior, la `transition_key`
  es la misma, y la repetición de la misma orden SIN exención sobre la entrada
  del producto anterior es un NO-OP (rc=0, sin segunda entrada, state byte a
  byte idéntico, salida que nombra la entrada histórica). El producto
  anterior queda representado por su producto real —no por una simulación— y
  por la FÓRMULA DE IDENTIDAD CONGELADA en este archivo (las 16 claves y la
  serialización canónica, copiadas de la forma que tenían al abrirse este
  RED).
- La invocación SIN las banderas escribe una entrada SIN los campos de
  exención (control negativo del caso positivo).
- Las clases SIN aprobación vigente (closure, disposition) conservan su
  comportamiento (replay = no-op): es lo que 005-014 PD-23 y 006-005
  PD-19(b) fijan (regresiones de la ficha).

Mapeo test → postcondición:

  test_pd9_exemption_flags_write_the_four_fields_in_the_entry
      -> PD-9 (la entrada de la exención): las cuatro banderas escriben
         `exempted_by`, `reason`, `requested_by` y `delegated`.
  test_pd9_without_the_flags_the_entry_carries_no_exemption_field
      -> PD-9 (control negativo): sin las banderas, la entrada no lleva
         esos campos.
  test_pd9_flags_outside_the_gate_class_are_rejected_naming_the_class
      -> PD-9 (admisibilidad): las banderas fuera de la clase `gate` se
         rechazan nombrando la clase, sin efectos.
  test_pd9_exemption_entry_does_not_enable_construction
      -> PD-9 + PD-14: la entrada de exención NO habilita construcción por
         sí sola (el pin de aprobación sigue siendo el que manda).
  test_pd9_approval_with_exemption_stays_vigente_for_the_closure
      -> PD-9 + V-4: la aprobación con exención sigue vigente para el
         cierre (PD-8(b)) y una segunda aprobación sin `--supersedes`
         sigue rechazándose.
  test_pd9_payload_carries_the_exemption_block_with_exactly_the_declared_fields
      -> PD-9 + R-11/R-12: el payload lleva un bloque `exemption` con
         exactamente los campos declarados y la clave se recomputa desde él.
  test_pd9_payload_block_carries_only_the_declared_fields
      -> PD-9 + R-12 (el otro lado de «exactamente»): con un subconjunto de
         las banderas, el bloque lleva sólo esos campos (los no declarados no
         están: no como `null`).
  test_pd9_identical_repetition_with_the_same_exemption_is_a_noop
      -> PD-9 + PD-11 + R-14(a): la repetición idéntica es un no-op.
  test_pd9_repetition_that_changes_the_exemption_is_not_a_noop
      -> PD-9 + B-2 + INV-12: la repetición que cambia la exención se
         registra por `--supersedes` o se rechaza explícitamente; nunca
         rc=0 sin registrar.
  test_pd9_two_revisions_gate_keeps_the_identity_and_the_replay_is_a_noop
      -> PD-9 + R-13 + D-14 + V-7 (control): recorrido de dos revisiones en
         `gate`.
  test_pd9_two_revisions_closure_keeps_the_identity_and_the_replay_is_a_noop
      -> PD-9 + R-13 + PD-23 + V-7 (control): recorrido de dos revisiones en
         `closure`.
  test_pd9_two_revisions_disposition_keeps_the_identity_and_the_replay_is_a_noop
      -> PD-9 + R-13 + PD-19(b) + V-7 (control): recorrido de dos revisiones
         en `disposition`.
  test_pd9_aba_walk_rejects_the_return_to_the_previous_payload
      -> PD-9 + R-14(b) + D-15 + V-8: el recorrido A→B→A rechaza la vuelta
         al payload anterior (las dos ramas) y la vigente sigue en vigor.
  test_pd9_aba_walk_registers_the_return_with_a_distinguishable_value
      -> PD-9 + R-14(b) + D-15: la salida que el rechazo declara existe:
         el registro con valor distinguible deja una entrada nueva, vigente
         y sin bloque `exemption`.

A-1 (plan §4): este RED NO REEMPLAZA ningún oráculo vigente: los oráculos de
identidad recomputan la clave desde el payload escrito y comprueban campos
sueltos (no fijan el conjunto de claves ni un digest literal), y los ficheros
de 005-014/006-005 no se tocan: se EJECUTAN como regresiones. Los REDs
nuevos AÑADEN casos.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from test_004_002_t2_bootstrap import prepare_args
from test_005_012_t1_register_transition_base import (
    APPROVER,
    CONTRACT_FILE,
    STATE_INCOHERENT,
    TRANSITION_DIGEST_RE,
    assert_unchanged,
    canonical_digest,
    entries,
)
from test_005_012_t3_closure_dispatch_resolution import (
    CLOSURE_REL,
    CLOSURE_STAGE,
    _ClosureFixture,
)
from test_005_012_t5_approval_vigency import _VigencyFixture
from test_006_005_u5_disposition_failed import _U5Fixture

REPO_ROOT = Path(__file__).resolve().parents[1]
CURRENT_CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"

# ---------------------------------------------------------------- oráculos

# La etapa 2 es la que lleva el pin del contrato (la vigencia de PD-14).
SPEC_STAGE = "specification"
# Etiqueta de un gate SIN pin de contrato (no habilita construcción por sí
# solo: es el control de «la exención no habilita construir»).
FREE_STAGE = "tdd-review"
# El LECTOR: un rol de construcción, observado en NEGRO por su efecto
# (rc=0 habilitado / rc=2 `approval pending`).
READER_ROLE = "test-writer"
READER_SUBSTAGE = "red"
APPROVAL_PENDING = "approval pending"
ALREADY_REGISTERED = "already registered"

# Los valores declarados de la exención (sintéticos y anónimos).
EXEMPTED_BY = "Owner Demo (fixture 006-006 U5)"
EXEMPTION_REASON = "revision proporcional exenta por el owner (fixture U5)"
REQUESTED_BY = "Requester Demo (fixture 006-006 U5)"

# Las cuatro banderas de la exención (spec §2.7, plan U5 zona 1).
EXEMPTED_BY_FLAG = "--exempted-by"
EXEMPTION_REASON_FLAG = "--exemption-reason"
REQUESTED_BY_FLAG = "--requested-by"
DELEGATED_FLAG = "--delegated"

# Los cuatro campos que la ENTRADA suma (planos) y los que el bloque
# `exemption` del payload lleva (R-12).
EXEMPTION_FIELDS = ("exempted_by", "reason", "requested_by", "delegated")
EXEMPTION_BLOCK = "exemption"
PAYLOAD_KEY = "transition_key_payload"

# La FÓRMULA DE IDENTIDAD ANTERIOR, CONGELADA en este archivo: las 16 claves
# del payload canónico de la revisión del producto vigente cuando se abrió
# este RED, con la misma regla «toda clave presente; un insumo ausente vale
# `null`» (R-11/R-13). Copia LITERAL del contrato observado, no una
# reimplementación: el oráculo fuerte de esta recorrido es la comparación
# byte a byte con el producto ANTERIOR (el `git archive` de abajo).
FROZEN_PAYLOAD_KEYS = frozenset({
    "approved_by",
    "artifacts",
    "closure",
    "contract",
    "current_stage",
    "execution_id",
    "feature_id",
    "packet_id",
    "plan",
    "postcondition",
    "receipt_sha256",
    "replaced_by",
    "resolution",
    "stage",
    "substage",
    "transition",
})


def frozen_identity_payload(*, transition: str, stage: str, execution_id: str,
                            feature_id: str, approved_by: str | None = None,
                            substage: str | None = None,
                            current_stage: str | None = None,
                            packet_id: str | None = None,
                            resolution: str | None = None,
                            receipt_sha256: str | None = None,
                            contract: dict | None = None,
                            plan: dict | None = None,
                            closure: dict | None = None,
                            postcondition: dict | None = None,
                            replaced_by: str | None = None,
                            artifacts: list | None = None) -> dict:
    """COPIA CONGELADA de la fórmula de identidad anterior (R-11/R-13)."""
    return {
        "approved_by": approved_by,
        "artifacts": list(artifacts or []),
        "closure": closure,
        "contract": contract,
        "current_stage": current_stage,
        "execution_id": execution_id,
        "feature_id": feature_id,
        "packet_id": packet_id,
        "plan": plan,
        "postcondition": postcondition,
        "receipt_sha256": receipt_sha256,
        "replaced_by": replaced_by,
        "resolution": resolution,
        "stage": stage,
        "substage": substage,
        "transition": transition,
    }


# El producto ANTERIOR: la revisión del producto vigente CUANDO SE ABRIÓ ESTE
# RED (antes de la implementación de U5). Se materializa con `git archive` en
# un directorio temporal —nunca con la instalación del HOME— y sus bytes son
# la representación real del «producto anterior» del recorrido de dos
# revisiones (plan §3 U5, R-13, V-7).
PREVIOUS_PRODUCT_COMMIT = "eabe2801683fe35852672d9afcad3d4c5c728cde"

# El contrato NO fija la forma léxica de los mensajes: se acepta cualquiera
# de las formas que el propio contrato describe. Lo que el contrato SÍ fija
# es el CONTENIDO (las claves nombradas, el marcador y las dos salidas).
VIGENCY_TOKENS = ("vigente", "vigency", "current", "active", "in force",
                  "en vigor")
DISTINGUISHABLE_EXIT_TOKENS = ("artifact", "artefact", "distingu")
RECONCILE_EXIT_TOKENS = ("reconcil",)


# ---------------------------------------------------------------- helpers


def gate_entries(state: dict) -> list[dict]:
    """Las entradas `transition: "gate"` de `stage_history`."""
    return [e for e in entries(state) if e.get("transition") == "gate"]


def last_transition_entry(state: dict, transition: str) -> dict:
    found = [e for e in entries(state) if e.get("transition") == transition]
    assert found, (
        f"precondición (fixture): no hay entrada `transition: {transition!r}` "
        f"en `stage_history`: {entries(state)!r}")
    return found[-1]


def state_bytes(root: Path) -> bytes:
    return (root / "docs" / ".cdad-state.json").read_bytes()


def read_state(root: Path) -> dict:
    return json.loads((root / "docs" / ".cdad-state.json").read_text(
        encoding="utf-8"))


def assert_flags_known(proc: subprocess.CompletedProcess, label: str) -> str:
    """El CLI debe CONOCER las banderas de la exención.

    Un error de uso («unrecognized arguments») significa que la bandera no
    existe todavía: la invocación no ejercitó la postcondición y el fallo
    sería por la razón equivocada. Este RED falla aquí, con un diagnóstico
    que lo dice.
    """
    out = proc.stdout + proc.stderr
    assert "unrecognized arguments" not in out, (
        f"PD-9 violada ({label}): el CLI no conoce las banderas de la "
        f"exención (`{EXEMPTED_BY_FLAG}`, `{EXEMPTION_REASON_FLAG}`, "
        f"`{REQUESTED_BY_FLAG}`, `{DELEGATED_FLAG}`): la invocación murió en "
        f"el parser (error de uso) sin ejercer la postcondición: {out!r}")
    return out


def exemption_flags(*, exempted_by: str | None = EXEMPTED_BY,
                    reason: str | None = EXEMPTION_REASON,
                    requested_by: str | None = REQUESTED_BY,
                    delegated: bool = True) -> list[str]:
    """Las banderas de la exención, tal y como las declara el contrato."""
    flags: list[str] = []
    if exempted_by is not None:
        flags += [EXEMPTED_BY_FLAG, exempted_by]
    if reason is not None:
        flags += [EXEMPTION_REASON_FLAG, reason]
    if requested_by is not None:
        flags += [REQUESTED_BY_FLAG, requested_by]
    if delegated:
        flags += [DELEGATED_FLAG]
    return flags


def previous_product_cli(dest: Path) -> Path:
    """El producto ANTERIOR, materializado con `git archive` (temporal)."""
    dest.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "archive", PREVIOUS_PRODUCT_COMMIT,
         "skills"],
        capture_output=True, check=False)
    assert archive.returncode == 0, (
        "precondición (entorno): no se pudo materializar el producto ANTERIOR "
        f"({PREVIOUS_PRODUCT_COMMIT}) con `git archive`; rc="
        f"{archive.returncode}: {archive.stderr[:400]!r}")
    subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout,
                   check=True)
    cli = dest / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
    assert cli.is_file(), (
        "precondición (entorno): el producto anterior no trae el CLI: "
        f"{cli}")
    return cli


def copy_project(src: Path, dest: Path) -> Path:
    """Una COPIA byte a byte idéntica del proyecto (mismo `execution_id`, mismo
    `packet_id`, mismos bytes citados)."""
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    return dest


def run_with(fx, cli: Path, *args: str) -> subprocess.CompletedProcess:
    """La MISMA invocación, con otro producto (el anterior)."""
    return fx._run(cli, list(args))


# ---------------------------------------------------------------- fixtures


class _ExemptionFixture(_VigencyFixture):
    """Proyecto descartable para la exención (clase `gate`).

    - El historial arranca SIN aprobación vigente (sólo la entrada histórica
      de `discovery`): así el LECTOR puede distinguir «habilitado» de
      «bloqueado» y el caso de la exención que NO habilita construcción es
      observable.
    - El paquete activo queda TERMINAL (una entrega legítima): el LECTOR
      (`prepare`) exige un paquete terminal para llegar a la comprobación del
      pin (misma forma que `tests/test_005_012_t5_approval_vigency.py`).
    """

    def __init__(self, base: Path) -> None:
        super().__init__(base)
        self.reset_history([self.historical_entry()])
        delivered = self.deliver()
        assert delivered.returncode == 0, (
            "precondición (fixture, comportamiento existente): la entrega "
            f"legítima debe registrar la transición (rc=0): "
            f"{delivered.stdout!r} {delivered.stderr!r}")

    # -- invocación (caja negra) ------------------------------------------

    def gate(self, *extra: str, stage: str = SPEC_STAGE,
             approve_by: str = APPROVER) -> subprocess.CompletedProcess:
        return self.register_transition(
            "--transition", "gate", "--stage", stage,
            "--approve-by", approve_by, *extra)

    def gate_with_exemption(self, *extra: str, **kwargs
                            ) -> subprocess.CompletedProcess:
        return self.gate(*extra, *exemption_flags(**kwargs))

    def run_with(self, cli: Path, *args: str) -> subprocess.CompletedProcess:
        """La MISMA invocación, con otro producto (el anterior)."""
        return run_with(self, cli, *args)

    def reader_in_copy(self, dest: Path) -> subprocess.CompletedProcess:
        """El LECTOR, observado en NEGRO, sobre una COPIA del proyecto.

        La sonda `prepare` PUBLICA un paquete (muta el state): el recorrido
        necesita el state byte a byte idéntico, y la sonda del lector NO
        puede contaminarlo. La copia conserva el state, el `execution_id` y el
        `packet_id`, de modo que la decisión del lector es la misma.
        """
        copy_project(self.root, dest)
        return self.run_packet(*prepare_args(
            dest, role=READER_ROLE, substage=READER_SUBSTAGE,
            objective="sonda de vigencia (fixture 006-006 U5)"))


class _ExemptionClosureFixture(_ClosureFixture):
    """Proyecto descartable listo para CERRAR (recibo durable + aprobación)."""

    def __init__(self, base: Path) -> None:
        super().__init__(base, mode="ready")

    def drop_approval(self) -> None:
        """Quita la aprobación `specification` del historial (mutación
        declarada del fixture, la misma forma que `reset_history` en
        `tests/test_005_012_t5_approval_vigency.py`): deja el proyecto SIN
        aprobación vigente, que es la precondición del caso V-4."""
        state = self.read_state()
        state["stage_history"] = [
            e for e in entries(state) if e.get("stage") != "specification"]
        self.write_state(state)

    def gate_with_exemption(self, *extra: str
                            ) -> subprocess.CompletedProcess:
        return self.register_transition(
            "--transition", "gate", "--stage", SPEC_STAGE,
            "--approve-by", APPROVER, *exemption_flags(), *extra)

    def closure(self) -> subprocess.CompletedProcess:
        return self.register_transition(
            "--transition", "closure", "--stage", CLOSURE_STAGE,
            "--approve-by", APPROVER, "--closure-path", CLOSURE_REL)


class _ExemptionDispositionFixture(_U5Fixture):
    """Proyecto descartable con un paquete `dispatched` listo para disponer."""

    def __init__(self, base: Path) -> None:
        super().__init__(base)

    def disposition(self, *extra: str) -> subprocess.CompletedProcess:
        return self.register_transition(
            "--transition", "disposition", "--packet", self.packet_id,
            "--resolution", "abandoned", *extra)


@pytest.fixture
def gate_fx(tmp_path: Path) -> _ExemptionFixture:
    return _ExemptionFixture(tmp_path)


@pytest.fixture
def closure_fx(tmp_path: Path) -> _ExemptionClosureFixture:
    return _ExemptionClosureFixture(tmp_path)


@pytest.fixture
def disposition_fx(tmp_path: Path) -> _ExemptionDispositionFixture:
    return _ExemptionDispositionFixture(tmp_path)


# ---------------------------------------------------------------- PD-9 (1)


def test_pd9_exemption_flags_write_the_four_fields_in_the_entry(
        gate_fx: _ExemptionFixture) -> None:
    """PD-9 (la entrada de la exención): `register-transition --transition gate`
    con las CUATRO banderas escribe una entrada de `stage_history` con
    `exempted_by`, `reason`, `requested_by` y `delegated` (planos, con el
    valor declarado por su bandera).

    RED hoy: el CLI no conoce las banderas → la invocación muere en el
    parser; falla la aserción del contrato, no la invocación.
    """
    proc = gate_fx.gate_with_exemption("--contract-path", CONTRACT_FILE)
    out = assert_flags_known(proc, "las cuatro banderas")
    assert proc.returncode == 0, (
        "PD-9 violada: la invocación con las cuatro banderas de la exención "
        f"debe registrarse (rc=0); rc={proc.returncode}: {out!r}")

    entry = last_transition_entry(gate_fx.read_state(), "gate")
    for field, expected in (("exempted_by", EXEMPTED_BY),
                            ("reason", EXEMPTION_REASON),
                            ("requested_by", REQUESTED_BY),
                            ("delegated", True)):
        assert entry.get(field) == expected, (
            f"PD-9 violada: la entrada de la exención debe llevar el campo "
            f"{field!r} con el valor declarado ({expected!r}); entrada: "
            f"{entry!r}")


# ---------------------------------------------------------------- PD-9 (2)


def test_pd9_without_the_flags_the_entry_carries_no_exemption_field(
        gate_fx: _ExemptionFixture) -> None:
    """PD-9 (control negativo): la invocación SIN las banderas escribe una
    entrada que NO lleva los campos de la exención (la forma por omisión es la
    vigente: R-11, «ni una clave, ni un valor»).

    CONTROL DECLARADO: verde con el producto en vigor; debe seguir verde con
    el producto nuevo (es el caso de la identidad byte-idéntica, R-13).
    """
    proc = gate_fx.gate("--contract-path", CONTRACT_FILE)
    assert proc.returncode == 0, (
        "precondición (comportamiento existente): el gate sin exención debe "
        f"registrarse (rc=0); rc={proc.returncode}: {proc.stdout!r} "
        f"{proc.stderr!r}")

    entry = last_transition_entry(gate_fx.read_state(), "gate")
    for field in EXEMPTION_FIELDS:
        assert field not in entry, (
            f"PD-9 violada (control negativo): sin las banderas la entrada NO "
            f"debe llevar el campo {field!r}: {entry!r}")


# ---------------------------------------------------------------- PD-9 (3)


def test_pd9_flags_outside_the_gate_class_are_rejected_naming_the_class(
        gate_fx: _ExemptionFixture) -> None:
    """PD-9 (admisibilidad): las banderas de la exención son admisibles SÓLO
    con `--transition gate`; fuera de esa clase la invocación se RECHAZA
    nombrando la clase, y sin efectos (INV-7: el state byte a byte idéntico).

    La clase usada es `advance` (una transición de la clase `gate` sería el
    caso trivial). El control previo —la MISMA forma de invocación SIN las
    banderas— se acepta (rc=0) y deja una entrada nueva: así el rechazo que
    se comprueba es el de las BANDERAS y no el de otra precondición, y el
    state byte-idéntico prueba que la invocación con las banderas no
    escribió nada.

    RED hoy: el CLI no conoce las banderas → falla la aserción del
    conocimiento de las banderas, no la del rechazo.
    """
    control = gate_fx.register_transition(
        "--transition", "advance", "--stage", "tdd-green-u5-control",
        "--current-stage", "tdd", "--substage", "green")
    assert control.returncode == 0, (
        "precondición (comportamiento existente): la misma forma de "
        "invocación SIN las banderas de la exención debe aceptarse (rc=0); "
        f"rc={control.returncode}: {control.stdout!r} {control.stderr!r}")

    before = gate_fx.state_bytes()
    count_before = len(entries(gate_fx.read_state()))
    proc = gate_fx.register_transition(
        "--transition", "advance", "--stage", "tdd-green-u5-flagged",
        "--current-stage", "tdd", "--substage", "red", *exemption_flags())
    out = assert_flags_known(proc, "las banderas fuera de la clase `gate`")

    assert proc.returncode != 0, (
        "PD-9 violada: las banderas de la exención son inadmisibles fuera de "
        f"la clase `gate`; la invocación debe rechazarse; rc="
        f"{proc.returncode}: {out!r}")
    assert "gate" in out.lower(), (
        "PD-9 violada: el rechazo debe NOMBRAR la clase admitida (`gate`): "
        f"{out!r}")
    assert_unchanged(gate_fx, before, "PD-9",
                     "banderas de exención fuera de la clase `gate`")
    assert len(entries(gate_fx.read_state())) == count_before, (
        "PD-9 violada: el rechazo no debe anexar ninguna entrada: "
        f"{entries(gate_fx.read_state())!r}")


# ---------------------------------------------------------------- PD-9 (4)


def test_pd9_exemption_entry_does_not_enable_construction(
        gate_fx: _ExemptionFixture, tmp_path: Path) -> None:
    """PD-9 + PD-14: la entrada de exención NO habilita construcción por sí
    sola (el pin de aprobación sigue siendo el que manda, INV-7 de 006-006).

    El caso: un `gate` SIN pin de contrato (etiqueta `tdd-review`) que lleva
    las cuatro banderas de la exención ⇒ se registra (rc=0) con sus campos, y
    el LECTOR (un rol de construcción) sigue BLOQUEADO con `approval pending`.

    RED hoy: el CLI no conoce las banderas → falla la aserción del
    conocimiento de las banderas.
    """
    proc = gate_fx.gate(*exemption_flags(), stage=FREE_STAGE)
    out = assert_flags_known(proc, "la exención sin pin de contrato")
    assert proc.returncode == 0, (
        "PD-9 violada: el gate con las cuatro banderas de la exención debe "
        f"registrarse (rc=0); rc={proc.returncode}: {out!r}")

    entry = last_transition_entry(gate_fx.read_state(), "gate")
    assert entry.get("exempted_by") == EXEMPTED_BY, (
        "PD-9 violada: la entrada debe llevar la exención declarada: "
        f"{entry!r}")
    assert entry.get("stage") == FREE_STAGE, (
        "precondición (fixture): la entrada debe ser la del gate SIN pin de "
        f"contrato: {entry!r}")

    reader = gate_fx.reader_in_copy(tmp_path / "reader-copy")
    reader_out = reader.stdout + reader.stderr
    assert reader.returncode != 0, (
        "PD-9/PD-14 violada: la entrada de exención NO habilita construcción "
        f"por sí sola; el LECTOR debe seguir bloqueado; rc="
        f"{reader.returncode}: {reader_out!r}")
    assert APPROVAL_PENDING in reader_out.lower(), (
        "PD-9/PD-14 violada: el LECTOR debe rechazar con el marcador "
        f"«{APPROVAL_PENDING}»: {reader_out!r}")


# ---------------------------------------------------------------- PD-9 (5)


def test_pd9_approval_with_exemption_stays_vigente_for_the_closure(
        closure_fx: _ExemptionClosureFixture, tmp_path: Path) -> None:
    """PD-9 + V-4: la aprobación con exención sigue VIGENTE para el cierre
    (PD-8(b)) y una segunda aprobación sin `--supersedes` sigue rechazándose.

    El recorrido: (i) sin aprobación, el cierre se rechaza por el pin
    ausente (comportamiento vigente, precondición); (ii) se registra la
    aprobación CON exención (mismo pin); (iii) el LECTOR la reconoce
    (habilitado) — sobre una COPIA, para no mutar el state del recorrido;
    (iv) una segunda aprobación sin `--supersedes` se rechaza; (v) el cierre
    se aplica, lo que prueba que la aprobación con exención es la vigente.

    RED hoy: el CLI no conoce las banderas → falla la aserción del
    conocimiento de las banderas.
    """
    closure_fx.drop_approval()
    closed_without = closure_fx.closure()
    assert closed_without.returncode != 0, (
        "precondición (comportamiento vigente, PD-8(b)): sin aprobación "
        "vigente el cierre debe rechazarse; rc="
        f"{closed_without.returncode}: {closed_without.stdout!r} "
        f"{closed_without.stderr!r}")

    proc = closure_fx.gate_with_exemption("--contract-path", CONTRACT_FILE)
    out = assert_flags_known(proc, "la aprobación con exención")
    assert proc.returncode == 0, (
        "PD-9 violada: la aprobación con exención debe registrarse (rc=0); "
        f"rc={proc.returncode}: {out!r}")

    entry = last_transition_entry(closure_fx.read_state(), "gate")
    assert entry.get("exempted_by") == EXEMPTED_BY, (
        "PD-9 violada: la entrada debe llevar la exención declarada: "
        f"{entry!r}")

    reader = closure_fx.run_packet(*prepare_args(
        copy_project(closure_fx.root, tmp_path / "reader-copy"),
        role=READER_ROLE, substage=READER_SUBSTAGE,
        objective="sonda de vigencia (fixture 006-006 U5)"))
    reader_out = reader.stdout + reader.stderr
    assert reader.returncode == 0, (
        "PD-9/V-4 violada: la aprobación con exención debe seguir VIGENTE "
        f"(el LECTOR debe habilitarla); rc={reader.returncode}: "
        f"{reader_out!r}")

    second = closure_fx.register_transition(
        "--transition", "gate", "--stage", SPEC_STAGE, "--approve-by", APPROVER,
        "--contract-path", CONTRACT_FILE, "--substage", "green")
    second_out = second.stdout + second.stderr
    assert second.returncode != 0, (
        "PD-9/V-4 violada: una segunda aprobación sin `--supersedes` debe "
        f"seguir rechazándose; rc={second.returncode}: {second_out!r}")
    assert STATE_INCOHERENT in second_out.lower(), (
        "PD-9/V-4 violada: el rechazo de la segunda aprobación debe llevar el "
        f"marcador «{STATE_INCOHERENT}»: {second_out!r}")
    assert "supersedes" in second_out, (
        "PD-9/V-4 violada: el rechazo debe nombrar la vía permitida "
        f"(`--supersedes`): {second_out!r}")

    closed = closure_fx.closure()
    closed_out = closed.stdout + closed.stderr
    assert closed.returncode == 0, (
        "PD-9/V-4 violada: la aprobación con exención debe ser la VIGENTE "
        f"para el cierre (PD-8(b)); el cierre debe aplicarse (rc=0); rc="
        f"{closed.returncode}: {closed_out!r}")


# ---------------------------------------------------------------- PD-9 (6)


def test_pd9_payload_carries_the_exemption_block_with_exactly_the_declared_fields(
        gate_fx: _ExemptionFixture) -> None:
    """PD-9 + R-11/R-12: con la exención declarada, el `transition_key_payload`
    lleva UN bloque `exemption` con EXACTAMENTE los campos declarados (los no
    declarados NO están: no como `null`, no están), y la `transition_key` se
    RECOMPUTA desde el payload escrito.

    El control negativo va en el otro test: sin exención declarada el payload
    NO lleva bloque.

    RED hoy: el CLI no conoce las banderas → falla la aserción del
    conocimiento de las banderas.
    """
    proc = gate_fx.gate_with_exemption("--contract-path", CONTRACT_FILE)
    out = assert_flags_known(proc, "el bloque `exemption`")
    assert proc.returncode == 0, (
        f"PD-9 violada: la invocación con exención debe registrarse (rc=0); "
        f"rc={proc.returncode}: {out!r}")

    entry = last_transition_entry(gate_fx.read_state(), "gate")
    payload = entry.get(PAYLOAD_KEY)
    assert isinstance(payload, dict) and payload, (
        "PD-9 violada: la entrada debe llevar el payload canónico de la "
        f"identidad ({PAYLOAD_KEY!r}): {entry!r}")

    block = payload.get(EXEMPTION_BLOCK)
    assert isinstance(block, dict), (
        "PD-9/R-11 violada: con la exención declarada el payload debe llevar "
        f"UN bloque {EXEMPTION_BLOCK!r}: {payload!r}")
    assert set(block) == set(EXEMPTION_FIELDS), (
        "PD-9/R-12 violada: el bloque `exemption` debe llevar EXACTAMENTE los "
        f"campos declarados {sorted(EXEMPTION_FIELDS)}; el bloque lleva "
        f"{sorted(block)}: {block!r}")
    assert block.get("exempted_by") == EXEMPTED_BY, (
        f"PD-9/R-12 violada: el bloque debe llevar el valor declarado: "
        f"{block!r}")
    assert block.get("reason") == EXEMPTION_REASON, (
        f"PD-9/R-12 violada: el bloque debe llevar el valor declarado: "
        f"{block!r}")
    assert block.get("requested_by") == REQUESTED_BY, (
        f"PD-9/R-12 violada: el bloque debe llevar el valor declarado: "
        f"{block!r}")
    assert block.get("delegated") is True, (
        f"PD-9/R-12 violada: el interruptor `--delegated` debe valer True en "
        f"el bloque: {block!r}")

    assert set(payload) == set(FROZEN_PAYLOAD_KEYS) | {EXEMPTION_BLOCK}, (
        "PD-9/R-11 violada: el payload debe llevar las 16 claves de la "
        f"fórmula anterior MÁS el bloque `exemption`; el payload lleva "
        f"{sorted(payload)}")
    recomputed = canonical_digest(payload)
    assert recomputed == entry.get("transition_key"), (
        "PD-9 violada: la `transition_key` debe recomputarse desde el payload "
        f"escrito con la serialización canónica declarada: recomputado "
        f"{recomputed!r}, entrada {entry.get('transition_key')!r}")


def test_pd9_payload_block_carries_only_the_declared_fields(
        gate_fx: _ExemptionFixture) -> None:
    """PD-9 + R-12 (el otro lado de «exactamente»): con un SUBCONJUNTO de las
    banderas, el bloque `exemption` lleva sólo esos campos —los no declarados
    no están (no como `null`).

    RED hoy: el CLI no conoce las banderas → falla la aserción del
    conocimiento de las banderas.
    """
    proc = gate_fx.gate("--contract-path", CONTRACT_FILE,
                        *exemption_flags(exempted_by=EXEMPTED_BY,
                                         reason=EXEMPTION_REASON,
                                         requested_by=None, delegated=False))
    out = assert_flags_known(proc, "el subconjunto de banderas")
    assert proc.returncode == 0, (
        f"PD-9 violada: la invocación con un subconjunto de las banderas "
        f"debe registrarse (rc=0); rc={proc.returncode}: {out!r}")

    entry = last_transition_entry(gate_fx.read_state(), "gate")
    payload = entry.get(PAYLOAD_KEY)
    assert isinstance(payload, dict), (
        f"PD-9 violada: falta el payload de la identidad: {entry!r}")
    block = payload.get(EXEMPTION_BLOCK)
    assert isinstance(block, dict), (
        "PD-9/R-11 violada: con exención declarada el payload debe llevar el "
        f"bloque `exemption`: {payload!r}")
    assert set(block) == {"exempted_by", "reason"}, (
        "PD-9/R-12 violada: el bloque debe llevar EXACTAMENTE los campos "
        f"declarados (`exempted_by`, `reason`); lleva {sorted(block)}: "
        f"{block!r}")
    assert "requested_by" not in block and "delegated" not in block, (
        "PD-9/R-12 violada: los campos NO declarados no están en el bloque "
        f"(no como `null`): {block!r}")


# ---------------------------------------------------------------- PD-9 (7)


def test_pd9_identical_repetition_with_the_same_exemption_is_a_noop(
        gate_fx: _ExemptionFixture) -> None:
    """PD-9 + PD-11 + R-14(a): la repetición IDÉNTICA (misma exención) es un
    NO-OP: rc=0, SIN segunda entrada, state byte a byte idéntico y salida que
    nombra la entrada existente (su `transition_key`).

    RED hoy: el CLI no conoce las banderas → falla la aserción del
    conocimiento de las banderas.
    """
    first = gate_fx.gate_with_exemption("--contract-path", CONTRACT_FILE)
    out = assert_flags_known(first, "la primera invocación con exención")
    assert first.returncode == 0, (
        f"PD-9 violada: la primera invocación con exención debe registrarse "
        f"(rc=0); rc={first.returncode}: {out!r}")

    state_after_first = gate_fx.state_bytes()
    count_after_first = len(entries(gate_fx.read_state()))
    key = last_transition_entry(gate_fx.read_state(), "gate").get(
        "transition_key")
    assert isinstance(key, str) and TRANSITION_DIGEST_RE.match(key), (
        f"precondición (fixture): la entrada debe llevar su `transition_key`: "
        f"{key!r}")

    repeat = gate_fx.gate_with_exemption("--contract-path", CONTRACT_FILE)
    repeat_out = assert_flags_known(repeat, "la repetición idéntica")
    assert repeat.returncode == 0, (
        "PD-9/PD-11 violada: repetir la invocación IDÉNTICA (misma exención) "
        f"debe ser un no-op exitoso (rc=0); rc={repeat.returncode}: "
        f"{repeat_out!r}")
    assert ALREADY_REGISTERED in repeat_out.lower(), (
        "PD-9/PD-11 violada: el no-op debe LO DECIR (la salida nombra la "
        f"entrada existente): {repeat_out!r}")
    assert key in repeat_out, (
        "PD-9/PD-11 violada: la salida del no-op debe NOMBRAR la entrada "
        f"existente (su `transition_key` {key!r}): {repeat_out!r}")
    assert len(entries(gate_fx.read_state())) == count_after_first, (
        "PD-9/PD-11 violada: la repetición idéntica NO debe anexar una segunda "
        f"entrada (siguen {count_after_first})")
    assert gate_fx.state_bytes() == state_after_first, (
        "PD-9/PD-11 violada: el no-op debe dejar el state byte a byte "
        "idéntico al de la primera invocación")


# ---------------------------------------------------------------- PD-9 (8)


def test_pd9_repetition_that_changes_the_exemption_is_not_a_noop(
        gate_fx: _ExemptionFixture) -> None:
    """PD-9 + B-2 + INV-12: la repetición que CAMBIA la exención NO es un
    no-op: o se REGISTRA por `--supersedes` (la entrada previa sigue en el
    historial y la nueva la marca) o se RECHAZA explícitamente nombrando la
    entrada vigente y la vía permitida — NUNCA rc=0 sin registrar.

    El oráculo es la DISYUNCIÓN que declara el contrato, con las dos ramas
    comprobadas con la misma exigencia: en la rama del registro, una entrada
    NUEVA que marca la previa; en la rama del rechazo, un diagnóstico que
    nombra la entrada vigente y la vía `--supersedes`. Lo que NO se admite es
    el tercer caso: rc=0 sin registrar nada.

    RED hoy: el CLI no conoce las banderas → falla la aserción del
    conocimiento de las banderas.
    """
    first = gate_fx.gate_with_exemption("--contract-path", CONTRACT_FILE)
    out = assert_flags_known(first, "la primera invocación con exención")
    assert first.returncode == 0, (
        f"PD-9 violada: la primera invocación con exención debe registrarse "
        f"(rc=0); rc={first.returncode}: {out!r}")
    key_first = last_transition_entry(gate_fx.read_state(), "gate").get(
        "transition_key")

    state_before = gate_fx.state_bytes()
    count_before = len(entries(gate_fx.read_state()))
    changed = gate_fx.gate(
        "--contract-path", CONTRACT_FILE,
        *exemption_flags(reason="otro motivo de exencion (fixture U5)"),
        "--supersedes", str(key_first))
    changed_out = assert_flags_known(changed, "la repetición que cambia la exención")

    if changed.returncode == 0:
        entries_after = entries(gate_fx.read_state())
        assert len(entries_after) == count_before + 1, (
            "PD-9/INV-12 violada: la repetición que cambia la exención no puede "
            "devolver éxito SIN registrar: la entrada previa sigue en el "
            f"historial y no hay entrada nueva (siguen {count_before}): "
            f"{changed_out!r}")
        new_entry = last_transition_entry(gate_fx.read_state(), "gate")
        assert new_entry.get("supersedes") == key_first, (
            "PD-9 violada: la entrada nueva debe MARCAR la entrada previa que "
            f"reemplaza (`supersedes` = {key_first!r}): {new_entry!r}")
        assert new_entry.get("transition_key") != key_first, (
            "PD-9 violada: la entrada nueva debe tener clave PROPIA (la "
            f"exención cambió): {new_entry!r}")
    else:
        assert STATE_INCOHERENT in changed_out.lower(), (
            "PD-9 violada: el rechazo explícito debe llevar el marcador "
            f"«{STATE_INCOHERENT}»: {changed_out!r}")
        assert "supersedes" in changed_out, (
            "PD-9 violada: el rechazo explícito debe nombrar la vía "
            f"permitida (`--supersedes`): {changed_out!r}")
        assert (str(key_first) in changed_out) or (CONTRACT_FILE in changed_out), (
            "PD-9 violada: el rechazo explícito debe NOMBRAR la entrada "
            f"vigente (su `transition_key` {key_first!r} o el `contract_path` "
            f"{CONTRACT_FILE!r}): {changed_out!r}")
        assert_unchanged(gate_fx, state_before, "PD-9",
                         "la repetición que cambia la exención, rechazada")


# ---------------------------------------------------------------- PD-9 (9-11)


def _two_revisions(fx, tmp_path: Path, label: str, transition: str,
                   register) -> tuple[dict, str]:
    """El RECORRIDO DE DOS REVISIONES (B-3, R-13, V-7).

    (i) el producto ANTERIOR (la revisión congelada de este RED) registra la
    orden en una COPIA del proyecto; (ii) el producto vigente registra la
    MISMA orden en otra COPIA byte a byte idéntica; (iii) el payload escrito
    por el vigente es BYTE-IDÉNTICO al del anterior y la `transition_key` es
    la misma; (iv) la repetición de la misma orden SIN exención sobre la
    entrada del producto anterior es un NO-OP (rc=0, sin segunda entrada,
    state byte a byte idéntico, salida que nombra la entrada histórica).

    Devuelve el payload y la clave que escribió el producto vigente.
    """
    prev_cli = previous_product_cli(tmp_path / "previous-product")
    root_old = copy_project(fx.root, tmp_path / "project-old")
    root_new = copy_project(fx.root, tmp_path / "project-new")

    old = register(prev_cli, root_old)
    old_out = old.stdout + old.stderr
    assert old.returncode == 0, (
        f"precondición (producto anterior, {label}): el producto anterior "
        f"debe registrar la transición (rc=0); rc={old.returncode}: "
        f"{old_out!r}")
    new = register(CURRENT_CLI, root_new)
    new_out = new.stdout + new.stderr
    assert new.returncode == 0, (
        f"precondición (producto vigente, {label}): el producto vigente debe "
        f"registrar la transición (rc=0); rc={new.returncode}: {new_out!r}")

    entry_old = last_transition_entry(read_state(root_old), transition)
    entry_new = last_transition_entry(read_state(root_new), transition)
    payload_old = entry_old.get(PAYLOAD_KEY)
    payload_new = entry_new.get(PAYLOAD_KEY)
    key_old = entry_old.get("transition_key")
    key_new = entry_new.get("transition_key")

    assert isinstance(key_old, str) and TRANSITION_DIGEST_RE.match(key_old), (
        f"precondición (producto anterior, {label}): la entrada debe llevar "
        f"su `transition_key`: {key_old!r}")
    assert payload_new == payload_old, (
        f"PD-9/R-13 violada ({label}): el payload de identidad escrito por el "
        f"producto vigente debe ser BYTE-IDÉNTICO al del producto anterior "
        f"(R-13, D-14 — sin enmienda de 005-014 PD-23 ni de 006-005 "
        f"PD-19(b)); vigente {payload_new!r} vs anterior {payload_old!r}")
    assert key_new == key_old, (
        f"PD-9/R-13 violada ({label}): la `transition_key` debe ser la misma "
        f"que la del producto anterior; vigente {key_new!r} vs anterior "
        f"{key_old!r}")
    assert set(payload_new or {}) == set(FROZEN_PAYLOAD_KEYS), (
        f"PD-9/R-11/R-13 violada ({label}): sin exención declarada el payload "
        f"debe llevar EXACTAMENTE las 16 claves de la fórmula anterior "
        f"(congelada); lleva {sorted(payload_new or {})}")

    # (iv) la repetición de la misma orden sobre la entrada del ANTERIOR.
    state_before = state_bytes(root_old)
    count_before = len(entries(read_state(root_old)))
    repeat = register(CURRENT_CLI, root_old)
    repeat_out = repeat.stdout + repeat.stderr
    assert repeat.returncode == 0, (
        f"PD-9/R-13 violada ({label}): repetir la misma orden SIN exención "
        f"sobre una entrada registrada por el producto ANTERIOR debe ser un "
        f"no-op (rc=0) — la identidad histórica se conserva; rc="
        f"{repeat.returncode}: {repeat_out!r}")
    assert ALREADY_REGISTERED in repeat_out.lower(), (
        f"PD-9/R-13 violada ({label}): el no-op debe LO DECIR: {repeat_out!r}")
    assert key_old in repeat_out, (
        f"PD-9/R-13 violada ({label}): la salida del no-op debe NOMBRAR la "
        f"entrada histórica (su `transition_key` {key_old!r}): {repeat_out!r}")
    assert len(entries(read_state(root_old))) == count_before, (
        f"PD-9/R-13 violada ({label}): la repetición NO debe anexar una "
        f"segunda entrada (siguen {count_before})")
    assert state_bytes(root_old) == state_before, (
        f"PD-9/R-13 violada ({label}): la repetición debe dejar el state byte "
        f"a byte idéntico")
    return payload_new, key_new


def test_pd9_two_revisions_gate_keeps_the_identity_and_the_replay_is_a_noop(
        gate_fx: _ExemptionFixture, tmp_path: Path) -> None:
    """PD-9 + R-13 + D-14 + V-7 (CONTROL, no regresión): el recorrido de dos
    revisiones en la clase `gate`.

    El payload escrito por el producto vigente es byte-idéntico al del
    producto anterior (la fórmula de identidad anterior, congelada en este
    archivo: las 16 claves), la `transition_key` es la misma y la repetición
    de la misma orden SIN exención sobre la entrada del producto anterior es
    un no-op que nombra la entrada histórica.

    CONTROL DECLARADO: verde con el producto en vigor; debe seguir verde con
    el producto nuevo (es lo que la forma condicional de R-11 protege).
    """
    state = gate_fx.read_state()
    expected = frozen_identity_payload(
        transition="gate", stage=SPEC_STAGE,
        execution_id=state["execution"]["id"],
        feature_id=state["active_feature"], approved_by=APPROVER,
        contract={"path": CONTRACT_FILE,
                  "sha256": hashlib.sha256(
                      (gate_fx.root / CONTRACT_FILE).read_bytes()).hexdigest()})

    def register(cli: Path, root: Path) -> subprocess.CompletedProcess:
        return run_with(
            gate_fx, cli, "register-transition", "--project-root", str(root),
            "--transition", "gate", "--stage", SPEC_STAGE,
            "--approve-by", APPROVER, "--contract-path", CONTRACT_FILE)

    payload, key = _two_revisions(gate_fx, tmp_path, "gate", "gate", register)
    assert payload == expected, (
        "PD-9/R-13 violada (gate): el payload escrito debe ser el de la "
        "FÓRMULA DE IDENTIDAD ANTERIOR congelada en este RED; esperado "
        f"{expected!r}, escrito {payload!r}")
    assert canonical_digest(payload) == key, (
        "PD-9 violada (gate): la `transition_key` debe recomputarse desde el "
        f"payload escrito: {key!r}")


def test_pd9_two_revisions_closure_keeps_the_identity_and_the_replay_is_a_noop(
        closure_fx: _ExemptionClosureFixture, tmp_path: Path) -> None:
    """PD-9 + R-13 + PD-23 + V-7 (CONTROL, no regresión): el recorrido de dos
    revisiones en la clase `closure`.

    La clase `closure` no tiene aprobación vigente que compita ⇒ el replay
    histórico SIGUE siendo un no-op (R-14(a), PD-23): es el oráculo de
    005-014 que esta feature NO enmienda (D-14).
    """
    state = closure_fx.read_state()
    expected = frozen_identity_payload(
        transition="closure", stage=CLOSURE_STAGE,
        execution_id=state["execution"]["id"],
        feature_id=state["active_feature"], approved_by=APPROVER,
        closure={"path": CLOSURE_REL,
                 "sha256": hashlib.sha256(
                     (closure_fx.root / CLOSURE_REL).read_bytes()).hexdigest()})

    def register(cli: Path, root: Path) -> subprocess.CompletedProcess:
        return run_with(
            closure_fx, cli, "register-transition", "--project-root", str(root),
            "--transition", "closure", "--stage", CLOSURE_STAGE,
            "--approve-by", APPROVER, "--closure-path", CLOSURE_REL)

    payload, key = _two_revisions(closure_fx, tmp_path, "closure", "closure",
                                  register)
    assert payload == expected, (
        "PD-9/R-13 violada (closure): el payload escrito debe ser el de la "
        "FÓRMULA DE IDENTIDAD ANTERIOR congelada en este RED; esperado "
        f"{expected!r}, escrito {payload!r}")
    assert canonical_digest(payload) == key, (
        "PD-9 violada (closure): la `transition_key` debe recomputarse desde "
        f"el payload escrito: {key!r}")


def test_pd9_two_revisions_disposition_keeps_the_identity_and_the_replay_is_a_noop(
        disposition_fx: _ExemptionDispositionFixture, tmp_path: Path) -> None:
    """PD-9 + R-13 + PD-19(b) + V-7 (CONTROL, no regresión): el recorrido de
    dos revisiones en la clase `disposition`.

    Como `closure`, la clase `disposition` no tiene aprobación vigente que
    compita ⇒ el replay histórico sigue siendo un no-op (R-14(a),
    PD-19(b)): el oráculo de 006-005 que esta feature NO enmienda (D-14).
    """
    state = disposition_fx.read_state()
    expected = frozen_identity_payload(
        transition="disposition", stage="dispatch-disposition",
        execution_id=state["execution"]["id"],
        feature_id=state["active_feature"],
        packet_id=disposition_fx.packet_id, resolution="abandoned")

    def register(cli: Path, root: Path) -> subprocess.CompletedProcess:
        return run_with(
            disposition_fx, cli, "register-transition", "--project-root",
            str(root), "--transition", "disposition", "--packet",
            disposition_fx.packet_id, "--resolution", "abandoned")

    payload, key = _two_revisions(disposition_fx, tmp_path, "disposition",
                                  "disposition", register)
    assert payload == expected, (
        "PD-9/R-13 violada (disposition): el payload escrito debe ser el de la "
        "FÓRMULA DE IDENTIDAD ANTERIOR congelada en este RED; esperado "
        f"{expected!r}, escrito {payload!r}")
    assert canonical_digest(payload) == key, (
        "PD-9 violada (disposition): la `transition_key` debe recomputarse "
        f"desde el payload escrito: {key!r}")


# ---------------------------------------------------------------- PD-9 (12)


def _register_a_and_b(fx: _ExemptionFixture) -> tuple[str, str]:
    """El recorrido A→B→A, pasos (i) y (ii).

    (i) **A**: la aprobación SIN exención (`--stage specification` con su
    pin) ⇒ rc=0 y una entrada con su `transition_key`.
    (ii) **B**: la MISMA orden con las cuatro banderas de la exención y
    `--supersedes <clave_de_A>` ⇒ rc=0 y una SEGUNDA entrada, cuya clave es
    DISTINTA (el bloque `exemption` entra en el payload).
    """
    a = fx.gate("--contract-path", CONTRACT_FILE)
    a_out = assert_flags_known(a, "el paso (i) del recorrido A→B→A")
    assert a.returncode == 0, (
        f"PD-9 violada (A→B→A, paso i): la aprobación A debe registrarse "
        f"(rc=0); rc={a.returncode}: {a_out!r}")
    entry_a = last_transition_entry(fx.read_state(), "gate")
    key_a = entry_a.get("transition_key")
    assert isinstance(key_a, str) and TRANSITION_DIGEST_RE.match(key_a), (
        f"precondición (fixture): la entrada A debe llevar su "
        f"`transition_key`: {key_a!r}")

    b = fx.gate("--contract-path", CONTRACT_FILE, *exemption_flags(),
                "--supersedes", key_a)
    b_out = assert_flags_known(b, "el paso (ii) del recorrido A→B→A")
    assert b.returncode == 0, (
        f"PD-9 violada (A→B→A, paso ii): la aprobación B (con exención y "
        f"`--supersedes`) debe registrarse (rc=0); rc={b.returncode}: "
        f"{b_out!r}")
    entry_b = last_transition_entry(fx.read_state(), "gate")
    key_b = entry_b.get("transition_key")
    assert isinstance(key_b, str) and TRANSITION_DIGEST_RE.match(key_b), (
        f"precondición (fixture): la entrada B debe llevar su "
        f"`transition_key`: {key_b!r}")
    assert key_b != key_a, (
        "PD-9/D-13 violada (A→B→A, paso ii): la clave de B debe ser DISTINTA "
        f"de la de A (la exención entra en el payload); A={key_a!r} "
        f"B={key_b!r}")
    assert entry_b.get("supersedes") == key_a, (
        "PD-9 violada (A→B→A, paso ii): la entrada B debe MARCAR la entrada A "
        f"que reemplaza (`supersedes` = {key_a!r}): {entry_b!r}")
    return key_a, key_b


def test_pd9_aba_walk_rejects_the_return_to_the_previous_payload(
        gate_fx: _ExemptionFixture, tmp_path: Path) -> None:
    """PD-9 + R-14(b) + D-15 + V-8: el recorrido A→B→A.

    (i) **A** (sin exención) ⇒ rc=0; (ii) **B** (con exención y
    `--supersedes A`) ⇒ rc=0, segunda entrada, clave distinta; (iii) **A de
    nuevo SIN `--supersedes`** ⇒ rc≠0 con el RECHAZO VIGENTE de una sola
    aprobación (nombra la entrada vigente y la vía `--supersedes`); (iv) **A
    de nuevo CON `--supersedes <clave_de_B>`** ⇒ rc≠0 con el RECHAZO DE
    COLISIÓN (nombra la clave que colisiona y que NO es la vigente, la clave
    de la vigente y las DOS salidas); en ambos rechazos el state queda byte
    a byte idéntico y la aprobación vigente SIGUE EN VIGOR, comprobado con el
    LECTOR; (v) el REPLAY de la vigente (repetir B) ⇒ rc=0, no-op, sin
    segunda entrada, state byte a byte idéntico y salida que nombra la
    entrada existente.

    RED hoy: el CLI no conoce las banderas ⇒ el paso (ii) falla. El defecto
    que este recorrido persigue —la rama de no-op que responde ANTES de
    examinar `--supersedes` y la aprobación vigente, y devuelve éxito
    dejando B vigente— sólo es alcanzable cuando la exención existe; hoy el
    recorrido muere antes, en el parser, y por eso el RED es una aserción
    sobre el comportamiento ausente, no un error de invocación.
    """
    key_a, key_b = _register_a_and_b(gate_fx)

    # (iii) A de nuevo, SIN `--supersedes` ⇒ el rechazo vigente.
    state_before = gate_fx.state_bytes()
    back = gate_fx.gate("--contract-path", CONTRACT_FILE)
    back_out = assert_flags_known(back, "el paso (iii) del recorrido A→B→A")
    assert back.returncode != 0, (
        "PD-9/R-14(b) violada (A→B→A, paso iii): volver al payload de A NO "
        "puede ser un no-op que deje B vigente: la invocación debe RECHAZARSE "
        f"(rc≠0); rc={back.returncode}: {back_out!r}")
    assert STATE_INCOHERENT in back_out.lower(), (
        "PD-9/R-14(b) violada (A→B→A, paso iii): el rechazo debe llevar el "
        f"marcador «{STATE_INCOHERENT}»: {back_out!r}")
    assert "supersedes" in back_out, (
        "PD-9/R-14(b) violada (A→B→A, paso iii): el rechazo debe nombrar la "
        f"vía permitida (`--supersedes`): {back_out!r}")
    assert (key_b in back_out) or (CONTRACT_FILE in back_out), (
        "PD-9/R-14(b) violada (A→B→A, paso iii): el rechazo debe NOMBRAR la "
        f"entrada vigente (su `transition_key` {key_b!r} o el "
        f"`contract_path` {CONTRACT_FILE!r}): {back_out!r}")
    assert_unchanged(gate_fx, state_before, "PD-9",
                     "A→B→A, paso (iii)")

    # (iv) A de nuevo, CON `--supersedes <clave_de_B>` ⇒ el rechazo de
    # colisión: la clave que colisiona (la de A) NO es la vigente (la de B).
    state_before = gate_fx.state_bytes()
    collision = gate_fx.gate("--contract-path", CONTRACT_FILE,
                             "--supersedes", key_b)
    collision_out = assert_flags_known(collision,
                                       "el paso (iv) del recorrido A→B→A")
    assert collision.returncode != 0, (
        "PD-9/R-14(b)/D-15 violada (A→B→A, paso iv): la invocación que vuelve "
        "al payload de A con `--supersedes` NO puede ser un no-op que deje B "
        f"vigente: debe RECHAZARSE (rc≠0); rc={collision.returncode}: "
        f"{collision_out!r}")
    assert STATE_INCOHERENT in collision_out.lower(), (
        "PD-9/R-14(b)/D-15 violada (A→B→A, paso iv): el rechazo de colisión "
        f"debe llevar el marcador «{STATE_INCOHERENT}»: {collision_out!r}")
    assert key_a in collision_out, (
        "PD-9/R-14(b) violada (A→B→A, paso iv): el rechazo debe NOMBRAR la "
        f"clave que colisiona ({key_a!r}): {collision_out!r}")
    assert key_b in collision_out, (
        "PD-9/R-14(b) violada (A→B→A, paso iv): el rechazo debe NOMBRAR la "
        f"clave de la vigente ({key_b!r}): {collision_out!r}")
    lowered = collision_out.lower()
    assert any(token in lowered for token in VIGENCY_TOKENS), (
        "PD-9/R-14(b) violada (A→B→A, paso iv): el rechazo debe DISTINGUIR la "
        "clave que colisiona de la clave de la vigente (la primera NO es la "
        f"vigente): {collision_out!r}")
    assert any(token in lowered for token in DISTINGUISHABLE_EXIT_TOKENS), (
        "PD-9/D-15 violada (A→B→A, paso iv): el rechazo debe nombrar la "
        "PRIMERA salida (registrar el cambio con un valor distinguible): "
        f"{collision_out!r}")
    assert any(token in lowered for token in RECONCILE_EXIT_TOKENS), (
        "PD-9/D-15 violada (A→B→A, paso iv): el rechazo debe nombrar la "
        f"SEGUNDA salida (reconciliar): {collision_out!r}")
    assert_unchanged(gate_fx, state_before, "PD-9",
                     "A→B→A, paso (iv)")

    # La vigente SIGUE EN VIGOR: lo dice el LECTOR (sobre una COPIA, para no
    # mutar el state que el recorrido compara byte a byte).
    reader = gate_fx.reader_in_copy(tmp_path / "reader-copy")
    reader_out = reader.stdout + reader.stderr
    assert reader.returncode == 0, (
        "PD-9/R-14(b) violada (A→B→A): tras los rechazos la aprobación "
        "VIGENTE debe seguir habilitando al rol de construcción (el LECTOR "
        f"debe habilitarla); rc={reader.returncode}: {reader_out!r}")
    assert APPROVAL_PENDING not in reader_out.lower(), (
        "PD-9/R-14(b) violada (A→B→A): la aprobación vigente debe seguir en "
        f"vigor: {reader_out!r}")

    # (v) el replay de la vigente (repetir B) ⇒ no-op.
    state_before = gate_fx.state_bytes()
    count_before = len(entries(gate_fx.read_state()))
    replay = gate_fx.gate("--contract-path", CONTRACT_FILE, *exemption_flags(),
                          "--supersedes", key_a)
    replay_out = assert_flags_known(replay, "el paso (v) del recorrido A→B→A")
    assert replay.returncode == 0, (
        "PD-9/R-14(a) violada (A→B→A, paso v): repetir la orden de la entrada "
        f"VIGENTE debe ser un no-op (rc=0); rc={replay.returncode}: "
        f"{replay_out!r}")
    assert ALREADY_REGISTERED in replay_out.lower(), (
        f"PD-9/R-14(a) violada (A→B→A, paso v): el no-op debe LO DECIR: "
        f"{replay_out!r}")
    assert key_b in replay_out, (
        "PD-9/R-14(a) violada (A→B→A, paso v): la salida del no-op debe "
        f"NOMBRAR la entrada existente (su `transition_key` {key_b!r}): "
        f"{replay_out!r}")
    assert len(entries(gate_fx.read_state())) == count_before, (
        "PD-9/R-14(a) violada (A→B→A, paso v): el replay NO debe anexar una "
        f"segunda entrada (siguen {count_before})")
    assert gate_fx.state_bytes() == state_before, (
        "PD-9/R-14(a) violada (A→B→A, paso v): el replay debe dejar el state "
        "byte a byte idéntico")


# ---------------------------------------------------------------- PD-9 (13)


def test_pd9_aba_walk_registers_the_return_with_a_distinguishable_value(
        gate_fx: _ExemptionFixture, tmp_path: Path) -> None:
    """PD-9 + R-14(b) + D-15: la SALIDA que el rechazo de colisión declara
    EXISTE.

    Repetir la orden de A citando la evidencia de la decisión del owner
    (`--artifact <archivo>`; su digest entra en la identidad) produce una
    clave PROPIA —distinta de la de A y de la de B—, de modo que la
    invocación se REGISTRA (rc=0) con `--supersedes <clave_de_B>`: una
    entrada NUEVA, VIGENTE (su clave no está en el conjunto de claves
    sustituidas) y SIN bloque `exemption` ⇒ la exención queda RETIRADA de
    verdad y la vigente anterior deja de habilitar.

    Si esta salida no se puede materializar, el RED falla (es la parte del
    contrato que el rechazo declara).

    RED hoy: el CLI no conoce las banderas ⇒ el paso (ii) falla.
    """
    key_a, key_b = _register_a_and_b(gate_fx)

    decision = gate_fx.root / ".cdad" / "local" / "owner-decision-u5.md"
    decision.parent.mkdir(parents=True, exist_ok=True)
    decision.write_bytes(b"# Decision del owner (fixture 006-006 U5)\n")
    digest = hashlib.sha256(decision.read_bytes()).hexdigest()

    third = gate_fx.gate("--contract-path", CONTRACT_FILE,
                         "--artifact", f"{decision}={digest}",
                         "--supersedes", key_b)
    third_out = assert_flags_known(third, "el registro con valor distinguible")
    assert third.returncode == 0, (
        "PD-9/D-15 violada: el registro con VALOR DISTINGUIBLE (la salida que "
        "el rechazo de colisión declara) debe aceptarse (rc=0); rc="
        f"{third.returncode}: {third_out!r}")

    entry = last_transition_entry(gate_fx.read_state(), "gate")
    key_third = entry.get("transition_key")
    assert isinstance(key_third, str) and TRANSITION_DIGEST_RE.match(
        key_third), (
        f"precondición (fixture): la entrada nueva debe llevar su "
        f"`transition_key`: {key_third!r}")
    assert key_third not in (key_a, key_b), (
        "PD-9/D-15 violada: el registro con valor distinguible debe tener una "
        f"clave PROPIA (distinta de la de A {key_a!r} y de la de B "
        f"{key_b!r}): {key_third!r}")
    payload = entry.get(PAYLOAD_KEY)
    assert isinstance(payload, dict), (
        f"PD-9 violada: falta el payload de la identidad: {entry!r}")
    assert EXEMPTION_BLOCK not in payload, (
        "PD-9/D-15 violada: la entrada que retira la exención NO debe llevar "
        f"bloque `exemption`: {payload!r}")
    assert entry.get("supersedes") == key_b, (
        "PD-9 violada: la entrada nueva debe MARCAR la entrada vigente que "
        f"reemplaza (`supersedes` = {key_b!r}): {entry!r}")

    # Vigente: el LECTOR la habilita (sobre una COPIA, para no mutar el state).
    reader = gate_fx.reader_in_copy(tmp_path / "reader-copy")
    reader_out = reader.stdout + reader.stderr
    assert reader.returncode == 0, (
        "PD-9/D-15 violada: la entrada nueva (sin exención) debe quedar "
        "VIGENTE y habilitar al rol de construcción (el LECTOR); rc="
        f"{reader.returncode}: {reader_out!r}")
