"""Opt-in join point for an injected Pipeline analysis_runner.

Index preparation runs alongside Text Diff. Query/source verification waits for
both; Semantic Diff receives the enriched amendment and the same Text Diff.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy

from ..schemas.contracts import AmendmentItem, SemanticDiffResult
from ..schemas.report_validation import validate_payload
from .context_builder import ContextBuild, validate_query_diff


def run_semantic_stage(item, *, context_prepare, context_work, text_diff, semantic_diff):
    """Callbacks are internal wiring, not a new module data contract.

    context_prepare(item) -> ContextBuild (index only);
    context_work(prepared_item, text_diff_result) -> ContextBuild (query);
    text_diff(item) -> TextDiffResult;
    semantic_diff(enriched_item, text_diff_result) -> SemanticDiffResult.
    The enclosing runner owns the client and cleanup in a finally block.
    """
    with ThreadPoolExecutor(max_workers=2) as pool:
        context_future = pool.submit(context_prepare, deepcopy(item))
        text_future = pool.submit(text_diff, deepcopy(item))
        context = context_future.result()
        text = text_future.result()
    if not isinstance(context, ContextBuild):
        raise TypeError("context_prepare must return ContextBuild")
    validate_payload(AmendmentItem, context.amendment)
    if context.amendment["amendment_id"] != item["amendment_id"]:
        raise ValueError("Context amendment ID mismatch")
    validate_query_diff(item, text)
    if not context.issues:
        context = context_work(deepcopy(context.amendment), deepcopy(text))
        if not isinstance(context, ContextBuild):
            raise TypeError("context_work must return ContextBuild")
        validate_payload(AmendmentItem, context.amendment)
        if context.amendment["amendment_id"] != item["amendment_id"]:
            raise ValueError("Context amendment ID mismatch")
    validate_query_diff(context.amendment, text)
    semantic = semantic_diff(context.amendment, text)
    validate_payload(SemanticDiffResult, semantic)
    if semantic["amendment_id"] != item["amendment_id"]:
        raise ValueError("Semantic Diff amendment ID mismatch")
    # Preserve degradation for downstream Scorer/report review propagation.
    if context.issues:
        semantic = deepcopy(semantic)
        semantic["needs_review"] = True
        semantic["review_reason"] = " ".join(filter(None, [semantic["review_reason"],
                                                            context.amendment["review_reason"]]))
    return context, text, semantic
