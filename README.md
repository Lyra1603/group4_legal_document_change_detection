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
- [Kết quả xác nhận schema](docs/schema-verification-report.md)
- [Workflow](docs/workflow.md)
- [Thử nghiệm LightRAG, hướng dẫn chạy và bằng chứng demo](docs/lightrag-integration-report.md)

Kiểm tra schema từ repo root, Python 3.11 trở lên; đã chạy Python 3.12.14:

```bash
python -m venv .venv
# PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python -m unittest discover -s test/schema_suite -p "test_*.py" -v
```

requirements.txt ghim Pydantic 2.13.4 và typing_extensions 4.16.0. Lần xác nhận: 51 test, 49 đạt và 2 expected failures ghi nhận giới hạn hiện tại; không phải 51 test đều đạt. Chi tiết, lệnh và môi trường ở báo cáo kiểm thử.

Backend có upload/đọc/parse; chưa có runner phân tích hoặc wiring validator trong Pipeline. POST /api/compare hiện nhận doc_v1/doc_s/reference_files ở backend/main.py; chưa gắn runner trả HTTP 501 / ANALYSIS_NOT_CONFIGURED sau đọc/parse hợp lệ. LightRAG có adapter HTTP/context thử nghiệm và điểm nối opt-in trước Semantic Diff; chưa chạy index/retrieval/KG trên dịch vụ thật và chưa bật trong API. Xem báo cáo thử nghiệm ở trên. requirements.txt hiện chỉ đủ dependency schema; HTTP client tùy chọn ở requirements-lightrag-client.txt, dịch vụ LightRAG chạy riêng.

Phân công: Dũng dữ liệu/docs và Pipeline/API; Thọ xử lý tài liệu; Ngọc Anh Text Diff; Tuấn Anh Semantic Diff/Scorer và frontend; Đức Anh schema/context và điều phối đánh giá; Dũng + Đức Anh AI Adapter và gọi/tích hợp LightRAG.
