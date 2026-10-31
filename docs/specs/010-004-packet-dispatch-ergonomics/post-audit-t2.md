# FINAL TEXT — test-writer POST-AUDIT T2 (010-004, dispatch C)

## 0. Validación de entrada (Route C)

- Script fuente: repositorio `skills/cdad-cycle/scripts/cdad_packet.py --project-root <repo>` (no se usó ni modificó la copia global; drift D-1 respetado).
- `validate-request` → exit 0 · `validate-packet` → exit 0 · `render` vs `PACKET.md` → **byte-idéntico** (`diff` vacío).
- Pins verificados por `sha256sum`: packet `b637c957…` ✓ · request `8c74ebee…` ✓ · spec (`fc6b2ccc…`) ✓ · plan (`2ae8ada3…`) ✓.
- Implementación no leída: ningún archivo de `skills/`, `scripts/`, `sources/`, `agents/`, `build/` fue leído; el CLI solo se ejecutó black-box para validación y en los tests. Edición restringida a `tests/**`.

## 1. Traza por test modificado

**(a) `tests/test_004_002_t6_landing.py::TestPd12LegacyIntake::test_pd12_legacy_without_policy_keeps_legacy_intake` (hoy :606-669)**
- Expectativa anterior (docstring :607-610 «conserva el camino implícito anterior», asertos :630-642: rc=0 + stdout empieza con `PACKET_BEGIN`): PD-12 de `docs/specs/004-002-project-execution-bootstrap/spec.md:112-115` (proyecto legacy «conserva su intake») con prepare implícito publicando el paquete legacy v1.
- Sustitución: owner decision `docs/specs/010-004-packet-dispatch-ergonomics/owner-decision-v2-new-assignments.md` (**todo encargo nuevo v2**; el canon v1 implícito sin policy queda cerrado) → `010-004/spec.md` **§7 N-3** (:453, sustitución explícita de `004-002:115`) + **PC-04** (:406) + **§4.1** («toda preparación nueva utiliza v2», «se rechaza una selección v1 … también cuando falta `docs/cdad-policy.json`», «no se copia, convierte o reubica») + **INV-11** (:446).
- Nuevo contrato del test: rc≠0, stdout vacío, `published_packets(root)=={}`, v1 byte-idéntico, sin contexto v2 fabricado, state sin binding v2 ni `active_packet`. Se conservan escenario y aserciones vigentes (v1 intacto, no v2, state). Nota honesta: el docstring de la **clase** (:603-604) queda byte-idéntico por estar fuera del test auditado; su wording PD-12 histórico queda reflejado en §4.1 y el método lo recoge.

**(b) `tests/test_packet_prepare.py::TestPrepareDefaults::test_p2_default_execution_context_and_out_dir_under_project_cdad` (hoy :402-507)**
- Expectativa anterior (docstring :403 «without flags, EXEC = ROOT/.cdad/execution.json», aserto `assertEqual(result.returncode, 0)` en la corrida sin flags): preparación exitosa usando el EXEC default no canónico.
- Sustitución (lado EXEC): misma cadena owner → `010-004/spec.md` **§4.1** (:123 «Una copia en otra ubicación no es un localizador admitido aunque contenga la misma identidad»; ubicación canónica `:117` `.cdad/executions/<execution_id>/execution.json`) → **PC-04** + **INV-11**.
- Lado OUT conservado en el **mismo** test (sin test aparte), según **resolución owner A2** de `audit-approval-2026-10-30.md` (:67-80): contexto v2 **explícito canónico** (`--execution-context` a `.cdad/executions/<EXECUTION_ID>/execution.json`), default OUT `ROOT/.cdad/packets`, request+cabecera coherentes; una sola promesa (P2). La declaración del localizador en request/cabecera (PC-04-c positivo) queda para el RED de T2.

## 2. Diff completo (commit `c6017728`, solo estos dos tests)

```diff
--- a/tests/test_004_002_t6_landing.py   (TestPd12LegacyIntake::test_pd12_legacy_without_policy_keeps_legacy_intake)
     def test_pd12_legacy_without_policy_keeps_legacy_intake(self) -> None:
-        """PD-12/I4-refinado: un proyecto legacy SIN política y SIN contexto
-        v2, ... conserva el camino implícito anterior: prepare (implícito)
-        publica el paquete legacy, no fabrica un contexto v2 y no modifica
-        el v1 (D2)."""
+        """PC-04 (010-004 §4.1/§7/INV-11, sustitución N-3 del owner). Un
+        proyecto legacy SIN política y SIN contexto v2, con su documento de
+        ejecución v1 en .cdad/execution.json, ya NO conserva el camino
+        implícito anterior (PD-12 de 004-002:112-115): la selección v1
+        implícita se RECHAZA antes de publicar (rc != 0, stdout vacío), sin
+        publicar paquete y sin efectos persistentes (INV-11). El v1 queda
+        byte-idéntico, no se fabrica contexto v2 y el state conserva su
+        intake histórico (§4.1) sin binding v2 ni paquete activo: su mera
+        presencia no habilita preparación nueva v1."""
         temp = tempfile.mkdtemp(prefix="cdad-t6-legacy-")
         ...
         v1_bytes = v1_path.read_bytes()
         # state sin binding v2 ni paquete activo (el intake legacy manda).
+        state_path = root / "docs" / ".cdad-state.json"
         write_consumer_state(root, consumer_state())
         proc = self.run_installed(root, "prepare", ...)
-        self.assertEqual(proc.returncode, 0, msg="el intake legacy se rompió...")
-        self.assertTrue(proc.stdout.startswith(PACKET_BEGIN), msg="el intake legacy no imprimió el paquete canónico")
+        # PC-04/INV-11: rechazo antes de publicar, sin paquete ni efectos.
+        self.assertNotEqual(proc.returncode, 0, msg="PC-04 ... debe rechazarse antes de publicar; prepare respondió exit 0 con ...")
+        self.assertEqual(proc.stdout, "", msg="el rechazo PC-04 no debe publicar paquete: stdout vacío exigido...")
+        self.assertEqual(published_packets(root), {}, msg="el rechazo PC-04 publicó un paquete (INV-11)")
         self.assertEqual(v1_path.read_bytes(), v1_bytes, msg="el documento v1 del proyecto legacy fue modificado")  # conservado
         self.assertEqual(v2_execution_docs(root), {},
-            msg="el camino legacy fabricó un contexto v2")
+            msg="el rechazo PC-04 fabricó un contexto v2 (§4.1: no se copia, convierte ni reubica el contexto para hacerla pasar)")
+        post_state = json.loads(state_path.read_text(encoding="utf-8"))
+        self.assertIsNone(post_state["execution"], msg="el rechazo PC-04 dejó binding v2 en state (INV-11)")
+        self.assertIsNone(post_state["active_packet"], msg="el rechazo PC-04 dejó paquete activo en state (INV-11)")

--- a/tests/test_packet_prepare.py   (TestPrepareDefaults::test_p2_default_execution_context_and_out_dir_under_project_cdad)
-        """P2 (§1): without flags, EXEC = ROOT/.cdad/execution.json and OUT = ROOT/.cdad/packets."""
+        """P2 (010-004 §4.1/PC-04 + decisión owner A2; sustituye el lado EXEC
+        de la expectativa 003-005). Sin flags, una copia v2 del contexto en
+        la ubicación NO canónica ROOT/.cdad/execution.json no es localizador
+        admisible para preparación nueva (§4.1: una copia en otra ubicación
+        no es localizador admitido) y debe rechazarse antes de publicar
+        (INV-11), sin copiar/convertir/reubicar el contexto para hacerla
+        pasar. Con el contexto v2 explícito en su ubicación canónica
+        (.cdad/executions/<execution_id>/execution.json), el default de
+        salida ROOT/.cdad/packets sigue declarado y la preparación nueva
+        exitosa publica allí con request y cabecera coherentes."""
         self.require_prepare()
         project = self.project()
         cdad_dir = project.root / ".cdad"
         cdad_dir.mkdir()
-        shutil.copyfile(project.execution_path, cdad_dir / "execution.json")
+        stale_copy = cdad_dir / "execution.json"
+        stale_copy.write_bytes(project.execution_path.read_bytes())
         project.execution_path.unlink()
+        # Lado EXEC (sustituido por PC-04): sin flags, la copia v2 en la
+        # ubicación no canónica no autoriza la preparación nueva.
         result = run_prepare(PACKET_CLI, "--project-root", str(project.root), "--role",
-            "test-writer", "--substage", "red", "--objective", "defaults")
-        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
+            project.role, "--substage", project.substage, "--objective", "defaults")
+        self.assertNotEqual(result.returncode, 0, msg="PC-04 ... debe rechazarse antes de publicar; prepare respondió exit 0 ...")
+        packets_dir = cdad_dir / "packets"
+        published = (list(packets_dir.glob("*/REQUEST.json")) if packets_dir.is_dir() else [])
+        self.assertEqual(published, [], msg="el rechazo PC-04 publicó un paquete (INV-11)")
+        self.assertTrue(stale_copy.is_file(), msg="el rechazo PC-04 reubicó o absorbió la copia no canónica ..." )
+        executions_dir = cdad_dir / "executions"
+        relocated = (list(executions_dir.glob("*/execution.json")) if executions_dir.is_dir() else [])
+        self.assertEqual(relocated, [], msg="el rechazo PC-04 fabricó un contexto canónico desde la copia no canónica (INV-11: sin efectos persistentes)")
+        state = json.loads(project.state_path.read_text(encoding="utf-8"))
+        self.assertIsNone(state["execution"], msg="el rechazo PC-04 dejó binding v2 en state (INV-11)")
+        self.assertIsNone(state["active_packet"], msg="el rechazo PC-04 dejó paquete activo en state (INV-11)")
+        # Lado OUT (conservado, decisión owner A2): contexto v2 explícito en
+        # su ubicación canónica, sin --out-dir: el default de salida
+        # ROOT/.cdad/packets sigue declarado y la preparación exitosa publica
+        # allí con request y cabecera coherentes.
+        canonical = cdad_dir / "executions" / EXECUTION_ID / "execution.json"
+        canonical.parent.mkdir(parents=True, exist_ok=True)
+        canonical.write_bytes(stale_copy.read_bytes())
+        result = run_prepare(PACKET_CLI, "--project-root", str(project.root), "--execution-context",
+            str(canonical), "--role", project.role, "--substage", project.substage, "--objective", "defaults")
+        self.assertEqual(result.returncode, 0, "P2 (decisión A2): ... " + result.stderr.decode(errors="replace"))
         packet_dir = cdad_dir / "packets" / project.packet_id()
         self.assertTrue((packet_dir / "REQUEST.json").is_file())                                       # conservado
         self.assertEqual((packet_dir / "PACKET.md").read_bytes(), result.stdout)                       # conservado
+        request = json.loads((packet_dir / "REQUEST.json").read_text(encoding="utf-8"))
+        self.assertEqual(request["packet_id"], project.packet_id(), msg="request y cabecera incoherentes con la publicación P2")
```

## 3. Evidencia de corrida (SEPARADA)

**Tests actualizados** (`python3 -m pytest tests/test_004_002_t6_landing.py::TestPd12LegacyIntake::test_pd12_legacy_without_policy_keeps_legacy_intake tests/test_packet_prepare.py::TestPrepareDefaults::test_p2_default_execution_context_and_out_dir_under_project_cdad -q`):

```
2 failed in 11.92s
```
- (a) **FAILED — AssertionError**, primer aserto nuevo (`test_004_002_t6_landing.py:637`): `AssertionError: 0 == 0 : ... prepare respondió exit 0 con stdout='---cdad-packet-json...policy":null...'` → PC-04 aún **no implementado**: prepare sigue publicando el encargo implícito v1 sin policy. Rojo legítimo por la razón esperada; **no se debilitó ninguna aserción**.
- (b) **FAILED — AssertionError** (`test_packet_prepare.py:434`): `AssertionError: 0 == 0 : ... prepare respondió exit 0 con stdout=b'---cdad-packet-json...'` → la copia v2 no canónica sigue siendo admitida sin flags. Mismo tratamiento: se reporta, no se implementa, no se convierte en RED nuevo (un solo subfase).

**Tests declarados intactos — TODOS verdes:**

| Corrida | Resumen |
|---|---|
| `test_packet_prepare.py::TestPrepareFailureHasNoEffects::test_p4_default_out_dir_is_not_created_on_failure` | `1 passed in 1.75s` |
| `test_004_002_t2_bootstrap.py::{TestPd10ForwardAdoption::test_pd10_v1_present_without_flag_fails_demanding_new_execution, TestPd3AuthorityNegatives::test_pd3_negative_policy_missing, TestPd4IdentityAndResume (clase completa, 4 tests)}` | `6 passed in 5.28s` |
| `test_role_packet_render.py::{TestPacketIntegrity::test_p2_validate_packet_rejects_tampered_body_metadata_and_hash, TestPublicTask2Surface::test_p1_all_role_substage_pairs_render_and_validate, TestPublicTask2Surface::test_p1_repeated_render_is_byte_deterministic, TestPacketIntegrity::test_p2_metadata_is_canonical_and_matches_request}` (PC-08a) | `4 passed in 16.25s` |
| `test_role_packet_review_regressions.py::TestReviewRegresions::test_p2_validate_packet_rejects_crlf_byte_variant` (PC-08a CRLF) | `1 passed in 10.76s` |

(Nonea: los nombres sin clase del paquete `test_role_packet_render.py`/`review_regressions` se resolvieron a sus clases reales `TestPacketIntegrity`/`TestPublicTask2Surface`/`TestReviewRegressions` — única referencia had. Sin suite completa, sin push, sin publicación.)

## 4. Archivos modificados y intactos

- Modificados: **solo** `tests/test_004_002_t6_landing.py` (1 hunk, el test (a)) y `tests/test_packet_prepare.py` (1 hunk, el test (b)) — `git diff --stat`: `2 files changed, 115 insertions(+), 16 deletions(-)`.
- `git status` tras el commit: solo el untracked preexistente `docs/specs/010-000-continuity-relative-root/discovery.md` (idéntico al estado que registró el AUDIT). Ningún test declarado intacto cambió; `docs/specs/004-002-project-execution-bootstrap/spec.md`, `010-004/spec.md`, `plan.md` y `test-audit.md` sin tocar.

## 5. Commit

```
c6017728 test: POST-AUDIT T1 (010-004) — sustituir expectativas PD-12 implícita v1 y default EXEC .cdad/execution.json por PC-04 (lado OUT conservado, A2)
HEAD ahora: c6017728 (base 1f2f238d)
```

Fin de la subfase: POST-AUDIT entregado. No escribí tests nuevos, no inicié RED, no implementé producto y no corrí la suite completa — el gate y los siguientes despachos (RED T2, GREEN) corresponden al orquestador.