"""Evidence-aware scoring baseline following data-annotation-guide section 5."""
from src.analysis_contracts import ChangeAspect, ScoringResult, SemanticChange
from src.semantic_diff.diff_engine import deadline_values

PRIORITY = ('CONSEQUENCES_SANCTIONS', 'RIGHTS_DUTIES_ACTIONS', 'SUBJECT_OBJECT',
            'CONDITIONS_EXCEPTIONS', 'PROCEDURE_AUTHORITY', 'TIME_QUANTITY',
            'SCOPE_EFFECT_TRANSITION', 'DEFINITIONS_REFERENCES')


def classify_and_score(change_id: str, aspects: list[dict], diff_details: str, *,
                       is_meaningful_change: bool | None = None,
                       needs_review: bool = False, review_reason: str = '') -> ScoringResult:
    """Old three-argument calls remain accepted but cannot imply certainty.

    No length-based scores. CRITICAL requires external review and is not inferred.
    """
    parsed = [ChangeAspect.model_validate(a) for a in aspects]
    reasons = [review_reason] if review_reason else []
    if needs_review and not review_reason:
        reasons.append('Kết luận ngữ nghĩa cần review.')
    for a in parsed:
        if a.needs_review or a.field_group is None:
            reasons.append(a.review_reason or 'Khía cạnh chưa xác định đầy đủ.')
        if not a.evidence or not all(e.document_id.strip() and e.source_refs and e.quote
                                    and all(r.strip() for r in e.source_refs) for e in a.evidence):
            reasons.append('Khía cạnh thiếu bằng chứng nguồn.')
    groups = {a.field_group for a in parsed if not a.needs_review}
    category = next((g for g in PRIORITY if g in groups), None)
    level = None
    if is_meaningful_change is False and not parsed and not reasons:
        category, level = 'WORDING_ONLY', 'LOW'
    elif is_meaningful_change is True and parsed and not reasons:
        def supported(a):
            if a.field_group != 'TIME_QUANTITY' or not a.old_quote or not a.new_quote:
                return False
            sources_ok = all(any(q in e.quote for e in a.evidence) for q in (a.old_quote, a.new_quote))
            return sources_ok and deadline_values(a.old_quote, a.new_quote) == (a.old_value, a.new_value)
        if all(supported(a) for a in parsed):
            level = 'HIGH'
        else:
            reasons.append('Cần review mức độ theo rubric; baseline chưa tự chấm dạng này.')
    else:
        reasons.append('Chưa đủ căn cứ kết luận và chấm mức độ tổng thể.')
    if reasons:
        level = None
    reason = ' '.join(dict.fromkeys(reasons))
    explanation = ('LOW: diễn đạt tương đương, không đổi nghĩa.' if level == 'LOW' else
        'HIGH: thay đổi thời hạn thực hiện theo rubric pilot; không tự coi là CRITICAL.' if level else
        'Chưa xác định mức độ; giữ các khía cạnh đã có căn cứ.')
    return ScoringResult(change_id=change_id, category=category, significance=level,
        is_critical=(level == 'CRITICAL') if level else None,
        reason=explanation, needs_review=bool(reason), review_reason=reason)


def score_semantic_change(change: SemanticChange) -> ScoringResult:
    missing_source = not change.evidence or not all(
        e.document_id.strip() and e.source_refs and all(r.strip() for r in e.source_refs) and e.quote
        for e in change.evidence)
    reason = ' '.join(r for r in [change.review_reason,
        'Thay đổi thiếu bằng chứng nguồn.' if missing_source else ''] if r)
    return classify_and_score(change.change_id, [a.model_dump() for a in change.aspects], change.diff_details,
        is_meaningful_change=change.is_meaningful_change,
        needs_review=change.needs_review or missing_source, review_reason=reason)
