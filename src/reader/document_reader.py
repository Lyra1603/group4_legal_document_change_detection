"""
Reader: đọc file DOCX hoặc PDF có lớp chữ và trả ExtractedDocument.

Quy ước source_ref (SRS mục 1.5 và mục 4):
- DOCX: "docx:paragraph_N" và "docx:table_N", đếm riêng theo loại,
  theo thứ tự xuất hiện trong body; đoạn rỗng vẫn được đếm số.
- PDF:  "pdf:page_N", N bắt đầu từ 1, tính từ trang đầu file.
"""

from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


SUPPORTED_ROLES = {"BASE", "AMENDMENT", "REFERENCE"}


class ReadError(Exception):
    """Lỗi đọc file, kèm mã để tầng API chuyển thành thông báo phù hợp."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _check_file(file_path: str) -> Path:
    path = Path(file_path)
    if not path.is_file():
        raise ReadError("FILE_NOT_FOUND", f"Không tìm thấy file: {path.name}")
    return path


def _check_role(role: str) -> None:
    if role not in SUPPORTED_ROLES:
        raise ValueError(f"role không hợp lệ: {role}")


def _iter_docx_body(document):
    """Duyệt body theo đúng thứ tự xuất hiện: đoạn văn và bảng."""
    for child in document.element.body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, document)
        elif child.tag == qn("w:tbl"):
            yield Table(child, document)


def _table_to_text(table: Table) -> str:
    """Đưa bảng về dạng text: mỗi hàng một dòng, các ô ngăn bởi ' | '."""
    rows = []
    for row in table.rows:
        cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
        rows.append(" | ".join(cells))
    return "\n".join(rows)


def read_docx(file_path: str, document_id: str, role: str) -> dict:
    path = _check_file(file_path)
    try:
        document = Document(str(path))
    except Exception as exc:
        raise ReadError("READ_FAILED", f"Không mở được file DOCX: {path.name}") from exc

    blocks = []
    para_no = 0
    table_no = 0

    for item in _iter_docx_body(document):
        if isinstance(item, Paragraph):
            para_no += 1
            text = item.text.strip()
            if not text:
                continue  # đoạn rỗng vẫn được đếm trong para_no
            blocks.append({"source_ref": f"docx:paragraph_{para_no}", "text": text})
        else:
            table_no += 1
            text = _table_to_text(item).strip()
            if not text:
                continue
            blocks.append({"source_ref": f"docx:table_{table_no}", "text": text})

    if not blocks:
        raise ReadError("NO_TEXT", f"File không có nội dung chữ: {path.name}")

    return {
        "document_id": document_id,
        "role": role,
        "filename": path.name,
        "file_type": "DOCX",
        "blocks": blocks,
    }


def read_pdf(file_path: str, document_id: str, role: str) -> dict:
    path = _check_file(file_path)
    if fitz is None:
        raise ReadError(
            "DEPENDENCY_MISSING",
            "Chưa cài PyMuPDF. Chạy: pip install pymupdf",
        )

    try:
        pdf = fitz.open(str(path))
    except Exception as exc:
        raise ReadError("READ_FAILED", f"Không mở được file PDF: {path.name}") from exc

    blocks = []
    try:
        if pdf.needs_pass:
            raise ReadError("PASSWORD_PROTECTED", f"File PDF có mật khẩu: {path.name}")
        for page_idx in range(len(pdf)):
            text = pdf[page_idx].get_text().strip()
            if not text:
                continue  # trang rỗng vẫn giữ số trang gốc
            blocks.append({"source_ref": f"pdf:page_{page_idx + 1}", "text": text})
    finally:
        pdf.close()

    if not blocks:
        raise ReadError("NO_TEXT", f"PDF không có lớp chữ (có thể là scan): {path.name}")

    return {
        "document_id": document_id,
        "role": role,
        "filename": path.name,
        "file_type": "PDF_TEXT",
        "blocks": blocks,
    }


def read_document(file_path: str, document_id: str, role: str) -> dict:
    """Hàm Reader chính: chọn đọc DOCX hoặc PDF theo đuôi file."""
    _check_role(role)
    suffix = Path(file_path).suffix.lower()
    if suffix == ".docx":
        return read_docx(file_path, document_id, role)
    if suffix == ".pdf":
        return read_pdf(file_path, document_id, role)
    raise ReadError("UNSUPPORTED_FORMAT", f"Định dạng không hỗ trợ: {suffix}")