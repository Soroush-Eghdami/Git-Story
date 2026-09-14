import typer
from pathlib import Path

from core import get_commits, validate_repo
from stats import compute_stats, stats_to_dict, stats_to_markdown
from display import render_stats

app = typer.Typer()


def _parse_compare(spec: str) -> tuple[str, str]:
    # Accept "main..dev", "main...dev", "main,dev", or "main dev".
    for sep in ("...", "..", ",", " "):
        if sep in spec:
            a, b = spec.split(sep, 1)
            return a.strip(), b.strip()
    raise typer.BadParameter("Use --compare as 'rev1..rev2' (e.g. main..dev).")


@app.command()
def main(
    repo_path: str = typer.Argument(".", help="Path to the git repo (defaults to current directory)"),
    since: str | None = typer.Option(None, help='Only commits since date, e.g. "1 month ago" or "2026-01-01"'),
    author: str | None = typer.Option(None, help='Filter by author, e.g. "Alice"'),
    export: str | None = typer.Option(None, help="Export instead of rendering: 'json' or 'md'"),
    compare: str | None = typer.Option(None, help="Compare two revisions side by side, e.g. 'main..dev'"),
):
    """
    Analyze a git repo's commit history and display stats.
    """
    # TODO 1: validate before doing anything else
    if not validate_repo(repo_path):
        typer.echo(f"Error: '{repo_path}' is not a valid git repository.", err=True)
        raise typer.Exit(code=1)

    # Compare mode: stats for revA vs revB side by side
    if compare:
        rev_a, rev_b = _parse_compare(compare)
        commits_a = get_commits(repo_path, since=since, author=author, revision=rev_a)
        commits_b = get_commits(repo_path, since=since, author=author, revision=rev_b)
        stats_a = compute_stats(commits_a)
        stats_b = compute_stats(commits_b)
        typer.echo(f"== {rev_a} ({len(commits_a)} commits) vs {rev_b} ({len(commits_b)} commits) ==")
        render_stats(stats_a, repo_name=f"{Path(repo_path).resolve().name}@{rev_a}")
        render_stats(stats_b, repo_name=f"{Path(repo_path).resolve().name}@{rev_b}")
        return

    # TODO 2: get commits, compute stats
    commits = get_commits(repo_path, since=since, author=author)
    stats = compute_stats(commits)

    # TODO 3: zero commits — compute_stats([]) is safe (zeros/None/[]),
    # but tell the user explicitly rather than showing only empty tables.
    if not commits:
        typer.echo("No commits found in this repository.")

    # TODO 4: friendly name for the header panel
    repo_name = Path(repo_path).resolve().name

    # --export flag: dump JSON/Markdown instead of the rich UI
    if export:
        fmt = export.lower().strip().lstrip(".")
        if fmt == "json":
            import json
            typer.echo(json.dumps(stats_to_dict(stats), indent=2))
        elif fmt in ("md", "markdown"):
            typer.echo(stats_to_markdown(stats, repo_name=repo_name))
        else:
            typer.echo("Error: --export must be 'json' or 'md'.", err=True)
            raise typer.Exit(code=1)
        return

    # TODO 5: render
    render_stats(stats, repo_name=repo_name)


if __name__ == "__main__":
    app()