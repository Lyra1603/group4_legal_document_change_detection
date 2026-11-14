"""Conservative rules adapted from Ngọc Anh's baseline at 92074d51536d.

No provider is selected. Completeness is NOT inferred from retrieval success.
Unconfirmed context, DERIVED or unsupported text keep null semantics + review.
"""
import re
import unicodedata
from copy import deepcopy


_DEADLINE = re.compile(r'trong thời hạn (?P<value>[1-9]\d*) ngày')


def deadline_values(old, new):
    a, b = list(_DEADLINE.finditer(old)), list(_DEADLINE.finditer(new))
    if len(a) != 1 or len(b) != 1:
        return None
    x, y = a[0], b[0]
    if old[:x.start('value')] + '<N>' + old[x.end('value'):] != new[:y.start('value')] + '<N>' + new[y.end('value'):]:
        return None
    if x['value'] == y['value']:
        return None
    return x['value'] + ' ngày', y['value'] + ' ngày'


def detect_semantic_changes(item, text_diff, *, context_complete=False):
    before, after = item['before_text'], item['after_text']
    refs = deepcopy(item['evidence'] + item['context']['evidence'])
    if item['instruction'] not in refs:
        refs.append(deepcopy(item['instruction']))
    def quoted(text, document):
        return text if text and any(e['document_id'] == document and text in e['quote'] for e in refs) else None
    old_quote = quoted(before, item['target_document'])
    new_quote = quoted(after, 's') if item['after_basis'] == 'QUOTED' else None
    reasons = [item['review_reason']] if item['needs_review'] else []
    if not context_complete:
        reasons.append('Chưa xác nhận đủ ngữ cảnh, dẫn chiếu và hiệu lực; model chưa được lựa chọn.')
    if item['after_basis'] != 'QUOTED':
        reasons.append('Nội dung sau là DERIVED/chưa xác định; baseline chưa tự kết luận ngữ nghĩa.')
    if not before or not after or old_quote is None or new_quote is None:
        reasons.append('Chưa có nguyên văn hai phía đủ căn cứ cho baseline.')
    aspects, meaningful = [], None
    details = 'Đã tính thay đổi chữ; chưa đủ căn cứ kết luận tác động ngữ nghĩa.'
    if not reasons:
        old, new = (unicodedata.normalize('NFC', t).strip() for t in (before, after))
        if old == new:
            return {'amendment_id': item['amendment_id'], 'changes': [], 'needs_review': False, 'review_reason': ''}
        if old.replace('chậm nhất vào ngày', 'không muộn hơn ngày') == new.replace('chậm nhất vào ngày', 'không muộn hơn ngày'):
            meaningful, details = False, 'Đổi cách diễn đạt thời hạn tương đương; phần còn lại giữ nguyên.'
        else:
            values = deadline_values(old, new)
            if values:
                meaningful = True
                details = f'Thay thời hạn {values[0]} thành {values[1]}; phần còn lại giữ nguyên.'
                aspects = [{'aspect_id': item['amendment_id'] + ':aspect_1', 'field_group': 'TIME_QUANTITY',
                            'old_value': values[0], 'new_value': values[1], 'interpretation': details,
                            'evidence': refs, 'old_quote': old_quote, 'new_quote': new_quote,
                            'needs_review': False, 'review_reason': ''}]
    if meaningful is None:
        reasons.append('Chưa xác định thay đổi nghĩa bằng quy tắc đã hỗ trợ; không coi là không đổi nghĩa.')
    reason = ' '.join(dict.fromkeys(reasons))
    change = {'change_id': item['amendment_id'] + ':change_1', 'is_meaningful_change': meaningful,
              'diff_details': details, 'aspects': aspects, 'evidence': refs,
              'old_quote': old_quote, 'new_quote': new_quote,
              'needs_review': bool(reason), 'review_reason': reason}
    return {'amendment_id': item['amendment_id'], 'changes': [change],
            'needs_review': bool(reason), 'review_reason': reason}
