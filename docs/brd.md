# BRD — Legal Document Change Detection

## 1. Vấn đề
- Khi một văn bản quy phạm pháp luật có phiên bản mới, người đọc phải tự so
sánh từng điều khoản, dễ bỏ sót thay đổi quan trọng (ví dụ thời hạn thanh
toán từ 30 ngày thành 15 ngày).

## 2. Người dùng
- Các nhóm pháp lý và tuân thủ doanh nghiệp; khối cơ quan nhà nước và nhà 
làm luật; khối dịch vụ pháp lý chuyên nghiệp; các nhóm nghiên cứu và đào 
tạo, ví dụ: chuyên viên pháp chế, luật sư, sinh viên luật,...

## 3. Mục tiêu
- Tự động tìm các điều khoản thay đổi giữa hai phiên bản, phân biệt thay
đổi thật sự với thay đổi văn phong, không chỉ phát hiện thay đổi về mặt
văn bản mà còn thay đổi về mặt ngữ nghĩa pháp lý và đánh dấu thay đổi quan trọng.

## 4. Chỉ số thành công
- Change Detection F1 >= 0.90
- Critical Change Recall >= 95%
(đo trên bộ dữ liệu có nhãn, tách riêng khỏi dữ liệu dùng để phát triển)

## 5. Trong phạm vi
- VBQPPL Việt Nam bằng tiếng Việt, có cấu trúc theo Điều.
- So sánh hai phiên bản đầy đủ của cùng một văn bản;
  người dùng xác định bản cũ và bản mới.
- Nhận file DOCX và PDF có lớp chữ.
- Bản đầu tiên ghép và so sánh ở cấp Điều, giữ nội dung
  Khoản/Điểm trong từng Điều.
- Phát hiện thay đổi chữ, phân tích đổi nghĩa và đánh giá
  mức độ theo bộ tiêu chí được nhóm thống nhất.
- Trả bằng chứng cũ/mới, giải thích và cảnh báo cần kiểm tra.

## 6. Ngoài phạm vi
- PDF scan/ảnh và OCR.
- Dựng phiên bản đầy đủ từ văn bản chỉ ghi nội dung sửa đổi.
- Tự động gom các văn bản sửa đổi rải rác.
- Hợp đồng, tài liệu phi cấu trúc và ngôn ngữ khác tiếng Việt.
- Tự động xử lý chắc chắn các trường hợp tách/gộp Điều;
  bản đầu chỉ cảnh báo để kiểm tra.
- Tư vấn pháp lý và lưu lịch sử so sánh trong bản đầu tiên.

## 7. Giả định và rủi ro
-  Xáo trộn số thứ tự Điều/Khoản do bãi bỏ hoặc chèn mới,
Định dạng văn bản thực tế không đồng nhất (thiếu ngắt dòng, dùng ký tự lạ, lỗi gõ phím),
Văn bản pháp luật có dung lượng lớn (hàng trăm trang như Luật Đất đai, Bộ luật Dân sự), ...
ví dụ: dữ liệu có nhãn ít; điều khoản bị đánh số lại giữa hai bản
