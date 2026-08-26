import re

from rank_bm25 import BM25Okapi


# --------------------------------------------------
# Tokenize Code
# --------------------------------------------------

def tokenize_code(text):
    """
    Convert source code or a query into
    searchable tokens.
    """

    text = text.lower()

    tokens = re.findall(
        r"[a-zA-Z_][a-zA-Z0-9_]*",
        text
    )

    expanded_tokens = []

    for token in tokens:

        expanded_tokens.append(
            token
        )

        # Expand snake_case identifiers
        if "_" in token:

            expanded_tokens.extend(
                token.split("_")
            )

    return expanded_tokens


# --------------------------------------------------
# BM25 Retriever
# --------------------------------------------------

class BM25Retriever:

    def __init__(self, chunks):
        """
        Build a BM25 index from the chunks
        produced by the ingestion pipeline.
        """

        self.chunks = chunks

        documents = [
            chunk["content"]
            for chunk in chunks
        ]

        tokenized_documents = [
            tokenize_code(document)
            for document in documents
        ]

        self.bm25 = BM25Okapi(
            tokenized_documents
        )


    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    def search(self, query, k=3):
        """
        Search code chunks using BM25.
        """

        tokenized_query = tokenize_code(
            query
        )

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_indexes = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True,
        )

        results = []

        for index in ranked_indexes[:k]:

            results.append({
                "content": self.chunks[index]["content"],
                "metadata": self.chunks[index]["metadata"],
                "score": float(scores[index]),
            })

        return results