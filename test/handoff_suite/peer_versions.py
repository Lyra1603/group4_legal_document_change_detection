"""Use one integrated checkout for handoff tests and evidence."""
import hashlib
from pathlib import Path
import subprocess

from backend.app.context import context_builder, semantic_bridge
from backend.app.document_processing import document_adapter
from backend.app.document_processing.parser import legal_structure_parser

ROOT = Path(__file__).resolve().parents[2]


def revision(ref):
    return subprocess.check_output(['git', 'rev-parse', '--verify', ref + '^{commit}'],
                                   cwd=ROOT, text=True).strip()


def peers(tho_ref=None, context_ref=None):
    """Return live imports; optional refs assert parity without loading Git blobs."""
    provenance = {'mode': 'INTEGRATED_WORKTREE', 'verified_refs': {}, 'sha256': {}}
    groups = (
        ('Tho', tho_ref, ('backend/app/document_processing',)),
        ('Context', context_ref, ('backend/app/context', 'backend/app/config.py',
                                  'backend/app/schemas', 'backend/app/change_analysis/text_diff.py')),
    )
    for owner, ref, paths in groups:
        if ref:
            commit = revision(ref)
            result = subprocess.run(['git', 'diff', '--quiet', commit, '--', *paths], cwd=ROOT)
            if result.returncode:
                raise ValueError(f'{owner} code in this checkout differs from {commit}. Use an integrated checkout.')
            provenance['verified_refs'][owner] = commit

    modules = (legal_structure_parser, document_adapter, context_builder, semantic_bridge)
    files = [Path(module.__file__).resolve().relative_to(ROOT).as_posix() for module in modules]
    files += ['backend/app/context/lightrag_client.py', 'backend/app/context/source_registry.py',
              'backend/app/context/chunk_builder.py', 'backend/app/change_analysis/text_diff.py',
              'backend/app/schemas/report_validation.py']
    provenance['sha256'] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files}
    return (*modules, provenance)
