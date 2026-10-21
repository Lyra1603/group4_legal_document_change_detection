from src.reader.document_reader import read_document
from src.parser.doc_parser import parse_document

doc = read_document("data/49.2026.TT.BCA.docx", "v1", "BASE")
clauses = parse_document(doc)
for i in (0, 9, 20):   # Điều 1, 10, 21
    c = clauses[i]
    print("=====", c["unit_id"], "|", c["title"])
    print(c["content"])
    print("source_refs:", c["source_refs"][0], "...", c["source_refs"][-1])