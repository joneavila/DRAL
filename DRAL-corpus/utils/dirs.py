from pathlib import Path


def make_dirs_in_path_if_not_exist(path: Path) -> None:
    """
    Create all directories in a path if they do not exist.

    Args:
        path (Path): Path with existing or nonexisting directories.
    """
    path.mkdir(parents=True, exist_ok=True)
