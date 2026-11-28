"""Build a source-bound document graph from the project's candidate DOCX corpus."""
import csv
from hashlib import sha256
import re
import unicodedata

from ..document_processing.document_number import normalize_document_number
from ..document_processing.parser.legal_structure_parser import parse_docx
from .chunk_builder import build_chunks, pack_adjacent_chunks
from .source_registry import SourceRegistry

DATASET = 'th1nhng0/vietnamese-legal-documents'
REVISION = '8977887f17be2defae4c5171d55562e1cde7d695'
CORPUS_DIR = 'data/legal-dataset-study/data/lightrag'
CATALOG_PATH = 'data/legal-dataset-study/data/ung_vien_dan_su.csv'
_DOC_TYPE = r'Bộ luật|Luật|Nghị định|Thông tư(?: liên tịch)?|Nghị quyết|Quyết định|Pháp lệnh|Chỉ thị|Lệnh'
_SYMBOL = r'[A-ZĐ][A-ZĐ0-9]*(?:\s*[-–—‑−]\s*[A-ZĐ0-9]+)*'
_CITATION = re.compile(rf'\b(?:{_DOC_TYPE})\s+(?:số\s*[:：]?\s*)?(?P<number>\d{{1,6}}\s*(?:/\s*(?:\d{{4}}\s*/\s*)?{_SYMBOL}(?:\s*/\s*{_SYMBOL})*|[-–—‑−]\s*{_SYMBOL}))\b', re.I)
_ARTICLE = re.compile(r'^\s*Điều\s+\d+[a-zđ]?\s*[.:]\s*', re.I)
_ITEM = re.compile(r'^\s*(?:\d+(?:\.\d+)*[a-zđ]?\s*[.)]|[a-zđ]\))\s+', re.I)
_ACTIONS = {'sửa đổi': 'AMENDS', 'bổ sung': 'SUPPLEMENTS', 'bãi bỏ': 'REPEALS'}
_ACTION = re.compile(r'^(sửa đổi|bổ sung|bãi bỏ)\b', re.I)
_ACTION_ANY = re.compile(r'\b(?:sửa đổi|bổ sung|bãi bỏ)\b', re.I)
_BASIS = re.compile(r'^căn cứ\b', re.I)
_CITES = re.compile(r'\b(?:theo|quy định tại|dẫn chiếu đến)\b', re.I)
_UNIT = r'\d+[a-zđ]?\b'
_POINT = r'(?:[a-zđ]|\d+(?:\.\d+)*)\b'
_SCOPE = re.compile(rf'\b(?:(?:Điều|khoản)\s+{_UNIT}(?:\s*(?:,|và|đến)\s*{_UNIT})*|'
                    rf'điểm\s+{_POINT}(?:\s*(?:,|và|đến)\s*{_POINT})*)', re.I)


def _number(raw):
    if not raw:
        return None
    try:
        return normalize_document_number(raw)
    except ValueError:
        return None


def _corpus_file(root, row):
    path = (root / row['download_path']).resolve()
    directory = (root / CORPUS_DIR).resolve()
    if (row['download_status'] != 'success' or not path.is_relative_to(directory)
            or path.suffix.lower() != '.docx' or not path.is_file()):
        return None
    return path


def _metadata_node(row):
    return dict(id=f'dataset:{row["id"]}', dataset_id=row['id'], number=_number(row['so_ky_hieu']),
                title=row['title'] or None, source=dict(dataset=DATASET, revision=REVISION,
                publisher_note=row['nguon_thu_thap'] or None),
                version=dict(snapshot_sha256=None, issued_date_reported=row['ngay_ban_hanh'] or None,
                             effective_date_reported=row['ngay_co_hieu_luc'] or None,
                             legal_version_verified=False))


def _evidence(document_id, block):
    return dict(document_id=document_id, source_refs=[block['source_ref']], quote=block['text'])


def _relations(document_id, own_number, blocks, *, track_inline_quotes=False):
    """Yield explicit references and numbered directives scoped by an article heading."""
    scope = None
    quote_closer = None
    quote_stack = []
    quote_start = None
    for block in blocks:
        raw = block['text']
        text = unicodedata.normalize('NFC', raw).strip()
        if track_inline_quotes:
            started_inside = bool(quote_stack)
            for char in text:
                if quote_stack and char == quote_stack[-1]:
                    quote_stack.pop()
                elif char in ('“', '"'):
                    quote_stack.append('”' if char == '“' else '"')
            if quote_stack and not started_inside:
                quote_start = block
            if not quote_stack:
                quote_start = None
            if started_inside or text.startswith(('“', '"')):
                continue
        if quote_closer is not None:
            if quote_closer in text:
                quote_closer = None
            continue
        if text.startswith(('“', '"')):
            closer = '”' if text.startswith('“') else '"'
            if closer not in text[1:]:
                quote_closer = closer
            continue
        article = _ARTICLE.match(text)
        instruction = _ITEM.match(text)
        if article:
            scope = None
        lead = text[(article or instruction).end():] if article or instruction else text
        boundary = re.split(r'\bnhư sau\b|[“"]', lead, maxsplit=1, flags=re.I)[0]
        cites = [(m, _number(m['number'])) for m in _CITATION.finditer(boundary)]
        cites = [(m, number) for m, number in cites if number]
        if cites and all(number == own_number for _, number in cites):
            continue  # The document naming itself is not an edge.
        evidence = _evidence(document_id, block)
        action = _ACTION.match(boundary)
        relation = None
        target = None
        scoped_evidence = None
        locators = []
        if action:
            relation = _ACTIONS[action[1].casefold()]
            action_text = boundary[action.end():cites[0][0].start() if cites else len(boundary)]
            # A collective article heading can establish scope without asserting each operation.
            collective_heading = bool(article and re.match(r'\s*,\s*bổ sung\b', action_text, re.I))
            if _ACTION_ANY.search(action_text) and not collective_heading:
                yield dict(reason='COMPOUND_ACTION', evidence=[evidence], mentioned_numbers=[n for _, n in cites])
                continue
            locators = [m.group() for m in _SCOPE.finditer(action_text)]
            if len(cites) == 1:
                target = cites[0][1]
            elif not cites and scope and instruction:
                target, scoped_evidence = scope
            if article and target:
                scope = (target, evidence)
            if collective_heading:
                yield dict(reason='COLLECTIVE_AMENDMENT_HEADING', evidence=[evidence],
                           mentioned_numbers=[n for _, n in cites])
                continue
        elif _BASIS.match(boundary):
            relation = 'BASIS'
            if cites and not re.search(r'\b(?:Luật|Bộ luật|Nghị định|Thông tư)\b',
                                      boundary[_BASIS.match(boundary).end():cites[0][0].start()], re.I):
                target = cites[0][1]  # Later citations may be nested in the basis document's description.
        elif len(cites) == 1 and _CITES.search(boundary[:cites[0][0].start()]):
            relation, target = 'CITES', cites[0][1]
            cue = list(_CITES.finditer(boundary[:cites[0][0].start()]))[-1]
            locators = [m.group() for m in _SCOPE.finditer(boundary[cue.end():cites[0][0].start()])]
        elif not cites:
            continue
        if not relation or not target or target == own_number:
            yield dict(reason='RELATION_OR_TARGET_UNRESOLVED', evidence=[evidence],
                       mentioned_numbers=[n for _, n in cites])
            continue
        yield dict(relation=relation, target_number=target, scope=locators or None,
                   evidence=[evidence, scoped_evidence] if scoped_evidence else [evidence],
                   basis='SCOPED_BY_HEADING' if scoped_evidence else 'EXPLICIT_TEXT')

    if quote_start is not None:
        yield dict(reason='UNCLOSED_QUOTATION', evidence=[_evidence(document_id, quote_start)],
                   mentioned_numbers=[])


def prepare_pilot(root, selection, session):
    """Return an exportable graph and the exact source registry sent to LightRAG."""
    inputs = selection['documents']
    selected = {item['dataset_id']: item for item in inputs}
    if not selected or len(selected) != len(inputs):
        raise ValueError('Select distinct dataset IDs in the pilot.')
    catalog = root / CATALOG_PATH
    with catalog.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    by_id = {row['id']: row for row in rows}
    if len(rows) != len(by_id):
        raise ValueError('Candidate CSV contains duplicate dataset IDs.')
    by_number = {}
    for row in rows:
        number = _number(row['so_ky_hieu'])
        if number:
            by_number.setdefault(number, []).append(row)

    nodes, files, blocks_by_doc, documents, versions = {}, [], {}, [], {}
    for dataset_id, entry in selected.items():
        row = by_id.get(dataset_id)
        path = _corpus_file(root, row) if row else None
        if path is None:
            raise ValueError(f'No tracked corpus DOCX for dataset ID {dataset_id}.')
        metadata = _metadata_node(row)
        if not metadata['number']:
            raise ValueError(f'Pilot document has no usable number: {dataset_id}.')
        document_id = metadata['id']
        digest = sha256(path.read_bytes()).hexdigest()
        if digest != entry['sha256']:
            raise ValueError(f'Pilot DOCX differs from the selected snapshot: {dataset_id}.')
        metadata['version']['snapshot_sha256'] = digest
        metadata['source']['path'] = path.relative_to(root).as_posix()
        metadata['source']['source_page_url'] = entry['source_page_url']
        metadata['full_text_status'] = 'AVAILABLE_IN_PILOT'
        tree = parse_docx(path, document_id=document_id)
        blocks = [dict(source_ref=b['source_ref'], text=b['text']) for b in tree['source_blocks']]
        refs = entry['index_refs']
        if not refs or len(refs) != len(set(refs)):
            raise ValueError(f'Index source references must be distinct: {dataset_id}.')
        index_blocks = [block for block in blocks if block['source_ref'] in refs]
        if len(index_blocks) != len(refs) or any(not b['text'].strip() for b in index_blocks):
            raise ValueError(f'Missing or empty pilot source reference: {dataset_id}.')
        documents.append(dict(document_id=document_id, role='REFERENCE', file_type='DOCX', filename=path.name,
                              blocks=index_blocks))
        blocks_by_doc[document_id] = blocks
        versions[document_id] = digest
        nodes[document_id] = metadata
        files.append(dict(document_id=document_id, path=metadata['source']['path'], sha256=digest,
                          parsed_blocks=len(blocks), indexed_source_refs=refs))

    edges, review = [], []
    for document_id, blocks in blocks_by_doc.items():
        for record in _relations(document_id, nodes[document_id]['number'], blocks):
            if 'reason' in record:
                review.append(dict(source_id=document_id, **record))
                continue
            number = record.pop('target_number')
            matches = by_number.get(number, [])
            if len(matches) > 1:
                review.append(dict(source_id=document_id, reason='AMBIGUOUS_DOCUMENT_NUMBER',
                                   candidate_dataset_ids=[row['id'] for row in matches],
                                   mentioned_numbers=[number], **record))
                continue
            if matches:
                target = _metadata_node(matches[0])
                path = _corpus_file(root, matches[0])
                target['full_text_status'] = 'AVAILABLE_OUTSIDE_PILOT' if path else 'MISSING_FULL_TEXT'
                if path:
                    target['source']['path'] = path.relative_to(root).as_posix()
            else:
                target = dict(id=f'number:{number}', dataset_id=None, number=number, title=None,
                              source=None, version=None, full_text_status='MISSING_FULL_TEXT')
            nodes.setdefault(target['id'], target)
            edges.append(dict(id=f'edge:{len(edges)+1}', source_id=document_id, target_id=target['id'], **record))

    chunks = build_chunks(session, documents, versions, max_chunks=50, max_chars=2000)
    chunks = pack_adjacent_chunks(chunks, 2000)
    output = dict(dataset=DATASET, revision=REVISION, catalog_path=CATALOG_PATH,
                  catalog_sha256=sha256(catalog.read_bytes()).hexdigest(),
                  files=files, nodes=list(nodes.values()), edges=edges, needs_review=review,
                  index_scope='SELECTED_DOCX_BLOCKS_ONLY', legal_effect_verified=False,
                  lightrag_source_map=[dict(file_source=c.file_source, document_id=c.document_id,
                      source_refs=list(c.source_refs), text=c.text) for c in chunks])
    return output, SourceRegistry(chunks, documents)
