"""Nhận diện số ký hiệu của chính văn bản và đặt tên đầu ra an toàn Windows.

Không lấy số hiệu đầu tiên trong phần căn cứ/nội dung sửa đổi làm số hiệu của S.
HTML/PDF thiếu số hiệu phải dùng metadata đã đối chiếu (--document-number),
hoặc chỉ định tên đầu ra thủ công. Không tự đoán từ dẫn chiếu.
"""
from pathlib import Path
import re
import unicodedata

_SYMBOL = r'[A-ZĐ][A-ZĐ0-9]*(?:\s*-\s*[A-ZĐ0-9]+)*'
_NUMBER = rf'\d{{1,6}}\s*/\s*(?:\d{{4}}\s*/\s*)?{_SYMBOL}(?:\s*/\s*{_SYMBOL})*'
_LEGACY_NUMBER = rf'\d{{1,6}}\s*-\s*{_SYMBOL}'
_EXACT = re.compile(rf'(?:{_NUMBER}|{_LEGACY_NUMBER})', re.IGNORECASE)
_LABEL = re.compile(rf'(?:^|\n)\s*(?:Số\s*[:：]|Số\s+(?:ký\s*hiệu|hiệu)\s*[:：]?|Ký\s*hiệu\s*[:：]?)\s*({_NUMBER})(?![\w/])', re.IGNORECASE)
_TITLE = re.compile(rf'^\s*(?:Bộ\s+luật|Luật|Nghị\s+định|Thông\s+tư(?:\s+liên\s+tịch)?|Nghị\s+quyết|Quyết\s+định|Văn\s+bản\s+hợp\s+nhất|Pháp\s+lệnh|Lệnh)\s+(?:số\s*[:：]?\s*)?({_NUMBER})(?![\w/])', re.IGNORECASE)


def normalize_document_number(value):
    """Giữ số 0 đầu, chuẩn hóa Unicode/hoa/khoảng trắng quanh dấu phân cách."""
    value = unicodedata.normalize('NFC', value).strip()
    value = value.translate(str.maketrans({'–': '-', '—': '-', '‑': '-', '−': '-'}))
    if not _EXACT.fullmatch(value):
        raise ValueError(f'Số ký hiệu không hợp lệ: {value!r}. Ví dụ: 84/2026/TT-BXD.')
    return re.sub(r'\s+', '', value).upper()


def identify_document_number(text='', *, title='', metadata=(), provided=None):
    """Trả (number hoặc None, bằng chứng); xung đột thì dừng thay vì chọn ngẫu nhiên.

    metadata: các giá trị đã gắn nhãn số ký hiệu của tài liệu, không phải các
    số hiệu bất kỳ tìm trong nội dung. provided là giá trị người gọi cung cấp.
    """
    evidence = []

    def add(value, origin):
        evidence.append({'value': normalize_document_number(value), 'source': origin})

    if provided is not None:
        add(provided, 'provided_metadata')
    for value in metadata:
        add(value, 'html_metadata')
    # Header ends before citations/body; numbers there identify other documents.
    header = unicodedata.normalize('NFC', text[:12000])
    header = re.split(r'(?:^|\n)\s*(?:Căn\s+cứ\b|Điều\s+\d+[a-zđ]?\s*\.|Chương\s+[IVXLCDM\d]+\b)', header, maxsplit=1, flags=re.I)[0]
    header = header.translate(str.maketrans({'–': '-', '—': '-', '‑': '-', '−': '-'}))
    for match in _LABEL.finditer(header):
        add(match.group(1), 'document_header')
    match = _TITLE.match(unicodedata.normalize('NFC', title))
    if match:
        add(match.group(1), 'document_title')
    candidates = {item['value'] for item in evidence}
    if len(candidates) > 1:
        raise ValueError('Số ký hiệu mơ hồ/xung đột giữa các nguồn: ' + ', '.join(sorted(candidates)))
    return (next(iter(candidates)) if candidates else None), evidence


def resolve_docx_output(source, output_path, number, output_dir=None):
    """Mặc định đặt cạnh nguồn; '/' -> '_', không tự thêm hậu tố khi trùng."""
    if output_path is not None and output_dir is not None:
        raise ValueError('Chọn tên đầu ra thủ công hoặc --output-dir, không dùng đồng thời.')
    if output_path is not None:
        output = Path(output_path)
    else:
        if not number:
            raise ValueError('Không xác định được số ký hiệu của văn bản. Cung cấp --document-number từ metadata đã đối chiếu hoặc tên đầu ra thủ công.')
        safe = normalize_document_number(number).replace('/', '_')
        output = (Path(output_dir) if output_dir is not None else Path(source).parent) / (safe + '.docx')
    if output.suffix.lower() != '.docx':
        raise ValueError('Đầu ra phải là .docx.')
    return output
