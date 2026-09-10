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
    k=10,
):
    """
    Rerank already-retrieved hybrid search results
    using a Cross-Encoder model.
    """

    if not results:
        return []

    # --------------------------------------------------
    # Create query-document pairs
    # --------------------------------------------------

    pairs = [
        (
            query,
            f"""
    File: {result['metadata'].get('file', '')}
    Class: {result['metadata'].get('class', '')}
    Function: {result['metadata'].get('function', '')}

    Code:
    {result['content']}
    """,
        )
        for result in results
    ]

    # --------------------------------------------------
    # Predict relevance scores
    # --------------------------------------------------

    scores = model.predict(pairs)

    # --------------------------------------------------
    # Attach scores
    # --------------------------------------------------

    reranked = []

    for result, score in zip(results, scores):

        result = result.copy()

        result["rerank_score"] = float(score)

        reranked.append(result)

    # --------------------------------------------------
    # Sort by Cross-Encoder score
    # --------------------------------------------------

    reranked.sort(
    key=lambda x: x["rerank_score"],
    reverse=True,
    )

    print("\n" + "=" * 70)
    print("RERANKING ORDER")
    print("=" * 70)

    for rank, result in enumerate(reranked, start=1):
        metadata = result["metadata"]

        print(
            f"Rank {rank} | "
            f"Score: {result['rerank_score']:.4f} | "
            f"File: {metadata.get('file')} | "
            f"Class: {metadata.get('class')} | "
            f"Function: {metadata.get('function')}"
        )

    return reranked[:k]


# ==================================================
# Testing
# ==================================================

if __name__ == "__main__":

    query = "How does the core recipe recommendation logic work?"
    repository_id = 4

    # --------------------------------------------------
    # Hybrid Retrieval
    # --------------------------------------------------

    hybrid_results = hybrid_search(
        query,
        repository_id=repository_id,
        k=30,
    )

    print("\n" + "=" * 60)
    print("HYBRID RESULTS")
    print("=" * 60)

    for result in hybrid_results:

        print("\n--- HYBRID RESULT ---")

        print(
            "File:",
            result["metadata"].get("file"),
        )

        print(
            "Function:",
            result["metadata"].get("function"),
        )

        print(
            "Class:",
            result["metadata"].get("class"),
        )

        print(
            "Hybrid Score:",
            result.get("hybrid_score"),
        )

        print("Code:")
        print(result["content"])

    # --------------------------------------------------
    # Reranking
    # --------------------------------------------------

    reranked_results = rerank(
        query,
        hybrid_results,
        k=30,
    )

    print("\n" + "=" * 60)
    print("RERANKED RESULTS")
    print("=" * 60)

    for result in reranked_results:

        print("\n--- RERANKED RESULT ---")

        print(
            "File:",
            result["metadata"].get("file"),
        )

        print(
            "Function:",
            result["metadata"].get("function"),
        )

        print(
            "Class:",
            result["metadata"].get("class"),
        )

        print(
            "Hybrid Score:",
            result.get("hybrid_score"),
        )

        print(
            "Rerank Score:",
            result.get("rerank_score"),
        )

        print("Code:")
        print(result["content"])