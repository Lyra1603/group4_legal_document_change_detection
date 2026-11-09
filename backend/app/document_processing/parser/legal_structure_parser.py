#!/usr/bin/env python3
"""Tách cấu trúc Điều - Khoản - Điểm từ DOCX, Python >= 3.10, không cần pip.

CLI (chạy ở thư mục gốc dự án):
    python backend/app/document_processing/legal_structure_parser.py input.docx output.json
API:
    from legal_structure_parser import parse_docx
    result = parse_docx("input.docx")

Đầu ra schema_version=1.0:
- articles: các Điều của thân văn bản, có children là Khoản/Điểm/QUOTATION.
- Mỗi node có kind, label, heading, node_id, children, segments, source_refs,
  full_text. segments chỉ là phần trực tiếp của node (không gồm children);
  full_text gồm cả các con, giữ chữ/số/dấu và xuống dòng của nguồn.
- QUOTATION chứa cây nội dung được trích (không phải Điều cấp ngoài của S).
- source_blocks giữ nguyên chữ trong từng paragraph/bảng của word/document.xml.
  source_ref + start/end trong segments là khoảng [start,end), tính từ 0 theo
  ký tự Python trong source_blocks[].text, không phải byte hoặc trang Word.
- outside giữ phần mở đầu, đề mục và phần sau thân bài, không vứt bỏ.
- warnings nêu phần cần kiểm tra; status chỉ nói về việc tách cấu trúc.

Căn cứ thiết kế lấy từ bản DOCX người dùng cung cấp (không kiểm định hiệu lực):
1. 78/2025/NĐ-CP: Điều 63 (cấp bố cục, Điều có thể không có Khoản), Điều 69
   khoản 4 (nhãn bổ sung có chữ/số).
2. Phụ lục I của 187/2025/NĐ-CP: Mục 1, Phần III, mục 2 điểm b
   (Điều N., Khoản N., Điểm a)); Phần II mục 5 (nhãn Điều/Khoản bổ sung).
3. 79/2025/NĐ-CP dùng để thử văn bản thường, có Điều không có Khoản.
Chỉ dùng quy tắc cấu trúc, không dùng font/cỡ chữ/ngày hiệu lực làm điều kiện.

Giới hạn: đầu vào phải có nhãn là chữ đọc được, ở đầu paragraph hoặc dòng
Word. Không đoán ranh giới nhiều khoản bị dính trên cùng một dòng; không tự
khôi phục nhãn Word đánh số tự động. Bảng giữ nguyên dưới dạng nguồn và không
phân tích các ô thành Điều/Khoản/Điểm. Chỉ xét thân chính trước phụ lục/khối
ký; văn bản ban hành kèm theo cần xử lý riêng. Trích dẫn nhiều dòng dùng dấu
ngoặc kép cong “...”; ngoặc thẳng nhiều dòng được giữ và cảnh báo, không suy
đoán. Không trích chỉ dẫn, liên kết V1-S, dựng V2 hoặc phân tích thay đổi.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = "{" + NS["w"] + "}"
LETTERS = "aăâbcdđeêghiklmnoôơpqrstuưvxy"
SUFFIX = f"[{LETTERS}]"
ARTICLE = re.compile(rf"^Điều\s+([0-9]+{SUFFIX}*)\.\s*(.*)$", re.IGNORECASE)
CLAUSE = re.compile(rf"^([0-9]+{SUFFIX}*)\.\s+(.*)$", re.IGNORECASE)
POINT = re.compile(rf"^([{LETTERS}][0-9]*)\)\s*(.*)$", re.IGNORECASE)
SECTION = re.compile(r"^(?:Phần|Chương|Mục|Tiểu mục)\s+(?:[IVXLCDM]+|[0-9]+|thứ\s+\S+)(?:\s|[.:]|$)", re.IGNORECASE)
ANNEX = re.compile(r"^PHỤ LỤC(?:\s+[IVXLCDM0-9]+)?\s*[.:]?\s*$", re.IGNORECASE)
SIGNATURE = re.compile(r"^(?:Nơi nhận\s*:|(?:TM\.|KT\.|TL\.|TUQ\.)\s+)", re.IGNORECASE)


def _text(element: ET.Element) -> str:
    """Đọc chữ hiển thị, kể cả hyperlink; bỏ chữ đã đánh dấu xóa."""
    out = []
    def visit(el):
        if el.tag in {W + "del", W + "moveFrom"}:
            return
        if el.tag == W + "t":
            out.append(el.text or "")
        elif el.tag == W + "tab":
            out.append("\t")
        elif el.tag in {W + "br", W + "cr"}:
            out.append("\n")
        else:
            for child in el:
                visit(child)
    visit(element)
    return "".join(out)


def _read_docx(path: Path):
    blocks, warnings = [], []
    with zipfile.ZipFile(path) as archive:
        body = ET.fromstring(archive.read("word/document.xml")).find("w:body", NS)
        if body is None:
            raise ValueError("DOCX không có w:body.")
        if body.find(".//w:del", NS) is not None or body.find(".//w:ins", NS) is not None:
            warnings.append({"code": "TRACKED_CHANGES", "message": "Đọc chữ ở trạng thái chấp nhận thay đổi; cần kiểm tra bản Word có track changes.", "source_refs": []})
        def read_children(parent):
            for el in parent:
                if el.tag == W + "p":
                    ref = f"block:{len(blocks) + 1}"
                    blocks.append({"source_ref": ref, "kind": "PARAGRAPH", "text": _text(el)})
                    if el.find("w:pPr/w:numPr", NS) is not None:
                        warnings.append({"code": "AUTO_NUMBERING", "message": "Paragraph có đánh số Word; nhãn không có trong chữ có thể chưa được tách.", "source_refs": [ref]})
                elif el.tag == W + "tbl":
                    # XML lưu ô merge một lần; không lặp ô như Table.rows.cells.
                    rows = []
                    for row in el.findall("w:tr", NS):
                        rows.append("\t".join("\n".join(_text(p) for p in cell.iter(W + "p")) for cell in row.findall("w:tc", NS)))
                    blocks.append({"source_ref": f"block:{len(blocks) + 1}", "kind": "TABLE", "text": "\n".join(rows)})
                elif el.tag == W + "sdt":
                    content = el.find("w:sdtContent", NS)
                    if content is not None:
                        read_children(content)
                elif el.tag not in {W + "sectPr"}:
                    if _text(el).strip():
                        blocks.append({"source_ref": f"block:{len(blocks) + 1}", "kind": "UNSUPPORTED", "text": _text(el)})
                        warnings.append({"code": "UNSUPPORTED_BLOCK", "message": "Giữ chữ của khối Word chưa hỗ trợ; không tách cấu trúc khối này.", "source_refs": [blocks[-1]["source_ref"]]})
        read_children(body)
    return blocks, warnings


def _lines(blocks):
    lines = []
    for block in blocks:
        if block["kind"] != "PARAGRAPH":
            lines.append({"source_ref": block["source_ref"], "start": 0, "end": len(block["text"]), "text": block["text"], "kind": block["kind"]})
            continue
        offset = 0
        for line in block["text"].splitlines(keepends=True) or [""]:
            end = offset + len(line.rstrip("\r\n"))
            lines.append({"source_ref": block["source_ref"], "start": offset, "end": end, "text": block["text"][offset:end], "kind": "PARAGRAPH"})
            offset += len(line)
    return lines


def _trim(line):
    left = len(line["text"]) - len(line["text"].lstrip())
    right = len(line["text"].rstrip())
    return {**line, "text": line["text"][left:right], "start": line["start"] + left, "end": line["start"] + right}


def _recognize(text):
    # NFC dùng riêng cho nhận diện; segments/full_text luôn lấy nguyên văn.
    t = unicodedata.normalize("NFC", text)
    for kind, pattern in (("ARTICLE", ARTICLE), ("CLAUSE", CLAUSE), ("POINT", POINT)):
        match = pattern.match(t)
        if match:
            return kind, match.group(1), match.group(2)
    return None


def _instruction(text):
    found = _recognize(text)
    return bool(found and re.match(r"(?:Sửa đổi|Bổ sung|Bãi bỏ|Thay thế)\b", found[2], re.IGNORECASE))


class _Parser:
    def __init__(self, blocks, document_id):
        self.blocks = {b["source_ref"]: b for b in blocks}
        self.document_id = document_id
        self.warnings = []
        self.counter = 0

    def warn(self, code, message, lines):
        self.warnings.append({"code": code, "message": message, "source_refs": list(dict.fromkeys(x["source_ref"] for x in lines))})

    def node(self, kind, label=None, heading=None):
        self.counter += 1
        return {"node_id": f"{self.document_id}:n{self.counter}", "kind": kind, "label": label, "heading": heading, "segments": [], "children": []}

    @staticmethod
    def add(node, line):
        node["segments"].append({k: line[k] for k in ("source_ref", "start", "end")})

    def parse(self, lines, quoted=False):
        root = self.node("QUOTED_CONTENT" if quoted else "BODY")
        outside = []
        article = clause = point = None
        after_body = False
        section_title_pending = False
        i = 0
        while i < len(lines):
            raw = lines[i]
            line = _trim(raw)
            t = line["text"]
            current = point or clause or article or root
            if not t:
                i += 1
                continue
            if raw["kind"] != "PARAGRAPH":
                if not quoted and article is not None and re.search(r"(?:^|\n)\s*Nơi nhận\s*:", t, re.IGNORECASE):
                    after_body = True
                if not quoted and (article is None or after_body):
                    outside.append({"region": "AFTER_BODY" if after_body else "BEFORE_BODY", **raw})
                else:
                    self.add(current, raw)
                    self.warn("TABLE_NOT_PARSED", "Giữ khối nguồn; chưa phân tách cấu trúc bên trong bảng/khối đặc biệt.", [raw])
                i += 1
                continue
            if not quoted and (ANNEX.match(t) or (article is not None and SIGNATURE.match(t))):
                after_body = True
            if after_body:
                outside.append({"region": "AFTER_BODY", **raw})
                i += 1
                continue
            # Chỉ mở khối trích dẫn khi ngoặc mở nằm đầu dòng, không phải
            # mọi cụm từ ngắn được đặt trong ngoặc kép ở giữa câu.
            if t.startswith('“'):
                gathered = []
                depth = 0
                closed = False
                interrupted = False
                j = i
                while j < len(lines):
                    part = lines[j]
                    if j > i and not quoted and _instruction(_trim(part)["text"]):
                        interrupted = True
                        break
                    gathered.append(part)
                    for ch in part["text"]:
                        if ch == '“':
                            depth += 1
                        elif ch == '”':
                            depth -= 1
                    if depth <= 0:
                        closed = True
                        break
                    j += 1
                if not closed:
                    self.warn("UNCLOSED_QUOTATION", "Ngoặc trích dẫn không đóng; giữ nguyên phần còn lại trong khối trích dẫn, cần kiểm tra.", gathered)
                q = self.node("QUOTATION")
                current["children"].append(q)
                # q sở hữu nguyên văn, kể cả ngoặc và dấu kết thúc.
                for part in gathered:
                    self.add(q, part)
                inner = [dict(x) for x in gathered]
                first = _trim(inner[0])
                inner[0] = {**first, "text": first["text"][1:], "start": first["start"] + 1}
                if closed:
                    last = inner[-1]
                    pos = last["text"].rfind('”')
                    if pos >= 0:
                        inner[-1] = {**last, "text": last["text"][:pos], "end": last["start"] + pos}
                subtree, _ = self.parse(inner, quoted=True)
                q["quoted_structure"] = subtree
                i = j if interrupted else j + 1
                continue
            if t.startswith('"'):
                self.warn("STRAIGHT_QUOTE", "Dòng bắt đầu bằng ngoặc kép thẳng; giữ nội dung, không tách nhãn bên trong dòng này.", [raw])
                self.add(current, raw)
                i += 1
                continue
            if SECTION.match(t):
                if quoted:
                    self.add(current, raw)
                else:
                    outside.append({"region": "SECTION_HEADING", **raw})
                    section_title_pending = not bool(re.search(r"[.:]\s*\S", t))
                    clause = point = None
                i += 1
                continue
            if section_title_pending:
                if not _recognize(t):
                    outside.append({"region": "SECTION_TITLE", **raw})
                    section_title_pending = False
                    i += 1
                    continue
                section_title_pending = False
            found = _recognize(t)
            # Một số file sửa đổi đóng ngoặc ngay sau tên Mục rồi để các
            # Điều bổ sung phía sau không có ngoặc mở (187/2025 có dạng này).
            # Không đẩy các Điều đó lên cấp S. Chỉ suy ranh giới khi có cả
            # chỉ dẫn '... như sau' và nhãn Điều lệch trình tự; luôn cảnh báo.
            if not quoted and found and not _instruction(t) and article is not None:
                expected = str(int(re.match(r"[0-9]+", article["label"])[0]) + 1)
                owner = point or clause
                instruction = "\n".join(self.blocks[s["source_ref"]]["text"][s["start"]:s["end"]] for s in owner["segments"]) if owner else ""
                previous_quote = bool(owner and owner["children"] and owner["children"][-1]["kind"] == "QUOTATION")
                is_outer_article = found[0] == "ARTICLE" and found[1] == expected
                if previous_quote and not is_outer_article and re.search(r"(?:sửa đổi|bổ sung).*như sau\s*:\s*$", instruction, re.IGNORECASE):
                    gathered = []
                    j = i
                    while j < len(lines):
                        candidate = _recognize(_trim(lines[j])["text"])
                        if j > i and candidate:
                            next_article = candidate[0] == "ARTICLE" and candidate[1] == expected
                            next_instruction = _instruction(_trim(lines[j])["text"])
                            if next_article or next_instruction:
                                break
                        gathered.append(lines[j])
                        j += 1
                    q = self.node("QUOTATION")
                    q["boundary_basis"] = "INFERRED_NEEDS_REVIEW"
                    current["children"].append(q)
                    for part in gathered:
                        self.add(q, part)
                    q["quoted_structure"], _ = self.parse(gathered, quoted=True)
                    self.warn("INFERRED_QUOTATION", "Nhãn tiếp diễn sau đoạn trích thiếu ngoặc mở; tách thành nội dung trích theo chỉ dẫn trước đó, cần kiểm tra ranh giới.", gathered)
                    i = j
                    continue
            if found:
                kind, label, heading = found
                if kind == "ARTICLE":
                    if any(n["kind"] == kind and n["label"].lower() == label.lower() for n in root["children"]):
                        self.warn("DUPLICATE_ARTICLE", f"Lặp nhãn Điều {label}; giữ các node riêng, không ghi đè.", [raw])
                    article = self.node(kind, label, heading)
                    root["children"].append(article)
                    clause = point = None
                    self.add(article, raw)
                elif kind == "CLAUSE" and (article is not None or quoted):
                    parent = article or root
                    if any(n["kind"] == kind and n["label"].lower() == label.lower() for n in parent["children"]):
                        self.warn("DUPLICATE_CLAUSE", f"Lặp nhãn Khoản {label} trong cùng cấp; cần kiểm tra ranh giới.", [raw])
                    clause = self.node(kind, label)
                    parent["children"].append(clause)
                    point = None
                    self.add(clause, raw)
                elif kind == "POINT" and (clause is not None or quoted):
                    parent = clause or article or root
                    if any(n["kind"] == kind and n["label"].lower() == label.lower() for n in parent["children"]):
                        self.warn("DUPLICATE_POINT", f"Lặp nhãn Điểm {label} trong cùng cấp; cần kiểm tra ranh giới.", [raw])
                    point = self.node(kind, label)
                    parent["children"].append(point)
                    self.add(point, raw)
                else:
                    self.warn("ORPHAN_LABEL", "Gặp nhãn nhưng chưa có cấp cha phù hợp; giữ nguyên, không tự tạo cha.", [raw])
                    if article is None and not quoted:
                        outside.append({"region": "BEFORE_BODY", **raw})
                    else:
                        self.add(current, raw)
            elif article is None and not quoted:
                outside.append({"region": "BEFORE_BODY", **raw})
            else:
                self.add(current, raw)
            i += 1
        return root, outside

    def finish(self, node):
        spans = list(node["segments"])
        for child in node["children"]:
            self.finish(child)
            spans.extend(child.pop("_all_segments"))
        if "quoted_structure" in node:
            self.finish(node["quoted_structure"])
            node["quoted_structure"].pop("_all_segments", None)
        spans.sort(key=lambda x: (int(x["source_ref"].split(":")[1]), x["start"]))
        node["source_refs"] = list(dict.fromkeys(s["source_ref"] for s in spans))
        node["full_text"] = "\n".join(self.blocks[s["source_ref"]]["text"][s["start"]:s["end"]] for s in spans)
        node["_all_segments"] = spans


def parse_docx(input_path: str | Path, document_id: str | None = None) -> dict:
    """Đọc DOCX thành dict JSON; không sửa file đầu vào, không gọi mạng/AI.

    document_id có thể truyền từ pipeline; mặc định là SHA256 của file.
    Định danh node chỉ có ý nghĩa trong kết quả của file, không dùng làm khóa
    để tự ghép nhận xét hoặc tự liên kết thay đổi giữa các phiên bản.
    """
    path = Path(input_path)
    if path.suffix.lower() != ".docx":
        raise ValueError("Chỉ nhận .docx; PDF cần được chuyển đổi trước.")
    document_id = document_id or "doc_" + hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    blocks, warnings = _read_docx(path)
    parser = _Parser(blocks, document_id)
    root, outside = parser.parse(_lines(blocks))
    parser.finish(root)
    root.pop("_all_segments", None)
    articles = [n for n in root["children"] if n["kind"] == "ARTICLE"]
    if not articles:
        parser.warn("NO_ARTICLES", "Không tìm thấy Điều dạng 'Điều N.' trong thân chính.", [])
    warnings.extend(parser.warnings)
    def count(nodes):
        result = {"articles": 0, "clauses": 0, "points": 0, "quotations": 0}
        names = {"ARTICLE": "articles", "CLAUSE": "clauses", "POINT": "points", "QUOTATION": "quotations"}
        for node in nodes:
            if node["kind"] in names:
                result[names[node["kind"]]] += 1
            sub = count(node["children"])
            for k in result:
                result[k] += sub[k]
        return result
    return {"schema_version": "1.0", "document_id": document_id, "filename": path.name,
            "status": "FAILED" if not articles else ("PARTIAL" if warnings else "SUCCESS"),
            "articles": articles, "outside": outside, "source_blocks": blocks,
            "warnings": warnings, "summary": count(articles)}


def main():
    ap = argparse.ArgumentParser(description="Tách Điều-Khoản-Điểm: DOCX -> JSON, không dùng AI.")
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--document-id")
    ap.add_argument("--overwrite", action="store_true", help="Cho phép ghi đè JSON đã có.")
    args = ap.parse_args()
    try:
        if args.output.resolve() == args.input.resolve():
            raise ValueError("Đầu ra phải khác file đầu vào.")
        result = parse_docx(args.input, args.document_id)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w" if args.overwrite else "x", encoding="utf-8") as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        print(json.dumps({"output": str(args.output), "status": result["status"], **result["summary"], "warnings": len(result["warnings"])}, ensure_ascii=False))
        return 2 if result["status"] == "FAILED" else 0
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
