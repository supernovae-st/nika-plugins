#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
#
# check-dead-forms.py — the kit-native half of the drift ratchet.
#
# The engine side already refuses a mirrored kit that teaches a form the
# engine rejects (nika-onboard's `the_kit_never_teaches_a_form_the_engine
# _refuses`). The kit-native surfaces here — the Hermes delegation skill,
# every integrations/ pack, the root README — had no equivalent, and they
# teach the same language to the same agents.
#
# Why it exists: the 2026-07-28 audit found the plugin teaching `vars:`,
# a scalar `workflow:`, a `tasks:` sequence and `capture: text` — three
# engine releases after each became a refusal. A file written from those
# instructions died at PARSE. Prose discipline decays; a grep does not.
#
# WHY IT WAS REPAIRED (2026-08-12). The rule set above was the 2026-07-28
# cohort and nothing else, so the language freeze went straight past it:
# measured by mutation, 16 of the 18 frozen-out forms produced a GREEN.
# The gate was not failing — it was answering a question nobody had
# updated. Three things changed:
#
#   1. THE FREEZE COHORT IS IN.   `nika: v1` + a `workflow:` envelope ·
#      `on_finally:` · `declassify:` · `inert:` · `to: trusted` ·
#      `policy:`/`prefer:`/`optimize:` · `on_error.fail_workflow` ·
#      `config:`/`types:`/`assert:` · the bare `for_each:` scalar and
#      task-level `max_parallel:`/`fail_fast:`.
#
#   2. THE ANCHOR IS THE DOCUMENT, NOT THE FILE.   An envelope key is only
#      an envelope key inside a nika workflow. The old `^env:` scanned
#      every tracked .yml, so a GitHub Actions workflow growing a
#      top-level `env:` — or this repo's own `listings.yaml`, which
#      carries a live `policy:` at column 0 — would have gone red for
#      being correct. A gate that reds correct files gets disarmed by its
#      author; that is how the wide motif kills the ratchet. Envelope
#      rules now fire only inside a fence (or a file) that a nika mark
#      identifies. See is_nika_block().
#
#   3. THE BLIND-SWEEP FLOOR NAMES ITS SURFACES.   `scanned < 5` passed
#      comfortably while the real harvest was 20 — a floor four times
#      under the truth is a formality. The floor is now the three
#      surfaces this gate exists to cover; losing any of them is RED.
#
# NOT in the walk, on purpose: *.py. The gate scripts carry these
# literals by construction, so scanning them is a guaranteed self-red,
# and the carve-out that follows is exactly the disarming this file is
# built to survive.
#
# USING a dead form is banned everywhere. NAMING one is legitimate where
# porting or history is the subject — but the language never shipped, so
# there is nothing to port FROM and no history to narrate. The exemption
# list is kept as machinery and is empty.
#
# Exit 0 = clean. Exit 1 = a dead form is being taught (file:line printed).

import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Engine-mirrored files are proven by the ENGINE's own test + the sha256
# pins in mirror.json; re-judging them here would report an upstream
# problem as a local one, and repairing one here would corrupt its pin.
SKIP_PREFIXES = (".agents/plugins/",)

WALK = ("*.md", "*.mdc", "*.yaml", "*.yml", "*.sh", "*.tape", "*.json")

# The sweep must keep reaching all three, whatever the walk does. A count
# floor rots the moment files move; a named surface does not.
ANCHOR_SURFACES = (
    ("the root README", lambda p: p == "README.md"),
    ("an integrations/ pack", lambda p: p.startswith("integrations/")),
    ("a kit-native skill", lambda p: p.startswith("skills/")),
)

FENCE = re.compile(r"^\s*(?:```|~~~)")
# What marks a block as a NIKA WORKFLOW rather than any other YAML. All
# four are nika-only at column 0 (GitHub Actions says jobs:/permissions:,
# our own registries say listings_version:/clients:). `workflow:` is in
# the list precisely because it is one of the dead forms — leave it out
# and a fence teaching the dead envelope becomes invisible to the rule
# aimed at it.
NIKA_MARK = re.compile(r"^(?:nika|tasks|permits|workflow):")

FENCE_SCOPE, PROSE_SCOPE, ANY_SCOPE = "fence", "prose", "any"


# ── A GATE MUST NOT BE AHEAD OF THE ENGINE ──────────────────────────────
#
# A dead form has TWO death dates, not one: the day the SPEC retires it,
# and the day the ENGINE refuses it. Between them, the replacement does
# not parse. A gate that enforces the spec date tells every author to
# write a file `nika check` rejects — it is not silent, it teaches the
# false, which is worse than saying nothing.
#
# Measured 2026-08-12 16:18 on nika 0.108.0, two arms:
#     nika: v1 + workflow: {id}  ⟶  rc=0   ACCEPTED (the control)
#     nika: <id>                 ⟶  rc=2   NIKA-PARSE-003
# The refusal lives in the SOURCE too (nika-schema/src/error.rs), so it is
# not a stale binary. The same day, docs/ migrated two chapters to the new
# envelope and reverted both eight minutes later.
#
# So the envelope rules below are PENDING: they warn until the engine
# takes the replacement, then they bite — and nothing has to be remembered
# on the day it lands, because the state is PROBED, never declared.
# Each pending rule names the REPLACEMENT it advises, and that
# replacement is probed on its own. One boolean would have been a lie:
# measured 2026-08-12, FOUR distinct replacements are refused, and they
# fail with three different codes.
PENDING = "pending-engine"


def pending(pat, scope, why, replacement):
    """A rule whose REPLACEMENT the engine does not accept yet."""
    return (pat, scope, why, (PENDING, replacement))


# The control. Old envelope, one read, permits declared — measured green
# on 0.108.0. Every probe below is this file plus ONE new form, so a red
# can only come from that form.
_CONTROL = """\
nika: v1
workflow:
  id: probe-control
const:
  p: "./x.txt"
permits:
  tools: ["nika:read"]
  fs:
    read: ["./x.txt"]
tasks:
  t:
    invoke:
      tool: "nika:read"
      args: { path: "${{ const.p }}" }
"""

_OLD_HEAD = 'nika: v1\nworkflow:\n  id: probe-control\n'

# replacement key -> the file that uses it. Measured 2026-08-12 · 0.108.0:
#   envelope-id   NIKA-PARSE-003  the value is exactly `v1`
#   lift          NIKA-PARSE-005  unknown field `lift` (task AND envelope)
#   after-unwind  NIKA-DAG-005    `unwind` is not a predicate · set is closed
_PROBES = {
    "envelope-id": _CONTROL.replace(_OLD_HEAD, "nika: probe-new-envelope\n"),
    "lift": _CONTROL + '    lift:\n      - law: taint\n'
                       '        from: t\n        because: "probe"\n',
    "after-unwind": _CONTROL + '  cleanup:\n    after: { t: unwind }\n'
                               '    invoke:\n      tool: "nika:read"\n'
                               '      args: { path: "${{ const.p }}" }\n',
}

_probe_cache: dict = {}


# NIKA_BIN is the repo's convention for "the binary this CI actually
# downloaded" (check-mcp-tools.py · check-skill-commands.py ·
# check-clients-matrix.py all read it). The released binary is the right
# reference for a TEACHING surface: what a reader installs is what has to
# accept what they were taught.
def _nika() -> str:
    return os.environ.get("NIKA_BIN") or "nika"


def _rc(text: str):
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        f = pathlib.Path(d) / "probe.nika.yaml"
        f.write_text(text)
        try:
            return subprocess.run([_nika(), "check", str(f)],
                                  capture_output=True, timeout=60).returncode
        except (OSError, subprocess.SubprocessError):
            return None


def engine_accepts(replacement):
    """True (parses) · False (refused) · None (could not ask).

    The control runs first. If the OLD form is not green the probe cannot
    see, so it answers None rather than guess — an instrument has to be
    qualified before its verdict counts, and a gate owes that to its own
    premise as much as a measurement does.
    """
    if replacement in _probe_cache:
        return _probe_cache[replacement]
    import shutil
    verdict = None
    have = pathlib.Path(_nika()).exists() or shutil.which(_nika()) is not None
    if have and _rc(_CONTROL) == 0:
        verdict = _rc(_PROBES[replacement]) == 0
    _probe_cache[replacement] = verdict
    return verdict


# (regex, scope, why[, PENDING]) — scope decides WHERE the literal counts
# as a teaching act. ANY = the literal is unambiguous wherever it appears.
RULES = [
    # ---- expressions and values · unambiguous anywhere -----------------
    (re.compile(r"\$\{\{\s*vars\."), ANY_SCOPE,
     "the vars namespace is dead — read inputs: or const:"),
    (re.compile(r"\$\{\{\s*env\."), ANY_SCOPE,
     "the env namespace is dead — read secrets: (a non-secret knob is an "
     "inputs: entry with a default:)"),
    (re.compile(r"\bcapture:\s*text\b"), ANY_SCOPE,
     "capture is stdout · stderr · combined · structured"),
    (re.compile(r":\s*succeeded\b"), ANY_SCOPE,
     "NIKA-DAG-005 · the predicate is `success`"),
    (re.compile(r":\s*failed\b"), ANY_SCOPE,
     "NIKA-DAG-005 · the predicate is `failure`"),

    # ---- the freeze · forms with no live homonym, so ANY --------------
    pending(re.compile(r"\bon_finally\b"), ANY_SCOPE,
     "on_finally: is dead — cleanup is a task on an unwind edge, "
     "`after: {producer: unwind}`", "after-unwind"),
    pending(re.compile(r"\bdeclassify\b"), ANY_SCOPE,
     "declassify: is dead — the one authored door is `lift:` "
     "(`- law: taint` · `from:` · `because:`)", "lift"),
    (re.compile(r"\bfail_workflow\b"), ANY_SCOPE,
     "on_error.fail_workflow is dead — 3 modes became 2 (`recover:` · "
     "`skip:`); failing IS the default"),
    pending(re.compile(r"\bto:\s*trusted\b"), ANY_SCOPE,
     "`to: trusted` is dead — a raise is a `lift:` entry naming its law",
            "lift"),
    # `inert` is also an English word this repo uses correctly ("the grant
    # sits inert"). The key form is what dies, so the anchor is key
    # position — line start, or inside backticks. Without that anchor this
    # rule reds the README for a sentence.
    pending(re.compile(r"(?:^\s*|`)inert:"), ANY_SCOPE,
     "inert: is dead — the data-as-code door is `lift:` "
     "(`- law: data-as-code` · `because:`)", "lift"),

    # ---- the freeze · envelope keys · only inside a nika document -----
    # PENDING · dissolving this block requires `nika: <id>`, which the
    # engine refuses today. See engine_takes_new_envelope().
    pending(re.compile(r"^workflow:"), FENCE_SCOPE,
            "the `workflow:` envelope is dead — `nika: <id>` IS the mark and "
            "the name (an `invoke:` target keeps its own `workflow:` key)",
            "envelope-id"),
    (re.compile(r"^vars:"), FENCE_SCOPE,
     "the vars envelope block is dead — inputs: / const:"),
    (re.compile(r"^env:"), FENCE_SCOPE,
     "the env envelope block is dead — secrets:, or an inputs: entry with "
     "a default: (an INDENTED env: under permits: is alive)"),
    (re.compile(r"^config:"), FENCE_SCOPE,
     "the config envelope block is dead — a deployment knob is an inputs: "
     "entry with required: false and a default:"),
    (re.compile(r"^types:"), FENCE_SCOPE,
     "the types envelope block is dead"),
    (re.compile(r"^assert:"), FENCE_SCOPE,
     "the assert envelope block is dead (the `nika:assert` builtin is alive "
     "and is a different thing)"),
    (re.compile(r"^policy:"), FENCE_SCOPE,
     "the policy envelope block is dead"),
    (re.compile(r"^\s*(?:prefer|optimize):"), FENCE_SCOPE,
     "prefer:/optimize: died with the policy: block"),
    # PENDING · the replacement IS the form the engine rejects. This is the
    # rule the two-arm probe was written for.
    pending(re.compile(r"^nika:\s*[\"']?v?[0-9]"), FENCE_SCOPE,
            "`nika:` carries the workflow ID, never a version — "
            "`nika: my-flow-id`", "envelope-id"),
    # There is no bare `for_each: <expr>` form — one construct, one
    # spelling: for_each: { items:, max_parallel:, fail_fast: }.
    (re.compile(r"^\s*for_each:\s*\S"), FENCE_SCOPE,
     "the bare `for_each: <expr>` scalar is dead — the block carries "
     "items: (plus optional max_parallel: / fail_fast:)"),

    # ---- the freeze · teaching mentions in prose ----------------------
    # No prose rule for `workflow:` (alive inside invoke:), `env:` (alive
    # under permits:), `max_parallel:`/`fail_fast:` (alive as for_each
    # sub-fields). Those three are caught by position, not by name.
    pending(re.compile(r"`nika:\s*[\"']?v?[0-9]"), PROSE_SCOPE,
            "`nika:` carries the workflow ID, never a version", "envelope-id"),
    (re.compile(r"`config:`"), PROSE_SCOPE,
     "the config: block is dead — classify into inputs: / const: / secrets:"),
    (re.compile(r"`types:`"), PROSE_SCOPE, "the types: block is dead"),
    (re.compile(r"`assert:`"), PROSE_SCOPE, "the assert: block is dead"),
    (re.compile(r"`policy:`"), PROSE_SCOPE, "the policy: block is dead"),
    (re.compile(r"`prefer:`|`optimize:`"), PROSE_SCOPE,
     "prefer:/optimize: died with the policy: block"),
    (re.compile(r"`vars:`"), PROSE_SCOPE,
     "the vars: block is dead — classify into inputs: / const:"),
    (re.compile(r"`depends_on`"), PROSE_SCOPE,
     "dead edge form — with: / after:"),
]

# Machinery kept, deliberately empty: the language never shipped, so no
# surface has porting or history as its subject.
MAY_NAME_THE_RETIRED: set = set()


def tracked_teaching_files() -> list:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", *WALK],
                         text=True, capture_output=True, check=True)
    return [p for p in out.stdout.splitlines()
            if p and not p.startswith(SKIP_PREFIXES)]


def is_nika_block(body: list) -> bool:
    return any(NIKA_MARK.match(line) for line in body)


def fence_lines(rel: str, lines: list) -> set:
    """1-based line numbers that sit inside a NIKA WORKFLOW document."""
    if rel.endswith((".nika.yaml", ".nika.yml")):
        return set(range(1, len(lines) + 1))
    if rel.endswith((".yaml", ".yml")):
        # A whole registry/CI file is a nika document only if it carries a
        # nika mark at column 0. listings.yaml (live `policy:`) and every
        # GitHub Actions workflow fail that test, which is the point.
        return set(range(1, len(lines) + 1)) if is_nika_block(lines) else set()
    inside, start, body, out = False, 0, [], set()
    for n, line in enumerate(lines, 1):
        if FENCE.match(line):
            if inside and is_nika_block(body):
                out.update(range(start + 1, n))
            inside, start, body = not inside, n, []
        elif inside:
            body.append(line)
    return out


def loop_misplacement(lines: list, in_fence: set) -> list:
    """max_parallel:/fail_fast: are alive INSIDE a for_each: block only.

    They were task-level fields before the freeze; a line regex cannot see
    nesting, so this walks indentation instead.
    """
    hits, block_indent = [], None
    for n, line in enumerate(lines, 1):
        if n not in in_fence or not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        m = re.match(r"^(\s*)for_each:\s*$", line)
        if m:
            block_indent = indent
            continue
        if block_indent is not None and indent <= block_indent:
            block_indent = None
        if re.match(r"^\s*(?:max_parallel|fail_fast):", line):
            if block_indent is None or indent <= block_indent:
                hits.append((n, "max_parallel:/fail_fast: are sub-fields of "
                                "the for_each: block, never task-level"))
    return hits


def main() -> int:
    failed = False
    held: dict = {}
    swept = tracked_teaching_files()
    for rel in swept:
        lines = (ROOT / rel).read_text().splitlines()
        in_fence = fence_lines(rel, lines)
        findings = []
        for rule in RULES:
            pat, scope, why = rule[0], rule[1], rule[2]
            # A rule is HELD only while the engine refuses the exact
            # replacement it advises. Each key is probed once, on its own.
            repl = rule[3][1] if len(rule) > 3 and rule[3][0] == PENDING \
                else None
            if scope == PROSE_SCOPE and rel in MAY_NAME_THE_RETIRED:
                continue
            for n, line in enumerate(lines, 1):
                if scope == FENCE_SCOPE and n not in in_fence:
                    continue
                if scope == PROSE_SCOPE and n in in_fence:
                    continue
                if pat.search(line):
                    findings.append((n, why, repl))
        findings += [(n, why, None) for n, why in
                     loop_misplacement(lines, in_fence)]
        for n, why, repl in sorted(findings, key=lambda f: f[0]):
            waived = repl is not None and engine_accepts(repl) is not True
            if waived:
                held[repl] = held.get(repl, 0) + 1
            else:
                failed = True
            print(f"{'⚠' if waived else '✗'} {rel}:{n} — {why}",
                  file=sys.stderr)
            print(f"    {lines[n - 1].strip()[:110]}", file=sys.stderr)
    if held:
        # A held finding has two possible reasons and they are NOT the same
        # claim: the engine was ASKED and refused, or it could not be asked
        # at all. Printing "the engine refuses" for the second is the very
        # dishonesty this mechanism exists to remove, one level up.
        rows = " · ".join(f"{k} ×{v}" for k, v in sorted(held.items()))
        unasked = [k for k in held if engine_accepts(k) is None]
        if unasked:
            why = (f"the replacement could not be probed — no runnable "
                   f"`{_nika()}` (set NIKA_BIN). Holding is the safe side, "
                   f"but this hold is a DEFAULT, not a measurement")
        else:
            why = ("the engine was asked and REFUSES the replacement they "
                   "advise, so migrating now would teach a form `nika "
                   "check` rejects")
        print(f"\n⚠ {sum(held.values())} finding(s) HELD, not enforced "
              f"({rows}) — {why}. Nothing has to be remembered on the day "
              f"it lands: the state is PROBED, never declared, so each of "
              f"these bites by itself the moment its replacement parses.",
              file=sys.stderr)
    if failed:
        print("\na kit-native surface teaches a form the engine refuses — "
              "fix the teaching, never the engine", file=sys.stderr)
        return 1
    # An empty sweep prints the same ✓ as a clean one, so the sweep has to
    # prove it still reaches the surfaces this gate exists for.
    missing = [name for name, hit in ANCHOR_SURFACES
               if not any(hit(p) for p in swept)]
    if missing:
        print(f"✗ the sweep no longer reaches {' · '.join(missing)} — the "
              f"walk moved and this gate is blind rather than satisfied "
              f"({len(swept)} file(s) swept)", file=sys.stderr)
        return 1
    print(f"✓ no dead language forms across {len(swept)} kit-native "
          f"teaching files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
