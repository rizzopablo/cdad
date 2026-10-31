#!/usr/bin/env python3
"""PROPERTIES — 010-004 T5: propiedades sembradas de INV-04 e INV-05.

Contrato: `docs/specs/010-004-packet-dispatch-ergonomics/spec.md`
(pin `fc6b2ccc…`), §6 (INV-04, INV-05), §4.2, §4.3, §4.4 y §5 (PC-01, PC-02,
PC-03, PC-08a). El CLI del repo se ejercita por subproceso, caja negra: este
archivo no importa ni lee el módulo del CLI, ni `skills/`, `scripts/`,
`sources/`, `agents/` ni `build/`. Archivo NUEVO: no edita tests existentes ni
fixtures compartidas; reutiliza `PublishedPacketCase` y los oráculos de ruta C
de `tests/test_010_004_t3_red.py`.

Semilla y muestra (declaradas, reproducibles):
- `SEED = 20261030`: un único `random.Random(SEED)` por propiedad, sin
  generadores abiertos ni exploración no reproducible.
- `CASES_PER_PROPERTY = 100`: entradas generadas y EJECUTADAS por propiedad,
  estratificadas por familia/región con cuota fija (25 cada una) para que
  ninguna región quede sin ejercitar y la muestra no dependa del azar.

Trazabilidad test → invariante → postcondición → consecuencia de usuario (R4):

| Test | Invariante | PC | R4: sin este test el usuario… |
|---|---|---|---|
| `test_inv05_complete_equality…` | INV-05: la igualdad completa no se sustituye por igualdad de cabecera ni semejanza semántica | PC-08a (§4.4), PC-01/PC-02 (§4.2) | …una comparación «semántica» de la cabecera —o una normalización de bytes— despacharía un paquete cuyas instrucciones nunca se validaron: el encargo ejecutado no sería el publicado (el episodio I-5 perdió backticks en un despacho real). |
| `test_inv04_failed_admission…` | INV-04: ninguna ruta permite elegir otro paquete tras fallar la admisión | PC-02 (§4.2), PC-03 (§4.3) | …un rechazo podría deslizarse al paquete que sí existe en disco (u otra copia) y el usuario ejecutaría un encargo que nunca fue admitido: el rechazo se convertiría en selección silenciosa. |

Selección acotada y justificada (no duplica la cobertura existente):
- INV-05: `tests/test_010_004_t3_red.py` cubre UNA divergencia de cuerpo por
  ruta C y `tests/test_role_packet_render.py` cubre cuerpo, metadata y CRLF por
  `validate-packet`. La propiedad generaliza la superficie que el despacho usa
  (la verificación publicada de C) sobre las tres regiones del paquete
  publicado —cabecera, cuerpo y bytes posteriores al cierre JSON— con 100
  mutaciones sembradas: la cabecera solo tenía casos puntuales y los bytes
  posteriores al cierre no tenían ninguno.
- INV-04: las pruebas vigentes rechazan variantes elegidas a mano (contexto v1,
  request fuera de la ubicación publicada, contexto no canónico, paquete
  divergente). La propiedad siembra familias de admisión fallida (copia fuera
  de la ubicación canónica, request no publicado, request ausente e
  identificación inválida) contra un SEGUNDO paquete presente en disco —que
  ninguna prueba vigente contempla— y verifica que un rechazo nunca emite la
  identificación de ese otro paquete.

Límites honestos: la propiedad acredita conducta del CLI sobre archivos
publicados; no acredita recepción nativa del mensaje por un runtime ni la
obediencia de un modelo (§4.7).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
import hashlib
import json
import random
from pathlib import Path
import unittest

from tests.test_010_004_t3_red import (
    ROUTE_C_DECLARATION,
    PublishedPacketCase,
    run_cli,
)


# §4.3: el marcador A abre la cabecera; su cierre JSON no termina el paquete.
PACKET_MARKER = b"---cdad-packet-json\n"
PACKET_METADATA_CLOSE = b"---end-cdad-packet-json"

# Propiedades sembradas y acotadas: semilla fija declarada y 100 entradas
# generadas y ejecutadas por propiedad.
SEED = 20261030
CASES_PER_PROPERTY = 100

# Regiones del paquete publicado que INV-05 no deja de comparar, y familias de
# admisión fallida que INV-04 no deja resolver hacia otro paquete.
INV05_FAMILIES = ("header-semantic", "header-value", "body", "post-close")
INV04_FAMILIES = (
    "copy-outside-canonical",
    "unpublished-request",
    "missing-request",
    "invalid-identification",
)


def _canonical_header(metadata: dict) -> bytes:
    """Serialización canónica de la cabecera (la que produce el render)."""
    return json.dumps(
        metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _family_quotas(families: tuple[str, ...]) -> Counter:
    """Cuota declarada por familia: la muestra no depende del azar."""
    quota, extra = divmod(CASES_PER_PROPERTY, len(families))
    return Counter(
        {
            family: quota + (1 if position < extra else 0)
            for position, family in enumerate(families)
        }
    )


@dataclass(frozen=True)
class _PublishedParts:
    """Regiones del `PACKET.md` publicado, sin interpretar su contenido."""

    opening: bytes
    header_text: bytes
    body: bytes
    metadata: dict

    @property
    def header_suffix(self) -> bytes:
        """Cierre de cabecera y cuerpo: todo lo que sigue al texto JSON."""
        return PACKET_METADATA_CLOSE + self.body

    @property
    def body_prefix(self) -> bytes:
        """Todo lo anterior al cuerpo (apertura, cabecera y cierre)."""
        return self.opening + self.header_text + PACKET_METADATA_CLOSE

    @property
    def canonical(self) -> bytes:
        return self.body_prefix + self.body


def _split_published(canonical: bytes) -> _PublishedParts:
    """Divide el paquete publicado en sus regiones; falla si no es canónico."""
    if not canonical.startswith(PACKET_MARKER):
        raise AssertionError(
            "fixture: el paquete publicado no abre con el marcador A"
        )
    if canonical.count(PACKET_METADATA_CLOSE) != 1:
        raise AssertionError(
            "fixture: el paquete publicado debe declarar un único cierre de "
            "cabecera"
        )
    header_end = canonical.index(PACKET_METADATA_CLOSE)
    header_text = canonical[len(PACKET_MARKER) : header_end]
    parts = _PublishedParts(
        opening=PACKET_MARKER,
        header_text=header_text,
        body=canonical[header_end + len(PACKET_METADATA_CLOSE) :],
        metadata=json.loads(header_text),
    )
    if parts.canonical != canonical:
        raise AssertionError(
            "fixture: las regiones no reconstruyen el paquete publicado"
        )
    return parts


def _leaf_paths(node: object, prefix: tuple = ()) -> list[tuple]:
    """Rutas a las hojas escalares de un documento JSON."""
    if isinstance(node, dict):
        paths: list[tuple] = []
        for key, value in node.items():
            paths.extend(_leaf_paths(value, prefix + (key,)))
        return paths
    if isinstance(node, list):
        paths = []
        for index, value in enumerate(node):
            paths.extend(_leaf_paths(value, prefix + (index,)))
        return paths
    return [prefix]


def _mutate_leaf(document: dict, path: tuple) -> None:
    """Cambia el valor de una hoja conservando el resto del documento."""
    target: object = document
    for key in path[:-1]:
        target = target[key]
    leaf = path[-1]
    value = target[leaf]
    if isinstance(value, bool):
        target[leaf] = not value
    elif isinstance(value, int):
        target[leaf] = value + 1
    elif isinstance(value, str):
        target[leaf] = value + "mut"
    elif value is None:
        target[leaf] = "mutated"
    else:
        raise AssertionError(f"fixture: hoja no soportada en {path!r}")


def _fill_quota(
    rng: random.Random,
    quota: int,
    factories: tuple[Callable[[random.Random], tuple[str, bytes]], ...],
    seen: set[bytes],
    canonical: bytes,
) -> list[tuple[str, bytes]]:
    """Completa la cuota con mutaciones distintas, distintas entre sí y
    distintas del canónico (una entrada igual al canónico vaciaría la
    propiedad)."""
    produced: list[tuple[str, bytes]] = []
    attempts = 0
    limit = quota * 50 + 100
    while len(produced) < quota:
        attempts += 1
        if attempts > limit:
            raise AssertionError(
                "fixture: el generador no alcanza la cuota declarada de "
                f"entradas distintas ({quota})"
            )
        label, mutant = rng.choice(factories)(rng)
        if mutant == canonical or mutant in seen:
            continue
        seen.add(mutant)
        produced.append((label, mutant))
    return produced


def inv05_cases(
    rng: random.Random, parts: _PublishedParts
) -> list[tuple[str, bytes]]:
    """100 mutaciones sembradas de un paquete publicado, por región (§6 INV-05).

    Cada mutación difiere del canónico y ninguna se repite. Las de cabecera
    incluyen transformaciones semánticamente neutras (misma metadata, otros
    bytes): solo la comparación completa puede rechazarlas.
    """

    canonical = parts.canonical

    def header_indented(sub_rng: random.Random) -> tuple[str, bytes]:
        indent = sub_rng.choice((1, 2, 3, 4))
        text = json.dumps(
            parts.metadata, ensure_ascii=False, indent=indent
        ).encode("utf-8")
        return (
            f"header-semantic:indented-{indent}",
            parts.opening + text + b"\n" + parts.header_suffix,
        )

    def header_spaced(sub_rng: random.Random) -> tuple[str, bytes]:
        after_comma = sub_rng.choice((1, 2, 3))
        after_colon = sub_rng.choice((1, 2))
        text = json.dumps(
            parts.metadata,
            ensure_ascii=False,
            separators=("," + " " * after_comma, ":" + " " * after_colon),
        ).encode("utf-8")
        return (
            f"header-semantic:spaced-{after_comma}-{after_colon}",
            parts.opening + text + b"\n" + parts.header_suffix,
        )

    def header_reordered(sub_rng: random.Random) -> tuple[str, bytes]:
        keys = list(parts.metadata)
        sub_rng.shuffle(keys)
        # Sin `sort_keys`: se conserva el orden sorteado (misma semántica JSON,
        # otros bytes) — con orden canónico el mutante sería el propio canónico.
        text = json.dumps(
            {key: parts.metadata[key] for key in keys},
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        return (
            "header-semantic:key-order",
            parts.opening + text + b"\n" + parts.header_suffix,
        )

    def header_padded(sub_rng: random.Random) -> tuple[str, bytes]:
        padding = sub_rng.randrange(1, 6)
        compact = _canonical_header(parts.metadata)
        return (
            f"header-semantic:brace-padding-{padding}",
            parts.opening
            + b"{"
            + b" " * padding
            + compact[1:]
            + b"\n"
            + parts.header_suffix,
        )

    def header_value(sub_rng: random.Random) -> tuple[str, bytes]:
        path = sub_rng.choice(_leaf_paths(parts.metadata))
        document = json.loads(json.dumps(parts.metadata))
        _mutate_leaf(document, path)
        return (
            "header-value:" + "/".join(str(part) for part in path),
            parts.opening
            + _canonical_header(document)
            + b"\n"
            + parts.header_suffix,
        )

    def body_insert(sub_rng: random.Random) -> tuple[str, bytes]:
        lines = parts.body.split(b"\n")
        index = sub_rng.randrange(len(lines))
        line = f"injected instruction line {sub_rng.randrange(10**9)}".encode()
        lines.insert(index, line)
        return "body:insert-line", parts.body_prefix + b"\n".join(lines)

    def body_delete(sub_rng: random.Random) -> tuple[str, bytes]:
        lines = parts.body.split(b"\n")
        candidates = [i for i, line in enumerate(lines) if line.strip()]
        del lines[sub_rng.choice(candidates)]
        return "body:delete-line", parts.body_prefix + b"\n".join(lines)

    def body_substitute(sub_rng: random.Random) -> tuple[str, bytes]:
        lines = parts.body.split(b"\n")
        candidates = [i for i, line in enumerate(lines) if line.strip()]
        position = sub_rng.choice(candidates)
        line = bytearray(lines[position])
        column = sub_rng.randrange(len(line))
        replacement = ord("X") if line[column] != ord("X") else ord("Y")
        line[column] = replacement
        lines[position] = bytes(line)
        return "body:substitute-char", parts.body_prefix + b"\n".join(lines)

    def body_duplicate(sub_rng: random.Random) -> tuple[str, bytes]:
        lines = parts.body.split(b"\n")
        candidates = [i for i, line in enumerate(lines) if line.strip()]
        position = sub_rng.choice(candidates)
        lines.insert(position, lines[position])
        return "body:duplicate-line", parts.body_prefix + b"\n".join(lines)

    def post_close_text(sub_rng: random.Random) -> tuple[str, bytes]:
        trailer = (
            f"appended after the JSON close {sub_rng.randrange(10**9)}".encode()
        )
        return "post-close:text-line", canonical + b"\n" + trailer + b"\n"

    def post_close_blank_then_text(sub_rng: random.Random) -> tuple[str, bytes]:
        blanks = sub_rng.randrange(1, 4)
        trailer = f"second trailer line {sub_rng.randrange(10**9)}".encode()
        return (
            "post-close:blank-then-text",
            canonical + b"\n" * blanks + trailer + b"\n",
        )

    def post_close_extra_newline(
        sub_rng: random.Random,
    ) -> tuple[str, bytes]:
        return "post-close:extra-newline", canonical + b"\n"

    def post_close_duplicate_close(
        sub_rng: random.Random,
    ) -> tuple[str, bytes]:
        return (
            "post-close:duplicate-close-marker",
            canonical + b"\n" + PACKET_METADATA_CLOSE + b"\n",
        )

    families: tuple[
        tuple[Callable[[random.Random], tuple[str, bytes]], ...], ...
    ] = (
        (header_indented, header_spaced, header_reordered, header_padded),
        (header_value,),
        (body_insert, body_delete, body_substitute, body_duplicate),
        (
            post_close_text,
            post_close_blank_then_text,
            post_close_extra_newline,
            post_close_duplicate_close,
        ),
    )

    quota, extra = divmod(CASES_PER_PROPERTY, len(families))
    cases: list[tuple[str, bytes]] = []
    seen: set[bytes] = set()
    for position, factories in enumerate(families):
        cases.extend(
            _fill_quota(
                rng,
                quota + (1 if position < extra else 0),
                factories,
                seen,
                canonical,
            )
        )
    rng.shuffle(cases)
    return cases


@dataclass(frozen=True)
class _AdmissionFailure:
    """Estado materializado de un escenario de admisión fallida."""

    label: str
    request_path: Path
    cleanup: Callable[[], None]


def inv04_scenarios(
    rng: random.Random,
    case: object,
    decoy_id: str,
    count: int,
) -> list[Callable[[int], _AdmissionFailure]]:
    """`count` escenarios de admisión fallida, estratificados por familia.

    Cada entrada es un `setup(index)` perezoso: materializa el estado, devuelve
    el escenario y deja su `cleanup` para restaurar los archivos canónicos.
    """

    canonical_request: bytes = case.request_path.read_bytes()
    document = json.loads(canonical_request)
    other_packet_ids = (
        decoy_id,
        "packet-other-identity",
        "003-001-role-packets-reviewer-review-001",
    )
    identification_kinds = (
        "packet-id-decoy",
        "packet-id-other",
        "execution-id-other",
        "contract-digest",
        "drop-packet-id",
        "drop-contract",
        "role-change",
        "truncated-json",
    )

    def copy_outside_canonical(index: int) -> _AdmissionFailure:
        directory = case.root / "admission-copies" / f"{index:03d}"
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"REQUEST-{rng.randrange(10**9)}.json"
        path.write_bytes(canonical_request)

        def cleanup() -> None:
            path.unlink()
            directory.rmdir()

        return _AdmissionFailure("copy-outside-canonical", path, cleanup)

    def unpublished_request(index: int) -> _AdmissionFailure:
        directory = case.root / "admission-unpublished" / f"{index:03d}"
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "REQUEST.json"
        path.write_bytes(canonical_request)
        hidden = case.request_path.with_name("REQUEST.json.unpublished")
        case.request_path.rename(hidden)

        def cleanup() -> None:
            hidden.rename(case.request_path)
            path.unlink()
            directory.rmdir()

        return _AdmissionFailure("unpublished-request", path, cleanup)

    def missing_request(index: int) -> _AdmissionFailure:
        hidden = case.request_path.with_name(f"REQUEST.json.missing-{index:03d}")
        case.request_path.rename(hidden)

        def cleanup() -> None:
            hidden.rename(case.request_path)

        return _AdmissionFailure("missing-request", case.request_path, cleanup)

    def invalid_identification(index: int) -> _AdmissionFailure:
        kind = rng.choice(identification_kinds)
        mutated = json.loads(json.dumps(document))
        if kind == "packet-id-decoy":
            mutated["packet_id"] = decoy_id
        elif kind == "packet-id-other":
            mutated["packet_id"] = rng.choice(other_packet_ids[1:])
        elif kind == "execution-id-other":
            mutated["execution_id"] = "exec-other-identity"
        elif kind == "contract-digest":
            mutated["contract"]["sha256"] = "0" * 64
        elif kind == "drop-packet-id":
            mutated.pop("packet_id")
        elif kind == "drop-contract":
            mutated.pop("contract")
        elif kind == "role-change":
            mutated["role"] = "implementer"
        else:  # truncated-json: la identificación deja de ser legible
            case.request_path.write_bytes(
                canonical_request[: rng.randrange(1, 80)]
            )
        if kind != "truncated-json":
            case.request_path.write_text(
                json.dumps(mutated, sort_keys=True), encoding="utf-8"
            )

        def cleanup() -> None:
            case.request_path.write_bytes(canonical_request)

        return _AdmissionFailure(
            f"invalid-identification:{kind}", case.request_path, cleanup
        )

    factories: tuple[Callable[[int], _AdmissionFailure], ...] = (
        copy_outside_canonical,
        unpublished_request,
        missing_request,
        invalid_identification,
    )
    quota, extra = divmod(count, len(factories))
    plan: list[Callable[[int], _AdmissionFailure]] = []
    for position, factory in enumerate(factories):
        plan.extend([factory] * (quota + (1 if position < extra else 0)))
    rng.shuffle(plan)
    return plan


class TestInv05CompleteEqualityProperties(PublishedPacketCase):
    """INV-05 — la igualdad completa no se sustituye por cabecera ni semántica."""

    def test_inv05_complete_equality_rejects_every_seeded_byte_divergence(
        self,
    ) -> None:
        """INV-05 (§6), PC-08a (§4.4) y PC-01/PC-02 (§4.2).

        Promesa observable: para un paquete publicado válido, los bytes
        canónicos exactos reciben una identificación C, y CADA una de las 100
        mutaciones sembradas —de cabecera (incluidas las semánticamente
        neutras), de cuerpo y de bytes posteriores al cierre JSON— se rechaza
        sin emitir identificación y sin normalizar el archivo. Una igualdad de
        cabecera o una semejanza semántica no sustituyen la igualdad completa.

        R4: sin esta prueba, una comparación semántica de la cabecera o una
        normalización de bytes despacharía un paquete cuyas instrucciones nunca
        se validaron; el encargo ejecutado no sería el publicado (I-5: un
        despacho real perdió backticks).

        Controles: la identificación canónica se exige ANTES y DESPUÉS de la
        tanda sembrada, de modo que el rechazo no pueda ser universal.
        """
        case = self.publish("cdad-t5prop-inv05-")
        canonical = case.packet_path.read_bytes()
        parts = _split_published(canonical)
        self.assertEqual(
            parts.header_text,
            _canonical_header(parts.metadata) + b"\n",
            msg="fixture: la cabecera publicada debe ser su serialización "
            "canónica (forma ya verificada por "
            "tests/test_role_packet_render.py::test_p2_metadata_is_canonical_"
            "and_matches_request); si no, las mutaciones de cabecera no "
            "estarían probando INV-05",
        )

        control = self.route_c_identification(self.route_c(case))
        self.assertEqual(
            control["packet_id"],
            case.packet_id,
            msg="control positivo (antes): el paquete canónico debe recibir su "
            "identificación C",
        )

        cases = inv05_cases(random.Random(SEED), parts)
        self.assertEqual(
            len(cases),
            CASES_PER_PROPERTY,
            msg=f"la propiedad debe generar y ejecutar {CASES_PER_PROPERTY} "
            f"entradas (semilla {SEED}); obtuvo {len(cases)}",
        )
        mutants = {mutant for _, mutant in cases}
        self.assertEqual(
            len(mutants),
            CASES_PER_PROPERTY,
            msg="las entradas sembradas deben ser distintas entre sí",
        )
        self.assertNotIn(
            canonical,
            mutants,
            msg="una entrada igual al canónico vaciaría la propiedad",
        )
        self.assertEqual(
            Counter(label.split(":", 1)[0] for label, _ in cases),
            _family_quotas(INV05_FAMILIES),
            msg="la muestra debe cubrir las tres regiones comparadas "
            f"(cabecera, cuerpo y bytes posteriores al cierre): {INV05_FAMILIES}",
        )

        accepted: list[dict[str, str]] = []
        for label, mutant in cases:
            case.packet_path.write_bytes(mutant)
            result = self.route_c(case)
            if result.returncode == 0:
                accepted.append(
                    {
                        "input": label,
                        "sha256": hashlib.sha256(mutant).hexdigest(),
                    }
                )
                continue
            self.assertNotIn(
                ROUTE_C_DECLARATION,
                result.stdout,
                msg=f"INV-05: un paquete mutado ({label}) no debe recibir la "
                f"declaración de ruta C; stdout={result.stdout!r}",
            )
            self.assertNotIn(
                "```json",
                result.stdout,
                msg=f"INV-05: un paquete mutado ({label}) no debe recibir un "
                f"bloque de identificación; stdout={result.stdout!r}",
            )
            self.assertEqual(
                case.packet_path.read_bytes(),
                mutant,
                msg=f"INV-05 ({label}): la verificación no debe normalizar ni "
                "reescribir el paquete recibido",
            )
        case.packet_path.write_bytes(canonical)

        self.assertEqual(
            accepted,
            [],
            msg="INV-05: la igualdad completa no se sustituye por igualdad de "
            "cabecera ni semejanza semántica; estas mutaciones sembradas "
            f"(semilla {SEED}) fueron aceptadas: {accepted}",
        )

        restored = self.route_c_identification(self.route_c(case))
        self.assertEqual(
            restored,
            control,
            msg="control positivo (después): restaurado el canónico, la "
            "identificación debe ser la misma que antes de la tanda sembrada",
        )


class TestInv04NoSubstitutePacketProperties(PublishedPacketCase):
    """INV-04 — ninguna ruta elige otro paquete tras fallar la admisión."""

    def test_inv04_failed_admission_never_emits_another_packet_identification(
        self,
    ) -> None:
        """INV-04 (§6), PC-02 (§4.2) y PC-03 (§4.3).

        Promesa observable: con un SEGUNDO paquete presente en
        `.cdad/packets/`, cada una de las 100 variantes sembradas de admisión
        fallida —request fuera de la ubicación canónica, request no publicado,
        request ausente e identificación inválida— se rechaza sin emitir
        identificación alguna y, en particular, sin emitir la del otro paquete;
        el rechazo no publica ni crea paquetes.

        R4: sin esta prueba, un rechazo podría deslizarse al paquete que sí
        existe en disco (u otra copia) y el usuario ejecutaría un encargo que
        nunca fue admitido: el rechazo se convertiría en selección silenciosa.

        Controles: la identificación del paquete solicitado se exige ANTES y
        DESPUÉS de la tanda, de modo que el rechazo no pueda ser universal.
        """
        case = self.publish("cdad-t5prop-inv04-")
        packets_dir = case.root / ".cdad" / "packets"
        canonical_request = case.request_path.read_bytes()
        decoy_id = f"{case.packet_id}-decoy"
        decoy = packets_dir / decoy_id
        decoy.mkdir()
        (decoy / "REQUEST.json").write_bytes(canonical_request)
        (decoy / "PACKET.md").write_bytes(case.packet_path.read_bytes())

        control = self.route_c_identification(self.route_c(case))
        self.assertEqual(
            control["packet_id"],
            case.packet_id,
            msg="control positivo (antes): el paquete canónico debe recibir su "
            "identificación C",
        )

        scenarios = inv04_scenarios(
            random.Random(SEED), case, decoy_id, CASES_PER_PROPERTY
        )
        self.assertEqual(
            len(scenarios),
            CASES_PER_PROPERTY,
            msg=f"la propiedad debe generar y ejecutar {CASES_PER_PROPERTY} "
            f"entradas (semilla {SEED}); obtuvo {len(scenarios)}",
        )

        observed: list[str] = []
        violations: list[dict[str, object]] = []
        for index, setup in enumerate(scenarios):
            scenario = setup(index)
            observed.append(scenario.label.split(":", 1)[0])
            packets_before = sorted(entry.name for entry in packets_dir.iterdir())
            result = run_cli(
                "render",
                "--project-root",
                str(case.root),
                "--request",
                str(scenario.request_path),
                "--route",
                "C",
                cwd=case.root,
            )
            packets_after = sorted(entry.name for entry in packets_dir.iterdir())
            scenario.cleanup()
            if (
                result.returncode == 0
                or result.stdout != ""
                or ROUTE_C_DECLARATION in result.stdout
                or decoy_id in result.stdout
                or packets_after != packets_before
            ):
                violations.append(
                    {
                        "input": scenario.label,
                        "returncode": result.returncode,
                        "stdout": result.stdout[:200],
                        "published": packets_before != packets_after,
                    }
                )

        self.assertEqual(
            Counter(observed),
            _family_quotas(INV04_FAMILIES),
            msg="la muestra debe cubrir las familias declaradas de admisión "
            f"fallida: {INV04_FAMILIES}",
        )
        self.assertEqual(
            violations,
            [],
            msg="INV-04: tras fallar la admisión ninguna ruta puede emitir una "
            "identificación —tampoco la del otro paquete presente en disco— ni "
            f"publicar paquetes (semilla {SEED}); violaciones: {violations}",
        )
        self.assertEqual(
            case.request_path.read_bytes(),
            canonical_request,
            msg="las variantes sembradas deben restaurar el request publicado",
        )

        after = self.route_c_identification(self.route_c(case))
        self.assertEqual(
            after,
            control,
            msg="control positivo (después): con el request canónico "
            "restaurado, la identificación debe ser la misma que antes de la "
            "tanda sembrada",
        )
        self.assertNotIn(
            decoy_id,
            json.dumps(after),
            msg="INV-04: la identificación emitida debe ser la del paquete "
            "solicitado, no la del otro paquete presente en disco",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
