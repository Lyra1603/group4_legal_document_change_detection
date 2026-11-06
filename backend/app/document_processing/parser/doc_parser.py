import re
from typing import List
from backend.app.schemas.contracts import Clause
from backend.app.schemas.contracts import ExtractedDocument
from backend.app.schemas.validation import validate_extracted_document
from backend.app.document_processing.document_reader import ReadError


ARTICLE_RE = re.compile(r"^Điều\s+(\d+[a-zđ]?)\.\s*(.*)$", re.IGNORECASE)
SECTION_RE = re.compile(r"^(?:Phần|Chương|Mục|Tiểu mục)\s+", re.IGNORECASE)
END_RE = re.compile(r"^(?:Nơi nhận\s*:|PHỤ LỤC\b|TM\.|KT\.|TL\.|TUQ\.)", re.IGNORECASE)


def parse_document(document: ExtractedDocument) -> List[Clause]:
    """Article-level baseline; source refs resolve against document.blocks.

    Keeps table text in the current article. Does not interpret amendments,
    quoted article headings, automatic Word numbering, or nested structure.
    Keep the original ExtractedDocument for preamble/outside content.
    """
    validate_extracted_document(document)
    clauses: List[Clause] = []
    current = None
    seen = set()
    ended = False
    for block in document['blocks']:
        is_table = block['source_ref'].startswith('docx:table_')
        for line in block['text'].splitlines():
            line = line.strip()
            if not line or ended:
                continue
            if not is_table and END_RE.match(line):
                current = None
                ended = True
                continue
            if not is_table and SECTION_RE.match(line):
                current = None
                continue
            match = None if is_table else ARTICLE_RE.match(line)
            if match:
                number, title = match.groups()
                unit_id = f"{document['document_id']}:article_{number.lower()}"
                if unit_id in seen:
                    raise ReadError('AMBIGUOUS_STRUCTURE', 'Nhãn Điều trùng hoặc nằm trong trích dẫn; cần parser cấu trúc nâng cao.')
                seen.add(unit_id)
                current = Clause(unit_id=unit_id, id=f'Điều {number}',
                                 title=title.strip(), content='',
                                 source_refs=[block['source_ref']])
                clauses.append(current)
            elif current is not None:
                current['content'] += ('\n' if current['content'] else '') + line
                if block['source_ref'] not in current['source_refs']:
                    current['source_refs'].append(block['source_ref'])
    if not clauses:
        raise ReadError('STRUCTURE_NOT_FOUND', f"Không tìm thấy Điều trong {document['filename']}")
    return clauses

def parse_clauses(text: str, document_id: str = 'text') -> List[Clause]:
    """
    Hiện tại: Dùng Regex tách Điều/Khoản từ chuỗi văn bản.
    Cần nâng cấp: Dùng PyMuPDF / OCR đọc từ file PDF thực tế.
    """
    pattern = r"(Điều \d+)\.\s*([^\n]+)\n(.*?)(?=Điều \d+\.|$)"
    matches = re.findall(pattern, text.strip(), re.DOTALL)
    return [
        {"unit_id": f"{document_id}:article_{m[0].split()[-1]}",
         "id": m[0].strip(), "title": m[1].strip(), "content": m[2].strip(),
         "source_refs": []}
        for m in matches
    ]
