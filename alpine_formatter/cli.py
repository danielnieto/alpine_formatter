import typer
from pathlib import Path
from pathspec import GitIgnoreSpec
from typing import Optional, List
from alpine_formatter.exceptions import InvalidPathError

app = typer.Typer()

SUPPORTED_EXTENSIONS = {".html", ".jinja"}


def load_gitignore(path: Path) -> Optional[GitIgnoreSpec]:
    """
    Load and parse .gitignore file if it exists in the given directory or any of its parents
    """
    absolute_path = path.resolve()
    dirs_to_look = list(absolute_path.parents)

    # if the path is a dir, include it in the list of dirs to search
    if absolute_path.is_dir():
        dirs_to_look = [absolute_path] + dirs_to_look

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
    is_git_ignored = gitignore.match_file(file) if gitignore else False
    return is_supported_extension and not is_git_ignored


def collect_files(path: Path, use_gitignore=True) -> List[Path]:
    """
    Find and return all files to be modified on the given path.
    """
    if not path.exists():
        raise InvalidPathError(f"{path} does not exist.")

    gitignore = load_gitignore(path) if use_gitignore else None
    collected = []

    if path.is_file():
        if should_process(path, gitignore):
            collected.append(path)
    elif path.is_dir():
        for file in path.rglob("*"):
            if should_process(file, gitignore):
                collected.append(file)
    else:
        raise InvalidPathError(f"{path} is invalid.")

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
