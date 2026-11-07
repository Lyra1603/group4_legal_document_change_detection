"""V1–S pipeline foundation for the uploaded repository (Python >= 3.11; tested on 3.12).

Real work implemented: DOCX parsing; PDF conversion through the existing module;
source/role preservation; input errors; report envelope; cooperative deadline.
NOT implemented here: amendment linking, LightRAG HTTP/index lifecycle, semantic
analysis or scoring. Without an injected analysis_runner, return FAILED with
ANALYSIS_NOT_CONFIGURED, never a fabricated successful comparison.

The runner must be synchronous, release its own HTTP/index resources before
returning/raising, respect the deadline and return SRS-compatible nested results.
Only the report envelope is implemented here; full nested schema validation must
be added in app/schemas. A deadline check cannot interrupt a blocking library.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from time import monotonic
from typing import Any, Callable, Literal
import logging
import tempfile
import zipfile
from xml.etree.ElementTree import ParseError

from .document_processing.parser.legal_structure_parser import parse_docx

logger = logging.getLogger(__name__)
MISSING_COMPONENTS = (
    "amendment_linker", "lightrag_client/index_lifecycle", "context_builder",
    "text_diff", "semantic_diff", "scorer", "nested_report_validation",
)


@dataclass(frozen=True)
class DocumentInput:
    document_id: str
    role: Literal["BASE", "AMENDMENT", "REFERENCE"]
    filename: str  # display basename, not the temporary storage path
    path: Path

    def identity(self) -> dict[str, str]:
        return {"document_id": self.document_id, "role": self.role,
                "filename": self.filename}


@dataclass(frozen=True)
class ParsedDocument:
    document: DocumentInput
    tree: dict[str, Any]
    # block:N + offsets refer to the DOCX parsed, not original PDF pages.
    source_format: Literal["DOCX", "CONVERTED_DOCX"]


@dataclass
class AnalysisOutcome:
    status: Literal["SUCCESS", "PARTIAL", "FAILED"]
    results: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


AnalysisRunner = Callable[[list[ParsedDocument], str, float], AnalysisOutcome]


class PipelineInputError(ValueError):
    def __init__(self, code: str, message: str, document_id: str | None = None):
        super().__init__(message)
        self.code = code
        self.document_id = document_id


def issue(stage: str, code: str, message: str) -> dict[str, Any]:
    return {"stage": stage, "code": code, "message": message,
            "amendment_id": None}


def check_deadline(deadline: float) -> None:
    if monotonic() >= deadline:
        raise TimeoutError("Comparison deadline exceeded")


def parse_documents(documents: list[DocumentInput], work_dir: Path,
                    deadline: float) -> list[ParsedDocument]:
    """Keep parser trees and source_blocks intact; do not index them here."""
    work_dir.mkdir(parents=True, exist_ok=True)
    parsed: list[ParsedDocument] = []
    for position, document in enumerate(documents):
        check_deadline(deadline)
        source = Path(document.path)
        suffix = source.suffix.lower()
        if not source.is_file() or suffix not in {".docx", ".pdf"}:
            raise PipelineInputError("INVALID_DOCUMENT", "File khong hop le.",
                                     document.document_id)
        converted = suffix == ".pdf"
        try:
            if converted:
                # Lazy import: DOCX-only parsing does not import PDF dependencies.
                from .document_processing.pdf_to_docx import convert_pdf_to_docx
                destination = work_dir / f"converted_{position}.docx"
                convert_pdf_to_docx(source, destination,
                                    kind="base" if document.role == "BASE" else "other")
                source = destination
            check_deadline(deadline)
            tree = parse_docx(source, document_id=document.document_id)
        except (zipfile.BadZipFile, ParseError, ValueError) as exc:
            raise PipelineInputError(
                "UNREADABLE_DOCUMENT", "Khong doc duoc cau truc tai lieu.",
                document.document_id,
            ) from exc
        check_deadline(deadline)
        if not any(str(b.get("text", "")).strip()
                   for b in tree.get("source_blocks", [])):
            raise PipelineInputError("NO_READABLE_TEXT", "Tai lieu khong co chu doc duoc.",
                                     document.document_id)
        if document.role != "REFERENCE" and not tree.get("articles"):
            raise PipelineInputError("NO_ARTICLES", "Khong tim thay Dieu trong V1 hoac S.",
                                     document.document_id)
        # References without articles remain usable as blocks/table context.
        parsed.append(ParsedDocument(document, tree,
                                     "CONVERTED_DOCX" if converted else "DOCX"))
    return parsed


def _validate_inputs(documents: list[DocumentInput]) -> None:
    ids = [d.document_id for d in documents]
    if len(set(ids)) != len(ids):
        raise PipelineInputError("DUPLICATE_DOCUMENT_ID", "Trung document_id.")
    bases = [d for d in documents if d.role == "BASE"]
    amendments = [d for d in documents if d.role == "AMENDMENT"]
    if len(bases) != 1 or len(amendments) != 1:
        raise PipelineInputError("INVALID_ROLES", "Can dung mot V1 va mot S.")
    if bases[0].document_id != "v1" or amendments[0].document_id != "s":
        raise PipelineInputError("INVALID_DOCUMENT_ID", "V1 dung id v1, S dung id s.")
    if any(d.role not in {"BASE", "AMENDMENT", "REFERENCE"} for d in documents):
        raise PipelineInputError("INVALID_ROLES", "Vai tro tai lieu khong hop le.")


def run_comparison(documents: list[DocumentInput], comparison_id: str, *,
                   deadline: float | None = None,
                   analysis_runner: AnalysisRunner | None = None) -> dict[str, Any]:
    """Return a report; input errors raise PipelineInputError.

    Future runner orchestration: extract/link -> create one isolated index ->
    retrieve per amendment -> AnalysisContext -> diff/semantics/scoring -> cleanup.
    No HTTP endpoint names or unverified LightRAG payloads are assumed here.
    """
    _validate_inputs(documents)
    if not comparison_id:
        raise PipelineInputError("INVALID_COMPARISON_ID", "Thieu comparison_id.")
    deadline = monotonic() + 300 if deadline is None else deadline
    report: dict[str, Any] = {
        "comparison_id": comparison_id,
        "base_document": next(d.identity() for d in documents if d.role == "BASE"),
        "amendment_document": next(d.identity() for d in documents if d.role == "AMENDMENT"),
        "reference_documents": [d.identity() for d in documents if d.role == "REFERENCE"],
        "status": "FAILED", "results": [], "warnings": [], "errors": [],
    }
    stage = "document_processing"
    try:
        # Temp files are removed only after conversion/runner calls have returned.
        with tempfile.TemporaryDirectory(prefix="legal_pipeline_") as temporary:
            parsed = parse_documents(documents, Path(temporary), deadline)
            for item in parsed:
                for warning in item.tree.get("warnings", []):
                    report["warnings"].append(issue(
                        "parser", warning.get("code", "PARSER_WARNING"),
                        f"{item.document.document_id}: {warning.get('message', '')}",
                    ))
                if item.source_format == "CONVERTED_DOCX":
                    report["warnings"].append(issue(
                        "document_processing", "PDF_SOURCE_MAPPING_UNVERIFIED",
                        f"{item.document.document_id}: nguon hien theo DOCX chuyen doi; "
                        "chua xac minh anh xa ve trang PDF goc.",
                    ))
            if analysis_runner is None:
                report["errors"].append(issue(
                    "pipeline", "ANALYSIS_NOT_CONFIGURED",
                    "Da doc/parse tai lieu; chua noi cac thanh phan: "
                    + ", ".join(MISSING_COMPONENTS),
                ))
                return report
            stage = "analysis"
            check_deadline(deadline)
            outcome = analysis_runner(parsed, comparison_id, deadline)
            check_deadline(deadline)
            if not isinstance(outcome, AnalysisOutcome):
                raise TypeError("analysis_runner must return AnalysisOutcome")
            if outcome.status not in {"SUCCESS", "PARTIAL", "FAILED"}:
                raise ValueError("Invalid outcome status")
            if outcome.status == "SUCCESS" and outcome.errors:
                raise ValueError("SUCCESS cannot contain processing errors")
            if outcome.status != "SUCCESS" and not (outcome.warnings or outcome.errors):
                raise ValueError("Incomplete/failed outcome must explain its status")
            report["status"] = outcome.status
            report["results"] = outcome.results
            report["warnings"].extend(outcome.warnings)
            report["errors"].extend(outcome.errors)
    except PipelineInputError:
        raise
    except TimeoutError:
        report["errors"].append(issue(stage, "PROCESSING_TIMEOUT",
                                      "Vuot ngan sach thoi gian xu ly."))
    except Exception:
        # Do not log exception text, filenames, paths or document content.
        logger.error("comparison=%s stage=%s failed", comparison_id, stage)
        report["errors"].append(issue(stage, "PROCESSING_FAILED",
                                      "Buoc xu ly that bai; can kiem tra cau hinh/module."))
    return report
