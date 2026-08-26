from pathlib import Path

from app.ingestion.js_parser import (
    parse_javascript_code,
    extract_javascript_structure
)


file_path = Path(
    r"C:\Users\JYOTHI~1\AppData\Local\Temp\debugpilot_88t38237\repository\staticfiles\admin\js\SelectFilter2.js"
)

print("1. Reading file...")

code = file_path.read_text(
    encoding="utf-8",
    errors="replace"
)

print("2. File read:", len(code))

print("3. Parsing...")

tree = parse_javascript_code(code)

print("4. Parsing completed")
print("Root:", tree.root_node.type)
print("Has errors:", tree.root_node.has_error)

print("5. Starting extraction...")

result = extract_javascript_structure(
    tree,
    file_path,
    code
)

print("6. Extraction completed")

print("Functions:", len(result["functions"]))
print("Classes:", len(result["classes"]))
print("Imports:", len(result["imports"]))
print("Exports:", len(result["exports"]))

print("7. SUCCESS")