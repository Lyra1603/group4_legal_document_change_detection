import re
from src.schemas import AlignedPair, SemanticDiffResult

def run_semantic_diff(pair: AlignedPair) -> SemanticDiffResult:
    """
    Hiện tại: Bản Baseline dùng Rule/Regex bắt thay đổi số liệu và từ khóa pháp lý.
    Cần nâng cấp: Kết hợp NLP / LLM để bắt thay đổi ngữ nghĩa sâu hơn.
    """
    if pair["align_type"] in ["ADDED", "DELETED"]:
        return {"is_meaningful_change": True, "diff_details": f"Điều khoản bị {pair['align_type']}"}

    t1 = pair["v1"]["content"] if pair["v1"] else ""
    t2 = pair["v2"]["content"] if pair["v2"] else ""
    if t1 == t2:
        return {"is_meaningful_change": False, "diff_details": "Giống hệt 100%"}

    numbers_v1 = re.findall(r"\d+(?:%| ngày| tháng| năm| đồng)?", t1)
    numbers_v2 = re.findall(r"\d+(?:%| ngày| tháng| năm| đồng)?", t2)

    modal_words = ["phải", "có nghĩa vụ", "không được", "có quyền", "có thể", "bắt buộc"]
    modals_v1 = [w for w in modal_words if w in t1.lower()]
    modals_v2 = [w for w in modal_words if w in t2.lower()]

    if numbers_v1 != numbers_v2 or modals_v1 != modals_v2:
        return {
            "is_meaningful_change": True,
            "diff_details": f"Số liệu: {numbers_v1} -> {numbers_v2} | Tính chất: {modals_v1} -> {modals_v2}"
        }

    return {"is_meaningful_change": False, "diff_details": "Chỉ thay đổi cách diễn đạt/văn phong"}