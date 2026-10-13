# Bàn giao phiên làm việc

## Trạng thái khởi tạo
- Base: nhánh `ducanh/docs`, commit `89d4712`.
- Có 6 docs và 3 cặp DOCX mẫu; code vẫn là baseline.
- Harness này hỗ trợ lập trình với AI; không thay thế Semantic Diff trong sản phẩm.
- Chưa có task tuần 6 nào được xác nhận hoàn thành bởi harness.

## Vấn đề đã biết
- SRS/BRD hỗ trợ DOCX và PDF text; Annotation Guide mục 2.2 lại ghi chỉ PDF. Cần nhóm chốt trước task Reader/API thật.
- Schema code chưa theo SRS mới có ChangeAspect/DocumentIdentity.
- API baseline nhận hai chuỗi text; chưa có upload, Reader, Text Diff riêng hoặc UI.
- Evaluator baseline chưa đủ để nghiệm thu chất lượng; smoke test không đo metric.
- Scorer baseline có nhánh DELETED trả HIGH nhưng is_critical=true; cần xử lý trong task Scorer.

## Task nên bắt đầu
- W6-SCHEMA: tạo schema theo SRS và fixture báo cáo giả định để các thành viên phát triển song song.

## Mẫu cập nhật sau mỗi phiên
- Task và commit/diff được kiểm tra:
- Hành vi đã thực hiện:
- Lệnh kiểm tra và kết quả:
- Phần còn mock/chưa xử lý:
- Vấn đề đang chặn:
- Bước tiếp theo:

Giữ ghi chú ngắn, phản ánh code thực tế; không ghi dữ liệu đầu vào đầy đủ hoặc bí mật.
