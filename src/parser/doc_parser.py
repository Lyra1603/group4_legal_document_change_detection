import re
from typing import List
from src.schemas import Clause

def parse_clauses(text: str) -> List[Clause]:
    """
    Hiện tại: Dùng Regex tách Điều/Khoản từ chuỗi văn bản.
    Cần nâng cấp: Dùng PyMuPDF / OCR đọc từ file PDF thực tế.
    """
    pattern = r"(Điều \d+)\.\s*([^\n]+)\n(.*?)(?=Điều \d+\.|$)"
    matches = re.findall(pattern, text.strip(), re.DOTALL)
    return [
        {"id": m[0].strip(), "title": m[1].strip(), "content": m[2].strip()}
        for m in matches
    ]