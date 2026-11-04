#!/usr/bin/env python3
"""RED de 016-001-contract-test-link — 10 verificadores R-A1..R-D2 + R-B3..R-B6.

Contrato: ``docs/specs/016-001-contract-test-link/spec.md`` (sha256
``88b144e5…eca688e``). Decisión §4 de ``test-audit.md`` (12 Mantener, 6 Añadir)
más RED-004 (review: B1 backtick suelto, B2 modo/obligaciones, O1 duplicados).

Selección por promesa observable (R2): un test por promesa, trazado a sus
postcondiciones numeradas — nunca cuota por postcondición. Ningún verificador
existente protege PC-1..PC-8 (AUDIT §1: cero coincidencias de
``contract-test-link`` / ``cdad:pc`` en ``tests/``).

Oráculo independiente: deriva solo del contrato y de fixtures propios
(contrato nuevo mínimo con marcadores ``cdad:pc``, contrato antiguo con
``legacy_obligations``, registros válido/roto/corrupto/ausente, colecciones
CURRENT/BASE con exit 0 y fallida). No lee implementación.

Caja negra: invoca el módulo por ruta con ``python3``, sin importar producto::

    python3 <cdad-cycle>/scripts/cdad_contract_links.py validate \
      --project-root ROOT --registry REGISTRY --collection CURRENT.json \
      [--baseline BASE.json]

El CLI no existe hoy: los 6 tests fallan por AssertionError de comportamiento
(pendiente no implementado), no por ImportError.
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


def run_validate(*args: str) -> subprocess.CompletedProcess[str]:
    """Invoca el validador por ruta como caja negra (nunca lo importa)."""
    return subprocess.run(
        [sys.executable, str(CLI), "validate", *args],
        text=True,
        capture_output=True,
        check=False,
    )


def make_project() -> Path:
    root = Path(tempfile.mkdtemp(prefix="cdad-016-001-"))
    return root


def make_contract_new(root: Path) -> tuple[Path, str]:
    """Contrato nuevo mínimo con marcadores estables cdad:pc (spec §2)."""
    contract = root / "contract.md"
    contract.write_text(
        "# spec-test\n"
        "<!-- cdad:pc PC-1 promise=entrega -->\n"
        "La entrega recupera el vínculo.\n"
        "<!-- cdad:pc PC-2 promise=entrega -->\n"
        "La entrega identifica la rotura.\n"
        "<!-- cdad:pc PC-3 promise=huecos -->\n"
        "Los huecos se agrupan por promesa.\n",
        encoding="utf-8",
    )
    return contract, sha256_of(contract)


def make_doc_ref(root: Path, name: str = "doc.md") -> tuple[Path, str, str]:
    doc = root / name
    locator = "fragmento literal único para 016-001"
    doc.write_text(f"# doc\n\n{locator}\n", encoding="utf-8")
    return doc, sha256_of(doc), locator


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


def make_registry(
    path: Path,
    contract_rel: str,
    contract_sha: str,
    links: list[dict],
    legacy: list[dict] | None = None,
) -> None:
    obj: dict = {
        "schema_version": 1,
        "unit": "example-unit",
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


class ContractTestLinkRed(unittest.TestCase):
    """Seis promesas observables de 016-001 (PC-1..PC-8)."""

    maxDiff = None

    # ------------------------------------------------------------------
    # R-A1 — PC-1, PC-2
    # ------------------------------------------------------------------
    def test_R_A1_enlace_recuperable_y_roturas_identificadas(self) -> None:
        """PC-1, PC-2: vínculo recuperable; cada rotura se identifica con exit 1.

        Sin este test, el usuario creería un vínculo que no resuelve o
        recibiría un ``1`` sin saber qué vínculo falló (contrato, obligación,
        referencia documental, nodeid o colección fallida).
        """
        root = make_project()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, True))
        contract, sha = make_contract_new(root)
        doc, doc_sha, locator = make_doc_ref(root)
        nodeid = "tests/test_example.py::test_observable_promise"
        registry = root / "contract-test-links.json"
        current = root / "CURRENT.json"
        make_collection(current, [nodeid], exit_code=0)
        contract_rel = contract.name
        doc_rel = doc.name
        make_registry(
            registry,
            contract_rel,
            sha,
            [
                {
                    "pc_ids": ["PC-1", "PC-2"],
                    "verifier": {"kind": "test", "nodeid": nodeid},
                    "protects": "La entrega recupera el vínculo.",
                    "evidence": [
                        {"path": doc_rel, "sha256": doc_sha, "locator": locator}
                    ],
                    "limits": "Declarado; ejecución y pertinencia aún no acreditadas.",
                },
                {
                    # PC-3 (huecos) no es la promesa de R-A1, pero el universo
                    # mecánico del contrato fixture la exige: sin este
                    # verificador el 0 esperado contradice PC-3 y R-B1.
                    "pc_ids": ["PC-3"],
                    "verifier": {
                        "kind": "review",
                        "reference": {
                            "path": doc_rel,
                            "sha256": doc_sha,
                            "locator": locator,
                        },
                        "reason": "Revisión manual del redactado de huecos; reutiliza PC-4 sin exigir tests de más.",
                    },
                    "protects": "Revisión del redactado de huecos (cobertura mecánica del fixture).",
                    "evidence": [],
                    "limits": "Declarado; no es ejecución de test.",
                },
            ],
        )

        proc = run_validate(
            "--project-root", str(root),
            "--registry", str(registry),
            "--collection", str(current),
        )
        self.assertEqual(
            proc.returncode, 0,
            "PC-1: el CLI pendiente no valida el registro válido "
            f"(rc={proc.returncode}): {proc.stderr[-1500:]}",
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(
            payload.get("status"), "ok",
            "PC-1: el resultado válido no declara status ok.",
        )
        # Cinco roturas, cada una con exit 1 e identificación del afectado.
        # 1) hash distinto del contrato.
        bad_hash = root / "registry-bad-hash.json"
        make_registry(bad_hash, contract_rel, "0" * 64, [valid_link(nodeid)])
        p1 = run_validate(
            "--project-root", str(root),
            "--registry", str(bad_hash),
            "--collection", str(current),
        )
        self.assertEqual(p1.returncode, 1, "PC-2: hash distinto debe dar 1.")
        self.assertIn("PC-1", p1.stdout, "PC-2: el 1 no identifica el vínculo.")
        # 2) pc_ids inexistente.
        bad_pc = root / "registry-bad-pc.json"
        make_registry(bad_pc, contract_rel, sha, [valid_link(nodeid, ["PC-99"])])
        p2 = run_validate(
            "--project-root", str(root),
            "--registry", str(bad_pc),
            "--collection", str(current),
        )
        self.assertEqual(p2.returncode, 1, "PC-2: obligación inexistente debe dar 1.")
        self.assertIn("PC-99", p2.stdout, "PC-2: el 1 no identifica la obligación.")
        # 3) referencia documental irresoluble (locator que no existe).
        bad_ref = root / "registry-bad-ref.json"
        link = valid_link(nodeid)
        link["evidence"] = [
            {"path": doc_rel, "sha256": doc_sha, "locator": "locator que no existe"}
        ]
        make_registry(bad_ref, contract_rel, sha, [link])
        p3 = run_validate(
            "--project-root", str(root),
            "--registry", str(bad_ref),
            "--collection", str(current),
        )
        self.assertEqual(p3.returncode, 1, "PC-2: referencia rota debe dar 1.")
        # 4) nodeid vinculado ausente de la colección.
        empty_col = root / "EMPTY.json"
        make_collection(empty_col, [], exit_code=0)
        p4 = run_validate(
            "--project-root", str(root),
            "--registry", str(registry),
            "--collection", str(empty_col),
        )
        self.assertEqual(p4.returncode, 1, "PC-2: nodeid ausente debe dar 1.")
        self.assertIn(nodeid, p4.stdout, "PC-2: el 1 no identifica el nodeid.")
        # 5) colección fallida no obtiene verde.
        failed_col = root / "FAILED.json"
        make_collection(failed_col, [nodeid], exit_code=1)
        p5 = run_validate(
            "--project-root", str(root),
            "--registry", str(registry),
            "--collection", str(failed_col),
        )
        self.assertEqual(p5.returncode, 1, "PC-2: colección fallida debe dar 1.")

    # ------------------------------------------------------------------
    # R-B1 — PC-3, PC-4
    # ------------------------------------------------------------------
    def test_R_B1_huecos_agrupados_y_reutilizacion_sin_cuota(self) -> None:
        """PC-3, PC-4: huecos agrupados por promesa; compartir test no exige más.

        Sin este test, el usuario no vería promesas sin verificador, o se le
        exigirían tests de más; un ``kind:review`` sin motivo pasaría como
        ejecución de test.
        """
        root = make_project()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, True))
        contract, sha = make_contract_new(root)
        doc, doc_sha, locator = make_doc_ref(root)
        nodeid = "tests/test_example.py::test_shared"
        registry = root / "contract-test-links.json"
        current = root / "CURRENT.json"
        make_collection(current, [nodeid], exit_code=0)
        # PC-1 y PC-2 comparten el mismo verificador; PC-3 queda sin cubrir.
        shared = valid_link(nodeid, ["PC-1", "PC-2"])
        make_registry(registry, contract.name, sha, [shared])
        proc = run_validate(
            "--project-root", str(root),
            "--registry", str(registry),
            "--collection", str(current),
        )
        self.assertEqual(
            proc.returncode, 1,
            "PC-3: el hueco (PC-3 sin verificador) debe dar 1 "
            f"(rc={proc.returncode}): {proc.stderr[-1500:]}",
        )
        payload = json.loads(proc.stdout)
        gaps = payload.get("gaps", payload.get("missing", []))
        self.assertTrue(gaps, "PC-3: el informe no enumera obligaciones sin verificador.")
        flat = json.dumps(payload)
        self.assertIn("PC-3", flat, "PC-3: el hueco no nombra la obligación.")
        self.assertIn("huecos", flat.lower(), "PC-3: el hueco no se agrupa por promesa.")
        # Compartir un test entre obligaciones no genera defecto extra.
        self.assertNotIn(
            "PC-1", json.dumps(gaps),
            "PC-4: reutilizar un test entre PC-1 y PC-2 no debe pedir más tests.",
        )
        # kind:review sin motivo ni referencia resoluble -> inválido.
        bad_review = root / "registry-review-bad.json"
        make_registry(
            bad_review, contract.name, sha,
            [{
                "pc_ids": ["PC-3"],
                "verifier": {"kind": "review"},
                "protects": "Revisión sin motivo.",
                "evidence": [],
                "limits": "Declarado.",
            }],
        )
        pr = run_validate(
            "--project-root", str(root),
            "--registry", str(bad_review),
            "--collection", str(current),
        )
        self.assertEqual(pr.returncode, 1, "PC-4: review sin motivo debe dar 1.")
        # kind:review con motivo y referencia resoluble -> no se presenta
        # como ejecución de test ni como aceptación semántica.
        good_review = root / "registry-review-ok.json"
        make_registry(
            good_review, contract.name, sha,
            [shared, {
                "pc_ids": ["PC-3"],
                "verifier": {
                    "kind": "review",
                    "reference": {"path": doc.name, "sha256": doc_sha, "locator": locator},
                    "reason": "Inspección manual del redactado.",
                },
                "protects": "Revisión del redactado de huecos.",
                "evidence": [],
                "limits": "Declarado; no es ejecución de test.",
            }],
        )
        pg = run_validate(
            "--project-root", str(root),
            "--registry", str(good_review),
            "--collection", str(current),
        )
        self.assertEqual(pg.returncode, 0, "PC-4: review motivado no debe dar 1.")
        out = json.loads(pg.stdout)
        self.assertNotIn("executed", json.dumps(out).lower(),
                         "PC-4: el review no debe presentarse como ejecución.")

    # ------------------------------------------------------------------
    # R-B2 — PC-3 (ejemplo inline / bloque no es obligación)
    # ------------------------------------------------------------------
    def test_R_B2_ejemplo_inline_y_bloque_no_son_obligaciones(self) -> None:
        """PC-3: los ejemplos de marcador no amplían el universo de obligaciones.

        Sin este test, el usuario vería un hueco fantasma `PC-1 (promesa A)`
        con exit 1 aunque su registro vincule la única obligación real; el
        ejemplo de la prosa (inline y en bloque de código) se contaría como
        postcondición del contrato.
        """
        root = make_project()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, True))
        contract = root / "contract.md"
        contract.write_text(
            "# spec-test\n"
            "Para adoptar usá `<!-- cdad:pc PC-1 promise=A -->` como ejemplo.\n"
            "\n"
            "```\n"
            "<!-- cdad:pc PC-1 promise=A -->\n"
            "```\n"
            "<!-- cdad:pc PC-2 promise=B -->\n"
            "La entrega recupera el vínculo.\n",
            encoding="utf-8",
        )
        sha = sha256_of(contract)
        nodeid = "tests/test_example.py::test_observable_promise"
        registry = root / "contract-test-links.json"
        current = root / "CURRENT.json"
        make_collection(current, [nodeid], exit_code=0)
        make_registry(
            registry, contract.name, sha, [valid_link(nodeid, ["PC-2"])],
        )
        proc = run_validate(
            "--project-root", str(root),
            "--registry", str(registry),
            "--collection", str(current),
        )
        self.assertEqual(
            proc.returncode, 0,
            "PC-3: el ejemplo inline / en bloque no es obligación; "
            "el vínculo de la única obligación real debe dar 0 "
            f"(rc={proc.returncode}): {proc.stderr[-1500:]} {proc.stdout[-1500:]}",
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(
            payload.get("status"), "ok",
            "PC-3: el resultado sin huecos reales debe declarar status ok.",
        )
        gaps = payload.get("gaps", payload.get("missing", []))
        self.assertEqual(gaps, [], "PC-3: no debe haber huecos; el ejemplo no es obligación.")
        flat = json.dumps(payload)
        self.assertNotIn(
            "PC-1", flat,
            "PC-3: la obligación de ejemplo (PC-1) no pertenece al universo.",
        )

    # ------------------------------------------------------------------
    # R-C1 — PC-5
    # ------------------------------------------------------------------
    def test_R_C1_nuevos_nodeids_entre_colecciones(self) -> None:
        """PC-5: nodeids nuevos (CURRENT−BASE) vinculados o informados con 1.

        Sin este test, el usuario introduciría tests sin vínculo sin enterarse;
        sin baseline la comprobación quedaría silenciosa en vez de declararse
        no realizada.
        """
        root = make_project()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, True))
        contract, sha = make_contract_new(root)
        doc, doc_sha, locator = make_doc_ref(root)
        old_node = "tests/test_example.py::test_observable_promise"
        new_node = "tests/test_example.py::test_nuevo_sin_vinculo"
        base = root / "BASE.json"
        current = root / "CURRENT.json"
        make_collection(base, [old_node], exit_code=0)
        make_collection(current, [old_node, new_node], exit_code=0)
        registry = root / "contract-test-links.json"
        make_registry(registry, contract.name, sha, [valid_link(old_node)])
        proc = run_validate(
            "--project-root", str(root),
            "--registry", str(registry),
            "--collection", str(current),
            "--baseline", str(base),
        )
        self.assertEqual(
            proc.returncode, 1,
            "PC-5: nodeid nuevo sin vínculo debe dar 1 "
            f"(rc={proc.returncode}): {proc.stderr[-1500:]}",
        )
        self.assertIn(new_node, proc.stdout, "PC-5: el 1 no informa el nodeid nuevo.")
        # Vinculado -> verde.
        linked = root / "registry-linked.json"
        make_registry(
            linked, contract.name, sha,
            [valid_link(old_node), valid_link(new_node, ["PC-2"]),
             {
                 # PC-3 (huecos) no es la promesa de R-C1, pero el universo
                 # mecánico del contrato fixture la exige: sin este
                 # verificador el 0 esperado contradice PC-3 y R-B1.
                 "pc_ids": ["PC-3"],
                 "verifier": {
                     "kind": "review",
                     "reference": {"path": doc.name, "sha256": doc_sha, "locator": locator},
                     "reason": "Revisión manual del redactado de huecos; reutiliza PC-4 sin exigir tests de más.",
                 },
                 "protects": "Revisión del redactado de huecos (cobertura mecánica del fixture).",
                 "evidence": [],
                 "limits": "Declarado; no es ejecución de test.",
             }],
        )
        pl = run_validate(
            "--project-root", str(root),
            "--registry", str(linked),
            "--collection", str(current),
            "--baseline", str(base),
        )
        self.assertEqual(pl.returncode, 0, "PC-5: nuevo vinculado no debe dar 1.")
        # Sin baseline la comprobación queda explícitamente no realizada.
        pn = run_validate(
            "--project-root", str(root),
            "--registry", str(linked),
            "--collection", str(current),
        )
        payload = json.loads(pn.stdout)
        self.assertIn(
            "tests nuevos no comprobados", pn.stdout,
            "PC-5: sin baseline el informe debe decir «tests nuevos no comprobados».",
        )
        self.assertNotIn(new_node, json.dumps(payload.get("new_unlinked", [])),
                         "PC-5: sin baseline no se acusa al nodeid nuevo.")

    # ------------------------------------------------------------------
    # R-C2 — PC-6
    # ------------------------------------------------------------------
    def test_R_C2_delta_y_exigencia_en_review_sin_gate_en_red(self) -> None:
        """PC-6: delta como texto + materialización; intermedios sin gate de RED.

        Sin este test, el usuario perdería deltas en los handoffs o vería
        bloqueado RED por una comprobación que solo toca a Review/cierre.
        """
        root = make_project()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, True))
        contract, sha = make_contract_new(root)
        doc, doc_sha, locator = make_doc_ref(root)
        nodeid = "tests/test_example.py::test_observable_promise"
        current = root / "CURRENT.json"
        make_collection(current, [nodeid], exit_code=0)
        # El delta es texto (registro propuesto) que el orquestador materializa:
        # validar el delta no modifica archivos y el intermedio (sin baseline)
        # se registra sin exigir baseline.
        before = {p.name: sha256_of(p) for p in (contract, current)}
        registry = root / "contract-test-links.json"
        # PC-2 y PC-3 no son la promesa de R-C2, pero el universo mecánico
        # del contrato fixture las exige: sin este verificador el 0
        # esperado contradice PC-3 y R-B1.
        make_registry(registry, contract.name, sha, [valid_link(nodeid),
            {
                "pc_ids": ["PC-2", "PC-3"],
                "verifier": {
                    "kind": "review",
                    "reference": {"path": doc.name, "sha256": doc_sha, "locator": locator},
                    "reason": "Revisión manual del redactado; reutiliza PC-4 sin exigir tests de más.",
                },
                "protects": "Revisión del redactado (cobertura mecánica del fixture).",
                "evidence": [],
                "limits": "Declarado; no es ejecución de test.",
            }])
        proc = run_validate(
            "--project-root", str(root),
            "--registry", str(registry),
            "--collection", str(current),
        )
        self.assertEqual(
            proc.returncode, 0,
            "PC-6: el intermedio (delta válido, sin baseline) no bloquea RED "
            f"(rc={proc.returncode}): {proc.stderr[-1500:]}",
        )
        payload = json.loads(proc.stdout)
        self.assertIn(
            "tests nuevos no comprobados", proc.stdout,
            "PC-6: el intermedio debe registrarse como no comprobado, no como gate.",
        )
        self.assertIn("scope", payload, "PC-6: el intermedio debe registrar su ámbito.")
        after = {p.name: sha256_of(p) for p in (contract, current)}
        self.assertEqual(before, after, "PC-6: validar no modifica contrato ni tests.")
        # En cierre (con baseline del mismo ámbito) la comprobación sí se exige.
        base = root / "BASE.json"
        make_collection(base, [nodeid], exit_code=0)
        current2 = root / "CURRENT2.json"
        cierre_nuevo = "tests/test_example.py::test_nuevo_en_cierre"
        make_collection(current2, [nodeid, cierre_nuevo], exit_code=0)
        pc = run_validate(
            "--project-root", str(root),
            "--registry", str(registry),
            "--collection", str(current2),
            "--baseline", str(base),
        )
        self.assertEqual(
            pc.returncode, 1,
            "PC-6: en cierre el nodeid nuevo sin vínculo debe dar 1.",
        )
        self.assertIn(
            cierre_nuevo, pc.stdout,
            "PC-6: el 1 debe nombrar el nodeid nuevo sin vínculo.",
        )

    # ------------------------------------------------------------------
    # R-D1 — PC-7
    # ------------------------------------------------------------------
    def test_R_D1_sin_registro_no_bloquea_y_corrupto_no_es_ausencia(self) -> None:
        """PC-7: sin registro ``not_configured`` no bloqueante; corrupto es ``invalid``.

        Sin este test, el usuario quedaría bloqueado sin haber adoptado el
        registro, o una corrupción pasaría como ausencia.
        """
        root = make_project()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, True))
        missing = root / "no-existe.json"
        proc = run_validate("--project-root", str(root), "--registry", str(missing))
        self.assertEqual(
            proc.returncode, 0,
            "PC-7: sin registro el ciclo continúa con diagnóstico no bloqueante "
            f"(rc={proc.returncode}): {proc.stderr[-1500:]}",
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(
            payload.get("status"), "not_configured",
            "PC-7: sin registro el status debe ser not_configured.",
        )
        self.assertIn(
            "sin registro", proc.stdout.lower(),
            "PC-7: el diagnóstico debe decir «sin registro de vínculos declarado» o similar.",
        )
        # Registro presente pero corrupto no se trata como ausente.
        corrupt = root / "contract-test-links.json"
        corrupt.write_text("{ no es json válido", encoding="utf-8")
        current = root / "CURRENT.json"
        make_collection(current, [], exit_code=0)
        pc = run_validate(
            "--project-root", str(root),
            "--registry", str(corrupt),
            "--collection", str(current),
        )
        self.assertEqual(pc.returncode, 1, "PC-7: registro corrupto debe dar 1.")
        self.assertNotEqual(
            json.loads(pc.stdout).get("status"), "not_configured",
            "PC-7: lo corrupto no es ausencia.",
        )

    # ------------------------------------------------------------------
    # R-D2 — PC-8 e invariantes
    # ------------------------------------------------------------------
    def test_R_D2_ambito_limites_y_reorden_sin_cambios(self) -> None:
        """PC-8 e invariantes: verde declara ámbito/límites; reorden no cambia nada.

        Sin este test, el usuario confundiría un verde estructural con
        aceptación semántica o con ejecución; un reorden inocente parecería
        un defecto nuevo.
        """
        root = make_project()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, True))
        contract, sha = make_contract_new(root)
        doc, doc_sha, locator = make_doc_ref(root, "doc-d2.md")
        n1 = "tests/test_example.py::test_a"
        n2 = "tests/test_example.py::test_b"
        current = root / "CURRENT.json"
        make_collection(current, [n1, n2], exit_code=0)
        registry = root / "contract-test-links.json"
        link1 = valid_link(n1, ["PC-1"])
        link2 = valid_link(n2, ["PC-2"])
        # PC-3 (huecos) no es la promesa de R-D2, pero el universo mecánico
        # del contrato fixture la exige: sin este verificador el 0 esperado
        # contradice PC-3 y R-B1.
        review_pc3 = {
            "pc_ids": ["PC-3"],
            "verifier": {
                "kind": "review",
                "reference": {"path": doc.name, "sha256": doc_sha, "locator": locator},
                "reason": "Revisión manual del redactado de huecos; reutiliza PC-4 sin exigir tests de más.",
            },
            "protects": "Revisión del redactado de huecos (cobertura mecánica del fixture).",
            "evidence": [],
            "limits": "Declarado; no es ejecución de test.",
        }
        make_registry(registry, contract.name, sha, [link1, link2, review_pc3])
        snapshot = {
            "contract": sha256_of(contract),
            "registry": sha256_of(registry),
            "collection": sha256_of(current),
        }
        proc = run_validate(
            "--project-root", str(root),
            "--registry", str(registry),
            "--collection", str(current),
        )
        self.assertEqual(
            proc.returncode, 0,
            "PC-8: el verde estructural debe dar 0 "
            f"(rc={proc.returncode}): {proc.stderr[-1500:]}",
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload.get("status"), "ok")
        self.assertIn("scope", payload, "PC-8: el verde declara su ámbito.")
        self.assertIn("limits", payload, "PC-8: el verde declara sus límites.")
        blob = json.dumps(payload).lower()
        self.assertNotIn("executed", blob, "PC-8: el verde no afirma ejecución.")
        self.assertNotIn("pertinence", blob, "PC-8: el verde no afirma pertinencia.")
        self.assertNotIn("sensitivity", blob, "PC-8: el verde no afirma sensibilidad.")
        self.assertNotIn("approved", blob, "PC-8: el verde no afirma aprobación.")
        # Reordenar vínculos y nodeids no cambia los conjuntos.
        reordered = root / "registry-reordered.json"
        make_registry(reordered, contract.name, sha, [link2, link1, review_pc3])
        shuffled_col = root / "CURRENT-shuffled.json"
        make_collection(shuffled_col, [n2, n1], exit_code=0)
        pr = run_validate(
            "--project-root", str(root),
            "--registry", str(reordered),
            "--collection", str(shuffled_col),
        )
        self.assertEqual(pr.returncode, 0, "Reordenar no debe cambiar el verde.")
        # Invariantes: validar no modifica nada; evidencia vacía no es ejecución.
        self.assertEqual(
            {"contract": sha256_of(contract), "registry": sha256_of(registry),
             "collection": sha256_of(current)},
            snapshot,
            "Validar no modifica contrato, registro ni tests.",
        )
        gap_reg = root / "registry-gap.json"
        make_registry(gap_reg, contract.name, sha, [link1])
        pg = run_validate(
            "--project-root", str(root),
            "--registry", str(gap_reg),
            "--collection", str(current),
        )
        self.assertEqual(pg.returncode, 1, "El hueco sigue dando 1 tras reordenar.")
        self.assertIn("PC-3", pg.stdout, "El hueco debe nombrar la obligación afectada.")

    # ------------------------------------------------------------------
    # R-B3 — PC-3 (B1: backtick suelto no traga marcadores posteriores)
    # ------------------------------------------------------------------
    def test_R_B3_backtick_suelto_no_traga_marcador_posterior(self) -> None:
        """PC-3: un backtick sin cerrar en la prosa no oculta obligaciones reales.

        Sin este test, el usuario recibiría un verde con rc 0 aunque PC-2 no
        tenga verificador: el span inline abierto por el backtick suelto se
        traga el marcador posterior y el universo queda truncado (falso verde).
        """
        root = make_project()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, True))
        contract = root / "contract.md"
        contract.write_text(
            "# spec-test\n"
            "<!-- cdad:pc PC-1 promise=entrega -->\n"
            "La entrega recupera el vínculo.\n"
            "Un párrafo con un backtick suelto ` sin cerrar que sigue y sigue.\n"
            "\n"
            "<!-- cdad:pc PC-2 promise=huecos -->\n"
            "Los huecos se agrupan por promesa.\n",
            encoding="utf-8",
        )
        sha = sha256_of(contract)
        nodeid = "tests/test_example.py::test_observable_promise"
        registry = root / "contract-test-links.json"
        current = root / "CURRENT.json"
        make_collection(current, [nodeid], exit_code=0)
        make_registry(registry, contract.name, sha, [valid_link(nodeid, ["PC-1"])])
        proc = run_validate(
            "--project-root", str(root),
            "--registry", str(registry),
            "--collection", str(current),
        )
        self.assertEqual(
            proc.returncode, 1,
            "PC-3: PC-2 queda sin verificador y debe informarse como hueco "
            f"(rc={proc.returncode}): {proc.stderr[-1500:]} {proc.stdout[-1500:]}",
        )
        payload = json.loads(proc.stdout)
        gaps = payload.get("gaps", payload.get("missing", []))
        self.assertTrue(gaps, "PC-3: el informe no enumera obligaciones sin verificador.")
        flat = json.dumps(payload)
        self.assertIn("PC-2", flat, "PC-3: el hueco no nombra la obligación tragada (PC-2).")
        self.assertIn("huecos", flat.lower(), "PC-3: el hueco no se agrupa por promesa.")
        self.assertNotIn(
            "PC-1", json.dumps(gaps),
            "PC-3: PC-1 está vinculada y no debe aparecer como hueco.",
        )

    # ------------------------------------------------------------------
    # R-B4 — PC-1, PC-8 (B2: el resultado declara modo y obligaciones)
    # ------------------------------------------------------------------
    def test_R_B4_resultado_declara_modo_y_obligaciones(self) -> None:
        """PC-1, PC-8: el resultado declara ``mode`` y lista ``obligations``.

        Sin este test, el usuario no sabría si el informe cubre marcadores o
        el índice legacy acotado: un verde en modo legacy parecería una
        extracción exhaustiva del contrato en vez de las obligaciones indexadas.
        """
        root = make_project()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, True))
        # Escenario 1: contrato con marcadores -> mode == "markers".
        contract, sha = make_contract_new(root)
        doc, doc_sha, locator = make_doc_ref(root)
        n1 = "tests/test_example.py::test_a"
        n2 = "tests/test_example.py::test_b"
        current = root / "CURRENT.json"
        make_collection(current, [n1, n2], exit_code=0)
        registry = root / "contract-test-links.json"
        review_pc3 = {
            "pc_ids": ["PC-3"],
            "verifier": {
                "kind": "review",
                "reference": {"path": doc.name, "sha256": doc_sha, "locator": locator},
                "reason": "Revisión manual del redactado de huecos; reutiliza PC-4 sin exigir tests de más.",
            },
            "protects": "Revisión del redactado de huecos (cobertura mecánica del fixture).",
            "evidence": [],
            "limits": "Declarado; no es ejecución de test.",
        }
        make_registry(
            registry, contract.name, sha,
            [valid_link(n1, ["PC-1"]), valid_link(n2, ["PC-2"]), review_pc3],
        )
        proc = run_validate(
            "--project-root", str(root),
            "--registry", str(registry),
            "--collection", str(current),
        )
        self.assertEqual(
            proc.returncode, 0,
            "PC-1: el registro válido con cobertura total debe dar 0 "
            f"(rc={proc.returncode}): {proc.stderr[-1500:]}",
        )
        payload = json.loads(proc.stdout)

        def _oid(o: dict) -> object:
            return o.get("id", o.get("pc_id"))

        def _opromise(o: dict) -> object:
            return o.get("promise", o.get("promesa"))

        def _overifiers(o: dict) -> object:
            if "verifiers" in o:
                return o["verifiers"]
            return o.get("verifier", "MISSING")

        self.assertEqual(
            payload.get("mode"), "markers",
            "PC-8: el resultado con marcadores debe declarar mode=markers.",
        )
        obligations = payload.get("obligations")
        self.assertIsInstance(
            obligations, list,
            "PC-1: el resultado debe listar obligations con id, promesa y verificadores.",
        )
        assert isinstance(obligations, list)
        ids = {_oid(o) for o in obligations if isinstance(o, dict)}
        self.assertTrue(
            {"PC-1", "PC-2", "PC-3"} <= ids,
            "PC-1: obligations no cubre las obligaciones del contrato con marcadores.",
        )
        for o in obligations:
            self.assertTrue(isinstance(o, dict) and _oid(o),
                            "PC-1: cada obligation declara su id.")
            self.assertTrue(_opromise(o),
                            "PC-8: cada obligation declara su promesa.")
            self.assertNotEqual(_overifiers(o), "MISSING",
                                "PC-1: cada obligation declara sus verificadores.")
        # Escenario 2: contrato antiguo con índice legacy -> mode == "legacy".
        legacy_contract = root / "legacy.md"
        legacy_locator = "fragmento literal único del contrato antiguo 016-001"
        legacy_contract.write_text(f"# antiguo\n\n{legacy_locator}\n", encoding="utf-8")
        legacy_sha = sha256_of(legacy_contract)
        legacy_node = "tests/test_example.py::test_legado"
        legacy_col = root / "CURRENT-legacy.json"
        make_collection(legacy_col, [legacy_node], exit_code=0)
        legacy_reg = root / "legacy-links.json"
        make_registry(
            legacy_reg, legacy_contract.name, legacy_sha,
            [valid_link(legacy_node, ["PD-1"])],
            legacy=[{"id": "PD-1", "promise": "entrega-correlacionada",
                     "locator": legacy_locator}],
        )
        pl = run_validate(
            "--project-root", str(root),
            "--registry", str(legacy_reg),
            "--collection", str(legacy_col),
        )
        self.assertEqual(
            pl.returncode, 0,
            "PC-1: el registro legacy válido debe dar 0 "
            f"(rc={pl.returncode}): {pl.stderr[-1500:]} {pl.stdout[-1500:]}",
        )
        legacy_payload = json.loads(pl.stdout)
        self.assertEqual(
            legacy_payload.get("mode"), "legacy",
            "PC-8: el resultado legacy debe declarar mode=legacy.",
        )
        legacy_obs = legacy_payload.get("obligations")
        self.assertIsInstance(
            legacy_obs, list,
            "PC-1: el resultado legacy debe listar obligations indexadas.",
        )
        assert isinstance(legacy_obs, list)
        self.assertIn(
            "PD-1", {_oid(o) for o in legacy_obs if isinstance(o, dict)},
            "PC-1: obligations no cubre la obligación indexada PD-1.",
        )
        self.assertIn(
            "obligaciones indexadas", pl.stdout.lower(),
            "PC-8: en modo legacy el informe declara que cubre las "
            "obligaciones indexadas, no una extracción exhaustiva.",
        )

    # ------------------------------------------------------------------
    # R-B5 — PC-3, PC-8 (B2: contrato sin obligaciones no da verde)
    # ------------------------------------------------------------------
    def test_R_B5_contrato_sin_obligaciones_no_da_verde(self) -> None:
        """PC-3, PC-8: sin marcadores ni índice legacy el resultado es 1.

        Sin este test, el usuario recibiría un verde con cero obligaciones: un
        falso verde que presenta como cubierto un contrato que no declara nada.
        """
        root = make_project()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, True))
        contract = root / "contract.md"
        contract.write_text(
            "# spec-test\n\nProsa sin marcadores y sin índice legacy.\n",
            encoding="utf-8",
        )
        sha = sha256_of(contract)
        nodeid = "tests/test_example.py::test_observable_promise"
        registry = root / "contract-test-links.json"
        current = root / "CURRENT.json"
        make_collection(current, [nodeid], exit_code=0)
        make_registry(registry, contract.name, sha, [])
        proc = run_validate(
            "--project-root", str(root),
            "--registry", str(registry),
            "--collection", str(current),
        )
        self.assertEqual(
            proc.returncode, 1,
            "PC-3: un contrato que no declara obligaciones no puede dar ok "
            f"(rc={proc.returncode}): {proc.stderr[-1500:]} {proc.stdout[-1500:]}",
        )
        low = proc.stdout.lower()
        self.assertIn(
            "obligac", low,
            "PC-8: el diagnóstico debe decir que el contrato no declara obligaciones.",
        )
        self.assertTrue(
            ("no declara" in low) or ("sin obligaciones" in low)
            or ("cero" in low) or ("zero" in low) or ("empty" in low),
            "PC-8: el diagnóstico debe ser explícito "
            "(p. ej. «no declara obligaciones»), no un 1 sin texto.",
        )
        payload = json.loads(proc.stdout)
        self.assertNotEqual(
            payload.get("status"), "ok",
            "PC-8: con cero obligaciones el status no puede ser ok.",
        )

    # ------------------------------------------------------------------
    # R-B6 — PC-3 (O1: marcador duplicado con promesas distintas)
    # ------------------------------------------------------------------
    def test_R_B6_marcador_duplicado_con_promesas_distintas(self) -> None:
        """PC-3: un id de marcador duplicado con promesas distintas da 1.

        Sin este test, el usuario creería cubiertas dos promesas distintas con
        un solo vínculo: el universo mecánico quedaría ambiguo y el hueco de
        una de ellas nunca se informaría (protección de regresión O1).
        """
        root = make_project()
        self.addCleanup(lambda: __import__("shutil").rmtree(root, True))
        contract = root / "contract.md"
        contract.write_text(
            "# spec-test\n"
            "<!-- cdad:pc PC-1 promise=A -->\n"
            "Texto de la primera promesa.\n"
            "<!-- cdad:pc PC-1 promise=B -->\n"
            "Texto de la segunda promesa con el mismo id.\n",
            encoding="utf-8",
        )
        sha = sha256_of(contract)
        nodeid = "tests/test_example.py::test_observable_promise"
        registry = root / "contract-test-links.json"
        current = root / "CURRENT.json"
        make_collection(current, [nodeid], exit_code=0)
        make_registry(registry, contract.name, sha, [valid_link(nodeid, ["PC-1"])])
        proc = run_validate(
            "--project-root", str(root),
            "--registry", str(registry),
            "--collection", str(current),
        )
        self.assertEqual(
            proc.returncode, 1,
            "PC-3: el marcador duplicado con promesas distintas debe dar 1 "
            f"(rc={proc.returncode}): {proc.stderr[-1500:]} {proc.stdout[-1500:]}",
        )
        self.assertIn(
            "duplicate_marker", proc.stdout,
            "PC-3: el 1 debe informar duplicate_marker.",
        )
        self.assertIn(
            "PC-1", proc.stdout,
            "PC-3: el 1 debe nombrar el id duplicado.",
        )


if __name__ == "__main__":
    unittest.main()
