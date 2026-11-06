"""Provisional upload route; existing /api/compare remains legacy JSON."""
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile, BadZipFile

from fastapi import APIRouter, Request, HTTPException
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile
from starlette.responses import JSONResponse

from backend.app.comparison import run_comparison
from backend.app.schemas.contracts import ComparisonReport
from backend.app.storage import workspace

router = APIRouter()


class BodyLimitMiddleware:
    """Bound streamed body before multipart parsing (including chunked bodies)."""
    def __init__(self, app, max_bytes):
        self.app, self.max_bytes = app, max_bytes

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        body = bytearray()
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            body.extend(message.get('body', b''))
            if len(body) > self.max_bytes:
                return await JSONResponse({'error': {'code': 'REQUEST_TOO_LARGE', 'message': 'Request body exceeds limit'}}, status_code=413)(scope, receive, send)
            if not message.get('more_body', False):
                break
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {'type': 'http.request', 'body': bytes(body), 'more_body': False}
            return await receive()
        await self.app(scope, replay, send)


def reject(status, code):
    raise HTTPException(status, detail={'code': code, 'message': code.replace('_', ' ').lower()})


UPLOAD_SCHEMA = {
    'type': 'object', 'required': ['doc_v1', 'doc_s'],
    'properties': {
        'doc_v1': {'type': 'string', 'format': 'binary'},
        'doc_s': {'type': 'string', 'format': 'binary'},
        'reference_files': {'type': 'array', 'items': {'type': 'string', 'format': 'binary'}},
    },
}


@router.post('/api/comparisons', response_model=ComparisonReport, openapi_extra={
    'requestBody': {'required': True, 'content': {'multipart/form-data': {'schema': UPLOAD_SCHEMA}}},
})
async def compare_uploads(request: Request):
    settings = request.app.state.settings
    slots = request.app.state.comparison_slots
    if not slots.acquire(blocking=False):
        reject(503, 'CAPACITY_EXCEEDED')
    try:
        if not request.headers.get('content-type', '').startswith('multipart/form-data'):
            reject(415, 'MULTIPART_REQUIRED')
        async with request.form(max_files=settings.max_references + 2, max_fields=0,
                                max_part_size=settings.max_file_bytes) as form:
            if set(form.keys()) - {'doc_v1', 'doc_s', 'reference_files'}:
                reject(422, 'UNKNOWN_FIELD')
            base, amendment = form.getlist('doc_v1'), form.getlist('doc_s')
            refs = form.getlist('reference_files')
            if len(base) != 1 or len(amendment) != 1:
                reject(422, 'PRIMARY_FILES_REQUIRED')
            if len(refs) > settings.max_references:
                reject(413, 'TOO_MANY_REFERENCES')
            files = [*base, *amendment, *refs]
            if any(not isinstance(f, UploadFile) for f in files):
                reject(422, 'FILE_REQUIRED')
            comparison_id = str(uuid4())
            # Remains alive until the synchronous worker finishes, even on cancellation.
            with workspace() as directory:
                inputs = []
                for index, upload in enumerate(files):
                    name = (upload.filename or '').replace('\\', '/').split('/')[-1]
                    suffix = Path(name).suffix.lower()
                    if suffix not in {'.docx', '.pdf'}:
                        reject(415, 'UNSUPPORTED_FORMAT')
                    identity = dict(document_id='v1' if index == 0 else 's' if index == 1 else f'ref_{index-1}',
                                    role='BASE' if index == 0 else 'AMENDMENT' if index == 1 else 'REFERENCE', filename=name)
                    path = Path(directory) / (identity['document_id'] + suffix)
                    size = 0
                    with path.open('wb') as stream:
                        while chunk := await upload.read(64 * 1024):
                            size += len(chunk)
                            if size > settings.max_file_bytes:
                                reject(413, 'FILE_TOO_LARGE')
                            stream.write(chunk)
                    if not size:
                        reject(422, 'EMPTY_FILE')
                    if suffix == '.docx':
                        try:
                            with ZipFile(path) as archive:
                                if sum(i.file_size for i in archive.infolist()) > settings.max_docx_expanded_bytes:
                                    reject(413, 'DOCX_EXPANSION_LIMIT')
                        except BadZipFile:
                            reject(422, 'INVALID_DOCX')
                    inputs.append((identity, str(path)))
                report = await run_in_threadpool(run_comparison, inputs, comparison_id, settings, request.app.state.services)
                return JSONResponse(report, status_code=422 if report['status'] == 'FAILED' else 200)
    finally:
        slots.release()
