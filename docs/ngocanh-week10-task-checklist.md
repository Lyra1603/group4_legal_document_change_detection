# Đối chiếu nhiệm vụ tuần 10 và giải thích kết quả của Ngọc Anh

Ngày đối chiếu: 16/11/2026. Thành viên: Đoàn Ngọc Anh. Căn cứ: bảng “Công việc của Ngọc Anh” được cung cấp, mã nguồn backend, đầu vào và kết quả trong `data/ngocanh-week10/`, cùng bộ kiểm thử riêng đã chạy đạt 12/12.

Text Diff đã có kết quả thật, offset đúng và kiểm tra dựng lại nội dung sau. Semantic đã có đầu ra đúng hợp đồng và giữ trạng thái chưa xác định khi thiếu căn cứ. Chưa hoàn tất toàn bộ nhiệm vụ vì còn thiếu kiểm chứng Semantic trên Context thật đầy đủ, tích hợp diff vào query và xác nhận chạy lại của bên nhận.

Tài liệu này tập trung đối chiếu danh sách nhiệm vụ và giải thích các câu hỏi cuối nhiệm vụ. Chi tiết thay đổi từng file, môi trường và lịch sử xử lý nằm trong [báo cáo công việc](ngocanh-week10-work-report.md).

## 1 Đối chiếu từng yêu cầu

| Nội dung trong nhiệm vụ | Trạng thái | Đã thực hiện và bằng chứng | Phần chưa hoàn thành |
| --- | --- | --- | --- |
| Đầu vào Text Diff | Đã kiểm chứng kỹ thuật | Nhận AmendmentItem thật `s:amendment_1`, có trước/sau của khoản 5 Điều 16; đối chiếu kho nguồn với DOCX case_02. So sánh hai trạng thái cùng khoản, không so toàn văn V1 với S | Thọ chưa xác nhận review trực tiếp trên phiên bản bàn giao này |
| Đầu ra Text Diff | Đã có output thật | TextDiffResult cùng amendment_id, có vùng chữ đổi và offset; validator kiểm tra slice và dựng lại after_text. File `ngocanh_to_ducanh_text_diff.json` dùng để bàn giao | Đức Anh chưa xác nhận dùng output thật đưa vùng đổi vào query |
| Semantic do Ngọc Anh làm chính | Đạt hợp đồng và xử lý thiếu căn cứ; chức năng còn giới hạn | Nhận item có cấu trúc Context cùng diff; trả SemanticDiffResult, change_id, evidence, quote và review. Ca thật thiếu context trả null; ca synthetic kiểm tra được quy tắc deadline và diễn đạt tương đương | Chưa có ca thật đủ Context được xác nhận để chứng minh phân tích nghĩa/aspects đầy đủ; chưa có xác nhận Dũng chạy lại |
| Đọc tài liệu | Đã đối chiếu trong đợt rà soát | Đã kiểm tra LK-04, LK-07, LK-08, LK-09, LK-12, CN-06 và các kiểu TextDiffResult, SemanticDiffResult, SemanticChange, ChangeAspect | Việc công cụ đã đọc không thay việc thành viên tự nắm nội dung để trình bày |
| Đọc code | Đã kiểm tra | Đã kiểm tra compute_text_diff, detect_semantic_changes, demo runner và test liên quan; xác định module demo dùng trong backend/app/change_analysis | Không có điểm chặn riêng cho nội dung này |
| Kiểm tra offset và dựng lại after_text | Đã thực hiện | Có validate_text_diff, test input thật, rỗng/None, Unicode, xuống dòng, văn bản lặp, diff sai và 200 cặp ngẫu nhiên | Helper chưa thay thế kiểm chứng reconstruction trong toàn bộ validator report chung |
| Semantic giữ đúng ID/nguồn, thiếu căn cứ trả null/review | Đã kiểm chứng trong phạm vi hỗ trợ | Kiểm tra diff, đích, thao tác, source_refs, reference/effect và cảnh báo thượng nguồn; không ép context_complete cho dữ liệu thật | Nguồn đúng không tự chứng minh đủ ngữ cảnh hoặc hiệu lực pháp lý |
| Phối hợp Thọ → diff | Đã chạy cục bộ | Dùng output JSON thật và kho nguồn, không sửa tay input để qua test | Chờ Thọ review và xác nhận |
| Phối hợp diff → query và Context → Semantic | Chưa hoàn tất | Đã có JSON diff thật và đầu vào Context theo schema; kiểm tra được ca Context thiếu | Query hiện chưa dùng TextDiffResult; chưa có Context thật đầy đủ được Đức Anh xác nhận |
| Phối hợp Semantic → Scorer | Đã chạy cục bộ | Gọi hàm score_changes hiện có trên Semantic vừa sinh; đúng change_id và giữ null/review | Dũng chưa chạy lại và xác nhận thay đổi này |
| Bàn giao diff thật, test dựng lại, ca lỗi/biên | Đã chuẩn bị đủ bằng chứng cục bộ | Có input/output, test, runner và manifest ghi commit nền/hash | Chưa có commit/PR chứa thay đổi hiện tại và xác nhận của người nhận |
| Bàn giao Semantic đúng schema và ca thiếu Context, được Dũng chạy lại | Đã có output và test; chưa đủ xác nhận | Có Semantic JSON, negative_cases và test thiếu Context độc lập | Điều kiện “được Dũng chạy lại” chưa có bằng chứng xác nhận |

“Đã kiểm chứng kỹ thuật” nghĩa là code/test thực thi được trên dữ liệu được ghi nhận. “Hoàn tất bàn giao” còn yêu cầu đúng người nhận dùng output đó chạy lại và xác nhận; hai trạng thái này được theo dõi riêng.

## 2 Các file bằng chứng để mở khi báo cáo

| Bằng chứng | Dùng để giải thích |
| --- | --- |
| [Input item thật](../data/ngocanh-week10/input/ban_giao_ca_dung.json) | Nhận từ đâu, sửa đơn vị nào, hai nội dung và trạng thái review |
| [Kho nguồn](../data/ngocanh-week10/input/ban_giao_kho_nguon.json) | Truy ngược document_id/source_refs/quote |
| [Output Text Diff](../data/ngocanh-week10/output/ngocanh_to_ducanh_text_diff.json) | Đoạn chữ đổi và offset trên từng chuỗi |
| [Output Semantic](../data/ngocanh-week10/output/ngocanh_to_dung_semantic.json) | Nhận định, evidence và lý do chưa xác định |
| [Output Scorer thực thi cục bộ](../data/ngocanh-week10/output/dung_scorer_actual.json) | change_id khớp và mức tác động null |
| [Ca thiếu hoặc sai dữ liệu](../data/ngocanh-week10/output/negative_cases.json) | Phản ứng khi thiếu before, đích chưa rõ hoặc Context chưa đủ |
| [Test riêng tuần 10](../test/handoff_suite/test_ngocanh_week10.py) | Assertion về reconstruction, nguồn, null/review và ca biên |
| [Manifest](../data/ngocanh-week10/output/manifest.json) | Phiên bản code/input và các xác nhận còn pending |

## 3 Giải thích câu hỏi đoạn nào đổi chữ

### 3.1 Ý nghĩa câu hỏi

Cần chỉ ra phần khác nhau cụ thể giữa `before_text` và `after_text` của đúng AmendmentItem, có thể đối chiếu trên nguồn. Không chỉ trả lời chung rằng “văn bản có thay đổi”, cũng không lấy câu lệnh sửa đổi trong S so trực tiếp với toàn văn V1.

### 3.2 Trả lời trên ca thật

Đơn vị so sánh là khoản 5 Điều 16, mã item `s:amendment_1`. Phần mở đầu của khoản và các tỷ lệ 40%, 37%, 34%, 30% được giữ trong hai chuỗi. Các mốc năm ở lộ trình có những khác biệt trực tiếp sau:

| Vị trí trong khoản | Nội dung trước | Nội dung sau | Khác biệt nhìn thấy trong nguyên văn |
| --- | --- | --- | --- |
| Điểm a | Đến hết ngày 30 tháng 9 năm 2020: 40% | Đến hết ngày 30 tháng 9 năm 2021: 40% | Năm kết thúc 2020 → 2021 |
| Điểm b | Từ ngày 01 tháng 10 năm 2020 đến hết ngày 30 tháng 9 năm 2021: 37% | Từ ngày 01 tháng 10 năm 2021 đến hết ngày 30 tháng 9 năm 2022: 37% | Năm bắt đầu 2020 → 2021; năm kết thúc 2021 → 2022 |
| Điểm c | Từ ngày 01 tháng 10 năm 2021 đến hết ngày 30 tháng 9 năm 2022: 34% | Từ ngày 01 tháng 10 năm 2022 đến hết ngày 30 tháng 9 năm 2023: 34% | Năm bắt đầu 2021 → 2022; năm kết thúc 2022 → 2023 |
| Điểm d | Từ ngày 01 tháng 10 năm 2022: 30% | Từ ngày 01 tháng 10 năm 2023: 30% | Năm bắt đầu 2022 → 2023 |

Bảng này là cách trình bày thủ công sự khác nhau của hai chuỗi đã nhận để người đọc dễ đối chiếu. Đây không phải danh sách ChangeAspect mà Semantic hiện đã tự suy ra, cũng không phải kết luận hiệu lực pháp lý.

Thuật toán SequenceMatcher trả bốn vùng thao tác ký tự:

| Vùng | Loại thao tác | Khoảng trước | Khoảng sau | Nội dung |
| --- | --- | --- | --- | --- |
| 1 | REPLACE | `[226, 227)` | `[226, 227)` | `0` → `1` |
| 2 | DELETE | `[235, 306)` | `[235, 235)` | Xóa một vùng ký tự cũ trong cách căn chỉnh |
| 3 | INSERT | `[372, 372)` | `[301, 372)` | Thêm một vùng ký tự mới trong cách căn chỉnh |
| 4 | REPLACE | `[406, 407)` | `[406, 407)` | `2` → `3` |

Số vùng thao tác ký tự không bằng số mốc năm thay đổi. Do các câu trong lộ trình lặp nhiều, thuật toán có thể chọn ghép đoạn giống nhau ở các vị trí khác nhau và biểu diễn phần còn lại bằng một vùng xóa/thêm dài. Vì vậy không được gọi vùng DELETE là “bãi bỏ điểm b” hoặc vùng INSERT là “bổ sung điểm c”.

### 3.3 Cách trả lời ngắn khi được hỏi

> Em so sánh nội dung trước và sau của cùng khoản 5 Điều 16. Những khác biệt dễ nhìn thấy nằm ở các mốc năm của lộ trình tại điểm a, b, c, d; các tỷ lệ vẫn giữ nguyên trong hai chuỗi. Text Diff biểu diễn chúng bằng bốn vùng chỉnh sửa ký tự. Em đã kiểm tra các vùng này khớp nguồn và dựng lại đúng toàn bộ nội dung sau; em không diễn giải thao tác xóa/thêm ký tự thành bãi bỏ/bổ sung quy phạm.

## 4 Giải thích câu hỏi offset thuộc chuỗi nào

### 4.1 Ý nghĩa câu hỏi

Offset phải có hệ tọa độ rõ ràng để bên nhận cắt đúng vùng chữ và tô sáng đúng vị trí. Cần biết đó là vị trí trong chuỗi trước hay sau, đếm theo đơn vị nào, tính từ đâu và có thay đổi chuỗi trước khi đếm hay không.

### 4.2 Quy ước đang dùng

| Trường offset | Thuộc chuỗi | Cách đối chiếu |
| --- | --- | --- |
| old_start, old_end | `item['before_text']` nguyên bản | `before_text[old_start:old_end] == old_text` |
| new_start, new_end | `item['after_text']` nguyên bản | `after_text[new_start:new_end] == new_text` |

Các vị trí bắt đầu từ 0, đếm theo Unicode code point của Python. Khoảng `[start, end)` bao gồm vị trí start và không bao gồm end. Đây không phải byte UTF-8, số trang Word, chỉ số block nguồn hoặc độ dài UTF-16 của JavaScript. Một ký tự hiển thị có dấu ở dạng tổ hợp có thể gồm nhiều code point; vì vậy Text Diff giữ nguyên chuỗi thay vì chuẩn hóa trước khi tính offset.

Ví dụ vùng đầu tiên của ca thật:

```python
before_text[226:227] == '0'
after_text[226:227] == '1'
```

Với vùng thêm, khoảng cũ có thể rỗng: `[372, 372)` chỉ vị trí chèn ở chuỗi trước; vùng chữ mới nằm ở `[301, 372)` của chuỗi sau. Không dùng old_start để cắt chuỗi sau vì những thay đổi trước đó có thể làm hai hệ vị trí lệch nhau.

Các offset trên chuỗi cục bộ cũng không thể áp thẳng vào toàn văn DOCX. Muốn về nguồn cần dùng `document_id` và `source_refs` của evidence. Ở ca này, trước là `v1` block:326–330, chỉ dẫn là `s` block:12, sau là `s` block:13–17.

### 4.3 Kiểm tra dựng lại nội dung sau

Khi áp dụng diff, lần lượt lấy phần chưa đổi của chuỗi trước, nối new_text của vùng thay đổi, rồi bỏ qua old_text tương ứng. Sau vùng cuối, nối phần còn lại của chuỗi trước. Kết quả phải bằng after_text nguyên bản.

`validate_text_diff` còn kiểm tra ID, kiểu offset là số nguyên, giới hạn chuỗi, thứ tự, không chồng lấn, loại thao tác và cả các khoảng được coi là không đổi. Kiểm tra từng slice riêng lẻ chưa đủ vì diff có thể bỏ sót một vùng thay đổi.

### 4.4 Cách trả lời ngắn khi được hỏi

> old_start/old_end thuộc before_text; new_start/new_end thuộc after_text của cùng item. Em đếm từ 0 theo code point Python và dùng khoảng nửa mở. Em không sửa hoặc chuẩn hóa hai chuỗi trước khi tính. Ngoài kiểm tra slice, em dùng toàn bộ diff dựng lại after_text để bảo đảm không bỏ sót vùng đổi.

## 5 Giải thích câu hỏi kết luận đổi nghĩa dựa vào đâu

### 5.1 Ý nghĩa câu hỏi

Cần giải thích cầu nối từ sự khác biệt câu chữ đến nhận định về nội dung quy định. Có thay đổi ký tự chưa tự chứng minh tác động pháp lý; ít ký tự thay đổi cũng chưa chứng minh tác động nhỏ. Kết luận phải gắn với đúng đơn vị đích, nguyên văn hai phía, bằng chứng và ngữ cảnh liên quan, cùng phương pháp hỗ trợ trường hợp đó.

Để có một kết luận được chấp nhận trong phạm vi hệ thống, cần kiểm tra:

1. Đúng văn bản và đơn vị đích; không còn mơ hồ về việc chỉ dẫn áp dụng vào đâu.
2. Nội dung trước/sau có căn cứ và nguồn truy ngược; phân biệt QUOTED với DERIVED.
3. Diff đúng item và đúng hai chuỗi; không bị truyền nhầm hoặc thiếu vùng thay đổi.
4. Đủ ngữ cảnh liên quan: định nghĩa, điều kiện, ngoại lệ, dẫn chiếu, hiệu lực và chuyển tiếp; không chỉ dựa vào việc có trường Context.
5. Quy tắc hoặc phương pháp ngữ nghĩa thực sự hỗ trợ dạng thay đổi; có diễn giải và aspects khi xác định được đổi nghĩa.
6. Không còn cảnh báo chưa giải quyết làm ảnh hưởng đến kết luận đó.

Đây là điều kiện kiểm chứng của dự án, không phải khẳng định chỉ cần một cờ hoặc đủ trường JSON là đã đủ căn cứ nghiệp vụ.

### 5.2 Phương pháp hiện tại hỗ trợ đến đâu

| Trường hợp | Điều kiện của baseline | Hành vi hiện tại |
| --- | --- | --- |
| Hai nội dung cục bộ giống nhau sau NFC và bỏ khoảng trắng đầu/cuối | Các chốt nguồn, diff, đích và context đều đạt | Không tạo SemanticChange; không kết luận toàn bộ S không có sửa đổi |
| “chậm nhất vào ngày” ↔ “không muộn hơn ngày” | Phần còn lại giống nhau và các chốt kiểm tra đều đạt | Một thay đổi được xác định không đổi nghĩa theo quy tắc hẹp, aspects rỗng |
| Đổi đúng một số nguyên dương trong “trong thời hạn N ngày” | Chỉ số N khác, phần còn lại giống nhau và các chốt đều đạt | Xác định đổi nghĩa theo quy tắc deadline; tạo aspect TIME_QUANTITY |
| Thiếu căn cứ, thao tác chưa hỗ trợ hoặc ngoài dạng quy tắc | Có chốt chưa đạt hoặc không có quy tắc phù hợp | Giữ nhận định null, needs_review=true và lý do |

Các ca có kết luận ở trên được kiểm thử bằng dữ liệu synthetic. Điều đó chứng minh hành vi phần mềm theo quy tắc đã viết, chưa chứng minh độ chính xác ngữ nghĩa trên một tập pháp lý độc lập. Mức tác động do Scorer xử lý và rubric review riêng; một kết luận có đổi nghĩa không tự quyết định HIGH hay CRITICAL.

### 5.3 Kết luận thực tế của ca đang bàn giao

Ca thật hiện chưa có kết luận đổi nghĩa. Output trả:

```json
{
  "is_meaningful_change": null,
  "aspects": [],
  "needs_review": true
}
```

Đây là trích các trường chính của SemanticChange, không phải payload đầy đủ. File output có thêm ID, nguyên văn, evidence và review_reason.

Lý do chưa xác định:

- Input đã có cảnh báo chưa xác minh đầy đủ ngữ cảnh và hiệu lực pháp lý.
- Context hiện rỗng và không có xác nhận đầy đủ; danh sách reference/effect rỗng không chứng minh không có dẫn chiếu hoặc vấn đề hiệu lực cần xét.
- Runner giữ `context_complete=False`, không bật cờ để đi vào nhánh sinh kết luận.
- Ca này thay nhiều mốc năm trong một lộ trình, không thuộc quy tắc chỉ thay đúng một số trong cụm “trong thời hạn N ngày”. Ngay cả khi context được xác nhận, vẫn cần phương pháp phù hợp với dạng này.

Ba giá trị cần phân biệt:

| Giá trị | Cách hiểu đúng |
| --- | --- |
| true | Phương pháp đã xác định có đổi nghĩa trong điều kiện hỗ trợ |
| false | Phương pháp đã xác định không đổi nghĩa trong điều kiện hỗ trợ |
| null | Chưa đủ căn cứ hoặc chưa có phương pháp hỗ trợ để quyết định |

`null` không phải “không đổi nghĩa”, cũng không phải lỗi schema. Scorer giữ category, significance và is_critical đều null cho output hiện tại, đồng thời giữ lý do review.

### 5.4 Cách trả lời ngắn khi được hỏi

> Em chỉ kết luận dựa trên nguyên văn hai phía có nguồn, đúng đích, diff hợp lệ, ngữ cảnh được kiểm chứng và quy tắc hỗ trợ. Với ca khoản 5 Điều 16 này, em mới xác nhận được phần chữ thay đổi. Context và hiệu lực còn chưa xác minh, đồng thời quy tắc hiện tại chưa bao phủ lộ trình nhiều mốc năm, nên em trả null/review và giữ bằng chứng. Em chưa khẳng định ca này không đổi nghĩa, cũng chưa chấm mức tác động.

## 6 Việc cần làm tiếp để chốt danh sách

| Thứ tự | Việc cần hoàn thành | Người phối hợp | Điều kiện ghi nhận xong |
| --- | --- | --- | --- |
| 1 | Review dữ liệu thật và diff | Thọ + Ngọc Anh | Kiểm tra đúng đơn vị, hai nội dung, nguồn và reconstruction |
| 2 | Dùng TextDiffResult thật trong query | Đức Anh, phối hợp Dũng | Query giữ đúng amendment_id và thực sự dùng vùng chữ đổi sau khi index sẵn sàng |
| 3 | Bàn giao Context được kiểm chứng | Đức Anh + Ngọc Anh | Ghi rõ căn cứ đủ/thiếu và phần hiệu lực liên quan, không đổi cờ thay cho xác minh |
| 4 | Chạy và mở rộng Semantic cho ca đủ căn cứ | Ngọc Anh, phối hợp người review | Có output giải thích được; dạng chưa hỗ trợ vẫn được công bố rõ |
| 5 | Người nhận chạy lại Scorer | Dũng + Ngọc Anh | Dũng dùng output Semantic thật, không sửa tay để chạy qua, xác nhận đúng change_id/null/reason |
| 6 | Gắn thay đổi với phiên bản bàn giao | Ngọc Anh và reviewer | Có commit/PR, lệnh test, input/output và xác nhận người nhận |

Khi báo cáo hiện tại, có thể ghi: “Đã hoàn thành kiểm chứng cục bộ Text Diff và cơ chế Semantic giữ null/review; đã chuẩn bị output thật và test. Còn chờ tích hợp query, Context đầy đủ và xác nhận chạy lại của người nhận.” Không nên ghi toàn bộ nhiệm vụ đã được nghiệm thu.
