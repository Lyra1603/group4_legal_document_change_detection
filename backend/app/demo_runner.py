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
    report = {'comparison_id': comparison_id,
              'base_document': next(p.document.identity() for p in parsed if p.document.role == 'BASE'),
              'amendment_document': next(p.document.identity() for p in parsed if p.document.role == 'AMENDMENT'),
              'reference_documents': [p.document.identity() for p in parsed if p.document.role == 'REFERENCE'],
              'status': 'PARTIAL', 'results': results, 'warnings': warnings, 'errors': []}
    validate_report(report)
    return AnalysisOutcome('PARTIAL', results, warnings, [])
