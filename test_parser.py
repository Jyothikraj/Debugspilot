from app.ingestion.file_parser import parse_file


result = parse_file("test_project/app/main.py")

print("CONTENT:")
print(result["content"])

print("\nMETADATA:")
print(result["metadata"])

