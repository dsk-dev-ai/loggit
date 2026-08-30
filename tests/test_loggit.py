"""Tests for loggit (zero-dependency, uses a scratch git repo)."""
import os
import shutil
import subprocess
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loggit.gitcore import GitError, git_log, human_age, is_repo, run_git  # noqa: E402
from loggit.render import authors_summary, pace_summary  # noqa: E402


def _git(repo, *args):
    subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True)


@pytest.fixture
def repo():
    tmp = tempfile.mkdtemp()
    _git(tmp, "init", "-q")
    _git(tmp, "config", "user.email", "dev@example.com")
    _git(tmp, "config", "user.name", "Dev Tester")
    return tmp


def _commit(repo, msg, file="a.txt", content="x\n"):
    path = os.path.join(repo, file)
    with open(path, "a") as fh:
        fh.write(content)
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", msg)


def test_is_repo(repo):
    assert is_repo(repo) is True
    temp = tempfile.mkdtemp()
    assert is_repo(temp) is False


def test_git_log_parses(repo):
    _commit(repo, "first commit")
    _commit(repo, "second commit")
    commits = git_log(cwd=repo, max_count=10)
    assert len(commits) == 2
    assert commits[0]["subject"] == "second commit"
    assert commits[0]["author"] == "Dev Tester"
    assert commits[1]["subject"] == "first commit"
    for c in commits:
        assert c["hash"]
        assert c["short"]
        assert c["age_human"]


def test_git_log_grep_filter(repo):
    _commit(repo, "adds awesome feature")
    _commit(repo, "fixes typo")
    commits = git_log(cwd=repo, max_count=10, grep="awesome")
    assert len(commits) == 1
    assert commits[0]["subject"] == "adds awesome feature"


def test_git_log_author_filter(repo):
    _commit(repo, "alpha")
    commits = git_log(cwd=repo, max_count=10, author="Tester")
    assert len(commits) == 1
    commits = git_log(cwd=repo, max_count=10, author="Nobody")
    assert len(commits) == 0


def test_authors_summary(repo):
    _commit(repo, "one")
    _commit(repo, "two")
    _commit(repo, "three")
    rows = authors_summary(git_log(cwd=repo, max_count=10, stat=True))
    assert len(rows) == 1
    assert rows[0]["count"] == 3
    assert rows[0]["added"] >= 3


def test_pace_summary(repo):
    _commit(repo, "one")
    _commit(repo, "two")
    p = pace_summary(git_log(cwd=repo, max_count=10, stat=True))
    assert p["commits"] == 2
    assert p["authors"] == 1
    assert p["avg_per_day"] > 0


def test_human_age():
    import datetime

    assert "ago" in human_age(datetime.datetime.now() - datetime.timedelta(hours=3))


def test_git_error_when_no_git():
    with pytest.raises(GitError):
        run_git(["--definitely-not-a-command"])
