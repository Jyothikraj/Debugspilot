from app.retrieval.retriever import retrieve
from app.retrieval.bm25_retriever import BM25Retriever


# --------------------------------------------------
# Reciprocal Rank Fusion
# --------------------------------------------------

def hybrid_search(
    query,
    chunks,
    k=3,
    rrf_k=60,
):
    """
    Combine vector search and BM25 search
    using Reciprocal Rank Fusion (RRF).

    Parameters:
        query   : User's search query
        chunks  : Chunks from repository ingestion
        k       : Number of final results
        rrf_k   : RRF constant
    """

    # --------------------------------------------------
    # Vector Search
    # --------------------------------------------------

    vector_results = retrieve(
        query,
        k=k,
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
    # Chroma ranking
    # --------------------------------------------------

    for rank, result in enumerate(
        vector_results,
        start=1,
    ):

        key = (
            result["metadata"].get("file", "")
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
    # BM25 ranking
    # --------------------------------------------------

    for rank, result in enumerate(
        keyword_results,
        start=1,
    ):

        key = (
            result["metadata"].get("file", "")
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
    # Sort by RRF score
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