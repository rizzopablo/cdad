#!/usr/bin/env python3
"""Propiedades de T7 — 010-002-documentary-role-integration.

Contrato: ``docs/specs/010-002-documentary-role-integration/spec.md`` v4
(sha256 ``0d630c49…81abc``). Este módulo cubre la parte generable de INV-04
(§5) y el recorrido integrado final de PC-12.b (§4, EV-04/EV-05). No es un
RED de implementación: el comportamiento de T6 está GREEN (commit
``a09f830a``) y estos verificadores agregan cobertura propia; si algo falla,
se reporta como hallazgo y no se corrige desde tests.

Registro de la subfase de propiedades (plan T7)
-----------------------------------------------
- **Semilla fija:** ``SEED = 20261031``. El generador es propio y
  determinista (``random.Random``); no se exige ``hypothesis`` ni otra
  biblioteca de propiedades (plan T7: «sin biblioteca concreta obligatoria»).
- **Dominio de publicación:** los cinco roles que reciben paquete en el
  procedimiento —``architect/draft``, ``test-writer/red``,
  ``implementer/green``, ``reviewer/review`` y ``scribe/memory``—. El
  orquestador prepara, coordina y verifica gates; no recibe trabajo de rol
  inline (spec §3), por lo que no es destinatario de una publicación.
- **Dominio de ``stack``:** ausente, ``null``, cadena vacía, ``"odoo"`` y
  sufijos no vacíos generados sobre ``[a-z][a-z0-9-]{0,9}`` (D3: cualquier
  cadena no vacía deriva ``cdad-<role>-<stack>``; ausente/``null``/vacía
  derivan ``cdad-<role>``).
- **Presupuesto:** 100 publicaciones válidas (20 de frontera —5 roles × 4
  representaciones— + 80 generadas); 100 discordancias estáticas + 20
  admisiones estáticas (5 roles × 4 formas de sufijo), más 5 comprobaciones
  de no publicación de ``render`` (una por rol); 100 discordancias
  contextuales de intento nuevo (10 bases publicadas: 5 roles × 2 stacks);
  y la regla de presencia sobre los 5 roles. No se usa combinatoria para
  perseguir cobertura: el objetivo es la invariante (packet T7).

Oráculo
-------
Todo se deriva del contrato y de los helpers públicos ya existentes
(``tests/test_010_002_documentary_role_integration.py`` y
``tests/test_packet_prepare.py``): derivación canónica (spec §2 D3), contraste
estático de rol sin consultar ``stack`` (D3/PC-07b), contraste contextual del
intento nuevo (D3/PC-07c), regla de presencia ``execution_context`` ⇒
``agent`` (D3/PC-08) y exclusión de ``agent`` del render (D3/PC-08). No se lee
implementación para fijar el resultado esperado.

Recorrido integrado final (PC-12.b, O5)
---------------------------------------
Generación (``make agents`` en la copia descartable) → instalación aislada con
``CDAD_INSTALL_ROOT`` propio y ``CDAD_SKILL_EXTRA_DIRS=""`` → preparación con
el CLI instalado → resolución por ``validate-request``/``record-dispatch`` y
presencia del agente en ambos destinos instalados. La fuente de comparación es
el repositorio (bytes de ``skills/cdad-cycle``) y los agentes promovidos de la
copia descartable; **nunca** ``build/staging`` del checkout.

Aislamiento y límites honestos (PD-15)
--------------------------------------
``tests/conftest.py`` fija ``HOME``/XDG/temporales por test y retira los
overrides heredados. Un canario compara el inventario del ``HOME`` visible
antes y después de la instalación y del recorrido: las operaciones no escriben
el ``HOME`` del proceso ni la instalación global. El ``HOME`` real del
operador queda fuera del alcance del proceso de tests: la sustitución por
``conftest.py`` es la evidencia de aislamiento, no una observación directa de
esa ruta. Un verde aquí **no** acredita fidelidad semántica, suficiencia de
una exclusión ni conducta efectiva de modelos (PC-13, T8); tampoco un sandbox.
"""

from __future__ import annotations

import atexit
import hashlib
import json
import os
import random
import shutil
import string
import subprocess
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

try:  # Motor real de JSON Schema (AUDIT §10 R6). Su ausencia es bloqueo de
    # entorno, no defecto del producto: el test se declara omitido con causa.
    import jsonschema
except ImportError:  # pragma: no cover - entorno sin el motor
    jsonschema = None

from tests.product_staging import run_scoped_base
from tests.test_006_004_u3_principle_single_source import disposable_product
from tests.test_010_001_documentary_contracts import (
    INSTALLED_AGENTS_DIRS,
    PROMOTED_DIRS,
    RUNTIMES,
)
from tests.test_010_002_documentary_role_integration import (
    AgentBindingCase,
    CANONICAL_PACKETS,
    SKILL_ROOTS,
)
from tests.test_packet_prepare import PACKET_CLI, PrepareProject, run_prepare
from tests.test_role_packet_render import parse_packet


REPO_ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Registro de la subfase (semilla, dominio y presupuesto).
# ---------------------------------------------------------------------------

SEED = 20261031

BUDGET_PUBLICATIONS = 100
BUDGET_STATIC_MISMATCH = 100
BUDGET_STATIC_ADMISSION = 20
BUDGET_CONTEXTUAL = 100
BUDGET_PRESENCE = 5

ROLE_CASES = (
    ("architect", "draft"),
    ("test-writer", "red"),
    ("implementer", "green"),
    ("reviewer", "review"),
    ("scribe", "memory"),
)

# Representaciones de frontera de D3 (ausente, null, vacía y sufijo no vacío).
BOUNDARY_STACKS = (
    ("ausente", None, True),
    ("null", None, False),
    ("vacía", "", False),
    ("sufijo 'odoo'", "odoo", False),
)

# Stacks vigentes de las bases contextuales (agente publicado no genérico).
CONTEXTUAL_STACKS = ("odoo", "erp-x")

# Los seis roles del contrato (§3); el orquestador no recibe paquete, pero es
# una familia de agente actual y se usa como discordancia estática de rol.
CURRENT_ROLES = (
    "architect",
    "test-writer",
    "implementer",
    "reviewer",
    "scribe",
    "orchestrator",
)

SUFFIX_ALPHABET = string.ascii_lowercase + string.digits + "-"

CLI_SOURCE = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
SCHEMA_SOURCE = (
    REPO_ROOT / "skills" / "cdad-cycle" / "assets" / "packet-request.schema.json"
)


# ---------------------------------------------------------------------------
# Temporales estables de módulo (las publicaciones se comparten entre tests).
# ---------------------------------------------------------------------------

def _stable_mkdtemp(prefix: str) -> Path:
    path = tempfile.mkdtemp(prefix=prefix, dir=str(run_scoped_base()))
    atexit.register(shutil.rmtree, path, True)
    return Path(path)


# ---------------------------------------------------------------------------
# Generadores deterministas.
# ---------------------------------------------------------------------------

def canonical_agent(role: str, stack: object, absent: bool = False) -> str:
    """Derivación canónica de D3: genérica para ausente/null/vacía."""
    if absent or stack is None or stack == "":
        return f"cdad-{role}"
    return f"cdad-{role}-{stack}"


def generated_suffix(rng: random.Random) -> str:
    """Sufijo no vacío sobre el dominio declarado: letra + [a-z0-9-]{0,9}."""
    length = rng.randint(1, 10)
    return rng.choice(string.ascii_lowercase) + "".join(
        rng.choice(SUFFIX_ALPHABET) for _ in range(length - 1)
    )


def _case_plan() -> list[tuple[str, str, object, bool, str]]:
    """20 casos de frontera (5 roles × 4 representaciones) + 80 generados."""
    plan: list[tuple[str, str, object, bool, str]] = []
    for role, substage in ROLE_CASES:
        for label, stack, absent in BOUNDARY_STACKS:
            plan.append((role, substage, stack, absent, label))
    rng = random.Random(SEED)
    while len(plan) < BUDGET_PUBLICATIONS:
        role, substage = rng.choice(ROLE_CASES)
        draw = rng.random()
        if draw < 0.10:
            stack, absent, label = None, True, "ausente"
        elif draw < 0.20:
            stack, absent, label = None, False, "null"
        elif draw < 0.30:
            stack, absent, label = "", False, "vacía"
        elif draw < 0.40:
            stack, absent, label = "odoo", False, "sufijo 'odoo'"
        else:
            suffix = generated_suffix(rng)
            stack, absent, label = suffix, False, f"sufijo {suffix!r}"
        plan.append((role, substage, stack, absent, label))
    return plan


def _set_stack(project: PrepareProject, stack: object, absent: bool) -> None:
    state = json.loads(project.state_path.read_text(encoding="utf-8"))
    if absent:
        state.pop("stack", None)
    else:
        state["stack"] = stack
    project.pre_state = state
    project.state_path.write_text(
        json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _canonical_argv(project: PrepareProject, objective: str) -> list[str]:
    """Argv de preparación ordinaria en la ruta canónica de paquetes."""
    argv = list(project.args(objective=objective))
    index = argv.index("--out-dir")
    del argv[index : index + 2]
    return argv


def _publish(
    project: PrepareProject, objective: str, label: str
) -> tuple[str, Path]:
    """Publica y devuelve ``(packet_id, packet_dir)`` o falla con la PC."""
    result = run_prepare(PACKET_CLI, *_canonical_argv(project, objective))
    if result.returncode != 0:
        raise AssertionError(
            "INV-04/PC-06 violada: una entrada admitida (rol/subfase y stack de "
            f"D3) no publicó su paquete; caso {label}: rc={result.returncode}: "
            + result.stderr.decode(errors="replace")[-1200:]
        )
    state = json.loads(project.state_path.read_text(encoding="utf-8"))
    packet_id = str((state.get("active_packet") or {}).get("id") or "")
    if not packet_id:
        raise AssertionError(
            "INV-04: `prepare` no registró `active_packet`; caso " + label
        )
    packet_dir = project.root / CANONICAL_PACKETS / packet_id
    if not (packet_dir / "REQUEST.json").is_file():
        raise AssertionError(
            "INV-04: `prepare` no publicó el request en la ruta canónica "
            f"(`{packet_dir / 'REQUEST.json'}`); caso {label}"
        )
    return packet_id, packet_dir


@dataclass
class GeneratedPublication:
    label: str
    role: str
    substage: str
    stack: object
    stack_absent: bool
    stack_label: str
    expected_agent: str
    objective: str
    project: PrepareProject
    packet_id: str
    packet_dir: Path
    request: dict
    packet_bytes: bytes


_PUBLICATIONS: list[GeneratedPublication] | None = None


def generated_publications() -> list[GeneratedPublication]:
    """Publicaciones generadas una vez y compartidas por las propiedades."""
    global _PUBLICATIONS
    if _PUBLICATIONS is None:
        publications: list[GeneratedPublication] = []
        for index, (
            role,
            substage,
            stack,
            absent,
            stack_label,
        ) in enumerate(_case_plan()):
            project = PrepareProject(
                _stable_mkdtemp("cdad-010-002-prop-"), role, substage
            )
            _set_stack(project, stack, absent)
            label = f"caso {index:03d}: {role}/{substage}, stack {stack_label}"
            objective = f"INV-04: {role}/{substage} stack {stack_label}"
            packet_id, packet_dir = _publish(project, objective, label)
            request = json.loads(
                (packet_dir / "REQUEST.json").read_text(encoding="utf-8")
            )
            publications.append(
                GeneratedPublication(
                    label=label,
                    role=role,
                    substage=substage,
                    stack=stack,
                    stack_absent=absent,
                    stack_label=stack_label,
                    expected_agent=canonical_agent(role, stack, absent),
                    objective=objective,
                    project=project,
                    packet_id=packet_id,
                    packet_dir=packet_dir,
                    request=request,
                    packet_bytes=(packet_dir / "PACKET.md").read_bytes(),
                )
            )
        _PUBLICATIONS = publications
    return _PUBLICATIONS


def _role_bases() -> dict[str, GeneratedPublication]:
    """Una publicación con ``stack: null`` por rol (frontera de D3)."""
    bases = {
        case.role: case
        for case in generated_publications()
        if case.stack_label == "null"
    }
    expected = {role for role, _ in ROLE_CASES}
    if set(bases) != expected:
        raise AssertionError(
            "fixture de propiedades: faltan bases genéricas por rol: "
            f"{sorted(expected - set(bases))}"
        )
    return bases


_CONTEXTUAL_BASES: dict[tuple[str, str], tuple[PrepareProject, str, Path]] | None = (
    None
)


def contextual_bases() -> dict[tuple[str, str], tuple[PrepareProject, str, Path]]:
    """Bases publicadas con agente no genérico (5 roles × 2 stacks)."""
    global _CONTEXTUAL_BASES
    if _CONTEXTUAL_BASES is None:
        bases: dict[tuple[str, str], tuple[PrepareProject, str, Path]] = {}
        for role, substage in ROLE_CASES:
            for stack in CONTEXTUAL_STACKS:
                project = PrepareProject(
                    _stable_mkdtemp("cdad-010-002-prop-ctx-"), role, substage
                )
                _set_stack(project, stack, False)
                label = f"base contextual {role}/{substage}, stack {stack!r}"
                packet_id, packet_dir = _publish(
                    project,
                    f"INV-04 contextual: {role}/{substage} stack {stack}",
                    label,
                )
                bases[(role, stack)] = (project, packet_id, packet_dir)
        _CONTEXTUAL_BASES = bases
    return _CONTEXTUAL_BASES


def _foreign_agent(rng: random.Random, role: str) -> str:
    """Agente que no pertenece a la familia estática de ``role`` (D3)."""
    foreign_roles = [item for item in CURRENT_ROLES if item != role]
    category = rng.randrange(5)
    if category == 0:
        return f"cdad-{rng.choice(foreign_roles)}"
    if category == 1:
        return f"cdad-{rng.choice(foreign_roles)}-{generated_suffix(rng)}"
    if category == 2:  # coincidencia parcial: nombre del rol truncado
        return f"cdad-{role}"[:-1]
    if category == 3:  # coincidencia parcial: carácter extra
        return f"cdad-{role}x"
    return f"cdad-{role}-"  # prefijo completo con sufijo vacío (inválido)


# ---------------------------------------------------------------------------
# Helpers del recorrido integrado final (PC-12.b).
# ---------------------------------------------------------------------------

def _run(cli: Path, *args: str, cwd: Path, env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(cli), *args],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        check=False,
    )


def home_inventory() -> dict[str, str]:
    """Digests del HOME visible para el proceso (aislado por conftest)."""
    home = Path(os.environ["HOME"])
    inventory: dict[str, str] = {}
    for path in sorted(home.rglob("*")):
        relpath = str(path.relative_to(home))
        if path.is_file():
            inventory[relpath] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            inventory[relpath + "/"] = "<dir>"
    return inventory


def _isolated_env(base: dict) -> dict:
    """Entorno del proceso hijo con el HOME/XDG aislado de la corrida.

    Se parte del entorno **vigente** para que ``TMPDIR`` apunte a la raíz del
    test que ejecuta el proceso (no a una raíz ya retirada, p. ej. la del test
    que construyó la copia descartable) y se sustituyen solo las rutas de
    usuario. Se retiran los overrides AJ2 heredados.
    """
    env = os.environ.copy()
    for key in (
        "HOME",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "XDG_STATE_HOME",
        "XDG_CACHE_HOME",
        "XDG_RUNTIME_DIR",
    ):
        value = base.get(key)
        if isinstance(value, str):
            env[key] = value
    for key in (
        "CDAD_INSTALL_ROOT",
        "CDAD_SKILL_EXTRA_DIRS",
        "CDAD_OPENCODE_AGENTS_DIR",
    ):
        env.pop(key, None)
    return env


_INSTALL_BUNDLE: dict[str, object] | None = None
_HOME_BASELINE: dict[str, str] | None = None


def final_install_bundle() -> dict[str, object]:
    """Instalación aislada propia, una vez por proceso.

    Toma el inventario del HOME **antes** de instalar, de modo que el canario
    de EV-05 cubra la instalación misma (no solo lo que ocurre después de una
    caché de otro módulo). ``CDAD_INSTALL_ROOT`` propio y
    ``CDAD_SKILL_EXTRA_DIRS`` vacío; ``HOME``/XDG son los de la copia
    descartable sembrada por ``disposable_product()``.
    """
    global _INSTALL_BUNDLE, _HOME_BASELINE
    if _HOME_BASELINE is None:
        _HOME_BASELINE = home_inventory()
    if _INSTALL_BUNDLE is None:
        disposable = disposable_product()
        product = disposable["product"]
        assert isinstance(product, Path)
        home_env = dict(disposable["env"])  # type: ignore[arg-type]
        env = _isolated_env(home_env)
        install_root = _stable_mkdtemp("cdad-010-002-prop-install-")
        env["CDAD_INSTALL_ROOT"] = str(install_root)
        env["CDAD_SKILL_EXTRA_DIRS"] = ""
        run = subprocess.run(
            ["bash", str(product / "install.sh")],
            cwd=str(product),
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        _INSTALL_BUNDLE = {
            "product": product,
            "install_root": install_root,
            "home_env": home_env,
            "run": run,
        }
    return _INSTALL_BUNDLE


def observation_document(session: str) -> dict:
    return {
        "runtime": "opencode",
        "model_configured": "glm-5.3-flash",
        "model_reported": "glm-5.3-flash",
        "started_at": "2026-10-31T00:00:00Z",
        "session": session,
        "provenance": {
            "runtime": "reported by runtime",
            "model_reported": "orchestrator",
            "session": "orchestrator",
        },
    }


def _inside(path: str, root: str) -> bool:
    return path == root or path.startswith(root.rstrip("/") + "/")


# ===========================================================================
# (INV-04) Propiedades generadas — parte comprobable del destinatario.
# ===========================================================================


class TestInv04Properties(AgentBindingCase):
    """INV-04 (§5): coherencia rol/stack/agente y conservación del request.

    Semilla ``SEED = 20261031``; dominio y presupuesto declarados en el
    docstring del módulo. Sin estos tests, una combinación admitida podría
    publicar un agente incoherente, la validación compartida podría aceptar una
    familia de otro rol, el registro de un intento nuevo podría despachar a un
    dominio que ya no rige, o la regla de presencia podría romper históricos
    legítimos o admitir contexto sin destinatario.
    """

    # -- derivación y aceptación en la misma vía -------------------------

    def test_publication_derivation_matches_the_canonical_rule(self) -> None:
        """INV-04/PC-06/PC-07a (garantía por construcción): para cada una de
        las 100 entradas válidas generadas, la publicación ordinaria deriva el
        agente canónico de D3 y el mismo request valida por la vía compartida.

        Sin este test, una combinación admitida (rol/subfase y stack) podría
        publicar un destinatario que no corresponde al rol o al dominio, y el
        usuario no sabría a qué agente se publicó su encargo.
        """
        cases = generated_publications()
        self.assertEqual(len(cases), BUDGET_PUBLICATIONS)

        for case in cases:
            with self.subTest(case=case.label):
                self.assertEqual(
                    case.request.get("agent"),
                    case.expected_agent,
                    msg="INV-04/PC-06 violada: la publicación debe derivar el "
                    "agente canónico del rol y del stack vigente (D3). "
                    f"{case.label}: esperado {case.expected_agent!r}, vio "
                    f"{case.request.get('agent')!r}",
                )
                context = case.request.get("execution_context")
                self.assertIsInstance(
                    context,
                    str,
                    msg="INV-04/PC-06 violada: toda publicación nueva declara "
                    f"`execution_context` textual; {case.label}: vio {context!r}",
                )
                self.assertTrue(
                    context.strip(),
                    msg="INV-04: `execution_context` no puede ser vacío "
                    f"({case.label})",
                )
                self.assertFalse(
                    Path(context).is_absolute(),
                    msg="INV-04: `execution_context` es el localizador "
                    f"canónico relativo, no una ruta absoluta ({case.label}): "
                    f"{context!r}",
                )
                self.assertTrue(
                    context.endswith("/execution.json"),
                    msg="INV-04: `execution_context` debe nombrar el documento "
                    f"canónico de la ejecución ({case.label}): {context!r}",
                )

                validation = self.validate(
                    case.project, case.packet_dir / "REQUEST.json"
                )
                self.assertEqual(
                    validation.returncode,
                    0,
                    msg="INV-04/PC-07a violada: el agente derivado por la "
                    "publicación no valida en la misma vía que publica; "
                    f"{case.label}: "
                    + validation.stderr.decode(errors="replace")[-1200:],
                )

    # -- conservación del request y del render ---------------------------

    def test_publication_conserves_the_admitted_request_and_render_fields(
        self,
    ) -> None:
        """INV-04/PC-08 (conservación): para cada una de las 100 entradas
        válidas generadas, el request publicado conserva los campos que ya
        tenía (ninguno se pierde y el conjunto solo crece con
        ``agent``/``execution_context``), los campos declarados por el fixture
        y el contrato conservan su valor, y el render publicado no contiene el
        campo ``agent``.

        ``invariants``, ``expected_output``, ``evidence_required`` y los
        alcances son derivaciones de ``prepare`` por rol (su oráculo exacto es
        ``test_packet_prepare::test_p2``, control ya verde): aquí se conserva
        su presencia y su forma, no un valor del fixture que ``prepare``
        sustituye por diseño.

        Sin este test, la corrección podría haber perdido o cambiado campos del
        request existente, o un campo de transporte podría entrar al render y
        romper la compatibilidad de bytes entre requests válidos.
        """
        cases = generated_publications()
        self.assertEqual(len(cases), BUDGET_PUBLICATIONS)

        preserved_values = (
            "schema_version",
            "execution_id",
            "feature_id",
            "role",
            "substage",
            "contract",
            "inputs",
        )
        preserved_shape = {
            "read_scope": list,
            "write_scope": list,
            "invariants": list,
            "expected_output": str,
            "evidence_required": list,
        }

        for case in cases:
            with self.subTest(case=case.label):
                published = case.request
                fixture_request = case.project.fixture.request

                self.assertEqual(
                    set(published),
                    set(fixture_request) | {"agent", "execution_context"},
                    msg="INV-04 violada: el request publicado no conserva el "
                    "conjunto de campos admitido (creció con un campo que no es "
                    f"`agent`/`execution_context`); {case.label}: "
                    f"{sorted(set(published) ^ (set(fixture_request) | {'agent', 'execution_context'}))}",
                )
                for key in preserved_values:
                    self.assertEqual(
                        published.get(key),
                        fixture_request.get(key),
                        msg="INV-04 violada: el request publicado alteró o "
                        f"perdió el campo declarado {key!r}; {case.label}",
                    )
                for key, expected_type in preserved_shape.items():
                    self.assertIsInstance(
                        published.get(key),
                        expected_type,
                        msg="INV-04 violada: el campo preexistente "
                        f"{key!r} perdió su forma ({expected_type.__name__}); "
                        f"{case.label}: {published.get(key)!r}",
                    )
                self.assertEqual(
                    published.get("packet_id"),
                    case.packet_id,
                    msg="INV-04: el request publicado debe nombrar el paquete "
                    f"canónico ({case.packet_id!r}); {case.label}",
                )
                self.assertEqual(
                    case.packet_id,
                    case.project.packet_id(1),
                    msg="INV-04: el paquete publicado debe conservar la "
                    f"identidad canónica; {case.label}",
                )
                self.assertEqual(
                    published.get("objective"),
                    case.objective,
                    msg="INV-04: el request publicado debe conservar el "
                    f"objetivo declarado; {case.label}",
                )

                metadata, _, _ = parse_packet(case.packet_bytes.decode("utf-8"))
                self.assertNotIn(
                    "agent",
                    metadata,
                    msg="PC-08/INV-04 violada: los bytes del render publicado "
                    "contienen el campo `agent`; debe quedar excluido "
                    f"({case.label}; claves: {sorted(metadata)})",
                )
                self.assertEqual(
                    metadata.get("execution_context"),
                    published.get("execution_context"),
                    msg="INV-04: el render publicado debe conservar el "
                    "localizador de ejecución del request; " + case.label,
                )

    # -- contraste estático de rol --------------------------------------

    def test_static_contrast_admits_the_declared_role_and_rejects_foreign_families(
        self,
    ) -> None:
        """INV-04/PC-07b: todo ``agent`` de la familia del rol declarado
        (genérico exacto o prefijo completo con sufijo no vacío) valida, y toda
        familia de otro rol o coincidencia parcial se rechaza sin consultar el
        ``stack`` vigente; el diagnóstico nombra rol, agente recibido y familia
        esperada y declara que el stack no se evalúa.

        Sin este test, un agente de otro rol podría recibir el trabajo, una
        coincidencia parcial del nombre del rol podría pasar, o un rechazo
        estático preemptor podría confundirse con el contextual.
        """
        bases = _role_bases()
        rng = random.Random(SEED + 1)
        admission = 0

        # (a) Admisión: 5 roles × 4 formas de la familia declarada.
        for role, case in bases.items():
            for suffix in (None, "odoo", "erp-x", generated_suffix(rng)):
                agent = (
                    f"cdad-{role}"
                    if suffix is None
                    else canonical_agent(role, suffix, False)
                )
                result = self._validate_agent(
                    case, agent, f"prop-static-admit-{role}.json"
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    msg="INV-04/PC-07b violada: un agente de la familia del rol "
                    f"declarado debe validar ({role!r}, {agent!r}): "
                    + result.stderr.decode(errors="replace")[-1000:],
                )
                admission += 1
        self.assertEqual(admission, BUDGET_STATIC_ADMISSION)

        # (b) Rechazo: 100 discordancias generadas (otro rol o parcial).
        for index in range(BUDGET_STATIC_MISMATCH):
            role, substage = rng.choice(ROLE_CASES)
            case = bases[role]
            agent = _foreign_agent(rng, role)
            result = self._validate_agent(
                case, agent, f"prop-static-reject-{index:03d}.json"
            )
            self.assertNotEqual(
                result.returncode,
                0,
                msg="INV-04/PC-07b violada: `validate-request` aceptó un agente "
                "que no pertenece a la familia estática del rol declarado "
                f"({role}/{substage}, recibido {agent!r})",
            )
            diagnostic = self.diagnostic(result).lower()
            for token in (role, agent.lower(), f"cdad-{role}"):
                self.assertIn(
                    token,
                    diagnostic,
                    msg="INV-04/PC-07b violada: el diagnóstico estático debe "
                    "nombrar el rol declarado, el agente recibido y la familia "
                    f"esperada (falta {token!r}): {diagnostic[-1000:]!r}",
                )
            self.assertRegex(
                diagnostic,
                r"(?s)stack.{0,200}(no|not|never|sin|nunca)|"
                r"(no|not|never|sin|nunca).{0,200}stack",
                msg="INV-04/PC-07b violada: el diagnóstico estático debe "
                "declarar que el `stack` NO se evalúa (discrimina del "
                f"contextual): {diagnostic[-1000:]!r}",
            )

        # (c) `render` no publica paquete con una familia de otro rol (una
        # muestra por rol: el rechazo estático se conserva en la publicación).
        for role, case in bases.items():
            foreign = next(item for item in CURRENT_ROLES if item != role)
            mutation = dict(case.request)
            mutation["agent"] = f"cdad-{foreign}"
            path = case.project.root / f"prop-static-render-{role}.json"
            path.write_text(
                json.dumps(mutation, ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            rendered = self.render(case.project, path)
            self.assertNotEqual(
                rendered.returncode,
                0,
                msg="INV-04/PC-07b violada: `render` produjo un paquete con un "
                f"agente de otro rol ({role} → {foreign!r})",
            )
            self.assertNotIn(
                b"---cdad-packet-json",
                rendered.stdout,
                msg="INV-04/PC-07b violada: `render` emitió un paquete válido "
                f"para un agente de otro rol ({role} → {foreign!r})",
            )

    # -- contraste contextual del intento nuevo -------------------------

    def test_contextual_contrast_rejects_a_new_intent_with_a_discordant_agent(
        self,
    ) -> None:
        """INV-04/PC-07c: para 100 intentos nuevos generados, un agente
        declarado que no corresponde al rol y al ``stack`` vigente falla antes
        de publicar el registro, con diagnóstico de rol, stack y agente
        esperado, sin efectos durables.

        Sin este test, un encargo se despacharía a un dominio que ya no
        corresponde, o el diagnóstico no permitiría distinguir este rechazo del
        estático.
        """
        bases = contextual_bases()
        rng = random.Random(SEED + 2)
        cases = 0

        for index in range(BUDGET_CONTEXTUAL):
            role, substage = rng.choice(ROLE_CASES)
            stack_a = rng.choice(CONTEXTUAL_STACKS)
            project, packet_id, packet_dir = bases[(role, stack_a)]
            request = json.loads(
                (packet_dir / "REQUEST.json").read_text(encoding="utf-8")
            )
            declared = request.get("agent")
            self.assertEqual(
                declared,
                canonical_agent(role, stack_a, False),
                msg="precondición (fixture): la base contextual publica el "
                f"agente del stack {stack_a!r}; vio {declared!r}",
            )

            while True:
                draw = rng.random()
                if draw < 0.20:
                    stack_b, absent_b = None, True
                elif draw < 0.40:
                    stack_b, absent_b = None, False
                elif draw < 0.60:
                    stack_b, absent_b = "", False
                else:
                    stack_b, absent_b = generated_suffix(rng), False
                expected = canonical_agent(role, stack_b, absent_b)
                if expected != declared:
                    break

            _set_stack(project, stack_b, absent_b)
            state_before = json.loads(
                project.state_path.read_text(encoding="utf-8")
            )
            status_before = (state_before.get("active_packet") or {}).get("status")
            before_files = self.dispatch_files(project)
            observation = self.observation(
                project, f"prop-ctx-obs-{index:03d}.json", f"ses-prop-{index:03d}"
            )
            result = self.record(
                project, packet_id, f"attempt-prop-{index:03d}", observation
            )

            self.assertNotEqual(
                result.returncode,
                0,
                msg="INV-04/PC-07c violada: un intento nuevo con agente "
                "declarado discorde con el stack vigente fue aceptado "
                f"({role}/{substage}: declarado {declared!r}, stack "
                f"{stack_b!r}, esperado {expected!r})",
            )
            diagnostic = self.diagnostic(result).lower()
            for token in (role, "stack", expected.lower()):
                self.assertIn(
                    token,
                    diagnostic,
                    msg="INV-04/PC-07c violada: el diagnóstico contextual debe "
                    "nombrar rol, stack y agente esperado (falta "
                    f"{token!r}): {diagnostic[-1000:]!r}",
                )
            if isinstance(stack_b, str) and stack_b:
                self.assertIn(
                    stack_b.lower(),
                    diagnostic,
                    msg="INV-04/PC-07c violada: el diagnóstico contextual debe "
                    f"nombrar el stack vigente {stack_b!r}: {diagnostic[-1000:]!r}",
                )

            self.assertEqual(
                self.dispatch_files(project),
                before_files,
                msg="INV-04/PC-07c violada: el rechazo contextual publicó un "
                "registro de despacho",
            )
            state_after = json.loads(
                project.state_path.read_text(encoding="utf-8")
            )
            self.assertEqual(
                (state_after.get("active_packet") or {}).get("status"),
                status_before,
                msg="INV-04/PC-07c violada: el rechazo contextual cambió el "
                "estado del paquete",
            )
            cases += 1

        self.assertEqual(cases, BUDGET_CONTEXTUAL)

    # -- regla de presencia agente/contexto -----------------------------

    def test_presence_rule_rejects_context_without_agent_and_admits_the_historical(
        self,
    ) -> None:
        """INV-04/PC-08/O2: ``execution_context`` presente sin ``agent`` se
        rechaza y el histórico admitido sin **ambos** campos sigue admitido
        (5 roles del dominio de publicación).

        Sin este test, un request con contexto quedaría sin destinatario, o la
        corrección rompería los históricos legítimos al exigirles un agente que
        nunca declararon.
        """
        bases = _role_bases()
        self.assertEqual(len(bases), BUDGET_PRESENCE)

        for role, case in bases.items():
            request = dict(case.request)
            without_agent = dict(request)
            without_agent.pop("agent", None)
            rejected = self._validate_document(
                case, without_agent, f"prop-presence-no-agent-{role}.json"
            )
            self.assertNotEqual(
                rejected.returncode,
                0,
                msg="INV-04/PC-08 violada: un request con `execution_context` y "
                f"sin `agent` fue aceptado ({role})",
            )
            diagnostic = self.diagnostic(rejected).lower()
            for token in ("agent", "execution_context"):
                self.assertIn(
                    token,
                    diagnostic,
                    msg="INV-04/PC-08 violada: el rechazo de presencia debe "
                    f"nombrar {token!r}: {diagnostic[-1000:]!r}",
                )

            historical = dict(request)
            historical.pop("agent", None)
            historical.pop("execution_context", None)
            admitted = self._validate_document(
                case, historical, f"prop-presence-historical-{role}.json"
            )
            self.assertEqual(
                admitted.returncode,
                0,
                msg="INV-04/PC-08 violada: el histórico sin contexto ni agente "
                f"dejó de admitirse ({role}): "
                + admitted.stderr.decode(errors="replace")[-1000:],
            )

    # -- helpers de mutación sobre la publicación -----------------------

    def _validate_document(
        self, case: GeneratedPublication, document: dict, filename: str
    ) -> subprocess.CompletedProcess:
        path = case.project.root / filename
        path.write_text(
            json.dumps(document, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return self.validate(case.project, path)

    def _validate_agent(
        self, case: GeneratedPublication, agent: str, filename: str
    ) -> subprocess.CompletedProcess:
        mutated = dict(case.request)
        mutated["agent"] = agent
        return self._validate_document(case, mutated, filename)


# ===========================================================================
# (PC-12.b) Recorrido integrado final sobre la instalación aislada.
# ===========================================================================


class TestFinalIsolatedDistribution(unittest.TestCase):
    """Promesa F, tramo PC-12.b: la instalación aislada final distribuye el CLI
    y el esquema corregidos, y el recorrido documental genérico y
    documental/Odoo conserva dominio, producto editable y fronteras.

    Sin estos tests, la instalación podría distribuir un CLI o un esquema
    anteriores aunque el producto fuente esté corregido, el encargo
    documental/Odoo podría resolver el agente genérico o perder su frontera de
    escritura, y la resolución no se habría ejercitado por la interfaz pública.
    """

    maxDiff = None

    def install_bundle(self) -> dict[str, object]:
        bundle = final_install_bundle()
        run = bundle["run"]
        assert isinstance(run, subprocess.CompletedProcess)
        self.assertTrue(
            run.returncode == 0,
            "PC-12.b: la instalación aislada falló (rc="
            f"{run.returncode}):\n{run.stdout[-1500:]}\n{run.stderr[-1500:]}",
        )
        return bundle

    @staticmethod
    def installed_skill_path(install_root: Path, skills_root: str, relpath: str) -> Path:
        return install_root / skills_root / "cdad-cycle" / relpath

    # -- distribución de CLI y esquema ----------------------------------

    def test_isolated_install_distributes_the_final_cli_and_schema(self) -> None:
        """PC-12.b/EV-04: las tres raíces `skills/` publicadas por el
        instalador distribuyen ``scripts/cdad_packet.py`` y
        ``assets/packet-request.schema.json`` con los bytes exactos de la
        fuente del repositorio, y la generación promovió los agentes de ambos
        runtimes en la copia descartable.

        Sin este test, el recorrido documental podría ejecutarse contra un CLI
        o un esquema anteriores al GREEN de T6 y la instalación no acreditaría
        PC-12.b por sus bytes.
        """
        bundle = self.install_bundle()
        install_root = bundle["install_root"]
        product = bundle["product"]
        assert isinstance(install_root, Path)
        assert isinstance(product, Path)

        self.assertEqual(len(SKILL_ROOTS), 3)
        for skills_root in SKILL_ROOTS:
            with self.subTest(skills_root=skills_root, artifact="cli"):
                installed = self.installed_skill_path(
                    install_root, skills_root, "scripts/cdad_packet.py"
                )
                self.assertTrue(
                    installed.is_file(),
                    f"PC-12.b: la instalación no publicó el CLI en "
                    f"`{skills_root}/cdad-cycle/scripts/cdad_packet.py`.",
                )
                self.assertEqual(
                    installed.read_bytes(),
                    CLI_SOURCE.read_bytes(),
                    f"PC-12.b: los bytes instalados del CLI en `{skills_root}` no "
                    "coinciden con la fuente del repositorio.",
                )
            with self.subTest(skills_root=skills_root, artifact="schema"):
                installed = self.installed_skill_path(
                    install_root, skills_root, "assets/packet-request.schema.json"
                )
                self.assertTrue(
                    installed.is_file(),
                    f"PC-12.b: la instalación no publicó el esquema en "
                    f"`{skills_root}/cdad-cycle/assets/packet-request.schema.json`.",
                )
                self.assertEqual(
                    installed.read_bytes(),
                    SCHEMA_SOURCE.read_bytes(),
                    f"PC-12.b: los bytes instalados del esquema en `{skills_root}` "
                    "no coinciden con la fuente del repositorio.",
                )

        # Generación previa a la instalación: los agentes promovidos existen en
        # la copia descartable para ambos runtimes (no se lee build/staging del
        # checkout como oráculo).
        for runtime in RUNTIMES:
            with self.subTest(runtime=runtime, artifact="promoted-agent"):
                promoted = product / PROMOTED_DIRS[runtime] / "cdad-orchestrator.md"
                self.assertTrue(
                    promoted.is_file(),
                    "PC-12.b: la generación no promovió los agentes del runtime "
                    f"`{runtime}` en la copia descartable.",
                )
                self.assertTrue(promoted.read_bytes().strip())

        # Canario: la instalación no escribió el HOME visible del proceso ni la
        # instalación global (CDAD_INSTALL_ROOT sigue retirado del entorno).
        self.assertEqual(
            home_inventory(),
            _HOME_BASELINE,
            "EV-05: la instalación aislada escribió en el HOME del proceso",
        )
        self.assertNotIn(
            "CDAD_INSTALL_ROOT",
            os.environ,
            "EV-05: el test no debe fijar CDAD_INSTALL_ROOT en el proceso",
        )
        self.assertFalse(
            (Path(os.environ["HOME"]) / ".config/opencode/skills/cdad-cycle").exists(),
            "EV-05: la instalación aislada no debe publicar en el HOME del "
            "proceso (destino global)",
        )
        self.assertNotIn(
            Path(os.environ["HOME"]),
            install_root.parents,
            "EV-05: la raíz de instalación debe quedar fuera del HOME del proceso",
        )

    # -- recorrido documental genérico y documental/Odoo ----------------

    def test_final_documentary_journeys_keep_domain_product_and_frontiers(
        self,
    ) -> None:
        """PC-12.b/O5: sobre la instalación aislada final, un encargo
        documental genérico y otro documental con ``stack=odoo`` recorren
        preparación → validación → registro por la interfaz pública instalada,
        resuelven el agente derivado del dominio en ambos runtimes instalados y
        conservan producto editable y fronteras: el implementer no obtiene
        escritura en tests, el test-writer solo en tests y los roles de lectura
        no escriben producto.

        Sin este test, la instalación final podría resolver el agente genérico
        para un dominio Odoo, permitir que la etiqueta documental amplíe la
        escritura hacia tests o addon, o no poder despachar el encargo con el
        CLI instalado.
        """
        bundle = self.install_bundle()
        install_root = bundle["install_root"]
        product = bundle["product"]
        env = _isolated_env(dict(bundle["home_env"]))  # type: ignore[arg-type]
        assert isinstance(install_root, Path)
        assert isinstance(product, Path)

        cli = self.installed_skill_path(
            install_root, ".config/opencode/skills", "scripts/cdad_packet.py"
        )
        self.assertTrue(
            cli.is_file(),
            "PC-12.b: la instalación no publicó el CLI con el que se ejecuta "
            "el recorrido.",
        )
        env["CDAD_OPENCODE_AGENTS_DIR"] = str(
            install_root / INSTALLED_AGENTS_DIRS["opencode"]
        )

        schema_path = self.installed_skill_path(
            install_root, ".config/opencode/skills", "assets/packet-request.schema.json"
        )
        validator = None
        if jsonschema is not None:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            validator_class = jsonschema.validators.validator_for(schema)
            validator_class.check_schema(schema)
            validator = validator_class(schema)

        journeys = (
            ("documental genérico", None, "implementer", "green", "docs=docs/report"),
            (
                "documental con stack odoo",
                "odoo",
                "test-writer",
                "properties",
                "tests=tests",
            ),
        )
        for label, stack, role, substage, scope in journeys:
            with self.subTest(journey=label):
                project = self.journey_project(role, substage, stack)
                prepared = run_prepare(
                    cli,
                    *_canonical_argv(project, f"PC-12.b {label}"),
                    "--write-scope",
                    scope,
                    cwd=project.root,
                    env=env,
                )
                self.assertEqual(
                    prepared.returncode,
                    0,
                    f"PC-12.b: la preparación del recorrido {label!r} con el CLI "
                    f"instalado falló (rc={prepared.returncode}): "
                    + prepared.stderr.decode(errors="replace")[-1500:],
                )

                packet_id, packet_dir = self.published_packet(project)
                request = json.loads(
                    (packet_dir / "REQUEST.json").read_text(encoding="utf-8")
                )
                expected_agent = canonical_agent(role, stack, False)

                self.assertEqual(
                    request.get("role"),
                    role,
                    f"PC-12.b: el recorrido {label!r} perdió el rol.",
                )
                self.assertEqual(
                    request.get("substage"),
                    substage,
                    f"PC-12.b: el recorrido {label!r} perdió la subfase.",
                )
                self.assertEqual(
                    request.get("agent"),
                    expected_agent,
                    f"PC-12.b: el recorrido {label!r} no deriva el agente del "
                    f"dominio; esperado {expected_agent!r}, vio "
                    f"{request.get('agent')!r}.",
                )
                context = request.get("execution_context")
                self.assertIsInstance(context, str)
                self.assertTrue(context.strip())
                self.assertFalse(Path(context).is_absolute())

                self.assert_frontier(request, role, scope, label)
                self.assert_installed_schema_accepts(
                    validator, request, label, schema_path
                )

                validated = _run(
                    cli,
                    "validate-request",
                    "--project-root",
                    str(project.root),
                    "--execution-context",
                    str(project.execution_path),
                    "--request",
                    str(packet_dir / "REQUEST.json"),
                    cwd=project.root,
                    env=env,
                )
                self.assertEqual(
                    validated.returncode,
                    0,
                    f"PC-12.b: `validate-request` instalado rechazó el request "
                    f"del recorrido {label!r}: "
                    + validated.stderr.decode(errors="replace")[-1500:],
                )

                observation = project.root / "journey-observation.json"
                observation.write_text(
                    json.dumps(observation_document(f"ses-{role}-{substage}"))
                    + "\n",
                    encoding="utf-8",
                )
                recorded = _run(
                    cli,
                    "prepare",
                    "--project-root",
                    str(project.root),
                    "--record-dispatch",
                    packet_id,
                    "--attempt-id",
                    f"attempt-{role}",
                    "--input",
                    str(observation),
                    cwd=project.root,
                    env=env,
                )
                self.assertEqual(
                    recorded.returncode,
                    0,
                    f"PC-12.b: `record-dispatch` instalado rechazó el intento del "
                    f"recorrido {label!r}: "
                    + recorded.stderr.decode(errors="replace")[-1500:],
                )
                state = json.loads(project.state_path.read_text(encoding="utf-8"))
                self.assertEqual(
                    (state.get("active_packet") or {}).get("status"),
                    "dispatched",
                    f"PC-12.b: el recorrido {label!r} no dejó el paquete "
                    "`dispatched`.",
                )
                dispatch_dir = (
                    project.root
                    / ".cdad"
                    / "executions"
                    / str((state.get("execution") or {}).get("id") or "")
                    / "dispatches"
                )
                self.assertTrue(
                    (dispatch_dir / f"attempt-{role}.json").is_file(),
                    f"PC-12.b: el recorrido {label!r} no publicó su registro de "
                    "despacho durable.",
                )

                # Resolución: el agente derivado existe, con los bytes
                # promovidos, en los dos destinos instalados.
                for runtime in RUNTIMES:
                    with self.subTest(journey=label, runtime=runtime):
                        installed = (
                            install_root
                            / INSTALLED_AGENTS_DIRS[runtime]
                            / f"{expected_agent}.md"
                        )
                        self.assertTrue(
                            installed.is_file(),
                            f"PC-12.b: el agente resuelto {expected_agent!r} no "
                            f"existe en el destino instalado de {runtime}.",
                        )
                        self.assertEqual(
                            installed.read_bytes(),
                            (
                                product
                                / PROMOTED_DIRS[runtime]
                                / f"{expected_agent}.md"
                            ).read_bytes(),
                            f"PC-12.b: el agente resuelto {expected_agent!r} "
                            f"instalado en {runtime} no procede de la generación "
                            "promovida.",
                        )

                # Frontera de los roles de lectura: no escriben producto.
                read_only = self.journey_project("reviewer", "review", stack)
                read_only_prepared = run_prepare(
                    cli,
                    *_canonical_argv(read_only, f"PC-12.b {label} reviewer"),
                    cwd=read_only.root,
                    env=env,
                )
                self.assertEqual(
                    read_only_prepared.returncode,
                    0,
                    f"PC-12.b: la preparación del rol de lectura del recorrido "
                    f"{label!r} falló (rc={read_only_prepared.returncode}): "
                    + read_only_prepared.stderr.decode(errors="replace")[-1500:],
                )
                _, read_only_dir = self.published_packet(read_only)
                read_only_request = json.loads(
                    (read_only_dir / "REQUEST.json").read_text(encoding="utf-8")
                )
                self.assertEqual(
                    read_only_request.get("write_scope"),
                    [],
                    f"PC-12.b: el rol de lectura del recorrido {label!r} obtuvo "
                    "escritura de producto; su frontera debe seguir vacía.",
                )
                self.assertEqual(
                    read_only_request.get("agent"),
                    canonical_agent("reviewer", stack, False),
                    f"PC-12.b: el rol de lectura del recorrido {label!r} no "
                    "deriva su agente del dominio.",
                )
                read_only_validated = _run(
                    cli,
                    "validate-request",
                    "--project-root",
                    str(read_only.root),
                    "--execution-context",
                    str(read_only.execution_path),
                    "--request",
                    str(read_only_dir / "REQUEST.json"),
                    cwd=read_only.root,
                    env=env,
                )
                self.assertEqual(
                    read_only_validated.returncode,
                    0,
                    f"PC-12.b: `validate-request` instalado rechazó el encargo "
                    f"del rol de lectura del recorrido {label!r}: "
                    + read_only_validated.stderr.decode(errors="replace")[-1500:],
                )

        self.assertEqual(
            home_inventory(),
            _HOME_BASELINE,
            "EV-05: el recorrido integrado escribió en el HOME del proceso",
        )

    # -- helpers del recorrido ------------------------------------------

    def journey_project(
        self, role: str, substage: str, stack: object
    ) -> PrepareProject:
        project = PrepareProject(
            _stable_mkdtemp("cdad-010-002-prop-journey-"), role, substage
        )
        if stack is not None:
            _set_stack(project, stack, False)
        return project

    def published_packet(self, project: PrepareProject) -> tuple[str, Path]:
        state = json.loads(project.state_path.read_text(encoding="utf-8"))
        packet_id = str((state.get("active_packet") or {}).get("id") or "")
        self.assertTrue(
            packet_id,
            "PC-12.b: `prepare` no registró el paquete activo del recorrido.",
        )
        packet_dir = project.root / CANONICAL_PACKETS / packet_id
        self.assertTrue(
            (packet_dir / "REQUEST.json").is_file(),
            f"PC-12.b: `prepare` no publicó `{packet_dir / 'REQUEST.json'}`.",
        )
        return packet_id, packet_dir

    def assert_frontier(
        self, request: dict, role: str, scope: str, label: str
    ) -> None:
        scope_class, _, scope_root = scope.partition("=")
        expected = [
            {"class": scope_class, "root": scope_root or scope_class}
        ]
        writes = request.get("write_scope")
        self.assertEqual(
            writes,
            expected,
            f"PC-12.b: el producto editable declarado del recorrido {label!r} "
            f"no es el esperado ({expected!r}): vio {writes!r}.",
        )
        contract = str((request.get("contract") or {}).get("path") or "")
        self.assertTrue(contract, f"PC-12.b: el recorrido {label!r} no declara "
                        "su contrato fuente.")
        for entry in writes or []:
            target = entry.get("root") or entry.get("path") or ""
            self.assertFalse(
                _inside(contract, target),
                f"PC-12.b: el producto editable del recorrido {label!r} incluye "
                f"el contrato fuente `{contract}` (frontera `{target}`).",
            )
        if role == "implementer":
            for entry in writes or []:
                target = entry.get("root") or entry.get("path") or ""
                self.assertNotEqual(entry.get("class"), "tests")
                self.assertFalse(
                    _inside(target, "tests"),
                    f"PC-12.b: el implementer del recorrido {label!r} obtuvo "
                    "escritura en tests.",
                )
        if role == "test-writer":
            self.assertEqual(
                [entry.get("class") for entry in writes or []],
                ["tests"],
                f"PC-12.b: el test-writer del recorrido {label!r} solo puede "
                f"escribir tests; vio {writes!r}.",
            )

    def assert_installed_schema_accepts(
        self, validator, request: dict, label: str, schema_path: Path
    ) -> None:
        if validator is None:
            self.skipTest(
                "bloqueo de entorno (no defecto del producto): el motor real de "
                "JSON Schema (`jsonschema`) no está disponible"
            )
        self.assertTrue(
            schema_path.is_file(),
            f"PC-12.b: la instalación no publicó el esquema evaluado "
            f"(`{schema_path}`).",
        )
        errors = [error.message for error in validator.iter_errors(request)]
        self.assertEqual(
            errors,
            [],
            f"PC-12.b/PC-10: el esquema instalado rechaza el request del "
            f"recorrido {label!r}: {errors[:4]}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
