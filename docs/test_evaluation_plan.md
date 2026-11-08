# Kế hoạch kiểm thử và đánh giá

**Dự án:** Legal Document Change Detection — POCS, Nhóm 4
**Phiên bản:** 0.1 — Khung chuẩn bị song song với quyết định và đặc tả module
**Ngày tạo:** 08/11/2026
**Trạng thái:** Khung kế hoạch đang hoàn thiện; Đức Anh điều phối. Hiện xác định cách đánh giá, chưa có ngưỡng chất lượng đạt/chưa đạt; contract và chi tiết phép đo còn chờ hoàn thiện.

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
| Hoàn thiện từng phần module.md | Điền input/output, expected output, ca kiểm tra, người thực hiện và reviewer | Contract, schema và fixture cùng cách hiểu |
| Có implementation | Tự kiểm tra module; kiểm tra điểm nối với đầu ra thật; tích hợp sớm | Có kết quả và giới hạn, không chỉ có code test |
| Chuẩn bị đánh giá chính thức | Cố định phiên bản, cấu hình, dữ liệu, nhãn, matching và phép đo | Các phần phụ thuộc đã rõ; không còn lỗi chặn phép đo |


Một phần có thể sẵn sàng trước phần khác. Không cần chờ toàn bộ decision.md hoặc module.md hoàn tất để kiểm tra module có đủ đặc tả. Riêng LK-13 giữ thứ tự chốt đã quy định trong decision.md: có thể khảo sát và chuẩn bị ca kiểm tra, nhưng chỉ chốt chi tiết còn lại sau các quyết định khác.

## 4. Trách nhiệm và điều phối

Phân công chức năng phải theo LK-01 đã chốt, không sao chép các bảng cũ chưa đồng bộ trong module.md.

| Phạm vi | Trách nhiệm hiện có | Trách nhiệm kiểm chứng đề xuất |
| --- | --- | --- |
| Xử lý tài liệu, Parser, adapter và linker | Thọ | Tự kiểm tra từ nguồn thật; bên nhận review output và vị trí nguồn |
| Text Diff | Ngọc Anh | Tự kiểm tra vùng đổi, offset và khả năng tái tạo khi contract cho phép; Tuấn Anh review dữ liệu nhận |
| Semantic Diff và Scorer | Tuấn Anh | Kiểm tra ngữ nghĩa, bằng chứng, ranh giới mức và trạng thái thiếu căn cứ; Dũng review phần dùng để tổng hợp/nghiệp vụ |
| Tích hợp, Pipeline và API nghiệp vụ | Dũng | Kiểm tra tổng hợp, truyền cảnh báo/lỗi và luồng API; phối hợp bên cung cấp và frontend |
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
| TEP-10 | Tổng hợp/API | Bỏ mất chỉ dẫn chưa phân tích, mất cảnh báo, nhầm lỗi với không có thay đổi | Fixture báo cáo và bảng null/rỗng/lỗi/trạng thái |
| TEP-11 | Toàn luồng | Một ca đủ căn cứ, một ca thiếu căn cứ, một ca lỗi; bổ sung tài liệu khi chức năng đã được chốt | Báo cáo kỳ vọng từ file thật, nguồn và phạm vi xử lý |
| TEP-12 | LightRAG và vòng đời | Sẵn sàng nhập/query, mapping, cách ly lượt chạy, cleanup và lỗi dịch vụ | Release/API thực tế theo LK-13; chưa chốt payload hoặc cấu hình trong kế hoạch này |

Mỗi module chọn các ca liên quan; không bắt buộc mọi test gọi mô hình hoặc dịch vụ thật. Kiểm tra dịch vụ thật vẫn cần có khi xác nhận tích hợp thật. Mock/fixture phải được đánh dấu rõ.

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

Hiện chưa có ngưỡng chất lượng đạt/chưa đạt. Kế hoạch xác định đơn vị đánh giá, matching, công thức, cách xử lý lỗi/chưa xác định, số mẫu hợp lệ và cách báo cáo kết quả. Không áp dụng các ngưỡng từ tài liệu cũ cho giai đoạn hiện tại. Không sửa cách tính sau khi thấy kết quả chỉ để tuyên bố đạt.

Trong matching 1–1, mỗi dự đoán được ghép tối đa với một nhãn chuẩn và mỗi nhãn chuẩn được ghép tối đa với một dự đoán; không tính trùng. Các trường hợp chia/gộp cần matching 1–n được ghi nhận để phát triển sau, chưa áp dụng cách tính 1–n trong đợt hiện tại.

### 8.3. So sánh phương pháp

Owner đề xuất baseline đơn giản, phù hợp với câu hỏi cần kiểm chứng. Ví dụ có thể so sánh cách chọn ngữ cảnh trực tiếp với cách bổ sung retrieval, nếu cả hai có cùng nhiệm vụ và đầu vào có thể so sánh. Đây là gợi ý thiết kế thí nghiệm, chưa chốt phương án cụ thể.

Giữ cùng dữ liệu và điều kiện so sánh; ghi các khác biệt cấu hình. Phân tích lỗi theo nhóm tình huống và phân biệt lỗi bắt nguồn từ Parser/linker/context với lỗi Semantic Diff/Scorer. Có thể chạy riêng bước sau bằng đầu vào chuẩn đã review để hỗ trợ tìm nguyên nhân; kết quả đó không thay thế đánh giá toàn luồng.

## 9. Điều kiện bàn giao và báo cáo

Một phần đủ điều kiện bàn giao khi có đặc tả liên quan đã chốt, code, mẫu vào ra, kiểm tra phù hợp, kết quả, cách chạy và giới hạn; bên nhận sử dụng được đầu ra thật. Trạng thái đủ đặc tả, đã hiện thực và đã tích hợp/kiểm tra phải được ghi riêng.

Mỗi đợt đo cần lưu commit, cấu hình, dependency/model khi có, phiên bản dữ liệu/nhãn, cách tính và kết quả. Nếu dùng lỗi test để chỉnh phương pháp, công bố việc đó; chỉ gọi một lần đánh giá mới là độc lập khi dùng dữ liệu chưa được dùng để chỉnh.

evaluation_report.md được tạo khi có kết quả thực tế. Báo cáo gồm phạm vi và phiên bản, phương pháp đo, số mẫu, kết quả, so sánh baseline nếu có, lỗi tiêu biểu, giới hạn và việc cần xử lý. Không cần đợi toàn bộ dự án xong mới ghi kết quả từng đợt, nhưng phải nêu rõ phạm vi đã đo.

## 10. Việc cần bổ sung sau đề xuất owner

| Việc cần chốt | Bên cần tham gia | Khi nào cập nhật |
| --- | --- | --- |
| Người thực hiện và người review từng phần | Đức Anh đã được xác nhận điều phối; các owner liên quan phối hợp | Bổ sung trước khi phân công chạy toàn luồng/chính thức |
| Contract, fixture và hành vi lỗi | Bên giao, bên nhận; schema/API khi liên quan | Sau quyết định CN/LK tương ứng |
| Ca kiểm tra, expected output và lệnh chạy | Owner và reviewer | Khi phần module đủ đặc tả/có implementation |
| Nhãn, rubric, dữ liệu và cách tính metric; matching 1–1 | Đức Anh điều phối; Dũng, owner phân tích và reviewer phối hợp | Trước đánh giá chính thức; chưa yêu cầu ngưỡng chất lượng, matching 1–n bổ sung sau khi hoàn thành 1–1 |
| Baseline và thiết kế thí nghiệm | Owner phương pháp, bên tích hợp và reviewer | Trước chạy so sánh |
| Cấu hình và kiểm tra LightRAG thật | Dũng + Đức Anh và các bên liên quan | Theo thứ tự chốt LK-13 |

Các mục chờ trên không tự tạo quyết định mới hoặc thay phân công đã chốt. Sau khi module.md hoàn thiện, rà lại kế hoạch để không thiếu điểm nối, lỗi và điều kiện bàn giao; không phải viết lại toàn bộ kế hoạch từ đầu.
