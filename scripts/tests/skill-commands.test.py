#!/usr/bin/env python3
"""Mutation proof for concise first-contact help and door probes."""

import importlib.util
import pathlib
import tempfile


SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "check-skill-commands.py"
SPEC = importlib.util.spec_from_file_location("check_skill_commands", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


with tempfile.TemporaryDirectory() as tmp:
    binary = pathlib.Path(tmp) / "nika"
    binary.write_text("""#!/bin/sh
if [ "$1" = "--help" ]; then
  printf '%s\n' 'nika             a plan from a file' 'nika doctor      PATH, model, sandbox'
  exit 0
fi
if [ "$1" = "doctor" ] && [ "$2" = "--help" ]; then exit 0; fi
exit 2
""")
    binary.chmod(0o755)

    shipped = MODULE.shipped_subcommands(str(binary))
    assert shipped == set(), f"concise help parsed phantom commands: {shipped}"
    cache = {}
    assert MODULE.quiet_door_ships(str(binary), "doctor", cache)
    assert not MODULE.quiet_door_ships(str(binary), "ghost", cache)

print("skill command concise-help probes: PASS")
