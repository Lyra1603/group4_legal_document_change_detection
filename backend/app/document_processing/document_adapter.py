"""Chuyển ParsedDocument (runner) hoặc dict của parse_docx sang BoundaryData theo schemas."""
from dataclasses import dataclass

from ..schemas.contracts import Clause
from ..schemas.report_validation import validate_payload
from ..schemas.validation import validate_extracted_document


@dataclass
class BoundaryData:
    documents: dict
    clauses: dict
    units: dict


def _get(obj, name, default=None):
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _normalize(parsed):
    """Trả dict chuẩn: document_id, role, filename, source_blocks, articles.

    Chấp nhận:
    - dict của parse_docx: có document_id, filename, source_blocks, articles;
    - ParsedDocument của runner: có .document (identity(), role, blocks) và .tree (articles).
    """
    if isinstance(parsed, dict) and "document_id" in parsed:
        return {
            "document_id": parsed["document_id"],
            "role": parsed.get("role"),
            "filename": parsed["filename"],
            "source_blocks": parsed["source_blocks"],
            "articles": parsed.get("articles", []),
        }
    doc = _get(parsed, "document")
    tree = _get(parsed, "tree")
    if doc is None or tree is None:
        raise TypeError(f"Không đọc được kiểu {type(parsed).__name__}: thiếu document hoặc tree")
    identity = doc.identity() if hasattr(doc, "identity") else {}
    blocks = _get(doc, "blocks")
    if blocks is None:
        blocks = _get(tree, "source_blocks")
    if blocks is None:
        raise TypeError("ParsedDocument không có blocks/source_blocks")
    return {
        "document_id": identity.get("document_id") or _get(doc, "document_id"),
        "role": identity.get("role") or _get(doc, "role"),
        "filename": identity.get("filename") or _get(doc, "filename"),
        "source_blocks": [
            {"source_ref": _get(b, "source_ref"), "text": _get(b, "text")} for b in blocks
        ],
        "articles": _get(tree, "articles", []),
    }


def _extracted(n):
    return {
        "document_id": n["document_id"],
        "role": n["role"],
        "filename": n["filename"],
        "file_type": "DOCX",
        "blocks": [{"source_ref": b["source_ref"], "text": b["text"]} for b in n["source_blocks"]],
    }


def adapt_documents(parsed_list, roles=None) -> BoundaryData:
    """parsed_list: [v1, s, ref_1, ...]. Role lấy từ object; nếu thiếu thì theo vị trí:
    đầu là BASE, thứ hai là AMENDMENT, còn lại là REFERENCE. roles (nếu truyền) ghi đè."""
    normalized = [_normalize(p) for p in parsed_list]
    for i, n in enumerate(normalized):
        if roles is not None:
            n["role"] = roles[i]
        elif not n["role"]:
            n["role"] = "BASE" if i == 0 else "AMENDMENT" if i == 1 else "REFERENCE"

    documents, clauses, units = {}, {}, {}
    for n in normalized:
        did = n["document_id"]
        document = _extracted(n)
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

        for article in n["articles"]:
            walk(article)
    return BoundaryData(documents, clauses, units)