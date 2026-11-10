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

Hiển thị bằng chứng có tài liệu/vị trí nguồn là chức năng chính.

Nhận xét là chức năng dự kiến sau khi các chức năng cốt lõi hoàn thiện, chỉ liệt kê trong phạm vi mở rộng, không là module chính hoặc điều kiện nghiệm thu bản đầu. Hai loại: (1) nhận xét sau phiên được lưu để phục vụ phát triển; (2) nhận xét trong phiên kết hợp nhận xét có sẵn để xem xét và cập nhật kết luận. Khi triển khai, giữ phân biệt kết luận ban đầu/cập nhật và căn cứ thay đổi; không tự coi nhận xét là gold/nhãn huấn luyện. Cách lưu, API, định danh, nguồn nhận xét có sẵn và cơ chế kết hợp chưa chốt; chưa mở rộng schema chung.

Thiết kế mục tiêu của bản đầu sử dụng request đồng bộ: backend xử lý hai file và
trả ComparisonReport trong cùng request; không dùng job nền
hoặc API polling.

Sau adapter, Context chuẩn bị chunk, registry và nhập chỉ mục song song nhánh Linker xác định đích/trước-sau → Text Diff. Điểm ghép chờ index sẵn sàng và TextDiffResult, kết hợp chỉ dẫn, trước/sau và vùng chữ đổi để tạo query. LightRAG truy xuất qua HTTP, registry kiểm tra nguồn/quote rồi mới chuyển sang Semantic. Semantic dùng rule trước, model khi cần; Scorer và Pipeline nhận kết quả cùng bằng chứng/cảnh báo để tổng hợp report.

LightRAG Server riêng qua HTTP là phương án đã chốt. Phạm vi đầu là retrieval; source registry kiểm tra nguồn, không dùng retrieval score làm mức tác động. Không triển khai Evaluator độc lập; giữ folder cũ, owner kiểm thử chéo tại từng điểm nối; Dũng điều phối tích hợp/Pipeline/API, Đức Anh điều phối kế hoạch đánh giá.

Ngọc Anh phụ trách Text Diff; Tuấn Anh phụ trách Semantic Change/Scorer; Thọ phụ trách xử lý tài liệu; Dũng phụ trách dữ liệu/docs và tích hợp/Pipeline/API; Dũng + Đức Anh phụ trách AI Adapter. Đức Anh phụ trách schema, context và điều phối kế hoạch đánh giá; Dũng + Đức Anh phụ trách gọi/tích hợp LightRAG. Xem LK-01 trong decision.md và module.md; không mặc định một owner chung cho toàn folder change_analysis.

Phát triển bán song song bằng contract/schema/fixture đã thống nhất; runtime vẫn có thứ tự. Các folder chính và file bắt buộc được cố định; owner có thể thêm file hỗ trợ trong module.

## 2. Mục tiêu hệ thống và ngưỡng đánh giá dự tính
- Change F1 ≥ 90% (dự tính): đo khả năng phát hiện từng thay đổi nghĩa.
- Critical Change Recall ≥ 95% (dự tính): tìm đúng thay đổi được gán nhãn CRITICAL theo bộ tiêu chí thống nhất.
- Các ngưỡng Change F1 ≥ 90% và Critical Change Recall ≥ 95% là dự tính và có thể thay đổi sau khi hoàn thiện test_evaluation_plan.md; chưa phải ngưỡng nghiệm thu chính thức.
- Đo trên bộ kiểm thử độc lập; báo cáo kết quả thực tế và giới hạn, chưa coi các mức dự tính là chất lượng đã đạt. Matching đánh giá áp dụng 1–1 trước; 1–n bổ sung sau khi hoàn thành 1–1.

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

Nhánh `ducanh_bachdung/integrate_LightRAG`, commit `e47e049ada29fdab95dcd39a5d0ad14d98c3b411`, đã có client HTTP, chunk builder, source registry, context builder và `context/semantic_bridge.py`. Có demo DOCX với adapter, Linker hẹp, Text Diff, baseline Semantic/Scorer và report PARTIAL. Demo chạy riêng bằng `backend.demo:app`; `backend.main:app` vẫn chưa cấu hình runner mặc định. Frontend demo là HTML/CSS/JavaScript, chưa thay định hướng frontend chính thức.

Chưa kiểm chứng LightRAG Server/model/index/KG thật; web demo tắt LightRAG. Bridge hiện chạy Context (gồm retrieval khi cấu hình) song song Text Diff rồi ghép trước Semantic; còn tách index/query và dùng Text Diff tạo query để khớp luồng mục tiêu mới. Rule baseline đã có, model fallback chưa tích hợp. Kết quả nhánh thử nghiệm không tự xác nhận đã merge main/nghiệm thu.

Căn cứ: [báo cáo tích hợp](https://github.com/Lyra1603/group4_legal_document_change_detection/blob/e47e049ada29fdab95dcd39a5d0ad14d98c3b411/docs/lightrag-integration-report.md), [demo và giới hạn](https://github.com/Lyra1603/group4_legal_document_change_detection/blob/e47e049ada29fdab95dcd39a5d0ad14d98c3b411/docs/local-web-demo.md). Kết quả test trong các báo cáo chưa được chạy lại trong đợt sửa tài liệu này.

Các gạch đầu dòng dưới đây mô tả nền main/schema, không phải hiện trạng đầy đủ của nhánh thử nghiệm.

- Cấu trúc nền đã có converter PDF → DOCX, Parser, Backend nhận upload và Pipeline đọc/parse; còn nhiều file chính là khung. Khi chưa có runner phân tích, trả `ANALYSIS_NOT_CONFIGURED`, không phải báo cáo so sánh thành công.
- Nhóm đã chốt dùng schema và validator của Đức Anh tại commit b6a13f98b9a7357b9fbb0936aba6bda065d03fcb. Schema đã merge qua [PR #2](https://github.com/Lyra1603/group4_legal_document_change_detection/pull/2) vào main (`a8a906a`); code nhập nguyên bản vào backend/app/schemas; adapter nguồn/Clause và wiring Pipeline còn cần triển khai. Xem [SRS mục 1.7](srs.md).
- API main dùng `doc_v1/doc_s/reference_files`; đổi sang `base_file/amendment_file` hoặc hỗ trợ alias vẫn là đề xuất chưa chốt ở LK-11, chưa có trong router.
- LightRAG HTTP đã chốt phương án, chưa đồng nghĩa đã hiện thực client và kiểm chứng vòng đời chỉ mục.
- Phân công chức năng đã chốt ở LK-01: Dũng + Đức Anh gọi/tích hợp LightRAG; Đức Anh phụ trách context và điều phối kế hoạch đánh giá. Dùng tám field_group/category theo schema chung; rubric và fixture nghiệp vụ còn cần review; benchmark/fixture phải được review trước khi dùng làm bằng chứng chất lượng.

## 4. Kiểm tra schema độc lập

Chạy từ repo root trong venv Python 3.11 trở lên (đã kiểm tra 3.12.14):

```bash
python -m pip install -r requirements.txt
python -m pip check
python -m unittest discover -s test/schema_suite -p "test_*.py" -v
```

requirements.txt ghim pydantic==2.13.4 và typing_extensions==4.16.0 cho schema. Kết quả thực tế: Python 3.12.14, 51 test: 49 đạt và 2 expected failures; chi tiết ở [báo cáo kiểm thử](schema-verification-report.md). Hai expected failures ghi nhận giới hạn chưa kiểm tra ID toàn báo cáo và TextDiff reconstruction, không phải đã sửa. requirements.txt chỉ khai báo dependency schema. API/PDF còn cần dependency runtime của module tương ứng; xem [hướng dẫn schema và runtime](schema-integration.md). Khi môi trường API đã được chuẩn bị, lệnh nền vẫn là `python -m uvicorn backend.main:app`; POST /api/compare nhận doc_v1/doc_s/reference_files. Chưa có analysis_runner thì trả FAILED/ANALYSIS_NOT_CONFIGURED, không tự có kết quả phân tích vì đã thêm schema.
