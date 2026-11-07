 <h1 align="center">Group 4 – Legal Document Change Detection</h1>

* **Đề tài:** Project 7 – Legal Document Change Detection (Engineering / R&D )
* **Bài toán:** Phát hiện các thay đổi **CÓ Ý NGHĨA** pháp lý (Semantic Diff) giữa hai phiên bản văn bản quy phạm pháp luật Việt Nam, phân biệt rạch ròi với những thay đổi về văn phong/chính tả thông thường.

**Tài liệu dự án (Yêu cầu đọc theo thứ tự):**
1. [BRD](brd.md): mục tiêu và phạm vi.
2. [SRS](srs.md): yêu cầu và hợp đồng dữ liệu.
3. [Architecture](architecture.md): thiết kế module và luồng xử lý.
4. [Implementation Plan](implementation-plan.md): công nghệ,
   phân công và tiến độ triển khai.
5. [Module](module.md): owner, file bắt buộc và file bổ sung.
6. [Decision](decision.md): lựa chọn và hợp đồng cần chốt.
7. [Workflow](workflow.md): Git, phát triển bán song song và kiểm thử.
8. Mã nguồn: kiểm tra đúng branch trước khi sử dụng schema/implementation.

---

## 1. Minimum Architecture dự kiến

Thiết kế mục tiêu của bản đầu sử dụng request đồng bộ: backend xử lý hai file và
trả ComparisonReport trong cùng request; không dùng job nền
hoặc API polling.

Các module xử lý nằm trong `backend/app/`, gọi nhau qua hàm/hợp đồng dùng chung. Luồng: đọc/chuyển đổi và Parser → adapter/linker → context/LightRAG HTTP → Text Diff → Semantic Diff → Scorer → Pipeline tổng hợp `ComparisonReport.documents/items`. Không diff toàn bộ V1 với S; Text Diff cần nội dung trước/sau cục bộ đã được xác định.

LightRAG Server riêng qua HTTP là phương án đã chốt. Phạm vi đầu là retrieval; source registry kiểm tra nguồn, không dùng retrieval score làm mức tác động. Không triển khai Evaluator độc lập; giữ folder cũ, owner kiểm thử chéo tại từng điểm nối và Dũng điều phối đầu-cuối.

Ngọc Anh phụ trách Text Diff; Tuấn Anh phụ trách Semantic Change/Scorer; Thọ phụ trách xử lý tài liệu; Dũng phụ trách dữ liệu/docs và tích hợp/Pipeline/API; Dũng + Đức Anh phụ trách AI Adapter. Đức Anh giữ phần schema/chuẩn bị context theo phân công hiện có; người gọi/tích hợp LightRAG bổ sung sau. Xem LK-01 trong decision.md và module.md; không mặc định một owner chung cho toàn folder change_analysis.

Phát triển bán song song bằng contract/schema/fixture đã thống nhất; runtime vẫn có thứ tự. Các folder chính và file bắt buộc được cố định; owner có thể thêm file hỗ trợ trong module.

## 2. Mục tiêu Hệ thống & Chỉ số Nghiệm thu (Targets)
- Change F1 ≥ 0,90: đo khả năng phát hiện từng thay đổi nghĩa.
- Critical Change Recall ≥ 0,95: tìm đúng ít nhất 95% thay đổi
  được gán nhãn CRITICAL theo bộ tiêu chí thống nhất.
- Đo trên bộ kiểm thử độc lập; đây là mục tiêu, chưa phải kết quả đạt được.

## 3. Cấu trúc Thư mục Dự án

```text
backend/
  main.py
  app/
    api/
    schemas/
    document_processing/
    context/
    change_analysis/
    evaluation/       # Giữ cấu trúc; không triển khai Evaluator riêng
    pipeline.py
    config.py
frontend/
test/
data/
deploy/
runtime/
docs/
requirements.txt
```

Giữ cấu trúc theo branch `plan_lightrag`; không tạo lại `src/` hoặc đổi `test/` thành `tests/`. Danh sách file chính theo [Module](module.md).

## Hiện trạng triển khai

- Cấu trúc nền đã có converter PDF → DOCX, Parser, Backend nhận upload và Pipeline đọc/parse; còn nhiều file chính là khung. Khi chưa có runner phân tích, trả `ANALYSIS_NOT_CONFIGURED`, không phải báo cáo so sánh thành công.
- Schema có implementation và validator trên nhánh `feat/ducanh-backend-integration` (commit schema `36d9727`) vẫn theo envelope trước `base_document/amendment_document/reference_documents/results`; chưa mặc định tương thích hợp đồng mục tiêu `documents/items`. Chỉ tích hợp phần đã review/chuyển đổi, không ghi đè implementation bằng file trống.
- API nền dùng `doc_v1/doc_s/reference_files`; API mục tiêu dùng `base_file/amendment_file/reference_files`. Chưa coi hai giao diện tương đương nếu chưa có adapter/alias được kiểm thử.
- LightRAG HTTP đã chốt phương án, chưa đồng nghĩa đã hiện thực client và kiểm chứng vòng đời chỉ mục.
- Phân công chức năng đã chốt ở LK-01; người gọi/tích hợp LightRAG bổ sung sau. Bốn mã phân loại và contract/fixture chi tiết còn chờ; benchmark/fixture phải được review trước khi dùng làm bằng chứng chất lượng.

## 4. Hướng dẫn Cài đặt & Chạy thử (Quick Start)
- Bước 1: Cài đặt thư viện môi trường
```
pip install -r requirements.txt
```

- Bước 2: Chạy bộ kiểm thử đã hiện thực theo [Workflow](workflow.md). Nếu dùng pytest và đã bổ sung dependency:
```bash
python -m pytest test/
```
Thư mục khung hoặc không tìm thấy test không phải bằng chứng đã đạt kiểm thử. Không dùng lệnh `python -m src.pipeline` của cấu trúc cũ.

- Bước 3: Khởi chạy Backend API Server
```
uvicorn backend.main:app --reload
```
- Truy cập API Docs tại: http://127.0.0.1:8000/docs


