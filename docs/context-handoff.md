# Context/LightRAG — bàn giao và chạy kiểm chứng

## Phạm vi

Bản làm việc `ducanh/context-integration`, nền main `161e601` sau PR #11. Chưa commit/push trong đợt triển khai này. Không nhập code Explorer chưa commit từ nhánh riêng và không thay API/schema/validator cũ. Tài liệu này hướng dẫn điểm nối Context, không phải bảng giao việc.

Đã có bộ nhận dữ liệu ca nguồn, runner Context và CLI chạy một LightRAG Server thật qua HTTP trong container riêng. Tái sử dụng client, registry, chunk builder và điểm ghép query từ PR #7. Không làm thay Parser, tìm V1, dựng trước/sau, Semantic hoặc Scorer. CLI chỉ chạy sau khi đã có AmendmentItem và V1 được giải quyết; không phải endpoint chỉ S.

## Đầu vào và đầu ra

[Ca giả định](../test/fixtures/context_cases/synthetic_civil.json) là mẫu `pocs-context-case-v1` do dự án tự tạo; KHÔNG phải ca lấy từ hai dataset hoặc văn bản pháp luật thật.

| Trường | Ý nghĩa |
| --- | --- |
| format, case_id, snapshot_id | Phiên bản điểm nối nội bộ, mã ca và phiên bản bộ nguồn |
| source_kind | SYNTHETIC, LOCAL_UNREVIEWED, DATASET_UNREVIEWED hoặc DATASET_REVIEWED; là nhãn của bên giao, không tự chứng minh pháp lý đúng |
| documents | Danh sách ExtractedDocument hiện có, giữ nguyên block/text/source_ref; v1/BASE, s/AMENDMENT, ref_*/REFERENCE |
| provenance | Theo ID cục bộ: source_identity, version_id, content_sha256 và unit_paths cho mọi block. Không dùng filename làm định danh |
| dataset, dataset_id, revision, source_url | Với nguồn dataset, ghi tên đầy đủ và commit 40 ký tự; không dùng main/latest. Hai nguồn ID giống nhau chưa phải cùng văn bản |
| origin=UPLOAD | Nguồn tải lên có thể đi cùng V1 từ dataset; không gán nguồn tải lên thành bản ghi dataset |
| amendment | AmendmentItem có trước/sau đủ căn cứ; trước có bằng chứng V1; QUOTED phải có nguyên văn S. Không tự dựng khi thiếu V1 |
| candidate_query | Tùy chọn, truy xuất ứng viên B; không xác nhận tác động |

Hai dataset được chấp nhận là th1nhng0/vietnamese-legal-documents (chính) và vohuutridung/vietnamese-legal-documents (bổ sung). Chưa tự tải hoặc trộn dataset. Thọ cần bàn giao nguồn/phiên bản đã xác minh, cùng adapter nội dung HTML/Markdown sang blocks; không giả DOCX để qua kiểm tra. Kiểu file/source locator từ dataset phải được review với hợp đồng nguồn hiện có trước khi nối toàn Pipeline.

`ContextCase.from_dict()` kiểm tra ID/phiên bản, digest nguyên văn, vai trò, vị trí và bằng chứng. `content_digest(document)` tính SHA-256 trên JSON canonical của blocks (UTF-8, sort_keys, separators không khoảng trắng). Nhãn version là căn cước bên giao cung cấp; code không tự xác minh hiệu lực pháp lý.

`run_case(case, client, registry)` trả:
- TextDiffResult dùng tạo query; context trước/sau retrieval và ProcessingIssue tương ứng.
- source_trace: EvidenceRef + định danh nguồn/phiên bản, dataset/revision và vị trí. Không dùng entity description hoặc câu trả lời LLM làm quote.
- Ứng viên B có evidence đã đối chiếu, luôn legal_impact_confirmed=false.
- Chỉ số thời gian, graph nguồn dự án và nhãn giới hạn; CLI real thêm KG trích xuất thật và audit metadata của graph.

Mỗi block là một chunk. Quá giới hạn số lượng/độ dài thì từ chối, không âm thầm cắt. Không thay đổi ReferenceRequirement thành AVAILABLE chỉ vì retrieval thành công, không xác nhận context đầy đủ hay bật chấm mức độ.

## Chạy kiểm thử độc lập

Từ repo root, dùng Python đã cài `requirements-demo.txt`:

```powershell
python -m unittest discover -s test/context_suite -v
python -m backend.context_cli --mode contract --input test/fixtures/context_cases/synthetic_civil.json --output runtime/lightrag/context-contract.json
```

Contract mode dùng HTTP double có nhãn, không phải LightRAG. Real mode không tự fallback sang double.

## Chạy LightRAG thật

Cần Docker Desktop, image upstream đã ghim và key/model được phép sử dụng. Mỗi lần chạy sinh container, workspace, endpoint, storage và ledger mới. Không gắn volume hoặc endpoint kho dùng chung.

Nếu chưa có image, build upstream nguyên bản (cần mạng và có thể mất thời gian):

```powershell
docker build -t pocs-lightrag:28ff1b05 https://github.com/HKUDS/LightRAG.git#28ff1b05f2ac3f3e6fa14dd2cd33656579bd0c9c
Copy-Item deploy/lightrag/context-provider.env.example deploy/lightrag/.env.context
```

Điền cấu hình vào `.env.context` đã được Git bỏ qua. Mẫu hỗ trợ native Gemini hoặc OpenAI của upstream; model ví dụ không phải quyết định chung của nhóm. Không gửi key vào chat hoặc commit. Khi chạy real, nội dung ca được gửi cho provider đã cấu hình và có thể phát sinh quota/chi phí.

```powershell
python -m backend.context_cli --mode real --input test/fixtures/context_cases/synthetic_civil.json --provider-env-file deploy/lightrag/.env.context --output runtime/lightrag/context-live.json --budget 600
```

Một đến ba query ngữ cảnh có thể chọn bằng --repeats (mặc định 1). Chỉ chạy thêm khi cần đánh giá độ ổn định, không tự tăng lượt gọi model.

Khi ghép runner, bên Pipeline quản lý một client/registry trong phạm vi comparison và cleanup trong finally; không tạo client mới cho từng item. Input mới phải qua ContextCase/registry trước khi nhập. Xem `backend/context_cli.py` về lifecycle; không dùng test double ở runner thật.

## Lỗi và vòng đời

- Index chưa sẵn sàng, sai nguồn/phiên bản, retrieval rỗng hoặc lỗi đều giữ lý do; không chuyển thành không có tài liệu/thay đổi.
- Timeout được giữ là RETRIEVAL_TIMEOUT. GET và POST /query/data chỉ đọc được retry tối đa một lần với lỗi tạm thời; không tự replay nhập/xóa sau ACK không rõ.
- Chỉ xóa doc IDs trong ledger của client đã dành server riêng. Không gọi purge/global delete.
- Chỉ stop/rm container khi ownership label khớp đúng UUID. Lỗi HTTP cleanup vẫn cố dừng đúng container sở hữu; không thao tác dịch vụ khác.
- Storage/ledger demo giữ ở runtime/lightrag để audit, được Git bỏ qua. Không coi giữ storage này là đã có kho dùng chung bền vững. Không tự dùng lại endpoint/ledger cũ.
- Khóa chỉ được ghi vào file env tạm cho Docker rồi xóa file đó; Docker vẫn giữ environment của container tới khi container được xóa. Không xuất key ra report/log của ứng dụng.

## Bằng chứng chạy thật ngày 22/11/2026

[Báo cáo lưu](../data/demo-results/context-handoff-synthetic-live.json) là REAL_LIGHTRAG_HTTP trên dữ liệu SYNTHETIC; không phải mock và không phải ca pháp luật thật.

| Nội dung | Quan sát |
| --- | --- |
| Upstream | v1.5.7, commit 28ff1b05f2ac3f3e6fa14dd2cd33656579bd0c9c; image ID ghi trong report |
| Provider local | Native Gemini, model và embedding thực tế ghi trong report; chưa chọn thay nhóm |
| Nguồn | Ba tài liệu giả định V1, S, B; cùng filename để kiểm chứng định danh độc lập |
| Index | Khoảng 11,7 giây ở lượt thành công |
| Query ngữ cảnh | Khoảng 2,0 giây; 3 bằng chứng có mapping nguồn, không có issue |
| Query ứng viên B | Có ref_1 trong kết quả, đồng thời có V1/S; không tính tất cả kết quả là B chịu tác động |
| KG thực tế | 5 node, 3 cạnh. Audit phát hiện node nhãn Điều 1 gắn nguồn ở nhiều tài liệu; ghi là khả năng gộp, không dùng node đó làm căn cước điều khoản |
| Cleanup | Không có issue; container dành riêng được dừng/xóa. Chưa kiểm chứng hai server thật đồng thời trong đợt này |
| Lượt đầu | Context thành công nhưng query B gặp lỗi dịch vụ HTTP; report có ghi nhận lượt lỗi. Lượt sau chạy lại thành công sau bổ sung retry query giới hạn |

Graph nguồn của dự án giữ định danh document/role/version riêng. KG upstream có thể gộp tên giống nhau hoặc trích sai loại entity; audit KHÔNG sửa hoặc xác nhận các quan hệ pháp lý. Graph_source_audit trong artifact được tính từ raw graph đã lưu, không phải một lượt gọi provider mới.

Bật/tắt retrieval trên cùng nguồn được lưu trong disabled/enabled: bản tắt không có evidence bổ sung; bản bật có evidence đã kiểm tra. Có thời gian và tùy chọn lặp, chưa đo độ chính xác pháp lý, chưa có gold hoặc ngưỡng nghiệm thu. Không lấy ba bằng chứng/ca giả định làm kết luận về chất lượng RAG trên dataset dân sự.

## Đề xuất báo cáo cấp S cần review

[Fixture đề xuất](../test/fixtures/context_cases/analysis_report_draft.json) có nhãn DRAFT, không được API nhập hoặc trả như hợp đồng chính thức. Bao analysis_id, corpus_snapshot_id/coverage, targets, unresolved_amendments, indirect_impacts và trạng thái/lỗi theo SRS §1.8. Mỗi target giữ ComparisonReport hiện có và source_bindings từ ID cục bộ về nguồn/phiên bản thật. Báo cáo cục bộ qua validator hiện có; lớp bao chưa có validator chính thức.

Dũng/Đức Anh/Tuấn Anh cần chốt kiểu dữ liệu đầy đủ, bằng chứng khi thiếu V1, mapping xuyên đích, trạng thái và định nghĩa kết quả hữu ích trước khi nối API/UI. Không thêm trường hoặc sửa nghĩa contract cũ trong đợt này.

## Phần còn chờ

- Tại ngày 23/11, PR #12 của Thọ ở eb13550 mới bổ sung báo cáo tiến độ, chưa có bộ nguồn/adapter/AmendmentItem dân sự bàn giao. Main đã có khảo sát metadata/HTML của Dũng qua PR #14; đây chưa phải kho chuẩn hóa hoặc ca S–V1–B đã duyệt. Cần chạy lại CLI sau khi có đầu ra thật, không coi dữ liệu khảo sát là đã nối xong Context.
- Chưa có ca dân sự thật lấy từ hai dataset trong lần kiểm chứng này; bộ ca/gold và căn cứ chọn phiên bản cần Thọ và Dũng bàn giao/review.
- Chưa triển khai Semantic/Scorer hay kết luận tác động B thay Ngọc Anh. Chưa nối API/UI chỉ S thay Dũng/Tuấn Anh.
- Chưa chốt báo cáo cấp S với Dũng, chưa có môi trường kho bền vững dùng chung, chưa sửa hiện tượng gộp entity của upstream.

## Kiểm thử local của đợt bàn giao

| Nhóm | Kết quả |
| --- | --- |
| Parser/Adapter | 10 đạt |
| Schema | 49 đạt, 2 expected failures đã biết |
| Context | 58 đạt, 2 kiểm thử hai chế độ server cũ skipped; 27 ca mới không gọi provider |
| Demo DOCX/API | 30 đạt |
| Handoff | 8 đạt |

Tổng 159 ca: 155 đạt, 2 expected failures và 2 skipped. Các nhóm không bị sửa đã chạy cùng lần hồi quy; sau bổ sung chặn registry/client/phiên bản chỉ chạy lại Context, các ca đều đạt. CLI real được chạy độc lập với ca giả định như bảng bằng chứng phía trên; không đổi skipped thành passed hoặc gọi mock là server thật. Không phát hiện key đang cấu hình trong các file sẽ bàn giao; liên kết file tương đối và git diff --check đạt. CI GitHub chưa chạy cho thay đổi chưa commit/push này.

## Rà soát trước push ngày 23/11/2026

Nhánh làm việc còn ở nền 161e601; đã kiểm tra trên bản sao main 90e16cb (sau PR #13) cộng toàn bộ thay đổi Context, không merge/reset nhánh hoặc chạm code Explorer chưa commit. Không phát hiện file thay đổi chồng lấn với main mới. Chưa commit/push trong lượt rà soát.

Đã sửa và thêm hồi quy cho các trường hợp:
- Lượt query thứ hai lỗi không còn bị che bởi lượt đầu thành công; ghi từng mẫu và tổng hợp issue, retrieval_completed chỉ đúng khi đủ các mẫu yêu cầu đều đã xác minh.
- Registry thiếu block, khác comparison hoặc khác phiên bản bị chặn trước khi nhập/query.
- Docker đã nhận lệnh run nhưng mất ACK vẫn được kiểm tra và dọn theo tên cùng ownership label; không xóa container khác. Chạy bằng image ID đã inspect để không phụ thuộc tag thay đổi giữa chừng.
- Lỗi close client không ngăn dừng container sở hữu; env tạm được tạo riêng, xóa sau lệnh Docker.
- Graph sai định dạng trả graph_issues riêng, không bị ghi nhầm thành lỗi cleanup. Số lượt/budget sai bị từ chối trước khi khởi động dịch vụ.
- Manifest đã cập nhật bằng chứng thật ngày 22/11, không còn ghi chưa từng chạy container.

Kiểm thử trên bản sao main mới: Parser/Adapter 10 đạt; Schema 49 đạt và 2 expected failures; Context 67 đạt và 2 skipped; Demo 30 đạt; Handoff 8 đạt. Tổng 168 ca: 164 đạt, 2 expected failures và 2 skipped. CLI contract với hai lượt query trả exit 0, không phải LightRAG thật. Bằng chứng provider thật phía trên vẫn là lần chạy ngày 22/11; không gọi lại Gemini trong lượt rà soát này.

Các khoảng chờ dữ liệu, review contract cấp S và giới hạn KG vẫn giữ nguyên; kiểm thử không biến chúng thành chức năng đã hoàn tất.
