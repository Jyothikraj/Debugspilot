import chromadb
import ollama


# --------------------------------------------------
# ChromaDB Client
# --------------------------------------------------

client = chromadb.PersistentClient(
    path="./chroma_db"
)


# --------------------------------------------------
# ChromaDB Collection
# --------------------------------------------------

collection = client.get_collection(
    name="debugpilot"
)


# --------------------------------------------------
# Vector Retrieval
# --------------------------------------------------

def retrieve(query, k=3):
    """
    Retrieve the most semantically relevant
    chunks from ChromaDB.
    """

    # --------------------------------------------------
    # Create query embedding
    # --------------------------------------------------

    response = ollama.embed(
        model="nomic-embed-text",
        input=query,
    )

    query_embedding = response[
        "embeddings"
    ][0]

    # --------------------------------------------------
    # Search ChromaDB
    # --------------------------------------------------

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=k,
    )

    # --------------------------------------------------
    # Format Results
    # --------------------------------------------------

    retrieved_chunks = []

    for i in range(
        len(results["ids"][0])
    ):

        retrieved_chunks.append({

            "id": results["ids"][0][i],

            "content": results[
                "documents"
            ][0][i],

            "metadata": results[
                "metadatas"
            ][0][i],

            "distance": results[
                "distances"
            ][0][i],
        })

    return retrieved_chunks


# ==================================================
# Testing
# ==================================================

if __name__ == "__main__":

    query = (
        "Which method cancels an order?"
    )

    results = retrieve(
        query,
        k=3,
    )

    for result in results:

        print(
            "\n--- VECTOR RESULT ---"
        )

        print(
            "File:",
            result["metadata"].get(
                "file"
            )
        )

        print(
            "Function:",
            result["metadata"].get(
                "function"
            )
        )

        print(
            "Distance:",
            result["distance"]
        )

        print(
            "Code:"
        )

        print(
            result["content"]
        )