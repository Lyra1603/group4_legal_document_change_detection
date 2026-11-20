# BRD — Hệ thống phân tích thay đổi văn bản pháp lý

**Dự án:** Legal Document Change Detection
**Nhóm:** Group 4
**Phiên bản tài liệu:** 1.3.0
**Phạm vi phiên bản đầu:** Người dùng nộp một văn bản sửa đổi (S). Hệ thống truy xuất văn bản bị sửa và phân tích thay đổi trực tiếp, tác động gián tiếp trong kho văn bản quy phạm pháp luật tiếng Việt thuộc lĩnh vực dân sự.

**Trạng thái ngày 20/11/2026:** phạm vi chỉ S/kho dân sự là mục tiêu phát triển. Demo trên main sau PR #7 vẫn nhận V1 + S, chưa có truy xuất đích hoặc tác động gián tiếp thật. Tài liệu không xác nhận các chức năng này đã hoàn thành.

## 1. Mục đích tài liệu

BRD mô tả mục tiêu sản phẩm. Nền DOCX chuẩn bị merge hỗ trợ dạng sửa hẹp theo [common-baseline.md](common-baseline.md); thêm/bãi bỏ, nhiều đích, LightRAG/model thật và đánh giá chất lượng tiếp tục sau merge. Không coi demo đã hoàn thành toàn bộ BRD.

BRD mô tả vấn đề nghiệp vụ, người sử dụng, giá trị mong đợi, phạm vi, yêu cầu nghiệp vụ và tiêu chí đánh giá của hệ thống. Tài liệu tập trung vào nhu cầu của luật sư, người làm công việc pháp chế và sinh viên luật.

BRD là căn cứ để nhóm xây dựng yêu cầu phần mềm trong SRS và lựa chọn thiết kế trong Architecture. Các cấu trúc dữ liệu, endpoint API, thư viện, mô hình và thuật toán được quy định trong các tài liệu kỹ thuật tương ứng.

Các nhu cầu người dùng và tiêu chí phân loại dưới đây là đề xuất của dự án, cần được rà soát qua trao đổi với giảng viên hoặc người có chuyên môn pháp luật. Tài liệu không khẳng định nhóm đã thực hiện khảo sát người dùng thực tế.

## 2. Bối cảnh và vấn đề nghiệp vụ

Khi một văn bản sửa đổi (S) xuất hiện, người dùng cần biết văn bản và phiên bản nào bị sửa, quy định nào thay đổi, nội dung sau sửa đổi có ý nghĩa gì và những quy định nào trong các văn bản khác có thể chịu tác động.

Việc đọc và so sánh thủ công có thể gặp các khó khăn sau:

- Văn bản dài, nhiều Điều và nhiều nội dung tương tự, khiến người dùng dễ bỏ sót khác biệt nhỏ.
- Một thay đổi ngắn như từ phủ định, đối tượng áp dụng, thời hạn hoặc điều kiện có thể làm thay đổi đáng kể nội dung quy định.
- Thay đổi định dạng, cách diễn đạt hoặc đánh lại số Điều có thể tạo nhiều khác biệt bề mặt, làm mất thời gian rà soát.
- Chỉ liệt kê phần chữ thay đổi chưa đủ để người dùng hiểu nội dung pháp lý nào cần chú ý.
- Người dùng cần kiểm chứng kết quả bằng đoạn trích cũ, đoạn trích mới và vị trí trong tài liệu gốc.
- Một văn bản khác (B) có thể dựa vào quy định bị sửa dù S và văn bản bị sửa (V1) đều không nhắc tên B. Người dùng cần tìm được B và kiểm tra căn cứ của mối liên hệ.

**Ví dụ giả định:** S giảm một thời hạn trong V1 từ 30 ngày xuống 15 ngày. Người dùng cần xác định chủ thể, công việc và mốc tính thời hạn. Nếu một quy định của B dựa vào thời hạn này, người dùng cần biết điều khoản nào của B có thể chịu tác động và căn cứ nào cho thấy mối liên hệ.

Hệ thống được xây dựng để hỗ trợ tìm kiếm, đối chiếu và ưu tiên rà soát các thay đổi. Người dùng tiếp tục chịu trách nhiệm kiểm tra văn bản nguồn và đưa ra kết luận cho công việc của mình.

## 3. Người dùng và các bên liên quan

Sinh viên luật và người nghiên cứu là nhóm ưu tiên; luật sư và người làm pháp chế, gồm pháp vụ doanh nghiệp, là nhóm bổ sung. Khi trực tiếp gửi S, bổ sung tài liệu và xem báo cáo, họ cùng đóng vai trò actor chính của Use Case. Mức ưu tiên nhóm người dùng được ghi theo mục tiêu sản phẩm.

### 3.1. Luật sư và người làm pháp chế — nhóm sử dụng bổ sung

**Công việc cần hỗ trợ:** Rà soát sự thay đổi của quy định trước khi cập nhật tài liệu nghiên cứu, quy trình nội bộ hoặc chuẩn bị nội dung tư vấn.

**Nhu cầu cụ thể:**

1. Từ S, tìm văn bản, phiên bản và các điều, khoản, điểm bị sửa trong kho.
2. Nhận biết thay đổi về chủ thể, phạm vi áp dụng, quyền, nghĩa vụ, điều kiện, thủ tục, thời hạn và chế tài dựa trên văn bản gốc, văn bản sửa đổi và nguồn liên quan.
3. Đọc nội dung cũ và mới cạnh nhau để xác minh nhận định của hệ thống.
4. Có lý do cho việc phân loại và mức độ ưu tiên rà soát.
5. Biết những trường hợp liên kết yêu cầu sửa đổi hoặc diễn giải thay đổi còn chưa chắc chắn.
6. Biết phần nào chưa được xử lý và phạm vi kho đã được phân tích.
7. Tìm quy định trong văn bản khác có thể chịu tác động và kiểm tra căn cứ liên hệ với thay đổi trực tiếp.

**Giá trị mong đợi:** Giảm công sức tìm khác biệt và giúp tập trung vào thay đổi đáng chú ý. Mức độ tiết kiệm thời gian cần được đo bằng thử nghiệm, không được mặc định coi là đã đạt.

### 3.2. Sinh viên luật và người nghiên cứu — nhóm sử dụng ưu tiên

**Công việc cần hỗ trợ:** Từ S, học và nghiên cứu thay đổi qua nội dung trước–sau và các quy định liên quan.

**Nhu cầu cụ thể:**

1. Nhìn thấy phần thêm, xóa hoặc sửa một cách rõ ràng.
2. Hiểu vì sao một thay đổi có thể ảnh hưởng đến nội dung quy định.
3. Phân biệt thay đổi cách diễn đạt với thay đổi quyền, nghĩa vụ hoặc điều kiện áp dụng.
4. Có đoạn trích và vị trí nguồn để tự đọc lại, thảo luận và kiểm chứng.
5. Nhận biết giới hạn của kết quả, đặc biệt khi cần đọc định nghĩa, dẫn chiếu hoặc tài liệu khác.

**Giá trị mong đợi:** Hỗ trợ đọc có định hướng và hình thành nhận xét có căn cứ. Hệ thống không thay thế hoạt động học, đọc văn bản và phân tích của sinh viên.

### 3.3. Các bên liên quan khác

| Bên liên quan | Vai trò |
| --- | --- |
| Nhóm phát triển | Hiện thực yêu cầu, kiểm thử và ghi nhận giới hạn của hệ thống. |
| Giảng viên hướng dẫn | Góp ý phạm vi, cách đánh giá và mức độ phù hợp với mục tiêu môn học. |
| Người rà soát có chuyên môn pháp luật | Khi có điều kiện tham gia: góp ý ví dụ, hướng dẫn gán nhãn, tiêu chí mức độ và các trường hợp bất đồng. |
| Người gán nhãn và đánh giá | Lập đáp án tham chiếu theo hướng dẫn chung, đối chiếu kết quả và ghi nhận sai sót. |

Việc liệt kê vai trò không có nghĩa dự án đã tuyển được người tham gia tương ứng. Nhóm cần ghi nhận nguồn lực thực tế trong kế hoạch triển khai.

## 4. Mục tiêu nghiệp vụ

| Mã | Mục tiêu | Biểu hiện mong đợi |
| --- | --- | --- |
| BG-01 | Tự tìm văn bản và quy định bị sửa | Từ S, người dùng nhận được danh sách văn bản đích, phiên bản được dùng và quy định bị sửa trong phạm vi kho. |
| BG-02 | Hỗ trợ nhận biết thay đổi nội dung quy định | Báo cáo mô tả nội dung thay đổi và phân biệt với khác biệt về cách diễn đạt khi có đủ căn cứ. |
| BG-03 | Hỗ trợ ưu tiên rà soát | Những thay đổi được đánh giá quan trọng có mức độ và lý do để người dùng xem trước. |
| BG-04 | Cho phép kiểm chứng | Người dùng đối chiếu được nhận định với nội dung cũ, mới và vị trí nguồn. |
| BG-05 | Hỗ trợ học tập và nghiên cứu | Sinh viên có thể giải thích thay đổi bằng bằng chứng, thay vì chỉ đọc một nhãn kết luận. |
| BG-06 | Thể hiện giới hạn rõ ràng | Báo cáo chỉ rõ nội dung cần kiểm tra, phạm vi kho, phần chưa xử lý và lỗi ảnh hưởng đến kết quả. |
| BG-07 | Hỗ trợ rà soát tác động gián tiếp | Người dùng thấy văn bản và quy định có thể chịu tác động, thay đổi trực tiếp liên quan và căn cứ để kiểm chứng. |

## 5. Phạm vi nghiệp vụ

### 5.1. Đầu vào

- Người dùng nộp một văn bản sửa đổi (S). Có thể kèm bối cảnh hoặc vấn đề cần quan tâm.
- DOCX là định dạng chính. Hỗ trợ PDF có lớp văn bản đọc được.
- Hệ thống tự tìm một hoặc nhiều văn bản bị sửa, phiên bản làm căn cứ trước sửa đổi (V1) cho từng thay đổi và tài liệu liên quan trong kho đã chuẩn bị. S cung cấp chỉ dẫn sửa đổi, còn V1 cung cấp nội dung trước sửa đổi.
- Kho gồm văn bản quy phạm pháp luật tiếng Việt thuộc lĩnh vực dân sự do nhóm chuẩn bị. Danh mục văn bản, nguồn và các phiên bản được lập chỉ mục cần được chốt trong kế hoạch dữ liệu. Báo cáo nêu phần vượt phạm vi kho hoặc thiếu phiên bản; phiên bản đầu chưa tự tìm thêm trên Internet. Chọn V1 phải có căn cứ về phiên bản và thời điểm; khi mơ hồ giữ ứng viên, không tự chọn bản mới nhất.
- Khi thiếu V1 hoặc phần nguồn cần thiết sau truy xuất, hệ thống chỉ rõ văn bản, phiên bản và điều khoản cần bổ sung, rồi cho người dùng chọn “Bổ sung tài liệu” hoặc “Hiện tại không có tài liệu”.
- Nếu chưa thể bổ sung, hệ thống tiếp tục phân tích chỉ dẫn trong S và các nguồn hợp lệ sẵn có. Nhận định được gắn căn cứ và giới hạn tương ứng; nội dung trước sửa đổi chưa xác định được ghi rõ. Các đích khác vẫn giữ kết quả.
- Tài liệu trong lĩnh vực dân sự nhưng chưa có trong kho được xử lý như thiếu nguồn. Kiểm tra phạm vi hỗ trợ có căn cứ riêng; khi chưa chắc chắn, hệ thống yêu cầu làm rõ. Với S nhiều lĩnh vực, hệ thống ghi lý do bỏ qua từng đích ngoài phạm vi và tiếp tục phần dân sự đủ căn cứ.

### 5.2. Đơn vị đối chiếu

Đơn vị phân tích trực tiếp là từng yêu cầu sửa đổi, bổ sung hoặc bãi bỏ trong S, liên kết với phiên bản và Điều/Khoản/Điểm hoặc cụm từ đích. Số Điều trong S có thể khác số Điều đích. Đơn vị ghi nhận tác động gián tiếp là quy định có thể chịu tác động và thay đổi trực tiếp làm phát sinh nhận định đó.

Một Điều của S có thể chứa nhiều yêu cầu, tác động đến một hoặc nhiều văn bản. Một Điều của V1 có thể chịu nhiều thay đổi. Chỉ xác định bổ sung, sửa đổi hoặc bãi bỏ dựa trên chỉ dẫn và bằng chứng liên quan.

Hệ thống dựng nội dung sau sửa đổi ở cấp quy định bị tác động, dùng phạm vi, đối tượng, định nghĩa, điều kiện và ngoại lệ liên quan để diễn giải. Việc hợp nhất toàn văn nằm ngoài phạm vi phiên bản đầu.

### 5.3. Đầu ra

- Danh sách văn bản đích, phiên bản V1 được dùng và căn cứ xác định.
- Danh sách yêu cầu sửa đổi, bổ sung hoặc bãi bỏ, vị trí đích, nội dung trước–sau và phần chữ khác biệt khi xác định được.
- Nhận định về thay đổi cách diễn đạt hoặc thay đổi ý nghĩa, nhóm nội dung, mức độ quan trọng và lý do theo tiêu chí áp dụng cho lĩnh vực dân sự.
- Danh sách quy định trong các văn bản khác có thể chịu tác động, thay đổi trực tiếp liên quan, giải thích tác động có thể xảy ra và căn cứ cho mối liên hệ.
- Trích dẫn nguồn, phân biệt nguyên văn với nội dung được dựng hoặc suy ra. Thể hiện thông tin hiệu lực, chuyển tiếp và phạm vi áp dụng khi có căn cứ.
- Phạm vi đã rà soát, phiên bản hoặc tài liệu còn thiếu, nhận định cần kiểm chứng và lỗi xử lý.

Có quan hệ với V1 không đồng nghĩa B chịu tác động; nhận định phải giải thích đúng phần quy định B phụ thuộc vào phần V1 bị sửa. Không tự kết luận B bị sửa hoặc hết hiệu lực. Một đích chưa xử lý được không làm mất kết quả hữu ích của các đích khác.

### 5.4. Phạm vi bao phủ

Hệ thống rà soát các văn bản S trực tiếp sửa và tìm tác động gián tiếp trên kho dân sự cùng nguồn bổ sung được kiểm tra hợp lệ. Với văn bản hoặc phiên bản đích ngoài kho, báo cáo nêu yêu cầu sửa đổi đã nhận diện và phần chưa phân tích được. Kết quả tác động gián tiếp phụ thuộc vào dữ liệu và căn cứ truy xuất được.

Phần mở đầu, chữ ký và phụ lục có thể cung cấp ngữ cảnh hoặc bằng chứng khi đọc được. Báo cáo nêu rõ phần liên quan chưa xử lý được.

## 6. Tình huống sử dụng

### 6.1. UC-01 — Luật sư rà soát văn bản sửa đổi

**Mục đích:** Xác định quy định thay đổi và các văn bản cần rà soát thêm.

1. Người dùng nộp S và có thể kèm bối cảnh.
2. Hệ thống đọc các yêu cầu sửa đổi, tìm văn bản đích và phiên bản V1 trong kho dân sự, rồi xác định vị trí bị sửa.
3. Hệ thống dựng nội dung trước–sau, phân tích ý nghĩa và mức độ quan trọng của thay đổi.
4. Hệ thống tìm quy định ở văn bản khác có thể chịu tác động và giải thích mối liên hệ bằng trích dẫn.
5. Người dùng xem các thay đổi ưu tiên, tác động có thể có, bằng chứng và phần cần rà soát thêm.

**Ngoại lệ:** Khi phiên bản chưa xác định được, tài liệu nằm ngoài kho hoặc một phần xử lý thất bại, báo cáo nêu rõ phần bị ảnh hưởng và hiển thị các kết quả còn đủ căn cứ.

### 6.2. UC-02 — Sinh viên nghiên cứu sự thay đổi

**Mục đích:** Hiểu một quy định đã thay đổi như thế nào và học cách lập luận từ bằng chứng.

**Luồng chính:**

1. Sinh viên nộp S và có thể nêu bối cảnh nghiên cứu.
2. Hệ thống tự tìm V1 và hiển thị yêu cầu sửa đổi cùng vị trí bị tác động.
3. Sinh viên chọn một thay đổi và đọc nội dung trước, sau.
4. Sinh viên xem giải thích về đối tượng, quyền, nghĩa vụ, điều kiện hoặc thời hạn bị thay đổi, nếu hệ thống xác định được.
5. Sinh viên mở lại đoạn nguồn, kiểm tra nhận định và ghi nhận giới hạn cần nghiên cứu thêm.

**Kết quả mong đợi:** Sinh viên mô tả được thay đổi và kiểm chứng bằng chứng, kể cả căn cứ liên hệ với văn bản khác nếu được báo cáo.

### 6.3. UC-03 — Rà soát trường hợp chưa chắc chắn

**Mục đích:** Tránh sử dụng một kết luận thiếu căn cứ.

**Tình huống kích hoạt:** Có nhiều phiên bản V1 khả dĩ, thiếu văn bản hoặc vị trí đích, nội dung có dấu hiệu tách/gộp, hoặc căn cứ cho tác động gián tiếp chưa đủ.

**Luồng chính:**

1. Hệ thống đánh dấu kết quả cần kiểm tra và ghi lý do.
2. Người dùng xem nội dung hai bên và vị trí nguồn.
3. Hệ thống chỉ rõ tài liệu và Điều/Khoản/bảng còn thiếu khi xác định được.
4. Người dùng có thể bổ sung V1 hoặc nguồn còn thiếu. Hệ thống kiểm tra định dạng, phạm vi, định danh, phiên bản và quan hệ V1–S. Nếu V1 không khớp, hệ thống nêu dấu hiệu và yêu cầu thay file. Nếu người dùng chọn “Hiện tại không có tài liệu”, tiếp tục với S và nguồn sẵn có, hiển thị phần chưa xác định.
5. Bổ sung hoặc thay file tạo lượt phân tích mới trong cùng trải nghiệm trên UI, giữ báo cáo trước trong khi chờ. Lượt lỗi vẫn cho phép xem báo cáo trước.
6. Sau khi có báo cáo, người dùng có thể mở bằng chứng nhiều lần. “Kết thúc phiên” xóa trạng thái, báo cáo và lựa chọn đang giữ trên UI.

**Kết quả mong đợi:** Người dùng biết nhận định nào cần kiểm chứng, lý do và tài liệu có thể bổ sung.

### 6.4. Bao phủ nhiều đích và điều kiện hoàn tất

Hệ thống liệt kê các văn bản mà chỉ dẫn trong S xác định là đích sửa đổi, kèm phiên bản đã chọn hoặc ứng viên cần làm rõ. Báo cáo đếm riêng văn bản đích, yêu cầu sửa đổi và điều khoản đã có/thiếu nguồn. Ví dụ có 8 điều khoản đích nhưng mới có nguồn cho 3 điều khoản thì hiển thị danh sách 5 điều khoản còn thiếu. Bổ sung được phần nào thì phân tích lại phần đó cùng các nguồn cần thiết. Trường hợp nhiều phiên bản của cùng văn bản phải được giải quyết bằng căn cứ lựa chọn.

Hoàn tất Use Case xét theo kết quả đúng phạm vi, bằng chứng xem được và giới hạn được hiển thị. Người dùng có thể chọn dừng thay vì bổ sung nguồn; kết thúc tương tác theo yêu cầu của họ và giữ rõ phạm vi kết quả đã cung cấp. Nhận xét của người dùng là chức năng mở rộng. Trạng thái chạy và chất lượng đúng/sai được kiểm tra riêng khi nghiệm thu.

## 7. Yêu cầu nghiệp vụ

Tất cả yêu cầu trong bảng là yêu cầu của phiên bản đầu trong phạm vi đã nêu. Mức độ tự động hóa thực tế phải được đánh giá bằng kiểm thử.

| Mã | Yêu cầu | Điều kiện đáp ứng từ góc nhìn người dùng |
| --- | --- | --- |
| BR-01 | Tiếp nhận S và xác định văn bản đích | Người dùng có thể bắt đầu chỉ với S. Báo cáo phân biệt S, các phiên bản V1 được tìm thấy và tài liệu liên quan. |
| BR-02 | Liên kết yêu cầu sửa đổi với nội dung gốc | Báo cáo chỉ rõ văn bản, phiên bản và Điều/Khoản/Điểm bị tác động. Liên kết chưa chắc chắn có cảnh báo. |
| BR-03 | Nhận biết thêm, xóa và sửa | Người dùng phân biệt được nội dung được bổ sung, bãi bỏ và sửa đổi. |
| BR-04 | Hiển thị khác biệt văn bản | Người dùng thấy đoạn chữ thay đổi trong tiêu đề hoặc nội dung, cùng ngữ cảnh của Điều. |
| BR-05 | Phân biệt thay đổi ý nghĩa và cách diễn đạt | Nhận định có lý do; thiếu căn cứ thì đánh dấu chưa chắc chắn, không suy ra không đổi nghĩa chỉ vì thiếu từ khóa. |
| BR-06 | Mô tả nội dung quy định bị thay đổi | Khi có căn cứ, báo cáo chỉ ra thay đổi liên quan đến chủ thể, phạm vi, quyền, nghĩa vụ, điều kiện, thủ tục, thời hạn hoặc chế tài. |
| BR-07 | Giữ bằng chứng và vị trí nguồn | Người dùng đọc được bằng chứng trong V1, chỉ dẫn sửa đổi trong S và tài liệu tham chiếu nếu sử dụng; phân biệt nội dung nguồn với nội dung sau sửa đổi được suy ra. |
| BR-08 | Phân loại mức độ và giải thích | Mức độ được gắn với từng thay đổi, có lý do theo tiêu chí của lĩnh vực dân sự. |
| BR-09 | Biểu diễn nhiều thay đổi trong cùng Điều | Một Điều có thể có nhiều nhận định riêng; không ép toàn bộ nội dung thành một thay đổi duy nhất. |
| BR-10 | Thể hiện nhu cầu kiểm tra của con người | Cảnh báo cho biết điều gì chưa chắc chắn và vì sao; người dùng vẫn xem được bằng chứng có sẵn. |
| BR-11 | Thể hiện trạng thái và phạm vi xử lý | Người dùng phân biệt kết quả xử lý đầy đủ, một phần và thất bại, đồng thời biết phần bị ảnh hưởng. |
| BR-12 | Dùng ngôn ngữ dễ hiểu | Giải thích thay đổi trực tiếp và tác động có thể có bằng nội dung và căn cứ mà người dùng kiểm tra được. |
| BR-13 | Bảo vệ nội dung tài liệu đầu vào | Nội dung không được công khai hoặc ghi toàn văn vào log vận hành; việc xử lý tệp tạm tuân theo chính sách được mô tả trong tài liệu kỹ thuật. |
| BR-14 | Bổ sung tài liệu tham chiếu | Hệ thống chỉ rõ căn cứ còn thiếu; người dùng có thể tải bổ sung. Thiếu tài liệu chỉ giới hạn nhận định bị ảnh hưởng, không che mất kết quả khác. |
| BR-15 | Thể hiện hiệu lực và chuyển tiếp | Báo cáo giữ nội dung, phạm vi áp dụng và nguồn của thông tin hiệu lực/chuyển tiếp. Thời điểm chưa đủ căn cứ được đánh dấu. |
| BR-16 | Phát hiện tác động gián tiếp | Báo cáo chỉ rõ văn bản và quy định có thể chịu tác động, quy định bị sửa có liên quan, căn cứ nối hai quy định và tác động có thể xảy ra. B có thể được tìm thấy dù S và V1 không nhắc tên B. |
| BR-17 | Thể hiện phạm vi truy xuất | Người dùng biết những văn bản hoặc phiên bản nào chưa tìm được, phần vượt phạm vi kho dân sự và phần chưa đủ căn cứ. |

## 8. Quy tắc nghiệp vụ

### 8.1. Thay đổi văn bản và thay đổi ý nghĩa

Khác biệt về ký tự chưa đồng nghĩa với thay đổi nội dung quy định. Ngược lại, thay đổi ít ký tự vẫn có thể ảnh hưởng đáng kể đến quyền, nghĩa vụ hoặc điều kiện.

- **Thay đổi cách diễn đạt:** Có khác biệt câu chữ nhưng nội dung quy định được đánh giá là không thay đổi, với căn cứ đủ để giải thích.
- **Thay đổi ý nghĩa:** Có thay đổi nội dung quy định thể hiện qua nội dung trước–sau và nguồn liên quan, chẳng hạn chủ thể, quyền, nghĩa vụ, điều kiện hoặc thời hạn.
- **Chưa xác định:** Chưa đủ căn cứ để phân biệt hai trường hợp trên. Hệ thống phải ghi nhận nhu cầu kiểm tra thay vì mặc định là thay đổi cách diễn đạt.

### 8.2. Nhóm nội dung cần chú ý

| Nhóm | Câu hỏi nghiệp vụ khi đối chiếu |
| --- | --- |
| Chủ thể và phạm vi áp dụng | Quy định áp dụng cho ai, cho hoạt động hoặc trường hợp nào? Phạm vi có mở rộng hay thu hẹp không? |
| Quyền | Chủ thể có thêm, mất hoặc bị giới hạn quyền nào được thể hiện trong Điều? |
| Nghĩa vụ và hành vi bị cấm | Yêu cầu bắt buộc hoặc hành vi bị cấm có thay đổi không? |
| Điều kiện và ngoại lệ | Điều kiện thực hiện, miễn trừ hoặc ngoại lệ có được thêm, bỏ hoặc sửa không? |
| Thủ tục và thẩm quyền | Hồ sơ, trình tự, cơ quan hoặc chủ thể thực hiện có thay đổi không? |
| Thời hạn, số lượng và ngưỡng | Giá trị, đơn vị, thời điểm bắt đầu hoặc cách tính có thay đổi không? |
| Chế tài và trách nhiệm | Biện pháp xử lý hoặc trách nhiệm được mô tả có thay đổi không? |
| Dẫn chiếu và định nghĩa | Dẫn chiếu hoặc cách gọi có thay đổi và có cần đọc thêm ngữ cảnh không? |

Một thay đổi có thể liên quan nhiều nhóm. Nhóm cần cụ thể hóa các tiêu chí và ví dụ gán nhãn theo lĩnh vực dân sự, kể cả trường hợp chưa đủ căn cứ.

### 8.3. Mức độ nghiêm trọng

Mức độ giúp người dùng ưu tiên rà soát theo tiêu chí và ví dụ đã thống nhất cho lĩnh vực dân sự.

| Mức | Tiêu chí đề xuất |
| --- | --- |
| LOW | Khác biệt về cách diễn đạt hoặc hình thức được xác định không làm thay đổi nội dung quy định. |
| MEDIUM | Thay đổi nội dung quy định có phạm vi tác động tương đối hạn chế theo bộ tiêu chí và ví dụ đã thống nhất. |
| HIGH | Thay đổi đáng kể về chủ thể, quyền, nghĩa vụ, điều kiện, thủ tục, thời hạn hoặc chế tài, có căn cứ để ưu tiên rà soát. |
| CRITICAL | Thay đổi đáp ứng tiêu chí quan trọng nhất trong hướng dẫn gán nhãn: có bằng chứng cho thấy đảo chiều, loại bỏ hoặc thay đổi trọng yếu nội dung quy định và cần được rà soát ưu tiên cao nhất. |

Nhóm phải bổ sung ví dụ ranh giới giữa MEDIUM, HIGH và CRITICAL trong hướng dẫn gán nhãn trước khi dùng để đánh giá. Không được coi mọi thay đổi về thời hạn, quyền hoặc nghĩa vụ là CRITICAL. Nếu chưa đủ căn cứ để gán mức độ, để trạng thái chưa xác định và yêu cầu kiểm tra; không ép thành LOW.

**Quy tắc nhất quán:** Thay đổi chỉ được đánh dấu critical khi mức độ đã xác định là CRITICAL. Điều thêm hoặc xóa không tự động đồng nghĩa với CRITICAL. Cần xem xét nội dung và tiêu chí đã thống nhất.

### 8.4. Liên kết và bao phủ kết quả

- Mỗi yêu cầu sửa đổi đã nhận diện trong S có kết quả hoặc lý do chưa xử lý, kể cả khi liên quan nhiều văn bản đích.
- Liên kết dựa trên văn bản đích, Điều/Khoản/Điểm và nội dung; không ghép theo số Điều của S với số Điều của V1.
- Với tách/gộp hoặc vị trí đích mơ hồ, yêu cầu kiểm tra; không tự khẳng định thêm hoặc bãi bỏ chỉ vì không tìm thấy đoạn tương ứng.
- Không phân tích phần thay đổi tách rời ngữ cảnh giữ nguyên có ảnh hưởng đến cách hiểu.
- Khi chỉ một phần được xử lý, báo cáo chỉ rõ phần thiếu hoặc vấn đề gặp phải.

### 8.5. Kết luận không phát hiện thay đổi

Chỉ thông báo không tìm thấy yêu cầu sửa đổi thuộc phạm vi phân tích khi đã xử lý đầy đủ S trong giới hạn hỗ trợ và có đủ căn cứ để kết luận về phạm vi đó. Yêu cầu chưa xác định được văn bản đích hoặc tác động vẫn phải được hiển thị cùng lý do.

Với tác động gián tiếp, nếu quá trình rà soát chưa tìm thấy mối liên hệ đủ căn cứ, báo cáo nêu kết quả trong phạm vi kho đã rà soát và ghi rõ phần dữ liệu còn thiếu.

### 8.6. Dẫn chiếu, hiệu lực và căn cứ phân tích

- Ưu tiên truy xuất văn bản, phiên bản và quy định liên quan từ kho dân sự. Báo cáo nêu căn cứ chọn phiên bản trước sửa đổi, hoặc các khả năng còn mơ hồ khi chưa thể xác định.
- Khi S đổi dẫn chiếu, phân tích tác động thực chất dựa trên nội dung trước–sau của quy định được dẫn chiếu và ngữ cảnh áp dụng.
- Tìm và rà soát quy định trong B có thể dựa vào quy định đã thay đổi trong V1, kể cả khi S và V1 không nhắc tên B. Một dẫn chiếu hoặc nội dung tương tự là căn cứ để rà soát. Khi nêu tác động, báo cáo cần giải thích phần thay đổi có liên quan đến cách B sử dụng quy định đó như thế nào.
- Với mối liên hệ hoặc tác động chưa đủ căn cứ, báo cáo ghi rõ nội dung cần kiểm chứng và nguồn còn thiếu. Cách phát hiện và kiểm chứng các quan hệ gián tiếp là nội dung nghiên cứu cần hoàn thiện.
- Trích thông tin hiệu lực và chuyển tiếp từ S, gắn với từng thay đổi khi có căn cứ. Báo cáo nêu giới hạn về khả năng xác minh hiệu lực.

## 9. Yêu cầu đối với báo cáo và trải nghiệm sử dụng

Một báo cáo có ích cần trả lời được các câu hỏi sau:

1. S trực tiếp sửa văn bản nào, hệ thống dùng phiên bản nào và dựa vào căn cứ gì?
2. Những Điều nào thêm, xóa hoặc sửa?
3. Nội dung trước và sau khác nhau ở đâu?
4. Hệ thống nhận định nội dung quy định đã thay đổi như thế nào, dựa trên bằng chứng nào?
5. Tôi nên ưu tiên kiểm tra những thay đổi nào và vì sao?
6. Kết quả nào chưa chắc chắn hoặc chưa được xử lý đầy đủ?
7. Phạm vi nào nằm ngoài báo cáo?
8. Thông tin hiệu lực/chuyển tiếp nào liên quan và cần bổ sung tài liệu nào?
9. Văn bản nào khác có thể chịu tác động, điều khoản nào của B liên quan đến thay đổi nào trong V1 và bằng chứng là gì?

Kết quả cần hiển thị nội dung cũ/mới cạnh nhau hoặc theo cách đối chiếu rõ ràng; phần chữ thay đổi phải dễ nhận biết. Người làm UI chọn tô nền, chữ đậm hoặc đánh dấu kèm nhãn để thể hiện phần liên quan và hỗ trợ nhận biết ngoài màu sắc. Mỗi nhận định hiển thị đường căn cứ có thể kiểm chứng: căn cứ chọn V1 → điều khoản trước/sau → nhận định thay đổi → căn cứ liên hệ B khi có → kết luận và giới hạn. Với dữ liệu thiếu, hiển thị mắt xích chưa xác định.

Tóm tắt báo cáo phải nhất quán với kết quả chi tiết. Không dùng tổng số Điều thay đổi thay thế cho tổng số thay đổi nội dung quy định mà không ghi rõ đơn vị đếm.

Phiên bản đầu không bắt buộc xuất báo cáo thành PDF/DOCX, quản lý tài khoản, lưu lịch sử hoặc cung cấp chức năng cộng tác.

Người dùng có thể yêu cầu thử lại sau lỗi dịch vụ. Hệ thống dùng lại dữ liệu trung gian còn hợp lệ nếu còn lưu, hoặc tạo lượt phân tích mới với nguồn cần thiết nếu đã cleanup. Hủy chủ động trước khi có kết quả theo E6 tiếp tục là đề xuất; đưa vào bản đầu cần đặc tả hành vi dừng bước tiếp theo, tác vụ còn chạy và cleanup.

## 10. Tiêu chí thành công và nghiệm thu

### 10.1. Mức độ đáp ứng công việc người dùng

Nhóm kiểm tra trên bộ ca bắt đầu từ S và kho dân sự đã chuẩn bị. Đáp án tham chiếu ghi văn bản đích, phiên bản V1, thay đổi trực tiếp và các quan hệ gián tiếp đã được rà soát cho từng ca.

| Đối tượng | Nhiệm vụ kiểm tra | Kết quả mong đợi |
| --- | --- | --- |
| Luật sư/pháp chế hoặc người đánh giá theo vai trò này | Tìm một thay đổi được yêu cầu và kiểm tra bằng chứng | Xác định đúng Điều và đọc được nội dung cũ/mới liên quan. |
| Luật sư/pháp chế hoặc người đánh giá theo vai trò này | Xem một thay đổi ưu tiên cao | Hiểu được mức độ và lý do; nhận ra trường hợp cần xác minh thêm. |
| Sinh viên hoặc người đánh giá theo vai trò này | Giải thích một thay đổi | Mô tả được nội dung trước/sau và chỉ ra bằng chứng, không chỉ lặp lại nhãn. |
| Cả hai nhóm | Đọc báo cáo có cảnh báo hoặc xử lý một phần | Nhận biết được phạm vi kho, phần chưa xử lý và dữ liệu thiếu. |
| Người đánh giá | Nộp riêng S và kiểm tra một kết quả về B | Xác định đúng văn bản và phiên bản đích trong ca có đáp án, kiểm tra quy định của B, đường liên hệ với thay đổi trực tiếp và căn cứ. |

Nhóm ghi nhận số nhiệm vụ hoàn thành đúng, thời gian thực hiện, lỗi diễn giải và phản hồi. Quy mô, người tham gia, phương pháp và tiêu chí đánh giá của thử nghiệm được hoàn thiện trong test_evaluation_plan.md. Nếu sử dụng thành viên nhóm đóng vai người dùng, báo cáo phải nêu rõ giới hạn này.

### 10.2. Mục tiêu chất lượng phát hiện

- **Change F1 ≥ 90% (dự tính):** Mục tiêu phát hiện các thay đổi có ý nghĩa theo đáp án tham chiếu.
- **Critical Change Recall ≥ 95% (dự tính):** Mục tiêu phát hiện các thay đổi được gán nhãn CRITICAL trong đáp án tham chiếu và đánh dấu critical đúng.

Hai ngưỡng trên là mục tiêu dự tính cho phát hiện thay đổi trực tiếp. Đánh giá đầu cuối bắt đầu từ S và tính cả lỗi truy xuất làm mất thay đổi. Kế hoạch đánh giá cần bổ sung phép đo truy xuất đúng văn bản và phiên bản. Với tác động gián tiếp, cần đo phát hiện sai và bỏ sót trên các ca đã rà soát, đồng thời kiểm tra căn cứ và giải thích cho từng tác động. Ngưỡng nghiệm thu cho truy xuất và tác động gián tiếp còn cần xác nhận.

### 10.3. Nguyên tắc đánh giá

- Có hướng dẫn gán nhãn, tiêu chí mức độ và quy trình xử lý bất đồng.
- Tách dữ liệu phát triển/validation khỏi tập test độc lập; không dùng tập test cuối để điều chỉnh thuật toán hoặc ngưỡng.
- Khóa dữ liệu test và quy tắc đối chiếu trước khi đánh giá cuối.
- Đánh giá theo đáp án tham chiếu đã review, tính cả phát hiện sai và bỏ sót. Xem [kế hoạch kiểm thử](test_evaluation_plan.md) để tra cách đối chiếu và chia tập.
- Phải tính cả phát hiện sai và bỏ sót, kể cả thay đổi bị mất do đọc tài liệu, tách cấu trúc, trích yêu cầu sửa đổi hoặc liên kết sai.
- Kết quả chưa chắc chắn không tự được tính là phát hiện đúng. Cách xử lý phải theo SRS và test_evaluation_plan.md.
- Khi không có mẫu phù hợp để tính một chỉ số, ghi không xác định và lý do, không tự ghi 100%.
- Báo cáo số ca S, số văn bản và phiên bản đích, số thay đổi, số mẫu CRITICAL, số quan hệ gián tiếp đã rà soát và giới hạn dữ liệu.

### 10.4. Điều kiện nghiệm thu chức năng

1. Xử lý được S dạng DOCX hoặc PDF có lớp văn bản trong giới hạn công bố, với S là tài liệu bắt buộc duy nhất.
2. Tìm đúng văn bản đích, phiên bản V1 và Điều/Khoản/Điểm trong các ca nghiệm thu đã chọn. Có ca S sửa nhiều văn bản, thiếu phiên bản hoặc có đích ngoài kho.
3. Trình bày trước–sau, trích dẫn, loại thay đổi và lý do đánh giá mức độ. Có ca thay đổi ý nghĩa, thay đổi cách diễn đạt và hiệu lực/chuyển tiếp.
4. Có ca tìm đúng B dù S và V1 đều không nhắc tên B. Báo cáo chỉ rõ quy định của B, quy định V1 bị sửa, căn cứ liên hệ và tác động có thể xảy ra.
5. Có ca B có liên hệ nhưng thay đổi đang xét không ảnh hưởng đến quy định của B, và ca thiếu căn cứ để kết luận. Kiểm tra việc tránh kết luận sai và thể hiện sự chưa chắc chắn.
6. Báo cáo thể hiện phần đã xử lý và phần còn thiếu khi truy xuất hoặc phân tích chỉ thành công một phần.
7. Có báo cáo thực nghiệm, hướng dẫn sử dụng và phạm vi kho đã đánh giá.

## 11. Ngoài phạm vi phiên bản đầu

- OCR hoặc xử lý PDF scan/ảnh không có lớp văn bản đọc được.
- So sánh hợp đồng, văn bản tiếng nước ngoài hoặc cặp văn bản không có quan hệ gốc–sửa đổi.
- Tự tái dựng phiên bản đầy đủ từ văn bản chỉ liệt kê nội dung sửa đổi, bổ sung.
- Tự động giải quyết đầy đủ mọi trường hợp tách/gộp hoặc yêu cầu sửa đổi không xác định được vị trí đích.
- So sánh toàn diện phần mở đầu, chữ ký và phụ lục; các phần đọc được vẫn có thể cung cấp ngữ cảnh hoặc bằng chứng liên quan.
- Bao phủ toàn bộ pháp luật Việt Nam hoặc tự động thu thập, cập nhật và duy trì kho. Phiên bản đầu sử dụng kho dân sự do nhóm chuẩn bị.
- Tự xác minh hiệu lực, tính chính thức, tính xác thực hoặc tính đầy đủ của văn bản đầu vào.
- Tự xác định quy định áp dụng cho một vụ việc cụ thể.
- Bảo đảm phát hiện tất cả tác động gián tiếp ngoài phạm vi kho hoặc suy ra tác động khi thiếu nguồn cần thiết.
- Cung cấp ý kiến tư vấn pháp lý cuối cùng hoặc bảo đảm không bỏ sót mọi thay đổi.
- Quản lý tài khoản, lịch sử so sánh, cơ sở dữ liệu nghiệp vụ hoặc chức năng cộng tác.

## 12. Giả định và phụ thuộc

1. Người dùng cung cấp S đọc được. Nhóm chuẩn bị kho dân sự có nguồn, thông tin phiên bản và cấu trúc đủ để truy xuất đến quy định cần phân tích.
2. Tài liệu có nội dung đọc được và cấu trúc đủ để nhận diện các Điều; mức độ hỗ trợ bố cục cụ thể được kiểm chứng qua bộ mẫu.
3. Nhóm có dữ liệu phát triển và các ca đánh giá bắt đầu từ S, với đáp án tham chiếu cho văn bản đích, thay đổi trực tiếp và các quan hệ gián tiếp đã rà soát.
4. Nhóm cần thống nhất tiêu chí phân loại và mức độ theo lĩnh vực dân sự, đồng thời xác nhận nguồn lực chuyên môn để rà soát tiêu chí và các ca tác động gián tiếp.
5. Giới hạn kích thước, độ dài, số Điều và thời gian xử lý được công bố theo thiết kế và số đo thực tế. BRD không tự đặt một cam kết hiệu năng chưa đo.
6. Người dùng đọc cảnh báo và kiểm chứng trước khi sử dụng kết quả vào công việc pháp lý.

## 13. Rủi ro và biện pháp xử lý

| Rủi ro | Ảnh hưởng nghiệp vụ | Biện pháp |
| --- | --- | --- |
| Truy xuất sai V1 hoặc phiên bản | Đối chiếu sai nội dung trước–sau | Hiển thị căn cứ chọn phiên bản, cảnh báo khi mơ hồ và kiểm thử bằng các ca có nhiều phiên bản. |
| Nguồn thiếu hoặc kho dân sự chưa bao phủ đủ | Bỏ sót văn bản đích hoặc văn bản B | Ghi nhận nguồn, phạm vi kho, phần thiếu và ảnh hưởng đến kết quả. |
| Suy diễn quá mức từ dẫn chiếu hoặc nội dung tương tự | Báo sai tác động lên B | Kiểm tra phần quy định B thực sự sử dụng, trích dẫn nguồn và đánh dấu khi chưa đủ căn cứ. |
| Bố cục phức tạp, bảng hoặc nhiều trang | Mất chữ, đảo thứ tự, tách Điều sai | Kiểm thử tài liệu thực tế; giữ vị trí nguồn; báo lỗi hoặc giới hạn khi nhận diện được vấn đề. |
| Đánh lại số, tách/gộp hoặc liên kết sai vị trí đích | Nhận định sai về thêm/xóa hoặc sửa | Kiểm tra nhiều tín hiệu đối chiếu; cảnh báo mơ hồ; đưa các tình huống này vào bộ kiểm thử. |
| Thiếu định nghĩa hoặc ngữ cảnh dẫn chiếu | Giải thích vượt quá căn cứ | Chỉ rõ tài liệu/nội dung cần bổ sung; cho phép tải thêm; không khẳng định tác động chưa có bằng chứng. |
| Tiêu chí mức độ không thống nhất | Các thành viên gán nhãn khác nhau, chỉ số khó tin cậy | Hướng dẫn có ví dụ ranh giới; gán nhãn chéo; ghi nhận và giải quyết bất đồng. |
| Sai hoặc bỏ sót thay đổi | Người dùng bỏ qua nội dung quan trọng | Giữ bằng chứng, cảnh báo; đánh giá đầy đủ phát hiện sai/bỏ sót; báo cáo kết quả và giới hạn thực tế. |
| Ít dữ liệu hoặc ít mẫu CRITICAL | Khó kết luận chất lượng tổng quát | Công bố số mẫu và cách chọn; không diễn giải chỉ số trên tập nhỏ thành bảo đảm rộng. |
| Người dùng tin tuyệt đối vào kết quả | Sử dụng nhận định thiếu kiểm chứng | Nhắc rõ vai trò hỗ trợ, lý do và phần chưa xác định trong báo cáo. |
| Lộ nội dung tài liệu qua log hoặc tệp tạm | Ảnh hưởng tính riêng tư của dữ liệu | Không log toàn văn; kiểm soát truy cập và vòng đời tệp tạm theo thiết kế triển khai. |

## 14. Ví dụ nghiệp vụ

- Thời hạn đổi từ 30 xuống 15 ngày. Người dùng cần thấy công việc nào bị ảnh hưởng, mốc bắt đầu tính hạn và nguồn quy định.
- Cụm “có thể cung cấp” đổi thành “phải cung cấp”. Người dùng cần thấy sự thay đổi về nghĩa vụ và điều kiện hoặc ngoại lệ liên quan.
- B quy định một thủ tục dựa trên thời hạn tại điều khoản của V1. Nếu S sửa thời hạn đó, hệ thống cần tìm được B dù B không được nêu trong S hoặc V1, rồi giải thích phần thủ tục nào có thể cần rà soát và trích căn cứ.

Xem [các ca tham chiếu trong hướng dẫn gán nhãn](data-annotation-guide.md#72-các-ca-tham-chiếu) và [kế hoạch kiểm thử](test_evaluation_plan.md) để tra ví dụ và kỳ vọng chi tiết.

## 15. Liên kết và thống nhất tài liệu

Các tài liệu kỹ thuật cần được cập nhật theo phạm vi nghiệp vụ của phiên bản BRD này.

| Tài liệu | Trách nhiệm |
| --- | --- |
| BRD | Người dùng, mục tiêu, phạm vi dân sự, yêu cầu nghiệp vụ và tiêu chí nghiệm thu. |
| SRS | Yêu cầu có thể kiểm thử cho luồng bắt đầu từ S, truy xuất phiên bản, đối chiếu và phân tích tác động. |
| Architecture | Thiết kế luồng agent dùng LightRAG và kho tri thức để truy xuất, dùng LLM cùng bộ quy tắc lĩnh vực dân sự để phân tích. Cách tìm và kiểm chứng quan hệ gián tiếp cần được hoàn thiện qua nghiên cứu và thử nghiệm. |
| README | Phạm vi và trạng thái triển khai thực tế. |
| Hướng dẫn gán nhãn và kế hoạch đánh giá | Đáp án tham chiếu và cách đo chất lượng truy xuất, thay đổi trực tiếp và tác động gián tiếp. |
