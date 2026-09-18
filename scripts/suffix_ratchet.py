#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Live old-suffix ratchet for issue #1684.

Canonical executable Nika program source is lowercase ``*.nika``.
Retired live spellings ``.nika.yaml`` and ``.nika.yml`` must not appear
in tracked pathnames or live teaching text. Project ``nika.yaml`` and
runtime ``.nika/`` are different artifacts and are not this gate.

Exceptions must name path + bounded match + category + reason + owner.
Categories: historical · frozen-evidence · negative-test.
This is not a live compatibility exemption.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORBIDDEN = re.compile(r"\.nika\.ya?ml")

# path relative to repo root · regex limited to that file · category · reason · owner
EXCEPTIONS: list[dict] = [{'category': 'negative-test',
  'match': '\\.nika\\.ya?ml',
  'owner': 'nika-plugins',
  'path': 'scripts/suffix_ratchet.py',
  'reason': "the ratchet's own forbidden-pattern data"},
 {'category': 'negative-test',
  'match': '\\.nika\\.ya?ml',
  'owner': 'nika-plugins',
  'path': 'scripts/test_suffix_ratchet.py',
  'reason': 'mutation fixture that must keep the retired spelling to prove detection'},
 {'category': 'frozen-evidence',
  'match': '\\.nika\\.ya?ml',
  'owner': 'engine-release / scripts/resync-mirror.py',
  'path_prefix': '.agents/plugins/nika/',
  'reason': 'RELEASE-BOUND engine-mirror of tag v0.118.7; canonical plugin is engine '
            '.agents/plugins/nika. Do not hand-edit; resync after engine file-identity commit + '
            'authorized tag.'},
 {'category': 'historical',
  'match': 'SchemaStore catalog \\(\\*\\.nika\\.yaml editor association\\)',
  'owner': 'nika-plugins listings',
  'path': 'listings.yaml',
  'reason': 'record of merged SchemaStore PR 5899 fileMatch, not live first-party teaching'},
 {'category': 'historical',
  'match': 'validates \\*\\.nika\\.yaml',
  'owner': 'nika-plugins listings',
  'path': 'listings.yaml',
  'reason': 'notes the SchemaStore merge as it actually shipped'},
 {'category': 'historical',
  'match': 'linkml-triage\\.nika\\.yaml',
  'owner': 'nika-plugins listings',
  'path': 'listings.yaml',
  'reason': 'external proof artifact filename as submitted'},
 {'category': 'historical',
  'match': 'pixi-release-notes\\.nika\\.yaml',
  'owner': 'nika-plugins listings',
  'path': 'listings.yaml',
  'reason': 'external proof artifact filename as submitted'},
 {'category': 'historical',
  'match': 'anki-release-notes\\.nika\\.yaml',
  'owner': 'nika-plugins listings',
  'path': 'listings.yaml',
  'reason': 'external proof artifact filename as submitted'},
 {'category': 'historical',
  'match': 'workflow\\.nika\\.yaml',
  'owner': 'nika-plugins listings',
  'path': 'listings.yaml',
  'reason': 'OWASP DockSec payload as offered in the listing record'}]


def tracked_files() -> list[pathlib.Path]:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return [ROOT / p.decode() for p in out.stdout.split(b"\0") if p]


def exception_for(rel: str, line: str) -> dict | None:
    for exc in EXCEPTIONS:
        if "path_prefix" in exc:
            if not rel.startswith(exc["path_prefix"]):
                continue
        elif exc.get("path") != rel:
            continue
        if re.search(exc["match"], line):
            return exc
    return None


def scan() -> list[str]:
    findings: list[str] = []
    used: set[tuple[str, str]] = set()
    for path in tracked_files():
        rel = path.relative_to(ROOT).as_posix()
        if FORBIDDEN.search(rel):
            if exception_for(rel, rel) is None:
                findings.append(f"PATH {rel}: retired suffix in a tracked pathname")
            else:
                exc = exception_for(rel, rel); used.add((exc.get("path") or exc.get("path_prefix"), exc["match"]))
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, IsADirectoryError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if not FORBIDDEN.search(line):
                continue
            exc = exception_for(rel, line)
            if exc is None:
                findings.append(f"{rel}:{n}: {line.strip()[:200]}")
            else:
                used.add((exc.get("path") or exc.get("path_prefix"), exc["match"]))
    declared = set()
    for e in EXCEPTIONS:
        key = (e.get("path") or e.get("path_prefix"), e["match"])
        declared.add(key)
    stale = declared - used
    for path, match in sorted(stale):
        findings.append(f"STALE EXCEPTION {path} match={match!r} — no remaining hit")
    return findings


def main() -> int:
    planted = "this-line-must-match .nika.yaml as a scanner self-check"
    if not FORBIDDEN.search(planted):
        print("suffix-ratchet: scanner no longer matches the retired spelling", file=sys.stderr)
        return 1
    findings = scan()
    if findings:
        print("suffix-ratchet: retired .nika.yaml / .nika.yml still live:", file=sys.stderr)
        for f in findings:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("suffix-ratchet: ok — no live .nika.yaml / .nika.yml outside allowlisted exceptions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
