from pathlib import Path


LANGUAGE_MAP = {
    # Python
    ".py": "python",

    # JavaScript / TypeScript
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",

    # Java
    ".java": "java",

    # C / C++
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "c",
    ".hpp": "cpp",

    # SQL
    ".sql": "sql",

    # Configuration
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",

    # Documentation
    ".md": "markdown",
    ".txt": "text",

    # Logs
    ".log": "log",
}


def parse_file(file_path):
    """
    Read a file and return its content
    along with basic metadata.
    """

    file_path = Path(file_path)

    content = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    metadata = {
        "file": str(file_path),
        "extension": file_path.suffix.lower(),
        "language": LANGUAGE_MAP.get(
            file_path.suffix.lower(),
            "unknown"
        ),
    }

    return {
        "content": content,
        "metadata": metadata,
    }