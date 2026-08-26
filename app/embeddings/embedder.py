import ollama 
from app.ingestion.file_scanner import scan_project
from app.ingestion.chunker import chunk_project

def create_embedding(text):
    response = ollama.embed(
        model = "nomic-embed-text",
        input = text,
    )

    return response["embeddings"][0]

project_path = "test_project"

files = scan_project(project_path)
chunks = chunk_project(files)

embedded_chunks = []

for chunk in chunks:
    embedding = create_embedding(chunk["content"])

    embedded_chunks.append({
        "content": chunk["content"],
        "embedding": embedding,
        "metadata": chunk["metadata"],
    })
    
for i, chunk in enumerate(embedded_chunks):
    print(
        f"Chunk {i + 1}: "
        f"vector dimensions = {len(chunk['embedding'])}"
    )

print("Total chunks:", len(embedded_chunks))
print("Vector length:", len(embedded_chunks[0]["embedding"]))
print("First chunk:")
print(embedded_chunks[0])



