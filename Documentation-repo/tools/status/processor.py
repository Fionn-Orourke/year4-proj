import argparse
import re
from datetime import datetime
from pathlib import Path


def read_records(directory, pattern):
    records = []

    if not directory.exists():
        return records

    for path in sorted(directory.glob(pattern)):
        records.append({
            "path": path,
            "text": path.read_text(encoding="utf-8-sig"),
        })

    return records


def extract_id(text):
    match = re.search(
        r"^id:\s*([A-Z]+-\d+)",
        text,
        re.MULTILINE,
    )

    return match.group(1) if match else None


def extract_date(text, field="updated"):
    match = re.search(
        rf"^{field}:\s*(\d{{4}}-\d{{2}}-\d{{2}})",
        text,
        re.MULTILINE,
    )

    if not match:
        return None

    return datetime.strptime(
        match.group(1),
        "%Y-%m-%d",
    ).date()


def extract_title(text):
    match = re.search(
        r"^#\s+([^\n]+)",
        text,
        re.MULTILINE,
    )

    if match:
        return match.group(1).strip()

    return "Untitled record"


def build_status(root):
    development = read_records(
        root / "development",
        "ACT-*.md",
    )

    requirements = read_records(
        root / "requirements",
        "REQ-*.md",
    )

    findings = read_records(
        root / "research" / "findings",
        "FIND-*.md",
    )

    decisions = read_records(
        root / "decisions",
        "DEC-*.md",
    )

    tests = read_records(
        root / "testing",
        "TEST-*.md",
    )

    activities = []

    for record in development:
        record_id = extract_id(record["text"])

        if record_id:
            activities.append({
                "id": record_id,
                "title": extract_title(record["text"]),
                "date": extract_date(record["text"]),
            })

    activities.sort(
        key=lambda item: item["date"] or datetime.min.date(),
        reverse=True,
    )

    recent_activities = activities[:5]

    lines = [
        "# Project Status",
        "",
        "> Automatically generated draft. Review before replacing the permanent project status.",
        "",
        "## Current Phase",
        "",
        "Project setup and initial engineering investigation.",
        "",
        "## Current Focus",
        "",
        "Automation system and project documentation infrastructure.",
        "",
        "## Current Objectives",
        "",
        "- Establish reliable project documentation automation.",
        "- Maintain traceable engineering records.",
        "- Prepare the project system for engineering development.",
        "",
        "## In Progress",
        "",
        "- Project Status Automation V1",
        "",
        "## Recently Completed",
        "",
    ]

    if recent_activities:
        for activity in recent_activities:
            date = (
                activity["date"].isoformat()
                if activity["date"]
                else "Date unknown"
            )

            lines.append(
                f"- {activity['id']} — "
                f"{activity['title']} ({date})"
            )
    else:
        lines.append("- None recorded.")

    lines.extend([
        "",
        "## Blockers",
        "",
        "- None automatically identified.",
        "",
        "## Open Questions",
        "",
        "- None automatically identified.",
        "",
        "## Recent Decisions",
        "",
    ])

    if decisions:
        for record in decisions[-5:]:
            lines.append(
                f"- {extract_id(record['text']) or 'DEC-???'} — "
                f"{extract_title(record['text'])}"
            )
    else:
        lines.append("- None recorded.")

    lines.extend([
        "",
        "## Recent Research",
        "",
    ])

    if findings:
        for record in findings[-5:]:
            lines.append(
                f"- {extract_id(record['text']) or 'FIND-???'} — "
                f"{extract_title(record['text'])}"
            )
    else:
        lines.append("- None recorded.")

    lines.extend([
        "",
        "## Recent Testing",
        "",
    ])

    if tests:
        for record in tests[-5:]:
            lines.append(
                f"- {extract_id(record['text']) or 'TEST-???'} — "
                f"{extract_title(record['text'])}"
            )
    else:
        lines.append("- None recorded.")

    lines.extend([
        "",
        "## Requirements",
        "",
        f"- {len(requirements)} requirement record(s) currently present.",
        "",
        "## Next Actions",
        "",
        "1. Review the generated project status.",
        "2. Continue setting up the project automation system.",
        "3. Begin engineering project work when the documentation system is ready.",
        "",
        "## Last Updated",
        "",
        datetime.now().date().isoformat(),
        "",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="PROJECT_STATUS_DRAFT.md")

    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = root / args.output

    content = build_status(root)

    output.write_text(
        content,
        encoding="utf-8",
    )

    print(f"CREATED: {output}")


if __name__ == "__main__":
    main()
