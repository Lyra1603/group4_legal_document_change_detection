import sys
import os
# Tự động thêm thư mục gốc của dự án vào đường dẫn tìm kiếm của Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from src.parser.doc_parser import parse_clauses
from src.aligner.version_aligner import align_versions
from src.semantic_diff.diff_engine import run_semantic_diff
from src.classifier_scorer.scorer import classify_and_score
from src.evaluation.evaluator import evaluate_predictions

def run_pipeline(doc_v1_text: str, doc_v2_text: str):
    clauses_v1 = parse_clauses(doc_v1_text)
    clauses_v2 = parse_clauses(doc_v2_text)
    aligned_pairs = align_versions(clauses_v1, clauses_v2)

    for pair in aligned_pairs:
        sem_diff = run_semantic_diff(pair)
        scoring = classify_and_score(pair, sem_diff)
        pair["semantic_diff"] = sem_diff
        pair["scoring"] = scoring

    return aligned_pairs

if __name__ == "__main__":
    sample_v1 = """
Điều 1. Phạm vi điều chỉnh
Hợp đồng này quy định về việc cung cấp dịch vụ phần mềm giữa Bên A và Bên B.
Điều 2. Thời hạn thanh toán
Bên B có nghĩa vụ thanh toán đầy đủ phí dịch vụ cho Bên A trong vòng 30 ngày kể từ ngày nhận hóa đơn.
Điều 3. Phạt vi phạm
Trường hợp chậm thanh toán, Bên B phải chịu mức phạt là 5% giá trị hợp đồng.
"""
    sample_v2 = """
Điều 1. Phạm vi điều chỉnh
Văn bản hợp đồng này quy định chi tiết việc cung ứng dịch vụ phần mềm giữa hai bên A và B.
Điều 2. Nghiệm thu sản phẩm
Hai bên tiến hành nghiệm thu sản phẩm theo từng giai đoạn bàn giao thực tế.
Điều 3. Thời hạn thanh toán
Bên B có nghĩa vụ thanh toán đầy đủ phí dịch vụ cho Bên A trong vòng 15 ngày kể từ ngày nhận hóa đơn.
Điều 4. Phạt vi phạm
Trường hợp chậm thanh toán, Bên B có thể chịu mức phạt là 12% giá trị hợp đồng.
"""
    sample_gt = {
        "Điều 1 -> Điều 1": {"is_meaningful_change": False, "is_critical": False},
        "None -> Điều 2":   {"is_meaningful_change": True,  "is_critical": False},
        "Điều 2 -> Điều 3": {"is_meaningful_change": True,  "is_critical": True},
        "Điều 3 -> Điều 4": {"is_meaningful_change": True,  "is_critical": True},
    }

    results = run_pipeline(sample_v1, sample_v2)
    metrics = evaluate_predictions(results, sample_gt)
    print("=== KẾT QUẢ CHẠY PIPELINE TỪ CÁC MODULE ĐỘC LẬP ===")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print("\n=== ĐIỂM ĐÁNH GIÁ (EVALUATION) ===")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))