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
- **Timeline** — first -> last commit date range
- **Momentum** — longest consecutive-day committing streak + weekly activity sparkline
- **Rhythm** — busiest weekday *and* busiest hour (are you a midnight coder?)
- **Hotspots** — top 5 most-changed files with bar charts
- **People** — commits-per-author table for team repos
- **Hygiene** — average message length + vague-message counter (`wip`, `fix`, `temp`…)
- **Stack** — churn grouped by file extension (`.py` vs `.md` vs …)

## 🚀 Quickstart

```bash
# 1. Clone & enter
git clone <your-fork> git-story && cd git-story

# 2. Environment
python -m venv venv && ./venv/Scripts/activate  # Windows
pip install typer rich

# 3. Tell a story
python main.py                    # current directory
python main.py /path/to/any/repo
python main.py "D:\My Stuff\Repo" # quote paths with spaces
```

No args? No problem — it defaults to `.`.

## 🎛️ Flags

```bash
# Filter the story
python main.py . --since "1 month ago"
python main.py . --since "2026-01-01" --author "Alice"

# Export it (paste into a PR or README)
python main.py . --export json
python main.py . --export md

# Compare two revisions side by side
python main.py . --compare main..dev
```

| Flag | Job |
|------|-----|
| `--since` | Passes `--since=` to `git log` — date, `1 month ago`, etc. |
| `--author` | Passes `--author=` to `git log` — filters by name/email pattern |
| `--export json\|md` | Dumps stats as JSON or Markdown instead of the rich UI |
| `--compare A..B` | Renders two dashboards: `A` vs `B` (also accepts `...`, `,`, space) |

## 🧠 How it works

```
main.py ──▶ core.py ──▶ stats.py ──▶ display.py
  CLI        git log       counters      rich tables
```

| File         | Job |
|--------------|-----|
| `core.py`    | Parses `git log --numstat` into `Commit` objects, validates repos, handles `--since`/`--author`/revision filters |
| `stats.py`   | Aggregates `Stats`: totals, streaks, weekdays, hours, authors, message health, file types, weekly activity + JSON/Markdown exporters |
| `display.py` | Renders it all with `rich` — panels, tables, hour heatmap, activity sparkline |
| `main.py`    | Glues it together with `typer`: validate → filter → analyze → render/export/compare |

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
