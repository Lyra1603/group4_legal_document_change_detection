**Legal Document Change Detection**

- Vấn đề: Khi một văn bản pháp lý/hợp đồng có phiên bản mới, người đọc phải tự so
sánh từng điều khoản, dễ bỏ sót thay đổi quan trọng (ví dụ thời hạn thanh
toán từ 30 ngày thành 15 ngày).

- Mục tiêu: Tự động tìm các điều khoản thay đổi giữa hai phiên bản, phân biệt thay
đổi thật sự với thay đổi văn phong, không chỉ phát hiện thay đổi về mặt
văn bản mà còn thay đổi về mặt ngữ nghĩa pháp lý và đánh dấu thay đổi quan trọng.

Cách chạy:
```
pip install -r requirements.txt 
python src/pipeline.py              # chạy ví dụ mẫu 
uvicorn backend.main:app --reload   # chạy API từ thư mục gốc 
```
- Đọc tài liệu theo thứ tự: docs/brd.md → docs/srs.md → code
