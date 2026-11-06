# Chạy và tích hợp backend

## Môi trường đã kiểm tra

Windows, Python 3.14; môi trường hiện tại của repo. Dependency trực tiếp được
pin trong requirements.txt, test dependency trong requirements-dev.txt.
requirements-lock.txt lưu toàn bộ phiên bản của môi trường đã kiểm tra;
chưa tuyên bố đã kiểm tra trên Linux hoặc các phiên bản Python khác.

Chạy từ thư mục gốc, không cần activate venv:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Mở http://127.0.0.1:8000/docs. `/api/compare` là baseline chuỗi V1/V2;
`/api/comparisons` là upload V1–S phát triển. Thử DOCX thật bằng PowerShell:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/comparisons -F "doc_v1=@data/example of amend/case_01/34_2017_TT-BTC_v1.docx" -F "doc_s=@data/example of amend/case_01/33_2019_TT-BTC_amendment.docx"
```

Đường dẫn trên thuộc nhánh backend hiện tại; main dùng data/raw. Mặc định
server trả FAILED / MODULE_NOT_CONFIGURED sau ingestion vì chưa nhận adapter
nghiệp vụ. Không dùng response này để tuyên bố hệ thống đã phân tích V1–S.
Để thử contract thành công, chạy tests/test_comparison.py: chỉ test dùng
adapter fixture. Report không yêu cầu database hoặc hàng đợi nền.

## Giới hạn phát triển, chưa phải ngưỡng nghiệm thu

Đây là giới hạn phòng ngừa có thể cấu hình, chưa được đo trên tập đại diện.
Nhóm cần đo và chốt giá trị cuối cùng theo Architecture trước nghiệm thu.

| Biến môi trường | Mặc định | Ý nghĩa |
| --- | --- | --- |
| LEGAL_MAX_FILE_BYTES | 10485760 | 10 MiB mỗi file |
| LEGAL_MAX_REQUEST_BYTES | 33554432 | 32 MiB body, cả multipart overhead |
| LEGAL_MAX_DOCX_EXPANDED_BYTES | 67108864 | Tổng kích thước khai báo entry DOCX giải nén |
| LEGAL_MAX_REFERENCES | 5 | Số file tham chiếu |
| LEGAL_MAX_CHARACTERS | 500000 | Số ký tự Reader mỗi tài liệu |
| LEGAL_MAX_AMENDMENTS | 200 | Số chỉ dẫn extractor trả |
| LEGAL_MAX_CONCURRENT | 2 | Slot so sánh mỗi tiến trình |
| LEGAL_DEADLINE_SECONDS | 60 | Deadline hợp tác giữa các bước pipeline |

Đặt biến trước khi khởi động server. Dùng một worker khi thử giới hạn tổng;
nhiều worker sẽ nhân số slot và cần quyết định giới hạn chung trước triển khai.
Slot được giữ tới khi worker đồng bộ kết thúc. Deadline kiểm tra trước bước
và cuối pipeline; không ngắt cứng thư viện DOCX/PDF hoặc module đang chạy.
Không được coi timeout HTTP là hủy tác vụ. Cần đo tác vụ native, chọn giới hạn
đầu vào hoặc cô lập tiến trình nếu nhóm yêu cầu hard timeout. Adapter gọi API
ngoài phải tự có timeout/retry giới hạn trong deadline; hiện chưa có gọi ngoài.
Reader, Parser và tổng ingestion được log riêng; các stage còn lại cũng log
riêng, gồm comparison_id, stage và duration, không log toàn văn tài liệu.
Chưa có số đo chất lượng/hiệu năng đại diện hoặc bảo đảm SLA.

## File tạm

Upload được giữ trong thư mục `legal-comparisons` dưới temp của hệ điều hành,
mỗi request một thư mục UUID riêng. Tên upload không được dùng làm đường dẫn.
OS lease giữ thư mục đang xử lý; finally dọn file sau worker. Mỗi lần tạo
workspace quét thư mục sở hữu đã quá 24 giờ và không còn lock để dọn phần sót
do tiến trình dừng bất thường. Không dọn thư mục đang giữ lease. Không có lịch
sử kết quả hoặc tiếp tục job sau reload. Pipeline nhận file local trực tiếp
không xóa file đầu vào của người dùng.

## Quy trình bàn giao

- Code vào nhánh riêng; PR nêu đầu ra, lệnh kiểm tra, giới hạn và contract đổi.
- Schema mục tiêu ở backend/app/schemas/contracts.py. LegacyScoringResult và
  AlignedPair chỉ phục vụ baseline V1/V2; không dùng trong báo cáo V1–S.
- Chủ module và bên nhận thử cùng fixture trước tích hợp; không đưa model hoặc
  nguồn cứng từ demo vào kết quả thật. Fixture không phải nhãn độc lập.
- Mỗi thay đổi contract cần cập nhật SRS/fixture và adapter liên quan sau review.
- Chốt release sau khi nhóm review dữ liệu, thuật toán và test độc lập; commit/tag
  phải gắn dependency/config/dữ liệu và kết quả tương ứng.

`pdf_to_docx.py` là công cụ riêng, chưa tích hợp. Nó còn cần pdf2docx (và tài
nguyên phụ thuộc) nếu dùng nhánh chuyển PDF; chưa khóa/kiểm thử môi trường đó.
Reader PDF trực tiếp dùng PyMuPDF, không bắt buộc chuyển qua công cụ này.
Parser cấu trúc nâng cao vẫn dùng source ref khác; chưa tự đổi sang contract
Reader. Trước khi đổi parser chính cần review cùng Thọ.
