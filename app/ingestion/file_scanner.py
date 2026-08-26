from pathlib import Path


# ============================================================
# Directories that should NEVER be ingested
# ============================================================

IGNORED_DIRECTORIES = {
    ".git",
    ".github",

    # Python
    ".venv",
    "venv",
    "__pycache__",

    # JavaScript / Node
    "node_modules",

    # Generated / build files
    "staticfiles",
    "static",
    "dist",
    "build",
    "coverage",

    # IDE
    ".idea",
    ".vscode",
}


# ============================================================
# Files that should NEVER be ingested
# ============================================================

IGNORED_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",

    "db.sqlite3",

    ".DS_Store",
}


# ============================================================
# File Scanner
# ============================================================

def scan_project(project_path):
    """
    Scan a project directory and return useful source files.

    Generated files, virtual environments, dependencies,
    sensitive configuration files and build artifacts are
    excluded.
    """

    project_path = Path(
        project_path
    )

    if not project_path.exists():

        raise FileNotFoundError(
            f"Project path does not exist: {project_path}"
        )

    if not project_path.is_dir():

        raise NotADirectoryError(
            f"Project path is not a directory: {project_path}"
        )

    files = []

    # ========================================================
    # Recursive scan
    # ========================================================

    for path in project_path.rglob("*"):

        # ----------------------------------------------------
        # Ignore directories
        # ----------------------------------------------------

        if path.is_dir():
            continue

        # ----------------------------------------------------
        # Ignore files inside ignored directories
        # ----------------------------------------------------

        if any(
            directory in IGNORED_DIRECTORIES
            for directory in path.parts
        ):
            continue

        # ----------------------------------------------------
        # Ignore sensitive / unwanted files
        # ----------------------------------------------------

        if path.name in IGNORED_FILES:
            continue

        # ----------------------------------------------------
        # Ignore hidden files
        # ----------------------------------------------------

        if path.name.startswith("."):
            continue

        # ----------------------------------------------------
        # Ignore common temporary files
        # ----------------------------------------------------

        if path.suffix.lower() in {
            ".pyc",
            ".pyo",
            ".tmp",
            ".temp",
            ".swp",
        }:
            continue

        files.append(
            path
        )

    # ========================================================
    # Stable ordering
    # ========================================================

    files.sort(
        key=lambda path: str(path).lower()
    )

    return files