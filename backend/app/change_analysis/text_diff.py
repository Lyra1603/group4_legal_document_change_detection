"""Adapted from Ngọc Anh's src/text_diff/diff_engine.py at 92074d51536d.

Same character-based SequenceMatcher logic; returns the shared TypedDict rather
than maintaining a second set of Pydantic contracts.
"""
from difflib import SequenceMatcher


def compute_text_diff(item):
    before, after = item['before_text'], item['after_text']
    if before is None or after is None:
        return None
    changes = []
    for tag, i, j, a, b in SequenceMatcher(None, before, after, autojunk=False).get_opcodes():
        if tag != 'equal':
            changes.append({'type': tag.upper(), 'old_text': before[i:j], 'new_text': after[a:b],
                            'old_start': i, 'old_end': j, 'new_start': a, 'new_end': b})
    return {'amendment_id': item['amendment_id'], 'changes': changes}
