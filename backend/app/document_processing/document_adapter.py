"""Map native Parser output to existing source/Clause contracts, without rewriting text."""
from dataclasses import dataclass

from ..context.chunk_builder import documents_from_parsed
from ..schemas.contracts import Clause
from ..schemas.report_validation import validate_payload
from ..schemas.validation import validate_extracted_document


@dataclass
class BoundaryData:
    documents: dict
    clauses: dict
    units: dict


def adapt_documents(parsed) -> BoundaryData:
    documents, clauses, units = {}, {}, {}
    for item, document in zip(parsed, documents_from_parsed(parsed)):
        # Source offsets on PDFs remain those of the converted DOCX.
        if document['file_type'] == 'PDF':
            document['file_type'] = 'PDF_TEXT'
        validate_extracted_document(document)
        did = document['document_id']
        documents[did], clauses[did], units[did] = document, [], {}

        def walk(node, article=None, clause=None):
            kind, label = node['kind'], node.get('label')
            if kind == 'ARTICLE':
                article, clause = label, None
            elif kind == 'CLAUSE':
                clause = label
            if kind in {'ARTICLE', 'CLAUSE', 'POINT'}:
                point = label if kind == 'POINT' else None
                key = tuple(str(v).casefold() if v is not None else None for v in (article, clause, point))
                value = {'unit_id': node['node_id'], 'id': ' / '.join(filter(None, [
                    f'Điều {article}', f'khoản {clause}' if clause else '', f'điểm {point}' if point else ''])),
                    'title': node.get('heading') or '', 'content': node['full_text'],
                    'source_refs': list(node['source_refs'])}
                validate_payload(Clause, value)
                clauses[did].append(value)
                units[did].setdefault(key, []).append(value)
            for child in node.get('children', []):
                # Quoted structures have their own namespace, never V1 targets.
                if child['kind'] not in {'QUOTATION', 'QUOTED_CONTENT'}:
                    walk(child, article, clause)
        for article in item.tree['articles']:
            walk(article)
    return BoundaryData(documents, clauses, units)
