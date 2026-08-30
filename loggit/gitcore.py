"""Low-level git interaction and log parsing (stdlib only, no deps)."""
import datetime as _dt
import subprocess
import sys


class GitError(RuntimeError):
    pass


def run_git(args, cwd=None):
    """Run a git command and return its stdout, raising on failure."""
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise GitError("git is not installed or not on PATH") from exc
    if proc.returncode != 0:
        raise GitError((proc.stderr or "git command failed").strip())
    return proc.stdout


def is_repo(cwd=None):
    try:
        run_git(["-C", (cwd or "."), "rev-parse", "--is-inside-work-tree"], cwd=cwd)
        return True
    except GitError:
        return False


def _parse_ts(iso):
    try:
        return _dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return _dt.datetime.now()


def human_age(dt, now=None):
    """Return a compact relative age like '3h ago' from a datetime."""
    now = now or _dt.datetime.now(dt.tzinfo) if dt.tzinfo else (_dt.datetime.now())
    delta = now - dt
    if dt.tzinfo is None:
        # naive datetimes: compare against naive now
        delta = _dt.datetime.now() - dt
    secs = int(delta.total_seconds())
    if secs < 0:
        secs = 0
    if secs < 90:
        return f"{secs}s ago"
    mins = secs // 60
    if mins < 60:
        return f"{mins}m ago"
    hours = mins // 60
    if hours < 48:
        return f"{hours}h ago"
    days = hours // 24
    if days < 30:
        return f"{days}d ago"
    months = days // 30
    if months < 12:
        return f"{months}mo ago"
    years = months // 12
    return f"{years}y ago"


def git_log(cwd=None, max_count=40, grep=None, author=None, since=None, until=None, stat=False, branches=None):
    """Fetch a parseable git log stream with a stable, machine-friendly format.

    Returns a list of dicts describing each commit.
    """
    sep = "\x1e"  # record separator unlikely to appear in messages
    fieldsep = "\x1f"
    args = ["-C", (cwd or "."), "log"]
    if max_count:
        args += ["--max-count", str(max_count)]
    if grep:
        args += ["--grep", grep, "--regexp-ignore-case"]
    if author:
        args += ["--author", author]
    if since:
        args += ["--since", since]
    if until:
        args += ["--until", until]
    if branches:
        args += [branches]
    else:
        args += ["--all"]

    fmt = "%H%x1f%h%x1f%an%x1f%ae%x1f%aI%x1f%s%x1f%D%x1f%n%b"
    # Use git's own %x1e hex escape so commits are separated by the real byte.
    args += [
        f"--pretty=format:{fmt}%x1e",
    ]
    out = run_git(args, cwd=None)
    commits = []
    for record in out.split(sep):
        record = record.strip("\n")
        if not record:
            continue
        lines = record.split("\n")
        header = lines[0]
        parts = header.split(fieldsep)
        if len(parts) < 7:
            continue
        full, short, name, email, iso, subject, refs = parts[:7]
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
        commits.append(
            {
                "hash": full,
                "short": short,
                "author": name,
                "email": email,
                "date": _parse_ts(iso),
                "age": iso,
                "subject": subject,
                "refs": refs,
                "body": body,
                "added": 0,
                "removed": 0,
            }
        )
        commits[-1]["age_human"] = human_age(commits[-1]["date"])

    if stat:
        stats = git_stats(cwd=cwd, max_count=max_count, branches=branches)
        for c in commits:
            s = stats.get(c["hash"])
            if s:
                c.update(s)
    return commits


def git_stats(cwd=None, max_count=None, branches=None):
    """Fetch per-commit added/removed/file counts keyed by full hash.

    Uses a separate --numstat stream (clean to parse, unlike --stat output).
    """
    args = [
        "-C",
        (cwd or "."),
        "log",
        "--numstat",
        "--no-renames",
        "--pretty=format:%x1e%H",
    ]
    if max_count:
        args += ["--max-count", str(max_count)]
    if branches:
        args += [branches]
    else:
        args += ["--all"]
    out = run_git(args, cwd=None)
    stats = {}
    for rec in out.split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        lines = rec.split("\n")
        h = lines[0]
        added = removed = files = 0
        for ln in lines[1:]:
            parts = ln.split("\t")
            if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit():
                added += int(parts[0])
                removed += int(parts[1])
                files += 1
        stats[h] = {"added": added, "removed": removed, "changed_files": files}
    return stats


def current_branch(cwd=None):
    try:
        return run_git(["-C", (cwd or "."), "branch", "--show-current"], cwd=None).strip()
    except GitError:
        return None
