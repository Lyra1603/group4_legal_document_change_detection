"""Chuyển HTML toàn văn sang DOCX để Reader/Parser đọc, không gọi mạng.

Cài: python -m pip install python-docx lxml
CLI: python backend/app/document_processing/html_to_docx.py input.html [output.docx]
     [--encoding utf-8] [--source-url URL] [--document-number 84/2026/TT-BXD]
     [--output-dir folder]
Mặc định: tự đọc số ký hiệu, lưu cạnh nguồn; dấu / đổi thành _. Không đoán từ dẫn chiếu.
API: convert_html_to_docx(input_path, output_path=None, encoding=None, source_url=None,
                          document_number=None, output_dir=None)
Trả (đường_dẫn_docx, đường_dẫn_report_json), giống pdf_to_docx.

Giữ thứ tự chữ, đoạn, nhấn mạnh, xuống dòng, bảng và ô gộp hình chữ nhật.
Không chạy script, tải ảnh/CSS, OCR hoặc dựng lại bố cục bản in chính thức.
Không sửa chữ/số/dấu câu hoặc đoán đơn vị pháp lý. Báo cáo luôn needs_review.
"""
from __future__ import annotations

import argparse
import codecs
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from lxml import etree, html

if __package__:
    from .document_number import identify_document_number, resolve_docx_output
else:
    from document_number import identify_document_number, resolve_docx_output

BLOCKS = frozenset(('p', 'div', 'section', 'article', 'header', 'footer', 'main',
                    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'ul', 'ol',
                    'li', 'blockquote', 'pre', 'center', 'address', 'dl', 'dt', 'dd'))
OMIT = frozenset(('head', 'script', 'style', 'noscript', 'template'))
ALIGN = {'left': WD_ALIGN_PARAGRAPH.LEFT, 'center': WD_ALIGN_PARAGRAPH.CENTER,
         'right': WD_ALIGN_PARAGRAPH.RIGHT, 'justify': WD_ALIGN_PARAGRAPH.JUSTIFY}


def _compact(text):
    return re.sub(r'\s+', '', text)


def _tag(element):
    return element.tag.lower() if isinstance(element.tag, str) else ''


def _css(element):
    return {k.strip().lower(): v.strip().lower() for entry in element.get('style', '').split(';')
            if ':' in entry for k, v in (entry.split(':', 1),)}


def _inline_style(element, inherited):
    tag, css = _tag(element), _css(element)
    style = set(inherited)
    for enabled, key in ((tag in ('b', 'strong') or css.get('font-weight') in ('bold', '600', '700', '800', '900'), 'bold'),
                         (tag in ('i', 'em') or css.get('font-style') == 'italic', 'italic'),
                         (tag == 'u' or 'underline' in css.get('text-decoration', ''), 'underline'),
                         (tag in ('s', 'strike', 'del'), 'strike'), (tag == 'sup', 'sup'), (tag == 'sub', 'sub'),
                         (tag == 'pre' or css.get('white-space', '').startswith('pre'), 'pre')):
        if enabled:
            style.add(key)
    if css.get('font-weight') in ('normal', '100', '200', '300', '400', '500'):
        style.discard('bold')
    if css.get('font-style') == 'normal':
        style.discard('italic')
    if css.get('white-space') == 'normal':
        style.discard('pre')
    return frozenset(style)


def _ancestor_style(element):
    style = frozenset()
    for ancestor in reversed(list(element.iterancestors())):
        style = _inline_style(ancestor, style)
    return style


def _decode(raw, encoding=None):
    if encoding is None:
        if raw.startswith(codecs.BOM_UTF8):
            encoding = 'utf-8-sig'
        elif raw.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
            encoding = 'utf-16'
        else:
            declared = re.search(br'<meta\b[^>]*charset\s*=\s*[\"\x27]?\s*([a-zA-Z0-9_-]+)', raw[:16384], re.I)
            encoding = declared.group(1).decode('ascii') if declared else 'utf-8'
    try:
        text = raw.decode(encoding, errors='strict')
    except (UnicodeError, LookupError) as error:
        raise ValueError('Không đọc được encoding HTML; chỉ định --encoding theo nguồn, không thay ký tự lỗi.') from error
    if '\ufffd' in text:
        raise ValueError('HTML có ký tự thay thế U+FFFD; kiểm tra lại nguồn/encoding trước khi chuyển.')
    return text, encoding


def _font(run):
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0, 0, 0)
    fonts = run._element.get_or_add_rPr().get_or_add_rFonts()
    for name in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
        fonts.set(qn('w:' + name), 'Times New Roman')


def _doc_text(document, generated_prefixes):
    parts = []
    for index, p in enumerate(document.element.body.iter(qn('w:p'))):
        value = ''.join(p.xpath('.//w:t/text()'))
        if index in generated_prefixes:
            prefix = generated_prefixes[index]
            if not value.startswith(prefix):
                raise RuntimeError('Nhãn danh sách tạo thêm không khớp sau khi lưu DOCX.')
            value = value[len(prefix):]
        parts.append(value)
    return ''.join(parts)


class _Converter:
    def __init__(self, document):
        self.doc = document
        self.warnings = []
        self.labels = []
        self.links = []
        self.table_count = 0
        self.merged_cells = 0
        self.preformatted = set()

    def warn(self, code, message):
        if not any(w['code'] == code for w in self.warnings):
            self.warnings.append({'code': code, 'message': message})

    def new_paragraph(self, parent, element):
        p = parent.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.2
        p.paragraph_format.widow_control = True
        align = ''
        for ancestor in (element, *element.iterancestors()):
            align = _css(ancestor).get('text-align', ancestor.get('align', '')).lower()
            if _tag(ancestor) == 'center' and not align:
                align = 'center'
            if align:
                break
        p.alignment = ALIGN.get(align, WD_ALIGN_PARAGRAPH.LEFT)
        if 'pre' in _inline_style(element, _ancestor_style(element)):
            self.preformatted.add(p._p)
        return p

    def text(self, p, value, style=()):
        if not value:
            return
        if 'pre' not in style:
            value = re.sub(r'[ \t\r\n\f]+', ' ', value)
        run = p.add_run(value)
        _font(run)
        run.bold, run.italic, run.underline = (key in style for key in ('bold', 'italic', 'underline'))
        run.font.strike = 'strike' in style
        if 'sup' in style:
            run.font.superscript = True
        elif 'sub' in style:
            run.font.subscript = True

    def inline(self, p, element, inherited=None):
        tag = _tag(element)
        style = _inline_style(element, _ancestor_style(element) if inherited is None else inherited)
        if tag in OMIT:
            return
        if tag == 'br':
            p.add_run().add_break()
            return
        if tag == 'img':
            self.warn('IMAGES_NOT_EMBEDDED', 'Không tải/nhúng ảnh hoặc OCR; cần kiểm tra phần nội dung chỉ có trong ảnh.')
        if tag in ('svg', 'math', 'iframe', 'object', 'input', 'textarea', 'select'):
            self.warn('UNSUPPORTED_CONTENT', 'Nguồn có công thức, đối tượng hoặc biểu mẫu tương tác; chỉ giữ chữ có sẵn, cần đối chiếu.')
        if tag == 'a' and element.get('href'):
            self.links.append({'text': ''.join(element.itertext()), 'href': element.get('href')})
            self.warn('LINK_TARGETS_IN_REPORT', 'Giữ chữ của liên kết trong DOCX; đích liên kết được ghi riêng ở report, không tạo liên kết bấm được.')
        self.text(p, element.text, style)
        for child in element:
            self.inline(p, child, frozenset(style))
            self.text(p, child.tail, style)

    def container(self, parent, element):
        """Nhóm inline liên tiếp thành đoạn, tách tại block; giữ cả tail text."""
        current = None
        if element.text and element.text.strip():
            current = self.new_paragraph(parent, element)
            self.text(current, element.text, _inline_style(element, _ancestor_style(element)))
        for child in element:
            tag = _tag(child)
            if tag in BLOCKS:
                current = None
                self.block(parent, child)
            elif tag not in OMIT:
                if current is None:
                    current = self.new_paragraph(parent, element)
                self.inline(current, child)
            if child.tail:
                if current is not None or child.tail.strip():
                    if current is None:
                        current = self.new_paragraph(parent, element)
                    self.text(current, child.tail, _inline_style(element, _ancestor_style(element)))

    def block(self, parent, element, prefix=None):
        tag = _tag(element)
        if tag in OMIT:
            return
        if tag == 'table':
            self.table(parent, element)
            return
        if tag in ('ul', 'ol'):
            self.list_block(parent, element)
            return
        if any(_tag(c) in BLOCKS for c in element):
            self.container(parent, element)
            return
        if not ''.join(element.itertext()).strip() and not element.xpath('.//img|.//svg'):
            return
        p = self.new_paragraph(parent, element)
        if prefix:
            self.text(p, prefix)
            self.labels.append((p._p, prefix))
        self.inline(p, element)
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            p.paragraph_format.keep_with_next = True
            for run in p.runs:
                run.bold = True
        elif re.match(r'^(Điều\s+\d+[a-zđ]?\.|Chương\s+[IVXLCDM\d]+\b)', p.text.strip()) and len(p.text.strip()) < 250:
            p.paragraph_format.keep_with_next = True

    def list_block(self, parent, element):
        # HTML list markers are absent from itertext. Emit literal markers so Parser
        # can read them; track additions separately for the source text invariant.
        ordered = _tag(element) == 'ol'
        try:
            number = int(element.get('start', '1'))
        except ValueError:
            raise ValueError('Thuộc tính start của danh sách không hợp lệ.')
        if element.text and element.text.strip():
            self.text(self.new_paragraph(parent, element), element.text)
        for child in element:
            if _tag(child) == 'li':
                if child.get('value'):
                    number = int(child.get('value'))
                kind = element.get('type', '1')
                if ordered and kind in ('a', 'A') and 1 <= number <= 26:
                    label = chr(ord(kind) + number - 1) + '. '
                elif ordered:
                    label = str(number) + '. '
                    if kind != '1':
                        self.warn('LIST_STYLE_APPROXIMATED', 'Kiểu nhãn danh sách không hỗ trợ được biểu diễn bằng số thập phân.')
                else:
                    label = '• '
                # Prefix must precede the first paragraph even for li containing p.
                before = set(parent._element.iter(qn('w:p')))
                self.block(parent, child)
                added = [p for p in parent._element.iter(qn('w:p')) if p not in before]
                if not added:
                    p = self.new_paragraph(parent, child)
                    added = [p._p]
                from docx.text.paragraph import Paragraph
                p = Paragraph(added[0], parent)
                run = p.add_run(label); _font(run)
                p._p.remove(run._r)
                position = 1 if p._p.pPr is not None else 0
                p._p.insert(position, run._r)
                self.labels.append((p._p, label))
                number += 1
            else:
                self.block(parent, child)
            if child.tail and child.tail.strip():
                self.text(self.new_paragraph(parent, element), child.tail)

    def table(self, parent, element):
        rows = element.xpath('./tr|./thead/tr|./tbody/tr|./tfoot/tr')
        if not rows:
            self.warn('EMPTY_TABLE', 'Bảng không có hàng; chỉ giữ chữ trong bảng nếu có.')
            self.container(parent, element)
            return
        plan, occupied, width = [], set(), 0
        for r, row in enumerate(rows):
            c = 0
            for cell in row:
                if _tag(cell) not in ('td', 'th'):
                    continue
                while (r, c) in occupied:
                    c += 1
                try:
                    cs = int(cell.get('colspan', '1'))
                    rs = int(cell.get('rowspan', '1'))
                except ValueError as error:
                    raise ValueError('colspan/rowspan không phải số nguyên.') from error
                rs = len(rows) - r if rs == 0 else rs
                if cs < 1 or cs > 100 or rs < 1 or r + rs > len(rows):
                    raise ValueError('Ô gộp không hợp lệ hoặc vượt kích thước bảng hỗ trợ.')
                rectangle = {(i, j) for i in range(r, r + rs) for j in range(c, c + cs)}
                if rectangle & occupied:
                    raise ValueError('Các ô bảng chồng nhau; cần kiểm tra HTML thay vì tự đoán.')
                occupied.update(rectangle)
                plan.append((r, c, rs, cs, cell))
                c += cs
                width = max(width, c)
        if not width:
            self.container(parent, element)
            return
        if width > 100:
            raise ValueError('Bảng quá rộng; cần kiểm tra nguồn.')
        for caption in element.xpath('./caption'):
            self.block(parent, caption)
        table = parent.add_table(rows=len(rows), cols=width)
        table.style = 'Table Grid'
        self.table_count += 1
        for r, c, rs, cs, source in plan:
            target = table.cell(r, c)
            if rs > 1 or cs > 1:
                target = target.merge(table.cell(r + rs - 1, c + cs - 1))
                self.merged_cells += 1
            self.block(target, source)
            # Remove only empty paragraphs introduced by python-docx before content.
            while len(target.paragraphs) > 1 and not target.paragraphs[0].text and len(target._tc) > 2:
                first = target.paragraphs[0]._p
                first.getparent().remove(first)


def convert_html_to_docx(input_path, output_path=None, encoding=None, source_url=None,
                         document_number=None, output_dir=None):
    source = Path(input_path)
    if not source.is_file():
        raise FileNotFoundError(f'Không tìm thấy {source}')
    if source.suffix.lower() not in ('.html', '.htm'):
        raise ValueError('Đầu vào phải .html/.htm.')
    raw = source.read_bytes()
    decoded, chosen_encoding = _decode(raw, encoding)
    parser = html.HTMLParser(no_network=True, remove_comments=True)
    try:
        tree = html.document_fromstring(decoded, parser=parser)
    except (etree.ParserError, ValueError) as error:
        raise ValueError('HTML không đọc được hoặc rỗng.') from error
    body = tree.find('body')
    if body is None:
        raise ValueError('HTML không có phần thân văn bản.')
    doc = Document()
    converter = _Converter(doc)
    omitted = 0
    for element in list(body.iterdescendants()):
        if _tag(element) in OMIT and element.getparent() is not None:
            element.drop_tree()
            omitted += 1
    expected = ''.join(body.itertext())
    if not _compact(expected):
        raise ValueError('HTML có body rỗng/không có chữ; không tạo DOCX trắng. Kiểm tra nguồn PDF nếu có.')
    if '\x00' in decoded:
        raise ValueError('HTML có ký tự NUL; kiểm tra encoding/nguồn.')
    title_node = tree.find('head/title')
    source_title = ''.join(title_node.itertext()).strip() if title_node is not None else ''
    metadata_numbers = [element.get('content') for element in tree.xpath('//meta[@name][@content]')
                        if element.get('name', '').lower() in ('document-number', 'document_number', 'docnumber', 'so_ky_hieu')
                        and element.get('content', '').strip()]
    number, number_evidence = identify_document_number(
        '\n'.join(body.itertext()), title=source_title, metadata=metadata_numbers, provided=document_number)
    output = resolve_docx_output(source, output_path, number, output_dir)
    log = output.with_suffix('.report.json')
    for target in (output, log):
        if target.exists():
            raise FileExistsError(f'Đã tồn tại {target}; hãy chọn đầu ra mới.')
    if not number:
        converter.warn('DOCUMENT_NUMBER_NOT_FOUND', 'Không xác định được số ký hiệu; chỉ dùng tên đầu ra thủ công đã cung cấp.')
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin, section.bottom_margin = Cm(2), Cm(2)
    section.left_margin, section.right_margin = Cm(3), Cm(2)
    doc.styles['Normal'].font.name = 'Times New Roman'
    doc.styles['Normal'].font.size = Pt(14)
    doc.core_properties.author = ''
    title = tree.find('head/title')
    doc.core_properties.title = ''.join(title.itertext()).strip()[:255] if title is not None else source.stem
    doc.core_properties.comments = 'Derived from HTML. Source and conversion limitations are in the adjacent report.'
    converter.container(doc, body)
    # Browser HTML collapses source-code indentation; keep explicit br and pre.
    for p in doc.element.body.iter(qn('w:p')):
        if p in converter.preformatted:
            continue
        texts = p.xpath('.//w:t')
        if texts:
            texts[0].text = (texts[0].text or '').lstrip(' \t\r\n\f')
            texts[-1].text = (texts[-1].text or '').rstrip(' \t\r\n\f')
    if omitted:
        converter.warn('NON_BODY_CONTENT_OMITTED', 'Bỏ script/style/noscript/template; không thực thi mã HTML.')
    if body.xpath('.//*[@hidden or contains(translate(@style,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),"display:") or @class]'):
        converter.warn('CSS_NOT_RENDERED', 'Không thực thi CSS ngoài/class hoặc ẩn/hiện theo trình duyệt; giữ chữ trong body, cần kiểm tra bố cục/khối ẩn.')
    if tree.xpath('//link[@rel="stylesheet"]|//style'):
        converter.warn('STYLESHEET_NOT_RENDERED', 'Không dựng lại stylesheet của trang web; chỉ ánh xạ định dạng inline cơ bản.')
    paragraph_indices = {p: i for i, p in enumerate(doc.element.body.iter(qn('w:p')))}
    prefixes = {paragraph_indices[p]: prefix for p, prefix in converter.labels}
    if _compact(_doc_text(doc, prefixes)) != _compact(expected):
        raise RuntimeError('Kiểm tra toàn vẹn thất bại: chữ/thứ tự ngoài khoảng trắng khác HTML; không xuất đầu ra.')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='html_to_docx_', dir=output.parent) as working:
        temporary = Path(working)
        converted = temporary / 'result.docx'
        doc.save(converted)
        reopened = Document(converted)
        if _compact(_doc_text(reopened, prefixes)) != _compact(expected):
            raise RuntimeError('Chữ trong DOCX sau lưu không khớp nguồn HTML.')
        report = {
            'input': str(source.resolve()), 'output': str(output.resolve()),
            'document_number': number, 'document_number_evidence': number_evidence,
            'automatic_output_name': output_path is None,
            'source_url': source_url, 'input_sha256': hashlib.sha256(raw).hexdigest(),
            'output_sha256': hashlib.sha256(converted.read_bytes()).hexdigest(),
            'encoding': chosen_encoding, 'status': 'needs_review',
            'whitespace_policy': 'Collapse HTML source indentation outside pre/pre-wrap; preserve explicit br; trim paragraph edge spaces.',
            'integrity_non_whitespace_exact_match': True,
            'non_whitespace_length_before': len(_compact(expected)),
            'non_whitespace_length_after': len(_compact(_doc_text(reopened, prefixes))),
            'paragraph_count': len(list(doc.element.body.iter(qn('w:p')))),
            'table_count': converter.table_count, 'merged_cell_count': converter.merged_cells,
            'generated_list_labels': [{'output_paragraph_0based': index, 'prefix': value} for index, value in prefixes.items()],
            'links': converter.links, 'warnings': converter.warnings,
            'requires_visual_review': True,
            'limitations': ['Không chứng nhận toàn văn nguồn đủ/chính xác hoặc đúng phiên bản pháp lý.',
                            'Không khôi phục bố cục bản in; không tải ảnh/CSS, không OCR.',
                            'Nhãn danh sách HTML được tạo thành chữ và ghi riêng; cần duyệt trước khi dùng làm nhãn pháp lý.',
                            'So sánh bỏ qua khoảng trắng; không chứng minh ngắt đoạn hoặc khoảng cách từ đúng.'],
            'intermediate_files_retained': False,
        }
        staged_report = temporary / 'report.json'
        staged_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        created = []
        try:
            for staged, target in ((converted, output), (staged_report, log)):
                with target.open('xb') as destination:
                    created.append(target)
                    with staged.open('rb') as handle:
                        shutil.copyfileobj(handle, destination)
        except Exception:
            for target in created:
                target.unlink(missing_ok=True)
            raise
    return output.resolve(), log.resolve()


if __name__ == '__main__':
    # Windows redirected terminals can default to cp1252; conversion must not
    # report failure merely because the Vietnamese output path cannot be printed.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='backslashreplace')
    arguments = argparse.ArgumentParser(description='HTML -> DOCX và report; không gọi mạng, không ghi đè file.')
    arguments.add_argument('input_file')
    arguments.add_argument('output_docx', nargs='?', help='Không truyền: tự đặt <số_ký_hiệu>.docx cạnh nguồn.')
    arguments.add_argument('--document-number', help='Số ký hiệu từ metadata đã đối chiếu khi HTML không có trường này.')
    arguments.add_argument('--output-dir', help='Thư mục đích khi dùng tên tự động.')
    arguments.add_argument('--encoding', help='Encoding đầu vào; mặc định BOM/meta charset hoặc UTF-8.')
    arguments.add_argument('--source-url', help='Nguồn gốc để ghi report, không tải URL này.')
    args = arguments.parse_args()
    try:
        output, report = convert_html_to_docx(args.input_file, args.output_docx, args.encoding, args.source_url,
                                              document_number=args.document_number, output_dir=args.output_dir)
        print(f'DOCX: {output}\nBáo cáo: {report}\nĐã kiểm tra chữ; cần review bố cục và nguồn.')
    except (OSError, ValueError, RuntimeError, etree.LxmlError) as error:
        arguments.exit(1, f'Thất bại: {error}\n')
