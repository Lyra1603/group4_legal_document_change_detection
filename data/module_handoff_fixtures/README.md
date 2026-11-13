# Module handoff fixtures

Bộ fixture cho các owner phát triển song song theo [Architecture](../../docs/architecture.md), [Module](../../docs/module.md) và [schema chung](../../backend/app/schemas/contracts.py). Mỗi thư mục là một điểm nối. Bên nhận dùng `input` để chạy module với dữ liệu mẫu. Hai bên đối chiếu kết quả với `expected_output` khi bàn giao. Hai khóa này chỉ dùng để đóng gói fixture.

Ca `deadline_reduction.json` xuyên suốt từ nguồn đến báo cáo. V1 yêu cầu nộp báo cáo trong 30 ngày kể từ ngày nhận thông báo, S thay Điều 2 bằng nội dung trích nguyên văn với hạn 15 ngày, và Điều 3 của V1 xác định đơn vị là ngày làm việc. Tên file và nội dung văn bản đều là dữ liệu giả định. Văn bản đã được biểu diễn thành các block để owner có thể bắt đầu từ JSON.

| Điểm nối | Owner giao → nhận | Đầu vào → kết quả mong đợi |
| --- | --- | --- |
| [Adapter → Linker](adapter_to_linker/deadline_reduction.json) | Thọ → Thọ | Kho `ExtractedDocument` và `Clause` → danh sách `AmendmentItem` có đúng đích, trước/sau và nguồn |
| [Adapter → Context](adapter_to_context/deadline_reduction.json) | Thọ → Đức Anh | Kho `ExtractedDocument` → tín hiệu chỉ mục sẵn sàng trong ca mẫu |
| [Document/Linker → Text Diff](document_to_text_diff/deadline_reduction.json) | Thọ → Ngọc Anh | `AmendmentItem` → `TextDiffResult` thay đúng hai ký tự ở đoạn cục bộ |
| [Text Diff + chỉ mục → Ghép query](text_diff_and_index_to_query/deadline_reduction.json) | Ngọc Anh + Đức Anh → Đức Anh/Dũng | Chỉ dẫn, `TextDiffResult` và chỉ mục đã sẵn sàng → nội dung query minh họa |
| [Retrieval → Context](retrieval_to_context/deadline_reduction.json) | Đức Anh/Dũng → Đức Anh | `AmendmentItem` và ứng viên nguồn đã ánh xạ sang dạng `EvidenceRef` → `AmendmentItem` bổ sung ngữ cảnh sau khi đối chiếu nguyên văn |
| [Context + Text Diff → Semantic Diff](context_and_text_diff_to_semantic/deadline_reduction.json) | Đức Anh + Ngọc Anh → Dũng + Đức Anh + Ngọc Anh | `AmendmentItem` đã có ngữ cảnh và `TextDiffResult` → `SemanticDiffResult` có khía cạnh `TIME_QUANTITY` |
| [Semantic Diff → Scorer](semantic_to_scorer/deadline_reduction.json) | Nhóm Semantic Diff → Nhóm Scorer (cùng phân công LK-01) | `AmendmentItem` và `SemanticDiffResult` → danh sách `ScoringResult` theo `change_id` |
| [Các module phân tích → Pipeline/API](analysis_to_pipeline/deadline_reduction.json) | Các owner → Dũng | Định danh tài liệu, `AmendmentResult` và các danh sách lỗi/cảnh báo → `ComparisonReport` |
| [API → Frontend](api_to_frontend/deadline_reduction.json) | Dũng → Tuấn Anh | `ComparisonReport` → nội dung cần hiển thị gồm thay đổi, mức tác động, bằng chứng, lỗi, cảnh báo và trạng thái |

Offset `TextChange` dùng chỉ số ký tự Python và khoảng nửa mở `[start, end)` trên đúng `before_text` hoặc `after_text`. Tra nguồn theo cặp `document_id` và `source_refs`. Có thể lấy kho nguồn từ `adapter_to_linker/deadline_reduction.json` để đối chiếu mọi quote trong ca. `context` rỗng ở đầu ra Linker vì Context sẽ điền sau bước query và kiểm chứng.

Các chi tiết chọn cho ca mẫu:

- `index_ready`, `query_text`, `candidate_evidence` và cách nhóm các đối số là quy ước fixture để dựng mock. Nội dung query minh họa những thông tin cần ghép; owner có thể dùng câu chữ khác. Hình thức request/response LightRAG và API của từng module được chốt riêng theo LK-06/LK-13.
- `MEDIUM` là mức mong đợi riêng của ca này. Rubric chung vẫn theo LK-09/LK-10. `SUCCESS` mô tả kịch bản mẫu đã xử lý đầy đủ; kết quả retrieval trong fixture được dựng sẵn.
- Đầu ra của điểm nối API → Frontend mô tả dữ liệu người dùng cần xem. Khóa `displayed_evidence` thuộc fixture giao diện. HTTP response vẫn dùng `ComparisonReport`.
