# KẾ HOẠCH TRIỂN KHAI DỰ ÁN

**Dự án:** Legal Document Change Detection
**Phiên bản kế hoạch:** 1.5.0
**Cập nhật:** 06/11/2026, hiện tại cuối tuần 9
**Người điều phối:** Dương Đức Anh
**Mốc bàn giao:** Hoàn tất cuối tuần 13; nộp đầu tuần 14 (chưa có ngày cụ thể).

**Nguồn đồng bộ:**
- [Lộ trình tuần trên Google Docs](https://docs.google.com/document/d/1-pSaoPC-GJR6JSGDpmCwj1UOE9N0dSPO4hZCD3iPn9s/edit): mục tiêu và đầu ra dự kiến từng tuần.
- [Phân công và tiến độ trên Google Sheets](https://docs.google.com/spreadsheets/d/1Fe9d8UHGrK9YG6j7BLtd0EwQQ7LA-CpPjvPzn6d3k48/edit): task theo thành viên, bằng chứng, trạng thái và việc chuyển tiếp.
- [BRD](brd.md), [SRS 1.3.0](srs.md), [Architecture](architecture.md): phạm vi và hợp đồng kỹ thuật.
- [API contract phát triển](api-contract.md), [Development guide](development-guide.md), [Data annotation guide](data-annotation-guide.md).

Bản 1.5.0 thay lịch tuần của bản 1.4.0, giữ mã PL và phân công chính.
Tuần 4–8 là kế hoạch lịch sử đã hiệu chỉnh phạm vi, không xác nhận công việc
đã hoàn thành hoặc đã được giao đúng tuần. Việc có trên nhánh riêng, chạy
được fixture, được bên nhận review và chạy xuyên hệ thống là các mức khác
nhau. Không dùng ngày cập nhật để ghi hoàn thành hồi tố.

## 1. Phạm vi và trách nhiệm

Hệ thống nhận V1, văn bản sửa đổi S và tài liệu tham chiếu người dùng cung cấp.
DOCX là định dạng chính, hỗ trợ PDF có lớp chữ. Phân tích từng yêu cầu sửa đổi,
liên kết đúng văn bản/Điều/Khoản/Điểm/cụm từ đích, giữ trước/sau cục bộ, nguồn,
ngữ cảnh, hiệu lực, cảnh báo và nhu cầu bổ sung căn cứ. Không so sánh toàn bộ V1
với S một–một và không xem phần V1 không được nhắc là bị xóa. V2 nếu có chỉ dùng
đối chiếu theo mục đích đã ghi; không phải đầu vào/đầu ra bắt buộc.

Không thêm OCR, kho pháp luật dùng chung hoặc tư vấn pháp lý tự động vào phạm vi.
Request đồng bộ; bản đầu không có job nền/lịch sử lâu dài. Người dùng bổ sung
tham chiếu thì chủ động gửi lại bộ file, tạo lần xử lý mới.

| Thành viên | Trách nhiệm chính | Đầu ra và bên nhận |
| --- | --- | --- |
| Bạch Công Dũng | Dữ liệu, nghiệp vụ, tài liệu; công cụ/parser cấu trúc đã có; đề xuất chủ trì ngữ cảnh | Mẫu/nguồn/manifest/guideline cho Thọ, Ngọc Anh, Tuấn Anh; cùng Thọ chốt adapter cấu trúc |
| Dương Đức Anh | Điều phối, backend, schema, API, pipeline, tích hợp, môi trường và đóng gói | Contract/fixture và báo cáo nhất quán; bên cung cấp/nhận chạy lại được |
| Bùi Quang Thọ | Reader/Parser theo contract, trích chỉ dẫn, liên kết đích và hiệu lực | ExtractedDocument/Clause/AmendmentItem có nguồn cho pipeline và Ngọc Anh |
| Đoàn Ngọc Anh | Text Diff, Semantic Diff/aspects, Classifier & Scorer | Kết quả có bằng chứng/ngữ cảnh/cảnh báo cho pipeline, UI và Evaluator |
| Đỗ Tuấn Anh | UI, Evaluator, điều phối kiểm thử và review nhãn | Hiển thị đúng report, ca tính tay/metrics và kiểm thử đầu-cuối |

Phần ngữ cảnh chưa có quyết định xác nhận người hiện thực. Đức Anh điều phối
Dũng–Thọ–Ngọc Anh chốt đầu tuần 10, không tự coi đã bàn giao hoặc giao thêm
trách nhiệm mà chưa xác nhận. Cả nhóm tham gia gán nhãn; reviewer khác người tạo.

## 2. Lịch chung tuần 4–13

10 tuần là tuần 4 đến tuần 13 của môn học, không phải một lịch đánh số lại 1–10.
Theo nhóm trưởng: hiện cuối tuần 9, nộp đầu tuần 14; chưa có ngày nộp cụ thể.
Các mốc tương lai là mục tiêu điều phối, chưa phải xác nhận cam kết của từng người.

| Tuần | Công việc cần thực hiện | Đầu ra / điều kiện kết thúc |
| --- | --- | --- |
| 4 | Xác định bài toán, phân công và dựng baseline minh họa; dự thảo BRD, SRS, kiến trúc và hợp đồng dữ liệu. | Tài liệu dự thảo và demo baseline. Đây là mục tiêu lịch sử, không xác nhận đã hoàn thành đúng tuần. |
| 5 | Review tài liệu, thống nhất phạm vi V1–S và request đồng bộ; chuẩn bị dữ liệu, guideline và hợp đồng API ban đầu. | Tài liệu có phiên bản, ví dụ đầu vào/đầu ra và danh sách quyết định còn mở. Phần chưa có bằng chứng bàn giao được chuyển tiếp. |
| 6 | Xây schema và fixture Reader/Parser; phát triển Reader, Parser và Text Diff; chuẩn bị pilot nhãn, Evaluator và UI mẫu. | Các module có ví dụ/test riêng theo hợp đồng. Không đồng nhất code trên nhánh với báo cáo thật qua API/UI; phần còn thiếu chuyển sang tuần 9–11. |
| 7 | Trích chỉ dẫn sửa đổi trong S và liên kết đúng văn bản, Điều/Khoản/Điểm của V1; chuẩn bị before_text/after_text và thử hợp đồng với Text/Semantic Diff. | Fixture chỉ dẫn–đích–trước/sau có nguồn, danh sách dạng hỗ trợ/chưa hỗ trợ. Không ghép V1 với S một–một; không coi phần V1 không được nhắc là bị xóa. Đây là kế hoạch, chưa xác nhận bàn giao. |
| 8 | Phát triển Semantic Diff/Scorer theo SRS; review nguồn, ngữ cảnh, nhãn và phép đo; chuẩn bị tích hợp, logging và hiển thị. | Module/test và report mẫu có nguồn, cảnh báo; bảng việc tồn. Chưa có bằng chứng hệ thống V1–S chạy xuyên API/UI; không ghi nhận mốc này đã đạt. |
| 9 | Chốt lại hiện trạng cuối tuần 9: đối chiếu các nhánh, schema, hai Parser, nguồn và API/report mẫu; xác nhận người sở hữu context và ca V1–S dùng chung. Đánh giá phạm vi nghiên cứu LightRAG nếu nhóm tiếp tục đề xuất. | Bảng trạng thái có commit/test và việc tồn theo người; fixture được bên giao/nhận review; danh sách quyết định mở. Backend 9179682 có 35 test nhưng adapter nghiệp vụ chưa cấu hình. Chuyển việc chưa chốt sang đầu tuần 10; không yêu cầu hồi tố hoàn thành. |
| 10 | Tạo nền tích hợp develop sau kiểm kê; đưa Reader/Parser, trích chỉ dẫn/liên kết và Text Diff vào một ca V1–S thật; nối API upload với UI cơ bản. Giữ nguồn và cảnh báo ở mọi bước. | Một ca thật chạy qua API/UI tới Text Diff; semantic/scoring chưa có phải để null kèm issue. Có test ca đích mơ hồ/ngoài văn bản; phía nhận chạy lại được. develop chỉ trở thành nền chung sau kiểm thử; chưa mặc định nhánh đã tồn tại. |
| 11 | Tích hợp và kiểm chứng Semantic Diff/Scorer với ngữ cảnh đủ/thiếu; sửa Evaluator để đếm prediction thừa/nhãn bị bỏ sót; review nhãn, chạy các ca đại diện trên dev và sửa lỗi. | Bản ứng viên cuối tuần 11, report dev và giới hạn; thuật toán, cấu hình, nhãn và matching cho test độc lập được cố định trước đánh giá tuần 12. LightRAG chỉ thử nếu đã chốt dữ liệu/tài nguyên; không chặn luồng chính. |
| 12 | Đánh giá các phiên bản thực sự có trên cùng bộ test độc lập; đo tài nguyên/giới hạn, thử trên máy khác; đóng gói và diễn tập demo gồm ca lỗi/thiếu căn cứ. | Kết quả Precision/Recall/F1/Critical Recall kèm số mẫu, TP/FP/FN và commit/tag; công bố đạt/chưa đạt. Nếu test đã dùng để chỉnh thuật toán phải công bố, không gọi là đánh giá độc lập. Có gói ứng viên và hướng dẫn chạy. |
| 13 | Cố định bản nộp, sửa lỗi chặn demo, hoàn thiện báo cáo/slide, kiểm tra dữ liệu được phép bàn giao và diễn tập; không mở rộng chức năng. | Cuối tuần 13 có gói mã nguồn/dependency/cấu hình/mẫu/minh chứng và demo chạy lại được; số liệu khớp commit/tag. Sẵn sàng nộp đầu tuần 14; ngày nộp cụ thể chưa được cung cấp. |

Nếu không đạt mốc, ghi đúng phần bị chặn, chủ xử lý và đầu ra kế tiếp; không
đổi nội dung báo cáo để làm như đã đạt. Mục tiêu F1 ≥ 0,90 và Critical Recall
≥ 0,95 vẫn giữ; nếu chưa đạt phải công bố kết quả thật và nguyên nhân.

## 3. Hiện trạng kiểm chứng cuối tuần 9

Đối chiếu code đã push ngày 06/11/2026; không kết luận code trên máy riêng chưa
push là chưa làm. Các bằng chứng dưới đây không xác nhận hoàn thành đúng tuần cũ.

| Phần | Bằng chứng | Trạng thái / còn thiếu |
| --- | --- | --- |
| Dương Đức Anh | [Nhánh/commit](https://github.com/Lyra1603/group4_legal_document_change_detection/commit/9179682cbe6786053dc93132f1c084c394406303) | Schema báo cáo/runtime validation, upload, pipeline adapter, deadline/slot/file tạm và docs có ở 9179682; 35 test đã chạy đạt. Upload DOCX thật dừng tại extraction MODULE_NOT_CONFIGURED. Chưa có xác nhận contract liên nhóm. |
| Bạch Công Dũng | [Nhánh/commit](https://github.com/Lyra1603/group4_legal_document_change_detection/tree/bachdung/docs) | Có công cụ PDF→DOCX, parser cấu trúc và mẫu ở main/bachdung/docs. Chưa xác nhận manifest/nhãn thật được review, adapter nguồn hoặc người hiện thực context. |
| Bùi Quang Thọ | [Nhánh/commit](https://github.com/Lyra1603/group4_legal_document_change_detection/tree/feature/week6-reader-parser) | Reader/Parser cơ bản đã tích hợp ở nhánh backend. Linker nhánh feature/week6-reader-parser mới tìm số Điều; chưa tạo AmendmentItem đầy đủ hoặc phân biệt chắc văn bản đích. |
| Đoàn Ngọc Anh | [Nhánh/commit](https://github.com/Lyra1603/group4_legal_document_change_detection/tree/ngocanh) | Nhánh ngocanh 7f66581 có Text Diff và demo; Semantic Diff/Scorer còn logic mẫu, nguồn cứng, mức MAJOR/MINOR khác SRS. Chưa tích hợp adapter. |
| Đỗ Tuấn Anh | [Nhánh/commit](https://github.com/Lyra1603/group4_legal_document_change_detection/tree/TuanAnh) | Nhánh TuanAnh 679bbca có 5 ca tổng hợp và test Evaluator baseline. Chưa thấy frontend/Evaluation Plan; review nhãn chưa được xác nhận. Evaluator còn cần sửa phép đếm và matching. |

Nhánh `ducanh/docs` đã xóa vì toàn bộ lịch sử đã có trong nhánh backend.
`develop` chưa được tạo tại thời điểm đối chiếu; các nhánh module vẫn tách rời.
`main` chưa phản ánh backend 9179682; việc tạo cấu trúc thư mục không chứng minh
code đã tích hợp. Không đưa thêm số đo chất lượng khi chưa có đánh giá độc lập.

## 4. Điểm phải thống nhất trước tích hợp

| Điểm bàn giao | Bên phối hợp | Quyết định và bằng chứng | Mốc xử lý |
| --- | --- | --- | --- |
| Hai Parser và nguồn | Dũng + Thọ + Đức Anh | Chọn parser/adapter; chuyển block:N sang nguồn Reader nếu dùng; giữ Khoản/Điểm/trích dẫn và phần ngoài Điều; test cùng file | Đầu tuần 10 |
| Chỉ dẫn–đích–trước/sau | Thọ + Dũng + Ngọc Anh | Phân biệt S/V1/văn bản khác; operation/applicability/after_basis, null khác không tồn tại; ca được review | Đầu tuần 10, mở rộng tuần 11 |
| Schema và API/report | Đức Anh + Thọ + Ngọc Anh + Tuấn Anh | Fixture SRS dùng được hai chiều, signature adapter, enum scoring/null, nguồn, warnings/PARTIAL và lỗi HTTP | Đầu tuần 10 |
| Context, tham chiếu, hiệu lực | Dũng + Thọ + Ngọc Anh; Đức Anh điều phối | Xác nhận người hiện thực, AVAILABLE/MISSING/UNRESOLVED, căn cứ trước/sau, phạm vi hiệu lực và giới hạn khi thiếu | Chốt đầu tuần 10; nối tuần 10–11 |
| UI và báo cáo | Đức Anh + Tuấn Anh + Ngọc Anh | Mock được gắn nhãn, hiển thị nguồn/aspects/null/lỗi, bổ sung rồi gửi lại toàn bộ file; không tự retry POST | Tuần 10–11 |
| Nhãn và Evaluator | Tuấn Anh + Dũng + Ngọc Anh | Severity/matching, prediction thừa, nhãn bị bỏ sót, cảnh báo chưa xác định, review độc lập và tách dev/test | Tuần 10–11, khóa trước tuần 12 |
| Vận hành và tài nguyên | Đức Anh + chủ module | Đo input/timeout/concurrency; phân biệt deadline hợp tác và ngắt cứng; cấu hình máy demo | Tuần 11–12 |

API upload phát triển và các mức giới hạn đã có trong code nhưng chưa phải quyết
định liên nhóm cuối cùng. Không tự đổi SRS hoặc gán giá trị giả để vừa schema.
Phía cung cấp và phía nhận cùng thử fixture trước khi đánh dấu bàn giao.

LightRAG chỉ là đề xuất nghiên cứu trong lộ trình mới, chưa phải dependency
hoặc thành phần kiến trúc bắt buộc. Chỉ thử khi xác định rõ vấn đề truy xuất,
dữ liệu được dùng, mô hình, tài nguyên/chi phí, người thực hiện và cách so sánh.
Nếu chưa chốt hoặc không có ích lợi đo được thì tiếp tục luồng chính không dùng nó.

## 5. Danh mục task và phụ thuộc

Mã PL giữ nguyên giữa repo và Sheet. Mốc dưới đây là lịch chuyển tiếp 1.5.0,
không sửa lịch sử thành đã hoàn thành. Chủ module có thể làm bằng fixture
trước; dữ liệu thật và xác nhận bên nhận là điều kiện đóng task tích hợp.

| Mã | Công việc | Chủ trì | Phụ thuộc / review | Mốc mới |
| --- | --- | --- | --- | --- |
| PL-01 | Tài liệu và điểm bàn giao | Đức Anh + Dũng | Chủ module review | Đầu tuần 10 |
| PL-02 | Schema và fixture | Đức Anh | Thọ/Ngọc Anh/Dũng cung cấp mẫu; Tuấn Anh thử report | Đầu tuần 10 |
| PL-03 | Reader/Parser và adapter nguồn | Thọ | Dũng bàn giao công cụ/mẫu; Đức Anh kiểm tra contract | Tuần 10 |
| PL-04 | Trích chỉ dẫn, liên kết và hiệu lực | Thọ | PL-03; Dũng review đích; Ngọc Anh thử trước/sau | Tuần 10; sửa lỗi tuần 11 |
| PL-05 | Text Diff | Ngọc Anh | PL-02/04 khi nối thật | Tuần 10 |
| PL-06 | Semantic Diff và Scorer | Ngọc Anh | PL-04/05/17 và tiêu chí nhãn được review | Tuần 11 |
| PL-07 | API/Pipeline và vận hành | Đức Anh | PL-02/03/04/05/06/17; backend nền đã có 9179682 | Tích hợp tối thiểu tuần 10; hoàn thiện tuần 11 |
| PL-08 | UI và bổ sung tài liệu | Tuấn Anh | API contract với Đức Anh, PL-07 khi nối thật | Tuần 10–11 |
| PL-09 | Dữ liệu, manifest và nhãn | Dũng quản lý; Tuấn Anh điều phối review | Cả nhóm gán nhãn; reviewer khác người tạo | Ca chung đầu tuần 10; khóa test cuối tuần 11 |
| PL-10 | Evaluator | Tuấn Anh | Nhãn/matching và ca tính tay với Dũng/Ngọc Anh | Tuần 10–11 |
| PL-11 | Cải thiện phương pháp/hiệu năng | Chủ module; Đức Anh điều phối | Luồng tích hợp, dev set và Evaluator | Tuần 11 |
| PL-12 | Kiểm thử toàn hệ thống | Tuấn Anh điều phối | PL-07/08; chủ module sửa lỗi mình | Tuần 10–11; tái lập tuần 12 |
| PL-13 | Phiên bản ứng viên | Đức Anh | PL-11/12; các bên review | Cuối tuần 11 |
| PL-14 | Đánh giá độc lập | Tuấn Anh | PL-13, test và matching đã khóa | Tuần 12 |
| PL-15 | Đóng gói, báo cáo, diễn tập | Đức Anh điều phối | PL-14; cả nhóm bàn giao phần phụ trách | Tuần 12–13 |
| PL-16 | Nộp và bàn giao | Đức Anh điều phối | PL-15 | Hoàn tất cuối tuần 13; nộp đầu tuần 14 |
| PL-17 | Ngữ cảnh và kiểm tra dẫn chiếu | Dũng — đề xuất, cần xác nhận người hiện thực | PL-03/04; Thọ cung cấp nguồn, Ngọc Anh thử đủ/thiếu căn cứ | Chốt chủ đầu tuần 10; tích hợp tuần 10–11 |

## 6. Phân công chuyển tiếp tuần 9–13

Sheet là nơi cập nhật trạng thái sống, commit, reviewer và việc tồn. Bảng dưới
đây giữ phạm vi công việc/đầu ra của bản 1.5.0; không dùng checkbox để tính
tiến độ nếu chưa kiểm tra đủ cả hàng. Các phần chưa chốt cuối tuần 9 chuyển
đầu tuần 10 thay vì đặt hạn hoàn thành hồi tố.

### Tuần 9

| Thành viên / mã | Công việc | Đầu ra kiểm chứng | Phối hợp / điều kiện |
| --- | --- | --- | --- |
| Dương Đức Anh — PL-01/02/07 | Chốt bảng contract/schema/API hiện có với bên nhận; kiểm kê commit, ghi kế hoạch develop và các adapter chưa bàn giao. | Fixture/report mẫu + điểm lệch và chủ xử lý; backend 9179682 là bằng chứng kỹ thuật, chưa coi cả hệ thống hoàn thành. | Thọ, Ngọc Anh, Tuấn Anh review contract; chưa tạo develop trong công việc đồng bộ tài liệu này. |
| Bạch Công Dũng — PL-01/09/17 | Chọn một cặp V1–S thật; xác nhận nguồn, vai trò V2, đáp án trực tiếp và dẫn chiếu; thống nhất ranh giới hai Parser và người hiện thực context. | Một ca có nguồn/vị trí, trước–sau được review và danh sách căn cứ đủ/thiếu; quyết định context còn mở có người chốt. | Thọ review cấu trúc; Ngọc Anh review ngữ cảnh; Tuấn Anh review nhãn. |
| Bùi Quang Thọ — PL-03/04 | Đối chiếu Reader/Parser cơ bản với parser cấu trúc; đề xuất adapter nguồn và đầu ra AmendmentItem trên ca chung. | JSON Điều và chỉ dẫn–đích–trước/sau, source_refs thật; ghi rõ dạng chỉ hỗ trợ thử nghiệm. | Cần Dũng cung cấp ca nguồn và Đức Anh kiểm tra contract. |
| Đoàn Ngọc Anh — PL-05/06 | Đối chiếu model riêng với schema chung; chỉ rõ phần giả lập và sửa đổi cần thiết về source, null và mức độ. | Text Diff fixture có assertion; danh sách đổi schema và ca giống nhau/thiếu nguồn/đổi nghĩa để triển khai tuần 10–11. | Cần đầu vào từ Thọ và review schema với Đức Anh; không dùng nguồn cứng. |
| Đỗ Tuấn Anh — PL-08/09/10 | Chốt report UI cần dùng, rà dữ liệu pilot/review nhãn và lỗi phép đếm Evaluator. | Mock UI/report có nhãn giả lập; ca tính tay prediction thừa/bỏ sót và danh sách nhãn chờ review. | Cùng Đức Anh chốt API; Dũng/Ngọc Anh review nhãn và matching. |

### Tuần 10

| Thành viên / mã | Công việc | Đầu ra kiểm chứng | Phối hợp / điều kiện |
| --- | --- | --- | --- |
| Dương Đức Anh — PL-07 | Tạo develop từ nền đã kiểm tra, đối chiếu main rồi tích hợp từng adapter; nối upload → ingestion → extraction/linking → Text Diff. | Commit tích hợp + test API trên ca thật và ca lỗi; report giữ metadata/nguồn/null; không có phân tích giả trong server. | PL-02/03/04/05 và quyết định nguồn/context; chưa đủ thì báo thiếu adapter và điểm chặn. |
| Bạch Công Dũng — PL-09/17 | Bàn giao bộ ca có nguồn và đáp án trực tiếp; phối hợp hiện thực ngữ cảnh theo phân công đã xác nhận. | Manifest, bằng chứng và fixture đủ/thiếu dẫn chiếu; ghi rõ người review; hỗ trợ ca S sửa nhiều văn bản. | Không tự coi context đã có chủ nếu chưa được xác nhận đầu tuần 10. |
| Bùi Quang Thọ — PL-03/04 | Bàn giao parser/adapter nguồn và extractor/linker cho dạng đã chọn; giữ OTHER_DOCUMENT/UNRESOLVED. | Một cặp thật tạo AmendmentItem hợp lệ; test đúng đích, đích mơ hồ và chỉ dẫn ngoài V1; hiệu lực chưa rõ có cảnh báo. | Dũng review nguồn/đích; Đức Anh chạy lại đầu ra. |
| Đoàn Ngọc Anh — PL-05/06 | Tích hợp Text Diff trên nội dung cục bộ; chuẩn bị Semantic Diff/Scorer theo schema, loại bỏ nguồn ghi cứng. | Test thêm/xóa/thay thế/không đổi/thiếu nội dung và offset; adapter Text Diff chạy trong pipeline thật. | Chưa đủ before/after phải null; semantic/scoring còn thiếu giữ issue. |
| Đỗ Tuấn Anh — PL-08/10 | Nối UI tối thiểu vào API upload; hiển thị nguồn, trạng thái và null; bắt đầu sửa Evaluator theo ca tính tay. | Một ca thật xem được report; phân biệt lỗi trước pipeline/PARTIAL/FAILED; không auto retry POST; test Evaluator mới. | Cần API contract được Đức Anh–Tuấn Anh review và đầu ra thật PL-07. |

### Tuần 11

| Thành viên / mã | Công việc | Đầu ra kiểm chứng | Phối hợp / điều kiện |
| --- | --- | --- | --- |
| Dương Đức Anh — PL-07/11/12/13 | Nối context/semantic/scorer đã bàn giao; kiểm tra contract, lỗi từng bước, tài nguyên và regression; chốt ứng viên. | Commit ứng viên cuối tuần 11, cấu hình và test tích hợp có ca đủ/thiếu căn cứ; báo rõ giới hạn chưa đạt. | Chủ module bàn giao; Tuấn Anh review toàn luồng trước khóa phiên bản. |
| Bạch Công Dũng — PL-09/17 | Review dữ liệu/nhãn, căn cứ dẫn chiếu và hiệu lực; phối hợp khóa test độc lập và hoàn thiện context. | Manifest/nhãn có phiên bản và reviewer; test không dùng chỉnh thuật toán; ca thiếu căn cứ được giữ nhãn phù hợp. | Tuấn Anh điều phối review; Ngọc Anh thống nhất ranh giới khía cạnh/severity. |
| Bùi Quang Thọ — PL-04/11 | Sửa lỗi parser, chỉ dẫn/liên kết trên dev; bổ sung regression cho S nhiều văn bản và bố cục khó. | Test lỗi đã sửa và danh sách dạng chưa hỗ trợ; source/target/EffectInfo không mất khi tích hợp. | Dũng kiểm chứng nguồn; Đức Anh kiểm tra adapter. |
| Đoàn Ngọc Anh — PL-06/11 | Hoàn thiện semantic/aspects và scorer dựa trên bằng chứng/ngữ cảnh; sửa ca không đổi nghĩa, null và cảnh báo. | Kết quả dev với test có đáp án; nhãn SRS LOW/MEDIUM/HIGH/CRITICAL/null và lý do; chưa đạt phải công bố. | Tiêu chí severity do Dũng/Ngọc Anh/Tuấn Anh review, không chấm theo độ dài mô tả. |
| Đỗ Tuấn Anh — PL-08/10/12 | Hoàn thiện UI và Evaluator, matching/TP/FP/FN; chạy kiểm thử hệ thống, khóa nhãn/quy tắc test trước tuần 12. | Ca tính tay bao phủ prediction thừa, nhãn thiếu và review; report lỗi có commit/input/expected/actual; bộ test khóa. | Dũng/Ngọc Anh review nhãn; Đức Anh phối hợp chốt ứng viên. |

### Tuần 12

| Thành viên / mã | Công việc | Đầu ra kiểm chứng | Phối hợp / điều kiện |
| --- | --- | --- | --- |
| Dương Đức Anh — PL-13/14/15 | Đóng gói đúng ứng viên đánh giá, đo thời gian/tài nguyên, kiểm tra máy khác và cấu hình; giữ commit/tag. | Gói chạy lại được, log thời gian từng bước, cấu hình giới hạn và phiên bản khớp kết quả. | Chỉ sửa lỗi cần thiết; đổi code ảnh hưởng số đo phải đánh giá lại và ghi phiên bản. |
| Bạch Công Dũng — PL-09/14/15 | Kiểm tra nguồn/quyền bàn giao dữ liệu, minh chứng nhãn và giới hạn nghiệp vụ. | Danh mục dữ liệu được phép phân phối, minh chứng nguồn/review và phần thiếu căn cứ. | Phối hợp Tuấn Anh đánh giá, không chỉnh nhãn test để làm đẹp kết quả. |
| Bùi Quang Thọ — PL-14/15 | Giải thích phương pháp đọc/liên kết, giới hạn và hỗ trợ tái lập demo. | Mô tả phương pháp + ca demo cấu trúc/đích và giới hạn có minh chứng. | Chỉ sửa lỗi chặn theo bản ứng viên, cập nhật regression và kết quả liên quan. |
| Đoàn Ngọc Anh — PL-14/15 | Phân tích lỗi ngữ nghĩa/scoring trên kết quả đánh giá; bàn giao phương pháp và giới hạn. | Kết quả so sánh phiên bản thực sự có; không dùng test để tune rồi gọi là độc lập. | Nếu LightRAG được thử, báo hiệu ích/chi phí riêng; không tuyên bố đã dùng nếu chưa có. |
| Đỗ Tuấn Anh — PL-14/15 | Chạy đánh giá độc lập và tổng hợp kiểm thử/khả năng hiểu UI; tổ chức demo đủ/thiếu căn cứ. | Precision/Recall/F1/Critical Recall, TP/FP/FN, số mẫu/review, commit và dữ liệu; ghi đạt/chưa đạt. | Chỉ dùng tập test đã khóa và phiên bản ứng viên; công bố mọi sai lệch quy trình. |

### Tuần 13

| Thành viên / mã | Công việc | Đầu ra kiểm chứng | Phối hợp / điều kiện |
| --- | --- | --- | --- |
| Dương Đức Anh — PL-15/16 | Chốt bản nộp, README/config/dependency và danh mục bàn giao; điều phối diễn tập, kiểm tra máy khác. | Commit/tag bản nộp và gói chạy cuối tuần 13; sẵn sàng nộp đầu tuần 14. | Không mở rộng chức năng; đổi code ảnh hưởng số đo phải ghi nhận và chạy lại. |
| Bạch Công Dũng — PL-15/16 | Hoàn thiện nội dung dữ liệu/nghiệp vụ báo cáo, kiểm tra nguồn và minh chứng. | Phần báo cáo và dữ liệu mẫu hợp lệ, khớp phiên bản bàn giao. | Cùng Đức Anh đối chiếu danh mục đầu ra. |
| Bùi Quang Thọ — PL-15/16 | Hoàn thiện mô tả Reader/Parser/linker và phần trình bày/demo phụ trách. | Phương pháp, giới hạn và kịch bản demo có thể chạy lại. | Giữ nguyên schema đã chốt; chỉ sửa lỗi chặn demo có test. |
| Đoàn Ngọc Anh — PL-15/16 | Hoàn thiện phần phương pháp/ngữ nghĩa/scoring, kết quả và giới hạn trong báo cáo/slide. | Số đo và ví dụ khớp phiên bản được trích dẫn; không phóng đại mức hoàn thiện. | Tuấn Anh đối chiếu số liệu đánh giá; Đức Anh kiểm tra bản nộp. |
| Đỗ Tuấn Anh — PL-15/16 | Hoàn thiện UI/demo, báo cáo kiểm thử/đánh giá và phối hợp slide, diễn tập. | Demo trên máy bàn giao, báo cáo/slide khớp code và dữ liệu; ca lỗi dự phòng. | Đầu tuần 14 nộp theo thông báo môn học; chưa có ngày cụ thể. |

## 7. Quy trình cập nhật và bàn giao

- SRS/Architecture là căn cứ phạm vi và contract; implementation-plan giữ mã
  task, trách nhiệm, phụ thuộc và lịch tuần. Google Docs là bản tóm tắt lịch;
  Google Sheets là trạng thái/đầu ra thực tế theo từng người.
- Mỗi thay đổi mốc/task cập nhật cùng mã và phiên bản ở cả ba nơi. Không sao
  chép trạng thái hoàn thành sang kế hoạch như một lời xác nhận mặc định.
- Chỉ tích hoàn thành khi có code/tài liệu, ví dụ đầu vào–đầu ra, lệnh/test,
  giới hạn và bên nhận đã chạy/review được. Có code riêng hoặc mock chưa đủ.
- Giữ các dòng lịch sử tuần 4–7; các checkbox tuần 4–5 là ghi nhận cũ chưa
  kiểm tra đầy đủ. Tuần 6 bỏ tích khi chưa đủ bằng chứng bàn giao, giữ lý do
  trong note. Tuần 8 bổ sung mục tiêu lịch sử và hiện trạng cuối tuần 9, không
  dựng lại việc đã giao hoặc ngày đã hoàn thành.
- Tạo develop sau kiểm kê từ nền backend đã kiểm thử, đối chiếu thay đổi main
  và ghép từng module bằng commit/PR có test. Không merge hàng loạt rồi coi
  hệ thống đã chạy. Giữ nhánh cũ cho tới khi xác nhận phần việc được bảo toàn.
- Khi develop đạt ca tích hợp đã chọn, nhóm trưởng xác nhận nền chung; thành
  viên tạo nhánh feature từ develop và review/test trước khi ghép lại.
  main dành cho bản ổn định đã được nhóm xác nhận; không đổi nhánh mặc định
  hoặc chính sách GitHub nếu chưa có quyết định tương ứng.
- Issue/PR ghi một owner, reviewer, PL, output, tiêu chí xong, phụ thuộc, commit
  và expected/actual. Nếu trễ, cập nhật việc tồn và tác động đến bên nhận.

## 8. Đánh giá và bản nộp

Dữ liệu có nguồn/hash/vai trò; V2 không được dùng như đầu vào bắt buộc. Dữ liệu
pilot tổng hợp không phải benchmark độc lập. Không dùng output thuật toán làm
đáp án; nhãn cần review và lưu bất đồng. Khóa code/config/dependency, dữ liệu,
nhãn và matching trước đánh giá tuần 12. Báo cáo TP/FP/FN cấp SemanticChange,
F1/Critical Recall, trường hợp chưa xác định, lỗi khía cạnh và số mẫu thực tế.
Nếu đã dùng test để chỉnh thuật toán, công bố và không gọi lần đo đó là độc lập.

Bản ứng viên cuối tuần 11; tuần 12 đánh giá/đóng gói/tái lập; cuối tuần 13 chốt
bản nộp sẵn sàng đầu tuần 14. Báo cáo/slide phải khớp commit/tag và dữ liệu.
Bộ bàn giao gồm code, dependency/config, hướng dẫn cài/chạy, dữ liệu mẫu được
phép phân phối, kết quả đánh giá, giới hạn và demo có ca lỗi/thiếu căn cứ.

Evaluation Plan vẫn là đầu ra còn thiếu của Tuấn Anh phối hợp Dũng/Ngọc Anh;
không tạo nội dung giả hoặc coi file được nhắc tới là đã tồn tại. Nhóm phải
hoàn thiện trước khi khóa tập test. Không tự hạ tiêu chí nghiệm thu để khớp
tiến độ; chức năng chưa đạt được công bố hoặc thống nhất điều chỉnh phạm vi.
