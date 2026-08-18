#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
#
# check-clients-matrix.py — the client × component matrix gate.
#
# clients.yaml is the SSOT of client coverage (mission nika-client-doors ·
# 2026-07-30). This gate proves, deterministically and offline by default:
#
#   1. SCHEMA      every row well-formed · cells within the closed enums ·
#                  every absent/none cell carries a reason (gaps or class_gap) ·
#                  proven rows cite a proof · recon rows ship no docs page.
#   2. MANIFESTS   class-A native-manifest rows have their adapter manifests
#                  on disk (bundle plugin.json + root marketplace.json).
#   3. COUNTS      every prose count claim ("4 skills" · "3 subagents" ·
#                  "2 rules" · "6 slash commands" · "3 hooks") in the teaching
#                  surfaces equals the count DERIVED from the bundle. This is
#                  the ratchet for the class found live 2026-07-30: the bundle
#                  grew a 6th command while three kit-native surfaces kept
#                  saying five. ("9 tools" claims stay with check-mcp-tools.py
#                  — binary truth, one home.)
#   4. WIRE        with a nika binary present (NIKA_BIN or PATH), the matrix
#                  `wire:` values and the binary's `nika wire` target list
#                  match in BOTH directions (rows with wire_pending excluded).
#   5. --upstream  the engine bundle tree holds no file the mirror does not
#                  pin (the addition-blindness class · doctor.md 2026-07-30).
#                  Network (GitHub trees API) · warns on push/PR, fails on the
#                  daily cron (GATE_EVENT=schedule) — same semantics as the
#                  upstream-drift step.

import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUNDLE = ROOT / ".agents/plugins/nika"

COMPONENT_KEYS = ("manifest", "skills", "subagents", "commands", "hooks",
                  "rules", "mcp", "presentation", "scaffold")
MECHANISMS = {"native-manifest", "agent-plugin", "claude-layout", "wire",
              "init", "mcp-config", "skill-pack", "none"}

# Agent Plugins 1.0.0 · the portable package, and the ONLY three cells it can
# fill: v1 standardises exactly two component types (§7 skills + MCP) plus the
# manifest that declares the package. A row claiming agent-plugin for hooks or
# commands would be claiming something the format refuses to carry.
AGENT_PLUGIN_FILES = {
    "manifest": ".agents/plugins/nika/plugin.json",
    "skills": ".agents/plugins/nika/skills",
    "mcp": ".agents/plugins/nika/mcp.json",
}
PORTABLE_MANIFEST = ".agents/plugins/nika/plugin.json"
CLASSES = {"A", "B", "C"}
STATUSES = {"recon", "wired", "proven"}

# class-A adapters that must exist on disk, per matrix row id
NATIVE_MANIFESTS = {
    "claude-code": [".agents/plugins/nika/.claude-plugin/plugin.json",
                    ".claude-plugin/marketplace.json"],
    "codex": [".agents/plugins/nika/.codex-plugin/plugin.json",
              ".agents/plugins/marketplace.json"],
    "cursor": [".agents/plugins/nika/.cursor-plugin/plugin.json",
               ".cursor-plugin/marketplace.json"],
}

# the teaching surfaces whose prose count claims must match the bundle
COUNT_SCAN = [
    "README.md",
    ".claude-plugin/marketplace.json",
    ".cursor-plugin/marketplace.json",
    ".agents/plugins/nika/README.md",
    ".agents/plugins/nika/.claude-plugin/plugin.json",
    ".agents/plugins/nika/.codex-plugin/plugin.json",
    ".agents/plugins/nika/.cursor-plugin/plugin.json",
    "integrations/grok-build/README.md",
    # the suite strip paints the same counts — same law, same derivation
    "media/suite-dark.svg",
    "media/suite-light.svg",
]
CLAIM_PATTERNS = {
    "skills": re.compile(r"(\d+)\s+skills?\b", re.I),
    "subagents": re.compile(r"(\d+)\s+subagents?\b", re.I),
    "rules": re.compile(r"(\d+)\s+rules?\b", re.I),
    "commands": re.compile(r"(\d+)\s+(?:slash\s+)?commands?\b", re.I),
    "hooks": re.compile(r"(\d+)\s+hooks?\b", re.I),
}


def derived_counts() -> dict:
    hooks_doc = json.loads((BUNDLE / "hooks/claude-hooks.json").read_text())
    return {
        "skills": len(list(BUNDLE.glob("skills/*/SKILL.md"))),
        "subagents": len(list(BUNDLE.glob("agents/*.md"))),
        "commands": len(list(BUNDLE.glob("commands/*.md"))),
        "rules": len(list(BUNDLE.glob("rules/*.mdc"))),
        "hooks": sum(len(v) for v in hooks_doc.get("hooks", {}).values()),
    }


def check_schema(doc, findings):
    rows = doc.get("clients")
    if doc.get("schema_version") != 1 or not rows:
        findings.append("clients.yaml: expected schema_version 1 + non-empty clients")
        return []
    seen = set()
    for row in rows:
        rid = row.get("id", "<missing id>")
        if rid in seen:
            findings.append(f"{rid}: duplicate id")
        seen.add(rid)
        if row.get("class") not in CLASSES:
            findings.append(f"{rid}: class must be one of {sorted(CLASSES)}")
        if row.get("status") not in STATUSES:
            findings.append(f"{rid}: status must be one of {sorted(STATUSES)}")
        cells = row.get("components", {})
        gaps = row.get("gaps", {}) or {}
        class_gap = row.get("class_gap")
        for key, mech in cells.items():
            if key not in COMPONENT_KEYS:
                findings.append(f"{rid}: unknown component key {key!r}")
            if not isinstance(mech, str) or mech not in MECHANISMS:
                findings.append(f"{rid}.{key}: mechanism {mech!r} outside the closed enum")
        for key in COMPONENT_KEYS:
            mech = cells.get(key)
            if mech is None or mech == "none":
                if not gaps.get(key) and not class_gap:
                    findings.append(
                        f"{rid}.{key}: absent/none without a reason "
                        f"(gaps.{key} or class_gap) — no silent caps")
        for key in gaps:
            if key not in COMPONENT_KEYS:
                findings.append(f"{rid}: gaps names unknown component {key!r}")
        if row.get("status") == "proven" and not row.get("proof"):
            findings.append(f"{rid}: proven without a proof fiche line")
        if row.get("status") == "recon":
            docs = str(row.get("docs", ""))
            if docs.endswith(".mdx"):
                findings.append(
                    f"{rid}: recon row points at a live docs page ({docs}) — "
                    f"pages ship at proven only")
        if row.get("wire") and row.get("wire_pending"):
            findings.append(f"{rid}: wire and wire_pending are exclusive")
    return rows


def check_manifests(rows, findings):
    for row in rows:
        paths = NATIVE_MANIFESTS.get(row.get("id"), [])
        for p in paths:
            if not (ROOT / p).is_file():
                findings.append(f"{row['id']}: adapter manifest missing on disk: {p}")


def check_agent_plugin(rows, findings):
    """The portable-package law, in BOTH directions.

    Forward · a cell claiming `agent-plugin` must have the file that makes the
    claim true, and must be one of the three cells the format can fill.
    Reverse · if the portable manifest is on disk, at least one row has to
    claim it. A package nobody claims is a surface we ship and never account
    for, which is the same blindness as a cell with no reason.
    """
    claimed = False
    for row in rows:
        for key, mech in (row.get("components") or {}).items():
            if mech != "agent-plugin":
                continue
            claimed = True
            if key not in AGENT_PLUGIN_FILES:
                findings.append(
                    f"{row['id']}.{key}: agent-plugin cannot fill this cell — "
                    f"Agent Plugins v1 standardises only "
                    f"{'/'.join(sorted(AGENT_PLUGIN_FILES))} (§7)")
                continue
            path = ROOT / AGENT_PLUGIN_FILES[key]
            if not path.exists():
                findings.append(
                    f"{row['id']}.{key}: claims agent-plugin but "
                    f"{AGENT_PLUGIN_FILES[key]} is not on disk")
    if (ROOT / PORTABLE_MANIFEST).is_file() and not claimed:
        findings.append(
            f"{PORTABLE_MANIFEST} ships and NO row claims agent-plugin — the "
            f"portable package reaches clients nobody accounts for "
            f"(bidirectional law)")
    return claimed


def check_counts(findings):
    derived = derived_counts()
    for rel in COUNT_SCAN:
        path = ROOT / rel
        if not path.is_file():
            findings.append(f"count scan: {rel} missing")
            continue
        text = path.read_text(encoding="utf-8")
        for kind, pat in CLAIM_PATTERNS.items():
            for m in pat.finditer(text):
                claimed = int(m.group(1))
                if claimed != derived[kind]:
                    findings.append(
                        f"{rel}: claims {claimed} {kind}, the bundle derives "
                        f"{derived[kind]} — heal the prose or the bundle")
    return derived


def wire_targets_from_binary() -> set | None:
    bin_ = os.environ.get("NIKA_BIN") or "nika"
    try:
        out = subprocess.run([bin_, "wire", "--help"], capture_output=True,
                             text=True, timeout=30).stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    # clap inline form (pre-0.107): [possible values: a, b, c]
    m = re.search(r"possible values:\s*([a-z0-9\-,\s]+)\]", out)
    if m:
        return {t.strip() for t in m.group(1).split(",") if t.strip()} - {"all"}
    # clap long form (0.107 help regroup): "Possible values:" then "- x" bullets
    m = re.search(r"Possible values:\n((?:\s*-\s+[a-z0-9\-]+\S*\n)+)", out)
    if m:
        return set(re.findall(r"^\s*-\s+([a-z0-9\-]+)",
                              m.group(1), re.M)) - {"all"}
    # The binary ANSWERED but the parse failed: a silent None here reads as
    # "no binary" and quietly kills the bidirectional wire law (found dead
    # 2026-08-02, three days after the 0.107 help regroup). Fail loud.
    raise SystemExit("check-clients-matrix: nika answered `wire --help` but "
                     "the possible-values parse failed — teach the probe the "
                     "new clap form")


def check_wire(rows, findings):
    targets = wire_targets_from_binary()
    if targets is None:
        print("  (no nika binary reachable — wire probe skipped · "
              "CI runs it against the released binary)")
        return
    declared = {row["wire"]: row["id"] for row in rows if row.get("wire")}
    for target, rid in declared.items():
        if target not in targets:
            findings.append(
                f"{rid}: wire target {target!r} not in the shipped binary "
                f"({', '.join(sorted(targets))})")
    for target in sorted(targets - set(declared)):
        findings.append(
            f"binary ships wire target {target!r} with no matrix row claiming "
            f"it — add the row (bidirectional law)")
    print(f"  wire probe: {len(targets)} binary targets ⇄ "
          f"{len(declared)} matrix rows")


def check_upstream(findings_warn):
    manifest = json.loads((ROOT / "mirror.json").read_text())
    scope = manifest.get("engine_scope", ".agents/plugins/nika/")
    repo = manifest["engine_repo"]
    known = {e.get("source", e["path"]) for e in manifest["entries"]
             if e["class"] == "engine-mirror"}
    ref = manifest.get("engine_ref", "main")  # the released tag the mirror follows
    url = f"https://api.github.com/repos/{repo}/git/trees/{ref}?recursive=1"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            tree = json.loads(resp.read())["tree"]
    except (urllib.error.URLError, TimeoutError, KeyError) as err:
        print(f"  upstream additions check skipped (trees API unreachable: {err})")
        return
    upstream = {t["path"] for t in tree
                if t["type"] == "blob" and t["path"].startswith(scope)}
    for path in sorted(upstream - known):
        findings_warn.append(
            f"engine grew {path} and the mirror does not pin it — run "
            f"scripts/resync-mirror.py (addition-blindness class)")
    for path in sorted(known - upstream):
        findings_warn.append(
            f"mirror entry source {path} no longer exists upstream — prune or "
            f"re-source the entry")
    if not (upstream - known) and not (known - upstream):
        print(f"  upstream additions: mirror covers all {len(upstream)} "
              f"bundle files under {scope}")


EVERYWHERE = ("https://raw.githubusercontent.com/supernovae-st/nika-docs/"
              "main/integrations/everywhere.mdx")


def check_everywhere(rows, findings_warn):
    """The docs map claims to be complete · prove it against this matrix.

    integrations/everywhere.mdx opens with "the complete map: every install
    path, IDE, agent, skill, plugin, CI surface, SDK and registry". Nothing
    checked that claim. When it was first checked (2026-08-07) it was short
    five of thirty-one rows, one of them a class-A client.

    `recon` rows are exempt BY THEIR STATUS, not by an allowlist: the enum
    says recon is "mechanism known from primary sources · nothing shipped or
    proven", and a map of doors that lists an unproven one turns recon into
    a claim. A row joins the page when it ships.
    """
    try:
        with urllib.request.urlopen(EVERYWHERE, timeout=30) as resp:
            page = resp.read().decode("utf-8", "replace").lower()
    except (urllib.error.URLError, TimeoutError) as err:
        print(f"  everywhere.mdx check skipped (unreachable: {err})")
        return
    owed = [r for r in rows if r.get("status") != "recon"]
    missing = []
    for row in owed:
        tokens = {row["id"], row["id"].replace("-", " "),
                  row["name"].split("·")[0].strip()}
        if not any(t and t.lower() in page for t in tokens):
            missing.append(row["id"])
    for rid in missing:
        findings_warn.append(
            f"clients.yaml row {rid!r} is shipped but everywhere.mdx does not "
            f"teach it — the page calls itself the complete map")
    exempt = len(rows) - len(owed)
    if not missing:
        print(f"  everywhere.mdx: all {len(owed)} shipped row(s) taught "
              f"({exempt} recon row(s) exempt by status)")


def main() -> int:
    upstream_mode = "--upstream" in sys.argv
    findings: list[str] = []
    doc = yaml.safe_load((ROOT / "clients.yaml").read_text())

    if upstream_mode:
        warns: list[str] = []
        check_upstream(warns)
        check_everywhere(doc.get("clients") or [], warns)
        for w in warns:
            print(f"::warning::{w}")
        if warns and os.environ.get("GATE_EVENT") == "schedule":
            print("::error::the mirror lags engine additions — re-sync is due")
            return 1
        return 0

    rows = check_schema(doc, findings)
    if rows:
        check_manifests(rows, findings)
        portable = check_agent_plugin(rows, findings)
        derived = check_counts(findings)
        check_wire(rows, findings)
        print(f"  agent-plugin: portable manifest "
              f"{'present' if (ROOT / PORTABLE_MANIFEST).is_file() else 'ABSENT'} ⇄ "
              f"{'claimed' if portable else 'UNCLAIMED'}")
        statuses = {}
        for row in rows:
            statuses[row["status"]] = statuses.get(row["status"], 0) + 1
        print(f"  matrix: {len(rows)} clients "
              f"({' · '.join(f'{v} {k}' for k, v in sorted(statuses.items()))}) · "
              f"bundle derives {derived}")
    if findings:
        print("::error::the client matrix does not hold")
        for f in findings:
            print(f"  ✗ {f}")
        return 1
    print("✓ the client matrix holds (schema · manifests · counts · wire)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
