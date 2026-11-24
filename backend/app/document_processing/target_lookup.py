"""Exact-number lookup for the shared demo. The catalog is local and source-bound."""
import csv
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from .amendment_linker import base_document_numbers, iter_directives, target_hint
from .document_number import identify_document_number, normalize_document_number

# The repository's previously exercised pair. These digests identify the exact
# demo snapshot, never a generally valid legal version or an effective date.
DEMO_AMENDMENT = '0f9a379a16e409430cfb2a4b45d3984d8d045ecf9fc38242a60fe5b952606417'
DEMO_BASE = 'fa8cda22bf5babe3681be68e342944c6a7406576a62777535bd822f84371b594'
DEMO_NUMBER = '22/2019/TT-NHNN'


@dataclass(frozen=True)
class Candidate:
    number: str
    path: Path
    digest: str
    title: str
    date: str
    source: str
    version_note: str

    @property
    def id(self):
        return sha256(f'{self.number}:{self.digest}'.encode()).hexdigest()

    def matches_file(self):
        return self.path.is_file() and file_digest(self.path) == self.digest

    def summary(self):
        return dict(id=self.id, filename=self.path.name, title=self.title,
                    document_date=self.date, source=self.source, version_note=self.version_note)


def file_digest(path):
    with path.open('rb') as stream:
        return sha256_stream(stream)


def sha256_stream(stream):
    digest = sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        digest.update(block)
    return digest.hexdigest()


def load_catalog(root):
    data = (root / 'data').resolve()
    demo_base = (data / 'raw/case_02/22_2019_TT-NHNN_v1.docx').resolve()
    candidates = [
        Candidate(DEMO_NUMBER, demo_base, DEMO_BASE, 'Thông tư 22/2019/TT-NHNN', '',
                  'data/raw/case_02', 'Bản dùng trong cặp demo đã kiểm chứng.')
    ] if demo_base.is_relative_to(data) else []
    manifest = data / 'manifest.csv'
    if not manifest.is_file():
        return [candidate for candidate in candidates if candidate.matches_file()]
    with manifest.open(encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream):
            if row['role'] != 'BASE':
                continue
            path = (root / row['local_path']).resolve()
            if not path.is_relative_to(data) or path.suffix.lower() not in {'.docx', '.pdf'}:
                continue
            try:
                number = normalize_document_number(row['document_number'])
            except ValueError:
                continue
            candidates.append(Candidate(number, path, row['sha256'], row['document_title'],
                                        row['document_date'], row['source_page_url'], row['content_state_note']))
    return list({candidate.id: candidate for candidate in candidates if candidate.matches_file()}.values())


def discover_targets(parsed, catalog):
    by_number = {}
    for entry in catalog:
        by_number.setdefault(entry.number, []).append(entry)
    fixture = file_digest(parsed.document.path) == DEMO_AMENDMENT
    groups, unresolved = {}, []
    for block, text, scope, _ in iter_directives(parsed.tree['source_blocks']):
        codes, names = target_hint(text, scope)
        source = dict(document_id='s', source_refs=[block['source_ref']], quote=block['text'])
        if len(codes) != 1:
            unresolved.append(dict(instruction=source, mentioned_numbers=codes, mentioned_names=names,
                                   reason='AMBIGUOUS_TARGET' if len(codes) > 1 else 'TARGET_NUMBER_UNKNOWN'))
            continue
        number = codes[0]
        groups.setdefault(number, []).append(source)

    targets = []
    for number, instructions in groups.items():
        matches = by_number.get(number, [])
        auto = fixture and number == DEMO_NUMBER and len(matches) == 1 and matches[0].digest == DEMO_BASE
        status = 'AUTO_MATCH' if auto else 'NEEDS_CONFIRMATION' if matches else 'NEEDS_V1'
        targets.append(dict(document_number=number, status=status, instructions=instructions,
                            candidates=[entry.summary() for entry in matches]))
    return dict(targets=targets, unresolved=unresolved,
                issues=[] if groups or unresolved else ['INSTRUCTIONS_NOT_RECOGNIZED'])


def base_identity(parsed, catalog):
    """Use the V1 header, or verified bytes of a catalog document without a header."""
    header, numbers = base_document_numbers(parsed.tree['source_blocks'])
    if not numbers:
        try:
            number, _ = identify_document_number(header)
        except ValueError:
            return None
        if number:
            numbers = [number]
    if numbers:
        return numbers[0] if len(numbers) == 1 else None

    digest = file_digest(parsed.document.path)
    identities = {entry.number for entry in catalog if entry.digest == digest}
    return next(iter(identities)) if len(identities) == 1 else None
