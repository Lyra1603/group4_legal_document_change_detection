# DECISION — Quyết định triển khai và hợp đồng module

Tài liệu ghi các quyết định đã chốt và phạm vi áp dụng của chúng. Quy ước chạy thử được ghi ngay tại mục liên quan. Sau phiên 1, nhóm cập nhật những quyết định mới dựa trên báo cáo chạy thật. [Workflow](workflow.md) quy định cách đề xuất, review và ghi nhận thay đổi.

## Quyết định dùng schema Đức Anh làm hợp đồng chung

Dùng [contracts.py](../backend/app/schemas/contracts.py) và validator đã merge vào main qua [PR #2](https://github.com/Lyra1603/group4_legal_document_change_detection/pull/2). Giữ cấu trúc mã nguồn theo main và phân công theo chức năng. Nhóm dùng fixture để phát triển bán song song và kiểm tra lại bằng đầu ra thật tại điểm nối. Phép đánh giá ghép dự đoán với nhãn theo matching 1–1 trước, 1–n bổ sung khi hoàn thành baseline. Quan hệ một chỉ dẫn với nhiều đích được giữ theo LK-05.

## A. Quyết định của owner về cách triển khai

### CN-01 — Đọc/chuyển đổi và parse tài liệu

Dùng bộ chuyển PDF và Parser DOCX hiện có làm nền phiên 1. Adapter xử lý ánh xạ sang schema chung theo LK-03.

### CN-03 — Chunking, query và chọn ngữ cảnh

Chuẩn bị nguồn và chỉ mục song song với Linker/Text Diff. Ghép truy vấn khi hai nhánh sẵn sàng theo LK-06.

### CN-04 — Cấu hình LightRAG và tài nguyên

Dũng và Đức Anh phụ trách tích hợp LightRAG Server qua HTTP theo LK-13.

### CN-06 — Phương pháp Semantic Diff

Semantic Diff dùng rule trước, model khi cần. Kết luận phải kèm căn cứ hoặc ghi rõ phần chưa xác định.

### CN-08 — AI Adapter và tổ chức gọi mô hình

Dũng và Đức Anh phụ trách AI Adapter. Adapter là điểm gọi mô hình và kiểm tra đầu ra theo hợp đồng dùng chung.

### CN-10 — Cách tự kiểm chứng implementation

Các owner dùng kiểm thử module, kiểm thử chéo và kiểm thử toàn luồng. Evaluator độc lập nằm ngoài phạm vi triển khai. Đức Anh điều phối kế hoạch đánh giá.

### Quyết định sẽ bổ sung sau phiên 1

Các mã CN-02 (Linker), CN-05 (Text Diff), CN-07 (Scorer) và chi tiết thuật toán, mô hình, rubric, môi trường của các CN liên quan sẽ được cập nhật từ báo cáo chạy của owner. Phiên 1 thực hiện theo phạm vi và fixture đã giao trong [Implementation Plan](implementation-plan.md).

## B. Quyết định liên kết và hợp đồng giữa các module

### LK-01 — Phân công theo module/chức năng

| Phạm vi/module/chức năng | Người phụ trách | Ghi chú |
| --- | --- | --- |
| Dữ liệu + docs | Dũng | Dữ liệu, nghiệp vụ, tài liệu và phối hợp fixture/nhãn |
| Xử lý dữ liệu/tài liệu | Thọ | Chuyển đổi, Parser, adapter, trích và liên kết chỉ dẫn sửa đổi |
| Text Diff | Ngọc Anh | Phân tích phần chữ thay đổi |
| Semantic Change/Semantic Diff | Tuấn Anh | Phân tích thay đổi nghĩa và tạo nhận định có bằng chứng |
| Classifier & Scorer | Tuấn Anh | Theo người chủ trì CN-07 |
| Tích hợp + API | Dũng | Pipeline, tổng hợp đầu ra và API nghiệp vụ; không đồng nhất với phần gọi LightRAG |
| AI Adapter/gọi mô hình | Dũng + Đức Anh | Theo người chủ trì CN-08; phân chia công việc nội bộ sẽ được điền tại CN-08 |
| Gọi/tích hợp LightRAG | Dũng + Đức Anh | Phụ trách gọi/tích hợp dịch vụ theo phương án HTTP đã chốt |
| Context | Đức Anh | Chuẩn bị chunk, truy vấn, chọn và kiểm tra ngữ cảnh/căn cứ |
| Điều phối kế hoạch đánh giá | Đức Anh | Tổng hợp yêu cầu từ thành viên, tổ chức hoàn thiện kế hoạch và theo dõi thực hiện |

Tuấn Anh phụ trách phần hiển thị báo cáo ở điểm nối API → Frontend. Vai trò từng đầu ra và bên nhận được cụ thể hóa trong [Module](module.md).

### LK-02 — Các cặp liên kết và giao diện giữa module/chức năng

Dùng hợp đồng TypedDict của schema đã merge. Module trong backend bàn giao dict/list theo schema. LightRAG dùng HTTP qua client riêng. Chín điểm nối và fixture tương ứng nằm trong [Module §4](module.md#4-đầu-vàođầu-ra-và-các-điểm-nối).

### LK-03 — Parser → Adapter/Linker/Context

Adapter ánh xạ đầu ra native của Parser sang `ExtractedDocument`, `SourceBlock` và `Clause`. Giữ nguyên văn và khả năng tra nguồn. Parser tiếp tục tự đọc DOCX. Xem [Schema Integration](schema-integration.md).

### LK-04 — Định danh, nguồn và offset

Dùng `v1`/BASE, `s`/AMENDMENT và ID riêng cho từng REFERENCE. `EvidenceRef` chứa `document_id`, `source_refs`, `quote`. Giữ `block:N` khi trỏ đúng khối và quote khớp nguồn. Text Diff dùng offset ký tự Python theo khoảng nửa mở trên đúng chuỗi trước/sau.

### LK-05 — Chỉ dẫn sửa đổi và nội dung trước/sau

Phiên 1 giữ toàn văn cùng một đơn vị đối chiếu ở cả hai trạng thái. Với sửa nội dung của Điểm, Khoản hoặc Điều hiện có, đơn vị đối chiếu là toàn văn đơn vị đó. Khi thêm hoặc bãi bỏ cả một đơn vị, dùng đơn vị chứa nhỏ nhất còn tồn tại ở hai phía, ví dụ toàn Điều khi thêm hoặc bãi bỏ một Khoản. Vị trí đích vẫn ghi chính xác Điểm, Khoản hoặc Điều mà S chỉ ra. Nếu chỉ dẫn có nhiều đích, giữ đủ đích và căn cứ cho từng đích.

Quy ước triển khai thử phiên 1 là một `AmendmentItem` cho mỗi đích có thể áp dụng độc lập. Các item cùng chỉ dẫn trỏ về cùng bằng chứng S. Với chỉ dẫn có đích chồng lấn hoặc thao tác phụ thuộc lẫn nhau, ghi nhận giới hạn và đưa ví dụ vào báo cáo phiên 1 để nhóm chốt cách xử lý.

Chỉ dùng `QUOTED` khi toàn bộ đoạn sau là nguyên văn từ S. Dùng `DERIVED` khi dựng lại đơn vị đối chiếu từ V1 và chỉ dẫn S. Phía đã xác định vắng mặt và phía chưa biết được biểu diễn theo [SRS §1.2](srs.md#12-amendmentitem-và-analysiscontext).

### LK-06 — Context song song Text Diff, ghép query trước Semantic Diff

Chuẩn bị Context và chỉ mục song song với Linker → Text Diff. Khi hai nhánh có đủ dữ liệu, ghép chỉ dẫn, trước/sau và vùng chữ đổi để truy xuất, kiểm tra nguồn và cung cấp `AnalysisContext` cho Semantic Diff. [Architecture §4.1](architecture.md#41-một-lượt-phân-tích) giữ sơ đồ chi tiết.

### LK-07 — Text Diff → Semantic Diff

Text Diff trả `TextDiffResult` theo cùng `amendment_id`. Các đoạn INSERT/DELETE/REPLACE có offset khớp hai chuỗi trước/sau. Semantic nhận phần chữ đổi cùng ngữ cảnh đã kiểm chứng.

### LK-08 — Cấu trúc Semantic Change

Dùng `SemanticDiffResult`, `SemanticChange` và `ChangeAspect` trong schema PR #2. Giữ bằng chứng, cảnh báo và trạng thái cần kiểm tra theo [SRS §1.3](srs.md#13-semanticdiffresult-hợp-đồng-kết-quả-phân-tích-ngữ-nghĩa).

### LK-09 — Tám nhóm field_group, category và ranh giới nhãn

Dùng tám `field_group` đã có. Với thay đổi nghĩa, category khác null phải thuộc một nhóm có trong aspects. Thay đổi chỉ về diễn đạt dùng `WORDING_ONLY` theo schema. Review ca giao thoa bằng văn bản nguồn trước khi chốt ranh giới nhãn.

### LK-10 — Semantic Diff → Classifier & Scorer

`ScoringResult` nối tới thay đổi bằng `change_id`. Khi có căn cứ gán nhóm khía cạnh nhưng chưa đủ căn cứ chấm mức độ, giữ nhóm đã xác định, dùng `significance = null`, `is_critical = null`, `needs_review = true` và ghi lý do. Rubric chi tiết và cách xử lý lỗi theo bước sẽ được cập nhật từ báo cáo của các thành viên sau lần chạy phiên 1.

### LK-11 — Báo cáo Pipeline → API/frontend

API trả `ComparisonReport` gồm kết quả theo `AmendmentResult`. Đầu vào hiện dùng `doc_v1`, `doc_s` và `reference_files` nếu có. Frontend hiện đoạn trích và vị trí từ bằng chứng trong báo cáo của lượt đang mở. Xem [Architecture §4.3](architecture.md#43-vị-trí-lưu-và-vòng-đời) về vòng đời nguồn.

### LK-12 — Null, rỗng, cảnh báo, lỗi và trạng thái

Khi chưa xác định được đích, giữ chỉ dẫn, thao tác đã nhận diện và bằng chứng. Dùng `applicability = UNRESOLVED`, `needs_review = true` và lý do. Giữ mục trong báo cáo và để các kết quả phân tích chưa chạy là `null`.

Giữ ràng buộc `SUCCESS`/`PARTIAL`/`FAILED` của schema. Mã lỗi, chính sách tiếp tục theo từng bước và quy tắc tổng hợp còn mở được cập nhật khi Đức Anh chạy phiên 1 và nhóm đối chiếu báo cáo của các owner.

### LK-13 — LightRAG HTTP và vòng đời dữ liệu

LightRAG Server riêng, backend gọi qua HTTP. Dũng và Đức Anh phụ trách tích hợp. Phạm vi chính là retrieval và kiểm chứng nguồn. Phiên 1 dùng fixture/mock để kiểm tra điểm nối, kết quả chạy làm căn cứ chốt release, endpoint, payload, cách ly và vòng đời chỉ mục.
