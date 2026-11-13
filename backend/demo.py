"""Local web demo: python -m uvicorn backend.demo:app --host 127.0.0.1 --port 8000.

Separate composition from backend.main: the default API retains its unconfigured
runner. No external model or LightRAG request is made in this deferred-model demo.
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .main import compare_documents, MAX_FILE_BYTES, MAX_TOTAL_BYTES, MAX_REFERENCE_FILES, DEADLINE_SECONDS
from .app.demo_runner import run_demo_analysis

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title='PoCS Local Demo', version='0.1.0-local-rules')
app.state.analysis_runner = run_demo_analysis
app.add_api_route('/api/compare', compare_documents, methods=['POST'])

SAMPLES = {
    'case_01': {'label': 'Đo đạc và bản đồ · có chỉ dẫn nhắm văn bản khác',
                'v1': '34_2017_TT-BTC_v1.docx', 's': '33_2019_TT-BTC_amendment.docx'},
    'case_02': {'label': 'Ngân hàng · sửa khoản 5 Điều 16',
                'v1': '22_2019_TT-NHNN_v1.docx', 's': '08_2020_TT-NHNN.docx'},
    'case_03': {'label': 'Trợ giúp xã hội · nhiều chỉ dẫn sửa đổi',
                'v1': '67_2007_ND-CP_v1.docx', 's': '13_2010_ND-CP.docx'},
}


@app.get('/health')
def health():
    return {'api': 'ok', 'comparison_ready': True, 'mode': 'LOCAL_RULES_PARTIAL',
            'lightrag_connection': 'disabled', 'model': 'not_selected'}


@app.get('/api/demo/config')
def demo_config():
    return {'mode': 'LOCAL_RULES_PARTIAL', 'lightrag_enabled': False, 'model_selected': False,
            'max_file_bytes': MAX_FILE_BYTES, 'max_total_bytes': MAX_TOTAL_BYTES,
            'max_reference_files': MAX_REFERENCE_FILES, 'deadline_seconds': DEADLINE_SECONDS,
            'samples': [{'id': key, **value} for key, value in SAMPLES.items()]}


@app.get('/api/demo/files/{case}/{role}')
def sample_file(case: str, role: str):
    if case not in SAMPLES or role not in {'v1', 's'}:
        raise HTTPException(404, detail='Không có tài liệu mẫu này.')
    path = ROOT / 'data' / 'raw' / case / SAMPLES[case][role]
    if not path.is_file():
        raise HTTPException(404, detail='Không tìm thấy file mẫu trong data/raw.')
    return FileResponse(path, filename=path.name,
                        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')


@app.get('/')
def index():
    return FileResponse(ROOT / 'frontend' / 'public' / 'index.html')


app.mount('/assets', StaticFiles(directory=ROOT / 'frontend' / 'src'), name='demo-assets')
