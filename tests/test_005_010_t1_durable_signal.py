#!/usr/bin/env python3
"""005-010 T1 RED — Señal durable real (SQLite), correlación, clasificación y
observación I8 (PD-1, PD-2, PD-5, PD-6; la PD-7 es la FIXTURE misma).

Contract: docs/specs/005-010-real-opencode-delegation/spec.md (PD-1, PD-2,
PD-5, PD-6, PD-7; INV-3, INV-4, INV-5) + plan.md §T1. La fixture (el doble
migrado de tests/test_005_009_t2_opencode_adapter.py, AdapterCase) es la
PD-7: un SQLite REAL CHICO con el esquema observado (`session_v2` +
`session_message`, discovery §3.4) escrito en la ruta `sessions_db` de la
config de ejecución, con la fila `session_v2` correlacionada llevando el id
recibido en `--session` y el TEXTO FINAL en el ÚLTIMO `session_message`
`assistant`.

Superficie observable bajo prueba (proyecto sintético en tempdir, binario
falso como frontera de proceso: NINGUNA lectura de implementación, ningún
runtime vivo). Los tests observan SOLO artefactos durables:

  - el argv registrado por el binario falso (`<fake>/calls.jsonl`):
    `--session <id>` y `--agent`;
  - la base SQLite del fixture (campo `sessions_db` de la config): filas
    `session_v2` y `session_message` (lectores `durable_*` importados);
  - el registro I8 del intento del worker
    (`.cdad/executions/<id>/dispatches/<attempt>.json`, esquema cerrado);
  - el recibo durable (`.cdad/runtime/results/<exec>/<packet>/receipt.json`);
  - el envelope {attempt, session, termination, delivery_ref, diagnosis}.

Invocación (la misma del oráculo 005-009):

    python3 <cdad_delegate.py> --project-root <raíz> --packet <packet-id> \
        --destination opencode --exec-config <config.json>

SEED_MODE = "all" en TODAS las unidades: el modo de carga vigente se
CONSERVA (el adaptador exige `mode: all` para despachar) — la inversión
(`mode: subagent` + identidad desde la fila durable) es T2 de 005-010.

Mapa test → postcondición (spec 005-010):

  1  TestPd1SessionCorrelation::test_pd1_durable_signal_correlated_by_session_id
       PD-1 — el argv lleva `--session <id>`, la fila leída es la de ESE id,
       el texto final es el del ÚLTIMO assistant (no el decoy intermedio),
       identidad de sesión y entrega durables.
  2  TestPd1SessionCorrelation::test_pd1_rc0_before_idle_is_not_completed
       PD-1 — un cliente rc=0 ANTES de que la fila quede idle NO produce
       `completed` (timeout acotado, sin recibo).
  3  TestPd2FailClosedStoreDiagnostics::test_pd2_unknown_schema_fails_closed_naming_missing_column
       PD-2 — store sin la columna `idle_outcome` → `blocked` con
       diagnóstico que NOMBRA la columna; sin recibo; sin esperar de más.
  4  TestPd2FailClosedStoreDiagnostics::test_pd2_unreadable_store_fails_closed_without_trace
       PD-2 — store NO SQLite (bytes basura) → `blocked` con diagnóstico;
       nunca una traza no capturada; sin recibo; sin esperar de más.
  5  TestPd5IdleOutcomeClassification::test_pd5_termination_from_idle_outcome_matrix
       PD-5 — `succeeded→completed` (recibo `pending`), `failed→blocked`,
       `interrupted→cancelled`, sin idle→`timeout`, `rc≠0` sin
       fila→`transport-error`; ninguna no-completada fabrica recibo.
  6  TestPd6WorkerI8FromDurableRow::test_pd6_worker_i8_session_and_model_from_durable_row
       PD-6 — el registro I8 del worker toma `session` y `model_reported`
       de la FILA DURABLE (el `model` de la fila es DISTINTO del
       `model_configured` de la config para probar la provenance por
       comportamiento), con `provenance` que declara la fuente; esquema
       cerrado I8 conservado; `runtime` sigue de la configuración y
       `model_configured` de la config de delegación (A-1 de 006-003
       U4/D3, reemplazo declarado).

A-1 (006-005 U1b, REEMPLAZO DECLARADO en el RED de esa unidad): la
localización «el registro nuevo del ledger que NO es el de la interfaz» del
caso 6 (`:431-449`) y las aserciones del registro de la INTERFAZ
(`:536-543`) se reemplazan por «UN SOLO registro por despacho»: la interfaz
RELAYA el `attempt` del módulo y no registra (D-14/PD-1), así que el registro
del despacho ES el del intento que el sobre declara, con `session` y
`model_reported` de la fila durable. Se conservan las aserciones del registro
del worker; se retiran las del registro de la interfaz (que ya no existe).

PD-7 (doble fiel): la plantilla FAKE_BINARY_SOURCE migrada + los lectores
`durable_*` viven en tests/test_005_009_t2_opencode_adapter.py; su fidelidad
se verifica por comportamiento en las unidades de arriba (variantes →
terminaciones declaradas).

RED esperado (plan §T1, adaptador vigente = lector JSON de `sessions.json`):
  (i)   variantes con fila idle (succeeded/failed/interrupted): sin señal
        material usable → NO completed/blocked/cancelled (el adaptador
        vigente termina `transport-error`/`timeout`, y contra el store no
        JSON puede morir con UnicodeDecodeError NO capturada — PD-2);
  (ii)  el argv NO lleva `--session <id>`;
  (iii) `model_reported`/`session` del I8 NO salen de la fila durable;
  (iv)  `unknown-schema` NO falla cerrado (ni `not-sqlite`).
Cada fallo RED debe ser AssertionError sobre el COMPORTAMIENTO ausente
(terminación/correlación/provenance), no import/sintaxis.
"""

from __future__ import annotations

import json
import time
import unittest

from test_005_009_t1_interface import I8_RECORD_KEYS, dispatch_records
from test_005_009_t2_opencode_adapter import (
    DECOY_FINAL_TEXT,
    FAKE_FINAL_TEXT,
    FAKE_MODEL,
    FAKE_RUNTIME,
    ROW_MODEL,
    TEST_WAIT_TIMEOUT_SECONDS,
    VARIANT_TERMINATION,
    AdapterCase,
    durable_last_assistant_text,
    durable_messages,
    durable_session_rows,
)


# ----------------------------------------------------------------- PD-1


class TestPd1SessionCorrelation(AdapterCase):
    """PD-1: el adaptador ELIGE el id y lo pasa en `--session <id>`; lee la
    base que declara la config (`sessions_db`, ruta configurable) y
    correlaciona inequívocamente por ese id; el texto final es el del
    ÚLTIMO mensaje `assistant`; nunca usa el rc del cliente como señal."""

    SEED_MODE = "all"

    def test_pd1_durable_signal_correlated_by_session_id(self) -> None:
        """PD-1: el argv de la invocación lleva `--session <id>`; la fila
        `session_v2` del store es EXACTAMENTE la de ese id (una sola fila);
        el envelope declara la identidad de sesión de esa fila; la entrega
        durable lleva el TEXTO FINAL del ÚLTIMO assistant del store (el
        texto intermedio decoy de un assistant ANTERIOR no viaja)."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("pd1-correlated", variant="succeeded")
        proc = self.run_opencode(fake)
        out = self.envelope(proc, "PD-1 correlación")

        # El argv lleva --session <id> (el id lo ELIGE el adaptador).
        call = self.packet_call(fake, "PD-1 correlación")
        argv = call["argv"]
        self.assertIn(
            "--session", argv,
            msg=f"el argv de la invocación no lleva `--session <id>` (PD-1: "
                f"correlación elegida por el adaptador): {argv!r}")
        index = argv.index("--session")
        self.assertLess(
            index + 1, len(argv),
            msg=f"`--session` sin valor en el argv (PD-1): {argv!r}")
        chosen = argv[index + 1]
        self.assertTrue(
            chosen.strip(),
            msg=f"el id pasado en --session está vacío (PD-1): {argv!r}")

        # La fila leída es la de ESE id (correlación inequívoca).
        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            [row.get("id") for row in rows], [chosen],
            msg=f"la fila durable no correlaciona con el id pasado en "
                f"--session (PD-1): elegido {chosen!r}, filas "
                f"{[row.get('id') for row in rows]!r}")
        row = rows[0]

        # La identidad de sesión declarada es la de la fila correlacionada.
        self.assertEqual(
            out["session"], chosen,
            msg=f"el envelope no declara la identidad de la fila "
                f"correlacionada (PD-1): {out['session']!r} != {chosen!r}")

        # El agente de la fila es el que la invocación declaró (--agent).
        self.assertIn(
            "--agent", argv,
            msg=f"el argv no nombra el agente destino (correlación de la "
                f"fila, PD-1): {argv!r}")
        self.assertEqual(
            row.get("agent"), argv[argv.index("--agent") + 1],
            msg=f"el agent de la fila durable no es el declarado en el "
                f"argv (correlación, PD-1): {row.get('agent')!r}")

        # El TEXTO FINAL es el del ÚLTIMO assistant (precondición del
        # fixture: assistant intermedio decoy + assistant final; PD-1).
        self.assertEqual(
            durable_last_assistant_text(fake["sessions_db"], chosen),
            FAKE_FINAL_TEXT,
            msg="fixture: el ÚLTIMO assistant del store no es el texto "
                "final acordado (precondición rota)")
        assistant_texts = []
        for message in durable_messages(fake["sessions_db"], chosen):
            if message["type"] != "assistant":
                continue
            assistant_texts.extend(
                part.get("text") for part in message["data"].get("content", [])
                if part.get("type") == "text" and part.get("text"))
        self.assertEqual(
            assistant_texts, [DECOY_FINAL_TEXT, FAKE_FINAL_TEXT],
            msg="fixture: el store no declara assistant intermedio (decoy) "
                "y assistant final (precondición rota del ÚLTIMO assistant)")

        # Terminación completed con entrega durable; el texto final (no el
        # decoy) viaja en la entrega.
        self.assertEqual(
            out["termination"], "completed",
            msg=f"la señal durable idle 'succeeded' no produjo terminación "
                f"completed (PD-1/PD-5): {out['termination']!r}")
        self.assert_durable_delivery_ref(out)
        self.assert_final_text_in_delivery()
        base = self.results_base()
        decoy_hits = [
            path for path in sorted(base.rglob("*"))
            if path.is_file()
            and DECOY_FINAL_TEXT.encode("utf-8") in path.read_bytes()]
        self.assertEqual(
            decoy_hits, [],
            msg="la entrega durable lleva el texto de un assistant "
                "INTERMEDIO (no el ÚLTIMO assistant, PD-1): "
                f"{[p.name for p in decoy_hits]!r}")

    def test_pd1_rc0_before_idle_is_not_completed(self) -> None:
        """PD-1 (verificable tercero): un cliente que retorna rc=0 ANTES de
        que la fila correlacionada quede idle NO produce `completed` — la
        terminación es `timeout` (espera acotada), sin recibo fabricado."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("pd1-rc0-early", variant="no-idle")
        proc = self.run_opencode(fake)
        out = self.envelope(proc, "PD-1 rc=0 temprano")

        # Hechos materiales del fixture: el cliente retornó rc=0, imprimió
        # el texto final por stdout, y la fila NUNCA quedó idle.
        call = self.packet_call(fake, "PD-1 rc=0 temprano")
        self.assertEqual(
            call.get("rc"), 0,
            msg="fixture: el cliente no retornó rc=0 (precondición del "
                "caso)")
        self.assertTrue(
            call.get("emitted_final_text") is True,
            msg="fixture: el texto final no fue emitido por stdout "
                "(precondición del caso)")
        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            [row.get("idle_outcome") for row in rows], [None],
            msg="fixture: la fila quedó idle (precondición rota)")

        # El rc=0 temprano NO es señal: terminación timeout, no completed.
        self.assertNotEqual(
            out["termination"], "completed",
            msg="el rc=0 del cliente produjo terminación completed (PD-1 "
                "violada: el rc NO es la señal durable)")
        self.assertEqual(
            out["termination"], "timeout",
            msg=f"el caso rc=0-sin-idle no terminó en la clase acotada "
                f"'timeout' (PD-1/PD-5): {out['termination']!r}")
        self.assert_no_receipt_fabricated("PD-1 rc=0 temprano")


# ----------------------------------------------------------------- PD-2


class TestPd2FailClosedStoreDiagnostics(AdapterCase):
    """PD-2: esquema desconocido o store ilegible → fallo CERRADO con
    diagnóstico accionable (que nombra el esquema/columna), SIN fabricar
    entrega ni recibo y SIN convertir el hecho ya conocido en un `timeout`
    por esperar de más (el UnicodeDecodeError del adaptador vigente deja de
    ser una excepción no capturada)."""

    SEED_MODE = "all"

    def test_pd2_unknown_schema_fails_closed_naming_missing_column(
            self) -> None:
        """PD-2: contra un store SQLite válido pero con esquema desconocido
        (sin la columna `idle_outcome`), el adaptador devuelve `blocked`
        con diagnóstico accionable que NOMBRA la columna; no espera de más
        (el hecho ya conocido no se degrada a timeout); sin recibo."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("pd2-unknown-schema",
                                 variant="unknown-schema")
        started = time.monotonic()
        proc = self.run_opencode(fake)
        elapsed = time.monotonic() - started

        out = self.envelope(
            proc, "PD-2 unknown-schema")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"esquema desconocido (sin idle_outcome): el adaptador no "
                f"falló cerrado en la clase 'blocked' (PD-2): "
                f"{out['termination']!r}")
        diagnosis = out.get("diagnosis")
        self.assertIsInstance(
            diagnosis, str, msg="PD-2: el diagnóstico no es texto")
        self.assertTrue(
            diagnosis.strip(),
            msg="PD-2: diagnóstico vacío (la salida legítima ante bloqueo "
                "es un diagnóstico accionable)")
        self.assertIn(
            "idle_outcome", diagnosis,
            msg=f"el diagnóstico no NOMBRA la columna faltante del esquema "
                f"(PD-2): {diagnosis!r}")
        self.assert_no_receipt_fabricated("PD-2 unknown-schema")
        # Sin esperar de más: el fallo cerrado es inmediato, no una espera
        # completa de la cota (el camino de espera acotada demora >= cota).
        self.assertLess(
            elapsed, TEST_WAIT_TIMEOUT_SECONDS,
            msg=f"el fallo cerrado esperó de más ({elapsed:.2f}s >= cota "
                f"{TEST_WAIT_TIMEOUT_SECONDS}s; PD-2: un hecho ya conocido "
                f"no se degrada a timeout)")

    def test_pd2_unreadable_store_fails_closed_without_trace(self) -> None:
        """PD-2: contra un store ILEGIBLE (bytes que no son una base
        SQLite), el adaptador devuelve `blocked` con diagnóstico accionable
        — NUNCA una excepción no capturada/traza como salida; no espera de
        más; sin recibo."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("pd2-not-sqlite", variant="not-sqlite")
        started = time.monotonic()
        proc = self.run_opencode(fake)
        elapsed = time.monotonic() - started

        out = self.envelope(
            proc, "PD-2 store no SQLite")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"store ilegible (no SQLite): el adaptador no falló "
                f"cerrado en la clase 'blocked' (PD-2; el "
                f"UnicodeDecodeError ya no es una excepción no capturada): "
                f"{out['termination']!r}")
        diagnosis = out.get("diagnosis")
        self.assertIsInstance(
            diagnosis, str, msg="PD-2: el diagnóstico no es texto")
        self.assertTrue(
            diagnosis.strip(),
            msg="PD-2: diagnóstico vacío ante un store ilegible (sin "
                "diagnóstico accionable)")
        # Nunca una traza no capturada como salida (PD-2).
        for stream_name, stream in (("stdout", proc.stdout),
                                    ("stderr", proc.stderr)):
            self.assertNotIn(
                "Traceback (most recent call last)", stream,
                msg=f"la salida {stream_name} contiene una traza no "
                    f"capturada (PD-2: fallo cerrado, nunca traza)")
        self.assert_no_receipt_fabricated("PD-2 store no SQLite")
        self.assertLess(
            elapsed, TEST_WAIT_TIMEOUT_SECONDS,
            msg=f"el fallo cerrado esperó de más ({elapsed:.2f}s >= cota "
                f"{TEST_WAIT_TIMEOUT_SECONDS}s; PD-2)")


# ----------------------------------------------------------------- PD-5


class TestPd5IdleOutcomeClassification(AdapterCase):
    """PD-5: la clasificación sale del HECHO MATERIAL de la fila
    correlacionada (`idle_outcome`), jamás del rc del cliente; `completed`
    es la ÚNICA terminación que persiste entrega por `receive` (recibo
    `pending`); las no-completadas jamás fabrican recibo.

    Orden: primero las no-completadas, la completed AL FINAL — el recibo
    persiste y contaminaría los controles negativos (mismo orden que el
    TestPd6 del oráculo 005-009)."""

    SEED_MODE = "all"

    def test_pd5_termination_from_idle_outcome_matrix(self) -> None:
        """PD-5: cada variante sale de su hecho material de fila:
        succeeded→completed (con texto final, recibo pending), failed→
        blocked, interrupted→cancelled, sin idle→timeout, rc≠0 sin fila→
        transport-error; ninguna terminación no-completada fabrica
        recibo."""
        non_completed = ("failed", "interrupted", "no-idle",
                         "transport-error")
        for variant in non_completed:
            with self.subTest(variant=variant):
                fake = self.fake_runtime(f"pd5-{variant}", variant=variant)
                proc = self.run_opencode(fake)
                out = self.envelope(proc, f"PD-5 {variant}")
                expected = VARIANT_TERMINATION[variant]
                self.assertEqual(
                    out["termination"], expected,
                    msg=f"{variant}: la terminación no ES la clase derivada "
                        f"del hecho material de la fila (PD-5): "
                        f"{out['termination']!r} != '{expected}'")
                self.assertNotEqual(
                    out["termination"], "completed",
                    msg=f"{variant}: terminación completed (un gate cerrado "
                        f"por un hecho que no lo autoriza, PD-5/INV-5)")
                self.assertTrue(
                    out.get("diagnosis"),
                    msg=f"{variant}: diagnóstico vacío (vocabulario exige "
                        f"diagnóstico accionable)")
                if variant == "transport-error":
                    call = self.packet_call(fake, f"PD-5 {variant}")
                    self.assertNotEqual(
                        call.get("rc"), 0,
                        msg="fixture: el cliente no falló en transporte "
                            "(precondición rota)")
                self.assert_no_receipt_fabricated(f"PD-5 {variant}")

        # completed: la ÚNICA terminación que persiste entrega (recibo
        # pending: entrega ≠ gate, INV-5).
        fake = self.fake_runtime("pd5-matrix-completed",
                                 variant="succeeded")
        out = self.envelope(self.run_opencode(fake), "PD-5 succeeded")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"la fila idle 'succeeded' con texto final no produjo "
                f"completed (PD-5): {out['termination']!r}")
        self.assert_durable_delivery_ref(out)
        self.assert_receipt_no_gate()
        self.assert_final_text_in_delivery()


# ----------------------------------------------------------------- PD-6


class TestPd6WorkerI8FromDurableRow(AdapterCase):
    """PD-6: el registro I8 del intento del WORKER toma `session` y
    `model_reported` de la FILA DURABLE (`session_v2.id` y
    `session_v2.model`), con `provenance` que lo declara; `runtime` sigue
    viniendo de la configuración de ejecución y `model_configured` de la
    config de delegación (A-1 de 006-003 U4/D3: el `model` de la exec-config
    dejó de ser su fuente); el esquema cerrado del registro se conserva."""

    SEED_MODE = "all"

    def test_pd6_worker_i8_session_and_model_from_durable_row(self) -> None:
        """PD-6: registro I8 del worker con esquema cerrado; `session` ==
        el id de la fila correlacionada; `model_reported` == el `model` de
        la fila (el fixture usa ROW_MODEL != FAKE_MODEL para discriminar
        la fuente por comportamiento); provenance declara la fuente de
        ambos; `runtime` de la config; `model_configured` de la config de
        delegación (A-1 de 006-003 U4/D3)."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("pd6-i8-durable", variant="succeeded")
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.run_opencode(fake)
        out = self.envelope(proc, "PD-6 I8 del worker")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"la corrida con fila durable no terminó completed "
                f"(precondición de la observación I8 del worker): "
                f"{out['termination']!r}")

        # A-1 (006-005 U1b, REEMPLAZO DECLARADO): UN SOLO registro por
        # despacho — la interfaz RELAYA el `attempt` del módulo y NO registra
        # (D-14/PD-1), así que la distinción interfaz/worker dentro de la vía
        # externa desaparece: el registro del despacho ES el del intento que
        # el sobre declara y su `session`/`model_reported` salen de la
        # observación del módulo (la fila durable). Se conservan las
        # aserciones del registro del worker y se retiran las del registro de
        # la interfaz (que ya no existe).
        record_path = self.assert_single_record_per_dispatch(
            out, records_before)
        record = json.loads(record_path.read_text(encoding="utf-8"))

        # Esquema cerrado del registro I8 conservado (PD-6).
        self.assertEqual(
            set(record), I8_RECORD_KEYS,
            msg=f"la forma del registro I8 no es la cerrada aprobada "
                f"(PD-6: el esquema se conserva): {sorted(record)}")

        # `session` desde la fila durable.
        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            len(rows), 1,
            msg="fixture: el store no tiene exactamente la fila "
                "correlacionada")
        row = rows[0]
        self.assertEqual(
            record["session"], row["id"],
            msg=f"el registro I8 del worker no toma `session` de la fila "
                f"durable (PD-6): {record['session']!r} != "
                f"{row['id']!r}")
        self.assertEqual(
            record["session"], out["session"],
            msg="el `session` del registro I8 no coincide con el del "
                "envelope (PD-6: la misma identidad correlacionada)")

        # `model_reported` desde la fila durable; el fixture usa un modelo
        # de fila DISTINTO del configurado para discriminar la fuente.
        self.assertNotEqual(
            row["model"], FAKE_MODEL,
            msg="fixture: el model de la fila debe ser distinto del "
                "model_configured (la comparación debe discriminar fuente)")
        self.assertEqual(
            record["model_reported"], row["model"],
            msg=f"el registro I8 del worker no toma `model_reported` de la "
                f"fila durable (PD-6): {record['model_reported']!r} != "
                f"{row['model']!r}")

        # Provenance declara la fuente de ambos campos (fila durable).
        provenance = record.get("provenance")
        self.assertIsInstance(
            provenance, dict, msg="provenance del registro no es un objeto")
        for field in ("session", "model_reported"):
            source = provenance.get(field)
            self.assertIsInstance(
                source, str,
                msg=f"provenance[{field!r}] no declara la fuente (PD-6: la "
                    f"provenance debe declarar que viene de la fila "
                    f"durable)")
            self.assertTrue(
                source.strip(),
                msg=f"provenance[{field!r}] vacío (PD-6)")

        # `runtime` sigue de la configuración de ejecución (PD-6;
        # conservado del oráculo 005-009).
        self.assertEqual(
            record["runtime"], FAKE_RUNTIME,
            msg=f"runtime del registro no es el de la configuración (PD-6): "
                f"{record['runtime']!r}")
        # A-1 (006-003 U4/D3): `model_configured` dejó de venir de la
        # exec-config — su única fuente es la config de delegación. Esta
        # corrida NO provisiona config de delegación, así que el valor
        # observado honesto es null (reemplazo declarado del oráculo que
        # exigía `model_configured == FAKE_MODEL`).
        self.assertIsNone(
            record["model_configured"],
            msg=f"model_configured refleja la exec-config pese a U4/D3 "
                f"(sin delegación debe ser null): "
                f"{record['model_configured']!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
