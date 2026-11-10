# KẾ HOẠCH TRIỂN KHAI DỰ ÁN

**Dự án:** Legal Document Change Detection
**Phiên bản kế hoạch:** 1.4.0
**Thời gian thực hiện:** Cuối tuần 5 đến hết tuần 13
**Người điều phối tích hợp/API và tài liệu:** Bạch Công Dũng
**Tài liệu liên quan:** [BRD](brd.md), [SRS](srs.md), [Architecture](architecture.md), [Hướng dẫn dữ liệu và gán nhãn](data-annotation-guide.md), [Workflow](workflow.md), [Module](module.md), [Workflow](workflow.md)

## 1. Công việc chính của từng thành viên

- **Bạch Công Dũng:** phụ trách dữ liệu, nghiệp vụ và tài liệu tổng quát; chuẩn bị các mẫu V1–S, tài liệu tham chiếu và hướng dẫn gán nhãn. Phụ trách tích hợp/Pipeline/API; cùng Đức Anh phụ trách AI Adapter; review nghiệp vụ/căn cứ và fixture. Cùng Đức Anh phụ trách gọi/tích hợp LightRAG; context do Đức Anh phụ trách.
- **Dương Đức Anh:** phụ trách schema và context; cùng Dũng phụ trách AI Adapter/gọi mô hình và gọi/tích hợp LightRAG; điều phối kế hoạch đánh giá. Phối hợp kỹ thuật và môi trường chung.
- **Bùi Quang Thọ:** phụ trách đọc và phân tích cấu trúc tài liệu, trích yêu cầu sửa đổi và liên kết với nội dung V1. Giữ vị trí nguồn, phân biệt văn bản đích và trích thông tin hiệu lực/chuyển tiếp.
- **Đoàn Ngọc Anh:** phụ trách Text Diff; bàn giao dữ liệu cho Tuấn Anh và Dũng theo hợp đồng/fixture đã review, kiểm thử chéo với bên nhận.
- **Đỗ Tuấn Anh:** phụ trách Semantic Diff/Semantic Change và Classifier & Scorer; giữ frontend/session theo phân công hiện có. Semantic Change → Scorer là điểm nối nội bộ, Dũng review khi nhận kết quả để tích hợp; không giao lại Evaluator riêng.

Phân công chức năng theo LK-01 đã chốt: Dũng tích hợp/API; Thọ xử lý tài liệu; Ngọc Anh Text Diff; Tuấn Anh Semantic Change/Scorer; Dũng + Đức Anh AI Adapter. Đức Anh phụ trách context và điều phối kế hoạch đánh giá; Dũng + Đức Anh gọi/tích hợp LightRAG, chi tiết LK-13 chốt khi các quyết định khác hoàn thành. Không tự gán một owner chung cho toàn folder change_analysis. Nếu đổi người phụ trách, cập nhật người sở hữu và mốc bàn giao tại đây, đồng thời đồng bộ Architecture.

## 2. Mục tiêu, phạm vi và mốc bàn giao

Sau adapter, Context chuẩn bị chunk, registry và nhập chỉ mục song song nhánh Linker xác định đích/trước-sau → Text Diff. Điểm ghép chờ index sẵn sàng và TextDiffResult, kết hợp chỉ dẫn, trước/sau và vùng chữ đổi để tạo query. LightRAG truy xuất qua HTTP, registry kiểm tra nguồn/quote rồi mới chuyển sang Semantic. Semantic dùng rule trước, model khi cần; Scorer và Pipeline nhận kết quả cùng bằng chứng/cảnh báo để tổng hợp report.

Nhận xét là chức năng dự kiến sau khi các chức năng cốt lõi hoàn thiện, chỉ liệt kê trong phạm vi mở rộng, không là module chính hoặc điều kiện nghiệm thu bản đầu. Hai loại: (1) nhận xét sau phiên được lưu để phục vụ phát triển; (2) nhận xét trong phiên kết hợp nhận xét có sẵn để xem xét và cập nhật kết luận. Khi triển khai, giữ phân biệt kết luận ban đầu/cập nhật và căn cứ thay đổi; không tự coi nhận xét là gold/nhãn huấn luyện. Cách lưu, API, định danh, nguồn nhận xét có sẵn và cơ chế kết hợp chưa chốt; chưa mở rộng schema chung.

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
| Công nghệ frontend và thành phần hiển thị nội bộ | Tuấn Anh chủ trì; phối hợp Dũng khi ảnh hưởng API/đóng gói và Đức Anh khi liên quan schema/AI Adapter | Hướng dẫn frontend, dependency |
| Backend/API, môi trường chung và đóng gói | Dũng chủ trì; Đức Anh phối hợp kỹ thuật; tham khảo người có module cần dependency hoặc tài nguyên đặc biệt | Architecture và development-guide |
| Định dạng/trường dữ liệu đi qua module | Người cung cấp và người nhận cùng thử trên fixture; Đức Anh duyệt thay đổi schema chung | SRS, schema, fixture và API contract nếu liên quan |
| Cách hiểu chỉ dẫn, bằng chứng, ranh giới nhãn | Dũng, chủ module liên quan và Tuấn Anh thống nhất trên ví dụ; giữ bất đồng chưa giải quyết | Data annotation guide, hồ sơ review |
| Mô hình/API ngoài, chi phí và việc gửi nội dung ra ngoài | Chủ module đề xuất; Đức Anh điều phối quyết định với các thành viên bị ảnh hưởng | Architecture, cấu hình và hướng dẫn chạy |
| Phạm vi chức năng, mốc bàn giao hoặc đổi người sở hữu | Dũng điều phối với người bị ảnh hưởng | BRD/SRS nếu đổi phạm vi; kế hoạch và issue |

LightRAG Server riêng qua HTTP là phương án tích hợp đã chốt. Release/API/model/storage và giới hạn là chi tiết cần kiểm chứng trong phương án này. Các thư viện/framework/mô hình nội bộ khác từng đề xuất là phương án để thử, không phải ràng buộc bắt buộc. Chủ module có thể thay phương pháp khi có bằng chứng phù hợp hơn. Đổi nội bộ không cần họp cả nhóm; đổi đầu vào–đầu ra phải thống nhất với bên nhận trước khi tích hợp.

Giới hạn dung lượng, số file tham chiếu, độ dài và thời gian xử lý được chốt sau đo trên mẫu đại diện. Giá trị vận hành được quản lý trong cấu hình/API contract; kế hoạch chỉ theo dõi người chốt và mốc hoàn thành.

## 4. Trách nhiệm, phối hợp và bàn giao

### 4.1. Người sở hữu đầu ra

Owner từng module tự xử lý và báo lỗi thuộc phần mình; chuyển bằng chứng có nguồn cùng lỗi/cảnh báo và phạm vi bị ảnh hưởng cho module nhận đầu ra theo contract chung. Bên nhận kiểm tra dữ liệu, không bỏ cảnh báo hoặc biến thiếu căn cứ thành không có thay đổi. Pipeline tổng hợp trạng thái báo cáo, không thay owner xử lý lỗi nội bộ.

| Hạng mục | Chủ trì | Đầu ra | Người review chính |
| --- | --- | --- | --- |
| Dữ liệu, manifest và guideline | Dũng | Mẫu V1–S, bộ tham chiếu, nguồn/hash, hướng dẫn gán nhãn | Tuấn Anh; Thọ kiểm tra khả năng đọc |
| Reader và Parser | Thọ | Nội dung có cấu trúc, thứ tự và vị trí nguồn | Dũng đối chiếu file; Đức Anh kiểm tra contract |
| Trích yêu cầu, liên kết và hiệu lực | Thọ | AmendmentItem có chỉ dẫn, vị trí đích, EffectInfo và cảnh báo | Dũng review nghiệp vụ; Ngọc Anh thử đầu vào |
| Chuẩn bị ngữ cảnh và dẫn chiếu | Đức Anh (context); Dũng + Đức Anh (gọi/tích hợp LightRAG) | Phần lấy ngữ cảnh và kiểm tra căn cứ, AnalysisContext/ReferenceRequirement theo SRS | Thọ kiểm tra truy nguồn; Tuấn Anh/Ngọc Anh kiểm tra đầu vào sử dụng |
| Text Diff | Ngọc Anh | Khác biệt chữ và vị trí cục bộ | Tuấn Anh/Dũng kiểm tra đầu vào sử dụng |
| Semantic Change và Scorer | Tuấn Anh | Nhận định, bằng chứng, giải thích và mức tác động | Ngọc Anh phối hợp Text Diff; Dũng review khi tích hợp |
| AI Adapter | Dũng + Đức Anh | Gọi mô hình, kiểm tra output/lỗi theo CN-08 | Tuấn Anh kiểm tra dữ liệu nhận |
| Schema; API và Pipeline | Đức Anh (schema); Dũng (API/Pipeline) | Luồng tích hợp, báo cáo đầy đủ, xử lý lỗi/file tạm | Tuấn Anh kiểm tra API/UI; chủ module kiểm tra dữ liệu |
| Frontend | Tuấn Anh | Chọn V1/S/tham chiếu, xem báo cáo và bổ sung tài liệu | Dũng kiểm tra API/tích hợp |
| Nhãn chuẩn và kiểm thử chéo | Dũng quản lý dữ liệu; hai owner từng điểm nối kiểm tra | Fixture/nhãn được review, contract test, integration test | Dũng điều phối tích hợp; Đức Anh điều phối kế hoạch đánh giá; thành viên khác kiểm tra phụ |

Mỗi issue có một người chịu trách nhiệm cuối cùng và một reviewer cụ thể. Cả nhóm tham gia gán nhãn; người review nhãn phải khác người tạo nhãn. Các task lấy mẫu, đọc cấu trúc, xây thuật toán và thiết kế UI có thể làm độc lập bằng fixture sau khi thống nhất ranh giới liên quan.

### 4.2. Những điểm phải phối hợp

| Điểm bàn giao | Thành viên cần làm việc cùng nhau | Cần quyết định gì | Kết quả cần có và thời điểm |
| --- | --- | --- | --- |
| Nguồn và khả năng đọc | Dũng + Thọ | Mẫu nào đại diện, lỗi nào do nguồn/chuyển đổi, cách giữ bảng và vị trí; file nào dùng làm ca lỗi | Bộ file mẫu kèm ghi chú và kết quả đọc, đầu tuần 6 |
| Chỉ dẫn và vị trí đích | Dũng + Thọ | Các dạng sửa toàn đơn vị, cụm từ, bổ sung/bãi bỏ; phân biệt Điều của S và V1; S sửa văn bản khác; trường hợp không đủ rõ | Ví dụ chỉ dẫn–đích đã review, tuần 6; cập nhật khi gặp dạng mới |
| Đầu vào cho Text Diff và Semantic Diff | Thọ + Ngọc Anh + Tuấn Anh; Đức Anh ở context, Dũng ở ca nghiệp vụ khó | Phần trước/sau cục bộ được trích hoặc suy ra thế nào; trường thông tin nào đã có, còn thiếu; bằng chứng và cảnh báo đi kèm; tránh yêu cầu Thọ phân tích nghĩa thay Tuấn Anh | Fixture được Ngọc Anh/Tuấn Anh dùng chạy thử và xác nhận, trước tích hợp tuần 7 |
| Ngữ cảnh và tài liệu dẫn chiếu | Đức Anh + Thọ + Tuấn Anh + Ngọc Anh; Dũng review | Thọ cung cấp truy xuất nguồn; Tuấn Anh xác định ngữ cảnh cho phân tích nghĩa, Ngọc Anh thử Text Diff, Tuấn Anh kiểm tra Scorer; Đức Anh hiện thực chuẩn bị context, Dũng + Đức Anh gọi/tích hợp LightRAG, Dũng review căn cứ đủ/thiếu. Thống nhất cách ghi AVAILABLE/MISSING/UNRESOLVED và giới hạn khi còn phụ thuộc | Người sở hữu task cụ thể và fixture đủ/thiếu dẫn chiếu, tuần 6; tích hợp tuần 7–8 |
| Hiệu lực và chuyển tiếp | Thọ + Dũng + Tuấn Anh + Ngọc Anh | Phạm vi áp dụng của ngày chung/ngoại lệ; khi nào chỉ là EffectInfo, khi nào đủ căn cứ thành khía cạnh thay đổi; không suy hiệu lực từ ngày ban hành | Mẫu ngày chung, mốc riêng và chưa rõ, tuần 6–7 |
| Schema và tích hợp Pipeline | Đức Anh + Thọ + Ngọc Anh + Tuấn Anh; Dũng review nghiệp vụ | Các trường được tạo ở bước nào; định danh và nguồn; giá trị null/rỗng; lỗi/cảnh báo; bước nào tiếp tục được khi thiếu dữ liệu | Schema và báo cáo mẫu chạy qua các module, tuần 6; kiểm tra lại tại mỗi lần đổi contract |
| API và giao diện | Dũng + Tuấn Anh | Tên file field, JSON response, lỗi HTTP, báo cáo PARTIAL; gửi lại cả bộ file khi bổ sung; hiển thị vai trò tài liệu, trạng thái chờ và chống gửi lặp | API contract và mock report cho UI, tuần 6; thử file thật tuần 7 |
| Nội dung hiển thị phân tích | Ngọc Anh + Tuấn Anh; Thọ khi có vấn đề truy nguồn | Cách hiển thị aspects, diễn giải, mức độ, nội dung suy ra và quote; lấy nhãn vị trí từ nguồn nào; không làm phẳng mất khía cạnh | Một báo cáo có nhiều khía cạnh và cảnh báo được hiển thị đúng, tuần 7 |
| Nhãn và phép đo | Đức Anh điều phối; Tuấn Anh + Dũng + Ngọc Anh phối hợp | Ranh giới change/aspect, ví dụ severity, matching 1–1 trước và 1–n bổ sung sau khi hoàn thành 1–1, ca chưa xác định; nhãn mong đợi khi thiếu tham chiếu; phân biệt lỗi mô hình với lỗi nguồn | Guideline/nhãn pilot và ca tính tay của kiểm thử/script phép đo, tuần 6–7; cố định trước đánh giá độc lập |
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
| Implementation Plan | Dũng cùng các chủ task | Có việc tuần đầu, đầu ra, phụ thuộc và reviewer |
| API contract | Dũng + Tuấn Anh; Đức Anh phối hợp schema | Có upload V1/S/tham chiếu, response mẫu, lỗi và báo cáo PARTIAL |
| Development guide | Đức Anh; từng chủ module bổ sung lệnh của mình | Thành viên khác cài, chạy và kiểm tra lại được |
| Workflow | Dũng | Có cách nhận task, branch, PR, review và tích hợp |
| Data annotation guide | Dũng; Tuấn Anh + Ngọc Anh review nhãn | Có mẫu V1–S, bằng chứng, dẫn chiếu, hiệu lực và quy trình review |
| test_evaluation_plan.md | Đức Anh điều phối; các owner phối hợp | Có ca pilot, phương án chia tập, matching 1–1 và cách kiểm tra kết luận thiếu căn cứ; matching 1–n bổ sung sau khi hoàn thành 1–1 |
| README | Đức Anh + Dũng | Giới thiệu đúng phạm vi và chỉ đến tài liệu chi tiết |

Hoàn thiện pilot trong tuần 6 rồi cập nhật quy tắc bị ảnh hưởng. Một quyết định công nghệ nội bộ chưa chốt không cản module khác dùng fixture; thiếu hợp đồng bàn giao thì cần xử lý trước khi tích hợp task phụ thuộc.

## 6. Tiến độ triển khai tuần 6–13

### Tuần 6 — Chốt điểm bàn giao và dựng khung

**Mục tiêu:** mỗi người có đầu vào–đầu ra mẫu, chạy được phần việc và biết điểm cần phối hợp.

- Dũng đồng bộ API/Pipeline, Đức Anh phối hợp schema và chuẩn bị context; các owner chốt contract/fixture rồi code song song. Dũng + Đức Anh phụ trách gọi/tích hợp LightRAG; chi tiết kỹ thuật chờ LK-13.
- Thọ triển khai Reader/Parser trên file thật; cùng Dũng lập fixture chỉ dẫn–vị trí đích, ngữ cảnh và hiệu lực.
- Ngọc Anh làm Text Diff trên fixture và cùng Thọ kiểm tra trước/sau; Tuấn Anh làm Semantic Change/Scorer. Các bên chốt dữ liệu Text Diff → Semantic Change, còn Semantic Change → Scorer là điểm nối nội bộ Tuấn Anh.
- Dũng tuyển chọn V1–S, manifest/tham chiếu và review căn cứ đủ/thiếu; hỗ trợ Thọ, Đức Anh, Ngọc Anh và Tuấn Anh xây fixture có đáp án nguồn.
- Tuấn Anh triển khai Semantic Diff với fixture/mock, giữ phần UI/session; kiểm tra chéo với Ngọc Anh và Đức Anh, phối hợp Dũng review nhãn pilot.

**Đầu ra:** môi trường chạy được, mock report hiển thị, Reader/Parser có kết quả file thật, fixture dùng chung, contract/fixture các điểm nối đã được bên giao và bên nhận xác nhận.

**Tiêu chí kết thúc:** từng người dùng được fixture của bên giao; quyết định còn thiếu có người xử lý và hạn chốt. Mock được ghi rõ trong môi trường phát triển.

### Tuần 7 — Tích hợp baseline V1–S

**Mục tiêu:** xử lý một cặp thật từ tải file đến báo cáo.

- Thọ hoàn thiện trích yêu cầu, liên kết V1 và hiệu lực cho các dạng đã thống nhất; giữ phần chưa xác định.
- Đức Anh hiện thực chuẩn bị context; Dũng + Đức Anh phụ trách gọi/tích hợp LightRAG, chi tiết kỹ thuật chốt theo LK-13 sau khi các quyết định khác hoàn thành; Thọ bảo đảm mapping nguồn, Dũng review căn cứ, Tuấn Anh/Ngọc Anh thử đầu vào phân tích.
- Ngọc Anh nối Text Diff; Tuấn Anh nối Semantic Change/Scorer với dữ liệu thật. Hai bên đối chiếu lỗi và kiểm tra chéo với Thọ/Đức Anh tại ranh giới bàn giao.
- Dũng tích hợp module thật, giữ định danh tài liệu, kết quả nội bộ và ComparisonReport.results/AmendmentResult cùng cảnh báo; báo PARTIAL phù hợp.
- Tuấn Anh nối UI, thử đủ/thiếu tài liệu, bổ sung rồi gửi lại bộ file; kiểm tra Semantic Diff và contract trên nhãn đã review.

**Đầu ra:** luồng chính không dùng mock nghiệp vụ, kết quả baseline trên tập phát triển và danh sách ca chưa hỗ trợ.

**Tiêu chí kết thúc:** có cả ca thành công và ca thiếu căn cứ; không biến lỗi hoặc Text Diff rỗng thành không có thay đổi.

### Tuần 8 — Cải thiện ngữ cảnh, ngữ nghĩa và độ ổn định

**Mục tiêu:** sửa lỗi gây mất/sai thay đổi, đo phương pháp và tài nguyên.

- Tuấn Anh so sánh phương pháp ngữ nghĩa với baseline trên tập phát triển; Ngọc Anh kiểm tra Text Diff, Tuấn Anh kiểm tra Scorer; ghi lỗi từng nhóm và thiếu/sai khía cạnh.
- Thọ sửa lỗi đọc, cấu trúc, vị trí đích và hiệu lực; Đức Anh sửa context, Dũng review căn cứ và bổ sung dữ liệu đại diện.
- Dũng đo thời gian từng bước, quản lý file tạm, giới hạn và deadline với chủ module liên quan.
- Tuấn Anh hoàn thiện hiển thị bằng chứng, nội dung suy ra, yêu cầu tham chiếu và PARTIAL; cùng owner bên giao/nhận kiểm thử tích hợp.
- Dũng + Tuấn Anh rà chất lượng nhãn, chia tập theo nguồn/chuỗi sửa đổi; Ngọc Anh kiểm tra matching 1–1 và ca tính tay; matching 1–n bổ sung sau khi hoàn thành 1–1. Giữ tập test độc lập với hiệu chỉnh thuật toán.

**Đầu ra:** báo cáo thử nghiệm trên tập phát triển, bộ regression, cấu hình đo được và phiên bản tích hợp ổn định.

**Tiêu chí kết thúc:** có bằng chứng cho lựa chọn phương pháp; không còn lỗi chặn luồng demo; biết giới hạn từng nhóm tình huống.

### Tuần 9 — Kiểm thử toàn hệ thống và trải nghiệm sử dụng

**Mục tiêu:** kiểm tra đầy đủ luồng nghiệp vụ, lỗi và khả năng sử dụng trước khi chốt thuật toán.

- Đức Anh điều phối kế hoạch kiểm thử toàn hệ thống theo SRS; Dũng điều phối tích hợp; Tuấn Anh kiểm tra Semantic Diff/UI; ghi lỗi kèm file đầu vào, commit, expected/actual và bằng chứng.
- Dũng kiểm tra API/Pipeline, giới hạn, deadline, dọn file và chạy đồng thời; sửa lỗi tích hợp.
- Thọ kiểm thử bố cục, bảng, ranh giới Điều, chỉ dẫn sửa đổi và các ca liên kết vị trí đích khó; bổ sung regression test.
- Tuấn Anh phân tích lỗi ngữ nghĩa/chấm điểm, Ngọc Anh phân tích Text Diff trên dev set; ưu tiên bỏ sót thay đổi quan trọng.
- Dũng kiểm tra nguồn, manifest, ngữ cảnh và trạng thái đủ/thiếu tham chiếu; Tuấn Anh điều phối thử nghiệm nhận diện V1/S/tham chiếu, giải thích thay đổi bằng lời của người tham gia, tìm bằng chứng/vị trí nguồn và hiểu cảnh báo. Ghi độ đúng, thời gian, lỗi diễn giải và phản hồi; nêu rõ nếu thành viên nhóm đóng vai người dùng.

**Đầu ra:** báo cáo kiểm thử tích hợp, danh sách lỗi có mức ưu tiên và người xử lý; các cải tiến UI được kiểm tra lại.

**Tiêu chí kết thúc:** các yêu cầu chính đều có ca kiểm thử và kết quả; lỗi chặn luồng có phương án xử lý trước mốc chốt tuần 10. Tập test độc lập tiếp tục được giữ riêng.

### Tuần 10 — Hoàn thiện chất lượng và chốt phiên bản ứng viên

**Mục tiêu:** hoàn tất cải thiện trên dev set và chuẩn bị một phiên bản ổn định cho đánh giá độc lập.

- Chủ module sửa lỗi ưu tiên từ tuần 9 và chạy lại regression; không mở rộng phạm vi chức năng.
- Ngọc Anh hoàn thiện Text Diff, Tuấn Anh hoàn thiện Semantic Change/Scorer trên dev set; ghi so sánh với baseline trên cùng dữ liệu.
- Dũng phối hợp Đức Anh đo lại thời gian/tài nguyên, chốt cấu hình vận hành và đóng gói phiên bản ứng viên.
- Hai owner từng điểm nối kiểm tra contract và script phép đo bằng ca tính tay, gồm nhiều khía cạnh, thiếu/sai khía cạnh; Dũng kiểm tra split/nhãn, Đức Anh kiểm tra quy tắc đối chiếu đã cố định.
- Cả nhóm review acceptance criteria, cập nhật hướng dẫn chạy và xác nhận các giới hạn cần công bố.

**Đầu ra:** phiên bản ứng viên gắn commit/tag, cấu hình và dependency cố định; bộ test độc lập có phiên bản; báo cáo thử nghiệm dev.

**Tiêu chí kết thúc:** không còn lỗi chặn đánh giá; dữ liệu, cách tính metric và lệnh chạy được cố định trước khi chạy đánh giá độc lập tuần 11.

### Tuần 11 — Đánh giá độc lập và nghiệm thu nội bộ

**Mục tiêu:** có kết quả chất lượng tái lập được cho phiên bản ứng viên.

- Đức Anh điều phối cả nhóm chạy đánh giá trên test set; Tuấn Anh kiểm tra ngữ nghĩa, Ngọc Anh kiểm tra Text Diff, Tuấn Anh kiểm tra Scorer; báo số mẫu, TP/FP/FN cấp SemanticChange, F1, Critical Change Recall, trường hợp chưa xác định và lỗi khía cạnh theo nhóm; tổng hợp đánh giá giải thích/khả năng hiểu báo cáo theo test_evaluation_plan.md.
- Cả nhóm kiểm tra acceptance criteria, trường hợp lỗi và chạy lại trên máy khác.
- Dũng tổng hợp minh chứng dữ liệu; Đức Anh tổng hợp phiên bản, giới hạn và báo cáo kỹ thuật.
- Chủ module phân tích lỗi; phân biệt lỗi cần sửa để bàn giao với hạn chế thuật toán cần công bố.
- Nhóm báo cáo số đo thực tế, phân tích lỗi và giới hạn theo cách đánh giá đã thống nhất; tạm lấy Change F1 ≥ 90% và Critical Change Recall ≥ 95%; đây là các ngưỡng dự tính và có thể thay đổi sau khi hoàn thiện test_evaluation_plan.md, chưa phải ngưỡng nghiệm thu chính thức.

**Đầu ra:** `evaluation-report.md`, biên bản nghiệm thu nội bộ, danh sách lỗi và giới hạn đã biết.

**Tiêu chí kết thúc:** số liệu gắn với phiên bản cụ thể. Nếu dùng lỗi trên test để chỉnh thuật toán, công bố việc đó; chỉ tuyên bố đánh giá độc lập mới trên dữ liệu chưa dùng để chỉnh.

### Tuần 12 — Đóng gói, hoàn thiện báo cáo và diễn tập

**Mục tiêu:** chuẩn bị đầy đủ bản nộp và kiểm chứng khả năng trình diễn.

- Dũng phối hợp Đức Anh đóng gói bản dự kiến nộp; thành viên khác chạy từ môi trường sạch theo hướng dẫn.
- Tuấn Anh cùng nhóm chuẩn bị kịch bản demo chính và dự phòng, dữ liệu mẫu và tài nguyên/mô hình chuẩn bị sẵn nếu sử dụng.
- Dũng rà soát nguồn và quyền phân phối dữ liệu; chủ module hoàn thiện mô tả phương pháp và giới hạn.
- Cả nhóm hoàn thiện README, báo cáo cuối kỳ, slide, phân công trình bày và diễn tập hỏi đáp.
- Chỉ sửa lỗi cần thiết; mọi thay đổi có regression test phù hợp. Nếu thay đổi ảnh hưởng kết quả, chạy lại đánh giá và ghi rõ quan hệ với kết quả tuần 11.

**Đầu ra:** gói sản phẩm dự kiến nộp, báo cáo/slide, hướng dẫn demo và checklist bàn giao.

**Tiêu chí kết thúc:** máy demo chạy được toàn luồng; số liệu trong báo cáo/slide khớp phiên bản được trích dẫn; mọi khác biệt với bản nộp đều được giải thích.

### Tuần 13 — Nộp sản phẩm và bàn giao

**Mục tiêu:** hoàn thành bàn giao chính thức và trình bày kết quả dự án.

- Dũng điều phối rà soát checklist, chốt commit/tag bản nộp và kiểm tra đầy đủ liên kết/tệp.
- Cả nhóm thực hiện demo và trình bày theo phân công; chuẩn bị giải thích phương pháp, kết quả và giới hạn.
- Bàn giao mã nguồn, dependency/cấu hình, hướng dẫn chạy, dữ liệu mẫu được phép phân phối, kết quả đánh giá, báo cáo và slide.
- Chỉ xử lý lỗi chặn bàn giao; nếu sửa, ghi phiên bản và kiểm tra lại phần bị ảnh hưởng trước khi nộp.
- Lưu bản nộp, ghi nhận phản hồi và các hướng phát triển tiếp theo.

**Đầu ra:** bộ sản phẩm cuối kỳ đầy đủ và bản ghi bàn giao.

**Tiêu chí kết thúc:** sản phẩm được nộp đúng yêu cầu; người nhận có thể chạy theo hướng dẫn; mã nguồn, tài liệu, minh chứng và kết quả đánh giá truy được về đúng phiên bản.

## 7. Danh mục công việc và phụ thuộc

Nhánh `ducanh_bachdung/integrate_LightRAG`, commit `e47e049ada29fdab95dcd39a5d0ad14d98c3b411`, đã có client HTTP, chunk builder, source registry, context builder và `context/semantic_bridge.py`. Có demo DOCX với adapter, Linker hẹp, Text Diff, baseline Semantic/Scorer và report PARTIAL. Demo chạy riêng bằng `backend.demo:app`; `backend.main:app` vẫn chưa cấu hình runner mặc định. Frontend demo là HTML/CSS/JavaScript, chưa thay định hướng frontend chính thức.

Chưa kiểm chứng LightRAG Server/model/index/KG thật; web demo tắt LightRAG. Bridge hiện chạy Context (gồm retrieval khi cấu hình) song song Text Diff rồi ghép trước Semantic; còn tách index/query và dùng Text Diff tạo query để khớp luồng mục tiêu mới. Rule baseline đã có, model fallback chưa tích hợp. Kết quả nhánh thử nghiệm không tự xác nhận đã merge main/nghiệm thu.

Căn cứ: [báo cáo tích hợp](https://github.com/Lyra1603/group4_legal_document_change_detection/blob/e47e049ada29fdab95dcd39a5d0ad14d98c3b411/docs/lightrag-integration-report.md), [demo và giới hạn](https://github.com/Lyra1603/group4_legal_document_change_detection/blob/e47e049ada29fdab95dcd39a5d0ad14d98c3b411/docs/local-web-demo.md). Kết quả test trong các báo cáo chưa được chạy lại trong đợt sửa tài liệu này.

Việc tiếp theo: tách index/query, ghép query từ Text Diff, kiểm chứng LightRAG thật, rule/model fallback và hiển thị bằng chứng. Nhận xét phát triển sau; mốc tuần vẫn là kế hoạch.

Task có thể bắt đầu bằng fixture trước khi module cung cấp dữ liệu hoàn thành; phụ thuộc dưới đây là điều kiện tích hợp bằng dữ liệu thật.

| Mã | Công việc | Chủ trì | Phụ thuộc và phối hợp để tích hợp | Mốc |
| --- | --- | --- | --- | --- |
| PL-01 | Tài liệu và điểm bàn giao | Đức Anh + Dũng | Chủ module review phạm vi liên quan | Đầu tuần 6 |
| PL-02 | Schema và fixture | Đức Anh | Thọ/Ngọc Anh/Dũng cung cấp ví dụ, Tuấn Anh thử report | Tuần 6 |
| PL-03 | Reader và Parser | Thọ | Dũng bàn giao file và vị trí nguồn kiểm chứng | Tuần 6 |
| PL-04 | Trích yêu cầu, liên kết và hiệu lực | Thọ | PL-03; Dũng review chỉ dẫn/đích, Ngọc Anh thử đầu vào | Tuần 6–7 |
| PL-05 | Text Diff | Ngọc Anh | PL-02; PL-04 khi tích hợp | Tuần 6–7 |
| PL-06 | Semantic Change và Scorer | Tuấn Anh | PL-04, PL-05, PL-17; nhãn pilot từ Dũng/Tuấn Anh | Tuần 6–8 |
| PL-07 | API/Pipeline | Dũng | PL-02; PL-03 đến PL-06, PL-17 khi nối thật | Tuần 6–7 |
| PL-08 | UI và bổ sung tài liệu | Tuấn Anh | API contract với Dũng; PL-07 khi nối thật | Tuần 6–8 |
| PL-09 | Dữ liệu, manifest và nhãn | Dũng quản lý dữ liệu/nhãn; người tạo và người review khác nhau | Cả nhóm gán nhãn, Ngọc Anh review ranh giới phân tích | Tuần 6–8 |
| PL-10 | Contract test và kiểm thử chéo | Hai owner tại từng điểm nối; Dũng điều phối | Fixture đã review; nhãn pilot/matching và ca tính tay với Dũng | Tuần 6–7 |
| PL-11 | Cải thiện phương pháp/hiệu năng | Chủ module; Dũng điều phối | Luồng tích hợp, dữ liệu phát triển và kiểm thử/script phép đo | Tuần 8–10 |
| PL-12 | Kiểm thử toàn hệ thống | Đức Anh điều phối kế hoạch; Dũng điều phối tích hợp; hai owner từng điểm nối kiểm tra | PL-07, PL-08; chủ module sửa lỗi của mình | Tuần 9–10 |
| PL-13 | Phiên bản ứng viên | Dũng; Đức Anh phối hợp kỹ thuật | PL-11, PL-12; cả nhóm review | Cuối tuần 10 |
| PL-14 | Đánh giá độc lập | Đức Anh điều phối cả nhóm | PL-13, tập test và cách tính cố định | Tuần 11 |
| PL-15 | Đóng gói, báo cáo, diễn tập | Dũng điều phối | PL-14; cả nhóm bàn giao phần phụ trách | Tuần 12 |
| PL-16 | Nộp và bàn giao | Dũng điều phối | PL-15 | Tuần 13 |
| PL-17 | Chuẩn bị ngữ cảnh/dẫn chiếu; gọi/tích hợp LightRAG | Đức Anh (context); Dũng + Đức Anh (gọi/tích hợp LightRAG) | PL-03, PL-04; Thọ cung cấp truy nguồn, Ngọc Anh thử đủ/thiếu căn cứ | Tuần 6–8 |

Mã giữ ổn định để dùng trong issue; PL-17 là phần ngữ cảnh có liên kết với PL-04 và PL-06, không phải bước chờ sau PL-16.

## 8. Dữ liệu, kiểm thử và đánh giá

Dũng bàn giao bộ V1–S với nguồn, hash, tham chiếu và giới hạn theo data-annotation-guide. Dũng quản lý nhãn/chia tập; người review khác người tạo nhãn. Hai owner từng điểm nối kiểm tra contract/matching 1–1; matching 1–n bổ sung sau khi hoàn thành 1–1; Đức Anh điều phối kế hoạch, khóa test và đánh giá theo test_evaluation_plan.md; Dũng phối hợp dữ liệu và tích hợp; Tuấn Anh kiểm tra ngữ nghĩa, Ngọc Anh kiểm tra Text Diff, Tuấn Anh kiểm tra mức độ. Cả nhóm tham gia review độc lập, không lấy kết quả thuật toán làm đáp án chuẩn.

Trước tuần 7 cần có mẫu sửa toàn đơn vị, sửa cụm từ, bổ sung/bãi bỏ, nhiều thay đổi trong một Điều, S sửa nhiều văn bản, vị trí đích mơ hồ và dẫn chiếu đủ/thiếu. Trước tuần 9 bổ sung hiệu lực có ngoại lệ, bảng/đoạn ngoài Điều làm căn cứ, file lỗi/quá giới hạn, null/rỗng, lỗi module, PARTIAL và gửi lại sau bổ sung tài liệu.

Đánh giá bằng các chỉ số và phân tích lỗi theo test_evaluation_plan.md; tạm lấy Change F1 ≥ 90% và Critical Change Recall ≥ 95%; đây là các ngưỡng dự tính và có thể thay đổi sau khi hoàn thiện test_evaluation_plan.md, chưa phải ngưỡng nghiệm thu chính thức. Đức Anh điều phối cả nhóm đo; hai owner từng điểm nối kiểm tra đầu ra/cách dùng, Dũng review căn cứ và chất lượng giải thích. Không sao chép công thức hoặc quy tắc gán nhãn vào kế hoạch này.

Kết quả phải gắn với commit, cấu hình, dependency/mô hình nếu có, dữ liệu và nhãn có phiên bản. Số liệu từ mẫu thiếu căn cứ hoặc dữ liệu giả định được giải thích đúng mục đích; không dùng thông tin ngoài bộ đầu vào để yêu cầu kết luận chắc chắn. Không chỉnh test sau khi xem kết quả để tuyên bố đạt.

## 9. Quy trình làm việc và bàn giao

1. Issue ghi phạm vi, người sở hữu, reviewer, đầu ra, tiêu chí hoàn thành, phụ thuộc và quyết định cần phối hợp.
2. Chủ module phát triển trên branch riêng, dùng fixture thống nhất. Chỉ yêu cầu phối hợp khi chạm điểm bàn giao hoặc gặp tình huống ảnh hưởng bên khác.
3. PR nêu thay đổi, cách kiểm tra, bằng chứng và giới hạn; nếu đổi contract ghi các bên nhận bị ảnh hưởng và thứ tự tích hợp.
4. Reviewer kiểm tra phần liên quan; người nhận đầu ra chạy thử fixture hoặc mẫu thật trước khi đóng task tích hợp.
5. Merge sau khi review và kiểm tra bắt buộc đạt; kiểm tra lại luồng bị ảnh hưởng sau merge.

Module hoàn thành khi có mã nguồn, ví dụ đầu vào–đầu ra, kiểm tra phù hợp, hướng dẫn chạy và giới hạn; bên nhận sử dụng được đầu ra. Tính năng đầu-cuối hoàn thành khi thao tác người dùng trả đúng kết quả hoặc lỗi theo hợp đồng.

Bàn giao cuối gồm mã nguồn, cấu hình/dependency, hướng dẫn chạy, dữ liệu mẫu được phép phân phối, kết quả đánh giá, báo cáo và slide. Đức Anh điều phối tổng hợp báo cáo kiểm thử/đánh giá từ các owner; Dũng tổng hợp minh chứng dữ liệu/nghiệp vụ; Thọ, Ngọc Anh và Tuấn Anh bàn giao phương pháp/giới hạn phần phụ trách; Dũng kiểm tra gói chạy/phiên bản chung, Đức Anh phối hợp kỹ thuật.

## 10. Cập nhật kế hoạch và quyết định

| Thay đổi | Người cần tham gia | Cập nhật chính |
| --- | --- | --- |
| Thuật toán/thư viện nội bộ | Chủ module; Đức Anh nếu ảnh hưởng môi trường | Dependency, hướng dẫn module và kết quả thử nghiệm |
| Hợp đồng dữ liệu | Bên cung cấp + bên nhận; Đức Anh điều phối | SRS, schema, fixture, API contract khi liên quan |
| Quy tắc nhãn/căn cứ | Dũng + Tuấn Anh + chủ module liên quan | Data annotation guide, nhãn bị ảnh hưởng và hồ sơ review |
| Phân công | Dũng + người giao/nhận task | Mục 1, 4, 7 và Architecture nếu thay vai trò module |
| Tiến độ | Dũng + chủ task và bên phụ thuộc | Mục 2, 6, 7; nêu ảnh hưởng và phương án |
| Giới hạn vận hành | Đức Anh + chủ module; Tuấn Anh ở phía UI | Cấu hình, API contract, hướng dẫn chạy và ca giới hạn |
| Phạm vi/kiến trúc | Đức Anh + Dũng + các chủ module bị ảnh hưởng | BRD/SRS/Architecture trước, rồi task và kế hoạch |
| Phép đo | Đức Anh điều phối; hai owner điểm nối và Dũng phối hợp | test_evaluation_plan.md và phiên bản kết quả |

Giữ lịch sử qua commit/PR, tăng phiên bản khi kế hoạch thay đổi. Không cần viết lại toàn bộ tài liệu vì một lựa chọn nội bộ; chỉ cập nhật phần sở hữu quyết định và các phần phụ thuộc thực sự bị ảnh hưởng.


## 11. Quy định triển khai áp dụng chung

- Giữ cấu trúc folder chính và file bắt buộc theo [Module](module.md); được thêm file hỗ trợ trong module, không tự đổi giao diện hoặc đường dẫn chính.
- Phát triển bán song song: trước task phụ thuộc, hai owner chốt hợp đồng và input/output fixture; bên nhận code với mock/fixture, bên giao hoàn thiện output thật; kiểm tra và tích hợp từng điểm nối sớm. Trình tự xử lý runtime không phải lịch chờ lập trình.
- Mỗi task và chức năng/module có người chịu trách nhiệm; có thể nhiều người tham gia. Folder change_analysis phân công theo chức năng: Ngọc Anh Text Diff, Tuấn Anh Semantic Change/Scorer; AI Adapter do Dũng + Đức Anh. Không tự gán owner toàn folder; Dũng + Đức Anh phụ trách gọi/tích hợp LightRAG; Đức Anh phụ trách context và điều phối kế hoạch đánh giá.
- Không triển khai Evaluator riêng; giữ folder/file cũ để không đổi cấu trúc. Test module do owner viết, contract/integration test do hai owner cùng review; Dũng điều phối tích hợp, Đức Anh điều phối kế hoạch đánh giá. Nhãn/metric vẫn cần khi đo chất lượng.
- Git theo [Workflow](workflow.md): issue/task, branch có tên thống nhất, commit theo phạm vi, PR và reviewer bên nhận; không tự push vào nhánh chung hoặc thay schema mà chưa phối hợp.

Dũng + Đức Anh đã được chốt phụ trách gọi/tích hợp LightRAG. Chi tiết LK-13 không bị áp một mốc tuần như nhiệm vụ kỹ thuật đã chốt; chỉ hoàn thiện sau các quyết định còn lại. Mốc chuẩn bị context/nguồn trong kế hoạch không đồng nghĩa chốt trước chi tiết kỹ thuật LightRAG. Quy trình Git và kiểm thử tập trung tại workflow.md.
