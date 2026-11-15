# Xác nhận đồng bộ tài liệu và kiểm thử schema sau PR #2

**Báo cáo lịch sử:** giữ làm bằng chứng theo commit/môi trường ghi dưới đây, không phải trạng thái nhánh LightRAG hiện tại. Kiểm tra mới ở [common-baseline.md](common-baseline.md). Các nhận định về module chưa triển khai chỉ thuộc mốc cũ.

## Căn cứ và phạm vi

- Main đã fetch: `a8a906a474a67e89195987ca757f7315c22231db`, merge [PR #2](https://github.com/Lyra1603/group4_legal_document_change_detection/pull/2).
- Schema/test merge từ `99907a8e738019c9e20ceb8fd3582ab8f238555d`; ba file schema giữ theo commit Đức Anh `b6a13f98b9a7357b9fbb0936aba6bda065d03fcb`.
- Tài liệu đối chiếu: `origin/bachdung/docs` tại `b20ba5806772d8bb1f5f41f55548471eb8e251e0` và bản docs đã đồng bộ Dũng vừa thay vào local. Remote docs chưa có các thay đổi local đó; bản đã duyệt được giữ khi phù hợp schema.
- Nhánh review: `bachdung/docs-schema-sync`, tạo từ main mới. Không merge nguyên nhánh docs cũ vì nhánh đó còn khác code/cấu trúc với main.
- Chỉ README.md và docs/ thay đổi; không sửa schema, fixture, test, requirements, Pipeline/API hoặc thuật toán. Không merge main trong đợt này.

## Danh sách file và lý do

| File | Thay đổi |
| --- | --- |
| [README.md](../README.md) | Sửa liên kết từ root; cập nhật phân công, schema PR #2, cài dependency/test và giới hạn runtime |
| [docs/README.md](README.md) | Đồng bộ tổng quan mới, hợp đồng results/tám nhóm và API hiện tại; thêm hướng dẫn kiểm thử |
| [architecture.md](architecture.md) | Thay hợp đồng phẳng bằng ComparisonReport/AmendmentResult; ghi API/Pipeline hiện có và ranh giới nhận xét |
| [srs.md](srs.md) | Đồng bộ các kiểu, trường nullable, nhóm/category/scoring và thứ tự validator; tách dữ liệu frontend |
| [module.md](module.md) | Đưa bản mới từ docs vào main, giữ owner mới nhất; ràng buộc output theo schema và ghi compare.py còn là khung |
| [decision.md](decision.md) | Giữ các bảng phương án còn mở; LK-08/09/10/11 ghi schema đã merge qua PR #2; không tự chốt API/thuật toán |
| [brd.md](brd.md) | Sửa mô tả nhóm phân loại và kết quả đầu ra bị schema ảnh hưởng |
| [data-annotation-guide.md](data-annotation-guide.md) | Tám nhóm/category và mẫu nhãn cùng hợp đồng; không coi ví dụ rời là response API đầy đủ |
| [implementation-plan.md](implementation-plan.md) | Giữ kế hoạch/phân công mới trên docs; đồng bộ phần bàn giao và tích hợp theo schema |
| [test_evaluation_plan.md](test_evaluation_plan.md) | Đưa kế hoạch mới vào main; kiểm tra hợp đồng riêng với đánh giá chất lượng mô hình |
| [workflow.md](workflow.md) | Đưa workflow mới vào main; xác nhận main là nhánh chung và payload TypedDict; giữ quy tắc review |
| [schema-integration.md](schema-integration.md) | Hướng dẫn kho nguồn/Clause và adapter, API/status theo code, dependency, giới hạn và đề xuất cần review riêng |
| [schema-verification-report.md](schema-verification-report.md) | Báo cáo đợt xác nhận này, bằng chứng, kết quả thực tế và việc tiếp theo |

Tài liệu nhập từ Windows được chuyển newline về LF và bỏ khoảng trắng cuối dòng để phù hợp diff trên main; không đổi cấu trúc module. Các quyết định phương pháp không bị schema ảnh hưởng và phân công mới nhất được giữ. F1 90%/Critical Recall 95% vẫn là ngưỡng dự tính, có thể thay đổi sau khi hoàn thiện test_evaluation_plan.md; matching đánh giá 1–1 trước, 1–n bổ sung sau.

## Môi trường và lệnh đã chạy

Chạy trên Linux, CPython 3.12.14 (Clang 22.1.3), trong venv đã có dependency; không tuyên bố lần này tạo môi trường trắng. Phiên bản quan sát:

| Package | Phiên bản |
| --- | --- |
| pydantic | 2.13.4 |
| pydantic-core | 2.46.4 |
| typing_extensions | 4.16.0 |
| annotated-types | 0.8.0 |
| typing-inspection | 0.4.5 |
| pip | 25.0.1 |

Từ repo root, dùng Python trong venv:

```bash
python --version
python -m pip install -r requirements.txt
python -m pip check
python -m unittest discover -s test/schema_suite -p "test_*.py" -v
git diff --check
```

Cài dependency: exit 0, các package ghim đã được thỏa mãn. `pip check`: exit 0, `No broken requirements found.` Bộ unittest: exit 0, kết quả thực tế:

```text
Ran 51 tests in 0.596s

OK (expected failures=2)
```

Có **49 test đạt và 2 expected failures**; không có unexpected failure/error/skip. Dòng log `comparison=runner-bad-source stage=analysis failed` là lỗi được test chủ động kích hoạt để xác nhận Pipeline trả FAILED, không phải test thất bại. Chưa chạy HTTP runtime, PDF conversion, LightRAG hoặc mô hình; không dùng kết quả này để xác nhận tích hợp/độ chính xác nghiệp vụ.

Fixture [common_contract.json](../test/fixtures/reports/common_contract.json) có ba kho nguồn v1/s/ref_1, Clause và report minh họa 30 → 15 ngày. Đây là dữ liệu giả định, mức HIGH chưa chứng minh rubric pháp lý. Các test kiểm tra trường bắt buộc và nullable, Literal/enum, ID, nguồn/quote, target Clause, offset, scoring, review propagation và status. [test_main_compatibility.py](../test/schema_suite/test_main_compatibility.py) kiểm tra envelope FAILED mặc định, adapter thử nghiệm giữ block:N, và runner chặn nguồn sai. Chỉ runner trong test gọi validator; production Pipeline chưa được nối.

## Hai expected failures phải theo dõi

| Test hiện có | Giới hạn được tái hiện | Việc cần review tiếp |
| --- | --- | --- |
| KnownBaselineGaps.test_global_change_id_uniqueness_not_enforced | Hai amendment khác nhau cùng chứa c1 vẫn được chấp nhận; validator chỉ kiểm tra trùng trong từng result | Đức Anh/Tuấn Anh/Dũng chốt change_id toàn cục hay khóa ghép amendment_id/change_id trước khi sửa validation và mapping frontend |
| KnownBaselineGaps.test_complete_text_reconstruction_not_enforced | before/after khác nhau nhưng changes=[] vẫn được chấp nhận | Ngọc Anh/Dũng review kiểm tra dựng lại toàn văn cục bộ, độ bao phủ, thứ tự và overlap; PR tăng kiểm tra riêng |

Không xóa decorator expectedFailure, không đổi expected output để biến thành đạt, không sửa validator trong đợt tài liệu. Khi hiện thực kiểm tra mới, cập nhật test và ghi quyết định được review tương ứng.

## Đối chiếu tài liệu và code

- 18 lớp mô tả trong code block SRS có cùng tập tên trường với contracts.py; đã đối chiếu bằng AST, không coi mô tả rút gọn là code validator thay thế.
- Ví dụ adapter Python trong schema-integration.md đã được thực thi với Parser main, DOCX tối thiểu và fixture. Kho nguồn giữ block:N, target_unit_ids dùng node_id thực tế; validate_payload, validate_extracted_document, validate_amendment, validate_sources, validate_report chạy được. Đây là kiểm tra ví dụ tài liệu, không phải code production mới.
- Rà toàn bộ liên kết Markdown nội bộ của README.md/docs và kiểm tra code fence: không có đường dẫn thiếu hoặc fence chưa đóng ở bản hoàn thiện. Liên kết HTTP bên ngoài không được kiểm tra khả dụng bằng yêu cầu mạng.
- git diff --check không báo lỗi ở bản hoàn thiện. Diff chỉ chứa tài liệu; schema/test/fixture/dependency/runtime giữ nguyên main.
- Hợp đồng không có documents/items, ReviewItem, ReviewRecord, schema_version hay item_id như trường mới. Những tên còn xuất hiện trong tài liệu là nội dung loại bỏ hoặc đề xuất frontend được ghi rõ, không phải yêu cầu triển khai backend.

## Điểm còn mở và owner tiếp theo

| Việc | Ví dụ/câu hỏi cần chốt | Bên phụ trách/review |
| --- | --- | --- |
| Adapter nguồn/Clause và validator production | ParsedDocument chưa là ExtractedDocument; final report phải kiểm tra trước cleanup/trả API; không chỉ gọi validate_report | Thọ + Dũng, Đức Anh review schema |
| Chữ ký điểm nối và readiness | Item chưa xác định đích hoặc before/after thì bước nào được chạy? SUCCESS/PARTIAL/FAILED cần điều kiện nghiệp vụ bổ sung nào? | Owner giao/nhận, Dũng điều phối |
| API upload/status/error body | Main dùng doc_v1/doc_s/reference_files; alias base_file/amendment_file chưa có; lỗi detail khác ComparisonReport; SUCCESS/PARTIAL hiện HTTP 200, mặc định chưa runner là 501 | Dũng + Tuấn Anh/frontend; LK-11, bảng đầy đủ ở hướng dẫn tích hợp |
| Nguồn sau cleanup | Report chỉ giữ identity/EvidenceRef; frontend giữ file hay cần cơ chế cung cấp block riêng? | Thọ + Dũng + Đức Anh + Tuấn Anh |
| Nhận xét frontend | Nhận xét amendment khi semantic_diff=null; ghép sau chạy lại; enum, khóa, vòng đời và lưu trữ chưa chốt | Tuấn Anh + Dũng |
| Rubric category/significance | Nhiều nhóm trong aspects nhưng một category; ranh giới HIGH/CRITICAL chưa suy ra từ enum | Tuấn Anh + Dũng, Đức Anh phối hợp đánh giá |
| Chất lượng nguồn/quote | old_quote/new_quote không tự được đối chiếu như EvidenceRef; PDF mapping chưa xác minh | Thọ + Tuấn Anh + Đức Anh |
| Runtime API/PDF | requirements hiện chỉ ghim schema, chưa đủ FastAPI/uvicorn/multipart/converter | Owner module + Dũng/Đức Anh review dependency ở PR runtime |
| LightRAG | Client, cấu hình, lifecycle chưa được PR schema hiện thực; HTTP/phân công không mở lại | Dũng + Đức Anh; giữ thứ tự LK-13 |

Các đề xuất mở rộng trường được liệt kê riêng ở [hướng dẫn tích hợp](schema-integration.md): dữ liệu nguồn, định danh/phiên bản đối chiếu và ReviewRecord. Chưa chọn tên trường/enum, chưa thêm schema. Hai tăng cường validator nêu trên và mọi thay đổi thuật toán cần PR riêng.

## Commit, PR và review

Chia thay đổi theo Conventional Commits: một commit đồng bộ hợp đồng/tài liệu, một commit bổ sung báo cáo xác nhận và liên kết kiểm thử. Đích PR là main; schema PR #2 đã merge nên không còn là PR phụ thuộc chưa hoàn thành. Không merge nguyên bachdung/docs vào main và không lấy code từ branch đó.

Reviewer cần: Đức Anh về schema/context; Tuấn Anh về semantic/scoring và frontend/nhận xét; Ngọc Anh về TextDiff; Thọ về nguồn/Clause; Dũng rà tích hợp/docs. Chưa tuyên bố có xác nhận của các reviewer. Không tự merge trước review theo workflow.
