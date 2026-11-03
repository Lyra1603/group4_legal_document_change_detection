from typing import Optional, TypedDict

class SourceBlock(TypedDict):
    source_ref: str
    text: str


class ExtractedDocument(TypedDict):
    document_id: str
    role: str
    filename: str
    file_type: str
    blocks: list[SourceBlock]

class Clause(TypedDict):
    unit_id: str # định danh Điều trong tài liệu nào, ví dụ "v1:article_2" thuộc điều 2 của V1
    id: str
    title: str
    content: str
    source_refs: list[str] # danh sách vị trí nguồn, vì một Điều có thể trải qua nhiều đoạn hoặc trang

class EvidenceRef(TypedDict):
    document_id: str
    source_refs: list[str]
    quote: str


class ReferenceRequirement(TypedDict):
    reference_id: str
    document_label: str
    target_locator: str
    purpose: str
    status: str
    evidence: list[EvidenceRef]
    reason: str


class EffectInfo(TypedDict):
    text: str
    applies_to: str
    evidence: list[EvidenceRef]
    needs_review: bool
    review_reason: str


class AnalysisContext(TypedDict):
    general_context: str
    evidence: list[EvidenceRef]
    references: list[ReferenceRequirement]


class AmendmentItem(TypedDict):
    amendment_id: str
    operation: str
    instruction: EvidenceRef
    target_document: str
    target_locator: str
    target_unit_ids: list[str]
    applicability: str
    before_text: Optional[str]
    after_text: Optional[str]
    after_basis: str
    evidence: list[EvidenceRef]
    effect_info: list[EffectInfo]
    context: AnalysisContext
    needs_review: bool
    review_reason: str

class ChangeAspect(TypedDict):
    aspect_id: str
    field_group: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    interpretation: str
    evidence: list[EvidenceRef]
    old_quote: Optional[str]
    new_quote: Optional[str]
    needs_review: bool
    review_reason: str


class SemanticChange(TypedDict):
    change_id: str
    is_meaningful_change: Optional[bool]
    diff_details: str
    aspects: list[ChangeAspect]
    evidence: list[EvidenceRef]
    old_quote: Optional[str]
    new_quote: Optional[str]
    needs_review: bool
    review_reason: str

class SemanticDiffResult(TypedDict):
    amendment_id: str
    changes: list[SemanticChange]
    needs_review: bool
    review_reason: str

class ScoringResult(TypedDict):
    category: str
    significance: str
    is_critical: bool

class BaselineSemanticDiffResult(TypedDict):
    is_meaningful_change: bool
    diff_details: str

class AlignedPair(TypedDict):
    pair_key: str
    v1: Optional[Clause]
    v2: Optional[Clause]
    align_type: str
    similarity_score: float
    semantic_diff: Optional[BaselineSemanticDiffResult]
    scoring: Optional[ScoringResult]