"""Classify semantic aspects and apply the agreed wording-only severity."""

PRIORITY = ('CONSEQUENCES_SANCTIONS', 'RIGHTS_DUTIES_ACTIONS', 'SUBJECT_OBJECT',
            'CONDITIONS_EXCEPTIONS', 'PROCEDURE_AUTHORITY', 'TIME_QUANTITY',
            'SCOPE_EFFECT_TRANSITION', 'DEFINITIONS_REFERENCES')


def score_changes(semantic):
    scores = []
    for change in semantic['changes']:
        aspects = change['aspects']
        groups = {a['field_group'] for a in aspects}
        category = next((g for g in PRIORITY if g in groups), None)
        level = None
        warnings = [entry['review_reason'] or 'Nhận định ngữ nghĩa cần kiểm tra.'
                    for entry in (change, *aspects) if entry['needs_review']]
        if change['is_meaningful_change'] is False and not aspects and not warnings:
            category, level = 'WORDING_ONLY', 'LOW'
            reason = 'Chỉ đổi cách diễn đạt, giữ nguyên nghĩa.'
        else:
            reason = (f'Nhóm chính {category} lấy từ khía cạnh đã xác định. ' if category else '')
            reason += 'Chưa đủ căn cứ chấm mức tác động theo rubric.'
            warnings.append(reason)
        scores.append({'change_id': change['change_id'], 'category': category, 'significance': level,
                       'is_critical': False if level == 'LOW' else None, 'reason': reason,
                       'needs_review': bool(warnings), 'review_reason': ' '.join(dict.fromkeys(warnings))})
    return scores
