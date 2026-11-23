# Demo web dùng chung cho nhóm

## Phạm vi hiện tại

Một máy chủ chạy web/API. Thành viên mở cùng URL; không cần clone repo, Docker hoặc nhập khóa LightRAG/Gemini để dùng demo. Backend tự sinh khóa server riêng và không trả khóa cho trình duyệt. LightRAG chỉ được publish trên loopback của máy chủ, không mở Web UI quản trị trực tiếp ra LAN.

Web chung có hai phần:
- Đối chiếu DOCX V1 + S và tài liệu tham chiếu tùy chọn. Reader/Parser → Adapter/Linker → Text Diff song song chuẩn bị index → truy xuất context → Semantic/Scorer baseline → báo cáo hiện có. Chưa có Semantic LLM hoặc tìm V1 tự động từ S; không tuyên bố hoàn thành hai chức năng đó.
- Index/query và xem graph LightRAG thực tế trên hai bản ghi metadata Bộ luật Dân sự 2005/2015, ID `18128`, `95942`, dataset `th1nhng0/vietnamese-legal-documents`, revision `8977887f17be2defae4c5171d55562e1cde7d695`. Đây là metadata có sẵn trong main, không phải toàn văn/đáp án và chưa được xác minh tình trạng hiệu lực hiện tại. Quan hệ graph do model trích xuất chưa phải căn cứ pháp lý.

Không thay schema/validator hoặc payload ComparisonReport. API phụ trợ chỉ dành cho demo, không phải hợp đồng báo cáo cấp S đã chốt.

## Chuẩn bị một lần trên máy chủ

Cài Python và Docker Desktop. Từ gốc repo:

```powershell
python -m pip install -r requirements-demo.txt
docker build -t pocs-lightrag:28ff1b05 https://github.com/HKUDS/LightRAG.git#28ff1b05f2ac3f3e6fa14dd2cd33656579bd0c9c
Copy-Item deploy/lightrag/context-provider.env.example deploy/lightrag/.env.shared
```

Quản trị điền provider key/model/embedding vào `.env.shared` bị Git bỏ qua, chỉ trên máy chủ. Không gửi file này cho thành viên hoặc commit key. Đổi key trong cùng Gemini project không giải quyết được quyền Free tier unavailable; tài khoản/model cần được phép gọi cả generation và embedding. Nâng billing là quyết định riêng của chủ tài khoản.

## Khởi động bằng một lệnh

```powershell
python -m backend.shared_demo --provider-env-file deploy/lightrag/.env.shared --host 0.0.0.0 --port 8000
```

Máy chủ mở `http://127.0.0.1:8000`. Thành viên cùng LAN mở `http://<IP-máy-chủ>:8000`; nếu firewall chặn thì quản trị cho phép đúng cổng trên mạng của nhóm. Không tự public lên Internet. Chạy đúng **một process/worker**, không dùng reload hoặc nhiều worker vì lock, nguồn và kết quả demo được giữ trong process này. Chỉ tiến trình chủ cần Docker và provider credentials.

Web/API khởi động trước; LightRAG instance được tạo khi nạp kho hoặc chạy đối chiếu. Nếu image/Docker/provider thiếu, web vẫn mở và báo lỗi, không thay bằng mock. Cấu hình model chỉ được áp dụng lại sau khi khởi động lại lệnh trên.

## Thao tác và kết quả

1. Mở web, không có hộp nhập API key.
2. Bấm **Index metadata thật** một lần. Trạng thái đi từ IDLE → INDEXING → READY hoặc FAILED. Trang tự cập nhật, có thể dùng nút cập nhật thủ công. READY chỉ sau khi upstream xác nhận các bản ghi processed và graph hợp lệ.
3. Khi READY, nhập câu hỏi và bấm **Truy xuất thật**. Xem quote nguyên văn cùng document_id/source_refs, ID dataset/revision và graph. Mở node/cạnh để đọc nguồn. Graph rỗng được hiển thị là rỗng; không dựng graph giả để thay thế.
4. Phần đối chiếu dùng file DOCX thật hoặc bộ mẫu trong data/raw. Khi xong, báo cáo giữ nguyên và có phần **LightRAG của lượt đối chiếu**: trạng thái, context, bằng chứng và graph. Index chỉ gồm toàn bộ block được trích làm bằng chứng chỉ dẫn/đích và các block tham chiếu đã nộp. Có cảnh báo RETRIEVAL_SCOPE_LIMITED; đây chưa phải kho toàn văn hoặc chứng nhận đủ context.
5. Khi provider lỗi/thiếu cấu hình, Text Diff vẫn được giữ nếu xử lý nguồn thành công; báo cáo PARTIAL và mã lỗi cụ thể. Không tự chuyển lỗi retrieval thành “không thay đổi”. Semantic/Scorer vẫn giữ null/review khi thiếu căn cứ.

PDF phụ thuộc bộ chuyển đổi; DOCX là đường chạy đã kiểm thử. Chỉ nộp S chưa được API này hỗ trợ; giao diện không giả vờ đã tự tìm V1.

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
| POST /api/compare | Payload và ComparisonReport hiện có, không đổi |

## Kiểm chứng và giới hạn nghiệm thu

`test/context_suite/test_shared_demo.py` kiểm tra HTTP/DOCX, key không vào browser, nguồn thật từ CSV, từ chối sai nguồn, retrieval rỗng, thiếu cấu hình, busy, cleanup comparison không xóa corpus và graph có mapping. Các ca này dùng HTTP double có nhãn, **không tính là LightRAG thật**.

```powershell
python -m unittest discover -s test/context_suite -v
python -m unittest discover -s test/demo_suite -v
```

Bằng chứng live cũ tại `data/demo-results/context-handoff-synthetic-live.json` là dữ liệu giả định ngày 22/11, không thay cho chạy metadata thật. Lượt metadata ngày 23/11 trước bổ sung web chung gặp Gemini `503 UNAVAILABLE`, không có graph (0 node, 0 cạnh). Kết quả kiểm chứng web chung mới cần ghi riêng theo lượt chạy; lỗi provider còn tồn tại thì chưa nghiệm thu demo retrieval/graph thật.
