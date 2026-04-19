from pathlib import Path

def ensure_dir(path: Path) -> None:
    """Ensure that a directory exists."""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

def ensure_file(path: Path) -> None:
    """Ensure that a file exists (creates an empty file if it doesn't)."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
