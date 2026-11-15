# Web demo cục bộ V1–S

Ngày 11/11/2026, trên nhánh `ducanh_bachdung/integrate_LightRAG`. Người dùng đã cho phép kiểm tra nhánh thành viên, tái sử dụng code và viết phần tối thiểu còn thiếu. Dữ liệu lấy từ `data/raw`; quyết định model được để lại sau.

**Cập nhật 12/11, code c192f43:** đây là điểm chạy nền chung theo quyết định Đức Anh. Linker đã sửa xác minh văn bản đích và chặn thao tác chưa hỗ trợ bị nhận thành AMEND; report/HTTP đã sửa. JSON/ảnh ngày 11/11 bên dưới là lịch sử, không tự ghi đè. Trạng thái mới ở [common-baseline.md](common-baseline.md).

## Kết quả hiện tại

Có luồng thực thi từ giao diện chọn file → upload HTTP → Reader/Parser → adapter Clause → Linker hẹp → Text Diff → baseline ngữ nghĩa/scoring → validator → báo cáo trên web. Không dùng đáp án trước/sau điền sẵn để tạo kết quả.

**Chưa có LightRAG/model thật trong web demo này.** Baseline giữ kết luận ngữ nghĩa và mức tác động chưa xác định khi context chưa xác nhận. Có mục phân tích dùng được nhưng còn thiếu thì PARTIAL; không có mục dùng được thì FAILED cùng chỉ dẫn/lý do. FAILED nghiệp vụ với errors rỗng vẫn HTTP 200; lỗi thực thi giữ mã HTTP phù hợp. Không tuyên bố nghiệm thu Semantic Diff hoặc LK-13.

## Cách mở

Từ repo root, dùng môi trường Python đã cài dependency của demo:

```powershell
python -m pip install -r requirements-demo.txt
python -m uvicorn backend.demo:app --host 127.0.0.1 --port 8000
```

Mở http://127.0.0.1:8000. Chọn V1 và S, thêm tài liệu tham chiếu nếu cần; hoặc chọn bộ Ngân hàng trong danh sách mẫu → Nạp file mẫu → Bắt đầu đối chiếu.

`backend.demo:app` là điểm khởi chạy riêng, dùng route upload hiện hành với runner demo. `backend.main:app` vẫn mặc định chưa cấu hình runner; không biến API nền thành demo một cách ngầm định. Payload upload và ComparisonReport không đổi. Request object chỉ dùng để lấy runner của đúng app, không thêm trường vào request người dùng.

Luồng đã kiểm chứng là DOCX. PDF vẫn qua bộ chuyển đổi hiện có, cần dependency và source mapping riêng; chưa kiểm thử PDF xuyên suốt trong đợt này. File lỗi hiển thị lỗi, không tạo báo cáo thành công giả. Giới hạn file/số tham chiếu/deadline lấy từ API nền. `POCS_DEMO_MAX_UNIT_CHARS` mặc định 12000 là giới hạn tính diff cho demo, không phải ngưỡng nghiệm thu chính thức.

## Phạm vi Linker

- Một lệnh thay cụm từ X bằng Y ở một Điều, tùy chọn một khoản và một điểm. Cụm cũ phải xuất hiện duy nhất; after_basis là DERIVED và không gán new_quote như nguyên văn.
- Thay nguyên đơn vị bằng một đoạn trích dẫn đóng/mở đầy đủ sau chỉ dẫn sửa đổi. Nhãn Điều/khoản/điểm của đoạn thay thế phải khớp đích; after_basis là QUOTED.
- Đối chiếu số hiệu từ header V1 và chỉ dẫn/heading S, hoặc tên văn bản khớp nguyên dòng header sau chuẩn hóa. Chỉ APPLIES khi có căn cứ xác minh, không chỉ vì trùng số Điều. Số hiệu đã xác định khác V1 giữ OTHER_DOCUMENT; thiếu căn cứ giữ UNRESOLVED, không mặc định V1.
- Chỉ dẫn bổ sung/bãi bỏ, nhiều đích, đích không duy nhất, cụm từ không duy nhất, quote hỏng hoặc đánh lại số chưa được thực hiện; giữ chỉ dẫn và cảnh báo trong báo cáo.
- Khi không nhận diện được chỉ dẫn, trả INSTRUCTIONS_NOT_RECOGNIZED, không suy ra “không có thay đổi”. Đây là bộ nhận diện mẫu hẹp, chưa chứng minh bao phủ mọi cách diễn đạt pháp luật.

## Những nhánh đã đối chiếu và code tái sử dụng

| Nguồn | Hiện trạng kiểm tra | Cách dùng |
| --- | --- | --- |
| origin/ngocanh, commit 92074d51536d0d1abafbdd0867cec61ba8afd718 | Có Text Diff, baseline Semantic và Scorer trong src/ | Chuyển logic sang file backend đúng cấu trúc; trả dict theo TypedDict chung, không nhập thêm bộ schema Pydantic song song |
| origin/TuanAnh, commit 8eae9aa | File change_analysis chính còn trống; có báo cáo owner | Không coi tài liệu owner là implementation |
| origin/feat/tho-reader-parser, commit 4d9d763 | Parser/PDF không có diff so với origin/main ở phần đã kiểm tra | Dùng Parser/PDF đã có trên nền; bổ sung adapter/Linker hẹp, không merge cả nhánh |

Text Diff giữ thuật toán SequenceMatcher(auto junk tắt), offset ký tự Python và nguyên văn. Baseline ngữ nghĩa giữ quy tắc hẹp về thời hạn/diễn đạt tương đương của Ngọc Anh, nhưng không tự đặt context_complete=True. Scorer không dùng số ký tự đổi hoặc similarity để chấm mức. Giao diện xử lý offset theo Unicode code points, tránh lệch khi JavaScript dùng UTF-16.

Nguồn tham khảo nội bộ được ghi trong docstring từng module; đây là adapter/hiện thực giới hạn, không khẳng định thay thế toàn bộ phần việc của owner. Các lựa chọn phương pháp chính thức trong decision.md vẫn cần nhóm review; không sửa chúng thành quyết định đã chốt.

Frontend hiện là prototype HTML/CSS/JavaScript cùng origin, không cần Node để chạy. Không chọn thay công nghệ frontend cuối cùng cho nhóm. Nội dung file hiển thị bằng text node; không đưa nguyên văn vào innerHTML. Không có tài khoản, database lịch sử hoặc lưu nhận xét.

## Bằng chứng chạy thật

Đã gửi file DOCX qua HTTP tới server local đang chạy, sau đó validate ComparisonReport. Đầu vào giữ nguyên, không lấy file V2 làm S.

| Bộ nguồn | Số mục ghi nhận | Có Text Diff | Trạng thái | Thời gian HTTP lần ghi nhận |
| --- | --- | --- | --- | --- |
| case_01 | 2 | 1 | PARTIAL | 671.675 ms |
| case_02 | 1 | 1 | PARTIAL | 1216.642 ms |
| case_03 | 13 | 13 | PARTIAL | 2204.599 ms |

Thời gian là một lần chạy cục bộ, không phải benchmark hoặc cam kết. “Có Text Diff” không đồng nghĩa kết luận pháp lý đúng hoặc mọi chỉ dẫn trong S đều đã được bao phủ. Chưa có gold được Dũng/người dùng review để đo độ chính xác.

- `data/demo-results/case_01.json`, `case_02.json`, `case_03.json` là báo cáo thực tế, gồm nguồn và cảnh báo.
- `data/demo-results/run-manifest.json` ghi SHA256 file đầu vào, thời điểm UTC, số mục và thời gian chạy.
- `data/demo-results/web-demo*.jpg` là ảnh chụp trình duyệt thực tế, gồm giao diện chọn file, báo cáo và thông báo sai định dạng.

Chạy lại phép thử HTTP sau khi khởi động server:

```powershell
python -m test.demo_suite.run_raw_demo
```

Lệnh sẽ cập nhật các JSON trong data/demo-results. Các ảnh không được script này tạo; cần chụp lại từ trình duyệt khi muốn cập nhật.

## Kiểm thử

```powershell
python -m unittest discover -s test/demo_suite -v
python -m unittest discover -s test/schema_suite -v
python -m unittest discover -s test/context_suite -v
```

- Web/backend: lần ghi nhận 11/11 có 12/12 đạt; sau hai commit sửa lỗi tại c192f43 có 30/30 đạt ngày 12/11. Bao gồm ba bộ thật, dựng lại after_text, DERIVED không giả quote, sai danh tính văn bản, ngoài phạm vi và phân biệt FAILED nghiệp vụ/lỗi thực thi. Kết quả sau đồng bộ docs ở common-baseline.md.
- Schema nền: 51 test, 49 đạt và 2 expected failures đã biết.
- Context/LightRAG: 26 test, 24 đạt và 2 real-service tests skipped. Không tuyên bố LightRAG thật đã chạy.
- Trình duyệt Edge: đã thử nạp mẫu, chọn file qua file chooser, thêm nhiều tham chiếu, bỏ file, gửi HTTP, xem kết quả và cảnh báo sai định dạng. Không có lỗi console trong lần kiểm tra. Chưa kiểm chứng riêng trên thiết bị di động hoặc trình duyệt khác.
- Nút xuất JSON có implementation Blob/download; thao tác bắt sự kiện download của công cụ kiểm thử bị timeout, chưa xác nhận độc lập file tải xuống trên trình duyệt. Các báo cáo HTTP đã được lưu và validate bằng script ở trên.

## Việc còn để hoàn thành demo có AI/retrieval

Chọn model/provider và môi trường chạy; xác nhận bộ gold; nối LightRAG thật với lifecycle/cách ly đã thiết kế; review context trước Semantic; kiểm chứng kết quả ngữ nghĩa và rubric. Không bật cờ “context đầy đủ” chỉ để có significance khác null. Không mở rộng thành phân tích mọi kiểu sửa đổi hoặc kết luận hiệu lực khi chưa có bằng chứng.

Code demo và sửa lỗi đã commit/push đến c192f43; đợt đồng bộ tài liệu hiện tại chưa tự commit/push hoặc merge main. Ảnh demo-summary.png có trước đợt web demo, không phải ảnh tạo mới trong lần cập nhật này.
