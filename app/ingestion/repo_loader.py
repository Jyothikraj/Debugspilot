import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from git import Repo
from git.exc import GitCommandError

from app.ingestion.file_scanner import scan_project
from app.ingestion.chunker import chunk_project
from app.retrieval.chroma_store import store_chunks


# ======================================================
# GitHub URL Validation
# ======================================================

def validate_github_url(repo_url):
    parsed_url = urlparse(repo_url)

    if parsed_url.scheme not in {"http", "https"}:
        raise ValueError(
            "Repository URL must use http or https."
        )

    if parsed_url.netloc.lower() != "github.com":
        raise ValueError(
            "Only GitHub repositories are supported."
        )

    if not parsed_url.path.strip("/"):
        raise ValueError(
            "Invalid GitHub repository URL."
        )


# ======================================================
# Clone Repository
# ======================================================

def clone_repository(repo_url):

    validate_github_url(repo_url)

    temp_directory = Path(
        tempfile.mkdtemp(
            prefix="debugpilot_"
        )
    )

    repository_path = (
        temp_directory / "repository"
    )

    try:

        Repo.clone_from(
            repo_url,
            repository_path,
        )

        return repository_path

    except GitCommandError as error:

        shutil.rmtree(
            temp_directory,
            ignore_errors=True,
        )

        raise RuntimeError(
            f"Failed to clone repository: {error}"
        )


# ======================================================
# Delete Temporary Repository
# ======================================================

def delete_repository(repository_path):

    repository_path = Path(
        repository_path
    )

    if repository_path.exists():

        shutil.rmtree(
            repository_path.parent,
            ignore_errors=True,
        )


# ======================================================
# Load Repository
# ======================================================

def load_repository(repo_url):

    repository_path = clone_repository(
        repo_url
    )

    try:

        # --------------------------------------------------
        # Scan repository
        # --------------------------------------------------

        files = scan_project(
            repository_path
        )

        print(
            f"Files found: {len(files)}"
        )

        # --------------------------------------------------
        # Create chunks
        # --------------------------------------------------

        chunks = chunk_project(
            files
        )

        print(
            f"Chunks created: {len(chunks)}"
        )

        # --------------------------------------------------
        # Store chunks in ChromaDB
        # --------------------------------------------------

        stored_count = store_chunks(
            chunks
        )

        print(
            f"Chunks stored in ChromaDB: {stored_count}"
        )

        return {
            "repository_path": repository_path,
            "files": files,
            "chunks": chunks,
            "stored_count": stored_count,
        }

    except Exception:

        # Delete repository only when
        # something goes wrong.

        delete_repository(
            repository_path
        )

        raise


# ======================================================
# Main
# ======================================================

if __name__ == "__main__":

    repo_url = input(
        "Enter GitHub repository URL: "
    ).strip()

    try:

        result = load_repository(
            repo_url
        )

        print(
            "\nRepository processed successfully."
        )

        # --------------------------------------------------
        # Repository Path
        # --------------------------------------------------

        print(
            "\nRepository path:"
        )

        print(
            result["repository_path"]
        )

        # --------------------------------------------------
        # Files
        # --------------------------------------------------

        print(
            "\nFiles:"
        )

        for file_path in result["files"]:

            print(
                file_path
            )

        # --------------------------------------------------
        # First Chunks
        # --------------------------------------------------

        print(
            "\nFirst chunks:"
        )

        for index, chunk in enumerate(
            result["chunks"][:10],
            start=1,
        ):

            metadata = chunk["metadata"]

            print(
                f"\n--- CHUNK {index} ---"
            )

            print(
                "File:",
                metadata.get("file")
            )

            print(
                "Language:",
                metadata.get("language")
            )

            print(
                "Type:",
                metadata.get("type")
            )

            print(
                "Class:",
                metadata.get("class")
            )

            print(
                "Function:",
                metadata.get("function")
            )

            print(
                "Lines:",
                metadata.get("start_line"),
                "-",
                metadata.get("end_line"),
            )

            print(
                "Code:"
            )

            print(
                chunk["content"]
            )

    except (ValueError, RuntimeError) as error:

        print(
            f"\nError: {error}"
        )

    except Exception as error:

        print(
            f"\nUnexpected error: {error}"
        )

        