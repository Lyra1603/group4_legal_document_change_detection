# Group 4 — Legal Document Change Detection

Dự án POCS phân tích văn bản gốc V1, văn bản sửa đổi S và tài liệu tham chiếu, hỗ trợ sinh viên Luật đối chiếu thay đổi chữ/nghĩa, bằng chứng và mức tác động.

Schema Đức Anh đã merge vào main qua [PR #2](https://github.com/Lyra1603/group4_legal_document_change_detection/pull/2). ComparisonReport giữ comparison_id, base_document, amendment_document, reference_documents, status, results, warnings, errors; mỗi result là AmendmentResult. Dùng tám field_group, category và significance theo validator, không chuyển sang báo cáo phẳng.

- [Tổng quan và phân công](docs/README.md)
- [Yêu cầu và hợp đồng dữ liệu](docs/srs.md)
- [Kiến trúc](docs/architecture.md)
- [Module và owner](docs/module.md)
- [Quyết định đã chốt/còn mở](docs/decision.md)
- [Hướng dẫn schema, API hiện tại và adapter còn thiếu](docs/schema-integration.md)
- [Kế hoạch kiểm thử](docs/test_evaluation_plan.md)
- [Workflow](docs/workflow.md)
- [Nền chung: cách chạy, trạng thái và việc còn thiếu](docs/common-baseline.md)
- [Fixture bàn giao tại 9 điểm nối](data/module_handoff_fixtures/README.md)
- [Web demo và bằng chứng chạy DOCX](docs/local-web-demo.md)
- [Thử nghiệm LightRAG qua HTTP](docs/lightrag-integration-report.md)
- [Báo cáo kiểm thử schema lịch sử](docs/schema-verification-report.md)

## Chạy nền DOCX hiện tại

Từ repo root, dùng Python 3.11 trở lên:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-demo.txt
python -m uvicorn backend.demo:app --host 127.0.0.1 --port 8000
```

Mở http://127.0.0.1:8000, chọn V1, S và tài liệu tham chiếu nếu có; hoặc nạp một trong ba bộ DOCX mẫu. LightRAG/model đang tắt. Có Text Diff không đồng nghĩa đã xác nhận ngữ nghĩa hoặc mức tác động; báo cáo còn thiếu căn cứ giữ `PARTIAL`, không có mục phân tích dùng được giữ `FAILED` cùng lý do. PDF chưa được kiểm chứng xuyên luồng và không là điều kiện của nền chung lần này.

Kiểm tra schema từ repo root, Python 3.11 trở lên; đã chạy Python 3.12.14:

```bash
python -m venv .venv
# PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python -m unittest discover -s test/schema_suite -p "test_*.py" -v
```

requirements.txt ghim Pydantic 2.13.4 và typing_extensions 4.16.0. Lần xác nhận: 51 test, 49 đạt và 2 expected failures ghi nhận giới hạn hiện tại; không phải 51 test đều đạt. Xem [hướng dẫn tích hợp schema](docs/schema-integration.md) để chạy lại kiểm tra.

`backend.demo:app` đã gắn runner thực thi DOCX → Parser → Adapter → Linker hẹp → Text Diff/Context → Semantic/Scorer giới hạn → validation → báo cáo và giao diện. Route dùng chung vẫn là POST `/api/compare`, nhận `doc_v1`, `doc_s`, `reference_files`. `backend.main:app` giữ API nền chưa gắn runner và trả HTTP 501 / ANALYSIS_NOT_CONFIGURED sau đầu vào hợp lệ. Client LightRAG HTTP đã có mã và kiểm thử mô phỏng; chưa kiểm chứng dịch vụ thật, chưa bật trong demo. `requirements.txt` chỉ đủ schema; chạy demo cần `requirements-demo.txt`. Cách chạy trên là điểm khởi động chung hiện tại, không tự đổi module main.

Phân công: Dũng dữ liệu/docs và Pipeline/API; Thọ xử lý tài liệu; Ngọc Anh Text Diff; Dũng + Đức Anh + Ngọc Anh phụ trách Semantic Diff và Scorer; Tuấn Anh phụ trách UI và xử lý lỗi trả về; Đức Anh schema/context và điều phối đánh giá; Dũng + Đức Anh AI Adapter và gọi/tích hợp LightRAG.
