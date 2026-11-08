# DECISION — Lựa chọn triển khai và hợp đồng module

**Dự án:** Legal Document Change Detection — POCS, Nhóm 4  
**Phiên bản:** Bản đầu tiên  
**Mục đích:** Ghi câu hỏi, lựa chọn của owner, sự thống nhất của bên liên quan và kết luận dùng để hoàn thiện [module.md](module.md).

Tài liệu có hai phần chính: A — quyết định owner về cách triển khai; B — quyết định liên kết/hợp đồng. Đây là lựa chọn thiết kế, không mặc định tồn tại một đáp án đúng duy nhất. Mỗi lựa chọn vẫn phải đáp ứng yêu cầu nghiệp vụ và có thể kiểm chứng bằng mẫu.

Owner có thể đề xuất phương án muốn dùng; chỉ chuyển thành quyết định dự án sau khi có xác nhận phù hợp phạm vi ảnh hưởng. Ví dụ “Semantic Change có 6/8/10 trường” là LK-08 vì bên khác phải đọc dữ liệu, không phải lựa chọn riêng owner. Số trường phải xuất phát từ thông tin cần bàn giao, không cần cố định trước khi xác định nhiệm vụ.

**Cách dùng:** phần đã chốt ghi rõ kết luận; phần chưa chốt giữ lựa chọn/kết luận còn trống. Mỗi thay đổi hợp đồng cần đối chiếu schema và fixture trước khi cập nhật module.md. Tài liệu không xác nhận implementation hoặc GitHub settings đã hoàn thành.

| Trạng thái | Ý nghĩa |
| --- | --- |
| CHO_DE_XUAT | Chưa có lựa chọn cụ thể từ người chủ trì |
| CHO_CAC_QUYET_DINH_KHAC_HOAN_THANH | Để chốt sau khi các quyết định còn lại hoàn thành; áp dụng cho LK-13 |
| DANG_BAN | Đã có phương án nhưng chưa đủ thống nhất |
| CHOT_MOT_PHAN | Một số ý đã chốt, các ý còn lại phải liệt kê rõ |
| DA_CHOT | Có kết luận, phạm vi áp dụng và xác nhận của bên liên quan |
| DUOC_THAY_THE | Đã có quyết định mới thay thế; giữ mã và dẫn sang mã mới |

Các nguyên tắc đã được xác lập: giữ cấu trúc folder chính theo plan_lightrag; phân biệt file chính/file bổ sung; phát triển bán song song bằng contract/fixture; bỏ Evaluator độc lập và kiểm thử chéo tại điểm nối; Tuấn Anh nhận Semantic Diff; LightRAG Server riêng qua HTTP là phương án tích hợp đã chốt. Không mở lại các nguyên tắc này chỉ vì chi tiết implementation chưa hoàn thiện.

Mẫu điền cho từng quyết định: vấn đề → người chủ trì → phương án → đề xuất/lý do → bên cần đồng ý → kết luận → trạng thái → đầu ra cần cập nhật. Không cần trường ngày sửa chữa. Các tên chủ trì ghi “đề xuất” chưa phải bổ nhiệm đã được nhóm xác nhận.

## A. Quyết định của owner về cách triển khai

Phần này ưu tiên những lựa chọn nằm trong module. Nếu đổi output, dependency chung, chi phí/vận hành hoặc yêu cầu bên khác thay code thì phải kết hợp quyết định LK tương ứng. Lựa chọn nội bộ được owner chốt và thông báo/review theo phạm vi ảnh hưởng, không bắt cả nhóm duyệt từng hàm phụ.

### CN-01 — Đọc/chuyển đổi và parse tài liệu

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Thọ

**Vấn đề cần chốt:** Công cụ/phiên bản PDF → DOCX; cách nhận diện Điều/Khoản/Điểm; giữ bảng/outside; xử lý đánh số Word và bố cục khó; kiểm tra sau chuyển đổi.

**Phương án để cân nhắc:** Giữ converter/Parser hiện có; bổ sung adapter, normalization hoặc thay phương pháp nội bộ nếu có kiểm chứng.

**Bên cần thống nhất/review:** Dũng review dữ liệu; Dũng/owner nhận review nếu thay đầu ra hoặc dependency.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** pdf_to_docx.py, legal_structure_parser.py, fixture tài liệu; hợp đồng nguồn theo LK-03/LK-04.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### CN-02 — Phương pháp trích và liên kết chỉ dẫn

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Thọ

**Vấn đề cần chốt:** Nhận diện văn bản đích, chỉ dẫn thay cụm từ/toàn đơn vị, bổ sung/bãi bỏ; tạo trước/sau cục bộ; tiêu chí liên kết mơ hồ và hiệu lực.

**Phương án để cân nhắc:** Rule, matching cấu trúc/nội dung hoặc kết hợp; không mặc định phải dùng mô hình.

**Bên cần thống nhất/review:** Đức Anh, Ngọc Anh, Tuấn Anh; Dũng review nghiệp vụ.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** amendment_linker.py, fixture chỉ dẫn–đích; output thuộc LK-05.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### CN-03 — Chunking, query và chọn ngữ cảnh

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Đức Anh

**Vấn đề cần chốt:** Kích thước/ghép chunk, giữ câu dẫn, tránh full_text lặp; tạo query; số/ngân sách kết quả; kiểm tra quote; tiêu chí chọn đủ căn cứ.

**Phương án để cân nhắc:** Chunk theo cấu trúc/đoạn hoặc kết hợp; truy xuất nhiều bước khi có nhu cầu và giới hạn.

**Bên cần thống nhất/review:** Thọ về nguồn; Tuấn Anh/Ngọc Anh về ngữ cảnh sử dụng; Dũng về căn cứ.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** chunk_builder.py, context_builder.py và fixture retrieval; contract theo LK-04/LK-06.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### CN-04 — Cấu hình LightRAG và tài nguyên

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Dũng + Đức Anh; phối hợp các bên liên quan về cấu hình và tài nguyên.

**Vấn đề cần chốt:** Cấu hình môi trường, tài nguyên, giới hạn/chi phí; caching nội bộ và quy tắc retry; điều kiện dịch vụ sẵn sàng. Không đổi phương án HTTP.

**Phương án để cân nhắc:** Chạy Server cùng máy hoặc máy riêng; lựa chọn release/model/embedding/storage trong phương án HTTP đã chốt.

**Bên cần thống nhất/review:** Owner dùng context và thành viên chịu chi phí/tài nguyên; thống nhất an toàn dữ liệu theo yêu cầu dự án.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Đã chốt Dũng + Đức Anh phụ trách gọi/tích hợp LightRAG; CN-04 cần phối hợp LK-13 theo thứ tự chốt sau các quyết định còn lại. Chưa có lựa chọn cấu hình cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** config.py, cấu hình chạy; API/cách ly/vòng đời theo LK-13.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### CN-05 — Thuật toán Text Diff

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Ngọc Anh

**Vấn đề cần chốt:** Cách chuẩn hóa nội bộ, nhóm vùng đổi, giữ tiếng Việt và dấu câu; cách kiểm tra reconstruction/offset.

**Phương án để cân nhắc:** So sánh ký tự, từ, dòng hoặc kết hợp.

**Bên cần thống nhất/review:** Tuấn Anh, Dũng/API và frontend nếu ảnh hưởng chuỗi/vị trí nhận.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** text_diff.py và unit fixture; output/offset theo LK-07/LK-04.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### CN-06 — Phương pháp Semantic Diff

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Tuấn Anh

**Vấn đề cần chốt:** Cách chia/gộp nhận định; prompt/ngữ cảnh; kiểm tra bằng chứng; xử lý output không hợp lệ/thiếu căn cứ và giới hạn suy luận.

**Phương án để cân nhắc:** Rule, LLM hoặc kết hợp; lựa chọn baseline và phương án cải thiện.

**Bên cần thống nhất/review:** Ngọc Anh bàn giao Text Diff; Dũng nhận kết quả tích hợp và review nghiệp vụ/nhãn; Đức Anh phối hợp AI Adapter khi liên quan.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** semantic_diff.py, fixture nhận định và giới hạn; số/tên trường thuộc LK-08, phân loại thuộc LK-09.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### CN-07 — Phương pháp Classifier & Scorer

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Tuấn Anh

**Vấn đề cần chốt:** Cách áp rubric, xử lý ranh giới mức, tạo lý do; biểu diễn trường hợp chưa đủ căn cứ; kiểm tra tính nhất quán severity/critical.

**Phương án để cân nhắc:** Rule/rubric, mô hình hoặc kết hợp; không mặc định số chữ đổi hay retrieval score là mức tác động.

**Bên cần thống nhất/review:** Ngọc Anh bàn giao Text Diff; Tuấn Anh phụ trách cả Semantic Change và Scorer; Dũng review rubric và nhận kết quả tích hợp/API.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** scorer.py, fixture ranh giới; ý nghĩa nhãn và dữ liệu bàn giao thuộc LK-09/LK-10.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### CN-08 — AI Adapter và tổ chức gọi mô hình

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Dũng + Đức Anh

**Vấn đề cần chốt:** Thư viện/nhà cung cấp, cấu hình model, timeout/token/cost, parse/validate output, kiểm tra quote, logging và fallback.

**Phương án để cân nhắc:** Adapter chỉ phục vụ Semantic Diff hoặc dùng chung với Scorer; cách chia prompt/parser/retry nội bộ.

**Bên cần thống nhất/review:** Tuấn Anh sử dụng Semantic Change/Scorer; Ngọc Anh nếu sử dụng mô hình; Dũng và Đức Anh phối hợp gọi mô hình/tích hợp; người chịu tài nguyên/chi phí.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** ai_adapter.py và file hỗ trợ nếu cần; public function/return/error theo LK-02/LK-12.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### CN-10 — Cách tự kiểm chứng implementation

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Mỗi owner

**Vấn đề cần chốt:** Ca kiểm tra quan trọng, expected output, lệnh chạy, tài nguyên; cách phân biệt đạt hợp đồng với đúng nghiệp vụ và giới hạn chưa hỗ trợ.

**Phương án để cân nhắc:** Unit test với dữ liệu giả định có căn cứ, mẫu thật hoặc cả hai; baseline để đối chiếu khi cần.

**Bên cần thống nhất/review:** Owner module nhận, Dũng hỗ trợ đáp án nghiệp vụ.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** Test module, fixture và hướng dẫn kiểm tra do owner/bên nhận thống nhất; không tạo mục quyết định liên kết riêng cho nội dung này trong bản hiện tại.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

## B. Quyết định liên kết và hợp đồng giữa các module

Mỗi quyết định phải có bên cung cấp và bên nhận cùng thống nhất. Dũng điều phối tích hợp/Pipeline/API và review nghiệp vụ; Đức Anh phối hợp schema theo Architecture và AI Adapter theo CN-08. Không chỉ chốt “trả JSON”: cần schema, ý nghĩa và ví dụ đúng/sai. Bên nhận có thể phát triển với fixture ngay sau khi phần hợp đồng liên quan đã chốt.

### LK-01 — Phân công theo module/chức năng

**Trạng thái:** DA_CHOT  
**Chủ trì điều phối:** Dũng

**Kết luận:** Áp dụng phân công theo chức năng dưới đây. Không mặc định một người sở hữu toàn bộ folder change_analysis khi các chức năng trong đó được giao cho người khác nhau.

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

**Phạm vi đã chốt:** phân công chức năng; Dũng + Đức Anh phụ trách gọi/tích hợp LightRAG; Đức Anh phụ trách context và điều phối kế hoạch đánh giá. Giữ cấu trúc folder chính theo plan_lightrag, không triển khai Evaluator riêng. Các chi tiết thuật toán và hợp đồng vẫn theo CN/LK tương ứng.

**Phần chưa quyết định tại LK-01:** không chốt lại người phụ trách frontend hoặc thay đổi ownership schema chỉ từ bảng chức năng này; không tự chuyển các nhiệm vụ ngoài phạm vi được liệt kê.

**Đầu ra cần cập nhật:** module.md và các bảng phân công khi thực hiện đồng bộ tài liệu; LK-02 và các điểm nối phải sử dụng tên người theo bảng trên.

### LK-02 — Các cặp liên kết và giao diện giữa module/chức năng

**Trạng thái:** DANG_BAN  
**Chủ trì:** Hai owner tại mỗi điểm nối; Dũng điều phối tích hợp/API, Đức Anh phối hợp schema và AI Adapter theo phạm vi liên quan.

**Mục đích:** Liệt kê các cặp kết nối theo Architecture và phân công LK-01. Mỗi cặp phải cùng chốt input/output; không chờ bên trước hoàn thiện mới bắt đầu code. Các cặp sau là điểm bàn giao dữ liệu hoặc lời gọi, không khẳng định mọi chức năng chạy nối tiếp thành một chuỗi duy nhất.

| Cặp liên kết theo chức năng | Dữ liệu/lời gọi cần thống nhất | Quyết định chi tiết |
| --- | --- | --- |
| API/Pipeline (Dũng) → Xử lý tài liệu (Thọ) | Bộ V1/S/tham chiếu, metadata, tham số xử lý; cấu trúc kết quả trả về | LK-03, LK-04, LK-05, LK-11, LK-12 |
| Parser/Adapter (Thọ) → Trích/liên kết chỉ dẫn (Thọ) | Cây, nguồn và cấu trúc chỉ dẫn; điểm nối nội bộ cùng người | LK-03, LK-04, LK-05 |
| Parser/Adapter/Linker (Thọ) → Context (Đức Anh) | Cấu trúc, nguyên văn, định danh, spans và yêu cầu ngữ cảnh; Dũng + Đức Anh phụ trách gọi/tích hợp LightRAG | LK-03, LK-04, LK-05, LK-06 |
| Linker — dữ liệu trước/sau (Thọ) → Text Diff (Ngọc Anh) | Nội dung cục bộ, chỉ dẫn/đích, căn cứ tạo nội dung sau, cảnh báo | LK-05, LK-07 |
| Context (Đức Anh) → Text Diff (Ngọc Anh) | Ngữ cảnh/trạng thái đủ căn cứ cần cho bước diff, nếu sử dụng | LK-06, LK-07 |
| Context (Đức Anh) → Semantic Change (Tuấn Anh) | Ngữ cảnh, tài liệu dẫn chiếu, bằng chứng và giới hạn | LK-06, LK-08 |
| Text Diff (Ngọc Anh) → Semantic Change (Tuấn Anh) | Các vùng thêm/xóa/thay thế, offset, ID và trường hợp không có kết quả diff | LK-07, LK-08 |
| Semantic Change (Tuấn Anh) → Scorer (Tuấn Anh) | Nhận định nghĩa, bằng chứng, khía cạnh/nhãn và cảnh báo; điểm nối nội bộ cùng người | LK-08, LK-09, LK-10 |
| AI Adapter (Dũng + Đức Anh) ↔ Semantic Change/Scorer (Tuấn Anh) | Yêu cầu gọi mô hình, output hợp lệ, bằng chứng và lỗi | CN-08, LK-08, LK-10, LK-12 |
| Xử lý tài liệu/Linker (Thọ) → Pipeline (Dũng) | Dữ liệu nguồn/chỉ dẫn và phần chưa phân tích được | LK-04, LK-05, LK-11, LK-12 |
| Text Diff (Ngọc Anh) → Pipeline (Dũng) | Kết quả diff phục vụ tổng hợp và hiển thị | LK-07, LK-11, LK-12 |
| Semantic Change/Scorer (Tuấn Anh) → Pipeline/API (Dũng) | Nhận định, nhãn, mức tác động, giải thích, nguồn và cảnh báo | LK-08, LK-09, LK-10, LK-11, LK-12 |
| Context (Đức Anh) → Pipeline (Dũng) | Ngữ cảnh, tình trạng tham chiếu và lỗi/cảnh báo liên quan | LK-06, LK-11, LK-12 |
| Pipeline (Dũng) → API (Dũng) | Envelope báo cáo, lỗi và trạng thái; điểm nối nội bộ cùng người | LK-11, LK-12 |
| API (Dũng) → Frontend (Tuấn Anh theo phân công hiện có) | Upload, báo cáo, nguồn hiển thị và lỗi; không tự thay phân công frontend tại đây | LK-11, LK-12 |
| Context/nguồn (Đức Anh/Thọ) ↔ Gọi LightRAG (Dũng + Đức Anh) | Payload nhập/query, mapping nguồn, trạng thái và lỗi; bổ sung chi tiết sau các quyết định khác | LK-13 |
| Pipeline (Dũng) ↔ Gọi LightRAG (Dũng + Đức Anh) | Khởi tạo, giới hạn thời gian, cách ly và dọn tài nguyên theo comparison | LK-13 |
| Dữ liệu/docs (Dũng) ↔ Các owner (Thọ, Ngọc Anh, Tuấn Anh, Đức Anh) | Mẫu nguồn, fixture, expected output và quy ước nghiệp vụ; phối hợp phát triển, không là bước runtime bắt buộc | LK-03 đến LK-12 theo dữ liệu liên quan |

**Lưu ý phân công:** Context do Đức Anh phụ trách; nguồn do Thọ phụ trách; gọi/tích hợp LightRAG do Dũng + Đức Anh phối hợp.

**Mỗi cặp cần điền:** tên public function/API, tham số, kiểu và cấu trúc return; trường bắt buộc/tùy chọn; ID, nguồn/offset; ý nghĩa null/rỗng/lỗi; phiên bản hợp đồng và một bộ input/output mẫu hai bên đã review.

**Cách trao đổi:** Các module cùng backend có thể gọi hàm với object/dict; JSON dùng lưu fixture hoặc trao đổi khi hai bên chọn. LightRAG là ranh giới HTTP đã chốt; không bắt mọi cặp dùng HTTP hoặc ghi file JSON.

**Kết luận hiện có:** Danh sách cặp là cơ sở chia việc bàn hợp đồng. Chữ ký hàm, trường dữ liệu và fixture từng cặp chưa tự được coi đã chốt chỉ vì đã liệt kê ở bảng.

**Đầu ra cần cập nhật:** từng hợp đồng LK-03 đến LK-12, schema/fixture và module.md sau khi hai bên thống nhất. LK-13 được hoàn thiện sau theo thứ tự riêng.

### LK-03 — Parser → Adapter/Linker/Context

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Thọ + Đức Anh

**Vấn đề cần chốt:** Cấu trúc cây, node/children, content/full_text/segments, bảng/outside, summary, status/warnings; định danh và mapping từ cây sang đầu ra bên nhận. Số đếm kỳ vọng lấy từ đâu để phát hiện bỏ sót.

**Phương án để cân nhắc:** Giữ native Parser và adapter; hoặc thay biểu diễn bàn giao sau khi các bên review.

**Bên cần thống nhất/review:** Thọ và Đức Anh; Ngọc Anh/Tuấn Anh nếu dùng trực tiếp; Dũng review mẫu nguồn.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** Contract cây/adapter, JSON fixture và test parse; module.md document_processing/context.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-04 — Định danh, nguồn và offset

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Thọ + Đức Anh + Tuấn Anh

**Vấn đề cần chốt:** document_id/role, unit/node ID, source_ref/spans, trích nguyên văn, đơn vị offset và chuẩn hóa chuỗi; metadata chunk; phạm vi duy nhất của ID; nguồn DOCX chuyển đổi so với PDF gốc.

**Phương án để cân nhắc:** Giữ block:N và offset Python hiện có, thêm adapter cho frontend khi cần; mapping PDF chỉ dùng khi kiểm chứng.

**Bên cần thống nhất/review:** Thọ, Đức Anh, Ngọc Anh và Tuấn Anh; Dũng kiểm tra căn cứ.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** Source schema/registry, fixture tiếng Việt/nguồn trùng tên/offset, hiển thị frontend.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-05 — Chỉ dẫn sửa đổi và nội dung trước/sau

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Thọ + Ngọc Anh + Tuấn Anh; Dũng điều phối tích hợp, Đức Anh phối hợp context khi liên quan

**Vấn đề cần chốt:** Trường chỉ dẫn, operation, văn bản đích, locator, applicability, before/after, after_basis, hiệu lực/chuyển tiếp, bằng chứng/cảnh báo; một Điều nhiều yêu cầu và một yêu cầu nhiều đích.

**Phương án để cân nhắc:** Bàn giao AmendmentItem hoặc cấu trúc tương đương được review; phân biệt trích trực tiếp, suy ra, không tồn tại và chưa biết.

**Bên cần thống nhất/review:** Thọ cung cấp; Ngọc Anh/Tuấn Anh và Dũng nhận; Đức Anh phối hợp context, Dũng review nghiệp vụ.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** Schema chỉ dẫn, fixture AMEND/ADD/REPEAL/UNRESOLVED và test bàn giao.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-06 — Context → Text Diff/Semantic Diff

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Đức Anh + Ngọc Anh + Tuấn Anh

**Vấn đề cần chốt:** Trường context/evidence, tham chiếu AVAILABLE/MISSING/UNRESOLVED; khi nào đủ trước/sau để Text Diff; khi nào Semantic Diff tiếp tục được và giới hạn kết luận; ai yêu cầu bổ sung.

**Phương án để cân nhắc:** Ngữ cảnh tổng quát + nguồn cục bộ/tham chiếu có liên quan; giới hạn theo ngân sách và căn cứ.

**Bên cần thống nhất/review:** Đức Anh, Ngọc Anh, Tuấn Anh; Thọ về truy nguồn, Dũng về nghiệp vụ.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** Context contract/fixture đủ-thiếu căn cứ, context_builder và module.md.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-07 — Text Diff → Semantic Diff

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Ngọc Anh + Tuấn Anh

**Vấn đề cần chốt:** Các trường TextChange/TextDiffResult, chuỗi gốc để tính offset, loại thay đổi, phân biệt null/rỗng, trường hợp bỏ qua diff; quan hệ amendment_id và yêu cầu nguồn.

**Phương án để cân nhắc:** INSERT/DELETE/REPLACE với các vùng old/new; trả object với offset hoặc dạng khác nếu cùng chấp thuận.

**Bên cần thống nhất/review:** Ngọc Anh, Tuấn Anh; Dũng/API và frontend nếu hiển thị vùng diff.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** Schema diff, fixture hai chuỗi và offset, test Text Diff → Semantic Diff.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-08 — Cấu trúc Semantic Change

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Tuấn Anh + Dũng; Ngọc Anh phối hợp đầu vào Text Diff, Đức Anh phối hợp AI Adapter/schema khi liên quan

**Vấn đề cần chốt:** Tên/kiểu/ý nghĩa/trường bắt buộc; ID; nhận định đổi nghĩa/chưa rõ; giải thích, bằng chứng, nội dung cũ/mới; khía cạnh nội bộ; một yêu cầu sinh bao nhiêu thay đổi; output lỗi/không tạo được nhận định.

**Phương án để cân nhắc:** 6, 8, 10 trường hoặc số khác đều là đề xuất; chọn trường theo nhu cầu bên nhận, không theo số lượng cố định trước.

**Bên cần thống nhất/review:** Tuấn Anh phụ trách cả Semantic Change và Scorer; Dũng nhận để tổng hợp/API; Ngọc Anh phối hợp đầu vào Text Diff; Đức Anh phối hợp AI Adapter/schema; frontend cùng review cách hiểu.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** Bảng trường đầy đủ + JSON fixture; schema và mapping sang báo cáo. Không coi bản đề xuất trong tài liệu khác là đã được hai bên chốt.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-09 — Bốn nhóm phân loại và ranh giới nhãn

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Tuấn Anh + Dũng; Ngọc Anh/Đức Anh phối hợp khi liên quan Text Diff hoặc AI Adapter/schema

**Vấn đề cần chốt:** Tên/mã bốn nhóm, định nghĩa, ví dụ ranh giới, một/nhiều nhãn, nơi phân loại; quan hệ field_group nội bộ/category/scoring/operation; ngoài phạm vi và chưa xác định xử lý thế nào.

**Phương án để cân nhắc:** Danh mục bốn mã/tên/định nghĩa cần được điền; không tự suy bốn mã bằng cách gộp tám khía cạnh cũ.

**Bên cần thống nhất/review:** Tuấn Anh, Ngọc Anh, Đức Anh, Dũng; frontend dùng nhãn cùng review.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** Danh mục mã và bảng ánh xạ có fixture; bộ lọc frontend, schema, nhãn chuẩn; chưa nghiệm thu phân loại khi thiếu danh mục.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-10 — Semantic Diff → Classifier & Scorer

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Tuấn Anh (Semantic Change và Scorer); Dũng review phần tích hợp

**Vấn đề cần chốt:** Những trường Scorer đọc; trường được/không được thay; category, significance, critical, reason; ID liên kết; truyền cảnh báo; ca ngữ nghĩa đã rõ nhưng mức tác động chưa đủ căn cứ.

**Phương án để cân nhắc:** Một score/mỗi Semantic Change hoặc phương án khác nếu có căn cứ và bên nhận thống nhất.

**Bên cần thống nhất/review:** Tuấn Anh chốt điểm nối nội bộ giữa Semantic Change và Scorer; Dũng nhận kết quả tích hợp/API và review rubric/nhãn; Ngọc Anh phối hợp Text Diff khi ảnh hưởng đầu vào.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** Contract scoring, fixture ranh giới và test một/một-nhiều; không dùng điểm retrieval thay severity.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-11 — Báo cáo Pipeline → API/frontend

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Dũng + owner phân tích + Tuấn Anh/frontend

**Vấn đề cần chốt:** Envelope và item có những trường nào; định danh/vai trò nguồn; tổng hợp nhiều kết quả; giữ chỉ dẫn chưa phân tích; nguồn để đọc sau khi dọn backend; upload field base_file/amendment_file/reference_files và tương thích doc_v1/doc_s nếu cần.

**Phương án để cân nhắc:** Architecture mục tiêu dùng documents/items và ReviewItem; implementation cũ cần mapping/adapter, không mặc định cùng contract.

**Bên cần thống nhất/review:** Dũng, Tuấn Anh, Ngọc Anh, Thọ khi liên quan nguồn; Đức Anh phối hợp schema/AI Adapter khi cần.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** Schema/fixture báo cáo và upload, API contract, mapping implementation cũ; module.md api/Pipeline.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-12 — Null, rỗng, cảnh báo, lỗi và trạng thái

**Trạng thái:** CHO_DE_XUAT  
**Chủ trì:** Các owner điểm nối; Dũng điều phối tích hợp/API

**Vấn đề cần chốt:** Trường nào nullable; ý nghĩa []/chuỗi rỗng; mã/lý do lỗi, cảnh báo được truyền tới đâu; SUCCESS/PARTIAL/FAILED; lỗi mô hình/retrieval/timeout; điều kiện được kết luận không có thay đổi.

**Phương án để cân nhắc:** Phân biệt không có, chưa biết, chưa chạy và thất bại; report status tách mã HTTP, needs_review và trạng thái người dùng.

**Bên cần thống nhất/review:** Bên cung cấp/nhận, API, frontend; Dũng review các kết luận nghiệp vụ.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Chưa có lựa chọn cuối cùng. Owner điền phương án mong muốn và lý do; các bên liên quan xác nhận trước khi dùng làm đặc tả chính thức.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** Bảng hành vi lỗi/null và fixture từng trường hợp; validator và hiển thị.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-13 — LightRAG HTTP và vòng đời dữ liệu

**Trạng thái:** CHO_CAC_QUYET_DINH_KHAC_HOAN_THANH  
**Chủ trì:** Dũng + Đức Anh; phối hợp owner nguồn/context/ngữ nghĩa và các bên nhận dữ liệu

**Vấn đề cần chốt:** API nhập/sẵn sàng/query/xóa thực tế; chunk/server có chia lại không, metadata được giữ thế nào; index dùng theo comparison; ID mapping; lỗi/retry/idempotency, timeout và cleanup khi client mất kết nối; không xóa vùng dùng chung để dọn một comparison.

**Phương án để cân nhắc:** LightRAG Server riêng qua HTTP đã chốt; còn lựa chọn release, endpoint/payload, cấu hình và cách ly.

**Bên cần thống nhất/review:** Dũng + Đức Anh phụ trách gọi/tích hợp LightRAG; Dũng về Pipeline/API, Thọ về nguồn, Đức Anh về context/AI Adapter khi liên quan, Tuấn Anh/Ngọc Anh về dữ liệu nhận.

**Phương án owner đề xuất:** [Điền lựa chọn cụ thể.]  
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Thứ tự chốt:** Chỉ chốt các chi tiết còn lại của LK-13 sau khi các quyết định khác trong file đã hoàn thành. Trước đó có thể khảo sát/chuẩn bị, không coi là kết luận cuối cùng.

**Kết luận hiện có:** Đã chốt phương án LightRAG Server qua HTTP, không phải tạm chọn; Dũng + Đức Anh phụ trách gọi/tích hợp. Chưa chốt/kiểm chứng release, endpoint, payload, model/embedding, storage, cách ly và lifecycle; không coi phương án đã chốt là đã tích hợp thành công.

**Xác nhận còn cần:** [Ghi người/bên cần đồng ý, hoặc ghi không ảnh hưởng bên khác và lý do.]  
**Đầu ra cần cập nhật:** lightrag_client/config/source_registry, fixture/service smoke test và hướng dẫn chạy; cập nhật module.md context.  
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]


**Điều kiện chuyển sang module.md hoàn thiện:** các quyết định ảnh hưởng đến đặc tả đã chốt và được phản ánh đúng. LK-13 được chốt sau các quyết định còn lại; việc này không làm thay đổi phương án HTTP đã thống nhất. Khi đồng bộ module.md, dùng phân công LK-01 và kiểm tra lại các cặp LK-02.

Các mục “[Điền ...]” và phương án đang cân nhắc chưa phải quyết định đã thông qua. Giữ mã các mục còn lại để không đổi số hàng loạt: CN-09 bị bỏ, CN-10 giữ nguyên mã; phần liên kết kết thúc ở LK-13.
