# Bằng chứng xử lý nhận xét ngày 17/11/2026

Đây là lần chạy bổ sung sau `462d70e`, giữ nguyên input và output lịch sử trong
`data/ngocanh-week10/`. Xem [báo cáo bàn giao hiện tại](../../docs/ngocanh-civil-review.md).

- `output/fresh_case_02.json`: AmendmentResult mới từ Parser/Adapter của Thọ,
  Text Diff/Semantic/Scorer dùng chung và payload query do code Context tạo.
- `output/docx_cases.json`: kết quả kiểm tra ba bộ DOCX, bao gồm mục chưa xử lý.
- `output/tests.txt`: kết quả 7 kiểm thử chéo, không phải độ chính xác pháp lý.
- `output/manifest.json`: SHA từng bên, hash code/input/output và xác nhận còn chờ.

## Chạy lại với bản đã ghép main

Chạy từ repo root sau khi cài `requirements-demo.txt` vào Python 3.11+.

```powershell
python -m unittest test.handoff_suite.test_peer_handoffs -v
python -m test.handoff_suite.run_peer_handoffs --output runtime/lightrag/text-diff-handoff
```

Runner dùng Parser, Adapter, Context, Text Diff, Semantic và Scorer từ cùng
working tree. HTTP dùng `httpx.MockTransport` và `ContractServer`. Báo cáo
ghi SHA và hash của mã nguồn được dùng, cùng số thay đổi bị lược trong câu
truy xuất dài. Lệnh xuất kết quả vào thư mục được chọn để giữ nguyên bằng
chứng lịch sử trong `output/`.

Có thể thêm `--tho-ref` hoặc `--context-ref` để kiểm tra mã thực thi trong
worktree khớp với ref được cung cấp. Nếu khác, runner báo lỗi và yêu cầu
chuẩn bị bản đã tích hợp. Không còn phụ thuộc tên nhánh Context đã xóa.
