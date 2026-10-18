#!/usr/bin/env python3
"""005-010 T3 RED — Referencias de la delegación actualizadas (PD-10; INV-7).

Contract: docs/specs/005-010-real-opencode-delegation/spec.md (PD-10; INV-7)
+ plan.md §T3. T3 edita DOS referencias de la metodología (archivos disjuntos
de T1/T2, paralelas):

  - skills/cdad-cycle/references/cli-delegation.md — documenta el contrato
    de la SEÑAL DURABLE REAL (store SQLite en SOLO LECTURA declarado por
    `sessions_db` de la config, correlación por `--session` elegida por el
    adaptador, FALLO CERRADO ante esquema desconocido, clasificación por el
    `idle_outcome` de la fila) y dónde viven `standalone`/`server`/`auto`
    (configuración de ejecución, no hardcode);
  - skills/cdad-cycle/references/opencode-delegation.md — actualiza el MODO
    DE CARGA (`mode: subagent` = entry NO interactiva válida en la versión
    instalada; identidad verificada desde la FILA DURABLE, sin fallback) y
    REEMPLAZA la tabla de modelos obsoleta por un PUNTERO a la ÚNICA tabla
    de modelos (`scripts/cdad-models.sh` + perfil activo), sin nombres de
    modelo concretos.

REFORMULADO por 006-002 U3 (PD-9; enmienda A-1): la segunda referencia sale del
árbol instalable (PD-9) y su detalle —modo de carga, identidad durable sin
fallback, puntero a la tabla única de modelos— se preserva como evidencia NO
instalable bajo `docs/**`. Las dos aserciones de la mitad OpenCode se repuntan
a esa evidencia (la COPIA PRESERVADA de la referencia, localizada por el helper
único `preservation_copy_documents()` de
`tests/test_006_002_u3_runtime_references.py` —por su declaración de
preservación, no por una ruta; testfix U3—) y agregan el assert de retiro; la
mitad `cli-delegation.md` (PD-10 de esta feature) sigue igual porque ese
documento permanece instalable. INV-7 sigue aplicando sólo a texto INSTALABLE:
la evidencia no instalable queda fuera de su alcance por diseño (PD-9), y la
mitad OpenCode de INV-7 la retira el mismo retiro del archivo del árbol.

MARCADORES ESTRUCTURALES (elección declarada del oráculo; plan §T3
«criterio de prosa»: no se fijan frases del prompt ni nombres internos —
la PROSA se verifica por review en stage 4). Este módulo usa:
  - CONCEPTOS CLAVE del contrato durable y del modo de carga, con
    alternativas de idioma (los papeles de referencia están en inglés y
    español; el oráculo exige el concepto, no una redacción);
  - AUSENCIA de patrones prohibidos (INV-7): artefactos de la señal JSON
    legado (`final_text`, `sessions.json`), identificadores de modelo
    concretos (familias con guion/hífen: claude-/gpt-/gemini-/deepseek-/
    glm-/grok-/kimi-/qwen-/mistral-, variantes espaciadas sonnet|opus|
    haiku+dígito), nombres de proveedores, rutas absolutas de host
    (/home/, /root/, /Users/) y URLs de servidor no neutrales (solo se
    toleran localhost/127.0.0.1, dominios example/.invalid y enlaces de
    documentación pública declarados en NEUTRAL_DOC_HOSTS).

Cada concepto se exige CONJUNTIVAMENTE: si falta UNO, la unidad falla. En
el estado vigente (referencias sin actualizar; spec §6 ubica la tabla de
modelos obsoleta en opencode-delegation.md:18-36 y la descripción de la
señal JSON en cli-delegation.md) el RED esperado es:

  (i)   los marcadores del contrato durable no están en cli-delegation.md;
  (ii)  la señal sigue descrita como JSON ({status, session, final_text});
  (iii) los marcadores del modo de carga actualizado no están en
        opencode-delegation.md;
  (iv)  la tabla de modelos obsoleta (nombres de modelo concretos) sigue
        presente y sin puntero a la tabla única.
Cada fallo RED debe ser AssertionError sobre el CONTENIDO ausente/prohibido,
no import/sintaxis. El artefacto observado es la REFERENCIA PUBLICADA
(el producto de T3); el oráculo NO lee implementación de producto.

Mapa test → postcondición (spec 005-010):

  1  TestPd10CliDelegationDurableSignal::test_pd10_cli_reference_documents_…  PD-10 (señal durable real + servidor/permisos)
  2  TestPd10CliDelegationDurableSignal::test_pd10_cli_reference_no_legacy_…  PD-10 (ya no describe la señal como JSON legado)
  3  TestPd10OpencodeLoadMode::test_pd10_opencode_reference_documents_…       PD-10 (entry subagent válida; identidad desde la fila; sin fallback)
  4  TestPd10OpencodeLoadMode::test_pd10_opencode_reference_points_to_single_… PD-10 (puntero a la ÚNICA tabla de modelos; sin modelos concretos)
  5  TestInv7ReferencesWithoutVpsValues::test_inv7_references_free_of_…       INV-7 (sin rutas absolutas de host, proveedor, modelo concreto ni servidor)
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

# Helper único de 006-002 U3 (PD-9): la COPIA PRESERVADA —localizada por su
# declaración de preservación, no por una ruta— de la referencia por runtime
# retirada (testfix U3: `framed_evidence_documents()` es la superficie ancha de
# candidatos, no la copia).
from tests.test_006_002_u3_runtime_references import (
    preservation_copy_documents,
)

PRESERVED_REFERENCE = "opencode-delegation.md"

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_REFERENCE = (REPO_ROOT / "skills" / "cdad-cycle" / "references"
                 / "cli-delegation.md")
# Referencia por runtime RETIRADA del árbol instalable por 006-002 U3 (PD-9):
# sigue siendo el punto de referencia del modo de carga y del puntero a la tabla
# única de modelos, pero su superficie viva es la evidencia no instalable bajo
# `docs/**` (helper único del RED de U3).
OPENCODE_REFERENCE = (REPO_ROOT / "skills" / "cdad-cycle" / "references"
                      / "opencode-delegation.md")
# Destino del puntero de la tabla ÚNICA de modelos (PD-10): existe en el
# repo; la comprobación es de EXISTENCIA (consistencia estructural del
# puntero), jamás de contenido.
MODELS_TABLE_SCRIPT = REPO_ROOT / "scripts" / "cdad-models.sh"

# --- patrones prohibidos (INV-7 / señal JSON legado) ----------------------

# Artefactos de la señal JSON LEGADO ({session, status, final_text,
# diagnosis} sobre <fake>/sessions.json): la referencia ya NO debe
# describir la señal como ese JSON (PD-10).
LEGACY_SIGNAL_TOKENS = ("final_text", "sessions.json")
# Forma JSON de la señal legado: claves "status" adyacentes a las claves
# del esquema viejo (cosales de la descripción JSON de la señal).
LEGACY_SIGNAL_JSON_RE = re.compile(
    r"\"(?:status|final_text|diagnosis)\"\s*,\s*"
    r"\"(?:status|final_text|diagnosis)\"")

# Identificadores de MODELO concretos (familia + guion) y variantes
# espaciadas de líneas de modelo (INV-7: jamás un modelo concreto en la
# fuente; el puntero a la tabla única los sustituye).
CONCRETE_MODEL_ID_RE = re.compile(
    r"(?i)\b(?:claude|gpt|gemini|deepseek|glm|grok|kimi|qwen|mistral)"
    r"[-–][\w.\-]+")
SPACED_MODEL_LINE_RE = re.compile(r"(?i)\b(?:sonnet|opus|haiku)\s*\d[\w.]*")

# Nombres de PROVEEDORES concretos (INV-7; la tabla de modelos se resuelve
# por config, el proveedor no se nombra en contratos públicos).
PROVIDER_RE = re.compile(
    r"(?i)\b(?:anthropic|openai|google|deepseek|moonshot|zhipu|x\.ai|xai"
    r"|mistral|qwen)\b")

# Rutas absolutas de HOST (INV-7: rutas absolutas del VPS prohibidas; las
# rutas del repo son relativas y no empiezan con /).
HOST_ABSOLUTE_PATH_RE = re.compile(r"/(?:home|root|Users)/")

# URLs de SERVIDOR: solo hosts neutrales (ejemplo/loopback/documentación
# pública declarada); cualquier otro host es un valor de despliegue
# (INV-7: el servidor se resuelve por configuración, no por la referencia).
URL_HOST_RE = re.compile(r"(?i)\bhttps?://([^/\s)>\]\"'`,]+)")
NEUTRAL_LOCAL_HOSTS = ("localhost", "127.", "::1")
NEUTRAL_DOC_HOSTS = ("opencode.ai", "github.com",
                     "raw.githubusercontent.com")
NEUTRAL_EXAMPLE_HOSTS = (".invalid", "example.com", "example.org",
                         "example.net")


def _host_is_neutral(host: str) -> bool:
    host = host.strip().lower()
    if not host:
        return True
    if host.startswith(NEUTRAL_LOCAL_HOSTS):
        return True
    if host.endswith(NEUTRAL_EXAMPLE_HOSTS) or host.startswith("example."):
        return True
    return any(host == doc or host.endswith("." + doc)
               for doc in NEUTRAL_DOC_HOSTS)


class ReferenceCase(unittest.TestCase):
    """Base común del oráculo T3: lee la REFERENCIA PUBLICADA (artefacto
    producto de T3) con puertas AssertionError (archivo existe, no vacío);
    jamás lee implementación de producto."""

    def read_reference(self, path: Path) -> str:
        self.assertTrue(
            path.is_file(),
            msg=f"la referencia publicada no existe (T3: el artefacto "
                f"producto debe existir): {path}")
        text = path.read_text(encoding="utf-8")
        self.assertTrue(
            text.strip(),
            msg=f"la referencia publicada está vacía (artefacto sin "
                f"contrato documentado): {path.name}")
        return text

    def require_any(self, text: str, alternatives: tuple[str, ...],
                    concept: str, document: str) -> None:
        """Exige UN concepto clave (conjunción entre conceptos de una
        unidad; cualquiera de las alternativas de idioma por concepto)."""
        lowered = text.lower()
        hits = [alt for alt in alternatives if alt.lower() in lowered]
        self.assertTrue(
            hits,
            msg=f"la referencia {document} no documenta el concepto "
                f"clave '{concept}' (PD-10: el contrato debe estar "
                f"documentado; alternativas buscadas "
                f"{list(alternatives)!r})")

    def forbid(self, text: str, pattern: re.Pattern, label: str,
               document: str) -> None:
        matches = pattern.findall(text)
        self.assertEqual(
            matches, [],
            msg=f"la referencia {document} contiene {label} (prohibido; "
                f"PD-10/INV-7): {matches[:6]!r}")


# ------------------------------------------------------- PD-10 / cli-*.md


class TestPd10CliDelegationDurableSignal(ReferenceCase):
    """PD-10 (mitad 1): cli-delegation.md documenta la señal durable REAL
    (SQLite en solo lectura por `sessions_db`, correlación por `--session`,
    fallo cerrado por esquema, clasificación por `idle_outcome`) y la
    ubicación de standalone/server/auto en la configuración; y YA NO
    describe la señal como el JSON legado {status, session, final_text}."""

    DOCUMENT = "cli-delegation.md"

    def test_pd10_cli_reference_documents_real_durable_signal(self) -> None:
        """PD-10: la referencia de delegación CLI documenta cada concepto
        del contrato durable real y de servidor/permisos (conceptos clave,
        no frases literales)."""
        text = self.read_reference(CLI_REFERENCE)

        # Store durable real: SQLite, declarado por la config (ruta
        # configurable, nunca hardcodeada) y abierto en SOLO lectura.
        self.require_any(text, ("sqlite",), "store SQLite",
                         self.DOCUMENT)
        self.require_any(text, ("sessions_db",),
                         "ruta del store declarada por la config",
                         self.DOCUMENT)
        self.require_any(text, ("read-only", "read only", "solo lectura"),
                         "lectura en solo lectura", self.DOCUMENT)

        # Correlación inequívoca por el id que el adaptador pasa en
        # --session; la fila correlacionada y su texto final.
        self.require_any(text, ("--session",),
                         "correlación por --session", self.DOCUMENT)
        self.require_any(text, ("session_v2", "fila durable",
                                "durable row"),
                         "fila de sesión durable correlacionada",
                         self.DOCUMENT)
        self.require_any(text, ("assistant",),
                         "texto final del último mensaje assistant",
                         self.DOCUMENT)

        # Clasificación desde el idle material de la fila (no del rc).
        self.require_any(text, ("idle_outcome",),
                         "clasificación por idle_outcome", self.DOCUMENT)
        for outcome in ("succeeded", "failed", "interrupted"):
            self.require_any(text, (outcome,),
                             f"resultado idle '{outcome}'", self.DOCUMENT)

        # Fallo cerrado ante esquema desconocido (con diagnóstico).
        self.require_any(text, ("fail closed", "fails closed",
                                "fallo cerrado", "closed failure"),
                         "fallo cerrado", self.DOCUMENT)
        self.require_any(text, ("unknown schema", "esquema desconocido",
                                "unknown-schema", "schema"),
                         "esquema desconocido del store", self.DOCUMENT)
        self.require_any(text, ("blocked",), "clase blocked",
                         self.DOCUMENT)

        # standalone/server/auto viven en la CONFIGURACIÓN de ejecución.
        for flag in ("--standalone", "--server", "--auto"):
            self.require_any(text, (flag,), f"invocación {flag}",
                             self.DOCUMENT)
        self.require_any(text, ("configuration", "config", "configuración"),
                         "ubicación en la configuración de ejecución",
                         self.DOCUMENT)

    def test_pd10_cli_reference_no_legacy_json_signal(self) -> None:
        """PD-10: la referencia YA NO describe la señal durable como el
        JSON legado {status, session, final_text} sobre sessions.json —
        esos artefactos del contrato viejo no aparecen."""
        text = self.read_reference(CLI_REFERENCE)
        for token in LEGACY_SIGNAL_TOKENS:
            self.assertNotIn(
                token, text,
                msg=f"la referencia {self.DOCUMENT} aún describe la señal "
                    f"como el JSON legado (token prohibido {token!r}; "
                    f"PD-10: la señal durable real es el store SQLite "
                    f"correlacionado, no {token!r})")
        self.assertEqual(
            LEGACY_SIGNAL_JSON_RE.findall(text), [],
            msg=f"la referencia {self.DOCUMENT} aún muestra la forma JSON "
                f"de la señal legado (claves status/final_text/diagnosis "
                f"coadyacentes; PD-10)")


# -------------------------------------------------- PD-10 / opencode-*.md


class TestPd10OpencodeLoadMode(ReferenceCase):
    """PD-10 (mitad 2, reformulada por 006-002 U3/PD-9): el modo de carga de
    OpenCode (`mode: subagent` = entry NO interactiva válida en la versión
    instalada) y la verificación de identidad desde la FILA DURABLE sin
    fallback se conservan como evidencia NO instalable bajo `docs/**` (la
    referencia por runtime salió del árbol de la skill), junto con el puntero a
    la ÚNICA tabla de modelos (`scripts/cdad-models.sh` + perfil activo)."""

    DOCUMENT = "opencode-delegation.md (retirada: evidencia no instalable)"

    def withdrawn_reference_is_gone(self) -> None:
        self.assertFalse(
            OPENCODE_REFERENCE.is_file(),
            msg="006-002 PD-9/U3: la referencia por runtime sigue en el árbol "
                "instalable de la skill — PD-9 la retira y preserva su detalle "
                "como evidencia no instalable bajo docs/**",
        )

    def preserved_evidence_text(self) -> str:
        """Texto de la COPIA PRESERVADA (PD-9) donde se conserva el detalle
        retirado —localizada por su declaración de preservación, no por una
        ruta—; su ausencia es aserción de contrato."""
        documents = preservation_copy_documents(PRESERVED_REFERENCE)
        self.assertTrue(
            documents,
            msg="006-002 PD-9/U3: no hay copia preservada bajo docs/** de la "
                f"referencia por runtime retirada (`{PRESERVED_REFERENCE}`) — "
                "PD-9 manda preservar su detalle como evidencia no instalable, "
                "declarándose la copia",
        )
        return "\n\n".join(path.read_text(encoding="utf-8")
                           for path in documents)

    def test_pd10_opencode_load_mode_and_durable_identity_survive_withdrawal(
            self) -> None:
        """PD-10: la entry `mode: subagent` está documentada como válida
        (no interactiva en la versión instalada) y la identidad del rol se
        verifica desde la fila durable, sin fallback a un agente genérico — y
        ese detalle NO se pierde con el retiro: se conserva como evidencia no
        instalable (006-002 PD-9)."""
        self.withdrawn_reference_is_gone()
        text = self.preserved_evidence_text()

        self.require_any(text, ("subagent",),
                         "modo de carga subagent", self.DOCUMENT)
        self.require_any(text, ("non-interactive", "noninteractive",
                                "no interactiva"),
                         "entry no interactiva en la versión instalada",
                         self.DOCUMENT)

        # Identidad desde la fila durable (barrera única), sin fallback.
        self.require_any(text, ("session_v2", "durable row",
                                "fila durable"),
                         "identidad verificada desde la fila durable",
                         self.DOCUMENT)
        self.require_any(text, ("without fallback", "no fallback",
                                "sin fallback"),
                         "sin fallback a agente genérico", self.DOCUMENT)

    def test_pd10_opencode_model_pointer_survives_the_withdrawal(self) -> None:
        """PD-10: el puntero a la ÚNICA tabla de modelos
        (`scripts/cdad-models.sh` + perfil activo) se conserva con el detalle
        retirado (evidencia no instalable; 006-002 PD-9), y el destino del
        puntero existe.

        La ausencia de nombres de modelo concretos YA NO se aserta sobre la
        referencia retirada: la evidencia NO instalable queda fuera del alcance
        de INV-7 por diseño (006-002 PD-9). El texto INSTALABLE sigue cubierto
        por `TestInv7ReferencesWithoutVpsValues` (cli-delegation.md) y por el
        oráculo de modelos de 006-002 PD-1/INV-2."""
        self.withdrawn_reference_is_gone()
        text = self.preserved_evidence_text()

        # Puntero a la tabla única + el perfil activo como selector.
        self.require_any(text, ("cdad-models.sh",),
                         "puntero a la única tabla de modelos",
                         self.DOCUMENT)
        self.require_any(text, ("profile", "perfil"),
                         "perfil activo como selector de modelo",
                         self.DOCUMENT)
        # Consistencia estructural del puntero: el destino existe.
        self.assertTrue(
            MODELS_TABLE_SCRIPT.is_file(),
            msg="el puntero a la tabla única de modelos apunta a un "
                "archivo inexistente en el repo (consistencia "
                f"estructural): {MODELS_TABLE_SCRIPT}")

        # La ausencia de nombres de modelo concretos se asertaba sobre esta
        # referencia; con el retiro (006-002 PD-9) esa mitad viaja a la
        # evidencia NO instalable, fuera del alcance de INV-7 por diseño. El
        # texto INSTALABLE sigue cubierto por TestInv7ReferencesWithoutVpsValues
        # y por el oráculo de modelos de 006-002 PD-1/INV-2.


# --------------------------------------------------------------- INV-7


class TestInv7ReferencesWithoutVpsValues(ReferenceCase):
    """INV-7: la referencia INSTALABLE de la delegación no contiene valores de
    este VPS: rutas absolutas de host, proveedor concreto, modelo concreto ni
    servidor (la configuración de ejecución los resuelve, git-ignorada).

    Reformulado por 006-002 U3 (PD-9; enmienda A-1): INV-7 gobierna texto
    INSTALABLE; la referencia por runtime `opencode-delegation.md` sale del
    árbol (su detalle se preserva como evidencia no instalable bajo `docs/**`,
    que queda fuera de este alcance por diseño). La mitad que se conserva es la
    de `cli-delegation.md`, que permanece instalable (PD-10)."""

    DOCUMENTS = (("cli-delegation.md", CLI_REFERENCE),)

    def test_inv7_references_free_of_host_paths_providers_models_and_servers(
            self) -> None:
        """INV-7: cada referencia está libre de rutas absolutas de host,
        proveedores, modelos concretos y URLs de servidor no neutrales."""
        for document, path in self.DOCUMENTS:
            with self.subTest(document=document):
                text = self.read_reference(path)

                self.forbid(text, HOST_ABSOLUTE_PATH_RE,
                            "rutas absolutas de host", document)
                self.forbid(text, PROVIDER_RE,
                            "nombres de proveedores concretos", document)
                self.forbid(text, CONCRETE_MODEL_ID_RE,
                            "identificadores de modelo concretos",
                            document)
                self.forbid(text, SPACED_MODEL_LINE_RE,
                            "nombres de modelo concretos espaciados",
                            document)

                # Servidor: toda URL debe apuntar a un host neutral
                # (loopback/ejemplo/documentación pública declarada).
                offending = [
                    host for host in URL_HOST_RE.findall(text)
                    if not _host_is_neutral(host)]
                self.assertEqual(
                    offending, [],
                    msg=f"la referencia {document} contiene URLs de "
                        f"servidor con host concreto (INV-7: el servidor "
                        f"se resuelve por configuración de ejecución): "
                        f"{offending[:6]!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
