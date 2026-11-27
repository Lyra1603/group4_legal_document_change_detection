"""Tải ứng viên, mặc định chuyển HTML tạm thành DOCX theo số hiệu.

CLI yêu cầu --id hoặc --all-candidates. --dry-run chỉ lập kế hoạch offline.
--html-only bật lưu HTML và .source.json. --report yêu cầu báo cáo tổng.
Hàm download_documents mặc định convert_docx=False để giữ caller cũ.
CLI mặc định bật DOCX. Kiểm tra trùng chưa xác nhận nội dung thuộc dân sự.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import io
import json
import os
import tempfile
from pathlib import Path
import re
import sys
import webbrowser
import zipfile

DATASET = 'th1nhng0/vietnamese-legal-documents'
REVISION = '8977887f17be2defae4c5171d55562e1cde7d695'
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_CANDIDATES = SCRIPT_DIR / 'data/ung_vien_dan_su.csv'
DEFAULT_MANIFEST = REPO_ROOT / 'data/manifest.csv'
_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]*\Z')


class _VisibleHTML(HTMLParser):
    """Kiểm tra có chữ trong body; không thực thi HTML, tải ảnh hoặc CSS."""
    IGNORED = {'head', 'title', 'script', 'style', 'noscript', 'template'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ignored = 0
        self.in_body = False
        self.has_body = False
        self.body_text = []
        self.fragment_text = []

    def handle_starttag(self, tag, attrs):
        if tag in self.IGNORED:
            self.ignored += 1
        if tag == 'body':
            self.has_body = self.in_body = True

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in self.IGNORED:
            self.ignored = max(0, self.ignored - 1)
        if tag == 'body':
            self.in_body = False

    def handle_data(self, value):
        if not self.ignored:
            self.fragment_text.append(value)
            if self.in_body:
                self.body_text.append(value)


def validate_html(content):
    if not isinstance(content, str) or not content.strip():
        raise ValueError('Nguồn HTML rỗng.')
    reader = _VisibleHTML()
    reader.feed(content)
    reader.close()
    text = ''.join(reader.body_text if reader.has_body else reader.fragment_text)
    visible = re.sub(r'[\s\u200b\ufeff]+', '', text)
    if not visible:
        raise ValueError('HTML không có chữ trong body; không lưu khung HTML trắng/nguồn chỉ có ảnh.')
    return {'has_body': reader.has_body, 'non_whitespace_characters': len(visible)}


def load_candidates(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not {'id', 'title', 'so_ky_hieu'} <= set(reader.fieldnames):
            raise ValueError('CSV ứng viên phải có id, title và so_ky_hieu.')
        rows = {}
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError('CSV ứng viên có dòng sai số cột.')
            identity = row.get('id', '')
            if not _ID.fullmatch(identity) or identity in rows:
                raise ValueError(f'ID không hợp lệ hoặc bị trùng trong CSV: {identity!r}')
            rows[identity] = row
    return rows


def _inside(path, root):
    return path.resolve().is_relative_to(root.resolve())


def _scan_target(root):
    if root.exists() and not root.is_dir():
        raise ValueError('Vị trí đích phải là thư mục.')
    files = {}
    if root.exists():
        for path in root.rglob('*'):
            if path.is_file() and _inside(path, root):
                files.setdefault(path.name.casefold(), []).append(path)
    return files


def _manifest_records(manifest_path, manifest_root, output):
    records = {}
    if manifest_path is None or not Path(manifest_path).is_file():
        return records
    with Path(manifest_path).open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not {'document_id', 'local_path', 'parent_files'} <= set(reader.fieldnames):
            raise ValueError('Manifest phải có document_id, local_path và parent_files.')
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError('Manifest có dòng sai số cột.')
            doc_id = row.get('document_id', '')
            if not doc_id.startswith(('th1nhng0:', DATASET + ':')):
                continue
            identity = doc_id.rsplit(':', 1)[-1]
            local_path = row.get('local_path', '')
            if not local_path:
                continue
            path = Path(local_path)
            path = path if path.is_absolute() else Path(manifest_root) / path
            if path.is_file() and _inside(path, output):
                records.setdefault(identity, []).append((path, row))
    return records


def _check_existing_file(path, expected_hash=None):
    try:
        raw = path.read_bytes()
    except OSError as error:
        return 'skipped_unverified', f'File đã có nhưng chưa đọc kiểm tra được: {error}'
    if not raw:
        return 'existing_invalid', 'File đã có nhưng rỗng; giữ nguyên để kiểm tra.'
    try:
        if path.suffix.casefold() in ('.html', '.htm'):
            validate_html(raw.decode('utf-8-sig'))
        elif path.suffix.casefold() == '.docx':
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                if 'word/document.xml' not in archive.namelist():
                    raise ValueError('Không có nội dung Word.')
        elif path.suffix.casefold() == '.pdf' and not raw.startswith(b'%PDF-'):
            raise ValueError('Không có chữ ký định dạng PDF.')
    except (ValueError, UnicodeError, zipfile.BadZipFile) as error:
        return 'existing_invalid', f'File đã có nhưng không đọc được nội dung: {error}'
    if expected_hash and hashlib.sha256(raw).hexdigest() != expected_hash:
        return 'existing_invalid', 'File đã có nhưng hash không khớp nguồn đã ghi.'
    return ('skipped_existing', 'Đã có file khớp bản ghi nguồn và hash.') if expected_hash else (
        'skipped_unverified', 'Đã có file; chưa có đủ bằng chứng cùng dataset/revision. Không tải đè.')


def _existing(row, output, files, registered):
    identity = row['id']
    for path, record in registered.get(identity, []):
        provenance = record.get('parent_files', '')
        if DATASET + '@' + REVISION + ':' not in provenance:
            return {'status': 'existing_identity_conflict', 'path': str(path),
                    'reason': 'Manifest có ID này trong thư mục đích nhưng chưa xác nhận cùng revision.'}
        status, reason = _check_existing_file(path, record.get('sha256'))
        return {'status': status, 'path': str(path), 'reason': reason}
    html_name = f'vbpl-{identity}.html'
    for path in sorted(files.get(html_name.casefold(), [])):
        sidecar = path.with_suffix('.source.json')
        expected_hash = None
        if sidecar.exists():
            try:
                source = json.loads(sidecar.read_text(encoding='utf-8'))
            except (OSError, ValueError) as error:
                return {'status': 'existing_invalid', 'path': str(path), 'reason': f'Không đọc được bản ghi nguồn: {error}'}
            if not isinstance(source, dict):
                return {'status': 'existing_invalid', 'path': str(path), 'reason': 'Bản ghi nguồn phải là JSON object.'}
            if (source.get('dataset'), source.get('revision'), str(source.get('id'))) != (DATASET, REVISION, identity):
                return {'status': 'existing_identity_conflict', 'path': str(path), 'reason': 'Bản ghi nguồn khác dataset/revision/ID cần tải.'}
            expected_hash = source.get('sha256')
        status, reason = _check_existing_file(path, expected_hash)
        return {'status': status, 'path': str(path), 'reason': reason}
    # Filename-only matches are possible duplicates, never verified identity.
    number = re.sub(r'\s+', '', row.get('so_ky_hieu', '')).translate(str.maketrans({'–': '-', '—': '-'}))
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', number)
    possible_names = [f'vbpl-{identity}.docx', f'vbpl-{identity}.pdf']
    if safe:
        possible_names += [safe + extension for extension in ('.docx', '.pdf', '.html', '.htm')]
    for name in dict.fromkeys(possible_names):
        for path in sorted(files.get(name.casefold(), [])):
            status, reason = _check_existing_file(path)
            return {'status': status, 'path': str(path), 'reason': reason}
    sidecar = output / f'vbpl-{identity}.source.json'
    target = output / html_name
    if sidecar.exists() or target.is_symlink():
        return {'status': 'existing_invalid', 'path': str(sidecar if sidecar.exists() else target),
                'reason': 'Đầu ra/bản ghi nguồn đã tồn tại nhưng không đầy đủ; cần kiểm tra trước khi tải lại.'}
    return None


def _stream_documents():
    from datasets import load_dataset
    return load_dataset(DATASET, 'content', split='data', streaming=True, revision=REVISION)


def _save(content, row, output):
    validation = validate_html(content)
    raw = content.encode('utf-8')
    source = {'dataset': DATASET, 'revision': REVISION, 'config': 'content', 'split': 'data',
              'id': row['id'], 'so_ky_hieu': row.get('so_ky_hieu', ''), 'title': row.get('title', ''),
              'downloaded_at': datetime.now(timezone.utc).isoformat(),
              'source_url': f'https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/data/content.parquet',
              'sha256': hashlib.sha256(raw).hexdigest(), 'validation': validation}
    output.mkdir(parents=True, exist_ok=True)
    path = output / f'vbpl-{row["id"]}.html'
    sidecar = path.with_suffix('.source.json')
    created = []
    try:
        for target, payload in ((path, raw), (sidecar, json.dumps(source, ensure_ascii=False, indent=2).encode('utf-8'))):
            # Exclusive creation also protects against a file appearing after planning.
            with target.open('xb') as handle:
                created.append(target)
                handle.write(payload)
    except Exception:
        for target in created:
            target.unlink(missing_ok=True)
        raise
    return path



class DocxConversionError(ValueError):
    pass


def _convert_source(source, row, output):
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from backend.app.document_processing.html_to_docx import convert_html_to_docx
    try:
        target, _ = convert_html_to_docx(source, document_number=row.get('so_ky_hieu', ''),
                                          output_dir=output, write_report=False)
    except FileExistsError:
        raise
    except Exception as error:
        raise DocxConversionError(str(error)) from error
    return target


def _save_docx(content, row, output):
    validate_html(content)
    # HTML is temporary and never written into the download directory.
    with tempfile.TemporaryDirectory(prefix='pocs_html_') as temporary:
        source = Path(temporary) / 'source.html'
        source.write_text(content, encoding='utf-8')
        return _convert_source(source, row, output)


def _convert_result(result, row, dry_run):
    source = Path(result['path'])
    if source.suffix.lower() != '.html':
        return
    if dry_run and result['status'] in {'would_download', 'skipped_existing'}:
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from backend.app.document_processing.document_number import normalize_document_number
        try:
            number = normalize_document_number(row.get('so_ky_hieu', ''))
        except ValueError as error:
            result.update(status='conversion_error', reason=f'Chưa thể đặt tên DOCX: {error}')
            return
        status = 'would_download_and_convert' if result['status'] == 'would_download' else 'would_convert'
        target = source.parent / (number.replace('/', '_') + '.docx')
        result.update(status=status, path=str(target),
                      reason='Dự kiến tải và chuyển DOCX theo số hiệu; thư mục đích chỉ lưu DOCX.')
    elif result['status'] == 'skipped_existing':
        try:
            target = _convert_source(source, row, source.parent)
            result.update(status='converted', path=str(target), reason='Đã chuyển HTML có sẵn thành DOCX.')
        except Exception as error:
            result.update(status='conversion_error', reason=f'{type(error).__name__}: {error}')




DOWNLOAD_COLUMNS = ('download_status', 'download_result', 'download_path')


class CandidateUpdateError(RuntimeError):
    """Stop instead of overwriting a concurrently edited candidate CSV."""


def relative_download_path(target):
    return Path(os.path.relpath(Path(target).resolve(), REPO_ROOT.resolve())).as_posix() if target else ''


class CandidateProgress:
    def __init__(self, path):
        self.path = Path(path)
        self.expected = self.path.read_bytes()

    def record(self, result):
        try:
            current = self.path.read_bytes()
            if current != self.expected:
                raise CandidateUpdateError('Candidate CSV changed during download; refusing to overwrite.')
            reader = csv.DictReader(io.StringIO(current.decode('utf-8-sig')))
            columns = list(reader.fieldnames or [])
            rows = list(reader)
            columns.extend(c for c in DOWNLOAD_COLUMNS if c not in columns)
            matches = [r for r in rows if r['id'] == result['id']]
            if len(matches) != 1:
                raise CandidateUpdateError('Candidate ID is missing or duplicated.')
            row = matches[0]
            row['download_status'] = 'success' if result['status'] in {
                'downloaded', 'converted', 'skipped_existing'} else 'failed'
            row['download_result'] = result['status'] + ': ' + result.get('reason', '')
            # Resolve against the checkout root when reading this CSV on another machine.
            row['download_path'] = relative_download_path(result.get('path', ''))
            text = io.StringIO(newline='')
            writer = csv.DictWriter(text, fieldnames=columns, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
            payload = text.getvalue().encode('utf-8-sig')
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(dir=self.path.parent, suffix='.tmp', delete=False) as handle:
                    temporary = Path(handle.name)
                    handle.write(payload)
                    handle.flush()
                    os.fsync(handle.fileno())
                if self.path.read_bytes() != current:
                    raise CandidateUpdateError('Candidate CSV changed during update; refusing to overwrite.')
                os.replace(temporary, self.path)
                self.expected = payload
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        except CandidateUpdateError:
            raise
        except Exception as error:
            raise CandidateUpdateError(f'Cannot save candidate status: {error}') from error


def download_documents(ids=None, *, all_candidates=False, candidates_path=DEFAULT_CANDIDATES,
                       output_dir=None, limit=None, dry_run=False,
                       manifest_path=DEFAULT_MANIFEST, manifest_root=REPO_ROOT, stream_factory=None, convert_docx=False):
    if bool(ids) == bool(all_candidates):
        raise ValueError('Chọn --id hoặc --all-candidates, không dùng đồng thời hoặc bỏ cả hai.')
    if limit is not None and limit < 1:
        raise ValueError('--limit phải lớn hơn 0.')
    candidates = load_candidates(candidates_path)
    ids = [ids] if isinstance(ids, str) else ids
    requested = list(candidates) if all_candidates else list(dict.fromkeys(str(identity) for identity in ids))
    unknown = [identity for identity in requested if identity not in candidates]
    if unknown:
        raise ValueError('ID không có trong danh sách ứng viên; không tải: ' + ', '.join(unknown))
    output = Path(output_dir).resolve() if output_dir is not None else SCRIPT_DIR / 'data'
    relative_download_path(output)  # Reject cross-drive targets before downloading/writing.
    files = _scan_target(output)
    registered = _manifest_records(manifest_path, manifest_root, output)
    progress = None if dry_run else CandidateProgress(candidates_path)

    def finish(result):
        if convert_docx:
            _convert_result(result, candidates[result['id']], dry_run)
        if progress is not None:
            progress.record(result)

    results, pending = [], {}
    for identity in requested:
        row = candidates[identity]
        old = _existing(row, output, files, registered)
        result = {'id': identity, 'so_ky_hieu': row.get('so_ky_hieu', ''), 'title': row.get('title', '')}
        if old:
            result.update(old)
            if not dry_run:
                finish(result)
        else:
            result.update(status='would_download' if dry_run else 'pending', path=str(output / f'vbpl-{identity}.html'))
            pending[identity] = result
        results.append(result)
        if limit is not None and len(pending) >= limit:
            break
    warnings = []
    if pending and not dry_run:
        documents = None
        try:
            documents = iter((stream_factory or _stream_documents)())
            for document in documents:
                identity = str(document.get('id', ''))
                if identity not in pending:
                    continue
                result = pending.pop(identity)
                try:
                    # Recheck the target tree after waiting for network retrieval.
                    old = _existing(candidates[identity], output, _scan_target(output),
                                    _manifest_records(manifest_path, manifest_root, output))
                    if old:
                        result.update(old)
                    else:
                        content = document.get('content_html') or ''
                        if convert_docx:
                            path = _save_docx(content, candidates[identity], output)
                            result.update(status='converted', path=str(path), reason='Đã lưu DOCX theo số hiệu.')
                        else:
                            path = _save(content, candidates[identity], output)
                            result.update(status='downloaded', path=str(path), reason='Đã lưu HTML và bản ghi nguồn.')
                except DocxConversionError as error:
                    result.update(status='conversion_error', reason=str(error))
                except ValueError as error:
                    result.update(status='empty_or_invalid_html', reason=str(error))
                except FileExistsError:
                    result.update(status='skipped_unverified', reason='File xuất hiện trong lúc tải; không ghi đè, cần kiểm tra.')
                except OSError as error:
                    result.update(status='write_error', reason=str(error))
                finish(result)
                if not pending:
                    break
            for result in pending.values():
                result.update(status='not_found', reason='Không tìm thấy ID trong content của snapshot đã chọn.')
                finish(result)
        except CandidateUpdateError:
            raise
        except Exception as error:
            for result in pending.values():
                result.update(status='download_error', reason=f'{type(error).__name__}: {error}')
                finish(result)
        finally:
            close = getattr(documents, 'close', None)
            if close:
                try:
                    close()
                except Exception as error:
                    warnings.append(f'Đã kết thúc đọc nguồn nhưng đóng kết nối có cảnh báo: {type(error).__name__}')
    if convert_docx and dry_run:
        for result in results:
            _convert_result(result, candidates[result['id']], dry_run)
    counts = dict(Counter(row['status'] for row in results))
    failures = {'conversion_error', 'existing_invalid', 'existing_identity_conflict', 'empty_or_invalid_html', 'write_error', 'not_found', 'download_error'}
    return {'dataset': DATASET, 'revision': REVISION, 'candidates': str(Path(candidates_path).resolve()),
            'output_dir': str(output), 'dry_run': dry_run, 'total_candidates': len(candidates),
            'considered': len(results), 'unexamined_due_to_limit': len(requested) - len(results),
            'counts': counts, 'has_errors': any(row['status'] in failures for row in results),
            'results': results, 'warnings': warnings}


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='backslashreplace')
    parser = argparse.ArgumentParser(description='Tải ứng viên thành DOCX theo số hiệu; kiểm tra file đã có ở đích và thư mục con.')
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--id', nargs='+', dest='ids', help='Một hoặc nhiều ID trong CSV ứng viên.')
    selection.add_argument('--all-candidates', action='store_true', help='Xét CSV ứng viên; nên thêm --limit để tải thử.')
    parser.add_argument('--candidates', type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument('--output-dir', type=Path, default=SCRIPT_DIR / 'data')
    parser.add_argument('--limit', type=int, help='Tùy chọn số nguyên dương: tối đa N văn bản chưa có được thử tải. Bỏ tham số để xét toàn bộ lựa chọn; file bỏ qua không tính vào N.')
    parser.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST, help='Manifest dự án để nhận diện DOCX đã có theo dataset/revision/ID.')
    parser.add_argument('--manifest-root', type=Path, default=REPO_ROOT, help='Gốc tính local_path tương đối trong manifest.')
    parser.add_argument('--dry-run', action='store_true', help='Lập kế hoạch offline, chưa tải/chuyển hoặc tạo file; --report cho phép lưu kế hoạch JSON.')
    parser.add_argument('--html-only', action='store_true', help='Chỉ tải HTML, bỏ bước chuyển DOCX mặc định.')
    parser.add_argument('--open', action='store_true', help='Mở đường dẫn DOCX/HTML vừa tạo qua trình duyệt hệ thống.')
    parser.add_argument('--report', type=Path, help='Lưu báo cáo JSON mới; không ghi đè file báo cáo đã có.')
    args = parser.parse_args()
    if args.report and (args.report.exists() or args.report.is_symlink()):
        parser.error('File --report đã tồn tại; chọn tên khác.')
    try:
        result = download_documents(args.ids, all_candidates=args.all_candidates, candidates_path=args.candidates,
                                    output_dir=args.output_dir, limit=args.limit, dry_run=args.dry_run,
                                    manifest_path=args.manifest, manifest_root=args.manifest_root, convert_docx=not args.html_only)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            with args.report.open('x', encoding='utf-8') as handle:
                json.dump(result, handle, ensure_ascii=False, indent=2)
    except (OSError, ValueError, CandidateUpdateError) as error:
        parser.exit(2, f'Thất bại: {error}\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'results'}, ensure_ascii=False, indent=2))
    for row in result['results'][:20]:
        print(f'{row["id"]}: {row["status"]} — {row.get("reason", "Dự kiến tải.")} [{row["path"]}]')
    if len(result['results']) > 20:
        print('Chỉ hiển thị 20 dòng đầu; dùng --report để xem đầy đủ kết quả.')
    if args.open and not args.dry_run:
        for row in result['results']:
            if row['status'] in {'downloaded', 'converted'}:
                webbrowser.open(Path(row['path']).as_uri())
    return 1 if result['has_errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
