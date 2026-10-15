#!/usr/bin/env python3
"""003-003 T2 review-fix RED — F1 (`allow` fabricado) + O-B.

Contract:
- docs/specs/003-003-progress-guards/spec.md (P3; P5; D6; invariantes 1 y 4)
- docs/specs/003-003-progress-guards/review-t2.md (F1, probes A-D-B-G'-E-C)
- docs/specs/003-003-progress-guards/review-t2-decision.md (remedio F1,
  puntos 1-5; O-B en tests/test_003_003_t2_preflight.py).

Un focal por punto de la decisión + un caso positivo. Cada aserción es
AssertionError contra el estado GREEN `2204bab` (el preflight existe y
hoy fabrica `allow` ante objetivos no evaluables) — nunca ImportError:
el test NO importa el módulo del guard, lo invoca por CLI como
superficie observable (contract `preflight-v1`).

Puntos fijados (review-t2-decision.md:4-8, con enmienda del dueño en
:12-14 — el preflight es CONSULTIVO: deny solo por regla explícita de
política o de scope del rol):

1. (Enmendado) `read` con escape `../` o ruta absoluta fuera de la
   raíz ⇒ `allow` con motivo honesto «outside project root: not
   governed by project policy»; NUNCA «within the declared scope»
   (eso fabricaría una evaluación que no ocurrió).
2. Herramienta sin destino resoluble (bash y cualquier no-write) ⇒
   `decision:"unknown"` con reason honesto; NUNCA «within the declared
   scope»; nunca un `deny` fabricado (P5, spec §2 sin-señal-fiable).
3. `read_scope` se consulta para las lecturas: leer fuera del
   read_scope del rol ⇒ deny por role-scope (probe G').
4. `path_policy` no-objeto o `private_paths` con tipo ≠ lista ⇒ rc≠0
   con «policy invalid» (fail-loud); ausentes ⇒ vacía declarada.
5. `--role` ≠ `exec_context.role` ⇒ rc≠0 con diagnóstico de
   inconsistencia de identidad (probe C).
6. (positivo, precondición) read legítimo DENTRO del read_scope sigue
   dando allow: el remedio no fabrica denies (P3/C4).

Fixtures: mismos del RED T2 (`test_003_003_t2_preflight`), proyecto
sintético en tmp — sin incidente real (P6). Los escenarios de fallo son
simulación sobre sondas propias, etiquetados como tal en cada docstring.
"""

from __future__ import annotations

import json
import unittest

from test_003_003_t2_preflight import (
    EXEC_CONTEXT_FIXTURE,
    OP_LEGIT,
    OP_PRIVATE,
    POLICY_FIXTURE,
    EstablishedProjectCase,
)


# ---------------------------------------------------------------- focales


class TestF1Punto1ReadFueraDeRaizAllowHonesto(EstablishedProjectCase):
    """Punto 1 (enmendado; P5): fuera de raíz ⇒ allow con motivo
    honesto, nunca «within the declared scope»."""

    def test_f1_p01_read_fuera_de_raiz_allow_con_motivo_honesto(
            self) -> None:
        """F1-A/F1-D (SIMULACIÓN, probe sintético): un `read` con escape
        `../` o con ruta absoluta fuera de la raíz del proyecto está
        HABILITADO por defecto (enmienda del dueño): allow rc=0 con
        motivo honesto «outside project root: not governed by project
        policy». Lo prohibido es la justificación fabricada «within the
        declared scope» (hoy, `2204bab`, allow rc=0 con esa frase) ⇒
        AssertionError.

        Mapa: P5 (el éxito declarado debe reflejar lo realmente
        evaluado), preflight consultivo (enmienda: deny solo por regla
        explícita)."""
        for op in (
            {"tool": "read", "path": "../outside/secrets.txt"},   # F1-A
            {"tool": "read", "path": "/tmp/cdad-f1-abs/secrets.txt"},  # F1-D
        ):
            proc = self.run_preflight(op)
            env = self.preflight_envelope(proc)
            self.assertEqual(
                proc.returncode, 0,
                msg="P5/enmienda (punto 1): read fuera de raíz está "
                    "habilitado por defecto → allow (rc 0), no rechazo "
                    f"fabricado; op={op!r} got rc={proc.returncode} "
                    f"stderr={proc.stderr!r}")
            self.assertEqual(
                env.get("decision"), "allow",
                msg="P5/enmienda (punto 1): la envolvente debe declarar "
                    f"decision=allow para {op!r} (fuera de raíz = "
                    "habilitado por defecto)")
            reason = env.get("reason") or ""
            self.assertIn(
                "outside project root: not governed by project policy",
                reason,
                msg="P5/enmienda (punto 1): el motivo del allow debe ser "
                    "el honesto «outside project root: not governed by "
                    f"project policy»; got reason={reason!r}")
            self.assertNotIn(
                "within the declared scope", reason,
                msg="P5/enmienda (punto 1): prohibida la justificación "
                    "fabricada «within the declared scope» sobre un "
                    f"objetivo fuera de raíz; got reason={reason!r}")


class TestF1Punto2TargetNoResolubleEsUnknown(EstablishedProjectCase):
    """Punto 2 (P5, spec §2 sin-señal-fiable): sin target resoluble ⇒
    decision unknown con reason honesto; prohibido fabricar."""

    def test_f1_p02_bash_sin_target_resoluble_es_unknown(self) -> None:
        """F1-B (SIMULACIÓN, probe sintético): `bash` (y toda herramienta
        que no escribe, sin target resoluble) no es evaluable → la
        envolvente debe declarar `decision:"unknown"` con un motivo
        honesto. Prohibido: `allow` (éxito fabricado), `deny` (rechazo
        fabricado) y reason «within the declared scope». Hoy
        (`2204bab`) fabrica allow rc=0 ⇒ AssertionError.

        Mapa: P5 + invariante 4 («unknown permanece unknown; no se
        fabrica éxito ni fracaso»)."""
        op = {"tool": "bash", "command": "rm -rf /tmp/x"}
        proc = self.run_preflight(op)
        env = self.preflight_envelope(proc)
        self.assertEqual(
            env.get("decision"), "unknown",
            msg="P5 (punto 2): bash sin destino resoluble no es evaluable "
                "→ decision='unknown' (ni allow fabricado ni deny "
                f"fabricado); got decision={env.get('decision')!r} "
                f"rc={proc.returncode}")
        combined = (proc.stdout + proc.stderr).decode("utf-8",
                                                      errors="replace")
        self.assertNotIn(
            "within the declared scope", combined,
            msg="P5 (punto 2): el motivo de unknown debe ser honesto — "
                "prohibida la frase «within the declared scope» sobre "
                f"nada evaluado; got stdout/stderr={combined!r}")


class TestF1Punto3ReadScopeSeConsulta(EstablishedProjectCase):
    """Punto 3 (P3/D6, probe G'): read_scope se consulta para lecturas."""

    def test_f1_p03_read_fuera_de_read_scope_se_deniega(self) -> None:
        """F1-G' (SIMULACIÓN, probe sintético): `read skills/lib.py` con
        un read_scope de solo `docs/specs/003-003-progress-guards` +
        `tests` ⇒ deny por role-scope (rc≠0): el read_scope se consulta
        para las lecturas. Hoy (`2204bab`) read_scope nunca se consulta
        y se fabrica allow ⇒ AssertionError.

        Mapa: P3 (prevalidación contra rol), D6."""
        op = {"tool": "read", "path": "skills/lib.py"}
        proc = self.run_preflight(op)
        self.assertNotEqual(
            proc.returncode, 0,
            msg="P3/D6 (punto 3): read fuera del read_scope del rol debe "
                "denegarse (rc≠0) antes de llamar; got "
                f"rc={proc.returncode} stdout={proc.stdout!r}")
        env = self.preflight_envelope(proc)
        self.assertEqual(
            env.get("decision"), "deny",
            msg="P3/D6 (punto 3): la envolvente debe declarar "
                f"decision=deny para {op!r}")
        self.assertEqual(
            env.get("denied_by"), "role-scope",
            msg="P3/D6 (punto 3): la evidencia del rechazo debe "
                "atribuirlo al scope del rol (denied_by='role-scope'), "
                f"no a la política; got {env.get('denied_by')!r}")


class TestF1PositivoReadLegitimoEnReadScopeSePermite(EstablishedProjectCase):
    """Punto 3 (caso positivo, P3/C4): el remedio no fabrica denies."""

    def test_f1_read_legitimo_dentro_de_read_scope_se_permite(self) -> None:
        """Caso positivo: `read tests/existing_test.py` (dentro del
        read_scope del rol y fuera de private_paths) sigue siendo allow
        (rc 0). Un deny de operación legítima es DEFECTO DEL PRODUCTO
        (P3/C4) — el remedio de F1 no debe fabricarlo.

        Mapa: P3 (deny de legítima = defecto), P7 (sin falsos
        positivos)."""
        op = {"tool": "read", "path": "tests/existing_test.py"}
        proc = self.run_preflight(op)
        self.assertEqual(
            proc.returncode, 0,
            msg="P3 (caso positivo): read legítimo dentro del read_scope "
                "debe seguir permitiéndose (rc 0) tras el remedio F1; got "
                f"rc={proc.returncode} stdout={proc.stdout!r} "
                f"stderr={proc.stderr!r}")
        env = self.preflight_envelope(proc)
        self.assertEqual(
            env.get("decision"), "allow",
            msg="P3 (caso positivo): decision=allow para un read dentro "
                "del read_scope del rol")


class TestF1Punto4PoliticaInvalidaFallaLoud(EstablishedProjectCase):
    """Punto 4 (fail-loud, probe E): shapes inválidos de política ⇒
    rc≠0 «policy invalid»; ausentes ⇒ vacía declarada."""

    def test_f1_p04_politica_con_tipo_invalido_falla_loud(self) -> None:
        """F1-E (SIMULACIÓN, fixture propio): `path_policy` con tipo no
        objeto, o `private_paths` presente con tipo ≠ lista, ⇒ rc≠0 con
        diagnóstico «policy invalid» (fail-loud: un shape inválido no se
        degrada a vacío). Si ambos faltan, se toman como vacía declarada
        y el flujo normal sigue (la legítima sigue siendo allow). Hoy
        (`2204bab`) el shape inválido es fail-open (allow) ⇒
        AssertionError.

        Mapa: P5 (no fabricar evaluación sobre entrada inválida),
        invariante 4."""
        # (a) path_policy como string (no objeto) → fail-loud.
        self.policy_path.write_text(
            json.dumps({"schema_version": 1, "path_policy": "no-es-objeto"},
                       indent=2) + "\n", encoding="utf-8")
        proc = self.run_preflight(OP_LEGIT)
        self.assertNotEqual(
            proc.returncode, 0,
            msg="P5 (punto 4): path_policy no-objeto debe fallar loud "
                "(rc≠0, policy invalid), no degradarse a vacío; got "
                f"rc={proc.returncode} stdout={proc.stdout!r}")
        combined = (proc.stdout + proc.stderr).decode("utf-8",
                                                      errors="replace")
        self.assertIn(
            "policy invalid", combined,
            msg="P5 (punto 4): el diagnóstico de política con shape "
                "inválido debe decir «policy invalid»; got "
                f"{combined!r}")

        # (b) private_paths como string (≠ lista) → fail-loud.
        policy = json.loads(json.dumps(POLICY_FIXTURE))
        policy["path_policy"]["private_paths"] = "secrets/credentials.local"
        self.policy_path.write_text(
            json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        proc = self.run_preflight(OP_PRIVATE)
        self.assertNotEqual(
            proc.returncode, 0,
            msg="P5 (punto 4): private_paths con tipo ≠ lista debe fallar "
                "loud (rc≠0), no ser ignorado (fail-open) mientras se "
                f"evalúa la ruta privada; got rc={proc.returncode} "
                f"stdout={proc.stdout!r}")
        combined = (proc.stdout + proc.stderr).decode("utf-8",
                                                      errors="replace")
        self.assertIn(
            "policy invalid", combined,
            msg="P5 (punto 4): el diagnóstico debe decir «policy invalid» "
                "ante private_paths mal tipado; got " f"{combined!r}")

        # (c) ausentes → vacía declarada: el flujo normal no se rompe.
        self.policy_path.write_text(
            json.dumps({"schema_version": 1}, indent=2) + "\n",
            encoding="utf-8")
        proc = self.run_preflight(OP_LEGIT)
        self.assertEqual(
            proc.returncode, 0,
            msg="P5 (punto 4): path_policy AUSENTE se toma como vacía "
                "declarada (no inválida): la operación legítima del rol "
                "sigue siendo allow (rc 0); got "
                f"rc={proc.returncode} stdout={proc.stdout!r}")


class TestF1Punto5RolDesalineadoSeRechaza(EstablishedProjectCase):
    """Punto 5 (identidad, probe C): --role ≠ exec_context.role ⇒ rc≠0."""

    def test_f1_p05_role_desalineado_de_exec_context_se_rechaza(
            self) -> None:
        """F1-C (SIMULACIÓN, probe sintético): `--role reviewer` con un
        execution-context cuyo `role` es `test-writer` ⇒ rc≠0 con
        diagnóstico de inconsistencia de identidad: el rol evaluado debe
        ser verificable contra el contexto, no un flag confiable a
        ciegas. Hoy (`2204bab`) el contraste no existe y se fabrica
        allow «within the declared scope of role 'reviewer'» ⇒
        AssertionError.

        Mapa: P5 (identidad no fabricada), D6 (prevalidación honesta)."""
        proc = self.run_preflight(OP_LEGIT, role="reviewer")
        self.assertNotEqual(
            proc.returncode, 0,
            msg="P5 (punto 5): --role que contradice "
                f"exec_context.role ({EXEC_CONTEXT_FIXTURE['role']!r}) "
                "debe rechazarse (rc≠0) con diagnóstico de "
                f"inconsistencia; got rc={proc.returncode} "
                f"stdout={proc.stdout!r}")
        combined = (proc.stdout + proc.stderr).decode("utf-8",
                                                      errors="replace")
        self.assertTrue(
            combined.strip(),
            msg="P5 (punto 5): el rechazo por rol desalineado exige un "
                "diagnóstico no vacío (stdout+stderr)")
        self.assertIn(
            "reviewer", combined,
            msg="P5 (punto 5): el diagnóstico debe nombrar el rol "
                f"desalineado ('reviewer'); got {combined!r}")


if __name__ == "__main__":
    unittest.main()
