"""
Baseline liên kết chỉ dẫn sửa đổi với unit_id của V1.

Chỉ kiểm tra việc tìm số Điều được nhắc trong chỉ dẫn và đối chiếu với V1.
Chưa xử lý: phân biệt văn bản đích, operation (AMEND/ADD/REPEAL),
before_text/after_text. Không thay thế align_versions (legacy).
"""

import re

TARGET_ARTICLE_RE = re.compile(r"Điều\s+(\d+[A-Za-z]?)")


def find_target_units(instruction_text: str, v1_clauses: list[dict]) -> list[str]:
    """
    Trả về danh sách unit_id của Điều V1 được nhắc trong chỉ dẫn.
    Số Điều không có trong V1 bị bỏ qua. Không chắc thì trả [].
    """
    numbers = TARGET_ARTICLE_RE.findall(instruction_text)
    v1_ids = {c["unit_id"] for c in v1_clauses}
    result: list[str] = []
    for number in numbers:
        unit_id = f"v1:article_{number.lower()}"
        if unit_id in v1_ids and unit_id not in result:
            result.append(unit_id)
    return result