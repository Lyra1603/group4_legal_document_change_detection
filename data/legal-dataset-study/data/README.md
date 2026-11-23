# Khảo sát legal-dataset-study và hướng dẫn tải HTML

Thư mục này dùng để khảo sát dataset, đọc metadata, chọn ứng viên dân sự và tải văn bản mẫu. Chưa có bước dựng knowledge graph hoặc nạp LightRAG.

## 1. Cấu trúc hiện tại

```text
legal-dataset-study/
├── .venv/                       Môi trường Python cục bộ
├── download_metadata.py         Tải metadata, xuất CSV và lọc ứng viên
├── open_document.py             Tìm một ID trong content và lưu HTML nguồn
└── data/
    ├── metadata.csv             Metadata của 171.556 văn bản
    ├── thong_ke_linh_vuc.csv     Thống kê số bản ghi theo linh_vuc
    ├── ung_vien_dan_su.csv       506 ứng viên theo từ khóa hiện tại
    ├── vbpl-111436.html          Bản đọc trích từ PDF của văn bản mẫu
    └── README.md                File hướng dẫn này
```

Hai script nằm ngang hàng với thư mục `data`. Phải chạy terminal tại `legal-dataset-study` vì script dùng đường dẫn tương đối. Hai script, môi trường và ba CSV thuộc phần khảo sát ban đầu; phần bổ sung chỉ gồm HTML mẫu và hướng dẫn này. Không đưa `.venv` lên Git.

## 2. Nguồn và thông tin dữ liệu

Nguồn chính: [th1nhng0/vietnamese-legal-documents](https://huggingface.co/datasets/th1nhng0/vietnamese-legal-documents). Hai script cố định revision `8977887f17be2defae4c5171d55562e1cde7d695`. Nguồn `vohuutridung` mới ở mức tham khảo bổ sung, chưa được các script sử dụng.

| Thành phần dataset | Nội dung và cách dùng hiện tại |
| --- | --- |
| `metadata` | Mô tả từng văn bản, xuất ra `metadata.csv`; không có toàn văn. |
| `content` | Nội dung HTML, ghép với metadata qua `id`. Script đọc streaming rồi lưu bản ghi tìm được. |
| `relationships` | Quan hệ giữa các văn bản; hai script hiện tại chưa tải hoặc xử lý. |

Metadata có 17 cột: `id`, `title`, `so_ky_hieu`, `ngay_ban_hanh`, `loai_van_ban`, `ngay_co_hieu_luc`, `ngay_het_hieu_luc`, `nguon_thu_thap`, `ngay_dang_cong_bao`, `nganh`, `linh_vuc`, `co_quan_ban_hanh`, `chuc_danh`, `nguoi_ky`, `pham_vi`, `thong_tin_ap_dung`, `tinh_trang_hieu_luc`.

Quy tắc tạo `ung_vien_dan_su.csv`: **`linh_vuc` chứa “dân sự” HOẶC `title` chứa “dân sự”**, không phân biệt hoa/thường; giá trị trống được thay bằng chuỗi rỗng trước khi lọc. Đây là tập ứng viên ban đầu, có thể bỏ sót hoặc lấy nhầm văn bản. Cần đọc và ghi bằng chứng trước khi đưa vào kho dân sự.

Có metadata trên máy chưa có nghĩa đã có toàn văn. Script đọc `content` cần mạng và có thể duyệt nhiều bản ghi trước khi gặp ID cần tìm. Hugging Face có thể lưu cache ngoài thư mục này.

## 3. Mở PowerShell đúng vị trí

```powershell
Set-Location -LiteralPath 'C:\Users\DELL\OneDrive - vnu.edu.vn\Desktop\đang học\problems of computer science\project pocs\bachdung-docs-commit\data\legal-dataset-study'
Get-Location
.\.venv\Scripts\python.exe --version
```

Nếu repo nằm ở vị trí khác, thay đường dẫn `Set-Location`. Nếu Python hiện có chạy được thì dùng luôn, không cần chạy `Activate.ps1`.

Chỉ khi chưa có `.venv` hoặc môi trường không chạy được sau khi chuyển thư mục, tạo lại bằng Python đã cài:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install datasets pandas pypdf
```

Nếu chỉ thiếu thư viện thì chỉ chạy dòng `pip install`. Lệnh cài thư viện cập nhật môi trường `.venv`.

## 4. Tải metadata và xem ứng viên

Nếu ba CSV đã có và chỉ muốn xem HTML mẫu thì bỏ qua bước tải lại.

```powershell
.\.venv\Scripts\python.exe -u .\download_metadata.py
```

Với revision hiện tại, kết quả dự kiến: `Số dòng: 171556`, `Số ứng viên theo tên/lĩnh vực: 506`, cuối cùng là `Đã lưu vào:` kèm đường dẫn `data`. Lệnh này ghi lại ba CSV, chưa tải toàn bộ văn bản.

```powershell
Import-Csv .\data\ung_vien_dan_su.csv -Encoding UTF8 | Select-Object -First 5 id, so_ky_hieu, title
Import-Csv .\data\metadata.csv -Encoding UTF8 | Where-Object { $_.id -eq '111436' } | Format-List id, so_ky_hieu, title
```

## 5. Mở HTML mẫu đã có



```powershell
Invoke-Item .\data\vbpl-111436.html
```

ID `111436` là Văn bản hợp nhất số `25/VBHN-BTC` về bảo hiểm bắt buộc trách nhiệm dân sự của chủ xe cơ giới. HTML nguồn đã lấy có body rỗng. Kiểm tra gateway ngày 23/11/2026 cũng cho `hasContent=false` và có tên PDF gốc. Vì vậy `vbpl-111436.html` hiện tại là bản đọc trích từ lớp chữ của PDF chính thức, có nhãn xuất xứ và phân đoạn theo 20 trang PDF. Bản trích có thể có lỗi ký tự hoặc bố cục và cần đối chiếu PDF khi trích dẫn. Đây là mẫu tải/chuyển đổi, phạm vi phù hợp cho ca dân sự của nhóm còn cần rà soát.

Nguồn kiểm tra gồm [VBPL gateway](https://vbpl-bientap-gateway.moj.gov.vn/api/qtdc/public/doc/111436) và [PDF gốc](https://vbpl-bientap-gateway.moj.gov.vn/api/qtdc/public/doc/minio/buckets/vbpl/111436/25-VBHN-BTC_25-VBHN-BTC.pdf/download). PDF được kiểm tra có 20 trang, có text trích được trên cả 20 trang và SHA-256 `b6575fef01acc35fc102dd34929ab0c655cb73a3fb6a09bc383f7084eedde4c6`.

## 6. Tải lại HTML có nội dung cho ID 111436

Cài thư viện đọc PDF vào môi trường đang dùng.

```powershell
.\.venv\Scripts\python.exe -m pip install pypdf
```

Chạy nguyên khối dưới đây. Python chạy trực tiếp từ terminal. PDF chỉ được giữ tạm trong bộ nhớ, đầu ra duy nhất được ghi là `data/vbpl-111436.html`.

```powershell
@'
from pathlib import Path
from io import BytesIO
from urllib.request import urlopen
import hashlib
import html
from pypdf import PdfReader

url = "https://vbpl-bientap-gateway.moj.gov.vn/api/qtdc/public/doc/minio/buckets/vbpl/111436/25-VBHN-BTC_25-VBHN-BTC.pdf/download"
with urlopen(url, timeout=120) as response:
    pdf = response.read()
if not pdf.startswith(b"%PDF-"):
    raise SystemExit("Nguon tra ve khong phai PDF.")
expected = "b6575fef01acc35fc102dd34929ab0c655cb73a3fb6a09bc383f7084eedde4c6"
if hashlib.sha256(pdf).hexdigest() != expected:
    raise SystemExit("PDF khac ban da kiem tra. Can doi chieu nguon truoc khi ghi de.")
pages = [page.extract_text() or "" for page in PdfReader(BytesIO(pdf)).pages]
if any(not text.strip() for text in pages):
    raise SystemExit("Co trang khong doc duoc chu. Can kiem tra PDF/OCR.")
parts = []
for number, text in enumerate(pages, 1):
    escaped = html.escape(text).replace("\n", "&#10;")
    parts.append(f"<h2>Trang PDF {number}</h2><pre>{escaped}</pre>")
content = (
    '<!doctype html><html lang="vi"><head><meta charset="utf-8">'
    '<title>25/VBHN-BTC</title><style>'
    'body{max-width:900px;margin:40px auto;padding:0 20px;font-family:Arial}'
    'pre{white-space:pre-wrap;font:inherit;line-height:1.5}'
    '</style></head><body><h1>25/VBHN-BTC</h1>'
    '<p>Ban doc duoc trich tu lop chu PDF goc. HTML nguon rong. '
    'Can doi chieu PDF khi trich dan.</p>'
    f'<p><a href="{html.escape(url)}">PDF nguon</a></p>'
    + ''.join(parts) + '</body></html>'
)
output = Path("data/vbpl-111436.html")
output.parent.mkdir(exist_ok=True)
output.write_text(content, encoding="utf-8")
print("Da luu", output.resolve(), "So trang PDF", len(pages))
'@ | .\.venv\Scripts\python.exe -
```

Khi thấy `Da luu` và `So trang PDF 20`, mở file bằng lệnh ở trên. Nếu tải lỗi do mất mạng, chạy lại khối lệnh. Lệnh chỉ ghi đè HTML sau khi tải và kiểm tra PDF thành công.

## 7. Tải HTML nguồn từ dataset cho ID khác

Mở `open_document.py`, đổi `document_id` rồi lưu và chạy.

```powershell
notepad .\open_document.py
.\.venv\Scripts\python.exe -u .\open_document.py
```

Script ban đầu chỉ kiểm tra chuỗi HTML có rỗng hay không, nên thông báo “Đã lưu” chưa chứng minh body có toàn văn. Với ID `111436`, chạy script này có thể ghi đè bản đọc từ PDF bằng HTML nguồn rỗng. Dùng khối tải PDF ở trên để khôi phục bản đọc có nội dung. Việc cải thiện script và nối Parser/Adapter sẽ được giao tiếp sau.

## 8. Kiểm tra hoàn tất

```powershell
Get-Item .\data\vbpl-111436.html | Select-Object Name, Length, LastWriteTime
Invoke-Item .\data\vbpl-111436.html
```

Hoàn tất khi terminal báo lưu file, trả lại dấu nhắc `PS ...>`, file tồn tại và trình duyệt hiển thị nội dung. Riêng HTML trích từ PDF của ID `111436` có các phần theo 20 trang. Thông báo lưu và kích thước file chưa chứng minh toàn văn đủ, đúng; cần đối chiếu nguồn khi trích dẫn.

- Không tìm thấy `metadata.csv`: kiểm tra đang đứng đúng `legal-dataset-study`, rồi chạy bước 4.
- Mất mạng: kết nối lại và chạy lại bước tải. Nếu HTML đã tồn tại, mở kiểm tra trước khi tải lại.
- HTML mở trắng: nguồn có thể có body rỗng; với ID `111436`, dùng bước 6.
- Cảnh báo thiếu `HF_TOKEN` hoặc symlink trên Windows: xem kết quả cuối cùng; cảnh báo riêng lẻ không tự chứng minh tải thất bại.

Dừng ở bước tải và đọc HTML để kiểm tra thủ công. Việc cải thiện script, chọn tập dân sự và nạp LightRAG sẽ được triển khai theo phân công tiếp theo.