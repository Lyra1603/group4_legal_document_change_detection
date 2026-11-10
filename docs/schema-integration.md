# Hợp đồng schema chung và hướng dẫn tích hợp

## Căn cứ và phạm vi nhập

Nhóm đã chọn hợp đồng tại commit `b6a13f98b9a7357b9fbb0936aba6bda065d03fcb` của nhánh `feat/ducanh-backend-integration`. Các file [contracts.py](../backend/app/schemas/contracts.py), [validation.py](../backend/app/schemas/validation.py), [report_validation.py](../backend/app/schemas/report_validation.py) và `__init__.py` được giữ nguyên từng byte so với commit căn cứ. Không nhập Pipeline, API, storage, runner, Parser hoặc các dependency không liên quan từ nhánh đó.

Schema đã merge qua [PR #2](https://github.com/Lyra1603/group4_legal_document_change_detection/pull/2), commit main `a8a906a474a67e89195987ca757f7315c22231db`. Tài liệu đồng bộ được chuẩn bị trên nền commit này; nội dung docs mới trên bachdung/docs (`b20ba5806772d8bb1f5f41f55548471eb8e251e0`) và bản docs đã được Dũng duyệt được giữ khi tương thích schema. Chỉ chuyển tài liệu, không merge nguyên nhánh docs cũ để tránh kéo ngược mã nguồn/cấu trúc.

## Cấu trúc và kiểm tra có sẵn

ComparisonReport chứa comparison_id, base_document, amendment_document, reference_documents, status, results, warnings, errors. Mỗi result là AmendmentResult với amendment, text_diff, semantic_diff, scoring. Các khóa TypedDict đều bắt buộc; Optional cho phép null, không cho phép bỏ khóa. Kiểu LegacyScoringResult, BaselineSemanticDiffResult và AlignedPair được giữ để bảo toàn code căn cứ, không thay hợp đồng V1–S chung.

| Hàm | Đầu vào | Kiểm tra chính |
| --- | --- | --- |
| validate_payload(kind, value) | TypedDict và dict/list | Kiểu strict, khóa bắt buộc, Literal, các trường có hậu tố _id không rỗng |
| validate_extracted_document(document) | ExtractedDocument | Metadata, role BASE/AMENDMENT/REFERENCE, file_type DOCX/PDF_TEXT, block refs duy nhất và có nội dung chữ |
| validate_sources(value, documents) | Cấu trúc lồng nhau và kho ExtractedDocument theo document_id | Mọi EvidenceRef phải có ref tồn tại và quote là chuỗi con nguyên văn của các block được ghép bằng newline theo thứ tự source_refs |
| validate_amendment(item, documents, clauses) | AmendmentItem, kho nguồn và dict có khóa v1 chứa list[Clause] | Kiểu/nguồn, chỉ dẫn từ s, target_unit_ids có trong clauses['v1'], review flags và trạng thái tham chiếu |
| validate_report(report) | ComparisonReport | Vai trò/ID tài liệu, filename, ID lồng nhau, offset cục bộ, nhóm/category/scoring, review propagation và điều kiện SUCCESS được code thực thi |

Không hàm nào tự chứng minh suy luận pháp lý đúng. validate_report không gọi validate_sources hoặc validate_amendment; chỉ gọi một hàm không thay toàn bộ kiểm tra. SourceBlock không bắt buộc định dạng prefix cụ thể: block:N được chấp nhận khi tồn tại trong đúng tài liệu và quote khớp. Khóa phụ không mặc định bị TypeAdapter từ chối; hàm validate_payload không trả lại đối tượng đã chuẩn hóa để thay đầu vào.

Tám nhóm: SUBJECT_OBJECT, RIGHTS_DUTIES_ACTIONS, CONDITIONS_EXCEPTIONS, TIME_QUANTITY, PROCEDURE_AUTHORITY, CONSEQUENCES_SANCTIONS, DEFINITIONS_REFERENCES, SCOPE_EFFECT_TRANSITION. category thuộc các nhóm đó, WORDING_ONLY hoặc null; category khác null của thay đổi nghĩa phải có trong aspects. Có thể dùng LOW/MEDIUM/HIGH/CRITICAL hoặc null theo ràng buộc scoring. Thứ tự ưu tiên khi nhiều category đều hợp lệ và rubric cụ thể vẫn do Tuấn Anh/Dũng review, không tự suy từ tập enum.

## Cung cấp kho nguồn và Clause từ Pipeline hiện tại

Main trả ParsedDocument(document, tree, source_format); tree chứa source_blocks, articles, outside, warnings và summary. Các đối tượng này chưa phải ExtractedDocument hoặc Clause. document_adapter.py hiện là khung; ví dụ dưới là cách bàn giao để owner hiện thực tiếp, không phải adapter production đã được merge.

```python
from backend.app.schemas.contracts import ExtractedDocument, Clause
from backend.app.schemas.report_validation import (
    validate_payload, validate_sources, validate_amendment, validate_report,
)
from backend.app.schemas.validation import validate_extracted_document

# parsed là list[ParsedDocument] nhận trong analysis_runner của main.
documents = {}
clauses = {}
for parsed_document in parsed:
    identity = parsed_document.document.identity()
    doc_id = identity['document_id']
    documents[doc_id] = {
        **identity,
        'file_type': ('PDF_TEXT' if parsed_document.document.path.suffix.lower() == '.pdf'
                      else 'DOCX'),
        'blocks': [{'source_ref': block['source_ref'], 'text': block['text']}
                   for block in parsed_document.tree['source_blocks']],
    }
    clauses[doc_id] = [
        {'unit_id': article['node_id'], 'id': 'Điều ' + article['label'],
         'title': article['heading'], 'content': article['full_text'],
         'source_refs': article['source_refs']}
        for article in parsed_document.tree['articles']
    ]
    validate_payload(ExtractedDocument, documents[doc_id])
    validate_extracted_document(documents[doc_id])
    for clause in clauses[doc_id]:
        validate_payload(Clause, clause)

# Linker phải dùng đúng unit_id trong clauses['v1']; không tự dựng theo số Điều.
for result in report['results']:
    validate_amendment(result['amendment'], documents, clauses)
validate_sources(report, documents)
validate_report(report)
```

`report` là báo cáo cuối do Pipeline tổng hợp, không phải một biến main cung cấp sẵn cho runner. Runner hiện nhận `(parsed, comparison_id, deadline)` và trả AnalysisOutcome. Owner có thể kiểm tra từng output theo đúng TypedDict và nguồn ngay trong runner; Dũng cần nối kiểm tra báo cáo cuối vào Pipeline trước khi trả API, khi kho nguồn còn tồn tại. Ví dụ ở [test_main_compatibility.py](../test/schema_suite/test_main_compatibility.py) chỉ dựng báo cáo fixture trong test để kiểm chứng điểm nối.

Giữ nguyên text của mọi block, kể cả bảng/outside; các field native như kind và segments có thể lưu riêng để không mất thông tin. Không dùng full_text mọi cấp làm kho block vì sẽ lặp nội dung. Với PDF chuyển sang DOCX, file_type phản ánh đầu vào PDF_TEXT, nhưng source_ref/offset vẫn thuộc DOCX đã parse; giữ cảnh báo mapping PDF chưa xác minh. Không hứa node_id ổn định giữa các lần parse; fixture main thực tế sinh v1:n2 cho Điều đầu tiên trong ví dụ, nên không hardcode v1:n1.

## Tương thích và việc cần nối tiếp

Nhánh `ducanh_bachdung/integrate_LightRAG`, commit `e47e049ada29fdab95dcd39a5d0ad14d98c3b411`, đã có client HTTP, chunk builder, source registry, context builder và `context/semantic_bridge.py`. Có demo DOCX với adapter, Linker hẹp, Text Diff, baseline Semantic/Scorer và report PARTIAL. Demo chạy riêng bằng `backend.demo:app`; `backend.main:app` vẫn chưa cấu hình runner mặc định. Frontend demo là HTML/CSS/JavaScript, chưa thay định hướng frontend chính thức.

Chưa kiểm chứng LightRAG Server/model/index/KG thật; web demo tắt LightRAG. Bridge hiện chạy Context (gồm retrieval khi cấu hình) song song Text Diff rồi ghép trước Semantic; còn tách index/query và dùng Text Diff tạo query để khớp luồng mục tiêu mới. Rule baseline đã có, model fallback chưa tích hợp. Kết quả nhánh thử nghiệm không tự xác nhận đã merge main/nghiệm thu.

Căn cứ: [báo cáo tích hợp](https://github.com/Lyra1603/group4_legal_document_change_detection/blob/e47e049ada29fdab95dcd39a5d0ad14d98c3b411/docs/lightrag-integration-report.md), [demo và giới hạn](https://github.com/Lyra1603/group4_legal_document_change_detection/blob/e47e049ada29fdab95dcd39a5d0ad14d98c3b411/docs/local-web-demo.md). Kết quả test trong các báo cáo chưa được chạy lại trong đợt sửa tài liệu này.

- Main đã trả cùng envelope base_document/amendment_document/reference_documents/results. Schema đã merge không tự bật validation: pipeline.py, backend/main.py, router và runner không bị sửa trong PR #2. Không có analysis_runner vẫn FAILED/ANALYSIS_NOT_CONFIGURED và API hiện trả HTTP 501.
- Thọ hiện thực document_adapter theo kho nguồn/Clause trên, giữ metadata native để linker/context dùng; linker tạo AmendmentItem, không biến S thành V2 đầy đủ. Reference không có Điều vẫn giữ blocks, có thể có clauses rỗng.
- Ngọc Anh trả TextDiffResult với amendment_id và offset Python [start,end) trên đúng before/after. Tuấn Anh trả SemanticDiffResult và list[ScoringResult]; Dũng nối bằng ID trong cùng amendment, không làm phẳng hay bỏ chỉ dẫn chưa có changes.
- Đức Anh review schema, context và kế hoạch đánh giá; Dũng + Đức Anh thực hiện AI Adapter và LightRAG theo phân công. LightRAG HTTP/lifecycle vẫn cần LK-13; schema không xác nhận API dịch vụ đã có.
- Frontend đọc identity từ ba trường tài liệu, duyệt results và changes, ghép scoring theo change_id trong result. Nhận xét hai loại triển khai sau theo mục riêng; chưa thêm decision/note vào schema backend.
- Endpoint/upload không thay trong PR schema: main hiện POST /api/compare, doc_v1/doc_s/reference_files. Định hướng tên upload khác trong docs vẫn là việc LK-11 cần review; không dùng việc chọn schema để tự chuyển API.

## Giới hạn giữ nguyên và ví dụ cần review riêng

| Điểm | Ví dụ cụ thể | Việc cần chốt tiếp |
| --- | --- | --- |
| ID chưa kiểm tra toàn comparison | Hai amendment khác ID đều chứa change_id = c1 vẫn được chấp nhận | Dùng khóa ghép amendment_id/change_id hay buộc change_id toàn cục; chưa đổi validator |
| Chưa kiểm tra reconstruction toàn diff | before có 30, after có 15, nhưng changes = [] vẫn được chấp nhận | Ngọc Anh/Dũng review kiểm tra bao phủ, thứ tự và thao tác chồng lấn |
| Không kiểm tra mọi trường quote độc lập | old_quote/new_quote là str thường; chỉ EvidenceRef được đối chiếu nguồn | Tuấn Anh/Thọ chốt mapping từng quote; không giả định mọi quote đã được validate |
| Review không thay thế readiness | Item thiếu đích nhưng đang needs_review có thể qua một số kiểm tra | Pipeline cần chính sách có thể chạy bước nào; không coi qua schema là đủ căn cứ |
| PARTIAL/FAILED chưa được kiểm chứng đầy đủ | Report PARTIAL rỗng và không có lý do vẫn có thể qua validator | Dũng/owner review tiêu chí kết quả dùng được và lý do bắt buộc |
| Metadata và ref list còn cần kiểm tra đầu vào | Kho documents key không khớp document_id, source_refs lặp hoặc input malformed | Adapter validate nguồn/Clause trước; tăng validation là PR riêng |
| Nhận xét hai loại — giai đoạn sau | Chưa có contract lưu hoặc cơ chế kết hợp | Chốt khi triển khai sau chức năng cốt lõi; không tự thêm ReviewItem |

Hai giới hạn đầu có test expectedFailure để ghi nhận thực tế, không phải tính năng được chấp nhận hoặc đã sửa. Các đề xuất tăng kiểm tra ở bảng trên chưa là quyết định mới của nhóm. Giữ code căn cứ là chủ đích phạm vi PR, không bỏ qua những giới hạn này khi nghiệm thu toàn hệ thống.

## API và HTTP status đối chiếu với main

Căn cứ [backend/main.py](../backend/main.py), chưa kiểm thử HTTP runtime trong đợt này. Route thực thi nằm ở main.py; [api/compare.py](../backend/app/api/compare.py) còn trống.

| Đầu vào/điều kiện trong code | Phản hồi hiện có |
| --- | --- |
| GET /health | HTTP 200; api, comparison_ready, lightrag_connection=not_checked, missing_components |
| POST /api/compare | multipart doc_v1 và doc_s bắt buộc, reference_files tùy chọn; alias base_file/amendment_file chưa được hỗ trợ |
| Báo cáo SUCCESS hoặc PARTIAL | HTTP 200 với ComparisonReport và X-Comparison-ID |
| FAILED / ANALYSIS_NOT_CONFIGURED | HTTP 501 với ComparisonReport; mặc định khi chưa gắn runner |
| FAILED / PROCESSING_TIMEOUT | HTTP 504, trừ khi cùng có ANALYSIS_NOT_CONFIGURED thì nhánh 501 được ưu tiên |
| FAILED khác | HTTP 500 với ComparisonReport |
| Sai định dạng; quá dung lượng; file rỗng/quá số tham chiếu | HTTP 415; 413; 422 với detail, không phải ComparisonReport |
| PipelineInputError hoặc thiếu upload bắt buộc | HTTP 422; lỗi dependency validation upload do FastAPI xử lý, body khác report |
| Đang có lượt so sánh khác | HTTP 503, Retry-After: 5 |
| Hết hạn khi nhận upload; lỗi API ngoài dự kiến | HTTP 504; 500 với detail |

Giới hạn mặc định trong code là 20 MiB/file, 60 MiB tổng, 5 file tham chiếu và deadline 300 giây; đây là cấu hình phát triển qua LEGAL_* env, chưa là chỉ tiêu nghiệm thu. Lock theo process và cleanup đồng bộ hiện tại vẫn giữ nguyên. Schema không mô tả error body detail của FastAPI; frontend phải xử lý cả report và lỗi HTTP.

Khác biệt cần LK-11 review: giữ hay đổi tên upload, alias/tương thích nếu đổi; chuẩn hóa HTTP error body; đưa route sang compare.py; cơ chế truy nguồn sau cleanup. Không quyết định hoặc hiện thực các thay đổi đó ở PR tài liệu.

## Nhận xét — phạm vi mở rộng chưa có contract

Nhận xét là chức năng dự kiến sau khi các chức năng cốt lõi hoàn thiện, chỉ liệt kê trong phạm vi mở rộng, không là module chính hoặc điều kiện nghiệm thu bản đầu. Hai loại: (1) nhận xét sau phiên được lưu để phục vụ phát triển; (2) nhận xét trong phiên kết hợp nhận xét có sẵn để xem xét và cập nhật kết luận. Khi triển khai, giữ phân biệt kết luận ban đầu/cập nhật và căn cứ thay đổi; không tự coi nhận xét là gold/nhãn huấn luyện. Cách lưu, API, định danh, nguồn nhận xét có sẵn và cơ chế kết hợp chưa chốt; chưa mở rộng schema chung.

Giữ contracts.py/validator; thay đổi contract sau này cần bên giao/nhận review.

## Chạy độc lập và dependency

Chạy từ repo root, Python 3.11 trở lên. requirements.txt chỉ thêm pydantic 2.13.4 và typing_extensions 4.16.0, đã cài và chạy kiểm tra trong venv sạch trên Python 3.12.14; các dependency chuyển tiếp do pip giải quyết và được kiểm tra bằng pip check. Không lấy nguyên requirements của nhánh Đức Anh vì có dependency cho API/storage ngoài phạm vi. API/PDF cần FastAPI, uvicorn, multipart và thư viện converter theo module khi thực hiện PR runtime; không tuyên bố requirements schema đã đủ chạy mọi tính năng.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
python -m unittest discover -s test/schema_suite -p "test_*.py" -v
```

Fixture [common_contract.json](../test/fixtures/reports/common_contract.json) là dữ liệu giả định để kiểm tra contract, không là nhãn pháp lý hoặc bằng chứng chất lượng mô hình. Test tích hợp dùng DOCX tối thiểu tự dựng bằng thư viện chuẩn và Parser có sẵn của main; không cần import API, storage, LightRAG hay mô hình. Ngưỡng F1 90%/Critical Recall 95% vẫn dự tính và có thể thay đổi sau khi hoàn thiện test_evaluation_plan.md; test schema không xác nhận hai ngưỡng đó.

Kết quả chạy lại trên main sau PR #2: [báo cáo kiểm thử và các điểm còn mở](schema-verification-report.md).
