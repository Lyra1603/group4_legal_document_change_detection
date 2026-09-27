from typing import Optional, TypedDict

class Clause(TypedDict):
    id: str
    title: str
    content: str

class SemanticDiffResult(TypedDict):
    is_meaningful_change: bool
    diff_details: str

class ScoringResult(TypedDict):
    category: str
    significance: str
    is_critical: bool

class AlignedPair(TypedDict):
    pair_key: str
    v1: Optional[Clause]
    v2: Optional[Clause]
    align_type: str
    similarity_score: float
    semantic_diff: Optional[SemanticDiffResult]
    scoring: Optional[ScoringResult]