#!/usr/bin/env python3
"""004-002 T7 P-1 RED — rutas privadas en la política del proyecto.

Contrato: docs/specs/004-002-project-execution-bootstrap/spec.md (PD-7/PD-8,
barreras efectivas — prueba positiva y negativa por las herramientas que
realmente media) + decisión del dueño (2026-10-02, ítem P-1 de T7,
supervisión de 004-002): campo OPCIONAL `path_policy.private_paths` (rutas
exactas o globs relativos a la raíz). Toda ruta privada queda denegada en
lectura y edición para TODOS los roles, en ambos runtimes:

  OpenCode (I9): cada derivado publicado lleva `read: <ruta>: deny` y
  `edit: <ruta>: deny` con precedencia findLast sobre los allow de raíz
  (la entrada de la ruta privada va DESPUÉS de los allow de tests/**, etc.).
  Sin el campo, los derivados son byte-idénticos a los actuales
  (compatibilidad).
  Claude Code (I10/C2): el guard dinámico bloquea Read/Edit/Write sobre la
  ruta privada y Grep/Glob cuando su `path` apunta exactamente a ella.

Validación (PD-2 — misma clase de rechazo que las raíces): entrada absoluta,
con `..` o vacía → `validate-policy` rc≠0 y ninguna publicación (la política
inválida impide preparar paquetes).

Fixture: los nombres de ruta privados y permitidos son FICTICIOS
("tests/secret.local", "tests/otro.py", "docs/private/**"); NO se lee ni
usa tests/.sensitive-patterns.local. Toda escritura queda en proyectos
sintéticos bajo tempdir; no se lee implementación (los archivos de producto
usados son las salidas declaradas del generador y el guard, mismo precedente
que test_004_002_t5_runtime.py).

Superficie observable (helpers reutilizados, no reimplementados):
  - T5/W-2/L-1: `LayoutProject` + `prepare` para derivados I9 en tempdirs,
    oráculo findLast de tests/pd10_permission_semantics.py (verdict).
  - Guard CC: `run_guard` de T5 con la forma REAL del JSON de hook.

Mapa test → postcondición (P-1, decisión del dueño):
  (a) test_p1_private_path_denied_in_every_derived_agent
      -> private_paths=["tests/secret.local"]: read y edit deny en cada
         derivado; tests/otro.py sigue allow para el test-writer.
  (a') test_p1_other_read_edit_verdicts_unchanged
      -> con el campo, todos los veredictos read/edit de las sondas exactas
         se conservan idénticos a la política sin el campo, salvo la ruta
         privada (que pasa a deny en ambos canales).
  (b) test_p1_private_glob_denied_in_every_derived_agent
      -> glob privado → read deny en cada derivado.
  (c) test_p1_cc_guard_blocks_private_path_and_allows_sibling
      -> guard CC (v2): Read/Write/Edit de tests/secret.local → exit 2;
         Read de tests/otro.py → permitido.
  (d) test_p1_without_field_deriveds_byte_identical
      -> derivados sin el campo byte-idénticos a los derivados actuales
         (compatibilidad).
  (e) test_p1_invalid_private_entries_rejected
      -> entradas absoluta / con ".." / vacía → rc≠0 con diagnóstico
         (validate-policy) y sin publicación (prepare rc≠0).

RED hoy (estado sondeado por este rol, en tempdirs sintéticos): el CLI
rechaza el campo (`ERROR: path_policy has unknown fields: private_paths`,
rc 2) — la feature NO está implementada aún. Estado declarado del oráculo:
  - (a), (a'), (b), (c) → RED por aserción de postcondición:
    * (a)/(a')/(b) fallan en la precondición verificable "prepare publica
      derivados con private_paths" (rc 2: campo desconocido — falta del
      comportamiento, no import/sintaxis);
    * (c) falla en el control "hermano permitido" (fails-first): con la
      política que lleva el campo, el guard NO PUEDE CLASIFICAR NADA
      ("cannot classify '...' under the project policy (invalid policy
      or classifier failure); blocking without fallback", y cita
      "unknown fields: private_paths") — bloquea TODO el trabajo
      legítimo: Read de tests/otro.py rc=2 en vez de 0.
      Complemento en (b)-CC: el guard bloquea el Glob privado por el
      MOTIVO EQUIVOCADO ("unknown fields") y no por una barrera de
      rutas privadas; la aserción exige rc=2 SIN ese diagnóstico.
  Además el sondeo fijó E0 (hallazgo, no requisito): NotebookEdit NO
  figura en ningún matcher de hooks CC (agents/claude-code/*) — el
  guard nunca la media, con o sin el campo; se registra y NO se exige
  su bloqueo (sería una ampliación no pedida; decidir si se agrega es
  del dueño/orquestador, fuera de este RED).
  - (d) y (e) → VERDE hoy por conservación: sin el campo los derivados no
    cambian (d), y el rechazo de entradas inválidas ya existe como
    rechazo de campos desconocidos (e); quedan como guardias de
    regresión de la decisión (compatibilidad y validación por VALOR, no
    por campo desconocido: tras la implementación, `/etc/hosts`,
    `tests/../secrets` y `""` deben seguir fallando —esta vez por
    validación de private_paths—).

P-1 review-fix 2 (RED 2, paquete 004-002-...-025; hallazgos del review-012
dispuestos por el orquestador 2026-10-02; tras review-fix 1 el campo ya se
acepta y se publica, con estos defectos residuales):
  - (g) R1: el frontmatter de CADA derivado publicado es YAML válido
    (yaml.safe_load; sin PyYAML, chequeo estructural estricto) y bajo
    `permission` hay un mapa con read/edit que niegan la ruta privada —
    hoy cdad-orchestrator.md publica `permission: allow` seguido de hijos
    indentados: YAML inválido (ScannerError).
  - (h) R3: private_paths=['tests/x/'] (barra final) — en los derivados de
    OpenCode, read de tests/x/a.py → deny (paridad con el guard de Claude
    Code, que ya lo deniega). Hoy se emite 'tests/x/' y 'tests/x//**',
    que no matchean nada (veredicto allow).
  - (i) R2ii: guard CC v2, private_paths=['docs/private'] — Glob con
    `path` en el padre y patrón que apunta a la ruta privada
    (path='docs', pattern='private/**') → bloqueado (exit 2), como B4 ya
    bloquea un patrón que apunta a implementación. Control:
    Glob(path='docs', pattern='*.md') → permitido.
  Limitaciones declaradas por el dueño (NO testeadas aquí): Grep sobre la
  carpeta padre y las variantes de entradas glob — grietas aceptadas.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import yaml as _yaml
except ImportError:  # pragma: no cover — PyYAML está en el entorno de tests
    _yaml = None

from test_004_002_t2_bootstrap import (  # noqa: E402
    FEATURE_ID,
    POLICY_FILE,
    SCRIPT,
    state_document,
    write_state,
)
from test_004_002_t5_runtime import (  # noqa: E402
    AGENTS_ENV,
    CLI_ENV,
    GUARD,
    LayoutProject,
    prepare_args,
    published_derived,
    require_derived,
)
from pd10_permission_semantics import verdict  # noqa: E402
from test_opencode_read_map_and_steps import (  # noqa: E402
    RULE_RE,
    frontmatter,
    glob_to_regex,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

SECRET = "tests/secret.local"
GLOB = "docs/private/**"
GLOB_PROBE = "docs/private/x.md"
OTRO = "tests/otro.py"
PRIVATE_FIELD = "private_paths"


def run_guard(root: Path, role: str, tool_name: str,
              tool_input: dict) -> subprocess.CompletedProcess:
    """Guard CC con la forma REAL del JSON de hook (I10/C2) — importado del
    precedente T5 (mismo medio, sin cámaras ajenas)."""
    import os
    env = dict(os.environ)
    env[CLI_ENV] = str(SCRIPT)
    payload = json.dumps({"tool_name": tool_name, "tool_input": tool_input})
    return subprocess.run(
        ["bash", str(GUARD), role],
        input=payload, capture_output=True, text=True,
        cwd=str(root), env=env,
    )


def root_clone(src: Path, tag: str) -> Path:
    """Copia del árbol del proyecto sintético (fixture, NO producto) para
    comparar derivados con y sin el campo (a'/d). Excluye .cdad (identidad
    y paquetes del primer proyecto) y resetea el state para que el clon sea
    bootstrap-elegible como proyecto nuevo."""
    import shutil
    tmp = tempfile.mkdtemp(prefix=f"cdad-p1-red-{tag}-")
    dst = Path(tmp) / "proj"
    shutil.copytree(src, dst,
                    ignore=shutil.ignore_patterns(".git", "__pycache__",
                                                  ".cdad"))
    write_state(dst, state_document())
    return dst


class _P1Base(LayoutProject):
    """Layout del fixture + escritura del campo private_paths."""

    def apply_private(self, root: Path | None, entries: list[str]) -> None:
        target = root or self.root
        doc = json.loads((target / POLICY_FILE).read_text(encoding="utf-8"))
        doc["path_policy"][PRIVATE_FIELD] = list(entries)
        (target / POLICY_FILE).write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")

    def remove_private(self, root: Path | None) -> None:
        target = root or self.root
        doc = json.loads((target / POLICY_FILE).read_text(encoding="utf-8"))
        doc["path_policy"].pop(PRIVATE_FIELD, None)
        (target / POLICY_FILE).write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")

    def prepare_on(self, root: Path, *, role: str = "test-writer",
                   substage: str = "red",
                   objective: str = "P-1 probe"):
        env = dict(os.environ)
        env[AGENTS_ENV] = str(self.agents_src)
        args = prepare_args(root, role=role, substage=substage,
                            objective=objective)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True, text=True, cwd=REPO_ROOT, env=env,
        )


def verdict_maps(root: Path, probes: tuple[str, ...]) -> dict[str, str]:
    """Veredictos read/edit de TODOS los derivados publicados, por sonda."""
    pub = published_derived(root)
    out: dict[str, str] = {}
    for agent, blob in sorted(pub.items()):
        text = blob.decode("utf-8") if isinstance(blob, bytes) else blob
        for tool in ("read", "edit"):
            for probe in probes:
                out[f"{agent}:{tool}:{probe}"] = verdict(text, tool, probe)
    return out


def byte_deriveds(root: Path) -> dict[str, bytes]:
    return {n: (b if isinstance(b, bytes) else b.encode("utf-8"))
            for n, b in published_derived(root).items()}


# ------------------------------------------------------------------- (a)


class TestP1PrivatePathDeriveds(_P1Base):
    """(a) Con private_paths, cada derivado deniega read+edit de la ruta
    privada; el trabajo legítimo hermano sigue permitido (I9)."""
    LAYOUT = "conventional"

    def test_p1_private_path_denied_in_every_derived_agent(self) -> None:
        """(a): con private_paths=["tests/secret.local"], CADA derivado
        publicado resuelve read y edit de la ruta privada como deny
        (precedencia findLast sobre los allow de tests/**), y el hermano
        tests/otro.py sigue allow para el test-writer."""
        self.apply_private(self.root, [SECRET])
        (self.root / SECRET).write_text("fixtures solo\n", encoding="utf-8")
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición prepare: {proc.stdout} {proc.stderr}")
        pub = require_derived(
            self, self.root,
            tuple(n for n in sorted(published_derived(self.root))))
        for n in sorted(pub):
            with self.subTest(derived=n):
                got_read = verdict(pub[n], "read", SECRET)
                got_edit = verdict(pub[n], "edit", SECRET)
                self.assertEqual(
                    got_read, "deny",
                    msg=f"P-1(a): {n} resuelve read({SECRET!r}) como "
                        f"{got_read!r} — la ruta privada debe quedar "
                        f"denegada de lectura para TODOS los roles (I9)")
                self.assertEqual(
                    got_edit, "deny",
                    msg=f"P-1(a): {n} resuelve edit({SECRET!r}) como "
                        f"{got_edit!r} — la ruta privada debe quedar "
                        f"denegada de edición para TODOS los roles (I9)")
        # Control positivo: el trabajo legítimo no cambia.
        self.assertEqual(
            verdict(pub["cdad-test-writer.md"], "read", OTRO), "allow",
            msg="P-1(a): el control tests/otro.py dejó de ser legible para "
                "el test-writer con private_paths (la barrera nueva no "
                "debe restringir trabajo legítimo)")
        self.assertEqual(
            verdict(pub["cdad-test-writer.md"], "edit", OTRO), "allow",
            msg="P-1(a): el control tests/otro.py dejó de ser editable "
                "para el test-writer con private_paths")
        self.assertEqual(
            verdict(pub["cdad-implementer.md"], "edit", "src/app.py"),
            "allow",
            msg="P-1(a): el mapa implementer edit(src/app.py) cambió con "
                "private_paths: el campo no debe restringir trabajo "
                "legítimo")


# ------------------------------------------------------------------ (a')


class TestP1VerdictMapUnchanged(_P1Base):
    """(a') Comparación de mapas: con el campo, TODOS los veredictos
    read/edit por sondas exactas coinciden con la misma política SIN el
    campo, salvo la ruta privada (que pasa a deny en read y edit)."""
    LAYOUT = "conventional"

    def test_p1_other_read_edit_verdicts_unchanged(self) -> None:
        """(a'): publish sin el campo (línea base) y con él (proyecto
        clonado); los veredictos read/edit por sonda exacta coinciden,
        salvo la ruta privada: deny en ambos canales."""
        probes = ("src/app.py", "src/pkg/test_a.py", "tests/test_a.py",
                  OTRO, SECRET)
        base_proc = self.prepare()
        self.assertEqual(
            base_proc.returncode, 0,
            msg=f"precondición base: {base_proc.stdout} {base_proc.stderr}")
        base = byte_deriveds(self.root)
        self.assertTrue(base,
                        msg="precondición: prepare no publicó derivados")
        base_maps = verdict_maps(self.root, probes)

        root2 = root_clone(self.root, "map")
        self.remove_private(root2)  # idempotente: sin el campo en la base
        self.apply_private(root2, [SECRET])
        second = self.prepare_on(root2, objective="P-1 with field")
        self.assertEqual(
            second.returncode, 0,
            msg=f"precondición private_paths: {second.stdout} {second.stderr}")
        got_maps = verdict_maps(root2, probes)
        self.assertEqual(
            sorted(got_maps), sorted(base_maps),
            msg="P-1(a'): los mapas comparados no cubren las mismas "
                "sondas (el clon no publicó los mismos derivados)")

        for key in sorted(base_maps):
            expect = base_maps[key]
            got = got_maps[key]
            _agent, _tool, probe = key.split(":", 2)
            if probe == SECRET:
                self.assertEqual(
                    got, "deny",
                    msg=f"P-1(a'): {key} debe resolver deny con el campo "
                        f"(obtuvo {got!r})")
            else:
                self.assertEqual(
                    got, expect,
                    msg=f"P-1(a'): sin el campo el veredicto era {expect!r} "
                        f"y con él es {got!r} — private_paths no debe "
                        f"restringir trabajo legítimo (única barrera "
                        f"nueva deliberadamente obvia)")


# ------------------------------------------------------------------- (b)


class TestP1PrivateGlobDeriveds(_P1Base):
    """(b) Un glob privado deniega la lectura de sus archivos en TODOS los
    derivados (pd10 findLast: la última regla matcheante gana)."""
    LAYOUT = "conventional"

    def test_p1_private_glob_denied_in_every_derived_agent(self) -> None:
        """(b): con private_paths=["docs/private/**"], cada derivado
        resuelve read de docs/private/x.md como deny."""
        self.apply_private(self.root, [GLOB])
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición prepare: {proc.stdout} {proc.stderr}")
        pub = require_derived(
            self, self.root,
            tuple(n for n in sorted(published_derived(self.root))))
        for n in sorted(pub):
            got = verdict(pub[n], "read", GLOB_PROBE)
            with self.subTest(derived=n):
                self.assertEqual(
                    got, "deny",
                    msg=f"P-1(b): {n} resuelve read({GLOB_PROBE!r}) como "
                        f"{got!r} con el glob privado {GLOB!r} — la "
                        f"lectura debe denegarse para TODOS los roles")

    def test_p1_private_glob_cc_guard_blocks_scoped_path(self) -> None:
        """(b)-CC (decisión del dueño: Grep/Glob cuando el `path` apunta a
        la ruta privada): con private_paths=["docs/private"], un Glob
        acotado a `docs/private/x.md` es DENEGADO por el motivo correcto
        —la regla de ruta privada, no un fallo de clasificación—. Con la
        implementación la política es válida y el guard cita la barrera
        privada; hoy (RED) rc=2 por "unknown fields" (motivo equivocado
        que la implementación corregirá) y la aserción de MOTIVO lo
        demuestra."""
        self.apply_private(self.root, ["docs/private"])
        proc = run_guard(self.root, "test-writer-read", "Glob",
                         {"pattern": "**/*.md", "path": GLOB_PROBE})
        self.assertEqual(
            proc.returncode, 2,
            msg=f"P-1(b)-CC: el guard NO bloqueó el Glob acotado a la "
                f"ruta privada {GLOB_PROBE!r} con private_paths "
                f"['docs/private'] (rc={proc.returncode}) — la decisión "
                f"del dueño exige el bloqueo")
        out = (proc.stdout + proc.stderr).strip()
        self.assertNotIn(
            "unknown fields", out,
            msg=f"P-1(b)-CC: el Glob privado fue bloqueado por el motivo "
                f"EQUIVOCADO (política inválida / campo desconocido) y no "
                f"por la barrera de rutas privadas: {out!r}")


# ------------------------------------------------------------------- (c)


class TestP1CcGuardPrivatePath(_P1Base):
    """(c) Guard CC dinámico (I10/C2): bloquea las operaciones sobre la
    ruta privada y permite el trabajo legítimo del rol. Rama v2 ( Política
    del proyecto)."""
    LAYOUT = "conventional"

    def test_p1_cc_guard_blocks_private_path_and_allows_sibling(self) -> None:
        """(c): con private_paths=["tests/secret.local"], el guard deniega
        (exit 2) Read/Edit/Write/MultiEdit de la ruta privada (relativa y
        absoluta) y permite (exit 0) Read de tests/otro.py; el implementer
        también queda bloqueado sobre la privada (TODOS los roles)."""
        self.apply_private(self.root, [SECRET])
        secret_abs = str(self.root / SECRET)
        cases = (
            ("test-writer-read", "Read", {"file_path": SECRET}, 2,
             "relativo"),
            ("test-writer-read", "Read", {"file_path": secret_abs}, 2,
             "absoluto"),
            ("test-writer-write", "Edit", {"file_path": SECRET}, 2,
             "edit relativo"),
            ("test-writer-write", "Write", {"file_path": SECRET}, 2,
             "write relativo"),
            ("test-writer-write", "MultiEdit", {"file_path": SECRET}, 2,
             "multiEdit relativo"),
            ("test-writer-write", "NotebookEdit", {"file_path": SECRET}, 0,
             "E0 (hallazgo del sondeo): NotebookEdit NO está en ningún "
             "matcher declarado de los hooks CC (agents/claude-code/"
             "cdad-*.md) — el guard nunca la media ni sin el campo; "
             "agregarla sería una ampliación no pedida; se registra el"
             "hallazgo, la decisión de cámara es del orquestador"),
            ("test-writer-read", "Grep",
             {"pattern": "TODO", "path": "tests/secret.local"}, 2,
             "grep path exacto — se deniega por no-clasificable con "
             "política 'inválida'; tras la implementación debe denegar "
             "por la barrera privada"),
            ("test-writer-read", "Glob",
             {"pattern": "*", "path": "tests/secret.local"}, 2,
             "glob path exacto"),
            ("test-writer-read", "Read", {"file_path": OTRO}, 0,
             "control hermano permitido"),
            ("test-writer-write", "Edit", {"file_path": OTRO}, 0,
             "control hermano editable"),
            ("implementer", "Edit", {"file_path": SECRET}, 2,
             "implementer bloqueado"),
        )
        for role, tool, tool_input, expected, label in cases:
            with self.subTest(role=role, tool=tool, case=label):
                proc = run_guard(self.root, role, tool, tool_input)
                self.assertEqual(
                    proc.returncode, expected,
                    msg=f"P-1(c): guard CC {tool}({tool_input}) para "
                        f"{role} → rc={proc.returncode}, esperado "
                        f"{expected} ({label}) — el guard debe bloquear "
                        f"la ruta privada y no frenar el trabajo "
                        f"legítimo; out="
                        f"{(proc.stdout + proc.stderr).strip()!r}")


# ------------------------------------------------------------------- (d)


class TestP1WithoutFieldByteIdentical(_P1Base):
    """(d) Sin el campo private_paths: derivados byte-idénticos entre
    publicaciones equivalentes (compatibilidad: sin el campo el
    comportamiento es idéntico al actual)."""
    LAYOUT = "conventional"

    def test_p1_without_field_deriveds_byte_identical(self) -> None:
        """(d): dos proyectos con el MISMO layout y la política SIN
        private_paths publican derivados byte-idénticos (regresión de
        compatibilidad del campo opcional)."""
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición base: {proc.stdout} {proc.stderr}")
        base = byte_deriveds(self.root)
        self.assertTrue(
            base, msg="precondición: prepare no publicó derivados")

        root2 = root_clone(self.root, "byte")
        second = self.prepare_on(root2, objective="P-1 compatibilidad")
        self.assertEqual(
            second.returncode, 0,
            msg=f"precondición segundo proyecto: {second.stdout} "
                f"{second.stderr}")
        repub = byte_deriveds(root2)
        self.assertEqual(
            sorted(base), sorted(repub),
            msg="P-1(d): el mismo layout sin el campo publicó derivados "
                "con una lista de nombres distinta")
        for name in sorted(base):
            with self.subTest(derived=name):
                self.assertEqual(
                    base[name], repub[name],
                    msg=f"P-1(d): los derivados SIN private_paths no son "
                        f"byte-idénticos ({name} diverge)")


# ------------------------------------------------------------------- (f)
# P-1 review-fix RED (F-P1, hallazgo confirmado por el orquestador contra
# cdad_packet.py ~1999-2033; sonda en vivo review-011): una ruta privada
# SIN glob (p. ej. el directorio 'docs/private') deniega en Claude Code
# (guard _is_private_path) la ruta y TODO su subárbol, pero los derivados
# de OpenCode emiten solo la entrada literal 'docs/private': deny — la
# sonda en vivo demostró que read con {'secrets/sub': 'deny'} NO deniega
# secrets/sub/deep.txt (0 de 20), mientras secret 'secrets/sub/**' sí
# (20 de 20): los runtimes quedan inconsistentes. El caso exigido (F-P1):
# con private_paths=['docs/private'] (sin glob), en cada derivado
# publicado el veredicto findLast (evaluador pd10) de read y edit para
# 'docs/private/x.md' y para 'docs/private' es deny; y la entrada simple
# 'tests/x' NO deniega 'tests/x2' ni 'tests/xy.py' (la entrada exacta
# solo captura su ruta exacta).

PRIVATE_DIR = "docs/private"
PRIVATE_DIR_PROBE = "docs/private/x.md"
PLAIN_ENTRY = "tests/x"
PLAIN_ENTRY_NONMATCH = ("tests/x2", "tests/xy.py")


class TestP1PrivateDirWithoutGlobCoversSubtree(_P1Base):
    """(f) F-P1: private_paths=['docs/private'] (SIN glob) → en cada
    derivado OpenCode, read y edit de 'docs/private/x.md' (subárbol) y de
    'docs/private' (la ruta misma) resuelven deny — la misma cobertura que el guard CC (_is_private_path cubre el
    subárbol), para que ambos runtimes sean consistentes (veredicto
    findLast, evaluador pd10/PD-7/PD-8)."""
    LAYOUT = "conventional"

    def test_p1_private_dir_without_glob_covers_subtree_in_every_derived(
            self) -> None:
        """F-P1: con private_paths=['docs/private'] (sin glob), CADA
        derivado publicado resuelve read y edit de 'docs/private/x.md' y
        de 'docs/private' como deny (findLast, evaluador pdf10/PD-7/PD-8:
        barrera efectiva de rutas privadas con la MISMA cobertura en OpenCode
        que en Claude Code — la sonda review-011 midió 0/20 vs 20/20).

        Control de no-sobre-captura (F-P1): con la entrada simple
        'tests/x', los derivados publicados NO resuelven deny read/edit de
        'tests/x2' ni 'tests/xy.py' para el test-writer: la entrada
        exacta captura únicamente su ruta exacta."""
        # Cobertura del subárbol: ['docs/private'] sin glob.
        self.apply_private(self.root, [PRIVATE_DIR])
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición prepare: {proc.stdout} {proc.stderr}")
        pub = require_derived(
            self, self.root,
            tuple(n for n in sorted(published_derived(self.root))))
        for n in sorted(pub):
            with self.subTest(derived=n):
                for tool, probe in (("read", PRIVATE_DIR_PROBE),
                                    ("edit", PRIVATE_DIR_PROBE),
                                    ("read", PRIVATE_DIR),
                                    ("edit", PRIVATE_DIR)):
                    got = verdict(pub[n], tool, probe)
                    self.assertEqual(
                        got, "deny",
                        msg=f"F-P1: {n} resuelve {tool}({probe!r}) como "
                            f"{got!r} con private_paths={PRIVATE_DIR!r} "
                            f"SIN glob — la entrada de ruta privada debe "
                            f"cubrir la ruta y su subárbol en los derivados "
                            f"de OpenCode, como ya lo hace el guard CC "
                            f"(_is_private_path); veredicto findLast pd10")
        # Control de no-sobre-captura: entrada simple 'tests/x'.
        root2 = root_clone(self.root, "sglob")
        self.remove_private(root2)  # idempotente: base no lleva el campo
        self.apply_private(root2, [PLAIN_ENTRY])
        second = self.prepare_on(root2, objective="F-P1 no sobre-captura")
        self.assertEqual(
            second.returncode, 0,
            msg=f"precondición control 'tests/x': {second.stdout} "
                f"{second.stderr}")
        got2 = require_derived(self, root2, ("cdad-test-writer.md",))[
            "cdad-test-writer.md"]
        for probe in PLAIN_ENTRY_NONMATCH:
            for tool in ("read", "edit"):
                with self.subTest(control=probe, tool=tool):
                    verdict_got = verdict(got2, tool, probe)
                    self.assertEqual(
                        verdict_got, "allow",
                        msg=f"F-P1: la entrada simple {PLAIN_ENTRY!r} "
                            f"sobre-capturó {tool}({probe!r}): resolvió "
                            f"{verdict_got!r} y debe ser allow para el "
                            f"test-writer (la entrada exacta no debe "
                            f"denegar rangos hermanos)")


# ------------------------------------------------------------------- (e)


class TestP1InvalidEntries(unittest.TestCase):
    """(e) Entradas inválidas (absoluta, con "..", vacía) → error de
    validación de la política (rc≠0), como las demás raíces (PD-2)."""

    def _policy_with_private(self, entries: list) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="cdad-p1-red-"))
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(tmp)],
                                               check=False))
        root = tmp / "proj"
        (root / "docs").mkdir(parents=True)
        (root / "docs" / "specs" / FEATURE_ID).mkdir(parents=True)
        (root / "tests").mkdir()
        doc = {"schema_version": 1,
               "path_policy": {
                   "test_roots": ["tests"],
                   "implementation_roots": ["src", "lib"],
                   "documentation_roots": ["docs"],
                   PRIVATE_FIELD: entries,
               },
               "temporary_roots": [".cdad/tmp"]}
        (root / POLICY_FILE).write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return root

    def test_p1_invalid_private_entries_rejected(self) -> None:
        """(e): entrada absoluta / con `..` / vacía → validate-policy rc≠0
        con diagnóstico (sin traceback); y prepare (usa la política) no
        publica paquete (rc≠0: la política inválida impide preparar)."""
        for label, entries in (
            ("absoluta", ["/etc/hosts"]),
            ("con dos puntos", ["tests/../secrets"]),
            ("vacía", [""]),
        ):
            with self.subTest(entry=label):
                root = self._policy_with_private(entries)
                proc = subprocess.run(
                    [sys.executable, str(SCRIPT), "validate-policy",
                     "--project-root", str(root)],
                    capture_output=True, text=True, cwd=REPO_ROOT)
                out = proc.stdout + proc.stderr
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"P-1(e) [{label}]: validate-policy aceptó la "
                        f"entrada inválida {entries!r}")
                self.assertNotIn(
                    "Traceback", out,
                    msg=f"P-1(e) [{label}]: fallo con traceback: {out!r}")
                self.assertTrue(
                    out.strip(),
                    msg=f"P-1(e) [{label}]: rc≠0 sin diagnóstico")
                prep = subprocess.run(
                    [sys.executable, str(SCRIPT), "prepare",
                     "--project-root", str(root),
                     "--role", "test-writer", "--substage", "red",
                     "--objective", "P-1 invalid probe"],
                    capture_output=True, text=True, cwd=REPO_ROOT)
                self.assertNotEqual(
                    prep.returncode, 0,
                    msg=f"P-1(e) [{label}]: prepare aceptó la política "
                        f"con la entrada inválida")
                self.assertEqual(
                    prep.stdout, "",
                    msg=f"P-1(e) [{label}]: el prepare con política "
                        f"inválida imprimió un paquete")


# --------------------------------------------------- (g)-(i) review-fix 2
# P-1 review-fix 2 (RED 2): hallazgos del review-012 (glm-5.3-flash)
# dispuestos por el orquestador (2026-10-02). Tras review-fix 1 el campo
# `private_paths` ya se acepta y se publica; estos son los defectos
# residuales, cada uno una postcondición observable de PD-7/PD-8 (barreras
# efectivas de rutas privadas en los mecanismos que realmente median).
#
# Helpers de YAML: el oráculo de R1 es yaml.safe_load cuando PyYAML está
# disponible en el entorno de tests; sin PyYAML, un chequeo estructural
# estricto que rechaza la forma inválida publicada hoy (`permission:
# <escalar>` seguido de hijos indentados) y extrae read/edit con las
# reglas declaradas (mismas regex de tests/test_opencode_read_map_and_steps.py,
# reutilizadas — nada reimplementa la evaluación).

R3_ENTRY = "tests/x/"
R3_PROBE = "tests/x/a.py"


def _permission_of(derived_text: str) -> dict:
    """Valor de `permission` del frontmatter del derivado, parseado como
    YAML (yaml.safe_load con PyYAML; chequeo estructural estricto sin
    PyYAML). Lanza AssertionError con diagnóstico si el frontmatter no es
    YAML válido o si `permission` no es un mapa."""
    fm = frontmatter(derived_text)
    if not fm.startswith("---\n"):
        raise AssertionError(
            f"P-1(g)/R1: frontmatter sin delimitador '---' inicial: "
            f"{fm[:80]!r}")
    body = fm[len("---\n"):]
    if _yaml is not None:
        try:
            data = _yaml.safe_load(body)
        except _yaml.YAMLError as exc:
            raise AssertionError(
                f"P-1(g)/R1: el frontmatter publicado NO es YAML válido "
                f"(yaml.safe_load): {exc}") from exc
        if not isinstance(data, dict):
            raise AssertionError(
                f"P-1(g)/R1: el frontmatter no parsea a un mapa YAML: "
                f"{type(data).__name__}")
        if "permission" not in data:
            raise AssertionError(
                "P-1(g)/R1: el frontmatter no declara 'permission'")
        perm = data["permission"]
        if not isinstance(perm, dict):
            raise AssertionError(
                f"P-1(g)/R1: 'permission' no es un mapa bajo el frontmatter "
                f"YAML válido: {type(perm).__name__}")
        return perm
    # Sin PyYAML: chequeo estructural estricto de la forma inválida hoy.
    lines = body.splitlines()
    idx = next((i for i, l in enumerate(lines)
                if re.match(r"^permission:(:.*)?$", l)), None)
    if idx is None:
        raise AssertionError("P-1(g)/R1: el frontmatter no declara "
                             "'permission'")
    inline = re.match(r"^permission:[ \t]+(\S+)[ \t]*$", lines[idx])
    if inline:
        for l in lines[idx + 1:]:
            if l and not l.startswith(" "):
                break
            if l.startswith(" "):
                raise AssertionError(
                    f"P-1(g)/R1: `permission: {inline.group(1)}` escalar "
                    f"seguido de hijos indentados (YAML inválido): {l!r}")
        return {"read": inline.group(1), "edit": inline.group(1)}
    perm: dict = {}
    for tool in ("read", "edit"):
        try:
            t_idx = next(i for i, l in enumerate(lines)
                         if l == f"  {tool}:")
        except StopIteration:
            if re.search(rf"^  {tool}:[ \t]+(allow|deny)[ \t]*$",
                         body, re.M):
                perm[tool] = re.search(
                    rf"^  {tool}:[ \t]+(allow|deny)[ \t]*$", body, re.M
                ).group(1)
            continue
        rules: list[tuple[str, str]] = []
        for l in lines[t_idx + 1:]:
            if l and not l.startswith("    "):
                break
            if (m := RULE_RE.search(l)):
                rules.append((m.group(1), m.group(2)))
        perm[tool] = rules
    return perm


def _perm_verdict(perm: dict, tool: str, probe: str) -> str:
    """Veredicto findLast de `tool` para `probe` sobre el mapa `permission`
    YA PARSEADO como YAML (el oráculo de R1; misma semántica findLast del
    evaluador pd10, aplicada a la estructura parseada)."""
    rules = perm.get(tool)
    if rules is None:
        return "allow"
    if isinstance(rules, str):
        return rules
    out = "allow"
    items = rules.items() if isinstance(rules, dict) else rules
    for pattern, verb in items:
        if re.fullmatch(glob_to_regex(pattern), probe):
            out = verb
    return out


class TestP1Rf2DerivedFrontmatterValidYaml(_P1Base):
    """(g) R1 (review-012, dispuesto): con private_paths declarado, el
    frontmatter de CADA derivado publicado —incluido cdad-orchestrator.md,
    cuyo origen declara `permission: allow` escalar— es YAML válido, y bajo
    `permission` hay un mapa con read/edit que niegan la ruta privada
    (PD-7/PD-8: barrera efectiva declarada y consumible por el runtime)."""
    LAYOUT = "conventional"

    def test_p1_rf2_yaml_valid_and_permission_map_denies_private(self) -> None:
        """(g) R1: cada derivado publicado con private_paths parsea con
        yaml.safe_load; `permission` es un mapa con read/edit cuyo veredicto
        findLast para la ruta privada es deny. Hoy el orquestador publica
        `permission: allow` + hijos indentados (YAML inválido)."""
        self.apply_private(self.root, [SECRET])
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición prepare: {proc.stdout} {proc.stderr}")
        pub = require_derived(
            self, self.root,
            tuple(n for n in sorted(published_derived(self.root))))
        self.assertIn(
            "cdad-orchestrator.md", pub,
            msg="precondición: el derivado del orquestador (origen con "
                "`permission: allow` escalar) no fue publicado")
        for name in sorted(pub):
            with self.subTest(derived=name):
                perm = _permission_of(pub[name])  # AssertionError con R1
                for tool in ("read", "edit"):
                    got = _perm_verdict(perm, tool, SECRET)
                    self.assertEqual(
                        got, "deny",
                        msg=f"P-1(g)/R1: {name} — bajo 'permission' "
                            f"YAML-válido, {tool}({SECRET!r}) resuelve "
                            f"{got!r}; el mapa permission debe negar la "
                            f"ruta privada en read y edit para TODOS los "
                            f"roles")


class TestP1Rf2TrailingSlashPrivatePath(_P1Base):
    """(h) R3 (review-012, dispuesto): private_paths=['tests/x/'] con barra
    final — en los derivados de OpenCode, read del archivo bajo la carpeta
    → deny, con paridad con el guard de Claude Code (que ya lo deniega,
    sondeado en vivo: rc 2). Hoy se emiten 'tests/x/' y 'tests/x//**',
    que no matchean nada."""
    LAYOUT = "conventional"

    def test_p1_rf2_trailing_slash_denied_in_opencode_deriveds(self) -> None:
        """(h) R3: con private_paths=['tests/x/'], CADA derivado publicado
        resuelve read de 'tests/x/a.py' como deny (la entrada con barra
        final cubre su subárbol, igual que el guard CC)."""
        self.apply_private(self.root, [R3_ENTRY])
        (self.root / "tests/x").mkdir(parents=True, exist_ok=True)
        (self.root / R3_PROBE).write_text("fixture\n", encoding="utf-8")
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición prepare: {proc.stdout} {proc.stderr}")
        pub = require_derived(
            self, self.root,
            tuple(n for n in sorted(published_derived(self.root))))
        for n in sorted(pub):
            got = verdict(pub[n], "read", R3_PROBE)
            with self.subTest(derived=n):
                self.assertEqual(
                    got, "deny",
                    msg=f"P-1(h)/R3: {n} resuelve read({R3_PROBE!r}) como "
                        f"{got!r} con private_paths={['tests/x/']!r} "
                        f"(barra final) — la entrada con barra final debe "
                        f"denegar la lectura de su subárbol en los "
                        f"derivados de OpenCode, en paridad con el guard "
                        f"de Claude Code")


class TestP1Rf2CcGuardGlobIntoPrivateParent(_P1Base):
    """(i) R2ii (review-012, dispuesto): guard CC v2 con
    private_paths=['docs/private'] — un Glob cuyo patrón apunta a la ruta
    privada aunque el `path` sea el padre ('docs' + 'private/**') queda
    BLOQUEADO (exit 2), igual que B4 ya bloquea un patrón que apunta a
    implementación. Control: 'docs' + '*.md' → permitido."""
    LAYOUT = "conventional"

    def test_p1_rf2_cc_guard_blocks_glob_pattern_into_private(self) -> None:
        """(i) R2ii: Glob(path='docs', pattern='private/**') → exit 2 con
        private_paths=['docs/private']; control Glob(path='docs',
        pattern='*.md') → exit 0. (Limitación declarada por el dueño, NO
        testuada: Grep sobre la carpeta padre.)"""
        self.apply_private(self.root, [PRIVATE_DIR])
        blocked = run_guard(self.root, "test-writer-read", "Glob",
                            {"pattern": "private/**", "path": "docs"})
        self.assertEqual(
            blocked.returncode, 2,
            msg="P-1(i)/R2ii: el guard NO bloqueó el Glob con patrón "
                "apuntando a la ruta privada (path='docs', "
                "pattern='private/**') con "
                f"private_paths={['docs/private']!r} "
                f"(rc={blocked.returncode}) — igual que B4 bloquea un "
                f"patrón que apunta a implementación; "
                f"out={(blocked.stdout + blocked.stderr).strip()!r}")
        control = run_guard(self.root, "test-writer-read", "Glob",
                            {"pattern": "*.md", "path": "docs"})
        self.assertEqual(
            control.returncode, 0,
            msg="P-1(i)/R2ii: el control legítimo Glob(pattern='*.md', "
                f"path='docs') fue bloqueado (rc={control.returncode}) — "
                "la barrera no debe frenar el trabajo legítimo")


if __name__ == "__main__":
    unittest.main(verbosity=2)
