# Group 4 — Legal Document Change Detection

Dự án POCS đối chiếu văn bản gốc V1 với văn bản sửa đổi S và tài liệu tham chiếu nếu có. Báo cáo trình bày thay đổi chữ, thay đổi nghĩa, mức độ tác động, bằng chứng và phần chưa xử lý.

- [BRD](brd.md), [SRS](srs.md), [Architecture](architecture.md)
- [Module](module.md), [Decision](decision.md), [Workflow](workflow.md)
- [Kế hoạch theo phiên code](implementation-plan.md), [Kế hoạch kiểm thử và đánh giá](test_evaluation_plan.md)
- [Hướng dẫn gán nhãn](data-annotation-guide.md), [Tích hợp và kiểm tra schema](schema-integration.md)

Luồng mục tiêu nhận tài liệu và trả báo cáo trong một request đồng bộ. Các module backend bàn giao theo schema chung. LightRAG là dịch vụ retrieval riêng qua HTTP. Xem [luồng xử lý](architecture.md#4-luồng-phân-tích-dữ-liệu-và-phiên) để tra sơ đồ và vòng đời nguồn.

Cấu trúc chuẩn lấy từ `main`. [Architecture §3](architecture.md#3-cấu-trúc-mã-nguồn-và-dữ-liệu) liệt kê các thư mục và file backend theo mốc Git được đối chiếu.

Change F1 ≥ 90% và Critical Change Recall ≥ 95% là các ngưỡng dự tính. Xem [kế hoạch đánh giá](test_evaluation_plan.md#82-phép-đo-cần-đề-xuất-và-chốt) để tra phương pháp đo và mốc xác nhận.
