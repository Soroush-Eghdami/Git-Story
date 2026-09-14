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
    
    
    # Top Files Table
    files_table = Table(title="Most Changed Files", show_header=True)
    files_table.add_column("File")
    files_table.add_column("Commits", justify="right")
    files_table.add_column("Bar")
    
    if stats.most_changed_files:
        max_count = max(c for _, c in stats.most_changed_files)
        for filename, count in stats.most_changed_files:
            bar_len = int(count / max_count * 30) if max_count else count
            bar = "█" * max(bar_len, 1)
            files_table.add_row(filename, str(count), f"[blue]{bar}[/blue]")
    else:
        files_table.add_row("—", "No files", "")

    
    # Print everything
    console.print(header)
    console.print()
    console.print(summary)
    console.print()
    console.print(files_table)    
    
    
    
if __name__ == "__main__":
    from core import get_commits
    from stats import compute_stats
    from pathlib import Path

    repo_path = "."
    commits = get_commits(repo_path)
    stats = compute_stats(commits)
    render_stats(stats, repo_name=Path(repo_path).resolve().name)