**Bàng thuật ngữ**

| Thuật ngữ | Định nghĩa đề xuất |
| :--- | :--- |
| **Clause** | Một Điều tách từ văn bản, gồm `id`, `title`, `content`. |
| **Aligned pair** | Một cặp điều khoản v1–v2 tương ứng, hoặc một điều chỉ có ở một bên. Có 3 loại: `PAIRED`, `ADDED`, `DELETED`. |
| **Meaningful change** | Thay đổi làm đổi nội dung (số liệu, tính chất nghĩa vụ như "phải" thành "có thể"). Đổi cách diễn đạt thì **không** tính. |
| **Critical change** | Thay đổi có thể ảnh hưởng trực tiếp đến quyền, nghĩa vụ, chế tài/tiền hoặc thời hạn (bao gồm các điều khoản mới được bổ sung (`ADDED`), điều khoản bị bãi bỏ (`DELETED`), hoặc `PAIRED` có thay đổi trọng yếu). |

## FR-01 — Tách điều khoản (parser)
- Đầu vào : text của một văn bản (str)
- Đầu ra  : List[Clause]  với Clause = {id, title, content}
- Quy tắc : mỗi "Điều N" ở đầu dòng là một Clause
- Ví dụ   : "Điều 1. Phạm vi\nNội dung" -> [{id:"Điều 1", title:"Phạm vi", content:"Nội dung"}]
- Nghiệm thu: văn bản có câu "theo quy định tại Điều 5." giữa dòng KHÔNG bị tách thành một Điều mới

## FR-02 — Ghép cặp (align_versions)
- Đầu vào : 2 danh sách List[Clause] (từ bản cũ và bản mới)[cite: 3]
- Đầu ra  : List[AlignedPair][cite: 3]
- Quy tắc : Dựa vào `id` của Clause (vd: "Điều 1") để ghép cặp. Trạng thái của AlignedPair sẽ là PAIRED (có ở cả 2), ADDED (chỉ có ở bản mới), hoặc DELETED (chỉ có ở bản cũ).
- Ví dụ   : Bản cũ có "Điều 1", "Điều 2"; bản mới có "Điều 1", "Điều 3" -> [{Điều 1: PAIRED}, {Điều 2: DELETED}, {Điều 3: ADDED}]
- Nghiệm thu: Không được bỏ sót điều khoản nào; tổng số Clause đầu vào phải được ánh xạ đầy đủ vào danh sách AlignedPair.

## FR-03 — So sánh ngữ nghĩa (run_semantic_diff)
- Đầu vào : AlignedPair[cite: 3]
- Đầu ra  : SemanticDiffResult[cite: 3]
- Quy tắc : Phân tích và trích xuất sự khác biệt về mặt ngữ nghĩa giữa 2 điều khoản trong cặp PAIRED.
- Ví dụ   : Đầu vào là cặp PAIRED của "Điều 1" -> Đầu ra là SemanticDiffResult chứa danh sách các cụm từ bị xóa/thêm và vị trí thay đổi.
- Nghiệm thu: Nhận diện đúng sự thay đổi kể cả khi cấu trúc câu bị đảo ngược, không bị treo (crash) nếu một trong hai nội dung bị rỗng.

## FR-04 — Phân loại và chấm điểm (scorer)
- Đầu vào : AlignedPair + SemanticDiffResult[cite: 3]
- Đầu ra  : ScoringResult = {category, significance, is_critical}[cite: 3]
- Quy tắc : không đổi nghĩa -> STYLISTIC_EDIT/LOW; bị xóa -> CRITICAL (is_critical=true)[cite: 3]
- Ví dụ   : "30 ngày" -> "15 ngày" => OBLIGATION_OR_METRIC_CHANGE, CRITICAL, true[cite: 3]
- Nghiệm thu: Sửa lỗi chính tả không làm thay đổi nghĩa (ví dụ: "sữ liệu" -> "dữ liệu") phải được phân loại đúng vào STYLISTIC_EDIT.

## FR-05 — Đánh giá (evaluate_predictions)
- Đầu vào : kết quả dự đoán + ground truth[cite: 3]
- Đầu ra  : 4 chỉ số[cite: 3]
- Quy tắc : So khớp kết quả phân loại của hệ thống (`is_critical`, `category`) với nhãn thực tế do chuyên gia đánh giá (ground truth) để tính độ chính xác mô hình.
- Ví dụ   : Đưa vào 100 dự đoán, có 80 dự đoán đúng nhãn -> Trả về các chỉ số (ví dụ: Precision, Recall, F1, Accuracy).
- Nghiệm thu: Tính toán các chỉ số chính xác và không bị chia cho 0 (ZeroDivisionError) khi tập dữ liệu test bị trống hoặc thiếu nhãn.