"""Runtime checks at module boundaries; no legal inference lives here."""
from pydantic import TypeAdapter

from backend.app.schemas.contracts import AmendmentItem, ComparisonReport

GROUPS = {'SUBJECT_OBJECT', 'RIGHTS_DUTIES_ACTIONS', 'CONDITIONS_EXCEPTIONS',
          'TIME_QUANTITY', 'PROCEDURE_AUTHORITY', 'CONSEQUENCES_SANCTIONS',
          'DEFINITIONS_REFERENCES', 'SCOPE_EFFECT_TRANSITION'}


def validate_payload(kind, value):
    TypeAdapter(kind).validate_python(value, strict=True)
    def identifiers(node):
        if isinstance(node, dict):
            for key, child in node.items():
                if key.endswith('_id') and child is not None and (not isinstance(child, str) or not child.strip()):
                    raise ValueError('Identifier must be a non-empty string')
                identifiers(child)
        elif isinstance(node, list):
            for child in node:
                identifiers(child)
    identifiers(value)


def validate_sources(value, documents):
    """Resolve every EvidenceRef against the actual Reader output."""
    if isinstance(value, list):
        for item in value:
            validate_sources(item, documents)
    elif isinstance(value, dict):
        if {'document_id', 'source_refs', 'quote'} <= value.keys():
            blocks = documents.get(value['document_id'], {}).get('blocks', [])
            lookup = {b['source_ref']: b['text'] for b in blocks}
            refs = value['source_refs']
            if not refs or any(ref not in lookup for ref in refs):
                raise ValueError('Evidence source does not exist in its document')
            if not value['quote'] or value['quote'] not in '\n'.join(lookup[r] for r in refs):
                raise ValueError('Evidence quote does not match source text')
        for item in value.values():
            validate_sources(item, documents)


def validate_amendment(item, documents, clauses):
    validate_payload(AmendmentItem, item)
    validate_sources(item, documents)
    if item['instruction']['document_id'] != 's':
        raise ValueError('Instruction must reference S')
    known = {c['unit_id'] for c in clauses['v1']}
    if any(uid not in known for uid in item['target_unit_ids']):
        raise ValueError('Target unit does not exist in V1')
    if item['needs_review'] != bool(item['review_reason']):
        raise ValueError('Review flag and reason disagree')
    if item['applicability'] == 'UNRESOLVED' and not item['needs_review']:
        raise ValueError('Unresolved target requires review')
    if item['applicability'] == 'APPLIES' and not item['target_unit_ids'] and item['operation'] != 'ADD' and not item['needs_review']:
        raise ValueError('Missing target units require review')
    for reference in item['context']['references']:
        if reference['status'] not in {'AVAILABLE', 'MISSING', 'UNRESOLVED'}:
            raise ValueError('Invalid reference status')


def validate_report(report: ComparisonReport):
    validate_payload(ComparisonReport, report)
    identities = [report['base_document'], report['amendment_document'], *report['reference_documents']]
    if (identities[0]['document_id'], identities[0]['role']) != ('v1', 'BASE') or (identities[1]['document_id'], identities[1]['role']) != ('s', 'AMENDMENT'):
        raise ValueError('Invalid primary document identities')
    ids = [d['document_id'] for d in identities]
    if len(ids) != len(set(ids)) or any(d['role'] != 'REFERENCE' for d in identities[2:]):
        raise ValueError('Invalid reference identities')
    if any('/' in d['filename'] or '\\' in d['filename'] for d in identities):
        raise ValueError('Filename must not contain a storage path')
    amendment_ids = set()
    for result in report['results']:
        item = result['amendment']
        aid = item['amendment_id']
        if aid in amendment_ids:
            raise ValueError('Duplicate amendment_id')
        amendment_ids.add(aid)
        def review_flags(value):
            if isinstance(value, dict):
                if 'needs_review' in value and value['needs_review'] != bool(value.get('review_reason')):
                    raise ValueError('Review flag and reason disagree')
                for nested in value.values():
                    review_flags(nested)
            elif isinstance(value, list):
                for nested in value:
                    review_flags(nested)
        review_flags(result)
        for key in ('text_diff', 'semantic_diff'):
            if result[key] is not None and result[key]['amendment_id'] != aid:
                raise ValueError('Module amendment_id mismatch')
        if result['text_diff'] is not None:
            before, after = item['before_text'], item['after_text']
            if before is None and item['operation'] != 'ADD' or after is None and not (item['operation'] == 'REPEAL' and item['after_basis'] == 'ABSENT'):
                raise ValueError('Cannot diff unknown content')
            before, after = before or '', after or ''
            for change in result['text_diff']['changes']:
                if change['type'] == 'INSERT' and (change['old_text'] or change['old_start'] != change['old_end']):
                    raise ValueError('INSERT must have an empty old span')
                if change['type'] == 'DELETE' and (change['new_text'] or change['new_start'] != change['new_end']):
                    raise ValueError('DELETE must have an empty new span')
                for side, text in [('old', before), ('new', after)]:
                    start, end = change[side + '_start'], change[side + '_end']
                    if not 0 <= start <= end <= len(text) or text[start:end] != change[side + '_text']:
                        raise ValueError('Text diff offset mismatch')
        semantic = result['semantic_diff']
        changes = semantic['changes'] if semantic else []
        change_ids = [c['change_id'] for c in changes]
        if len(change_ids) != len(set(change_ids)):
            raise ValueError('Duplicate change_id')
        for change in changes:
            aspect_ids = [a['aspect_id'] for a in change['aspects']]
            if len(aspect_ids) != len(set(aspect_ids)):
                raise ValueError('Duplicate aspect_id')
            for aspect in change['aspects']:
                if aspect['field_group'] not in GROUPS | {None}:
                    raise ValueError('Invalid field_group')
                if aspect['field_group'] is None and not aspect['needs_review']:
                    raise ValueError('Unknown aspect requires review')
                if aspect['needs_review'] and not change['needs_review']:
                    raise ValueError('Aspect warning must propagate to change')
                if not aspect['needs_review'] and not aspect['evidence']:
                    raise ValueError('Resolved aspect requires source evidence')
            if change['needs_review'] and not semantic['needs_review']:
                raise ValueError('Change warning must propagate to semantic result')
            if change['is_meaningful_change'] is None and not change['needs_review']:
                raise ValueError('Unknown change requires review')
            if change['is_meaningful_change'] is True and not change['aspects']:
                raise ValueError('Meaningful change requires aspects')
            if change['is_meaningful_change'] is False and change['aspects']:
                raise ValueError('Wording-only changes must not contain changed aspects')
        scoring = result['scoring']
        if scoring is not None:
            if semantic is None or sorted(s['change_id'] for s in scoring) != sorted(change_ids):
                raise ValueError('One score is required for each semantic change')
            for score in scoring:
                if score['category'] not in GROUPS | {'WORDING_ONLY', None}:
                    raise ValueError('Invalid category')
                if score['significance'] is None:
                    if score['is_critical'] is not None or not score['needs_review']:
                        raise ValueError('Unknown significance requires review and null critical flag')
                elif score['is_critical'] != (score['significance'] == 'CRITICAL'):
                    raise ValueError('Critical flag disagrees with significance')
                change = next(c for c in changes if c['change_id'] == score['change_id'])
                if change['needs_review'] and not score['needs_review']:
                    raise ValueError('Change warning must propagate to scoring')
                if change['is_meaningful_change'] is None and score['significance'] is not None:
                    raise ValueError('Cannot score an unknown change')
                if change['is_meaningful_change'] is False and (score['category'] != 'WORDING_ONLY' or score['significance'] != 'LOW'):
                    raise ValueError('Wording-only change must be LOW')
                if change['is_meaningful_change'] is True and score['category'] is not None and score['category'] not in {a['field_group'] for a in change['aspects']}:
                    raise ValueError('Category must come from aspects')
    if report['status'] == 'SUCCESS' and report['errors']:
        raise ValueError('SUCCESS cannot contain processing errors')
    if report['status'] == 'SUCCESS' and any(
        r['amendment']['applicability'] == 'UNRESOLVED' or
        (r['amendment']['applicability'] == 'APPLIES' and any(r[k] is None for k in ('text_diff', 'semantic_diff', 'scoring')))
        for r in report['results']):
        raise ValueError('SUCCESS cannot contain unfinished analysis')
