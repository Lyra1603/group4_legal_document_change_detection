"""Conservative rules adapted from Ngọc Anh's baseline at 92074d51536d.

No provider is selected. Completeness is NOT inferred from retrieval success.
Unconfirmed context, DERIVED or unsupported text keep null semantics + review.
"""
import re
import unicodedata
from copy import deepcopy

from .text_diff import validate_text_diff


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
        return text if text and document and any(
            e['document_id'] == document and e['source_refs']
            and all(r.strip() for r in e['source_refs']) and text in e['quote']
            for e in refs) else None
    old_quote = quoted(before, item['target_document'])
    new_quote = quoted(after, item['instruction']['document_id']) if item['after_basis'] == 'QUOTED' else None
    reasons = ([item['review_reason'] or 'Mục sửa đổi cần kiểm tra.']
               if item['needs_review'] or item['review_reason'] else [])
    if item['applicability'] != 'APPLIES' or not item['target_unit_ids']:
        reasons.append('Chưa xác định chắc văn bản hoặc vị trí đích.')
    if item['operation'] != 'AMEND':
        reasons.append('Baseline chỉ hỗ trợ AMEND có nội dung trước/sau.')
    for ref in item['context']['references']:
        if ref['status'] != 'AVAILABLE' or not ref['evidence']:
            reasons.append('Dẫn chiếu chưa đủ căn cứ: ' + ref['reference_id'])
    for effect in item['effect_info']:
        if effect['needs_review'] or effect['review_reason']:
            reasons.append(effect['review_reason'] or 'Hiệu lực/chuyển tiếp cần kiểm tra.')
    diff_valid = False
    try:
        validate_text_diff(item, text_diff)
        diff_valid = text_diff is not None
    except (ValueError, KeyError, TypeError):
        reasons.append('Text Diff thiếu hoặc không khớp ID, nội dung và offset của mục sửa đổi.')
    if not context_complete:
        reasons.append('Chưa xác nhận đủ ngữ cảnh, dẫn chiếu và hiệu lực; model chưa được lựa chọn.')
    if item['after_basis'] != 'QUOTED':
        reasons.append('Nội dung sau là DERIVED/chưa xác định; baseline chưa tự kết luận ngữ nghĩa.')
    if not before or not after or old_quote is None or new_quote is None:
        reasons.append('Chưa có nguyên văn hai phía đủ căn cứ cho baseline.')
    aspects, meaningful = [], None
    details = ('Đã kiểm tra Text Diff; chưa đủ căn cứ kết luận tác động ngữ nghĩa.' if diff_valid
               else 'Chưa có Text Diff hợp lệ cho cặp nội dung trước/sau.')
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
