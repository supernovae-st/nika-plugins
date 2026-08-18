#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
#
# resync-mirror.py — the re-sync ritual as one command. The mirror follows
# the engine at `mirror.json.engine_ref` — the RELEASED tag (the stable
# train · what a user installs), never engine main. When the daily cron
# goes loud ("a newer engine release exists"), run this with `--ref
# <tag>`: it fetches every engine-mirror file at that ref, rewrites the
# local bytes, recomputes the sha256 pins, and stamps the ref + the engine
# SHA the sync was proven against. Review the diff, commit. Never hand-edit
# a mirrored file or a pin.
#
# Why the released tag and not main (2026-08-18): the kit is TEACHING —
# what an agent generates. Mirrored from main it taught the 0.109 language
# (the nine-key name envelope · three authorities) to users whose brew
# binary was 0.108.0 (`nika: v1` + `workflow:` · four authorities): every
# marketplace install generated files the shipped binary refused, while the
# gate's own binary-truth checks ran against that same released binary.
# One identity per train: the mirror, the marketplace version and the
# binary the gate judges with are the SAME release.
#
#   python3 scripts/resync-mirror.py                 # re-sync at engine_ref
#   python3 scripts/resync-mirror.py --ref v0.109.0  # move the mirror to a newer release
#   python3 scripts/resync-mirror.py --dry           # show what would change
#   python3 scripts/resync-mirror.py --engine <dir>  # sync from a local clone
#   NIKA_ENGINE_CLONE=<dir> python3 scripts/resync-mirror.py   # same, via env
#
# Resilience (each rule earned by a live failure, 2026-07-12):
# - A local clone is FETCHED before it is read (git fetch origin main) —
#   an unfetched clone pins pre-merge bytes and stamps a stale SHA, and
#   the versions-agree gate only catches it one CI round later.
# - The raw API rate-limits (HTTP 403/429) mid-run. With a local clone
#   available the script FALLS BACK to it automatically; without one it
#   names the exact remedy instead of dying half-synced.
# - Bytes and the stamped SHA always come from the SAME source.

import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = "https://raw.githubusercontent.com/{repo}/{ref}/{path}"
API = "https://api.github.com/repos/{repo}/commits/{ref}"
TAG_RE = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$")


class Source:
    """Where mirror bytes come from — the engine at ONE ref (a release tag ·
    `mirror.json.engine_ref`), read over the raw API or from a fetched
    local clone. Bytes and the stamped SHA always come from the same ref."""

    def __init__(self, repo: str, ref: str, clone: pathlib.Path | None):
        self.repo = repo
        self.ref = ref
        self.clone = clone
        if clone is not None:
            self._fetch_clone()

    def _fetch_clone(self) -> None:
        # The stale-clone trap: reading a ref without fetching pins
        # yesterday's bytes. Fetch is mandatory, not polite — the tag too
        # (a clone made before the release has never seen it).
        r = subprocess.run(
            ["git", "-C", str(self.clone), "fetch", "--quiet", "origin", self.ref],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            sys.exit(f"engine clone at {self.clone}: git fetch {self.ref} failed: {r.stderr.strip()}")

    @classmethod
    def resolve(cls, repo: str, ref: str, argv: list[str]) -> "Source":
        clone = None
        if "--engine" in argv:
            clone = pathlib.Path(argv[argv.index("--engine") + 1])
        elif os.environ.get("NIKA_ENGINE_CLONE"):
            clone = pathlib.Path(os.environ["NIKA_ENGINE_CLONE"])
        if clone is not None and not (clone / ".git").exists():
            sys.exit(f"--engine {clone}: not a git clone")
        return cls(repo, ref, clone)

    def _rev(self) -> str:
        # A tag resolves to the commit it points at (peeled), a sha to itself.
        return f"{self.ref}^{{commit}}"

    def head(self) -> str:
        if self.clone is not None:
            r = subprocess.run(
                ["git", "-C", str(self.clone), "rev-parse", self._rev()],
                capture_output=True, text=True, check=True,
            )
            return r.stdout.strip()
        with urllib.request.urlopen(API.format(repo=self.repo, ref=self.ref), timeout=30) as resp:
            return json.loads(resp.read())["sha"]

    def read(self, path: str) -> bytes:
        if self.clone is not None:
            r = subprocess.run(
                ["git", "-C", str(self.clone), "show", f"{self._rev()}:{path}"],
                capture_output=True,
            )
            if r.returncode != 0:
                sys.exit(f"engine clone: {self.ref}:{path} unreadable")
            return r.stdout
        with urllib.request.urlopen(RAW.format(repo=self.repo, ref=self.ref, path=path), timeout=30) as resp:
            return resp.read()

    def ls(self, prefix: str) -> list[str]:
        """Every blob under prefix at the ref — clone ls-tree or trees API."""
        if self.clone is not None:
            r = subprocess.run(
                ["git", "-C", str(self.clone), "ls-tree", "-r", "--name-only",
                 self._rev(), prefix],
                capture_output=True, text=True, check=True,
            )
            return [p for p in r.stdout.splitlines() if p]
        url = f"https://api.github.com/repos/{self.repo}/git/trees/{self.ref}?recursive=1"
        with urllib.request.urlopen(url, timeout=30) as resp:
            tree = json.loads(resp.read())["tree"]
        return [t["path"] for t in tree
                if t["type"] == "blob" and t["path"].startswith(prefix)]

    def try_local_fallback(self) -> bool:
        """Rate-limited mid-run: switch to a discoverable clone if one exists."""
        for candidate in (
            os.environ.get("NIKA_ENGINE_CLONE"),
            str(ROOT.parent / "nika"),          # sibling checkout
        ):
            if candidate and (pathlib.Path(candidate) / ".git").exists():
                self.clone = pathlib.Path(candidate)
                self._fetch_clone()
                print(f"  ! raw API rate-limited — continuing from the local clone at {self.clone}")
                return True
        return False


def main() -> int:
    # Strict argv — this tool REWRITES bytes by default, so a guessed flag
    # (a `--check` that does not exist) must fail loud, never fall through
    # to the mutating path. Earned live 2026-07-14.
    args = sys.argv[1:]
    i = 0
    ref_arg = None
    while i < len(args):
        if args[i] == "--engine":
            if i + 1 == len(args):
                sys.exit("usage: resync-mirror.py [--dry] [--ref <tag>] [--engine <dir>] — --engine needs a path")
            i += 2
        elif args[i] == "--ref":
            if i + 1 == len(args):
                sys.exit("usage: resync-mirror.py [--dry] [--ref <tag>] [--engine <dir>] — --ref needs a release tag")
            ref_arg = args[i + 1]
            i += 2
        elif args[i] == "--dry":
            i += 1
        else:
            sys.exit(f"unknown flag {args[i]!r} — usage: resync-mirror.py [--dry] [--ref <tag>] [--engine <dir>]")
    dry = "--dry" in sys.argv
    manifest_path = ROOT / "mirror.json"
    manifest = json.loads(manifest_path.read_text())
    # One canonical stamp field — a hand-rolled sync once wrote a stray
    # sibling key; drop any impostor so the manifest never carries two truths.
    manifest.pop("engine_sha", None)
    repo = manifest["engine_repo"]
    # The ref the mirror follows: a RELEASE tag (the stable train). `--ref`
    # moves it (the release heal's move · a human's deliberate one); a ref
    # that is not a release tag is refused — `main` is the next train and
    # teaches a language the shipped binary may not speak.
    ref = ref_arg or manifest.get("engine_ref")
    if not ref:
        sys.exit("mirror.json carries no engine_ref and no --ref was given — the mirror follows a RELEASE tag, never main")
    if not TAG_RE.match(ref):
        sys.exit(f"engine_ref {ref!r} is not a release tag (vX.Y.Z) — the mirror follows the released engine, never a branch")
    if ref != manifest.get("engine_ref"):
        print(f"  → engine_ref {manifest.get('engine_ref')} → {ref}")
        if not dry:
            manifest["engine_ref"] = ref
    source = Source.resolve(repo, ref, sys.argv)

    changed = 0
    for e in manifest["entries"]:
        if e["class"] != "engine-mirror":
            continue
        path = e.get("source", e["path"])
        try:
            upstream = source.read(path)
        except urllib.error.HTTPError as err:
            if err.code in (403, 429) and source.try_local_fallback():
                upstream = source.read(path)
            else:
                sys.exit(
                    f"raw API answered {err.code} on {path} and no local clone "
                    f"was found — re-run with --engine <path-to-nika-clone> "
                    f"(or set NIKA_ENGINE_CLONE)"
                )
        digest = hashlib.sha256(upstream).hexdigest()
        local = ROOT / e["path"]
        same_bytes = local.is_file() and local.read_bytes() == upstream
        same_pin = e["sha256"] == digest
        if same_bytes and same_pin:
            print(f"  = {e['path']}")
            continue
        changed += 1
        print(f"  ~ {e['path']}  pin {e['sha256'][:9]} → {digest[:9]}"
              f"{'' if same_bytes else '  (bytes updated)'}")
        if not dry:
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_bytes(upstream)
            if str(local).endswith(".sh"):
                local.chmod(0o755)
            e["sha256"] = digest

    # Addition-blindness ratchet (earned 2026-07-30: the engine grew
    # commands/doctor.md and the walk above — entries-only — never saw it,
    # while the mirrored manifests already announced six commands). The
    # engine bundle scope must be FULLY covered: an upstream file without
    # an entry is mirrored + pinned on the spot; an entry whose source
    # vanished upstream is named loud (pruning stays a human move).
    scope = manifest.setdefault("engine_scope", ".agents/plugins/nika/")
    upstream_set = set(source.ls(scope))
    known = {e.get("source", e["path"]) for e in manifest["entries"]
             if e["class"] == "engine-mirror"}
    for path in sorted(upstream_set - known):
        upstream = source.read(path)
        digest = hashlib.sha256(upstream).hexdigest()
        changed += 1
        print(f"  + {path}  (new upstream file → mirrored + pinned {digest[:9]})")
        if not dry:
            local = ROOT / path
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_bytes(upstream)
            if str(local).endswith(".sh"):
                local.chmod(0o755)
            manifest["entries"].append(
                {"class": "engine-mirror", "path": path, "sha256": digest})
    # A kit-native file whose path EXISTS at the ref is a mirror candidate
    # (the portable Agent Plugins pair reached the engine kit after the
    # v0.108.0 tag and rides here as kit-native until the first release
    # that carries it): named loud, the class flip stays a human move.
    for e in manifest["entries"]:
        if e["class"] == "kit-native" and e["path"].startswith(scope) and e["path"] in upstream_set:
            print(f"  ! {e['path']}: kit-native here but PRESENT at engine {ref} — "
                  f"flip its class to engine-mirror (drop the note) and re-run")
    for path in sorted(p for p in known
                       if p.startswith(scope) and p not in upstream_set):
        print(f"  ! {path}: entry source no longer exists at engine {ref} — "
              f"prune or re-source the entry (left untouched)")

    head = source.head()
    stamp_moved = (manifest.get("synced_at_engine_sha") != head
                   or json.loads(manifest_path.read_text()).get("engine_ref") != ref)
    if (changed or stamp_moved) and not dry:
        manifest["synced_at_engine_sha"] = head
        manifest_path.write_text(json.dumps(manifest, indent=2,
                                            ensure_ascii=False) + "\n")
        print(f"re-pinned {changed} file(s) at engine {ref} ({head[:9]}) — review the "
              f"diff, then commit")
    elif changed or stamp_moved:
        print(f"--dry: {changed} file(s) would re-sync (engine {ref} · {head[:9]})")
    else:
        # A clean pass still heals a polluted stamp field.
        if not dry and json.loads(manifest_path.read_text()).get("engine_sha") is not None:
            manifest_path.write_text(json.dumps(manifest, indent=2,
                                                ensure_ascii=False) + "\n")
        print(f"mirror already current with engine {ref} ({head[:9]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
