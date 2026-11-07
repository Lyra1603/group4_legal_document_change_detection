# Group 4 — Legal Document Change Detection

## 1. Giới thiệu dự án

Dự án hỗ trợ rà soát thay đổi trong văn bản quy phạm pháp luật tiếng Việt, hướng tới luật sư, người làm pháp chế và người nghiên cứu luật. Mục tiêu là giúp người dùng nhận biết thay đổi về nội dung quy định, phân biệt với thay đổi diễn đạt và đối chiếu kết quả với bằng chứng nguồn.

## 2. Chức năng và phạm vi

Đầu vào gồm văn bản ban đầu **V1**, văn bản sửa đổi **S** và tài liệu tham chiếu nếu cần. S chứa chỉ dẫn sửa đổi, không phải bản đầy đủ sau sửa đổi V2.

Hệ thống được thiết kế để:

- Nhận diện yêu cầu sửa đổi, bổ sung hoặc bãi bỏ trong S và tìm nội dung đích trong V1.
- Đối chiếu nội dung trước/sau cục bộ, phân tích thay đổi nghĩa và mức tác động.
- Cung cấp bằng chứng, thông tin hiệu lực/chuyển tiếp được nêu trong nguồn và cảnh báo khi thiếu căn cứ.
- Hỗ trợ DOCX và PDF có lớp chữ; bổ sung truy xuất ngữ cảnh bằng LightRAG.

Phiên bản đầu không hỗ trợ OCR/PDF scan, không bắt buộc dựng V2 đầy đủ và không tự xác minh hiệu lực pháp lý thực tế. Kết quả phục vụ rà soát, cần được người dùng kiểm chứng.

## 3. Trạng thái hiện tại

Dự án đang phát triển. Đã có công cụ PDF → DOCX và Parser cấu trúc văn bản. Bản API nền hỗ trợ upload và đọc/parse; luồng phân tích thay đổi đầu-cuối, giao diện và tích hợp LightRAG chưa hoàn thiện.

Phương án tích hợp tạm chọn là chạy LightRAG Server riêng và gọi qua HTTP. Dịch vụ có thể chạy trên cùng máy; nhu cầu Internet phụ thuộc cấu hình LLM/embedding.

## 4. Cài đặt và chạy nhanh

Yêu cầu Python 3.11 trở lên; khuyến nghị Python 3.12 theo môi trường đã kiểm tra. Các lệnh dưới áp dụng cho bản API nền hỗ trợ upload, chạy từ thư mục gốc dự án.

Tạo môi trường Python:

```bash
python -m venv .venv
```

Kích hoạt trên Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Hoặc trên Linux/macOS:

```bash
source .venv/bin/activate
```

Cài thư viện và khởi động backend:

```bash
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Mở [API Docs](http://127.0.0.1:8000/docs), chọn `POST /api/compare` và gửi `doc_v1`, `doc_s`, cùng `reference_files` nếu có.

Bản nền hiện báo chưa cấu hình phân tích sau bước đọc/parse; chưa trả báo cáo thay đổi hoàn chỉnh. LightRAG được cài/chạy riêng và chưa được nối vào API này.

## 5. Cấu trúc thư mục tổng quan — mục tiêu

```text
backend/
frontend/
data/
tests/
docs/
deploy/
runtime/
requirements.txt
.env.example
.gitignore
```

## 6. Tài liệu dự án

| Tài liệu | Nội dung |
| --- | --- |
| [BRD](brd.md) | Nhu cầu, người dùng và phạm vi nghiệp vụ |
| [SRS](srs.md) | Yêu cầu, hợp đồng dữ liệu và hành vi hệ thống |
| [Architecture](architecture.md) | Thiết kế module, cây thư mục chi tiết và phương án tích hợp |
| [Implementation Plan](implementation-plan.md) | Công việc, phân công, phụ thuộc và mốc bàn giao |
| [Data Annotation Guide](data-annotation-guide.md) | Chuẩn bị dữ liệu, bằng chứng và gán nhãn |

Tài liệu cần bổ sung: `api-contract.md`, `development-guide.md` và `test-evaluation-plan.md`.

## 7. Nhóm thực hiện

**Học phần và nhóm:** Problems of Computer Science (POCS) — Nhóm 4  
**Người điều phối:** Dương Đức Anh

| Thành viên | Phụ trách chính |
| --- | --- |
| Bạch Công Dũng | Dữ liệu, nghiệp vụ, tài liệu tổng quát và hướng dẫn gán nhãn; đề xuất chủ trì chuẩn bị ngữ cảnh và kiểm tra căn cứ |
| Dương Đức Anh | Điều phối nhóm; Backend, schema, API, Pipeline, môi trường chung và tích hợp |
| Bùi Quang Thọ | Reader, Parser; trích yêu cầu sửa đổi, liên kết với V1, vị trí nguồn và thông tin hiệu lực/chuyển tiếp |
| Đoàn Ngọc Anh | Text Diff, Semantic Diff và Classifier & Scorer; phân tích thay đổi với ngữ cảnh, bằng chứng và mức tác động |
| Đỗ Tuấn Anh | Frontend, Evaluator; điều phối kiểm thử, review nhãn chuẩn và đánh giá chất lượng hệ thống |

Phân công theo [Implementation Plan](implementation-plan.md). hiện tại tích hợp Lightrag sẽ do DŨng và Đức Anh 
