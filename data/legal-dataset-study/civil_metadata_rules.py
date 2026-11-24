"""Lượt 2: mở rộng ứng viên dân sự từ metadata, KHÔNG kết luận ngành luật.

Chạy offline: python data/legal-dataset-study/civil_metadata_rules.py
Xem thử: thêm --dry-run. Xem cột/quy tắc/căn cứ: --describe-rules.
Giữ nguyên metadata.csv, 17 cột nguồn và mọi ứng viên đã có; thêm ứng viên
vào ung_vien_dan_su.csv. Bằng chứng/nhóm duyệt nằm ở CSV phụ, thống kê ở JSON.
Không tải toàn văn, không gọi LLM, không loại văn bản cũ/hết hiệu lực.

Các cụm từ dưới đây là cách vận dụng khái niệm pháp lý để tìm ứng viên,
không phải quy tắc phân loại do luật ban hành. Mọi kết quả cần đọc toàn văn
ở lượt 3; nhóm liên quan không được coi là dân sự cốt lõi đã xác nhận.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata

RULE_VERSION = 'round2-0.1.0'
DATASET = {'name': 'th1nhng0/vietnamese-legal-documents', 'config': 'metadata',
           'revision': '8977887f17be2defae4c5171d55562e1cde7d695'}
SOURCES = {
    'BLDS2015': {
        'title': 'Bộ luật Dân sự 91/2015/QH13',
        'url': 'https://rfd.gov.vn/content/vanban/Lists/VBPQ/Attachments/108/91_2015_QH13_Bo%20Luat%20Dan%20su.pdf',
        'locators': 'Điều 1, 3, 4, 8, 14, 17; Phần II; Điều 274, 292, 385, 584, 609',
        'use': 'Khung khái niệm và chủ đề; không quy định thuật toán lọc metadata.',
    },
    'BLTTDS2015': {
        'title': 'Bộ luật Tố tụng dân sự 92/2015/QH13',
        'url': 'https://vanban.chinhphu.vn/?docid=183189&pageid=27160',
        'locators': 'Điều 1',
        'use': 'Tố tụng được giữ ở nhóm liên quan/hỗ trợ, không đồng nhất luật nội dung.',
    },
    'SYSTEM_TEACHING': {
        'title': 'Giáo trình Pháp luật kèm Thông tư 08/2014/TT-BLĐTBXH',
        'url': 'https://congbao.chinhphu.vn/van-ban/thong-tu-so-08-2014-tt-bldtbxh-9844/41836.htm',
        'locators': 'Công báo 513+514 ngày 20/5/2014, trang in 41, mục 2.1.3',
        'use': 'Tài liệu giảng dạy về ngành luật; không phải bảng phân loại dataset bắt buộc.',
    },
    'CYBER2025': {
        'title': 'Luật An ninh mạng năm 2025',
        'url': 'https://vbpl.moj.gov.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=187039',
        'locators': 'Điều 3 khoản 20',
        'use': 'Căn cứ phân biệt thuật ngữ mật mã dân sự với phạm vi luật dân sự.',
    },
}

COLUMNS = ('id', 'title', 'so_ky_hieu', 'ngay_ban_hanh', 'loai_van_ban',
           'ngay_co_hieu_luc', 'ngay_het_hieu_luc', 'nguon_thu_thap',
           'ngay_dang_cong_bao', 'nganh', 'linh_vuc', 'co_quan_ban_hanh',
           'chuc_danh', 'nguoi_ky', 'pham_vi', 'thong_tin_ap_dung', 'tinh_trang_hieu_luc')
COLUMN_POLICY = {
    'id': ('identity', 'Chỉ nối/khử trùng trong cùng dataset và revision, không suy ra ngành luật.'),
    'title': ('topic', 'Lượt 1 đã dùng từ dân sự; lượt 2 mở rộng theo các chủ đề có căn cứ.'),
    'so_ky_hieu': ('identity', 'Chỉ định danh; không suy ra ngành luật từ mã cơ quan hoặc số hiệu.'),
    'ngay_ban_hanh': ('temporal', 'Giữ để chọn phiên bản về sau; không dùng để xác định dân sự.'),
    'loai_van_ban': ('support', 'Chỉ ưu tiên duyệt khi đã có chủ đề; không nhận chỉ vì là Luật/Nghị định.'),
    'ngay_co_hieu_luc': ('temporal', 'Không quyết định chủ đề, không lọc bỏ theo hiệu lực.'),
    'ngay_het_hieu_luc': ('temporal', 'Không quyết định chủ đề; văn bản hết hiệu lực vẫn có thể là V1.'),
    'nguon_thu_thap': ('provenance', 'Nguồn để kiểm chứng, không phải đối tượng điều chỉnh.'),
    'ngay_dang_cong_bao': ('temporal', 'Thông tin công bố, không phải dấu hiệu dân sự.'),
    'nganh': ('topic_support', 'Nhãn quản lý; dùng chủ đề cụ thể hoặc kết hợp ngữ cảnh, không nhận riêng nhãn Tư pháp.'),
    'linh_vuc': ('topic', 'Lượt 1 đã dùng từ dân sự; lượt 2 đọc các chủ đề cụ thể, nhãn nguồn vẫn cần duyệt.'),
    'co_quan_ban_hanh': ('support', 'Chỉ kết hợp chủ đề; Bộ Tư pháp/Tòa án không tự làm văn bản thành dân sự.'),
    'chuc_danh': ('not_domain', 'Chức vụ người ký không chứng minh đối tượng điều chỉnh.'),
    'nguoi_ky': ('not_domain', 'Tên người ký không chứng minh đối tượng điều chỉnh.'),
    'pham_vi': ('territorial', 'Trung ương/địa phương không phải ngành luật; không loại văn bản địa phương.'),
    'thong_tin_ap_dung': ('topic_if_available', 'Có thể xét nội dung mô tả nếu có; thống kê độ đầy đủ, không tự bù dữ liệu trống.'),
    'tinh_trang_hieu_luc': ('temporal', 'Giữ để tra lịch sử, không lọc bỏ văn bản đã hết hiệu lực.'),
}
TOPIC_COLUMNS = ('title', 'linh_vuc', 'nganh', 'thong_tin_ap_dung')


def normalize(value):
    value = unicodedata.normalize('NFC', value or '').casefold()
    value = value.replace('uỷ', 'ủy').replace('thoả', 'thỏa').replace('hoà', 'hòa')
    return re.sub(r'\s+', ' ', value).strip()


def rule(code, group, terms, locator):
    return {'id': code, 'group': group, 'terms': tuple(terms), 'basis': 'BLDS2015',
            'locator': locator, 'interpretation': 'Dấu hiệu để lấy ứng viên, không xác nhận ngành luật.'}


RULES = (
    rule('R2_01_CIVIL_CODE', 'core_candidate', ['bộ luật dân sự', 'quan hệ dân sự', 'quyền dân sự', 'nghĩa vụ dân sự'], 'Điều 1, 3, 4'),
    rule('R2_02_PERSON', 'core_candidate', ['quyền nhân thân', 'năng lực hành vi dân sự', 'giám hộ', 'quyền đối với hình ảnh', 'bí mật đời tư'], 'Điều 17; Chương III'),
    rule('R2_03_PROPERTY', 'core_candidate', ['quyền sở hữu', 'quyền khác đối với tài sản', 'quyền hưởng dụng', 'quyền bề mặt', 'bất động sản liền kề', 'chiếm hữu tài sản'], 'Phần II'),
    rule('R2_04_CONTRACT', 'core_candidate', ['giao dịch dân sự', 'hợp đồng dân sự', 'giao kết hợp đồng', 'thực hiện hợp đồng', 'hợp đồng vay', 'hợp đồng mượn', 'hợp đồng thuê tài sản', 'hợp đồng mua bán', 'hợp đồng tặng cho', 'hợp đồng ủy quyền', 'chuyển giao quyền yêu cầu', 'nghĩa vụ hoàn trả', 'thực hiện công việc không có ủy quyền'], 'Điều 8, 274, 385; Phần III'),
    rule('R2_05_SECURITY', 'core_candidate', ['giao dịch bảo đảm', 'biện pháp bảo đảm thực hiện nghĩa vụ', 'đăng ký biện pháp bảo đảm', 'thế chấp', 'cầm cố', 'bảo lưu quyền sở hữu', 'cầm giữ tài sản', 'đặt cọc', 'ký cược', 'ký quỹ', 'bảo lãnh', 'tín chấp'], 'Điều 292; cần phân biệt điều tiết ngành với quan hệ dân sự'),
    rule('R2_06_TORT', 'core_candidate', ['bồi thường thiệt hại ngoài hợp đồng', 'bồi thường ngoài hợp đồng'], 'Điều 584; Chương XX'),
    rule('R2_07_INHERITANCE', 'core_candidate', ['thừa kế', 'di chúc', 'khai nhận di sản', 'phân chia di sản'], 'Điều 609; Phần IV'),
    rule('R2_08_IP', 'related_candidate', ['sở hữu trí tuệ', 'quyền tác giả', 'quyền liên quan', 'sở hữu công nghiệp', 'chuyển giao công nghệ'], 'Điều 4, Điều 8 khoản 4; chỉ nhận diện khả năng liên quan'),
    rule('R2_09_REAL_ESTATE', 'related_candidate', ['chuyển nhượng quyền sử dụng đất', 'tặng cho quyền sử dụng đất', 'thế chấp quyền sử dụng đất', 'hợp đồng về nhà ở', 'hợp đồng mua bán nhà', 'hợp đồng thuê nhà', 'luật nhà ở', 'luật đất đai', 'luật kinh doanh bất động sản'], 'Điều 4; Chương XVI, chỉ giữ khả năng có phần điều chỉnh giao dịch'),
    rule('R2_10_NOTARY', 'related_candidate', ['công chứng', 'chứng thực hợp đồng', 'chứng thực giao dịch', 'chứng thực chữ ký và chứng thực hợp đồng'], 'Điều 4; Điều 119 về hình thức giao dịch'),
    rule('R2_11_PROTECTION', 'related_candidate', ['tố tụng dân sự', 'thi hành án dân sự', 'trọng tài thương mại', 'hòa giải thương mại', 'thừa phát lại'], 'Điều 14; hỗ trợ bảo vệ/thực hiện quyền, không đồng nhất ngành luật'),
    rule('R2_12_FAMILY', 'related_candidate', ['hôn nhân và gia đình', 'nuôi con nuôi', 'tài sản chung của vợ chồng', 'tài sản của vợ chồng'], 'Điều 4; chỉ đánh dấu lĩnh vực giao thoa để duyệt, không tự mở phạm vi'),
    rule('R2_13_DAMAGE_PRIVACY', 'related_candidate', ['bồi thường thiệt hại', 'trách nhiệm bồi thường', 'bảo vệ dữ liệu cá nhân', 'quyền riêng tư', 'bảo vệ quyền lợi người tiêu dùng'], 'Điều 4, 13, 38, 584, 608; ngữ cảnh có thể thuộc lĩnh vực khác'),
)


def compile_terms(terms):
    return re.compile(r'(?<!\w)(?:' + '|'.join(re.escape(normalize(t)) for t in sorted(terms, key=len, reverse=True)) + r')(?!\w)')


PATTERNS = {r['id']: compile_terms(r['terms']) for r in RULES}
GATE_TERMS = tuple({normalize(term) for definition in RULES for term in definition['terms']} | {'dân sự', 'hợp đồng', 'giao dịch', 'tranh chấp', 'quyền tài sản'})
WEAK_CONTEXT = compile_terms(('hợp đồng', 'giao dịch', 'tranh chấp', 'quyền tài sản'))
JUDICIAL_INDUSTRY = compile_terms(('tư pháp', 'dân sự', 'dân sự - kinh tế'))
JUDICIAL_AGENCY = compile_terms(('bộ tư pháp', 'tòa án nhân dân', 'toà án nhân dân', 'hội đồng thẩm phán'))
FLAGS = {
    'term_collision': compile_terms(('mật mã dân sự', 'phòng thủ dân sự', 'hàng không dân sự')),
    'personnel_or_organization': compile_terms(('tuyển dụng', 'bổ nhiệm', 'công chức', 'viên chức', 'cơ cấu tổ chức', 'chức năng, nhiệm vụ', 'chức năng nhiệm vụ', 'biên chế', 'tiền lương', 'thi đua', 'khen thưởng')),
    'public_management': compile_terms(('xử phạt vi phạm hành chính', 'xử lý vi phạm hành chính', 'ngân sách nhà nước', 'thu hồi đất', 'tái định cư', 'bồi thường nhà nước', 'bồi thường của nhà nước', 'quyền sở hữu toàn dân', 'tài sản công', 'tài sản nhà nước', 'quản lý nhà nước', 'đo đạc địa chính', 'cấp giấy chứng nhận quyền sử dụng đất', 'phí đăng ký', 'lệ phí đăng ký', 'chế độ thu')),
    'specialized_regulation': compile_terms(('bảo lãnh chính phủ', 'bảo lãnh của chính phủ', 'phục hồi môi trường', 'ký quỹ bảo vệ môi trường', 'người lao động đi làm việc ở nước ngoài')),
}
PRIORITY_TYPES = {normalize(t) for t in ('Bộ luật', 'Luật', 'Pháp lệnh', 'Nghị định', 'Thông tư', 'Thông tư liên tịch', 'Nghị quyết', 'Quyết định', 'Nghị quyết liên tịch', 'Sắc lệnh', 'Thông tư liên bộ')}


def classify(row):
    values = {k: normalize(row.get(k, '')) for k in (*TOPIC_COLUMNS, 'co_quan_ban_hanh', 'loai_van_ban')}
    hits = []
    first = 'dân sự' in values['title'] or 'dân sự' in values['linh_vuc']
    if first:
        hits.append({'rule_id': 'R1_DAN_SU', 'basis': 'BLDS2015', 'locator': 'Điều 1; quy tắc từ khóa lịch sử của lượt 1, không kết luận pháp lý',
                     'evidence': [{'column': c, 'value': row.get(c, ''), 'matched_terms': ['dân sự']} for c in ('title', 'linh_vuc') if 'dân sự' in values[c]]})
    groups = set()
    # Cheap literal precheck only skips impossible matches; actual admission still
    # requires the full rules/boundaries below. Avoid dozens of regex scans per row.
    topic_text = '\n'.join(values[c] for c in TOPIC_COLUMNS)
    active_rules = RULES if any(term in topic_text for term in GATE_TERMS) else ()
    for definition in active_rules:
        evidence = []
        for column in TOPIC_COLUMNS:
            found = sorted(set(PATTERNS[definition['id']].findall(values[column])))
            if found:
                evidence.append({'column': column, 'value': row.get(column, ''), 'matched_terms': found})
        if evidence:
            groups.add(definition['group'])
            hits.append({'rule_id': definition['id'], 'basis': definition['basis'], 'locator': definition['locator'], 'evidence': evidence})
    context_evidence = []
    weak = sorted(set(WEAK_CONTEXT.findall(values['title'])))
    for column, pattern in (('nganh', JUDICIAL_INDUSTRY), ('co_quan_ban_hanh', JUDICIAL_AGENCY)):
        found = sorted(set(pattern.findall(values[column])))
        if found:
            context_evidence.append({'column': column, 'value': row.get(column, ''), 'matched_terms': found})
    if weak and context_evidence:
        groups.add('related_candidate')
        hits.append({'rule_id': 'R2_14_CONTEXT_COMBINATION', 'basis': 'BLDS2015', 'locator': 'Điều 1, 4; kết hợp yếu do dự án đề xuất, phải đọc toàn văn',
                     'evidence': [{'column': 'title', 'value': row.get('title', ''), 'matched_terms': weak}] + context_evidence})
    if values['nganh'] in ('dân sự', 'dân sự - kinh tế'):
        groups.add('related_candidate')
        hits.append({'rule_id': 'R2_15_INDUSTRY_LABEL', 'basis': 'BLDS2015', 'locator': 'Điều 1, 4; nhãn metadata chưa được xác minh',
                     'evidence': [{'column': 'nganh', 'value': row.get('nganh', ''), 'matched_terms': [values['nganh']]}]})
    flags = [name for name, pattern in FLAGS.items() if pattern.search(values['title'])]
    if 'term_collision' in flags:
        # This is not a deletion rule. Preserve R1 rows and flag contradictory hints.
        group, priority = 'scope_conflict_review', 'low'
    elif 'core_candidate' in groups:
        group, priority = 'core_candidate', 'high'
    elif groups:
        group, priority = 'related_candidate', 'medium'
    else:
        group, priority = 'round1_or_existing_review', 'low'
    if flags and 'term_collision' not in flags:
        group, priority = 'mixed_context_review', 'low'
    kind = row.get('loai_van_ban', '')
    if group == 'related_candidate' and values['loai_van_ban'] not in PRIORITY_TYPES:
        priority = 'low'
    return {'phase1': first, 'phase2': bool(groups), 'group': group, 'priority': priority,
            'flags': flags, 'hits': hits, 'context': context_evidence,
            'type_context': {'column': 'loai_van_ban', 'value': kind,
                             'form_supported_for_priority': values['loai_van_ban'] in PRIORITY_TYPES,
                             'note': 'Hình thức chỉ giúp ưu tiên; chưa xác nhận văn bản cụ thể là VBQPPL.'}}


def _load(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames
        if columns is None or len(columns) != len(set(columns)) or 'id' not in columns:
            raise ValueError(f'CSV thiếu header/id hoặc trùng tên cột: {path}')
        rows, identities = [], set()
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f'CSV sai số cột: {path}')
            identity = row['id']
            if not identity or identity in identities:
                raise ValueError(f'ID trống/trùng trong {path}: {identity!r}')
            identities.add(identity)
            rows.append(row)
    return columns, rows


def _csv_bytes(columns, rows):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=columns, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode('utf-8-sig')


def _publish(files):
    staged = []
    try:
        for path, content in files:
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(prefix='.civil_round2_', dir=path.parent, delete=False) as handle:
                temporary = Path(handle.name)
                staged.append((temporary, path))
                handle.write(content)
        # Each replacement is atomic. metadata.csv is never an output target.
        for temporary, path in staged:
            os.replace(temporary, path)
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)


def expand_candidates(metadata_path, candidates_path, *, evidence_path=None, report_path=None, dry_run=False):
    metadata_path, candidates_path = Path(metadata_path).resolve(), Path(candidates_path).resolve()
    evidence_path = Path(evidence_path).resolve() if evidence_path else candidates_path.with_name(candidates_path.stem + '_luot2_evidence.csv')
    report_path = Path(report_path).resolve() if report_path else candidates_path.with_name(candidates_path.stem + '_luot2_report.json')
    if len({metadata_path, candidates_path, evidence_path, report_path}) != 4:
        raise ValueError('Các đường dẫn input/output phải khác nhau; không ghi đè metadata.csv.')
    metadata_bytes = metadata_path.read_bytes()
    candidate_before = candidates_path.read_bytes() if candidates_path.exists() else None
    columns, metadata = _load(metadata_path)
    if set(columns) != set(COLUMNS):
        raise ValueError('Metadata phải có đúng 17 cột của snapshot đã chốt; cần review nếu schema thay đổi.')
    registry = {r['id']: r for r in metadata}
    existing_columns, existing = _load(candidates_path) if candidates_path.exists() else (columns, [])
    if existing_columns != columns:
        raise ValueError('Ứng viên cũ không cùng schema metadata; không tự bỏ cột hoặc ghi đè.')
    for row in existing:
        if row['id'] not in registry or row != registry[row['id']]:
            raise ValueError(f'Ứng viên {row["id"]} không khớp metadata hiện tại; kiểm tra nguồn/revision trước khi ghép.')
    existing_ids = {r['id'] for r in existing}
    selected, results, first_ids = [], {}, set()
    filled = Counter()
    for row in metadata:
        filled.update(column for column, value in row.items() if value.strip())
        result = classify(row)
        if result['phase1']:
            first_ids.add(row['id'])
        if result['phase1'] or result['phase2'] or row['id'] in existing_ids:
            results[row['id']] = result
            selected.append(row)
    # Preserve old row order/values, append new rows in the metadata source order.
    combined = existing + [r for r in selected if r['id'] not in existing_ids]
    evidence_rows = []
    for row in combined:
        result = results[row['id']]
        evidence_rows.append({
            'id': row['id'], 'title': row['title'], 'so_ky_hieu': row['so_ky_hieu'],
            'selection_round': '1' if result['phase1'] else '2' if result['phase2'] else 'existing_only',
            'proposed_group': result['group'], 'download_priority': result['priority'],
            'review_status': 'needs_fulltext_review', 'rule_version': RULE_VERSION,
            'rule_ids': ';'.join(hit['rule_id'] for hit in result['hits']),
            'review_flags': ';'.join(result['flags']),
            'legal_basis_ids': ';'.join(sorted({hit['basis'] for hit in result['hits']} | ({'CYBER2025'} if 'mật mã dân sự' in normalize(row['title']) else set()))),
            'evidence_json': json.dumps(result['hits'], ensure_ascii=False, separators=(',', ':')),
            'context_json': json.dumps({'supporting_context': result['context'], 'document_type': result['type_context']}, ensure_ascii=False, separators=(',', ':')),
        })
    ids = {r['id'] for r in combined}
    summary = {'metadata_rows': len(metadata), 'round1_rows': len(first_ids),
               'previous_candidate_rows': len(existing), 'added_this_run': len(ids - existing_ids),
               'added_beyond_round1': len(ids - first_ids), 'total_candidates': len(combined),
               'preserved_all_existing': existing_ids <= ids,
               'groups': dict(Counter(r['proposed_group'] for r in evidence_rows)),
               'priorities': dict(Counter(r['download_priority'] for r in evidence_rows)),
               'not_selected_is_not_legal_exclusion': True}
    report = {
        'rule_version': RULE_VERSION, 'dataset': DATASET, 'summary': summary,
        'metadata_sha256': hashlib.sha256(metadata_bytes).hexdigest(),
        'candidate_csv_columns_unchanged': columns, 'sources': SOURCES,
        'rule_hit_counts': dict(Counter(hit['rule_id'] for result in results.values() for hit in result['hits'])),
        'new_admission_columns': dict(Counter(column for row in combined if row['id'] not in first_ids
                                            for column in {e['column'] for hit in results[row['id']]['hits']
                                                           if hit['rule_id'].startswith('R2_') for e in hit['evidence']})),
        'column_policy': {c: {'role': COLUMN_POLICY[c][0], 'reason': COLUMN_POLICY[c][1],
                               'observed_nonempty': filled[c], 'observed_empty': len(metadata) - filled[c],
                               'active_topic_data': c in TOPIC_COLUMNS and bool(filled[c])} for c in columns},
        'rules': list(RULES) + [
            {'id': 'R2_14_CONTEXT_COMBINATION', 'condition': 'title có chủ đề yếu VÀ nganh/cơ quan có ngữ cảnh tư pháp', 'basis': 'BLDS2015 Điều 1, 4; chính sách ứng viên cần duyệt'},
            {'id': 'R2_15_INDUSTRY_LABEL', 'condition': 'nganh có toàn giá trị dân sự hoặc dân sự - kinh tế', 'basis': 'Nhãn nguồn hỗ trợ; không phải kết luận pháp lý'}],
        'review_flags_policy': {key: {'pattern': pattern.pattern, 'effect': 'Chỉ chuyển nhóm chờ duyệt/giảm ưu tiên; không xóa ứng viên.',
                                     'basis': 'BLDS2015 Điều 1, 4; dấu hiệu ngữ cảnh do dự án đề xuất, không kết luận ngành luật.'}
                                for key, pattern in FLAGS.items()},
        'limitations': ['Chỉ sàng lọc metadata, chưa đọc toàn văn hoặc xác nhận ngành luật.',
                        'Không dùng số hiệu/ngày/hiệu lực/tên người ký để quyết định ngành luật.',
                        'Giữ toàn bộ ứng viên cũ kể cả nghi nhiễu; chưa nạp kho hoặc tải toàn văn.',
                        'Ngành trong dataset là nhãn quản lý; thiếu dữ liệu không phải bằng chứng loại.',
                        'Liên quan/hỗ trợ hoặc giao thoa không đồng nghĩa nằm trong phạm vi dân sự đã duyệt.',
                        'Không công bố precision/recall khi chưa có nhãn kiểm chứng độc lập.'],
    }
    if not dry_run:
        if metadata_path.read_bytes() != metadata_bytes:
            raise RuntimeError('Metadata thay đổi trong lúc chạy; dừng để tránh ghép sai snapshot.')
        candidate_now = candidates_path.read_bytes() if candidates_path.exists() else None
        if candidate_now != candidate_before:
            raise RuntimeError('CSV ứng viên thay đổi trong lúc chạy; dừng để bảo toàn cập nhật của người khác.')
        evidence_columns = list(evidence_rows[0]) if evidence_rows else ['id', 'title', 'so_ky_hieu', 'selection_round', 'proposed_group', 'download_priority', 'review_status', 'rule_version', 'rule_ids', 'review_flags', 'legal_basis_ids', 'evidence_json', 'context_json']
        _publish([(candidates_path, _csv_bytes(columns, combined)),
                  (evidence_path, _csv_bytes(evidence_columns, evidence_rows)),
                  (report_path, json.dumps(report, ensure_ascii=False, indent=2).encode('utf-8'))])
    return report


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='backslashreplace')
    default = Path(__file__).resolve().parent / 'data'
    parser = argparse.ArgumentParser(description='Lượt 2 mở rộng ứng viên dân sự từ metadata; không tải toàn văn.')
    parser.add_argument('--metadata', type=Path, default=default / 'metadata.csv')
    parser.add_argument('--candidates', type=Path, default=default / 'ung_vien_dan_su.csv')
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--dry-run', action='store_true', help='Chỉ thống kê, không ghi file.')
    parser.add_argument('--describe-rules', action='store_true', help='In cột, căn cứ và quy tắc; không đọc/ghi dữ liệu.')
    args = parser.parse_args()
    if args.describe_rules:
        print(json.dumps({'column_policy': COLUMN_POLICY, 'sources': SOURCES, 'rules': RULES,
                          'additional_rules': {'R2_14_CONTEXT_COMBINATION': 'title có hợp đồng/giao dịch/tranh chấp/quyền tài sản VÀ nganh/cơ quan có ngữ cảnh tư pháp',
                                               'R2_15_INDUSTRY_LABEL': 'Toàn giá trị nganh là dân sự hoặc dân sự - kinh tế'},
                          'review_flags': {key: pattern.pattern for key, pattern in FLAGS.items()}}, ensure_ascii=False, indent=2))
        return
    try:
        result = expand_candidates(args.metadata, args.candidates, evidence_path=args.evidence, report_path=args.report, dry_run=args.dry_run)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f'Thất bại: {error}\n')
    print(json.dumps(result['summary'], ensure_ascii=False, indent=2))
    print('Dry-run: chưa ghi dữ liệu.' if args.dry_run else 'Đã cập nhật ứng viên, evidence CSV và report JSON. Metadata gốc không bị sửa.')


if __name__ == '__main__':
    main()
