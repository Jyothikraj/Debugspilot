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

    print(
        "DEBUG 1: main started",
        flush=True,
    )

    # ============================================================
    # GET REPOSITORY URL
    # ============================================================

    repo_url = input(
        "\nEnter GitHub repository URL: "
    ).strip()

    if not repo_url:

        print(
            "\nNo repository URL provided.",
            flush=True,
        )

        return

    print(
        "DEBUG 2: URL received",
        flush=True,
    )

    repository_path = None

    try:

        # ========================================================
        # CLONE REPOSITORY
        # ========================================================

        print(
            "\nDEBUG 2A: cloning repository...",
            flush=True,
        )

        clone_start = time.time()

        repository_path = clone_repository(
            repo_url
        )

        clone_time = time.time() - clone_start

        print(
            "DEBUG 3: repository cloned",
            flush=True,
        )

        print(
            f"Repository path: {repository_path}",
            flush=True,
        )

        print(
            f"[TIME] Repository cloning: {clone_time:.2f}s",
            flush=True,
        )

        # ========================================================
        # SCAN PROJECT
        # ========================================================

        print(
            "\nDEBUG 4: starting project scan...",
            flush=True,
        )

        scan_start = time.time()

        files = scan_project(
            repository_path
        )

        scan_time = time.time() - scan_start

        print(
            "DEBUG 4: scanning completed",
            flush=True,
        )

        print(
            f"Files found: {len(files)}",
            flush=True,
        )

        print(
            f"[TIME] File scanning: {scan_time:.2f}s",
            flush=True,
        )

        # ========================================================
        # CHUNK PROJECT
        # ========================================================

        print(
            "\nDEBUG 5: starting project chunking...",
            flush=True,
        )

        chunk_start = time.time()

        chunks = chunk_project(
            files
        )

        chunk_time = time.time() - chunk_start

        print(
            "\nDEBUG 5: chunking completed",
            flush=True,
        )

        print(
            f"Chunks created: {len(chunks)}",
            flush=True,
        )

        print(
            f"[TIME] Chunking: {chunk_time:.2f}s",
            flush=True,
        )

        # ========================================================
        # STORE IN CHROMADB
        # ========================================================

        print(
            "\nDEBUG 6: about to store chunks",
            flush=True,
        )

        print(
            "DEBUG 6A: store_chunks function =",
            store_chunks,
            flush=True,
        )

        print(
            "DEBUG 6B: store_chunks module =",
            store_chunks.__module__,
            flush=True,
        )

        print(
            "\nDEBUG 6C: starting ChromaDB storage...",
            flush=True,
        )

        store_start = time.time()

        stored_count = store_chunks(
            chunks
        )

        store_time = time.time() - store_start

        print(
            "\nDEBUG 7: chunks stored successfully",
            flush=True,
        )

        print(
            f"Chunks stored in ChromaDB: {stored_count}",
            flush=True,
        )

        print(
            f"[TIME] ChromaDB storage: {store_time:.2f}s",
            flush=True,
        )

        # ========================================================
        # INGESTION SUMMARY
        # ========================================================

        print(
            "\n========================================",
            flush=True,
        )

        print(
            "Repository ingestion completed.",
            flush=True,
        )

        print(
            "========================================",
            flush=True,
        )

        print(
            f"Files:   {len(files)}",
            flush=True,
        )

        print(
            f"Chunks:  {len(chunks)}",
            flush=True,
        )

        print(
            f"Stored:  {stored_count}",
            flush=True,
        )

        total_ingestion_time = (
            clone_time
            + scan_time
            + chunk_time
            + store_time
        )

        print(
            f"Total ingestion time: "
            f"{total_ingestion_time:.2f}s",
            flush=True,
        )

        print(
            "\nReady for retrieval.",
            flush=True,
        )

        # ========================================================
        # QUERY
        # ========================================================

        query = input(
            "\nEnter your question: "
        ).strip()

        if not query:

            print(
                "\nNo query provided.",
                flush=True,
            )

            return

        print(
            "\nDEBUG 8: query received",
            flush=True,
        )

        print(
            f"Question: {query}",
            flush=True,
        )

        # ========================================================
        # IMPORT GENERATOR
        # ========================================================
        #
        # Imported after ingestion so generator.py does not
        # execute retrieval/generation code during startup.
        #

        print(
            "\nDEBUG 9: importing generator...",
            flush=True,
        )

        from app.llm.generator import (
            generate_answer,
        )

        print(
            "DEBUG 9A: generator imported",
            flush=True,
        )

        # ========================================================
        # GENERATE ANSWER
        # ========================================================

        print(
            "\nDEBUG 9B: starting retrieval + generation...",
            flush=True,
        )

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
            "\nDEBUG 9C: retrieval + generation completed",
            flush=True,
        )

        print(
            f"[TIME] Total retrieval + generation: "
            f"{generation_time:.2f}s",
            flush=True,
        )

        # ========================================================
        # DISPLAY ANSWER
        # ========================================================

        print(
            "\n========================================",
            flush=True,
        )

        print(
            "DEBUGPILOT ANSWER",
            flush=True,
        )

        print(
            "========================================",
            flush=True,
        )

        print(
            answer,
            flush=True,
        )

    finally:

        # ========================================================
        # CLEANUP
        # ========================================================

        if repository_path:

            print(
                "\nDEBUG 10: cleaning temporary repository",
                flush=True,
            )

            try:

                delete_repository(
                    repository_path
                )

                print(
                    "Temporary repository deleted.",
                    flush=True,
                )

            except Exception as cleanup_error:

                print(
                    "WARNING: Failed to delete "
                    "temporary repository.",
                    flush=True,
                )

                print(
                    "Cleanup error:",
                    cleanup_error,
                    flush=True,
                )


# ================================================================
# ENTRY POINT
# ================================================================

if __name__ == "__main__":

    try:

        main()

    except (ValueError, RuntimeError) as error:

        print(
            f"\nError: {error}",
            flush=True,
        )

    except Exception as error:

        print(
            f"\nUnexpected error: {error}",
            flush=True,
        )

        raise