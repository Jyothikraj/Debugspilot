
import time

import ollama

from app.llm.context_builder import build_context
from app.llm.prompt import build_prompt
from app.retrieval.reranker import rerank
from app.retrieval.hybrid_retriever import hybrid_search


# --------------------------------------------------
# Generate Answer
# --------------------------------------------------

def generate_answer(query, repository_id):

    start = time.perf_counter()


    # --------------------------------------------------
    # Hybrid Retrieval
    # --------------------------------------------------

    t = time.perf_counter()

    hybrid_results = hybrid_search(
        query,
        repository_id=repository_id,
        k=30,
    )

    print(
        f"[TIME] Hybrid retrieval: "
        f"{time.perf_counter() - t:.2f}s",
        flush=True,
    )


    # --------------------------------------------------
    # Reranking
    # --------------------------------------------------

    t = time.perf_counter()

    reranked_results = rerank(
        query,
        hybrid_results,
        k=10,
    )

    print(
        f"[TIME] Reranking: "
        f"{time.perf_counter() - t:.2f}s",
        flush=True,
    )


    # --------------------------------------------------
    # Context
    # --------------------------------------------------

    t = time.perf_counter()

    context = build_context(
        reranked_results
    )

    print("\n========== FINAL CONTEXT ==========", flush=True)
    print(context, flush=True)
    print("========== END CONTEXT ==========\n", flush=True)

    print(
        f"[TIME] Context building: "
        f"{time.perf_counter() - t:.2f}s",
        flush=True,
    )


    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------

    t = time.perf_counter()

    prompt = build_prompt(
        query,
        context,
    )

    print(
        f"[TIME] Prompt building: "
        f"{time.perf_counter() - t:.2f}s",
        flush=True,
    )


    # --------------------------------------------------
    # LLM Generation
    # --------------------------------------------------

    print(
        "[TIME] Starting Qwen generation...",
        flush=True,
    )

    t = time.perf_counter()

    response = ollama.chat(
        model="qwen2.5-coder:7b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    print(
        f"[TIME] Qwen generation: "
        f"{time.perf_counter() - t:.2f}s",
        flush=True,
    )


    # --------------------------------------------------
    # Total Time
    # --------------------------------------------------

    print(
        f"[TIME] TOTAL: "
        f"{time.perf_counter() - start:.2f}s",
        flush=True,
    )


    return response[
        "message"
    ][
        "content"
    ]


# ==================================================
# Module Information
# ==================================================

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
