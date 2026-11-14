"""Chuyển dict của parse_docx sang BoundaryData theo schemas (không đọc lại file)."""
from dataclasses import dataclass

from ..schemas.contracts import Clause
from ..schemas.report_validation import validate_payload
from ..schemas.validation import validate_extracted_document


@dataclass
class BoundaryData:
    documents: dict
    clauses: dict
    units: dict


def _extracted(parsed, role):
    return {
        "document_id": parsed["document_id"],
        "role": role,
        "filename": parsed["filename"],
        "file_type": "DOCX",
        "blocks": [{"source_ref": b["source_ref"], "text": b["text"]} for b in parsed["source_blocks"]],
    }


def adapt_documents(parsed_list, roles=("BASE", "AMENDMENT")) -> BoundaryData:
    """parsed_list: [dict_v1, dict_s] từ parse_docx; roles tương ứng từng dict."""
    documents, clauses, units = {}, {}, {}
    for parsed, role in zip(parsed_list, roles):
        did = parsed["document_id"]
        document = _extracted(parsed, role)
        validate_extracted_document(document)
        documents[did] = document
        clauses[did], units[did] = [], {}

        def walk(node, article=None, clause=None):
            kind, label = node["kind"], node.get("label")
            if kind == "ARTICLE":
                article, clause = label, None
            elif kind == "CLAUSE":
                clause = label
            if kind in {"ARTICLE", "CLAUSE", "POINT"}:
                point = label if kind == "POINT" else None
                key = tuple(str(v).casefold() if v is not None else None for v in (article, clause, point))
                value = {
                    "unit_id": node["node_id"],
                    "id": " / ".join(filter(None, [
                        f"Điều {article}" if article else "",
                        f"khoản {clause}" if clause else "",
                        f"điểm {point}" if point else "",
                    ])),
                    "title": node.get("heading") or "",
                    "content": node["full_text"],
                    "source_refs": list(node["source_refs"]),
                }
                validate_payload(Clause, value)
                clauses[did].append(value)
                units[did].setdefault(key, []).append(value)
            for child in node.get("children", []):
                if child["kind"] not in {"QUOTATION", "QUOTED_CONTENT"}:
                    walk(child, article, clause)

        for article in parsed["articles"]:
            walk(article)
    return BoundaryData(documents, clauses, units)