
import time

from app.ingestion.repo_loader import (
    clone_repository,
    delete_repository,
)

from app.ingestion.file_scanner import (
    scan_project,
)

from app.ingestion.chunker import (
    chunk_project,
)

from app.retrieval.chroma_store import (
    store_chunks,
)


def main():

    repo_url = input(
        "\nEnter GitHub repository URL: "
    ).strip()

    if not repo_url:
        print("\nNo repository URL provided.")
        return

    repository_path = None

    try:

        # ========================================================
        # CLONE
        # ========================================================

        print("\nCloning repository...")

        clone_start = time.time()

        repository_path = clone_repository(
            repo_url
        )

        clone_time = time.time() - clone_start

        print(
            f"Repository cloned in {clone_time:.2f}s"
        )

        # ========================================================
        # SCAN
        # ========================================================

        print("\nScanning project...")

        scan_start = time.time()

        files = scan_project(
            repository_path
        )

        scan_time = time.time() - scan_start

        print(
            f"Files found: {len(files)} "
            f"({scan_time:.2f}s)"
        )

        # ========================================================
        # CHUNK
        # ========================================================

        print("\nChunking project...")

        chunk_start = time.time()

        chunks = chunk_project(
            files
        )

        chunk_time = time.time() - chunk_start

        print(
            f"Chunks created: {len(chunks)} "
            f"({chunk_time:.2f}s)"
        )

        # ========================================================
        # STORE
        # ========================================================

        print("\nStoring chunks in ChromaDB...")

        store_start = time.time()

        stored_count = store_chunks(
            chunks
        )

        store_time = time.time() - store_start

        print(
            f"Chunks stored: {stored_count} "
            f"({store_time:.2f}s)"
        )

        # ========================================================
        # INGESTION SUMMARY
        # ========================================================

        total_ingestion_time = (
            clone_time
            + scan_time
            + chunk_time
            + store_time
        )

        print(
            "\n========================================"
        )

        print(
            "Repository ingestion completed."
        )

        print(
            "========================================"
        )

        print(
            f"Files:   {len(files)}"
        )

        print(
            f"Chunks:  {len(chunks)}"
        )

        print(
            f"Stored:  {stored_count}"
        )

        print(
            f"Time:    {total_ingestion_time:.2f}s"
        )

        # ========================================================
        # GENERATOR
        # ========================================================

        from app.llm.generator import (
            generate_answer,
        )

        print(
            "\nReady for retrieval."
        )

        print(
            "Type 'exit' to stop."
        )

        # ========================================================
        # QUERY LOOP
        # ========================================================

        while True:

            query = input(
                "\nEnter your question: "
            ).strip()

            if query.lower() in {
                "exit",
                "quit",
            }:

                print(
                    "\nExiting DebugPilot..."
                )

                break

            if not query:

                print(
                    "Please enter a question."
                )

                continue

            generation_start = time.time()

            answer = generate_answer(
                query,
                chunks,
            )

            generation_time = (
                time.time()
                - generation_start
            )

            print(
                "\n========================================"
            )

            print(
                "DEBUGPILOT ANSWER"
            )

            print(
                "========================================"
            )

            print(
                answer
            )

            print(
                f"\nResponse time: "
                f"{generation_time:.2f}s"
            )

    finally:

        # ========================================================
        # CLEANUP
        # ========================================================

        if repository_path:

            print(
                "\nCleaning temporary repository..."
            )

            try:

                delete_repository(
                    repository_path
                )

                print(
                    "Temporary repository deleted."
                )

            except Exception as error:

                print(
                    f"Warning: cleanup failed: {error}"
                )


if __name__ == "__main__":

    try:

        main()

    except (ValueError, RuntimeError) as error:

        print(
            f"\nError: {error}"
        )

    except Exception as error:

        print(
            f"\nUnexpected error: {error}"
        )

        raise
