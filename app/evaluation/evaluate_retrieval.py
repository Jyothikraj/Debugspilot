from app.retrieval.hybrid_retriever import hybrid_search
from app.evaluation.dataset import evaluation_queries
from app.evaluation.metrics import recall_at_k, precision_at_k


K = 3

total_recall = 0
total_precision = 0


for item in evaluation_queries:

    query = item["query"]
    relevant = item["relevant_functions"]

    results = hybrid_search(query, k=K)

    retrieved_functions = [
        result["metadata"].get("function")
        for result in results
    ]

    recall = recall_at_k(
        retrieved_functions,
        relevant,
        K
    )

    precision = precision_at_k(
        retrieved_functions,
        relevant,
        K
    )

    total_recall += recall
    total_precision += precision

    print("\n--- EVALUATION ---")
    print("Query:", query)
    print("Expected:", relevant)
    print("Retrieved:", retrieved_functions)
    print("Recall@3:", recall)
    print("Precision@3:", precision)


count = len(evaluation_queries)

print("\n=== OVERALL ===")
print("Average Recall@3:", total_recall / count)
print("Average Precision@3:", total_precision / count)