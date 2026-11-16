# Báo cáo công việc và bàn giao tuần 10 của Đoàn Ngọc Anh

Ngày lập báo cáo: 16/11/2026. Thành viên: Đoàn Ngọc Anh, mã sinh viên 24021363. Phạm vi phụ trách chính: Text Diff và Semantic Diff theo phân công tuần 10.

Phần Text Diff đã được kiểm chứng trên dữ liệu thật, trả đúng định danh và có thể dựng lại chính xác nội dung sau sửa đổi. Phần Semantic đã được bổ sung kiểm tra đầu vào, giữ nguồn và cảnh báo khi chưa đủ căn cứ. Với ca thật đang bàn giao, kết luận ngữ nghĩa và mức tác động vẫn chưa xác định do ngữ cảnh, hiệu lực chưa được xác nhận và phương pháp hiện tại còn giới hạn. Gói đầu vào, đầu ra và lệnh chạy lại đã có; xác nhận của người nhận còn chờ.

## 1 Phạm vi công việc và trách nhiệm

| Công việc | Trách nhiệm của Ngọc Anh | Người phối hợp hoặc nhận kết quả |
| --- | --- | --- |
| Tiếp nhận AmendmentItem | Kiểm tra có đúng item, đơn vị đích, trước/sau và bằng chứng để tính diff | Thọ cung cấp dữ liệu |
| Text Diff | Tính vùng thêm, xóa, thay thế; kiểm tra ID, offset và dựng lại nội dung sau | Đức Anh nhận diff để tạo query; Semantic sử dụng |
| Semantic Diff | Nhận item có Context cùng Text Diff; trả nhận định, aspects, bằng chứng, trạng thái cần kiểm tra | Đức Anh cung cấp Context; Dũng nhận Semantic |
| Kiểm thử Semantic → Scorer | Chạy hàm Scorer hiện có trên output Semantic, kiểm tra change_id và null/review | Dũng làm chính Scorer và review kết quả |
| Báo cáo và bàn giao | Ghi rõ phần chạy thật, phần synthetic, giới hạn và điều kiện xác nhận | Thọ, Đức Anh và Dũng |

Phân công cụ thể tuần 10 được dùng để xác định người làm chính. Những nhiệm vụ Scorer, Context/query, Pipeline/API và UI có liên quan đến điểm nối nhưng không được tự tính toàn bộ là phần việc Ngọc Anh đã triển khai.

## 2 Nền mã nguồn dùng để thực hiện

- Nhánh đang làm: `ngocanh/text_diff`.
- Commit nền: `a0f45b1c1054a122d800ce2a0d19a0bf6c28bb3a`.
- Entry point demo: `backend.demo:app`.
- Module Text Diff thực sự được demo gọi: `backend/app/change_analysis/text_diff.py`.
- Module Semantic thực sự được demo gọi: `backend/app/change_analysis/semantic_diff.py`.
- Hợp đồng dữ liệu: `backend/app/schemas/contracts.py`.
- Trạng thái thay đổi tại thời điểm lập báo cáo: còn ở working tree, chưa commit/push trong phiên thực hiện này.

`src/text_diff/diff_engine.py`, `src/semantic_diff/diff_engine.py` và `src/classifier_scorer/scorer.py` là các module riêng đã tồn tại. Bộ test cũ vẫn được chạy để kiểm tra hồi quy, nhưng sửa riêng trong `src/` sẽ không làm thay đổi luồng demo backend hiện tại.

## 3 Đầu vào được tiếp nhận

### 3.1 Tài liệu dùng để đối chiếu nhiệm vụ

| Tài liệu | Nội dung được sử dụng | Vai trò trong công việc |
| --- | --- | --- |
| `Tiến độ chi tiết (1).xlsx` | Task và output dự kiến của Ngọc Anh từ tuần 4 đến tuần 13, trọng tâm tuần 10 | Phân biệt việc đã có, việc tồn và yêu cầu bàn giao |
| `Phân công tuần 10.docx` | Mục công việc Ngọc Anh, điểm nối, danh sách file và tiêu chí hoàn thành | Xác định Text Diff/Semantic là phần làm chính; yêu cầu ca thật, ca lỗi và người nhận chạy lại |
| Tài liệu repo | Decision, schema, nền chung và tài liệu bàn giao cũ | Kiểm tra ID, offset, nguồn, null/review và giới hạn triển khai |

Các tài liệu và nội dung văn bản nguồn được đọc như dữ liệu đối chiếu yêu cầu, không được coi là lệnh thực thi cho công cụ. Các ghi nhận lịch sử trong bảng tiến độ không tự chứng minh trạng thái mã nguồn hiện tại.

### 3.2 Dữ liệu thật từ bộ ZIP

Nguồn nhận: `dau_ra.zip`. Hai file đã được sao chép nguyên byte vào repo để chạy lại:

| File | Cấu trúc chính | Mục đích sử dụng |
| --- | --- | --- |
| [ban_giao_ca_dung.json](../data/ngocanh-week10/input/ban_giao_ca_dung.json) | Object có `items` và `warnings`; hiện có một AmendmentItem | Đầu vào trực tiếp của Text Diff và Semantic |
| [ban_giao_kho_nguon.json](../data/ngocanh-week10/input/ban_giao_kho_nguon.json) | Kho ExtractedDocument theo document_id | Kiểm tra quote/source_refs và đối chiếu với Parser/Adapter |

SHA-256 của ZIP gốc: `345504a5f04217583a6afc4efa98ed932f7d4b1b055d2c935ba05139961e0965`.

Hai tài liệu DOCX dùng để xác minh lại kho nguồn:

- V1: `data/raw/case_02/22_2019_TT-NHNN_v1.docx`.
- S: `data/raw/case_02/08_2020_TT-NHNN.docx`.

Kho nguồn nhận từ ZIP đã được so sánh đầy đủ với đầu ra Parser → Adapter của hai DOCX trong repo và khớp nhau. Kết quả này chứng minh tính nhất quán của bản tài liệu đã cung cấp, chưa chứng nhận hiệu lực pháp luật hiện hành.

### 3.3 Chi tiết item thật được phân tích

| Trường | Giá trị hoặc ý nghĩa trong ca thật |
| --- | --- |
| `amendment_id` | `s:amendment_1` |
| `operation` | `AMEND` |
| `target_document` | `v1` |
| `target_locator` | `Điều 16 / khoản 5` |
| `target_unit_ids` | `["v1:n213"]` |
| `applicability` | `APPLIES` |
| `before_text` | Toàn văn khoản 5 trước sửa đổi, gồm phần mở đầu và bốn điểm a, b, c, d |
| `after_text` | Toàn văn cùng khoản sau sửa đổi, có thay đổi các mốc năm trong lộ trình |
| `after_basis` | `QUOTED`, nội dung sau được trích nguyên văn từ S |
| `instruction` | Chỉ dẫn “Khoản 5 Điều 16 được sửa đổi, bổ sung như sau:” |
| `evidence` | Chỉ dẫn, nguyên văn nội dung sau và nguyên văn nội dung trước |
| `context.general_context` | Chuỗi rỗng |
| `context.evidence` | Danh sách rỗng |
| `context.references` | Danh sách rỗng |
| `effect_info` | Danh sách rỗng |
| `needs_review` | `true` |
| `review_reason` | `Chưa xác minh đầy đủ ngữ cảnh và hiệu lực pháp lý.` |

Các nguồn có thể truy ngược:

| Thành phần | document_id | source_refs |
| --- | --- | --- |
| Nội dung trước | `v1` | `block:326` đến `block:330` |
| Câu lệnh sửa đổi | `s` | `block:12` |
| Nội dung sau | `s` | `block:13` đến `block:17` |

Text Diff so sánh hai nội dung cục bộ của cùng khoản này. Không đưa toàn văn V1 và toàn văn S vào so sánh trực tiếp để thay thế bước xác định đích.

### 3.4 Điều kiện đầu vào của từng module

Text Diff nhận một `AmendmentItem`, sử dụng `amendment_id`, `before_text` và `after_text`. Nếu một phía là `None`, hàm trả `None` vì chưa có đủ cặp nội dung. Chuỗi rỗng `""` vẫn là dữ liệu đã biết và có thể được so sánh.

Semantic nhận `item`, `text_diff` và tham số keyword `context_complete`, mặc định `False`. Ngoài hai chuỗi, module còn kiểm tra thao tác, đích, căn cứ nội dung sau, nguồn, dẫn chiếu, hiệu lực và cảnh báo thượng nguồn. Chỉ truyền `context_complete=True` khi phía chuẩn bị ngữ cảnh đã xác minh thực tế; không đặt cờ chỉ để sinh kết luận.

## 4 Đầu ra đã tạo và cách sử dụng

### 4.1 Danh sách file đầu ra

Tất cả file dưới đây nằm trong `data/ngocanh-week10/output/` và được sinh bằng chương trình.

| File | Cấu trúc | Người nhận hoặc mục đích |
| --- | --- | --- |
| [ngocanh_to_ducanh_text_diff.json](../data/ngocanh-week10/output/ngocanh_to_ducanh_text_diff.json) | Danh sách TextDiffResult, hiện có một phần tử | Đức Anh sử dụng vùng chữ đổi để tạo query |
| [ngocanh_to_dung_semantic.json](../data/ngocanh-week10/output/ngocanh_to_dung_semantic.json) | Danh sách SemanticDiffResult, hiện có một phần tử | Dũng đưa từng kết quả vào Scorer |
| [dung_scorer_actual.json](../data/ngocanh-week10/output/dung_scorer_actual.json) | Danh sách các danh sách ScoringResult, tương ứng từng item | Bằng chứng đã chạy hàm Scorer thật cục bộ |
| [tho_to_ngocanh_analysis.json](../data/ngocanh-week10/output/tho_to_ngocanh_analysis.json) | Danh sách object gồm amendment, text_diff, semantic_diff, scoring | Truy vết từ input thật đến ba kết quả |
| [negative_cases.json](../data/ngocanh-week10/output/negative_cases.json) | Ba ca biến đổi kiểm thử, có nhãn scenario và result | Kiểm tra thiếu before, đích chưa rõ và thiếu context |
| [case_01_api_report.json](../data/ngocanh-week10/output/case_01_api_report.json) | ComparisonReport | Bằng chứng upload DOCX thật qua API bằng TestClient |
| [case_02_api_report.json](../data/ngocanh-week10/output/case_02_api_report.json) | ComparisonReport | Báo cáo API của ca chung |
| [case_03_api_report.json](../data/ngocanh-week10/output/case_03_api_report.json) | ComparisonReport | Kiểm tra nhiều item trong một lượt |
| [manifest.json](../data/ngocanh-week10/output/manifest.json) | Metadata lần chạy, hash code/input, kết quả và xác nhận còn chờ | Đối chiếu phiên bản khi chạy lại |

Các file đầu ra dạng danh sách phục vụ bàn giao nhiều item. Khi gọi `score_changes`, truyền từng object SemanticDiffResult trong danh sách, không truyền cả file JSON như một SemanticDiffResult duy nhất.

### 4.2 Chi tiết Text Diff

Mỗi TextDiffResult gồm `amendment_id` và danh sách `changes`. Mỗi change có loại thao tác, chuỗi cũ/mới và hai khoảng offset:

| Trường | Ý nghĩa |
| --- | --- |
| `type` | `INSERT`, `DELETE` hoặc `REPLACE` ở mức chuỗi ký tự |
| `old_text` | Nội dung `before_text[old_start:old_end]` |
| `new_text` | Nội dung `after_text[new_start:new_end]` |
| `old_start`, `old_end` | Vị trí trên đúng chuỗi trước |
| `new_start`, `new_end` | Vị trí trên đúng chuỗi sau |

Offset dùng Unicode code point Python, bắt đầu từ 0, theo khoảng nửa mở `[start, end)`. Không chuẩn hóa hoặc thay khoảng trắng của chuỗi trước khi tính offset.

Ca thật có bốn vùng thao tác:

| Thứ tự | Loại | Khoảng trên chuỗi trước | Khoảng trên chuỗi sau | Ghi nhận |
| --- | --- | --- | --- | --- |
| 1 | REPLACE | `[226, 227)` | `[226, 227)` | `0` → `1` |
| 2 | DELETE | `[235, 306)` | `[235, 235)` | Một vùng ký tự cũ dài 71 code point |
| 3 | INSERT | `[372, 372)` | `[301, 372)` | Một vùng ký tự mới dài 71 code point |
| 4 | REPLACE | `[406, 407)` | `[406, 407)` | `2` → `3` |

Hai vùng thêm/xóa dài xuất hiện do SequenceMatcher căn chỉnh văn bản có nhiều đoạn lặp. Các thao tác này là mô tả chỉnh sửa chuỗi; không thể từ đó suy ra có bổ sung hoặc bãi bỏ một quy phạm. Tiêu chí kỹ thuật đã đạt là các slice khớp và áp dụng đầy đủ diff sẽ dựng lại đúng toàn bộ `after_text`.

### 4.3 Chi tiết Semantic Diff

SemanticDiffResult trả cùng `amendment_id`, danh sách SemanticChange và trạng thái review tổng. Mỗi SemanticChange có `change_id`, nhận định đổi nghĩa, giải thích, aspects, evidence, quote trước/sau và lý do cần kiểm tra.

Kết quả thật hiện tại:

```json
{
  "amendment_id": "s:amendment_1",
  "change_id": "s:amendment_1:change_1",
  "is_meaningful_change": null,
  "aspects": [],
  "needs_review": true
}
```

Đây là trích các trường chính để giải thích, không phải payload đầy đủ thay cho schema. File output đầy đủ có evidence, quote, diff_details và review_reason.

`null` nghĩa chưa xác định, khác với `false` là đã xác định không đổi nghĩa. `aspects=[]` trong ca chưa xác định không phải bằng chứng rằng không có thay đổi khía cạnh. Module giữ nguyên nguyên văn trước/sau và nguồn để người nhận kiểm tra tiếp.

Lý do giữ chưa xác định gồm cảnh báo ngữ cảnh/hiệu lực từ input, chưa xác nhận context đầy đủ và chưa có quy tắc hỗ trợ đủ cho thay đổi lộ trình nhiều mốc năm của ca này. Việc nhìn thấy con số thay đổi không đủ để tự hoàn thiện kết luận pháp lý.

### 4.4 Đầu ra kiểm thử chéo Scorer

Hàm `score_changes` hiện có đã được chạy trên Semantic thật ở trên. Kết quả nối đến `s:amendment_1:change_1`, với:

```json
{
  "change_id": "s:amendment_1:change_1",
  "category": null,
  "significance": null,
  "is_critical": null,
  "reason": "Chưa chấm mức tác động khi ngữ nghĩa/ngữ cảnh chưa xác nhận.",
  "needs_review": true
}
```

Trích đoạn này lược bỏ review_reason; file thật giữ đầy đủ lý do. Scorer thuộc phần Dũng làm chính. Phiên này kiểm thử khả năng nhận output và giữ trạng thái chưa xác định, chưa sửa thuật toán Scorer hoặc xác nhận rubric đã được duyệt.

## 5 Những công việc đã thực hiện

| Công việc | Cách thực hiện | Kết quả hoặc bằng chứng |
| --- | --- | --- |
| Xác định đúng module đang chạy | Đọc entry point, demo runner và import | Xác định backend/change_analysis là nơi cần bổ sung |
| Đối chiếu nhiệm vụ | Đọc bảng tiến độ, phân công tuần 10, schema và Decision | Tách Text Diff/Semantic của Ngọc Anh với Scorer/Context của người phối hợp |
| Tiếp nhận ca thật | Sao chép hai JSON từ ZIP, không sửa nội dung | Có input cố định trong repo để chạy lại |
| Kiểm chứng nguồn | Parse DOCX, adapt documents, so sánh kho nguồn và validate bằng chứng/đích | Kho nguồn khớp, item truy ngược về block gốc |
| Kiểm tra độ đúng Text Diff | Kiểm tra ID, offset, chuỗi slice, thứ tự và reconstruction | Ca thật và ca biên dựng lại đúng nội dung sau |
| Bổ sung chốt kiểm tra Semantic | Dùng diff thật để xác minh; kiểm tra đích, thao tác, nguồn, reference/effect và review | Đầu vào thiếu hoặc sai không được nâng thành kết luận chắc chắn |
| Kiểm thử chéo Scorer | Gọi hàm hiện có trên Semantic vừa sinh | Đúng change_id, giữ null/review |
| Tạo chương trình bàn giao | Viết runner từ repo root | Sinh output cùng manifest và ba report API |
| Chạy hồi quy | Chạy schema, context, demo, handoff và src cũ | Không phát hiện test hồi quy mới bị hỏng |
| Cập nhật tài liệu | Thêm báo cáo và ghi chú vào tài liệu ngày 07/11 | Giảm nhầm lẫn giữa bản lịch sử với trạng thái mới |

## 6 Các file đã thay đổi và lý do

### 6.1 File đã có được chỉnh sửa

| File | Nội dung thay đổi | Mục đích và lý do |
| --- | --- | --- |
| [backend/app/change_analysis/text_diff.py](../backend/app/change_analysis/text_diff.py) | Thêm `validate_text_diff(item, result)`; giữ thuật toán tính diff hiện có | Có kiểm tra dùng lại tại điểm nối, phát hiện diff sai ID, sai offset, chồng lấn, sai loại thao tác hoặc bỏ sót vùng thay đổi |
| [backend/app/change_analysis/semantic_diff.py](../backend/app/change_analysis/semantic_diff.py) | Gọi validator diff; kiểm tra applicability, target_unit_ids, operation, reference/effect, review_reason; yêu cầu source_refs có nội dung; dùng document_id từ instruction cho quote sau | Tham số text_diff trước đây chưa được kiểm tra; tránh kết luận chắc chắn khi upstream thiếu căn cứ hoặc truyền nhầm kết quả |
| [.gitignore](../.gitignore) | Bỏ qua hai môi trường Python tạm và helper trích dữ liệu của lần kiểm chứng | Không đưa dependency/môi trường cục bộ và script tạm vào gói source bàn giao |
| [docs/ngocanh-handover.md](ngocanh-handover.md) | Thêm ghi chú đầu file dẫn đến báo cáo tuần 10 | Bản 07/11 có mô tả pipeline và mức tác động đã cũ; cần giữ lịch sử nhưng hướng người đọc đến trạng thái mới |
| [docs/yeu-cau-ban-giao-tho-ngocanh.md](yeu-cau-ban-giao-tho-ngocanh.md) | Thêm ghi chú về dữ liệu thật đã nhận, phân công mới và mức tác động null | Phân biệt đề xuất bàn giao cũ với dữ liệu đã chạy và trách nhiệm hiện tại |

`validate_text_diff` chỉ kiểm tra, không tự sửa diff sai. Semantic bắt lỗi kiểm tra tại điểm nối để trả kết quả cần review. Kiểm chứng reconstruction mới chưa được đưa vào mọi nơi gọi report validator của dự án.

### 6.2 File mới được tạo

| File hoặc nhóm file | Nội dung | Mục đích và lý do tạo |
| --- | --- | --- |
| [test/handoff_suite/test_ngocanh_week10.py](../test/handoff_suite/test_ngocanh_week10.py) | 12 test, gồm input thật và các ca synthetic có assertion | Kiểm chứng riêng tiêu chí tuần 10, đặc biệt reconstruction và thiếu context |
| [test/handoff_suite/run_ngocanh_week10.py](../test/handoff_suite/run_ngocanh_week10.py) | Chương trình chạy input thật, source validation, Semantic/Scorer và API | Để người nhận tái lập được output mà không sửa tay hoặc dựa vào ảnh chụp |
| `data/ngocanh-week10/input/ban_giao_ca_dung.json` | Item nhận từ ZIP | Giữ nguyên đầu vào có thể tái lập |
| `data/ngocanh-week10/input/ban_giao_kho_nguon.json` | Kho nguồn nhận từ ZIP | Có dữ liệu đối chứng cho nguồn và quote |
| Chín file trong `data/ngocanh-week10/output/` | Diff, Semantic, Scorer, kết quả tổng hợp, ca lỗi, ba report API và manifest | Cung cấp đầu ra thực thi và bằng chứng phiên bản |
| `docs/ngocanh-week10-work-report.md` | Báo cáo chi tiết hiện tại | Tổng hợp đầu vào/đầu ra, việc đã làm, vướng mắc, file thay đổi và lý do để báo cáo cá nhân |

Các file JSON trong output là kết quả sinh tự động. `.codex-tmp/ngocanh-py312/`, `.codex-tmp/ngocanh-venv/` và `.codex-tmp/read_inputs.py` chỉ là công cụ môi trường cục bộ, không phải module sản phẩm. Scorer, Context, schema, API, UI và các module src cũ không được sửa trong đợt này.

## 7 Vướng mắc đã gặp và cách xử lý

| Vướng mắc | Ảnh hưởng | Cách xử lý hoặc trạng thái |
| --- | --- | --- |
| File src đang mở khác module demo gọi | Sửa nhầm vị trí sẽ không ảnh hưởng luồng chung | Đọc import và bổ sung ở backend/app/change_analysis |
| Tài liệu bàn giao cũ có thông tin không còn đúng | Dễ báo thiếu pipeline dù code mới đã chạy, hoặc mặc định mức HIGH | Thêm ghi chú lịch sử và báo cáo hiện trạng mới |
| Lệnh python mặc định qua Windows alias không chạy được | Không khởi chạy được kiểm thử ban đầu | Dùng đường dẫn executable cụ thể để kiểm tra môi trường |
| Python 3.15 thiếu dependency; pydantic-core ghim chưa có wheel tương thích trong lần cài | Bộ test lỗi import, cài đặt chuyển sang build từ source | Dừng hướng cài này và tạo môi trường Python 3.12 trong workspace |
| Mạng bị chặn trong sandbox ở lần cài đầu | pip không truy cập được package index | Cài dependency đã ghim qua quyền thực thi được hệ thống chấp thuận; cài thành công trong môi trường 3.12 |
| Input thật chưa xác nhận context/hiệu lực | Không đủ điều kiện kết luận ngữ nghĩa hoặc severity | Giữ null/review, bàn giao lý do cho Đức Anh/Dũng; chưa giải quyết bằng cách đổi cờ |
| Quy tắc Semantic chỉ bao phủ một số dạng hẹp | Ca lộ trình nhiều mốc năm không tự có kết luận đầy đủ | Công bố giới hạn, giữ bằng chứng để mở rộng và review tiếp |
| Văn bản lặp làm diff có vùng thêm/xóa dài | Output khó đọc như một thay đổi nghiệp vụ đơn lẻ | Kiểm chứng reconstruction và ghi rõ giới hạn; chưa đổi thuật toán để tránh thay phạm vi nền |
| Query hiện chưa nhận vùng diff trong luồng Context | Chưa hoàn tất điểm nối Ngọc Anh → Đức Anh | Cung cấp JSON diff thật; phần ghép query chờ Đức Anh/Dũng triển khai và chạy lại |
| Chưa có dịch vụ LightRAG/model thật | Hai test dịch vụ thật bị bỏ qua; chưa có retrieval thực tế | Ghi rõ skipped và demo không dùng model/RAG |
| Validator chung còn hai giới hạn đã biết | Chưa ép change_id duy nhất toàn report và reconstruction toàn diff | Giữ expected failures; chốt reconstruction ở điểm vào Semantic, chưa sửa phạm vi schema của nhóm |
| Chưa có người nhận xác nhận trực tiếp | Chưa đủ tiêu chí nghiệm thu bàn giao | Chuẩn bị output/lệnh/hash và để xác nhận pending |

Các lỗi môi trường ban đầu đã được xử lý đủ để chạy kiểm thử. Những điểm còn mở về nghiệp vụ, ngữ cảnh và phối hợp chưa được coi là đã giải quyết.

## 8 Kiểm thử và kết quả

### 8.1 Phạm vi bộ kiểm thử mới

12 test bao phủ: item thật và nguồn; offset/reconstruction ở ca biên; None khác chuỗi rỗng; 200 cặp chuỗi ngẫu nhiên có seed; từ chối diff thiếu/sai; Semantic với context thật chưa đủ; quy tắc deadline trên dữ liệu synthetic; cờ context không xóa review thượng nguồn; thiếu context độc lập; thiếu dẫn chiếu/hiệu lực/đích/nguồn hoặc thao tác chưa hỗ trợ; diff sai không sinh kết luận chắc chắn; chuỗi giống nhau và diễn đạt tương đương.

200 cặp ngẫu nhiên là các trường hợp bên trong một test, không được cộng thêm thành 200 test độc lập. Ca synthetic có context đầy đủ là giả định kiểm thử kỹ thuật, không phải ca thật được chuyên gia xác nhận.

### 8.2 Tổng kết kiểm thử đã thực hiện

| Bộ kiểm thử | Tổng ca | Đạt | Ghi chú |
| --- | --- | --- | --- |
| Schema | 51 | 49 | 2 expected failures đã biết |
| Context | 26 | 24 | 2 skipped do chưa có dịch vụ thật |
| Demo DOCX/API | 30 | 30 | Không phát hiện hồi quy |
| Handoff | 20 | 20 | 8 ca cũ và 12 ca mới |
| Module src cũ | 16 | 16 | Không phát hiện hồi quy |
| Tổng | 143 | 139 | 2 expected failures và 2 skipped |

`pip check` không phát hiện dependency hỏng. `git diff --check` không phát hiện lỗi khoảng trắng. Mã băm code/input trong manifest đã được kiểm tra khớp với file tại thời điểm bàn giao. Có cảnh báo deprecation của Starlette về TestClient/httpx, nhưng các ca API vẫn chạy thành công trong môi trường đã cài.

### 8.3 Kết quả upload dữ liệu thật

| Bộ DOCX | HTTP | Report status | Số item | Số item có Text Diff |
| --- | --- | --- | --- | --- |
| case_01 | 200 | PARTIAL | 2 | 1 |
| case_02 | 200 | PARTIAL | 1 | 1 |
| case_03 | 200 | PARTIAL | 13 | 13 |

Mọi diff đã tính trong ba report đều được kiểm tra dựng lại. `PARTIAL` nghĩa có kết quả dùng được nhưng vẫn còn phần chưa xác nhận. HTTP 200 không có nghĩa toàn bộ phân tích đã hoàn thiện. Lần chạy này dùng FastAPI TestClient với file DOCX thật, chưa phải kiểm chứng mới qua thao tác trình duyệt hoặc dịch vụ mạng triển khai độc lập.

## 9 Cách chạy lại để nhận bàn giao

Chạy từ thư mục gốc dự án, dùng Python 3.12 đã cài `requirements-demo.txt`. Trên máy kiểm chứng hiện tại:

```powershell
$py = '.codex-tmp/ngocanh-py312/Scripts/python.exe'
& $py -m unittest test.handoff_suite.test_ngocanh_week10 -v
& $py -m test.handoff_suite.run_ngocanh_week10
& $py -m pip check
```

Người nhận dùng môi trường Python riêng có thể thay `$py` bằng đường dẫn tương ứng. Runner sinh lại các file trong output; timestamp và comparison_id sẽ khác giữa các lần chạy. Hash input/code trong manifest dùng để đối chiếu đúng dữ liệu và phiên bản.

Chạy đầy đủ các bộ hồi quy:

```powershell
& $py -m unittest discover -s test/schema_suite -v
& $py -m unittest discover -s test/context_suite -v
& $py -m unittest discover -s test/demo_suite -v
& $py -m unittest discover -s test/handoff_suite -v
& $py -m unittest test_pipeline_modules -v
```

## 10 Công việc còn lại và điều kiện hoàn thành

| Việc còn lại | Người phụ trách hoặc phối hợp | Bằng chứng cần có |
| --- | --- | --- |
| Review item thật và Text Diff | Thọ + Ngọc Anh | Kiểm tra đúng đích, đơn vị, nguồn và reconstruction trên phiên bản bàn giao |
| Dùng vùng đổi tạo query | Đức Anh, phối hợp Dũng | Chạy bằng JSON TextDiffResult thật, đúng ID, có index ready và query thực sự dùng vùng đổi |
| Xác nhận Context → Semantic | Đức Anh + Ngọc Anh | Định nghĩa, điều kiện, ngoại lệ, dẫn chiếu và hiệu lực liên quan được kiểm tra |
| Người nhận chạy Scorer | Dũng + Ngọc Anh kiểm thử chéo | Dũng chạy output Semantic thật, kiểm tra change_id/null/reason và xác nhận |
| Mở rộng phương pháp Semantic | Ngọc Anh; Dũng/Đức Anh cho AI Adapter | Ca dev được review, hỗ trợ nhiều khía cạnh và phương pháp/model được chốt |
| Hoàn thiện rubric tác động | Dũng cùng nhóm | Tiêu chí được review, có căn cứ cho các mức, không suy từ số chữ đổi |
| Đánh giá chất lượng | Theo phân công đánh giá của nhóm | Tập nhãn độc lập và ứng viên đã khóa trước khi đo |
| Commit và bàn giao thay đổi | Ngọc Anh cùng reviewer | Commit/PR chứa code, test, tài liệu, input/output và kết quả review |

Trạng thái xác nhận hiện tại là Thọ chờ review, Đức Anh chờ chạy điểm nhận query, Dũng đã có bằng chứng Scorer chạy cục bộ nhưng chưa xác nhận thay đổi này. Không tự điền tên người xác nhận hoặc coi lần chạy bằng công cụ là review của các thành viên.

## 11 Nội dung có thể dùng khi báo cáo tiến độ cá nhân

> Tôi đã kiểm tra và bổ sung Text Diff, Semantic Diff trên nền backend hiện có. Text Diff nhận item thật của khoản 5 Điều 16 từ bộ dữ liệu bàn giao, giữ đúng ID và nguồn, có offset khớp hai chuỗi và dựng lại chính xác nội dung sau. Tôi đã thêm kiểm tra tại điểm nối để Semantic giữ null/review khi diff sai hoặc ngữ cảnh, đích, dẫn chiếu, hiệu lực chưa đủ căn cứ. Tôi đã chuẩn bị output thật cho Đức Anh và Dũng, chạy Scorer hiện có, bổ sung 12 test và hướng dẫn chạy lại. Phần còn lại là người nhận xác nhận bàn giao, tích hợp diff vào query và hoàn thiện căn cứ/phương pháp để kết luận ngữ nghĩa ca thật. Tôi chưa xác nhận hoàn tất toàn bộ Semantic, rubric tác động hoặc đánh giá chất lượng pháp lý.
