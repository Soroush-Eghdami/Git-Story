from dataclasses import dataclass
from datetime import datetime 
from pathlib import Path
import subprocess

@dataclass
class Commit:
    hash_: str
    author: str 
    files: list[str]
    date: datetime 
    message: str 
    files_changed: int
    insertions: int
    deletions: int
    
    
def get_commits(
    repo_path: str,
    since: str | None = None,
    author: str | None = None,
    revision: str | None = None,
) -> list[Commit]:
    """Get commits for repo_path, optionally filtered by revision/since/author."""
    cmd = ["git", "log", "--numstat", "--pretty=format:COMMIT|||%H|||%an|||%ad|||%s"]
    if since:
        cmd.append(f"--since={since}")
    if author:
        cmd.append(f"--author={author}")
    if revision:
        cmd.append(revision)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=repo_path,
    )
    if result.returncode != 0:
        return []
    raw = result.stdout
    
    chunks = raw.split("COMMIT|||")[1:]  # For skipping the first empty split
    
    commits = []
    
    for chunk in chunks: 
        parts = chunk.strip().split("\n", 1)
        header_line = parts[0]
        rest = parts[1] if len(parts) > 1 else "" # For handling empty commit cases
        
        hash_, author, date_str, message = header_line.split("|||", 3)
        
        insertions = deletions = files_changed = 0 
        files: list[str] = []
        if rest.strip():
            for line in rest.strip().splitlines():
                if not line.strip():
                    continue
                added, deleted, filename = line.split("\t", 2)
                files.append(filename.strip())
                insertions += int(added) if added != "-" else 0
                deletions += int(deleted) if deleted != "-" else 0
                files_changed += 1
                
        date = datetime.strptime(date_str.strip(), "%a %b %d %H:%M:%S %Y %z")
        
        commits.append(Commit(
            hash_=hash_,
            author=author,
            files=files,
            date=date,
            message=message,
            files_changed=files_changed,
            insertions=insertions,
            deletions=deletions,
        ))
    return commits


def validate_repo(repo_path: str) -> bool:
    """Checks if the repo_path is a valid git repository,"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            cwd=repo_path
        )
    except OSError:
        return False # Git is not found 
    if result.returncode != 0:
        return False
    return result.stdout.strip().lower() == "true"


if __name__ == "__main__":
    commits = get_commits(".")
    for c in commits[:3]:
        print(c.files)