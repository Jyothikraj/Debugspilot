
from app.retrieval.retriever import retrieve
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.chroma_store import get_repository_chunks


# --------------------------------------------------
# Reciprocal Rank Fusion
# --------------------------------------------------

def hybrid_search(
    query,
    repository_id,
    k=3,
    rrf_k=60,
):
    """
    Combine Vector Search and BM25 Search
    using Reciprocal Rank Fusion (RRF).

    Parameters:
        query         : User's search query
        repository_id : Repository to search
        k             : Number of final results
        rrf_k         : RRF constant
    """

    # --------------------------------------------------
    # Vector Search
    # --------------------------------------------------

    vector_results = retrieve(
        query,
        repository_id=repository_id,
        k=k,
    )


    # --------------------------------------------------
    # Get Repository Chunks for BM25
    # --------------------------------------------------

    chunks = get_repository_chunks(
        repository_id
    )


    # --------------------------------------------------
    # BM25 Search
    # --------------------------------------------------

    bm25 = BM25Retriever(
        chunks
    )

    keyword_results = bm25.search(
        query,
        k=k,
    )


    # --------------------------------------------------
    # RRF Scores
    # --------------------------------------------------

    scores = {}
    documents = {}


    # --------------------------------------------------
    # Vector Ranking
    # --------------------------------------------------

    for rank, result in enumerate(
        vector_results,
        start=1,
    ):

        key = (
            result["metadata"].get(
                "file",
                "",
            )
            + ":"
            + str(
                result["metadata"].get(
                    "start_line"
                )
            )
        )

        scores[key] = (
            scores.get(key, 0)
            + 1 / (rrf_k + rank)
        )

        documents[key] = result


    # --------------------------------------------------
    # BM25 Ranking
    # --------------------------------------------------

    for rank, result in enumerate(
        keyword_results,
        start=1,
    ):

        key = (
            result["metadata"].get(
                "file",
                "",
            )
            + ":"
            + str(
                result["metadata"].get(
                    "start_line"
                )
            )
        )

        scores[key] = (
            scores.get(key, 0)
            + 1 / (rrf_k + rank)
        )

        documents[key] = result


    # --------------------------------------------------
    # Sort by RRF Score
    # --------------------------------------------------

    ranked_keys = sorted(
        scores,
        key=scores.get,
        reverse=True,
    )


    # --------------------------------------------------
    # Final Results
    # --------------------------------------------------

    results = []

    for key in ranked_keys[:k]:

        result = documents[key].copy()

        result["hybrid_score"] = scores[key]

        results.append(
            result
        )


    return results


if __name__ == "__main__":

    results = hybrid_search(
        "get_popular_recipes",
        repository_id=4,
        k=10,
    )

    for result in results:

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
            "Repository:",
            result["metadata"].get("repository_id"),
        )

        print(
            "Hybrid Score:",
            result["hybrid_score"],
        )

        print("Code:")

        print(
            result["content"]
        )
