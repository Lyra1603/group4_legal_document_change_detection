import json
from time import monotonic
from backend.app.document_processing.parser.doc_parser import parse_clauses
from backend.app.change_analysis.aligner.version_aligner import align_versions
from backend.app.change_analysis.semantic_diff.diff_engine import run_semantic_diff
from backend.app.change_analysis.classifier_scorer.scorer import classify_and_score
from backend.app.document_processing.document_reader import read_document
from backend.app.document_processing.parser.doc_parser import parse_document


def read_and_parse_document(file_path: str, document_id: str, role: str, on_stage=None):
    """Read a file and keep both source blocks and article-level clauses.

    This ingestion entry point does not compare V1 against amendment S.
    """
    start = monotonic()
    try:
        document = read_document(file_path, document_id, role)
    finally:
        if on_stage:
            on_stage('reader', monotonic() - start)
    start = monotonic()
    try:
        if role == 'REFERENCE':
            # References may contain only tables or unnumbered paragraphs.
            from backend.app.document_processing.document_reader import ReadError
            try:
                clauses = parse_document(document)
            except ReadError as exc:
                if exc.code != 'STRUCTURE_NOT_FOUND':
                    raise
                clauses = []
        else:
            clauses = parse_document(document)
    finally:
        if on_stage:
            on_stage('parser', monotonic() - start)
    return {'document': document, 'clauses': clauses}

def run_pipeline(doc_v1_text: str, doc_v2_text: str):
    clauses_v1 = parse_clauses(doc_v1_text, 'v1')
    clauses_v2 = parse_clauses(doc_v2_text, 'v2')
    aligned_pairs = align_versions(clauses_v1, clauses_v2)

    for pair in aligned_pairs:
        sem_diff = run_semantic_diff(pair)
        scoring = classify_and_score(pair, sem_diff)
        pair["semantic_diff"] = sem_diff
        pair["scoring"] = scoring

    return aligned_pairs

if __name__ == "__main__":
    from src.evaluation.evaluator import evaluate_predictions
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
