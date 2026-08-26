import time
import ollama

from app.llm.context_builder import build_context
from app.llm.prompt import build_prompt
from app.retrieval.reranker import rerank
from app.retrieval.hybrid_retriever import hybrid_search


def generate_answer(query, chunks):

    start = time.perf_counter()

    # --------------------------------------------------
    # Hybrid retrieval
    # --------------------------------------------------

    t = time.perf_counter()

    hybrid_results = hybrid_search(
        query,
        chunks,
        k=30
    )

    print(
        f"[TIME] Hybrid retrieval: {time.perf_counter() - t:.2f}s",
        flush=True
    )

    # --------------------------------------------------
    # Reranking
    # --------------------------------------------------

    t = time.perf_counter()

    reranked_results = rerank(
        query,
        hybrid_results,
        k=10
    )

    print(
        f"[TIME] Reranking: {time.perf_counter() - t:.2f}s",
        flush=True
    )

    # --------------------------------------------------
    # Context
    # --------------------------------------------------

    t = time.perf_counter()

    context = build_context(
        reranked_results
    )

    print(
        f"[TIME] Context building: {time.perf_counter() - t:.2f}s",
        flush=True
    )

    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------

    t = time.perf_counter()

    prompt = build_prompt(
        query,
        context
    )

    print(
        f"[TIME] Prompt building: {time.perf_counter() - t:.2f}s",
        flush=True
    )

    # --------------------------------------------------
    # LLM
    # --------------------------------------------------

    print(
        "[TIME] Starting Qwen generation...",
        flush=True
    )

    t = time.perf_counter()

    response = ollama.chat(
        model="qwen2.5:7b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    print(
        f"[TIME] Qwen generation: {time.perf_counter() - t:.2f}s",
        flush=True
    )

    print(
        f"[TIME] TOTAL: {time.perf_counter() - start:.2f}s",
        flush=True
    )

    return response["message"]["content"]


if __name__ == "__main__":

    print(
        "generator.py is a module."
    )

    print(
        "Run DebugPilot using:"
    )

    print(
        "python -m app.main"
    )
