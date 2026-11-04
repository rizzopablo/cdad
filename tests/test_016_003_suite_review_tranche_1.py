#!/usr/bin/env python3
"""RED de 016-003-suite-review-tranche-1 — 5 verificadores R-A..R-E (PC-1..PC-10).

Contrato: ``docs/specs/016-003-suite-review-tranche-1/spec.md`` (sha256
``b3f91691e9cd44e32b60f5fa9aa98b42fffa9e363757a4ec28592622d069f9c4``).
Decisión del test-audit §2 (5 Añadir R-A..R-E, cero protección existente:
ningún test menciona ``cdad_suite_review`` / ``suite-review``).

Selección por promesa observable (R2): un test por promesa, trazado a sus
postcondiciones numeradas — nunca cuota por postcondición. Oráculo
independiente: deriva solo del contrato (§4-§7) y de fixtures propios
autocontenidos (repositorio git temporal con antigüedad controlada,
colecciones válida/fallida/duplicada, tranche sintético válido y variantes
inválidas por caso). No lee implementación.

Caja negra: invoca la herramienta nueva por ruta con ``python3``, sin
importar producto::

    python3 skills/cdad-cycle/scripts/cdad_suite_review.py select \
      --project-root ROOT --revision REV --collection COLLECTION.json
    python3 skills/cdad-cycle/scripts/cdad_suite_review.py validate \
      --project-root ROOT --tranche DIR --selection SELECTION.json

La herramienta no existe hoy: los 5 tests fallan por AssertionError de
comportamiento (el CLI pendiente no produce la selección / validación),
nunca por ImportError.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_suite_review.py"

R2_VOCABULARY = {"Mantener", "Extender", "Sustituir", "Consolidar", "Añadir", "Retirar"}


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    """Invoca la herramienta por ruta como caja negra (nunca la importa)."""
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def run_select(*args: str) -> subprocess.CompletedProcess[str]:
    return run_tool("select", *args)


def run_validate(*args: str) -> subprocess.CompletedProcess[str]:
    return run_tool("validate", *args)


def make_project() -> Path:
    return Path(tempfile.mkdtemp(prefix="cdad-016-003-"))


def git(repo: Path, *args: str, env_extra: dict | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["git", *args], cwd=str(repo), text=True, capture_output=True, env=env, check=False
    )


def init_repo(repo: Path) -> None:
    assert git(repo, "init", "-q").returncode == 0
    git(repo, "config", "user.email", "red@example.test")
    git(repo, "config", "user.name", "red")


def commit_file(repo: Path, rel: str, content: str, date: str, message: str) -> None:
    target = repo / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    git(repo, "add", rel)
    env = {"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
    proc = git(repo, "commit", "-q", "-m", message, env_extra=env)
    assert proc.returncode == 0, f"commit falló: {proc.stderr[-800:]}"


def head_rev(repo: Path) -> str:
    proc = git(repo, "rev-parse", "HEAD")
    assert proc.returncode == 0
    return proc.stdout.strip()


def make_collection(path: Path, nodeids: list[str], exit_code: int = 0,
                    revision: str = "r1") -> None:
    write_json(path, {
        "revision": revision,
        "command": ["pytest", "-q"],
        "scope": ["tests"],
        "exit_code": exit_code,
        "nodeids": nodeids,
    })


def make_selection(path: Path, nodeids: list[str], revision: str = "r1") -> None:
    write_json(path, {"revision": revision, "selection": nodeids,
                      "total": len(nodeids), "size": len(nodeids)})


def extract_selection(payload: object) -> list[str] | None:
    if isinstance(payload, dict):
        for key in ("selection", "nodeids", "tranche"):
            val = payload.get(key)
            if isinstance(val, list) and all(isinstance(v, str) for v in val):
                return list(val)
    if isinstance(payload, list) and all(isinstance(v, str) for v in payload):
        return list(payload)
    return None


def extract_rows(payload: object) -> list[dict] | None:
    if isinstance(payload, dict):
        for key in ("rows", "audit", "filas"):
            val = payload.get(key)
            if isinstance(val, list):
                return val  # type: ignore[return-value]
    if isinstance(payload, list) and all(isinstance(v, dict) for v in payload):
        return payload  # type: ignore[return-value]
    return None


def make_contract_and_doc(root: Path, unit: str = "unit-a") -> tuple[str, str, str, str]:
    """Contrato mínimo + documento de evidencia con localizador resoluble."""
    spec_dir = root / "docs" / "specs" / unit
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec = spec_dir / "spec.md"
    spec.write_text("# spec-test\n<!-- cdad:pc PC-1 promise=B -->\nTexto.\n", encoding="utf-8")
    doc = root / "doc.md"
    locator = "fragmento literal único para 016-003"
    doc.write_text(f"# doc\n\n{locator}\n", encoding="utf-8")
    return f"docs/specs/{unit}/spec.md", sha256_of(spec), "doc.md", locator


def valid_audit_row(nodeid: str, contract_rel: str, contract_sha: str,
                    doc_rel: str, doc_sha: str, locator: str) -> dict:
    return {
        "nodeid": nodeid,
        "revision": "r1",
        "contract": {"path": contract_rel, "sha256": contract_sha},
        "obligation": "PC-1",
        "promise": "B",
        "check": {
            "assertions": ["assert observable"],
            "setup": "fixture propio",
            "helpers": ["make_project"],
        },
        "consequence": "sin este test, el usuario aceptaría el tramo sin saber qué protege",
        "evidence": [{"path": doc_rel, "sha256": doc_sha, "locator": locator}],
        "references": [{"path": doc_rel, "sha256": doc_sha, "locator": locator}],
        "disposition": "Mantener",
        "motive": "protección vigente distinta",
        "uncertainties": [],
    }


def valid_costs() -> dict:
    return {
        "activities": [{
            "session": "ses-red",
            "role": "test-writer",
            "scope": "auditoría barata",
            "nodeids": ["tests/test_example.py::test_a"],
            "commands": [{"command": "pytest -q", "duration_s": 3.0,
                          "exit_code": 0, "log_ref": "logs/a.log"}],
            "tokens": {"input": 10, "output": 5, "cache": 0},
            "started": "2026-11-04T00:00:00Z",
            "ended": "2026-11-04T00:00:03Z",
            "duration_s": 3.0,
        }],
        "totals": {"elapsed_s": 3.0, "aggregated_s": 3.0, "commands_s": 3.0},
        "projection": {
            "formula": "fijo + n_tests * t_audit + n_candidatos * t_exp",
            "observed": {"t_audit": 3.0, "n_tests": 1},
            "assumptions": ["el tramo más nuevo no es muestra aleatoria del resto"],
        },
    }


def valid_decision() -> str:
    return (
        "# Decisión del tramo\n\n"
        "Decisión: continuar con cambios explícitos de método.\n\n"
        "Responsable: responsable del mantenimiento de la suite.\n"
        "Autoridad: mandato del epic 016.\n"
        "Motivo: costo calibrado y candidatos acotados.\n"
        "Evidencia: costs.json y experiments/ del tramo.\n"
        "Alcance: autoriza solo el tramo siguiente con el método declarado.\n"
    )


def valid_candidate() -> dict:
    return {
        "candidate": "tests/test_example.py::test_a",
        "hypothesis": "el candidato protege la misma promesa que la comparación",
        "promise": "B",
        "defect": "degradación contractual concreta en la copia (diff conservado)",
        "comparison": ["tests/test_example.py::test_b"],
        "justification": "incluye el verificador alternativo; excluye el propio candidato",
        "revisions": {"healthy": "r1", "degraded": "r1+diff"},
        "environment": "imagen de test declarada",
        "commands": ["pytest candidato contra sano", "pytest candidato contra degradado",
                     "pytest comparación contra degradado sin el candidato"],
        "budget": {"max_attempts": 3, "stop_condition": "tres intentos o inestabilidad"},
        "steps": {
            "sano_candidato": "pass",
            "sano_comparacion": "pass",
            "degradado_candidato": "fail: aserción contractual esperada",
            "degradado_comparacion": "pass: no detecta",
            "correspondence": "el fallo corresponde a la comprobación contractual",
        },
        "classification": "aporte diferencial demostrado",
        "evidence": ["experiments/log-candidato.txt"],
    }


def make_legacy_contract(root: Path, unit: str = "unit-legacy") -> tuple[str, str]:
    """Contrato anterior a 016-001: secciones explicitas, sin marcadores.

    No contiene el literal reservado de marcadores: la ausencia es la
    condicion que el indice legacy por demanda debe resolver.
    """
    spec_dir = root / "docs" / "specs" / unit
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec = spec_dir / "spec.md"
    spec.write_text(
        "# spec-legacy\n\n"
        "## Alcance\n\n"
        "Contrato anterior a 016-001, con secciones explicitas.\n\n"
        "## Promesas\n\n"
        "### LEGACY-1 (promesa B)\n\n"
        "Texto de la promesa B con localizador explicito: seccion LEGACY-1-B.\n\n"
        "### LEGACY-2 (promesa B)\n\n"
        "Segunda obligacion con localizador explicito: seccion LEGACY-2-B.\n",
        encoding="utf-8",
    )
    return f"docs/specs/{unit}/spec.md", sha256_of(spec)


def make_registry(path: Path, unit: str, contract_rel: str, contract_sha: str,
                  obligations: list[dict]) -> None:
    write_json(path, {
        "unit": unit,
        "contract": {"path": contract_rel, "sha256": contract_sha},
        "legacy_obligations": obligations,
    })


def legacy_obligation(ob_id: str, promise: str, locator: str) -> dict:
    return {"id": ob_id, "promise": promise, "locator": locator}


def make_valid_tranche(root: Path, dirname: str, nodeids: list[str]) -> Path:
    tranche = root / dirname
    (tranche / "experiments").mkdir(parents=True, exist_ok=True)
    contract_rel, contract_sha, doc_rel, locator = make_contract_and_doc(root)
    doc_sha = sha256_of(root / doc_rel)
    rows = [valid_audit_row(n, contract_rel, contract_sha, doc_rel, doc_sha, locator)
            for n in nodeids]
    write_json(tranche / "audit.json", {"rows": rows})
    write_json(tranche / "costs.json", valid_costs())
    (tranche / "decision.md").write_text(valid_decision(), encoding="utf-8")
    (tranche / "experiments" / "candidates.json").write_text(
        json.dumps([valid_candidate()], sort_keys=True, indent=2), encoding="utf-8")
    (tranche / "experiments" / "manifest.json").write_text(
        json.dumps({"copy": "copies/copy-1", "workspace": "workspaces/ws-1",
                    "logs": ["experiments/log-candidato.txt"]},
                   sort_keys=True, indent=2), encoding="utf-8")
    (tranche / "experiments" / "log-candidato.txt").write_text("log sano/degradado\n",
                                                               encoding="utf-8")
    return tranche


class SuiteReviewTranche1Red(unittest.TestCase):
    """Cinco promesas observables de 016-003 (PC-1..PC-10)."""

    maxDiff = None

    # ------------------------------------------------------------------
    # R-A — PC-1, PC-2
    # ------------------------------------------------------------------
    def test_R_A_seleccion_congelada_reproducible_y_diagnostico_ante_insumo_incompatible(self) -> None:
        """PC-1, PC-2: selección reproducible byte a byte; insumos rotos dan 1.

        Sin este test, el usuario aceptaría un tramo distinto del congelado
        (§4: orden por antigüedad de módulo, ``ceil(N/5)``, identidad literal
        con parámetros) o un ``0`` ante colección fallida, duplicados,
        revisión inexistente o historial superficial.
        """
        repo = make_project()
        self.addCleanup(lambda: shutil.rmtree(repo, True))
        init_repo(repo)
        # Antigüedad controlada por módulo: viejo < medio < nuevo.
        commit_file(repo, "tests/test_old.py", "def test_a(): pass\n",
                    "2020-01-01T00:00:00+00:00", "add old")
        commit_file(repo, "tests/test_mid.py", "def test_m(): pass\n",
                    "2021-01-01T00:00:00+00:00", "add mid")
        commit_file(repo, "tests/test_new.py", "def test_n(): pass\n",
                    "2022-01-01T00:00:00+00:00", "add new")
        # Renombrado que NO debe seguirse: la incorporación de la ruta nueva
        # es el commit del renombrado, no la fecha del archivo original.
        commit_file(repo, "tests/test_orig.py", "def test_o(): pass\n",
                    "2019-01-01T00:00:00+00:00", "add orig")
        git(repo, "mv", "tests/test_orig.py", "tests/test_renamed.py")
        env = {"GIT_AUTHOR_DATE": "2023-01-01T00:00:00+00:00",
               "GIT_COMMITTER_DATE": "2023-01-01T00:00:00+00:00"}
        assert git(repo, "commit", "-q", "-m", "rename", env_extra=env).returncode == 0
        rev = head_rev(repo)

        nodeids = [
            "tests/test_old.py::test_a",
            "tests/test_old.py::test_b[param-1]",
            "tests/test_mid.py::test_m",
            "tests/test_mid.py::test_m[param-x]",
            "tests/test_new.py::test_n",
            "tests/test_new.py::test_n[param-y]",
        ]
        collection = repo / "COLLECTION.json"
        make_collection(collection, nodeids, exit_code=0, revision=rev)
        before = {p.name: sha256_of(p) for p in (collection,)}
        listing_before = sorted(p.name for p in repo.iterdir())

        first = run_select("--project-root", str(repo), "--revision", rev,
                           "--collection", str(collection))
        self.assertEqual(
            first.returncode, 0,
            "PC-1: la selección válida con historial controlable debe dar 0 "
            f"(rc={first.returncode}): {first.stderr[-1500:]}",
        )
        payload = json.loads(first.stdout)
        selection = extract_selection(payload)
        self.assertIsNotNone(selection, "PC-1: el JSON debe traer la lista literal del tramo.")
        assert selection is not None
        # ceil(6/5) = 2, del módulo más nuevo, con identidad literal y orden.
        self.assertEqual(len(selection), 2, "PC-1: el tramo es ceil(N/5).")
        self.assertEqual(
            selection,
            ["tests/test_new.py::test_n", "tests/test_new.py::test_n[param-y]"],
            "PC-1: orden por (timestamp módulo desc, ruta asc, nodeid asc) "
            "con identidad literal incluidos parámetros.",
        )
        blob = json.dumps(payload).lower()
        self.assertIn(rev[:8].lower(), blob,
                      "PC-1: el resultado incluye la revisión congelada.")
        self.assertTrue(any(k in blob for k in ("incorpor", "module", "rule", "ceil")),
                        "PC-1: el resultado incluye regla e incorporaciones por módulo.")
        self.assertTrue(any(k in blob for k in ("sha256", "hash", "digest")),
                        "PC-1: el resultado incluye hashes del insumo/tramo.")
        second = run_select("--project-root", str(repo), "--revision", rev,
                            "--collection", str(collection))
        self.assertEqual(second.stdout, first.stdout,
                         "PC-1: repetir con los mismos insumos produce los mismos bytes.")
        after = {p.name: sha256_of(p) for p in (collection,)}
        self.assertEqual(before, after, "PC-1: select no escribe ni muta insumos.")
        self.assertEqual(sorted(p.name for p in repo.iterdir()), listing_before,
                         "PC-1: select no crea archivos ni ejecuta tests.")

        # Insumos incompatibles (§4): diagnóstico con 1, nunca 0.
        failed = repo / "FAILED.json"
        make_collection(failed, nodeids, exit_code=1, revision=rev)
        for name, col in (
            ("colección fallida", failed),
        ):
            proc = run_select("--project-root", str(repo), "--revision", rev,
                              "--collection", str(col))
            self.assertEqual(proc.returncode, 1, f"PC-2: {name} debe dar 1.")
            self.assertTrue(proc.stdout.strip() or proc.stderr.strip(),
                            f"PC-2: {name} debe traer diagnóstico.")
        dup = repo / "DUP.json"
        make_collection(dup, nodeids + [nodeids[0]], exit_code=0, revision=rev)
        pd = run_select("--project-root", str(repo), "--revision", rev,
                        "--collection", str(dup))
        self.assertEqual(pd.returncode, 1, "PC-2: duplicados deben dar 1.")
        self.assertIn("duplic", (pd.stdout + pd.stderr).lower(),
                      "PC-2: el 1 de duplicados debe diagnosticarlo.")
        pb = run_select("--project-root", str(repo), "--revision", "muerta000",
                        "--collection", str(collection))
        self.assertEqual(pb.returncode, 1, "PC-2: revisión inexistente debe dar 1.")
        missing_mod = repo / "MISSING-MOD.json"
        make_collection(missing_mod, ["tests/test_no_existe.py::test_z"], exit_code=0,
                        revision=rev)
        pm = run_select("--project-root", str(repo), "--revision", rev,
                        "--collection", str(missing_mod))
        self.assertEqual(pm.returncode, 1, "PC-2: módulo inexistente en la revisión debe dar 1.")
        # Historial superficial: clon --depth 1 sobre el repo.
        shallow_parent = Path(tempfile.mkdtemp(prefix="cdad-016-003-shallow-"))
        self.addCleanup(lambda: shutil.rmtree(shallow_parent, True))
        shallow = shallow_parent / "shallow"
        ps = subprocess.run(["git", "clone", "-q", "--depth", "1",
                             f"file://{repo}", str(shallow)],
                            text=True, capture_output=True)
        self.assertEqual(ps.returncode, 0, "fixture: el clon superficial debe crearse")
        shallow_col = shallow_parent / "COLLECTION-shallow.json"
        make_collection(shallow_col, nodeids, exit_code=0,
                        revision=head_rev(shallow))
        ph = run_select("--project-root", str(shallow), "--revision", head_rev(shallow),
                        "--collection", str(shallow_col))
        self.assertEqual(ph.returncode, 1, "PC-2: historial superficial debe dar 1.")
        # Uso inválido del CLI: 2.
        pu = run_tool("select", "--project-root", str(repo))
        self.assertEqual(pu.returncode, 2, "PC-2: uso inválido del CLI debe dar 2.")

    # ------------------------------------------------------------------
    # R-B — PC-3, PC-4
    # ------------------------------------------------------------------
    def test_R_B_fila_por_nodeid_con_disposicion_y_vinculo_recuperable(self) -> None:
        """PC-3, PC-4: exactamente una fila por nodeid, con vínculo que resuelve.

        Sin este test, el usuario recibiría filas de menos/más, disposiciones
        sin evidencia, o un vínculo inventado contado como protección.
        """
        root = make_project()
        self.addCleanup(lambda: shutil.rmtree(root, True))
        nodeids = ["tests/test_example.py::test_a", "tests/test_example.py::test_b[p1]"]
        selection = root / "SELECTION.json"
        make_selection(selection, nodeids)
        tranche = make_valid_tranche(root, "tranche", nodeids)

        proc = run_validate("--project-root", str(root), "--tranche", str(tranche),
                            "--selection", str(selection))
        self.assertEqual(
            proc.returncode, 0,
            "PC-3: el tramo válido con una fila por nodeid debe dar 0 "
            f"(rc={proc.returncode}): {proc.stderr[-1500:]}",
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload.get("status"), "ok",
                         "PC-3: el tramo válido declara status ok.")
        blob = json.dumps(payload).lower()
        self.assertNotIn("executed", blob, "PC-3: validate no afirma ejecución.")
        # Fila faltante.
        missing_dir = root / "tranche-missing"
        shutil.copytree(tranche, missing_dir)
        rows = json.loads((missing_dir / "audit.json").read_text(encoding="utf-8"))["rows"]
        write_json(missing_dir / "audit.json", {"rows": rows[:-1]})
        pm = run_validate("--project-root", str(root), "--tranche", str(missing_dir),
                          "--selection", str(selection))
        self.assertEqual(pm.returncode, 1, "PC-3: fila faltante debe dar 1.")
        self.assertIn(nodeids[-1], pm.stdout, "PC-3: el 1 nombra el nodeid sin fila.")
        # Fila sobrante.
        extra_dir = root / "tranche-extra"
        shutil.copytree(tranche, extra_dir)
        rows = json.loads((extra_dir / "audit.json").read_text(encoding="utf-8"))["rows"]
        contract_rel, contract_sha, doc_rel, locator = make_contract_and_doc(root)
        doc_sha = sha256_of(root / doc_rel)
        rows.append(valid_audit_row("tests/test_fuera.py::test_z", contract_rel,
                                    contract_sha, doc_rel, doc_sha, locator))
        write_json(extra_dir / "audit.json", {"rows": rows})
        pe = run_validate("--project-root", str(root), "--tranche", str(extra_dir),
                          "--selection", str(selection))
        self.assertEqual(pe.returncode, 1, "PC-3: fila sobrante debe dar 1.")
        # Vínculo inventado (locator que no existe en el documento).
        bad_dir = root / "tranche-badlink"
        shutil.copytree(tranche, bad_dir)
        rows = json.loads((bad_dir / "audit.json").read_text(encoding="utf-8"))["rows"]
        rows[0]["evidence"] = [{"path": doc_rel, "sha256": doc_sha,
                                "locator": "locator que no existe"}]
        rows[0]["references"] = rows[0]["evidence"]
        write_json(bad_dir / "audit.json", {"rows": rows})
        pb = run_validate("--project-root", str(root), "--tranche", str(bad_dir),
                          "--selection", str(selection))
        self.assertEqual(pb.returncode, 1, "PC-4: vínculo inventado debe dar 1.")
        # Disposición fuera del vocabulario R2 o ausente.
        disp_dir = root / "tranche-baddisp"
        shutil.copytree(tranche, disp_dir)
        rows = json.loads((disp_dir / "audit.json").read_text(encoding="utf-8"))["rows"]
        rows[0]["disposition"] = "Quizás"
        write_json(disp_dir / "audit.json", {"rows": rows})
        pd = run_validate("--project-root", str(root), "--tranche", str(disp_dir),
                          "--selection", str(selection))
        self.assertEqual(pd.returncode, 1, "PC-3: disposición fuera de R2 debe dar 1.")
        # Uso inválido: 2.
        pu = run_tool("validate", "--project-root", str(root))
        self.assertEqual(pu.returncode, 2, "PC-4: uso inválido del CLI debe dar 2.")

    # ------------------------------------------------------------------
    # R-C — PC-5, PC-6
    # ------------------------------------------------------------------
    def test_R_C_candidato_con_hipotesis_y_comparacion_con_resultado_acotado(self) -> None:
        """PC-5, PC-6: cada candidato trae hipótesis, defecto, comparación y pasos.

        Sin este test, el usuario leería un candidato como redundancia probada
        y podaría protección real.
        """
        root = make_project()
        self.addCleanup(lambda: shutil.rmtree(root, True))
        nodeids = ["tests/test_example.py::test_a"]
        selection = root / "SELECTION.json"
        make_selection(selection, nodeids)
        tranche = make_valid_tranche(root, "tranche", nodeids)

        proc = run_validate("--project-root", str(root), "--tranche", str(tranche),
                            "--selection", str(selection))
        self.assertEqual(
            proc.returncode, 0,
            "PC-5: el candidato con hipótesis, defecto, comparación y pasos "
            f"del §6 debe dar 0 (rc={proc.returncode}): {proc.stderr[-1500:]}",
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload.get("status"), "ok")
        blob = json.dumps(payload).lower()
        self.assertNotIn("universal", blob,
                         "PC-6: el verde acotado no se presenta como redundancia universal.")
        # Candidato sin resultados de los pasos del §6.
        nores_dir = root / "tranche-nores"
        shutil.copytree(tranche, nores_dir)
        cands = json.loads((nores_dir / "experiments" / "candidates.json")
                           .read_text(encoding="utf-8"))
        cands[0].pop("steps", None)
        cands[0].pop("classification", None)
        (nores_dir / "experiments" / "candidates.json").write_text(
            json.dumps(cands, sort_keys=True, indent=2), encoding="utf-8")
        pn = run_validate("--project-root", str(root), "--tranche", str(nores_dir),
                          "--selection", str(selection))
        self.assertEqual(pn.returncode, 1, "PC-5: candidato sin resultados debe dar 1.")
        # Afirmación de redundancia universal sin aporte diferencial.
        uni_dir = root / "tranche-uni"
        shutil.copytree(tranche, uni_dir)
        cands = json.loads((uni_dir / "experiments" / "candidates.json")
                           .read_text(encoding="utf-8"))
        cands[0]["classification"] = "redundancia universal: suprimir sin más"
        cands[0]["steps"]["degradado_comparacion"] = "fail: también detecta"
        (uni_dir / "experiments" / "candidates.json").write_text(
            json.dumps(cands, sort_keys=True, indent=2), encoding="utf-8")
        pu = run_validate("--project-root", str(root), "--tranche", str(uni_dir),
                          "--selection", str(selection))
        self.assertEqual(pu.returncode, 1,
                         "PC-6: redundancia universal sin aporte diferencial debe dar 1.")

    # ------------------------------------------------------------------
    # R-D — PC-7, PC-8
    # ------------------------------------------------------------------
    def test_R_D_costo_reconstruible_y_proyeccion_con_supuestos_mas_decision(self) -> None:
        """PC-7, PC-8: costo por actividad, proyección con supuestos y decisión.

        Sin este test, el usuario escalaría a ciegas: doble conteo de
        paralelo, métricas ausentes leídas como cero, tramo nuevo tratado
        como muestra aleatoria, o decisión pendiente que compromete el tramo
        siguiente.
        """
        root = make_project()
        self.addCleanup(lambda: shutil.rmtree(root, True))
        nodeids = ["tests/test_example.py::test_a"]
        selection = root / "SELECTION.json"
        make_selection(selection, nodeids)
        tranche = make_valid_tranche(root, "tranche", nodeids)

        proc = run_validate("--project-root", str(root), "--tranche", str(tranche),
                            "--selection", str(selection))
        self.assertEqual(
            proc.returncode, 0,
            "PC-7: el tramo con costo reconstruible y decisión explícita debe "
            f"dar 0 (rc={proc.returncode}): {proc.stderr[-1500:]}",
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload.get("status"), "ok")
        # Métricas ausentes leídas como cero.
        zero_dir = root / "tranche-zero"
        shutil.copytree(tranche, zero_dir)
        costs = json.loads((zero_dir / "costs.json").read_text(encoding="utf-8"))
        costs["activities"][0].pop("tokens", None)
        costs["projection"] = {"formula": "cero experimental",
                               "observed": {},
                               "assumptions": []}
        write_json(zero_dir / "costs.json", costs)
        pz = run_validate("--project-root", str(root), "--tranche", str(zero_dir),
                          "--selection", str(selection))
        self.assertEqual(pz.returncode, 1,
                         "PC-7: métricas ausentes no pueden leerse como cero.")
        # Decisión incompleta (sin responsable/autoridad/motivo/evidencia/alcance).
        pending_dir = root / "tranche-pending"
        shutil.copytree(tranche, pending_dir)
        (pending_dir / "decision.md").write_text(
            "# Decisión\n\nPendiente de definir.\n", encoding="utf-8")
        pd = run_validate("--project-root", str(root), "--tranche", str(pending_dir),
                          "--selection", str(selection))
        self.assertEqual(pd.returncode, 1, "PC-8: decisión incompleta debe dar 1.")
        self.assertNotIn("ok", pd.stdout.lower().split("status")[0] if "status" in pd.stdout.lower() else "",
                         "PC-8: lo pendiente no se presenta como ok.")

    # ------------------------------------------------------------------
    # R-E — PC-9, PC-10
    # ------------------------------------------------------------------
    def test_R_E_experimentos_en_copia_y_entrega_con_control_declarado(self) -> None:
        """PC-9, PC-10: experimentos confinados a copia autorizada; entrega tripartita.

        Sin este test, el usuario aceptaría un tramo cuyos experimentos
        mutaron tests/producto original, o una aceptación con pendientes que
        impiden verificar una promesa.
        """
        root = make_project()
        self.addCleanup(lambda: shutil.rmtree(root, True))
        # Producto original bajo el project-root.
        product = root / "skills" / "cdad-cycle" / "scripts" / "producto.py"
        product.parent.mkdir(parents=True, exist_ok=True)
        product.write_text("VALOR = 1\n", encoding="utf-8")
        test_file = root / "tests" / "test_example.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("def test_a(): pass\n", encoding="utf-8")
        prod_sha = sha256_of(product)
        test_sha = sha256_of(test_file)
        nodeids = ["tests/test_example.py::test_a"]
        selection = root / "SELECTION.json"
        make_selection(selection, nodeids)
        tranche = make_valid_tranche(root, "tranche", nodeids)

        proc = run_validate("--project-root", str(root), "--tranche", str(tranche),
                            "--selection", str(selection))
        self.assertEqual(
            proc.returncode, 0,
            "PC-9: el tramo con copia y workspace declarados y original "
            f"intacto debe dar 0 (rc={proc.returncode}): {proc.stderr[-1500:]}",
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload.get("status"), "ok")
        blob = json.dumps(payload).lower()
        self.assertTrue(any(k in blob for k in ("estructural", "structural")),
                        "PC-10: la entrega distingue control estructural.")
        self.assertTrue(any(k in blob for k in ("ejecu", "execut")),
                        "PC-10: la entrega distingue ejecución real.")
        self.assertTrue(any(k in blob for k in ("semántica", "semantica", "revisión",
                                                "revision", "review", "independent")),
                        "PC-10: la entrega distingue revisión semántica independiente.")
        self.assertEqual(sha256_of(product), prod_sha,
                         "PC-9: validate no modifica el producto original.")
        self.assertEqual(sha256_of(test_file), test_sha,
                         "PC-9: validate no modifica los tests originales.")
        # Cambio en el checkout original durante los experimentos.
        dirty_dir = root / "tranche-dirty"
        shutil.copytree(tranche, dirty_dir)
        product.write_text("VALOR = 2  # mutado por experimento fugado\n", encoding="utf-8")
        pd = run_validate("--project-root", str(root), "--tranche", str(dirty_dir),
                          "--selection", str(selection))
        self.assertEqual(pd.returncode, 1,
                         "PC-9: cambios en el checkout original deben dar 1.")
        product.write_text("VALOR = 1\n", encoding="utf-8")
        # Copia/workspace sin declarar.
        nocopy_dir = root / "tranche-nocopy"
        shutil.copytree(tranche, nocopy_dir)
        (nocopy_dir / "experiments" / "manifest.json").write_text(
            json.dumps({}, sort_keys=True, indent=2), encoding="utf-8")
        pn = run_validate("--project-root", str(root), "--tranche", str(nocopy_dir),
                          "--selection", str(selection))
        self.assertEqual(pn.returncode, 1,
                         "PC-9: copia y workspace sin declarar deben dar 1.")

    # ------------------------------------------------------------------
    # R-F — PC-3, PC-4 (RED-002: contratos sin marcadores via indice legacy)
    # ------------------------------------------------------------------
    def test_R_F_contrato_sin_marcadores_resuelve_por_indice_legacy(self) -> None:
        """PC-3, PC-4: fila de contrato sin marcadores resuelve por registro.

        Sin este test, el usuario veria rechazada toda fila legitima de los
        35 modulos del tramo congelado cuyos contratos son anteriores a
        016-001 (sin marcadores): el validador exige que la obligacion
        resuelva solo contra marcadores reales y responde «obligacion ... no
        resuelve», aunque exista un registro enlazado cuyo ``contract.path``
        y ``sha256`` coinciden con los de la fila y cuya entrada
        ``legacy_obligations`` trae la obligacion con la misma promesa.
        """
        root = make_project()
        self.addCleanup(lambda: shutil.rmtree(root, True))
        node_legacy = "tests/test_legacy.py::test_legacy"
        selection = root / "SELECTION.json"
        make_selection(selection, [node_legacy])
        tranche = make_valid_tranche(root, "tranche", [node_legacy])
        # RED-003: make_valid_tranche deja costs.json y candidates.json con
        # tests/test_example.py::test_a; el camino feliz legacy debe
        # referenciar node_legacy para que actividad ∈ selección∪comparaciones
        # y candidato ∈ selección, sin debilitar el resto de aserciones.
        costs_path = tranche / "costs.json"
        costs = json.loads(costs_path.read_text(encoding="utf-8"))
        costs["activities"][0]["nodeids"] = [node_legacy]
        write_json(costs_path, costs)
        cands_path = tranche / "experiments" / "candidates.json"
        cands = json.loads(cands_path.read_text(encoding="utf-8"))
        cands[0]["candidate"] = node_legacy
        cands_path.write_text(
            json.dumps(cands, sort_keys=True, indent=2) + "\n", encoding="utf-8")

        legacy_rel, legacy_sha = make_legacy_contract(root)
        self.assertNotIn("cdad:pc", Path(root / legacy_rel).read_text(encoding="utf-8"),
                         "fixture: el contrato legacy no debe traer marcadores.")
        marker_rel = "docs/specs/unit-a/spec.md"
        marker_sha = sha256_of(root / marker_rel)

        rows = json.loads((tranche / "audit.json").read_text(encoding="utf-8"))["rows"]
        rows[0]["contract"] = {"path": legacy_rel, "sha256": legacy_sha}
        rows[0]["obligation"] = "LEGACY-1"
        rows[0]["promise"] = "B"
        write_json(tranche / "audit.json", {"rows": rows})

        registry_ok = root / "registry-ok.json"
        make_registry(registry_ok, "unit-legacy", legacy_rel, legacy_sha,
                      [legacy_obligation("LEGACY-1", "B", "seccion LEGACY-1-B"),
                       legacy_obligation("LEGACY-2", "B", "seccion LEGACY-2-B")])

        # Camino feliz: contrato sin marcadores + registro enlazado cuyo
        # path y sha coinciden -> la obligacion resuelve en el indice y la
        # promesa coincide -> status ok.
        proc = run_validate("--project-root", str(root), "--tranche", str(tranche),
                            "--selection", str(selection),
                            "--registry", str(registry_ok))
        self.assertEqual(
            proc.returncode, 0,
            "PC-4: la fila legacy con registro enlazado (path+sha coincidentes, "
            "promesa igual a la del indice) debe dar 0 "
            f"(rc={proc.returncode}): {(proc.stdout + proc.stderr)[-1500:]}",
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload.get("status"), "ok",
                         "PC-4: el tramo legacy valido declara status ok.")

        # Compatibilidad: sin --registry, el contrato CON marcadores sigue en 0.
        marker_node = "tests/test_example.py::test_a"
        marker_selection = root / "SELECTION-marker.json"
        make_selection(marker_selection, [marker_node])
        marker_tranche = make_valid_tranche(root, "tranche-marker", [marker_node])
        pm = run_validate("--project-root", str(root), "--tranche", str(marker_tranche),
                          "--selection", str(marker_selection))
        self.assertEqual(pm.returncode, 0,
                         "PC-4: sin --registry, el contrato con marcadores no cambia.")

        def expect_reject(name: str, tranche_dir: Path,
                          registries: list[Path] | None) -> None:
            args = ["--project-root", str(root), "--tranche", str(tranche_dir),
                    "--selection", str(selection)]
            for reg in registries or []:
                args += ["--registry", str(reg)]
            pr = run_validate(*args)
            self.assertEqual(pr.returncode, 1, f"PC-4: {name} debe dar 1.")
            self.assertIn(node_legacy, pr.stdout + pr.stderr,
                          f"PC-4: {name} debe nombrar la fila.")

        # Obligacion inexistente en el indice.
        miss_dir = root / "tranche-miss"
        shutil.copytree(tranche, miss_dir)
        rows = json.loads((miss_dir / "audit.json").read_text(encoding="utf-8"))["rows"]
        rows[0]["obligation"] = "LEGACY-9"
        write_json(miss_dir / "audit.json", {"rows": rows})
        expect_reject("obligacion inexistente en el indice", miss_dir, [registry_ok])

        # Promesa de la fila distinta de la del indice.
        prom_dir = root / "tranche-prom"
        shutil.copytree(tranche, prom_dir)
        rows = json.loads((prom_dir / "audit.json").read_text(encoding="utf-8"))["rows"]
        rows[0]["promise"] = "C"
        write_json(prom_dir / "audit.json", {"rows": rows})
        expect_reject("promesa distinta de la del indice", prom_dir, [registry_ok])

        # Registro con hash de contrato distinto del declarado en la fila.
        registry_badr = root / "registry-badhash.json"
        make_registry(registry_badr, "unit-legacy", legacy_rel, "0" * 64,
                      [legacy_obligation("LEGACY-1", "B", "seccion LEGACY-1-B")])
        expect_reject("hash de contrato distinto en el registro", tranche, [registry_badr])

        # Fila de contrato sin marcadores sin ningun registro enlazado.
        expect_reject("fila legacy sin registro enlazado", tranche, None)

        # Registro corrupto.
        registry_corrupt = root / "registry-corrupt.json"
        registry_corrupt.write_text("{no json valido", encoding="utf-8")
        expect_reject("registro corrupto", tranche, [registry_corrupt])

        # Registro que mezcla legacy_obligations con un contrato CON marcadores.
        registry_mixed = root / "registry-mixed.json"
        make_registry(registry_mixed, "unit-a", marker_rel, marker_sha,
                      [legacy_obligation("LEGACY-1", "B", "seccion LEGACY-1-B")])
        mixed_dir = root / "tranche-mixed"
        shutil.copytree(marker_tranche, mixed_dir)
        mixed_selection = root / "SELECTION-mixed.json"
        make_selection(mixed_selection, [marker_node])
        args = ["--project-root", str(root), "--tranche", str(mixed_dir),
                "--selection", str(mixed_selection),
                "--registry", str(registry_mixed)]
        px = run_validate(*args)
        self.assertEqual(px.returncode, 1,
                         "PC-4: mezclar legacy_obligations con contrato con "
                         "marcadores debe dar 1.")
        self.assertIn(marker_node, px.stdout + px.stderr,
                      "PC-4: la mezcla debe nombrar la fila.")


if __name__ == "__main__":
    unittest.main()
