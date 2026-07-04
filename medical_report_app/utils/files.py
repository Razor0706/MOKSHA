from pathlib import Path


def safe_delete_file(filepath):
    try:
        Path(filepath).unlink(missing_ok=True)
    except OSError:
        return False
    return True
