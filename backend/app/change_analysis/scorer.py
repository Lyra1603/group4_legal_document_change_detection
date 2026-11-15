"""Conservative scoring adapted from Ngọc Anh 92074d51536d; no invented severity."""
from .semantic_diff import deadline_values

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
        reason = change['review_reason']
        if change['is_meaningful_change'] is False and not aspects and not change['needs_review']:
            category, level = 'WORDING_ONLY', 'LOW'
        elif change['is_meaningful_change'] is True and aspects and not change['needs_review']:
            supported = all(a['field_group'] == 'TIME_QUANTITY' and a['old_quote'] and a['new_quote']
                            and deadline_values(a['old_quote'], a['new_quote']) == (a['old_value'], a['new_value'])
                            and all(any(q in e['quote'] for e in a['evidence']) for q in (a['old_quote'], a['new_quote']))
                            for a in aspects)
            if supported:
                level = 'HIGH'
        if level is None:
            reason = reason or 'Chưa đủ căn cứ chấm mức tác động theo rubric; cần kiểm tra.'
        scores.append({'change_id': change['change_id'], 'category': category, 'significance': level,
                       'is_critical': level == 'CRITICAL' if level else None,
                       'reason': 'Chưa chấm mức tác động khi ngữ nghĩa/ngữ cảnh chưa xác nhận.' if level is None else 'Áp dụng quy tắc pilot đã hỗ trợ, không suy mức từ số chữ thay đổi.',
                       'needs_review': bool(reason), 'review_reason': reason})
    return scores
