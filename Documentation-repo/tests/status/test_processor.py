import tempfile
import unittest
from datetime import date
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "status"))

import processor


def marked_status(manual="Project setup"):
    return (
        "# Project Status\n\n"
        f"{processor.MANUAL_START}\n\n"
        f"{manual}\n\n"
        f"{processor.MANUAL_END}\n"
    )


class StatusProcessorTests(unittest.TestCase):

    def test_empty_project_generates_status(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "PROJECT_STATUS.md").write_text(marked_status())

            result = processor.build_status(root)

            self.assertIn("# Project Status", result)
            self.assertIn("## Project Timeline", result)
            self.assertIn("No records currently available.", result)
            self.assertIn(processor.MANUAL_START, result)
            self.assertIn(processor.MANUAL_END, result)

    def test_activity_uses_event_date_not_updated(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "PROJECT_STATUS.md").write_text(marked_status())
            development = root / "development"
            development.mkdir()
            (development / "ACT-001.md").write_text(
                "---\n"
                "id: ACT-001\n"
                "type: activity\n"
                "title: Test activity\n"
                "status: Draft\n"
                "date: 2026-10-03\n"
                "updated: 2026-11-01\n"
                "---\n\n"
                "# ACT-001 - Test activity\n",
                encoding="utf-8",
            )

            records = processor.load_records(
                root,
                [("development", "ACT-*.md", "activity")],
            )

            self.assertEqual(records[0]["event_date"], date(2026, 10, 3))
            self.assertEqual(records[0]["updated"], date(2026, 11, 1))

    def test_manual_content_is_preserved_exactly(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manual = "## Current Phase\n\n  Custom text\n\n- keep | formatting"
            original = marked_status(manual)
            status = root / "PROJECT_STATUS.md"
            status.write_text(original)

            result = processor.build_status(root)

            extracted = processor.extract_manual_content(result)
            self.assertEqual(extracted, "\n\n" + manual + "\n\n")

    def test_missing_manual_marker_is_critical(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            status = root / "PROJECT_STATUS.md"
            status.write_text("# Project Status\n")

            with self.assertRaises(processor.CriticalStatusError):
                processor.build_status(root)

    def test_duplicate_manual_marker_is_critical(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            status = root / "PROJECT_STATUS.md"
            status.write_text(
                marked_status() + processor.MANUAL_START + "\n" + processor.MANUAL_END
            )

            with self.assertRaises(processor.CriticalStatusError):
                processor.build_status(root)

    def test_malformed_marker_order_is_critical(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            status = root / "PROJECT_STATUS.md"
            status.write_text(
                processor.MANUAL_END + "\n" + processor.MANUAL_START
            )

            with self.assertRaises(processor.CriticalStatusError):
                processor.build_status(root)

    def test_missing_id_and_invalid_date_are_warnings(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "PROJECT_STATUS.md").write_text(marked_status())
            development = root / "development"
            development.mkdir()
            (development / "bad.md").write_text(
                "---\ntype: activity\ntitle: Broken\ndate: 2026-99-99\nupdated: nope\n---\n",
                encoding="utf-8",
            )

            records = processor.load_records(
                root,
                [("development", "*.md", "activity")],
            )

            self.assertIsNone(records[0]["id"])
            self.assertIn("Missing ID", records[0]["warnings"])
            self.assertTrue(
                any("Invalid date" in warning for warning in records[0]["warnings"])
            )

    def test_duplicate_ids_are_flagged(self):
        records = [
            {"id": "REQ-001"},
            {"id": "REQ-001"},
            {"id": "REQ-002"},
        ]
        duplicate_ids = processor.duplicate_ids(records)
        self.assertIn("REQ-001", duplicate_ids)
        self.assertNotIn("REQ-002", duplicate_ids)

    def test_explicit_and_inferred_relationships_are_distinguished(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            records = [
                {
                    "id": "REQ-001",
                    "path": root / "REQ-001.md",
                    "text": (
                        "LoRa engineering requirement; propagation model\n\n"
                        "## Related Records\n\nDEC-001"
                    ),
                    "category": "requirement",
                },
                {
                    "id": "DEC-001",
                    "path": root / "DEC-001.md",
                    "text": "LoRa engineering decision; propagation model",
                    "category": "decision",
                },
                {
                    "id": "FIND-001",
                    "path": root / "FIND-001.md",
                    "text": "LoRa propagation investigation",
                    "category": "research",
                },
            ]
            explicit, inferred = processor.find_relationships(records, root)

            self.assertTrue(explicit)
            self.assertTrue(
                all("Unverified Suggestion" not in item["evidence"] for item in explicit)
            )
            self.assertTrue(inferred)
            self.assertIn("Shared terminology", inferred[0]["reason"])

    def test_internal_link_resolution_and_broken_link(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.md"
            target = root / "ACT-001.md"
            target.write_text("# ACT-001")

            state, found = processor.resolve_internal_link(root, source, "ACT-001.md")
            self.assertEqual(state, "resolved")
            self.assertEqual(found, target)

            state, _ = processor.resolve_internal_link(root, source, "missing.md")
            self.assertEqual(state, "broken")

    def test_external_link_statuses_are_classified_without_blocking(self):
        self.assertIn(
            "Successful",
            processor.check_external_link_status(200),
        )
        self.assertEqual(
            processor.check_external_link_status(403),
            "Access restricted (HTTP 403)",
        )
        self.assertEqual(
            processor.check_external_link_status(404),
            "Confirmed broken link (HTTP 404)",
        )

    def test_build_status_does_not_write_permanent_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = marked_status("Manual\n")
            status = root / "PROJECT_STATUS.md"
            status.write_text(original)

            processor.build_status(root)

            self.assertEqual(status.read_text(), original)

    def test_missing_invalid_and_malformed_dates_are_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "PROJECT_STATUS.md").write_text(marked_status())
            development = root / "development"
            development.mkdir()
            (development / "ACT-001.md").write_text(
                "---\nid: ACT-001\ntitle: Invalid date\nstatus: Draft\n"
                "date: 2026-02-30\n---\n",
                encoding="utf-8",
            )
            (development / "ACT-002.md").write_text(
                "---\nid ACT-002\ntitle: Malformed\nstatus: Draft\n---\n",
                encoding="utf-8",
            )
            result = processor.build_status(root)
            self.assertIn("2026-02-30", result)
            self.assertIn("Invalid:", result)
            self.assertIn("ACT-002", result)

    def test_internal_link_ambiguity_and_repair(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "a").mkdir()
            (root / "b").mkdir()
            (root / "a" / "ACT-001.md").write_text("# A")
            (root / "b" / "ACT-001.md").write_text("# B")
            source = root / "source.md"
            state, _ = processor.resolve_internal_link(root, source, "ACT-001.md")
            self.assertEqual(state, "ambiguous")

            only = root / "ACT-002.md"
            only.write_text("# ACT-002")
            state, target = processor.resolve_internal_link(
                root, source, "elsewhere/ACT-002.md"
            )
            self.assertEqual(state, "repairable")
            self.assertEqual(target, only)

    def test_external_link_timeout_and_inconclusive_failures(self):
        with patch.object(processor.urllib.request, "urlopen", side_effect=TimeoutError()):
            self.assertEqual(processor.check_external_link("https://example.test"), "Timeout")

        with patch.object(processor.urllib.request, "urlopen", side_effect=OSError("dns")):
            result = processor.check_external_link("https://example.test")
            self.assertIn("Temporary", result)

    def test_record_id_in_prose_is_not_explicit_relationship(self):
        records = [{
            "id": "REQ-001",
            "path": Path("/tmp/REQ-001.md"),
            "text": "DEC-001 appears only in explanatory prose",
            "front": {},
            "category": "requirement",
        }]
        explicit, _ = processor.find_relationships(records, Path("/tmp"))
        self.assertEqual(explicit, [])

    def test_explicit_relationship_section_and_reference_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "PROJECT_STATUS.md").write_text(marked_status())
            research = root / "research" / "findings"
            research.mkdir(parents=True)
            (research / "FIND-001.md").write_text(
                "---\n"
                "id: FIND-001\n"
                "title: LoRa investigation\n"
                "status: Draft\n"
                "date: 2026-10-10\n"
                "references: REF-001, REF-002\n"
                "---\n\n"
                "## Investigation\n\nMeasured range.\n\n"
                "## Findings\n\nRange was dependent on terrain.\n\n"
                "## Conclusions\n\nLoRa was suitable for testing.\n",
                encoding="utf-8",
            )
            result = processor.build_status(root)
            self.assertIn("Measured range", result)
            self.assertIn("REF-001", result)
            self.assertIn("REF-002", result)

    def test_feature_and_master_have_separate_reference_lists(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "PROJECT_STATUS.md").write_text(marked_status())
            features = root / "features"
            master = root / "master"
            features.mkdir()
            master.mkdir()
            (features / "V1.md").write_text(
                "---\nid: FV-001\ntitle: V1\nstatus: Draft\n"
                "updated: 2026-10-10\nreferences: REF-001\n---\n",
                encoding="utf-8",
            )
            (master / "MASTER-001.md").write_text(
                "---\nid: MAS-001\ntitle: Master\nstatus: Draft\n"
                "updated: 2026-10-11\nreferences: REF-002\n---\n",
                encoding="utf-8",
            )
            result = processor.build_status(root)
            self.assertIn("FV-001 references:** REF-001", result)
            self.assertIn("Master MAS-001 references:** REF-002", result)

    def test_generated_report_validation_and_repeat_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            status = root / "PROJECT_STATUS.md"
            status.write_text(marked_status("Keep this exactly"))

            first = processor.build_status(root)
            processor.write_status(root, first)
            second = processor.build_status(root)

            self.assertEqual(first, second)
            self.assertIn("Keep this exactly", first)
            with self.assertRaises(processor.CriticalStatusError):
                processor.validate_generated_report("# Wrong\n")

    def test_git_history_preserves_rename_branch_and_merge_context(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            import subprocess
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root)
            (root / "Documentation-repo").mkdir()
            old = root / "Documentation-repo" / "old.md"
            old.write_text("old")
            subprocess.run(["git", "add", "."], cwd=root)
            subprocess.run(["git", "commit", "-q", "-m", "docs: initial"], cwd=root)
            subprocess.run(["git", "mv", str(old), str(root / "Documentation-repo" / "new.md")], cwd=root)
            subprocess.run(["git", "commit", "-q", "-m", "docs: rename record"], cwd=root)
            subprocess.run(["git", "branch", "project-work"], cwd=root)

            commits, error = processor.get_git_history(root)

            self.assertIsNone(error)
            rename_commit = next(c for c in commits if "rename" in c["subject"])
            self.assertEqual(rename_commit["branches"], ["main", "project-work"])
            self.assertTrue(any(change_type.startswith("R") for _, change_type in rename_commit["changed"]))

    def test_git_history_contains_merge_and_changed_types(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            import subprocess
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root)
            (root / "a.txt").write_text("a")
            subprocess.run(["git", "add", "."], cwd=root)
            subprocess.run(["git", "commit", "-q", "-m", "docs: initial"], cwd=root)

            commits, error = processor.get_git_history(root)

            self.assertIsNone(error)
            self.assertTrue(commits)
            self.assertEqual(commits[0]["subject"], "docs: initial")
            self.assertTrue(commits[0]["changed"])


if __name__ == "__main__":
    unittest.main()
