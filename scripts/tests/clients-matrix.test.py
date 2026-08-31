#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
#
# Mutation proof for the agent-plugin law in check-clients-matrix.py.
#
# A gate nobody has seen fail is decoration. This copies the repo to a
# scratch tree, breaks the portable-package claim one way at a time, and
# asserts the gate goes RED for each break — in BOTH directions:
#
#   forward · a cell claiming `agent-plugin` must have the file that makes
#             the claim true, and must be one of the three cells Agent
#             Plugins v1 can fill (manifest · skills · mcp · §7)
#   reverse · if the portable manifest ships, some row must claim it, or we
#             are shipping a surface nobody accounts for
#
# Two controls guard the proof itself. The pristine tree must be GREEN, so
# a gate that always failed could not pass; and the YAML round-trip alone
# must be GREEN, so a mutation that never lands cannot look like a kill.
# That second control was earned: the first version of this file edited
# clients.yaml as text, produced a duplicate `mcp` key, and YAML kept the
# last one — the mutation silently did not apply and the case passed for
# free.
#
# Exit: 0 all mutations killed · 1 one survived.

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
GATE = "scripts/check-clients-matrix.py"
BUNDLE = ".agents/plugins/nika"

# vscode is the row that carries the portable claim (PRIMARY-verified
# 2026-08-07). If that ever moves, this constant moves with it.
ROW = "vscode"
CELLS = {"manifest": "agent-plugin", "skills": "agent-plugin",
         "mcp": "wire", "scaffold": "init"}


def gate(tree: pathlib.Path) -> int:
    return subprocess.run([sys.executable, GATE], cwd=tree,
                          capture_output=True, text=True).returncode


def set_cells(tree: pathlib.Path, cells: dict) -> None:
    """Rewrite the row's components through the YAML loader, never as text."""
    path = tree / "clients.yaml"
    doc = yaml.safe_load(path.read_text())
    for row in doc["clients"]:
        if row["id"] == ROW:
            row["components"] = cells
    with path.open("w") as fh:
        yaml.safe_dump(doc, fh, allow_unicode=True, sort_keys=False)


def replace_text(path: pathlib.Path, old: str, new: str) -> None:
    text = path.read_text()
    if old not in text:
        raise AssertionError(f"mutation anchor absent: {old}")
    path.write_text(text.replace(old, new, 1))


def main() -> int:
    fails = 0
    total = 0
    print("clients-matrix · agent-plugin mutation proof")

    with tempfile.TemporaryDirectory() as work:
        base = pathlib.Path(work) / "base"
        shutil.copytree(ROOT, base,
                        ignore=shutil.ignore_patterns(".git", "__pycache__"))

        def case(label: str, want: str, mutate) -> None:
            nonlocal fails, total
            total += 1
            tree = pathlib.Path(work) / f"case{total}"
            shutil.rmtree(tree, ignore_errors=True)
            shutil.copytree(base, tree)
            mutate(tree)
            rc = gate(tree)
            got = "GREEN" if rc == 0 else "RED"
            if got != want:
                fails += 1
            print(f"  {'ok  ' if got == want else 'FAIL'} {label}  ({got}, rc={rc})")

        case("pristine tree", "GREEN", lambda t: None)
        case("yaml round-trip alone (control)", "GREEN",
             lambda t: set_cells(t, dict(CELLS)))
        case("agent-plugin on hooks · a cell v1 cannot fill", "RED",
             lambda t: set_cells(t, {**CELLS, "hooks": "agent-plugin"}))
        case("claims manifest · plugin.json deleted", "RED",
             lambda t: (t / BUNDLE / "plugin.json").unlink())
        case("claims mcp · mcp.json deleted", "RED",
             lambda t: (set_cells(t, {**CELLS, "mcp": "agent-plugin"}),
                        (t / BUNDLE / "mcp.json").unlink()))
        case("claims skills · skills/ deleted", "RED",
             lambda t: shutil.rmtree(t / BUNDLE / "skills"))
        case("plugin.json ships · NO row claims it", "RED",
             lambda t: set_cells(t, {"manifest": "native-manifest",
                                     "skills": "native-manifest",
                                     "mcp": "wire", "scaffold": "init"}))
        case("claude desktop reclaims retired MCPB install", "RED",
             lambda t: replace_text(
                 t / "clients.yaml",
                 "install the current engine via Homebrew or a verified release archive · then nika wire claude-desktop",
                 "one-click .mcpb bundle (release assets)"))
        case("README promises MCPB on every release", "RED",
             lambda t: replace_text(
                 t / "integrations/mcp/README.md",
                 "MCPB is a historical distribution lane",
                 "MCPB hosts: every engine release ships bundles"))

    if fails:
        print(f"\n{fails}/{total} mutation(s) survived — the gate does not "
              f"catch what it claims.", file=sys.stderr)
        return 1
    print(f"\n{total}/{total} mutations killed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
