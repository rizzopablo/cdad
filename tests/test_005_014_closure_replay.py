#!/usr/bin/env python3
"""005-014 T1 RED — la clase `closure` SIN feature activa: el replay idéntico
es un no-op (PD-23), el cierre distinto rechaza cerrado (PD-25), el `--feature`
que difiere de la activa nunca desvía en silencio (PD-24) y el `--feature`
faltante sin feature activa rechaza sin sugerir `open-unit` (PD-22).

Contract:
- docs/specs/005-014-closure-replay/spec.md §2 (postcondiciones PD-22, PD-23,
  PD-24, PD-25), §3 (invariantes INV-10, INV-11, INV-12), §4 (AC-1, AC-2),
  §5 (tarea T1: los cuatro casos de esta focal).
- docs/specs/005-014-closure-replay/discovery.md §0-§5 (el defecto medido: el
  guard de feature nula `:5062-5065` con el mensaje literal
  «state incoherent: there is no active feature … open the unit first
  (`open-unit`)» corre ANTES del no-op `:5310`; `--feature` se ignora en
  silencio cuando hay feature activa; `CLOSED_FEATURE_STATUSES` nunca se
  consulta en la rama `closure`).

Superficie observable bajo prueba (caja negra: SOLO subprocess sobre el CLI
real del repo; el módulo de implementación NUNCA se importa y su código NUNCA
se lee — mismo patrón que los focales de 005-012):

    python3 skills/cdad-cycle/scripts/cdad_packet.py register-transition \\
        --project-root <ABS> --transition closure --stage <token> \\
        --approve-by <texto> --closure-path <p> [--feature <feature-id>]

Fixture: proyecto descartable en un tempdir (política válida, contrato
pineado en `stage_history`, delegación HITL vigente, ejecución v2 y paquete
real con recibo durable y aprobación `specification` vigente → las dos
comprobaciones de PD-8 verdes), construido por el camino legítimo del CLI.
El `HOME` del subproceso queda en un tempdir VACÍO (nunca el HOME real,
nunca este repo). Se reutilizan el patrón y los helpers de
`tests/test_005_012_t3_closure_dispatch_resolution.py` (fixture de cierre,
`entries`/`last_entry_with`/`assert_unchanged`). Los ids del fixture son
sintéticos y anónimos; ninguna mutación toca el state de este repo. No hay
mocks sobre el plumbing ni tests de cobertura no derivados de un PD.

RAZÓN DEL ROJO (medida por el discovery §0, declarada por caso):
- test_pd23_*: la primera invocación cierra (rc=0, comportamiento existente
  PD-9); la repetición idéntica muere HOY en el guard de feature nula
  (`:5062-5065`, que corre antes del no-op) → rc=2 con el mensaje que sugiere
  abrir la unidad → falla la aserción del rc=0 (el no-op nunca se alcanza).
- test_pd25_*: la repetición con OTRO payload muere HOY en el mismo guard →
  rc=2 pero el mensaje NO nombra la feature ni su estado (`done`) y SÍ
  contiene `open-unit`/`open the unit` → fallan las aserciones del mensaje.
- test_pd24_*: HOY `--feature` se ignora en silencio cuando hay feature
  activa (solo `late-delivery` lo lee, `:5061`): el cierre cierra la feature
  EQUIVOCADA (rc=0) → falla la aserción del rc=2 (nunca rechaza).
- test_pd22_*: HOY el guard de feature nula rechaza (rc=2) con el texto que
  sugiere `open-unit`/`open the unit` y SIN nombrar la salida legítima
  (`--feature <feature-id>`) → fallan las aserciones del mensaje.

En los cuatro casos el fallo RED es AssertionError de contrato (rc, marcador
o mensaje), jamás ImportError, SyntaxError, JSONDecodeError ni error de
setup; los marcadores de dominio discriminan frente al error de uso de
argparse.

Mapeo test → postcondición:

  test_pd23_identical_closure_replay_is_noop_naming_the_registered_entry
      -> PD-23 + INV-10 + INV-12: cerrar por la operación y repetir la MISMA
         orden → rc=0, salida «transition already registered» que nombra la
         entrada existente (su `transition_key`), state byte a byte idéntico
         (sha256 antes = después), UNA sola entrada `transition: "closure"` y
         la entrada original intacta (`transition_key`/`closed_at`/
         `closure_evidence` sin reescritura).
  test_pd25_distinct_closure_after_closure_rejects_closed_naming_feature_and_done
      -> PD-25 + INV-11: tras un cierre, una orden de cierre DISTINTA (otro
         `--stage` u otro `--closure-path` con otros bytes) → rc=2, marcador
         `state incoherent`, el mensaje NOMBRANDO la feature y su estado
         (`done`), SIN `open-unit` ni `open the unit`, y state byte a byte
         idéntico (INV-7/INV-11: nada escrito).
  test_pd24_closure_with_feature_differing_from_active_feature_fails_closed
      -> PD-24 + INV-11: con la feature activa, `--feature <otra>` → rc=2,
         marcador `state incoherent` nombrando las dos features; el state
         queda byte a byte idéntico (ni la activa ni la otra quedan cerradas
         — nunca desvío silencioso).
  test_pd22_closure_without_feature_and_without_active_feature_rejects_without_open_unit
      -> PD-22 + INV-11: `--transition closure` SIN `--feature` y con
         `state.active_feature` nulo (y sin cierre previo registrado en la
         historia) → rc=2, marcador `state incoherent`, SIN `open-unit` ni
         `open the unit`, y el mensaje ofreciendo la salida legítima
         (`--feature <feature-id>`); state byte a byte idéntico.

Interpretaciones y límites declarados (el contrato fue verificable y no hubo
detención):

1. **La orden repetida de PD-23 es la MISMA invocación** (los comandos de
   verificación de PD-23/AC-1/AC-3 en la spec no llevan `--feature`): cerrar
   una feature por la operación y repetir el comando EXACTO. El estado del
   fixture tras el cierre (`active_feature: null`, `execution` intacto) es
   el que el discovery documenta para la reanudación.
2. **Etiqueta de la clase y paths.** `--stage` es la etiqueta real del cierre
   del ciclo (`feature-closure`, discovery §4 de 005-012) y los paths de
   cierre son RELATIVOS a la raíz del proyecto, la misma convención de los
   focales de 005-012.
3. **`--closure-path` distinta con bytes distintos.** PD-23 declara que la
   identidad lleva el digest RESUELTO del cierre, así que para que la
   repetición sea un cierre DISTINTO (PD-25, no PD-23) la variante de otro
   path usa bytes distintos; con los mismos bytes la clave sería idéntica y
   el caso sería replay (PD-23).
4. **Mitad «árbol» de INV-7:** como declaran los RED de 005-012, se asevera
   el state byte a byte idéntico; el snapshot completo del árbol no se
   asevera (el lock/cleanup dentro de la operación crea y borra su archivo).
"""

from __future__ import annotations

import pytest

from test_005_012_t1_register_transition_base import (
    APPROVER,
    FEATURE_ID,
    STATE_INCOHERENT,
    TRANSITION_DIGEST_RE,
    assert_unchanged,
    entries,
    last_entry_with,
)
from test_005_012_t3_closure_dispatch_resolution import (
    CLOSURE_BYTES,
    CLOSURE_REL,
    CLOSURE_STAGE,
    FEATURE_CLOSED,
    _ClosureFixture,
    _feature_entry,
)

# Segunda etiqueta de `--stage` (token plano libre): cierra DISTINTO (PD-25).
CLOSURE_STAGE_ALT = "feature-closure-replay-alt"
# Segundo cierre citado, con bytes DISTINTOS (interpretación 3): otra clave.
CLOSURE_REL_ALT = f"docs/specs/{FEATURE_ID}/closure-alt.md"
CLOSURE_BYTES_ALT = (
    b"# Closure fixture (demo-100 closure replay, divergent bytes)\n")

# Otra feature (sintética y anónima) para el caso PD-24: distinta de la activa.
OTHER_FEATURE_ID = "demo-100-replay-other-fixture"

ALREADY_REGISTERED = "already registered"


# ---------------------------------------------------------------- helpers


class _ReplayFixture(_ClosureFixture):
    """Fixture LISTO PARA CERRAR (PD-8 verde: recibo durable + aprobación
    vigente) con el cierre citado escrito, más un SEGUNDO cierre citado con
    bytes distintos (la variante de `--closure-path` de PD-25)."""

    def __init__(self, base, mode: str = "ready") -> None:
        super().__init__(base, mode=mode)
        self.closure_alt_file = self.root / CLOSURE_REL_ALT
        self.closure_alt_file.parent.mkdir(parents=True, exist_ok=True)
        self.closure_alt_file.write_bytes(CLOSURE_BYTES_ALT)

    # -- invocación (caja negra) ------------------------------------------

    def invoke_closure(self, *, stage: str = CLOSURE_STAGE,
                       closure_rel: str = CLOSURE_REL,
                       feature: str | None = None):
        """La clase `closure` con los argumentos declarados por caso."""
        args = [
            "--transition", "closure", "--stage", stage,
            "--approve-by", APPROVER, "--closure-path", closure_rel,
        ]
        if feature is not None:
            args += ["--feature", feature]
        return self.register_transition(*args)

    # -- mutaciones declaradas del fixture --------------------------------

    def clear_active_feature(self) -> None:
        """Deja `state.active_feature` en null (la forma del defecto: el
        escenario PD-22 declarado por la spec)."""
        state = self.read_state()
        state["active_feature"] = None
        self.write_state(state)

    def add_feature(self, feature_id: str) -> None:
        """Agrega OTRA feature a `epic_features` (PD-24: el `--feature` que
        difiere de la activa debe nombrar las dos)."""
        state = self.read_state()
        state["epic_features"] = list(state.get("epic_features") or []) + [
            {"id": feature_id, "status": "in-progress"},
        ]
        self.write_state(state)


def closure_entries(state: dict) -> list[dict]:
    """Las entradas `transition: "closure"` de `stage_history`."""
    return [e for e in entries(state) if e.get("transition") == "closure"]


def assert_closed_once(fx: _ReplayFixture, label: str) -> dict:
    """Precondición compartida: el cierre se APLICÓ exactamente una vez y la
    entrada lleva su clave de identidad (PD-9/PD-10, comportamiento
    existente). Devuelve la entrada de cierre."""
    state = fx.read_state()
    closed = closure_entries(state)
    assert len(closed) == 1, (
        f"precondición (fixture, {label}): la feature debe quedar con UNA "
        f"entrada `transition: \"closure\"`; hay {len(closed)}")
    entry = closed[0]
    key = entry.get("transition_key")
    assert isinstance(key, str) and TRANSITION_DIGEST_RE.match(key), (
        f"precondición (fixture, {label}): la entrada de cierre lleva su "
        f"`transition_key`: {key!r}")
    feature = _feature_entry(state, FEATURE_ID)
    assert (feature or {}).get("status") == FEATURE_CLOSED, (
        f"precondición (fixture, {label}): la feature quedó "
        f"{FEATURE_CLOSED!r}")
    assert state.get("active_feature") is None, (
        f"precondición (fixture, {label}): tras el cierre `active_feature` "
        "es null (el escenario del discovery)")
    return entry


# ---------------------------------------------------------------- PD-23


def test_pd23_identical_closure_replay_is_noop_naming_the_registered_entry(
        tmp_path) -> None:
    """PD-23 (+ INV-10, + INV-12): cerrar una feature por la operación y
    repetir la MISMA orden (el comando exacto de la spec, sin `--feature`)
    → 1ª vez rc=0 (aplica el cierre) y 2ª vez rc=0 con el no-op que LO DICE
    (`transition already registered`) y NOMBRA la entrada existente (su
    `transition_key`); el state queda byte a byte idéntico (sha256 antes =
    después, INV-10) y existe UNA sola entrada `transition: "closure"` de esa
    feature, con la entrada original intacta (INV-12: `transition_key`,
    `closed_at` y `closure_evidence` sin reescritura).

    Aislamiento de causas: el fixture está listo para cerrar (PD-8 verde) y
    la única causa del RED es el ORDEN — el guard de feature nula corre hoy
    antes del no-op (`:5062-5065` antes de `:5310`).

    RED hoy: la repetición muere en el guard de feature nula → rc=2 con el
    mensaje que sugiere `open-unit` → falla la aserción del rc=0.
    """
    fx = _ReplayFixture(tmp_path, mode="ready")

    first = fx.invoke_closure()
    out_first = first.stdout + first.stderr
    assert first.returncode == 0, (
        "precondición (comportamiento existente PD-9): la primera invocación "
        f"debe aplicar el cierre (rc=0); rc={first.returncode}: "
        f"{out_first!r}")
    entry_before = assert_closed_once(fx, "desde el primer cierre")
    state_before = fx.state_bytes()

    repeat = fx.invoke_closure()
    out_repeat = repeat.stdout + repeat.stderr

    assert repeat.returncode == 0, (
        "PD-23 violada: repetir la MISMA orden de cierre de una feature ya "
        "cerrada debe ser un no-op exitoso (rc=0); hoy muere en el guard de "
        f"feature nula antes del no-op; rc={repeat.returncode}: "
        f"{out_repeat!r}")
    assert ALREADY_REGISTERED in out_repeat.lower(), (
        "PD-23 violada: el no-op debe LO DECIR (el mensaje de la spec es "
        f"«transition already registered»): {out_repeat!r}")
    key = entry_before.get("transition_key")
    assert key and key in out_repeat, (
        "PD-23 violada: la salida del no-op debe NOMBRAR la entrada "
        f"existente (su `transition_key` {key!r}): {out_repeat!r}")
    # INV-10: la repetición idéntica NO escribe el state.
    assert fx.state_bytes() == state_before, (
        "PD-23/INV-10 violada: el replay idéntico NO debe escribir "
        "`docs/.cdad-state.json` (sha256 antes = después)")
    # PD-23/INV-12: UNA sola entrada `closure` y la entrada original intacta.
    closed_after = closure_entries(fx.read_state())
    assert len(closed_after) == 1, (
        "PD-23 violada: el replay debe dejar UNA sola entrada "
        f"`transition: \"closure\"`; hay {len(closed_after)}")
    assert closed_after[0] == entry_before, (
        "PD-23/INV-12 violada: la entrada de cierre original debe quedar "
        f"intacta (append-only, sin reescritura): "
        f"{entry_before!r} → {closed_after[0]!r}")


# ---------------------------------------------------------------- PD-25


def test_pd25_distinct_closure_after_closure_rejects_closed_naming_feature_and_done(
        tmp_path) -> None:
    """PD-25 (+ INV-11): tras un cierre aplicado, una orden de cierre
    DISTINTA (otro `--stage`, u otro `--closure-path` con otros bytes — otra
    identidad, PD-23 no la reconoce) → rc=2, marcador `state incoherent`, el
    mensaje NOMBRANDO la feature y su estado (`done`), SIN `open-unit` ni
    `open the unit` (el texto vigente a evitar, discovery §0), y SIN efectos:
    el state queda byte a byte idéntico (INV-7/INV-11). No se re-cierra
    (D-14 acotada a `closure`).

    RED hoy: la repetición distinta muere en el guard de feature nula → rc=2
    con el mensaje que NO nombra la feature ni `done` y SÍ sugiere
    `open-unit`/`open the unit` → fallan las aserciones del mensaje.
    """
    fx = _ReplayFixture(tmp_path, mode="ready")
    first = fx.invoke_closure()
    out_first = first.stdout + first.stderr
    assert first.returncode == 0, (
        "precondición (comportamiento existente PD-9): el cierre inicial se "
        f"aplica (rc=0); rc={first.returncode}: {out_first!r}")
    assert_closed_once(fx, "antes del cierre distinto")
    state_before = fx.state_bytes()

    variants = (
        ("otro --stage", dict(stage=CLOSURE_STAGE_ALT)),
        ("otro --closure-path (otros bytes)",
         dict(closure_rel=CLOSURE_REL_ALT)),
    )
    for label, kwargs in variants:
        proc = fx.invoke_closure(**kwargs)
        out = proc.stdout + proc.stderr

        assert proc.returncode == 2, (
            f"PD-25 violada ({label}): el cierre DISTINTO de una feature ya "
            f"cerrada debe rechazar cerrado (rc=2); rc={proc.returncode}: "
            f"{out!r}")
        assert STATE_INCOHERENT in out.lower(), (
            f"PD-25 violada ({label}): el rechazo debe llevar el marcador "
            f"«{STATE_INCOHERENT}»: {out!r}")
        assert FEATURE_ID in out, (
            f"PD-25 violada ({label}): el mensaje debe NOMBRAR la feature "
            f"({FEATURE_ID!r}): {out!r}")
        assert FEATURE_CLOSED in out, (
            f"PD-25 violada ({label}): el mensaje debe nombrar su estado "
            f"({FEATURE_CLOSED!r}): {out!r}")
        assert "open-unit" not in out.lower(), (
            f"PD-25 violada ({label}): el mensaje NO debe sugerir abrir la "
            f"unidad (`open-unit`): {out!r}")
        assert "open the unit" not in out.lower(), (
            f"PD-25 violada ({label}): el mensaje NO debe sugerir abrir la "
            f"unidad (`open the unit`): {out!r}")
        # INV-11: todo rechazo ocurre antes de cualquier escritura.
        assert_unchanged(fx, state_before, "PD-25", label)


# ---------------------------------------------------------------- PD-24


def test_pd24_closure_with_feature_differing_from_active_feature_fails_closed(
        tmp_path) -> None:
    """PD-24 (+ INV-11), rama (a): con `state.active_feature` no vacío,
    `closure --feature <otra>` → rc=2, marcador `state incoherent`
    NOMBRANDO las dos features, SIN efectos (state byte a byte idéntico):
    ni la activa ni la otra quedan cerradas — nunca desvío silencioso.

    RED hoy: `--feature` se IGNORA en silencio cuando hay feature activa
    (solo `late-delivery` lo lee) → el cierre cierra la feature EQUIVOCADA
    (rc=0) → falla la aserción del rc=2.
    """
    fx = _ReplayFixture(tmp_path, mode="ready")
    fx.add_feature(OTHER_FEATURE_ID)
    state = fx.read_state()
    assert state.get("active_feature") == FEATURE_ID, (
        "precondición (fixture): la feature activa es la del fixture")
    active = _feature_entry(state, FEATURE_ID)
    other = _feature_entry(state, OTHER_FEATURE_ID)
    assert active is not None and other is not None, (
        "precondición (fixture): las dos features existen en "
        "`epic_features`")
    assert active.get("status") != FEATURE_CLOSED, (
        "precondición (fixture): la activa está ABIERTA")
    assert other.get("status") != FEATURE_CLOSED, (
        "precondición (fixture): la otra feature está ABIERTA")
    before = fx.state_bytes()

    proc = fx.invoke_closure(feature=OTHER_FEATURE_ID)
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-24 violada: `closure --feature <otra>` con una feature activa "
        "DISTINTA debe rechazar por coherencia (rc=2), nunca cerrar la "
        "activa en silencio; hoy el `--feature` se ignora y cierra la "
        f"feature EQUIVOCADA; rc={proc.returncode}: {out!r}")
    assert STATE_INCOHERENT in out.lower(), (
        "PD-24 violada: el rechazo debe llevar el marcador "
        f"«{STATE_INCOHERENT}»: {out!r}")
    assert FEATURE_ID in out and OTHER_FEATURE_ID in out, (
        "PD-24 violada: el mensaje debe NOMBRAR las dos features (la activa "
        f"{FEATURE_ID!r} y la pedida {OTHER_FEATURE_ID!r}): {out!r}")
    assert_unchanged(fx, before, "PD-24", "--feature difiere de la activa")
    state_after = fx.read_state()
    assert (_feature_entry(state_after, FEATURE_ID) or {}).get(
        "status") != FEATURE_CLOSED, (
        "PD-24 violada: la feature ACTIVA no debe quedar cerrada (desvío "
        "silencioso)")
    assert (_feature_entry(state_after, OTHER_FEATURE_ID) or {}).get(
        "status") != FEATURE_CLOSED, (
        "PD-24 violada: la feature PEDIDA no debe quedar cerrada")
    assert state_after.get("active_feature") == FEATURE_ID, (
        "PD-24 violada: la feature activa no debe cambiar")


# ---------------------------------------------------------------- PD-22


def test_pd22_closure_without_feature_and_without_active_feature_rejects_without_open_unit(
        tmp_path) -> None:
    """PD-22 (+ INV-11): `--transition closure` SIN `--feature` y con
    `state.active_feature` nulo (y sin cierre previo registrado en la
    historia) → rc=2, marcador `state incoherent`, SIN `open-unit` ni
    `open the unit`, y el mensaje ofreciendo la salida legítima — nombrar la
    feature con `--feature <feature-id>`; SIN efectos (state byte a byte
    idéntico).

    RED hoy: el guard de feature nula rechaza (rc=2) pero su texto sugiere
    `open-unit`/`open the unit` y NO ofrece `--feature` → fallan las
    aserciones del mensaje.
    """
    fx = _ReplayFixture(tmp_path, mode="ready")
    fx.clear_active_feature()
    state = fx.read_state()
    assert state.get("active_feature") is None, (
        "precondición (fixture): `active_feature` quedó en null")
    assert not closure_entries(state), (
        "precondición (fixture): sin cierre previo en la historia (el caso "
        "de PD-22 es la resolución SIN feature, no un replay)")
    assert (_feature_entry(state, FEATURE_ID) or {}).get(
        "status") != FEATURE_CLOSED, (
        "precondición (fixture): la feature sigue ABIERTA en "
        "`epic_features`")
    before = fx.state_bytes()

    proc = fx.invoke_closure()
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-22 violada: `closure` sin `--feature` y sin feature activa debe "
        f"fallar cerrado (rc=2); rc={proc.returncode}: {out!r}")
    assert STATE_INCOHERENT in out.lower(), (
        "PD-22 violada: el rechazo debe llevar el marcador "
        f"«{STATE_INCOHERENT}»: {out!r}")
    assert "open-unit" not in out.lower(), (
        "PD-22 violada: el mensaje NO debe sugerir abrir la unidad "
        f"(`open-unit`): {out!r}")
    assert "open the unit" not in out.lower(), (
        "PD-22 violada: el mensaje NO debe sugerir abrir la unidad "
        f"(`open the unit`): {out!r}")
    assert "--feature" in out, (
        "PD-22 violada: el mensaje debe OFRECER la salida legítima (nombrar "
        f"la feature con `--feature <feature-id>`): {out!r}")
    assert_unchanged(fx, before, "PD-22", "sin --feature y sin feature activa")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
