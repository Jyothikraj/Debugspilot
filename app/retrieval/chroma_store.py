import chromadb
import uuid
import ollama


# --------------------------------------------------
# ChromaDB Client
# --------------------------------------------------

client = chromadb.PersistentClient(
    path="./chroma_db"
)


# --------------------------------------------------
# Collection
# --------------------------------------------------

collection = client.get_or_create_collection(
    name="debugpilot"
)


# --------------------------------------------------
# Sanitize Metadata
# --------------------------------------------------

def sanitize_metadata(metadata):
    """
    Convert chunk metadata into values
    accepted by ChromaDB.
    """

    clean_metadata = {}

    for key, value in metadata.items():

        # Chroma does not accept None
        if value is None:
            continue

        # Convert lists to strings
        if isinstance(value, list):

            if not value:
                continue

            value = ", ".join(
                str(item)
                for item in value
            )

        # Convert dictionaries to strings
        elif isinstance(value, dict):

            if not value:
                continue

            value = str(value)

        clean_metadata[key] = value

    return clean_metadata


# --------------------------------------------------
# Store Chunks
# --------------------------------------------------

def store_chunks(chunks):
    """
    Generate embeddings using Ollama and store
    the chunks and embeddings in ChromaDB.
    """

    if not chunks:
        print("DEBUG: No chunks to store.")
        return 0

    documents = []
    metadatas = []
    ids = []

    for chunk in chunks:

        content = chunk["content"]

        metadata = sanitize_metadata(
            chunk["metadata"]
        )

        documents.append(
            content
        )

        metadatas.append(
            metadata
        )

        ids.append(
            str(uuid.uuid4())
        )

    print(
        f"DEBUG: Preparing {len(documents)} documents"
    )

    # --------------------------------------------------
    # Generate embeddings
    # --------------------------------------------------

    print(
        "DEBUG: Generating Ollama embeddings..."
    )

    response = ollama.embed(
        model="nomic-embed-text",
        input=documents,
    )

    print(
        "DEBUG: Ollama embeddings received"
    )

    embeddings = response["embeddings"]

    print(
        f"DEBUG: Embeddings generated: {len(embeddings)}"
    )

    print(
        f"DEBUG: Embedding dimension: {len(embeddings[0])}"
    )

    # --------------------------------------------------
    # Store in ChromaDB
    # --------------------------------------------------

    print(
        "DEBUG: Adding chunks to ChromaDB..."
    )

    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )

    print(
        "DEBUG: ChromaDB storage completed"
    )

    return len(chunks)