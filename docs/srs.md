**Bàng thuật ngữ**

| Thuật ngữ | Định nghĩa đề xuất |
| :--- | :--- |
| **Clause** | Một Điều tách từ văn bản, gồm `id`, `title`, `content`. |
| **Aligned pair** | Một cặp điều khoản v1–v2 tương ứng, hoặc một điều chỉ có ở một bên. Có 3 loại: `PAIRED`, `ADDED`, `DELETED`. |
| **Meaningful change** | Thay đổi làm đổi nội dung (số liệu, tính chất nghĩa vụ như "phải" thành "có thể"). Đổi cách diễn đạt thì **không** tính. |
| **Critical change** | Thay đổi có thể ảnh hưởng trực tiếp đến quyền, nghĩa vụ, chế tài/tiền hoặc thời hạn (bao gồm các điều khoản mới được bổ sung (`ADDED`), điều khoản bị bãi bỏ (`DELETED`), hoặc `PAIRED` có thay đổi trọng yếu). |

# SYSTEM REQUIREMENTS SPECIFICATION (SRS) & DATA CONTRACT

Hệ thống hoạt động theo mô hình Pipeline tuần tự: `Raw Text` -> `[Parser]` -> `Clauses` -> `[Aligner]` -> `AlignedPairs` -> `[SemanticDiff]` -> `DiffResults` -> `[Scorer]` -> `FinalReport`.

Dưới đây là Data Contract (Hợp đồng dữ liệu) quy định bắt buộc định dạng Input/Output giữa các module. Mọi thay đổi đều phải được Nhóm trưởng phê duyệt.

# SYSTEM REQUIREMENTS SPECIFICATION (SRS) & DATA CONTRACT

Hệ thống hoạt động theo mô hình Pipeline tuần tự: `Raw Text` -> `[Parser]` -> `Clauses` -> `[Aligner]` -> `AlignedPairs` -> `[SemanticDiff]` -> `DiffResults` -> `[Scorer]` -> `FinalReport`.

Dưới đây là Data Contract (Hợp đồng dữ liệu) quy định bắt buộc định dạng Input/Output giữa các module. Mọi thay đổi đều phải được Nhóm trưởng phê duyệt.

## 1. Data Structures (Cấu trúc dữ liệu dùng chung)

### 1.1 Clause (Điều khoản đơn lẻ)
```
class Clause:
    id: str       # BẮT BUỘC có chữ "Điều " ở trước. Vd: "Điều 1", "Điều 2a"
    title: str    # Tiêu đề điều khoản. Vd: "Phạm vi áp dụng" (Nếu không có, để chuỗi rỗng "")
    content: str  # Nội dung chi tiết (Đã lược bỏ ký tự xuống dòng thừa)
```
### 1.2 AlignedPair (Cặp điều khoản đã căn chỉnh)
```
class AlignedPair:
    pair_id: str               # Vd: "Điều 1 -> Điều 1" hoặc "None -> Điều 2"
    align_type: str            # CHỈ ĐƯỢC DÙNG: "PAIRED", "ADDED", "DELETED"
    v1_clause: Clause | None   # None nếu align_type là "ADDED"
    v2_clause: Clause | None   # None nếu align_type là "DELETED"
```

### 1.3 SemanticDiffResult (Kết quả phân tích ngữ nghĩa)
```
class SemanticDiffResult:
    is_meaningful_change: bool # True: Đổi nghĩa pháp lý / False: Sửa văn phong
    diff_details: str          # Giải thích ngắn gọn lý do
```

### 1.4 ScoringResult (Kết quả phân loại & chấm điểm)
```
class ScoringResult:
    category: str       # Vd: "OBLIGATION_OR_METRIC_CHANGE", "STYLISTIC_EDIT", "CLAUSE_ADDED"
    significance: str   # CHỈ ĐƯỢC DÙNG: "LOW", "MEDIUM", "HIGH", "CRITICAL"
    is_critical: bool   # Flag bắt buộc để tính Critical Change Recall
```

### 2. Functional Requirements (Đặc tả Module)
**FR-01 — Tách điều khoản (Parser)**
Input: text_v1 (str), text_v2 (str)
Output: List[Clause]
Acceptance Criteria: Không được tách sai khi trong nội dung có câu trích dẫn "theo quy định tại Điều N...".

**FR-02 — Căn chỉnh (Version Aligner)**
Input: v1_list: List[Clause], v2_list: List[Clause]
Output: List[AlignedPair]
Acceptance Criteria: Tổng số điều khoản ở bản cũ bị bãi bỏ (DELETED) và các cặp ghép được (PAIRED) phải bằng đúng số lượng v1_list.

**FR-03 & FR-04 — Semantic Diff & Scorer**
Input: Một đối tượng AlignedPair
Output: Đối tượng đó được bổ sung 2 thuộc tính SemanticDiffResult và ScoringResult.
Acceptance Criteria: Những thay đổi chỉ là sửa lỗi chính tả (vd: "sữ liệu" -> "dữ liệu") bắt buộc trả về is_meaningful_change = False và significance = LOW.

**FR-05 — Đánh giá hệ thống (Evaluator)**
Input: Danh sách kết quả dự đoán của toàn bộ Pipeline và danh sách Ground Truth.
Output: Dictionary chứa: Precision, Recall, Change_F1, Critical_Change_Recall.
Acceptance Criteria: Xử lý ngoại lệ ZeroDivisionError nếu tập mẫu test rỗng hoặc không có lỗi Critical nào trong bộ Ground Truth.