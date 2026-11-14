"""Opt-in join point for an injected Pipeline analysis_runner.

Context (including index preparation) runs alongside Text Diff. Semantic Diff
starts only after both finish. Does not configure/replace missing domain modules.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy

from ..schemas.contracts import AmendmentItem, TextDiffResult, SemanticDiffResult
from ..schemas.report_validation import validate_payload
from .context_builder import ContextBuild


def run_semantic_stage(item, *, context_work, text_diff, semantic_diff):
    """Callbacks are internal wiring, not a new module data contract.

    context_work(item) -> ContextBuild; text_diff(item) -> TextDiffResult;
    semantic_diff(enriched_item, text_diff_result) -> SemanticDiffResult.
    The enclosing runner owns the client and cleanup in a finally block.
    """
    with ThreadPoolExecutor(max_workers=2) as pool:
        context_future = pool.submit(context_work, deepcopy(item))
        text_future = pool.submit(text_diff, deepcopy(item))
        context = context_future.result()
        text = text_future.result()
    if not isinstance(context, ContextBuild):
        raise TypeError("context_work must return ContextBuild")
    validate_payload(AmendmentItem, context.amendment)
    if context.amendment["amendment_id"] != item["amendment_id"]:
        raise ValueError("Context amendment ID mismatch")
    validate_payload(TextDiffResult, text)
    if text["amendment_id"] != item["amendment_id"]:
        raise ValueError("Text Diff amendment ID mismatch")
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
