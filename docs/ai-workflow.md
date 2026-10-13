# Làm việc với AI bằng harness tối thiểu

Harness ở đây là bộ hướng dẫn, công cụ kiểm tra và thông tin bàn giao để coding agent làm đúng task. Nó hỗ trợ phát triển dự án; không phải mô hình AI phân tích thay đổi pháp lý trong sản phẩm.

## 1. Ba lệnh cần nhớ

Chạy ở thư mục repo (Windows có thể dùng `py` thay `python`):

```bash
python scripts/harness.py status
python scripts/harness.py check
python scripts/harness.py verify W6-SCHEMA
```

- `status`: xem nhánh, thay đổi hiện có và danh sách task.
- `check`: kiểm tra cấu trúc task, cú pháp Python và smoke test luồng text baseline.
- `verify TASK_ID`: chạy bộ behavioral test unittest của task. Thiếu test, zero tests, mọi test bị skip hoặc test thất bại thì không pass.
- Harness dùng thư viện chuẩn Python; không cần thêm package hay API key.
- `check` pass không có nghĩa đáp ứng SRS hoặc đạt F1. `verify` pass cũng cần review nội dung test và phạm vi thực sự đã bao phủ.
- Danh sách test_file là vị trí dự kiến để tạo test, không khẳng định repo đã có bộ kiểm thử mới. Với UI, wrapper Python có thể gọi test runner frontend; lỗi/missing runner phải làm test thất bại, không skip để báo pass.

## 2. Một phiên làm việc

1. AI đọc AGENTS.md, progress.md, chạy status và chọn một task.
2. Đọc đúng mục SRS/Architecture có liên quan; nói bằng lời dữ liệu vào/ra và những file sẽ sửa.
3. Hiện thực task; dùng fixture khi phần của thành viên khác chưa xong.
4. Kiểm tra hành vi: đầu vào mẫu, kết quả mong đợi, lỗi và cảnh báo. Chạy check và verify.
5. Đưa thay đổi cùng kết quả chạy cho người phụ trách review.
6. Cập nhật progress.md: đã làm, lệnh đã chạy, kết quả, phần còn mock và bước tiếp theo.

Task có trạng thái todo → in_progress → review → done; blocked dùng khi vướng quyết định/dependency. Mỗi nhánh chỉ có một in_progress. done phải có evidence và reviewer; không viết đã xong khi chỉ có file code. Task W6-SCHEMA nên bắt đầu trước các task tiêu thụ schema; các thành viên vẫn làm song song trên nhánh riêng với fixture đã thống nhất.

Lệnh verify không tự sửa trạng thái. Người phụ trách ghi command, commit hoặc diff thực tế đã kiểm tra, kết quả và giới hạn trong evidence/progress; reviewer kiểm tra trước khi chuyển done. JSON và test vẫn sửa được bởi người có quyền repo: đây là quy trình hỗ trợ, không phải cơ chế chống giả mạo hay đánh giá độc lập.

## 3. Prompt bắt đầu dành cho Đức Anh

> Đọc AGENTS.md và harness/progress.md, chạy python scripts/harness.py status. Làm task W6-SCHEMA theo đúng SRS hiện tại. Trước khi sửa, giải thích bằng ví dụ Điều cũ 30 ngày → mới 15 ngày: dữ liệu cần có những trường nào và các module sẽ dùng chúng ra sao. Tạo schema và fixture; viết test hành vi cho dữ liệu hợp lệ, null/chưa xác định và báo cáo PARTIAL. Chạy check và verify W6-SCHEMA. Báo kết quả thật, phần chưa triển khai và cập nhật bàn giao. Giải thích mỗi thay đổi để tôi hiểu được code.

Với task của người khác, thay TASK_ID và đọc đúng phần tài liệu của module. Không yêu cầu AI “làm toàn bộ hệ thống” trong một lượt.

## 4. Các bài giảng và cách áp dụng

Repo tham khảo: [WalkingLabs — Learn Harness Engineering](https://github.com/walkinglabs/learn-harness-engineering/tree/main/docs/vi/lectures). Nội dung dưới đây là diễn giải phục vụ dự án, không chép nguyên bộ bài giảng.

| Bài | Ý chính | Áp dụng ở repo này |
| --- | --- | --- |
| [01](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/lectures/lecture-01-why-capable-agents-still-fail/index.md) | Mô hình mạnh vẫn có thể thực thi sai | Quan sát lỗi trước khi đổi mô hình. |
| [02](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/lectures/lecture-02-what-a-harness-actually-is/index.md) | Hướng dẫn, công cụ, môi trường, trạng thái, phản hồi | AGENTS + script + Python + progress + tests. |
| [03](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/index.md) | Thông tin cần thiết phải có trong repo | SRS/Architecture và bàn giao có thể đọc lại. |
| [04](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/lectures/lecture-04-why-one-giant-instruction-file-fails/index.md) | Tệp hướng dẫn ngắn, dẫn đến tài liệu đúng | AGENTS làm bản đồ, không nhét toàn bộ SRS. |
| [05](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/lectures/lecture-05-why-long-running-tasks-lose-continuity/index.md) | Giữ liên tục giữa các phiên | progress ghi task, kiểm tra và bước sau. |
| [06](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/lectures/lecture-06-why-initialization-needs-its-own-phase/index.md) | Khởi tạo và kiểm tra môi trường trước khi code | status/check phát hiện code baseline và phần còn thiếu. |
| [07](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/lectures/lecture-07-why-agents-overreach-and-under-finish/index.md) | Giới hạn một task có đầu ra rõ | Một in_progress mỗi nhánh. |
| [08](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/lectures/lecture-08-why-feature-lists-are-harness-primitives/index.md) | Task có hành vi, xác minh và trạng thái | tasks.json có acceptance và test_file. |
| [09](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/lectures/lecture-09-why-agents-declare-victory-too-early/index.md) | Đòi bằng chứng trước khi tuyên bố hoàn thành | Không pass khi test chưa có; review trước done. |
| [10](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/lectures/lecture-10-why-end-to-end-testing-changes-results/index.md) | Kiểm tra xuyên ranh giới module | Task upload/UI cần test tích hợp ngoài unit test. |
| [11](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/lectures/lecture-11-why-observability-belongs-inside-the-harness/index.md) | Quan sát lỗi và runtime | Lệnh trả lỗi rõ; ghi số test và giới hạn. |
| [12](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/lectures/lecture-12-why-every-session-must-leave-a-clean-state/index.md) | Bàn giao cuối phiên và trạng thái tái lập | Để lại lệnh chạy và vấn đề, không xóa thay đổi người dùng. |
| [13](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/lectures/lecture-13-loop-engineering/index.md) | Vòng lặp có mục tiêu và điều kiện dừng | Để sau khi kiểm tra/task đã ổn định. |
| [14](https://github.com/walkinglabs/learn-harness-engineering/blob/main/docs/vi/lectures/lecture-14-graph-engineering/index.md) | Định tuyến công việc và phụ thuộc | depends_on mô tả các task cần schema; chưa cần framework đồ thị. |

Đọc trước **02 → 04 → 07 → 08 → 09**, sau đó 05/06/10/12 khi bắt đầu code. Bài 13/14 dành cho giai đoạn đã có task và kiểm chứng ổn định; hiện không triển khai vòng lặp tự động hoặc multi-agent.

## 5. Hiểu tác dụng bằng ví dụ

Không có harness: “Làm backend” → AI dễ đổi schema, bổ sung nhiều công nghệ, rồi báo xong dù UI chưa dùng được.

Với harness: W6-SCHEMA → đọc mục dữ liệu SRS → tạo một báo cáo mẫu → chạy test null/PARTIAL → người phụ trách review → bàn giao để UI/API sử dụng. Bạn có thể mở fixture và thấy cụ thể vì sao mỗi trường tồn tại.

## 6. Giới hạn và việc tiếp theo

- Đây là starter harness cho code baseline; chưa có CI enforcement, môi trường frontend hay bộ test nghiệm thu pháp lý.
- Khi schema/Pipeline chuyển sang SRS mới, thay smoke baseline bằng smoke của hợp đồng mới cùng task tích hợp, không giữ assertion cho output cũ.
- docs chưa thống nhất PDF-only hay DOCX/PDF. Chốt trước task Reader/API thật.
- Không đưa khóa API/nội dung tài liệu đầy đủ vào ghi chú bàn giao hoặc log.
- Benchmark chất lượng legal diff dùng dữ liệu/nhãn và Evaluator riêng. Harness kiểm tra coding không thay thế Evaluation Plan.
- Mỗi thay đổi nên được người phụ trách giải thích và chạy lại; AI hỗ trợ để nhóm hiểu và kiểm soát triển khai.
