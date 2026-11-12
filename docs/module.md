# MODULE — Phân công, cấu trúc và bàn giao

**Dự án:** Legal Document Change Detection — POCS, Nhóm 4
**Phiên bản:** Bản đầu tiên
**Trạng thái:** Đang hoàn thiện theo các quyết định trong [decision.md](decision.md)

## 1. Mục đích và quy định chung

**Nền đã chạy và công việc tiếp theo:** xem [common-baseline.md](common-baseline.md). Lấy tài liệu Dũng `6dbda8d` làm thiết kế; code `c192f43` đã có Adapter, Linker hẹp, Text Diff, Context và demo runner. Owner tiếp tục review/mở rộng code đó, không thay bằng file khung. Demo chung chạy `backend.demo:app`, LightRAG/model tắt; ADD/REPEAL/nhiều đích và query từ diff là công việc sau merge. Fixture là kỳ vọng kỹ thuật, không chứng minh module hiện đã tạo được mọi output mẫu.

Owner từng module tự xử lý và báo lỗi thuộc phần mình; chuyển bằng chứng có nguồn cùng lỗi/cảnh báo và phạm vi bị ảnh hưởng cho module nhận đầu ra theo contract chung. Bên nhận kiểm tra dữ liệu, không bỏ cảnh báo hoặc biến thiếu căn cứ thành không có thay đổi. Pipeline tổng hợp trạng thái báo cáo, không thay owner xử lý lỗi nội bộ.

Nhận xét của người dùng thuộc phạm vi mở rộng. Xem [SRS](srs.md#9-phạm-vi-mở-rộng) để tra phạm vi.

Tài liệu ghi nhiệm vụ, người chịu trách nhiệm, file chính, điểm nối và điều kiện bàn giao từng module. Các lựa chọn và nội dung đang bàn được ghi trong decision.md; module.md chỉ ghi lựa chọn đã chốt, hoặc đánh dấu rõ phần còn chờ và mã quyết định liên quan.

- Cấu trúc thư mục chuẩn lấy từ `main`, xem [Architecture](architecture.md#3-cấu-trúc-mã-nguồn-và-dữ-liệu). Quy trình thay đổi đường dẫn hoặc giao diện chung nằm trong [Workflow](workflow.md).
- File bắt buộc là file chính được cố định đường dẫn và trách nhiệm. Được sửa implementation; không tự đổi giao diện công khai, xóa/đổi tên/chuyển vị trí.
- File hỗ trợ do thành viên bổ sung trong module để chia nhỏ code, hỗ trợ file chính hoặc cải thiện phương pháp. Owner module review; không tự tạo dependency mới lên module khác hoặc thay hợp đồng chung.
- Mỗi module/chức năng được phân công có người chịu trách nhiệm cuối cùng và có thể có người khác tham gia. Với folder chứa nhiều chức năng như change_analysis, áp dụng owner theo từng chức năng đã chốt ở LK-01; không tự gán owner toàn folder. Mỗi task có một người chịu trách nhiệm chính.
- Owner không phải người duy nhất được code. Người phụ trách chức năng chủ động triển khai trong ranh giới đã chốt; người nhận đầu ra review hợp đồng và cách sử dụng.
- Không tạo file trống ghi đè implementation đã có. Danh sách file bắt buộc không phải danh sách duy nhất được phép tồn tại.
- LightRAG Server riêng qua HTTP là phương án đã chốt; API/release/cấu hình cụ thể vẫn cần xác nhận.
- Không triển khai Evaluator độc lập. Giữ folder/file cũ để không tự đổi cấu trúc; kiểm thử do owner từng phần và hai owner tại điểm nối đảm nhiệm, cần có cả kiểm tra toàn luồng.

## 2. Tổng quan module và phân công

Đường dẫn module dưới đây tính từ backend/app/.

| Module | Owner/phân công hiện có | Người tham gia và review | Trạng thái đặc tả |
| --- | --- | --- | --- |
| api/ | Dũng | Owner Pipeline, frontend và các bên dùng API | Báo cáo đã chốt theo schema chung; endpoint/upload và mapping còn chờ |
| schemas/ | Đức Anh | Owner bên cung cấp và bên nhận từng kiểu dữ liệu | Hợp đồng chung đã chọn; validator đã merge qua PR #2, wiring Pipeline còn chờ |
| document_processing/ | Thọ | Đức Anh, Ngọc Anh, Tuấn Anh theo điểm nối; Dũng review nguồn/nghiệp vụ | ExtractedDocument/Clause/AmendmentItem đã chốt; mapping cây native và thuật toán còn chờ |
| context/ | Đức Anh phụ trách context; Dũng + Đức Anh phụ trách gọi/tích hợp LightRAG | Thọ cung cấp nguồn; Ngọc Anh/Tuấn Anh nhận ngữ cảnh; Dũng nhận phần tích hợp | HTTP đã chốt; chi tiết LightRAG chờ LK-13 sau các quyết định còn lại |
| change_analysis/ | Chốt theo chức năng ở LK-01, không gán owner chung toàn folder | Ngọc Anh: Text Diff; Tuấn Anh: Semantic Change/Scorer; Dũng + Đức Anh: AI Adapter | Phân công và kiểu dữ liệu chung đã chốt; thuật toán/giao diện gọi chi tiết còn chờ |
| evaluation/ | Không triển khai như module riêng | Test chuyển sang các owner và test/ | Giữ cấu trúc, không giao lại đầu việc Evaluator |

| Thành phần ngoài các folder trên | Người phụ trách | Ghi chú |
| --- | --- | --- |
| backend/main.py | Dũng | Khởi tạo ứng dụng, đăng ký thành phần backend |
| backend/app/pipeline.py | Dũng | Điều phối và tổng hợp báo cáo |
| backend/app/config.py | Dũng điều phối cấu hình tích hợp/API; Đức Anh phối hợp phần kỹ thuật liên quan | Dũng + Đức Anh phối hợp cấu hình LightRAG |
| frontend/ | Tuấn Anh theo phân công hiện có | Cần xác nhận khối lượng sau khi nhận thêm Semantic Diff; không tự chuyển người |
| Dữ liệu, nghiệp vụ, nhãn/fixture nghiệp vụ và tài liệu tổng quát | Dũng | Owner liên quan phối hợp, người review nhãn khác người tạo |

## 3. Đặc tả từng module

### 3.1. api/

**Owner:** Dũng

**Nhiệm vụ và ranh giới:** Nhận yêu cầu, kiểm tra đầu vào cấp HTTP, gọi Pipeline và trả báo cáo/lỗi. Không thực hiện thuật toán phân tích pháp lý trong router.

| File chính | Trách nhiệm |
| --- | --- |
| compare.py | File khung mục tiêu để tách router; hiện route POST /api/compare vẫn ở backend/main.py. Trách nhiệm dự kiến: nhận file/tham số, gọi Pipeline, ánh xạ lỗi HTTP. |

**Đầu vào:** File V1, S, tài liệu tham chiếu và tham số upload theo hợp đồng đã chốt.

**Đầu ra:** ComparisonReport với base_document/amendment_document/reference_documents/results theo schema chung; nguồn cần đọc và lỗi có cấu trúc. Mã HTTP tách khỏi trạng thái nghiệp vụ; không thêm dữ liệu nhận xét vào báo cáo AI.

**Bên kết nối:** Pipeline, schemas, frontend.

**File hỗ trợ:** được thêm trong module theo quy định mục 1; tên/cấu trúc nội bộ chỉ cố định khi owner đề xuất và các bên liên quan thống nhất.

**Điều kiện bàn giao:** Fixture upload hợp lệ/lỗi, báo cáo đầy đủ/một phần/thất bại; frontend và Pipeline cùng xác nhận dùng được.

**Quyết định liên quan:** LK-02, LK-11, LK-12. Tra cứu trong [decision.md](decision.md).

### 3.2. schemas/

**Owner:** Đức Anh

**Nhiệm vụ và ranh giới:** Giữ định nghĩa dữ liệu dùng chung và quy tắc kiểm tra tại ranh giới module. Không tự quyết định kết luận nghiệp vụ hoặc thuật toán của module khác.

| File chính | Trách nhiệm |
| --- | --- |
| contracts.py | Hợp đồng TypedDict chung theo commit Đức Anh được nhóm chọn. |
| validation.py | validate_extracted_document kiểm tra metadata, blocks, source_ref và nội dung đọc được. |
| report_validation.py | validate_payload, validate_sources, validate_amendment, validate_report kiểm tra ranh giới theo hợp đồng chung. |

**Đầu vào:** Các quyết định hợp đồng, input/output mẫu và quy tắc nghiệp vụ đã chốt.

**Đầu ra:** Schema/validator dùng chung, phiên bản hợp đồng và fixture hợp lệ/không hợp lệ.

**Bên kết nối:** Mọi module trao đổi dữ liệu; mỗi owner review kiểu dữ liệu mình cung cấp hoặc nhận.

**File hỗ trợ:** được thêm trong module theo quy định mục 1; tên/cấu trúc nội bộ chỉ cố định khi owner đề xuất và các bên liên quan thống nhất.

**Điều kiện bàn giao:** Schema và fixture nhất quán với decision; validator phát hiện ca sai liên quan. contracts.py, validation.py, report_validation.py giữ nguyên code căn cứ; fixture và test độc lập ở test/schema_suite. Pipeline chưa được nối validation; kho nguồn/Clause và thứ tự gọi theo [SRS mục 1.7](srs.md).

**Quyết định liên quan:** LK-02 đến LK-12. Tra cứu trong [decision.md](decision.md).

### 3.3. document_processing/

**Owner:** Thọ

**Nhiệm vụ và ranh giới:** Đọc/chuyển đổi, parse cây tài liệu, chuẩn hóa nguồn và trích/liên kết chỉ dẫn sửa đổi. Không phân tích nghĩa thay Semantic Diff hoặc coi V1 và S là hai bản đầy đủ để diff toàn văn.

| File chính | Trách nhiệm |
| --- | --- |
| pdf_to_docx.py | Chuyển PDF có lớp chữ sang DOCX khi cần, giữ thông tin chuyển đổi và cảnh báo. |
| parser/legal_structure_parser.py | Parse Điều/Khoản/Điểm, bảng và nội dung ngoài Điều; giữ cây và nguồn. |
| document_adapter.py | Chuẩn hóa output Parser sang hợp đồng các bên nhận; giữ định danh, vai trò và vị trí nguồn. |
| amendment_linker.py | Trích yêu cầu trong S, liên kết đích V1, xác định nội dung trước/sau cục bộ và thông tin hiệu lực/chuyển tiếp có căn cứ. |

**Đầu vào:** V1, S và tài liệu tham chiếu đã kiểm tra định dạng; metadata định danh/vai trò.

**Đầu ra:** Cây/nguồn chuẩn hóa; chỉ dẫn sửa đổi, vị trí đích, nội dung cục bộ, hiệu lực và cảnh báo theo schema chung; adapter từ cây native còn cần hiện thực.

**Bên kết nối:** Thọ → Đức Anh ở nguồn/context; Thọ → Dũng ở Pipeline/API; Thọ → Ngọc Anh/Tuấn Anh qua dữ liệu trước/sau và căn cứ.

**File hỗ trợ:** được thêm trong module theo quy định mục 1; tên/cấu trúc nội bộ chỉ cố định khi owner đề xuất và các bên liên quan thống nhất.

**Điều kiện bàn giao:** Có fixture file thật/cây mong đợi, bảng/outside, chỉ dẫn mơ hồ và sai văn bản đích. Số lượng Điều/Khoản/Điểm kỳ vọng được review độc lập từ nguồn; summary tự đếm không chứng minh Parser không bỏ sót.

**Quyết định liên quan:** CN-01, CN-02, LK-03, LK-04, LK-05, LK-12. Tra cứu trong [decision.md](decision.md).

### 3.4. context/

File hỗ trợ trên nhánh: `semantic_bridge.py` ghép Context/Text Diff trước Semantic; cần điều chỉnh điểm ghép query mới. Chuẩn bị index nhận nguồn adapter; query nhận chỉ dẫn/trước-sau/TextDiffResult. Giữ owner/schema chung.

**Owner:** Đức Anh phụ trách context; Dũng + Đức Anh phụ trách gọi/tích hợp LightRAG. LK-13 chốt sau các quyết định còn lại.

**Nhiệm vụ và ranh giới:** Chuẩn bị chunk, truy xuất LightRAG và chọn ngữ cảnh/căn cứ cho phân tích. LightRAG phục vụ retrieval; không tự thay linker, Semantic Diff hoặc Scorer.

| File chính | Trách nhiệm |
| --- | --- |
| chunk_builder.py | Đức Anh: tạo đoạn đủ nghĩa, giữ metadata và liên kết nguồn. |
| source_registry.py | Đức Anh: ánh xạ chunk/kết quả truy xuất về đúng document_id và nguyên văn nguồn. |
| lightrag_client.py | Dũng + Đức Anh: gọi LightRAG Server qua HTTP: nhập, theo dõi sẵn sàng, truy vấn, xử lý lỗi và dọn dữ liệu. |
| context_builder.py | Đức Anh: lập truy vấn, chọn/kiểm tra căn cứ, cung cấp ngữ cảnh và nhu cầu tham chiếu thiếu/chưa rõ. |

**Đầu vào:** Tài liệu/cây/nguồn và yêu cầu sửa đổi đã chuẩn hóa.

**Đầu ra:** Ngữ cảnh có nguồn, tình trạng tài liệu tham chiếu, cảnh báo và trạng thái retrieval/index theo hợp đồng.

**Bên kết nối:** Thọ cung cấp nguồn; Ngọc Anh/Tuấn Anh dùng context; Pipeline quản lý luồng và việc dọn.

**File hỗ trợ:** được thêm trong module theo quy định mục 1; tên/cấu trúc nội bộ chỉ cố định khi owner đề xuất và các bên liên quan thống nhất.

**Điều kiện bàn giao:** Kiểm chứng nhập/sẵn sàng/query/mapping/cách ly/xóa trên release cố định; không coi query rỗng là tài liệu chắc chắn thiếu, không dùng retrieval score làm significance.

**Quyết định liên quan:** CN-03, CN-04, LK-04, LK-06, LK-12, LK-13. Tra cứu trong [decision.md](decision.md).

### 3.5. change_analysis/

**Owner:** Phân theo chức năng đã chốt tại LK-01: Ngọc Anh — Text Diff; Tuấn Anh — Semantic Change/Scorer; Dũng + Đức Anh — AI Adapter. Không tự gán owner chung toàn folder.

**Nhiệm vụ và ranh giới:** Phân tích chữ và nghĩa trên nội dung trước/sau cục bộ có ngữ cảnh; phân loại và chấm tác động theo bằng chứng. Không tự dựng dữ liệu nguồn hoặc xóa cảnh báo của bước trước.

| File chính | Trách nhiệm |
| --- | --- |
| text_diff.py | Ngọc Anh: xác định vùng INSERT/DELETE/REPLACE theo hai chuỗi cục bộ. |
| semantic_diff.py | Tuấn Anh: rule trước, model khi cần; xác định Semantic Change, giải thích, bằng chứng và trường hợp chưa đủ căn cứ. |
| scorer.py | Tuấn Anh: phân loại/chấm mức tác động theo kết quả ngữ nghĩa và rubric chung. |
| ai_adapter.py | Dũng + Đức Anh: đóng gói gọi mô hình và kiểm tra output; chi tiết cách gọi/giao diện còn chờ CN-08/LK-02. |

**Đầu vào:** Yêu cầu sửa đổi có nội dung trước/sau và context; Text Diff được cung cấp cho Semantic Diff khi có.

**Đầu ra:** TextDiffResult, SemanticDiffResult và list[ScoringResult] theo contracts.py; Pipeline đặt vào AmendmentResult trong ComparisonReport.results.

**Bên kết nối:** Ngọc Anh → Tuấn Anh ở Text Diff; Semantic Change → Scorer là điểm nối nội bộ của Tuấn Anh; các phần → Dũng ở Pipeline/API; Dũng + Đức Anh cung cấp AI Adapter.

**File hỗ trợ:** được thêm trong module theo quy định mục 1; tên/cấu trúc nội bộ chỉ cố định khi owner đề xuất và các bên liên quan thống nhất.

**Điều kiện bàn giao:** Các điểm nối Text Diff → Semantic Diff → Scorer có contract/fixture và test output thật; dữ liệu đủ/thiếu căn cứ, chỉ đổi diễn đạt và lỗi mô hình không bị nhầm thành không có thay đổi.

**Quyết định liên quan:** CN-05, CN-06, CN-07, CN-08, LK-01, LK-07, LK-08, LK-09, LK-10, LK-11, LK-12. Tra cứu trong [decision.md](decision.md).

### 3.6. evaluation/

**Owner:** Không phân công triển khai Evaluator độc lập.

**Nhiệm vụ và ranh giới:** Giữ thư mục để không thay cấu trúc đã chốt. Trách nhiệm kiểm thử vẫn tồn tại ở từng module, điểm nối và toàn luồng.

| File chính | Trách nhiệm |
| --- | --- |
| evaluator.py | Giữ file hiện có; không thuộc danh sách bắt buộc phải hoàn thiện ở giai đoạn này. |

**Đầu vào:** Không thiết lập hợp đồng runtime mới cho module này.

**Đầu ra:** Không có đầu ra bắt buộc từ Evaluator riêng; phép đo nếu cần thực hiện qua test/script đã thống nhất.

**Bên kết nối:** Đức Anh điều phối kế hoạch đánh giá; các owner thực hiện kiểm tra phần mình và kiểm tra chéo; thành viên khác kiểm tra phụ; Dũng phụ trách tích hợp/Pipeline/API.

**File hỗ trợ:** được thêm trong module theo quy định mục 1; tên/cấu trúc nội bộ chỉ cố định khi owner đề xuất và các bên liên quan thống nhất.

**Điều kiện bàn giao:** Có người chịu trách nhiệm kiểm tra từng điểm nối và toàn luồng; bỏ Evaluator không được hiểu là bỏ expected output, nhãn chuẩn hoặc phép đo khi báo cáo yêu cầu.

**Quyết định liên quan:** LK-01. Tra cứu trong [decision.md](decision.md).

## 4. Đầu vào–đầu ra và các điểm nối

Phiên 1 giữ toàn văn cùng một đơn vị đối chiếu ở cả hai trạng thái. Với sửa nội dung của Điểm, Khoản hoặc Điều hiện có, đơn vị đối chiếu là toàn văn đơn vị đó. Khi thêm hoặc bãi bỏ cả một đơn vị, dùng đơn vị chứa nhỏ nhất còn tồn tại ở hai phía, ví dụ toàn Điều khi thêm hoặc bãi bỏ một Khoản. Vị trí đích vẫn ghi chính xác Điểm, Khoản hoặc Điều mà S chỉ ra. Nếu chỉ dẫn có nhiều đích, giữ đủ đích và căn cứ cho từng đích. Xem [LK-05](decision.md#lk-05--chỉ-dẫn-sửa-đổi-và-nội-dung-trướcsau) để tra quyết định và điểm còn mở.

| Điểm nối | Bên giao → bên nhận | Đầu vào | Đầu ra | Điều kiện | Fixture và quyết định |
| --- | --- | --- | --- | --- | --- |
| Adapter → Linker | Thọ → Thọ | Kho `ExtractedDocument`, `Clause` của V1 và chỉ dẫn từ S | Danh sách `AmendmentItem` giữ đủ vị trí, nguồn và trước/sau | Giữ chỉ dẫn kèm lý do nếu chưa tìm được đích | [Ca mẫu](../data/module_handoff_fixtures/adapter_to_linker/deadline_reduction.json) · LK-03–05 |
| Adapter → Context | Thọ → Đức Anh | Kho tài liệu chuẩn hóa và nguồn | Chunk, ánh xạ nguồn và trạng thái chỉ mục. Fixture minh họa trạng thái sẵn sàng | Có thể chuẩn bị chỉ mục song song với Linker | [Ca mẫu](../data/module_handoff_fixtures/adapter_to_context/deadline_reduction.json) · LK-03/04/06/13 |
| Linker → Text Diff | Thọ → Ngọc Anh | `AmendmentItem` có hai trạng thái đủ căn cứ | `TextDiffResult` và offset theo hai chuỗi | Bỏ qua item chưa đủ nội dung để diff | [Ca mẫu](../data/module_handoff_fixtures/document_to_text_diff/deadline_reduction.json) · LK-04/05/07 |
| Text Diff + chỉ mục → Ghép query | Ngọc Anh + Đức Anh → Đức Anh + Dũng | Chỉ dẫn, trước/sau, `TextDiffResult` và chỉ mục đã sẵn sàng | Truy vấn cho đúng `amendment_id` | Chờ đủ dữ liệu ở hai nhánh. Ghi rõ lý do nếu bỏ qua | [Ca mẫu](../data/module_handoff_fixtures/text_diff_and_index_to_query/deadline_reduction.json) · LK-06/07/13 |
| Retrieval → Context | Dũng + Đức Anh → Đức Anh | `AmendmentItem` và ứng viên nguồn đã ánh xạ | `AmendmentItem` bổ sung `AnalysisContext` và căn cứ đã đối chiếu | Giữ lý do khi kết quả truy xuất rỗng, lỗi hoặc thiếu căn cứ | [Ca mẫu](../data/module_handoff_fixtures/retrieval_to_context/deadline_reduction.json) · LK-04/06/12/13 |
| Context + Text Diff → Semantic Diff | Đức Anh + Ngọc Anh → Tuấn Anh | `AmendmentItem` có context và `TextDiffResult` nếu đã tạo | `SemanticDiffResult` khớp `amendment_id` | Chạy rule trước và dùng model khi cần theo CN-06. Báo giới hạn khi thiếu căn cứ | [Ca mẫu](../data/module_handoff_fixtures/context_and_text_diff_to_semantic/deadline_reduction.json) · CN-06/LK-06–09/12 |
| Semantic Diff → Scorer | Tuấn Anh → Tuấn Anh | `AmendmentItem` và `SemanticDiffResult` | Danh sách `ScoringResult` nối theo `change_id` | Giữ mức độ chưa xác định theo LK-10. Có reviewer khác khi kiểm thử chéo | [Ca mẫu](../data/module_handoff_fixtures/semantic_to_scorer/deadline_reduction.json) · LK-09/10/12 |
| Phân tích → Pipeline/API | Các owner → Dũng | Định danh tài liệu, kết quả từng item, cảnh báo và lỗi | `ComparisonReport` qua validator | Giữ item có bước chưa chạy và ghi lý do | [Ca mẫu](../data/module_handoff_fixtures/analysis_to_pipeline/deadline_reduction.json) · LK-11/12 |
| API → Frontend | Dũng → Tuấn Anh | `ComparisonReport` hoặc lỗi HTTP theo API | Hiển thị trước/sau, kết luận, trạng thái và bằng chứng | Hiện `quote` và vị trí đã trả. Mục chưa xử lý phải nhìn thấy được | [Ca mẫu](../data/module_handoff_fixtures/api_to_frontend/deadline_reduction.json) · LK-11/12 |

Các fixture mô tả hợp đồng tại từng điểm nối. Trạng thái chỉ mục, câu query và dữ liệu hiển thị trong fixture dùng để mô phỏng, theo [README của bộ fixture](../data/module_handoff_fixtures/README.md). Tên hàm và chi tiết tích hợp còn mở được chốt khi có kết quả chạy.

Binding code hiện tại: `adapt_documents(parsed) -> BoundaryData(documents, clauses, units)`; `link_amendments(boundary) -> (items, issues)`; `compute_text_diff(item)`; `detect_semantic_changes(item, text_diff)`; `score_changes(semantic)` (chưa nhận item riêng như wrapper fixture); runner `(parsed, comparison_id, deadline) -> AnalysisOutcome`. Fixture đóng gói input không quy định chữ ký hàm. Khi nối dùng adapter tại bên gọi, không sửa contract TypedDict hoặc buộc mọi module đổi hàm theo tên khóa JSON. Bridge Context/Text Diff hiện tại chưa thực hiện điểm ghép query mục tiêu.

## 5. Phối hợp triển khai bán song song

Thực hiện quy trình chốt → code song song → kiểm thử chéo → tích hợp theo [workflow.md](workflow.md). Các cặp cụ thể theo LK-02 trong decision.md. File này xác định nhiệm vụ/đầu ra từng module, không định nghĩa một quy trình vận hành khác.

## 6. Kiểm thử và điều kiện hoàn thành

Checklist, trách nhiệm hai bên, cách báo lỗi và điều kiện merge theo [workflow.md](workflow.md). Bàn giao module vẫn cần code, input/output mẫu, lệnh/kết quả kiểm tra và giới hạn. Các điều kiện đặc thù trong mục 3 là căn cứ kiểm tra, không thay quy trình kiểm thử chung. Thiết kế đánh giá và phép đo theo [Kế hoạch kiểm thử và đánh giá](test_evaluation_plan.md).

## 7. Trạng thái hoàn thiện

File này chỉ được coi hoàn thiện khi toàn bộ quyết định có liên quan trong decision.md đã chốt và kết luận được phản ánh đúng vào đặc tả module. Một module có thể đủ đặc tả trước các module khác nếu các quyết định ảnh hưởng trực tiếp đã chốt; không được xem phần còn chờ là phương án chính thức.

Phân biệt ba trạng thái: đủ đặc tả, đã hiện thực và đã tích hợp/kiểm thử. Việc chốt tài liệu không tự xác nhận code đã có hoặc kiểm tra đã đạt.

| Hạng mục | Trạng thái hiện tại | Việc cần hoàn thiện |
| --- | --- | --- |
| Folder chính và danh sách file chính | Đã có cấu trúc làm căn cứ | Review phạm vi file và giữ ổn định đường dẫn |
| LightRAG qua HTTP | Đã chốt phương án | CN-03/CN-04 và LK-13 còn chi tiết kỹ thuật |
| Semantic Diff giao Tuấn Anh; bỏ Evaluator riêng | Đã chốt phân công chức năng | Hoàn thiện contract/fixture và trách nhiệm test |
| Phân công change_analysis/AI Adapter | Đã chốt theo chức năng | LK-01; CN-05/CN-06/CN-07/CN-08 còn lựa chọn triển khai |
| Người gọi/tích hợp LightRAG | Đã chốt Dũng + Đức Anh | Chi tiết kỹ thuật còn chờ CN-04/LK-13; LK-13 chốt sau các quyết định còn lại |
| Hợp đồng dữ liệu và báo cáo | Đã chốt dùng schema Đức Anh | LK-08 đến LK-11 đã ghi nhận; adapter/wiring, thuật toán, rubric và API chi tiết còn chờ |
| Phương pháp nội bộ từng owner | Chờ owner điền lựa chọn | Các quyết định CN liên quan |

Khi thêm/xóa một quyết định, rà lại các mã phụ thuộc tại đây. Nếu quyết định đã chốt bị thay thế, không tiếp tục dùng đặc tả cũ cho các module nhận dữ liệu.
