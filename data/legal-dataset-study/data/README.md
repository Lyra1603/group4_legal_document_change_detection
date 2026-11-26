# legal-dataset-study

Thư mục khảo sát nguồn văn bản pháp luật, lọc ứng viên dân sự từ metadata và tải văn bản thành DOCX theo số hiệu. HTML được xử lý tạm trong luồng mặc định.

## Cấu trúc thư mục

```text
legal-dataset-study/
├── download_metadata.py           Tải metadata, xuất CSV và gọi bộ lọc ứng viên
├── civil_metadata_rules.py        Bổ sung quy tắc lọc dữ liệu dân sự từ metadata
├── open_document.py               Tải ứng viên thành DOCX theo số hiệu
└── data/
    ├── README.md                 Hướng dẫn sử dụng thư mục
    ├── metadata.csv              Metadata gốc xuất từ dataset
    ├── thong_ke_linh_vuc.csv      Thống kê số văn bản theo linh_vuc
    ├── ung_vien_dan_su.csv        Danh sách ứng viên sau các lượt lọc metadata
    ├── ung_vien_dan_su_luot2_evidence.csv
    │                             Quy tắc và giá trị metadata làm căn cứ theo ID
    ├── ung_vien_dan_su_luot2_report.json
    │                             Thống kê kết quả, vai trò cột và nguồn tham khảo
    ├── vbpl-111436.html           HTML mẫu trích từ PDF nguồn
    └── lightrag/                 Thư mục đích minh họa, chứa DOCX theo số hiệu
```

## Nguồn dữ liệu

Nguồn chính: [th1nhng0/vietnamese-legal-documents](https://huggingface.co/datasets/th1nhng0/vietnamese-legal-documents).

Các script tải dữ liệu cố định revision `8977887f17be2defae4c5171d55562e1cde7d695`.

| Thành phần dataset | Nội dung | Sử dụng trong thư mục |
| --- | --- | --- |
| `metadata` | Thông tin mô tả từng văn bản | Xuất thành `data/metadata.csv`, dùng để khảo sát và lọc ứng viên |
| `content` | Toàn văn trong trường `content_html` | Đọc streaming theo ID; chuyển HTML tạm thành DOCX |
| `relationships` | Quan hệ giữa các văn bản | Chưa được các script trong thư mục xử lý |

[vohuutridung/vietnamese-legal-documents](https://huggingface.co/datasets/vohuutridung/vietnamese-legal-documents) là nguồn tham khảo bổ sung, chưa được tích hợp vào các script hiện tại.

`metadata.csv` có 171.556 dòng và 17 cột trong snapshot đi kèm. File được xuất từ metadata của dataset, không chứa toàn văn. Có metadata trên máy không đồng nghĩa đã tải toàn bộ nội dung văn bản.

## Chức năng các script

| File | Chức năng |
| --- | --- |
| `download_metadata.py` | Tải phần metadata, xuất `metadata.csv`, thống kê lĩnh vực và cập nhật danh sách ứng viên qua bộ quy tắc lọc |
| `civil_metadata_rules.py` | Bổ sung việc lọc ứng viên dân sự ngoài cách chỉ tìm từ “dân sự” trong `title` và `linh_vuc`; kết hợp thêm các cột metadata phù hợp, lưu căn cứ cho từng ID |
| `open_document.py` | Chỉ nhận ID trong CSV ứng viên; kiểm tra HTML/PDF/DOCX đã có ở thư mục đích và thư mục con, tải những văn bản còn thiếu, kiểm tra có chữ rồi chuyển DOCX theo số hiệu |

## Chuẩn bị môi trường

Mở PowerShell tại thư mục gốc repo, sau đó chuyển vào thư mục nghiên cứu:

```powershell
Set-Location .\data\legal-dataset-study
$studyVenv = Join-Path $env:USERPROFILE '.venvs\pocs-study'
python -m venv $studyVenv
$studyPython = Join-Path $studyVenv 'Scripts\python.exe'
& $studyPython -m pip install datasets pandas python-docx lxml
```

Dùng môi trường riêng ở đường dẫn ngắn để tránh giới hạn Windows. Khi mở cửa sổ PowerShell mới, khai báo lại `$studyVenv` và `$studyPython` như trên; không cần tạo lại môi trường hoặc cài lại thư viện nếu đã có. Các lệnh dưới đây chạy tại `legal-dataset-study`, trừ khi có ghi chú khác.

## Tải hoặc xem metadata

Các CSV đi kèm có thể sử dụng ngay. Chỉ chạy lệnh sau khi cần tải lại metadata:

```powershell
& $studyPython -u .\download_metadata.py
```

download_metadata.py ghi lại metadata.csv và thống kê lĩnh vực, sau đó bộ lọc cập nhật ứng viên/evidence/report. Script dùng đường dẫn tương đối nên chạy tại legal-dataset-study. Lệnh chưa tải toàn văn. Hugging Face có thể lưu cache ngoài thư mục dự án.

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
& $studyPython .\civil_metadata_rules.py --describe-rules
& $studyPython .\civil_metadata_rules.py --dry-run
& $studyPython .\civil_metadata_rules.py
```

`--dry-run` không ghi file. Chạy cập nhật nhiều lần không nhân bản ID. Script giữ các ứng viên đã có, bổ sung dòng mới và không sửa `metadata.csv`. Có thể chỉ định `--metadata`, `--candidates`, `--evidence`, `--report` để thử trên bản sao.

| File kết quả | Cách sử dụng |
| --- | --- |
| `ung_vien_dan_su.csv` | Danh sách để lựa chọn văn bản cần tải; giữ nguyên 17 cột metadata, bổ sung cột trạng thái khi tải |
| `ung_vien_dan_su_luot2_evidence.csv` | Nối với danh sách qua `id`; xem nhóm đề xuất, ưu tiên, mã quy tắc, cờ cần duyệt và giá trị metadata làm căn cứ |
| `ung_vien_dan_su_luot2_report.json` | Xem số lượng, độ đầy đủ/vai trò các cột, phiên bản quy tắc và nguồn tham khảo |

Snapshot đi kèm có 506 ứng viên từ lượt 1 và 4.093 ứng viên sau lượt 2. Các số lượng có thể thay đổi khi cập nhật dữ liệu hoặc quy tắc; xem report của lần chạy tương ứng.

Danh sách này chưa phải tập văn bản dân sự đã xác nhận. Nhóm liên quan/hỗ trợ và trường hợp dễ nhầm được đánh dấu để đọc toàn văn. Ngược lại, một văn bản không được chọn qua metadata cũng chưa có nghĩa đã được xác định ngoài phạm vi.

## Tải văn bản thành DOCX

Chạy các lệnh sau tại `data/legal-dataset-study`, sau khi đã khai báo `$studyPython` theo phần chuẩn bị môi trường. Script nhận lựa chọn qua tham số terminal, không hỏi nhập đường dẫn khi chạy. Các đường dẫn tương đối được tính từ thư mục terminal hiện tại.

Kiểm tra một ID trong ứng viên, chưa tải hoặc chuyển đổi:

```powershell
& $studyPython -u .\open_document.py --id 15289 --output-dir .\data\lightrag --dry-run
```

Tải thật cùng ID; có thể truyền nhiều ID sau `--id`:

```powershell
& $studyPython -u .\open_document.py --id 15289 --output-dir .\data\lightrag
```

Xét danh sách ứng viên và thử tối đa 10 văn bản chưa có:

```powershell
& $studyPython -u .\open_document.py --all-candidates --limit 10 --output-dir .\data\lightrag --dry-run
& $studyPython -u .\open_document.py --all-candidates --limit 10 --output-dir .\data\lightrag
```

Mặc định thư mục đích chỉ nhận DOCX theo số hiệu, ví dụ `100_2006_NĐ-CP.docx`. HTML được xử lý trong thư mục tạm rồi dọn, không tạo HTML, `.source.json` hoặc `.report.json` cho mỗi DOCX. Thư mục đích được tạo khi cần lưu kết quả. `data/lightrag/` hiện có 9 DOCX mẫu; đây là thư mục tài liệu, chưa phải chỉ mục hoặc knowledge graph LightRAG đã xây dựng.

### Kiểm tra trùng và nguồn

- Chỉ chấp nhận ID có trong CSV ứng viên, kể cả khi ID tồn tại trong metadata gốc.
- Quét thư mục đích và thư mục con để kiểm tra HTML/PDF/DOCX đã có. DOCX được kiểm tra gói ZIP và sự hiện diện của `word/document.xml`.
- Nếu có manifest hoặc bản ghi nguồn phù hợp, đối chiếu dataset, revision, ID và hash theo thông tin được cung cấp. Chỉ trùng tên file thì báo `skipped_unverified`, chưa xác nhận đúng nguồn/phiên bản.
- File đã có không bị ghi đè; file rỗng, hỏng hoặc xung đột nguồn được giữ lại và báo để kiểm tra. Số hiệu có thể trùng giữa các văn bản, vì vậy không dùng tên file làm định danh duy nhất.
- Script không tự cập nhật `data/manifest.csv`, xác định vai trò S–V1, phân loại toàn văn hoặc nạp LightRAG. Khi đưa dữ liệu vào kho chính thức, cần ghi ánh xạ dataset/revision/ID với đường dẫn file và nguồn đối chiếu.

Danh sách được xét theo thứ tự CSV, chưa sắp xếp theo `download_priority`. `--limit N` chỉ tính văn bản chưa có được thử tải; số DOCX thành công có thể ít hơn N vì lỗi tải/chuyển đổi. Bỏ `--limit` sẽ xét toàn bộ lựa chọn, bao gồm toàn bộ CSV khi dùng `--all-candidates`.

### Theo dõi trạng thái trong CSV ứng viên

Mỗi văn bản đã xử lý trong lần tải thật được cập nhật ngay vào CSV được chọn bởi `--candidates` (mặc định `data/ung_vien_dan_su.csv`):

| Cột | Nội dung |
| --- | --- |
| `download_status` | `success`: đã tải/chuyển thành công hoặc file đã có khớp nguồn; `failed`: lỗi hoặc chưa xác minh được file trùng tên |
| `download_result` | Trạng thái chi tiết và lý do, ví dụ `converted`, `empty_or_invalid_html`, `skipped_unverified` |
| `download_path` | Đường dẫn kết quả hoặc đích dự kiến; với `failed`, file có thể không tồn tại |

ID chưa xử lý giữ nguyên giá trị cũ hoặc để trống. `--dry-run` không thêm cột hay ghi trạng thái. Lần chạy sau ghi kết quả mới nhất của ID được xử lý; trạng thái không tự loại ID khỏi lần tải sau. Chạy lại bộ lọc metadata giữ các cột này; `metadata.csv` không bị sửa. Không chạy đồng thời nhiều tiến trình cập nhật cùng CSV. Khi dừng giữa chừng, các kết quả đã ghi được giữ lại; ID chưa có kết quả không bị gán `failed`.

### Tham số terminal

| Tham số | Ý nghĩa |
| --- | --- |
| `--id ID [ID ...]` | Chọn một hoặc nhiều ID thuộc CSV ứng viên; không dùng cùng `--all-candidates` |
| `--all-candidates` | Xét các ID trong CSV ứng viên |
| `--limit N` | Giới hạn số văn bản chưa có được thử tải; N phải là số nguyên dương |
| `--output-dir PATH` | Thư mục kiểm tra trùng và lưu kết quả; mặc định `data` cạnh script |
| `--candidates PATH` | CSV ứng viên; mặc định `data/ung_vien_dan_su.csv` cạnh script |
| `--manifest PATH` | Manifest đối chiếu file có sẵn; mặc định `data/manifest.csv` tại gốc repo |
| `--manifest-root PATH` | Gốc tính `local_path` tương đối trong manifest; mặc định gốc repo |
| `--dry-run` | Lập kế hoạch offline, không tải/chuyển hoặc tạo file; có thể ghi kế hoạch nếu chỉ định `--report` |
| `--html-only` | Lưu `vbpl-<id>.html` và `vbpl-<id>.source.json`, bỏ chuyển DOCX |
| `--report PATH` | Ghi báo cáo JSON tổng tại đường dẫn mới; không ghi đè báo cáo đã có |
| `--open` | Mở đường dẫn DOCX/HTML vừa tạo qua trình duyệt hệ thống |

Ví dụ giữ HTML để kiểm tra hoặc gọi converter riêng:

```powershell
& $studyPython -u .\open_document.py --id 15289 --html-only --output-dir .\data
```

Streaming cần mạng và có thể đọc qua nhiều bản ghi trước khi gặp ID cần tìm. Terminal in thống kê và tối đa 20 dòng kết quả; dùng `--report` với tên file mới nếu cần lưu toàn bộ kết quả. `converted` là đã tạo DOCX; `downloaded` là đã lưu HTML; `would_download_and_convert` là dự kiến trong dry-run. `conversion_error`, `empty_or_invalid_html`, `not_found` và các lỗi nguồn/file cần được kiểm tra. Mã thoát 0 là không có trạng thái lỗi, vẫn có thể gồm file bỏ qua chưa xác minh; 1 là có lỗi xử lý, 2 là lỗi tham số/đầu vào. Kiểm tra nội dung và nguồn chính thức trước khi sử dụng tài liệu.

### HTML mẫu 111436

`data/vbpl-111436.html` là bản đọc trích từ lớp chữ của PDF văn bản hợp nhất `25/VBHN-BTC`, không phải HTML nguyên bản có toàn văn của dataset. File có các phần tương ứng 20 trang PDF.

```powershell
Invoke-Item .\data\vbpl-111436.html
```

Nguồn đối chiếu: [thông tin văn bản](https://vbpl-bientap-gateway.moj.gov.vn/api/qtdc/public/doc/111436) và [PDF nguồn](https://vbpl-bientap-gateway.moj.gov.vn/api/qtdc/public/doc/minio/buckets/vbpl/111436/25-VBHN-BTC_25-VBHN-BTC.pdf/download).

HTML nguồn đã kiểm tra của ID này có `body` rỗng. Bộ tải giữ nguyên mẫu đang có và báo `skipped_unverified` nếu chưa có bản ghi nguồn cùng dataset/revision. Khi tải vào một thư mục trống, HTML nguồn rỗng sẽ bị từ chối. Muốn có nội dung cần đối chiếu PDF/nguồn khác và ghi rõ việc chuyển đổi.

## Chuyển HTML sang DOCX

Bộ chuyển đổi nằm tại `backend/app/document_processing/html_to_docx.py`. Sau khi tải HTML, có thể gọi riêng từ thư mục nghiên cứu:

```powershell
& $studyPython -m pip install python-docx lxml
& $studyPython ..\..\backend\app\document_processing\html_to_docx.py .\data\vbpl-15289.html --document-number "100/2006/NĐ-CP" --output-dir ..\raw\case_moi
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
- Luồng mặc định chỉ giữ DOCX. Đối chiếu qua ID, dataset/revision trong CSV, số hiệu và manifest nếu có. --html-only là chế độ riêng để lưu HTML và .source.json.
- Các ca nguồn phục vụ dự án đặt trong `data/raw/<case_id>/`, cập nhật nguồn và thông tin file trong `data/manifest.csv`.
- Đáp án phân loại/trước–sau đã duyệt cần lưu riêng với nguồn dùng cho truy xuất.

## Kiểm thử bộ lọc và bộ tải

Chạy tại thư mục gốc repo bằng môi trường Python đang sử dụng:

```powershell
& $studyPython -B -m unittest discover -s test\data_suite -v
```

## Lỗi thường gặp

| Hiện tượng | Kiểm tra |
| --- | --- |
| Không tìm thấy `metadata.csv` | Chạy script tải metadata tại `legal-dataset-study`; kiểm tra file nằm trong thư mục con `data` |
| Môi trường `.venv` không chạy sau khi chuyển máy/thư mục | Tạo môi trường tại đường dẫn ngắn như $env:USERPROFILE\.venvs\pocs-study rồi cài thư viện |
| Tải toàn văn bị ngắt | Chạy lại cùng lựa chọn và đích. DOCX có sẵn được bỏ qua; khi chỉ có tên file, trạng thái là skipped_unverified. |
| Cảnh báo WinError 10038 sau khi báo `downloaded` | Chạy lại cùng ID và đích để kiểm tra file có sẵn. Hash cần manifest phù hợp; luồng DOCX-only không sinh bản ghi nguồn. |
| `existing_invalid` / `existing_identity_conflict` | Kiểm tra file cũ, hash, dataset và revision; bộ tải không tự sửa hoặc ghi đè |
| `empty_or_invalid_html` | Nguồn không có chữ đọc được; đối chiếu HTML/PDF chính thức thay vì tạo DOCX trắng |
| Không nhận diện được số ký hiệu khi chuyển DOCX | Bộ tải lấy so_ky_hieu từ CSV. Xác minh metadata nếu thiếu hoặc mâu thuẫn; --document-number chỉ dùng khi gọi converter thủ công. |
| Bộ lọc báo ứng viên không khớp metadata | Kiểm tra dataset, revision và giá trị gốc; không ghép hoặc ghi đè trước khi làm rõ |
