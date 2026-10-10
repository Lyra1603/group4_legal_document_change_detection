# HƯỚNG DẪN TUYỂN CHỌN DỮ LIỆU VÀ GÁN NHÃN

**Dự án:** Legal Document Change Detection  
**Phiên bản:** 1.0.1  
**Ngày cập nhật:** 10/10/2026  
**Trạng thái:** Bản đầu để nhóm review và kiểm chứng qua pilot tuần 6  
**Related Documents:** [BRD](brd.md), [SRS 1.2.0](srs.md), [Architecture 1.2.0](architecture.md), [Implementation Plan 1.3.0](implementation-plan.md), [Evaluation Plan — tài liệu dự kiến](test-evaluation-plan.md)

## 1. Mục đích và tài liệu tham chiếu

Hướng dẫn này giúp các thành viên chọn đúng cặp dữ liệu và tạo đáp án tham chiếu nhất quán cho phát triển, kiểm thử và đánh giá. Đáp án được lập từ hai đầu vào đã kiểm tra; không lấy kết quả thuật toán làm nhãn chuẩn.

SRS mục 1.3–1.4 sở hữu cấu trúc SemanticChange, ChangeAspect, ScoringResult và danh mục mã. Tài liệu này quy định cách đọc, điền, chia/gộp, chọn nhãn và review trong thực tế; không định nghĩa lại schema API. Phạm vi theo BRD/SRS; luồng phần mềm theo Architecture; công thức chỉ số, matching và phân chia dữ liệu theo Evaluation Plan.

Đầu ra của hoạt động dữ liệu gồm: file nguồn được giữ nguyên; cặp đầu vào đã kiểm tra; manifest; nhãn tham chiếu có khía cạnh và bằng chứng; nhật ký dựng phiên bản nếu có; biên bản review và phiên bản nhãn. Các ví dụ trong mục 7 minh họa quy tắc dự án, không khẳng định pháp luật đã thay đổi.

## 2. Tuyển chọn và quản lý dữ liệu

### 2.1. Nguồn và tiêu chí tuyển chọn

Nguồn chính là file Word (`.doc`, `.docx`) và PDF tải trực tiếp từ [Cơ sở dữ liệu quốc gia về văn bản pháp luật — VBPL](https://vbpl.vn/). Người thu thập mở trang hồ sơ, ghi URL trang và URL tệp tải xuống nếu lấy được, thời điểm tải, số/ký hiệu, tên, cơ quan, ngày và thông tin nguồn. So khớp metadata với nội dung tệp; chưa khớp thì giữ để kiểm tra, không tự xác nhận chỉ từ tên file.

| Tình huống | Cách xử lý |
| --- | --- |
| Hai trạng thái đầy đủ của cùng văn bản, xác định được chiều cũ/mới | Nhận sau kiểm tra nội dung, phạm vi và mốc phiên bản |
| Một bản đầy đủ và văn bản chỉ liệt kê sửa đổi | Lưu nguồn; người chuẩn bị dựng bản đầy đủ theo mục 2.4 trước khi nhận thành cặp |
| PDF và Word cùng một trạng thái nội dung | Hai dạng thể hiện của một nguồn; không tự gọi là V1/V2 |
| PDF có lớp chữ | Có thể làm đầu vào hệ thống sau kiểm tra trích xuất và giới hạn công bố |
| Word `.doc`, `.docx` | Giữ làm nguồn và phục vụ chuẩn bị dữ liệu; xuất PDF có lớp chữ, kiểm tra lại theo mục 2.3 trước khi đưa vào hệ thống |
| Scan, file hỏng/mật khẩu, thiếu phần Điều, sai cặp | Loại khỏi bộ so sánh hợp lệ; có thể lưu riêng làm ca kiểm thử lỗi |
| Mơ hồ về chuỗi sửa đổi, mốc áp dụng hoặc nguồn không khớp | Tạm giữ để review; không sử dụng như cặp pháp lý đã xác minh |

Không tự suy ra phiên bản từ ngày tải, ngày lưu file hoặc số thứ tự tên file. Cặp có nhiều mốc hiệu lực phải ghi rõ trạng thái nội dung được chọn; chưa xác định đủ thì không gọi là bản đang áp dụng tại một ngày cụ thể.

### 2.2. Đặc điểm tài liệu nguồn và cách đặt tên file

Tài liệu nguồn có thể được cung cấp dưới dạng Word (`.doc`, `.docx`) hoặc PDF. Một văn bản có thể có nhiều định dạng với cùng trạng thái nội dung; khác định dạng không đồng nghĩa khác phiên bản. Phạm vi đầu vào hệ thống hiện tại là hai PDF có lớp văn bản, không xử lý OCR; Word được dùng để lưu nguồn, đối chiếu và chuẩn bị dữ liệu.

Cấu trúc thường gặp gồm thông tin cơ quan ban hành, số/ký hiệu, địa danh và ngày tháng, tên văn bản, phần căn cứ, nội dung chia theo Chương/Mục/Điều/Khoản/Điểm, phần ký và phụ lục. Tùy loại văn bản, một số thành phần có thể không xuất hiện. Tài liệu có thể chứa bảng, chú thích, số trang, đầu/chân trang và Điều có hậu tố chữ. Văn bản hợp nhất có thể kèm thông tin văn bản gốc, các lần sửa đổi và mốc áp dụng khác nhau. Không mặc định mọi tài liệu có cùng bố cục hoặc đầy đủ mọi cấp cấu trúc.

Tên file nguồn có thể chứa số/ký hiệu, năm, chữ viết tắt loại văn bản hoặc cơ quan, mô tả nội dung và phần mở rộng. Đây là các dấu hiệu hỗ trợ tra cứu, không phải quy tắc bắt buộc cho mọi tệp trên VBPL.

| Thành phần có thể gặp | Cách hiểu và kiểm tra |
| --- | --- |
| Số thứ tự, năm | Đối chiếu với số/ký hiệu trong nội dung; không suy ra ngày hiệu lực từ năm trong tên |
| Chữ viết tắt loại văn bản, cơ quan | Hỗ trợ nhận diện; xác minh bằng nội dung và hồ sơ nguồn |
| Dấu chấm, gạch nối, gạch dưới, khoảng trắng | Có thể dùng để phân tách thành phần; không ép mọi tên vào một biểu thức cố định |
| `.pdf`, `.doc`, `.docx` | Biểu thị định dạng tệp, không chứng minh khác biệt nội dung hoặc phiên bản pháp lý |
| Hậu tố như `(1)`, `(2)` | Có thể phát sinh khi tải/lưu bản sao; không coi là số lần sửa đổi |

Giữ nguyên tên tệp tải về trong `original_filename`. Quy ước tên nội bộ của nhóm tách biệt với tên nguồn: `<pair_id>__v1__source.pdf`, `<pair_id>__v2__derived.pdf`, `<pair_id>__v2__synthetic.pdf`. Bản Word phục vụ biên soạn có thể lưu riêng với phần mở rộng tương ứng. Không sửa nội dung file gốc để đổi nhãn. Dùng số/ký hiệu, tên, cơ quan, ngày và nguồn để nhận diện văn bản; dùng SHA-256 để nhận diện chính xác tệp, không coi hash là danh tính pháp lý.

### 2.3. Lưu file, chuyển định dạng và manifest

Sử dụng các vị trí dữ liệu trong Architecture: `data/raw/` cho nguồn; `data/02_filtered_pairs/` cho cặp đầu vào đã chọn; `data/manifest.csv` cho metadata; `data/gold/` cho nhãn. Nhật ký dựng/chuyển file và review được lưu kèm cặp hoặc nhãn, không ghi đè nguồn.

Word `.doc` là định dạng cũ; nếu cần chỉnh sửa, mở bằng Word/LibreOffice và lưu thành `.docx`. Đổi phần mở rộng đơn thuần không chuyển định dạng. Bản Word dùng làm đầu vào so sánh phải được xuất thành PDF có lớp văn bản; việc lưu DOCX chỉ là bước chuẩn bị, không mở rộng phạm vi Reader. Ghi phần mềm, phiên bản, thời điểm, tên/hash trước và sau mỗi lần chuyển; review số Điều, thứ tự Khoản/Điểm, bảng, ký tự số và chú thích. PDF nguồn dùng trực tiếp được nếu trích xuất chữ đạt kiểm tra và không vượt giới hạn.

Manifest có thể dùng một dòng cho mỗi tệp; các tệp cùng cặp dùng chung pair_id. Bộ cột tối thiểu đề xuất:

| Nhóm | Cột cần ghi |
| --- | --- |
| Liên kết | pair_id, lineage_id, role (`v1`/`v2`/`reference`), format, local_path |
| Nguồn | original_filename, source_page_url, source_file_url, downloaded_at, sha256 |
| Văn bản | document_number, document_title, issuing_body, document_date, content_state_note |
| Nguồn gốc dữ liệu | origin (`SOURCE`/`CONVERTED`/`DERIVED_REAL`/`SYNTHETIC`), parent_files, construction_log |
| Kiểm soát | annotator, reviewer, review_status, label_version, guideline_version, split, limitations |

Nếu chưa có URL hồ sơ hoặc URL tải xuống, ghi rõ thông tin còn thiếu và bổ sung sau khi người thu thập xác nhận; không tự tạo URL/ItemID. Phân biệt nguồn do người cung cấp khai báo với nguồn đã đối chiếu hồ sơ.

Tài liệu có thể dài và chứa nhiều phụ lục; số trang không phải giới hạn duy nhất. Trước khi nhận để demo, đo dung lượng, ký tự trích xuất và số Điều so với cấu hình nhóm đã chốt. Không tự cắt bớt nội dung một Điều để vượt qua giới hạn. Có thể tạo fixture trích đoạn riêng nhưng phải đánh dấu không phải hai bản đầy đủ.

### 2.4. Dựng V2 từ V1 và chỉ dẫn sửa đổi

Đây là bước chuẩn bị dữ liệu do người thực hiện, ngoài Pipeline phần mềm.

1. Chọn V1 đầy đủ phản ánh trạng thái trước đợt sửa đổi; kiểm tra các sửa đổi trước đó và nguồn tương ứng.
2. Chọn văn bản sửa đổi và mốc áp dụng; tách đúng chỉ dẫn liên quan văn bản mục tiêu khi một văn bản sửa nhiều văn bản.
3. Lập bảng thao tác: chỉ dẫn/đoạn nguồn; văn bản đích; Điều/Khoản/Điểm đích; thao tác; nội dung trước/sau; mốc áp dụng; người thực hiện.
4. Áp dụng từng thao tác vào bản sao V1. Giữ phần không bị tác động; cập nhật nhãn/thứ tự chỉ khi có chỉ dẫn. Không coi nội dung không được nhắc là bị xóa.
5. Người khác kiểm tra toàn bộ chỉ dẫn, vùng đã sửa và vùng giữ nguyên; chưa xác định được đích hoặc mốc thì giữ cặp để kiểm tra, không nhận như V2 chuẩn.
6. Lưu V2, hash, nhật ký và review. Gắn DERIVED_REAL, ghi rõ bản nhóm dựng phục vụ nghiên cứu, không phải bản hợp nhất chính thức.

Văn bản có thể chứa nhiều mốc hiệu lực hoặc quy định chuyển tiếp. Ngày ban hành/ngày lập bản hợp nhất không đủ để xác nhận toàn bộ nội dung cùng có hiệu lực tại một thời điểm. Ghi `content_state_note` theo những mốc được kiểm tra; hệ thống so sánh nội dung không tự xác minh hiệu lực.

### 2.5. Tạo cặp giả định phục vụ pilot

Chọn một văn bản đầy đủ đã kiểm tra làm nền, tạo bản sao V1_SYNTHETIC_BASE và V2_SYNTHETIC rồi sửa có kiểm soát tại các Điều đã chọn. Giữ file nguồn riêng; đặt tên/metadata để không nhầm V2 giả định với tài liệu chính thức. Dùng nhật ký nêu từng sửa đổi giả định và review như mục 2.4; đánh dấu cặp là SYNTHETIC và ghi nguồn gốc từng tệp. Xuất cả hai bản thành PDF có lớp văn bản và kiểm tra lại trước khi chạy toàn Pipeline.

Mỗi ca mục 7 là một cặp/fixture riêng nếu không ghi rõ tổ hợp. Trích đoạn trong hướng dẫn chỉ minh họa; muốn test toàn Pipeline phải áp dụng vào các bản đầy đủ và kiểm tra lại. Hai định dạng của cùng nội dung không tự trở thành cặp có thay đổi. Các cặp cùng văn bản nền/chuỗi sửa đổi phải cùng lineage_id để Evaluation Plan không chia các biến thể gần trùng vào cả dev và test. Không dùng kết quả trên cặp giả định để tuyên bố chất lượng trên sửa đổi pháp luật thực tế.

## 3. Quy trình gán nhãn một cặp tài liệu

| Bước | Hoạt động | Đầu ra cần ghi |
| --- | --- | --- |
| 1 | Kiểm tra nguồn, trạng thái nội dung, chiều V1/V2 và định dạng | Cặp được nhận hoặc lý do giữ/loại |
| 2 | Đọc phần Điều trong hai bản; xác định Điều tương ứng hoặc thêm/xóa | Đối chiếu chuẩn và các vùng ghép mơ hồ |
| 3 | Rà soát toàn bộ các Điều thuộc phạm vi, gồm Điều không có thay đổi | Danh sách khác biệt và coverage; không chỉ đọc đoạn thuật toán tìm được |
| 4 | Xác định đổi nghĩa, chỉ đổi diễn đạt hoặc chưa đủ căn cứ | Kết luận và lý do, có bằng chứng |
| 5 | Chia/gộp SemanticChange, rồi ghi từng ChangeAspect | Các khía cạnh, giá trị trước/sau, diễn giải và quote |
| 6 | Chọn category tổng thể và severity theo mục 5 | ScoringResult cùng lý do/cảnh báo |
| 7 | Kiểm tra quote, nguồn, tính nhất quán; gửi review | Nhãn dự thảo và checklist |
| 8 | Review, giải quyết bất đồng, cố định phiên bản | Nhãn được chấp nhận hoặc vẫn chưa giải quyết |

Người gán nhãn phải đọc ngữ cảnh đủ để hiểu điều kiện, ngoại lệ, chủ thể, hành vi và đơn vị tính. Chỉ dẫn sửa đổi hoặc nhật ký giả định giúp tìm vị trí nhưng không thay việc phân tích ý nghĩa. Nhãn chuẩn lập độc lập với dự đoán; ID của gold và prediction không cần giống nhau, matching theo Evaluation Plan.

## 4. Quy tắc gán nhãn và các trường hợp dễ nhầm

### 4.1. Đổi nghĩa, đổi diễn đạt và chưa xác định

- Đổi nghĩa khi đủ bằng chứng nội dung quy định thay đổi: đối tượng, quyền/nghĩa vụ, điều kiện, thời hạn hoặc khía cạnh khác. Đổi ít chữ vẫn có thể đổi nghĩa.
- Đổi diễn đạt khi khác chữ nhưng xác định được nội dung tương đương; phải giải thích căn cứ. Độ tương đồng embedding hoặc không thấy từ khóa không phải căn cứ đủ.
- Chưa xác định khi thiếu ngữ cảnh, thiếu nội dung nguồn, dẫn chiếu ngoài hai đầu vào hoặc ghép Điều chưa chắc. Dùng null và cảnh báo theo SRS; không ép thành false/LOW.
- Không đổi thì SemanticDiffResult.changes = []; chỉ đổi diễn đạt vẫn có SemanticChange, aspects = [], category = WORDING_ONLY. Chưa xác định cũng có thể aspects = [], nhưng kết luận null và cảnh báo; không đồng nhất hai trường hợp.

### 4.2. Chia/gộp thay đổi và khía cạnh

Đơn vị thực hành là một quy định về một hành vi/quyền/nghĩa vụ hoặc một quan hệ áp dụng có thể đối chiếu riêng. Nhiều đặc điểm cùng thay đổi trong quy định đó là các khía cạnh của một SemanticChange. Hai quy định về hành vi hoặc nghĩa vụ khác nhau, dù trong một câu hoặc một Điều, được tách riêng.

Ví dụ: đổi chủ thể báo cáo sự cố và ngưỡng thời gian gián đoạn của cùng nghĩa vụ báo cáo → một SemanticChange với hai aspects. Đổi thời hạn báo cáo sự cố và đổi hồ sơ xin cấp phép ở quy định độc lập → hai SemanticChange. Một lần đổi thời hạn không sinh hai changes chỉ vì liên quan nghĩa vụ. Hai thời hạn độc lập của cùng quy định có thể có hai aspects cùng nhóm; phải có giá trị/bằng chứng riêng.

Nếu không thống nhất được ranh giới, ghi phương án và lý do để adjudication; khóa quy tắc sau pilot và cập nhật nhãn bị ảnh hưởng. Không thay cách chia để làm tăng chỉ số sau khi xem test.

### 4.3. Ranh giới 8 nhóm

Mã và cấu trúc theo SRS; bảng này hướng dẫn chọn nhóm ở ca giao nhau.

| Trường hợp | Nhóm sử dụng | Quy tắc phân biệt |
| --- | --- | --- |
| Thêm một tổ chức vào đối tượng chịu nghĩa vụ | SUBJECT_OBJECT | Chủ thể phải làm; khác với cơ quan có quyền xử lý |
| “Có thể” thành “phải”, bỏ hoặc thêm nghĩa vụ | RIGHTS_DUTIES_ACTIONS | Ghi cả hành vi và tính chất bắt buộc/cho phép/cấm |
| Thêm trường hợp miễn, điều kiện kích hoạt nghĩa vụ | CONDITIONS_EXCEPTIONS | Nếu chỉ đổi số trong ngưỡng đã có thì ưu tiên TIME_QUANTITY |
| Hạn nộp, ngưỡng phút gián đoạn, tỷ lệ/số lượng | TIME_QUANTITY | Giữ đơn vị, mốc tính và dấu “quá/từ/đến”; hiệu lực thuộc nhóm khác |
| Cơ quan tiếp nhận/quyết định, phương thức báo cáo, giấy tờ | PROCEDURE_AUTHORITY | Đổi cơ quan có thẩm quyền không ghi thêm SUBJECT_OBJECT trùng |
| Tăng mức phạt hoặc đổi hình thức xử lý | CONSEQUENCES_SANCTIONS | Giá trị phạt ghi ở nhóm này, không nhân bản vào TIME_QUANTITY |
| Đổi thuật ngữ định nghĩa hoặc đích dẫn chiếu | DEFINITIONS_REFERENCES | Phân tích trực tiếp nội dung có trong hai đầu vào; thiếu đích thì không suy diễn tác động |
| Địa bàn/lĩnh vực áp dụng, ngày hiệu lực, chuyển tiếp | SCOPE_EFFECT_TRANSITION | Mở rộng nhóm người chịu nghĩa vụ cụ thể ưu tiên SUBJECT_OBJECT; thời hạn thực hiện ưu tiên TIME_QUANTITY |

Một biến đổi chỉ có một nhóm; các biến đổi khác nhau của cùng quy định có thể thuộc nhiều nhóm. Không cố điền đủ 8 nhóm cho mỗi thay đổi. Định nghĩa thuật ngữ thay đổi được ghi nhóm định nghĩa; tác động tới các Điều khác chỉ ghi khi có đủ căn cứ trong phạm vi và tránh suy luận lan truyền không được kiểm chứng.

### 4.4. Giá trị, diễn giải và bằng chứng

- old_value/new_value mô tả đúng nội dung trước/sau, giữ đủ đơn vị và điều kiện. Quote là nguyên văn trong title/content ở đúng phía, không thay bằng câu diễn giải.
- interpretation trả lời “đã đổi thế nào”: ví dụ “hạ ngưỡng kích hoạt nghĩa vụ báo cáo từ quá 30 phút xuống quá 15 phút”; không chỉ viết “thời gian thay đổi”. diff_details tổng hợp các khía cạnh.
- Dùng quote ngắn đủ căn cứ ở cấp aspect và đoạn ngữ cảnh đủ ở cấp change. Dẫn vị trí Điều/Khoản/Điểm phục vụ gán nhãn; source_refs của Clause theo Reader. Không tự tạo tham chiếu trang/vị trí nếu chưa kiểm tra PDF đầu vào thực tế.
- None do phía không tồn tại khác None do chưa biết. interpretation phải nói rõ; chưa biết phải needs_review và có review_reason. Không tìm thấy không đồng nghĩa không có quy định.
- Giữ cảnh báo ghép mơ hồ từ Aligner. Nếu một khía cạnh có bằng chứng đổi nghĩa và một khía cạnh khác chưa rõ, có thể true kèm cảnh báo theo SRS; chấm severity chỉ khi đủ căn cứ tổng thể.

### 4.5. Các trường hợp cấu trúc dễ gây nhầm

Điều có thể có hậu tố chữ, chẳng hạn Điều 4a hoặc Điều 10b; không loại Điều vì đặc điểm này và không sửa nhãn để làm dãy số liên tục. Đánh lại số không tự là thêm/xóa. Tách/gộp chỉ được cảnh báo giới hạn ghép một–một, không giả định một cặp đã xử lý đầy đủ.

Phần mở đầu, chữ ký/xác thực và phụ lục nằm ngoài phạm vi so sánh. Chú thích có thể trích lại Điều của văn bản sửa đổi; không coi Điều trong chú thích là Điều mới của thân văn bản. Tách chú thích biên tập khỏi nội dung quy định; giữ nguồn để kiểm tra. Nếu Reader/Parser gộp nhầm hoặc không xác định được ranh giới, ghi lỗi/cảnh báo để xử lý, không dùng nhãn sai làm gold.

Một thay đổi chỉ có trong phụ lục được ghi là ngoài phạm vi, không gán cho Điều dẫn chiếu như nội dung Điều đã đổi. Số trang nguồn PDF tính theo trang vật lý file từ 1, không dùng số in trên trang nếu khác. Word/PDF có thể khác bố cục; source_refs phải phản ánh PDF thực tế được đưa vào hệ thống, không sao chép vị trí từ bản Word hoặc PDF khác.

## 5. Tiêu chí chọn nhãn tổng thể và mức độ

### 5.1. Chọn category tổng thể

category tóm tắt SemanticChange; giữ nguyên tất cả aspects. Chỉ chọn trong các field_group đã xác định có đổi nghĩa của thay đổi đó. Quy tắc pilot đề xuất: CONSEQUENCES_SANCTIONS → RIGHTS_DUTIES_ACTIONS → SUBJECT_OBJECT → CONDITIONS_EXCEPTIONS → PROCEDURE_AUTHORITY → TIME_QUANTITY → SCOPE_EFFECT_TRANSITION → DEFINITIONS_REFERENCES. Thứ tự này là quy ước trình bày của dự án, không phải thứ tự mức tác động pháp lý.

Ví dụ có SUBJECT_OBJECT và TIME_QUANTITY thì category = SUBJECT_OBJECT; reason vẫn giải thích cả việc mở rộng chủ thể và thay ngưỡng. Trường hợp đổi nội dung quyền/nghĩa vụ và chủ thể thì ưu tiên RIGHTS_DUTIES_ACTIONS. Chưa có nhóm được xác định đủ căn cứ thì category = null và cảnh báo; chỉ đổi diễn đạt thì WORDING_ONLY. Thứ tự ưu tiên phải được nhóm review qua pilot, ghi phiên bản trước sử dụng chung.

### 5.2. Bộ tiêu chí severity phục vụ dự án

Các mức dưới đây cụ thể hóa BRD để gán nhãn thử nghiệm; cần review chuyên môn khi có điều kiện. Chấm tác động trực tiếp thể hiện trong hai đầu vào, không suy đoán vụ việc/thiệt hại thực tế hoặc coi loại văn bản là mức độ.

| Mức | Quy tắc pilot | Ví dụ và ranh giới |
| --- | --- | --- |
| LOW | Đã xác định chỉ đổi diễn đạt/hình thức, không đổi nghĩa | “chậm nhất vào ngày” thành “không muộn hơn ngày”, mọi điều kiện giữ nguyên |
| MEDIUM | Đổi nghĩa về cách thực hiện có phạm vi hẹp; giữ nguyên nghĩa vụ cốt lõi, nhóm chủ thể và điều kiện quan trọng | Thay một phương thức báo cáo bằng phương thức khác đã xác định tương đương về yêu cầu; thiếu căn cứ tương đương thì review |
| HIGH | Có căn cứ thay đổi đáng kể chủ thể, nội dung nghĩa vụ/quyền, điều kiện hoặc ngưỡng/thời hạn của quy định | Mở rộng bên chịu nghĩa vụ; hạ ngưỡng kích hoạt báo cáo sự cố. Không tự thành CRITICAL chỉ vì có số liệu |
| CRITICAL | Đảo chiều bắt buộc/cho phép/cấm hoặc loại bỏ toàn bộ một nghĩa vụ/quyền cốt lõi, có bằng chứng rõ và được reviewer xác nhận theo ví dụ ranh giới | Từ bắt buộc báo cáo sự cố thành không phải báo cáo bất kỳ sự cố nào. Chỉ bỏ một phương thức báo cáo không đủ tiêu chí này |
| null | Thiếu căn cứ phân biệt mức hoặc chưa giải quyết mơ hồ có ảnh hưởng chấm điểm | Thiếu văn bản dẫn chiếu, thiếu nội dung sau sửa đổi, hoặc chưa xác định phần bị tác động |

MEDIUM/HIGH phân biệt bằng việc đổi cách thực hiện hạn chế hay đổi phạm vi/điều kiện/nội dung nghĩa vụ đáng kể. HIGH/CRITICAL phân biệt bằng sửa đặc điểm quan trọng hay đảo chiều/loại bỏ toàn bộ nội dung cốt lõi theo rubric. Khó phân biệt phải đưa review, không chọn mức theo cảm giác hay tỷ lệ số chữ đổi.

Chỉ đổi nghĩa đã xác định không gán LOW theo rubric hiện tại. Thêm/xóa Điều đánh giá nội dung, không tự CRITICAL. Một SemanticChange có một severity; không cộng điểm theo số aspects. is_critical = true khi và chỉ khi severity đã xác định CRITICAL; mức chưa rõ dùng null theo SRS. reason nêu quy tắc được áp dụng và bằng chứng hỗ trợ, không chỉ lặp lại mức.

## 6. Review, xử lý bất đồng và quản lý phiên bản nhãn

Dũng điều phối nguồn, manifest và guideline; Tuấn Anh điều phối nhãn chuẩn và đánh giá; Ngọc Anh review khả năng áp dụng quy tắc ngữ nghĩa. Cả nhóm có thể gán nhãn. Mỗi cặp có người gán nhãn và một người review khác; không tự review bản mình như kiểm tra độc lập. Khi có người có chuyên môn pháp luật tham gia, ghi rõ vai trò và phạm vi kiểm tra; không mặc định nhóm đã có chuyên gia.

### 6.1. Checklist review

- [ ] Đúng cặp/chiều, định dạng hợp lệ, nguồn và mốc trạng thái có ghi chú.
- [ ] Đã đọc đủ phần Điều, có kiểm tra thêm/xóa, đánh lại số và vùng chưa chắc.
- [ ] Không gộp phụ lục/chú thích thành Điều; Điều có hậu tố chữ được giữ.
- [ ] Ranh giới SemanticChange nhất quán; aspects không trùng biến đổi.
- [ ] Nhóm, giá trị, đơn vị, điều kiện, diễn giải và quote khớp hai đầu vào.
- [ ] category theo quy tắc; severity có lý do; null/rỗng/cảnh báo đúng nghĩa.
- [ ] Định danh và tham chiếu hợp lệ; một ScoringResult cho mỗi change_id.
- [ ] V2 dựng/giả định có nhật ký và người review; không nhầm nguồn thật.
- [ ] Nhãn được kiểm tra độc lập với dự đoán; có phiên bản và giới hạn.

### 6.2. Xử lý bất đồng

Lưu hai phương án cùng đoạn nguồn, tiêu chí viện dẫn và lý do. Hai người đối chiếu; nếu chưa thống nhất, Tuấn Anh điều phối một người thứ ba xem xét, phối hợp Dũng/Ngọc Anh hoặc giảng viên/người có chuyên môn khi có. Người quyết định ghi căn cứ và thay đổi cuối, không chỉ lấy đa số để xác nhận nội dung pháp lý.

Trạng thái quản lý nhãn đề xuất: DRAFT → IN_REVIEW → ACCEPTED, hoặc UNRESOLVED khi chưa giải quyết. Đây là metadata gán nhãn, không phải ComparisonReport.status. ACCEPTED nghĩa là được chấp nhận theo quy trình dự án, không chứng nhận đúng pháp lý tuyệt đối. Nhãn còn bất đồng không được coi là gold xác định; giữ nguyên danh sách và để Evaluation Plan quy định cách báo cáo/đánh giá, không tự coi negative hoặc loại bỏ âm thầm.

### 6.3. Phiên bản và điều kiện sử dụng

Lưu label_version, guideline_version, người/thời điểm gán và review, hash file V1/V2, nhật ký quyết định. Sửa input thì review lại nhãn liên quan. Đổi guideline thì rà những nhãn chịu ảnh hưởng; giữ lịch sử thay vì ghi đè không dấu vết.

Pilot tuần 6 có ví dụ không đổi, đổi diễn đạt, đổi nghĩa, nhiều khía cạnh, thêm/xóa và chưa xác định; ghi độ thống nhất và ca bất đồng để chỉnh guideline. Quy mô cuối và split theo Evaluation Plan, không đặt số lượng tùy ý trong tài liệu này. Khóa nhãn test và quy tắc trước đánh giá; các biến thể cùng nguồn/chuỗi sửa đổi giữ chung nhóm split.

Chỉ đưa vào bộ đánh giá xác định khi nguồn/cặp được kiểm tra, nhãn được ACCEPTED và cấu trúc đã validate. Báo riêng SYNTHETIC và DERIVED_REAL; số liệu từ mẫu giả định không đại diện tự động cho dữ liệu thực tế. Lỗi trích xuất/căn chỉnh của hệ thống không làm thay đổi nhãn chuẩn đã kiểm tra bằng tài liệu nguồn.

## 7. Ví dụ và mẫu gán nhãn hoàn chỉnh

### 7.1. Cách hiểu ví dụ giả định

Toàn bộ nội dung trước và sau trong mục này là ví dụ tự xây dựng để minh họa cách gán nhãn, không trích từ một văn bản pháp luật cụ thể và không mô tả quy định đang có hiệu lực. Số Điều và chủ thể trong ví dụ chỉ là định danh giả định; vị trí trang phải xác định khi tạo fixture thực tế.

Mỗi ca giả định độc lập, trừ EX-03 cố ý chứa hai khía cạnh trong cùng nghĩa vụ. Chỉ áp dụng đúng sửa đổi đã mô tả; giữ ngữ cảnh ngoài đoạn trích. Với fixture, quote phải khớp chuỗi Clause thực tế sau chuẩn hóa; khi xuất PDF phải xác minh lại source_refs.

### 7.2. Các ca tham chiếu

| Mã | Bối cảnh giả định | Nội dung trước → sau giả định | Nhãn/nhận xét đề xuất |
| --- | --- | --- | --- |
| EX-01 | Hạn nộp báo cáo định kỳ | “chậm nhất vào ngày 12” → “không muộn hơn ngày 12” | false; aspects = []; WORDING_ONLY; LOW, nếu các điều kiện khác giữ nguyên |
| EX-02 | Hạn nộp báo cáo tháng | “ngày 12 của tháng tiếp theo” → “ngày 10 của tháng tiếp theo” | TIME_QUANTITY; true; HIGH theo pilot vì rút ngắn thời hạn; các điều kiện khác giữ nguyên |
| EX-03 | Nghĩa vụ báo cáo sự cố tại Điều 5 giả định | “Đơn vị vận hành” → “Đơn vị vận hành và đơn vị cung cấp dịch vụ”; “quá 30 phút” → “quá 15 phút” trong cùng câu | Một change, hai aspects SUBJECT_OBJECT và TIME_QUANTITY; category SUBJECT_OBJECT; HIGH |
| EX-04 | Nghĩa vụ báo cáo sự cố | “Đơn vị vận hành phải báo cáo mọi sự cố” → “Đơn vị vận hành không phải báo cáo bất kỳ sự cố nào” | RIGHTS_DUTIES_ACTIONS; CRITICAL theo pilot nếu bỏ hoàn toàn nghĩa vụ cốt lõi; cần reviewer xác nhận và kiểm tra ngữ cảnh |
| EX-05 | Quyền chuyển hạn khi ngày cuối là ngày nghỉ | Bổ sung ngoại lệ “không áp dụng việc chuyển hạn nếu hệ thống tiếp nhận trực tuyến vẫn hoạt động” | CONDITIONS_EXCEPTIONS; true; HIGH vì thu hẹp quyền chuyển hạn; giữ cả ngữ cảnh thời hạn |
| EX-06 | Phương thức nộp báo cáo | “nộp qua cổng điện tử A” → “nộp qua cổng điện tử B” | PROCEDURE_AUTHORITY; true; MEDIUM chỉ khi ngữ cảnh xác nhận yêu cầu cốt lõi tương đương; thiếu căn cứ thì mức null |
| EX-07 | Định nghĩa hoạt động kiểm tra | “bao gồm thu thập thông tin, đánh giá và khuyến nghị” → “bao gồm thu thập thông tin và đánh giá” | DEFINITIONS_REFERENCES; true; severity null nếu chưa đủ căn cứ xác định tác động; không suy ra nghĩa vụ ở Điều khác tự bị bỏ |
| EX-08 | Điều khoản hiệu lực giả định | “có hiệu lực từ ngày 01/01/2030” → “có hiệu lực từ ngày 01/07/2030” | SCOPE_EFFECT_TRANSITION; true; mức xét theo rubric/ngữ cảnh; không khẳng định hiệu lực thật |
| EX-09 | Bổ sung hậu quả xử lý | Không có khoản tương ứng → “Đơn vị không nộp báo cáo phải thực hiện biện pháp khắc phục theo yêu cầu của cơ quan tiếp nhận” | CONSEQUENCES_SANCTIONS; old_value/old_quote = null vì khoản mới không tồn tại; mức theo nội dung và review, không tự CRITICAL |
| EX-10 | Đánh lại số Điều | Đổi nhãn Điều nhưng nội dung giữ nguyên và ghép chắc | Không tạo meaningful change chỉ vì đánh lại số; ghi alignment. Nếu đổi đích dẫn chiếu có nội dung khác thì xử lý riêng |
| EX-11 | Tách một Điều thành hai Điều | Chưa đủ căn cứ ghép một–một | needs_review; không khẳng định hai kết quả thêm/xóa là kết luận đã xác nhận |

Các kịch bản phải được đặt trong ngữ cảnh đầy đủ và ghi nguyên văn vào nhật ký khi tạo fixture. Bảng này minh họa cách chọn nhãn, không khẳng định các ca đã có tệp đầu vào chạy được.

### 7.3. Mẫu JSON hoàn chỉnh cho EX-03

Ví dụ sử dụng quy định tự xây dựng tại Điều 5 giả định. V1: “Đơn vị vận hành phải báo cáo cho cơ quan tiếp nhận ngay khi phát hiện sự cố gây gián đoạn dịch vụ quá 30 phút.” V2: “Đơn vị vận hành và đơn vị cung cấp dịch vụ phải báo cáo cho cơ quan tiếp nhận ngay khi phát hiện sự cố gây gián đoạn dịch vụ quá 15 phút.” Các phần còn lại được giữ nguyên khi tạo cặp đầy đủ. Hai aspects có đủ căn cứ trong giả định này; bản nhãn vẫn phải qua review theo mục 6.

```json
{
  "pair_key": "v1:article_5|v2:article_5",
  "changes": [
    {
      "change_id": "ex03:change_1",
      "is_meaningful_change": true,
      "diff_details": "Mở rộng chủ thể phải báo cáo sự cố sang đơn vị cung cấp dịch vụ và hạ ngưỡng gián đoạn kích hoạt nghĩa vụ từ quá 30 phút xuống quá 15 phút; hành vi báo cáo ngay khi phát hiện được giữ nguyên.",
      "aspects": [
        {
          "aspect_id": "a1",
          "field_group": "SUBJECT_OBJECT",
          "old_value": "Đơn vị vận hành",
          "new_value": "Đơn vị vận hành và đơn vị cung cấp dịch vụ",
          "interpretation": "Bổ sung đơn vị cung cấp dịch vụ vào nhóm chủ thể chịu nghĩa vụ báo cáo sự cố.",
          "old_quote": "Đơn vị vận hành",
          "new_quote": "Đơn vị vận hành và đơn vị cung cấp dịch vụ",
          "needs_review": false,
          "review_reason": ""
        },
        {
          "aspect_id": "a2",
          "field_group": "TIME_QUANTITY",
          "old_value": "Gián đoạn quá 30 phút",
          "new_value": "Gián đoạn quá 15 phút",
          "interpretation": "Hạ ngưỡng thời gian gián đoạn kích hoạt nghĩa vụ báo cáo; đây là ngưỡng sự cố, không phải hạn gửi báo cáo.",
          "old_quote": "quá 30 phút",
          "new_quote": "quá 15 phút",
          "needs_review": false,
          "review_reason": ""
        }
      ],
      "old_quote": "Đơn vị vận hành phải báo cáo cho cơ quan tiếp nhận ngay khi phát hiện sự cố gây gián đoạn dịch vụ quá 30 phút.",
      "new_quote": "Đơn vị vận hành và đơn vị cung cấp dịch vụ phải báo cáo cho cơ quan tiếp nhận ngay khi phát hiện sự cố gây gián đoạn dịch vụ quá 15 phút.",
      "needs_review": false,
      "review_reason": ""
    }
  ],
  "needs_review": false,
  "review_reason": ""
}
```

ScoringResult tương ứng, vẫn chấm một lần cho toàn bộ thay đổi:

```json
[
  {
    "change_id": "ex03:change_1",
    "category": "SUBJECT_OBJECT",
    "significance": "HIGH",
    "is_critical": false,
    "reason": "Theo thứ tự ưu tiên pilot, SUBJECT_OBJECT là nhãn tổng thể trong hai nhóm được xác định. Mở rộng chủ thể chịu nghĩa vụ và hạ ngưỡng kích hoạt là thay đổi đáng kể theo rubric HIGH; không đảo chiều hoặc loại bỏ nghĩa vụ cốt lõi nên không gán CRITICAL.",
    "needs_review": false,
    "review_reason": ""
  }
]
```

Hai khối là SemanticDiffResult và list[ScoringResult], không phải ComparisonReport đầy đủ. Khi tạo fixture toàn Pipeline, thêm AlignedPair/Clause, TextDiffResult, metadata hai file và source_refs theo SRS. Vị trí bằng chứng ở cả V1 và V2 phải được kiểm tra sau khi dựng PDF; không gán sẵn số trang từ ví dụ minh họa.

### 7.4. Mẫu hồ sơ gán nhãn cho mỗi cặp

| Nội dung | Giá trị cần ghi |
| --- | --- |
| Nhận diện | pair_id; lineage_id; file/hash V1/V2; nguồn và mốc trạng thái |
| Nguồn gốc | SOURCE/CONVERTED/DERIVED_REAL/SYNTHETIC; nhật ký liên quan |
| Bao phủ | Điều đã rà; vùng ngoài phạm vi; vùng thiếu/mơ hồ; đối chiếu Điều chuẩn |
| Nhãn | SemanticDiffResult và ScoringResult theo SRS; các Điều không đổi cũng có kết quả xác định |
| Review | Người gán/review; quyết định; bất đồng và căn cứ xử lý |
| Phiên bản | label_version; guideline_version; trạng thái nhãn; split theo Evaluation Plan |

Metadata quản lý nằm trong hồ sơ/manifest, không thêm vào schema API nếu SRS chưa quy định. Tuấn Anh chốt định dạng gold với Evaluator trong Evaluation Plan; Đức Anh hiện thực schema chung. JSON ở mục 7.3 là mẫu cấu trúc để nhóm bắt đầu fixture tuần 6; bộ ví dụ và tiêu chí pilot được review trước khi dùng làm gold đánh giá cuối.
