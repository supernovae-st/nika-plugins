#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Mutation and alias proofs for the bounded old-suffix ratchet."""
from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suffix_ratchet as ratchet


class SuffixRatchet(unittest.TestCase):
    def test_scanner_flags_retired_suffix_and_aliases(self):
        self.assertTrue(ratchet.content_hit_lines("flows/report.nika.yaml"))
        self.assertTrue(ratchet.content_hit_lines("flows/report.nika.yml"))
        self.assertTrue(ratchet.content_hit_lines("glob *.nika.yaml"))
        self.assertTrue(ratchet.content_hit_lines("regex " + r"\.nika\.yaml"))
        self.assertTrue(ratchet.content_hit_lines("brace " + ".nika.{yaml,yml}"))
        self.assertFalse(ratchet.content_hit_lines("flows/report.nika"))
        self.assertFalse(ratchet.content_hit_lines("project file is nika.yaml"))
        self.assertFalse(ratchet.content_hit_lines(".nika/traces/run.ndjson"))

    def test_escaped_alias_is_detected_without_plain_spelling(self):
        line = "pattern " + r"\.nika\.yaml"
        self.assertNotIn(".nika.yaml", line)
        self.assertTrue(ratchet.content_hit_lines(line), line)

    def test_brace_alias_is_detected_without_plain_spelling(self):
        line = "forms " + ".nika.{yaml,yml}"
        self.assertNotIn(".nika.yaml", line)
        self.assertTrue(ratchet.content_hit_lines(line), line)

    def test_planted_live_file_is_detected(self):
        exceptions, _ = ratchet.load_exceptions()
        findings = ratchet.scan(
            exceptions,
            extra_paths=["scripts/_planted.md"],
            overlay={"scripts/_planted.md": "nika check hello.nika.yaml\n"},
        )
        self.assertTrue(any("hello.nika.yaml" in f for f in findings), findings)

    def test_canonical_and_project_names_are_clean(self):
        exceptions, _ = ratchet.load_exceptions()
        findings = ratchet.scan(
            exceptions,
            extra_paths=["scripts/_clean.md"],
            overlay={
                "scripts/_clean.md": (
                    "nika check hello.nika\nproject file is nika.yaml\nruntime is .nika/\n"
                )
            },
        )
        self.assertFalse(any("scripts/_clean.md" in f for f in findings), findings)

    def test_mutation_inside_allowlisted_file_is_red(self):
        exceptions, cfg = ratchet.load_exceptions()
        inject = cfg["inject_path"]
        original = (ratchet.ROOT / inject).read_text(encoding="utf-8")
        findings = ratchet.scan(
            exceptions,
            overlay={inject: original + "\nnew live teaching: foo.nika.yaml\n"},
        )
        self.assertTrue(
            any(
                inject in f
                and ("foo.nika.yaml" in f or "hit count" in f or "hash mismatch" in f or "digest mismatch" in f)
                for f in findings
            ),
            findings,
        )

    def test_new_file_under_no_directory_exemption_is_red(self):
        exceptions, cfg = ratchet.load_exceptions()
        new_file = cfg.get("new_prefix_file") or cfg["new_file"]
        findings = ratchet.scan(
            exceptions,
            extra_paths=[new_file],
            overlay={new_file: "historical leftover foo.nika.yaml\n"},
        )
        self.assertTrue(any(new_file in f for f in findings), findings)


if __name__ == "__main__":
    unittest.main()
