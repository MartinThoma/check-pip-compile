# Core Library modules
import datetime
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# Third party modules
import click

# First party modules
import check_pip_compile


@click.version_option(version=check_pip_compile.__version__)
@click.command()
@click.argument(
    "paths", type=click.Path(exists=True, file_okay=True, dir_okay=True), nargs=-1
)
def entry_point(paths):
    """Check if pip-compile needs to be run."""
    succeeded = True
    for in_file in paths:
        if os.path.isdir(in_file):
            tmp = check_directory(in_file)
        else:
            txt_file: Optional[str] = get_corresponding_txt_file(in_file)
            if not txt_file or not os.path.isfile(txt_file):
                txt_file = None
            tmp = check_file(in_file, txt_file)
        succeeded = succeeded and tmp
    if not succeeded:
        sys.exit(-1)


def check_directory(path: str) -> bool:
    in_files = discover_in_files(path)
    txt_files = discover_txt_files(path)
    matched_files = match_in_with_txt(in_files, txt_files)

    succeeded = True
    for in_file, txt_file in matched_files:
        tmp = check_file(in_file, txt_file)
        succeeded = tmp and succeeded
    return succeeded


def check_file(in_file: Optional[str], txt_file: Optional[str]) -> bool:
    """Return True, if it's ok."""
    succeeded = True
    if in_file is None:
        print(f"WARNING: {txt_file} has no corresponding in file")
    elif txt_file is None:
        print(f"Run 'pip-compile {in_file}', as no corresponding txt file exists")
        succeeded = False
    else:
        in_age = datetime.datetime.fromtimestamp(os.path.getmtime(in_file))
        txt_age = datetime.datetime.fromtimestamp(os.path.getmtime(txt_file))
        if in_age > txt_age:
            print(
                f"Run 'pip-compile {in_file}' ({in_age}), as {txt_file} "
                f"({txt_age}) might be outdated"
            )
            succeeded = False
    return succeeded


def discover_in_files(path: str) -> List[str]:
    p = Path(path)
    in_files = [str(el) for el in p.glob("*.in")]
    if os.path.isfile(p / "setup.py"):
        in_files.append(str(p / "setup.py"))
    return in_files


def discover_txt_files(path: str) -> List[str]:
    p = Path(path)
    return [str(el) for el in p.glob("*.txt")]


def get_corresponding_txt_file(in_file: str) -> str:
    if in_file.endswith("setup.py"):
        txt_file = in_file[: -len("setup.py")] + "requirements.txt"
    else:
        txt_file = in_file[:-2] + "txt"
    return txt_file


def match_in_with_txt(
    in_files: List[str], txt_files: List[str]
) -> List[Tuple[Optional[str], Optional[str]]]:
    matched_files: List[Tuple[Optional[str], Optional[str]]] = []
    for in_file in in_files:
        txt_file = get_corresponding_txt_file(in_file)
        if txt_file in txt_files:
            matched_files.append((in_file, txt_file))
            txt_files.remove(txt_file)
        else:
            matched_files.append((in_file, None))
    for txt_file in txt_files:
        matched_files.append((None, txt_file))
    return matched_files
