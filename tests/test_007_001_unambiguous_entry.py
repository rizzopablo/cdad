#!/usr/bin/env python3
"""007-001 RED — entrada inequívoca: situación operativa, siguiente operación
y referencia verificable de aprobación.

Contract: docs/specs/007-001-unambiguous-entry/spec.md
(sha256 base b09f5410dd8ac7fd64e8c4784d500a4f87de3ac8e5c83e7c477ba656a90c4728,
APROBADA 2026-10-23; enmienda aprobada 2026-10-23: el localizador es
`record.index` 0-based en el historial que determina `object`, según §2.3
«Localizadores y determinismo» y §6) §2.1 (situación y pertenencia mínima),
§2.2 (siguiente operación), §2.3 (referencia de aprobación: vocabulario,
fuentes, tablas C1–C3, D1, S1–S6, A1–A4, localizadores), §2.4 (compatibilidad
diagnóstica),
§3 (alineación del orquestador), §4 PC-01…PC-14, §5 INV-1…INV-8.

Audit: docs/specs/007-001-unambiguous-entry/test-audit.md (matriz de
fixtures y las cinco aclaraciones del orquestador que estos tests aplican).

Superficie observable bajo prueba (caja negra: SOLO subproceso sobre el CLI
del skill; el módulo NUNCA se importa y la implementación NUNCA se lee):

    python3 <skill-dir>/scripts/cdad_packet.py status --project-root <ABS>
        [--max-bytes N]

Los proyectos son fixtures sintéticos autocontenidos en tempdirs (política,
state, contrato, autoridad y paquete armados por el test con los helpers del
proyecto), el `HOME` del subproceso SIEMPRE es un tempdir vacío (nunca el
HOME real) y los ids son inventados (`999-…`): ningún proyecto real ni ruta
del dueño. Cada test falla en la ASERCIÓN del comportamiento del contrato
(AssertionError), nunca en ImportError, SyntaxError, KeyError, JSONDecodeError
ni error de setup: los accesos al documento pasan por helpers que declaran la
falta como aserción.

Mapeo test → postcondición (spec §4):

  test_situation_operation_matrix                  -> PC-01 (los seis valores
      de §2.1 y la precedencia de ilegibilidad, parametrizados)
  test_prepared_and_dispatched_operations          -> PC-02 (preparado →
      validate-packet; despachado → reconcile; scripts y procedimientos
      existen bajo el directorio del skill)
  test_closed_execution_is_history                 -> PC-03 (ejecución
      histórica cerrada: ni `execution-active` ni aprobación vigente)
  test_unresolved_pending_work_is_not_dispatchable -> PC-04 (8 variaciones de
      pertenencia y selección; parametrizado)
  test_architect_approval_uses_epic_mandate        -> PC-05 (mandato real de
      `epic_history`, `record.index` 0-based resoluble, sin pin del plan;
      A2/A3/A4)
  test_spec_approval_status_matrix                 -> PC-06 (tabla S1–S6,
      parametrizada, con las combinaciones bytes cambiados + sin registros y
      bytes cambiados + todos sustituidos)
  test_approval_checks_path_and_current_bytes      -> PC-07 (hash con ruta
      ajena nunca vigente; bytes cambiados nunca vigente; precedencia de
      ausencia/sustitución ante bytes cambiados)
  test_draft_plan_requires_no_approval             -> PC-08 (`draft-plan` sin
      aprobación y sin exigir bytes; observed_sha256 explícito)
  test_approval_unknown_vs_absent                  -> PC-09 (C1/C2/S1/S2:
      desconocida ≠ ausente)
  test_approval_selection_and_supersession         -> PC-10 (selección
      determinista entre varios registros y sustituciones)
  test_status_is_additive                          -> PC-11 grupo 1
      (compatibilidad estricta: sólo se agregan `situation`,
      `next.operation` y `authority.approval_reference`)
  test_status_preserves_and_extends_unknowns       -> PC-11 grupo 2
      (extensión diagnóstica: diagnósticos anteriores intactos y causas
      nuevas por concepto)
  test_status_is_read_only                          -> PC-12 (CONTROL: pasa
      hoy y debe seguir pasando; ninguna escritura)
  test_status_bound_and_history_independence        -> PC-13 (un único JSON
      acotado; `--max-bytes` falla cerrado; historial no seleccionado no
      altera la salida)
  test_orchestrator_references_operation_map        -> PC-14 (mapa
      verbo→script documentado, scripts existentes y distinción de los dos
      registros de despacho)

RED de corrección (review-001, packet test-writer-red-002):

  test_malformed_approval_sources_are_unknown_not_absent -> BLOCKING 1
      (stage_history/epic_history no interpretables como lista: `desconocida`
      con causa; historiales legibles sin aprobaciones: `ausente`)
  test_unreadable_contract_cause_reaches_unknowns        -> BLOCKING 2(a)
      (contrato ilegible: la causa fuente+condición llega a `unknowns`)
  test_unreadable_pending_candidate_stays_unproven       -> BLOCKING 2(b)
      (sin `active_packet`: un candidato con REQUEST.json ilegible no se
      convierte en pendiente probado y `_pending_work` no cambia)
  test_request_symlink_escape_is_unresolved              -> BLOCKING 3
      (REQUEST.json alcanzado por symlink que escapa del árbol de paquetes:
      `pending-work-unresolved` + `desconocida` + causa en `unknowns`)

RED de cierre (review-002, packet test-writer-red-003):

  test_null_history_value_is_unknown_not_absent -> BLOCKING residual
      (`stage_history`/`epic_history` con clave presente y valor null:
      `desconocida` con causa en `reason` y en `unknowns`; `[]` sigue
      produciendo `ausente` en el control del mismo fixture)

Aclaraciones del audit aplicadas aquí:

1. Estado ilegible → `situation=diagnosis` (y `at-rest` exige estado
   legible): casos `state-unreadable` / `state-missing` de PC-01.
2. S3 es alcanzable con una entrada no aprobatoria posterior que sustituye la
   clave de la única aprobación; el fixture describe el estado observado por
   el selector (caso `s3-all-superseded-bytes-changed`).
3. `observed_sha256` es `null` explícito —nunca omitido— cuando se emite
   `contract` sin comprobar bytes (PC-08 caso ilegible y S1 de PC-06).
4. `next.operation.source` de `pending-work-unresolved` es la cadena exacta
   `docs/.cdad-state.json:active_packet / .cdad/packets`.
5. Los `unknowns`/`reason` nuevos se prueban por concepto (fuente +
   condición); los diagnósticos anteriores, por contenido y orden relativo.

Riesgos declarados por el audit que estos tests fijan: `next.route` es prosa
congelada por los tests PD-5 (la acción estructurada va en `next.operation`);
`entry` no se toca; límite de 16.384 B con fixture rico; `big_doc ==
small_doc` (`record.index` del primer registro aplicable en su historial, sin
contadores derivados del historial); en reposo `next.operation.source` NO es
`docs/.cdad-state.json:execution`.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from test_004_002_t2_bootstrap import (
    CONTRACT_BYTES,
    CONTRACT_FILE,
    FEATURE_ID,
    POLICY_FILE,
    STATE_FILE,
    build_project,
    prepare_args,
    read_state,
    tree_snapshot,
    write_state,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
SKILL_DIR = REPO_ROOT / "skills" / "cdad-cycle"
MAX_BYTES = 16_384
CLI_TIMEOUT_S = 120

DECLARED_SPEC_SHA = hashlib.sha256(CONTRACT_BYTES).hexdigest()

# §2.2: rutas relativas al directorio del skill instalado.
PACKET_SCRIPT = "scripts/cdad_packet.py"
CONTINUITY_SCRIPT = "scripts/cdad_continuity.py"
RESULT_SCRIPT = "scripts/cdad_result.py"

SITUATION_VALUES = {
    "diagnosis",
    "packet-dispatched",
    "packet-prepared",
    "pending-work-unresolved",
    "execution-active",
    "at-rest",
}
APPROVAL_STATUSES = {
    "vigente",
    "ausente",
    "sustituida",
    "contrato cambiado",
    "no requerida",
    "desconocida",
}
APPROVAL_OBJECTS = {"epic-plan", "feature-spec", "draft-plan", None}
REFERENCE_KEYS = {"role", "object", "status", "record", "contract", "reason"}
RECORD_KEYS = {"path", "index", "transition_key", "approved_by"}
CONTRACT_KEYS = {"path", "declared_sha256", "observed_sha256"}
OPERATION_KEYS = ("verb", "script", "procedure", "source")

# §2.2: letras congeladas por los tests PD-5 existentes (riesgo 1 del audit).
DISPATCH_ROUTE = re.compile(r"(?i)\bdispatch|despach")
RECONCILE_ROUTE = re.compile(r"(?i)\breconcil")
REPEAT_ROUTE = re.compile(r"(?i)\b(?:repeat|resume)\b")

# PC-11 grupo 1: proyección anterior al 007-001 (campos y valores intactos).
OLD_TOP_LEVEL = frozenset({
    "project", "epic", "feature", "execution", "packet",
    "authority", "version", "next", "entry", "unknowns", "unit_contract",
})
NEW_CAUSE_TOKEN = re.compile(
    r"(?i)pertenencia|membership|active_packet|\.cdad/packets|unresolved|"
    r"inconsisten"
)

# Conceptos exigidos a las causas NUEVAS de `unknowns` (aclaración 5: no se
# exige texto estable, sí que identifiquen la fuente y la condición).
_SOURCE_REQUEST = re.compile(r"(?i)request|solicitud|request\.json|\.cdad/packets")
_SOURCE_EXECUTION = re.compile(
    r"(?i)request|solicitud|execution|ejecuci[oó]n|packet|paquete"
)
_SOURCE_PACKET = re.compile(
    r"(?i)request|solicitud|packet|paquete|directorio|directory|\.cdad/packets"
)
_SOURCE_FEATURE = re.compile(r"(?i)request|solicitud|feature|unidad|packet|paquete")
_SOURCE_ROLE = re.compile(
    r"(?i)request|solicitud|role|rol|substage|subfase|packet|paquete"
)
_CONDITION_MISMATCH = re.compile(
    r"(?i)match|coincid|mismatch|differ|pertenencia|membership|identidad|"
    r"identity|inconsisten|discord|ajen|no es el mismo|not the same|≠"
)
_CONDITION_UNREADABLE = re.compile(
    r"(?i)unreadable|ilegible|cannot read|invalid|malformed|parse|json|"
    r"corrupt|truncat|no puede leer|no se puede leer"
)
_PENDING_CAUSE = re.compile(
    r"(?i)(?:pending|pendiente)[^.]{0,200}(?:packet|paquete)|"
    r"(?:packet|paquete)[^.]{0,200}(?:pending|pendiente)|"
    r"active_packet|unresolved"
)

DRAFT_REL = "docs/planning-contract-draft.md"
DRAFT_BYTES = b"# Plan draft fixture (007-001)\n\nEstado: borrador del fixture\n"
DRAFT_SHA = hashlib.sha256(DRAFT_BYTES).hexdigest()

PLAN_BYTES = (
    b"# Epic plan fixture (007-001)\n\n"
    b"| Feature | Objective |\n|---|---|\n"
    + FEATURE_ID.encode()
    + b" | fixture |\n"
)

K1 = hashlib.sha256(b"007-k1").hexdigest()
K2 = hashlib.sha256(b"007-k2").hexdigest()


# ---------------------------------------------------------------- helpers


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_sha(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _member(mapping: object, key: str, label: str):
    """Acceso declarado: la falta de la clave es una ASERCIÓN de contrato."""
    assert isinstance(mapping, dict), (
        f"{label}: se esperaba un objeto JSON, hay {type(mapping).__name__}"
    )
    assert key in mapping, (
        f"{label}: falta la clave {key!r}; claves presentes: {sorted(mapping)}"
    )
    return mapping[key]


def _key(doc: dict, key: str):
    return _member(doc, key, "documento `status`")


def _home(base: Path) -> Path:
    home = base / "home"
    home.mkdir(parents=True, exist_ok=True)
    return home


def _env(home: Path) -> dict:
    env = dict(os.environ)
    env["HOME"] = str(home)  # NUNCA el HOME real
    return env


def _status(root: Path, home: Path, *extra: str) -> subprocess.CompletedProcess:
    assert CLI.is_file(), f"CLI del repo ausente: {CLI}"
    return subprocess.run(
        [sys.executable, str(CLI), "status", "--project-root", str(root), *extra],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=_env(home),
        stdin=subprocess.DEVNULL,
        timeout=CLI_TIMEOUT_S,
    )


def _document(proc: subprocess.CompletedProcess) -> dict:
    """El único documento JSON de la vista, o AssertionError de contrato.

    Nunca deja escapar JSONDecodeError: si la vista no emitió el documento,
    la aserción lo declara.
    """
    assert proc.returncode == 0, (
        "PC-01/PC-13: la vista `status` debe emitir la proyección (rc=0); "
        f"hoy rc={proc.returncode}; stderr={proc.stderr.strip()!r}"
    )
    assert proc.stdout.strip(), (
        "PC-13: la vista no emitió el documento por stdout; "
        f"stderr={proc.stderr.strip()!r}"
    )
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            "PC-13: stdout no es un ÚNICO documento JSON válido: "
            f"{proc.stdout[:200]!r}"
        ) from exc
    assert isinstance(doc, dict), (
        f"PC-13: el documento de la vista no es un objeto JSON: {doc!r}"
    )
    return doc


def _situation(doc: dict) -> str:
    assert "situation" in doc, (
        "PC-01: falta el campo raíz `situation` (siempre presente, §2.1); "
        f"claves del documento: {sorted(doc)}"
    )
    situation = doc["situation"]
    assert situation in SITUATION_VALUES, (
        f"PC-01: `situation` fuera del vocabulario de §2.1: {situation!r}"
    )
    return situation


def _next(doc: dict) -> dict:
    next_block = _key(doc, "next")
    assert isinstance(next_block, dict), (
        f"PC-11: `next` no es un objeto: {next_block!r}"
    )
    return next_block


def _operation(doc: dict) -> dict:
    """`next.operation` con sus cuatro campos obligatorios (§2.2)."""
    next_block = _next(doc)
    assert "operation" in next_block, (
        "PC-02: falta `next.operation` (los cuatro campos son obligatorios, "
        f"§2.2); `next` hoy: {next_block!r}"
    )
    op = next_block["operation"]
    assert isinstance(op, dict), (
        f"PC-02: `next.operation` no es un objeto: {op!r}"
    )
    missing = [k for k in OPERATION_KEYS if k not in op]
    assert not missing, (
        f"PC-02: faltan campos obligatorios de `next.operation`: {missing}; "
        f"hay {sorted(op)}"
    )
    assert isinstance(op["verb"], str) and op["verb"].strip(), (
        f"PC-02: `next.operation.verb` vacío: {op['verb']!r}"
    )
    assert op["script"] is None or (
        isinstance(op["script"], str) and op["script"].strip()
    ), f"PC-02: `next.operation.script` inválido: {op['script']!r}"
    assert isinstance(op["procedure"], str) and op["procedure"].strip(), (
        f"PC-02: `next.operation.procedure` vacío: {op['procedure']!r}"
    )
    assert isinstance(op["source"], str) and op["source"].strip(), (
        f"PC-02: `next.operation.source` vacío: {op['source']!r}"
    )
    return op


def _approval_reference(doc: dict) -> dict:
    """`authority.approval_reference` validada contra §2.3 (forma común)."""
    authority = _key(doc, "authority")
    assert isinstance(authority, dict), (
        f"PC-11: `authority` no es un objeto: {authority!r}"
    )
    assert "approval_reference" in authority, (
        "PC-11: falta `authority.approval_reference` (§2.3, hermano de "
        f"`authority.approval`); `authority` hoy: {sorted(authority)}"
    )
    ref = authority["approval_reference"]
    assert isinstance(ref, dict), (
        f"PC-11: `authority.approval_reference` no es un objeto: {ref!r}"
    )
    assert set(ref) == REFERENCE_KEYS, (
        "PC-11: `authority.approval_reference` no tiene exactamente los "
        f"campos obligatorios de §2.3: {sorted(ref)}"
    )
    assert ref["status"] in APPROVAL_STATUSES, (
        f"PC-11: `status` fuera del vocabulario de §2.3: {ref['status']!r}"
    )
    assert ref["object"] in APPROVAL_OBJECTS, (
        f"PC-11: `object` fuera del vocabulario de §2.3: {ref['object']!r}"
    )
    role = ref["role"]
    assert role is None or (isinstance(role, str) and role.strip()), (
        f"PC-11: `role` debe ser un rol no vacío o null: {role!r}"
    )
    record = ref["record"]
    if record is not None:
        assert isinstance(record, dict) and set(record) == RECORD_KEYS, (
            "PC-11: `record` no es null ni tiene los campos obligatorios de "
            f"§2.3: {record!r}"
        )
        assert record["path"] == STATE_FILE, (
            f"PC-11: `record.path` no apunta al estado: {record['path']!r}"
        )
        index = record["index"]
        assert isinstance(index, int) and not isinstance(index, bool) and index >= 0, (
            "PC-11: `record.index` debe ser un entero 0-based en el historial "
            f"que determina `object` (§2.3): {index!r}"
        )
        assert record["transition_key"] is None or isinstance(
            record["transition_key"], str
        ), f"PC-11: `record.transition_key` inválido: {record['transition_key']!r}"
        assert isinstance(record["approved_by"], str) and record["approved_by"].strip(), (
            f"PC-11: `record.approved_by` vacío: {record['approved_by']!r}"
        )
    contract = ref["contract"]
    if contract is not None:
        assert isinstance(contract, dict) and set(contract) == CONTRACT_KEYS, (
            "PC-11: `contract` no es null ni tiene los campos obligatorios de "
            f"§2.3: {contract!r}"
        )
        assert isinstance(contract["path"], str) and contract["path"].strip(), (
            f"PC-11: `contract.path` vacío: {contract['path']!r}"
        )
        assert _is_sha(contract["declared_sha256"]), (
            "PC-11: `contract.declared_sha256` no es un SHA-256: "
            f"{contract['declared_sha256']!r}"
        )
        observed = contract["observed_sha256"]
        assert observed is None or _is_sha(observed), (
            f"PC-11: `contract.observed_sha256` inválido: {observed!r}"
        )
    if ref["status"] == "vigente":
        assert ref["reason"] is None, (
            "PC-11: `reason` debe ser null para `vigente` (§2.3): "
            f"{ref['reason']!r}"
        )
    else:
        assert isinstance(ref["reason"], str) and ref["reason"].strip(), (
            "PC-11: `reason` debe explicar un resultado distinto de `vigente` "
            f"(§2.3): status={ref['status']!r} reason={ref['reason']!r}"
        )
    return ref


def _assert_no_history_token(
    proc: subprocess.CompletedProcess, label: str
) -> None:
    """PD-1 (§2.3): el localizador no emite el nombre del historial."""
    for token in ("stage_history", "epic_history"):
        assert token not in proc.stdout, (
            f"{label}/PD-1: la salida emite el token del historial {token!r}; "
            "el localizador debe ser `record.index`"
        )


_HISTORY_BY_OBJECT = {
    "feature-spec": "stage_history",
    "epic-plan": "epic_history",
}


def _resolve_record(document: dict, object_kind: str, record: dict):
    """Resuelve `record.index` en el historial real que determina `object`.

    Oráculo independiente: sea `object=feature-spec` (historial
    `stage_history`) o `object=epic-plan` (historial `epic_history`), el índice
    entero 0-based debe identificar el registro esperado en el orden real del
    historial del fixture (§2.3, «Localizadores y determinismo»).
    """
    history_key = _HISTORY_BY_OBJECT.get(object_kind)
    assert history_key is not None, (
        "PC-11: `record.index` sólo localiza registros de `feature-spec` o "
        f"`epic-plan`; object={object_kind!r}"
    )
    index = _member(record, "index", "record")
    assert isinstance(index, int) and not isinstance(index, bool) and index >= 0, (
        f"PC-11: `record.index` debe ser un entero 0-based: {index!r}"
    )
    history = _member(document, history_key, "estado del fixture")
    assert isinstance(history, list), (
        f"PC-11: `{history_key}` no es una lista en el estado: {history!r}"
    )
    assert index < len(history), (
        f"PC-11: `record.index`={index} fuera de rango en `{history_key}` "
        f"(historial de {len(history)} registros)"
    )
    return history[index]


def _assert_preserved(old: object, new: object) -> None:
    """Diagnósticos anteriores: mismo contenido y orden relativo (§2.4)."""
    assert isinstance(old, list) and isinstance(new, list), (
        f"PC-11/§2.4: `unknowns` debe ser lista; antes={old!r} ahora={new!r}"
    )
    index = 0
    for entry in new:
        if index < len(old) and entry == old[index]:
            index += 1
    assert index == len(old), (
        "PC-11/§2.4: se perdió o reordenó un diagnóstico anterior de "
        f"`unknowns`; antes={old!r} ahora={new!r}"
    )


def _assert_new_cause(unknowns: object, groups: list[list[re.Pattern]],
                      label: str) -> None:
    """Al menos una causa NUEVA identifica la fuente y la condición (aclaración 5)."""
    assert isinstance(unknowns, list), f"{label}: `unknowns` no es lista: {unknowns!r}"
    matches = [
        entry
        for entry in unknowns
        if all(any(pattern.search(entry) for pattern in group) for group in groups)
    ]
    assert matches, (
        f"{label}: ninguna entrada de `unknowns` identifica la fuente y la "
        f"condición del diagnóstico; grupos={[[p.pattern for p in g] for g in groups]}; "
        f"unknowns={unknowns!r}"
    )


def _strip_additions(doc: dict) -> dict:
    """Quita SOLO las tres adiciones declaradas por §2.1–§2.3 (PC-11)."""
    stripped = dict(doc)
    stripped.pop("situation", None)
    next_block = stripped.get("next")
    if isinstance(next_block, dict):
        next_block = dict(next_block)
        next_block.pop("operation", None)
        stripped["next"] = next_block
    authority = stripped.get("authority")
    if isinstance(authority, dict):
        authority = dict(authority)
        authority.pop("approval_reference", None)
        stripped["authority"] = authority
    return stripped


def _project(base: Path) -> tuple[Path, Path]:
    root = base / "proj"
    build_project(root)
    return root, _home(base)


def _prepare(
    root: Path,
    home: Path,
    *,
    role: str = "test-writer",
    substage: str = "red",
    objective: str = "007-001 fixture",
) -> subprocess.CompletedProcess:
    assert CLI.is_file(), f"CLI del repo ausente: {CLI}"
    proc = subprocess.run(
        [
            sys.executable,
            str(CLI),
            *prepare_args(root, role=role, substage=substage, objective=objective),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=_env(home),
        stdin=subprocess.DEVNULL,
        timeout=CLI_TIMEOUT_S,
    )
    assert proc.returncode == 0, (
        "fixture: `prepare` del proyecto sintético debe tener éxito; "
        f"rc={proc.returncode}; stderr={proc.stderr.strip()!r}"
    )
    return proc


def _active_packet(root: Path) -> dict:
    state = read_state(root)
    packet = _member(state, "active_packet", "state del fixture")
    assert isinstance(packet, dict), (
        f"fixture: `active_packet` no es un objeto: {packet!r}"
    )
    return packet


def _packet_id(root: Path) -> str:
    packet_id = _member(_active_packet(root), "id", "state.active_packet")
    assert isinstance(packet_id, str) and packet_id, (
        f"fixture: `active_packet.id` vacío: {packet_id!r}"
    )
    return packet_id


def _request_path(root: Path, packet_id: str) -> Path:
    return root / ".cdad" / "packets" / packet_id / "REQUEST.json"


def _mutate_request(root: Path, active_packet_id: str, **changes) -> dict:
    path = _request_path(root, active_packet_id)
    assert path.is_file(), f"fixture: falta {path}"
    request = json.loads(path.read_text(encoding="utf-8"))
    request.update(changes)
    path.write_text(json.dumps(request), encoding="utf-8")
    return request


def _add_pending_dir(
    root: Path, template_packet: str, new_packet: str, **overrides
) -> Path:
    """Copia un paquete de la MISMA ejecución sin recibo (trabajo pendiente)."""
    source = root / ".cdad" / "packets" / template_packet
    target = root / ".cdad" / "packets" / new_packet
    assert source.is_dir(), f"fixture: falta {source}"
    assert not target.exists(), f"fixture: {target} ya existe"
    shutil.copytree(source, target)
    request = json.loads((target / "REQUEST.json").read_text(encoding="utf-8"))
    request["packet_id"] = new_packet
    request.update(overrides)
    (target / "REQUEST.json").write_text(json.dumps(request), encoding="utf-8")
    return target


def _add_receipt(root: Path, execution_id: str, packet_id: str) -> None:
    receipt = root / ".cdad" / "runtime" / "results" / execution_id / packet_id
    receipt.mkdir(parents=True, exist_ok=True)
    (receipt / "receipt.json").write_text(
        json.dumps({"runtime": "opencode", "rc": 0}), encoding="utf-8"
    )


def _drop_active_packet(root: Path) -> None:
    state = read_state(root)
    state["active_packet"] = None
    write_state(root, state)


def _set_packet_status(root: Path, status: str) -> None:
    state = read_state(root)
    packet = _member(state, "active_packet", "state del fixture")
    assert isinstance(packet, dict), f"fixture: {packet!r}"
    packet["status"] = status
    write_state(root, state)


# ---------------------------------------------------------------- PC-01 cases


def _case_at_rest(base: Path) -> tuple[Path, Path]:
    """Sin ejecución activa, sin paquete y sin pendientes; estado legible."""
    return _project(base)


def _case_execution_active(base: Path) -> tuple[Path, Path]:
    """Ejecución activa sin paquete activo ni directorios pendientes."""
    root, home = _project(base)
    _prepare(root, home)
    _drop_active_packet(root)
    shutil.rmtree(root / ".cdad" / "packets")
    return root, home


def _case_prepared(base: Path) -> tuple[Path, Path]:
    """Paquete activo inequívoco en estado `prepared`."""
    root, home = _project(base)
    _prepare(root, home)
    return root, home


def _case_dispatched(base: Path) -> tuple[Path, Path]:
    """Paquete activo inequívoco en estado `dispatched`."""
    root, home = _case_prepared(base)
    _set_packet_status(root, "dispatched")
    return root, home


def _case_pending(base: Path) -> tuple[Path, Path]:
    """Sin `active_packet` y un directorio pendiente de la ejecución activa."""
    root, home = _case_prepared(base)
    _drop_active_packet(root)
    return root, home


def _case_diagnosis(base: Path) -> tuple[Path, Path]:
    """Configuración incompleta (sin política): la selección es `diagnosis`."""
    root, home = _project(base)
    (root / POLICY_FILE).unlink()
    return root, home


def _case_diagnosis_with_prepared(base: Path) -> tuple[Path, Path]:
    """Configuración incompleta CON paquete preparado: `diagnosis` precede."""
    root, home = _case_prepared(base)
    (root / POLICY_FILE).unlink()
    return root, home


def _case_state_corrupt(base: Path) -> tuple[Path, Path]:
    """Estado ilegible (JSON inválido): precedencia de ilegibilidad (§2.1)."""
    root, home = _project(base)
    (root / STATE_FILE).write_text("{not json", encoding="utf-8")
    return root, home


def _case_state_missing(base: Path) -> tuple[Path, Path]:
    """Estado ausente = no puede leerse: misma precedencia que ilegible."""
    root, home = _project(base)
    (root / STATE_FILE).unlink()
    return root, home


MATRIX_CASES = [
    pytest.param(
        _case_at_rest,
        dict(
            entry="next-unit",
            situation="at-rest",
            verb="open-unit",
            script=PACKET_SCRIPT,
            procedure="references/project-start.md",
            source="docs/.cdad-state.json:active_feature",
        ),
        id="at-rest",
    ),
    pytest.param(
        _case_execution_active,
        dict(
            entry="continuity-reconcile",
            situation="execution-active",
            verb="resume",
            script=CONTINUITY_SCRIPT,
            procedure="references/continuity.md",
            source="docs/.cdad-state.json:execution",
        ),
        id="execution-active",
    ),
    pytest.param(
        _case_prepared,
        dict(
            entry="continuity-reconcile",
            situation="packet-prepared",
            verb="validate-packet",
            script=PACKET_SCRIPT,
            procedure="references/orientation.md",
            source="docs/.cdad-state.json:active_packet.status",
        ),
        id="packet-prepared",
    ),
    pytest.param(
        _case_dispatched,
        dict(
            entry="continuity-reconcile",
            situation="packet-dispatched",
            verb="reconcile",
            script=CONTINUITY_SCRIPT,
            procedure="references/continuity.md",
            source="docs/.cdad-state.json:active_packet.status",
        ),
        id="packet-dispatched",
    ),
    pytest.param(
        _case_pending,
        dict(
            entry="continuity-reconcile",
            situation="pending-work-unresolved",
            verb="diagnose",
            script=None,
            procedure="references/project-execution.md",
            source="docs/.cdad-state.json:active_packet / .cdad/packets",
        ),
        id="pending-work-unresolved",
    ),
    pytest.param(
        _case_diagnosis,
        dict(
            entry="diagnosis",
            situation="diagnosis",
            verb="diagnose",
            script=None,
            procedure="references/project-start.md",
            source=None,  # §2.2: `next.source` existente
        ),
        id="diagnosis-config",
    ),
    pytest.param(
        _case_diagnosis_with_prepared,
        dict(
            entry="diagnosis",
            situation="diagnosis",
            verb="diagnose",
            script=None,
            procedure="references/project-start.md",
            source=None,
        ),
        id="diagnosis-precedes-prepared",
    ),
    pytest.param(
        _case_state_corrupt,
        dict(
            entry="next-unit",
            situation="diagnosis",
            verb="diagnose",
            script=None,
            procedure="references/project-start.md",
            source="docs/.cdad-state.json",
        ),
        id="state-unreadable",
    ),
    pytest.param(
        _case_state_missing,
        dict(
            entry="next-unit",
            situation="diagnosis",
            verb="diagnose",
            script=None,
            procedure="references/project-start.md",
            source="docs/.cdad-state.json",
        ),
        id="state-missing",
    ),
]


# ---------------------------------------------------------------- PC-01


@pytest.mark.parametrize("build,expected", MATRIX_CASES)
def test_situation_operation_matrix(tmp_path: Path, build, expected: dict) -> None:
    """PC-01/§2.1–§2.2: cada escenario produce EXACTAMENTE la situación y la
    operación de las tablas, respetando la precedencia (incluida la
    ilegibilidad del estado: `diagnosis` con `verb=diagnose`, `script=null`,
    `procedure=references/project-start.md` y `source=docs/.cdad-state.json`).
    """
    root, home = build(tmp_path)
    doc = _document(_status(root, home))

    entry = _key(doc, "entry")
    assert entry == expected["entry"], (
        f"PC-11/§2.1: `entry` cambió de su mapa existente para el escenario "
        f"{expected['situation']!r}: {entry!r} != {expected['entry']!r}"
    )
    situation = _situation(doc)
    assert situation == expected["situation"], (
        f"PC-01: situación incorrecta; esperada {expected['situation']!r}, "
        f"hoy {situation!r}"
    )

    op = _operation(doc)
    assert op["verb"] == expected["verb"], (
        f"PC-02: verbo incorrecto para {situation!r}: {op['verb']!r} != "
        f"{expected['verb']!r}"
    )
    assert op["script"] == expected["script"], (
        f"PC-02: script incorrecto para {situation!r}: {op['script']!r} != "
        f"{expected['script']!r}"
    )
    assert op["procedure"] == expected["procedure"], (
        f"PC-02: procedimiento incorrecto para {situation!r}: "
        f"{op['procedure']!r} != {expected['procedure']!r}"
    )

    if expected["source"] is None:
        existing = _member(_next(doc), "source", "next")
        assert isinstance(existing, str) and existing.strip(), (
            f"PC-02: `next.source` existente vacío en {situation!r}: {existing!r}"
        )
        assert op["source"] == existing, (
            "PC-02/§2.2: en diagnóstico de configuración `operation.source` es "
            f"el `next.source` existente ({existing!r}), no {op['source']!r}"
        )
    else:
        assert op["source"] == expected["source"], (
            f"PC-02/§2.2: `operation.source` incorrecto para {situation!r}: "
            f"{op['source']!r} != {expected['source']!r}"
        )

    route = _member(_next(doc), "route", "next")
    assert isinstance(route, str) and route.strip(), (
        f"PC-11: `next.route` vacío en {situation!r}: {route!r}"
    )


# ---------------------------------------------------------------- PC-02


def test_prepared_and_dispatched_operations(tmp_path: Path) -> None:
    """PC-02/§2.2: preparado → `validate-packet`; despachado → `reconcile`;
    ambos scripts y procedimientos existen bajo el directorio del skill y los
    verbos difieren (el primer paso no es una macro de despacho)."""
    root, home = _case_prepared(tmp_path)
    doc = _document(_status(root, home))
    assert _situation(doc) == "packet-prepared", (
        f"PC-02: el fixture preparado no proyecta packet-prepared: {doc.get('situation')!r}"
    )
    prepared = _operation(doc)
    assert prepared["verb"] == "validate-packet", (
        f"PC-02: preparado debe indicar validate-packet: {prepared['verb']!r}"
    )
    assert prepared["script"] == PACKET_SCRIPT, (
        f"PC-02: preparado debe ejecutarse con {PACKET_SCRIPT}: "
        f"{prepared['script']!r}"
    )
    assert prepared["procedure"] == "references/orientation.md", (
        f"PC-02: procedimiento de preparado incorrecto: {prepared['procedure']!r}"
    )

    _set_packet_status(root, "dispatched")
    doc = _document(_status(root, home))
    assert _situation(doc) == "packet-dispatched", (
        f"PC-02: el fixture despachado no proyecta packet-dispatched: {doc.get('situation')!r}"
    )
    dispatched = _operation(doc)
    assert dispatched["verb"] == "reconcile", (
        f"PC-02: despachado debe indicar reconcile: {dispatched['verb']!r}"
    )
    assert dispatched["script"] == CONTINUITY_SCRIPT, (
        f"PC-02: despachado debe ejecutarse con {CONTINUITY_SCRIPT}: "
        f"{dispatched['script']!r}"
    )
    assert dispatched["procedure"] == "references/continuity.md", (
        f"PC-02: procedimiento de despachado incorrecto: "
        f"{dispatched['procedure']!r}"
    )
    assert dispatched["verb"] != prepared["verb"], (
        "PC-02: preparado y despachado no pueden colapsar en el mismo verbo: "
        f"{prepared['verb']!r}"
    )

    for relative in (
        prepared["script"],
        prepared["procedure"],
        dispatched["script"],
        dispatched["procedure"],
    ):
        assert (SKILL_DIR / relative).is_file(), (
            f"PC-02: la referencia declarada no existe bajo el skill: {relative}"
        )


# ---------------------------------------------------------------- PC-03


def test_closed_execution_is_history(tmp_path: Path) -> None:
    """PC-03/§2.1: la ejecución histórica que queda en el estado tras cerrar
    una feature no produce `execution-active` (la vista queda `at-rest`) ni una
    aprobación vigente histórica: sin paquete activo aplicable, C1 la declara
    `desconocida` con `role`/`object`/`record` nulos — aunque el historial
    conserve la aprobación de la spec con su pin."""
    root, home = _case_prepared(tmp_path)
    packet_id = _packet_id(root)
    execution_id = _member(
        _member(read_state(root), "execution", "state del fixture"),
        "id",
        "state.execution",
    )
    assert isinstance(execution_id, str) and execution_id

    # Directorios históricos: el paquete activo (sin recibo) y uno recibido.
    _add_pending_dir(root, packet_id, "999-001-fixture-unit-test-writer-red-901")
    _add_receipt(root, execution_id, "999-001-fixture-unit-test-writer-red-901")

    state = read_state(root)
    state["epic_features"] = [{"id": FEATURE_ID, "status": "done"}]
    state["active_feature"] = None
    state["current_stage"] = "idle"
    state["tdd_substage"] = None
    state["active_packet"] = None
    write_state(root, state)

    doc = _document(_status(root, home))

    assert _situation(doc) == "at-rest", (
        "PC-03: con la feature cerrada la ejecución del bloque `execution` es "
        f"historia: se esperaba `at-rest`, no {doc.get('situation')!r}"
    )
    op = _operation(doc)
    assert op["verb"] == "open-unit", (
        f"PC-03: en reposo el primer paso es open-unit: {op['verb']!r}"
    )
    assert _key(doc, "entry") == "next-unit", (
        f"PC-03: en reposo la entrada debe ser next-unit: {_key(doc, 'entry')!r}"
    )

    ref = _approval_reference(doc)
    assert ref["status"] == "desconocida", (
        "PC-03/§2.3 C1: sin paquete activo aplicable no se afirma una "
        f"aprobación vigente histórica: {ref['status']!r}"
    )
    assert ref["role"] is None and ref["object"] is None, (
        f"PC-03/§2.3 C1: role/object deben ser null: {ref['role']!r}/{ref['object']!r}"
    )
    assert ref["record"] is None, (
        f"PC-03/§2.3 C1: `record` debe ser null: {ref['record']!r}"
    )


# ---------------------------------------------------------------- PC-04 cases


def _p_foreign_execution(base: Path) -> tuple[Path, Path]:
    root, home = _case_prepared(base)
    _mutate_request(root, _packet_id(root), execution_id="exec-999-999-foreign")
    return root, home


def _p_packet_identity(base: Path) -> tuple[Path, Path]:
    root, home = _case_prepared(base)
    _mutate_request(root, _packet_id(root), packet_id="999-999-foreign-packet")
    return root, home


def _p_foreign_feature(base: Path) -> tuple[Path, Path]:
    root, home = _case_prepared(base)
    _mutate_request(root, _packet_id(root), feature_id="999-999-foreign-feature")
    return root, home


def _p_role_substage(base: Path) -> tuple[Path, Path]:
    root, home = _case_prepared(base)
    _mutate_request(root, _packet_id(root), role="reviewer")
    return root, home


def _p_request_unreadable(base: Path) -> tuple[Path, Path]:
    root, home = _case_prepared(base)
    _request_path(root, _packet_id(root)).write_text("{broken", encoding="utf-8")
    return root, home


def _p_no_active_one(base: Path) -> tuple[Path, Path]:
    return _case_pending(base)


def _p_no_active_many(base: Path) -> tuple[Path, Path]:
    root, home = _case_prepared(base)
    template = _packet_id(root)
    for index in range(2):
        _add_pending_dir(
            root, template, f"999-001-fixture-unit-test-writer-red-90{index}"
        )
    _drop_active_packet(root)
    return root, home


def _p_explicit_with_pending(base: Path) -> tuple[Path, Path]:
    root, home = _case_prepared(base)
    template = _packet_id(root)
    for index in range(2):
        _add_pending_dir(
            root, template, f"999-001-fixture-unit-test-writer-red-91{index}"
        )
    return root, home


PENDING_CASES = [
    pytest.param(
        _p_foreign_execution,
        [[_SOURCE_EXECUTION], [_CONDITION_MISMATCH]],
        id="foreign-execution-id",
    ),
    pytest.param(
        _p_packet_identity,
        [[_SOURCE_PACKET], [_CONDITION_MISMATCH]],
        id="packet-identity-mismatch",
    ),
    pytest.param(
        _p_foreign_feature,
        [[_SOURCE_FEATURE], [_CONDITION_MISMATCH]],
        id="foreign-feature-id",
    ),
    pytest.param(
        _p_role_substage,
        [[_SOURCE_ROLE], [_CONDITION_MISMATCH]],
        id="role-substage-mismatch",
    ),
    pytest.param(
        _p_request_unreadable,
        [[_SOURCE_REQUEST], [_CONDITION_UNREADABLE]],
        id="request-unreadable",
    ),
    pytest.param(_p_no_active_one, [[_PENDING_CAUSE]], id="no-active-packet-one"),
    pytest.param(_p_no_active_many, [[_PENDING_CAUSE]], id="no-active-packet-many"),
]


# ---------------------------------------------------------------- PC-04


@pytest.mark.parametrize("build,cause_groups", PENDING_CASES)
def test_unresolved_pending_work_is_not_dispatchable(
    tmp_path: Path, build, cause_groups: list[list[re.Pattern]]
) -> None:
    """PC-04/§2.1: toda pertenencia inconsistente o pendiente sin paquete
    inequívoco produce `pending-work-unresolved`, diagnóstico sin script
    ejecutable (`verb=diagnose`, `script=null`), con el `source` exacto de
    §2.2 y una causa nueva en `unknowns` que identifica fuente y condición
    (aclaración 5), conservando los diagnósticos anteriores."""
    control_root, control_home = _case_prepared(tmp_path / "control")
    control = _document(_status(control_root, control_home))
    control_unknowns = _key(control, "unknowns")
    assert isinstance(control_unknowns, list)

    root, home = build(tmp_path / "case")
    doc = _document(_status(root, home))

    assert _situation(doc) == "pending-work-unresolved", (
        "PC-04: la pertenencia inconsistente o el pendiente sin paquete "
        f"inequívoco debe producir pending-work-unresolved: {doc.get('situation')!r}"
    )
    op = _operation(doc)
    assert op["verb"] == "diagnose", (
        f"PC-04: el caso pendiente no habilita una operación ejecutable: {op['verb']!r}"
    )
    assert op["script"] is None, (
        f"PC-04: `diagnose` no tiene script ejecutable: {op['script']!r}"
    )
    assert op["procedure"] == "references/project-execution.md", (
        f"PC-04: procedimiento esperado references/project-execution.md: "
        f"{op['procedure']!r}"
    )
    assert op["source"] == "docs/.cdad-state.json:active_packet / .cdad/packets", (
        "PC-04/§2.2: `source` exacto de pending-work-unresolved incorrecto "
        f"(aclaración 4): {op['source']!r}"
    )

    unknowns = _key(doc, "unknowns")
    _assert_preserved(control_unknowns, unknowns)
    _assert_new_cause(unknowns, cause_groups, "PC-04")


def test_explicit_valid_packet_is_not_ambiguous_with_pending_dirs(
    tmp_path: Path,
) -> None:
    """PC-04/§2.1: un `active_packet` explícito que cumple los bindings NO se
    vuelve ambiguo por otros directorios pendientes: sigue
    `packet-prepared` → `validate-packet`, y los directorios ajenos a la
    selección no agregan causas a `unknowns` (no son una inconsistencia)."""
    control_root, control_home = _case_prepared(tmp_path / "control")
    control = _document(_status(control_root, control_home))

    root, home = _p_explicit_with_pending(tmp_path / "case")
    doc = _document(_status(root, home))

    assert _situation(doc) == "packet-prepared", (
        "PC-04: con un paquete explícito válido, otros directorios pendientes "
        f"no anulan su evidencia: {doc.get('situation')!r}"
    )
    op = _operation(doc)
    assert op["verb"] == "validate-packet", (
        f"PC-04: el paquete explícito válido sigue siendo validable: {op['verb']!r}"
    )
    assert op["script"] == PACKET_SCRIPT, (
        f"PC-04: script esperado {PACKET_SCRIPT}: {op['script']!r}"
    )
    assert _key(doc, "unknowns") == _key(control, "unknowns"), (
        "PC-04/§2.4: los directorios pendientes que no seleccionan no agregan "
        "causas a `unknowns` (sólo la pertenencia inconsistente o el request "
        f"ilegible las agregan); control={_key(control, 'unknowns')!r}; "
        f"con pendientes={_key(doc, 'unknowns')!r}"
    )


# ---------------------------------------------------------------- PC-05


def _architect_project(base: Path) -> tuple[Path, Path, str]:
    root, home = _project(base)
    state = read_state(root)
    epic = _member(state, "active_epic", "state del fixture")
    assert isinstance(epic, str) and epic, f"fixture: active_epic vacío: {epic!r}"
    plan_rel = f"docs/epics/{epic}/plan.md"
    (root / plan_rel).parent.mkdir(parents=True, exist_ok=True)
    (root / plan_rel).write_bytes(PLAN_BYTES)
    state["epic_history"] = [
        {
            "epic": epic,
            "stage": "epic-plan",
            "approved_by": "orquestador-fixture",
            "approved_at": "2026-10-20T00:00:00Z",
            "plan_path": plan_rel,
            "note": "mandato del fixture (sin pin del plan)",
        }
    ]
    write_state(root, state)
    _prepare(
        root,
        home,
        role="architect",
        substage="discovery",
        objective="007-001 architect fixture",
    )
    return root, home, plan_rel


def test_architect_approval_uses_epic_mandate(tmp_path: Path) -> None:
    """PC-05/§2.3 A2–A4: para architect el objeto es `epic-plan` y el registro
    es exactamente el mandato que selecciona `_approved_epic_plan_entry` en
    `epic_history` — con `record.index` 0-based resoluble y SIN exigir pin del
    plan (A4 → vigente; A3 → contrato cambiado conservando el mandato; A2 →
    ausente con fuentes legibles)."""
    root, home, plan_rel = _architect_project(tmp_path)

    proc = _status(root, home)
    _assert_no_history_token(proc, "PC-05")
    doc = _document(proc)
    ref = _approval_reference(doc)
    assert ref["role"] == "architect", (
        f"PC-05: el rol del request es architect: {ref['role']!r}"
    )
    assert ref["object"] == "epic-plan", (
        f"PC-05: para architect el objeto es epic-plan: {ref['object']!r}"
    )
    assert ref["status"] == "vigente", (
        "PC-05/A4: con mandato y bytes coincidentes la referencia es vigente "
        f"(el pin del plan NO se exige): {ref['status']!r}"
    )
    assert ref["reason"] is None, f"PC-05: vigente no lleva reason: {ref['reason']!r}"

    state = read_state(root)
    mandate = _member(state, "epic_history", "state del fixture")[0]
    record = ref["record"]
    assert record is not None, "PC-05: A4 conserva el mandato seleccionado"
    assert record["index"] == 0, (
        f"PC-05: índice 0-based del mandato incorrecto: {record['index']!r}"
    )
    resolved = _resolve_record(state, "epic-plan", record)
    assert isinstance(resolved, dict), (
        "PC-05: `record.index` no resuelve a un objeto del historial"
    )
    assert resolved.get("stage") == "epic-plan", (
        f"PC-05: el registro seleccionado no es el mandato: {resolved!r}"
    )
    assert resolved.get("approved_by") == record["approved_by"] == mandate["approved_by"]
    assert record["transition_key"] == mandate.get("transition_key"), (
        "PC-05: `transition_key` debe ser el del mandato (null si no lo tiene): "
        f"{record['transition_key']!r}"
    )

    contract = ref["contract"]
    assert contract is not None, "PC-05: se declara el contrato del request"
    assert contract["path"] == plan_rel, (
        f"PC-05: contract.path es el del request: {contract['path']!r}"
    )
    assert contract["declared_sha256"] == _sha(PLAN_BYTES), (
        f"PC-05: declared_sha256 debe ser el del request: {contract['declared_sha256']!r}"
    )
    assert contract["observed_sha256"] == _sha(PLAN_BYTES), (
        f"PC-05/A4: observed_sha256 debe coincidir: {contract['observed_sha256']!r}"
    )

    # A3: los bytes del contrato del request cambian → contrato cambiado,
    # conservando el mandato (la discrepancia de pin del PLAN no aplica).
    (root / plan_rel).write_bytes(PLAN_BYTES + b"\n<!-- cambio posterior -->\n")
    changed = _approval_reference(_document(_status(root, home)))
    assert changed["status"] == "contrato cambiado", (
        f"PC-05/A3: bytes discrepan del digest declarado: {changed['status']!r}"
    )
    assert changed["record"] == record, (
        "PC-05/A3: la discrepancia conserva el mandato seleccionado: "
        f"{changed['record']!r} != {record!r}"
    )
    assert changed["status"] != "sustituida", (
        "PC-05: el resultado `sustituida` no se aplica al mandato del epic"
    )
    assert changed["contract"]["observed_sha256"] != changed["contract"][
        "declared_sha256"
    ], "PC-05/A3: observed_sha256 debe reflejar los bytes actuales"

    # A2: fuentes legibles, sin mandato → ausente (aunque los bytes sigan
    # contradiciendo el digest declarado).
    state = read_state(root)
    state["epic_history"] = []
    write_state(root, state)
    absent = _approval_reference(_document(_status(root, home)))
    assert absent["status"] == "ausente", (
        "PC-05/A2: con fuentes legibles y sin mandato el resultado es ausente: "
        f"{absent['status']!r}"
    )
    assert absent["record"] is None, (
        f"PC-05/A2: ausente no inventa registro: {absent['record']!r}"
    )
    assert absent["reason"], "PC-05/A2: ausente explica su causa"


# ---------------------------------------------------------------- PC-06


def _spec_entry(
    *,
    contract_path: str = CONTRACT_FILE,
    contract_sha256: str = DECLARED_SPEC_SHA,
    transition_key: str | None = None,
    approved_by: str = "Pablo",
    **extra,
) -> dict:
    entry = {
        "feature": FEATURE_ID,
        "stage": "specification",
        "approved_by": approved_by,
        "approved_at": "2026-10-20T00:00:00Z",
        "contract_path": contract_path,
        "contract_sha256": contract_sha256,
    }
    if transition_key is not None:
        entry["transition_key"] = transition_key
    entry.update(extra)
    return entry


def _history_entry(**extra) -> dict:
    entry = {
        "feature": FEATURE_ID,
        "stage": "discovery",
        "approved_by": "Pablo",
        "approved_at": "2026-10-19T00:00:00Z",
        "note": "entrada histórica del fixture (no es registro de aprobación)",
    }
    entry.update(extra)
    return entry


def _spec_case(
    base: Path,
    *,
    history: list[dict],
    contract_bytes: bytes | None = None,
    delete_contract: bool = False,
) -> tuple[Path, Path]:
    root, home = _case_prepared(base)
    state = read_state(root)
    state["stage_history"] = list(history)
    write_state(root, state)
    if delete_contract:
        (root / CONTRACT_FILE).unlink()
    elif contract_bytes is not None:
        (root / CONTRACT_FILE).write_bytes(contract_bytes)
    return root, home


CHANGED_BYTES = CONTRACT_BYTES + b"\n<!-- bytes cambiados despues del pin -->\n"

SPEC_CASES = [
    pytest.param(
        dict(history=[_spec_entry()], delete_contract=True),
        "desconocida",
        "any-valid",
        None,
        id="s1-contract-bytes-unreadable",
    ),
    pytest.param(
        dict(history=[_history_entry()], contract_bytes=CHANGED_BYTES),
        "ausente",
        None,
        None,
        id="s2-no-records-bytes-changed",
    ),
    pytest.param(
        dict(
            history=[
                _spec_entry(transition_key=K1),
                _history_entry(stage="tdd", supersedes=K1),
            ],
            contract_bytes=CHANGED_BYTES,
        ),
        "sustituida",
        0,
        "superseded",
        id="s3-all-superseded-bytes-changed",
    ),
    pytest.param(
        dict(history=[_spec_entry(contract_path="docs/specs/999-999-other/spec.md")]),
        "contrato cambiado",
        0,
        "non-pin",
        id="s4-no-pin-match-foreign-path",
    ),
    pytest.param(
        dict(history=[_spec_entry()], contract_bytes=CHANGED_BYTES),
        "contrato cambiado",
        0,
        "pin-matching",
        id="s5-bytes-changed-pin-matches",
    ),
    pytest.param(
        dict(history=[_history_entry(), _spec_entry()]),
        "vigente",
        1,
        "pin-matching",
        id="s6-vigente-keyless-record",
    ),
    pytest.param(
        dict(history=[_spec_entry(transition_key=K1), _spec_entry(transition_key=K2)]),
        "vigente",
        0,
        "pin-matching",
        id="s6-multiple-records-first-selected",
    ),
]


# ---------------------------------------------------------------- PC-06


@pytest.mark.parametrize("build,expected_status,expected_index,record_kind", SPEC_CASES)
def test_spec_approval_status_matrix(
    tmp_path: Path,
    build: dict,
    expected_status: str,
    expected_index: int | str | None,
    record_kind: str | None,
) -> None:
    """PC-06/§2.3 S1–S6: cada fixture produce EXACTAMENTE un resultado
    normativo de la tabla ordenada (incluidas las combinaciones bytes
    cambiados + sin registros y bytes cambiados + todos sustituidos) y
    `record.index` (0-based) apunta al registro seleccionado en el historial
    real que determina `object`."""
    root, home = _spec_case(tmp_path, **build)

    state = read_state(root)
    packet = _member(state, "active_packet", "state del fixture")
    assert _member(packet, "status", "state.active_packet") == "prepared", (
        "fixture: el paquete activo debe seguir preparado"
    )

    proc = _status(root, home)
    _assert_no_history_token(proc, "PC-06")
    doc = _document(proc)
    ref = _approval_reference(doc)
    assert ref["object"] == "feature-spec", (
        f"PC-06: objeto esperado feature-spec: {ref['object']!r}"
    )
    assert ref["role"] == "test-writer", (
        f"PC-06: rol tomado del request: {ref['role']!r}"
    )
    assert ref["status"] == expected_status, (
        f"PC-06: resultado normativo incorrecto; esperado {expected_status!r}, "
        f"hoy {ref['status']!r} (reason={ref['reason']!r})"
    )

    contract = ref["contract"]
    assert contract is not None, (
        "PC-06: la declaración del contrato se conoce y se emite"
    )
    assert contract["path"] == CONTRACT_FILE, (
        f"PC-06: contract.path del request: {contract['path']!r}"
    )
    assert contract["declared_sha256"] == DECLARED_SPEC_SHA, (
        f"PC-06: declared_sha256 del request: {contract['declared_sha256']!r}"
    )
    contract_file = root / CONTRACT_FILE
    observed = _sha(contract_file.read_bytes()) if contract_file.is_file() else None
    assert contract["observed_sha256"] == observed, (
        "PC-06/§2.3: `observed_sha256` debe ser el SHA-256 de los bytes "
        f"actuales (o null si no pueden leerse): {contract['observed_sha256']!r} "
        f"!= {observed!r}"
    )

    record = ref["record"]
    if expected_index is None:
        assert record is None, (
            f"PC-06: este resultado no conserva registro: {record!r}"
        )
        return
    assert record is not None, "PC-06: el resultado selecciona un registro"
    if expected_index != "any-valid":
        assert record["index"] == expected_index, (
            f"PC-06: índice incorrecto; esperado {expected_index!r}, "
            f"hoy {record['index']!r}"
        )
    resolved = _resolve_record(state, ref["object"], record)
    assert isinstance(resolved, dict), (
        f"PC-06: `record.index` no resuelve a un objeto: {resolved!r}"
    )
    assert resolved.get("stage") == "specification", (
        f"PC-06: el registro seleccionado no es una aprobación: {resolved!r}"
    )
    assert resolved.get("approved_by") == record["approved_by"], (
        "PC-06: `record.approved_by` debe ser el del registro seleccionado: "
        f"{record['approved_by']!r} != {resolved.get('approved_by')!r}"
    )
    if record_kind == "pin-matching":
        assert resolved.get("contract_path") == CONTRACT_FILE, (
            f"PC-06: pin coincidente exige la ruta declarada: {resolved!r}"
        )
        assert resolved.get("contract_sha256") == DECLARED_SPEC_SHA, (
            f"PC-06: pin coincidente exige el digest declarado: {resolved!r}"
        )
    elif record_kind == "non-pin":
        assert (
            resolved.get("contract_path") != CONTRACT_FILE
            or resolved.get("contract_sha256") != DECLARED_SPEC_SHA
        ), f"PC-06: S4 selecciona un registro SIN pin coincidente: {resolved!r}"
    elif record_kind == "superseded":
        assert resolved.get("transition_key") == K1, (
            "PC-06/S3: el registro es la aprobación sustituida (primera del "
            f"historial real): {resolved!r}"
        )


# ---------------------------------------------------------------- PC-07


def test_approval_checks_path_and_current_bytes(tmp_path: Path) -> None:
    """PC-07/§2.3: un hash coincidente con ruta ajena y un contrato cuyos
    bytes cambiaron NUNCA producen `vigente`; la ausencia y la sustitución
    conservan su precedencia ante bytes cambiados (S2/S3 antes que S4/S5)."""
    # (a) Mismo digest, ruta ajena: el pin exige ruta Y digest.
    root, home = _spec_case(
        tmp_path / "foreign-path",
        history=[
            _spec_entry(contract_path="docs/specs/999-999-other/spec.md")
        ],
    )
    ref = _approval_reference(_document(_status(root, home)))
    assert ref["status"] != "vigente", (
        "PC-07: un hash coincidente con ruta ajena no puede producir vigente: "
        f"{ref['status']!r}"
    )
    assert ref["status"] == "contrato cambiado", (
        f"PC-07/S4: sin pin coincidente el resultado es contrato cambiado: "
        f"{ref['status']!r}"
    )

    # (b) Pin coincidente pero bytes actuales cambiados.
    root, home = _spec_case(
        tmp_path / "changed-bytes",
        history=[_spec_entry()],
        contract_bytes=CHANGED_BYTES,
    )
    ref = _approval_reference(_document(_status(root, home)))
    assert ref["status"] != "vigente", (
        "PC-07: disponer de un registro no prueba que los bytes actuales "
        f"estén aprobados: {ref['status']!r}"
    )
    assert ref["status"] == "contrato cambiado", (
        f"PC-07/S5: bytes cambiados con pin coincidente: {ref['status']!r}"
    )

    # (c) Ausencia y sustitución preceden a la discrepancia de bytes.
    root, home = _spec_case(
        tmp_path / "absent",
        history=[_history_entry()],
        contract_bytes=CHANGED_BYTES,
    )
    ref = _approval_reference(_document(_status(root, home)))
    assert ref["status"] == "ausente", (
        "PC-07/S2: sin registros el resultado es ausente aunque los bytes "
        f"contradigan el digest declarado: {ref['status']!r}"
    )

    root, home = _spec_case(
        tmp_path / "superseded",
        history=[
            _spec_entry(transition_key=K1),
            _history_entry(stage="tdd", supersedes=K1),
        ],
        contract_bytes=CHANGED_BYTES,
    )
    ref = _approval_reference(_document(_status(root, home)))
    assert ref["status"] == "sustituida", (
        "PC-07/S3: con todos los registros sustituidos el resultado es "
        f"sustituida aunque los bytes hayan cambiado: {ref['status']!r}"
    )
    assert ref["record"] is not None and ref["record"]["index"] == 0, (
        "PC-07/S3: se conserva el primer registro sustituido: "
        f"{ref['record']!r}"
    )


# ---------------------------------------------------------------- PC-08


def _draft_case(base: Path, *, write_draft: bool) -> tuple[Path, Path]:
    root, home = _case_prepared(base)
    packet_id = _packet_id(root)
    state = read_state(root)
    packet = _member(state, "active_packet", "state del fixture")
    assert isinstance(packet, dict)
    packet["role"] = "reviewer"
    packet["substage"] = "plan-review"
    packet["contract_kind"] = "draft-plan"
    packet["contract_sha256"] = DRAFT_SHA
    write_state(root, state)
    request = _mutate_request(
        root,
        packet_id,
        role="reviewer",
        substage="plan-review",
        contract={
            "kind": "draft-plan",
            "path": DRAFT_REL,
            "sha256": DRAFT_SHA,
            "commit": None,
            "plan_version": "draft-001",
        },
    )
    assert request["contract"]["kind"] == "draft-plan"
    if write_draft:
        (root / DRAFT_REL).parent.mkdir(parents=True, exist_ok=True)
        (root / DRAFT_REL).write_bytes(DRAFT_BYTES)
    return root, home


def test_draft_plan_requires_no_approval(tmp_path: Path) -> None:
    """PC-08/§2.3 D1: `draft-plan` declara `no requerida` y no inventa
    registro; la exención no exige comprobar los bytes del borrador (también
    con el borrador ilegible) y el `observed_sha256` se emite como null
    explícito, nunca omitido (aclaración 3)."""
    # Borrador legible: la aprobación de spec del fixture NO se usa.
    root, home = _draft_case(tmp_path / "readable", write_draft=True)
    ref = _approval_reference(_document(_status(root, home)))
    assert ref["object"] == "draft-plan", (
        f"PC-08/D1: objeto draft-plan: {ref['object']!r}"
    )
    assert ref["status"] == "no requerida", (
        f"PC-08/D1: un borrador no requiere aprobación: {ref['status']!r}"
    )
    assert ref["record"] is None, (
        f"PC-08/D1: no se busca registro de aprobación: {ref['record']!r}"
    )
    if ref["contract"] is not None:
        assert ref["contract"]["path"] == DRAFT_REL, (
            f"PC-08: contract.path del request: {ref['contract']['path']!r}"
        )
        assert ref["contract"]["declared_sha256"] == DRAFT_SHA
        assert "observed_sha256" in ref["contract"], (
            "PC-08/aclaración 3: `observed_sha256` nunca se omite"
        )

    # Borrador ilegible: la exención se establece sin comprobar bytes y el
    # contrato conserva la declaración con observed_sha256 = null explícito.
    root, home = _draft_case(tmp_path / "unreadable", write_draft=False)
    ref = _approval_reference(_document(_status(root, home)))
    assert ref["status"] == "no requerida", (
        "PC-08/D1: la ilegibilidad del borrador no transforma el resultado en "
        f"ausente ni contrato cambiado: {ref['status']!r}"
    )
    contract = ref["contract"]
    assert contract is not None, (
        "PC-08/§2.3: se conoce la declaración del borrador y se emite"
    )
    assert contract["path"] == DRAFT_REL
    assert contract["declared_sha256"] == DRAFT_SHA
    assert contract["observed_sha256"] is None, (
        "PC-08/aclaración 3: `observed_sha256` es null explícito cuando no se "
        f"comprueban los bytes: {contract['observed_sha256']!r}"
    )


# ---------------------------------------------------------------- PC-09


def _u_no_active_packet(base: Path) -> tuple[Path, Path]:
    return _project(base)


def _u_request_unreadable(base: Path) -> tuple[Path, Path]:
    root, home = _case_prepared(base)
    _request_path(root, _packet_id(root)).write_text("{broken", encoding="utf-8")
    return root, home


def _u_contract_unreadable(base: Path) -> tuple[Path, Path]:
    return _spec_case(base, history=[_spec_entry()], delete_contract=True)


def _u_no_record(base: Path) -> tuple[Path, Path]:
    return _spec_case(base, history=[_history_entry()])


UNKNOWN_ABSENT_CASES = [
    pytest.param(_u_no_active_packet, "desconocida", "c1", id="c1-no-active-packet"),
    pytest.param(
        _u_request_unreadable, "desconocida", "c2", id="c2-request-unreadable"
    ),
    pytest.param(
        _u_contract_unreadable, "desconocida", "s1", id="s1-contract-bytes-unreadable"
    ),
    pytest.param(_u_no_record, "ausente", "s2", id="s2-no-approval-record"),
]


# ---------------------------------------------------------------- PC-09


@pytest.mark.parametrize("build,expected_status,reason_kind", UNKNOWN_ABSENT_CASES)
def test_approval_unknown_vs_absent(
    tmp_path: Path, build, expected_status: str, reason_kind: str
) -> None:
    """PC-09/§2.3 C1/C2/S1/S2: request o contrato ilegible, ausencia de
    paquete y falta de registro se distinguen conforme a las tablas
    ordenadas: desconocida NUNCA equivale a ausente y la ilegibilidad de las
    fuentes precede al juicio de aprobación."""
    root, home = build(tmp_path)
    doc = _document(_status(root, home))
    ref = _approval_reference(doc)

    assert ref["status"] == expected_status, (
        f"PC-09/§2.3: resultado incorrecto para {reason_kind!r}; esperado "
        f"{expected_status!r}, hoy {ref['status']!r} (reason={ref['reason']!r})"
    )
    assert ref["status"] != "vigente", (
        f"PC-09: sin evidencia legible no se afirma vigencia: {ref['status']!r}"
    )
    assert ref["reason"], f"PC-09: el resultado {expected_status!r} explica su causa"

    if reason_kind == "c1":
        assert ref["role"] is None and ref["object"] is None, (
            f"PC-09/C1: role/object null: {ref['role']!r}/{ref['object']!r}"
        )
        assert ref["record"] is None, f"PC-09/C1: record null: {ref['record']!r}"
        assert ref["contract"] is None, (
            f"PC-09/C1: no se inventa la declaración del contrato: {ref['contract']!r}"
        )
    elif reason_kind == "c2":
        assert ref["role"] is None and ref["object"] is None, (
            "PC-09/C2: el request ilegible no permite inferir rol ni objeto: "
            f"{ref['role']!r}/{ref['object']!r}"
        )
        assert ref["record"] is None, f"PC-09/C2: record null: {ref['record']!r}"
    elif reason_kind == "s1":
        assert ref["role"] == "test-writer", (
            f"PC-09/S1: el rol sigue siendo el del request: {ref['role']!r}"
        )
        assert ref["object"] == "feature-spec", (
            f"PC-09/S1: el objeto sigue siendo feature-spec: {ref['object']!r}"
        )
        contract = ref["contract"]
        assert contract is not None and contract["observed_sha256"] is None, (
            "PC-09/S1: los bytes ilegibles dejan observed_sha256 null: "
            f"{ref['contract']!r}"
        )
        if ref["record"] is not None:
            _resolve_record(read_state(root), ref["object"], ref["record"])
    elif reason_kind == "s2":
        assert ref["role"] == "test-writer"
        assert ref["object"] == "feature-spec"
        assert ref["record"] is None, (
            f"PC-09/S2: ausente no inventa registro: {ref['record']!r}"
        )


# ---------------------------------------------------------------- PC-10


def test_approval_selection_and_supersession(tmp_path: Path) -> None:
    """PC-10/§2.3: la selección entre varios registros y sustituciones es
    determinista y coherente con los selectores de autorización existentes:
    un registro sustituido nunca se selecciona aunque su pin coincida, el
    primero del historial real gana entre iguales y repetir la vista devuelve
    la misma referencia."""
    # Una aprobación vigente sustituida por otra: gana la segunda (no la
    # primera, cuyo pin también coincide con los bytes actuales).
    root, home = _spec_case(
        tmp_path / "supersedes",
        history=[
            _spec_entry(transition_key=K1),
            _spec_entry(transition_key=K2, supersedes=K1),
        ],
    )
    first = _approval_reference(_document(_status(root, home)))
    assert first["status"] == "vigente", (
        f"PC-10: la aprobación no sustituida está vigente: {first['status']!r}"
    )
    record = first["record"]
    assert record is not None and record["index"] == 1, (
        "PC-10: se selecciona la aprobación NO sustituida (índice 1), no la "
        f"primera: {record!r}"
    )
    state = read_state(root)
    resolved = _resolve_record(state, first["object"], record)
    assert resolved.get("transition_key") == K2, (
        f"PC-10: el registro seleccionado debe ser el de clave K2: {resolved!r}"
    )
    history = _member(state, "stage_history", "state del fixture")
    superseded_keys = {
        entry.get("supersedes")
        for entry in history
        if isinstance(entry, dict) and entry.get("supersedes")
    }
    assert resolved.get("transition_key") not in superseded_keys, (
        "PC-10: nunca se selecciona una aprobación sustituida: "
        f"{resolved!r} (sustituidas: {superseded_keys})"
    )
    assert resolved.get("approved_by") == record["approved_by"]
    assert resolved.get("contract_path") == CONTRACT_FILE
    assert resolved.get("contract_sha256") == DECLARED_SPEC_SHA

    again = _approval_reference(_document(_status(root, home)))
    assert again == first, (
        "PC-10: la selección debe ser determinista (misma entrada, misma "
        f"referencia): {again!r} != {first!r}"
    )

    # Todos los registros sustituidos: gana el PRIMERO del historial real.
    root, home = _spec_case(
        tmp_path / "all-superseded",
        history=[
            _spec_entry(transition_key=K1),
            _spec_entry(transition_key=K2),
            _history_entry(stage="tdd", supersedes=K1),
            _history_entry(stage="tdd", supersedes=K2),
        ],
    )
    ref = _approval_reference(_document(_status(root, home)))
    assert ref["status"] == "sustituida", (
        f"PC-10: todos sustituidos → sustituida: {ref['status']!r}"
    )
    assert ref["record"] is not None and ref["record"]["index"] == 0, (
        "PC-10: `sustituida` conserva el PRIMER registro sustituido: "
        f"{ref['record']!r}"
    )
    assert _resolve_record(read_state(root), ref["object"], ref["record"]).get(
        "transition_key"
    ) == K1, "PC-10: el primer registro sustituido es el de clave K1"


# ---------------------------------------------------------------- PC-11


def test_status_is_additive(tmp_path: Path) -> None:
    """PC-11 grupo 1/§2.1–§2.4: en un fixture sin las condiciones que añaden
    diagnósticos, la proyección conserva TODOS los campos y valores
    anteriores (`entry`, `next.route` con su acción natural y su rama
    condicional, `next.source`, `authority.approval`, `packet`, `epic`,
    `feature`, `execution`, `project`, `version`, `unit_contract`) y las
    únicas adiciones son `situation`, `next.operation` y
    `authority.approval_reference`: quitarlas recupera la proyección antigua
    completa."""
    root, home = _case_prepared(tmp_path)
    state = read_state(root)
    packet = _member(state, "active_packet", "state del fixture")
    execution = _member(state, "execution", "state del fixture")

    doc = _document(_status(root, home))
    assert _situation(doc) == "packet-prepared"

    # Sólo las tres adiciones declaradas (raíz y ubicaciones exactas).
    assert set(doc) == OLD_TOP_LEVEL | {"situation"}, (
        "PC-11: la proyección debe contener los campos anteriores más "
        f"`situation` y nada más; hoy {sorted(doc)}"
    )
    next_block = _next(doc)
    assert set(next_block) == {"route", "source", "operation"}, (
        "PC-11: `next` sólo agrega `operation`; hoy "
        f"{sorted(next_block)}"
    )
    authority = _key(doc, "authority")
    assert set(authority) == {
        "approval",
        "approver",
        "hitl_delegation",
        "approval_reference",
    }, (
        "PC-11: `authority` sólo agrega `approval_reference`; hoy "
        f"{sorted(authority)}"
    )

    # Valores anteriores intactos.
    assert _key(doc, "entry") == "continuity-reconcile", (
        f"PC-11: `entry` conserva su mapa existente: {_key(doc, 'entry')!r}"
    )
    assert next_block["source"] == "docs/.cdad-state.json:active_packet.status", (
        f"PC-11: `next.source` anterior intacto: {next_block['source']!r}"
    )
    route = next_block["route"]
    assert DISPATCH_ROUTE.search(route), (
        "PC-11/PD-5: `next.route` conserva la acción natural del paquete "
        f"preparado (despacharlo): {route!r}"
    )
    assert "--replace-packet" in route, (
        "PC-11/PD-5: `next.route` conserva su rama condicional "
        f"(`--replace-packet`): {route!r}"
    )
    assert authority["approval"] == {
        "authority_ref": _member(execution, "authority_ref", "state.execution"),
        "contract_sha256": DECLARED_SPEC_SHA,
    }, (
        "PC-11: `authority.approval` se conserva intacto: "
        f"{authority['approval']!r}"
    )
    packet_block = _key(doc, "packet")
    assert packet_block == {
        "id": _member(packet, "id", "state.active_packet"),
        "role": _member(packet, "role", "state.active_packet"),
        "substage": _member(packet, "substage", "state.active_packet"),
        "status": "prepared",
    }, f"PC-11: bloque `packet` anterior intacto: {packet_block!r}"

    # Sin condiciones nuevas, `unknowns` no agrega causas.
    for entry in _key(doc, "unknowns"):
        assert not NEW_CAUSE_TOKEN.search(entry), (
            "PC-11: un fixture sin las condiciones de §2.4 no agrega causas "
            f"nuevas a `unknowns`: {entry!r}"
        )

    # La rama condicional y la de reconciliación se conservan por separado.
    _set_packet_status(root, "dispatched")
    dispatched = _document(_status(root, home))
    assert _situation(dispatched) == "packet-dispatched"
    dispatched_route = _next(dispatched)["route"]
    assert _key(dispatched, "entry") == "continuity-reconcile", (
        "PC-11: `entry` no cambia para despachado: "
        f"{_key(dispatched, 'entry')!r}"
    )
    assert RECONCILE_ROUTE.search(dispatched_route), (
        f"PC-11/PD-5: la ruta de despachado conserva la reconciliación: "
        f"{dispatched_route!r}"
    )
    assert REPEAT_ROUTE.search(dispatched_route), (
        "PC-11/PD-5: la ruta de despachado conserva la reconciliación ANTES "
        f"DE REPETIR: {dispatched_route!r}"
    )
    assert dispatched_route != route, (
        "PC-11/PD-5: preparado y despachado no pueden colapsar en la misma "
        f"prosa: {route!r}"
    )


def test_status_preserves_and_extends_unknowns(tmp_path: Path) -> None:
    """PC-11 grupo 2/§2.4: en un fixture CON una condición diagnóstica nueva,
    quitar las tres adiciones deja todos los campos anteriores iguales
    EXCEPTO `unknowns`; la lista conserva todos los diagnósticos anteriores
    con su contenido y orden relativo y añade la causa nueva requerida
    (fuente + condición, aclaración 5)."""
    control_root, control_home = _case_prepared(tmp_path / "control")
    control = _document(_status(control_root, control_home))

    root, home = _case_prepared(tmp_path / "inconsistent")
    _mutate_request(root, _packet_id(root), execution_id="exec-999-999-foreign")
    doc = _document(_status(root, home))

    assert _situation(control) == "packet-prepared"
    assert _situation(doc) == "pending-work-unresolved", (
        "PC-04: la pertenencia inconsistente produce pending-work-unresolved: "
        f"{doc.get('situation')!r}"
    )

    stripped_control = _strip_additions(control)
    stripped_doc = _strip_additions(doc)
    old_control = dict(stripped_control)
    old_doc = dict(stripped_doc)
    old_control.pop("unknowns", None)
    old_doc.pop("unknowns", None)
    differ = sorted(
        key
        for key in set(old_control) | set(old_doc)
        if old_control.get(key) != old_doc.get(key)
    )
    assert not differ, (
        "PC-11/§2.4: al quitar las tres adiciones, todos los campos anteriores "
        f"salvo `unknowns` deben coincidir; difieren {differ}; control="
        f"{json.dumps(old_control, sort_keys=True)[:400]}"
    )

    old_unknowns = _key(control, "unknowns")
    new_unknowns = _key(doc, "unknowns")
    _assert_preserved(old_unknowns, new_unknowns)
    new_causes = [entry for entry in new_unknowns if entry not in old_unknowns]
    assert new_causes, (
        "PC-11/§2.4: la condición nueva debe añadir su causa a `unknowns`, "
        f"sin sustituir las anteriores: {new_unknowns!r}"
    )
    _assert_new_cause(
        new_unknowns, [[_SOURCE_EXECUTION], [_CONDITION_MISMATCH]], "PC-11/§2.4"
    )

    # La pertenencia inconsistente no habilita la referencia de aprobación.
    ref = _approval_reference(doc)
    assert ref["status"] == "desconocida", (
        f"PC-11/§2.3 C1: sin pertenencia inequívoca: {ref['status']!r}"
    )
    assert ref["role"] is None and ref["object"] is None and ref["record"] is None


# ---------------------------------------------------------------- PC-12


def test_status_is_read_only(tmp_path: Path) -> None:
    """PC-12/INV-3: ejecutar `status` no altera bytes del estado, requests,
    contratos, historiales ni checkpoints (árbol del proyecto byte-idéntico).

    CONTROL declarado: esta propiedad ya se cumple antes de 007-001 y el test
    debe seguir pasando después (guardia de neutralidad).
    """
    root, home = _case_prepared(tmp_path)
    before_tree = tree_snapshot(root)
    before_state = (root / STATE_FILE).read_bytes()
    before_request = _request_path(root, _packet_id(root)).read_bytes()
    before_contract = (root / CONTRACT_FILE).read_bytes()

    doc = _document(_status(root, home))
    assert _key(doc, "entry"), "PC-12: la vista debe emitir su proyección"

    assert (root / STATE_FILE).read_bytes() == before_state, (
        "PC-12/INV-3: `status` modificó docs/.cdad-state.json"
    )
    assert (root / CONTRACT_FILE).read_bytes() == before_contract, (
        "PC-12/INV-3: `status` modificó el contrato"
    )
    assert _request_path(root, _packet_id(root)).read_bytes() == before_request, (
        "PC-12/INV-3: `status` modificó el REQUEST.json del paquete activo"
    )
    after_tree = tree_snapshot(root)
    changed = sorted(
        path
        for path in set(before_tree) | set(after_tree)
        if before_tree.get(path) != after_tree.get(path)
    )
    assert not changed, (
        f"PC-12/INV-3: `status` escribió en el proyecto: {changed}"
    )


# ---------------------------------------------------------------- PC-13


def test_status_bound_and_history_independence(tmp_path: Path) -> None:
    """PC-13/INV-6: la salida sigue siendo un único JSON acotado (16.384 B);
    superar `--max-bytes` falla cerrado sin JSON parcial y con diagnóstico; y
    agregar historial no seleccionado no aumenta ni altera la salida
    (`big_doc == small_doc`: `record.index` es el del primer registro
    aplicable en su historial, sin contadores derivados del historial)."""
    root, home = _case_prepared(tmp_path)
    small_proc = _status(root, home)
    small = _document(small_proc)
    assert _situation(small) == "packet-prepared"
    assert _approval_reference(small)["status"] == "vigente", (
        "fixture: la aprobación sembrada por el fixture está vigente"
    )
    assert len(small_proc.stdout.encode("utf-8")) <= MAX_BYTES, (
        f"PC-13: el documento supera {MAX_BYTES} B por defecto"
    )

    state = read_state(root)
    selected = list(_member(state, "stage_history", "state del fixture"))
    extra = [
        {
            "feature": f"999-99{index:03d}-other-feature",
            "stage": "specification",
            "approved_by": "Pablo",
            "approved_at": "2026-10-20T00:00:00Z",
            "contract_path": f"docs/specs/999-99{index:03d}-other/spec.md",
            "contract_sha256": _sha(f"other-{index}".encode()),
        }
        for index in range(800)
    ]
    state["stage_history"] = selected + extra
    write_state(root, state)
    assert (root / STATE_FILE).stat().st_size > MAX_BYTES, (
        "fixture: el historial sintético no agrandó el estado"
    )

    big_proc = _status(root, home)
    big = _document(big_proc)
    assert len(big_proc.stdout.encode("utf-8")) <= MAX_BYTES, (
        f"PC-13/INV-6: con historial grande el documento supera {MAX_BYTES} B "
        f"({len(big_proc.stdout.encode('utf-8'))} B)"
    )
    assert "stage_history" not in big_proc.stdout, (
        "PC-13: la vista no vuelca el historial"
    )
    assert big == small, (
        "PC-13: la proyección cambió al agregar historial NO seleccionado "
        "(debe ser función de los campos operativos y del primer registro "
        f"aplicable, sin contadores); small={json.dumps(small, sort_keys=True)[:400]}"
    )

    limited = _status(root, home, "--max-bytes", "64")
    out = limited.stdout + limited.stderr
    assert limited.returncode != 0, (
        "PC-13/INV-6: con --max-bytes 64 la vista debe fallar cerrado "
        f"(rc=0 hoy, rc={limited.returncode})"
    )
    assert limited.stdout.strip() == "", (
        "PC-13/INV-6: no debe emitir una proyección parcial: "
        f"{limited.stdout[:200]!r}"
    )
    assert "--max-bytes" in out, (
        "PC-13/INV-6: el diagnóstico debe nombrar el camino legítimo "
        f"(--max-bytes N): {out.strip()!r}"
    )
    assert re.search(r"(?i)\bbytes\b|\bl[ií]mite\b|\blimit\b", out), (
        f"PC-13/INV-6: el diagnóstico debe nombrar la causa (el límite): "
        f"{out.strip()!r}"
    )


# ---------------------------------------------------------------- PC-14


def test_orchestrator_references_operation_map() -> None:
    """PC-14/§3: el mapa documentado verbo→script existe en
    `references/orientation.md`, resuelve a scripts existentes bajo el skill,
    el cuerpo canónico del orquestador lo referencia leyendo `situation` y
    `next.operation`, y los dos registros de despacho se distinguen
    (`prepare --record-dispatch` no es el verbo `record` de transporte)."""
    orientation_path = SKILL_DIR / "references" / "orientation.md"
    orchestrator_path = REPO_ROOT / "sources" / "roles" / "orchestrator.md"
    assert orientation_path.is_file(), (
        f"PC-14: falta el propietario del mapa: {orientation_path}"
    )
    assert orchestrator_path.is_file(), (
        f"PC-14: falta el cuerpo canónico del orquestador: {orchestrator_path}"
    )
    orientation = orientation_path.read_text(encoding="utf-8")
    orchestrator = orchestrator_path.read_text(encoding="utf-8")
    lines = orientation.splitlines()

    expected_map = {
        PACKET_SCRIPT: [
            "status",
            "validate-packet",
            "open-unit",
            "prepare",
            "render",
            "prepare --record-dispatch",
        ],
        CONTINUITY_SCRIPT: ["begin", "checkpoint", "reconcile", "resume", "trigger"],
        RESULT_SCRIPT: ["receive"],
    }
    for script, verbs in expected_map.items():
        assert (SKILL_DIR / script).is_file(), (
            f"PC-14: el script del mapa no existe bajo el skill: {script}"
        )
        for verb in verbs:
            matches = [
                line
                for line in lines
                if script in line
                and re.search(
                    rf"(?<![\w-]){re.escape(verb)}(?![\w-])", line
                )
            ]
            assert matches, (
                "PC-14: el mapa de orientación no asigna el verbo "
                f"{verb!r} a {script!r}; líneas que nombran el script: "
                f"{[l for l in lines if script in l][:5]!r}"
            )

    # `prepare --record-dispatch` y el verbo `record` de transporte no son
    # alias intercambiables (§3): ninguna fila del mapa asigna el verbo
    # `record` a `cdad_packet.py`.
    for line in lines:
        if PACKET_SCRIPT not in line or "|" not in line:
            continue
        row = line.replace("--record-dispatch", "")
        assert not re.search(r"(?<![\w-])record(?![\w-])", row), (
            "PC-14/§3: `prepare --record-dispatch` no es el verbo `record` de "
            f"la entrada de transporte; fila inválida: {line!r}"
        )

    assert "orientation.md" in orchestrator, (
        "PC-14/§3: el árbol del orquestador debe citar el mapa desde "
        "`references/orientation.md`"
    )
    assert "situation" in orchestrator, (
        "PC-14/§3: el árbol del orquestador debe leer `situation`"
    )
    assert "next.operation" in orchestrator, (
        "PC-14/§3: el árbol del orquestador debe leer `next.operation`"
    )
    assert "pending-work-unresolved" in (orchestrator + orientation), (
        "PC-14/§3: el caso pendiente irresuelto debe declararse como "
        "diagnóstico sin despacho (pending-work-unresolved)"
    )


# ---------------------------------------------------------------- review-001
# RED de corrección (paquete test-writer-red-002): los diagnósticos NUEVOS se
# prueban por concepto —fuente y condición—, no por texto exacto (aclaración 5
# del audit); los anteriores, por contenido y orden relativo (§2.4).

_SOURCE_STAGE_HISTORY = re.compile(
    r"(?i)stage[_ ]history|stage history|historial|history"
)
_SOURCE_EPIC_HISTORY = re.compile(
    r"(?i)epic[_ ]history|epic history|historial|history|mandato|mandate"
)
_SOURCE_CONTRACT_BYTES = re.compile(
    r"(?i)contract|contrato|spec|bytes|docs/specs|digest"
)
_CONDITION_MALFORMED_SOURCE = re.compile(
    r"(?i)lista|list|malform|malformed|corrupt|ilegible|unreadable|interpret|"
    r"invalid|inv[aá]lid|json|estructura|shape|tipo|type"
)
_CONDITION_ESCAPE = re.compile(
    r"(?i)symlink|enlace|escape|escapa|outside|fuera|confin|pertenencia|"
    r"membership|unresolved|inconsisten|no pertenece|not inside|not within"
)


# ------------------------------------------------- review-001 BLOCKING 1


def _r1_malformed_stage_history(base: Path) -> tuple[Path, Path]:
    """Fuente de aprobación no interpretable como lista (string)."""
    root, home = _case_prepared(base)
    state = read_state(root)
    state["stage_history"] = "corrupt"
    write_state(root, state)
    return root, home


def _r1_malformed_stage_history_mapping(base: Path) -> tuple[Path, Path]:
    """Fuente de aprobación no interpretable como lista (objeto JSON)."""
    root, home = _case_prepared(base)
    state = read_state(root)
    state["stage_history"] = {"corrupt": True}
    write_state(root, state)
    return root, home


def _r1_malformed_epic_history(base: Path) -> tuple[Path, Path]:
    """Mandato del epic no interpretable como lista (string)."""
    root, home, _plan_rel = _architect_project(base)
    state = read_state(root)
    state["epic_history"] = "corrupt"
    write_state(root, state)
    return root, home


def _r1_readable_stage_history_without_approvals(
    base: Path,
) -> tuple[Path, Path]:
    """Historial legible y vacío: no hay registros de aprobación."""
    root, home = _case_prepared(base)
    state = read_state(root)
    state["stage_history"] = []
    write_state(root, state)
    return root, home


def _r1_readable_epic_history_without_mandate(base: Path) -> tuple[Path, Path]:
    """Historial legible y vacío: no hay mandato del epic."""
    root, home, _plan_rel = _architect_project(base)
    state = read_state(root)
    state["epic_history"] = []
    write_state(root, state)
    return root, home


MALFORMED_SOURCE_CASES = [
    pytest.param(
        _r1_malformed_stage_history,
        _r1_readable_stage_history_without_approvals,
        "desconocida",
        "test-writer",
        "feature-spec",
        [[_SOURCE_STAGE_HISTORY], [_CONDITION_MALFORMED_SOURCE]],
        id="stage-history-not-a-list",
    ),
    pytest.param(
        _r1_malformed_stage_history_mapping,
        _r1_readable_stage_history_without_approvals,
        "desconocida",
        "test-writer",
        "feature-spec",
        [[_SOURCE_STAGE_HISTORY], [_CONDITION_MALFORMED_SOURCE]],
        id="stage-history-mapping-not-a-list",
    ),
    pytest.param(
        _r1_malformed_epic_history,
        _r1_readable_epic_history_without_mandate,
        "desconocida",
        "architect",
        "epic-plan",
        [[_SOURCE_EPIC_HISTORY], [_CONDITION_MALFORMED_SOURCE]],
        id="epic-history-not-a-list",
    ),
    pytest.param(
        _r1_readable_stage_history_without_approvals,
        _r1_readable_stage_history_without_approvals,
        "ausente",
        "test-writer",
        "feature-spec",
        None,
        id="readable-stage-history-empty-is-absent",
    ),
    pytest.param(
        _r1_readable_epic_history_without_mandate,
        _r1_readable_epic_history_without_mandate,
        "ausente",
        "architect",
        "epic-plan",
        None,
        id="readable-epic-history-empty-is-absent",
    ),
]


@pytest.mark.parametrize(
    "build,control_build,expected_status,expected_role,expected_object,"
    "cause_groups",
    MALFORMED_SOURCE_CASES,
)
def test_malformed_approval_sources_are_unknown_not_absent(
    tmp_path: Path,
    build,
    control_build,
    expected_status: str,
    expected_role: str,
    expected_object: str,
    cause_groups: list[list[re.Pattern]] | None,
) -> None:
    """review-001 BLOCKING 1 — fuentes de aprobación malformadas (PC-09/S1,
    PC-05/A1 y PC-11/§2.4): una `stage_history`/`epic_history` que no puede
    interpretarse como lista impide resolver la referencia → `desconocida`
    (nunca `ausente`) con causa de fuente y condición en `unknowns`,
    conservando los diagnósticos anteriores; un historial LEGIBLE sin
    aprobaciones sigue dando `ausente` y no agrega causas."""
    control_root, control_home = control_build(tmp_path / "control")
    control = _document(_status(control_root, control_home))
    control_unknowns = _key(control, "unknowns")

    root, home = build(tmp_path / "case")
    doc = _document(_status(root, home))
    ref = _approval_reference(doc)

    assert ref["role"] == expected_role, (
        "review-001 BLOCKING 1: el rol se resuelve desde el request legible: "
        f"{ref['role']!r}"
    )
    assert ref["object"] == expected_object, (
        "review-001 BLOCKING 1: el objeto se resuelve desde el request "
        f"legible: {ref['object']!r}"
    )
    assert ref["status"] == expected_status, (
        "review-001 BLOCKING 1: resultado incorrecto para el historial del "
        f"fixture; esperado {expected_status!r}, hoy {ref['status']!r} "
        f"(reason={ref['reason']!r})"
    )

    if expected_status == "desconocida":
        assert ref["status"] != "ausente", (
            "review-001 BLOCKING 1/§2.3 S1-A1: una fuente NO interpretable no "
            f"prueba ausencia de aprobación: {ref['status']!r}"
        )
        assert ref["record"] is None, (
            "review-001 BLOCKING 1/§2.3: sin historial interpretable no se "
            f"fabrica un localizador: {ref['record']!r}"
        )
        assert isinstance(ref["reason"], str) and ref["reason"].strip(), (
            "review-001 BLOCKING 1: `desconocida` explica su causa en `reason`"
        )
        unknowns = _key(doc, "unknowns")
        _assert_preserved(control_unknowns, unknowns)
        _assert_new_cause(unknowns, cause_groups, "review-001 BLOCKING 1")
    else:
        assert ref["status"] != "desconocida", (
            "review-001 BLOCKING 1/§2.3 S2-A2: un historial legible sin "
            f"aprobaciones es ausencia, no desconocida: {ref['status']!r}"
        )
        assert ref["record"] is None, (
            f"review-001 BLOCKING 1: `ausente` no inventa registro: {ref['record']!r}"
        )
        assert isinstance(ref["reason"], str) and ref["reason"].strip(), (
            "review-001 BLOCKING 1: `ausente` explica su causa"
        )
        assert _key(doc, "unknowns") == control_unknowns, (
            "review-001 BLOCKING 1/§2.4: un historial legible aunque vacío no "
            "es una fuente ilegible y no agrega causas a `unknowns`: "
            f"{_key(doc, 'unknowns')!r} != {control_unknowns!r}"
        )


# ------------------------------------------------- review-001 BLOCKING 2(a)


def test_unreadable_contract_cause_reaches_unknowns(tmp_path: Path) -> None:
    """review-001 BLOCKING 2(a) — contrato ilegible (PC-09/S1, §2.3 C2/S1 y
    §2.4): el resultado sigue siendo `desconocida`, pero la causa NUEVA debe
    identificar la fuente (la declaración/bytes del contrato) y la condición
    (no puede leerse) en `unknowns`, conservando el diagnóstico previo."""
    control_root, control_home = _case_prepared(tmp_path / "control")
    control = _document(_status(control_root, control_home))
    control_unknowns = _key(control, "unknowns")
    assert isinstance(control_unknowns, list)

    root, home = _case_prepared(tmp_path / "case")
    (root / CONTRACT_FILE).unlink()
    doc = _document(_status(root, home))
    ref = _approval_reference(doc)

    assert ref["status"] == "desconocida", (
        "review-001 BLOCKING 2(a)/PC-09/S1: sin bytes actuales del contrato no "
        f"se afirma ausencia ni vigencia: {ref['status']!r}"
    )
    assert ref["status"] != "ausente", (
        "review-001 BLOCKING 2(a)/INV-4: desconocido no equivale a ausente: "
        f"{ref['status']!r}"
    )
    assert isinstance(ref["reason"], str) and ref["reason"].strip(), (
        "review-001 BLOCKING 2(a): `desconocida` explica su causa en `reason`"
    )

    unknowns = _key(doc, "unknowns")
    _assert_preserved(control_unknowns, unknowns)
    new_causes = [entry for entry in unknowns if entry not in control_unknowns]
    assert new_causes, (
        "review-001 BLOCKING 2(a)/§2.4: la causa del contrato ilegible debe "
        "agregarse a `unknowns` sin sustituir el diagnóstico anterior: "
        f"{unknowns!r}"
    )
    _assert_new_cause(
        unknowns,
        [[_SOURCE_CONTRACT_BYTES], [_CONDITION_UNREADABLE]],
        "review-001 BLOCKING 2(a)",
    )


# ------------------------------------------------- review-001 BLOCKING 2(b)


def test_unreadable_pending_candidate_stays_unproven(tmp_path: Path) -> None:
    """review-001 BLOCKING 2(b) — sin `active_packet` y un candidato con
    `REQUEST.json` ilegible (§2.1, PC-04 y §2.4): la ilegibilidad se informa
    en `unknowns`, el candidato NO se convierte en pendiente probado y
    `_pending_work` no cambia (la situación sigue siendo `execution-active`,
    como sin candidatos; el mismo candidato legible sí sería
    `pending-work-unresolved`)."""
    control_root, control_home = _case_execution_active(tmp_path / "control")
    control = _document(_status(control_root, control_home))
    assert _situation(control) == "execution-active", (
        "review-001 BLOCKING 2(b): control sin candidatos: "
        f"{control.get('situation')!r}"
    )
    control_unknowns = _key(control, "unknowns")

    root, home = _case_prepared(tmp_path / "case")
    packet_id = _packet_id(root)
    _request_path(root, packet_id).write_text("{broken", encoding="utf-8")
    _drop_active_packet(root)
    doc = _document(_status(root, home))

    assert _situation(doc) == "execution-active", (
        "review-001 BLOCKING 2(b)/§2.1: un request ilegible no prueba "
        "pertenencia a la ejecución activa y no puede convertir el candidato "
        f"en pendiente probado; hoy {doc.get('situation')!r}"
    )
    assert _situation(doc) != "pending-work-unresolved", (
        "review-001 BLOCKING 2(b)/§2.1: la ilegibilidad no inventa trabajo "
        f"pendiente: {doc.get('situation')!r}"
    )

    ref = _approval_reference(doc)
    assert ref["status"] == "desconocida", (
        "review-001 BLOCKING 2(b)/§2.3 C1: sin paquete activo inequívoco no "
        f"se establece la aprobación aplicable: {ref['status']!r}"
    )
    assert ref["role"] is None and ref["object"] is None, (
        f"review-001 BLOCKING 2(b)/C1: role/object null: "
        f"{ref['role']!r}/{ref['object']!r}"
    )
    assert ref["record"] is None, (
        f"review-001 BLOCKING 2(b)/C1: record null: {ref['record']!r}"
    )

    unknowns = _key(doc, "unknowns")
    _assert_preserved(control_unknowns, unknowns)
    _assert_new_cause(
        unknowns,
        [[_SOURCE_REQUEST], [_CONDITION_UNREADABLE]],
        "review-001 BLOCKING 2(b)",
    )

    # `_pending_work` no cambia: el MISMO candidato con request legible sí
    # prueba trabajo pendiente (ausencia de recibo en su ruta existente).
    readable_root, readable_home = _case_pending(tmp_path / "readable")
    readable = _document(_status(readable_root, readable_home))
    assert _situation(readable) == "pending-work-unresolved", (
        "review-001 BLOCKING 2(b): control: un candidato legible de la misma "
        "ejecución sin recibo sí es trabajo pendiente probado: "
        f"{readable.get('situation')!r}"
    )


# --------------------------------------------------- review-001 BLOCKING 3


def test_request_symlink_escape_is_unresolved(tmp_path: Path) -> None:
    """review-001 BLOCKING 3 — confinamiento del request (§2.1 requisito 3,
    PC-04 y §2.4): un `REQUEST.json` alcanzado por un symlink cuya ruta
    resuelta escapa del árbol de paquetes no puede leerse como paquete activo
    inequívoco; se rechaza con `pending-work-unresolved`,
    `approval_reference.status=desconocida` (C1, sin rol/objeto/registro) y
    una causa de pertenencia en `unknowns`, sin fallback."""
    control_root, control_home = _case_prepared(tmp_path / "control")
    control = _document(_status(control_root, control_home))
    control_unknowns = _key(control, "unknowns")

    root, home = _case_prepared(tmp_path / "case")
    packet_id = _packet_id(root)
    request_path = _request_path(root, packet_id)
    assert request_path.is_file(), f"fixture: falta {request_path}"

    escape_dir = tmp_path / "escape"
    escape_dir.mkdir()
    outside = escape_dir / "REQUEST.json"
    shutil.move(str(request_path), outside)
    os.symlink(outside, request_path)
    assert request_path.is_symlink(), (
        f"fixture: el request no quedó como symlink: {request_path}"
    )
    assert root.resolve() not in outside.resolve().parents, (
        f"fixture: el destino del symlink no escapó del proyecto: {outside}"
    )

    doc = _document(_status(root, home))

    assert _situation(doc) == "pending-work-unresolved", (
        "review-001 BLOCKING 3/§2.1: un request que resuelve fuera del árbol "
        "de paquetes es una inconsistencia de pertenencia del paquete activo "
        f"y no habilita despacho; hoy {doc.get('situation')!r}"
    )
    op = _operation(doc)
    assert op["verb"] == "diagnose", (
        f"review-001 BLOCKING 3/§2.2: el escape no ejecuta una operación: {op['verb']!r}"
    )
    assert op["script"] is None, (
        f"review-001 BLOCKING 3/§2.2: diagnose no lleva script: {op['script']!r}"
    )
    assert op["procedure"] == "references/project-execution.md", (
        f"review-001 BLOCKING 3/§2.2: procedimiento esperado: {op['procedure']!r}"
    )
    assert op["source"] == "docs/.cdad-state.json:active_packet / .cdad/packets", (
        "review-001 BLOCKING 3/§2.2: `source` exacto de "
        f"pending-work-unresolved: {op['source']!r}"
    )

    ref = _approval_reference(doc)
    assert ref["status"] == "desconocida", (
        "review-001 BLOCKING 3/§2.3 C1: sin pertenencia inequívoca no se "
        f"afirma aprobación: {ref['status']!r}"
    )
    assert ref["status"] != "vigente", (
        "review-001 BLOCKING 3: el identificador seguro no garantiza el "
        f"confinamiento del request: {ref['status']!r}"
    )
    assert ref["role"] is None and ref["object"] is None, (
        "review-001 BLOCKING 3/C1: la ruta se verifica ANTES de leer; no se "
        f"inventan rol ni objeto: {ref['role']!r}/{ref['object']!r}"
    )
    assert ref["record"] is None, (
        f"review-001 BLOCKING 3/C1: record null: {ref['record']!r}"
    )

    unknowns = _key(doc, "unknowns")
    _assert_preserved(control_unknowns, unknowns)
    _assert_new_cause(
        unknowns,
        [[_SOURCE_REQUEST], [_CONDITION_ESCAPE]],
        "review-001 BLOCKING 3",
    )


# --------------------- review-002 residual (clave presente, valor null)
# review-002 distingue PERTENENCIA de clave y VALOR: una fuente de aprobación
# presente con valor null no es un historial legible y vacío. `[]` conserva el
# resultado `ausente` (guarda ya cubierta por MALFORMED_SOURCE_CASES y
# verificado de nuevo como control del MISMO fixture en este test).

_CONDITION_NULL_HISTORY = re.compile(
    r"(?i)null|none|nil|lista|list|array|tipo|type|shape|estructura|"
    r"interpret|malform|invalid|unreadable|ilegible|readable|"
    r"no puede leer|no se puede leer|ausente|absent|missing"
)


def _r2_null_stage_history(base: Path) -> tuple[Path, Path]:
    """`stage_history` presente con valor null (no es un historial vacío)."""
    root, home = _case_prepared(base)
    state = read_state(root)
    state["stage_history"] = None
    write_state(root, state)
    return root, home


def _r2_empty_stage_history(base: Path) -> tuple[Path, Path]:
    """Control: `stage_history` presente y vacío → ausente (guarda vigente)."""
    root, home = _case_prepared(base)
    state = read_state(root)
    state["stage_history"] = []
    write_state(root, state)
    return root, home


def _r2_null_epic_history(base: Path) -> tuple[Path, Path]:
    """`epic_history` presente con valor null (no es un historial vacío)."""
    root, home, _plan_rel = _architect_project(base)
    state = read_state(root)
    state["epic_history"] = None
    write_state(root, state)
    return root, home


def _r2_empty_epic_history(base: Path) -> tuple[Path, Path]:
    """Control: `epic_history` presente y vacío → ausente (guarda vigente)."""
    root, home, _plan_rel = _architect_project(base)
    state = read_state(root)
    state["epic_history"] = []
    write_state(root, state)
    return root, home


NULL_HISTORY_CASES = [
    pytest.param(
        _r2_null_stage_history,
        _r2_empty_stage_history,
        "test-writer",
        "feature-spec",
        _SOURCE_STAGE_HISTORY,
        id="stage-history-null",
    ),
    pytest.param(
        _r2_null_epic_history,
        _r2_empty_epic_history,
        "architect",
        "epic-plan",
        _SOURCE_EPIC_HISTORY,
        id="epic-history-null",
    ),
]


@pytest.mark.parametrize(
    "build,control_build,expected_role,expected_object,source_pattern",
    NULL_HISTORY_CASES,
)
def test_null_history_value_is_unknown_not_absent(
    tmp_path: Path,
    build,
    control_build,
    expected_role: str,
    expected_object: str,
    source_pattern: re.Pattern,
) -> None:
    """review-002 residual (PC-06/S1, PC-05/A1, §2.3 y §2.4): una fuente de
    aprobación con la clave presente y valor `null` no puede interpretarse
    como historial: produce `desconocida` (nunca `ausente`) con una causa de
    fuente y condición en `reason` y en `unknowns`, conservando los
    diagnósticos anteriores. `[]` sigue produciendo `ausente` (control del
    mismo fixture; guarda ya existente)."""
    control_root, control_home = control_build(tmp_path / "control")
    control = _document(_status(control_root, control_home))
    control_ref = _approval_reference(control)
    assert control_ref["status"] == "ausente", (
        "review-002/§2.3: un historial presente y VACÍO ([]) sigue siendo "
        f"ausencia, no desconocida: {control_ref['status']!r}"
    )
    assert control_ref["record"] is None, (
        f"review-002/§2.3: `[]` no inventa registro: {control_ref['record']!r}"
    )
    control_unknowns = _key(control, "unknowns")

    root, home = build(tmp_path / "case")
    proc = _status(root, home)
    _assert_no_history_token(proc, "review-002")
    doc = _document(proc)
    ref = _approval_reference(doc)

    assert ref["role"] == expected_role, (
        "review-002/§2.3: el rol se resuelve desde el request legible: "
        f"{ref['role']!r}"
    )
    assert ref["object"] == expected_object, (
        "review-002/§2.3: el objeto se resuelve desde el request legible: "
        f"{ref['object']!r}"
    )
    assert ref["status"] == "desconocida", (
        "review-002/§2.3 S1-A1: una clave presente con valor null no es un "
        "historial legible y vacío; el resultado es desconocida, no "
        f"ausente: {ref['status']!r} (reason={ref['reason']!r})"
    )
    assert ref["status"] != "ausente", (
        "review-002/INV-4: desconocido no equivale a ausente: "
        f"{ref['status']!r}"
    )
    assert ref["record"] is None, (
        "review-002/§2.3: sin historial interpretable no se fabrica un "
        f"localizador: {ref['record']!r}"
    )
    assert isinstance(ref["reason"], str) and ref["reason"].strip(), (
        "review-002: `desconocida` explica su causa en `reason`"
    )
    _assert_new_cause(
        [ref["reason"]],
        [[source_pattern], [_CONDITION_NULL_HISTORY]],
        "review-002/reason",
    )

    unknowns = _key(doc, "unknowns")
    _assert_preserved(control_unknowns, unknowns)
    new_causes = [entry for entry in unknowns if entry not in control_unknowns]
    assert new_causes, (
        "review-002/§2.4: la causa del historial presente con valor null debe "
        "agregarse a `unknowns` sin sustituir los diagnósticos anteriores: "
        f"{unknowns!r}"
    )
    _assert_new_cause(
        new_causes,
        [[source_pattern], [_CONDITION_NULL_HISTORY]],
        "review-002/unknowns",
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
