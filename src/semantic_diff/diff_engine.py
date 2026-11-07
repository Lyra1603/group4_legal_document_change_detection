"""Conservative local baseline: unknown semantics remain null with review."""
import re
import unicodedata
from typing import Optional
from src.analysis_contracts import ChangeAspect, EvidenceRef, SemanticChange, SemanticDiffResult

_DEADLINE = re.compile(r'trong thời hạn (?P<value>[1-9]\d*) ngày')


def deadline_values(old: str, new: str):
    """Only one integer deadline may differ; all other characters must match."""
    a, b = list(_DEADLINE.finditer(old)), list(_DEADLINE.finditer(new))
    if len(a) != 1 or len(b) != 1:
        return None
    x, y = a[0], b[0]
    left = old[:x.start('value')] + '<N>' + old[x.end('value'):]
    right = new[:y.start('value')] + '<N>' + new[y.end('value'):]
    if left != right or x['value'] == y['value']:
        return None
    return x['value'] + ' ngày', y['value'] + ' ngày'


def detect_semantic_changes(
    amendment_id: str, before_text: Optional[str], after_text: Optional[str], *,
    evidence: Optional[list[EvidenceRef | dict]] = None,
    before_document_id: Optional[str] = None, after_document_id: Optional[str] = None,
    context_complete: bool = False, inherited_review_reason: str = '',
    after_basis: str = 'QUOTED',
) -> SemanticDiffResult:
    """Requires caller-supplied evidence/context; never invent document locations.

    Equal local text is not proof that the amendment document has no instructions.
    Derived content, additions/repeals and other semantics need review in this baseline.
    """
    refs = [EvidenceRef.model_validate(e) for e in (evidence or [])]
    reasons = [inherited_review_reason] if inherited_review_reason else []
    if not before_text or not after_text:
        reasons.append('Thiếu nội dung cục bộ; cần phân biệt bổ sung/bãi bỏ với chưa xác định.')
    if not context_complete:
        reasons.append('Ngữ cảnh chưa được xác nhận đầy đủ.')
    if after_basis != 'QUOTED':
        reasons.append('Baseline chưa hỗ trợ kết luận cho nội dung sau suy ra hoặc chưa xác định.')

    def sourced(text, doc):
        return bool(text and doc and any(e.document_id == doc and e.source_refs
                    and all(r.strip() for r in e.source_refs) and e.quote and text in e.quote for e in refs))

    before_ok = sourced(before_text, before_document_id)
    after_ok = after_basis == 'QUOTED' and sourced(after_text, after_document_id)
    if not before_ok or not after_ok:
        reasons.append('Chưa có bằng chứng và vị trí nguồn đầy đủ cho hai phía.')
    old_quote = before_text if before_ok else None
    new_quote = after_text if after_ok else None
    aspects, meaningful = [], None
    details = 'Chưa đủ căn cứ hoặc ngoài phạm vi baseline; cần review ngữ nghĩa.'
    if not reasons:
        old = unicodedata.normalize('NFC', before_text).strip()
        new = unicodedata.normalize('NFC', after_text).strip()
        if old == new:
            return SemanticDiffResult(amendment_id=amendment_id, changes=[])
        if old.replace('chậm nhất vào ngày', 'không muộn hơn ngày') == new.replace('chậm nhất vào ngày', 'không muộn hơn ngày'):
            meaningful = False
            details = 'Đổi cách diễn đạt thời hạn tương đương; phần còn lại giữ nguyên.'
        else:
            values = deadline_values(old, new)
            if values:
                meaningful = True
                details = f'Đổi thời hạn từ {values[0]} thành {values[1]}; phần còn lại giữ nguyên.'
                aspects = [ChangeAspect(aspect_id=f'{amendment_id}:aspect_1', field_group='TIME_QUANTITY',
                    old_value=values[0], new_value=values[1], interpretation=details,
                    evidence=refs, old_quote=old_quote, new_quote=new_quote)]
    if meaningful is None:
        reasons.append('Chưa xác định đổi nghĩa bằng quy tắc đã hỗ trợ.')
    reason = ' '.join(dict.fromkeys(reasons))
    change = SemanticChange(change_id=f'{amendment_id}:change_1', is_meaningful_change=meaningful,
        diff_details=details, aspects=aspects, evidence=refs, old_quote=old_quote, new_quote=new_quote,
        needs_review=bool(reason), review_reason=reason)
    return SemanticDiffResult(amendment_id=amendment_id, changes=[change],
                              needs_review=bool(reason), review_reason=reason)
