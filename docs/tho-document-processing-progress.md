# Tiến độ công việc – Thọ

## 1. Mục tiêu

Phụ trách dữ liệu, tìm kiếm văn bản V1 và kết nối Adapter/Linker cho luồng phân tích văn bản pháp luật dân sự.

## 2. Phần đã có trong main

- Các thay đổi Parser từ PR trước đã được tích hợp vào main.
- Nhánh làm việc đã cập nhật theo main tại commit `161e601`.

## 3. Phần đang thực hiện

- Khảo sát dữ liệu hiện có trong `data/raw`.
- Khảo sát dataset `th1nhng0/vietnamese-legal-documents`.
- Kiểm tra cấu trúc metadata và relationships để tìm cặp văn bản sửa đổi – văn bản gốc.
- Xác định một ca dân sự thực tế phù hợp với khả năng xử lý hiện tại.
- Chuẩn bị dữ liệu và nguồn đối chiếu để gửi Dũng duyệt.

## 4. Phần chưa hoàn thành

- Chưa chọn được cặp S–V1 dân sự chính thức.
- Chưa hoàn thành kho dữ liệu dân sự nhỏ có metadata và nguồn đối chiếu.
- Chưa hoàn thành chức năng tự tìm V1 từ chỉ dẫn trong S.
- Chưa có kết quả AmendmentItem thật cho ca dân sự.
- Chưa kiểm chứng các trường hợp thiếu V1 và mơ hồ về đích/phiên bản.
- Chưa ghép kiểm thử với Pipeline và LightRAG.

## 5. Kế hoạch tiếp theo

1. Chọn và gửi Dũng duyệt ca S–V1 dân sự.
2. Chuẩn bị dữ liệu, metadata và bằng chứng nguồn.
3. Tích hợp tìm V1 với Adapter/Linker hiện có.
4. Kiểm tra nội dung trước/sau và nguồn bằng chứng.
5. Bàn giao output cho Ngọc Anh, Đức Anh và Dũng để ghép luồng.

## 6. Trạng thái PR

Đây là Draft PR để nhóm review sớm tiến độ và phạm vi công việc. Các phần chưa hoàn thành sẽ được bổ sung bằng những commit tiếp theo.
