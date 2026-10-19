from pathlib import Path
from typing import Dict, List

from docx import Document

try:
    import fitz
except ImportError:
    fitz = None


def read_docx(
    file_path: str,
    document_id: str,
    role: str,
) -> Dict:
    """
    Đọc file DOCX và giữ vị trí nguồn.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file: {file_path}"
        )

    document = Document(file_path)

    blocks: List[Dict] = []

    for idx, paragraph in enumerate(
        document.paragraphs,
        start=1,
    ):
        text = paragraph.text.strip()

        if not text:
            continue

        blocks.append(
            {
                "source_ref": f"docx:paragraph_{idx}",
                "text": text,
            }
        )

    return {
        "document_id": document_id,
        "role": role,
        "filename": path.name,
        "file_type": "DOCX",
        "blocks": blocks,
    }


def read_pdf(
    file_path: str,
    document_id: str,
    role: str,
) -> Dict:
    """
    Đọc PDF có lớp text.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file: {file_path}"
        )

    if fitz is None:
        raise ImportError(
            "Chưa cài PyMuPDF. "
            "Chạy: pip install pymupdf"
        )

    pdf = fitz.open(file_path)

    blocks: List[Dict] = []

    for page_idx in range(len(pdf)):
        page = pdf[page_idx]

        text = page.get_text().strip()

        if not text:
            continue

        blocks.append(
            {
                "source_ref": f"pdf:page_{page_idx + 1}",
                "text": text,
            }
        )

    pdf.close()

    return {
        "document_id": document_id,
        "role": role,
        "filename": path.name,
        "file_type": "PDF_TEXT",
        "blocks": blocks,
    }


def read_document(
    file_path: str,
    document_id: str,
    role: str,
) -> Dict:
    """
    Hàm Reader chính.
    """

    suffix = Path(file_path).suffix.lower()

    if suffix == ".docx":
        return read_docx(
            file_path=file_path,
            document_id=document_id,
            role=role,
        )

    if suffix == ".pdf":
        return read_pdf(
            file_path=file_path,
            document_id=document_id,
            role=role,
        )

    raise ValueError(
        f"Định dạng không hỗ trợ: {suffix}"
    )

