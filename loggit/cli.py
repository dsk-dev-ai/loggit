"""loggit CLI - a friendly terminal git history explorer (zero dependencies)."""
import argparse
import sys
from datetime import datetime

from loggit import __version__
from loggit.gitcore import (
    GitError,
    current_branch,
    git_log,
    is_repo,
)
from loggit.render import (
    RESET,
    BOLD,
    DIM,
    CYAN,
    GREEN,
    RED,
    YELLOW,
    authors_summary,
    pace_summary,
    render_authors,
    render_commit,
)


def build_parser():
    p = argparse.ArgumentParser(
        prog="loggit",
        description="Friendly terminal git history explorer. Zero dependencies.",
    )
    p.add_argument("-n", "--max-count", type=int, default=40, help="commits to show (default: 40)")
    p.add_argument("--grep", help="only commits whose message matches")
    p.add_argument("--author", help="only commits by this author (name or email)")
    p.add_argument("--since", help="only commits since this date/ref")
    p.add_argument("--until", help="only commits until this date/ref")
    p.add_argument("--stat", action="store_true", help="show added/removed lines per commit")
    p.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    p.add_argument("--branch", help="limit to a specific branch (default: all)")
    p.add_argument("--version", action="version", version=f"loggit {__version__}")
    sub = p.add_subparsers(dest="command")

    authors_p = sub.add_parser("authors", help="per-author commit/churn summary")
    authors_p.add_argument("-n", "--max-count", type=int, default=40, help="commits to consider")
    authors_p.add_argument("--branch", help="limit to a specific branch")
    authors_p.add_argument("--no-color", action="store_true", help="disable ANSI colors")

    pace_p = sub.add_parser("pace", help="overall stats for the captured window")
    pace_p.add_argument("-n", "--max-count", type=int, default=40, help="commits to consider")
    pace_p.add_argument("--branch", help="limit to a specific branch")
    pace_p.add_argument("--no-color", action="store_true", help="disable ANSI colors")

    json_p = sub.add_parser("json", help="machine-readable log (objects, one per line)")
    json_p.add_argument("-n", "--max-count", type=int, default=40, help="commits to emit")
    json_p.add_argument("--branch", help="limit to a specific branch")
    json_p.add_argument("--grep", help="only commits whose message matches")
    json_p.add_argument("--author", help="only commits by this author")
    json_p.add_argument("--since", help="only commits since this date/ref")
    json_p.add_argument("--until", help="only commits until this date/ref")
    json_p.add_argument("--no-color", action="store_true", help="disable ANSI colors")

    return p


def _disable_color():
    sys.stdout.isatty = lambda: False


def cmd_log(args):
    commits = git_log(
        cwd=".",
        max_count=args.max_count,
        grep=args.grep,
        author=args.author,
        since=args.since,
        until=args.until,
        stat=args.stat,
        branches=args.branch,
    )
    branch = current_branch(".")
    title = f" {branch or 'repository'} "
    print(f"\n{BOLD}{CYAN}▌{title}{RESET}")
    print(f"{DIM}  {len(commits)} commits{RESET}")
    for c in commits:
        print()
        print(render_commit(c))


def cmd_authors(args):
    commits = git_log(cwd=".", max_count=args.max_count, branches=args.branch, stat=True)
    rows = authors_summary(commits)
    print(f"\n{BOLD}{CYAN}▌ Authors{RESET}")
    print(render_authors(rows))


def cmd_pace(args):
    commits = git_log(cwd=".", max_count=args.max_count, branches=args.branch, stat=True)
    p = pace_summary(commits)
    print(f"\n{BOLD}{CYAN}▌ Pace / stats{RESET}")
    print(f"  commits          {p['commits']}")
    print(f"  authors          {p['authors']}")
    print(f"  window           {p['span_days']:.1f} days")
    print(f"  avg/day          {p['avg_per_day']:.2f}")
    print(f"  lines added      {GREEN}+{p['added']}{RESET}")
    print(f"  lines removed    {RED}-{p['removed']}{RESET}")


def cmd_json(args):
    import json as _json

    commits = git_log(
        cwd=".",
        max_count=args.max_count,
        grep=args.grep,
        author=args.author,
        since=args.since,
        until=args.until,
        stat=False,
        branches=args.branch,
    )
    for c in commits:
        out = {
            "hash": c["hash"],
            "short": c["short"],
            "author": c["author"],
            "email": c["email"],
            "date": c["age"],
            "subject": c["subject"],
            "refs": c["refs"].strip(),
        }
        print(_json.dumps(out))


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.no_color:
        _disable_color()

    if not is_repo("."):
        print(f"{RED}✗ not inside a git repository{RESET}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.command == "authors":
            cmd_authors(args)
        elif args.command == "pace":
            cmd_pace(args)
        elif args.command == "json":
            cmd_json(args)
        else:
            cmd_log(args)
    except GitError as exc:
        print(f"{RED}✗ {exc}{RESET}", file=sys.stderr)
        sys.exit(1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
