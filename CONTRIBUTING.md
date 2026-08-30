# Contributing to loggit

Thanks for wanting to help! `loggit` is a small, focused, zero-dependency git-history explorer — that's its superpower. Please keep changes aligned with that spirit.

## Getting started

```bash
git clone https://github.com/dsk-dev-ai/loggit.git
cd loggit
python -m pytest
```

No third-party dependencies, no virtualenv required — pure Python stdlib.

## How to contribute

1. **Open an issue** first for any bug or feature so we can discuss the approach.
2. **Fork** the repo and create a branch: `git checkout -b feat/my-change`.
3. **Write or update tests** in `tests/` — every change should be covered.
4. **Run the tests**: `python -m pytest` (all must pass).
5. Commit with a clear, conventional message (e.g. `feat: ...`, `fix: ...`, `docs: ...`).
6. Open a **pull request** back to `main`.

## Guidelines

- **Zero new dependencies.** Prefer stdlib. If you must add one, start a discussion first.
- Parsing must stay robust across git versions and repos — cover edge cases with tests.
- Keep terminal-aware output: colors auto-disable when piped.
- Follow the existing code style in `loggit/`.

## Project structure

```
loggit/
  cli.py      # command-line entry point
  gitcore.py  # runs & parses `git log` (stdlib only)
  render.py   # terminal rendering, colors, charts
tests/        # pytest suite
```

## Questions?

Open an issue tagged `question`, or reach out via [GitHub Discussions](https://github.com/dsk-dev-ai/loggit/discussions) if enabled.
