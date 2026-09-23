from pathlib import Path

from . import SET_SUFFIXES

def is_set_file(file: Path | str) -> bool:
    file = Path(file)
    if not file.exists():
        return False
    if not file.is_file():
        return False
    return file.suffix.lower() in SET_SUFFIXES
