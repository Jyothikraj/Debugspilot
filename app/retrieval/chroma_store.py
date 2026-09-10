
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
# ChromaDB Collection
# --------------------------------------------------

collection = client.get_or_create_collection(
    name="debugpilot"
)


# --------------------------------------------------
# Metadata Sanitization
# --------------------------------------------------

def sanitize_metadata(metadata):
    """
    Make metadata compatible with ChromaDB.
    """

    clean_metadata = {}

    for key, value in metadata.items():

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
# Embedding Text
# --------------------------------------------------

def get_embedding_text(chunk):
    """
    Build the text used for semantic embedding.

    The Gemini-generated summary is combined with
    the original code so that embeddings contain
    both conceptual and implementation information.
    """

    summary = chunk["metadata"].get(
        "summary",
        ""
    ).strip()

    content = chunk["content"].strip()

    if summary:
        return (
            f"Summary:\n"
            f"{summary}\n\n"
            f"Code:\n"
            f"{content}"
        )

    # Fallback for chunks without a summary
    return content


# --------------------------------------------------
# Store Chunks
# --------------------------------------------------

def store_chunks(chunks, repository_id):
    """
    Generate embeddings for code chunks
    and store them in ChromaDB.

    Each chunk is tagged with its repository_id
    so retrieval can be restricted to one repository.

    Original code is stored as the Chroma document.

    Gemini summary + original code are used
    as the embedding input.
    """

    if not chunks:

        print(
            "DEBUG: No chunks to store."
        )

        return 0

    # --------------------------------------------------
    # Prepare Storage Data
    # --------------------------------------------------

    documents = []
    metadatas = []
    ids = []
    embedding_inputs = []

    for chunk in chunks:

        content = chunk["content"]

        metadata = sanitize_metadata(
            chunk["metadata"]
        )

        # IMPORTANT:
        # Associate every chunk with its repository
        metadata["repository_id"] = repository_id

        # --------------------------------------------------
        # Store ORIGINAL CODE
        # --------------------------------------------------

        documents.append(
            content
        )

        # --------------------------------------------------
        # Store metadata
        # --------------------------------------------------

        metadatas.append(
            metadata
        )

        # --------------------------------------------------
        # Unique ID
        # --------------------------------------------------

        ids.append(
            str(uuid.uuid4())
        )

        # --------------------------------------------------
        # Prepare embedding input
        # --------------------------------------------------

        embedding_inputs.append(
            get_embedding_text(chunk)
        )

    print(
        f"DEBUG: Preparing {len(documents)} documents"
    )

    # --------------------------------------------------
    # Generate Embeddings
    # --------------------------------------------------

    print(
        "DEBUG: Generating Ollama embeddings "
        "(summary + code)..."
    )

    response = ollama.embed(
        model="nomic-embed-text",
        input=embedding_inputs,
    )

    print(
        "DEBUG: Ollama embeddings received"
    )

    embeddings = response["embeddings"]

    print(
        f"DEBUG: Embeddings generated: "
        f"{len(embeddings)}"
    )

    if embeddings:

        print(
            f"DEBUG: Embedding dimension: "
            f"{len(embeddings[0])}"
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


# --------------------------------------------------
# Get Repository Chunks
# --------------------------------------------------

def get_repository_chunks(repository_id):
    """
    Retrieve all chunks belonging to a specific
    repository from ChromaDB.

    These chunks are used to build the BM25 index.
    """

    results = collection.get(
        where={
            "repository_id": repository_id
        },
        include=[
            "documents",
            "metadatas",
        ],
    )

    chunks = []

    for i in range(
        len(results["ids"])
    ):

        chunks.append({
            "id": results["ids"][i],

            "content": results[
                "documents"
            ][i],

            "metadata": results[
                "metadatas"
            ][i],
        })

    return chunks
