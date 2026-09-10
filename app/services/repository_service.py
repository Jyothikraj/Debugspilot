import shutil
import tempfile
from pathlib import Path

from git import Repo


def clone_repository(repo_url: str) -> str:
    temp_dir = tempfile.mkdtemp(prefix="debugpilot_")

    Repo.clone_from(
        repo_url,
        temp_dir,
    )

    return temp_dir