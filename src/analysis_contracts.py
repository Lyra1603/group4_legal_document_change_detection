"""Shared contracts for local analysis modules, matching SRS 1.3."""
from typing import Literal, Optional
from pydantic import BaseModel

FieldGroup = Literal['SUBJECT_OBJECT', 'RIGHTS_DUTIES_ACTIONS', 'CONDITIONS_EXCEPTIONS',
                     'TIME_QUANTITY', 'PROCEDURE_AUTHORITY', 'CONSEQUENCES_SANCTIONS',
                     'DEFINITIONS_REFERENCES', 'SCOPE_EFFECT_TRANSITION']


class EvidenceRef(BaseModel):
    document_id: str
    source_refs: list[str]
    quote: str


class ChangeAspect(BaseModel):
    aspect_id: str
    field_group: Optional[FieldGroup] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    interpretation: str
    evidence: list[EvidenceRef]
    old_quote: Optional[str] = None
    new_quote: Optional[str] = None
    needs_review: bool = False
    review_reason: str = ''


class SemanticChange(BaseModel):
    change_id: str
    is_meaningful_change: Optional[bool] = None
    diff_details: str
    aspects: list[ChangeAspect]
    evidence: list[EvidenceRef]
    old_quote: Optional[str] = None
    new_quote: Optional[str] = None
    needs_review: bool = False
    review_reason: str = ''


class SemanticDiffResult(BaseModel):
    amendment_id: str
    changes: list[SemanticChange]
    needs_review: bool = False
    review_reason: str = ''


class ScoringResult(BaseModel):
    change_id: str
    category: Optional[str] = None
    significance: Optional[Literal['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']] = None
    is_critical: Optional[bool] = None
    reason: str
    needs_review: bool = False
    review_reason: str = ''
