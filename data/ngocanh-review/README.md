# Bằng chứng xử lý nhận xét ngày 17/11/2026

Đây là lần chạy bổ sung sau `462d70e`, giữ nguyên input và output lịch sử trong
`data/ngocanh-week10/`. Xem [báo cáo bàn giao hiện tại](../../docs/ngocanh-civil-review.md).

- `output/fresh_case_02.json`: AmendmentResult mới từ Parser/Adapter của Thọ,
  Text Diff/Semantic/Scorer dùng chung và payload query do code Context tạo.
- `output/docx_cases.json`: kết quả kiểm tra ba bộ DOCX, bao gồm mục chưa xử lý.
- `output/tests.txt`: kết quả 7 kiểm thử chéo, không phải độ chính xác pháp lý.
- `output/manifest.json`: SHA từng bên, hash code/input/output và xác nhận còn chờ.

Chạy từ repo root sau khi cài `requirements-demo.txt` vào Python 3.11+:

```powershell
git fetch origin
python -m test.handoff_suite.run_peer_handoffs --tho-ref ffd2f86aa135a8c6f717782baa65350010c48f9b --context-ref 159e3552ce7a3ceb39dcea6ad3de767b83d359cd
```

Runner đọc các Git blob được chỉ định, nạp bằng tên module riêng để không đổi
working tree hoặc merge code của bên khác. Chỉ chạy với commit tin cậy đã review.
Code xử lý tài liệu và code Context đều được thực thi, không chép đáp án fixture.
Test HTTP dùng `httpx.MockTransport` và `ContractServer`, không gọi dịch vụ thật.
Query payload được kiểm tra ở bộ dựng query và ở request `/query/data` của
HTTP contract double; chưa xác nhận retrieval thực hoặc đầy đủ Context pháp lý.

Có thể dùng `--output <thư mục>` để giữ riêng một lần chạy mới. Các SHA mặc định
theo remote branch có thể thay đổi; lệnh trên pin đúng phiên bản đã ghi nhận.
