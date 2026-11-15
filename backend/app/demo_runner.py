"""Executable local demo runner. No fixture answers, mock model or implicit RAG.

The model decision is deferred. Semantic/scoring remain conservative null/review;
LightRAG is off, explicitly reported, rather than simulated as successful.
"""
import os
from .pipeline import AnalysisOutcome, check_deadline, issue
from .document_processing.document_adapter import adapt_documents
from .document_processing.amendment_linker import link_amendments
from .change_analysis.text_diff import compute_text_diff
from .change_analysis.semantic_diff import detect_semantic_changes
from .change_analysis.scorer import score_changes
from .context.context_builder import build_context
from .context.chunk_builder import build_chunks
from .context.source_registry import SourceRegistry
from .context.semantic_bridge import run_semantic_stage
from .schemas.report_validation import validate_amendment, validate_report, validate_sources


def _needs_review(value):
    if isinstance(value, dict):
        return value.get('needs_review') is True or any(_needs_review(v) for v in value.values())
    if isinstance(value, list):
        return any(_needs_review(v) for v in value)
    return False


def classify_demo_results(results):
    """Text comparison is usable even when semantics need review or changes=[].

    This demo supports AMEND before/after pairs. A skipped/unresolved item alone
    is not a usable analysis; informational warnings alone do not force PARTIAL.
    """
    usable = [r for r in results if r['amendment']['applicability'] == 'APPLIES'
              and r['amendment']['operation'] == 'AMEND'
              and r['amendment']['before_text'] is not None
              and r['amendment']['after_text'] is not None
              and r['text_diff'] is not None]
    if not usable:
        return 'FAILED'
    if (len(usable) != len(results) or _needs_review(results)
            or any(r['semantic_diff'] is None or r['scoring'] is None for r in usable)):
        return 'PARTIAL'
    return 'SUCCESS'


def run_demo_analysis(parsed, comparison_id, deadline):
    boundary = adapt_documents(parsed)
    check_deadline(deadline)
    items, warnings = link_amendments(boundary)
    warnings.append(issue('context', 'LIGHTRAG_DISABLED', 'LightRAG chưa bật vì chưa chốt dịch vụ/model; đang dùng nguồn cục bộ, không giả lập retrieval.'))
    warnings.append(issue('semantic', 'LOCAL_BASELINE_ONLY', 'Demo quy tắc cục bộ; model chưa chọn, không tự xác nhận ngữ cảnh hoặc mức tác động.'))
    if any(p.document.role == 'REFERENCE' for p in parsed):
        warnings.append(issue('context', 'REFERENCES_NOT_ANALYZED', 'Đã đọc tài liệu tham chiếu nhưng chưa truy xuất/đối chiếu đầy đủ; không tự xác nhận đủ ngữ cảnh.'))
    # Version labels here mean uploaded content identity only, not legal effect.
    versions = {d: 'uploaded-source' for d in boundary.documents}
    chunks = build_chunks(comparison_id, list(boundary.documents.values()), versions,
                          max_chunks=5000, max_chars=100000)
    registry = SourceRegistry(chunks, list(boundary.documents.values()))
    results = []
    max_chars = int(os.getenv('POCS_DEMO_MAX_UNIT_CHARS', '12000'))
    if max_chars < 1:
        raise ValueError('POCS_DEMO_MAX_UNIT_CHARS must be positive')
    for item in items:
        check_deadline(deadline)
        if item['applicability'] != 'APPLIES' or item['before_text'] is None or item['after_text'] is None:
            results.append({'amendment': item, 'text_diff': None, 'semantic_diff': None, 'scoring': None})
            continue
        if max(len(item['before_text']), len(item['after_text'])) > max_chars:
            warnings.append({'stage': 'text_diff', 'code': 'DEMO_UNIT_TOO_LONG',
                             'message': 'Đơn vị sửa đổi vượt giới hạn độ dài của demo; chưa tính diff để tránh xử lý kéo dài.',
                             'amendment_id': item['amendment_id']})
            results.append({'amendment': item, 'text_diff': None, 'semantic_diff': None, 'scoring': None})
            continue
        context, text, semantic = run_semantic_stage(item,
            context_work=lambda value: build_context(value, registry, None),
            text_diff=compute_text_diff, semantic_diff=detect_semantic_changes)
        validate_amendment(context.amendment, boundary.documents, boundary.clauses)
        score = score_changes(semantic)
        result = {'amendment': context.amendment, 'text_diff': text, 'semantic_diff': semantic, 'scoring': score}
        validate_sources(result, boundary.documents)
        warnings.extend(context.issues)
        results.append(result)
    status = classify_demo_results(results)
    if status == 'FAILED':
        warnings.append(issue('analysis', 'NO_USABLE_ANALYSIS',
                              'Đã xử lý đầu vào nhưng chưa tạo được mục phân tích dùng được; xem chỉ dẫn và lý do đi kèm. Không kết luận không có thay đổi.'))
    report = {'comparison_id': comparison_id,
              'base_document': next(p.document.identity() for p in parsed if p.document.role == 'BASE'),
              'amendment_document': next(p.document.identity() for p in parsed if p.document.role == 'AMENDMENT'),
              'reference_documents': [p.document.identity() for p in parsed if p.document.role == 'REFERENCE'],
              'status': status, 'results': results, 'warnings': warnings, 'errors': []}
    validate_report(report)
    return AnalysisOutcome(status, results, warnings, [])
