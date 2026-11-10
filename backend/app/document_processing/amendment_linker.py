"""Narrow, source-bound demo Linker. Unsupported instructions remain visible.

Supports one literal phrase replacement at one explicit locator, or a quoted
whole point/clause/article replacement. Does not infer legal effect or identity
from a matching article number alone when S names another document.
"""
import re

from ..schemas.report_validation import validate_amendment

NUMBER = re.compile(r'(?:^|[\n\t])\s*Số\s*:?\s*(\d+/\d{4}/[^\s;,]+)', re.I)
DOC_CODE = re.compile(r'\b\d+/\d{4}/[\wĐđ-]+', re.I)
LOCATOR = re.compile(r'\bĐiều\s+(\d+[a-zđ]?)\b', re.I)
CLAUSE = re.compile(r'\bkhoản\s+(\d+[a-zđ]?)\b', re.I)
POINT = re.compile(r'\bđiểm\s+([a-zđ])\b', re.I)
ACTION = re.compile(r'^(?:Sửa đổi|Bổ sung|Bãi bỏ|Thay thế|Đánh lại số|Chuyển|Tách|Hợp nhất|Thay\s+(?:cụm\s+)?từ)\b|^(?:Điểm|Khoản|Điều)\s+.+?\bđược\s+(?:sửa đổi|thay thế|bãi bỏ)', re.I)
PHRASE = re.compile(r'Thay\s+(?:cụm\s+)?từ\s+[“"](?P<old>[^”"]+)[”"]\s+bằng\s+(?:cụm\s+từ\s+|từ\s+)?[“"](?P<new>[^”"]+)[”"]\s+tại\s+(?P<locator>.+?)\.?$', re.I)


def issue(code, message, aid=None):
    return {'stage': 'linker', 'code': code, 'message': message, 'amendment_id': aid}


def _body(text):
    text = re.sub(r'^\s*Điều\s+\d+[a-zđ]?\s*[.:]\s*', '', text, flags=re.I)
    return re.sub(r'^\s*\d+\s*\.\s*', '', text).strip()


def _quoted(blocks, index):
    selected = []
    for position in range(index + 1, min(index + 81, len(blocks))):
        text = blocks[position]['text']
        if not text.strip():
            if selected:
                selected.append(blocks[position])
            continue
        if not selected and not text.lstrip().startswith(('“', '"')):
            return None
        selected.append(blocks[position])
        joined = '\n'.join(b['text'] for b in selected)
        if len(joined) > 30000:
            return None
        opening = joined.lstrip()[0]
        balanced = joined.count('“') == joined.count('”') if opening == '“' else joined.count('"') % 2 == 0
        closing = re.search(r'[”"]\s*[.;]?\s*$', joined)
        if balanced and closing:
            start = joined.index(opening) + 1
            return joined[start:closing.start()], [b['source_ref'] for b in selected], position
    return None


def link_amendments(boundary):
    documents, units = boundary.documents, boundary.units
    blocks = documents['s']['blocks']
    base_header = '\n'.join(b['text'] for b in documents['v1']['blocks'][:8])
    match = NUMBER.search(base_header)
    base_number = match.group(1).casefold() if match else None
    items, warnings = [], []
    scope = ''
    consumed = -1
    for index, block in enumerate(blocks):
        raw, text = block['text'], _body(block['text'])
        if index <= consumed:
            continue
        if re.match(r'^\s*Điều\s+\d+[a-zđ]?\s*[.:]', raw, re.I):
            scope = text
        if not ACTION.search(text):
            continue
        # A generic amendment article heading scopes concrete child directives.
        if text.casefold() in {'sửa đổi', 'sửa đổi, bổ sung'}:
            continue
        if re.search(r'một số điều', text, re.I) and not LOCATOR.search(text):
            continue
        aid = f"s:amendment_{len(items)+1}"
        instruction = {'document_id': 's', 'source_refs': [block['source_ref']], 'quote': raw}
        item = {'amendment_id': aid, 'operation': 'UNRESOLVED', 'instruction': instruction,
                'target_document': 'v1', 'target_locator': text, 'target_unit_ids': [],
                'applicability': 'UNRESOLVED', 'before_text': None, 'after_text': None,
                'after_basis': 'UNRESOLVED', 'evidence': [instruction], 'effect_info': [],
                'context': {'general_context': '', 'evidence': [], 'references': []},
                'needs_review': True, 'review_reason': 'Chưa xác minh đầy đủ ngữ cảnh và hiệu lực pháp lý.'}
        quote = None if PHRASE.search(text) else _quoted(blocks, index)
        if quote:
            consumed = quote[2]
        locators = LOCATOR.findall(text)
        clauses, points = CLAUSE.findall(text), POINT.findall(text)
        codes = DOC_CODE.findall(text) or DOC_CODE.findall(scope)
        reason = None
        if codes and (base_number is None or codes[0].casefold() != base_number):
            item['target_document'] = codes[0]
            item['applicability'] = 'OTHER_DOCUMENT'
            reason = ('TARGET_OTHER_DOCUMENT', 'Chỉ dẫn nhắm văn bản khác hoặc chưa đối chiếu được định danh với V1 đã chọn.')
        elif len(locators) != 1 or len(clauses) > 1 or len(points) > 1 or (points and not clauses):
            reason = ('UNSUPPORTED_LOCATOR', 'Demo cần đúng một Điều, tùy chọn một khoản và một điểm; chưa hỗ trợ nhiều đích.')
        else:
            key = (locators[0].casefold(), clauses[0].casefold() if clauses else None, points[0].casefold() if points else None)
            targets = units['v1'].get(key, [])
            if len(targets) != 1:
                reason = ('TARGET_NOT_UNIQUE', 'Không tìm thấy duy nhất vị trí đích trong V1; không tự đoán theo tên gần giống.')
            else:
                target = targets[0]
                item.update(applicability='APPLIES', target_locator=target['id'], target_unit_ids=[target['unit_id']])
                if re.search(r'^(?:Bổ sung|Bãi bỏ)\b|được bãi bỏ', text, re.I):
                    item['operation'] = 'ADD' if re.match('Bổ sung', text, re.I) else 'REPEAL'
                    reason = ('UNSUPPORTED_OPERATION', 'Demo chưa triển khai bổ sung/bãi bỏ; giữ nguyên chỉ dẫn để kiểm tra.')
                else:
                    item['operation'] = 'AMEND'
                    phrase = PHRASE.search(text)
                    if phrase and target['content'].count(phrase['old']) == 1:
                        item.update(before_text=target['content'], after_text=target['content'].replace(phrase['old'], phrase['new'], 1), after_basis='DERIVED')
                    elif phrase:
                        reason = ('PHRASE_NOT_UNIQUE', 'Cụm từ cũ không xuất hiện đúng một lần ở đích; chưa áp dụng sửa đổi.')
                    elif quote:
                        value, refs, _ = quote
                        prefix = rf'^{re.escape(points[0])}\)' if points else rf'^{re.escape(clauses[0])}\.' if clauses else rf'^Điều\s+{re.escape(locators[0])}\s*[.:]'
                        if not re.search(prefix, value.strip(), re.I):
                            reason = ('QUOTED_TARGET_MISMATCH', 'Nhãn của nội dung trích dẫn không khớp đơn vị đích; chưa hỗ trợ đánh lại số.')
                        else:
                            item.update(before_text=target['content'], after_text=value, after_basis='QUOTED')
                            item['evidence'].append({'document_id': 's', 'source_refs': refs, 'quote': value})
                    else:
                        reason = ('UNSUPPORTED_INSTRUCTION', 'Chưa nhận được một lệnh thay cụm từ hoặc đoạn thay thế trích nguyên văn đóng/mở đầy đủ.')
                    if item['before_text'] is not None:
                        item['evidence'].append({'document_id': 'v1', 'source_refs': target['source_refs'], 'quote': target['content']})
        if reason:
            item['review_reason'] = reason[1]
            warnings.append(issue(*reason, aid))
        else:
            warnings.append(issue('CONTEXT_NOT_CONFIRMED', item['review_reason'], aid))
        validate_amendment(item, documents, boundary.clauses)
        items.append(item)
    if not items:
        warnings.append(issue('INSTRUCTIONS_NOT_RECOGNIZED', 'Chưa nhận diện được chỉ dẫn thuộc mẫu hỗ trợ; không được kết luận văn bản không có thay đổi.'))
    return items, warnings
