# Backend API — development contract

Đây là giao diện triển khai trên nhánh backend, chưa thay thế quyết định
liên nhóm về tên field/endpoint và HTTP mapping. Đức Anh + Tuấn Anh cần
review trước khi frontend phụ thuộc vào giao diện này. Schema nội dung báo
cáo theo SRS 1.3.0; không tự thay đổi danh mục nghiệp vụ.

## Endpoint

- `GET /health`: trạng thái tiến trình và `comparison_ready`. Readiness là
  kiểm tra đủ adapter được đăng ký, không chứng minh chất lượng thuật toán.
- `POST /api/compare`: JSON `doc_v1`, `doc_v2` của baseline cũ, trả
  `{status: "success", data: AlignedPair[]}`; không dùng để gửi V1–S.
- `POST /api/comparisons`: giao diện upload phát triển, multipart/form-data.
  Một file `doc_v1`, một file `doc_s`, không hoặc nhiều file `reference_files`.
  Chỉ nhận DOCX/PDF; tên file được bỏ đường dẫn, lưu bằng tên nội bộ riêng.
  S có thể sửa nhiều văn bản; adapter phải phân biệt OTHER_DOCUMENT.

Upload trả trực tiếp `ComparisonReport` (không có envelope `data`).
`comparison_id` là UUID mới cho mỗi request, không phải mã job có thể tra lại.
`base_document`, `amendment_document`, `reference_documents` giữ filename và
role kể cả khi tên file trùng nhau. Không trả đường dẫn lưu file nội bộ.
Mỗi kết quả giữ amendment, text_diff, semantic_diff và scoring theo SRS.
Các bước chưa chạy hoặc thất bại là `null` kèm issue, không điền danh sách rỗng
để giả vờ hoàn thành. Không tự retry toàn bộ POST hoặc lưu file chờ bổ sung.

## Status và lỗi

| HTTP | Body | Ý nghĩa |
| --- | --- | --- |
| 200 | ComparisonReport với SUCCESS/PARTIAL | Hoàn tất hoặc có kết quả một phần |
| 422 | ComparisonReport với FAILED | Không tạo được báo cáo nghiệp vụ sử dụng được, kể cả adapter chưa cấu hình |
| 422 | `{error: {code, message}}` | Thiếu file, file rỗng, cấu trúc request sai, DOCX hỏng trước Reader |
| 415 | error | Sai content-type hoặc định dạng file không hỗ trợ |
| 413 | error | Quá giới hạn body/file/số tham chiếu hoặc DOCX giải nén |
| 503 | error | Hết slot xử lý trong tiến trình |

Multipart hỏng có thể trả HTTP 400 từ parser với error envelope. Client phải
phân biệt báo cáo FAILED (có comparison_id) và lỗi trước khi chạy pipeline.
Phân biệt lỗi theo `code`, không dựa vào câu message. Exception nội bộ module
được ghi thành MODULE_FAILED, không trả nội dung exception/tài liệu cho client.

SUCCESS không đồng nghĩa chắc chắn về pháp lý; needs_review vẫn phải được
hiển thị. Pipeline hiện xử lý thận trọng: có yêu cầu review sẽ trả PARTIAL.
PARTIAL không đồng nghĩa tất cả module đã hoàn thành.

## Trạng thái hiện tại và điểm bàn giao đang chờ

Mặc định `Services()` không đăng ký extractor/context/text/semantic/scorer.
Upload đọc file thật, sau đó trả FAILED / MODULE_NOT_CONFIGURED ở extraction.
Không có mock nghiệp vụ trong server. SUCCESS trong test được tạo bằng adapter
fixture chỉ để kiểm tra orchestration, không phải kết quả thuật toán thực.

Adapter được đăng ký qua `app.state.services` khi khởi tạo server:

| Adapter | Giao diện Python (dict/list theo contracts.py) | Bên cần review |
| --- | --- | --- |
| extract | `(documents_by_id, clauses_by_id) -> list[AmendmentItem]` | Thọ + Đức Anh |
| context | `(item, documents_by_id, clauses_by_id) -> AmendmentItem` | Dũng/Thọ/Ngọc Anh + Đức Anh |
| text_diff | `(item) -> TextDiffResult` | Ngọc Anh + Đức Anh |
| semantic_diff | `(item, text_diff_or_none) -> SemanticDiffResult` | Ngọc Anh + Đức Anh |
| score | `(item, semantic_result) -> list[ScoringResult]` | Ngọc Anh + Đức Anh |

Không đăng ký một adapter pass-through context khi chưa có căn cứ xác nhận
ngữ cảnh đã đủ. Pydantic model của module riêng cần adapter serialize về dict;
chưa tự import các module ở nhánh khác. Các adapter phải báo đủ cảnh báo,
phạm vi chưa xử lý và tuân thủ timeout của tài nguyên ngoài nếu có.
Evidence được kiểm tra bằng document_id/source_ref và đoạn quote trong nguồn.
Text diff offset phải khớp chuỗi cục bộ. Report được kiểm tra runtime trước trả.

Việc chọn parser cấu trúc chính, đổi `block:N` sang nguồn Reader, ranh giới
gán nhãn/severity, người sở hữu context và API cuối cùng vẫn chờ các thành viên
review. Không ghép V1 với S bằng align_versions của baseline.
