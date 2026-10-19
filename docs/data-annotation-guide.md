# HƯỚNG DẪN TUYỂN CHỌN DỮ LIỆU VÀ GÁN NHÃN

**Dự án:** Legal Document Change Detection  
**Phiên bản:** 1.2.0  
**Ngày cập nhật:** 14/10/2026  
**Trạng thái:** Hướng dẫn phục vụ pilot và review nhãn  
**Tài liệu liên quan:** [BRD](brd.md), [SRS 1.3.0](srs.md), [Architecture 1.3.0](architecture.md), [Evaluation Plan — tài liệu dự kiến](test-evaluation-plan.md)

## 1. Mục đích và phạm vi hướng dẫn

Tài liệu quy định cách tuyển chọn, lưu nguồn, tổ chức dữ liệu, lập nhãn tham chiếu và kiểm tra chất lượng nhãn. Đáp án được lập từ tài liệu nguồn đã kiểm tra, độc lập với kết quả thuật toán.

Một mẫu gồm văn bản ban đầu **V1**, văn bản sửa đổi **S** và các tài liệu tham chiếu được cung cấp cho mẫu đó nếu cần. Đơn vị gán nhãn là từng yêu cầu sửa đổi trong S và các thay đổi nội dung quy định tương ứng. Không bắt buộc dựng bản đầy đủ sau sửa đổi V2. V2 đã dựng có thể giữ làm tài liệu đối chiếu nội bộ, không thay thế V1, S hoặc bằng chứng nguồn.

| Nội dung | Tài liệu sở hữu |
| --- | --- |
| Mục tiêu, người dùng và phạm vi nghiệp vụ | BRD |
| Yêu cầu chức năng, mã nhãn và cấu trúc dữ liệu | SRS, đặc biệt mục 1.2–1.4 |
| Module, luồng xử lý, API và lựa chọn triển khai | Architecture |
| Tuyển chọn nguồn, quy tắc điền nhãn, ví dụ ranh giới và review | Hướng dẫn này |
| Thiết kế phép thử, matching, công thức chỉ số và kế hoạch chia tập | Evaluation Plan |

Đầu ra của hoạt động dữ liệu gồm file nguồn, bộ đầu vào của từng mẫu, manifest, nhãn tham chiếu có bằng chứng, hồ sơ review và phiên bản nhãn. Không định nghĩa lại schema API trong tài liệu này; các ví dụ chỉ minh họa cách điền theo SRS.

## 2. Tuyển chọn và quản lý dữ liệu

### 2.1. Nguồn và tiêu chí tuyển chọn

Nguồn chính của bộ dữ liệu là các tệp tải từ Cơ sở dữ liệu quốc gia về văn bản pháp luật (VBPL). Người thu thập ghi URL hồ sơ và URL tải tệp nếu có, thời điểm tải, số/ký hiệu, tên, cơ quan và ngày ban hành; đối chiếu metadata với nội dung tệp. Nguồn chưa kiểm tra phải ghi rõ, không tự xác nhận chỉ từ tên file.

| Tình huống | Cách xử lý dữ liệu |
| --- | --- |
| V1 và S có chỉ dẫn sửa đổi V1 | Nhận sau khi kiểm tra quan hệ, nội dung và trạng thái nền; không yêu cầu V2 |
| S sửa nhiều văn bản | Giữ toàn bộ S; đánh dấu từng yêu cầu thuộc V1, thuộc văn bản khác hoặc chưa rõ đối tượng |
| Cần nội dung dẫn chiếu ngoài V1 và S | Thu thập tài liệu tham chiếu phù hợp cho mẫu đủ căn cứ; hoặc ghi rõ là mẫu kiểm tra thiếu căn cứ |
| Chưa xác định V1 có phản ánh đúng trạng thái trước sửa đổi | Giữ để review; không mặc định bản gốc đầu tiên luôn là trạng thái nền phù hợp |
| Hai bản đầy đủ hoặc bản hợp nhất | Có thể giữ làm nguồn đối chiếu; không tự dùng bản đầy đủ sau sửa đổi thay S trong bộ đầu vào chính |
| PDF và DOCX cùng nội dung | Hai dạng thể hiện của cùng tài liệu, không tự coi là hai phiên bản pháp lý |
| DOCX hoặc PDF có lớp chữ | Nhận sau kiểm tra nội dung, cấu trúc và khả năng đọc |
| Word `.doc` | Giữ nguồn; chuyển thực sự sang DOCX và kiểm tra lại |
| Scan, tệp hỏng/mật khẩu hoặc sai cặp | Không dùng như mẫu đầu vào hợp lệ; có thể lưu riêng làm ca lỗi có ghi rõ mục đích |

Không suy ra phiên bản hoặc hiệu lực từ ngày tải, ngày lưu hay hậu tố tên file. Ghi rõ mốc trạng thái và các sửa đổi trước đó đã kiểm tra. Một mẫu có thể cố ý thiếu tài liệu tham chiếu nhưng phải xác định được phần kết luận mong đợi và phần phải để chưa rõ.

### 2.2. Đặc điểm nguồn và cách đặt tên

DOCX là định dạng chính; PDF có lớp văn bản là định dạng hỗ trợ, không bao gồm OCR. Tài liệu có thể chia Chương/Mục/Điều/Khoản/Điểm, có bảng, chú thích, đầu/chân trang, phụ lục và Điều có hậu tố chữ. Không mặc định mọi tệp cùng bố cục hoặc dùng Word Heading.

Giữ tên tải về trong `original_filename`. Tên nội bộ đề xuất:

- V1: `<document_key>_v1.docx`.
- S: `<amendment_key>_amendment.docx`.
- Tài liệu tham chiếu: `<reference_key>.docx` hoặc `.pdf` theo định dạng thực tế.

`document_key`, `amendment_key` và `reference_key` hỗ trợ nhận diện tệp; không nhất thiết giống nhau vì S và tài liệu tham chiếu có số hiệu riêng. PDF giữ đuôi `.pdf`; không đổi đuôi để giả định dạng. Hậu tố `(1)`, `(2)` có thể chỉ là bản sao tải xuống. Vai trò được ghi rõ trong manifest, không suy ra từ tên hoặc năm. SHA-256 nhận diện chính xác tệp, không chứng minh danh tính hay hiệu lực pháp lý.

### 2.3. Thư mục, chuyển định dạng và manifest

`data/` nằm ngang cấp `docs/`. T1 là nhóm mục đích dữ liệu được giải thích trong `data/README.md`; từng mẫu có mã ổn định như T1-001.

```text
data/
  README.md
  manifest.csv
  raw/                         # File nguồn giữ nguyên
  T1/
    T1-001/
      <document_key>_v1.docx
      <amendment_key>_amendment.docx
      references/              # Tài liệu thực sự cung cấp cho mẫu, nếu có
      README.md                # Nguồn, vai trò, giới hạn và trạng thái mẫu
      gold.json                # Nhãn theo cấu trúc được thống nhất
      review.md                # Bất đồng, quyết định và phiên bản nhãn
```

Tệp dùng chung có thể được tham chiếu bằng đường dẫn và hash thay vì sao chép; hồ sơ phải xác định chính xác bộ file đưa vào từng mẫu. Giữ file nguồn riêng, không ghi đè. Bộ mẫu nhỏ có thể đưa lên GitHub; bỏ qua tệp tạm Word `~$...docx`. V2 dựng sẵn chỉ lưu riêng như tài liệu đối chiếu nội bộ, ghi nguồn gốc, không đặt vào `references/` của mẫu nếu không chủ định cung cấp nó làm đầu vào.

Với `.doc`, chuyển sang DOCX bằng công cụ phù hợp, không chỉ đổi phần mở rộng. PDF có thể giữ nguyên để kiểm tra đầu vào PDF hoặc chuyển sang DOCX để chuẩn bị dữ liệu. Khi chuyển, lưu công cụ/phiên bản, thời điểm, hash và liên kết trước–sau. Kiểm tra chữ, dấu phủ định, số liệu, đơn vị, thứ tự Điều/Khoản/Điểm, hàng/cột bảng và chú thích. Sai font/cỡ chữ chỉ chấp nhận khi không ảnh hưởng nội dung hoặc cấu trúc. Không sao chép vị trí nguồn giữa PDF và DOCX nếu chưa kiểm tra.

Manifest dùng một dòng cho mỗi tệp trong mỗi mẫu; các dòng cùng mẫu dùng `pair_id`:

| Nhóm | Trường quản lý dữ liệu |
| --- | --- |
| Liên kết | pair_id, lineage_id, document_id, role (`BASE`/`AMENDMENT`/`REFERENCE`), format, local_path |
| Nguồn | original_filename, source_page_url, source_file_url, downloaded_at, sha256 |
| Văn bản | document_number, document_title, issuing_body, document_date, content_state_note |
| Nguồn gốc | origin (`SOURCE`/`CONVERTED`/`DERIVED_REAL`/`SYNTHETIC`), parent_files, preparation_log |
| Kiểm soát | annotator, reviewer, review_status, label_version, guideline_version, split, limitations |

`document_id` của đầu vào theo SRS: `v1`, `s`, `ref_1`... Các trường quản lý bổ sung ở manifest không tự trở thành trường API. Tài liệu đối chiếu không đưa vào đầu vào được ghi riêng trong README với đường dẫn/hash, tránh nhầm với REFERENCE. Không tự tạo URL hoặc số hiệu còn thiếu.

### 2.4. Chuẩn bị tài liệu tham chiếu và bộ căn cứ

Với mỗi dẫn chiếu cần để hiểu thay đổi, ghi văn bản, Điều/Khoản/Điểm/bảng cần đọc, mục đích dùng làm căn cứ trước/sau hoặc ngữ cảnh, và trạng thái theo ReferenceRequirement của SRS:

| Trạng thái | Cách gán |
| --- | --- |
| AVAILABLE | Đã có tài liệu phù hợp, tìm được đúng nội dung và ghi bằng chứng |
| MISSING | Tài liệu/nội dung cần thiết chưa được cung cấp trong bộ đầu vào của mẫu |
| UNRESOLVED | Có file nhưng chưa xác định đúng phiên bản, vị trí, phạm vi hoặc nội dung cần đọc |

Đổi dẫn chiếu A → B: xác định được thay đổi tên/đích dẫn chiếu từ V1 và S chưa đủ để kết luận mức thu, đối tượng hoặc điều kiện đã thay đổi thế nào. Phân tích tác động cần nội dung A và B cùng ngữ cảnh liên quan nếu chúng chưa nằm trong đầu vào.

Có thể tạo hai biến thể cùng nguồn: mẫu đủ tham chiếu và mẫu thiếu tham chiếu. Giữ cùng `lineage_id`, ghi rõ file được cung cấp ở từng mẫu và lập nhãn theo đúng bộ căn cứ đó. Không lấy thông tin chỉ có ở bộ đầy đủ để gán kết luận chắc chắn cho bộ thiếu. Nếu tiếp tục gặp phụ thuộc dẫn chiếu chưa giải quyết, ghi giới hạn cụ thể.

### 2.5. Tạo dữ liệu giả định và tài liệu đối chiếu

Tạo mẫu giả định bằng V1 đã kiểm tra và S giả định chứa chỉ dẫn sửa đổi rõ ràng; ghi `SYNTHETIC`, nguồn nền và nhật ký các thay đổi. S giả định phải được phân biệt với văn bản chính thức. Không cần tạo V2 đầy đủ. Tài liệu tham chiếu giả định cũng phải có đánh dấu và nội dung đủ để kiểm tra nhãn.

Nếu giữ V2 đã dựng từ nguồn thật, ghi `DERIVED_REAL`, nguồn V1/S, nhật ký và người review; chỉ dùng làm tài liệu hỗ trợ kiểm tra, không lấy bản dựng tự động làm gold. Nội dung trước/sau cục bộ trong nhãn vẫn phải truy về V1 và S.

Các biến thể cùng văn bản nền/chuỗi sửa đổi giữ chung `lineage_id` để tránh rò rỉ giữa tập phát triển và test. Fixture trích đoạn phải ghi rõ giới hạn; không trình bày như bộ văn bản đầy đủ. Kết quả trên mẫu giả định phải báo riêng với mẫu thực tế.

## 3. Quy trình gán nhãn một mẫu V1–S

| Bước | Hoạt động | Đầu ra cần ghi |
| --- | --- | --- |
| 1 | Kiểm tra nguồn, vai trò file và trạng thái nền V1 | Bộ đầu vào và lý do nhận/giữ/loại |
| 2 | Đọc toàn bộ S, liệt kê các yêu cầu và phân biệt văn bản đích | Danh sách chỉ dẫn, vị trí nguồn; APPLIES/OTHER_DOCUMENT/UNRESOLVED |
| 3 | Liên kết từng yêu cầu với V1 | Điều/Khoản/Điểm/cụm từ đích, thao tác, nội dung trước/sau cục bộ và bằng chứng |
| 4 | Đọc thông tin tổng quát V1 và ngữ cảnh cần thiết | Định nghĩa, điều kiện, ngoại lệ, dẫn chiếu và nhu cầu tài liệu còn thiếu |
| 5 | Rà hiệu lực/chuyển tiếp trong S | Nội dung, phạm vi áp dụng, bằng chứng và phần chưa rõ |
| 6 | Xác định đổi nghĩa, đổi diễn đạt hoặc chưa đủ căn cứ | SemanticChange, các ChangeAspect, giá trị và diễn giải có nguồn |
| 7 | Chọn category và significance theo mục 5 | ScoringResult cùng lý do/cảnh báo |
| 8 | Kiểm tra độ bao phủ, nguồn và cấu trúc; review độc lập | Nhãn được chấp nhận hoặc hồ sơ bất đồng |

Rà soát mọi yêu cầu trong S để tránh bỏ sót, nhưng chỉ phân tích ngữ nghĩa phần tác động đến V1 cùng ngữ cảnh cần thiết. Không phải gán một bản ghi cho mọi Điều không thay đổi của V1. Không dựa duy nhất vào vùng do thuật toán phát hiện. ID của nhãn chuẩn và dự đoán không bắt buộc giống nhau; cách matching thuộc Evaluation Plan.

## 4. Quy tắc gán nhãn và các trường hợp dễ nhầm

### 4.1. Đổi nghĩa, đổi diễn đạt và chưa xác định

- Đổi nghĩa khi đủ bằng chứng nội dung quy định thay đổi: đối tượng, quyền/nghĩa vụ, điều kiện, thời hạn hoặc khía cạnh khác. Đổi ít chữ vẫn có thể đổi nghĩa.
- Đổi diễn đạt khi khác chữ nhưng xác định được nội dung tương đương; phải giải thích căn cứ. Độ tương đồng embedding hoặc không thấy từ khóa không phải căn cứ đủ.
- Chưa xác định khi thiếu ngữ cảnh, thiếu nội dung nguồn, dẫn chiếu chưa được cung cấp hoặc vị trí đích chưa chắc. Dùng null và cảnh báo theo SRS; không ép thành false/LOW.
- Yêu cầu sửa đổi vẫn được ghi nhận kể cả chưa xác định được tác động. Chỉ đổi diễn đạt: có SemanticChange, aspects = [], category = WORDING_ONLY. Chưa xác định: có thể aspects = [], kết luận null và cảnh báo. Danh sách rỗng hoặc đoạn chữ giống nhau không tự chứng minh S không sửa V1.

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
| Đổi thuật ngữ định nghĩa hoặc đích dẫn chiếu | DEFINITIONS_REFERENCES | Phân tích trực tiếp nội dung có trong bộ tài liệu được cung cấp; thiếu đích thì không suy diễn tác động |
| Địa bàn/lĩnh vực áp dụng, ngày hiệu lực, chuyển tiếp | SCOPE_EFFECT_TRANSITION | Mở rộng nhóm người chịu nghĩa vụ cụ thể ưu tiên SUBJECT_OBJECT; thời hạn thực hiện ưu tiên TIME_QUANTITY |

Một biến đổi chỉ có một nhóm; các biến đổi khác nhau của cùng quy định có thể thuộc nhiều nhóm. Không cố điền đủ 8 nhóm cho mỗi thay đổi. Định nghĩa thuật ngữ thay đổi được ghi nhóm định nghĩa; tác động tới các Điều khác chỉ ghi khi có đủ căn cứ trong phạm vi và tránh suy luận lan truyền không được kiểm chứng.

### 4.4. Giá trị, diễn giải và bằng chứng

- old_value/new_value mô tả đúng nội dung trước/sau, giữ đủ đơn vị và điều kiện. Quote là nguyên văn trong V1, S hoặc tài liệu tham chiếu, kèm EvidenceRef xác định document_id và source_refs; không thay bằng câu diễn giải.
- interpretation trả lời “đã đổi thế nào”: ví dụ “hạ ngưỡng kích hoạt nghĩa vụ báo cáo từ quá 30 phút xuống quá 15 phút”; không chỉ viết “thời gian thay đổi”. diff_details tổng hợp các khía cạnh.
- Dùng quote ngắn đủ căn cứ ở cấp aspect và đoạn ngữ cảnh đủ ở cấp change. Dẫn vị trí Điều/Khoản/Điểm phục vụ gán nhãn; source_refs phải khớp tài liệu và quy ước nguồn trong SRS. Không tự tạo tham chiếu đoạn/bảng/vị trí nếu chưa kiểm tra DOCX thực tế; nếu nguồn là PDF, giữ cả tham chiếu nguồn PDF khi đã xác minh.
- None do phía không tồn tại khác None do chưa biết. interpretation phải nói rõ; chưa biết phải needs_review và có review_reason. Không tìm thấy không đồng nghĩa không có quy định.
- Giữ cảnh báo về chỉ dẫn hoặc vị trí đích chưa rõ. Nếu một khía cạnh có bằng chứng đổi nghĩa và một khía cạnh khác chưa rõ, có thể true kèm cảnh báo theo SRS; chấm significance chỉ khi đủ căn cứ tổng thể.

### 4.5. Chỉ dẫn sửa đổi và vị trí đích

Phân biệt Điều chứa chỉ dẫn trong S với Điều/Khoản/Điểm bị tác động trong V1. Một Điều S có thể có nhiều yêu cầu; một Điều V1 có thể bị nhiều yêu cầu tác động. `AmendmentItem` ghi yêu cầu sửa đổi, còn `SemanticChange` ghi thay đổi nội dung quy định; không đồng nhất số yêu cầu, số khía cạnh và số Điều.

| Chỉ dẫn trong S | Cách ghi nhãn |
| --- | --- |
| Thay toàn bộ Điều/Khoản/Điểm bằng nội dung được cung cấp | AMEND; lấy đúng đơn vị trước trong V1 và nội dung thay thế trong S; after_basis = QUOTED |
| Thay/bổ sung từ hoặc cụm từ trong một phạm vi | AMEND; giữ chỉ dẫn và phạm vi; nếu suy ra câu cục bộ sau sửa đổi, after_basis = DERIVED |
| Bổ sung đơn vị mới | ADD; ghi vị trí chèn, before_text = null vì chưa tồn tại; không gọi là thiếu căn cứ chỉ vì không tìm được đơn vị mới trong V1 |
| Bãi bỏ nội dung được chỉ định | REPEAL; giữ nội dung trước và chỉ dẫn trong S; after_text = null, after_basis = ABSENT |
| Không xác định được thao tác hoặc vị trí | UNRESOLVED ở trường tương ứng; giữ nguồn và lý do cần kiểm tra |

Không chỉ dựa vào một từ khóa để xác định thay toàn bộ hay thay cụm từ; đọc đầy đủ đối tượng, phạm vi và ngoại lệ. Nội dung không được nhắc trong S không phải bị bãi bỏ. Giữ nhãn Điều có hậu tố chữ, không tự đánh lại số. Với tách/gộp hoặc vị trí mơ hồ, ghi phần xác định được và phần cần review.

Điều được trích trong chú thích hoặc nội dung thay thế không tự trở thành Điều độc lập của S. Phần mở đầu, chữ ký và phụ lục không được đối chiếu toàn diện; bảng/đoạn liên quan vẫn có thể làm căn cứ. Chỉ dẫn thay phụ lục được ghi nhận với vị trí đích và giới hạn xử lý; không gán nhầm nội dung phụ lục thành nội dung Điều dẫn chiếu.

### 4.6. Nội dung cục bộ, ngữ cảnh và dẫn chiếu

`before_text` là nội dung trước trong V1; `after_text` là nội dung cục bộ sau sửa đổi. Phân biệt nội dung trích trực tiếp (`QUOTED`), suy ra từ chỉ dẫn (`DERIVED`), không tồn tại (`ABSENT`) và chưa xác định (`UNRESOLVED`) theo SRS. Chưa biết không được thay bằng chuỗi rỗng như đã bãi bỏ.

Nội dung suy ra không được đặt vào quote như nguyên văn nguồn. `new_quote` có thể là null nếu không có câu sau được trích trực tiếp; giữ bằng chứng của V1 và chỉ dẫn S, giải thích phép suy ra. Trường hợp suy ra rõ ràng không tự là thiếu căn cứ.

Đọc ngữ cảnh giữ nguyên có liên quan: định nghĩa, đối tượng, điều kiện và ngoại lệ. Thông tin tổng quát V1 giúp định hướng nhưng không thay thế đoạn nguồn. Không biến thông tin giữ nguyên thành một aspect thay đổi. Với dẫn chiếu, gán trạng thái căn cứ theo mục 2.4; có thể xác định đổi dẫn chiếu nhưng để tác động thực chất và mức độ chưa xác định.

### 4.7. Hiệu lực và chuyển tiếp

Ghi nội dung hiệu lực/chuyển tiếp được nêu trong S, phạm vi áp dụng và bằng chứng trong `EffectInfo`. Rà ngoại lệ và mốc riêng; không tự áp một ngày chung cho mọi yêu cầu hoặc lấy ngày ban hành thay ngày hiệu lực.

Chưa rõ phạm vi áp dụng: ghi needs_review và lý do. Không thấy thông tin liên quan: effect_info rỗng kèm lý do và cảnh báo theo SRS. Đây là nhãn nội dung được nêu trong nguồn, không xác nhận hiệu lực pháp lý thực tế.

Một ngày hiệu lực được nêu trong S không tự là thay đổi ngày hiệu lực của V1. Chỉ tạo aspect SCOPE_EFFECT_TRANSITION về thay đổi trước–sau khi có đủ bằng chứng đối chiếu; nếu chỉ là thông tin áp dụng của S thì giữ ở EffectInfo.

## 5. Tiêu chí chọn nhãn tổng thể và mức độ

### 5.1. Chọn category tổng thể

category tóm tắt SemanticChange; giữ nguyên tất cả aspects. Chỉ chọn trong các field_group đã xác định có đổi nghĩa của thay đổi đó. Quy tắc pilot đề xuất: CONSEQUENCES_SANCTIONS → RIGHTS_DUTIES_ACTIONS → SUBJECT_OBJECT → CONDITIONS_EXCEPTIONS → PROCEDURE_AUTHORITY → TIME_QUANTITY → SCOPE_EFFECT_TRANSITION → DEFINITIONS_REFERENCES. Thứ tự này là quy ước trình bày của dự án, không phải thứ tự mức tác động pháp lý.

Ví dụ có SUBJECT_OBJECT và TIME_QUANTITY thì category = SUBJECT_OBJECT; reason vẫn giải thích cả việc mở rộng chủ thể và thay ngưỡng. Trường hợp đổi nội dung quyền/nghĩa vụ và chủ thể thì ưu tiên RIGHTS_DUTIES_ACTIONS. Chưa có nhóm được xác định đủ căn cứ thì category = null và cảnh báo; chỉ đổi diễn đạt thì WORDING_ONLY. Thứ tự ưu tiên phải được nhóm review qua pilot, ghi phiên bản trước sử dụng chung.

### 5.2. Bộ tiêu chí significance phục vụ dự án

Các mức dưới đây cụ thể hóa BRD để gán nhãn thử nghiệm; cần review chuyên môn khi có điều kiện. Chấm tác động trực tiếp thể hiện trong bộ tài liệu được cung cấp, không suy đoán vụ việc/thiệt hại thực tế hoặc coi loại văn bản là mức độ.

| Mức | Quy tắc pilot | Ví dụ và ranh giới |
| --- | --- | --- |
| LOW | Đã xác định chỉ đổi diễn đạt/hình thức, không đổi nghĩa | “chậm nhất vào ngày” thành “không muộn hơn ngày”, mọi điều kiện giữ nguyên |
| MEDIUM | Đổi nghĩa về cách thực hiện có phạm vi hẹp; giữ nguyên nghĩa vụ cốt lõi, nhóm chủ thể và điều kiện quan trọng | Thay một phương thức báo cáo bằng phương thức khác đã xác định tương đương về yêu cầu; thiếu căn cứ tương đương thì review |
| HIGH | Có căn cứ thay đổi đáng kể chủ thể, nội dung nghĩa vụ/quyền, điều kiện hoặc ngưỡng/thời hạn của quy định | Mở rộng bên chịu nghĩa vụ; hạ ngưỡng kích hoạt báo cáo sự cố. Không tự thành CRITICAL chỉ vì có số liệu |
| CRITICAL | Đảo chiều bắt buộc/cho phép/cấm hoặc loại bỏ toàn bộ một nghĩa vụ/quyền cốt lõi, có bằng chứng rõ và được reviewer xác nhận theo ví dụ ranh giới | Từ bắt buộc báo cáo sự cố thành không phải báo cáo bất kỳ sự cố nào. Chỉ bỏ một phương thức báo cáo không đủ tiêu chí này |
| null | Thiếu căn cứ phân biệt mức hoặc chưa giải quyết mơ hồ có ảnh hưởng chấm điểm | Thiếu văn bản dẫn chiếu, thiếu nội dung sau sửa đổi, hoặc chưa xác định phần bị tác động |

MEDIUM/HIGH phân biệt bằng việc đổi cách thực hiện hạn chế hay đổi phạm vi/điều kiện/nội dung nghĩa vụ đáng kể. HIGH/CRITICAL phân biệt bằng sửa đặc điểm quan trọng hay đảo chiều/loại bỏ toàn bộ nội dung cốt lõi theo rubric. Khó phân biệt phải đưa review, không chọn mức theo cảm giác hay tỷ lệ số chữ đổi.

Chỉ đổi nghĩa đã xác định không gán LOW theo rubric hiện tại. Thêm/xóa Điều đánh giá nội dung, không tự CRITICAL. Một SemanticChange có một mức significance; không cộng điểm theo số aspects. is_critical = true khi và chỉ khi significance đã xác định CRITICAL; mức chưa rõ dùng null theo SRS. reason nêu quy tắc được áp dụng và bằng chứng hỗ trợ, không chỉ lặp lại mức.

## 6. Review, xử lý bất đồng và quản lý phiên bản nhãn

Phân công nhân sự theo Architecture. Mỗi cặp có người gán nhãn và một người review khác; không tự review bản mình như kiểm tra độc lập. Khi có người có chuyên môn pháp luật tham gia, ghi rõ vai trò và phạm vi kiểm tra; không mặc định nhóm đã có chuyên gia.

### 6.1. Checklist review

- [ ] Đúng V1–S, trạng thái nền và vai trò của từng tài liệu; file và hash khớp manifest.
- [ ] Đã rà toàn bộ S; mỗi yêu cầu có nhãn hoặc lý do chưa xử lý; phân biệt sửa V1 và văn bản khác.
- [ ] Đúng vị trí đích, thao tác và nội dung trước/sau; không nhầm số Điều S với V1.
- [ ] Phân biệt trích nguyên văn, nội dung suy ra, không tồn tại và chưa xác định.
- [ ] Ngữ cảnh tổng quát, định nghĩa và ngoại lệ cần thiết được đọc; không gán phần giữ nguyên thành thay đổi.
- [ ] Tài liệu tham chiếu và trạng thái AVAILABLE/MISSING/UNRESOLVED phản ánh đúng bộ đầu vào.
- [ ] Hiệu lực/chuyển tiếp có nguồn và phạm vi; chưa rõ được đánh dấu.
- [ ] Ranh giới SemanticChange nhất quán; aspects không trùng biến đổi; giá trị giữ đủ đơn vị và điều kiện.
- [ ] Quote/EvidenceRef khớp đúng tài liệu, vị trí và nội dung; không bịa vị trí trang/đoạn.
- [ ] category và significance có lý do; null/rỗng/cảnh báo đúng nghĩa; một ScoringResult cho mỗi change_id.
- [ ] Dữ liệu giả định/chuyển đổi/tài liệu dựng có nguồn gốc và nhật ký; không lấy dự đoán làm gold.
- [ ] Có người review độc lập, phiên bản nhãn và hồ sơ bất đồng.

### 6.2. Xử lý bất đồng

Lưu hai phương án cùng đoạn nguồn, tiêu chí viện dẫn và lý do. Hai người đối chiếu; nếu chưa thống nhất, người điều phối nhãn mời người thứ ba xem xét, tham khảo giảng viên/người có chuyên môn khi có. Người quyết định ghi căn cứ và thay đổi cuối, không chỉ lấy đa số để xác nhận nội dung pháp lý.

Trạng thái quản lý nhãn đề xuất: DRAFT → IN_REVIEW → ACCEPTED, hoặc UNRESOLVED khi chưa giải quyết. Đây là metadata gán nhãn, không phải ComparisonReport.status. ACCEPTED nghĩa là được chấp nhận theo quy trình dự án, không chứng nhận đúng pháp lý tuyệt đối. Nhãn còn bất đồng không được coi là gold xác định; giữ nguyên danh sách và để Evaluation Plan quy định cách báo cáo/đánh giá, không tự coi negative hoặc loại bỏ âm thầm.

### 6.3. Phiên bản và điều kiện sử dụng

Lưu label_version, guideline_version, người/thời điểm gán và review, hash file V1/S và toàn bộ tài liệu tham chiếu được cung cấp, nhật ký quyết định. Sửa input thì review lại nhãn liên quan. Đổi guideline thì rà những nhãn chịu ảnh hưởng; giữ lịch sử thay vì ghi đè không dấu vết.

Pilot tuần 6 có ví dụ không đổi, đổi diễn đạt, đổi nghĩa, nhiều khía cạnh, bổ sung/bãi bỏ, S sửa nhiều văn bản, hiệu lực có ngoại lệ, đủ/thiếu dẫn chiếu và chưa xác định; ghi độ thống nhất và ca bất đồng để chỉnh guideline. Quy mô cuối và split theo Evaluation Plan, không đặt số lượng tùy ý trong tài liệu này. Khóa nhãn test và quy tắc trước đánh giá; các biến thể cùng nguồn/chuỗi sửa đổi giữ chung nhóm split.

Chỉ đưa vào bộ đánh giá khi bộ đầu vào được kiểm tra, nhãn được ACCEPTED và cấu trúc đã validate. ACCEPTED có thể bao gồm nhãn mong đợi “chưa đủ căn cứ” ở mẫu cố ý thiếu tài liệu nếu người review đã xác nhận giới hạn đó; khác với UNRESOLVED do người gán nhãn còn bất đồng. Báo riêng SYNTHETIC và DERIVED_REAL; số liệu từ mẫu giả định không đại diện tự động cho dữ liệu thực tế. Lỗi trích xuất/liên kết của hệ thống không làm thay đổi nhãn chuẩn đã kiểm tra bằng tài liệu nguồn.

## 7. Ví dụ và hồ sơ gán nhãn

### 7.1. Cách hiểu ví dụ giả định

Các ví dụ tự xây dựng, không trích dẫn quy định pháp luật hiện hành. Nội dung trước lấy từ V1; nội dung mới/chỉ dẫn lấy từ S. Mỗi ca độc lập trừ EX-03 có nhiều khía cạnh của cùng nghĩa vụ. Khi tạo fixture, giữ đủ ngữ cảnh và kiểm tra vị trí nguồn trên file thực tế.

### 7.2. Các ca tham chiếu

| Mã | Bối cảnh giả định | Nội dung V1 → nội dung sửa đổi trong S | Nhãn/nhận xét đề xuất |
| --- | --- | --- | --- |
| EX-01 | Hạn nộp báo cáo định kỳ | “chậm nhất vào ngày 12” → “không muộn hơn ngày 12” | false; aspects = []; WORDING_ONLY; LOW, nếu các điều kiện khác giữ nguyên |
| EX-02 | Hạn nộp báo cáo tháng | “ngày 12 của tháng tiếp theo” → “ngày 10 của tháng tiếp theo” | TIME_QUANTITY; true; HIGH theo pilot vì rút ngắn thời hạn; các điều kiện khác giữ nguyên |
| EX-03 | Nghĩa vụ báo cáo sự cố tại Điều 5 giả định | “Đơn vị vận hành” → “Đơn vị vận hành và đơn vị cung cấp dịch vụ”; “quá 30 phút” → “quá 15 phút” trong cùng câu | Một change, hai aspects SUBJECT_OBJECT và TIME_QUANTITY; category SUBJECT_OBJECT; HIGH |
| EX-04 | Nghĩa vụ báo cáo sự cố | “Đơn vị vận hành phải báo cáo mọi sự cố” → “Đơn vị vận hành không phải báo cáo bất kỳ sự cố nào” | RIGHTS_DUTIES_ACTIONS; CRITICAL theo pilot nếu bỏ hoàn toàn nghĩa vụ cốt lõi; cần reviewer xác nhận và kiểm tra ngữ cảnh |
| EX-05 | Quyền chuyển hạn khi ngày cuối là ngày nghỉ | Bổ sung ngoại lệ “không áp dụng việc chuyển hạn nếu hệ thống tiếp nhận trực tuyến vẫn hoạt động” | CONDITIONS_EXCEPTIONS; true; HIGH vì thu hẹp quyền chuyển hạn; giữ cả ngữ cảnh thời hạn |
| EX-06 | Phương thức nộp báo cáo | “nộp qua cổng điện tử A” → “nộp qua cổng điện tử B” | PROCEDURE_AUTHORITY; true; MEDIUM chỉ khi ngữ cảnh xác nhận yêu cầu cốt lõi tương đương; thiếu căn cứ thì mức null |
| EX-07 | Định nghĩa hoạt động kiểm tra | “bao gồm thu thập thông tin, đánh giá và khuyến nghị” → “bao gồm thu thập thông tin và đánh giá” | DEFINITIONS_REFERENCES; true; significance null nếu chưa đủ căn cứ xác định tác động; không suy ra nghĩa vụ ở Điều khác tự bị bỏ |
| EX-08 | Điều khoản hiệu lực giả định | “có hiệu lực từ ngày 01/01/2030” → “có hiệu lực từ ngày 01/07/2030” | SCOPE_EFFECT_TRANSITION; true; mức xét theo rubric/ngữ cảnh; không khẳng định hiệu lực thật |
| EX-09 | Bổ sung hậu quả xử lý | Không có khoản tương ứng → “Đơn vị không nộp báo cáo phải thực hiện biện pháp khắc phục theo yêu cầu của cơ quan tiếp nhận” | CONSEQUENCES_SANCTIONS; old_value/old_quote = null vì khoản mới không tồn tại; mức theo nội dung và review, không tự CRITICAL |
| EX-10 | Đánh lại số Điều | Đổi nhãn Điều nhưng nội dung giữ nguyên và chỉ dẫn rõ | Không tạo meaningful change chỉ vì đánh lại số; giữ chỉ dẫn và vị trí đích. Nếu đổi đích dẫn chiếu có nội dung khác thì xử lý riêng |
| EX-11 | Tách một Điều thành hai Điều | Chưa đủ căn cứ xác định phạm vi và nội dung đích | needs_review; không khẳng định các kết quả bổ sung/bãi bỏ là kết luận đã xác nhận |
| EX-12 | Chuyển dẫn chiếu từ bảng A sang bảng B, thiếu B | Xác định được chỉ dẫn đổi dẫn chiếu | Ghi DEFINITIONS_REFERENCES cho phần xác định được; yêu cầu B và A nếu thiếu; không suy ra mức thu tăng/giảm, significance chưa đủ căn cứ thì null |
| EX-13 | S có ngày áp dụng chung và ngoại lệ cho một khoản | Hai mốc áp dụng được nêu rõ | Ghi EffectInfo với đúng phạm vi từng mốc; không coi ngày của S tự là thay đổi ngày hiệu lực V1 |

Các kịch bản phải được đặt trong ngữ cảnh đầy đủ và ghi nguyên văn vào nhật ký khi tạo fixture. Bảng này minh họa cách chọn nhãn, không khẳng định các ca đã có tệp đầu vào chạy được.

### 7.3. Mẫu điền nhãn cho EX-03

Giả định S thay toàn bộ khoản quy định nghĩa vụ báo cáo sự cố trong V1, cung cấp nguyên văn câu mới. `AmendmentItem` có amendment_id = ex03:amendment_1, operation = AMEND, applicability = APPLIES và after_basis = QUOTED. Câu trước nằm tại đoạn 13 của V1; câu mới nằm tại đoạn 4 của S trong fixture giả định. Các vị trí này chỉ có giá trị minh họa, phải đối chiếu trước khi dùng với file thật.

SemanticDiffResult theo SRS:

```json
{
  "amendment_id": "ex03:amendment_1",
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
          "review_reason": "",
          "evidence": [
            {
              "document_id": "v1",
              "source_refs": [
                "docx:paragraph_13"
              ],
              "quote": "Đơn vị vận hành"
            },
            {
              "document_id": "s",
              "source_refs": [
                "docx:paragraph_4"
              ],
              "quote": "Đơn vị vận hành và đơn vị cung cấp dịch vụ"
            }
          ]
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
          "review_reason": "",
          "evidence": [
            {
              "document_id": "v1",
              "source_refs": [
                "docx:paragraph_13"
              ],
              "quote": "quá 30 phút"
            },
            {
              "document_id": "s",
              "source_refs": [
                "docx:paragraph_4"
              ],
              "quote": "quá 15 phút"
            }
          ]
        }
      ],
      "old_quote": "Đơn vị vận hành phải báo cáo cho cơ quan tiếp nhận ngay khi phát hiện sự cố gây gián đoạn dịch vụ quá 30 phút.",
      "new_quote": "Đơn vị vận hành và đơn vị cung cấp dịch vụ phải báo cáo cho cơ quan tiếp nhận ngay khi phát hiện sự cố gây gián đoạn dịch vụ quá 15 phút.",
      "needs_review": false,
      "review_reason": "",
      "evidence": [
        {
          "document_id": "v1",
          "source_refs": [
            "docx:paragraph_13"
          ],
          "quote": "Đơn vị vận hành phải báo cáo cho cơ quan tiếp nhận ngay khi phát hiện sự cố gây gián đoạn dịch vụ quá 30 phút."
        },
        {
          "document_id": "s",
          "source_refs": [
            "docx:paragraph_4"
          ],
          "quote": "Đơn vị vận hành và đơn vị cung cấp dịch vụ phải báo cáo cho cơ quan tiếp nhận ngay khi phát hiện sự cố gây gián đoạn dịch vụ quá 15 phút."
        }
      ]
    }
  ],
  "needs_review": false,
  "review_reason": ""
}
```

ScoringResult cho cùng thay đổi:

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

Hai khối minh họa cách điền nhãn ngữ nghĩa và mức độ, không phải hồ sơ đầy đủ. Chỉ dẫn, vị trí đích, ngữ cảnh, dẫn chiếu và hiệu lực phải được ghi trong AmendmentItem theo SRS; không tạo thêm schema ở đây. Mẫu không quyết định trước số lượng file hoặc số trang của dữ liệu thực tế.

### 7.4. Hồ sơ gán nhãn mỗi mẫu

| Nội dung | Cần ghi |
| --- | --- |
| Nhận diện | pair_id, lineage_id, bộ file V1/S/tham chiếu, hash, nguồn và mốc trạng thái |
| Nguồn gốc | SOURCE/CONVERTED/DERIVED_REAL/SYNTHETIC; nhật ký chuẩn bị |
| Bao phủ | Danh sách chỉ dẫn trong S, vị trí đích, phần thuộc văn bản khác, vùng thiếu/mơ hồ |
| Căn cứ | Ngữ cảnh sử dụng, tài liệu được cung cấp, tài liệu còn thiếu, nguồn hiệu lực/chuyển tiếp |
| Nhãn | AmendmentItem, SemanticDiffResult và ScoringResult theo SRS; nhãn chưa xác định có lý do |
| Review | Người gán/review, phương án bất đồng, quyết định và căn cứ |
| Phiên bản | label_version, guideline_version, trạng thái review, split theo Evaluation Plan |

Metadata quản lý lưu trong manifest/hồ sơ, không tự thêm vào API. Định dạng đóng gói gold.json và cách matching được thống nhất với Evaluation Plan; tên trường nghiệp vụ tuân theo SRS.

### 7.5. Ngữ cảnh giữ nguyên ảnh hưởng cách hiểu

V1 có Điều 2 gồm khoản 1 “Tổ chức A phải nộp báo cáo” và khoản 2 “Báo cáo quy định tại khoản 1 được nộp trong 10 ngày”. S thay khoản 1 bằng “Tổ chức A và tổ chức B phải nộp báo cáo”.

Gán AMEND, đích khoản 1 Điều 2, khía cạnh SUBJECT_OBJECT vì thêm tổ chức B. Giữ khoản 2 làm bằng chứng ngữ cảnh để giải thích nghĩa vụ nộp trong 10 ngày cũng liên quan đến chủ thể được bổ sung. Không gán TIME_QUANTITY như thời hạn vừa đổi; không cần dựng toàn bộ V2 để lập nhãn này.
