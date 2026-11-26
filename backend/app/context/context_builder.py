"""Supplement AnalysisContext with source-verified quotations only."""
from copy import deepcopy
from dataclasses import dataclass
import json

from ..change_analysis.text_diff import validate_text_diff
from ..schemas.contracts import AnalysisContext, AmendmentItem, TextDiffResult
from ..schemas.report_validation import validate_payload, validate_sources
from .lightrag_client import MAX_QUERY_CHARS, LightRAGClient, RetrievalError
from .source_registry import SourceRegistry


@dataclass
class ContextBuild:
    """Internal bookkeeping, never serialized as a new shared data contract."""
    amendment: AmendmentItem
    issues: list[dict]
    retrieved: dict | None


def _failure(item, code, retrieved=None):
    result = deepcopy(item)
    result["needs_review"] = True
    reason = f"LightRAG supplemental context unverified ({code})."
    result["review_reason"] = " ".join(filter(None, [result["review_reason"], reason]))
    issue = {"stage": "context", "code": code, "message": reason,
             "amendment_id": item["amendment_id"]}
    return ContextBuild(result, [issue], retrieved)


def prepare_index(item: AmendmentItem, registry: SourceRegistry,
                  client: LightRAGClient | None) -> ContextBuild:
    """Prepare the index without querying; safe to run alongside Text Diff.

    The client deduplicates index submissions within a comparison. The runner
    owns cleanup and must report CLEANUP_PENDING if cleanup returns it.
    """
    validate_payload(AmendmentItem, item)
    validate_sources(item, registry.documents)
    if client is not None:
        try:
            client.index(list(registry.chunks.values()))
        except RetrievalError as exc:
            return _failure(item, exc.code)
    return ContextBuild(deepcopy(item), [], None)


def prepare_context(item: AmendmentItem, registry: SourceRegistry,
                    client: LightRAGClient | None, *,
                    text_diff: TextDiffResult | None = None) -> ContextBuild:
    """Sequential convenience wrapper; the parallel bridge uses prepare_index."""
    prepared = prepare_index(item, registry, client)
    if prepared.issues:
        return prepared
    return build_context(prepared.amendment, registry, client, text_diff=text_diff)


def validate_query_diff(item: AmendmentItem, text_diff: TextDiffResult) -> None:
    """Check the local handoff against the exact before/after strings.

    This does not change the shared schema/validator. In particular, a diff
    from another amendment or another pair of strings must not drive retrieval.
    """
    validate_payload(TextDiffResult, text_diff)
    if not isinstance(item['before_text'], str) or not isinstance(item['after_text'], str):
        raise ValueError('Query requires known before/after text')
    validate_text_diff(item, text_diff)


def build_retrieval_query(item: AmendmentItem, text_diff: TextDiffResult) -> str:
    """Serialize source data, including changed spans; never invent legal intent."""
    validate_query_diff(item, text_diff)
    payload = {
        'task': 'Find related source clauses, not legal conclusions',
        'amendment_id': item['amendment_id'],
        'instruction': item['instruction']['quote'],
        'instruction_source': item['instruction'],
        'target_document': item['target_document'],
        'target_locator': item['target_locator'],
        'before_text': item['before_text'],
        'after_text': item['after_text'],
        'text_diff': text_diff,
    }
    query = json.dumps(payload, ensure_ascii=False)
    if len(query) <= MAX_QUERY_CHARS:
        return query

    # Keep exact offsets and nearby words. The complete validated diff still goes
    # to Semantic; only the search request is shortened.
    def excerpt(text, start, end):
        start = max(0, start - 100)
        return text[start:min(end + 100, start + 320)]

    compact = {
        'task': payload['task'],
        'amendment_id': item['amendment_id'],
        'instruction': item['instruction']['quote'][:450],
        'target_document': (item['target_document'] or '')[:160],
        'target_locator': (item['target_locator'] or '')[:160],
        'changes': [],
        'omitted_change_count': len(text_diff['changes']),
    }
    if not text_diff['changes']:
        compact['unchanged_excerpt'] = item['before_text'][:300]
    query = json.dumps(compact, ensure_ascii=False)
    if len(query) > MAX_QUERY_CHARS:
        raise RetrievalError('QUERY_INVALID')
    for change in text_diff['changes']:
        span = {key: change[key] for key in ('type', 'old_start', 'old_end', 'new_start', 'new_end')}
        span['before_excerpt'] = excerpt(item['before_text'], change['old_start'], change['old_end'])
        span['after_excerpt'] = excerpt(item['after_text'], change['new_start'], change['new_end'])
        # A slice from the start of the edit still identifies a large replacement.
        span['removed_excerpt'] = change['old_text'][:100]
        span['added_excerpt'] = change['new_text'][:100]
        compact['changes'].append(span)
        compact['omitted_change_count'] -= 1
        candidate = json.dumps(compact, ensure_ascii=False)
        if len(candidate) > MAX_QUERY_CHARS:
            break
        query = candidate
    return query


def build_context(item: AmendmentItem, registry: SourceRegistry,
                  client: LightRAGClient | None, *,
                  text_diff: TextDiffResult | None = None) -> ContextBuild:
    validate_payload(AmendmentItem, item)
    validate_sources(item, registry.documents)
    result = deepcopy(item)
    if client is None:
        return ContextBuild(result, [], None)
    if text_diff is None:
        return _failure(item, 'TEXT_DIFF_UNAVAILABLE')
    try:
        query = build_retrieval_query(item, text_diff)
    except RetrievalError as exc:
        return _failure(item, exc.code)
    except ValueError:
        return _failure(item, 'TEXT_DIFF_INVALID')
    retrieved = None
    try:
        # Treat documents as untrusted data. The query supplies no execution/tool
        # instructions, and the adapter ignores generated descriptions/answers.
        retrieved = client.query(query)
        evidence = [registry.evidence(chunk) for chunk in retrieved["chunks"]]
        if not evidence:
            raise RetrievalError("RETRIEVAL_EMPTY_UNCONFIRMED")
        context = result["context"]
        for ref in evidence:
            if ref not in context["evidence"]:
                context["evidence"].append(ref)
        additions = []
        for raw, ref in zip(retrieved["chunks"], evidence):
            source = registry.chunks[raw["file_path"]]
            locators = ', '.join(ref['source_refs'])
            additions.append(f"[{source.document_id} / {source.role} / version={source.version} / {locators}] {ref['quote']}")
        additions = "\n".join(additions)
        context["general_context"] = "\n".join(filter(None, [context["general_context"], additions]))
        validate_payload(AnalysisContext, context)
        validate_sources(context, registry.documents)
        return ContextBuild(result, [], retrieved)
    except (RetrievalError, ValueError) as exc:
        code = exc.code if isinstance(exc, RetrievalError) else "RETRIEVAL_SOURCE_REJECTED"
        # Keep pre-existing context/reference/effect status exactly as supplied.
        # Empty retrieval never changes a ReferenceRequirement to MISSING.
        return _failure(item, code, retrieved)
