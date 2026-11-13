# KẾ HOẠCH TRIỂN KHAI POCS THEO PHIÊN CODE

Phạm vi nghiệp vụ lấy từ [BRD](brd.md), yêu cầu và dữ liệu từ [SRS](srs.md), cấu trúc và luồng chạy từ [Architecture](architecture.md). Xem [Decision](decision.md) để tra các quyết định đã chốt và [Workflow](workflow.md) để thực hiện quy trình làm việc.

## 1. Phiên 1 — Hoàn thiện luồng cơ sở V1–S

Mục tiêu là chạy được một lượt so sánh từ V1, S và tài liệu tham chiếu nếu có đến báo cáo có trước/sau và bằng chứng. Các module dùng [fixture bàn giao](../data/module_handoff_fixtures/README.md) để làm bán song song. Ca có thật đi qua bộ đọc và Parser. Đường gọi LightRAG hoặc mô hình có thể dùng đầu ra mô phỏng tại các điểm nối trong phiên này.

| Người phụ trách | File hoặc phạm vi hoàn thiện | Đầu ra của phiên |
| --- | --- | --- |
| Thọ | `backend/app/document_processing/pdf_to_docx.py`, `parser/legal_structure_parser.py` trong cùng thư mục, `document_adapter.py`, `amendment_linker.py` | Dùng converter/Parser hiện có, bổ sung phần thiếu nếu kiểm thử phát hiện lỗi. Trả tài liệu chuẩn hóa, căn cứ nguồn và đủ đích. Tạo hai bản toàn văn của đơn vị đối chiếu. |
| Ngọc Anh | `backend/app/change_analysis/text_diff.py` | Trả đúng các vùng chữ đổi và offset. Đối chiếu khả năng dựng lại đoạn sau từ kết quả diff. |
| Đức Anh | `backend/app/context/chunk_builder.py`, `source_registry.py`, `context_builder.py` | Chuẩn bị nguồn và ngữ cảnh cơ sở. Ghép đầu ra Text Diff với dữ liệu chỉ mục mô phỏng và đối chiếu ứng viên bằng chứng với nguồn thật. |
| Dũng + Đức Anh + Ngọc Anh | `backend/app/change_analysis/semantic_diff.py`, `scorer.py` | Chạy rule trên ca chuẩn, giữ khía cạnh và căn cứ, ghi phần chưa thể chấm. |
| Tuấn Anh | Phần giao diện trong `frontend/` | Hiện trước/sau, trạng thái và bằng chứng từ báo cáo. Xử lý và hiển thị lỗi, cảnh báo và kết quả từng phần do Pipeline/API trả về. |
| Dũng | `backend/app/pipeline.py`, `backend/app/api/compare.py` và nối điểm vào trong `backend/main.py` khi cần | Ghép module, kiểm tra báo cáo và nguồn, trả báo cáo qua API hiện có, giữ chỉ dẫn chưa xử lý cùng lý do. |
| Dũng + Đức Anh | Hợp đồng vào/ra của `backend/app/context/lightrag_client.py`, `backend/app/change_analysis/ai_adapter.py` và cấu hình liên quan | Thử điểm nối bằng mock và ghi dữ liệu cần xác nhận khi chuyển sang dịch vụ thật. |
| Dũng + Đức Anh và các owner | `data/module_handoff_fixtures/` và ca kiểm thử theo [kế hoạch đánh giá](test_evaluation_plan.md) | Dũng chuẩn bị ca và nhãn tham chiếu. Hai bên của từng điểm nối đối chiếu kỳ vọng. Đức Anh điều phối tổng hợp kết quả. |

**Đầu ra khi kết thúc phiên:** Một ca chạy xuyên luồng có báo cáo qua validator và hiển thị được bằng chứng. Ghi rõ bước nào dùng đầu ra thật hoặc mô phỏng. Mỗi owner nộp kết quả chạy, lỗi có thể tái hiện và phần hợp đồng cần làm rõ. Đức Anh điều phối chốt nội dung phiên tiếp theo từ kết quả đó.

## 2. Phiên 2 — Tích hợp các đầu ra thật

Phạm vi dự kiến được xác nhận sau phiên 1.

| File hoặc phạm vi | Đầu ra dự kiến |
| --- | --- |
| `backend/app/context/lightrag_client.py`, `chunk_builder.py`, `source_registry.py`, `context_builder.py`, `backend/app/config.py` | Nối LightRAG qua HTTP. Kiểm chứng nhập chỉ mục, truy vấn, ánh xạ nguồn, vòng đời dữ liệu và hành vi lỗi theo các quyết định mới từ phiên 1. |
| `backend/app/change_analysis/ai_adapter.py`, `semantic_diff.py`, `scorer.py` | Hoàn thiện phần phân tích còn thiếu. Nối model khi kết quả phiên 1 cho thấy cần thiết. Kiểm tra output theo schema và rubric được nhóm duyệt. |
| `backend/app/pipeline.py`, `backend/app/api/compare.py`, `backend/main.py`, `frontend/` | Chạy lại API và giao diện với dữ liệu thật. Kiểm tra luồng chuẩn, thiếu đích và bằng chứng sau cleanup. |
| `data/module_handoff_fixtures/`, `test/` | Hoàn thiện các bộ ca theo cùng danh sách tại chín điểm nối. Kiểm thử hồi quy các lỗi được ghi nhận trong phiên 1. |

**Đầu ra dự kiến:** Chạy xuyên luồng với các module thật thuộc phạm vi đã chốt, có bằng chứng kiểm thử và mô tả các giới hạn còn lại.

## 3. Phiên 3 — Kiểm thử, đánh giá và bàn giao

Phạm vi dự kiến được cập nhật từ kết quả phiên 2. Hoàn thiện các file còn lỗi chặn luồng. Chạy ca tích hợp trong `test/` và đánh giá độc lập theo [kế hoạch kiểm thử](test_evaluation_plan.md). Ghi kết quả chất lượng, lỗi, độ trễ và chi phí nếu có gọi dịch vụ. Cập nhật `README.md` và `docs/schema-integration.md` theo cách chạy thực tế. Hoàn thiện dữ liệu được phép bàn giao, báo cáo đánh giá và slide.

**Đầu ra kết thúc:** Một phiên bản chạy lại được với dữ liệu mẫu, kết quả kiểm thử gắn commit, giới hạn được công bố và minh chứng để nhóm bảo vệ.
