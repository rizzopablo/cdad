#!/usr/bin/env python3
"""RED de 016-002-gap-report — 5 verificadores R-A..R-E (PC-1..PC-10).

Contrato: ``docs/specs/016-002-gap-report/spec.md`` (sha256
``315fad2c…54bc7c4b``). Decisión del test-audit §2 (5 Añadir, cero
protección existente: ningún test menciona ``gap-report``).

Selección por promesa observable (R2): un test por promesa, trazado a sus
postcondiciones numeradas — nunca cuota por postcondición. Oráculo
independiente: deriva solo del contrato y de fixtures propios
autocontenidos (estados, contratos con marcadores o con índice legacy,
registros válidos/rotos/corruptos/ausentes, colecciones CURRENT válidas o
fallidas, exclusiones válidas e inválidas). No lee implementación.

Caja negra: invoca el subcomando por ruta con ``python3``, sin importar
producto (la ruta del CLI se toma del verificador hermano 016-001,
insumo autorizado, no del producto bajo ``skills/``)::

    python3 <cdad-cycle>/scripts/cdad_contract_links.py gap-report \
      --project-root ROOT --state STATE.json \
      [--registry UNIT=REGISTRY.json ...] [--collection CURRENT.json] \
      [--exclusions EXCLUSIONS.json]

El subcomando no existe hoy: los 5 tests fallan por AssertionError de
comportamiento (el CLI devuelve 2 ante el subcomando pendiente), nunca
por ImportError.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_contract_links.py"


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, sort_keys=True, indent=2), encoding="utf-8")


def run_gap_report(*args: str) -> subprocess.CompletedProcess[str]:
    """Invoca gap-report por ruta como caja negra (nunca lo importa)."""
    return subprocess.run(
        [sys.executable, str(CLI), "gap-report", *args],
        text=True,
        capture_output=True,
        check=False,
    )


def run_validate(*args: str) -> subprocess.CompletedProcess[str]:
    """Compatibilidad de validate (PC-8): el subcomando existente no cambia."""
    return subprocess.run(
        [sys.executable, str(CLI), "validate", *args],
        text=True,
        capture_output=True,
        check=False,
    )


def make_project() -> Path:
    return Path(tempfile.mkdtemp(prefix="cdad-016-002-"))


def make_unit(root: Path, unit: str, markers: list[tuple[str, str]]) -> tuple[str, str]:
    """Contrato con marcadores reales + cierre que resuelve (spec §3).

    Devuelve (ruta relativa del spec, sha256 del spec). El cierre vive en
    ``docs/specs/<unit>/closure.md`` y su hash se usa en el estado.
    """
    spec_dir = root / "docs" / "specs" / unit
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec = spec_dir / "spec.md"
    body = "# spec-test\n"
    for pc_id, promise in markers:
        body += f"<!-- cdad:pc {pc_id} promise={promise} -->\nTexto de {pc_id}.\n"
    spec.write_text(body, encoding="utf-8")
    closure = spec_dir / "closure.md"
    closure.write_text(f"# cierre de {unit}\n", encoding="utf-8")
    return f"docs/specs/{unit}/spec.md", sha256_of(spec)


def closure_sha(root: Path, unit: str) -> str:
    return sha256_of(root / "docs" / "specs" / unit / "closure.md")


def make_state(path: Path, features: list[dict], history: list[dict] | None = None) -> None:
    write_json(path, {"epic_features": features, "epic_history": history or []})


def done_row(root: Path, unit: str, status: str = "done") -> dict:
    return {
        "id": unit,
        "status": status,
        "closure_evidence": {
            "path": f"docs/specs/{unit}/closure.md",
            "sha256": closure_sha(root, unit),
        },
    }


def make_registry(
    path: Path,
    unit: str,
    contract_rel: str,
    contract_sha: str,
    links: list[dict],
    legacy: list[dict] | None = None,
) -> None:
    obj: dict = {
        "schema_version": 1,
        "unit": unit,
        "contract": {"path": contract_rel, "sha256": contract_sha},
        "links": links,
    }
    if legacy is not None:
        obj["legacy_obligations"] = legacy
    write_json(path, obj)


def valid_link(nodeid: str, pcs: list[str] | None = None) -> dict:
    return {
        "pc_ids": pcs or ["PC-1"],
        "verifier": {"kind": "test", "nodeid": nodeid},
        "protects": "Resultado observable que comprueba el verificador.",
        "evidence": [],
        "limits": "Declarado; ejecución y pertinencia aún no acreditadas.",
    }


def review_link(doc_rel: str, doc_sha: str, locator: str, pcs: list[str]) -> dict:
    return {
        "pc_ids": pcs,
        "verifier": {
            "kind": "review",
            "reference": {"path": doc_rel, "sha256": doc_sha, "locator": locator},
            "reason": "Revisión manual del redactado; no es ejecución.",
        },
        "protects": "Revisión del redactado.",
        "evidence": [],
        "limits": "Declarado; no es ejecución de test.",
    }


def make_collection(path: Path, nodeids: list[str], exit_code: int = 0) -> None:
    write_json(
        path,
        {
            "revision": "r1",
            "command": ["pytest", "-q"],
            "scope": ["tests/test_example.py"],
            "exit_code": exit_code,
            "nodeids": nodeids,
        },
    )


def make_exclusions(path: Path, exclusions: list[dict]) -> None:
    write_json(path, {"schema_version": 1, "exclusions": exclusions})


def valid_exclusion(unit: str, contract_rel: str, contract_sha: str, promise: str) -> dict:
    return {
        "unit": unit,
        "contract": {"path": contract_rel, "sha256": contract_sha},
        "promise": promise,
        "reason": "Priorización del tramo: se revisa después (decisión recuperable).",
    }


def iter_strings(obj: object) -> list[str]:
    """Todos los valores de texto del informe (oráculos de límites, PC-10)."""
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        return [s for v in obj.values() for s in iter_strings(v)]
    if isinstance(obj, list):
        return [s for v in obj for s in iter_strings(v)]
    return []


def iter_keys(obj: object) -> list[str]:
    """Todas las claves del informe (detectar declaraciones de ejecución)."""
    found: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            found.append(k)
            found.extend(iter_keys(v))
    elif isinstance(obj, list):
        for v in obj:
            found.extend(iter_keys(v))
    return found


class GapReportRed(unittest.TestCase):
    """Cinco promesas observables de 016-002 (PC-1..PC-10)."""

    maxDiff = None

    # ------------------------------------------------------------------
    # R-A — PC-1, PC-2
    # ------------------------------------------------------------------
    def test_R_A_universo_desde_estado_y_cierre_no_registrado_vs_roto(self) -> None:
        """PC-1, PC-2: universo desde el estado; no registrado fuera, roto da 1.

        Sin este test, el usuario reincorporaría silenciosamente una unidad
        cerrada-histórica sobre una fila actual no cerrada, o confundiría
        «sin evidencia» con «evidencia rota» y aceptaría un informe
        incompleto como completo.
        """
        root = make_project()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, True))
        spec_rel, spec_sha = make_unit(root, "unit-a", [("PC-1", "A"), ("PC-2", "A")])
        nodeid = "tests/test_example.py::test_observable_promise"
        registry = root / "unit-a-links.json"
        current = root / "CURRENT.json"
        make_collection(current, [nodeid], exit_code=0)
        make_registry(registry, "unit-a", spec_rel, spec_sha, [valid_link(nodeid, ["PC-1", "PC-2"])])
        state = root / "STATE.json"
        make_state(
            state,
            [
                done_row(root, "unit-a"),
                # Fila actual no cerrada: su copia histórica no la reincorpora.
                {"id": "unit-c", "status": "in-progress"},
                # Fila done sin evidencia: cierre no registrado, fuera del universo.
                {"id": "unit-b", "status": "done"},
            ],
            [
                {
                    "epic": "epic-pasado",
                    "epic_features": [
                        {
                            "id": "unit-c",
                            "status": "done",
                            "closure_evidence": {
                                "path": "docs/specs/unit-c/closure.md",
                                "sha256": "0" * 64,
                            },
                        }
                    ],
                }
            ],
        )

        proc = run_gap_report(
            "--project-root", str(root),
            "--state", str(state),
            "--registry", f"unit-a={registry}",
            "--collection", str(current),
        )
        self.assertEqual(
            proc.returncode, 0,
            "PC-1: el informe con cierres registrados debe producirse "
            f"(rc={proc.returncode}): {proc.stderr[-1500:]}",
        )
        payload = json.loads(proc.stdout)
        universe_units = [
            u.get("unit") if isinstance(u, dict) else u
            for u in payload.get("universe", [])
        ]
        self.assertIn("unit-a", universe_units, "PC-1: unit-a pertenece al universo.")
        self.assertIn(
            "unit-b", json.dumps(payload.get("unregistered_closures", payload)),
            "PC-1: unit-b se informa como cierre no registrado.",
        )
        self.assertNotIn(
            "unit-c", universe_units,
            "PC-1: la copia histórica no reincorpora la fila actual al universo.",
        )
        ooo = payload.get("out_of_universe", [])
        ooo_flat = json.dumps(ooo)
        self.assertIn("unit-c", ooo_flat, "PC-1: unit-c queda fuera del universo con estado recuperable.")
        self.assertIn("in-progress", ooo_flat, "PC-1: se recupera el estado de unit-c.")
        self.assertTrue(
            any(
                isinstance(e, dict) and e.get("unit") == "unit-c" and e.get("status") == "in-progress"
                for e in ooo
            ),
            "PC-1: out_of_universe lista unit-c con su status in-progress.",
        )
        # Evidencia declarada pero rota: exit 1 que identifica la referencia.
        broken_state = root / "STATE-broken.json"
        bad = done_row(root, "unit-a")
        bad["closure_evidence"]["sha256"] = "0" * 64
        make_state(broken_state, [bad])
        pb = run_gap_report(
            "--project-root", str(root),
            "--state", str(broken_state),
            "--registry", f"unit-a={registry}",
            "--collection", str(current),
        )
        self.assertEqual(pb.returncode, 1, "PC-2: evidencia rota debe dar 1.")
        self.assertIn("unit-a", pb.stdout, "PC-2: el 1 identifica la referencia afectada.")
        self.assertNotIn("completo", pb.stdout.lower(), "PC-2: lo roto no se presenta como completo.")

    # ------------------------------------------------------------------
    # R-B — PC-3, PC-4
    # ------------------------------------------------------------------
    def test_R_B_obligaciones_huecos_agrupados_y_review_declarado(self) -> None:
        """PC-3, PC-4: obligaciones de marcadores o legacy sin mezclar; hueco agrupado.

        Sin este test, el usuario presentaría «not_indexed» como cubierta o
        como hueco, inventaría promesas, exigiría un test por obligación
        compartida (cuota), o confundiría un «review» con un test ejecutado.
        """
        root = make_project()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, True))
        spec_rel, spec_sha = make_unit(
            root, "unit-a", [("PC-1", "A"), ("PC-2", "A"), ("PC-3", "B")]
        )
        nodeid = "tests/test_example.py::test_shared"
        registry = root / "unit-a-links.json"
        current = root / "CURRENT.json"
        make_collection(current, [nodeid], exit_code=0)
        # PC-1 y PC-2 comparten verificador; PC-3 queda sin cubrir -> hueco de B.
        make_registry(registry, "unit-a", spec_rel, spec_sha, [valid_link(nodeid, ["PC-1", "PC-2"])])
        state = root / "STATE.json"
        make_state(state, [done_row(root, "unit-a")])

        proc = run_gap_report(
            "--project-root", str(root),
            "--state", str(state),
            "--registry", f"unit-a={registry}",
            "--collection", str(current),
        )
        self.assertEqual(
            proc.returncode, 0,
            "PC-3: el informe con huecos se produce con entradas válidas "
            f"(rc={proc.returncode}): {proc.stderr[-1500:]}",
        )
        payload = json.loads(proc.stdout)
        gaps = json.dumps(payload.get("gaps", []))
        self.assertIn("PC-3", gaps, "PC-3: el hueco nombra la obligación sin verificador.")
        self.assertIn("B", gaps, "PC-3: el hueco se agrupa bajo su promesa.")
        self.assertNotIn("PC-1", json.dumps(payload.get("gaps", [])),
                         "PC-4: compartir verificador no exige tests adicionales.")
        # Cobertura N1 (review): el mismo verificador acredita también PC-2.
        declared_ids = [
            d.get("id") if isinstance(d, dict) else d
            for d in payload.get("declared", [])
        ]
        self.assertIn("PC-1", declared_ids, "PC-4: el verificador compartido acredita PC-1.")
        self.assertIn("PC-2", declared_ids, "PC-4: el mismo verificador acredita también PC-2.")
        declared_obligations = [
            o.get("id") if isinstance(o, dict) else o
            for o in payload.get("obligations", [])
            if isinstance(o, dict) and o.get("disposition") == "declared"
        ]
        self.assertIn("PC-1", declared_obligations, "PC-4: PC-1 figura como declared en obligations.")
        self.assertIn("PC-2", declared_obligations, "PC-4: PC-2 figura como declared en obligations.")
        # review válido cuenta como declarado sin ejecutarse.
        doc = root / "doc.md"
        locator = "fragmento literal único para 016-002"
        doc.write_text(f"# doc\n\n{locator}\n", encoding="utf-8")
        reviewed = root / "unit-a-reviewed.json"
        make_registry(
            reviewed, "unit-a", spec_rel, spec_sha,
            [valid_link(nodeid, ["PC-1", "PC-2"]),
             review_link("doc.md", sha256_of(doc), locator, ["PC-3"])],
        )
        pr = run_gap_report(
            "--project-root", str(root),
            "--state", str(state),
            "--registry", f"unit-a={reviewed}",
            "--collection", str(current),
        )
        self.assertEqual(pr.returncode, 0, "PC-4: review motivado no reabre hueco.")
        self.assertNotIn("executed", json.dumps(json.loads(pr.stdout)).lower(),
                         "PC-4: el review no se presenta como ejecución.")
        # Registro presente sin obligaciones -> inválido.
        empty_reg = root / "unit-a-empty.json"
        make_registry(empty_reg, "unit-a", spec_rel, spec_sha, [])
        pe = run_gap_report(
            "--project-root", str(root),
            "--state", str(state),
            "--registry", f"unit-a={empty_reg}",
            "--collection", str(current),
        )
        self.assertEqual(pe.returncode, 1, "PC-3: registro sin obligaciones debe dar 1.")

    # ------------------------------------------------------------------
    # R-C — PC-5, PC-6
    # ------------------------------------------------------------------
    def test_R_C_exclusion_valida_aparta_e_invalida_da_1(self) -> None:
        """PC-5, PC-6: exclusión válida aparta con motivo; inválida da 1 sin ocultar.

        Sin este test, el usuario leería una promesa excluida como
        «protegida» (cobertura inflada), o colaría una exclusión con motivo
        vacío que borra huecos accionables del informe.
        """
        root = make_project()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, True))
        spec_rel, spec_sha = make_unit(
            root, "unit-a", [("PC-1", "A"), ("PC-2", "B")]
        )
        nodeid = "tests/test_example.py::test_shared"
        registry = root / "unit-a-links.json"
        current = root / "CURRENT.json"
        make_collection(current, [nodeid], exit_code=0)
        make_registry(registry, "unit-a", spec_rel, spec_sha, [valid_link(nodeid, ["PC-1"])])
        state = root / "STATE.json"
        make_state(state, [done_row(root, "unit-a")])
        exclusions = root / "EXCLUSIONS.json"
        make_exclusions(exclusions, [valid_exclusion("unit-a", spec_rel, spec_sha, "B")])

        proc = run_gap_report(
            "--project-root", str(root),
            "--state", str(state),
            "--registry", f"unit-a={registry}",
            "--collection", str(current),
            "--exclusions", str(exclusions),
        )
        self.assertEqual(
            proc.returncode, 0,
            "PC-5: la exclusión válida se procesa con el informe "
            f"(rc={proc.returncode}): {proc.stderr[-1500:]}",
        )
        payload = json.loads(proc.stdout)
        excluded = json.dumps(
            payload.get("excluded", payload.get("exclusions", [])),
            ensure_ascii=False,
        )
        self.assertIn("B", excluded, "PC-5: la promesa excluida aparece en su sección.")
        self.assertIn("Priorización", excluded, "PC-5: el motivo queda recuperable.")
        self.assertNotIn("PC-2", json.dumps(payload.get("gaps", [])),
                         "PC-5: lo excluido no se presenta como hueco accionable.")
        self.assertNotIn("PC-2", json.dumps(payload.get("declared", [])),
                         "PC-5: lo excluido no se presenta como protegido.")
        # Exclusión inválida (motivo vacío): exit 1 y el hueco persiste en gaps,
        # no en excluded (B2: el oráculo de cadena dejaba pasar la degradación).
        bad_exc = root / "EXCLUSIONS-bad.json"
        bad = valid_exclusion("unit-a", spec_rel, spec_sha, "B")
        bad["reason"] = "   "
        make_exclusions(bad_exc, [bad])
        pb = run_gap_report(
            "--project-root", str(root),
            "--state", str(state),
            "--registry", f"unit-a={registry}",
            "--collection", str(current),
            "--exclusions", str(bad_exc),
        )
        self.assertEqual(pb.returncode, 1, "PC-6: exclusión sin motivo debe dar 1.")
        bad_payload = json.loads(pb.stdout)
        bad_gap_ids = [
            g.get("id") if isinstance(g, dict) else g
            for g in bad_payload.get("gaps", [])
        ]
        self.assertIn("PC-2", bad_gap_ids, "PC-6: el 1 no suprime el hueco subyacente (PC-2 en gaps).")
        self.assertNotIn(
            "PC-2", json.dumps(bad_payload.get("excluded", [])),
            "PC-6: la exclusión inválida no aparece en excluded.",
        )
        # Exclusión DUPLICADA (B1): dos entradas idénticas no aplican ninguna;
        # PC-2 sigue en gaps y no en excluded.
        dup_exc = root / "EXCLUSIONS-dup.json"
        make_exclusions(
            dup_exc,
            [valid_exclusion("unit-a", spec_rel, spec_sha, "B"),
             valid_exclusion("unit-a", spec_rel, spec_sha, "B")],
        )
        pd = run_gap_report(
            "--project-root", str(root),
            "--state", str(state),
            "--registry", f"unit-a={registry}",
            "--collection", str(current),
            "--exclusions", str(dup_exc),
        )
        self.assertEqual(pd.returncode, 1, "PC-6: exclusión duplicada debe dar 1.")
        dup_payload = json.loads(pd.stdout)
        dup_gap_ids = [
            g.get("id") if isinstance(g, dict) else g
            for g in dup_payload.get("gaps", [])
        ]
        self.assertIn("PC-2", dup_gap_ids, "PC-6: con duplicada, PC-2 sigue en gaps.")
        self.assertNotIn(
            "PC-2", json.dumps(dup_payload.get("excluded", [])),
            "PC-6: con duplicada, ninguna entrada se aplica (PC-2 no en excluded).",
        )

    # ------------------------------------------------------------------
    # R-D — PC-7, PC-8
    # ------------------------------------------------------------------
    def test_R_D_reproducible_orden_estable_sin_efectos_y_codigos(self) -> None:
        """PC-7, PC-8: bytes reproducibles, orden estable, sin efectos, códigos 0/1/2.

        Sin este test, el usuario aceptaría informes no reproducibles (hora,
        rutas absolutas, aleatoriedad), un exit 0 que mutó fuentes o ejecutó
        tests, o una regresión silenciosa de «validate».
        """
        root = make_project()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, True))
        spec_rel, spec_sha = make_unit(root, "unit-a", [("PC-1", "A")])
        nodeid = "tests/test_example.py::test_observable_promise"
        registry = root / "unit-a-links.json"
        current = root / "CURRENT.json"
        make_collection(current, [nodeid], exit_code=0)
        make_registry(registry, "unit-a", spec_rel, spec_sha, [valid_link(nodeid, ["PC-1"])])
        state = root / "STATE.json"
        make_state(state, [done_row(root, "unit-a")])
        before = {p.name: sha256_of(p) for p in (state, registry, current)}

        args = (
            "--project-root", str(root),
            "--state", str(state),
            "--registry", f"unit-a={registry}",
            "--collection", str(current),
        )
        first = run_gap_report(*args)
        self.assertEqual(
            first.returncode, 0,
            "PC-7: el informe válido se emite con entradas identificadas "
            f"(rc={first.returncode}): {first.stderr[-1500:]}",
        )
        second = run_gap_report(*args)
        self.assertEqual(
            second.stdout, first.stdout,
            "PC-7: repetir con entradas idénticas produce salida idéntica.",
        )
        after = {p.name: sha256_of(p) for p in (state, registry, current)}
        self.assertEqual(before, after, "PC-8: producir el informe no modifica sus entradas.")
        blob = first.stdout.lower()
        self.assertNotIn("executed", blob, "PC-8: el informe no afirma ejecución.")
        # Datos rotos -> 1; uso inválido del CLI -> 2.
        corrupt = root / "STATE-corrupt.json"
        corrupt.write_text("{ no es json válido", encoding="utf-8")
        p1 = run_gap_report(
            "--project-root", str(root),
            "--state", str(corrupt),
            "--registry", f"unit-a={registry}",
            "--collection", str(current),
        )
        self.assertEqual(p1.returncode, 1, "PC-8: estado corrupto debe dar 1.")
        p2 = run_gap_report("--project-root", str(root))
        self.assertEqual(p2.returncode, 2, "PC-8: uso inválido del CLI debe dar 2.")
        # validate sigue compatible.
        pv = run_validate(
            "--project-root", str(root),
            "--registry", str(registry),
            "--collection", str(current),
        )
        self.assertEqual(pv.returncode, 0, "PC-8: validate no regresa con gap-report.")

    # ------------------------------------------------------------------
    # R-E — PC-9, PC-10
    # ------------------------------------------------------------------
    def test_R_E_sin_registros_produce_informe_con_limites(self) -> None:
        """PC-9, PC-10: sin registros hay informe sin colección, con límites.

        Sin este test, el usuario bloquearía el ciclo normal por no tener
        registros, exigiría migración (inventario vivo, backfill, gate) para
        adoptar gap-report, o leería el informe como prueba de ejecución o
        aceptación.
        """
        root = make_project()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, True))
        make_unit(root, "unit-a", [("PC-1", "A")])
        make_unit(root, "unit-b", [])
        state = root / "STATE.json"
        make_state(state, [done_row(root, "unit-a"), done_row(root, "unit-b")])

        proc = run_gap_report("--project-root", str(root), "--state", str(state))
        self.assertEqual(
            proc.returncode, 0,
            "PC-9: sin registros el informe se produce sin colección "
            f"(rc={proc.returncode}): {proc.stderr[-1500:]}",
        )
        payload = json.loads(proc.stdout)
        self.assertIn(
            "sin registro", proc.stdout.lower(),
            "PC-9: el informe declara «sin registro de vínculos declarado».",
        )
        # Cobertura N1 (review): unit-b no indexada, fuera de gaps y obligations.
        self.assertIn("unit-b", json.dumps(payload.get("not_indexed", [])),
                      "PC-9: unit-b aparece en not_indexed.")
        gap_units = [
            g.get("unit") if isinstance(g, dict) else g
            for g in payload.get("gaps", [])
        ]
        self.assertNotIn("unit-b", gap_units, "PC-9: unit-b no aparece en gaps.")
        obligation_units = [
            o.get("unit") if isinstance(o, dict) else o
            for o in payload.get("obligations", [])
        ]
        self.assertNotIn("unit-b", obligation_units, "PC-9: unit-b no aparece en obligations.")
        self.assertIn("unit-b", json.dumps(payload), "PC-9: lo no indexado se muestra.")
        self.assertIn("PC-1", json.dumps(payload), "PC-9: con marcadores hay huecos conocidos.")
        # PC-10 estructural y falsable (contrato §6, §10, PC-10): el informe
        # no declara ejecución y el bloque de límites lo dice explícitamente.
        # «no ejecuta» vive dentro del texto de límites, así que una mención
        # a ejecución, pertinencia, sensibilidad o aprobación solo vale
        # negada («no …», «sin …», «ningún …»); fuera de ese marco es una
        # afirmación y el test falla. Sin este bloque, el usuario leería el
        # informe como prueba de ejecución o aceptación.
        limits_texts = [s for s in iter_strings(payload) if "estructural" in s.lower()]
        self.assertTrue(
            limits_texts,
            "PC-10: el informe declara que la comprobación es estructural.",
        )
        limits_flat = "\n".join(limits_texts).lower()
        self.assertIn(
            "no ejecuta", limits_flat,
            "PC-10: los límites declaran que el informe no ejecuta tests.",
        )
        denials = ("no ", "sin ", "ningún", "ningun")
        for token in ("ejecut", "pertinencia", "sensibilidad", "aprob"):
            offenders = [
                s for s in iter_strings(payload)
                if token in s.lower()
                and not any(m in s.lower() for m in denials)
            ]
            self.assertEqual(
                offenders, [],
                f"PC-10: el informe no debe afirmar {token}.",
            )
        report_keys = [k.lower() for k in iter_keys(payload)]
        for forbidden in ("executed", "execution"):
            self.assertNotIn(
                forbidden, report_keys,
                f"PC-10: el informe no declara ejecución ({forbidden}).",
            )


if __name__ == "__main__":
    unittest.main()
