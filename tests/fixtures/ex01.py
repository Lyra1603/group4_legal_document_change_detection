V1_CLAUSES = [
    {
        "unit_id": "v1:article_5",
        "id": "Điều 5",
        "title": "Nộp hồ sơ",
        "content": "1. Hồ sơ phải được nộp trong thời hạn 30 ngày.\n2. Hồ sơ gồm đơn và giấy tờ liên quan.",
        "source_refs": ["docx:paragraph_13", "docx:paragraph_14"],
    },
    {
        "unit_id": "v1:article_6",
        "id": "Điều 6",
        "title": "Hiệu lực",
        "content": "Thông tư này có hiệu lực từ ngày ký.",
        "source_refs": ["docx:paragraph_20"],
    },
]

S_CLAUSES = [
    {
        "unit_id": "s:article_1",
        "id": "Điều 1",
        "title": "Sửa đổi Điều 5",
        "content": "Sửa đổi khoản 1 Điều 5 của Văn bản A: thay cụm từ \"30 ngày\" bằng cụm từ \"15 ngày\".",
        "source_refs": ["docx:paragraph_1", "docx:paragraph_2"],
    },
]

EXPECTED_TARGET = ["v1:article_5"]

# Ca 2: chỉ dẫn nhắc Điều 31 của Luật (văn bản khác), V1 không có Điều 31
CASE_OTHER_DOC = {
    "instruction": "Căn cứ khoản 2 Điều 31 của Luật Dẫn độ, sửa đổi khoản 1 Điều 5 của Văn bản A.",
    "expected": ["v1:article_5"],
}

# Ca 3: số Điều không tồn tại trong V1
CASE_MISSING = {
    "instruction": "Bãi bỏ khoản 2 Điều 99 của Văn bản A.",
    "expected": [],
}

# Ca 4: nhắc nhiều Điều của V1
CASE_MULTI = {
    "instruction": "Sửa đổi Điều 5 và Điều 6 của Văn bản A.",
    "expected": ["v1:article_5", "v1:article_6"],
}