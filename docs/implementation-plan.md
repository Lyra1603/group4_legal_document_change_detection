# KẾ HOẠCH TRIỂN KHAI DỰ ÁN

**Dự án:** Legal Document Change Detection  
**Phiên bản kế hoạch:** 1.3.0  
**Thời gian thực hiện:** Cuối tuần 5 đến hết tuần 13  
**Người điều phối:** Dương Đức Anh  
**Tài liệu liên quan:** [BRD](brd.md), [SRS 1.2.0](srs.md), [Architecture 1.2.0](architecture.md)  

## 1. Mục tiêu

Xây dựng ứng dụng so sánh hai phiên bản văn bản pháp luật, phát hiện thay đổi chữ và thay đổi nghĩa, phân loại mức tác động và hiển thị báo cáo có bằng chứng.

Kế hoạch gồm năm giai đoạn:

1. **Cuối tuần 5:** hoàn thành bộ tài liệu tổng quát và hướng dẫn bàn giao để các thành viên bắt đầu triển khai từ tuần 6.
2. **Tuần 6–8:** xây dựng các module, tích hợp ứng dụng và cải thiện chất lượng.
3. **Tuần 9–10:** kiểm thử toàn hệ thống, cải thiện chất lượng và hoàn thiện phiên bản ứng viên.
4. **Tuần 11–12:** đánh giá độc lập, nghiệm thu nội bộ và chuẩn bị bản nộp.
5. **Tuần 13:** trình bày, nộp sản phẩm và bàn giao dự án.

Kế hoạch mô tả mục tiêu, trách nhiệm và đầu ra. Tên công nghệ được quản lý tập trung tại mục 3; công việc ở các mục sau được mô tả theo chức năng để thuận tiện cập nhật sau các cuộc họp.

## 2. Phạm vi sản phẩm

### 2.1. Đầu vào và đầu ra

- Nhận hai phiên bản đầy đủ của cùng một VBQPPL Việt Nam bằng tiếng Việt; người dùng chỉ rõ bản cũ V1 và bản mới V2.
- Hỗ trợ PDF có lớp chữ và DOCX; giữ vị trí nguồn của nội dung trích xuất.
- Phân tách và so sánh ở cấp Điều; giữ nội dung Khoản/Điểm bên trong Điều.
- Nhận diện cặp Điều tương ứng, Điều thêm/xóa và đánh lại số; cảnh báo khi ghép mơ hồ hoặc nghi ngờ tách/gộp.
- Báo cáo nhận diện hai file bằng old_document/new_document, hiển thị rõ bản cũ V1, bản mới V2 và chiều so sánh, kể cả khi trùng tên file.
- Báo cáo gồm thay đổi chữ, kết luận thay đổi nghĩa, nhãn tổng thể, mức tác động, giải thích, bằng chứng và cảnh báo; mỗi SemanticChange có danh sách ChangeAspect theo 8 nhóm trong SRS.
- Mỗi khía cạnh có nhóm trường, nội dung cũ/mới, diễn giải ý nghĩa chuyển đổi, bằng chứng và cảnh báo. UI hiển thị vị trí nguồn của Điều ở đúng phiên bản; không chỉ dùng màu để truyền đạt kết quả.
- Phân biệt kết luận không có thay đổi với trường hợp chưa xử lý hoặc chưa xác định được.

### 2.2. Giới hạn

Không thực hiện OCR, dựng phiên bản đầy đủ từ văn bản chỉ liệt kê sửa đổi, tự giải quyết căn chỉnh một-nhiều/nhiều-một hoặc tư vấn pháp lý. Nội dung ngoài phần Điều được ghi nhận là ngoài phạm vi so sánh. Bản đầu không có tài khoản, lịch sử so sánh lâu dài hoặc cơ sở dữ liệu nghiệp vụ.

### 2.3. Cách vận hành

Ứng dụng dùng request đồng bộ. Frontend gửi hai file; Backend kiểm tra đầu vào, chạy Pipeline và trả báo cáo trong cùng request. Giao diện hiển thị đang xử lý trong thời gian chờ.

Pipeline gọi lần lượt Reader → Parser → Aligner → Text Diff → Semantic Diff → Classifier & Scorer rồi tổng hợp ComparisonReport. Các module dùng hợp đồng dữ liệu chung. Evaluator chạy riêng khi kiểm thử và đánh giá.

Backend ghi nhận DocumentIdentity của V1/V2 và truyền cùng file cho Pipeline. Semantic Diff tạo aspects; Classifier & Scorer chọn category và chấm toàn bộ SemanticChange. Pipeline giữ đầy đủ khía cạnh, bằng chứng, vị trí nguồn và tổng hợp cảnh báo đến báo cáo theo Architecture 1.2.0.

## 3. Danh mục lựa chọn kỹ thuật

Bảng dưới đây là phương án kỹ thuật được đề xuất để các thành viên lựa chọn


| STT | Thành phần | Lựa chọn | Lý do và ranh giới |
| --- | --- | --- | --- |
| 1 | Backend | Python 3.11, FastAPI, Uvicorn | Phù hợp các module xử lý văn bản Python; API chỉ nhận/trả HTTP và điều phối |
| 2 | Schema | Pydantic | Kiểm tra cấu trúc dữ liệu ở ranh giới; hợp đồng nghiệp vụ theo SRS |
| 3 | Frontend | React + TypeScript + Vite, CSS thông thường | Một trang upload/báo cáo; chia component và kiểu dữ liệu rõ ràng |
| 4 | Giao tiếp | HTTP multipart upload, JSON response, trình duyệt dùng Fetch | API đồng bộ `POST /api/compare`; file fields `doc_v1`, `doc_v2` |
| 5 | Reader | PyMuPDF cho PDF; python-docx cho DOCX | Giữ thứ tự nội dung, trang/đoạn/bảng và source refs; kiểm thử layout thực tế |
| 6 | Parser | Quy tắc cấu trúc và biểu thức chính quy Python | Tách cấp Điều; kiểm tra câu dẫn chiếu và ranh giới phụ lục |
| 7 | Aligner | Số Điều + tiêu đề + độ tương đồng nội dung; difflib làm baseline | Ghép một-một có kiểm soát; trường hợp cạnh tranh/mơ hồ cần review |
| 8 | Text Diff | Python difflib | Xác định thêm/xóa/thay thế ở mức token; giữ dấu câu và số liệu |
| 9 | Semantic Diff | Quy tắc nghiệp vụ kết hợp Sentence Transformers; mô hình `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` chạy local | Baseline rules-only để đối chiếu; embedding hỗ trợ nhận diện diễn đạt, không tự quyết định ý nghĩa pháp lý |
| 10 | Classifier & Scorer | Bộ quy tắc có cấu hình, theo guideline gán nhãn | Đọc aspects, chọn category tổng thể và chấm từng SemanticChange; không tạo lại aspects hoặc chấm riêng từng khía cạnh |
| 11 | Dữ liệu | File nguồn + CSV manifest + JSON nhãn/kết quả | Dễ kiểm tra và tái lập; file upload nằm trong thư mục tạm riêng |
| 12 | Kiểm thử | pytest cho backend/evaluator; Vitest và React Testing Library cho UI; GitHub Actions cho kiểm tra tự động | Kiểm thử hành vi, contract và các trường hợp lỗi quan trọng |
| 13 | Môi trường phát triển | venv + pip; Node.js 22.12 trở lên thuộc nhánh 22 LTS + npm | Khóa phiên bản dependency đã kiểm tra; lưu package-lock.json và requirements có phiên bản |
| 14 | Chạy demo | Một máy local; frontend build tĩnh được backend phục vụ | Một địa chỉ truy cập; mô hình tải và chuẩn bị trước demo, suy luận local |

### 3.1. Nguyên tắc triển khai phần ngữ nghĩa

- Phân tích các đoạn thay đổi kèm ngữ cảnh và giữ liên kết với toàn bộ cặp Điều.
- Semantic Diff tạo SemanticChange với giải thích tổng thể và aspects theo SRS mục 1.3: nhóm trường, nội dung cũ/mới, interpretation, bằng chứng và cảnh báo. Danh mục 8 nhóm là hợp đồng dữ liệu; đo khả năng nhận diện thực tế từng nhóm, không mặc định baseline nhận diện tốt tất cả.
- Các khía cạnh cùng mô tả một thay đổi quy định được nhóm chung; thay đổi độc lập được tách theo guideline. Không nhân bản cùng một biến đổi vào nhiều nhóm; quy tắc ranh giới theo SRS.
- Classifier & Scorer chọn category tổng thể từ các nhóm đã xác định; WORDING_ONLY khi chỉ đổi diễn đạt, null khi chưa chọn được nhãn. Một SemanticChange có một ScoringResult; không cộng mức độ theo số khía cạnh.
- Giữ cảnh báo từ khía cạnh lên các cấp kết quả. aspects rỗng phải được đọc cùng is_meaningful_change và needs_review; không tự suy ra không đổi nghĩa. Nội dung hoặc bằng chứng chưa xác định phải được phân biệt với phía không tồn tại.
- Với Điều dài, chia đoạn có ánh xạ nguồn theo giới hạn tokenizer; không cắt bỏ âm thầm phần cuối khi tạo embedding.
- Kiểm tra riêng số tiền, thời hạn, chủ thể, quyền/nghĩa vụ, phủ định và điều kiện áp dụng. Độ tương đồng cao không đủ kết luận không đổi nghĩa.
- Giải thích bằng mẫu có bằng chứng; không yêu cầu mô hình embedding sinh văn bản giải thích.
- Trường hợp vượt khả năng quy tắc hoặc bằng chứng không đủ trả trạng thái chưa xác định theo SRS.
- Hiệu chỉnh ngưỡng trên tập phát triển và so sánh với baseline; không coi lựa chọn mô hình là bảo đảm đạt metric.
- Nạp mô hình một lần khi khởi động; báo sẵn sàng sau khi mô hình đã nạp. Thuật toán được đóng gói trong module để có thể thay đổi mà giữ input/output.

### 3.2. Cấu hình vận hành ban đầu

Các giá trị cấu hình dưới đây là đề xuất ban đầu để thử nghiệm,
chưa phải giới hạn đã được nhóm xác nhận hoặc hiệu năng đã đo.

| Tham số | Giá trị kế hoạch |
| --- | --- |
| Dung lượng tối đa | 10 MiB mỗi file |
| Nội dung trích xuất tối đa | 100.000 ký tự mỗi phiên bản |
| Số Điều tối đa | 100 Điều mỗi phiên bản |
| Mức đồng thời demo | 1 lần so sánh; yêu cầu vượt mức nhận lỗi bận |
| Ngân sách xử lý Pipeline | 120 giây |
| Thời gian chờ frontend | 150 giây, gồm dư địa nhận phản hồi; xét riêng thời gian upload khi đo |
| Gửi lại yêu cầu | Người dùng chủ động gửi lại; frontend không tự retry toàn bộ POST |

Deadline được kiểm tra giữa các bước/đoạn xử lý. Timeout request không tự ngắt phép tính đang chạy; tác vụ không hỗ trợ hủy chỉ được dọn file khi đã kết thúc. Chỉ trả PARTIAL khi tổng hợp được báo cáo hợp lệ; lỗi và phần chưa xử lý phải rõ ràng. Các giá trị HTTP cụ thể được định nghĩa một lần trong API contract.

## 4. Phân công trách nhiệm

| Thành viên | Phụ trách chính | Đầu ra bàn giao | Kiểm tra chéo |
| --- | --- | --- | --- |
| Dương Đức Anh | Tài liệu tổng quát, schema, API, Pipeline và tích hợp | Contract có ChangeAspect/DocumentIdentity, môi trường chạy, báo cáo giữ đủ aspects/metadata và quản lý lỗi | Tuấn Anh kiểm thử API/UI; Thọ review dữ liệu |
| Bùi Quang Thọ | Reader, Parser, Aligner | Module đọc/tách/ghép, fixture, test và source refs | Dũng đối chiếu nguồn; Đức Anh review contract |
| Đoàn Ngọc Anh | Text Diff, Semantic Diff, Classifier & Scorer | Baseline và phương pháp ngữ nghĩa tạo aspects, quy tắc chọn category/chấm tổng thể và test | Tuấn Anh/Dũng đối chiếu nhãn; Đức Anh review tích hợp |
| Bạch Công Dũng | Architecture, dữ liệu và manifest, phối hợp guideline | Cặp tài liệu, nguồn, guideline cho 8 nhóm và nhãn khía cạnh được review, các ca khó | Thọ kiểm tra khả năng đọc; Tuấn Anh kiểm tra dữ liệu đánh giá |
| Đỗ Tuấn Anh | Frontend, Evaluator, điều phối kiểm thử | UI hiển thị khía cạnh/vị trí nguồn, Evaluator với nhãn có aspects, test report và metric | Đức Anh review UI/API; Ngọc Anh kiểm tra ví dụ tính metric |

Tuấn Anh điều phối nhãn chuẩn và cách đánh giá; Dũng quản lý dữ liệu/manifest, phối hợp guideline; Ngọc Anh review khả năng phân tích và ranh giới khía cạnh.

Mỗi chủ module tự viết test phù hợp. Cả nhóm tham gia gán nhãn và kiểm tra chéo để giảm tải cho người phụ trách đánh giá. Mọi task có một người chịu trách nhiệm cuối cùng và một người review; người phối hợp được ghi trong issue.

## 5. Kế hoạch tài liệu đến cuối tuần 5

**Mốc bàn giao:** cuối tuần 5 có bộ tài liệu tổng quát đủ để các thành viên nhận việc từ tuần 6. Đức Anh điều phối và hoàn thiện; chủ module review phần liên quan.

| Tài liệu | Nội dung cần có ở mốc bàn giao |
| --- | --- |
| `brd.md` | Mục tiêu, phạm vi và đầu ra sản phẩm |
| `srs.md` | SRS 1.2.0: ChangeAspect, 8 nhóm trường, DocumentIdentity, trạng thái/cảnh báo và tiêu chí chất lượng |
| `architecture.md` | Architecture 1.2.0: ranh giới tạo khía cạnh/chấm tổng thể, luồng dữ liệu và request đồng bộ |
| `implementation-plan.md` | Công nghệ, phân công, tiến độ và tiêu chí hoàn thành |
| `api-contract.md` | Upload, response mẫu có old_document/new_document và aspects, lỗi HTTP và SUCCESS/PARTIAL/FAILED |
| `development-guide.md` | Môi trường, dependency, lệnh chạy/test và cấu hình |
| `workflow.md` | Nhận task, branch, PR, review, kiểm thử và merge |
| `data-annotation-guide.md` | Bản đầu: chọn cặp/nguồn, 8 nhóm khía cạnh, ví dụ ranh giới, chia/gộp SemanticChange, chọn category và severity; Dũng phối hợp Tuấn Anh/Ngọc Anh |
| `test-evaluation-plan.md` | Bản đầu: test case, chia dữ liệu, matching có xét thiếu/sai khía cạnh, metric và đánh giá giải thích/khả năng hiểu báo cáo; Tuấn Anh chủ trì |
| README gốc | Giới thiệu, thứ tự đọc tài liệu và hướng dẫn bắt đầu |

Guideline và evaluation plan được hoàn thiện bằng pilot tuần 6, rồi cố định quy tắc trước đánh giá độc lập. Cuối tuần 5 không yêu cầu thuật toán hoặc dữ liệu đánh giá đã hoàn thành.

**Tiêu chí bàn giao tài liệu:** không mâu thuẫn phạm vi/contract; có ví dụ dữ liệu; công nghệ và trách nhiệm rõ ràng; từng thành viên xác định được input, output, task đầu tiên và cách kiểm tra kết quả. Nếu một chi tiết chưa đủ để thực hiện, bổ sung vào đúng tài liệu sở hữu trước khi giao task phụ thuộc.

## 6. Tiến độ triển khai tuần 6–13

### Tuần 6 — Môi trường, hợp đồng và khung xử lý

**Mục tiêu:** các thành viên chạy được dự án và phát triển song song theo cùng contract.

- Đức Anh dựng môi trường, hiện thực schema có ChangeAspect/DocumentIdentity, API upload và Pipeline bằng mock; báo cáo giữ metadata V1/V2, aspects và cảnh báo theo SRS 1.2.0.
- Thọ triển khai Reader PDF/DOCX, Parser cấp Điều; phát triển Aligner baseline bằng fixture.
- Ngọc Anh triển khai Text Diff và baseline ngữ nghĩa tạo aspects/chấm tổng thể trên cặp Điều mẫu; ghi rõ nhóm nhận diện được và trường hợp chưa xác định.
- Tuấn Anh dựng form V1/V2 và báo cáo mock hiển thị từng khía cạnh, bằng chứng, vị trí nguồn; tạo khung Evaluator cấp SemanticChange với ca tính tay và nhãn có aspects.
- Dũng tuyển chọn cặp tài liệu, lập manifest; phối hợp Tuấn Anh tổ chức pilot gán nhãn khía cạnh theo 8 nhóm cùng nhóm.
- Nhóm hoàn thiện guideline và tạo fixture cho không đổi, đổi diễn đạt, đổi nghĩa, thêm/xóa, đánh lại số, ghép mơ hồ; có một thay đổi nhiều khía cạnh, khía cạnh chưa rõ và file trùng tên.

**Đầu ra:** repo chạy được theo hướng dẫn; upload nhận hai file; mock report hiển thị trên UI; Reader/Parser có test trên file thật; các module còn lại có đầu vào/đầu ra mẫu.

**Tiêu chí kết thúc:** một thành viên khác chạy lại được; schema/fixture thống nhất; ghi rõ mock trong môi trường phát triển, không trình bày như kết quả phân tích thật.

### Tuần 7 — Tích hợp đầu-cuối bằng baseline

**Mục tiêu:** so sánh hai tài liệu thật và trả báo cáo qua giao diện.

- Thọ hoàn thiện Aligner; kiểm tra thêm/xóa, đánh lại số và ghép mơ hồ.
- Ngọc Anh hoàn thiện baseline Text Diff/Semantic Diff/Scorer với aspects, bằng chứng, category tổng thể và trạng thái chưa xác định; kiểm tra tránh ghi trùng khía cạnh.
- Đức Anh nối các module thật vào Pipeline, giữ metadata hai file, định danh/source refs và aspects; tổng hợp cảnh báo từ khía cạnh cùng lỗi đến báo cáo.
- Tuấn Anh kết nối UI với API thật, hiển thị cũ/mới và từng khía cạnh; hoàn thiện Evaluator trên bộ nhỏ đã review, không đếm mỗi aspect thành một thay đổi độc lập.
- Dũng cùng nhóm mở rộng dữ liệu, đối chiếu lỗi trích xuất/căn chỉnh và rà soát nhãn.

**Đầu ra:** luồng file → Reader → Parser → Aligner → Diff → Scorer → UI không dùng mock ở các bước nghiệp vụ; có số đo baseline trên dev set.

**Tiêu chí kết thúc:** xử lý đúng hợp đồng các ca đại diện và lỗi; không biến thất bại phân tích thành kết luận không thay đổi. Mốc này xác nhận luồng hoạt động, chưa chứng nhận đạt mục tiêu chất lượng.

### Tuần 8 — Cải thiện ngữ nghĩa và ổn định hệ thống

**Mục tiêu:** đo, cải thiện lỗi quan trọng và kiểm soát tài nguyên.

- Ngọc Anh tích hợp phương pháp ngữ nghĩa tại mục 9 trong bảng công nghệ, so sánh với rules-only trên cùng dev set; ghi kết quả theo 8 nhóm, lỗi thiếu/sai khía cạnh và giới hạn nhận diện.
- Thọ sửa lỗi đọc, tách và ghép có ảnh hưởng lớn; bổ sung regression test.
- Đức Anh đo thời gian từng module, hiệu chỉnh cấu hình, xử lý file tạm, quá tải và deadline.
- Tuấn Anh hoàn thiện hiển thị PARTIAL, cảnh báo từng khía cạnh và vị trí nguồn đúng V1/V2; kiểm tra tên file trùng, phân biệt category với field_group và chạy kiểm thử tích hợp.
- Dũng hoàn thiện manifest, nhãn có khía cạnh và ca khó; Tuấn Anh cùng nhóm cố định cách matching, xử lý thiếu/sai khía cạnh và tập test độc lập; ghi độ bao phủ 8 nhóm.

**Đầu ra:** báo cáo thử nghiệm dev, cấu hình vận hành, bộ regression và phiên bản tích hợp để kiểm thử mở rộng.

**Tiêu chí kết thúc:** có bằng chứng chọn phương pháp; không còn lỗi chặn luồng demo; dữ liệu test không được dùng để hiệu chỉnh thuật toán.

### Tuần 9 — Kiểm thử toàn hệ thống và trải nghiệm sử dụng

**Mục tiêu:** kiểm tra đầy đủ luồng nghiệp vụ, lỗi và khả năng sử dụng trước khi chốt thuật toán.

- Tuấn Anh điều phối kiểm thử đầu-cuối theo SRS; ghi lỗi kèm file đầu vào, commit, expected/actual và bằng chứng.
- Đức Anh kiểm tra API/Pipeline, giới hạn, deadline, dọn file và chạy đồng thời; sửa lỗi tích hợp.
- Thọ kiểm thử layout, bảng, ranh giới Điều và các ca căn chỉnh khó; bổ sung regression test.
- Ngọc Anh phân tích lỗi ngữ nghĩa/chấm điểm trên dev set, ưu tiên bỏ sót thay đổi quan trọng.
- Dũng rà soát nguồn, manifest và nhãn; Tuấn Anh điều phối thử nghiệm nhận diện cũ/mới, giải thích thay đổi bằng lời của người tham gia, tìm bằng chứng/vị trí nguồn và hiểu cảnh báo. Ghi độ đúng, thời gian, lỗi diễn giải và phản hồi; nêu rõ nếu thành viên nhóm đóng vai người dùng.

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
- Tuấn Anh cùng nhóm chuẩn bị kịch bản demo chính và dự phòng, dữ liệu mẫu và mô hình tải sẵn.
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

Các mã là mã lập kế hoạch, được dùng khi tạo issue. Task có thể làm bằng fixture trước khi module cung cấp dữ liệu hoàn thành.

| Mã | Công việc | Chủ trì | Phụ thuộc để tích hợp | Mốc |
| --- | --- | --- | --- | --- |
| PL-01 | Bàn giao tài liệu tổng quát | Đức Anh | Review của nhóm | Cuối tuần 5 |
| PL-02 | Môi trường, schema và fixture có ChangeAspect/DocumentIdentity | Đức Anh | PL-01 | Tuần 6 |
| PL-03 | Reader và Parser | Thọ | PL-02, dữ liệu mẫu | Tuần 6 |
| PL-04 | Aligner | Thọ | PL-03 | Tuần 7 |
| PL-05 | Text Diff | Ngọc Anh | PL-02; PL-04 khi tích hợp | Tuần 6–7 |
| PL-06 | Semantic Diff tạo aspects và Scorer baseline chấm tổng thể | Ngọc Anh | PL-05, guideline | Tuần 7 |
| PL-07 | API/Pipeline giữ metadata hai file, aspects và cảnh báo | Đức Anh | PL-02; PL-03 đến PL-06 khi tích hợp | Tuần 6–7 |
| PL-08 | Giao diện chọn file và báo cáo khía cạnh/bằng chứng/vị trí nguồn | Tuấn Anh | API contract; PL-07 khi tích hợp | Tuần 6–7 |
| PL-09 | Dữ liệu, manifest và nhãn chuẩn có khía cạnh | Dũng; Tuấn Anh phối hợp | Guideline; review của nhóm | Tuần 6–8 |
| PL-10 | Evaluator cấp SemanticChange có kiểm tra khía cạnh | Tuấn Anh | Schema, quy tắc đo và nhãn mẫu | Tuần 6–7 |
| PL-11 | Cải thiện chất lượng và hiệu năng | Chủ module; Đức Anh điều phối | Luồng tích hợp, PL-09, PL-10 | Tuần 8–10 |
| PL-12 | Kiểm thử toàn hệ thống, diễn giải/khả năng hiểu báo cáo và sửa lỗi | Tuấn Anh; các chủ module | Luồng tích hợp, PL-09, PL-10 | Tuần 9–10 |
| PL-13 | Chốt phiên bản ứng viên | Đức Anh; cả nhóm | PL-11, PL-12 | Cuối tuần 10 |
| PL-14 | Đánh giá độc lập và nghiệm thu nội bộ | Tuấn Anh; cả nhóm | PL-13, tập test cố định | Tuần 11 |
| PL-15 | Đóng gói, báo cáo và diễn tập demo | Đức Anh; cả nhóm | PL-14 | Tuần 12 |
| PL-16 | Nộp sản phẩm và bàn giao chính thức | Đức Anh; cả nhóm | PL-15 | Tuần 13 |

## 8. Dữ liệu, kiểm thử và mục tiêu chất lượng

### 8.1. Tổ chức dữ liệu

Dũng quản lý manifest liên kết V1/V2, nguồn, phiên bản, định dạng, phạm vi và split. Fixture tự tạo phục vụ test kỹ thuật được phân biệt với tài liệu thật dùng đánh giá. Nhãn quan trọng có người review độc lập và ghi lý do giải quyết bất đồng.

Nhãn chuẩn lưu SemanticChange và các khía cạnh kỳ vọng theo SRS, gồm nhóm, nội dung trước/sau, diễn giải và bằng chứng. Tuấn Anh điều phối nhãn chuẩn; Dũng phối hợp tuyển chọn, ghi độ bao phủ 8 nhóm và các trường hợp chưa xác định. Phân biệt số cặp tài liệu, số thay đổi và số khía cạnh; không dùng số khía cạnh thay cho số thay đổi.

Chia dữ liệu theo nhóm văn bản/chuỗi phiên bản để tránh cùng nội dung hoặc cặp chồng lặp xuất hiện ở cả dev và test. Chọn quy mô sau pilot theo năng lực gán nhãn, ghi số lượng trong evaluation plan; số lượng không thay thế độ đa dạng ca kiểm thử.

### 8.2. Ca kiểm thử bắt buộc

- Không đổi; đổi diễn đạt; đổi nghĩa liên quan số liệu, thời hạn, phủ định hoặc điều kiện.
- Thêm/xóa, đánh lại số, ghép mơ hồ, nghi ngờ tách/gộp Điều.
- Điều nhiều trang, bảng, câu dẫn chiếu chứa chữ “Điều”, phụ lục sau Điều cuối.
- Thiếu file, file rỗng/hỏng/sai định dạng/scan, vượt giới hạn và hệ thống bận.
- Module lỗi, deadline, báo cáo một phần và kết luận chưa xác định.
- Một SemanticChange có nhiều khía cạnh; nhiều thay đổi độc lập trong một Điều; khía cạnh cùng nhóm nhưng nội dung khác nhau; không nhân bản một biến đổi vào nhiều nhóm.
- Đối chiếu field_group, giá trị cũ/mới, diễn giải và bằng chứng đúng phía; phân biệt thiếu căn cứ với phía không tồn tại; cảnh báo được giữ từ khía cạnh đến UI.
- Chỉ đổi diễn đạt với aspects rỗng; chưa xác định với aspects rỗng; category tổng thể khác với danh sách nhóm của khía cạnh; mức độ không tăng theo số khía cạnh.
- Hai file trùng tên vẫn phân biệt được V1/V2; nhiều vị trí nguồn của một Điều; Điều thêm/xóa chỉ có nguồn phía tồn tại.
- UI hiển thị đủ khía cạnh và đúng source refs/cảnh báo, không chỉ dùng màu, không gửi lặp và không nhầm null hoặc aspects rỗng với không có thay đổi. Vị trí là của Điều; bản đầu không bắt buộc nhúng trình xem file.

### 8.3. Đánh giá

- Mục tiêu: Change F1 ≥ 0,90 và Critical Change Recall ≥ 0,95 theo SRS. Đây là mục tiêu cần kiểm chứng bằng thực nghiệm.
- Đối chiếu từng SemanticChange một-một, không đếm trùng hoặc tính mỗi ChangeAspect thành một thay đổi độc lập; lỗi bỏ sót từ Reader/Parser/Aligner vẫn được tính đầu-cuối.
- Quy tắc matching xử lý thiếu/sai khía cạnh phải cố định trước đánh giá. Không tính đúng chỉ vì trùng field_group; ghi riêng lỗi nhóm, nội dung trước/sau, diễn giải và bằng chứng, kèm số mẫu từng nhóm.
- Kiểm tra chất lượng giải thích và khả năng hiểu báo cáo theo SRS mục 4; F1/Critical Change Recall không thay thế đánh giá này. Evaluation Plan chốt người tham gia, quy mô, cách chấm và ngưỡng trước thử nghiệm; ghi giới hạn khi nhóm tự đóng vai người dùng. Hoạt động này nằm ngoài luồng so sánh, không thêm module phản hồi.
- Không tính kết quả chưa xác định là đúng; mẫu số bằng 0 trả null và lý do.
- Báo số mẫu, số thay đổi CRITICAL, các lỗi và giới hạn của tập đánh giá.
- Lưu commit, dependency, mô hình, cấu hình, dữ liệu, môi trường và lệnh chạy.
- Nếu chưa đạt mục tiêu, báo số liệu thật và phân tích nguyên nhân; không sửa test/tiêu chí sau khi xem kết quả để tuyên bố đạt.

## 9. Quy trình làm việc và bàn giao

1. Issue có phạm vi, người thực hiện, người kiểm tra, estimate và acceptance criteria.
2. Thành viên phát triển trên branch riêng; dùng fixture đúng contract để làm song song.
3. PR ghi thay đổi, cách test, bằng chứng và giới hạn.
4. Reviewer kiểm tra code/contract; người kiểm thử chạy trên commit được ghi rõ.
5. Sửa và kiểm tra lại các lỗi; merge khi review và kiểm tra bắt buộc đạt.
6. Kiểm tra tích hợp sau merge trước khi đóng task tích hợp.

Một module hoàn thành khi có mã nguồn, input/output mẫu, test phù hợp, hướng dẫn chạy và giới hạn đã biết; đầu ra được người kiểm tra chéo xác nhận. Một tính năng đầu-cuối hoàn thành khi người dùng thực hiện được thao tác và nhận đúng báo cáo/lỗi theo hợp đồng.

Các tài liệu bổ sung theo tiến trình: mẫu bug report trước tuần 7; ghi chép thử nghiệm từ tuần 8; báo cáo kiểm thử tích hợp tuần 9–10; evaluation report tuần 11; hướng dẫn demo, báo cáo cuối kỳ và slide tuần 12; bộ hồ sơ bàn giao chính thức tuần 13.

## 10. Cập nhật kế hoạch sau cuộc họp

| Loại thay đổi | Nơi cập nhật chính | Kiểm tra ảnh hưởng |
| --- | --- | --- |
| Thư viện/framework/mô hình | Bảng công nghệ mục 3 | Dependency, module liên quan, hướng dẫn chạy, test và đo lại |
| Phân công | Mục 4 và người sở hữu task mục 7 | Bàn giao công việc và tải của thành viên |
| Mốc thời gian | Thời gian đầu tài liệu, giai đoạn mục 1, mục 6, mốc task mục 7 và lịch tài liệu mục 9 | Phụ thuộc và đầu ra tuần kế tiếp |
| Tham số vận hành | Cấu hình và mục 3.2 | API contract, hướng dẫn chạy và kiểm thử giới hạn |
| Phạm vi hoặc schema/API | BRD/SRS/architecture/API contract trước, sau đó kế hoạch | Mọi module, fixture và test tiêu thụ hợp đồng bị đổi |
| Cách đánh giá | Evaluation plan và mục 8 | Tính so sánh của kết quả; cố định lại trước đánh giá độc lập |

Đổi công nghệ trong cùng ranh giới module không nhất thiết đổi toàn bộ tiến độ. Thay đổi input/output, phạm vi hoặc kiến trúc cần đánh giá lại các task phụ thuộc. Giữ lịch sử quyết định trong commit/PR và tăng phiên bản kế hoạch khi nội dung thay đổi.

## 11. Nguồn kỹ thuật tham khảo

- [FastAPI — Request Files](https://fastapi.tiangolo.com/tutorial/request-files/)
- [React — Build a React app from Scratch](https://react.dev/learn/build-a-react-app-from-scratch)
- [Vite — Getting Started](https://vite.dev/guide/)
- [PyMuPDF — Text extraction](https://pymupdf.readthedocs.io/en/latest/recipes-text.html)
- [python-docx — Documentation](https://python-docx.readthedocs.io/en/stable/)
- [Sentence Transformers — Mô hình được chọn](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)