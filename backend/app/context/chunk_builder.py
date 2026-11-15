"""Build source-bound ingestion records, not a replacement for the Parser.

One Reader block per record. Oversized blocks fail rather than silently losing
text. LightRAG may rechunk; registry validation handles literal substrings only.
"""
from dataclasses import dataclass
import hashlib
import json
from typing import TYPE_CHECKING

from ..schemas.contracts import ExtractedDocument
from ..schemas.report_validation import validate_payload

if TYPE_CHECKING:
    from ..pipeline import ParsedDocument


def documents_from_parsed(parsed: list["ParsedDocument"]) -> list[ExtractedDocument]:
    """Narrow Reader-block adapter; does not implement Clause/linker contracts.

    For converted PDFs, source_ref still addresses the converted DOCX; caller
    must retain the Pipeline's PDF_SOURCE_MAPPING_UNVERIFIED warning.
    """
    result = []
    for item in parsed:
        document = {**item.document.identity(),
                    "file_type": "PDF" if item.source_format == "CONVERTED_DOCX" else "DOCX",
                    "blocks": [{"source_ref": b["source_ref"], "text": b["text"]}
                               for b in item.tree["source_blocks"]]}
        validate_payload(ExtractedDocument, document)
        result.append(document)
    return result


@dataclass(frozen=True)
class SourceChunk:
    comparison_id: str
    file_source: str
    document_id: str
    role: str
    version: str
    source_ref: str
    text: str
    indexed_text: str


def build_chunks(comparison_id: str, documents: list[ExtractedDocument],
                 versions: dict[str, str], *, max_chunks: int = 100,
                 max_chars: int = 12000) -> list[SourceChunk]:
    if not comparison_id or not documents:
        raise ValueError("Comparison and source documents are required")
    result, ids = [], set()
    for document in documents:
        validate_payload(ExtractedDocument, document)
        did = document["document_id"]
        if did in ids or not versions.get(did) or document["role"] not in {"BASE", "AMENDMENT", "REFERENCE"}:
            raise ValueError("Duplicate document ID, absent version or invalid role")
        ids.add(did)
        refs = set()
        for block in document["blocks"]:
            ref, text = block["source_ref"], block["text"]
            if not ref or ref in refs:
                raise ValueError("Duplicate/empty source_ref")
            refs.add(ref)
            if not text.strip():
                continue
            if len(text) > max_chars:
                raise ValueError("Source block exceeds configured bound; agree structural chunking first")
            identity = [comparison_id, did, document["role"], versions[did], ref, text]
            token = hashlib.sha256(json.dumps(identity, ensure_ascii=False).encode()).hexdigest()
            source = f"pocs_{token}.txt"
            header = json.dumps({"comparison": comparison_id, "document_id": did,
                                 "role": document["role"], "version": versions[did],
                                 "source_ref": ref}, ensure_ascii=False)
            result.append(SourceChunk(comparison_id, source, did, document["role"], versions[did], ref,
                                      text, f"POCS_SOURCE {header}\n{text}"))
            if len(result) > max_chunks:
                raise ValueError("Too many source blocks for configured ingestion bound")
    if not result:
        raise ValueError("No readable source blocks")
    return result
