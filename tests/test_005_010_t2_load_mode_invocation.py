#!/usr/bin/env python3
"""005-010 T2 RED — Modo de carga por la versión instalada + invocación
configurable (PD-3, PD-4; INV-2, INV-6, INV-7).

Contract: docs/specs/005-010-real-opencode-delegation/spec.md (PD-3, PD-4;
INV-2, INV-6, INV-7) + plan.md §T2. Consume `senal-durable-sqlite` (T1,
GREEN): la fixture AdapterCase (migrada a SQLite real chico, PD-7) y la
unidad de modo de este RED.

Superficie observable bajo prueba (proyecto sintético en tempdir, binario
falso como frontera de proceso: NINGUNA lectura de implementación, ningún
runtime vivo). Los tests observan SOLO artefactos:

  - el argv registrado por el binario falso (`<fake>/calls.jsonl`):
    `--agent`, `--session`, `--standalone`/`--server <url>`/`--auto`;
  - la base SQLite del fixture (campo `sessions_db` de la config): la fila
    `session_v2` correlacionada y su columna `agent`;
  - el registro I8 del intento (mismo ledger, esquema cerrado);
  - el recibo durable (`.cdad/runtime/results/<exec>/<packet>/receipt.json`);
  - el envelope {attempt, session, termination, delivery_ref, diagnosis}.

La configuración de ejecución llega por `--exec-config` (el mismo archivo
del fixture, reescrito por el test con las claves `server`/`auto` cuando la
variante lo requiere — PD-4: el nivel correcto es la configuración, nada
hardcodeado). URL del fixture: `fixture.invalid` (TLD reservado; sin
valores de este VPS, INV-7).

Mapa test → postcondición (spec 005-010):

  1  TestPd3SubagentEntryDispatches::test_pd3_subagent_entry_dispatches_and_completes
       PD-3 (positiva) — con el derivado cdad-<rol> publicado con
       `mode: subagent`, el adaptador SÍ despacha y llega a `completed`
       con entrega durable (recibo `pending`) y la fila durable declarando
       la identidad cdad del rol.
  2  TestPd3UnpublishedDerivedFailsClosed::test_pd3_unpublished_derived_fails_closed_before_dispatch
       PD-3 — si el derivado NO está publicado, falla cerrado ANTES de
       despachar (sin invocación, sin transporte, sin sesión, sin recibo)
       con diagnóstico que nombra el agente.
  3  TestPd3DurableIdentityMismatch::test_pd3_durable_identity_mismatch_never_delivers_never_generic
       PD-3 (INV-6) — si la fila durable declara un agente DISTINTO de
       cdad-<rol>, no declara entrega (`blocked` con diagnóstico que
       nombra AMBOS agentes) y JAMÁS invoca un agente no-Cdad.
  4  TestPd4InvocationArgvMatrix::test_pd4_default_argv_standalone_auto_without_server
       PD-4 — argv por defecto incluye `--standalone` y `--auto` y NO
       `--server`.
  5  TestPd4InvocationArgvMatrix::test_pd4_server_config_uses_server_without_standalone
       PD-4 — con `server` en la config, argv incluye `--server <url>` y
       NO `--standalone`.
  6  TestPd4InvocationArgvMatrix::test_pd4_auto_false_omits_auto_flag
       PD-4 — con `auto: false` en la config, argv NO incluye `--auto`.
  7  TestPd4PwdProjectDirectory::test_invocation_pwd_is_project_root_and_durable_row_directory_matches
       PD-4 ('invocación realmente soportada'; hecho del orquestador
       verificado contra OpenCode v2.0.26 REAL: `opencode run` toma el
       DIRECTORIO DEL PROYECTO de la env PWD, NO del cwd del proceso) +
       PD-3 de 005-009 (proyecto explícito, independiente del cwd del
       coordinador) — delegando desde un coordinador con PWD apuntando a
       OTRO directorio, la invocación recibe PWD == project root, el
       binario falso (como el runtime real) halla el agente derivado en
       ese PWD, la fila durable lleva directory == project root y la
       delegación completa.

RED esperado (plan §T2, adaptador vigente post T1-GREEN):
  (1)  la entry `subagent` es RECHAZADA (`blocked` en vez de `completed`);
  (3)  con la fila declarando otro agente, el vigente no verifica identidad
       desde la fila y DECLARA ENTREGA (`completed`);
  (4)  el argv NO lleva `--standalone`/`--auto`.
  (2)  puede pasar hoy (el vigente ya falla cerrado pre-despacho por otra
       causa): la unidad fija el comportamiento postcondición — se reporta
       su estado observado en el RED.
  (5)/(6)  hoy la config `server`/`auto` no existe: `--server <url>` no
       aparece (el subtest 5 falla por la ausencia de `--server`).
  (7)  RED de T2b (corrección del orquestador): el adaptador vigente HEREDA
       el PWD del coordinador (no fija PWD = project root en la invocación)
       — la aserción `pwd == project root` falta por comportamiento (pwd
       ajeno registrado por el binario falso) y la fila durable lleva
       directory == el PWD ajeno del coordinador, no el project root.
Cada fallo RED debe ser AssertionError sobre el COMPORTAMIENTO ausente
(despacho/terminación/identidad/argv/pwd), no import/sintaxis.
"""

from __future__ import annotations

import json
from pathlib import Path

from test_005_009_t1_interface import dispatch_records
from test_005_009_t2_opencode_adapter import (
    FOREIGN_ROW_AGENT,
    AdapterCase,
    durable_session_rows,
)

EXPECTED_ROLE_AGENT = "cdad-test-writer"  # el derivado cdad-<rol> del paquete
FIXTURE_SERVER_URL = "http://fixture.invalid:4747"  # TLD reservado (INV-7)


# ----------------------------------------------------------------- PD-3


class TestPd3SubagentEntryDispatches(AdapterCase):
    """PD-3 positiva: con el agente derivado cdad-<rol> publicado con
    `mode: subagent` (semilla real de la fixture), el adaptador SÍ
    despacha y llega a `completed`: la identidad se verifica desde la fila
    durable, sin fallback genérico (INV-6)."""

    def test_pd3_subagent_entry_dispatches_and_completes(self) -> None:
        """PD-3 (positiva): la entry derivada `mode: subagent` publicada
        SÍ despacha: terminación `completed` con entrega durable (recibo
        `pending`, texto final dentro de la entrega), intento en el ledger
        I8, el argv nombra el agente cdad del paquete, la fila durable
        declara la identidad cdad del rol ( identidad desde la fila) y la
        identidad de sesión declarada es la que la invocación pasó en
        `--session <id>` (PD-1)."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("pd3-subagent", variant="succeeded")
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.run_opencode(fake)
        out = self.envelope(proc, "PD-3 entry subagent")

        # El despacho ocurre y llega a completed (RED hoy: blocked).
        self.assertEqual(
            out["termination"], "completed",
            msg=f"entry `mode: subagent` publicada: el adaptador NO "
                f"despachó a completed (PD-3: el modo DEJA de condicionar; "
                f"la barrera es la identidad desde la fila): "
                f"{out['termination']!r}, diagnosis {out.get('diagnosis')!r}")
        self.assert_durable_delivery_ref(out)
        self.assert_receipt_no_gate()
        self.assert_final_text_in_delivery()
        self.assert_attempt_is_in_ledger(out, records_before)

        # El argv nombra al agente cdad del paquete (jamás un genérico).
        call = self.packet_call(fake, "PD-3 entry subagent")
        self.assertIn(
            EXPECTED_ROLE_AGENT, " ".join(call["argv"]),
            msg=f"la invocación del binario no nombra el agente cdad del "
                f"paquete ({EXPECTED_ROLE_AGENT}): "
                f"{' '.join(call['argv'])!r}")
        self.assert_no_generic_agent_fallback(fake)

        # La fila durable declara la identidad cdad del rol (la invocación
        # pasó --agent cdad-<rol> y la fila la reporta).
        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            [row.get("agent") for row in rows], [EXPECTED_ROLE_AGENT],
            msg=f"la fila durable no declara la identidad cdad del rol "
                f"(PD-3, identidad desde la fila): "
                f"{[row.get('agent') for row in rows]!r}")
        self.assertEqual(
            out["session"], call.get("session_id_written"),
            msg=f"la identidad de sesión declarada no es el id que la "
                f"invocación pasó en --session (PD-1): {out['session']!r}")


class TestPd3UnpublishedDerivedFailsClosed(AdapterCase):
    """PD-3: si el derivado cdad-<rol> NO está publicado, falla cerrado
    ANTES de despachar (sin invocación del binario), con diagnóstico que
    nombra el agente; sin sesión, sin entrega, sin recibo."""

    def test_pd3_unpublished_derived_fails_closed_before_dispatch(self) -> None:
        """PD-3 (pre-despacho): con `.opencode/agents/cdad-test-writer.md`
        AUSENTE del proyecto publicado, el adaptador falla cerrado:
        terminación `blocked` con diagnóstico accionable que nombra el
        agente derivado faltante; el binario falso NUNCA es invocado, no
        hubo transporte de bytes, no se declara identidad de sesión, no
        hay recibo y jamás un agente genérico no-Cdad (INV-6)."""
        self.assert_derived_agents_published()
        derived = self.root / ".opencode" / "agents" / "cdad-test-writer.md"
        self.assertTrue(
            derived.is_file(),
            msg="precondición (fixture): el derivado cdad-test-writer.md "
                "no está publicado antes de la manipulación")
        derived.unlink()  # fixture: el derivado cdad-<rol> NO está publicado
        fake = self.fake_runtime("pd3-absent", variant="succeeded")

        proc = self.run_opencode(fake)
        out = self.envelope(proc, "PD-3 derivado ausente")

        # Fallo cerrado pre-despacho, nombrado.
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"derivado ausente: el adaptador no falló cerrado en la "
                f"clase 'blocked' (PD-3: sin derivado publicado no hay "
                f"despacho): {out['termination']!r}")
        diagnosis = out.get("diagnosis")
        self.assertIsInstance(
            diagnosis, str, msg="derivado ausente: el diagnóstico no es texto")
        self.assertTrue(
            diagnosis.strip(),
            msg="derivado ausente: diagnóstico vacío (la salida legítima "
                "ante bloqueo es un diagnóstico accionable)")
        self.assertIn(
            EXPECTED_ROLE_AGENT, diagnosis.lower(),
            msg=f"derivado ausente: el diagnóstico no nombra el agente "
                f"derivado faltante '{EXPECTED_ROLE_AGENT}' (PD-3): "
                f"{diagnosis!r}")

        # SIN invocación ni despacho parcial.
        self.assertEqual(
            self.binary_calls(fake), [],
            msg="derivado ausente: DESPACHÓ sesión (el binario falso fue "
                "invocado; argv ver fixtures)")
        self.assertFalse(
            fake["sent"].is_file(),
            msg="derivado ausente: entregó bytes al binario falso (sin "
                "invocación, PD-3)")
        self.assertFalse(
            out.get("session"),
            msg=f"derivado ausente: declaró identidad de sesión "
                f"({out.get('session')!r}; nunca hubo sesión)")
        self.assert_no_receipt_fabricated("PD-3 derivado ausente")
        self.assert_no_generic_agent_fallback(fake)


class TestPd3DurableIdentityMismatch(AdapterCase):
    """PD-3/INV-6: si la fila durable declara un agente DISTINTO de
    cdad-<rol>, no declara entrega: `blocked` con diagnóstico que nombra
    AMBOS agentes, sin recibo, y JAMÁS invoca un agente no-Cdad.

    SEED_MODE = "all": bajo el adaptador VIGENTE (que aún exige `mode:
    all`) la semilla `subagent` bloquearía antes de despachar y el RED no
    observaría el hecho de identidad. Con `all` el vigente SÍ despacha y
    DECLARA ENTREGA con la fila foránea — la violación PD-3 observada.
    Bajo GREEN T2 el modo ya no condiciona: la semilla es irrelevante y la
    unidad vale igual."""

    SEED_MODE = "all"

    def test_pd3_durable_identity_mismatch_never_delivers_never_generic(self) -> None:
        """PD-3/INV-6: con la variante `wrong-agent` (fila durable con
        idle_outcome 'succeeded' pero agent = FOREIGN_ROW_AGENT), el
        adaptador NO declara entrega: terminación `blocked` con
        diagnóstico que nombra AMBOS agentes; sin recibo; UNA sola
        invocación, con el agente cdad del paquete en el argv (jamás un
        genérico no-Cdad)."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("pd3-identity", variant="wrong-agent")
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.run_opencode(fake)
        out = self.envelope(proc, "PD-3 identidad distinta")

        # Precondición del fixture: la fila durable declara el agente
        # foráneo (todo lo demás es una fila 'succeeded' normal).
        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            [row.get("agent") for row in rows], [FOREIGN_ROW_AGENT],
            msg="fixture: la fila durable no declara el agente foráneo "
                f"{FOREIGN_ROW_AGENT!r} (precondición de la unidad): filas "
                f"{[dict(row) for row in rows]!r}")

        # La identidad desde la fila es la barrera: SIN entrega (RED hoy:
        # el vigente declara completed).
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"la fila durable declara {FOREIGN_ROW_AGENT!r} (distinto "
                f"de {EXPECTED_ROLE_AGENT}): el adaptador no falló cerrado "
                f"en la clase 'blocked' (PD-3: la identidad se verifica "
                f"desde la fila durable): {out['termination']!r}")
        self.assertFalse(
            out.get("delivery_ref"),
            msg=f"la fila declara otro agente y el adaptador declaró "
                f"entrega (delivery_ref {out.get('delivery_ref')!r}; PD-3: "
                f"NO declara entrega)")
        self.assert_no_receipt_fabricated("PD-3 identidad distinta")

        # Diagnóstico que nombra AMBOS agentes (el de la fila y el cdad).
        diagnosis = out.get("diagnosis")
        self.assertIsInstance(
            diagnosis, str, msg="el diagnóstico no es texto")
        self.assertTrue(
            diagnosis.strip(),
            msg="diagnóstico vacío (la salida legítima ante bloqueo es un "
                "diagnóstico accionable)")
        for token in (FOREIGN_ROW_AGENT, EXPECTED_ROLE_AGENT):
            self.assertIn(
                token.lower(), diagnosis.lower(),
                msg=f"el diagnóstico no nombra {token!r} (PD-3: ambos "
                    f"agentes, el de la fila y el cdad esperado): "
                    f"{diagnosis!r}")

        # JAMÁS un agente no-Cdad (INV-6): UNA sola invocación, y con el
        # agente cdad del paquete en el argv.
        calls = self.binary_calls(fake)
        self.assertEqual(
            len(calls), 1,
            msg=f"la invocación no fue UNA sola (¿reintento con otro "
                f"agente?, PD-3/INV-6): {len(calls)}; argv: "
                f"{[call.get('argv') for call in calls]!r}")
        self.assertIn(
            EXPECTED_ROLE_AGENT, " ".join(calls[0].get("argv", [])),
            msg=f"la única invocación no nombró al agente cdad del paquete "
                f"(PD-3): {' '.join(calls[0].get('argv', []))!r}")
        self.assert_no_generic_agent_fallback(fake)
        self.assert_attempt_is_in_ledger(out, records_before)


# ----------------------------------------------------------------- PD-4


class TestPd4InvocationArgvMatrix(AdapterCase):
    """PD-4: la invocación usa el transporte/permisos del NIVEL CORRECTO
    (config de ejecución), nunca hardcodeados: `--standalone` por defecto
    con `--auto` (activado por defecto) y sin `--server`; con `server` en
    la config, `--server <url>` en vez de `--standalone`; con `auto:
    false`, sin `--auto`.

    SEED_MODE = "all": bajo el adaptador VIGENTE (que aún exige `mode:
    all`) la semilla `subagent` bloquearía ANTES de despachar y el RED
    fracasaría en «sin invocación» en vez de en el argv ausente. Con `all`
    el vigente SÍ despacha y el RED observa EXACTAMENTE el argv: sin
    `--standalone`/`--auto`. Bajo GREEN T2 el modo ya no condiciona.
    """

    SEED_MODE = "all"

    def _dispatch_argv(self, name: str, *,
                       overrides: dict | None = None) -> tuple[list[str], dict]:
        """Despacha con el binario falso y devuelve (argv de LA invocación
        que transportó el paquete, envelope). Con `overrides`, reescribe la
        config de ejecución del fixture (nivel correcto: el archivo que la
        interfaz pasa al adaptador, PD-4)."""
        fake = self.fake_runtime(name, variant="succeeded")
        if overrides:
            config = json.loads(fake["config"].read_text(encoding="utf-8"))
            config.update(overrides)
            fake["config"].write_text(
                json.dumps(config, indent=2, sort_keys=True) + "\n",
                encoding="utf-8")
        proc = self.run_opencode(fake)
        out = self.envelope(proc, f"PD-4 {name}")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"{name}: el despacho no llegó a completed (precondición "
                f"de la observación del argv): {out['termination']!r}, "
                f"diagnosis {out.get('diagnosis')!r}")
        call = self.packet_call(fake, f"PD-4 {name}")
        return call["argv"], out

    def test_pd4_default_argv_standalone_auto_without_server(self) -> None:
        """PD-4 (por defecto): con config por defecto (sin `server`/`auto`
        declarados), el argv incluye `--standalone` y `--auto` y NO
        `--server` (nunca se acopla al servicio de fondo del dueño sin
        pedirlo, PD-4/R4)."""
        argv, _out = self._dispatch_argv("pd4-default")
        self.assertIn(
            "--standalone", argv,
            msg=f"el argv por defecto no lleva `--standalone` (PD-4: el "
                f"servidor privado es el defecto; sin él se acopla al "
                f"servicio de fondo del dueño): {argv!r}")
        self.assertIn(
            "--auto", argv,
            msg=f"el argv por defecto no lleva `--auto` (PD-4: permisos "
                f"no interactivos, activado por defecto): {argv!r}")
        self.assertNotIn(
            "--server", argv,
            msg=f"el argv por defecto lleva `--server` (PD-4: sin `server` "
                f"en la config no hay servidor declarado): {argv!r}")

    def test_pd4_server_config_uses_server_without_standalone(self) -> None:
        """PD-4 (server por config): con `server` en la config de
        ejecución, el argv incluye `--server <url>` (la URL declarada por
        la config) y NO `--standalone` (alternativas excluyentes, nunca a
        la vez)."""
        argv, _out = self._dispatch_argv(
            "pd4-server", overrides={"server": FIXTURE_SERVER_URL})
        self.assertIn(
            "--server", argv,
            msg=f"con `server` en la config el argv no lleva `--server` "
                f"(PD-4: el despliegue lo declara por config): {argv!r}")
        index = argv.index("--server")
        self.assertLess(
            index + 1, len(argv),
            msg=f"`--server` sin valor en el argv (PD-4): {argv!r}")
        self.assertEqual(
            argv[index + 1], FIXTURE_SERVER_URL,
            msg=f"el valor de --server no es el declarado por la config "
                f"(PD-4/INV-7): {argv[index + 1]!r} != "
                f"{FIXTURE_SERVER_URL!r}")
        self.assertNotIn(
            "--standalone", argv,
            msg=f"con `server` en la config el argv lleva TAMBIÉN "
                f"`--standalone` (PD-4: alternativas excluyentes): "
                f"{argv!r}")

    def test_pd4_auto_false_omits_auto_flag(self) -> None:
        """PD-4 (auto configurable): con `auto: false` en la config, el
        argv NO incluye `--auto` (configurable, no hardcodeado); el resto
        del defecto (standalone) se conserva."""
        argv, _out = self._dispatch_argv("pd4-noauto", overrides={"auto": False})
        self.assertNotIn(
            "--auto", argv,
            msg=f"con `auto: false` en la config el argv lleva `--auto` "
                f"(PD-4: configurable por config): {argv!r}")
        self.assertIn(
            "--standalone", argv,
            msg=f"con `auto: false` el defecto `--standalone` dejó de "
                f"aplicar (PD-4: la clave `auto` no altera el transporte): "
                f"{argv!r}")
        self.assertNotIn(
            "--server", argv,
            msg=f"con `auto: false` el argv lleva `--server` (PD-4: sin "
                f"`server` en la config no hay servidor): {argv!r}")


# ------------------------------------- PD-4 invocación real: PWD del proyecto
# T2b de 005-010 (corrección del orquestador). Hecho verificado contra
# OpenCode v2.0.26 REAL: `opencode run` toma el DIRECTORIO DEL PROYECTO de
# la variable de entorno PWD, no del cwd del proceso (cwd=tmp con PWD=repo
# -> la sesión queda en el repo y no ve los agentes del proyecto temporal;
# PWD=tmp -> correcto). El adaptador por tanto debe fijar PWD == project
# root en la invocación (PD-4 'invocación realmente soportada'; PD-3 de
# 005-009: proyecto explícito e independiente del cwd del coordinador). El
# binario falso, fiel al runtime, registra el PWD de su entorno y usa ese
# PWD como directorio del proyecto (búsqueda del agente derivado y columna
# session_v2.directory — fixture migrado en test_005_009_t2_opencode_
# adapter.py).


class TestPd4PwdProjectDirectory(AdapterCase):
    """PD-4 ('invocación realmente soportada') + PD-3 de 005-009: la
    invocación del CLI destino lleva PWD == project root — el directorio
    del proyecto es EXPLÍCITO e independiente del PWD/cwd del coordinador.

    El coordinador delega con su PWD apuntando a OTRO directorio (como un
    shell cd'ed a un tempdir ajeno); el runtime real tomaría ese PWD como
    proyecto y NO vería los agentes derivados del proyecto temporal. La
    corrección exige que la invocación reciba PWD == project root, que la
    fila durable declare directory == project root y que la delegación
    completa (entrega durable por receive)."""

    def test_invocation_pwd_is_project_root_and_durable_row_directory_matches(self) -> None:
        """Delegando desde un coordinador con PWD ajeno: la invocación del
        binario recibe PWD == project root (no el PWD del coordinador), el
        agente derivado cdad-<rol> se halla en ese proyecto PWD (como lo
        busca el runtime real), la fila durable correlacionada lleva
        directory == project root y la delegación completa: terminación
        `completed` con entrega durable (recibo `pending`, texto final
        dentro de la entrega) e intento en el ledger I8."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("pwd-project", variant="succeeded")
        records_before = dispatch_records(self.root, self.execution_id)

        # PWD del coordinador apuntando a OTRO directorio (tempdir ajeno:
        # no es el repo, ni el proyecto, ni contiene el árbol stageado).
        pwd_foreign = Path(self._tmp) / "pwd-foreign"
        pwd_foreign.mkdir(parents=True, exist_ok=True)

        proc = self.run_opencode(fake, cwd=pwd_foreign)
        out = self.envelope(proc, "PWD del coordinador ajeno")

        # La delegación completa (precondición de la observación).
        self.assertEqual(
            out["termination"], "completed",
            msg=f"PWD del coordinador ajeno: la delegación no completó "
                f"(precondición de la observación del pwd y de la fila): "
                f"{out['termination']!r}, diagnosis {out.get('diagnosis')!r}")

        # 1. La invocación recibe PWD == project root (PD-4: el directorio
        #    del proyecto que el runtime real toma de la env PWD es el
        #    EXPLÍCITO del encargo — jamás el PWD heredado del coordinador).
        call = self.packet_call(fake, "PWD del coordinador ajeno")
        self.assertEqual(
            call.get("pwd"), str(self.root),
            msg=f"la invocación no recibió PWD == project root (PD-4/T2b: "
                f"el runtime real toma el directorio del proyecto de la "
                f"env PWD y NO del cwd del proceso; el coordinador delegó "
                f"con PWD ajeno y el adaptador debe fijar PWD = project "
                f"root en la invocación): pwd registrado "
                f"{call.get('pwd')!r} != {str(self.root)!r}")

        # 2. El agente derivado cdad-<rol> se HALLA en el proyecto PWD (el
        #    binario falso, como el runtime real, lo busca en
        #    <PWD>/.opencode/agents/: ahí lo publicó `prepare`).
        self.assertIs(
            call.get("agent_found_in_project"), True,
            msg=f"el binario falso no halló el agente derivado "
                f"{EXPECTED_ROLE_AGENT} en el proyecto PWD de la "
                f"invocación (PD-4/T2b: con PWD == project root el "
                f"derivado publicado por prepare DEBE hallarse donde el "
                f"runtime real lo busca): agent_found_in_project "
                f"{call.get('agent_found_in_project')!r}")

        # 3. La fila durable lleva directory == project root (no el PWD
        #    ajeno del coordinador, no el cwd del proceso).
        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            [row.get("directory") for row in rows], [str(self.root)],
            msg=f"la fila durable no declara directory == project root "
                f"(PD-4/T2b: el runtime real registra en session_v2."
                f"directory el proyecto tomado de la env PWD de la "
                f"invocación): "
                f"{[row.get('directory') for row in rows]!r} != "
                f"[{str(self.root)!r}]")

        # 4. La delegación completa es la recorrida durable completa.
        self.assert_durable_delivery_ref(out)
        self.assert_receipt_no_gate()
        self.assert_final_text_in_delivery()
        self.assert_attempt_is_in_ledger(out, records_before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
