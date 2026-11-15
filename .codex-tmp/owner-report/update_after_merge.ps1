$ErrorActionPreference = 'Stop'
$taskDir = Join-Path (Get-Location) '.codex-tmp/owner-report'
$path = Join-Path $taskDir 'content.json'
$data = Get-Content -LiteralPath $path -Encoding UTF8 -Raw | ConvertFrom-Json
$replacements = @{
 'Chưa có module context tích hợp trong checkout.' = 'Các file context hiện là khung rỗng, chưa có triển khai tích hợp.'
 'Chưa có module context tích hợp trong checkout' = 'Các file context hiện là khung rỗng, chưa có triển khai tích hợp'
 'Checkout mới có Pydantic local tại src/analysis_contracts.py, chưa có TypedDict/validator được mẫu nhắc tới; cần Đức Anh cung cấp đúng revision để mapping và thử fixture ở LK-02/LK-08/LK-12.' = 'Sau merge main tại e0f5068, TypedDict và validator đã có tại backend/app/schemas/contracts.py, validation.py và report_validation.py. Cần mapping output Pydantic local ở src/analysis_contracts.py sang đúng contract này và thử fixture ở LK-02/LK-08/LK-12; có schema chưa đồng nghĩa Pipeline đã gọi đầy đủ validator.'
 'Chưa có test_evaluation_plan.md, bộ nhãn khóa hoặc bằng chứng chạy 51 ca schema trong checkout; không ghi đạt F1/Recall hay hoàn tất nghiệm thu.' = 'docs/test_evaluation_plan.md đã có sau merge. Kiểm thử ngày 09/11/2026 trên Windows, Python 3.14.5, dependency theo requirements.txt: schema 51 ca, 49 đạt và 2 expected failures; module Ngọc Anh 16/16 đạt. Hai khoảng trống schema là change_id duy nhất toàn báo cáo và reconstruction đầy đủ của Text Diff. Chưa có bộ nhãn khóa hay số đo chất lượng pháp lý để ghi đạt F1/Recall hoặc hoàn tất nghiệm thu.'
 'Chưa chốt tên hàm Linker/Context/Pipeline vì chưa có implementation và schema revision tương ứng trong checkout.' = 'Schema và Pipeline đã có sau merge main; Linker/Context vẫn là các file khung. Dùng ranh giới analysis_runner(parsed, comparison_id, deadline) trả AnalysisOutcome của Pipeline để lập kế hoạch mapping, chưa coi adapter local đã nối vào runner.'
 'Cần nhận contracts.py, validator và decision.md đúng revision; không dùng model local thay contract chung hoặc tự bổ sung trường để vượt kiểm tra.' = 'contracts.py, validator và decision.md đã có sau merge main. Dùng đúng các file này để đối chiếu; không dùng model local thay contract chung hoặc tự bổ sung trường để vượt kiểm tra.'
 'Chưa thể chốt mapping từng trường vì checkout không có contracts.py của schema được mẫu viện dẫn; không mặc định cây schema_version=1.0 đã là payload bàn giao.' = 'Contract đã có: ExtractedDocument gồm DocumentIdentity, file_type và blocks; Clause gồm unit_id, id, title, content, source_refs. Dùng hướng dẫn docs/schema-integration.md: blocks lấy nguyên văn source_blocks; Clause ánh xạ node_id, nhãn, heading, full_text và source_refs. document_adapter.py vẫn rỗng; cần hiện thực và kiểm chứng mapping, không mặc định cây schema_version=1.0 đã là payload bàn giao.'
 'Thọ và Đức Anh cần đối chiếu schema thực tế trước khi xác định cách giữ thông tin không mất nguồn.' = 'Theo schema-integration.md, kind/segments và metadata native có thể giữ nội bộ; không thêm vào contract chung khi chưa review. Thọ và Đức Anh cần kiểm chứng thông tin không mất qua adapter.'
 'Checkout hiện backend/main.py nhận JSON doc_v1/doc_v2 và import src.pipeline không tồn tại, backend/app/pipeline.py rỗng; khác thông tin main mà mẫu mô tả. Cần Dũng/Đức Anh đối chiếu đúng revision trước khi sửa API hoặc xác nhận tích hợp.' = 'Sau merge main, backend/main.py đã nhận multipart doc_v1/doc_s/reference_files và gọi backend/app/pipeline.py. Pipeline đọc/parse tài liệu, nhận analysis_runner nhưng mặc định app.state.analysis_runner=None nên chưa thực hiện phân tích đầy đủ; không còn lỗi import src.pipeline của checkout cũ. Cần Dũng/Đức Anh nối runner và kiểm tra validator trước khi xác nhận tích hợp.'
 'Không coi route hiện tại là API upload đã hoạt động và không tự thêm trường nhận xét vào schema backend.' = 'API đã có mã xử lý upload nhưng chưa kiểm thử end-to-end dịch vụ trong đợt này; không tự thêm trường nhận xét vào schema backend.'
 'chưa có validator chung trong checkout để xác nhận chính sách đã được triển khai.' = 'validator chung đã có, nhưng Pipeline chưa nối đầy đủ validate_sources/validate_amendment/validate_report trước trả API; bộ test schema không xác nhận wiring production này.'
 'Cần schema, validator cùng fixture lỗi từng bước;' = 'Dùng schema và validator đã merge cùng fixture lỗi từng bước;'
 'Chưa có phương án đánh giá chất lượng độc lập đầy đủ.' = 'Chưa có phương án triển khai và xác nhận kết quả đánh giá chất lượng độc lập đầy đủ; kế hoạch đánh giá đã có để nhóm tiếp tục hoàn thiện.'
}
foreach($property in $data.PSObject.Properties) {
 for($i=0;$i -lt 2;$i++) {
  $text = [string]$property.Value[$i]
  foreach($pair in $replacements.GetEnumerator()) { $text = $text.Replace($pair.Key,$pair.Value) }
  $property.Value[$i]=$text
 }
}
$data | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $path -Encoding UTF8
$fillPath = Join-Path $taskDir 'fill.ps1'
$fill = Get-Content -LiteralPath $fillPath -Encoding UTF8 -Raw
$fill = $fill.Replace("Set-Text `$note 'Kết quả đối chiếu checkout 92074d5", "Set-Text `$note 'Kết quả đối chiếu checkout 92074d5")
$start = $fill.IndexOf("    Set-Text `$note '")
$end = $fill.IndexOf("`n",$start)
$newLine = "    Set-Text `$note 'Bản đối chiếu sau merge main ngày 09/11/2026 tại e0f5068, nhập origin/main f76610e: đã có contracts.py, validator, decision.md, docs/test_evaluation_plan.md và Pipeline/API upload. Module Linker, Context, AI Adapter và các file change_analysis mới vẫn là khung; analysis_runner mặc định chưa được nối. Schema chạy 51 ca với 2 expected failures; module Ngọc Anh đạt 16/16. Các đề xuất dưới đây phân biệt phần contract đã có với implementation và chất lượng nghiệp vụ còn cần kiểm chứng. Phân công theo decision.md và module.md sau merge.'"
$fill = $fill.Substring(0,$start)+$newLine+$fill.Substring($end)
Set-Content -LiteralPath $fillPath -Value $fill -Encoding UTF8
Invoke-Expression $fill
