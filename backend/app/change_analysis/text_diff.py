"""Adapted from Ngọc Anh's src/text_diff/diff_engine.py at 92074d51536d.

Same character-based SequenceMatcher logic; returns the shared TypedDict rather
than maintaining a second set of Pydantic contracts.
"""
from difflib import SequenceMatcher

from ..schemas.contracts import AmendmentItem, TextDiffResult


def validate_text_diff(item: AmendmentItem, result: TextDiffResult | None) -> None:
    """Check code-point offsets and reconstruct both unchanged gaps and after.

    Offsets are half-open slices of the original strings, never normalized text.
    A missing side permits only None; an empty string is a known, valid side.
    """
    before, after = item['before_text'], item['after_text']
    if before is None or after is None:
        if result is not None:
            raise ValueError('Cannot diff unknown content')
        return
    if result is None or result['amendment_id'] != item['amendment_id']:
        raise ValueError('Missing Text Diff or amendment ID mismatch')
    old_cursor = new_cursor = 0
    pieces = []
    for change in result['changes']:
        i, j, a, b = (change[k] for k in ('old_start', 'old_end', 'new_start', 'new_end'))
        if any(type(v) is not int for v in (i, j, a, b)):
            raise ValueError('Text Diff offsets must be integers')
        if not (old_cursor <= i <= j <= len(before) and new_cursor <= a <= b <= len(after)):
            raise ValueError('Text Diff offsets overlap or are out of bounds')
        if before[i:j] != change['old_text'] or after[a:b] != change['new_text']:
            raise ValueError('Text Diff spans do not match input')
        expected = 'INSERT' if i == j else 'DELETE' if a == b else 'REPLACE'
        if (i == j and a == b) or change['type'] != expected or before[i:j] == after[a:b]:
            raise ValueError('Invalid Text Diff operation')
        if before[old_cursor:i] != after[new_cursor:a]:
            raise ValueError('Text Diff omits a changed gap')
        pieces.extend((before[old_cursor:i], change['new_text']))
        old_cursor, new_cursor = j, b
    pieces.append(before[old_cursor:])
    if before[old_cursor:] != after[new_cursor:] or ''.join(pieces) != after:
        raise ValueError('Text Diff does not reconstruct after_text')


def compute_text_diff(item: AmendmentItem) -> TextDiffResult | None:
    before, after = item['before_text'], item['after_text']
    if before is None or after is None:
        return None
    if before == after:
        return {'amendment_id': item['amendment_id'], 'changes': []}
    changes = []
    for tag, i, j, a, b in SequenceMatcher(None, before, after, autojunk=False).get_opcodes():
        if tag != 'equal':
            changes.append({'type': tag.upper(), 'old_text': before[i:j], 'new_text': after[a:b],
                            'old_start': i, 'old_end': j, 'new_start': a, 'new_end': b})
    return {'amendment_id': item['amendment_id'], 'changes': changes}
