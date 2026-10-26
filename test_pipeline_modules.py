import json
from src.text_diff.diff_engine import compute_text_diff
from src.semantic_diff.diff_engine import detect_semantic_changes
from src.classifier_scorer.scorer import classify_and_score

def test_pipeline():
    print("=" * 60)
    print("BẮT ĐẦU KIỂM THỬ LIÊN HOÀN 3 MODULE (Text Diff -> Semantic Diff -> Scorer)")
    print("=" * 60)

    # 1. Dữ liệu đầu vào giả định cho 1 yêu cầu sửa đổi (AmendmentItem)
    amendment_id = "amendment_test_01"
    before_text = "Hồ sơ phải được nộp trong thời hạn 30 ngày."
    after_text = "Hồ sơ phải được nộp trong thời hạn 15 ngày."

    print(f"\n[INPUT]")
    print(f"- Before Text: {before_text}")
    print(f"- After Text : {after_text}\n")

    # 2. Bước 1: Chạy Text Diff
    text_diff_res = compute_text_diff(amendment_id, before_text, after_text)
    print("------------------------------------------------------------")
    print("[STEP 1] Kết quả Text Diff:")
    if text_diff_res:
        print(text_diff_res.model_dump_json(indent=2))
    else:
        print("Text Diff trả về None (Do thiếu chuỗi before hoặc after).")

    # 3. Bước 2: Chạy Semantic Diff
    semantic_diff_res = detect_semantic_changes(amendment_id, before_text, after_text)
    print("------------------------------------------------------------")
    print("[STEP 2] Kết quả Semantic Diff:")
    print(semantic_diff_res.model_dump_json(indent=2))

    # 4. Bước 3: Chạy Classifier & Scorer cho từng SemanticChange phát hiện được
    print("------------------------------------------------------------")
    print("[STEP 3] Kết quả Classifier & Scorer:")
    for change in semantic_diff_res.changes:
        # Chuyển aspects từ Pydantic Model sang dict để truyền vào scorer
        aspects_dict = [aspect.model_dump() for aspect in change.aspects]
        
        scoring_res = classify_and_score(
            change_id=change.change_id,
            aspects=aspects_dict,
            diff_details=change.diff_details
        )
        print(scoring_res.model_dump_json(indent=2))

    print("\n" + "=" * 60)
    print("KIỂM THỬ HOÀN TẤT THÀNH CÔNG!")
    print("=" * 60)

if __name__ == "__main__":
    test_pipeline()