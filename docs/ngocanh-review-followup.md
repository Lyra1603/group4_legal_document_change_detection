# Xử lý nhận xét Text Diff và Semantic Diff

Ngày 17/11/2026. Nhánh Ngọc Anh được kiểm tra tại
`462d70ed34f3e6f6098f1c3de456dbf8511e5894`, so với main
`e0e27e55bd72a75bbd1f19d64b927202e39eb669` sau `git fetch origin`.
Các thay đổi chưa commit được nhận diện bằng SHA-256 trong manifest.

## Các điểm nối đã chạy lại

| Yêu cầu nhận xét | Thực hiện và kết quả |
| --- | --- |
| Đối chiếu LK-06–10 | LK-06: chuẩn bị index song song diff, ghép query sau hai nhánh; LK-07: đúng amendment_id, hai chuỗi và offset; LK-08: SemanticDiffResult/ChangeAspect chung; LK-09: giữ tám nhóm; LK-10: Scorer nối change_id và giữ null/review khi chưa đủ căn cứ. Không sửa schema. |
| Thọ → Text Diff | Chạy trực tiếp Parser và Adapter tại `ffd2f86aa135a8c6f717782baa65350010c48f9b` trên cả ba bộ DOCX; dùng Linker cục bộ tạo item rồi gọi compute_text_diff/validate_text_diff. Case_02 khớp input lịch sử về amendment_id, đơn vị, target_unit_ids, before/after và evidence; kho nguồn cũng khớp. Không sửa fixture để khớp output. |
| Text Diff → query | Chạy consumer và bridge tại `159e3552ce7a3ceb39dcea6ad3de767b83d359cd` của nhánh Context. Query giữ nguyên toàn bộ TextDiffResult, chỉ dẫn, nguồn, trước/sau và amendment_id. ID sai, offset sai và changes=[] khi hai chuỗi khác nhau bị từ chối với TEXT_DIFF_INVALID trước khi gọi retrieval. |
| Đồng bộ index/query | Kiểm thử bridge dùng barrier xác nhận index và diff hoàn tất trước ghép query/Semantic. Kiểm thử HTTP contract double xác nhận INDEX_NOT_READY không gửi request query; sau index, request /query/data chứa đúng diff. Đây không phải lần gọi LightRAG thật. |
| Semantic → Scorer | Dùng backend/app/change_analysis/semantic_diff.py và scorer.py đang có. Ca thật không truyền context_complete=True; meaningful=null, needs_review=true, lý do đầy đủ; Scorer giữ change_id, significance=null và is_critical=null. Payload AmendmentResult có bốn phần theo schema chung. |
| Hai fixture bàn giao | Kiểm thử chung test_fixture_consistency đối chiếu Text Diff → query với đầu ra Text Diff và kiểm tra Semantic → Scorer giữ category/null/review của ca deadline_reduction. Fixture query là hợp đồng synthetic, không dùng query_text diễn giải sẵn làm đáp án cho dữ liệu thật. |
| Tách src/ | Thêm src/README.md nêu rõ đường chạy thử nghiệm, output có cảnh báo cấp ngoài không phải AmendmentResult, không thay model/schema backend. |

Các Git blob của bên giao/nhận được nạp riêng trong tiến trình kiểm thử. Không
chép code PR #6/#7 vào runtime của nhánh Ngọc Anh hoặc giả định chúng đã merge.
Linker vẫn là bản cục bộ của nhánh Ngọc Anh, hash được ghi trong manifest.

## Kết quả và giới hạn

| Kiểm tra | Kết quả |
| --- | --- |
| 7 kiểm thử chéo mới | 7 đạt |
| Discover test/ (Context, demo, handoff) | 83 chạy: 81 đạt, 2 bỏ qua vì chưa bật dịch vụ thật |
| Schema suite riêng | 51 chạy: 49 đạt, 2 expected failures đã có từ trước |
| Bản thử nghiệm src/ | 16 đạt |

Schema suite cần chạy riêng vì thư mục đó không được unittest discover từ test/
thu thập trong cấu trúc hiện tại. Không cộng các lần chạy lặp thành số ca độc lập.
Hai expected failures là kiểm tra uniqueness change_id toàn báo cáo và khả năng
dựng lại toàn văn của validator report chung; validate_text_diff có kiểm tra
reconstruction tại điểm nối của Ngọc Anh.

Ba bộ DOCX lần lượt cho 1/2, 1/1 và 13/13 item có Text Diff; các mục ngoài phạm
vi vẫn được giữ cùng lý do. Payload query được dựng với đủ diff cho các item
có hai chuỗi, nhưng không phải mọi payload đã được gửi HTTP hoặc phù hợp giới
hạn query của dịch vụ thật. Test HTTP dùng ca khoản 5 Điều 16, nguồn DOCX thật
và phản hồi contract double. Không có thước đo độ chính xác ngữ nghĩa pháp lý.

Semantic hiện chỉ hỗ trợ AMEND có before/after QUOTED, đủ bằng chứng, đúng diff,
đích đã xác định và không còn cảnh báo: hai chuỗi bằng nhau sau NFC/strip;
cặp diễn đạt thời hạn tương đương đã định nghĩa; hoặc đổi duy nhất một số
nguyên dương trong “trong thời hạn N ngày”, phần còn lại giữ nguyên. Các ca
đủ Context trong test là synthetic. ADD/REPEAL/DERIVED, lộ trình nhiều mốc năm,
nhiều khía cạnh và các dạng chưa có rule vẫn giữ null/review. Thành công của
retrieval không tự xác nhận đủ Context. Không dùng số test để nói đã phân tích
đúng mọi thay đổi pháp luật.

## Chạy lại và bằng chứng

Lệnh pin SHA và các output nằm trong [README bằng chứng](../data/ngocanh-review/README.md).
Manifest ghi SHA Ngọc Anh, Thọ, Context, main và hash code/input/output;
`fresh_case_02.json` giữ cả item mới lẫn kết quả so sánh input cũ.

```powershell
python -m unittest discover -s test -p "test_*.py" -q
python -m unittest discover -s test/schema_suite -p "test_*.py" -q
python -m unittest test_pipeline_modules -q
```

Đã hoàn tất chạy lại cục bộ các điểm nối. Chưa có xác nhận reviewer trực tiếp
của Thọ, Đức Anh hoặc Dũng; manifest ghi rõ HUMAN_REVIEW_PENDING, không ghi
đã được bên nhận nghiệm thu. Chưa có Context pháp lý thật được xác nhận đầy đủ.

## Phạm vi PR đề xuất

Tiêu đề: **Kiểm chứng Text Diff với Parser/Adapter mới và consumer query; giữ Semantic chưa đủ căn cứ ở null/review**.

PR mô tả kết quả cụ thể: Text Diff kiểm tra offset/reconstruction trên nguyên
văn và đầu vào mới của Thọ; consumer Context dùng đủ diff và chặn dữ liệu sai;
Semantic/Scorer giữ trạng thái chưa xác định của ca thật. Nêu các test và giới
hạn ở trên, cùng SHA của hai bên; không ghi hoàn tất nhận diện mọi loại sửa đổi.

Khi tạo nhánh PR sạch từ main, chỉ lấy các thay đổi phục vụ task:

- backend/app/change_analysis/text_diff.py và semantic_diff.py;
- test/handoff_suite/test_ngocanh_week10.py, run_ngocanh_week10.py,
  peer_versions.py, test_peer_handoffs.py và run_peer_handoffs.py;
- data/ngocanh-week10/ và data/ngocanh-review/ là input/output kiểm chứng;
- docs/ngocanh-week10-work-report.md, ngocanh-week10-task-checklist.md,
  ngocanh-review-followup.md và src/README.md để giải thích phạm vi/giới hạn.

Nhánh hiện có `.codex-tmp/owner-report` đã được track từ trước; thêm gitignore
không loại chúng khỏi diff của PR. Không đưa cả nhánh hiện tại vào PR mới.
Giữ nguyên các artifact cục bộ, lấy riêng path ở trên vào nhánh PR sạch và
kiểm tra `git diff --name-only origin/main...HEAD` trước khi mở PR. Các tài liệu
lịch sử khác và các thay đổi thuật toán src/ không thuộc PR task tích hợp này.
