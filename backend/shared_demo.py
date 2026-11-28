"""Team demo: one backend owns credentials; browsers never call LightRAG directly."""
import argparse
import json
from contextlib import asynccontextmanager
from functools import lru_cache
import logging
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from time import monotonic
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from . import demo
from .main import DEADLINE_SECONDS, _save_upload
from .app.pipeline import PipelineInputError, parse_documents
from .app.document_processing.document_number import normalize_document_number
from .app.document_processing.target_lookup import base_identity, discover_targets, load_catalog
from .app.context.corpus_document_graph import GRAPH_FILENAME, RUN_DIRECTORY
from .app.context.document_graph_view import DocumentGraphView
from .app.context.owned_server import read_provider_env
from .app.context.shared_service import SharedContextService
from .app.context.lightrag_client import MAX_QUERY_CHARS, RetrievalError
from .app.context.provider_settings import check_groq_jina

ROOT = Path(__file__).resolve().parents[1]
MESSAGES = {
    'REAL_SERVICE_CONFIGURATION_REQUIRED': 'Máy chủ chưa cấu hình đủ provider/model. Người dùng không cần nhập key.',
    'DEMO_BUSY': 'Máy chủ đang xử lý một lượt khác; vui lòng thử lại sau.',
    'INDEX_NOT_READY': 'Kho chưa index thành công; chưa thể truy xuất.',
    'CORPUS_RESTART_REQUIRED': 'Lượt index trước chưa hoàn tất hoặc đã lỗi. Quản trị kiểm tra dịch vụ, rồi khởi động lại demo để tạo kho riêng mới.',
    'INDEX_FAILED': 'Index thất bại. Quản trị kiểm tra provider, quota/billing và cấu hình model.',
    'RETRIEVAL_HTTP_ERROR': 'Dịch vụ truy xuất từ chối hoặc chưa xử lý được yêu cầu.',
    'RETRIEVAL_EMPTY': 'Không nhận được bằng chứng; chưa thể kết luận nội dung pháp luật.',
}


class QueryInput(BaseModel):
    query: str = Field(min_length=1, max_length=MAX_QUERY_CHARS)


def _inspect_upload(upload, document_id, role, inspect):
    deadline = monotonic() + DEADLINE_SECONDS
    try:
        with TemporaryDirectory(prefix='pocs_target_lookup_') as tmp:
            path = Path(tmp)
            item = _save_upload(upload, path, 0, document_id, role, [0], deadline)
            parsed, = parse_documents([item], path, deadline)
            return inspect(parsed)
    except PipelineInputError as exc:
        raise HTTPException(422, detail=dict(code=exc.code, message=str(exc))) from None
    except TimeoutError:
        raise HTTPException(504, detail=dict(code='PROCESSING_TIMEOUT',
                            message='Hết thời gian đọc văn bản.')) from None
    finally:
        upload.file.close()


def create_app(*, settings=None, runtime=None, service=None, document_graph_path=None):
    service = service or SharedContextService(ROOT, runtime or ROOT / 'runtime/lightrag/shared',
        read_provider_env(os.getenv('POCS_PROVIDER_ENV_FILE')) if settings is None else settings)

    @asynccontextmanager
    async def lifespan(app):
        yield
        codes = service.close()
        if codes:
            logging.getLogger(__name__).warning('Shared demo cleanup pending: %s', codes)

    app = FastAPI(title='PoCS Shared Context Demo', lifespan=lifespan)
    app.state.context_service = service
    app.state.analysis_runner = service.compare
    # Reuse upload/validation and sample/static routes. Shared health/config/index
    # are explicit overrides; the old local-rules demo remains unchanged.
    app.router.routes.extend(r for r in demo.app.router.routes
        if getattr(r, 'path', '') not in ('/', '/health', '/api/demo/config', '/openapi.json', '/docs', '/docs/oauth2-redirect', '/redoc'))

    @app.get('/')
    def index():
        html = (ROOT / 'frontend/public/index.html').read_text(encoding='utf-8')
        return HTMLResponse(html.replace('</head>', '<script type="module" src="/assets/pages/shared.js"></script></head>'))

    @app.get('/health')
    def health():
        return dict(api='ok', mode='SHARED_CONTEXT', provider_configured=service.configured,
                    corpus_state=service.status()['state'], semantic_mode='LOCAL_BASELINE')

    @app.get('/api/demo/config')
    def config():
        return {**demo.demo_config(), 'mode': 'SHARED_CONTEXT', 'lightrag_enabled': True,
                'provider_configured': service.configured, 'model_selected': False,
                'semantic_mode': 'LOCAL_BASELINE', 'server_key_required_in_browser': False,
                'target_lookup_enabled': True}

    def failure(exc):
        return HTTPException(409 if exc.code in ('DEMO_BUSY', 'CORPUS_RESTART_REQUIRED') else 503,
            detail=dict(code=exc.code, message=MESSAGES.get(exc.code, 'Truy xuất chưa thành công; không kết luận không có thay đổi.')))

    @app.post('/api/demo/targets')
    def targets(doc_s: Annotated[UploadFile, File()]):
        return _inspect_upload(doc_s, 's', 'AMENDMENT',
                               lambda parsed: discover_targets(parsed, load_catalog(ROOT)))

    @app.get('/api/demo/targets/candidates/{candidate_id}')
    def candidate_file(candidate_id: str):
        for entry in load_catalog(ROOT):
            if entry.id == candidate_id:
                return FileResponse(entry.path, filename=entry.path.name)
        raise HTTPException(404, detail=dict(code='V1_CANDIDATE_UNAVAILABLE',
                            message='Phiên bản đã chọn không còn trong kho đã kiểm tra.'))

    @app.post('/api/demo/targets/verify-v1')
    def verify_v1(doc_v1: Annotated[UploadFile, File()], document_number: Annotated[str, Form()]):
        try:
            expected = normalize_document_number(document_number)
        except ValueError:
            raise HTTPException(422, detail=dict(code='INVALID_TARGET_NUMBER',
                                message='Số hiệu đích không hợp lệ.')) from None
        actual = _inspect_upload(doc_v1, 'v1', 'BASE', lambda parsed: base_identity(parsed, load_catalog(ROOT)))
        if actual != expected:
            message = (f'File có số hiệu {actual}, đích yêu cầu {expected}.' if actual
                       else f'Chưa xác minh được số hiệu của file. Hãy bổ sung bản có số hiệu {expected}.')
            raise HTTPException(422, detail=dict(code='V1_IDENTITY_MISMATCH', message=message))
        return dict(document_number=actual)

    graph_path = document_graph_path or ROOT / RUN_DIRECTORY / GRAPH_FILENAME

    @lru_cache(maxsize=1)
    def document_graph():
        return DocumentGraphView(graph_path)

    def require_document_graph():
        try:
            return document_graph()
        except FileNotFoundError:
            raise HTTPException(503, detail=dict(code='DOCUMENT_GRAPH_NOT_BUILT',
                                message='Chưa dựng đồ thị văn bản.')) from None
        except (OSError, ValueError, TypeError, KeyError):
            raise HTTPException(503, detail=dict(code='DOCUMENT_GRAPH_INVALID',
                                message='Không đọc được dữ liệu đồ thị.')) from None

    @app.get('/api/demo/document-graph/overview')
    def document_graph_overview():
        return require_document_graph().overview

    @app.get('/api/demo/document-graph')
    def browse_document_graph(
        q: Annotated[str | None, Query(max_length=240)] = None,
        node_id: Annotated[str | None, Query(max_length=240)] = None,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=40)] = 12,
    ):
        graph = require_document_graph()
        if q is not None:
            return {**graph.summary, **graph.search(q, offset, limit)}
        selected = node_id if node_id is not None else graph.default_id
        if selected is None:
            return {**graph.summary, 'node': None, 'edges': [], 'neighbors': [], 'total': 0}
        if selected not in graph.nodes:
            raise HTTPException(404, detail=dict(code='DOCUMENT_GRAPH_NODE_NOT_FOUND',
                                message='Văn bản không có trong đồ thị.'))
        return {**graph.summary, **graph.selection(selected, offset, limit)}

    @app.get('/api/demo/corpus')
    def corpus():
        return service.status()

    @app.post('/api/demo/corpus/index', status_code=202)
    def index_corpus():
        try:
            return service.start_corpus()
        except RetrievalError as exc:
            raise failure(exc) from None

    @app.post('/api/demo/corpus/query')
    def query(body: QueryInput):
        if not body.query.strip():
            raise HTTPException(422, detail=dict(code='QUERY_INVALID', message='Cần nhập câu hỏi.'))
        try:
            return service.query(body.query.strip())
        except RetrievalError as exc:
            raise failure(exc) from None

    @app.get('/api/demo/contexts/{comparison_id}')
    def comparison_context(comparison_id: str):
        value = service.context(comparison_id)
        if value is None:
            raise HTTPException(404, detail=dict(code='CONTEXT_NOT_RETAINED', message='Không còn context trong bộ nhớ demo (giữ tối đa 10 lượt).'))
        return value

    return app


app = create_app()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--provider-env-file', type=Path)
    parser.add_argument('--document-graph-file', type=Path)
    parser.add_argument('--check-providers', action='store_true',
                        help='Run two small Groq/Jina requests without starting the web server')
    args = parser.parse_args()
    try:
        settings = read_provider_env(args.provider_env_file)
    except (ValueError, OSError):
        parser.error('Cannot read provider configuration')
    if args.check_providers:
        if args.provider_env_file is None:
            parser.error('--check-providers requires --provider-env-file')
        try:
            result = check_groq_jina(settings)
        except RetrievalError as exc:
            print(json.dumps({'status': exc.code}))
            return 1
        print(json.dumps(result))
        return int(any(probe['status'] != 'OK' for probe in result.values()))
    if os.name == 'nt' and not shutil.which('docker'):
        location = Path(os.getenv('LOCALAPPDATA', '')) / 'Programs/DockerDesktop/resources/bin'
        if (location / 'docker.exe').exists():
            os.environ['PATH'] = str(location) + os.pathsep + os.environ.get('PATH', '')
    import uvicorn
    uvicorn.run(create_app(settings=settings, document_graph_path=args.document_graph_file),
                host=args.host, port=args.port, workers=1)


if __name__ == '__main__':
    raise SystemExit(main())
