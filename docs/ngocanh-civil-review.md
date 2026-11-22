# Text Diff, Semantic Diff và Scorer — bàn giao Ngọc Anh

Nền `origin/main` tại `161e60123911c9e6dac24248c07bf08dd13f8f2f`. Đối chiếu SRS §1.3, §1.4, §1.6 và Decision LK-07–10. [SRS](srs.md) · [Decision](decision.md)

## Thay đổi

- `detect_semantic_changes` ghi rõ khi Text Diff thiếu hoặc sai. Với Text Diff hợp lệ, kết quả vẫn giữ nguyên văn, bằng chứng và lý do cần kiểm tra. Schema và tám nhóm khía cạnh giữ nguyên theo LK-09.
- `score_changes` nối theo `change_id`, giữ nhóm chính đã xác định và chuyển cảnh báo của khía cạnh xuống kết quả chấm. Bỏ mức `HIGH` tự động cho thay đổi số ngày. Khi rubric chưa có căn cứ, `significance` và `is_critical` là `null`, `needs_review=true`. `WORDING_ONLY` vẫn dùng `LOW` theo SRS.
- Text Diff tiếp tục dùng offset Unicode code point, bắt đầu từ 0, khoảng `[start, end)` trên nguyên văn. `validate_text_diff` đối chiếu từng slice và dựng lại toàn bộ chuỗi sau.

## Ca có nguồn thật đã chạy

Ca hồi quy `case_02`, item `s:amendment_1`, đối chiếu khoản 5 Điều 16 Thông tư 22/2019/TT-NHNN với nội dung sửa đổi trong Thông tư 08/2020/TT-NHNN. Runner kiểm tra kho nguồn bàn giao bằng Parser/Adapter trên hai DOCX gốc. Bằng chứng gồm V1 `block:326`–`block:330`, chỉ dẫn S `block:12` và nguyên văn sau `block:13`–`block:17`. [Đầu vào](../data/ngocanh-week10/input/ban_giao_ca_dung.json) · [Kết quả ba module](../data/ngocanh-civil-review/tho_to_ngocanh_analysis.json)

- Text Diff sinh bốn thao tác và dựng lại chính xác khoản 5 sau sửa đổi. Các đoạn lặp có thể được căn chỉnh thành cặp xóa/thêm ở mức ký tự.
- Đối chiếu thủ công văn bản cho thấy dãy 40%, 37%, 34%, 30% giữ nguyên và mỗi mốc hạ tỷ lệ chuyển muộn một năm. Ví dụ, mốc áp dụng 30% dịch từ 01/10/2022 sang 01/10/2023. Nhóm tham chiếu thủ công là `TIME_QUANTITY` cho lộ trình áp dụng các ngưỡng. Đây là nhận định dựa trên hai đoạn trích của ca hồi quy.
- Semantic chạy quy tắc cục bộ và trả `is_meaningful_change=null`, `needs_review=true` do thiếu Context đã xác nhận và quy tắc chưa hỗ trợ lộ trình nhiều mốc. Scorer giữ `change_id=s:amendment_1:change_1`, mức độ và cờ nghiêm trọng đều `null`. Ba ca DOCX qua FastAPI TestClient trả HTTP 200 và `PARTIAL`. [Manifest và hash](../data/ngocanh-civil-review/manifest.json)
- Kiểm thử đủ Context dùng fixture ghi rõ là giả định, xác nhận quy tắc 30 → 15 ngày gán `TIME_QUANTITY` và giữ mức `null`. Kiểm thử thiếu nội dung V1, đích chưa rõ và thiếu Context được tạo bằng biến thể của input hồi quy. Nhánh thiếu V1 tại lớp phân tích trả Text Diff `null` và lý do review. [Ca âm](../data/ngocanh-civil-review/negative_cases.json)

## Ca dân sự, B và người nhận

Tại mốc bàn giao của Thọ `eb13550`, cặp S–V1 dân sự và kho nguồn còn chờ chọn, duyệt và bàn giao. Ca hồi quy ngân hàng sử dụng DOCX trong repo, không có ID hay phiên bản dữ liệu từ Hugging Face. Cần `AmendmentItem` với định danh phiên bản, vị trí, căn cứ trước/sau từ Thọ và Context nguồn đã đối chiếu từ Đức Anh để chạy ca dân sự. Ca chỉ nộp S và tự tìm V1 cần điểm nối của Pipeline. [Tiến độ Thọ tại eb13550](https://github.com/Lyra1603/group4_legal_document_change_detection/blob/eb13550/docs/tho-document-processing-progress.md)

Phiếu đối chiếu B đang chờ văn bản có nguồn. Khi có B, ghi điều/khoản và bản đang áp dụng của B, trích đoạn thể hiện B dùng đúng phần V1 bị sửa, rồi ghép với chỉ dẫn và hai đoạn trước/sau. Kiểm tra B dẫn tới phiên bản cố định hay áp dụng theo quy định thay đổi, cùng mốc hiệu lực và ngoại lệ. Ví dụ giả thuyết cho ca hồi quy, nếu một điều khoản B dùng ngưỡng của khoản 5 Điều 16 trong thời gian 01/10/2022–30/09/2023, cần đối chiếu ngưỡng 30% theo lộ trình cũ với 34% theo lộ trình mới; cần chính điều khoản B và căn cứ hiệu lực trước khi kết luận. Hiện chưa có bằng chứng B dùng khoản này hoặc kết quả hệ thống để đối chiếu.

Đức Anh có thể lấy `text_diff` trong JSON bàn giao để kiểm tra query. Dũng và Tuấn Anh có thể kiểm tra `semantic_diff`, `scoring`, quote và lý do review ở cùng item. Xác nhận của người nhận, lần chạy LightRAG thật và đối chiếu B còn chờ. Lần chạy này dùng quy tắc cục bộ, không cần cấu hình LLM.

## Chạy lại

Dùng Python 3.12 có `requirements-demo.txt`, từ thư mục gốc. Runner tạo đầy đủ report API và JSON theo từng điểm nối trong thư mục được chỉ định.

```powershell
python -m unittest test.handoff_suite.test_ngocanh_week10 -v
python -m test.handoff_suite.run_ngocanh_week10 --output .codex-tmp/ngocanh-verified-run
python -m unittest discover -s test -q
python -m unittest discover -s test/schema_suite -q
```
