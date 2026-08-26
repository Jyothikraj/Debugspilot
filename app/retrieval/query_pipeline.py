from app.retrieval.retriever import retrieve
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.reranker import rerank


# ============================================================
# BUILD UNIQUE DOCUMENT KEY
# ============================================================

def get_document_key(result):
    """
    Create a stable identifier for a retrieved chunk.

    File + start_line + end_line is used so that the same
    chunk retrieved by vector search and BM25 is merged
    during RRF.
    """

    metadata = result.get("metadata", {})

    file_path = str(
        metadata.get("file", "")
    )

    start_line = str(
        metadata.get("start_line", "")
    )

    end_line = str(
        metadata.get("end_line", "")
    )

    return (
        f"{file_path}:"
        f"{start_line}:"
        f"{end_line}"
    )


# ============================================================
# BUILD CONTEXT
# ============================================================

def build_context(results):
    """
    Convert the final reranked chunks into a context string
    for the LLM.

    Only the final retrieved chunks are included.
    """

    context_parts = []

    for index, result in enumerate(
        results,
        start=1,
    ):

        metadata = result.get(
            "metadata",
            {}
        )

        file_path = metadata.get(
            "file",
            "unknown",
        )

        start_line = metadata.get(
            "start_line",
            "?",
        )

        end_line = metadata.get(
            "end_line",
            "?",
        )

        language = metadata.get(
            "language",
            "",
        )

        chunk_type = metadata.get(
            "type",
            "",
        )

        class_name = metadata.get(
            "class",
            "",
        )

        function_name = metadata.get(
            "function",
            "",
        )

        context_parts.append(
            f"""
--- SOURCE {index} ---

File: {file_path}
Language: {language}
Type: {chunk_type}
Class: {class_name}
Function: {function_name}
Lines: {start_line} - {end_line}

Code:
{result.get("content", "")}
"""
        )

    return "\n".join(
        context_parts
    )


# ============================================================
# VECTOR + BM25 + RRF + RERANKING
# ============================================================

def query_pipeline(
    query,
    chunks,
    retrieval_k=30,
    final_k=10,
):
    """
    Complete DebugPilot retrieval pipeline.

    Query
        ↓
    Chroma Vector Search
        ↓
    BM25 Keyword Search
        ↓
    Reciprocal Rank Fusion
        ↓
    CrossEncoder Reranking
        ↓
    Final Top-K
        ↓
    Context Builder
        ↓
    LLM
    """

    if not query or not query.strip():

        raise ValueError(
            "Query cannot be empty."
        )

    if not chunks:

        raise ValueError(
            "No project chunks are available for retrieval."
        )

    query = query.strip()

    print(
        "\n========================================",
        flush=True,
    )

    print(
        "DEBUG RETRIEVAL PIPELINE",
        flush=True,
    )

    print(
        "========================================",
        flush=True,
    )

    print(
        f"Query: {query}",
        flush=True,
    )

    print(
        f"Total project chunks: {len(chunks)}",
        flush=True,
    )

    print(
        f"Initial retrieval K: {retrieval_k}",
        flush=True,
    )

    print(
        f"Final context K: {final_k}",
        flush=True,
    )

    # ========================================================
    # STEP 1: VECTOR SEARCH
    # ========================================================

    print(
        "\n[TIME] Starting vector retrieval...",
        flush=True,
    )

    vector_results = retrieve(
        query,
        k=retrieval_k,
    )

    print(
        f"[RETRIEVAL] Vector results: "
        f"{len(vector_results)}",
        flush=True,
    )

    # ========================================================
    # STEP 2: BM25
    # ========================================================

    print(
        "\n[TIME] Starting BM25 retrieval...",
        flush=True,
    )

    bm25 = BM25Retriever(
        chunks
    )

    keyword_results = bm25.search(
        query,
        k=retrieval_k,
    )

    print(
        f"[RETRIEVAL] BM25 results: "
        f"{len(keyword_results)}",
        flush=True,
    )

    # ========================================================
    # STEP 3: RECIPROCAL RANK FUSION
    # ========================================================

    print(
        "\n[RETRIEVAL] Performing RRF hybrid fusion...",
        flush=True,
    )

    scores = {}

    documents = {}

    # --------------------------------------------------------
    # Vector results
    # --------------------------------------------------------

    for rank, result in enumerate(
        vector_results,
        start=1,
    ):

        key = get_document_key(
            result
        )

        rrf_score = (
            1 / (60 + rank)
        )

        scores[key] = (
            scores.get(key, 0)
            + rrf_score
        )

        documents[key] = result

    # --------------------------------------------------------
    # BM25 results
    # --------------------------------------------------------

    for rank, result in enumerate(
        keyword_results,
        start=1,
    ):

        key = get_document_key(
            result
        )

        rrf_score = (
            1 / (60 + rank)
        )

        scores[key] = (
            scores.get(key, 0)
            + rrf_score
        )

        documents[key] = result

    # --------------------------------------------------------
    # Sort by RRF score
    # --------------------------------------------------------

    ranked_keys = sorted(
        scores,
        key=scores.get,
        reverse=True,
    )

    hybrid_results = []

    for key in ranked_keys[
        :retrieval_k
    ]:

        result = documents[
            key
        ].copy()

        result["hybrid_score"] = (
            scores[key]
        )

        hybrid_results.append(
            result
        )

    print(
        f"[RETRIEVAL] Hybrid results: "
        f"{len(hybrid_results)}",
        flush=True,
    )

    # ========================================================
    # STEP 4: CROSS-ENCODER RERANKING
    # ========================================================

    print(
        "\n[TIME] Starting reranking...",
        flush=True,
    )

    reranked_results = rerank(
        query,
        hybrid_results,
        k=final_k,
    )

    print(
        f"[RETRIEVAL] Final reranked chunks: "
        f"{len(reranked_results)}",
        flush=True,
    )

    # ========================================================
    # STEP 5: SHOW FINAL SOURCES
    # ========================================================

    print(
        "\n========================================",
        flush=True,
    )

    print(
        "FINAL RETRIEVED SOURCES",
        flush=True,
    )

    print(
        "========================================",
        flush=True,
    )

    for index, result in enumerate(
        reranked_results,
        start=1,
    ):

        metadata = result.get(
            "metadata",
            {}
        )

        print(
            f"\n[{index}] "
            f"{metadata.get('file', 'unknown')}",
            flush=True,
        )

        print(
            f"    Lines: "
            f"{metadata.get('start_line', '?')} - "
            f"{metadata.get('end_line', '?')}",
            flush=True,
        )

        print(
            f"    Class: "
            f"{metadata.get('class', '')}",
            flush=True,
        )

        print(
            f"    Function: "
            f"{metadata.get('function', '')}",
            flush=True,
        )

        print(
            f"    Hybrid score: "
            f"{result.get('hybrid_score', '')}",
            flush=True,
        )

        print(
            f"    Rerank score: "
            f"{result.get('rerank_score', '')}",
            flush=True,
        )

    # ========================================================
    # STEP 6: BUILD CONTEXT
    # ========================================================

    print(
        "\n[TIME] Building final LLM context...",
        flush=True,
    )

    context = build_context(
        reranked_results
    )

    print(
        f"[RETRIEVAL] Context characters: "
        f"{len(context)}",
        flush=True,
    )

    print(
        f"[RETRIEVAL] Context chunks: "
        f"{len(reranked_results)}",
        flush=True,
    )

    # ========================================================
    # RETURN
    # ========================================================

    return {
        "query": query,

        "results": reranked_results,

        "context": context,

        "retrieval_k": retrieval_k,

        "final_k": final_k,

        "total_chunks": len(chunks),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    from app.ingestion.file_scanner import (
        scan_project
    )

    from app.ingestion.chunker import (
        chunk_project
    )

    # --------------------------------------------------------
    # Load test project
    # --------------------------------------------------------

    project_path = "test_project"

    print(
        "\nScanning project...",
        flush=True,
    )

    files = scan_project(
        project_path
    )

    print(
        f"Files found: {len(files)}",
        flush=True,
    )

    # --------------------------------------------------------
    # Chunk project
    # --------------------------------------------------------

    print(
        "\nChunking project...",
        flush=True,
    )

    chunks = chunk_project(
        files
    )

    print(
        f"Chunks created: {len(chunks)}",
        flush=True,
    )

    # --------------------------------------------------------
    # Query
    # --------------------------------------------------------

    query = input(
        "\nEnter your question: "
    ).strip()

    if not query:

        print(
            "No query provided."
        )

        raise SystemExit

    # --------------------------------------------------------
    # Run retrieval
    # --------------------------------------------------------

    result = query_pipeline(
        query,
        chunks,
        retrieval_k=30,
        final_k=10,
    )

    # ========================================================
    # DISPLAY CONTEXT
    # ========================================================

    print(
        "\n========================================"
    )

    print(
        "FINAL LLM CONTEXT"
    )

    print(
        "========================================"
    )

    print(
        result["context"]
    )

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    print(
        "\n========================================"
    )

    print(
        "FINAL RERANKED RESULTS"
    )

    print(
        "========================================"
    )

    for index, item in enumerate(
        result["results"],
        start=1,
    ):

        metadata = item.get(
            "metadata",
            {}
        )

        print(
            f"\n--- RESULT {index} ---"
        )

        print(
            "File:",
            metadata.get(
                "file"
            )
        )

        print(
            "Language:",
            metadata.get(
                "language"
            )
        )

        print(
            "Type:",
            metadata.get(
                "type"
            )
        )

        print(
            "Class:",
            metadata.get(
                "class"
            )
        )

        print(
            "Function:",
            metadata.get(
                "function"
            )
        )

        print(
            "Lines:",
            metadata.get(
                "start_line"
            ),
            "-",
            metadata.get(
                "end_line"
            ),
        )

        print(
            "Hybrid score:",
            item.get(
                "hybrid_score"
            )
        )

        print(
            "Rerank score:",
            item.get(
                "rerank_score"
            )
        )