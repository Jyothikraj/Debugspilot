import chromadb
import ollama


# ======================================================
# ChromaDB
# ======================================================

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="debugpilot"
)


# ======================================================
# Metadata Sanitizer
# ======================================================

def sanitize_metadata(metadata):

    clean_metadata = {}

    for key, value in metadata.items():

        # None is not allowed
        if value is None:
            continue

        # Lists are not allowed by Chroma
        if isinstance(value, list):

            # Skip empty lists
            if len(value) == 0:
                continue

            # Convert non-empty list to string
            value = ", ".join(
                str(item)
                for item in value
            )

        # Dictionaries are not allowed
        elif isinstance(value, dict):

            if len(value) == 0:
                continue

            value = str(value)

        clean_metadata[key] = value

    return clean_metadata


# ======================================================
# Embedding
# ======================================================

def get_embedding(text):

    response = ollama.embed(
        model="nomic-embed-text",
        input=text,
    )

    return response["embeddings"][0]


# ======================================================
# Store Chunks
# ======================================================

def store_chunks(chunks):

    print("\n[Chroma] store_chunks() called")

    ids = []
    documents = []
    metadatas = []
    embeddings = []

    for index, chunk in enumerate(chunks):

        content = chunk.get(
            "content",
            ""
        ).strip()

        if not content:
            continue

        original_metadata = chunk.get(
            "metadata",
            {}
        )

        print(
            f"\n[Chroma] Processing chunk {index + 1}"
        )

        print(
            "[Chroma] Original metadata:"
        )

        print(
            original_metadata
        )

        # IMPORTANT:
        # Sanitize BEFORE collection.add()

        metadata = sanitize_metadata(
            original_metadata
        )

        print(
            "[Chroma] Sanitized metadata:"
        )

        print(
            metadata
        )

        # --------------------------------------------------
        # Unique ID
        # --------------------------------------------------

        file_path = metadata.get(
            "file",
            "unknown"
        )

        start_line = metadata.get(
            "start_line",
            index
        )

        chunk_id = (
            f"{file_path}:"
            f"{start_line}:"
            f"{index}"
        )

        ids.append(
            chunk_id
        )

        documents.append(
            content
        )

        metadatas.append(
            metadata
        )

        embeddings.append(
            get_embedding(content)
        )

    if not ids:
        return 0

    print(
        "\n[Chroma] Adding chunks..."
    )

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(
        "[Chroma] Successfully stored chunks."
    )

    return len(ids)