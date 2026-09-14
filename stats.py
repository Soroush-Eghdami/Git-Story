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
    
    return Stats(
    total_commits=total_commits,
    total_insertions=total_insertions,
    total_deletions=total_deletions,
    date_range=date_range,
    longest_streak_days=longest_streak_days,
    busiest_weekday=busiest_weekday,
    most_changed_files=most_changed_files,
)
    
if __name__ == "__main__":
    from core import get_commits
    commits = get_commits(".")
    stats = compute_stats(commits)
    print(stats)