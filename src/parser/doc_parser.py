import re

from src.reader.document_reader import ReadError

# Đầu Điều: "Điều 1." / "Điều 5a." ở đầu block, sau đó là tiêu đề
ARTICLE_RE = re.compile(r"^Điều\s+(\d+[A-Za-z]?)\.\s*(.*)$")

# Đầu Chương/Mục: "Chương I", "Mục 2"
SECTION_RE = re.compile(r"^(Chương|Mục)\s+[IVXLC\d]+", re.IGNORECASE)


def parse_document(doc: dict) -> list[dict]:
    """
    Tách ExtractedDocument thành list[Clause].
    Block ngoài Điều (Chương, phần mở đầu, bảng) không được gộp vào Điều nào.
    """
    document_id = doc["document_id"]
    clauses: list[dict] = []
    current: dict | None = None

    for block in doc["blocks"]:
        text = block["text"].strip()
        source_ref = block["source_ref"]

        # Bảng (ví dụ "Nơi nhận") nằm ngoài nội dung Điều: đóng Điều hiện tại
        if source_ref.startswith("docx:table_"):
            current = None
            continue

        match = ARTICLE_RE.match(text)

        if match:
            number = match.group(1)
            title = match.group(2).strip().rstrip(".")
            current = {
                "unit_id": f"{document_id}:article_{number.lower()}",
                "id": f"Điều {number}",
                "title": title,
                "content_parts": [],
                "source_refs": [source_ref],
            }
            clauses.append(current)
        elif current is not None:
            # Chương/Mục nằm giữa hai Điều sẽ đóng Điều trước
            if SECTION_RE.match(text):
                current = None
                continue
            current["content_parts"].append(text)
            current["source_refs"].append(source_ref)

    if not clauses:
        raise ReadError(
            "STRUCTURE_NOT_FOUND",
            f"Không tìm thấy Điều nào trong: {doc['filename']}",
        )

    for clause in clauses:
        clause["content"] = "\n".join(clause.pop("content_parts"))
    return clauses