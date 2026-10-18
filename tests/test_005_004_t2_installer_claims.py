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
  HOME) y el manifiesto de propiedad `<root>.cdad-install-manifest.json`
  (interfaz declarada de 004-001 T5, reusada por import desde
  `tests/test_install_ownership.py`: PD-9 no duplica el patrón).
- el generador de staging (`make staging` en una **copia** temporal del repo) y
  el generador de agentes — la ausencia de la línea `model:` es un hecho de
  GENERACIÓN (PD-2/PD-5).

ORACLE REPLACEMENTS (006-003 U2 — spec docs/specs/006-003-installer-single-
profile-delegation-config/spec.md, §2.1/PD-1a/D1; regla A-1 del plan: los tests
acoplados al perfil se reformulan declarando el reemplazo). Qué cambió y por qué,
para que ningún assert se caiga en silencio:

- `make staging PROFILE=<perfil>` → `make staging`: D1 retira el eje de perfiles
  del generador y del Makefile (PD-1b/PD-1f, unidad U1). El fixture
  `_isolated_profile_install(profile)` pasa a `_isolated_install()` (un solo
  caso) y su assert `staging_manifest["profile"] == profile` se REPLACE por
  «el staging fresco NO trae clave `profile`» (PD-1d).
- `install.sh --optimus` → `install.sh --basic`: PD-1a rechaza los flags de
  perfil y D1 conserva `--basic` como alias deprecado sin efecto. El control
  positivo de bytes verbatim (PD-2(ii)/AC-2) se conserva íntegro; lo que
  desaparece es el eje «perfil que fija modelos», porque ningún perfil fija
  modelos ya (INV-3/PD-1e).
- `manifest["profile"] == profile` → el manifiesto de propiedad NO registra
  `profile` (PD-1d/D1).
- El enunciado del adaptador que atribuía la ausencia de `model:` al «perfil de
  generación» se reformula a la causa vigente: el GENERADOR sin perfiles y sin
  mapa no emite `model:` (PD-1e/PD-1f). El reclamo de honestidad de PD-5(b) (el
  instalador NO garantiza la invariante anti-sesgo) se CONSERVA, reformulado sin
  perfiles (INV-5: garantizado por configuración o declarado, nunca silencio).

Mapa test → postcondición/criterio (un test por afirmación observable; el
«ROJO hoy» de la tabla original era el del RED de 005-004 y el GREEN de 005-004
ya lo resolvió — el estado por test está medido en la sección RED esperado):

- `test_pd2_i_sweep_no_declared_surface_claims_the_installer_removes_the_model_field`
      → PD-2(i) / AC-2                       (barrido; verde hoy)
- `test_pd2_ii_adapter_states_the_installer_deploys_staged_bytes_untransformed`
      → PD-2(ii) / AC-2                      (mecanismo real + coincidencia con
                                              `install.sh --help`; verde hoy)
- `test_pd2_ii_adapter_attributes_the_missing_model_line_to_the_generator`
      → PD-2(ii) / AC-2                      (causa = generador sin perfiles;
                                              REPLACE declarado de la variante
                                              «generation profile»; verde hoy)
- `test_pd5_adapter_declares_no_model_per_role`
      → PD-5(a) / AC-5                       (REPLACE declarado de la variante
                                              «under basic»; verde hoy)
- `test_pd5_adapter_declares_the_installer_does_not_guarantee_the_anti_bias_invariant`
      → PD-5(b) / AC-5                       (reclamo de honestidad CONSERVADO,
                                              encuadre sin perfiles; verde hoy)
- `test_pd5_adapter_references_the_exemption_source_instead_of_copying_it`
      → PD-5(c) / PD-9 / AC-5                (exención explícita por referencia;
                                              verde hoy)
- `test_pd2_ii_isolated_install_deploys_staged_cc_agent_bytes_verbatim`
      → PD-2(ii)/PD-1d / AC-2 (control positivo) (REPLACE del control por
                                              perfil: los bytes desplegados son
                                              los staged y el manifiesto no
                                              registra `profile`; ROJO hoy por
                                              PD-1d/D1)
- `test_pd1e_absence_of_model_lines_is_produced_by_the_generator`
      → PD-1e/PD-2(ii) / AC-5 (control)       (REPLACE de «basic profile
                                              absence»: la ausencia de `model:`
                                              la produce el generador sin
                                              perfiles; verde hoy)

RED esperado (MEDIDO contra el árbol de hoy, post-U1; se corrige el «ROJO hoy»
histórico del RED de 005-004, ya resuelto por su GREEN):

- Los cinco tests de enunciado/barrido (`test_pd2_i_*`, los dos
  `test_pd2_ii_adapter_*`, `test_pd5_adapter_*`) están **verdes** hoy: el GREEN
  de 005-004 ya reescribió el adaptador. Esta sesión NO debilita su oráculo: se
  conservan los grupos de co-ocurrencia y sólo se retiran los dos que el propio
  cambio vuelve falsos (`\bbasic\b`, y «generation profile» como CAUSA, que pasó
  a «generador/staging sin perfiles»).
- `test_pd2_ii_isolated_install_deploys_staged_cc_agent_bytes_verbatim` es
  **ROJO** hoy por el reemplazo declarado: el manifiesto de propiedad todavía
  registra `profile` (PD-1d/D1). Antes de esta sesión ya era rojo por el eje de
  perfiles retirado (U1), pero por una precondición del fixture; ahora falla por
  la aserción del contrato.
- `test_pd1e_absence_of_model_lines_is_produced_by_the_generator` es el control
  verde (PD-1e ya cumplido por U1: el staging fresco no trae `model:`).

Ningún fallo es `ImportError`/`SyntaxError`/`NameError`.

Límite declarado del barrido (PD-2(i)): las superficies declaradas por el
contrato son `sources/`, `skills/` e `install.sh`. La segunda ocurrencia que el
contrato nombra (`scripts/cdad-generate.py`, comentario `strip`, §9 `:443-446`)
queda **fuera** de esa superficie declarada y no se barre aquí; su corrección
está en el alcance de T2 (plan §4) y no la fuerza este focal.

Dependencia declarada (006-003 U3): los tres asserts sobre el ENUNCIADO del
adaptador (`sources/agents/adapters/claude-code.md`) quedan rojos hasta que U3
reescriba la sección `delegation` de los adaptadores (plan U3, PD-7b). Es una
regresión esperada y declarada, no un fallo nuevo.
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

# 006-003 U2 (A-1): sólo sobrevive el alias deprecado `--basic` (D1). El eje de
# perfiles (`basic` vs `optimus`) se retiró con el oráculo que lo describía.
DEPRECATED_ALIAS = "basic"
ALIAS_FLAG = f"--{DEPRECATED_ALIAS}"

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


def test_pd2_ii_adapter_attributes_the_missing_model_line_to_the_generator():
    """PD-2(ii)/AC-2 (REPLACE 006-003 U2 de la variante «generation profile»):
    el adaptador atribuye la ausencia de la línea `model:` al GENERADOR —que ya
    no tiene perfiles ni mapa de modelos (PD-1e/PD-1f, INV-3)—, no al
    instalador."""
    adapter = _read_text(ADAPTER, "PD-2(ii)")
    attributes_cause = co_occurs(
        adapter,
        [
            [r"generation", r"generator", r"generated", r"regenerated",
             r"at generation time", r"generation-time", r"staging",
             r"build/staging"],
            [r"model"],
            [r"absent", r"absence", r"missing", r"omitted", r"omits", r"omit",
             r"not present", r"no model", r"without a model", r"lacks",
             r"carries no", r"no longer"],
        ],
        window=45,
    )
    assert attributes_cause, (
        "PD-2(ii)/AC-2: el adaptador no atribuye la ausencia de la línea "
        "`model:` al generador/staging (que ya no tiene perfiles ni mapa: la "
        "línea nunca se produce), — hoy la atribuye al instalador o a un perfil"
    )


# ------------------------------- PD-5 — procedencia bajo el perfil `basic`


def test_pd5_adapter_declares_no_model_per_role():
    """PD-5(a)/AC-5 (REPLACE 006-003 U2 de la variante «under basic»): el
    adaptador declara que NO hay modelo por rol —ningún agente lleva `model:`—
    porque no hay perfiles ni modelo fijo por rol (INV-3/PD-1e); el modelo de la
    delegación externa se configura aparte (D3)."""
    adapter = _read_text(ADAPTER, "PD-5(a)")
    declared = co_occurs(
        adapter,
        [
            [r"\binstaller\b", r"\binstallation\b", r"\bgenerator\b",
             r"\bgenerated\b", r"\bagents?\b", r"\bcdad[-\w]*\.md\b"],
            [r"no per-role model", r"no per role model", r"no model",
             r"without a model", r"no fixed model", r"no models",
             r"model:.*(absent|missing|omitted|not present)",
             r"(absent|missing|omitted|not present).*model"],
            [r"per-role", r"per role", r"role", r"roles", r"dispatch"],
        ],
        window=45,
    )
    assert declared, (
        "PD-5(a)/AC-5: el adaptador no declara que no hay modelo por rol "
        "(ningún agente lleva `model:` y no hay perfiles que lo fijen) — la "
        "procedencia del modelo quedaría implícita"
    )


def test_pd5_adapter_declares_the_installer_does_not_guarantee_the_anti_bias_invariant():
    """PD-5(b)/AC-5 (reclamo de honestidad CONSERVADO; encuadre reformulado en
    006-003 U2): el adaptador declara que el instalador NO garantiza la
    invariante reviewer≠implementer —nunca como invariante satisfecha—. Sin
    perfiles ni modelo por rol (INV-3/PD-1e), la garantía sólo puede venir de la
    configuración de delegación o declararse como no garantizada (INV-5: nunca
    silencio); el ajuste del enunciado pertenece a U3 (PD-7b)."""
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
        "invariante satisfecha en silencio (INV-5: garantizado por "
        "configuración o declarado)"
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
def _isolated_install() -> dict:
    """Genera el staging en la copia (`make staging`, ya sin perfiles: U1) y lo
    instala en una raíz AISLADA (`CDAD_INSTALL_ROOT` → temporal, nunca HOME),
    devolviendo los bytes staged y los desplegados de los agentes de Claude Code.

    REPLACE 006-003 U2: el fixture era `_isolated_profile_install(profile)`
    (`make staging PROFILE=<perfil>` + `install.sh --<perfil>`). D1 retira el eje
    de perfiles; queda UN caso instalado con el alias deprecado `--basic` y el
    assert de perfil se invierte a «no hay clave `profile`».
    """
    sandbox = _sandbox_root()
    staged_result = subprocess.run(
        ["make", "staging"],
        cwd=str(sandbox),
        text=True,
        capture_output=True,
        check=False,
    )
    assert staged_result.returncode == 0, (
        f"fixture T2: `make staging` falló "
        f"(rc={staged_result.returncode}): {staged_result.stderr!r}"
    )
    staging_manifest = load_staging_manifest(sandbox)
    assert "profile" not in staging_manifest, (
        "fixture T2 (PD-1d/D1): el staging generado todavía trae la clave "
        f"`profile` ({staging_manifest.get('profile')!r}) — el generador no "
        "tiene perfiles"
    )
    staged_dir = sandbox / "build" / "staging" / "agents" / "claude-code"
    staged = {
        path.name: path.read_bytes()
        for path in sorted(staged_dir.glob("*.md"))
        if path.is_file()
    }
    assert len(staged) >= 10, (
        "fixture T2: el staging no trae los agentes de Claude "
        f"Code (encontrados {len(staged)})"
    )

    root = Path(tempfile.mkdtemp(prefix="cdad-t2-install-root-"))
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

    result = run_installer(sandbox, root, ALIAS_FLAG)
    assert result.returncode == 0, (
        f"fixture T2: la instalación aislada falló "
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
        f"fixture T2: la instalación no desplegó los "
        f"agentes de Claude Code (encontrados {len(deployed)})"
    )
    return {
        "staged": staged,
        "deployed": deployed,
        "mapping": mapping,
        "manifest": manifest,
        "conflicts": manifest.get("conflicts"),
    }


def _model_line_holders(blobs: dict[str, bytes]) -> list[str]:
    return sorted(
        name for name, data in blobs.items() if MODEL_LINE_RE.search(data.decode())
    )


def test_pd2_ii_isolated_install_deploys_staged_cc_agent_bytes_verbatim():
    """PD-2(ii)/PD-1d / AC-2 (control positivo, REPLACE 006-003 U2): en una raíz
    aislada, los bytes desplegados de los agentes de Claude Code SON los bytes
    staged (sin transformación) y el manifiesto de propiedad NO registra
    `profile` (D1: el instalador no tiene perfiles; el staging que consume
    tampoco). El control «la línea `model:` del perfil viaja» se retira con el
    eje de perfiles: ningún staging fija modelos ya (INV-3/PD-1e)."""
    data = _isolated_install()
    assert data["conflicts"] == [], (
        "PD-2(ii)/AC-2: la instalación aislada reportó conflictos; el control "
        f"de bytes desplegados no es limpio: {data['conflicts']}"
    )
    assert "profile" not in data["manifest"], (
        "PD-2(ii)/PD-1d: el manifiesto de propiedad todavía registra `profile` "
        f"({data['manifest'].get('profile')!r}); el instalador no tiene perfiles"
    )
    assert sorted(data["mapping"]) == sorted(
        f"{CC_PREFIX}{name}" for name in data["staged"]
    ), (
        "PD-2(ii): el conjunto de agentes de Claude Code desplegado no es el "
        f"conjunto staged (desplegado {sorted(data['mapping'])}, staged "
        f"{sorted(data['staged'])})"
    )

    staged_with_model = _model_line_holders(data["staged"])
    assert staged_with_model == [], (
        "PD-2(ii)/PD-1e (control): el staging SÍ trae la línea `model:` en "
        f"{staged_with_model} — el generador sin perfiles no la produce"
    )
    deployed_with_model = _model_line_holders(data["deployed"])
    assert deployed_with_model == [], (
        "PD-2(ii)/PD-1e: la salida desplegada lleva la línea `model:` en "
        f"{deployed_with_model} — ningún texto instalable fija modelos"
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


def test_pd1e_absence_of_model_lines_is_produced_by_the_generator():
    """PD-1e/PD-2(ii) (control, REPLACE 006-003 U2 de «basic profile absence»):
    la línea `model:` no existe ya en staging (la ausencia la produce el
    GENERADOR sin perfiles ni mapa) y tampoco en la salida desplegada, que sigue
    siendo copia de los bytes staged."""
    data = _isolated_install()
    staged_with_model = _model_line_holders(data["staged"])
    assert staged_with_model == [], (
        "PD-2(ii)/PD-1e (control): el staging trae la línea "
        f"`model:` en {staged_with_model} — la ausencia no vendría del generador"
    )
    deployed_with_model = _model_line_holders(data["deployed"])
    assert deployed_with_model == [], (
        "PD-2(ii)/PD-1e (control): la salida desplegada lleva la línea "
        f"`model:` en {deployed_with_model} — incompatible con un staging sin "
        "modelos fijos"
    )
    not_verbatim = sorted(
        source
        for source, data_bytes in data["deployed"].items()
        if data_bytes != data["staged"][Path(source).name]
    )
    assert not_verbatim == [], (
        "PD-2(ii)/AC-2: los bytes desplegados tampoco son los "
        f"bytes staged (el instalador transformó el contenido): {not_verbatim}"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
