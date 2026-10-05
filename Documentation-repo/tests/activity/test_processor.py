import unittest
from datetime import datetime, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "activity"))

import processor


def commit(minutes, branch="main", sha="abcdef1234567890", subject="test"):
    return {
        "sha": sha,
        "time": datetime(2026, 10, 5, 10, 0) + timedelta(minutes=minutes),
        "branch": branch,
        "subject": subject,
    }


class ActivityProcessorTests(unittest.TestCase):

    def test_groups_commits_within_60_minutes_on_same_branch(self):
        commits = [
            commit(0, sha="aaa1111"),
            commit(30, sha="bbb2222"),
        ]

        groups = processor.group_commits(commits)

        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 2)

    def test_splits_commits_after_60_minutes(self):
        commits = [
            commit(0, sha="aaa1111"),
            commit(61, sha="bbb2222"),
        ]

        groups = processor.group_commits(commits)

        self.assertEqual(len(groups), 2)

    def test_splits_different_branches(self):
        commits = [
            commit(0, branch="main", sha="aaa1111"),
            commit(10, branch="feature/test", sha="bbb2222"),
        ]

        groups = processor.group_commits(commits)

        self.assertEqual(len(groups), 2)

    def test_60_minute_boundary_is_same_session(self):
        commits = [
            commit(0, sha="aaa1111"),
            commit(60, sha="bbb2222"),
        ]

        groups = processor.group_commits(commits)

        self.assertEqual(len(groups), 1)

    def test_activity_contains_git_evidence(self):
        commits = [
            commit(
                0,
                sha="abcdef1234567890",
                subject="add activity automation",
            )
        ]

        result = processor.make_activity(1, commits)

        self.assertIn("ACT-001", result)
        self.assertIn("abcdef1", result)
        self.assertIn("add activity automation", result)
        self.assertIn("Branch: main", result)
        self.assertIn("Status: Draft", result)


if __name__ == "__main__":
    unittest.main()
