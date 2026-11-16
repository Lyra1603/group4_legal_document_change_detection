"""Load explicitly selected peer Git blobs without changing the working tree."""
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def revision(ref):
    return subprocess.check_output(['git', 'rev-parse', '--verify', ref + '^{commit}'],
                                   cwd=ROOT, text=True).strip()


def load_blob(commit, path, name, *, dependencies=None):
    source = subprocess.check_output(['git', 'show', f'{commit}:{path}'], cwd=ROOT)
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader=None))
    module.__file__ = f'git:{commit}:{path}'
    # Dataclasses inspect sys.modules while the class is being defined.
    with patch.dict(sys.modules, {name: module, **(dependencies or {})}):
        exec(compile(source, module.__file__, 'exec'), module.__dict__)
    return module, {'commit': commit, 'path': path, 'sha256': hashlib.sha256(source).hexdigest()}


def peers(tho_ref='origin/tho/document_processing', context_ref='origin/ducanh/context-integration'):
    tho, context = revision(tho_ref), revision(context_ref)
    parser, p = load_blob(tho, 'backend/app/document_processing/parser/legal_structure_parser.py',
                          'backend.app.document_processing.parser._handoff_peer')
    adapter, a = load_blob(tho, 'backend/app/document_processing/document_adapter.py',
                           'backend.app.document_processing._handoff_adapter')
    consumer, c = load_blob(context, 'backend/app/context/context_builder.py',
                            'backend.app.context._handoff_consumer')
    bridge, b = load_blob(context, 'backend/app/context/semantic_bridge.py',
                          'backend.app.context._handoff_bridge',
                          dependencies={'backend.app.context.context_builder': consumer})
    return parser, adapter, consumer, bridge, {'Tho': tho, 'Context': context, 'blobs': [p, a, c, b]}
