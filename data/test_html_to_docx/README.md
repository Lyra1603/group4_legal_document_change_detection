# Kiểm tra chuyển HTML sang DOCX

Ba ca dưới đây dùng để duyệt bộ chuyển đổi `backend/app/document_processing/html_to_docx.py`. Mỗi ca là một văn bản, không phải một cặp V1–S. Không thay thế các ca trong `data/raw` hoặc ca PDF.

## Nguồn mẫu

Nguồn: [th1nhng0/vietnamese-legal-documents](https://huggingface.co/datasets/th1nhng0/vietnamese-legal-documents), config `content`, split `data`, trường `content_html`, revision `8977887f17be2defae4c5171d55562e1cde7d695`. HTML được lấy qua streaming ngày 23/11/2026; không chỉnh sửa nội dung nguồn trước khi lưu `input.html`.

| Thư mục | ID dataset | Số hiệu | Mục đích thử |
| --- | --- | --- | --- |
| `case_01` | `15289` | 100/2006/NĐ-CP | Văn bản dài, Chương/Điều/Khoản/Điểm và nhấn mạnh |
| `case_02` | `56666` | 08/2014/TT-BTP | Văn bản sửa đổi, trích dẫn nội dung thay thế và nhãn Điều có hậu tố |
| `case_03` | `119155` | 216/2016/TT-BTC | Khối đầu/khối ký dựng bằng div và CSS, ví dụ tính tiền và tỷ lệ |

Nguồn đối chiếu: [15289](https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=15289), [56666](https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=56666), [119155](https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=119155). Mẫu nguồn chưa được chứng nhận đầy đủ hoặc đúng trạng thái pháp lý tại một thời điểm.

## Các file trong mỗi ca

```text
case_01/ (tương tự case_02 và case_03)
├── input.html                 HTML nguồn từ dataset
├── converted.docx             DOCX được bộ chuyển đổi tạo
└── converted.report.json      Hash, nguồn, kiểm tra chữ, cảnh báo và thông tin kiểm tra mẫu
```

DOCX là bản chuyển đổi để đọc/phân tích, không phải DOCX gốc chính thức. Report mẫu được bổ sung ID dataset và thông tin kiểm tra bố cục sau khi chạy converter. Ảnh/PDF dùng kiểm tra được giữ ngoài repo.

## Tên đầu ra mặc định theo số ký hiệu

Cả `html_to_docx.py` và `pdf_to_docx.py` cho phép bỏ đối số tên đầu ra. Chương trình nhận diện số ký hiệu của chính văn bản từ trường metadata/dòng `Số:` hoặc tiêu đề có số hiệu, rồi lưu cạnh file nguồn. Trên Windows, dấu `/` đổi thành `_`: `84/2026/TT-BXD` → `84_2026_TT-BXD.docx`, kèm `84_2026_TT-BXD.report.json`.

```powershell
py backend\app\document_processing\html_to_docx.py data\test_html_to_docx\case_03\input.html
py backend\app\document_processing\pdf_to_docx.py input.pdf
```

HTML của case_01 và case_02 không có số ký hiệu của chính văn bản trong phần thân/tiêu đề đã lưu. Truyền giá trị `so_ky_hieu` từ metadata đã đối chiếu, ví dụ:

```powershell
py backend\app\document_processing\html_to_docx.py data\test_html_to_docx\case_01\input.html --document-number "100/2006/NĐ-CP"
```

Chỉ định `--output-dir thu_muc` để chọn thư mục đích nhưng vẫn đặt tên tự động. API nhận `output_path=None`, `document_number=...`, `output_dir=...`. Tên đầu ra thủ công vẫn được hỗ trợ như trước. Không tự lấy số của văn bản được viện dẫn làm số của S; thiếu số mà chưa cung cấp metadata/tên đầu ra, số xung đột hoặc file đã tồn tại thì dừng và báo lý do. Report ghi số ký hiệu, bằng chứng nhận diện và cách đặt tên. Không dùng ảnh chụp màn hình để OCR.

Chạy cả kiểm thử chuyển đổi và đặt tên:

```powershell
py -B -m unittest discover -s test\unit\document_processing -p test_html_to_docx.py -v
py -B -m unittest discover -s test\unit\document_processing -p test_document_number.py -v
```

## Chạy lại

Chạy tại thư mục gốc repo, dùng Python của môi trường bạn đang sử dụng:

```powershell
py -m pip install python-docx lxml
py backend\app\document_processing\html_to_docx.py data\test_html_to_docx\case_01\input.html data\test_html_to_docx\case_01\converted_again.docx
```

Lệnh tạo hai file: `converted_again.docx` và `converted_again.report.json`. Không ghi đè đầu ra đã tồn tại; khi chạy lần nữa phải chọn tên khác. Module chỉ chuyển HTML cục bộ, chưa tự tải dataset hoặc nối vào `open_document.py`/Pipeline.

API dùng nội bộ:

```python
from backend.app.document_processing.html_to_docx import convert_html_to_docx

docx_path, report_path = convert_html_to_docx(
    "input.html", "output.docx", source_url="URL nguồn để ghi vào report"
)
```

Chạy kiểm thử offline:

```powershell
py -B -m unittest discover -s test\unit\document_processing -p test_html_to_docx.py -v
```

## Đã kiểm tra và giới hạn

- 14 kiểm thử hồi quy: HTML rỗng, tiếng Việt/encoding, đường dẫn tiếng Việt ở CLI Windows, định dạng inline, khoảng trắng HTML so với `pre`/`br`, bảng có rowspan/colspan, bảng và danh sách lồng nhau, liên kết/ảnh và chống ghi đè.
- Cả ba mẫu: mở lại DOCX và so chữ/thứ tự với HTML nguồn, bỏ qua khoảng trắng. Nhãn danh sách do converter tạo được ghi riêng, không tính là chữ gốc.
- Đã mở ba DOCX bằng Microsoft Word ở chế độ chỉ đọc, xuất PDF, dựng ảnh và kiểm tra bố cục. Số trang trên môi trường này lần lượt là 21, 23 và 9; máy khác có thể phân trang khác.
- Đã sửa lỗi khoảng trắng thụt mã HTML gây giãn trang; khoảng trắng mã nguồn ngoài `pre` được co lại, còn `<br>` được giữ là xuống dòng.
- Parser hiện tại đọc được cả ba DOCX: lần lượt 48, 3 và 10 Điều. Đây là kiểm tra kết nối, không phải đáp án cấu trúc đã được chuyên môn duyệt.
- Ba HTML thật này không có phần tử `table`; bảng gộp ô được kiểm tra bằng ca tổng hợp trong unit test, chưa phải bằng chứng về mọi dạng bảng thực tế.

Không tải CSS/ảnh bên ngoài, không OCR, không đảm bảo khôi phục bố cục in. Khối dùng CSS `display: table` được đọc theo thứ tự DOM, chưa dựng lại hai cột. Đích liên kết nằm trong report, DOCX chỉ giữ chữ liên kết. Trạng thái `needs_review` và `requires_visual_review` được giữ để người dùng duyệt; kiểm tra chữ không chứng minh toàn văn nguồn đã đủ.

## Dũng kiểm tra thủ công

Mở `input.html` và `converted.docx` cạnh nhau; kiểm tra tiêu đề, thứ tự đoạn, số tiền/tỷ lệ, nhãn Điều/Khoản/Điểm và khối trích dẫn. Với case_03, khối đầu/khối ký không được giãn thành nhiều dòng trống. Ghi lại ca, trang/đoạn và lỗi thấy được để sửa tiếp.
