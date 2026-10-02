# BRD — Legal Document Change Detection

## 1. Vấn đề
- Khi một văn bản pháp lý/hợp đồng có phiên bản mới, người đọc phải tự so
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
- Văn bản quy phạm pháp luật (VBQPPL) Việt Nam (Luật, Nghị định, Thông tư, Quyết định)
- Văn bản tiếng Việt, cấu trúc theo "Điều" "Khoản"
- So sánh 2 phiên bản của 1 văn bản quy phạm pháp luật

## 6. Ngoài phạm vi
- Xử lý OCR văn bản scan/ảnh, tự động gom văn bản sửa đổi rải rác,
so sánh tài liệu phi cấu trúc ví dụ: PDF scan cần OCR, tư vấn pháp lý,
ngôn ngữ khác tiếng Việt

## 7. Giả định và rủi ro
-  Xáo trộn số thứ tự Điều/Khoản do bãi bỏ hoặc chèn mới,
Định dạng văn bản thực tế không đồng nhất (thiếu ngắt dòng, dùng ký tự lạ, lỗi gõ phím),
Văn bản pháp luật có dung lượng lớn (hàng trăm trang như Luật Đất đai, Bộ luật Dân sự), ...
ví dụ: dữ liệu có nhãn ít; điều khoản bị đánh số lại giữa hai bản