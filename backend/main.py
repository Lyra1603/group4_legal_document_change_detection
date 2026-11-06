from fastapi import FastAPI
from pydantic import BaseModel
from backend.app.pipeline import run_pipeline
from backend.app.api.uploads import router, BodyLimitMiddleware
from backend.app.config import Settings
from backend.app.comparison import Services
from threading import BoundedSemaphore
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
import logging

app = FastAPI(title="Legal Document Change Detection API")
app.state.settings = Settings.from_env()
app.state.services = Services()
app.state.comparison_slots = BoundedSemaphore(app.state.settings.max_concurrent)
app.add_middleware(BodyLimitMiddleware, max_bytes=app.state.settings.max_request_bytes)
app.include_router(router)


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    logging.getLogger(__name__).error('Unhandled backend error type=%s', type(exc).__name__)
    return JSONResponse({'error': {'code': 'INTERNAL_ERROR', 'message': 'Backend processing failed'}}, status_code=500)


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    if exc.status_code == 400 and isinstance(exc.detail, str) and 'Too many files' in exc.detail:
        return JSONResponse({'error': {'code': 'TOO_MANY_FILES', 'message': 'Multipart file limit exceeded'}}, status_code=413)
    detail = exc.detail if isinstance(exc.detail, dict) else {'code': 'HTTP_ERROR', 'message': str(exc.detail)}
    return JSONResponse({'error': detail}, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse({'error': {'code': 'INVALID_REQUEST', 'message': 'Request validation failed'}}, status_code=422)


@app.get('/health')
def health():
    return {'status': 'ok', 'comparison_ready': all(vars(app.state.services).values())}

class CompareRequest(BaseModel):
    doc_v1: str
    doc_v2: str

@app.post("/api/compare")
def compare_documents(req: CompareRequest):
    results = run_pipeline(req.doc_v1, req.doc_v2)
    return {"status": "success", "data": results}
