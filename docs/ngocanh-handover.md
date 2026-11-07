# Bàn giao phần Ngọc Anh — từ tuần 6

Ngày cập nhật: 07/11/2026. Phạm vi: PL-05/06 và phần kiểm thử/tài liệu liên quan.
Đây là tiến độ thực hiện hiện tại, không xác nhận hoàn thành hồi tố các tuần.

## Cách chạy

Python 3.10 trở lên, Pydantic 2: `python -m pip install -r requirements-analysis.txt`.

Chạy regression: `python -m unittest test_pipeline_modules -v`.
Các ca trong test là SYNTHETIC, vị trí `fixture:*` thuộc fixture trong bộ nhớ;
không phải nguồn DOCX thật, gold đã review hoặc tập đánh giá độc lập.
Fixture JSON dùng lại: `tests/fixtures/ngocanh_deadline_synthetic.json`.

Đầu vào tích hợp: `src.local_analysis.analyze_amendment(item, context_complete=True)`.
`item` là mapping AmendmentItem theo SRS. Chỉ truyền `context_complete=True` sau
khi bên chuẩn bị ngữ cảnh kiểm tra đủ định nghĩa, điều kiện, ngoại lệ và dẫn chiếu.
Mặc định là False. Adapter không tự đọc file, tìm đích hoặc xác minh hiệu lực.
Đầu ra có amendment gốc, text_diff, semantic_diff, scoring và cảnh báo tổng hợp;
đây là dữ liệu bàn giao module, chưa phải ComparisonReport/API hoàn chỉnh.

## Tuần 6–7: module và kiểm thử

- Text Diff: thêm/xóa/thay thế với offset ký tự Python, khoảng nửa mở [start, end).
  Không chuẩn hóa đầu vào trước khi tính offset. Tắt autojunk để không bỏ qua
  ký tự lặp trên văn bản dài. None ở một phía trả None; chuỗi rỗng vẫn là chuỗi
  hợp lệ cho phép so sánh; adapter giữ operation để không nhầm thiếu dữ liệu với bãi bỏ.
- Các model ngữ nghĩa/scoring dùng chung tại `src/analysis_contracts.py`, đối chiếu
  SRS 1.3. Không tuyên bố đây là schema backend đã được nhóm duyệt.
- Semantic Diff không tạo document_id/source_refs cố định. Bằng chứng được truyền
  từ đầu vào; quote chỉ được gán khi tìm thấy nguyên văn trong bằng chứng cùng document_id.
- Hai chuỗi cục bộ giống nhau, nguồn và context đủ: không tạo SemanticChange.
  AmendmentItem gốc vẫn giữ nguyên; không suy ra toàn bộ S không có sửa đổi.
- Một dạng diễn đạt tương đương được hỗ trợ: “chậm nhất vào ngày” ↔ “không muộn
  hơn ngày”, toàn bộ phần còn lại giữ nguyên. Kết quả false, aspects rỗng, LOW.
- Một dạng đổi nghĩa được hỗ trợ: đúng một số nguyên dương trong cụm
  “trong thời hạn N ngày”, toàn bộ phần còn lại giữ nguyên. TIME_QUANTITY,
  HIGH theo rubric pilot; không tự CRITICAL.
- Dạng khác, thiếu nguồn/context, đích mơ hồ, cảnh báo thượng nguồn hoặc dẫn chiếu
  thiếu: null kèm needs_review/review_reason. Không tự cho rằng không đổi nghĩa.
- Scorer bỏ MAJOR/MINOR, impact_score và rationale; trả significance,
  is_critical, reason theo SRS. Lời gọi cũ ba đối số vẫn nhận được nhưng không
  có kết luận ngữ nghĩa rõ thì không tự gán mức.

## Tuần 8–10: adapter và ca cần bàn giao

Adapter giữ instruction/evidence/context/effect_info trong amendment gốc;
OTHER_DOCUMENT không chạy phân tích; UNRESOLVED và cảnh báo không bị bỏ qua.
DERIVED không được gán new_quote như câu nguyên văn. ADD/REPEAL được giữ lại
nhưng baseline chưa tự kết luận ngữ nghĩa; Text Diff trả null khi thiếu một phía.
Ngữ nghĩa/scoring chưa biết luôn có cảnh báo, không được trình bày như hoàn thành.

Checklist bên nhận:

1. Đức Anh đối chiếu model và adapter với schema backend thực tế; chuyển mapping
   sang report chính thức và giữ cảnh báo/null. Backend hiện có import `src.pipeline`
   nhưng file đó không có trong checkout; `backend/app/pipeline.py` đang rỗng.
2. Thọ bàn giao AmendmentItem từ một cặp V1–S thật: document_id, target_unit_ids,
   before/after, after_basis, instruction và vị trí nguồn đã kiểm chứng.
3. Dũng xác nhận context, nội dung dẫn chiếu và hiệu lực; không chỉ đặt cờ để
   bỏ cảnh báo. Bộ kiểm thử hiện tại không thay thế bước này.
4. Ngọc Anh/Đức Anh chạy lại adapter trên ca thật và ghi commit/input/output.
   Chưa có bước này thì chưa xác nhận tích hợp pipeline thật hoàn thành.

## Tuần 11: rubric, giới hạn và việc tiếp theo

Danh mục 8 nhóm, ưu tiên category và ranh giới LOW/MEDIUM/HIGH/CRITICAL lấy từ
[Data annotation guide, mục 4–5](data-annotation-guide.md) và
[SRS, mục 1.3–1.4](srs.md), không dựng bộ tiêu chí cạnh tranh.

Category tổng thể chọn theo thứ tự pilot: CONSEQUENCES_SANCTIONS,
RIGHTS_DUTIES_ACTIONS, SUBJECT_OBJECT, CONDITIONS_EXCEPTIONS,
PROCEDURE_AUTHORITY, TIME_QUANTITY, SCOPE_EFFECT_TRANSITION,
DEFINITIONS_REFERENCES. Chỉ chọn trong các nhóm xác định được; giữ mọi aspects.
WORDING_ONLY chỉ dùng khi false đã xác định, không suy từ aspects rỗng.

MEDIUM cần căn cứ cách thực hiện tương đương; CRITICAL cần reviewer xác nhận
đảo chiều hoặc loại bỏ toàn bộ nghĩa vụ/quyền cốt lõi. Baseline hiện tại chưa
tự gán hai mức này. Thêm/xóa Điều và số chữ thay đổi không quyết định severity.
Không dùng mức HIGH của dạng thời hạn làm kết luận cho tiền phạt, ngày hiệu lực,
điều kiện mới, phạm vi chủ thể hoặc nhiều thay đổi độc lập.

Chưa hoàn tất: phân tích 8 nhóm tổng quát, nhiều SemanticChange độc lập,
ADD/REPEAL/DERIVED có kết luận đầy đủ, phương pháp ngữ nghĩa thứ hai,
review nhãn/pilot với Dũng–Tuấn Anh và tích hợp trên dữ liệu thật.
Không thay những phần còn thiếu bằng kết quả giả.

## Tuần 12–13: đầu ra phụ thuộc đánh giá

Chưa có số đo chất lượng pháp lý. Regression chỉ kiểm tra hành vi phần mềm.
Chưa thể công bố F1/Critical Recall, so sánh phiên bản trên tập test độc lập,
hoặc hoàn tất báo cáo/slide có số liệu trước khi nhóm khóa bộ nhãn và ứng viên.
Tuấn Anh điều phối đo; Ngọc Anh bàn giao phương pháp, lỗi và giới hạn ở tài liệu này.
LightRAG chưa được dùng và không phải điều kiện chạy baseline.
