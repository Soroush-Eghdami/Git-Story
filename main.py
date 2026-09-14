import typer
from pathlib import Path

from core import get_commits, validate_repo
from stats import compute_stats
from display import render_stats

app = typer.Typer()


@app.command()
def main(repo_path: str = typer.Argument(".", help="Path to the git repo (defaults to current directory)")):
    """
    Analyze a git repo's commit history and display stats.
    """
    # TODO 1: validate before doing anything else
    if not validate_repo(repo_path):
        typer.echo(f"Error: '{repo_path}' is not a valid git repository.", err=True)
        raise typer.Exit(code=1)

    # TODO 2: get commits, compute stats
    commits = get_commits(repo_path)
    stats = compute_stats(commits)

    # TODO 3: zero commits — compute_stats([]) is safe (zeros/None/[]),
    # but tell the user explicitly rather than showing only empty tables.
    if not commits:
        typer.echo("No commits found in this repository.")

    # TODO 4: friendly name for the header panel
    repo_name = Path(repo_path).resolve().name

    # TODO 5: render
    render_stats(stats, repo_name=repo_name)


if __name__ == "__main__":
    app()