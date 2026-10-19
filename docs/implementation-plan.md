# KẾ HOẠCH TRIỂN KHAI DỰ ÁN

**Dự án:** Legal Document Change Detection  
**Phiên bản kế hoạch:** 1.4.0  
**Thời gian thực hiện:** Cuối tuần 5 đến hết tuần 13  
**Người điều phối:** Dương Đức Anh  
**Tài liệu liên quan:** [BRD](brd.md), [SRS 1.3.0](srs.md), [Architecture 1.3.0](architecture.md), [Hướng dẫn dữ liệu và gán nhãn 1.2.0](data-annotation-guide.md), [Evaluation Plan](test-evaluation-plan.md)  
**Ngày cập nhật:** 14/10/2026

## 1. Công việc chính của từng thành viên

- **Bạch Công Dũng:** phụ trách dữ liệu, nghiệp vụ và tài liệu tổng quát; chuẩn bị các mẫu V1–S, tài liệu tham chiếu và hướng dẫn gán nhãn. Đề xuất chủ trì phần chuẩn bị ngữ cảnh và xác định căn cứ cần bổ sung, phối hợp Thọ và Ngọc Anh để hiện thực.
- **Dương Đức Anh:** điều phối nhóm, phụ trách Backend, schema, Pipeline và tích hợp. Bảo đảm các module trao đổi đúng dữ liệu, trả báo cáo nhất quán và có môi trường chạy chung.
- **Bùi Quang Thọ:** phụ trách đọc và phân tích cấu trúc tài liệu, trích yêu cầu sửa đổi và liên kết với nội dung V1. Giữ vị trí nguồn, phân biệt văn bản đích và trích thông tin hiệu lực/chuyển tiếp.
- **Đoàn Ngọc Anh:** phụ trách Text Diff, Semantic Diff và Classifier & Scorer. Phân tích phần thay đổi với ngữ cảnh, tạo các khía cạnh có bằng chứng và đánh giá mức tác động theo tiêu chí chung.
- **Đỗ Tuấn Anh:** phụ trách giao diện, Evaluator và điều phối kiểm thử/nhãn chuẩn. Hiển thị kết quả, nhu cầu tài liệu bổ sung và tổ chức đánh giá chất lượng trên dữ liệu đã review.

Phân công là cơ sở triển khai; chủ trì phần ngữ cảnh cần được xác nhận trước khi nhận task tương ứng. Nếu đổi người phụ trách, cập nhật người sở hữu và mốc bàn giao tại đây, đồng thời đồng bộ Architecture.

## 2. Mục tiêu, phạm vi và mốc bàn giao

Ứng dụng phân tích văn bản ban đầu V1 và văn bản sửa đổi S, nhận diện nội dung bị tác động, giải thích thay đổi với ngữ cảnh và bằng chứng, kèm thông tin hiệu lực/chuyển tiếp được nêu trong nguồn. Người dùng cung cấp tài liệu tham chiếu khi cần; thiếu căn cứ thì giữ phần đã xác định và thể hiện giới hạn.

DOCX là định dạng chính, hỗ trợ PDF có lớp chữ; không OCR, không bắt buộc dựng V2 đầy đủ hoặc xây kho pháp luật. Request đồng bộ, hỗ trợ gửi lại bộ file khi người dùng chủ động bổ sung tài liệu. Phạm vi và tiêu chí chi tiết theo BRD/SRS; luồng module và hợp đồng trao đổi theo Architecture/SRS.

| Giai đoạn | Kết quả cần đạt |
| --- | --- |
| Cuối tuần 5 / bàn giao đầu tuần 6 | Tài liệu thống nhất, chủ task rõ, mẫu đầu vào–đầu ra đủ để bắt đầu |
| Tuần 6–8 | Xây module, tích hợp baseline V1–S, bổ sung ngữ cảnh/dẫn chiếu và ổn định luồng |
| Tuần 9–10 | Kiểm thử toàn hệ thống, cải thiện trên tập phát triển, chốt phiên bản ứng viên |
| Tuần 11–12 | Đánh giá độc lập, nghiệm thu nội bộ, đóng gói và diễn tập |
| Tuần 13 | Trình bày, nộp và bàn giao |

Các mốc là kế hoạch, không xác nhận công việc đã hoàn thành. Thiếu đầu ra tiền đề phải được ghi rõ cùng người xử lý và ảnh hưởng tiến độ.

## 3. Quyền quyết định khi triển khai

| Loại quyết định | Người quyết định / phối hợp | Nơi ghi nhận |
| --- | --- | --- |
| Thuật toán, thư viện nội bộ không đổi hợp đồng | Chủ module tự chọn, tự kiểm tra; thông báo yêu cầu môi trường cho Đức Anh | PR, dependency và hướng dẫn module |
| Công nghệ frontend và thành phần hiển thị nội bộ | Tuấn Anh chủ trì; chỉ phối hợp Đức Anh khi ảnh hưởng API hoặc đóng gói | Hướng dẫn frontend, dependency |
| Backend, môi trường chung và đóng gói | Đức Anh chủ trì; tham khảo người có module cần dependency hoặc tài nguyên đặc biệt | Architecture và development-guide |
| Định dạng/trường dữ liệu đi qua module | Người cung cấp và người nhận cùng thử trên fixture; Đức Anh duyệt thay đổi schema chung | SRS, schema, fixture và API contract nếu liên quan |
| Cách hiểu chỉ dẫn, bằng chứng, ranh giới nhãn | Dũng, chủ module liên quan và Tuấn Anh thống nhất trên ví dụ; giữ bất đồng chưa giải quyết | Data annotation guide, hồ sơ review |
| Mô hình/API ngoài, chi phí và việc gửi nội dung ra ngoài | Chủ module đề xuất; Đức Anh điều phối quyết định với các thành viên bị ảnh hưởng | Architecture, cấu hình và hướng dẫn chạy |
| Phạm vi chức năng, mốc bàn giao hoặc đổi người sở hữu | Đức Anh điều phối với người bị ảnh hưởng | BRD/SRS nếu đổi phạm vi; kế hoạch và issue |

Các thư viện/framework/mô hình từng đề xuất là phương án để thử, không phải ràng buộc bắt buộc. Chủ module có thể thay phương pháp khi có bằng chứng phù hợp hơn. Đổi nội bộ không cần họp cả nhóm; đổi đầu vào–đầu ra phải thống nhất với bên nhận trước khi tích hợp.

Giới hạn dung lượng, số file tham chiếu, độ dài và thời gian xử lý được chốt sau đo trên mẫu đại diện. Giá trị vận hành được quản lý trong cấu hình/API contract; kế hoạch chỉ theo dõi người chốt và mốc hoàn thành.

## 4. Trách nhiệm, phối hợp và bàn giao

### 4.1. Người sở hữu đầu ra

| Hạng mục | Chủ trì | Đầu ra | Người review chính |
| --- | --- | --- | --- |
| Dữ liệu, manifest và guideline | Dũng | Mẫu V1–S, bộ tham chiếu, nguồn/hash, hướng dẫn gán nhãn | Tuấn Anh; Thọ kiểm tra khả năng đọc |
| Reader và Parser | Thọ | Nội dung có cấu trúc, thứ tự và vị trí nguồn | Dũng đối chiếu file; Đức Anh kiểm tra contract |
| Trích yêu cầu, liên kết và hiệu lực | Thọ | AmendmentItem có chỉ dẫn, vị trí đích, EffectInfo và cảnh báo | Dũng review nghiệp vụ; Ngọc Anh thử đầu vào |
| Chuẩn bị ngữ cảnh và dẫn chiếu | Dũng — đề xuất | Phần lấy ngữ cảnh và kiểm tra căn cứ, AnalysisContext/ReferenceRequirement theo SRS | Thọ kiểm tra truy nguồn; Ngọc Anh kiểm tra khả năng sử dụng |
| Text Diff, Semantic Diff và Scorer | Ngọc Anh | Nội dung thay đổi, aspects, diễn giải và mức độ | Tuấn Anh đối chiếu nhãn; Dũng review căn cứ |
| Schema, API và Pipeline | Đức Anh | Luồng tích hợp, báo cáo đầy đủ, xử lý lỗi/file tạm | Tuấn Anh kiểm tra API/UI; chủ module kiểm tra dữ liệu |
| Frontend | Tuấn Anh | Chọn V1/S/tham chiếu, xem báo cáo và bổ sung tài liệu | Đức Anh kiểm tra tích hợp |
| Nhãn chuẩn, Evaluator và kiểm thử | Tuấn Anh điều phối | Bộ nhãn được review, chương trình đo và báo cáo kiểm thử | Dũng review dữ liệu; Ngọc Anh kiểm tra ca đo |

Mỗi issue có một người chịu trách nhiệm cuối cùng và một reviewer cụ thể. Cả nhóm tham gia gán nhãn; người review nhãn phải khác người tạo nhãn. Các task lấy mẫu, đọc cấu trúc, xây thuật toán và thiết kế UI có thể làm độc lập bằng fixture sau khi thống nhất ranh giới liên quan.

### 4.2. Những điểm phải phối hợp

| Điểm bàn giao | Thành viên cần làm việc cùng nhau | Cần quyết định gì | Kết quả cần có và thời điểm |
| --- | --- | --- | --- |
| Nguồn và khả năng đọc | Dũng + Thọ | Mẫu nào đại diện, lỗi nào do nguồn/chuyển đổi, cách giữ bảng và vị trí; file nào dùng làm ca lỗi | Bộ file mẫu kèm ghi chú và kết quả đọc, đầu tuần 6 |
| Chỉ dẫn và vị trí đích | Dũng + Thọ | Các dạng sửa toàn đơn vị, cụm từ, bổ sung/bãi bỏ; phân biệt Điều của S và V1; S sửa văn bản khác; trường hợp không đủ rõ | Ví dụ chỉ dẫn–đích đã review, tuần 6; cập nhật khi gặp dạng mới |
| Đầu vào cho phân tích ngữ nghĩa | Thọ + Ngọc Anh; Dũng tham gia ở ca nghiệp vụ khó | Phần trước/sau cục bộ được trích hoặc suy ra thế nào; trường thông tin nào đã có, còn thiếu; bằng chứng và cảnh báo đi kèm; tránh yêu cầu Thọ phân tích nghĩa thay Ngọc Anh | Một fixture được Ngọc Anh dùng chạy thử và xác nhận, trước tích hợp tuần 7 |
| Ngữ cảnh và tài liệu dẫn chiếu | Dũng + Thọ + Ngọc Anh | Thọ cung cấp cách truy xuất Điều/đoạn/bảng; Ngọc Anh xác định loại ngữ cảnh cần đọc; Dũng chốt căn cứ đủ/thiếu trên mẫu. Thống nhất ai hiện thực từng phần, cách ghi AVAILABLE/MISSING/UNRESOLVED và giới hạn khi còn phụ thuộc | Người sở hữu task cụ thể và fixture đủ/thiếu dẫn chiếu, tuần 6; tích hợp tuần 7–8 |
| Hiệu lực và chuyển tiếp | Thọ + Dũng + Ngọc Anh | Phạm vi áp dụng của ngày chung/ngoại lệ; khi nào chỉ là EffectInfo, khi nào đủ căn cứ thành khía cạnh thay đổi; không suy hiệu lực từ ngày ban hành | Mẫu ngày chung, mốc riêng và chưa rõ, tuần 6–7 |
| Schema và tích hợp Pipeline | Đức Anh + Thọ + Ngọc Anh + Dũng ở phần ngữ cảnh | Các trường được tạo ở bước nào; định danh và nguồn; giá trị null/rỗng; lỗi/cảnh báo; bước nào tiếp tục được khi thiếu dữ liệu | Schema và báo cáo mẫu chạy qua các module, tuần 6; kiểm tra lại tại mỗi lần đổi contract |
| API và giao diện | Đức Anh + Tuấn Anh | Tên file field, JSON response, lỗi HTTP, báo cáo PARTIAL; gửi lại cả bộ file khi bổ sung; hiển thị vai trò tài liệu, trạng thái chờ và chống gửi lặp | API contract và mock report cho UI, tuần 6; thử file thật tuần 7 |
| Nội dung hiển thị phân tích | Ngọc Anh + Tuấn Anh; Thọ khi có vấn đề truy nguồn | Cách hiển thị aspects, diễn giải, mức độ, nội dung suy ra và quote; lấy nhãn vị trí từ nguồn nào; không làm phẳng mất khía cạnh | Một báo cáo có nhiều khía cạnh và cảnh báo được hiển thị đúng, tuần 7 |
| Nhãn và phép đo | Tuấn Anh + Dũng + Ngọc Anh | Ranh giới change/aspect, ví dụ severity, matching, ca chưa xác định; nhãn mong đợi khi thiếu tham chiếu; phân biệt lỗi mô hình với lỗi nguồn | Guideline/nhãn pilot và ca tính tay Evaluator, tuần 6–7; cố định trước đánh giá độc lập |
| Tài nguyên và chạy demo | Đức Anh + chủ module có tác vụ nặng; Tuấn Anh ở thời gian chờ UI | Dependency, mô hình/API, tài nguyên, timeout và điều kiện sẵn sàng; giới hạn đo được và cách báo lỗi | Cấu hình và kết quả đo, tuần 8; chốt tuần 10 |

Chỉ mời người cung cấp đầu vào, người nhận đầu ra và người có trách nhiệm quyết định liên quan. Không yêu cầu cả nhóm cùng viết một module hoặc cùng dự mọi trao đổi.

### 4.3. Cách chốt và thay đổi quyết định

1. Người phát hiện vướng mắc đưa một file/fixture cụ thể, chỉ rõ đầu ra hiện có và điều cần quyết định.
2. Các bên liên quan thử trên cùng mẫu, chọn phương án đủ cho bước tiếp theo; nếu chưa giải quyết, giữ cảnh báo và giới hạn thay vì điền giá trị giả.
3. Ghi quyết định ngắn trong issue/PR: người chốt, phương án, ví dụ kiểm tra, người sửa và tài liệu/schema chịu ảnh hưởng.
4. Nếu đổi contract, Đức Anh phối hợp cập nhật schema/fixture; người cung cấp và người nhận sửa cùng nhánh tích hợp hoặc các PR có thứ tự rõ. Nếu đổi cách hiểu nhãn, Dũng/Tuấn Anh rà lại mẫu bị ảnh hưởng.

Tài liệu là cơ sở làm việc có phiên bản. Phương pháp và hợp đồng có thể điều chỉnh trong phát triển khi có bằng chứng; thay đổi phải được truyền tới đúng bên phụ thuộc, không để code và tài liệu dùng hai quy ước khác nhau.

## 5. Tài liệu cần có khi bắt đầu triển khai

| Tài liệu | Người điều phối | Đủ để bắt đầu khi |
| --- | --- | --- |
| BRD, SRS, Architecture | Dũng + Đức Anh; chủ module review phần liên quan | Phạm vi V1–S thống nhất, có mẫu đầu vào–đầu ra và chủ trách nhiệm |
| Implementation Plan | Đức Anh cùng các chủ task | Có việc tuần đầu, đầu ra, phụ thuộc và reviewer |
| API contract | Đức Anh + Tuấn Anh | Có upload V1/S/tham chiếu, response mẫu, lỗi và báo cáo PARTIAL |
| Development guide | Đức Anh; từng chủ module bổ sung lệnh của mình | Thành viên khác cài, chạy và kiểm tra lại được |
| Workflow | Đức Anh | Có cách nhận task, branch, PR, review và tích hợp |
| Data annotation guide | Dũng; Tuấn Anh + Ngọc Anh review nhãn | Có mẫu V1–S, bằng chứng, dẫn chiếu, hiệu lực và quy trình review |
| Test evaluation plan | Tuấn Anh; Dũng + Ngọc Anh phối hợp | Có ca pilot, phương án chia tập, matching và cách kiểm tra kết luận thiếu căn cứ |
| README | Đức Anh + Dũng | Giới thiệu đúng phạm vi và chỉ đến tài liệu chi tiết |

Hoàn thiện pilot trong tuần 6 rồi cập nhật quy tắc bị ảnh hưởng. Một quyết định công nghệ nội bộ chưa chốt không cản module khác dùng fixture; thiếu hợp đồng bàn giao thì cần xử lý trước khi tích hợp task phụ thuộc.

## 6. Tiến độ triển khai tuần 6–13

### Tuần 6 — Chốt điểm bàn giao và dựng khung

**Mục tiêu:** mỗi người có đầu vào–đầu ra mẫu, chạy được phần việc và biết điểm cần phối hợp.

- Đức Anh hiện thực schema theo SRS 1.3.0, API và Pipeline bằng mock; cùng Tuấn Anh chốt upload/report mẫu.
- Thọ triển khai Reader/Parser trên file thật; cùng Dũng lập fixture chỉ dẫn–vị trí đích, ngữ cảnh và hiệu lực.
- Ngọc Anh làm Text Diff và baseline ngữ nghĩa/chấm điểm trên AmendmentItem mẫu; cùng Thọ kiểm tra dữ liệu trước/sau và bằng chứng cần nhận.
- Dũng tuyển chọn V1–S, manifest và tham chiếu; chủ trì xác định căn cứ đủ/thiếu và nhận task phần ngữ cảnh sau khi xác nhận phân công. Cùng Thọ/Ngọc Anh chốt ranh giới lấy nguồn và sử dụng ngữ cảnh.
- Tuấn Anh dựng UI và Evaluator với dữ liệu mẫu; cùng Dũng/Ngọc Anh tổ chức pilot nhãn và ca tính tay.

**Đầu ra:** môi trường chạy được, mock report hiển thị, Reader/Parser có kết quả file thật, fixture dùng chung, người sở hữu phần ngữ cảnh đã được xác nhận.

**Tiêu chí kết thúc:** từng người dùng được fixture của bên giao; quyết định còn thiếu có người xử lý và hạn chốt. Mock được ghi rõ trong môi trường phát triển.

### Tuần 7 — Tích hợp baseline V1–S

**Mục tiêu:** xử lý một cặp thật từ tải file đến báo cáo.

- Thọ hoàn thiện trích yêu cầu, liên kết V1 và hiệu lực cho các dạng đã thống nhất; giữ phần chưa xác định.
- Dũng phối hợp Thọ hiện thực chuẩn bị ngữ cảnh và truy xuất tài liệu tham chiếu; cùng Ngọc Anh kiểm tra căn cứ đã đủ cho phân tích hay cần giới hạn kết luận.
- Ngọc Anh nối Text Diff/Semantic Diff/Scorer với AmendmentItem thật, giữ aspects và bằng chứng; đối chiếu lỗi với Thọ ở đúng ranh giới bàn giao.
- Đức Anh tích hợp module thật, giữ định danh tài liệu, AmendmentResult và cảnh báo; báo PARTIAL phù hợp.
- Tuấn Anh nối UI, thử đủ/thiếu tài liệu, bổ sung rồi gửi lại bộ file; kiểm tra Evaluator trên nhãn đã review.

**Đầu ra:** luồng chính không dùng mock nghiệp vụ, kết quả baseline trên tập phát triển và danh sách ca chưa hỗ trợ.

**Tiêu chí kết thúc:** có cả ca thành công và ca thiếu căn cứ; không biến lỗi hoặc Text Diff rỗng thành không có thay đổi.

### Tuần 8 — Cải thiện ngữ cảnh, ngữ nghĩa và độ ổn định

**Mục tiêu:** sửa lỗi gây mất/sai thay đổi, đo phương pháp và tài nguyên.

- Ngọc Anh so sánh phương pháp ngữ nghĩa với baseline trên cùng tập phát triển; ghi lỗi từng nhóm và thiếu/sai khía cạnh.
- Thọ sửa lỗi đọc, cấu trúc, vị trí đích và hiệu lực; Dũng sửa phần chọn ngữ cảnh/căn cứ và bổ sung dữ liệu đại diện.
- Đức Anh đo thời gian từng bước, quản lý file tạm, giới hạn và deadline với chủ module liên quan.
- Tuấn Anh hoàn thiện hiển thị bằng chứng, nội dung suy ra, yêu cầu tham chiếu và PARTIAL; điều phối kiểm thử tích hợp.
- Dũng + Tuấn Anh rà chất lượng nhãn, chia tập theo nguồn/chuỗi sửa đổi; Ngọc Anh kiểm tra matching và ca tính tay. Giữ tập test độc lập với hiệu chỉnh thuật toán.

**Đầu ra:** báo cáo thử nghiệm trên tập phát triển, bộ regression, cấu hình đo được và phiên bản tích hợp ổn định.

**Tiêu chí kết thúc:** có bằng chứng cho lựa chọn phương pháp; không còn lỗi chặn luồng demo; biết giới hạn từng nhóm tình huống.

### Tuần 9 — Kiểm thử toàn hệ thống và trải nghiệm sử dụng

**Mục tiêu:** kiểm tra đầy đủ luồng nghiệp vụ, lỗi và khả năng sử dụng trước khi chốt thuật toán.

- Tuấn Anh điều phối kiểm thử đầu-cuối theo SRS; ghi lỗi kèm file đầu vào, commit, expected/actual và bằng chứng.
- Đức Anh kiểm tra API/Pipeline, giới hạn, deadline, dọn file và chạy đồng thời; sửa lỗi tích hợp.
- Thọ kiểm thử bố cục, bảng, ranh giới Điều, chỉ dẫn sửa đổi và các ca liên kết vị trí đích khó; bổ sung regression test.
- Ngọc Anh phân tích lỗi ngữ nghĩa/chấm điểm trên dev set, ưu tiên bỏ sót thay đổi quan trọng.
- Dũng kiểm tra nguồn, manifest, ngữ cảnh và trạng thái đủ/thiếu tham chiếu; Tuấn Anh điều phối thử nghiệm nhận diện V1/S/tham chiếu, giải thích thay đổi bằng lời của người tham gia, tìm bằng chứng/vị trí nguồn và hiểu cảnh báo. Ghi độ đúng, thời gian, lỗi diễn giải và phản hồi; nêu rõ nếu thành viên nhóm đóng vai người dùng.

**Đầu ra:** báo cáo kiểm thử tích hợp, danh sách lỗi có mức ưu tiên và người xử lý; các cải tiến UI được kiểm tra lại.

**Tiêu chí kết thúc:** các yêu cầu chính đều có ca kiểm thử và kết quả; lỗi chặn luồng có phương án xử lý trước mốc chốt tuần 10. Tập test độc lập tiếp tục được giữ riêng.

### Tuần 10 — Hoàn thiện chất lượng và chốt phiên bản ứng viên

**Mục tiêu:** hoàn tất cải thiện trên dev set và chuẩn bị một phiên bản ổn định cho đánh giá độc lập.

- Chủ module sửa lỗi ưu tiên từ tuần 9 và chạy lại regression; không mở rộng phạm vi chức năng.
- Ngọc Anh hoàn thiện quy tắc/ngưỡng trên dev set, ghi so sánh phương pháp với baseline trên cùng dữ liệu.
- Đức Anh đo lại thời gian/tài nguyên, chốt cấu hình vận hành và đóng gói phiên bản ứng viên.
- Tuấn Anh kiểm tra Evaluator bằng ca tính tay có nhiều khía cạnh, thiếu/sai khía cạnh; cùng Dũng kiểm tra split, phiên bản nhãn và quy tắc đối chiếu đã cố định.
- Cả nhóm review acceptance criteria, cập nhật hướng dẫn chạy và xác nhận các giới hạn cần công bố.

**Đầu ra:** phiên bản ứng viên gắn commit/tag, cấu hình và dependency cố định; bộ test độc lập có phiên bản; báo cáo thử nghiệm dev.

**Tiêu chí kết thúc:** không còn lỗi chặn đánh giá; dữ liệu, cách tính metric và lệnh chạy được cố định trước khi chạy đánh giá độc lập tuần 11.

### Tuần 11 — Đánh giá độc lập và nghiệm thu nội bộ

**Mục tiêu:** có kết quả chất lượng tái lập được cho phiên bản ứng viên.

- Tuấn Anh chạy đánh giá trên test set; báo số mẫu, TP/FP/FN cấp SemanticChange, F1, Critical Change Recall, trường hợp chưa xác định và lỗi khía cạnh theo nhóm; tổng hợp đánh giá giải thích/khả năng hiểu báo cáo theo Evaluation Plan.
- Cả nhóm kiểm tra acceptance criteria, trường hợp lỗi và chạy lại trên máy khác.
- Dũng tổng hợp minh chứng dữ liệu; Đức Anh tổng hợp phiên bản, giới hạn và báo cáo kỹ thuật.
- Chủ module phân tích lỗi; phân biệt lỗi cần sửa để bàn giao với hạn chế thuật toán cần công bố.
- Nhóm đối chiếu mục tiêu chất lượng với số đo thực tế và ghi rõ tiêu chí đạt/chưa đạt.

**Đầu ra:** `evaluation-report.md`, biên bản nghiệm thu nội bộ, danh sách lỗi và giới hạn đã biết.

**Tiêu chí kết thúc:** số liệu gắn với phiên bản cụ thể. Nếu dùng lỗi trên test để chỉnh thuật toán, công bố việc đó; chỉ tuyên bố đánh giá độc lập mới trên dữ liệu chưa dùng để chỉnh.

### Tuần 12 — Đóng gói, hoàn thiện báo cáo và diễn tập

**Mục tiêu:** chuẩn bị đầy đủ bản nộp và kiểm chứng khả năng trình diễn.

- Đức Anh đóng gói bản dự kiến nộp; thành viên khác chạy từ môi trường sạch theo hướng dẫn.
- Tuấn Anh cùng nhóm chuẩn bị kịch bản demo chính và dự phòng, dữ liệu mẫu và tài nguyên/mô hình chuẩn bị sẵn nếu sử dụng.
- Dũng rà soát nguồn và quyền phân phối dữ liệu; chủ module hoàn thiện mô tả phương pháp và giới hạn.
- Cả nhóm hoàn thiện README, báo cáo cuối kỳ, slide, phân công trình bày và diễn tập hỏi đáp.
- Chỉ sửa lỗi cần thiết; mọi thay đổi có regression test phù hợp. Nếu thay đổi ảnh hưởng kết quả, chạy lại đánh giá và ghi rõ quan hệ với kết quả tuần 11.

**Đầu ra:** gói sản phẩm dự kiến nộp, báo cáo/slide, hướng dẫn demo và checklist bàn giao.

**Tiêu chí kết thúc:** máy demo chạy được toàn luồng; số liệu trong báo cáo/slide khớp phiên bản được trích dẫn; mọi khác biệt với bản nộp đều được giải thích.

### Tuần 13 — Nộp sản phẩm và bàn giao

**Mục tiêu:** hoàn thành bàn giao chính thức và trình bày kết quả dự án.

- Đức Anh điều phối rà soát checklist, chốt commit/tag bản nộp và kiểm tra đầy đủ liên kết/tệp.
- Cả nhóm thực hiện demo và trình bày theo phân công; chuẩn bị giải thích phương pháp, kết quả và giới hạn.
- Bàn giao mã nguồn, dependency/cấu hình, hướng dẫn chạy, dữ liệu mẫu được phép phân phối, kết quả đánh giá, báo cáo và slide.
- Chỉ xử lý lỗi chặn bàn giao; nếu sửa, ghi phiên bản và kiểm tra lại phần bị ảnh hưởng trước khi nộp.
- Lưu bản nộp, ghi nhận phản hồi và các hướng phát triển tiếp theo.

**Đầu ra:** bộ sản phẩm cuối kỳ đầy đủ và bản ghi bàn giao.

**Tiêu chí kết thúc:** sản phẩm được nộp đúng yêu cầu; người nhận có thể chạy theo hướng dẫn; mã nguồn, tài liệu, minh chứng và kết quả đánh giá truy được về đúng phiên bản.

## 7. Danh mục công việc và phụ thuộc

Task có thể bắt đầu bằng fixture trước khi module cung cấp dữ liệu hoàn thành; phụ thuộc dưới đây là điều kiện tích hợp bằng dữ liệu thật.

| Mã | Công việc | Chủ trì | Phụ thuộc và phối hợp để tích hợp | Mốc |
| --- | --- | --- | --- | --- |
| PL-01 | Tài liệu và điểm bàn giao | Đức Anh + Dũng | Chủ module review phạm vi liên quan | Đầu tuần 6 |
| PL-02 | Schema và fixture | Đức Anh | Thọ/Ngọc Anh/Dũng cung cấp ví dụ, Tuấn Anh thử report | Tuần 6 |
| PL-03 | Reader và Parser | Thọ | Dũng bàn giao file và vị trí nguồn kiểm chứng | Tuần 6 |
| PL-04 | Trích yêu cầu, liên kết và hiệu lực | Thọ | PL-03; Dũng review chỉ dẫn/đích, Ngọc Anh thử đầu vào | Tuần 6–7 |
| PL-05 | Text Diff | Ngọc Anh | PL-02; PL-04 khi tích hợp | Tuần 6–7 |
| PL-06 | Semantic Diff và Scorer | Ngọc Anh | PL-04, PL-05, PL-17; nhãn pilot từ Dũng/Tuấn Anh | Tuần 6–8 |
| PL-07 | API/Pipeline | Đức Anh | PL-02; PL-03 đến PL-06, PL-17 khi nối thật | Tuần 6–7 |
| PL-08 | UI và bổ sung tài liệu | Tuấn Anh | API contract với Đức Anh; PL-07 khi nối thật | Tuần 6–8 |
| PL-09 | Dữ liệu, manifest và nhãn | Dũng quản lý dữ liệu; Tuấn Anh điều phối review nhãn | Cả nhóm gán nhãn, Ngọc Anh review ranh giới phân tích | Tuần 6–8 |
| PL-10 | Evaluator | Tuấn Anh | Nhãn pilot, matching và ca tính tay với Dũng/Ngọc Anh | Tuần 6–7 |
| PL-11 | Cải thiện phương pháp/hiệu năng | Chủ module; Đức Anh điều phối | Luồng tích hợp, dữ liệu phát triển và Evaluator | Tuần 8–10 |
| PL-12 | Kiểm thử toàn hệ thống | Tuấn Anh điều phối | PL-07, PL-08; chủ module sửa lỗi của mình | Tuần 9–10 |
| PL-13 | Phiên bản ứng viên | Đức Anh | PL-11, PL-12; cả nhóm review | Cuối tuần 10 |
| PL-14 | Đánh giá độc lập | Tuấn Anh | PL-13, tập test và cách tính cố định | Tuần 11 |
| PL-15 | Đóng gói, báo cáo, diễn tập | Đức Anh điều phối | PL-14; cả nhóm bàn giao phần phụ trách | Tuần 12 |
| PL-16 | Nộp và bàn giao | Đức Anh điều phối | PL-15 | Tuần 13 |
| PL-17 | Ngữ cảnh và kiểm tra dẫn chiếu | Dũng — đề xuất, xác nhận tuần 6 | PL-03, PL-04; Thọ cung cấp truy nguồn, Ngọc Anh thử đủ/thiếu căn cứ | Tuần 6–8 |

Mã giữ ổn định để dùng trong issue; PL-17 là phần ngữ cảnh có liên kết với PL-04 và PL-06, không phải bước chờ sau PL-16.

## 8. Dữ liệu, kiểm thử và đánh giá

Dũng bàn giao bộ V1–S với nguồn, hash, tham chiếu và giới hạn theo data-annotation-guide. Tuấn Anh điều phối review nhãn, chia tập và khóa test theo Evaluation Plan; Ngọc Anh phối hợp xác nhận ca matching và mức độ. Cả nhóm tham gia review độc lập, không lấy kết quả thuật toán làm đáp án chuẩn.

Trước tuần 7 cần có mẫu sửa toàn đơn vị, sửa cụm từ, bổ sung/bãi bỏ, nhiều thay đổi trong một Điều, S sửa nhiều văn bản, vị trí đích mơ hồ và dẫn chiếu đủ/thiếu. Trước tuần 9 bổ sung hiệu lực có ngoại lệ, bảng/đoạn ngoài Điều làm căn cứ, file lỗi/quá giới hạn, null/rỗng, lỗi module, PARTIAL và gửi lại sau bổ sung tài liệu.

Mục tiêu chất lượng theo SRS: Change F1 ≥ 0,90 và Critical Change Recall ≥ 0,95; đây là mục tiêu cần kiểm chứng. Tuấn Anh tổ chức đo cùng kiểm tra liên kết đích, hiệu lực, dẫn chiếu, chất lượng giải thích và khả năng hiểu báo cáo theo Evaluation Plan. Không sao chép công thức hoặc quy tắc gán nhãn vào kế hoạch này.

Kết quả phải gắn với commit, cấu hình, dependency/mô hình nếu có, dữ liệu và nhãn có phiên bản. Số liệu từ mẫu thiếu căn cứ hoặc dữ liệu giả định được giải thích đúng mục đích; không dùng thông tin ngoài bộ đầu vào để yêu cầu kết luận chắc chắn. Không chỉnh test sau khi xem kết quả để tuyên bố đạt.

## 9. Quy trình làm việc và bàn giao

1. Issue ghi phạm vi, người sở hữu, reviewer, đầu ra, tiêu chí hoàn thành, phụ thuộc và quyết định cần phối hợp.
2. Chủ module phát triển trên branch riêng, dùng fixture thống nhất. Chỉ yêu cầu phối hợp khi chạm điểm bàn giao hoặc gặp tình huống ảnh hưởng bên khác.
3. PR nêu thay đổi, cách kiểm tra, bằng chứng và giới hạn; nếu đổi contract ghi các bên nhận bị ảnh hưởng và thứ tự tích hợp.
4. Reviewer kiểm tra phần liên quan; người nhận đầu ra chạy thử fixture hoặc mẫu thật trước khi đóng task tích hợp.
5. Merge sau khi review và kiểm tra bắt buộc đạt; kiểm tra lại luồng bị ảnh hưởng sau merge.

Module hoàn thành khi có mã nguồn, ví dụ đầu vào–đầu ra, kiểm tra phù hợp, hướng dẫn chạy và giới hạn; bên nhận sử dụng được đầu ra. Tính năng đầu-cuối hoàn thành khi thao tác người dùng trả đúng kết quả hoặc lỗi theo hợp đồng.

Bàn giao cuối gồm mã nguồn, cấu hình/dependency, hướng dẫn chạy, dữ liệu mẫu được phép phân phối, kết quả đánh giá, báo cáo và slide. Tuấn Anh điều phối báo cáo kiểm thử/đánh giá; Dũng tổng hợp minh chứng dữ liệu/nghiệp vụ; Thọ và Ngọc Anh bàn giao phương pháp/giới hạn module; Đức Anh kiểm tra gói chạy và phiên bản chung.

## 10. Cập nhật kế hoạch và quyết định

| Thay đổi | Người cần tham gia | Cập nhật chính |
| --- | --- | --- |
| Thuật toán/thư viện nội bộ | Chủ module; Đức Anh nếu ảnh hưởng môi trường | Dependency, hướng dẫn module và kết quả thử nghiệm |
| Hợp đồng dữ liệu | Bên cung cấp + bên nhận; Đức Anh điều phối | SRS, schema, fixture, API contract khi liên quan |
| Quy tắc nhãn/căn cứ | Dũng + Tuấn Anh + chủ module liên quan | Data annotation guide, nhãn bị ảnh hưởng và hồ sơ review |
| Phân công | Đức Anh + người giao/nhận task | Mục 1, 4, 7 và Architecture nếu thay vai trò module |
| Tiến độ | Đức Anh + chủ task và bên phụ thuộc | Mục 2, 6, 7; nêu ảnh hưởng và phương án |
| Giới hạn vận hành | Đức Anh + chủ module; Tuấn Anh ở phía UI | Cấu hình, API contract, hướng dẫn chạy và ca giới hạn |
| Phạm vi/kiến trúc | Đức Anh + Dũng + các chủ module bị ảnh hưởng | BRD/SRS/Architecture trước, rồi task và kế hoạch |
| Phép đo | Tuấn Anh + Dũng + Ngọc Anh | Evaluation Plan và phiên bản kết quả |

Giữ lịch sử qua commit/PR, tăng phiên bản khi kế hoạch thay đổi. Không cần viết lại toàn bộ tài liệu vì một lựa chọn nội bộ; chỉ cập nhật phần sở hữu quyết định và các phần phụ thuộc thực sự bị ảnh hưởng.
