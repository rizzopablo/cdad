#!/usr/bin/env python3
"""006-002 U1 RED — secciones `delegation` de los adaptadores y su composición
en el orquestador generado (PD-2 y la parte de texto de PD-4; §3 INV; D-1/D-3).

Contrato (oráculo):
- `docs/specs/006-002-delegation-by-layer/spec.md` — PD-2 (a)-(d) y la parte
  de texto de PD-4; §3 INV-1..8; §4 D-1, D-3.
- `docs/specs/006-002-delegation-by-layer/plan.md` — ficha U1 + enmienda A-1
  (los asserts acoplados de esta superficie cambian en ESTE RED, nunca en el
  GREEN).

La regla de delegación de CADA runtime vive en su orquestador, generada desde
una NUEVA sección `delegation` del adaptador fuente
(`sources/agents/adapters/{opencode,claude-code}.md`, D-1) compuesta por el
generador. Hoy NO existe tal sección (verificado en el árbol): los orquestadores
generados no declaran el mecanismo nativo con `subagent_type`, no prohíben el
adaptador CLI intra-runtime, no llevan la declaración de familia D-3 y no
enlazan al protocolo de materialización.

Oráculo de artefacto (caja negra, consumidor): los tests leen
  - la salida GENERADA `build/staging/agents/{opencode,claude-code}/
    cdad-orchestrator.md` con `make staging`, producida en una COPIA temporal
    del checkout (patrón de `tests/product_staging.py`; nunca se escribe en el
    repo). REFORMULADO por 006-003 U3 (PD-1b/D7): la receta ya no recibe perfil
    — `PROFILE=basic` describiría la superficie retirada por PD-1/D1 —, y
  - las fuentes de adaptador `sources/agents/adapters/*.md` (D-1: dueñas del
    contenido de la sección; lectura de consumidor declarada por el paquete).
NO se lee implementación (`scripts/`, `skills/`): la composición se verifica
por conceptos compartidos fuente↔generado, sin depender del orden interno del
documento compuesto (ninguna aserción fija posición ni orden de secciones).

Marcadores ESTRUCTURALES por concepto con alternativas (patrón `require_any`
de `tests/test_005_010_t3_references.py`), no frases exactas. Dos excepciones
declaradas:
  - la frase de enlace «Orchestrator materialization protocol» (PD-5(b)/PD-2(d))
    es el ANCLA del enlace: un enlace debe coincidir con su destino;
  - los campos de registro `model_configured`/`model_reported` (D-3(2)) son
    nombres de campo fijados normativamente por el contrato.

Los formularios de herramienta siguen el oráculo de ausencia de la spec §2:
code-spans `` `task` `` / `` `Agent` `` y el token `subagent_type` — nunca la
palabra suelta *task* ("atomic task" no matchea; discovery §4 riesgo 6).

REFORMULADO por 006-003 U3 (PD-7b, D7) y, sobre él, por la ENMIENDA A-5 del
dueño (006-003 §9, 2026-10-18): la declaración de FAMILIA de D-3(iii)/(iv)
hablaba de la rama `basic` (el perfil que fijaba modelos) y U3 la convirtió en
una «verificación de configuración declarada». **A-5 retira el requisito
entero**: ningún texto instalable exige al orquestador elegir, controlar,
verificar ni declarar la familia o el modelo del reviewer respecto del
implementer (INV-5 reformulada). Así que el assert se INVIERTE y se repunta —no
se borra—: el orquestador compuesto no lleva vocabulario de perfiles ni
`--basic`, y NO exige ni declara la familia/modelo del reviewer (oráculo único
`all_offenders` de u2). Los campos de registro I8 (`model_configured`/
`model_reported`) y las reglas «nunca elige ni inventa modelo» / «modelo sólo
desde la configuración» de D-3 se conservan sin cambio.

RED esperado en el árbol vigente de esta unidad (histórico: los bloques
`delegation` ya existen). Estado OBSERVADO bajo A-5:

  - PD-2(a)/(b), mecanismo nativo, prohibición intra-runtime, pase + enlace:
    PASAN hoy (GREEN de 006-002 U1) — controles de conservación;
  - registro I8 + «nunca elige» + «modelo sólo desde la configuración»
    (conservados por A-5): PASAN hoy — controles de conservación;
  - ausencia del requisito de FAMILIA (reformulada por A-5): FALLA por
    AssertionError de CONTENIDO en AMBOS orquestadores — el compuesto todavía
    declara la familia del reviewer como verificación de configuración y su
    caveat «invariant not guaranteed».
Todo fallo RED es AssertionError de CONTENIDO (contrato PD-2/PD-4/A-5), nunca
ImportError/SyntaxError ni fallo de fixture.

Mapa test → postcondición (spec 006-002; fila 6 reformulada por A-5):

  1  TestPd2aExactlyOneDelegationSection::test_pd2a_…_adapter_…          PD-2(a) (bloque único por adaptador)
  2  TestPd2bSourceOwnsDelegationContent::test_pd2b_…_source_block_…     PD-2(a)/(b) + D-1 (el contenido vive en la fuente)
  3  TestPd2cOcOrchestratorNativeMechanism::test_pd2c_…                  PD-2(c) (OpenCode: `task` + subagent_type)
  4  TestPd2cCcOrchestratorNativeMechanism::test_pd2c_…                  PD-2(c) (Claude Code: `Agent` + subagent_type; control)
  5  TestPd4IntraRuntimeAdapterProhibition::test_pd4_ii_…                PD-4(ii) / D-1 (prohibición explícita, ambos)
  6  TestPd4DelegationRegistrationWithoutFamilyRequirement::test_pd4_…   PD-4(iii)+(iv)/D-3 con la familia RETIRADA → INV-5/A-5 (ambos)
  7  TestPd2dPacketPassAndReceiptLink::test_pd2d_…                       PD-2(d) + PD-5(b) (pase byte-idéntico + enlace)
"""

from __future__ import annotations

import atexit
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

# Oráculo único de AUSENCIA del requisito de familia/modelo del reviewer (A-5),
# compartido con las demás superficies (definición única en u2).
from tests.test_006_002_u2_neutral_skill import all_offenders
from tests.product_staging import run_scoped_mkdtemp

REPO_ROOT = Path(__file__).resolve().parents[1]

# Orquestadores generados, staging `basic` (ficha U1 / PD-4).
OC_ORCH_REL = Path("build") / "staging" / "agents" / "opencode" / "cdad-orchestrator.md"
CC_ORCH_REL = Path("build") / "staging" / "agents" / "claude-code" / "cdad-orchestrator.md"
# Fuentes de adaptador (D-1: dueñas del contenido de la sección `delegation`).
OC_ADAPTER_REL = Path("sources") / "agents" / "adapters" / "opencode.md"
CC_ADAPTER_REL = Path("sources") / "agents" / "adapters" / "claude-code.md"

# --- marcadores estructurales -------------------------------------------

# Gramática de secciones (spec PD-2(a): scripts/cdad-generate.py:107-155).
SECTION_OPEN_RE = re.compile(r"<!--\s*cdad-section:delegation\s*-->")
SECTION_CLOSE_RE = re.compile(r"<!--\s*/cdad-section\s*-->")

# Formularios de HERRAMIENTA (spec §2: code-spans y nombres de tool form;
# NUNCA la palabra suelta *task* — "atomic task" no es un despacho).
OC_MECHANISM_FORMS = ("`task`", "task tool", "native task", "task dispatch",
                      "task mechanism")
CC_MECHANISM_FORMS = ("`agent`", "agent tool", "agent dispatch",
                      "agent mechanism")

# Mapeo rol→subagente: `subagent_type` junto a `cdad-<role>` o a un rol
# concreto (`cdad-reviewer` etc.).
ROLE_MAPPING_RE = re.compile(
    r"subagent_type[^\n]{0,80}cdad-(?:<role>|architect|test-writer"
    r"|implementer|reviewer|scribe|orchestrator)"
    r"|cdad-<role>[^\n]{0,80}subagent_type")

# Adaptador CLI (la seÑAL durable del adaptador de programa, PD-10/005-010):
# el despacho INTRA-runtime no pasa por él (D-1; spec §1, measured consequence).
CLI_ADAPTER_TOKENS = ("cli adapter", "cli delegation", "cli-delegation",
                      "cdad_delegate")
PROHIBITION_TOKENS = ("must not", "never", "shall not", "prohibit", "forbid",
                      "not use", "is not used", "no se usa", "no debe")
INTRA_RUNTIME_TOKENS = ("intra-runtime", "intra runtime", "same runtime",
                        "within the runtime", "inside the runtime",
                        "own runtime", "mismo runtime")

# Rama `delegation` y registro del intento (D-3 de 006-002; la parte de FAMILIA
# fue RETIRADA por la enmienda A-5 de 006-003 §9 — ver la cabecera del módulo).
# La rama `basic` de D-3 (perfil que fijaba modelos) se retira con los perfiles
# (PD-1/D1) y con ella TODO requisito sobre la familia/modelo del reviewer
# respecto del implementer: ningún rastro de perfil ni de familia sobrevive en
# el orquestador. Los campos de registro I8 y las reglas «nunca elige» /
# «modelo sólo desde la configuración» (D-3) se CONSERVAN.
PROFILE_VOCABULARY_RE = re.compile(r"(?i)\bperfil(?:es)?\b|\bprofile(?:s)?\b")
RETIRED_BASIC_FLAG_RE = re.compile(r"--basic\b")
# D-3(2): campos de registro fijados por el contrato (nombres normativos).
REGISTRATION_FIELD_TOKENS = ("model_configured", "model_reported")
# D-3: el orquestador NO elige ni inventa modelo.
NEVER_CHOOSES_MODEL_TOKENS = ("never chooses", "does not choose",
                              "neither chooses", "must not choose",
                              "never invents", "does not invent",
                              "never selects", "does not select",
                              "never pick", "does not pick")
# D-3(3): un modelo se pasa SOLO si viene de la configuración del entorno.
MODEL_FROM_CONFIG_TOKENS = ("only if it comes from the environment",
                            "only from the environment configuration",
                            "comes from the environment configuration",
                            "environment configuration",
                            "environment's configuration",
                            "configured in the environment",
                            "the runtime configuration")

# Pase del paquete (PD-2(d)) y enlace al protocolo de recibo (PD-5(b)/PD-2(d)):
# la frase de enlace es el ANCLA del enlace destino (re-entry.md), fijada por
# la spec; se exige tal cual porque un enlace debe coincidir con su destino.
BYTE_PASS_TOKENS = ("byte-identical", "byte for byte", "exact bytes",
                    "same bytes", "unchanged", "verbatim")
RECEIPT_LINK_PHRASE = "orchestrator materialization protocol"

_STAGING_ROOT: Path | None = None


def staging_root() -> Path:
    """Raíz de producto (copia temporal) con `make staging`.

    Reformulado por 006-003 U3 (PD-1b/D7): la receta ya no recibe perfil — el
    generador no tiene `--profile` y el instalador no tiene perfiles; pedir
    `PROFILE=basic` describiría una superficie retirada. Patrón de
    `tests/product_staging.py`: una copia del checkout por proceso, staging
    generado UNA vez dentro de la copia; nunca se escribe en el repo y no hay
    rutas de host en las aserciones (INV: sin valores del host).
    """
    global _STAGING_ROOT
    if _STAGING_ROOT is None:
        tmp = run_scoped_mkdtemp("cdad-006-002-u1-")
        atexit.register(shutil.rmtree, tmp, ignore_errors=True)
        copy = Path(tmp) / "product"
        shutil.copytree(
            REPO_ROOT,
            copy,
            symlinks=True,
            ignore=shutil.ignore_patterns(
                ".git", ".pytest_cache", "__pycache__", "build"),
        )
        run = subprocess.run(
            ["make", "staging"],
            cwd=str(copy), text=True, capture_output=True,
        )
        manifest = copy / "build" / "staging" / "manifest.json"
        if run.returncode != 0 or not manifest.is_file():
            raise AssertionError(
                "U1 fixture: `make staging` no generó el staging en la copia "
                f"del fixture (rc={run.returncode}): "
                f"{run.stdout[-400:]!r} {run.stderr[-400:]!r}")
        _STAGING_ROOT = copy
    return _STAGING_ROOT


class U1Case(unittest.TestCase):
    """Base del oráculo U1: puertas AssertionError (existe, no vacío) sobre
    los artefactos declarados; jamás lee implementación de producto."""

    def read(self, path: Path, why: str) -> str:
        self.assertTrue(
            path.is_file(),
            msg=f"{why}: el artefacto declarado por el contrato no existe: "
                f"{path}")
        text = path.read_text(encoding="utf-8")
        self.assertTrue(
            text.strip(),
            msg=f"{why}: el artefacto declarado está vacío: {path.name}")
        return text

    def orchestrator(self, rel: Path) -> tuple[str, str]:
        """Texto del orquestador generado (staging `basic`)."""
        root = staging_root()
        label = rel.parent.parent.name + "/" + rel.parent.name
        return self.read(root / rel, f"PD-2/PD-4 staging ({label})"), label

    def require_any(self, text: str, alternatives: tuple[str, ...],
                    concept: str, document: str) -> None:
        """Exige UN concepto clave: cualquiera de las alternativas (la forma
        de la prosa la verifica el review de stage 4)."""
        lowered = text.lower()
        hits = [alt for alt in alternatives if alt.lower() in lowered]
        self.assertTrue(
            hits,
            msg=f"{document} no declara el concepto clave '{concept}' "
                f"(PD-2/PD-4; alternativas buscadas {list(alternatives)!r})")

    def forbid(self, text: str, pattern: re.Pattern, label: str,
               document: str) -> None:
        matches = pattern.findall(text)
        self.assertEqual(
            matches, [],
            msg=f"{document} contiene {label} (prohibido por el contrato): "
                f"{matches[:6]!r}")

    def co_located_window(self, text: str, groups: list[tuple[str, ...]],
                          anchor: tuple[str, ...], window: int = 12,
                          document: str = "") -> None:
        """Exige una ventana co-ubicada: alrededor de CADA línea-ancla
        (matchea `anchor`) debe existir UN hit de cada grupo en ±`window`
        líneas. Conceptos co-ubicados, no frases exactas."""
        lines = text.splitlines()
        lowered_lines = [line.lower() for line in lines]
        for idx, line in enumerate(lowered_lines):
            if not any(tok in line for tok in anchor):
                continue
            lo, hi = max(0, idx - window), min(len(lines), idx + window + 1)
            chunk = "\n".join(lowered_lines[lo:hi])
            if all(any(tok in chunk for tok in group) for group in groups):
                return
        self.fail(
            msg=f"{document} no co-ubica los conceptos requeridos "
                f"{[list(g) for g in groups]!r} alrededor de un ancla "
                f"{list(anchor)!r} (±{window} líneas) — PD-2/PD-4: la regla "
                "debe estar declarada junto a su ancla")


# ------------------------------------------------------- PD-2(a) — fuentes


class TestPd2aExactlyOneDelegationSection(U1Case):
    """PD-2(a): CADA adaptador fuente lleva EXACTAMENTE un bloque
    `<!-- cdad-section:delegation -->` con su cierre (gramática de secciones
    del generador, spec :107-155)."""


    def assert_exactly_one(self, adapter_rel: Path, label: str) -> None:
        root = staging_root()
        text = self.read(root / adapter_rel, f"PD-2(a) ({label})")
        opens = SECTION_OPEN_RE.findall(text)
        self.assertEqual(
            len(opens), 1,
            msg=f"PD-2(a): {label} debe llevar EXACTAMENTE un bloque "
                f"`<!-- cdad-section:delegation -->` (encontrados "
                f"{len(opens)}; D-1: la regla de delegación vive en la "
                "sección del adaptador fuente)")
        match = SECTION_OPEN_RE.search(text)
        close = SECTION_CLOSE_RE.search(text, match.end())
        self.assertIsNotNone(
            close,
            msg=f"PD-2(a): {label}: el bloque `delegation` no tiene cierre "
                "`<!-- /cdad-section -->` (gramática de secciones)")
        block = text[match.end():close.start()]
        self.assertTrue(
            block.strip(),
            msg=f"PD-2(a): {label}: el bloque `delegation` está vacío")

    def test_pd2a_opencode_adapter_has_exactly_one_delegation_section(
            self) -> None:
        """PD-2(a): opencode.md lleva exactamente un bloque `delegation`."""
        self.assert_exactly_one(OC_ADAPTER_REL, "opencode.md")

    def test_pd2a_claude_code_adapter_has_exactly_one_delegation_section(
            self) -> None:
        """PD-2(a): claude-code.md lleva exactamente un bloque `delegation`."""
        self.assert_exactly_one(CC_ADAPTER_REL, "claude-code.md")


# ------------------------------------- PD-2(a)/(b) + D-1 — fuente dueña


class TestPd2bSourceOwnsDelegationContent(U1Case):
    """PD-2(a)/(b) + D-1: el CONTENIDO de la regla de delegación vive en la
    sección del adaptador fuente (el generador lo compone, no lo hardcodea).
    Cada bloque `delegation` declara los conceptos que PD-2 exige ver en el
    orquestador generado: el mecanismo nativo con `subagent_type`/mapeo, la
    prohibición intra-runtime del adaptador, el pase byte-idéntico del
    paquete y el enlace al protocolo de materialización."""


    def assert_block_owns_concepts(self, adapter_rel: Path, label: str,
                                   mechanism_forms: tuple[str, ...]) -> None:
        root = staging_root()
        text = self.read(root / adapter_rel, f"PD-2(a)/(b) ({label})")
        match = SECTION_OPEN_RE.search(text)
        self.assertIsNotNone(
            match,
            msg=f"PD-2(b)/D-1: {label} no tiene bloque "
                "`<!-- cdad-section:delegation -->` — el contenido no vive "
                "en la fuente (el generador no debe hardcodearlo)")
        close = SECTION_CLOSE_RE.search(text, match.end())
        self.assertIsNotNone(close, msg=f"PD-2(b)/D-1: {label}: bloque "
                                        "`delegation` sin cierre")
        block = text[match.end():close.start()]

        self.require_any(block, mechanism_forms, "mecanismo nativo",
                         label)
        self.assertIn(
            "subagent_type", block.lower(),
            msg=f"PD-2(b)/D-1: {label}: el bloque `delegation` no declara "
                "`subagent_type` (mapeo rol→subagente)")
        self.assertRegex(
            block, ROLE_MAPPING_RE,
            msg=f"PD-2(b)/D-1: {label}: el bloque `delegation` no asocia "
                "`subagent_type` con `cdad-<role>` (mapeo rol→subagente)")
        self.co_located_window(
            block, [PROHIBITION_TOKENS, INTRA_RUNTIME_TOKENS],
            CLI_ADAPTER_TOKENS, window=8, document=f"{label} (bloque)")
        self.require_any(block, BYTE_PASS_TOKENS,
                         "pase del paquete byte-idéntico", label)
        self.assertIn(
            RECEIPT_LINK_PHRASE, block.lower(),
            msg=f"PD-2(b)/D-1: {label}: el bloque `delegation` no enlaza al "
                f"«{RECEIPT_LINK_PHRASE}» (PD-5(b): el recibo es la salida "
                "única de toda ruta)")

    def test_pd2b_opencode_source_block_owns_the_delegation_concepts(
            self) -> None:
        """PD-2(a)/(b)/D-1: el bloque de opencode.md dueña de los conceptos."""
        self.assert_block_owns_concepts(
            OC_ADAPTER_REL, "opencode.md", OC_MECHANISM_FORMS)

    def test_pd2b_claude_code_source_block_owns_the_delegation_concepts(
            self) -> None:
        """PD-2(a)/(b)/D-1: el bloque de claude-code.md dueña de los conceptos."""
        self.assert_block_owns_concepts(
            CC_ADAPTER_REL, "claude-code.md", CC_MECHANISM_FORMS)


# --------------------------------------- PD-2(c) — mecanismo nativo


class TestPd2cOcOrchestratorNativeMechanism(U1Case):
    """PD-2(c): el orquestador OpenCode generado (staging `basic`) declara su
    mecanismo NATIVO (`task`, formulario de herramienta) con
    `subagent_type: cdad-<role>` — el despacho intra-runtime es nativo, no
    CLI."""


    def test_pd2c_opencode_orchestrator_names_native_task_with_subagent_type(
            self) -> None:
        """PD-2(c): `task` (forma de herramienta) + `subagent_type` +
        `cdad-<role>` en el orquestador OpenCode generado."""
        text, label = self.orchestrator(OC_ORCH_REL)
        self.require_any(text, OC_MECHANISM_FORMS,
                         "mecanismo nativo `task`", label)
        self.assertIn(
            "subagent_type", text.lower(),
            msg=f"{label}: no declara `subagent_type` (PD-2(c): el mecanismo "
                "nativo se nombra con su parámetro de rol)")
        self.assertRegex(
            text, ROLE_MAPPING_RE,
            msg=f"{label}: `subagent_type` no está asociado a `cdad-<role>` "
                "(PD-2(c): mapeo rol→subagente ausente)")


class TestPd2cCcOrchestratorNativeMechanism(U1Case):
    """PD-2(c): el orquestador Claude Code generado (staging `basic`) declara
    su mecanismo NATIVO (`Agent`) con `subagent_type: cdad-<role>`.

    Control de no-regresión: el tool-loading del adaptador CC ya nombra
    `Agent` + `subagent_type` hoy (005-004 T1), así que este test PASA en el
    árbol vigente; los fallos RED de la superficie CC vienen de PD-2(a)
    (bloque ausente), la prohibición y la declaración D-3."""


    def test_pd2c_claude_code_orchestrator_names_agent_with_subagent_type(
            self) -> None:
        """PD-2(c): `Agent` (forma de herramienta) + `subagent_type` +
        `cdad-<role>` en el orquestador Claude Code generado."""
        text, label = self.orchestrator(CC_ORCH_REL)
        self.require_any(text, CC_MECHANISM_FORMS,
                         "mecanismo nativo `Agent`", label)
        self.assertIn(
            "subagent_type", text.lower(),
            msg=f"{label}: no declara `subagent_type` (PD-2(c))")
        self.assertRegex(
            text, ROLE_MAPPING_RE,
            msg=f"{label}: `subagent_type` no está asociado a `cdad-<role>` "
                "(PD-2(c): mapeo rol→subagente ausente)")


# ------------------------------- PD-4(ii) — prohibición intra-runtime


class TestPd4IntraRuntimeAdapterProhibition(U1Case):
    """PD-4(ii)/D-1: NINGUNO de los dos orquestadores exige el adaptador CLI
    para un despacho dentro del mismo runtime, y AMBOS lo prohíben
    explícitamente (co-ubicado con el ancla del adaptador)."""


    def test_pd4_ii_neither_orchestrator_requires_cli_adapter_intra_runtime(
            self) -> None:
        """PD-4(ii): prohibición explícita co-ubicada (adaptador CLI +
        prohibición + intra-runtime) en ambos orquestadores generados."""
        for rel in (OC_ORCH_REL, CC_ORCH_REL):
            with self.subTest(orchestrator=str(rel.parent.parent.name)):
                text, label = self.orchestrator(rel)
                self.co_located_window(
                    text,
                    [PROHIBITION_TOKENS, INTRA_RUNTIME_TOKENS],
                    CLI_ADAPTER_TOKENS, window=12, document=label)


# ------------------- PD-4(iii)+(iv) / A-5 — registro sin requisito de familia
#
# REFORMULADO por 006-003 U3 (PD-7b) y luego por la ENMIENDA A-5 del dueño
# (006-003 §9, 2026-10-18): la rama `basic` de D-3 (006-002) describía el perfil
# que fijaba modelos, y la reformulación de U3 convirtió la familia del reviewer
# en una «verificación de configuración declarada». A-5 RETIRA el requisito
# entero: el orquestador no elige, controla, verifica ni declara la familia ni
# el modelo del reviewer respecto del implementer (INV-5 reformulada). El oráculo
# NO se borra: se invierte (ausencia del requisito, con el oráculo único
# ``all_offenders`` de u2) y se CONSERVAN los campos de registro I8
# (``model_configured``/``model_reported``, que sólo registran lo ocurrido) y las
# reglas «nunca elige» / «modelo sólo desde la configuración» de D-3.


class TestPd4DelegationRegistrationWithoutFamilyRequirement(U1Case):
    """PD-4(iii)+(iv) de 006-002 con la parte de familia retirada por A-5 —
    idéntica en CADA orquestador: el perfil retirado no sobrevive en el artefacto
    compuesto, la familia/modelo del reviewer no se exige, verifica ni declara, el
    intento se REGISTRA con los campos del contrato (I8), el orquestador NUNCA
    elige ni inventa un modelo y solo pasa uno si viene de la configuración."""


    def assert_delegation_without_family_requirement(self, rel: Path) -> None:
        text, label = self.orchestrator(rel)
        # (i) ausencia: el perfil y su flag ya no existen en el compuesto.
        self.forbid(text, PROFILE_VOCABULARY_RE,
                    "vocabulario de perfiles", label)
        self.forbid(text, RETIRED_BASIC_FLAG_RE,
                    "el flag retirado `--basic`", label)
        # (ii) A-5/INV-5: la familia/modelo del reviewer respecto del implementer
        # no se exige, controla, verifica ni declara (oráculo único ``all_offenders``).
        # La ruta que se reporta es la del artefacto LÓGICO (la copia de staging
        # vive en un tempdir): `build/staging/agents/<runtime>/cdad-orchestrator.md`.
        offenders = all_offenders(text, REPO_ROOT / rel)
        self.assertEqual(
            offenders, [],
            msg=f"{label}: el orquestador generado todavía exige o declara la "
                "familia/modelo del reviewer respecto del implementer "
                f"(A-5/PD-7b): {offenders[:20]!r}")
        # (iii) registro con los campos fijados por D-3(2) — CONSERVADO por A-5.
        self.require_any(text, REGISTRATION_FIELD_TOKENS,
                         "campos de registro model_configured/model_reported",
                         label)
        # (iv) el orquestador nunca elige ni inventa un modelo.
        self.require_any(text, NEVER_CHOOSES_MODEL_TOKENS,
                         "el orquestador no elige ni inventa modelo", label)
        # (v) modelo pasado SOLO si viene de la configuración del entorno.
        self.require_any(text, MODEL_FROM_CONFIG_TOKENS,
                         "modelo solo desde la configuración del entorno",
                         label)


    def test_pd4_delegation_registration_without_family_requirement_opencode(
            self) -> None:
        """PD-4(iii)+(iv)/D-3 + A-5: registro I8 sin requisito de familia en el
        orquestador OpenCode generado."""
        self.assert_delegation_without_family_requirement(OC_ORCH_REL)


    def test_pd4_delegation_registration_without_family_requirement_claude_code(
            self) -> None:
        """PD-4(iii)+(iv)/D-3 + A-5: registro I8 sin requisito de familia en el
        orquestador Claude Code generado."""
        self.assert_delegation_without_family_requirement(CC_ORCH_REL)


# ------------------------------ PD-2(d) + PD-5(b) — paquete y recibo


class TestPd2dPacketPassAndReceiptLink(U1Case):
    """PD-2(d) + PD-5(b): cada sección `delegation` declara el pase del
    paquete byte-idéntico y enlaza al «Orchestrator materialization
    protocol» (el recibo es la salida única de toda ruta; INV-3)."""


    def test_pd2d_packet_pass_and_receipt_link_in_both_orchestrators(
            self) -> None:
        """PD-2(d)/PD-5(b): pase byte-idéntico del paquete + enlace al
        protocolo de materialización en ambos orquestadores generados."""
        for rel in (OC_ORCH_REL, CC_ORCH_REL):
            with self.subTest(orchestrator=str(rel.parent.parent.name)):
                text, label = self.orchestrator(rel)
                # El pase del paquete se declara (byte-idéntico).
                self.require_any(text, BYTE_PASS_TOKENS,
                                 "pase del paquete byte-idéntico", label)
                # El enlace al protocolo de recibo (ancla exacta).
                self.assertIn(
                    RECEIPT_LINK_PHRASE, text.lower(),
                    msg=f"{label} no enlaza al «{RECEIPT_LINK_PHRASE}» "
                        "(PD-2(d)/PD-5(b): cada sección `delegation` enlaza "
                        "al protocolo de recibo; INV-3: el mismo `receive` "
                        "termina toda ruta)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
