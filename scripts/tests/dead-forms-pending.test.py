#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
#
# Mutation proof for the PENDING mechanism in check-dead-forms.py.
#
# The mechanism makes a promise that is cheap to write and expensive to
# get wrong: "a rule whose replacement the engine refuses is HELD, and it
# bites BY ITSELF the day the engine takes it." A bug in it fails silently
# and in the worst direction — every pending rule waived forever, on a
# gate that still prints a reassuring summary.
#
# So the promise is tested in BOTH directions, which is the only way a
# waiver mechanism can be proven:
#
#   the HOLD · engine refuses the replacement  ⟶  ⚠, and it does NOT
#              contribute to the exit code
#   the BITE · engine accepts the replacement  ⟶  ✗, and it DOES
#
# Two controls guard the proof itself. A rule that is NOT pending must go
# red in both worlds (otherwise "held" could just mean "never fired"), and
# the probe must answer None — never a guess — when its own control is not
# green, because an instrument has to be qualified before its verdict
# counts.
#
# Run · python3 scripts/tests/dead-forms-pending.test.py

import importlib.util
import io
import pathlib
import re
import sys
from contextlib import redirect_stderr

GATE = pathlib.Path(__file__).resolve().parent.parent / "check-dead-forms.py"

# A finding line is `<glyph> path:line — why`. The SUMMARY line also opens
# with the warning glyph and also carries an em dash, so a naive
# startswith() counted it as a fourteenth finding and the conservation
# check failed on the instrument, not on the mechanism. Anchor on the
# `path:line` shape instead.
FINDING = re.compile(r"^[⚠✗] \S+:\d+ ")


def findings(text: str, glyph: str) -> list:
    return [l for l in text.splitlines()
            if FINDING.match(l) and l.startswith(glyph)]

spec = importlib.util.spec_from_file_location("deadforms", GATE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

FAILURES = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'ok      ' if ok else 'FAILED  '}{label}"
          f"{'   <-- ' + detail if detail and not ok else ''}")
    if not ok:
        FAILURES.append(label)


def run_with(verdicts: dict):
    """Run the gate with the probe pre-answered. Returns (rc, stderr)."""
    mod._probe_cache.clear()
    mod._probe_cache.update(verdicts)
    err = io.StringIO()
    with redirect_stderr(err):
        rc = mod.main()
    mod._probe_cache.clear()
    return rc, err.getvalue()


ALL_KEYS = list(mod._PROBES)

print("== the HOLD · engine refuses every replacement")
rc_hold, out_hold = run_with({k: False for k in ALL_KEYS})
held = findings(out_hold, "⚠")
hard = findings(out_hold, "✗")
check("pending findings are HELD, not refused", len(held) > 0,
      "nothing was held — the mechanism never fired")
check("the summary names the held replacements",
      "HELD, not enforced" in out_hold)
check("a NON-pending form still refuses (control)", len(hard) > 0,
      "everything was waived — a gate that holds all is a gate that is off")

print()
print("== the BITE · engine accepts every replacement")
rc_bite, out_bite = run_with({k: True for k in ALL_KEYS})
held_b = findings(out_bite, "⚠")
hard_b = findings(out_bite, "✗")
check("nothing is held once the engine accepts", len(held_b) == 0,
      f"{len(held_b)} still held — the rule would NEVER bite")
check("the held findings became refusals", len(hard_b) > len(hard),
      f"{len(hard_b)} vs {len(hard)} — they vanished instead of biting")
check("held + refused is conserved across the two worlds",
      len(hard_b) == len(hard) + len(held),
      f"{len(hard_b)} != {len(hard)} + {len(held)}")
check("the exit code is still red", rc_bite == 1)

print()
print("== the probe refuses to guess when it cannot see")
real_rc = mod._rc
try:
    mod._rc = lambda text: 2            # even the CONTROL comes back red
    mod._probe_cache.clear()
    v = mod.engine_accepts("envelope-id")
    check("an unqualified probe answers None, never False/True", v is None,
          f"answered {v!r} — it guessed")
finally:
    mod._rc = real_rc
    mod._probe_cache.clear()

rc_unknown, out_unknown = run_with({k: None for k in ALL_KEYS})
check("an unknown verdict HOLDS (warning is the safe side)",
      len(findings(out_unknown, "⚠")) > 0)

print()
print("== the measured world · what the binary actually says today")
mod._probe_cache.clear()
live = {k: mod.engine_accepts(k) for k in ALL_KEYS}
for k, v in live.items():
    state = {True: "ACCEPTS", False: "refuses", None: "unaskable"}[v]
    print(f"  {k:<14} {state}")
check("the probe reached a verdict for every replacement",
      all(v is not None for v in live.values()),
      "no `nika` on PATH · the hold is correct but unmeasured here")

print()
if FAILURES:
    print(f"FAILED · {len(FAILURES)} check(s): {' · '.join(FAILURES)}")
    sys.exit(1)
print("ok · the hold holds, and the bite bites")
