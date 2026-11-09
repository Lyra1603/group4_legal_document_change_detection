# Báo cáo phần việc — Đỗ Tuấn Anh

## 1. Phạm vi được phân công

Theo [decision.md](decision.md), phần việc chính của Tuấn Anh gồm:

- **Semantic Change / Semantic Diff:** phân tích thay đổi về nghĩa, tạo nhận
  định có bằng chứng và giữ rõ giới hạn khi thiếu căn cứ.
- **Classifier & Scorer:** áp dụng rubric để phân loại và chấm mức tác động;
  bảo đảm `significance`, `is_critical`, `reason` và trạng thái review nhất
  quán.
- Phối hợp với Ngọc Anh ở điểm nối **Text Diff → Semantic Change**.
- Phối hợp với Đức Anh ở điểm nối **Context → Semantic Change** và với Dũng +
  Đức Anh ở điểm nối **AI Adapter ↔ Semantic Change/Scorer**.
- Phối hợp với Dũng ở điểm nối kết quả phân tích → **Pipeline/API/frontend**.

Các trường và cấu trúc đầu ra phải dùng schema chung đã được nhóm chốt, không
được tự tạo một contract khác.

## 2. Việc đã thực hiện

- Đã tạo bộ fixture tổng hợp ban đầu gồm 5 tình huống: không thay đổi, đổi
  cách diễn đạt, đổi số liệu, bổ sung Điều và bãi bỏ chế tài.
- Đã tạo nhãn kết quả dự kiến, manifest và ghi chú giải thích cho các fixture.
- Đã viết test cho Evaluator baseline, gồm Precision, Recall, F1, Critical
  Change Recall, false positive, false negative và trường hợp thiếu dữ liệu.
- Bộ test baseline đã chạy đạt **4/4 test**.
- Các fixture này được giữ ở mục đích phát triển, chưa dùng để khẳng định
  chất lượng trên benchmark độc lập.

## 3. Việc cần triển khai theo decision.md

### Semantic Diff — CN-06

Đề xuất bắt đầu bằng cách chạy song song hai baseline:

1. Rule cho các thay đổi rõ ràng như số liệu, phủ định, chủ thể, nghĩa vụ và
   thời hạn.
2. LLM có output có cấu trúc cho các ca cần phân tích ngữ cảnh sâu hơn.

Mỗi kết quả phải:

- Nhận `before/after`, chỉ dẫn sửa đổi, context và evidence đã kiểm tra.
- Tách một `SemanticChange` theo một thay đổi quy định; nhiều khía cạnh liên
  quan nằm trong `aspects`.
- Giữ `old_quote`, `new_quote`, `EvidenceRef` và `review_reason`.
- Trả `is_meaningful_change = None` khi chưa đủ căn cứ, không biến thành
  `False`.
- Không tự suy ra hiệu lực hoặc tác động từ tài liệu không có trong đầu vào.

### Classifier & Scorer — CN-07

Đề xuất dùng rubric có ví dụ ở các ranh giới gần nhau, kết hợp rule kiểm tra
nhất quán. Mô hình chỉ hỗ trợ khi có bằng chứng cải thiện.

Nguyên tắc chấm:

- Một `ScoringResult` cho mỗi `SemanticChange`, tham chiếu đúng `change_id`.
- `CRITICAL` phải đi cùng `is_critical = True`; trường hợp chưa đủ căn cứ để
  chấm phải giữ `significance = None`, `is_critical = None` và yêu cầu review.
- Không lấy số ký tự thay đổi, similarity hay retrieval score làm mức tác động.
- Thêm/xóa Điều không tự động là `CRITICAL`; phải xét nội dung và hậu quả.
- `reason` phải giải thích được căn cứ của mức chấm.

### Tự kiểm chứng — CN-10

Bộ kiểm tra cần mở rộng từ fixture tổng hợp sang các ca có căn cứ và ca lỗi:

- Chỉ đổi văn phong.
- Đổi phủ định, chủ thể, quyền/nghĩa vụ và thời hạn.
- Một thay đổi có nhiều aspects.
- Thiếu hoặc không truy được tài liệu dẫn chiếu.
- Quote không tồn tại trong nguồn.
- Output sai enum, thiếu evidence, thiếu `change_id`, timeout hoặc lỗi adapter.

Mỗi ca cần ghi input, expected, actual, lệnh chạy, phiên bản và reviewer.
Không dùng output của thuật toán làm đáp án chuẩn.

## 4. Các điểm cần phối hợp/chốt với nhóm

- Với **Ngọc Anh:** thống nhất format `TextDiffResult`, offset, vùng
  thêm/xóa/thay và cách biểu diễn trường hợp không có diff.
- Với **Đức Anh:** thống nhất điều kiện context đủ để phân tích, trạng thái
  `AVAILABLE/MISSING/UNRESOLVED` và cách truyền `AnalysisContext`.
- Với **Dũng + Đức Anh:** thống nhất cách AI Adapter nhận yêu cầu, validate
  output, xử lý retry/timeout và truyền lỗi; adapter không được tự quyết định
  nghiệp vụ.
- Với **Dũng:** thống nhất cách đưa `semantic_diff` và `scoring` vào
  `ComparisonReport.results`, giữ nguyên ID, evidence, warning và trạng thái
  `SUCCESS/PARTIAL/FAILED`.
- Với nhóm review nghiệp vụ: chốt rubric và các ca ranh giới trước khi dùng
  để đánh giá.

## 5. Trạng thái hiện tại và giới hạn

Schema chung và bộ test schema đã có trên `main`. Tuy nhiên các file chính
trong `backend/app/change_analysis/` hiện vẫn là khung, nên Semantic Diff và
Scorer chưa được nối hoàn chỉnh vào Pipeline/API. Bộ fixture baseline trước
đây dùng cấu trúc `AlignedPair`; cần được chuyển dần sang
`AmendmentItem`/`SemanticChange` theo schema mới trước khi đánh giá chính thức.

## 6. Đề nghị trưởng nhóm xác nhận

1. Cho phép dùng hybrid rule + LLM làm phương án thử nghiệm ban đầu cho CN-06.
2. Xác nhận rubric rule-based có ví dụ ranh giới là baseline cho CN-07.
3. Xác nhận bộ ca kiểm thử và reviewer cho Semantic Diff/Scorer.
4. Chốt người cung cấp fixture Text Diff và Context để bắt đầu nối module.
5. Xác nhận phạm vi tài nguyên, model và chi phí cần dùng cho AI Adapter trước
   khi chạy thử thật.
