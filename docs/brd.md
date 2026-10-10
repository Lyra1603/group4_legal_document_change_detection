# BRD — Hệ thống phân tích thay đổi văn bản pháp lý

**Dự án:** Legal Document Change Detection  
**Nhóm:** Group 4  
**Trạng thái:** Bản chi tiết đề xuất để nhóm review và thống nhất với SRS, Architecture.  
**Phạm vi phiên bản đầu:** So sánh hai phiên bản đầy đủ của cùng một văn bản quy phạm pháp luật tiếng Việt.

## 1. Mục đích tài liệu

BRD mô tả vấn đề nghiệp vụ, người sử dụng, giá trị mong đợi, phạm vi, yêu cầu nghiệp vụ và tiêu chí đánh giá của hệ thống. Tài liệu tập trung vào nhu cầu của luật sư, người làm công việc pháp chế và sinh viên luật.

BRD là căn cứ để nhóm xây dựng yêu cầu phần mềm trong SRS và lựa chọn thiết kế trong Architecture. Các cấu trúc dữ liệu, endpoint API, thư viện, mô hình và thuật toán được quy định trong các tài liệu kỹ thuật tương ứng.

Các nhu cầu người dùng và tiêu chí phân loại dưới đây là đề xuất của dự án, cần được rà soát qua trao đổi với giảng viên hoặc người có chuyên môn pháp luật. Tài liệu không khẳng định nhóm đã thực hiện khảo sát người dùng thực tế.

## 2. Bối cảnh và vấn đề nghiệp vụ

Khi nghiên cứu hoặc thực hiện công việc pháp lý, người dùng cần đối chiếu nội dung giữa phiên bản cũ và phiên bản mới của một văn bản. Họ cần biết những quy định nào được thêm, xóa hoặc sửa; sự thay đổi có ảnh hưởng đến nội dung quy định hay chỉ là thay đổi cách diễn đạt; và những nội dung nào cần được kiểm tra trước.

Việc đọc và so sánh thủ công có thể gặp các khó khăn sau:

- Văn bản dài, nhiều Điều và nhiều nội dung tương tự, khiến người dùng dễ bỏ sót khác biệt nhỏ.
- Một thay đổi ngắn như từ phủ định, đối tượng áp dụng, thời hạn hoặc điều kiện có thể làm thay đổi đáng kể nội dung quy định.
- Thay đổi định dạng, cách diễn đạt hoặc đánh lại số Điều có thể tạo nhiều khác biệt bề mặt, làm mất thời gian rà soát.
- Chỉ liệt kê phần chữ thay đổi chưa đủ để người dùng hiểu nội dung pháp lý nào cần chú ý.
- Người dùng cần kiểm chứng kết quả bằng đoạn trích cũ, đoạn trích mới và vị trí trong tài liệu gốc.
- Một số thay đổi cần kiến thức hoặc văn bản liên quan ngoài hai tài liệu đầu vào để kết luận; hệ thống phải thể hiện sự chưa chắc chắn.

**Ví dụ giả định:** Nếu một quy định đổi thời hạn từ “30 ngày” thành “15 ngày”, người dùng cần nhận ra thời hạn đã giảm, xác định đúng đối tượng và hoạt động chịu thời hạn đó, đồng thời kiểm tra đoạn quy định gốc. Nếu hệ thống chỉ đánh dấu hai con số khác nhau thì chưa đáp ứng đầy đủ nhu cầu nghiệp vụ.

Hệ thống được xây dựng để hỗ trợ tìm kiếm, đối chiếu và ưu tiên rà soát các thay đổi. Người dùng tiếp tục chịu trách nhiệm kiểm tra văn bản nguồn và đưa ra kết luận cho công việc của mình.

## 3. Người dùng và các bên liên quan

### 3.1. Luật sư và người làm pháp chế — nhóm sử dụng ưu tiên

**Công việc cần hỗ trợ:** Rà soát sự thay đổi của quy định trước khi cập nhật tài liệu nghiên cứu, quy trình nội bộ hoặc chuẩn bị nội dung tư vấn.

**Nhu cầu cụ thể:**

1. Tìm nhanh các Điều được thêm, xóa hoặc sửa giữa hai phiên bản.
2. Nhận biết thay đổi về chủ thể, phạm vi áp dụng, quyền, nghĩa vụ, điều kiện, thủ tục, thời hạn và chế tài khi nội dung đó thể hiện trong hai phiên bản.
3. Đọc nội dung cũ và mới cạnh nhau để xác minh nhận định của hệ thống.
4. Có lý do cho việc phân loại và mức độ ưu tiên rà soát.
5. Biết những trường hợp ghép Điều hoặc diễn giải thay đổi còn chưa chắc chắn.
6. Biết phần nào chưa được xử lý, tránh hiểu nhầm báo cáo đã bao phủ toàn bộ tài liệu.

**Giá trị mong đợi:** Giảm công sức tìm khác biệt và giúp tập trung vào thay đổi đáng chú ý. Mức độ tiết kiệm thời gian cần được đo bằng thử nghiệm, không được mặc định coi là đã đạt.

### 3.2. Sinh viên luật và người nghiên cứu — nhóm sử dụng bổ sung

**Công việc cần hỗ trợ:** Học và nghiên cứu sự thay đổi của quy định thông qua đối chiếu hai phiên bản.

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

- Hai phiên bản đầy đủ của cùng một văn bản quy phạm pháp luật tiếng Việt, do người dùng lựa chọn làm phiên bản cũ và phiên bản mới.
- Định dạng được hỗ trợ: DOCX và PDF có lớp văn bản đọc được.
- Người dùng chịu trách nhiệm lựa chọn đúng cặp phiên bản, đúng thứ tự và kiểm tra nguồn tài liệu.
- Hệ thống kiểm tra khả năng đọc và xử lý đầu vào trong giới hạn công bố; không mặc định xác minh được tính chính thức, tính đầy đủ hoặc hiệu lực pháp lý của tài liệu.

### 5.2. Đơn vị đối chiếu

Trong phiên bản đầu, hệ thống phân tích và ghép tương ứng ở cấp **Điều**. Nội dung Khoản và Điểm nằm trong Điều được giữ lại để phục vụ phát hiện và diễn giải thay đổi; chưa cam kết ghép độc lập từng Khoản hoặc Điểm.

Hệ thống hỗ trợ ghép một–một, nhận biết Điều thêm và Điều xóa. Khi đánh lại số Điều hoặc nội dung thay đổi, việc ghép không được dựa duy nhất vào số Điều. Trường hợp ghép mơ hồ, tách hoặc gộp Điều được đánh dấu để người dùng kiểm tra.

### 5.3. Đầu ra

- Danh sách các cặp Điều tương ứng và Điều được thêm hoặc xóa.
- Phần văn bản khác biệt trong tiêu đề hoặc nội dung Điều.
- Nhận định về thay đổi nội dung quy định, nhóm nội dung thay đổi, mức độ và lý do khi có đủ căn cứ.
- Nội dung cũ, mới và vị trí nguồn phục vụ đối chiếu.
- Cảnh báo về kết quả chưa chắc chắn, phạm vi chưa xử lý hoặc lỗi xử lý.

### 5.4. Phạm vi bao phủ

Phần đối chiếu nghiệp vụ tập trung vào nội dung các Điều. Phần mở đầu, chữ ký và phụ lục nằm ngoài phạm vi so sánh của phiên bản đầu. Báo cáo phải nêu giới hạn này; không được diễn đạt rằng toàn bộ văn bản không thay đổi chỉ vì các Điều được xử lý không có khác biệt.

## 6. Tình huống sử dụng

### 6.1. UC-01 — Luật sư rà soát hai phiên bản

**Mục đích:** Xác định các thay đổi cần chú ý trước khi tiếp tục nghiên cứu hoặc cập nhật công việc pháp lý.

**Điều kiện:** Người dùng có hai phiên bản đầy đủ, đúng phạm vi và đọc được.

**Luồng chính:**

1. Người dùng chọn tài liệu cũ và tài liệu mới.
2. Hệ thống kiểm tra đầu vào và xử lý các Điều trong phạm vi hỗ trợ.
3. Hệ thống trả báo cáo về Điều thêm, xóa, sửa và các phần chưa chắc chắn.
4. Người dùng xem các thay đổi có mức độ ưu tiên cao hoặc cần kiểm tra.
5. Người dùng đọc nội dung cũ, mới, bằng chứng và lý do của từng nhận định.
6. Người dùng xác minh với tài liệu gốc và tiếp tục đánh giá theo bối cảnh công việc.

**Kết quả mong đợi:** Người dùng tìm được thay đổi liên quan và có đủ thông tin để kiểm tra trước khi sử dụng nhận định.

**Ngoại lệ:** Nếu một phần xử lý thất bại, báo cáo phải nêu rõ phần bị ảnh hưởng. Nếu không thể tạo kết quả có ích, hệ thống thông báo thất bại và lý do; không trả một danh sách rỗng như kết luận không có thay đổi.

### 6.2. UC-02 — Sinh viên nghiên cứu sự thay đổi

**Mục đích:** Hiểu một quy định đã thay đổi như thế nào và học cách lập luận từ bằng chứng.

**Luồng chính:**

1. Sinh viên chọn hai phiên bản đúng phạm vi.
2. Hệ thống hiển thị các Điều tương ứng cùng phần thêm, xóa hoặc sửa.
3. Sinh viên chọn một thay đổi và đọc nội dung trước, sau.
4. Sinh viên xem giải thích về đối tượng, quyền, nghĩa vụ, điều kiện hoặc thời hạn bị thay đổi, nếu hệ thống xác định được.
5. Sinh viên mở lại đoạn nguồn, kiểm tra nhận định và ghi nhận giới hạn cần nghiên cứu thêm.

**Kết quả mong đợi:** Sinh viên có thể mô tả thay đổi bằng lời của mình và chỉ ra bằng chứng. Việc ghi chú của sinh viên có thể thực hiện ngoài hệ thống; phiên bản đầu không bắt buộc có chức năng quản lý ghi chú.

### 6.3. UC-03 — Rà soát trường hợp chưa chắc chắn

**Mục đích:** Tránh sử dụng một kết luận thiếu căn cứ.

**Tình huống kích hoạt:** Ghép Điều mơ hồ, nội dung có dấu hiệu tách/gộp, hoặc thay đổi cần ngữ cảnh chưa có.

**Luồng chính:**

1. Hệ thống đánh dấu kết quả cần kiểm tra và ghi lý do.
2. Người dùng xem nội dung hai bên và vị trí nguồn.
3. Người dùng tự đối chiếu, đọc thêm tài liệu liên quan khi cần và đưa ra nhận xét ngoài hệ thống.

**Kết quả mong đợi:** Người dùng biết nhận định chưa được xác định chắc chắn. Phiên bản đầu không bắt buộc có giao diện sửa kết quả ghép hoặc lưu xác nhận của người dùng.

## 7. Yêu cầu nghiệp vụ

Tất cả yêu cầu trong bảng là yêu cầu của phiên bản đầu trong phạm vi đã nêu. Mức độ tự động hóa thực tế phải được đánh giá bằng kiểm thử.

| Mã | Yêu cầu | Điều kiện đáp ứng từ góc nhìn người dùng |
| --- | --- | --- |
| BR-01 | Phân biệt phiên bản cũ và mới | Người dùng biết rõ chiều so sánh; phần thêm và xóa không bị diễn giải ngược. |
| BR-02 | Đối chiếu Điều tương ứng | Báo cáo hiển thị cặp Điều để kiểm chứng; ghép chưa chắc chắn có cảnh báo. |
| BR-03 | Nhận biết thêm, xóa và sửa | Người dùng phân biệt được Điều mới, Điều bị loại bỏ và Điều có nội dung khác biệt. |
| BR-04 | Hiển thị khác biệt văn bản | Người dùng thấy đoạn chữ thay đổi trong tiêu đề hoặc nội dung, cùng ngữ cảnh của Điều. |
| BR-05 | Phân biệt thay đổi ý nghĩa và cách diễn đạt | Nhận định có lý do; thiếu căn cứ thì đánh dấu chưa chắc chắn, không suy ra không đổi nghĩa chỉ vì thiếu từ khóa. |
| BR-06 | Mô tả các nội dung quy định bị thay đổi | Khi có căn cứ trong đầu vào, báo cáo chỉ ra thay đổi liên quan đến chủ thể, phạm vi, quyền, nghĩa vụ, điều kiện, thủ tục, thời hạn hoặc chế tài. |
| BR-07 | Giữ bằng chứng và vị trí nguồn | Người dùng đọc được nội dung liên quan ở hai phiên bản và xác định được vị trí nguồn. Điều thêm/xóa chỉ có bằng chứng ở phiên bản tương ứng. |
| BR-08 | Phân loại mức độ và giải thích | Mức độ được gắn với từng thay đổi được nhận diện, có lý do và theo tiêu chí chung; không chỉ dựa vào số chữ đổi. |
| BR-09 | Biểu diễn nhiều thay đổi trong cùng Điều | Một Điều có thể có nhiều nhận định riêng; không ép toàn bộ nội dung thành một thay đổi duy nhất. |
| BR-10 | Thể hiện nhu cầu kiểm tra của con người | Cảnh báo cho biết điều gì chưa chắc chắn và vì sao; người dùng vẫn xem được bằng chứng có sẵn. |
| BR-11 | Thể hiện trạng thái và phạm vi xử lý | Người dùng phân biệt kết quả xử lý đầy đủ, một phần và thất bại, đồng thời biết phần bị ảnh hưởng. |
| BR-12 | Dùng ngôn ngữ dễ hiểu | Giải thích tập trung vào nội dung cũ/mới và tác động trực tiếp được suy ra từ hai đầu vào; tránh kết luận rộng hơn bằng chứng. |
| BR-13 | Bảo vệ nội dung tài liệu đầu vào | Nội dung không được công khai hoặc ghi toàn văn vào log vận hành; việc xử lý tệp tạm tuân theo chính sách được mô tả trong tài liệu kỹ thuật. |

## 8. Quy tắc nghiệp vụ

### 8.1. Thay đổi văn bản và thay đổi ý nghĩa

Khác biệt về ký tự chưa đồng nghĩa với thay đổi nội dung quy định. Ngược lại, thay đổi ít ký tự vẫn có thể ảnh hưởng đáng kể đến quyền, nghĩa vụ hoặc điều kiện.

- **Thay đổi cách diễn đạt:** Có khác biệt câu chữ nhưng nội dung quy định được đánh giá là không thay đổi, với căn cứ đủ để giải thích.
- **Thay đổi ý nghĩa:** Có thay đổi nội dung quy định thể hiện trong hai phiên bản, chẳng hạn chủ thể, quyền, nghĩa vụ, điều kiện hoặc thời hạn.
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

### 8.4. Ghép Điều và bao phủ kết quả

- Mỗi Điều trong phạm vi xử lý cần được thể hiện trong một cặp tương ứng hoặc trạng thái thêm/xóa, tránh mất nội dung hoặc tính trùng.
- Không coi hai Điều là tương ứng chỉ vì cùng số thứ tự.
- Với tách/gộp hoặc ghép mơ hồ, hệ thống thể hiện giới hạn của đối chiếu một–một và yêu cầu kiểm tra; không khẳng định đã xử lý chính xác toàn bộ cấu trúc đó.
- Khi chỉ một phần tài liệu được xử lý, báo cáo phải chỉ rõ phần thiếu hoặc vấn đề gặp phải theo thông tin có sẵn.

### 8.5. Kết luận không phát hiện thay đổi

Chỉ được thông báo không phát hiện khác biệt văn bản trong phạm vi hỗ trợ khi tất cả nội dung thuộc phạm vi đó đã được xử lý, không còn đối chiếu chưa chắc chắn và không có khác biệt văn bản.

Nếu có khác biệt câu chữ nhưng được đánh giá không đổi ý nghĩa, báo cáo phải thể hiện khác biệt đó và nhận định tương ứng. Nếu còn lỗi, phần chưa xử lý hoặc nhận định chưa chắc chắn, không được dùng kết luận chung “không có thay đổi”.

## 9. Yêu cầu đối với báo cáo và trải nghiệm sử dụng

Một báo cáo có ích cần trả lời được các câu hỏi sau:

1. Tôi đang so sánh những tài liệu nào, theo chiều cũ → mới nào?
2. Những Điều nào thêm, xóa hoặc sửa?
3. Nội dung trước và sau khác nhau ở đâu?
4. Hệ thống nhận định nội dung quy định đã thay đổi như thế nào, dựa trên bằng chứng nào?
5. Tôi nên ưu tiên kiểm tra những thay đổi nào và vì sao?
6. Kết quả nào chưa chắc chắn hoặc chưa được xử lý đầy đủ?
7. Phạm vi nào nằm ngoài báo cáo?

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
- Phải tính cả phát hiện sai và bỏ sót, kể cả thay đổi bị mất do đọc tài liệu, tách Điều hoặc ghép Điều sai.
- Kết quả chưa chắc chắn không tự được tính là phát hiện đúng. Cách xử lý phải theo SRS và Evaluation Plan.
- Khi không có mẫu phù hợp để tính một chỉ số, ghi không xác định và lý do, không tự ghi 100%.
- Báo cáo số cặp tài liệu, số thay đổi, số thay đổi CRITICAL, số trường hợp cần kiểm tra và các giới hạn dữ liệu.

### 10.4. Điều kiện nghiệm thu chức năng

1. Xử lý được các cặp DOCX/PDF text hợp lệ trong giới hạn công bố.
2. Báo cáo thể hiện được Điều thêm, xóa, sửa và bằng chứng đối chiếu.
3. Có ví dụ kiểm thử thay đổi chủ thể, quyền/nghĩa vụ, điều kiện hoặc thời hạn; có cả ví dụ thay đổi cách diễn đạt.
4. Có ví dụ đánh lại số Điều, ghép mơ hồ và tách/gộp để kiểm tra cảnh báo.
5. Nhận định và mức độ có lý do; trường hợp thiếu căn cứ thể hiện chưa xác định.
6. Lỗi đầu vào hoặc xử lý một phần không bị trình bày như không có thay đổi.
7. Có báo cáo thực nghiệm, hướng dẫn sử dụng và giới hạn đã biết.

## 11. Ngoài phạm vi phiên bản đầu

- OCR hoặc xử lý PDF scan/ảnh không có lớp văn bản đọc được.
- So sánh hợp đồng, văn bản tiếng nước ngoài hoặc hai văn bản độc lập không phải hai phiên bản của cùng một văn bản.
- Tự tái dựng phiên bản đầy đủ từ văn bản chỉ liệt kê nội dung sửa đổi, bổ sung.
- Ghép đầy đủ cấu trúc tách/gộp Điều hoặc ghép độc lập từng Khoản, Điểm.
- Phân tích thay đổi ở phần mở đầu, chữ ký và phụ lục.
- Tự tải hoặc cập nhật văn bản từ cơ sở dữ liệu pháp luật.
- Tự xác minh hiệu lực, tính chính thức, tính xác thực hoặc tính đầy đủ của văn bản đầu vào.
- Tự xác định quy định áp dụng cho một vụ việc cụ thể.
- Suy luận toàn bộ tác động từ các văn bản được dẫn chiếu nhưng không nằm trong hai đầu vào.
- Cung cấp ý kiến tư vấn pháp lý cuối cùng hoặc bảo đảm không bỏ sót mọi thay đổi.
- Quản lý tài khoản, lịch sử so sánh, cơ sở dữ liệu nghiệp vụ hoặc chức năng cộng tác.

## 12. Giả định và phụ thuộc

1. Người dùng cung cấp đúng hai phiên bản, đúng thứ tự và trong phạm vi hỗ trợ.
2. Tài liệu có nội dung đọc được và cấu trúc đủ để nhận diện các Điều; mức độ hỗ trợ bố cục cụ thể được kiểm chứng qua bộ mẫu.
3. Nhóm có các cặp tài liệu có nguồn và quyền sử dụng phù hợp cho phát triển, gán nhãn và đánh giá.
4. Có tiêu chí phân loại được thống nhất; sự tham gia của người có chuyên môn pháp luật là nguồn lực cần tìm kiếm và xác nhận.
5. Giới hạn kích thước, độ dài, số Điều và thời gian xử lý được công bố theo thiết kế và số đo thực tế. BRD không tự đặt một cam kết hiệu năng chưa đo.
6. Người dùng đọc cảnh báo và kiểm chứng trước khi sử dụng kết quả vào công việc pháp lý.

## 13. Rủi ro và biện pháp xử lý

| Rủi ro | Ảnh hưởng nghiệp vụ | Biện pháp |
| --- | --- | --- |
| Chọn sai phiên bản hoặc sai thứ tự | Diễn giải nhầm thêm/xóa, hiểu sai chiều thay đổi | Hiển thị rõ hai đầu vào và chiều so sánh; hướng dẫn người dùng kiểm tra trước khi xử lý. |
| Nguồn không chính thức hoặc tài liệu thiếu | Báo cáo không phản ánh đúng nội dung cần nghiên cứu | Dữ liệu đánh giá có nguồn; người dùng kiểm tra đầu vào; không coi đọc thành công là xác minh pháp lý thành công. |
| Bố cục phức tạp, bảng hoặc nhiều trang | Mất chữ, đảo thứ tự, tách Điều sai | Kiểm thử tài liệu thực tế; giữ vị trí nguồn; báo lỗi hoặc giới hạn khi nhận diện được vấn đề. |
| Đánh lại số, tách/gộp hoặc ghép sai Điều | Nhận định sai về thêm/xóa hoặc sửa | Kiểm tra nhiều tín hiệu đối chiếu; cảnh báo mơ hồ; đưa các tình huống này vào bộ kiểm thử. |
| Thiếu định nghĩa hoặc ngữ cảnh dẫn chiếu | Giải thích vượt quá căn cứ | Nêu nhu cầu đọc thêm; không khẳng định tác động chưa có bằng chứng. |
| Tiêu chí mức độ không thống nhất | Các thành viên gán nhãn khác nhau, chỉ số khó tin cậy | Hướng dẫn có ví dụ ranh giới; gán nhãn chéo; ghi nhận và giải quyết bất đồng. |
| Sai hoặc bỏ sót thay đổi | Người dùng bỏ qua nội dung quan trọng | Giữ bằng chứng, cảnh báo; đánh giá đầy đủ phát hiện sai/bỏ sót; báo cáo kết quả và giới hạn thực tế. |
| Ít dữ liệu hoặc ít mẫu CRITICAL | Khó kết luận chất lượng tổng quát | Công bố số mẫu và cách chọn; không diễn giải chỉ số trên tập nhỏ thành bảo đảm rộng. |
| Người dùng tin tuyệt đối vào kết quả | Sử dụng nhận định thiếu kiểm chứng | Nhắc rõ vai trò hỗ trợ, lý do và phần chưa xác định trong báo cáo. |
| Lộ nội dung tài liệu qua log hoặc tệp tạm | Ảnh hưởng tính riêng tư của dữ liệu | Không log toàn văn; kiểm soát truy cập và vòng đời tệp tạm theo thiết kế triển khai. |

## 14. Ví dụ nghiệp vụ để xây dựng bộ kiểm thử

**Toàn bộ ví dụ trong mục này là giả định, không trích dẫn quy định pháp luật hiện hành.** Mức độ cụ thể chỉ được gán sau khi đối chiếu hướng dẫn gán nhãn đã chốt.

| Mã | Nội dung cũ → mới | Điều cần kiểm tra |
| --- | --- | --- |
| EX-01 | “Trong thời hạn 30 ngày” → “Trong thời hạn 15 ngày” | Nhận biết giảm thời hạn; xác định hoạt động và chủ thể liên quan từ ngữ cảnh; không chỉ báo thay số. |
| EX-02 | “Có thể cung cấp” → “Phải cung cấp” | Nhận biết khả năng chuyển từ lựa chọn sang nghĩa vụ; đọc đầy đủ điều kiện và ngoại lệ. |
| EX-03 | “Áp dụng đối với tổ chức” → “Áp dụng đối với tổ chức và cá nhân” | Nhận biết mở rộng đối tượng; giữ đúng bằng chứng. |
| EX-04 | Một câu được viết lại nhưng nội dung được người gán nhãn xác nhận tương đương | Phát hiện khác biệt chữ và giải thích căn cứ không đổi nội dung quy định. |
| EX-05 | Điều 5 cũ thành Điều 6 mới, nội dung giữ nguyên | Không nhầm đánh lại số thành một Điều xóa và một Điều thêm khi có đủ căn cứ ghép. |
| EX-06 | Một Điều cũ được phân thành hai Điều mới | Cảnh báo giới hạn tách/gộp; không khẳng định kết quả ghép một–một đã bao phủ đúng toàn bộ. |
| EX-07 | Một đoạn không đọc được hoặc một giai đoạn xử lý bị lỗi | Báo phần bị ảnh hưởng; không kết luận toàn bộ không thay đổi. |
| EX-08 | Sửa một dẫn chiếu nhưng tài liệu được dẫn chiếu không có trong đầu vào | Chỉ ra thay đổi dẫn chiếu; ghi rõ chưa đủ căn cứ kết luận tác động rộng hơn. |

## 15. Liên kết và thống nhất tài liệu

| Tài liệu | Trách nhiệm |
| --- | --- |
| BRD | Người dùng, nhu cầu, giá trị, phạm vi và quy tắc nghiệp vụ. |
| SRS | Cụ thể hóa yêu cầu chức năng, dữ liệu, trạng thái, ràng buộc và cách kiểm chứng. |
| Architecture | Thiết kế các module, luồng xử lý và các quyết định triển khai để đáp ứng SRS. |
| README | Giới thiệu dự án, phạm vi và trạng thái triển khai thực tế; chỉ dẫn đến tài liệu chi tiết. |
| Annotation Guideline và Evaluation Plan | Ví dụ phân loại, tiêu chí mức độ, đáp án tham chiếu, quy trình và cách tính chỉ số. |

Khi cập nhật BRD, nhóm rà soát các điểm tương ứng trong SRS và Architecture, đặc biệt: hai phiên bản đầy đủ; DOCX/PDF text; cấp Điều; ghép một–một; bằng chứng và vị trí nguồn; nhiều thay đổi trong một Điều; mức độ chưa xác định; cảnh báo; trạng thái xử lý; và chỉ số đánh giá.

Việc thêm nhu cầu người dùng vào BRD không tự động mở rộng phạm vi kỹ thuật. Yêu cầu mới vượt phạm vi phải được nhóm thống nhất và cập nhật các tài liệu liên quan trước khi triển khai.
