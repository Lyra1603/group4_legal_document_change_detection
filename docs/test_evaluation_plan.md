# Kế hoạch kiểm thử và đánh giá

**Dự án:** Legal Document Change Detection — POCS, Nhóm 4
**Phiên bản:** 0.1 — Khung chuẩn bị song song với quyết định và đặc tả module
**Ngày tạo:** 08/11/2026
**Trạng thái:** Khung kế hoạch đang hoàn thiện; Đức Anh điều phối. Hiện xác định cách đánh giá; tạm lấy Change F1 ≥ 90% và Critical Change Recall ≥ 95%. Đây là các ngưỡng dự tính và có thể thay đổi sau khi hoàn thiện test_evaluation_plan.md, chưa phải ngưỡng nghiệm thu chính thức; hợp đồng schema chung đã chốt, adapter/fixture nghiệp vụ và chi tiết phép đo còn chờ hoàn thiện.

## 1. Mục đích và phạm vi

Tài liệu quy định cách chuẩn bị và thực hiện kiểm thử module, kiểm tra điểm nối, kiểm tra toàn luồng và đánh giá chất lượng phương pháp. Viết khung từ sớm để yêu cầu kiểm chứng được xem xét khi owner đề xuất cách triển khai, không chờ toàn bộ module.md hoàn thành.

Đầu vào nghiệp vụ là V1, văn bản sửa đổi S và tài liệu tham chiếu khi cần. S chứa chỉ dẫn sửa đổi, không mặc định là bản V2 đầy đủ. Kế hoạch bao gồm cả xử lý thành công, thiếu căn cứ, chưa xác định và thất bại.

Đây là kế hoạch của POCS. Việc lấy ý kiến người dùng của HCI được quản lý theo dự án HCI; không mặc định biến thành yêu cầu đánh giá riêng của POCS.

Không triển khai lại một module Evaluator độc lập. Có thể dùng test hoặc script để tính số đo; mỗi phép đo phải có dữ liệu, quy tắc và kết quả kiểm chứng được.

## 2. Quan hệ với các tài liệu khác

| Tài liệu | Nội dung sở hữu | Cách phối hợp |
| --- | --- | --- |
| decision.md | Đề xuất, lựa chọn, lý do, đánh đổi và xác nhận của bên liên quan | CN-10 nhận đề xuất tự kiểm chứng của owner; các quyết định CN/LK liên quan xác định contract và phương pháp cần kiểm tra |
| module.md | Đặc tả đã chốt, trách nhiệm, điểm nối và điều kiện bàn giao | Ghi tiêu chí kiểm chứng tối thiểu tại module và dẫn tới mã kiểm tra trong kế hoạch này |
| test_evaluation_plan.md | Phạm vi kiểm tra, thiết kế ca, dữ liệu, baseline, phép đo và tổ chức thực hiện | Bổ sung theo từng phần đã chốt; phần chưa chốt phải giữ trạng thái rõ |
| Hướng dẫn dữ liệu và gán nhãn | Nguồn, quy tắc nhãn, căn cứ và review đáp án | Kế hoạch dẫn tới phiên bản áp dụng, không tạo một bộ quy tắc nhãn thứ hai |

Các đường dẫn tới test, fixture và script cụ thể được bổ sung sau khi kiểm tra cấu trúc repo và thống nhất với owner. Không tự đổi cấu trúc folder chính đã chốt.

## 3. Cách hoàn thiện theo tiến độ

| Giai đoạn | Việc thực hiện | Điều kiện để sử dụng chính thức |
| --- | --- | --- |
| Chờ đề xuất owner | Liệt kê rủi ro, chuẩn bị mẫu nghiệp vụ và yêu cầu bằng chứng; owner đề xuất cách tự kiểm chứng | Mẫu và đáp án được review; chưa coi cấu trúc dữ liệu dự kiến là contract |
| Review và chốt quyết định | Kiểm tra phương án có thể đo/kiểm chứng; thống nhất phần ảnh hưởng bên nhận | Quyết định liên quan được xác nhận theo decision.md |
| Hoàn thiện từng phần module.md | Điền input/output, expected output, ca kiểm tra, người thực hiện và reviewer | Dùng hợp đồng schema Đức Anh đã chọn; fixture nghiệp vụ và adapter được hai bên review |
| Có implementation | Tự kiểm tra module; kiểm tra điểm nối với đầu ra thật; tích hợp sớm | Có kết quả và giới hạn, không chỉ có code test |
| Chuẩn bị đánh giá chính thức | Cố định phiên bản, cấu hình, dữ liệu, nhãn, matching và phép đo | Các phần phụ thuộc đã rõ; không còn lỗi chặn phép đo |

Một phần có thể sẵn sàng trước phần khác. Không cần chờ toàn bộ decision.md hoặc module.md hoàn tất để kiểm tra module có đủ đặc tả. Riêng LK-13 giữ thứ tự chốt đã quy định trong decision.md: có thể khảo sát và chuẩn bị ca kiểm tra, nhưng chỉ chốt chi tiết còn lại sau các quyết định khác.

## 4. Trách nhiệm và điều phối

Phân công chức năng phải theo LK-01 đã chốt, không sao chép các bảng cũ chưa đồng bộ trong module.md.

| Phạm vi | Trách nhiệm hiện có | Trách nhiệm kiểm chứng đề xuất |
| --- | --- | --- |
| Xử lý tài liệu, Parser, adapter và linker | Thọ | Tự kiểm tra từ nguồn thật; bên nhận review output và vị trí nguồn |
| Text Diff | Ngọc Anh | Tự kiểm tra vùng đổi, offset và khả năng tái tạo khi contract cho phép; bên nhận Semantic Diff review dữ liệu bàn giao |
| Semantic Diff và Scorer | Dũng + Đức Anh + Ngọc Anh | Kiểm tra ngữ nghĩa, bằng chứng, ranh giới mức và trạng thái thiếu căn cứ; Dũng review phần dùng để tổng hợp/nghiệp vụ |
| Tích hợp, Pipeline và API nghiệp vụ | Dũng | Kiểm tra tổng hợp, truyền cảnh báo/lỗi và luồng API; phối hợp bên cung cấp và frontend |
| UI và xử lý lỗi trả về | Tuấn Anh | Kiểm tra hiển thị lỗi, cảnh báo, trạng thái và phần kết quả còn dùng được. |
| AI Adapter | Dũng và Đức Anh | Kiểm tra phản hồi hợp lệ/không hợp lệ, lỗi, giới hạn và việc giữ nguồn; phân chia nội bộ theo CN-08 |
| Gọi/tích hợp LightRAG | Dũng + Đức Anh | Phối hợp kiểm tra dịch vụ, tích hợp context/Pipeline và vòng đời dữ liệu |
| Context và schema | Đức Anh phụ trách schema và context | Hợp đồng dùng chung được bên giao/nhận thống nhất; đồng bộ module.md |
| Điều phối đánh giá toàn hệ thống | Đức Anh điều phối kế hoạch | Các thành viên đề xuất yêu cầu, thực hiện và review phần liên quan; không đồng nghĩa kiểm thử thay các owner |

Owner tự kiểm tra trước bàn giao. Bên giao và bên nhận kiểm tra chéo tại điểm nối. Khi hai chức năng có cùng owner, vẫn phải kiểm tra ranh giới chức năng và có review phù hợp từ bên sử dụng kết quả. Người review đáp án nghiệp vụ không chỉ xác nhận lại đầu ra AI làm chuẩn.

## 5. Phân biệt các loại kiểm chứng

| Loại | Câu hỏi | Bằng chứng cần có |
| --- | --- | --- |
| Kiểm thử module | Implementation có đáp ứng đặc tả của phần này không? | Input, expected output được review, actual output và cách chạy |
| Kiểm tra điểm nối | Bên giao và bên nhận có hiểu cùng ý nghĩa dữ liệu không? | Fixture theo contract và đầu ra thật được bên nhận sử dụng |
| Kiểm tra toàn luồng | Từ file tải lên có tạo được báo cáo đúng hoặc lỗi đúng không? | File thật, kết quả cuối và khả năng truy nguồn/trạng thái |
| Đánh giá phương pháp | Chất lượng, giới hạn và đánh đổi của phương án là gì? | Baseline khi phù hợp, dữ liệu và cấu hình cố định, phép đo và phân tích lỗi |

Đúng schema hoặc chạy không lỗi chưa chứng minh đúng nghiệp vụ. Kết quả cuối đúng trên một ví dụ chưa chứng minh mọi bước đều đúng; lỗi giữa các bước có thể bù trừ hoặc bị che mất.

## 6. Danh mục kiểm tra ban đầu

Bổ sung ca: index chạy song song Linker/Text Diff; query chờ cả hai nhánh và sử dụng đúng TextDiffResult; lỗi một nhánh không bị che. Kiểm tra quote/document_id/source_refs qua retrieval → Semantic/Scorer → frontend. Sau cleanup, kiểm tra UI vẫn hiện được đoạn trích và vị trí từ báo cáo đã nhận. Kiểm tra rule trước/model khi cần, lỗi model không tạo kết luận giả; owner giao/nhận lỗi cùng bằng chứng. Nhận xét hai loại là backlog giai đoạn sau, không là điều kiện nghiệm thu bản đầu.

Các mã dưới đây là mã của kế hoạch này, không phải mã quyết định mới. Đây là phạm vi chuẩn bị, chưa xác nhận các test đã được hiện thực hoặc đã đạt.

| Mã | Phạm vi | Tình huống/rủi ro cần kiểm tra | Căn cứ xác định expected output |
| --- | --- | --- | --- |
| TEP-01 | Chuyển đổi và Parser | Mất chữ, sai thứ tự, sai ranh giới Điều/Khoản/Điểm, bỏ bảng hoặc nội dung ngoài Điều | Đọc/review độc lập tài liệu nguồn; không dùng summary tự đếm làm đáp án duy nhất |
| TEP-02 | Adapter và nguồn | Sai vai trò V1/S/tham chiếu, ID không khớp, quote lệch nội dung, sai vị trí nguồn | Đối chiếu trực tiếp đoạn nguồn và contract đã chốt |
| TEP-03 | Linker | Sửa toàn đơn vị/cụm từ, bổ sung, bãi bỏ, nhiều thay đổi, sai văn bản đích hoặc đích mơ hồ | Chỉ dẫn trong S cùng nội dung đích V1 được review |
| TEP-04 | Nội dung trước sau | Mất điều kiện/ngoại lệ; nhầm chưa xác định với không tồn tại; gộp sai nhiều chỉ dẫn | Mẫu cục bộ có giải thích căn cứ và thứ tự áp dụng khi liên quan |
| TEP-05 | Text Diff | Offset sai chuỗi, thay đổi tiếng Việt/dấu câu, thêm/xóa, null/rỗng | Hai chuỗi đúng phiên bản và quy tắc offset đã chốt |
| TEP-06 | Context và retrieval | Thiếu ngữ cảnh, truy sai tài liệu, mất liên kết nguồn, nhầm query rỗng với thiếu tài liệu | Bộ ca có nguồn cần thiết được review; không mặc định chỉ có một đoạn đúng |
| TEP-07 | Semantic Diff | Chỉ đổi diễn đạt, thay đổi nghĩa, nhiều khía cạnh, nhận định không có căn cứ | Nhãn/nhận định tham chiếu và matching được thống nhất |
| TEP-08 | Scorer | Ranh giới mức tác động, thiếu căn cứ, sai liên kết với nhận định, dùng retrieval score thay mức tác động | Rubric và ví dụ ranh giới được chốt |
| TEP-09 | AI Adapter | Output sai cấu trúc, trích dẫn không có trong nguồn, timeout hoặc lỗi mô hình | Contract lỗi và quy tắc validation; có thể giả lập lỗi để kiểm tra ổn định |
| TEP-10 | Tổng hợp/API | Bỏ mất chỉ dẫn chưa phân tích, mất cảnh báo, nhầm lỗi với không có thay đổi | ComparisonReport/results/AmendmentResult theo schema chung và bảng null/rỗng/lỗi/trạng thái |
| TEP-11 | Toàn luồng | Một ca đủ căn cứ, một ca thiếu căn cứ, một ca lỗi; bổ sung tài liệu khi chức năng đã được chốt | Báo cáo kỳ vọng từ file thật, nguồn và phạm vi xử lý |
| TEP-12 | LightRAG và vòng đời | Sẵn sàng nhập/query, mapping, cách ly lượt chạy, cleanup và lỗi dịch vụ | Release/API thực tế theo LK-13; chưa chốt payload hoặc cấu hình trong kế hoạch này |

Mỗi module chọn các ca liên quan; không bắt buộc mọi test gọi mô hình hoặc dịch vụ thật. Kiểm tra dịch vụ thật vẫn cần có khi xác nhận tích hợp thật. Mock/fixture phải được đánh dấu rõ.

### Bộ ca bàn giao phiên 1

**Nền merge và kế hoạch mở rộng:** bộ chung hiện có 9 file deadline_reduction, 2 ca chặn query và 6 ca lỗi (17 JSON ca), cùng provenance. Ca chung giữ mức độ null và PARTIAL; expected Semantic là giả định kỹ thuật, chưa là nhãn review hoặc output demo. Các ca bên dưới là kế hoạch sau merge, không đòi 45 JSON trước khi dùng nền DOCX. case_06/07/08 ở nhánh Dũng 6dbda8d, chưa nhập local đợt này; cần lấy nguồn và kiểm chứng PDF trước khi dùng. Test nguồn/contract, module thật và dịch vụ thật được báo riêng theo [nền chung](common-baseline.md).

Một mã ca xuất hiện ở cả 9 thư mục trong [bộ fixture](../data/module_handoff_fixtures/README.md). Mỗi file ghi input và output mong đợi hoặc điều kiện bỏ qua kèm lý do. Danh sách tên ca phải trùng nhau giữa 9 thư mục. Khi đủ bộ dự kiến sẽ có 5 ca × 9 điểm nối = 45 JSON.

| Ca | Nguồn | Điều kiện đạt chính | Trạng thái |
| --- | --- | --- | --- |
| `deadline_reduction` | Fixture hiện có | Thay cả đơn vị, giữ hai bản toàn văn, kiểm chứng offset, nhận định và bằng chứng đến UI | Đã có fixture tại 9 điểm nối |
| Sửa cục bộ | `case_06` | Giữ toàn bộ vị trí thuộc chỉ dẫn được chọn, dựng toàn văn trước/sau từng đơn vị và giữ nguyên văn chỉ dẫn S | Chuẩn bị sau khi hoàn thiện docs |
| Bổ sung | `case_08` | Giữ vị trí chèn và kiểm tra nội dung được thêm giữa hai trạng thái của cùng đơn vị chứa | Chuẩn bị sau khi hoàn thiện docs |
| Bãi bỏ | `case_07` | Giữ đầy đủ đích của chỉ dẫn được chọn và đối chiếu phần bị bỏ trong toàn văn đơn vị chứa | Chuẩn bị sau khi hoàn thiện docs |
| Thiếu đích | Biến thể ca sửa cục bộ | Giữ chỉ dẫn, lý do cần kiểm tra và mục báo cáo. Bỏ qua bước thiếu điều kiện | Chuẩn bị sau khi hoàn thiện docs |

Tách ba kết quả khi báo cáo: fixture qua contract, tích hợp với đầu ra thật, và đánh giá chất lượng trên dữ liệu có nhãn. Điều phối đánh giá do Đức Anh phụ trách. Sau phiên 1, dùng báo cáo từng module để bổ sung ca lỗi và tiêu chí chấm còn mở.

## 7. Mẫu hoàn thiện từng ca kiểm tra

Mỗi ca cụ thể cần ghi đủ:

- Mã ca và mục TEP liên quan; quyết định CN/LK, yêu cầu hoặc phần đặc tả được kiểm tra.
- Mục đích, rủi ro, người thực hiện và người review.
- Điều kiện chạy, phiên bản contract và đường dẫn dữ liệu/fixture.
- Expected output hoặc quy tắc chấp nhận, nguồn xác nhận và phần chưa chắc chắn.
- Lệnh hoặc các bước chạy; dependency và cấu hình liên quan.
- Actual output, trạng thái đạt/chưa đạt/bị chặn, liên kết bằng chứng và lỗi cần xử lý.

Nếu quyết định còn mở, ghi rõ phần bị chặn và mã quyết định; không tự điền trường dữ liệu như đã được thông qua.

## 8. Dữ liệu nhãn và đánh giá chất lượng

### 8.1. Chuẩn bị dữ liệu

Giữ nguồn, vai trò tài liệu, phiên bản, chất lượng chuyển đổi và tài liệu tham chiếu. Phân biệt dữ liệu giả định phục vụ kiểm tra logic với file thật phục vụ kiểm tra khả năng xử lý. Đáp án phải có căn cứ và review phù hợp, không lấy đầu ra thuật toán làm nhãn chuẩn tự động.

Trước phép đánh giá độc lập, thống nhất chia dữ liệu phát triển/kiểm thử và tránh rò rỉ giữa các văn bản thuộc cùng nguồn hoặc chuỗi sửa đổi. Quy mô và cách chia còn chờ xác nhận theo dữ liệu thực tế.

### 8.2. Phép đo cần đề xuất và chốt

| Phạm vi | Câu hỏi đánh giá | Chi tiết còn phải chốt |
| --- | --- | --- |
| Parser/linker | Nội dung và vị trí đích được giữ/tìm đúng đến đâu? | Đơn vị đối chiếu, xử lý khớp một phần và các ca mơ hồ |
| Retrieval/context | Có tìm đủ căn cứ cần thiết và giữ đúng nguồn không? | Bộ nguồn tham chiếu, tiêu chí đủ căn cứ và cách chấm nhiều đoạn hợp lệ |
| Thay đổi ngữ nghĩa | Tìm đúng và bỏ sót những nhận định nào? | Đơn vị thay đổi, TP/FP/FN và Precision/Recall/F1 khi phù hợp; áp dụng matching 1–1 trước, matching 1–n bổ sung sau khi hoàn thành 1–1 |
| Mức tác động | Nhận diện thay đổi trọng yếu và mức độ đúng đến đâu? | Rubric, định nghĩa trọng yếu, cách tính recall và mẫu số |
| Giải thích/bằng chứng | Kết luận có được nguồn hỗ trợ và nêu đúng giới hạn không? | Rubric review, người review và cách giải quyết bất đồng |
| Hiệu năng/tài nguyên | Luồng mất bao lâu, tốn tài nguyên hoặc chi phí nào? | Môi trường, cách lặp, cache, model/embedding và cách tổng hợp |

Các ngưỡng Change F1 ≥ 90% và Critical Change Recall ≥ 95% là dự tính và có thể thay đổi sau khi hoàn thiện test_evaluation_plan.md; chưa phải ngưỡng nghiệm thu chính thức. Kế hoạch xác định đơn vị đánh giá, matching, công thức, cách xử lý lỗi/chưa xác định, số mẫu hợp lệ và cách báo cáo kết quả. Sau khi hoàn thiện kế hoạch, nhóm xác nhận ngưỡng chính thức trước đánh giá độc lập; không sửa ngưỡng hoặc cách tính sau khi thấy kết quả chỉ để tuyên bố đạt.

Trong matching 1–1, mỗi dự đoán được ghép tối đa với một nhãn chuẩn và mỗi nhãn chuẩn được ghép tối đa với một dự đoán; không tính trùng. Các trường hợp chia/gộp cần matching 1–n được ghi nhận để phát triển sau, chưa áp dụng cách tính 1–n trong đợt hiện tại.

### 8.3. So sánh phương pháp

Owner đề xuất baseline đơn giản, phù hợp với câu hỏi cần kiểm chứng. Ví dụ có thể so sánh cách chọn ngữ cảnh trực tiếp với cách bổ sung retrieval, nếu cả hai có cùng nhiệm vụ và đầu vào có thể so sánh. Đây là gợi ý thiết kế thí nghiệm, chưa chốt phương án cụ thể.

Giữ cùng dữ liệu và điều kiện so sánh; ghi các khác biệt cấu hình. Phân tích lỗi theo nhóm tình huống và phân biệt lỗi bắt nguồn từ Parser/linker/context với lỗi Semantic Diff/Scorer. Có thể chạy riêng bước sau bằng đầu vào chuẩn đã review để hỗ trợ tìm nguyên nhân; kết quả đó không thay thế đánh giá toàn luồng.

## 9. Điều kiện bàn giao và báo cáo

Ghi riêng kết quả validator, kết quả luồng có mock và kết quả gọi dịch vụ thật. Đánh giá chất lượng nghiệp vụ dùng tập có nhãn đã review và phương pháp ghi ở mục 8.

Một phần đủ điều kiện bàn giao khi có đặc tả liên quan đã chốt, code, mẫu vào ra, kiểm tra phù hợp, kết quả, cách chạy và giới hạn; bên nhận sử dụng được đầu ra thật. Trạng thái đủ đặc tả, đã hiện thực và đã tích hợp/kiểm tra phải được ghi riêng.

Mỗi đợt đo cần lưu commit, cấu hình, dependency/model khi có, phiên bản dữ liệu/nhãn, cách tính và kết quả. Nếu dùng lỗi test để chỉnh phương pháp, công bố việc đó; chỉ gọi một lần đánh giá mới là độc lập khi dùng dữ liệu chưa được dùng để chỉnh.

evaluation_report.md được tạo khi có kết quả thực tế. Báo cáo gồm phạm vi và phiên bản, phương pháp đo, số mẫu, kết quả, so sánh baseline nếu có, lỗi tiêu biểu, giới hạn và việc cần xử lý. Không cần đợi toàn bộ dự án xong mới ghi kết quả từng đợt, nhưng phải nêu rõ phạm vi đã đo.

## 10. Việc cần bổ sung sau đề xuất owner

| Việc cần chốt | Bên cần tham gia | Khi nào cập nhật |
| --- | --- | --- |
| Người thực hiện và người review từng phần | Đức Anh đã được xác nhận điều phối; các owner liên quan phối hợp | Bổ sung trước khi phân công chạy toàn luồng/chính thức |
| Contract, fixture và hành vi lỗi | Bên giao, bên nhận; schema/API khi liên quan | Sau quyết định CN/LK tương ứng |
| Ca kiểm tra, expected output và lệnh chạy | Owner và reviewer | Khi phần module đủ đặc tả/có implementation |
| Nhãn, rubric, dữ liệu và cách tính metric; matching 1–1 | Đức Anh điều phối; Dũng, owner phân tích và reviewer phối hợp | Trước đánh giá chính thức; ngưỡng dự tính Change F1 ≥ 90% và Critical Change Recall ≥ 95% có thể thay đổi sau khi hoàn thiện test_evaluation_plan.md; matching 1–n bổ sung sau khi hoàn thành 1–1 |
| Baseline và thiết kế thí nghiệm | Owner phương pháp, bên tích hợp và reviewer | Trước chạy so sánh |
| Cấu hình và kiểm tra LightRAG thật | Dũng + Đức Anh và các bên liên quan | Theo thứ tự chốt LK-13 |

Các mục chờ trên không tự tạo quyết định mới hoặc thay phân công đã chốt. Sau khi module.md hoàn thiện, rà lại kế hoạch để không thiếu điểm nối, lỗi và điều kiện bàn giao; không phải viết lại toàn bộ kế hoạch từ đầu.

## Kiểm tra hợp đồng chung độc lập

Các test schema chạy từ repo root: `python -m unittest discover -s test/schema_suite -p "test_*.py" -v` sau khi cài `requirements.txt`. Fixture nguồn dùng block:N, có báo cáo thành công, từng biến thể sai schema/nguồn/scoring và report nền main chưa có runner. Đây là kiểm tra hợp đồng, không phải đánh giá chất lượng mô hình hoặc xác nhận Pipeline đã nối validation. Các giới hạn validator giữ nguyên và ví dụ cần review ở [SRS mục 1.7](srs.md).
