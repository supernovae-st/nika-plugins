#!/usr/bin/env python3
"""Mutation proof for concise first-contact help and door probes."""

import importlib.util
import contextlib
import io
import os
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

# A real subcommand does not prove a retired argument form works. This stub
# accepts `new --help`, so only the teaching-form gate can reject the fixture.
with tempfile.TemporaryDirectory() as tmp:
    root = pathlib.Path(tmp)
    binary = root / "nika"
    binary.write_text("#!/bin/sh\nexit 0\n")
    binary.chmod(0o755)
    md = root / "SKILL.md"
    saved_root, saved_paths = MODULE.ROOT, MODULE.kit_native_paths
    saved_binary = os.environ.get("NIKA_BIN")
    MODULE.ROOT, MODULE.kit_native_paths = root, lambda: [md]
    os.environ["NIKA_BIN"] = str(binary)
    try:
        for form in [
            "`nika new --from '?'`",
            "`nika new --from`",
            "`nika new --from=chain flow.nika.yaml`",
            '```\nterminal(command="nika new flow.nika.yaml --from chain")\n```',
            "```sh\nnika new --force --from chain flow.nika.yaml\n```",
        ]:
            md.write_text(form)
            stderr = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                code = MODULE.main()
            assert code == 1, f"retired form slipped green: {form}"
            assert "--from" in stderr.getvalue(), stderr.getvalue()
        for form in [
            "- `nika new --from ...` is obsolete here. Use positional intent and destination;",
            "`nika new '?'`", "`nika new chain flow.nika.yaml`",
            "```sh\nnika new 'summarize a page' flow.nika.yaml --force\n```",
            "`nika run flow.nika.yaml --from task`",
            "```sh\nnika new chain flow.nika.yaml; nika run flow.nika.yaml --from task\n```",
        ]:
            md.write_text(form)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                assert MODULE.main() == 0, f"valid form rejected: {form}"
    finally:
        MODULE.ROOT, MODULE.kit_native_paths = saved_root, saved_paths
        if saved_binary is None:
            os.environ.pop("NIKA_BIN", None)
        else:
            os.environ["NIKA_BIN"] = saved_binary

print("skill command retired-form rejection: PASS")
