from core import Commit
from collections import Counter
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Stats:
    total_commits: int
    total_insertions: int
    total_deletions: int
    date_range: tuple[datetime, datetime]       # (first commit, last commit)
    longest_streak_days: int
    busiest_weekday: str                         # e.g. "Tuesday"
    most_changed_files: list[tuple[str, int]]    # top N: [(filename, count), ...]
    # New insight fields (defaulted so old callers keep working)
    commits_per_author: list[tuple[str, int]] = None
    avg_message_length: float = 0.0
    vague_message_count: int = 0
    busiest_hour: int | None = None
    hourly_counts: list[int] = None              # 24 buckets, index == hour
    file_types: list[tuple[str, int]] = None     # [(extension, touches), ...]
    weekly_activity: list[tuple[str, int]] = None  # [(YYYY-Www, commits), ...]

VAGUE_WORDS = {"wip", "fix", "fixes", "fixed", "temp", "tmp", "test", "update", "updates", "updated", "stuff", "misc", "tweak", "tweaks", "wip:"}


def _extension_of(filename: str) -> str:
    # Handles renames like "old => new.py" by looking at the last path part.
    name = filename.split("=>")[-1].strip().strip("{} ").split("/")[-1].split("\\")[-1]
    if "." in name and not name.startswith("."):
        return "." + name.rsplit(".", 1)[-1].lower()
    return "(no ext)"


def stats_to_dict(stats: Stats) -> dict:
    first, last = stats.date_range
    return {
        "total_commits": stats.total_commits,
        "total_insertions": stats.total_insertions,
        "total_deletions": stats.total_deletions,
        "date_range": [
            first.isoformat() if first else None,
            last.isoformat() if last else None,
        ],
        "longest_streak_days": stats.longest_streak_days,
        "busiest_weekday": stats.busiest_weekday,
        "most_changed_files": [list(x) for x in (stats.most_changed_files or [])],
        "commits_per_author": [list(x) for x in (stats.commits_per_author or [])],
        "avg_message_length": stats.avg_message_length,
        "vague_message_count": stats.vague_message_count,
        "busiest_hour": stats.busiest_hour,
        "hourly_counts": list(stats.hourly_counts or [0] * 24),
        "file_types": [list(x) for x in (stats.file_types or [])],
        "weekly_activity": [list(x) for x in (stats.weekly_activity or [])],
    }


def stats_to_markdown(stats: Stats, repo_name: str = "") -> str:
    d = stats_to_dict(stats)
    lines = [f"# git-story report for {repo_name or 'repo'}", ""]
    lines.append(f"- Total commits: {d['total_commits']}")
    lines.append(f"- Insertions: +{d['total_insertions']} / Deletions: -{d['total_deletions']}")
    dr = d["date_range"]
    lines.append(f"- Date range: {dr[0] or '?'} -> {dr[1] or '?'}")
    lines.append(f"- Longest streak: {d['longest_streak_days']} days")
    lines.append(f"- Busiest weekday: {d['busiest_weekday'] or 'N/A'} / Busiest hour: {d['busiest_hour'] if d['busiest_hour'] is not None else 'N/A'}")
    lines.append(f"- Avg message length: {d['avg_message_length']:.1f} chars, vague messages: {d['vague_message_count']}")
    lines.append("")
    lines.append("## Top files")
    for f, c in d["most_changed_files"]:
        lines.append(f"- `{f}` - {c}")
    lines.append("")
    lines.append("## Authors")
    for a, c in d["commits_per_author"]:
        lines.append(f"- {a} - {c}")
    lines.append("")
    lines.append("## File types")
    for ext, c in d["file_types"]:
        lines.append(f"- `{ext}` - {c}")
    return "\n".join(lines) + "\n"


def compute_stats(commits: list[Commit]) -> Stats:
    """Compute aggregate stats from a list of Commit objects."""
    
    total_commits = len(commits)
    total_insertions = sum(c.insertions for c in commits)
    total_deletions = sum(c.deletions for c in commits)



    first_commit = min(c.date for c in commits) if commits else None
    last_commit = max(c.date for c in commits) if commits else None
    # Error handling for empty commits list
    if first_commit is None or last_commit is None:
        date_range = (None, None)
    else:
        date_range = (first_commit, last_commit)



    unique_days = sorted({c.date.date() for c in commits})
    if not unique_days:
        longest_streak_days = 0
    else:
        cur = best = 1
        for i in range(1, len(unique_days)):
            if (unique_days[i] - unique_days[i-1]).days == 1:
                cur += 1
            else:
                cur = 1
            best = max(best, cur)    
        longest_streak_days = best
    
    if not commits:
        busiest_weekday = None
    else:
        busiest_weekday = Counter(c.date.strftime("%A") for c in commits).most_common(1)[0][0]

    most_changed_files = Counter(f for c in commits for f in c.files).most_common(5)

    # Author breakdown
    commits_per_author = Counter(c.author for c in commits).most_common()

    # Commit message health
    if commits:
        lengths = [len((c.message or "").strip()) for c in commits]
        avg_message_length = sum(lengths) / len(lengths)
        vague_message_count = sum(
            1 for c in commits if (c.message or "").strip().lower() in VAGUE_WORDS
        )
    else:
        avg_message_length = 0.0
        vague_message_count = 0

    # Time-of-day heatmap (24 hourly buckets)
    hourly_counts = [0] * 24
    for c in commits:
        try:
            hourly_counts[c.date.hour] += 1
        except Exception:
            pass
    busiest_hour = max(range(24), key=lambda h: hourly_counts[h]) if commits else None

    # File type breakdown (touches per extension)
    file_types = Counter(_extension_of(f) for c in commits for f in c.files).most_common()

    # Weekly activity for sparkline (ISO week buckets, chronological)
    per_week: dict[str, int] = {}
    for c in commits:
        try:
            iso_year, iso_week, _ = c.date.isocalendar()
            key = f"{iso_year}-W{iso_week:02d}"
            per_week[key] = per_week.get(key, 0) + 1
        except Exception:
            pass
    weekly_activity = sorted(per_week.items())
    
    return Stats(
    total_commits=total_commits,
    total_insertions=total_insertions,
    total_deletions=total_deletions,
    date_range=date_range,
    longest_streak_days=longest_streak_days,
    busiest_weekday=busiest_weekday,
    most_changed_files=most_changed_files,
    commits_per_author=commits_per_author,
    avg_message_length=avg_message_length,
    vague_message_count=vague_message_count,
    busiest_hour=busiest_hour,
    hourly_counts=hourly_counts,
    file_types=file_types,
    weekly_activity=weekly_activity,
)
    
if __name__ == "__main__":
    from core import get_commits
    commits = get_commits(".")
    stats = compute_stats(commits)
    print(stats)