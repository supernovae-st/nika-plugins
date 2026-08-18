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
# The probe must also SURVIVE THE FLIP (added 2026-08-19). Measured on a
# 0.109.0 build: with a control written in the fourteen-key envelope, the
# nine-key engine refused the control itself, every probe answered None,
# every PENDING rule was waived, and the summary blamed a missing binary.
# So three stub binaries — one per world, zero real engine — pin the
# contract: a NINE-KEY-ONLY binary answers True for every replacement and
# waives NOTHING; a FOURTEEN-KEY-ONLY binary answers False (the 0.108.0
# hold, unchanged); a binary that accepts NEITHER head answers None and
# the summary says so (unqualified · not "no binary").
#
# Run · python3 scripts/tests/dead-forms-pending.test.py

import importlib.util
import io
import os
import pathlib
import stat
import tempfile
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


def reset_probes() -> None:
    mod._probe_cache.clear()
    getattr(mod, "_base_cache", {}).clear()


def run_with(verdicts: dict):
    """Run the gate with the probe pre-answered. Returns (rc, stderr)."""
    reset_probes()
    mod._probe_cache.update(verdicts)
    err = io.StringIO()
    with redirect_stderr(err):
        rc = mod.main()
    reset_probes()
    return rc, err.getvalue()



FIXTURE = """# Control fixture · a teaching surface that names a dead block.
#
# `config:` is NOT pending — no probe can waive it — so it must go red in
# BOTH worlds. Planting it here rather than reading it off the repo keeps
# the control true whatever the tree looks like.
The `config:` block is dead.
"""


def run_over_fixture(verdicts: dict):
    """Run the gate over a one-file synthetic tree. Returns (rc, stderr)."""
    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        rel = "FIXTURE.md"
        (root / rel).write_text(FIXTURE)
        real_root, real_files = mod.ROOT, mod.tracked_teaching_files
        mod.ROOT = root
        mod.tracked_teaching_files = lambda: [rel]
        try:
            return run_with(verdicts)
        finally:
            mod.ROOT, mod.tracked_teaching_files = real_root, real_files


# The replacement keys the gate probes (`_PROBE_KEYS` since the flip
# repair; the pre-repair gate exposed them as the `_PROBES` dict — reading
# either lets this file judge both, which is what a mutation proof needs).
ALL_KEYS = list(getattr(mod, "_PROBE_KEYS", None) or mod._PROBES)

print("== the HOLD · engine refuses every replacement")
rc_hold, out_hold = run_with({k: False for k in ALL_KEYS})
held = findings(out_hold, "⚠")
hard = findings(out_hold, "✗")
check("pending findings are HELD, not refused", len(held) > 0,
      "nothing was held — the mechanism never fired")
check("the summary names the held replacements",
      "HELD, not enforced" in out_hold)
# The control needs a NON-pending dead form to be REFUSED even when every
# probe says "the engine rejects the replacement". It used to read that
# form off the repo itself — which made the proof depend on the tree
# staying dirty. It stopped being true the day the last real violation was
# fixed, and the control failed for the one reason that is not a bug: the
# surface got clean. A control that a repair can break is not a control.
# So it carries its OWN fixture now, and asserts on that alone.
rc_ctl, out_ctl = run_over_fixture({k: False for k in ALL_KEYS})
hard_ctl = findings(out_ctl, "\u2717")
check("a NON-pending form still refuses (control)", len(hard_ctl) > 0,
      "everything was waived — a gate that holds all is a gate that is off")
check("the control's refusal is the one the fixture plants",
      any("config:" in l for l in hard_ctl),
      f"got {hard_ctl!r} — the fixture's `config:` line did not fire")

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
print("== the flip · a stub binary per world, zero real engine")
# One PENDING form per replacement key, planted so the fixture is true
# whatever the tree looks like: `\`nika: v1\`` in prose (envelope-id),
# `declassify` (lift), `on_finally` (after-unwind).
FLIP_FIXTURE = """# Flip fixture · a teaching surface that names three PENDING forms.
The `nika: v1` head is dead. `declassify:` is dead. `on_finally:` is dead.
"""
# The stub judges `check <file>` from ONE rule: which envelope head it
# accepts. What a real engine ALSO judges is spelled out so a probe that
# adds a dead form to an accepted head still fails on the right binary:
# the nine-key engine refuses `workflow:` at column 0 (NIKA-PARSE-005);
# the fourteen-key engine refuses `lift:` and `unwind` (the new-only
# forms). Modes: new (0.109.0+) · old (0.108.0) · none (accepts neither).
STUB = r"""#!/usr/bin/env python3
import re, sys
MODE = "%(mode)s"
argv = sys.argv[1:]
path = next((a for a in argv[1:] if not a.startswith("-")), None)
text = open(path, encoding="utf-8").read() if path else ""
first = text.split("\n", 1)[0]
head_new = re.match(r"^nika:\s*[a-z][a-z0-9-]*\s*$", first) is not None
head_old = text.startswith("nika: v1\nworkflow:\n")
new_only = ("lift:" in text) or ("unwind" in text)
old_only = re.search(r"^workflow:", text, re.M) is not None
if MODE == "none":
    sys.exit(2)
if MODE == "new":
    sys.exit(0 if (head_new and not old_only) else 2)
if MODE == "old":
    sys.exit(0 if (head_old and not new_only) else 2)
sys.exit(2)
"""


def with_stub(mode: str):
    """Run the gate over the flip fixture with a stub `nika` in NIKA_BIN.

    Returns (verdicts, rc, stderr) — the verdicts are the LIVE answers the
    probe gave that binary (nothing pre-answered).
    """
    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        bin_path = root / "nika"
        bin_path.write_text(STUB % {"mode": mode})
        bin_path.chmod(bin_path.stat().st_mode | stat.S_IXUSR)
        # The synthetic tree carries the three ANCHOR surfaces by name, so
        # the exit code below is the findings' and not the blind-sweep
        # floor's. The fixture sits in the README; the other two are inert.
        rels = ["README.md", "integrations/flip/README.md",
                "skills/flip/SKILL.md"]
        for rel in rels:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(FLIP_FIXTURE if rel == "README.md"
                                    else "# inert anchor\n")
        saved_env = os.environ.get("NIKA_BIN")
        real_root, real_files = mod.ROOT, mod.tracked_teaching_files
        os.environ["NIKA_BIN"] = str(bin_path)
        mod.ROOT = root
        mod.tracked_teaching_files = lambda: list(rels)
        try:
            reset_probes()
            verdicts = {k: mod.engine_accepts(k) for k in ALL_KEYS}
            err = io.StringIO()
            with redirect_stderr(err):
                rc = mod.main()
            return verdicts, rc, err.getvalue()
        finally:
            mod.ROOT, mod.tracked_teaching_files = real_root, real_files
            if saved_env is None:
                os.environ.pop("NIKA_BIN", None)
            else:
                os.environ["NIKA_BIN"] = saved_env
            reset_probes()


v_new, rc_new, out_new = with_stub("new")
check("a nine-key-only binary answers True for every replacement",
      all(v is True for v in v_new.values()),
      f"got {v_new!r} — the control did not survive the flip")
check("on that binary NO pending rule is waived",
      len(findings(out_new, "⚠")) == 0,
      f"{len(findings(out_new, '⚠'))} still held — the gate is blind at the flip")
check("on that binary every planted pending form BITES",
      len(findings(out_new, "✗")) == 3 and rc_new == 1,
      f"{len(findings(out_new, '✗'))} refusal(s), rc={rc_new}")

v_old, rc_old, out_old = with_stub("old")
check("a fourteen-key-only binary answers False for every replacement",
      all(v is False for v in v_old.values()),
      f"got {v_old!r} — the 0.108.0 hold changed")
check("on that binary the planted forms are HELD and the summary says "
      "the engine REFUSES",
      len(findings(out_old, "⚠")) == 3 and rc_old == 0
      and "asked and REFUSES" in out_old,
      f"{len(findings(out_old, '⚠'))} held, rc={rc_old}")

v_none, rc_none, out_none = with_stub("none")
check("a binary that accepts neither head answers None for every replacement",
      all(v is None for v in v_none.values()),
      f"got {v_none!r} — it guessed")
check("that hold is reported as UNQUALIFIED, not as a missing binary",
      "accepts NEITHER control head" in out_none
      and "no runnable" not in out_none,
      "the summary blamed a missing binary that was right there")

print()
print("== the measured world · what the binary actually says today")
reset_probes()
live = {k: mod.engine_accepts(k) for k in ALL_KEYS}
for k, v in live.items():
    state = {True: "ACCEPTS", False: "refuses", None: "unaskable"}[v]
    print(f"  {k:<14} {state}")
check("the probe reached a verdict for every replacement",
      all(v is not None for v in live.values()),
      "no `nika` on PATH · the hold is correct but unmeasured here")
# The three replacements arrived TOGETHER (the nine-key envelope · `lift:`
# · the unwind edge · 0.109.0). So on an engine that takes the nine-key
# head, a `refuses` on lift or after-unwind is a malformed PROBE (the
# empty-room lift shape did exactly that, measured 2026-08-19), never the
# engine — and a malformed probe HOLDS its rules forever with an honest-
# looking summary. Skipped on a fourteen-key engine, where all three
# refuse for real.
if live.get("envelope-id") is True:
    check("on a nine-key engine every advised replacement is live "
          "(a `refuses` here is a malformed probe)",
          all(v is True for v in live.values()),
          f"got {live!r} — re-shape the probe, the engine took the flip")

print()
if FAILURES:
    print(f"FAILED · {len(FAILURES)} check(s): {' · '.join(FAILURES)}")
    sys.exit(1)
print("ok · the hold holds, and the bite bites")
