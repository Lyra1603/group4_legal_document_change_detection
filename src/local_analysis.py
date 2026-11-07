"""Pipeline-facing adapter for PL-05/06; does not read files or resolve amendments."""
from src.text_diff.diff_engine import compute_text_diff
from src.semantic_diff.diff_engine import detect_semantic_changes
from src.classifier_scorer.scorer import score_semantic_change


def analyze_amendment(item: dict, *, context_complete: bool = False) -> dict:
    """Consume SRS AmendmentItem mapping; preserve metadata, warnings and nulls.

    Caller must explicitly confirm context completeness after resolving references.
    Unsupported ADD/REPEAL/DERIVED retain their instruction and require review.
    """
    amendment_id = item['amendment_id']
    if item.get('applicability') == 'OTHER_DOCUMENT':
        return {'amendment': item, 'text_diff': None, 'semantic_diff': None,
                'scoring': [], 'needs_review': bool(item.get('needs_review')),
                'review_reason': item.get('review_reason', '')}
    reasons = []
    if item.get('needs_review'):
        reasons.append(item.get('review_reason') or 'Yêu cầu sửa đổi cần review.')
    if item.get('applicability') != 'APPLIES' or not item.get('target_unit_ids'):
        reasons.append('Chưa xác định chắc văn bản hoặc vị trí đích.')
    if item.get('operation') != 'AMEND':
        reasons.append('Baseline tự động chỉ hỗ trợ AMEND có nội dung trước/sau.')
    context = item.get('context') or {}
    for ref in context.get('references', []):
        if ref.get('status') != 'AVAILABLE':
            reasons.append('Thiếu hoặc chưa xác định dẫn chiếu: ' + ref.get('reference_id', '?'))
    for effect in item.get('effect_info', []):
        if effect.get('needs_review'):
            reasons.append(effect.get('review_reason') or 'Hiệu lực/chuyển tiếp cần review.')
    before, after = item.get('before_text'), item.get('after_text')
    refs = list(item.get('evidence', [])) + list(context.get('evidence', []))
    if item.get('instruction'):
        refs.append(item['instruction'])
    semantic = detect_semantic_changes(amendment_id, before, after, evidence=refs,
        before_document_id=item.get('target_document'),
        after_document_id=(item.get('instruction') or {}).get('document_id'),
        context_complete=context_complete, inherited_review_reason=' '.join(reasons),
        after_basis=item.get('after_basis', 'UNRESOLVED'))
    text = compute_text_diff(amendment_id, before, after)
    scores = [score_semantic_change(change).model_dump() for change in semantic.changes]
    review_reasons = [semantic.review_reason] + [s['review_reason'] for s in scores]
    return {'amendment': item, 'text_diff': text.model_dump() if text is not None else None,
            'semantic_diff': semantic.model_dump(), 'scoring': scores,
            'needs_review': semantic.needs_review or any(s['needs_review'] for s in scores),
            'review_reason': ' '.join(dict.fromkeys(r for r in review_reasons if r))}
