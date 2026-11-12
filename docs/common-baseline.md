# Nền DOCX chung — trạng thái và bàn giao

## Căn cứ

Đồng bộ ngày 12/11/2026 trên `ducanh_bachdung/integrate_LightRAG`. Tài liệu lấy từ `bachdung/docs` tại **6dbda8da7a050e4d21f354c5e59765244e2f176a**; code đối chiếu tại **c192f43b785f9a38a64c8ca6e4166c0e40622528**, gồm sửa Linker `f0ed2d7`. Schema giữ nguyên so với main `f76610e`. Tài liệu này không xác nhận thay đổi đã commit/push hoặc merge.

Quyết định Đức Anh: lấy tài liệu Dũng làm nền, một bộ fixture tại 9 điểm nối; ca 30 → 15 ngày giữ mức tác động null và report PARTIAL; giữ thiết kế index song song Linker/Text Diff rồi query; giữ báo cáo lịch sử. ADD/REPEAL, nhiều đích, model và retrieval thật tiếp tục sau merge nền DOCX.

## Cách chạy và luồng hiện tại

Theo [README gốc](../README.md#chạy-nền-docx-hiện-tại): cài `requirements-demo.txt`, chạy `python -m uvicorn backend.demo:app --host 127.0.0.1 --port 8000`, mở http://127.0.0.1:8000. Không cần model, API key, Node hoặc LightRAG Server cho luồng này. `backend.main:app` chưa gắn runner và trả 501 sau đầu vào hợp lệ; tên module main không phải tên nhánh Git.

Upload V1/S/tham chiếu → Pipeline đọc/Parser → Adapter kho nguồn/Clause → Linker hẹp → Text Diff song song Context không retrieval → Semantic quy tắc giới hạn → Scorer → validation → ComparisonReport → giao diện. Demo tính kết quả từ DOCX, không dùng đáp án fixture.

## Đối chiếu thiết kế và code

| Phần | Code thực tế | Việc sau merge và người phụ trách |
| --- | --- | --- |
| Reader/Parser/Adapter | DOCX thật; `BoundaryData` chứa documents/clauses/units, giữ nguyên text và source_ref | Thọ review PDF/mapping nguồn. Fixture Adapter → Linker chưa mô tả units; cần binding/adapter nội bộ, không đổi schema |
| Linker | Xác minh số hiệu hoặc tên header chính xác; sửa cụm từ duy nhất/đoạn QUOTED tại một đích; DERIVED không giả quote S | Thọ triển khai ADD/REPEAL bằng đơn vị chứa, nhiều đích, thao tác phụ thuộc. Chưa bao phủ mọi kiểu câu; không coi không nhận diện được là không có thay đổi |
| Text Diff | TextDiffResult, offset ký tự Python; kiểm thử dựng lại after_text | Ngọc Anh review ca mở rộng và hai chuỗi cùng đơn vị |
| Context/LightRAG | Chunk/registry/client HTTP, kiểm thử mô phỏng; bridge chạy Context và Text Diff song song; demo client=None | Đức Anh + Dũng tách index/query, query nhận TextDiffResult sau hai nhánh; Ngọc Anh bàn giao diff; kiểm chứng dịch vụ thật sau chọn môi trường/model |
| Semantic/AI Adapter | Rule hẹp; demo chưa xác nhận context đầy đủ, kết luận chưa rõ giữ null/review; AI Adapter chưa có implementation | Tuấn Anh hoàn thiện rule/model; Dũng + Đức Anh gọi model/validate output; không ép context_complete để sinh nhãn |
| Scorer | Null khi chưa đủ căn cứ; có rule HIGH cho ca thời hạn hẹp khi ngữ nghĩa đã xác nhận, demo chưa đi vào nhánh này | Tuấn Anh + Dũng duyệt rubric trước khi bật nhánh chấm mức; fixture 30 → 15 không mặc định MEDIUM/HIGH |
| Pipeline/API | Demo runner validate amendment/source/report; Pipeline nền kiểm tra envelope; HTTP phân biệt FAILED nghiệp vụ và lỗi thực thi | Dũng tích hợp runner chính thức/validation chung; route còn ở main.py, api/compare.py là khung |
| Frontend | HTML/CSS/JavaScript chọn file, diff/quote/source_ref/cảnh báo; report FAILED vẫn hiện item | Tuấn Anh tiếp tục từ demo; React/TypeScript là hướng mục tiêu, chưa bắt buộc trước merge |

Đợt này không thay thứ tự code, schema hoặc validator. Các khoảng cách trên là backlog công khai, không phải tính năng đã nghiệm thu. Source label khi chưa xác minh không phải document_id: code giữ chuỗi gợi ý hoặc rỗng và applicability=UNRESOLVED; bên nhận kiểm tra applicability trước khi xử lý.

## Fixture, dữ liệu và bằng chứng

- [Bộ fixture duy nhất](../data/module_handoff_fixtures/README.md): 9 file deadline_reduction, 2 ca chặn query và 6 ca lỗi. Là JSON giả định; Semantic dự kiến có thể khác output demo, không phải gold pháp lý hoặc retrieval thật.
- Ca chung dùng document_id v1 khi đã xác minh; significance/is_critical=null, có review_reason và report PARTIAL. SUCCESS dành cho ca hoàn tất mọi bước bắt buộc riêng.
- Ba bộ DOCX `data/raw/case_01`–`case_03` được demo kiểm thử. Năm cặp PDF `case_04`–`case_08` còn ở nhánh Dũng `6dbda8d`, chưa nhập local trong đợt docs/fixture này. Các ca dự kiến trong kế hoạch không là dữ liệu đã chạy được.
- JSON/ảnh `data/demo-results` là bằng chứng lịch sử ngày 11/11, không tự cập nhật khi code đổi. [Báo cáo schema lịch sử](schema-verification-report.md), [web demo](local-web-demo.md), [thử nghiệm LightRAG](lightrag-integration-report.md) được giữ nguyên ý nghĩa bằng chứng theo mốc, không thay kết quả kiểm thử mới.

## Kiểm chứng

Từ repo root sau khi cài dependency demo:

```powershell
python -m pip check
python -m unittest discover -s test/schema_suite
python -m unittest discover -s test/context_suite
python -m unittest discover -s test/demo_suite
python -m unittest discover -s test/handoff_suite
```

Kiểm tra lại ngày 12/11 sau đồng bộ docs/fixture, Python 3.14.8 trên Windows, code c192f43 và thay đổi tài liệu/fixture local:

| Bộ | Kết quả |
| --- | --- |
| pip check | Không có dependency hỏng |
| Schema | 51 ca: 49 đạt, 2 expected failures đã biết |
| Context | 26 ca: 24 đạt, 2 dịch vụ thật bỏ qua |
| Demo DOCX/API | 30/30 đạt; ba bộ DOCX giữ số mục/có Text Diff lần lượt 2/1, 1/1, 13/13 |
| Fixture và hàm thật | 8/8 đạt: nhất quán nguồn/ID/offset/mapping, Text Diff đúng fixture, Scorer giữ null/review trên ca chung, classifier trả PARTIAL |
| Liên kết Markdown | Không có đích file tương đối bị thiếu trong README/docs/README fixture |

Tổng 115 ca: 111 đạt, 2 expected failures và 2 skipped; không gọi đó là 115 ca đều đạt. Expected failure là validator chưa ép change_id duy nhất toàn report và reconstruction toàn diff. Test fixture không xác nhận đã nối 9 module thật hoặc chất lượng pháp lý. Kiểm thử API dùng TestClient với DOCX thật/tự dựng, không phải lần chụp trình duyệt mới.

Đã kiểm tra lại bốn bộ trong bản sao tạm chỉ chứa file tracked và tài liệu/fixture/test mới sẽ bàn giao, không mang .git, .env hoặc file local ngoài phạm vi. Kết quả giữ nguyên 111 đạt/2 expected failures/2 skipped. Dùng lại venv hiện tại, không phải lần cài dependency mới trên máy khác; chưa xác nhận mọi phiên bản Python được README cho phép đều chạy được. Không thấy lỗi chặn trong phạm vi nền DOCX đã thống nhất, nhưng không dùng kết quả này để nghiệm thu toàn bộ thiết kế.

Chưa kiểm chứng LightRAG/model thật, PDF xuyên luồng, đánh giá có gold hoặc benchmark chất lượng. Trình duyệt có bằng chứng lịch sử; đợt này không tự nhận đã thử lại tải xuống/di động. Deadline cooperative, khóa so sánh theo process: chạy một worker cho nền local; chưa xác nhận phục vụ nhiều người dùng.

## Điều kiện đưa vào main làm nền

1. Commit/push tài liệu và fixture, mở PR để Dũng/owner review. Thay đổi local chưa tự đến máy các thành viên.
2. Giữ lệnh demo, input API và schema; kiểm thử hồi quy đạt. Người nhận chạy README trên máy mình trước khi báo bàn giao.
3. Thông báo main là nền DOCX giới hạn. Thành viên cập nhật nhánh task từ main sau khi PR merge, bảo toàn code đang làm của họ; không reset nhánh cá nhân.

Giữ kế hoạch 3 phiên của Dũng, nhận việc theo bảng trên. Không cần làm lại module đã có hoặc nhập nhánh cũ để thay implementation bằng khung.
