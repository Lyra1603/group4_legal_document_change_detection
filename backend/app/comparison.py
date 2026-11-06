"""SRS orchestration. Domain modules are supplied explicitly, never simulated."""
from dataclasses import dataclass
from copy import deepcopy
import logging
from time import monotonic
from typing import Callable

from backend.app.config import Settings
from backend.app.pipeline import read_and_parse_document
from backend.app.schemas.report_validation import validate_amendment, validate_report, validate_sources

logger = logging.getLogger(__name__)


@dataclass
class Services:
    # extract(documents, clauses) -> list[AmendmentItem]
    extract: Callable | None = None
    # context(item, documents, clauses) -> AmendmentItem
    context: Callable | None = None
    # Each analysis module receives the full item, preserving source/context.
    text_diff: Callable | None = None
    semantic_diff: Callable | None = None  # (item, text_diff) -> SemanticDiffResult
    score: Callable | None = None          # (item, semantic_diff) -> list[ScoringResult]


def run_comparison(inputs, comparison_id, settings=None, services=None):
    """inputs: [(DocumentIdentity, internal_path)], metadata never includes paths.

    Deadline is cooperative between calls; synchronous native calls cannot be
    forcibly interrupted. Service adapters must enforce their own I/O timeouts.
    """
    settings, services = settings or Settings(), services or Services()
    start = monotonic()
    report = dict(comparison_id=comparison_id, base_document=inputs[0][0],
                  amendment_document=inputs[1][0], reference_documents=[i[0] for i in inputs[2:]],
                  status='FAILED', results=[], warnings=[], errors=[])
    documents, clauses = {}, {}

    def issue(stage, code, aid=None, warning=False):
        report['warnings' if warning else 'errors'].append(dict(
            stage=stage, code=code, message=code.replace('_', ' ').lower(), amendment_id=aid))

    def call(stage, fn, *args):
        if monotonic() - start >= settings.deadline_seconds:
            raise TimeoutError('Pipeline deadline exceeded')
        tick = monotonic()
        try:
            return fn(*args)
        finally:
            logger.info('comparison=%s stage=%s duration=%.4f', comparison_id, stage, monotonic() - tick)

    def failure(stage, exc, aid=None):
        code = 'DEADLINE_EXCEEDED' if isinstance(exc, TimeoutError) else getattr(exc, 'code', 'MODULE_FAILED')
        issue(stage, code, aid)
        logger.warning('comparison=%s stage=%s code=%s', comparison_id, stage, code)

    def ingestion_stage(stage, seconds):
        logger.info('comparison=%s stage=%s duration=%.4f', comparison_id, stage, seconds)
        if monotonic() - start >= settings.deadline_seconds:
            raise TimeoutError('Pipeline deadline exceeded')

    for identity, path in inputs:
        try:
            value = call('ingestion', read_and_parse_document, path, identity['document_id'], identity['role'], ingestion_stage)
            if sum(len(b['text']) for b in value['document']['blocks']) > settings.max_characters:
                raise ValueError('Content limit exceeded')
            documents[identity['document_id']] = value['document']
            clauses[identity['document_id']] = value['clauses']
        except Exception as exc:
            failure('ingestion', exc)
    if not {'v1', 's'} <= documents.keys():
        validate_report(report)
        return report
    if services.extract is None:
        issue('extraction', 'MODULE_NOT_CONFIGURED')
        validate_report(report)
        return report
    try:
        items = call('extraction', services.extract, deepcopy(documents), deepcopy(clauses))
        if not isinstance(items, list) or len(items) > settings.max_amendments:
            raise ValueError('Invalid extraction result or amendment limit exceeded')
        for item in items:
            validate_amendment(item, documents, clauses)
        if len({i['amendment_id'] for i in items}) != len(items):
            raise ValueError('Duplicate amendment ids')
    except Exception as exc:
        failure('extraction', exc)
        validate_report(report)
        return report

    for original in items:
        item = original
        aid = item['amendment_id']
        result = dict(amendment=item, text_diff=None, semantic_diff=None, scoring=None)
        report['results'].append(result)
        if item['applicability'] == 'OTHER_DOCUMENT':
            continue
        if item['applicability'] == 'UNRESOLVED':
            issue('linking', 'UNRESOLVED_TARGET', aid, True)
            continue
        stage = 'context'
        try:
            if services.context is None:
                issue(stage, 'MODULE_NOT_CONFIGURED', aid)
                continue
            item = call(stage, services.context, deepcopy(item), deepcopy(documents), deepcopy(clauses))
            validate_amendment(item, documents, clauses)
            if item['amendment_id'] != aid:
                raise ValueError('Context changed amendment identity')
            result['amendment'] = item
            if any(r['status'] != 'AVAILABLE' for r in item['context']['references']):
                issue(stage, 'REFERENCE_UNAVAILABLE', aid, True)
            for stage, fn in [('text_diff', services.text_diff), ('semantic_diff', services.semantic_diff), ('scoring', services.score)]:
                if fn is None:
                    issue(stage, 'MODULE_NOT_CONFIGURED', aid)
                    continue
                if stage == 'text_diff':
                    if (item['before_text'] is None and item['operation'] != 'ADD') or (item['after_text'] is None and not (item['operation'] == 'REPEAL' and item['after_basis'] == 'ABSENT')):
                        issue(stage, 'UNKNOWN_CONTENT', aid, True)
                        continue
                    value = call(stage, fn, deepcopy(item))
                elif stage == 'semantic_diff':
                    value = call(stage, fn, deepcopy(item), deepcopy(result['text_diff']))
                else:
                    if result['semantic_diff'] is None:
                        issue(stage, 'SEMANTIC_RESULT_UNAVAILABLE', aid)
                        continue
                    value = call(stage, fn, deepcopy(item), deepcopy(result['semantic_diff']))
                result[stage] = value
                try:
                    if value is None:
                        raise ValueError('A configured module must return a result')
                    validate_sources(value, documents)
                    validate_report(report)
                except Exception:
                    result[stage] = None
                    raise
        except Exception as exc:
            failure(stage, exc, aid)
    if monotonic() - start >= settings.deadline_seconds:
        issue('pipeline', 'DEADLINE_EXCEEDED')
    def needs_review(value):
        if isinstance(value, dict):
            return value.get('needs_review', False) or any(needs_review(v) for v in value.values())
        if isinstance(value, list):
            return any(needs_review(v) for v in value)
        return False
    for result in report['results']:
        if needs_review(result):
            issue('analysis', 'REVIEW_REQUIRED', result['amendment']['amendment_id'], True)
    incomplete = report['errors'] or report['warnings'] or any(
        r['amendment']['applicability'] == 'APPLIES' and any(r[k] is None for k in ('text_diff', 'semantic_diff', 'scoring'))
        for r in report['results'])
    # Linked results themselves are useful, but empty extraction with errors is not.
    report['status'] = ('PARTIAL' if report['results'] else 'FAILED') if incomplete else 'SUCCESS'
    validate_report(report)
    return report
