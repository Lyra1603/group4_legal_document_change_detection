# Demo Docker · đồ thị văn bản từ kho DOCX

Demo dòng lệnh dùng hai DOCX trong kho ứng viên Dũng bàn giao qua PR #18. Mỗi file được đọc toàn bộ để dò quan hệ. LightRAG chỉ lập chỉ mục **ba đoạn trích từ hai DOCX**, theo danh sách được ghim trong [cấu hình bộ thử](../data/legal-dataset-study/document-graph-pilot.json).

| Dataset ID | Văn bản | Đoạn được đưa vào LightRAG |
| --- | --- | --- |
| `26170` | Thông tư `05/2011/TT-BTP` | `block:11` |
| `56666` | Thông tư `08/2014/TT-BTP` | `block:21`, `block:22` được gộp, cùng `block:167` |

## 1. Đồ thị và nguồn

- Đồ thị của dự án dùng ID theo bản ghi dataset. Nút giữ số hiệu, tên, nguồn, ngày theo metadata khi có và SHA-256 của DOCX đã đọc. SHA-256 xác định file cụ thể. Phiên bản pháp lý có hiệu lực còn cần đối chiếu.
- Cạnh đi từ **văn bản chứa chỉ dẫn hoặc lời dẫn** sang **văn bản được nhắc tới**. Gồm `AMENDS` (sửa đổi), `SUPPLEMENTS` (bổ sung), `REPEALS` (bãi bỏ), `CITES` (dẫn chiếu) và `BASIS` (căn cứ). Mỗi cạnh có đoạn trích nguyên văn và vị trí `block:N`. Khi chỉ dẫn con kế thừa đích từ đầu Điều, giữ cả hai đoạn. Phạm vi Điều/Khoản/Điểm lưu dưới dạng cụm từ trong nguồn.
- `AVAILABLE_IN_PILOT` là đã đọc toàn bộ DOCX trong bộ thử. `AVAILABLE_OUTSIDE_PILOT` là có file trong kho chung nhưng chưa được đọc trong lượt thử. `MISSING_FULL_TEXT` là kho ứng viên hiện tại chưa có file đã xác định cho đích. Trường tên, nguồn gốc đích hoặc phiên bản chưa biết được giữ là `null`. Có nhiều bản ghi trùng số hiệu hoặc chỉ dẫn ghép nhiều hành động thì ghi `needs_review` cùng căn cứ.
- Cạnh dẫn chiếu hoặc căn cứ thể hiện cách nguồn nhắc tới văn bản khác. Trạng thái hiệu lực và tác động pháp lý cần kiểm tra riêng.

| Đầu ra | Phần tạo kết quả |
| --- | --- |
| `document-graph.json` | Dự án đọc DOCX, đối chiếu số hiệu với CSV, dựng nút/cạnh, ghi đề mục cần rà soát và xuất ánh xạ `file_source → document_id → source_refs` |
| `lightrag-live.json` | LightRAG Server trả trạng thái lập chỉ mục, kết quả truy xuất và đồ thị trích xuất. Dự án xác minh trích dẫn với registry và ghi kết quả dọn tài nguyên |

Đồ thị trích xuất của máy chủ có thể có cả tổ chức, điều khoản và các thực thể khác. Khi đọc nó, tra `file_path` trong `lightrag_source_map` để về đúng file và vị trí. Dự án giữ đồ thị văn bản riêng và không đưa các cạnh do mô hình sinh thẳng vào đó. Phiên bản máy chủ ghim tại [manifest upstream](../deploy/lightrag/upstream-manifest.json). Các bước kiểm tra sử dụng HTTP client có sẵn và API gốc của máy chủ.

## 2. Chạy trên máy thành viên

Chạy từ gốc repo. Cài Python 3.11 trở lên và bật Docker Desktop hoặc Docker Engine trước.

```powershell
python -m pip install -r requirements-demo.txt
docker build -t pocs-lightrag:28ff1b05 https://github.com/HKUDS/LightRAG.git#28ff1b05f2ac3f3e6fa14dd2cd33656579bd0c9c
```

Nếu chỉ muốn xem đồ thị văn bản và kiểm tra dữ liệu nguồn, có thể xuất JSON ngay. Chế độ này chạy bằng Python và không gọi dịch vụ AI.

```powershell
$run = 'runtime/lightrag/document-graph-offline-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
python -m backend.document_graph_cli --output-dir $run
```

Để chạy dịch vụ thật, tạo tệp cấu hình riêng từ mẫu nếu chưa có.

```powershell
Copy-Item deploy/lightrag/context-provider.env.example deploy/lightrag/.env.graph-pilot
```

Mở `.env.graph-pilot` và điền hai khóa Groq/Jina của người chạy vào `GROQ_API_KEY` và `JINA_API_KEY`. Git bỏ qua tệp này. Sau đó chạy:

```powershell
$run = 'runtime/lightrag/document-graph-live-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
python -m backend.document_graph_cli --mode real `
  --provider-env-file deploy/lightrag/.env.graph-pilot --output-dir $run
```

Lệnh mở một container riêng chỉ nghe nội bộ, nạp đoạn trích, chờ chỉ mục sẵn sàng, gửi một truy vấn thật rồi dọn container. Mỗi lần chạy dùng thư mục kết quả mới. Nếu lỗi provider, xem `failure`, `retrieval.issues` và `cleanup_issues` trong JSON. Chế độ `real` luôn gọi máy chủ thật.

## 3. Kiểm tra và bàn giao kết quả

1. Trong `document-graph.json`, mở `files` để xem danh mục đã đọc và `nodes` để xem nguồn đủ/thiếu. Mở cạnh từ Thông tư 08/2014 sang 05/2011 và tra `block:22` cùng `block:21` trong DOCX nguồn.
2. Trong `lightrag-live.json`, kiểm tra `index_ready`, `expected_evidence_found`, `verified` và `cleanup_issues`. Kỳ vọng tìm được chỉ dẫn sửa khoản 2 Điều 2 từ `dataset:56666`, `block:22`. Dùng `indexed_documents` và `lightrag_source_map` để lần theo ID máy chủ về DOCX gốc.
3. Khi một thành viên chạy lại, bàn giao tên máy hoặc môi trường, kết quả JSON, thời gian chạy và mã lỗi nếu có. [Bằng chứng chạy thật đã ghi nhận](../data/demo-results/document-graph-pilot-live.json) là lượt trên máy tích hợp. Lượt trên máy thành viên cần ghi riêng.

Bộ thử ưu tiên khả năng truy vết một quan hệ trên tài liệu thật. Kho 409 DOCX, chất lượng truy xuất trên toàn kho và giao diện đồ thị là các bước mở rộng sau khi rà dữ liệu nguồn.
