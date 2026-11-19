import argparse
import re
import subprocess
import socket
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


MANUAL_START = "<!-- MANUAL:PROJECT_DIRECTION:START -->"
MANUAL_END = "<!-- MANUAL:PROJECT_DIRECTION:END -->"
GENERATED_START = "<!-- GENERATED:PROJECT_STATUS:START -->"
GENERATED_END = "<!-- GENERATED:PROJECT_STATUS:END -->"
INTERNAL_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
EXTERNAL_URL_RE = re.compile(r"https?://[^\s<>)\]\"']+", re.I)
RECORD_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*-\d+\b")


class CriticalStatusError(RuntimeError):
    pass


def run_git(root, *args):
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def read_records(directory, pattern="*.md"):
    records = []
    if not directory.exists():
        return records
    for path in sorted(directory.glob(pattern)):
        if path.is_file():
            records.append({
                "path": path,
                "text": path.read_text(encoding="utf-8-sig"),
            })
    return records


def extract_id(text):
    front = parse_front_matter(text)
    value = front.get("id") if isinstance(front, dict) else None
    if value:
        return str(value).strip().strip('"')
    match = re.search(r"^id:\s*([A-Z][A-Z0-9]*-\d+)", text, re.MULTILINE | re.I)
    return match.group(1).upper() if match else None


def parse_front_matter(text):
    if not text.startswith("---"):
        return {}
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
    if not match:
        return None
    result = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            return None
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        result[key.lower()] = value
    return result


def parse_date_value(value):
    if value is None:
        return None
    value = str(value).strip()
    match = re.match(r"^(\d{4}-\d{2}-\d{2})(?:[T ].*)?$", value)
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%Y-%m-%d").date()
    except ValueError:
        return None


def extract_date(text, field="updated"):
    front = parse_front_matter(text)
    if isinstance(front, dict):
        value = front.get(field.lower())
    else:
        match = re.search(rf"^{field}\s*:\s*(.+)$", text, re.MULTILINE | re.I)
        value = match.group(1).strip() if match else None
    return parse_date_value(value)


def extract_title(text):
    front = parse_front_matter(text)
    if isinstance(front, dict) and front.get("title"):
        return front["title"].strip()
    match = re.search(r"^#\s+([^\n]+)", text, re.MULTILINE)
    return match.group(1).strip() if match else "Untitled record"


def extract_status(text):
    front = parse_front_matter(text)
    if isinstance(front, dict):
        return front.get("status") or "Unknown"
    match = re.search(r"^status:\s*(.+)$", text, re.MULTILINE | re.I)
    return match.group(1).strip() if match else "Unknown"


def extract_field(text, field):
    front = parse_front_matter(text)
    if isinstance(front, dict):
        return front.get(field.lower())
    match = re.search(rf"^{field}\s*:\s*(.+)$", text, re.MULTILINE | re.I)
    return match.group(1).strip() if match else None


def record_link(path, root):
    try:
        relative = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        relative = path.as_posix()
    return relative


def markdown_link(path, root, label=None):
    label = label or path.name
    return f"[{label}]({record_link(path, root)})"


def validate_manual_markers(status_text):
    start_count = status_text.count(MANUAL_START)
    end_count = status_text.count(MANUAL_END)
    if start_count != 1 or end_count != 1:
        raise CriticalStatusError(
            "Critical validation error: PROJECT_STATUS.md must contain exactly one "
            "PROJECT_DIRECTION start marker and one end marker."
        )
    start = status_text.index(MANUAL_START)
    end = status_text.index(MANUAL_END)
    if start >= end:
        raise CriticalStatusError(
            "Critical validation error: PROJECT_DIRECTION markers are incorrectly ordered."
        )


def extract_manual_content(status_text):
    validate_manual_markers(status_text)
    start = status_text.index(MANUAL_START) + len(MANUAL_START)
    end = status_text.index(MANUAL_END)
    return status_text[start:end]


def section_text(text, heading):
    match = re.search(
        rf"^##\s+{re.escape(heading)}\s*$.*?(?=^##\s+|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(0).strip() if match else None


def raw_date(front, field):
    if isinstance(front, dict):
        return front.get(field)
    return None


def extract_body_field(text, field_names):
    for field_name in field_names:
        match = re.search(
            rf"^{re.escape(field_name)}:\s*(.+)$",
            text,
            re.MULTILINE | re.I,
        )
        if match:
            return match.group(1).strip()
    return None


def load_records(root, directories):
    records = []
    for directory_name, pattern, category in directories:
        directory = root / directory_name
        for record in read_records(directory, pattern):
            text = record["text"]
            front = parse_front_matter(text)
            record_id = extract_id(text)
            warnings = []
            if front is None:
                warnings.append("Invalid front matter")
            elif not isinstance(front, dict):
                warnings.append("Invalid front matter")
            if not record_id:
                warnings.append("Missing ID")

            raw_event = None
            event_field = {
                "activity": "date",
                "requirement": "created",
                "research": "date",
                "decision": "date",
                "test": "date",
                "task": "created",
                "blocker": "date",
                "open_question": "date",
                "feature": "updated",
                "master": "updated",
            }.get(category)
            if isinstance(front, dict):
                raw_event = front.get(event_field) if event_field else None
                if not front.get("title") and not re.search(r"^#\s+", text, re.MULTILINE):
                    warnings.append("Missing title")
            if raw_event is None:
                body_field_names = {
                    "activity": ("Date", "Activity Date"),
                    "requirement": ("Created", "Creation Date", "Date"),
                    "research": ("Research Date", "Date"),
                    "decision": ("Decision Date", "Date"),
                    "test": ("Test Date", "Execution Date", "Date"),
                    "task": ("Created", "Date"),
                    "blocker": ("Date", "Reported"),
                    "open_question": ("Date", "Raised"),
                    "feature": ("Updated", "Date"),
                    "master": ("Updated", "Date"),
                }.get(category, ())
                raw_event = extract_body_field(text, body_field_names)
            event_date = parse_date_value(raw_event)
            if raw_event and event_date is None:
                warnings.append(f"Invalid date: {raw_event}")
            elif not raw_event:
                warnings.append("Missing date")

            records.append({
                "path": record["path"],
                "text": text,
                "front": front if isinstance(front, dict) else {},
                "id": record_id,
                "title": extract_title(text),
                "status": extract_status(text),
                "category": category,
                "event_field": event_field,
                "event_date": event_date,
                "raw_event": raw_event,
                "updated": extract_date(text, "updated"),
                "raw_updated": (
                    front.get("updated") if isinstance(front, dict) else None
                ),
                "warnings": warnings,
            })
    return records


def find_unclassified(root):
    known = {
        "PROJECT_RULES.md",
        "PROJECT_STATUS.md",
        "PROJECT_STATUS_DRAFT.md",
        "README.md",
    }
    excluded_dirs = {"tools", "tests", "templates"}
    records = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in excluded_dirs for part in path.relative_to(root).parts):
            continue
        relative = path.relative_to(root)
        if relative.name in known or path.suffix.lower() not in (".md", ".txt", ".yaml", ".yml"):
            continue
        text = path.read_text(encoding="utf-8-sig")
        if relative.parts and relative.parts[0] in {
            "development", "requirements", "research", "decisions",
            "testing", "tasks", "blockers", "open-questions",
            "features", "master", "references",
        }:
            continue
        if "ideas" in relative.parts:
            kind = "Markdown idea record"
        else:
            kind = "Markdown document" if path.suffix == ".md" else "Text document"
        records.append({
            "path": path,
            "type": kind,
            "description": extract_title(text),
            "reason": "The file is outside a recognised status record directory.",
        })
    return records


def check_external_link(url):
    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "year4-proj-status-automation/2.0"},
            method="HEAD",
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                code = getattr(response, "status", 200)
        except urllib.error.HTTPError as error:
            code = error.code
        if 200 <= code < 400:
            return "Successful response"
        if code == 403:
            return "Access restricted (HTTP 403)"
        if code == 404:
            return "Confirmed broken link (HTTP 404)"
        if code:
            return f"Inconclusive response (HTTP {code})"
        return "Inconclusive response"
    except urllib.error.HTTPError as error:
        if error.code == 403:
            return "Access restricted (HTTP 403)"
        if error.code == 404:
            return "Confirmed broken link (HTTP 404)"
        return f"Inconclusive response (HTTP {error.code})"
    except TimeoutError:
        return "Timeout"
    except socket.timeout:
        return "Timeout"
    except urllib.error.URLError as error:
        reason = str(error.reason).lower()
        if "timed out" in reason or "timeout" in reason:
            return "Timeout"
        return "Temporary server or network failure"
    except Exception:
        return "Temporary server or network failure"


def check_external_link_status(code):
    if 200 <= code < 400:
        return "Successful response"
    if code == 403:
        return "Access restricted (HTTP 403)"
    if code == 404:
        return "Confirmed broken link (HTTP 404)"
    return f"Inconclusive response (HTTP {code})"


def resolve_internal_link(root, source, target):
    if target.startswith(("http://", "https://", "#", "mailto:")):
        return "external", None
    target_path = target.split("#", 1)[0]
    if not target_path:
        return "anchor", None
    candidate = (source.parent / target_path).resolve()
    if candidate.exists():
        return "resolved", candidate

    matches = []
    for path in root.rglob("*"):
        if path.is_file() and (
            path.name == Path(target_path).name
            or path.stem == Path(target_path).stem
        ):
            matches.append(path)
    if len(matches) == 1:
        return "repairable", matches[0]
    if len(matches) > 1:
        return "ambiguous", None
    return "broken", None


def get_git_history(root):
    try:
        raw = run_git(
            root,
            "log",
            "--all",
            "--date=iso-strict",
            "--format=%H%x1f%aI%x1f%P%x1f%s",
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return [], "Git history unavailable."

    commits = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\x1f", 3)
        if len(parts) != 4:
            continue
        sha, date_text, parents, subject = parts
        try:
            commit_date = datetime.fromisoformat(date_text)
        except ValueError:
            commit_date = None
        try:
            names = run_git(root, "branch", "--all", "--contains", sha).splitlines()
            branches = sorted(
                set(
                name.strip().lstrip("* ").replace("remotes/", "")
                for name in names
                if name.strip()
                )
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            branches = []

        try:
            names_status = run_git(
                root,
                "show",
                "--pretty=format:",
                "--name-status",
                "--find-renames",
                "--find-copies",
                sha,
            ).splitlines()
        except (subprocess.CalledProcessError, FileNotFoundError):
            names_status = []
        changed = []
        for change in names_status:
            fields = change.split("\t")
            if len(fields) >= 2:
                change_type = fields[0]
                if change_type.startswith("R") and len(fields) >= 3:
                    filename = f"{fields[1]} -> {fields[2]}"
                elif change_type.startswith("C") and len(fields) >= 3:
                    filename = f"{fields[1]} -> {fields[2]}"
                else:
                    filename = fields[-1]
                changed.append((filename, change_type))

        text = f"{subject.lower()} " + " ".join(path for path, _ in changed)
        if re.search(r"\b(test|fix|bug|feat|docs|ci|build|activity|status|reference)\b", text):
            relevance = "Project-related"
        elif any(path.startswith(("Documentation-repo/", "src/", "hardware/", "firmware/", "software/")) for path, _ in changed):
            relevance = "Project-related"
        elif changed and re.search(r"\b(chore|merge|housekeeping)\b", text):
            relevance = "Unrelated"
        elif changed:
            relevance = "Uncertain"
        else:
            relevance = "Uncertain"

        commits.append({
            "sha": sha,
            "date": commit_date,
            "raw_date": date_text,
            "subject": subject,
            "parents": parents.split(),
            "merge": len(parents.split()) > 1,
            "branches": branches,
            "changed": changed,
            "relevance": relevance,
        })
    commits.sort(
        key=lambda item: item["date"] or datetime.min.replace(tzinfo=timezone.utc),
        reverse=False,
    )
    return commits, None


def duplicate_ids(records):
    positions = {}
    duplicates = set()
    for record in records:
        if record["id"]:
            positions.setdefault(record["id"], []).append(record)
    for record_id, items in positions.items():
        if len(items) > 1:
            duplicates.add(record_id)
    return duplicates


def find_relationships(records, root):
    explicit = []
    inferred = []
    related_front_fields = (
        "related", "relations", "relationships", "related_records",
        "related_requirements", "related_decisions", "related_research",
        "related_tests", "related_tasks", "related_feature",
        "requirements", "decisions", "research", "tests", "tasks",
        "references", "sources",
    )
    for record in records:
        text = record["text"]
        front = record.get("front", {}) if isinstance(record.get("front"), dict) else {}
        ids = set()
        for key, value in front.items():
            if key in related_front_fields or "related" in key:
                ids.update(RECORD_ID_RE.findall(str(value).upper()))
        section_match = re.search(
            r"^##+\s+(?:Related Records|Relationships|Related Requirements|"
            r"Related Decisions|Related Research|References|Sources)\s*$"
            r"(.*?)(?=^##|\Z)",
            text,
            re.MULTILINE | re.DOTALL | re.I,
        )
        if section_match:
            ids.update(RECORD_ID_RE.findall(section_match.group(1).upper()))
        for other_id in ids:
            if other_id != record["id"]:
                explicit.append({
                    "source": record["id"] or record["path"].name,
                    "target": other_id,
                    "evidence": "Explicit relationship declared in record metadata or related-record section",
                })

    by_id = {record["id"]: record for record in records if record["id"]}
    boilerplate = {
        "activity", "activities", "automation", "automatically", "development",
        "project", "record", "records", "session", "status", "git", "main",
        "branch", "created", "updated", "recorded", "unknown", "none",
        "a632d0f", "a0b608",
    }
    for left in records:
        words = set(re.findall(r"[A-Za-z][A-Za-z0-9_-]{4,}", left["text"].lower()))
        words = words - boilerplate
        for right in records:
            if left["path"] == right["path"]:
                continue
            if right["id"] and right["id"] in left["text"]:
                continue
            right_words = set(
                re.findall(r"[A-Za-z][A-Za-z0-9_-]{4,}", right["text"].lower())
            ) - boilerplate
            common = words.intersection(right_words)
            if len(common) >= 2:
                inferred.append({
                    "source": left["id"] or left["path"].name,
                    "target": right["id"] or right["path"].name,
                    "reason": "Shared terminology: " + ", ".join(sorted(common)[:3]),
                })
    return explicit, inferred


def compact_record_lines(records, root, category_name):
    if not records:
        return ["No records currently available."]
    lines = []
    duplicates = duplicate_ids(records)
    for record in records:
        label = record["id"] or "Unknown"
        title = record["title"]
        status = record["status"]
        date = date_label(record)
        link = markdown_link(record["path"], root)
        warnings = []
        if record["warnings"]:
            warnings.append("; ".join(record["warnings"]))
        if record["id"] in duplicates:
            warnings.append("Possible duplicate record")
        warning_text = f" — Validation warning: {'; '.join(warnings)}" if warnings else ""
        lines.append(
            f"- **{label} — {title}** ({status}; date: {date}) — {link}{warning_text}"
        )
    return lines


def date_label(record):
    if record["event_date"]:
        return record["event_date"].isoformat()
    if record["raw_event"]:
        return f"Invalid: {record['raw_event']}"
    return "Unknown"


def record_body_details(record):
    text = record["text"]
    if text.startswith("---"):
        match = re.match(r"\A---\r?\n.*?\r?\n---(?:\r?\n|$)", text, re.DOTALL)
        if match:
            text = text[match.end():]
    text = re.sub(r"\r\n?", "\n", text).strip()
    return text if text else "No additional recorded details."


def related_reference_ids(record):
    front = record.get("front", {}) if isinstance(record.get("front"), dict) else {}
    ids = set()
    for key, value in front.items():
        if key in ("references", "sources", "related_references") or "reference" in key:
            ids.update(RECORD_ID_RE.findall(str(value).upper()))
    section_match = re.search(
        r"^##+\s+(?:References|Related References|Sources)\s*$"
        r"(.*?)(?=^##|\Z)",
        record["text"],
        re.MULTILINE | re.DOTALL | re.I,
    )
    if section_match:
        ids.update(RECORD_ID_RE.findall(section_match.group(1).upper()))
    return sorted(ids)


def validate_generated_report(content):
    if not content.startswith("# Project Status"):
        raise CriticalStatusError("Critical validation error: generated report has no title.")
    if content.count(GENERATED_START) != 1 or content.count(GENERATED_END) != 1:
        raise CriticalStatusError(
            "Critical validation error: generated report markers are missing or duplicated."
        )
    if content.index(GENERATED_START) >= content.index(GENERATED_END):
        raise CriticalStatusError(
            "Critical validation error: generated report markers are incorrectly ordered."
        )


def build_status(root):
    root = Path(root).resolve()
    status_path = root / "PROJECT_STATUS.md"
    if not status_path.exists():
        raise CriticalStatusError(
            "Critical validation error: PROJECT_STATUS.md does not exist."
        )
    status_text = status_path.read_text(encoding="utf-8-sig")
    manual_content = extract_manual_content(status_text)

    directories = [
        ("development", "ACT-*.md", "activity"),
        ("requirements", "REQ-*.md", "requirement"),
        ("research/findings", "FIND-*.md", "research"),
        ("decisions", "DEC-*.md", "decision"),
        ("testing", "TEST-*.md", "test"),
        ("tasks", "TASK-*.md", "task"),
        ("blockers", "*.md", "blocker"),
        ("open-questions", "*.md", "open_question"),
        ("features", "*.md", "feature"),
        ("master", "*.md", "master"),
    ]
    records = load_records(root, directories)
    by_category = {
        category: [record for record in records if record["category"] == category]
        for category in (
            "activity", "requirement", "research", "decision", "test",
            "task", "blocker", "open_question", "feature", "master",
        )
    }

    lines = [
        "# Project Status",
        "",
        MANUAL_START + manual_content + MANUAL_END,
        "",
        GENERATED_START,
        "",
        "## Active Work",
        "",
    ]
    active = [
        record for record in by_category["task"]
        if record["status"].lower() not in ("completed", "complete", "done", "closed")
    ]
    if active:
        lines.extend(
            f"- **{record['id'] or 'Unknown'} — {record['title']}** "
            f"(Status: {record['status']})"
            for record in active
        )
    else:
        lines.append("No active work recorded.")

    lines.extend(["", "## Project Timeline", ""])
    timeline = sorted(
        (
            record for record in records
            if record["category"] in (
                "activity", "requirement", "research", "decision", "test",
                "blocker", "open_question", "feature", "master",
            )
        ),
        key=lambda record: (
            record["event_date"] is None,
            record["event_date"] or datetime.min,
        ),
    )
    if timeline:
        for record in timeline:
            date = date_label(record)
            link = markdown_link(record["path"], root)
            lines.append(
                f"- **{date}** — {record['category'].replace('_', ' ').title()}: "
                f"{record['title']} ({record['status']}; ID: {record['id'] or 'Unknown'}) — {link}"
            )
            ref_ids = related_reference_ids(record)
            if ref_ids:
                lines.append("  - References: " + ", ".join(ref_ids))
            lines.append("  - Recorded details:")
            for detail_line in record_body_details(record).splitlines():
                if detail_line.strip():
                    lines.append("    " + detail_line)
    else:
        lines.append("No timeline records currently available.")

    lines.extend(["", "## Timeline Category Summaries", ""])
    for category, heading in (
        ("research", "Research and Investigations"),
        ("decision", "Engineering Decisions"),
        ("activity", "Development Activities"),
        ("test", "Testing and Results"),
        ("requirement", "Requirements Changes"),
        ("blocker", "Problems and Resolutions"),
        ("open_question", "Open Questions"),
        ("feature", "Project Milestones"),
    ):
        lines.extend(["### " + heading, ""])
        lines.extend(compact_record_lines(by_category[category], root, heading))
        lines.append("")

    lines.extend(["## Development History", ""])
    for record in by_category["activity"]:
        date = record["event_date"].isoformat() if record["event_date"] else "Unknown"
        lines.append(
            f"- **{date}** — {record['title']} "
            f"(Status: {record['status']}; ID: {record['id'] or 'Unknown'}) — "
            f"{markdown_link(record['path'], root)}"
        )
    if not by_category["activity"]:
        lines.append("No development activity records currently available.")

    lines.extend(["", "## Requirements", ""])
    lines.extend(compact_record_lines(by_category["requirement"], root, "Requirements"))

    lines.extend(["", "## Research", ""])
    lines.extend(compact_record_lines(by_category["research"], root, "Research"))

    lines.extend(["", "## Engineering Decisions", ""])
    lines.extend(compact_record_lines(by_category["decision"], root, "Decisions"))

    lines.extend(["", "## Testing", ""])
    lines.extend(compact_record_lines(by_category["test"], root, "Testing"))

    lines.extend(["", "## Tasks", ""])
    lines.extend(compact_record_lines(by_category["task"], root, "Tasks"))

    lines.extend(["", "## Blockers", ""])
    lines.extend(compact_record_lines(by_category["blocker"], root, "Blockers"))

    lines.extend(["", "## Open Questions", ""])
    lines.extend(compact_record_lines(by_category["open_question"], root, "Open Questions"))

    lines.extend(["", "## Feature Versions", ""])
    if by_category["feature"]:
        lines.extend(compact_record_lines(by_category["feature"], root, "Feature Versions"))
        for record in by_category["feature"]:
            ref_ids = related_reference_ids(record)
            if ref_ids:
                lines.append(
                    f"- **{record['id'] or record['path'].name} references:** "
                    + ", ".join(ref_ids)
                )
            else:
                lines.append(
                    f"- **{record['id'] or record['path'].name} references:** "
                    "No references recorded."
                )
    else:
        lines.append("No Feature Version records currently available.")

    lines.extend(["", "## Master", ""])
    if by_category["master"]:
        lines.extend(compact_record_lines(by_category["master"], root, "Master"))
        for record in by_category["master"]:
            ref_ids = related_reference_ids(record)
            if ref_ids:
                lines.append(
                    f"- **Master {record['id'] or record['path'].name} references:** "
                    + ", ".join(ref_ids)
                )
            else:
                lines.append(
                    f"- **Master {record['id'] or record['path'].name} references:** "
                    "No references recorded."
                )
    else:
        lines.append("No Master records currently available.")

    lines.extend(["", "## References", ""])
    reference_records = read_records(root / "references", "REF-*.md")
    if reference_records:
        for record in reference_records:
            text = record["text"]
            front = parse_front_matter(text)
            record_id = extract_id(text) or "Unknown"
            title = extract_title(text)
            status = extract_status(text)
            url = extract_field(text, "url")
            url_status = check_external_link(url) if url and url not in ("null", "none") else "URL unavailable"
            url_text = f" — [{url}]({url})" if url and url not in ("null", "none") else ""
            lines.append(
                f"- **{record_id} — {title}** (Status: {status})"
                f"{url_text} — Link check: {url_status}"
            )
    else:
        lines.append("No references currently available.")

    lines.extend(["", "## Relationships", ""])
    explicit, inferred = find_relationships(records, root)
    if explicit:
        lines.append("### Confirmed relationships")
        lines.extend(
            f"- {item['source']} → {item['target']} — {item['evidence']}"
            for item in explicit
        )
    else:
        lines.append("No confirmed relationships recorded.")
    if inferred:
        lines.append("### Unverified Suggestions")
        lines.extend(
            f"- **Unverified Suggestion:** {item['source']} → {item['target']} "
            f"— {item['reason']}"
            for item in inferred
        )
    else:
        lines.append("No inferred relationships available.")

    lines.extend(["", "## Git Development History", ""])
    git_commits, git_error = get_git_history(root)
    unrelated = [commit for commit in git_commits if commit["relevance"] != "Project-related"]
    uncertain = [commit for commit in git_commits if commit["relevance"] == "Uncertain"]
    remote_url = ""
    try:
        remote_url = run_git(root, "config", "--get", "remote.origin.url").strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        remote_url = ""
    match = re.search(r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?$", remote_url)
    github_base = (
        f"https://github.com/{match.group(1)}/{match.group(2)}"
        if match else None
    )
    if git_error:
        lines.append(git_error)
    elif git_commits:
        for commit in git_commits:
            if commit["relevance"] not in ("Project-related", "Uncertain"):
                continue
            date = (
                commit["date"].isoformat()
                if commit["date"]
                else commit["raw_date"]
            )
            merge = " — Merge commit" if commit["merge"] else ""
            branches = ", ".join(commit["branches"]) if commit["branches"] else "Unavailable"
            uncertainty = " — Classification: uncertain" if commit["relevance"] == "Uncertain" else ""
            if github_base:
                commit_url = f"{github_base}/commit/{commit['sha']}"
                sha_text = f"[`{commit['sha'][:12]}`]({commit_url})"
            else:
                sha_text = f"`{commit['sha'][:12]}`"
            lines.append(
                f"- **{date}** — {commit['subject']} — {sha_text}"
                f"{merge}{uncertainty} — Branches containing commit: {branches}"
            )
            if commit["changed"]:
                changes = []
                for filename, change_type in commit["changed"]:
                    type_name = {
                        "A": "added",
                        "M": "modified",
                        "D": "deleted",
                        "R": "renamed",
                        "C": "copied",
                        "T": "type changed",
                    }.get(change_type[0], "changed")
                    changes.append(f"{type_name}: {filename}")
                lines.append("  - " + "; ".join(changes))
            else:
                lines.append("  - Changed filenames: Unavailable")
        if unrelated:
            unrelated_count = len([c for c in unrelated if c["relevance"] == "Unrelated"])
            full_history = f"[Full Git history]({github_base}/commits)" if github_base else "Full Git history: Git log unavailable"
            lines.append(
                f"- Unrelated commit count: {unrelated_count}; "
                f"Uncertain commit count: {len(uncertain)} — {full_history}"
            )
    else:
        lines.append("No Git commits currently available.")

    lines.extend(["", "## Validation Warnings", ""])
    warnings = []
    for record in records:
        if record["warnings"]:
            warnings.append(
                f"- {record['path'].relative_to(root).as_posix()}"
                f"{' (' + record['id'] + ')' if record['id'] else ''}: "
                f"{'; '.join(record['warnings'])}"
            )
    duplicates = duplicate_ids(records)
    for record_id in sorted(duplicates):
        warnings.append(f"- Possible duplicate record ID: {record_id}")

    lines.extend(warnings or ["- No validation warnings."])

    lines.extend(["", "## Internal and External Link Check", ""])
    link_warnings = []
    checked_urls = set()
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in (".md", ".txt"):
            continue
        if path == status_path:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            continue
        for match in INTERNAL_LINK_RE.findall(text):
            state, target = resolve_internal_link(root, path, match)
            if state == "broken":
                link_warnings.append(
                    f"- Broken internal link: {match} in "
                    f"{path.relative_to(root).as_posix()}"
                )
            elif state == "ambiguous":
                link_warnings.append(
                    f"- Ambiguous internal link: {match} in "
                    f"{path.relative_to(root).as_posix()}"
                )
            elif state == "repairable":
                link_warnings.append(
                    f"- Unambiguous internal-link repair available: {match} → "
                    f"{target.relative_to(root).as_posix()} "
                    f"in {path.relative_to(root).as_posix()}"
                )
        for url in EXTERNAL_URL_RE.findall(text):
            if url not in checked_urls:
                checked_urls.add(url)
                link_warnings.append(
                    f"- {url}: {check_external_link(url)} "
                    f"(in {path.relative_to(root).as_posix()})"
                )
    lines.extend(link_warnings or ["- No internal or external link problems detected."])

    lines.extend(["", "## Unclassified Records", ""])
    unclassified = find_unclassified(root)
    if unclassified:
        for item in unclassified:
            lines.append(
                f"- **{item['path'].relative_to(root).as_posix()}** "
                f"— Type: {item['type']}; {item['description']} "
                f"— Reason: {item['reason']}"
            )
    else:
        lines.append("No unclassified records currently available.")

    lines.extend(["", "## Next Actions", ""])
    lines.append("### Manually Recorded Actions")
    manual_actions = section_text(extract_manual_content(status_text), "Next Actions")
    if manual_actions:
        lines.append(manual_actions)
    else:
        lines.append("No manually recorded actions currently available.")
    lines.extend([
        "",
        "### Automated Suggestions",
        "",
    ])
    suggestions = []
    if not by_category["requirement"]:
        suggestions.append("Review whether requirement records are needed.")
    if not by_category["research"]:
        suggestions.append("Review whether research findings are currently available.")
    if not by_category["decision"]:
        suggestions.append("Review whether engineering decisions need to be recorded.")
    if not by_category["test"]:
        suggestions.append("Review whether testing records are currently available.")
    if warnings:
        suggestions.append("Resolve outstanding validation warnings.")
    if suggestions:
        lines.extend(f"- **Suggestion:** {suggestion}" for suggestion in suggestions)
    else:
        lines.append("- No automated suggestions.")

    source_dates = [
        record["event_date"] for record in records
        if record["event_date"] is not None
    ]
    source_dates.extend(commit["date"].date() for commit in git_commits if commit["date"])
    last_source_date = max(source_dates).isoformat() if source_dates else "Unavailable"
    lines.extend(["", "## Last Updated", "", last_source_date, "", GENERATED_END, ""])

    content = "\n".join(lines)
    validate_generated_report(content)
    validate_manual_markers(content)
    return content


def write_status(root, content):
    status_path = Path(root).resolve() / "PROJECT_STATUS.md"
    validate_generated_report(content)
    previous = status_path.read_text(encoding="utf-8-sig")
    validate_manual_markers(previous)
    if extract_manual_content(previous) != extract_manual_content(content):
        raise CriticalStatusError(
            "Critical validation error: generated report changed manual content."
        )
    status_path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--output",
        default="PROJECT_STATUS.md",
        help="Deprecated; PROJECT_STATUS.md is always the output file.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = root / "PROJECT_STATUS.md"
    try:
        content = build_status(root)
        if not Path(root / "PROJECT_STATUS.md").exists():
            raise CriticalStatusError("PROJECT_STATUS.md is missing.")
        previous = (root / "PROJECT_STATUS.md").read_text(encoding="utf-8-sig")
        if content != previous:
            output.write_text(content, encoding="utf-8")
            print(f"CREATED: {output}")
        else:
            print(f"UNCHANGED: {output}")
    except CriticalStatusError as error:
        print(f"FAILED: {error}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
