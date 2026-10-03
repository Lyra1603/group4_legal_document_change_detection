# Bảng thuật ngữ

| Thuật ngữ | Định nghĩa đề xuất |
| :--- | :--- |
| **Clause** | Một Điều tách từ văn bản, gồm `id`, `title`, `content`. |
| **Aligned pair** | Một cặp điều khoản v1–v2 tương ứng, hoặc một điều chỉ có ở một bên. Có 3 loại: `PAIRED`, `ADDED`, `DELETED`. |
| **Meaningful change** | Thay đổi làm đổi nội dung (số liệu, tính chất nghĩa vụ như "phải" thành "có thể"). Đổi cách diễn đạt thì **không** tính. |
| **Critical change** | Thay đổi có thể ảnh hưởng trực tiếp đến quyền, nghĩa vụ, chế tài/tiền hoặc thời hạn (bao gồm các điều khoản mới được bổ sung (`ADDED`), điều khoản bị bãi bỏ (`DELETED`), hoặc `PAIRED` có thay đổi trọng yếu). |

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
    pair_key: str               # Vd: "Điều 1 -> Điều 1" hoặc "None -> Điều 2"
    align_type: str            # CHỈ ĐƯỢC DÙNG: "PAIRED", "ADDED", "DELETED"
    v1: Clause | None   # None nếu align_type là "ADDED"
    v2: Clause | None   # None nếu align_type là "DELETED"
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

## 2. Functional Requirements (Đặc tả Module)
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

## 3. Thiết kế module
### 3.1 Module Reader(đọc file)

| | Reader |
|---|---|
| Nhận vào | Một file `.docx` hoặc PDF có lớp chữ |
| Công việc | Đọc nội dung chữ theo thứ tự trong tài liệu |
| Trả ra | Nội dung văn bản đã trích xuất |
| Khi không đọc được chữ | Báo lỗi, không coi là văn bản rỗng hợp lệ |
- Thư viện dự kiến:
  + PyMuPDF đọc PDF: đã có trong requirements.txt của branch.
  + python-docx đọc Word: cần bổ sung khi triển khai.
 
### 3.2 Module Parser — tách văn bản thành các Điều: Reader trả về chữ trong file. Parser nhận phần chữ đó và xác định ranh giới từng Điều để các module sau có thể so sánh.
  
| Nội dung | Quy định |
|---|---|
| Đầu vào | Nội dung chữ do Reader trả về của **một văn bản** |
| Xử lý | Nhận diện và tách từng Điều |
| Đầu ra | Danh sách Điều; mỗi Điều có `id`, `title`, `content` |
| Yêu cầu | Giữ đúng thứ tự; không nhầm câu dẫn chiếu “theo Điều 5…” thành đầu một Điều |
| Lỗi | Không tìm được Điều nào thì báo lỗi để kiểm tra |

Ví dụ đầu vào: 
```
Điều 1. Phạm vi điều chỉnh
Văn bản này quy định về...
Điều 2. Đối tượng áp dụng
Áp dụng đối với...
```

Đầu ra(JSON):
```
[
  {
    "id": "Điều 1",
    "title": "Phạm vi điều chỉnh",
    "content": "Văn bản này quy định về..."
  },
  {
    "id": "Điều 2",
    "title": "Đối tượng áp dụng",
    "content": "Áp dụng đối với..."
  }
]
```

### 3.3 Module Aligner - ghép các Điều tương ứng giữa bản cũ và bản mới.

Ví dụ: Điều 5 bản cũ được chuyển thành Điều 6 bản mới. Aligner cần ghép chúng với nhau để module sau so sánh đúng nội dung.

| Nội dung | Quy định |
|---|---|
| Đầu vào | Hai danh sách Điều do Parser trả về: bản cũ và bản mới |
| Xử lý | Tìm các Điều tương ứng dựa trên số Điều, tiêu đề và nội dung |
| Đầu ra | Danh sách `AlignedPair` |
| Yêu cầu | Mỗi Điều xuất hiện đúng một lần trong kết quả; không ghép chỉ dựa vào số Điều |

Mỗi AlignedPair có ba trường chính:
| Trường | Ý nghĩa |
|---|---|
| `align_type` | `PAIRED`: ghép được; `ADDED`: thêm mới; `DELETED`: bị xóa |
| `v1` | Điều bản cũ; bằng `null` nếu thêm mới |
| `v2` | Điều bản mới; bằng `null` nếu bị xóa |

Ví dụ một cặp ghép được:
```
{
  "pair_key": "Điều 5 -> Điều 6",
  "align_type": "PAIRED",
  "v1": {
    "id": "Điều 5",
    "title": "Thời hạn",
    "content": "Phải nộp trong 30 ngày."
  },
  "v2": {
    "id": "Điều 6",
    "title": "Thời hạn",
    "content": "Phải nộp trong 15 ngày."
  }
}
```

### 3.4 Module Text Diff — tìm những đoạn chữ thay đổi: Sau khi Aligner ghép đúng hai Điều, Text Diff chỉ ra chữ nào được thêm, xóa hoặc thay thế.

| Nội dung | Quy định |
|---|---|
| Đầu vào | Một `AlignedPair` do Aligner trả về |
| Xử lý | So sánh tiêu đề và nội dung của hai Điều |
| Đầu ra | Danh sách đoạn chữ thay đổi, gồm loại thay đổi, đoạn cũ và đoạn mới |
| Loại thay đổi | `INSERT`: thêm; `DELETE`: xóa; `REPLACE`: thay thế |
| Điều thêm/xóa toàn bộ | Ghi nhận toàn bộ nội dung phía tương ứng |

Ví dụ:
- Cũ: “Phải nộp trong 30 ngày.”
- Mới: “Phải nộp trong 15 ngày.”
Kết quả minh họa(JSON):
```
{
  "pair_key": "Điều 5 -> Điều 6",
  "changes": [
    {
      "field": "content",
      "type": "REPLACE",
      "old_text": "30",
      "new_text": "15"
    }
  ]
}
```

### 3.5 Module Semantic Diff — xác định thay đổi có làm đổi nghĩa hay không.

| Nội dung | Quy định |
|---|---|
| Đầu vào | Một `AlignedPair` và kết quả Text Diff; giữ đầy đủ nội dung hai Điều để hiểu ngữ cảnh |
| Xử lý | Phân biệt sửa cách diễn đạt với thay đổi nội dung, như quyền, nghĩa vụ, chủ thể, điều kiện, thời hạn hoặc chế tài |
| Đầu ra | Kết luận có đổi nghĩa không, giải thích và trích đoạn cũ/mới làm bằng chứng |
| Chưa đủ căn cứ | Đánh dấu cần kiểm tra; không tự kết luận là sửa văn phong |
| Ranh giới trách nhiệm | Mức độ nghiêm trọng do module Scorer xử lý sau |

Ví dụ đầu ra đề xuất(JSON):
```
{
  "pair_key": "Điều 5 -> Điều 6",
  "is_meaningful_change": true,
  "diff_details": "Thời hạn nộp giảm từ 30 xuống 15 ngày.",
  "old_quote": "Phải nộp trong 30 ngày.",
  "new_quote": "Phải nộp trong 15 ngày.",
  "needs_review": false
}
```
Quy định thêm: khi needs_review = true, cho phép is_meaningful_change = null để biểu thị chưa xác định.

Tiêu chí nghiệm thu tối thiểu:
- Chỉ sửa chính tả, không đổi nghĩa → false.
- “30 ngày” → “15 ngày” → true.
- “phải” → “có thể” trong cùng nghĩa vụ → true.
- Đổi chủ thể thực hiện dù không đổi số liệu → true.

### 3.6 Module Classifier & Scorer — phân loại và đánh giá mức độ quan trọng của thay đổi.

| Nội dung | Quy định |
|---|---|
| Đầu vào | `AlignedPair` và kết quả Semantic Diff |
| Xử lý | Xác định loại thay đổi và mức độ theo bộ tiêu chí thống nhất của nhóm |
| Đầu ra | `category`, `significance`, `is_critical`, `reason`, `needs_review` |
| Yêu cầu | Mức độ phải có lý do dựa trên nội dung và bằng chứng của thay đổi |

Các loại thay đổi ban đầu có thể gồm: sửa văn phong, thay đổi quyền/nghĩa vụ, chủ thể, thời hạn, chế tài, thêm Điều hoặc xóa Điều.

Quy tắc cần ghi rõ:
- significance nhận một trong bốn mức: LOW, MEDIUM, HIGH, CRITICAL.
- is_critical = true khi và chỉ khi significance = CRITICAL.
- Chỉ sửa văn phong, không đổi nghĩa → LOW.
- Thêm/xóa Điều không tự động được coi là CRITICAL.
- Chưa đủ căn cứ → needs_review = true, significance và is_critical để null.
- Bộ tiêu chí phân biệt các mức phải có ví dụ được nhóm thống nhất trước khi đánh giá hệ thống.

Ví dụ cấu trúc kết quả(JSON):
```
{
  "category": "STYLISTIC_EDIT",
  "significance": "LOW",
  "is_critical": false,
  "reason": "Sửa lỗi chính tả, giữ nguyên nội dung quy định.",
  "needs_review": false
}
```

### 3.7 Module Evaluator — đo hệ thống làm đúng đến đâu: Evaluator đối chiếu kết quả dự đoán với ground truth: đáp án do người gán nhãn và kiểm tra trước.

| Nội dung | Quy định |
|---|---|
| Đầu vào | Kết quả pipeline và bộ đáp án chuẩn của cùng các cặp văn bản |
| Xử lý | Đối chiếu các thay đổi dự đoán với đáp án chuẩn |
| Đầu ra | Precision, Recall, Change F1, Critical Change Recall |
| Cách sử dụng | Chạy khi kiểm thử, đánh giá; không bắt buộc chạy mỗi lần người dùng so sánh |

Ý nghĩa các chỉ số:

| Chỉ số | Câu hỏi được trả lời |
|---|---|
| Precision | Trong các thay đổi nghĩa hệ thống báo, bao nhiêu là đúng? |
| Recall | Trong các thay đổi nghĩa thực sự, hệ thống tìm được bao nhiêu? |
| Change F1 | Điểm tổng hợp Precision và Recall |
| Critical Change Recall | Hệ thống tìm đúng bao nhiêu thay đổi trọng yếu thực sự? |

Yêu cầu nghiệm thu cần ghi:
- Mục tiêu: Change F1 ≥ 0,90, Critical Change Recall ≥ 0,95 trên bộ kiểm thử độc lập.
- Thay đổi có trong đáp án nhưng hệ thống bỏ sót phải được tính là lỗi; không bỏ qua do thiếu kết quả hoặc ghép sai.
- Kết quả needs_review chưa được giải quyết không được tính là phát hiện đúng; phải báo thêm số lượng cần kiểm tra.
- Tập kiểm thử không được dùng để điều chỉnh thuật toán.
- Chỉ số không tính được do mẫu số bằng 0 trả null kèm lý do; không báo đạt mục tiêu.

Ví dụ: đáp án có 10 thay đổi trọng yếu, hệ thống tìm đúng 8 → Critical Change Recall = 80%.

## 4. Yêu cầu tải tài liệu và xem kết quả

| Chức năng | Yêu cầu |
|---|---|
| Chọn đầu vào | Người dùng chọn hai file `.docx` hoặc PDF có lớp chữ, xác định rõ **bản cũ / bản mới** |
| Bắt đầu so sánh | Người dùng nhấn “So sánh”; hệ thống kiểm tra file rồi chạy pipeline |
| Trạng thái xử lý | Hiển thị đang xử lý, hoàn thành hoặc thất bại |
| Xem kết quả | Hiển thị các Điều tương ứng, đoạn cũ/mới và phần chữ thay đổi |
| Xem phân tích | Mỗi thay đổi có kết luận đổi nghĩa, loại thay đổi, mức độ và lý do |
| Cần kiểm tra | Hiển thị rõ các kết quả `needs_review = true`; mức độ chưa xác định ghi “Chưa xác định” |
| Không có thay đổi | Chỉ thông báo khi xử lý thành công và không phát hiện thay đổi; nếu chỉ sửa văn phong thì vẫn hiển thị phần sửa |

## 5. Xử lý lỗi và cảnh báo
   
| Tình huống | Hành vi yêu cầu |
|---|---|
| Thiếu một trong hai file hoặc sai định dạng | Không chạy; yêu cầu chọn đủ hai file `.docx` hoặc PDF có lớp chữ |
| File hỏng, có mật khẩu hoặc không đọc được chữ | Dừng xử lý; báo rõ file nào gặp lỗi |
| Parser không tìm được Điều | Báo lỗi cấu trúc; không trả kết quả “không có thay đổi” |
| Ghép Điều mơ hồ hoặc nghi ngờ tách/gộp Điều | Cảnh báo cần kiểm tra; không coi phần chưa ghép chắc chắn là thêm/xóa đã xác nhận |
| Phân tích nghĩa hoặc chấm mức độ chưa đủ căn cứ | Đánh dấu `needs_review = true`; kết luận chưa xác định để `null` |
| Một bước xử lý thất bại | Báo bước gặp lỗi; nếu hiển thị kết quả một phần, phải ghi rõ báo cáo chưa hoàn tất |
Yêu cầu chung: thông báo lỗi phải dễ hiểu và có hướng xử lý; không hiển thị lỗi kỹ thuật nội bộ cho người dùng.

## 6. Yêu cầu vận hành

| Nội dung | Yêu cầu |
|---|---|
| Cấu hình | Giới hạn dung lượng file và thời gian xử lý phải cấu hình được; giá trị cụ thể cần nhóm thống nhất trước nghiệm thu |
| Tính toàn vẹn | Không âm thầm cắt bỏ nội dung; nếu không xử lý hết tài liệu phải thông báo rõ |
| Truy vết | Mỗi lần so sánh có `comparison_id`; ghi lại bước xử lý và lỗi để phục vụ kiểm tra |
| Quản lý file | File tải lên chỉ dùng để xử lý; bản đầu tiên không yêu cầu lưu lịch sử. File tạm phải được xóa sau xử lý |
| Bảo mật | Không ghi toàn bộ nội dung tài liệu vào log. Nếu dùng API bên ngoài, phải thống nhất việc gửi dữ liệu và quản lý khóa API |
| Đo hiệu năng | Ghi nhận thời gian xử lý và kích thước tài liệu; chỉ chốt mục tiêu tốc độ sau khi đo trên bộ tài liệu mẫu và môi trường xác định |

## 7. Quy định dữ liệu trao đổi giữa các module

Đây là hợp đồng dữ liệu: quy định các module nhận và trả những gì để ghép được với nhau.

| Dữ liệu | Nội dung tối thiểu |
|---|---|
| Reader → Parser | Nội dung trích xuất theo thứ tự và vị trí nguồn: trang PDF hoặc đoạn/bảng Word |
| Parser → Aligner | Danh sách Điều có định danh trong từng phiên bản, số Điều, tiêu đề, nội dung và vị trí nguồn |
| Aligner → Text Diff | `pair_key`, `align_type`, `v1`, `v2`, `needs_review` và lý do nếu ghép chưa chắc chắn |
| Text Diff → Semantic Diff | Cặp Điều đầy đủ và danh sách đoạn thêm/xóa/thay thế; mỗi đoạn ghi trường được so sánh, chữ cũ/mới và vị trí trong trường đó |
| Semantic Diff → Scorer | Danh sách thay đổi; mỗi thay đổi có `change_id`, kết luận đổi nghĩa, giải thích, bằng chứng cũ/mới và `needs_review` |
| Pipeline → giao diện | `comparison_id`, trạng thái xử lý, danh sách kết quả, cảnh báo và lỗi |





