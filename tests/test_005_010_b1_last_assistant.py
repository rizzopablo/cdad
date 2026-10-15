#!/usr/bin/env python3
"""005-010 RED B1 — el texto final es SOLO el del ÚLTIMO assistant.

Contract: docs/specs/005-010-real-opencode-delegation/spec.md (PD-1, PD-5;
INV-5) + review-codex-2026-10-11.md (hallazgo B1, corrección requerida
antes del despliegue). Misma superficie observable del oráculo T2
(proyecto sintético en tempdir, doble SQLite real chico como señal
durable, binario falso como frontera de proceso: NINGUNA lectura de
implementación, ningún runtime vivo — PD-7; jamás el binario real).

Hallazgo B1 (dictamen: corrección requerida): el texto final vive en el
ÚLTIMO mensaje `assistant` (PD-1). Un texto INTERMEDIO de un assistant
anterior no puede sustituir una entrega final ausente (PD-5: succeeded
sin texto EN ese último mensaje → `blocked` con diagnóstico, sin entrega
ni recibo). El helper del oráculo `durable_last_assistant_text` se
alineó en la fixture (tests/test_005_009_t2_opencode_adapter.py) para
tomar SOLO el último assistant (concatenación de sus partes textuales),
sin debilitar las precondiciones vigentes.

Variantes NUEVAS del doble (fixture; NINGUNA variante previa cambia de
conducta):

  - `b1-last-assistant-reasoning-only`: assistant seq=2 con texto
    intermedio ('Voy a analizar el contrato; todavía no tengo el
    resultado.') + assistant seq=3 (último) SOLO con una parte de
    razonamiento (sin parte `type: text`) + fila correlacionada
    `idle_outcome=succeeded` → `blocked`, sin entrega ni recibo nuevo;
    el texto intermedio no aparece en ninguna entrega.
  - `b1-last-assistant-multi-text`: decoy + ÚLTIMO assistant con DOS
    partes textuales → `completed` y la entrega es la CONCATENACIÓN de
    las partes de ESE mensaje solamente (sin texto de mensajes
    anteriores). REGRESIÓN del caso normal.

Mapa test → postcondición (spec 005-010) y hallazgo:

  1  TestB1LastAssistantOnly::test_b1_intermediate_text_does_not_substitute_missing_final_text
       PD-1 + PD-5 (B1) — texto intermedio + último assistant sin parte
       textual + succeeded → blocked, sin entrega ni recibo nuevo; el
       texto intermedio no aparece en ninguna entrega; sin esperar de
       más (el hecho ya conocido no se degrada a timeout).
  2  TestB1LastAssistantOnly::test_b1_multi_text_last_assistant_delivery_is_that_message_concatenation_only
       PD-1 (B1 regresión) — último assistant con varias partes
       textuales → completed; la entrega contiene las partes de ESE
       mensaje y NO el texto de mensajes anteriores.

RED esperado (estado vigente post-cierre 005-010, según review B1):
  (1) falla por COMPORTAMIENTO: el vigente devuelve el texto intermedio
      (búsqueda descendente del primero con texto) → `completed` con
      entrega del avance, en vez de `blocked` sin entrega;
  (2) estado observado (regresión del caso normal): se reporta.
Cada fallo RED debe ser AssertionError sobre el COMPORTAMIENTO ausente
(terminación/entrega/recibo), no import/sintaxis.
"""

from __future__ import annotations

import time
import unittest

from test_005_009_t2_opencode_adapter import (
    B1_FINAL_PART1,
    B1_FINAL_PART2,
    B1_INTERMEDIATE_TEXT,
    B1_REASONING_TEXT,
    DECOY_FINAL_TEXT,
    TEST_WAIT_TIMEOUT_SECONDS,
    AdapterCase,
    durable_last_assistant_text,
    durable_messages,
    durable_session_rows,
)


def assert_diag_actionable(case: unittest.TestCase, out: dict,
                           label: str) -> str:
    """Salida legítima ante bloqueo: diagnóstico accionable no vacío
    (vocabulario de la spec §2)."""
    diagnosis = out.get("diagnosis")
    case.assertIsInstance(
        diagnosis, str, msg=f"{label}: el diagnóstico no es texto")
    case.assertTrue(
        diagnosis.strip(),
        msg=f"{label}: diagnóstico vacío (la salida legítima ante bloqueo "
            f"exige un diagnóstico accionable)")
    return diagnosis


class TestB1LastAssistantOnly(AdapterCase):
    """B1 (review-codex-2026-10-11, corrección requerida): el ÚLTIMO
    mensaje `assistant` de la sesión correlacionada es la ÚNICA fuente del
    texto final (PD-1); `succeeded` sin texto EN ESE mensaje → `blocked`
    con diagnóstico, sin entrega ni recibo nuevo (PD-5)."""

    def _text_hits_in_results(self, text: str) -> list:
        """Archivos de la entrega durable (árbol canónico results) que
        contienen `text` (bytes UTF-8)."""
        base = self.results_base()
        return [
            path for path in sorted(base.rglob("*"))
            if path.is_file() and text.encode("utf-8") in path.read_bytes()]

    def test_b1_intermediate_text_does_not_substitute_missing_final_text(self) -> None:
        """B1 (PD-1 + PD-5): assistant seq=2 con TEXTO INTERMEDIO ('Voy a
        analizar...') + assistant seq=3 (último) SOLO con una parte de
        razonamiento (sin parte `type: text`) + fila correlacionada
        `idle_outcome=succeeded` → terminación `blocked` con diagnóstico
        accionable (NUNCA `completed` con el avance), sin entrega
        declarada, sin recibo nuevo; el texto intermedio (y el texto de
        la parte de razonamiento) no aparece en ninguna entrega; y sin
        esperar de más (el hecho ya conocido no se degrada a timeout)."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime(
            "b1-reasoning-only", variant="b1-last-assistant-reasoning-only")
        started = time.monotonic()
        proc = self.run_opencode(fake)
        elapsed = time.monotonic() - started
        out = self.envelope(proc, "B1 último assistant sin parte textual")

        # Precondición del fixture: fila idle 'succeeded'; el ÚLTIMO
        # assistant NO tiene parte textual; SÍ existe texto intermedio en
        # un assistant ANTERIOR (hecho material B1).
        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            [row.get("idle_outcome") for row in rows], ["succeeded"],
            msg="fixture: la fila no está idle 'succeeded' (precondición "
                "B1 rota)")
        session_id = rows[0]["id"]
        assistants = [
            message for message
            in durable_messages(fake["sessions_db"], session_id)
            if message["type"] == "assistant"]
        self.assertEqual(
            len(assistants), 2,
            msg="fixture: la sesión no tiene DOS mensajes assistant "
                "(intermedio con texto + último sin parte textual; "
                "precondición B1 rota)")
        self.assertIsNone(
            durable_last_assistant_text(fake["sessions_db"], session_id),
            msg="fixture: el ÚLTIMO assistant SÍ tiene parte textual "
                "(precondición B1 'sin texto final' rota)")
        intermediate_in_store = [
            part.get("text") for part
            in assistants[0]["data"].get("content", [])
            if part.get("type") == "text" and part.get("text")]
        self.assertEqual(
            intermediate_in_store, [B1_INTERMEDIATE_TEXT],
            msg="fixture: el assistant INTERMEDIO no lleva el texto "
                "intermedio (precondición B1 rota)")

        # El contrato: blocked, sin entrega ni recibo nuevo (PD-1/PD-5).
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"B1: un texto INTERMEDIO de un assistant anterior "
                f"sustituyó la entrega final ausente (PD-1: el texto "
                f"final es el del ÚLTIMO assistant; PD-5: succeeded sin "
                f"texto en ESE mensaje → blocked): termination "
                f"{out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")
        assert_diag_actionable(self, out, "B1 sin texto final")
        self.assertFalse(
            out.get("delivery_ref"),
            msg=f"B1: se declaró entrega sin texto final del ÚLTIMO "
                f"assistant (PD-5): {out.get('delivery_ref')!r}")
        self.assert_no_receipt_fabricated("B1 sin texto final")

        # El texto intermedio NO aparece en ninguna entrega durable
        # (PD-1: la entrega no lleva texto de assistants anteriores).
        self.assertEqual(
            self._text_hits_in_results(B1_INTERMEDIATE_TEXT), [],
            msg="la entrega durable lleva el TEXTO INTERMEDIO de un "
                "assistant ANTERIOR (B1/PD-1: el texto final es el del "
                "ÚLTIMO assistant, no el de un mensaje previo)")
        # Ni el texto de la parte de razonamiento (no es parte textual).
        self.assertEqual(
            self._text_hits_in_results(B1_REASONING_TEXT), [],
            msg="la entrega durable lleva el texto de una parte de "
                "razonamiento (no es parte `type: text`, PD-1)")

        # Sin esperar de más: el hecho ya conocido no se degrada a timeout.
        self.assertLess(
            elapsed, TEST_WAIT_TIMEOUT_SECONDS,
            msg=f"la rama 'succeeded sin texto en el ÚLTIMO assistant' "
                f"esperó de más ({elapsed:.2f}s >= cota; PD-5: el hecho "
                f"ya conocido no se degrada a timeout)")

    def test_b1_multi_text_last_assistant_delivery_is_that_message_concatenation_only(self) -> None:
        """B1 REGRESIÓN (PD-1): con el ÚLTIMO assistant llevando VARIAS
        partes textuales, la terminación es `completed` y la entrega es la
        CONCATENACIÓN de las partes de ESE mensaje solamente — contiene
        ambas partes y NO el texto de mensajes assistant anteriores."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime(
            "b1-multi-text", variant="b1-last-assistant-multi-text")
        proc = self.run_opencode(fake)
        out = self.envelope(proc, "B1 regresión varias partes textuales")

        # Precondición del fixture: fila idle 'succeeded'; el ÚLTIMO
        # assistant lleva DOS partes textuales; un assistant ANTERIOR
        # lleva el decoy.
        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            [row.get("idle_outcome") for row in rows], ["succeeded"],
            msg="fixture: la fila no está idle 'succeeded' (precondición "
                "B1 regresión rota)")
        session_id = rows[0]["id"]
        assistants = [
            message for message
            in durable_messages(fake["sessions_db"], session_id)
            if message["type"] == "assistant"]
        self.assertEqual(
            len(assistants), 2,
            msg="fixture: la sesión no tiene DOS mensajes assistant "
                "(decoy + último con varias partes; precondición rota)")
        last_parts = [
            part.get("text") for part
            in assistants[-1]["data"].get("content", [])
            if part.get("type") == "text" and part.get("text")]
        self.assertEqual(
            last_parts, [B1_FINAL_PART1, B1_FINAL_PART2],
            msg="fixture: el ÚLTIMO assistant no lleva las DOS partes "
                "textuales (precondición B1 regresión rota)")
        self.assertEqual(
            durable_last_assistant_text(fake["sessions_db"], session_id),
            B1_FINAL_PART1 + "\n" + B1_FINAL_PART2,
            msg="fixture: el oráculo alineado no concatena las partes "
                "textuales del ÚLTIMO assistant (B1)")

        # Regresión del caso normal: completed con entrega durable.
        self.assertEqual(
            out["termination"], "completed",
            msg=f"B1 regresión: el ÚLTIMO assistant con varias partes "
                f"textuales no produjo completed: "
                f"{out['termination']!r}")
        self.assert_durable_delivery_ref(out)
        self.assert_receipt_no_gate()

        # La entrega es la CONCATENACIÓN de las partes de ESE mensaje:
        # contiene ambas partes...
        for part in (B1_FINAL_PART1, B1_FINAL_PART2):
            self.assertTrue(
                self._text_hits_in_results(part),
                msg=f"la entrega durable no contiene la parte textual del "
                    f"ÚLTIMO assistant (PD-1: concatenación de las partes "
                    f"de ESE mensaje): {part!r}")
        # ...y NO el texto de mensajes assistant anteriores.
        self.assertEqual(
            self._text_hits_in_results(DECOY_FINAL_TEXT), [],
            msg="la entrega durable lleva el texto de un assistant "
                "ANTERIOR (PD-1: SOLO las partes del ÚLTIMO mensaje)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
