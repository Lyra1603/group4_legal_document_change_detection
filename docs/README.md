# Group 4 — Legal Document Change Detection

Mục tiêu POCS: từ một S, tự tìm đích/phiên bản trong kho dân sự nhóm chuẩn bị, giải thích thay đổi trực tiếp và kiểm chứng tác động gián tiếp. Nền đang chạy vẫn là demo V1 + S; xem [nền chung](common-baseline.md) để phân biệt code với mục tiêu.

- [BRD](brd.md), [SRS](srs.md), [Architecture](architecture.md)
- [Module](module.md), [Decision](decision.md), [Workflow](workflow.md)
- [Kế hoạch theo phiên code](implementation-plan.md), [Kế hoạch kiểm thử và đánh giá](test_evaluation_plan.md)
- [Hướng dẫn gán nhãn](data-annotation-guide.md), [Tích hợp và kiểm tra schema](schema-integration.md)
- [Nền chung đang chạy và việc còn thiếu](common-baseline.md), [Cách mở web demo](local-web-demo.md)
- [Fixture bàn giao](../data/module_handoff_fixtures/README.md), [Báo cáo schema lịch sử](schema-verification-report.md)

Tài liệu lấy nền từ nhánh Dũng `bachdung/docs` tại `6dbda8d`, bổ sung theo quyết định Đức Anh ngày 12/11/2026. Thiết kế mục tiêu bên dưới không đồng nghĩa mọi chức năng đã có code. Nền hiện tại chạy bằng `backend.demo:app` theo README gốc, dùng DOCX và chưa bật LightRAG/model; không dùng `backend.main:app` để kỳ vọng có kết quả phân tích. Bảng đối chiếu implementation và kết quả kiểm thử tập trung tại [common-baseline.md](common-baseline.md).

Luồng mục tiêu nhận S, bối cảnh/nguồn bổ sung tùy chọn và trả báo cáo cấp S. Request đồng bộ là phương án dự kiến, cần đo trên ca nhiều đích và tác động gián tiếp. Các module backend bàn giao theo schema chung. LightRAG là dịch vụ retrieval riêng qua HTTP. Xem [luồng xử lý](architecture.md#4-luồng-phân-tích-dữ-liệu-và-phiên) để tra sơ đồ và vòng đời nguồn.

Cấu trúc chuẩn lấy từ `main`. [Architecture §3](architecture.md#3-cấu-trúc-mã-nguồn-và-dữ-liệu) định vị code hiện có và phân biệt các chức năng mục tiêu chưa có file.

Change F1 ≥ 90% và Critical Change Recall ≥ 95% là các ngưỡng dự tính. Xem [kế hoạch đánh giá](test_evaluation_plan.md#82-phép-đo-cần-đề-xuất-và-chốt) để tra phương pháp đo và mốc xác nhận.
