# Bảng thuật ngữ

| Thuật ngữ | Định nghĩa đề xuất |
| :--- | :--- |
| **Clause** | Một Điều trong một phiên bản, gồm định danh, nhãn Điều, tiêu đề, nội dung và vị trí nguồn |
| **Aligned pair** | Một cặp điều khoản v1–v2 tương ứng, hoặc một điều chỉ có ở một bên. Có 3 loại: `PAIRED`, `ADDED`, `DELETED`. |
| **Meaningful change** | Thay đổi làm đổi nội dung quy định; sửa diễn đạt chỉ được coi là không đổi nghĩa khi giữ nguyên nội dung. |
| **Critical change** | Thay đổi nghĩa đáp ứng tiêu chí CRITICAL trong bộ tiêu chí nhóm thống nhất; thêm/xóa Điều không tự động là critical |

# SYSTEM REQUIREMENTS SPECIFICATION (SRS) & DATA CONTRACT

**Phiên bản tài liệu:** 1.2.0  
**Related Document:** [Business Requirements Document (BRD)](brd.md)

Hệ thống so sánh hai phiên bản đầy đủ của cùng một VBQPPL Việt Nam.
Người dùng cung cấp bản cũ và bản mới dưới dạng `.docx` hoặc PDF có
lớp chữ. Không hỗ trợ PDF scan hoặc dựng bản mới từ văn bản sửa đổi.

Luồng xử lý:
Hai file → Reader → Parser → Aligner → Text Diff → Semantic Diff
→ Classifier & Scorer → Báo cáo kết quả.

Reader và Parser chạy riêng cho từng phiên bản. Aligner nhận kết quả
của cả hai phiên bản để ghép các Điều tương ứng.

Bản đầu tiên ghép và so sánh ở cấp Điều; giữ nội dung Khoản/Điểm
bên trong từng Điều. Chỉ hỗ trợ ghép một Điều với một Điều;
trường hợp nghi ngờ tách/gộp hoặc ghép mơ hồ phải cảnh báo kiểm tra.

Pipeline điều phối các module. Backend API nhận yêu cầu từ giao diện,
gọi Pipeline và trả báo cáo để giao diện hiển thị.

Evaluator chạy riêng khi kiểm thử, đối chiếu kết quả với đáp án chuẩn;
không nằm trong luồng so sánh thông thường của người dùng.

Dưới đây là Data Contract (Hợp đồng dữ liệu) quy định bắt buộc định dạng Input/Output giữa các module. Mọi thay đổi đều phải được Nhóm trưởng phê duyệt.

## 1. Data Structures (Cấu trúc dữ liệu dùng chung)

### 1.1 Clause (Một Điều trong văn bản)

```python
class Clause:
    unit_id: str            # Định danh duy nhất trong phiên bản
    id: str                 # Nhãn Điều, ví dụ: "Điều 5"
    title: str              # Không có tiêu đề thì để ""
    content: str            # Giữ nội dung Khoản/Điểm và thứ tự
    source_refs: list[str]  # Vị trí nguồn chứa Điều này
```

Quy định:
- `unit_id` phân biệt các Điều trong từng phiên bản, ví dụ:
  `v1:article_5` và `v2:article_6`.
- `id` là nhãn trong tài liệu; có thể thay đổi khi đánh lại số Điều.
- `source_refs` tham chiếu các vị trí do Reader ghi nhận:
  trang PDF hoặc đoạn/bảng Word; một Điều có thể trải qua nhiều vị trí.
- Không xóa ngắt dòng phân chia Khoản/Điểm khi chuẩn hóa nội dung.
  
### 1.2 AlignedPair (Cặp Điều được căn chỉnh)

```python
class AlignedPair:
    pair_key: str              # Định danh cặp trong lần so sánh
    align_type: str            # PAIRED | ADDED | DELETED
    v1: Clause | None          # Điều bản cũ
    v2: Clause | None          # Điều bản mới
    needs_review: bool
    review_reason: str         # Để "" khi không cần kiểm tra
```

Quy định:
- PAIRED: có cả v1 và v2.
- ADDED: v1 = None, có v2.
- DELETED: có v1, v2 = None.
- pair_key được tạo từ unit_id hai phía, không chỉ từ số Điều.
- Mỗi Điều ở mỗi phiên bản xuất hiện đúng một lần trong kết quả.
- Ghép mơ hồ hoặc nghi ngờ tách/gộp Điều:
  needs_review = True và ghi rõ review_reason.
- Khi needs_review = True, việc ghép hoặc thêm/xóa chỉ là
  kết quả tạm thời; không được hiển thị như kết luận đã xác nhận.

### 1.3 SemanticDiffResult (Kết quả phân tích ngữ nghĩa)

```python
class ChangeAspect:
    aspect_id: str             # Duy nhất trong SemanticChange
    field_group: str | None    # Một trong 8 nhóm bên dưới; None nếu chưa rõ
    old_value: str | None      # Nội dung ngữ nghĩa trước thay đổi
    new_value: str | None      # Nội dung ngữ nghĩa sau thay đổi
    interpretation: str       # Giải thích sự chuyển đổi trước → sau
    old_quote: str | None      # Bằng chứng nguyên văn phía cũ nếu có
    new_quote: str | None      # Bằng chứng nguyên văn phía mới nếu có
    needs_review: bool
    review_reason: str

class SemanticChange:
    change_id: str             # Định danh thay đổi trong lần so sánh
    is_meaningful_change: bool | None
    diff_details: str         # Giải thích tổng thể của thay đổi
    aspects: list[ChangeAspect]
    old_quote: str | None      # None khi không có phía cũ
    new_quote: str | None      # None khi không có phía mới
    needs_review: bool
    review_reason: str

class SemanticDiffResult:
    pair_key: str
    changes: list[SemanticChange]
    needs_review: bool
    review_reason: str
```

Quy định:
- Một cặp Điều có thể có nhiều SemanticChange. Mỗi SemanticChange
  đại diện một thay đổi quy định có thể giải thích và đối chiếu riêng;
  bên trong có thể có nhiều ChangeAspect mô tả các khía cạnh liên quan.
- Các khía cạnh cùng mô tả một thay đổi quy định được nhóm chung;
  các thay đổi độc lập về quy định hoặc hành vi được tách riêng.
  Không tạo thêm SemanticChange chỉ vì có thêm một nhóm trường.
  Quy tắc chia/gộp chi tiết phải thống nhất với nhãn chuẩn trước đánh giá.
- is_meaningful_change:
  True = đổi nghĩa; False = không đổi nghĩa;
  None = chưa đủ căn cứ kết luận.
- Kết luận chưa xác định phải có needs_review = True.
- Bằng chứng phải lấy từ tiêu đề hoặc nội dung hai Điều tương ứng.
- Cảnh báo từ Aligner phải được giữ trong kết quả.
- changes rỗng chỉ biểu thị không có thay đổi sau khi so sánh
  thành công; không dùng để che giấu lỗi hoặc phần chưa xử lý.

Danh mục field_group của ChangeAspect:

| Mã | Nhóm trường | Nội dung phân tích |
| --- | --- | --- |
| SUBJECT_OBJECT | Chủ thể và đối tượng | Ai hoặc cái gì chịu tác động; chủ thể, đối tượng được bổ sung, loại bỏ hoặc thay thế |
| RIGHTS_DUTIES_ACTIONS | Nội dung quyền, nghĩa vụ và hành vi | Được làm, phải làm, bị cấm làm gì; tính chất và nội dung hành vi |
| CONDITIONS_EXCEPTIONS | Điều kiện và ngoại lệ | Điều kiện áp dụng, ngoại lệ, miễn trừ hoặc giảm yêu cầu |
| TIME_QUANTITY | Thời gian và định lượng | Thời hạn thực hiện, số tiền, tỷ lệ, số lượng, đơn vị, ngưỡng hoặc cách tính |
| PROCEDURE_AUTHORITY | Thủ tục, hồ sơ và thẩm quyền | Trình tự, phương thức, hồ sơ, chứng cứ; cơ quan hoặc người tiếp nhận, quyết định |
| CONSEQUENCES_SANCTIONS | Hậu quả pháp lý và chế tài | Trách nhiệm, hình thức xử lý, bồi thường và biện pháp khắc phục |
| DEFINITIONS_REFERENCES | Định nghĩa và dẫn chiếu | Nội dung định nghĩa, thuật ngữ và Điều/văn bản được viện dẫn |
| SCOPE_EFFECT_TRANSITION | Phạm vi, hiệu lực và chuyển tiếp | Phạm vi áp dụng, thời điểm quy định bắt đầu/hết áp dụng và xử lý trường hợp chuyển tiếp |

Đây là danh mục thiết kế dữ liệu của dự án, áp dụng trong phạm vi các
Điều được so sánh; không mở rộng phạm vi sang phần ngoài Điều hoặc
tự xác minh hiệu lực thực tế của văn bản.

Quy định về ChangeAspect:
- Mỗi khía cạnh có một field_group; interpretation chỉ rõ thành phần
  nào trong nhóm đã đổi và ý nghĩa trước → sau, không chỉ định nghĩa tên nhóm.
  Chỉ ghi các khía cạnh thực sự thay đổi hoặc đang cần xác minh;
  thông tin giữ nguyên được dùng làm ngữ cảnh trong diff_details.
- old_value/new_value là mô tả nội dung tương ứng, giữ đủ đơn vị,
  điều kiện và ngữ cảnh cần thiết. old_quote/new_quote phải là đoạn
  trích nguyên văn từ title/content của Clause ở đúng phía.
- None ở value/quote biểu thị không có nội dung tương ứng hoặc chưa
  xác định được; interpretation phải phân biệt rõ hai trường hợp.
  Nếu chưa xác định được thì needs_review = True và có review_reason.
  Không suy ra “không có quy định” chỉ vì không tìm thấy bằng chứng.
- Thêm/xóa có thể chỉ có value/quote ở một phía; phía không tồn tại
  dùng None. Khi có đủ căn cứ, một khía cạnh phải có ít nhất một
  đoạn trích; bằng chứng cấp SemanticChange vẫn giữ ngữ cảnh tổng thể.
- field_group = None chỉ khi chưa phân nhóm được; phải có cảnh báo.
  needs_review = False thì review_reason = "". Cảnh báo ở một khía cạnh
  phải được tổng hợp lên SemanticChange, SemanticDiffResult và ScoringResult.
- is_meaningful_change = True phải có ít nhất một khía cạnh đổi nghĩa
  có căn cứ. Nếu còn khía cạnh khác chưa rõ, vẫn giữ cảnh báo và
  không mô tả toàn bộ thay đổi như đã được xác định đầy đủ.
- Chỉ sửa diễn đạt và đã xác định không đổi nghĩa: aspects = [],
  is_meaningful_change = False; giữ giải thích và bằng chứng cấp thay đổi.
  Chưa đủ căn cứ: is_meaningful_change = None, needs_review = True;
  aspects có thể rỗng nếu chưa xác định được khía cạnh nào.
  Danh sách aspects rỗng tự nó không phải kết luận không có thay đổi.
- Cho phép nhiều khía cạnh cùng nhóm nếu mô tả các nội dung khác nhau.
  Không ghi trùng cùng một biến đổi vào nhiều nhóm: thời hạn thực hiện
  thuộc TIME_QUANTITY; thời điểm hiệu lực thuộc SCOPE_EFFECT_TRANSITION;
  mức phạt tiền thuộc CONSEQUENCES_SANCTIONS; cơ quan cấp phép thuộc
  PROCEDURE_AUTHORITY. Giá trị trước/sau vẫn được ghi đầy đủ.
- Nếu chỉ thay đổi dẫn chiếu mà thiếu nội dung văn bản được dẫn chiếu,
  mô tả thay đổi dẫn chiếu và giới hạn suy luận, không tự kết luận tác động rộng hơn.

Ví dụ giả định: “Doanh nghiệp phải nộp báo cáo trong 30 ngày.” →
“Doanh nghiệp và hộ kinh doanh phải nộp báo cáo trong 15 ngày.”
Có thể biểu diễn một SemanticChange về nghĩa vụ nộp báo cáo với hai khía cạnh:

| aspect_id | field_group | old_value / old_quote | new_value / new_quote | interpretation |
| --- | --- | --- | --- | --- |
| a1 | SUBJECT_OBJECT | Doanh nghiệp | Doanh nghiệp và hộ kinh doanh | Bổ sung hộ kinh doanh vào nhóm chủ thể phải nộp báo cáo. |
| a2 | TIME_QUANTITY | 30 ngày | 15 ngày | Rút ngắn thời hạn nộp báo cáo từ 30 xuống 15 ngày. |

Trong ví dụ này, value trùng với quote; cả hai khía cạnh có
needs_review = False và review_reason = "". SemanticChange có
is_meaningful_change = True, diff_details tổng hợp hai khía cạnh,
old_quote/new_quote là hai câu đầy đủ. Hành vi nộp báo cáo và tính chất
bắt buộc không đổi nên chỉ giữ làm ngữ cảnh. Mức độ được chấm riêng
theo guideline; ví dụ không mặc định là CRITICAL.

### 1.4 ScoringResult (Phân loại và chấm từng thay đổi)

```
class ScoringResult:
    change_id: str             # Tham chiếu SemanticChange
    category: str | None
    significance: str | None  # LOW | MEDIUM | HIGH | CRITICAL
    is_critical: bool | None
    reason: str
    needs_review: bool
    review_reason: str
```

Quy định:
- Mỗi SemanticChange có một ScoringResult tương ứng.
- Khi xác định được mức độ:
  is_critical = True khi và chỉ khi significance = CRITICAL.
- Chỉ sửa văn phong, không đổi nghĩa: significance = LOW.
- Thêm/xóa Điều không tự động được coi là CRITICAL.
- Chưa đủ căn cứ chấm mức độ:
  significance = None, is_critical = None,
  needs_review = True và ghi rõ lý do.
- category là nhãn tổng thể phục vụ tóm tắt/ưu tiên, không thay thế
  danh sách aspects. Với thay đổi nghĩa, chọn một trong các field_group
  đã xác định trong aspects theo quy tắc ưu tiên của guideline;
  reason giải thích việc chọn nhãn chính và mức độ của toàn bộ thay đổi.
- Chỉ sửa diễn đạt, không đổi nghĩa: category = WORDING_ONLY.
  Đây là nhãn tổng thể, không phải nhóm thứ chín của ChangeAspect.
- Chưa đủ căn cứ chọn nhãn tổng thể: category = None,
  needs_review = True và ghi rõ review_reason; vẫn giữ các khía cạnh
  đã xác định. Không bỏ bớt khía cạnh để ép về một category.
- Classifier & Scorer đọc các nhóm do Semantic Diff cung cấp để chọn
  nhãn tổng thể và chấm mức độ; không tự tạo bản aspects thứ hai.
- Mỗi SemanticChange vẫn có một ScoringResult; không chấm severity
  riêng cho từng ChangeAspect hoặc cộng điểm theo số lượng khía cạnh.
  Cảnh báo ở cấp khía cạnh được giữ đến kết quả chấm; nếu cảnh báo
  khiến chưa đủ căn cứ chấm mức độ tổng thể thì dùng None theo quy định trên.
- Chấm mức độ theo bộ tiêu chí và ví dụ nhóm đã thống nhất.

### 1.5 ExtractedDocument (Đầu ra Reader)

```
class SourceBlock:
    source_ref: str       # Ví dụ: "pdf:page_1" hoặc "docx:paragraph_5"
    text: str

class ExtractedDocument:
    version_id: str       # "v1" hoặc "v2" trong lần so sánh
    filename: str
    file_type: str        # DOCX | PDF_TEXT
    blocks: list[SourceBlock]
```

Quy định:
- blocks giữ thứ tự nội dung trong tài liệu, bao gồm nội dung bảng.
- Parser dùng blocks để tách Điều và lưu source_refs.
- Không đọc được nội dung thì báo lỗi, không trả văn bản rỗng hợp lệ.
- source_ref phải duy nhất trong từng phiên bản.
- Khi truy nguồn, dùng đồng thời version_id và source_ref.
- source_refs của v1 chỉ tra trong ExtractedDocument bản cũ;
  source_refs của v2 chỉ tra trong ExtractedDocument bản mới.

### 1.6 TextDiffResult (Đầu ra Text Diff)

```
class TextChange:
    field: str           # title | content
    type: str            # INSERT | DELETE | REPLACE
    old_text: str
    new_text: str
    old_start: int
    old_end: int
    new_start: int
    new_end: int

class TextDiffResult:
    pair_key: str
    changes: list[TextChange]
```

Quy định:
- Vị trí tính theo ký tự trong trường title/content, bắt đầu từ 0;
  khoảng [start, end) bao gồm start và không bao gồm end.
- INSERT: old_text = ""; DELETE: new_text = "".
- Vị trí phải khớp chính xác chuỗi của Clause được trả trong báo cáo.
- Điều thêm/xóa toàn bộ được biểu diễn bằng INSERT/DELETE
  cho các trường tương ứng; phía không tồn tại dùng chuỗi rỗng.
- Hai Điều giống nhau có changes = [].
- Đánh lại số Điều được thể hiện qua AlignedPair,
  không tính là thay đổi nội dung.

### 1.7 ComparisonReport (Báo cáo tổng hợp)

```
class PairResult:
    alignment: AlignedPair
    text_diff: TextDiffResult | None
    semantic_diff: SemanticDiffResult | None
    scoring: list[ScoringResult] | None

class ProcessingIssue:
    stage: str
    code: str
    message: str
    pair_key: str | None

class DocumentIdentity:
    version_id: str       # "v1" = bản cũ; "v2" = bản mới
    filename: str         # Tên file đầu vào, không chứa đường dẫn lưu nội bộ

class ComparisonReport:
    comparison_id: str
    old_document: DocumentIdentity
    new_document: DocumentIdentity
    status: str           # SUCCESS | PARTIAL | FAILED
    results: list[PairResult]
    warnings: list[ProcessingIssue]
    errors: list[ProcessingIssue]
```

Quy định:
- old_document.version_id = "v1" và new_document.version_id = "v2";
  metadata được Backend ghi nhận từ hai đầu vào và truyền cho Pipeline
  để giữ trong mọi ComparisonReport, kể cả PARTIAL hoặc FAILED.
- filename dùng để nhận diện file người dùng đã chọn, không xác nhận
  tên pháp lý hoặc hiệu lực của văn bản. Hai file có thể trùng tên;
  UI luôn hiển thị kèm nhãn bản cũ V1 / bản mới V2 và chiều V1 → V2.
- SUCCESS: các bước xử lý đã hoàn tất; vẫn có thể có kết quả
  cần người kiểm tra.
- PARTIAL: chỉ hoàn tất một phần; phải chỉ rõ phần chưa xử lý.
- FAILED: không tạo được báo cáo so sánh có thể sử dụng.
- Kết quả chưa được xử lý dùng None và ghi lỗi tương ứng;
  không thay bằng danh sách rỗng để biểu thị không có thay đổi.
- Mỗi ScoringResult tham chiếu change_id trong SemanticDiffResult.
- Cảnh báo ghép hoặc phân tích chưa chắc chắn phải giữ tới báo cáo.
- Chỉ thông báo "Không có thay đổi" khi status = SUCCESS,
  không còn phần chưa xác định và mọi TextDiffResult.changes đều rỗng.
- scoring = None: bước chấm mức độ chưa hoàn tất hoặc thất bại;
  phải có lỗi tương ứng.
- scoring = []: bước chấm mức độ đã hoàn tất nhưng không có
  SemanticChange nào để chấm.
- Nếu is_meaningful_change = None, không được tự chấm LOW;
  significance và is_critical phải là None, needs_review = True.
- Cảnh báo từ Aligner phải được giữ tới kết quả chấm mức độ.

  
## 2. Functional Requirements

| Mã | Chức năng | Đầu vào → đầu ra | Tiêu chí nghiệm thu tối thiểu |
|---|---|---|---|
| FR-01 | Reader | Một file → ExtractedDocument | Đọc DOCX/PDF text, giữ thứ tự và vị trí nguồn; không đọc được phải báo lỗi |
| FR-02 | Parser | Một ExtractedDocument → list[Clause] | Tách cấp Điều; giữ Khoản/Điểm; không nhầm dẫn chiếu thành đầu Điều; không tìm được Điều phải báo lỗi |
| FR-03 | Aligner | Hai list[Clause] → list[AlignedPair] | Mỗi Điều mỗi phía xuất hiện đúng một lần; hỗ trợ đánh lại số; ghép mơ hồ/tách/gộp phải cảnh báo |
| FR-04 | Text Diff | Một AlignedPair → TextDiffResult | Chỉ ra phần thêm/xóa/thay thế trong tiêu đề và nội dung; vị trí khớp chuỗi nguồn |
| FR-05 | Semantic Diff | AlignedPair và TextDiffResult → SemanticDiffResult | Phân tích từng thay đổi với đầy đủ ngữ cảnh; trả aspects theo 8 nhóm với giá trị cũ/mới, diễn giải và bằng chứng; chưa đủ căn cứ phải đánh dấu kiểm tra |
| FR-06 | Classifier & Scorer | AlignedPair và SemanticDiffResult → list[ScoringResult] | Chọn nhãn tổng thể từ các khía cạnh và chấm từng SemanticChange theo tiêu chí; is_critical nhất quán với significance; có lý do |
| FR-07 | Evaluator | Báo cáo dự đoán và đáp án chuẩn → chỉ số đánh giá | Tính cả thay đổi bỏ sót và dự đoán sai; không bỏ qua do ghép sai hoặc thiếu kết quả |
| FR-08 | Upload và xem kết quả | Hai file → báo cáo hiển thị | Chọn rõ cũ/mới; hiển thị chữ thay đổi, phân tích, mức độ, cảnh báo và lỗi |

Mục tiêu đánh giá: Change F1 ≥ 0,90 và Critical Change Recall ≥ 0,95
trên bộ kiểm thử độc lập. Đây là mục tiêu nghiệm thu, chưa phải
chất lượng đã được chứng minh của mã nguồn hiện tại.

Evaluator:
- Đối chiếu ở cấp từng SemanticChange theo quy tắc gán nhãn thống nhất;
  không đếm mỗi ChangeAspect thành một thay đổi độc lập. Nhãn chuẩn
  phải chứa các khía cạnh kỳ vọng; quy tắc matching quy định cách xử lý
  thiếu/sai khía cạnh trước khi chạy đánh giá, không tính đúng chỉ vì
  trùng một field_group. Ghi riêng lỗi nhóm, giá trị, diễn giải và bằng chứng.
- Dự đoán và nhãn chuẩn được ghép một-một; không tính trùng.
- Nhãn chuẩn không được tìm thấy phải tính là bỏ sót.
- Thay đổi nghĩa dự đoán không có nhãn chuẩn tương ứng phải tính
  là phát hiện sai sau khi kiểm tra tính đầy đủ của nhãn chuẩn.
- Một thay đổi critical chỉ được tính tìm đúng khi đối chiếu đúng
  thay đổi và dự đoán is_critical = True.
- Kết quả cần kiểm tra chưa được giải quyết không tính là tìm đúng.
- Mẫu số bằng 0 trả null kèm lý do; không báo đạt mục tiêu.
- Báo số mẫu kiểm thử và số kết quả cần kiểm tra cùng các chỉ số.

## 3. Thiết kế module
### 3.1 Module Reader(đọc file)

| | Reader |
|---|---|
| Nhận vào | Một file `.docx` hoặc PDF có lớp chữ |
| Công việc | Đọc nội dung chữ theo thứ tự trong tài liệu |
| Đầu ra | Nội dung văn bản đã trích xuất (ExtractedDocument) |
| Khi không đọc được chữ | Báo lỗi, không coi là văn bản rỗng hợp lệ |
- Thư viện dự kiến:
  + PyMuPDF đọc PDF: đã có trong requirements.txt của branch.
  + python-docx đọc Word: cần bổ sung khi triển khai.
 
### 3.2 Module Parser — tách văn bản thành các Điều: Reader trả về chữ trong file. Parser nhận phần chữ đó và xác định ranh giới từng Điều để các module sau có thể so sánh.
  
| Nội dung | Quy định |
|---|---|
| Đầu vào |Một ExtractedDocument |
| Xử lý | Nhận diện và tách từng Điều |
| Đầu ra | list[Clause] |
| Yêu cầu | Giữ đúng thứ tự; không nhầm câu dẫn chiếu “theo Điều 5…” thành đầu một Điều |
| Lỗi | Không tìm được Điều nào thì báo lỗi để kiểm tra |

Ví dụ nội dung chữ trong các blocks: 
```
Điều 1. Phạm vi điều chỉnh
Văn bản này quy định về...
Điều 2. Đối tượng áp dụng
Áp dụng đối với...
```

### 3.3 Module Aligner - ghép các Điều tương ứng giữa bản cũ và bản mới.

Ví dụ: Điều 5 bản cũ được chuyển thành Điều 6 bản mới. Aligner cần ghép chúng với nhau để module sau so sánh đúng nội dung.

| Nội dung | Quy định |
|---|---|
| Đầu vào | Hai danh sách Điều do Parser trả về: bản cũ và bản mới |
| Xử lý | Tìm các Điều tương ứng dựa trên số Điều, tiêu đề và nội dung |
| Đầu ra | Danh sách `AlignedPair` |
| Yêu cầu | Mỗi Điều xuất hiện đúng một lần trong kết quả; không ghép chỉ dựa vào số Điều |

Mỗi AlignedPair có ba trường chính:
| Trường | Ý nghĩa |
|---|---|
| `align_type` | `PAIRED`: ghép được; `ADDED`: thêm mới; `DELETED`: bị xóa |
| `v1` | Điều bản cũ; bằng `null` nếu thêm mới |
| `v2` | Điều bản mới; bằng `null` nếu bị xóa |

### 3.4 Module Text Diff — tìm những đoạn chữ thay đổi: Sau khi Aligner ghép đúng hai Điều, Text Diff chỉ ra chữ nào được thêm, xóa hoặc thay thế.

| Nội dung | Quy định |
|---|---|
| Đầu vào | Một `AlignedPair` do Aligner trả về |
| Xử lý | So sánh tiêu đề và nội dung của hai Điều |
| Đầu ra | TextDiffResult theo mục 1.6 |
| Loại thay đổi | `INSERT`: thêm; `DELETE`: xóa; `REPLACE`: thay thế |
| Điều thêm/xóa toàn bộ | Ghi nhận toàn bộ nội dung phía tương ứng |

Ví dụ:
- Cũ: “Phải nộp trong 30 ngày.”
- Mới: “Phải nộp trong 15 ngày.”

### 3.5 Module Semantic Diff — xác định thay đổi có làm đổi nghĩa hay không.

| Nội dung | Quy định |
|---|---|
| Đầu vào | Một `AlignedPair` và kết quả Text Diff; giữ đầy đủ nội dung hai Điều để hiểu ngữ cảnh |
| Xử lý | Phân biệt sửa cách diễn đạt với thay đổi nội dung, như quyền, nghĩa vụ, chủ thể, điều kiện, thời hạn hoặc chế tài |
| Đầu ra | SemanticDiffResult chứa danh sách SemanticChange; mỗi thay đổi có aspects theo hợp đồng mục 1.3 |
| Chưa đủ căn cứ | Đánh dấu cần kiểm tra; không tự kết luận là sửa văn phong |
| Ranh giới trách nhiệm | Semantic Diff xác định khía cạnh, field_group, nội dung trước/sau và diễn giải; Classifier & Scorer chọn nhãn tổng thể và chấm mức độ sau |

Quy định thêm: khi needs_review = true, cho phép is_meaningful_change = null để biểu thị chưa xác định.

Tiêu chí nghiệm thu tối thiểu:
- Chỉ sửa chính tả, không đổi nghĩa → false.
- “30 ngày” → “15 ngày” → true.
- “phải” → “có thể” trong cùng nghĩa vụ → true.
- Đổi chủ thể thực hiện dù không đổi số liệu → true.
- Một thay đổi đồng thời đổi chủ thể và thời hạn → giữ đủ hai khía cạnh,
  mỗi khía cạnh có nhóm, nội dung trước/sau, diễn giải và bằng chứng.
- Chỉ sửa diễn đạt → aspects rỗng và có giải thích không đổi nghĩa;
  chưa xác định được khía cạnh → giữ cảnh báo, không tự kết luận false.

### 3.6 Module Classifier & Scorer — phân loại và đánh giá mức độ quan trọng của thay đổi.

| Nội dung | Quy định |
|---|---|
| Đầu vào | `AlignedPair` và kết quả Semantic Diff |
| Xử lý | Xác định loại thay đổi và mức độ theo bộ tiêu chí thống nhất của nhóm |
| Đầu ra | list[ScoringResult], một kết quả cho mỗi SemanticChange|
| Yêu cầu | Mức độ phải có lý do dựa trên nội dung và bằng chứng của thay đổi |

Nhãn tổng thể category dùng 8 mã nhóm tại mục 1.3 hoặc WORDING_ONLY theo mục 1.4; thêm/xóa Điều được thể hiện ở align_type, còn nội dung thay đổi được phân tích trong aspects.

Quy tắc cần ghi rõ:
- significance nhận một trong bốn mức: LOW, MEDIUM, HIGH, CRITICAL.
- is_critical = true khi và chỉ khi significance = CRITICAL.
- Chỉ sửa văn phong, không đổi nghĩa → LOW.
- Thêm/xóa Điều không tự động được coi là CRITICAL.
- Chưa đủ căn cứ → needs_review = true, significance và is_critical để null.
- Bộ tiêu chí phân biệt các mức phải có ví dụ được nhóm thống nhất trước khi đánh giá hệ thống.

### 3.7 Module Evaluator — đo hệ thống làm đúng đến đâu: Evaluator đối chiếu kết quả dự đoán với ground truth: đáp án do người gán nhãn và kiểm tra trước.

| Nội dung | Quy định |
|---|---|
| Đầu vào | Kết quả pipeline và bộ đáp án chuẩn của cùng các cặp văn bản |
| Xử lý | Đối chiếu các thay đổi dự đoán với đáp án chuẩn |
| Đầu ra | Precision, Recall, Change F1, Critical Change Recall |
| Cách sử dụng | Chạy khi kiểm thử, đánh giá; không bắt buộc chạy mỗi lần người dùng so sánh |

Ý nghĩa các chỉ số:

| Chỉ số | Câu hỏi được trả lời |
|---|---|
| Precision | Trong các thay đổi nghĩa hệ thống báo, bao nhiêu là đúng? |
| Recall | Trong các thay đổi nghĩa thực sự, hệ thống tìm được bao nhiêu? |
| Change F1 | Điểm tổng hợp Precision và Recall |
| Critical Change Recall | Hệ thống tìm đúng bao nhiêu thay đổi trọng yếu thực sự? |

Yêu cầu nghiệm thu cần ghi:
- Mục tiêu: Change F1 ≥ 0,90, Critical Change Recall ≥ 0,95 trên bộ kiểm thử độc lập.
- Thay đổi có trong đáp án nhưng hệ thống bỏ sót phải được tính là lỗi; không bỏ qua do thiếu kết quả hoặc ghép sai.
- Kết quả needs_review chưa được giải quyết không được tính là phát hiện đúng; phải báo thêm số lượng cần kiểm tra.
- Tập kiểm thử không được dùng để điều chỉnh thuật toán.
- Chỉ số không tính được do mẫu số bằng 0 trả null kèm lý do; không báo đạt mục tiêu.

Ví dụ: đáp án có 10 thay đổi trọng yếu, hệ thống tìm đúng 8 → Critical Change Recall = 80%.

## 4. Yêu cầu tải tài liệu và xem kết quả

| Chức năng | Yêu cầu |
|---|---|
| Chọn đầu vào | Người dùng chọn hai file `.docx` hoặc PDF có lớp chữ, xác định rõ **bản cũ / bản mới** |
| Bắt đầu so sánh | Người dùng nhấn “So sánh”; hệ thống kiểm tra file rồi chạy pipeline |
| Trạng thái xử lý | Hiển thị đang xử lý, hoàn thành, hoàn thành một phần hoặc thất bại; phân biệt hoàn thành với kết quả còn cần kiểm tra |
| Xem kết quả | Hiển thị các Điều tương ứng, đoạn cũ/mới và phần chữ thay đổi |
| Nhận diện tài liệu | Hiển thị tên hai file từ old_document/new_document, nhãn bản cũ V1 / bản mới V2 và chiều V1 → V2 trong báo cáo, kể cả khi tên file giống nhau hoặc báo cáo chỉ hoàn tất một phần |
| Xem phân tích | Mỗi SemanticChange có kết luận đổi nghĩa, giải thích tổng thể, category, mức độ và lý do; hiển thị từng ChangeAspect gồm tên nhóm tiếng Việt, nội dung cũ/mới, interpretation, bằng chứng và cảnh báo. Phân biệt nhãn tổng thể với nhóm của khía cạnh; không chỉ hiển thị category rồi ẩn các khía cạnh còn lại |
| Vị trí nguồn | Bên cạnh nội dung mỗi Điều, hiển thị vị trí thuộc đúng V1/V2 từ Clause.source_refs: trang PDF hoặc đoạn/bảng DOCX; Điều thêm/xóa chỉ hiển thị nguồn ở phía tồn tại |
| Cần kiểm tra | Hiển thị rõ các kết quả `needs_review = true`; mức độ chưa xác định ghi “Chưa xác định” |
| Không có thay đổi | Chỉ thông báo khi xử lý thành công và không phát hiện thay đổi; nếu chỉ sửa văn phong thì vẫn hiển thị phần sửa |

Quy định hiển thị vị trí nguồn:
- Chuyển source_refs thành nhãn dễ đọc, ví dụ `pdf:page_3` →
  “Trang 3”, `docx:paragraph_12` → “Đoạn 12”, `docx:table_2` →
  “Bảng 2”. Số trang PDF tính từ trang đầu file, bắt đầu từ 1;
  đoạn và bảng DOCX được Reader đánh số riêng theo thứ tự xuất hiện,
  bắt đầu từ 1, bao gồm đoạn rỗng trong danh sách đoạn.
- Một Điều có nhiều source_refs phải hiển thị đủ các vị trí;
  nhãn ghi rõ đây là vị trí của Điều, không khẳng định đó là vị trí
  chính xác của từng old_quote/new_quote khi chưa có ánh xạ chi tiết.
- Người dùng đọc đoạn trích và vị trí để tự đối chiếu file gốc.
  Bản đầu không bắt buộc nhúng trình xem file hoặc mở đúng vị trí
  bằng một lần nhấn. Không suy ra số trang Word từ chỉ số đoạn/bảng.

Kiểm tra chất lượng giải thích và khả năng hiểu báo cáo theo BRD mục 10.1:
- Trên bộ ví dụ có đáp án tham chiếu đã rà soát, người đánh giá kiểm tra
  diff_details có mô tả đúng nội dung trước/sau; aspects có đủ nhóm
  liên quan, giá trị cũ/mới và interpretation đúng từng khía cạnh,
  không trùng lặp; old_quote/new_quote ở cả hai cấp khớp đầu vào;
  reason có căn cứ cho nhãn chính
  và mức độ; giải thích không suy diễn vượt bằng chứng và nêu rõ
  trường hợp chưa đủ căn cứ. Ghi kết quả đạt/chưa đạt từng tiêu chí
  và lỗi cụ thể; không dùng riêng F1 hoặc Critical Change Recall
  để kết luận chất lượng giải thích.
- Người tham gia thực hiện các nhiệm vụ: xác định đúng cũ/mới;
  tìm thay đổi và vị trí nguồn; giải thích nội dung trước/sau bằng
  lời của mình; hiểu lý do ưu tiên; nhận biết kết quả cần kiểm tra,
  báo cáo một phần và phạm vi chưa được so sánh.
- Ghi số nhiệm vụ hoàn thành đúng, thời gian thực hiện, lỗi diễn giải
  và phản hồi. Kiểm tra cả ca chỉ đổi diễn đạt, đổi nghĩa, thêm/xóa,
  chưa xác định và PARTIAL; loại thay đổi, mức độ và cảnh báo phải
  có nhãn chữ hoặc ký hiệu dễ hiểu, không chỉ phân biệt bằng màu.
- Quy mô mẫu, người tham gia, cách chấm và ngưỡng chấp nhận được chốt
  trong Evaluation Plan trước thử nghiệm. Nếu thành viên nhóm đóng
  vai luật sư/pháp chế hoặc sinh viên luật, phải ghi rõ giới hạn này.
  Đây là hoạt động đánh giá ngoài luồng so sánh, không yêu cầu thêm
  module hoặc chức năng thu thập phản hồi trong sản phẩm.

## 5. Xử lý lỗi và cảnh báo
   
| Tình huống | Hành vi yêu cầu |
|---|---|
| Thiếu một trong hai file hoặc sai định dạng | Không chạy; yêu cầu chọn đủ hai file `.docx` hoặc PDF có lớp chữ |
| File hỏng, có mật khẩu hoặc không đọc được chữ | Dừng xử lý; báo rõ file nào gặp lỗi |
| Parser không tìm được Điều | Báo lỗi cấu trúc; không trả kết quả “không có thay đổi” |
| Ghép Điều mơ hồ hoặc nghi ngờ tách/gộp Điều | Cảnh báo cần kiểm tra; không coi phần chưa ghép chắc chắn là thêm/xóa đã xác nhận |
| Phân tích nghĩa hoặc chấm mức độ chưa đủ căn cứ | Đánh dấu `needs_review = true`; kết luận chưa xác định để `null` |
| Một bước xử lý thất bại | Báo bước gặp lỗi; nếu hiển thị kết quả một phần, phải ghi rõ báo cáo chưa hoàn tất |
Yêu cầu chung: thông báo lỗi phải dễ hiểu và có hướng xử lý; không hiển thị lỗi kỹ thuật nội bộ cho người dùng.

## 6. Yêu cầu vận hành

| Nội dung | Yêu cầu |
|---|---|
| Cấu hình | Giới hạn dung lượng file và thời gian xử lý phải cấu hình được; giá trị cụ thể cần nhóm thống nhất trước nghiệm thu |
| Tính toàn vẹn | Không âm thầm cắt bỏ nội dung; nếu không xử lý hết tài liệu phải thông báo rõ |
| Truy vết | Mỗi lần so sánh có `comparison_id`; ghi lại bước xử lý và lỗi để phục vụ kiểm tra |
| Quản lý file | File tải lên chỉ dùng để xử lý; bản đầu tiên không yêu cầu lưu lịch sử. File tạm phải được xóa sau xử lý |
| Bảo mật | Không ghi toàn bộ nội dung tài liệu vào log. Nếu dùng API bên ngoài, phải thống nhất việc gửi dữ liệu và quản lý khóa API |
| Đo hiệu năng | Ghi nhận thời gian xử lý và kích thước tài liệu; chỉ chốt mục tiêu tốc độ sau khi đo trên bộ tài liệu mẫu và môi trường xác định |

- Reader phải trích xuất toàn bộ nội dung có thể đọc được.
- Phần nằm ngoài các Điều, như lời mở đầu, chữ ký hoặc phụ lục,
  chưa được so sánh trong bản đầu tiên.
- Báo cáo phải nêu rõ giới hạn này; “Không có thay đổi”
  chỉ áp dụng cho các Điều đã xử lý.
- Nếu không xử lý hết nội dung thuộc một Điều, phải báo
  PARTIAL hoặc FAILED, không báo SUCCESS.
- Bản đầu sử dụng request đồng bộ: backend nhận hai file,
  chạy Pipeline và trả báo cáo trong cùng request.
- Không sử dụng job nền hoặc API polling trong bản đầu.
- Giao diện hiển thị đang xử lý, ngăn gửi lặp và không tự
  gửi lại yêu cầu so sánh khi timeout.
- Giới hạn đầu vào, thời gian xử lý và cách trả lỗi được
  quy định trong API contract và cấu hình triển khai.

## 7. Quy định dữ liệu trao đổi giữa các module

Đây là hợp đồng dữ liệu: quy định các module nhận và trả những gì để ghép được với nhau.

| Dữ liệu | Nội dung tối thiểu |
|---|---|
| Reader → Parser | Nội dung trích xuất theo thứ tự và vị trí nguồn: trang PDF hoặc đoạn/bảng Word |
| Parser → Aligner | Danh sách Điều có định danh trong từng phiên bản, số Điều, tiêu đề, nội dung và vị trí nguồn |
| Aligner → Text Diff | `pair_key`, `align_type`, `v1`, `v2`, `needs_review` và lý do nếu ghép chưa chắc chắn |
| Text Diff → Semantic Diff | Cặp Điều đầy đủ và danh sách đoạn thêm/xóa/thay thế; mỗi đoạn ghi trường được so sánh, chữ cũ/mới và vị trí trong trường đó |
| Semantic Diff → Scorer | Danh sách thay đổi; mỗi thay đổi có `change_id`, kết luận đổi nghĩa, giải thích tổng thể, bằng chứng cũ/mới, `aspects` theo mục 1.3 và `needs_review` |
| Pipeline → giao diện | `comparison_id`, `old_document`/`new_document` nhận diện hai file, trạng thái xử lý, danh sách kết quả kèm aspects của từng thay đổi và source_refs của từng Điều, cảnh báo và lỗi |


## 8. Các quyết định cần chốt trước triển khai/nghiệm thu

- Bộ tiêu chí LOW/MEDIUM/HIGH/CRITICAL, kèm ví dụ có nhãn.
- Ví dụ ranh giới giữa 8 nhóm field_group, quy tắc chia/gộp thay đổi
  và chọn category tổng thể từ aspects; danh mục mã theo mục 1.3–1.4.
- Quy tắc đối chiếu dự đoán với ground truth, bao gồm trường hợp
  một thay đổi được diễn đạt hoặc chia nhỏ khác nhau.
- Bộ dữ liệu phát triển và kiểm thử độc lập.
- Giới hạn dung lượng, thời gian xử lý và môi trường đo hiệu năng.
- Thuật toán Semantic Diff; có sử dụng mô hình hoặc API ngoài không.
- Công nghệ frontend.

Các mục chưa chốt không được coi là yêu cầu đã được triển khai
hoặc tiêu chí nghiệm thu đã được xác nhận.




