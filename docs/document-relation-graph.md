# Demo đồ thị quan hệ văn bản trên web

Đồ thị dựng quan hệ trực tiếp từ DOCX của nhóm theo BRD §8.7 và SRS §1.9.
Nút có ID nguồn, số hiệu, tên, trạng thái toàn văn và hash bản chụp khi có.
Các cạnh đi từ văn bản chứa chỉ dẫn hoặc dẫn chiếu tới văn bản được nhắc tới.
Mỗi cạnh giữ nguyên văn, vị trí block và phạm vi điều khoản khi quy tắc nhận ra.

## Dựng dữ liệu và mở demo tại cổng 8002

Từ gốc repo, chạy PowerShell với Python 3.11 trở lên.

```powershell
python -m pip install -r requirements-demo.txt
$run = 'runtime/lightrag/document-relation-graph'
python -m backend.document_graph_cli --mode corpus --output-dir $run
python -m backend.shared_demo --host 127.0.0.1 --port 8002
```

Mở [web demo](http://127.0.0.1:8002/). Mục **Đồ thị quan hệ văn bản pháp luật**
nằm trước form nộp S. **Toàn bộ đồ thị** vẽ mọi nút và cạnh bằng Canvas.
Lọc theo loại cạnh, kéo để di chuyển, dùng bản đồ nhỏ để chuyển vùng và **Vừa khung**
để trở lại toàn kho. Có thể mở toàn màn hình hoặc chọn văn bản từ kết quả tìm kiếm.
Khi khung vẽ có tiêu điểm, dùng phím mũi tên để di chuyển, phím cộng/trừ để thu phóng
và phím 0 để về vừa khung. Bộ lọc cạnh luôn giữ các nút văn bản.
Sau khi chọn, dùng **Xem bằng chứng quanh nút** để mở đồ thị lân cận. Tìm theo số hiệu hoặc tên, chọn kết quả và bấm nhãn cạnh
để mở nguyên văn cùng `document_id`, `block:N` và đường dẫn DOCX. Danh sách cạnh có
phân trang và ghi rõ chiều đi, đến. Văn bản đứng riêng vẫn được trả về khi tìm.

Lệnh dựng yêu cầu một thư mục đầu ra mới. Nếu dựng lại, chọn thư mục mới rồi
khởi động lại web với `--document-graph-file <thư-mục-mới>/document-graph.json`.
Khi thiếu file đồ thị, trang hiển thị trạng thái chưa dựng và vẫn cho nộp S.

- `document-graph.json` chứa nút, cạnh, số liệu và hash CSV đầu vào.
- `build-report.json` ghi số file đã đọc, cảnh báo Parser theo block, file
  không khớp danh mục, nhóm số hiệu mơ hồ và tham chiếu cần rà soát.

## Quy tắc định danh và giới hạn

- Chỉ đọc DOCX có đúng một dòng `success` trỏ tới file. Giữ nút riêng khi
  cùng số hiệu nhưng khác nội dung hoặc phiên bản báo cáo. Bản trùng hash, số
  hiệu và ngày ban hành được gộp, kèm danh sách ID/đường dẫn thay thế.
- Khi một số hiệu có nhiều ứng viên, giữ nguyên đoạn nguồn trong báo cáo rà
  soát. Khi ngoài danh mục hoặc thiếu DOCX, vẫn có thể ghi cạnh có căn cứ từ
  văn bản nguồn và tạo nút ghi rõ thiếu toàn văn.
- Năm loại cạnh là sửa đổi, bổ sung, bãi bỏ, dẫn chiếu và căn cứ. Kết quả do
  quy tắc nhận dạng từ chữ và cấu trúc hiện có. Các chỉ dẫn ghép, câu không
  đủ dấu hiệu và ranh giới trích dẫn chưa rõ cần kiểm tra thủ công. Hash chỉ
  xác định bản chụp file. Phiên bản pháp lý và hiệu lực cần đối chiếu riêng.

## Truy xuất LightRAG

Đồ thị văn bản dùng dữ liệu đã dựng sẵn. Để bật truy xuất cho web, thêm
`--provider-env-file <đường-dẫn-cấu-hình-local>` vào lệnh khởi động. Web giữ
phần bằng chứng LightRAG cho metadata mẫu và lượt đối chiếu.

Chế độ `--mode real` của CLI giữ bộ thử hai DOCX và ba đoạn trích, với kiểm
tra ID, nguyên văn và vị trí nguồn. Xem [lệnh chạy thật](document-graph-pilot.md#2-chạy-trên-máy-thành-viên)
và [cách cấu hình web dùng chung](shared-web-demo.md). Kết quả truy xuất thật
được lưu riêng với dữ liệu đồ thị. Cạnh ngữ nghĩa và phân tích tác động gián
tiếp thuộc phạm vi đợt sau.

## Kiểm tra tự động đồ thị trên GitHub

Workflow Project checks giữ job **Python tests**. Hai job bổ sung chạy cùng
workflow khi push hoặc mở PR hướng main.

- **Web demo checks** dựng đồ thị nhỏ từ DOCX thật, mở Chromium, kiểm tra Canvas
  có hình, lọc và tìm văn bản, đọc đúng block:22, rồi nộp S mẫu qua giao diện.
  Báo cáo ghi thời gian vẽ lần đầu. Khi lỗi, tải ảnh và trace từ tab Actions.
- **Corpus integrity** dựng lại toàn kho khi đổi dữ liệu, mã dựng đồ thị,
  giao diện hoặc CI. Job kiểm tra ánh xạ ID/đường dẫn, hash DOCX và nguyên văn
  cạnh. Với PR/push, job ghi file bị xóa và báo lỗi nếu bản ghi từng thành công
  bị hạ trạng thái. Phần hiệu năng xác nhận 120 lượt kéo/zoom mô phỏng dùng lại
  lớp đã vẽ. Báo cáo không đo tốc độ khung hình của trình duyệt.

Lượt LightRAG thật chạy riêng trong Actions → **LightRAG live pilot** → **Run workflow**.
Thiết lập secrets GROQ_API_KEY và JINA_API_KEY. Có thể đặt thêm các biến repository
GROQ_MODEL, JINA_EMBEDDING_MODEL và JINA_EMBEDDING_DIM nếu dùng model khác
cấu hình mẫu. Kết quả truy xuất thật nằm trong artifact lightrag-live-result.
