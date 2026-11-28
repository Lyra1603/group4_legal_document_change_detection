# Demo web dùng chung cho nhóm

## Phạm vi hiện tại

Một máy chủ chạy web/API. Thành viên mở cùng URL; không cần clone repo, Docker hoặc nhập khóa LightRAG hoặc khóa API nhà cung cấp để dùng demo. Backend tự sinh khóa server riêng và không trả khóa cho trình duyệt. LightRAG chỉ được publish trên loopback của máy chủ, không mở Web UI quản trị trực tiếp ra LAN.

Từ bản dựng đồ thị toàn kho, web có thêm mục [Đồ thị quan hệ văn bản pháp luật](document-relation-graph.md)
trước form nộp S. Hướng dẫn đó dùng cổng 8002 và có thể chạy khi chưa cấu hình LightRAG.

Các chức năng của web chung:
- Nộp văn bản sửa đổi S để tìm từng văn bản gốc theo số hiệu trong chỉ dẫn. Hệ thống tự dùng V1 cho đúng cặp mẫu `case_02` đã kiểm chứng. Với các bản trong danh mục nguồn chưa xác minh phiên bản, người dùng chọn ứng viên. Nếu thiếu V1, web yêu cầu bổ sung theo từng đích. Các tài liệu tham chiếu là tùy chọn.
- Từng đích có V1 được đối chiếu qua Reader/Parser → Adapter/Linker → Text Diff song song chuẩn bị chỉ mục → truy xuất Context → Semantic/Scorer quy tắc → báo cáo. Đích thiếu nguồn vẫn hiện chỉ dẫn và lý do. Trường hợp chưa đủ căn cứ phân tách một chỉ dẫn có nhiều số hiệu được giữ để kiểm tra.
- Index/query và xem bằng chứng, nguồn thực thể và liên hệ LightRAG thực tế trên hai bản ghi metadata Bộ luật Dân sự 2005/2015, ID `18128`, `95942`, dataset `th1nhng0/vietnamese-legal-documents`, revision `8977887f17be2defae4c5171d55562e1cde7d695`. Đây là metadata có sẵn trong main, không phải toàn văn/đáp án và chưa được xác minh tình trạng hiệu lực hiện tại. Quan hệ graph do model trích xuất chưa phải căn cứ pháp lý.

Không thay schema/validator hoặc payload ComparisonReport. API phụ trợ chỉ dành cho demo, không phải hợp đồng báo cáo cấp S đã chốt.

## Chuẩn bị một lần trên máy chủ

Cài Python và Docker Desktop. Từ gốc repo:

```powershell
python -m pip install -r requirements-demo.txt
docker build -t pocs-lightrag:28ff1b05 https://github.com/HKUDS/LightRAG.git#28ff1b05f2ac3f3e6fa14dd2cd33656579bd0c9c
Copy-Item deploy/lightrag/context-provider.env.example deploy/lightrag/.env.groq-jina
```

Quản trị dùng [Groq Free](https://console.groq.com/keys) cho trích xuất thực thể, quan hệ và từ khóa. Dùng [Jina Embeddings](https://jina.ai/api-dashboard/key-manager) cho các vector tìm kiếm. Điền `GROQ_API_KEY` và `JINA_API_KEY` vào `.env.groq-jina` trên máy chủ. Git bỏ qua file này. Thành viên sử dụng qua web.

Mẫu cấu hình chọn Qwen 3.8 27B qua Groq và jina-embeddings-v4 (2048 chiều). Kiểm tra đúng model, hạn mức và số dư thử nghiệm trong bảng điều khiển của hai dịch vụ. Có thể chọn lại Gemini hoặc OpenAI bằng cấu hình rõ ràng. Chỉ mục được dựng mới cho mỗi instance và dùng cùng một model embedding khi nạp và truy vấn.

Kiểm tra kết nối bằng hai yêu cầu nhỏ với dữ liệu giả định trước khi chạy web:

```powershell
python -m backend.shared_demo --provider-env-file deploy/lightrag/.env.groq-jina --check-providers
```

Cả Groq và Jina cần trả về OK. Lệnh kiểm tra nội dung JSON từ Groq và độ dài vector Jina. Lệnh chỉ in trạng thái, mã HTTP và số chiều nếu đạt.

Chế độ Groq–Jina dành cho kho demo nhỏ. Mỗi lượt lập chỉ mục nhận tối đa 12 đoạn, 2500 ký tự nguồn mỗi đoạn. Các block liền nhau trong cùng văn bản được gộp khi nằm trong giới hạn. Trích dẫn vẫn lưu tất cả vị trí nguồn của đoạn. LightRAG xử lý tuần tự, giới hạn đầu ra 1024 token mỗi lần gọi Groq và tắt lượt trích xuất bổ sung. Đây là giới hạn khối lượng thử nghiệm. Hạn mức thực tế vẫn do nhà cung cấp quyết định. Khi vượt giới hạn đầu vào, backend giữ Text Diff và báo INDEX_INPUT_INVALID. Chỉ sử dụng văn bản công khai được phép gửi cho hai nhà cung cấp khi chạy demo này.

## Khởi động bằng một lệnh

```powershell
python -m backend.shared_demo --provider-env-file deploy/lightrag/.env.groq-jina --host 0.0.0.0 --port 8000
```

Máy chủ mở `http://127.0.0.1:8000`. Thành viên cùng LAN mở `http://<IP-máy-chủ>:8000`; nếu firewall chặn thì quản trị cho phép đúng cổng trên mạng của nhóm. Không tự public lên Internet. Chạy đúng **một process/worker**, không dùng reload hoặc nhiều worker vì lock, nguồn và kết quả demo được giữ trong process này. Chỉ tiến trình chủ cần Docker và provider credentials.

Web/API khởi động trước; LightRAG instance được tạo khi nạp kho hoặc chạy đối chiếu. Nếu image/Docker/provider thiếu, web vẫn mở và báo lỗi, không thay bằng mock. Cấu hình model chỉ được áp dụng lại sau khi khởi động lại lệnh trên.

## Thao tác và kết quả

1. Mở web, không có hộp nhập API key.
2. Bấm **Index metadata thật** một lần. Trạng thái đi từ IDLE → INDEXING → READY hoặc FAILED. Trang tự cập nhật, có thể dùng nút cập nhật thủ công. READY chỉ sau khi upstream xác nhận các bản ghi processed và graph hợp lệ.
3. Khi READY, nhập câu hỏi và bấm **Truy xuất thật**. Xem quote nguyên văn cùng document_id/source_refs và ID dataset/revision. Mở mục nguồn thực thể và liên hệ LightRAG để kiểm tra thông tin trích xuất.
4. Chọn S hoặc nạp S của mẫu Ngân hàng, rồi bấm **Tìm văn bản gốc**. Với các đích khác, chọn bản ứng viên hoặc bổ sung file V1 đúng số hiệu. Nếu đã có cả hai file, dùng **Tôi có sẵn V1**. Khi xong, báo cáo giữ nguyên và có phần **LightRAG của lượt đối chiếu**: trạng thái, context, bằng chứng và nguồn liên hệ LightRAG. Index chỉ gồm toàn bộ block được trích làm bằng chứng chỉ dẫn/đích và các block tham chiếu đã nộp. Có cảnh báo RETRIEVAL_SCOPE_LIMITED; đây chưa phải kho toàn văn hoặc chứng nhận đủ context.
5. Khi provider lỗi/thiếu cấu hình, Text Diff vẫn được giữ nếu xử lý nguồn thành công; báo cáo PARTIAL và mã lỗi cụ thể. Không tự chuyển lỗi retrieval thành “không thay đổi”. Semantic/Scorer vẫn giữ null/review khi thiếu căn cứ.

PDF phụ thuộc bộ chuyển đổi; DOCX là đường chạy đã kiểm thử. Bước tìm V1 đối chiếu số hiệu chính xác với các bản BASE có file và checksum hợp lệ trong danh mục. Tìm số hiệu không gọi Groq/Jina. Hệ thống chưa tìm ngoài kho, chưa suy ra lịch sử hiệu lực và chưa tự chọn bản mới nhất.

## Vòng đời và đồng thời

- Một lock giới hạn một thao tác provider tại một thời điểm (index/query/đối chiếu). Lượt khác nhận DEMO_BUSY; không tự nạp trùng hoặc xếp hàng ẩn.
- Kho metadata dùng instance riêng, giữ tới khi tắt web. Sau lỗi index, không tự replay hoặc thay kho đang lỗi; quản trị kiểm tra cấu hình và khởi động lại web để có instance sạch.
- Mỗi đối chiếu dùng instance/ledger khác; cleanup chỉ tài nguyên được gắn nhãn sở hữu của chính lượt đó. Không dùng cleanup comparison để xóa kho metadata.
- Khi tắt bằng Ctrl+C, chờ thao tác đang chạy và cleanup đúng instance kho metadata. Dữ liệu runtime và khóa tạm bị Git bỏ qua. Nếu mất điện/kill process, quản trị kiểm tra các container mang nhãn `pocs.context.session`; không chạy purge toàn Docker.
- Giữ tối đa 10 context gần nhất trong bộ nhớ dùng chung của nhóm; restart xóa cache. Đây là demo chung, chưa có tài khoản/phân quyền cá nhân, lịch sử bền vững hoặc hủy tác vụ.

## API phụ trợ (trình duyệt không gửi khóa upstream)

| Route | Vai trò |
| --- | --- |
| GET /health, GET /api/demo/config | Cấu hình công khai, tách configured khỏi ready |
| POST /api/demo/corpus/index | Nạp bộ metadata cố định, không nhận đường dẫn tùy ý |
| GET /api/demo/corpus | Trạng thái, nguồn và graph đã quan sát |
| POST /api/demo/corpus/query | Câu hỏi dài 1–8000 ký tự, chỉ query sau READY |
| GET /api/demo/contexts/{comparison_id} | Context/graph phụ trợ của lượt so sánh đã trả về |
| POST /api/demo/targets | Nhận S, trả nhóm đích, ứng viên và chỉ dẫn còn thiếu căn cứ |
| GET /api/demo/targets/candidates/{candidate_id} | Tải bản trong danh mục đã kiểm checksum |
| POST /api/demo/targets/verify-v1 | Kiểm tra số hiệu của V1 được chọn trước khi đối chiếu |
| POST /api/compare | Payload và ComparisonReport cho một V1–S hiện có, không đổi |

## Kiểm chứng và giới hạn nghiệm thu

`test/context_suite/test_shared_demo.py` kiểm tra HTTP/DOCX, key không vào browser, nguồn thật từ CSV, từ chối sai nguồn, retrieval rỗng, thiếu cấu hình, busy, cleanup comparison không xóa corpus và graph có mapping. Các ca này dùng HTTP double có nhãn, **không tính là LightRAG thật**.

```powershell
python -m unittest discover -s test/context_suite -v
python -m unittest discover -s test/demo_suite -v
```

Bằng chứng live cũ tại `data/demo-results/context-handoff-synthetic-live.json` là dữ liệu giả định ngày 22/11, không thay cho chạy metadata thật. Lượt metadata ngày 23/11 trước bổ sung web chung gặp Gemini `503 UNAVAILABLE`, không có graph (0 node, 0 cạnh). Kết quả kiểm chứng web chung mới cần ghi riêng theo lượt chạy; lỗi provider còn tồn tại thì chưa nghiệm thu demo retrieval/graph thật.

Kiểm chứng Groq–Jina qua web bằng bộ metadata thật trên, sau đó chạy ca DOCX cặp V1–S. Chỉ ghi nhận nghiệm thu khi kho READY, truy vấn trả bằng chứng đúng nguồn và graph có node/cạnh thực tế. Với ca DOCX, kiểm tra cảnh báo, Text Diff và artifact Context chuyển vào Semantic. Ghi định danh nguồn và kết quả thực tế, tách khỏi kết quả kiểm thử mô phỏng.

Kết quả chạy thật qua API web ngày 24/11/2026 với Groq Qwen 3.8 27B và Jina Embeddings v4:

- Hai bản ghi 18128 và 95942 đều lập chỉ mục thành công. Truy vấn về 91/2015/QH13 trả hai bằng chứng metadata, gồm bản ghi 95942. Graph có 9 nút, 9 cạnh và tất cả có vị trí nguồn. Lượt này từng báo CLEANUP_PENDING khi tắt kho.
- Ca DOCX case_02 với Thông tư 22/2019/TT-NHNN và 08/2020/TT-NHNN dùng 11 block nguồn liền nhau, được tổ chức thành hai đoạn. Báo cáo có một Text Diff. Context READY trả một bằng chứng đã đối chiếu nguyên văn và sáu vị trí trong S. Graph có 10 nút, 9 cạnh, đều liên kết được đến nguồn. Lượt này không báo lỗi Context hay cleanup.
- Báo cáo nghiệp vụ vẫn PARTIAL vì Semantic/Scorer đang ở chế độ quy tắc cục bộ. Hai ca trên kiểm chứng đường nối LightRAG, chưa đo độ bao phủ hoặc chất lượng pháp lý trên toàn kho.

Trước khi gộp đoạn, cả Qwen và GPT-OSS 20B qua Groq Free đều gặp lỗi 429 trên ca DOCX này. Nhóm cần giữ cấu hình trong hạn mức thực tế của tài khoản và theo dõi mã INDEX_PROVIDER_RATE_LIMITED khi thử ca lớn hơn.

### Kiểm thử luồng nộp S

- case_02 tự nạp bản V1 đã ghim theo checksum và chạy đối chiếu.
- case_10 nhận diện hai đích. 05/2011/TT-BTP có bản ứng viên cần xác nhận. 22/2010/TT-BTP yêu cầu bổ sung V1. Kết quả cho đích có nguồn được giữ khi đích kia còn thiếu.
- Với khoản dài, câu truy xuất dùng các đoạn sát vị trí thay đổi. Bước Semantic vẫn nhận Text Diff đầy đủ. Đồ thị ẩn nút/cạnh thiếu nguồn và ghi số lượng hoặc lý do trong phần kiểm tra nguồn.
