#!/usr/bin/env python3
"""agent-overlay.py — the ONE owner of the user-owned agent overlay (009-001).

The installer deploys agents whose frontmatter some values are the USER's, not
CDAD's: the model each role runs on is configured by the person who installs
(`model:`), never by the product (006-003 D1/INV-3). An update must therefore
bring every other byte from staging while the user's value survives. This file
is the single definition of that overlay: install, `--check` (including its
legacy path) and `scripts/validate-subagents.sh` consume it and never
reimplement it in bash.

USER-OWNED KEYS ARE DATA
------------------------
`USER_OWNED_KEYS` is the list. Adding a key is one entry here plus a fixture:
every consumer inherits the behaviour (install, `--check`, validator).

ADMITTED GRAMMAR (deliberately narrow; nothing else is interpreted)
------------------------------------------------------------------
- An agent file is text whose FIRST line is exactly `---` and that closes the
  frontmatter with the next line that is exactly `---`.
- A user-owned key lives at column 0 inside that frontmatter block, as
  `key: value`. Its value is the rest of the line, stripped, and must not be
  empty. The value is preserved verbatim (never reinterpreted, never YAML
  parsed).
- Merging reinserts the keys at the END of the staged frontmatter, in
  `USER_OWNED_KEYS` order: the result is a pure function of
  (staged bytes, extracted values), which is what makes a second install a
  no-op.

FAIL CLOSED
-----------
No frontmatter, an unterminated frontmatter, a duplicated key, a key nested
inside the frontmatter, a key declared in the BODY of the file and an empty
value are all *ambiguous*: they raise OverlayError with the reason. An
ambiguous copy is never partially extracted and never silently accepted — the
caller preserves it as a conflict (D3).

CLI (exit codes: 0 ok, 1 divergent, 2 error/ambiguous)
-----------------------------------------------------
  agent-overlay.py extract FILE
      Prints one `key=value` line per user-owned key present (nothing when the
      copy carries none). The diagnostic of an ambiguous copy goes to stderr
      and nothing is printed.
  agent-overlay.py base-sha FILE
      Prints the sha256 of the file with the user-owned key lines removed: the
      BASE an install can compare against its recorded provenance.
  agent-overlay.py merge STAGED FILE [--out PATH]
      Writes STAGED with the user-owned values of FILE reinserted (stdout by
      default, PATH with --out: the byte path never rides on a shell variable).
  agent-overlay.py compare INSTALLED EXPECTED
      Prints `identical`, `overlay-only: model=...` or `divergent: <reason>`.
      Exit 0 for the two in-sync verdicts, 1 for divergent, 2 for ambiguous.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

# The user's keys — DATA, not code (D1). One definition, every consumer.
USER_OWNED_KEYS = ("model",)

# `key: value` at column 0 (the only shape a user-owned key may take).
KEY_LINE = re.compile(rb"^(?P<key>[A-Za-z0-9_-]+):(?P<value>.*)$")
# The same key INDENTED: nested inside a block, hence not a top-level user key.
NESTED_KEY_LINE = re.compile(rb"^[ \t]+(?P<key>[A-Za-z0-9_-]+):")
DELIMITER = b"---"


class OverlayError(Exception):
    """The copy cannot be read as a well-formed agent with/without an overlay."""


def _declared_key(line: bytes) -> str:
    """The user-owned key a line DECLARES at column 0, or "" when none."""
    match = KEY_LINE.match(line.rstrip(b"\r"))
    if not match:
        return ""
    key = match.group("key").decode("ascii")
    return key if key in USER_OWNED_KEYS else ""


def _declares_user_key(line: bytes) -> bool:
    return bool(_declared_key(line))


def _declared_value(line: bytes) -> bytes:
    """The value of a line `_declared_key` recognized (after its `key:`)."""
    return KEY_LINE.match(line.rstrip(b"\r")).group("value").strip()


def split_frontmatter(data: bytes) -> tuple[list[bytes], list[bytes]]:
    """Split into (frontmatter lines INCLUDING both delimiters, body lines).

    Splitting on `b"\\n"` and rejoining with it is byte exact, so no content is
    normalized on the way through.
    """
    lines = data.split(b"\n")
    if lines[0].rstrip(b"\r") != DELIMITER:
        raise OverlayError("no frontmatter: the first line is not '---'")
    for index in range(1, len(lines)):
        if lines[index].rstrip(b"\r") == DELIMITER:
            return lines[:index + 1], lines[index + 1:]
    raise OverlayError("the frontmatter is not closed by a '---' line")


def extract(data: bytes) -> dict[str, bytes]:
    """The user-owned keys declared by `data`, in USER_OWNED_KEYS order."""
    header, body = split_frontmatter(data)
    found: dict[str, bytes] = {}
    for raw in header[1:-1]:
        key = _declared_key(raw)
        if key:
            value = _declared_value(raw)
            if not value:
                raise OverlayError(
                    f"{key}: declared with an empty value — a user-owned key "
                    f"needs a value")
            if key in found:
                raise OverlayError(
                    f"{key}: declared more than once in the frontmatter")
            found[key] = value
            continue
        nested = NESTED_KEY_LINE.match(raw.rstrip(b"\r"))
        if nested and nested.group("key").decode("ascii") in USER_OWNED_KEYS:
            raise OverlayError(
                f"{nested.group('key').decode('ascii')}: nested in the "
                f"frontmatter, not a top-level user-owned key")
    for raw in body:
        declared = _declared_key(raw)
        if declared:
            raise OverlayError(
                f"{declared}: declared in the body of the file, outside the "
                f"frontmatter")
    return {key: found[key] for key in USER_OWNED_KEYS if key in found}


def strip_overlay(data: bytes) -> bytes:
    """`data` without its user-owned key lines (the BASE the overlay sits on)."""
    header, body = split_frontmatter(data)
    header = [
        line for index, line in enumerate(header)
        if index in (0, len(header) - 1) or not _declares_user_key(line)
    ]
    return b"\n".join(header + body)


def merge(staged: bytes, overlay: dict[str, bytes]) -> bytes:
    """STAGED bytes with the user-owned values reinserted (D2: never the old file)."""
    header, body = split_frontmatter(staged)
    carried = extract(staged)
    if carried:
        raise OverlayError(
            "the staged bytes already declare " + ", ".join(carried)
            + ": installable text must not carry a user-owned key")
    lines = [
        key.encode("ascii") + b": " + overlay[key]
        for key in USER_OWNED_KEYS if key in overlay
    ]
    return b"\n".join(header[:-1] + lines + [header[-1]] + body)


def compare(installed: bytes, expected: bytes) -> tuple[str, str]:
    """(verdict, detail) of an installed copy against its expectation."""
    try:
        overlay = extract(installed)
        base = strip_overlay(installed)
    except OverlayError as error:
        return "error", str(error)
    detail = ", ".join(
        key + "=" + overlay[key].decode("utf-8", "backslashreplace")
        for key in USER_OWNED_KEYS if key in overlay)
    if base == expected:
        return ("overlay-only", detail) if overlay else ("identical", "")
    if overlay:
        return ("divergent",
                f"the bytes outside the user-owned overlay ({detail}) no "
                f"longer match the staged bytes")
    return ("divergent",
            "the bytes differ from the staged bytes outside any user-owned "
            "overlay")


def _read(path: str) -> bytes:
    try:
        return Path(path).read_bytes()
    except OSError as error:
        raise OverlayError(f"{path}: {error.strerror}") from error


def _usage() -> int:
    print(__doc__.strip(), file=sys.stderr)
    return 2


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        return _usage()
    command = argv[1]
    try:
        if command == "extract" and len(argv) == 3:
            for key, value in extract(_read(argv[2])).items():
                sys.stdout.write(
                    f"{key}={value.decode('utf-8', 'backslashreplace')}\n")
            return 0
        if command == "base-sha" and len(argv) == 3:
            print(hashlib.sha256(strip_overlay(_read(argv[2]))).hexdigest())
            return 0
        if command == "merge" and len(argv) in (4, 6) and (
                len(argv) == 4 or argv[4] == "--out"):
            merged = merge(_read(argv[2]), extract(_read(argv[3])))
            if len(argv) == 4:
                sys.stdout.buffer.write(merged)
            else:
                try:
                    Path(argv[5]).write_bytes(merged)
                except OSError as error:
                    raise OverlayError(f"{argv[5]}: {error.strerror}") from error
            return 0
        if command == "compare" and len(argv) == 4:
            verdict, detail = compare(_read(argv[2]), _read(argv[3]))
            print(f"{verdict}: {detail}" if detail else verdict)
            return {"identical": 0, "overlay-only": 0,
                    "divergent": 1}.get(verdict, 2)
    except OverlayError as error:
        print(str(error), file=sys.stderr)
        return 2
    return _usage()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
