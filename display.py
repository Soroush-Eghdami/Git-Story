from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from stats import Stats

def render_stats(stats: Stats, repo_name: str = "") -> None:
    
    # The Table Header
    console = Console()
    
    first, last = stats.date_range
    if first and last:
        date_str = f"{first.strftime('%Y-%m-%d')} -> {last.strftime('%Y-%m-%d')}"
    else:
        date_str = "No Commits"
        
    title = f"Git Stats for {repo_name}" if repo_name else "Git Stats"
    header = Panel(f"[bold]{title}[/bold]\n{date_str}", style="cyan")

    
    # Summary Table
    summary = Table(title="Summary", show_header=True)
    summary.add_column("Metric", style="bold")
    summary.add_column("Value", justify="right")
    
    summary.add_row("Total Commits", str(stats.total_commits))
    summary.add_row("Insertions", str(stats.total_insertions))
    summary.add_row("Deletions", str(stats.total_deletions))
    summary.add_row("Longest Streak", f"{stats.longest_streak_days} days")
    summary.add_row("Busiest Weekday", stats.busiest_weekday or "N/A")
    # Message health + busiest hour (new insight rows)
    avg_len = getattr(stats, "avg_message_length", 0.0) or 0.0
    vague = getattr(stats, "vague_message_count", 0) or 0
    summary.add_row("Avg Msg Length", f"{avg_len:.1f} chars")
    summary.add_row("Vague Messages", str(vague))
    bh = getattr(stats, "busiest_hour", None)
    summary.add_row("Busiest Hour", f"{bh:02d}:00" if bh is not None else "N/A")
    
    
    # Top Files Table
    files_table = Table(title="Most Changed Files", show_header=True)
    files_table.add_column("File")
    files_table.add_column("Commits", justify="right")
    files_table.add_column("Bar")
    
    if stats.most_changed_files:
        max_count = max(c for _, c in stats.most_changed_files)
        for filename, count in stats.most_changed_files:
            bar_len = int(count / max_count * 30) if max_count else count
            bar = "#" * max(bar_len, 1)
            files_table.add_row(filename, str(count), f"[blue]{bar}[/blue]")
    else:
        files_table.add_row("—", "No files", "")

    # Authors table
    authors_table = Table(title="Authors", show_header=True)
    authors_table.add_column("Author")
    authors_table.add_column("Commits", justify="right")
    for author, count in (getattr(stats, "commits_per_author", None) or []):
        authors_table.add_row(author, str(count))
    if not (getattr(stats, "commits_per_author", None) or []):
        authors_table.add_row("-", "0")

    # File types table
    types_table = Table(title="File Types", show_header=True)
    types_table.add_column("Extension")
    types_table.add_column("Touches", justify="right")
    for ext, count in (getattr(stats, "file_types", None) or []):
        types_table.add_row(ext, str(count))
    if not (getattr(stats, "file_types", None) or []):
        types_table.add_row("-", "0")

    # Hour heatmap: one scaled bar per hour (00-23)
    hours_table = Table(title="Commits by Hour", show_header=True)
    hours_table.add_column("Hour", justify="right")
    hours_table.add_column("Commits", justify="right")
    hours_table.add_column("Bar")
    hourly = getattr(stats, "hourly_counts", None) or [0] * 24
    peak = max(hourly) if hourly else 0
    for h, count in enumerate(hourly):
        bar = "#" * (int(count / peak * 20) if peak else 0)
        style = "[yellow]" if h == getattr(stats, "busiest_hour", -1) else ""
        end = "[/]" if style else ""
        hours_table.add_row(f"{h:02d}", str(count), f"{style}{bar}{end}")

    # Weekly activity sparkline
    activity = getattr(stats, "weekly_activity", None) or []
    if activity:
        counts = [c for _, c in activity]
        peak_w = max(counts)
        blocks = " .:-=+*#%@"
        spark = "".join(
            blocks[int(c / peak_w * (len(blocks) - 1))] if peak_w else " "
            for c in counts
        )
        span = f"{activity[0][0]} -> {activity[-1][0]}" if len(activity) > 1 else activity[0][0]
        activity_panel = Panel(f"[bold]{spark}[/bold]\n{span} ({stats.total_commits} commits)",
                               title="Activity (per week)")
    else:
        activity_panel = Panel("No activity", title="Activity (per week)")

    
    # Print everything
    console.print(header)
    console.print()
    console.print(summary)
    console.print()
    console.print(files_table)
    console.print()
    console.print(authors_table)
    console.print()
    console.print(types_table)
    console.print()
    console.print(hours_table)
    console.print()
    console.print(activity_panel)
    
    
    
if __name__ == "__main__":
    from core import get_commits
    from stats import compute_stats
    from pathlib import Path

    repo_path = "."
    commits = get_commits(repo_path)
    stats = compute_stats(commits)
    render_stats(stats, repo_name=Path(repo_path).resolve().name)