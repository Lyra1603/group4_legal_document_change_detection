import difflib
from typing import List, Optional
from pydantic import BaseModel

class TextChange(BaseModel):
    type: str            # INSERT | DELETE | REPLACE
    old_text: str
    new_text: str
    old_start: int
    old_end: int
    new_start: int
    new_end: int

class TextDiffResult(BaseModel):
    amendment_id: str
    changes: List[TextChange]

def compute_text_diff(amendment_id: str, before_text: Optional[str], after_text: Optional[str]) -> Optional[TextDiffResult]:
    """
    Hàm so sánh đối chiếu before_text và after_text cục bộ của một AmendmentItem.
    """
    if before_text is None or after_text is None:
        return None

    matcher = difflib.SequenceMatcher(None, before_text, after_text)
    changes: List[TextChange] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            continue

        change_type = tag.upper()
        old_sub = before_text[i1:i2]
        new_sub = after_text[j1:j2]

        changes.append(
            TextChange(
                type=change_type,
                old_text=old_sub,
                new_text=new_sub,
                old_start=i1,
                old_end=i2,
                new_start=j1,
                new_end=j2
            )
        )

    return TextDiffResult(
        amendment_id=amendment_id,
        changes=changes
    )