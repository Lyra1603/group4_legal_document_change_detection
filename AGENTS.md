# Hướng dẫn cho AI coding agent

## Bắt đầu
- Đọc `harness/progress.md`, chạy `python scripts/harness.py status`.
- Chọn một task trong `harness/tasks.json`; làm một task mỗi lượt.
- Kiểm tra `git status` trước khi sửa; giữ các thay đổi đang có của người dùng.
- Đọc đúng mục tài liệu liên quan, không cần đọc toàn bộ docs mỗi lượt.

## Nguồn tham chiếu
- Nhu cầu và phạm vi: `docs/brd.md`.
- Hợp đồng dữ liệu, null, cảnh báo và trạng thái: `docs/srs.md`.
- Ranh giới module và request đồng bộ: `docs/architecture.md`.
- Công nghệ đề xuất và phân công: `docs/implementation-plan.md`.
- Dữ liệu, nhãn và tiêu chí pilot: `docs/data-annotation-guide.md`.
- Cách làm việc và xác minh: `docs/ai-workflow.md`.

## Ràng buộc dự án
- Hai phiên bản đầy đủ của cùng VBQPPL tiếng Việt; không OCR, hợp đồng hoặc tự dựng V2 trong Pipeline.
- So sánh cấp Điều, giữ nội dung Khoản/Điểm; ghép mơ hồ/tách/gộp phải cảnh báo.
- Giữ định danh, bằng chứng, vị trí nguồn và cảnh báo xuyên suốt Pipeline.
- Không đổi null/lỗi thành danh sách rỗng hoặc kết luận không có thay đổi.
- SRS sở hữu schema. Nếu docs mâu thuẫn về định dạng đầu vào, nêu điểm cần chốt trước khi hiện thực phần bị ảnh hưởng.
- Công nghệ trong kế hoạch là đề xuất; ghi rõ dependency mới và lý do khi cần thêm.
- Không lấy chỉ số từ baseline hiện tại làm bằng chứng đạt F1/Critical Recall mục tiêu.

## Kết thúc task
- Chạy `python scripts/harness.py check` và kiểm thử hành vi của task.
- `check` chỉ kiểm tra harness/cú pháp/luồng baseline, không chứng nhận đáp ứng SRS.
- Chạy `python scripts/harness.py verify TASK_ID` khi có bộ test của task.
- Giải thích ngắn: sửa gì, dữ liệu vào/ra, lệnh kiểm tra, kết quả và giới hạn.
- Cập nhật task và `harness/progress.md`; chưa chạy hoặc thất bại thì ghi rõ.
- Không sửa test/tiêu chí chỉ để biến lỗi thành pass. Có thay đổi tiêu chí phải giải thích căn cứ.
- Commit/push theo yêu cầu người dùng; không force push hoặc merge main nếu chưa được yêu cầu.
