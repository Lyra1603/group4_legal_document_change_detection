from src.reader.document_reader import read_document, ReadError

FILE = "data/49.2026.TT.BCA.docx"   # sửa tên file ở đây

try:
    doc = read_document(FILE, "v1", "BASE")
    print("Filename:", doc["filename"], "| Type:", doc["file_type"])
    for b in doc["blocks"]:
        print(b["source_ref"], "|", b["text"])
except ReadError as e:
    print("Lỗi [", e.code, "]:", e.message)