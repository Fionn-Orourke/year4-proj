import argparse
import re
import subprocess
from datetime import datetime
from pathlib import Path

SESSION_GAP_MINUTES = 60
GENERATED_PREFIX = "docs: generate activity"


def run_git(root, *args):
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def parse_commit(line):
    sha, timestamp, subject = line.split("|", 2)
    return {
        "sha": sha,
        "time": datetime.fromisoformat(timestamp),
        "subject": subject,
    }


def next_id(development):
    ids = []

    for path in development.glob("ACT-*.md"):
        match = re.match(r"ACT-(\d+)\.md$", path.name)
        if match:
            ids.append(int(match.group(1)))

    return max(ids, default=0) + 1


def load_start(root):
    config = root / "tools" / "activity" / "config.txt"

    value = config.read_text(encoding="utf-8-sig").strip()

    return datetime.fromisoformat(value)


def get_commits(root, start):
    branch = run_git(
        root,
        "rev-parse",
        "--abbrev-ref",
        "HEAD",
    ).strip()

    raw = run_git(
        root,
        "log",
        "--format=%H|%aI|%s",
        "--reverse",
        "--all",
        f"--since={start.isoformat()}",
    )

    commits = []

    for line in raw.splitlines():
        if not line.strip():
            continue

        commit = parse_commit(line)
        commit["branch"] = branch

        if not commit["subject"].startswith(GENERATED_PREFIX):
            commits.append(commit)

    return commits


def group_commits(commits):
    groups = []

    for commit in commits:
        if not groups:
            groups.append([commit])
            continue

        previous = groups[-1][-1]

        gap = (
            commit["time"] - previous["time"]
        ).total_seconds() / 60

        same_branch = commit["branch"] == previous["branch"]

        if same_branch and gap <= SESSION_GAP_MINUTES:
            groups[-1].append(commit)
        else:
            groups.append([commit])

    return groups


def make_activity(number, group):
    first = group[0]["time"]
    last = group[-1]["time"]

    if first.date() == last.date():
        period = f"{first:%Y-%m-%d %H:%M}–{last:%H:%M}"
    else:
        period = (
            f"{first:%Y-%m-%d %H:%M}"
            f"–{last:%Y-%m-%d %H:%M}"
        )

    subjects = "\n".join(
        f"- `{commit['sha'][:7]}` — {commit['subject']}"
        for commit in group
    )

    return f"""---
id: ACT-{number:03d}
type: activity
title: Development session
status: Draft
created: {first:%Y-%m-%d}
updated: {last:%Y-%m-%d}
source: git
---

# ACT-{number:03d} - Development session

Date: {first:%Y-%m-%d}
Type: Development
Status: Draft
Branch: {group[0]["branch"]}

## What I Did

Development work recorded by Git during this session.

## Result

Git commits were created during the session ({period}).

## Problems / Issues

[Not established automatically]

## Evidence

### Git Commits

{subjects}

## Related Records

- Task:
- Requirement:
- Feature / Version:
- Decision:
- Test:
"""


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--root",
        default=".",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
    )

    args = parser.parse_args()

    root = Path(args.root).resolve()
    development = root / "development"

    development.mkdir(
        parents=True,
        exist_ok=True,
    )

    start = load_start(root)
    commits = get_commits(root, start)
    groups = group_commits(commits)

    existing_commits = set()

    for path in development.glob("ACT-*.md"):
        text = path.read_text(encoding="utf-8")

        existing_commits.update(
            re.findall(
                r"`([0-9a-f]{7,40})`",
                text,
            )
        )

    groups = [
        [
            commit
            for commit in group
            if commit["sha"] not in existing_commits
        ]
        for group in groups
    ]

    groups = [
        group
        for group in groups
        if group
    ]

    number = next_id(development)

    if not groups:
        print("No new development sessions.")
        return

    for group in groups:
        content = make_activity(
            number,
            group,
        )

        path = development / f"ACT-{number:03d}.md"

        if args.dry_run:
            print(f"WOULD CREATE: {path}")
            print(content)
        else:
            path.write_text(
                content,
                encoding="utf-8",
            )

            print(f"CREATED: {path}")

        number += 1


if __name__ == "__main__":
    main()
