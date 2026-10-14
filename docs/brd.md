# BRD — Hệ thống phân tích thay đổi văn bản pháp lý

**Dự án:** Legal Document Change Detection  
**Nhóm:** Group 4  
**Phiên bản tài liệu:** 1.1.0   
**Phạm vi phiên bản đầu:** Phân tích văn bản quy phạm pháp luật tiếng Việt ban đầu (V1) và văn bản sửa đổi (S), kèm tài liệu tham chiếu do người dùng cung cấp khi cần.

## 1. Mục đích tài liệu

BRD mô tả vấn đề nghiệp vụ, người sử dụng, giá trị mong đợi, phạm vi, yêu cầu nghiệp vụ và tiêu chí đánh giá của hệ thống. Tài liệu tập trung vào nhu cầu của luật sư, người làm công việc pháp chế và sinh viên luật.

BRD là căn cứ để nhóm xây dựng yêu cầu phần mềm trong SRS và lựa chọn thiết kế trong Architecture. Các cấu trúc dữ liệu, endpoint API, thư viện, mô hình và thuật toán được quy định trong các tài liệu kỹ thuật tương ứng.

Các nhu cầu người dùng và tiêu chí phân loại dưới đây là đề xuất của dự án, cần được rà soát qua trao đổi với giảng viên hoặc người có chuyên môn pháp luật. Tài liệu không khẳng định nhóm đã thực hiện khảo sát người dùng thực tế.

## 2. Bối cảnh và vấn đề nghiệp vụ

Khi nghiên cứu hoặc thực hiện công việc pháp lý, người dùng cần đối chiếu yêu cầu trong văn bản sửa đổi với nội dung tương ứng của văn bản ban đầu. Họ cần biết những quy định nào được thêm, xóa hoặc sửa; sự thay đổi có ảnh hưởng đến nội dung quy định hay chỉ là thay đổi cách diễn đạt; và những nội dung nào cần được kiểm tra trước.

Việc đọc và so sánh thủ công có thể gặp các khó khăn sau:

- Văn bản dài, nhiều Điều và nhiều nội dung tương tự, khiến người dùng dễ bỏ sót khác biệt nhỏ.
- Một thay đổi ngắn như từ phủ định, đối tượng áp dụng, thời hạn hoặc điều kiện có thể làm thay đổi đáng kể nội dung quy định.
- Thay đổi định dạng, cách diễn đạt hoặc đánh lại số Điều có thể tạo nhiều khác biệt bề mặt, làm mất thời gian rà soát.
- Chỉ liệt kê phần chữ thay đổi chưa đủ để người dùng hiểu nội dung pháp lý nào cần chú ý.
- Người dùng cần kiểm chứng kết quả bằng đoạn trích cũ, đoạn trích mới và vị trí trong tài liệu gốc.
- Một số thay đổi cần kiến thức hoặc văn bản liên quan ngoài hai tài liệu đầu vào để kết luận; hệ thống phải thể hiện sự chưa chắc chắn.

**Ví dụ giả định:** Nếu một quy định đổi thời hạn từ “30 ngày” thành “15 ngày”, người dùng cần nhận ra thời hạn đã giảm, xác định đúng đối tượng và hoạt động chịu thời hạn đó từ đó suy ra được kết luận ví dụ như:"độ nghiêm trọng của vấn đề có thể đã được đánh giá lại" đồng thời kiểm tra đoạn quy định gốc. Nếu hệ thống chỉ đánh dấu hai con số khác nhau thì chưa đáp ứng đầy đủ nhu cầu nghiệp vụ.

Hệ thống được xây dựng để hỗ trợ tìm kiếm, đối chiếu và ưu tiên rà soát các thay đổi. Người dùng tiếp tục chịu trách nhiệm kiểm tra văn bản nguồn và đưa ra kết luận cho công việc của mình.

## 3. Người dùng và các bên liên quan

### 3.1. Luật sư và người làm pháp chế — nhóm sử dụng ưu tiên

**Công việc cần hỗ trợ:** Rà soát sự thay đổi của quy định trước khi cập nhật tài liệu nghiên cứu, quy trình nội bộ hoặc chuẩn bị nội dung tư vấn.

**Nhu cầu cụ thể:**

1. Tìm nhanh các Điều được thêm, xóa hoặc sửa được nêu trong văn bản sửa đổi.
2. Nhận biết thay đổi về chủ thể, phạm vi áp dụng, quyền, nghĩa vụ, điều kiện, thủ tục, thời hạn và chế tài khi nội dung đó thể hiện trong văn bản gốc, văn bản sửa đổi và tài liệu tham chiếu được cung cấp.
3. Đọc nội dung cũ và mới cạnh nhau để xác minh nhận định của hệ thống.
4. Có lý do cho việc phân loại và mức độ ưu tiên rà soát.
5. Biết những trường hợp liên kết yêu cầu sửa đổi hoặc diễn giải thay đổi còn chưa chắc chắn.
6. Biết phần nào chưa được xử lý, tránh hiểu nhầm báo cáo đã bao phủ toàn bộ tài liệu.

**Giá trị mong đợi:** Giảm công sức tìm khác biệt và giúp tập trung vào thay đổi đáng chú ý. Mức độ tiết kiệm thời gian cần được đo bằng thử nghiệm, không được mặc định coi là đã đạt.

### 3.2. Sinh viên luật và người nghiên cứu — nhóm sử dụng bổ sung

**Công việc cần hỗ trợ:** Học và nghiên cứu sự thay đổi của quy định thông qua đối chiếu văn bản gốc với nội dung sửa đổi.

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
| BG-01 | Hỗ trợ tìm khác biệt nhanh hơn | Người dùng nhận được danh sách Điều thêm, xóa hoặc sửa thay vì tự tìm từng khác biệt từ đầu. |
| BG-02 | Hỗ trợ nhận biết thay đổi nội dung quy định | Báo cáo mô tả nội dung thay đổi và phân biệt với khác biệt về cách diễn đạt khi có đủ căn cứ. |
| BG-03 | Hỗ trợ ưu tiên rà soát | Những thay đổi được đánh giá quan trọng có mức độ và lý do để người dùng xem trước. |
| BG-04 | Cho phép kiểm chứng | Người dùng đối chiếu được nhận định với nội dung cũ, mới và vị trí nguồn. |
| BG-05 | Hỗ trợ học tập và nghiên cứu | Sinh viên có thể giải thích thay đổi bằng bằng chứng, thay vì chỉ đọc một nhãn kết luận. |
| BG-06 | Thể hiện giới hạn rõ ràng | Báo cáo chỉ rõ nội dung cần kiểm tra, phần chưa xử lý và lỗi ảnh hưởng đến kết quả. |

## 5. Phạm vi nghiệp vụ

### 5.1. Đầu vào

- Hai tài liệu chính: văn bản ban đầu (V1) và văn bản sửa đổi (S) có nội dung tác động đến V1. S không phải bản đầy đủ sau sửa đổi (V2).
- DOCX là định dạng chính; hỗ trợ PDF có lớp văn bản đọc được. Không hỗ trợ PDF scan/ảnh.
- Người dùng cung cấp tài liệu tham chiếu bổ sung khi việc phân tích cần nội dung ngoài V1 và S; có thể tải ngay từ đầu hoặc bổ sung theo yêu cầu cụ thể của hệ thống.
- Người dùng chịu trách nhiệm chọn đúng văn bản gốc, văn bản sửa đổi, phiên bản tài liệu tham chiếu và kiểm tra nguồn tài liệu.
- Hệ thống kiểm tra khả năng đọc và sự phù hợp của tài liệu với nội dung được dẫn chiếu trong giới hạn hỗ trợ; không mặc định xác minh được tính chính thức, tính đầy đủ hoặc hiệu lực pháp lý thực tế.

### 5.2. Đơn vị đối chiếu

Đơn vị phân tích là từng yêu cầu sửa đổi, bổ sung hoặc bãi bỏ trong S, liên kết với đúng văn bản và Điều/Khoản/Điểm hoặc cụm từ bị tác động trong V1. Số Điều trong S không phải số Điều đích trong V1.

Một Điều của S có thể chứa nhiều yêu cầu; một Điều của V1 có thể chịu nhiều thay đổi. Không ghép toàn bộ hai văn bản theo quy tắc một–một và không xem phần V1 không được nhắc đến trong S là bị xóa.

Phân tích tập trung vào phần thay đổi, sử dụng thông tin tổng quát của V1 về phạm vi, đối tượng và mục đích điều chỉnh cùng ngữ cảnh liên quan như định nghĩa, điều kiện, ngoại lệ. Không bắt buộc dựng V2 đầy đủ hoặc phân tích ngữ nghĩa từng đoạn không thay đổi.

### 5.3. Đầu ra

- Danh sách yêu cầu sửa đổi, bổ sung, bãi bỏ và vị trí bị tác động trong V1.
- Nội dung trước thay đổi, nội dung hoặc chỉ dẫn sửa đổi trong S và phần chữ khác biệt khi xác định được.
- Nhận định về thay đổi nội dung quy định, nhóm nội dung thay đổi, mức độ và lý do khi có đủ căn cứ.
- Bằng chứng và vị trí nguồn trong V1, S và tài liệu tham chiếu được sử dụng.
- Thông tin hiệu lực và chuyển tiếp được nêu trong S, kèm phạm vi áp dụng và căn cứ; phần chưa xác định phải được đánh dấu.
- Danh sách tài liệu/nội dung tham chiếu còn thiếu, cảnh báo và lỗi xử lý.

### 5.4. Phạm vi bao phủ

Hệ thống xử lý những yêu cầu trong S tác động đến V1 được chọn, cùng thông tin hiệu lực và chuyển tiếp liên quan. Yêu cầu sửa văn bản khác phải được phân biệt và ghi rõ nằm ngoài đối tượng phân tích.

Phần mở đầu, chữ ký và phụ lục không được so sánh toàn diện trong phiên bản đầu. Nội dung đọc được ở các phần này, bao gồm bảng được dẫn chiếu, có thể làm ngữ cảnh hoặc bằng chứng. Nội dung không xử lý được phải được báo rõ; không mặc định suy ra toàn bộ văn bản không thay đổi.

## 6. Tình huống sử dụng

### 6.1. UC-01 — Luật sư rà soát văn bản sửa đổi

**Mục đích:** Xác định các thay đổi cần chú ý trước khi tiếp tục nghiên cứu hoặc cập nhật công việc pháp lý.

**Điều kiện:** Người dùng có V1 và S phù hợp, đọc được.

**Luồng chính:**

1. Người dùng chọn văn bản gốc V1, văn bản sửa đổi S và tài liệu tham chiếu nếu có.
2. Hệ thống kiểm tra đầu vào, trích yêu cầu sửa đổi trong S và liên kết với nội dung V1.
3. Hệ thống trả báo cáo về Điều thêm, xóa, sửa và các phần chưa chắc chắn.
4. Người dùng xem các thay đổi có mức độ ưu tiên cao hoặc cần kiểm tra.
5. Người dùng đọc nội dung cũ, mới, bằng chứng và lý do của từng nhận định.
6. Người dùng xác minh với tài liệu gốc và tiếp tục đánh giá theo bối cảnh công việc.

**Kết quả mong đợi:** Người dùng tìm được thay đổi liên quan và có đủ thông tin để kiểm tra trước khi sử dụng nhận định.

**Ngoại lệ:** Nếu một phần xử lý thất bại, báo cáo phải nêu rõ phần bị ảnh hưởng. Nếu không thể tạo kết quả có ích, hệ thống thông báo thất bại và lý do; không trả một danh sách rỗng như kết luận không có thay đổi.

### 6.2. UC-02 — Sinh viên nghiên cứu sự thay đổi

**Mục đích:** Hiểu một quy định đã thay đổi như thế nào và học cách lập luận từ bằng chứng.

**Luồng chính:**

1. Sinh viên chọn V1 và S đúng phạm vi.
2. Hệ thống hiển thị yêu cầu sửa đổi cùng nội dung và vị trí bị tác động trong V1.
3. Sinh viên chọn một thay đổi và đọc nội dung trước, sau.
4. Sinh viên xem giải thích về đối tượng, quyền, nghĩa vụ, điều kiện hoặc thời hạn bị thay đổi, nếu hệ thống xác định được.
5. Sinh viên mở lại đoạn nguồn, kiểm tra nhận định và ghi nhận giới hạn cần nghiên cứu thêm.

**Kết quả mong đợi:** Sinh viên có thể mô tả thay đổi bằng lời của mình và chỉ ra bằng chứng. Việc ghi chú của sinh viên có thể thực hiện ngoài hệ thống; phiên bản đầu không bắt buộc có chức năng quản lý ghi chú.

### 6.3. UC-03 — Rà soát trường hợp chưa chắc chắn

**Mục đích:** Tránh sử dụng một kết luận thiếu căn cứ.

**Tình huống kích hoạt:** Vị trí đích chưa rõ, nội dung có dấu hiệu tách/gộp, hoặc thay đổi cần ngữ cảnh/tài liệu tham chiếu chưa có.

**Luồng chính:**

1. Hệ thống đánh dấu kết quả cần kiểm tra và ghi lý do.
2. Người dùng xem nội dung hai bên và vị trí nguồn.
3. Hệ thống chỉ rõ tài liệu và Điều/Khoản/bảng còn thiếu khi xác định được.
4. Người dùng có thể tải tài liệu bổ sung để phân tích lại. Nếu không bổ sung, kết quả đã xác định vẫn được hiển thị cùng giới hạn phân tích.

**Kết quả mong đợi:** Người dùng biết nhận định chưa được xác định chắc chắn. Phiên bản đầu không bắt buộc có giao diện sửa kết quả liên kết hoặc lưu xác nhận của người dùng.

## 7. Yêu cầu nghiệp vụ

Tất cả yêu cầu trong bảng là yêu cầu của phiên bản đầu trong phạm vi đã nêu. Mức độ tự động hóa thực tế phải được đánh giá bằng kiểm thử.

| Mã | Yêu cầu | Điều kiện đáp ứng từ góc nhìn người dùng |
| --- | --- | --- |
| BR-01 | Phân biệt vai trò tài liệu | Người dùng nhận diện rõ V1, S và tài liệu tham chiếu; S không được trình bày như bản V2 đầy đủ. |
| BR-02 | Liên kết yêu cầu sửa đổi với nội dung gốc | Báo cáo chỉ rõ văn bản và Điều/Khoản/Điểm bị tác động; liên kết chưa chắc chắn có cảnh báo. |
| BR-03 | Nhận biết thêm, xóa và sửa | Người dùng phân biệt được nội dung được bổ sung, bãi bỏ và sửa đổi. |
| BR-04 | Hiển thị khác biệt văn bản | Người dùng thấy đoạn chữ thay đổi trong tiêu đề hoặc nội dung, cùng ngữ cảnh của Điều. |
| BR-05 | Phân biệt thay đổi ý nghĩa và cách diễn đạt | Nhận định có lý do; thiếu căn cứ thì đánh dấu chưa chắc chắn, không suy ra không đổi nghĩa chỉ vì thiếu từ khóa. |
| BR-06 | Mô tả các nội dung quy định bị thay đổi | Khi có căn cứ trong đầu vào, báo cáo chỉ ra thay đổi liên quan đến chủ thể, phạm vi, quyền, nghĩa vụ, điều kiện, thủ tục, thời hạn hoặc chế tài. |
| BR-07 | Giữ bằng chứng và vị trí nguồn | Người dùng đọc được bằng chứng trong V1, chỉ dẫn sửa đổi trong S và tài liệu tham chiếu nếu sử dụng; phân biệt nội dung nguồn với nội dung sau sửa đổi được suy ra. |
| BR-08 | Phân loại mức độ và giải thích | Mức độ được gắn với từng thay đổi được nhận diện, có lý do và theo tiêu chí chung; không chỉ dựa vào số chữ đổi. |
| BR-09 | Biểu diễn nhiều thay đổi trong cùng Điều | Một Điều có thể có nhiều nhận định riêng; không ép toàn bộ nội dung thành một thay đổi duy nhất. |
| BR-10 | Thể hiện nhu cầu kiểm tra của con người | Cảnh báo cho biết điều gì chưa chắc chắn và vì sao; người dùng vẫn xem được bằng chứng có sẵn. |
| BR-11 | Thể hiện trạng thái và phạm vi xử lý | Người dùng phân biệt kết quả xử lý đầy đủ, một phần và thất bại, đồng thời biết phần bị ảnh hưởng. |
| BR-12 | Dùng ngôn ngữ dễ hiểu | Giải thích tập trung vào nội dung cũ/mới và tác động trực tiếp được suy ra từ các tài liệu được cung cấp; tránh kết luận rộng hơn bằng chứng. |
| BR-13 | Bảo vệ nội dung tài liệu đầu vào | Nội dung không được công khai hoặc ghi toàn văn vào log vận hành; việc xử lý tệp tạm tuân theo chính sách được mô tả trong tài liệu kỹ thuật. |
| BR-14 | Bổ sung tài liệu tham chiếu | Hệ thống chỉ rõ căn cứ còn thiếu; người dùng có thể tải bổ sung. Thiếu tài liệu chỉ giới hạn nhận định bị ảnh hưởng, không che mất kết quả khác. |
| BR-15 | Thể hiện hiệu lực và chuyển tiếp | Báo cáo giữ nội dung, phạm vi áp dụng và nguồn của thông tin hiệu lực/chuyển tiếp trong S; chưa đủ căn cứ thì không tự áp một thời điểm cho mọi thay đổi. |

## 8. Quy tắc nghiệp vụ

### 8.1. Thay đổi văn bản và thay đổi ý nghĩa

Khác biệt về ký tự chưa đồng nghĩa với thay đổi nội dung quy định. Ngược lại, thay đổi ít ký tự vẫn có thể ảnh hưởng đáng kể đến quyền, nghĩa vụ hoặc điều kiện.

- **Thay đổi cách diễn đạt:** Có khác biệt câu chữ nhưng nội dung quy định được đánh giá là không thay đổi, với căn cứ đủ để giải thích.
- **Thay đổi ý nghĩa:** Có thay đổi nội dung quy định thể hiện trong văn bản gốc, văn bản sửa đổi và tài liệu tham chiếu được cung cấp, chẳng hạn chủ thể, quyền, nghĩa vụ, điều kiện hoặc thời hạn.
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

Một thay đổi có thể liên quan nhiều nhóm. Nhóm nghiệp vụ ở đây cần được ánh xạ với các nhãn được chốt trong SRS và hướng dẫn gán nhãn; không yêu cầu mỗi câu hỏi trở thành một nhãn kỹ thuật riêng.

### 8.3. Mức độ nghiêm trọng

Mức độ hỗ trợ ưu tiên rà soát theo tiêu chí chung của dự án. Nó không tự xác định tác động đối với từng khách hàng hoặc vụ việc.

| Mức | Tiêu chí đề xuất |
| --- | --- |
| LOW | Khác biệt về cách diễn đạt hoặc hình thức được xác định không làm thay đổi nội dung quy định. |
| MEDIUM | Thay đổi nội dung quy định có phạm vi tác động tương đối hạn chế theo bộ tiêu chí và ví dụ đã thống nhất. |
| HIGH | Thay đổi đáng kể về chủ thể, quyền, nghĩa vụ, điều kiện, thủ tục, thời hạn hoặc chế tài, có căn cứ để ưu tiên rà soát. |
| CRITICAL | Thay đổi đáp ứng tiêu chí quan trọng nhất trong hướng dẫn gán nhãn: có bằng chứng cho thấy đảo chiều, loại bỏ hoặc thay đổi trọng yếu nội dung quy định và cần được rà soát ưu tiên cao nhất. |

Nhóm phải bổ sung ví dụ ranh giới giữa MEDIUM, HIGH và CRITICAL trong hướng dẫn gán nhãn trước khi dùng để đánh giá. Không được coi mọi thay đổi về thời hạn, quyền hoặc nghĩa vụ là CRITICAL. Nếu chưa đủ căn cứ để gán mức độ, để trạng thái chưa xác định và yêu cầu kiểm tra; không ép thành LOW.

**Quy tắc nhất quán:** Thay đổi chỉ được đánh dấu critical khi mức độ đã xác định là CRITICAL. Điều thêm hoặc xóa không tự động đồng nghĩa với CRITICAL. Cần xem xét nội dung và tiêu chí đã thống nhất.

### 8.4. Liên kết và bao phủ kết quả

- Mỗi yêu cầu sửa đổi liên quan đến V1 phải có kết quả hoặc lý do chưa xử lý; tránh bỏ sót và tính trùng.
- Liên kết dựa trên văn bản đích, Điều/Khoản/Điểm và nội dung; không ghép theo số Điều của S với số Điều của V1.
- Với tách/gộp hoặc vị trí đích mơ hồ, yêu cầu kiểm tra; không tự khẳng định thêm hoặc bãi bỏ chỉ vì không tìm thấy đoạn tương ứng.
- Không phân tích phần thay đổi tách rời ngữ cảnh giữ nguyên có ảnh hưởng đến cách hiểu.
- Khi chỉ một phần được xử lý, báo cáo chỉ rõ phần thiếu hoặc vấn đề gặp phải.

### 8.5. Kết luận không phát hiện thay đổi

Chỉ thông báo “Không tìm thấy yêu cầu sửa đổi đối với V1 trong S đã cung cấp” khi đã xử lý đầy đủ S trong phạm vi hỗ trợ, không còn nội dung chưa xác định và không tìm thấy yêu cầu liên quan. Kết luận này không khẳng định V1 chưa từng được sửa đổi bởi văn bản khác.

Có yêu cầu sửa đổi nhưng chưa xác định tác động thì vẫn phải hiển thị yêu cầu đó. Không dùng kết quả Text Diff rỗng, lỗi hoặc thiếu tài liệu làm căn cứ kết luận không có thay đổi.

### 8.6. Dẫn chiếu, hiệu lực và căn cứ phân tích

- Khi dẫn chiếu chuyển từ nội dung A sang B, phân biệt việc xác định đổi dẫn chiếu với việc xác định tác động thực chất. Phân tích tác động trước–sau cần nội dung A và B cùng ngữ cảnh áp dụng liên quan, nếu chưa có trong đầu vào.
- Người dùng cung cấp tài liệu còn thiếu; hệ thống không tự thu thập hoặc duy trì kho văn bản pháp luật. Chỉ kết luận trong phạm vi bằng chứng có sẵn.
- Ưu tiên dẫn chiếu trực tiếp liên quan đến thay đổi; nếu còn phụ thuộc chưa được giải quyết, ghi rõ giới hạn thay vì suy luận không có căn cứ.
- Thông tin hiệu lực và chuyển tiếp được trích từ S và gắn với thay đổi khi có căn cứ. Việc trích xuất không đồng nghĩa với xác minh hiệu lực pháp lý thực tế tại mọi thời điểm.

## 9. Yêu cầu đối với báo cáo và trải nghiệm sử dụng

Một báo cáo có ích cần trả lời được các câu hỏi sau:

1. Văn bản nào là V1, văn bản nào là S và tài liệu tham chiếu nào đã được sử dụng?
2. Những Điều nào thêm, xóa hoặc sửa?
3. Nội dung trước và sau khác nhau ở đâu?
4. Hệ thống nhận định nội dung quy định đã thay đổi như thế nào, dựa trên bằng chứng nào?
5. Tôi nên ưu tiên kiểm tra những thay đổi nào và vì sao?
6. Kết quả nào chưa chắc chắn hoặc chưa được xử lý đầy đủ?
7. Phạm vi nào nằm ngoài báo cáo?
8. Thông tin hiệu lực/chuyển tiếp nào liên quan và cần bổ sung tài liệu nào?

Kết quả cần hiển thị nội dung cũ/mới cạnh nhau hoặc theo cách đối chiếu rõ ràng; phần chữ thay đổi phải dễ nhận biết. Không chỉ dùng màu sắc để truyền đạt loại thay đổi, mức độ hoặc cảnh báo.

Tóm tắt báo cáo phải nhất quán với kết quả chi tiết. Không dùng tổng số Điều thay đổi thay thế cho tổng số thay đổi nội dung quy định mà không ghi rõ đơn vị đếm.

Phiên bản đầu không bắt buộc xuất báo cáo thành PDF/DOCX, quản lý tài khoản, lưu lịch sử hoặc cung cấp chức năng cộng tác.

## 10. Tiêu chí thành công và nghiệm thu

### 10.1. Mức độ đáp ứng công việc người dùng

Nhóm kiểm tra bằng các nhiệm vụ trên một bộ cặp tài liệu và đáp án tham chiếu đã rà soát:

| Đối tượng | Nhiệm vụ kiểm tra | Kết quả mong đợi |
| --- | --- | --- |
| Luật sư/pháp chế hoặc người đánh giá theo vai trò này | Tìm một thay đổi được yêu cầu và kiểm tra bằng chứng | Xác định đúng Điều và đọc được nội dung cũ/mới liên quan. |
| Luật sư/pháp chế hoặc người đánh giá theo vai trò này | Xem một thay đổi ưu tiên cao | Hiểu được mức độ và lý do; nhận ra trường hợp cần xác minh thêm. |
| Sinh viên hoặc người đánh giá theo vai trò này | Giải thích một thay đổi | Mô tả được nội dung trước/sau và chỉ ra bằng chứng, không chỉ lặp lại nhãn. |
| Cả hai nhóm | Đọc báo cáo có cảnh báo hoặc xử lý một phần | Nhận biết được giới hạn, không hiểu danh sách thiếu là kết luận không có thay đổi. |

Nhóm ghi nhận số nhiệm vụ hoàn thành đúng, thời gian thực hiện, lỗi diễn giải và phản hồi. Quy mô, người tham gia, phương pháp và ngưỡng chấp nhận của thử nghiệm được chốt trong Evaluation Plan. Nếu sử dụng thành viên nhóm đóng vai người dùng, báo cáo phải nêu rõ giới hạn này.

### 10.2. Mục tiêu chất lượng phát hiện

- **Change F1 ≥ 0,90:** Mục tiêu phát hiện các thay đổi có ý nghĩa theo đáp án tham chiếu.
- **Critical Change Recall ≥ 0,95:** Mục tiêu phát hiện các thay đổi được gán nhãn CRITICAL trong đáp án tham chiếu và đánh dấu critical đúng.

Đây là mục tiêu đánh giá, chưa phải kết quả đã chứng minh. Nhóm phải báo cáo kết quả thực tế và kết luận đạt hoặc chưa đạt.

### 10.3. Nguyên tắc đánh giá

- Có hướng dẫn gán nhãn, tiêu chí mức độ và quy trình xử lý bất đồng.
- Tách dữ liệu phát triển/validation khỏi tập test độc lập; không dùng tập test cuối để điều chỉnh thuật toán hoặc ngưỡng.
- Khóa dữ liệu test và quy tắc đối chiếu trước khi đánh giá cuối.
- Quy tắc đối chiếu thay đổi dự đoán với đáp án tham chiếu phải thống nhất, tránh tính trùng.
- Phải tính cả phát hiện sai và bỏ sót, kể cả thay đổi bị mất do đọc tài liệu, tách cấu trúc, trích yêu cầu sửa đổi hoặc liên kết sai.
- Kết quả chưa chắc chắn không tự được tính là phát hiện đúng. Cách xử lý phải theo SRS và Evaluation Plan.
- Khi không có mẫu phù hợp để tính một chỉ số, ghi không xác định và lý do, không tự ghi 100%.
- Báo cáo số cặp tài liệu, số thay đổi, số thay đổi CRITICAL, số trường hợp cần kiểm tra và các giới hạn dữ liệu.

### 10.4. Điều kiện nghiệm thu chức năng

1. Xử lý được các cặp DOCX/PDF text hợp lệ trong giới hạn công bố.
2. Báo cáo thể hiện được Điều thêm, xóa, sửa và bằng chứng đối chiếu.
3. Có ví dụ kiểm thử thay đổi chủ thể, quyền/nghĩa vụ, điều kiện hoặc thời hạn; có cả ví dụ thay đổi cách diễn đạt.
4. Có ví dụ sửa Khoản/Điểm, S sửa nhiều văn bản, liên kết mơ hồ, đủ/thiếu tài liệu dẫn chiếu và thông tin hiệu lực khác nhau để kiểm tra kết quả và cảnh báo.
5. Nhận định và mức độ có lý do; trường hợp thiếu căn cứ thể hiện chưa xác định.
6. Lỗi đầu vào hoặc xử lý một phần không bị trình bày như không có thay đổi.
7. Có báo cáo thực nghiệm, hướng dẫn sử dụng và giới hạn đã biết.

## 11. Ngoài phạm vi phiên bản đầu

- OCR hoặc xử lý PDF scan/ảnh không có lớp văn bản đọc được.
- So sánh hợp đồng, văn bản tiếng nước ngoài hoặc cặp văn bản không có quan hệ gốc–sửa đổi.
- Tự tái dựng phiên bản đầy đủ từ văn bản chỉ liệt kê nội dung sửa đổi, bổ sung.
- Tự động giải quyết đầy đủ mọi trường hợp tách/gộp hoặc yêu cầu sửa đổi không xác định được vị trí đích.
- So sánh toàn diện phần mở đầu, chữ ký và phụ lục; các phần đọc được vẫn có thể cung cấp ngữ cảnh hoặc bằng chứng liên quan.
- Tự tải, cập nhật hoặc duy trì kho văn bản pháp luật dùng chung.
- Tự xác minh hiệu lực, tính chính thức, tính xác thực hoặc tính đầy đủ của văn bản đầu vào.
- Tự xác định quy định áp dụng cho một vụ việc cụ thể.
- Suy luận toàn bộ tác động từ các văn bản được dẫn chiếu nhưng chưa được cung cấp.
- Cung cấp ý kiến tư vấn pháp lý cuối cùng hoặc bảo đảm không bỏ sót mọi thay đổi.
- Quản lý tài khoản, lịch sử so sánh, cơ sở dữ liệu nghiệp vụ hoặc chức năng cộng tác.

## 12. Giả định và phụ thuộc

1. Người dùng cung cấp đúng V1, S và tài liệu tham chiếu cần thiết trong phạm vi hỗ trợ.
2. Tài liệu có nội dung đọc được và cấu trúc đủ để nhận diện các Điều; mức độ hỗ trợ bố cục cụ thể được kiểm chứng qua bộ mẫu.
3. Nhóm có các cặp tài liệu có nguồn và quyền sử dụng phù hợp cho phát triển, gán nhãn và đánh giá.
4. Có tiêu chí phân loại được thống nhất; sự tham gia của người có chuyên môn pháp luật là nguồn lực cần tìm kiếm và xác nhận.
5. Giới hạn kích thước, độ dài, số Điều và thời gian xử lý được công bố theo thiết kế và số đo thực tế. BRD không tự đặt một cam kết hiệu năng chưa đo.
6. Người dùng đọc cảnh báo và kiểm chứng trước khi sử dụng kết quả vào công việc pháp lý.

## 13. Rủi ro và biện pháp xử lý

| Rủi ro | Ảnh hưởng nghiệp vụ | Biện pháp |
| --- | --- | --- |
| Chọn sai V1, S hoặc phiên bản tài liệu tham chiếu | Diễn giải nhầm thêm/xóa, hiểu sai chiều thay đổi | Hiển thị rõ vai trò của các tài liệu; hướng dẫn người dùng kiểm tra trước khi xử lý. |
| Nguồn không chính thức hoặc tài liệu thiếu | Báo cáo không phản ánh đúng nội dung cần nghiên cứu | Dữ liệu đánh giá có nguồn; người dùng kiểm tra đầu vào; không coi đọc thành công là xác minh pháp lý thành công. |
| Bố cục phức tạp, bảng hoặc nhiều trang | Mất chữ, đảo thứ tự, tách Điều sai | Kiểm thử tài liệu thực tế; giữ vị trí nguồn; báo lỗi hoặc giới hạn khi nhận diện được vấn đề. |
| Đánh lại số, tách/gộp hoặc liên kết sai vị trí đích | Nhận định sai về thêm/xóa hoặc sửa | Kiểm tra nhiều tín hiệu đối chiếu; cảnh báo mơ hồ; đưa các tình huống này vào bộ kiểm thử. |
| Thiếu định nghĩa hoặc ngữ cảnh dẫn chiếu | Giải thích vượt quá căn cứ | Chỉ rõ tài liệu/nội dung cần bổ sung; cho phép tải thêm; không khẳng định tác động chưa có bằng chứng. |
| Tiêu chí mức độ không thống nhất | Các thành viên gán nhãn khác nhau, chỉ số khó tin cậy | Hướng dẫn có ví dụ ranh giới; gán nhãn chéo; ghi nhận và giải quyết bất đồng. |
| Sai hoặc bỏ sót thay đổi | Người dùng bỏ qua nội dung quan trọng | Giữ bằng chứng, cảnh báo; đánh giá đầy đủ phát hiện sai/bỏ sót; báo cáo kết quả và giới hạn thực tế. |
| Ít dữ liệu hoặc ít mẫu CRITICAL | Khó kết luận chất lượng tổng quát | Công bố số mẫu và cách chọn; không diễn giải chỉ số trên tập nhỏ thành bảo đảm rộng. |
| Người dùng tin tuyệt đối vào kết quả | Sử dụng nhận định thiếu kiểm chứng | Nhắc rõ vai trò hỗ trợ, lý do và phần chưa xác định trong báo cáo. |
| Lộ nội dung tài liệu qua log hoặc tệp tạm | Ảnh hưởng tính riêng tư của dữ liệu | Không log toàn văn; kiểm soát truy cập và vòng đời tệp tạm theo thiết kế triển khai. |

## 14. Ví dụ nghiệp vụ để xây dựng bộ kiểm thử

**Toàn bộ ví dụ trong mục này là giả định, không trích dẫn quy định pháp luật hiện hành.** Nội dung cũ lấy từ V1; nội dung mới hoặc chỉ dẫn sửa đổi lấy từ S. Mức độ cụ thể chỉ được gán sau khi đối chiếu hướng dẫn gán nhãn đã chốt.

| Mã | Nội dung cũ → mới | Điều cần kiểm tra |
| --- | --- | --- |
| EX-01 | “Trong thời hạn 30 ngày” → “Trong thời hạn 15 ngày” | Nhận biết giảm thời hạn; xác định hoạt động và chủ thể liên quan từ ngữ cảnh; không chỉ báo thay số. |
| EX-02 | “Có thể cung cấp” → “Phải cung cấp” | Nhận biết khả năng chuyển từ lựa chọn sang nghĩa vụ; đọc đầy đủ điều kiện và ngoại lệ. |
| EX-03 | “Áp dụng đối với tổ chức” → “Áp dụng đối với tổ chức và cá nhân” | Nhận biết mở rộng đối tượng; giữ đúng bằng chứng. |
| EX-04 | Một câu được viết lại nhưng nội dung được người gán nhãn xác nhận tương đương | Phát hiện khác biệt chữ và giải thích căn cứ không đổi nội dung quy định. |
| EX-05 | Điều 5 cũ thành Điều 6 mới, nội dung giữ nguyên | Nhận diện chỉ dẫn đánh lại số trong S; không tự diễn giải thành bãi bỏ và bổ sung nội dung. |
| EX-06 | Một Điều cũ được phân thành hai Điều mới | Liên kết chỉ dẫn tách/gộp với Điều gốc; cảnh báo nếu chưa xác định đủ nội dung bị tác động. |
| EX-07 | Một đoạn không đọc được hoặc một giai đoạn xử lý bị lỗi | Báo phần bị ảnh hưởng; không kết luận toàn bộ không thay đổi. |
| EX-08 | Sửa một dẫn chiếu nhưng tài liệu được dẫn chiếu không có trong đầu vào | Chỉ ra thay đổi dẫn chiếu, yêu cầu tài liệu bổ sung và giới hạn kết luận; phân tích lại khi đủ nội dung trước/sau. |

## 15. Liên kết và thống nhất tài liệu

| Tài liệu | Trách nhiệm |
| --- | --- |
| BRD | Người dùng, nhu cầu, giá trị, phạm vi và quy tắc nghiệp vụ. |
| SRS | Cụ thể hóa yêu cầu chức năng, dữ liệu, trạng thái, ràng buộc và cách kiểm chứng. |
| Architecture | Thiết kế các module, luồng xử lý và các quyết định triển khai để đáp ứng SRS. |
| README | Giới thiệu dự án, phạm vi và trạng thái triển khai thực tế; chỉ dẫn đến tài liệu chi tiết. |
| Annotation Guideline và Evaluation Plan | Ví dụ phân loại, tiêu chí mức độ, đáp án tham chiếu, quy trình và cách tính chỉ số. |


