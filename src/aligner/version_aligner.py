from difflib import SequenceMatcher
from typing import List
from src.schemas import Clause, AlignedPair

def align_versions(clauses_v1: List[Clause], clauses_v2: List[Clause], threshold: float = 0.45) -> List[AlignedPair]:
    """
    Ghép cặp các điều khoản tương ứng giữa phiên bản v1 và v2.
    """
    aligned: List[AlignedPair] = []
    used_v2 = set()

    for c1 in clauses_v1:
        best_c2, best_score, best_idx = None, 0.0, -1
        for idx, c2 in enumerate(clauses_v2):
            if idx in used_v2:
                continue
            title_sim = SequenceMatcher(None, c1["title"], c2["title"]).ratio()
            content_sim = SequenceMatcher(None, c1["content"], c2["content"]).ratio()
            score = 0.4 * title_sim + 0.6 * content_sim
            if score > best_score:
                best_score, best_c2, best_idx = score, c2, idx

        if best_score >= threshold and best_c2 is not None:
            used_v2.add(best_idx)
            aligned.append({
                "pair_key": f"{c1['id']} -> {best_c2['id']}",
                "v1": c1,
                "v2": best_c2,
                "align_type": "PAIRED",
                "similarity_score": round(best_score, 3),
                "semantic_diff": None,
                "scoring": None
            })
        else:
            aligned.append({
                "pair_key": f"{c1['id']} -> None",
                "v1": c1,
                "v2": None,
                "align_type": "DELETED",
                "similarity_score": 0.0,
                "semantic_diff": None,
                "scoring": None
            })

    for idx, c2 in enumerate(clauses_v2):
        if idx not in used_v2:
            aligned.append({
                "pair_key": f"None -> {c2['id']}",
                "v1": None,
                "v2": c2,
                "align_type": "ADDED",
                "similarity_score": 0.0,
                "semantic_diff": None,
                "scoring": None
            })
    return aligned