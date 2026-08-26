from app.ingestion.file_scanner import scan_project


files = scan_project("test_project")

for file in files:
    print(file)