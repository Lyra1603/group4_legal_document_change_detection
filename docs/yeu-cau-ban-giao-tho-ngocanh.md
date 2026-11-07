# Yêu cầu bàn giao từ Thọ và đầu ra phân tích của Ngọc Anh

Ngày cập nhật: 07/11/2026.

Tài liệu này thống nhất dữ liệu Thọ cần bàn giao để Ngọc Anh so sánh câu chữ, phân tích thay đổi ngữ nghĩa, phân loại và đánh giá mức độ quan trọng. Các yêu cầu bàn giao dưới đây là đề xuất để phối hợp; phạm vi tự động hóa hiện tại được ghi riêng để không nhầm yêu cầu với tính năng đã hoàn thành.

## 1. Luồng xử lý và trách nhiệm

```text
Thọ trích xuất tài liệu và xác định mục sửa đổi cùng điều khoản đích
    → Ghép nội dung trước và sau, giữ câu lệnh sửa đổi và nguồn
    → Bổ sung, xác nhận ngữ cảnh và hiệu lực liên quan
    → Ngọc Anh tính Text Diff
    → Ngọc Anh phân tích Semantic Diff
    → Ngọc Anh phân loại và chấm mức độ
    → Backend tổng hợp báo cáo, frontend hiển thị để kiểm tra
```

- **Thọ:** bàn giao nội dung trích xuất và thông tin nguồn. Đầu ra lý tưởng có từng mục sửa đổi đã ghép đúng với điều khoản gốc. Nếu Thọ chỉ trả danh sách điều đã trích xuất, nhóm phải phân công thêm bước ghép đích và chuẩn bị nội dung trước–sau.
- **Ngọc Anh:** nhận từng mục đã chuẩn bị; xác định thay đổi câu chữ, ý nghĩa, nhóm và mức độ trong phạm vi phương pháp hỗ trợ; giữ bằng chứng và báo những chỗ chưa đủ căn cứ.
- **Người chuẩn bị ngữ cảnh, có thể là Dũng:** bổ sung hoặc xác nhận định nghĩa, điều kiện, ngoại lệ, dẫn chiếu và hiệu lực. Cần thống nhất trách nhiệm này, không mặc định Thọ phải làm toàn bộ.
- **Bên tích hợp, có thể là Đức Anh:** chuyển kết quả module sang schema báo cáo/API chính thức, giữ nguyên các giá trị chưa xác định và cảnh báo.

Thọ không cần kết luận đổi nghĩa hay chấm mức độ trước khi bàn giao. Đó là phần phân tích của Ngọc Anh.

## 2. Đầu ra lý tưởng của Thọ

Đơn vị bàn giao là **một mục sửa đổi có mã riêng**, đã xác định đích và nội dung tương ứng trước–sau. Không chỉ bàn giao các chữ hoặc số thay đổi.

| Thông tin | Trường dự kiến | Yêu cầu |
|---|---|---|
| Mã mục sửa đổi | `amendment_id` | Duy nhất, dùng liên kết đầu vào, kết quả và lỗi cần kiểm tra. |
| Văn bản đích | `target_document` | Mã văn bản gốc bị sửa đổi. |
| Điều khoản đích | `target_unit_ids`, `target_locator` | Xác định đúng điều/khoản/điểm; có mô tả dễ đọc và định danh truy vết được. |
| Loại thao tác | `operation` | `AMEND`: sửa đổi; `ADD`: bổ sung; `REPEAL`: bãi bỏ. |
| Trạng thái áp dụng | `applicability` | `APPLIES`: đúng văn bản đích; `UNRESOLVED`: chưa chắc; `OTHER_DOCUMENT`: thuộc văn bản khác. |
| Nội dung trước | `before_text` | Nguyên văn nội dung cũ, đủ câu/khoản để hiểu nghĩa. |
| Nội dung sau | `after_text` | Nội dung mới tương ứng, cùng phạm vi so sánh với nội dung trước. |
| Cơ sở nội dung sau | `after_basis` | `QUOTED`: trích nguyên văn; `DERIVED`: suy ra từ câu lệnh; `UNRESOLVED`: chưa xác định. |
| Câu lệnh sửa đổi | `instruction` | Nguyên văn yêu cầu sửa đổi, kèm `document_id`, `source_refs`, `quote`. |
| Bằng chứng | `evidence` | Mỗi bằng chứng có mã tài liệu, vị trí nguồn và trích dẫn; truy ngược được về tài liệu thực tế. |
| Ngữ cảnh | `context` | Định nghĩa, điều kiện, ngoại lệ, bằng chứng và dẫn chiếu liên quan; ghi trạng thái dẫn chiếu đã có hay còn thiếu. |
| Hiệu lực và chuyển tiếp | `effect_info` | Nội dung liên quan nếu có, cùng cảnh báo cần kiểm tra. |
| Điểm chưa chắc chắn | `needs_review`, `review_reason` | Ghi rõ thiếu dữ liệu, đích mơ hồ, nhiều đích có thể khớp hoặc lỗi trích xuất. |

### Quy tắc nội dung và nguồn

1. Giữ cả câu hoặc khoản chứa phần sửa đổi để biết thay đổi áp dụng cho hành vi gì, của ai. Ví dụ chỉ có `30 → 15` thì chưa đủ để đánh giá.
2. Ghép đúng đích và đúng phạm vi hai phía. Không ghép điều khoản chỉ vì có cùng số điều hoặc chứa cùng cụm từ.
3. Giữ nguyên văn trích xuất để đối chiếu. Nếu làm sạch dữ liệu, cần giữ bản nguồn hoặc ánh xạ về nội dung và vị trí gốc; không âm thầm sửa chữ, dấu câu hoặc xuống dòng.
4. Nguồn phải chỉ rõ văn bản và vị trí thực tế của đoạn gốc, câu lệnh sửa đổi và đoạn mới nếu được trích nguyên văn. Không tạo vị trí nguồn giả.
5. Nếu dựng câu mới bằng cách áp dụng lệnh thay từ, phải ghi `DERIVED`; không coi câu đó là trích nguyên văn trong văn bản sửa đổi.
6. Phân biệt thiếu dữ liệu (`null`) với chuỗi rỗng (`""`). Với bổ sung/bãi bỏ, giữ `operation` để người nhận hiểu lý do một phía không có nội dung.
7. Khi chưa xác định được, giữ cảnh báo và lý do; không tự chọn đích hoặc dựng nội dung như đã chắc chắn.

### Câu thống nhất với Thọ

> Mỗi mục bạn trả cần có điều khoản đích, loại sửa đổi, nội dung trước và sau đã ghép đúng, câu lệnh sửa đổi, vị trí nguồn và cờ báo những chỗ chưa chắc. Giữ đủ câu hoặc khoản để đánh giá ý nghĩa; nội dung sau suy ra thì ghi rõ.

## 3. Ví dụ đầu vào bàn giao

Ví dụ dưới đây chỉ minh họa cấu trúc, không lấy từ văn bản pháp luật thật. Các vị trí nguồn khi triển khai phải truy ngược được về tài liệu thực tế.

### Trường hợp nội dung sau được suy ra

```text
Mã mục: amend-001
Đích: Khoản 2 Điều 5 của văn bản A
Thao tác: AMEND
Trạng thái: APPLIES

Trước: Cơ quan phải giải quyết hồ sơ trong thời hạn 30 ngày.
Câu lệnh ở B: Thay cụm từ “30 ngày” bằng “15 ngày” tại khoản 2 Điều 5.
Sau: Cơ quan phải giải quyết hồ sơ trong thời hạn 15 ngày.
Cơ sở sau: DERIVED

Nguồn: Đoạn gốc ở A và câu lệnh sửa đổi ở B, kèm vị trí cụ thể.
```

Câu sau được dựng từ câu lệnh thay cụm từ, nên phải là `DERIVED`. Baseline hiện tại giữ lại trường hợp này nhưng chưa tự kết luận ngữ nghĩa hoặc chấm mức độ.

### Trường hợp nội dung sau được trích nguyên văn

```json
{
  "amendment_id": "amend-002",
  "operation": "AMEND",
  "applicability": "APPLIES",
  "target_document": "van-ban-A",
  "target_unit_ids": ["van-ban-A:dieu-5:khoan-2"],
  "target_locator": "Khoản 2 Điều 5",
  "before_text": "Cơ quan phải giải quyết hồ sơ trong thời hạn 30 ngày.",
  "after_text": "Cơ quan phải giải quyết hồ sơ trong thời hạn 15 ngày.",
  "after_basis": "QUOTED",
  "instruction": {
    "document_id": "van-ban-B",
    "source_refs": ["dieu-1:khoan-2"],
    "quote": "Sửa đổi khoản 2 Điều 5 như sau: Cơ quan phải giải quyết hồ sơ trong thời hạn 15 ngày."
  },
  "evidence": [
    {
      "document_id": "van-ban-A",
      "source_refs": ["dieu-5:khoan-2"],
      "quote": "Cơ quan phải giải quyết hồ sơ trong thời hạn 30 ngày."
    }
  ],
  "context": {
    "general_context": "Quy định về thời hạn giải quyết hồ sơ.",
    "evidence": [],
    "references": []
  },
  "effect_info": [],
  "needs_review": false,
  "review_reason": ""
}
```

Danh sách dẫn chiếu rỗng hoặc `needs_review=false` tự nó không chứng minh đã đủ ngữ cảnh. Chỉ xác nhận `context_complete=True` sau khi người phụ trách thực sự kiểm tra định nghĩa, điều kiện, ngoại lệ và dẫn chiếu liên quan.

## 4. Yêu cầu đối với đầu ra của Ngọc Anh

Đầu ra cần cho biết **sửa đổi ở đâu, thay chữ gì, có đổi nghĩa không, thuộc nhóm nào, mức độ ra sao và căn cứ để kết luận**.

| Yêu cầu | Nội dung cần trả |
|---|---|
| Truy vết mục sửa đổi | Giữ amendment gốc, mã mục, văn bản và điều khoản tương ứng để liên kết đầu vào với kết quả. |
| So sánh câu chữ | Các đoạn thêm/xóa/thay thế, nội dung cũ/mới và vị trí trong hai chuỗi. |
| Kết luận ý nghĩa | `is_meaningful_change=true` khi xác định có đổi nghĩa, `false` khi xác định không đổi nghĩa, `null` khi chưa đủ căn cứ. |
| Giải thích tác động | Mô tả thay đổi; danh sách `aspects` với nhóm, giá trị cũ/mới và diễn giải từng khía cạnh xác định được. |
| Phân loại | Nhóm của từng khía cạnh và `category` tổng thể theo quy tắc ưu tiên. |
| Đánh giá mức độ | `significance` là `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` hoặc `null`; có `is_critical` và lý do. |
| Bằng chứng kiểm chứng | Giữ trích dẫn, mã tài liệu và vị trí nguồn liên quan; không gán nội dung suy ra thành nguyên văn. |
| Cảnh báo | `needs_review` và `review_reason` rõ ràng cho dữ liệu thiếu, ngữ cảnh chưa đủ, kết luận chưa chắc hoặc ngoài phạm vi hỗ trợ. |

### Quy tắc phân loại và mức độ

Khi có nhiều khía cạnh đã xác định, category tổng thể chọn nhóm xuất hiện đầu tiên trong thứ tự pilot sau; mọi aspects vẫn được giữ:

1. `CONSEQUENCES_SANCTIONS`: hậu quả, chế tài.
2. `RIGHTS_DUTIES_ACTIONS`: quyền, nghĩa vụ, hành vi.
3. `SUBJECT_OBJECT`: chủ thể, đối tượng.
4. `CONDITIONS_EXCEPTIONS`: điều kiện, ngoại lệ.
5. `PROCEDURE_AUTHORITY`: thủ tục, thẩm quyền.
6. `TIME_QUANTITY`: thời gian, số lượng.
7. `SCOPE_EFFECT_TRANSITION`: phạm vi, hiệu lực, chuyển tiếp.
8. `DEFINITIONS_REFERENCES`: định nghĩa, dẫn chiếu.

Đây là thứ tự chọn nhóm chính, không phải thứ tự mức độ nghiêm trọng. `WORDING_ONLY` chỉ dùng khi đã xác định không đổi nghĩa, không suy ra từ danh sách aspects rỗng.

Mức độ phải dựa vào rubric trong [hướng dẫn gán nhãn](data-annotation-guide.md) và [SRS](srs.md). Không chấm chỉ dựa vào số chữ thay đổi hoặc thao tác thêm/xóa điều. `MEDIUM` cần căn cứ về cách thực hiện tương đương; `CRITICAL` cần reviewer xác nhận đảo chiều hoặc loại bỏ toàn bộ nghĩa vụ/quyền cốt lõi.

### Ví dụ đầu ra khi đủ điều kiện của baseline

Với ví dụ `amend-002` có nội dung sau trích nguyên văn, nguồn hợp lệ và ngữ cảnh thực sự đầy đủ:

```text
Mục sửa đổi: amend-002
Đích: Khoản 2 Điều 5
Thay đổi chữ: 30 → 15, kèm offset trong hai chuỗi
Có đổi nghĩa: true
Khía cạnh: Thời hạn giải quyết hồ sơ
Giá trị cũ: 30 ngày
Giá trị mới: 15 ngày
Nhóm: TIME_QUANTITY
Mức độ: HIGH
Là CRITICAL: false
Lý do: Thay đổi thời hạn thực hiện theo rubric pilot
Bằng chứng: Trích dẫn và vị trí nguồn của hai phía
```

Không dùng kết luận `HIGH` này cho mọi thay đổi con số, tiền phạt, ngày hiệu lực hoặc nhiều thay đổi đồng thời. Với ví dụ `amend-001` có `DERIVED`, baseline hiện tại phải giữ kết luận ngữ nghĩa và mức độ chưa xác định, kèm yêu cầu review.

## 5. Cấu trúc tích hợp hiện tại

Đầu vào là mapping `AmendmentItem` qua:

```python
from src.local_analysis import analyze_amendment

# Chỉ truyền True sau khi ngữ cảnh đã được kiểm tra đầy đủ.
result = analyze_amendment(item, context_complete=True)
```

Kết quả adapter có các phần:

```text
amendment       Mục sửa đổi gốc cùng instruction, evidence, context, effect_info
text_diff       Các thay đổi chữ, hoặc null nếu thiếu một phía
semantic_diff   Các thay đổi ngữ nghĩa và cảnh báo, hoặc null khi bỏ qua phân tích
scoring         Danh sách kết quả phân loại và mức độ cho từng SemanticChange
needs_review    Trạng thái cần kiểm tra tổng hợp
review_reason   Các lý do cần kiểm tra tổng hợp
```

Đây là đầu ra bàn giao module, chưa phải `ComparisonReport` hoặc API hoàn chỉnh. Bên tích hợp cần đối chiếu schema backend thực tế và giữ nguyên `null` cùng cảnh báo.

## 6. Mức đáp ứng hiện tại và giới hạn

| Phần việc | Code hiện tại đáp ứng |
|---|---|
| Text Diff | Thêm/xóa/thay thế với offset ký tự Python theo khoảng `[start, end)`; giữ đầu vào khi tính offset; phân biệt `None` và chuỗi rỗng. |
| Giữ dữ liệu và nguồn | Adapter giữ amendment gốc; ngữ nghĩa nhận nguồn từ đầu vào; quote chỉ được gán khi tìm thấy nguyên văn trong bằng chứng cùng mã tài liệu. |
| Hai đoạn giống nhau | Khi nguồn và ngữ cảnh đủ, hai đoạn giống nhau sau chuẩn hóa NFC và bỏ khoảng trắng đầu/cuối không tạo SemanticChange. Không suy ra toàn bộ văn bản sửa đổi không có thay đổi. |
| Diễn đạt tương đương | Hỗ trợ “chậm nhất vào ngày” ↔ “không muộn hơn ngày” khi phần còn lại giữ nguyên; trả false, WORDING_ONLY, LOW. |
| Đổi thời hạn | Hỗ trợ đúng một số nguyên dương trong cụm “trong thời hạn N ngày”, phần còn lại giữ nguyên; trả true, TIME_QUANTITY, HIGH khi đủ điều kiện. |
| Thiếu dữ liệu hoặc ngoài phạm vi | Giữ kết luận ngữ nghĩa và mức độ chưa xác định, kèm lý do cần review. |
| ADD, REPEAL, DERIVED | Giữ thông tin nhưng chưa tự kết luận ngữ nghĩa đầy đủ; DERIVED không được gán new_quote như nguyên văn. |
| Trạng thái khác | OTHER_DOCUMENT bỏ qua phân tích; UNRESOLVED, thiếu đích, thiếu dẫn chiếu hoặc cảnh báo hiệu lực được chuyển thành yêu cầu review. |

Chưa hoàn tất: phân tích tổng quát tám nhóm, nhiều SemanticChange độc lập, tự chấm MEDIUM/CRITICAL, phương pháp ngữ nghĩa thứ hai và tích hợp trên dữ liệu thật. Adapter không tự đọc file, tìm đích hoặc xác minh hiệu lực.

Bộ kiểm thử hiện tại dùng dữ liệu synthetic để kiểm tra hành vi phần mềm; chưa chứng minh chất lượng pháp lý và chưa đủ để công bố F1/Critical Recall. Xem thêm [tài liệu bàn giao hiện trạng](ngocanh-handover.md).

## 7. Checklist nhận và bàn giao

### Khi nhận dữ liệu từ Thọ

- [ ] Mỗi mục có ID, thao tác và trạng thái áp dụng rõ ràng.
- [ ] Xác định được văn bản cùng điều/khoản/điểm đích, hoặc đã ghi rõ lý do chưa xác định.
- [ ] Nội dung trước–sau tương ứng, đủ câu/khoản để hiểu nghĩa.
- [ ] Có câu lệnh sửa đổi, trích dẫn và vị trí nguồn truy ngược được.
- [ ] Phân biệt QUOTED, DERIVED và UNRESOLVED; không gán nguồn giả cho câu suy ra.
- [ ] Thiếu hụt, lỗi trích xuất và đích mơ hồ đều có cảnh báo.
- [ ] Người phụ trách đã bổ sung hoặc xác nhận ngữ cảnh, dẫn chiếu và hiệu lực trước khi yêu cầu kết luận chắc chắn.

### Khi Ngọc Anh trả kết quả

- [ ] Kết quả truy ngược được về đúng mục sửa đổi và dữ liệu nguồn.
- [ ] Thay đổi chữ có nội dung và offset đúng hai chuỗi đầu vào.
- [ ] Phân biệt rõ true, false và null trong kết luận ngữ nghĩa.
- [ ] Giữ các khía cạnh xác định được và giải thích giá trị trước–sau.
- [ ] Category và mức độ có căn cứ; không chấm vượt phạm vi phương pháp hỗ trợ.
- [ ] Giữ bằng chứng, phân biệt trích nguyên văn và nội dung suy ra.
- [ ] Giữ cảnh báo và lý do; không trình bày trường hợp chưa xác định như đã phân tích hoàn thành.
- [ ] Khi chạy tích hợp ca thật, lưu phiên bản code, input và output để kiểm tra lại.

## 8. Mô tả phần việc để dùng trong báo cáo

> Nhận các mục sửa đổi đã được trích xuất và xác định đích; tạo kết quả so sánh câu chữ, phân tích thay đổi ngữ nghĩa, phân loại và đánh giá mức độ quan trọng, kèm bằng chứng nguồn và cảnh báo cần kiểm tra. Kết quả phục vụ backend tổng hợp báo cáo và frontend hiển thị để người dùng kiểm chứng. Khả năng tự động kết luận hiện giới hạn ở các mẫu baseline đã hỗ trợ.
