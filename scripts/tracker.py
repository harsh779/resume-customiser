"""
Application tracker for resume-customiser.

Commands:
  tracker.py add <json_string>           Add new application entry
  tracker.py list                        List all applications (table)
  tracker.py update <id> <status>        Update application status
  tracker.py view <id>                   Show full details of one application
  tracker.py stats                       Summary stats across all applications

Status values: tailored | applied | phone_screen | interview | offer | rejected | withdrawn

Tracker file lives at: <REPO_DIR>/applications.json
REPO_DIR is set by install.py. Override anytime with env var RESUME_REPO_PATH.
"""
import sys
import os
import json
from datetime import datetime

# Force UTF-8 output on Windows to handle Unicode bar characters
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO_DIR = os.environ.get(
    "RESUME_REPO_PATH",
    r"{{REPO_DIR}}"
)
TRACKER_FILE = os.path.join(REPO_DIR, "applications.json")

STATUS_ORDER = [
    "tailored", "applied", "phone_screen", "interview", "offer", "rejected", "withdrawn"
]

STATUS_DISPLAY = {
    "tailored":     "Tailored    ",
    "applied":      "Applied     ",
    "phone_screen": "Phone Screen",
    "interview":    "Interview   ",
    "offer":        "Offer       ",
    "rejected":     "Rejected    ",
    "withdrawn":    "Withdrawn   ",
}


def load():
    if not os.path.exists(TRACKER_FILE):
        return {"applications": []}
    with open(TRACKER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    os.makedirs(REPO_DIR, exist_ok=True)
    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def next_id(data):
    existing = [a.get("id", 0) for a in data["applications"]]
    return max(existing, default=0) + 1


def cmd_add(json_str):
    entry = json.loads(json_str)
    data = load()
    entry["id"] = next_id(data)
    entry.setdefault("date", datetime.now().strftime("%Y-%m-%d"))
    entry.setdefault("status", "tailored")
    data["applications"].append(entry)
    save(data)
    print(f"Added application #{entry['id']}: {entry.get('company')} — {entry.get('role')}")
    return entry["id"]


def cmd_list():
    data = load()
    apps = data["applications"]
    if not apps:
        print("No applications tracked yet.")
        return

    header = f"{'ID':>3}  {'Date':<12}  {'Status':<12}  {'Company':<22}  {'Role':<30}  {'Match':>6}"
    print(header)
    print("-" * len(header))
    for a in sorted(apps, key=lambda x: x.get("date", ""), reverse=True):
        stats = a.get("match_stats", {})
        strong = stats.get("strong", "-")
        partial = stats.get("partial", "-")
        gaps = stats.get("gaps", "-")
        match_str = f"{strong}S/{partial}P/{gaps}G"
        status = STATUS_DISPLAY.get(a.get("status", "tailored"), a.get("status", ""))
        print(
            f"{a['id']:>3}  "
            f"{a.get('date', ''):<12}  "
            f"{status:<12}  "
            f"{a.get('company', '')[:22]:<22}  "
            f"{a.get('role', '')[:30]:<30}  "
            f"{match_str:>10}"
        )


def cmd_update(app_id, status):
    app_id = int(app_id)
    if status not in STATUS_ORDER:
        print(f"Invalid status '{status}'. Valid: {', '.join(STATUS_ORDER)}")
        sys.exit(1)
    data = load()
    for a in data["applications"]:
        if a["id"] == app_id:
            old = a.get("status", "tailored")
            a["status"] = status
            a["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            save(data)
            print(f"#{app_id} {a.get('company')} — {a.get('role')}: {old} → {status}")
            return
    print(f"Application #{app_id} not found.")
    sys.exit(1)


def cmd_view(app_id):
    app_id = int(app_id)
    data = load()
    for a in data["applications"]:
        if a["id"] == app_id:
            print(f"\n{'='*50}")
            print(f"Application #{a['id']}")
            print(f"{'='*50}")
            print(f"Company     : {a.get('company', '')}")
            print(f"Role        : {a.get('role', '')}")
            print(f"Date        : {a.get('date', '')}")
            print(f"Status      : {a.get('status', '')}")
            print(f"JD Source   : {a.get('jd_source', '')}")
            print(f"Base Resume : {a.get('resume_input', '')}")
            print(f"Output DOCX : {a.get('resume_output', '')}")
            stats = a.get("match_stats", {})
            print(f"\nMatch Stats :")
            print(f"  Strong    : {stats.get('strong', 0)}")
            print(f"  Partial   : {stats.get('partial', 0)}")
            print(f"  Gaps      : {stats.get('gaps', 0)}")
            gaps = a.get("gaps", [])
            if gaps:
                print(f"\nGaps Identified:")
                for g in gaps:
                    print(f"  - {g}")
            print()
            return
    print(f"Application #{app_id} not found.")
    sys.exit(1)


def cmd_stats():
    data = load()
    apps = data["applications"]
    total = len(apps)
    if total == 0:
        print("No applications yet.")
        return

    by_status = {}
    for a in apps:
        s = a.get("status", "tailored")
        by_status[s] = by_status.get(s, 0) + 1

    avg_strong = avg_gaps = 0
    count_with_stats = 0
    for a in apps:
        stats = a.get("match_stats", {})
        if stats:
            avg_strong += stats.get("strong", 0)
            avg_gaps += stats.get("gaps", 0)
            count_with_stats += 1

    print(f"\nApplication Pipeline — {total} total")
    print("-" * 35)
    for s in STATUS_ORDER:
        n = by_status.get(s, 0)
        if n:
            bar = "█" * n
            print(f"  {STATUS_DISPLAY.get(s, s)}: {n:>3}  {bar}")

    if count_with_stats:
        print(f"\nAvg match stats (across {count_with_stats} applications):")
        print(f"  Strong matches : {avg_strong / count_with_stats:.1f}")
        print(f"  Gaps           : {avg_gaps / count_with_stats:.1f}")
    print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "add":
        if len(sys.argv) < 3:
            print("Usage: tracker.py add '<json_string>'")
            sys.exit(1)
        cmd_add(sys.argv[2])

    elif cmd == "list":
        cmd_list()

    elif cmd == "update":
        if len(sys.argv) < 4:
            print("Usage: tracker.py update <id> <status>")
            sys.exit(1)
        cmd_update(sys.argv[2], sys.argv[3])

    elif cmd == "view":
        if len(sys.argv) < 3:
            print("Usage: tracker.py view <id>")
            sys.exit(1)
        cmd_view(sys.argv[2])

    elif cmd == "stats":
        cmd_stats()

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: add | list | update | view | stats")
        sys.exit(1)


if __name__ == "__main__":
    main()
