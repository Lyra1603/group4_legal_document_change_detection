# Fixture bàn giao chung — bản chuẩn bị tích hợp

Nguồn fixture ban đầu là `bachdung/docs-data` tại **cf62188b5f1e366957666a4b0edb6003da5679d5**, được đối chiếu lại trên `bachdung/docs` tại **6dbda8da7a050e4d21f354c5e59765244e2f176a** (9 file gốc không đổi). Đây là bộ mẫu chung duy nhất; không giữ song song bản MEDIUM/SUCCESS cũ. `provenance.json` ghi nguồn, các khác biệt theo quyết định Đức Anh ngày 12/11 và phạm vi kiểm chứng. Không sửa nhánh Dũng.

**Đây là dữ liệu giả định để phát triển và kiểm tra hợp đồng. Không phải output chạy thật, gold đã được review, index sẵn sàng thật hoặc LightRAG đã truy xuất thành công.** Các khóa input/expected_output/metadata và expected trong ca lỗi là vỏ fixture, không thêm trường vào schema runtime.

## Ca xuyên suốt deadline_reduction

V1 có Điều 2 yêu cầu báo cáo trong 30 ngày và Điều 3 quy định ngày làm việc; S thay Điều 2 bằng đoạn 15 ngày trích nguyên văn. Nguyên văn nguồn và offset của Dũng được giữ. Các thay đổi thống nhất:

- Khi đã xác định đích là V1, target_document dùng document_id `v1`; tên văn bản vẫn có trong nguồn chỉ dẫn.
- Query chờ cả index và TextDiffResult; dùng chỉ dẫn, trước/sau và vùng chữ đổi. Câu chữ query chỉ là minh họa.
- significance/is_critical chưa được review giữ null; ScoringResult có needs_review và lý do. Không ép MEDIUM/HIGH thành gold.
- Báo cáo mẫu dùng PARTIAL với warning review, không coi đã xử lý đầy đủ mọi mặt.
- Kết quả Semantic trong fixture là đáp án kỹ thuật dự kiến từ bản Dũng, **không chứng minh baseline hiện tại chạy ra kết quả đó**. Quy tắc, độ đầy đủ context, model và nhãn nghiệp vụ còn cần owner review.

| Thư mục | Bên giao → nhận | Dữ liệu chính |
| --- | --- | --- |
| adapter_to_linker | Thọ → Thọ | Kho nguồn và Clause → AmendmentItem |
| adapter_to_context | Thọ → Đức Anh | Kho nguồn → tín hiệu index mẫu |
| document_to_text_diff | Thọ → Ngọc Anh | AmendmentItem → TextDiffResult |
| text_diff_and_index_to_query | Ngọc Anh + Đức Anh → Đức Anh/Dũng | Index + diff + item → yêu cầu query |
| retrieval_to_context | Đức Anh/Dũng → Đức Anh | Ứng viên EvidenceRef → context đã kiểm tra |
| context_and_text_diff_to_semantic | Đức Anh + Ngọc Anh → Tuấn Anh | Item có context + diff → SemanticDiffResult |
| semantic_to_scorer | Tuấn Anh → Tuấn Anh | SemanticDiffResult → list[ScoringResult] |
| analysis_to_pipeline | Các owner → Dũng | Kết quả và issue → ComparisonReport |
| api_to_frontend | Dũng → Tuấn Anh | Report → các giá trị cần hiển thị |

`index_ready`, `query_text`, `candidate_evidence`, `displayed_evidence` và `significance_label` là quy ước fixture, không tự trở thành tên hàm, API LightRAG hoặc field schema chung. Fixture Adapter → Linker chưa cung cấp `BoundaryData.units` của implementation hiện tại; owner phải chốt binding/adapter nội bộ, không sửa schema chỉ để giữ đối tượng hỗ trợ này.

## Ca lỗi và điều kiện chờ

Trong `scenarios/` có sáu ca:

1. `unverified_document`: chưa đủ căn cứ xác minh tên/số hiệu đích → UNRESOLVED, không lấy V1 làm đích mặc định.
2. `other_document`: số hiệu được xác định khác V1 → OTHER_DOCUMENT, không áp dụng vào V1.
3. `missing_target`: đúng văn bản nhưng không có Điều đích → UNRESOLVED.
4. `ambiguous_target`: lặp nhãn Điều, không có đích duy nhất → UNRESOLVED.
5. `unsupported_move`: biết vị trí nhưng không hỗ trợ thao tác chuyển → không tự đổi thành AMEND.
6. `mixed_supported_unsupported`: có một mục dùng được và một mục ngoài phạm vi → giữ cả hai, PARTIAL.

Các expected trong sáu ca là **assertion theo tập con**, không phải ComparisonReport đầy đủ. Các khóa như analysis_permitted, operation_must_not_be, usable_results, item_count, review_reason_required chỉ dùng mô tả điều kiện kiểm thử. Runtime vẫn phải trả đủ field theo contracts.py. Fixture chưa ấn định giá trị target_document khi danh tính văn bản chưa xác minh; không tự thêm ID giả hoặc enum mới vào schema. Ca biết đúng V1 nhưng không tìm thấy đơn vị vẫn có thể giữ ID v1.

Hai ca trong `text_diff_and_index_to_query/` kiểm tra index chưa ready hoặc chưa có TextDiffResult: không query, giữ lý do. index_ready=true trong ca chuẩn chỉ là mock điều kiện; không phải bằng chứng dịch vụ thật.

## Cách kiểm tra và mức độ bằng chứng

```powershell
python -m unittest discover -s test/handoff_suite -v
```

Bộ kiểm tra kiểm tra shape, nguồn, ID, offset/reconstruction và tính nhất quán giữa fixture; thêm kiểm tra gọi trực tiếp Text Diff/Scorer và phân loại report trên đầu vào fixture. Không gọi model, không chạy toàn bộ Linker từ các SourceBlock mẫu này và không xác nhận nhãn pháp lý. Metadata TARGET chỉ nói fixture là kỳ vọng, không kết luận thuật toán hiện chưa có. Hai lỗi Linker và mapping HTTP/status đã được sửa, kiểm thử riêng trong test/demo_suite tại c192f43. Query đợi index và TextDiffResult vẫn là mục tiêu cần nối code, không được fixture/mock chứng minh đã hoàn tất.

File DOCX/PDF trong data/raw dùng chạy tích hợp thật, không tự thành gold. Khi owner nhận task, bàn giao bằng cả fixture này và output thật có lệnh chạy/commit/giới hạn. Không dùng màu xanh của test dữ liệu mẫu để tuyên bố hệ thống đã hoàn thiện.
