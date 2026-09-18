#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Mutation proof: a planted live old suffix is detected."""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import suffix_ratchet as ratchet


class SuffixRatchet(unittest.TestCase):
    def test_scanner_flags_retired_suffix(self):
        self.assertRegex("flows/report.nika.yaml", ratchet.FORBIDDEN)
        self.assertRegex("flows/report.nika.yml", ratchet.FORBIDDEN)
        self.assertIsNone(ratchet.FORBIDDEN.search("flows/report.nika"))
        self.assertIsNone(ratchet.FORBIDDEN.search("nika.yaml"))
        self.assertIsNone(ratchet.FORBIDDEN.search(".nika/traces/run.ndjson"))

    def test_planted_live_file_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            planted = root / "live.md"
            planted.write_text("nika check hello.nika.yaml\n", encoding="utf-8")
            with mock.patch.object(ratchet, "ROOT", root), mock.patch.object(
                ratchet, "tracked_files", lambda: [planted]
            ), mock.patch.object(ratchet, "EXCEPTIONS", []):
                findings = ratchet.scan()
        self.assertTrue(any("hello.nika.yaml" in f for f in findings), findings)

    def test_canonical_and_project_names_are_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            page = root / "README.md"
            page.write_text(
                "nika check hello.nika\nproject file is nika.yaml\nruntime is .nika/\n",
                encoding="utf-8",
            )
            with mock.patch.object(ratchet, "ROOT", root), mock.patch.object(
                ratchet, "tracked_files", lambda: [page]
            ), mock.patch.object(ratchet, "EXCEPTIONS", []):
                self.assertEqual(ratchet.scan(), [])


if __name__ == "__main__":
    unittest.main()
