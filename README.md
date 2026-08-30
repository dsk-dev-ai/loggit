<p align="center">
  <img src="https://img.shields.io/badge/dependencies-ZERO-22c55e?style=flat-square" alt="zero deps">
  <img src="https://img.shields.io/badge/python-3.8+-4B8BBE?style=flat-square&logo=python&logoColor=white" alt="python">
  <img src="https://img.shields.io/pypi/v/loggit?style=flat-square" alt="pypi version">
  <a href="https://github.com/dsk-dev-ai/loggit/actions"><img src="https://img.shields.io/github/actions/workflow/status/dsk-dev-ai/loggit/ci.yml?style=flat-square" alt="CI"></a>
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="MIT">
  <a href="https://github.com/users/dsk-dev-ai/packages/container/package/loggit"><img src="https://img.shields.io/badge/docker-ghcr-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker GHCR"></a>
</p>

# loggit 🪵

**Your git history, actually readable.** A friendly terminal explorer that turns `git log` into color, graphs, and answers — zero dependencies.

Stop squinting at `git log --oneline`. `loggit` gives you a clear, colored view of **what your repository is really doing** — commits, authors, churn, and pace — in one command. Pure Python stdlib, works on any laptop, installs instantly.

```
▌ main
  17 commits

1000a50   Add Docker/GHCR badge + usage section to README
    dsk-dev-ai  ·  6m ago
    +14/-0 in 1 file(s)
```

---

## ✨ Features

| | |
|---|---|
| 🎨 **Pretty output** | colored, aligned, compact log view with refs, ages, and authors |
| 👥 **Author stats** | per-developer commit counts and line churn as a bar chart |
| 📈 **Pace metrics** | commits/day, authors, and added/removed lines over any window |
| 🔎 **Powerful filters** | `--grep`, `--author`, `--since`, `--until`, `--branch` |
| 📦 **Machine-readable** | `loggit json` for one-line-per-commit JSON |
| 💸 **100% free** | zero dependencies, no AI, no server, no API keys |

## 🔧 Install

```bash
pip install loggit
```

No dependencies. No compiled extensions. Works on Python 3.8+ everywhere.

## 🐳 Docker

```bash
docker pull ghcr.io/dsk-dev-ai/loggit:latest
docker run --rm -v "$PWD:/repo" -w /repo ghcr.io/dsk-dev-ai/loggit:latest authors
```

## 🚀 Usage

```bash
loggit                        # pretty log of recent commits (default: 40)
loggit -n 100                 # show more
loggit --stat                 # add per-commit +added/-removed lines
loggit --grep "docker"        # only commits mentioning "docker"
loggit --author "ada"         # only commits by a specific developer
loggit --since "2 weeks ago"  # recent activity only
loggit authors                # per-developer commit & churn summary
loggit pace                   # overall stats + velocity
loggit json                   # JSON, one object per line (great for scripting)
```

See `loggit --help` for the full list of options.

<details>
<summary><b>JSON output (for piping into your tools)</b></summary>

```bash
loggit json -n 5 > commits.ndjson
```

```json
{"hash": "1000a50", "author": "dsk-dev-ai", "date": "2026-08-31T02:14:39+05:30", "subject": "Add Docker/GHCR badge", "refs": "HEAD -> main"}
```
</details>

## 🧠 How it works

1. **Runs `git log`** with a stable, machine-friendly pretty-format.
2. **Parses** commits, refs, dates, and message bodies (stdlib only).
3. **Renders** a clean, terminal-aware view — colors auto-disable when piped.
4. **Summarizes** per-author and per-window metrics on demand.

## 🤝 Contributing

Have an idea or spotted a quirk? Open an issue or a pull request. Want to add a metric or a new view? It's a focused module in `loggit/`.

## 📄 License

[MIT](LICENSE) — free to use, modify, and distribute.

## ⭐ Support

If `loggit` saved you a minute of `git log` squinting, **give it a star** ⭐.
