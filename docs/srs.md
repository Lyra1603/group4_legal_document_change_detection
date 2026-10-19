# Bảng thuật ngữ

| Thuật ngữ | Định nghĩa đề xuất |
| :--- | :--- |
| **Clause** | Một Điều trong một tài liệu, gồm định danh, nhãn Điều, tiêu đề, nội dung và vị trí nguồn |
| **AmendmentItem** | Một yêu cầu sửa đổi, bổ sung hoặc bãi bỏ trong S, kèm vị trí nguồn và vị trí đích trong V1. |
| **V1 / S / V2** | Văn bản ban đầu / văn bản sửa đổi / bản đầy đủ sau sửa đổi. V2 không phải đầu vào hoặc đầu ra bắt buộc. |
| **Reference document** | Tài liệu do người dùng bổ sung để cung cấp nội dung được dẫn chiếu cần cho phân tích. |
| **Meaningful change** | Thay đổi làm đổi nội dung quy định; sửa diễn đạt chỉ được coi là không đổi nghĩa khi giữ nguyên nội dung. |
| **Critical change** | Thay đổi nghĩa đáp ứng tiêu chí CRITICAL trong bộ tiêu chí nhóm thống nhất; thêm/xóa Điều không tự động là critical |

# SYSTEM REQUIREMENTS SPECIFICATION (SRS) & DATA CONTRACT

**Phiên bản tài liệu:** 1.3.0  
**Related Document:** [Business Requirements Document (BRD)](brd.md)

Hệ thống phân tích văn bản ban đầu (V1) và văn bản sửa đổi (S) của VBQPPL Việt Nam. DOCX là định dạng chính; hỗ trợ PDF có lớp chữ, không hỗ trợ PDF scan. Người dùng cung cấp tài liệu tham chiếu khi cần. Không bắt buộc tạo bản đầy đủ sau sửa đổi (V2).

Luồng xử lý:
V1 + S + tài liệu tham chiếu nếu có → Reader → Parser → Trích yêu cầu sửa đổi và liên kết với V1 → Chuẩn bị ngữ cảnh, kiểm tra dẫn chiếu → Text Diff tại phần thay đổi → Semantic Diff → Classifier & Scorer → Báo cáo.

Reader và Parser chạy riêng cho từng tài liệu. Phân tích tập trung vào từng yêu cầu trong S tác động đến V1, định vị đến Điều/Khoản/Điểm hoặc cụm từ được chỉ định. Không ghép toàn bộ V1 và S một–một; không coi phần V1 không được nhắc đến là bị xóa.

Ngữ cảnh gồm thông tin tổng quát của V1 về phạm vi, đối tượng và mục đích điều chỉnh, cùng định nghĩa, điều kiện, ngoại lệ và nội dung dẫn chiếu liên quan. Không bắt buộc phân tích mọi đoạn không thay đổi. Thiếu tài liệu phải chỉ rõ căn cứ cần bổ sung và giữ các kết quả đã xác định.

Pipeline điều phối các module. Backend API nhận yêu cầu từ giao diện,
gọi Pipeline và trả báo cáo để giao diện hiển thị.

Evaluator chạy riêng khi kiểm thử, đối chiếu kết quả với đáp án chuẩn;
không nằm trong luồng so sánh thông thường của người dùng.

Dưới đây là Data Contract (Hợp đồng dữ liệu) quy định bắt buộc định dạng Input/Output giữa các module. Mọi thay đổi đều phải được Nhóm trưởng phê duyệt.

## 1. Data Structures (Cấu trúc dữ liệu dùng chung)

### 1.1 Clause (Một Điều trong văn bản)

```python
class Clause:
    unit_id: str            # Định danh duy nhất trong tài liệu
    id: str                 # Nhãn Điều, ví dụ: "Điều 5"
    title: str              # Không có tiêu đề thì để ""
    content: str            # Giữ nội dung Khoản/Điểm và thứ tự
    source_refs: list[str]  # Vị trí nguồn chứa Điều này
```

Quy định:
- `unit_id` phân biệt các Điều trong từng tài liệu, ví dụ:
  `v1:article_5`, `s:article_1` và `ref_1:article_6`.
- `id` là nhãn trong tài liệu; có thể thay đổi khi đánh lại số Điều.
- `source_refs` tham chiếu các vị trí do Reader ghi nhận:
  trang PDF hoặc đoạn/bảng Word; một Điều có thể trải qua nhiều vị trí.
- Không xóa ngắt dòng phân chia Khoản/Điểm khi chuẩn hóa nội dung.
  
### 1.2 AmendmentItem và AnalysisContext

```python
class EvidenceRef:
    document_id: str            # v1 | s | ref_1 ...
    source_refs: list[str]
    quote: str                 # Trích nguyên văn trong tài liệu này

class ReferenceRequirement:
    reference_id: str
    document_label: str        # Số hiệu/tên được dẫn chiếu nếu xác định được
    target_locator: str        # Điều/Khoản/Điểm/bảng cần đọc
    purpose: str               # Căn cứ trước/sau hoặc ngữ cảnh cần làm rõ
    status: str                # AVAILABLE | MISSING | UNRESOLVED
    evidence: list[EvidenceRef]
    reason: str

class EffectInfo:
    text: str                  # Nội dung hiệu lực/chuyển tiếp được nêu
    applies_to: str            # Phạm vi áp dụng theo bằng chứng
    evidence: list[EvidenceRef]
    needs_review: bool
    review_reason: str

class AnalysisContext:
    general_context: str       # Phạm vi, đối tượng, mục đích của V1
    evidence: list[EvidenceRef] # Nội dung tổng quát và ngữ cảnh liên quan
    references: list[ReferenceRequirement]

class AmendmentItem:
    amendment_id: str
    operation: str             # AMEND | ADD | REPEAL | UNRESOLVED
    instruction: EvidenceRef  # Chỉ dẫn nguyên văn trong S
    target_document: str
    target_locator: str       # Điều/Khoản/Điểm/cụm từ bị tác động
    target_unit_ids: list[str] # Điều trong V1; có thể rỗng nếu chưa định vị
    applicability: str        # APPLIES | OTHER_DOCUMENT | UNRESOLVED
    before_text: str | None
    after_text: str | None     # Chỉ nội dung cục bộ, không phải V2 đầy đủ
    after_basis: str           # QUOTED | DERIVED | ABSENT | UNRESOLVED
    evidence: list[EvidenceRef]
    effect_info: list[EffectInfo]
    context: AnalysisContext
    needs_review: bool
    review_reason: str
```

Quy định:
- Mỗi yêu cầu độc lập có `amendment_id`; một Điều V1 có thể được nhiều yêu cầu tham chiếu. Không áp dụng quy tắc mỗi Điều xuất hiện đúng một lần.
- Phân biệt vị trí chỉ dẫn trong S và vị trí bị tác động trong V1. Với bổ sung, định vị Điều chứa hoặc vị trí chèn; không yêu cầu nội dung mới phải tồn tại trong V1.
- `before_text` lấy từ V1; `after_text` là nội dung thay thế trích từ S hoặc nội dung cục bộ suy ra từ chỉ dẫn rõ ràng. Nội dung suy ra dùng `DERIVED`, phải giữ bằng chứng của V1 và S, không coi là trích nguyên văn hoặc bản hợp nhất chính thức.
- Bổ sung không có nội dung cũ: `before_text = None`. Bãi bỏ không có nội dung thay thế: `after_text = None`, `after_basis = ABSENT`; vẫn giữ chỉ dẫn bãi bỏ trong S.
- Không xác định được nội dung khác với không tồn tại nội dung. Trường hợp chưa rõ dùng `UNRESOLVED`, cảnh báo và không tạo kết luận thêm/bãi bỏ do thiếu đoạn nguồn.
- Yêu cầu sửa văn bản khác dùng `OTHER_DOCUMENT`, được liệt kê là ngoài đối tượng V1 và không đưa vào phân tích thay đổi của V1. Không rõ đối tượng dùng `UNRESOLVED` và yêu cầu kiểm tra.
- `effect_info` giữ thông tin hiệu lực/chuyển tiếp liên quan trong S. Không tự áp ngày hiệu lực chung nếu có ngoại lệ hoặc chưa rõ phạm vi; chưa xác định phải có cảnh báo. Không thấy thông tin thì danh sách rỗng kèm lý do trong `review_reason`, `needs_review = True`. Việc thiếu thông tin này không tự làm mất kết quả xác định thay đổi nội dung đã có căn cứ.
- `references` chỉ ra nội dung dẫn chiếu cần thiết. Đổi dẫn chiếu A → B cần căn cứ cả A và B để phân tích tác động trước–sau nếu chưa có trong đầu vào. File có mặt nhưng chưa tìm được đúng nội dung vẫn là `UNRESOLVED`.
- Ngữ cảnh tổng quát không thay thế việc đọc đoạn gốc, định nghĩa, điều kiện và ngoại lệ liên quan. Kết luận dựa trên tài liệu tham chiếu phải có `EvidenceRef` tương ứng.

### 1.3 SemanticDiffResult (Kết quả phân tích ngữ nghĩa)

```python
class ChangeAspect:
    aspect_id: str             # Duy nhất trong SemanticChange
    field_group: str | None    # Một trong 8 nhóm bên dưới; None nếu chưa rõ
    old_value: str | None      # Nội dung ngữ nghĩa trước thay đổi
    new_value: str | None      # Nội dung ngữ nghĩa sau thay đổi
    interpretation: str       # Giải thích sự chuyển đổi trước → sau
    evidence: list[EvidenceRef] # Nguồn của các trích dẫn và nhận định
    old_quote: str | None      # Bằng chứng nguyên văn phía cũ nếu có
    new_quote: str | None      # Bằng chứng nguyên văn phía mới nếu có
    needs_review: bool
    review_reason: str

class SemanticChange:
    change_id: str             # Định danh thay đổi trong lần so sánh
    is_meaningful_change: bool | None
    diff_details: str         # Giải thích tổng thể của thay đổi
    aspects: list[ChangeAspect]
    evidence: list[EvidenceRef] # Nguồn của các trích dẫn và nhận định
    old_quote: str | None      # None khi không có phía cũ
    new_quote: str | None      # None khi không có phía mới
    needs_review: bool
    review_reason: str

class SemanticDiffResult:
    amendment_id: str
    changes: list[SemanticChange]
    needs_review: bool
    review_reason: str
```

Quy định:
- Một AmendmentItem có thể có nhiều SemanticChange. Mỗi SemanticChange
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
- Bằng chứng phải lấy từ V1, S hoặc tài liệu tham chiếu đã cung cấp; mỗi đoạn trích có EvidenceRef xác định tài liệu và vị trí.
- Cảnh báo từ bước liên kết phải được giữ trong kết quả.
- changes rỗng chỉ biểu thị không có nhận định ngữ nghĩa được tạo; yêu cầu sửa đổi vẫn phải hiển thị. Lỗi hoặc thiếu căn cứ phải ghi rõ, không suy ra không có thay đổi.

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
yêu cầu sửa đổi được phân tích và ngữ cảnh cần thiết; không tự xác minh hiệu lực thực tế của văn bản.

Quy định về ChangeAspect:
- Mỗi khía cạnh có một field_group; interpretation chỉ rõ thành phần
  nào trong nhóm đã đổi và ý nghĩa trước → sau, không chỉ định nghĩa tên nhóm.
  Chỉ ghi các khía cạnh thực sự thay đổi hoặc đang cần xác minh;
  thông tin giữ nguyên được dùng làm ngữ cảnh trong diff_details.
- old_value/new_value là mô tả nội dung tương ứng, giữ đủ đơn vị,
  điều kiện và ngữ cảnh cần thiết. old_quote/new_quote phải là đoạn
  trích nguyên văn trong tài liệu nguồn được chỉ rõ bằng EvidenceRef. Nội dung sau sửa đổi được suy ra chỉ ghi ở value/interpretation, không gán thành quote nguyên văn.
- Với nội dung sau sửa đổi được suy ra, new_quote có thể là None; evidence phải giữ chỉ dẫn trong S và đoạn V1 làm căn cứ. Điều này không tự tạo cảnh báo nếu phép suy ra đã có đủ căn cứ.
- Trong các trường hợp khác, None ở value/quote biểu thị không có nội dung tương ứng hoặc chưa
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
  mô tả thay đổi dẫn chiếu, ghi ReferenceRequirement còn thiếu và giới hạn suy luận; cho phép bổ sung tài liệu để phân tích lại, không tự kết luận tác động rộng hơn.

Ví dụ giả định: S thay thế quy định trong V1 bằng câu mới được trích đầy đủ: “Doanh nghiệp phải nộp báo cáo trong 30 ngày.” →
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
    document_id: str      # v1 | s | ref_1 ...
    role: str             # BASE | AMENDMENT | REFERENCE
    filename: str
    file_type: str        # DOCX | PDF_TEXT
    blocks: list[SourceBlock]
```

Quy định:
- blocks giữ thứ tự nội dung trong tài liệu, bao gồm nội dung bảng.
- Parser dùng blocks để tách Điều và lưu source_refs.
- Không đọc được nội dung thì báo lỗi, không trả văn bản rỗng hợp lệ.
- source_ref phải duy nhất trong từng tài liệu.
- Khi truy nguồn, dùng đồng thời document_id và source_ref.
- Mỗi source_ref chỉ tra trong ExtractedDocument có document_id tương ứng; không suy ra vai trò hoặc số hiệu pháp lý từ tên file.

### 1.6 TextDiffResult (Đầu ra Text Diff)

```python
class TextChange:
    type: str            # INSERT | DELETE | REPLACE
    old_text: str
    new_text: str
    old_start: int
    old_end: int
    new_start: int
    new_end: int

class TextDiffResult:
    amendment_id: str
    changes: list[TextChange]
```

Quy định:
- Chỉ đối chiếu `before_text` và `after_text` cục bộ của AmendmentItem khi đã xác định được hai phía hoặc xác định rõ một phía không tồn tại do bổ sung/bãi bỏ.
- Vị trí theo ký tự, từ 0, khoảng [start, end), khớp hai chuỗi cục bộ trong báo cáo; không phải tọa độ trực tiếp trong file gốc.
- INSERT dùng old_text = ""; DELETE dùng new_text = "". Phía không tồn tại được quy về chuỗi rỗng để tính vị trí.
- Chưa xác định được một phía: không chạy Text Diff, trả None ở báo cáo kèm cảnh báo. Không dùng chuỗi rỗng thay cho nội dung chưa biết.
- Nội dung giống nhau có changes = []; chỉ dẫn sửa đổi và phân tích hiệu lực vẫn được giữ. Không diff toàn bộ V1 với S.

### 1.7 ComparisonReport (Báo cáo tổng hợp)

```python
class AmendmentResult:
    amendment: AmendmentItem
    text_diff: TextDiffResult | None
    semantic_diff: SemanticDiffResult | None
    scoring: list[ScoringResult] | None

class ProcessingIssue:
    stage: str
    code: str
    message: str
    amendment_id: str | None

class DocumentIdentity:
    document_id: str
    role: str                 # BASE | AMENDMENT | REFERENCE
    filename: str             # Không chứa đường dẫn lưu nội bộ

class ComparisonReport:
    comparison_id: str
    base_document: DocumentIdentity
    amendment_document: DocumentIdentity
    reference_documents: list[DocumentIdentity]
    status: str               # SUCCESS | PARTIAL | FAILED
    results: list[AmendmentResult]
    warnings: list[ProcessingIssue]
    errors: list[ProcessingIssue]
```

Quy định:
- BASE có document_id = "v1"; AMENDMENT có document_id = "s"; mỗi REFERENCE có định danh riêng. Metadata được giữ kể cả báo cáo PARTIAL/FAILED. Tên file không xác nhận tên pháp lý hoặc hiệu lực; UI luôn hiển thị vai trò dù các file trùng tên.
- SUCCESS: hoàn tất các bước trong phạm vi yêu cầu; vẫn có thể có nhận định cần kiểm tra. PARTIAL: một phần chưa xử lý hoặc chưa thể phân tích vì thiếu căn cứ; phải chỉ rõ phần bị ảnh hưởng. FAILED: không tạo được kết quả sử dụng được.
- Thiếu tài liệu tham chiếu cần thiết cho phân tích tác động: PARTIAL, giữ thay đổi trực tiếp đã xác định và liệt kê nhu cầu bổ sung. Không chặn các kết quả khác.
- Bước chưa thực hiện hoặc thất bại dùng None kèm lỗi/cảnh báo và lý do; không thay bằng danh sách rỗng. scoring = [] chỉ khi hoàn tất nhưng không có SemanticChange để chấm.
- Mỗi ScoringResult tham chiếu change_id trong SemanticDiffResult của cùng AmendmentResult. Cảnh báo phải giữ đến báo cáo và kết quả chấm mức độ.
- Nếu is_meaningful_change = None: significance và is_critical là None, needs_review = True; không tự chấm LOW.
- Chỉ thông báo “Không tìm thấy yêu cầu sửa đổi đối với V1 trong S đã cung cấp” khi status = SUCCESS, đã xử lý đầy đủ S, không có yêu cầu APPLIES và không còn đối tượng/phần nội dung chưa xác định. Text Diff rỗng không đủ để đưa ra kết luận này.

## 2. Functional Requirements

| Mã | Chức năng | Đầu vào → đầu ra | Tiêu chí nghiệm thu tối thiểu |
|---|---|---|---|
| FR-01 | Reader | Một file → ExtractedDocument | Đọc DOCX/PDF text, giữ thứ tự và vị trí nguồn; không đọc được phải báo lỗi |
| FR-02 | Parser | Một ExtractedDocument → list[Clause] và blocks được giữ | Tách Điều, giữ Khoản/Điểm và nguồn; giữ bảng/ngữ cảnh ngoài Điều để truy xuất khi cần |
| FR-03 | Trích yêu cầu và liên kết | V1, S đã phân tích cấu trúc → list[AmendmentItem] | Trích sửa/bổ sung/bãi bỏ; định vị văn bản và Điều/Khoản/Điểm; phân biệt yêu cầu sửa văn bản khác; cảnh báo đích chưa rõ |
| FR-04 | Text Diff | AmendmentItem đủ nội dung cục bộ → TextDiffResult | Chỉ rõ thêm/xóa/thay thế; tọa độ khớp before_text/after_text; không diff toàn bộ V1 với S |
| FR-05 | Semantic Diff | AmendmentItem có context và TextDiffResult nếu có → SemanticDiffResult | Phân tích thay đổi với ngữ cảnh và bằng chứng; trả aspects theo 8 nhóm; thiếu căn cứ phải cảnh báo |
| FR-06 | Classifier & Scorer | AmendmentItem và SemanticDiffResult → list[ScoringResult] | Chọn nhãn và mức độ theo tiêu chí; is_critical nhất quán với significance; có lý do |
| FR-07 | Evaluator | Báo cáo dự đoán và đáp án chuẩn → chỉ số đánh giá | Tính cả thay đổi bỏ sót và dự đoán sai; không bỏ qua do liên kết sai hoặc thiếu kết quả |
| FR-08 | Upload và xem kết quả | V1, S và tài liệu tham chiếu nếu có → báo cáo | Chọn đúng vai trò, hiển thị thay đổi, nguồn, hiệu lực, mức độ, tài liệu thiếu; cho phép bổ sung và phân tích lại |
| FR-09 | Ngữ cảnh và dẫn chiếu | V1, yêu cầu sửa đổi, các tài liệu đã cung cấp → AnalysisContext | Giữ thông tin tổng quát và ngữ cảnh liên quan; tìm đúng nội dung dẫn chiếu, báo thiếu cụ thể; không tự thu thập tài liệu |
| FR-10 | Hiệu lực và chuyển tiếp | S và yêu cầu sửa đổi → list[EffectInfo] | Giữ nội dung, phạm vi áp dụng và bằng chứng; ngoại lệ/chưa rõ phải cảnh báo; không tự xác minh hiệu lực thực tế |

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
- Kiểm tra riêng độ đúng của liên kết đích, trích hiệu lực và yêu cầu bổ sung tài liệu. Mẫu thiếu căn cứ được đánh giá theo khả năng nhận diện giới hạn; không ép gán tác động chưa có bằng chứng. Nhãn chuẩn phải phản ánh đúng bộ tài liệu cung cấp cho mẫu, không dùng tài liệu ẩn để yêu cầu hệ thống kết luận.

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
| Lỗi | V1 hoặc S không tìm được Điều: báo lỗi cấu trúc. Tài liệu tham chiếu có thể cung cấp bảng/đoạn qua blocks; không loại bỏ chỉ vì thiếu nhãn Điều |

Ví dụ nội dung chữ trong các blocks: 
```
Điều 1. Phạm vi điều chỉnh
Văn bản này quy định về...
Điều 2. Đối tượng áp dụng
Áp dụng đối với...
```

### 3.3 Module trích yêu cầu sửa đổi và liên kết

| Nội dung | Quy định |
|---|---|
| Đầu vào | V1 và S sau Reader/Parser |
| Xử lý | Trích từng yêu cầu sửa/bổ sung/bãi bỏ; nhận diện văn bản đích, Điều/Khoản/Điểm/cụm từ và liên kết với V1 |
| Đầu ra | list[AmendmentItem] theo mục 1.2 |
| Yêu cầu | Một Điều có thể có nhiều yêu cầu; phân biệt số Điều trong S với vị trí đích; không coi nội dung không được nhắc đến là bãi bỏ |
| Chưa rõ | Giữ chỉ dẫn nguồn, cảnh báo; không tự áp sửa đổi khi thiếu căn cứ |

Bước chuẩn bị ngữ cảnh lấy thông tin tổng quát và nội dung liên quan từ V1, kiểm tra tài liệu dẫn chiếu người dùng cung cấp, tạo AnalysisContext. Nội dung hiệu lực/chuyển tiếp trong S được gắn qua EffectInfo; giữ ngoại lệ và phần chưa xác định. Các trách nhiệm này có thể được tách module khi triển khai nhưng phải giữ hợp đồng dữ liệu mục 1.2.

### 3.4 Module Text Diff — tìm những đoạn chữ thay đổi: Sau khi xác định nội dung trước/sau cục bộ, Text Diff chỉ ra chữ nào được thêm, xóa hoặc thay thế.

| Nội dung | Quy định |
|---|---|
| Đầu vào | Một `AmendmentItem` đủ căn cứ đối chiếu |
| Xử lý | So sánh before_text và after_text cục bộ |
| Đầu ra | TextDiffResult theo mục 1.6 |
| Loại thay đổi | `INSERT`: thêm; `DELETE`: xóa; `REPLACE`: thay thế |
| Điều thêm/xóa toàn bộ | Ghi nhận toàn bộ nội dung phía tương ứng |

Ví dụ:
- Cũ: “Phải nộp trong 30 ngày.”
- Mới: “Phải nộp trong 15 ngày.”

### 3.5 Module Semantic Diff — xác định thay đổi có làm đổi nghĩa hay không.

| Nội dung | Quy định |
|---|---|
| Đầu vào | Một `AmendmentItem`, AnalysisContext và kết quả Text Diff nếu có; giữ ngữ cảnh liên quan và bằng chứng |
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
| Đầu vào | `AmendmentItem` và kết quả Semantic Diff |
| Xử lý | Xác định loại thay đổi và mức độ theo bộ tiêu chí thống nhất của nhóm |
| Đầu ra | list[ScoringResult], một kết quả cho mỗi SemanticChange|
| Yêu cầu | Mức độ phải có lý do dựa trên nội dung và bằng chứng của thay đổi |

Nhãn tổng thể category dùng 8 mã nhóm tại mục 1.3 hoặc WORDING_ONLY theo mục 1.4; sửa/bổ sung/bãi bỏ được thể hiện ở operation, còn nội dung thay đổi được phân tích trong aspects.

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
| Đầu vào | Kết quả pipeline và bộ đáp án chuẩn của cùng các cặp V1–S và bộ tài liệu tham chiếu tương ứng |
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
- Thay đổi có trong đáp án nhưng hệ thống bỏ sót phải được tính là lỗi; không bỏ qua do thiếu kết quả hoặc liên kết sai.
- Kết quả needs_review chưa được giải quyết không được tính là phát hiện đúng; phải báo thêm số lượng cần kiểm tra.
- Tập kiểm thử không được dùng để điều chỉnh thuật toán.
- Chỉ số không tính được do mẫu số bằng 0 trả null kèm lý do; không báo đạt mục tiêu.

Ví dụ: đáp án có 10 thay đổi trọng yếu, hệ thống tìm đúng 8 → Critical Change Recall = 80%.

## 4. Yêu cầu tải tài liệu và xem kết quả

| Chức năng | Yêu cầu |
|---|---|
| Chọn đầu vào | Người dùng chọn hai file `.docx` hoặc PDF có lớp chữ, xác định rõ **văn bản gốc V1 / văn bản sửa đổi S**, có thể thêm tài liệu tham chiếu |
| Bắt đầu so sánh | Người dùng nhấn “So sánh”; hệ thống kiểm tra file rồi chạy pipeline |
| Trạng thái xử lý | Hiển thị đang xử lý, hoàn thành, hoàn thành một phần hoặc thất bại; phân biệt hoàn thành với kết quả còn cần kiểm tra |
| Xem kết quả | Hiển thị từng yêu cầu sửa đổi, vị trí đích và nội dung trước/sau cục bộ; đánh dấu nội dung sau được suy ra |
| Nhận diện tài liệu | Hiển thị tên file từ base_document/amendment_document/reference_documents và vai trò V1 / S / tài liệu tham chiếu trong báo cáo, kể cả khi tên file giống nhau hoặc báo cáo chỉ hoàn tất một phần |
| Xem phân tích | Mỗi SemanticChange có kết luận đổi nghĩa, giải thích tổng thể, category, mức độ và lý do; hiển thị từng ChangeAspect gồm tên nhóm tiếng Việt, nội dung cũ/mới, interpretation, bằng chứng và cảnh báo. Phân biệt nhãn tổng thể với nhóm của khía cạnh; không chỉ hiển thị category rồi ẩn các khía cạnh còn lại |
| Vị trí nguồn | Hiển thị EvidenceRef trong đúng V1, S hoặc tài liệu tham chiếu: trang PDF hoặc đoạn/bảng DOCX; luôn giữ nguồn chỉ dẫn trong S kể cả bãi bỏ |
| Cần kiểm tra | Hiển thị rõ các kết quả `needs_review = true`; mức độ chưa xác định ghi “Chưa xác định” |
| Không có thay đổi | Chỉ thông báo không tìm thấy yêu cầu sửa đổi đối với V1 theo mục 1.7; nếu chỉ sửa văn phong thì vẫn hiển thị phần sửa |
| Tài liệu bổ sung | Hiển thị văn bản và vị trí còn thiếu theo ReferenceRequirement; cho phép tải bổ sung và gửi lại để phân tích; không bổ sung thì giữ báo cáo cùng giới hạn |
| Hiệu lực/chuyển tiếp | Hiển thị nội dung, phạm vi áp dụng và bằng chứng trong EffectInfo; phần chưa xác định phải có cảnh báo |

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
- Người tham gia thực hiện các nhiệm vụ: xác định đúng V1/S/tài liệu tham chiếu;
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
| Parser không tìm được Điều trong V1 hoặc S | Báo lỗi cấu trúc; không trả kết quả “không có thay đổi” |
| Đích sửa đổi mơ hồ hoặc chỉ dẫn tách/gộp chưa xác định đủ | Cảnh báo cần kiểm tra; không coi phần chưa liên kết chắc chắn là bổ sung/bãi bỏ đã xác nhận |
| Phân tích nghĩa hoặc chấm mức độ chưa đủ căn cứ | Đánh dấu `needs_review = true`; kết luận chưa xác định để `null` |
| Một bước xử lý thất bại | Báo bước gặp lỗi; nếu hiển thị kết quả một phần, phải ghi rõ báo cáo chưa hoàn tất |
| Thiếu hoặc sai nội dung tham chiếu | Giữ kết quả đã xác định; báo PARTIAL và chỉ rõ tài liệu/nội dung cần bổ sung; không tự suy luận tác động |
| S chứa yêu cầu sửa văn bản khác | Ghi OTHER_DOCUMENT, không áp dụng vào V1 |
| Chưa rõ hiệu lực hoặc ngoại lệ chuyển tiếp | Giữ trích dẫn, cảnh báo phạm vi chưa xác định; không tự gán một ngày cho mọi thay đổi |
Yêu cầu chung: thông báo lỗi phải dễ hiểu và có hướng xử lý; không hiển thị lỗi kỹ thuật nội bộ cho người dùng.

## 6. Yêu cầu vận hành

| Nội dung | Yêu cầu |
|---|---|
| Cấu hình | Giới hạn dung lượng file và thời gian xử lý phải cấu hình được; giá trị cụ thể cần nhóm thống nhất trước nghiệm thu |
| Tính toàn vẹn | Không âm thầm cắt bỏ nội dung; nếu không xử lý hết tài liệu phải thông báo rõ |
| Truy vết | Mỗi lần so sánh có `comparison_id`; ghi lại bước xử lý và lỗi để phục vụ kiểm tra |
| Quản lý file | File tải lên chỉ dùng để xử lý; không yêu cầu lưu lịch sử hoặc kho pháp luật dùng chung. File tạm được xóa sau mỗi request; giao diện giữ lựa chọn file để người dùng gửi lại kèm tài liệu bổ sung |
| Bảo mật | Không ghi toàn bộ nội dung tài liệu vào log. Nếu dùng API bên ngoài, phải thống nhất việc gửi dữ liệu và quản lý khóa API |
| Đo hiệu năng | Ghi nhận thời gian xử lý và kích thước tài liệu; chỉ chốt mục tiêu tốc độ sau khi đo trên bộ tài liệu mẫu và môi trường xác định |

- Reader phải trích xuất toàn bộ nội dung có thể đọc được, giữ bảng và vị trí nguồn. Tài liệu PDF được đọc trực tiếp hoặc chuyển đổi trong Reader phải giữ khả năng truy nguồn; lựa chọn công cụ không làm thay đổi hợp đồng đầu ra.
- Không so sánh toàn diện phần mở đầu, chữ ký hoặc phụ lục; nội dung đọc được ở các phần này có thể dùng làm ngữ cảnh hoặc bằng chứng, bao gồm bảng được dẫn chiếu.
- Không xử lý hết yêu cầu trong S hoặc phần nguồn cần thiết phải báo PARTIAL/FAILED, không báo hoàn tất toàn bộ.
- Bản đầu sử dụng request đồng bộ: backend nhận V1, S và tài liệu tham chiếu nếu có, chạy Pipeline và trả báo cáo trong cùng request.
- Khi bổ sung tài liệu, giao diện gửi lại các file đầu vào kèm tài liệu mới trong một request đồng bộ để phân tích lại; không yêu cầu lưu trạng thái xử lý trên server.
- Không sử dụng job nền hoặc API polling trong bản đầu.
- Giao diện hiển thị đang xử lý, ngăn gửi lặp và không tự gửi lại khi timeout.
- Giới hạn số lượng/dung lượng file, thời gian xử lý và cách trả lỗi được quy định trong API contract và cấu hình triển khai.

## 7. Quy định dữ liệu trao đổi giữa các module

Đây là hợp đồng dữ liệu: quy định các module nhận và trả những gì để ghép được với nhau.

| Dữ liệu | Nội dung tối thiểu |
|---|---|
| Reader → Parser | Nội dung trích xuất theo thứ tự, document_id, vai trò và vị trí nguồn; giữ bảng và blocks |
| Parser → Trích yêu cầu/liên kết | Điều có định danh, cấu trúc Khoản/Điểm được giữ, nguồn của V1 và S |
| Trích yêu cầu/liên kết → Ngữ cảnh | AmendmentItem có chỉ dẫn, vị trí đích, nội dung cục bộ, bằng chứng và cảnh báo |
| Ngữ cảnh → Text Diff/Semantic Diff | AmendmentItem kèm AnalysisContext, ReferenceRequirement và EffectInfo; Text Diff chỉ chạy khi đủ nội dung cục bộ |
| Semantic Diff → Scorer | change_id, kết luận đổi nghĩa, diff_details, aspects, evidence và cảnh báo theo mục 1.3 |
| Pipeline → giao diện | ComparisonReport theo mục 1.7: định danh tài liệu, kết quả từng yêu cầu, hiệu lực, tài liệu thiếu, nguồn, trạng thái và lỗi |

## 8. Các quyết định cần chú ý khi triển khai/nghiệm thu

- Bộ tiêu chí LOW/MEDIUM/HIGH/CRITICAL, kèm ví dụ có nhãn.
- Ví dụ ranh giới giữa 8 nhóm field_group, quy tắc chia/gộp thay đổi
  và chọn category tổng thể từ aspects; danh mục mã theo mục 1.3–1.4.
- Quy tắc đối chiếu dự đoán với ground truth, bao gồm trường hợp
  một thay đổi được diễn đạt hoặc chia nhỏ khác nhau.
- Bộ dữ liệu V1–S phát triển và kiểm thử độc lập, kèm nhãn vị trí đích, bằng chứng, hiệu lực và tình trạng đủ/thiếu tài liệu tham chiếu.
- Giới hạn dung lượng, thời gian xử lý và môi trường đo hiệu năng.
- Thuật toán Semantic Diff; có sử dụng mô hình hoặc API ngoài không.
- Công nghệ frontend.





