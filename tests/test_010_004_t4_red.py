#!/usr/bin/env python3
"""RED — 010-004 T4: guarda mecánica mínima del camino de despacho (ruta C).

Contrato: `docs/specs/010-004-packet-dispatch-ergonomics/spec.md`
(pin `fc6b2ccc…`), PC-03 y PC-12; decisión
`docs/specs/010-004-packet-dispatch-ergonomics/decision-t4-mechanical-guard.md`
(§5 R4 medida, §6 alcance estrecho). Caja negra sobre superficies de texto: las
rutas de las superficies son DATOS de este paquete y se leen en tiempo de
ejecución, no al escribir la prueba. Archivo NUEVO: no edita tests existentes
ni fixtures compartidas; tampoco importa `skills/` ni `scripts/` (el CLI se
ejercita por subproceso).

Trazabilidad test → postcondición numerada → consecuencia de usuario (R4):

| Test | PC | Promesa observable | R4: sin este test el usuario… |
|---|---|---|---|
| `test_pc03_pc12_dispatch_surfaces_name_the_route_c_path` | PC-03, PC-12 | las superficies de despacho documentadas (`sources/roles/orchestrator.md`, ambos adaptadores y `handoff-prompts.md`) nombran el camino de ruta C con el token estable `--route C`, tras un control positivo que prueba que el flag existe de verdad en el CLI (`render --help` nombra `--route`) | …una edición futura de esas superficies deja el despacho sin instrucción de ruta C con todos los gates actuales verdes; el orquestador vuelve al vehículo inline que en esta épica ya perdió backticks en un despacho y corrompió un snapshot base64 en otro, y el paquete ejecutado no es el publicado (INV-05/INV-12), con descubrimiento tardío (decision-t4 §5). |
| `test_pc12_declaration_and_derived_orchestrators_survive_regeneration` | PC-12 | (a) el literal de intake `Route C — explicit file backup` está hoy en su host `sources/roles/architect.md` y en cada agente de rol derivado de los cuatro árboles (control positivo, excluidos los orquestadores, que tienen intake propio); y (b) tras él, los cuatro `cdad-orchestrator.md` derivados nombran `--route C`, de modo que una regeneración que pierda el camino o un derivado parcheado a mano fallan | …una regeneración coherente que no propague el camino deja el despacho sin instrucción de ruta C y todos los gates actuales siguen verdes (determinismo, manifiesto, composición, consistencia estructural, drift entre árboles); el usuario recibe payloads corruptos y el paquete ejecutado no es el publicado (INV-05/INV-12), con coste de rehacer el encargo (decision-t4 §5). |

Redacción de estado (honesta, sin RED fabricado): hoy ambas pruebas fallan con
`AssertionError` por comportamiento AUSENTE (`--route C` no está ni en las
superficies de despacho ni en los orquestadores derivados), y el fallo ocurre
DESPUÉS de que sus controles positivos hayan pasado: `render --help` nombra
`--route` (interfaz real del CLI) y la declaración de intake ya está presente en
su host y en los derivados de rol. La declaración NO se fabrica como RED: hoy
está verde y es control positivo declarado. Ningún fallo es por importación,
sintaxis ni archivo ausente.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
import unittest


# Raíz del repo resuelta desde este archivo (tests/ está un nivel debajo).
REPO_ROOT = Path(__file__).resolve().parents[1]

# CLI del repo, invocado por subproceso (nunca importado).
CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"

# §6.1: token estable del contrato, tolerante a espacios y saltos de línea.
ROUTE_C_TOKEN = re.compile(r"--route\s+C")

# §4.2 / §6.2: literal de intake (constante `ROUTE_C_DECLARATION` del CLI).
ROUTE_C_DECLARATION = "Route C — explicit file backup"

# §6.1: superficies de despacho que deben nombrar el camino.
DISPATCH_SURFACES = (
    "sources/roles/orchestrator.md",
    "sources/agents/adapters/opencode.md",
    "sources/agents/adapters/claude-code.md",
    "skills/cdad-cycle/references/handoff-prompts.md",
)

# §6.2: host de la declaración de intake.
DECLARATION_HOST = "sources/roles/architect.md"

# §6.2: árboles de agentes derivados de rol (globs `cdad-*.md`, sin orquestadores).
DERIVED_ROLE_TREES = (
    "agents",
    "agents/claude-code",
    "build/staging/agents/opencode",
    "build/staging/agents/claude-code",
)

# §6.3: derivados que despachan; el token debe sobrevivir a la regeneración.
DERIVED_ORCHESTRATORS = (
    "agents/cdad-orchestrator.md",
    "agents/claude-code/cdad-orchestrator.md",
    "build/staging/agents/opencode/cdad-orchestrator.md",
    "build/staging/agents/claude-code/cdad-orchestrator.md",
)


def _text(relpath: str) -> str | None:
    """Texto de una superficie, o None si no existe (fallo de aserción, no excepción)."""
    path = REPO_ROOT / relpath
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _missing_regex(relpaths: tuple[str, ...], pattern: re.Pattern[str]) -> list[str]:
    """Rutas que no contienen el token; cada entrada nombra archivo y token."""
    missing: list[str] = []
    for relpath in relpaths:
        text = _text(relpath)
        if text is None:
            missing.append(f"{relpath}: file not found")
        elif pattern.search(text) is None:
            missing.append(
                f"{relpath}: missing token `--route C` (regex {pattern.pattern!r})"
            )
    return missing


def _missing_literal(
    relpaths: tuple[str, ...], literal: str, label: str
) -> list[str]:
    """Rutas que no contienen el literal; cada entrada nombra archivo y literal."""
    missing: list[str] = []
    for relpath in relpaths:
        text = _text(relpath)
        if text is None:
            missing.append(f"{relpath}: file not found")
        elif literal not in text:
            missing.append(f"{relpath}: missing literal {label}")
    return missing


class TestDispatchSurfacesNameRouteC(unittest.TestCase):
    """PC-03 / PC-12 — el despacho documentado nombra el camino de ruta C."""

    def test_pc03_pc12_dispatch_surfaces_name_the_route_c_path(self) -> None:
        """PC-03, PC-12.

        Las cuatro superficies de despacho declaradas nombran el camino de
        ruta C con el token estable `--route C`. Control positivo previo: el
        flag es una interfaz real del CLI — `render --help` (subproceso, sin
        importar el módulo) sale rc=0 y nombra `--route`.

        R4 (decision-t4-mechanical-guard.md §5): sin este test, una edición de
        `sources/roles/orchestrator.md`, de los adaptadores o de
        `handoff-prompts.md` deja el despacho sin instrucción de ruta C y
        todos los gates actuales siguen verdes; el orquestador vuelve al
        vehículo inline que ya corrompió payloads en esta épica y el paquete
        ejecutado no es el publicado (INV-05/INV-12), con descubrimiento
        tardío.
        """
        # Control positivo (obligatorio, PRIMERO): el flag existe de verdad.
        help_run = subprocess.run(
            [sys.executable, str(CLI), "render", "--help"],
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            0,
            help_run.returncode,
            msg=(
                "positive control: `render --help` must exit 0 (the --route "
                f"flag is a real CLI interface); stderr={help_run.stderr!r}"
            ),
        )
        self.assertIn(
            "--route",
            help_run.stdout,
            msg=(
                "positive control: `render --help` must name the --route flag; "
                f"stdout={help_run.stdout!r}"
            ),
        )

        # RED: cada superficie nombra el camino con el token estable.
        missing = _missing_regex(DISPATCH_SURFACES, ROUTE_C_TOKEN)
        self.assertEqual(
            [],
            missing,
            msg=(
                "PC-03/PC-12: the documented dispatch surfaces must name the "
                "Route C path with the stable token `--route C` "
                f"(regex {ROUTE_C_TOKEN.pattern!r}); missing: {missing}"
            ),
        )


class TestRegeneratedAgentsKeepRouteC(unittest.TestCase):
    """PC-12 — la declaración y los derivados sobreviven a la regeneración."""

    def test_pc12_declaration_and_derived_orchestrators_survive_regeneration(
        self,
    ) -> None:
        """PC-12.

        (a) Control positivo PRIMERO: el literal de intake
        `Route C — explicit file backup` está en su host
        `sources/roles/architect.md` y en cada agente de rol derivado de los
        cuatro árboles (glob `cdad-*.md`, excluidos los orquestadores, que
        tienen intake propio). (b) DESPUÉS, RED: los cuatro
        `cdad-orchestrator.md` derivados nombran `--route C`, de modo que una
        regeneración que pierda el camino —o un derivado parcheado a
        mano— falla.

        R4 (decision-t4-mechanical-guard.md §5): sin este test, una
        regeneración coherente que no propague el camino deja el despacho sin
        instrucción de ruta C y todos los gates actuales siguen verdes
        (determinismo, manifiesto, composición, consistencia estructural,
        drift entre árboles); el usuario recibe payloads corruptos y el
        paquete ejecutado no es el publicado (INV-05/INV-12), con coste de
        rehacer el encargo.
        """
        # (a) CONTROL POSITIVO (primero): la declaración ya existe hoy.
        host_text = _text(DECLARATION_HOST)
        self.assertIsNotNone(
            host_text,
            msg=f"fixture: declaration host {DECLARATION_HOST} must exist",
        )
        self.assertIn(
            ROUTE_C_DECLARATION,
            host_text,
            msg=(
                f"fixture: {DECLARATION_HOST} must carry the intake declaration "
                f"{ROUTE_C_DECLARATION!r} today"
            ),
        )

        declaration_counts: dict[str, int] = {}
        missing_declaration: list[str] = []
        for tree in DERIVED_ROLE_TREES:
            derived = sorted(
                path
                for path in (REPO_ROOT / tree).glob("cdad-*.md")
                if not path.name.startswith("cdad-orchestrator")
            )
            relpaths = tuple(str(path.relative_to(REPO_ROOT)) for path in derived)
            declaration_counts[tree] = len(relpaths)
            self.assertTrue(
                relpaths,
                msg=(
                    f"fixture: tree {tree} must expose derived role agents "
                    "(cdad-*.md, excluding cdad-orchestrator*)"
                ),
            )
            missing_declaration.extend(
                _missing_literal(
                    relpaths,
                    ROUTE_C_DECLARATION,
                    repr(ROUTE_C_DECLARATION),
                )
            )
        self.assertEqual(
            [],
            missing_declaration,
            msg=(
                "fixture: the intake declaration must be present in every "
                "derived role agent today (20/20 per tree measured); missing: "
                f"{missing_declaration}"
            ),
        )

        # (b) RED: los orquestadores derivados nombran el camino.
        missing_token = _missing_regex(DERIVED_ORCHESTRATORS, ROUTE_C_TOKEN)
        self.assertEqual(
            [],
            missing_token,
            msg=(
                "PC-12: derived orchestrators must name the Route C path with "
                "the stable token `--route C` "
                f"(regex {ROUTE_C_TOKEN.pattern!r}) so a regeneration that loses "
                "it fails; declaration control passed for "
                f"{declaration_counts}; missing: {missing_token}"
            ),
        )


if __name__ == "__main__":
    unittest.main()
