from sentence_transformers import CrossEncoder

from app.retrieval.hybrid_retriever import hybrid_search


# --------------------------------------------------
# Cross-Encoder Model
# --------------------------------------------------

model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


# --------------------------------------------------
# Rerank Results
# --------------------------------------------------

def rerank(
    query,
    results,
    k=3,
):
    """
    Rerank retrieved code chunks using
    a Cross-Encoder model.
    """

    if not results:
        return []

    # --------------------------------------------------
    # Create query-document pairs
    # --------------------------------------------------

    pairs = [
        (
            query,
            result["content"]
        )
        for result in results
    ]

    # --------------------------------------------------
    # Predict relevance scores
    # --------------------------------------------------

    scores = model.predict(
        pairs
    )

    # --------------------------------------------------
    # Attach scores
    # --------------------------------------------------

    reranked = []

    for result, score in zip(
        results,
        scores,
    ):

        result = result.copy()

        result["rerank_score"] = float(
            score
        )

        reranked.append(
            result
        )

    # --------------------------------------------------
    # Sort by relevance
    # --------------------------------------------------

    reranked.sort(
        key=lambda x: x["rerank_score"],
        reverse=True,
    )

    return reranked[:k]


# ==================================================
# Testing
# ==================================================

if __name__ == "__main__":

    query = "cancel order"

    # --------------------------------------------------
    # Load chunks
    # --------------------------------------------------

    from app.ingestion.file_scanner import scan_project
    from app.ingestion.chunker import chunk_project

    project_path = "test_project"

    files = scan_project(
        project_path
    )

    chunks = chunk_project(
        files
    )

    # --------------------------------------------------
    # Hybrid Retrieval
    # --------------------------------------------------

    hybrid_results = hybrid_search(
        query,
        chunks,
        k=3,
    )

    # --------------------------------------------------
    # Reranking
    # --------------------------------------------------

    results = rerank(
        query,
        hybrid_results,
        k=3,
    )

    # --------------------------------------------------
    # Display Results
    # --------------------------------------------------

    for result in results:

        print(
            "\n--- RERANKED RESULT ---"
        )

        print(
            "File:",
            result["metadata"].get("file")
        )

        print(
            "Function:",
            result["metadata"].get(
                "function"
            )
        )

        print(
            "Class:",
            result["metadata"].get(
                "class"
            )
        )

        print(
            "Hybrid Score:",
            result.get(
                "hybrid_score"
            )
        )

        print(
            "Rerank Score:",
            result["rerank_score"]
        )

        print(
            "Code:"
        )

        print(
            result["content"]
        )