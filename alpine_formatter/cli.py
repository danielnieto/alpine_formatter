import typer
from pathlib import Path
from pathspec import GitIgnoreSpec
from typing import Optional, List
from alpine_formatter.exceptions import InvalidPathError

app = typer.Typer()

SUPPORTED_EXTENSIONS = {".html", ".jinja"}


def load_gitignore(path: Path) -> Optional[GitIgnoreSpec]:
    """
    Load and parse .gitignore file if it exists in the given directory or any of it's parents
    """
    absolute_path = path.resolve()
    dirs_to_look = [absolute_path] + list(absolute_path.parents)

    for directory in dirs_to_look:
        gitignore_path = directory / ".gitignore"

        if gitignore_path.exists():
            with open(gitignore_path) as f:
                return GitIgnoreSpec.from_lines(f)

    return None


def should_process(file: Path, gitignore: Optional[GitIgnoreSpec] = None) -> bool:
    """
    Determine if a file should be processed based on its extension and .gitignore rules.
    """
    is_supported_extension = file.suffix in SUPPORTED_EXTENSIONS
    is_git_ignored = False
    if gitignore:
        is_git_ignored = gitignore.match_file(file)
    return is_supported_extension and not is_git_ignored


def collect_files(path: Path, use_gitignore=True) -> List[Path]:
    """
    Find and return all files to be modified on the given path.
    """
    if not path.exists():
        raise InvalidPathError(f"{path} does not exist.")

    collected = []

    if path.is_file():
        if should_process(path):
            collected.append(path)
    elif path.is_dir():
        gitignore = load_gitignore(path) if use_gitignore else None
        for file in path.rglob("*"):
            if should_process(file, gitignore):
                collected.append(file)

    return collected


@app.command()
def format(path: Path):
    """
    Format files in a given path.
    """
    files = collect_files(path)
    for file in files:
        print(file)


if __name__ == "__main__":
    app()
