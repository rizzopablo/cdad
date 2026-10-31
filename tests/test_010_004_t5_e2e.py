#!/usr/bin/env python3
"""INTEGRATION/E2E — 010-004 T5 (PC-12): consumidor INSTALADO aislado.

Contrato: `docs/specs/010-004-packet-dispatch-ergonomics/spec.md`
(pin `fc6b2ccc…`), §4.2 («Emisión de ruta C») y §5 PC-12: «Un consumidor
instalado aislado puede preparar un paquete nuevo v2, emitir C y
resolver/validar su contexto, sin modificar la instalación global».

Superficie propia de esta unidad (no la del checkout): el entrypoint es el que
`install.sh` DEPOSITA en una raíz de instalación aislada,

    <raiz aislada>/install-root/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py

invocado por subproceso (caja negra) con `HOME`, `XDG_CONFIG_HOME`,
`XDG_DATA_HOME`, `XDG_CACHE_HOME`, `CDAD_INSTALL_ROOT` y
`CDAD_SKILL_EXTRA_DIRS` redirigidos bajo la raíz declarada. El wrapper
`scripts/cdad_packet.py` del checkout NUNCA se usa como sustituto: se afirma
que el entrypoint resuelve bajo la raíz aislada, no en el checkout.

Raíz temporal declarada: `.cdad/tmp/t5-isolated-consumer/` (subdirectorio
único por corrida, retirado al final por limpieza de clase; `.cdad/` está
ignorado por git). `.cdad/tmp` es raíz temporal declarada por la política del
proyecto.

Nota de fixture declarada: el instalador rechaza un destino gestionado dentro
del repositorio fuente («Managed install destination overlaps the source
repository»), así que el producto se COPIA dentro de la raíz aislada
(`<raíz>/product`, staging incluido) y se instala desde esa copia hacia
`<raíz>/install-root`. La instalación no ejecuta el checkout y el consumidor
sigue siendo el entrypoint depositado bajo la raíz aislada.

Reutilización (sin duplicar andamiaje ni oráculos ya cubiertos):
- `tests.test_packet_prepare.PrepareProject` / `run_prepare`: project fixture
  y preparación v2 (T2).
- `tests.test_010_004_t3_red`: `Published`, `PublishedPacketCase` (oráculos de
  §4.2: `route_c_identification`, `assert_rejection`, `tracked_bytes`,
  `packet_dirs`, `expected_identification`) y la constante
  `ROUTE_C_CONTRACT_KEYS`.
- `tests.test_install_ownership.load_install_manifest` /
  `load_staging_manifest` y `tests.product_staging.product_root`: instalación
  aislada (004-001 T5, portabilidad de staging).

Casos YA cubiertos por T2/T3 que aquí NO se repiten como casos propios (solo
se re-ejercitan a través del consumidor instalado, que es la superficie de este
E2E): `tests/test_010_004_t3_red.py::TestRouteCPositiveIdentification`
(identificación exacta y determinismo) y
`::TestRouteCRejections` (v1, request no publicado, contexto no canónico,
paquete divergente con el CLI del repo). T2 cubre la matriz de contexto y la
preparación v2 con el CLI del repo.

Mapa test → postcondición → consecuencia de usuario (R4):

| Test | PC | Promesa observable | R4: sin este test el usuario… |
|---|---|---|---|
| `test_pc12_isolated_consumer_prepares_validates_and_emits_canonical_route_c` | PC-12 (protege PC-01/PC-05 en la superficie instalada) | El consumidor instalado prepara un paquete nuevo v2, resuelve su contexto sin argumento explícito, valida request y paquete (rc=0), re-renderiza el paquete byte-idéntico y emite la identificación C canónica de siete campos, determinista, sin modificar archivos ni la instalación global | …la mejora solo estaría demostrada sobre el CLI del checkout: un defecto de empaquetado o instalación (script, instrucciones o assets ausentes, instalación que escribe fuera de su raíz) llegaría a la máquina del usuario con toda la suite del repo en verde, y su despacho fallaría o emitiría una identificación no canónica |
| `test_pc12_isolated_consumer_rejects_divergent_packet_and_non_canonical_copies_fail_closed` | PC-12 (protege PC-02) | En el consumidor instalado, C rechaza fail-closed un `PACKET.md` publicado divergente y sendas copias no canónicas (request fuera de `.cdad/packets/<id>/REQUEST.json`; contexto fuera de `.cdad/executions/<id>/execution.json`): sin identificación, sin efectos persistentes, sin normalizar ni reescribir archivos, con control positivo antes y después de cada tanda | …las restricciones de C estarían acreditadas solo en el checkout: un consumidor instalado podría aceptar un paquete divergente o una copia fuera de su ubicación canónica y despachar un encargo nunca validado, sin que ninguna prueba lo notara |

Límite declarado: la corrida acredita conducta del CLI instalado sobre archivos
publicados; no acredita recepción nativa del mensaje por un runtime ni
obediencia de un modelo (spec §4.7). La instantánea de la instalación global
del proceso es de solo lectura y compara inventario y bytes: no observa
escrituras transitorias revertidas entre instantáneas.

Nota observada (no una falla de la promesa): con el HOME aislado sin agentes
globales, `prepare` responde rc=0 y avisa por stderr que no publica agentes
derivados (`OpenCode agents source directory not found`). La promesa
ejercitada —preparar, emitir C y resolver/validar el contexto— no depende de
esa publicación, así que la prueba no exige stderr vacío.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.product_staging import product_root
from tests.test_010_004_t3_red import (
    ROUTE_C_CONTRACT_KEYS,
    Published,
    PublishedPacketCase,
)
from tests.test_install_ownership import (
    load_install_manifest,
    load_staging_manifest,
)
from tests.test_packet_prepare import PrepareProject, run_prepare
from tests.test_role_packets import REPO_ROOT


# Raíz temporal declarada por el paquete (subdirectorio único por corrida).
ISOLATED_ROOT_PARENT = REPO_ROOT / ".cdad" / "tmp" / "t5-isolated-consumer"

# Destino que `install.sh` publica para el runtime opencode (mismo layout que
# citan `tests/test_003_002_t4_integration.py` y `tests/test_004_001_t6.py`).
INSTALLED_CLI_REL = (
    Path(".config") / "opencode" / "skills" / "cdad-cycle" / "scripts"
    / "cdad_packet.py"
)

# Wrapper del checkout: PROHIBIDO usarlo como sustituto del instalado.
CHECKOUT_WRAPPER = REPO_ROOT / "scripts" / "cdad_packet.py"

# Entradas del producto que alimentan al instalador (mismo conjunto que
# `tests/test_003_002_t4_integration.py::PRODUCT_ENTRIES`, más el staging ya
# generado por `tests.product_staging.product_root`).
PRODUCT_ENTRIES = (
    "install.sh",
    "scripts",
    "skills",
    "sources",
    "agents",
    "build",
    "Makefile",
)

# Las seis variables que el paquete exige redirigir bajo la raíz aislada.
ISOLATED_ENV_KEYS = (
    "HOME",
    "XDG_CONFIG_HOME",
    "XDG_DATA_HOME",
    "XDG_CACHE_HOME",
    "CDAD_INSTALL_ROOT",
    "CDAD_SKILL_EXTRA_DIRS",
)

# Instalación global visible por el proceso (el HOME de la corrida): la
# instantánea se toma solo lectura, antes y después del recorrido.
GLOBAL_INSTALL_RELATIVE_ROOTS = (".config/opencode", ".agents", ".claude")

_MISSING_BODY_FRAGMENTS = (
    "cdad-instructions",
    "cdad-packet-json",
    "Prepare objective",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_installed_cli(
    cli: Path, env: dict[str, str], *args: str, cwd: Path
) -> subprocess.CompletedProcess[str]:
    """Ejercita el CLI INSTALADO por subproceso (caja negra, sin importarlo)."""
    return subprocess.run(
        [sys.executable, str(cli), *args],
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def isolated_env(base: Path) -> dict[str, str]:
    """Entorno del consumidor: las seis raíces declaradas bajo `base`."""
    env = os.environ.copy()
    env.update(
        {
            "HOME": str(base / "home"),
            "XDG_CONFIG_HOME": str(base / "xdg-config"),
            "XDG_DATA_HOME": str(base / "xdg-data"),
            "XDG_CACHE_HOME": str(base / "xdg-cache"),
            "CDAD_INSTALL_ROOT": str(base / "install-root"),
            "CDAD_SKILL_EXTRA_DIRS": str(base / "extra-skills"),
        }
    )
    return env


def staged_product_copy(product: Path, destination: Path) -> Path:
    """Copia del producto (staging incluido) dentro de la raíz aislada.

    El instalador rechaza un destino gestionado dentro del repositorio fuente
    («Managed install destination overlaps the source repository»), así que el
    producto se copia fuera del árbol fuente —bajo la raíz aislada— y se
    instala desde ahí. Es además la forma más fuerte de «consumidor
    instalado»: la instalación no ejecuta el checkout.
    """
    destination.mkdir(parents=True)
    for entry in PRODUCT_ENTRIES:
        source = product / entry
        target = destination / entry
        if source.is_dir():
            shutil.copytree(
                source,
                target,
                symlinks=True,
                ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"),
            )
        else:
            shutil.copy2(source, target)
    return destination


def install_isolated(
    product: Path, install_root: Path, env: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    """`install.sh --basic` desde la copia del producto hacia la raíz aislada.

    NOTA DE REUTILIZACIÓN: se reutilizan `tests.product_staging.product_root`
    (staging garantizado, nunca escribe en el checkout) y
    `tests.test_install_ownership.load_staging_manifest` /
    `load_install_manifest` (oráculos del contrato de instalación), pero NO se
    usa `run_installer`, porque ese helper fija `CDAD_SKILL_EXTRA_DIRS=""` y
    el paquete exige esa variable redirigida bajo la raíz aislada: usarlo
    rompería la aislación declarada.
    """
    return subprocess.run(
        ["bash", str(product / "install.sh"), "--basic"],
        cwd=str(product),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def global_installation_snapshot() -> dict[str, str]:
    """Inventario de solo lectura (ruta relativa al HOME → sha256)."""
    home = Path(os.environ["HOME"])
    snapshot: dict[str, str] = {}
    for rel_root in GLOBAL_INSTALL_RELATIVE_ROOTS:
        root = home / rel_root
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file():
                snapshot[str(path.relative_to(home))] = sha256_bytes(
                    path.read_bytes()
                )
    return snapshot


class IsolatedInstalledConsumerCase(PublishedPacketCase):
    """Instalación aislada del producto (una vez por clase) y proyecto
    consumidor por prueba.

    Nada escribe fuera de `.cdad/tmp/t5-isolated-consumer/<corrida>/`: la
    copia del producto, el instalador, el HOME, los XDG, la raíz de
    instalación, los destinos extra y el proyecto consumidor viven bajo esa
    raíz, que se retira al terminar.
    """

    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        ISOLATED_ROOT_PARENT.mkdir(parents=True, exist_ok=True)
        cls.iso_root = Path(
            tempfile.mkdtemp(
                prefix=f"run-{os.getpid()}-", dir=ISOLATED_ROOT_PARENT
            )
        ).resolve()
        cls.addClassCleanup(cls._remove_isolated_root)

        cls.env = isolated_env(cls.iso_root)
        for rel in (
            "home",
            "xdg-config",
            "xdg-data",
            "xdg-cache",
            "extra-skills",
            "install-root",
        ):
            (cls.iso_root / rel).mkdir(parents=True, exist_ok=True)

        # Producto instalable: copia con staging dentro de la raíz aislada.
        cls.product = staged_product_copy(
            product_root(), cls.iso_root / "product"
        )
        # Precondición declarada (004-001 T5): el instalador consume un
        # staging no vacío.
        load_staging_manifest(cls.product)

        cls.install_root = Path(cls.env["CDAD_INSTALL_ROOT"])
        cls.install_result = install_isolated(
            cls.product, cls.install_root, cls.env
        )
        if cls.install_result.returncode != 0:
            raise AssertionError(
                "precondición del E2E: `install.sh --basic` debe instalar en "
                "la raíz aislada; rc="
                f"{cls.install_result.returncode}; "
                f"stderr={cls.install_result.stderr[-2000:]!r}"
            )

        cls.installed_cli = cls.install_root / INSTALLED_CLI_REL
        if not cls.installed_cli.is_file():
            raise AssertionError(
                "precondición del E2E: el instalador debe depositar el CLI del "
                f"consumidor en {cls.installed_cli}"
            )
        cls.installed_cli_sha256 = sha256_bytes(cls.installed_cli.read_bytes())

    @classmethod
    def _remove_isolated_root(cls) -> None:
        shutil.rmtree(cls.iso_root)
        if cls.iso_root.exists():
            raise AssertionError(
                "el recorrido debe limpiar su raíz temporal "
                f"{cls.iso_root} (sigue existiendo al terminar)"
            )

    # -- fixture: paquete publicado por el CLI INSTALADO --------------------

    def publish(self, prefix: str) -> Published:
        root = Path(
            tempfile.mkdtemp(prefix=prefix, dir=self.iso_root)
        ).resolve()
        self.addCleanup(shutil.rmtree, root, True)
        project = PrepareProject(root, "test-writer", "e2e")
        packets_dir = root / ".cdad" / "packets"
        result = run_prepare(
            self.installed_cli,
            *project.args(out_dir=packets_dir),
            cwd=root,
            env=self.env,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg="fixture: el CLI INSTALADO debe publicar el paquete v2 del "
                "fixture (preparación nueva v2, PC-12): "
                + result.stderr.decode(errors="replace"),
        )
        state = json.loads(project.state_path.read_text(encoding="utf-8"))
        packet_id = state["active_packet"]["id"]
        packet_dir = packets_dir / packet_id
        request_path = packet_dir / "REQUEST.json"
        packet_path = packet_dir / "PACKET.md"
        self.assertTrue(
            request_path.is_file(),
            msg=f"fixture: falta el request publicado {request_path}",
        )
        self.assertTrue(
            packet_path.is_file(),
            msg=f"fixture: falta el paquete publicado {packet_path}",
        )
        request = json.loads(request_path.read_text(encoding="utf-8"))
        self.assertEqual(
            request["packet_id"],
            packet_id,
            msg="fixture: el request publicado no declara el paquete activo",
        )
        self.assertEqual(
            state["execution"]["id"],
            request["execution_id"],
            msg="fixture: state.execution no concuerda con el request",
        )
        return Published(
            root=root,
            state_path=project.state_path,
            packet_id=packet_id,
            request=request,
            request_path=request_path,
            packet_path=packet_path,
        )

    # -- oráculos de ruta C sobre el CLI INSTALADO -------------------------

    def route_c(
        self, case: Published, *extra: str
    ) -> subprocess.CompletedProcess[str]:
        return run_installed_cli(
            self.installed_cli,
            self.env,
            "render",
            "--project-root",
            str(case.root),
            "--request",
            str(case.request_path),
            "--route",
            "C",
            *extra,
            cwd=case.root,
        )

    def cli(self, case: Published, *args: str) -> subprocess.CompletedProcess[str]:
        """Corrida del CLI instalado desde el proyecto consumidor."""
        return run_installed_cli(
            self.installed_cli, self.env, *args, cwd=case.root
        )


class TestIsolatedConsumerE2E(IsolatedInstalledConsumerCase):
    def test_pc12_isolated_consumer_prepares_validates_and_emits_canonical_route_c(
        self,
    ) -> None:
        """PC-12 (spec §5: «un consumidor instalado aislado puede preparar un
        paquete nuevo v2, emitir C y resolver/validar su contexto, sin
        modificar la instalación global»; protege PC-01/PC-05 en la superficie
        instalada; §4.1 matriz fila 1 y §4.2 «Representación»).

        Promesa observable: el CLI que `install.sh` depositó en la raíz
        aislada —no el wrapper del checkout— prepara un paquete nuevo v2,
        resuelve el localizador del request SIN `--execution-context`,
        valida request y paquete (rc=0), re-renderiza el paquete byte-idéntico
        a `PACKET.md` y emite la identificación C canónica de siete campos,
        concordante con los archivos, determinista, sin modificar request,
        paquete, contexto ni estado, y sin tocar la instalación global.

        R4: sin esta prueba, la mejora solo estaría demostrada sobre el CLI
        del checkout: un defecto de empaquetado o instalación (script,
        instrucciones o assets ausentes; instalación que escribe fuera de su
        raíz) llegaría a la máquina del usuario con toda la suite del repo en
        verde, y su despacho fallaría o emitiría una identificación no
        canónica.
        """
        # -- consumidor instalado, no el wrapper del checkout ---------------
        self.assertTrue(
            self.installed_cli.resolve().is_relative_to(self.iso_root),
            msg="PC-12: el entrypoint debe resolver bajo la raíz aislada; "
                f"resuelve a {self.installed_cli.resolve()} (un enlace al "
                "checkout no es un consumidor instalado)",
        )
        self.assertNotEqual(
            self.installed_cli.resolve(),
            CHECKOUT_WRAPPER.resolve(),
            msg="PC-12: el CLI ejercitado no puede ser el wrapper del checkout",
        )
        self.assertEqual(
            self.installed_cli.resolve(),
            self.installed_cli,
            msg="PC-12: el CLI instalado debe ser un archivo real de la raíz "
                "aislada, no un enlace",
        )

        # -- las seis raíces declaradas viven bajo la raíz aislada ----------
        for key in ISOLATED_ENV_KEYS:
            self.assertTrue(
                Path(self.env[key]).is_relative_to(self.iso_root),
                msg=f"PC-12: {key} debe quedar redirigida bajo la raíz "
                    f"aislada; obtuvo {self.env[key]!r}",
            )
        self.assertNotEqual(
            self.env["HOME"],
            os.environ["HOME"],
            msg="PC-12: el consumidor no debe heredar el HOME del proceso",
        )

        # -- la instalación confina sus artefactos --------------------------
        manifest = load_install_manifest(self.install_root)
        artifacts = manifest["artifacts"]
        self.assertTrue(
            artifacts,
            msg="PC-12: el manifiesto de instalación no debe estar vacío",
        )
        owned: dict[Path, dict] = {}
        for rel, record in artifacts.items():
            destination = Path(rel)
            installed = (
                destination if destination.is_absolute()
                else self.install_root / destination
            ).resolve()
            self.assertTrue(
                installed.is_relative_to(self.iso_root),
                msg="PC-12: todo artefacto instalado debe quedar bajo la raíz "
                    f"aislada; {rel!r} resuelve a {installed}",
            )
            self.assertTrue(
                installed.is_file(),
                msg=f"PC-12: el manifiesto declara {rel!r} pero no está "
                    "instalado",
            )
            self.assertEqual(
                record["sha256"],
                sha256_bytes(installed.read_bytes()),
                msg=f"PC-12: sha256 del manifiesto no corresponde a {rel!r}",
            )
            owned[installed] = record
        self.assertEqual(
            len(owned),
            len(artifacts),
            msg="PC-12: el manifiesto declara artefactos con destinos "
                "repetidos o no verificables",
        )
        self.assertIn(
            self.installed_cli.resolve(),
            owned,
            msg="PC-12: el manifiesto de instalación debe registrar la "
                "propiedad del CLI ejercitado "
                f"({self.installed_cli}); registrados="
                f"{sorted(str(p) for p in owned)[:5]}",
        )
        self.assertEqual(
            owned[self.installed_cli.resolve()]["sha256"],
            self.installed_cli_sha256,
            msg="PC-12: el sha256 registrado del CLI instalado debe "
                "corresponder a sus bytes",
        )
        # El destino extra declarado por `CDAD_SKILL_EXTRA_DIRS` se honró
        # BAJO la raíz aislada (no en una ubicación global).
        extra_root = Path(self.env["CDAD_SKILL_EXTRA_DIRS"]).resolve()
        self.assertTrue(
            any(path.is_relative_to(extra_root) for path in owned),
            msg="PC-12/§4.6: el destino extra de skills debe quedar bajo la "
                f"raíz aislada ({extra_root}); destinos="
                f"{sorted(str(p) for p in owned)[:5]}",
        )

        global_before = global_installation_snapshot()

        # -- preparación nueva v2 con el CLI INSTALADO ----------------------
        case = self.publish("cdad-t5e2e-journey-")
        request = case.request
        expected_context = (
            f".cdad/executions/{request['execution_id']}/execution.json"
        )
        self.assertEqual(
            request["execution_context"],
            expected_context,
            msg="PC-12/§4.1: la preparación nueva debe declarar el "
                "localizador canónico de su contexto v2 (concordante con el "
                f"execution_id); obtuvo {request.get('execution_context')!r}",
        )
        self.assertTrue(
            (case.root / expected_context).is_file(),
            msg="PC-12/§4.1: el contexto canónico declarado debe existir en "
                f"{expected_context}",
        )
        before = self.tracked_bytes(case)

        # -- resolución del localizador SIN argumento explícito -------------
        validated_request = self.cli(
            case,
            "validate-request",
            "--project-root",
            str(case.root),
            "--request",
            str(case.request_path),
        )
        self.assertEqual(
            validated_request.returncode,
            0,
            msg="PC-12/§4.1 fila 1: `validate-request` debe resolver el "
                "localizador del request sin `--execution-context`: "
                + validated_request.stderr,
        )
        validated_packet = self.cli(
            case,
            "validate-packet",
            "--project-root",
            str(case.root),
            "--request",
            str(case.request_path),
            "--packet",
            str(case.packet_path),
        )
        self.assertEqual(
            validated_packet.returncode,
            0,
            msg="PC-12/§4.1 fila 1: `validate-packet` debe resolver el "
                "localizador del request sin `--execution-context`: "
                + validated_packet.stderr,
        )

        # -- render completo: identidad byte a byte con el paquete publicado
        rendered = self.cli(
            case,
            "render",
            "--project-root",
            str(case.root),
            "--request",
            str(case.request_path),
        )
        self.assertEqual(
            rendered.returncode,
            0,
            msg="PC-12: `render` por defecto debe emitir el paquete completo "
                "desde el consumidor instalado: " + rendered.stderr,
        )
        self.assertEqual(
            rendered.stdout.encode("utf-8"),
            case.packet_path.read_bytes(),
            msg="PC-12: el render del consumidor instalado debe ser "
                "byte-idéntico al PACKET.md publicado (sin normalización)",
        )

        # -- emisión C canónica --------------------------------------------
        first = self.route_c(case)
        identification = self.route_c_identification(first)
        self.assertEqual(
            set(identification),
            ROUTE_C_CONTRACT_KEYS,
            msg="PC-12/§4.2: la identificación C debe tener exactamente los "
                f"siete campos declarados; obtuvo {sorted(identification)}",
        )
        self.assertEqual(
            identification,
            self.expected_identification(case),
            msg="PC-12/§4.2: la identificación C del consumidor instalado debe "
                "ser el objeto completo y exacto derivado de los archivos "
                "publicados",
        )
        self.assertEqual(
            Path(identification["project_root"]),
            case.root,
            msg="PC-12/§4.2: `project_root` debe ser la raíz absoluta del "
                f"consumidor; obtuvo {identification['project_root']!r}",
        )
        self.assertEqual(
            identification["contract"],
            request["contract"],
            msg="PC-12/§4.2: el contrato debe conservar todos sus campos "
                "declarados y su digest",
        )

        second = self.route_c(case)
        self.assertEqual(
            first.stdout.encode("utf-8"),
            second.stdout.encode("utf-8"),
            msg="PC-12/§4.2: para iguales archivos y raíz la emisión C del "
                "consumidor instalado debe ser determinista",
        )
        self.assertEqual(
            self.route_c_identification(second),
            identification,
            msg="PC-12/§4.2: ambas corridas deben emitir el mismo objeto",
        )

        # -- sin efectos: ni archivos publicados ni instalación global ------
        self.assertEqual(
            self.tracked_bytes(case),
            before,
            msg="PC-12: el recorrido no debe modificar request, paquete, "
                "estado ni contexto del consumidor",
        )
        self.assertEqual(
            self.packet_dirs(case),
            [case.packet_id],
            msg="PC-12: el recorrido no debe publicar ni crear otro paquete",
        )
        self.assertEqual(
            global_installation_snapshot(),
            global_before,
            msg="PC-12: resolver, validar y emitir C desde el consumidor "
                "aislado no debe modificar la instalación global del proceso",
        )


class TestIsolatedConsumerFailClosed(IsolatedInstalledConsumerCase):
    def test_pc12_isolated_consumer_rejects_divergent_packet_and_non_canonical_copies_fail_closed(
        self,
    ) -> None:
        """PC-12 con PC-02 (spec §4.2 puntos 1-3 y 6; §4.5; §5 PC-02).

        Promesa observable: en el consumidor INSTALADO, C rechaza fail-closed
        un `PACKET.md` publicado divergente (cuerpo alterado, cabecera
        intacta) y sendas copias no canónicas — request byte-idéntico fuera de
        `.cdad/packets/<id>/REQUEST.json` y contexto v2 byte-idéntico fuera de
        `.cdad/executions/<id>/execution.json` —: sin identificación, rc≠0,
        diagnóstico con envoltura `ERROR:` que no divulga el cuerpo, sin
        efectos persistentes y sin normalizar ni reescribir ninguno de los
        archivos; control positivo (la identificación canónica) antes y
        después de cada tanda negativa.

        R4: sin esta prueba, las restricciones de C estarían acreditadas solo
        en el checkout: un consumidor instalado podría aceptar un paquete
        divergente o una copia fuera de su ubicación canónica y despachar un
        encargo nunca validado, sin que ninguna prueba lo notara.
        """
        case = self.publish("cdad-t5e2e-failclosed-")
        original = case.packet_path.read_bytes()

        # Control positivo ANTES de las tandas negativas.
        baseline = self.route_c_identification(self.route_c(case))
        before = self.tracked_bytes(case)

        # -- (A) paquete publicado divergente -------------------------------
        tampered_marker = "tampered-body-line-not-part-of-the-contract"
        tampered = original + tampered_marker.encode("utf-8") + b"\n"
        case.packet_path.write_bytes(tampered)
        stderr = self.assert_rejection(self.route_c(case), "PC-12/divergente")
        self.assertRegex(
            stderr,
            r"(?i)(?<![A-Za-z0-9_])packet(?!\.py)[^\n]{0,60}"
            r"(differ|diverg|match|can[oó]nic)"
            r"|(differ|diverg|match|can[oó]nic)[^\n]{0,60}"
            r"(?<![A-Za-z0-9_])packet(?!\.py)",
            msg="PC-12/PC-09: el diagnóstico del consumidor instalado debe "
                f"distinguir la divergencia del paquete; stderr={stderr!r}",
        )
        for fragment in (tampered_marker, *_MISSING_BODY_FRAGMENTS):
            self.assertNotIn(
                fragment,
                stderr,
                msg="PC-12/PC-09: el diagnóstico no debe divulgar el cuerpo "
                    f"del encargo (fragmento {fragment!r})",
            )
        self.assertEqual(
            case.packet_path.read_bytes(),
            tampered,
            msg="PC-12: el rechazo no debe normalizar ni reescribir el "
                "PACKET.md divergente",
        )
        self.assertEqual(
            self.tracked_bytes(case)["request"],
            before["request"],
            msg="PC-12: el rechazo no debe reescribir el request publicado",
        )
        case.packet_path.write_bytes(original)
        self.assertEqual(
            self.tracked_bytes(case),
            before,
            msg="PC-12: el rechazo no debe dejar efectos persistentes en "
                "request, paquete, estado ni contexto",
        )

        # Control positivo DESPUÉS de (A): el rechazo no es universal.
        self.assertEqual(
            self.route_c_identification(self.route_c(case)),
            baseline,
            msg="PC-12: tras rechazar el paquete divergente, el consumidor "
                "instalado debe seguir emitiendo la identificación canónica",
        )

        # -- (B) request fuera de la ubicación publicada ---------------------
        copy_path = case.root / "REQUEST-copy.json"
        copy_path.write_bytes(case.request_path.read_bytes())
        self.assertEqual(
            copy_path.read_bytes(),
            case.request_path.read_bytes(),
            msg="fixture: la copia debe ser byte-idéntica al request publicado",
        )
        copy_before = copy_path.read_bytes()
        result = self.cli(
            case,
            "render",
            "--project-root",
            str(case.root),
            "--request",
            str(copy_path),
            "--route",
            "C",
        )
        stderr = self.assert_rejection(result, "PC-12/request no publicado")
        expected_reference = f".cdad/packets/{case.packet_id}/REQUEST.json"
        self.assertIn(
            expected_reference,
            stderr,
            msg="PC-12/PC-09: el diagnóstico debe presentar de manera segura y "
                "project-relative el request publicado esperado "
                f"({expected_reference!r}); stderr={stderr!r}",
        )
        self.assertEqual(
            copy_path.read_bytes(),
            copy_before,
            msg="PC-12: el rechazo no debe reescribir la copia del request",
        )
        self.assertEqual(
            self.tracked_bytes(case),
            before,
            msg="PC-12: el rechazo no debe modificar el paquete publicado, el "
                "estado ni el contexto (sin efectos persistentes)",
        )

        # -- (C) contexto v2 fuera de la ubicación canónica ------------------
        context_path = case.root / case.request["execution_context"]
        context_copy = case.root / "EXECUTION.json"
        context_copy.write_bytes(context_path.read_bytes())
        self.assertEqual(
            context_copy.read_bytes(),
            context_path.read_bytes(),
            msg="fixture: la copia debe ser byte-idéntica al contexto canónico",
        )
        context_copy_before = context_copy.read_bytes()
        result = self.cli(
            case,
            "render",
            "--project-root",
            str(case.root),
            "--execution-context",
            str(context_copy),
            "--request",
            str(case.request_path),
            "--route",
            "C",
        )
        stderr = self.assert_rejection(result, "PC-12/contexto no canónico")
        self.assertRegex(
            stderr,
            r"(?i)(execution context|contexto de ejecuci[oó]n)",
            msg="PC-12/PC-09: el diagnóstico debe distinguir la causa de "
                f"contexto (§4.5); stderr={stderr!r}",
        )
        canonical_reference = (
            f".cdad/executions/{case.request['execution_id']}/execution.json"
        )
        self.assertIn(
            canonical_reference,
            stderr,
            msg="PC-12/PC-09: el diagnóstico debe presentar la referencia "
                f"canónica segura project-relative ({canonical_reference!r}); "
                f"stderr={stderr!r}",
        )
        self.assertEqual(
            context_copy.read_bytes(),
            context_copy_before,
            msg="PC-12: el rechazo no debe reescribir la copia del contexto",
        )
        self.assertEqual(
            self.tracked_bytes(case),
            before,
            msg="PC-12: el rechazo no debe modificar request, paquete, estado "
                "ni contexto canónico (sin efectos persistentes)",
        )
        self.assertEqual(
            self.packet_dirs(case),
            [case.packet_id],
            msg="PC-12: ninguna tanda negativa debe publicar paquetes",
        )

        # Control positivo FINAL después de todas las tandas negativas.
        self.assertEqual(
            self.route_c_identification(self.route_c(case)),
            baseline,
            msg="PC-12: tras las tandas negativas, el consumidor instalado "
                "debe seguir emitiendo la identificación canónica completa",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
