#!/usr/bin/env python3
"""Guarda mecánica B1 — 010-004 T6 (archivo NUEVO; nace VERDE).

Contrato: `docs/specs/010-004-packet-dispatch-ergonomics/spec.md`
(pin `fc6b2ccc…5d64`), §4.3 (`:296`, `:309-311`) y PC-03; hallazgo
bloqueante B1 de `review.md`.

La guarda es de REGRESIÓN (A1-style), no un RED fabricado: el dueño único
del texto de intake es `sources/roles/architect.md`, bloque delimitado por
`<!-- cdad-shared:intake-core -->` y `<!-- /cdad-shared -->`, y sus 20
derivados de rol (2 runtimes × 5 roles × {genérico, odoo}) ya contienen los
enunciados. La prueba impide que una edición futura del bloque, o una
regeneración descuidada, borre (a) que la ruta C exige contexto v2, y
(b) que la mezcla A+C se rechaza aunque el inline coincida.

Solo se afirman tokens estables de palabra (`assertIn`/`assertNotIn` sobre
el texto con espacios normalizados): no se congela prosa ni se cuentan
ocurrencias. El control negativo (los dos orquestadores) prueba que la
ausencia no es vacua: el orquestador enuncia su propia regla de mezcla
(`A+C is rejected`, `even when the inline coincides`) en lugar de heredar
el texto del dueño de rol.

Trazabilidad PC-03 → R4: sin esta guarda, si el bloque intake-core o sus
derivados pierden el enunciado C/v2 o el rechazo A+C, la suite quedaría
verde y el usuario volvería a recibir un intake ambiguo (identificación C
junto con un paquete A de inline coincidente) o una ruta C sobre contexto
v1 sin el diagnóstico prescrito.
"""

from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]

INTAKE_SOURCE = Path("sources") / "roles" / "architect.md"
INTAKE_BLOCK_OPEN = "<!-- cdad-shared:intake-core -->"
INTAKE_BLOCK_CLOSE = "<!-- /cdad-shared -->"

# Tokens estables que el dueño del intake y TODOS sus derivados de rol deben
# conservar. Los cuatro primeros son los exigidos por el encargo; el último
# es el refuerzo admitido del rechazo como paquete inválido.
REQUIRED_TOKENS = (
    "v2 execution context",
    "v1 context",
    "Route A and route C are exclusive",
    "even when the inline matches",
    "rejected as an invalid packet",
)

# 5 roles × 2 variantes × 2 runtimes = 20 derivados de rol.
ROLES = ("architect", "test-writer", "implementer", "reviewer", "scribe")
VARIANTS = ("", "-odoo")
RUNTIMES = ("", "claude-code")

# El orquestador NO hereda el texto del dueño de rol; enuncia su propia regla.
ORCHESTRATORS = (
    Path("agents") / "cdad-orchestrator.md",
    Path("agents") / "claude-code" / "cdad-orchestrator.md",
)
ROLE_OWNER_TOKENS = (
    "v2 execution context",
    "Route A and route C are exclusive",
)
ORCHESTRATOR_OWN_TOKENS = (
    "A+C is rejected",
    "even when the inline coincides",
)


def _read(relative_path: Path) -> str:
    """Texto UTF-8 de un archivo declarado; inexistente ⇒ fallo explícito."""
    path = REPO_ROOT / relative_path
    if not path.is_file():
        raise AssertionError(
            f"archivo declarado por la guarda B1 inexistente: {relative_path.as_posix()}"
        )
    return path.read_text(encoding="utf-8")


def _words(text: str) -> str:
    """Texto con espacios normalizados: un token de palabra no depende del
    corte de línea del markdown. No altera palabras ni su orden."""
    return " ".join(text.split())


def _derived_role_agents() -> list[Path]:
    """Las 20 rutas derivadas, construidas por roles × variantes × runtimes."""
    return [
        Path("agents", runtime, f"cdad-{role}{variant}.md")
        for runtime in RUNTIMES
        for role in ROLES
        for variant in VARIANTS
    ]


class TestB1IntakeCoreGuard(unittest.TestCase):
    """PC-03 (spec §4.3 `:296`,`:309-311`): la ruta C exige contexto v2 y la
    mezcla A+C se rechaza incluso con inline coincidente."""

    def test_b1_intake_core_and_derived_role_agents_keep_c_v2_and_a_plus_c_rejection(
        self,
    ) -> None:
        """El dueño único del texto de intake y sus 20 derivados conservan los
        enunciados C/v2 y rechazo A+C; los orquestadores conservan su regla
        propia y no el texto del dueño de rol.

        R4: sin esta prueba, una edición futura del bloque intake-core o una
        regeneración descuidada puede borrar el enunciado C/v2 o el rechazo
        A+C, la suite seguiría verde y el usuario volvería a recibir un
        intake ambiguo.
        """
        # 1. Dueño único: el bloque se localiza por sus marcadores, nunca por
        # número de línea.
        source_text = _read(INTAKE_SOURCE)
        self.assertIn(
            INTAKE_BLOCK_OPEN,
            source_text,
            msg=f"{INTAKE_SOURCE.as_posix()} perdió el marcador de apertura "
            f"{INTAKE_BLOCK_OPEN!r} del bloque del dueño de intake (B1/PC-03)",
        )
        block_start = source_text.find(INTAKE_BLOCK_OPEN) + len(INTAKE_BLOCK_OPEN)
        self.assertIn(
            INTAKE_BLOCK_CLOSE,
            source_text[block_start:],
            msg=f"{INTAKE_SOURCE.as_posix()} abrió el bloque del dueño de intake "
            f"sin su marcador de cierre {INTAKE_BLOCK_CLOSE!r} (B1/PC-03)",
        )
        block_end = source_text.find(INTAKE_BLOCK_CLOSE, block_start)
        owner_block = _words(source_text[block_start:block_end])

        for token in REQUIRED_TOKENS:
            self.assertIn(
                token,
                owner_block,
                msg=f"el bloque intake-core de {INTAKE_SOURCE.as_posix()} perdió "
                f"el token estable {token!r}: el usuario volvería a recibir un "
                "intake ambiguo (B1/PC-03)",
            )

        # 2. Derivados: los 20 agentes de rol de ambos runtimes incorporan los
        # mismos enunciados (la lista se deriva, no se escribe a mano).
        derived = _derived_role_agents()
        self.assertEqual(
            len(derived),
            20,
            msg="la derivación de roles × variantes × runtimes debe dar 20 "
            f"agentes de rol, dio {len(derived)}",
        )
        self.assertEqual(
            len(set(derived)),
            20,
            msg=f"la derivación contiene rutas duplicadas: {derived!r}",
        )
        missing = [path.as_posix() for path in derived if not (REPO_ROOT / path).is_file()]
        self.assertEqual(
            missing,
            [],
            msg=f"faltan derivados de rol declarados por la guarda B1: {missing}",
        )
        for relative_path in derived:
            agent_text = _words(_read(relative_path))
            for token in REQUIRED_TOKENS:
                self.assertIn(
                    token,
                    agent_text,
                    msg=f"{relative_path.as_posix()} no contiene el token estable "
                    f"{token!r}: la regeneración derivada perdió el enunciado "
                    "del dueño de intake (B1/PC-03)",
                )

        # 3. Control negativo no vacuo: los dos orquestadores no contienen los
        # tokens del dueño de rol y sí contienen su regla propia.
        for relative_path in ORCHESTRATORS:
            orchestrator_text = _words(_read(relative_path))
            for token in ROLE_OWNER_TOKENS:
                self.assertNotIn(
                    token,
                    orchestrator_text,
                    msg=f"{relative_path.as_posix()} contiene el token del dueño "
                    f"de rol {token!r}: el control negativo de la guarda B1 "
                    "dejaría de discriminar",
                )
            for token in ORCHESTRATOR_OWN_TOKENS:
                self.assertIn(
                    token,
                    orchestrator_text,
                    msg=f"{relative_path.as_posix()} no contiene su regla propia "
                    f"{token!r}: el orquestador debe enunciar el rechazo A+C con "
                    "su propio texto (B1), no heredar el del dueño de rol",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
