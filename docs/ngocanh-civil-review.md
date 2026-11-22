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

### Rà soát thao tác dựng trước/sau và Text Diff

Chọn hai ca từ Nghị định 10/2023/NĐ-CP để đối chiếu với Nghị định 43/2014/NĐ-CP ở phiên bản ngay trước lần sửa đổi năm 2023. Đây là ca kiểm thử lịch sử. Hai ca dưới đây đã được chọn và đối chiếu chỉ dẫn từ nguồn chính thức, còn chờ chạy nguyên văn qua Reader/Parser và Linker. [S bản ký](https://datafiles.chinhphu.vn/cpp/files/vbpq/2023/4/10-2023-cp.signed.pdf) · [V1 bản gốc](https://vanban.chinhphu.vn/?classid=1&docid=173985&pageid=27160)

| Thao tác | Ca đã chọn và kỳ vọng | Hiện trạng mã nguồn |
| --- | --- | --- |
| Sửa cụm từ | Khoản 2 Điều 5 của S đổi cụm “nơi đăng ký hộ khẩu thường trú” thành “nơi đăng ký thường trú” tại Điều 3a của V1; lấy Điều 3a từ lần bổ sung tại khoản 2 Điều 2 Nghị định 01/2017/NĐ-CP. Xác minh cụm cũ xuất hiện duy nhất trong đơn vị đích, dựng chuỗi sau với `after_basis=DERIVED` và kiểm tra diff dựng lại đầy đủ chuỗi sau. [Toàn văn S](https://xaydungchinhsach.chinhphu.vn/toan-van-nghi-dinh-so-10-2023-nd-cp-ngay-3-4-2023-sua-doi-bo-sung-mot-so-dieu-cua-cac-nghi-dinh-huong-dan-thi-hanh-luat-dat-dai-119230404170932622.htm) · [Nguồn Điều 3a trước sửa](https://congbao.chinhphu.vn/tai-ve-van-ban-so-01-2017-nd-cp-22024-16398?format=pdf) | Linker đã qua test synthetic với mẫu `Thay cụm từ … bằng … tại …`. Regex hiện chưa khớp cách viết `Thay thế cụm từ …` của ca thật đã chọn. |
| Bổ sung khoản | Khoản 4 Điều 1 của S bổ sung khoản 5 Điều 32 của V1, về chứng nhận quyền sở hữu công trình lưu trú du lịch trên đất thương mại, dịch vụ. Kiểm tra V1 đúng phiên bản, xác minh khoản 5 chưa tồn tại và vị trí chèn, rồi đối chiếu `INSERT` trên cùng phạm vi Điều 32 trước/sau. [Chỉ dẫn và nội dung khoản mới](https://xaydungchinhsach.chinhphu.vn/toan-van-nghi-dinh-so-10-2023-nd-cp-ngay-3-4-2023-sua-doi-bo-sung-mot-so-dieu-cua-cac-nghi-dinh-huong-dan-thi-hanh-luat-dat-dai-119230404170932622.htm) | Text Diff xử lý được chuỗi có đoạn chèn và phân biệt chuỗi rỗng với vế chưa biết (`null`). Linker nhận diện `ADD` nhưng chưa dựng cặp trước/sau cho khoản mới. |

Đã chạy lại `python -m unittest test.demo_suite.test_web_demo test.handoff_suite.test_ngocanh_week10 -q`, 25/25 test đạt. Kết quả này kiểm chứng hành vi hiện có, gồm thay cụm từ trên fixture và Text Diff trên các cặp chuỗi thử nghiệm. `case_09` bên dưới là ca thay nguyên khoản, có mục đích kiểm chứng riêng.

### Ứng viên dân sự `case_09`

Rà lại main `161e601` và nhánh Thọ `eb13550`. Dùng thêm ứng viên do Dũng lưu tại `33aeeec1c3681d8247d382689ac3f139d2727824`, gồm hai PDF Công báo có hash ghi trong manifest nguồn. Đây là nguồn chính thức cho phép kiểm chứng cục bộ trong khi chờ chốt dữ liệu chung. [Manifest trên nhánh dữ liệu](https://github.com/Lyra1603/group4_legal_document_change_detection/blob/33aeeec1c3681d8247d382689ac3f139d2727824/data/manifest.csv)

- **Đáp án trực tiếp.** S là Luật 43/2024/QH15, Điều 3 (Công báo trang 93). V1 là Luật Kinh doanh bất động sản 29/2023/QH15 bản ban hành 28/11/2023, khoản 1 Điều 82 (Công báo trang 87). Ngày hiệu lực ghi tại khoản này chuyển từ **01/01/2025** sang **01/08/2024**, nhóm `SCOPE_EFFECT_TRANSITION`. Điều 5 của S quy định hiệu lực của chính S. [V1 trên Công báo](https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2023/11/40868/47862-1-202443-4429-2023-qh15.pdf) · [S trên Công báo](https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2024/6/42578/51470-1-2024987-98843-2024-qh15.pdf)
- **B có căn cứ.** Khoản 1 Điều 38 Nghị định 96/2024/NĐ-CP bản ban hành 24/07/2024 dùng điều kiện chứng chỉ môi giới được cấp “trước ngày Luật Kinh doanh bất động sản có hiệu lực thi hành” để tiếp tục sử dụng theo thời hạn trên chứng chỉ. Khoản 12 Điều 83 V1 dùng cùng mốc. Do khoản 1 Điều 82 đổi ngày hiệu lực, dấu cắt của điều kiện này dịch từ 01/01/2025 sang 01/08/2024. Khi đối chiếu hai câu chữ, ngày cấp trong khoảng 01/08–31/12/2024 nằm trước mốc cũ và nằm ngoài điều kiện thời điểm của mốc mới. Đây là so sánh điều kiện chuyển tiếp, cần kiểm tra giấy cấp và quy định còn lại trước khi kết luận về một chứng chỉ cụ thể. B có ngày hiệu lực riêng tại Điều 39. [Điều 38–39 Nghị định 96/2024/NĐ-CP](https://xaydungchinhsach.chinhphu.vn/toan-van-nghi-dinh-96-2024-nd-cp-quy-dinh-chi-tiet-mot-so-dieu-cua-luat-kinh-doanh-bat-dong-san-119240827180542829.htm)
- **Giới hạn đối chiếu B.** Hiện có căn cứ và nhận định tham chiếu để review. API demo chưa có kết quả tác động gián tiếp để so với nhận định này. Đầu ra API ca `case_09` và đáp án thủ công được lưu riêng để tránh đưa kết luận mẫu vào kho retrieval.
- **Kết quả API.** Nộp cả hai PDF thật qua FastAPI TestClient, HTTP 200 với báo cáo `FAILED`. Linker trả `TARGET_DOCUMENT_UNRESOLVED` cho chỉ dẫn Điều 3 và các chỉ dẫn còn lại. Chỉ dẫn Điều 3 nằm trong một block cùng tiêu đề và nội dung trích, nên cần Thọ xem lại điểm nối Parser/Adapter–Linker. Cảnh báo nguồn PDF của API vẫn còn. Nộp riêng S trả HTTP 422 và yêu cầu `doc_v1`; đây là hành vi API hai file hiện tại.
- **Kết quả ở biên ba module.** Runner lấy hai đoạn đúng khoản từ PDF gốc theo vị trí chọn thủ công, xác minh chuỗi trích trên trang nguồn và kiểm tra offset/dựng lại. Semantic xác định trực tiếp mốc ghi trong khoản đã đổi, gán `SCOPE_EFFECT_TRANSITION` và giữ review cho ngữ cảnh, dẫn chiếu và chuyển tiếp. Scorer nối `change_id`, giữ nhóm này và trả `null` cho mức độ và cờ nghiêm trọng. Biến thể bỏ V1 dùng cùng nguồn S để kiểm tra Text Diff `null` và lý do thiếu V1. [API và đầu ra ba module](../data/ngocanh-civil-review/case_09_api.json)

### Tích hợp ca chung

Tại mốc bàn giao của Thọ `eb13550`, cặp S–V1 dân sự và kho nguồn còn chờ chọn, duyệt và bàn giao. Ca hồi quy ngân hàng sử dụng DOCX trong repo, không có ID hay phiên bản dữ liệu từ Hugging Face. Cần `AmendmentItem` với định danh phiên bản, vị trí, căn cứ trước/sau từ Thọ và Context nguồn đã đối chiếu từ Đức Anh để chạy ca dân sự. Ca chỉ nộp S và tự tìm V1 cần điểm nối của Pipeline. [Tiến độ Thọ tại eb13550](https://github.com/Lyra1603/group4_legal_document_change_detection/blob/eb13550/docs/tho-document-processing-progress.md)

Đức Anh có thể lấy `text_diff` trong JSON bàn giao để kiểm tra query. Dũng và Tuấn Anh có thể kiểm tra `semantic_diff`, `scoring`, quote và lý do review ở cùng item. Xác nhận của người nhận, lần chạy LightRAG thật và đối chiếu B còn chờ. Lần chạy này dùng quy tắc cục bộ, không cần cấu hình LLM.

Rà mã frontend tại `45223de` cho thấy UI nối kết quả chấm theo `change_id`, hiển thị bằng chứng Semantic, mức `null` thành “Chưa xác định” và lý do review. Ca PDF đi qua API còn dừng ở Linker, nên việc hiển thị đầu ra phân tích ca này mới được đối chiếu ở mức hợp đồng và mã nguồn.

## Chạy lại

Dùng Python 3.12 có `requirements-demo.txt`, từ thư mục gốc. Runner tạo đầy đủ report API và JSON theo từng điểm nối trong thư mục được chỉ định.

```powershell
python -m unittest test.handoff_suite.test_ngocanh_week10 -v
python -m test.handoff_suite.run_ngocanh_week10 --output .codex-tmp/ngocanh-verified-run
python -m unittest discover -s test -q
python -m unittest discover -s test/schema_suite -q
```

Để chạy thêm `case_09`, cần commit nguồn `33aeeec1` trong Git local và phụ thuộc PDF tùy chọn. Ca này dùng PyMuPDF 2.1 và pdf2docx 0.5.13 trong lần kiểm chứng.

```powershell
python -m pip install pdf2docx==0.5.13 pymupdf==2.1
python -m test.handoff_suite.run_ngocanh_civil_case .codex-tmp/ngocanh-verified-run/case_09_api.json
```
