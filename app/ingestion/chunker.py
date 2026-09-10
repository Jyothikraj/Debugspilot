

from app.ingestion.file_parser import parse_file
from app.ingestion.file_scanner import scan_project

from app.ingestion.ast_parser import (
    parse_python_code,
    extract_python_structure,
)

from app.ingestion.js_parser import (
    parse_javascript_code,
    extract_javascript_structure,
)

from app.ingestion.java_parser import (
    parse_java_code,
    extract_java_structure,
)

from app.ingestion.cpp_parser import (
    parse_cpp_code,
    extract_cpp_structure,
)




# ============================================================
# VALIDATION
# ============================================================

def is_valid_chunk(chunk):
    content = chunk.get("content", "")
    return bool(content and content.strip())


# ============================================================
# METADATA NORMALIZATION
# ============================================================

def normalize_metadata(data):
    return {
        "file": str(data.get("file", "")),
        "language": str(data.get("language", "")),
        "type": str(data.get("type", "")),
        "class": str(data.get("class", "")),
        "function": str(data.get("function", "")),
        "start_line": int(data.get("start_line", 0) or 0),
        "end_line": int(data.get("end_line", 0) or 0),
    }


# ============================================================
# CREATE CHUNK
# ============================================================

def create_code_chunk(code_data):
    chunk = {
        "content": code_data.get("content", ""),
        "metadata": normalize_metadata(code_data),
    }

    return chunk


# ============================================================
# CREATE CHUNKS
# ============================================================

def create_chunks(code_units):
    chunks = []

    for code_unit in code_units:
        chunk = create_code_chunk(code_unit)

        if is_valid_chunk(chunk):
            chunks.append(chunk)

    return chunks


# ============================================================
# GENERIC TEXT CHUNK
# ============================================================

def create_text_chunk(file_path, parsed_file):
    content = parsed_file.get("content", "")

    if not content.strip():
        return None

    language = (
        parsed_file
        .get("metadata", {})
        .get("language", "unknown")
    )

    return {
        "content": content,
        "metadata": {
            "file": str(file_path),
            "language": str(language),
            "type": "document",
            "class": "",
            "function": "",
            "start_line": 1,
            "end_line": len(content.splitlines()),
        },
    }


# ============================================================
# PYTHON
# ============================================================

def chunk_python_file(file_path, parsed_file):
    code = parsed_file["content"]

    tree = parse_python_code(code)

    structure = extract_python_structure(
        tree,
        file_path,
        code,
    )

    code_units = []

    # --------------------------------------------------------
    # Functions
    # --------------------------------------------------------

    for function in structure.get("functions", []):
        function["type"] = "function"
        code_units.append(function)

    # --------------------------------------------------------
    # Classes
    # --------------------------------------------------------

    for class_data in structure.get("classes", []):
        class_data["type"] = "class"
        code_units.append(class_data)

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not code_units:
        chunk = create_text_chunk(
            file_path,
            parsed_file,
        )

        return [chunk] if chunk else []

    return create_chunks(code_units)


# ============================================================
# JAVASCRIPT / TYPESCRIPT
# ============================================================

def chunk_javascript_file(file_path, parsed_file):
    code = parsed_file["content"]

    tree = parse_javascript_code(code)

    structure = extract_javascript_structure(
        tree,
        file_path,
        code,
    )

    code_units = []

    # --------------------------------------------------------
    # Functions
    # --------------------------------------------------------

    for function in structure.get("functions", []):
        function["type"] = "function"
        code_units.append(function)

    # --------------------------------------------------------
    # Classes
    # --------------------------------------------------------

    for class_data in structure.get("classes", []):
        class_data["type"] = "class"
        code_units.append(class_data)

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not code_units:
        chunk = create_text_chunk(
            file_path,
            parsed_file,
        )

        return [chunk] if chunk else []

    return create_chunks(code_units)


# ============================================================
# JAVA
# ============================================================

def chunk_java_file(file_path, parsed_file):
    code = parsed_file["content"]

    tree = parse_java_code(code)

    structure = extract_java_structure(
        tree,
        file_path,
        code,
    )

    code_units = []

    # --------------------------------------------------------
    # Functions / Methods
    # --------------------------------------------------------

    for function in structure.get("functions", []):
        function["type"] = "function"
        code_units.append(function)

    # --------------------------------------------------------
    # Classes
    # --------------------------------------------------------

    for class_data in structure.get("classes", []):
        class_data["type"] = "class"
        code_units.append(class_data)

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not code_units:
        chunk = create_text_chunk(
            file_path,
            parsed_file,
        )

        return [chunk] if chunk else []

    return create_chunks(code_units)


# ============================================================
# C / C++
# ============================================================

def chunk_cpp_file(file_path, parsed_file):
    code = parsed_file["content"]

    print(
        "    C++: parsing...",
        flush=True,
    )

    tree = parse_cpp_code(code)

    print(
        "    C++: parsing complete",
        flush=True,
    )

    print(
        "    C++: extracting structure...",
        flush=True,
    )

    structure = extract_cpp_structure(
        tree,
        file_path,
        code,
    )

    print(
        "    C++: extraction complete",
        flush=True,
    )

    functions = structure.get(
        "functions",
        [],
    )

    classes = structure.get(
        "classes",
        [],
    )

    print(
        f"    C++: functions={len(functions)}, "
        f"classes={len(classes)}",
        flush=True,
    )

    # --------------------------------------------------------
    # Combine classes and functions
    # --------------------------------------------------------

    code_units = []

    code_units.extend(classes)
    code_units.extend(functions)

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not code_units:
        chunk = create_text_chunk(
            file_path,
            parsed_file,
        )

        return [chunk] if chunk else []

    chunks = create_chunks(code_units)

    print(
        f"    C++: chunks={len(chunks)}",
        flush=True,
    )

    return chunks


# ============================================================
# MAIN PROJECT CHUNKER
# ============================================================

def chunk_project(files):
    all_chunks = []

    total_files = len(files)

    print(
        f"\nStarting chunking... {total_files} files",
        flush=True,
    )

    for index, file_path in enumerate(
        files,
        start=1,
    ):
        print(
            f"[{index}/{total_files}] {file_path.name}",
            flush=True,
        )

        extension = file_path.suffix.lower()

        try:

            # ------------------------------------------------
            # Read file
            # ------------------------------------------------

            parsed_file = parse_file(
                file_path
            )

            # ------------------------------------------------
            # Python
            # ------------------------------------------------

            if extension == ".py":
                chunks = chunk_python_file(
                    file_path,
                    parsed_file,
                )

            # ------------------------------------------------
            # JavaScript / TypeScript
            # ------------------------------------------------

            elif extension in {
                ".js",
                ".jsx",
                ".ts",
                ".tsx",
            }:
                chunks = chunk_javascript_file(
                    file_path,
                    parsed_file,
                )

            # ------------------------------------------------
            # Java
            # ------------------------------------------------

            elif extension == ".java":
                chunks = chunk_java_file(
                    file_path,
                    parsed_file,
                )

            # ------------------------------------------------
            # C / C++
            # ------------------------------------------------

            elif extension in {
                ".c",
                ".cpp",
                ".cc",
                ".cxx",
                ".h",
                ".hpp",
            }:
                chunks = chunk_cpp_file(
                    file_path,
                    parsed_file,
                )

            # ------------------------------------------------
            # Other files
            # ------------------------------------------------

            else:
                chunk = create_text_chunk(
                    file_path,
                    parsed_file,
                )

                chunks = [chunk] if chunk else []

            # ------------------------------------------------
            # Store results
            # ------------------------------------------------

            all_chunks.extend(chunks)

            print(
                f"    chunks: {len(chunks)}",
                flush=True,
            )

        except Exception as error:
            print(
                f"    ERROR: "
                f"{type(error).__name__}: {error}",
                flush=True,
            )

            continue

    # ========================================================
    # CHUNKING COMPLETE
    # ========================================================

    print(
        f"\nChunking completed: "
        f"{len(all_chunks)} total chunks",
        flush=True,
    )

    # ========================================================
    # GEMINI SUMMARIZATION
    # ========================================================

    
        

        

    return all_chunks


# ============================================================
# EMBEDDING TEXT
# ============================================================

def get_embedding_text(chunk):
    summary = chunk["metadata"].get(
        "summary",
        "",
    )

    return f"""
Summary:
{summary}

Code:
{chunk["content"]}
""".strip()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    files = scan_project(
        "test_project"
    )

    chunks = chunk_project(
        files
    )

    print(
        f"\nGenerated {len(chunks)} chunks."
    )

    for index, chunk in enumerate(
        chunks,
        start=1,
    ):

        metadata = chunk["metadata"]

        print(
            f"\n========== CHUNK {index} =========="
        )

        print(
            "File:",
            metadata["file"],
        )

        print(
            "Language:",
            metadata["language"],
        )

        print(
            "Type:",
            metadata["type"],
        )

        print(
            "Class:",
            metadata["class"],
        )

        print(
            "Function:",
            metadata["function"],
        )

        print(
            "Lines:",
            metadata["start_line"],
            "-",
            metadata["end_line"],
        )

        print(
            "Summary:",
            metadata.get(
                "summary",
                "",
            ),
        )

        print(
            "\nCONTENT:"
        )

        print(
            chunk["content"]
        )