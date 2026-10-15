#!/usr/bin/env python3
"""003-002 T3 RED review-fix — hallazgos R1–R3 de review-t3.md.

Contract:
- docs/specs/003-002-artifact-tools/spec.md (P5, §8: «Las selecciones son
  roots/paths explícitos; si no puede demostrarse que cubren lo relevante,
  la equivalencia es unknown»; «descubre archivos tracked y untracked no
  ignorados»; `valid-current` exige exit 0 + conteos + snapshots before/
  after iguales + contract vigente; Limitaciones: «una selección incompleta
  o desconocida degrada a stale/unknown, no a verde»).
- docs/specs/003-002-artifact-tools/review-t3.md (dictamen: R1–R3 BLOCKING
  → review-fix del implementer).

Mapa hallazgo → test (cada test nombra su hallazgo y su postcondición P5):

- R1 (BLOCKING, bucket h) — «las selecciones declaradas en RUN.json deben
  estar ligadas a lo que argv realmente ejecuta»:
  - `test_r1a_selections_outside_argv_never_green_gate` — RUN.json con
    `discover -s tests` pero selecciones en `docs/` (Exp-A de la review) ⇒
    binding argv↔selecciones violado ⇒ `unknown`, nunca verde.
  - `test_r1b_mutation_of_executed_tree_outside_skewed_selections_caught`
    — con las mismas selecciones sesgadas (docs/), mutar el archivo test
    EJECUTADO entre corrida y validación (Exp-C) ⇒ la revalidación no es
    `valid-current` (la regla activa de §8, no sólo el campo ausente).
  - `test_r1c_source_selection_outside_executed_source_mutation_caught` —
    `test_selection=["tests"]` correcto pero `source_selection=["docs"]`
    (no cubre lo relevante: no interseca la fuente del suite) + mutación
    de `src/app.py` ⇒ no `valid-current` (§8: «si no puede demostrarse
    que cubren lo relevante, la equivalencia es unknown»).
  - `test_r1d_evidence_selections_must_match_run_request` — Exp-D:
    `evidence.source_selection`/`test_selection` reescritos (bogus/vacío)
    se comparan contra RUN.json ⇒ mismatch ⇒ nunca verde.

- R2 (BLOCKING, bucket m) — «validate-run-evidence debe RE-DERIVAR del
  log capturado»:
  - `test_r2a_tampered_counts_and_log_never_green_gate` — Exp-B:
    `tests_run 1→7` y `log` reemplazado por «LOG TAMPERED - no unittest
    output at all» ⇒ re-parseo del log con el conteo declarado ⇒ `unknown`
    / inválido, nunca `valid-current`.
  - `test_r2b_count_tamper_against_intact_log_never_green_gate` — conteos
    tamperados (tests_run 1→7) CON log intacto («Ran 1 test ... OK») ⇒
    la re-derivación exit/'Ran N tests'/failures=/skipped= del log debe
    detectar la inconsistencia (hoy se aprueba como válido: la review
    Exp-B con log reemplazado es un subconjunto de este vector).
  - `test_r2c_evidence_with_unknown_extra_key_never_green_gate` —
    conjunto cerrado de claves de evidence (RUN_EVIDENCE_KEYS en el
    contrato de la review): evidence con una clave extra desconocida no
    es evidencia canónica ⇒ nunca gate verde.

- R3 (BLOCKING, bucket m) — «descubrimiento de snapshots debe respetar
  'tracked y untracked no ignorados' de §8; usar git cuando el proyecto
  es un repo git»:
  - `test_r3a_tracked_but_ignored_file_is_scheduled_and_mutations_caught`
    — repo git del fixture: `src/notes.log` TRACKED (commiteado antes de
    la regla `*.log` de .gitignore; git no ignora archivos tracked). La
    snapshot de la selección `src/` debe incluirớ (§8: «tracked y
    untracked no ignorados» — hoy la aproximacion de patrones lo excluye
    y la mutacion es invisible ⇒ `valid-current` falso); luego (control)
    un archivo ignorado untracked (`src/cache.data` vs `*.data`) NO debe
    invalidar; y la mutación del tracked-ignorado SÍ debe invalidar.

Locks previos (argv, digests del caller, mutación, contract drift,
trampas unittest) NO se repiten aqui: cada caso negativo lleva el control
positivo interno `green_cycle()` (corrida verde con selecciones correctas
⇒ `valid-current`) del MISMO proyecto, que es por sí el lock de que el
binding nuevo no rompe el caso bueno.

Superficie observable: CLI de §2 (`run-python-unittest`,
`validate-run-evidence`), evidencia JSON por stdout y su revalidación.
Corridas del CLI con cwd en la raíz del repo;fixtures son tempdirs;
nunca se lee implementación. RED hoy: cada vector fracasa por aserción
del comportamiento ausente (los experimentos hoy terminan
`valid-current`), no por ImportError.
"""
from __future__ import annotations

import copy
import json
import subprocess
import unittest
from pathlib import Path

from tests.test_003_002_t3_run_evidence import (
    T3RunEvidenceCase,
    decode,
    parse_json_or_none,
    validate_is_current,
    walk_nodes,
)

TAMPERED_LOG = "LOG TAMPERED - no unittest output at all"
TAMPERED_COUNT = 7          # tests_run declarado por el tamper (1 real)
UNKNOWN_SELECTION = "/ABSOLUTELY/BOGUS"
EXTRA_EVIDENCE_KEY = "bogus_extra_key"

TRACKED_BUT_IGNORED = "src/notes.log"
IGNORED_UNTRACKED = "src/cache.data"


# ------------------------------------------------------- helpers de tamper


def _deep_copy(doc: dict) -> dict:
    return copy.deepcopy(doc)


def tamper_int(doc: dict, key: str, value: int) -> None:
    """Reemplaza TODO int `key` del documento (top y anidado)."""
    def walk(node: object) -> None:
        if isinstance(node, dict):
            if isinstance(node.get(key), int) and \
                    not isinstance(node.get(key), bool):
                node[key] = value
            for item in node.values():
                walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)
    walk(doc)


def tamper_str(doc: dict, key: str, value: str) -> None:
    def walk(node: object) -> None:
        if isinstance(node, dict):
            if isinstance(node.get(key), str):
                node[key] = value
            for item in node.values():
                walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)
    walk(doc)


# ------------------------------------------------------------------- suite


class T3ReviewFixCase(T3RunEvidenceCase):
    """Base review-fix: reutiliza el fixture dispatched de la batería RED."""

    # -- evidencia persistida y alterada ------------------------------------

    def save_evidence_doc(self, evidence: dict) -> Path:
        """Re-escribe la evidencia (tamper) en scratch y la liga al
        RUN.json vigente de `_last`."""
        self.run_counter += 1
        path = Path(self._tmp) / f"evidence-rf-{self.run_counter}.json"
        path.write_text(json.dumps(evidence, ensure_ascii=False,
                                   indent=2, sort_keys=True),
                        encoding="utf-8")
        evidence_path, run_request_path = self._last
        self._last = (path, run_request_path)
        return path

    def validate_tampered(self, evidence: dict) -> subprocess.CompletedProcess:
        path = self.save_evidence_doc(evidence)
        return self.validate_last()

    # -- oráculo ------------------------------------------------------------

    def must_not_be_current(self, validation: subprocess.CompletedProcess,
                            claim: str) -> None:
        self.assertFalse(
            validate_is_current(validation),
            msg=f"P5 ({claim}): la evidencia NO debe aprobarse como gate "
                "verde valid-current (§8: la selección incompleta o "
                "desconocida degrada a stale/unknown, no a verde); obtuve "
                f"rc={validation.returncode} {decode(validation.stdout)} "
                f"{decode(validation.stderr)}")

    def assert_evidence_scheduled_path(self, evidence: dict,
                                       relpath: str) -> None:
        found = False
        for node in walk_nodes(evidence.get("snapshots", {})):
            if isinstance(node, dict) and node.get("path") == relpath:
                found = True
                break
        entries = json.dumps(
            [e for e in walk_nodes(evidence.get("snapshots", {}))
             if isinstance(e, dict) and "path" in e][:8])
        self.assertTrue(
            found,
            msg="P5 (R3, §8: 'tracked y untracked no ignorados'): la "
                f"snapshot de la selección debe programar {relpath}: es un "
                "archivo TRACKED del repo git y .gitignore no excluye "
                "archivos tracked; entries observados: " + entries[:400])


# ------------------------------------------------------- R1 (bucket h)


class TestR1SelectionBinding(T3ReviewFixCase):
    """R1 — las selecciones declaradas están ligadas a lo que argv ejecuta."""

    def test_r1a_selections_outside_argv_never_green_gate(self) -> None:
        """R1/P5 (Exp-A): `discover -s tests` pero
        source_selection=test_selection=["docs"] ⇒ el binding mecánico
        argv↔selecciones falla (el árbol descubierto no está declarado) ⇒
        unknown; jamás gate verde. Control positivo: selecciones correctas
        del mismo proyecto sí aprueban."""
        self.new_dispatched_project()
        self.green_cycle()
        run_json = self.run_request_path(
            source_selection=["docs"], test_selection=["docs"])
        proc = self.run_run_python_unittest(run_json)
        self.never_gate(proc, run_json)

    def test_r1b_mutation_of_executed_tree_outside_skewed_selections_caught(
            self) -> None:
        """R1/P5 (Exp-C): con las selecciones sesgadas de Exp-A, MUTAR el
        test del árbol ejecutado entre corrida y validación. La regla
        activa de §8 exige que el binding argv↔selecciones degrada a
        unknown (o que el recálculo por lo relevado revele el drift):
        nunca `valid-current` con el snapshot pescando en docs/."""
        self.new_dispatched_project()
        self.green_cycle()
        run_json = self.run_request_path(
            source_selection=["docs"], test_selection=["docs"])
        proc = self.run_run_python_unittest(run_json)
        if proc.returncode != 0 or parse_json_or_none(proc) is None:
            return  # la corrida rechaza la condición: regla activa aplicada
        self.save_evidence(proc, run_json)
        self.clear_test_modules()
        self.write_test_module(b"""import unittest

class TestReplaced(unittest.TestCase):
    def test_replaced(self) -> None:
        self.assertTrue(True)
""")
        self.must_not_be_current(
            self.validate_last(),
            "R1 Exp-C: mutación del árbol ejecutado fuera de las "
            "selecciones sesgadas")

    def test_r1c_source_selection_outside_executed_source_mutation_caught(
            self) -> None:
        """R1/P5: test_selection correcto y source_selection fuera del
        árbol de fuente relevante (["docs"]: docs no es fuente del suite).
        La mutación de `src/app.py` (la fuente real bajo test) NO se debe
        escapar: §8 — si no puede demostrarse que las selecciones cubren
        lo relevante, la equivalencia es unknown/invalid, nunca verde."""
        self.new_dispatched_project()
        self.green_cycle()
        run_json = self.run_request_path(
            source_selection=["docs"], test_selection=["tests"])
        proc = self.run_run_python_unittest(run_json)
        if proc.returncode != 0 or parse_json_or_none(proc) is None:
            return  # rechazo upfront por binding/relevancia de source
        self.save_evidence(proc, run_json)
        self.append_to("src/app.py", b"APP_EXTRA = 'r1c mutation'\n")
        self.must_not_be_current(
            self.validate_last(),
            "R1: source_selection no relevante + mutación de la fuente "
            "real debe invalidar la evidencia")

    def test_r1d_evidence_selections_must_match_run_request(self) -> None:
        """R1/P5 (Exp-D): la evidencia canónica expone
        source_selection/test_selection; validate debe COMPARARLA contra
        RUN.json. Evidencia con selecciones reescritas (bogus + vacío) ⇒
        mismatch ⇒ nunca verde. Control: la evidencia intacta del mismo
        proyecto aprueba justo antes (green_cycle)."""
        self.new_dispatched_project()
        self.green_cycle()
        tampered = _deep_copy(self.evidence_doc)
        tampered["source_selection"] = [UNKNOWN_SELECTION]
        tampered["test_selection"] = []
        self.must_not_be_current(
            self.validate_tampered(tampered),
            "R1 Exp-D: selecciones de evidence ≠ RUN.json")


# ------------------------------------------------------- R2 (bucket m)


class TestR2LogReDerivation(T3ReviewFixCase):
    """R2 — la evidencia se RE-DERIVA del log capturado; claves cerradas."""

    def test_r2a_tampered_counts_and_log_never_green_gate(self) -> None:
        """R2/P5 (Exp-B): tests_run 1→7 y `log` reemplazado por texto
        tamperado. El re-parseo del log con el mismo parser del runner
        (exit/'Ran N tests'/'failures='/'skipped=') rinde cero tests sin
        formato unittest ⇒ inconsistencia ⇒ unknown, nunca valid-current."""
        self.new_dispatched_project()
        self.green_cycle()
        tampered = _deep_copy(self.evidence_doc)
        tamper_int(tampered, "tests_run", TAMPERED_COUNT)
        tamper_str(tampered, "log", TAMPERED_LOG)
        self.must_not_be_current(
            self.validate_tampered(tampered),
            "R2 Exp-B: counts+log tamperados")

    def test_r2b_count_tamper_against_intact_log_never_green_gate(
            self) -> None:
        """R2/P5: conteos tamperados (tests_run 1→7) con `log` INTACTO
        ('Ran 1 test ... OK'). La re-derivación debe exigir consistencia
        del log (Ran N, failures=, skipped=) con los conteos grabados:
        7 ≠ 1 ⇒ invalid/unknown, nunca verde. (Subconjunto activo de
        Exp-B: el log solo basta para falsificar el conteo.)"""
        self.new_dispatched_project()
        self.green_cycle()
        tampered = _deep_copy(self.evidence_doc)
        tamper_int(tampered, "tests_run", TAMPERED_COUNT)
        self.must_not_be_current(
            self.validate_tampered(tampered),
            "R2: conteo tamperado vs. log intacto ('Ran 1 test')")

    def test_r2c_evidence_with_unknown_extra_key_never_green_gate(
            self) -> None:
        """R2/P5: conjunto cerrado de claves de evidence: una clave extra
        desconocida demuestra que el documento NO es la evidencia canónica
        del runner ⇒ la revalidación no la aprueba como gate verde."""
        self.new_dispatched_project()
        self.green_cycle()
        tampered = _deep_copy(self.evidence_doc)
        tampered[EXTRA_EVIDENCE_KEY] = 1
        self.must_not_be_current(
            self.validate_tampered(tampered),
            "R2: evidence con clave extra fuera del conjunto cerrado")


# ------------------------------------------------------- R3 (bucket m)


class TestR3GitDiscovery(T3ReviewFixCase):
    """R3 — descubrimiento por `git ls-files` con repo git (§8)."""

    def gitify(self) -> None:
        """Convierte el fixture en repo git y deja TRACKEADO un archivo
        que MATCHA una regla de ignore posterior (git no ignora tracked):
        commit de `src/notes.log` ANTES de agregar `*.log` al .gitignore."""
        root = self.root
        notes = root / TRACKED_BUT_IGNORED
        notes.write_bytes(b"run log fixture (tracked)\n")
        self.git(
            "init", "-q", )
        self.git(
            "-c", "user.email=fixture@example.invalid",
            "-c", "user.name=fixture", "add", "-A")
        self.git(
            "-c", "user.email=fixture@example.invalid",
            "-c", "user.name=fixture", "commit", "-q", "-m", "fixture base")
        gitignore = root / ".gitignore"
        gitignore.write_text(gitignore.read_text() + "*.log\n*.data\n")
        self.git(
            "-c", "user.email=fixture@example.invalid",
            "-c", "user.name=fixture", "add", "-A")
        self.git(
            "-c", "user.email=fixture@example.invalid",
            "-c", "user.name=fixture", "commit", "-q", "-m", "ignore rules")
        tracked = self.git("ls-files", "--cached", TRACKED_BUT_IGNORED)
        self.assertIn(
            TRACKED_BUT_IGNORED, decode(tracked.stdout),
            msg="precondición (fixture): el archivo debe quedar TRACKED "
                "pese a matchar la regla *.log (git no ignora tracked)")

    def git(self, *args: str) -> subprocess.CompletedProcess:
        proc = subprocess.run(
            ["git", "-C", str(self.root), *args],
            capture_output=True)
        self.assertEqual(
            proc.returncode, 0,
            msg="precondición (fixture): `git " + " ".join(args) +
                "` con código 0; " + decode(proc.stderr)[:300])
        return proc

    def test_r3a_tracked_but_ignored_file_is_scheduled_and_mutations_caught(
            self) -> None:
        """R3/P5 (§8): 'descubre archivos tracked y untracked no
        ignorados'. En un repo git, un archivo TRACKED que matcha el
        patrón *.log (commit previo a la regla) DEBE entrar en la
        snapshot (hoy lo excluye erroneamente la aproximación de
        patrones); su mutación entre corrida y validación DEBE invalidar.
        Control previo (ambas implementaciones): un archivo ignorado
        untracked (`*.data`) NO invalida y un entry extra tampoco."""
        self.new_dispatched_project()
        self.gitify()
        self.green_cycle()
        self.assert_evidence_scheduled_path(
            self.evidence_doc, TRACKED_BUT_IGNORED)
        # Control: archivo ignorado untracked nuevo — no afecta la
        # snapshot (§8: ignore standard aplica a untracked nuevos).
        (self.root / IGNORED_UNTRACKED).write_bytes(b"ignored cache\n")
        validation = self.validate_last()
        self.assertTrue(
            validate_is_current(validation),
            msg="P5 (R3 control): un archivo ignorado untracked no entra "
                "en la snapshot (§8) y NO invalida la evidencia; obtuve "
                f"rc={validation.returncode} {decode(validation.stdout)} "
                f"{decode(validation.stderr)}")
        # Discriminador: mutación del tracked-but-ignored.
        notes = self.root / TRACKED_BUT_IGNORED
        notes.write_bytes(notes.read_bytes() + b"mutated\n")
        self.must_not_be_current(
            self.validate_last(),
            "R3: mutación de un archivo TRACKED (aunque matche *.log) "
            "debe invalidar la evidencia")


if __name__ == "__main__":
    unittest.main()
