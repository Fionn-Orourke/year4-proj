import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "status"))

import processor


class StatusProcessorTests(unittest.TestCase):

    def test_empty_project_generates_status(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            result = processor.build_status(root)

            self.assertIn("# Project Status", result)
            self.assertIn("Project setup", result)
            self.assertIn("## Recent Decisions", result)

    def test_activity_is_included(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            development = root / "development"
            development.mkdir()

            (development / "ACT-001.md").write_text(
                """---
id: ACT-001
type: activity
title: Test activity
status: Draft
created: 2026-10-05
updated: 2026-10-05
---

# ACT-001 - Test activity
""",
                encoding="utf-8",
            )

            result = processor.build_status(root)

            self.assertIn("ACT-001", result)
            self.assertIn("Test activity", result)

    def test_does_not_modify_permanent_status(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            status = root / "PROJECT_STATUS.md"
            original = "# Human project status\n"
            status.write_text(original, encoding="utf-8")

            processor.build_status(root)

            self.assertEqual(
                status.read_text(encoding="utf-8"),
                original,
            )


if __name__ == "__main__":
    unittest.main()