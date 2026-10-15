#!/usr/bin/env python3
"""005-004 T2 RED — enunciados del adaptador CC reconciliados (PD-2, PD-5, PD-9).

Contrato (oráculo):
- `docs/specs/005-004-claude-code-roles/spec.md` — §2 (tabla de contrato),
  §3 PD-2 (i)-(iii) y PD-5 (a)-(c), §4 INV-2/INV-4, §5 AC-2 y AC-5
  (sha256 79d57e0a…).
- `docs/specs/005-004-claude-code-roles/plan.md` — ficha T2 y su bloque
  `plan-tasks` (focal declarado: `tests/test_005_004_t2_installer_claims.py`).

El oráculo NO se deriva de la implementación: no se leen `sources/`, `skills/`,
`scripts/` ni `install.sh` para escribirlo. Se lee el **enunciado** que el
contrato manda corregir (el adaptador, dueño del texto) y se **ejecutan**
artefactos declarados:

- `install.sh --help` — ayuda publicada por el propio instalador (el contrato
  cita textualmente «the installer transforms nothing», install.sh:388-396):
  es la verdad de referencia con la que el enunciado del adaptador debe
  coincidir (PD-2/AC-2).
- la instalación en **raíz aislada** (`CDAD_INSTALL_ROOT` → temporal, nunca
  HOME) y el manifiesto de propiedad `<root>/.cdad-install-manifest.json`
  (interfaz declarada de 004-001 T5, reusada por import desde
  `tests/test_install_ownership.py`: PD-9 no duplica el patrón).
- el generador de staging (`make staging PROFILE=<perfil>` en una **copia**
  temporal del repo) y el generador de agentes — la ausencia de la línea
  `model:` bajo `basic` es un hecho de GENERACIÓN (PD-2/PD-5).

Mapa test → postcondición/criterio (un test por afirmación observable):

- `test_pd2_i_sweep_no_declared_surface_claims_the_installer_removes_the_model_field`
      → PD-2(i) / AC-2                       (barrido; ROJO hoy)
- `test_pd2_ii_adapter_states_the_installer_deploys_staged_bytes_untransformed`
      → PD-2(ii) / AC-2                      (mecanismo real + coincidencia con
                                              `install.sh --help`; ROJO hoy)
- `test_pd2_ii_adapter_attributes_the_missing_model_line_to_the_generation_profile`
      → PD-2(ii) / AC-2                      (causa = perfil de generación; ROJO hoy)
- `test_pd5_adapter_declares_no_model_per_role_under_basic`
      → PD-5(a) / AC-5                       (ROJO hoy)
- `test_pd5_adapter_declares_the_installer_does_not_guarantee_the_anti_bias_invariant`
      → PD-5(b) / AC-5                       (ROJO hoy)
- `test_pd5_adapter_references_the_exemption_source_instead_of_copying_it`
      → PD-5(c) / PD-9 / AC-5                (exención explícita por referencia;
                                              ROJO hoy)
- `test_pd2_ii_isolated_install_deploys_staged_cc_agent_bytes_verbatim`
      → PD-2(ii) / AC-2 (control positivo)   (verde hoy: el instalador ya copia
                                              los bytes staged y la línea
                                              `model:` del perfil viaja)
- `test_pd2_ii_basic_profile_absence_is_produced_by_the_generator`
      → PD-2(ii), PD-5 / AC-5 (control)      (verde hoy: bajo `basic` la línea
                                              `model:` la omite el generador)

RED esperado: los seis primeros fallan por `AssertionError` (el adaptador hoy
afirma que el instalador quita el campo `model` y hoy no enuncia el mecanismo
real, la causa por perfil ni la procedencia bajo `basic`); los dos controles de
instalación quedan verdes hoy. Ningún fallo es `ImportError`/`SyntaxError`/
`NameError`.

Límite declarado del barrido (PD-2(i)): las superficies declaradas por el
contrato son `sources/`, `skills/` e `install.sh`. La segunda ocurrencia que el
contrato nombra (`scripts/cdad-generate.py`, comentario `strip`, §9 `:443-446`)
queda **fuera** de esa superficie declarada y no se barre aquí; su corrección
está en el alcance de T2 (plan §4) y no la fuerza este focal.
"""

from __future__ import annotations

import atexit
import functools
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Patrón de instalación aislada ya existente en la superficie de tests (la
# regresión declarada `tests/test_install_ownership.py`): se REUSA por import,
# no se duplica (PD-9).
from tests.test_install_ownership import (
    load_install_manifest,
    load_staging_manifest,
    run_installer,
)

REPO = Path(__file__).resolve().parents[1]

INSTALLER = REPO / "install.sh"
ADAPTER = REPO / "sources" / "agents" / "adapters" / "claude-code.md"
GUARD = REPO / "scripts" / "validate-subagents.sh"

# Superficies del barrido tal como las fija PD-2(i).
SWEEP_ROOTS = ("sources", "skills")
SWEEP_FILES = (INSTALLER,)
# Suelo anti-vacuidad: si el barrido no recorre un corpus real, no prueba nada.
SWEEP_MIN_FILES = {"sources": 5, "skills": 50}

# La línea de modelo del frontmatter (lo que el contrato discute: `model:`).
MODEL_LINE_RE = re.compile(r"(?m)^model:")
MODEL_WORD_RE = re.compile(r"(?i)\bmodel\b")

# Perfiles del contrato: `basic` (sin modelos fijos) y uno que SÍ fija modelos.
BASIC_PROFILE = "basic"
MODELED_PROFILE = "optimus"

CC_PREFIX = "agents/claude-code/"


# ------------------------------------------------------------------ helpers


def _read_text(path: Path, why: str) -> str:
    """Lee una superficie declarada por el contrato; si falta, es una aserción
    de contrato (AssertionError), nunca un ImportError."""
    assert path.is_file(), (
        f"{why}: la superficie declarada por el contrato no existe: "
        f"{_rel(path)}"
    )
    return path.read_text(encoding="utf-8")


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[^\s]+", text.lower().replace("`", ""))


def co_occurs(text: str, groups: list[list[str]], window: int = 45) -> bool:
    """¿Enunciado presente? Verdadero si alguna ventana de `window` palabras
    contiene al menos una coincidencia de CADA grupo de alternativas.

    El oráculo es de CONTENIDO declarado (el contrato enuncia qué debe decir el
    adaptador), no de plantilla: las alternativas cubren las formas razonables
    del enunciado.
    """
    words = _tokens(text)
    for start in range(len(words)):
        segment = " ".join(words[start:start + window])
        if all(
            any(re.search(alt, segment) for alt in group) for group in groups
        ):
            return True
    return False


def _has(text: str, *alternatives: str) -> bool:
    """Busca alternativas en el texto completo, por línea (una afirmación del
    adaptador vive en su propia línea o viñeta). Devuelve bool para no volcar
    contenido de la fuente en el log de pytest."""
    for line in text.splitlines():
        lowered = line.lower()
        for alt in alternatives:
            if re.search(alt, lowered):
                return True
    return False


# --------------------------------------------------------- PD-2(i) — barrido

# Verbos que afirman quitar/recortar (el repo es bilingüe). `quit`/`quita` se
# tratan aparte: exigen el objeto «model» inmediatamente después.
REMOVAL_VERB_RE = re.compile(
    r"(?i)\b(?:strip(?:s|ped|ping)?|remov(?:e|es|ed|ing)|trim(?:s|med|ming)?|"
    r"cut(?:s|ting)?|drop(?:s|ped|ping)?|discard(?:s|ed|ing)?|"
    r"recort(?:a|as|an|e|es|en|ado|ada|ando)?|"
    r"elimin(?:a|as|an|e|es|en|ado|ada|ando)?|"
    r"borr(?:a|as|an|e|es|en|ado|ada|ando)?|remuev(?:e|en|an)?)\b"
)
QUIT_VERB_RE = re.compile(r"(?i)\b(?:quit(?:s|ting)?|quita(?:r|do|da|n|s)?)\b")
NEGATION_BEFORE_RE = re.compile(
    r"(?i)(?:^|[^0-9A-Za-z_])(?:not|n['’]t|never|no|without|sin|nunca|jam[áa]s|"
    r"tampoco)\W*$"
)
# Negación por objeto: «strips nothing» / «no quita nada» no es una afirmación
# de remoción.
NEGATION_AFTER_RE = re.compile(r"(?i)^[\s,;:]*?(?:nothing|nada)\b")


def removal_claim_lines(text: str) -> list[int]:
    """Líneas que AFIRMAN que algo quita/recorta el campo `model:`.

    Una NEGACIÓN («the installer does not strip the model field») no es una
    afirmación de strip: no se marca (el contrato prohíbe afirmar que el
    instalador quita el campo, no decir que no lo hace).
    """
    hits: list[int] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        low = line.lower()
        matched = False
        for pattern, requires_object_after in (
            (REMOVAL_VERB_RE, False),
            (QUIT_VERB_RE, True),
        ):
            for match in pattern.finditer(low):
                prefix = low[max(0, match.start() - 32):match.start()]
                if NEGATION_BEFORE_RE.search(prefix):
                    continue
                if NEGATION_AFTER_RE.match(low[match.end():match.end() + 20]):
                    continue
                window = low[max(0, match.start() - 90):match.end() + 90]
                if not MODEL_WORD_RE.search(window):
                    continue
                if requires_object_after and not MODEL_WORD_RE.search(
                    low[match.end():match.end() + 40]
                ):
                    continue
                hits.append(lineno)
                matched = True
                break
            if matched:
                break
    return hits


def _text_files(root: Path) -> list[Path]:
    """Archivos de texto legibles bajo `root` (los binarios no son enunciados)."""
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if b"\0" in data:
            continue
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        files.append(path)
    return files


def test_pd2_i_sweep_no_declared_surface_claims_the_installer_removes_the_model_field():
    """PD-2(i)/AC-2: ninguna de las superficies declaradas (`sources/`,
    `skills/`, `install.sh`) afirma que el instalador quita o recorta el campo
    `model:`. Control de vacuidad: el barrido recorre un corpus real y el
    predicado detecta la afirmación que el contrato cita textualmente (y no
    marca su negación)."""
    # Control de vacuidad (1): el predicado detecta la afirmación del contrato
    # y no su negación. Es la frase que el contrato cita («the installer STRIPS
    # the model field at install time») y su forma correcta.
    assert removal_claim_lines(
        "The installer STRIPS the model field at install time."
    ) == [1], (
        "PD-2(i): el predicado del barrido no detecta la afirmación que el "
        "contrato cita — el barrido sería vacuo"
    )
    assert removal_claim_lines(
        "The installer does not strip the model field: it deploys the staged "
        "bytes untransformed."
    ) == [], (
        "PD-2(i): el predicado marca una NEGACIÓN como si fuera una "
        "afirmación de strip — el barrido daría falsos positivos"
    )
    assert removal_claim_lines(
        "El instalador quita el campo `model` al instalar."
    ) == [1], (
        "PD-2(i): el predicado del barrido no detecta la afirmación en "
        "castellano — el barrido no cubriría el corpus bilingüe"
    )
    assert removal_claim_lines(
        "The installer strips nothing: the staged bytes keep the model line."
    ) == [], (
        "PD-2(i): el predicado marca «strips nothing» (negación por objeto) "
        "como afirmación de remoción — el barrido daría falsos positivos"
    )

    # Control de vacuidad (2): el corpus declarado existe y es real.
    corpus: list[Path] = []
    for name in SWEEP_ROOTS:
        root = REPO / name
        assert root.is_dir(), (
            f"PD-2(i): la superficie declarada {name}/ no existe — el barrido "
            "no es verificable"
        )
        files = _text_files(root)
        assert len(files) >= SWEEP_MIN_FILES[name], (
            f"PD-2(i): el barrido de {name}/ recorrió sólo {len(files)} "
            f"archivos de texto (suelo {SWEEP_MIN_FILES[name]}) — el barrido "
            "sería vacuo"
        )
        corpus.extend(files)
    for path in SWEEP_FILES:
        assert path.is_file(), (
            f"PD-2(i): la superficie declarada {_rel(path)} no existe — el "
            "barrido no es verificable"
        )
        corpus.append(path)

    offenders = [
        f"{_rel(path)}:{lineno}"
        for path in corpus
        for lineno in removal_claim_lines(path.read_text(encoding="utf-8"))
    ]
    assert offenders == [], (
        "PD-2(i)/AC-2: hay afirmaciones de que el instalador quita o recorta "
        "el campo `model:` en las superficies declaradas (el instalador "
        f"despliega los bytes staged sin transformarlos): {offenders}"
    )


# ------------------------------------- PD-2(ii) — mecanismo real y su causa


def _installer_help() -> tuple[int, str]:
    """Ayuda publicada por el instalador (superficie observable declarada por
    PD-2/AC-2; nunca HOME: `--help` no instala nada)."""
    assert INSTALLER.is_file(), (
        f"PD-2(ii)/AC-2: el instalador declarado {_rel(INSTALLER)} no existe"
    )
    result = subprocess.run(
        ["bash", str(INSTALLER), "--help"],
        cwd=str(REPO),
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode, result.stdout + result.stderr


def test_pd2_ii_adapter_states_the_installer_deploys_staged_bytes_untransformed():
    """PD-2(ii)/AC-2: el adaptador enuncia el mecanismo real —el instalador
    despliega los bytes staged sin transformarlos— y coincide con la ayuda del
    instalador («the installer transforms nothing»)."""
    # Verdad de referencia (control): la ayuda del instalador es la fuente con
    # la que el enunciado debe coincidir (PD-2, AC-2).
    rc, help_text = _installer_help()
    assert rc == 0, (
        f"PD-2(ii)/AC-2: `install.sh --help` devolvió rc={rc}; la verdad de "
        "referencia del enunciado no es observable"
    )
    help_transforms_nothing = bool(
        re.search(r"(?i)installer\s+transforms\s+nothing", help_text)
    )
    assert help_transforms_nothing, (
        "PD-2(ii)/AC-2: la ayuda del instalador ya no declara «the installer "
        "transforms nothing» — la verdad de referencia del enunciado cambió "
        "(el contrato T2 no toca install.sh)"
    )
    help_deploys_staged = bool(
        re.search(r"(?i)deployed bytes are the staged bytes", help_text)
    )
    assert help_deploys_staged, (
        "PD-2(ii)/AC-2: la ayuda del instalador ya no declara que los bytes "
        "desplegados son los staged — la verdad de referencia del enunciado "
        "cambió (el contrato T2 no toca install.sh)"
    )

    # El enunciado del adaptador debe enunciar el MISMO mecanismo.
    adapter = _read_text(ADAPTER, "PD-2(ii)")
    states_mechanism = co_occurs(
        adapter,
        [
            [r"copy", r"copies", r"copied", r"cp -p", r"deploy", r"deploys",
             r"deployed", r"install", r"installs", r"installed",
             r"installation"],
            [r"staged"],
            [r"without transform", r"untransformed", r"transforms? nothing",
             r"does not transform", r"never transforms", r"no transformation",
             r"not transform", r"verbatim", r"byte-for-byte", r"as-is",
             r"unchanged"],
        ],
        window=50,
    )
    assert states_mechanism, (
        "PD-2(ii)/AC-2: el adaptador no enuncia el mecanismo real (los "
        "agentes se despliegan como copia de los bytes staged, sin "
        "transformación) — hoy afirma lo contrario"
    )


def test_pd2_ii_adapter_attributes_the_missing_model_line_to_the_generation_profile():
    """PD-2(ii)/AC-2: el adaptador atribuye la ausencia de la línea `model:`
    bajo el perfil vigente al PERFIL DE GENERACIÓN (lo omite el generador),
    no al instalador."""
    adapter = _read_text(ADAPTER, "PD-2(ii)")
    attributes_cause = co_occurs(
        adapter,
        [
            [r"generation-time profile", r"generation time profile",
             r"generation profile", r"generation-time", r"at generation time",
             r"generator", r"generated", r"regenerated"],
            [r"model"],
            [r"absent", r"absence", r"missing", r"omitted", r"omits", r"omit",
             r"not present", r"no model", r"without a model", r"lacks"],
        ],
        window=45,
    )
    assert attributes_cause, (
        "PD-2(ii)/AC-2: el adaptador no atribuye la ausencia de la línea "
        "`model:` al perfil de generación (el generador la omite cuando el "
        "modelo es vacío) — hoy la atribuye al instalador"
    )


# ------------------------------- PD-5 — procedencia bajo el perfil `basic`


def test_pd5_adapter_declares_no_model_per_role_under_basic():
    """PD-5(a)/AC-5: el adaptador declara que bajo el perfil `basic` no hay
    modelo por rol (los agentes no llevan `model:`)."""
    adapter = _read_text(ADAPTER, "PD-5(a)")
    declared = co_occurs(
        adapter,
        [
            [r"\bbasic\b"],
            [r"no per-role model", r"no per role model", r"no model",
             r"without a model", r"no fixed model", r"no models",
             r"model:.*(absent|missing|omitted|not present)",
             r"(absent|missing|omitted|not present).*model"],
            [r"per-role", r"per role", r"role", r"roles", r"dispatch"],
        ],
        window=45,
    )
    assert declared, (
        "PD-5(a)/AC-5: el adaptador no declara que bajo el perfil `basic` no "
        "hay modelo por rol — la procedencia del modelo quedaría implícita"
    )


def test_pd5_adapter_declares_the_installer_does_not_guarantee_the_anti_bias_invariant():
    """PD-5(b)/AC-5: el adaptador declara que el instalador NO garantiza la
    invariante reviewer≠implementer bajo el perfil vigente (nunca como
    invariante satisfecha)."""
    adapter = _read_text(ADAPTER, "PD-5(b)")
    declared = co_occurs(
        adapter,
        [
            [r"installer", r"installation", r"install"],
            [r"does not guarantee", r"doesn't guarantee", r"not guaranteed",
             r"no guarantee", r"cannot guarantee", r"does not enforce",
             r"not enforced", r"is not enforced", r"no la garantiza"],
            [r"reviewer", r"implementer", r"anti-bias", r"invariant", r"bias"],
        ],
        window=55,
    )
    assert declared, (
        "PD-5(b)/AC-5: el adaptador no declara que el instalador no garantiza "
        "la invariante reviewer≠implementer — la exención quedaría como "
        "invariante satisfecha en silencio"
    )


def _verbatim_runs(from_text: str, of_text: str, size: int = 12) -> int:
    """Cuenta las corridas de `size` tokens de `from_text` que aparecen
    literalmente en `of_text` (copia textual)."""
    source = _tokens(from_text)
    target = " ".join(_tokens(of_text))
    runs = 0
    for index in range(len(source) - size + 1):
        if " ".join(source[index:index + size]) in target:
            runs += 1
    return runs


def test_pd5_adapter_references_the_exemption_source_instead_of_copying_it():
    """PD-5(c)/PD-9/AC-5: el adaptador declara la exención como EXPLÍCITA y
    VISIBLE y la REFERENCIA por su fuente (`scripts/validate-subagents.sh` /
    `ADR-007`), sin copiar el texto del dueño (fuente única)."""
    adapter = _read_text(ADAPTER, "PD-5(c)")
    explicit = co_occurs(
        adapter,
        [
            [r"exempt", r"exempts", r"exemption", r"exención", r"exencion",
             r"exime", r"waiv"],
            [r"explicit", r"explicitly", r"explícita", r"explicita", r"visible",
             r"declared", r"not silent", r"nunca silencios"],
        ],
        window=45,
    )
    assert explicit, (
        "PD-5(c)/AC-5: el adaptador no declara que la exención de la "
        "invariante es explícita y visible — quedaría silenciosa"
    )
    references_owner = _has(
        adapter, r"validate-subagents", r"adr[- _]?007", r"adr 007"
    )
    assert references_owner, (
        "PD-5(c)/PD-9: el adaptador no REFERENCIA la fuente de la exención "
        "(scripts/validate-subagents.sh / ADR-007) — una regla con dueño no "
        "se re-enuncia sin dueño"
    )

    # «sin copiarla»: ninguna corrida larga del adaptador puede aparecer
    # literalmente en el dueño (guarda la fuente única, PD-9). El mensaje no
    # vuelca el contenido comparado.
    guard_text = _read_text(GUARD, "PD-5(c)/PD-9")
    copied = _verbatim_runs(adapter, guard_text)
    assert copied == 0, (
        "PD-5(c)/PD-9: el adaptador copia texto del dueño de la exención "
        f"({_rel(GUARD)}): {copied} corrida(s) verbatim de 12 tokens — debe "
        "referenciarlo, no copiarlo"
    )


# --------------------------- PD-2(ii) — la instalación en RAIZ AISLADA


@functools.lru_cache(maxsize=None)
def _sandbox_root() -> Path:
    """Copia temporal del repo (nunca el checkout real) para generar staging
    por perfil y ejecutar el instalador: el fixture no escribe en el repo."""
    tmp = Path(tempfile.mkdtemp(prefix="cdad-t2-sandbox-"))
    atexit.register(shutil.rmtree, tmp, ignore_errors=True)
    sandbox = tmp / "product"
    shutil.copytree(
        REPO,
        sandbox,
        symlinks=True,
        ignore=shutil.ignore_patterns(
            ".git", ".cdad", "build", "logs", ".pytest_cache", "__pycache__"
        ),
    )
    return sandbox


@functools.lru_cache(maxsize=None)
def _isolated_profile_install(profile: str) -> dict:
    """Genera el staging del perfil pedido en la copia y lo instala en una raíz
    AISLADA (`CDAD_INSTALL_ROOT` → temporal, nunca HOME), devolviendo los bytes
    staged y los desplegados de los agentes de Claude Code."""
    sandbox = _sandbox_root()
    staged_result = subprocess.run(
        ["make", "staging", f"PROFILE={profile}"],
        cwd=str(sandbox),
        text=True,
        capture_output=True,
        check=False,
    )
    assert staged_result.returncode == 0, (
        f"fixture T2: `make staging PROFILE={profile}` falló "
        f"(rc={staged_result.returncode}): {staged_result.stderr!r}"
    )
    staging_manifest = load_staging_manifest(sandbox)
    assert staging_manifest.get("profile") == profile, (
        "fixture T2: el staging generado no tiene el perfil pedido "
        f"(pedido {profile!r}, obtenido {staging_manifest.get('profile')!r}) "
        "— el caso por perfil no es verificable"
    )
    staged_dir = sandbox / "build" / "staging" / "agents" / "claude-code"
    staged = {
        path.name: path.read_bytes()
        for path in sorted(staged_dir.glob("*.md"))
        if path.is_file()
    }
    assert len(staged) >= 10, (
        f"fixture T2: el staging de `{profile}` no trae los agentes de Claude "
        f"Code (encontrados {len(staged)})"
    )

    root = Path(tempfile.mkdtemp(prefix=f"cdad-t2-{profile}-root-"))
    atexit.register(shutil.rmtree, root, ignore_errors=True)
    tmp_dir = Path(tempfile.gettempdir()).resolve()
    assert root.resolve().is_relative_to(tmp_dir), (
        f"fixture T2: la raíz de instalación aislada {root} no está bajo "
        f"{tmp_dir}"
    )
    assert not root.resolve().is_relative_to(Path.home().resolve()), (
        f"fixture T2: la raíz de instalación aislada {root} está bajo HOME — "
        "el contrato prohíbe instalar en HOME"
    )

    result = run_installer(sandbox, root, f"--{profile}")
    assert result.returncode == 0, (
        f"fixture T2: la instalación aislada del perfil `{profile}` falló "
        f"(rc={result.returncode}): {result.stderr or result.stdout}"
    )
    manifest = load_install_manifest(root)
    deployed: dict[str, bytes] = {}
    mapping: dict[str, str] = {}
    for dest, record in manifest["artifacts"].items():
        source = str(record.get("source", ""))
        if source.startswith(CC_PREFIX):
            mapping[source] = dest
            deployed[source] = (root / dest).read_bytes()
    assert len(deployed) >= 10, (
        f"fixture T2: la instalación del perfil `{profile}` no desplegó los "
        f"agentes de Claude Code (encontrados {len(deployed)})"
    )
    return {
        "profile": profile,
        "staged": staged,
        "deployed": deployed,
        "mapping": mapping,
        "manifest_profile": manifest.get("profile"),
        "conflicts": manifest.get("conflicts"),
    }


def _model_line_holders(blobs: dict[str, bytes]) -> list[str]:
    return sorted(
        name for name, data in blobs.items() if MODEL_LINE_RE.search(data.decode())
    )


def test_pd2_ii_isolated_install_deploys_staged_cc_agent_bytes_verbatim():
    """PD-2(ii)/AC-2 (control positivo): en una raíz aislada, los bytes
    desplegados de los agentes de Claude Code SON los bytes staged (sin
    transformación) y, en un perfil que fija modelos, la línea `model:` viaja
    a la salida (el instalador no la quita)."""
    data = _isolated_profile_install(MODELED_PROFILE)
    assert data["conflicts"] == [], (
        "PD-2(ii)/AC-2: la instalación aislada reportó conflictos; el control "
        f"de bytes desplegados no es limpio: {data['conflicts']}"
    )
    assert data["manifest_profile"] == MODELED_PROFILE, (
        "PD-2(ii): el manifiesto de propiedad no registró el perfil del "
        f"staging desplegado ({data['manifest_profile']!r})"
    )
    assert sorted(data["mapping"]) == sorted(
        f"{CC_PREFIX}{name}" for name in data["staged"]
    ), (
        "PD-2(ii): el conjunto de agentes de Claude Code desplegado no es el "
        f"conjunto staged (desplegado {sorted(data['mapping'])}, staged "
        f"{sorted(data['staged'])})"
    )

    staged_with_model = _model_line_holders(data["staged"])
    assert staged_with_model, (
        f"PD-2(ii)/AC-2 (control positivo): el perfil `{MODELED_PROFILE}` no "
        "staged ningún agente de Claude Code con línea `model:` — el control "
        "positivo no demuestra nada"
    )
    deployed_with_model = _model_line_holders(data["deployed"])
    assert deployed_with_model, (
        "PD-2(ii)/AC-2 (control positivo): ningún agente de Claude Code "
        f"desplegado lleva la línea `model:` staged ({staged_with_model} la "
        "llevan en staging) — la línea NO viaja a la salida"
    )

    not_verbatim = sorted(
        source
        for source, data_bytes in data["deployed"].items()
        if data_bytes != data["staged"][Path(source).name]
    )
    assert not_verbatim == [], (
        "PD-2(ii)/AC-2: los bytes desplegados de los agentes de Claude Code "
        "NO son los bytes staged (el instalador transformó el contenido): "
        f"{not_verbatim}"
    )


def test_pd2_ii_basic_profile_absence_is_produced_by_the_generator():
    """PD-2(ii)/PD-5/AC-5 (control): bajo el perfil `basic` la línea `model:`
    no existe ya en staging (la omite el GENERADOR) y tampoco en la salida
    desplegada, que sigue siendo copia de los bytes staged."""
    data = _isolated_profile_install(BASIC_PROFILE)
    assert data["manifest_profile"] == BASIC_PROFILE, (
        "PD-5/AC-5: el manifiesto de propiedad no registró el perfil `basic` "
        f"del staging desplegado ({data['manifest_profile']!r})"
    )
    staged_with_model = _model_line_holders(data["staged"])
    assert staged_with_model == [], (
        "PD-2(ii)/PD-5 (control): bajo `basic` el staging SÍ trae la línea "
        f"`model:` en {staged_with_model} — la ausencia no vendría del "
        "generador"
    )
    deployed_with_model = _model_line_holders(data["deployed"])
    assert deployed_with_model == [], (
        "PD-2(ii)/PD-5 (control): la salida desplegada bajo `basic` lleva la "
        f"línea `model:` en {deployed_with_model} — incompatible con un "
        "staging sin modelos fijos"
    )
    not_verbatim = sorted(
        source
        for source, data_bytes in data["deployed"].items()
        if data_bytes != data["staged"][Path(source).name]
    )
    assert not_verbatim == [], (
        "PD-2(ii)/AC-2: bajo `basic` los bytes desplegados tampoco son los "
        f"bytes staged (el instalador transformó el contenido): {not_verbatim}"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
