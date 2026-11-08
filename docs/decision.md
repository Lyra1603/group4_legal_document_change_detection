# DECISION — Lựa chọn triển khai và hợp đồng module

**Dự án:** Legal Document Change Detection — POCS, Nhóm 4
**Phiên bản:** Bản đầu tiên
**Mục đích:** Ghi câu hỏi, lựa chọn của owner, sự thống nhất của bên liên quan và kết luận dùng để hoàn thiện [module.md](module.md).

Tài liệu có hai phần chính: A — quyết định owner về cách triển khai; B — quyết định liên kết/hợp đồng. Đây là lựa chọn thiết kế, không mặc định tồn tại một đáp án đúng duy nhất. Mỗi lựa chọn vẫn phải đáp ứng yêu cầu nghiệp vụ và có thể kiểm chứng bằng mẫu.

Owner có thể đề xuất phương án muốn dùng; chỉ chuyển thành quyết định dự án sau khi có xác nhận phù hợp phạm vi ảnh hưởng. Cấu trúc SemanticChange và các trường bàn giao đã chốt theo schema Đức Anh ở LK-08; owner tiếp tục đề xuất cách triển khai trong cấu trúc đó. Đổi kiểu/trường dùng chung sau này phải được bên giao/nhận review, không tự chọn lại số trường trong báo cáo owner.

**Cách dùng:** phần đã chốt ghi rõ kết luận; phần chưa chốt giữ lựa chọn/kết luận còn trống. Mỗi thay đổi hợp đồng cần đối chiếu schema và fixture trước khi cập nhật module.md. Schema và test đã merge qua PR #2; điều đó chưa xác nhận thuật toán, wiring Pipeline/API hoặc GitHub settings đã hoàn thành.

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

**Cách dùng phần gợi ý bổ sung**

Các bảng dưới đây tham khảo cách trình bày phương án của module-owner-decisions-hci, nhưng chỉ áp dụng phân công, phạm vi và quyết định POCS trong tài liệu này. Hai file decision.md và decision(1).md đính kèm giống nhau; bản bổ sung giữ nguyên nội dung gốc, mã quyết định, trạng thái, owner và kết luận đã chốt.

Mỗi nội dung nhỏ còn mở có hai hoặc ba phương án để cân nhắc. Cột thứ tư ghi phương án C khi cần, hoặc điều kiện phân biệt A/B; không phải mọi hàng đều có ba phương án. Các hàng còn mở là các chiều lựa chọn có thể kết hợp nếu tương thích, không bắt chọn nguyên một cột cho cả module. Hàng ghi “Đã chốt” áp dụng schema chung, không yêu cầu owner chọn lại; chỉ các phần chưa chốt mới cần đề xuất phương án. “Hướng tôi ưu tiên để thử trước” là nhận định thiết kế của người soạn theo phạm vi hiện tại, chưa phải kết quả benchmark hoặc lựa chọn owner. Owner vẫn có thể điều chỉnh/đề xuất phương án khác và phải điền lựa chọn, lý do, phần chưa rõ ở các trường gốc.

Lựa chọn nội bộ chỉ do owner quyết định trong ranh giới đã giao. Đổi input/output, ý nghĩa trạng thái, schema, dữ liệu/nhãn, nguồn lực dùng chung hoặc phạm vi phải có bên thực sự bị ảnh hưởng thống nhất. Tên thành phần hoặc kiểu trường trong các phương án còn mở chỉ mô tả cách hiện thực; dữ liệu bàn giao phải theo schema Đức Anh đã chốt, không tự thành contract mới. LK-01 đã chốt nên không thêm phương án phân công thay thế. LK-13 có phương án khảo sát nhưng vẫn giữ thứ tự chốt sau các quyết định khác. CN-09 không được khôi phục.

Giữ baseline đánh giá hiện hành: matching dự đoán–nhãn chuẩn 1–1 trước, matching 1–n bổ sung sau khi hoàn thành 1–1. Quan hệ một chỉ dẫn–nhiều đích, một amendment–nhiều changes hoặc một change–nhiều aspects là quan hệ dữ liệu nghiệp vụ, không tự thay baseline matching đánh giá. Change F1 ≥ 90% và Critical Change Recall ≥ 95% là các ngưỡng dự tính và có thể thay đổi sau khi hoàn thiện test_evaluation_plan.md; chưa phải ngưỡng nghiệm thu chính thức. Các ngưỡng similarity/retrieval nội bộ phải được thiết kế và đo riêng, không lấy hai tỷ lệ này áp sang thuật toán.

**Nguồn kỹ thuật dùng để đối chiếu gợi ý:** [S1] [LightRAG Server — tài liệu chính thức](https://github.com/HKUDS/LightRAG/blob/main/docs/LightRAG-API-Server.md); [S2] [Python difflib — tài liệu chính thức](https://docs.python.org/3/library/difflib.html). Đã đối chiếu ngày 08/11/2026; các trang có thể thay đổi, vì vậy release và cấu hình triển khai thật vẫn phải được cố định và thử nghiệm. Nguồn này hỗ trợ kiểm tra khả năng/kỹ thuật, không xác nhận lựa chọn thiết kế phù hợp nhất cho dữ liệu POCS.

## Quyết định dùng schema Đức Anh làm hợp đồng chung

Nhóm đã chốt dùng contracts.py, validation.py và report_validation.py của Đức Anh tại commit `b6a13f98b9a7357b9fbb0936aba6bda065d03fcb` trên nhánh `feat/ducanh-backend-integration` làm hợp đồng chung. Hợp đồng đã merge vào main qua [PR #2](https://github.com/Lyra1603/group4_legal_document_change_detection/pull/2), commit `a8a906a474a67e89195987ca757f7315c22231db` (schema commit `99907a8e738019c9e20ceb8fd3582ab8f238555d`). Quyết định này xác định kiểu/trường và các ràng buộc validator hiện có, không chốt thay thuật toán của owner, rubric nghiệp vụ, endpoint/upload hoặc dữ liệu nhận xét frontend.

ComparisonReport có comparison_id, base_document, amendment_document, reference_documents, status, results, warnings, errors. results là list[AmendmentResult]; mỗi kết quả có amendment, text_diff, semantic_diff, scoring. Các kiểu AmendmentItem, SemanticChange, ChangeAspect, SemanticDiffResult, TextDiffResult và ScoringResult giữ theo code căn cứ. Mọi khóa TypedDict bắt buộc có mặt; Optional cho phép null, không cho phép bỏ khóa.

Tám nhóm field_group/category và ràng buộc significance theo report_validation.py; không tiếp tục yêu cầu danh mục bốn nhóm hoặc đổi envelope sang dạng báo cáo phẳng. Phân công LK-01, phương án LightRAG HTTP và thứ tự chốt LK-13 giữ nguyên. Phần hướng dẫn chi tiết và phạm vi nhận xét frontend theo SRS mục 1.7–1.8.

Các giới hạn validator đã merge nhưng chưa được quyết định sửa trong đợt này: change_id chưa được kiểm tra duy nhất xuyên các amendment; chưa kiểm tra reconstruction toàn Text Diff; các trường old_quote/new_quote không tự được kiểm chứng như EvidenceRef; PARTIAL/FAILED chưa được kiểm tra mọi điều kiện nghiệp vụ. Schema đã ở main; không diễn giải “qua schema” thành “đúng nghiệp vụ” hoặc “Pipeline đã gọi validator”. Xem [hướng dẫn schema](schema-integration.md).

## A. Quyết định của owner về cách triển khai

Phần này ưu tiên những lựa chọn nằm trong module. Nếu đổi output, dependency chung, chi phí/vận hành hoặc yêu cầu bên khác thay code thì phải kết hợp quyết định LK tương ứng. Lựa chọn nội bộ được owner chốt và thông báo/review theo phạm vi ảnh hưởng, không bắt cả nhóm duyệt từng hàm phụ.

### CN-01 — Đọc/chuyển đổi và parse tài liệu

**Trạng thái:** CHO_DE_XUAT
**Chủ trì:** Thọ

**Vấn đề cần chốt:** Công cụ/phiên bản PDF → DOCX; cách nhận diện Điều/Khoản/Điểm; giữ bảng/outside; xử lý đánh số Word và bố cục khó; kiểm tra sau chuyển đổi.

**Phương án để cân nhắc:** Giữ converter/Parser hiện có; bổ sung adapter, normalization hoặc thay phương pháp nội bộ nếu có kiểm chứng.

**Gợi ý cụ thể cho từng nội dung cần chốt (chưa phải lựa chọn của owner):**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| PDF → DOCX và phiên bản | Giữ converter hiện có, cố định phiên bản/cấu hình để có baseline. | Thử converter thay thế sau cùng giao diện, chỉ áp dụng nếu giữ nguồn và bố cục tốt hơn trên bộ mẫu. | Ưu tiên A để ít sửa dây chuyền; B cần so sánh cùng file, thời gian, lỗi và dependency. |
| Nhận diện Điều/Khoản/Điểm | Quy tắc theo nhãn và cấp cấu trúc, có điều kiện tránh nhận nhầm câu dẫn chiếu. | Quy tắc kết hợp style/đánh số Word và trạng thái đọc để xử lý nhãn không nằm trong text. | Không lấy style làm căn cứ duy nhất; giữ ca chưa nhận diện và cảnh báo. |
| Bảng và nội dung ngoài Điều | Giữ block có thứ tự và loại block; node pháp lý tham chiếu block. | Giữ bảng/outside trong cây native rồi adapter xuất sang contract chung. | A thuận truy nguồn; B ít thay Parser nhưng phải kiểm tra không mất thứ tự hoặc bảng. |
| Chuẩn hóa và bố cục khó | Chuẩn hóa trên bản phụ; bảo toàn chuỗi gốc và mapping vị trí. | Chỉ chuẩn hóa nhãn cấu trúc, giữ nguyên toàn bộ nội dung cho bước sau. | A hỗ trợ matching nhưng tốn mapping; B đơn giản hơn, cần kiểm tra biến thể khoảng trắng/Unicode. |
| Kiểm tra sau chuyển đổi | Đối chiếu chữ, thứ tự và số đơn vị kỳ vọng được review độc lập. | Kết hợp các kiểm tra tự động với review trực quan ca có cảnh báo/bảng/bố cục khó. | Không dùng summary tự đếm làm bằng chứng duy nhất; không tự bổ sung OCR ngoài phạm vi. |

**Hướng tôi ưu tiên để thử trước:** Giữ converter/Parser hiện có, bổ sung adapter và ca kiểm tra lỗi; chỉ thay công cụ sau so sánh trên cùng mẫu.

**Ràng buộc và phần cần phối hợp:** Thọ tự chọn implementation nội bộ; đổi cây/nguồn/offset cần LK-03/LK-04 và bên nhận review. Không đổi folder chính hoặc coi vị trí DOCX chuyển đổi là trang PDF đã xác minh.

**Bằng chứng cần có trước khi chốt:** Mẫu DOCX/PDF có đánh số Word, bảng, outside và câu dẫn chiếu; expected tree/đếm từ nguồn độc lập, nguyên văn và vị trí nguồn; ghi phiên bản và lỗi chuyển đổi.

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

**Gợi ý cụ thể cho từng nội dung cần chốt (chưa phải lựa chọn của owner):**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Nhận diện chỉ dẫn và thao tác | Rule theo mẫu sửa/thay/bổ sung/bãi bỏ, tách từng yêu cầu. | Rule tạo ứng viên rồi bộ phân tích có mô hình hỗ trợ ca khó. | B chỉ dùng khi có lợi trên mẫu; mô hình không tự xác nhận đích hoặc nguồn. |
| Văn bản đích và locator | Ưu tiên số hiệu/văn bản đích và Điều/Khoản/Điểm được nêu trực tiếp. | Dùng cấu trúc xác định phạm vi, đối chiếu cụm từ để phân biệt ứng viên. | Nếu nhiều đích vẫn hợp lý, giữ UNRESOLVED và danh sách ứng viên thay vì chọn bắt buộc. |
| Nội dung trước/sau cục bộ | Áp phép sửa xác định vào đúng chuỗi V1, lưu chỉ dẫn và cách tạo after. | Chỉ bàn giao chuỗi trích trực tiếp hoặc suy ra duy nhất; ca còn lại giữ chưa xác định. | A bao phủ thêm ca nhưng phải kiểm tra nhiều lần xuất hiện; B bảo thủ hơn và có thể giảm độ bao phủ. |
| Nhiều chỉ dẫn và hiệu lực | Áp theo thứ tự nguồn khi có căn cứ rõ, phát hiện xung đột. | Lập các phép sửa độc lập rồi kiểm tra chồng lấn trước khi dựng kết quả. | Không tự giả định thứ tự pháp lý; hiệu lực chỉ lấy từ nguồn, không thay bằng ngày ban hành. |
| Tiêu chí liên kết mơ hồ | Chấp nhận khi đích và thao tác xác định duy nhất theo quy tắc. | Kết hợp các tín hiệu có rubric và điều kiện chấp nhận được review trên pilot. | Điểm tương đồng chỉ là tín hiệu; ngưỡng liên kết nội bộ phải được đo riêng, không lấy 90%/95% đánh giá làm ngưỡng matching. |

**Hướng tôi ưu tiên để thử trước:** Rule và cấu trúc làm baseline; đối chiếu nội dung hỗ trợ khi cần, giữ chưa xác định nếu thiếu căn cứ.

**Ràng buộc và phần cần phối hợp:** Đổi trường chỉ dẫn/before/after theo LK-05. Matching chỉ dẫn–đích ở đây khác matching dự đoán–nhãn chuẩn trong đánh giá; phạm vi đánh giá vẫn 1–1 trước.

**Bằng chứng cần có trước khi chốt:** Ca sửa cụm từ lặp, thay toàn đơn vị, ADD/REPEAL, S sửa văn bản khác, nhiều đích và hiệu lực có ngoại lệ; giải thích được vì sao chọn hoặc từ chối từng đích.

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

**Gợi ý cụ thể cho từng nội dung cần chốt (chưa phải lựa chọn của owner):**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Chia và ghép chunk | Chunk theo Điều/Khoản/Điểm, giữ câu dẫn cần thiết. | Chunk cấu trúc kết hợp cửa sổ đoạn khi đơn vị quá dài. | A dễ truy nguồn; B cần mapping phần cắt và kiểm tra không tách điều kiện/ngoại lệ khỏi nội dung. |
| Giữ câu dẫn và tránh full_text lặp | Lấy segments/block lá, thêm câu dẫn có nguồn đúng một lần. | Dùng full_text của cấp được chọn, không đồng thời nạp lại full_text cấp con. | Hai cách đều cần khóa chống trùng theo nguồn/span; trùng văn bản không tự có nghĩa trùng tài liệu. |
| Tạo query | Query từ chỉ dẫn, locator và đoạn trước/sau liên quan. | Tách query cho nội dung chính, định nghĩa và dẫn chiếu rồi hợp nhất có giới hạn. | B phù hợp ngữ cảnh phân tán; cần đo lợi ích so với lượng truy vấn tăng. |
| Số kết quả và ngân sách | Giới hạn cố định top-k và token, chọn cấu hình sau pilot. | Ngân sách thích nghi theo loại chỉ dẫn và mức thiếu căn cứ, có trần dừng. | Không tự điền k/token như đã chốt; nếu bị cắt phải ghi giới hạn, không kết luận chắc chắn đủ căn cứ. |
| Kiểm tra quote và chọn căn cứ | Đối chiếu nguyên văn và vị trí trên registry rồi chọn đoạn liên quan. | Đối chiếu nguyên văn kèm kiểm tra vai trò tài liệu, phạm vi và dẫn chiếu. | Quote tồn tại chưa chứng minh suy luận đúng; retrieval score không là mức tác động. |
| Truy xuất bổ sung | Một lượt retrieval để lập baseline dễ kiểm tra. | Lượt bổ sung có điều kiện khi chỉ ra được nhu cầu cụ thể, giới hạn số lượt. | Không tự thu thập tài liệu ngoài bộ người dùng đã cung cấp; hết ngân sách thì báo chưa rõ. |

**Hướng tôi ưu tiên để thử trước:** Chunk cấu trúc, nguồn gốc rõ, một lượt query làm baseline; thử cửa sổ hoặc lượt bổ sung trên ca thiếu ngữ cảnh.

**Ràng buộc và phần cần phối hợp:** Đức Anh phụ trách context; phối hợp Thọ về nguồn, Dũng + Đức Anh về client HTTP. Đổi output theo LK-06; không để query rỗng tự thành MISSING.

**Bằng chứng cần có trước khi chốt:** Fixture đơn vị dài, câu dẫn chung, định nghĩa/ngoại lệ ở đoạn khác, dẫn chiếu đủ/thiếu; đo căn cứ tìm được và trùng lặp với cùng bộ đầu vào.

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

**Gợi ý cụ thể cho từng nội dung cần chốt (chưa phải lựa chọn của owner):**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Vị trí LightRAG Server | Server riêng trên cùng máy qua localhost. | Server riêng trên máy khác có địa chỉ và quyền truy cập được cấu hình. | Cả hai đều HTTP đã chốt; A dễ thử cục bộ, B cần mạng và người vận hành. |
| Release và cấu hình | Cố định release đã chạy smoke test, lưu cấu hình tái lập. | Thử release khác trong môi trường tách biệt rồi so sánh trước khi chuyển. | Không chốt số phiên bản theo tên mới nhất; API và hành vi phải kiểm chứng trên bản dùng thật [S1]. |
| LLM/embedding và tài nguyên | Dùng dịch vụ mô hình qua cấu hình adapter, đo chất lượng/chi phí. | Chạy mô hình trên tài nguyên nhóm kiểm soát nếu có đủ năng lực và quyền dùng. | Có thể tách nơi chạy LLM/embedding; localhost của LightRAG không bảo đảm toàn hệ thống offline. |
| Storage và cache | Dùng cấu hình lưu trữ tối thiểu đã kiểm chứng, cache theo phạm vi comparison. | Dùng storage phù hợp máy dịch vụ, cache có khóa gồm phiên bản dữ liệu và cấu hình. | Không tái sử dụng cache giữa các nguồn/cấu hình khác nhau nếu chưa kiểm chứng tính đúng và cách ly. |
| Timeout, retry và chi phí | Deadline theo giai đoạn, retry hữu hạn cho lỗi tạm thời an toàn. | Deadline tổng và ngân sách theo comparison, phân bổ từng bước và dừng khi hết. | Không retry nhập dữ liệu mù; cần idempotency/trạng thái theo LK-13, thông số do pilot xác định. |
| Điều kiện sẵn sàng | Kiểm tra dịch vụ rồi xác nhận bộ tài liệu của lượt chạy đã index xong. | Smoke test dịch vụ và thử retrieval nguồn đã biết trước khi cho dùng cấu hình. | Health/API hoạt động chưa chứng minh index sẵn sàng hoặc kết quả đúng. |

**Hướng tôi ưu tiên để thử trước:** Server HTTP cùng máy để kiểm chứng luồng; cố định release/cấu hình và đo tài nguyên trước khi chuyển máy hoặc thêm storage.

**Ràng buộc và phần cần phối hợp:** Dũng + Đức Anh phối hợp người chịu tài nguyên/chi phí. Đây là phương án khảo sát; chi tiết liên quan LK-13 vẫn chốt sau các quyết định khác. Không đưa endpoint/payload chưa thử thành contract.

**Bằng chứng cần có trước khi chốt:** Cấu hình có thể chạy lại, thời gian nhập/query, phản hồi lỗi, cache cũ, mất kết nối và lần chạy mới; ghi dịch vụ mô hình nào cần mạng.

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

**Gợi ý cụ thể cho từng nội dung cần chốt (chưa phải lựa chọn của owner):**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Đơn vị so sánh | Diff theo ký tự để giữ tọa độ trực tiếp trên chuỗi gốc. | Diff theo token/từ rồi ánh xạ về offset ký tự. | C: diff đoạn/dòng trước rồi tinh chỉnh vùng khác theo từ/ký tự; phù hợp đoạn dài nhưng nhiều bước mapping. |
| Thuật toán baseline | SequenceMatcher làm baseline so sánh chuỗi dễ thử; ghi rõ cấu hình heuristic [S2]. | Thuật toán edit-script như Myers nếu cần kiểm soát chuỗi thao tác và đã có implementation được kiểm tra. | Không khẳng định SequenceMatcher cho edit-script ngắn nhất; so sánh theo reconstruction, vị trí và độ dễ đọc. |
| Chuẩn hóa tiếng Việt/dấu câu | Không chuẩn hóa chuỗi dùng làm offset; chỉ tạo bản phụ để hỗ trợ so sánh. | Chuẩn hóa có mapping hai chiều về chuỗi gốc. | Không bỏ dấu, từ phủ định, đơn vị hoặc dấu so sánh; cần kiểm tra Unicode tổ hợp. |
| Nhóm vùng đổi | Giữ thao tác nhỏ, chỉ gộp vùng kề nhau theo quy tắc rõ. | Nhóm theo cụm nghĩa để hiển thị, nhưng giữ các thao tác nền để kiểm tra. | Không gộp làm mất thay đổi độc lập; quy tắc trình bày không thay kết luận ngữ nghĩa. |
| Reconstruction và offset | Kiểm tra áp edit-script vào before tạo đúng after. | Kiểm tra reconstruction cùng mọi slice old/new, ca biên và Unicode. | B mạnh hơn ở bàn giao; cần thống nhất khoảng nửa mở và đơn vị offset theo LK-04/LK-07. |

**Hướng tôi ưu tiên để thử trước:** Dùng ký tự hoặc token có mapping về chuỗi gốc làm baseline; lựa chọn cuối theo kết quả fixture và khả năng bên nhận sử dụng.

**Ràng buộc và phần cần phối hợp:** Ngọc Anh tự chọn thuật toán; Tuấn Anh và frontend review dữ liệu nhận. Chỉ chạy trên nội dung cục bộ đủ căn cứ; null/rỗng theo LK-12.

**Bằng chứng cần có trước khi chốt:** Thêm/xóa/thay, số/đơn vị, phủ định, dấu câu, text lặp và tiếng Việt; reconstruction đúng và slice khớp nguồn cho cả hai phía.

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

**Gợi ý cụ thể cho từng nội dung cần chốt (chưa phải lựa chọn của owner):**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Phương pháp phân tích | Rule trên các biến đổi rõ ràng làm baseline có phạm vi được công bố. | LLM nhận before/after, chỉ dẫn, context và output có cấu trúc qua AI Adapter. | C: rule tìm tín hiệu, LLM phân tích ca còn lại; ưu tiên thử nhưng phải đánh giá riêng từng thành phần. |
| Chia/gộp nhận định | Một nhận định cho cùng quy định/nghĩa vụ, nhiều aspects bên trong. | Tách theo các tác động độc lập có căn cứ và liên kết chung amendment_id. | Không tách chỉ vì khác field_group; quy tắc chia/gộp phải thống nhất với gold và LK-08. |
| Prompt và ngữ cảnh | Một lần phân tích có cấu trúc với context đã xác minh nguồn. | Tách trích khía cạnh/bằng chứng rồi tổng hợp nhận định, có kiểm tra giữa bước. | B dễ quan sát lỗi nhưng tăng chi phí; không dùng prompt để bù dữ liệu nguồn chưa có. |
| Kiểm chứng bằng chứng | Validate schema, quote và định danh nguồn bằng code. | Kết hợp validator với lượt review tính liên quan của bằng chứng và kết luận. | Review bằng mô hình chỉ là hỗ trợ; quote có thật chưa đủ chứng minh suy luận pháp lý đúng. |
| Sai output hoặc thiếu căn cứ | Trả trạng thái chưa xác định/lỗi theo contract, giữ phần nguồn đã có. | Sửa định dạng qua lượt gọi hữu hạn, rồi validate lại; nếu vẫn sai thì giữ lỗi. | Không tự bịa nội dung sau sửa; không biến hết retry thành không có thay đổi. |

**Hướng tôi ưu tiên để thử trước:** So sánh baseline rule với LLM có cấu trúc; nếu dùng hybrid, ghi rõ ca nào do thành phần nào xử lý.

**Ràng buộc và phần cần phối hợp:** Tuấn Anh phụ trách nội dung nghĩa; Dũng + Đức Anh cung cấp adapter. Không tự suy tác động hoặc hiệu lực từ tài liệu ngoài đầu vào; không thay trường đã chốt hoặc danh mục tám nhóm của hợp đồng chung.

**Bằng chứng cần có trước khi chốt:** Ca chỉ đổi diễn đạt, đổi phủ định/chủ thể/thời hạn, nhiều aspects, thiếu dẫn chiếu và quote không hỗ trợ kết luận; chấm theo matching 1–1 hiện tại.

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

**Gợi ý cụ thể cho từng nội dung cần chốt (chưa phải lựa chọn của owner):**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Áp rubric | Rule theo rubric và ví dụ ranh giới đã review, tạo lý do từ căn cứ. | LLM áp rubric có cấu trúc, validator kiểm tra mức và lý do. | C: LLM đề xuất, rule kiểm tra nhất quán và trả cần review khi xung đột. |
| Ranh giới mức | Bảng quyết định với ví dụ đối chứng giữa hai mức kề nhau. | Rubric theo tiêu chí có căn cứ rồi tổng hợp mức theo quy tắc rõ. | Không đếm số chữ đổi hoặc lấy retrieval score làm mức tác động; trọng số nếu có phải được review. |
| Thiếu căn cứ | Cho mức và critical chưa xác định, kèm lý do/căn cứ thiếu. | Chấm phần nhận định đủ căn cứ, giữ phần khác chưa xác định qua kết quả từng change. | Không gán LOW/false chỉ để output có giá trị; kiểu và trạng thái theo LK-10/LK-12. |
| Severity/critical | Suy cờ critical từ mức CRITICAL đã xác định theo contract. | Tính hai trường rồi validator buộc nhất quán; xung đột được trả review/lỗi. | A ít nguồn mâu thuẫn hơn; B chỉ dùng khi cần kiểm tra độc lập và có cách giải quyết rõ. |

**Hướng tôi ưu tiên để thử trước:** Rubric có ví dụ ranh giới và rule kiểm tra nhất quán; dùng mô hình hỗ trợ khi có bằng chứng cải thiện.

**Ràng buộc và phần cần phối hợp:** Rubric, ý nghĩa mức và nhãn do Tuấn Anh phối hợp Dũng review; đổi output cần LK-09/LK-10. Phân biệt severity nghiệp vụ với ngưỡng F1/Recall đánh giá.

**Bằng chứng cần có trước khi chốt:** Cặp ca gần ranh giới, cùng thay đổi ở ngữ cảnh khác nhau, thiếu căn cứ, thêm/xóa không mặc định CRITICAL; reason truy được bằng chứng.

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

**Gợi ý cụ thể cho từng nội dung cần chốt (chưa phải lựa chọn của owner):**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Thư viện/nhà cung cấp | Một provider qua adapter nhỏ, cô lập SDK và cấu hình. | Giao diện provider chung với hai implementation khi nhóm cần so sánh thực tế. | Không thêm nhiều provider chỉ để dự phòng; cần quyền dùng, chi phí và khả năng validate output. |
| Phạm vi adapter | Phục vụ Semantic Diff trước, Scorer dùng rule riêng. | Dùng chung cơ chế gọi/timeout/validation cho Semantic Diff và Scorer, prompt riêng từng nhiệm vụ. | B tái sử dụng hạ tầng; adapter không sở hữu quyết định ngữ nghĩa/rubric của Tuấn Anh. |
| Model và ngân sách | Một cấu hình cố định cho baseline, ghi model/phiên bản, token và thời gian đo được. | Profile theo nhiệm vụ: phân tích và chấm điểm có giới hạn riêng, tổng ngân sách comparison. | Chưa chốt model/token/cost; thay cấu hình ảnh hưởng thí nghiệm phải ghi nhận và chạy lại phần liên quan. |
| Parse/validate output | Output có cấu trúc và schema, từ chối trường/giá trị sai theo contract. | Kết hợp kiểm tra định dạng của provider nếu có với validator nghiệp vụ ở backend. | Không coi JSON hợp lệ là đúng ngữ nghĩa; không lặng lẽ điền default có ý nghĩa pháp lý. |
| Quote, retry và fallback | Kiểm tra quote/nguồn bằng code; lỗi thì giữ kết quả chưa xác định. | Sửa định dạng qua số lượt hữu hạn rồi kiểm tra lại; fallback rule chỉ cho phạm vi rule chứng minh được. | Fallback phải được đánh dấu; không âm thầm đổi mô hình/cách tính trong đợt đánh giá cố định. |
| Logging | Log metadata tối thiểu: request ID, model, thời gian, trạng thái và lỗi. | Trace từng bước với prompt/template version và hash nguồn, nội dung chỉ khi có phạm vi lưu được đồng ý. | Không ghi khóa hoặc toàn văn mặc định; giữ đủ thông tin tái lập mà không biến log thành kho tài liệu. |

**Hướng tôi ưu tiên để thử trước:** Một adapter gọn với schema/quote validation và deadline; mở dùng chung theo nhu cầu Semantic Diff/Scorer.

**Ràng buộc và phần cần phối hợp:** Dũng + Đức Anh phối hợp; Tuấn Anh review lời gọi/return theo LK-02/LK-12. Phân công nội bộ được ghi rõ, không chuyển ownership nội dung nghĩa cho adapter.

**Bằng chứng cần có trước khi chốt:** Phản hồi hợp lệ, JSON lỗi, sai enum/quote, timeout, hết ngân sách và fallback; mock để phát triển nhưng phải có chạy thật khi xác nhận tích hợp.

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

**Gợi ý cụ thể cho từng nội dung cần chốt (chưa phải lựa chọn của owner):**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Bộ ca tự kiểm tra | Fixture nhỏ có expected output được review và lệnh chạy tự động. | Kết hợp fixture nhỏ với mẫu thật đại diện và review thủ công ca khó. | B ưu tiên khi bàn giao; không lấy output thuật toán làm expected output tự động. |
| Kiểm tra hợp đồng/nghiệp vụ | Tách validator/contract test với đối chiếu đáp án nghiệp vụ. | Chạy pipeline thu nhỏ qua điểm nối rồi đối chiếu cả contract và căn cứ. | A định vị lỗi nhanh; B chứng minh bên nhận dùng được; có thể kết hợp. |
| Baseline và phép đo | So sánh với phương pháp đơn giản trên dữ liệu phát triển chung. | So sánh cấu hình có/không thành phần cải thiện để tìm đóng góp cụ thể. | Cần cùng nhiệm vụ/đầu vào; baseline yếu không tự chứng minh chất lượng đủ dùng. |
| Tài nguyên và tái lập | Một lệnh chạy, cấu hình và dependency cố định. | Bổ sung profile đo thời gian/chi phí và giả lập lỗi dependency. | Mock phải ghi rõ; chốt các con số sau khi đo, không đưa số giả làm yêu cầu đã đạt. |
| Giới hạn và đánh giá | Báo từng ca đạt hợp đồng/chưa đạt/bị chặn cùng bằng chứng. | Bổ sung Precision/Recall/F1 và phân tích lỗi khi đã có nhãn/matching đủ rõ. | Matching 1–1 trước; F1 90% và Critical Recall 95% chỉ dự tính, có thể thay đổi sau khi hoàn thiện test_evaluation_plan.md. |

**Hướng tôi ưu tiên để thử trước:** Fixture có căn cứ kết hợp mẫu thật và chạy điểm nối; đo chất lượng theo kế hoạch do Đức Anh điều phối.

**Ràng buộc và phần cần phối hợp:** Owner tự kiểm tra, bên nhận review; không tạo Evaluator độc lập. Ngưỡng dự tính không biến thành điều kiện nghiệm thu chính thức chỉ vì có trong phương án.

**Bằng chứng cần có trước khi chốt:** Input/expected/actual, phiên bản, lệnh chạy, reviewer, giới hạn; có ca lỗi và thiếu căn cứ, không chỉ một ví dụ thành công.

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

**Trạng thái:** CHOT_MOT_PHAN
**Chủ trì:** Hai owner tại mỗi điểm nối; Dũng điều phối tích hợp/API, Đức Anh phối hợp schema và AI Adapter theo phạm vi liên quan.

**Phần đã chốt theo schema:** Dùng các TypedDict của schema Đức Anh tại các điểm nối. Trong backend, payload bàn giao là dict/list theo contracts.py; LightRAG vẫn là ranh giới HTTP.

**Phần còn cần quyết định:** Tên public function, tham số gọi, mapping dữ liệu native, cách trả lỗi và fixture từng cặp.

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

**Gợi ý cho phần hiện thực còn mở và nội dung đã chốt theo schema:**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Giao diện module trong backend | Hàm nhận/trả dict/list có annotation TypedDict của schema chung. | Adapter chuyển biểu diễn nội bộ sang cùng dict/list đã validate. | Đã chốt kiểu payload bàn giao; hai phương án chỉ khác nơi thực hiện chuyển đổi. |
| Giao diện adapter AI/LightRAG | Wrapper hẹp chuyển request/response dịch vụ sang contract nội bộ. | Wrapper hẹp kết hợp đối tượng kết quả có trạng thái/lỗi chung. | LightRAG vẫn HTTP; không để payload dịch vụ thô lan sang Pipeline hoặc ép mọi module dùng HTTP. |
| Chốt chữ ký và dữ liệu | Bảng function/params/return và một fixture hợp lệ/sai cho từng cặp. | Schema chung kèm contract test và ví dụ cách gọi của bên nhận. | Cần đủ cả ý nghĩa, ID/nguồn, null/rỗng/lỗi; không chốt chỉ bằng tên JSON. |
| Phiên bản và thay đổi contract | Một phiên bản chung, cập nhật hai bên cùng đợt tích hợp. | Adapter chuyển đổi tạm khi hai bên phải chuyển theo đợt, có điều kiện gỡ. | Không tồn tại hai API chính thức mâu thuẫn; giữ phiên bản fixture khớp code. |

**Hướng tôi ưu tiên để thử trước:** Schema chung và public function hẹp; mỗi cặp có fixture đã được cả hai bên dùng thử.

**Ràng buộc và phần cần phối hợp:** Giữ toàn bộ cặp và phân công LK-01; các hàng là hướng áp dụng cho từng cặp, không biến tất cả thành chuỗi runtime. LK-13 còn chờ thứ tự chốt riêng.

**Bằng chứng cần có trước khi chốt:** Hai bên chạy cùng fixture, truyền output thật qua điểm nối; ca sai kiểu, thiếu field, lệch ID, lỗi upstream và phiên bản cũ.

**Mỗi cặp cần điền:** tên public function/API, tham số, kiểu và cấu trúc return; trường bắt buộc/tùy chọn; ID, nguồn/offset; ý nghĩa null/rỗng/lỗi; phiên bản hợp đồng và một bộ input/output mẫu hai bên đã review.

**Cách trao đổi:** Các module cùng backend gọi hàm với dict/list theo TypedDict; biểu diễn nội bộ khác cần chuyển đổi ở boundary; JSON dùng lưu fixture hoặc trao đổi khi hai bên chọn. LightRAG là ranh giới HTTP đã chốt; không bắt mọi cặp dùng HTTP hoặc ghi file JSON.

**Kết luận hiện có:** Kiểu dữ liệu và ràng buộc nêu ở phần đã chốt áp dụng theo quyết định nhóm. Chỉ phần còn cần quyết định mới tiếp tục nhận đề xuất; không coi thuật toán hoặc tích hợp đã hoàn thành.

**Đầu ra cần cập nhật:** từng hợp đồng LK-03 đến LK-12, schema/fixture và module.md sau khi hai bên thống nhất. LK-13 được hoàn thiện sau theo thứ tự riêng.

### LK-03 — Parser → Adapter/Linker/Context

**Trạng thái:** CHOT_MOT_PHAN
**Chủ trì:** Thọ + Đức Anh

**Phần đã chốt theo schema:** Dùng ExtractedDocument(document_id, role, filename, file_type, blocks), SourceBlock(source_ref, text) và Clause(unit_id, id, title, content, source_refs).

**Phần còn cần quyết định:** Cách chuyển cây Parser/native sang contract, giữ bảng/outside/segments và kiểm chứng số đếm; cây native chưa được schema chung định nghĩa lại.

**Vấn đề cần chốt:** Cấu trúc cây, node/children, content/full_text/segments, bảng/outside, summary, status/warnings; định danh và mapping từ cây sang đầu ra bên nhận. Số đếm kỳ vọng lấy từ đâu để phát hiện bỏ sót.

**Phương án cho phần còn mở:** Giữ cây native và adapter xuất ExtractedDocument/Clause đã chốt; so sánh cách mapping và giữ metadata, không chọn contract bàn giao khác.

**Gợi ý cho phần hiện thực còn mở và nội dung đã chốt theo schema:**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Biểu diễn cây bàn giao | Giữ cây native nội bộ, adapter xuất ExtractedDocument/Clause. | Bổ sung lớp truy cập cây/registry nội bộ nhưng boundary vẫn xuất ExtractedDocument/Clause. | Contract bàn giao đã chốt; không thêm cây node hoặc field mới vào payload chung. |
| content/full_text/segments | Một nguồn nội dung chính là segments; full_text được tổng hợp có quy tắc. | Giữ các trường native nhưng công bố trường có thẩm quyền cho từng thao tác. | Không để bên nhận cộng cả parent/child full_text rồi đếm hoặc index trùng. |
| Bảng/outside và thứ tự | Block có loại, thứ tự và nguồn; node tham chiếu block. | Bảng/outside nằm trong cây và adapter cung cấp cách duyệt theo thứ tự nguồn. | Không được mất nội dung chỉ vì không thuộc Điều; định dạng bảng phải được fixture kiểm tra. |
| summary và số kỳ vọng | summary báo số đã parse; expected count do reviewer đọc nguồn độc lập. | Bổ sung danh sách vị trí/ID kỳ vọng để kiểm tra cả đếm và bao phủ. | Đếm đúng chưa bảo đảm nội dung đúng; số kỳ vọng không sao chép từ summary. |
| Trạng thái và mapping | Giữ status/warnings native trong nội bộ và ánh xạ ra ProcessingIssue khi tổng hợp. | Adapter trả metadata native riêng cho Pipeline khi cần, không đổi schema chung. | Không thêm envelope runtime mới hoặc đưa cây rỗng như parse thành công. |

**Hướng tôi ưu tiên để thử trước:** Giữ Parser hiện có, adapter xuất contract ổn định và registry để các bên nhận không phụ thuộc dict native.

**Ràng buộc và phần cần phối hợp:** Thọ + Đức Anh cùng chốt; Ngọc Anh/Tuấn Anh review nếu dùng trực tiếp. ID/offset theo LK-04; không đổi biểu diễn ngoài ranh giới mà chưa có mapping.

**Bằng chứng cần có trước khi chốt:** Cây nhiều cấp, bảng, outside, nguồn không có Điều, lệch số đếm và lỗi parse; truy ngược mỗi phần bàn giao về nguồn.

**Bên cần thống nhất/review:** Thọ và Đức Anh; Ngọc Anh/Tuấn Anh nếu dùng trực tiếp; Dũng review mẫu nguồn.

**Phương án owner đề xuất cho phần còn mở:** [Điền lựa chọn cụ thể, giữ schema đã chốt.]
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Kiểu dữ liệu và ràng buộc nêu ở phần đã chốt áp dụng theo quyết định nhóm. Chỉ phần còn cần quyết định mới tiếp tục nhận đề xuất; không coi thuật toán hoặc tích hợp đã hoàn thành.

**Xác nhận còn cần:** Bên liên quan review phương án/fixture cho phần còn mở; quyết định dùng schema Đức Anh đã được nhóm xác nhận.
**Đầu ra cần cập nhật:** Contract cây/adapter, JSON fixture và test parse; module.md document_processing/context.
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-04 — Định danh, nguồn và offset

**Trạng thái:** CHOT_MOT_PHAN
**Chủ trì:** Thọ + Đức Anh + Tuấn Anh

**Phần đã chốt theo schema:** DocumentIdentity dùng v1/BASE, s/AMENDMENT, các reference có ID riêng và role REFERENCE. EvidenceRef gồm document_id, source_refs, quote; block:N được giữ khi tồn tại đúng tài liệu và quote khớp nguyên văn. Offset TextChange theo chỉ số Python [start,end) trên đúng chuỗi.

**Phần còn cần quyết định:** Cách tạo unit/chunk ID, ổn định qua lần chạy, mapping PDF và chuyển offset frontend. Validator chỉ kiểm tra change_id trong từng result, chưa chốt tính duy nhất toàn comparison.

**Vấn đề cần chốt:** document_id/role, unit/node ID, source_ref/spans, trích nguyên văn, đơn vị offset và chuẩn hóa chuỗi; metadata chunk; phạm vi duy nhất của ID; nguồn DOCX chuyển đổi so với PDF gốc.

**Phương án để cân nhắc:** Giữ block:N và offset Python hiện có, thêm adapter cho frontend khi cần; mapping PDF chỉ dùng khi kiểm chứng.

**Gợi ý cho phần hiện thực còn mở và nội dung đã chốt theo schema:**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| document_id và vai trò | Đã chốt: v1/BASE, s/AMENDMENT; reference có ID riêng và role REFERENCE. | Phương án còn mở: lưu hash/namespace nội bộ ngoài payload chung. | Không đổi document_id đã dùng trong report và EvidenceRef theo cách tạo ID mới. |
| unit/block/chunk ID | ID cục bộ được ghép với document_id và comparison_id. | ID có tiền tố loại đối tượng, registry ánh xạ về đúng document_id/span. | Đổi parse/chunk phải có phiên bản; không hứa ID ổn định xuyên phiên bản nếu chưa thiết kế. |
| Nguồn và quote | Đã chốt EvidenceRef(document_id, source_refs, quote); giữ block:N khi đúng kho nguồn. | Offset/spans chi tiết có thể lưu trong registry nội bộ để truy nguồn chính xác. | Không thêm SourceRef object thay chuỗi source_refs; quote phải khớp nguyên văn. |
| Đơn vị offset và Unicode | Đã chốt offset TextChange trên chỉ số ký tự Python [start,end). | Chuyển sang UTF-16 ở lớp frontend nếu giao diện cần. | Không đổi đơn vị của payload TextChange hoặc dùng offset trên chuỗi đã chuẩn hóa khác. |
| Chuẩn hóa và metadata chunk | Nguồn gốc bất biến, chuỗi phụ chuẩn hóa có mapping riêng. | Chỉ chuẩn hóa phần phục vụ tìm kiếm, quote luôn lấy lại từ nguồn gốc. | A linh hoạt nhưng tốn mapping; B đơn giản hơn; chunk phải giữ ID nguồn và phiên bản chuỗi. |
| PDF gốc và DOCX chuyển đổi | Hiển thị nguồn DOCX chuyển đổi, công bố chưa có mapping trang PDF. | Thêm mapping trang/vùng PDF khi converter và đối chiếu thực tế chứng minh được. | Không tự coi số block, page break Word hoặc số trang DOCX là vị trí PDF. |

**Hướng tôi ưu tiên để thử trước:** Nguồn bất biến, block/span và quy ước offset rõ; adapter frontend xử lý khác biệt đơn vị.

**Ràng buộc và phần cần phối hợp:** Thọ + Đức Anh + Tuấn Anh phối hợp, Ngọc Anh review offset. Đây là đề xuất biểu diễn, không thêm tên trường vào API đã chốt khi chưa đồng bộ schema/fixture.

**Bằng chứng cần có trước khi chốt:** Tiếng Việt NFC/NFD, emoji, trùng tên file, nhiều spans, đổi phiên bản parse và DOCX từ PDF; slice trả đúng quote.

**Bên cần thống nhất/review:** Thọ, Đức Anh, Ngọc Anh và Tuấn Anh; Dũng kiểm tra căn cứ.

**Phương án owner đề xuất cho phần còn mở:** [Điền lựa chọn cụ thể, giữ schema đã chốt.]
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Kiểu dữ liệu và ràng buộc nêu ở phần đã chốt áp dụng theo quyết định nhóm. Chỉ phần còn cần quyết định mới tiếp tục nhận đề xuất; không coi thuật toán hoặc tích hợp đã hoàn thành.

**Xác nhận còn cần:** Bên liên quan review phương án/fixture cho phần còn mở; quyết định dùng schema Đức Anh đã được nhóm xác nhận.
**Đầu ra cần cập nhật:** Source schema/registry, fixture tiếng Việt/nguồn trùng tên/offset, hiển thị frontend.
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-05 — Chỉ dẫn sửa đổi và nội dung trước/sau

**Trạng thái:** CHOT_MOT_PHAN
**Chủ trì:** Thọ + Ngọc Anh + Tuấn Anh; Dũng điều phối tích hợp, Đức Anh phối hợp context khi liên quan

**Phần đã chốt theo schema:** Bàn giao AmendmentItem theo contracts.py. operation: AMEND/ADD/REPEAL/UNRESOLVED; applicability: APPLIES/OTHER_DOCUMENT/UNRESOLVED; after_basis: QUOTED/DERIVED/ABSENT/UNRESOLVED; before_text/after_text là str hoặc null; effect_info là list[EffectInfo].

**Phần còn cần quyết định:** Thuật toán trích/liên kết, dựng after, chia nhiều yêu cầu/đích, áp nhiều chỉ dẫn và xử lý hiệu lực có căn cứ.

**Vấn đề cần chốt:** Trường chỉ dẫn, operation, văn bản đích, locator, applicability, before/after, after_basis, hiệu lực/chuyển tiếp, bằng chứng/cảnh báo; một Điều nhiều yêu cầu và một yêu cầu nhiều đích.

**Phương án để cân nhắc:** Bàn giao đúng AmendmentItem đã chốt; phân biệt trích trực tiếp, suy ra, không tồn tại và chưa biết.

**Gợi ý cho phần hiện thực còn mở và nội dung đã chốt theo schema:**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Đơn vị AmendmentItem | Tách các yêu cầu độc lập thành AmendmentItem; target_unit_ids chứa các đích liên quan. | Nhóm chỉ dẫn/đích trong nội bộ rồi xuất cùng AmendmentItem cho boundary. | Cách chia/gộp còn cần review; không thay schema bằng danh sách đích con có cấu trúc mới. |
| operation, locator, applicability | Đã chốt enum operation/applicability và target_locator dạng str. | Dùng locator có cấu trúc trong nội bộ, serialize ra chuỗi của contract. | Giữ instruction nguyên văn từ S; không thay target_locator bằng object trong payload chung. |
| before/after và after_basis | Đã chốt before_text/after_text là str hoặc null và after_basis theo Literal. | Phép dựng/trạng thái nội bộ được kiểm chứng trước khi ánh xạ về cùng trường. | Không thay chuỗi nullable bằng object nội dung; giữ phân biệt không tồn tại và chưa biết. |
| Nhiều chỉ dẫn cùng đích | Tách item, lưu thứ tự có căn cứ và quan hệ phụ thuộc. | Nhóm theo đích, giữ danh sách thao tác và kết quả kiểm tra xung đột. | Cần quy tắc chồng lấn, không tự chọn thứ tự nếu nguồn không đủ rõ. |
| Hiệu lực, cảnh báo và nguồn | Đã chốt effect_info là list[EffectInfo] trong AmendmentItem. | Có thể chia sẻ kết quả trích hiệu lực trong bộ nhớ nội bộ, nhưng serialize đủ EffectInfo cho item. | Không thay list[EffectInfo] bằng danh sách ID; không suy hiệu lực từ ngày ban hành. |

**Hướng tôi ưu tiên để thử trước:** Một thao tác–một đích cho ranh giới bàn giao, liên kết lại chỉ dẫn gốc để giữ quan hệ nhiều yêu cầu.

**Ràng buộc và phần cần phối hợp:** Một chỉ dẫn nhiều đích là quan hệ nghiệp vụ, khác matching 1–n khi đánh giá. Thọ cung cấp, Ngọc Anh/Tuấn Anh/Dũng nhận; LK-04/LK-12 quyết định nguồn và trạng thái.

**Bằng chứng cần có trước khi chốt:** AMEND/ADD/REPEAL, đích mơ hồ, một Điều nhiều yêu cầu, một yêu cầu nhiều đích và nhiều chỉ dẫn chồng lấn; review cách tạo after.

**Bên cần thống nhất/review:** Thọ cung cấp; Ngọc Anh/Tuấn Anh và Dũng nhận; Đức Anh phối hợp context, Dũng review nghiệp vụ.

**Phương án owner đề xuất cho phần còn mở:** [Điền lựa chọn cụ thể, giữ schema đã chốt.]
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Kiểu dữ liệu và ràng buộc nêu ở phần đã chốt áp dụng theo quyết định nhóm. Chỉ phần còn cần quyết định mới tiếp tục nhận đề xuất; không coi thuật toán hoặc tích hợp đã hoàn thành.

**Xác nhận còn cần:** Bên liên quan review phương án/fixture cho phần còn mở; quyết định dùng schema Đức Anh đã được nhóm xác nhận.
**Đầu ra cần cập nhật:** Schema chỉ dẫn, fixture AMEND/ADD/REPEAL/UNRESOLVED và test bàn giao.
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-06 — Context → Text Diff/Semantic Diff

**Trạng thái:** CHOT_MOT_PHAN
**Chủ trì:** Đức Anh + Ngọc Anh + Tuấn Anh

**Phần đã chốt theo schema:** Dùng AnalysisContext(general_context, evidence, references), ReferenceRequirement và EffectInfo đã có. Reference status dùng AVAILABLE/MISSING/UNRESOLVED; evidence là list[EvidenceRef].

**Phần còn cần quyết định:** Cách chọn ngữ cảnh, readiness từng bước, ngân sách truy xuất và yêu cầu bổ sung; không tự thêm trường/enum vào payload chung.

**Vấn đề cần chốt:** Trường context/evidence, tham chiếu AVAILABLE/MISSING/UNRESOLVED; khi nào đủ trước/sau để Text Diff; khi nào Semantic Diff tiếp tục được và giới hạn kết luận; ai yêu cầu bổ sung.

**Phương án để cân nhắc:** Ngữ cảnh tổng quát + nguồn cục bộ/tham chiếu có liên quan; giới hạn theo ngân sách và căn cứ.

**Gợi ý cho phần hiện thực còn mở và nội dung đã chốt theo schema:**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Biểu diễn context/evidence | Đã chốt AnalysisContext với general_context, evidence, references. | Chọn/lọc nguồn bằng phương pháp nội bộ rồi xuất đúng AnalysisContext. | Không thêm trường role/status mới vào EvidenceRef; vai trò được tra từ kho tài liệu. |
| Trạng thái tham chiếu | AVAILABLE/MISSING/UNRESOLVED tách theo tài liệu và đoạn cần đọc. | Trạng thái tài liệu cùng kết quả tìm đoạn riêng, adapter ánh xạ về contract chung. | Có file nhưng chưa tìm ra đoạn là UNRESOLVED; query rỗng không tự là MISSING. |
| Điều kiện Text Diff | Chạy khi before/after xác định, kể cả không tồn tại được biểu diễn rõ cho ADD/REPEAL. | Gửi yêu cầu kiểm tra readiness cho từng item rồi chạy phần đã đủ. | Không đợi context phân tích nghĩa đầy đủ mới diff chữ nếu hai chuỗi đã đủ; không ép chuỗi thiếu thành rỗng. |
| Điều kiện Semantic Diff | Chỉ phân tích nhận định có đủ căn cứ; phần khác trả chưa xác định. | Phân tích giới hạn từng khía cạnh, tách rõ phần xác định và phần chưa đủ căn cứ. | B giữ được nhiều kết quả hơn nhưng cần schema/trình bày không làm người dùng hiểu là toàn bộ đã rõ. |
| Yêu cầu bổ sung và ngân sách | Context builder ghi nhu cầu tham chiếu; Pipeline tổng hợp cho frontend. | Semantic Diff chỉ ra nhu cầu cụ thể rồi context builder đối chiếu bộ tài liệu và trả trạng thái. | Không vòng lặp vô hạn; giữ request đồng bộ, lượt bổ sung có trần, không tự tải tài liệu ngoài. |

**Hướng tôi ưu tiên để thử trước:** Gói nguồn có cấu trúc và trạng thái rõ; cho phép phân tích phần đủ căn cứ, công bố giới hạn phần còn lại.

**Ràng buộc và phần cần phối hợp:** Đức Anh + Ngọc Anh + Tuấn Anh thống nhất readiness/output; Thọ review truy nguồn, Dũng review kết luận nghiệp vụ. Không để LightRAG tự định nghĩa đủ căn cứ.

**Bằng chứng cần có trước khi chốt:** Có file/thiếu file/có file nhưng không tìm đoạn, thay dẫn chiếu A→B, đủ Text Diff nhưng chưa đủ tác động, hết ngân sách retrieval.

**Bên cần thống nhất/review:** Đức Anh, Ngọc Anh, Tuấn Anh; Thọ về truy nguồn, Dũng về nghiệp vụ.

**Phương án owner đề xuất cho phần còn mở:** [Điền lựa chọn cụ thể, giữ schema đã chốt.]
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Kiểu dữ liệu và ràng buộc nêu ở phần đã chốt áp dụng theo quyết định nhóm. Chỉ phần còn cần quyết định mới tiếp tục nhận đề xuất; không coi thuật toán hoặc tích hợp đã hoàn thành.

**Xác nhận còn cần:** Bên liên quan review phương án/fixture cho phần còn mở; quyết định dùng schema Đức Anh đã được nhóm xác nhận.
**Đầu ra cần cập nhật:** Context contract/fixture đủ-thiếu căn cứ, context_builder và module.md.
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-07 — Text Diff → Semantic Diff

**Trạng thái:** CHOT_MOT_PHAN
**Chủ trì:** Ngọc Anh + Tuấn Anh

**Phần đã chốt theo schema:** Dùng TextDiffResult(amendment_id, changes) và TextChange với type INSERT/DELETE/REPLACE, old_text/new_text, old_start/old_end/new_start/new_end. amendment_id phải khớp yêu cầu; spans phải khớp hai chuỗi.

**Phần còn cần quyết định:** Thuật toán diff, chuẩn hóa có mapping, gộp vùng và điều kiện skip; kiểm tra reconstruction/overlap toàn bộ chưa được validator căn cứ thực hiện.

**Vấn đề cần chốt:** Các trường TextChange/TextDiffResult, chuỗi gốc để tính offset, loại thay đổi, phân biệt null/rỗng, trường hợp bỏ qua diff; quan hệ amendment_id và yêu cầu nguồn.

**Phương án để cân nhắc:** INSERT/DELETE/REPLACE với các vùng old/new; bàn giao đúng TextDiffResult/TextChange; phương pháp tạo edit-script nội bộ còn được owner lựa chọn.

**Gợi ý cho phần hiện thực còn mở và nội dung đã chốt theo schema:**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Trường và vùng old/new | Đã chốt các trường TextDiffResult/TextChange và hai vùng old/new. | Thuật toán có thể dùng edit-script/opcode nội bộ rồi chuyển về TextChange. | Không đưa opcode hoặc schema khác thay payload đã chốt. |
| Chuỗi gốc và nguồn | Boundary trả TextChange old_text/new_text và offset trên before_text/after_text của AmendmentItem. | Giữ thêm hash/phiên bản ở registry nội bộ để kiểm tra đúng cặp chuỗi. | Không bỏ old_text/new_text hoặc thay trường bắt buộc bằng ref/hash. |
| Null/rỗng/bỏ qua | Đã chốt text_diff null khi chưa có kết quả; changes là list khi đã tạo TextDiffResult. | Pipeline ghi lý do skip/lỗi qua ProcessingIssue và review fields thích hợp. | Không thêm trạng thái/envelope mới; [] không tự chứng minh không đổi chữ hoặc không đổi nghĩa. |
| Quan hệ amendment_id | Một TextDiffResult cho một item bàn giao, chứa danh sách TextChange. | Kết quả theo cặp before/after, thêm mapping tới các item dùng chung. | A ưu tiên đơn giản; B cần chứng minh không gắn nhầm nguồn/cảnh báo khi tái sử dụng. |

**Hướng tôi ưu tiên để thử trước:** Một kết quả theo item, hai chuỗi chính xác, spans rõ và trạng thái độc lập với danh sách thay đổi.

**Ràng buộc và phần cần phối hợp:** Ngọc Anh + Tuấn Anh chốt; Dũng/frontend review nếu hiển thị. Text Diff không kết luận có/không đổi nghĩa và không tự xóa warnings.

**Bằng chứng cần có trước khi chốt:** Ca không đổi chữ, chỉ đổi dấu câu, ADD/REPEAL, thiếu after, skip và lỗi; kiểm tra reconstruction, nguồn và bên nhận đọc đúng ý nghĩa.

**Bên cần thống nhất/review:** Ngọc Anh, Tuấn Anh; Dũng/API và frontend nếu hiển thị vùng diff.

**Phương án owner đề xuất cho phần còn mở:** [Điền lựa chọn cụ thể, giữ schema đã chốt.]
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Kiểu dữ liệu và ràng buộc nêu ở phần đã chốt áp dụng theo quyết định nhóm. Chỉ phần còn cần quyết định mới tiếp tục nhận đề xuất; không coi thuật toán hoặc tích hợp đã hoàn thành.

**Xác nhận còn cần:** Bên liên quan review phương án/fixture cho phần còn mở; quyết định dùng schema Đức Anh đã được nhóm xác nhận.
**Đầu ra cần cập nhật:** Schema diff, fixture hai chuỗi và offset, test Text Diff → Semantic Diff.
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-08 — Cấu trúc Semantic Change

**Trạng thái:** CHOT_MOT_PHAN
**Chủ trì:** Tuấn Anh + Dũng; Ngọc Anh phối hợp đầu vào Text Diff, Đức Anh phối hợp AI Adapter/schema khi liên quan

**Phần đã chốt theo schema:** Đã áp dụng schema merge qua [PR #2](https://github.com/Lyra1603/group4_legal_document_change_detection/pull/2) trên main (`a8a906a`); Dùng nguyên SemanticChange, ChangeAspect và SemanticDiffResult trong contracts.py: nhận định nullable, diff_details, aspects, evidence, old_quote/new_quote, needs_review/review_reason và các ID liên quan. SemanticDiffResult gắn amendment_id và chứa list[SemanticChange].

**Phần còn cần quyết định:** Quy tắc chia/gộp nhận định, cách tạo/kiểm chứng ngữ nghĩa và ID qua nhiều lần chạy. Không chọn lại số trường hoặc đổi kiểu bàn giao.

**Vấn đề còn cần chốt:** Quy tắc tạo ID, chia/gộp nhận định, kiểm chứng nội dung và xử lý trường hợp chưa tạo được nhận định; tên/kiểu/trường bắt buộc đã theo schema chung.

**Phương án cho phần còn mở:** Giữ các trường SemanticChange/ChangeAspect/SemanticDiffResult đã chốt; đề xuất quy tắc chia/gộp và phương pháp tạo nội dung, không chọn lại số trường.

**Gợi ý cho phần hiện thực còn mở và nội dung đã chốt theo schema:**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Tổ chức trường Semantic Change | Đã chốt SemanticChange và ChangeAspect trong contracts.py. | Có thể tổ chức object nội bộ khác, nhưng adapter phải xuất đúng TypedDict. | Không chọn lại 6/8/10 trường hoặc đổi schema lồng nhau của boundary. |
| ID và số thay đổi mỗi yêu cầu | Một amendment_id có danh sách change_id; mỗi change là một tác động độc lập. | Nhóm các nhận định theo đích/quy định, giữ danh sách ID liên kết và quan hệ chia/gộp. | A dễ triển khai baseline; B cần quy tắc không đếm trùng khi nhiều chỉ dẫn cùng tác động. |
| Đổi nghĩa/chưa rõ/không đổi | Dùng is_meaningful_change true/false/null và review fields đã chốt. | Giữ AmendmentResult với semantic_diff null hoặc SemanticDiffResult có changes theo kết quả thực tế. | Không thêm status cho SemanticChange hoặc AmendmentResult; changes rỗng không đồng nghĩa không đổi hoặc thành công. |
| Trước/sau và bằng chứng | Giữ old_quote/new_quote nullable và evidence: list[EvidenceRef] theo contract. | Registry nội bộ hỗ trợ truy nguồn nhưng không thay các trường quote/evidence bắt buộc. | Nội dung suy ra không được gán thành quote nguyên văn; không bỏ khóa nullable. |
| Khía cạnh nội bộ | Đã chốt aspects: list[ChangeAspect] với field_group, values, diễn giải, evidence và review fields. | Owner chọn cách trích/chia/gộp khía cạnh rồi serialize đúng cấu trúc đó. | Không biến mỗi aspect thành change chỉ để tăng số đếm; dùng tám nhóm theo LK-09. |
| Output lỗi/không nhận định | Giữ AmendmentResult với semantic_diff null nếu chưa có kết quả và lý do trong report. | SemanticDiffResult có changes rỗng khi đã tạo kết quả nhưng không có nhận định, vẫn giữ amendment. | Không thêm envelope riêng hoặc bỏ item lỗi; phân biệt không nhận định với không đổi nghĩa. |

**Hướng tôi ưu tiên để thử trước:** Một nhận định có nhiều aspects và bằng chứng; trạng thái/kết luận rõ, liên kết amendment_id và change_id.

**Ràng buộc và phần cần phối hợp:** Tuấn Anh + Dũng và Đức Anh/schema cùng review. Tên/kiểu bàn giao đã theo contracts.py; phương án nội bộ không tự thay contract chung. Matching đánh giá 1–1 trước, khác số changes của một amendment.

**Bằng chứng cần có trước khi chốt:** JSON hợp lệ/sai, một yêu cầu sinh nhiều tác động, một change nhiều aspects, chỉ đổi diễn đạt và không tạo được nhận định; Pipeline/Scorer dùng được.

**Bên cần thống nhất/review:** Tuấn Anh phụ trách cả Semantic Change và Scorer; Dũng nhận để tổng hợp/API; Ngọc Anh phối hợp đầu vào Text Diff; Đức Anh phối hợp AI Adapter/schema; frontend cùng review cách hiểu.

**Phương án owner đề xuất cho phần còn mở:** [Điền lựa chọn cụ thể, giữ schema đã chốt.]
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Kiểu dữ liệu và ràng buộc nêu ở phần đã chốt áp dụng theo quyết định nhóm. Chỉ phần còn cần quyết định mới tiếp tục nhận đề xuất; không coi thuật toán hoặc tích hợp đã hoàn thành.

**Xác nhận còn cần:** Bên liên quan review phương án/fixture cho phần còn mở; quyết định dùng schema Đức Anh đã được nhóm xác nhận.
**Đầu ra cần cập nhật:** Bảng trường đầy đủ + JSON fixture; schema và mapping sang báo cáo. Giữ các trường theo commit căn cứ; review fixture và phần phương pháp còn mở.
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-09 — Tám nhóm field_group, category và ranh giới nhãn

**Trạng thái:** CHOT_MOT_PHAN
**Chủ trì:** Tuấn Anh + Dũng; Ngọc Anh/Đức Anh phối hợp khi liên quan Text Diff hoặc AI Adapter/schema

**Phần đã chốt theo schema:** Đã áp dụng schema merge qua [PR #2](https://github.com/Lyra1603/group4_legal_document_change_detection/pull/2) trên main (`a8a906a`); Dùng tám mã GROUPS: SUBJECT_OBJECT, RIGHTS_DUTIES_ACTIONS, CONDITIONS_EXCEPTIONS, TIME_QUANTITY, PROCEDURE_AUTHORITY, CONSEQUENCES_SANCTIONS, DEFINITIONS_REFERENCES, SCOPE_EFFECT_TRANSITION. category thuộc GROUPS, WORDING_ONLY hoặc null. Với thay đổi nghĩa, category khác null phải có trong aspects; không đổi nghĩa thì WORDING_ONLY và LOW.

**Phần còn cần quyết định:** Rubric ranh giới và ưu tiên category khi nhiều nhóm hợp lệ, ví dụ nhãn được review. Không lập danh mục bốn nhóm mới; null/needs_review theo validator, không thêm scope_status hoặc enum ngoài phạm vi.

**Vấn đề còn cần chốt:** Ví dụ ranh giới tám nhóm, ưu tiên category khi nhiều aspects và trách nhiệm phân loại; giữ nguyên các trường/enum và quy tắc nullable của schema chung.

**Phương án cho phần còn mở:** Review rubric/ví dụ trên tám mã đã chọn; không đặt danh mục hoặc mã đầu ra mới.

**Gợi ý cho phần hiện thực còn mở và nội dung đã chốt theo schema:**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Tám nhóm theo nghiệp vụ | Đã chốt tám field_group của GROUPS, không còn hai danh mục bốn nhóm ứng viên. | Reviewer tạo ví dụ đối chứng để kiểm tra ranh giới trên tám nhóm hiện có. | Không chọn lại tên/mã hoặc tự gộp nhóm. |
| Tên/mã/định nghĩa | Giữ nguyên tám mã và ý nghĩa theo SRS/validator. | Có thể đề xuất nhãn hiển thị dễ hiểu nhưng phải ánh xạ đúng mã hiện có. | Không thay enum kỹ thuật; ví dụ/rubric vẫn cần review. |
| Một/nhiều nhãn | Đã chốt một category nullable cho mỗi ScoringResult, giữ nhiều aspects trong change. | Scorer có thể cân nhắc nhiều nhóm nội bộ rồi chọn một category hợp lệ có reason. | Không đổi category thành list hoặc xuất nhiều mã chính thức cho một score. |
| Nơi phân loại | Semantic Diff tạo aspects, Scorer ánh xạ category theo bảng được review. | Semantic Diff đề xuất nhóm, Scorer kiểm tra và chấm tác động. | Cần một nơi sở hữu kết quả cuối; không để hai bước sửa nhãn qua lại mà không có lý do. |
| Ngoài phạm vi/chưa rõ | Không có scope_status trong hợp đồng; giữ category/field_group null và review flags theo validator khi chưa xác định. | Diễn giải giới hạn qua reason/review_reason và bằng chứng đã có, không tạo enum mới. | OTHER_DOCUMENT vẫn là applicability; không đồng nhất với lỗi retrieval hoặc thêm nhóm OTHER. |

**Hướng tôi ưu tiên để thử trước:** Dùng bộ ví dụ nghiệp vụ để kiểm tra ranh giới/ưu tiên trong tám nhóm đã chốt; không chọn lại danh mục.

**Ràng buộc và phần cần phối hợp:** Tuấn Anh + Dũng chủ trì; Ngọc Anh/Đức Anh/frontend review phần bị ảnh hưởng. Danh mục tám nhóm đã chốt; rubric và ví dụ ranh giới vẫn cần review trước đánh giá.

**Bằng chứng cần có trước khi chốt:** Các cặp thời hạn–định lượng, chủ thể–nghĩa vụ, điều kiện–thủ tục, hiệu lực/chuyển tiếp, nhiều khía cạnh và ngoài phạm vi; có người review nhãn và phiên bản.

**Bên cần thống nhất/review:** Tuấn Anh, Ngọc Anh, Đức Anh, Dũng; frontend dùng nhãn cùng review.

**Phương án owner đề xuất cho phần còn mở:** [Điền lựa chọn cụ thể, giữ schema đã chốt.]
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Kiểu dữ liệu và ràng buộc nêu ở phần đã chốt áp dụng theo quyết định nhóm. Chỉ phần còn cần quyết định mới tiếp tục nhận đề xuất; không coi thuật toán hoặc tích hợp đã hoàn thành.

**Xác nhận còn cần:** Bên liên quan review phương án/fixture cho phần còn mở; quyết định dùng schema Đức Anh đã được nhóm xác nhận.
**Đầu ra cần cập nhật:** Fixture tám nhóm/category, ví dụ ranh giới, bộ lọc frontend và nhãn chuẩn; không yêu cầu bảng ánh xạ bốn nhóm.
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-10 — Semantic Diff → Classifier & Scorer

**Trạng thái:** CHOT_MOT_PHAN
**Chủ trì:** Tuấn Anh (Semantic Change và Scorer); Dũng review phần tích hợp

**Phần đã chốt theo schema:** Đã áp dụng schema merge qua [PR #2](https://github.com/Lyra1603/group4_legal_document_change_detection/pull/2) trên main (`a8a906a`); Dùng ScoringResult với change_id, category, significance, is_critical, reason, needs_review, review_reason. Khi scoring khác null, có một score cho mỗi SemanticChange. significance là LOW/MEDIUM/HIGH/CRITICAL hoặc null; null cần is_critical null và review; mức xác định phải nhất quán với cờ critical. Kết luận đổi nghĩa null không được chấm mức xác định.

**Phần còn cần quyết định:** Rubric, phương pháp chấm, reason và cách phối hợp đọc dữ liệu trong nội bộ Tuấn Anh; không sửa cấu trúc scoring hoặc bằng chứng nguồn.

**Vấn đề cần chốt:** Những trường Scorer đọc; trường được/không được thay; category, significance, critical, reason; ID liên kết; truyền cảnh báo; ca ngữ nghĩa đã rõ nhưng mức tác động chưa đủ căn cứ.

**Phương án để cân nhắc:** Khi scoring khác null, dùng đúng một ScoringResult/mỗi SemanticChange; cách áp rubric và tạo reason còn cần đề xuất.

**Gợi ý cho phần hiện thực còn mở và nội dung đã chốt theo schema:**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Trường Scorer được đọc | Nhận Semantic Change đã validate, gồm nội dung/aspects/bằng chứng/trạng thái. | Nhận yêu cầu scoring chỉ chứa các trường cần thiết và ID liên kết về change. | A ít mapping; B ranh giới gọn nhưng không được cắt mất ngoại lệ hoặc căn cứ cần chấm. |
| Số score và ID liên kết | Một score cho mỗi Semantic Change, tham chiếu change_id. | Chi tiết điểm theo aspect trong nội bộ rồi tổng hợp một score cho change. | B cần quy tắc tổng hợp được review; không tự thay thành nhiều score API cho một change. |
| Trường được sửa | Scorer tạo list[ScoringResult] tách khỏi SemanticChange theo contract. | Hàm nội bộ có thể tổ chức chung nhưng boundary vẫn giữ semantic_diff và scoring riêng. | Không sửa quote/before/after hoặc kết luận ngữ nghĩa để khớp mức chấm. |
| Critical và reason | Đã chốt is_critical nhất quán significance; null theo ràng buộc review. | Owner chọn rule/LLM tạo reason rồi validator kiểm tra cấu trúc/quan hệ. | Validator không chứng minh reason được nguồn hỗ trợ; lỗi phải xử lý theo Pipeline, không tự đổi dữ liệu. |
| Ngữ nghĩa rõ nhưng tác động chưa rõ | Giữ nhận định nghĩa, mức tác động/critical chưa xác định và lý do. | Chấm phần change đủ căn cứ, ghi riêng kết quả chưa chấm cho phần khác. | Không ép mức thấp; warnings từ bước trước phải tiếp tục tới báo cáo. |

**Hướng tôi ưu tiên để thử trước:** Một score/change, kết quả list[ScoringResult] đặt riêng trong AmendmentResult.scoring; Semantic Change và bằng chứng không bị sửa.

**Ràng buộc và phần cần phối hợp:** Tuấn Anh kiểm tra điểm nối nội bộ, Dũng review tích hợp/rubric. Quan hệ nhiều aspects trong scoring không thay phạm vi matching đánh giá 1–1.

**Bằng chứng cần có trước khi chốt:** Score thiếu/trùng change_id, reason không hỗ trợ mức, critical mâu thuẫn, nhiều aspects và trường hợp chỉ xác định được đổi nghĩa.

**Bên cần thống nhất/review:** Tuấn Anh chốt điểm nối nội bộ giữa Semantic Change và Scorer; Dũng nhận kết quả tích hợp/API và review rubric/nhãn; Ngọc Anh phối hợp Text Diff khi ảnh hưởng đầu vào.

**Phương án owner đề xuất cho phần còn mở:** [Điền lựa chọn cụ thể, giữ schema đã chốt.]
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Kiểu dữ liệu và ràng buộc nêu ở phần đã chốt áp dụng theo quyết định nhóm. Chỉ phần còn cần quyết định mới tiếp tục nhận đề xuất; không coi thuật toán hoặc tích hợp đã hoàn thành.

**Xác nhận còn cần:** Bên liên quan review phương án/fixture cho phần còn mở; quyết định dùng schema Đức Anh đã được nhóm xác nhận.
**Đầu ra cần cập nhật:** Contract scoring, fixture ranh giới và test một/một-nhiều; không dùng điểm retrieval thay severity.
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-11 — Báo cáo Pipeline → API/frontend

**Trạng thái:** CHOT_MOT_PHAN
**Chủ trì:** Dũng + owner phân tích + Tuấn Anh/frontend

**Phần đã chốt theo schema:** Đã áp dụng schema merge qua [PR #2](https://github.com/Lyra1603/group4_legal_document_change_detection/pull/2) trên main (`a8a906a`); Dùng ComparisonReport và AmendmentResult hiện có: định danh qua base_document/amendment_document/reference_documents; kết quả nằm trong results, có amendment/text_diff/semantic_diff/scoring. Không yêu cầu chuyển sang documents/items hoặc ReviewItem; frontend ghép scoring theo change_id trong cùng result.

**Phần còn cần quyết định:** Endpoint/upload/alias, cách đọc nguồn sau cleanup và nhận xét frontend. Chọn schema không tự đổi POST /api/compare hoặc doc_v1/doc_s/reference_files trên main; kiểu/khóa nhận xét chưa chốt và không nằm trong báo cáo AI.

**Vấn đề còn cần chốt:** Cách tổng hợp results và bảo toàn chỉ dẫn, nguồn sau cleanup, endpoint/upload/alias và nhận xét frontend; envelope và các trường đã theo schema Đức Anh.

**Phương án cho phần còn mở:** Pipeline và frontend sử dụng ComparisonReport.results/AmendmentResult đã chốt; chỉ đề xuất cách ghép dữ liệu, validation và cơ chế truy nguồn trong phạm vi hiện tại.

**Gợi ý cho phần hiện thực còn mở và nội dung đã chốt theo schema:**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Chuyển code cũ sang báo cáo mục tiêu | Đã chốt ComparisonReport theo schema Đức Anh. | Adapter chỉ chuyển output module khác biểu diễn về đúng AmendmentResult. | Không yêu cầu documents/items hoặc ReviewItem; việc nối validator vẫn phải hiện thực. |
| Upload và alias | Giữ doc_v1/doc_s/reference_files theo API main hiện tại. | Đề xuất base_file/amendment_file hoặc alias chỉ sau review và test tương thích. | Chưa chốt đổi tên; backend/main.py hiện không triển khai các alias đó. |
| Envelope và tổng hợp item | Mỗi result giữ amendment, text_diff, semantic_diff, scoring đúng contract. | Pipeline đối soát chỉ dẫn với results và từng kết quả để phát hiện bỏ sót. | Không mất result chưa phân tích hoặc warnings; không thêm trường item_id. |
| Nguồn sau cleanup | Frontend giữ file đầu vào trong phiên; EvidenceRef của báo cáo trỏ đúng nguồn. | Chuẩn bị dữ liệu nguồn riêng ở lớp frontend theo giao diện cần review; không thêm vào ComparisonReport mặc định. | Không thêm kho lịch sử/backend URL đã hết hạn; cơ chế đọc nguồn sau cleanup vẫn cần LK-11. |
| Định danh và trạng thái | Dùng document_id/role, amendment_id và change_id trong result; report status riêng. | Kiểm tra đối soát ID/role trước serialize theo validator chung. | Không thêm item_id hoặc đồng nhất HTTP status, report status và review người dùng. |

**Hướng tôi ưu tiên để thử trước:** Pipeline xuất đúng ComparisonReport/AmendmentResult và đối soát bao phủ các chỉ dẫn; không chuyển sang hợp đồng phẳng khác.

**Ràng buộc và phần cần phối hợp:** Dũng và Tuấn Anh/frontend cùng thử fixture; Đức Anh phối hợp schema. Không tự thêm endpoint lưu file, job, database hoặc contract HCI chỉ vì dùng tài liệu HCI làm mẫu.

**Bằng chứng cần có trước khi chốt:** Upload mục tiêu/alias nếu hỗ trợ, report đủ/một phần/lỗi, item chưa phân tích, nguồn còn đọc được sau cleanup và frontend hiển thị đúng.

**Bên cần thống nhất/review:** Dũng, Tuấn Anh, Ngọc Anh, Thọ khi liên quan nguồn; Đức Anh phối hợp schema/AI Adapter khi cần.

**Phương án owner đề xuất cho phần còn mở:** [Điền lựa chọn cụ thể, giữ schema đã chốt.]
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Kiểu dữ liệu và ràng buộc nêu ở phần đã chốt áp dụng theo quyết định nhóm. Chỉ phần còn cần quyết định mới tiếp tục nhận đề xuất; không coi thuật toán hoặc tích hợp đã hoàn thành.

**Xác nhận còn cần:** Bên liên quan review phương án/fixture cho phần còn mở; quyết định dùng schema Đức Anh đã được nhóm xác nhận.
**Đầu ra cần cập nhật:** Schema/fixture báo cáo và upload, API contract, mapping implementation cũ; module.md api/Pipeline.
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-12 — Null, rỗng, cảnh báo, lỗi và trạng thái

**Trạng thái:** CHOT_MOT_PHAN
**Chủ trì:** Các owner điểm nối; Dũng điều phối tích hợp/API

**Phần đã chốt theo schema:** Dùng kiểu nullable, Literal, ProcessingIssue và SUCCESS/PARTIAL/FAILED theo code căn cứ. needs_review nhất quán review_reason; warning aspect truyền lên change/semantic/scoring. SUCCESS không có errors, đích UNRESOLVED hoặc bước phân tích null ở item APPLIES.

**Phần còn cần quyết định:** Chính sách tiếp tục/dừng theo lỗi, completeness và lý do PARTIAL/FAILED, điều kiện kết luận không có thay đổi; validator không tự kiểm tra nguồn nếu không gọi validate_sources/validate_amendment.

**Vấn đề cần chốt:** Trường nào nullable; ý nghĩa []/chuỗi rỗng; mã/lý do lỗi, cảnh báo được truyền tới đâu; SUCCESS/PARTIAL/FAILED; lỗi mô hình/retrieval/timeout; điều kiện được kết luận không có thay đổi.

**Phương án để cân nhắc:** Phân biệt không có, chưa biết, chưa chạy và thất bại; report status tách mã HTTP, needs_review và trạng thái người dùng.

**Gợi ý cho phần hiện thực còn mở và nội dung đã chốt theo schema:**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Nullable và dữ liệu không tồn tại | Đã chốt khóa nullable theo contracts.py; mọi khóa TypedDict vẫn bắt buộc. | Giải thích không tồn tại/chưa biết qua các trường basis/review và ProcessingIssue hiện có. | Không đổi nullable thành union/envelope mới hoặc tự dùng empty string thay thiếu dữ liệu. |
| Danh sách rỗng | [] chỉ khi bước đã chạy thành công và không có kết quả thuộc loại đó. | Danh sách kết quả luôn đi cùng trạng thái bước và thông tin bao phủ. | B làm rõ ca chưa chạy/lỗi; không suy không có thay đổi từ một danh sách rỗng đơn lẻ. |
| Cảnh báo và lỗi | Đã chốt ProcessingIssue(stage, code, message, amendment_id). | Owner thống nhất mã/lý do và cách truyền lỗi trong chính các trường đã có. | Không thêm refs hoặc envelope lỗi mới vào contract; không lộ nội dung hoặc nuốt lỗi upstream. |
| SUCCESS/PARTIAL/FAILED | Quy tắc theo khả năng tạo kết quả dùng được và phần chưa xử lý. | Ma trận trạng thái theo từng bước rồi Pipeline tổng hợp có đối soát. | Không quy định PARTIAL chỉ vì bất kỳ warning nào; cần bảng ví dụ xác định kết quả còn dùng được. |
| Lỗi mô hình/retrieval/timeout | Dừng phần phụ thuộc, giữ nguồn và cảnh báo, tiếp tục phần độc lập hợp lệ. | Dừng toàn comparison nếu lỗi làm mất tính đúng của mọi kết quả. | Cả hai áp theo loại lỗi; lỗi retrieval không chứng minh tài liệu thiếu. |
| Kết luận không có thay đổi | Chỉ khi phạm vi cần xét đã xử lý đủ và không có thay đổi được xác định. | Nếu còn unresolved/lỗi, báo không có thay đổi trong phần đã xác định cùng giới hạn. | B không được trình bày như kết luận phủ định toàn bộ; needs_review và review người dùng là trạng thái riêng. |

**Hướng tôi ưu tiên để thử trước:** Ma trận trạng thái theo bước/item cùng lý do có cấu trúc; tổng hợp SUCCESS/PARTIAL/FAILED dựa trên kết quả thực sự dùng được.

**Ràng buộc và phần cần phối hợp:** Các owner giao/nhận cùng chốt, Dũng điều phối tích hợp/API. Không tự đặt thêm enum chính thức hoặc thay nghĩa null của SRS khi chưa đồng bộ schema/fixture.

**Bằng chứng cần có trước khi chốt:** Bảng từng trường null/[]/rỗng, upstream chưa chạy/lỗi, hết deadline, query rỗng, một phần đủ căn cứ và ca xác định không đổi.

**Bên cần thống nhất/review:** Bên cung cấp/nhận, API, frontend; Dũng review các kết luận nghiệp vụ.

**Phương án owner đề xuất cho phần còn mở:** [Điền lựa chọn cụ thể, giữ schema đã chốt.]
**Lý do và đánh đổi:** [Điền lý do, giới hạn và ví dụ kiểm chứng.]

**Kết luận hiện có:** Kiểu dữ liệu và ràng buộc nêu ở phần đã chốt áp dụng theo quyết định nhóm. Chỉ phần còn cần quyết định mới tiếp tục nhận đề xuất; không coi thuật toán hoặc tích hợp đã hoàn thành.

**Xác nhận còn cần:** Bên liên quan review phương án/fixture cho phần còn mở; quyết định dùng schema Đức Anh đã được nhóm xác nhận.
**Đầu ra cần cập nhật:** Bảng hành vi lỗi/null và fixture từng trường hợp; validator và hiển thị.
**Quyết định thay thế/liên quan bổ sung:** [Điền nếu có.]

### LK-13 — LightRAG HTTP và vòng đời dữ liệu

**Trạng thái:** CHO_CAC_QUYET_DINH_KHAC_HOAN_THANH
**Chủ trì:** Dũng + Đức Anh; phối hợp owner nguồn/context/ngữ nghĩa và các bên nhận dữ liệu

**Vấn đề cần chốt:** API nhập/sẵn sàng/query/xóa thực tế; chunk/server có chia lại không, metadata được giữ thế nào; index dùng theo comparison; ID mapping; lỗi/retry/idempotency, timeout và cleanup khi client mất kết nối; không xóa vùng dùng chung để dọn một comparison.

**Phương án để cân nhắc:** LightRAG Server riêng qua HTTP đã chốt; còn lựa chọn release, endpoint/payload, cấu hình và cách ly.

**Gợi ý cụ thể cho từng nội dung cần chốt (chưa phải lựa chọn của owner):**

| Nội dung | Phương án A | Phương án B | Phương án C / điều kiện phân biệt |
| --- | --- | --- | --- |
| Release và API HTTP | Cố định release, xác minh nhập/trạng thái/query/xóa rồi wrapper hóa. | Lớp adapter theo capability để kiểm tra tính năng có trên release đang chạy. | B chỉ khi cần nhiều môi trường thật; không ghi endpoint/payload phỏng đoán thành API chính thức [S1]. |
| Chunk phía client/server | Gửi đoạn nguồn có định danh và kiểm chứng server xử lý lại thế nào. | Gửi văn bản tài liệu rồi ánh xạ các chunk trả về vào registry nguồn. | A cũng có thể bị server chia lại; cả hai cần thử metadata có được giữ và quote có đối chiếu được. |
| Index theo comparison | Một môi trường/storage tách riêng cho comparison, nếu cách triển khai hỗ trợ và đã thử. | Server dùng chung nhưng có cơ chế scope cách ly thực sự được release hỗ trợ và kiểm chứng. | Không coi thêm comparison_id vào payload hoặc chỉ lọc kết quả cuối là đủ cách ly; metadata lọc sau không ngăn truy xuất lẫn. |
| Sẵn sàng và theo dõi nhập | Theo dõi trạng thái nhập tới hoàn tất trong deadline request. | Theo dõi trạng thái cùng retrieval kiểm tra một nguồn đã biết trước khi phân tích. | Không đổi sang hệ thống job người dùng; việc index nội bộ có trạng thái không đồng nghĩa dự án đã có queue API. |
| Mapping và idempotency | Lưu registry ID client ↔ tài liệu/chunk dịch vụ cho một comparison. | Kết hợp registry với khóa thao tác có phiên bản và tra trạng thái trước khi thử lại. | Không retry upload mù khi chưa biết lần trước đã tạo gì; cần xác minh API thực tế cho phép kiểm tra nào. |
| Cleanup và mất kết nối | Cleanup trong khối kết thúc, chỉ xóa tài nguyên đã ghi nhận thuộc comparison. | Kết hợp cleanup tức thời với danh sách tài nguyên cần dọn lại khi có lỗi/crash. | Không xóa storage/graph dùng chung; phải xử lý ngắt kết nối và process chết, không chỉ đường thành công. |
| Timeout và retry | Deadline riêng nhập/query/xóa, retry hữu hạn theo loại lỗi an toàn. | Deadline tổng và ngân sách từng thao tác, ghi phần cleanup còn chưa hoàn tất. | Các giá trị chờ đo; không báo đã xóa khi mới gửi yêu cầu mà chưa xác nhận. |

**Hướng tôi ưu tiên để thử trước:** Khảo sát wrapper hẹp, registry nguồn và môi trường thử tách biệt; chỉ chọn cơ chế scope sau khi chứng minh được cách ly/xóa trên release thực tế.

**Ràng buộc và phần cần phối hợp:** HTTP và Dũng + Đức Anh đã chốt; toàn bộ phương án chi tiết tại đây chỉ để chuẩn bị, chốt sau các quyết định khác theo thứ tự LK-13. Không mặc định LightRAG có workspace động hoặc xóa theo comparison trên mọi release.

**Bằng chứng cần có trước khi chốt:** Hai comparison đồng thời có nội dung phân biệt, nhập lặp, query trước index, lỗi mạng giữa nhập, cleanup sau lỗi/ngắt kết nối; kiểm tra không lẫn và không xóa nhầm nguồn của lượt khác.

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
