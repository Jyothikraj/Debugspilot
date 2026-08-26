def recall_at_k(retrieved_functions, relevant_functions, k):
    retrieved = set(retrieved_functions[:k])
    relevant = set(relevant_functions)

    if not relevant:
        return 0.0

    return len(retrieved & relevant) / len(relevant)


def precision_at_k(retrieved_functions, relevant_functions, k):
    retrieved = retrieved_functions[:k]
    relevant = set(relevant_functions)

    if not retrieved:
        return 0.0

    return sum(
        function in relevant
        for function in retrieved
    ) / len(retrieved)