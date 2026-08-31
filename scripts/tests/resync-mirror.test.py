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

    changed = MODULE.align_marketplace_versions("0.116.0")
    assert changed == 2, f"expected two aligned manifests, got {changed}"
    for relative in MODULE.MARKETPLACE_MANIFESTS:
        document = json.loads((root / relative).read_text())
        assert document["plugins"][0]["version"] == "0.116.0"

    unchanged = MODULE.align_marketplace_versions("0.116.0")
    assert unchanged == 0, f"idempotence failed: {unchanged} change(s)"

    cursor = root / ".cursor-plugin/marketplace.json"
    cursor.write_text(json.dumps({"plugins": []}) + "\n")
    try:
        MODULE.align_marketplace_versions("0.116.0")
    except SystemExit as error:
        assert "exactly one nika plugin entry" in str(error)
    else:
        raise AssertionError("missing nika entry did not fail closed")

print("resync mirror marketplace alignment: PASS")
