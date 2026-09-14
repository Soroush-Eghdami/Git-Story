# git-story 📖

> Every repo tells a story. `git-story` reads yours.

A tiny CLI that turns any git repository's history into a beautiful terminal dashboard — commits, churn, streaks, habits, and hotspots, all in one glance.

```
╭──────────────────────────────╮
│  Git Stats for git-story     │
│  2026-09-14 -> 2026-09-14    │
╰──────────────────────────────╯

        Summary
┏━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric         ┃ Value ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Commits  │     2 │
│ Insertions     │   229 │
│ Deletions      │     5 │
│ Longest Streak │ 1 day │
│ Busiest Day    │ Mon   │
└────────────────┴───────┘

          Most Changed Files
┏━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ File     ┃ Commits ┃ Bar            ┃
┡━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ core.py  │       2 │ ██████████████ │
└──────────┴─────────┴────────────────┘
```

## ✨ What it tells you

- **Volume** — total commits, insertions `+`, deletions `-`
- **Timeline** — first → last commit date range
- **Momentum** — longest consecutive-day committing streak
- **Rhythm** — busiest weekday (are you a Monday warrior?)
- **Hotspots** — top 5 most-changed files with bar charts

## 🚀 Quickstart

```bash
# 1. Clone & enter
git clone <your-fork> git-story && cd git-story

# 2. Environment
python -m venv venv && ./venv/Scripts/activate  # Windows
pip install typer rich

# 3. Tell a story
python main.py              # current directory
python main.py /path/to/any/repo
```

No args? No problem — it defaults to `.`.

## 🧠 How it works

```
main.py ──▶ core.py ──▶ stats.py ──▶ display.py
  CLI        git log       counters      rich tables
```

| File         | Job |
|--------------|-----|
| `core.py`    | Parses `git log --numstat` into `Commit` objects, validates repos via `git rev-parse` |
| `stats.py`   | Aggregates `Stats`: totals, date range, streaks, weekdays, file hotspots |
| `display.py` | Renders it all with `rich` — panels, colored tables, bar charts |
| `main.py`    | Glues it together with `typer`: validate → analyze → render |

## 🛡️ Edge cases handled

- ❌ Not a git repo / path doesn't exist → friendly error, exit code `1`
- 🌱 Fresh repo, zero commits → `No commits found`, empty tables instead of a crash
- 🗂️ Binary files (`-` in numstat) → counted as files, `0` churn
- 📭 Empty commits → skipped gracefully

## 📦 Requirements

- Python 3.13+
- `typer`, `rich`
- `git` on your `PATH`

---
*Built for fun, useful for retros. Go run it on your oldest repo — you might be surprised.* 💛
