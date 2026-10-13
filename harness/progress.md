# Bàn giao phiên làm việc

## Trạng thái khởi tạo
- Base: nhánh `ducanh/docs`, commit `89d4712`.
- Có 6 docs và 3 cặp DOCX mẫu; code vẫn là baseline.
- Harness này hỗ trợ lập trình với AI; không thay thế Semantic Diff trong sản phẩm.
- Chưa có task tuần 6 nào được xác nhận hoàn thành bởi harness.

## Vấn đề đã biết
- SRS/BRD hỗ trợ DOCX và PDF text; Annotation Guide mục 2.2 lại ghi chỉ PDF. Cần nhóm chốt trước task Reader/API thật.
- Schema code chưa theo SRS mới có ChangeAspect/DocumentIdentity.
- API baseline nhận hai chuỗi text; chưa có upload, Reader, Text Diff riêng hoặc UI.
- Evaluator baseline chưa đủ để nghiệm thu chất lượng; smoke test không đo metric.
- Scorer baseline có nhánh DELETED trả HIGH nhưng is_critical=true; cần xử lý trong task Scorer.

## Task nên bắt đầu
- W6-SCHEMA: tạo schema theo SRS và fixture báo cáo giả định để các thành viên phát triển song song.

## Mẫu cập nhật sau mỗi phiên
- Task và commit/diff được kiểm tra: W6-SCHEMA (chưa commit, đang review)
- Hành vi đã thực hiện:
  - Tạo dataclass schema trong `src/schemas.py` theo SRS §1.1–§1.7: Clause, AlignedPair, ChangeAspect, SemanticChange, SemanticDiffResult, ScoringResult, ExtractedDocument, TextDiffResult, PairResult, ProcessingIssue, DocumentIdentity, ComparisonReport.
  - Bảo đảm các trường bắt buộc và ràng buộc null/chưa xác định (is_meaningful_change, significance, is_critical, category nhận None khi needs_review=True).
  - Giữ Legacy TypedDict aliases (LegacyClause, LegacyAlignedPair, ...) để baseline modules giữ nguyên tính tương thích.
  - Tạo `tests/fixtures.py`: factory cho SUCCESS (ví dụ thời hạn 30→15 ngày), PARTIAL (lỗi scoring=None kèm ProcessingIssue), undetermined (thay đổi chưa rõ nghĩa), ADDED, DELETED. Khớp offset ký tự thực tế [29, 31).
  - Tạo `tests/test_schema_contract.py`: 48 behavioral tests (kiểm tra cấu trúc, liên kết change_id giữa SemanticChange và ScoringResult, đối chiếu bằng chứng old_quote/new_quote và source_refs, khớp offset TextChange, phân biệt null vs []).
- Lệnh kiểm tra và kết quả:
  - `.\.venv\Scripts\python.exe scripts/harness.py check`: PASS (9 Python files + baseline smoke)
  - `.\.venv\Scripts\python.exe scripts/harness.py verify W6-SCHEMA`: 48 tests OK
  - `.\.venv\Scripts\python.exe scripts/harness.py status`: exit 0
- Phần còn mock/chưa xử lý:
  - Pipeline runtime hiện tại vẫn trả về legacy flat dict; chưa chuyển sang sinh ComparisonReport trực tiếp (sẽ thực hiện qua các task W6-UPLOAD, W6-READER, W6-DIFF).
  - Reader (ExtractedDocument/SourceBlock) chỉ mới định nghĩa contract, chưa có parser đọc file thật.
- Vấn đề đang chặn: Không có.
- Bước tiếp theo: Chờ phê duyệt review W6-SCHEMA trước khi bắt đầu W6-UPLOAD hoặc W6-DIFF.

Giữ ghi chú ngắn, phản ánh code thực tế; không ghi dữ liệu đầu vào đầy đủ hoặc bí mật.
