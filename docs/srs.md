# Bảng thuật ngữ

**Phạm vi thiết kế và nền chạy:** SRS mô tả mục tiêu của dự án. Đối chiếu code hiện tại và phần sau merge tại [common-baseline.md](common-baseline.md). Nền chung dùng `backend.demo:app`, DOCX, chưa bật LightRAG/model; thêm/bãi bỏ và nhiều đích chưa được demo tự áp dụng. Không đổi schema trong đợt đồng bộ 12/11. Fixture 30 → 15 ngày giữ mức tác động null và report PARTIAL, không là gold ngữ nghĩa đã duyệt.

| Thuật ngữ | Định nghĩa đề xuất |
| :--- | :--- |
| **Clause** | Một Điều trong một tài liệu, gồm định danh, nhãn Điều, tiêu đề, nội dung và vị trí nguồn |
| **AmendmentItem** | Một yêu cầu sửa đổi, bổ sung hoặc bãi bỏ trong S, kèm vị trí nguồn và vị trí đích trong V1. |
| **V1 / S / V2** | Văn bản ban đầu / văn bản sửa đổi / bản đầy đủ sau sửa đổi. V2 không phải đầu vào hoặc đầu ra bắt buộc. |
| **Reference document** | Nguồn ngữ cảnh truy xuất từ kho dân sự hoặc do người dùng bổ sung khi cần. |
| **Quan hệ văn bản** | Cạnh có hướng A → B khi A nhắc B, giữ nguồn nhắc và căn cứ phân giải đích; nhắc tên không tự đồng nghĩa sửa đổi. |
| **Quan hệ ngữ nghĩa** | Quan hệ dựa trên nội dung/quy định có nguồn của A/B dù không nhắc tên nhau; khác với Semantic Diff trước–sau và chưa tự chứng minh tác động. |
| **Meaningful change** | Thay đổi làm đổi nội dung quy định; sửa diễn đạt chỉ được coi là không đổi nghĩa khi giữ nguyên nội dung. |
| **Critical change** | Thay đổi nghĩa đáp ứng tiêu chí CRITICAL trong bộ tiêu chí nhóm thống nhất; thêm/xóa Điều không tự động là critical |

# SYSTEM REQUIREMENTS SPECIFICATION (SRS) & DATA CONTRACT

**Phiên bản tài liệu:** 1.6.0
**Căn cứ nghiệp vụ:** BRD 1.4.0
**Related Document:** [Business Requirements Document (BRD)](brd.md)

Người dùng nộp một văn bản sửa đổi S, có thể kèm bối cảnh. Hệ thống tìm các văn bản bị sửa và phiên bản trước sửa đổi V1 trong kho VBQPPL dân sự tiếng Việt do nhóm chuẩn bị. DOCX và PDF có lớp chữ là định dạng hỗ trợ. Hệ thống dựng nội dung sau sửa đổi ở cấp quy định, phân tích thay đổi trực tiếp và tìm tác động có thể có lên quy định trong các văn bản khác.

**Phân biệt mục tiêu và code:** luồng chỉ S và báo cáo cấp S dưới đây là đặc tả cần triển khai. Nền sau PR #7 (`95e1d79`) vẫn nhận V1 + S qua `/api/compare`, demo tắt LightRAG/model; schema mục 1.1–1.7 không thay đổi trong đợt tài liệu này. Xem [nền chung](common-baseline.md).

Luồng xử lý mục tiêu:
S + bối cảnh tùy chọn → Reader/Parser → Trích yêu cầu từ S → Agent truy xuất văn bản, phiên bản và quy định đích trong kho dân sự → Dựng nội dung trước/sau và chuẩn bị ngữ cảnh → Text Diff → Semantic Diff → Classifier & Scorer → Tìm và kiểm chứng tác động gián tiếp → Báo cáo cấp S. LightRAG hỗ trợ truy xuất. LLM và bộ quy tắc dân sự hỗ trợ diễn giải và chấm mức độ.

Reader và Parser xử lý từng nguồn. Hệ thống tách các yêu cầu độc lập từ S, giữ vị trí chỉ dẫn và định vị từng đích đến Điều/Khoản/Điểm hoặc cụm từ. Phạm vi đầu là kho dân sự nhóm chuẩn bị; ngoài kho báo giới hạn/yêu cầu bổ sung, chưa tự tìm Internet. Chọn phiên bản theo nguồn và căn cứ thời điểm, không tự chọn bản mới nhất; nhiều ứng viên hoặc thiếu căn cứ thì giữ lý do cần rà soát. Mỗi đích đã xác định được đưa vào luồng đối chiếu theo phiên bản tương ứng.

Ngữ cảnh gồm thông tin tổng quát của V1 về phạm vi, đối tượng và mục đích điều chỉnh, cùng định nghĩa, điều kiện, ngoại lệ và nội dung dẫn chiếu liên quan. Không bắt buộc phân tích mọi đoạn không thay đổi. Thiếu tài liệu phải chỉ rõ căn cứ cần bổ sung và giữ các kết quả đã xác định.

Pipeline điều phối các module. Backend API nhận yêu cầu từ giao diện,
gọi Pipeline và trả báo cáo để giao diện hiển thị.

Không triển khai Evaluator như một module/đầu việc độc lập. Kiểm thử chủ yếu do owner bên cung cấp và bên nhận tại từng điểm nối cùng thực hiện; Dũng điều phối tích hợp/Pipeline/API, Đức Anh điều phối kế hoạch đánh giá. Phép đo với đáp án chuẩn được thực hiện bằng kiểm thử/script trong `test/` khi cần, không mất trách nhiệm kiểm tra nghiệp vụ.

Các kiểu dữ liệu mục 1.1–1.7 mô tả hợp đồng backend hiện có cho một đích. Mục 1.8 đặc tả hợp đồng cấp S cần triển khai. Các bộ kiểm tra của hợp đồng hiện có tiếp tục áp dụng ở cấp từng đích. Kiểm tra quan hệ giữa nhiều đích, văn bản và bằng chứng tác động thuộc hợp đồng cấp S.

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
- `source_refs` tham chiếu nguồn được Parser/adapter giữ lại. Implementation hiện dùng `block:N`; offset theo ký tự Python, khoảng `[start,end)`. Với PDF chuyển sang DOCX, nguồn hiện chỉ xác nhận trên DOCX chuyển đổi; không suy số trang PDF từ số block. Một Điều có thể trải qua nhiều vị trí.
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
    after_text: str | None     # Toàn văn đơn vị đối chiếu sau áp dụng chỉ dẫn
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
- Phiên 1 giữ toàn văn cùng một đơn vị đối chiếu ở cả hai trạng thái. Với sửa nội dung của Điểm, Khoản hoặc Điều hiện có, đơn vị đối chiếu là toàn văn đơn vị đó. Khi thêm hoặc bãi bỏ cả một đơn vị, dùng đơn vị chứa nhỏ nhất còn tồn tại ở hai phía, ví dụ toàn Điều khi thêm hoặc bãi bỏ một Khoản. Vị trí đích vẫn ghi chính xác Điểm, Khoản hoặc Điều mà S chỉ ra. Nếu chỉ dẫn có nhiều đích, giữ đủ đích và căn cứ cho từng đích. Nội dung dựng từ V1 và chỉ dẫn S dùng `DERIVED`. Chỉ dùng `QUOTED` khi toàn bộ đoạn sau là nguyên văn trong S.
- Schema vẫn dùng giá trị `null` và `ABSENT` để biểu diễn phía đã xác định là không tồn tại. Với ca ADD/REPEAL có đơn vị chứa đối chiếu được, phiên 1 dùng hai bản toàn văn của đơn vị chứa. Khi chưa xác định được đơn vị đối chiếu, ghi giới hạn thay vì tạo chuỗi giả.
- Không xác định được nội dung khác với không tồn tại nội dung. Trường hợp chưa rõ dùng `UNRESOLVED`, cảnh báo và không tạo kết luận thêm/bãi bỏ do thiếu đoạn nguồn.
- `OTHER_DOCUMENT` chỉ mô tả quan hệ với V1 của một báo cáo đối chiếu cục bộ. Pipeline cấp S phải định tuyến yêu cầu đến báo cáo của đích tương ứng hoặc giữ ở danh sách chưa xử lý cùng lý do. Không rõ đối tượng dùng trạng thái `UNRESOLVED` trong hợp đồng cục bộ.
- `effect_info` giữ thông tin hiệu lực/chuyển tiếp liên quan trong S. Không tự áp ngày hiệu lực chung nếu có ngoại lệ hoặc chưa rõ phạm vi; chưa xác định phải có cảnh báo. Không thấy thông tin thì danh sách rỗng kèm lý do trong `review_reason`, `needs_review = True`. Việc thiếu thông tin này không tự làm mất kết quả xác định thay đổi nội dung đã có căn cứ.
- `references` chỉ ra nội dung dẫn chiếu cần thiết. Đổi dẫn chiếu A → B cần căn cứ cả A và B để phân tích tác động trước–sau nếu chưa có trong đầu vào. File có mặt nhưng chưa tìm được đúng nội dung vẫn là `UNRESOLVED`.
- Ngữ cảnh tổng quát không thay thế việc đọc đoạn gốc, định nghĩa, điều kiện và ngoại lệ liên quan. Kết luận dựa trên tài liệu tham chiếu phải có `EvidenceRef` tương ứng.

### 1.3 SemanticDiffResult (Hợp đồng kết quả phân tích ngữ nghĩa)

Phân công Semantic Diff theo [LK-01](decision.md#lk-01--phân-công-theo-modulechức-năng). Tám field_group dưới đây là danh mục dùng chung của ChangeAspect và category trong ScoringResult theo report_validation.py; không yêu cầu danh mục phân loại bốn nhóm riêng.

```python
class ChangeAspect:
    aspect_id: str             # Duy nhất trong SemanticChange
    field_group: str | None    # Một trong 8 nhóm dùng chung bên dưới; None nếu chưa rõ
    old_value: str | None      # Nội dung ngữ nghĩa trước thay đổi
    new_value: str | None      # Nội dung ngữ nghĩa sau thay đổi
    interpretation: str       # Giải thích sự chuyển đổi trước → sau
    evidence: list[EvidenceRef] # Nguồn của các trích dẫn và nhận định
    old_quote: str | None      # Bằng chứng nguyên văn phía cũ nếu có
    new_quote: str | None      # Bằng chứng nguyên văn phía mới nếu có
    needs_review: bool
    review_reason: str

class SemanticChange:
    change_id: str             # Định danh thay đổi; validator hiện kiểm tra duy nhất trong từng result
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
- Bằng chứng lấy từ phiên bản V1 đã chọn, S hoặc tài liệu tham chiếu truy xuất từ kho hay được bổ sung. Mỗi đoạn trích có EvidenceRef xác định tài liệu và vị trí.
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

### 1.4 ScoringResult (Hợp đồng phân loại và chấm từng thay đổi)

Phân công Scorer theo LK-01. category theo tám mã GROUPS hoặc WORDING_ONLY/null, được kiểm tra bởi report_validation.py; rubric và thứ tự ưu tiên của guideline còn cần review, không phải điều kiện enum mới.

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
- Khi scoring khác null, mỗi SemanticChange có một ScoringResult tương ứng.
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
- Khi scoring khác null, mỗi SemanticChange vẫn có một ScoringResult; không chấm severity
  riêng cho từng ChangeAspect hoặc cộng điểm theo số lượng khía cạnh.
  Cảnh báo ở cấp khía cạnh được giữ đến kết quả chấm; nếu cảnh báo
  khiến chưa đủ căn cứ chấm mức độ tổng thể thì dùng None theo quy định trên.
- Chấm mức độ theo bộ tiêu chí và ví dụ nhóm đã thống nhất.

### 1.5 ExtractedDocument (Biểu diễn nguồn qua adapter)

```
class SourceBlock:
    source_ref: str       # block:N; định dạng khác chỉ khi đã kiểm chứng mapping
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
- Parser hiện tự đọc DOCX; document_adapter ánh xạ cây và source_blocks sang biểu diễn chung, không bắt Parser đọc lại từ ExtractedDocument. Native Parser trả articles/outside/source_blocks/warnings/status/summary; node có children, segments, full_text và source_refs.
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

### 1.7 ComparisonReport và AmendmentResult cấp văn bản đích

`ComparisonReport` là kết quả đối chiếu cục bộ cho một phiên bản V1. Các ID cục bộ `v1`, `s` và bộ kiểm tra hiện có áp dụng trong phạm vi báo cáo này. Báo cáo cấp S ánh xạ chúng về định danh phiên bản thực tế theo mục 1.8.

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
    role: Literal['BASE', 'AMENDMENT', 'REFERENCE']
    filename: str

class ComparisonReport:
    comparison_id: str
    base_document: DocumentIdentity
    amendment_document: DocumentIdentity
    reference_documents: list[DocumentIdentity]
    status: Literal['SUCCESS', 'PARTIAL', 'FAILED']
    results: list[AmendmentResult]
    warnings: list[ProcessingIssue]
    errors: list[ProcessingIssue]
```

Định nghĩa thực thi là các TypedDict trong [contracts.py](../backend/app/schemas/contracts.py). Mọi khóa phải có mặt, kể cả khóa có giá trị null; validator nhận dict/list, không nhận các dataclass Pipeline như payload thay thế. TypeAdapter chạy strict nhưng không tự cấm mọi khóa thừa; các owner không được dựa vào đó để thêm contract riêng.

- base_document có document_id = v1, role = BASE; amendment_document có document_id = s, role = AMENDMENT. Reference dùng role REFERENCE và ID không trùng các tài liệu khác. Filename chỉ là tên hiển thị, không chứa đường dẫn lưu nội bộ.
- Mỗi result giữ một AmendmentItem. text_diff/semantic_diff phải có amendment_id khớp item; semantic_diff có thể chứa nhiều SemanticChange. scoring khác null phải chứa một score cho mỗi change, nối bằng change_id trong cùng result.
- Bước chưa chạy/lỗi dùng null kèm lý do ở warnings/errors và review fields thích hợp; [] chỉ có nghĩa danh sách đã tạo rỗng, không tự chứng minh không có thay đổi. Giữ amendment ngay cả khi các bước sau null.
- category khác null của thay đổi nghĩa phải là một field_group có trong aspects. Không đổi nghĩa thì category = WORDING_ONLY, significance = LOW. Chưa xác định đổi nghĩa không được chấm mức xác định; significance null cần is_critical null và needs_review true. needs_review phải nhất quán với review_reason.
- SUCCESS không được có errors, đích UNRESOLVED hoặc bước phân tích null ở item APPLIES. Cờ review không tự đồng nghĩa thất bại. Pipeline vẫn phải quyết định PARTIAL/FAILED dựa trên kết quả dùng được và giải thích phần chưa xử lý; validator căn cứ chưa kiểm chứng mọi quy tắc tổng hợp trạng thái.
- validate_report kiểm tra cấu trúc và quan hệ, không nhận kho nguồn. Phải gọi thêm validate_sources(report, documents), validate_extracted_document cho từng nguồn và validate_amendment(item, documents, clauses). Cách cấp dữ liệu và thứ tự gọi được ghi ngay dưới đây.
- Không thay block:N khi đã trỏ đúng block và quote khớp nguyên văn. Chỉ dẫn lấy từ s; target_unit_ids kiểm tra theo clauses['v1']. Với PDF chuyển đổi, chỉ khẳng định vị trí DOCX đã parse nếu chưa có mapping về PDF gốc.
- Hiện change_id được validator kiểm tra trùng trong từng result, aspect_id trong từng change. Duy nhất toàn comparison và tái tạo toàn bộ Text Diff là yêu cầu cần review tăng cường riêng; không tuyên bố validator hiện tại đã bảo đảm.

Chi tiết cấp kho nguồn và cách gọi validator nằm trong [hướng dẫn tích hợp schema](schema-integration.md).

Cách cung cấp dữ liệu cho validator: documents là dict theo document_id, mỗi giá trị là ExtractedDocument gồm document_id/role/filename/file_type/blocks. Từ ParsedDocument của main, adapter lấy tree.source_blocks và giữ nguyên source_ref/text; articles được ánh xạ thành Clause(unit_id từ node_id, id từ nhãn Điều, title từ heading, content từ full_text, source_refs). clauses là dict có khóa v1 chứa list[Clause] của V1. Metadata/segments native giữ riêng khi cần, không thêm trường vào hợp đồng chung.

Thứ tự kiểm tra: validate_payload(ExtractedDocument, document) và validate_extracted_document(document) cho từng nguồn; validate_payload(Clause, clause) cho từng Clause; validate_amendment(result['amendment'], documents, clauses) cho từng result; validate_sources(report, documents); cuối cùng validate_report(report). Các hàm ở backend/app/schemas/validation.py và report_validation.py. validate_report không tự kiểm tra kho nguồn; các trường old_quote/new_quote thường cũng không tự được đối chiếu như EvidenceRef. Pipeline/runner phải được nối kiểm tra riêng, không suy đã có wiring chỉ vì có schema.

Ở cấp S, thiếu V1 vẫn cho phép giữ kết quả phân tích từ chỉ dẫn S và nguồn hợp lệ còn lại. Các kết luận này giữ nguồn và giới hạn theo yêu cầu ở mục 4.1, gắn với yêu cầu chưa giải quyết khi chưa có binding đích. Kiểu dữ liệu chi tiết cho kết quả này cần được thiết kế cùng validator cấp S. Các trường cục bộ hiện có tiếp tục tuân thủ quy tắc nguồn/null của từng đích.

### 1.8 Hợp đồng báo cáo cấp S

Bảng mô tả dữ liệu tối thiểu cần triển khai. Tên trường dùng để đặc tả điểm nối. Hợp đồng API và validator thực thi cần được cập nhật tương ứng.

| Trường | Nội dung tối thiểu |
|---|---|
| `analysis_id`, `amendment_document` | ID lượt xử lý, định danh S và nguồn đọc được. |
| `corpus_snapshot_id`, `coverage` | Phiên bản kho dân sự dùng cho lượt chạy, phạm vi đã rà soát và phần còn thiếu. |
| `targets` | Mỗi phần tử có ID đích, định danh văn bản, định danh phiên bản, nguồn và căn cứ chọn phiên bản. Kèm `ComparisonReport` cục bộ nếu đã phân tích, cùng ánh xạ ID nguồn cục bộ sang định danh cấp S. |
| `unresolved_amendments` | ID yêu cầu, thao tác hoặc đích được nêu, đoạn nguồn trong S, lý do và các ứng viên khi có. Phân biệt thiếu văn bản, thiếu phiên bản, ngoài kho, mơ hồ, ngoài phạm vi hỗ trợ và lỗi xử lý. Giữ liên kết đến kết luận có căn cứ từ S/nguồn sẵn có khi còn thiếu V1. |
| `indirect_impacts` | Danh sách nhận định có hoặc còn thiếu căn cứ về quy định của B, có liên kết về thay đổi trực tiếp. |
| `status`, `warnings`, `errors` | Trạng thái và vấn đề theo từng bước, đích hoặc tác động. Tách phần đã rà soát với phần chưa chạy hoặc bị giới hạn. |

Mỗi nhận định gián tiếp có ID riêng, ID đích, `amendment_id` và `change_id` khi có thay đổi nghĩa tương ứng, định danh văn bản/phiên bản B, vị trí quy định B, giải thích quan hệ và tác động có thể xảy ra, trích dẫn về quy định V1 bị sửa và quy định B, cùng nguồn trung gian nếu dùng. Khi thiếu căn cứ, giữ dữ kiện đã kiểm tra, đánh dấu cần rà soát và chỉ rõ phần còn thiếu. Nhận định có đủ căn cứ vẫn được diễn đạt theo phạm vi tác động có thể xác định từ nguồn.

Nếu một chỉ dẫn áp dụng cho nhiều đích, giữ một mã chỉ dẫn cấp S và liên kết đến từng kết quả cục bộ tương ứng. Dùng tổ hợp ID đích và ID cục bộ để định danh một kết quả đối chiếu. Mọi liên kết cấp S phải phân giải được theo ID đích và ID cục bộ. Kiểm tra trích dẫn với phiên bản nguồn tương ứng. Hệ thống giữ kết quả hữu ích khi một đích hoặc bước tác động gián tiếp chưa hoàn tất. Các trạng thái cụ thể của ứng viên B, kiểu dữ liệu đầy đủ, mapping ID và validator cấp S cần review trước khi code; không dùng mảng rỗng thay cho bước chưa chạy hoặc lỗi. Danh sách rỗng chỉ thể hiện kết quả sau khi bước liên quan đã chạy, với phạm vi rà soát được ghi rõ. `SUCCESS` áp dụng khi các bước bắt buộc hoàn thành trong phạm vi công bố, `PARTIAL` khi còn phần chưa xử lý nhưng có kết quả hữu ích, và `FAILED` khi không thể cung cấp kết quả hữu ích.

### 1.9 Đặc tả mục tiêu cho nút và hai loại quan hệ

Bổ sung ngày 27/11/2026, cụ thể hóa [BRD §8.7](brd.md#87-hai-loại-quan-hệ-giữa-các-văn-bản). Đây là yêu cầu dữ liệu cần thiết kế contract/validator/fixture trước triển khai, không phải trường mới đã có trong `ComparisonReport`, `SemanticDiffResult` hoặc API hiện tại. Không đồng nhất quan hệ ngữ nghĩa giữa hai văn bản với Semantic Diff của một cặp trước–sau.

| Đối tượng | Dữ liệu tối thiểu và quy tắc |
| --- | --- |
| Nút văn bản | Định danh toàn kho, định danh phiên bản và snapshot, số hiệu/tên khi biết, nguồn và vị trí file, hash khi có. Nút chưa phân giải giữ dấu hiệu gốc và lý do; không giả định đủ metadata/toàn văn. |
| Thuộc tính ngữ nghĩa | Chủ thể, đối tượng, hoạt động, quyền/nghĩa vụ, điều kiện/ngoại lệ và phạm vi không gian/thời gian khi có căn cứ. Mỗi giá trị gắn quy định/Điều/Khoản/Điểm hoặc block nguồn, phiên bản và nguyên văn. Thiếu thì ghi chưa biết, không suy từ nhãn chủ đề. |
| Cạnh dùng chung | ID, đầu nguồn/đích, loại quan hệ văn bản hay ngữ nghĩa, ý nghĩa quan hệ theo chiều, căn cứ/đoạn nguồn, phạm vi quy định liên quan, snapshot/phiên bản, cách tạo và trạng thái kiểm chứng cùng lý do. Cùng cặp nút được có nhiều cạnh và hai loại cạnh độc lập. |
| Quan hệ văn bản | Chiều A → B là A nhắc B. Bằng chứng nhắc tên nằm ở A; định danh/phiên bản B cần căn cứ phân giải riêng. Nhãn sửa đổi/bổ sung/bãi bỏ chỉ được gán khi xác định được vai trò chỉ dẫn và đích; tham chiếu chưa rõ được giữ để rà soát. |
| Quan hệ ngữ nghĩa | Giữ thuộc tính/quy định giao nhau và bằng chứng từ cả A/B, giải thích vì sao tạo liên hệ. Có thể đề xuất từ retrieval nhưng phải đối chiếu nguồn để xác minh. Quan hệ hai chiều cần căn cứ cho từng chiều, không suy nghịch đảo. |
| Kết quả kiểm chứng tác động | Nối tới thay đổi trực tiếp, cạnh/căn cứ được dùng và quy định B. Phân biệt có tác động có căn cứ, không thấy tác động với phần đã xét, chưa đủ căn cứ và bước chưa chạy/lỗi; tên trường và enum cần review riêng. |
| Trạng thái nút/cạnh | Tách độ đầy đủ nguồn, xác minh định danh/phiên bản và xác minh quan hệ. Độ sẵn sàng nguồn không chứng minh cạnh đúng hoặc kết luận tác động đúng; màu chỉ là biểu diễn của trạng thái đã chốt. |

EvidenceRef tiếp tục đối chiếu đúng phiên bản, source_refs và quote nguyên văn. Cạnh ngữ nghĩa chưa đủ căn cứ chỉ là ứng viên cần kiểm tra. Thiếu toàn văn B không ngăn lưu cạnh tham chiếu từ A, nhưng không được dùng làm căn cứ giả cho thuộc tính hoặc nội dung B.

Báo cáo cấp S ở §1.8 phải tham chiếu được các quan hệ đã dùng và các phần chưa giải quyết qua mapping định danh/phiên bản, không nhét các trường đồ thị vào contract cục bộ để bỏ qua validator. Lưu quan hệ theo snapshot/phiên bản; dữ liệu thay đổi thì các quan hệ liên quan cần kiểm tra lại, không tự áp dụng nhãn xác minh của bản cũ cho bản mới.

**Điểm còn mở:** quy ước thống nhất chiều phụ thuộc/tác động của cạnh ngữ nghĩa; nhãn chi tiết, thuật toán/ngưỡng trích xuất; tiêu chí màu và chuyển màu. Phải chốt chiều và điểm nối dữ liệu trước khi triển khai phần phụ thuộc. Không bổ sung database, công nghệ graph, endpoint hoặc thay đổi trách nhiệm module trong đặc tả này.

## 2. Functional Requirements

| Mã | Chức năng | Đầu vào → đầu ra | Tiêu chí nghiệm thu tối thiểu |
|---|---|---|---|
| FR-01 | Reader | Một file → ExtractedDocument | Đọc DOCX/PDF text, giữ thứ tự và vị trí nguồn; không đọc được phải báo lỗi |
| FR-02 | Parser | Một ExtractedDocument → list[Clause] và blocks được giữ | Tách Điều, giữ Khoản/Điểm và nguồn; giữ bảng/ngữ cảnh ngoài Điều để truy xuất khi cần |
| FR-03 | Trích yêu cầu từ S | S đã phân tích cấu trúc → danh sách yêu cầu | Giữ ID, thao tác, chỉ dấu văn bản/Điều/Khoản/Điểm đích và vị trí nguồn trong S. Việc trích không đòi hỏi V1 đã có. |
| FR-04 | Text Diff | AmendmentItem đủ nội dung cục bộ → TextDiffResult | Chỉ rõ thêm/xóa/thay thế; tọa độ khớp before_text/after_text; không diff toàn bộ V1 với S |
| FR-05 | Semantic Diff — rule trước, model khi cần | AmendmentItem có context và TextDiffResult nếu có → SemanticDiffResult | Semantic Diff phân tích nghĩa/bằng chứng; bộ tổng hợp giữ SemanticDiffResult trong AmendmentResult, không ép nhãn khi chưa rõ |
| FR-06 | Classifier & Scorer | AmendmentItem và SemanticDiffResult → list[ScoringResult] | Áp dụng rubric dân sự, giữ căn cứ và lý do. is_critical nhất quán với significance. |
| FR-07 | Kiểm thử chéo và đầu-cuối | Fixture/đáp án chuẩn, đầu ra thật và kết quả tích hợp | Hai owner kiểm tra hợp đồng và cách dùng; tính sai/bỏ sót khi đo, không triển khai Evaluator riêng |
| FR-08 | Upload và xem kết quả | S, bối cảnh và tài liệu bổ sung nếu có → báo cáo cấp S | Hiển thị đích, phiên bản, thay đổi, tác động, nguồn, hiệu lực, mức độ và phần chưa xử lý. |
| FR-09 | Ngữ cảnh và dẫn chiếu | V1, yêu cầu sửa đổi và nguồn truy xuất/bổ sung → AnalysisContext | Tìm đúng nội dung dẫn chiếu trong kho dân sự, giữ nguồn và báo cụ thể phần còn thiếu. |
| FR-10 | Hiệu lực và chuyển tiếp | S và yêu cầu sửa đổi → list[EffectInfo] | Giữ nội dung, phạm vi áp dụng và bằng chứng; ngoại lệ/chưa rõ phải cảnh báo; không tự xác minh hiệu lực thực tế |
| FR-11 | Truy xuất và giải quyết đích | Yêu cầu từ S và kho dân sự → đích và phiên bản trước sửa đổi | Tìm mọi đích đã nhận diện trong S. Dùng định danh, nguồn, vị trí điều khoản và căn cứ thời điểm/phạm vi áp dụng để kiểm tra lựa chọn. Giữ yêu cầu và lý do nếu chưa xác định được. |
| FR-12 | Dựng trạng thái sau sửa đổi | Yêu cầu đã liên kết và nguồn → AmendmentItem | Dựng nội dung cục bộ theo chỉ dẫn S, giữ vị trí đích, nguồn và xuất xứ QUOTED/DERIVED/ABSENT. Cảnh báo thao tác chưa thực hiện được. |
| FR-13 | Tìm và kiểm chứng tác động gián tiếp | Thay đổi trực tiếp và kho dân sự → các nhận định về B | Tìm ứng viên dù S và V1 không nêu B. Kiểm tra quy định B sử dụng phần nào của quy định V1 và giải thích tác động dựa trên nguồn kiểm chứng được. |
| FR-14 | Tổng hợp báo cáo cấp S | Kết quả từng đích, yêu cầu chưa giải quyết và tác động → báo cáo mục 1.8 | Giữ truy vết nguồn và liên kết kết quả giữa các bước. Hiển thị phạm vi kho, trạng thái và căn cứ còn thiếu. |

Các ngưỡng Change F1 ≥ 90% và Critical Change Recall ≥ 95% là dự tính và có thể thay đổi sau khi hoàn thiện test_evaluation_plan.md; chưa phải ngưỡng nghiệm thu chính thức. Đo trên bộ kiểm thử độc lập; đây chưa phải chất lượng đã được chứng minh của mã nguồn hiện tại.

Kiểm thử và phép đo ngoài luồng người dùng:
- Đối chiếu ở cấp từng SemanticChange theo quy tắc gán nhãn thống nhất;
  không đếm mỗi ChangeAspect thành một thay đổi độc lập. Nhãn chuẩn
  phải chứa các khía cạnh kỳ vọng; quy tắc matching quy định cách xử lý
  thiếu/sai khía cạnh trước khi chạy đánh giá, không tính đúng chỉ vì
  trùng một field_group. Ghi riêng lỗi nhóm, giá trị, diễn giải và bằng chứng.
- Dự đoán và nhãn chuẩn được ghép một-một; không tính trùng. Matching 1–n bổ sung sau khi hoàn thành 1–1, theo test_evaluation_plan.md.
- Nhãn chuẩn không được tìm thấy phải tính là bỏ sót.
- Thay đổi nghĩa dự đoán không có nhãn chuẩn tương ứng phải tính
  là phát hiện sai sau khi kiểm tra tính đầy đủ của nhãn chuẩn.
- Một thay đổi critical chỉ được tính tìm đúng khi đối chiếu đúng
  thay đổi và dự đoán is_critical = True.
- Kết quả cần kiểm tra chưa được giải quyết không tính là tìm đúng.
- Mẫu số bằng 0 trả null kèm lý do; không báo đạt mục tiêu.
- Báo số mẫu kiểm thử và số kết quả cần kiểm tra cùng các chỉ số.
- Kiểm tra riêng độ đúng của liên kết đích, trích hiệu lực và yêu cầu bổ sung tài liệu. Mẫu thiếu căn cứ được đánh giá theo khả năng nhận diện giới hạn; không ép gán tác động chưa có bằng chứng. Nhãn chuẩn phải phản ánh nguồn có trong phiên bản kho dùng cho ca kiểm thử và nguồn bổ sung nếu có.

Bổ sung yêu cầu quan hệ:

| Mã | Chức năng | Đầu vào → đầu ra | Tiêu chí nghiệm thu tối thiểu |
| --- | --- | --- | --- |
| FR-15 | Dựng quan hệ văn bản | Nội dung A + danh mục nguồn/phiên bản → tham chiếu A → B và căn cứ | Phân giải đúng đích hoặc giữ chưa giải quyết; nhắc tên không tự gán sửa đổi. Ca chỉ S phải tự tìm/kiểm tra V1, không dựa vào cặp đã chọn sẵn. |
| FR-16 | Trích thuộc tính và quan hệ ngữ nghĩa | Nguồn A/B → thuộc tính có bằng chứng, ứng viên và quan hệ được kiểm chứng | Tìm được liên hệ khi không nhắc tên nhau; phân biệt cùng chủ đề với phụ thuộc có căn cứ, phạm vi giao nhau và không giao nhau; hướng cạnh phải có ý nghĩa rõ. |
| FR-17 | Kiểm tra nguồn và trình bày trạng thái đồ thị | Nút/cạnh và registry → kết quả kiểm tra, phần hợp lệ và phần cần rà soát | Trạng thái nút/cạnh độc lập; nguồn không phân giải được không trở thành bằng chứng đã xác minh. Thành công truy xuất không xác nhận toàn bộ đồ thị. |

## 3. Yêu cầu theo module

Các tài liệu Architecture, Module và kế hoạch kiểm thử cần đồng bộ với hợp đồng cấp S khi triển khai.

### 3.1 Xử lý đầu vào và adapter

Thọ phụ trách `document_processing/`: giữ `pdf_to_docx.py`, `document_adapter.py`, `amendment_linker.py` và `parser/legal_structure_parser.py`. PDF có lớp chữ được chuyển sang DOCX khi cần, kiểm tra nội dung và giữ liên kết nguồn. Không thêm folder Reader riêng hoặc bắt refactor code hiện có để khớp sơ đồ cũ.

Adapter chuẩn hóa output Parser để các bên nhận dùng được, giữ document_id, vai trò, filename, nguồn gốc và cảnh báo. Không đọc được chữ thì báo lỗi; không coi file rỗng là đầu vào hợp lệ.

### 3.2 Parser cấu trúc văn bản

Parser tự đọc DOCX, trả cây `articles`, `outside`, `source_blocks`, `warnings`, `status`, `summary`; node giữ `children`, `segments`, `full_text`, `source_refs`. Không nhầm câu dẫn chiếu thành đầu Điều. V1/S không có Điều: báo lỗi cấu trúc; tham chiếu không có Điều vẫn có thể dùng blocks/bảng.

Thọ và bên nhận chốt cấu trúc JSON fixture, định danh, đơn vị đếm và mapping nguồn. `summary` đếm theo cây đã parse, không tự chứng minh không bỏ sót nội dung; phải đối chiếu số lượng và vị trí kỳ vọng được review độc lập từ mẫu nguồn. Cây Parser không phải knowledge graph hoặc payload LightRAG được chốt sẵn.

### 3.3 Module trích yêu cầu sửa đổi và liên kết

| Nội dung | Quy định |
|---|---|
| Đầu vào | S sau Reader/Parser và các phiên bản V1 truy xuất từ kho theo yêu cầu |
| Xử lý | Trích từng yêu cầu sửa/bổ sung/bãi bỏ trong S. Tìm đích, kiểm tra phiên bản và liên kết Điều/Khoản/Điểm trước khi dựng nội dung cục bộ. |
| Đầu ra | AmendmentItem cho từng đích đã liên kết và yêu cầu chưa giải quyết ở báo cáo cấp S |
| Yêu cầu | Một Điều có thể có nhiều yêu cầu; phân biệt số Điều trong S với vị trí đích; không coi nội dung không được nhắc đến là bãi bỏ |
| Chưa rõ | Giữ chỉ dẫn nguồn, cảnh báo; không tự áp sửa đổi khi thiếu căn cứ |

Bước chuẩn bị ngữ cảnh lấy định nghĩa, ngoại lệ và quy định dẫn chiếu từ phiên bản V1, kho dân sự hoặc nguồn bổ sung. Gắn hiệu lực/chuyển tiếp từ S qua EffectInfo. LightRAG hỗ trợ tìm ứng viên nguồn ở ba mục đích: xác định đích/phiên bản trước Linker, bổ sung ngữ cảnh trước Semantic, và tìm B sau phân tích trực tiếp. Query ngữ cảnh của PR #7 cần TextDiffResult; hai mục đích còn lại không dùng chung điều kiện này. Tra số hiệu/metadata chính xác trước khi dùng retrieval mở rộng. Pipeline kiểm tra lại định danh, phiên bản, vị trí và nguyên văn trước khi dùng ứng viên làm căn cứ. Dữ liệu bổ sung theo lượt được quản lý riêng với kho dùng chung.

### 3.4 Module Text Diff — tìm những đoạn chữ thay đổi: Sau khi xác định nội dung trước/sau cục bộ, Text Diff chỉ ra chữ nào được thêm, xóa hoặc thay thế.

| Nội dung | Quy định |
|---|---|
| Đầu vào | Một `AmendmentItem` đủ căn cứ đối chiếu |
| Xử lý | So sánh before_text và after_text cục bộ |
| Đầu ra | TextDiffResult theo mục 1.6; Ngọc Anh chủ trì |
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
| Đầu ra | SemanticDiffResult theo mục 1.3, Pipeline tổng hợp AmendmentResult theo mục 1.7 |
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
| Đầu ra | list[ScoringResult], một kết quả cho mỗi SemanticChange |
| Yêu cầu | Mức độ phải có lý do dựa trên nội dung và bằng chứng của thay đổi |

Nhãn tổng thể category dùng tám mã tại mục 1.3 hoặc WORDING_ONLY/null theo mục 1.4; operation thể hiện sửa/bổ sung/bãi bỏ, aspects giữ toàn bộ nội dung khía cạnh.

Quy tắc cần ghi rõ:
- significance nhận LOW, MEDIUM, HIGH, CRITICAL hoặc null theo ràng buộc tại mục 1.4 và validator.
- is_critical = true khi và chỉ khi significance = CRITICAL.
- Chỉ sửa văn phong, không đổi nghĩa → LOW.
- Thêm/xóa Điều không tự động được coi là CRITICAL.
- Chưa đủ căn cứ → needs_review = true, significance và is_critical để null.
- Bộ tiêu chí phân biệt các mức phải có ví dụ được nhóm thống nhất trước khi đánh giá hệ thống.

### 3.7 Kiểm thử chéo và phép đo

Không triển khai Evaluator độc lập, không giao Tuấn Anh đầu việc Evaluator. Owner module kiểm thử phần mình; hai owner tại điểm nối review input/output và chạy tích hợp. Dũng điều phối tích hợp/Pipeline/API; Đức Anh điều phối kế hoạch đánh giá; các owner phối hợp, Dũng hỗ trợ dữ liệu/nghiệp vụ và người khác review nhãn. Script phép đo nếu cần đặt trong `test/`; thiết kế đánh giá và phép đo theo [Kế hoạch kiểm thử và đánh giá](test_evaluation_plan.md), quy trình kiểm thử chéo theo [Workflow](workflow.md). Các yêu cầu đo dưới đây vẫn được giữ, không thay bằng việc hai module chỉ chạy thông nhau.

| Nội dung | Quy định |
|---|---|
| Đầu vào | Các ca chỉ nộp S, kho dân sự cố định và đáp án có đích/phiên bản, thay đổi trực tiếp và tác động gián tiếp đã rà soát |
| Xử lý | Đối chiếu các thay đổi dự đoán với đáp án chuẩn |
| Đầu ra | Độ đúng truy xuất văn bản/phiên bản, Precision, Recall, Change F1, Critical Change Recall cho thay đổi trực tiếp và phép đo riêng cho tác động gián tiếp |
| Cách sử dụng | Chạy khi kiểm thử, đánh giá; không bắt buộc chạy mỗi lần người dùng so sánh |

Ý nghĩa các chỉ số:

| Chỉ số | Câu hỏi được trả lời |
|---|---|
| Precision | Trong các thay đổi nghĩa hệ thống báo, bao nhiêu là đúng? |
| Recall | Trong các thay đổi nghĩa thực sự, hệ thống tìm được bao nhiêu? |
| Change F1 | Điểm tổng hợp Precision và Recall |
| Critical Change Recall | Hệ thống tìm đúng bao nhiêu thay đổi trọng yếu thực sự? |

Yêu cầu nghiệm thu cần ghi:
- Các ngưỡng Change F1 ≥ 90% và Critical Change Recall ≥ 95% là dự tính và có thể thay đổi sau khi hoàn thiện test_evaluation_plan.md; chưa phải ngưỡng nghiệm thu chính thức. Đo trên bộ kiểm thử độc lập.
- Thay đổi có trong đáp án nhưng hệ thống bỏ sót phải được tính là lỗi; không bỏ qua do thiếu kết quả hoặc liên kết sai.
- Kết quả needs_review chưa được giải quyết không được tính là phát hiện đúng; phải báo thêm số lượng cần kiểm tra.
- Tập kiểm thử không được dùng để điều chỉnh thuật toán.
- Chỉ số không tính được do mẫu số bằng 0 trả null kèm lý do; không báo đạt mục tiêu.

Ca nghiệm thu tối thiểu:
- Chỉ nộp S và kiểm tra đúng văn bản, phiên bản và Điều/Khoản/Điểm. Có ca S sửa nhiều văn bản, ca nhiều phiên bản khả dĩ và ca đích nằm ngoài kho.
- S rút thời hạn tại V1 từ 30 ngày xuống 15 ngày. B sử dụng thời hạn đó dù S và V1 không nêu tên B. Kiểm tra đúng quy định B, mối liên hệ, tác động và trích dẫn.
- B có quan hệ với V1 nhưng phần bị sửa không ảnh hưởng đến cách áp dụng của B. Có ca riêng thiếu căn cứ để kết luận, cần hiển thị trạng thái rà soát.
- Tính lỗi truy xuất làm mất thay đổi trực tiếp vào phép đo đầu cuối. Đo riêng TP/FP/FN của tác động gián tiếp trên phạm vi đã gán nhãn và rà soát chất lượng giải thích, trích dẫn. Ngưỡng riêng cho truy xuất và tác động gián tiếp cần thống nhất trong kế hoạch đánh giá.

Ví dụ: đáp án có 10 thay đổi trọng yếu, hệ thống tìm đúng 8 → Critical Change Recall = 80%.

### 3.8 Kho dân sự và truy xuất

Kho do nhóm chuẩn bị, có danh mục phiên bản có thể truy vết. Mỗi bản lưu định danh văn bản, định danh phiên bản, nguồn, thông tin hiệu lực khi có và chỉ mục Điều/Khoản/Điểm trỏ về đoạn gốc. Khi không đủ thông tin thời điểm hoặc có nhiều phiên bản khả dĩ, giữ ứng viên cùng lý do cần rà soát. Danh mục cụ thể và quy trình chuẩn bị dữ liệu thuộc kế hoạch dữ liệu.

#### 3.8.1. Chuẩn bị hai loại quan hệ trong kho

Thực hiện lượt quan hệ văn bản trước, mở rộng thuộc tính và quan hệ ngữ nghĩa theo §1.9 sau đó. Không cần chờ dựng xong mọi quan hệ ngữ nghĩa mới được tra tham chiếu đã đủ căn cứ. Reader/Parser cung cấp nguyên văn/vị trí; chuẩn bị kho giữ định danh/phiên bản và thuộc tính có nguồn; retrieval tìm ứng viên; bước dùng kết quả kiểm chứng nội dung trước khi xác nhận quan hệ. Giữ phân công theo [Module](module.md), không giao lại toàn bộ chức năng cho một module/người.

Nhận diện ranh giới và vai trò trích dẫn/thay thế qua nhiều block, kể cả ngoặc kép lồng nhau. Chưa rõ thì ghi cần rà soát và giữ nguyên văn; không lấy hành động bên trong trích dẫn làm chỉ dẫn trực tiếp của S mà thiếu phân tích vai trò. Chỉ xác nhận S → V1 sau khi kiểm tra đích/phiên bản; pilot với hai DOCX chọn sẵn không đủ nghiệm thu luồng chỉ S.

### 3.9 Phân tích tác động gián tiếp

Agent truy xuất các quy định có khả năng phụ thuộc vào quy định V1 bị sửa. Với từng ứng viên B, lấy nguyên văn quy định liên quan và đối chiếu cách B sử dụng quy định V1 với nội dung trước/sau. Quan hệ dẫn chiếu hoặc độ tương đồng dùng để tìm ứng viên, không đủ để xác nhận tác động. Phân biệt quan hệ có căn cứ trực tiếp và quan hệ suy ra; không tự kết luận B bị sửa hoặc hết hiệu lực. Căn cứ báo tác động phải giải thích phần thay đổi liên quan đến điều kiện, nghĩa vụ, thời hạn hoặc nội dung áp dụng trong B. Nếu quan hệ có thật nhưng phần thay đổi không ảnh hưởng đến B, loại ứng viên khỏi danh sách tác động. Nếu chưa đủ căn cứ để phân định, ghi nhận nội dung cần rà soát. Phương pháp tìm quan hệ không có dẫn chiếu trực tiếp và ngưỡng đánh giá cần được xác nhận qua thử nghiệm.

#### 3.9.1. Dùng quan hệ để kiểm chứng tác động

Từ quy định V1 thực sự thay đổi, tìm ứng viên qua cả hai loại quan hệ, lấy đúng nguồn A/B và kiểm tra phần thay đổi có giao với căn cứ tạo cạnh không. Mỗi kết quả giữ liên kết tới yêu cầu/thay đổi trực tiếp, quy định liên quan, cạnh và trích dẫn. Có quan hệ nhưng thay đổi không liên quan thì không báo thành tác động; thiếu căn cứ giữ ứng viên, phạm vi đã kiểm tra và phần còn thiếu. Không tự truyền tác động sang mọi hàng xóm hoặc đảo chiều cạnh ngữ nghĩa khi quy ước hướng chưa chốt.

Khi có đồ thị hiển thị, trình bày nhãn và lý do trạng thái của từng nút/cạnh, hỗ trợ nhận biết ngoài màu sắc. Nút thiếu toàn văn vẫn có thể giữ cạnh tham chiếu đã có bằng chứng từ A. Chưa xác định tiêu chí màu xanh/vàng/đỏ trong lần cập nhật này; không nghiệm thu đúng/sai chỉ dựa màu.

## 4. Yêu cầu tải tài liệu và xem kết quả

Khi người dùng chọn **Hiện bằng chứng**, giao diện hiện đoạn trích và vị trí nguồn từ `EvidenceRef` của kết quả đang xem. Hành vi này dùng báo cáo đã trả trong lượt hiện tại. Xem [vòng đời nguồn](architecture.md#43-vị-trí-lưu-và-vòng-đời).

Hiển thị bằng chứng là chức năng chính: xem quote, tài liệu/vị trí nguồn gắn với nhận định; phân biệt nguyên văn và DERIVED. Không coi entity/relation hay retrieval score là bằng chứng đã xác minh.

| Chức năng | Yêu cầu |
|---|---|
| Chọn đầu vào | Một S dạng DOCX/PDF có lớp chữ là tệp bắt buộc. Bối cảnh và tài liệu bổ sung là tùy chọn. |
| Bắt đầu so sánh | Người dùng nhấn “So sánh”; hệ thống kiểm tra file rồi chạy pipeline |
| Trạng thái xử lý | Hiển thị đang xử lý, hoàn thành, hoàn thành một phần hoặc thất bại; phân biệt hoàn thành với kết quả còn cần kiểm tra |
| Xem kết quả | Hiển thị thay đổi trước/sau theo từng đích và đánh dấu phần được dựng. Hiển thị tác động lên B với quy định liên quan, trích dẫn và liên kết về thay đổi trực tiếp. |
| Nhận diện tài liệu | Hiển thị S, từng đích và phiên bản được dùng, căn cứ lựa chọn, nguồn tham chiếu và phần chưa xác định. |
| Xem phân tích | Duyệt results, hiển thị amendment, text_diff, semantic_diff.changes và scoring theo change_id; lọc theo tám field_group/category, giữ nguồn và cảnh báo |
| Nhận xét dự kiến | Hai loại theo mục 9; phát triển sau chức năng cốt lõi, không bắt buộc bản đầu |
| Vị trí nguồn | Hiển thị EvidenceRef trong đúng V1, S hoặc tài liệu tham chiếu: trang PDF hoặc đoạn/bảng DOCX; luôn giữ nguồn chỉ dẫn trong S kể cả bãi bỏ |
| Cần kiểm tra | Hiển thị rõ các kết quả `needs_review = true`; mức độ chưa xác định ghi “Chưa xác định” |
| Không có thay đổi | Chỉ hiển thị kết luận trong phạm vi đã xử lý đầy đủ. Yêu cầu chưa định vị hoặc chưa phân tích phải hiển thị kèm lý do. |
| Tài liệu bổ sung | Hiển thị văn bản, phiên bản và vị trí còn thiếu; cho bổ sung hoặc chọn “Hiện tại không có tài liệu”, tiếp tục theo UI-01–UI-02. |
| Hiệu lực/chuyển tiếp | Hiển thị nội dung, phạm vi áp dụng và bằng chứng trong EffectInfo; phần chưa xác định phải có cảnh báo |

Quy định hiển thị vị trí nguồn:
- Chuyển source_refs thành nhãn dễ đọc theo nguồn thực tế: `block:N` là khối trong DOCX đã parse, segments có offset ký tự Python `[start,end)`. Nếu frontend dùng chỉ số khác phải chuyển đổi và có fixture. Trang PDF chỉ hiển thị khi đã kiểm chứng mapping về PDF gốc; không suy từ số block hoặc ghi nhãn DOCX như trang PDF.

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
- Quy mô mẫu, người tham gia, cách chấm và tiêu chí đánh giá được hoàn thiện
  trong test_evaluation_plan.md trước thử nghiệm. Nếu thành viên nhóm đóng
  vai luật sư/pháp chế hoặc sinh viên luật, phải ghi rõ giới hạn này.
  Đây là hoạt động đánh giá ngoài luồng so sánh. Nhận xét kiểm chứng trong phiên theo mục 9 là dữ liệu sản phẩm riêng; không tự chuyển thành dữ liệu nghiên cứu hoặc nhãn chuẩn.

### 4.1. Tương tác thiếu nguồn, phiên và bằng chứng

| Mã | Hành vi mục tiêu có thể kiểm thử |
| --- | --- |
| UI-01 | Khi chưa tìm được V1 hoặc điều khoản cần thiết, liệt kê phần thiếu và cho chọn “Bổ sung tài liệu” hoặc “Hiện tại không có tài liệu”. Khi chọn lựa chọn thứ hai, tiếp tục phân tích S và nguồn hợp lệ sẵn có, trình bày kết luận có căn cứ và chỉ rõ phần trước/sau hoặc tác động chưa xác định. Giữ kết quả của các đích khác. |
| UI-02 | Kiểm tra V1 bổ sung về định dạng, phạm vi, định danh, phiên bản và quan hệ với S. Khi không khớp, nêu dấu hiệu và yêu cầu thay file. Người dùng có thể chọn chưa có tài liệu để xử lý theo UI-01. |
| UI-03 | Kiểm tra phạm vi dân sự tại tiếp nhận S và nguồn bổ sung, ghi căn cứ. Khi chưa chắc chắn thì yêu cầu làm rõ. Văn bản dân sự chưa có trong kho được báo thiếu nguồn. Với S nhiều lĩnh vực, ghi nhận đích ngoài phạm vi và tiếp tục các đích dân sự đủ căn cứ. |
| UI-04 | Đếm riêng văn bản đích, yêu cầu sửa đổi và điều khoản đủ/thiếu nguồn. Liệt kê từng phần cần bổ sung. Nhiều phiên bản ứng viên của cùng văn bản cần căn cứ lựa chọn trước khi đối chiếu. |
| UI-05 | Phân biệt tài liệu ngữ cảnh giúp hiểu thay đổi trực tiếp với B là đối tượng rà soát tác động. Một nguồn có thể mang cả hai vai trò. Mỗi tác động lên B phải liên kết quy định B sử dụng phần nào của V1, thay đổi liên quan và bằng chứng. |
| UI-06 | Người làm UI chọn cách tô nền, chữ đậm hoặc đánh dấu kèm nhãn, hỗ trợ nhận biết ngoài màu sắc. Hiển thị căn cứ chọn V1, trước/sau, nhận định thay đổi, căn cứ liên hệ B khi có, kết luận và giới hạn. Chỉ rõ mắt xích thiếu dữ liệu. |
| UI-07 | Bổ sung tài liệu tạo lượt phân tích mới với S và nguồn cần thiết trong cùng trải nghiệm UI. Giữ báo cáo trước trong khi chờ và khi lượt mới thất bại; báo cáo mới được phân biệt theo lượt và nguồn đã dùng. |
| UI-08 | Sau khi nhận báo cáo, người dùng mở bằng chứng nhiều lần dù tài nguyên xử lý tạm đã được dọn. “Kết thúc phiên” xóa báo cáo, trạng thái và lựa chọn đang giữ trên UI. |
| UI-09 | Hoàn tất xử lý xét theo phạm vi kết quả, bằng chứng và giới hạn. Nhận xét là chức năng mở rộng. Đánh giá đúng/sai của kết luận được ghi nhận riêng trong nghiệm thu kể cả khi trạng thái là SUCCESS. |
| UI-10 | Cho phép người dùng chủ động thử lại sau lỗi dịch vụ theo E4. Dùng lại dữ liệu đã kiểm tra còn hợp lệ nếu còn lưu; nếu dữ liệu cần thiết đã dọn hoặc thay đổi thì tạo lượt phân tích mới. Thông báo phần được chạy lại, tránh gửi lặp và giữ báo cáo có sẵn khi thử lại lỗi. |

Nếu bằng chứng chưa truy cập được, thông báo phần gặp lỗi và cho mở lại. Khi chưa khôi phục được, ghi rõ chưa đáp ứng điều kiện xem bằng chứng của nhận định liên quan; giữ nội dung có nguồn đã trả và cho kết thúc phiên theo yêu cầu.

### 4.2. Nhánh hủy đang đề xuất

E6 tiếp tục ở mức đề xuất. Nếu đưa nút hủy trong lúc xử lý vào bản đầu, cần chốt cách ghi nhận hủy, dừng bước tiếp theo, theo dõi tác vụ backend còn chạy và cleanup. Chỉ đưa nhánh này thành điều kiện nghiệm thu khi nhóm xác nhận phạm vi và đầu ra kỳ vọng.

## 5. Xử lý lỗi và cảnh báo

Khi chưa xác định được đích, giữ chỉ dẫn, thao tác đã nhận diện và bằng chứng. Dùng `applicability = UNRESOLVED`, `needs_review = true` và lý do. Giữ mục trong báo cáo và để các kết quả phân tích chưa chạy là `null`.

Khi có căn cứ gán nhóm khía cạnh nhưng chưa đủ căn cứ chấm mức độ, giữ nhóm đã xác định, dùng `significance = null`, `is_critical = null`, `needs_review = true` và ghi lý do. Rubric chi tiết và cách xử lý lỗi theo bước sẽ được cập nhật từ báo cáo của các thành viên sau lần chạy phiên 1.

Owner từng module tự xử lý và báo lỗi thuộc phần mình; chuyển bằng chứng có nguồn cùng lỗi/cảnh báo và phạm vi bị ảnh hưởng cho module nhận đầu ra theo contract chung. Bên nhận kiểm tra dữ liệu, không bỏ cảnh báo hoặc biến thiếu căn cứ thành không có thay đổi. Pipeline tổng hợp trạng thái báo cáo, không thay owner xử lý lỗi nội bộ.

| Tình huống | Hành vi yêu cầu |
|---|---|
| Thiếu S hoặc S sai định dạng | Dừng và hướng dẫn nộp S dạng DOCX hoặc PDF có lớp chữ |
| File hỏng, có mật khẩu hoặc không đọc được chữ | Dừng xử lý; báo rõ file nào gặp lỗi |
| Parser không tìm được Điều trong V1 hoặc S | Báo lỗi cấu trúc; không trả kết quả “không có thay đổi” |
| Đích sửa đổi mơ hồ hoặc chỉ dẫn tách/gộp chưa xác định đủ | Cảnh báo cần kiểm tra; không coi phần chưa liên kết chắc chắn là bổ sung/bãi bỏ đã xác nhận |
| Phân tích nghĩa hoặc chấm mức độ chưa đủ căn cứ | Đánh dấu `needs_review = true`; kết luận chưa xác định để `null` |
| Một bước xử lý thất bại | Báo bước gặp lỗi; nếu hiển thị kết quả một phần, phải ghi rõ báo cáo chưa hoàn tất |
| Thiếu hoặc sai nội dung tham chiếu | Giữ kết quả đã xác định; báo PARTIAL và chỉ rõ tài liệu/nội dung cần bổ sung; không tự suy luận tác động |
| S sửa nhiều văn bản | Phân tích theo từng đích. Nếu đích ngoài kho, thiếu hoặc chưa xác định được phiên bản, giữ chỉ dẫn trong S, lý do và các ứng viên khi có |
| Thiếu căn cứ về tác động lên B | Giữ thông tin đã kiểm tra và chỉ rõ căn cứ còn thiếu. Hiển thị phạm vi kho đã rà soát. |
| Chưa rõ hiệu lực hoặc ngoại lệ chuyển tiếp | Giữ trích dẫn, cảnh báo phạm vi chưa xác định; không tự gán một ngày cho mọi thay đổi |
Yêu cầu chung: thông báo lỗi phải dễ hiểu và có hướng xử lý; không hiển thị lỗi kỹ thuật nội bộ cho người dùng.

Thiếu V1 được xử lý theo UI-01. V1 bổ sung sai đích được xử lý theo UI-02. Thiếu nguồn của một đích chỉ giới hạn phần phụ thuộc vào nguồn đó. Kết quả dựa trên S phải giữ căn cứ nguyên văn và phần chưa thể đối chiếu; bộ kiểm tra cấp S cần kiểm chứng các quan hệ này.

Tài liệu ngoài phạm vi và tài liệu dân sự thiếu trong kho được xử lý theo UI-03. Lỗi retrieval được ghi là lỗi truy xuất; việc xác định thiếu nguồn hoặc phạm vi cần kiểm tra căn cứ độc lập.

### 5.1. Phân biệt truy xuất và xác minh đồ thị

Giữ riêng kết quả lập chỉ mục/truy xuất, đối chiếu nguồn đồ thị và dọn tài nguyên. Không gắn một nhãn xác minh toàn lượt chỉ vì retrieval tìm được đoạn kỳ vọng. Nếu nút/cạnh không ánh xạ được về registry thì loại khỏi phần bằng chứng đã xác minh, ghi vấn đề nguồn và giữ phần kết quả hợp lệ.

Việc bước bắt buộc chưa hoàn tất ảnh hưởng báo cáo cấp S theo §1.8: có kết quả hữu ích nhưng còn lỗi/phần chưa kiểm tra thì PARTIAL; không có kết quả hữu ích thì FAILED. Không thay quy tắc SUCCESS/PARTIAL/FAILED của validator báo cáo cục bộ hoặc coi mọi mục cần review là lỗi thực thi. Hoàn thành xử lý và đúng về nghĩa/hiệu lực pháp lý là hai phép đánh giá khác nhau.

## 6. Yêu cầu vận hành

| Nội dung | Yêu cầu |
|---|---|
| Cấu hình | Giới hạn dung lượng file và thời gian xử lý phải cấu hình được; giá trị cụ thể cần nhóm thống nhất trước nghiệm thu |
| Tính toàn vẹn | Không âm thầm cắt bỏ nội dung; nếu không xử lý hết tài liệu phải thông báo rõ |
| Truy vết | Dùng analysis_id cho lượt xử lý và comparison_id cho kết quả từng đích. Giữ phiên bản kho, các bước và lỗi. |
| Quản lý file | Tách kho dân sự do nhóm chuẩn bị với tài liệu tạm theo lượt. Dữ liệu bổ sung và index tạm theo lượt được dọn đúng phạm vi sau xử lý; không xóa kho/index dùng chung. Không tự đưa tài liệu người dùng vào kho chung. Client thử nghiệm hiện cách ly một server cho một comparison, chưa thực thi vòng đời kho bền vững. |
| Bảo mật | Không ghi toàn bộ nội dung tài liệu vào log. Nếu dùng API bên ngoài, phải thống nhất việc gửi dữ liệu và quản lý khóa API |
| Đo hiệu năng | Ghi nhận thời gian xử lý và kích thước tài liệu; chỉ chốt mục tiêu tốc độ sau khi đo trên bộ tài liệu mẫu và môi trường xác định |

- Reader phải trích xuất toàn bộ nội dung có thể đọc được, giữ bảng và vị trí nguồn. Tài liệu PDF được đọc trực tiếp hoặc chuyển đổi trong Reader phải giữ khả năng truy nguồn; lựa chọn công cụ không làm thay đổi hợp đồng đầu ra.
- Không so sánh toàn diện phần mở đầu, chữ ký hoặc phụ lục; nội dung đọc được ở các phần này có thể dùng làm ngữ cảnh hoặc bằng chứng, bao gồm bảng được dẫn chiếu.
- Không xử lý hết yêu cầu trong S hoặc phần nguồn cần thiết phải báo PARTIAL/FAILED, không báo hoàn tất toàn bộ.
- API mục tiêu dự kiến dùng request đồng bộ, nhận S bắt buộc, bối cảnh và tài liệu bổ sung tùy chọn. API đang chạy vẫn nhận V1 + S; chưa có endpoint chỉ S. Đo thời gian truy xuất nhiều đích và tác động gián tiếp để xác nhận giới hạn vận hành trước nghiệm thu.
- Khi bổ sung tài liệu, giao diện gửi S và nguồn cần thiết trong lượt phân tích mới theo UI-07. Báo cáo và bằng chứng trả về có đủ dữ liệu để tiếp tục xem sau cleanup; UI-08 quy định thời điểm kết thúc phiên.
- Không sử dụng job nền hoặc API polling trong bản đầu.
- Giao diện hiển thị đang xử lý, ngăn gửi lặp và không tự gửi lại khi timeout.
- Giới hạn số lượng/dung lượng file, thời gian xử lý và cách trả lỗi được quy định trong API contract và cấu hình triển khai.

## 7. Quy định dữ liệu trao đổi giữa các module

Đây là hợp đồng dữ liệu: quy định các module nhận và trả những gì để ghép được với nhau.

| Dữ liệu | Nội dung tối thiểu |
|---|---|
| Parser → Adapter | Cây articles/outside/source_blocks, nguồn, cảnh báo và summary; Parser tự đọc DOCX |
| Adapter → Trích yêu cầu/liên kết | Cấu trúc, định danh và nguồn S để trích yêu cầu. Đích và phiên bản V1 thu được qua bước truy xuất. |
| Trích yêu cầu/liên kết → Ngữ cảnh | AmendmentItem có chỉ dẫn, vị trí đích, nội dung cục bộ, bằng chứng và cảnh báo |
| Linker → Text Diff; chuẩn bị Context song song | AmendmentItem có trước/sau đủ căn cứ cho Text Diff; index sẵn sàng và TextDiffResult được ghép để query/kiểm tra nguồn trước Semantic |
| Semantic Diff → Scorer | change_id, kết luận đổi nghĩa, diff_details, aspects, evidence và cảnh báo theo mục 1.3 |
| Pipeline → giao diện | Báo cáo cấp S theo mục 1.8, chứa kết quả đối chiếu từng đích, tác động gián tiếp, nguồn, phạm vi và lỗi |

## 8. Các quyết định cần chú ý khi triển khai/nghiệm thu

- Bộ tiêu chí LOW/MEDIUM/HIGH/CRITICAL, kèm ví dụ có nhãn.
- Ví dụ ranh giới giữa 8 nhóm field_group, quy tắc chia/gộp thay đổi
  và chọn category tổng thể từ aspects; danh mục mã theo mục 1.3–1.4.
- Quy tắc đối chiếu dự đoán với ground truth theo test_evaluation_plan.md: áp dụng matching 1–1 trước; trường hợp chia/gộp cần matching 1–n được bổ sung sau khi hoàn thành 1–1.
- Danh mục và phiên bản kho dân sự, bộ ca chỉ nộp S có đáp án đích/phiên bản, vị trí, bằng chứng, hiệu lực và tác động gián tiếp.
- Giới hạn dung lượng, thời gian xử lý và môi trường đo hiệu năng.
- Cấu hình truy xuất LightRAG, bộ quy tắc và rubric dân sự, cách kiểm chứng ứng viên B và ngưỡng đánh giá riêng.
- Công nghệ frontend.

### Quy tắc phát triển và kiểm tra hợp đồng

Luồng chạy có thứ tự không buộc các owner chờ nhau hoàn thành mới code. Mỗi điểm nối có input/output mẫu đã review, phiên bản schema ghi trong metadata fixture riêng và kiểm tra tự động; không thêm schema_version vào payload chung. JSON dùng lưu fixture, module trong backend bàn giao dict/list theo TypedDict đã chốt. Không bắt mỗi bước ghi file JSON hoặc gọi HTTP. Bên nhận code với fixture/mock, bên giao tạo output thật theo cùng hợp đồng; hai bên kiểm tra chéo khi tích hợp. Các file bắt buộc và giới hạn sửa cấu trúc theo [Module](module.md); Git/PR theo [Workflow](workflow.md).

Phân công chức năng theo LK-01 trong decision.md: Dũng tích hợp/API; Thọ xử lý tài liệu; Ngọc Anh Text Diff; Dũng + Đức Anh + Ngọc Anh phụ trách Semantic Diff và Scorer; Tuấn Anh phụ trách UI và xử lý lỗi trả về; Dũng + Đức Anh AI Adapter. Schema chung đã chốt theo commit căn cứ; chữ ký hàm, mapping và hành vi chưa được code căn cứ quy định vẫn cần owner/bên nhận review.

## 9. Phạm vi mở rộng

Nhận xét có hai hướng: lưu phản hồi sau lượt phân tích để cải thiện dự án, và dùng nhận xét trong lượt để người dùng xem xét lại kết luận. Khi triển khai, giao diện phân biệt kết luận ban đầu, kết luận cập nhật và căn cứ thay đổi. API, định danh, cách lưu và cơ chế kết hợp nhận xét sẽ được chốt khi triển khai. Nhận xét là dữ liệu phản hồi cần review trước khi dùng cho đánh giá hoặc huấn luyện.
