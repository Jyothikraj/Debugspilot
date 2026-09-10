# DebugPilot

DebugPilot is an AI-powered codebase assistant that helps developers understand,
debug, and analyze backend projects.

Users can connect a GitHub repository, which DebugPilot analyzes and indexes.
They can then ask questions about the codebase and receive answers grounded in
the actual source code.

## Key Features

- GitHub repository ingestion
- Automatic source-code file scanning
- Python AST and Tree-sitter based code parsing
- Code-aware chunking using functions, classes, and modules
- Code metadata extraction
- Vector embeddings using Ollama
- ChromaDB vector search
- BM25 keyword search
- Hybrid retrieval using Reciprocal Rank Fusion (RRF)
- Cross-encoder reranking
- RAG-based code understanding
- AI-powered code explanations
- AI-powered debugging assistance
- Repository-specific chat
- Persistent chat history
- JWT authentication
- Repository management
- Simple HTML, CSS and JavaScript frontend

## How It Works

```text
                    GitHub Repository
                           |
                           v
                    Repository Clone
                           |
                           v
                      File Scanner
                           |
                           v
                    Code Parsing
                  /                \
             Python AST         Tree-sitter
                  \                /
                   \              /
                    v            v
                   Code-aware Chunking
                           |
                           v
                      Embeddings
                           |
                 +---------+---------+
                 |                   |
                 v                   v
             ChromaDB              BM25
           Vector Search       Keyword Search
                 |                   |
                 +---------+---------+
                           |
                           v
                    Hybrid Retrieval
                         (RRF)
                           |
                           v
                  Cross-Encoder Reranker
                           |
                           v
                    Relevant Context
                           |
                           v
                       Local LLM
                           |
                           v
                    Grounded Answer
