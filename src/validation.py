from src.schemas import ExtractedDocument


def validate_extracted_document(document: ExtractedDocument) -> None:
    required_fields = (
        "document_id", "role", "filename", "file_type", "blocks"
    )

    for field in required_fields:
        if field not in document:
            raise ValueError(f"Thiếu trường: {field}")

    for field in ("document_id", "role", "filename", "file_type"):
        value = document[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} phải là chuỗi không rỗng")

    if document["role"] not in {"BASE", "AMENDMENT", "REFERENCE"}:
        raise ValueError("Vai trò tài liệu không hợp lệ")

    if document["file_type"] not in {"DOCX", "PDF_TEXT"}:
        raise ValueError("Định dạng tài liệu không hợp lệ")

    blocks = document["blocks"]
    if not isinstance(blocks, list):
        raise ValueError("blocks phải là danh sách")

    seen_refs = set()
    has_text = False

    for block in blocks:
        if not isinstance(block, dict):
            raise ValueError("Mỗi block phải là dictionary")

        source_ref = block.get("source_ref")
        text = block.get("text")

        if not isinstance(source_ref, str) or not source_ref.strip():
            raise ValueError("source_ref phải là chuỗi không rỗng")

        if source_ref in seen_refs:
            raise ValueError(f"Vị trí nguồn bị trùng: {source_ref}")

        if not isinstance(text, str):
            raise ValueError("text của block phải là chuỗi")

        seen_refs.add(source_ref)

        if text.strip():
            has_text = True

    if not has_text:
        raise ValueError("Tài liệu không có nội dung chữ đọc được")