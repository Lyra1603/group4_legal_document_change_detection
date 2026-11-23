# legal-dataset-study

Thư mục khảo sát nguồn văn bản pháp luật, lọc ứng viên dân sự từ metadata và tải từng văn bản HTML để kiểm tra, chuẩn hóa dữ liệu.

## Cấu trúc thư mục

```text
legal-dataset-study/
├── .venv/                         Môi trường Python cục bộ, không đưa lên Git
├── download_metadata.py           Tải metadata, xuất CSV và gọi bộ lọc ứng viên
├── civil_metadata_rules.py        Bổ sung quy tắc lọc dữ liệu dân sự từ metadata
├── open_document.py               Tải HTML của một văn bản theo ID
└── data/
    ├── README.md                 Hướng dẫn sử dụng thư mục
    ├── metadata.csv              Metadata gốc xuất từ dataset
    ├── thong_ke_linh_vuc.csv      Thống kê số văn bản theo linh_vuc
    ├── ung_vien_dan_su.csv        Danh sách ứng viên sau các lượt lọc metadata
    ├── ung_vien_dan_su_luot2_evidence.csv
    │                             Quy tắc và giá trị metadata làm căn cứ theo ID
    ├── ung_vien_dan_su_luot2_report.json
    │                             Thống kê kết quả, vai trò cột và nguồn tham khảo
    └── vbpl-111436.html           HTML mẫu trích từ PDF nguồn
```

## Nguồn dữ liệu

Nguồn chính: [th1nhng0/vietnamese-legal-documents](https://huggingface.co/datasets/th1nhng0/vietnamese-legal-documents).

Các script tải dữ liệu cố định revision `8977887f17be2defae4c5171d55562e1cde7d695`.

| Thành phần dataset | Nội dung | Sử dụng trong thư mục |
| --- | --- | --- |
| `metadata` | Thông tin mô tả từng văn bản | Xuất thành `data/metadata.csv`, dùng để khảo sát và lọc ứng viên |
| `content` | Toàn văn trong trường `content_html` | Đọc streaming, tìm theo `id` rồi lưu thành HTML |
| `relationships` | Quan hệ giữa các văn bản | Chưa được các script trong thư mục xử lý |

[vohuutridung/vietnamese-legal-documents](https://huggingface.co/datasets/vohuutridung/vietnamese-legal-documents) là nguồn tham khảo bổ sung, chưa được tích hợp vào các script hiện tại.

`metadata.csv` có 171.556 dòng và 17 cột trong snapshot đi kèm. File được xuất từ metadata của dataset, không chứa toàn văn. Có metadata trên máy không đồng nghĩa đã tải toàn bộ nội dung văn bản.

## Chức năng các script

| File | Chức năng |
| --- | --- |
| `download_metadata.py` | Tải phần metadata, xuất `metadata.csv`, thống kê lĩnh vực và cập nhật danh sách ứng viên qua bộ quy tắc lọc |
| `civil_metadata_rules.py` | Bổ sung việc lọc ứng viên dân sự ngoài cách chỉ tìm từ “dân sự” trong `title` và `linh_vuc`; kết hợp thêm các cột metadata phù hợp, lưu căn cứ cho từng ID |
| `open_document.py` | Đọc `metadata.csv`, tìm một văn bản theo `document_id`, tải `content_html`, lưu file và mở trong trình duyệt |

## Chuẩn bị môi trường

Mở PowerShell tại thư mục gốc repo, sau đó chuyển vào thư mục nghiên cứu:

```powershell
Set-Location .\data\legal-dataset-study
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install datasets pandas
```

Mỗi máy tạo `.venv` riêng; không sao chép môi trường từ máy khác. Nếu môi trường đã chạy được thì không cần tạo lại. Các lệnh dưới đây chạy tại `legal-dataset-study`, trừ khi có ghi chú khác.

## Tải hoặc xem metadata

Các CSV đi kèm có thể sử dụng ngay. Chỉ chạy lệnh sau khi cần tải lại metadata:

```powershell
.\.venv\Scripts\python.exe -u .\download_metadata.py
```

Script xuất ba CSV chính và các file bằng chứng/thống kê của bộ lọc. Lệnh chưa tải toàn văn. Hugging Face có thể lưu cache ngoài thư mục dự án.

Xem danh sách ứng viên và tra một văn bản:

```powershell
Import-Csv .\data\ung_vien_dan_su.csv -Encoding UTF8 | Select-Object -First 10 id, so_ky_hieu, title
Import-Csv .\data\metadata.csv -Encoding UTF8 | Where-Object { $_.id -eq '15289' } | Format-List id, so_ky_hieu, title
```

## Lọc ứng viên dân sự từ metadata

- Lượt 1: tìm từ “dân sự” trong `title` hoặc `linh_vuc`.
- Lượt 2: mở rộng theo chủ đề và các cột metadata phù hợp bằng `civil_metadata_rules.py`.

`title`, `linh_vuc`, `nganh` và `thong_tin_ap_dung` có thể cung cấp dấu hiệu chủ đề. `co_quan_ban_hanh` và `loai_van_ban` chỉ hỗ trợ kết hợp ngữ cảnh hoặc ưu tiên duyệt. Cột trống không được tự bổ sung giá trị. Số hiệu, ngày tháng, hiệu lực, người ký và phạm vi lãnh thổ không được dùng để quyết định văn bản thuộc dân sự.

Xem quy tắc, kiểm tra dự kiến và cập nhật kết quả:

```powershell
.\.venv\Scripts\python.exe .\civil_metadata_rules.py --describe-rules
.\.venv\Scripts\python.exe .\civil_metadata_rules.py --dry-run
.\.venv\Scripts\python.exe .\civil_metadata_rules.py
```

`--dry-run` không ghi file. Chạy cập nhật nhiều lần không nhân bản ID. Script giữ các ứng viên đã có, bổ sung dòng mới và không sửa `metadata.csv`. Có thể chỉ định `--metadata`, `--candidates`, `--evidence`, `--report` để thử trên bản sao.

| File kết quả | Cách sử dụng |
| --- | --- |
| `ung_vien_dan_su.csv` | Danh sách để lựa chọn văn bản cần tải; giữ nguyên 17 cột metadata |
| `ung_vien_dan_su_luot2_evidence.csv` | Nối với danh sách qua `id`; xem nhóm đề xuất, ưu tiên, mã quy tắc, cờ cần duyệt và giá trị metadata làm căn cứ |
| `ung_vien_dan_su_luot2_report.json` | Xem số lượng, độ đầy đủ/vai trò các cột, phiên bản quy tắc và nguồn tham khảo |

Snapshot đi kèm có 506 ứng viên từ lượt 1 và 4.093 ứng viên sau lượt 2. Các số lượng có thể thay đổi khi cập nhật dữ liệu hoặc quy tắc; xem report của lần chạy tương ứng.

Danh sách này chưa phải tập văn bản dân sự đã xác nhận. Nhóm liên quan/hỗ trợ và trường hợp dễ nhầm được đánh dấu để đọc toàn văn. Ngược lại, một văn bản không được chọn qua metadata cũng chưa có nghĩa đã được xác định ngoài phạm vi.

## Tải HTML của một văn bản

1. Chọn ID trong metadata hoặc danh sách ứng viên; đối chiếu tên và số hiệu.
2. Mở `open_document.py`, đặt `document_id` thành ID cần tải, ví dụ `"15289"`, rồi lưu file.
3. Chạy script và kiểm tra HTML được tạo.

```powershell
notepad .\open_document.py
.\.venv\Scripts\python.exe -u .\open_document.py
Invoke-Item .\data\vbpl-15289.html
```

Đầu ra có dạng `data/vbpl-<id>.html`. Script chỉ tải một ID mỗi lần, không tự tải toàn bộ danh sách ứng viên hoặc chuyển DOCX. Streaming cần mạng và có thể đọc qua nhiều bản ghi trước khi gặp ID cần tìm.

Khi terminal báo `Đã lưu`, cần mở file để kiểm tra có toàn văn. Script hiện chỉ kiểm tra chuỗi HTML không rỗng, chưa xác minh nội dung trong `body`; chạy lại cùng ID có thể ghi đè HTML đã có.

### HTML mẫu 111436

`data/vbpl-111436.html` là bản đọc trích từ lớp chữ của PDF văn bản hợp nhất `25/VBHN-BTC`, không phải HTML nguyên bản có toàn văn của dataset. File có các phần tương ứng 20 trang PDF.

```powershell
Invoke-Item .\data\vbpl-111436.html
```

Nguồn đối chiếu: [thông tin văn bản](https://vbpl-bientap-gateway.moj.gov.vn/api/qtdc/public/doc/111436) và [PDF nguồn](https://vbpl-bientap-gateway.moj.gov.vn/api/qtdc/public/doc/minio/buckets/vbpl/111436/25-VBHN-BTC_25-VBHN-BTC.pdf/download).

HTML nguồn đã kiểm tra của ID này có `body` rỗng. Chạy `open_document.py` với ID `111436` có thể ghi đè mẫu đang có bằng HTML trắng. Khi gặp nguồn rỗng, cần đối chiếu nguồn khác và ghi rõ việc chuyển đổi; không coi thông báo lưu file là bằng chứng đã có toàn văn.

## Chuyển HTML sang DOCX

Bộ chuyển đổi nằm tại `backend/app/document_processing/html_to_docx.py`. Sau khi tải HTML, có thể gọi riêng từ thư mục nghiên cứu:

```powershell
.\.venv\Scripts\python.exe -m pip install python-docx lxml
.\.venv\Scripts\python.exe ..\..\backend\app\document_processing\html_to_docx.py .\data\vbpl-15289.html --document-number "100/2006/NĐ-CP" --output-dir ..\raw\case_moi
```

Ví dụ trên tạo `data/raw/case_moi/100_2006_NĐ-CP.docx` và report chuyển đổi. Thay thư mục, ID và số hiệu theo văn bản thực tế. Bộ chuyển đổi tự nhận diện số ký hiệu nếu HTML có thông tin phù hợp; `--document-number` dùng giá trị từ metadata đã đối chiếu khi HTML thiếu số của chính văn bản. Dấu `/` được đổi thành `_` trong tên file; đầu ra đã tồn tại sẽ không bị ghi đè.

DOCX là sản phẩm chuyển đổi, cần kiểm tra với HTML/nguồn chính thức trước khi dùng cho Parser. Mẫu kiểm thử converter nằm trong `data/test_html_to_docx`; PDF dùng bộ chuyển đổi riêng `backend/app/document_processing/pdf_to_docx.py`.

## Hướng phát triển lượt lọc 3

Lượt 3 chưa được triển khai. Giả định đầu vào là danh sách ứng viên sau lượt 2 cùng toàn văn đã tải và có thể đọc được. Hướng xử lý tiếp theo:

1. Đọc nội dung cụ thể, ưu tiên phạm vi điều chỉnh, đối tượng áp dụng và các quy định về quan hệ nhân thân/tài sản.
2. Đề xuất nhóm phù hợp phạm vi dân sự, liên quan/hỗ trợ, ngoài phạm vi hoặc chưa đủ căn cứ; kiểm tra lại các trường hợp metadata gây nhầm.
3. Ghi nguyên văn làm bằng chứng, vị trí Điều/Khoản/Điểm hoặc block, nguồn và phiên bản văn bản cho từng nhận định.
4. Rà soát thủ công một tập mẫu để đánh giá và điều chỉnh cách phân loại trước khi mở rộng.

Kết quả lọc theo nội dung nên được lưu riêng, nối qua ID và thông tin nguồn, không sửa metadata gốc hoặc ghi đè bằng chứng lượt 2. Việc chọn các cặp S–V1, xác minh phiên bản và nạp kho truy xuất là bước tiếp theo sau khi dữ liệu được duyệt.

## Quy ước khi bổ sung dữ liệu

- Đọc ID dưới dạng chuỗi và giữ kèm tên dataset, revision, số hiệu, nguồn đối chiếu.
- Không ghép hai nguồn chỉ vì ID giống nhau; cần đối chiếu định danh và phiên bản văn bản.
- Giữ HTML nguồn để đối chiếu với DOCX; phân biệt tài liệu nguyên bản và bản chuyển đổi.
- Các ca nguồn phục vụ dự án đặt trong `data/raw/<case_id>/`, cập nhật nguồn và thông tin file trong `data/manifest.csv`.
- Đáp án phân loại/trước–sau đã duyệt cần lưu riêng với nguồn dùng cho truy xuất.

## Kiểm thử bộ lọc metadata

Chạy tại thư mục gốc repo bằng môi trường Python đang sử dụng:

```powershell
py -B -m unittest discover -s test\data_suite -p test_civil_metadata_rules.py -v
```

## Lỗi thường gặp

| Hiện tượng | Kiểm tra |
| --- | --- |
| Không tìm thấy `metadata.csv` | Chạy script tải metadata tại `legal-dataset-study`; kiểm tra file nằm trong thư mục con `data` |
| Môi trường `.venv` không chạy sau khi chuyển máy/thư mục | Tạo lại môi trường tại vị trí hiện tại và cài thư viện |
| Tải toàn văn bị ngắt | Kiểm tra mạng, mở file đã lưu nếu có rồi mới quyết định tải lại |
| HTML mở trắng | Kiểm tra nội dung `body`, đối chiếu nguồn; không chuyển file trắng thành DOCX rồi coi là hoàn tất |
| Không nhận diện được số ký hiệu khi chuyển DOCX | Đối chiếu metadata và truyền `--document-number`; không lấy số của văn bản được viện dẫn |
| Bộ lọc báo ứng viên không khớp metadata | Kiểm tra dataset, revision và giá trị gốc; không ghép hoặc ghi đè trước khi làm rõ |
