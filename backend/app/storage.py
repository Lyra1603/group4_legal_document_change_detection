"""Request workspaces with OS leases; sweep only old, unlocked owned folders."""
from contextlib import contextmanager
import logging
import os
from pathlib import Path
import re
import shutil
import tempfile
import time
from uuid import uuid4

logger = logging.getLogger(__name__)
OWNED = re.compile(r'^comparison-[0-9a-f]{32}$')


def lock(stream):
    stream.seek(0)
    if os.name == 'nt':
        import msvcrt
        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def unlock(stream):
    stream.seek(0)
    if os.name == 'nt':
        import msvcrt
        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def sweep(root, max_age_seconds=86400):
    root = Path(root).resolve()
    for candidate in root.iterdir():
        if not OWNED.fullmatch(candidate.name) or candidate.is_symlink() or not candidate.is_dir():
            continue
        if root != candidate.resolve().parent:
            continue
        marker = candidate / '.lease'
        try:
            if marker.is_symlink() or time.time() - marker.stat().st_mtime < max_age_seconds:
                continue
            with marker.open('r+b') as stream:
                lock(stream)  # active workers own this lease, even after HTTP disconnect
                unlock(stream)
            shutil.rmtree(candidate)
        except (OSError, FileNotFoundError):
            # Locked/removed by another worker: leave it alone.
            continue


@contextmanager
def workspace(root=None):
    root = Path(root) if root else Path(tempfile.gettempdir()) / 'legal-comparisons'
    root.mkdir(parents=True, exist_ok=True)
    sweep(root)
    directory = root / ('comparison-' + uuid4().hex)
    directory.mkdir()
    marker = directory / '.lease'
    stream = marker.open('w+b')
    stream.write(b'1')
    stream.flush()
    lock(stream)
    try:
        yield directory
    finally:
        unlock(stream)
        stream.close()
        try:
            shutil.rmtree(directory)
        except OSError:
            logger.warning('Temporary workspace cleanup deferred to stale sweep')
