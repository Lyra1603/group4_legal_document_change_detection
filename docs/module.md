# MODULE — Phân công, cấu trúc và bàn giao

**Dự án:** Legal Document Change Detection — POCS, Nhóm 4  
**Phiên bản:** Bản đầu tiên  
**Trạng thái:** Đang hoàn thiện theo các quyết định trong [decision.md](decision.md)

## 1. Mục đích và quy định chung

Tài liệu ghi nhiệm vụ, người chịu trách nhiệm, file chính, điểm nối và điều kiện bàn giao từng module. Các lựa chọn và nội dung đang bàn được ghi trong decision.md; module.md chỉ ghi lựa chọn đã chốt, hoặc đánh dấu rõ phần còn chờ và mã quyết định liên quan.

- Giữ các folder chính theo cấu trúc plan_lightrag; không tự xóa, đổi tên hoặc chuyển vị trí. Cấu trúc chuẩn không phụ thuộc việc nhánh tích hợp sau đó mang tên main hay plan_lightrag.
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
| api/ | Dũng | Owner Pipeline, frontend và các bên dùng API | Chờ hợp đồng API/báo cáo |
| schemas/ | Đức Anh | Owner bên cung cấp và bên nhận từng kiểu dữ liệu | Chờ các hợp đồng chung |
| document_processing/ | Thọ | Đức Anh, Ngọc Anh, Tuấn Anh theo điểm nối; Dũng review nguồn/nghiệp vụ | Chờ hợp đồng cây/nguồn/chỉ dẫn |
| context/ | Đức Anh ở phần chuẩn bị context; người gọi/tích hợp LightRAG bổ sung sau | Thọ cung cấp nguồn; Ngọc Anh/Tuấn Anh nhận ngữ cảnh; Dũng nhận phần tích hợp | HTTP đã chốt; chi tiết LightRAG chờ LK-13 sau các quyết định còn lại |
| change_analysis/ | Chốt theo chức năng ở LK-01, không gán owner chung toàn folder | Ngọc Anh: Text Diff; Tuấn Anh: Semantic Change/Scorer; Dũng + Đức Anh: AI Adapter | Phân công đã chốt; contract chi tiết còn chờ |
| evaluation/ | Không triển khai như module riêng | Test chuyển sang các owner và test/ | Giữ cấu trúc, không giao lại đầu việc Evaluator |

| Thành phần ngoài các folder trên | Người phụ trách | Ghi chú |
| --- | --- | --- |
| backend/main.py | Dũng | Khởi tạo ứng dụng, đăng ký thành phần backend |
| backend/app/pipeline.py | Dũng | Điều phối và tổng hợp báo cáo |
| backend/app/config.py | Dũng điều phối cấu hình tích hợp/API; Đức Anh phối hợp phần kỹ thuật liên quan | Cấu hình LightRAG do người phụ trách được bổ sung sau phối hợp |
| frontend/ | Tuấn Anh theo phân công hiện có | Cần xác nhận khối lượng sau khi nhận thêm Semantic Diff; không tự chuyển người |
| Dữ liệu, nghiệp vụ, nhãn/fixture nghiệp vụ và tài liệu tổng quát | Dũng | Owner liên quan phối hợp, người review nhãn khác người tạo |

## 3. Đặc tả từng module

### 3.1. api/

**Owner:** Dũng

**Nhiệm vụ và ranh giới:** Nhận yêu cầu, kiểm tra đầu vào cấp HTTP, gọi Pipeline và trả báo cáo/lỗi. Không thực hiện thuật toán phân tích pháp lý trong router.

| File chính | Trách nhiệm |
| --- | --- |
| compare.py | Endpoint so sánh; nhận file và tham số, chuyển lời gọi sang Pipeline, ánh xạ kết quả/lỗi HTTP. |

**Đầu vào:** File V1, S, tài liệu tham chiếu và tham số upload theo hợp đồng đã chốt.

**Đầu ra:** Báo cáo và nguồn cho frontend hoặc lỗi có cấu trúc; mã HTTP tách khỏi trạng thái nghiệp vụ.

**Bên kết nối:** Pipeline, schemas, frontend.

**File hỗ trợ:** được thêm trong module theo quy định mục 1; tên/cấu trúc nội bộ chỉ cố định khi owner đề xuất và các bên liên quan thống nhất.

**Điều kiện bàn giao:** Fixture upload hợp lệ/lỗi, báo cáo đầy đủ/một phần/thất bại; frontend và Pipeline cùng xác nhận dùng được.

**Quyết định liên quan:** LK-02, LK-11, LK-12. Tra cứu trong [decision.md](decision.md).

### 3.2. schemas/

**Owner:** Đức Anh

**Nhiệm vụ và ranh giới:** Giữ định nghĩa dữ liệu dùng chung và quy tắc kiểm tra tại ranh giới module. Không tự quyết định kết luận nghiệp vụ hoặc thuật toán của module khác.

| File chính | Trách nhiệm |
| --- | --- |
| contracts.py | Định nghĩa kiểu dữ liệu, trường và giá trị hợp lệ theo hợp đồng được hai bên thống nhất. |

**Đầu vào:** Các quyết định hợp đồng, input/output mẫu và quy tắc nghiệp vụ đã chốt.

**Đầu ra:** Schema/validator dùng chung, phiên bản hợp đồng và fixture hợp lệ/không hợp lệ.

**Bên kết nối:** Mọi module trao đổi dữ liệu; mỗi owner review kiểu dữ liệu mình cung cấp hoặc nhận.

**File hỗ trợ:** được thêm trong module theo quy định mục 1; tên/cấu trúc nội bộ chỉ cố định khi owner đề xuất và các bên liên quan thống nhất.

**Điều kiện bàn giao:** Schema và fixture nhất quán với decision; validator phát hiện ca sai liên quan. Các file validation.py/report_validation.py hiện có ở nhánh khác được review để tái sử dụng, không tự xóa hoặc coi đã tương thích.

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

**Đầu ra:** Cây/nguồn chuẩn hóa; chỉ dẫn sửa đổi, vị trí đích, nội dung cục bộ, hiệu lực và cảnh báo theo contract chờ chốt.

**Bên kết nối:** Thọ → Đức Anh ở nguồn/context; Thọ → Dũng ở Pipeline/API; Thọ → Ngọc Anh/Tuấn Anh qua dữ liệu trước/sau và căn cứ.

**File hỗ trợ:** được thêm trong module theo quy định mục 1; tên/cấu trúc nội bộ chỉ cố định khi owner đề xuất và các bên liên quan thống nhất.

**Điều kiện bàn giao:** Có fixture file thật/cây mong đợi, bảng/outside, chỉ dẫn mơ hồ và sai văn bản đích. Số lượng Điều/Khoản/Điểm kỳ vọng được review độc lập từ nguồn; summary tự đếm không chứng minh Parser không bỏ sót.

**Quyết định liên quan:** CN-01, CN-02, LK-03, LK-04, LK-05, LK-12. Tra cứu trong [decision.md](decision.md).

### 3.4. context/

**Owner:** Đức Anh ở phần chuẩn bị context; người gọi/tích hợp LightRAG bổ sung sau. LK-13 chốt sau các quyết định còn lại.

**Nhiệm vụ và ranh giới:** Chuẩn bị chunk, truy xuất LightRAG và chọn ngữ cảnh/căn cứ cho phân tích. LightRAG phục vụ retrieval; không tự thay linker, Semantic Diff hoặc Scorer.

| File chính | Trách nhiệm |
| --- | --- |
| chunk_builder.py | Tạo đoạn đủ nghĩa, giữ metadata và liên kết nguồn. |
| source_registry.py | Ánh xạ chunk/kết quả truy xuất về đúng document_id và nguyên văn nguồn. |
| lightrag_client.py | Gọi LightRAG Server qua HTTP: nhập, theo dõi sẵn sàng, truy vấn, xử lý lỗi và dọn dữ liệu. |
| context_builder.py | Lập truy vấn, chọn/kiểm tra căn cứ, cung cấp ngữ cảnh và nhu cầu tham chiếu thiếu/chưa rõ. |

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
| semantic_diff.py | Tuấn Anh: xác định Semantic Change, giải thích, bằng chứng và trường hợp chưa đủ căn cứ. |
| scorer.py | Tuấn Anh: phân loại/chấm mức tác động theo kết quả ngữ nghĩa và rubric chung. |
| ai_adapter.py | Dũng + Đức Anh: đóng gói gọi mô hình và kiểm tra output; chi tiết cách gọi/giao diện còn chờ CN-08/LK-02. |

**Đầu vào:** Yêu cầu sửa đổi có nội dung trước/sau và context; Text Diff được cung cấp cho Semantic Diff khi có.

**Đầu ra:** TextDiffResult, kết quả Semantic Change và scoring theo hợp đồng chờ chốt; Pipeline ánh xạ sang báo cáo mục tiêu.

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

**Bên kết nối:** Các owner kiểm tra chéo; thành viên khác kiểm tra phụ; đầu-cuối cần người điều phối được xác nhận.

**File hỗ trợ:** được thêm trong module theo quy định mục 1; tên/cấu trúc nội bộ chỉ cố định khi owner đề xuất và các bên liên quan thống nhất.

**Điều kiện bàn giao:** Có người chịu trách nhiệm kiểm tra từng điểm nối và toàn luồng; bỏ Evaluator không được hiểu là bỏ expected output, nhãn chuẩn hoặc phép đo khi báo cáo yêu cầu.

**Quyết định liên quan:** LK-01. Tra cứu trong [decision.md](decision.md).

## 4. Đầu vào–đầu ra và các điểm nối

| Điểm nối | Bên giao | Bên nhận | Nội dung cần chốt | Mã |
| --- | --- | --- | --- | --- |
| Parser/adapter → linker/context | Thọ | Thọ/Đức Anh | Cây, ID, nguồn, summary và cảnh báo | LK-03, LK-04 |
| Linker/context → Text Diff | Thọ/Đức Anh | Ngọc Anh | Nội dung trước/sau cục bộ và căn cứ | LK-05, LK-06, LK-07 |
| Text Diff + context → Semantic Diff | Ngọc Anh/Đức Anh | Tuấn Anh | Vùng chữ đổi, ngữ cảnh, bằng chứng và lỗi | LK-06, LK-07, LK-08 |
| Semantic Diff → Scorer | Tuấn Anh | Tuấn Anh | Semantic Change, phân loại/khía cạnh và trạng thái chưa rõ | LK-08, LK-09, LK-10 |
| Phân tích → Pipeline/API → frontend | Owner từng phần/Dũng | Dũng/Tuấn Anh | Báo cáo, nguồn, trạng thái và phiên kiểm chứng | LK-11, LK-12 |

Tên hàm, tên trường, kiểu, danh mục mã và fixture chính thức được chốt ở decision rồi đồng bộ vào schema. Không điền một hợp đồng mới trong module.md như đã được các bên đồng ý. JSON có thể dùng lưu fixture; các module cùng backend có thể truyền object/dict qua hàm, không bắt mọi điểm nối dùng file hoặc HTTP.

## 5. Phối hợp triển khai bán song song

Thực hiện quy trình chốt → code song song → kiểm thử chéo → tích hợp theo [workflow.md](workflow.md). Các cặp cụ thể theo LK-02 trong decision.md. File này xác định nhiệm vụ/đầu ra từng module, không định nghĩa một quy trình vận hành khác.

## 6. Kiểm thử và điều kiện hoàn thành

Checklist, trách nhiệm hai bên, cách báo lỗi và điều kiện merge theo [workflow.md](workflow.md). Bàn giao module vẫn cần code, input/output mẫu, lệnh/kết quả kiểm tra và giới hạn. Các điều kiện đặc thù trong mục 3 là căn cứ kiểm tra, không thay quy trình kiểm thử chung.

## 7. Trạng thái hoàn thiện

File này chỉ được coi hoàn thiện khi toàn bộ quyết định có liên quan trong decision.md đã chốt và kết luận được phản ánh đúng vào đặc tả module. Một module có thể đủ đặc tả trước các module khác nếu các quyết định ảnh hưởng trực tiếp đã chốt; không được xem phần còn chờ là phương án chính thức.

Phân biệt ba trạng thái: đủ đặc tả, đã hiện thực và đã tích hợp/kiểm thử. Việc chốt tài liệu không tự xác nhận code đã có hoặc kiểm tra đã đạt.

| Hạng mục | Trạng thái hiện tại | Việc cần hoàn thiện |
| --- | --- | --- |
| Folder chính và danh sách file chính | Đã có cấu trúc làm căn cứ | Review phạm vi file và giữ ổn định đường dẫn |
| LightRAG qua HTTP | Đã chốt phương án | CN-03/CN-04 và LK-13 còn chi tiết kỹ thuật |
| Semantic Diff giao Tuấn Anh; bỏ Evaluator riêng | Đã chốt phân công chức năng | Hoàn thiện contract/fixture và trách nhiệm test |
| Phân công change_analysis/AI Adapter | Đã chốt theo chức năng | LK-01; CN-05/CN-06/CN-07/CN-08 còn lựa chọn triển khai |
| Người gọi/tích hợp LightRAG | Bổ sung sau | LK-13 chốt sau các quyết định còn lại |
| Hợp đồng dữ liệu và báo cáo | Chưa đóng băng | LK-02 đến LK-12 và LK-13 |
| Phương pháp nội bộ từng owner | Chờ owner điền lựa chọn | Các quyết định CN liên quan |

Khi thêm/xóa một quyết định, rà lại các mã phụ thuộc tại đây. Nếu quyết định đã chốt bị thay thế, không tiếp tục dùng đặc tả cũ cho các module nhận dữ liệu.
