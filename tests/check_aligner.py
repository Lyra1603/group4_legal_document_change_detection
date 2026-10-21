from tests.fixtures.ex01 import (
    V1_CLAUSES, S_CLAUSES, EXPECTED_TARGET,
    CASE_OTHER_DOC, CASE_MISSING, CASE_MULTI,
)
from src.aligner.amendment_linker_baseline import find_target_units

cases = [
    ("Ca 1: chỉ dẫn gốc", S_CLAUSES[0]["content"], EXPECTED_TARGET),
    ("Ca 2: có Điều của văn bản khác", CASE_OTHER_DOC["instruction"], CASE_OTHER_DOC["expected"]),
    ("Ca 3: Điều không có trong V1", CASE_MISSING["instruction"], CASE_MISSING["expected"]),
    ("Ca 4: nhiều Điều", CASE_MULTI["instruction"], CASE_MULTI["expected"]),
]

all_ok = True
for name, text, expected in cases:
    result = find_target_units(text, V1_CLAUSES)
    ok = result == expected
    all_ok = all_ok and ok
    print(name, "| kết quả:", result, "| mong đợi:", expected, "|", "ĐÚNG" if ok else "SAI")

print("TỔNG:", "ĐẠT" if all_ok else "CHƯA ĐẠT")