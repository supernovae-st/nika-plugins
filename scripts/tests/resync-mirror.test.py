#!/usr/bin/env python3
"""Mutation proof for the release mirror's kit-native version alignment."""

import importlib.util
import json
import pathlib
import tempfile


SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "resync-mirror.py"
SPEC = importlib.util.spec_from_file_location("resync_mirror", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def marketplace(version: str) -> dict:
    return {"plugins": [{"name": "nika", "version": version}]}


with tempfile.TemporaryDirectory() as tmp:
    root = pathlib.Path(tmp)
    MODULE.ROOT = root
    for relative in MODULE.MARKETPLACE_MANIFESTS:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(marketplace("0.115.0")) + "\n")
    dockerfile = root / MODULE.DOCKERFILE
    dockerfile.parent.mkdir(parents=True, exist_ok=True)
    dockerfile.write_text(
        "# --build-arg NIKA_VERSION=0.115.0\n"
        "ARG NIKA_VERSION=0.115.0\n"
    )

    changed = MODULE.align_marketplace_versions("0.116.0")
    assert changed == 2, f"expected two aligned manifests, got {changed}"
    for relative in MODULE.MARKETPLACE_MANIFESTS:
        document = json.loads((root / relative).read_text())
        assert document["plugins"][0]["version"] == "0.116.0"

    unchanged = MODULE.align_marketplace_versions("0.116.0")
    assert unchanged == 0, f"idempotence failed: {unchanged} change(s)"

    docker_changed = MODULE.align_docker_version("0.116.0")
    assert docker_changed == 1, "expected the Docker default to align"
    assert dockerfile.read_text().count("NIKA_VERSION=0.116.0") == 2
    assert MODULE.align_docker_version("0.116.0") == 0, "Docker alignment is not idempotent"

    dockerfile.write_text("ARG NIKA_VERSION=0.115.0\n")
    try:
        MODULE.align_docker_version("0.116.0")
    except SystemExit as error:
        assert "exactly two NIKA_VERSION surfaces" in str(error)
    else:
        raise AssertionError("a missing Docker version surface did not fail closed")

    cursor = root / ".cursor-plugin/marketplace.json"
    cursor.write_text(json.dumps({"plugins": []}) + "\n")
    try:
        MODULE.align_marketplace_versions("0.116.0")
    except SystemExit as error:
        assert "exactly one nika plugin entry" in str(error)
    else:
        raise AssertionError("missing nika entry did not fail closed")

print("resync mirror marketplace alignment: PASS")

# A retired engine-mirror path (commands/new.md at v0.120.0) must be a
# prune warning under --dry, not a hard abort. The local retired file stays.
import contextlib
import io
import os
import subprocess
import sys


def _git(cwd: pathlib.Path, *args: str) -> None:
    env = {**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.com",
           "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.com"}
    subprocess.check_call(["git", "-C", str(cwd), *args], env=env,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    engine = tmp / "engine"
    plugin = engine / ".agents/plugins/nika"
    plugin.mkdir(parents=True)
    (plugin / "plugin.json").write_text('{"version": "0.120.0"}\n')
    (plugin / "keep.md").write_text("keep\n")
    _git(engine, "init")
    _git(engine, "add", ".")
    _git(engine, "commit", "-m", "kit")
    _git(engine, "tag", "v0.120.0")
    origin = tmp / "engine.git"
    subprocess.check_call(["git", "clone", "--bare", "--quiet", str(engine), str(origin)])
    _git(engine, "remote", "add", "origin", str(origin))

    kit = tmp / "kit"
    MODULE.ROOT = kit
    (kit / ".agents/plugins/nika/commands").mkdir(parents=True)
    (kit / ".agents/plugins/nika/keep.md").write_text("stale-keep\n")
    retired = kit / ".agents/plugins/nika/commands/new.md"
    retired.write_text("retired-bytes\n")
    retired_bytes = retired.read_bytes()
    (kit / ".claude-plugin").mkdir()
    (kit / ".cursor-plugin").mkdir()
    for relative in MODULE.MARKETPLACE_MANIFESTS:
        (kit / relative).write_text(json.dumps(marketplace("0.118.7")) + "\n")
    dockerfile = kit / MODULE.DOCKERFILE
    dockerfile.parent.mkdir(parents=True, exist_ok=True)
    dockerfile.write_text(
        "# --build-arg NIKA_VERSION=0.118.7\n"
        "ARG NIKA_VERSION=0.118.7\n"
    )
    digest = "0" * 64
    manifest = {
        "engine_repo": "supernovae-st/nika",
        "engine_ref": "v0.118.7",
        "engine_scope": ".agents/plugins/nika/",
        "synced_at_engine_sha": "deadbeef",
        "entries": [
            {"class": "engine-mirror", "path": ".agents/plugins/nika/keep.md",
             "sha256": digest},
            {"class": "engine-mirror",
             "path": ".agents/plugins/nika/commands/new.md",
             "sha256": digest},
        ],
    }
    (kit / "mirror.json").write_text(json.dumps(manifest) + "\n")

    saved_argv = sys.argv
    sys.argv = [str(SCRIPT), "--dry", "--ref", "v0.120.0", "--engine", str(engine)]
    stdout = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout):
            code = MODULE.main()
    finally:
        sys.argv = saved_argv
    output = stdout.getvalue()
    assert code == 0, output
    assert "commands/new.md" in output and "no longer exists" in output, output
    assert retired.read_bytes() == retired_bytes, "retired local bytes mutated under --dry"
    assert "keep.md" in output, output

print("resync mirror vanished engine-mirror path is prune-warn, not abort: PASS")
