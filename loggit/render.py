"""Terminal rendering and summary statistics (stdlib only)."""
import sys


# ANSI helpers - no deps, degrade gracefully when not a TTY.
def _c(code):
    if not sys.stdout.isatty():
        return ""
    return f"\x1b[{code}m"


RESET = _c("0")
BOLD = _c("1")
DIM = _c("2")
RED = _c("31")
GREEN = _c("32")
YELLOW = _c("33")
BLUE = _c("34")
MAGENTA = _c("35")
CYAN = _c("36")


def render_commit(c):
    """Render a single commit as a compact colored block."""
    lines = []
    head = f"{BOLD}{YELLOW}{c['short']}{RESET}"
    refs = f" {CYAN}{c['refs'].strip()}{RESET}" if c.get("refs", "").strip() else ""
    author = f"{MAGENTA}{c['author']}{RESET}"
    age = f"{DIM}{c['age_human']}{RESET}"
    lines.append(f"{head}{refs}  {c['subject']}")
    lines.append(f"    {author}  ·  {age}")
    if c.get("body"):
        for line in c["body"].split("\n"):
            lines.append(f"    {DIM}{line}{RESET}")
    if c.get("changed_files"):
        lines.append(
            f"    {GREEN}+{c['added']}{RESET}/{RED}-{c['removed']}{RESET} in "
            f"{c['changed_files']} file(s)"
        )
    return "\n".join(lines)


def __getattr__(name):
    # Allow graceful fallback in case color is disabled
    raise AttributeError(name)


def authors_summary(commits):
    """Summarize commit counts per author: [(name, count, added, removed), ...]."""
    agg = {}
    for c in commits:
        a = agg.setdefault(
            c["author"],
            {"name": c["author"], "count": 0, "added": 0, "removed": 0},
        )
        a["count"] += 1
        a["added"] += c.get("added", 0)
        a["removed"] += c.get("removed", 0)
    return sorted(agg.values(), key=lambda a: (-a["count"], -a["added"]))


def render_authors(author_rows, width=None):
    width = width or 24
    lines = []
    for a in author_rows:
        name = f"{BOLD}{a['name']}{RESET}"
        bar = "█" * min(a["count"], 40)
        lines.append(
            f"  {name:<{width}} {a['count']:>4} commits  "
            f"{GREEN}+{a['added']}{RESET}/{RED}-{a['removed']}{RESET}  {bar}"
        )
    return "\n".join(lines)


def pace_summary(commits):
    """Return a dict with overall stats for the captured window."""
    if not commits:
        return {"commits": 0}
    dates = [c["date"] for c in commits]
    try:
        span_days = max((max(dates) - min(dates)).total_seconds() / 86400.0, 0.0001)
    except Exception:
        span_days = 0.0001
    total_added = sum(c.get("added", 0) for c in commits)
    total_removed = sum(c.get("removed", 0) for c in commits)
    return {
        "commits": len(commits),
        "authors": len({c["author"] for c in commits}),
        "span_days": span_days,
        "avg_per_day": len(commits) / span_days,
        "added": total_added,
        "removed": total_removed,
    }
