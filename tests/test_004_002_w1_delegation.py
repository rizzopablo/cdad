#!/usr/bin/env python3
"""004-002 W-1/W-1b/W-1c RED — Delegación vigente sin `status` ni `epic_id`
y tokenización del `scope` (PD-3/I2; corte C §4 y aclaración de I2 en plan).

Contract: docs/specs/004-002-project-execution-bootstrap/spec.md (PD-3:
autoridad revocada/vencida/fuera de alcance → error; registros vigentes
reconocidos "sin exigirles retrospectivamente campos exclusivos de otro
epic") + docs/specs/004-002-project-execution-bootstrap/plan.md (I2) +
docs/specs/004-002-project-execution-bootstrap/cut-c.md §4 (hallazgos W-1,
W-1b y W-1c). Reglas I2 vigentes:

  - W-1:  sin `status`, deciden las condiciones de I2; con `status`, debe
          ser `active` (cualquier otro valor → no activa).
  - W-1b: si `epic_id` existe, debe coincidir con el epic activo; si falta,
          decide `scope`.
  - W-1c: en `scope`, `:` y paréntesis separan tokens; la coincidencia es
          exacta del token (F2): nunca subcadena ni prefijo de otro id.

Superficie observable (proyectos sintéticos T2 en tempdirs; ninguna
escritura en este repo):

    python3 scripts/cdad_packet.py prepare --project-root <raíz> \
        --role test-writer --substage red --objective <encargo>
    python3 scripts/cdad_packet.py validate-state --project-root <raíz>

Mapa test → postcondición (PD-3 + I2/W-1 en todos):

  1  delegation_without_status_meets_i2_bootstraps_v2   PD-3 (I2/W-1)
  2  status_active_control_still_succeeds              PD-3 (control)
  3  status_other_than_active_rejected                 PD-3 (I2/W-1)
  4  no_status_with_revoked_at_rejected                PD-3 (I2: sin revoked_at)
  5  no_status_missing_source_rejected                 PD-3 (I2: source existente)
  6  validate_state_accepts_bootstrap_without_status   PD-3/I3 (si el CLI valida v2)
  7  no_epic_id_with_i2_scope_bootstraps_v2            PD-3 (I2/W-1b) RED
  8  epic_id_equal_accepted                            PD-3 (control W-1b)
  9  epic_id_of_other_epic_rejected                    PD-3 (I2/W-1b)
 10  scope_with_colon_after_epic_id_accepted           PD-3 (I2/W-1c) RED
 11  scope_parenthesized_epic_id_accepted              PD-3 (I2/W-1c) RED
 12  scope_epic_prefix_of_other_id_rejected            PD-3 (I2/W-1c/F2)
 13  scope_x_prefix_rejected                           PD-3 (I2/W-1c/F2)
 14  real_registry_shape_bootstraps_and_validates      PD-3/I3 (integral) RED

RED hoy (W-1 ya corregido en el producto): los casos 7, 10, 11 y 14 deben
fallar por AssertionError sobre la postcondición ausente (el productor aún
exige `epic_id` y su tokenizador de `scope` no separa por `:` ni `()`),
no por import ni sintaxis. Los casos 2–6, 8, 9, 12 y 13 (controles y
negativos) ya pueden pasar contra el código actual.

Fixtures: reutilizados por import de tests/test_004_002_t2_bootstrap.py sin
modificarlos. No se lee implementación.
"""

from __future__ import annotations

import unittest

from test_004_002_t2_bootstrap import (
    AUTHORITY_REF,
    EPIC_ID,
    PACKET_BEGIN,
    ProjectTestCase,
    STATE_FILE,
    published_packets,
    read_state,
    run_prepare,
    run_validate_state,
    state_document,
    tree_snapshot,
    v2_execution_docs,
    write_state,
)


# ---------------------------------------------------------------- helpers


def delegation_i2(**overrides) -> dict:
    """Registro `hitl_delegation` con las condiciones I2 (sin campo `status`).

    I2: presente, `source` existente, `scope` que nombra el epic, epic activo
    (`active_epic`) y sin `revoked_at`. La ausencia de `status` no invalida.
    """
    hitl = {
        "epic_id": EPIC_ID,
        "source": AUTHORITY_REF,
        "scope": EPIC_ID,
        "expires_on": ["epic-closed", "epic-cancelled", "user-revoked"],
    }
    hitl.update(overrides)
    return hitl


def delegation_without(field: str, **overrides) -> dict:
    """Registro I2 sin el campo indicado (como el registro real del repo,
    que no lleva `epic_id` —W-1b—)."""
    hitl = delegation_i2(**overrides)
    hitl.pop(field, None)
    return hitl


# Forma real del `scope` del registro del dueño (cut-c §4 W-1c): dos puntos
# pegados al id del epic y texto de alcance detrás.
REAL_SCOPE = f"{EPIC_ID}: alcance del epic, specs, plan y derivados"


class W1TestCase(ProjectTestCase):
    """Base W-1: proyecto T2 con la delegación mutada y snapshot fresco."""

    def set_delegation(self, hitl: dict) -> None:
        """Sustituye `hitl_delegation` en el state y re-toma el snapshot para
        el examen de no-publicación (comparación contra lo que ve prepare)."""
        state = read_state(self.root)
        state["hitl_delegation"] = hitl
        write_state(self.root, state)
        self.before = tree_snapshot(self.root)
        self.state_before = (self.root / STATE_FILE).read_bytes()

    def assert_state_unchanged_public(self) -> None:
        super().assert_state_unchanged()
        self.assertEqual(
            tree_snapshot(self.root), self.before,
            msg="hubo publicación parcial (árbol modificado)")


# ---------------------------------------------------------------- PD-3/I2/W-1


class TestW1DelegationWithoutStatus(W1TestCase):
    """PD-3/I2 (W-1, corte C §4): sin `status`, deciden las condiciones I2."""

    def test_w1_delegation_without_status_meets_i2_bootstraps_v2(self) -> None:
        """PD-3/I2/W-1 (RED): delegación sin campo `status` con todas las
        condiciones I2 (source existente, scope que nombra el epic,
        active_epic coincide, sin revoked_at) → `prepare` rc 0 y contexto v2
        publicado (binding y paquete coherentes)."""
        self.set_delegation(delegation_i2())
        proc = run_prepare(self.root)
        self.assertEqual(
            proc.returncode, 0,
            msg="W-1: un registro vigente sin campo `status` (condiciones I2 "
                f"cumplidas) debe bootstrapear v2: {proc.stdout} {proc.stderr}")
        docs = v2_execution_docs(self.root)
        self.assertEqual(
            len(docs), 1,
            msg=f"se esperaba exactamente un contexto v2, hay: {sorted(docs)}")
        execution_id, doc = next(iter(docs.items()))
        self.assertEqual(
            doc.get("schema_version"), 2,
            msg=f"el contexto publicado no es v2: {doc.get('schema_version')!r}")
        state = read_state(self.root)
        self.assertEqual(
            state.get("execution", {}).get("id"), execution_id,
            msg=f"state.execution no referencia el contexto creado: "
                f"{state.get('execution')!r} vs {execution_id}")
        self.assertTrue(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="stdout no comienza con el paquete canónico")
        self.assertEqual(
            len(published_packets(self.root)), 1,
            msg="el bootstrap sin `status` no publicó el paquete")

    def test_w1_status_active_control_still_succeeds(self) -> None:
        """PD-3 (control): `status: \"active\"` con las mismas condiciones I2
        sigue aceptado (fixture T2 sin mutar)."""
        proc = run_prepare(self.root)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"control `status: active` debe tener éxito: "
                f"{proc.stdout} {proc.stderr}")
        self.assertEqual(
            len(v2_execution_docs(self.root)), 1,
            msg="el control no publicó contexto v2")
        self.assertTrue(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="el control no publicó el paquete")

    def test_w1_status_other_than_active_rejected(self) -> None:
        """PD-3 (I2/W-1): `status` presente con un valor distinto de
        \"active\" → delegación no activa: rc≠0, diagnóstico que nombra la
        delegación, sin escrituras (árbol y state idénticos)."""
        for value in ("revoked", "expired", "inactive", ""):
            with self.subTest(status=value):
                self.set_delegation(delegation_i2(status=value))
                proc = run_prepare(self.root)
                out = proc.stdout + proc.stderr
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"status={value!r}: prepare fue aceptado")
                self.assertNotIn(
                    "Traceback", proc.stderr,
                    msg=f"status={value!r}: fallo con traceback")
                self.assertEqual(
                    proc.stdout, "",
                    msg=f"status={value!r}: stdout no vacío")
                self.assertRegex(
                    out, r"hitl_delegation|delegaci|status",
                    msg=f"status={value!r}: el diagnóstico no nombra la "
                        f"delegación: {out!r}")
                self.assert_state_unchanged_public()

    def test_w1_no_status_with_revoked_at_rejected(self) -> None:
        """PD-3 (I2: sin `revoked_at`): registro sin `status` pero revocado →
        rc≠0, diagnóstico de revocación, sin escrituras."""
        self.set_delegation(delegation_i2(revoked_at="2026-09-29T12:00:00Z"))
        proc = run_prepare(self.root)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg="delegación sin `status` con `revoked_at` fue aceptada")
        self.assertNotIn("Traceback", proc.stderr, msg="fallo con traceback")
        self.assertEqual(proc.stdout, "", msg="stdout no vacío")
        self.assertRegex(
            out, r"revok|revocad",
            msg=f"el diagnóstico no nombra la revocación: {out!r}")
        self.assert_state_unchanged_public()

    def test_w1_no_status_missing_source_rejected(self) -> None:
        """PD-3 (I2: `source` existente): registro sin `status` cuyo `source`
        no existe → rc≠0, diagnóstico que nombra la delegación, sin escrituras."""
        self.set_delegation(delegation_i2(
            source="docs/epics/epic-004-single-source-planning/missing-authority.md"))
        proc = run_prepare(self.root)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg="delegación sin `status` y con `source` inexistente fue aceptada")
        self.assertNotIn("Traceback", proc.stderr, msg="fallo con traceback")
        self.assertEqual(proc.stdout, "", msg="stdout no vacío")
        self.assertRegex(
            out, r"hitl_delegation|delegaci|source",
            msg=f"el diagnóstico no nombra la delegación: {out!r}")
        self.assert_state_unchanged_public()

    def test_w1_validate_state_accepts_bootstrap_without_status(self) -> None:
        """PD-3/I3 (condicionado): si el CLI valida v2, `validate-state` sobre
        el state resultante de un bootstrap sin `status` da rc 0."""
        self.set_delegation(delegation_i2())
        proc = run_prepare(self.root)
        self.assertEqual(
            proc.returncode, 0,
            msg="W-1: el bootstrap sin `status` debe tener éxito antes de "
                f"validar el state: {proc.stdout} {proc.stderr}")
        validated = run_validate_state(self.root)
        self.assertEqual(
            validated.returncode, 0,
            msg=f"validate-state sobre el state v2 sin `status`: "
                f"{validated.stdout} {validated.stderr}")


# ---------------------------------------------------------------- PD-3/I2/W-1b


class TestW1bEpicIdOptional(W1TestCase):
    """PD-3/I2 (W-1b, corte C §4): si `epic_id` falta, decide `scope`; si
    existe, debe coincidir con el epic activo."""

    def test_w1b_no_epic_id_with_i2_scope_bootstraps_v2(self) -> None:
        """PD-3/I2/W-1b (RED): delegación sin `epic_id` con `scope` que nombra
        el epic y el resto de I2 → rc 0, contexto v2 con el epic resuelto y
        paquete publicado."""
        self.set_delegation(delegation_without("epic_id"))
        proc = run_prepare(self.root)
        self.assertEqual(
            proc.returncode, 0,
            msg="W-1b: un registro vigente sin `epic_id` (scope que nombra el "
                f"epic + resto de I2) debe bootstrapear v2: "
                f"{proc.stdout} {proc.stderr}")
        docs = v2_execution_docs(self.root)
        self.assertEqual(
            len(docs), 1,
            msg=f"se esperaba exactamente un contexto v2, hay: {sorted(docs)}")
        _, doc = next(iter(docs.items()))
        execution = doc.get("execution", doc)
        self.assertEqual(
            execution.get("epic_id"), EPIC_ID,
            msg=f"el contexto v2 no resolvió el epic desde `scope`: "
                f"{execution.get('epic_id')!r}")
        self.assertTrue(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="stdout no comienza con el paquete canónico")
        self.assertEqual(
            len(published_packets(self.root)), 1,
            msg="el bootstrap sin `epic_id` no publicó el paquete")

    def test_w1b_epic_id_equal_accepted(self) -> None:
        """PD-3/I2/W-1b (control): `epic_id` presente e igual al epic activo,
        sin `status` → aceptado (rc 0)."""
        self.set_delegation(delegation_i2())
        proc = run_prepare(self.root)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"control `epic_id` igual debe aceptarse: "
                f"{proc.stdout} {proc.stderr}")
        self.assertEqual(
            len(v2_execution_docs(self.root)), 1,
            msg="el control con `epic_id` igual no publicó contexto v2")
        self.assertTrue(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="el control con `epic_id` igual no publicó el paquete")

    def test_w1b_epic_id_of_other_epic_rejected(self) -> None:
        """PD-3/I2/W-1b: `epic_id` de otro epic → rc≠0, diagnóstico que nombra
        la delegación/epic, sin escrituras (árbol y state idénticos)."""
        self.set_delegation(delegation_i2(epic_id="epic-003-other-epic"))
        proc = run_prepare(self.root)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg="delegación con `epic_id` de otro epic fue aceptada")
        self.assertNotIn(
            "Traceback", proc.stderr,
            msg="fallo con traceback")
        self.assertEqual(
            proc.stdout, "", msg="stdout no vacío")
        self.assertRegex(
            out, r"hitl_delegation|delegaci|epic_id",
            msg=f"el diagnóstico no nombra la delegación/epic: {out!r}")
        self.assert_state_unchanged_public()


# ---------------------------------------------------------------- PD-3/I2/W-1c


class TestW1cScopeTokenization(W1TestCase):
    """PD-3/I2 (W-1c, corte C §4): en `scope`, `:` y paréntesis separan
    tokens; la coincidencia es exacta del token (F2)."""

    def test_w1c_scope_with_colon_after_epic_id_accepted(self) -> None:
        """PD-3/I2/W-1c (RED): `scope` con la forma real
        \"<epic-id>: alcance del epic, …\" (dos puntos pegados al id) → rc 0."""
        self.set_delegation(delegation_i2(scope=REAL_SCOPE))
        proc = run_prepare(self.root)
        self.assertEqual(
            proc.returncode, 0,
            msg="W-1c: `scope` con dos puntos pegados al id del epic debe "
                f"aceptarse (los `:` separan tokens): {proc.stdout} {proc.stderr}")
        self.assertEqual(
            len(v2_execution_docs(self.root)), 1,
            msg="el bootstrap con `scope` real no publicó contexto v2")
        self.assertTrue(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="el bootstrap con `scope` real no publicó el paquete")

    def test_w1c_scope_parenthesized_epic_id_accepted(self) -> None:
        """PD-3/I2/W-1c (RED): `scope` \"(<epic-id>)\" → rc 0 (los paréntesis
        separan tokens)."""
        self.set_delegation(delegation_i2(scope=f"({EPIC_ID})"))
        proc = run_prepare(self.root)
        self.assertEqual(
            proc.returncode, 0,
            msg="W-1c: `scope` con paréntesis alrededor del id debe aceptarse: "
                f"{proc.stdout} {proc.stderr}")
        self.assertEqual(
            len(v2_execution_docs(self.root)), 1,
            msg="el bootstrap con `scope` entre paréntesis no publicó contexto v2")
        self.assertTrue(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="el bootstrap con `scope` entre paréntesis no publicó el paquete")

    def test_w1c_scope_epic_prefix_of_other_id_rejected(self) -> None:
        """PD-3/I2/W-1c/F2: `scope` \"<epic-id>-extra: …\" (el epic como
        prefijo de OTRO id) → rc≠0, sin escrituras (F2: coincidencia exacta
        del token, nunca prefijo)."""
        self.set_delegation(delegation_i2(scope=f"{EPIC_ID}-extra: alcance de otro id"))
        proc = run_prepare(self.root)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg="scope con epic-id como prefijo de otro id fue aceptado (F2)")
        self.assertNotIn(
            "Traceback", proc.stderr,
            msg="fallo con traceback")
        self.assertEqual(
            proc.stdout, "", msg="stdout no vacío")
        self.assertRegex(
            out, r"hitl_delegation|delegaci|scope",
            msg=f"el diagnóstico no nombra la delegación/scope: {out!r}")
        self.assert_state_unchanged_public()

    def test_w1c_scope_x_prefix_rejected(self) -> None:
        """PD-3/I2/W-1c/F2: `scope` \"x<epic-id>: …\" (id con prefijo extra)
        → rc≠0, sin escrituras (F2: coincidencia exacta del token)."""
        self.set_delegation(delegation_i2(scope=f"x{EPIC_ID}: alcance con prefijo"))
        proc = run_prepare(self.root)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg="scope con prefijo extra antes del id fue aceptado (F2)")
        self.assertNotIn(
            "Traceback", proc.stderr,
            msg="fallo con traceback")
        self.assertEqual(
            proc.stdout, "", msg="stdout no vacío")
        self.assertRegex(
            out, r"hitl_delegation|delegaci|scope",
            msg=f"el diagnóstico no nombra la delegación/scope: {out!r}")
        self.assert_state_unchanged_public()


# ---------------------------------------------------------------- PD-3/I2/I3 (integral)


class TestW1RealRegistryShape(W1TestCase):
    """PD-3/I2/I3 (integral, corte C §4): la forma exacta del registro real
    del dueño (sin `status`, sin `epic_id`, scope \"<epic-id>: alcance del
    epic, …\", `source` existente) debe bootstrapear y validar."""

    def test_w1_real_registry_shape_bootstraps_and_validates(self) -> None:
        """PD-3/I2/I3 (integral, RED): delegación sin `status` ni `epic_id`,
        scope real \"<epic-id>: alcance del epic, …\" y `source` existente →
        `prepare` rc 0 con paquete publicado y `validate-state` rc 0."""
        self.set_delegation(delegation_without("epic_id", scope=REAL_SCOPE))
        proc = run_prepare(self.root)
        self.assertEqual(
            proc.returncode, 0,
            msg="integral W-1+W-1b+W-1c: la forma real del registro del dueño "
                f"debe bootstrapear v2: {proc.stdout} {proc.stderr}")
        self.assertEqual(
            len(v2_execution_docs(self.root)), 1,
            msg="el bootstrap con la forma real no publicó contexto v2")
        self.assertTrue(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="el bootstrap con la forma real no publicó el paquete")
        self.assertEqual(
            len(published_packets(self.root)), 1,
            msg="el bootstrap con la forma real no dejó paquete en disco")
        validated = run_validate_state(self.root)
        self.assertEqual(
            validated.returncode, 0,
            msg=f"validate-state sobre el state v2 de la forma real: "
                f"{validated.stdout} {validated.stderr}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
