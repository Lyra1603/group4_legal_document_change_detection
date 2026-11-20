# DECISION — Quyết định triển khai và hợp đồng module

Tài liệu ghi các quyết định đã chốt và phạm vi áp dụng của chúng. Quy ước chạy thử được ghi ngay tại mục liên quan. Sau phiên 1, nhóm cập nhật những quyết định mới dựa trên báo cáo chạy thật. [Workflow](workflow.md) quy định cách đề xuất, review và ghi nhận thay đổi.

**Đồng bộ ngày 12/11/2026:** Dùng bản Dũng `6dbda8d` làm nền và các quyết định Đức Anh đã xác nhận dưới đây. [Nền chung](common-baseline.md) tách rõ thiết kế mục tiêu, code tại `c192f43`, fixture giả định và kiểm thử thật. Không đổi schema hoặc thuật toán trong đợt đồng bộ tài liệu này.

**Cập nhật phân công ngày 13/11/2026:** Đức Anh duyệt thay đổi từ `bachdung/docs` tại `ad4c272c7f5426bbc9c5891112c8e6cfe4f6f4b0`. Semantic Diff/Scorer chuyển sang Dũng + Đức Anh + Ngọc Anh; Tuấn Anh phụ trách UI/lỗi trả về. Giữ nguyên các quyết định schema, null/PARTIAL, HTTP và phạm vi demo đã chốt. Người làm chính và reviewer từng phần trong nhóm ba người còn cần xác nhận.

## Phạm vi cập nhật ngày 20/11/2026

Căn cứ [ghi chú buổi học 17/11](https://docs.google.com/document/d/1MzAXePwcTFb18FKzVs5J4jh8rc9Qz1CwCf1u7wW2Mrw/edit), BRD/SRS của Dũng tại PR #9 (`e745237`) và xác nhận của Đức Anh. Các mốc 12–13/11 bên trên là lịch sử. Các quyết định dưới đây mở rộng nghiệp vụ; không xác nhận code đã hiện thực. Code căn cứ sau PR #7 là main `95e1d79`.

1. Đầu vào mục tiêu là một S, bối cảnh và nguồn bổ sung tùy chọn. Chỉ phân tích trong kho dân sự nhóm chọn; chưa tự tìm Internet. Ngoài kho hoặc thiếu nguồn thì giữ yêu cầu và báo giới hạn/yêu cầu bổ sung.
2. Một S có thể sửa nhiều văn bản. Phân tích từng đích rồi tổng hợp; một đích chưa xử lý không làm mất kết quả hữu ích của đích khác.
3. Chọn phiên bản V1 theo định danh, nguồn và căn cứ thời điểm/phạm vi áp dụng. Không tự chọn bản mới nhất; thiếu căn cứ hoặc nhiều ứng viên thì giữ ứng viên/lý do cần kiểm tra.
4. Tác động gián tiếp phải chỉ ra điều khoản B sử dụng phần nào của V1, phần sửa đổi ảnh hưởng cách hiểu/áp dụng B thế nào và bằng chứng. Có liên quan chưa phải có tác động; không tự kết luận B bị sửa hoặc hết hiệu lực.
5. Ba mục đích retrieval: tìm đích/phiên bản từ S, tìm ngữ cảnh trước Semantic, tìm B để kiểm chứng tác động. Tra cứu định danh chính xác trước, retrieval bổ sung ứng viên; kiểm tra nguồn trước suy luận và kiểm tra đầu ra trước báo cáo.
6. Kho nguồn/chỉ mục kho được giữ qua các lượt; S/nguồn bổ sung/index tạm cách ly theo lượt và dọn riêng. Không xóa kho dùng chung khi cleanup một comparison. Client hiện tại chưa đáp ứng vòng đời kho bền vững.

Phân công LK-01 giữ nguyên; owner/task và hợp đồng chi tiết của chức năng mới cần thống nhất với bên giao/nhận. Chưa chọn thêm database, model, đa agent, API polling hoặc ngưỡng nghiệm thu. Cách biểu diễn đầy đủ báo cáo cấp S và validator cần triển khai theo SRS §1.8; không thêm trường vào schema cũ trong đợt này.

## Quyết định dùng schema Đức Anh làm hợp đồng chung

Ở cấp báo cáo từng đích, dùng [contracts.py](../backend/app/schemas/contracts.py) và validator đã merge vào main qua [PR #2](https://github.com/Lyra1603/group4_legal_document_change_detection/pull/2). Giữ cấu trúc mã nguồn theo main và phân công theo chức năng. Nhóm dùng fixture để phát triển bán song song và kiểm tra lại bằng đầu ra thật tại điểm nối. Phép đánh giá ghép dự đoán với nhãn theo matching 1–1 trước, 1–n bổ sung khi hoàn thành baseline. Quan hệ một chỉ dẫn với nhiều đích được giữ theo LK-05.

## A. Quyết định của owner về cách triển khai

### CN-01 — Đọc/chuyển đổi và parse tài liệu

Dùng bộ chuyển PDF và Parser DOCX hiện có làm nền phiên 1. Adapter xử lý ánh xạ sang schema chung theo LK-03.

### CN-03 — Chunking, query và chọn ngữ cảnh

Trong lõi từng đích, chuẩn bị nguồn/index tạm song song với Linker/Text Diff và ghép query ngữ cảnh khi đủ dữ liệu theo LK-06. Truy xuất đích từ S và tìm B là hai bước khác, không phụ thuộc TextDiffResult. Kho dùng chung được lập chỉ mục trước lượt chạy; không nhập lại toàn kho cho mỗi item.

### CN-04 — Cấu hình LightRAG và tài nguyên

Dũng và Đức Anh phụ trách tích hợp LightRAG Server qua HTTP theo LK-13.

### CN-06 — Phương pháp Semantic Diff

Dũng + Đức Anh + Ngọc Anh phụ trách Semantic Diff. Semantic Diff dùng rule trước, model khi cần. Kết luận phải kèm căn cứ hoặc ghi rõ phần chưa xác định.

### CN-08 — AI Adapter và tổ chức gọi mô hình

Dũng và Đức Anh phụ trách AI Adapter. Adapter là điểm gọi mô hình và kiểm tra đầu ra theo hợp đồng dùng chung.

### CN-10 — Cách tự kiểm chứng implementation

Các owner dùng kiểm thử module, kiểm thử chéo và kiểm thử toàn luồng. Evaluator độc lập nằm ngoài phạm vi triển khai. Đức Anh điều phối kế hoạch đánh giá.

### Quyết định sẽ bổ sung sau phiên 1

Các mã CN-02 (Linker), CN-05 (Text Diff), CN-07 (Scorer) và chi tiết thuật toán, mô hình, rubric, môi trường của các CN liên quan sẽ được cập nhật từ báo cáo chạy của owner. Phiên 1 thực hiện theo phạm vi và fixture đã giao trong [Implementation Plan](implementation-plan.md).

## B. Quyết định liên kết và hợp đồng giữa các module

### LK-01 — Phân công theo module/chức năng

| Phạm vi/module/chức năng | Người phụ trách | Ghi chú |
| --- | --- | --- |
| Dữ liệu + docs | Dũng | Dữ liệu, nghiệp vụ, tài liệu và phối hợp fixture/nhãn |
| Xử lý dữ liệu/tài liệu | Thọ | Chuyển đổi, Parser, adapter, trích và liên kết chỉ dẫn sửa đổi |
| Text Diff | Ngọc Anh | Phân tích phần chữ thay đổi |
| Semantic Change/Semantic Diff | Dũng + Đức Anh + Ngọc Anh | Phân tích thay đổi nghĩa và tạo nhận định có bằng chứng |
| Classifier & Scorer | Dũng + Đức Anh + Ngọc Anh | Phân loại và chấm mức tác động theo kết quả ngữ nghĩa |
| Tích hợp + API | Dũng | Pipeline, tổng hợp đầu ra và API nghiệp vụ; không đồng nhất với phần gọi LightRAG |
| AI Adapter/gọi mô hình | Dũng + Đức Anh | Theo người chủ trì CN-08; phân chia công việc nội bộ sẽ được điền tại CN-08 |
| Gọi/tích hợp LightRAG | Dũng + Đức Anh | Phụ trách gọi/tích hợp dịch vụ theo phương án HTTP đã chốt |
| Context | Đức Anh | Chuẩn bị chunk, truy vấn, chọn và kiểm tra ngữ cảnh/căn cứ |
| Điều phối kế hoạch đánh giá | Đức Anh | Tổng hợp yêu cầu từ thành viên, tổ chức hoàn thiện kế hoạch và theo dõi thực hiện |

Tuấn Anh phụ trách UI, gồm hiển thị báo cáo và xử lý lỗi, cảnh báo, trạng thái nhận từ Pipeline/API. Các module phát hiện và báo lỗi của phần mình. Pipeline/API tổng hợp và trả về frontend. Vai trò từng đầu ra và bên nhận được cụ thể hóa trong [Module](module.md).

### LK-02 — Các cặp liên kết và giao diện giữa module/chức năng

Dùng hợp đồng TypedDict của schema đã merge. Module trong backend bàn giao dict/list theo schema. LightRAG dùng HTTP qua client riêng. Chín điểm nối và fixture tương ứng nằm trong [Module §4](module.md#4-đầu-vàođầu-ra-và-các-điểm-nối).

### LK-03 — Parser → Adapter/Linker/Context

Adapter ánh xạ đầu ra native của Parser sang `ExtractedDocument`, `SourceBlock` và `Clause`. Giữ nguyên văn và khả năng tra nguồn. Parser tiếp tục tự đọc DOCX. Xem [Schema Integration](schema-integration.md).

### LK-04 — Định danh, nguồn và offset

Trong mỗi ComparisonReport cục bộ dùng `v1`/BASE, `s`/AMENDMENT và ID riêng cho từng REFERENCE. Cấp S cần ánh xạ (target_id, ID nguồn cục bộ) về định danh văn bản/phiên bản thật và snapshot kho; filename/số Điều không phải khóa toàn kho. `EvidenceRef` chứa `document_id`, `source_refs`, `quote`. Giữ `block:N` khi trỏ đúng khối và quote khớp nguồn. Text Diff dùng offset ký tự Python theo khoảng nửa mở trên đúng chuỗi trước/sau.

### LK-05 — Chỉ dẫn sửa đổi và nội dung trước/sau

Phiên 1 giữ toàn văn cùng một đơn vị đối chiếu ở cả hai trạng thái. Với sửa nội dung của Điểm, Khoản hoặc Điều hiện có, đơn vị đối chiếu là toàn văn đơn vị đó. Khi thêm hoặc bãi bỏ cả một đơn vị, dùng đơn vị chứa nhỏ nhất còn tồn tại ở hai phía, ví dụ toàn Điều khi thêm hoặc bãi bỏ một Khoản. Vị trí đích vẫn ghi chính xác Điểm, Khoản hoặc Điều mà S chỉ ra. Nếu chỉ dẫn có nhiều đích, giữ đủ đích và căn cứ cho từng đích.

Quy ước triển khai thử phiên 1 là một `AmendmentItem` cho mỗi đích có thể áp dụng độc lập. Các item cùng chỉ dẫn trỏ về cùng bằng chứng S. Với chỉ dẫn có đích chồng lấn hoặc thao tác phụ thuộc lẫn nhau, ghi nhận giới hạn và đưa ví dụ vào báo cáo phiên 1 để nhóm chốt cách xử lý.

Chỉ dùng `QUOTED` khi toàn bộ đoạn sau là nguyên văn từ S. Dùng `DERIVED` khi dựng lại đơn vị đối chiếu từ V1 và chỉ dẫn S. Phía đã xác định vắng mặt và phía chưa biết được biểu diễn theo [SRS §1.2](srs.md#12-amendmentitem-và-analysiscontext).

**Giới hạn nền trước merge:** quy tắc thêm/bãi bỏ và nhiều đích là mục tiêu sau merge. Linker demo hiện hỗ trợ sửa cụm từ duy nhất hoặc đoạn thay thế trích nguyên văn tại một đích. Chưa đủ căn cứ xác minh văn bản đích phải giữ `UNRESOLVED`, không mặc định `v1`. Thao tác chưa hỗ trợ giữ chỉ dẫn, nguồn, lý do và bỏ qua phân tích phụ thuộc; không tự đổi thành `AMEND`. Đích đã xác minh là V1 dùng document_id `v1`. Khi chưa xác minh, code giữ chuỗi gợi ý từ nguồn hoặc chuỗi rỗng; OTHER_DOCUMENT giữ số hiệu khác được xác minh từ nguồn. Các chuỗi nhãn ngoài V1 không phải ID tài liệu đã nhập, bên nhận luôn kiểm tra applicability trước; cách mở rộng định danh ngoài V1 được review khi triển khai, không thêm ID giả.

### LK-06 — Context song song Text Diff, ghép query trước Semantic Diff

Đoạn này áp dụng query ngữ cảnh của lõi từng đích, sau khi đã tìm đúng V1. Chuẩn bị Context và chỉ mục tạm song song với Linker → Text Diff; kiểm tra readiness của chỉ mục kho đã có, không nhập lại toàn kho. Khi hai nhánh có đủ dữ liệu, ghép chỉ dẫn, trước/sau và vùng chữ đổi để truy xuất, kiểm tra nguồn và cung cấp `AnalysisContext` cho Semantic Diff. [Architecture §4.1](architecture.md#41-một-lượt-phân-tích) giữ sơ đồ chi tiết.

Bridge hiện tách `context_prepare(item)` để chuẩn bị chỉ mục song song Text Diff, rồi gọi `context_work(item, text_diff)` để truy vấn sau khi cả hai hoàn tất. Query nhận chỉ dẫn, trước/sau và vùng chữ đổi; kiểm tra ID, offset và nội dung diff tại điểm nối nội bộ, không đổi schema/validator chung. Nếu index lỗi, bỏ qua query và giữ cảnh báo cho Semantic. Việc chuẩn bị chỉ mục từ Adapter song song cả Linker vẫn thuộc tích hợp Pipeline tiếp theo; demo hiện tắt retrieval. Kiểm thử HTTP mô phỏng không xác nhận hoàn thành LK-13 hoặc dịch vụ thật.

### LK-07 — Text Diff → Semantic Diff

Text Diff trả `TextDiffResult` theo cùng `amendment_id`. Các đoạn INSERT/DELETE/REPLACE có offset khớp hai chuỗi trước/sau. Semantic nhận phần chữ đổi cùng ngữ cảnh đã kiểm chứng.

### LK-08 — Cấu trúc Semantic Change

Dùng `SemanticDiffResult`, `SemanticChange` và `ChangeAspect` trong schema PR #2. Giữ bằng chứng, cảnh báo và trạng thái cần kiểm tra theo [SRS §1.3](srs.md#13-semanticdiffresult-hợp-đồng-kết-quả-phân-tích-ngữ-nghĩa).

### LK-09 — Tám nhóm field_group, category và ranh giới nhãn

Dùng tám `field_group` đã có. Với thay đổi nghĩa, category khác null phải thuộc một nhóm có trong aspects. Thay đổi chỉ về diễn đạt dùng `WORDING_ONLY` theo schema. Review ca giao thoa bằng văn bản nguồn trước khi chốt ranh giới nhãn.

### LK-10 — Semantic Diff → Classifier & Scorer

Dũng + Đức Anh + Ngọc Anh phụ trách Scorer. `ScoringResult` nối tới thay đổi bằng `change_id`. Khi có căn cứ gán nhóm khía cạnh nhưng chưa đủ căn cứ chấm mức độ, giữ nhóm đã xác định, dùng `significance = null`, `is_critical = null`, `needs_review = true` và ghi lý do. Rubric chi tiết và cách xử lý lỗi theo bước sẽ được cập nhật từ báo cáo của các thành viên sau lần chạy phiên 1.

Ca fixture chung `deadline_reduction` (30 → 15 ngày) dùng mức độ `null`, không lấy `MEDIUM` hoặc `HIGH` làm nhãn đã duyệt. Report của ca chung dùng `PARTIAL` cùng lý do chờ review; kết quả Semantic có trong fixture là kỳ vọng kỹ thuật giả định, không phải output được baseline hiện tại xác nhận.

### LK-11 — Báo cáo Pipeline → API/frontend

API đang chạy trả `ComparisonReport` gồm kết quả theo `AmendmentResult`. Đầu vào hiện dùng `doc_v1`, `doc_s` và `reference_files` nếu có. Frontend hiện đoạn trích và vị trí từ bằng chứng trong báo cáo của lượt đang mở. Xem [Architecture §4.3](architecture.md#43-vị-trí-lưu-và-vòng-đời) về vòng đời nguồn.

API mục tiêu nhận S và trả báo cáo cấp S theo SRS §1.8, bao các ComparisonReport cục bộ, yêu cầu chưa giải quyết, tác động gián tiếp và phạm vi. Endpoint/payload/schema/validator/fixture cấp S chưa được triển khai; phải review trước khi đổi bên giao/nhận. API cũ không tự trở thành API chỉ S khi tài liệu được merge.

Điểm chạy nền chung là `backend.demo:app` (HTML/CSS/JavaScript, DOCX). `backend.main:app` vẫn chưa gắn runner. Không yêu cầu nối lại main hoặc chuyển sang React trước merge nền; hướng frontend chính thức giữ theo SRS, việc mở rộng thực hiện sau.

### LK-12 — Null, rỗng, cảnh báo, lỗi và trạng thái

Khi chưa xác định được đích, giữ chỉ dẫn, thao tác đã nhận diện và bằng chứng. Dùng `applicability = UNRESOLVED`, `needs_review = true` và lý do. Giữ mục trong báo cáo và để các kết quả phân tích chưa chạy là `null`.

Các module báo lỗi và cảnh báo của phần mình. Dũng tổng hợp và trả qua Pipeline/API. Tuấn Anh xử lý và hiển thị lỗi, cảnh báo và trạng thái trả về trên UI.

`SUCCESS`: các bước bắt buộc đã hoàn thành và không còn trạng thái cần kiểm tra. `PARTIAL`: có kết quả dùng được nhưng còn phần thiếu/chưa xác nhận. `FAILED`: không tạo được mục phân tích dùng được; vẫn giữ các chỉ dẫn đã nhận diện, nguồn và lý do. Trong demo AMEND hiện tại, một cặp trước/sau có Text Diff được tính là kết quả dùng được, kể cả diff rỗng; không từ đó suy ra toàn văn không đổi nghĩa. Fixture chung dùng `PARTIAL`; `SUCCESS` chỉ dùng cho ca riêng hoàn tất mọi bước bắt buộc, không gắn cho demo để che phần chưa triển khai.

HTTP và trạng thái report tách biệt: xử lý hợp lệ, hoàn tất nhưng không phân tích được trả HTTP 200 + report `FAILED` nếu không có lỗi thực thi. Lỗi dịch vụ/thực thi có errors trả 500, timeout 504, chưa cấu hình runner 501; lỗi upload giữ 415/413/422/409 theo [bảng API](schema-integration.md#api-và-http-status-hiện-tại). Mã lỗi và chính sách chi tiết cho các module/dịch vụ mới tiếp tục review khi triển khai, không tự mở rộng schema.

### LK-13 — LightRAG HTTP và vòng đời dữ liệu

LightRAG Server riêng, backend gọi qua HTTP. Dũng và Đức Anh phụ trách tích hợp. Phạm vi chính là retrieval và kiểm chứng nguồn. Phiên 1 dùng fixture/mock để kiểm tra điểm nối, kết quả chạy làm căn cứ chốt release, endpoint, payload, cách ly và vòng đời chỉ mục.

Kho dân sự và index kho được giữ qua nhiều analysis. Chỉ dọn nguồn/index tạm thuộc lượt đang xử lý; lỗi retrieval/rỗng không chứng minh thiếu văn bản hoặc không có tác động. Client hiện tại dành server/storage riêng cho một comparison, chưa hỗ trợ kho bền vững dùng chung; phải thiết kế binding/vòng đời mới và kiểm chứng trước khi bật kho thật. Xem Architecture §4.3.

Client thử nghiệm đã pin upstream tại `28ff1b05f2ac3f3e6fa14dd2cd33656579bd0c9c`; đó là mốc đã dùng để đọc API và viết adapter, chưa là nghiệm thu dịch vụ thật hoặc lựa chọn triển khai cuối. Giữ [báo cáo thử nghiệm](lightrag-integration-report.md) và [bằng chứng demo](local-web-demo.md) với mốc/lệnh/giới hạn; không mô tả mock là retrieval thành công. Bộ fixture chung duy nhất ở `data/module_handoff_fixtures/`, lấy 9 điểm nối của Dũng, sửa nhãn/trạng thái theo LK-10/12 và thêm ca lỗi. [Provenance](../data/module_handoff_fixtures/provenance.json) ghi nguồn và các khác biệt.
